# DID Integration Guide

This document describes how Decentralized Identifiers (DIDs) and Verifiable Credentials (VCs) are implemented in the namechart project.

## Overview

Namechart uses DIDs and VCs to enable:
- **Family-scoped credentials**: Issue credentials to family members based on GEDCOM data
- **Cross-app authentication**: Use DID-based auth with Polly for family-scoped polling
- **Portable identity**: Users control their own identifiers

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Namechart     │     │     Polly       │
│                 │     │                 │
│  ┌───────────┐  │     │  ┌───────────┐  │
│  │CustomUser │  │     │  │CustomUser │  │
│  │  - did    │◄─┼─────┼─►│  - did    │  │
│  │  - vcs    │  │     │  │  - vcs    │  │
│  └───────────┘  │     │  └───────────┘  │
│        │        │     │        │        │
│        ▼        │     │        ▼        │
│  ┌───────────┐  │     │  ┌───────────┐  │
│  │did_utils  │  │     │  │did_utils  │  │
│  └───────────┘  │     │  └───────────┘  │
└────────┬─────────┘     └────────┬────────┘
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────┐
│         /home/user/CODE_BASE/did_rust/              │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │       Rust DID Library          │   │
│  │   (generate_did, verify_vc)    │   │
│  └─────────────────────────────────┘   │
│              │                         │
│              ▼                         │
│  ┌─────────────────────────────────┐   │
│  │     libdid_rust.so (FFI)        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Components

### 1. CustomUser Model

Located in `apps/users/models.py`:

```python
class CustomUser(AbstractUser):
    did = models.CharField(max_length=255, unique=True, null=True)
    did_method = models.CharField(max_length=50, default="key")
    did_key = models.TextField(blank=True)  # JWK format
    vcs = models.JSONField(default=list)  # List of VCs
```

### 2. DID Utilities

Located in `apps/users/did_utils.py`:

| Function | Description |
|----------|-------------|
| `generate_did(method)` | Generate a new DID |
| `verify_vc(vc_json)` | Verify a VC |
| `issue_vc(credential, did, key)` | Issue a VC |
| `generate_key()` | Generate a key pair |

### 3. DID Views (API Endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/did/generate/` | POST | Generate DID for user |
| `/api/did/` | GET | Get user's DID |
| `/api/did/verify/` | POST | Verify a VC |
| `/api/did/vc/issue/` | POST | Issue a VC |
| `/api/did/vc/add/` | POST | Add VC to profile |
| `/api/did/vcs/` | GET | List user's VCs |
| `/api/did/vcs/type/<type>/` | GET | Filter VCs by type |

### 4. Rust DID Library

Located in `/home/user/CODE_BASE/did_rust/`:

```
did_rust/
├── Cargo.toml
├── src/
│   └── lib.rs          # FFI functions
├── python_wrapper/      # Python FFI
└── wasm-bindings/       # WASM for web
```

## Backend Selection

DID operations can use either Rust or Python backend:

```bash
# Use Rust backend (recommended for production)
DID_BACKEND=rust uv run python manage.py runserver

# Use Python backend (default)
uv run python manage.py runserver
```

## API Usage Examples

### Generate a DID

```bash
curl -X POST /api/did/generate/ \
  -H "Authorization: Cookie sessionid=..." \
  -H "Content-Type: application/json" \
  -d '{"method": "key"}'
```

Response:
```json
{
  "did": "did:key:z6M...",
  "method": "key",
  "generated": true
}
```

### Issue a VC

```bash
curl -X POST /api/did/vc/issue/ \
  -H "Authorization: Cookie sessionid=..." \
  -H "Content-Type: application/json" \
  -d '{
    "credentialSubject": {"id": "did:key:...", "name": "John Doe"},
    "type": ["VerifiableCredential", "FamilyMemberCredential"],
    "name": "Family Member"
  }'
```

## Family Credential Flow

1. User uploads GEDCOM file to namechart
2. User generates a DID via `/api/did/generate/`
3. User requests family credential
4. Namechart verifies family membership via GEDCOM data
5. Namechart issues VC with family scope
6. User presents VC to Polly for family-scoped polling

## Security Considerations

- Private keys are stored encrypted in the database
- VC verification uses cryptographic signatures
- Credentials can be revoked by the issuer
- Users control their own DIDs

## Future Enhancements

- WASM bindings for browser-based DID operations
- GrampsWeb integration for family data
- Cross-app credential federation with Polly
