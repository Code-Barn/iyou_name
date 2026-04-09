# Deployment Guide

This directory contains deployment configurations for running namechart with GrampsWeb integration.

## Structure

```
deploy/
├── docker/                    # Docker Compose setup for local development
│   ├── docker-compose.yml     # Main compose file
│   ├── .env.example          # Environment variables template
│   ├── setup.sh              # Automated setup script
│   ├── init-db.sh            # Database initialization script
│   ├── Caddyfile             # Caddy reverse proxy config
│   └── traefik-labels.toml   # Traefik labels reference
├── kubernetes/                # Kubernetes manifests for production
│   ├── 00-namespaces.yaml
│   ├── 01-postgresql.yaml
│   ├── 02-redis.yaml
│   ├── 03-namechart-web.yaml
│   ├── 04-grampsweb.yaml
│   ├── 05-grampsweb-celery.yaml
│   ├── 06-ingress.yaml
│   └── 07-secrets.yaml
└── README.md
```

## Docker Compose (Development)

### Quick Start

```bash
cd deploy/docker
./setup.sh
```

The setup script will:
1. Create `.env` from `.env.example` (first run only)
2. Build and start all containers
3. Create databases automatically
4. Run Django migrations

### Genealogy Options

Choose one mode in `.env`:

| Mode | Service | Description |
|------|---------|-------------|
| `disabled` | - | No genealogy link |
| `grampsweb` | GrampsWeb | Private family trees |
| `webtrees` | WebTrees | Public/multi-user trees |
| `external` | URL | Link to external site |

Start with a specific genealogy service:
```bash
docker compose --profile grampsweb up -d
docker compose --profile webtrees up -d
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| web | 8000 | Namechart Django app |
| db | 5433 | PostgreSQL (internal 5432, exposed 5433) |
| redis | 6379 | Redis for caching |
| grampsweb | 8080 | GrampsWeb genealogy (profile) |
| webtrees | 8081 | WebTrees genealogy (profile) |

## Kubernetes (Production)

### Prerequisites

- Kubernetes 1.24+
- kubectl configured
- nginx-ingress controller
- cert-manager (for TLS)

### Deployment

```bash
# Create namespaces
kubectl apply -f 00-namespaces.yaml

# Update secrets (change default passwords!)
# Edit 07-secrets.yaml with real credentials
kubectl apply -f 07-secrets.yaml

# Deploy in order
kubectl apply -f 01-postgresql.yaml
kubectl apply -f 02-redis.yaml
kubectl apply -f 03-namechart-web.yaml
kubectl apply -f 04-grampsweb.yaml
kubectl apply -f 05-grampsweb-celery.yaml
kubectl apply -f 06-ingress.yaml

# Check status
kubectl get pods -n namechart
kubectl get pods -n grampsweb
```

### Subdomain Configuration

Update the ingress hosts in `06-ingress.yaml`:
- `namechart.example.com` - Main application
- `genealogy.example.com` - GrampsWeb instance

### Database Configuration

GrampsWeb uses the same PostgreSQL instance as namechart but with a separate database (`grampsweb`).
The connection string is:
```
postgresql://namechart:PASSWORD@postgresql.namechart:5432/grampsweb
```

## Environment Variables

### Namechart

| Variable | Description |
|----------|-------------|
| `GRAMPSWEB_API_URL` | Base URL of GrampsWeb API |
| `GRAMPSWEB_API_TOKEN` | API token for GrampsWeb authentication |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |

### GrampsWeb

| Variable | Description |
|----------|-------------|
| `GRAMPSWEB_TREE` | Name of the family tree |
| `GRAMPSWEB_SECRET_KEY` | Flask secret key |
| `GRAMPSWEB_BASE_URL` | Public URL of GrampsWeb |
| `GRAMPSWEB_CORS_ORIGINS` | Allowed CORS origins |
| `GRAMPSWEB_USER_DB_URI` | User database connection |

## Architecture

```
                    ┌─────────────────┐
                    │   DNS / Ingress  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌───────────┐ ┌───────────┐ ┌───────────┐
        │ namechart │ │ grampsweb │ │   Redis   │
        │   .com    │ │ .genealogy│ │   (both)  │
        │           │ │   .com    │ │           │
        └─────┬─────┘ └─────┬─────┘ └───────────┘
              │             │
              │             │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ PostgreSQL  │
              │ (2 dbs)    │
              └─────────────┘
```

## GrampsWeb API Integration

Namechart can sync data from GrampsWeb via the REST API:

1. Generate an API token in GrampsWeb (Settings > API Access)
2. Configure `GRAMPSWEB_API_URL` and `GRAMPSWEB_API_TOKEN` in namechart
3. Use the sync endpoint to fetch GEDCOM data

### API Endpoints Used

- `GET /api/people/` - List people
- `GET /api/people/{handle}` - Get person details
- `GET /api/families/{handle}` - Get family details
- `POST /api/exporters/gedcom/file` - Export GEDCOM
