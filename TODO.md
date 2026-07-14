# TODO — iyou_name (Genealogy Registry)

**Orchestrated from:** `omni_social` (central hub)
**Last synced:** 2026-07-13

---

## Layer 0 — Ecosystem Standardization

> Templates generated via `omni_social/generate_templates.py`. Do not edit
> `_ecosystem_bar.html` or `_standard_header.html` manually — changes will be
> overwritten on next regeneration. Edit the canonical source in omni_social instead.

- [x] `pt-5` removed from `_standard_header.html` — **Done 2026-07-13** (coordinated from omni_social)
- [x] `core/base.html` body classes added (`bg-gray-100 min-h-screen`) — **Done 2026-07-13** (local agent)
- [x] **Ecosystem bar gap drift:** Bootstrap CSS loaded in `core/base.html` (line 21-23) interferes with Tailwind's `gap-4` on the ecosystem bar. Add scoped reset: `#sovereign-ecosystem-topbar a, #sovereign-ecosystem-topbar span { margin: 0; padding: 0; }` to `_ecosystem_bar.html` or a `<style>` block in `base.html`. Verify spacing matches other repos visually. — **Done 2026-07-14** (local agent, inline `<style>` in `_ecosystem_bar.html`)

## Layer 1 — PKCE / Auth

- [x] PKCE ingress verified: `PkceAuthMixin` with `oidc_states` dict, 300s prune cycle — **Done 2026-07-13**

## Layer 2 — App-Specific

- [ ] **(Potential)** Bootstrap → Tailwind migration: iyou_name is the only repo using Bootstrap (`core/base.html` line 21-23). Dual-framework hybrid with `preflight: false`. Page templates deeply use Bootstrap classes (`container`, `d-flex`, `card`, `list-group`, `form-control`, `navbar`, `data-bs-toggle`, Bootstrap Icons). *Not committed — pending decision.*

---
