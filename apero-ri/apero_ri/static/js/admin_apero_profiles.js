/* =========================================================================
   Admin APERO Profiles page logic
   ========================================================================= */
(function () {
    'use strict';

    var cfg = window.ARI_APERO_PROFILES;

    /* -- Field definitions ----------------------------------------------- */
    var PATH_FIELDS = [
        { key: 'PATH_RAW',   id: 'profile-path-raw' },
        { key: 'PATH_PP',    id: 'profile-path-pp' },
        { key: 'PATH_RED',   id: 'profile-path-red' },
        { key: 'PATH_CALIB', id: 'profile-path-calib' },
        { key: 'PATH_TELLU', id: 'profile-path-tellu' },
        { key: 'PATH_LOG',   id: 'profile-path-log' },
        { key: 'PATH_LBL',   id: 'profile-path-lbl' },
    ];

    var DB_TEXT_FIELDS = [
        { key: 'DATABASE_HOST',     id: 'profile-db-host' },
        { key: 'DATABASE_USERNAME', id: 'profile-db-user' },
        { key: 'DATABASE_PASSWORD', id: 'profile-db-pass' },
        { key: 'DATABASE_NAME',     id: 'profile-db-name' },
    ];

    var TABLE_FIELDS = [
        { key: 'ASTROM_TABLENAME',  id: 'profile-tbl-astrom' },
        { key: 'CALIB_TABLENAME',   id: 'profile-tbl-calib' },
        { key: 'FINDEX_TABLENAME',  id: 'profile-tbl-findex' },
        { key: 'LOG_TABLENAME',     id: 'profile-tbl-log' },
        { key: 'TELLU_TABLENAME',   id: 'profile-tbl-tellu' },
        { key: 'REJECT_TABLENAME',  id: 'profile-tbl-reject' },
    ];

    /* -- DOM refs -------------------------------------------------------- */
    var tabsContainer = document.getElementById('instrument-tabs');
    var workspace = document.getElementById('ap-workspace');
    var emptyState = document.getElementById('ap-empty');

    var profileList = document.getElementById('profile-list');
    var profileCount = document.getElementById('profile-count');

    var formTitle = document.getElementById('form-title');
    var profileNameInput = document.getElementById('profile-name');
    var profileVersionInput = document.getElementById('profile-version');
    var profileServerInput = document.getElementById('profile-server');
    var profileDbMode = document.getElementById('profile-db-mode');

    var btnSaveProfile = document.getElementById('btn-save-profile');
    var btnCancelEdit = document.getElementById('btn-cancel-edit');
    var btnAddProfile = document.getElementById('btn-add-profile');
    var formSection = document.getElementById('form-section');
    var btnTestDb = document.getElementById('btn-test-db');
    var dbTestResult = document.getElementById('db-test-result');

    var groupsSection = document.getElementById('groups-section');
    var groupsTitle = document.getElementById('groups-title');
    var groupsContainer = document.getElementById('profile-groups');
    var groupsNoPerm = document.getElementById('groups-no-perm');

    var browseModal = document.getElementById('browse-modal');
    var browsePathInput = document.getElementById('browse-path-input');
    var btnBrowseGo = document.getElementById('btn-browse-go');
    var browseStatus = document.getElementById('browse-status');
    var browseList = document.getElementById('browse-list');
    var btnBrowseCancel = document.getElementById('btn-browse-cancel');
    var btnBrowseSelect = document.getElementById('btn-browse-select');

    var deleteModal = document.getElementById('delete-modal');
    var deleteModalName = document.getElementById('delete-modal-name');
    var btnCancelDelete = document.getElementById('btn-cancel-delete');
    var btnConfirmDelete = document.getElementById('btn-confirm-delete');

    var toast = document.getElementById('toast');

    // Build lookup for path input elements
    var pathInputs = {};
    PATH_FIELDS.forEach(function (f) {
        pathInputs[f.id] = document.getElementById(f.id);
    });

    // Build lookup for DB text input elements
    var dbInputs = {};
    DB_TEXT_FIELDS.forEach(function (f) {
        dbInputs[f.id] = document.getElementById(f.id);
    });

    // Build lookup for table name input elements
    var tableInputs = {};
    TABLE_FIELDS.forEach(function (f) {
        tableInputs[f.id] = document.getElementById(f.id);
    });

    /* -- State ----------------------------------------------------------- */
    var currentInstrument = null;
    var profiles = [];
    var editingProfile = null;
    var currentBrowsePath = '/';
    var dragSrcIndex = null;
    var browseTargetId = null;   // id of the input field being browsed for
    var lastBrowsePaths = {};    // remember last browsed path per field id
    var formDirty = false;       // track unsaved changes

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

    /* -- Mark form dirty ------------------------------------------------- */
    function markDirty() { formDirty = true; }

    /* -- Instrument tabs ------------------------------------------------- */
    function renderTabs() {
        var instruments = cfg.instruments || [];
        if (instruments.length === 0) {
            emptyState.style.display = 'block';
            workspace.style.display = 'none';
            return;
        }
        emptyState.style.display = 'none';
        tabsContainer.innerHTML = '';
        instruments.forEach(function (inst) {
            var btn = document.createElement('button');
            btn.className = 'ari-sg-tab';
            btn.textContent = inst;
            btn.addEventListener('click', function () {
                if (!guardUnsaved()) return;
                selectInstrument(inst);
            });
            tabsContainer.appendChild(btn);
        });
        selectInstrument(instruments[0]);
    }

    function selectInstrument(inst) {
        currentInstrument = inst;
        var tabs = tabsContainer.querySelectorAll('.ari-sg-tab');
        tabs.forEach(function (t) {
            t.classList.toggle('ari-sg-tab--active', t.textContent === inst);
        });
        workspace.style.display = 'block';
        resetForm();
        loadProfiles();
    }

    /* -- Guard against unsaved changes ----------------------------------- */
    function guardUnsaved() {
        if (!formDirty) return true;
        return confirm('You have unsaved changes. Discard them?');
    }

    /* -- Load profiles --------------------------------------------------- */
    function loadProfiles() {
        profileList.innerHTML = '<div class="ari-sg-loading">Loading...</div>';
        fetch(cfg.listUrl + '?instrument=' + encodeURIComponent(currentInstrument))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    profileList.innerHTML = '<div class="ari-sg-error">' +
                        escapeHtml(data.error || 'Error') + '</div>';
                    return;
                }
                profiles = data.profiles || [];
                renderProfiles();
            })
            .catch(function () {
                profileList.innerHTML = '<div class="ari-sg-error">Failed to load</div>';
            });
    }

    /* -- Render profile cards -------------------------------------------- */
    function renderProfiles() {
        profileList.innerHTML = '';
        profileCount.textContent = profiles.length;

        if (profiles.length === 0) {
            profileList.innerHTML = '<div class="ari-sg-empty-small">No profiles yet</div>';
            return;
        }

        profiles.forEach(function (p, idx) {
            var hasGroups = p.groups && p.groups.length > 0;
            var isOk = p.all_paths_ok && hasGroups;
            var card = document.createElement('div');
            card.className = 'ari-ap-card' +
                (isOk ? ' ari-ap-card--valid' : ' ari-ap-card--invalid');
            card.setAttribute('draggable', 'true');
            card.setAttribute('data-index', idx);

            var statusIcon = isOk
                ? '<i class="fa-solid fa-circle-check"></i>'
                : '<i class="fa-solid fa-circle-xmark"></i>';

            var statusText = '';
            if (isOk) {
                statusText = 'Valid profile';
            } else if (!hasGroups) {
                statusText = 'No groups assigned';
            } else {
                statusText = 'Some paths do not exist';
            }

            var metaParts = [];
            if (p.apero_version) metaParts.push('v' + escapeHtml(p.apero_version));
            if (p.reduction_server) metaParts.push(escapeHtml(p.reduction_server));
            if (p.groups && p.groups.length > 0) metaParts.push(escapeHtml(p.groups.join(', ')));
            var metaHtml = metaParts.length > 0
                ? '<div class="ari-ap-card__meta">' + metaParts.join(' &middot; ') + '</div>'
                : '';

            card.innerHTML =
                '<div class="ari-ap-card__grip" title="Drag to reorder">' +
                    '<i class="fa-solid fa-grip-vertical"></i>' +
                '</div>' +
                '<div class="ari-ap-card__status">' + statusIcon + '</div>' +
                '<div class="ari-ap-card__body">' +
                    '<div class="ari-ap-card__name">' + escapeHtml(p.name) + '</div>' +
                    metaHtml +
                    '<div class="ari-ap-card__hint">' + escapeHtml(statusText) + '</div>' +
                '</div>' +
                '<div class="ari-ap-card__actions">' +
                    '<button class="ari-ap-card__btn ari-ap-card__btn--edit" title="Edit">' +
                        '<i class="fa-solid fa-pen"></i>' +
                    '</button>' +
                    '<button class="ari-ap-card__btn ari-ap-card__btn--delete" title="Delete">' +
                        '<i class="fa-solid fa-trash"></i>' +
                    '</button>' +
                '</div>';

            card.querySelector('.ari-ap-card__btn--edit').addEventListener('click', function (e) {
                e.stopPropagation();
                if (!guardUnsaved()) return;
                enterEditMode(p);
            });

            card.querySelector('.ari-ap-card__btn--delete').addEventListener('click', function (e) {
                e.stopPropagation();
                openDeleteModal(p.name);
            });

            // Drag events
            card.addEventListener('dragstart', function (e) {
                dragSrcIndex = idx;
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', String(idx));
                card.classList.add('ari-ap-card--dragging');
            });
            card.addEventListener('dragend', function () {
                card.classList.remove('ari-ap-card--dragging');
                dragSrcIndex = null;
                profileList.querySelectorAll('.ari-ap-card--dragover').forEach(function (c) {
                    c.classList.remove('ari-ap-card--dragover');
                });
            });
            card.addEventListener('dragover', function (e) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                card.classList.add('ari-ap-card--dragover');
            });
            card.addEventListener('dragleave', function () {
                card.classList.remove('ari-ap-card--dragover');
            });
            card.addEventListener('drop', function (e) {
                e.preventDefault();
                card.classList.remove('ari-ap-card--dragover');
                var fromIdx = parseInt(e.dataTransfer.getData('text/plain'), 10);
                var toIdx = idx;
                if (fromIdx === toIdx) return;
                var moved = profiles.splice(fromIdx, 1)[0];
                profiles.splice(toIdx, 0, moved);
                renderProfiles();
                saveOrder();
            });

            profileList.appendChild(card);
        });
    }

    /* -- Save order after drag ------------------------------------------- */
    function saveOrder() {
        var order = profiles.map(function (p) { return p.name; });
        fetch(cfg.reorderUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instrument: currentInstrument, order: order })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success) showToast('Order updated', 'success');
            else showToast(data.error || 'Reorder failed', 'error');
        })
        .catch(function () { showToast('Reorder failed', 'error'); });
    }

    /* -- Add / Edit form ------------------------------------------------- */
    function resetForm() {
        editingProfile = null;
        formDirty = false;
        profileNameInput.value = '';
        profileNameInput.disabled = false;
        profileVersionInput.value = '';
        profileServerInput.value = '';
        profileDbMode.value = 'mysql+pymysql';
        DB_TEXT_FIELDS.forEach(function (f) { dbInputs[f.id].value = ''; });
        TABLE_FIELDS.forEach(function (f) { tableInputs[f.id].value = ''; });
        PATH_FIELDS.forEach(function (f) {
            pathInputs[f.id].value = '';
            var vdiv = document.getElementById(f.id + '-validation');
            if (vdiv) vdiv.style.display = 'none';
        });
        dbTestResult.style.display = 'none';
        formTitle.innerHTML = '<i class="fa-solid fa-plus"></i> Add Profile';
        formSection.style.display = 'none';
        groupsSection.style.display = 'none';
        groupsContainer.innerHTML = '';
    }

    function enterEditMode(profile) {
        editingProfile = profile.name;
        formDirty = false;
        profileNameInput.value = profile.name;
        profileNameInput.disabled = true;
        profileVersionInput.value = profile.apero_version || '';
        profileServerInput.value = profile.reduction_server || '';
        profileDbMode.value = profile.DATABASE_MODE || 'mysql+pymysql';
        DB_TEXT_FIELDS.forEach(function (f) {
            dbInputs[f.id].value = profile[f.key] || '';
        });
        TABLE_FIELDS.forEach(function (f) {
            tableInputs[f.id].value = profile[f.key] || '';
        });
        PATH_FIELDS.forEach(function (f) {
            pathInputs[f.id].value = profile[f.key] || '';
            validatePathField(f.id, profile[f.key] || '');
        });
        dbTestResult.style.display = 'none';
        formTitle.innerHTML = '<i class="fa-solid fa-pen"></i> Edit Profile: ' +
            escapeHtml(profile.name);
        formSection.style.display = '';
        formTitle.scrollIntoView({ behavior: 'smooth', block: 'start' });
        renderProfileGroups(profile);
    }

    /* -- Path validation (directory exists) ------------------------------ */
    var _pathTimers = {};
    function validatePathField(fieldId, path) {
        var vdiv = document.getElementById(fieldId + '-validation');
        if (!vdiv) return;
        if (!path) { vdiv.style.display = 'none'; return; }
        clearTimeout(_pathTimers[fieldId]);
        _pathTimers[fieldId] = setTimeout(function () {
            fetch(cfg.validateUrl + '?path=' + encodeURIComponent(path))
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (!data.success) {
                        showFieldValidation(vdiv, false, data.error || 'Invalid path');
                        return;
                    }
                    if (data.valid) {
                        showFieldValidation(vdiv, true, 'Directory exists');
                    } else {
                        showFieldValidation(vdiv, false, 'Directory does not exist');
                    }
                })
                .catch(function () {
                    showFieldValidation(vdiv, false, 'Could not validate');
                });
        }, 400);
    }

    function showFieldValidation(el, valid, message) {
        el.style.display = 'block';
        el.className = 'ari-ap-validation' +
            (valid ? ' ari-ap-validation--valid' : ' ari-ap-validation--invalid');
        var icon = valid ? 'fa-circle-check' : 'fa-circle-xmark';
        el.innerHTML = '<i class="fa-solid ' + icon + '"></i> ' + escapeHtml(message);
    }

    /* -- Test database connection ---------------------------------------- */
    function testDbConnection() {
        var mode = profileDbMode.value;
        var host = dbInputs['profile-db-host'].value.trim();
        var user = dbInputs['profile-db-user'].value.trim();
        var pass = dbInputs['profile-db-pass'].value;
        var name = dbInputs['profile-db-name'].value.trim();

        if (!host || !user || !name) {
            showFieldValidation(dbTestResult, false, 'Fill in all database fields first');
            return;
        }

        btnTestDb.disabled = true;
        btnTestDb.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing...';
        fetch(cfg.testDbUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                DATABASE_MODE: mode,
                DATABASE_HOST: host,
                DATABASE_USERNAME: user,
                DATABASE_PASSWORD: pass,
                DATABASE_NAME: name
            })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            btnTestDb.disabled = false;
            btnTestDb.innerHTML = '<i class="fa-solid fa-plug"></i> Test Connection';
            if (data.valid) {
                showFieldValidation(dbTestResult, true, 'Connection successful');
            } else {
                showFieldValidation(dbTestResult, false, data.error || 'Connection failed');
            }
        })
        .catch(function () {
            btnTestDb.disabled = false;
            btnTestDb.innerHTML = '<i class="fa-solid fa-plug"></i> Test Connection';
            showFieldValidation(dbTestResult, false, 'Request failed');
        });
    }

    /* -- Collect all form values ----------------------------------------- */
    function collectFormData() {
        var payload = {
            instrument: currentInstrument,
            name: profileNameInput.value.trim(),
            apero_version: profileVersionInput.value.trim(),
            reduction_server: profileServerInput.value.trim(),
            DATABASE_MODE: profileDbMode.value,
        };
        DB_TEXT_FIELDS.forEach(function (f) {
            payload[f.key] = dbInputs[f.id].value.trim();
        });
        // PASSWORD: don't trim (may have intentional spaces)
        payload.DATABASE_PASSWORD = dbInputs['profile-db-pass'].value;
        TABLE_FIELDS.forEach(function (f) {
            payload[f.key] = tableInputs[f.id].value.trim();
        });
        PATH_FIELDS.forEach(function (f) {
            payload[f.key] = pathInputs[f.id].value.trim();
        });
        return payload;
    }

    /* -- Validate all required before save ------------------------------- */
    function validateRequired() {
        var payload = collectFormData();
        if (!payload.name) { showToast('Profile name is required', 'error'); return null; }
        if (!payload.apero_version) { showToast('APERO version is required', 'error'); return null; }
        if (!payload.reduction_server) { showToast('Reduction server is required', 'error'); return null; }

        var dbReq = ['DATABASE_MODE', 'DATABASE_HOST', 'DATABASE_USERNAME', 'DATABASE_NAME'];
        for (var i = 0; i < dbReq.length; i++) {
            if (!payload[dbReq[i]]) {
                showToast(dbReq[i] + ' is required', 'error');
                return null;
            }
        }
        for (var j = 0; j < TABLE_FIELDS.length; j++) {
            if (!payload[TABLE_FIELDS[j].key]) {
                showToast(TABLE_FIELDS[j].key + ' is required', 'error');
                return null;
            }
        }
        for (var k = 0; k < PATH_FIELDS.length; k++) {
            if (!payload[PATH_FIELDS[k].key]) {
                showToast(PATH_FIELDS[k].key + ' is required', 'error');
                return null;
            }
        }
        return payload;
    }

    /* -- Save profile ---------------------------------------------------- */
    function saveProfile() {
        var payload = validateRequired();
        if (!payload) return;

        // Check groups for existing profile
        if (editingProfile) {
            var current = profiles.find(function (p) { return p.name === editingProfile; });
            if (current && (!current.groups || current.groups.length === 0)) {
                showToast('At least one group must be assigned before saving', 'error');
                return;
            }
        }

        btnSaveProfile.disabled = true;
        fetch(cfg.saveUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            btnSaveProfile.disabled = false;
            if (data.success) {
                formDirty = false;
                var verb = editingProfile ? 'Updated' : 'Created';
                showToast(verb + ' "' + payload.name + '"', 'success');
                resetForm();
                loadProfiles();
            } else {
                showToast(data.error || 'Save failed', 'error');
            }
        })
        .catch(function () {
            btnSaveProfile.disabled = false;
            showToast('Save failed', 'error');
        });
    }

    /* -- Delete ---------------------------------------------------------- */
    var pendingDelete = null;

    function openDeleteModal(name) {
        pendingDelete = name;
        deleteModalName.textContent = name;
        deleteModal.style.display = 'flex';
    }

    function closeDeleteModal() {
        deleteModal.style.display = 'none';
        pendingDelete = null;
    }

    function doDelete() {
        if (!pendingDelete) return;
        btnConfirmDelete.disabled = true;
        fetch(cfg.deleteUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instrument: currentInstrument, name: pendingDelete })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            btnConfirmDelete.disabled = false;
            if (data.success) {
                showToast('Deleted "' + pendingDelete + '"', 'success');
                closeDeleteModal();
                if (editingProfile === pendingDelete) resetForm();
                loadProfiles();
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

    /* -- File browser ---------------------------------------------------- */
    function openBrowseModal(targetFieldId) {
        browseTargetId = targetFieldId;
        var inputEl = pathInputs[targetFieldId];
        // Use remembered path, or current field value, or /
        var startPath = lastBrowsePaths[targetFieldId]
                        || (inputEl ? inputEl.value.trim() : '')
                        || '/';
        currentBrowsePath = startPath;
        browsePathInput.value = startPath;
        browseModal.style.display = 'flex';
        btnBrowseSelect.disabled = false;
        browseTo(startPath);
    }

    function closeBrowseModal() {
        browseModal.style.display = 'none';
    }

    function browseTo(path) {
        browseList.innerHTML = '<div class="ari-sg-loading">Loading...</div>';
        browseStatus.style.display = 'none';

        fetch(cfg.browseUrl + '?path=' + encodeURIComponent(path))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    browseList.innerHTML = '<div class="ari-sg-error">' +
                        escapeHtml(data.error || 'Error') + '</div>';
                    browsePathInput.value = currentBrowsePath;
                    return;
                }

                currentBrowsePath = data.path;
                browsePathInput.value = data.path;
                if (browseTargetId) lastBrowsePaths[browseTargetId] = data.path;

                // Show exists status
                if (data.validation) {
                    browseStatus.style.display = 'block';
                    browseStatus.className = 'ari-ap-browser__status ari-ap-browser__status--valid';
                    browseStatus.innerHTML =
                        '<i class="fa-solid fa-circle-check"></i> Directory exists';
                }
                btnBrowseSelect.disabled = false;

                browseList.innerHTML = '';
                var dirs = data.dirs || [];

                if (data.path !== '/') {
                    var parent = data.path.replace(/\/[^/]+\/?$/, '') || '/';
                    var upItem = document.createElement('div');
                    upItem.className = 'ari-ap-browser__item ari-ap-browser__item--parent';
                    upItem.innerHTML = '<i class="fa-solid fa-arrow-up"></i> ..';
                    upItem.addEventListener('click', function () { browseTo(parent); });
                    browseList.appendChild(upItem);
                }

                if (dirs.length === 0) {
                    var empty = document.createElement('div');
                    empty.className = 'ari-sg-empty-small';
                    empty.textContent = 'No subdirectories';
                    browseList.appendChild(empty);
                } else {
                    dirs.forEach(function (d) {
                        var item = document.createElement('div');
                        item.className = 'ari-ap-browser__item';
                        item.innerHTML = '<i class="fa-solid fa-folder"></i> ' + escapeHtml(d);
                        item.addEventListener('click', function () {
                            var newPath = data.path.replace(/\/$/, '') + '/' + d;
                            browseTo(newPath);
                        });
                        browseList.appendChild(item);
                    });
                }
            })
            .catch(function () {
                browseList.innerHTML = '<div class="ari-sg-error">Failed to browse</div>';
            });
    }

    function selectBrowsePath() {
        if (browseTargetId && pathInputs[browseTargetId]) {
            pathInputs[browseTargetId].value = currentBrowsePath;
            lastBrowsePaths[browseTargetId] = currentBrowsePath;
            validatePathField(browseTargetId, currentBrowsePath);
            markDirty();
        }
        closeBrowseModal();
    }

    /* -- Profile groups -------------------------------------------------- */
    function computeEncompassed(enabledGroups, inheritedMap) {
        var encompassed = new Set();
        enabledGroups.forEach(function (g) {
            var inherited = inheritedMap[g] || [];
            inherited.forEach(function (sub) { encompassed.add(sub); });
        });
        return encompassed;
    }

    function renderProfileGroups(profile) {
        groupsContainer.innerHTML = '';
        var allGroups = cfg.allGroups || [];
        var canManage = new Set(cfg.canManageGroups || []);
        var inheritedMap = cfg.inheritedMap || {};
        var profileGroups = new Set(profile.groups || []);

        if (canManage.size === 0) {
            groupsNoPerm.style.display = '';
            groupsSection.style.display = '';
            groupsTitle.innerHTML = '<i class="fa-solid fa-users-gear"></i> Groups: ' +
                escapeHtml(profile.name);
            return;
        }
        groupsNoPerm.style.display = 'none';
        groupsSection.style.display = '';
        groupsTitle.innerHTML = '<i class="fa-solid fa-users-gear"></i> Groups: ' +
            escapeHtml(profile.name);

        var encompassed = computeEncompassed(profileGroups, inheritedMap);

        allGroups.forEach(function (group) {
            var isEnabled = profileGroups.has(group);
            var canManageThis = canManage.has(group);
            var isEncompassed = encompassed.has(group) && !profileGroups.has(group);
            var isEncompassedEnabled = encompassed.has(group) && profileGroups.has(group);

            var card = document.createElement('span');
            var stateClass, iconHtml, tooltip;

            if (!canManageThis) {
                stateClass = 'ari-toggle-card--locked';
                iconHtml = isEnabled
                    ? '<i class="fa-solid fa-check ari-toggle-card__icon"></i>'
                    : '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>';
                tooltip = 'You do not have permission to manage group: ' + group;
            } else if (isEncompassedEnabled) {
                stateClass = 'ari-toggle-card--encompassed';
                iconHtml = '<i class="fa-solid fa-check ari-toggle-card__icon"></i>';
                tooltip = 'Already encompassed by a higher-level group';
            } else if (isEncompassed) {
                stateClass = 'ari-toggle-card--encompassed';
                iconHtml = '<i class="fa-solid fa-minus ari-toggle-card__icon"></i>';
                tooltip = 'Already included via a higher-level group';
            } else if (isEnabled) {
                stateClass = 'ari-toggle-card--enabled';
                iconHtml = '<i class="fa-solid fa-check ari-toggle-card__icon"></i>';
                tooltip = 'Click to remove';
            } else {
                stateClass = 'ari-toggle-card--disabled';
                iconHtml = '<i class="fa-solid fa-xmark ari-toggle-card__icon"></i>';
                tooltip = 'Click to add';
            }

            card.className = 'ari-toggle-card ' + stateClass;
            card.innerHTML = iconHtml + ' ' + escapeHtml(group);
            card.title = tooltip;

            if (canManageThis && !isEncompassed && !isEncompassedEnabled) {
                card.addEventListener('click', function () {
                    toggleProfileGroup(profile, group);
                });
            }

            groupsContainer.appendChild(card);
        });
    }

    function toggleProfileGroup(profile, group) {
        var groups = (profile.groups || []).slice();
        var idx = groups.indexOf(group);
        if (idx >= 0) groups.splice(idx, 1);
        else groups.push(group);

        fetch(cfg.updateGroupsUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: currentInstrument,
                name: profile.name,
                groups: groups
            })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success) {
                profile.groups = groups;
                renderProfileGroups(profile);
                renderProfiles();
                showToast('Groups updated', 'success');
            } else {
                showToast(data.error || 'Update failed', 'error');
            }
        })
        .catch(function () { showToast('Network error', 'error'); });
    }

    /* -- Event listeners ------------------------------------------------- */
    [profileNameInput, profileVersionInput, profileServerInput].forEach(function (el) {
        el.addEventListener('input', markDirty);
    });
    DB_TEXT_FIELDS.forEach(function (f) { dbInputs[f.id].addEventListener('input', markDirty); });
    TABLE_FIELDS.forEach(function (f) { tableInputs[f.id].addEventListener('input', markDirty); });
    profileDbMode.addEventListener('change', markDirty);

    PATH_FIELDS.forEach(function (f) {
        pathInputs[f.id].addEventListener('input', function () {
            markDirty();
            validatePathField(f.id, pathInputs[f.id].value.trim());
        });
    });

    document.querySelectorAll('.btn-browse-path').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var targetId = btn.getAttribute('data-target');
            openBrowseModal(targetId);
        });
    });

    btnSaveProfile.addEventListener('click', saveProfile);
    btnCancelEdit.addEventListener('click', function () {
        if (!guardUnsaved()) return;
        resetForm();
    });
    btnAddProfile.addEventListener('click', function () {
        if (!guardUnsaved()) return;
        resetForm();
        formSection.style.display = '';
        profileNameInput.focus();
    });

    btnTestDb.addEventListener('click', testDbConnection);

    btnBrowseCancel.addEventListener('click', closeBrowseModal);
    btnBrowseSelect.addEventListener('click', selectBrowsePath);
    btnBrowseGo.addEventListener('click', function () {
        browseTo(browsePathInput.value.trim() || '/');
    });
    browsePathInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') browseTo(browsePathInput.value.trim() || '/');
    });

    btnCancelDelete.addEventListener('click', closeDeleteModal);
    btnConfirmDelete.addEventListener('click', doDelete);

    browseModal.addEventListener('click', function (e) {
        if (e.target === browseModal) closeBrowseModal();
    });
    deleteModal.addEventListener('click', function (e) {
        if (e.target === deleteModal) closeDeleteModal();
    });

    window.addEventListener('beforeunload', function (e) {
        if (formDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    /* -- Init ------------------------------------------------------------ */
    renderTabs();
})();
