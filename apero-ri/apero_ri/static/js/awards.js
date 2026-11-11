(function () {
    'use strict';

    var labels = JSON.parse(document.getElementById('aw-labels').textContent);
    document.querySelectorAll('.aw-board').forEach(function (board) {
    var prefix = board.dataset.awPrefix;
    var kind = board.dataset.awKind;
    var instrument = board.dataset.awInstrument;

    function el(id) {
        return document.getElementById(id.replace(/^aw-/, prefix + '-'));
    }

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function medalIcon(medalName, title) {
        if (['gold', 'silver', 'bronze'].indexOf(medalName) < 0) {
            return '';
        }
        return (
            '<i class="fa-solid fa-medal upu-medal upu-medal--' + medalName +
            '" role="img" aria-label="' + esc(labels[medalName]) +
            '" title="' + esc(title + ' - ' + labels[medalName]) + '"></i>'
        );
    }

    var dataEl = document.getElementById('aw-data');
    var allRows = [];
    try {
        allRows = JSON.parse(dataEl ? dataEl.textContent : '[]') || [];
    } catch (e) {
        allRows = [];
    }
    var instruments = kind === 'instrument' ? [instrument] : [];

    // ── Columns ──────────────────────────────────────────────────
    var COLUMNS = [
        {key: 'username', label: labels.username, filterable: true,
            render: function (row) {
                return '<a class="ari-user-link" data-username="' +
                    esc(row.username) + '" href="/user_portal/users/' +
                    encodeURIComponent(row.username) + '">' +
                    esc(row.username) + '</a>';
            }},
        {key: 'who', label: labels.name, filterable: true}
    ];
    instruments.forEach(function (inst) {
        COLUMNS.push({
            key: 'inst:' + inst,
            label: labels.hours,
            filterable: false,
            numeric: true,
            getValue: function (row) {
                return Number((row.instruments || {})[inst] || 0);
            },
            render: function (row) {
                var hours = (row.instruments || {})[inst];
                var medal = (row.instrument_medals || {})[inst];
                var txt = hours != null ? Number(hours).toFixed(2) : '—';
                return txt + medalIcon(medal, inst);
            }
        });
    });
    if (kind === 'service') {
    COLUMNS.push({
        key: 'total_hours',
        label: labels.hours,
        filterable: false,
        numeric: true,
        render: function (row) {
            return (
                Number(row.total_hours || 0).toFixed(2) +
                medalIcon(row.service_medal, labels.service)
            );
        }
    });
    COLUMNS.push({
        key: 'issues_resolved',
        label: labels.issues,
        filterable: false,
        numeric: true,
        render: function (row) {
            return (
                String(row.issues_resolved || 0) +
                medalIcon(row.issues_medal, labels.issues)
            );
        }
    });
    }
    if (kind === 'bytes' || kind === 'files') {
        COLUMNS.push({
            key: 'download_' + kind,
            label: labels[kind],
            numeric: true,
            render: function (row) {
                var value = Number(row['download_' + kind] || 0);
                var text = value.toLocaleString();
                if (kind === 'bytes') {
                    var units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'];
                    var unit = 0;
                    while (value >= 1024 && unit < units.length - 1) {
                        value /= 1024;
                        unit += 1;
                    }
                    text = value.toLocaleString(undefined,
                        {maximumFractionDigits: 2}) + ' ' + units[unit];
                }
                return text + medalIcon((row.download_medals || {})[kind], labels[kind]);
            }
        });
    }

    var metricKey = kind === 'instrument' ? 'inst:' + instrument :
        (kind === 'service' ? 'total_hours' : 'download_' + kind);
    allRows = allRows.filter(function (row) {
        if (kind === 'instrument') return Number((row.instruments || {})[instrument] || 0) > 0;
        if (kind === 'service') return Number(row.total_hours || 0) > 0 || Number(row.issues_resolved || 0) > 0;
        return Number(row[metricKey] || 0) > 0;
    });

    // ── State ────────────────────────────────────────────────────
    var sortCol = metricKey;
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

            var lbl = document.createElement('button');
            lbl.type = 'button';
            lbl.className = 'ot-th__label aw-sort';
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
            if (sortCol === col.key) {
                th.setAttribute('aria-sort', sortDir > 0 ? 'ascending' : 'descending');
            }

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
                inp.placeholder = labels.filter;
                inp.setAttribute('aria-label', labels.filter + ': ' + col.label);
                inp.value = colFilters[col.key] || '';
                inp.addEventListener('input', function () {
                    colFilters[col.key] = inp.value.trim().toLowerCase();
                    currentPage = 1;
                    applyFilterSort(true);
                });
                tf.appendChild(inp);
            }
            filterRow.appendChild(tf);
        });
    }

    function applyFilterSort(keepHeaders) {
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
                    return (av - bv) * sortDir || String(a.username).localeCompare(String(b.username));
                }
                av = String(av == null ? '' : av).toLowerCase();
                bv = String(bv == null ? '' : bv).toLowerCase();
                return av < bv ? -sortDir : av > bv ? sortDir : 0;
            });
        }

        filteredRows = rows;
        if (!keepHeaders) renderHeaders();
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
        pageInfo.textContent = n.toLocaleString();
        pageInput.value = currentPage;
        pageInput.max = tp;
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
                '" class="ot-loading">' + esc(labels.empty) + '</td></tr>'
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
    });
})();
