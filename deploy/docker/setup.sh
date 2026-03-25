#!/bin/bash
# Setup script for namechart + GrampsWeb development environment
set -e

echo "=== namechart + GrampsWeb Setup ==="

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env and set secure values for:"
    echo "  - GRAMPSWEB_SECRET_KEY (generate with: python -c \"import secrets; print(secrets.token_hex(32))\")"
    echo "  - POSTGRES_PASSWORD"
    echo "  - EMAIL_* settings for password reset"
    echo ""
    read -p "Press Enter when you've edited .env..."
fi

# Build and start containers
echo "Building and starting containers..."
docker compose up -d --build

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
sleep 5

# Create grampsweb database if it doesn't exist
echo "Ensuring grampsweb database exists..."
docker compose exec -T db psql -U namechart -c "SELECT 1 FROM pg_database WHERE datname='grampsweb'" | grep -q 1 || \
    docker compose exec -T db psql -U namechart -c "CREATE DATABASE grampsweb;"

# Wait for GrampsWeb to be ready
echo "Waiting for GrampsWeb to initialize..."
for i in {1..30}; do
    if docker compose exec -T grampsweb curl -sf http://localhost:5000/api/health > /dev/null 2>&1; then
        echo "GrampsWeb is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Run Django migrations
echo "Running Django migrations..."
docker compose exec -T web uv run python manage.py migrate

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Services:"
echo "  namechart:  http://localhost:8000"
echo "  grampsweb:  http://localhost:8080"
echo ""
echo "To stop: docker compose down"
echo "To view logs: docker compose logs -f"
