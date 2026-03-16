/* ==========================================================================
   Object Table page logic — sortable, filterable, paginated data table
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_OBJ_TABLE;

    /* -----------------------------------------------------------------------
       State
    ----------------------------------------------------------------------- */
    var allRows      = [];       // rows returned from API (already filtered)
    var filteredRows = [];       // after column filters applied
    var columns      = [];       // ordered column list (no RUN_ID)
    var hiddenCols   = {};       // col -> true when hidden
    var sortCol      = null;     // currently sorted column (null = unsorted)
    var sortDir      = 1;        // 1 = asc, -1 = desc
    var colFilters   = {};       // col -> filter string
    var columnMeta   = {};       // col -> {sortable, filterable, removable, default, type}
    var currentPage  = 1;
    var perPage      = 50;       // 0 = show all

    /* -----------------------------------------------------------------------
       DOM refs
    ----------------------------------------------------------------------- */
    var lastUpdatedEl  = document.getElementById('ot-last-updated');
    var rowSummaryEl   = document.getElementById('ot-row-summary');

    var btnColumns     = document.getElementById('ot-btn-columns');
    var btnClearFilter = document.getElementById('ot-btn-clear-filters');
    var perpageSelect  = document.getElementById('ot-perpage');

    var colPanel       = document.getElementById('ot-col-panel');
    var colToggles     = document.getElementById('ot-col-toggles');
    var colClose       = document.getElementById('ot-col-close');
    var colAll         = document.getElementById('ot-col-all');
    var colNone        = document.getElementById('ot-col-none');

    var scrollTopEl    = document.getElementById('ot-scroll-top');
    var scrollSizer    = document.getElementById('ot-scroll-sizer');
    var tableWrap      = document.getElementById('ot-table-wrap');
    var tableEl        = document.getElementById('ot-table');
    var headerRow      = document.getElementById('ot-header-row');
    var filterRow      = document.getElementById('ot-filter-row');
    var tbody          = document.getElementById('ot-tbody');

    var pageInfo       = document.getElementById('ot-page-info');
    var pageInput      = document.getElementById('ot-page-input');
    var pageTotal      = document.getElementById('ot-page-total');
    var btnFirst       = document.getElementById('ot-btn-first');
    var btnPrev        = document.getElementById('ot-btn-prev');
    var btnNext        = document.getElementById('ot-btn-next');
    var btnLast        = document.getElementById('ot-btn-last');

    /* -----------------------------------------------------------------------
       Helpers
    ----------------------------------------------------------------------- */
    function escHtml(str) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(str)));
        return d.innerHTML;
    }

    function formatDate(iso) {
        if (!iso) return '—';
        try {
            return new Date(iso).toLocaleString();
        } catch (e) {
            return iso;
        }
    }

    function normalizeColumnMeta(rawMeta) {
        var out = {};
        if (!rawMeta || typeof rawMeta !== 'object') {
            return out;
        }
        Object.keys(rawMeta).forEach(function (key) {
            var meta = rawMeta[key] || {};
            out[key] = {
                sortable: meta.sortable !== false,
                filterable: meta.filterable !== false,
                removable: meta.removable !== false,
                default: meta.default !== false,
                type: meta.type ? String(meta.type).toLowerCase() : 'string',
            };
        });
        return out;
    }

    function getColumnMeta(col) {
        return columnMeta[col] || {};
    }

    function isColumnSortable(col) {
        var meta = getColumnMeta(col);
        return meta.sortable !== false;
    }

    function isColumnFilterable(col) {
        var meta = getColumnMeta(col);
        return meta.filterable !== false;
    }

    function isColumnRemovable(col) {
        // Keep the object identifier always visible.
        if (col === 'OBJNAME') return false;
        var meta = getColumnMeta(col);
        return meta.removable !== false;
    }

    function isColumnDefaultVisible(col) {
        var meta = getColumnMeta(col);
        return meta.default !== false;
    }

    function parseStrictNumber(value) {
        var raw = String(value === null || value === undefined ? '' : value).trim();
        if (!raw || !/^-?\d+(\.\d+)?$/.test(raw)) {
            return null;
        }
        var num = Number(raw);
        return isNaN(num) ? null : num;
    }

    function parseNightDate(value) {
        var raw = String(value === null || value === undefined ? '' : value).trim();
        if (!raw) return null;
        if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
            return Date.parse(raw + 'T00:00:00Z');
        }
        if (/^\d{8}$/.test(raw)) {
            var y = raw.slice(0, 4);
            var m = raw.slice(4, 6);
            var d = raw.slice(6, 8);
            return Date.parse(y + '-' + m + '-' + d + 'T00:00:00Z');
        }
        var parsed = Date.parse(raw);
        return isNaN(parsed) ? null : parsed;
    }

    function normalizeForSort(col, value) {
        var meta = getColumnMeta(col);
        var type = String(meta.type || '').toLowerCase();

        if (type === 'date' || type === 'datetime' || type === 'night') {
            var ts = parseNightDate(value);
            if (ts !== null) {
                return { kind: 'number', value: ts };
            }
        }

        if (type === 'number' || type === 'int' || type === 'float') {
            var forcedNum = parseStrictNumber(value);
            if (forcedNum !== null) {
                return { kind: 'number', value: forcedNum };
            }
        }

        var autoNum = parseStrictNumber(value);
        if (autoNum !== null) {
            return { kind: 'number', value: autoNum };
        }

        return {
            kind: 'string',
            value: String(value === null || value === undefined ? '' : value).toLowerCase(),
        };
    }

    /* -----------------------------------------------------------------------
       Load data from API
    ----------------------------------------------------------------------- */
    function loadData() {
        tbody.innerHTML = '<tr><td class="ot-loading" colspan="20">'
            + '<i class="fa-solid fa-spinner fa-spin"></i> Loading data&hellip;'
            + '</td></tr>';

        fetch(cfg.apiUrl + '?profile_id=' + encodeURIComponent(cfg.profileId))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    tbody.innerHTML = '<tr><td class="ot-error" colspan="20">'
                        + escHtml(data.error || 'Failed to load data') + '</td></tr>';
                    return;
                }

                allRows  = data.rows    || [];
                columns  = data.columns || [];
                columnMeta = normalizeColumnMeta(data.column_meta || {});

                // Initialize per-column visibility from metadata defaults.
                hiddenCols = {};
                columns.forEach(function (col) {
                    hiddenCols[col] = !isColumnDefaultVisible(col);
                    if (!isColumnRemovable(col)) {
                        hiddenCols[col] = false;
                    }
                });

                // Metadata
                if (data.generated_at) {
                    lastUpdatedEl.innerHTML =
                        '<i class="fa-solid fa-clock"></i> Last updated: '
                        + escHtml(formatDate(data.generated_at));
                } else {
                    lastUpdatedEl.innerHTML =
                        '<i class="fa-solid fa-circle-exclamation"></i> No data generated yet';
                }

                // Show "no data" message when the JSON exists but is empty
                if (data.message && allRows.length === 0) {
                    tbody.innerHTML = '<tr><td class="ot-empty" colspan="20">'
                        + escHtml(data.message) + '</td></tr>';
                    return;
                }

                buildHeaders();
                applyFilterSort();
            })
            .catch(function (err) {
                tbody.innerHTML = '<tr><td class="ot-error" colspan="20">'
                    + 'Network error: ' + escHtml(String(err)) + '</td></tr>';
            });
    }

    /* -----------------------------------------------------------------------
       Build header cells and column-toggle panel
    ----------------------------------------------------------------------- */
    function buildHeaders() {
        // Populate column toggle panel
        colToggles.innerHTML = '';
        columns.forEach(function (col) {
            if (!isColumnRemovable(col)) {
                hiddenCols[col] = false;
            }

            var label = document.createElement('label');
            label.className = 'ot-col-toggle';

            var cb = document.createElement('input');
            cb.type    = 'checkbox';
            cb.checked = !hiddenCols[col];
            cb.dataset.col = col;
            if (!isColumnRemovable(col)) {
                cb.disabled = true;
                hiddenCols[col] = false;
            }
            cb.addEventListener('change', function () {
                if (!isColumnRemovable(col)) {
                    this.checked = true;
                    hiddenCols[col] = false;
                    return;
                }
                hiddenCols[col] = !this.checked;
                renderHeaders();
                renderPage();
            });

            label.appendChild(cb);
            label.appendChild(document.createTextNode(' ' + col));
            colToggles.appendChild(label);
        });

        renderHeaders();
    }

    function renderHeaders() {
        headerRow.innerHTML = '';
        filterRow.innerHTML = '';

        var visible = columns.filter(function (c) { return !hiddenCols[c]; });

        visible.forEach(function (col) {
            /* --- sort header --- */
            var th = document.createElement('th');
            th.className  = 'ot-th';
            th.dataset.col = col;

            var sortable = isColumnSortable(col);
            if (!sortable) {
                th.classList.add('ot-th--nonsortable');
            }

            var lbl = document.createElement('span');
            lbl.className   = 'ot-th__label';
            lbl.textContent = col;

            var icn = document.createElement('span');
            icn.className = 'ot-th__sort-icon';
            if (!sortable) {
                icn.innerHTML = '<i class="fa-solid fa-minus ot-sort-idle"></i>';
            } else if (col === sortCol) {
                icn.innerHTML = sortDir === 1
                    ? '<i class="fa-solid fa-sort-up"></i>'
                    : '<i class="fa-solid fa-sort-down"></i>';
                th.classList.add(sortDir === 1 ? 'ot-th--asc' : 'ot-th--desc');
            } else {
                icn.innerHTML = '<i class="fa-solid fa-sort ot-sort-idle"></i>';
            }

            th.appendChild(lbl);
            th.appendChild(icn);
            th.addEventListener('click', function () {
                if (!isColumnSortable(col)) {
                    return;
                }
                if (sortCol === col) {
                    sortDir = -sortDir;
                } else {
                    sortCol = col;
                    sortDir = 1;
                }
                currentPage = 1;
                renderHeaders();
                applyFilterSort();
            });
            headerRow.appendChild(th);

            /* --- filter input --- */
            var ftd = document.createElement('th');
            ftd.className = 'ot-filter-cell';
            if (isColumnFilterable(col)) {
                var inp = document.createElement('input');
                inp.type        = 'text';
                inp.className   = 'ot-filter-input';
                inp.placeholder = '\u2315';
                inp.value       = colFilters[col] || '';
                inp.dataset.col = col;
                inp.title       = 'Filter ' + col;
                inp.addEventListener('input', function () {
                    colFilters[col] = this.value;
                    currentPage = 1;
                    applyFilterSort();
                });
                ftd.appendChild(inp);
            }
            filterRow.appendChild(ftd);
        });

        syncScrollMirror();
    }

    /* -----------------------------------------------------------------------
       Filter + sort
    ----------------------------------------------------------------------- */
    function applyFilterSort() {
        filteredRows = allRows.filter(function (row) {
            for (var col in colFilters) {
                if (!isColumnFilterable(col)) {
                    continue;
                }
                var fv = colFilters[col];
                if (!fv) continue;
                var cell = (row[col] === null || row[col] === undefined)
                    ? '' : String(row[col]);
                if (cell.toLowerCase().indexOf(fv.toLowerCase()) === -1) {
                    return false;
                }
            }
            return true;
        });

        if (sortCol && isColumnSortable(sortCol)) {
            filteredRows.sort(function (a, b) {
                var av = (a[sortCol] === null || a[sortCol] === undefined)
                    ? '' : a[sortCol];
                var bv = (b[sortCol] === null || b[sortCol] === undefined)
                    ? '' : b[sortCol];

                var va = normalizeForSort(sortCol, av);
                var vb = normalizeForSort(sortCol, bv);

                if (va.kind === 'number' && vb.kind === 'number') {
                    return sortDir * (va.value - vb.value);
                }

                var sa = String(va.value);
                var sb = String(vb.value);
                if (sa < sb) return -sortDir;
                if (sa > sb) return  sortDir;
                return 0;
            });
        } else if (sortCol && !isColumnSortable(sortCol)) {
            sortCol = null;
            sortDir = 1;
        }

        updatePagination();
        renderPage();
    }

    /* -----------------------------------------------------------------------
       Render one page of rows
    ----------------------------------------------------------------------- */
    function renderPage() {
        var visible = columns.filter(function (c) { return !hiddenCols[c]; });
        var total   = filteredRows.length;

        var start = 0;
        var end   = total;
        if (perPage > 0) {
            start = (currentPage - 1) * perPage;
            end   = Math.min(start + perPage, total);
        }
        var pageRows = filteredRows.slice(start, end);

        tbody.innerHTML = '';

        if (pageRows.length === 0) {
            var tr = document.createElement('tr');
            var td = document.createElement('td');
            td.colSpan   = visible.length || 1;
            td.className = allRows.length === 0 ? 'ot-empty' : 'ot-empty';
            td.textContent = allRows.length === 0
                ? 'No data available for this profile.'
                : 'No rows match the current filters.';
            tr.appendChild(td);
            tbody.appendChild(tr);
            syncScrollMirror();
            return;
        }

        var frag = document.createDocumentFragment();
        pageRows.forEach(function (row) {
            var tr = document.createElement('tr');
            tr.className = 'ot-row';

            visible.forEach(function (col) {
                var td = document.createElement('td');
                td.className = 'ot-cell';

                var val = row[col];
                if (val === null || val === undefined || val === '') {
                    td.innerHTML = '<span class="ot-null">\u2014</span>';
                } else if (col === 'OBJNAME') {
                    var a = document.createElement('a');
                    a.href      = '/data_portal/'
                        + encodeURIComponent(cfg.profileId)
                        + '/' + encodeURIComponent(String(val));
                    a.className = 'ot-obj-link';
                    a.textContent = String(val);
                    a.title = 'Open object page';
                    td.appendChild(a);
                } else {
                    td.textContent = String(val);
                }
                tr.appendChild(td);
            });

            frag.appendChild(tr);
        });
        tbody.appendChild(frag);

        syncScrollMirror();
    }

    /* -----------------------------------------------------------------------
       Pagination
    ----------------------------------------------------------------------- */
    function updatePagination() {
        var total      = filteredRows.length;
        var totalPages = (perPage > 0)
            ? Math.max(1, Math.ceil(total / perPage))
            : 1;

        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1)         currentPage = 1;

        var start = (perPage > 0) ? (currentPage - 1) * perPage + 1 : 1;
        var end   = (perPage > 0) ? Math.min(currentPage * perPage, total) : total;
        if (total === 0) { start = 0; end = 0; }

        var allTotal = allRows.length;
        var suffix   = (total < allTotal)
            ? ' (filtered from ' + allTotal + ')'
            : '';
        pageInfo.textContent = 'Showing '
            + (total === 0 ? 0 : start) + '\u2013' + end
            + ' of ' + total + ' rows' + suffix;

        rowSummaryEl.textContent = total + ' of ' + allTotal + ' objects';

        pageInput.value = currentPage;
        pageInput.max   = totalPages;
        pageTotal.textContent = totalPages;

        btnFirst.disabled = (currentPage <= 1);
        btnPrev.disabled  = (currentPage <= 1);
        btnNext.disabled  = (currentPage >= totalPages);
        btnLast.disabled  = (currentPage >= totalPages);
    }

    /* -----------------------------------------------------------------------
       Dual scroll mirror
    ----------------------------------------------------------------------- */
    function syncScrollMirror() {
        scrollSizer.style.width = tableEl.scrollWidth + 'px';
    }

    var _scrollSync = false;
    scrollTopEl.addEventListener('scroll', function () {
        if (_scrollSync) return;
        _scrollSync = true;
        tableWrap.scrollLeft = scrollTopEl.scrollLeft;
        _scrollSync = false;
    });
    tableWrap.addEventListener('scroll', function () {
        if (_scrollSync) return;
        _scrollSync = true;
        scrollTopEl.scrollLeft = tableWrap.scrollLeft;
        _scrollSync = false;
        syncScrollMirror();
    });

    /* -----------------------------------------------------------------------
       Pagination event listeners
    ----------------------------------------------------------------------- */
    btnFirst.addEventListener('click', function () {
        currentPage = 1;
        updatePagination();
        renderPage();
    });
    btnPrev.addEventListener('click', function () {
        currentPage = Math.max(1, currentPage - 1);
        updatePagination();
        renderPage();
    });
    btnNext.addEventListener('click', function () {
        var total = filteredRows.length;
        var tp    = (perPage > 0) ? Math.ceil(total / perPage) : 1;
        currentPage = Math.min(tp, currentPage + 1);
        updatePagination();
        renderPage();
    });
    btnLast.addEventListener('click', function () {
        var total = filteredRows.length;
        currentPage = (perPage > 0) ? Math.max(1, Math.ceil(total / perPage)) : 1;
        updatePagination();
        renderPage();
    });
    pageInput.addEventListener('change', function () {
        var v = parseInt(this.value, 10);
        if (!isNaN(v)) {
            currentPage = v;
            updatePagination();
            renderPage();
        }
    });
    perpageSelect.addEventListener('change', function () {
        perPage     = parseInt(this.value, 10) || 0;
        currentPage = 1;
        updatePagination();
        renderPage();
    });

    /* -----------------------------------------------------------------------
       Column toggle panel
    ----------------------------------------------------------------------- */
    btnColumns.addEventListener('click', function (e) {
        e.stopPropagation();
        colPanel.style.display = (colPanel.style.display === 'none')
            ? 'block' : 'none';
    });
    colClose.addEventListener('click', function () {
        colPanel.style.display = 'none';
    });
    document.addEventListener('click', function (e) {
        if (!colPanel.contains(e.target) && e.target !== btnColumns) {
            colPanel.style.display = 'none';
        }
    });
    colAll.addEventListener('click', function () {
        hiddenCols = {};
        columns.forEach(function (col) {
            hiddenCols[col] = false;
        });
        colToggles.querySelectorAll('input[type=checkbox]').forEach(function (cb) {
            cb.checked = true;
        });
        renderHeaders();
        renderPage();
    });
    colNone.addEventListener('click', function () {
        columns.forEach(function (col) {
            hiddenCols[col] = isColumnRemovable(col);
        });
        colToggles.querySelectorAll('input[type=checkbox]').forEach(function (cb) {
            cb.checked = !hiddenCols[cb.dataset.col];
        });
        renderHeaders();
        renderPage();
    });

    /* -----------------------------------------------------------------------
       Clear filters
    ----------------------------------------------------------------------- */
    btnClearFilter.addEventListener('click', function () {
        colFilters = {};
        filterRow.querySelectorAll('input.ot-filter-input').forEach(
            function (inp) { inp.value = ''; }
        );
        currentPage = 1;
        applyFilterSort();
    });

    /* -----------------------------------------------------------------------
       Window resize: re-sync scroll mirror width
    ----------------------------------------------------------------------- */
    window.addEventListener('resize', syncScrollMirror);

    /* -----------------------------------------------------------------------
       Init
    ----------------------------------------------------------------------- */
    loadData();

}());
