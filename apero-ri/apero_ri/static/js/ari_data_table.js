/* ari_data_table.js
 * Lightweight sortable + filterable HTML table component.
 *
 * Usage:
 *   var table = AriDataTable.create({
 *       table:           HTMLTableElement,        // required
 *       columns:         [ { key, label, render?, sort?, filter?,
 *                            type?, dropdownThreshold? }, ... ],
 *       rows:            Array<object>,
 *       dropdownThreshold: 10,                    // global default
 *       emptyMsg:        'No matching rows.',
 *   });
 *   table.setRows(newRows);   // re-render with new data
 *
 * Per-column options:
 *   key:    string (required) - data key in row
 *   label:  string            - header text (default: key)
 *   render: (val, row) => HTMLElement|string|null (custom cell)
 *   sort:   (a, b) => number  (custom comparator over row objects)
 *   filter: 'text' | 'dropdown' | 'auto'  (default 'auto')
 *   type:   'text'|'number'|'int'|'float'|'date'|'datetime'
 *   dropdownThreshold: int    (override component default)
 */
(function () {
    'use strict';

    function _esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function _strict_number(v) {
        if (v === null || v === undefined || v === '') return null;
        var n = Number(v);
        return isFinite(n) ? n : null;
    }

    function _is_blank(v) {
        return v === null || v === undefined
            || String(v).trim() === '';
    }

    function _auto_use_dropdown(col, rows) {
        var type = String(col.type || '').toLowerCase();
        if (type === 'number' || type === 'int' || type === 'float'
            || type === 'date' || type === 'datetime') {
            return false;
        }
        var nonBlank = [];
        for (var i = 0; i < rows.length; i++) {
            var v = rows[i][col.key];
            if (!_is_blank(v)) nonBlank.push(v);
        }
        if (!nonBlank.length) return true;
        var allNumeric = true;
        for (var j = 0; j < nonBlank.length; j++) {
            if (_strict_number(nonBlank[j]) === null) {
                allNumeric = false;
                break;
            }
        }
        if (allNumeric) return false;
        return true;
    }

    function _default_compare(col, a, b) {
        var va = a[col.key];
        var vb = b[col.key];
        var na = _strict_number(va);
        var nb = _strict_number(vb);
        if (na !== null && nb !== null) {
            if (na < nb) return -1;
            if (na > nb) return 1;
            return 0;
        }
        var sa = va == null ? '' : String(va).toLowerCase();
        var sb = vb == null ? '' : String(vb).toLowerCase();
        if (sa < sb) return -1;
        if (sa > sb) return 1;
        return 0;
    }

    function create(opts) {
        if (!opts || !opts.table) {
            throw new Error('AriDataTable: table is required');
        }
        var table = opts.table;
        var columns = (opts.columns || []).slice();
        var allRows = (opts.rows || []).slice();
        var dropdownThreshold = (typeof opts.dropdownThreshold
            === 'number') ? opts.dropdownThreshold : 10;
        var emptyMsg = opts.emptyMsg || 'No matching rows.';

        // Internal state
        var sortKey = null;
        var sortDir = 1;
        var colFilters = {};

        // Build skeleton
        table.classList.add('ari-dt');
        var thead = table.tHead || table.createTHead();
        thead.innerHTML = '';
        var headerRow = thead.insertRow();
        headerRow.className = 'ari-dt__header-row';
        var filterRow = thead.insertRow();
        filterRow.className = 'ari-dt__filter-row';
        var tbody = table.tBodies[0];
        if (!tbody) {
            tbody = document.createElement('tbody');
            table.appendChild(tbody);
        }

        function _render_header() {
            headerRow.innerHTML = '';
            filterRow.innerHTML = '';
            columns.forEach(function (col) {
                var th = document.createElement('th');
                th.className = 'ari-dt__th';
                th.dataset.col = col.key;
                var label = col.label || col.key;
                var arrow = '';
                if (sortKey === col.key) {
                    arrow = sortDir === 1
                        ? ' <i class="fa-solid fa-caret-up"></i>'
                        : ' <i class="fa-solid fa-caret-down"></i>';
                }
                th.innerHTML = '<span class="ari-dt__th-label">'
                    + _esc(label) + '</span>' + arrow;
                th.title = 'Click to sort by ' + label;
                th.addEventListener('click', function () {
                    if (sortKey === col.key) {
                        sortDir = -sortDir;
                    } else {
                        sortKey = col.key;
                        sortDir = 1;
                    }
                    _render_header();
                    _render_body();
                });
                headerRow.appendChild(th);

                var ftd = document.createElement('th');
                ftd.className = 'ari-dt__filter-cell';
                ftd.dataset.col = col.key;
                _build_filter_widget(col, ftd);
                filterRow.appendChild(ftd);
            });
        }

        function _build_filter_widget(col, ftd) {
            var mode = col.filter || 'auto';
            var thr = (typeof col.dropdownThreshold === 'number')
                ? col.dropdownThreshold : dropdownThreshold;
            var uniq = [];
            var seen = {};
            for (var i = 0; i < allRows.length; i++) {
                var v = allRows[i][col.key];
                var s = v == null ? '' : String(v);
                if (!Object.prototype.hasOwnProperty.call(seen, s)) {
                    seen[s] = 1;
                    uniq.push(s);
                }
            }
            uniq.sort();
            var useDropdown = false;
            if (mode === 'dropdown') {
                useDropdown = true;
            } else if (mode === 'text') {
                useDropdown = false;
            } else if (allRows.length > 0
                       && uniq.length <= thr
                       && _auto_use_dropdown(col, allRows)) {
                useDropdown = true;
            }
            var current = colFilters[col.key] || '';
            if (useDropdown) {
                var sel = document.createElement('select');
                sel.className = 'ari-dt__filter-select';
                sel.dataset.col = col.key;
                sel.title = 'Filter ' + (col.label || col.key);
                var optAll = document.createElement('option');
                optAll.value = '';
                optAll.textContent = '(all)';
                sel.appendChild(optAll);
                uniq.forEach(function (u) {
                    var o = document.createElement('option');
                    o.value = u;
                    o.textContent = u === '' ? '(blank)' : u;
                    if (u === current) o.selected = true;
                    sel.appendChild(o);
                });
                sel.addEventListener('change', function () {
                    colFilters[col.key] = sel.value;
                    _render_body();
                });
                ftd.appendChild(sel);
            } else {
                var inp = document.createElement('input');
                inp.type = 'text';
                inp.className = 'ari-dt__filter-input';
                inp.placeholder = '\u2315';
                inp.dataset.col = col.key;
                inp.value = current;
                inp.title = 'Filter ' + (col.label || col.key);
                var t = null;
                inp.addEventListener('input', function () {
                    if (t) clearTimeout(t);
                    t = setTimeout(function () {
                        colFilters[col.key] = inp.value;
                        _render_body();
                    }, 120);
                });
                ftd.appendChild(inp);
            }
        }

        function _row_matches(row) {
            for (var i = 0; i < columns.length; i++) {
                var col = columns[i];
                var f = colFilters[col.key];
                if (!f) continue;
                var raw = row[col.key];
                var s = raw == null ? '' : String(raw);
                // Dropdown filters use exact match
                var mode = col.filter || 'auto';
                var widget = filterRow.querySelector(
                    'select[data-col="' + CSS.escape(col.key) + '"]'
                );
                if (widget || mode === 'dropdown') {
                    if (s !== f) return false;
                } else {
                    if (s.toLowerCase().indexOf(
                            String(f).toLowerCase()) === -1) {
                        return false;
                    }
                }
            }
            return true;
        }

        function _filtered_sorted() {
            var out = [];
            for (var i = 0; i < allRows.length; i++) {
                if (_row_matches(allRows[i])) out.push(allRows[i]);
            }
            if (sortKey) {
                var col = null;
                for (var j = 0; j < columns.length; j++) {
                    if (columns[j].key === sortKey) {
                        col = columns[j];
                        break;
                    }
                }
                if (col) {
                    var cmp = col.sort
                        || function (a, b) {
                            return _default_compare(col, a, b);
                        };
                    out.sort(function (a, b) {
                        return sortDir * cmp(a, b);
                    });
                }
            }
            return out;
        }

        function _render_body() {
            var rows = _filtered_sorted();
            tbody.innerHTML = '';
            if (!rows.length) {
                var tr = tbody.insertRow();
                var td = tr.insertCell();
                td.colSpan = columns.length;
                td.className = 'ari-dt__empty';
                td.textContent = emptyMsg;
                _emit_render(rows);
                return;
            }
            rows.forEach(function (row) {
                var tr = tbody.insertRow();
                tr.className = 'ari-dt__row';
                if (typeof opts.rowClass === 'function') {
                    var rc = opts.rowClass(row);
                    if (rc) tr.classList.add(rc);
                }
                columns.forEach(function (col) {
                    var td = tr.insertCell();
                    td.dataset.col = col.key;
                    var val = row[col.key];
                    if (typeof col.render === 'function') {
                        var out = col.render(val, row);
                        if (out instanceof Node) {
                            td.appendChild(out);
                        } else if (out == null) {
                            td.innerHTML = '';
                        } else {
                            td.innerHTML = String(out);
                        }
                    } else {
                        td.textContent = (val == null) ? '' : val;
                    }
                });
            });
            _emit_render(rows);
        }

        function _emit_render(rows) {
            if (typeof opts.onRender === 'function') {
                try {
                    opts.onRender(rows, allRows);
                } catch (err) { /* noop */ }
            }
        }

        function setRows(newRows) {
            allRows = (newRows || []).slice();
            _render_header();
            _render_body();
        }

        function getRows() {
            return allRows.slice();
        }

        _render_header();
        _render_body();

        return {
            setRows: setRows,
            getRows: getRows,
            refresh: _render_body,
            element: table,
        };
    }

    window.AriDataTable = { create: create };
}());
