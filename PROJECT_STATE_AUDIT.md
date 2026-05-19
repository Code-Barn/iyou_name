# iyou_name — Project State Audit

> Repository: `iyou_name` (formerly `namecharts_django`, ecosystem brand: **Namecharts (aka iyou_name)**)
> Generated: 2026-05-19

---

## 1. Current Project Layout & Frameworks

### 1.1 Technology Stack

| Component | Version / Choice |
|-----------|------------------|
| **Python** | 3.13+ (`.python-version`), Dockerfile still on `python:3.12-slim` |
| **Django** | 6.0.x (settings header: `Django 6.0`, migration timestamps confirm 6.0) |
| **Package Manager** | `uv` — uses `uv sync`, `uv run`, `uv add`; `uv.lock` present |
| **Database** | PostgreSQL via `dj-database-url`; Docker compose also provisions Postgres |
| **Image Library** | Wand 0.6.13 (Python ctypes wrapper for ImageMagick) |
| **Frontend** | Vanilla JS, Bootstrap 5, static HUD JS |
| **Testing** | `unittest`/Django TestCase, Playwright e2e (`@playwright/test` ^1.57.0) |
| **Formatter/Linter** | `ruff` 0.14.x (installed as dev dependency) |

### 1.2 Project Identity

- `pyproject.toml` line 2: `name = "namechart"` — **needs update to `iyou_name`**
- `package.json` line 2: `"name": "namechart"` — **needs update**
- `pyproject.toml` line 3: `version = "0.1.0"`

### 1.3 Directory Layout

```
/Users/macuser/CODE_BASE/iyou_name/
├── apps/                          # All Django applications
│   ├── browse/                    # Individual browsing (empty models)
│   ├── chart_storage/             # Persistent settings, buffers, photos
│   │   ├── migrations/
│   │   ├── individual_settings_views.py
│   │   ├── photo_views.py
│   │   ├── preset_views.py
│   │   └── storage_views.py
│   ├── charts/                    # Chart serving (empty models)
│   │   └── templates/
│   ├── core/                      # Shared utilities, middleware, rate-limiting
│   │   ├── grampsweb/             # GrampsWeb API client
│   │   ├── middleware.py
│   │   ├── auth_security.py       # Auth monitor
│   │   ├── rate_limiting.py
│   │   └── templates/
│   ├── generator/                 # Chart generation engine (HEAVY)
│   │   ├── hud/                   # DUPLICATE HUD app (identical to apps/hud)
│   │   ├── migrations/
│   │   ├── models.py              # GedcomFile, GedcomShare
│   │   ├── models/                # Split model files (gedcom_file.py)
│   │   ├── template_mapping.py
│   │   ├── utils/
│   │   │   ├── prototype/         # 7 generation generators
│   │   │   │   ├── prototype_image_1generator.py .. 7generator.py
│   │   │   │   ├── individual_printer.py    (1197 lines)
│   │   │   │   ├── date_utils.py
│   │   │   │   ├── place_name_utils.py      (3229 lines)
│   │   │   │   └── tests/                  (debug position scripts)
│   │   │   ├── simple_buffer_manager.py     (417 lines)
│   │   │   ├── sunbeam_position_calculator.py (269 lines)
│   │   │   ├── settings_validator.py
│   │   │   └── name_utils.py
│   │   └── views.py
│   ├── hud/                       # Interactive HUD (DUPLICATE of generator/hud)
│   │   ├── static/hud/js/         # hud.js, hud-organized.js
│   │   └── templates/hud/
│   ├── parser/                    # GEDCOM parsing (PersonData dataclass)
│   ├── selector/                  # Individual selection
│   ├── upload/                    # File upload
│   └── users/                     # CustomUser, DID/VC system
│       ├── did_utils.py
│       ├── did_views.py
│       └── did_rust_wrapper/      # Rust FFI (hardcoded dev path)
├── config/
│   ├── settings.py
│   ├── urls.py                    # Root URL conf
│   └── wsgi.py / asgi.py
├── tests/                         # 79 test/debug files (sprawl)
├── deploy/
│   ├── docker/
│   └── kubernetes/
├── staticfiles/                   # Collected static (admin, Bootstrap, flags, PDFs)
├── docs/
├── pyproject.toml
├── uv.lock
├── Dockerfile
└── docker-compose.yml
```

---

## 2. Domain Model & Database Matrix

### 2.1 Model Inventory

| App | Model | Fields | Purpose |
|-----|-------|--------|---------|
| `users` | `CustomUser` | `did`, `did_method`, `did_key`, `vcs` (JSON) | Extends `AbstractUser` with Decentralized Identity |
| `generator` | `GedcomFile` | `user` (FK), `file` (FileField), `parsed_data` (JSON), `home_person_id`, `is_processed`, `processing_date`, `last_activity` | Uploaded GEDCOM with inline parsed data blob |
| `generator` | `GedcomShare` | `gedcom_file` (FK), `shared_with` (FK), `can_edit`, `shared_by` (FK) | User-to-user GEDCOM sharing |
| `chart_storage` | `UserStorageQuota` | `user` (1-to-1), `bytes_used`, `bytes_limit` (500MB default) | Per-user buffer storage tracking |
| `chart_storage` | `UserSettingsPreset` | `user` (FK), `name`, `description`, `settings_json`, `is_default` | Named preset configurations |
| `chart_storage` | `GedcomInfo` | `user` (FK), `gedcom_hash`, `filename`, `display_name`, `individual_count` | Metadata about processed GEDCOM files |
| `chart_storage` | `IndividualSettings` | `user` (FK), `gedcom_hash`, `individual_id`, `settings_json`, `is_home_person` | Per-individual settings |
| `chart_storage` | `ChartBuffer` | `user` (FK), `gedcom_hash`, `individual_id`, `generation`, `settings_hash`, `chart_version`, `buffer_file` (FileField) | Long-term buffer cache (disk-backed) |
| `chart_storage` | `IndividualPhoto` | `user` (FK), `gedcom_hash`, `individual_id`, `photo` (ImageField), `file_size`, `width`, `height` | Per-individual profile photos |
| `parser` | `PersonData` | **dataclass** (not Django Model) — see below | In-memory individual representation |

### 2.2 PersonData Dataclass (`apps/parser/models.py`)

The core domain entity is NOT a Django Model — it is a `@dataclass` with:
- Identity: `id`, `given_name`, `surname`, `full_name`, `sex`, `title`, `honorific`, `suffix`, `occupation`
- Life events: `birth_date`, `birth_place`, `death_date`, `death_place`, `burial_place`
- Binary flags: `birth_flag`, `death_flag`
- Relationships: `father`, `mother`, `spouse` (List[str]), `children` (List[str])
- Siblings: `siblings`, `half_siblings`, `step_siblings`, `all_siblings`
- Alternative parents: `adoptive_parents`, `foster_parents`, `step_parents`, `adopted`
- Spousal children tree: `spouses_children` (Dict[str, List[str]])
- Grandparents: `paternal_grandfather`, `paternal_grandmother`, `maternal_grandfather`, `maternal_grandmother`
- Events: `events` (List[Dict])

### 2.3 Data Storage Architecture

```
GEDCOM file (upload)
  → Parser: PersonData objects → Dict → serialized into GedcomFile.parsed_data (JSONField)
  → Rendered: Deserialized back to PersonData → fed to generators
```

Key insight: **All genealogical data lives in a single JSON blob** on `GedcomFile.parsed_data`. There are no normalized SQL tables for individuals, families, or events. This is a monolithic document-store pattern inside a relational database.

### 2.4 Recursive Mapping Structure

Multi-generation ancestor resolution is done **entirely in Python code**, not SQL:
- Each generator (1gen–7gen) traces ancestor IDs through `father`/`mother` fields
- The 7gen generator recursively resolves 2^N − 1 ancestors by walking `PersonData.father` → `PersonData.mother` chains
- The `sunbeam_position_calculator.py` provides the mathematical layout for up to 10 generations using concentric-square positioning

---

## 3. Image Generation Engine Specifics

### 3.1 Rendering Pipeline Files

| File | Lines | Role |
|------|-------|------|
| `apps/generator/utils/prototype/individual_printer.py` | **1,197** | Core text rendering: font metrics, coordinate math, rotation, multi-line name layout, outside stroke |
| `apps/generator/utils/prototype/prototype_image_1generator.py` | 427 | 1-gen chart: single person, flag overlay on background |
| `apps/generator/utils/prototype/prototype_image_2generator.py` | 524 | 2-gen: primary + parents in rotated quadrants |
| `apps/generator/utils/prototype/prototype_image_3generator.py` | ~500 | 3-gen: adds grandparents |
| `apps/generator/utils/prototype/prototype_image_4generator.py` | ~600 | 4-gen: adds great-grandparents |
| `apps/generator/utils/prototype/prototype_image_5generator.py` | ~700 | 5-gen |
| `apps/generator/utils/prototype/prototype_image_6generator.py` | ~800 | 6-gen |
| `apps/generator/utils/prototype/prototype_image_7generator.py` | **873** | 7-gen: most complex, composites 6-gen overlay |
| `apps/generator/utils/prototype/date_utils.py` | 391 | Date parsing/formatting (MONTH_ABBREVIATIONS, date format selection) |
| `apps/generator/utils/prototype/place_name_utils.py` | **3,229** | Place abbreviation, flag image path resolution (very large) |
| `apps/generator/utils/name_utils.py` | ~250 | Name splitting, display formatting, hyphenation logic |
| `apps/generator/utils/settings_validator.py` | — | Coerces user settings dict to typed values (Color, int, bool) |
| `apps/generator/utils/simple_buffer_manager.py` | 417 | In-memory buffer cache, BytesIO management, generator routing |
| `apps/generator/utils/sunbeam_position_calculator.py` | 269 | Concentric-square mathematical positioning for 8–10 gen |

### 3.2 Primary Data Flow (DB → Canvas → File)

```
1. Client request (individual_id, template, user_settings)
       │
2. GedcomFile.objects.get(id=file_id)
   → gedcom_file.parsed_data (JSON blob)
       │
3. Deserialize dicts → PersonData dataclass objects
   person_data_objects[person_id] = PersonData(**person_data)
       │
4. template_mapping.py resolves template ID → module + function
   e.g., "3" → prototype_image_3generator.generate_prototype_3gen_preview
       │
5. Generator function called with (primary_individual, family_data, template_type, user_settings)
       │
6. Inside generator:
   a) Validate settings via get_validated_settings(settings_schema)
   b) Load preview template PNG from static/hud/images/preview_image_templates/
   c) Create Wand Image + Drawing context
   d) Draw background rectangle
   e) Render flag overlay (composite flag PNG on background)
   f) Call print_individual() for each ancestor position
      - print_individual sets: font, font_size, fill_color
      - Translates to center_x/center_y
      - Applies rotation (0°, 90°, 180°, 270°)
      - Uses get_font_metrics() for text sizing
      - Draws each text line at calculated coordinates
      - Supports outside stroke (duplicate text with stroke behind)
   g) For "preview" → return PNG via create_preview_buffer()
   h) For "final" → composite onto US_LETTER_XGEN_BW.pdf base template
                      → return PDF via create_pdf_buffer()
       │
7. Buffer returned as BytesIO → HTTP response
   - Preview: image/png
   - Final: application/pdf (attachment)
```

### 3.3 Coordinate System

- Standard canvas: **1950 × 1950 px** at **300 DPI**
- 10-gen canvas: **4700 × 4700 px**
- Image center: (975, 975)
- Preview templates stored at: `apps/hud/static/hud/images/preview_image_templates/`
- Final base templates stored at: `staticfiles/charts/images/base_image_templates/US_LETTER_{1-7}GEN_BW.pdf`
- Rotational positioning: ancestors placed at 0°, 90°, 180°, 270° around center
- Math: rotated_x = dx·cos(θ) − dy·sin(θ), rotated_y = dx·sin(θ) + dy·cos(θ)

### 3.4 Caching / Buffer System

Two-layer caching:
1. **In-memory** (`SimpleBufferManager`): Settings-hash keyed, invalidated on change
2. **Disk-backed** (`ChartBuffer` model via FileField): User-specific, persistent across restarts

---

## 4. Federation & Identity Status

### 4.1 Authentication

| Aspect | Status |
|--------|--------|
| Auth backend | Standard `django.contrib.auth.backends.ModelBackend` |
| User model | `CustomUser(AbstractUser)` — swappable |
| Login flow | Template-based (login.html, password change/reset templates) |
| Session engine | DB-backed (`django.contrib.sessions.backends.db`) |
| Password validators | Default Django 6.0 validators |
| Rate limiting | Custom `RateLimitMiddleware` in `apps/core/rate_limiting.py` |
| Auth monitoring | In-memory `AuthenticationMonitor` in `apps/core/auth_security.py` |
| Registration | Not currently active — `django_registration` is commented out |
| Social/OAuth | **None** — no `django-allauth`, `python-social-auth`, or OAuth2 present |

### 4.2 Decentralized Identity (DID) System

**Status: Experimental / Hybrid**

- Model fields on `CustomUser`: `did`, `did_method`, `did_key`, `vcs` (JSON array)
- Three-backend architecture:
  1. **Rust FFI backend** (`apps/users/did_rust_wrapper/`) — production path, hardcoded library path: `/home/user/CODE_BASE/did_rust/target/release/libdid_rust.so`
  2. **didkit** (Python package) — secondary, tried on import
  3. **Python mock** — fallback (`did:key:mock-{uuid}`)
- API endpoints (all behind `@login_required`):
  - `POST /users/api/did/generate/` — generate DID for user
  - `GET /users/api/did/` — get user's DID
  - `POST /users/api/did/verify/` — verify a VC
  - `POST /users/api/did/vc/issue/` — issue a VC
  - `POST /users/api/did/vc/add/` — add VC to user
  - `GET /users/api/did/vcs/` — list VCs
  - `GET /users/api/did/vcs/type/<str>/` — filter by type

### 4.3 Ecosystem / Microservice Hooks

| Integration | Status |
|-------------|--------|
| **GrampsWeb** | REST API client implemented (`apps/core/grampsweb/client.py`), gated by `GENEALOGY_MODE=grampsweb` |
| **WebTrees** | Config present in settings.py (`WEBTREES_URL`, `WEBTREES_API_URL`, `WEBTREES_API_TOKEN`) but no client module |
| **External genealogy URL** | Config-only, no integration code |
| **Redis** | URL configured but no explicit caching code using Redis |
| **Docker deployment** | `docker-compose.yml` + Kubernetes manifests in `deploy/` |
| **Polly** (family polling) | Mentioned in README but no code found in project |

**Assessment**: This project is largely **monolithic with grafted-on federation**. The DID system is a standalone feature with no shared auth provider integration. The genealogy integrations are thin API wrappers. No OpenID Connect, OAuth2, or internal service mesh patterns are present.

---

## 5. Technical Debt & Disruptions

### 5.1 Hardcoded Absolute Paths (37+ occurrences — CRITICAL)

These will **immediately break** any deployment not at the exact original path:

**`template_mapping.py`** (lines 26–69): All 7 template paths hardcoded:
```python
"filename": "/home/user/CODE_BASE/namechart/apps/charts/static/charts/images/base_image_templates/US_LETTER_1GEN_BW.pdf"
```

**Test files** — systematic use of `sys.path.append("/home/user/CODE_BASE/namechart")`:
- `tests/test_buffer_system.py`, `test_buffer_simple.py`, `test_enhanced_buffer.py`
- `tests/test_3gen_byers.py`, `test_3gen_fix.py`, `test_3gen_positioning.py`, `test_3gen_real_data.py`
- `tests/test_enhanced_generator.py`, `test_parent_positions.py`
- `tests/test_pdf_generation*.py`, `test_preview_debug.py`
- `tests/debug_*.py` (at least 6 files)
- `tests/find_winfield.py`, `tests/final_test.py`, `tests/generate_visual_test.py`
- `tests/simple_preview_test.py`, `tests/test_parser_fix.py`
- `tests/test_responsive_css.py`, `tests/test_zoom_functionality.py`

**Output paths in tests**: Many write output to hardcoded `/home/user/CODE_BASE/namechart/` (e.g., `test_3gen_byers.png`, `test_3gen_positioning.png`, `prototype_4gen_output_test.png`).

**Production code**:
- `apps/users/did_rust_wrapper/rust_ffi.py:39`: Hardcoded `.so` path
- `prototype_image_1generator.py` flag font path: `/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf`

### 5.2 Duplicate HUD Application

Two nearly identical HUD implementations exist:

| Path | Status |
|------|--------|
| `apps/hud/` | Appears to be the **active** one (referenced in `INSTALLED_APPS`) |
| `apps/generator/hud/` | **Duplicate** — same URL patterns, same view code, same templates |

Both define `app_name = "hud"`, both have `urls.py` with identical patterns. The `generator/hud/` is a dead code path. This will cause namespace collisions if ever imported.

### 5.3 Testing Sprawl & Fragility

- **79 files** in `/tests/` directory — mix of `unittest.TestCase`, standalone functions, Playwright specs, debug scripts, and one-off verification scripts
- No consistent test runner configuration (many files use `sys.path` manipulation instead of Django's test discovery)
- Test data: binary `.spec.ts` files, `.pdf` debug outputs, `.png` snapshots committed to repo
- Debug scripts in production version-controlled directory: `apps/generator/utils/prototype/tests/debug_*gen_positions*`

### 5.4 Dockerfile Version Mismatch

- `Dockerfile` uses `python:3.12-slim`
- Project requires `python >= 3.13`
- Will break at `uv sync` due to Python version constraint

### 5.5 Place Name Utils Bloat

`apps/generator/utils/prototype/place_name_utils.py` is **3,229 lines** — the single largest file. It contains massive dictionaries of county/country abbreviations and flag path generation. Should be split or moved to a data file (JSON/YAML).

### 5.6 Monolithic Parsed Data

`GedcomFile.parsed_data` is a JSON blob containing ALL individuals and families. This means:
- No SQL-level querying for individuals
- Must deserialize entire dataset to access one person
- No indexing, no partial loading
- Memory pressure proportional to total GEDCOM size

### 5.7 In-Memory Auth Monitor

`apps/core/auth_security.py` keeps failed-login tracking in a process-local `defaultdict`. This is **reset on every server restart** and **not shared across worker processes** — effectively non-functional in production.

### 5.8 Commented Legacy Imports

`apps/generator/views.py` lines 14–22: Old direct import pattern is commented out:
```python
# from apps.generator.utils import (
#    image_1generator,
#    image_2generator, ...
# )
```

### 5.9 Other Issues

- `config/settings.py` comment on line 235 references "Django 5.2" (should be 6.0)
- `config/settings.py` line 48: `django_registration` is commented out but present in `EXTERNAL_APPS` list — unused dependency
- `GedcomShare.unique_together` — order matters for composite index creation but is undocumented
- No internationalization present despite `USE_I18N = True`
- `DEFAULT_AUTO_FIELD` repeated (line 243)
- `ChartBuffer` model's `buffer_file` FileField stores potentially large images — no compression or cleanup scheduled
- `Signal handler` in `generator/models.py:86` (`delete_parsed_data`) has an empty body and a TODO comment

---

## Summary

**Project Namecharts (aka iyou_name)** is a Django 6.0 monolithic genealogical chart generator with 7 generation levels, a Wand/ImageMagick rendering pipeline, a DID/VC identity experiment, and integrations with GrampsWeb/WebTrees. The rendering engine is the heart of the project — 8 generator scripts, a 1,197-line individual printer, and a 3,229-line place-name utility produce family tree charts as PNG previews or PDF output.

**Key rendering files discovered:**
- `apps/generator/utils/prototype/individual_printer.py` — core text/position engine
- `apps/generator/utils/prototype/prototype_image_1generator.py` through `prototype_image_7generator.py` — 7 generation-level generators
- `apps/generator/utils/prototype/date_utils.py` — date formatting
- `apps/generator/utils/prototype/place_name_utils.py` — place abbreviation + flag paths
- `apps/generator/utils/name_utils.py` — name parsing/display
- `apps/generator/utils/settings_validator.py` — settings coercion
- `apps/generator/utils/simple_buffer_manager.py` — buffer cache + routing
- `apps/generator/utils/sunbeam_position_calculator.py` — 8–10 gen math
- `apps/generator/template_mapping.py` — routes template IDs to generator functions
- `apps/generator/views.py` — `generate_final_chart` entry point

The codebase has significant technical debt concentrated in hardcoded filesystem paths, duplicate HUD applications, a sprawling test directory, and oversized single-file utilities. The architecture is fundamentally sound but will benefit from targeted extraction of the rendering pipeline into a standalone module and a systematic path-hygiene pass.
