# iyou_name

Generate printable family trees in our unique format — Namecharts.

## Features

- **GEDCOM Import**: Upload and parse GEDCOM files for genealogical data
- **Interactive Charts**: Generate multi-generation family tree charts
- **Live Preview**: Customize charts with real-time preview (HUD)
- **OIDC Auth**: Passwordless login via iyou_idp (external Rust-based identity provider)
- **Rust Chart Kernel** (pending): Accelerated image generation via `../iyou_name_rust`

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd namechart
uv sync

# Run migrations
uv run python manage.py migrate

# Start server
uv run python manage.py runserver
```

## Authentication

All login, registration, and logout is handled by the external **iyou_idp** OIDC provider.
See `docs/NAME_DEVELOPER_GUIDE.md` for configuration.

## Documentation

- [Developer Guide](docs/NAME_DEVELOPER_GUIDE.md) - Comprehensive development documentation
- [Buffer System](docs/BUFFER_SYSTEM.md) - Chart caching architecture
- [GEDCOM Parser](docs/GEDCOM_PARSER.md) - Parser design and data model
- [Multi-Generation Spec](docs/MULTI_GENERATION_STANDARDIZATION_SPEC.md) - Validated generator standards
