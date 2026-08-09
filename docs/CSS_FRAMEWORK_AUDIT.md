# CSS Framework Audit — Bootstrap → Tailwind Migration Assessment

> Audit date: 2026-07-19
> Status: Feasibility evaluation for pure Tailwind migration

---

## 1. Current Stack Overview

| Layer | Technology | Status |
|---|---|---|
| **CSS Framework** | Bootstrap 5.x (vendored `bootstrap.min.css`, 228KB) | Active — 28/30 templates |
| **Icon Set** | Bootstrap Icons (vendored `bootstrap-icons.css`, 96KB) | Active — ~30 icon classes |
| **Tailwind CSS** | Referenced via `static/css/output.css` | **BROKEN** — file does not exist |
| **Tailwind CDN** | `<script src="https://cdn.tailwindcss.com">` | **COMMENTED OUT** in base.html |
| **Dark Mode** | CSS custom properties (`html.dark {}`) + Tailwind `dark:` prefix | Split system |
| **Preprocessor** | None | Plain CSS only |

### Tailwind Build Pipeline — Non-Functional

| Artifact | Status |
|---|---|
| `tailwind.config.js` | **MISSING** |
| `postcss.config.js` | **MISSING** |
| `static/css/output.css` | **MISSING** (referenced in base.html:131) |
| `includes/_tailwind_safe_init.html` | **MISSING** (referenced in base.html:142) |
| `package.json` tailwindcss dep | **MISSING** |
| CDN script | **COMMENTED OUT** (base.html:130) |

**Conclusion:** Tailwind is currently inert. The two templates using Tailwind classes (`_ecosystem_bar.html`, `_standard_header.html`) are rendering **unstyled** unless `output.css` is somehow generated outside the repo.

---

## 2. Template Inventory (30 files)

### Bootstrap-Only Templates (28 files)

| App | Template | Key Bootstrap Components |
|---|---|---|
| **core** | `base.html` | Navbar, container, grid, footer |
| **core** | `components/individual_header.html` | Flex, list-group, form, collapse |
| **core** | `components/basic_info.html` | List-group, typography |
| **core** | `components/family_info.html` | List-group, buttons, collapse, badges |
| **core** | `components/locations.html` | List-group |
| **core** | `components/back_button.html` | Button |
| **hud** | `display_tree.html` | Cards, buttons, forms, progress, badges |
| **hud** | `error.html` | Card, alert, buttons |
| **hud** | `settings/1gen_settings.html` | Forms (range, color, select) |
| **hud** | `settings/2gen_settings.html` | Forms |
| **hud** | `settings/3gen_settings.html` | Forms |
| **hud** | `settings/4gen_settings.html` | Forms, cards |
| **hud** | `settings/5gen_settings.html` | Forms |
| **hud** | `settings/6gen_settings.html` | Forms |
| **hud** | `settings/7gen_settings.html` | Forms |
| **hud** | `settings/default_settings.html` | Forms, alerts |
| **upload** | `upload_file.html` | Card, form, alert |
| **upload** | `error.html` | Card, button |
| **users** | `profile.html` | Table, modals, badges, list-group |
| **users** | `error.html` | Card, alert, buttons |
| **browse** | `browse_individuals.html` | List-group, form, buttons |
| **browse** | `individual_detail.html` | Cards, badges, buttons, grid |
| **browse** | `error.html` | Card, alert, buttons |
| **selector** | `select_individual.html` | Card, table, form, buttons |
| **selector** | `error.html` | Card, alert, buttons |
| **charts** | `generate_chart.html` | Cards, form, grid |
| **charts** | `generate_success.html` | Card, alert, buttons |
| **charts** | `adjust_output.html` | Cards, form, grid |

### Tailwind-Only Templates (2 files)

| Template | Tailwind Classes | Dark Mode |
|---|---|---|
| `templates/includes/_ecosystem_bar.html` | ~40 tokens (fixed, flex, snap, arbitrary values) | `dark:` prefix not used (self-contained dark bg) |
| `templates/includes/_standard_header.html` | ~35 tokens (flex, dark mode, transitions) | Heavy `dark:` prefix usage |

### Mixed Template (1 file)

| Template | Bootstrap | Tailwind |
|---|---|---|
| `apps/core/templates/core/base.html` | Navbar, grid, container, footer (~50 classes) | `bg-gray-100`, `min-h-screen` (2 classes on `<body>`) |

---

## 3. Bootstrap Component Dependency Map

### Critical Components (would require custom replacements)

| Component | Usage Count | Templates | Replacement Effort |
|---|---|---|---|
| **Grid system** (`container`, `row`, `col-md-*`) | ~519 class tokens | 28 templates | Medium — Tailwind grid/flex is simpler |
| **Forms** (`form-control`, `form-label`, `form-range`, `form-select`, `form-check`) | ~1,263 class tokens | 15 templates | **High** — forms are the heaviest dependency |
| **Buttons** (`btn-*`, 15 variants) | ~154 class tokens | 20 templates | Low — Tailwind button patterns are straightforward |
| **Cards** (`card`, `card-body`, `card-header`) | ~82 class tokens | 18 templates | Low — Tailwind `rounded border shadow` patterns |
| **Spacing utilities** (`mb-*`, `mt-*`, `ms-*`, `me-*`, `p-*`) | ~700+ class tokens | All templates | Automatic — Tailwind equivalents exist |

### Interactive Components (require JS replacement)

| Component | Usage | Templates | JS Required |
|---|---|---|---|
| **Modals** | 3 modals (delete, sync, share) | `profile.html` | **Yes** — Alpine.js or Headless UI |
| **Collapse** | Siblings/children toggles, navbar | `family_info.html`, `base.html` | **Yes** — Alpine.js `x-show` or `<details>` |
| **Navbar toggler** | Responsive hamburger menu | `base.html` | **Yes** — Alpine.js or vanilla JS |

### Components with Tailwind Equivalents (no JS)

| Component | Bootstrap Class | Tailwind Equivalent |
|---|---|---|
| Alerts | `alert alert-info` | `bg-blue-50 border border-blue-200 text-blue-800 rounded p-4` |
| Badges | `badge bg-success` | `bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full` |
| Tables | `table table-striped` | Custom via `divide-y` + alternating row colors |
| Progress bars | `progress progress-bar` | `bg-gray-200 rounded-full h-2` + inner `bg-blue-600 h-2 rounded-full` |
| List groups | `list-group list-group-item` | `divide-y rounded-lg border` |
| Input groups | `input-group input-group-text` | `flex` + `rounded-l-lg rounded-r-lg` patterns |

---

## 4. Bootstrap Icons Dependency

~30 unique icon classes used across templates:

| Icon | Used In |
|---|---|
| `bi-moon-fill`, `bi-sun-fill` | Theme toggle |
| `bi-github` | Navbar |
| `bi-globe` | Navbar |
| `bi-arrow-left`, `bi-arrow-right` | Navigation |
| `bi-house`, `bi-house-fill` | HUD navigation |
| `bi-zoom-in`, `bi-zoom-out` | Chart preview |
| `bi-eye`, `bi-eye-slash` | Debug toggle |
| `bi-trash`, `bi-x`, `bi-x-lg` | Delete/close actions |
| `bi-check`, `bi-check-circle-fill` | Success states |
| `bi-bookmark`, `bi-bookmark-check` | Save actions |
| `bi-camera`, `bi-link` | Photo actions |
| `bi-download`, `bi-gear` | Actions |
| `bi-person`, `bi-person-check` | User actions |
| `bi-lock`, `bi-info-circle` | Status indicators |
| `bi-file-earmark-pdf` | File type |

**Replacement options:** Heroicons (Tailwind-native), Lucide Icons, or Phosphor Icons.

---

## 5. Dark Mode Architecture

### Current Split System

| Mechanism | Where | What It Styles |
|---|---|---|
| **CSS custom properties** in `base.html` inline `<style>` | `:root` and `html.dark` selectors | Navbar, footer, body backgrounds, text colors |
| **Tailwind `dark:` prefix** | `_standard_header.html`, `_ecosystem_bar.html` | Header backgrounds, text, borders |
| **JavaScript class toggle** | `base.html` theme toggle script | Adds/removes `dark` class on `<html>` |
| **JavaScript logo swap** | `base.html` theme toggle script | Switches logo images on theme change |

### Tailwind Migration Impact on Dark Mode

With pure Tailwind, dark mode becomes unified via `dark:` prefix on every element. The CSS custom property system in `base.html` (lines 34-100) can be replaced entirely with Tailwind `dark:` variants.

---

## 6. Inline Style Inventory (45 instances)

| Pattern | Count | Migrate To |
|---|---|---|
| `width: 50px; height: 50px; object-fit: cover;` | ~9 | `class="w-[50px] h-[50px] object-cover"` |
| `width: 50px; height: 50px; flex-shrink: 0;` | ~9 | `class="w-[50px] h-[50px] shrink-0"` |
| `max-height: Npx; overflow-y: auto;` | ~5 | `class="max-h-[Npx] overflow-y-auto"` |
| `display: none;` | ~3 | `class="hidden"` or `x-show` |
| `background: none; border: none; cursor: pointer; ...` | ~3 | `class="bg-transparent border-none cursor-pointer"` |
| `height: 60px; width: auto;` | 1 | `class="h-[60px] w-auto"` |
| `font-size: 4rem;` | 1 | `class="text-[4rem]"` |
| `min-height: 200px; background-color: #f8f9fa;` | 1 | `class="min-h-[200px] bg-gray-50"` |

**All 45 inline styles are trivially replaceable with Tailwind arbitrary values.**

---

## 7. JavaScript CSS Manipulation Inventory

| Template | Manipulation | Tailwind Approach |
|---|---|---|
| `base.html` | `classList.add/remove('dark')` | Keep as-is — Tailwind uses same mechanism |
| `base.html` | `classList.add/remove('d-none')` on icons | Replace with `hidden` class |
| `display_tree.html` | `style.display` toggle (debug panel) | Alpine.js `x-show` or `hidden` |
| `display_tree.html` | `className` swap on icons | Alpine.js class binding |
| `display_tree.html` | Dynamic `style.width/height` on preview | Keep as-is (dynamic sizing) |
| `individual_header.html` | `style.display` toggle (search results) | Alpine.js `x-show` |
| `browse_individuals.html` | `style.display` filter | Alpine.js `x-show` with `x-for` |
| `select_individual.html` | `style.display` search filter | Alpine.js `x-show` |
| `profile.html` | Dynamic HTML injection with Bootstrap classes | Rewrite with Tailwind classes |
| `individual_detail.html` | `classList.toggle('d-none')` | `classList.toggle('hidden')` |

---

## 8. Migration Effort Assessment

### Scope Summary

| Metric | Value |
|---|---|
| Total templates | 30 |
| Templates requiring rewrite | 28 (Bootstrap-only) + 1 (mixed) |
| Templates already Tailwind | 2 (no changes needed) |
| Bootstrap class tokens to replace | ~2,200+ |
| Inline styles to convert | 45 |
| JS class manipulations to update | ~12 sites |
| Interactive components needing JS | 3 (modals, collapse, navbar toggler) |
| `hud.css` custom CSS | 204 lines (will need audit) |
| `zoom.css` custom CSS | 279 lines (will need audit) |

### Effort by Section

| Section | Templates | Effort | Notes |
|---|---|---|---|
| **Base layout** | `base.html` | **High** | Navbar, footer, dark mode system — the foundation everything inherits |
| **HUD settings** | 8 settings templates | **Medium** | Repetitive form patterns — template one, replicate to all |
| **HUD display** | `display_tree.html` | **High** | 741 lines, complex JS, responsive preview, debug panel |
| **Core components** | 5 component includes | **Medium** | family_info.html has 32 inline styles |
| **Error pages** | 5 error templates | **Low** | Identical pattern — card + alert + buttons |
| **CRUD pages** | upload, browse, selector, charts, profile | **Medium** | Standard form/table/card patterns |

### Estimated Effort

| Phase | Description | Estimated Time |
|---|---|---|
| 1. Scaffolding | Install Tailwind, configure build pipeline, set up `tailwind.config.js`, heroicons | 1-2 hours |
| 2. Base template | Rewrite `base.html` (navbar, footer, dark mode, theme toggle) | 3-4 hours |
| 3. Error pages | 5 identical patterns — template once, replicate | 1 hour |
| 4. Core components | 5 include templates (family_info is heaviest) | 2-3 hours |
| 5. HUD settings | 8 form-heavy templates with shared patterns | 3-4 hours |
| 6. HUD display | Most complex template — preview, controls, JS integration | 4-5 hours |
| 7. CRUD pages | upload, browse, selector, charts, profile (modals) | 4-5 hours |
| 8. JS migration | Replace `d-none` → `hidden`, Alpine.js for modals/collapse | 2-3 hours |
| 9. Cleanup | Remove Bootstrap CSS/JS, `hud.css` audit, `zoom.css` audit | 1-2 hours |
| **Total** | | **21-29 hours** |

---

## 9. Feasibility Verdict

### ✅ Fully Feasible

| Factor | Assessment |
|---|---|
| **Template count** | 30 templates — manageable scope |
| **Framework dominance** | Bootstrap is 100% of active styling — clean break, no partial migration needed |
| **Tailwind already present** | 2 templates + body class prove the pattern works in this project |
| **Dark mode** | Tailwind `dark:` prefix unifies the current split system |
| **Inline styles** | All 45 are trivial arbitrary-value replacements |
| **Custom CSS** | `hud.css` (204 lines) and `zoom.css` (279 lines) are small — can be audited and inlined |
| **No preprocessors** | No Sass/Less to untangle — plain CSS throughout |
| **Build pipeline** | Already partially configured (Tailwind config in base.html, output.css reference) — just needs completion |

### Recommended Approach

| Step | Action |
|---|---|
| 1 | **Install Tailwind CSS v4** via npm, create `tailwind.config.js` with content paths |
| 2 | **Set up build pipeline** — `npx @tailwindcss/cli -i ./input.css -o ./static/css/output.css --watch` |
| 3 | **Keep Bootstrap Icons** as a separate icon library (or migrate to Heroicons) |
| 4 | **Add Alpine.js** (~15KB) for modals, collapse, and dynamic class toggling |
| 5 | **Rewrite `base.html` first** — this is the foundation; all other templates inherit from it |
| 6 | **Template one HUD settings page**, then replicate pattern to all 7 |
| 7 | **Convert error pages** (identical pattern — do once, copy 5 times) |
| 8 | **Tackle `display_tree.html` last** — most complex, highest risk |
| 9 | **Remove `bootstrap.min.css` and `bootstrap.bundle.min.js`** after full migration |
| 10 | **Delete `hud.css`** duplicate at `apps/generator/hud/static/hud/css/hud.css` |

### Risk Factors

| Risk | Mitigation |
|---|---|
| Tailwind output.css file size (all utilities) | Use `content` paths in config to purge unused classes |
| Dark mode flash on page load | Keep the existing `<! dark mode script>` pattern, just use Tailwind `dark:` |
| Bootstrap Icons removal | Migrate to Heroicons (Tailwind-native, SVG, tree-shakeable) |
| JS `className` manipulation breaks | Replace `d-none` references with `hidden` globally |
| `hud.css` custom styles conflict | Audit and inline as Tailwind `@layer components` |

---

## 10. Files to Modify (Complete List)

### Templates (30 files)

```
apps/core/templates/core/base.html                              ← REWRITE
apps/core/templates/core/components/individual_header.html      ← REWRITE
apps/core/templates/core/components/basic_info.html             ← REWRITE
apps/core/templates/core/components/family_info.html            ← REWRITE (heaviest)
apps/core/templates/core/components/locations.html              ← REWRITE
apps/core/templates/core/components/back_button.html            ← REWRITE
apps/hud/templates/hud/display_tree.html                        ← REWRITE (most complex)
apps/hud/templates/hud/error.html                               ← REWRITE
apps/hud/templates/hud/settings/1gen_settings.html              ← REWRITE
apps/hud/templates/hud/settings/2gen_settings.html              ← REWRITE
apps/hud/templates/hud/settings/3gen_settings.html              ← REWRITE
apps/hud/templates/hud/settings/4gen_settings.html              ← REWRITE
apps/hud/templates/hud/settings/5gen_settings.html              ← REWRITE
apps/hud/templates/hud/settings/6gen_settings.html              ← REWRITE
apps/hud/templates/hud/settings/7gen_settings.html              ← REWRITE
apps/hud/templates/hud/settings/default_settings.html           ← REWRITE
apps/upload/templates/upload/upload_file.html                   ← REWRITE
apps/upload/templates/upload/error.html                         ← REWRITE
apps/users/templates/users/profile.html                         ← REWRITE (modals)
apps/users/templates/users/error.html                           ← REWRITE
apps/browse/templates/browse/browse_individuals.html            ← REWRITE
apps/browse/templates/browse/individual_detail.html             ← REWRITE
apps/browse/templates/browse/error.html                         ← REWRITE
apps/selector/templates/selector/select_individual.html        ← REWRITE
apps/selector/templates/selector/error.html                     ← REWRITE
apps/charts/templates/charts/generate_chart.html               ← REWRITE
apps/charts/templates/charts/generate_success.html             ← REWRITE
apps/charts/templates/charts/adjust_output.html                ← REWRITE
templates/includes/_standard_header.html                        ← NO CHANGE (already Tailwind)
templates/includes/_ecosystem_bar.html                          ← NO CHANGE (already Tailwind)
```

### CSS Files (3 files)

```
apps/core/static/vendor/bootstrap/bootstrap.min.css             ← DELETE
apps/core/static/vendor/bootstrap/icons/bootstrap-icons.css     ← DELETE or KEEP (if keeping BI)
apps/core/static/core/css/style.css                             ← INLINE or DELETE
apps/core/static/core/css/zoom.css                              ← AUDIT + INLINE
apps/hud/static/hud/css/hud.css                                 ← AUDIT + INLINE
apps/generator/hud/static/hud/css/hud.css                       ← DELETE (duplicate)
```

### JavaScript (2 files)

```
apps/core/static/vendor/bootstrap/bootstrap.bundle.min.js       ← DELETE (replace with Alpine.js)
apps/hud/static/hud/js/hud-organized.js                         ← AUDIT (update d-none → hidden)
```

### Build Config (new files)

```
tailwind.config.js                                              ← CREATE
postcss.config.js                                               ← CREATE
package.json                                                    ← UPDATE (add tailwindcss, alpinejs, heroicons)
```
