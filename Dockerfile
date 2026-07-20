# =====================================================================
# STAGE 1: Node.js Asset Builder (Tailwind CSS)
# =====================================================================
FROM node:20-alpine AS assets

WORKDIR /app
COPY iyou_name_django/package.json iyou_name_django/package-lock.json ./
RUN npm ci --ignore-scripts
COPY iyou_name_django/tailwind.config.js iyou_name_django/postcss.config.js ./
COPY iyou_name_django/static/css/input.css ./static/css/input.css
COPY iyou_name_django/apps/ ./apps/
COPY iyou_name_django/templates/ ./templates/
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

# =====================================================================
# STAGE 2: The Heavy Compilation Forge
# =====================================================================
FROM python:3.13-slim-trixie AS forge

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config libmagickwand-7.q16hdri-dev libmagickwand-dev libclang-dev curl patchelf \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /forge_space
RUN python -m venv .venv && .venv/bin/pip install --upgrade pip maturin

# Copy the Rust workspace from the unified repo layout
COPY ./iyou_name_rust /forge_space/iyou_name_rust

WORKDIR /forge_space/iyou_name_rust
ENV MAGICKCORE_HDRI_ENABLE=1
ENV MAGICKCORE_QUANTUM_DEPTH=16
ENV BINDGEN_EXTRA_CLANG_ARGS="-DMAGICKCORE_HDRI_ENABLE=1 -DMAGICKCORE_QUANTUM_DEPTH=16"
RUN ../.venv/bin/maturin build --release --features python --out /forge_space/dist

# =====================================================================
# STAGE 3: Production Runner
# =====================================================================
FROM python:3.13-slim-trixie AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagickwand-7.q16hdri-10 libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN groupadd -g 1000 appgroup && useradd -u 1000 -g appgroup -m appuser

WORKDIR /app

# Pull dependency definitions from the unified Django subdirectory path
COPY ./iyou_name_django/pyproject.toml ./iyou_name_django/uv.lock* /app/
COPY --from=forge /forge_space/dist /tmp/dist

RUN pip install --no-cache-dir /tmp/dist/*.whl && rm -rf /tmp/dist
RUN cd /app && uv sync --no-dev --frozen

# Copy the unified Django application codebase straight into the runner app path
COPY --chown=appuser:appgroup ./iyou_name_django /app

# Copy compiled Tailwind CSS from assets stage (overwrites any stale output.css)
COPY --from=assets /app/static/css/output.css /app/static/css/output.css

# Collect all static files into STATIC_ROOT (must run before switching to appuser)
RUN python manage.py collectstatic --noinput

RUN mkdir -p /app/media && chown -R appuser:appgroup /app/staticfiles /app/media /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
