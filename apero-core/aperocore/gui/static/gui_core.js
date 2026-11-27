/* ==========================================================================
   aperocore gui - core helpers (GUI namespace)

   api requests, html escaping and formatting, theme, top level tabs and
   sub tabs, toasts, dialogs (incl. typed confirmation), ANSI colour
   rendering, copy to clipboard, the /api/state poller (activity logs and
   data-change notifications), runtime info, shutdown and restart.

   Applications configure GUI.config before calling GUI.init().
   ========================================================================== */
var GUI = window.GUI || {};
window.GUI = GUI;

GUI.config = GUI.config || {};
// prefix for localStorage keys (theme, remembered values)
GUI.config.storagePrefix = GUI.config.storagePrefix || 'aperocore-gui';
// request timeout (ms)
GUI.config.timeout = GUI.config.timeout || 30000;
// /api/state poll interval (ms)
GUI.config.statePoll = GUI.config.statePoll || 2000;

// callbacks run when the server says data on disk changed
GUI.dataListeners = [];
// callbacks run when a top level tab is shown: name -> [fn]
GUI.tabListeners = {};
// the current top level tab
GUI.currentTab = null;
// the last /api/state response
GUI.lastState = null;

/* ---- storage ------------------------------------------------------------ */
GUI.store = function (key, value) {
    // remember a value in localStorage (ignored if storage is disabled)
    try {
        localStorage.setItem(GUI.config.storagePrefix + '-' + key,
                             JSON.stringify(value));
    } catch (err) { /* storage disabled */ }
};

GUI.recall = function (key, fallback) {
    // get a remembered value (fallback if missing)
    try {
        var raw = localStorage.getItem(GUI.config.storagePrefix + '-' + key);
        return raw === null ? fallback : JSON.parse(raw);
    } catch (err) { return fallback; }
};

/* ---- formatting --------------------------------------------------------- */
GUI.esc = function (value) {
    // escape text for html
    return String(value === null || value === undefined ? '' : value)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
};

GUI.fmtBytes = function (n) {
    // human readable size
    if (n === null || n === undefined) { return ''; }
    var units = ['B', 'KB', 'MB', 'GB', 'TB'];
    var it = 0;
    while (n >= 1024 && it < units.length - 1) { n /= 1024; it++; }
    return (it === 0 ? n : n.toFixed(n < 10 ? 1 : 0)) + ' ' + units[it];
};

GUI.fmtTime = function (epoch) {
    // local date + time of a unix time stamp (seconds)
    if (!epoch) { return ''; }
    var d = new Date(epoch * 1000);
    var pad = function (v) { return (v < 10 ? '0' : '') + v; };
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' +
           pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' +
           pad(d.getMinutes());
};

GUI.fmtAge = function (epoch) {
    // "5 min ago" style age of a unix time stamp (seconds)
    if (!epoch) { return ''; }
    var sec = Math.max(0, Date.now() / 1000 - epoch);
    if (sec < 60) { return Math.round(sec) + ' s ago'; }
    if (sec < 3600) { return Math.round(sec / 60) + ' min ago'; }
    if (sec < 86400) { return (sec / 3600).toFixed(1) + ' h ago'; }
    return (sec / 86400).toFixed(1) + ' d ago';
};

GUI.basename = function (path) {
    // the last component of a path
    var parts = String(path || '').split('/');
    return parts[parts.length - 1] || path;
};

GUI.dirname = function (path) {
    // the directory of a path
    var text = String(path || '');
    var cut = text.lastIndexOf('/');
    return cut <= 0 ? '/' : text.substring(0, cut);
};

/* ---- api ---------------------------------------------------------------- */
GUI.apiFetch = function (url, options) {
    // fetch json with a timeout; rejects with an Error(message) on failure
    options = options || {};
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); },
                           options.timeout || GUI.config.timeout);
    options.signal = controller.signal;
    options.cache = 'no-store';
    // relative urls keep the gui working behind a proxy path
    var target = url.charAt(0) === '/' ? url.substring(1) : url;
    return fetch(target, options).then(function (resp) {
        clearTimeout(timer);
        return resp.json().catch(function () {
            throw new Error('HTTP ' + resp.status);
        }).then(function (data) {
            if (!resp.ok) {
                throw new Error((data && data.error) || ('HTTP ' +
                                                         resp.status));
            }
            return data;
        });
    }, function (err) {
        clearTimeout(timer);
        if (err.name === 'AbortError') {
            throw new Error('request timed out: ' + url);
        }
        throw err;
    });
};

GUI.get = function (url, params) {
    // GET json (params become the query string)
    if (params) {
        var query = Object.keys(params).filter(function (key) {
            return params[key] !== null && params[key] !== undefined;
        }).map(function (key) {
            return encodeURIComponent(key) + '=' +
                   encodeURIComponent(params[key]);
        }).join('&');
        if (query) { url += (url.indexOf('?') >= 0 ? '&' : '?') + query; }
    }
    return GUI.apiFetch(url);
};

GUI.post = function (url, data, timeout) {
    // POST json
    return GUI.apiFetch(url, {method: 'POST', timeout: timeout,
                              headers: {'Content-Type': 'application/json'},
                              body: JSON.stringify(data || {})});
};

GUI.rawUrl = function (path, extra) {
    // url of the raw bytes of a file (images, downloads)
    return 'api/fs/raw?path=' + encodeURIComponent(path) + (extra || '');
};

/* ---- toasts ------------------------------------------------------------- */
GUI.toast = function (message, kind, ms) {
    // show a short notification (kind: ok / bad / undefined)
    var wrap = document.getElementById('toast-wrap');
    if (!wrap) {
        wrap = document.createElement('div');
        wrap.id = 'toast-wrap';
        wrap.className = 'toast-wrap';
        document.body.appendChild(wrap);
    }
    var item = document.createElement('div');
    item.className = 'toast' + (kind ? ' ' + kind : '');
    item.textContent = message;
    item.onclick = function () { item.remove(); };
    wrap.appendChild(item);
    setTimeout(function () { item.remove(); },
               ms || (kind === 'bad' ? 9000 : 4000));
};

GUI.fail = function (err) {
    // standard error handler for promise chains
    GUI.toast(String((err && err.message) || err), 'bad');
    console.log(err);
};

/* ---- theme -------------------------------------------------------------- */
GUI.applyTheme = function (theme) {
    document.documentElement.setAttribute('data-theme', theme);
    GUI.store('theme', theme);
};

GUI.toggleTheme = function () {
    var now = document.documentElement.getAttribute('data-theme');
    GUI.applyTheme(now === 'dark' ? 'light' : 'dark');
};

/* ---- tabs --------------------------------------------------------------- */
GUI.setTab = function (name) {
    // show one top level tab (buttons #tab-btn-NAME, pages #tab-NAME)
    var pages = document.querySelectorAll('.tabpage');
    if (!document.getElementById('tab-' + name)) { return; }
    pages.forEach(function (page) {
        page.classList.toggle('active', page.id === 'tab-' + name);
    });
    document.querySelectorAll('#tabbar button').forEach(function (btn) {
        btn.classList.toggle('active', btn.id === 'tab-btn-' + name);
    });
    GUI.currentTab = name;
    if (location.hash !== '#' + name) {
        history.replaceState(null, '', '#' + name);
    }
    (GUI.tabListeners[name] || []).forEach(function (fn) { fn(); });
};

GUI.onTab = function (name, fn) {
    // run fn whenever tab "name" is shown
    (GUI.tabListeners[name] = GUI.tabListeners[name] || []).push(fn);
};

GUI.setSubTab = function (group, name) {
    // show one sub tab (buttons #GROUP-btn-NAME, pages #GROUP-NAME)
    document.querySelectorAll('[data-subtab="' + group + '"]')
        .forEach(function (el) {
            el.classList.toggle('active', el.id === group + '-' + name);
        });
    document.querySelectorAll('[data-subtab-btn="' + group + '"]')
        .forEach(function (btn) {
            btn.classList.toggle('active', btn.id === group + '-btn-' + name);
        });
    GUI.store('subtab-' + group, name);
    (GUI.tabListeners[group + ':' + name] || []).forEach(function (fn) {
        fn();
    });
};

/* ---- dialogs ------------------------------------------------------------ */
GUI.dialogStack = [];

GUI.dialog = function (opts) {
    // create (or reuse) a dialog: opts = {id, title, body (html), wide,
    // narrow, buttons: [{label, cls, onclick(close)}], onclose}
    var dlg = document.getElementById(opts.id);
    if (!dlg) {
        dlg = document.createElement('div');
        dlg.id = opts.id;
        dlg.className = 'gui-dialog';
        dlg.innerHTML = '<div class="gui-dialog-panel" role="dialog" ' +
            'aria-modal="true"><div class="gui-dialog-head"><h2></h2>' +
            '<span class="dlg-tools"></span>' +
            '<button class="small" data-close="1">&#10005; Close</button>' +
            '</div><div class="gui-dialog-body"></div>' +
            '<div class="gui-dialog-foot"></div></div>';
        dlg.addEventListener('mousedown', function (ev) {
            if (ev.target === dlg) { GUI.closeDialog(opts.id); }
        });
        dlg.querySelector('[data-close]').onclick = function () {
            GUI.closeDialog(opts.id);
        };
        document.body.appendChild(dlg);
    }
    var panel = dlg.querySelector('.gui-dialog-panel');
    panel.classList.toggle('wide', !!opts.wide);
    panel.classList.toggle('narrow', !!opts.narrow);
    dlg.querySelector('h2').textContent = opts.title || '';
    dlg.querySelector('.dlg-tools').innerHTML = opts.tools || '';
    if (opts.body !== undefined) {
        dlg.querySelector('.gui-dialog-body').innerHTML = opts.body;
    }
    var foot = dlg.querySelector('.gui-dialog-foot');
    foot.innerHTML = '';
    foot.style.display = (opts.buttons && opts.buttons.length) ? '' : 'none';
    (opts.buttons || []).forEach(function (spec) {
        if (spec.grow) {
            var span = document.createElement('span');
            span.className = 'grow muted small';
            span.innerHTML = spec.html || '';
            foot.appendChild(span);
            return;
        }
        var btn = document.createElement('button');
        btn.textContent = spec.label;
        if (spec.cls) { btn.className = spec.cls; }
        if (spec.id) { btn.id = spec.id; }
        btn.onclick = function () {
            if (spec.onclick) {
                spec.onclick(function () { GUI.closeDialog(opts.id); }, btn);
            } else { GUI.closeDialog(opts.id); }
        };
        foot.appendChild(btn);
    });
    dlg.onclose = opts.onclose || null;
    GUI.openDialog(opts.id);
    return dlg;
};

GUI.openDialog = function (id) {
    var dlg = document.getElementById(id);
    if (!dlg) { return; }
    dlg.classList.add('open');
    GUI.dialogStack = GUI.dialogStack.filter(function (d) { return d !== id; });
    GUI.dialogStack.push(id);
};

GUI.closeDialog = function (id) {
    var dlg = document.getElementById(id);
    if (!dlg) { return; }
    dlg.classList.remove('open');
    GUI.dialogStack = GUI.dialogStack.filter(function (d) { return d !== id; });
    if (dlg.onclose) { dlg.onclose(); }
};

GUI.confirmTyped = function (opts) {
    // a confirmation that needs a word typed (e.g. RESET - case does not
    // matter): opts = {title, html, word, label}; resolves true/false
    return new Promise(function (resolve) {
        var word = opts.word || 'RESET';
        var same = function (text) {
            return text.trim().toLowerCase() === word.toLowerCase(); };
        var answered = false;
        var body = '<div>' + (opts.html || '') + '</div>' +
            '<label class="field-label">Type <code>' + GUI.esc(word) +
            '</code> to confirm</label>' +
            '<input type="text" class="confirm-input" id="confirm-typed-in"' +
            ' autocomplete="off" spellcheck="false">';
        var finish = function (value, close) {
            answered = true;
            close();
            resolve(value);
        };
        GUI.dialog({id: 'confirm-typed', title: opts.title || 'Confirm',
                    narrow: true, body: body,
                    onclose: function () { if (!answered) { resolve(false); } },
                    buttons: [
                        {label: 'Cancel', onclick: function (close) {
                            finish(false, close); }},
                        {label: opts.label || 'Confirm', cls: 'danger',
                         id: 'confirm-typed-ok',
                         onclick: function (close) {
                             var input = document.getElementById(
                                 'confirm-typed-in');
                             if (!same(input.value)) {
                                 input.classList.add('bad');
                                 input.focus();
                                 return;
                             }
                             finish(true, close);
                         }}]});
        var input = document.getElementById('confirm-typed-in');
        var okBtn = document.getElementById('confirm-typed-ok');
        okBtn.disabled = true;
        input.oninput = function () {
            input.classList.remove('bad');
            okBtn.disabled = !same(input.value);
        };
        input.onkeydown = function (ev) {
            if (ev.key === 'Enter' && !okBtn.disabled) { okBtn.click(); }
        };
        setTimeout(function () { input.focus(); }, 50);
    });
};

GUI.confirm = function (title, html, label) {
    // a simple yes/no confirmation dialog; resolves true/false
    return new Promise(function (resolve) {
        var answered = false;
        GUI.dialog({id: 'confirm-simple', title: title, narrow: true,
                    body: '<div>' + html + '</div>',
                    onclose: function () { if (!answered) { resolve(false); } },
                    buttons: [
                        {label: 'Cancel', onclick: function (close) {
                            answered = true; close(); resolve(false); }},
                        {label: label || 'OK', cls: 'primary',
                         onclick: function (close) {
                             answered = true; close(); resolve(true); }}]});
    });
};

document.addEventListener('keydown', function (ev) {
    // Esc closes the top dialog (the log viewer handles its own Esc)
    if (ev.key !== 'Escape' || GUI.dialogStack.length === 0) { return; }
    var lightbox = document.getElementById('lightbox');
    if (lightbox && lightbox.classList.contains('open')) { return; }
    GUI.closeDialog(GUI.dialogStack[GUI.dialogStack.length - 1]);
});

/* ---- clipboard ---------------------------------------------------------- */
GUI.copyText = function (text, button) {
    // copy text to the clipboard (with a textarea fallback for http)
    var done = function () {
        if (button) {
            var label = button.textContent;
            button.textContent = 'Copied';
            setTimeout(function () { button.textContent = label; }, 1200);
        } else { GUI.toast('Copied to clipboard', 'ok', 1500); }
    };
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, function () {
            GUI.toast('Could not copy', 'bad');
        });
        return;
    }
    var area = document.createElement('textarea');
    area.value = text;
    document.body.appendChild(area);
    area.select();
    try { document.execCommand('copy'); done(); }
    catch (err) { GUI.toast('Could not copy', 'bad'); }
    area.remove();
};

GUI.copyCli = function (id, button) {
    var el = document.getElementById(id);
    if (el) { GUI.copyText(el.value || el.textContent, button); }
};

GUI.setCli = function (id, text) {
    // fill a cli equivalent box (textarea or code element)
    var el = document.getElementById(id);
    if (!el) { return; }
    if ('value' in el && el.tagName === 'TEXTAREA') { el.value = text; }
    else { el.textContent = text; }
};

GUI.shellQuote = function (value) {
    // quote one shell argument (only when needed)
    var text = String(value);
    if (/^[A-Za-z0-9_\-+=.,/:@%]+$/.test(text)) { return text; }
    return "'" + text.replace(/'/g, "'\\''") + "'";
};

/* ---- ANSI colours ------------------------------------------------------- */
GUI.ansiToHtml = function (text) {
    // convert one line with ANSI SGR colour codes into escaped html spans
    var out = '';
    var open = false;
    var state = {bold: false, fg: null};
    var parts = String(text).split(/\x1b\[([0-9;]*)m/);
    for (var it = 0; it < parts.length; it++) {
        if (it % 2 === 0) {
            if (parts[it]) { out += GUI.esc(parts[it]); }
            continue;
        }
        var codes = parts[it] === '' ? [0] : parts[it].split(';').map(Number);
        codes.forEach(function (code) {
            if (code === 0) { state.bold = false; state.fg = null; }
            else if (code === 1) { state.bold = true; }
            else if (code === 22) { state.bold = false; }
            else if (code >= 30 && code <= 37) { state.fg = code - 30; }
            else if (code >= 90 && code <= 97) { state.fg = code - 82; }
            else if (code === 39) { state.fg = null; }
        });
        if (open) { out += '</span>'; open = false; }
        var cls = [];
        if (state.bold) { cls.push('a-b'); }
        if (state.fg !== null) { cls.push('a-fg' + state.fg); }
        if (cls.length) { out += '<span class="' + cls.join(' ') + '">';
                          open = true; }
    }
    if (open) { out += '</span>'; }
    // strip any other escape sequences (cursor movement etc.)
    return out.replace(/\x1b\[[0-9;?]*[A-Za-z]/g, '');
};

GUI.ansiLinesHtml = function (lines) {
    return (lines || []).map(GUI.ansiToHtml).join('\n');
};

/* ---- state polling ------------------------------------------------------ */
GUI.onDataChange = function (fn) {
    // run fn whenever the server reports changed data (data_version)
    GUI.dataListeners.push(fn);
};

GUI.renderActivity = function (state) {
    // fill every element with data-activity="CHANNEL" (or "all")
    document.querySelectorAll('[data-activity]').forEach(function (el) {
        var channel = el.getAttribute('data-activity');
        var msgs = channel === 'all' ? state.messages :
            (state.activity_messages[channel] || []);
        var text = msgs.slice().reverse().join('\n');
        if (el.textContent !== text) { el.textContent = text; }
    });
};

GUI.refreshState = function () {
    if (GUI.stateLoading) { return Promise.resolve(); }
    GUI.stateLoading = true;
    return GUI.get('api/state').then(function (state) {
        GUI.stateLoading = false;
        var prev = GUI.lastState;
        GUI.lastState = state;
        GUI.renderActivity(state);
        var err = document.getElementById('status-error');
        if (err) { err.textContent = ''; }
        if (prev && prev.data_version !== state.data_version) {
            GUI.dataListeners.forEach(function (fn) { fn(state); });
        }
        if (GUI.onState) { GUI.onState(state, prev); }
    }).catch(function (e) {
        GUI.stateLoading = false;
        var err = document.getElementById('status-error');
        if (err) { err.textContent = 'server: ' + e.message; }
    });
};

/* ---- runtime info / shutdown / restart ---------------------------------- */
GUI.showRuntimeInfo = function () {
    GUI.get('api/runtime_info').then(function (info) {
        var lines = Object.keys(info).map(function (key) {
            var value = info[key];
            if (typeof value === 'object') { value = JSON.stringify(value); }
            return key + ': ' + value;
        });
        GUI.dialog({id: 'runtime-dialog', title: 'GUI runtime information',
                    narrow: true,
                    body: '<p class="muted">Snapshot taken when the gui ' +
                          'worker started.</p><pre class="runtime-pre">' +
                          GUI.esc(lines.join('\n')) + '</pre>'});
    }).catch(GUI.fail);
};

GUI.shutdownServer = function () {
    GUI.confirm('Shutdown GUI', 'Stop the gui server? Jobs started from ' +
                'the gui keep running.', 'Shutdown').then(function (ok) {
        if (!ok) { return; }
        GUI.post('api/shutdown', {}).catch(function () { return null; })
            .then(function () {
                document.body.innerHTML = '<h2 style="padding:30px">GUI ' +
                    'stopped - you can close this tab.</h2>';
            });
    });
};

GUI.restartServer = function () {
    GUI.confirm('Restart server', 'Restart the gui worker? Running jobs ' +
                'are not stopped (their consoles detach - open them from ' +
                'the Processes tab).', 'Restart').then(function (ok) {
        if (!ok) { return; }
        GUI.post('api/shutdown', {restart: true}).catch(function () {
            return null;
        }).then(function () {
            GUI.toast('Restarting...', null, 3000);
            var attempts = 0;
            var wait = function () {
                GUI.get('api/state').then(function () { location.reload(); })
                    .catch(function () {
                        if (++attempts < 60) { setTimeout(wait, 1000); }
                        else { GUI.toast('Server did not come back', 'bad'); }
                    });
            };
            setTimeout(wait, 1500);
        });
    });
};

/* ---- init --------------------------------------------------------------- */
GUI.init = function (defaultTab) {
    // start state polling and open the tab from the url hash
    GUI.applyTheme(GUI.recall('theme', 'dark'));
    var tab = location.hash ? location.hash.substring(1) : defaultTab;
    GUI.setTab(document.getElementById('tab-' + tab) ? tab : defaultTab);
    GUI.refreshState();
    setInterval(GUI.refreshState, GUI.config.statePoll);
    window.addEventListener('hashchange', function () {
        var name = location.hash.substring(1);
        if (name && name !== GUI.currentTab) { GUI.setTab(name); }
    });
};
