(function () {
    'use strict';

    var cfg = window.AperoRejectionList || {};
    var tabs = Array.isArray(cfg.tabs) ? cfg.tabs : [];
    var canManageHistory = !!cfg.canManageHistory;
    if (!tabs.length) return;

    var state = {
        tab: tabs[0].key,
        page: 1,
        perPage: 50,
        sort: 'identifier_asc',
        q: '',
        filters: {
            pp: '',
            tel: '',
            rv: '',
            used: ''
        },
        total: 0,
        pages: 0,
        historyPage: 1,
        historyPages: 0,
        historyPerPage: 50,
        historyQ: ''
    };
    var filterTimer = null;
    var historyTimer = null;

    function esc(value) {
        return String(value == null ? '' : value).replace(
            /[<>&"']/g,
            function (char) {
                return ({
                    '<': '&lt;',
                    '>': '&gt;',
                    '&': '&amp;',
                    '"': '&quot;',
                    "'": '&#39;'
                })[char];
            }
        );
    }

    function fmtTime(value) {
        return String(value || '').replace('T', ' ');
    }

    function prettyAction(value) {
        var action = String(value || '').trim().toLowerCase();
        if (!action) return 'Update';
        return action.charAt(0).toUpperCase() + action.slice(1);
    }

    function diffChipHtml(value, mode) {
        var text = String(value || '');
        var cls = 'rj-diff-chip rj-diff-chip--neutral';
        if (mode === 'add') cls = 'rj-diff-chip rj-diff-chip--add';
        if (mode === 'remove') cls = 'rj-diff-chip rj-diff-chip--remove';
        if (!text) {
            text = '(empty)';
        }
        return '<span class="' + cls + '">'
            + esc(text).replace(/\n/g, '<br>') + '</span>';
    }

    function renderDiffCard(key, previous, next) {
        var prevHtml = diffChipHtml(previous, 'neutral');
        var nextHtml = diffChipHtml(next, 'neutral');
        if (!previous && next) {
            nextHtml = diffChipHtml(next, 'add');
        } else if (previous && !next) {
            prevHtml = diffChipHtml(previous, 'remove');
        }
        return '<div class="rj-diff-card">'
            + '<h4 class="rj-diff-card__title">' + esc(key) + '</h4>'
            + '<div class="rj-diff-card__row">'
            + '<span class="rj-diff-card__label">Was</span>'
            + prevHtml + '</div>'
            + '<div class="rj-diff-card__row">'
            + '<span class="rj-diff-card__label">Now</span>'
            + nextHtml + '</div></div>';
    }

    function setStatus(id, html) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = html || '';
    }

    function showOverlay(id, show) {
        var el = document.getElementById(id);
        if (el) el.hidden = !show;
    }

    function setMainView(mode) {
        var listCard = document.getElementById('rj-list-card');
        var histCard = document.getElementById('rj-history-card');
        var showHistory = mode === 'history';
        if (listCard) {
            listCard.hidden = showHistory;
            listCard.style.display = showHistory ? 'none' : '';
        }
        if (histCard) {
            histCard.hidden = !showHistory;
            histCard.style.display = showHistory ? '' : 'none';
        }
    }

    function updateTabButtons(active) {
        document.querySelectorAll('[data-rj-tab]').forEach(function (btn) {
            btn.classList.toggle(
                'rj-htab--active',
                btn.getAttribute('data-rj-tab') === active
            );
        });
    }

    function currentTabLabel() {
        for (var i = 0; i < tabs.length; i += 1) {
            if (tabs[i].key === state.tab) return tabs[i].label;
        }
        return state.tab.toUpperCase();
    }

    function flagHtml(name, value) {
        var on = Number(value || 0) === 1;
        return '<span class="rj-flag' + (on ? ' rj-flag--on' : '') + '">'
            + '<strong>' + esc(name) + '</strong> '
            + esc(on ? '1' : '0') + '</span>';
    }

    function renderRows(rows) {
        var host = document.getElementById('rj-list');
        var count = document.getElementById('rj-count');
        var info = document.getElementById('rj-page-info');
        var prev = document.getElementById('rj-prev');
        var next = document.getElementById('rj-next');
        if (count) {
            count.textContent = state.total
                ? state.total + ' entries in ' + currentTabLabel()
                : '0 entries';
        }
        if (info) {
            info.textContent = state.pages
                ? state.page + ' of ' + state.pages
                : '0 of 0';
        }
        if (prev) prev.disabled = state.page <= 1;
        if (next) next.disabled = state.page >= state.pages;
        if (!host) return;
        host.innerHTML = '';

        var addCard = document.createElement('button');
        addCard.type = 'button';
        addCard.className = 'rj-card rj-card--add';
        addCard.innerHTML = '<div><i class="fa-solid fa-plus"></i> '
            + 'Add rejection entry</div>';
        addCard.addEventListener('click', function () {
            openEditOverlay(null);
        });
        host.appendChild(addCard);

        if (!rows.length) {
            var empty = document.createElement('div');
            empty.className = 'rj-empty';
            empty.textContent = 'No entries match this filter.';
            host.appendChild(empty);
            return;
        }

        rows.forEach(function (row) {
            var card = document.createElement('div');
            card.className = 'rj-card';
            card.innerHTML = ''
                + '<div class="rj-card__name">'
                + '<i class="fa-solid fa-ban"></i>'
                + '<span>' + esc(row.IDENTIFIER) + '</span>'
                + '</div>'
                + '<div class="rj-card__flags-col">'
                + '<div class="rj-card__flags">'
                + flagHtml('PP', row.PP)
                + flagHtml('TEL', row.TEL)
                + flagHtml('RV', row.RV)
                + flagHtml('USED', row.USED)
                + '</div></div>'
                + '<div class="rj-card__comment" title="'
                + esc(row.COMMENT || '') + '">' + esc(row.COMMENT || '—')
                + '</div>'
                + '<div class="rj-card__actions">'
                + '<button type="button" class="rj-btn-icon" '
                + 'data-action="edit" title="Edit entry">'
                + '<i class="fa-solid fa-pen"></i></button>'
                + '<button type="button" '
                + 'class="rj-btn-icon rj-btn-icon--danger" '
                + 'data-action="delete" title="Delete entry">'
                + '<i class="fa-solid fa-trash"></i></button>'
                + '</div>';
            card.querySelector('[data-action="edit"]').addEventListener(
                'click',
                function () {
                    openEditOverlay(row);
                }
            );
            card.querySelector('[data-action="delete"]').addEventListener(
                'click',
                function () {
                    deleteRow(row);
                }
            );
            host.appendChild(card);
        });
    }

    function loadRows() {
        setMainView('list');
        setStatus('rj-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Loading...');
        var params = new URLSearchParams();
        params.set('instrument', state.tab);
        params.set('page', state.page);
        params.set('per_page', state.perPage);
        params.set('sort', state.sort);
        if (state.q) params.set('q', state.q);
        Object.keys(state.filters).forEach(function (key) {
            if (state.filters[key] !== '') {
                params.set(key, state.filters[key]);
            }
        });
        fetch('/api/rejection-list/list?' + params.toString(), {
            credentials: 'same-origin'
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, body: body };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                setStatus('rj-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown'));
                return;
            }
            state.total = res.body.total || 0;
            state.pages = res.body.pages || 0;
            state.page = res.body.page || 1;
            setStatus('rj-status', '');
            renderRows(res.body.rows || []);
        }).catch(function (err) {
            setStatus('rj-status', 'Failed: ' + esc(err));
        });
    }

    function openEditOverlay(row) {
        document.getElementById('rj-edit-mode').value = row ? 'edit' : 'add';
        document.getElementById('rj-edit-original').value = row
            ? String(row.IDENTIFIER || '') : '';
        document.getElementById('rj-edit-title').textContent = row
            ? 'Edit rejection entry'
            : 'Add rejection entry';
        document.getElementById('rj-identifier').value = row
            ? String(row.IDENTIFIER || '') : '';
        document.getElementById('rj-pp').value = String(row ? row.PP : 1);
        document.getElementById('rj-tel').value = String(row ? row.TEL : 1);
        document.getElementById('rj-rv').value = String(row ? row.RV : 1);
        document.getElementById('rj-used').value = String(row ? row.USED : 1);
        document.getElementById('rj-comment').value = row
            ? String(row.COMMENT || '') : '';
        setStatus('rj-edit-status', '');
        showOverlay('rj-edit-overlay', true);
        document.getElementById('rj-identifier').focus();
    }

    function collectEditPayload() {
        var payload = {
            instrument: state.tab,
            identifier: document.getElementById('rj-identifier').value.trim(),
            IDENTIFIER: document.getElementById('rj-identifier').value.trim(),
            PP: document.getElementById('rj-pp').value,
            TEL: document.getElementById('rj-tel').value,
            RV: document.getElementById('rj-rv').value,
            USED: document.getElementById('rj-used').value,
            COMMENT: document.getElementById('rj-comment').value.trim()
        };
        return payload;
    }

    function saveRow(forceReplace) {
        var mode = document.getElementById('rj-edit-mode').value;
        var payload = collectEditPayload();
        if (!payload.IDENTIFIER) {
            setStatus('rj-edit-status', 'Identifier is required.');
            return;
        }
        if (mode === 'edit') {
            payload.old_identifier =
                document.getElementById('rj-edit-original').value;
        }
        if (forceReplace) payload.replace_existing = true;
        var url = mode === 'edit'
            ? '/api/rejection-list/update'
            : '/api/rejection-list/add';
        setStatus('rj-edit-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Saving...');
        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, status: resp.status, body: body };
            });
        }).then(function (res) {
            if (res.status === 409 && res.body
                    && res.body.requires_confirmation) {
                var question = 'Identifier already exists in '
                    + currentTabLabel() + '. Replace it?';
                if (window.confirm(question)) {
                    saveRow(true);
                } else {
                    setStatus('rj-edit-status', 'Replacement cancelled.');
                }
                return;
            }
            if (!res.body || !res.body.success) {
                setStatus('rj-edit-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown'));
                return;
            }
            showOverlay('rj-edit-overlay', false);
            loadRows();
        }).catch(function (err) {
            setStatus('rj-edit-status', 'Failed: ' + esc(err));
        });
    }

    function deleteRow(row) {
        if (!window.confirm('Delete ' + row.IDENTIFIER + ' from '
                + currentTabLabel() + '?')) {
            return;
        }
        setStatus('rj-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Deleting...');
        fetch('/api/rejection-list/delete', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: state.tab,
                identifier: row.IDENTIFIER
            })
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, body: body };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                setStatus('rj-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown'));
                return;
            }
            loadRows();
        }).catch(function (err) {
            setStatus('rj-status', 'Failed: ' + esc(err));
        });
    }

    function submitUpload(forceReplace) {
        var fileEl = document.getElementById('rj-upload-file');
        if (!fileEl.files || !fileEl.files[0]) {
            setStatus('rj-upload-status', 'Select a CSV file first.');
            return;
        }
        var fd = new FormData();
        fd.append('instrument', state.tab);
        fd.append('file', fileEl.files[0]);
        if (forceReplace) fd.append('replace_existing', '1');
        setStatus('rj-upload-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...');
        fetch('/api/rejection-list/upload', {
            method: 'POST',
            credentials: 'same-origin',
            body: fd
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, status: resp.status, body: body };
            });
        }).then(function (res) {
            if (res.status === 409 && res.body
                    && res.body.requires_confirmation) {
                var msg = 'Upload has ' + (res.body.conflict_count || 0)
                    + ' existing identifiers in ' + currentTabLabel()
                    + '. Replace all of them?';
                if (window.confirm(msg)) {
                    submitUpload(true);
                } else {
                    setStatus('rj-upload-status', 'Upload cancelled.');
                }
                return;
            }
            if (!res.body || !res.body.success) {
                var details = '';
                if (res.body && Array.isArray(res.body.details)) {
                    details = ' ' + res.body.details.join(' | ');
                }
                setStatus('rj-upload-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown')
                    + esc(details));
                return;
            }
            setStatus('rj-upload-status', '');
            showOverlay('rj-upload-overlay', false);
            fileEl.value = '';
            loadRows();
        }).catch(function (err) {
            setStatus('rj-upload-status', 'Failed: ' + esc(err));
        });
    }

    function renderHistory(rows) {
        var host = document.getElementById('rj-history-list');
        var info = document.getElementById('rj-history-page');
        var prev = document.getElementById('rj-history-prev');
        var next = document.getElementById('rj-history-next');
        if (info) {
            info.textContent = state.historyPages
                ? state.historyPage + ' of ' + state.historyPages
                : '0 of 0';
        }
        if (prev) prev.disabled = state.historyPage <= 1;
        if (next) next.disabled = state.historyPage >= state.historyPages;
        if (!host) return;
        host.innerHTML = '';
        if (!rows.length) {
            host.innerHTML = '<div class="rj-empty">'
                + 'No history entries match this filter.</div>';
            return;
        }
        rows.forEach(function (row) {
            var card = document.createElement('div');
            var fieldHtml = (row.fields || []).map(function (field) {
                return '<span>' + esc(field) + '</span>';
            }).join('');
            if (row.previous_identifier) {
                fieldHtml = '<span>' + esc('from ' + row.previous_identifier)
                    + '</span>' + fieldHtml;
            }
            card.className = 'rj-history-card';
            card.innerHTML = ''
                + '<div class="rj-history-card__time">'
                + esc(fmtTime(row.timestamp)) + '</div>'
                + '<div class="rj-history-card__user">'
                + esc(row.user || '') + '</div>'
                + '<div class="rj-history-card__what">'
                + '<span class="rj-history-badge rj-history-badge--action">'
                + esc(prettyAction(row.action)) + '</span>'
                + '<span class="rj-history-card__name">'
                + esc(row.identifier || '') + '</span>'
                + '<span class="rj-history-badge">'
                + esc(row.instrument || '') + '</span>'
                + '<span class="rj-history-fields">' + fieldHtml + '</span>'
                + '</div>'
                + '<div class="rj-history-card__actions">'
                + '<button type="button" class="rj-btn-small" '
                + 'data-action="view" title="View change">'
                + '<i class="fa-solid fa-eye"></i> View</button>'
                + '<button type="button" class="rj-btn-small" '
                + 'data-action="restore" title="Restore this state">'
                + '<i class="fa-solid fa-clock-rotate-left"></i> '
                + 'Restore</button>'
                + (canManageHistory
                    ? '<button type="button" class="rj-btn-small" '
                    + 'data-action="delete-history" '
                    + 'title="Delete history entry">'
                    + '<i class="fa-solid fa-trash"></i> Delete</button>'
                    : '')
                + '</div>';
            card.querySelector('[data-action="view"]').addEventListener(
                'click',
                function () {
                    openHistoryEntry(row.id);
                }
            );
            card.querySelector('[data-action="restore"]').addEventListener(
                'click',
                function () {
                    restoreHistoryEntry(row.id);
                }
            );
            var deleteBtn = card.querySelector(
                '[data-action="delete-history"]'
            );
            if (deleteBtn) {
                deleteBtn.addEventListener('click', function () {
                    deleteHistoryEntry(row.id);
                });
            }
            host.appendChild(card);
        });
    }

    function parseJsonSafe(resp) {
        return resp.text().then(function (txt) {
            var body = null;
            try {
                body = JSON.parse(txt);
            } catch (err) {
                body = null;
            }
            return { ok: resp.ok, status: resp.status,
                body: body, raw: txt };
        });
    }

    function restoreHistoryEntry(id) {
        if (!window.confirm('Restore this rejection-list state?')) {
            return;
        }
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Restoring...');

        function doRestore(url) {
            return fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id })
            }).then(parseJsonSafe);
        }

        doRestore('/api/rejection-list/history/restore').then(function (res) {
            var needsLegacy = res.status === 404 || res.body === null;
            if (needsLegacy) {
                return doRestore('/api/rejection-list/history/resolve');
            }
            return res;
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                var message = (res.body && res.body.error) || '';
                if (!message) {
                    message = 'HTTP ' + String(res.status || 'error');
                }
                setStatus('rj-history-status', 'Failed: ' + esc(message));
                return;
            }
            setStatus('rj-history-status',
                '<i class="fa-solid fa-check"></i> Restored.');
            loadHistory();
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    function deleteHistoryEntry(id) {
        if (!canManageHistory) return;
        if (!window.confirm('Delete this history entry?')) {
            return;
        }
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Deleting...');
        fetch('/api/rejection-list/history/delete', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id })
        }).then(parseJsonSafe).then(function (res) {
            if (!res.body || !res.body.success) {
                var message = (res.body && res.body.error) || '';
                if (!message) {
                    message = 'HTTP ' + String(res.status || 'error');
                }
                setStatus('rj-history-status', 'Failed: ' + esc(message));
                return;
            }
            setStatus('rj-history-status',
                '<i class="fa-solid fa-check"></i> Deleted.');
            loadHistory();
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    function clearHistory() {
        if (!canManageHistory) return;
        if (!window.confirm('Clear ALL rejection history entries?')) {
            return;
        }
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Clearing...');
        fetch('/api/rejection-list/history/clear', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        }).then(parseJsonSafe).then(function (res) {
            if (!res.body || !res.body.success) {
                var message = (res.body && res.body.error) || '';
                if (!message) {
                    message = 'HTTP ' + String(res.status || 'error');
                }
                setStatus('rj-history-status', 'Failed: ' + esc(message));
                return;
            }
            state.historyPage = 1;
            setStatus('rj-history-status',
                '<i class="fa-solid fa-check"></i> History cleared.');
            loadHistory();
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    function loadHistory() {
        setMainView('history');
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Loading...');
        var params = new URLSearchParams();
        params.set('page', state.historyPage);
        params.set('per_page', state.historyPerPage);
        if (state.historyQ) params.set('q', state.historyQ);
        fetch('/api/rejection-list/history/list?' + params.toString(), {
            credentials: 'same-origin'
        }).then(function (resp) {
            return resp.json().then(function (body) {
                return { ok: resp.ok, body: body };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                setStatus('rj-history-status', 'Failed: '
                    + esc((res.body && res.body.error) || 'unknown'));
                return;
            }
            state.historyPages = res.body.pages || 0;
            state.historyPage = res.body.page || 1;
            setStatus('rj-history-status', '');
            renderHistory(res.body.rows || []);
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    function openHistoryEntry(id) {
        setStatus('rj-history-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> Loading entry...');
        fetch('/api/rejection-list/history/get?id=' + encodeURIComponent(id), {
            credentials: 'same-origin'
        }).then(function (resp) {
            return resp.json();
        }).then(function (body) {
            setStatus('rj-history-status', '');
            if (!body || !body.success) {
                setStatus('rj-history-status', 'Failed: '
                    + esc((body && body.error) || 'unknown'));
                return;
            }
            var entry = body.entry || {};
            var before = entry.before || {};
            var after = entry.after || {};
            var keys = {};
            Object.keys(before).forEach(function (key) { keys[key] = true; });
            Object.keys(after).forEach(function (key) { keys[key] = true; });
            var rows = Object.keys(keys).sort().map(function (key) {
                var b = before[key];
                var a = after[key];
                return renderDiffCard(key,
                    b == null ? '' : String(b),
                    a == null ? '' : String(a));
            }).join('');
            document.getElementById('rj-diff-title').textContent =
                'History entry for ' + (entry.identifier || '');
            document.getElementById('rj-diff-body').innerHTML = ''
                + '<div class="rj-history-card__time">'
                + esc(fmtTime(entry.timestamp || '')) + ' · '
                + esc(entry.user || '') + ' · '
                + esc(entry.instrument || '') + '</div>'
                + '<p style="margin:8px 0 12px 0; color:#57606a;">'
                + 'Changed fields rendered inline using the same add/remove '
                + 'colour treatment as astrometrics history.</p>'
                + '<div class="rj-diff-grid">' + rows + '</div>';
            showOverlay('rj-diff-overlay', true);
        }).catch(function (err) {
            setStatus('rj-history-status', 'Failed: ' + esc(err));
        });
    }

    document.querySelectorAll('[data-rj-tab]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var tab = btn.getAttribute('data-rj-tab');
            updateTabButtons(tab);
            if (tab === 'history') {
                loadHistory();
                return;
            }
            state.tab = tab;
            state.page = 1;
            loadRows();
        });
    });

    document.addEventListener('click', function (event) {
        var close = event.target.closest('[data-rj-close]');
        if (!close) return;
        var which = close.getAttribute('data-rj-close');
        showOverlay('rj-' + which + '-overlay', false);
    });

    document.getElementById('rj-save').addEventListener('click', function () {
        saveRow(false);
    });

    document.getElementById('rj-open-upload').addEventListener(
        'click',
        function () {
            setStatus('rj-upload-status', '');
            showOverlay('rj-upload-overlay', true);
        }
    );

    document.getElementById('rj-upload-submit').addEventListener(
        'click',
        function () {
            submitUpload(false);
        }
    );

    document.getElementById('rj-filter-input').addEventListener(
        'input',
        function (event) {
            if (filterTimer) window.clearTimeout(filterTimer);
            filterTimer = window.setTimeout(function () {
                state.q = event.target.value || '';
                state.page = 1;
                loadRows();
            }, 250);
        }
    );

    document.getElementById('rj-per-page').addEventListener(
        'change',
        function (event) {
            state.perPage = Number(event.target.value || 50);
            state.page = 1;
            loadRows();
        }
    );

    document.getElementById('rj-sort').addEventListener(
        'change',
        function (event) {
            state.sort = String(event.target.value || 'identifier_asc');
            state.page = 1;
            loadRows();
        }
    );

    ['pp', 'tel', 'rv', 'used'].forEach(function (key) {
        var el = document.getElementById('rj-filter-' + key);
        if (!el) return;
        el.addEventListener('change', function (event) {
            state.filters[key] = String(event.target.value || '');
            state.page = 1;
            loadRows();
        });
    });

    document.getElementById('rj-prev').addEventListener('click', function () {
        if (state.page > 1) {
            state.page -= 1;
            loadRows();
        }
    });

    document.getElementById('rj-next').addEventListener('click', function () {
        if (state.page < state.pages) {
            state.page += 1;
            loadRows();
        }
    });

    if (cfg.canViewHistory) {
        var histFilter = document.getElementById('rj-history-filter');
        var histPer = document.getElementById('rj-history-per-page');
        var histPrev = document.getElementById('rj-history-prev');
        var histNext = document.getElementById('rj-history-next');
        var histClear = document.getElementById('rj-history-clear');
        if (histFilter) {
            histFilter.addEventListener(
            'input',
            function (event) {
                if (historyTimer) window.clearTimeout(historyTimer);
                historyTimer = window.setTimeout(function () {
                    state.historyQ = event.target.value || '';
                    state.historyPage = 1;
                    loadHistory();
                }, 250);
            }
            );
        }
        if (histPer) {
            histPer.addEventListener(
            'change',
            function (event) {
                state.historyPerPage = Number(event.target.value || 50);
                state.historyPage = 1;
                loadHistory();
            }
            );
        }
        if (histPrev) {
            histPrev.addEventListener(
            'click',
            function () {
                if (state.historyPage > 1) {
                    state.historyPage -= 1;
                    loadHistory();
                }
            }
            );
        }
        if (histNext) {
            histNext.addEventListener(
            'click',
            function () {
                if (state.historyPage < state.historyPages) {
                    state.historyPage += 1;
                    loadHistory();
                }
            }
            );
        }
        if (histClear) {
            histClear.addEventListener('click', clearHistory);
        }
    }

    updateTabButtons(state.tab);
    loadRows();
}());