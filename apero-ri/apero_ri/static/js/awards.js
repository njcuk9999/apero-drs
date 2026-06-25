(function () {
    'use strict';

    function el(id) {
        return document.getElementById(id);
    }

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function medalIcon(medalName, title) {
        if (!medalName) {
            return '';
        }
        return (
            '<i class="fa-solid fa-medal upu-medal upu-medal--' + medalName +
            '" title="' + esc(title) + ' (' + medalName + ')"></i>'
        );
    }

    var dataEl = el('aw-data');
    var allRows = [];
    try {
        allRows = JSON.parse(dataEl ? dataEl.textContent : '[]') || [];
    } catch (e) {
        allRows = [];
    }
    var instruments = window.ARI_AWARDS_INSTRUMENTS || [];

    // ── Columns ──────────────────────────────────────────────────
    var COLUMNS = [
        {key: 'username', label: 'Username', filterable: true},
        {key: 'who', label: 'Name', filterable: true}
    ];
    instruments.forEach(function (inst) {
        COLUMNS.push({
            key: 'inst:' + inst,
            label: inst + ' hours',
            filterable: false,
            numeric: true,
            getValue: function (row) {
                return Number((row.instruments || {})[inst] || 0);
            },
            render: function (row) {
                var hours = (row.instruments || {})[inst];
                var medal = (row.instrument_medals || {})[inst];
                var txt = hours != null ? Number(hours).toFixed(2) : '—';
                return txt + medalIcon(medal, inst + ' top monitor');
            }
        });
    });
    COLUMNS.push({
        key: 'total_hours',
        label: 'Total hours',
        filterable: false,
        numeric: true,
        render: function (row) {
            return (
                Number(row.total_hours || 0).toFixed(2) +
                medalIcon(row.service_medal, 'Service award')
            );
        }
    });
    COLUMNS.push({
        key: 'issues_resolved',
        label: 'Issues resolved',
        filterable: false,
        numeric: true,
        render: function (row) {
            return (
                String(row.issues_resolved || 0) +
                medalIcon(row.issues_medal, 'Issue resolution award')
            );
        }
    });

    // ── State ────────────────────────────────────────────────────
    var sortCol = 'total_hours';
    var sortDir = -1;
    var colFilters = {};
    var filteredRows = allRows.slice();
    var currentPage = 1;
    var perPage = 10;
    var pageRowOffset = 0;

    var headerRow = el('aw-header-row');
    var filterRow = el('aw-filter-row');
    var tbody = el('aw-tbody');
    var pageInfo = el('aw-page-info');
    var pageInput = el('aw-page-input');
    var pageTotal = el('aw-page-total');
    var btnFirst = el('aw-btn-first');
    var btnPrev = el('aw-btn-prev');
    var btnNext = el('aw-btn-next');
    var btnLast = el('aw-btn-last');
    var perpageSelect = el('aw-perpage');

    function getValue(row, col) {
        if (col.getValue) {
            return col.getValue(row);
        }
        return row[col.key];
    }

    function renderHeaders() {
        headerRow.innerHTML = '';
        filterRow.innerHTML = '';

        COLUMNS.forEach(function (col) {
            var th = document.createElement('th');
            th.className = 'ot-th ot-th--sortable';
            if (sortCol === col.key) {
                th.classList.add(sortDir > 0 ? 'ot-th--asc' : 'ot-th--desc');
            }

            var lbl = document.createElement('span');
            lbl.className = 'ot-th__label';
            lbl.textContent = col.label;
            th.appendChild(lbl);

            var icn = document.createElement('span');
            icn.className = 'ot-th__sort-icon';
            if (sortCol === col.key) {
                icn.innerHTML = sortDir > 0
                    ? '<i class="fa-solid fa-sort-up"></i>'
                    : '<i class="fa-solid fa-sort-down"></i>';
            } else {
                icn.innerHTML = '<i class="fa-solid fa-sort ot-sort-idle"></i>';
            }
            th.appendChild(icn);

            th.addEventListener('click', function () {
                if (sortCol === col.key) {
                    sortDir = -sortDir;
                } else {
                    sortCol = col.key;
                    sortDir = col.numeric ? -1 : 1;
                }
                applyFilterSort();
            });
            headerRow.appendChild(th);

            var tf = document.createElement('th');
            tf.className = 'ot-filter-cell';
            if (col.filterable) {
                var inp = document.createElement('input');
                inp.type = 'text';
                inp.className = 'ot-filter-input';
                inp.placeholder = 'Filter…';
                inp.value = colFilters[col.key] || '';
                inp.addEventListener('input', function () {
                    colFilters[col.key] = inp.value.trim().toLowerCase();
                    currentPage = 1;
                    applyFilterSort();
                });
                tf.appendChild(inp);
            }
            filterRow.appendChild(tf);
        });
    }

    function applyFilterSort() {
        var rows = allRows.slice();

        Object.keys(colFilters).forEach(function (key) {
            var q = colFilters[key];
            if (!q) {
                return;
            }
            rows = rows.filter(function (row) {
                return String(row[key] == null ? '' : row[key])
                    .toLowerCase().indexOf(q) !== -1;
            });
        });

        var col = null;
        COLUMNS.forEach(function (c) {
            if (c.key === sortCol) {
                col = c;
            }
        });
        if (col) {
            rows.sort(function (a, b) {
                var av = getValue(a, col);
                var bv = getValue(b, col);
                if (col.numeric) {
                    av = Number(av || 0);
                    bv = Number(bv || 0);
                    return (av - bv) * sortDir;
                }
                av = String(av == null ? '' : av).toLowerCase();
                bv = String(bv == null ? '' : bv).toLowerCase();
                return av < bv ? -sortDir : av > bv ? sortDir : 0;
            });
        }

        filteredRows = rows;
        renderHeaders();
        updatePagination();
        renderPage();
    }

    function totalPages() {
        if (!perPage) {
            return 1;
        }
        return Math.max(1, Math.ceil(filteredRows.length / perPage));
    }

    function pageRows() {
        if (!perPage) {
            return filteredRows;
        }
        var start = (currentPage - 1) * perPage;
        return filteredRows.slice(start, start + perPage);
    }

    function updatePagination() {
        var tp = totalPages();
        if (currentPage > tp) {
            currentPage = tp;
        }
        pageRowOffset = perPage ? (currentPage - 1) * perPage : 0;
        var n = filteredRows.length;
        pageInfo.textContent = n + ' monitor' + (n !== 1 ? 's' : '');
        pageInput.value = currentPage;
        pageTotal.textContent = tp;
        btnFirst.disabled = currentPage <= 1;
        btnPrev.disabled = currentPage <= 1;
        btnNext.disabled = currentPage >= tp;
        btnLast.disabled = currentPage >= tp;
    }

    function renderPage() {
        var rows = pageRows();
        if (!rows.length) {
            tbody.innerHTML = (
                '<tr><td colspan="' + COLUMNS.length +
                '" class="ot-empty">No monitors found.</td></tr>'
            );
            return;
        }
        var frag = document.createDocumentFragment();
        rows.forEach(function (row) {
            var tr = document.createElement('tr');
            tr.className = 'ot-row';
            COLUMNS.forEach(function (col) {
                var td = document.createElement('td');
                td.className = 'ot-cell';
                if (col.render) {
                    td.innerHTML = col.render(row);
                } else {
                    td.textContent = row[col.key] == null ? '—' : row[col.key];
                }
                tr.appendChild(td);
            });
            frag.appendChild(tr);
        });
        tbody.innerHTML = '';
        tbody.appendChild(frag);
    }

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
        currentPage = Math.min(totalPages(), currentPage + 1);
        updatePagination();
        renderPage();
    });
    btnLast.addEventListener('click', function () {
        currentPage = totalPages();
        updatePagination();
        renderPage();
    });
    pageInput.addEventListener('change', function () {
        var v = parseInt(pageInput.value, 10) || 1;
        currentPage = Math.max(1, Math.min(v, totalPages()));
        updatePagination();
        renderPage();
    });
    perpageSelect.addEventListener('change', function () {
        perPage = Number(perpageSelect.value) || 10;
        currentPage = 1;
        updatePagination();
        renderPage();
    });

    perpageSelect.value = String(perPage);
    applyFilterSort();
})();
