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
            var label = document.createElement('label');
            label.className = 'ot-col-toggle';

            var cb = document.createElement('input');
            cb.type    = 'checkbox';
            cb.checked = (col === 'OBJNAME') ? true : !hiddenCols[col];
            cb.dataset.col = col;
            if (col === 'OBJNAME') {
                cb.disabled = true;
                hiddenCols[col] = false;
            }
            cb.addEventListener('change', function () {
                if (col === 'OBJNAME') {
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

            var lbl = document.createElement('span');
            lbl.className   = 'ot-th__label';
            lbl.textContent = col;

            var icn = document.createElement('span');
            icn.className = 'ot-th__sort-icon';
            if (col === sortCol) {
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

            var inp = document.createElement('input');
            inp.type        = 'text';
            inp.className   = 'ot-filter-input';
            inp.placeholder = '\u2315';    // search icon character
            inp.value       = colFilters[col] || '';
            inp.dataset.col = col;
            inp.title       = 'Filter ' + col;
            inp.addEventListener('input', function () {
                colFilters[col] = this.value;
                currentPage = 1;
                applyFilterSort();
            });

            ftd.appendChild(inp);
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

        if (sortCol) {
            filteredRows.sort(function (a, b) {
                var av = (a[sortCol] === null || a[sortCol] === undefined)
                    ? '' : a[sortCol];
                var bv = (b[sortCol] === null || b[sortCol] === undefined)
                    ? '' : b[sortCol];
                var na = parseFloat(av);
                var nb = parseFloat(bv);
                if (!isNaN(na) && !isNaN(nb)) {
                    return sortDir * (na - nb);
                }
                var sa = String(av).toLowerCase();
                var sb = String(bv).toLowerCase();
                if (sa < sb) return -sortDir;
                if (sa > sb) return  sortDir;
                return 0;
            });
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
                    // Placeholder hyperlink — will become a real route later
                    var a = document.createElement('a');
                    a.href      = '#';
                    a.className = 'ot-obj-link';
                    a.textContent = String(val);
                    a.title = 'Object detail (coming soon)';
                    a.addEventListener('click', function (e) {
                        e.preventDefault();
                    });
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
        colToggles.querySelectorAll('input[type=checkbox]').forEach(
            function (cb) { cb.checked = true; }
        );
        renderHeaders();
        renderPage();
    });
    colNone.addEventListener('click', function () {
        // Always keep OBJNAME visible
        columns.forEach(function (col) {
            hiddenCols[col] = (col !== 'OBJNAME');
        });
        colToggles.querySelectorAll('input[type=checkbox]').forEach(
            function (cb) { cb.checked = (cb.dataset.col === 'OBJNAME'); }
        );
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
