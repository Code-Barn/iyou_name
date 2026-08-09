# GEDCOM Parsing Pipeline — Full Audit

> Audit date: 2026-07-19
> Status: Reference document for future Rust parser integration

---

## 1. File Locations

| Component | Path |
|---|---|
| Parser script | `apps/parser/utils/gedcom_parser.py` (1095 lines) |
| PersonData model | `apps/parser/models.py` (77 lines) |
| GedcomFile DB model | `apps/generator/models/gedcom_file.py` (99 lines) |
| Upload view | `apps/upload/views.py` (298 lines) |
| Upload template | `apps/upload/templates/upload/upload_file.html` |
| Security pre-scan | `apps/core/file_validation.py` |

---

## 2. Data Flow (Upload Pipeline)

```
User uploads .ged/.gedcom
  → upload_and_generate() view
    → validate_uploaded_file()        [file size/type/content security scan]
    → GedcomFile.objects.create()     [saves raw file to disk]
    → convert_to_utf8(bytes)          [charset-normalizer detection + fallback strategies]
    → parse_gedcom_data(content_str)  ← THE BOTTLENECK (6-pass ged4py + raw line scan)
    → person.to_dict() for each individual
    → GedcomFile.parsed_data = {      [single JSONField blob]
        "individuals": {id: {person_dict}},
        "families":    {id: {family_dict}},
        "root_individuals": [id, ...]
      }
    → redirect to selector view
```

---

## 3. Fields Extracted from GEDCOM Records

### Python `PersonData` (parser) — 42 fields

| Field | Source |
|---|---|
| `id` | XREF ID (e.g. `@I1@`) stripped to `I1` |
| `full_name` | NAME record `.format()` or `given + surname` |
| `given_name` | NAME.GIVN |
| `surname` | NAME.SURN |
| `birth_date` | BIRT.DATE |
| `birth_place` | BIRT.PLAC |
| `death_date` | DEAT.DATE |
| `death_place` | DEAT.PLAC |
| `burial_place` | BURI.PLAC |
| `father` / `mother` | FAMC links + PEDI correction |
| `spouse` / `children` | FAMS + FAM.CHIL links |
| `siblings` / `half_siblings` / `step_siblings` | Computed from shared parents |
| `adoptive_parents` / `foster_parents` / `step_parents` | PEDI, _FREL, _MREL tags |
| `spouses_children` | Dict mapping spouse→children |
| `events` | List of {tag, date, place, description} for BIRT/DEAT/CHR/BURI/EVEN/ADOP/etc. |
| `sex` | SEX tag |
| `title` / `honorific` / `suffix` | NAME.TITL, NAME.NPFX, NAME.NSFX |
| `occupation` | OCCU tag |
| `adopted` | ADOP event presence |
| `paternal_grandfather` etc. | Declared but not populated in parser |

### Rust `PersonData` (chart kernel) — 8 fields

```rust
pub struct PersonData {
    pub id: String,
    pub full_name: String,
    pub given_name: String,
    pub surname: String,
    pub birth_date: Option<String>,
    pub birth_place: Option<String>,
    pub death_date: Option<String>,
    pub death_place: Option<String>,
}
```

> **Gap**: Rust is a strict subset of the Python model. A new `GedcomPersonData` struct
> would be needed for parsing, with a projection down to the 8-field `PersonData` for chart rendering.

---

## 4. Storage Model

Parsed data is stored as a **JSON blob** in `GedcomFile.parsed_data` (Django `JSONField`):

```json
{
  "individuals": {
    "I1": { "full_name": "...", "father": "I2", "mother": "I3", ... },
    "I2": { ... }
  },
  "families": {
    "F1": {
      "husband": "I1",
      "wife": "I2",
      "children": ["I3", "I4"],
      "events": [{"tag": "MARR", "date": "...", "place": "..."}]
    }
  },
  "root_individuals": ["I1"]
}
```

No separate `Person` or `Family` DB tables — the entire parsed tree is serialized into one JSON column. The full blob is loaded into memory on every request that needs it.

---

## 5. Identified Bottlenecks

| Bottleneck | Severity | Details |
|---|---|---|
| **ged4py `GedcomReader`** | **High** | Two full passes over the file: one for INDI records, one for FAM records. Each pass creates Python objects with deep attribute traversal (`record.sub_tag()`, `record.sub_tags()`). |
| **3rd raw-line PEDI pass** | **High** | After ged4py parsing, the code does a **third pass** by splitting `gedcom_content` into lines and scanning for PEDI/_FREL/_MREL tags with nested lookahead loops (lines 617–739). This is O(n × lookahead) on the raw string. |
| **6-pass sequential architecture** | **High** | Pass 1 (INDI scan), Pass 2 (FAM linking), Pass 3 (root detection), Pass 4 (raw line scan), Pass 5 (pedigree correction), Pass 6 (sibling classification). O(6n) over all records. |
| **Synchronous in request cycle** | **High** | Entire pipeline blocks the HTTP response. Large files (>5MB) cause request timeouts. |
| **Python GIL contention** | Medium | Single-threaded parse, no multiprocessing. CPU-bound text processing serialized behind GIL. |
| **Sibling computation** | Medium | O(n²) nested loop over all individuals to find half-siblings via shared parents (lines 958–977). |
| **Full JSON serialization on read** | Medium | Every individual is serialized via `dataclasses.asdict()` → dict → stored as JSON. On read, the entire JSON blob is deserialized for every page load. |
| **Excessive `print()` calls** | Low | ~50+ `print()` debug statements in production code (not `logger.debug()`), each triggering I/O. |
| **`charset_normalizer` + multi-strategy decode** | Low | Tries 4+ decoding strategies with string replacement character cleanup. |

---

## 6. Rust Workspace — Integration Assessment

### Current PyO3 Entry Point (`src/python_module.rs`)

Single function exposed:

```python
from iyou_chart_kernel import render_chart_from_json
image_bytes = render_chart_from_json(generation, primary_json, ancestors_json, settings_json)
```

Module name: `iyou_chart_kernel`, registered via `#[pymodule]`.

### Existing Rust Structs — Alignment

| Rust Struct | Python Equivalent | Compatible? |
|---|---|---|
| `PersonData` (8 fields) | `PersonData` (42 fields) | Partial — Rust is a **subset** |
| `AncestorData` (`HashMap<String, PersonData>`) | `family_data["individuals"]` | Maps 1:1 |
| `ChartSettings` (11 fields) | N/A (visual config) | Separate concern |

### `utils/` Module

Currently contains only `validate_settings()`. **No parser exists.** The slot for `src/utils/parser.rs` is open.

### `ChartError` Enum

```rust
pub enum ChartError {
    MagickError, InvalidCoordinate, FontMetricsError,
    CompositionError, InvalidSettings, EnvironmentNotInitialized
}
```

No parsing-related error variants exist yet.

### Proposed Module Layout

```
src/utils/
  mod.rs              (existing — validate_settings)
  gedcom_parser.rs    (NEW — line-by-line streaming parser)
  gedcom_types.rs     (NEW — rich PersonData + Family structs)
```

### Proposed PyO3 Function

```rust
#[pyfunction]
pub fn parse_gedcom(content: &str) -> PyResult<String> {
    // 1. Single-pass line-by-line state machine (no ged4py dependency)
    // 2. Extract INDI records, FAM records, PEDI/_FREL/_MREL in one pass
    // 3. Return serde_json::to_string() of the full family_data dict
    //    matching the exact shape Python expects
}
```

### Conceptual FFI Layout

```
Python (upload view)
  │
  │  raw GEDCOM bytes (or UTF-8 string)
  │
  ▼
parse_gedcom_to_json(content: &str) -> PyResult<String>
  │  src/utils/parser.rs
  │  ┌─────────────────────────────────┐
  │  │ Line-by-line streaming parse    │
  │  │ Single pass (no 6-pass overhead)│
  │  │ Build HashMap<id, FullPerson>   │
  │  │ Build HashMap<id, Family>       │
  │  │ Detect root individuals         │
  │  │ Resolve PEDI/_FREL/_MREL inline │
  │  └─────────────────────────────────┘
  │
  │  Returns JSON string:
  │  { "individuals": {...}, "families": {...}, "root_individuals": [...] }
  │
  ▼
Django view receives JSON string → json.loads() → store in JSONField
```

---

## 7. Key Design Decisions

| Decision | Options | Recommendation |
|---|---|---|
| **PersonData struct split** | A) Single struct with all 42 fields, B) Separate `GedcomPersonData` + render `PersonData` | **B** — keep rendering struct lean, add `GedcomPersonData` in `gedcom_types.rs` |
| **ged4py dependency** | A) Rust-native parser from scratch, B) Use `gedcom` crate, C) Line-by-line `&str` scanner | **C** — you only need INDI/FAM XREF + tag extraction; a hand-rolled line scanner avoids crate bloat and matches the raw scan you already do in Python |
| **Output format** | A) Return JSON string to Python, B) Return Python dict via PyO3 | **A** — JSON string is zero-copy at the FFI boundary and matches the existing `render_chart_from_json` pattern |
| **Encoding** | A) Rust handles charset detection, B) Python pre-decodes to UTF-8 | **B** — `charset_normalizer` is Python-native; pass clean `&str` to Rust |
| **Registration** | Single `#[pymodule]` with both functions | Add `parse_gedcom` next to `render_chart_from_json` in `python_module.rs` |
| **Dependencies** | No new crates needed | `regex` and `once_cell` already exist in `Cargo.toml` |

---

## 8. Expected Performance Gains

| Aspect | Python (ged4py) | Rust (proposed) |
|---|---|---|
| Parse passes | 3+ (ged4py INDI + ged4py FAM + raw line scan) | 1 single-pass state machine |
| Object creation | Per-field Python attribute access | Zero-alloc `&str` slices |
| Sibling computation | O(n²) Python loops | O(n) hash-set intersection |
| Serialization | `dataclasses.asdict()` → dict | `serde_json` direct to string |
| Memory per individual | ~2.5KB (33-field dataclass + dict) | ~400B (compact struct) |
| 10K individuals estimate | ~25MB + 6 iterations | ~4MB + 1 iteration |
| GIL blocking | Full request cycle | None (returns immediately) |
| Memory model | Full Python object graph | Borrowed slices, stack-allocated |

---

## 9. Next Steps (When Resumed)

1. Scaffold `src/utils/gedcom_parser.rs` and `src/utils/gedcom_types.rs` with a working line-by-line parser
2. Register `parse_gedcom` in the `#[pymodule]`
3. Wire into `apps/upload/views.py` as an optional replacement (feature flag or env var toggle)
4. Validate output matches existing `parse_gedcom_data()` shape with the existing test suite
5. Benchmark against large GEDCOM files (50MB+) to measure throughput improvement
