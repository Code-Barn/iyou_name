#!/bin/bash
# This script runs automatically when PostgreSQL is first initialized
# It creates the grampsweb database for GrampsWeb

set -e

echo "Initializing databases..."

# Create grampsweb database for GrampsWeb
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE grampsweb;
EOSQL

echo "Database initialization complete."
echo "Created: grampsweb database for GrampsWeb"
