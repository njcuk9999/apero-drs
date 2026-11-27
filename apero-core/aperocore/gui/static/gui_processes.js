/* ==========================================================================
   aperocore gui - processes page

   GUI.Processes(containerId, opts) renders the process registry (see
   aperocore.gui.procs): a tool bar (stop selected, Slurm jobs, remove
   selected, clear finished, reset list, show finished) and a table with
   one row per process (status, kind, description, start / finish, where,
   logs). Clicking a row (or a log button) opens its log(s) in the log
   viewer. The table refreshes every 5 s while its tab is shown.
   ========================================================================== */
var GUI = window.GUI || {};
window.GUI = GUI;

GUI.PROC_ACTIVE = {running: true, pending: true, unknown: true};

GUI.Processes = function (containerId, opts) {
    this.container = document.getElementById(containerId);
    this.opts = opts || {};
    this.data = [];
    this.checked = {};
    this.slurm = false;
    this.loading = false;
    this.build();
    var self = this;
    setInterval(function () {
        if (!self.opts.tab || GUI.currentTab === self.opts.tab) {
            self.refresh();
        }
    }, 5000);
    if (this.opts.tab) { GUI.onTab(this.opts.tab, function () {
        self.refresh(); }); }
    GUI.onDataChange(function () { self.refresh(); });
};

GUI.Processes.prototype.build = function () {
    var self = this;
    this.container.innerHTML =
        '<div class="section-card proc-bar"><span class="proc-actions">' +
        '<button class="danger" data-op="stop">&#9632; Stop selected' +
        '</button><button data-op="slurm" style="display:none">Slurm jobs' +
        '</button><button data-op="remove">Remove selected from list' +
        '</button><button data-op="clear_finished">Clear finished</button>' +
        '<button class="danger" data-op="clear_all">Reset process list' +
        '</button><button data-op="refresh">&#8635; Refresh</button>' +
        '</span><label class="inline"><input type="checkbox" ' +
        'data-role="finished" checked> Show finished</label>' +
        '<span class="muted small" data-role="note"></span></div>' +
        '<div class="section-card table-wrap"><table><thead><tr>' +
        '<th><input type="checkbox" data-role="all"></th><th>Status</th>' +
        '<th>Kind</th><th>Description</th><th>Started</th><th>Finished</th>' +
        '<th>Where</th><th>Logs</th><th></th></tr></thead>' +
        '<tbody data-role="body"></tbody></table></div>';
    this.q = function (sel) { return self.container.querySelector(sel); };
    this.container.querySelectorAll('[data-op]').forEach(function (btn) {
        btn.onclick = function () { self.op(btn.getAttribute('data-op')); };
    });
    this.q('[data-role="finished"]').onchange = function () { self.render(); };
    this.q('[data-role="all"]').onclick = function () {
        var on = this.checked;
        self.visible().forEach(function (proc) {
            self.checked[proc.id] = on;
        });
        self.render();
    };
};

GUI.Processes.prototype.refresh = function () {
    var self = this;
    if (this.loading) { return; }
    this.loading = true;
    GUI.get('api/processes').then(function (data) {
        self.loading = false;
        self.data = data.processes || [];
        self.slurm = !!data.slurm;
        self.host = data.host;
        self.render();
    }).catch(function () { self.loading = false; });
};

GUI.Processes.prototype.visible = function () {
    var showFinished = this.q('[data-role="finished"]').checked;
    return this.data.filter(function (proc) {
        return showFinished || GUI.PROC_ACTIVE[proc.status];
    });
};

GUI.Processes.prototype.selected = function () {
    var self = this;
    return this.data.filter(function (proc) {
        return self.checked[proc.id];
    }).map(function (proc) { return proc.id; });
};

GUI.Processes.prototype.render = function () {
    var self = this;
    var body = this.q('[data-role="body"]');
    var rows = this.visible();
    this.q('[data-op="slurm"]').style.display = this.slurm ? '' : 'none';
    var active = this.data.filter(function (p) {
        return GUI.PROC_ACTIVE[p.status]; }).length;
    this.q('[data-role="note"]').textContent = this.data.length +
        ' process(es), ' + active + ' active';
    if (rows.length === 0) {
        body.innerHTML = '<tr><td colspan="9" class="muted">No processes ' +
            'recorded yet.</td></tr>';
        return;
    }
    body.innerHTML = '';
    rows.forEach(function (proc) {
        var tr = document.createElement('tr');
        tr.className = 'clickable';
        var where = proc.slurm_jobs && proc.slurm_jobs.length ?
            'slurm ' + proc.slurm_jobs.join(', ') :
            (proc.host || '') + (proc.pid ? ' pid ' + proc.pid : '');
        var logs = (proc.logs || []).map(function (name, index) {
            return '<button class="small" data-log="' + index + '" title="' +
                GUI.esc(name) + '">' + GUI.esc(name.length > 26 ?
                '...' + name.slice(-24) : name) + '</button>';
        }).join('');
        tr.innerHTML = '<td><input type="checkbox"' +
            (self.checked[proc.id] ? ' checked' : '') + '></td>' +
            '<td><span class="badge ' + GUI.esc(proc.status) + '">' +
            GUI.esc(proc.status) + '</span>' +
            (proc.returncode !== null && proc.returncode !== undefined &&
             proc.returncode !== 0 ? ' <span class="muted small">rc=' +
             GUI.esc(proc.returncode) + '</span>' : '') + '</td>' +
            '<td>' + GUI.esc(proc.kind) + '</td>' +
            '<td class="mono small" style="max-width:520px;word-break:' +
            'break-all">' + GUI.esc(proc.label) + '</td>' +
            '<td class="nowrap small">' + GUI.esc(proc.started || '') +
            '</td><td class="nowrap small">' + GUI.esc(proc.finished || '') +
            '</td><td class="small">' + GUI.esc(where) + '</td>' +
            '<td class="proc-logs">' + (logs || '<span class="muted small">' +
            'none</span>') + '</td><td>' + (GUI.PROC_ACTIVE[proc.status] ?
            '<button class="small danger" data-stop="1">Stop</button>' : '') +
            '</td>';
        tr.querySelector('input').onclick = function (ev) {
            ev.stopPropagation();
            self.checked[proc.id] = this.checked;
        };
        tr.querySelectorAll('[data-log]').forEach(function (btn) {
            btn.onclick = function (ev) {
                ev.stopPropagation();
                self.openLog(proc, Number(btn.getAttribute('data-log')));
            };
        });
        var stopBtn = tr.querySelector('[data-stop]');
        if (stopBtn) {
            stopBtn.onclick = function (ev) {
                ev.stopPropagation();
                self.stop([proc.id]);
            };
        }
        tr.onclick = function () {
            (proc.logs || []).forEach(function (name, index) {
                self.openLog(proc, index);
            });
            if (!(proc.logs || []).length) { GUI.toast('No log files (yet)'); }
        };
        body.appendChild(tr);
    });
};

GUI.Processes.prototype.openLog = function (proc, index) {
    var name = (proc.logs || [])[index] || 'log';
    GUI.openLog('proc:' + proc.id + ':' + index,
                {label: proc.kind + ': ' + name, subtitle: proc.label});
};

GUI.Processes.prototype.stop = function (ids) {
    var self = this;
    if (ids.length === 0) { GUI.toast('Select processes first'); return; }
    GUI.confirm('Stop processes', 'Stop ' + ids.length + ' process(es)? ' +
                'Local processes are terminated (whole process group), ' +
                'Slurm jobs are cancelled.', 'Stop').then(function (ok) {
        if (!ok) { return; }
        self.post('stop', ids);
    });
};

GUI.Processes.prototype.post = function (op, ids) {
    var self = this;
    return GUI.post('api/process', {op: op, ids: ids}).then(function (res) {
        GUI.toast(res.message, res.success ? 'ok' : 'bad');
        self.checked = {};
        self.refresh();
    }).catch(GUI.fail);
};

GUI.Processes.prototype.op = function (op) {
    var self = this;
    if (op === 'refresh') { this.refresh(); return; }
    if (op === 'stop') { this.stop(this.selected()); return; }
    if (op === 'slurm') { this.showSlurm(); return; }
    if (op === 'remove') {
        if (this.selected().length === 0) {
            GUI.toast('Select processes first');
            return;
        }
        this.post('remove', this.selected());
        return;
    }
    if (op === 'clear_finished') { this.post('clear_finished', []); return; }
    if (op === 'clear_all') {
        GUI.confirm('Reset process list', 'Remove every finished process ' +
                    'record and its gui log files? Active processes are ' +
                    'kept.', 'Reset list').then(function (ok) {
            if (ok) { self.post('clear_all', []); }
        });
    }
};

GUI.Processes.prototype.showSlurm = function () {
    GUI.get('api/slurm').then(function (data) {
        var cols = ['job_id', 'name', 'state', 'partition', 'reason',
                    'elapsed', 'time_limit', 'time_left', 'nodes', 'cpus',
                    'memory', 'node_list', 'dependency', 'submit_time'];
        var html = '<p class="muted">' + GUI.esc(data.user) + ': ' +
            (data.jobs || []).length + ' job(s)' +
            (data.error ? ' - ' + GUI.esc(data.error) : '') + '</p>' +
            '<div class="table-wrap"><table><thead><tr>' +
            cols.map(function (c) { return '<th>' + c + '</th>'; }).join('') +
            '</tr></thead><tbody>' + (data.jobs || []).map(function (job) {
                return '<tr>' + cols.map(function (c) {
                    return '<td class="nowrap small">' + GUI.esc(job[c]) +
                        '</td>';
                }).join('') + '</tr>';
            }).join('') + '</tbody></table></div>';
        GUI.dialog({id: 'slurm-dialog', title: 'Slurm jobs', body: html});
    }).catch(GUI.fail);
};
