# =====================================================================
# STAGE 1: The Heavy Compilation Forge
# =====================================================================
FROM python:3.13-slim-trixie AS forge

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config libmagickwand-dev curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /forge_space
RUN python -m venv .venv && .venv/bin/pip install --upgrade pip maturin

# Copy the Rust workspace out of the parent context root
COPY ./iyou_name_rust /forge_space/iyou_name_rust

WORKDIR /forge_space/iyou_name_rust
RUN ../.venv/bin/maturin build --release --features python --out /forge_space/dist

# =====================================================================
# STAGE 2: The Production Runtime Environment
# =====================================================================
FROM python:3.13-slim-trixie AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagickwand-7.q16-10 libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appgroup && useradd -u 1000 -g appgroup -m appuser

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Pull dependency definitions from the relative flat application path
COPY ./iyou_name/pyproject.toml ./iyou_name/uv.lock* /app/

# Pull the native wheel from the forge stage
COPY --from=forge /forge_space/dist /tmp/dist

RUN pip install --no-cache-dir /tmp/dist/*.whl \
    && rm -rf /tmp/dist

# Install Python dependencies via uv (project convention)
RUN cd /app && uv sync --no-dev --frozen

# CRITICAL: Copy the flat app files directly into /app to satisfy the root runtime layout
COPY --chown=appuser:appgroup ./iyou_name /app

RUN mkdir -p /app/staticfiles /app/media && chown -R appuser:appgroup /app/staticfiles /app/media

ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
