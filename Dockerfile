FROM python:3.12-slim

# Install system dependencies (The Linux way—this ALWAYS works)
RUN apt-get update && apt-get install -y \
    libmagickwand-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set up the app
WORKDIR /app
COPY . .

# Install Python dependencies using uv
RUN uv sync --frozen

# Run your Django app
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

