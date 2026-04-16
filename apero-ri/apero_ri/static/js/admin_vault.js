/* ARI Vault — admin portal vault page manager.
 * Depends on: window.ARI_VAULT (injected by vault.html)
 */
(function () {
    'use strict';

    var CFG = window.ARI_VAULT;

    // -------------------------------------------------------------------
    // State
    // -------------------------------------------------------------------
    var _allEntries = {};   // { level: [entries, ...] }
    var _sortOrder  = 'modified_desc';
    var _searchTerm = '';

    // -------------------------------------------------------------------
    // Utility helpers
    // -------------------------------------------------------------------
    function _fmt(iso) {
        if (!iso) { return '—'; }
        try {
            var d = new Date(iso);
            return d.toLocaleDateString(undefined, {
                year: 'numeric', month: 'short', day: 'numeric'
            });
        } catch (e) { return String(iso).slice(0, 10); }
    }

    function _levelLabel(level) {
        var sec = (CFG.sections || []).find(function (s) {
            return s.level === level;
        });
        return sec ? sec.label : level;
    }

    function _showMsg(text, isError) {
        var el = document.getElementById('vault-msg');
        if (!el) { return; }
        el.textContent = text;
        el.style.display = 'block';
        el.style.color = isError
            ? 'var(--ari-danger, #c0392b)'
            : 'var(--ari-success, #27ae60)';
        clearTimeout(el._t);
        el._t = setTimeout(function () {
            el.style.display = 'none';
        }, 5000);
    }

    function _post(url, body, cb) {
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        })
        .then(function (r) { return r.json(); })
        .then(cb)
        .catch(function (e) {
            cb({ success: false, error: String(e) });
        });
    }

    function _get(url, cb) {
        fetch(url)
        .then(function (r) { return r.json(); })
        .then(cb)
        .catch(function (e) {
            cb({ success: false, error: String(e) });
        });
    }

    // -------------------------------------------------------------------
    // Sorting and filtering
    // -------------------------------------------------------------------
    function _sortEntries(entries) {
        var arr = entries.slice();
        if (_sortOrder === 'modified_desc') {
            arr.sort(function (a, b) {
                return (b.modified_at || '').localeCompare(
                    a.modified_at || ''
                );
            });
        } else if (_sortOrder === 'modified_asc') {
            arr.sort(function (a, b) {
                return (a.modified_at || '').localeCompare(
                    b.modified_at || ''
                );
            });
        } else if (_sortOrder === 'title_asc') {
            arr.sort(function (a, b) {
                return (a.title || '').localeCompare(b.title || '');
            });
        } else {
            arr.sort(function (a, b) {
                return (b.title || '').localeCompare(a.title || '');
            });
        }
        return arr;
    }

    function _filterEntries(entries) {
        if (!_searchTerm) { return entries; }
        var q = _searchTerm.toLowerCase();
        return entries.filter(function (e) {
            return (e.title || '').toLowerCase().indexOf(q) !== -1;
        });
    }

    // -------------------------------------------------------------------
    // Card rendering
    // -------------------------------------------------------------------
    function _makeCard(entry, canManage) {
        var div = document.createElement('div');
        div.className = 'vault-card';
        div.dataset.id = entry.id;

        // Left: icon + title
        var titleCell = document.createElement('div');
        titleCell.className = 'vault-title-cell';

        var lockIcon = document.createElement('i');
        lockIcon.className = 'fa-solid fa-lock';
        lockIcon.style.cssText =
            'color:var(--ari-text-muted,#aaa);' +
            'flex-shrink:0;font-size:0.9rem;';
        titleCell.appendChild(lockIcon);

        var titleSpan = document.createElement('span');
        titleSpan.className = 'vault-title-text';
        titleSpan.textContent = entry.title || '(untitled)';
        titleCell.appendChild(titleSpan);
        div.appendChild(titleCell);

        // Right: badge + date + buttons
        var meta = document.createElement('div');
        meta.className = 'vault-meta';

        var badge = document.createElement('span');
        badge.className =
            'ari-health-badge ari-health-badge--ok';
        badge.style.fontSize = '0.72rem';
        badge.textContent = _levelLabel(entry.level);
        meta.appendChild(badge);

        var dateEl = document.createElement('span');
        dateEl.className = 'vault-date';
        dateEl.textContent = _fmt(entry.modified_at);
        meta.appendChild(dateEl);

        var viewBtn = document.createElement('button');
        viewBtn.className =
            'ari-btn ari-btn--secondary ari-btn--sm';
        viewBtn.title = 'View information';
        viewBtn.innerHTML =
            '<i class="fa-solid fa-eye"></i>';
        viewBtn.addEventListener('click', function () {
            vaultView(entry.id);
        });
        meta.appendChild(viewBtn);

        if (canManage) {
            var editBtn = document.createElement('button');
            editBtn.className =
                'ari-btn ari-btn--secondary ari-btn--sm';
            editBtn.title = 'Edit';
            editBtn.innerHTML =
                '<i class="fa-solid fa-pen-to-square"></i>';
            editBtn.addEventListener('click', function () {
                vaultEdit(entry.id);
            });
            meta.appendChild(editBtn);

            var delBtn = document.createElement('button');
            delBtn.className =
                'ari-btn ari-btn--danger ari-btn--sm';
            delBtn.title = 'Delete';
            delBtn.innerHTML =
                '<i class="fa-solid fa-trash"></i>';
            delBtn.addEventListener('click', function () {
                vaultConfirmDelete(entry.id, entry.title);
            });
            meta.appendChild(delBtn);
        }

        div.appendChild(meta);
        return div;
    }

    function _renderSection(level) {
        var container =
            document.getElementById('vault-entries-' + level);
        if (!container) { return; }

        var sec = (CFG.sections || []).find(function (s) {
            return s.level === level;
        });
        var canManage = !!(sec && sec.can_manage);

        var entries = _filterEntries(
            _sortEntries(_allEntries[level] || [])
        );

        container.innerHTML = '';
        if (entries.length === 0) {
            var empty = document.createElement('p');
            empty.style.cssText =
                'color:var(--ari-text-muted,#aaa);' +
                'font-size:0.85rem;padding:4px 2px;';
            empty.textContent =
                canManage
                    ? 'No entries yet. Click "Add entry…" above.'
                    : 'No entries.';
            container.appendChild(empty);
            return;
        }

        entries.forEach(function (entry) {
            container.appendChild(
                _makeCard(entry, canManage)
            );
        });
    }

    function _renderAll() {
        (CFG.sections || []).forEach(function (sec) {
            _renderSection(sec.level);
        });
    }

    // -------------------------------------------------------------------
    // Data loading
    // -------------------------------------------------------------------
    function _loadEntries() {
        _get(CFG.listUrl, function (data) {
            if (!data.success) {
                _showMsg(
                    data.error || 'Failed to load entries.',
                    true
                );
                return;
            }
            _allEntries = {};
            (CFG.sections || []).forEach(function (sec) {
                _allEntries[sec.level] = [];
            });
            (data.entries || []).forEach(function (e) {
                var lvl = e.level || 'moderator';
                if (!_allEntries[lvl]) {
                    _allEntries[lvl] = [];
                }
                _allEntries[lvl].push(e);
            });
            _renderAll();
        });
    }

    // -------------------------------------------------------------------
    // Overlay management
    // -------------------------------------------------------------------
    function _closeAll() {
        [
            'vault-edit-overlay',
            'vault-view-overlay',
            'vault-del-overlay'
        ].forEach(function (id) {
            var el = document.getElementById(id);
            if (el) { el.style.display = 'none'; }
        });
    }

    // -------------------------------------------------------------------
    // Add / Edit overlay
    // -------------------------------------------------------------------
    window.vaultOpenAdd = function (level) {
        document.getElementById('vault-edit-heading')
            .innerHTML =
            '<i class="fa-solid fa-vault"></i> Add Entry';
        document.getElementById('vault-edit-id').value   = '';
        document.getElementById('vault-edit-name').value = '';
        document.getElementById('vault-edit-info').value = '';
        var lvlEl =
            document.getElementById('vault-edit-level');
        if (lvlEl) { lvlEl.value = level; }
        document.getElementById('vault-edit-error')
            .style.display = 'none';
        document.getElementById('vault-edit-overlay')
            .style.display = 'flex';
        document.getElementById('vault-edit-name').focus();
    };

    window.vaultEdit = function (entryId) {
        _get(
            CFG.getUrl + '?id=' +
                encodeURIComponent(entryId),
            function (data) {
                if (!data.success) {
                    _showMsg(
                        data.error || 'Failed to load.',
                        true
                    );
                    return;
                }
                var e = data.entry;
                document.getElementById('vault-edit-heading')
                    .innerHTML =
                    '<i class="fa-solid fa-pen-to-square">' +
                    '</i> Edit Entry';
                document.getElementById(
                    'vault-edit-id'
                ).value   = e.id;
                document.getElementById(
                    'vault-edit-name'
                ).value  = e.title || '';
                document.getElementById(
                    'vault-edit-info'
                ).value  = e.information || '';
                var lvlEl = document.getElementById(
                    'vault-edit-level'
                );
                if (lvlEl) {
                    lvlEl.value = e.level || 'moderator';
                }
                document.getElementById('vault-edit-error')
                    .style.display = 'none';
                document.getElementById('vault-edit-overlay')
                    .style.display = 'flex';
            }
        );
    };

    function _saveEntry() {
        var idEl   = document.getElementById('vault-edit-id');
        var nameEl =
            document.getElementById('vault-edit-name');
        var lvlEl  =
            document.getElementById('vault-edit-level');
        var infoEl =
            document.getElementById('vault-edit-info');
        var errEl  =
            document.getElementById('vault-edit-error');

        var title = (nameEl.value || '').trim();
        if (!title) {
            errEl.textContent = 'Title is required.';
            errEl.style.display = 'block';
            return;
        }

        var body = {
            id:          idEl.value || null,
            title:       title,
            information: (infoEl.value || '').trim(),
            level:       lvlEl ? lvlEl.value : 'moderator'
        };
        var url = body.id ? CFG.updateUrl : CFG.addUrl;

        _post(url, body, function (data) {
            if (!data.success) {
                errEl.textContent =
                    data.error || 'Save failed.';
                errEl.style.display = 'block';
                return;
            }
            _closeAll();
            _showMsg(
                body.id ? 'Entry updated.' : 'Entry added.',
                false
            );
            _loadEntries();
        });
    }

    // -------------------------------------------------------------------
    // View information overlay
    // -------------------------------------------------------------------
    window.vaultView = function (entryId) {
        _get(
            CFG.getUrl + '?id=' +
                encodeURIComponent(entryId),
            function (data) {
                if (!data.success) {
                    _showMsg(
                        data.error || 'Failed to load.',
                        true
                    );
                    return;
                }
                var e = data.entry;
                document.getElementById(
                    'vault-view-name'
                ).textContent = e.title || '';
                document.getElementById(
                    'vault-view-info'
                ).textContent = e.information || '(empty)';
                document.getElementById(
                    'vault-view-badge'
                ).textContent = _levelLabel(e.level);
                document.getElementById(
                    'vault-view-modified'
                ).textContent = _fmt(e.modified_at);
                document.getElementById(
                    'vault-view-creator'
                ).textContent = e.created_by || '—';
                document.getElementById('vault-view-overlay')
                    .style.display = 'flex';
            }
        );
    };

    // -------------------------------------------------------------------
    // Delete confirm overlay
    // -------------------------------------------------------------------
    window.vaultConfirmDelete = function (entryId, title) {
        document.getElementById(
            'vault-del-id'
        ).value = entryId;
        document.getElementById(
            'vault-del-name'
        ).textContent = title || entryId;
        document.getElementById('vault-del-overlay')
            .style.display = 'flex';
    };

    function _doDelete() {
        var entryId =
            document.getElementById('vault-del-id').value;
        _post(
            CFG.deleteUrl,
            { id: entryId },
            function (data) {
                _closeAll();
                if (!data.success) {
                    _showMsg(
                        data.error || 'Delete failed.',
                        true
                    );
                    return;
                }
                _showMsg('Entry deleted.', false);
                _loadEntries();
            }
        );
    }

    // -------------------------------------------------------------------
    // Initialisation
    // -------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {
        // Sort
        var sortEl = document.getElementById('vault-sort');
        if (sortEl) {
            sortEl.addEventListener('change', function () {
                _sortOrder = this.value;
                _renderAll();
            });
        }

        // Search
        var searchEl =
            document.getElementById('vault-search');
        if (searchEl) {
            searchEl.addEventListener('input', function () {
                _searchTerm = this.value;
                _renderAll();
            });
        }

        // Edit overlay
        var saveBtn =
            document.getElementById('vault-edit-save');
        if (saveBtn) {
            saveBtn.addEventListener('click', _saveEntry);
        }
        document.getElementById('vault-edit-cancel')
            .addEventListener('click', _closeAll);
        document.getElementById('vault-edit-close')
            .addEventListener('click', _closeAll);

        // View overlay
        document.getElementById('vault-view-close')
            .addEventListener('click', _closeAll);
        document.getElementById('vault-view-close-btn')
            .addEventListener('click', _closeAll);

        // Delete overlay
        document.getElementById('vault-del-confirm')
            .addEventListener('click', _doDelete);
        document.getElementById('vault-del-cancel')
            .addEventListener('click', _closeAll);
        document.getElementById('vault-del-close')
            .addEventListener('click', _closeAll);

        // Escape key closes any open overlay
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') { _closeAll(); }
        });

        // Initial data load
        _loadEntries();
    });
}());
