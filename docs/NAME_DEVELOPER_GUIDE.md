# iyou_name Developer Guide

## 1. Project Identity

| Field | Value |
|-------|-------|
| Repository | `iyou_name` (ecosystem brand: **Namecharts**) |
| Author | Byers Brands, LLC |
| Version | 0.1.0 |
| License | AGPL-3.0 |

**Mission**: Public name resolution engine — generate printable family tree namecharts from GEDCOM genealogical data, with Decentralized Identity (DID) integration for cross-app sovereign identity via the integrated `crates/iyou_chart_kernel/` cryptographic backend.

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
| **Frontend** | Vanilla JS, Hybrid CSS Matrix (Tailwind + Bootstrap), static HUD JS |
| **CSS Framework** | Tailwind CSS 3.4 (compiled) + Bootstrap 5 (scoped grid) |
| **Authentication** | Passwordless OIDC via `mozilla-django-oidc` + `MyOIDCAuthenticationBackend`; all auth flows delegated to `../iyou_idp` |
| **Integrated Rust (auth/DID)** | `../iyou_idp` → `../did_rust` — handles all login, DID generation, VC ops outside this repo |
| **Integrated Rust (chart kernel)** | `crates/iyou_chart_kernel/` → `libiyou_chart_kernel.so` via PyO3 (wired with fallback) |
| **Server** | Gunicorn 23+ (production); `runserver` (dev) |
| **Testing** | Django TestCase + Playwright e2e (`@playwright/test`) |
| **Linter** | Ruff 0.14.x |
| **CSS Processor** | PostCSS + Tailwind CLI |
| **Build System** | Node.js 20 (Tailwind) + Python 3.13 (Django) + Rust (Maturin) |
| **Deployment** | Multi-stage Docker (Node.js + Python + Rust) + Kubernetes manifests |

---

## 3.5 Frontend & Styling Strategy: Hybrid CSS Matrix

The project employs a **dual-CSS framework architecture** that combines the best of both worlds:

### Tailwind CSS (Primary Framework)
- **Purpose**: Utility-first styling for ecosystem components, headers, and utility classes
- **Build Process**: `npm run tailwind:build` compiles `static/css/input.css` → `static/css/output.css`
- **Scope**: Ecosystem bar (`_ecosystem_bar.html`), standard header (`_standard_header.html`), utility classes
- **Configuration**: `tailwind.config.js` with custom colors, fonts, and breakpoints
- **PostCSS**: Processed through `postcss.config.js` for optimization

### Bootstrap 5 (Structural Bridge)
- **Purpose**: Layout grid system for main content containers, cards, forms, and navigation
- **Integration**: Scoped CSS definitions in `base.html` alongside Tailwind
- **Scope**: `.container`, `.row`, `.col-*`, `.card`, `.form-control`, `.btn`, `.alert`, `.navbar`
- **Responsive**: Full grid system with breakpoints (576px, 768px, 992px, 1200px, 1400px)
- **Static Files**: `static/vendor/bootstrap/bootstrap.min.css` and `bootstrap.bundle.min.js`

### Hybrid Architecture Benefits
- **No Conflicts**: Tailwind and Bootstrap coexist peacefully with scoped selectors
- **Best of Both**: Tailwind's utility classes + Bootstrap's proven grid system
- **Performance**: Tailwind's purgeable CSS + Bootstrap's minimal grid-only subset
- **Maintainability**: Clear separation of concerns between ecosystem UI and content layout

### Build Commands
```bash
# Build Tailwind CSS
npm run tailwind:build

# Watch for changes during development
npm run tailwind:watch

# Full static asset pipeline
npm run build
```

### Template Structure
```
templates/
├── base.html                  # Root template with Hybrid CSS Matrix
├── includes/
│   ├── _ecosystem_bar.html   # Tailwind-only (utility classes)
│   ├── _standard_header.html  # Tailwind-only (utility classes)
│   ├── _tailwind_safe_init.html # Tailwind initialization
│   ├── _nav.html              # Layer 2 app header (Tailwind-only)
│   └── _footer.html           # Site footer (Tailwind-only)
└── apps/                     # App-specific templates (use both frameworks)
```

### Known Frontend Debt

Global Bootstrap 5 Reboot CSS in `base.html` introduces micro-font/flex resets that cause subtle spacing differences compared to pure Tailwind sister repos (`iyou_wun`/`iyou_poly`). Future task: Deprecate global Bootstrap completely in favor of scoped Tailwind UI components.

---

## 3. Directory Layout (Flattened Monorepo)

```
iyou_name/
├── manage.py              # Django entrypoint (root)
├── config/                # Django settings (settings.py), root URL conf, WSGI/ASGI
├── apps/                  # Django applications
│   ├── accounts/          # Sovereign Mesh OIDC authentication backend
│   ├── browse/            # Individual browsing & family detail views
│   ├── chart_storage/     # Persistent settings, buffer cache, photos
│   ├── charts/            # Chart serving (download/final PDF)
│   ├── core/              # Shared utilities, middleware, rate-limiting, GrampsWeb client
│   ├── generator/         # Chart generation engine (1gen–7gen + buffer manager)
│   ├── hud/               # Interactive HUD (live preview, settings UI)
│   ├── parser/            # GEDCOM parsing → PersonData dataclass
│   ├── selector/          # Individual selection interface
│   ├── upload/            # GEDCOM upload handling
│   └── users/             # CustomUser model, OIDC-authenticated user management
├── crates/
│   └── iyou_chart_kernel/ # INTEGRATED RUST CRATE: Chart kernel (PyO3)
│       ├── src/
│       │   ├── lib.rs            # Main library entry point
│       │   ├── python_module.rs  # PyO3 Python bindings
│       │   ├── core/             # Types, constants, coordinate system, errors
│       │   ├── generators/       # gen1.rs, gen2.rs, unified_generator.rs, strategies/, specs/
│       │   ├── rendering/        # Text renderer, place abbreviation
│       │   └── utils/
│       ├── tests/           # Rust unit + integration tests
│       ├── Cargo.toml       # Rust dependencies (magick_rust, pyo3, serde)
│       └── pyproject.toml   # Maturin build configuration
├── static/                # Source static assets (CSS, JS, images)
│   └── css/               # Tailwind input/output files
├── templates/             # Global templates and includes
│   └── includes/          # Reusable components (_ecosystem_bar.html, _standard_header.html, _nav.html, _footer.html)
├── docs/                  # Comprehensive documentation
│   ├── NAME_DEVELOPER_GUIDE.md  # This file (canonical reference)
│   └── ecosystem_shared/    # Shared ecosystem specifications
├── tests/                 # Test suite (Django TestCase + Playwright)
├── deploy/                # Docker + Kubernetes manifests
├── Dockerfile             # Root multi-stage Dockerfile (Node.js + Python + Rust)
├── docker-compose.yml     # Unified development environment
├── pyproject.toml         # Python dependencies & project metadata
├── package.json           # Node.js dependencies for Tailwind CSS
└── tailwind.config.js     # Tailwind CSS configuration
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

Auth and DID handling lives in sibling repos; the chart kernel lives **inside this repo** under `crates/iyou_chart_kernel/` (see §5.2).

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

### 5.2 Chart Kernel: `crates/iyou_chart_kernel/` (Integrated & Wired)

**Purpose**: High-performance Rust reimplementation of the Python chart generation engine (Gen1–7). Uses ImageMagick via `magick_rust` for all rendering.

**Location**: `crates/iyou_chart_kernel/` (integrated into the flattened monorepo)

**Integration**: PyO3 Python extension. Exposes `iyou_chart_kernel.render_chart_from_json(json_payload) -> bytes`.

**Current status**: **FULLY WIRED WITH FALLBACK**. Django code in `apps/generator/views.py` automatically detects and uses the Rust kernel when available, with graceful fallback to Python prototype on any exception.

```
┌─────────────────────────────────────────────────────────────┐
│                     iyou_name (Django)                       │
│  apps/generator/views.py → generate_final_chart()          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ PyO3 Rust Kernel Ingress Hook                         │  │
│  │   try:                                                 │  │
│  │       import iyou_chart_kernel                        │  │
│  │       RUST_KERNEL_AVAILABLE = True                    │  │
│  │   except ImportError:                                  │  │
│  │       RUST_KERNEL_AVAILABLE = False                   │  │
│  └───────────────┬───────────────────────────────────┘  │
│                  │                                    │  │
│                  ▼                                    │  │
│  ┌─────────────────────────┐                          │  │
│  │ Rust Kernel Available  │                          │  │
│  └─────────────────────────┘                          │  │
│                  │                                    │  │
│                  ▼                                    │  │
│  ┌───────────────────────────────────────────────────┐  │  │
│  │ iyou_chart_kernel.render_chart_from_json(json_str) │  │  │
│  └───────────────────────────────────────────────────┘  │  │
│                  │                                    │  │
│                  ▼                                    │  │
│  ┌───────────────────────────────────────────────────┐  │  │
│  │ Fallback: Python Prototype (on any Rust exception)│  │  │
│  └───────────────────────────────────────────────────┘  │  │
│                  │                                    │  │
│                  ▼                                    │  │
└──────────────────┼────────────────────────────────────┘  │
                   │                                         │
                   ▼                                         │
┌─────────────────────────────────────────────────────────────┐  │
│                crates/iyou_chart_kernel                      │  │
│  src/python_module.rs → render_chart_from_json()          │  │
│  src/generators/strategies/                                │  │
│  ├── gen1.rs               # 1-generation chart renderer  │  │
│  ├── gen2.rs               # 2-generation chart renderer  │  │
│  ├── radial.rs             # 3-5 generation radial strategy│  │
│  └── sunbeam.rs           # 6-7 generation sunbeam strategy│  │
└─────────────────────────────────────────────────────────────┘  │
                   ▲                                         │
                   │                                         │
                   └─────────────────────────────────────────┘
```

**Build methods**:

| Method | Command | Output |
|--------|---------|--------|
| Cargo | `cargo build --release` | `target/release/libiyou_chart_kernel.so` |
| Maturin (dev) | `maturin develop --release` | Installs into current Python venv |
| Maturin (wheel) | `maturin build --release` | `.whl` in `target/wheels/` |

**Current Implementation**:
- ✅ Automatic Rust kernel detection in `generate_final_chart()`
- ✅ JSON payload construction with family data, template, and settings
- ✅ Rust kernel execution with exception handling
- ✅ Graceful fallback to Python prototype on any error
- ✅ End-to-end testing verified (Python prototype operational)
- ⚠️ Rust kernel not yet built/available (expected - will auto-use when present)

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

The heart of the project produces family tree charts as PNG previews or PDF output via a **dual-engine architecture** with automatic fallback.

**Primary Engine**: PyO3 Rust kernel (`iyou_chart_kernel.render_chart_from_json()`)
**Fallback Engine**: Pure-Python Wand/ImageMagick + Ghostscript pipeline

**Pipeline**: Template → Background → Flag overlay → Individual text (rotated) → Composite → Output

**Dual-Engine Flow**:
```
┌─────────────────────────────────────────────────────────────┐
│                 Chart Generation Request                     │
└─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│  1. PyO3 Rust Kernel Detection (apps/generator/views.py)     │
│     try:                                                     │
│         import iyou_chart_kernel                            │
│         RUST_KERNEL_AVAILABLE = True                        │
│     except ImportError:                                      │
│         RUST_KERNEL_AVAILABLE = False                       │
└─────────────────────────────────────────────────────────────┘
                                    │
                            ┌───────┴───────┐
                            │                │
                            ▼                ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│  Rust Kernel Available  │  │  Rust Kernel Unavailable│
└─────────────────────────┘  └─────────────────────────┘
                            │                                │
                            ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│  2. JSON Payload Construction                               │
│     - Convert family_data to JSON                           │
│     - Include individual_id, template, settings             │
└─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Rust Kernel Execution                                   │
│     image_buffer = iyou_chart_kernel.render_chart_from_json(json_str)│
└─────────────────────────────────────────────────────────────┘
│
│  ┌─────────────────────────────────────────────────────────┐
│  │ 4. Fallback to Python Prototype (on any Rust exception)   │
│  │    image_buffer = generator_function(primary_individual, │
│  │                                      family_data, template_type, │
│  │                                      user_settings)              │
│  └─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│  5. Return PDF Response                                      │
│     HttpResponse(image_buffer, content_type="application/pdf")│
└─────────────────────────────────────────────────────────────┘
```

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

The root `Dockerfile` uses a **three-stage build** process integrating Node.js (Tailwind), Python (Django), and Rust (chart kernel):

**Stage 1 — Node.js Assets (Tailwind CSS)**:
- Base: `node:20-alpine`
- Installs Node.js dependencies via `npm ci`
- Compiles Tailwind CSS: `npx tailwindcss -i static/css/input.css -o static/css/output.css --minify`
- Output: Minified `output.css` for production

**Stage 2 — Python Build Forge**:
- Base: `python:3.13-slim`
- System: `build-essential`, `curl`, `gcc`, `git`, `libpq-dev`, `libmagickwand-dev`
- Installs `uv`, runs `uv sync --no-dev --frozen`
- Copies compiled `output.css` from Node.js stage
- Runs `collectstatic --noinput`
- **Rust Integration**: When available, will include `maturin build --release` for chart kernel

**Stage 3 — Runtime Vessel**:
- Base: `python:3.13-slim`
- System: `libmagickwand-dev`, `ghostscript`, `libpq5`
- Copies `.venv`, `staticfiles`, and compiled assets from builder
- **PyO3 Rust Kernel**: Automatic detection via `import iyou_chart_kernel` with fallback
- Non-root `appuser` with proper permissions
- Entrypoint: `docker-entrypoint.sh` (migrate → exec gunicorn)
- CMD: `uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000`

**Key Build Commands**:
```bash
# Build production image
docker build -t iyou_name -f Dockerfile .

# Development build with cache
docker build --cache-from iyou_name -t iyou_name -f Dockerfile .

# Multi-arch build (ARM64 + AMD64)
docker buildx build --platform linux/amd64,linux/arm64 -t iyou_name -f Dockerfile --push .

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

### 8.3 Chart Kernel Deployment (`crates/iyou_chart_kernel/` — fully wired with fallback)

The Rust chart kernel is **fully integrated** with automatic detection and fallback:

**Current Implementation**:
- ✅ Automatic PyO3 kernel detection in `apps/generator/views.py`
- ✅ JSON payload construction and Rust execution
- ✅ Graceful fallback to Python prototype on any error
- ✅ End-to-end testing verified (Python prototype operational)

**Deployment Methods**:

| Method | Steps | Status |
|--------|-------|--------|
| **Embed in Docker image** | `cd crates/iyou_chart_kernel && maturin build --release && cp target/wheels/iyou_chart_kernel-*.whl ../../` then add to Dockerfile Stage 2 | ✅ Recommended |
| **Sidecar container** | Build the crate's own Dockerfile and deploy as separate K8s container | ⚠️ Alternative |

**Dockerfile Integration** (Stage 2 - Python Build Forge):
```dockerfile
# Add to Stage 2 after uv sync
COPY --from=iyou_chart_kernel_build /app/target/wheels/iyou_chart_kernel-*.whl /tmp/
RUN uv pip install /tmp/iyou_chart_kernel-*.whl
```

**Kubernetes Deployment**:
- The chart kernel is automatically used when the Python package is installed
- No additional configuration needed - the fallback mechanism handles missing kernel
- Monitor usage via logs: `grep "PyO3 Rust kernel" pods/logs`

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

# Install Node.js (for Tailwind CSS)
# Option 1: Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install 20
nvm use 20

# Option 2: Direct install
# Follow instructions at https://nodejs.org/en/download

# Install Python dependencies
uv sync

# Install Node.js dependencies
npm install

# Copy env and edit
cp .env.example .env

# Build Tailwind CSS
npm run tailwind:build

# Run migrations
uv run python manage.py migrate

# Start dev server
uv run python manage.py runserver
```

### 9.1.1 Development Workflow with Auto-reload

```bash
# Terminal 1: Django development server
uv run python manage.py runserver

# Terminal 2: Tailwind CSS watch mode
npm run tailwind:watch

# Terminal 3: Rust development (when working on chart kernel)
cd crates/iyou_chart_kernel
cargo watch -x "build --release"
```

### 9.2 Running Tests

```bash
uv run python manage.py test                          # All tests
uv run python manage.py test tests.test_buffer_system # Specific file
uv run python manage.py test --verbosity=2            # Verbose
```

### 9.3 Linting

```bash
# Python linting
ruff check apps/
ruff check --fix apps/

# CSS linting (if Stylelint is installed)
npx stylelint "static/css/**/*.css"
```

### 9.4 Build Commands

```bash
# Build Tailwind CSS for production
npm run tailwind:build

# Watch Tailwind CSS during development
npm run tailwind:watch

# Full asset pipeline (CSS + static files)
npm run build

# Build Rust chart kernel (development)
cd crates/iyou_chart_kernel
maturin develop --release

# Build Rust chart kernel (production wheel)
cd crates/iyou_chart_kernel
maturin build --release

# Install Rust kernel into Django environment
uv pip install crates/iyou_chart_kernel/target/wheels/iyou_chart_kernel-*.whl
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

### ✅ Resolved Items

1. **✅ CSS Framework Conflict**: Resolved via Hybrid CSS Matrix (Tailwind + Bootstrap)
2. **✅ Rust Kernel Integration**: Fully wired with automatic detection and fallback
3. **✅ Monorepo Structure**: Unified Django and Rust codebases
4. **✅ CSRF/Session Secure-Cookie Fix**: `CSRF_COOKIE_SECURE = not DEBUG` and `SESSION_COOKIE_SECURE = not DEBUG` in `config/settings.py` — cookies stay HTTP-safe for local development while remaining Secure in production.
5. **✅ Layer 2 Header Refactor**: 3-logo branding cluster (Namecharts logo + tagline + harp seal) with a floating hamburger dropdown card (`templates/includes/_nav.html`).

### 🚧 Active Tech Debt

1. **Duplicate HUD app**: `apps/generator/hud/` is a dead-code copy of `apps/hud/` — same URL patterns.
2. **Monolithic `parsed_data` JSON blob**: All genealogical data in a single field; no SQL-level indexing on individuals.
3. **`place_name_utils.py`**: 3,229-line single file with massive hardcoded dictionaries — candidate for JSON data file extraction.
4. **Test sprawl**: ~79 test/debug files in `tests/` with mixed conventions.

### 🎯 Future Enhancements

1. **Rust Kernel Performance**: Build and integrate the PyO3 chart kernel for production use
2. **Docker Optimization**: Multi-arch builds and smaller final image size
3. **CSS Optimization**: Further Tailwind purge configuration and critical CSS extraction
4. **Kubernetes**: Horizontal pod autoscaling based on chart generation load
5. **Dockerfile Python version**: Was pinned to 3.12 despite project requiring 3.13 (now fixed in multi-stage refactor).
6. **Hardcoded test paths**: Many test files use `sys.path.append("/home/user/CODE_BASE/namechart")`.

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
| Rust chart kernel | `crates/iyou_chart_kernel/` | Integrated PyO3 chart kernel (Rust, `Cargo.toml`, `src/`, `tests/`) |
