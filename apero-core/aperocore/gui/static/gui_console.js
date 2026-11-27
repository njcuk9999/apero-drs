/* ==========================================================================
   aperocore gui - job consoles

   GUI.Console(channel, containerId, opts) shows the current/last job of
   one channel (see aperocore.gui.jobs): a header (state badge, title,
   command, stop / hide buttons), the coloured output and - for running
   interactive jobs - an input row so prompts can be answered from the
   browser (plus quick Y / N / Enter buttons).

   The console polls /api/job?channel= (fast while a job runs).
   ========================================================================== */
var GUI = window.GUI || {};
window.GUI = GUI;

// prompt endings that mean the job probably waits for input
GUI.PROMPT_RE = /(\?|:|>>|\]|\)|>)\s*$/;

GUI.Console = function (channel, containerId, opts) {
    this.channel = channel;
    this.container = document.getElementById(containerId);
    this.opts = opts || {};
    this.job = null;
    this.hidden = false;
    this.lastText = null;
    this.loading = false;
    this.wasRunning = false;
    this.build();
    GUI.consoles = GUI.consoles || {};
    GUI.consoles[channel] = this;
    var self = this;
    this.timer = setInterval(function () { self.tick(); }, 1000);
    this.ticks = 0;
    this.refresh();
};

GUI.Console.prototype.build = function () {
    // create the console markup inside the container
    var id = 'console-' + this.channel;
    this.container.classList.add('console-section');
    this.container.innerHTML =
        '<h3>' + GUI.esc(this.opts.title || 'Console') + '</h3>' +
        '<div class="muted small" id="' + id + '-empty">No job has run ' +
        'here yet.</div>' +
        '<div class="job-card" id="' + id + '-card" style="display:none">' +
        '<div class="job-head"><span class="badge" id="' + id +
        '-badge"></span><span class="job-title" id="' + id + '-title">' +
        '</span><span class="job-cmd" id="' + id + '-cmd"></span>' +
        '<button id="' + id + '-copy">Copy command</button>' +
        '<button id="' + id + '-stop">&#9632; Stop</button>' +
        '<button id="' + id + '-toggle">Hide output</button></div>' +
        '<pre class="job-output" id="' + id + '-out"></pre>' +
        '<div class="job-input" id="' + id + '-inrow" style="display:none">' +
        '<span class="job-input-label">Answer:</span>' +
        '<input type="text" id="' + id + '-in" autocomplete="off" ' +
        'spellcheck="false" placeholder="type an answer and press Enter">' +
        '<button id="' + id + '-send">Send</button>' +
        '<button class="quick" data-quick="Y">Y</button>' +
        '<button class="quick" data-quick="N">N</button>' +
        '<button class="quick" data-quick="">&#9166; Enter</button>' +
        '</div></div>';
    var self = this;
    this.el = function (suffix) {
        return document.getElementById(id + '-' + suffix);
    };
    this.el('toggle').onclick = function () {
        self.hidden = !self.hidden;
        self.el('out').style.display = self.hidden ? 'none' : '';
        this.textContent = self.hidden ? 'Show output' : 'Hide output';
    };
    this.el('copy').onclick = function () {
        if (self.job) { GUI.copyText(self.job.label || self.job.cmd, this); }
    };
    this.el('stop').onclick = function () { self.stop(); };
    this.el('send').onclick = function () { self.send(self.el('in').value); };
    this.el('in').onkeydown = function (ev) {
        if (ev.key === 'Enter') { self.send(self.el('in').value); }
    };
    this.container.querySelectorAll('[data-quick]').forEach(function (btn) {
        btn.onclick = function () {
            self.send(btn.getAttribute('data-quick'));
        };
    });
};

GUI.Console.prototype.tick = function () {
    // poll every second while running, every 5 s otherwise
    this.ticks++;
    var running = this.job && this.job.running;
    if (running || this.ticks % 5 === 0) { this.refresh(); }
};

GUI.Console.prototype.refresh = function () {
    var self = this;
    if (this.loading) { return; }
    this.loading = true;
    GUI.get('api/job', {channel: this.channel}).then(function (job) {
        self.loading = false;
        self.render(job);
    }).catch(function () { self.loading = false; });
};

GUI.Console.prototype.render = function (job) {
    this.job = job && job.kind ? job : null;
    if (!this.job) {
        this.el('card').style.display = 'none';
        this.el('empty').style.display = '';
        return;
    }
    this.el('empty').style.display = 'none';
    this.el('card').style.display = '';
    var badge = this.el('badge');
    var state = job.running ? 'running' :
        (job.returncode === 0 ? 'complete' : 'failed');
    badge.className = 'badge ' + state;
    badge.textContent = job.running ? 'running' :
        (job.returncode === 0 ? 'done' : 'exit ' + job.returncode);
    this.el('title').textContent = job.kind + '  ' + (job.started || '');
    // the display text (cli equivalent) of the job, full command on hover
    this.el('cmd').textContent = job.label || job.cmd;
    this.el('cmd').title = job.cmd;
    this.el('stop').style.display = job.running ? '' : 'none';
    // update the output (keep the scroll position unless at the end)
    var out = this.el('out');
    var text = (job.lines || []).join('\n');
    if (text !== this.lastText) {
        var atEnd = out.scrollTop + out.clientHeight >= out.scrollHeight - 30;
        out.innerHTML = GUI.ansiLinesHtml(job.lines);
        if (atEnd || this.lastText === null) {
            out.scrollTop = out.scrollHeight;
        }
        this.lastText = text;
    }
    // the input row for running interactive jobs
    var interactive = job.running && job.interactive;
    this.el('inrow').style.display = interactive ? '' : 'none';
    if (interactive) {
        var lines = job.lines || [];
        var last = lines.length ? lines[lines.length - 1] : '';
        var plain = last.replace(/\x1b\[[0-9;]*m/g, '');
        var waiting = GUI.PROMPT_RE.test(plain);
        this.el('in').classList.toggle('waiting', waiting);
    }
    // notify when a job finishes
    if (this.wasRunning && !job.running && this.opts.onDone) {
        this.opts.onDone(job);
    }
    this.wasRunning = !!job.running;
};

GUI.Console.prototype.send = function (text) {
    var self = this;
    GUI.post('api/job_input', {channel: this.channel, text: text})
        .then(function (res) {
            if (!res.success) { GUI.toast(res.message, 'bad'); return; }
            self.el('in').value = '';
            self.refresh();
            self.el('in').focus();
        }).catch(GUI.fail);
};

GUI.Console.prototype.stop = function () {
    var self = this;
    GUI.confirm('Stop job', 'Stop <b>' + GUI.esc(this.job.kind) +
                '</b> (the whole process group is terminated)?', 'Stop')
        .then(function (ok) {
            if (!ok) { return; }
            GUI.post('api/job_stop', {channel: self.channel})
                .then(function (res) {
                    GUI.toast(res.message, res.success ? 'ok' : 'bad');
                    self.refresh();
                }).catch(GUI.fail);
        });
};

GUI.Console.prototype.focus = function () {
    // scroll the console into view (e.g. after starting a job)
    this.container.scrollIntoView({behavior: 'smooth', block: 'start'});
    var self = this;
    setTimeout(function () { self.refresh(); }, 300);
};

GUI.startJob = function (url, data, consoleObj) {
    // POST a job start request and focus the console that shows it
    return GUI.post(url, data).then(function (res) {
        if (res.started === false || res.success === false) {
            GUI.toast(res.message || res.error, 'bad');
            return res;
        }
        if (res.message) { GUI.toast(res.message, 'ok'); }
        if (consoleObj) { consoleObj.focus(); }
        return res;
    }).catch(GUI.fail);
};
