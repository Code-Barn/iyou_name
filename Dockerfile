# =====================================================================
# STAGE 1: The Heavy Compilation Forge
# =====================================================================
FROM python:3.13-slim-bookworm AS forge

# Install essential system compilers and ImageMagick headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libmagickwand-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install the canonical Rust compiler toolchain
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /forge_space
RUN python -m venv .venv && .venv/bin/pip install --upgrade pip maturin

# Copy only the Rust source tree context to utilize layer caching
COPY ./iyou_name_rust /forge_space/iyou_name_rust

WORKDIR /forge_space/iyou_name_rust
# Compile the optimized native PyO3 wheel asset
RUN ../.venv/bin/maturin build --release --features python --out /forge_space/dist

# =====================================================================
# STAGE 2: The Production Runtime Environment
# =====================================================================
FROM python:3.13-slim-bookworm AS runner

# Install runtime-only ImageMagick shared objects (no heavy headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagickwand-7.q16-10 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Setup privileged execution boundary context
RUN groupadd -g 1000 appgroup && useradd -u 1000 -g appgroup -m appuser

# Install uv for dependency management and entrypoint
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Pull the compiled native wheel package from the Forge stage
COPY --from=forge /forge_space/dist /tmp/dist

# Copy Python dependency manifests first for layer caching
COPY ./iyou_name/pyproject.toml ./iyou_name/uv.lock /app/

# Install the local native compiled Rust wheel into system Python
RUN pip install --no-cache-dir /tmp/dist/*.whl \
    && rm -rf /tmp/dist

# Install Python dependencies via uv (matches existing project convention)
RUN cd /app && uv sync --no-dev --frozen

# Copy the rest of the application codebase
COPY --chown=appuser:appgroup ./iyou_name /app

RUN mkdir -p /app/staticfiles /app/media && chown -R appuser:appgroup /app/staticfiles /app/media

ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
