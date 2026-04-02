/* APERO RI – Admin User Management */
(function () {
    'use strict';

    var CONFIG = window.ARI_ADMIN;

    // Fallback precedence (used only if API metadata is unavailable)
    var GROUP_PRECEDENCE_FALLBACK = ['super_admin', 'admin', 'moderator', 'developer', 'monitor', 'general', 'public'];

    // =========================================================================
    // DOM refs
    // =========================================================================
    var tabNew            = document.getElementById('um-tab-new');
    var tabCurrent        = document.getElementById('um-tab-current');
    var panelNew          = document.getElementById('um-new');
    var panelCurrent      = document.getElementById('um-current');
    var newBanner         = document.getElementById('um-new-banner');
    var newCountEl        = document.getElementById('um-new-count');
    var newBadge          = document.getElementById('um-new-badge');
    var currentBadge      = document.getElementById('um-current-badge');
    var newResults        = document.getElementById('um-new-results');
    var newEmpty          = document.getElementById('um-new-empty');
    var searchInput       = document.getElementById('user-search');
    var searchStatus      = document.getElementById('search-status');
    var currentResults    = document.getElementById('um-current-results');
    var groupFilterWrap   = document.getElementById('um-group-filter');
    var detailPanel       = document.getElementById('user-detail');
    var detailAvatar      = document.getElementById('detail-avatar');
    var detailUsername    = document.getElementById('detail-username');
    var detailGroupsSummary = document.getElementById('detail-groups-summary');
    var groupsContainer   = document.getElementById('detail-groups');
    var groupsNoPerm      = document.getElementById('groups-no-perm');
    var instrumentsContainer = document.getElementById('detail-instruments');
    var instrumentsNoPerm = document.getElementById('instruments-no-perm');
    var dangerZone        = document.getElementById('danger-zone');
    var deleteModal       = document.getElementById('delete-modal');
    var deleteModalUser   = document.getElementById('delete-modal-user');
    var btnDeleteUser     = document.getElementById('btn-delete-user');
    var btnCloseDetail    = document.getElementById('btn-close-detail');
    var btnCancelDelete   = document.getElementById('btn-cancel-delete');
    var btnConfirmDelete  = document.getElementById('btn-confirm-delete');

    // =========================================================================
    // State
    // =========================================================================
    var searchMeta        = {};
    var allUsers          = [];
    var newMembers        = [];
    var currentMembers    = [];
    var selectedUser      = null;
    var openedAsNewMember = false;
    var activeGroupFilter = null;   // null = show all

    // =========================================================================
    // Utility
    // =========================================================================
    function isNewMember(user) {
        var g = user.groups || [];
        return g.length === 0 || (g.length === 1 && g[0] === 'public');
    }

    function getGroupOrder() {
        var ordered = (searchMeta && Array.isArray(searchMeta.all_groups) && searchMeta.all_groups.length)
            ? searchMeta.all_groups.slice()
            : GROUP_PRECEDENCE_FALLBACK.slice();
        if (ordered.indexOf('public') === -1) {
            ordered.push('public');
        }
        return ordered;
    }

    function getHighestGroup(user) {
        var groups = new Set(user.groups || []);
        var precedence = getGroupOrder();
        for (var i = 0; i < precedence.length; i++) {
            if (groups.has(precedence[i])) return precedence[i];
        }
        return 'public';
    }

    function getGroupStyle(groupName) {
        var precedence = getGroupOrder();
        var idx = precedence.indexOf(groupName);
        if (idx < 0) idx = precedence.length - 1;
        var hue = (210 + idx * 37) % 360;

        return {
            cardBg: 'hsl(' + hue + ', 72%, 95%)',
            cardBorder: 'hsl(' + hue + ', 42%, 72%)',
            avatarBg: 'hsl(' + hue + ', 52%, 44%)',
            avatarFg: '#ffffff'
        };
    }

    function escapeHtml(str) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(str)));
        return d.innerHTML;
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

    // =========================================================================
    // Tab switching
    // =========================================================================
    function activateTab(name) {
        if (name === 'new') {
            tabNew.classList.add('ari-sg-tab--active');
            tabNew.setAttribute('aria-selected', 'true');
            tabCurrent.classList.remove('ari-sg-tab--active');
            tabCurrent.setAttribute('aria-selected', 'false');
            panelNew.style.display = '';
            panelCurrent.style.display = 'none';
        } else {
            tabCurrent.classList.add('ari-sg-tab--active');
            tabCurrent.setAttribute('aria-selected', 'true');
            tabNew.classList.remove('ari-sg-tab--active');
            tabNew.setAttribute('aria-selected', 'false');
            panelCurrent.style.display = '';
            panelNew.style.display = 'none';
        }
        closeDetail();
    }

    tabNew.addEventListener('click', function () { activateTab('new'); });
    tabCurrent.addEventListener('click', function () { activateTab('current'); });

    // =========================================================================
    // Load data
    // =========================================================================
    function loadAll() {
        searchStatus.textContent = 'Loading…';
        fetch(CONFIG.searchUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    searchStatus.textContent = 'Error: ' + (data.error || 'Unknown');
                    return;
                }
                searchMeta = data;
                allUsers = data.users;
                rebuildUserLists();
                renderGroupFilterPills();
            })
            .catch(function () {
                searchStatus.textContent = 'Failed to load users.';
            });
    }

    function rebuildUserLists() {
        newMembers     = allUsers.filter(isNewMember);
        currentMembers = allUsers.filter(function (u) { return !isNewMember(u); });
        if (currentBadge) currentBadge.textContent = currentMembers.length;
        renderNewMembersTab();
        renderCurrentMembersFiltered();
    }

    // =========================================================================
    // New Members tab
    // =========================================================================
    function renderNewMembersTab() {
        var count = newMembers.length;
        newBadge.textContent = count;
        newBadge.classList.toggle('ari-um-badge--zero', count === 0);

        if (count > 0) {
            newCountEl.textContent = count;
            newBanner.style.display = '';
            newResults.style.display = '';
            newEmpty.style.display = 'none';
        } else {
            newBanner.style.display = 'none';
            newResults.style.display = 'none';
            newEmpty.style.display = '';
        }

        newResults.innerHTML = '';
        newMembers.forEach(function (user) {
            newResults.appendChild(buildUserCard(user, true));
        });
    }

    // =========================================================================
    // Current Members tab
    // =========================================================================
    function renderGroupFilterPills() {
        groupFilterWrap.innerHTML = '';
        var allGroups = searchMeta.all_groups || [];

        var allPill = document.createElement('button');
        allPill.type = 'button';
        allPill.className = 'ari-um-filter-pill' +
            (activeGroupFilter === null ? ' ari-um-filter-pill--active' : '');
        allPill.textContent = 'All';
        allPill.setAttribute('aria-pressed', activeGroupFilter === null ? 'true' : 'false');
        allPill.addEventListener('click', function () {
            activeGroupFilter = null;
            renderGroupFilterPills();
            renderCurrentMembersFiltered();
        });
        groupFilterWrap.appendChild(allPill);

        allGroups.forEach(function (group) {
            var pill = document.createElement('button');
            pill.type = 'button';
            var isActive = (activeGroupFilter === group);
            pill.className = 'ari-um-filter-pill ari-um-filter-pill--' + group +
                (isActive ? ' ari-um-filter-pill--active' : '');
            pill.textContent = group;
            pill.setAttribute('aria-pressed', isActive ? 'true' : 'false');
            pill.addEventListener('click', function () {
                activeGroupFilter = (activeGroupFilter === group) ? null : group;
                renderGroupFilterPills();
                renderCurrentMembersFiltered();
            });
            groupFilterWrap.appendChild(pill);
        });
    }

    searchInput.addEventListener('input', renderCurrentMembersFiltered);

    function renderCurrentMembersFiltered() {
        var q = searchInput.value.trim().toLowerCase();
        var filtered = currentMembers;

        if (q) {
            filtered = filtered.filter(function (u) {
                return u.username.toLowerCase().indexOf(q) !== -1 ||
                    ((u.first_names || '') + ' ' + (u.last_name || '')).toLowerCase().indexOf(q) !== -1;
            });
        }

        if (activeGroupFilter !== null) {
            filtered = filtered.filter(function (u) {
                return (u.groups || []).indexOf(activeGroupFilter) !== -1;
            });
        }

        searchStatus.textContent = filtered.length + ' member(s) found.';
        currentResults.innerHTML = '';
        filtered.forEach(function (user) {
            currentResults.appendChild(buildUserCard(user, false));
        });
    }

    // =========================================================================
    // User card builder
    // =========================================================================
    function buildUserCard(user, isNew) {
        var card = document.createElement('div');
        var highest = getHighestGroup(user);
        var groupStyle = getGroupStyle(highest);
        card.className = 'ari-user-result-card';
        card.dataset.group = highest;
        card.style.background = groupStyle.cardBg;
        card.style.borderColor = groupStyle.cardBorder;

        var avatar = document.createElement('div');
        avatar.className = 'ari-user-result-card__avatar';
        avatar.style.background = groupStyle.avatarBg;
        avatar.style.color = groupStyle.avatarFg;
        avatar.innerHTML = '<i class="fa-solid fa-user"></i>';
        card.appendChild(avatar);

        var info = document.createElement('div');
        info.className = 'ari-user-result-card__info';

        var nameLine = document.createElement('div');
        nameLine.className = 'ari-user-result-card__name';
        nameLine.textContent = user.username;
        if (user.first_names || user.last_name) {
            var nameDetail = document.createElement('span');
            nameDetail.className = 'ari-user-result-card__fullname';
            nameDetail.textContent = ' (' +
                [user.first_names, user.last_name].filter(Boolean).join(' ') + ')';
            nameLine.appendChild(nameDetail);
        }
        info.appendChild(nameLine);

        var groupLine = document.createElement('div');
        groupLine.className = 'ari-user-result-card__groups';
        groupLine.textContent = isNew
            ? 'Awaiting assignment'
            : ((user.groups || []).join(', ') || 'No groups');
        info.appendChild(groupLine);

        card.appendChild(info);

        if (isNew) {
            var badge = document.createElement('span');
            badge.className = 'ari-um-new-pill';
            badge.textContent = 'New';
            card.appendChild(badge);
        }

        card.addEventListener('click', function () { openDetail(user, isNew); });
        return card;
    }

    // =========================================================================
    // Detail panel
    // =========================================================================
    btnCloseDetail.addEventListener('click', function () {
        if (openedAsNewMember && selectedUser && isNewMember(selectedUser)) {
            if (!confirm(
                'This user (' + selectedUser.username + ') has not been assigned ' +
                'groups or instruments yet. Close the panel anyway?'
            )) {
                return;
            }
        }
        closeDetail();
    });

    // Warn on page leave if a new-member panel is open and unchanged
    window.addEventListener('beforeunload', function (e) {
        if (openedAsNewMember && selectedUser && isNewMember(selectedUser)) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    function openDetail(user, fromNewTab) {
        selectedUser      = user;
        openedAsNewMember = !!fromNewTab;

        // Avatar colour matches card colour
        var highest = getHighestGroup(user);
        var groupStyle = getGroupStyle(highest);
        detailAvatar.className = 'ari-user-detail__avatar';
        detailAvatar.dataset.group = highest;
        detailAvatar.style.background = groupStyle.avatarBg;
        detailAvatar.style.color = groupStyle.avatarFg;

        var displayName = user.username;
        if (user.first_names || user.last_name) {
            displayName += ' — ' + [user.first_names, user.last_name].filter(Boolean).join(' ');
        }
        detailUsername.textContent = displayName;
        detailGroupsSummary.textContent = (user.groups || []).join(', ') || 'No groups assigned';

        renderGroups(user);
        renderInstruments(user);
        renderDangerZone(user);

        detailPanel.style.display = '';
        detailPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function closeDetail() {
        detailPanel.style.display = 'none';
        selectedUser      = null;
        openedAsNewMember = false;
    }

    // =========================================================================
    // Groups
    // =========================================================================
    function renderGroups(user) {
        groupsContainer.innerHTML = '';
        var allGroups    = searchMeta.all_groups || [];
        var canAdd       = new Set(searchMeta.can_add_groups || []);
        var inheritedMap = searchMeta.inherited_map || {};
        var userGroups   = new Set(user.groups || []);
        var editorIsAdmin = !!searchMeta.editor_is_admin;
        var editorIsSuperAdmin = !!searchMeta.editor_is_super_admin;
        var targetIsAdmin = userGroups.has('admin') || userGroups.has('super_admin');

        if (targetIsAdmin && !editorIsSuperAdmin) {
            groupsNoPerm.style.display = '';
            allGroups.forEach(function (group) {
                var card = document.createElement('span');
                card.className = 'ari-toggle-card ari-toggle-card--locked';
                card.innerHTML = (userGroups.has(group)
                    ? '<i class="fa-solid fa-check ari-toggle-card__icon"></i>'
                    : '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>') +
                    ' ' + escapeHtml(group);
                card.title = 'Admin-level accounts cannot be edited from this page';
                groupsContainer.appendChild(card);
            });
            return;
        }

        if (canAdd.size === 0 && !editorIsAdmin) {
            groupsNoPerm.style.display = '';
            return;
        }
        groupsNoPerm.style.display = 'none';

        var encompassed = computeEncompassed(userGroups, inheritedMap);

        allGroups.forEach(function (group) {
            var isEnabled          = userGroups.has(group);
            var canManage          = canAdd.has(group) || (editorIsAdmin && group !== 'admin' && group !== 'super_admin');
            var isEncompassed      = encompassed.has(group) && !isEnabled;
            var isEncompassedOn    = encompassed.has(group) && isEnabled;

            var card = document.createElement('span');
            var stateClass, iconHtml, tooltip;

            if ((group === 'admin' || group === 'super_admin') && !editorIsSuperAdmin) {
                stateClass = isEnabled
                    ? 'ari-toggle-card--locked'
                    : 'ari-toggle-card--disabled';
                iconHtml   = isEnabled
                    ? '<i class="fa-solid fa-check ari-toggle-card__icon"></i>'
                    : '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>';
                tooltip = isEnabled
                    ? 'Admin-level groups cannot be edited from this page'
                    : 'Admin-level groups cannot be assigned from this page';
            } else if (!canManage) {
                stateClass = 'ari-toggle-card--locked';
                iconHtml   = isEnabled
                    ? '<i class="fa-solid fa-check ari-toggle-card__icon"></i>'
                    : '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>';
                tooltip = 'No permission to manage group: ' + group;
            } else if (isEncompassedOn) {
                stateClass = 'ari-toggle-card--encompassed';
                iconHtml   = '<i class="fa-solid fa-check ari-toggle-card__icon"></i>';
                tooltip = 'Already encompassed by a higher-level group';
            } else if (isEncompassed) {
                stateClass = 'ari-toggle-card--encompassed';
                iconHtml   = '<i class="fa-solid fa-minus ari-toggle-card__icon"></i>';
                tooltip = 'Already included via a higher-level group';
            } else if (isEnabled) {
                stateClass = 'ari-toggle-card--enabled';
                iconHtml   = '<i class="fa-solid fa-check ari-toggle-card__icon"></i>';
                tooltip = 'Click to remove';
            } else {
                stateClass = 'ari-toggle-card--disabled';
                iconHtml   = '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>';
                tooltip = 'Click to add';
            }

            card.className = 'ari-toggle-card ' + stateClass;
            card.innerHTML = iconHtml + ' ' + escapeHtml(group);
            card.title     = tooltip;

            if (canManage && !isEncompassed && !isEncompassedOn) {
                card.addEventListener('click', function () { toggleGroup(user, group); });
            }
            groupsContainer.appendChild(card);
        });
    }

    function computeEncompassed(enabledGroups, inheritedMap) {
        var enc = new Set();
        enabledGroups.forEach(function (g) {
            (inheritedMap[g] || []).forEach(function (sub) { enc.add(sub); });
        });
        return enc;
    }

    function toggleGroup(user, group) {
        var groups = (user.groups || []).slice();
        var idx = groups.indexOf(group);
        if (idx >= 0) groups.splice(idx, 1); else groups.push(group);

        fetch(CONFIG.updateGroupsUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user.username, groups: groups })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) {
                showToast('Error: ' + (data.error || 'Failed'), 'error');
                return;
            }
            var wasNew = isNewMember(user);
            user.groups = groups;
            var isNowNew = isNewMember(user);

            // Summary and detail panel
            detailGroupsSummary.textContent = groups.join(', ') || 'No groups assigned';
            renderGroups(user);

            // If graduated from new-member, clear flag and rebuild lists
            if (wasNew && !isNowNew) {
                openedAsNewMember = false;
            }
            rebuildUserLists();
            showToast('Groups updated', 'success');
        })
        .catch(function () { showToast('Network error', 'error'); });
    }

    // =========================================================================
    // Instruments
    // =========================================================================
    function renderInstruments(user) {
        instrumentsContainer.innerHTML = '';
        var allInstruments   = searchMeta.all_instruments || [];
        var canAddInstrument = searchMeta.can_add_instrument;
        var canAddInstrumentGroups = new Set(searchMeta.can_add_instrument_groups || []);
        var editorUsername   = searchMeta.editor_username;
        var editorIsAdmin    = !!searchMeta.editor_is_admin;
        var editorIsSuperAdmin = !!searchMeta.editor_is_super_admin;
        var editorInstruments = new Set(searchMeta.editor_instruments || []);
        var userInstruments  = new Set(user.instruments || []);
        var userGroups       = new Set(user.groups || []);
        var targetIsAdmin = (user.groups || []).indexOf('admin') !== -1
            || (user.groups || []).indexOf('super_admin') !== -1;

        var canManageTargetGroups = true;
        userGroups.forEach(function (group) {
            if (!canAddInstrumentGroups.has(group)) {
                canManageTargetGroups = false;
            }
        });

        var canManage = (!targetIsAdmin || editorIsSuperAdmin) &&
            (canAddInstrument || editorIsAdmin || canManageTargetGroups ||
                (user.username === editorUsername));

        if (!canManage) {
            instrumentsNoPerm.style.display = '';
            allInstruments.forEach(function (inst) {
                var card = document.createElement('span');
                card.className = 'ari-toggle-card ari-toggle-card--locked';
                card.innerHTML = (userInstruments.has(inst)
                    ? '<i class="fa-solid fa-check ari-toggle-card__icon"></i>'
                    : '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>') +
                    ' ' + escapeHtml(inst);
                card.title = 'No permission to manage instruments for this user';
                instrumentsContainer.appendChild(card);
            });
            return;
        }
        instrumentsNoPerm.style.display = 'none';

        var visible = (canAddInstrument || editorIsAdmin || canManageTargetGroups)
            ? allInstruments
            : allInstruments.filter(function (i) { return editorInstruments.has(i); });

        visible.forEach(function (inst) {
            var isEnabled = userInstruments.has(inst);
            var card = document.createElement('span');
            card.className = 'ari-toggle-card ' +
                (isEnabled ? 'ari-toggle-card--enabled' : 'ari-toggle-card--disabled');
            card.innerHTML = (isEnabled
                ? '<i class="fa-solid fa-check ari-toggle-card__icon"></i>'
                : '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>') +
                ' ' + escapeHtml(inst);
            card.title = isEnabled ? 'Click to remove' : 'Click to add';
            card.addEventListener('click', function () { toggleInstrument(user, inst); });
            instrumentsContainer.appendChild(card);
        });
    }

    function toggleInstrument(user, instrument) {
        var instruments = (user.instruments || []).slice();
        var idx = instruments.indexOf(instrument);
        if (idx >= 0) instruments.splice(idx, 1); else instruments.push(instrument);

        fetch(CONFIG.updateInstrumentsUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user.username, instruments: instruments })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) {
                showToast('Error: ' + (data.error || 'Failed'), 'error');
                return;
            }
            user.instruments = instruments;
            renderInstruments(user);
            showToast('Instruments updated', 'success');
        })
        .catch(function () { showToast('Network error', 'error'); });
    }

    // =========================================================================
    // Danger zone / delete
    // =========================================================================
    function renderDangerZone(user) {
        var canAdd  = new Set(searchMeta.can_add_groups || []);
        var groups  = user.groups || [];
        if (user.username === searchMeta.editor_username) {
            dangerZone.style.display = 'none';
            return;
        }
        var canDelete = groups.length > 0 && groups.every(function (g) { return canAdd.has(g); });
        dangerZone.style.display = canDelete ? '' : 'none';
    }

    btnDeleteUser.addEventListener('click', function () {
        if (!selectedUser) return;
        deleteModalUser.textContent = selectedUser.username;
        deleteModal.style.display = '';
    });

    btnCancelDelete.addEventListener('click', function () { deleteModal.style.display = 'none'; });

    deleteModal.addEventListener('click', function (e) {
        if (e.target === deleteModal) deleteModal.style.display = 'none';
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
                allUsers = allUsers.filter(function (u) { return u.username !== username; });
                rebuildUserLists();
            } else {
                showToast('Error: ' + (data.error || 'Failed'), 'error');
            }
        })
        .catch(function () {
            deleteModal.style.display = 'none';
            showToast('Network error', 'error');
        });
    });

    // =========================================================================
    // Init
    // =========================================================================
    loadAll();
})();
