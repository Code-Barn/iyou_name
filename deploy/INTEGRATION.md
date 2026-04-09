# Genealogy Integration

## Overview

namechart supports multiple genealogy integration options. Choose the one that fits your use case:

| Mode | Use Case | Multi-user | Privacy |
|------|----------|-----------|---------|
| `disabled` | No genealogy link | N/A | N/A |
| `grampsweb` | Private family trees | No | Private |
| `webtrees` | Public/multi-user trees | Yes | Public |
| `external` | Link to any URL | Varies | Varies |

## Quick Start

```bash
cd deploy/docker
./setup.sh
```

Edit `.env` to set `GENEALOGY_MODE` and configure your chosen service.

## Configuration

### Common Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `GENEALOGY_MODE` | Integration mode | `disabled` |
| `GENEALOGY_EXTERNAL_URL` | URL for external mode | - |

### GrampsWeb (Private)

For private family trees where you want full control.

```bash
GENEALOGY_MODE=grampsweb
GRAMPSWEB_BASE_URL=http://localhost:8080
GRAMPSWEB_SECRET_KEY=your-secret-key
GRAMPSWEB_TREE=Family Tree
```

```bash
docker compose --profile grampsweb up -d
```

### WebTrees (Public)

For public, multi-user genealogy sites.

```bash
GENEALOGY_MODE=webtrees
WEBTREES_URL=http://localhost:8081
WEBTREES_ADMIN_PASSWORD=your-admin-password
```

```bash
docker compose --profile webtrees up -d
```

### External URL

Link to any external genealogy service.

```bash
GENEALOGY_MODE=external
GENEALOGY_EXTERNAL_URL=https://www.familysearch.org
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DNS / Ingress                          │
│           namechart.example.com  +  genealogy.example.com     │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
       ┌─────────┐      ┌──────────┐      ┌─────────┐
       │namechart│      │ GrampsWeb│      │ WebTrees│
       │ (Django)│      │ (Private)│      │(Public) │
       └────┬────┘      └────┬─────┘      └────┬────┘
            │                │                 │
            └────────────────┴─────────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │ PostgreSQL  │
                       └─────────────┘
```

## Services & Ports

| Service | Docker Port | Purpose |
|---------|-------------|---------|
| namechart | 8000 | Chart generation |
| grampsweb | 8080 | Private genealogy (profile) |
| webtrees | 8081 | Public genealogy (profile) |
| postgresql | 5433 (host) / 5432 (container) | Database |
| redis | 6379 | Caching |

## Navbar Integration

The navbar shows a "Genealogy" link based on your mode:

| Mode | Label | URL |
|------|-------|-----|
| grampsweb | My Tree | GrampsWeb URL |
| webtrees | Family Trees | WebTrees URL |
| external | Genealogy | External URL |
| disabled | (no link) | - |
