/* ==========================================================================
   Admin Async Tasks page logic
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_ASYNC_TASKS;
    var instruments = cfg.instruments || [];
    var urls = cfg.urls;
    var GLOBAL_SCOPE = '__GLOBAL__';

    /* -----------------------------------------------------------------------
       State
    ----------------------------------------------------------------------- */
    var currentInstrument = null;
    var currentView = 'instruments';
    var allTasks = [];          // task configs for currentInstrument
    var currentProfileNames = [];
    var taskClasses = [];       // available task classes from server
    var selectedTaskId = null;
    var editingTaskId = null;   // null = add, string = edit
    var pendingDeleteId = null;
    var pollTimer = null;
    var POLL_FAST_MS = 1000;
    var POLL_SLOW_MS = 5000;
    var OUTPUT_PREVIEW_PER_TYPE = 3;
    var pollIntervalMs = POLL_SLOW_MS;
    var dragSrcId = null;

    /* -----------------------------------------------------------------------
       DOM refs
    ----------------------------------------------------------------------- */
    var tabsEl          = document.getElementById('at-tabs');
    var instrumentPicker = document.getElementById('at-instrument-picker');
    var instrumentCards = document.getElementById('at-instrument-cards');
    var instrWs         = document.getElementById('at-instrument-workspace');
    var queueWs         = document.getElementById('at-queue-workspace');
    var noInstrEl       = document.getElementById('at-no-instruments');

    var btnRunAll       = document.getElementById('btn-run-all');
    var btnForceRunAll  = document.getElementById('btn-force-run-all');
    var runningBadge    = document.getElementById('at-running-badge');

    var activeList      = document.getElementById('active-task-list');
    var inactiveList    = document.getElementById('inactive-task-list');
    var activeCount     = document.getElementById('active-count');
    var inactiveCount   = document.getElementById('inactive-count');

    var detailEmpty     = document.getElementById('at-detail-empty');
    var detailCard      = document.getElementById('at-detail');

    var detName         = document.getElementById('det-name');
    var detStatusBadge  = document.getElementById('det-status-badge');
    var detTaskKey      = document.getElementById('det-task-key');
    var detDesc         = document.getElementById('det-description');
    var detFreq         = document.getElementById('det-frequency');
    var detParallelRow  = document.getElementById('det-parallel-row');
    var detParallel     = document.getElementById('det-parallel');
    var detSyncModeRow  = document.getElementById('det-sync-mode-row');
    var detSyncMode     = document.getElementById('det-sync-mode');
    var detBackupRetentionRow = document.getElementById(
        'det-backup-retention-row');
    var detBackupRetention    = document.getElementById(
        'det-backup-retention');
    var detBackupMaxSizeRow   = document.getElementById(
        'det-backup-max-size-row');
    var detBackupMaxSize      = document.getElementById(
        'det-backup-max-size');
    var detBackupExcludeDirsRow = document.getElementById(
        'det-backup-exclude-dirs-row');
    var detBackupExcludeDirs    = document.getElementById(
        'det-backup-exclude-dirs');
    var detBackupExcludePathsRow = document.getElementById(
        'det-backup-exclude-paths-row');
    var detBackupExcludePaths    = document.getElementById(
        'det-backup-exclude-paths');
    var detKvList       = document.getElementById('det-kv-list');
    var detProgressRow  = document.getElementById('det-progress-row');
    var detProgressFill = document.getElementById('det-progress-fill');
    var detProgressPct  = document.getElementById('det-progress-pct');
    var detSubprogressRow  = document.getElementById('det-subprogress-row');
    var detSubprogressFill = document.getElementById('det-subprogress-fill');
    var detSubprogressPct  = document.getElementById('det-subprogress-pct');
    var detLastRun      = document.getElementById('det-last-run');
    var detRunCount     = document.getElementById('det-run-count');
    var detFiltersWarning = document.getElementById('det-filters-warning');
    var detFiltersWarningList = document.getElementById(
        'det-filters-warning-list'
    );
    // Section cards
    var detInfoSection  = document.getElementById('det-info-section');
    var detInfoBody     = document.getElementById('det-info-body');
    var detInfoEl       = document.getElementById('det-info');
    var detInfoEmpty    = document.getElementById('det-info-empty');
    var detBtnToggleInfo= document.getElementById('det-btn-toggle-info');
    var detBtnCopyInfo  = document.getElementById('det-btn-copy-info');
    var detErrorSection = document.getElementById('det-error-section');
    var detErrorBody    = document.getElementById('det-error-body');
    var detError        = document.getElementById('det-error');
    var detBtnToggleError = document.getElementById('det-btn-toggle-error');
    var detBtnCopyError = document.getElementById('det-btn-copy-error');
    var detParamsSection      = document.getElementById('det-params-section');
    var detParamsBody         = document.getElementById('det-params-body');
    var detParamsBreadcrumb   = document.getElementById('det-params-breadcrumb');
    var detParamsExplorer     = document.getElementById('det-params-explorer');
    var detBtnToggleParams    = document.getElementById('det-btn-toggle-params');
    var detFilesSection = document.getElementById('det-files-section');
    var detBtnPurgeFiles = document.getElementById('det-btn-purge-files');
    var detOutputFiles  = document.getElementById('det-output-files');

    var detBtnToggle    = document.getElementById('det-btn-toggle');
    var detBtnEdit      = document.getElementById('det-btn-edit');
    var detBtnDelete    = document.getElementById('det-btn-delete');
    var detBtnRunNow    = document.getElementById('det-btn-run-now');
    var detBtnForceRun  = document.getElementById('det-btn-force-run');
    var detBtnStop      = document.getElementById('det-btn-stop');
    var detBtnViewLog   = document.getElementById('det-btn-view-log');

    // Queue tab
    var btnStopAll          = document.getElementById('btn-stop-all');
    var btnKillAll          = document.getElementById('btn-kill-all');
    var btnClearHistory     = document.getElementById('btn-clear-history');
    var queueRunning        = document.getElementById('queue-running');
    var queueRunningName    = document.getElementById('queue-running-name');
    var queueRunningInstr   = document.getElementById('queue-running-instrument');
    var queueProgressFill   = document.getElementById('queue-progress-fill');
    var queueProgressPct    = document.getElementById('queue-progress-pct');
    var queueSubprogressRow = document.getElementById('queue-subprogress-row');
    var queueSubprogressFill= document.getElementById('queue-subprogress-fill');
    var queueSubprogressPct = document.getElementById('queue-subprogress-pct');
    var queueRunningInfo    = document.getElementById('queue-running-info');
    var queueBtnViewLog     = document.getElementById('queue-btn-view-log');
    var queueBtnStop        = document.getElementById('queue-btn-stop');
    var queuePendingList    = document.getElementById('queue-pending-list');
    var queueHistoryList    = document.getElementById('queue-history-list');

    // Edit modal
    var editModal       = document.getElementById('at-edit-modal');
    var editModalTitle  = document.getElementById('edit-modal-title');
    var editTaskKey     = document.getElementById('edit-task-key');
    var editTaskInfoRow = document.getElementById('edit-task-info-row');
    var editTaskName    = document.getElementById('edit-task-name');
    var editTaskDesc    = document.getElementById('edit-task-desc');
    var editTabRunBtn   = document.getElementById('edit-tab-run');
    var editTabFiltersBtn = document.getElementById('edit-tab-filters');
    var editPaneRun     = document.getElementById('edit-pane-run');
    var editPaneFilters = document.getElementById('edit-pane-filters');
    var editFrequency   = document.getElementById('edit-frequency');
    var editLegacyGsheetFields = document.getElementById(
        'edit-legacy-gsheet-fields');
    var editDryRun      = document.getElementById('edit-dry-run');
    var editGoogleSecretName = document.getElementById(
        'edit-google-secret-name');
    var editGoogleOauthFile = document.getElementById(
        'edit-google-oauth-file');
    var editGoogleOauthHint = document.getElementById(
        'edit-google-oauth-hint');
    var editGoogleOauthAuthBtn = document.getElementById(
        'at-gsheet-oauth-authorize-btn');
    var editCheckGsheetUrlFields = document.getElementById(
        'edit-check-gsheet-url-fields');
    var editOverrideSheetUrlField = document.getElementById(
        'edit-override-sheet-url-field');
    var editMonitoringSheetUrl = document.getElementById(
        'edit-monitoring-sheet-url');
    var editOverrideSheetUrl = document.getElementById(
        'edit-override-sheet-url');
    var editKnownErrorsSheetUrlField = document.getElementById(
        'edit-known-errors-sheet-url-field');
    var editKnownErrorsSheetUrl = document.getElementById(
        'edit-known-errors-sheet-url');
    var editBackupFields= document.getElementById('edit-backup-fields');
    var editDailyCopies = document.getElementById('edit-daily-copies');
    var editWeeklyCopies= document.getElementById('edit-weekly-copies');
    var editBackupMaxSizeMb = document.getElementById(
        'edit-backup-max-size-mb');
    var editBackupMaxSizeSaved = document.getElementById(
        'edit-backup-max-size-saved');
    var editBackupExcludeDirs = document.getElementById(
        'edit-backup-exclude-dirs');
    var editBackupExcludePaths = document.getElementById(
        'edit-backup-exclude-paths');
    var editBackupExcludeDirsDefault = document.getElementById(
        'edit-backup-exclude-dirs-default');
    var editBackupExcludePathsDefault = document.getElementById(
        'edit-backup-exclude-paths-default');
    var editAssetsFields= document.getElementById('edit-assets-fields');
    var editAssetsMode  = document.getElementById('edit-assets-mode');
    var editAssetsLocalSrcRow = document.getElementById(
        'edit-assets-local-source-row');
    var editAssetsLocalSrc = document.getElementById(
        'edit-assets-local-source');
    var editAssetsLocalBrowse = document.getElementById(
        'edit-assets-local-browse');
    var editAssetsDrsUconfigRow = document.getElementById(
        'edit-assets-drs-uconfig-row');
    var editAssetsDrsUconfig = document.getElementById(
        'edit-assets-drs-uconfig');
    var editAssetsDrsUconfigBrowse = document.getElementById(
        'edit-assets-drs-uconfig-browse');
    var editMpFields    = document.getElementById('edit-mp-fields');
    var editNcores      = document.getElementById('edit-ncores');
    var editMpBackend   = document.getElementById('edit-mp-backend');
    var editMpStartMethod = document.getElementById('edit-mp-start-method');
    var editMpWarn      = document.getElementById('edit-mp-warn');
    var editLocalSyncFields = document.getElementById('edit-local-sync-fields');
    var editSyncProfilesEmpty = document.getElementById(
        'edit-sync-profiles-empty');
    var editSyncProfilesWrap = document.getElementById(
        'edit-sync-profiles-wrap');
    var editSyncProfilesBody = document.getElementById(
        'edit-sync-profiles-body');
    var editRunCountRow = document.getElementById('edit-run-count-row');
    var editRunCount    = document.getElementById('edit-run-count');
    var editActive      = document.getElementById('edit-active');
    var editFiltersEmpty = document.getElementById('edit-filters-empty');
    var editFiltersContainer = document.getElementById('edit-filters-container');
    var btnEditCancel   = document.getElementById('btn-edit-cancel');
    var btnEditSave     = document.getElementById('btn-edit-save');
    var btnEditClose    = document.getElementById('btn-edit-modal-close');

    // Delete modal
    var deleteModal     = document.getElementById('at-delete-modal');
    var deleteModalName = document.getElementById('delete-modal-name');
    var btnDeleteCancel = document.getElementById('btn-delete-cancel');
    var btnDeleteConfirm= document.getElementById('btn-delete-confirm');

    // Run All modal
    var runAllModal     = document.getElementById('at-runall-modal');
    var btnRunAllReplace= document.getElementById('btn-runall-replace');
    var btnRunAllAdd    = document.getElementById('btn-runall-add');
    var btnRunAllCancel = document.getElementById('btn-runall-cancel');
    var runAllForceMode = false;
    var editFilterInputs = {};

    // File viewer modal
    var fileModal       = document.getElementById('at-file-modal');
    var fileModalTitle  = document.getElementById('file-modal-title');
    var fileModalContent= document.getElementById('file-modal-content');
    var btnFileModalClose= document.getElementById('btn-file-modal-close');
    var btnFileModalOk  = document.getElementById('btn-file-modal-ok');

    var taskLogModal = document.getElementById('at-task-log-modal');
    var taskLogModalTitle = document.getElementById('task-log-modal-title');
    var taskLogModalContent = document.getElementById('task-log-modal-content');
    var btnTaskLogClose = document.getElementById('btn-task-log-close');
    var btnTaskLogCloseX = document.getElementById('btn-task-log-close-x');
    var btnTaskLogRefresh = document.getElementById('btn-task-log-refresh');
    var btnTaskLogCopy = document.getElementById('btn-task-log-copy');

    var syncBrowseModal = document.getElementById('at-sync-browse-modal');
    var syncBrowsePathInput = document.getElementById(
        'sync-browse-path-input');
    var syncBrowseStatus = document.getElementById('sync-browse-status');
    var syncBrowseList = document.getElementById('sync-browse-list');
    var btnSyncBrowseGo = document.getElementById('btn-sync-browse-go');
    var btnSyncBrowseClose = document.getElementById(
        'btn-sync-browse-close');
    var btnSyncBrowseCloseX = document.getElementById(
        'btn-sync-browse-close-x');
    var btnSyncBrowseSelect = document.getElementById(
        'btn-sync-browse-select');
    var syncBrowsePath = '/';
    var syncBrowseTargetInput = null;

    var BACKUP_TASK_KEY = 'ARI_LOCAL_DATA_BACKUP';
    var ASSETS_TASK_KEY = 'APERO_SYNC_ASSETS';
    var LEGACY_ASTROM_TASK_KEY       = 'LEGACY_ASTROM_GSHEET';
    var LEGACY_REJECT_TASK_KEY       = 'LEGACY_REJECT_GSHEET';
    var LEGACY_CHECK_TASK_KEY        = 'LEGACY_CHECK_GSHEET';
    var LEGACY_KNOWN_ERRORS_TASK_KEY = 'LEGACY_KNOWN_ERRORS_GSHEET';

    function normalizeInstrumentKey(value) {
        return String(value || '')
            .trim()
            .toUpperCase()
            .replace(/-/g, '_');
    }

    function getLegacyCheckUrl(task, mapKey, singleKey) {
        if (!task || typeof task !== 'object') return '';
        var mapObj = task[mapKey];
        var instrumentKey = normalizeInstrumentKey(currentInstrument);
        if (mapObj && typeof mapObj === 'object' && instrumentKey) {
            var perInstrument = String(
                mapObj[instrumentKey] || ''
            ).trim();
            if (perInstrument) return perInstrument;
        }
        return String(task[singleKey] || '').trim();
    }

    var currentInfoText = '';
    var currentErrorText = '';
    var currentTaskLogText = '';
    var currentParamsData = null;   // { 'Task Params': {...}, 'Input Params': {...} }
    var currentParamsExpanded = new Set();
    var currentParamsOwnerTaskId = null;
    var openTaskLogTaskId = null;
    var taskLogRefreshTimer = null;
    var mpConfig = {
        max_cores: 1,
        recommended_max_cores: 1,
        backends: ['threads', 'processes'],
        start_methods: ['default', 'spawn', 'fork', 'forkserver'],
    };

    var toast = document.getElementById('at-toast');

    /* -----------------------------------------------------------------------
       Initialisation
    ----------------------------------------------------------------------- */
    function init() {
        // If the page skeleton is not present, skip binding to avoid hard JS errors.
        if (!tabsEl || !instrWs || !queueWs || !detailEmpty || !detailCard) {
            return;
        }
        renderTabs();
        renderInstrumentCards();
        loadTaskClasses();
        bindEditModal();
        bindDeleteModal();
        bindRunAllModal();
        bindQueue();
        bindRunAll();
        bindFileModal();
        bindTaskLogModal();
        bindSyncBrowseModal();
        bindSectionToggles();
        bindOauthHelpModal();

        if (instruments.length === 0) {
            noInstrEl.style.display = '';
        } else {
            selectTab('instruments');
        }
    }

    /* -----------------------------------------------------------------------
       Tabs
    ----------------------------------------------------------------------- */
    function renderTabs() {
        if (!tabsEl) return;
        tabsEl.innerHTML = '';
        [
            { value: 'global', label: '<i class="fa-solid fa-globe"></i> Global' },
            { value: 'instruments', label: '<i class="fa-solid fa-satellite-dish"></i> Instruments' },
            { value: 'queue', label: '<i class="fa-solid fa-layer-group"></i> Queue' },
        ].forEach(function (tabDef) {
            var btn = document.createElement('button');
            btn.className = 'ari-sg-tab';
            btn.innerHTML = tabDef.label;
            btn.dataset.value = tabDef.value;
            btn.addEventListener('click', function () { selectTab(tabDef.value); });
            tabsEl.appendChild(btn);
        });
    }

    function renderInstrumentCards() {
        if (!instrumentCards) return;
        instrumentCards.innerHTML = '';
        instruments.forEach(function (inst) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'at-instrument-card';
            btn.textContent = inst;
            btn.dataset.instrument = inst;
            btn.addEventListener('click', function () {
                currentInstrument = inst;
                highlightInstrumentCard();
                loadTasks();
            });
            instrumentCards.appendChild(btn);
        });
        highlightInstrumentCard();
    }

    function highlightInstrumentCard() {
        if (!instrumentCards) return;
        Array.from(instrumentCards.querySelectorAll('.at-instrument-card')).forEach(function (btn) {
            btn.classList.toggle('at-instrument-card--active', btn.dataset.instrument === currentInstrument);
        });
    }

    function selectTab(value) {
        if (!tabsEl) return;
        // Update active styling
        Array.from(tabsEl.querySelectorAll('.ari-sg-tab')).forEach(function (b) {
            b.classList.toggle('ari-sg-tab--active', b.dataset.value === value);
        });

        stopPoll();
        currentView = value;

        if (value === 'queue') {
            currentInstrument = null;
            if (instrumentPicker) instrumentPicker.style.display = 'none';
            instrWs.style.display = 'none';
            queueWs.style.display = '';
            noInstrEl.style.display = 'none';
            refreshQueueView();
            startPoll();
            return;
        }

        queueWs.style.display = 'none';
        instrWs.style.display = '';
        noInstrEl.style.display = 'none';
        selectedTaskId = null;
        showDetail(null);

        if (value === 'global') {
            currentInstrument = GLOBAL_SCOPE;
            if (instrumentPicker) instrumentPicker.style.display = 'none';
            if (btnRunAll) {
                btnRunAll.innerHTML = '<i class="fa-solid fa-play"></i> Run All Global';
            }
            loadGlobalTasks();
            startPoll();
            return;
        }

        if (instrumentPicker) instrumentPicker.style.display = '';
        if (!currentInstrument || currentInstrument === GLOBAL_SCOPE) {
            currentInstrument = instruments[0] || null;
        }
        highlightInstrumentCard();
        if (btnRunAll) {
            btnRunAll.innerHTML = '<i class="fa-solid fa-play"></i> Run All';
        }
        queueWs.style.display = 'none';
        noInstrEl.style.display = 'none';
        loadTasks();
        startPoll();
    }

    /* -----------------------------------------------------------------------
       Task list
    ----------------------------------------------------------------------- */
    function loadTasks() {
        if (!currentInstrument || currentInstrument === GLOBAL_SCOPE) return;
        fetch(urls.list + '?instrument=' + encodeURIComponent(currentInstrument))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) { showToast('Failed to load tasks: ' + data.error, 'error'); return; }
                allTasks = data.tasks || [];
                currentProfileNames = Array.isArray(data.profile_names)
                    ? data.profile_names
                    : [];
                renderTaskLists();
                updateRunningBadge(data.queue);
                if (selectedTaskId) {
                    var selected = allTasks.find(function (t) { return t.id === selectedTaskId; });
                    if (selected) {
                        showDetail(selected);
                    } else {
                        showDetail(null);
                    }
                }
            });
    }

    function loadGlobalTasks() {
        fetch(urls.globalList)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) { showToast('Failed to load global tasks: ' + data.error, 'error'); return; }
                allTasks = data.tasks || [];
                renderTaskLists();
                updateRunningBadge(data.queue);
                if (selectedTaskId) {
                    var selected = allTasks.find(function (t) { return t.id === selectedTaskId; });
                    if (selected) {
                        showDetail(selected);
                    } else {
                        showDetail(null);
                    }
                }
            });
    }

    function refreshCurrentTasks() {
        if (currentInstrument === GLOBAL_SCOPE) {
            loadGlobalTasks();
            return;
        }
        loadTasks();
    }

    function renderTaskLists() {
        if (!activeList || !inactiveList || !activeCount || !inactiveCount) return;
        var active   = allTasks.filter(function (t) { return t.active !== false; });
        var inactive = allTasks.filter(function (t) { return t.active === false; });
        var draggable = (currentInstrument !== GLOBAL_SCOPE);

        activeCount.textContent   = active.length;
        inactiveCount.textContent = inactive.length;

        renderList(activeList, active, draggable);
        renderList(inactiveList, inactive, false);
    }

    function renderList(container, tasks, draggable) {
        container.innerHTML = '';
        if (tasks.length === 0) {
            container.innerHTML = '<div class="ari-sg-empty-small">None</div>';
            return;
        }
        tasks.forEach(function (task) {
            var card = buildTaskCard(task, draggable);
            container.appendChild(card);
        });
    }

    function buildTaskCard(task, draggable) {
        var rt = task.runtime || {};
        var status = rt.found ? rt.status : 'not_started';
        var isRunning = (status === 'in_progress');
        var isQueued  = rt.is_queued;
        var hasError = (status === 'failed') || !!String(rt.error || '').trim();

        var card = document.createElement('div');
        card.className = 'at-task-card' +
            (task.active !== false ? ' at-task-card--active' : '') +
            (task.id === selectedTaskId ? ' at-task-card--selected' : '') +
            (task.active === false ? ' at-task-card--inactive' : '') +
            (hasError ? ' at-task-card--error' : '');
        card.dataset.id = task.id;

        var grip = draggable
            ? '<span class="at-task-card__grip" title="Drag to reorder">' +
              '<i class="fa-solid fa-grip-vertical"></i></span>'
            : '';

        var statusDot = '<span class="at-task-dot at-task-dot--' + statusClass(status) + '"></span>';

        var progressHtml = (isRunning || isQueued)
            ? '<div class="at-card-progress"><div class="at-card-progress__fill" style="width:' +
              Math.round((rt.progress || 0) * 100) + '%;"></div></div>'
            : '';

        var tags = '';
        if (isQueued) {
            tags += '<span class="at-tag at-tag--queued">queued</span>';
        } else if (isRunning) {
            tags += '<span class="at-tag at-tag--running">running</span>';
        }
        if (hasError) {
            tags += '<span class="at-tag at-tag--error">ERROR</span>';
        }

        var instLabel = (currentInstrument && currentInstrument !== GLOBAL_SCOPE)
            ? '<span class="at-task-card__inst">' + esc(currentInstrument) + ':</span> '
            : '';

        card.innerHTML =
            grip + statusDot +
            '<div class="at-task-card__body">' +
                '<span class="at-task-card__name">' + instLabel + esc(task.name || task.task_key) + '</span>' +
                '<span class="at-task-card__freq">' + (task.frequency ? esc(task.frequency) + ' hrs' : '') + '</span>' +
                tags +
            '</div>' +
            progressHtml;

        card.addEventListener('click', function () {
            selectedTaskId = task.id;
            highlightSelected();
            showDetail(task);
        });

        if (draggable) {
            card.setAttribute('draggable', 'true');
            card.addEventListener('dragstart', function (e) {
                dragSrcId = task.id;
                e.dataTransfer.effectAllowed = 'move';
                card.classList.add('at-task-card--dragging');
            });
            card.addEventListener('dragend', function () {
                card.classList.remove('at-task-card--dragging');
                activeList.querySelectorAll('.at-task-card--dragover').forEach(function (c) {
                    c.classList.remove('at-task-card--dragover');
                });
                dragSrcId = null;
            });
            card.addEventListener('dragover', function (e) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                card.classList.add('at-task-card--dragover');
            });
            card.addEventListener('dragleave', function () {
                card.classList.remove('at-task-card--dragover');
            });
            card.addEventListener('drop', function (e) {
                e.preventDefault();
                card.classList.remove('at-task-card--dragover');
                if (dragSrcId && dragSrcId !== task.id) {
                    reorderTasks(dragSrcId, task.id);
                }
            });
        }

        return card;
    }

    function highlightSelected() {
        document.querySelectorAll('.at-task-card').forEach(function (c) {
            c.classList.toggle('at-task-card--selected', c.dataset.id === selectedTaskId);
        });
    }

    /* -----------------------------------------------------------------------
       Drag reorder
    ----------------------------------------------------------------------- */
    function reorderTasks(srcId, targetId) {
        var active = allTasks.filter(function (t) { return t.active !== false; });
        var srcIdx = active.findIndex(function (t) { return t.id === srcId; });
        var tgtIdx = active.findIndex(function (t) { return t.id === targetId; });
        if (srcIdx < 0 || tgtIdx < 0) return;

        var moved = active.splice(srcIdx, 1)[0];
        active.splice(tgtIdx, 0, moved);

        var inactive = allTasks.filter(function (t) { return t.active === false; });
        allTasks = active.concat(inactive);
        renderTaskLists();

        var orderList = active.map(function (t) { return t.id; });
        fetch(urls.reorder, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instrument: currentInstrument, order: orderList }),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (!d.success) { showToast('Reorder failed: ' + d.error, 'error'); }
        });
    }

    /* -----------------------------------------------------------------------
       Detail panel
    ----------------------------------------------------------------------- */
    function restripeKvList() {
        if (!detKvList) return;
        var rows = detKvList.querySelectorAll('.at-kv-row');
        var i = 0;
        rows.forEach(function (row) {
            // Skip rows hidden via inline display:none
            if (row.style.display === 'none') {
                row.classList.remove('at-kv-row--alt');
                return;
            }
            if (i % 2 === 1) {
                row.classList.add('at-kv-row--alt');
            } else {
                row.classList.remove('at-kv-row--alt');
            }
            i += 1;
        });
    }

    function showDetail(task) {
        if (!task) {
            detailCard.style.display = 'none';
            detailEmpty.style.display = '';
            return;
        }

        detailEmpty.style.display = 'none';
        detailCard.style.display = '';

        var cls = taskClasses.find(function (c) { return c.key === task.task_key; }) || {};
        detName.textContent = cls.name || task.task_key;
        detTaskKey.textContent = task.task_key;
        detDesc.textContent = cls.description || '';
        detFreq.textContent = task.frequency ? task.frequency + ' hrs' : '';
        if (detParallelRow && detParallel) {
            var supportsMp = !!cls.multi_process
                || ('ncores' in task)
                || ('mp_backend' in task)
                || ('mp_start_method' in task);
            if (supportsMp) {
                var ncores = parseInt(task.ncores, 10) || 1;
                var backend = String(task.mp_backend || 'threads');
                var method = String(task.mp_start_method || 'default');
                detParallel.textContent = 'NCORES=' + ncores + ', backend=' + backend + ', method=' + method;
                detParallelRow.style.display = '';
            } else {
                detParallel.textContent = '';
                detParallelRow.style.display = 'none';
            }
        }
        if (detSyncModeRow && detSyncMode) {
            var supportsLocalTask = !!cls.local_task
                || !!task.local_task
                || ('sync_source' in task)
                || ('sync_profiles' in task);
            if (supportsLocalTask) {
                var syncProfiles = getTaskSyncProfiles(task);
                var fetchNames = Object.keys(syncProfiles);
                var legacySync = String(task.sync_source || '').trim();
                if (fetchNames.length) {
                    var totalProfiles = currentProfileNames.length
                        || fetchNames.length;
                    var runCount = Math.max(
                        totalProfiles - fetchNames.length,
                        0
                    );
                    detSyncMode.textContent = fetchNames.length
                        + ' profile(s) fetch pre-computed'
                        + (runCount
                            ? '; ' + runCount + ' run on server'
                            : '');
                } else if (legacySync) {
                    detSyncMode.textContent = 'Legacy sync source: '
                        + legacySync;
                } else {
                    detSyncMode.textContent = 'All profiles run on server';
                }
                detSyncModeRow.style.display = '';
            } else {
                detSyncMode.textContent = '';
                detSyncModeRow.style.display = 'none';
            }
        }

        // Backup-task specific rows (retention + max archive size)
        var isBackupTask = (task.task_key === BACKUP_TASK_KEY);
        if (detBackupRetentionRow && detBackupRetention) {
            if (isBackupTask) {
                var dc = parseInt(task.daily_copies, 10);
                var wc = parseInt(task.weekly_copies, 10);
                if (!isFinite(dc)) dc = 0;
                if (!isFinite(wc)) wc = 0;
                detBackupRetention.textContent =
                    dc + ' daily, ' + wc + ' weekly';
                detBackupRetentionRow.style.display = '';
            } else {
                detBackupRetention.textContent = '';
                detBackupRetentionRow.style.display = 'none';
            }
        }
        if (detBackupMaxSizeRow && detBackupMaxSize) {
            if (isBackupTask) {
                var maxMb = parseFloat(task.backup_max_size_mb);
                if (!isFinite(maxMb) || maxMb <= 0) {
                    maxMb = 1024;
                }
                var maxMbStr = (maxMb % 1 === 0)
                    ? String(maxMb)
                    : maxMb.toFixed(2).replace(/\.?0+$/, '');
                detBackupMaxSize.textContent = maxMbStr + ' MB';
                detBackupMaxSize.title = maxMbStr + ' MB ('
                    + (maxMb / 1024).toFixed(2) + ' GiB)';
                detBackupMaxSizeRow.style.display = '';
            } else {
                detBackupMaxSize.textContent = '';
                detBackupMaxSize.title = '';
                detBackupMaxSizeRow.style.display = 'none';
            }
        }
        // Backup exclude lists. Display the effective list:
        // admin override if set, otherwise the built-in defaults.
        var renderExcludeRow = function (rowEl, valEl, override, defaults) {
            if (!rowEl || !valEl) return;
            if (!isBackupTask) {
                valEl.textContent = '';
                valEl.title = '';
                rowEl.style.display = 'none';
                return;
            }
            var ov = Array.isArray(override) ? override : [];
            var df = Array.isArray(defaults) ? defaults : [];
            var effective = ov.length ? ov : df;
            var suffix = ov.length ? ' (custom)' : ' (default)';
            valEl.textContent = (effective.length
                ? effective.join(', ')
                : '(none)') + suffix;
            valEl.title = effective.join('\n');
            rowEl.style.display = '';
        };
        renderExcludeRow(
            detBackupExcludeDirsRow, detBackupExcludeDirs,
            task.exclude_dirs, task.default_exclude_dirs);
        renderExcludeRow(
            detBackupExcludePathsRow, detBackupExcludePaths,
            task.exclude_paths, task.default_exclude_paths);

        if (detFiltersWarning && detFiltersWarningList) {
            var rawFilters = (task.filters && typeof task.filters === 'object')
                ? task.filters
                : {};
            var appliedKeys = Object.keys(rawFilters).filter(function (key) {
                var value = String(rawFilters[key] || '').trim();
                return value.length > 0;
            });

            if (appliedKeys.length > 0) {
                var items = appliedKeys.map(function (key) {
                    var value = String(rawFilters[key] || '').trim();
                    return '<li><strong>' + esc(key) + ':</strong> '
                        + '<code>' + esc(value) + '</code></li>';
                });
                detFiltersWarningList.innerHTML = items.join('');
                detFiltersWarning.style.display = '';
            } else {
                detFiltersWarningList.innerHTML = '';
                detFiltersWarning.style.display = 'none';
            }
        }

        var isActive = task.active !== false;
        detBtnToggle.querySelector('i').className =
            'fa-solid ' + (isActive ? 'fa-toggle-on' : 'fa-toggle-off');
        detBtnToggle.title = isActive ? 'Deactivate task' : 'Activate task';

        restripeKvList();
        updateDetailRuntime();
    }

    function updateDetailRuntime() {
        var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
        if (!task) return;

        var rt = task.runtime || {};
        var status = rt.found ? rt.status : 'not_started';
        var progress = rt.found ? (rt.progress || 0) : 0;
        var subprogress = rt.found ? (rt.subprogress || 0) : 0;
        var useSubprocess = !!rt.use_subprocess;

        detStatusBadge.textContent = status.replace(/_/g, ' ');
        detStatusBadge.className = 'at-status-badge at-status-badge--' + statusClass(status);

        var isActive = (status === 'in_progress' || status === 'queued' || status === 'cancelling');
        detProgressRow.style.display = isActive ? '' : 'none';
        if (isActive) {
            var pct = (progress * 100).toFixed(2);
            detProgressFill.style.width = pct + '%';
            detProgressPct.textContent = pct + '%';
        }

        if (detSubprogressRow) {
            var showSub = isActive && useSubprocess;
            detSubprogressRow.style.display = showSub ? '' : 'none';
            if (showSub) {
                var subPct = (subprogress * 100).toFixed(2);
                detSubprogressFill.style.width = subPct + '%';
                detSubprogressPct.textContent = subPct + '%';
            }
        }

        // Stop button: show when running, queued, or cancelling
        var canStop = (status === 'in_progress' || status === 'queued' || status === 'cancelling');
        if (detBtnStop) {
            detBtnStop.style.display = canStop ? '' : 'none';
            detBtnStop.disabled = (status === 'cancelling');
            detBtnStop.title = (status === 'cancelling') ? 'Cancellation requested…' : 'Stop this task';
        }

        detLastRun.textContent = (rt.last_run && rt.last_run !== 'Never') ? rt.last_run : 'Never';
        detRunCount.textContent = (rt.run_count !== undefined) ? rt.run_count : 0;

        // Info section
        if (rt.info) {
            currentInfoText = String(rt.info);
            detInfoEl.style.display = '';
            detInfoEmpty.style.display = 'none';
            if (window.marked) {
                detInfoEl.innerHTML = window.marked.parse(rt.info);
            } else {
                detInfoEl.innerHTML = '<pre>' + esc(rt.info) + '</pre>';
            }
        } else {
            currentInfoText = '';
            detInfoEl.style.display = 'none';
            detInfoEmpty.style.display = '';
        }

        // Error section
        if (rt.error) {
            currentErrorText = String(rt.error);
            detErrorSection.style.display = '';
            detError.textContent = rt.error;
        } else {
            currentErrorText = '';
            detErrorSection.style.display = 'none';
        }

        // Params section
        var runParams = (rt.run_params && typeof rt.run_params === 'object') ? rt.run_params : {};
        var taskConfig = (runParams.TASK_CONFIG && typeof runParams.TASK_CONFIG === 'object')
            ? runParams.TASK_CONFIG
            : {};
        var taskParams = {};
        Object.keys(runParams).forEach(function (key) {
            if (key === 'TASK_CONFIG') return;
            taskParams[key] = runParams[key];
        });
        if (Object.keys(taskParams).length || Object.keys(taskConfig).length) {
            detParamsSection.style.display = '';
            currentParamsData = {};
            if (Object.keys(taskParams).length) { currentParamsData['Task Params'] = taskParams; }
            if (Object.keys(taskConfig).length)  { currentParamsData['Input Params'] = taskConfig; }
            if (currentParamsOwnerTaskId !== selectedTaskId) {
                // Start with top-level folders collapsed for less visual noise.
                currentParamsExpanded = new Set();
                currentParamsOwnerTaskId = selectedTaskId;
            }
            renderParamsExplorer();
        } else {
            detParamsSection.style.display = 'none';
            currentParamsData = null;
            currentParamsExpanded = new Set();
            currentParamsOwnerTaskId = null;
        }

        // Files section
        var files = rt.output_files || [];
        if (files.length) {
            detFilesSection.style.display = '';
            if (detBtnPurgeFiles) {
                detBtnPurgeFiles.disabled = false;
            }
            detOutputFiles.innerHTML = renderOutputFileList(files);
            detOutputFiles.querySelectorAll('.at-file-preview-btn').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    previewFile(btn.dataset.path);
                });
            });
            detOutputFiles.querySelectorAll('.at-file-download-btn').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    downloadFile(btn.dataset.path);
                });
            });
        } else {
            detFilesSection.style.display = 'none';
            if (detBtnPurgeFiles) {
                detBtnPurgeFiles.disabled = true;
            }
        }
    }

    function bindSectionToggles() {
        bindSectionToggle(detBtnToggleInfo, detInfoBody);
        bindSectionToggle(detBtnToggleError, detErrorBody);
        bindSectionToggle(detBtnToggleParams, detParamsBody);
    }

    function bindSectionToggle(button, body) {
        if (!button || !body) return;
        button.addEventListener('click', function () {
            var isHidden = body.style.display === 'none';
            body.style.display = isHidden ? '' : 'none';
            var icon = button.querySelector('i');
            if (icon) {
                icon.className = 'fa-solid ' + (isHidden ? 'fa-chevron-up' : 'fa-chevron-down');
            }
        });
    }

    function formatJson(value) {
        try {
            return JSON.stringify(value || {}, null, 2);
        } catch (_err) {
            return String(value || '{}');
        }
    }

    /* -----------------------------------------------------------------------
       Params tree-explorer
    ----------------------------------------------------------------------- */

    function pxIsPrimitive(val) {
        return val === null || typeof val !== 'object';
    }

    function pxLabel(val) {
        if (val === null) { return 'null'; }
        if (typeof val === 'boolean') { return val ? 'true' : 'false'; }
        return String(val);
    }

    // Short (≤5 items) array or dict whose values are all primitive → show inline
    function pxIsShortSimple(val) {
        if (pxIsPrimitive(val)) return true;
        var items = Array.isArray(val) ? val : Object.values(val);
        return items.length <= 5 && items.every(pxIsPrimitive);
    }

    function pxInlineFormat(val) {
        if (Array.isArray(val)) {
            return '[ ' + val.map(pxLabel).join(', ') + ' ]';
        }
        return '{ ' + Object.keys(val).map(function (k) {
            return k + ': ' + pxLabel(val[k]);
        }).join(', ') + ' }';
    }

    function pxNodeId(path) {
        return path.join('::');
    }

    function pxRows(node, path, depth) {
        if (node === undefined || node === null) {
            return '<div class="at-px-empty">No data</div>';
        }
        if (pxIsPrimitive(node)) {
            return '<div class="at-px-row at-px-row--leaf" style="padding-left:'
                + (0.55 + depth * 1.1) + 'rem;">'
                + '<span class="at-px-row__icon"><i class="fa-solid fa-tag"></i></span>'
                + '<span class="at-px-row__key">value</span>'
                + '<span class="at-px-row__val">' + esc(pxLabel(node)) + '</span>'
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
            if (pxIsShortSimple(v)) {
                var display = pxIsPrimitive(v) ? pxLabel(v) : pxInlineFormat(v);
                html += '<div class="at-px-row at-px-row--leaf" style="padding-left:'
                    + (0.55 + depth * 1.1) + 'rem;">'
                    + '<span class="at-px-row__icon"><i class="fa-solid fa-tag"></i></span>'
                    + '<span class="at-px-row__key">' + esc(k) + '</span>'
                    + '<span class="at-px-row__val">' + esc(display) + '</span>'
                    + '</div>';
            } else {
                var childPath = path.concat([k]);
                var id = pxNodeId(childPath);
                var expanded = currentParamsExpanded.has(id);
                var hint = Array.isArray(v)
                    ? ('[ ' + v.length + ' ]')
                    : ('{ ' + Object.keys(v).length + ' }');
                html += '<div class="at-px-row at-px-row--folder at-px-tree-toggle" data-node="'
                    + esc(id) + '" style="padding-left:' + (0.55 + depth * 1.1) + 'rem;">'
                    + '<span class="at-px-row__icon"><i class="fa-solid fa-'
                    + (expanded ? 'folder-open' : 'folder') + '"></i></span>'
                    + '<span class="at-px-row__key">' + esc(k) + '</span>'
                    + '<span class="at-px-row__val at-px-row__val--hint">' + hint + '</span>'
                    + '<span class="at-px-row__chevron"><i class="fa-solid fa-chevron-'
                    + (expanded ? 'down' : 'right') + '"></i></span>'
                    + '</div>';
                if (expanded) {
                    html += pxRows(v, childPath, depth + 1);
                }
            }
        });
        return html;
    }

    function renderParamsExplorer() {
        if (detParamsBreadcrumb) {
            detParamsBreadcrumb.innerHTML = '<span class="at-px-crumb at-px-crumb--active">Parameters Tree</span>';
        }
        detParamsExplorer.innerHTML = pxRows(currentParamsData, [], 0);
        detParamsExplorer.querySelectorAll('.at-px-tree-toggle').forEach(function (el) {
            el.addEventListener('click', function () {
                var id = el.getAttribute('data-node') || '';
                if (currentParamsExpanded.has(id)) {
                    currentParamsExpanded.delete(id);
                } else {
                    currentParamsExpanded.add(id);
                }
                renderParamsExplorer();
            });
        });
    }

    function previewFile(path) {
        var fname = path.split('/').pop();
        fileModalTitle.textContent = fname + ' preview';
        fileModalContent.innerHTML = '<div class="ari-sg-loading" style="padding:1.5rem;">Loading…</div>';
        fileModal.style.display = '';

        fetch(urls.readFile + '?path=' + encodeURIComponent(path) + '&lines=50')
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (!d.success) {
                    fileModalContent.innerHTML = '<div class="ari-sg-error" style="padding:1rem;">' +
                        esc(d.error || 'Error loading file') + '</div>';
                    return;
                }
                var html = '<div class="at-file-preview-meta">';
                if (d.is_binary) {
                    html += '<span>Binary file</span>';
                } else {
                    html += '<span>Showing first ' + esc(String(d.preview_lines || 50)) + ' lines</span>';
                    if (d.truncated) {
                        html += '<span>Preview truncated from ' + esc(String(d.line_count || 0)) + ' lines</span>';
                    }
                    if (d.is_json && d.json_table) {
                        html += '<span>JSON table rows: ' + esc(String(d.json_table.row_count || 0)) + '</span>';
                        if (d.json_table.truncated) {
                            html += '<span>Table limited to first ' + esc(String((d.json_table.rows || []).length)) + ' rows</span>';
                        }
                    }
                }
                html += '</div>';

                if (d.is_json && d.json_table) {
                    html += renderJsonPreviewTable(d.json_table);
                } else {
                    html += '<pre class="at-file-preview">' + esc(d.preview || '') + '</pre>';
                }
                fileModalContent.innerHTML = html;
            })
            .catch(function () {
                fileModalContent.innerHTML = '<div class="ari-sg-error" style="padding:1rem;">Request failed</div>';
            });
    }

    function renderJsonPreviewTable(table) {
        var columns = Array.isArray(table.columns) ? table.columns.slice() : [];
        var rows = Array.isArray(table.rows) ? table.rows : [];

        if (!columns.length && rows.length) {
            var seen = {};
            rows.forEach(function (row) {
                if (!row || typeof row !== 'object' || Array.isArray(row)) return;
                Object.keys(row).forEach(function (key) {
                    if (!seen[key]) {
                        seen[key] = true;
                        columns.push(key);
                    }
                });
            });
        }

        if (!columns.length || !rows.length) {
            return '<pre class="at-file-preview">(JSON has no tabular rows to display)</pre>';
        }

        var html = '<div class="at-file-preview-wrap"><table class="at-file-table"><thead><tr>';
        columns.forEach(function (col) {
            html += '<th>' + esc(String(col)) + '</th>';
        });
        html += '</tr></thead><tbody>';

        rows.forEach(function (row) {
            html += '<tr>';
            columns.forEach(function (col) {
                var value = row && row[col] !== undefined ? row[col] : '';
                html += '<td>' + esc(String(value)) + '</td>';
            });
            html += '</tr>';
        });

        html += '</tbody></table></div>';
        return html;
    }

    function outputFileType(path) {
        var name = String(path || '').split('/').pop() || '';
        var lower = name.toLowerCase();
        if (lower.endsWith('.fits.gz')) return '.fits.gz';
        if (lower.endsWith('.tar.gz')) return '.tar.gz';
        var idx = lower.lastIndexOf('.');
        if (idx <= 0 || idx === lower.length - 1) return '(no extension)';
        return lower.slice(idx);
    }

    function outputFileGroups(paths) {
        var order = [];
        var groups = {};
        (paths || []).forEach(function (path) {
            var key = outputFileType(path);
            if (!groups[key]) {
                groups[key] = [];
                order.push(key);
            }
            groups[key].push(path);
        });
        return { order: order, groups: groups };
    }

    function renderOutputFileList(paths) {
        var grouped = outputFileGroups(paths);
        var html = '';

        grouped.order.forEach(function (key) {
            var files = grouped.groups[key] || [];
            var visible = files.slice(0, OUTPUT_PREVIEW_PER_TYPE);
            var hiddenCount = Math.max(files.length - visible.length, 0);

            html += '<li class="at-file-list__item" style="padding-top:0.45rem;">'
                + '<strong>' + esc(key) + '</strong>'
                + '<span class="at-muted-hint" style="font-style:normal;">'
                + ' (' + files.length + ' file' + (files.length === 1 ? '' : 's') + ')</span>'
                + '</li>';

            visible.forEach(function (f) {
                html += '<li class="at-file-list__item">'
                    + '<code class="at-file-list__path">' + esc(f) + '</code>'
                    + '<button class="ari-btn ari-btn--sm ari-btn--secondary at-file-preview-btn"'
                    + ' data-path="' + esc(f) + '">'
                    + '<i class="fa-solid fa-file-lines"></i> Preview</button>'
                    + '<button class="ari-btn ari-btn--sm ari-btn--secondary at-file-download-btn"'
                    + ' data-path="' + esc(f) + '">'
                    + '<i class="fa-solid fa-download"></i> Download</button>'
                    + '</li>';
            });

            if (hiddenCount > 0) {
                html += '<li class="at-file-list__item">'
                    + '<span class="at-muted-hint" style="font-style:normal;">'
                    + '... ' + hiddenCount + ' more ' + esc(key) + ' file'
                    + (hiddenCount === 1 ? '' : 's') + '</span>'
                    + '</li>';
            }
        });
        return html;
    }

    function downloadFile(path) {
        window.location.href = urls.downloadFile + '?path=' + encodeURIComponent(path);
    }

    function bindFileModal() {
        [btnFileModalClose, btnFileModalOk].forEach(function (btn) {
            btn.addEventListener('click', function () { fileModal.style.display = 'none'; });
        });
        fileModal.addEventListener('click', function (e) {
            if (e.target === fileModal) fileModal.style.display = 'none';
        });
    }

    function fetchTaskLog(taskId, lines) {
        return fetch(urls.taskLog + '?task_id=' + encodeURIComponent(taskId) + '&lines=' + encodeURIComponent(lines || 400))
            .then(function (r) { return r.json(); });
    }

    var taskLogFindState = { matches: [], idx: 0 };

    function escForLog(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function _logContentHasSelection() {
        try {
            var sel = window.getSelection();
            if (!sel || sel.isCollapsed) return false;
            var node = sel.anchorNode;
            return !!(node && taskLogModalContent && taskLogModalContent.contains(node));
        } catch (_e) { return false; }
    }

    function renderTaskLogContent(text) {
        currentTaskLogText = text;
        // Don't clobber an active text selection inside the log panel.
        if (_logContentHasSelection()) return;
        var html = '';
        text.split('\n').forEach(function (line, idx) {
            if (!line) return;
            var escaped = escForLog(line);
            var open = '<span class="acq-log-line" id="atlog-' + idx +
                '" data-line="' + idx + '">';
            if (line.indexOf('-!!|') >= 0) {
                html += open + '<span class="acq-log-error">' + escaped + '</span></span>';
            } else if (line.indexOf('-@!|') >= 0) {
                html += open + '<span class="acq-log-warn">' + escaped + '</span></span>';
            } else {
                html += open + escaped + '</span>';
            }
        });
        taskLogModalContent.innerHTML = html || '(No log lines yet)';
        taskLogModalContent.scrollTop = taskLogModalContent.scrollHeight;
        updateTaskLogFind();
    }

    function taskLogScrollToMatch(el) {
        if (!el || !taskLogModalContent) return;
        var cr = taskLogModalContent.getBoundingClientRect();
        var er = el.getBoundingClientRect();
        taskLogModalContent.scrollTop +=
            (er.top - cr.top) - taskLogModalContent.clientHeight / 2 + el.clientHeight / 2;
    }

    function updateTaskLogFind() {
        var input = document.getElementById('task-log-find');
        var count = document.getElementById('task-log-find-count');
        if (!taskLogModalContent) return;
        var query = input ? input.value.trim() : '';

        var lines = taskLogModalContent.querySelectorAll('.acq-log-line');
        lines.forEach(function (el) {
            el.classList.remove('acq-log-match-line', 'acq-log-match-current');
        });

        if (!query) {
            taskLogFindState.matches = [];
            taskLogFindState.idx = 0;
            if (count) count.textContent = '';
            return;
        }

        var lq = query.toLowerCase();
        var matches = [];
        lines.forEach(function (el) {
            if ((el.textContent || '').toLowerCase().indexOf(lq) >= 0) {
                el.classList.add('acq-log-match-line');
                matches.push(el);
            }
        });

        taskLogFindState.matches = matches;
        taskLogFindState.idx = 0;

        if (matches.length > 0) {
            matches[0].classList.add('acq-log-match-current');
            taskLogScrollToMatch(matches[0]);
        }

        if (count) {
            count.textContent = matches.length === 0 ? 'No matches' : '1 / ' + matches.length;
        }
    }

    function taskLogFindNav(dir) {
        var matches = taskLogFindState.matches;
        var count = document.getElementById('task-log-find-count');
        if (!matches || !matches.length) return;
        matches[taskLogFindState.idx].classList.remove('acq-log-match-current');
        taskLogFindState.idx = (taskLogFindState.idx + dir + matches.length) % matches.length;
        matches[taskLogFindState.idx].classList.add('acq-log-match-current');
        taskLogScrollToMatch(matches[taskLogFindState.idx]);
        if (count) {
            count.textContent = (taskLogFindState.idx + 1) + ' / ' + matches.length;
        }
    }

    function refreshOpenTaskLog() {
        if (!openTaskLogTaskId) return;
        fetchTaskLog(openTaskLogTaskId, 600)
            .then(function (d) {
                if (!d || !d.success) {
                    // Keep last visible content on transient fetch/auth errors.
                    if (!currentTaskLogText) {
                        renderTaskLogContent('(No log lines yet)');
                    }
                    return;
                }
                renderTaskLogContent(String(d.content || ''));
            })
            .catch(function () {
                // Keep existing log text instead of clobbering it.
                if (!currentTaskLogText) {
                    renderTaskLogContent('(No log lines yet)');
                }
            });
    }

    function openLiveTaskLog(taskId, taskName, isLive) {
        openTaskLogTaskId = String(taskId || '');
        if (!openTaskLogTaskId) return;
        taskLogModalTitle.textContent = 'Task Log - ' + String(taskName || openTaskLogTaskId);
        renderTaskLogContent('Loading...');
        taskLogModal.style.display = '';
        if (taskLogRefreshTimer) {
            clearInterval(taskLogRefreshTimer);
            taskLogRefreshTimer = null;
        }
        refreshOpenTaskLog();
        if (isLive !== false) {
            taskLogRefreshTimer = setInterval(refreshOpenTaskLog, 1500);
        }
    }

    /* Open the log viewer for a finished (history) task without polling. */
    function openTaskLogOverlay(taskId, taskName) {
        openLiveTaskLog(taskId, taskName, false);
    }

    function closeLiveTaskLog() {
        if (taskLogRefreshTimer) {
            clearInterval(taskLogRefreshTimer);
            taskLogRefreshTimer = null;
        }
        openTaskLogTaskId = null;
        taskLogModal.style.display = 'none';
    }

    function bindTaskLogModal() {
        if (!taskLogModal) return;
        [btnTaskLogClose, btnTaskLogCloseX].forEach(function (btn) {
            if (!btn) return;
            btn.addEventListener('click', closeLiveTaskLog);
        });
        if (btnTaskLogRefresh) {
            btnTaskLogRefresh.addEventListener('click', refreshOpenTaskLog);
        }
        if (btnTaskLogCopy) {
            btnTaskLogCopy.addEventListener('click', function () {
                if (!currentTaskLogText) {
                    showToast('No log to copy.', 'error');
                    return;
                }
                copyToClipboard(currentTaskLogText, 'Task log copied to clipboard.');
            });
        }
        var backdrop = document.getElementById('at-task-log-backdrop');
        if (backdrop) backdrop.addEventListener('click', closeLiveTaskLog);

        var findInput = document.getElementById('task-log-find');
        var findPrev = document.getElementById('task-log-find-prev');
        var findNext = document.getElementById('task-log-find-next');
        if (findInput) {
            findInput.addEventListener('input', updateTaskLogFind);
            findInput.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    taskLogFindNav(e.shiftKey ? -1 : 1);
                } else if (e.key === 'Escape') {
                    closeLiveTaskLog();
                }
            });
        }
        if (findPrev) findPrev.addEventListener('click', function () { taskLogFindNav(-1); });
        if (findNext) findNext.addEventListener('click', function () { taskLogFindNav(1); });

        document.addEventListener('keydown', function (e) {
            if (taskLogModal.style.display === 'none') return;
            if (e.key === 'Escape') closeLiveTaskLog();
        });
    }
    if (detBtnToggle) {
        detBtnToggle.addEventListener('click', function () {
            if (!selectedTaskId) return;
            fetch(urls.toggle, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ instrument: currentInstrument, id: selectedTaskId }),
            }).then(function (r) { return r.json(); }).then(function (d) {
                if (d.success) { refreshCurrentTasks(); } else { showToast('Toggle failed: ' + d.error, 'error'); }
            });
        });
    }

    if (detBtnEdit) {
        detBtnEdit.addEventListener('click', function () {
            if (!selectedTaskId) return;
            var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
            if (!task) return;
            openEditModal(task);
        });
    }

    if (detBtnDelete) {
        detBtnDelete.addEventListener('click', function () {
            if (!selectedTaskId) return;
            var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
            if (!task) return;
            pendingDeleteId = task.id;
            if (deleteModalName) {
                deleteModalName.textContent = task.name || task.task_key;
            }
            if (deleteModal) {
                deleteModal.style.display = '';
            }
        });
    }

    function queueSelectedTask(forceRun) {
        if (!selectedTaskId) return;
        var localDir = (window.location.search.match(/local_data_dir=([^&]+)/) || [])[1]
                    || window.ARI_LOCAL_DATA_DIR || '';
        fetch(urls.runNow, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: currentInstrument,
                id: selectedTaskId,
                local_data_dir: localDir,
                force_run: !!forceRun,
            }),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (d.success) {
                showToast(forceRun
                    ? 'Task force-queued for immediate execution.'
                    : 'Task queued for immediate execution.', 'success');
                refreshCurrentTasks();
            } else {
                showToast('Run failed: ' + d.error, 'error');
            }
        });
    }

    if (detBtnRunNow) {
        detBtnRunNow.addEventListener('click', function () {
            queueSelectedTask(false);
        });
    }

    if (detBtnForceRun) {
        detBtnForceRun.addEventListener('click', function () {
            queueSelectedTask(true);
        });
    }

    function cancelTask(taskId, taskName) {
        if (!taskId) return;
        var label = taskName || taskId;
        if (!confirm('Stop task "' + label + '"?\n\nRunning tasks will be signalled to stop; they may take a moment to finish.')) return;
        fetch(urls.cancelTask, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId }),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (d.success) {
                var msg = d.was_running
                    ? 'Stop signal sent. Task will finish current operation then cancel.'
                    : 'Task removed from queue.';
                showToast(msg, 'success');
                refreshCurrentTasks();
            } else {
                showToast('Cancel failed: ' + (d.error || 'unknown error'), 'error');
            }
        }).catch(function () {
            showToast('Cancel request failed.', 'error');
        });
    }

    if (detBtnStop) {
        detBtnStop.addEventListener('click', function () {
            if (!selectedTaskId) return;
            var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
            var name = task ? (task.name || task.task_key || selectedTaskId) : selectedTaskId;
            cancelTask(selectedTaskId, name);
        });
    }

    if (detBtnViewLog) {
        detBtnViewLog.addEventListener('click', function () {
            if (!selectedTaskId) return;
            var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
            var name = task ? (task.name || task.task_key || selectedTaskId) : selectedTaskId;
            openLiveTaskLog(selectedTaskId, name);
        });
    }

    if (detBtnCopyInfo) {
        detBtnCopyInfo.addEventListener('click', function () {
            if (!currentInfoText) {
                showToast('No info to copy.', 'error');
                return;
            }
            copyToClipboard(currentInfoText, 'Info copied to clipboard.');
        });
    }

    if (detBtnCopyError) {
        detBtnCopyError.addEventListener('click', function () {
            if (!currentErrorText) {
                showToast('No error to copy.', 'error');
                return;
            }
            copyToClipboard(currentErrorText, 'Error copied to clipboard.');
        });
    }

    if (detBtnPurgeFiles) {
        detBtnPurgeFiles.addEventListener('click', function () {
            if (!selectedTaskId) return;
            var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
            if (!task) return;
            var rt = task.runtime || {};
            var files = Array.isArray(rt.output_files) ? rt.output_files : [];
            if (!files.length) {
                showToast('No output files to purge.', 'error');
                return;
            }

            var label = task.name || task.task_key || selectedTaskId;
            if (!confirm('Purge ' + files.length + ' output file(s) for "' + label + '"?\n\nThis will delete files from disk and clear them from task output files.')) {
                return;
            }

            fetch(urls.purgeFiles, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    instrument: currentInstrument,
                    id: selectedTaskId,
                }),
            }).then(function (r) { return r.json(); }).then(function (d) {
                if (!d.success) {
                    showToast('Purge failed: ' + (d.error || 'unknown error'), 'error');
                    return;
                }

                var deleted = Array.isArray(d.deleted) ? d.deleted.length : 0;
                var missing = Array.isArray(d.missing) ? d.missing.length : 0;
                var failed = Array.isArray(d.failed) ? d.failed.length : 0;
                showToast(
                    'Purge complete: deleted ' + deleted + ', missing ' + missing + ', failed ' + failed + '.',
                    failed > 0 ? 'error' : 'success'
                );
                refreshCurrentTasks();
            }).catch(function () {
                showToast('Purge request failed.', 'error');
            });
        });
    }

    /* -----------------------------------------------------------------------
       Run All
    ----------------------------------------------------------------------- */
    function bindRunAll() {
        function queueRunAll(forceRun) {
            runAllForceMode = !!forceRun;
            // Check if queue is non-empty
            fetch(urls.status)
                .then(function (r) { return r.json(); })
                .then(function (d) {
                    if (!d.success) return;
                    var q = d.queue || {};
                    var busy = q.queue_length > 0 || q.current;
                    if (busy) {
                        runAllModal.style.display = '';
                    } else {
                        doRunAll('add', runAllForceMode);
                    }
                });
        }

        if (btnRunAll) {
            btnRunAll.addEventListener('click', function () {
                queueRunAll(false);
            });
        }
        if (btnForceRunAll) {
            btnForceRunAll.addEventListener('click', function () {
                queueRunAll(true);
            });
        }
        if (!btnRunAll && !btnForceRunAll) return;
    }

    function doRunAll(action, forceRun) {
        var localDir = window.ARI_LOCAL_DATA_DIR || '';
        fetch(urls.runAll, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: currentInstrument,
                action: action,
                force_run: !!forceRun,
                local_data_dir: localDir,
            }),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (d.success) {
                var msgPrefix = forceRun ? 'Force-queued ' : 'Added ';
                showToast(msgPrefix + (d.added || []).length + ' task(s) to queue.', 'success');
                refreshCurrentTasks();
            } else {
                showToast('Run All failed: ' + d.error, 'error');
            }
        });
    }

    function bindRunAllModal() {
        if (!btnRunAllReplace || !btnRunAllAdd || !btnRunAllCancel || !runAllModal) {
            return;
        }
        btnRunAllReplace.addEventListener('click', function () {
            runAllModal.style.display = 'none';
            doRunAll('replace', runAllForceMode);
        });
        btnRunAllAdd.addEventListener('click', function () {
            runAllModal.style.display = 'none';
            doRunAll('add', runAllForceMode);
        });
        btnRunAllCancel.addEventListener('click', function () {
            runAllModal.style.display = 'none';
        });
    }

    /* -----------------------------------------------------------------------
       Edit / Add modal
    ----------------------------------------------------------------------- */
    function loadTaskClasses() {
        fetch(urls.taskList)
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (!d.success) return;
                taskClasses = d.tasks || [];
                mpConfig = d.multiprocessing || mpConfig;
                populateTaskKeySelect();
            });
    }

    function populateTaskKeySelect() {
        // Keep the default placeholder
        while (editTaskKey.options.length > 1) editTaskKey.remove(1);
        taskClasses.forEach(function (cls) {
            var opt = document.createElement('option');
            opt.value = cls.key;
            opt.textContent = cls.key + ' — ' + cls.name;
            editTaskKey.appendChild(opt);
        });
    }

    function openEditModal(task) {
        if (!task) return;

        editingTaskId = task.id;
        editModalTitle.innerHTML = '<i class="fa-solid fa-pen"></i> Edit Task';

        editTaskKey.value = task.task_key || '';
        editTaskKey.disabled = true;
        editFrequency.value = task.frequency || 24;
        if (editDryRun) {
            editDryRun.checked = !!(
                task.DRY_RUN === true || task.dry_run === true
            );
        }
        if (editGoogleSecretName) {
            editGoogleSecretName.value = String(
                task.google_secret_name || 'legacy_gsheet_oauth.json'
            );
        }
        if (editGoogleOauthFile) {
            editGoogleOauthFile.value = '';
        }
        if (editMonitoringSheetUrl) {
            editMonitoringSheetUrl.value = getLegacyCheckUrl(
                task,
                'monitoring_sheet_urls',
                'monitoring_sheet_url'
            );
        }
        if (editOverrideSheetUrl) {
            editOverrideSheetUrl.value = getLegacyCheckUrl(
                task,
                'override_sheet_urls',
                'override_sheet_url'
            );
        }
        if (editKnownErrorsSheetUrl) {
            var keSheetId = String(task.sheet_id || '');
            editKnownErrorsSheetUrl.value = keSheetId
                ? 'https://docs.google.com/spreadsheets/d/' + keSheetId + '/edit'
                : '';
        }
        editDailyCopies.value = task.daily_copies || 0;
        editWeeklyCopies.value = task.weekly_copies || 0;
        if (editBackupMaxSizeMb) {
            var maxMb = parseFloat(task.backup_max_size_mb);
            if (!isFinite(maxMb) || maxMb <= 0) {
                maxMb = 1024;
            }
            // Render integers without trailing zeros for whole MB.
            editBackupMaxSizeMb.value = (maxMb % 1 === 0)
                ? String(parseInt(maxMb, 10))
                : String(maxMb);
            // Make the on-disk value visible so the admin can tell
            // that the field reflects the persisted value (not a
            // stale HTML default).
            if (editBackupMaxSizeSaved) {
                editBackupMaxSizeSaved.textContent =
                    ' Currently saved: '
                    + ((maxMb % 1 === 0)
                        ? String(parseInt(maxMb, 10))
                        : String(maxMb))
                    + ' MB.';
            }
        }
        // Populate exclude lists + show the built-in defaults so
        // the admin knows what kicks in when the override is empty.
        if (editBackupExcludeDirs) {
            var excDirs = Array.isArray(task.exclude_dirs)
                ? task.exclude_dirs
                : [];
            editBackupExcludeDirs.value = excDirs.join('\n');
        }
        if (editBackupExcludePaths) {
            var excPaths = Array.isArray(task.exclude_paths)
                ? task.exclude_paths
                : [];
            editBackupExcludePaths.value = excPaths.join('\n');
        }
        if (editBackupExcludeDirsDefault) {
            var defDirs = Array.isArray(task.default_exclude_dirs)
                ? task.default_exclude_dirs
                : [];
            editBackupExcludeDirsDefault.textContent =
                defDirs.length ? defDirs.join(', ') : '(none)';
        }
        if (editBackupExcludePathsDefault) {
            var defPaths = Array.isArray(task.default_exclude_paths)
                ? task.default_exclude_paths
                : [];
            editBackupExcludePathsDefault.textContent =
                defPaths.length ? defPaths.join(', ') : '(none)';
        }
        if (editAssetsMode) {
            var _modeRaw = String(task.mode || 'remote').toLowerCase();
            if (_modeRaw === 'sync' || _modeRaw === 'upload' ||
                    _modeRaw === 'remote') {
                _modeRaw = 'remote';
            } else if (_modeRaw !== 'local') {
                _modeRaw = 'remote';
            }
            editAssetsMode.value = _modeRaw;
        }
        if (editAssetsLocalSrc) {
            editAssetsLocalSrc.value = String(
                task.local_source_path || ''
            );
        }
        if (editAssetsDrsUconfig) {
            editAssetsDrsUconfig.value = String(task.drs_uconfig || '');
        }
        updateAssetsLocalSrcVisibility();
        editNcores.value = task.ncores || 1;
        editMpBackend.value = task.mp_backend || 'threads';
        editMpStartMethod.value = task.mp_start_method || 'default';
        renderSyncProfiles(task);
        editRunCount.textContent = task.runtime ? (task.runtime.run_count || 0) : 0;
        editActive.checked = task.active !== false;
        selectEditTab('run');
        onTaskKeyChange();
        editModal.style.display = '';
    }

    function selectEditTab(tabName) {
        var showRun = (tabName !== 'filters');
        if (editPaneRun) {
            editPaneRun.classList.toggle('at-edit-tab-pane--active', showRun);
        }
        if (editPaneFilters) {
            editPaneFilters.classList.toggle('at-edit-tab-pane--active', !showRun);
        }
        if (editTabRunBtn) {
            editTabRunBtn.classList.toggle('at-edit-tab--active', showRun);
        }
        if (editTabFiltersBtn) {
            editTabFiltersBtn.classList.toggle('at-edit-tab--active', !showRun);
        }
    }

    function taskFilterKeys(taskKey) {
        var cls = taskClasses.find(function (c) { return c.key === taskKey; }) || {};
        var values = Array.isArray(cls.filters) ? cls.filters : [];
        return values
            .map(function (x) { return String(x || '').trim(); })
            .filter(function (x) { return !!x; });
    }

    function renderTaskFilters(taskKey, taskConfig) {
        if (!editFiltersContainer || !editFiltersEmpty) return;
        editFiltersContainer.innerHTML = '';
        editFilterInputs = {};

        var keys = taskFilterKeys(taskKey);
        var currentFilters = (taskConfig && typeof taskConfig.filters === 'object')
            ? taskConfig.filters
            : {};

        if (!keys.length) {
            editFiltersEmpty.style.display = '';
            return;
        }

        editFiltersEmpty.style.display = 'none';
        keys.forEach(function (key) {
            var field = document.createElement('div');
            field.className = 'ari-ap-form__field';

            var label = document.createElement('label');
            label.setAttribute('for', 'edit-filter-' + key);
            label.textContent = key;

            var input = document.createElement('input');
            input.type = 'text';
            input.id = 'edit-filter-' + key;
            input.className = 'ari-ap-input';
            input.value = String(currentFilters[key] || '');
            if (key.toUpperCase() === 'OBJNAME_INCLUDE') {
                input.placeholder = 'Comma-separated object names to include only';
            }
            if (key.toUpperCase() === 'OBJNAME_EXCLUDE') {
                input.placeholder = 'Comma-separated object names to exclude';
            }
            if (key.toUpperCase() === 'APERO_PROFILE_INCLUDE') {
                input.placeholder =
                    'Comma-separated APERO profile names to include only';
            }
            if (key.toUpperCase() === 'APERO_PROFILE_EXCLUDE') {
                input.placeholder =
                    'Comma-separated APERO profile names to exclude';
            }

            field.appendChild(label);
            field.appendChild(input);
            editFiltersContainer.appendChild(field);
            editFilterInputs[key] = input;
        });
    }

    function getTaskSyncProfiles(task) {
        var out = {};
        if (task && task.sync_profiles
                && typeof task.sync_profiles === 'object') {
            Object.keys(task.sync_profiles).forEach(function (profileName) {
                var entry = task.sync_profiles[profileName];
                if (!entry || typeof entry !== 'object') return;
                var mode = String(entry.mode || 'run_server').trim();
                var syncSource = String(
                    entry.sync_source || ''
                ).trim();
                if (mode === 'fetch_precomputed' && syncSource) {
                    out[profileName] = {
                        mode: 'fetch_precomputed',
                        sync_source: syncSource,
                    };
                }
            });
        }
        if (Object.keys(out).length === 0) {
            var legacySync = String(task && task.sync_source || '').trim();
            if (legacySync) {
                currentProfileNames.forEach(function (profileName) {
                    out[profileName] = {
                        mode: 'fetch_precomputed',
                        sync_source: legacySync,
                    };
                });
            }
        }
        return out;
    }

    function updateSyncProfileRow(row) {
        if (!row) return;
        var modeEl = row.querySelector('select[data-role="mode"]');
        var pathEl = row.querySelector('input[data-role="path"]');
        var browseBtn = row.querySelector('button[data-role="browse"]');
        var aliasEl = row.querySelector('[data-role="alias"]');
        var mode = modeEl ? String(modeEl.value || '').trim() : 'run_server';
        var enabled = (mode === 'fetch_precomputed');
        if (pathEl) pathEl.disabled = !enabled;
        if (browseBtn) browseBtn.disabled = !enabled;
        if (aliasEl) {
            var profileName = row.dataset.profile || '';
            var syncPath = pathEl ? String(pathEl.value || '').trim() : '';
            var baseName = syncPath.replace(/\/+$/, '').split('/').pop() || '';
            aliasEl.textContent = (enabled && syncPath && baseName
                    && baseName !== profileName)
                ? ('Selected task directory: ' + baseName)
                : '';
        }
    }

    function renderSyncProfiles(task) {
        if (!editSyncProfilesBody || !editSyncProfilesWrap
                || !editSyncProfilesEmpty) {
            return;
        }
        var syncProfiles = getTaskSyncProfiles(task || {});
        editSyncProfilesBody.innerHTML = '';
        if (!currentProfileNames.length) {
            editSyncProfilesWrap.style.display = 'none';
            editSyncProfilesEmpty.style.display = '';
            return;
        }

        editSyncProfilesWrap.style.display = '';
        editSyncProfilesEmpty.style.display = 'none';
        currentProfileNames.forEach(function (profileName) {
            var entry = syncProfiles[profileName] || {};
            var mode = entry.sync_source
                ? 'fetch_precomputed'
                : 'run_server';
            var syncSource = String(entry.sync_source || '');
            var row = document.createElement('tr');
            row.dataset.profile = profileName;
            row.innerHTML = ''
                + '<td><strong>' + esc(profileName) + '</strong></td>'
                + '<td>'
                + '<select class="ari-ap-input" data-role="mode">'
                + '<option value="run_server">Run on server</option>'
                + '<option value="fetch_precomputed">'
                + 'Fetch pre-computed</option>'
                + '</select></td>'
                + '<td>'
                + '<div class="at-sync-profiles__path-wrap">'
                + '<input type="text" class="ari-ap-input"'
                + ' data-role="path"'
                + ' placeholder="/path/to/precomputed/profile"'
                + ' value="' + esc(syncSource) + '">'
                + '<button type="button"'
                + ' class="ari-btn ari-btn--secondary"'
                + ' data-role="browse">'
                + '<i class="fa-solid fa-folder-open"></i> Browse'
                + '</button></div>'
                + '<div class="at-sync-profiles__alias"'
                + ' data-role="alias"></div></td>';
            editSyncProfilesBody.appendChild(row);

            var modeEl = row.querySelector('select[data-role="mode"]');
            var pathEl = row.querySelector('input[data-role="path"]');
            var browseBtn = row.querySelector('button[data-role="browse"]');
            modeEl.value = mode;
            modeEl.addEventListener('change', function () {
                updateSyncProfileRow(row);
                onTaskKeyChange();
            });
            pathEl.addEventListener('input', function () {
                updateSyncProfileRow(row);
            });
            browseBtn.addEventListener('click', function () {
                openSyncBrowseModal(pathEl);
            });
            updateSyncProfileRow(row);
        });
    }

    function collectSyncProfiles(validate) {
        var out = {};
        var anyRunOnServer = !currentProfileNames.length;
        var anyFetch = false;
        var rows = editSyncProfilesBody
            ? editSyncProfilesBody.querySelectorAll('tr[data-profile]')
            : [];
        rows.forEach(function (row) {
            var profileName = row.dataset.profile || '';
            var modeEl = row.querySelector('select[data-role="mode"]');
            var pathEl = row.querySelector('input[data-role="path"]');
            var mode = modeEl ? String(modeEl.value || '').trim() : '';
            var syncSource = pathEl ? String(pathEl.value || '').trim() : '';
            if (mode === 'fetch_precomputed') {
                anyFetch = true;
                if (validate && !syncSource) {
                    throw new Error(
                        'Pre-computed directory is required for '
                        + profileName + '.'
                    );
                }
                if (syncSource) {
                    out[profileName] = {
                        mode: 'fetch_precomputed',
                        sync_source: syncSource,
                    };
                }
            } else {
                anyRunOnServer = true;
            }
        });
        return {
            profiles: out,
            anyRunOnServer: anyRunOnServer,
            anyFetch: anyFetch,
        };
    }

    function openSyncBrowseModal(targetInput) {
        if (!syncBrowseModal || !syncBrowsePathInput) return;
        syncBrowseTargetInput = targetInput || null;
        syncBrowsePath = targetInput
            ? String(targetInput.value || '').trim() || '/'
            : '/';
        syncBrowsePathInput.value = syncBrowsePath;
        syncBrowseModal.style.display = 'flex';
        browseSyncDirectory(syncBrowsePath);
    }

    function closeSyncBrowseModal() {
        if (!syncBrowseModal) return;
        syncBrowseModal.style.display = 'none';
        syncBrowseTargetInput = null;
    }

    function browseSyncDirectory(path) {
        if (!syncBrowseList || !syncBrowseStatus) return;
        syncBrowseList.innerHTML = ''
            + '<div class="ari-sg-loading">Loading...</div>';
        syncBrowseStatus.style.display = 'none';
        fetch(urls.browseProfiles + '?path=' + encodeURIComponent(path))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    syncBrowseList.innerHTML = '<div class="ari-sg-error">'
                        + esc(data.error || 'Browse failed')
                        + '</div>';
                    return;
                }
                syncBrowsePath = data.path;
                syncBrowsePathInput.value = data.path;
                syncBrowseStatus.className = 'ari-ap-browser__status '
                    + 'ari-ap-browser__status--valid';
                syncBrowseStatus.innerHTML = ''
                    + '<i class="fa-solid fa-circle-check"></i>'
                    + ' Directory exists';
                syncBrowseStatus.style.display = 'block';
                syncBrowseList.innerHTML = '';

                if (data.path !== '/') {
                    var parent = data.path.replace(/\/[^\/]+\/?$/, '') || '/';
                    var upItem = document.createElement('div');
                    upItem.className = 'ari-ap-browser__item '
                        + 'ari-ap-browser__item--parent';
                    upItem.innerHTML = ''
                        + '<i class="fa-solid fa-arrow-up"></i> ..';
                    upItem.addEventListener('click', function () {
                        browseSyncDirectory(parent);
                    });
                    syncBrowseList.appendChild(upItem);
                }

                if (!(data.dirs || []).length) {
                    syncBrowseList.innerHTML = ''
                        + '<div class="ari-sg-empty-small">'
                        + 'No subdirectories</div>';
                    return;
                }

                (data.dirs || []).forEach(function (dirname) {
                    var item = document.createElement('div');
                    item.className = 'ari-ap-browser__item';
                    item.innerHTML = '<i class="fa-solid fa-folder"></i> '
                        + esc(dirname);
                    item.addEventListener('click', function () {
                        var nextPath = data.path.replace(/\/$/, '')
                            + '/' + dirname;
                        browseSyncDirectory(nextPath);
                    });
                    syncBrowseList.appendChild(item);
                });
            })
            .catch(function () {
                syncBrowseList.innerHTML = '<div class="ari-sg-error">'
                    + 'Failed to browse</div>';
            });
    }

    function bindSyncBrowseModal() {
        if (!syncBrowseModal || !syncBrowsePathInput
                || !btnSyncBrowseSelect) {
            return;
        }
        function goToPath() {
            browseSyncDirectory(
                String(syncBrowsePathInput.value || '').trim() || '/'
            );
        }
        if (btnSyncBrowseGo) {
            btnSyncBrowseGo.addEventListener('click', goToPath);
        }
        syncBrowsePathInput.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                goToPath();
            }
        });
        btnSyncBrowseSelect.addEventListener('click', function () {
            if (syncBrowseTargetInput) {
                syncBrowseTargetInput.value = syncBrowsePath;
                updateSyncProfileRow(
                    syncBrowseTargetInput.closest('tr[data-profile]')
                );
            }
            closeSyncBrowseModal();
        });
        if (btnSyncBrowseClose) {
            btnSyncBrowseClose.addEventListener(
                'click', closeSyncBrowseModal
            );
        }
        if (btnSyncBrowseCloseX) {
            btnSyncBrowseCloseX.addEventListener(
                'click', closeSyncBrowseModal
            );
        }
        syncBrowseModal.addEventListener('click', function (event) {
            if (event.target === syncBrowseModal) {
                closeSyncBrowseModal();
            }
        });
    }

    function updateAssetsLocalSrcVisibility() {
        var mode = editAssetsMode ? editAssetsMode.value : 'remote';
        if (editAssetsLocalSrcRow) {
            editAssetsLocalSrcRow.style.display = (mode === 'local') ? '' : 'none';
        }
        if (editAssetsDrsUconfigRow) {
            editAssetsDrsUconfigRow.style.display = (mode === 'remote') ? '' : 'none';
        }
    }

    if (editAssetsMode) {
        editAssetsMode.addEventListener(
            'change', updateAssetsLocalSrcVisibility);
    }
    if (editAssetsLocalBrowse) {
        editAssetsLocalBrowse.addEventListener('click', function (ev) {
            ev.preventDefault();
            aatOpenAssetsBrowseModal(editAssetsLocalSrc);
        });
    }
    if (editAssetsDrsUconfigBrowse) {
        editAssetsDrsUconfigBrowse.addEventListener('click', function (ev) {
            ev.preventDefault();
            aatOpenAssetsBrowseModal(editAssetsDrsUconfig);
        });
    }

    // ---- inline directory browser (shared for local-source and drs-uconfig) ----
    var aatBrowseModal = null;
    var aatBrowseList = null;
    var aatBrowseCurrent = null;
    var aatBrowseTitle = null;
    var aatBrowseTargetInput = null; // which input to write the selected path into

    function aatEnsureBrowseModal() {
        if (aatBrowseModal) return;
        var overlay = document.createElement('div');
        overlay.id = 'aat-browse-overlay';
        overlay.style.cssText =
            'position:fixed; inset:0; background:rgba(0,0,0,0.45);' +
            ' z-index:10000; display:flex; align-items:center;' +
            ' justify-content:center;';
        overlay.style.display = 'none';
        var box = document.createElement('div');
        box.style.cssText =
            'background:var(--ari-card-bg, #fff); color:inherit;' +
            ' border-radius:6px; padding:12px; width:min(640px, 92vw);' +
            ' max-height:80vh; display:flex; flex-direction:column;' +
            ' box-shadow:0 6px 24px rgba(0,0,0,0.25);';
        box.innerHTML =
            '<div style="display:flex; justify-content:space-between;' +
            ' align-items:center; margin-bottom:8px;">' +
            '<strong>Browse for local source directory</strong>' +
            '<button type="button" class="ari-ap-btn"' +
            ' id="aat-browse-close">Close</button></div>' +
            '<div id="aat-browse-current" style="font-family:monospace;' +
            ' font-size:12px; padding:4px 6px; background:rgba(0,0,0,0.05);' +
            ' border-radius:3px; margin-bottom:6px; word-break:break-all;">' +
            '</div>' +
            '<div id="aat-browse-list" style="flex:1 1 auto;' +
            ' overflow:auto; border:1px solid rgba(0,0,0,0.15);' +
            ' border-radius:3px;"></div>' +
            '<div style="display:flex; gap:6px; justify-content:flex-end;' +
            ' margin-top:8px;">' +
            '<button type="button" class="ari-ap-btn"' +
            ' id="aat-browse-up">Up</button>' +
            '<button type="button" class="ari-ap-btn ari-ap-btn--primary"' +
            ' id="aat-browse-select">Select this directory</button>' +
            '</div>';
        overlay.appendChild(box);
        document.body.appendChild(overlay);
        aatBrowseModal = overlay;
        aatBrowseList = box.querySelector('#aat-browse-list');
        aatBrowseTitle = box.querySelector('#aat-browse-current');
        box.querySelector('#aat-browse-close').addEventListener(
            'click', function () { aatBrowseModal.style.display = 'none'; });
        box.querySelector('#aat-browse-up').addEventListener(
            'click', function () {
                aatBrowseTo(aatBrowseCurrent
                    ? (aatBrowseCurrent.replace(/\/+$/, '')
                        .split('/').slice(0, -1).join('/') || '/')
                    : '');
            });
        box.querySelector('#aat-browse-select').addEventListener(
            'click', function () {
                if (aatBrowseTargetInput && aatBrowseCurrent) {
                    aatBrowseTargetInput.value = aatBrowseCurrent;
                }
                aatBrowseModal.style.display = 'none';
            });
    }

    function aatOpenAssetsBrowseModal(targetInput) {
        aatBrowseTargetInput = targetInput || editAssetsLocalSrc;
        aatEnsureBrowseModal();
        aatBrowseModal.style.display = 'flex';
        var startPath = (aatBrowseTargetInput && aatBrowseTargetInput.value) || '';
        aatBrowseTo(startPath);
    }

    function aatBrowseTo(path) {
        var url = '/api/admin/backups/browse';
        if (path) {
            url += '?path=' + encodeURIComponent(path);
        }
        fetch(url, {credentials: 'same-origin'})
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    aatBrowseList.innerHTML =
                        '<div style="padding:8px; color:red;">' +
                        (data && data.error ? data.error : 'Failed to list')
                        + '</div>';
                    return;
                }
                aatBrowseCurrent = data.path || '/';
                if (aatBrowseTitle) {
                    aatBrowseTitle.textContent = aatBrowseCurrent;
                }
                var dirs = Array.isArray(data.dirs) ? data.dirs : [];
                if (!dirs.length) {
                    aatBrowseList.innerHTML =
                        '<div style="padding:8px; opacity:0.7;">' +
                        '(no subdirectories)</div>';
                    return;
                }
                var html = '';
                for (var i = 0; i < dirs.length; i++) {
                    var d = dirs[i];
                    var name = (d && d.name) ? d.name : String(d);
                    var full = (d && d.path) ? d.path :
                        (aatBrowseCurrent.replace(/\/+$/, '')
                            + '/' + name);
                    html += '<div class="aat-browse-item"' +
                        ' data-path="' + full.replace(/"/g, '&quot;')
                        + '" style="padding:4px 8px; cursor:pointer;">' +
                        '\u{1F4C1} ' + name + '</div>';
                }
                aatBrowseList.innerHTML = html;
                Array.prototype.forEach.call(
                    aatBrowseList.querySelectorAll('.aat-browse-item'),
                    function (el) {
                        el.addEventListener('click', function () {
                            aatBrowseTo(el.getAttribute('data-path'));
                        });
                    });
            })
            .catch(function (err) {
                aatBrowseList.innerHTML =
                    '<div style="padding:8px; color:red;">' +
                    String(err) + '</div>';
            });
    }

    function onTaskKeyChange() {
        var key = editTaskKey.value;
        var cls = taskClasses.find(function (c) { return c.key === key; });
        var isBackup = key === BACKUP_TASK_KEY;
        var isLegacyGsheet = (
            key === LEGACY_ASTROM_TASK_KEY
            || key === LEGACY_REJECT_TASK_KEY
            || key === LEGACY_CHECK_TASK_KEY
            || key === LEGACY_KNOWN_ERRORS_TASK_KEY
        );
        var isCheckGsheet = (key === LEGACY_CHECK_TASK_KEY);
        var isKnownErrorsGsheet = (key === LEGACY_KNOWN_ERRORS_TASK_KEY);
        var currentTask = allTasks.find(function (t) {
            return t.id === editingTaskId;
        }) || {};
        var supportsMp = !!(cls && cls.multi_process)
            || ('ncores' in currentTask)
            || ('mp_backend' in currentTask)
            || ('mp_start_method' in currentTask);
        var supportsLocalTask = !!(cls && cls.local_task)
            || !!currentTask.local_task
            || ('sync_source' in currentTask)
            || ('sync_profiles' in currentTask)
            || key === 'APERO_OBJECT_QUERY';
        var syncState = collectSyncProfiles(false);
        if (cls) {
            editTaskInfoRow.style.display = '';
            editTaskName.textContent = cls.name;
            editTaskDesc.textContent = cls.description;
        } else {
            editTaskInfoRow.style.display = 'none';
        }
        editBackupFields.style.display = isBackup ? '' : 'none';
        if (editLegacyGsheetFields) {
            editLegacyGsheetFields.style.display = isLegacyGsheet ? '' : 'none';
        }
        if (editCheckGsheetUrlFields) {
            editCheckGsheetUrlFields.style.display = isCheckGsheet ? '' : 'none';
        }
        if (editOverrideSheetUrlField) {
            editOverrideSheetUrlField.style.display = isCheckGsheet ? '' : 'none';
        }
        if (editKnownErrorsSheetUrlField) {
            editKnownErrorsSheetUrlField.style.display = isKnownErrorsGsheet ? '' : 'none';
        }
        var isAssets = key === ASSETS_TASK_KEY;
        if (editAssetsFields) editAssetsFields.style.display = isAssets ? '' : 'none';
        if (isAssets) updateAssetsLocalSrcVisibility();

        if (editLocalSyncFields) {
            editLocalSyncFields.style.display = supportsLocalTask ? '' : 'none';
        }

        editMpFields.style.display = (supportsMp && syncState.anyRunOnServer)
            ? ''
            : 'none';

        if (supportsMp && syncState.anyRunOnServer) {
            renderNcoresWarning();
        }
        editRunCountRow.style.display = editingTaskId ? '' : 'none';
        renderTaskFilters(key, currentTask);
    }

    function renderNcoresWarning() {
        if (!editMpWarn) return;
        var ncores = parseInt(editNcores.value, 10) || 1;
        var rec = parseInt(mpConfig.recommended_max_cores, 10) || 1;
        if (ncores > rec) {
            editMpWarn.style.display = '';
            var hint = editMpWarn.querySelector('.at-muted-hint');
            if (hint) {
                hint.textContent = 'Warning: this server recommends <= ' + rec + ' cores (N-1). You can still save this value.';
            }
        } else {
            editMpWarn.style.display = 'none';
        }
    }

    if (editTaskKey) {
        editTaskKey.addEventListener('change', onTaskKeyChange);
    }

    function bindEditModal() {
        if (!btnEditCancel || !btnEditClose || !btnEditSave || !editModal) {
            return;
        }
        btnEditCancel.addEventListener('click', closeEditModal);
        btnEditClose.addEventListener('click', closeEditModal);
        btnEditSave.addEventListener('click', saveTask);
        if (editTabRunBtn) {
            editTabRunBtn.addEventListener('click', function () { selectEditTab('run'); });
        }
        if (editTabFiltersBtn) {
            editTabFiltersBtn.addEventListener('click', function () { selectEditTab('filters'); });
        }
        if (editNcores) {
            editNcores.addEventListener('input', renderNcoresWarning);
        }
        // Close on backdrop click
        editModal.addEventListener('click', function (e) {
            if (e.target === editModal) closeEditModal();
        });
        if (editGoogleOauthFile) {
            editGoogleOauthFile.addEventListener('change', onOauthFileChange);
        }
        if (editGoogleOauthAuthBtn) {
            editGoogleOauthAuthBtn.addEventListener('click', startGsheetOauth);
        }
    }

    function closeEditModal() {
        editModal.style.display = 'none';
        editTaskKey.disabled = false;
        editingTaskId = null;
    }

    function saveTask() {
        var taskKey = editTaskKey.value.trim();
        var cls = taskClasses.find(function (c) { return c.key === taskKey; }) || {};
        var currentTask = allTasks.find(function (t) {
            return t.id === editingTaskId;
        }) || {};
        var supportsMp = !!cls.multi_process
            || ('ncores' in currentTask)
            || ('mp_backend' in currentTask)
            || ('mp_start_method' in currentTask);
        var supportsLocalTask = !!cls.local_task
            || !!currentTask.local_task
            || ('sync_source' in currentTask)
            || ('sync_profiles' in currentTask)
            || taskKey === 'APERO_OBJECT_QUERY';
        var syncState;
        var frequency = parseFloat(editFrequency.value);
        var dailyCopies = parseInt(editDailyCopies.value, 10) || 0;
        var weeklyCopies = parseInt(editWeeklyCopies.value, 10) || 0;
        var backupMaxSizeMb = null;
        if (editBackupMaxSizeMb) {
            backupMaxSizeMb = parseFloat(editBackupMaxSizeMb.value);
        }
        var ncores = parseInt(editNcores.value, 10) || 1;
        var mpBackend = (editMpBackend.value || 'threads').trim();
        var mpStartMethod = (editMpStartMethod.value || 'default').trim();
        try {
            syncState = collectSyncProfiles(true);
        } catch (err) {
            showToast(err.message, 'error');
            return;
        }
        if (!taskKey) { showToast('Missing task key.', 'error'); return; }
        if (isNaN(frequency) || frequency <= 0) { showToast('Frequency must be a positive number of hours.', 'error'); return; }
        if (dailyCopies < 0 || weeklyCopies < 0) { showToast('Backup copy counts must be non-negative.', 'error'); return; }
        if (supportsMp && syncState.anyRunOnServer && ncores <= 0) {
            showToast('NCORES must be >= 1.', 'error');
            return;
        }
        if (taskKey === BACKUP_TASK_KEY && dailyCopies + weeklyCopies <= 0) {
            showToast('Backup task needs at least one retained daily or weekly copy.', 'error');
            return;
        }
        if (taskKey === BACKUP_TASK_KEY) {
            if (!isFinite(backupMaxSizeMb) || backupMaxSizeMb <= 0) {
                showToast('Max archive input size (MB) must be a positive number.', 'error');
                return;
            }
        }
        var payload = {
            instrument: currentInstrument,
            task_key: taskKey,
            frequency: frequency,
            daily_copies: dailyCopies,
            weekly_copies: weeklyCopies,
            active: editActive.checked,
            filters: {},
        };
        if (
            taskKey === LEGACY_ASTROM_TASK_KEY
            || taskKey === LEGACY_REJECT_TASK_KEY
            || taskKey === LEGACY_CHECK_TASK_KEY
            || taskKey === LEGACY_KNOWN_ERRORS_TASK_KEY
        ) {
            payload.dry_run = !!(editDryRun && editDryRun.checked);
            payload.google_secret_name = editGoogleSecretName
                ? String(editGoogleSecretName.value || '').trim()
                : 'legacy_gsheet_oauth.json';
        }
        if (taskKey === LEGACY_CHECK_TASK_KEY) {
            payload.monitoring_sheet_url = editMonitoringSheetUrl
                ? (editMonitoringSheetUrl.value || '').trim()
                : '';
            payload.override_sheet_url = editOverrideSheetUrl
                ? (editOverrideSheetUrl.value || '').trim()
                : '';
        }
        if (taskKey === LEGACY_KNOWN_ERRORS_TASK_KEY) {
            payload.sheet_url = editKnownErrorsSheetUrl
                ? (editKnownErrorsSheetUrl.value || '').trim()
                : '';
        }
        if (taskKey === BACKUP_TASK_KEY && isFinite(backupMaxSizeMb)
                && backupMaxSizeMb > 0) {
            payload.backup_max_size_mb = backupMaxSizeMb;
        }
        if (taskKey === BACKUP_TASK_KEY) {
            // Always send the exclude lists (even if empty) so an
            // admin can remove a previously-set override and revert
            // to the built-in defaults.
            var splitLines = function (el) {
                if (!el) return [];
                var raw = String(el.value || '').split(/\r?\n/);
                var out = [];
                for (var i = 0; i < raw.length; i++) {
                    var s = raw[i].trim();
                    if (s && out.indexOf(s) === -1) out.push(s);
                }
                return out;
            };
            payload.exclude_dirs = splitLines(editBackupExcludeDirs);
            payload.exclude_paths = splitLines(editBackupExcludePaths);
        }
        if (taskKey === ASSETS_TASK_KEY) {
            payload.assets_mode = editAssetsMode
                ? editAssetsMode.value
                : 'remote';
            if (editAssetsLocalSrc) {
                payload.assets_local_source_path = String(
                    editAssetsLocalSrc.value || ''
                ).trim();
            }
            if (editAssetsDrsUconfig) {
                payload.assets_drs_uconfig = String(
                    editAssetsDrsUconfig.value || ''
                ).trim();
            }
        }
        Object.keys(editFilterInputs || {}).forEach(function (keyName) {
            var inputEl = editFilterInputs[keyName];
            if (!inputEl) return;
            payload.filters[keyName] = String(inputEl.value || '').trim();
        });
        if (supportsMp && syncState.anyRunOnServer) {
            payload.ncores = ncores;
            payload.mp_backend = mpBackend;
            payload.mp_start_method = mpStartMethod;
        }
        if (supportsLocalTask) {
            payload.sync_profiles = syncState.profiles;
        }
        payload.id = editingTaskId;

        var doSave = function () {
            setSaveBusy(true);
            fetch(urls.save, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            }).then(function (r) { return r.json(); }).then(function (d) {
                setSaveBusy(false);
                if (d.success) {
                    closeEditModal();
                    showToast('Task saved.', 'success');
                    if (Array.isArray(d.warnings) && d.warnings.length) {
                        showToast(d.warnings.join(' '), 'error');
                    }
                    refreshCurrentTasks();
                } else {
                    showToast('Save failed: ' + d.error, 'error');
                }
            }).catch(function () {
                setSaveBusy(false);
                showToast('Save failed: network or server error.', 'error');
            });
        };

        var isLegacyGsheet = (
            taskKey === LEGACY_ASTROM_TASK_KEY
            || taskKey === LEGACY_REJECT_TASK_KEY
            || taskKey === LEGACY_CHECK_TASK_KEY
            || taskKey === LEGACY_KNOWN_ERRORS_TASK_KEY
        );
        var hasOauthFile = !!(
            editGoogleOauthFile
            && editGoogleOauthFile.files
            && editGoogleOauthFile.files[0]
        );
        // If the selected file is a raw client_secret (handled by the
        // OAuth flow), skip the upload — the credential is already saved.
        var isClientSecret = hasOauthFile && !!_pendingClientSecret;
        if (!isLegacyGsheet || !hasOauthFile || isClientSecret) {
            doSave();
            return;
        }

        setSaveBusy(true);
        var reader = new FileReader();
        reader.onload = function (evt) {
            var text = String((evt && evt.target && evt.target.result) || '');
            var parsed = null;
            try {
                parsed = JSON.parse(text);
            } catch (err) {
                setSaveBusy(false);
                showToast('Invalid OAuth JSON file.', 'error');
                return;
            }
            if (!parsed || typeof parsed !== 'object') {
                setSaveBusy(false);
                showToast('Invalid OAuth JSON payload.', 'error');
                return;
            }
            payload.google_oauth_upload = parsed;
            doSave();
        };
        reader.onerror = function () {
            setSaveBusy(false);
            showToast('Could not read OAuth JSON file.', 'error');
        };
        reader.readAsText(editGoogleOauthFile.files[0]);
    }

    var _pendingClientSecret = null;

    function _isClientSecretFile(parsed) {
        return parsed && typeof parsed === 'object'
            && (parsed.installed || parsed.web)
            && !parsed.refresh_token
            && !parsed.private_key;
    }

    function onOauthFileChange() {
        if (!editGoogleOauthFile || !editGoogleOauthFile.files
                || !editGoogleOauthFile.files[0]) {
            _pendingClientSecret = null;
            if (editGoogleOauthAuthBtn) editGoogleOauthAuthBtn.style.display = 'none';
            if (editGoogleOauthHint) editGoogleOauthHint.textContent = '';
            return;
        }
        var reader = new FileReader();
        reader.onload = function (evt) {
            var text = String((evt && evt.target && evt.target.result) || '');
            var parsed = null;
            try { parsed = JSON.parse(text); } catch (_) {}
            if (!parsed) {
                _pendingClientSecret = null;
                if (editGoogleOauthAuthBtn) editGoogleOauthAuthBtn.style.display = 'none';
                return;
            }
            if (_isClientSecretFile(parsed)) {
                _pendingClientSecret = parsed;
                if (editGoogleOauthAuthBtn) {
                    editGoogleOauthAuthBtn.style.display = '';
                }
                if (editGoogleOauthHint) {
                    editGoogleOauthHint.textContent =
                        'This is a client secret file — click "Authorize with Google"'
                        + ' to complete the OAuth flow and get a refresh token.';
                    editGoogleOauthHint.style.color = 'var(--ari-warning, #c07000)';
                }
            } else {
                _pendingClientSecret = null;
                if (editGoogleOauthAuthBtn) editGoogleOauthAuthBtn.style.display = 'none';
                if (editGoogleOauthHint) {
                    editGoogleOauthHint.textContent = '';
                }
            }
        };
        reader.readAsText(editGoogleOauthFile.files[0]);
    }

    function startGsheetOauth() {
        if (!_pendingClientSecret) {
            showToast('Select a client secret JSON file first.', 'error');
            return;
        }
        var secretName = (editGoogleSecretName && editGoogleSecretName.value.trim())
            || 'legacy_gsheet_oauth.json';
        if (editGoogleOauthAuthBtn) {
            editGoogleOauthAuthBtn.disabled = true;
            editGoogleOauthAuthBtn.textContent = 'Opening…';
        }
        fetch('/api/admin/async-tasks/gsheet-oauth-start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                client_secret: _pendingClientSecret,
                secret_name: secretName,
            }),
        }).then(function (r) { return r.json(); })
          .then(function (d) {
            if (editGoogleOauthAuthBtn) {
                editGoogleOauthAuthBtn.disabled = false;
                editGoogleOauthAuthBtn.innerHTML =
                    '<i class="fa-brands fa-google"></i> Authorize with Google';
            }
            if (!d.ok) {
                showToast('OAuth start failed: ' + d.error, 'error');
                return;
            }
            var popup = window.open(d.auth_url, 'gsheet_oauth',
                'width=600,height=700,left=200,top=100');
            if (!popup) {
                showToast('Pop-up blocked — allow pop-ups and retry.', 'error');
                return;
            }
            if (editGoogleOauthHint) {
                editGoogleOauthHint.textContent =
                    'Complete authorization in the pop-up window, then save the task.';
                editGoogleOauthHint.style.color = 'var(--ari-success, #2a7a2a)';
            }
        }).catch(function () {
            if (editGoogleOauthAuthBtn) {
                editGoogleOauthAuthBtn.disabled = false;
                editGoogleOauthAuthBtn.innerHTML =
                    '<i class="fa-brands fa-google"></i> Authorize with Google';
            }
            showToast('OAuth start failed: network error.', 'error');
        });
    }

    var _editSaveOrigHtml = null;

    function setSaveBusy(busy) {
        if (!btnEditSave) return;
        if (busy) {
            if (_editSaveOrigHtml === null) {
                _editSaveOrigHtml = btnEditSave.innerHTML;
            }
            btnEditSave.disabled = true;
            btnEditSave.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
        } else {
            btnEditSave.disabled = false;
            if (_editSaveOrigHtml !== null) {
                btnEditSave.innerHTML = _editSaveOrigHtml;
            }
        }
    }

    /* -----------------------------------------------------------------------
       Delete modal
    ----------------------------------------------------------------------- */
    function bindDeleteModal() {
        if (!btnDeleteCancel || !btnDeleteConfirm || !deleteModal) {
            return;
        }
        btnDeleteCancel.addEventListener('click', function () {
            deleteModal.style.display = 'none';
            pendingDeleteId = null;
        });
        btnDeleteConfirm.addEventListener('click', function () {
            if (!pendingDeleteId) return;
            fetch(urls.delete, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ instrument: currentInstrument, id: pendingDeleteId }),
            }).then(function (r) { return r.json(); }).then(function (d) {
                deleteModal.style.display = 'none';
                if (d.success) {
                    showToast('Task deleted.', 'success');
                    if (selectedTaskId === pendingDeleteId) {
                        selectedTaskId = null;
                        showDetail(null);
                    }
                    pendingDeleteId = null;
                    refreshCurrentTasks();
                } else {
                    showToast('Delete failed: ' + d.error, 'error');
                }
            });
        });
        // Close on backdrop click
        deleteModal.addEventListener('click', function (e) {
            if (e.target === deleteModal) {
                deleteModal.style.display = 'none';
                pendingDeleteId = null;
            }
        });
    }

    /* -----------------------------------------------------------------------
       Queue tab
    ----------------------------------------------------------------------- */
    function bindQueue() {
        if (!btnStopAll) return;
        btnStopAll.addEventListener('click', function () {
            fetch(urls.stop, { method: 'POST' })
                .then(function (r) { return r.json(); })
                .then(function (d) {
                    if (d.success) {
                        showToast('Queue cleared.', 'success');
                        refreshQueueView();
                    } else {
                        showToast('Stop failed: ' + d.error, 'error');
                    }
                });
        });

        if (btnKillAll) {
            btnKillAll.addEventListener('click', function () {
                if (!confirm('Kill ALL async tasks immediately? This will interrupt the running task and clear the queue.')) return;
                fetch(urls.killAll, { method: 'POST' })
                    .then(function (r) { return r.json(); })
                    .then(function (d) {
                        if (d.success) {
                            showToast('All tasks killed. Queue cleared.', 'success');
                            refreshQueueView();
                            refreshCurrentTasks();
                        } else {
                            showToast('Kill failed: ' + (d.error || 'Unknown error'), 'error');
                        }
                    });
            });
        }

        if (btnClearHistory) {
            btnClearHistory.addEventListener('click', function () {
                if (!confirm('Clear recent async task history? This cannot be undone.')) return;
                fetch(urls.clearHistory, { method: 'POST' })
                    .then(function (r) { return r.json(); })
                    .then(function (d) {
                        if (d.success) {
                            showToast('Recent history cleared.', 'success');
                            refreshQueueView();
                        } else {
                            showToast('Clear history failed: ' + (d.error || 'Unknown error'), 'error');
                        }
                    });
            });
        }
    }

    function refreshQueueView() {
        return fetch(urls.status)
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (!d.success) return;
                updatePollCadence(d.queue);
                renderQueuePanel(d.queue, d.statuses || {});
            });
    }

    function renderQueuePanel(queue, statuses) {
        if (!queue) return;
        var current = queue.current;
        var pending = queue.queue || [];

        if (current) {
            var currentInfo = queue.current_info || {};
            var tid = currentInfo.task_id || current[1];
            var inst = currentInfo.instrument || current[0];
            var tname = currentInfo.task_name || tid;
            var st = statuses[tid] || {};
            var useSubprocess = !!st.use_subprocess;
            queueRunning.style.display = '';
            queueRunningName.textContent = tname;
            queueRunningInstr.textContent = inst;
            var pct = ((st.progress || 0) * 100).toFixed(2);
            queueProgressFill.style.width = pct + '%';
            queueProgressPct.textContent = pct + '%';
            if (queueSubprogressRow) {
                var subPct = ((st.subprogress || 0) * 100).toFixed(2);
                queueSubprogressRow.style.display = useSubprocess ? '' : 'none';
                queueSubprogressFill.style.width = subPct + '%';
                queueSubprogressPct.textContent = subPct + '%';
            }
            if (st.info && window.marked) {
                queueRunningInfo.innerHTML = window.marked.parse(st.info);
            } else {
                queueRunningInfo.innerHTML = '';
            }
            if (queueBtnStop) {
                var isCancelling = (st.status === 'cancelling');
                queueBtnStop.disabled = isCancelling;
                queueBtnStop.title = isCancelling ? 'Cancellation requested…' : 'Stop this task';
                queueBtnStop.onclick = function () { cancelTask(tid, tname); };
            }
            if (queueBtnViewLog) {
                queueBtnViewLog.onclick = function () {
                    openLiveTaskLog(tid, tname);
                };
            }
        } else {
            queueRunning.style.display = 'none';
            if (queueSubprogressRow) {
                queueSubprogressRow.style.display = 'none';
            }
            if (queueBtnStop) {
                queueBtnStop.onclick = null;
            }
            if (queueBtnViewLog) {
                queueBtnViewLog.onclick = null;
            }
        }

        if (pending.length === 0) {
            queuePendingList.innerHTML = '<div class="ari-sg-empty-small">Queue is empty</div>';
        } else {
            var pendingInfo = Array.isArray(queue.queue_info) ? queue.queue_info : [];
            queuePendingList.innerHTML = pending.map(function (entry, idx) {
                var info = pendingInfo[idx] || {};
                var instrument = info.instrument || entry[0] || '';
                var taskName = info.task_name || info.task_id || entry[1] || '';
                var taskId = info.task_id || entry[1] || '';
                return '<div class="at-queue-item">' +
                    '<span class="at-queue-item__inst">' + esc(instrument) + '</span>' +
                    '<span class="at-queue-item__id">' + esc(taskName) + '</span>' +
                    (taskId && taskId !== taskName
                        ? '<span class="at-queue-item__id" style="opacity:0.7;">' + esc(taskId) + '</span>'
                        : '') +
                    (taskId
                        ? '<button class="ari-btn ari-btn--sm ari-btn--danger at-queue-cancel-btn" data-task-id="' + esc(taskId) + '" data-task-name="' + esc(taskName) + '" style="margin-left:auto;">'
                          + '<i class="fa-solid fa-stop"></i> Stop</button>'
                          + '<button class="ari-btn ari-btn--sm ari-btn--secondary at-queue-log-btn" data-task-id="' + esc(taskId) + '" data-task-name="' + esc(taskName) + '">'
                          + '<i class="fa-solid fa-file-lines"></i> Log</button>'
                        : '') +
                    '</div>';
            }).join('');
            queuePendingList.querySelectorAll('.at-queue-cancel-btn').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    cancelTask(btn.dataset.taskId || '', btn.dataset.taskName || '');
                });
            });
            queuePendingList.querySelectorAll('.at-queue-log-btn').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    openLiveTaskLog(btn.dataset.taskId || '', btn.dataset.taskName || '');
                });
            });
        }

        var history = Array.isArray(queue.recent_history) ? queue.recent_history : [];
        if (!queueHistoryList) return;
        if (!history.length) {
            queueHistoryList.innerHTML = '<div class="ari-sg-empty-small">No recent history yet</div>';
            return;
        }
        queueHistoryList.innerHTML = history.map(function (item) {
            var ts = item.timestamp || '';
            var stamp = ts ? ts.replace('T', ' ').replace('Z', ' UTC') : '';
            var duration = Number(item.duration_seconds);
            var durationText = Number.isFinite(duration)
                ? (' (' + duration.toFixed(2) + 's)')
                : '';
            var line = '[' + (item.status || 'unknown') + '] ' +
                (item.instrument || '') + ' - ' + (item.task_name || item.task_id || '') +
                durationText;
            var taskId = item.task_id || '';
            var taskName = item.task_name || taskId || '';
            return '<div class="at-queue-item">' +
                '<span class="at-queue-item__inst">' + esc(stamp) + '</span>' +
                '<span class="at-queue-item__id">' + esc(line) + '</span>' +
                (taskId
                    ? '<button class="ari-btn ari-btn--sm ari-btn--secondary at-queue-log-btn" ' +
                      'data-task-id="' + esc(taskId) + '" data-task-name="' + esc(taskName) +
                      '" style="margin-left:auto;" title="View log">' +
                      '<i class="fa-solid fa-file-lines"></i> Log</button>'
                    : '') +
                '</div>';
        }).join('');
        queueHistoryList.querySelectorAll('.at-queue-log-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                openTaskLogOverlay(btn.dataset.taskId || '', btn.dataset.taskName || '');
            });
        });
    }

    /* -----------------------------------------------------------------------
       Running badge
    ----------------------------------------------------------------------- */
    function updateRunningBadge(queue) {
        var busy = queue && (queue.queue_length > 0 || queue.current);
        runningBadge.style.display = busy ? '' : 'none';
    }

    /* -----------------------------------------------------------------------
       Polling
    ----------------------------------------------------------------------- */
    function startPoll() {
        stopPoll();
        pollIntervalMs = POLL_SLOW_MS;
        scheduleNextPoll(pollIntervalMs);
    }

    function stopPoll() {
        if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
    }

    function scheduleNextPoll(delayMs) {
        stopPoll();
        pollTimer = setTimeout(pollStatus, Math.max(250, Number(delayMs) || POLL_SLOW_MS));
    }

    function updatePollCadence(queue) {
        var busy = !!(queue && (queue.queue_length > 0 || queue.current));
        pollIntervalMs = busy ? POLL_FAST_MS : POLL_SLOW_MS;
    }

    function pollStatus() {
        if (currentInstrument === null) {
            // queue tab
            refreshQueueView()
                .catch(function () {})
                .finally(function () {
                    scheduleNextPoll(pollIntervalMs);
                });
            return;
        }
        if (!allTasks.length) {
            pollIntervalMs = POLL_SLOW_MS;
            scheduleNextPoll(pollIntervalMs);
            return;
        }

        var ids = allTasks.map(function (t) { return t.id; }).filter(Boolean).join(',');
        fetch(urls.status + '?ids=' + encodeURIComponent(ids))
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (!d.success) return;
                updatePollCadence(d.queue);
                // Merge runtime statuses back into allTasks
                allTasks.forEach(function (t) {
                    if (d.statuses[t.id]) t.runtime = d.statuses[t.id];
                });
                renderTaskLists();
                updateRunningBadge(d.queue);
                if (selectedTaskId) updateDetailRuntime();
            })
            .catch(function () {
                pollIntervalMs = POLL_SLOW_MS;
            })
            .finally(function () {
                scheduleNextPoll(pollIntervalMs);
            });
    }

    /* -----------------------------------------------------------------------
       Utility
    ----------------------------------------------------------------------- */
    function statusClass(status) {
        switch (status) {
            case 'completed':   return 'ok';
            case 'in_progress': return 'running';
            case 'cancelling':  return 'queued';
            case 'queued':      return 'queued';
            case 'failed':      return 'error';
            case 'cancelled':   return 'cancelled';
            default:            return 'idle';
        }
    }

    function esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function copyToClipboard(text, okMessage) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text)
                .then(function () { showToast(okMessage || 'Copied to clipboard.', 'success'); })
                .catch(function () {
                    if (_copyWithExecCommand(text)) {
                        showToast(okMessage || 'Copied to clipboard.', 'success');
                    } else {
                        showToast('Copy failed.', 'error');
                    }
                });
            return;
        }
        if (_copyWithExecCommand(text)) {
            showToast(okMessage || 'Copied to clipboard.', 'success');
        } else {
            showToast('Copy failed.', 'error');
        }
    }

    function _copyWithExecCommand(text) {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        ta.setSelectionRange(0, ta.value.length);
        var ok = false;
        try {
            ok = document.execCommand('copy');
        } catch (_err) {
            ok = false;
        }
        document.body.removeChild(ta);
        return ok;
    }

    function bindOauthHelpModal() {
        var openBtn = document.getElementById('at-oauth-info-btn');
        var modal = document.getElementById('at-oauth-help-modal');
        var closeBtn = document.getElementById('at-oauth-help-close');
        var closeX = document.getElementById('at-oauth-help-close-x');
        if (!openBtn || !modal) return;
        function open() { modal.style.display = 'flex'; }
        function close() { modal.style.display = 'none'; }
        openBtn.addEventListener('click', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            open();
        });
        if (closeBtn) closeBtn.addEventListener('click', close);
        if (closeX) closeX.addEventListener('click', close);
        modal.addEventListener('click', function (ev) {
            if (ev.target === modal) close();
        });
        document.addEventListener('keydown', function (ev) {
            if (ev.key === 'Escape' && modal.style.display !== 'none') {
                close();
            }
        });
    }

    var toastTimer = null;
    function showToast(msg, type) {
        toast.textContent = msg;
        toast.className = 'ari-toast ari-toast--' + (type || 'info');
        toast.style.display = '';
        if (toastTimer) clearTimeout(toastTimer);
        toastTimer = setTimeout(function () { toast.style.display = 'none'; }, 3500);
    }

    /* -----------------------------------------------------------------------
       Bootstrap
    ----------------------------------------------------------------------- */
    document.addEventListener('DOMContentLoaded', init);

}());
