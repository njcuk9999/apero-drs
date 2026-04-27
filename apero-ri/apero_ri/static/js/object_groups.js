/* ==========================================================================
   Object Groups page logic – shared object collections.
   Depends on window.ARI_OBJECT_GROUPS being set.
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_OBJECT_GROUPS || {};

    /* ── DOM refs ────────────────────────────────────────────────── */
    var loadingEl = document.getElementById('og-loading');
    var errorEl = document.getElementById('og-error');
    var container = document.getElementById(
        'og-groups-container'
    );
    var emptyEl = document.getElementById('og-empty');
    var groupCountEl = document.getElementById(
        'og-group-count'
    );
    var groupPluralEl = document.getElementById(
        'og-group-plural'
    );
    var createBtn = document.getElementById(
        'og-create-group-btn'
    );
    var filterInput = document.getElementById(
        'og-filter-input'
    );

    /* Add-objects modal */
    var addModal = document.getElementById('og-add-modal');
    var addModalClose = document.getElementById(
        'og-add-modal-close'
    );
    var addQuery = document.getElementById('og-add-query');
    var addGroupInput = document.getElementById(
        'og-add-group'
    );
    var addSingleBtn = document.getElementById(
        'og-add-single-btn'
    );
    var addBulkFile = document.getElementById(
        'og-add-bulk-file'
    );
    var addBulkBtn = document.getElementById(
        'og-add-bulk-btn'
    );
    var addBulkResult = document.getElementById(
        'og-add-bulk-result'
    );
    var addSingleResult = document.getElementById(
        'og-add-single-result'
    );

    /* Rename modal */
    var renameModal = document.getElementById(
        'og-rename-modal'
    );
    var renameClose = document.getElementById(
        'og-rename-modal-close'
    );
    var renameInput = document.getElementById(
        'og-rename-input'
    );
    var renameOld = document.getElementById('og-rename-old');
    var renameSubmit = document.getElementById(
        'og-rename-submit'
    );

    var groupsData = [];
    var canModerate = false;

    /* ── Helpers ─────────────────────────────────────────────────── */
    function hide(el) {
        if (el) el.style.display = 'none';
    }
    function show(el) {
        if (el) el.style.display = '';
    }
    function esc(text) {
        var d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }
    function postJson(url, body) {
        return fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        }).then(function (r) { return r.json(); });
    }
    function getJson(url) {
        return fetch(url).then(function (r) {
            return r.json();
        });
    }

    /* ================================================================
       Load group list
       ================================================================ */
    function loadGroups() {
        hide(errorEl);
        hide(emptyEl);
        hide(container);
        show(loadingEl);

        var url = cfg.listApiUrl +
            '?profile_id=' +
            encodeURIComponent(cfg.profileId);

        getJson(url).then(function (data) {
            hide(loadingEl);
            if (!data.success) {
                errorEl.textContent = data.error ||
                    'Failed to load groups.';
                show(errorEl);
                return;
            }
            groupsData = data.groups || [];
            canModerate = data.can_moderate || false;
            renderGroups();
        }).catch(function () {
            hide(loadingEl);
            errorEl.textContent =
                'Network error loading groups.';
            show(errorEl);
        });
    }

    /* ================================================================
       Render groups as expandable section cards
       ================================================================ */
    function renderGroups() {
        groupCountEl.textContent = String(groupsData.length);
        groupPluralEl.textContent =
            groupsData.length === 1 ? '' : 's';

        if (!groupsData.length) {
            container.innerHTML = '';
            hide(container);
            show(emptyEl);
            return;
        }
        hide(emptyEl);
        show(container);

        var html = '';
        groupsData.forEach(function (g) {
            html += '<div class="at-section-card' +
                ' og-group-section"' +
                ' data-group="' + esc(g.name) + '">';
            html += '<div class="at-section-card__header"' +
                ' style="cursor:pointer;">';
            html += '<i class="fa-solid fa-layer-group' +
                ' ari-fav-section__icon"></i>';
            html += '<span class="ari-fav-section__name">' +
                esc(g.name) + '</span>';
            html += '<span class="ari-fav-section__count">' +
                '(' + (g.object_count || 0) + ')</span>';
            html += '<span class="at-muted-hint"' +
                ' style="margin-left:0.6em;font-size:0.8em;">' +
                'by ' + esc(g.created_by || '?') + '</span>';
            html += '<div class="op-section-controls">';
            html += '<button type="button"' +
                ' class="ari-btn ari-btn--sm' +
                ' ari-btn--secondary og-add-objects-btn"' +
                ' data-group="' + esc(g.name) + '"' +
                ' title="Add objects to this group">' +
                '<i class="fa-solid fa-plus"></i></button>';
            if (g.can_edit) {
                html += ' <button type="button"' +
                    ' class="ari-btn ari-btn--sm' +
                    ' ari-btn--secondary og-rename-btn"' +
                    ' data-group="' + esc(g.name) + '"' +
                    ' title="Rename group">' +
                    '<i class="fa-solid fa-pen"></i>' +
                    '</button>';
            }
            if (g.can_delete) {
                html += ' <button type="button"' +
                    ' class="ari-btn ari-btn--sm' +
                    ' ari-btn--danger og-delete-btn"' +
                    ' data-group="' + esc(g.name) + '"' +
                    ' title="Delete group">' +
                    '<i class="fa-solid fa-trash"></i>' +
                    '</button>';
            }
            html += '<button type="button"' +
                ' class="ari-fav-section__collapse-btn' +
                ' op-section-btn og-toggle-btn"' +
                ' data-group="' + esc(g.name) + '"' +
                ' aria-expanded="false">' +
                '<i class="fa-solid fa-chevron-right">' +
                '</i></button>';
            html += '</div>';
            html += '</div>';
            html += '<div class="at-section-card__body' +
                ' og-group-body"' +
                ' data-group="' + esc(g.name) + '"' +
                ' style="display:none;">';
            html += '<div class="og-group-objects-loading' +
                ' at-muted-hint">' +
                '<i class="fa-solid fa-spinner fa-spin">' +
                '</i> Loading objects&hellip;</div>';
            html += '<div class="og-group-objects"' +
                ' style="display:none;"></div>';
            html += '</div>';
            html += '</div>';
        });
        container.innerHTML = html;
        wireGroupButtons();
        applyFilter();
    }

    /* ================================================================
       Wire button handlers
       ================================================================ */
    function wireGroupButtons() {
        /* Helper: toggle collapse for a group section */
        function toggleGroup(grp) {
            var btn = container.querySelector(
                '.og-toggle-btn[data-group="' +
                grp + '"]'
            );
            var body = container.querySelector(
                '.og-group-body[data-group="' +
                grp + '"]'
            );
            if (!btn || !body) return;
            var expanded = btn.getAttribute(
                'aria-expanded'
            ) === 'true';
            if (expanded) {
                hide(body);
                btn.setAttribute(
                    'aria-expanded', 'false'
                );
                btn.querySelector('i').className =
                    'fa-solid fa-chevron-right';
            } else {
                show(body);
                btn.setAttribute(
                    'aria-expanded', 'true'
                );
                btn.querySelector('i').className =
                    'fa-solid fa-chevron-down';
                var objHost = body.querySelector(
                    '.og-group-objects'
                );
                if (!objHost.dataset.loaded) {
                    loadGroupObjects(grp, body);
                }
            }
        }

        /* Collapse / expand via chevron button */
        container.querySelectorAll(
            '.og-toggle-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                toggleGroup(btn.dataset.group);
            });
        });

        /* Collapse / expand via header bar click */
        container.querySelectorAll(
            '.at-section-card__header'
        ).forEach(function (header) {
            header.addEventListener('click', function (ev) {
                var target = ev.target;
                if (!target) return;
                /* Ignore clicks on buttons/controls */
                if (target.closest(
                    '.op-section-controls,' +
                    'button,a,input,select,textarea'
                )) return;
                var card = header.closest(
                    '.og-group-section'
                );
                if (card) {
                    toggleGroup(card.dataset.group);
                }
            });
        });

        /* Add objects */
        container.querySelectorAll(
            '.og-add-objects-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                addGroupInput.value = btn.dataset.group;
                addQuery.value = '';
                hide(addBulkResult);
                show(addModal);
                addQuery.focus();
            });
        });

        /* Rename */
        container.querySelectorAll(
            '.og-rename-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                renameOld.value = btn.dataset.group;
                renameInput.value = btn.dataset.group;
                show(renameModal);
                renameInput.focus();
            });
        });

        /* Delete */
        container.querySelectorAll(
            '.og-delete-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                var grp = btn.dataset.group;
                if (!confirm(
                    'Delete group "' + grp + '"' +
                    ' and all its objects?'
                )) return;
                btn.disabled = true;
                postJson(cfg.deleteApiUrl, {
                    profile_id: cfg.profileId,
                    name: grp,
                }).then(function (data) {
                    btn.disabled = false;
                    if (data.success) {
                        loadGroups();
                    } else {
                        alert(data.error ||
                            'Failed to delete group.');
                    }
                }).catch(function () {
                    btn.disabled = false;
                    alert('Network error.');
                });
            });
        });
    }

    /* ================================================================
       Load objects for a single group
       ================================================================ */
    function loadGroupObjects(groupName, bodyEl) {
        var loadingEl2 = bodyEl.querySelector(
            '.og-group-objects-loading'
        );
        var objHost = bodyEl.querySelector(
            '.og-group-objects'
        );
        show(loadingEl2);
        hide(objHost);

        var url = cfg.objectsApiUrl +
            '?profile_id=' +
            encodeURIComponent(cfg.profileId) +
            '&group=' +
            encodeURIComponent(groupName);

        getJson(url).then(function (data) {
            hide(loadingEl2);
            objHost.dataset.loaded = '1';
            if (!data.success) {
                objHost.innerHTML =
                    '<span class="at-muted-hint">' +
                    esc(data.error || 'Error') + '</span>';
                show(objHost);
                return;
            }
            renderGroupObjects(
                groupName, objHost,
                data.objects || [],
                data.can_moderate || false
            );
        }).catch(function () {
            hide(loadingEl2);
            objHost.innerHTML =
                '<span class="at-muted-hint">' +
                'Network error.</span>';
            show(objHost);
        });
    }

    function renderGroupObjects(
        groupName, host, objects, canMod
    ) {
        if (!objects.length) {
            host.innerHTML =
                '<span class="at-muted-hint">' +
                'No visible objects in this group.</span>';
            show(host);
            return;
        }
        var html = '';
        objects.forEach(function (obj) {
            var pageUrl = cfg.objectPageBaseUrl +
                encodeURIComponent(obj.objname);
            html += '<article class="ari-rp-section-card' +
                ' ari-fav-card og-object-card">';
            html += '<div class="ari-rp-section-card__icon">';
            html += '<i class="fa-solid fa-atom"></i>';
            html += '</div>';
            html += '<a href="' + esc(pageUrl) + '"' +
                ' class="ari-rp-section-card__body">';
            html += '<h3>' + esc(obj.objname) + '</h3>';
            html += '<p class="at-muted-hint">' +
                'added by ' + esc(obj.added_by || '?') +
                '</p>';
            html += '</a>';
            if (canMod) {
                html += '<div class="ari-fav-card__actions">';
                html += '<button type="button"' +
                    ' class="ari-btn ari-btn--sm' +
                    ' ari-btn--danger og-remove-obj-btn"' +
                    ' data-group="' + esc(groupName) + '"' +
                    ' data-objname="' +
                    esc(obj.objname) + '"' +
                    ' title="Remove from group">' +
                    '<i class="fa-solid fa-trash"></i>' +
                    '</button>';
                html += '</div>';
            }
            html += '</article>';
        });
        host.innerHTML = html;
        show(host);

        /* Wire remove buttons */
        host.querySelectorAll(
            '.og-remove-obj-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                btn.disabled = true;
                postJson(cfg.removeObjectApiUrl, {
                    profile_id: cfg.profileId,
                    group: btn.dataset.group,
                    objname: btn.dataset.objname,
                }).then(function (data) {
                    btn.disabled = false;
                    if (data.success) {
                        loadGroups();
                    } else {
                        alert(data.error ||
                            'Failed to remove object.');
                    }
                }).catch(function () {
                    btn.disabled = false;
                    alert('Network error.');
                });
            });
        });
    }

    /* ================================================================
       Create group
       ================================================================ */
    if (createBtn) {
        createBtn.addEventListener('click', function () {
            var name = prompt('Enter new group name:');
            if (!name || !name.trim()) return;
            createBtn.disabled = true;
            postJson(cfg.createApiUrl, {
                profile_id: cfg.profileId,
                name: name.trim(),
            }).then(function (data) {
                createBtn.disabled = false;
                if (data.success) {
                    loadGroups();
                } else {
                    alert(data.error ||
                        'Failed to create group.');
                }
            }).catch(function () {
                createBtn.disabled = false;
                alert('Network error.');
            });
        });
    }

    /* ================================================================
       Add objects modal
       ================================================================ */
    function closeAddModal() { hide(addModal); }
    if (addModalClose) {
        addModalClose.addEventListener('click', closeAddModal);
    }
    if (addModal) {
        addModal.addEventListener('click', function (e) {
            if (e.target === addModal) closeAddModal();
        });
    }

    /* Single add */
    function showSingleResult(html, isError) {
        if (!addSingleResult) return;
        addSingleResult.innerHTML = html;
        addSingleResult.style.color = isError
            ? '#c33' : '#2a7';
        show(addSingleResult);
    }

    if (addSingleBtn) {
        addSingleBtn.addEventListener('click', function () {
            var name = addQuery.value.trim();
            var grp = addGroupInput.value;
            if (!name || !grp) return;
            addSingleBtn.disabled = true;
            if (addSingleResult) hide(addSingleResult);
            postJson(cfg.addObjectApiUrl, {
                profile_id: cfg.profileId,
                group: grp,
                objname: name,
            }).then(function (data) {
                addSingleBtn.disabled = false;
                if (data.success) {
                    var msg = 'Added <b>' +
                        esc(data.resolved_objname) +
                        '</b>';
                    if (data.nickname) {
                        msg += ' (alias for <i>' +
                            esc(data.nickname) +
                            '</i>)';
                    }
                    showSingleResult(msg, false);
                    addQuery.value = '';
                    loadGroups();
                } else if (
                    data.candidates &&
                    data.candidates.length
                ) {
                    var parts = [
                        esc(data.error || 'Ambiguous'),
                        ': ',
                    ];
                    data.candidates.forEach(
                        function (c, i) {
                            if (i) parts.push(', ');
                            parts.push(
                                '<a href="#" ' +
                                'class="og-cand" ' +
                                'data-name="' +
                                esc(c) + '">' +
                                esc(c) + '</a>'
                            );
                        }
                    );
                    showSingleResult(
                        parts.join(''), true
                    );
                } else {
                    showSingleResult(
                        esc(
                            data.error ||
                            'Failed to add object.'
                        ),
                        true
                    );
                }
            }).catch(function () {
                addSingleBtn.disabled = false;
                showSingleResult(
                    'Network error.', true
                );
            });
        });
    }

    /* Click on a candidate link fills the input */
    if (addSingleResult) {
        addSingleResult.addEventListener(
            'click', function (e) {
                var el = e.target.closest('.og-cand');
                if (!el) return;
                e.preventDefault();
                addQuery.value = el.dataset.name || '';
                hide(addSingleResult);
            }
        );
    }

    /* Bulk upload */
    if (addBulkBtn) {
        addBulkBtn.addEventListener('click', function () {
            var grp = addGroupInput.value;
            var file = addBulkFile.files[0];
            if (!grp || !file) {
                alert('Select a file first.');
                return;
            }
            addBulkBtn.disabled = true;
            hide(addBulkResult);

            var fd = new FormData();
            fd.append('profile_id', cfg.profileId);
            fd.append('group', grp);
            fd.append('file', file);

            fetch(cfg.addBulkApiUrl, {
                method: 'POST',
                body: fd,
            }).then(function (r) {
                return r.json();
            }).then(function (data) {
                addBulkBtn.disabled = false;
                if (data.success) {
                    var msg = 'Added: ' +
                        (data.added || 0) +
                        ', skipped: ' +
                        (data.skipped || 0);
                    if (
                        data.not_found &&
                        data.not_found.length
                    ) {
                        msg += ', not found: ' +
                            data.not_found.length;
                        msg += '<br><small>' +
                            'Unresolved: ' +
                            data.not_found
                                .map(esc).join(', ') +
                            '</small>';
                    }
                    addBulkResult.innerHTML = msg;
                    show(addBulkResult);
                    loadGroups();
                } else {
                    addBulkResult.textContent =
                        data.error || 'Upload failed.';
                    show(addBulkResult);
                }
            }).catch(function () {
                addBulkBtn.disabled = false;
                addBulkResult.textContent =
                    'Network error.';
                show(addBulkResult);
            });
        });
    }

    /* ================================================================
       Rename modal
       ================================================================ */
    function closeRenameModal() { hide(renameModal); }
    if (renameClose) {
        renameClose.addEventListener(
            'click', closeRenameModal
        );
    }
    if (renameModal) {
        renameModal.addEventListener('click', function (e) {
            if (e.target === renameModal) closeRenameModal();
        });
    }
    if (renameSubmit) {
        renameSubmit.addEventListener('click', function () {
            var oldName = renameOld.value;
            var newName = renameInput.value.trim();
            if (!oldName || !newName) return;
            renameSubmit.disabled = true;
            postJson(cfg.renameApiUrl, {
                profile_id: cfg.profileId,
                old_name: oldName,
                new_name: newName,
            }).then(function (data) {
                renameSubmit.disabled = false;
                if (data.success) {
                    closeRenameModal();
                    loadGroups();
                } else {
                    alert(data.error ||
                        'Failed to rename.');
                }
            }).catch(function () {
                renameSubmit.disabled = false;
                alert('Network error.');
            });
        });
    }

    /* Escape key closes modals */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeAddModal();
            closeRenameModal();
        }
    });

    /* ================================================================
       Filter groups by name
       ================================================================ */
    function applyFilter() {
        if (!container) return;
        var query = (filterInput ? filterInput.value : '')
            .trim().toLowerCase();
        var sections = container.querySelectorAll(
            '.og-group-section'
        );
        var visible = 0;
        sections.forEach(function (sec) {
            var name = (sec.dataset.group || '').toLowerCase();
            if (!query || name.indexOf(query) !== -1) {
                sec.style.display = '';
                visible++;
            } else {
                sec.style.display = 'none';
            }
        });
        if (emptyEl) {
            if (visible === 0 && groupsData.length > 0) {
                emptyEl.textContent =
                    'No groups matching filter.';
                show(emptyEl);
            } else if (groupsData.length === 0) {
                show(emptyEl);
            } else {
                hide(emptyEl);
            }
        }
    }

    if (filterInput) {
        filterInput.addEventListener('input', applyFilter);
    }

    /* ── Initial load ───────────────────────────────────────────── */
    loadGroups();
}());
