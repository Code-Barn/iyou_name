# iyou_name Developer Guide

## 1. Project Identity

| Field | Value |
|-------|-------|
| Repository | `iyou_name` (ecosystem brand: **Namecharts**) |
| Author | Byers Brands, LLC |
| Version | 0.1.0 |
| License | AGPL-3.0 |

**Mission**: Public name resolution engine — generate printable family tree namecharts from GEDCOM genealogical data, with Decentralized Identity (DID) integration for cross-app sovereign identity via the iyou_name_rust cryptographic backend.

---

## 2. Technology Stack

| Component | Version / Choice |
|-----------|------------------|
| **Python** | 3.13+ |
| **Framework** | Django 6.0 |
| **Package Manager** | `uv` |
| **Database** | PostgreSQL (via `django-environ`/`DATABASE_URL`) |
| **Image Library** | Wand 0.6.13 (Python ctypes wrapper for ImageMagick) |
| **PDF** | Ghostscript (base template compositing) |
| **Frontend** | Vanilla JS, Bootstrap 5, static HUD JS |
| **Authentication** | Passwordless OIDC via `mozilla-django-oidc` + `MyOIDCAuthenticationBackend`; all auth flows delegated to `../iyou_idp` |
| **External Rust (auth/DID)** | `../iyou_idp` → `../did_rust` — handles all login, DID generation, VC ops outside this repo |
| **External Rust (chart kernel)** | `../iyou_name_rust` → `libiyou_chart_kernel.so` via PyO3 (untested, not yet wired) |
| **Server** | Gunicorn 23+ (production); `runserver` (dev) |
| **Testing** | Django TestCase + Playwright e2e (`@playwright/test`) |
| **Linter** | Ruff 0.14.x |
| **Deployment** | Docker (multi-stage) + Kubernetes manifests |

---

## 3. Directory Layout

```
iyou_name/
├── apps/
│   ├── accounts/        # Sovereign Mesh OIDC authentication backend
│   ├── browse/          # Individual browsing & family detail views
│   ├── chart_storage/   # Persistent settings, buffer cache, photos
│   ├── charts/          # Chart serving (download/final PDF)
│   ├── core/            # Shared utilities, middleware, rate-limiting, GrampsWeb client
│   ├── generator/       # Chart generation engine (1gen–7gen + buffer manager)
│   ├── hud/             # Interactive HUD (live preview, settings UI)
│   ├── parser/          # GEDCOM parsing → PersonData dataclass
│   ├── selector/        # Individual selection interface
│   └── users/           # CustomUser model, OIDC-authenticated user management
├── config/              # Django settings (settings.py), root URL conf, WSGI/ASGI
├── deploy/
│   ├── docker/          # Docker Compose for local dev + optional genealogy
│   └── kubernetes/      # Production K8s manifests (namespaces, PVCs, ingress, HPA)
├── docker-entrypoint.sh # Container startup: migrate → exec gunicorn
├── Dockerfile           # Multi-stage build (python:3.13-slim)
├── staticfiles/         # Pre-collected static assets
├── tests/               # Test suite (Django TestCase + Playwright)
├── pyproject.toml       # Python dependencies & project metadata
├── uv.lock              # Locked dependency tree
├── AGENT.md             # AI coding agent guidelines
│
├── ../iyou_name_rust/   # SIBLING REPO: Rust chart kernel retrofit (PyO3)
│   ├── src/             # Rust source: generators, rendering, core types
│   ├── Cargo.toml       # Rust dependencies: magick_rust, pyo3, serde
│   ├── pyproject.toml   # Maturin build config
│   └── tests/           # 42 Rust tests (unit + integration)
│
├── ../iyou_idp/         # SIBLING REPO: OIDC identity provider (handles all auth/login)
└── ../did_rust/         # SIBLING REPO: DID crypto backend (used by iyou_idp, not directly by iyou_name)
```

---

## 4. App Architecture & Data Flow

### 4.1 User Journey

```
Upload GEDCOM → Parse → Select Individual → HUD (live preview + settings) → Generate Final (PDF/PNG)
```

### 4.2 Core Data Model

The genealogical domain model is **not** normalized SQL — it's a `@dataclass` in `apps/parser/models.py`:

```python
@dataclass
class PersonData:
    id: str
    given_name: str
    surname: str
    full_name: str
    sex: str
    birth_date: str
    birth_place: str
    death_date: str
    death_place: str
    father: str        # person ID
    mother: str        # person ID
    spouse: List[str]
    children: List[str]
    # ... plus grandparents, siblings, adoptive parents, events
```

All persons are serialized into a single JSON blob on `GedcomFile.parsed_data` (JSONField). Multi-generation resolution happens entirely in Python by walking `father`/`mother` ID chains — not via SQL JOINs.

### 4.3 Key Django Models

| App | Model | Purpose |
|-----|-------|---------|
| `users` | `CustomUser` | Extends `AbstractUser` with `did`, `did_key`, `vcs` fields |
| `generator` | `GedcomFile` | Uploaded GEDCOM with `parsed_data` JSON blob |
| `generator` | `GedcomShare` | User-to-user GEDCOM sharing |
| `chart_storage` | `ChartBuffer` | Disk-backed buffer cache (`buffer_file` FileField) |
| `chart_storage` | `UserSettingsPreset` | Named preset configurations |
| `chart_storage` | `IndividualSettings` | Per-individual display settings |
| `chart_storage` | `IndividualPhoto` | Per-individual profile photo |
| `chart_storage` | `GedcomInfo` | Metadata about processed GEDCOM files |

---

## 5. External Rust Repos

All Rust-based functionality lives in sibling repos. **iyou_name does not contain or directly call any Rust code itself** — it delegates via OIDC (auth) and will eventually import a PyO3 module (chart kernel).

### 5.1 Auth & DID: `../iyou_idp` → `../did_rust`

| Repo | Role |
|------|------|
| `../iyou_idp/` | OIDC identity provider — handles **100% of login, registration, logout**. iyou_name redirects all auth flows to iyou_idp via `mozilla-django-oidc`. |
| `../did_rust/` | DID crypto library (`libdid_rust.so`) — called by iyou_idp for DID generation, VC signing/verification. Not directly used by iyou_name. |

**iyou_name's only involvement**: the `CustomUser` model retains `did`, `did_key`, `vcs` fields for storing identity data that may arrive via OIDC claims from iyou_idp.

```
User browser ──→ iyou_name (/users/login/) ──redirect──→ iyou_idp (OIDC) ──→ did_rust (crypto)
                                                        │
                                              ←─callback──
                        iyou_name creates/updates User ←─
```

---

### 5.2 Chart Kernel: `../iyou_name_rust` (Retrofit — UNTESTED)

**Purpose**: High-performance Rust reimplementation of the Python chart generation engine (Gen1–7). Uses ImageMagick via `magick_rust` for all rendering.

**Repo**: `../iyou_name_rust/`

**Integration**: PyO3 Python extension. Exposes `iyou_chart_kernel.render_chart_from_json(generation, primary_json, ancestors_json, settings_json) -> bytes`.

**Current status**: **NOT WIRED**. No Django code calls `import iyou_chart_kernel`. The Rust project has 42 tests passing and a Python bridge verification script (`verify_bridge.py`), but end-to-end integration from Django has never been executed.

```
┌────────────────────────────────────────────┐
│             iyou_name                      │
│  # nothing calls iyou_chart_kernel yet     │
└──────────────────┬─────────────────────────┘
                   │ (future: render_chart_from_json)
                   ▼
┌────────────────────────────────────────────┐
│           iyou_name_rust                    │
│  src/python_module.rs → render_chart_from_json()
│  src/generators/strategies/                │
│  ├── gen1.rs                               │
│  ├── gen2.rs                               │
│  ├── radial.rs  (Gen3-5)                   │
│  └── sunbeam.rs (Gen6-7)                   │
└────────────────────────────────────────────┘
```

**Build methods**:

| Method | Command | Output |
|--------|---------|--------|
| Cargo | `cargo build --release` | `target/release/libiyou_chart_kernel.so` |
| Maturin (dev) | `maturin develop --release` | Installs into current Python venv |
| Maturin (wheel) | `maturin build --release` | `.whl` in `target/wheels/` |

**To wire it in**: (1) `import iyou_chart_kernel` in a generator view, (2) replace the Python generator call, (3) add the `.whl` to the Dockerfile, (4) test end-to-end.

---

### 5.3 OIDC Configuration

All auth endpoints point to iyou_idp via environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `OIDC_OP_AUTHORIZATION_ENDPOINT` | `https://iyou.me/openid/authorize/` | Auth redirect target |
| `OIDC_OP_TOKEN_ENDPOINT` | `http://127.0.0.1:8000/openid/token/` | Token exchange |
| `OIDC_OP_USER_ENDPOINT` | `http://127.0.0.1:8000/openid/userinfo/` | User info claims |
| `OIDC_OP_JWKS_ENDPOINT` | `http://127.0.0.1:8000/openid/jwks/` | JWKS key set |
| `OIDC_RP_CALLBACK_URL` | `http://127.0.0.1:8000/oidc/callback/` | OIDC callback |

### 5.4 Auth URL Patterns

Admin templates require bare `{% url 'login' %}` / `{% url 'logout' %}` (Django 5.0+ removed built-in auth views). All redirect to iyou_idp via OIDC:

| URL name | Path | Target |
|----------|------|--------|
| `login` (root) | `/accounts/login/` | RedirectView → `oidc_authentication_init` |
| `logout` (root) | `/accounts/logout/` | RedirectView → `oidc_logout` |
| `users:login` | `/users/login/` | RedirectView → `oidc_authentication_init` |
| `users:register` | `/users/register/` | RedirectView → `oidc_authentication_init` |
| `users:logout` | `/users/logout/` | RedirectView → `oidc_logout` |

---

## 6. Image Generation Engine

### 6.1 Rendering Pipeline

The heart of the project produces family tree charts as PNG previews or PDF output via Wand (ImageMagick).

**Pipeline**: Template → Background → Flag overlay → Individual text (rotated) → Composite → Output

### 6.2 Generator Files

| File | Lines | Role |
|------|-------|------|
| `prototype_image_1generator.py` | 427 | 1-gen: single person |
| `prototype_image_2generator.py` | 524 | 2-gen: + parents |
| `prototype_image_3generator.py` | ~500 | 3-gen: + grandparents |
| `prototype_image_4generator.py` | ~600 | 4-gen: + great-grandparents |
| `prototype_image_5generator.py` | ~700 | 5-gen |
| `prototype_image_6generator.py` | ~800 | 6-gen |
| `prototype_image_7generator.py` | 873 | 7-gen: composites 6-gen overlay |
| `individual_printer.py` | 1,197 | Core text rendering, font metrics, rotation |
| `place_name_utils.py` | 3,229 | Place abbreviation, flag image path resolution |
| `date_utils.py` | 391 | Date parsing/formatting |
| `name_utils.py` | ~250 | Name splitting, display formatting |
| `sunbeam_position_calculator.py` | 269 | Concentric-square positioning for 8–10 gen |
| `simple_buffer_manager.py` | 417 | In-memory buffer cache, generator routing |
| `settings_validator.py` | — | Coerces user settings to typed values |
| `template_mapping.py` | — | Routes template IDs → generator functions |

### 6.3 Settings Schema

User-facing settings (stored in localStorage, synced to server via `IndividualSettings`):

- `flag_choice`: str ("country", "region", ...)
- `color_1`, `color_2`, `color_3`: Wand Color
- `inside_fill`, `outside_fill`: int (opacity)
- `show_place_names`, `show_dates`: bool
- `font_size_type_name`, `font_size_type_detail`: int
- `generation_line_weight`: str

### 6.4 Coordinate System

- Standard canvas: **1950 × 1950 px** at **300 DPI**
- 10-gen canvas: **4700 × 4700 px**
- Center: (975, 975); ancestors placed at 0°, 90°, 180°, 270° rotations

### 6.5 Buffer Cache (Two-layer)

1. **In-memory** (`SimpleBufferManager`): Settings-hash keyed, invalidated on change
2. **Disk-backed** (`ChartBuffer` model via FileField): User-specific, persistent across restarts

See `docs/BUFFER_SYSTEM.md` for full details.

---

## 7. GEDCOM Parser

Located at `apps/parser/`. Handles GEDCOM 5.5 and 7.0 formats via `ged4py`.

**Key output**: `PersonData` dataclass instances keyed by individual ID.

Full parser documentation: `docs/GEDCOM_PARSER.md`

---

## 8. Deployment & Containerization

### 8.1 Multi-stage Dockerfile

The `Dockerfile` (root and `deploy/docker/Dockerfile`) uses a two-stage `python:3.13-slim` build:

**Stage 1 — Build Forge**:
- System: `build-essential`, `curl`, `gcc`, `git`, `libpq-dev`
- Installs `uv`, runs `uv sync --no-dev --frozen`
- Runs `collectstatic --noinput`

**Stage 2 — Runtime Vessel**:
- System: `libmagickwand-dev`, `ghostscript`, `libpq5`
- Copies `.venv` and `staticfiles` from builder
- **No** iyou_name_rust chart kernel included (not yet wired)
- Non-root `appuser`
- Entrypoint: `docker-entrypoint.sh` (migrate → exec gunicorn)
- CMD: `uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000`

### 8.2 Kubernetes (Production)

K8s manifests in `deploy/kubernetes/`:

| File | Resource |
|------|----------|
| `00-namespaces.yaml` | `namechart` + `grampsweb` namespaces |
| `01-postgresql.yaml` | PostgreSQL 16 (headless service, 10Gi PVC) |
| `02-redis.yaml` | Redis 7 (1Gi PVC) |
| `03-namechart-web.yaml` | Django app (HPA 2–10, 2Gi limit, probes on `/health/`) |
| `04-grampsweb.yaml` | GrampsWeb API (2Gi limit) |
| `05-grampsweb-celery.yaml` | Celery worker + grampsweb Redis |
| `06-ingress.yaml` | nginx-ingress for `namechart.example.com` + `genealogy.example.com` |
| `07-secrets.yaml` | DB passwords, Django SECRET_KEY, API tokens |

### 8.3 Chart Kernel Deployment (`../iyou_name_rust` — not yet wired)

Once integration code is added to Django, deploy via either:

| Method | Steps |
|--------|-------|
| **Embed in Docker image** | `cd iyou_name_rust && maturin build --release && cp target/wheels/iyou_chart_kernel-*.whl ../iyou_name/` then add `COPY *.whl /tmp/ && uv pip install /tmp/iyou_chart_kernel-*.whl` to Dockerfile |
| **Sidecar container** | Build iyou_name_rust's own Dockerfile and deploy as a separate container in the K8s pod |

Currently **neither is implemented** — this is a pending integration task.

### 8.4 Required Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `NAME_SECRET_KEY` | Yes | — | Django secret key |
| `NAME_DEBUG` | Yes | `False` | Debug mode |
| `NAME_ALLOWED_HOSTS` | Yes | — | e.g. `namechart.example.com` |
| `DATABASE_URL` | Yes | — | PostgreSQL DSN |
| `OIDC_RP_CLIENT_SECRET` | Yes | — | OIDC client secret |
| `OIDC_RP_CLIENT_ID` | Conditional | `name-client` | OIDC client ID |
| `OIDC_RP_CALLBACK_URL` | Conditional | `http://127.0.0.1:8000/oidc/callback/` | OIDC callback URL |
| `GENEALOGY_MODE` | No | `disabled` | `disabled`, `grampsweb`, `webtrees`, `external` |
| `GRAMPSWEB_API_URL` | Conditional | — | GrampsWeb API base URL |
| `GRAMPSWEB_API_TOKEN` | Conditional | — | GrampsWeb JWT |
| `REDIS_URL` | No | — | Redis for caching |

---

## 9. Development Workflow

### 9.1 Quick Start

```bash
# Clone and enter
git clone <repo-url> && cd iyou_name

# Install uv (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Copy env and edit
cp .env.example .env

# Run migrations
uv run python manage.py migrate

# Start dev server
uv run python manage.py runserver
```

### 9.2 Running Tests

```bash
uv run python manage.py test                          # All tests
uv run python manage.py test tests.test_buffer_system # Specific file
uv run python manage.py test --verbosity=2            # Verbose
```

### 9.3 Linting

```bash
ruff check apps/
ruff check --fix apps/
```

---

## 10. Genealogy Integration

| Mode | Service | Description |
|------|---------|-------------|
| `disabled` | — | No genealogy link |
| `grampsweb` | GrampsWeb | Private family trees (REST API) |
| `webtrees` | WebTrees | Public/multi-user trees |
| `external` | URL | Link to any external site |

GrampsWeb sync: `GENEALOGY_MODE=grampsweb` with `GRAMPSWEB_API_URL` + `GRAMPSWEB_API_TOKEN` enables GEDCOM export via the `/api/exporters/gedcom/file` endpoint.

---

## 11. Key Tech Debt Items

1. **Duplicate HUD app**: `apps/generator/hud/` is a dead-code copy of `apps/hud/` — same URL patterns.
2. **Monolithic `parsed_data` JSON blob**: All genealogical data in a single field; no SQL-level indexing on individuals.
3. **`place_name_utils.py`**: 3,229-line single file with massive hardcoded dictionaries — candidate for JSON data file extraction.
4. **Test sprawl**: ~79 test/debug files in `tests/` with mixed conventions.
5. **Dockerfile Python version**: Was pinned to 3.12 despite project requiring 3.13 (now fixed in multi-stage refactor).
6. **Hardcoded test paths**: Many test files use `sys.path.append("/home/user/CODE_BASE/namechart")`.
7. **iyou_name_rust chart kernel unwired**: The Rust chart generation retrofit (`../iyou_name_rust/`) has 42 passing tests but has never been called from Django. No `import iyou_chart_kernel` exists anywhere in the codebase.

---

## 12. Reference Documents

| Document | Location | Content |
|----------|----------|---------|
| Agent guidelines | `AGENT.md` (root) | AI agent coding conventions |
| Buffer/cache system | `docs/BUFFER_SYSTEM.md` | Chart caching architecture |
| DID integration | `docs/outdated/DID_INTEGRATION.md` | Legacy DID/VC documentation (archived) |
| GEDCOM parser | `docs/GEDCOM_PARSER.md` | Parser design and data model |
| Multi-gen spec | `docs/MULTI_GENERATION_STANDARDIZATION_SPEC.md` | Validated generator standards |
| Outdated docs | `docs/outdated/` | Archived documentation (do not reference) |
| Project state audit | `PROJECT_STATE_AUDIT.md` (root) | Full technical debt audit (2026-05-19) |
| Rust chart kernel | `../iyou_name_rust/README.md` | iyou_name_rust project overview |
| Rust deployment | `../iyou_name_rust/DEPLOYMENT_READY.md` | Chart kernel deployment instructions |
| Rust CI/CD | `../iyou_name_rust/CI_CD_GUIDE.md` | Dual-repo CI/CD pipeline reference |
| Rust test matrix | `../iyou_name_rust/TEST_MATRIX.md` | Test coverage (42 Rust tests) |
| Rust status | `../iyou_name_rust/PROJECT_STATUS.md` | v1.1.0-python-ready status report |
| Rust integration summary | `../iyou_name_rust/FINAL_SUMMARY.md` | Python-PyO3 integration (5-day retrofit) |
| Rust bridge verification | `../iyou_name_rust/verify_bridge.py` | E2E Python bridge test script (run with `python verify_bridge.py`) |
