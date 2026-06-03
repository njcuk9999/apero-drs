---
description: "Apply to every UI change in ARI. Covers dark/light theme requirements, mobile-responsive rules, the permission system, instrument-specific config locations, and all architectural conventions learned from the codebase."
name: "ARI General Rules"
applyTo: "apero-ri/**"
---

# ARI General Rules

These rules apply to **every** change in `apero-ri/`. They complement the more
specific `ari-new-page.instructions.md` and `ari-tables.instructions.md`.

---

## 1. Theme support — dark, light, and standard (default)

The active theme is set via `data-theme="dark"` or `data-theme="light"` on `<html>`.
Absent means "standard" (the `:root` palette in `style.css`).

### Hard rules

- **Never hard-code colors** in templates, inline styles, or new CSS rules.
  Always use the CSS custom properties:

  | Variable | Meaning |
  |----------|---------|
  | `--ari-bg` | Page background |
  | `--ari-card-bg` | Card / panel background |
  | `--ari-surface-muted` | Slightly tinted surface (filter rows, toolbars) |
  | `--ari-surface-alt` | Alternate surface (hover rows, secondary panels) |
  | `--ari-text` | Primary text |
  | `--ari-text-muted` | Secondary / label text |
  | `--ari-border` | All borders |
  | `--ari-primary` | Brand blue (links, active tabs, primary buttons) |
  | `--ari-primary-dark` | Darker brand blue |
  | `--ari-primary-light` | Light tint of brand blue (table headers) |
  | `--ari-accent` | Orange accent |
  | `--ari-accent-dark` | Darker orange |
  | `--ari-success` | Green |
  | `--ari-warning` | Yellow/amber |
  | `--ari-danger` | Red |
  | `--ari-info` | Info blue |
  | `--ari-header-bg` | Top navigation background |
  | `--ari-header-text` | Top navigation text |

- If you need a color not covered above, **add a new variable** in `:root` AND
  add a `[data-theme="dark"]` override in the same commit.

- Any selector with a theme-sensitive value (background, border, text on a colored
  chip, hover state, modal chrome) **must** have a `[data-theme="dark"]` counterpart in
  the same CSS file or in `static/css/mobile_overrides.css`.

- Inline `style=""` attributes that hard-code colors break dark mode.  Move them to CSS
  classes instead, or use `color: var(--ari-text)` syntax.

### Reference dark-theme palette (for `[data-theme="dark"]` overrides)

```
background / panel:  #0d1117 / #161b22 / #1c2128 / #21262d
text:                #e6edf3 (primary)   #8b949e (muted)
border:              #30363d
primary:             #58a6ff
success bg/text:     #0d2818 / #3fb950
warning bg/text:     #2a1700 / #fdba74
danger  bg/text:     #2a0d09 / #f85149
info    bg/text:     #0c1929 / #79b8ff
```

### Status / state color conventions (chips, cards, badges)

| State | Light bg | Light text | Dark bg | Dark text |
|-------|----------|------------|---------|-----------|
| passed/ok | `color-mix(in srgb, #22c55e 16%, var(--ari-card-bg))` | `#166534` | `#0d2818` | `#3fb950` |
| failed/error | `color-mix(in srgb, #ef4444 16%, …)` | `#b91c1c` | `#2a0d09` | `#f85149` |
| monitored | `color-mix(in srgb, #f59e0b 16%, …)` | `#b45309` | `#2a1f05` | `#f2cc60` |
| overridden | `color-mix(in srgb, #7c3aed 16%, …)` | `#5b21b6` | `#1a1040` | `#c4b5fd` |
| info/blue | `#eff6ff` | `#1d4ed8` | `#0c1929` | `#79b8ff` |

---

## 2. Mobile / small-screen support

Every page must be usable on a phone (min width 360 px).

### Hard rules

- Use the **four standard breakpoints** — do not invent new ones:

  | Breakpoint | Usage |
  |------------|-------|
  | `@media (max-width: 1100px)` | Large tablets |
  | `@media (max-width: 980px)` | Small tablet; sidebar collapses to off-canvas |
  | `@media (max-width: 768px)` | Primary mobile (stacks, tables scroll/collapse) |
  | `@media (max-width: 600px)` | Small phones (extra stack, larger tap targets) |

- `mobile_overrides.css` already provides a global safety net (table scroll wrappers,
  modal height caps, form stacking, sidebar collapse).  Add page-specific rules in the
  page's own CSS file.

- Multi-column grids (`grid-template-columns: repeat(N, ...)`) **must** collapse to
  `1fr` at ≤ 768 px via a media query.

- Flex rows of buttons must have `flex-wrap: wrap` so they don't overflow on phones.

- Tables must be inside `<div class="ot-table-wrap">` (overflow-x: auto) or collapse
  to stacked cards at ≤ 768 px.

- Modal dialogs: `max-width: 96vw !important; max-height: 90vh; overflow-y: auto;`

- Tap targets ≥ 44×44 CSS px at ≤ 768 px.

- Long pre/code blocks: `overflow-x: auto; word-break: break-word;`

---

## 3. Permissions

### Where permissions live

| Thing | Location |
|-------|----------|
| Page view permissions | `apero_ri/resources/pages.yaml` (`view-permission` key) |
| Group memberships & grant tree | `apero_ri/resources/groups.yaml` |
| Runtime permission check (server) | `_require_*` helpers in `application.py` / `monitor_view_helpers.py` |

### Naming convention

```
view.<area>                    # Read-only access
edit.<area>.<sub>              # Non-admin edits
manage.<area>[.<sub>]          # Full admin control
login_as.<group>               # Impersonation
manage.group.<group>           # Group management
manage.instrument.<INSTRUMENT> # Instrument-scoped management
```

Instrument-scoped permissions append `.<INSTRUMENT>` (uppercase), e.g.
`manage.apero_profile.SPIROU`.  Groups inherit through the `groups:` key in
`groups.yaml` — never duplicate permissions across levels.

### Never gate in templates

Permission checks belong in the Python route / view helper, not in Jinja
`{% if … %}` blocks.  The template can adapt the UI (show/hide edit buttons), but
the underlying data endpoint must independently enforce the same permission.

---

## 4. Instrument-specific configuration

Instrument-specific parameters **belong in the aprofile yaml files**, not in Python:

```
apero_ri/resources/aprofile_instruments/
    spirou_v7.yaml
    spirou_v8.yaml
    nirps_ha_v7.yaml
    nirps_ha_v8.yaml
    nirps_he_v7.yaml
    nirps_he_v8.yaml
```

All v7 and v8 pairs for each instrument should be kept in sync (same new sections).
When adding a new parameter block (e.g. `apero-checks.my_new_check`), add it to all
six files.  SPIROU and NIRPS variants may have different default values but must have
the same keys present.

---

## 5. API helpers — use `ari_api/`

Internal ARI API calls (to the ARI server itself) must go through
`apero_ri/ari_api/` helper modules, not bare `requests.get/post`.  If an endpoint
is not yet wrapped, add a helper function in the appropriate `ari_api/*.py` file.

---

## 6. Async tasks

- Task modules live in `apero_ri/tasks/`.
- Tasks inherit from `apero_async.AperoAsyncTask` and implement `run_job(self, params)`.
- Register in `tasks/__init__.py` using `_register_task(KEY, module_name, ClassName, TYPE)`.
- `GLOBAL` tasks appear in the async-tasks admin for all profiles; `INSTRUMENT` tasks
  are per-instrument.
- Task config overrides (frequency, enabled, custom keys) live in
  `~/.ari/admin/async_tasks/async_tasks.yaml` — the catalog auto-merges from the
  registry on first load, so no manual YAML edit is needed for a new task.
- Use `TASK_LOGGER` from `params` for progress messages (shown in the task log UI).

---

## 7. PDF generation (fail reports)

PDF reports use **reportlab**.  Key patterns:

- `Paragraph(html_str, style)` — inline markup with `<b>`, `<br/>`, `<a href>`,
  `<font color>`.  Use `html.escape()` on user data before embedding.
- `Table([[cell, …], …], colWidths=[…*mm])` — cell can be a `Paragraph` or a string.
  A list of `Paragraph` objects in a cell is **not reliably rendered** — join them
  with `<br/>` into one `Paragraph` instead.
- `[data-theme="dark"]` does not apply to PDFs; use explicit `colors.HexColor` for any
  themed element, choosing a palette that reads well on white paper.
- Store generated PDFs under `~/.ari/reports/<token>/` using `fail_report.store_report_pdf()`.
- Share/download URLs must be **scheme-relative** (`//host/path`) so they work on both
  HTTP and HTTPS.  Strip the scheme with `re.sub(r"^https?:", "", request.url_root)`.

---

## 8. Error grouping (fail report analyser)

APERO log line format: `HH:MM:SS.sss-!!|RECIPE_NAME[pid]|actual message`

- Strip the prefix in two passes: (1) up to and including `-!!|`, then (2) up to the
  next `|` (the `RECIPE[pid]` label).
- Group error *blocks* (consecutive `-!!|` lines) not individual lines.
- Normalize blocks by replacing variable parts (paths, numbers, object names in
  `[brackets]`, quoted strings) with placeholders before building the signature.
- Display: substitute constant variables back into the template; number only the truly
  varying ones as `{{1}}`, `{{2}}`, etc.  Show all unique values with no truncation.

---

## 9. Miscellaneous conventions learned from the codebase

- **Token / share URLs**: use UUID4 (`str(uuid.uuid4())`), store in
  `~/.ari/secret/` with `chmod 0o600` via `secret_store.protect_path`.
- **Caching**: in-memory caches use a module-level dict + `threading.Lock`.  Disk caches
  sit in `~/.ari/` subdirectories.  Always invalidate both layers after a config save.
- **Download triggers**: use a hidden `<iframe src="url">` (synchronously, inside the
  click handler) to trigger `Content-Disposition: attachment` downloads without popup
  blockers and without navigating away from the page.
- **CSS class naming**: prefix with the page/component abbreviation
  (e.g. `ac-` for apero-checks, `aci-` for check-info, `mi-` for monitor-issues,
  `ms-` for monitor-schedule, `pl-` for processing-logs, `upm-` for user-messaging).
- **JS versioning**: static JS/CSS files are cache-busted via `?v=YYYYMMDDX` query
  strings.  Bump the version whenever the file content changes.
- **Flash banners** (`ari-flash--success/danger/warning/info`) require both light and
  dark variants — see `mobile_overrides.css` for the dark overrides.
- **Bokeh plots** must use `apply_bokeh_theme(fig, theme)` from `apero_ri/plots/bokeh_theme.py`.
  Re-fetch on `CustomEvent('ari:theme-change')`.
- **File paths**: never hard-code absolute paths.  Resolve relative to
  `local_data_dir = app._resolve_local_data_dir()` or `ARI_DIR = Path.home() / ".ari"`.
- **Google OAuth tokens** for GSheet sync: stored in `~/.ari/admin/legacy_gsheet_oauth.json`.
  Loaded and used by all `LEGACY_*_GSHEET` tasks.
- **Template JS config pattern**: inject server-side values into a `window.MY_PAGE = {…}`
  object inside a `<script>` block, then read from the global in your JS IIFE.
- **Jinja `tojson` filter**: always use `{{ value | tojson }}` when embedding Python
  values in JS — never string-interpolate them directly.
