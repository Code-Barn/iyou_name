# Stage 1: Build Forge
FROM python:3.13-slim AS builder

WORKDIR /app

# System dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV DJANGO_SETTINGS_MODULE=config.settings \
    UV_PYTHON_PREFERENCE=only-system

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy application code
COPY . .

# Harvest static assets
RUN uv run python manage.py collectstatic --noinput

# Stage 2: Runtime Vessel
FROM python:3.13-slim

WORKDIR /app

# System application dependencies
RUN apt-get update && apt-get install -y \
    ghostscript \
    libmagickwand-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy collected static assets
COPY --from=builder /app/staticfiles /app/staticfiles

# Copy application code (excluding .venv and staticfiles from build context)
COPY --from=builder /app /app

# The Shared Object Guard: if libdid_rust.so is present in the build context,
# place it where ctypes can resolve it. To use, place the file at
# context root as libdid_rust.so before building.
COPY libdid_rust.so /usr/local/lib/libdid_rust.so 2>/dev/null || true

# Non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
