# GrampsWeb Integration Summary

## Overview

namechart can integrate with GrampsWeb to fetch genealogy data from a running GrampsWeb instance.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DNS / Ingress                          │
│           namechart.example.com  +  genealogy.example.com     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌─────────┐          ┌──────────┐         ┌─────────┐
   │namechart│          │GrampsWeb │         │  Redis  │
   │  (Django)│         │ (Flask)  │         │         │
   └────┬────┘          └────┬─────┘         └─────────┘
        │                    │
        │   GEDCOM API       │
        └──────────────────► │ ◄── REST API
                             │
                             ▼
                      ┌─────────────┐
                      │ PostgreSQL  │
                      │  (shared)   │
                      └─────────────┘
```

## Deployment Options

### Docker Compose (Development)
```bash
cd deploy/docker
./setup.sh
```

### Kubernetes (Production)
```bash
kubectl apply -f deploy/kubernetes/
```

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `GRAMPSWEB_API_URL` | GrampsWeb base URL (e.g., `http://grampsweb:5000`) | Yes |
| `GRAMPSWEB_API_TOKEN` | JWT token from GrampsWeb | Yes |
| `GRAMPSWEB_API_TIMEOUT` | Request timeout (default: 30s) | No |

## Usage

```python
from apps.core.grampsweb import get_client, fetch_gedcom_from_grampsweb

client = get_client()
if client:
    # Check availability
    if client.is_available():
        # Get GEDCOM export
        gedcom_bytes = fetch_gedcom_from_grampsweb()
        
        # Or query individual records
        person = client.get_person(handle)
```

## Services & Ports

| Service | Docker Port | K8s Namespace | Purpose |
|---------|-------------|---------------|---------|
| namechart | 8000 | namechart | Chart generation |
| grampsweb | 8080 | grampsweb | Genealogy database |
| postgresql | 5432 | namechart | User data |
| redis | 6379 | namechart | Caching |

## Security

- CORS configured to allow cross-origin requests between services
- API token authentication for GrampsWeb API access
- Secrets stored in Kubernetes Secrets (update defaults before deploy)
