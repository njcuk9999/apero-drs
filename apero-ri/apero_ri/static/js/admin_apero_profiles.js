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
        { key: 'PATH_OUT',   id: 'profile-path-out' },
        { key: 'PATH_CALIB', id: 'profile-path-calib' },
        { key: 'PATH_TELLU', id: 'profile-path-tellu' },
        { key: 'PATH_LOG',   id: 'profile-path-log' },
        { key: 'PATH_LBL',   id: 'profile-path-lbl' },
    ];

    var DB_TEXT_FIELDS = [
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

    var aprofileSelect      = document.getElementById('profile-instrument-profile');
    var sciParamsBtnRow     = document.getElementById('sci-params-btn-row');
    var btnShowSciParams = document.getElementById('btn-show-sci-params');
    var sciParamsPanel   = document.getElementById('sci-params-panel');
    var sciParamsBreadcrumb = document.getElementById('sci-params-breadcrumb');
    var sciParamsExplorer   = document.getElementById('sci-params-explorer');

    /* -- DOM refs -------------------------------------------------------- */
    var tabsContainer = document.getElementById('instrument-tabs');
    var workspace = document.getElementById('ap-workspace');
    var emptyState = document.getElementById('ap-empty');
    var globalStatusBox = document.getElementById('apero-global-status-box');
    var globalStatusHeadline = document.getElementById('apero-global-status-headline');
    var globalStatusDetails = document.getElementById('apero-global-status-details');
    var globalStatusToggle = document.getElementById('apero-global-status-toggle');
    var instrumentStatusBox = document.getElementById('apero-instrument-status-box');
    var instrumentStatusHeadline = document.getElementById('apero-instrument-status-headline');
    var instrumentStatusDetails = document.getElementById('apero-instrument-status-details');

    var profileList = document.getElementById('profile-list');
    var profileCount = document.getElementById('profile-count');

    var formTitle = document.getElementById('form-title');
    var profileNameInput = document.getElementById('profile-name');
    var profileVersionInput = document.getElementById('profile-version');
    var profileServerInput = document.getElementById('profile-server');
    var profileDbSource = document.getElementById('profile-db-source');
    var profileDbDefinitionName = document.getElementById('profile-db-definition-name');

    var btnSaveProfile = document.getElementById('btn-save-profile');
    var btnCancelEdit = document.getElementById('btn-cancel-edit');
    var btnAddProfile = document.getElementById('btn-add-profile');
    var formSection = document.getElementById('form-section');
    var btnTestDb = document.getElementById('btn-test-db');
    var dbTestResult = document.getElementById('db-test-result');
    var btnTestTables = document.getElementById('btn-test-tables');
    var tablesTestResult = document.getElementById('tables-test-result');
    var btnTestPaths = document.getElementById('btn-test-paths');
    var pathsTestResult = document.getElementById('paths-test-result');

    var tablesSection = document.getElementById('tables-section');
    var scienceSection = document.getElementById('science-section');
    var pathsSection = document.getElementById('paths-section');
    var dbSection = document.getElementById('db-section');
    var dbStepStatus = document.getElementById('db-step-status');
    var tablesStepStatus = document.getElementById('tables-step-status');
    var scienceStepStatus = document.getElementById('science-step-status');
    var pathsStepStatus = document.getElementById('paths-step-status');

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
    var dbTestPassed = false;
    var tablesTestPassed = false;
    var pathsTestPassed = false;
    var draftGroups = [];
    var availableDbTables = [];
    var globalStatusLastSignature = '';
    var globalStatusCollapsed = true;
    var dbLocalOptions = [];
    var dbTunnelOptions = [];
    var sectionCollapsePrefs = {
        db: null,
        tables: null,
        science: null,
        paths: null,
    };
    var sciParamsData = null;    // full YAML data for selected instrument profile
    var sciParamsExpanded = new Set();

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

    function setTableOptions(tableNames, preserveCurrent) {
        availableDbTables = Array.isArray(tableNames)
            ? tableNames.slice().sort()
            : [];

        TABLE_FIELDS.forEach(function (field) {
            var select = tableInputs[field.id];
            var currentValue = select.value;
            var seen = {};
            select.innerHTML = '<option value="">Select table...</option>';

            availableDbTables.forEach(function (tableName) {
                if (seen[tableName]) return;
                seen[tableName] = true;
                var option = document.createElement('option');
                option.value = tableName;
                option.textContent = tableName;
                select.appendChild(option);
            });

            if (preserveCurrent && currentValue && !seen[currentValue]) {
                var currentOption = document.createElement('option');
                currentOption.value = currentValue;
                currentOption.textContent = currentValue + ' (current)';
                select.appendChild(currentOption);
            }
            select.value = currentValue || '';
        });
    }

    function setSingleTableValue(fieldId, value) {
        var select = tableInputs[fieldId];
        var currentValue = String(value || '').trim();
        if (!select) return;
        if (!currentValue) {
            select.value = '';
            return;
        }
        var exists = Array.prototype.some.call(select.options, function (option) {
            return option.value === currentValue;
        });
        if (!exists) {
            var currentOption = document.createElement('option');
            currentOption.value = currentValue;
            currentOption.textContent = currentValue + ' (current)';
            select.appendChild(currentOption);
        }
        select.value = currentValue;
    }

    function clearTableOptions(preserveCurrent) {
        setTableOptions([], !!preserveCurrent);
    }

    function loadAvailableTables(options) {
        options = options || {};
        var payload = buildDbPayload();
        return fetch(cfg.listTablesUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.valid) {
                setTableOptions(data.tables || [], true);
                if (!options.silent) {
                    showFieldValidation(tablesTestResult, true,
                        'Loaded ' + String((data.tables || []).length) + ' tables from database.');
                }
                return data.tables || [];
            }
            if (!options.silent) {
                showFieldValidation(tablesTestResult, false,
                    data.error || 'Failed to load database tables');
            }
            throw new Error(data.error || 'Failed to load database tables');
        });
    }

    function populateDbDefinitionSelect(source, selectedName) {
        if (!profileDbDefinitionName) return;
        var current = String(selectedName || profileDbDefinitionName.value || '').trim();
        var useTunnel = source === 'db_ssh_tunnel';
        var rows = useTunnel ? dbTunnelOptions : dbLocalOptions;
        profileDbDefinitionName.innerHTML = '<option value="">Select database definition...</option>';
        rows.forEach(function (row) {
            var name = String(row.name || '').trim();
            if (!name) return;
            var option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            profileDbDefinitionName.appendChild(option);
        });
        if (current) {
            var hasCurrent = Array.prototype.some.call(
                profileDbDefinitionName.options,
                function (opt) { return opt.value === current; }
            );
            if (!hasCurrent) {
                var missing = document.createElement('option');
                missing.value = current;
                missing.textContent = current + ' (missing)';
                profileDbDefinitionName.appendChild(missing);
            }
            profileDbDefinitionName.value = current;
        }
    }

    function loadDbDefinitionOptions(source, selectedName) {
        var resolvedSource = String(source || (profileDbSource ? profileDbSource.value : 'local') || 'local');
        var jobs = [];

        if (cfg.localDbListUrl) {
            jobs.push(
                fetch(cfg.localDbListUrl)
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (!data.success) throw new Error(data.error || 'Could not load local database definitions');
                        dbLocalOptions = Array.isArray(data.local_databases) ? data.local_databases : [];
                    })
            );
        } else {
            dbLocalOptions = [];
        }

        if (cfg.dbTunnelListUrl) {
            jobs.push(
                fetch(cfg.dbTunnelListUrl)
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (!data.success) throw new Error(data.error || 'Could not load DB tunnel definitions');
                        dbTunnelOptions = Array.isArray(data.tunnels) ? data.tunnels : [];
                    })
            );
        } else {
            dbTunnelOptions = [];
        }

        return Promise.all(jobs)
            .then(function () {
                populateDbDefinitionSelect(resolvedSource, selectedName || '');
                return resolvedSource === 'db_ssh_tunnel' ? dbTunnelOptions : dbLocalOptions;
            })
            .catch(function (err) {
                populateDbDefinitionSelect(resolvedSource, selectedName || '');
                showToast(err.message || 'Could not load database definitions', 'error');
                return [];
            });
    }

    /* -- Instrument tabs ------------------------------------------------- */
    function renderTabs() {
        var instruments = cfg.instruments || [];
        loadGlobalStatus();
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
                    updateInstrumentStatusBox({
                        level: 'error',
                        headline: 'Could not load profile status for this instrument.',
                        details: [String(data.error || 'Unknown error')],
                    });
                    loadGlobalStatus();
                    return;
                }
                profiles = data.profiles || [];
                updateInstrumentStatusBox(data.status || null);
                renderProfiles();
                loadGlobalStatus();
            })
            .catch(function () {
                profileList.innerHTML = '<div class="ari-sg-error">Failed to load</div>';
                updateInstrumentStatusBox({
                    level: 'error',
                    headline: 'Could not load profile status for this instrument.',
                    details: ['Network error while loading profiles.'],
                });
                loadGlobalStatus();
            });
    }

    function updateStatusBox(status, box, headlineEl, detailsEl, fallbackHeadline, options) {
        if (!box || !headlineEl || !detailsEl) return;
        options = options || {};

        var level = (status && status.level) ? String(status.level) : 'info';
        var headline = (status && status.headline)
            ? String(status.headline)
            : fallbackHeadline;
        var details = (status && Array.isArray(status.details)) ? status.details : [];
        var toggleEl = options.toggleEl || null;
        var collapseThreshold = options.collapseThreshold || 6;
        var collapsible = !!options.collapsible && details.length > collapseThreshold;
        var collapsed = !!options.collapsed;

        var icon = 'fa-circle-info';
        if (level === 'ok') icon = 'fa-circle-check';
        else if (level === 'warning') icon = 'fa-triangle-exclamation';
        else if (level === 'error') icon = 'fa-circle-xmark';

        box.classList.remove('ari-ap-status--info', 'ari-ap-status--ok',
            'ari-ap-status--warning', 'ari-ap-status--error');
        box.classList.add('ari-ap-status--' +
            (level === 'ok' || level === 'warning' || level === 'error' ? level : 'info'));

        headlineEl.innerHTML = '<i class="fa-solid ' + icon + '"></i> ' + escapeHtml(headline);

        if (toggleEl) {
            if (collapsible) {
                toggleEl.style.display = '';
                toggleEl.textContent = collapsed
                    ? 'Show issue breakdown (' + details.length + ')'
                    : 'Hide issue breakdown';
                toggleEl.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
            } else {
                toggleEl.style.display = 'none';
                toggleEl.textContent = '';
                toggleEl.setAttribute('aria-expanded', 'false');
            }
        }

        if (details.length && !(collapsible && collapsed)) {
            detailsEl.style.display = '';
            detailsEl.innerHTML = details.map(function (d) {
                return '<li>' + escapeHtml(String(d)) + '</li>';
            }).join('');
        } else {
            detailsEl.style.display = 'none';
            detailsEl.innerHTML = '';
        }
    }

    function updateInstrumentStatusBox(status) {
        updateStatusBox(
            status,
            instrumentStatusBox,
            instrumentStatusHeadline,
            instrumentStatusDetails,
            'Select an instrument to check APERO profile status.'
        );
    }

    function updateGlobalStatusBox(status) {
        var details = (status && Array.isArray(status.details)) ? status.details : [];
        var signature = JSON.stringify({
            level: (status && status.level) ? String(status.level) : 'info',
            details: details,
        });
        if (signature !== globalStatusLastSignature) {
            globalStatusLastSignature = signature;
            globalStatusCollapsed = true;
        }

        updateStatusBox(
            status,
            globalStatusBox,
            globalStatusHeadline,
            globalStatusDetails,
            'Checking APERO profile readiness across all instruments.',
            {
                collapsible: true,
                collapsed: globalStatusCollapsed,
                toggleEl: globalStatusToggle,
                collapseThreshold: 5,
            }
        );
    }

    function loadGlobalStatus() {
        fetch(cfg.statusOverviewUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    updateGlobalStatusBox({
                        level: 'error',
                        headline: 'Could not load all-profiles status.',
                        details: [String(data.error || 'Unknown error')],
                    });
                    return;
                }
                updateGlobalStatusBox(data.status || null);
            })
            .catch(function () {
                updateGlobalStatusBox({
                    level: 'error',
                    headline: 'Could not load all-profiles status.',
                    details: ['Network error while loading status.'],
                });
            });
    }

    if (globalStatusToggle) {
        globalStatusToggle.addEventListener('click', function () {
            globalStatusCollapsed = !globalStatusCollapsed;
            loadGlobalStatus();
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
                statusText = 'Ready';
            } else if (!hasGroups) {
                statusText = 'Needs group assignment';
            } else {
                statusText = 'Needs path checks';
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
                    '<button class="ari-ap-card__btn ari-ap-card__btn--duplicate" title="Duplicate">' +
                        '<i class="fa-solid fa-copy"></i>' +
                    '</button>' +
                    '<button class="ari-ap-card__btn ari-ap-card__btn--edit" title="Edit">' +
                        '<i class="fa-solid fa-pen"></i>' +
                    '</button>' +
                    '<button class="ari-ap-card__btn ari-ap-card__btn--delete" title="Delete">' +
                        '<i class="fa-solid fa-trash"></i>' +
                    '</button>' +
                '</div>';

            card.querySelector(
                '.ari-ap-card__btn--duplicate'
            ).addEventListener('click', function (e) {
                e.stopPropagation();
                if (!guardUnsaved()) return;
                var newName = promptDuplicateName(p.name);
                if (!newName) return;
                enterDuplicateMode(p, newName);
            });

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
        dbTestPassed = false;
        tablesTestPassed = false;
        pathsTestPassed = false;
        sectionCollapsePrefs.db = null;
        sectionCollapsePrefs.tables = null;
        sectionCollapsePrefs.science = null;
        sectionCollapsePrefs.paths = null;
        draftGroups = [];
        profileNameInput.value = '';
        profileNameInput.disabled = false;
        profileVersionInput.value = '';
        profileServerInput.value = '';
        if (profileDbSource) profileDbSource.value = 'local';
        if (profileDbDefinitionName) profileDbDefinitionName.value = '';
        DB_TEXT_FIELDS.forEach(function (f) { dbInputs[f.id].value = ''; });
        clearTableOptions(false);
        PATH_FIELDS.forEach(function (f) {
            pathInputs[f.id].value = '';
            var vdiv = document.getElementById(f.id + '-validation');
            if (vdiv) vdiv.style.display = 'none';
        });
        if (aprofileSelect) aprofileSelect.value = '';
        if (sciParamsBtnRow) sciParamsBtnRow.style.display = 'none';
        if (sciParamsPanel) sciParamsPanel.style.display = 'none';
        sciParamsData = null;
        sciParamsExpanded = new Set();
        dbTestResult.style.display = 'none';
        tablesTestResult.style.display = 'none';
        if (pathsTestResult) pathsTestResult.style.display = 'none';
        formTitle.innerHTML = '<i class="fa-solid fa-plus"></i> Add Profile';
        formSection.style.display = 'none';
        groupsSection.style.display = 'none';
        groupsContainer.innerHTML = '';
        groupsNoPerm.style.display = 'none';
        loadDbDefinitionOptions('local', '');
        syncTunnelVisibility();
        updateWorkflowState();
    }

    function enterEditMode(profile) {
        editingProfile = profile.name;
        formDirty = false;
        profileNameInput.value = profile.name;
        profileNameInput.disabled = true;
        profileVersionInput.value = profile.apero_version || '';
        profileServerInput.value = profile.reduction_server || '';
        if (profileDbSource) {
            profileDbSource.value = profile.DATABASE_SOURCE || 'local';
        }
        if (profileDbDefinitionName) {
            profileDbDefinitionName.value = profile.DATABASE_SOURCE === 'db_ssh_tunnel'
                ? (profile.DATABASE_TUNNEL_NAME || '')
                : (profile.DATABASE_LOCAL_NAME || '');
        }
        DB_TEXT_FIELDS.forEach(function (f) {
            dbInputs[f.id].value = profile[f.key] || '';
        });
        clearTableOptions(false);
        TABLE_FIELDS.forEach(function (f) {
            setSingleTableValue(f.id, profile[f.key] || '');
        });
        loadAvailableTables({ silent: true }).catch(function () {
            // Keep current saved values even if table discovery fails.
        });
        // Restore instrument profile file selection
        if (aprofileSelect) {
            aprofileSelect.value = profile.APERO_INSTRUMENT_PROFILE || '';
        }
        updateSciPreview();
        // Treat existing saved profile as already tested; tests will be
        // reset automatically if the user edits DB or table-name fields.
        dbTestPassed = true;
        tablesTestPassed = true;
        pathsTestPassed = true;
        PATH_FIELDS.forEach(function (f) {
            pathInputs[f.id].value = profile[f.key] || '';
            var vdiv = document.getElementById(f.id + '-validation');
            if (vdiv) vdiv.style.display = 'none';
        });
        dbTestResult.style.display = 'none';
        tablesTestResult.style.display = 'none';
        if (pathsTestResult) pathsTestResult.style.display = 'none';
        formTitle.innerHTML = '<i class="fa-solid fa-pen"></i> Edit Profile: ' +
            escapeHtml(profile.name);
        formSection.style.display = '';
        formTitle.scrollIntoView({ behavior: 'smooth', block: 'start' });
        renderProfileGroups(profile);
        loadDbDefinitionOptions(
            profile.DATABASE_SOURCE || 'local',
            profile.DATABASE_SOURCE === 'db_ssh_tunnel'
                ? (profile.DATABASE_TUNNEL_NAME || '')
                : (profile.DATABASE_LOCAL_NAME || '')
        );
        syncTunnelVisibility();
        updateWorkflowState();
    }

    function suggestDuplicateName(sourceName) {
        var base = String(sourceName || '').trim() || 'profile_copy';
        var candidate = base + '_copy';
        var suffix = 2;

        while (profiles.some(function (prof) {
            return String(prof.name || '') === candidate;
        })) {
            candidate = base + '_copy_' + String(suffix);
            suffix += 1;
        }
        return candidate;
    }

    function promptDuplicateName(sourceName) {
        var defaultName = suggestDuplicateName(sourceName);
        var promptMsg = 'Enter new profile name';

        while (true) {
            var input = window.prompt(promptMsg, defaultName);
            if (input === null) return null;

            var nextName = String(input || '').trim();
            if (!nextName) {
                showToast('Profile name is required', 'error');
                continue;
            }
            if (profiles.some(function (prof) {
                return String(prof.name || '') === nextName;
            })) {
                showToast('A profile with this name already exists', 'error');
                defaultName = nextName;
                continue;
            }
            return nextName;
        }
    }

    function enterDuplicateMode(profile, newName) {
        editingProfile = null;
        formDirty = false;
        dbTestPassed = true;
        tablesTestPassed = true;
        pathsTestPassed = true;

        profileNameInput.value = String(newName || '').trim();
        profileNameInput.disabled = false;
        profileVersionInput.value = profile.apero_version || '';
        profileServerInput.value = profile.reduction_server || '';

        if (profileDbSource) {
            profileDbSource.value = profile.DATABASE_SOURCE || 'local';
        }
        if (profileDbDefinitionName) {
            profileDbDefinitionName.value = profile.DATABASE_SOURCE
                === 'db_ssh_tunnel'
                ? (profile.DATABASE_TUNNEL_NAME || '')
                : (profile.DATABASE_LOCAL_NAME || '');
        }

        DB_TEXT_FIELDS.forEach(function (f) {
            dbInputs[f.id].value = profile[f.key] || '';
        });

        clearTableOptions(false);
        TABLE_FIELDS.forEach(function (f) {
            setSingleTableValue(f.id, profile[f.key] || '');
        });

        PATH_FIELDS.forEach(function (f) {
            pathInputs[f.id].value = profile[f.key] || '';
            var vdiv = document.getElementById(f.id + '-validation');
            if (vdiv) vdiv.style.display = 'none';
        });

        if (aprofileSelect) {
            aprofileSelect.value = profile.APERO_INSTRUMENT_PROFILE || '';
        }
        updateSciPreview();

        draftGroups = Array.isArray(profile.groups)
            ? profile.groups.slice()
            : [];

        dbTestResult.style.display = 'none';
        tablesTestResult.style.display = 'none';
        if (pathsTestResult) pathsTestResult.style.display = 'none';

        formTitle.innerHTML = '<i class="fa-solid fa-copy"></i> Duplicate: '
            + escapeHtml(profile.name)
            + ' → '
            + escapeHtml(String(newName || '').trim());
        formSection.style.display = '';
        formTitle.scrollIntoView({ behavior: 'smooth', block: 'start' });

        renderDraftGroups();

        loadDbDefinitionOptions(
            profile.DATABASE_SOURCE || 'local',
            profile.DATABASE_SOURCE === 'db_ssh_tunnel'
                ? (profile.DATABASE_TUNNEL_NAME || '')
                : (profile.DATABASE_LOCAL_NAME || '')
        );
        syncTunnelVisibility();
        updateWorkflowState();
        profileNameInput.focus();
        profileNameInput.select();
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

    function validatePathNow(fieldId, path) {
        var vdiv = document.getElementById(fieldId + '-validation');
        if (!vdiv) return Promise.resolve(false);
        if (!path) {
            showFieldValidation(vdiv, false, 'Path is required');
            return Promise.resolve(false);
        }
        return fetch(cfg.validateUrl + '?path=' + encodeURIComponent(path))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var ok = !!(data.success && data.valid);
                if (ok) {
                    showFieldValidation(vdiv, true, 'Directory exists');
                } else {
                    showFieldValidation(vdiv, false,
                        (data && data.error) ? data.error : 'Directory does not exist');
                }
                return ok;
            })
            .catch(function () {
                showFieldValidation(vdiv, false, 'Could not validate');
                return false;
            });
    }

    function testPaths() {
        var checks = [];
        var allFilled = true;

        PATH_FIELDS.forEach(function (f) {
            var value = pathInputs[f.id].value.trim();
            if (!value) allFilled = false;
            checks.push(validatePathNow(f.id, value));
        });

        if (!allFilled) {
            pathsTestPassed = false;
            if (pathsTestResult) {
                showFieldValidation(pathsTestResult, false,
                    'All paths are required before running path test.');
            }
            updateWorkflowState();
            return;
        }

        if (btnTestPaths) {
            btnTestPaths.disabled = true;
            btnTestPaths.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing...';
        }

        Promise.all(checks)
            .then(function (results) {
                var okCount = results.filter(function (r) { return !!r; }).length;
                pathsTestPassed = okCount === PATH_FIELDS.length;
                if (pathsTestResult) {
                    if (pathsTestPassed) {
                        showFieldValidation(pathsTestResult, true,
                            'All ' + String(PATH_FIELDS.length) + ' paths validated.');
                    } else {
                        showFieldValidation(pathsTestResult, false,
                            String(okCount) + '/' + String(PATH_FIELDS.length)
                            + ' paths validated. Fix invalid paths and test again.');
                    }
                }
            })
            .catch(function () {
                pathsTestPassed = false;
                if (pathsTestResult) {
                    showFieldValidation(pathsTestResult, false,
                        'Path test failed due to a network/server error.');
                }
            })
            .finally(function () {
                if (btnTestPaths) {
                    btnTestPaths.innerHTML = '<i class="fa-solid fa-list-check"></i> Test Paths';
                }
                updateWorkflowState();
            });
    }

    function showFieldValidation(el, valid, message) {
        el.style.display = 'block';
        el.className = 'ari-ap-validation' +
            (valid ? ' ari-ap-validation--valid' : ' ari-ap-validation--invalid');
        var icon = valid ? 'fa-circle-check' : 'fa-circle-xmark';
        el.innerHTML = '<i class="fa-solid ' + icon + '"></i> ' + escapeHtml(message);
    }

    function showFieldValidationHtml(el, valid, html) {
        el.style.display = 'block';
        el.className = 'ari-ap-validation' +
            (valid ? ' ari-ap-validation--valid' : ' ari-ap-validation--invalid');
        var icon = valid ? 'fa-circle-check' : 'fa-circle-xmark';
        el.innerHTML = '<i class="fa-solid ' + icon + '"></i> ' + html;
    }

    function isTruthy(value) {
        if (typeof value === 'boolean') return value;
        if (value === null || value === undefined) return false;
        return ['1', 'true', 'yes', 'on'].indexOf(String(value).trim().toLowerCase()) >= 0;
    }

    function splitDbHostPort(host, port) {
        var hostValue = String(host || '').trim();
        var portValue = String(port || '').trim();
        if (!portValue && hostValue && hostValue.indexOf(':') >= 0) {
            var match = hostValue.match(/^(.*):(\d+)$/);
            if (match && match[1]) {
                hostValue = match[1].trim();
                portValue = match[2].trim();
            }
        }
        return { host: hostValue, port: portValue };
    }

    function isDbTunnelEnabled() {
        return !!(profileDbSource && profileDbSource.value === 'db_ssh_tunnel');
    }

    function syncTunnelVisibility() {
        var source = profileDbSource ? profileDbSource.value : 'local';
        populateDbDefinitionSelect(source, profileDbDefinitionName ? profileDbDefinitionName.value : '');
        if (btnInteractiveTunnel) {
            btnInteractiveTunnel.style.display = 'none';
        }
    }

    function resetDbAndTableTests() {
        dbTestPassed = false;
        tablesTestPassed = false;
        availableDbTables = [];
        clearTableOptions(true);
        dbTestResult.style.display = 'none';
        tablesTestResult.style.display = 'none';
    }

    function buildDbPayload() {
        var source = isDbTunnelEnabled() ? 'db_ssh_tunnel' : 'local';
        var definitionName = profileDbDefinitionName ? profileDbDefinitionName.value.trim() : '';
        return {
            DATABASE_SOURCE: source,
            DATABASE_LOCAL_NAME: source === 'local' ? definitionName : '',
            DATABASE_TUNNEL_NAME: source === 'db_ssh_tunnel' ? definitionName : '',
            DATABASE_USERNAME: dbInputs['profile-db-user'].value.trim(),
            DATABASE_PASSWORD: dbInputs['profile-db-pass'].value,
            DATABASE_NAME: dbInputs['profile-db-name'].value.trim(),
        };
    }

    function isTableFieldsComplete() {
        for (var i = 0; i < TABLE_FIELDS.length; i++) {
            if (!tableInputs[TABLE_FIELDS[i].id].value.trim()) return false;
        }
        return true;
    }

    function lockSection(sectionEl, locked) {
        if (!sectionEl) return;
        sectionEl.classList.toggle('ari-ap-step--locked', locked);
        sectionEl.querySelectorAll('input, select, button, textarea').forEach(function (el) {
            if (el.id === 'btn-test-tables') return;
            if (el.id === 'btn-test-paths') return;
            if (el.id === 'profile-science-types') return;
            if (el.id === 'btn-save-profile') return;
            if (el.classList.contains('ari-dpr-card')) return;
            if (locked) {
                if (!el.hasAttribute('data-was-disabled')) {
                    el.setAttribute('data-was-disabled', el.disabled ? '1' : '0');
                }
                el.disabled = true;
            } else {
                var was = el.getAttribute('data-was-disabled');
                if (was !== '1') el.disabled = false;
                el.removeAttribute('data-was-disabled');
            }
        });
    }

    function setSectionCollapsed(sectionEl, statusEl, key, autoCollapsed) {
        if (!sectionEl || !statusEl) return;
        var pref = sectionCollapsePrefs[key];
        var collapsed = (pref === null) ? !!autoCollapsed : !!pref;
        sectionEl.classList.toggle('ari-ap-step--collapsed', collapsed);
        statusEl.classList.add('ari-ap-step-status--toggle');
        statusEl.title = collapsed ? 'Click to expand section' : 'Click to collapse section';
        statusEl.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
    }

    function installSectionToggle(statusEl, key) {
        if (!statusEl || statusEl.dataset.toggleInstalled === '1') return;
        statusEl.dataset.toggleInstalled = '1';
        statusEl.addEventListener('click', function () {
            var pref = sectionCollapsePrefs[key];
            var currentlyCollapsed = pref === null
                ? statusEl.getAttribute('aria-expanded') === 'false'
                : !!pref;
            sectionCollapsePrefs[key] = !currentlyCollapsed;
            updateWorkflowState();
        });
    }

    /* -- Populate instrument profile dropdown --------------------------- */
    function populateInstrumentProfileSelect() {
        if (!aprofileSelect) return;
        var data = cfg.sciProfileData || {};
        var keys = Object.keys(data).sort();
        aprofileSelect.innerHTML = '<option value="">Select profile...</option>';
        keys.forEach(function (k) {
            var opt = document.createElement('option');
            opt.value = k;
            opt.textContent = k.replace(/\.yaml$/i, '');
            aprofileSelect.appendChild(opt);
        });
    }

    /* -- Display instrument profile params button ----------------------- */
    function updateSciPreview() {
        var key = aprofileSelect ? aprofileSelect.value : '';
        var data = (cfg.sciProfileData || {})[key];
        if (!key || !data) {
            if (sciParamsBtnRow) sciParamsBtnRow.style.display = 'none';
            if (sciParamsPanel) sciParamsPanel.style.display = 'none';
            sciParamsData = null;
            sciParamsExpanded = new Set();
            return;
        }
        // Prepare params data (hide panel on profile switch)
        sciParamsData = data.params || null;
        sciParamsExpanded = new Set();
        if (sciParamsPanel) sciParamsPanel.style.display = 'none';
        if (btnShowSciParams) btnShowSciParams.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Show Parameters';
        if (sciParamsBtnRow) sciParamsBtnRow.style.display = sciParamsData ? '' : 'none';
    }

    /* -- Instrument profile params navigator ----------------------------- */
    function apEscHtml(str) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(str)));
        return d.innerHTML;
    }

    function apPxIsPrimitive(val) {
        return val === null || typeof val !== 'object';
    }

    function apPxLabel(val) {
        if (val === null) { return 'null'; }
        if (typeof val === 'boolean') { return val ? 'true' : 'false'; }
        return String(val);
    }

    // Short (≤5 items) array or dict whose values are all primitive → show inline
    function apPxIsShortSimple(val) {
        if (apPxIsPrimitive(val)) return true;
        var items = Array.isArray(val) ? val : Object.values(val);
        return items.length <= 5 && items.every(apPxIsPrimitive);
    }

    function apPxInlineFormat(val) {
        if (Array.isArray(val)) {
            return '[ ' + val.map(apPxLabel).join(', ') + ' ]';
        }
        return '{ ' + Object.keys(val).map(function (k) {
            return k + ': ' + apPxLabel(val[k]);
        }).join(', ') + ' }';
    }

    function apPxNodeId(path) {
        return path.join('::');
    }

    function apPxRows(node, path, depth) {
        if (node === undefined || node === null) {
            return '<div class="at-px-empty">No data</div>';
        }
        if (apPxIsPrimitive(node)) {
            return '<div class="at-px-row at-px-row--leaf" style="padding-left:'
                + (0.55 + depth * 1.1) + 'rem;">'
                + '<span class="at-px-row__icon"><i class="fa-solid fa-tag"></i></span>'
                + '<span class="at-px-row__key">value</span>'
                + '<span class="at-px-row__val">' + apEscHtml(apPxLabel(node)) + '</span>'
                + '</div>';
        }
        var entries = Array.isArray(node)
            ? node.map(function (v, i) { return [String(i), v]; })
            : Object.keys(node).map(function (k) { return [k, node[k]]; });
        if (entries.length === 0) {
            return '<div class="at-px-empty" style="padding-left:'
                + (0.55 + depth * 1.1) + 'rem;">(empty)</div>';
        }

        var html = '';
        entries.forEach(function (e) {
            var k = e[0], v = e[1];
            if (apPxIsShortSimple(v)) {
                var display = apPxIsPrimitive(v) ? apPxLabel(v) : apPxInlineFormat(v);
                html += '<div class="at-px-row at-px-row--leaf" style="padding-left:'
                    + (0.55 + depth * 1.1) + 'rem;">'
                    + '<span class="at-px-row__icon"><i class="fa-solid fa-tag"></i></span>'
                    + '<span class="at-px-row__key">' + apEscHtml(k) + '</span>'
                    + '<span class="at-px-row__val">' + apEscHtml(display) + '</span>'
                    + '</div>';
            } else {
                var childPath = path.concat([k]);
                var id = apPxNodeId(childPath);
                var expanded = sciParamsExpanded.has(id);
                var hint = Array.isArray(v)
                    ? ('[ ' + v.length + ' ]')
                    : ('{ ' + Object.keys(v).length + ' }');
                html += '<div class="at-px-row at-px-row--folder at-px-tree-toggle" data-node="'
                    + apEscHtml(id) + '" style="padding-left:' + (0.55 + depth * 1.1) + 'rem;">'
                    + '<span class="at-px-row__icon"><i class="fa-solid fa-'
                    + (expanded ? 'folder-open' : 'folder') + '"></i></span>'
                    + '<span class="at-px-row__key">' + apEscHtml(k) + '</span>'
                    + '<span class="at-px-row__val at-px-row__val--hint">' + hint + '</span>'
                    + '<span class="at-px-row__chevron"><i class="fa-solid fa-chevron-'
                    + (expanded ? 'down' : 'right') + '"></i></span>'
                    + '</div>';
                if (expanded) {
                    html += apPxRows(v, childPath, depth + 1);
                }
            }
        });
        return html;
    }

    function renderSciParamsExplorer() {
        if (!sciParamsExplorer) return;
        if (sciParamsBreadcrumb) {
            sciParamsBreadcrumb.innerHTML = '<span class="at-px-crumb at-px-crumb--active">Parameters Tree</span>';
        }
        sciParamsExplorer.innerHTML = apPxRows(sciParamsData, [], 0);
        sciParamsExplorer.querySelectorAll('.at-px-tree-toggle').forEach(function (el) {
            el.addEventListener('click', function () {
                var id = el.getAttribute('data-node') || '';
                if (sciParamsExpanded.has(id)) {
                    sciParamsExpanded.delete(id);
                } else {
                    sciParamsExpanded.add(id);
                }
                renderSciParamsExplorer();
            });
        });
    }

    /* -- Password visibility toggle ------------------------------------- */
    var btnToggleDbPass = document.getElementById('btn-toggle-db-pass');
    if (btnToggleDbPass) {
        btnToggleDbPass.addEventListener('click', function () {
            var inp = document.getElementById('profile-db-pass');
            if (!inp) return;
            var show = inp.type === 'password';
            inp.type = show ? 'text' : 'password';
            btnToggleDbPass.innerHTML = show
                ? '<i class="fa-solid fa-eye-slash"></i>'
                : '<i class="fa-solid fa-eye"></i>';
        });
    }

    /* -- Interactive SSH tunnel terminal -------------------------------- */
    var apSshToken = null;
    var apSshPollTimer = null;
    var btnInteractiveTunnel = document.getElementById('btn-interactive-ssh-tunnel');

    function apSshTermSetVisIcon(visible) {
        var btn = document.getElementById('apSshTermToggleVis');
        if (btn) btn.innerHTML = visible
            ? '<i class="fa-solid fa-eye-slash"></i>'
            : '<i class="fa-solid fa-eye"></i>';
    }

    function apSshShowSuccess() {
        var popup = document.getElementById('apSshSuccessPopup');
        if (popup) popup.style.display = 'flex';
    }

    function apSshDismissSuccess() {
        var popup = document.getElementById('apSshSuccessPopup');
        if (popup) popup.style.display = 'none';
        apSshTermClose();
        testDbConnection();
    }

    function apSshTermToggleVisibility() {
        var input = document.getElementById('apSshTermInput');
        if (!input) return;
        var showing = input.type === 'text';
        input.type = showing ? 'password' : 'text';
        apSshTermSetVisIcon(!showing);
    }

    function apSshTermOpen() {
        var overlay = document.getElementById('apSshTermOverlay');
        var output  = document.getElementById('apSshTermOutput');
        var input   = document.getElementById('apSshTermInput');
        var status  = document.getElementById('apSshTermStatus');
        var popup   = document.getElementById('apSshSuccessPopup');
        if (overlay) overlay.style.display = 'flex';
        if (output) output.textContent = '';
        if (input)  { input.value = ''; input.disabled = false; input.type = 'password'; }
        if (popup) popup.style.display = 'none';
        apSshTermSetVisIcon(false);
        if (status) status.textContent = 'Connecting...';
    }

    function apSshTermClose() {
        if (apSshPollTimer) { clearInterval(apSshPollTimer); apSshPollTimer = null; }
        var overlay = document.getElementById('apSshTermOverlay');
        if (overlay) overlay.style.display = 'none';

        if (apSshToken) {
            fetch(cfg.sshTunnelCloseUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: apSshToken }),
            }).catch(function () {});
            apSshToken = null;
        }
    }

    function apSshTermAppend(text) {
        var output = document.getElementById('apSshTermOutput');
        if (!output || !text) return;
        output.textContent += text;
        output.scrollTop = output.scrollHeight;
    }

    function apSshTermStartPolling() {
        if (apSshPollTimer) clearInterval(apSshPollTimer);
        apSshPollTimer = setInterval(function () {
            if (!apSshToken) return;
            fetch(cfg.sshTunnelPollUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: apSshToken }),
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.ok) {
                    apSshTermAppend('\n[Session expired or closed]\n');
                    clearInterval(apSshPollTimer);
                    apSshPollTimer = null;
                    var status = document.getElementById('apSshTermStatus');
                    if (status) status.textContent = 'Session ended.';
                    var input = document.getElementById('apSshTermInput');
                    if (input) input.disabled = true;
                    return;
                }
                if (data.output) apSshTermAppend(data.output);
                if (data.finished) {
                    clearInterval(apSshPollTimer);
                    apSshPollTimer = null;
                    var code = data.exit_code;
                    var status = document.getElementById('apSshTermStatus');
                    var input = document.getElementById('apSshTermInput');
                    if (input) input.disabled = true;
                    if (code === 0) {
                        if (status) status.textContent = 'Tunnel authenticated';
                        apSshShowSuccess();
                    } else {
                        apSshTermAppend('\n[Session ended with exit code ' + code + ']\n');
                        if (status) {
                            status.textContent = 'SSH tunnel failed (exit code ' + code + '). You can try again.';
                        }
                    }
                } else {
                    // Session is active — update status hint
                    var status = document.getElementById('apSshTermStatus');
                    if (status && data.output && data.output.length > 0) {
                        status.textContent = 'Session active — respond to any prompts below.';
                    }
                }
            })
            .catch(function () { /* network error — keep polling */ });
        }, 500);
    }

    function apSshTermSendInput() {
        var input = document.getElementById('apSshTermInput');
        if (!input || !apSshToken) return;
        var text = input.value;
        input.value = '';
        // Reset to hidden after every send
        input.type = 'password';
        apSshTermSetVisIcon(false);
        fetch(cfg.sshTunnelSendUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: apSshToken, data: text + '\n' }),
        }).catch(function () {
            apSshTermAppend('\n[Failed to send input]\n');
        });
    }

    function startInteractiveSshTunnel() {
        var selectedTunnel = profileDbDefinitionName ? profileDbDefinitionName.value.trim() : '';
        var tunnelDef = null;
        for (var i = 0; i < dbTunnelOptions.length; i++) {
            if (String(dbTunnelOptions[i].name || '').trim() === selectedTunnel) {
                tunnelDef = dbTunnelOptions[i];
                break;
            }
        }
        var sshHost = tunnelDef ? String(tunnelDef.ssh_config_host || '').trim() : '';
        var localPort = tunnelDef ? String(tunnelDef.local_port || '').trim() : '';
        var remoteHost = tunnelDef ? String(tunnelDef.remote_host || '').trim() : '';
        var remotePort = tunnelDef ? String(tunnelDef.remote_port || '').trim() : '3306';

        if (!sshHost || !localPort || !remoteHost) {
            showFieldValidation(dbTestResult, false,
                'Select a valid DB tunnel definition first');
            return;
        }

        apSshTermOpen();

        fetch(cfg.sshTunnelStartUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ssh_config_host: sshHost,
                local_port: parseInt(localPort, 10),
                remote_host: remoteHost,
                remote_port: parseInt(remotePort, 10),
            }),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.ok) {
                apSshTermAppend('[Error] ' + (data.error || 'Failed to start session.') + '\n');
                var status = document.getElementById('apSshTermStatus');
                if (status) status.textContent = 'Failed to start.';
                return;
            }
            apSshToken = data.token;
            var status = document.getElementById('apSshTermStatus');
            if (status) status.textContent = 'Session active — respond to any prompts below.';
            apSshTermStartPolling();
        })
        .catch(function (err) {
            apSshTermAppend('[Error] ' + err.message + '\n');
        });
    }

    // Wire up terminal modal controls
    var apSshTermCloseBtn = document.getElementById('apSshTermCloseBtn');
    var apSshTermSendBtn = document.getElementById('apSshTermSendBtn');
    var apSshTermInput = document.getElementById('apSshTermInput');
    var apSshTermToggleVisBtn = document.getElementById('apSshTermToggleVis');
    var apSshSuccessCloseBtn = document.getElementById('apSshSuccessCloseBtn');
    if (apSshTermCloseBtn) apSshTermCloseBtn.addEventListener('click', apSshTermClose);
    if (apSshTermSendBtn) apSshTermSendBtn.addEventListener('click', apSshTermSendInput);
    if (apSshTermToggleVisBtn) apSshTermToggleVisBtn.addEventListener('click', apSshTermToggleVisibility);
    if (apSshSuccessCloseBtn) apSshSuccessCloseBtn.addEventListener('click', apSshDismissSuccess);
    if (apSshTermInput) {
        apSshTermInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') { e.preventDefault(); apSshTermSendInput(); }
        });
    }
    if (btnInteractiveTunnel) {
        btnInteractiveTunnel.addEventListener('click', startInteractiveSshTunnel);
    }

    function updateWorkflowState() {
        syncTunnelVisibility();
        var dbFieldsFilled = dbInputs['profile-db-user'].value.trim()
            && dbInputs['profile-db-name'].value.trim();
        dbFieldsFilled = dbFieldsFilled
            && profileDbDefinitionName
            && profileDbDefinitionName.value.trim();

        installSectionToggle(tablesStepStatus, 'tables');
        installSectionToggle(scienceStepStatus, 'science');
        installSectionToggle(pathsStepStatus, 'paths');
        installSectionToggle(dbStepStatus, 'db');

        btnTestDb.disabled = !dbFieldsFilled;
        lockSection(tablesSection, !dbTestPassed);

        var tableFieldsFilled = isTableFieldsComplete();
        btnTestTables.disabled = !(dbTestPassed && tableFieldsFilled);

        // Science section is always unlocked (uses local profile file, not DB)
        lockSection(scienceSection, false);
        var selectedSciProfile = aprofileSelect ? aprofileSelect.value.trim() : '';
        var scienceComplete = !!selectedSciProfile;
        lockSection(pathsSection, !scienceComplete);

        var allPathsFilled = true;
        PATH_FIELDS.forEach(function (f) {
            if (!pathInputs[f.id].value.trim()) allPathsFilled = false;
        });
        if (btnTestPaths) {
            btnTestPaths.disabled = !(scienceComplete && allPathsFilled);
        }

        if (!dbTestPassed) {
            dbStepStatus.innerHTML = '<i class="fa-solid fa-circle-info"></i> Database test is required before continuing.';
            tablesStepStatus.innerHTML = '<i class="fa-solid fa-lock"></i> Complete and test database settings first.';
        } else {
            dbStepStatus.innerHTML = '<i class="fa-solid fa-circle-check"></i> Database test passed.';
            tablesStepStatus.innerHTML = '<i class="fa-solid fa-circle-info"></i> Fill all table names, then run table test.';
        }

        if (!scienceComplete) {
            scienceStepStatus.innerHTML = '<i class="fa-solid fa-circle-info"></i> Select an instrument profile.';
            pathsStepStatus.innerHTML = '<i class="fa-solid fa-lock"></i> Complete science settings first.';
        } else if (!allPathsFilled) {
            scienceStepStatus.innerHTML = '<i class="fa-solid fa-circle-check"></i> Science settings complete.';
            pathsStepStatus.innerHTML = '<i class="fa-solid fa-circle-info"></i> Fill all paths, then click Test Paths.';
        } else if (!pathsTestPassed) {
            scienceStepStatus.innerHTML = '<i class="fa-solid fa-circle-check"></i> Science settings complete.';
            pathsStepStatus.innerHTML = '<i class="fa-solid fa-circle-info"></i> Click Test Paths to verify all path directories.';
        } else {
            scienceStepStatus.innerHTML = '<i class="fa-solid fa-circle-check"></i> Science settings complete.';
            pathsStepStatus.innerHTML = '<i class="fa-solid fa-circle-check"></i> Paths test passed.';
        }

        var tablesDone = !!tablesTestPassed;
        var scienceDone = !!scienceComplete;
        var pathsDone = !!(scienceDone && allPathsFilled && pathsTestPassed);

        if (!tablesDone) sectionCollapsePrefs.tables = null;
        if (!scienceDone) sectionCollapsePrefs.science = null;
        if (!pathsDone) sectionCollapsePrefs.paths = null;
        if (!dbTestPassed) sectionCollapsePrefs.db = null;

        setSectionCollapsed(dbSection, dbStepStatus, 'db', !!dbTestPassed);
        setSectionCollapsed(tablesSection, tablesStepStatus, 'tables', tablesDone);
        setSectionCollapsed(scienceSection, scienceStepStatus, 'science', scienceDone);
        setSectionCollapsed(pathsSection, pathsStepStatus, 'paths', pathsDone);

        var groupsOk = false;
        if (editingProfile) {
            var current = profiles.find(function (p) { return p.name === editingProfile; });
            groupsOk = !!(current && current.groups && current.groups.length > 0);
        } else {
            groupsOk = draftGroups.length > 0;
        }

        btnSaveProfile.disabled = !(dbTestPassed && tablesTestPassed
            && pathsTestPassed
            && scienceComplete && allPathsFilled && groupsOk);
    }

    /* -- Test database connection ---------------------------------------- */
    function testDbConnection() {
        var payload = buildDbPayload();
        var user = payload.DATABASE_USERNAME;
        var name = payload.DATABASE_NAME;

        if (!user || !name) {
            showFieldValidation(dbTestResult, false,
                'DATABASE_USERNAME and DATABASE_NAME are required');
            return;
        }
        if (payload.DATABASE_SOURCE === 'local' && !payload.DATABASE_LOCAL_NAME) {
            showFieldValidation(dbTestResult, false,
                'Select a local database definition');
            return;
        }
        if (payload.DATABASE_SOURCE === 'db_ssh_tunnel' && !payload.DATABASE_TUNNEL_NAME) {
            showFieldValidation(dbTestResult, false,
                'Select a DB tunnel for db ssh tunnel source');
            return;
        }

        btnTestDb.disabled = true;
        btnTestDb.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing...';
        fetch(cfg.testDbUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            btnTestDb.disabled = false;
            btnTestDb.innerHTML = '<i class="fa-solid fa-plug"></i> Test Connection';
            if (data.requires_tunnel_admin) {
                var adminUrl = String(data.tunnel_admin_url || cfg.dbTunnelAdminUrl || '').trim();
                var msg = escapeHtml(String(data.error || 'DB tunnel is required before testing this profile.'));
                if (adminUrl) {
                    msg += ' <a href="' + encodeURI(adminUrl) + '" style="font-weight:600;">Open DB SSH Tunnel Management</a>';
                }
                showFieldValidationHtml(dbTestResult, false, msg);
                dbTestPassed = false;
                tablesTestPassed = false;
                return [];
            }
            if (data.valid) {
                showFieldValidation(dbTestResult, true, 'Connection successful');
                dbTestPassed = true;
                return loadAvailableTables({ silent: true })
                    .catch(function (err) {
                        showFieldValidation(tablesTestResult, false,
                            err.message || 'Connection succeeded, but table discovery failed');
                        return [];
                    });
            } else {
                showFieldValidation(dbTestResult, false, data.error || 'Connection failed');
                dbTestPassed = false;
                return [];
            }
        })
        .then(function () {
            if (!dbTestPassed) {
                tablesTestPassed = false;
            }
            updateWorkflowState();
        })
        .catch(function () {
            btnTestDb.disabled = false;
            btnTestDb.innerHTML = '<i class="fa-solid fa-plug"></i> Test Connection';
            showFieldValidation(dbTestResult, false, 'Request failed');
            dbTestPassed = false;
            tablesTestPassed = false;
            updateWorkflowState();
        });
    }

    function testTableNames() {
        if (!dbTestPassed) {
            showFieldValidation(tablesTestResult, false,
                'Database test must pass before table tests');
            return;
        }

        var payload = buildDbPayload();
        TABLE_FIELDS.forEach(function (f) {
            payload[f.key] = tableInputs[f.id].value.trim();
        });

        btnTestTables.disabled = true;
        btnTestTables.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing...';
        fetch(cfg.testTablesUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            btnTestTables.innerHTML =
                '<i class="fa-solid fa-vial-circle-check"></i> Test Table Names';
            if (data.requires_tunnel_admin) {
                var adminUrl = String(data.tunnel_admin_url || cfg.dbTunnelAdminUrl || '').trim();
                var msg = escapeHtml(String(data.error || 'DB tunnel is required before table tests.'));
                if (adminUrl) {
                    msg += ' <a href="' + encodeURI(adminUrl) + '" style="font-weight:600;">Open DB SSH Tunnel Management</a>';
                }
                tablesTestPassed = false;
                showFieldValidationHtml(tablesTestResult, false, msg);
                updateWorkflowState();
                return;
            }
            if (data.valid) {
                tablesTestPassed = true;
                showFieldValidation(tablesTestResult, true, 'Table checks passed.');
            } else {
                tablesTestPassed = false;
                showFieldValidation(tablesTestResult, false,
                    data.error || 'Table checks failed');
            }
            updateWorkflowState();
        })
        .catch(function () {
            btnTestTables.innerHTML =
                '<i class="fa-solid fa-vial-circle-check"></i> Test Table Names';
            tablesTestPassed = false;
            showFieldValidation(tablesTestResult, false, 'Request failed');
            updateWorkflowState();
        });
    }

    /* -- Collect all form values ----------------------------------------- */
    function collectFormData() {
        var payload = {
            instrument: currentInstrument,
            name: profileNameInput.value.trim(),
            apero_version: profileVersionInput.value.trim(),
            reduction_server: profileServerInput.value.trim(),
        };
        var dbPayload = buildDbPayload();
        Object.keys(dbPayload).forEach(function (key) {
            payload[key] = dbPayload[key];
        });
        DB_TEXT_FIELDS.forEach(function (f) {
            payload[f.key] = dbInputs[f.id].value.trim();
        });
        // PASSWORD: don't trim (may have intentional spaces)
        payload.DATABASE_PASSWORD = dbInputs['profile-db-pass'].value;
        TABLE_FIELDS.forEach(function (f) {
            payload[f.key] = tableInputs[f.id].value.trim();
        });
        // Science fields come from the selected instrument profile file
        var sciKey = aprofileSelect ? aprofileSelect.value.trim() : '';
        var sciData = (cfg.sciProfileData || {})[sciKey] || {};
        payload.APERO_INSTRUMENT_PROFILE = sciKey;
        payload.SCIENCE_FIBER = sciData.science_fiber || '';
        payload.SCIENCE_TYPES = Array.isArray(sciData.science_types)
            ? sciData.science_types.slice() : [];
        if (editingProfile) {
            var prof = profiles.find(function (p) { return p.name === editingProfile; });
            payload.groups = (prof && Array.isArray(prof.groups)) ? prof.groups.slice() : [];
        } else {
            payload.groups = draftGroups.slice();
        }
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

        var dbReq = ['DATABASE_SOURCE', 'DATABASE_LOCAL_NAME', 'DATABASE_USERNAME', 'DATABASE_NAME'];
        if (payload.DATABASE_SOURCE === 'db_ssh_tunnel') {
            dbReq = ['DATABASE_SOURCE', 'DATABASE_TUNNEL_NAME', 'DATABASE_USERNAME', 'DATABASE_NAME'];
        }
        for (var i = 0; i < dbReq.length; i++) {
            if (!payload[dbReq[i]]) {
                showToast(dbReq[i] + ' is required', 'error');
                return null;
            }
        }
        if (!dbTestPassed) {
            showToast('Database test is required before save', 'error');
            return null;
        }
        if (!tablesTestPassed) {
            showToast('Table name test is required before save', 'error');
            return null;
        }
        if (!payload.APERO_INSTRUMENT_PROFILE) {
            showToast('Instrument profile selection is required', 'error');
            return null;
        }
        if (!payload.SCIENCE_FIBER) {
            showToast('SCIENCE_FIBER not found in selected instrument profile', 'error');
            return null;
        }
        if (!payload.SCIENCE_TYPES || payload.SCIENCE_TYPES.length === 0) {
            showToast('SCIENCE_TYPES not found in selected instrument profile', 'error');
            return null;
        }
        if (!payload.groups || payload.groups.length === 0) {
            showToast('At least one group must be selected', 'error');
            return null;
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

        btnSaveProfile.disabled = true;
        fetch(cfg.saveUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(function (r) {
            return r.text().then(function (text) {
                var data = null;
                try { data = JSON.parse(text); } catch (_) { data = null; }
                return {
                    ok: r.ok,
                    status: r.status,
                    data: data,
                    text: text || ''
                };
            });
        })
        .then(function (res) {
            btnSaveProfile.disabled = false;
            var data = res.data || {};
            if (res.ok && data.success) {
                formDirty = false;
                var verb = editingProfile ? 'Updated' : 'Created';
                showToast(verb + ' "' + payload.name + '"', 'success');
                resetForm();
                loadProfiles();
            } else {
                var errMsg = data.error || '';
                if (!errMsg && res.text) {
                    errMsg = String(res.text).trim().slice(0, 220);
                }
                if (!errMsg) {
                    errMsg = 'Save failed (HTTP ' + res.status + ')';
                }
                showToast(errMsg, 'error');
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
            pathsTestPassed = false;
            var vdiv = document.getElementById(browseTargetId + '-validation');
            if (vdiv) vdiv.style.display = 'none';
            if (pathsTestResult) pathsTestResult.style.display = 'none';
            markDirty();
            updateWorkflowState();
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
                updateWorkflowState();
                showToast('Groups updated', 'success');
            } else {
                showToast(data.error || 'Update failed', 'error');
            }
        })
        .catch(function () { showToast('Network error', 'error'); });
    }

    function renderDraftGroups() {
        groupsContainer.innerHTML = '';
        var allGroups = cfg.allGroups || [];
        var canManage = new Set(cfg.canManageGroups || []);

        groupsSection.style.display = '';
        groupsTitle.innerHTML = '<i class="fa-solid fa-users-gear"></i> Profile Groups';

        if (canManage.size === 0) {
            groupsNoPerm.style.display = '';
            return;
        }
        groupsNoPerm.style.display = 'none';

        allGroups.forEach(function (group) {
            if (!canManage.has(group)) return;
            var selected = draftGroups.indexOf(group) >= 0;
            var card = document.createElement('span');
            card.className = 'ari-toggle-card ' +
                (selected ? 'ari-toggle-card--enabled' : 'ari-toggle-card--disabled');
            card.innerHTML = '<i class="fa-solid ' +
                (selected ? 'fa-check' : 'fa-xmark') +
                ' ari-toggle-card__icon"></i> ' + escapeHtml(group);
            card.title = selected ? 'Click to remove' : 'Click to add';
            card.addEventListener('click', function () {
                var idx = draftGroups.indexOf(group);
                if (idx >= 0) draftGroups.splice(idx, 1);
                else draftGroups.push(group);
                markDirty();
                renderDraftGroups();
                updateWorkflowState();
            });
            groupsContainer.appendChild(card);
        });
    }

    /* -- Event listeners ------------------------------------------------- */
    [profileNameInput, profileVersionInput, profileServerInput].forEach(function (el) {
        el.addEventListener('input', function () {
            markDirty();
            updateWorkflowState();
        });
    });
    DB_TEXT_FIELDS.forEach(function (f) {
        dbInputs[f.id].addEventListener('input', function () {
            markDirty();
            resetDbAndTableTests();
            pathsTestPassed = false;
            if (pathsTestResult) pathsTestResult.style.display = 'none';
            updateWorkflowState();
        });
    });
    TABLE_FIELDS.forEach(function (f) {
        tableInputs[f.id].addEventListener('change', function () {
            markDirty();
            tablesTestPassed = false;
            tablesTestResult.style.display = 'none';
            updateWorkflowState();
        });
    });
    if (profileDbSource) {
        profileDbSource.addEventListener('change', function () {
            markDirty();
            resetDbAndTableTests();
            pathsTestPassed = false;
            if (pathsTestResult) pathsTestResult.style.display = 'none';
            loadDbDefinitionOptions(profileDbSource.value, '');
            updateWorkflowState();
        });
    }
    if (profileDbDefinitionName) {
        profileDbDefinitionName.addEventListener('change', function () {
            markDirty();
            resetDbAndTableTests();
            pathsTestPassed = false;
            if (pathsTestResult) pathsTestResult.style.display = 'none';
            updateWorkflowState();
        });
    }

    if (aprofileSelect) {
        aprofileSelect.addEventListener('change', function () {
            markDirty();
            updateSciPreview();
            updateWorkflowState();
        });
    }

    if (btnShowSciParams) {
        btnShowSciParams.addEventListener('click', function () {
            var visible = sciParamsPanel && sciParamsPanel.style.display !== 'none';
            if (visible) {
                sciParamsPanel.style.display = 'none';
                btnShowSciParams.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Show Parameters';
            } else {
                renderSciParamsExplorer();
                if (sciParamsPanel) sciParamsPanel.style.display = '';
                btnShowSciParams.innerHTML = '<i class="fa-solid fa-eye-slash"></i> Hide Parameters';
            }
        });
    }

    PATH_FIELDS.forEach(function (f) {
        pathInputs[f.id].addEventListener('input', function () {
            markDirty();
            pathsTestPassed = false;
            var vdiv = document.getElementById(f.id + '-validation');
            if (vdiv) vdiv.style.display = 'none';
            if (pathsTestResult) pathsTestResult.style.display = 'none';
            updateWorkflowState();
        });
    });

    if (btnTestPaths) {
        btnTestPaths.addEventListener('click', testPaths);
    }

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
        renderDraftGroups();
        profileNameInput.focus();
    });

    btnTestDb.addEventListener('click', testDbConnection);
    btnTestTables.addEventListener('click', testTableNames);

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

    var apSshTermOverlay = document.getElementById('apSshTermOverlay');
    if (apSshTermOverlay) {
        apSshTermOverlay.addEventListener('click', function (e) {
            if (e.target === apSshTermOverlay) apSshTermClose();
        });
    }

    window.addEventListener('beforeunload', function (e) {
        if (formDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    /* -- Init ------------------------------------------------------------ */
    populateInstrumentProfileSelect();
    loadDbDefinitionOptions('local', '');
    renderTabs();
    updateWorkflowState();
})();
