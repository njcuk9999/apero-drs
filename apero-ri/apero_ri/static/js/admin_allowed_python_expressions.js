(function () {
    'use strict';

    var cfg = window.ARI_ALLOWED_EXPR || {};
    var tableBody = document.getElementById('ape-rows');
    var addBtn = document.getElementById('ape-add-row');
    var saveBtn = document.getElementById('ape-save');
    var statusEl = document.getElementById('ape-status');

    var state = {
        rows: [],
    };

    function esc(text) {
        var d = document.createElement('div');
        d.textContent = String(text || '');
        return d.innerHTML;
    }

    function setStatus(text, isError) {
        if (!statusEl) return;
        statusEl.textContent = String(text || '');
        statusEl.style.color = isError ? '#a54528' : '#4f613b';
    }

    function normalisedRows() {
        return state.rows
            .map(function (row) {
                return {
                    expression: String(row.expression || '').trim(),
                    comment: String(row.comment || '').trim(),
                };
            })
            .filter(function (row) {
                return !!row.expression;
            });
    }

    function renderRows() {
        if (!tableBody) return;
        if (!state.rows.length) {
            tableBody.innerHTML = '<tr><td colspan="3"'
                + ' class="at-muted-hint">No rules yet.</td></tr>';
            return;
        }

        tableBody.innerHTML = '';
        state.rows.forEach(function (row, index) {
            var tr = document.createElement('tr');
            tr.innerHTML = '<td><input type="text" class="ari-input"'
                + ' data-field="expression" data-index="'
                + String(index)
                + '" value="'
                + esc(row.expression)
                + '" placeholder="e.g. Time = astropy.time.Time"></td>'
                + '<td><input type="text" class="ari-input"'
                + ' data-field="comment" data-index="'
                + String(index)
                + '" value="'
                + esc(row.comment)
                + '" placeholder="Comment"></td>'
                + '<td><button type="button" class="ari-btn ari-btn--danger"'
                + ' data-action="remove" data-index="'
                + String(index)
                + '" title="Remove rule">'
                + '<i class="fa-solid fa-trash"></i></button></td>';
            tableBody.appendChild(tr);
        });

        tableBody.querySelectorAll('input[data-field]').forEach(function (el) {
            el.addEventListener('input', function () {
                var idx = Number(el.dataset.index || -1);
                var field = String(el.dataset.field || '');
                if (idx < 0 || idx >= state.rows.length) return;
                state.rows[idx][field] = el.value;
            });
        });

        tableBody.querySelectorAll('button[data-action="remove"]')
            .forEach(function (btn) {
                btn.addEventListener('click', function () {
                    var idx = Number(btn.dataset.index || -1);
                    if (idx < 0 || idx >= state.rows.length) return;
                    state.rows.splice(idx, 1);
                    renderRows();
                });
            });
    }

    function getJson(url) {
        return fetch(url).then(function (r) {
            return r.json();
        });
    }

    function postJson(url, body) {
        return fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body),
        }).then(function (r) {
            return r.json();
        });
    }

    function loadRows() {
        if (!cfg.apiUrl) return;
        setStatus('Loading rules...', false);
        getJson(cfg.apiUrl).then(function (data) {
            if (!data.success) {
                setStatus(data.error || 'Failed to load rules.', true);
                return;
            }
            state.rows = Array.isArray(data.rows) ? data.rows : [];
            renderRows();
            if (Array.isArray(data.warnings) && data.warnings.length) {
                setStatus('Loaded with warnings: ' + data.warnings.join(' | '), true);
                return;
            }
            setStatus('Loaded ' + String(state.rows.length) + ' rules.', false);
        }).catch(function () {
            setStatus('Network error while loading rules.', true);
        });
    }

    function saveRows() {
        if (!cfg.apiUrl) return;
        var rows = normalisedRows();
        if (!rows.length) {
            setStatus('Please provide at least one expression rule.', true);
            return;
        }
        setStatus('Saving rules...', false);
        postJson(cfg.apiUrl, {rows: rows}).then(function (data) {
            if (!data.success) {
                setStatus(data.error || 'Save failed.', true);
                return;
            }
            state.rows = Array.isArray(data.rows) ? data.rows : rows;
            renderRows();
            if (Array.isArray(data.warnings) && data.warnings.length) {
                setStatus('Saved with warnings: ' + data.warnings.join(' | '), true);
                return;
            }
            setStatus('Saved successfully.', false);
        }).catch(function () {
            setStatus('Network error while saving rules.', true);
        });
    }

    if (addBtn) {
        addBtn.addEventListener('click', function () {
            state.rows.push({expression: '', comment: ''});
            renderRows();
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', saveRows);
    }

    loadRows();
}());
