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
    var basketAddApiUrl = cfg.basketAddApiUrl || '/api/data-portal/basket/add';
    var basketSummaryApiUrl = cfg.basketSummaryApiUrl || '/api/data-portal/basket/summary';
    var presets = Array.isArray(cfg.presets) ? cfg.presets : [];

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
    /** Current result columns */
    var resultColumns = [];
    /** Selected result row indices (global indices in resultRows) */
    var selectedRowIdxs = new Set();
    /** Addable row indices currently visible on page */
    var visibleAddableIdxs = [];

    /** Top horizontal scroll mirror state */
    var _scrollSync = false;

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

    function formatBytes(num) {
        var n = Number(num || 0);
        if (!isFinite(n) || n <= 0) return '0 B';
        var units = ['B', 'KB', 'MB', 'GB', 'TB'];
        var i = 0;
        while (n >= 1024 && i < units.length - 1) {
            n /= 1024;
            i++;
        }
        return n.toFixed(i === 0 ? 0 : 1) + ' ' + units[i];
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
                renderFilters();
                updateJoinsSection();
                show('qdb-tables-section');
                show('qdb-filters-section');
                show('qdb-sort-section');
                show('qdb-run-section');
                initPresetsSection();
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
                pruneInvalidJoins();
                pruneInvalidFilters();
                renderTablesSection();
                updateJoinsSection();
                renderFilters();
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
                    pruneInvalidJoins();
                    pruneInvalidFilters();
                    updateJoinsSection();
                    renderFilters();
                    updateSortOptions();
                });

                var noneBtn = makeEl('button', 'qdb-col-ctrl-btn',
                    '<i class="fa-solid fa-xmark"></i> None');
                noneBtn.type = 'button';
                noneBtn.addEventListener('click', function () {
                    selectedTables[label].columns = [];
                    renderTablesSection();
                    pruneInvalidJoins();
                    pruneInvalidFilters();
                    updateJoinsSection();
                    renderFilters();
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
                        pruneInvalidJoins();
                        pruneInvalidFilters();
                        renderFilters();
                        updateJoinsSection();
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
            pruneInvalidJoins();
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

    function pruneInvalidJoins() {
        var tableSet = new Set(availableTableLabels());
        joins = joins.filter(function (j) {
            if (!tableSet.has(j.left_label) || !tableSet.has(j.right_label)) {
                return false;
            }
            var leftCols = (selectedTables[j.left_label] || {}).columns || [];
            var rightCols = (selectedTables[j.right_label] || {}).columns || [];
            return leftCols.indexOf(j.left_col) > -1
                && rightCols.indexOf(j.right_col) > -1;
        });
    }

    function pruneInvalidFilters() {
        var tableSet = new Set(availableTableLabels());
        filters = filters.filter(function (f) {
            if (!tableSet.has(f.table_label)) return false;
            var tbl = schema.find(function (t) { return t.label === f.table_label; });
            var cols = tbl ? tbl.columns : [];
            return cols.indexOf(f.column) > -1;
        });
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

        if (!filters.length) {
            var empty = makeEl(
                'button',
                'qdb-empty-add',
                '<i class="fa-solid fa-plus"></i> Click to add filter'
            );
            empty.type = 'button';
            empty.addEventListener('click', function () {
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
            body.appendChild(empty);
            return;
        }

        filters.forEach(function (f, idx) {
            body.appendChild(makeFilterRow(f, idx));
        });
    }

    function allSelectedCols() {
        var tables = availableTableLabels();
        var opts = [{ value: '', label: '— col —' }];
        tables.forEach(function (label) {
            var tbl = schema.find(function (t) { return t.label === label; });
            var cols = tbl ? tbl.columns : [];
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
    /* Presets                                                             */
    /* ------------------------------------------------------------------ */
    function initPresetsSection() {
        var section = el('qdb-presets-section');
        var sel = el('qdb-preset-select');
        if (!section || !sel || !presets.length) return;

        show(section);
        while (sel.options.length > 1) sel.remove(1);

        presets.forEach(function (preset, idx) {
            var opt = document.createElement('option');
            opt.value = String(idx);
            opt.textContent = preset.name || ('Preset ' + (idx + 1));
            sel.appendChild(opt);
        });
    }

    function stripSqlIdentifier(raw) {
        return String(raw || '')
            .replace(/^[`\"']+|[`\"']+$/g, '')
            .trim();
    }

    function splitSqlCommaList(text) {
        var out = [];
        var cur = '';
        var depth = 0;
        var quote = '';
        for (var i = 0; i < text.length; i++) {
            var ch = text[i];
            if (quote) {
                cur += ch;
                if (ch === quote) quote = '';
                continue;
            }
            if (ch === '\'' || ch === '"') {
                quote = ch;
                cur += ch;
                continue;
            }
            if (ch === '(') {
                depth++;
                cur += ch;
                continue;
            }
            if (ch === ')') {
                depth = Math.max(0, depth - 1);
                cur += ch;
                continue;
            }
            if (ch === ',' && depth === 0) {
                if (cur.trim()) out.push(cur.trim());
                cur = '';
                continue;
            }
            cur += ch;
        }
        if (cur.trim()) out.push(cur.trim());
        return out;
    }

    function parsePresetFilterCondition(cond, label, allowedCols) {
        var raw = String(cond || '').trim();
        if (!raw) return null;

        var mNull = raw.match(/^(.+?)\s+(IS\s+NOT\s+NULL|IS\s+NULL)$/i);
        if (mNull) {
            var colNull = stripSqlIdentifier(mNull[1].split('.').pop());
            var opNull = mNull[2].toUpperCase().replace(/\s+/g, ' ');
            if (allowedCols.indexOf(colNull) > -1) {
                return {
                    table_label: label,
                    column: colNull,
                    op: opNull,
                    value: '',
                };
            }
            return null;
        }

        var mCmp = raw.match(/^(.+?)\s*(NOT\s+LIKE|LIKE|!=|<=|>=|=|<|>)\s*(.+)$/i);
        if (!mCmp) return null;

        var col = stripSqlIdentifier(mCmp[1].split('.').pop());
        var op = mCmp[2].toUpperCase().replace(/\s+/g, ' ');
        var val = String(mCmp[3] || '').trim();
        val = val.replace(/^['\"]|['\"]$/g, '');

        if (allowedCols.indexOf(col) === -1) return null;
        return {
            table_label: label,
            column: col,
            op: op,
            value: val,
        };
    }

    function parsePresetSqlToSpec(sql) {
        var text = String(sql || '').trim().replace(/;\s*$/, '');
        if (!text) return null;

        var m = text.match(
            /^\s*SELECT\s+([\s\S]+?)\s+FROM\s+([^\s]+(?:\s+[^\s]+)?)\s*(?:WHERE\s+([\s\S]*?))?\s*(?:ORDER\s+BY\s+([\s\S]*?))?\s*(?:LIMIT\s+(\d+))?\s*$/i
        );
        if (!m) return null;

        var selectText = m[1] || '';
        var fromText = m[2] || '';
        var whereText = m[3] || '';
        var orderText = m[4] || '';
        var limitText = m[5] || '';

        var fromParts = fromText.trim().split(/\s+/);
        var tableName = stripSqlIdentifier(fromParts[0]);

        var tbl = schema.find(function (t) {
            return String(t.table_name || '').toLowerCase() === tableName.toLowerCase();
        });
        if (!tbl) return null;

        var label = tbl.label;
        var allowedCols = (tbl.columns || []).slice();
        var selectedCols = [];

        splitSqlCommaList(selectText).forEach(function (exprRaw) {
            var expr = String(exprRaw || '').trim();
            if (!expr) return;

            if (expr === '*') {
                selectedCols = allowedCols.slice();
                return;
            }

            var src = expr;
            var asMatch = expr.match(/^(.+?)\s+AS\s+.+$/i);
            if (asMatch) src = asMatch[1];
            else {
                var parts = expr.split(/\s+/);
                if (parts.length > 1) src = parts[0];
            }

            var col = stripSqlIdentifier(src.split('.').pop());
            if (allowedCols.indexOf(col) > -1 && selectedCols.indexOf(col) === -1) {
                selectedCols.push(col);
            }
        });

        if (!selectedCols.length) {
            selectedCols = allowedCols.slice();
        }

        var parsedFilters = [];
        if (whereText) {
            whereText.split(/\s+AND\s+/i).forEach(function (part) {
                var parsed = parsePresetFilterCondition(part, label, allowedCols);
                if (parsed) parsedFilters.push(parsed);
            });
        }

        var orderBy = null;
        if (orderText) {
            var firstOrder = splitSqlCommaList(orderText)[0] || '';
            var om = String(firstOrder).trim().match(/^(.+?)(?:\s+(ASC|DESC))?$/i);
            if (om) {
                var orderCol = stripSqlIdentifier(String(om[1] || '').split('.').pop());
                if (selectedCols.indexOf(orderCol) > -1) {
                    orderBy = {
                        table_label: label,
                        column: orderCol,
                        direction: (om[2] || 'ASC').toUpperCase(),
                    };
                }
            }
        }

        var limit = limitText ? parseInt(limitText, 10) : 500;
        if (isNaN(limit)) limit = 500;

        return {
            tables: [{ label: label, columns: selectedCols }],
            joins: [],
            filters: parsedFilters,
            order_by: orderBy,
            limit: limit,
        };
    }

    function applyQuerySpecToBuilder(spec) {
        var nextTables = {};
        (spec.tables || []).forEach(function (t) {
            if (!t || !t.label) return;
            var sTable = schema.find(function (st) { return st.label === t.label; });
            if (!sTable) return;
            var allowed = new Set(sTable.columns || []);
            var cols = (t.columns || []).filter(function (c) { return allowed.has(c); });
            if (!cols.length) cols = (sTable.columns || []).slice();
            nextTables[t.label] = { columns: cols };
        });

        selectedTables = nextTables;
        joins = Array.isArray(spec.joins) ? spec.joins.slice() : [];
        filters = Array.isArray(spec.filters) ? spec.filters.slice() : [];

        pruneInvalidJoins();
        pruneInvalidFilters();

        renderTablesSection();
        updateJoinsSection();
        renderFilters();
        updateSortOptions();

        var sortColSel = el('qdb-sort-col');
        var sortDirSel = el('qdb-sort-dir');
        if (sortColSel) {
            if (spec.order_by && spec.order_by.table_label && spec.order_by.column) {
                sortColSel.value = spec.order_by.table_label + '.' + spec.order_by.column;
            } else {
                sortColSel.value = '';
            }
        }
        if (sortDirSel && spec.order_by && spec.order_by.direction) {
            sortDirSel.value = String(spec.order_by.direction).toUpperCase() === 'DESC'
                ? 'DESC' : 'ASC';
        }

        var limitSel = el('qdb-limit');
        if (limitSel) {
            var wanted = String(spec.limit || 500);
            var hasOption = false;
            for (var i = 0; i < limitSel.options.length; i++) {
                if (limitSel.options[i].value === wanted) {
                    hasOption = true;
                    break;
                }
            }
            if (!hasOption) {
                var opt = document.createElement('option');
                opt.value = wanted;
                opt.textContent = wanted;
                limitSel.appendChild(opt);
            }
            limitSel.value = wanted;
        }
    }

    function applySelectedPreset() {
        var sel = el('qdb-preset-select');
        if (!sel || sel.value === '') return;

        var idx = parseInt(sel.value, 10);
        if (isNaN(idx) || !presets[idx]) return;

        var sql = presets[idx].query || '';
        var spec = parsePresetSqlToSpec(sql);
        if (!spec) {
            showError('Could not parse selected preset.');
            return;
        }

        applyQuerySpecToBuilder(spec);
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
                refreshBasketSummary();
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
        resultColumns = Array.isArray(columns) ? columns.slice() : [];
        selectedRowIdxs.clear();
        visibleAddableIdxs = [];

        if (!rows.length) {
            el('qdb-idle').innerHTML =
                '<i class="fa-solid fa-inbox qdb-idle__icon"></i>' +
                '<p>No rows returned.</p>';
            show('qdb-idle');
            hide('qdb-table-wrap');
            hide('qdb-scroll-top');
            hide('qdb-pagination');
            show('qdb-results-meta');
            el('qdb-results-count').textContent = '0 rows';
            el('qdb-results-time').textContent = 'in ' + elapsed + 's';
            hide('qdb-export-csv');
            updateBasketActionState();
            return;
        }

        // Build header
        var hdr = el('qdb-header-row');
        hdr.innerHTML = '';

        var thSel = makeEl('th', 'ot-th qdb-th-check');
        var cbAll = document.createElement('input');
        cbAll.type = 'checkbox';
        cbAll.id = 'qdb-select-all';
        cbAll.title = 'Select all visible rows';
        cbAll.addEventListener('change', function () {
            var checked = !!this.checked;
            visibleAddableIdxs.forEach(function (idx) {
                if (checked) selectedRowIdxs.add(idx);
                else selectedRowIdxs.delete(idx);
            });
            renderPage(resultColumns, resultRows);
            updateBasketActionState();
        });
        thSel.appendChild(cbAll);
        hdr.appendChild(thSel);

        columns.forEach(function (col) {
            var th = makeEl('th', 'ot-th');
            th.textContent = formatColHeader(col, columns);
            th.title = col;
            th.dataset.colKey = col;
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
        show('qdb-scroll-top');
        show('qdb-table-wrap');
        show('qdb-pagination');
        syncScrollMirror();
        updateBasketActionState();
    }

    function rowValueBySuffix(row, wanted) {
        var want = String(wanted || '').toUpperCase();
        if (!want || !row || typeof row !== 'object') return '';
        var keys = Object.keys(row);
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            var up = String(key).toUpperCase();
            if (up === want || up.endsWith('__' + want)) {
                var val = row[key];
                return val !== null && val !== undefined ? val : '';
            }
        }
        return '';
    }

    function buildBasketEntryFromRow(row) {
        var blockKind = String(rowValueBySuffix(row, 'BLOCK_KIND') || '').trim();
        var obsDir = String(rowValueBySuffix(row, 'OBS_DIR') || '').trim();
        var filename = String(rowValueBySuffix(row, 'FILENAME') || '').trim();
        var runId = String(rowValueBySuffix(row, 'KW_RUN_ID') || '').trim();

        if (!blockKind || !obsDir || !filename || !runId) return null;

        return {
            profile_id: profileId,
            instrument: '',
            objname: String(rowValueBySuffix(row, 'KW_OBJNAME')
                || rowValueBySuffix(row, 'OBJNAME') || '').trim(),
            block_kind: blockKind,
            obs_dir: obsDir,
            filename: filename,
            kw_output: String(rowValueBySuffix(row, 'KW_OUTPUT') || '').trim(),
            kw_run_id: runId,
            kw_dprtype: String(rowValueBySuffix(row, 'KW_DPRTYPE') || '').trim(),
            kw_fiber: String(rowValueBySuffix(row, 'KW_FIBER') || '').trim(),
            kw_pi_name: String(rowValueBySuffix(row, 'KW_PI_NAME') || '').trim(),
            mid_obs_time: String(rowValueBySuffix(row, 'MID_OBS_TIME') || '').trim(),
            passed_all_qc: rowValueBySuffix(row, 'PASSED_ALL_QC'),
            identifier: String(rowValueBySuffix(row, 'IDENTIFIER') || '').trim(),
        };
    }

    function canAddRowToBasket(row) {
        return !!buildBasketEntryFromRow(row);
    }

    function renderPage(columns, rows) {
        var tbody = el('qdb-tbody');
        tbody.innerHTML = '';
        visibleAddableIdxs = [];

        var total = rows.length;
        var totalPages = Math.ceil(total / rowsPerPage);
        if (totalPages < 1) totalPages = 1;
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        var start = (currentPage - 1) * rowsPerPage;
        var end = Math.min(start + rowsPerPage, total);
        var pageRows = rows.slice(start, end);

        pageRows.forEach(function (row, idx) {
            var globalIdx = start + idx;
            var tr = document.createElement('tr');
            tr.className = 'qdb-row ' + ((start + idx) % 2 === 0 ? 'qdb-row--odd' : 'qdb-row--even');

            var tdSel = makeEl('td', 'ot-td bk-cell-check');
            var cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.className = 'qdb-row-check';
            cb.dataset.idx = String(globalIdx);
            cb.checked = selectedRowIdxs.has(globalIdx);
            var addable = canAddRowToBasket(row);
            if (!addable) {
                cb.disabled = true;
                cb.title = 'Requires BLOCK_KIND, OBS_DIR, FILENAME, and KW_RUN_ID in query result.';
            } else {
                visibleAddableIdxs.push(globalIdx);
            }
            cb.addEventListener('change', function () {
                if (cb.checked) selectedRowIdxs.add(globalIdx);
                else selectedRowIdxs.delete(globalIdx);
                updateBasketActionState();
                updateSelectAllCheckbox();
            });
            tdSel.appendChild(cb);
            tr.appendChild(tdSel);

            columns.forEach(function (col) {
                var td = makeEl('td', 'ot-td');
                var val = row[col];
                td.textContent = val !== null && val !== undefined ? String(val) : '';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        updateSelectAllCheckbox();
        updateBasketActionState();

        // Update pagination controls
        el('qdb-page-input').value = currentPage;
        el('qdb-page-total').textContent = totalPages;
        el('qdb-page-info').textContent =
            'Rows ' + (start + 1) + '–' + end + ' of ' + total;

        el('qdb-btn-first').disabled = currentPage <= 1;
        el('qdb-btn-prev').disabled = currentPage <= 1;
        el('qdb-btn-next').disabled = currentPage >= totalPages;
        el('qdb-btn-last').disabled = currentPage >= totalPages;

        syncScrollMirror();
    }

    function updateSelectAllCheckbox() {
        var cbAll = el('qdb-select-all');
        if (!cbAll) return;
        if (!visibleAddableIdxs.length) {
            cbAll.checked = false;
            cbAll.indeterminate = false;
            cbAll.disabled = true;
            return;
        }
        cbAll.disabled = false;
        var selectedVisible = visibleAddableIdxs.filter(function (idx) {
            return selectedRowIdxs.has(idx);
        }).length;
        cbAll.checked = selectedVisible === visibleAddableIdxs.length;
        cbAll.indeterminate = selectedVisible > 0 && selectedVisible < visibleAddableIdxs.length;
    }

    function updateBasketActionState() {
        var selectedCount = selectedRowIdxs.size;
        var btnSelected = el('qdb-btn-add-selected');
        var btnVisible = el('qdb-btn-add-visible');
        var btnClear = el('qdb-btn-clear-selection');

        if (btnSelected) {
            btnSelected.disabled = selectedCount === 0;
            btnSelected.innerHTML = '<i class="fa-solid fa-basket-shopping"></i> Add to basket'
                + (selectedCount ? ' (' + selectedCount + ')' : '');
        }
        if (btnVisible) {
            btnVisible.disabled = visibleAddableIdxs.length === 0;
            btnVisible.innerHTML = '<i class="fa-solid fa-layer-group"></i> Add all visible'
                + (visibleAddableIdxs.length ? ' (' + visibleAddableIdxs.length + ')' : '');
        }
        if (btnClear) {
            btnClear.disabled = selectedCount === 0;
        }
    }

    function refreshBasketSummary() {
        fetch(basketSummaryApiUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) return;
                var countEl = el('qdb-basket-count');
                var sizeEl = el('qdb-basket-size');
                var n = Number(data.accessible_files || 0);
                if (countEl) {
                    countEl.textContent = n + ' file' + (n !== 1 ? 's' : '');
                }
                if (sizeEl) {
                    sizeEl.textContent = 'Total size: ' + formatBytes(data.total_size_bytes || 0);
                }
            })
            .catch(function () {});
    }

    function addRowsToBasketByIndices(indices) {
        if (!indices || !indices.length) return;

        var seen = new Set();
        var entries = [];
        var skippedMissing = 0;

        indices.forEach(function (idx) {
            var i = Number(idx);
            if (!isFinite(i) || i < 0 || i >= resultRows.length || seen.has(i)) return;
            seen.add(i);
            var entry = buildBasketEntryFromRow(resultRows[i]);
            if (!entry) {
                skippedMissing++;
                return;
            }
            entries.push(entry);
        });

        if (!entries.length) {
            alert('No selectable rows found. Include BLOCK_KIND, OBS_DIR, FILENAME, and KW_RUN_ID in your query output.');
            return;
        }

        fetch(basketAddApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ entries: entries }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    alert('Failed to add rows to basket: ' + ((data && data.error) || 'unknown'));
                    return;
                }
                refreshBasketSummary();
                var msg = (data.added || 0) + ' file(s) added to basket';
                var skipped = Number(data.skipped || 0) + skippedMissing;
                if (skipped > 0) msg += ' (' + skipped + ' skipped)';
                alert(msg + '.');
            })
            .catch(function (err) {
                alert('Request failed: ' + String(err));
            });
    }

    function syncScrollMirror() {
        var scrollTopEl = el('qdb-scroll-top');
        var scrollSizer = el('qdb-scroll-sizer');
        var tableWrap = el('qdb-table-wrap');
        var tableEl = el('qdb-table');
        if (!scrollTopEl || !scrollSizer || !tableWrap || !tableEl) return;

        var scrollWidth = tableEl.scrollWidth || 0;
        var clientWidth = tableWrap.clientWidth || 0;
        scrollSizer.style.width = scrollWidth + 'px';

        if (scrollWidth > clientWidth + 1) {
            show(scrollTopEl);
            scrollTopEl.scrollLeft = tableWrap.scrollLeft;
        } else {
            hide(scrollTopEl);
            scrollTopEl.scrollLeft = 0;
        }
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
        var scrollTopEl = el('qdb-scroll-top');
        var tableWrap = el('qdb-table-wrap');

        if (scrollTopEl && tableWrap) {
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
        }

        // Run query
        var runBtn = el('qdb-run-btn');
        if (runBtn) runBtn.addEventListener('click', runQuery);

        var addSelectedBtn = el('qdb-btn-add-selected');
        if (addSelectedBtn) {
            addSelectedBtn.addEventListener('click', function () {
                addRowsToBasketByIndices(Array.from(selectedRowIdxs));
            });
        }

        var addVisibleBtn = el('qdb-btn-add-visible');
        if (addVisibleBtn) {
            addVisibleBtn.addEventListener('click', function () {
                if (!visibleAddableIdxs.length) return;
                if (!confirm('Add ' + visibleAddableIdxs.length + ' visible row(s) to basket?')) return;
                addRowsToBasketByIndices(visibleAddableIdxs.slice());
            });
        }

        var clearSelBtn = el('qdb-btn-clear-selection');
        if (clearSelBtn) {
            clearSelBtn.addEventListener('click', function () {
                selectedRowIdxs.clear();
                renderPage(resultColumns, resultRows);
                updateBasketActionState();
            });
        }

        // Add join
        var addJoinBtn = el('qdb-add-join');
        if (addJoinBtn) {
            addJoinBtn.addEventListener('click', function (ev) {
                ev.preventDefault();
                ev.stopPropagation();
                var tables = availableTableLabels();
                if (tables.length < 2) return;
                var joinsSection = el('qdb-joins-section');
                if (joinsSection && joinsSection.tagName === 'DETAILS') {
                    joinsSection.open = true;
                }
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
            addFilterBtn.addEventListener('click', function (ev) {
                ev.preventDefault();
                ev.stopPropagation();
                var labels = availableTableLabels();
                if (!labels.length) return;
                var filtersSection = el('qdb-filters-section');
                if (filtersSection && filtersSection.tagName === 'DETAILS') {
                    filtersSection.open = true;
                }
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

        // Apply preset
        var applyPresetBtn = el('qdb-apply-preset');
        if (applyPresetBtn) {
            applyPresetBtn.addEventListener('click', function () {
                applySelectedPreset();
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
        return resultColumns.slice();
    }

    /* ------------------------------------------------------------------ */
    /* Init                                                                 */
    /* ------------------------------------------------------------------ */
    function init() {
        wireEvents();
        window.addEventListener('resize', syncScrollMirror);
        refreshBasketSummary();
        updateBasketActionState();
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
