/* =========================================================================
   Admin Science Groups page logic — dual-list transfer with drag-and-drop
   ========================================================================= */
(function () {
    'use strict';

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
    var allUsers = [];
    var selectedRunIds = [];
    var selectedUsers = [];

    var LAZY_BATCH = 80;

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
    }

    function hideDetailSections() {
        selectPrompt.style.display = '';
        runidSection.style.display = 'none';
        userSection.style.display = 'none';
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
        currentInstrument = inst;
        currentGroup = null;
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
        fetch(cfg.listUrl + '?instrument=' + encodeURIComponent(currentInstrument))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    groupList.innerHTML = '<div class="ari-sg-error">' +
                        escapeHtml(data.error || 'Error') + '</div>';
                    return;
                }
                allGroups = data.groups || [];
                allRunIds = data.run_ids || [];
                allUsers = data.available_users || [];
                setScienceHealth(
                    data.health_status || 'warning',
                    data.health_message || '',
                    data.health_details || []
                );
                renderGroupList('');
            })
            .catch(function () {
                groupList.innerHTML = '<div class="ari-sg-error">Failed to load</div>';
            });
    }

    function refreshScienceHealthBanner() {
        if (!currentInstrument) return;
        fetch(cfg.listUrl + '?instrument=' + encodeURIComponent(currentInstrument))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) return;
                allGroups = data.groups || [];
                allRunIds = data.run_ids || [];
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
        currentGroup = name;
        var items = groupList.querySelectorAll('.ari-sg-item');
        items.forEach(function (it) {
            it.classList.toggle('ari-sg-item--active',
                it.textContent.trim() === name);
        });
        btnSave.disabled = false;
        btnDelete.disabled = isAllGroupName(name);
        btnAddAllRunIds.disabled = isAllGroupName(name);

        fetch(cfg.getUrl + '?instrument=' + encodeURIComponent(currentInstrument) +
              '&name=' + encodeURIComponent(name))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) return;
                selectedRunIds = data.group.run_ids || [];
                selectedUsers = data.group.users || [];
                showDetailSections();
                refreshTransfer('runid');
                refreshTransfer('user');
            })
            .catch(function () {
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
        btnSave.disabled = true;
        btnDelete.disabled = true;
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
                return it.toLowerCase().indexOf(lower) !== -1;
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
            var card = createTransferCard(type, side, item, icon);
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

    function createTransferCard(type, side, item, icon) {
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
            '<div class="ari-sg-transfer-card__name">' + escapeHtml(item) + '</div>' +
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
        autoSave();
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
        autoSave();
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
            currentGroup + '"?'
        );
        if (!ok) return;

        if (type === 'runid') {
            selectedRunIds = allItems.slice();
        } else {
            selectedUsers = allItems.slice();
        }

        refreshTransfer(type);
        saveGroup();
    }

    /* -- Auto-save (debounced) ------------------------------------------- */
    var _autoSaveTimer = null;
    function autoSave() {
        clearTimeout(_autoSaveTimer);
        _autoSaveTimer = setTimeout(function () {
            saveGroup();
        }, 400);
    }

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
        if (!currentInstrument || !currentGroup) return;
        btnSave.disabled = true;
        fetch(cfg.saveUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: currentInstrument,
                name: currentGroup,
                run_ids: selectedRunIds,
                users: selectedUsers
            })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            btnSave.disabled = false;
            if (data.success) {
                if (data.group && typeof data.group === 'object') {
                    selectedRunIds = data.group.run_ids || [];
                    selectedUsers = data.group.users || [];
                    refreshTransfer('runid');
                    refreshTransfer('user');
                }
                showToast('Saved "' + currentGroup + '"', 'success');
                refreshScienceHealthBanner();
            } else {
                showToast(data.error || 'Save failed', 'error');
            }
        })
        .catch(function () {
            btnSave.disabled = false;
            showToast('Save failed', 'error');
        });
    }

    /* -- Create group ---------------------------------------------------- */
    function openCreateModal() {
        newGroupName.value = '';
        createError.style.display = 'none';
        createModal.style.display = 'flex';
        newGroupName.focus();
    }

    function closeCreateModal() {
        createModal.style.display = 'none';
    }

    function doCreate() {
        var name = newGroupName.value.trim();
        if (!name) {
            createError.textContent = 'Name is required.';
            createError.style.display = 'block';
            return;
        }
        btnConfirmCreate.disabled = true;
        fetch(cfg.createUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: currentInstrument,
                name: name
            })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            btnConfirmCreate.disabled = false;
            if (data.success) {
                closeCreateModal();
                showToast('Created "' + name + '"', 'success');
                loadGroupList();
            } else {
                createError.textContent = data.error || 'Failed';
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
                showToast('Deleted "' + currentGroup + '"', 'success');
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
})();
