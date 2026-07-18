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
RUN OIDC_RP_CLIENT_ID=builder OIDC_RP_CLIENT_SECRET=builder OIDC_RP_CALLBACK_URL=builder \
    uv run python manage.py collectstatic --noinput

# Stage 2: Runtime Vessel
FROM python:3.13-slim

WORKDIR /app

# System application dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagickwand-7.q16-10 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 --no-create-home appuser

# Single COPY from builder — no redundant layer copies
COPY --from=builder --chown=appuser:appgroup /app /app

ENV PATH="/app/.venv/bin:$PATH"
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
