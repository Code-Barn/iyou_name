#!/bin/bash
# This script runs automatically when PostgreSQL is first initialized

set -e

echo "Initializing databases..."

# Create grampsweb database for GrampsWeb
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE grampsweb;
EOSQL

# Create webtrees database for WebTrees
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE webtrees;
EOSQL

echo "Database initialization complete."
echo "Created: grampsweb and webtrees databases"
