# TODO — iyou_name (Genealogy Registry)

**Orchestrated from:** `omni_social` (central hub)
**Last synced:** 2026-07-14

---

## Layer 0 — Ecosystem Standardization

> Templates generated via `omni_social/generate_templates.py`. Do not edit
> `_ecosystem_bar.html` or `_standard_header.html` manually — changes will be
> overwritten on next regeneration. Edit the canonical source in omni_social instead.

- [x] `pt-5` removed from `_standard_header.html` — **Done 2026-07-13** (coordinated from omni_social)
- [x] `core/base.html` body classes added (`bg-gray-100 min-h-screen`) — **Done 2026-07-13** (local agent)
- [x] **Ecosystem bar gap drift:** Bootstrap CSS loaded in `core/base.html` (line 21-23) interferes with Tailwind's `gap-4` on the ecosystem bar. Add scoped reset: `#sovereign-ecosystem-topbar a, #sovereign-ecosystem-topbar span { margin: 0; padding: 0; }` to `_ecosystem_bar.html` or a `<style>` block in `base.html`. Verify spacing matches other repos visually. — **Done 2026-07-14** (local agent, inline `<style>` in `_ecosystem_bar.html`)

## Layer 1 — PKCE / Auth — Public PKCE Alignment

> Canonical spec: `omni_social/docs/OMNI_SOCIAL_AUTH_STANDARDIZATION.md`
> Reference module: `omni_social/templates/utils/auth_pkce.py`

Current state: `PkceAuthMixin` with `oidc_states` dict, 300s prune cycle. Custom `get_username` override pins to `sub`. Uses `os.environ.get("ADMIN_DID")`. Needs alignment to canonical pattern.

- [ ] **Scope alignment:** Verify `OIDC_RP_SCOPES = "openid profile email"` in settings.py. Not `"openid"` alone — matches IDP default scope set.
- [ ] **Rule 1 — Proxy Header:** Add `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` to `settings.py`
- [ ] **Rule 2 — Public Client:** Verify backend inherits `auth.Backend`, not `OIDCAuthenticationBackend`. Remove any `OIDC_RP_CLIENT_SECRET` references.
- [ ] **Rule 3 — Instance State Relay:** Verify callback view overrides `get_backend_kwargs()`, not `get()`. Verifier must flow through kwargs to backend.
- [x] **Rule 4 — Sovereign Profile Anchoring:** `get_username()` pinned to `sub` claim. — Verified
- [ ] **Privilege evaluation:** Verify `settings.ADMIN_DID` (not `os.environ.get`). Uses `save(update_fields=[...])`.
- [ ] **Dirty-flag pattern:** Verify `user.save()` only executes when staff/superuser state actually changes.
- [ ] **Exception guard:** Verify `try/except requests.RequestException` on all back-channel HTTP calls.
- [ ] **Secret stripping:** Remove `OIDC_RP_CLIENT_SECRET` from container manifests (Helm values.yaml, Docker Compose .env).

## Layer 2 — App-Specific

- [ ] **(Potential)** Bootstrap → Tailwind migration: iyou_name is the only repo using Bootstrap (`core/base.html` line 21-23). Dual-framework hybrid with `preflight: false`. Page templates deeply use Bootstrap classes (`container`, `d-flex`, `card`, `list-group`, `form-control`, `navbar`, `data-bs-toggle`, Bootstrap Icons). *Not committed — pending decision.*
- [ ] **Ecosystem Doc Organization:** Standardize repo layout to match iyou_wun precedent — root: `AGENT.md`, `README.md`; `docs/`: `DEVELOPER_GUIDE.md`, `DESIGN_DOC.md`, `TODO.md`, `ecosystem_shared/`, `archive/`.

---
