/* manage_uploads.js – Admin: Manage Upload Directories */
(function () {
    'use strict';

    /* ------------------------------------------------------------------ */
    /* State                                                                */
    /* ------------------------------------------------------------------ */
    var _dirs        = [];   // loaded directory configs
    var _allGroups   = [];   // all group names
    var _canManage   = [];   // groups this editor can set
    var _pendingDel  = null; // {id, name} for confirm modal
    var _muBrowsePath = '/'; // current browse path

    /* ------------------------------------------------------------------ */
    /* DOM shortcuts                                                        */
    /* ------------------------------------------------------------------ */
    function $$(id) { return document.getElementById(id); }

    /* ------------------------------------------------------------------ */
    /* Tab switching                                                        */
    /* ------------------------------------------------------------------ */
    function initTabs() {
        var tabs = {
            'mu-tab-manage': 'mu-manage',
            'mu-tab-quota':  'mu-quota',
        };
        Object.keys(tabs).forEach(function (tabId) {
            ($$( tabId) || {}).addEventListener &&
            $$(tabId).addEventListener('click', function () {
                Object.keys(tabs).forEach(function (t) {
                    $$(t).classList.toggle(
                        'ari-sg-tab--active', t === tabId
                    );
                    $$(t).setAttribute(
                        'aria-selected', String(t === tabId)
                    );
                    var panel = $$(tabs[t]);
                    if (panel) panel.style.display =
                        t === tabId ? '' : 'none';
                });
                if (tabId === 'mu-tab-quota') loadQuota();
            });
        });
    }

    /* ------------------------------------------------------------------ */
    /* Load config                                                          */
    /* ------------------------------------------------------------------ */
    function loadConfig() {
        fetch('/api/admin/uploads/config')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    showError('Failed to load config: ' + (data.error || ''));
                    return;
                }
                _dirs      = data.directories || [];
                _allGroups = data.all_groups   || [];
                _canManage = data.can_manage_groups || [];
                renderDirList();
            })
            .catch(function () { showError('Network error'); });
    }

    /* ------------------------------------------------------------------ */
    /* Render directory cards                                               */
    /* ------------------------------------------------------------------ */
    function renderDirList() {
        var list  = $$('mu-dir-list');
        var empty = $$('mu-dir-empty');
        list.innerHTML = '';
        if (!_dirs.length) {
            list.style.display  = 'none';
            empty.style.display = '';
            return;
        }
        list.style.display  = '';
        empty.style.display = 'none';

        _dirs.forEach(function (d) {
            var quota = typeof d.quota_gb === 'number'
                ? d.quota_gb.toFixed(1) + ' GB' : '–';
            var groups = (d.allowed_groups || []).join(', ') || '(none)';
            var typeLabel = d.type === 'global' ? 'Global' : 'Per-user';
            var typeIcon  = d.type === 'global'
                ? 'fa-solid fa-folder' : 'fa-solid fa-users';

            var card = document.createElement('div');
            card.className = 'mu-dir-card';
            card.innerHTML =
                '<div class="mu-dir-card__header">' +
                    '<span class="mu-dir-card__name">' +
                        esc(d.name) +
                    '</span>' +
                    '<div class="mu-dir-card__actions">' +
                        '<button class="ari-btn ari-btn--sm ari-btn--secondary' +
                            ' mu-btn-edit" data-id="' + esc(d.id) + '"' +
                            ' title="Edit"><i class="fa-solid fa-pen"></i>' +
                        '</button>' +
                        '<button class="ari-btn ari-btn--sm ari-btn--danger' +
                            ' mu-btn-delete" data-id="' + esc(d.id) + '"' +
                            ' data-name="' + esc(d.name) + '"' +
                            ' title="Remove"><i class="fa-solid fa-trash"></i>' +
                        '</button>' +
                    '</div>' +
                '</div>' +
                '<div class="mu-dir-card__body">' +
                    '<div class="mu-dir-meta">' +
                        '<span class="mu-dir-meta__item">' +
                            '<i class="' + typeIcon + '"></i> ' + typeLabel +
                        '</span>' +
                        '<span class="mu-dir-meta__item">' +
                            '<i class="fa-solid fa-hard-drive"></i> ' +
                            esc(d.path) +
                        '</span>' +
                        '<span class="mu-dir-meta__item">' +
                            '<i class="fa-solid fa-database"></i> Quota: ' +
                            quota +
                        '</span>' +
                        '<span class="mu-dir-meta__item">' +
                            '<i class="fa-solid fa-users"></i> Groups: ' +
                            esc(groups) +
                        '</span>' +
                    '</div>' +
                '</div>';
            list.appendChild(card);
        });

        /* Wire buttons */
        list.querySelectorAll('.mu-btn-edit').forEach(function (btn) {
            btn.addEventListener('click', function () {
                openModal(btn.dataset.id);
            });
        });
        list.querySelectorAll('.mu-btn-delete').forEach(function (btn) {
            btn.addEventListener('click', function () {
                openConfirm(btn.dataset.id, btn.dataset.name);
            });
        });
    }

    /* ------------------------------------------------------------------ */
    /* Add / Edit modal                                                     */
    /* ------------------------------------------------------------------ */
    function openModal(editId) {
        var isEdit = !!editId;
        $$('mu-modal-title-text').textContent = isEdit
            ? 'Edit Directory' : 'Add Directory';
        $$('mu-edit-id').value = editId || '';
        $$('mu-modal-error').style.display = 'none';

        /* Populate group cards */
        var wrap = $$('mu-groups-wrap');
        wrap.innerHTML = '';
        _allGroups.forEach(function (g) {
            var canSet     = _canManage.indexOf(g) > -1;
            var isSelected = isEdit
                && (_dirs.find(function (x) { return x.id === editId; })
                    ? ((_dirs.find(
                        function (x) { return x.id === editId; }
                    ).allowed_groups || []).indexOf(g) > -1)
                    : false);
            var card = document.createElement('button');
            card.type      = 'button';
            card.className = 'mu-group-card ' +
                (isSelected ? 'mu-group-card--on' : 'mu-group-card--off') +
                (canSet ? '' : ' mu-group-card--disabled');
            card.dataset.group = g;
            card.disabled = !canSet;
            card.innerHTML = '<i class="fa-solid fa-' +
                (isSelected ? 'check' : 'xmark') + '"></i> ' + esc(g);
            card.addEventListener('click', function () {
                toggleGroupCard(card);
            });
            wrap.appendChild(card);
        });

        if (isEdit) {
            var d = _dirs.find(function (x) { return x.id === editId; });
            if (d) {
                $$('mu-name').value  = d.name;
                $$('mu-path').value  = d.path;
                $$('mu-type').value  = d.type || 'per_user';
                $$('mu-quota').value = d.quota_gb || 1.0;
            }
        } else {
            $$('mu-name').value  = '';
            $$('mu-path').value  = '';
            $$('mu-type').value  = 'per_user';
            $$('mu-quota').value = '1.0';
        }

        $$('mu-modal-overlay').style.display = '';
        $$('mu-name').focus();
    }

    function closeModal() {
        $$('mu-modal-overlay').style.display = 'none';
    }

    function saveModal() {
        var editId = $$('mu-edit-id').value.trim();
        var name   = $$('mu-name').value.trim();
        var path   = $$('mu-path').value.trim();
        var type   = $$('mu-type').value;
        var quota  = parseFloat($$('mu-quota').value) || 1.0;
        var groups = [];
        $$('mu-groups-wrap').querySelectorAll(
            '.mu-group-card--on'
        ).forEach(function (btn) { groups.push(btn.dataset.group); });

        if (!name) {
            showModalError('Name is required.');
            return;
        }
        if (!path) {
            showModalError('Path is required.');
            return;
        }

        var url     = editId
            ? '/api/admin/uploads/dir/edit'
            : '/api/admin/uploads/dir/add';
        var payload = {
            name: name,
            path: path,
            type: type,
            quota_gb: quota,
            allowed_groups: groups,
        };
        if (editId) payload.id = editId;

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) {
                showModalError(data.error || 'Save failed');
                return;
            }
            closeModal();
            loadConfig();
        })
        .catch(function () { showModalError('Network error'); });
    }

    function showModalError(msg) {
        var el = $$('mu-modal-error');
        el.textContent = msg;
        el.style.display = '';
    }

    function toggleGroupCard(card) {
        if (card.disabled) return;
        var isOn = card.classList.contains('mu-group-card--on');
        card.classList.toggle('mu-group-card--on',  !isOn);
        card.classList.toggle('mu-group-card--off',  isOn);
        var icon = card.querySelector('i');
        if (icon) {
            icon.className = 'fa-solid fa-' + (isOn ? 'xmark' : 'check');
        }
    }

    /* ------------------------------------------------------------------ */
    /* File browser modal                                                   */
    /* ------------------------------------------------------------------ */
    function openBrowseModal() {
        var cur = ($$('mu-path').value || '').trim() || '/';
        _muBrowsePath = cur;
        $$('mu-browse-path-input').value = cur;
        $$('mu-browse-modal').style.display = 'flex';
        muBrowseTo(cur);
    }

    function closeBrowseModal() {
        $$('mu-browse-modal').style.display = 'none';
    }

    function muBrowseTo(path) {
        var list   = $$('mu-browse-list');
        var status = $$('mu-browse-status');
        list.innerHTML = '<div class="ari-sg-loading">Loading...</div>';
        status.style.display = 'none';

        fetch('/api/admin/apero-profiles/browse?path=' +
                encodeURIComponent(path))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    list.innerHTML = '<div class="ari-sg-error">' +
                        esc(data.error || 'Error') + '</div>';
                    $$('mu-browse-path-input').value = _muBrowsePath;
                    return;
                }
                _muBrowsePath = data.path;
                $$('mu-browse-path-input').value = data.path;

                if (data.validation) {
                    status.style.display = 'block';
                    status.className = 'ari-ap-browser__status' +
                        ' ari-ap-browser__status--valid';
                    status.innerHTML =
                        '<i class="fa-solid fa-circle-check"></i>' +
                        ' Directory exists';
                }

                list.innerHTML = '';
                var dirs = data.dirs || [];

                if (data.path !== '/') {
                    var parent = data.path.replace(/\/[^\/]+\/?$/, '') || '/';
                    var upItem = document.createElement('div');
                    upItem.className =
                        'ari-ap-browser__item ari-ap-browser__item--parent';
                    upItem.innerHTML =
                        '<i class="fa-solid fa-arrow-up"></i> ..';
                    upItem.addEventListener('click', function () {
                        muBrowseTo(parent);
                    });
                    list.appendChild(upItem);
                }

                if (dirs.length === 0) {
                    var empty = document.createElement('div');
                    empty.className = 'ari-sg-empty-small';
                    empty.textContent = 'No subdirectories';
                    list.appendChild(empty);
                } else {
                    dirs.forEach(function (d) {
                        var item = document.createElement('div');
                        item.className = 'ari-ap-browser__item';
                        item.innerHTML =
                            '<i class="fa-solid fa-folder"></i> ' + esc(d);
                        item.addEventListener('click', function () {
                            var newPath =
                                data.path.replace(/\/$/, '') + '/' + d;
                            muBrowseTo(newPath);
                        });
                        list.appendChild(item);
                    });
                }
            })
            .catch(function () {
                list.innerHTML =
                    '<div class="ari-sg-error">Failed to browse</div>';
            });
    }

    function muSelectBrowsePath() {
        $$('mu-path').value = _muBrowsePath;
        closeBrowseModal();
    }

    /* ------------------------------------------------------------------ */
    /* Delete confirm modal                                                 */
    /* ------------------------------------------------------------------ */
    function openConfirm(id, name) {
        _pendingDel = { id: id, name: name };
        $$('mu-confirm-name').textContent = name;
        $$('mu-confirm-overlay').style.display = '';
    }

    function closeConfirm() {
        _pendingDel = null;
        $$('mu-confirm-overlay').style.display = 'none';
    }

    function doDelete() {
        if (!_pendingDel) return;
        var payload = { id: _pendingDel.id };
        closeConfirm();
        fetch('/api/admin/uploads/dir/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) {
                showError(data.error || 'Delete failed');
                return;
            }
            loadConfig();
        })
        .catch(function () { showError('Network error'); });
    }

    /* ------------------------------------------------------------------ */
    /* Quota tab                                                            */
    /* ------------------------------------------------------------------ */
    function loadQuota() {
        var body  = $$('mu-quota-body');
        var empty = $$('mu-quota-empty');
        body.innerHTML = '<p class="mu-loading">' +
            '<i class="fa-solid fa-spinner fa-spin"></i> Loading…</p>';

        fetch('/api/admin/uploads/quota')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                body.innerHTML = '';
                if (!data.success || !data.quota || !data.quota.length) {
                    body.style.display   = 'none';
                    empty.style.display  = '';
                    return;
                }
                empty.style.display = 'none';
                body.style.display  = '';

                data.quota.forEach(function (q) {
                    var section = document.createElement('div');
                    section.className = 'mu-quota-section';

                    var rows = (q.rows || []).map(function (r) {
                        var pct = Math.min(100, r.pct || 0);
                        var barClass = pct >= 90 ? 'mu-quota-bar--red'
                            : pct >= 80          ? 'mu-quota-bar--yellow'
                            : 'mu-quota-bar--green';
                        return '<tr class="mu-quota-row">' +
                            '<td class="mu-quota-username">' +
                                esc(r.username) +
                            '</td>' +
                            '<td class="mu-quota-used">' +
                                fmtBytes(r.used_bytes) +
                                ' / ' + r.quota_gb.toFixed(1) + ' GB' +
                            '</td>' +
                            '<td class="mu-quota-bar-cell">' +
                                '<div class="mu-quota-bar-wrap">' +
                                    '<div class="mu-quota-bar ' + barClass +
                                        '" style="width:' + pct + '%">' +
                                    '</div>' +
                                '</div>' +
                                '<span class="mu-quota-pct">' +
                                    pct.toFixed(1) + '%' +
                                '</span>' +
                            '</td>' +
                        '</tr>';
                    }).join('');

                    section.innerHTML =
                        '<h3 class="mu-quota-dir-name">' +
                            '<i class="fa-solid fa-folder"></i> ' +
                            esc(q.name) +
                        '</h3>' +
                        (rows
                            ? '<table class="mu-quota-table"><thead><tr>' +
                                '<th>User</th><th>Used</th><th>Usage</th>' +
                                '</tr></thead><tbody>' + rows +
                                '</tbody></table>'
                            : '<p class="mu-no-data">No uploads yet.</p>');
                    body.appendChild(section);
                });
            })
            .catch(function () {
                body.innerHTML = '<p class="mu-error">Failed to load quota.</p>';
            });
    }

    /* ------------------------------------------------------------------ */
    /* Utilities                                                            */
    /* ------------------------------------------------------------------ */
    function esc(s) {
        return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function fmtBytes(b) {
        if (b < 1024)           return b + ' B';
        if (b < 1024 * 1024)    return (b / 1024).toFixed(1) + ' KB';
        if (b < 1024 ** 3)      return (b / (1024 * 1024)).toFixed(1) + ' MB';
        return (b / (1024 ** 3)).toFixed(2) + ' GB';
    }

    function showError(msg) {
        console.error('[manage_uploads]', msg);
    }

    /* ------------------------------------------------------------------ */
    /* Bootstrap                                                            */
    /* ------------------------------------------------------------------ */
    document.addEventListener('DOMContentLoaded', function () {
        initTabs();
        loadConfig();

        $$(  'mu-add-btn').addEventListener('click', function () {
            openModal(null);
        });
        $$('mu-modal-close').addEventListener('click', closeModal);
        $$('mu-modal-cancel').addEventListener('click', closeModal);
        $$('mu-modal-save').addEventListener('click', saveModal);
        $$('mu-modal-overlay').addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });

        $$('mu-confirm-close').addEventListener('click', closeConfirm);
        $$('mu-confirm-no').addEventListener('click', closeConfirm);
        $$('mu-confirm-yes').addEventListener('click', doDelete);
        $$('mu-confirm-overlay').addEventListener('click', function (e) {
            if (e.target === this) closeConfirm();
        });

        $$('mu-browse-btn').addEventListener('click', openBrowseModal);
        $$('mu-browse-cancel').addEventListener('click', closeBrowseModal);
        $$('mu-browse-cancel-x').addEventListener('click', closeBrowseModal);
        $$('mu-browse-select').addEventListener('click', muSelectBrowsePath);
        $$('mu-browse-go').addEventListener('click', function () {
            muBrowseTo($$('mu-browse-path-input').value.trim() || '/');
        });
        $$('mu-browse-path-input').addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                muBrowseTo($$('mu-browse-path-input').value.trim() || '/');
            }
        });
        $$('mu-browse-modal').addEventListener('click', function (e) {
            if (e.target === this) closeBrowseModal();
        });
    });
}());
