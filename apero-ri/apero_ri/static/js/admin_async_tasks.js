/* ==========================================================================
   Admin Async Tasks page logic
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_ASYNC_TASKS;
    var instruments = cfg.instruments || [];
    var urls = cfg.urls;

    /* -----------------------------------------------------------------------
       State
    ----------------------------------------------------------------------- */
    var currentInstrument = null;
    var allTasks = [];          // task configs for currentInstrument
    var taskClasses = [];       // available task classes from server
    var selectedTaskId = null;
    var editingTaskId = null;   // null = add, string = edit
    var pendingDeleteId = null;
    var pollTimer = null;
    var dragSrcId = null;

    /* -----------------------------------------------------------------------
       DOM refs
    ----------------------------------------------------------------------- */
    var tabsEl          = document.getElementById('at-tabs');
    var instrWs         = document.getElementById('at-instrument-workspace');
    var queueWs         = document.getElementById('at-queue-workspace');
    var noInstrEl       = document.getElementById('at-no-instruments');

    var btnRunAll       = document.getElementById('btn-run-all');
    var btnAddTask      = document.getElementById('btn-add-task');
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
    var detInfoEl       = document.getElementById('det-info');
    var detInfoEmpty    = document.getElementById('det-info-empty');
    var detErrorSection = document.getElementById('det-error-section');
    var detError        = document.getElementById('det-error');
    var detFilesSection = document.getElementById('det-files-section');
    var detOutputFiles  = document.getElementById('det-output-files');

    var detBtnToggle    = document.getElementById('det-btn-toggle');
    var detBtnEdit      = document.getElementById('det-btn-edit');
    var detBtnDelete    = document.getElementById('det-btn-delete');
    var detBtnRunNow    = document.getElementById('det-btn-run-now');

    // Queue tab
    var btnStopAll          = document.getElementById('btn-stop-all');
    var queueRunning        = document.getElementById('queue-running');
    var queueRunningName    = document.getElementById('queue-running-name');
    var queueRunningInstr   = document.getElementById('queue-running-instrument');
    var queueProgressFill   = document.getElementById('queue-progress-fill');
    var queueProgressPct    = document.getElementById('queue-progress-pct');
    var queueRunningInfo    = document.getElementById('queue-running-info');
    var queuePendingList    = document.getElementById('queue-pending-list');

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

    var toast = document.getElementById('at-toast');

    /* -----------------------------------------------------------------------
       Initialisation
    ----------------------------------------------------------------------- */
    function init() {
        renderTabs();
        loadTaskClasses();
        bindEditModal();
        bindDeleteModal();
        bindRunAllModal();
        bindQueue();
        bindRunAll();
        bindAddTask();
        bindFileModal();

        if (instruments.length === 0) {
            noInstrEl.style.display = '';
        } else {
            // Activate the first instrument tab
            selectTab(instruments[0]);
        }
    }

    /* -----------------------------------------------------------------------
       Tabs
    ----------------------------------------------------------------------- */
    function renderTabs() {
        tabsEl.innerHTML = '';
        instruments.forEach(function (inst) {
            var btn = document.createElement('button');
            btn.className = 'ari-sg-tab';
            btn.textContent = inst;
            btn.dataset.value = inst;
            btn.addEventListener('click', function () { selectTab(inst); });
            tabsEl.appendChild(btn);
        });

        // Queue tab
        var qBtn = document.createElement('button');
        qBtn.className = 'ari-sg-tab';
        qBtn.innerHTML = '<i class="fa-solid fa-layer-group"></i> Queue';
        qBtn.dataset.value = '__queue__';
        qBtn.addEventListener('click', function () { selectTab('__queue__'); });
        tabsEl.appendChild(qBtn);
    }

    function selectTab(value) {
        // Update active styling
        Array.from(tabsEl.querySelectorAll('.ari-sg-tab')).forEach(function (b) {
            b.classList.toggle('ari-sg-tab--active', b.dataset.value === value);
        });

        stopPoll();

        if (value === '__queue__') {
            currentInstrument = null;
            instrWs.style.display = 'none';
            queueWs.style.display = '';
            noInstrEl.style.display = 'none';
            refreshQueueView();
            startPoll();
            return;
        }

        currentInstrument = value;
        queueWs.style.display = 'none';
        noInstrEl.style.display = 'none';
        instrWs.style.display = '';
        selectedTaskId = null;
        showDetail(null);
        loadTasks();
        startPoll();
    }

    /* -----------------------------------------------------------------------
       Task list
    ----------------------------------------------------------------------- */
    function loadTasks() {
        if (!currentInstrument) return;
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

    function renderTaskLists() {
        var active   = allTasks.filter(function (t) { return t.active !== false; });
        var inactive = allTasks.filter(function (t) { return t.active === false; });

        activeCount.textContent   = active.length;
        inactiveCount.textContent = inactive.length;

        renderList(activeList, active, true);
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

        var card = document.createElement('div');
        card.className = 'at-task-card' +
            (task.id === selectedTaskId ? ' at-task-card--selected' : '') +
            (task.active === false ? ' at-task-card--inactive' : '');
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

        var queuedTag = isQueued
            ? '<span class="at-tag at-tag--queued">queued</span>'
            : (isRunning ? '<span class="at-tag at-tag--running">running</span>' : '');

        card.innerHTML =
            grip + statusDot +
            '<div class="at-task-card__body">' +
                '<span class="at-task-card__name">' + esc(task.name || task.task_key) + '</span>' +
                '<span class="at-task-card__freq">' + (task.frequency ? esc(task.frequency) + ' hrs' : '') + '</span>' +
                queuedTag +
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
            detInfoEl.style.display = '';
            detInfoEmpty.style.display = 'none';
            if (window.marked) {
                detInfoEl.innerHTML = window.marked.parse(rt.info);
            } else {
                detInfoEl.innerHTML = '<pre>' + esc(rt.info) + '</pre>';
            }
        } else {
            detInfoEl.style.display = 'none';
            detInfoEmpty.style.display = '';
        }

        // Error section
        if (rt.error) {
            detErrorSection.style.display = '';
            detError.textContent = rt.error;
        } else {
            detErrorSection.style.display = 'none';
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
                }
                html += '</div>';
                html += '<pre class="at-file-preview">' + esc(d.preview || '') + '</pre>';
                fileModalContent.innerHTML = html;
            })
            .catch(function () {
                fileModalContent.innerHTML = '<div class="ari-sg-error" style="padding:1rem;">Request failed</div>';
            });
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
            if (d.success) { loadTasks(); } else { showToast('Toggle failed: ' + d.error, 'error'); }
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
                loadTasks();
            } else {
                showToast('Run failed: ' + d.error, 'error');
            }
        });
    });

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
                loadTasks();
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
       Add Task
    ----------------------------------------------------------------------- */
    function bindAddTask() {
        btnAddTask.addEventListener('click', function () {
            openEditModal(null);
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
        editingTaskId = task ? task.id : null;
        editModalTitle.innerHTML = task
            ? '<i class="fa-solid fa-pen"></i> Edit Task'
            : '<i class="fa-solid fa-plus"></i> Add Task';

        editTaskKey.value = task ? (task.task_key || '') : '';
        editFrequency.value = task ? (task.frequency || 24) : 24;
        editDailyCopies.value = task ? (task.daily_copies || 0) : 7;
        editWeeklyCopies.value = task ? (task.weekly_copies || 0) : 4;
        editRunCount.value = task && task.runtime ? (task.runtime.run_count || 0) : 0;
        editActive.checked = task ? (task.active !== false) : true;
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
        editingTaskId = null;
    }

    function saveTask() {
        var taskKey = editTaskKey.value.trim();
        var frequency = parseFloat(editFrequency.value);
        var dailyCopies = parseInt(editDailyCopies.value, 10) || 0;
        var weeklyCopies = parseInt(editWeeklyCopies.value, 10) || 0;
        if (!taskKey) { showToast('Please select a task.', 'error'); return; }
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
        if (editingTaskId) payload.id = editingTaskId;

        fetch(urls.save, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        }).then(function (r) { return r.json(); }).then(function (d) {
            if (d.success) {
                closeEditModal();
                showToast('Task saved.', 'success');
                loadTasks();
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
                    loadTasks();
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
    }

    function refreshQueueView() {
        fetch(urls.status)
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (!d.success) return;
                renderQueuePanel(d.queue, d.statuses || {});
            });
    }

    function renderQueuePanel(queue, statuses) {
        if (!queue) return;
        var current = queue.current;
        var pending = queue.queue || [];

        if (current) {
            var tid = current[1];
            var inst = current[0];
            var st = statuses[tid] || {};
            queueRunning.style.display = '';
            queueRunningName.textContent = tid;
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
            queuePendingList.innerHTML = pending.map(function (entry) {
                return '<div class="at-queue-item">' +
                    '<span class="at-queue-item__inst">' + esc(entry[0]) + '</span>' +
                    '<span class="at-queue-item__id">' + esc(entry[1]) + '</span>' +
                    '</div>';
            }).join('');
        }
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
        pollTimer = setInterval(pollStatus, 2000);
    }

    function stopPoll() {
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    }

    function pollStatus() {
        if (currentInstrument === null) {
            // queue tab
            refreshQueueView();
            return;
        }
        if (!allTasks.length) return;

        var ids = allTasks.map(function (t) { return t.id; }).filter(Boolean).join(',');
        fetch(urls.status + '?ids=' + encodeURIComponent(ids))
            .then(function (r) { return r.json(); })
            .then(function (d) {
                if (!d.success) return;
                // Merge runtime statuses back into allTasks
                allTasks.forEach(function (t) {
                    if (d.statuses[t.id]) t.runtime = d.statuses[t.id];
                });
                renderTaskLists();
                updateRunningBadge(d.queue);
                if (selectedTaskId) updateDetailRuntime();
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
