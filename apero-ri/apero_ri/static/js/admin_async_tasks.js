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
    var taskClasses = [];       // available task classes from server
    var selectedTaskId = null;
    var editingTaskId = null;   // null = add, string = edit
    var pendingDeleteId = null;
    var pollTimer = null;
    var POLL_FAST_MS = 1000;
    var POLL_SLOW_MS = 5000;
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
    var detProgressRow  = document.getElementById('det-progress-row');
    var detProgressFill = document.getElementById('det-progress-fill');
    var detProgressPct  = document.getElementById('det-progress-pct');
    var detLastRun      = document.getElementById('det-last-run');
    var detRunCount     = document.getElementById('det-run-count');
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
    var detParamsSection = document.getElementById('det-params-section');
    var detParamsBody    = document.getElementById('det-params-body');
    var detTaskParams    = document.getElementById('det-task-params');
    var detInputParams   = document.getElementById('det-input-params');
    var detBtnToggleParams = document.getElementById('det-btn-toggle-params');
    var detFilesSection = document.getElementById('det-files-section');
    var detOutputFiles  = document.getElementById('det-output-files');

    var detBtnToggle    = document.getElementById('det-btn-toggle');
    var detBtnEdit      = document.getElementById('det-btn-edit');
    var detBtnDelete    = document.getElementById('det-btn-delete');
    var detBtnRunNow    = document.getElementById('det-btn-run-now');

    // Queue tab
    var btnStopAll          = document.getElementById('btn-stop-all');
    var btnClearHistory     = document.getElementById('btn-clear-history');
    var queueRunning        = document.getElementById('queue-running');
    var queueRunningName    = document.getElementById('queue-running-name');
    var queueRunningInstr   = document.getElementById('queue-running-instrument');
    var queueProgressFill   = document.getElementById('queue-progress-fill');
    var queueProgressPct    = document.getElementById('queue-progress-pct');
    var queueRunningInfo    = document.getElementById('queue-running-info');
    var queuePendingList    = document.getElementById('queue-pending-list');
    var queueHistoryList    = document.getElementById('queue-history-list');

    // Edit modal
    var editModal       = document.getElementById('at-edit-modal');
    var editModalTitle  = document.getElementById('edit-modal-title');
    var editTaskKey     = document.getElementById('edit-task-key');
    var editTaskInfoRow = document.getElementById('edit-task-info-row');
    var editTaskName    = document.getElementById('edit-task-name');
    var editTaskDesc    = document.getElementById('edit-task-desc');
    var editFrequency   = document.getElementById('edit-frequency');
    var editBackupFields= document.getElementById('edit-backup-fields');
    var editDailyCopies = document.getElementById('edit-daily-copies');
    var editWeeklyCopies= document.getElementById('edit-weekly-copies');
    var editRunCountRow = document.getElementById('edit-run-count-row');
    var editRunCount    = document.getElementById('edit-run-count');
    var editActive      = document.getElementById('edit-active');
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

    // File viewer modal
    var fileModal       = document.getElementById('at-file-modal');
    var fileModalTitle  = document.getElementById('file-modal-title');
    var fileModalContent= document.getElementById('file-modal-content');
    var btnFileModalClose= document.getElementById('btn-file-modal-close');
    var btnFileModalOk  = document.getElementById('btn-file-modal-ok');

    var BACKUP_TASK_KEY = 'ARI_LOCAL_DATA_BACKUP';
    var currentInfoText = '';
    var currentErrorText = '';

    var toast = document.getElementById('at-toast');

    /* -----------------------------------------------------------------------
       Initialisation
    ----------------------------------------------------------------------- */
    function init() {
        renderTabs();
        renderInstrumentCards();
        loadTaskClasses();
        bindEditModal();
        bindDeleteModal();
        bindRunAllModal();
        bindQueue();
        bindRunAll();
        bindFileModal();
        bindSectionToggles();

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
            btnRunAll.innerHTML = '<i class="fa-solid fa-play"></i> Run All Global';
            loadGlobalTasks();
            startPoll();
            return;
        }

        if (instrumentPicker) instrumentPicker.style.display = '';
        if (!currentInstrument || currentInstrument === GLOBAL_SCOPE) {
            currentInstrument = instruments[0] || null;
        }
        highlightInstrumentCard();
        btnRunAll.innerHTML = '<i class="fa-solid fa-play"></i> Run All';
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
                renderTaskLists();
                updateRunningBadge(data.queue);
                if (selectedTaskId) {
                    updateDetailRuntime();
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
                    updateDetailRuntime();
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

        card.innerHTML =
            grip + statusDot +
            '<div class="at-task-card__body">' +
                '<span class="at-task-card__name">' + esc(task.name || task.task_key) + '</span>' +
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

        var isActive = task.active !== false;
        detBtnToggle.querySelector('i').className =
            'fa-solid ' + (isActive ? 'fa-toggle-on' : 'fa-toggle-off');
        detBtnToggle.title = isActive ? 'Deactivate task' : 'Activate task';

        updateDetailRuntime();
    }

    function updateDetailRuntime() {
        var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
        if (!task) return;

        var rt = task.runtime || {};
        var status = rt.found ? rt.status : 'not_started';
        var progress = rt.found ? (rt.progress || 0) : 0;

        detStatusBadge.textContent = status.replace(/_/g, ' ');
        detStatusBadge.className = 'at-status-badge at-status-badge--' + statusClass(status);

        var isActive = (status === 'in_progress' || status === 'queued');
        detProgressRow.style.display = isActive ? '' : 'none';
        if (isActive) {
            var pct = Math.round(progress * 100);
            detProgressFill.style.width = pct + '%';
            detProgressPct.textContent = pct + '%';
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
            detTaskParams.textContent = formatJson(taskParams);
            detInputParams.textContent = formatJson(taskConfig);
        } else {
            detParamsSection.style.display = 'none';
            detTaskParams.textContent = '{}';
            detInputParams.textContent = '{}';
        }

        // Files section
        var files = rt.output_files || [];
        if (files.length) {
            detFilesSection.style.display = '';
            detOutputFiles.innerHTML = files.map(function (f) {
                return '<li class="at-file-list__item">' +
                    '<code class="at-file-list__path">' + esc(f) + '</code>' +
                    '<button class="ari-btn ari-btn--sm ari-btn--secondary at-file-preview-btn"' +
                    ' data-path="' + esc(f) + '">' +
                    '<i class="fa-solid fa-file-lines"></i> Preview</button>' +
                    '<button class="ari-btn ari-btn--sm ari-btn--secondary at-file-download-btn"' +
                    ' data-path="' + esc(f) + '">' +
                    '<i class="fa-solid fa-download"></i> Download</button>' +
                    '</li>';
            }).join('');
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
       File viewer
    ----------------------------------------------------------------------- */
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

    detBtnEdit.addEventListener('click', function () {
        if (!selectedTaskId) return;
        var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
        if (!task) return;
        openEditModal(task);
    });

    detBtnDelete.addEventListener('click', function () {
        if (!selectedTaskId) return;
        var task = allTasks.find(function (t) { return t.id === selectedTaskId; });
        if (!task) return;
        pendingDeleteId = task.id;
        deleteModalName.textContent = task.name || task.task_key;
        deleteModal.style.display = '';
    });

    detBtnRunNow.addEventListener('click', function () {
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
            }),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (d.success) {
                showToast('Task queued for immediate execution.', 'success');
                refreshCurrentTasks();
            } else {
                showToast('Run failed: ' + d.error, 'error');
            }
        });
    });

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

    /* -----------------------------------------------------------------------
       Run All
    ----------------------------------------------------------------------- */
    function bindRunAll() {
        btnRunAll.addEventListener('click', function () {
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
                        doRunAll('add');
                    }
                });
        });
    }

    function doRunAll(action) {
        var localDir = window.ARI_LOCAL_DATA_DIR || '';
        fetch(urls.runAll, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                instrument: currentInstrument,
                action: action,
                local_data_dir: localDir,
            }),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (d.success) {
                showToast('Added ' + (d.added || []).length + ' task(s) to queue.', 'success');
                refreshCurrentTasks();
            } else {
                showToast('Run All failed: ' + d.error, 'error');
            }
        });
    }

    function bindRunAllModal() {
        btnRunAllReplace.addEventListener('click', function () {
            runAllModal.style.display = 'none';
            doRunAll('replace');
        });
        btnRunAllAdd.addEventListener('click', function () {
            runAllModal.style.display = 'none';
            doRunAll('add');
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
        editDailyCopies.value = task.daily_copies || 0;
        editWeeklyCopies.value = task.weekly_copies || 0;
        editRunCount.textContent = task.runtime ? (task.runtime.run_count || 0) : 0;
        editActive.checked = task.active !== false;
        onTaskKeyChange();
        editModal.style.display = '';
    }

    function onTaskKeyChange() {
        var key = editTaskKey.value;
        var cls = taskClasses.find(function (c) { return c.key === key; });
        var isBackup = key === BACKUP_TASK_KEY;
        if (cls) {
            editTaskInfoRow.style.display = '';
            editTaskName.textContent = cls.name;
            editTaskDesc.textContent = cls.description;
        } else {
            editTaskInfoRow.style.display = 'none';
        }
        editBackupFields.style.display = isBackup ? '' : 'none';
        editRunCountRow.style.display = editingTaskId ? '' : 'none';
    }

    editTaskKey.addEventListener('change', onTaskKeyChange);

    function bindEditModal() {
        btnEditCancel.addEventListener('click', closeEditModal);
        btnEditClose.addEventListener('click', closeEditModal);
        btnEditSave.addEventListener('click', saveTask);
        // Close on backdrop click
        editModal.addEventListener('click', function (e) {
            if (e.target === editModal) closeEditModal();
        });
    }

    function closeEditModal() {
        editModal.style.display = 'none';
        editTaskKey.disabled = false;
        editingTaskId = null;
    }

    function saveTask() {
        var taskKey = editTaskKey.value.trim();
        var frequency = parseFloat(editFrequency.value);
        var dailyCopies = parseInt(editDailyCopies.value, 10) || 0;
        var weeklyCopies = parseInt(editWeeklyCopies.value, 10) || 0;
        if (!taskKey) { showToast('Missing task key.', 'error'); return; }
        if (isNaN(frequency) || frequency <= 0) { showToast('Frequency must be a positive number of hours.', 'error'); return; }
        if (dailyCopies < 0 || weeklyCopies < 0) { showToast('Backup copy counts must be non-negative.', 'error'); return; }
        if (taskKey === BACKUP_TASK_KEY && dailyCopies + weeklyCopies <= 0) {
            showToast('Backup task needs at least one retained daily or weekly copy.', 'error');
            return;
        }

        var payload = {
            instrument: currentInstrument,
            task_key: taskKey,
            frequency: frequency,
            daily_copies: dailyCopies,
            weekly_copies: weeklyCopies,
            active: editActive.checked,
        };
        payload.id = editingTaskId;

        fetch(urls.save, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (d.success) {
                closeEditModal();
                showToast('Task saved.', 'success');
                refreshCurrentTasks();
            } else {
                showToast('Save failed: ' + d.error, 'error');
            }
        });
    }

    /* -----------------------------------------------------------------------
       Delete modal
    ----------------------------------------------------------------------- */
    function bindDeleteModal() {
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
            queueRunning.style.display = '';
            queueRunningName.textContent = tname;
            queueRunningInstr.textContent = inst;
            var pct = Math.round((st.progress || 0) * 100);
            queueProgressFill.style.width = pct + '%';
            queueProgressPct.textContent = pct + '%';
            if (st.info && window.marked) {
                queueRunningInfo.innerHTML = window.marked.parse(st.info);
            } else {
                queueRunningInfo.innerHTML = '';
            }
        } else {
            queueRunning.style.display = 'none';
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
                    '</div>';
            }).join('');
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
            return '<div class="at-queue-item">' +
                '<span class="at-queue-item__inst">' + esc(stamp) + '</span>' +
                '<span class="at-queue-item__id">' + esc(line) + '</span>' +
                '</div>';
        }).join('');
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
