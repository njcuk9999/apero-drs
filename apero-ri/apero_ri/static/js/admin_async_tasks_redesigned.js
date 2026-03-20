/* ==========================================================================
   Admin Async Tasks page logic - REDESIGNED
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_ASYNC_TASKS;
    var instruments = cfg.instruments || [];
    var urls = cfg.urls;

    /* -------  State ------- */
    var globalTasks = [];
    var instrumentTasks = {}; // instrument -> [tasks]
    var taskClasses = {};     // task_key -> {name, desc, type}
    var currentLevel = 'global';  // 'global', 'instruments', 'queue'
    var currentInstrument = null;
    var selectedTaskId = null;
    var taskClassesByKey = {};
    var pollTimer = null;

    /* ------- DOM refs ------- */
    var topTabsEl = document.getElementById('at-top-tabs');
    var globalWorkspace = document.getElementById('at-global-workspace');
    var instrumentsWorkspace = document.getElementById('at-instruments-workspace');
    var queueWorkspace = document.getElementById('at-queue-workspace');
    var noInstrEl = document.getElementById('at-no-instruments');
    
    var globalTasksContainer = document.getElementById('global-tasks-container');
    var instrumentsTasksContainer = document.getElementById('instruments-tasks-container');

    /* -------  Initialize ------- */
    function init() {
        if (!instruments || instruments.length === 0) {
            noInstrEl.style.display = '';
            return;
        }

        setupTabHandlers();
        loadTaskClasses();
        loadGlobalTasks();
        instruments.forEach(function(inst) {
            loadInstrumentTasks(inst);
        });
        startPoll();
    }

    /* ------- Event handlers ------- */
    function setupTabHandlers() {
        document.querySelectorAll('#at-top-tabs .ari-sg-tab').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var level = this.dataset.level;
                selectLevel(level);
            });
        });
    }

    function selectLevel(level) {
        currentLevel = level;
        document.querySelectorAll('#at-top-tabs .ari-sg-tab').forEach(function(b) {
            b.classList.toggle('ari-sg-tab--active', b.dataset.level === level);
        });

        globalWorkspace.style.display = (level === 'global') ? 'block' : 'none';
        instrumentsWorkspace.style.display = (level === 'instruments') ? 'block' : 'none';
        queueWorkspace.style.display = (level === 'queue') ? 'block' : 'none';

        if (level === 'global') {
            renderGlobalTasks();
        } else if (level === 'instruments') {
            renderInstrumentTasks();
        } else if (level === 'queue') {
            refreshQueueView();
        }
    }

    /* ------- API calls ------- */
    function loadTaskClasses() {
        fetch(urls.taskList)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    taskClasses = {};
                    (data.tasks || []).forEach(function(t) {
                        taskClasses[t.key] = t;
                        taskClassesByKey[t.key] = t;
                    });
                }
            });
    }

    function loadGlobalTasks() {
        fetch(urls.globalList)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    globalTasks = data.tasks || [];
                    if (currentLevel === 'global') {
                        renderGlobalTasks();
                    }
                }
            });
    }

    function loadInstrumentTasks(instrument) {
        fetch(urls.list + '?instrument=' + encodeURIComponent(instrument))
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.success) {
                    var instTasks = (data.tasks || []).filter(function(t) {
                        return (t.task_type || 'INSTRUMENT') === 'INSTRUMENT';
                    });
                    instrumentTasks[instrument] = instTasks;
                    if (currentLevel === 'instruments') {
                        renderInstrumentTasks();
                    }
                }
            });
    }

    /* ------- Render ------- */
    function renderGlobalTasks() {
        if (globalTasks.length === 0) {
            globalTasksContainer.innerHTML = '<div class="ari-sg-empty-small" style="grid-column: 1/-1;">No global tasks</div>';
            return;
        }

        globalTasksContainer.innerHTML = '';
        globalTasks.forEach(function(task) {
            var card = createTaskCard(task);
            card.addEventListener('click', function() {
                selectTask(task);
            });
            globalTasksContainer.appendChild(card);
        });
    }

    function renderInstrumentTasks() {
        instrumentsTasksContainer.innerHTML = '';
        
        instruments.forEach(function(inst) {
            var tasks = instrumentTasks[inst] || [];
            if (tasks.length === 0) return;

            var section = document.createElement('div');
            section.className = 'at-instrument-section';
            
            var header = document.createElement('h3');
            header.textContent = inst;
            header.style.marginTop = '2rem';
            section.appendChild(header);

            var grid = document.createElement('div');
            grid.className = 'at-tasks-grid';
            
            tasks.forEach(function(task) {
                var card = createTaskCard(task);
                card.addEventListener('click', function() {
                    currentInstrument = inst;
                    selectTask(task);
                });
                grid.appendChild(card);
            });
            
            section.appendChild(grid);
            instrumentsTasksContainer.appendChild(section);
        });
    }

    function createTaskCard(task) {
        var card = document.createElement('div');
        card.className = 'at-task-card';
        card.dataset.taskId = task.id;

        var isActive = task.active !== false;
        var statusColor = isActive ? '#4caf50' : '#f44336';
        var statusIcon = isActive ? '✓' : '✕';

        var taskKey = task.task_key || '';
        var taskClass = taskClasses[taskKey] || {};
        
        card.innerHTML = 
            '<div style="color: ' + statusColor + '; font-weight: bold; font-size: 1.2rem;">' + statusIcon + '</div>' +
            '<div style="font-weight: bold;">' + (taskClass.name || taskKey) + '</div>' +
            '<div style="font-size: 0.9rem; color: #666;">(' + (task.frequency || 24) + ' hrs)</div>';

        card.style.cssText = 'padding: 1rem; border: 2px solid ' + statusColor + '; border-radius: 4px; ' +
            'background: ' + (isActive ? '#f1f8e9' : '#ffebee') + '; cursor: pointer; ' +
            'text-align: center; transition: all 0.2s;';

        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = 'none';
        });

        return card;
    }

    function selectTask(task) {
        selectedTaskId = task.id;
        var detailArea = (currentLevel === 'global') ? 
            document.getElementById('at-detail-area-global') :
            document.getElementById('at-detail-area-instruments');
        
        renderTaskDetail(task, detailArea);
    }

    function renderTaskDetail(task, container) {
        container.innerHTML = '';
        
        var taskKey = task.task_key || '';
        var taskClass = taskClasses[taskKey] || {};
        var isActive = task.active !== false;
        var statusColor = isActive ? '#4caf50' : '#f44336';
        var statusText = isActive ? 'ACTIVE' : 'INACTIVE';

        var detailHTML = 
            '<div style="background: ' + statusColor + '; color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1.5rem;">' +
            '<strong>' + statusText + '</strong>' +
            '</div>' +
            '<div style="background: #f5f5f5; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;">' +
            '<p><strong>' + (taskClass.name || taskKey) + '</strong></p>' +
            '<p style="margin: 0.5rem 0; font-size: 0.9rem; color: #666;">' + (taskClass.description || '') + '</p>' +
            '<p style="margin: 0.5rem 0;"><strong>Frequency:</strong> ' + (task.frequency || 24) + ' hours</p>' +
            '<p style="margin: 0.5rem 0;"><strong>Last run:</strong> ' + (task.runtime && task.runtime.last_run ? task.runtime.last_run : 'Never') + '</p>' +
            '<p style="margin: 0.5rem 0;"><strong>Times run:</strong> ' + ((task.runtime && task.runtime.run_count) || 0) + '</p>' +
            '</div>' +
            '<div style="display: flex; gap: 0.5rem;">' +
            '<button class="ari-btn ari-btn--primary" onclick="toggleTask(\'' + task.id + '\', ' + !isActive + ');">' +
            (isActive ? '<i class="fa-solid fa-toggle-on"></i> Deactivate' : '<i class="fa-solid fa-toggle-on"></i> Activate') +
            '</button>' +
            '<button class="ari-btn ari-btn--secondary" onclick="runTaskNow(\'' + task.id + '\');"><i class="fa-solid fa-play"></i> Run Now</button>' +
            '</div>';

        container.innerHTML = detailHTML;
    }

    /* ------- Queue ------- */
    function refreshQueueView() {
        fetch(urls.status)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                // Render queue UI
                // (keep existing queue logic)
            });
    }

    function startPoll() {
        pollTimer = setInterval(function() {
            if (currentLevel === 'global') {
                loadGlobalTasks();
            } else if (currentLevel === 'instruments' && currentInstrument) {
                loadInstrumentTasks(currentInstrument);
            } else if (currentLevel === 'queue') {
                refreshQueueView();
            }
        }, 3000);
    }

    function stopPoll() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    /* ------- Global functions for inline onclick ------- */
    window.toggleTask = function(taskId, newState) {
        var task = getTaskById(taskId);
        if (!task) return;
        
        var instrument = currentInstrument || task.instrument || instruments[0];
        
        fetch(urls.toggle, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: taskId,
                instrument: instrument,
                active: newState,
            }),
        }).then(function(r) { return r.json(); })
          .then(function(d) {
              if (d.success) {
                  if (currentLevel === 'global') {
                      loadGlobalTasks();
                  } else {
                      loadInstrumentTasks(instrument);
                  }
              }
          });
    };

    window.runTaskNow = function(taskId) {
        var task = getTaskById(taskId);
        if (!task) return;
        
        var instrument = currentInstrument || task.instrument || instruments[0];
        
        fetch(urls.runNow, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: taskId,
                instrument: instrument,
            }),
        }).then(function(r) { return r.json(); })
          .then(function(d) {
              if (d.success) {
                  selectLevel('queue');
              }
          });
    };

    function getTaskById(taskId) {
        for (var i = 0; i < globalTasks.length; i++) {
            if (globalTasks[i].id === taskId) return globalTasks[i];
        }
        for (var inst in instrumentTasks) {
            for (var j = 0; j < instrumentTasks[inst].length; j++) {
                if (instrumentTasks[inst][j].id === taskId) return instrumentTasks[inst][j];
            }
        }
        return null;
    }

    /* ------- Start ------- */
    init();
})();
