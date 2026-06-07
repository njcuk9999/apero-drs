---
description: "Use when adding any data table, paginated list, sortable grid, or filterable result set in ARI. Covers the standard ot-* CSS class pattern, sticky headers, filter row, sort icons, odd/even striping, pagination, dark-theme overrides, and the JS wiring pattern."
name: "ARI Table Pattern"
applyTo: "apero-ri/**"
---

# ARI Table / Data-Grid Pattern

All paginated tables in ARI use the shared `ot-*` (object-table) CSS class system
defined in `static/css/style.css` (around line 7265).  **Do not invent a new table
style** — extend this one.

---

## 1. HTML structure

```html
<!-- Outer scroll wrapper — add to every table -->
<div class="ot-table-wrap">
    <table class="ot-table">
        <thead>
            <!-- Header row with sort icons -->
            <tr class="ot-header-row" id="my-header-row"></tr>
            <!-- Per-column filter row (inputs or dropdowns) -->
            <tr class="ot-filter-row"  id="my-filter-row"></tr>
        </thead>
        <tbody id="my-tbody">
            <!-- Loading placeholder -->
            <tr><td class="ot-loading" colspan="5">
                <i class="fa-solid fa-spinner fa-spin"></i>
                Loading data…
            </td></tr>
        </tbody>
    </table>
</div>

<!-- Pagination bar below the table -->
<div class="ot-pagination" id="my-pagination">
    <div id="my-page-info"   class="ot-page-info"></div>
    <div class="ot-page-controls">
        <button id="my-btn-first" class="ari-btn ari-btn--sm ari-btn--secondary"
                title="First page" disabled>
            <i class="fa-solid fa-angles-left"></i>
        </button>
        <button id="my-btn-prev"  class="ari-btn ari-btn--sm ari-btn--secondary"
                title="Previous page" disabled>
            <i class="fa-solid fa-angle-left"></i>
        </button>
        <span class="ot-page-num">
            Page&nbsp;<input id="my-page-input" class="ot-page-input"
                             type="number" min="1" value="1"
                             title="Jump to page">
            &nbsp;of&nbsp;<span id="my-page-total">1</span>
        </span>
        <button id="my-btn-next"  class="ari-btn ari-btn--sm ari-btn--secondary"
                title="Next page" disabled>
            <i class="fa-solid fa-angle-right"></i>
        </button>
        <button id="my-btn-last"  class="ari-btn ari-btn--sm ari-btn--secondary"
                title="Last page" disabled>
            <i class="fa-solid fa-angles-right"></i>
        </button>
    </div>
</div>
```

Toolbar (filter text + per-page selector) sits **above** the table wrap:

```html
<div class="ot-toolbar">
    <div class="ot-toolbar__left">
        <button class="ari-btn ari-btn--sm ari-btn--secondary" …>
            <i class="fa-solid fa-filter-circle-xmark"></i>
            Clear Filters
        </button>
    </div>
    <div class="ot-toolbar__right">
        <label class="ot-perpage-label">
            Rows per page
            <select id="my-perpage" class="ot-perpage-select">
                <option value="25">25</option>
                <option value="50" selected>50</option>
                <option value="100">100</option>
                <option value="250">250</option>
                <option value="0">All</option>
            </select>
        </label>
    </div>
</div>
```

---

## 2. CSS classes

| Class | Purpose |
|-------|---------|
| `ot-table-wrap` | Scroll wrapper: `overflow-x/y: auto`, `max-height: 62vh`, border + radius |
| `ot-table` | `width:100%; border-collapse:collapse; font-size:0.85rem` |
| `ot-header-row` | Sticky top:0 z-index:3 |
| `ot-filter-row` | Sticky top:37px z-index:2 (immediately below header) |
| `ot-th` | Header cell: `background:var(--ari-primary-light)`, bold, with sort icon |
| `ot-th--asc` / `ot-th--desc` | Active sort direction highlight |
| `ot-th--nonsortable` | Header cell that is not sortable (no hover highlight) |
| `ot-filter-cell` | Filter row `<th>`: `background:var(--ari-bg)` |
| `ot-filter-input` | Text filter input (width 100%) |
| `ot-filter-select` | Dropdown filter — **use when a column has < 10 unique values** |
| `ot-row` | Data `<tr>` — gains the odd/even stripe automatically |
| `ot-cell` | Data `<td>`: padding, right border, bottom border, `color:var(--ari-text)` |
| `ot-loading` | Loading / no-results placeholder cell |
| `ot-pagination` | Flex row wrapping page info + controls |
| `ot-page-info` | Muted text (e.g. "1 – 50 of 312") |
| `ot-page-controls` | Flex row of pagination buttons |
| `ot-page-input` | Page-jump number input |
| `ot-toolbar` | Flex row above the table (left: filter buttons, right: per-page) |
| `ot-perpage-label` / `ot-perpage-select` | Per-page dropdown |
| `ot-meta-bar` | Secondary info bar (row counts, last-updated, small action buttons) |

### Odd / even row striping

For the **data portal object table** the palette is warm yellow/orange:
- Odd rows: `background: #fffde7`
- Even rows: `background: #ffeed8`
- Hover: `background: rgba(255, 152, 0, 0.16)`

For tables outside the data portal (monitor portal, admin portal), prefer using CSS
variables so the table adapts to the current theme instead:
```css
.my-table .ot-row:nth-child(odd)  td { background: var(--ari-card-bg); }
.my-table .ot-row:nth-child(even) td { background: var(--ari-surface-muted, #f8fafc); }
.my-table .ot-row:hover           td { background: var(--ari-primary-light, #eef2ff); }
```

### Column separators

Header cells get `border-right: 1px solid var(--ari-border)`.
Data cells get `border-right: 1px solid var(--ari-border)` and
`border-bottom: 1px solid var(--ari-border)`.
The **last column** in a row uses `border-right: none`.

---

## 3. Dark-theme overrides (required for every table)

The `ot-*` classes in `style.css` already include dark overrides.  If you use these
classes you get dark mode for free.

If you add custom table CSS (e.g. for row stripe overrides), you **must** add:

```css
/* Light theme: custom stripe colors */
.my-table .ot-row:nth-child(odd)  td { background: #fffde7; }
.my-table .ot-row:nth-child(even) td { background: #ffeed8; }

/* Dark theme: override custom stripes */
[data-theme="dark"] .my-table .ot-row:nth-child(odd)  td { background: #161b22; }
[data-theme="dark"] .my-table .ot-row:nth-child(even) td { background: #1c2128; }
[data-theme="dark"] .my-table .ot-row:hover           td { background: #21262d; }
```

---

## 4. Filter column decision rule

| Unique values in column | Use |
|------------------------|-----|
| < 10 | `<select class="ot-filter-select">` with "All" option first, then sorted unique values |
| ≥ 10 | `<input class="ot-filter-input">` for free-text substring search |

---

## 5. Sort icon pattern (header cells)

```html
<th class="ot-th ot-th--sortable" data-col="recipe">
    <span class="ot-th__label">Recipe</span>
    <i class="fa-solid fa-sort ot-th__sort-icon ot-sort-idle"></i>
</th>
```

When sorted ascending, replace the icon with `fa-sort-up` and add `ot-th--asc`.
When sorted descending, use `fa-sort-down` and `ot-th--desc`.

---

## 6. Mobile rules

- The `ot-table-wrap` already provides `overflow-x: auto` so tables scroll horizontally
  on small screens.
- At ≤ 768 px, optionally collapse columns: use `display: none` on low-priority `<th>`
  and `<td>` pairs with a matching `@media (max-width: 768px)` rule.
- Never set a fixed `width:` on `ot-table-wrap`; use `max-width: 100%` or leave it to
  fill its parent.

---

## 7. JavaScript pattern (vanilla JS)

All existing tables use a self-contained IIFE pattern with a `state` object:

```javascript
(function () {
    "use strict";
    var state = {
        allRows: [],        // all rows from the API
        filteredRows: [],   // after filters applied
        columns: [],
        dropdownCols: [],   // columns using <select> filter
        sortCol: null,
        sortDir: "asc",
        page: 1,
        perPage: 50,
        filters: {},
    };

    function filterRows() { /* rebuild filteredRows, call renderPage */ }
    function renderPage() { /* slice filteredRows, build <tbody> innerHTML */ }
    function buildHeader() { /* create <th> with sort icons and filter cells */ }
    function loadData()  { /* fetch from API, populate state, call buildHeader + renderPage */ }
    function wireEvents() { /* attach click/change listeners */ }

    document.addEventListener("DOMContentLoaded", function () {
        wireEvents();
        loadData();
    });
}());
```

See `static/js/processing_logs.js` for the reference implementation.

---

## 8. Server-side pagination for large tables

**Rule: any table that may contain more than ~5 000 rows MUST use server-side
pagination.**  Client-side pagination of 100 K+ rows causes unacceptable JSON
transfer times, client memory exhaustion, and DOM rendering freezes.

### When to apply

- Processing-log recipe tables (can exceed 391 K rows).
- Any table backed by a DB query without a narrow WHERE clause.
- Any table whose JSON response may exceed ~5 MB.

### API design

Add optional parameters `paged`, `page`, `per_page`, `sort_col`, `sort_dir`,
and `filters` to the POST endpoint.  When `paged=true`:

1. Run a **COUNT** query with only the WHERE clause → return `total`.
2. Run the data query with `ORDER BY … LIMIT {per_page} OFFSET {(page-1)*per_page}`.
3. Return `{rows, columns, dropdown_columns, total, page, per_page, paged: true}`.

Use `LIMIT / OFFSET` in MySQL/MariaDB.  With a proper index on the sorted column
this is O(log N + per_page) — essentially free.

Keep the original full-fetch path (no `paged` param) for backward compat with
other callers or for tables that are never large.

### JavaScript pattern

```javascript
var state = {
    pagedMode: false,     // true after first paged response
    serverTotal: 0,       // total matching rows from server
    pageCache: {},        // key → rows (prefetch cache)
};

// Cache key must encode page + per_page + sort + filters.
function cacheKey(page) {
    return JSON.stringify({ p: page, pp: state.perPage,
                            sc: state.sortCol, sd: state.sortDir,
                            f: state.filters });
}

function loadPagedData(page, skipCache) {
    var key = cacheKey(page);
    if (!skipCache && state.pageCache[key]) {
        applyData(state.pageCache[key], page);
        prefetchPage(page + 1);
        return;
    }
    fetchFromServer(page).then(function (data) {
        state.pageCache[key] = data;
        applyData(data, page);
        prefetchPage(page + 1);   // look-ahead of 1 page
    });
}

function prefetchPage(page) {
    var key = cacheKey(page);
    if (state.pageCache[key]) return;
    var go = function () {
        fetchFromServer(page).then(function (d) {
            state.pageCache[key] = d;
        }).catch(function () {});
    };
    if (typeof requestIdleCallback === "function") {
        requestIdleCallback(go, { timeout: 2000 });
    } else {
        setTimeout(go, 300);
    }
}

// Invalidate the page cache whenever filter or sort changes.
function resetAndFetch() {
    state.pageCache = {};
    state.page = 1;
    loadPagedData(1, true);
}
```

**Rules:**
- Filter-input changes must debounce (300 ms) then call `resetAndFetch()`.
- Sort-header clicks must call `resetAndFetch()` with the new sort.
- The per-page selector change must call `resetAndFetch()`.
- The Refresh button must call `loadPagedData(state.page, true)` (skip cache, keep page).
- Always pre-fetch the **next** page after rendering the current one.
- Cache entries are tied to the current filter+sort state; invalidate on any change.
- Do NOT pre-fetch more than 1 page ahead — it wastes DB queries for pages the
  user may never visit.
- The per-page `"All"` option (`value="0"`) is disabled in paged mode — always
  enforce a finite `per_page` (max 500 recommended).
