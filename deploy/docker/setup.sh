#!/bin/bash
# Setup script for namechart + optional genealogy services
set -e

echo "=== namechart Setup ==="

cd "$(dirname "$0")"

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and set:"
    echo "  - GENEALOGY_MODE (disabled, grampsweb, webtrees, or external)"
    echo ""
    echo "Then run this script again."
    exit 0
fi

# Load environment
source .env

echo "Genealogy mode: $GENEALOGY_MODE"

# Build and start base containers (web, db, redis always run)
echo "Building and starting base services..."
docker compose up -d --build db redis web

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U namechart > /dev/null 2>&1; then
        echo "PostgreSQL is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "PostgreSQL failed to start"
        exit 1
    fi
    sleep 1
done

# Create databases if they don't exist
echo "Ensuring databases exist..."
docker compose exec -T db psql -U namechart -c "SELECT 1 FROM pg_database WHERE datname='grampsweb'" | grep -q 1 || \
    docker compose exec -T db psql -U namechart -c "CREATE DATABASE grampsweb;" || true

docker compose exec -T db psql -U namechart -c "SELECT 1 FROM pg_database WHERE datname='webtrees'" | grep -q 1 || \
    docker compose exec -T db psql -U namechart -c "CREATE DATABASE webtrees;" || true

# Start genealogy service based on mode
if [ "$GENEALOGY_MODE" = "grampsweb" ]; then
    echo "Starting GrampsWeb..."
    docker compose up -d --profile grampsweb
elif [ "$GENEALOGY_MODE" = "webtrees" ]; then
    echo "Starting WebTrees..."
    docker compose up -d --profile webtrees
fi

# Wait for web to be ready
echo "Waiting for namechart to start..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health/ > /dev/null 2>&1; then
        echo "namechart is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Run Django migrations
echo "Running Django migrations..."
docker compose exec -T web uv run python manage.py migrate --noinput || true

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Services:"
echo "  namechart:  http://localhost:8000"

if [ "$GENEALOGY_MODE" = "grampsweb" ]; then
    echo "  grampsweb:  http://localhost:8080"
elif [ "$GENEALOGY_MODE" = "webtrees" ]; then
    echo "  webtrees:   http://localhost:8081"
elif [ "$GENEALOGY_MODE" = "external" ]; then
    echo "  genealogy:  $GENEALOGY_EXTERNAL_URL"
fi

echo ""
echo "To stop: docker compose down"
echo "To start with GrampsWeb: docker compose --profile grampsweb up -d"
echo "To start with WebTrees: docker compose --profile webtrees up -d"
