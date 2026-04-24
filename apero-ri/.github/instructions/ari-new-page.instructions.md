---
description: "Use when adding or editing any ARI page, template, stylesheet, or front-end JS. Enforces page registration, permissions, sidebar wiring, all three themes (dark/light/standard) and mobile responsiveness for every new feature."
name: "ARI New Page / New Content Rules"
applyTo: "apero-ri/**"
---

# ARI New Page / New Content Rules

When adding a new page, template, stylesheet, JS module, or any
user-visible UI in `apero-ri/`, the change is **not complete** until
every item in this checklist holds. Treat this as the definition of
done — an MR that adds a page without these is broken.

## 1. Page registration & navigation

- Add the page to `apero-ri/apero_ri/resources/pages.yaml` with all
  six required keys: `label`, `parent`, `view-permission`, `icon`
  (FontAwesome class), `quick-nav`, and the `side-nav` block
  (`pinned`, `top-level`, `show`).
- Use a hierarchical id (e.g. `home.user_portal.users`,
  `home.monitor_portal.issues`).
- If the page has children that should appear in the side-nav,
  set `top-level: True` on the section root and add children with the
  matching `parent:` value. Sub-pages must NOT set `top-level: True`.
- Never hard-code a sidebar in a template. The shared sidebar
  partial reads `pages.yaml` automatically — adding a page there is
  what makes it appear.
- The route in `apero-ri/apero_ri/application/routes.py` and the
  view function in `application.py` must use the SAME page id used
  in `pages.yaml`.

## 2. Permissions

- Add the new `view-permission` value (and any `edit.*` /
  `manage.*` values referenced) to
  `apero-ri/apero_ri/resources/groups.yaml` under every group that
  should receive it. Inherit through nested groups; do not duplicate.
- Use the existing naming scheme:
  `view.<area>`, `edit.<area>.<sub>`, `manage.<area>.<sub>`,
  `login_as.<group>`, optionally instrument-scoped via
  `.<INSTRUMENT>` suffix (e.g. `manage.group.monitor.SPIROU`).
- Server route handlers MUST gate with the same permission via the
  existing `_require_*` helpers (e.g. `_require_user`,
  `_require_admin_perm`, `_require_async_tasks_perm`).
- Never expose data through an API endpoint without the matching
  permission check, even if the page itself is gated.

## 3. Themes — dark, light, standard (the default)

Every new visual element must render correctly under all three
themes. The active theme is set on `<html>` via
`data-theme="dark"`, `data-theme="light"`, or absent (= standard,
which is the `:root` palette in `static/css/style.css`).

**Hard rules:**

- NEVER hard-code colors in templates, inline styles, or new CSS
  rules. Use the CSS custom properties in `:root`:
  `--ari-bg`, `--ari-card-bg`, `--ari-text`, `--ari-text-muted`,
  `--ari-border`, `--ari-primary`, `--ari-primary-dark`,
  `--ari-primary-light`, `--ari-accent`, `--ari-accent-dark`,
  `--ari-success`, `--ari-warning`, `--ari-danger`, `--ari-info`,
  `--ari-header-bg`, `--ari-header-text`, `--ari-header-link`.
- If a new component needs a color that is NOT covered by an
  existing variable, add a new variable in `:root` AND override it
  for `[data-theme="dark"]` and `[data-theme="light"]` in the same
  commit.
- Any selector you write that is theme-sensitive (backgrounds,
  borders, text on colored chips, hover states, pills, badges,
  tab chrome, modal chrome) MUST have matching
  `[data-theme="dark"] <selector> { ... }` rules in
  `static/css/style.css` (or the page's dedicated CSS file).
- Test by toggling the theme in the UI before declaring the
  feature done. Astrometrics and Monitor Portal Issues are the
  reference cases for "what NOT to ship" — fix-by-example.

### Bokeh graphs

This codebase uses Bokeh (not Plotly) for object-page plots. Every
Bokeh figure must respond to the active theme.

**Server-side (Python) — required pattern:**

```python
from apero_ri.plots.bokeh_theme import apply_bokeh_theme

theme = params.get("theme", "default")  # 'default' | 'light' | 'dark'
fig = figure(...)
apply_bokeh_theme(fig, theme)
```

`apply_bokeh_theme()` (in `apero_ri/plots/bokeh_theme.py`) sets
`background_fill_color`, `border_fill_color`, axis label / tick
text colors, grid colors, title colors, and legend text colors
based on the requested theme.

**Client-side (JS) — required pattern:**

- Pass the active theme in the API request:
  `?theme=' + (document.documentElement.getAttribute('data-theme') || 'default')`
- Re-fetch the plot when the user toggles theme. The theme
  toggle dispatches `CustomEvent('ari:theme-change',
  { detail: { theme } })` on `document` — listen for it on each
  page that owns Bokeh embeds and re-request the plot data, or
  call the page-local `refreshPlots(theme)` helper.

**Hard rules:**

- Never hard-code `background_fill_color="white"` in a
  `figure(...)` call. Always go through `apply_bokeh_theme`.
- Tooltips/HoverTool stylesheets must read from CSS vars; do
  not embed inline colors.
- Server endpoints that return Bokeh JSON must accept a `theme`
  query/body parameter and forward it to `apply_bokeh_theme`.

## 4. Mobile / small-screen support

The site MUST be usable on phones and tablets. Add responsive
styles for every page; do not assume desktop width.

**Hard rules:**

- Every base template that renders `<head>` must include
  `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Use `box-sizing: border-box` (already global) and avoid fixed
  pixel widths on containers. Prefer `max-width`, `width: 100%`,
  flex-basis, `min()/max()/clamp()`.
- Standard breakpoints used in this repo (use ONE of these — do
  not invent new ones unless absolutely necessary):
  - `@media (max-width: 1100px)` — large tablets
  - `@media (max-width: 980px)`  — small tablet / sidebar collapse
  - `@media (max-width: 768px)`  — primary mobile breakpoint
  - `@media (max-width: 600px)`  — small phones
- At ≤ 980px the sidebar must collapse to a drawer/off-canvas
  pattern (already implemented for core pages — copy that pattern;
  do not reimplement).
- At ≤ 768px any wide table must either:
  (a) collapse to stacked cards (`display:block` on rows + cells
  with data-label pseudo-elements), or
  (b) become horizontally scrollable inside a wrapper with
  `overflow-x: auto; -webkit-overflow-scrolling: touch;`.
- Tap targets (buttons, nav links, icons) must be ≥ 44×44 CSS
  pixels at the mobile breakpoint.
- Forms must stack vertically at ≤ 768px (no side-by-side label/
  input grids).
- Test at 360px, 414px, 768px, and 1100px widths before declaring
  the feature done. Modal dialogs must fit within the viewport
  with `max-height: 90vh; overflow-y: auto;`.

## 5. Sidebar pattern

Re-use the existing sidebar partial. Concretely:

- Inherit from the same base template the sibling pages use
  (`base.html` / portal-specific base).
- Pass the page id to the sidebar context via the existing
  `ariapp_build_sidebar_context` helper — never construct a
  sidebar fragment by hand.
- If your page is part of a portal section (e.g. `user_portal`,
  `monitor_portal`), set `parent:` to that portal in `pages.yaml`
  so the sidebar tree picks it up automatically.

## 6. Pre-merge checklist (run for every UI change)

Before declaring the change done:

1. Page appears under expected parent in `pages.yaml`; sidebar
   shows it for the right groups (toggle a test user in each
   relevant group).
2. Permission denied returns a 403 (or redirect) for users
   without the `view-permission`.
3. Toggle the theme to dark, light, standard — every panel,
   chip, table, modal, and graph remains legible.
4. Resize the window to 360 / 414 / 768 / 1100 px — content
   reflows, no horizontal scroll on the body, sidebar collapses,
   tables/forms remain usable.
5. `node --check` passes on any new JS file.
6. `python -m py_compile` passes on any new Python file.
7. `Jinja2` parse passes on any new template.
8. The new page is reachable from at least one card or sidebar
   entry — orphan pages are not allowed.
