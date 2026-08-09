#!/bin/bash
set -e

# Run database migrations before handing off to the application server.
# Static assets are already baked into the image by the build stage.
echo "Running database migrations..."
uv run python manage.py migrate --noinput

# Hand off to the CMD (gunicorn)
echo "Starting gunicorn..."
exec "$@"
