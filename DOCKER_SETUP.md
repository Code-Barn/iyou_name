yaml

services:
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=namechart_db
      - POSTGRES_USER=macuser
      - POSTGRES_PASSWORD=password123
    ports:
      - "5432:5432"

  web:
    build: .
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgres://macuser:password123@db:5432/namechart_db
    depends_on:
      - db

volumes:
  postgres_data:

Use code with caution.

    db:5432: Inside Docker, you don't use localhost. You use the service name (db) as the hostname Docker Docs.
    volumes: This ensures your data isn't deleted when you stop the container Docker Docs.

2. Update Django settings.py
You need a way to parse that DATABASE_URL. The easiest way is using dj-database-url.
First, add the package using uv:
bash

uv add dj-database-url psycopg2-binary

Use code with caution.
Then, update your settings.py:
python

import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'postgres://macuser:password123@localhost:5432/namechart_db')
    )
}

Use code with caution.
3. Launch and Migrate
Since the database is new, you need to run your migrations inside the container:
bash

# Start the containers
docker compose up -d

# Run migrations inside the 'web' container
docker compose exec web uv run python manage.py migrate
