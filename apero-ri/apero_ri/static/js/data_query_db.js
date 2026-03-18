/**
 * ARI Data Portal — Database Query Explorer
 *
 * Builds a structured query (tables, columns, joins, filters, sort/limit)
 * and submits it to /api/data-portal/query-db/run for safe execution.
 * All validation is done server-side; this file only handles the UI.
 */
(function () {
    'use strict';

    /* ------------------------------------------------------------------ */
    /* Globals                                                              */
    /* ------------------------------------------------------------------ */
    var cfg = window.QDB_CONFIG || {};
    var profileId = cfg.profileId || '';
    var schemaApiUrl = cfg.schemaApiUrl || '/api/data-portal/query-db/schema';
    var runApiUrl = cfg.runApiUrl || '/api/data-portal/query-db/run';

    /** Full schema returned by /schema API: [{label, table_name, columns, has_run_id_filter}] */
    var schema = [];
    /** Currently selected tables: {label: {columns: [selected cols]}} */
    var selectedTables = {};
    /** Join rows: [{left_label, left_col, right_label, right_col, type}] */
    var joins = [];
    /** Filter rows: [{table_label, column, op, value}] */
    var filters = [];
    /** Last query result rows (all pages) */
    var resultRows = [];
    /** Pagination state */
    var currentPage = 1;
    var rowsPerPage = 50;

    /* ------------------------------------------------------------------ */
    /* DOM helpers                                                          */
    /* ------------------------------------------------------------------ */
    function el(id) { return document.getElementById(id); }

    function show(id) {
        var e = typeof id === 'string' ? el(id) : id;
        if (e) e.style.display = '';
    }

    function hide(id) {
        var e = typeof id === 'string' ? el(id) : id;
        if (e) e.style.display = 'none';
    }

    function makeEl(tag, cls, html) {
        var e = document.createElement(tag);
        if (cls) e.className = cls;
        if (html !== undefined) e.innerHTML = html;
        return e;
    }

    function makeSelect(options, value, cls) {
        var sel = document.createElement('select');
        if (cls) sel.className = cls;
        options.forEach(function (opt) {
            var o = document.createElement('option');
            o.value = opt.value !== undefined ? opt.value : opt;
            o.textContent = opt.label !== undefined ? opt.label : opt;
            if (o.value === value) o.selected = true;
            sel.appendChild(o);
        });
        return sel;
    }

    /* ------------------------------------------------------------------ */
    /* Schema loading                                                       */
    /* ------------------------------------------------------------------ */
    function loadSchema() {
        hide('qdb-no-access');
        show('qdb-schema-loading');

        fetch(schemaApiUrl + '?profile_id=' + encodeURIComponent(profileId))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                hide('qdb-schema-loading');
                if (!data.success || !data.tables || !data.tables.length) {
                    show('qdb-no-access');
                    return;
                }
                schema = data.tables;
                renderTablesSection();
                show('qdb-tables-section');
                show('qdb-filters-section');
                show('qdb-sort-section');
                show('qdb-run-section');
            })
            .catch(function () {
                hide('qdb-schema-loading');
                show('qdb-no-access');
            });
    }

    /* ------------------------------------------------------------------ */
    /* Tables & Columns section                                             */
    /* ------------------------------------------------------------------ */
    function renderTablesSection() {
        var body = el('qdb-tables-body');
        body.innerHTML = '';

        schema.forEach(function (tbl) {
            var label = tbl.label;
            var isSelected = !!selectedTables[label];

            var card = makeEl('div', 'qdb-table-card' + (isSelected
                ? ' qdb-table-card--selected' : ''));
            card.dataset.label = label;

            var hdr = makeEl('div', 'qdb-table-card__hdr');
            var checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = isSelected;
            checkbox.dataset.label = label;
            checkbox.addEventListener('change', function () {
                if (this.checked) {
                    selectedTables[label] = { columns: tbl.columns.slice() };
                } else {
                    delete selectedTables[label];
                }
                renderTablesSection();
                updateJoinsSection();
                updateSortOptions();
                updateJoinTableOptions();
            });

            var titleSpan = makeEl('span', 'qdb-table-card__title');
            titleSpan.textContent = label;

            var badgeSpan = makeEl('span',
                'qdb-table-card__badge' +
                    (tbl.has_run_id_filter ? ' qdb-badge--findex' : ''));
            badgeSpan.textContent = tbl.has_run_id_filter
                ? '🔒 Run-ID filtered' : tbl.table_name;

            hdr.appendChild(checkbox);
            hdr.appendChild(titleSpan);
            hdr.appendChild(badgeSpan);
            card.appendChild(hdr);

            if (isSelected) {
                // Column checkboxes
                var colWrap = makeEl('div', 'qdb-col-wrap');
                var selCols = selectedTables[label].columns;
                var selSet = new Set(selCols);

                var allBtn = makeEl('button', 'qdb-col-ctrl-btn',
                    '<i class="fa-solid fa-check-double"></i> All');
                allBtn.type = 'button';
                allBtn.addEventListener('click', function () {
                    selectedTables[label].columns = tbl.columns.slice();
                    renderTablesSection();
                    updateSortOptions();
                });

                var noneBtn = makeEl('button', 'qdb-col-ctrl-btn',
                    '<i class="fa-solid fa-xmark"></i> None');
                noneBtn.type = 'button';
                noneBtn.addEventListener('click', function () {
                    selectedTables[label].columns = [];
                    renderTablesSection();
                    updateSortOptions();
                });

                var ctrlRow = makeEl('div', 'qdb-col-ctrl-row');
                ctrlRow.appendChild(allBtn);
                ctrlRow.appendChild(noneBtn);
                colWrap.appendChild(ctrlRow);

                var grid = makeEl('div', 'qdb-col-grid');
                tbl.columns.forEach(function (col) {
                    var lbl = makeEl('label', 'qdb-col-label');
                    var cb = document.createElement('input');
                    cb.type = 'checkbox';
                    cb.checked = selSet.has(col);
                    cb.dataset.label = label;
                    cb.dataset.col = col;
                    cb.addEventListener('change', function () {
                        var cols = selectedTables[label].columns;
                        if (this.checked) {
                            if (cols.indexOf(col) === -1) cols.push(col);
                        } else {
                            var idx = cols.indexOf(col);
                            if (idx > -1) cols.splice(idx, 1);
                        }
                        updateSortOptions();
                    });
                    var span = makeEl('span', '', col);
                    lbl.appendChild(cb);
                    lbl.appendChild(span);
                    grid.appendChild(lbl);
                });
                colWrap.appendChild(grid);
                card.appendChild(colWrap);
            }

            body.appendChild(card);
        });
    }

    /* ------------------------------------------------------------------ */
    /* Joins section                                                        */
    /* ------------------------------------------------------------------ */
    function updateJoinsSection() {
        var numSelected = Object.keys(selectedTables).length;
        var sec = el('qdb-joins-section');
        if (numSelected >= 2) {
            show(sec);
        } else {
            hide(sec);
            joins = [];
            renderJoins();
        }
        updateJoinTableOptions();
    }

    function availableTableLabels() {
        return Object.keys(selectedTables).sort();
    }

    function colsForTable(label) {
        var tbl = schema.find(function (t) { return t.label === label; });
        return tbl ? tbl.columns : [];
    }

    function renderJoins() {
        var body = el('qdb-joins-body');
        body.innerHTML = '';
        joins.forEach(function (j, idx) {
            body.appendChild(makeJoinRow(j, idx));
        });
    }

    function makeJoinRow(j, idx) {
        var row = makeEl('div', 'qdb-join-row');

        var tables = availableTableLabels();

        // Type selector
        var typeOpts = ['INNER', 'LEFT', 'RIGHT'].map(function (t) {
            return { value: t, label: t + ' JOIN' };
        });
        var typeSel = makeSelect(typeOpts, j.type || 'LEFT', 'qdb-select');
        typeSel.addEventListener('change', function () {
            joins[idx].type = this.value;
        });

        // Left table
        var leftOpts = tables.map(function (t) {
            return { value: t, label: t };
        });
        var leftSel = makeSelect(leftOpts, j.left_label, 'qdb-select');
        leftSel.addEventListener('change', function () {
            joins[idx].left_label = this.value;
            joins[idx].left_col = '';
            renderJoins();
        });

        // Left column
        var leftCols = colsForTable(j.left_label);
        var leftColOpts = [{ value: '', label: '— col —' }].concat(
            leftCols.map(function (c) { return { value: c, label: c }; })
        );
        var leftColSel = makeSelect(leftColOpts, j.left_col, 'qdb-select');
        leftColSel.addEventListener('change', function () {
            joins[idx].left_col = this.value;
        });

        var eqSpan = makeEl('span', 'qdb-join-eq', '=');

        // Right table
        var rightSel = makeSelect(leftOpts, j.right_label, 'qdb-select');
        rightSel.addEventListener('change', function () {
            joins[idx].right_label = this.value;
            joins[idx].right_col = '';
            renderJoins();
        });

        // Right column
        var rightCols = colsForTable(j.right_label);
        var rightColOpts = [{ value: '', label: '— col —' }].concat(
            rightCols.map(function (c) { return { value: c, label: c }; })
        );
        var rightColSel = makeSelect(rightColOpts, j.right_col, 'qdb-select');
        rightColSel.addEventListener('change', function () {
            joins[idx].right_col = this.value;
        });

        // Remove button
        var removeBtn = makeEl('button', 'qdb-remove-btn',
            '<i class="fa-solid fa-xmark"></i>');
        removeBtn.type = 'button';
        removeBtn.title = 'Remove join';
        removeBtn.addEventListener('click', function () {
            joins.splice(idx, 1);
            renderJoins();
        });

        row.appendChild(typeSel);
        row.appendChild(leftSel);
        row.appendChild(leftColSel);
        row.appendChild(eqSpan);
        row.appendChild(rightSel);
        row.appendChild(rightColSel);
        row.appendChild(removeBtn);
        return row;
    }

    function updateJoinTableOptions() {
        // Re-render so selects reflect current table selection
        renderJoins();
    }

    /* ------------------------------------------------------------------ */
    /* Filters section                                                      */
    /* ------------------------------------------------------------------ */
    function renderFilters() {
        var body = el('qdb-filters-body');
        body.innerHTML = '';
        filters.forEach(function (f, idx) {
            body.appendChild(makeFilterRow(f, idx));
        });
    }

    function allSelectedCols() {
        var tables = availableTableLabels();
        var opts = [{ value: '', label: '— col —' }];
        tables.forEach(function (label) {
            var cols = (selectedTables[label] || {}).columns || [];
            cols.forEach(function (col) {
                opts.push({ value: label + '.' + col, label: label + '.' + col });
            });
        });
        return opts;
    }

    var FILTER_OPS = [
        { value: '=', label: '=' },
        { value: '!=', label: '!=' },
        { value: '<', label: '<' },
        { value: '>', label: '>' },
        { value: '<=', label: '<=' },
        { value: '>=', label: '>=' },
        { value: 'LIKE', label: 'LIKE' },
        { value: 'NOT LIKE', label: 'NOT LIKE' },
        { value: 'IS NULL', label: 'IS NULL' },
        { value: 'IS NOT NULL', label: 'IS NOT NULL' },
    ];

    function makeFilterRow(f, idx) {
        var row = makeEl('div', 'qdb-filter-row');

        var colOpts = allSelectedCols();
        var colKey = f.table_label ? (f.table_label + '.' + f.column) : '';
        var colSel = makeSelect(colOpts, colKey, 'qdb-select qdb-select--wide');
        colSel.addEventListener('change', function () {
            var parts = this.value.split('.', 2);
            filters[idx].table_label = parts[0] || '';
            filters[idx].column = parts[1] || '';
        });

        var opSel = makeSelect(FILTER_OPS, f.op || '=', 'qdb-select');
        opSel.addEventListener('change', function () {
            filters[idx].op = this.value;
            // Toggle value input visibility
            var valInput = row.querySelector('.qdb-filter-val');
            if (valInput) {
                valInput.style.display =
                    (this.value === 'IS NULL' || this.value === 'IS NOT NULL')
                        ? 'none' : '';
            }
        });

        var isNull = (f.op === 'IS NULL' || f.op === 'IS NOT NULL');
        var valInput = makeEl('input', 'qdb-filter-val qdb-input');
        valInput.type = 'text';
        valInput.value = f.value || '';
        valInput.placeholder = 'value';
        if (isNull) valInput.style.display = 'none';
        valInput.addEventListener('input', function () {
            filters[idx].value = this.value;
        });

        var removeBtn = makeEl('button', 'qdb-remove-btn',
            '<i class="fa-solid fa-xmark"></i>');
        removeBtn.type = 'button';
        removeBtn.title = 'Remove filter';
        removeBtn.addEventListener('click', function () {
            filters.splice(idx, 1);
            renderFilters();
        });

        row.appendChild(colSel);
        row.appendChild(opSel);
        row.appendChild(valInput);
        row.appendChild(removeBtn);
        return row;
    }

    /* ------------------------------------------------------------------ */
    /* Sort options                                                         */
    /* ------------------------------------------------------------------ */
    function updateSortOptions() {
        var sel = el('qdb-sort-col');
        if (!sel) return;
        var prev = sel.value;
        while (sel.options.length > 0) sel.remove(0);

        var noneOpt = document.createElement('option');
        noneOpt.value = '';
        noneOpt.textContent = '— none —';
        sel.appendChild(noneOpt);

        availableTableLabels().forEach(function (label) {
            var cols = (selectedTables[label] || {}).columns || [];
            cols.forEach(function (col) {
                var opt = document.createElement('option');
                opt.value = label + '.' + col;
                opt.textContent = label + '.' + col;
                if (opt.value === prev) opt.selected = true;
                sel.appendChild(opt);
            });
        });
    }

    /* ------------------------------------------------------------------ */
    /* Run Query                                                            */
    /* ------------------------------------------------------------------ */
    function buildQuerySpec() {
        var tables = availableTableLabels().map(function (label) {
            var cols = (selectedTables[label] || {}).columns || [];
            return { label: label, columns: cols };
        });

        var cleanJoins = joins
            .filter(function (j) {
                return j.left_label && j.right_label && j.left_col && j.right_col;
            })
            .map(function (j) {
                return {
                    left_label: j.left_label,
                    left_col: j.left_col,
                    right_label: j.right_label,
                    right_col: j.right_col,
                    type: j.type || 'LEFT',
                };
            });

        var cleanFilters = filters
            .filter(function (f) {
                return f.table_label && f.column && f.op;
            })
            .map(function (f) {
                return {
                    table_label: f.table_label,
                    column: f.column,
                    op: f.op,
                    value: f.value || '',
                };
            });

        var sortColSel = el('qdb-sort-col');
        var orderBy = null;
        if (sortColSel && sortColSel.value) {
            var parts = sortColSel.value.split('.', 2);
            orderBy = {
                table_label: parts[0],
                column: parts[1] || '',
                direction: (el('qdb-sort-dir') || {}).value || 'ASC',
            };
        }

        var limitSel = el('qdb-limit');
        var limit = limitSel ? parseInt(limitSel.value, 10) : 500;

        return {
            profile_id: profileId,
            tables: tables,
            joins: cleanJoins,
            filters: cleanFilters,
            order_by: orderBy,
            limit: limit,
        };
    }

    function runQuery() {
        var labels = availableTableLabels();
        if (!labels.length) {
            showError('Select at least one table before running.');
            return;
        }

        // Check all selected tables have at least one column
        for (var i = 0; i < labels.length; i++) {
            if (!(selectedTables[labels[i]].columns || []).length) {
                showError('Table ' + labels[i] + ' has no columns selected.');
                return;
            }
        }

        var btn = el('qdb-run-btn');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running…';
        }
        hide('qdb-error');
        hide('qdb-table-wrap');
        hide('qdb-pagination');
        hide('qdb-results-meta');
        hide('qdb-export-csv');
        show('qdb-idle');
        el('qdb-idle').innerHTML =
            '<i class="fa-solid fa-spinner fa-spin qdb-idle__icon"></i>' +
            '<p>Running query…</p>';

        var spec = buildQuerySpec();
        var t0 = Date.now();

        fetch(runApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(spec),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var elapsed = ((Date.now() - t0) / 1000).toFixed(2);
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML =
                        '<i class="fa-solid fa-play"></i> Run Query';
                }

                // Update SQL preview
                var pre = el('qdb-sql-pre');
                if (pre) pre.textContent = data.sql_preview || '—';
                var badge = el('qdb-sql-badge');
                if (badge) badge.textContent = data.success ? '' : 'error';

                if (!data.success) {
                    showError(data.error || 'Unknown error.');
                    return;
                }

                resultRows = data.rows || [];
                renderResults(data.columns || [], resultRows, elapsed);
            })
            .catch(function (err) {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML =
                        '<i class="fa-solid fa-play"></i> Run Query';
                }
                showError('Network error: ' + err);
            });
    }

    /* ------------------------------------------------------------------ */
    /* Results rendering                                                    */
    /* ------------------------------------------------------------------ */
    /**
     * Format a TABLE__col key for display.
     * If all columns share the same table prefix, strip it.
     * Otherwise, show "col (TABLE)".
     */
    function formatColHeader(key, allKeys) {
        var parts = key.split('__', 2);
        if (parts.length < 2) return key;
        var tableLabel = parts[0];
        var col = parts[1];
        // Check if all columns share the same table
        var tables = new Set(allKeys.map(function (k) {
            return k.split('__', 2)[0];
        }));
        if (tables.size === 1) return col;
        return col + ' (' + tableLabel + ')';
    }

    function renderResults(columns, rows, elapsed) {
        if (!rows.length) {
            el('qdb-idle').innerHTML =
                '<i class="fa-solid fa-inbox qdb-idle__icon"></i>' +
                '<p>No rows returned.</p>';
            show('qdb-idle');
            hide('qdb-table-wrap');
            hide('qdb-pagination');
            show('qdb-results-meta');
            el('qdb-results-count').textContent = '0 rows';
            el('qdb-results-time').textContent = 'in ' + elapsed + 's';
            hide('qdb-export-csv');
            return;
        }

        // Build header
        var hdr = el('qdb-header-row');
        hdr.innerHTML = '';
        columns.forEach(function (col) {
            var th = makeEl('th', 'ot-th');
            th.textContent = formatColHeader(col, columns);
            th.title = col;
            hdr.appendChild(th);
        });

        // Pagination
        currentPage = 1;
        renderPage(columns, rows);

        // Meta bar
        show('qdb-results-meta');
        el('qdb-results-count').textContent =
            rows.length + ' row' + (rows.length !== 1 ? 's' : '');
        el('qdb-results-time').textContent = 'in ' + elapsed + 's';
        show('qdb-export-csv');

        hide('qdb-idle');
        show('qdb-table-wrap');
        show('qdb-pagination');
    }

    function renderPage(columns, rows) {
        var tbody = el('qdb-tbody');
        tbody.innerHTML = '';

        var total = rows.length;
        var totalPages = Math.ceil(total / rowsPerPage);
        if (totalPages < 1) totalPages = 1;
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        var start = (currentPage - 1) * rowsPerPage;
        var end = Math.min(start + rowsPerPage, total);
        var pageRows = rows.slice(start, end);

        pageRows.forEach(function (row) {
            var tr = document.createElement('tr');
            columns.forEach(function (col) {
                var td = makeEl('td', 'ot-td');
                var val = row[col];
                td.textContent = val !== null && val !== undefined ? String(val) : '';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        // Update pagination controls
        el('qdb-page-input').value = currentPage;
        el('qdb-page-total').textContent = totalPages;
        el('qdb-page-info').textContent =
            'Rows ' + (start + 1) + '–' + end + ' of ' + total;

        el('qdb-btn-first').disabled = currentPage <= 1;
        el('qdb-btn-prev').disabled = currentPage <= 1;
        el('qdb-btn-next').disabled = currentPage >= totalPages;
        el('qdb-btn-last').disabled = currentPage >= totalPages;
    }

    /* ------------------------------------------------------------------ */
    /* CSV export                                                           */
    /* ------------------------------------------------------------------ */
    function exportCsv(columns) {
        var lines = [];
        lines.push(columns.map(csvEscape).join(','));
        resultRows.forEach(function (row) {
            lines.push(columns.map(function (c) {
                return csvEscape(
                    row[c] !== null && row[c] !== undefined ? String(row[c]) : ''
                );
            }).join(','));
        });
        var blob = new Blob([lines.join('\r\n')], { type: 'text/csv' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = profileId + '_query_result.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function csvEscape(val) {
        if (val.indexOf(',') > -1 || val.indexOf('"') > -1
                || val.indexOf('\n') > -1) {
            return '"' + val.replace(/"/g, '""') + '"';
        }
        return val;
    }

    /* ------------------------------------------------------------------ */
    /* Error display                                                        */
    /* ------------------------------------------------------------------ */
    function showError(msg) {
        el('qdb-idle').innerHTML =
            '<i class="fa-solid fa-exclamation-triangle qdb-idle__icon"></i>' +
            '<p>Query failed.</p>';
        show('qdb-idle');
        show('qdb-error');
        el('qdb-error-msg').textContent = msg;
    }

    /* ------------------------------------------------------------------ */
    /* Event wiring                                                         */
    /* ------------------------------------------------------------------ */
    function wireEvents() {
        // Run query
        var runBtn = el('qdb-run-btn');
        if (runBtn) runBtn.addEventListener('click', runQuery);

        // Add join
        var addJoinBtn = el('qdb-add-join');
        if (addJoinBtn) {
            addJoinBtn.addEventListener('click', function () {
                var tables = availableTableLabels();
                if (tables.length < 2) return;
                joins.push({
                    type: 'LEFT',
                    left_label: tables[0],
                    left_col: '',
                    right_label: tables[1],
                    right_col: '',
                });
                renderJoins();
            });
        }

        // Add filter
        var addFilterBtn = el('qdb-add-filter');
        if (addFilterBtn) {
            addFilterBtn.addEventListener('click', function () {
                var labels = availableTableLabels();
                if (!labels.length) return;
                var firstCols = (selectedTables[labels[0]] || {}).columns || [];
                filters.push({
                    table_label: labels[0],
                    column: firstCols[0] || '',
                    op: '=',
                    value: '',
                });
                renderFilters();
            });
        }

        // Pagination buttons
        el('qdb-btn-first').addEventListener('click', function () {
            currentPage = 1;
            var cols = currentColumns();
            renderPage(cols, resultRows);
        });
        el('qdb-btn-prev').addEventListener('click', function () {
            if (currentPage > 1) { currentPage--; renderPage(currentColumns(), resultRows); }
        });
        el('qdb-btn-next').addEventListener('click', function () {
            currentPage++;
            renderPage(currentColumns(), resultRows);
        });
        el('qdb-btn-last').addEventListener('click', function () {
            var total = Math.ceil(resultRows.length / rowsPerPage);
            currentPage = total;
            renderPage(currentColumns(), resultRows);
        });
        el('qdb-page-input').addEventListener('change', function () {
            var n = parseInt(this.value, 10);
            if (!isNaN(n)) {
                currentPage = n;
                renderPage(currentColumns(), resultRows);
            }
        });

        // Export CSV
        el('qdb-export-csv').addEventListener('click', function () {
            exportCsv(currentColumns());
        });
    }

    function currentColumns() {
        var ths = el('qdb-header-row').querySelectorAll('th');
        var cols = [];
        // Use title attribute which stores the raw TABLE__col key
        ths.forEach(function (th) { cols.push(th.title || th.textContent); });
        return cols;
    }

    /* ------------------------------------------------------------------ */
    /* Init                                                                 */
    /* ------------------------------------------------------------------ */
    function init() {
        wireEvents();
        if (profileId) {
            loadSchema();
        } else {
            show('qdb-no-access');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
