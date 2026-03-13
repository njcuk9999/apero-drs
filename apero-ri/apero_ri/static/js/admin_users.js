/* APERO RI – Admin User Management */
(function () {
    'use strict';

    var CONFIG = window.ARI_ADMIN;
    var searchInput = document.getElementById('user-search');
    var searchStatus = document.getElementById('search-status');
    var resultsContainer = document.getElementById('user-results');
    var detailPanel = document.getElementById('user-detail');
    var detailUsername = document.getElementById('detail-username');
    var detailGroupsSummary = document.getElementById('detail-groups-summary');
    var groupsContainer = document.getElementById('detail-groups');
    var groupsNoPerm = document.getElementById('groups-no-perm');
    var instrumentsContainer = document.getElementById('detail-instruments');
    var instrumentsNoPerm = document.getElementById('instruments-no-perm');
    var dangerZone = document.getElementById('danger-zone');
    var deleteModal = document.getElementById('delete-modal');
    var deleteModalUser = document.getElementById('delete-modal-user');
    var btnDeleteUser = document.getElementById('btn-delete-user');
    var btnCloseDetail = document.getElementById('btn-close-detail');
    var btnCancelDelete = document.getElementById('btn-cancel-delete');
    var btnConfirmDelete = document.getElementById('btn-confirm-delete');

    // State
    var searchMeta = {};
    var allUsers = [];
    var selectedUser = null;

    // =====================================================================
    // Load all users on init
    // =====================================================================
    function loadAll() {
        searchStatus.textContent = 'Loading users...';
        fetch(CONFIG.searchUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    searchStatus.textContent = 'Error: ' + (data.error || 'Unknown');
                    return;
                }
                searchMeta = data;
                allUsers = data.users;
                renderFiltered();
            })
            .catch(function () {
                searchStatus.textContent = 'Failed to load users.';
            });
    }

    // =====================================================================
    // Filter (local, instant)
    // =====================================================================
    searchInput.addEventListener('input', function () {
        renderFiltered();
    });

    function renderFiltered() {
        var q = searchInput.value.trim().toLowerCase();
        var filtered = allUsers;
        if (q) {
            filtered = allUsers.filter(function (u) {
                return u.username.toLowerCase().indexOf(q) !== -1;
            });
        }
        renderResults(filtered);
    }

    function renderResults(users) {
        resultsContainer.innerHTML = '';
        if (users.length === 0) {
            searchStatus.textContent = 'No users found.';
            return;
        }
        searchStatus.textContent = users.length + ' user(s) found.';

        users.forEach(function (user) {
            var card = document.createElement('div');
            card.className = 'ari-user-result-card';
            card.innerHTML =
                '<div class="ari-user-result-card__avatar"><i class="fa-solid fa-user"></i></div>' +
                '<div class="ari-user-result-card__info">' +
                '<div class="ari-user-result-card__name">' + escapeHtml(user.username) + '</div>' +
                '<div class="ari-user-result-card__groups">' + escapeHtml(user.groups.join(', ') || 'No groups') + '</div>' +
                '</div>';
            card.addEventListener('click', function () {
                openDetail(user);
            });
            resultsContainer.appendChild(card);
        });
    }

    // =====================================================================
    // Detail panel
    // =====================================================================
    btnCloseDetail.addEventListener('click', closeDetail);

    function openDetail(user) {
        selectedUser = user;
        detailPanel.style.display = '';
        detailUsername.textContent = user.username;
        detailGroupsSummary.textContent = user.groups.join(', ') || 'No groups';

        renderGroups(user);
        renderInstruments(user);
        renderDangerZone(user);

        // Scroll into view
        detailPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function closeDetail() {
        detailPanel.style.display = 'none';
        selectedUser = null;
    }

    // =====================================================================
    // Groups toggle cards
    // =====================================================================
    function renderGroups(user) {
        groupsContainer.innerHTML = '';
        var allGroups = searchMeta.all_groups || [];
        var canAdd = new Set(searchMeta.can_add_groups || []);
        var inheritedMap = searchMeta.inherited_map || {};
        var userGroups = new Set(user.groups || []);

        if (canAdd.size === 0) {
            groupsNoPerm.style.display = '';
            return;
        }
        groupsNoPerm.style.display = 'none';

        // Compute encompassed groups: groups that are inherited by any
        // currently-enabled higher group
        var encompassed = computeEncompassed(userGroups, inheritedMap);

        allGroups.forEach(function (group) {
            var isEnabled = userGroups.has(group);
            var canManage = canAdd.has(group);
            var isEncompassed = encompassed.has(group) && !userGroups.has(group);
            var isEncompassedEnabled = encompassed.has(group) && userGroups.has(group);

            var card = document.createElement('span');
            var stateClass, iconHtml, tooltip;

            if (!canManage) {
                // No permission — locked
                stateClass = 'ari-toggle-card--locked';
                iconHtml = isEnabled
                    ? '<i class="fa-solid fa-check ari-toggle-card__icon"></i>'
                    : '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>';
                tooltip = 'You do not have permission to manage group: ' + group;
            } else if (isEncompassedEnabled) {
                // Encompassed by a higher group and enabled — grey it out
                stateClass = 'ari-toggle-card--encompassed';
                iconHtml = '<i class="fa-solid fa-check ari-toggle-card__icon"></i>';
                tooltip = 'Already encompassed by a higher-level group';
            } else if (isEncompassed) {
                // Encompassed by a higher group but not directly enabled
                stateClass = 'ari-toggle-card--encompassed';
                iconHtml = '<i class="fa-solid fa-minus ari-toggle-card__icon"></i>';
                tooltip = 'Already included via a higher-level group';
            } else if (isEnabled) {
                stateClass = 'ari-toggle-card--enabled';
                iconHtml = '<i class="fa-solid fa-check ari-toggle-card__icon"></i>';
                tooltip = 'Click to disable';
            } else {
                stateClass = 'ari-toggle-card--disabled';
                iconHtml = '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>';
                tooltip = 'Click to enable';
            }

            card.className = 'ari-toggle-card ' + stateClass;
            card.innerHTML = iconHtml + ' ' + escapeHtml(group);
            card.title = tooltip;
            card.setAttribute('data-group', group);

            if (canManage && !isEncompassed && !isEncompassedEnabled) {
                card.addEventListener('click', function () {
                    toggleGroup(user, group);
                });
            }

            groupsContainer.appendChild(card);
        });
    }

    function computeEncompassed(enabledGroups, inheritedMap) {
        var encompassed = new Set();
        enabledGroups.forEach(function (g) {
            var inherited = inheritedMap[g] || [];
            inherited.forEach(function (sub) {
                encompassed.add(sub);
            });
        });
        return encompassed;
    }

    function toggleGroup(user, group) {
        var groups = user.groups.slice();
        var idx = groups.indexOf(group);
        if (idx >= 0) {
            groups.splice(idx, 1);
        } else {
            groups.push(group);
        }

        fetch(CONFIG.updateGroupsUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user.username, groups: groups })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    user.groups = groups;
                    detailGroupsSummary.textContent = groups.join(', ') || 'No groups';
                    renderGroups(user);
                    updateResultCard(user);
                    showToast('Groups updated', 'success');
                } else {
                    showToast('Error: ' + (data.error || 'Failed'), 'error');
                }
            })
            .catch(function () {
                showToast('Network error', 'error');
            });
    }

    // =====================================================================
    // Instruments toggle cards
    // =====================================================================
    function renderInstruments(user) {
        instrumentsContainer.innerHTML = '';
        var allInstruments = searchMeta.all_instruments || [];
        var canAddInstrument = searchMeta.can_add_instrument;
        var editorUsername = searchMeta.editor_username;
        var editorInstruments = new Set(searchMeta.editor_instruments || []);
        var userInstruments = new Set(user.instruments || []);

        // Can manage if: has manage instrument permission, OR target is self
        var canManageForUser = canAddInstrument || (user.username === editorUsername);

        if (!canManageForUser) {
            instrumentsNoPerm.style.display = '';
            instrumentsContainer.innerHTML = '';
            // Still show instruments as locked cards
            allInstruments.forEach(function (inst) {
                var isEnabled = userInstruments.has(inst);
                var card = document.createElement('span');
                card.className = 'ari-toggle-card ari-toggle-card--locked';
                card.innerHTML = (isEnabled
                    ? '<i class="fa-solid fa-check ari-toggle-card__icon"></i>'
                    : '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>') +
                    ' ' + escapeHtml(inst);
                card.title = 'You do not have permission to manage instruments for this user';
                instrumentsContainer.appendChild(card);
            });
            return;
        }
        instrumentsNoPerm.style.display = 'none';

        // If not global manage instrument perm, only show editor's own instruments
        var visibleInstruments = canAddInstrument
            ? allInstruments
            : allInstruments.filter(function (inst) {
                return editorInstruments.has(inst);
            });

        visibleInstruments.forEach(function (inst) {
            var isEnabled = userInstruments.has(inst);
            var card = document.createElement('span');

            if (isEnabled) {
                card.className = 'ari-toggle-card ari-toggle-card--enabled';
                card.innerHTML = '<i class="fa-solid fa-check ari-toggle-card__icon"></i> ' +
                    escapeHtml(inst);
                card.title = 'Click to disable';
            } else {
                card.className = 'ari-toggle-card ari-toggle-card--disabled';
                card.innerHTML = '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i> ' +
                    escapeHtml(inst);
                card.title = 'Click to enable';
            }

            card.addEventListener('click', function () {
                toggleInstrument(user, inst);
            });
            instrumentsContainer.appendChild(card);
        });
    }

    function toggleInstrument(user, instrument) {
        var instruments = (user.instruments || []).slice();
        var idx = instruments.indexOf(instrument);
        if (idx >= 0) {
            instruments.splice(idx, 1);
        } else {
            instruments.push(instrument);
        }

        fetch(CONFIG.updateInstrumentsUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user.username, instruments: instruments })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    user.instruments = instruments;
                    renderInstruments(user);
                    showToast('Instruments updated', 'success');
                } else {
                    showToast('Error: ' + (data.error || 'Failed'), 'error');
                }
            })
            .catch(function () {
                showToast('Network error', 'error');
            });
    }

    // =====================================================================
    // Danger zone / deletion
    // =====================================================================
    function renderDangerZone(user) {
        // Show danger zone only if editor can delete this user
        var canAdd = new Set(searchMeta.can_add_groups || []);
        var userGroups = user.groups || [];
        var editorUsername = searchMeta.editor_username;

        // Cannot delete yourself
        if (user.username === editorUsername) {
            dangerZone.style.display = 'none';
            return;
        }

        // Must have manage.group.{group} for ALL of the user's groups
        var canDelete = userGroups.length > 0 && userGroups.every(function (g) {
            return canAdd.has(g);
        });

        dangerZone.style.display = canDelete ? '' : 'none';
    }

    btnDeleteUser.addEventListener('click', function () {
        if (!selectedUser) return;
        deleteModalUser.textContent = selectedUser.username;
        deleteModal.style.display = '';
    });

    btnCancelDelete.addEventListener('click', function () {
        deleteModal.style.display = 'none';
    });

    deleteModal.addEventListener('click', function (e) {
        if (e.target === deleteModal) {
            deleteModal.style.display = 'none';
        }
    });

    btnConfirmDelete.addEventListener('click', function () {
        if (!selectedUser) return;
        var username = selectedUser.username;

        fetch(CONFIG.deleteUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                deleteModal.style.display = 'none';
                if (data.success) {
                    showToast('User "' + username + '" deleted', 'success');
                    closeDetail();
                    // Reload all users to refresh list
                    loadAll();
                } else {
                    showToast('Error: ' + (data.error || 'Failed'), 'error');
                }
            })
            .catch(function () {
                deleteModal.style.display = 'none';
                showToast('Network error', 'error');
            });
    });

    // =====================================================================
    // Helpers
    // =====================================================================
    function updateResultCard(user) {
        // Update the groups text on the result card
        var cards = resultsContainer.querySelectorAll('.ari-user-result-card');
        cards.forEach(function (card) {
            var nameEl = card.querySelector('.ari-user-result-card__name');
            if (nameEl && nameEl.textContent === user.username) {
                var groupsEl = card.querySelector('.ari-user-result-card__groups');
                if (groupsEl) {
                    groupsEl.textContent = user.groups.join(', ') || 'No groups';
                }
            }
        });
    }

    function showToast(message, type) {
        var toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = 'ari-toast ari-toast--' + (type || 'success');
        toast.style.display = '';
        toast.style.opacity = '1';
        setTimeout(function () {
            toast.style.opacity = '0';
            setTimeout(function () { toast.style.display = 'none'; }, 300);
        }, 3000);
    }

    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    // =====================================================================
    // Init – load all users
    // =====================================================================
    loadAll();
})();
