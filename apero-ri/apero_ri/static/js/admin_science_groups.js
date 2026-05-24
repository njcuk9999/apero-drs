/* =========================================================================
   Admin Science Groups page logic — dual-list transfer with drag-and-drop
   ========================================================================= */
(function () {
    'use strict';

    if (window.__ARI_SCI_GROUPS_INIT__) {
        console.warn('admin_science_groups.js duplicate init ignored');
        return;
    }
    window.__ARI_SCI_GROUPS_INIT__ = true;

    function init() {
    var cfg = window.ARI_SCI_GROUPS;

    /* -- DOM refs -------------------------------------------------------- */
    var tabsContainer = document.getElementById('instrument-tabs');
    var sgHealth = document.getElementById('sg-health');
    var sgHealthHeadline = document.getElementById('sg-health-headline');
    var sgHealthDetails = document.getElementById('sg-health-details');
    var workspace = document.getElementById('sg-workspace');
    var emptyState = document.getElementById('sg-empty');
    var actionsBar = document.getElementById('sg-actions');
    var selectPrompt = document.getElementById('sg-select-prompt');

    var groupFilter = document.getElementById('group-filter');
    var groupList = document.getElementById('group-list');
    var btnAddGroup = document.getElementById('btn-add-group');

    /* Transfer list DOM refs */
    var runidSection = document.getElementById('runid-section');
    var runidAvailFilter = document.getElementById('runid-avail-filter');
    var runidAddedFilter = document.getElementById('runid-added-filter');
    var runidAvailable = document.getElementById('runid-available');
    var runidAdded = document.getElementById('runid-added');
    var runidCount = document.getElementById('runid-count');
    var runidAvailCount = document.getElementById('runid-avail-count');
    var runidAddedCount = document.getElementById('runid-added-count');
    var btnRefreshRunIds = document.getElementById('btn-refresh-runids');
    var btnGlobalIo = document.getElementById('btn-global-io');
    var globalIoModal = document.getElementById('global-io-modal');
    var globalIoKind = document.getElementById('global-io-kind');
    var globalIoSelection = document.getElementById('global-io-selection');
    var globalIoMode = document.getElementById('global-io-mode');
    var globalIoFile = document.getElementById('global-io-file');
    var btnGlobalExport = document.getElementById('btn-global-export');
    var btnGlobalImport = document.getElementById('btn-global-import');
    var btnGlobalIoClose = document.getElementById('btn-global-io-close');

    var groupIoModal = document.getElementById('group-io-modal');
    var groupIoSelectedName = document.getElementById(
        'group-io-selected-name');
    var groupIoMode = document.getElementById('group-io-mode');
    var groupIoFile = document.getElementById('group-io-file');
    var btnGroupIo = document.getElementById('btn-group-io');
    var btnGroupIoTop = document.getElementById('btn-group-io-top');
    var btnGroupExport = document.getElementById('btn-group-export');
    var btnGroupImport = document.getElementById('btn-group-import');
    var btnGroupIoClose = document.getElementById('btn-group-io-close');
    var btnAddAllRunIds = document.getElementById('btn-add-all-runids');

    var userSection = document.getElementById('user-section');
    var userAvailFilter = document.getElementById('user-avail-filter');
    var userAddedFilter = document.getElementById('user-added-filter');
    var userAvailable = document.getElementById('user-available');
    var userAdded = document.getElementById('user-added');
    var userCount = document.getElementById('user-count');
    var userAvailCount = document.getElementById('user-avail-count');
    var userAddedCount = document.getElementById('user-added-count');
    var btnAddAllUsers = document.getElementById('btn-add-all-users');

    var btnSave = document.getElementById('btn-save-group');
    var btnDelete = document.getElementById('btn-delete-group');
    var savingOverlay = document.getElementById('sg-saving-overlay');

    var createModal = document.getElementById('create-modal');
    var newGroupName = document.getElementById('new-group-name');
    var createError = document.getElementById('create-error');
    var btnCancelCreate = document.getElementById('btn-cancel-create');
    var btnConfirmCreate = document.getElementById('btn-confirm-create');

    var deleteModal = document.getElementById('delete-modal');
    var deleteModalName = document.getElementById('delete-modal-name');
    var btnCancelDelete = document.getElementById('btn-cancel-delete');
    var btnConfirmDelete = document.getElementById('btn-confirm-delete');

    var toast = document.getElementById('toast');

    /* -- State ----------------------------------------------------------- */
    var currentInstrument = null;
    var currentGroup = null;
    var allGroups = [];
    var allRunIds = [];
    var runIdLabels = {};
    var allUsers = [];
    var selectedRunIds = [];
    var selectedUsers = [];
    var baselineGroups = {};
    var draftGroups = {};

    var LAZY_BATCH = 80;

    function makeGroupKey(instrument, groupName) {
        return String(instrument || '').trim() + '||' +
            String(groupName || '').trim();
    }

    function normalizeValues(values) {
        var uniq = Object.create(null);
        var out = [];
        (Array.isArray(values) ? values : []).forEach(function (item) {
            var value = String(item || '').trim();
            if (!value || uniq[value]) return;
            uniq[value] = true;
            out.push(value);
        });
        out.sort();
        return out;
    }

    function valuesEqual(a, b) {
        var left = normalizeValues(a);
        var right = normalizeValues(b);
        if (left.length !== right.length) return false;
        var i;
        for (i = 0; i < left.length; i += 1) {
            if (left[i] !== right[i]) return false;
        }
        return true;
    }

    function hasAnyDrafts() {
        return Object.keys(draftGroups).length > 0;
    }

    function isCurrentSelectionDirty() {
        if (!currentInstrument || !currentGroup) {
            return false;
        }
        var key = makeGroupKey(currentInstrument, currentGroup);
        var base = baselineGroups[key] || { run_ids: [], users: [] };
        return !valuesEqual(selectedRunIds, base.run_ids) ||
            !valuesEqual(selectedUsers, base.users);
    }

    function updateDirtyState() {
        dirty = isCurrentSelectionDirty();
        setSaveButtonsState();
    }

    function cacheCurrentDraft() {
        if (!currentInstrument || !currentGroup) {
            return;
        }
        var key = makeGroupKey(currentInstrument, currentGroup);
        var base = baselineGroups[key] || { run_ids: [], users: [] };
        var changed = !valuesEqual(selectedRunIds, base.run_ids) ||
            !valuesEqual(selectedUsers, base.users);
        if (changed) {
            draftGroups[key] = {
                instrument: currentInstrument,
                name: currentGroup,
                run_ids: normalizeValues(selectedRunIds),
                users: normalizeValues(selectedUsers)
            };
        } else {
            delete draftGroups[key];
        }
        updateDirtyState();
    }

    function applyDraftForCurrentIfAny() {
        if (!currentInstrument || !currentGroup) {
            return;
        }
        var key = makeGroupKey(currentInstrument, currentGroup);
        var draft = draftGroups[key];
        if (draft && typeof draft === 'object') {
            selectedRunIds = normalizeValues(draft.run_ids || []);
            selectedUsers = normalizeValues(draft.users || []);
        }
    }

    function isAllGroupName(name) {
        return String(name || '').trim().toLowerCase() === 'all';
    }

    function setScienceHealth(status, message, healthDetails) {
        if (!sgHealth || !sgHealthHeadline) return;
        sgHealth.className = 'ari-ap-status ari-ap-status--' +
            (status === 'ok' ? 'ok' : 'warning');

        if (sgHealthDetails) {
            sgHealthDetails.innerHTML = '';
        }

        if (status === 'ok') {
            sgHealthHeadline.innerHTML =
                '<i class="fa-solid fa-circle-check"></i> ' + escapeHtml(message || 'All users are assigned.');
            return;
        }
        sgHealthHeadline.innerHTML =
            '<i class="fa-solid fa-triangle-exclamation"></i> ' + escapeHtml(message || 'Some users are missing science-group assignments.');

        if (sgHealthDetails && Array.isArray(healthDetails) && healthDetails.length) {
            var escapedDetails = healthDetails.map(function (item) {
                return escapeHtml(String(item));
            });
            sgHealthDetails.innerHTML =
                '<details>' +
                '<summary style="cursor:pointer; font-size:0.86rem;">' +
                'Show warning details (' + escapedDetails.length + ')' +
                '</summary>' +
                '<ul style="margin:0.3rem 0 0 1.1rem; font-size:0.85rem; line-height:1.45;">' +
                escapedDetails.map(function (item) {
                    return '<li>' + item + '</li>';
                }).join('') +
                '</ul>' +
                '</details>';
        }
    }

    /* -- Toast ----------------------------------------------------------- */
    function showToast(msg, type) {
        toast.textContent = msg;
        toast.className = 'ari-toast ari-toast--' + type;
        toast.style.display = 'block';
        clearTimeout(toast._timer);
        toast._timer = setTimeout(function () {
            toast.style.display = 'none';
        }, 3000);
    }

    /* -- Escape helper --------------------------------------------------- */
    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    /* -- Show/hide detail sections --------------------------------------- */
    function showDetailSections() {
        selectPrompt.style.display = 'none';
        runidSection.style.display = '';
        userSection.style.display = '';
        var topBar = document.getElementById('sg-actions-top');
        if (topBar) topBar.style.display = 'flex';
    }

    function hideDetailSections() {
        selectPrompt.style.display = '';
        runidSection.style.display = 'none';
        userSection.style.display = 'none';
        var topBar = document.getElementById('sg-actions-top');
        if (topBar) topBar.style.display = 'none';
    }

    /* -- Instrument tabs ------------------------------------------------- */
    function renderTabs() {
        var instruments = cfg.instruments || [];
        if (instruments.length === 0) {
            emptyState.style.display = 'block';
            workspace.style.display = 'none';
            actionsBar.style.display = 'none';
            return;
        }
        emptyState.style.display = 'none';
        tabsContainer.innerHTML = '';
        instruments.forEach(function (inst) {
            var btn = document.createElement('button');
            btn.className = 'ari-sg-tab';
            btn.textContent = inst;
            btn.addEventListener('click', function () {
                selectInstrument(inst);
            });
            tabsContainer.appendChild(btn);
        });
        selectInstrument(instruments[0]);
    }

    function selectInstrument(inst) {
        cacheCurrentDraft();
        currentInstrument = inst;
        currentGroup = null;
        updateDirtyState();
        var tabs = tabsContainer.querySelectorAll('.ari-sg-tab');
        tabs.forEach(function (t) {
            t.classList.toggle('ari-sg-tab--active', t.textContent === inst);
        });
        workspace.style.display = 'block';
        actionsBar.style.display = 'flex';
        clearDetail();
        loadGroupList();
    }

    /* -- Group list ------------------------------------------------------ */
    function loadGroupList() {
        groupList.innerHTML = '<div class="ari-sg-loading">Loading...</div>';
        // Capture the instrument the request was issued for. If the
        // user switches tabs before the response arrives, discard the
        // stale payload so groups from one instrument never bleed
        // into another.
        var requestedInstrument = currentInstrument;
        fetch(cfg.listUrl + '?instrument=' + encodeURIComponent(requestedInstrument))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (requestedInstrument !== currentInstrument) return;
                if (!data.success) {
                    groupList.innerHTML = '<div class="ari-sg-error">' +
                        escapeHtml(data.error || 'Error') + '</div>';
                    return;
                }
                allGroups = data.groups || [];
                allRunIds = data.run_ids || [];
                runIdLabels = data.run_id_labels || {};
                allUsers = data.available_users || [];
                setScienceHealth(
                    data.health_status || 'warning',
                    data.health_message || '',
                    data.health_details || []
                );
                renderGroupList('');
            })
            .catch(function () {
                if (requestedInstrument !== currentInstrument) return;
                groupList.innerHTML = '<div class="ari-sg-error">Failed to load</div>';
            });
    }

    function refreshScienceHealthBanner() {
        if (!currentInstrument) return;
        var requestedInstrument = currentInstrument;
        fetch(cfg.listUrl + '?instrument=' + encodeURIComponent(requestedInstrument))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (requestedInstrument !== currentInstrument) return;
                if (!data.success) return;
                allGroups = data.groups || [];
                allRunIds = data.run_ids || [];
                runIdLabels = data.run_id_labels || {};
                allUsers = data.available_users || [];
                setScienceHealth(
                    data.health_status || 'warning',
                    data.health_message || '',
                    data.health_details || []
                );
                renderGroupList(groupFilter.value || '');
                if (currentGroup) {
                    refreshTransfer('runid');
                    refreshTransfer('user');
                }
            })
            .catch(function () {
                /* Keep existing banner state on transient errors. */
            });
    }

    function renderGroupList(filter) {
        groupList.innerHTML = '';
        var lower = filter.toLowerCase();
        var shown = 0;
        allGroups.forEach(function (name) {
            if (lower && name.toLowerCase().indexOf(lower) === -1) return;
            shown++;
            var item = document.createElement('div');
            item.className = 'ari-sg-item';
            if (name === currentGroup) item.classList.add('ari-sg-item--active');
            item.innerHTML = '<i class="fa-solid fa-layer-group"></i> ' + escapeHtml(name);
            item.addEventListener('click', function () {
                selectGroup(name);
            });
            groupList.appendChild(item);
        });
        if (shown === 0 && allGroups.length > 0) {
            groupList.innerHTML = '<div class="ari-sg-empty-small">No matching groups</div>';
        } else if (allGroups.length === 0) {
            groupList.innerHTML = '<div class="ari-sg-empty-small">No groups yet</div>';
        }
    }

    /* -- Select a group -------------------------------------------------- */
    function selectGroup(name) {
        if (currentGroup && name !== currentGroup) {
            cacheCurrentDraft();
        }
        currentGroup = name;
        var items = groupList.querySelectorAll('.ari-sg-item');
        items.forEach(function (it) {
            it.classList.toggle('ari-sg-item--active',
                it.textContent.trim() === name);
        });
        updateDirtyState();
        btnAddAllRunIds.disabled = isAllGroupName(name);

        // Capture instrument+group identity at fetch time so that a
        // stale response from a previous tab/group click cannot
        // clobber the current selection.
        var requestedInstrument = currentInstrument;
        var requestedGroup = name;
        fetch(cfg.getUrl + '?instrument=' + encodeURIComponent(requestedInstrument) +
              '&name=' + encodeURIComponent(requestedGroup))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (requestedInstrument !== currentInstrument) return;
                if (requestedGroup !== currentGroup) return;
                if (!data.success) return;
                var key = makeGroupKey(
                    requestedInstrument,
                    requestedGroup
                );
                baselineGroups[key] = {
                    run_ids: normalizeValues(data.group.run_ids || []),
                    users: normalizeValues(data.group.users || [])
                };
                selectedRunIds = baselineGroups[key].run_ids.slice();
                selectedUsers = baselineGroups[key].users.slice();
                applyDraftForCurrentIfAny();
                showDetailSections();
                refreshTransfer('runid');
                refreshTransfer('user');
                updateDirtyState();
            })
            .catch(function () {
                if (requestedInstrument !== currentInstrument) return;
                if (requestedGroup !== currentGroup) return;
                showToast('Failed to load group details', 'error');
            });
    }

    function clearDetail() {
        currentGroup = null;
        selectedRunIds = [];
        selectedUsers = [];
        runidAvailable.innerHTML = '';
        runidAdded.innerHTML = '';
        userAvailable.innerHTML = '';
        userAdded.innerHTML = '';
        runidCount.textContent = '0';
        userCount.textContent = '0';
        runidAvailCount.textContent = '0';
        runidAddedCount.textContent = '0';
        userAvailCount.textContent = '0';
        userAddedCount.textContent = '0';
        dirty = false;
        setSaveButtonsState();
        btnAddAllRunIds.disabled = false;
        groupFilter.value = '';
        runidAvailFilter.value = '';
        runidAddedFilter.value = '';
        userAvailFilter.value = '';
        userAddedFilter.value = '';
        hideDetailSections();
    }

    /* ====================================================================
       Transfer list rendering (left = available, right = added)
       ==================================================================== */

    function getState(type) {
        if (type === 'runid') {
            return {
                all: allRunIds,
                selected: selectedRunIds,
                availContainer: runidAvailable,
                addedContainer: runidAdded,
                availFilter: runidAvailFilter,
                addedFilter: runidAddedFilter,
                headerCount: runidCount,
                availBadge: runidAvailCount,
                addedBadge: runidAddedCount,
                labelMap: runIdLabels,
                icon: 'fa-hashtag'
            };
        }
        return {
            all: allUsers,
            selected: selectedUsers,
            availContainer: userAvailable,
            addedContainer: userAdded,
            availFilter: userAvailFilter,
            addedFilter: userAddedFilter,
            headerCount: userCount,
            availBadge: userAvailCount,
            addedBadge: userAddedCount,
                labelMap: {},
            icon: 'fa-user'
        };
    }

    function refreshTransfer(type) {
        var s = getState(type);
        renderPane(type, 'available', s.all, s.selected, s.availFilter.value,
                   s.availContainer, s.icon);
        renderPane(type, 'added', s.all, s.selected, s.addedFilter.value,
                   s.addedContainer, s.icon);
        updateCounts(type);
    }

    /**
     * Render one pane of the transfer list.
     * side = 'available' or 'added'
     */
    function renderPane(type, side, allItems, selectedItems, filter, container, icon) {
        var lower = filter.toLowerCase();
        container.innerHTML = '';

        var items;
        if (side === 'available') {
            items = allItems.filter(function (it) {
                return selectedItems.indexOf(it) === -1;
            });
        } else {
            items = selectedItems.slice();
        }

        if (lower) {
            items = items.filter(function (it) {
                // Check raw item
                if (it.toLowerCase().indexOf(lower) !== -1) {
                    return true;
                }
                // For runids, also check display label (includes PI name)
                if (type === 'runid' && runIdLabels[it]) {
                    return runIdLabels[it].toLowerCase()
                        .indexOf(lower) !== -1;
                }
                return false;
            });
        }

        var totalCount = items.length;
        var capped = items.slice(0, LAZY_BATCH);

        if (capped.length === 0) {
            var emptyMsg = (side === 'available') ? 'None available' : 'None added';
            container.innerHTML = '<div class="ari-sg-empty-small">' + emptyMsg + '</div>';
            return;
        }

        capped.forEach(function (item) {
            var displayName = item;
            if (type === 'runid' && runIdLabels[item]) {
                displayName = runIdLabels[item];
            }
            var card = createTransferCard(
                type,
                side,
                item,
                displayName,
                icon
            );
            container.appendChild(card);
        });

        if (totalCount > LAZY_BATCH) {
            var more = document.createElement('div');
            more.className = 'ari-sg-load-more';
            more.textContent = 'Showing ' + LAZY_BATCH + ' of ' + totalCount +
                ' — use filter to narrow results';
            container.appendChild(more);
        }
    }

    function createTransferCard(type, side, item, displayName, icon) {
        var card = document.createElement('div');
        card.className = 'ari-sg-transfer-card';
        card.setAttribute('draggable', 'true');
        card.setAttribute('data-type', type);
        card.setAttribute('data-side', side);
        card.setAttribute('data-value', item);

        var actionIcon, actionTitle, actionClass;
        if (side === 'available') {
            actionIcon = 'fa-plus';
            actionTitle = 'Add';
            actionClass = 'ari-sg-transfer-card__action--add';
        } else {
            actionIcon = 'fa-xmark';
            actionTitle = 'Remove';
            actionClass = 'ari-sg-transfer-card__action--remove';
        }

        card.innerHTML =
            '<div class="ari-sg-transfer-card__grip" title="Drag to move">' +
                '<i class="fa-solid fa-grip-vertical"></i>' +
            '</div>' +
            '<div class="ari-sg-transfer-card__icon">' +
                '<i class="fa-solid ' + icon + '"></i>' +
            '</div>' +
            '<div class="ari-sg-transfer-card__name">'
            + escapeHtml(displayName) + '</div>' +
            '<button class="ari-sg-transfer-card__action ' + actionClass + '" title="' + actionTitle + '">' +
                '<i class="fa-solid ' + actionIcon + '"></i>' +
            '</button>';

        // Click action button
        card.querySelector('.ari-sg-transfer-card__action').addEventListener('click', function (e) {
            e.stopPropagation();
            if (side === 'available') {
                addSelection(type, item);
            } else {
                removeSelection(type, item);
            }
        });

        // Drag events
        card.addEventListener('dragstart', function (e) {
            e.dataTransfer.setData('text/plain', JSON.stringify({
                type: type,
                side: side,
                value: item
            }));
            e.dataTransfer.effectAllowed = 'move';
            card.classList.add('ari-sg-transfer-card--dragging');
        });

        card.addEventListener('dragend', function () {
            card.classList.remove('ari-sg-transfer-card--dragging');
        });

        return card;
    }

    /* -- Drop zone setup ------------------------------------------------- */
    function setupDropZone(container, targetSide, type) {
        container.addEventListener('dragover', function (e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            container.classList.add('ari-sg-transfer__list--dragover');
        });

        container.addEventListener('dragleave', function (e) {
            if (!container.contains(e.relatedTarget)) {
                container.classList.remove('ari-sg-transfer__list--dragover');
            }
        });

        container.addEventListener('drop', function (e) {
            e.preventDefault();
            container.classList.remove('ari-sg-transfer__list--dragover');
            var raw = e.dataTransfer.getData('text/plain');
            if (!raw) return;
            try {
                var data = JSON.parse(raw);
            } catch (_) {
                return;
            }
            if (data.type !== type) return;
            if (data.side === targetSide) return; // dropped on same side

            if (targetSide === 'added') {
                addSelection(data.type, data.value);
            } else {
                removeSelection(data.type, data.value);
            }
        });
    }

    /* -- Add / remove ---------------------------------------------------- */
    function addSelection(type, item) {
        if (type === 'runid' && isAllGroupName(currentGroup)) {
            showToast('Run IDs for "All" are managed automatically', 'info');
            return;
        }
        var arr = (type === 'runid') ? selectedRunIds : selectedUsers;
        if (arr.indexOf(item) === -1) {
            arr.push(item);
        }
        refreshTransfer(type);
        cacheCurrentDraft();
    }

    function removeSelection(type, item) {
        if (type === 'runid' && isAllGroupName(currentGroup)) {
            showToast('Run IDs for "All" are managed automatically', 'info');
            return;
        }
        if (type === 'runid') {
            selectedRunIds = selectedRunIds.filter(function (x) { return x !== item; });
        } else {
            selectedUsers = selectedUsers.filter(function (x) { return x !== item; });
        }
        refreshTransfer(type);
        cacheCurrentDraft();
    }

    function addAllSelections(type) {
        if (!currentGroup) {
            showToast('Select a group first', 'warning');
            return;
        }
        if (type === 'runid' && isAllGroupName(currentGroup)) {
            showToast('Run IDs for "All" are managed automatically', 'info');
            return;
        }

        var allItems = (type === 'runid') ? allRunIds.slice() : allUsers.slice();
        var selected = (type === 'runid') ? selectedRunIds.slice() : selectedUsers.slice();
        var toAdd = allItems.filter(function (it) {
            return selected.indexOf(it) === -1;
        });

        if (toAdd.length === 0) {
            showToast('Nothing to add', 'info');
            return;
        }

        var label = (type === 'runid') ? 'run IDs' : 'users';
        var ok = window.confirm(
            'Add all available ' + label + ' (' + toAdd.length + ') to group "' +
            currentGroup + '"? You will still need to click Save to persist.'
        );
        if (!ok) return;

        if (type === 'runid') {
            selectedRunIds = allItems.slice();
        } else {
            selectedUsers = allItems.slice();
        }

        refreshTransfer(type);
        cacheCurrentDraft();
    }

    /* -- Dirty tracking + unsaved-changes guard -------------------------- */
    var dirty = false;

    function setSaveButtonsState() {
        // Enable/disable both top and bottom Save/Delete clones to
        // reflect the current dirty / group-loaded state.
        var saveBtns = document.querySelectorAll(
            '#btn-save-group, #btn-save-group-top');
        var deleteBtns = document.querySelectorAll(
            '#btn-delete-group, #btn-delete-group-top');
        var ioBtns = document.querySelectorAll(
            '#btn-group-io, #btn-group-io-top');
        saveBtns.forEach(function (b) {
            b.disabled = !hasAnyDrafts();
        });
        deleteBtns.forEach(function (b) {
            b.disabled = !currentGroup || isAllGroupName(currentGroup);
        });
        ioBtns.forEach(function (b) {
            b.disabled = !currentGroup;
        });
    }

    function markDirty() {
        cacheCurrentDraft();
    }

    function markClean() {
        updateDirtyState();
    }

    // Returns true if it is safe to navigate away from / replace
    // the current group editor state (no unsaved changes, or the
    // user explicitly confirmed discarding them).
    function confirmDiscard() {
        if (!hasAnyDrafts()) return true;
        return window.confirm(
            'You have unsaved science-group edits. Discard them?'
        );
    }

    window.addEventListener('beforeunload', function (e) {
        if (!hasAnyDrafts()) return;
        // Setting returnValue triggers the browser's native
        // "Leave site?" prompt. The exact message is fixed by
        // modern browsers but the prompt itself shows up.
        e.preventDefault();
        e.returnValue = '';
        return '';
    });

    function updateCounts(type) {
        var s = getState(type);
        var numAdded = s.selected.length;
        var numAvail = s.all.length - numAdded;
        s.headerCount.textContent = numAdded;
        s.availBadge.textContent = numAvail;
        s.addedBadge.textContent = numAdded;
    }

    /* -- Save ------------------------------------------------------------ */
    function saveGroup() {
        var pendingKeys = Object.keys(draftGroups);
        if (!pendingKeys.length) {
            showToast('No pending science-group edits to save', 'info');
            return;
        }
        var saveBtns = document.querySelectorAll(
            '#btn-save-group, #btn-save-group-top');
        var saved = 0;
        var failed = 0;
        var failedNames = [];
        saveBtns.forEach(function (b) { b.disabled = true; });
        if (savingOverlay) {
            savingOverlay.style.display = 'flex';
            savingOverlay.setAttribute('aria-hidden', 'false');
        }
        var chain = Promise.resolve();
        pendingKeys.forEach(function (key) {
            chain = chain.then(function () {
                var entry = draftGroups[key];
                if (!entry) {
                    return;
                }
                return fetch(cfg.saveUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        instrument: entry.instrument,
                        name: entry.name,
                        run_ids: entry.run_ids,
                        users: entry.users
                    })
                })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (!data || !data.success) {
                            failed += 1;
                            failedNames.push(entry.instrument +
                                '/' + entry.name);
                            return;
                        }
                        var savedRunIds = normalizeValues(
                            (data.group || {}).run_ids || entry.run_ids || []
                        );
                        var savedUsers = normalizeValues(
                            (data.group || {}).users || entry.users || []
                        );
                        baselineGroups[key] = {
                            run_ids: savedRunIds,
                            users: savedUsers
                        };
                        delete draftGroups[key];
                        if (
                            entry.instrument === currentInstrument &&
                            entry.name === currentGroup
                        ) {
                            selectedRunIds = savedRunIds.slice();
                            selectedUsers = savedUsers.slice();
                            refreshTransfer('runid');
                            refreshTransfer('user');
                        }
                        saved += 1;
                    })
                    .catch(function () {
                        failed += 1;
                        failedNames.push(entry.instrument + '/' + entry.name);
                    });
            });
        });

        chain.finally(function () {
            updateDirtyState();
            if (savingOverlay) {
                savingOverlay.style.display = 'none';
                savingOverlay.setAttribute('aria-hidden', 'true');
            }
            refreshScienceHealthBanner();
            if (failed === 0) {
                showToast(
                    'Saved all science groups (' + saved + ')',
                    'success'
                );
            } else {
                showToast(
                    'Saved ' + saved + ', failed ' + failed +
                    ' (' + failedNames.join(', ') + ')',
                    'error'
                );
            }
        });
    }

    function refreshRunIds() {
        if (!currentInstrument) {
            showToast('Select an instrument first', 'warning');
            return;
        }
        if (!cfg.refreshRunIdsUrl) {
            showToast('Run ID refresh is not configured', 'error');
            return;
        }

        if (btnRefreshRunIds) btnRefreshRunIds.disabled = true;
        fetch(cfg.refreshRunIdsUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instrument: currentInstrument })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (btnRefreshRunIds) btnRefreshRunIds.disabled = false;
            if (!data.success) {
                showToast(data.error || 'Run ID refresh failed', 'error');
                return;
            }

            var scannedCount = Array.isArray(data.run_ids) ? data.run_ids.length : 0;
            console.log('Refresh API returned ' + scannedCount + ' run IDs');

            // Reload all server-derived lists and re-open the current group.
            loadGroupList();
            setTimeout(function () {
                var msg = 'Run IDs refreshed (found ' + allRunIds.length + ' total)';
                showToast(msg, 'success');
                if (currentGroup) {
                    selectGroup(currentGroup);
                }
            }, 100);
        })
        .catch(function () {
            if (btnRefreshRunIds) btnRefreshRunIds.disabled = false;
            showToast('Run ID refresh failed', 'error');
        });
    }

    function buildIoExportUrl(scope, kind, selection, groupName) {
        var params = new URLSearchParams();
        params.set('instrument', currentInstrument || '');
        params.set('scope', scope);
        params.set('kind', kind);
        if (selection) {
            params.set('selection', selection);
        }
        if (groupName) {
            params.set('group', groupName);
        }
        return cfg.ioExportUrl + '?' + params.toString();
    }

    function downloadIoExport(scope, kind, selection, groupName, done) {
        if (!currentInstrument) {
            showToast('Select an instrument first', 'warning');
            return;
        }
        if (!cfg.ioExportUrl) {
            showToast('Import/Export API is not configured', 'error');
            return;
        }
        var url = buildIoExportUrl(scope, kind, selection, groupName);
        fetch(url)
            .then(function (response) {
                if (!response.ok) {
                    return response.json().then(function (body) {
                        throw new Error(body.error || 'Export failed');
                    });
                }
                return response.blob().then(function (blob) {
                    return {
                        blob: blob,
                        disposition: response.headers.get(
                            'Content-Disposition') || ''
                    };
                });
            })
            .then(function (payload) {
                var filename = 'science_groups_export.yaml';
                var match = /filename=([^;]+)/i.exec(payload.disposition);
                if (match && match[1]) {
                    filename = match[1].trim().replace(/^"|"$/g, '');
                }
                var objectUrl = window.URL.createObjectURL(payload.blob);
                var link = document.createElement('a');
                link.href = objectUrl;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(objectUrl);
                showToast('YAML exported', 'success');
                if (done) done();
            })
            .catch(function (err) {
                showToast(err.message || 'YAML export failed', 'error');
            });
    }

    function uploadIoImport(scope, kind, mode, groupName, file, done) {
        if (!currentInstrument) {
            showToast('Select an instrument first', 'warning');
            return;
        }
        if (!cfg.ioImportUrl) {
            showToast('Import/Export API is not configured', 'error');
            return;
        }
        var body = new FormData();
        body.append('instrument', currentInstrument);
        body.append('scope', scope);
        body.append('kind', kind);
        body.append('mode', mode || 'merge');
        if (groupName) {
            body.append('group', groupName);
        }
        body.append('file', file);

        fetch(cfg.ioImportUrl, {
            method: 'POST',
            body: body
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    showToast(data.error || 'YAML import failed', 'error');
                    return;
                }
                showToast('YAML imported (' + (mode || 'merge') + ')',
                          'success');
                loadGroupList();
                if (currentGroup) {
                    setTimeout(function () {
                        selectGroup(currentGroup);
                    }, 120);
                }
                if (done) done();
            })
            .catch(function () {
                showToast('YAML import failed', 'error');
            });
    }

    function openGlobalIoModal() {
        if (!currentInstrument) {
            showToast('Select an instrument first', 'warning');
            return;
        }
        if (globalIoModal) {
            globalIoModal.style.display = 'flex';
        }
    }

    function closeGlobalIoModal() {
        if (globalIoModal) {
            globalIoModal.style.display = 'none';
        }
    }

    function openGroupIoModal() {
        if (!currentInstrument || !currentGroup) {
            showToast('Select a science group first', 'warning');
            return;
        }
        if (groupIoSelectedName) {
            groupIoSelectedName.textContent = currentGroup;
        }
        if (groupIoModal) {
            groupIoModal.style.display = 'flex';
        }
    }

    function closeGroupIoModal() {
        if (groupIoModal) {
            groupIoModal.style.display = 'none';
        }
    }

    /* -- Create group ---------------------------------------------------- */
    // Instrument captured when the create modal was opened. Using
    // this (instead of currentInstrument) means the create request
    // always targets the tab the user was on when they opened the
    // dialog, even if a stray click changes tabs while it is open.
    var createModalInstrument = null;

    function openCreateModal() {
        if (!currentInstrument) {
            showToast('Select an instrument first', 'warning');
            return;
        }
        createModalInstrument = currentInstrument;
        newGroupName.value = '';
        createError.style.display = 'none';
        createModal.style.display = 'flex';
        newGroupName.focus();
    }

    function closeCreateModal() {
        createModal.style.display = 'none';
        createModalInstrument = null;
    }

    function doCreate() {
        var name = newGroupName.value.trim();
        if (!name) {
            createError.textContent = 'Name is required.';
            createError.style.display = 'block';
            return;
        }
        var targetInstrument = createModalInstrument || currentInstrument;
        if (!targetInstrument) {
            createError.textContent = 'No instrument selected.';
            createError.style.display = 'block';
            return;
        }
        btnConfirmCreate.disabled = true;
        fetch(cfg.createUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: targetInstrument,
                name: name
            })
        })
        .then(function (r) {
            return r.json().then(function (body) {
                return { status: r.status, body: body };
            });
        })
        .then(function (resp) {
            btnConfirmCreate.disabled = false;
            var data = resp.body || {};
            if (data.success) {
                closeCreateModal();
                showToast('Created "' + name + '" in ' + targetInstrument,
                          'success');
                if (targetInstrument === currentInstrument) {
                    loadGroupList();
                }
            } else {
                var msg = data.error || 'Failed';
                if (resp.status === 409) {
                    msg = '"' + name + '" already exists in ' +
                          targetInstrument + '.';
                    // Refresh so the user can see the existing entry
                    // in this instrument's list.
                    if (targetInstrument === currentInstrument) {
                        loadGroupList();
                    }
                }
                createError.textContent = msg;
                createError.style.display = 'block';
            }
        })
        .catch(function () {
            btnConfirmCreate.disabled = false;
            createError.textContent = 'Request failed';
            createError.style.display = 'block';
        });
    }

    /* -- Delete group ---------------------------------------------------- */
    function openDeleteModal() {
        if (!currentGroup) return;
        deleteModalName.textContent = currentGroup;
        deleteModal.style.display = 'flex';
    }

    function closeDeleteModal() {
        deleteModal.style.display = 'none';
    }

    function doDelete() {
        if (!currentGroup) return;
        btnConfirmDelete.disabled = true;
        fetch(cfg.deleteUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: currentInstrument,
                name: currentGroup
            })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            btnConfirmDelete.disabled = false;
            if (data.success) {
                closeDeleteModal();
                var deletedKey = makeGroupKey(currentInstrument, currentGroup);
                delete baselineGroups[deletedKey];
                delete draftGroups[deletedKey];
                showToast('Deleted "' + currentGroup + '"', 'success');
                markClean();
                clearDetail();
                loadGroupList();
            } else {
                showToast(data.error || 'Delete failed', 'error');
                closeDeleteModal();
            }
        })
        .catch(function () {
            btnConfirmDelete.disabled = false;
            showToast('Request failed', 'error');
            closeDeleteModal();
        });
    }

    /* -- Event listeners ------------------------------------------------- */
    groupFilter.addEventListener('input', function () {
        renderGroupList(groupFilter.value);
    });

    runidAvailFilter.addEventListener('input', function () {
        var s = getState('runid');
        renderPane('runid', 'available', s.all, s.selected,
                   runidAvailFilter.value, s.availContainer, s.icon);
    });
    runidAddedFilter.addEventListener('input', function () {
        var s = getState('runid');
        renderPane('runid', 'added', s.all, s.selected,
                   runidAddedFilter.value, s.addedContainer, s.icon);
    });
    userAvailFilter.addEventListener('input', function () {
        var s = getState('user');
        renderPane('user', 'available', s.all, s.selected,
                   userAvailFilter.value, s.availContainer, s.icon);
    });
    userAddedFilter.addEventListener('input', function () {
        var s = getState('user');
        renderPane('user', 'added', s.all, s.selected,
                   userAddedFilter.value, s.addedContainer, s.icon);
    });

    btnAddGroup.addEventListener('click', openCreateModal);
    btnSave.addEventListener('click', saveGroup);
    btnDelete.addEventListener('click', openDeleteModal);
    // Top-bar clones (added by template) bind to the same
    // handlers so users can save/delete from either end of the
    // editor without scrolling.
    var btnSaveTop = document.getElementById('btn-save-group-top');
    if (btnSaveTop) {
        btnSaveTop.addEventListener('click', saveGroup);
    }
    var btnDeleteTop = document.getElementById('btn-delete-group-top');
    if (btnDeleteTop) {
        btnDeleteTop.addEventListener('click', openDeleteModal);
    }
    if (btnRefreshRunIds) {
        btnRefreshRunIds.addEventListener('click', refreshRunIds);
    }
    if (btnGlobalIo) {
        btnGlobalIo.addEventListener('click', openGlobalIoModal);
    }
    if (btnGroupIo) {
        btnGroupIo.addEventListener('click', openGroupIoModal);
    }
    if (btnGroupIoTop) {
        btnGroupIoTop.addEventListener('click', openGroupIoModal);
    }
    if (btnGlobalExport) {
        btnGlobalExport.addEventListener('click', function () {
            var kind = globalIoKind ? globalIoKind.value : 'users';
            var selection = globalIoSelection
                ? globalIoSelection.value : 'all';
            downloadIoExport('global', kind, selection, '', null);
        });
    }
    if (btnGlobalImport) {
        btnGlobalImport.addEventListener('click', function () {
            if (!globalIoFile) return;
            globalIoFile.click();
        });
    }
    if (globalIoFile) {
        globalIoFile.addEventListener('change', function () {
            if (!globalIoFile.files || !globalIoFile.files[0]) return;
            var kind = globalIoKind ? globalIoKind.value : 'users';
            var mode = globalIoMode ? globalIoMode.value : 'merge';
            var file = globalIoFile.files[0];
            uploadIoImport('global', kind, mode, '', file, function () {
                globalIoFile.value = '';
            });
        });
    }
    if (btnGlobalIoClose) {
        btnGlobalIoClose.addEventListener('click', closeGlobalIoModal);
    }
    if (btnGroupExport) {
        btnGroupExport.addEventListener('click', function () {
            if (!currentGroup) {
                showToast('Select a science group first', 'warning');
                return;
            }
            downloadIoExport('group', 'group', '', currentGroup, null);
        });
    }
    if (btnGroupImport) {
        btnGroupImport.addEventListener('click', function () {
            if (!groupIoFile) return;
            groupIoFile.click();
        });
    }
    if (groupIoFile) {
        groupIoFile.addEventListener('change', function () {
            if (!groupIoFile.files || !groupIoFile.files[0]) return;
            if (!currentGroup) {
                showToast('Select a science group first', 'warning');
                groupIoFile.value = '';
                return;
            }
            var mode = groupIoMode ? groupIoMode.value : 'merge';
            var file = groupIoFile.files[0];
            uploadIoImport('group', 'group', mode, currentGroup, file,
                function () {
                    groupIoFile.value = '';
                });
        });
    }
    if (btnGroupIoClose) {
        btnGroupIoClose.addEventListener('click', closeGroupIoModal);
    }
    btnAddAllRunIds.addEventListener('click', function () {
        addAllSelections('runid');
    });
    btnAddAllUsers.addEventListener('click', function () {
        addAllSelections('user');
    });

    btnCancelCreate.addEventListener('click', closeCreateModal);
    btnConfirmCreate.addEventListener('click', doCreate);

    btnCancelDelete.addEventListener('click', closeDeleteModal);
    btnConfirmDelete.addEventListener('click', doDelete);

    // Close modals on backdrop click
    createModal.addEventListener('click', function (e) {
        if (e.target === createModal) closeCreateModal();
    });
    deleteModal.addEventListener('click', function (e) {
        if (e.target === deleteModal) closeDeleteModal();
    });
    if (globalIoModal) {
        globalIoModal.addEventListener('click', function (e) {
            if (e.target === globalIoModal) {
                closeGlobalIoModal();
            }
        });
    }
    if (groupIoModal) {
        groupIoModal.addEventListener('click', function (e) {
            if (e.target === groupIoModal) {
                closeGroupIoModal();
            }
        });
    }

    // Enter key in create modal
    newGroupName.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') doCreate();
    });

    /* -- Set up drop zones ----------------------------------------------- */
    setupDropZone(runidAvailable, 'available', 'runid');
    setupDropZone(runidAdded, 'added', 'runid');
    setupDropZone(userAvailable, 'available', 'user');
    setupDropZone(userAdded, 'added', 'user');

    /* -- Init ------------------------------------------------------------ */
    renderTabs();
    } // end init

    document.addEventListener('DOMContentLoaded', init);
})();
