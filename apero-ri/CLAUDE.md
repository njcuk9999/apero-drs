# ARI (APERO Reduction Interface) — Claude Code Guide

This file gives Claude Code essential context about the `apero-ri` repository so every
code-generation session starts with the right mental model.

---

## Quick orientation

| Area | Path |
|------|------|
| Flask application | `apero_ri/application/` |
| Templates (Jinja2) | `apero_ri/templates/` |
| Static assets | `apero_ri/static/` (CSS in `css/`, JS in `js/`) |
| Core Python helpers | `apero_ri/core/` |
| Async task modules | `apero_ri/tasks/` |
| ARI API client helpers | `apero_ri/ari_api/` |
| Resource config (YAML) | `apero_ri/resources/` |
| Instruction files | `.github/instructions/` |

---

## Instruction files (read these before any UI change)

| File | When to apply |
|------|---------------|
| [ari-new-page.instructions.md](.github/instructions/ari-new-page.instructions.md) | Any new page, template, stylesheet, or JS module |
| [ari-tables.instructions.md](.github/instructions/ari-tables.instructions.md) | Any data table, paginated list, or sortable grid |
| [ari-general.instructions.md](.github/instructions/ari-general.instructions.md) | Every UI change — themes, mobile, permissions, configs |

Claude Code automatically applies any instruction file whose `applyTo` glob matches the
file being edited, but **read all three** when adding a new page or feature.

---

## Key conventions (summary — details in the instruction files)

1. **Permissions** live in `apero_ri/resources/groups.yaml`; page registration in
   `apero_ri/resources/pages.yaml`.  Never gate access in templates; always use the
   `_require_*` helpers in the route/view.

2. **Instrument-specific parameters** belong in the `aprofile_instruments/*.yaml`
   files under `apero_ri/resources/aprofile_instruments/`, not hard-coded in Python.

3. **Never hard-code colors.** Use `--ari-*` CSS custom properties.  Every new color
   needs a `[data-theme="dark"]` override.

4. **Mobile first.** Use the four standard breakpoints (1100 / 980 / 768 / 600 px).
   Tables must either collapse or scroll at ≤ 768 px.

5. **Tables** follow the `ot-*` CSS class pattern.  See `ari-tables.instructions.md`.

6. **ARI API calls** go through `apero_ri/ari_api/` helpers, not raw `requests`.
