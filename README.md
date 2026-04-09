# namechart-django

Generate printable family trees in our unique format.

## Features

- **GEDCOM Import**: Upload and parse GEDCOM files for genealogical data
- **Interactive Charts**: Generate multi-generation family tree charts
- **Live Preview**: Customize charts with real-time preview (HUD)
- **DID Identity**: Decentralized identity support for family-scoped credentials
- **Cross-App Integration**: Works with Polly for family-scoped polling

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

## DID Integration

Namechart supports Decentralized Identifiers (DIDs) for:

- **Family Credentials**: Issue verifiable credentials to family members
- **Polly Integration**: Use credentials for family-scoped voting in Polly
- **Portable Identity**: Users control their own identifiers

See [docs/DID_INTEGRATION.md](docs/DID_INTEGRATION.md) for details.

### DID API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/did/generate/` | POST | Generate DID for user |
| `/api/did/` | GET | Get user's DID |
| `/api/did/verify/` | POST | Verify a VC |
| `/api/did/vc/issue/` | POST | Issue a VC |
| `/api/did/vcs/` | GET | List user's VCs |

### Using Rust Backend

For production, use the Rust DID backend:

```bash
DID_BACKEND=rust uv run python manage.py runserver
```

See [/home/user/CODE_BASE/did_rust/README.md](file:///home/user/CODE_BASE/did_rust/README.md) for building the Rust library.

## Documentation

- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Detailed development documentation
- [DID Integration](docs/DID_INTEGRATION.md) - DID/VC implementation details
