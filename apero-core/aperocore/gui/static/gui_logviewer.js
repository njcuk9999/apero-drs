/* ==========================================================================
   aperocore gui - log viewer

   A full screen, tabbed log viewer (always dark). Each tab follows one log
   incrementally (offset based polling, see aperocore.gui.webapp.read_log):
   search with highlights (case / regex / only matching lines), level filter
   (warnings / errors), follow, wrap, pause, next error, copy.

   Tabs are opened with GUI.openLog(id, info). The default url for an id
   "proc:{process id}:{file index}" is /api/process_log; applications can
   set GUI.logUrl = function (tab) {...} for their own log ids.
   ========================================================================== */
var GUI = window.GUI || {};
window.GUI = GUI;

GUI.lv = {tabs: {}, order: [], active: null, open: false, timer: null};
// lines treated as errors / warnings (applications may override)
GUI.config = GUI.config || {};
GUI.LV_ERR_RE = GUI.config.logErrRe ||
    /\|!!\||Traceback \(most recent call last\)|\bERROR\b|\berror:|Exception\b/;
GUI.LV_WARN_RE = GUI.config.logWarnRe || /\|@@\||\bWARNING\b|\bwarning\b/;
// maximum number of lines kept per tab (older lines are dropped)
GUI.LV_MAX_LINES = 200000;

GUI.logUrl = GUI.logUrl || function (tab) {
    // default: process logs "proc:{id}:{file}"
    var parts = tab.id.split(':');
    return 'api/process_log?id=' + encodeURIComponent(parts[1]) +
           '&file=' + (parts[2] || 0) + '&offset=' + tab.offset;
};

GUI.lvEl = function (name) { return document.getElementById('lv-' + name); };

GUI.openLog = function (id, info) {
    // open (or focus) a log tab: info = {label, subtitle, search} - search
    //   (optional) jumps to the first line containing that text
    info = info || {};
    var lv = GUI.lv;
    if (lv.tabs[id] && info.search) {
        lv.tabs[id].pendingSearch = info.search;
    }
    if (!lv.tabs[id]) {
        var body = document.createElement('div');
        body.className = 'lv-body';
        GUI.lvEl('bodies').appendChild(body);
        var tab = {id: id, label: info.label || id,
                   subtitle: info.subtitle || '', body: body, lines: [],
                   offset: -1, state: null, path: '', size: 0, done: false,
                   loading: false, follow: true, partial: '', error: null,
                   truncated: false, pendingSearch: info.search || null};
        body.addEventListener('scroll', function () {
            tab.follow = body.scrollTop + body.clientHeight >=
                         body.scrollHeight - 24;
            GUI.lvUpdateHead();
        });
        lv.tabs[id] = tab;
        lv.order.push(id);
        GUI.lvPoll(tab);
    }
    GUI.lvActivate(id);
    GUI.lvShow();
    GUI.lvApplySearch(lv.tabs[id]);
};

GUI.lvShow = function () {
    var lv = GUI.lv;
    if (lv.order.length === 0) { GUI.toast('No logs open'); return; }
    document.getElementById('logviewer').classList.add('open');
    lv.open = true;
    if (!lv.timer) {
        lv.timer = setInterval(function () {
            if (!lv.open || GUI.lvEl('pause').classList.contains('on')) {
                return;
            }
            lv.order.forEach(function (id) { GUI.lvPoll(lv.tabs[id]); });
        }, 1500);
    }
    GUI.lvUpdateTabs();
};

GUI.lvHide = function () {
    document.getElementById('logviewer').classList.remove('open');
    GUI.lv.open = false;
    GUI.lvUpdateReopen();
};

GUI.lvUpdateReopen = function () {
    var btn = document.getElementById('lv-reopen');
    if (btn) { btn.textContent = 'Logs (' + GUI.lv.order.length + ')'; }
};

GUI.lvPoll = function (tab) {
    if (!tab || tab.loading || tab.done) { return; }
    tab.loading = true;
    GUI.apiFetch(GUI.logUrl(tab)).then(function (data) {
        tab.loading = false;
        if (!GUI.lv.tabs[tab.id]) { return; }
        tab.state = data.state;
        tab.path = data.path;
        tab.size = data.size;
        tab.error = data.error;
        if (data.error) { tab.done = true; GUI.lvRender(tab); return; }
        if (data.reset) { tab.lines = []; tab.partial = ''; }
        if (data.truncated) { tab.truncated = true; }
        if (data.exists) {
            tab.offset = data.offset;
            GUI.lvAppend(tab, data.text);
        }
        var final = data.state !== 'running' && data.offset >= data.size;
        if (final) {
            // flush a last line without a new line
            if (tab.partial) { tab.lines.push(tab.partial); tab.partial = '';
                               GUI.lvRender(tab); }
            tab.done = true;
        }
        if (tab.lines.length === 0) { GUI.lvRender(tab); }
        GUI.lvApplySearch(tab);
        GUI.lvUpdateTabs();
        GUI.lvUpdateHead();
    }).catch(function () { tab.loading = false; });
};

GUI.lvAppend = function (tab, text) {
    if (!text) { return; }
    var chunks = (tab.partial + text).replace(/\r\n/g, '\n')
        .replace(/\r/g, '\n').split('\n');
    tab.partial = chunks.pop();
    if (chunks.length === 0) { return; }
    tab.lines = tab.lines.concat(chunks);
    if (tab.lines.length > GUI.LV_MAX_LINES) {
        tab.lines = tab.lines.slice(tab.lines.length - GUI.LV_MAX_LINES);
        tab.truncated = true;
    }
    GUI.lvRender(tab);
};

GUI.lvMatcher = function () {
    // the current search as a RegExp (null = no search)
    var text = GUI.lvEl('search').value;
    var input = GUI.lvEl('search');
    input.classList.remove('bad');
    if (!text) { return null; }
    var flags = GUI.lvEl('case').checked ? 'g' : 'gi';
    try {
        var src = GUI.lvEl('regex').checked ? text :
            text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return new RegExp(src, flags);
    } catch (err) { input.classList.add('bad'); return null; }
};

GUI.lvRender = function (tab) {
    // re-render the visible lines of a tab (search, filter, highlight)
    var body = tab.body;
    if (tab.lines.length === 0) {
        var msg = tab.error ? 'Error: ' + tab.error :
            (tab.state === null ? 'Loading...' : 'No output (yet).');
        body.innerHTML = '<div class="lv-empty">' + GUI.esc(msg) + '</div>';
        return;
    }
    var matcher = GUI.lvMatcher();
    var only = GUI.lvEl('only').checked;
    var level = GUI.lvEl('level').value;
    var html = [];
    var nmatch = 0;
    for (var it = 0; it < tab.lines.length; it++) {
        var raw = tab.lines[it];
        var plain = raw.replace(/\x1b\[[0-9;?]*[A-Za-z]/g, '');
        var isErr = GUI.LV_ERR_RE.test(plain);
        var isWarn = !isErr && GUI.LV_WARN_RE.test(plain);
        if (level === 'err' && !isErr) { continue; }
        if (level === 'warn' && !isErr && !isWarn) { continue; }
        var lineHtml;
        if (matcher) {
            matcher.lastIndex = 0;
            var found = matcher.test(plain);
            if (only && !found) { continue; }
            if (found) {
                nmatch++;
                lineHtml = GUI.lvHighlight(plain, matcher);
            } else { lineHtml = GUI.ansiToHtml(raw); }
        } else { lineHtml = GUI.ansiToHtml(raw); }
        html.push('<div class="lv-line' + (isErr ? ' err' : '') +
                  (isWarn ? ' warn' : '') + '"><span class="lv-ln" ' +
                  'data-n="' + (it + 1) + '"></span>' + lineHtml + '</div>');
    }
    body.innerHTML = html.join('');
    tab.nmatch = nmatch;
    tab.cur = -1;
    if (tab.follow) { body.scrollTop = body.scrollHeight; }
    if (tab.id === GUI.lv.active) { GUI.lvUpdateHead(); }
};

GUI.lvHighlight = function (plain, matcher) {
    // escape a line and wrap every match in <mark> (match ranges are found
    // on the plain text so the html escaping never breaks a match)
    var parts = [];
    var last = 0;
    var match;
    matcher.lastIndex = 0;
    while ((match = matcher.exec(plain)) !== null) {
        if (match[0] === '') { matcher.lastIndex++; continue; }
        parts.push(GUI.esc(plain.slice(last, match.index)));
        parts.push('<mark>' + GUI.esc(match[0]) + '</mark>');
        last = match.index + match[0].length;
    }
    parts.push(GUI.esc(plain.slice(last)));
    return parts.join('');
};

GUI.lvRenderAll = function () {
    GUI.lv.order.forEach(function (id) { GUI.lvRender(GUI.lv.tabs[id]); });
};

GUI.lvApplySearch = function (tab) {
    // jump to a requested search text once the log has content
    if (!tab.pendingSearch || tab.lines.length === 0 ||
        tab.id !== GUI.lv.active) { return; }
    var text = tab.pendingSearch;
    tab.pendingSearch = null;
    GUI.lvEl('search').value = text;
    GUI.lvEl('regex').checked = false;
    tab.follow = false;
    GUI.lvRender(tab);
    GUI.lvStep(1);
};

GUI.lvActivate = function (id) {
    var lv = GUI.lv;
    lv.active = id;
    lv.order.forEach(function (other) {
        lv.tabs[other].body.classList.toggle('active', other === id);
    });
    GUI.lvUpdateTabs();
    GUI.lvUpdateHead();
};

GUI.lvUpdateTabs = function () {
    var lv = GUI.lv;
    var holder = GUI.lvEl('tabs');
    holder.innerHTML = '';
    lv.order.forEach(function (id) {
        var tab = lv.tabs[id];
        var el = document.createElement('div');
        el.className = 'lv-tab' + (id === lv.active ? ' active' : '');
        el.title = tab.path || tab.label;
        el.innerHTML = '<span class="lv-dot ' + GUI.esc(tab.state || '') +
            '"></span>' + GUI.esc(tab.label) +
            '<span class="lv-x" title="Close">&#10005;</span>';
        el.onclick = function (ev) {
            if (ev.target.classList.contains('lv-x')) { GUI.lvClose(id); }
            else { GUI.lvActivate(id); }
        };
        holder.appendChild(el);
    });
    GUI.lvUpdateReopen();
};

GUI.lvUpdateHead = function () {
    var tab = GUI.lv.tabs[GUI.lv.active];
    if (!tab) { return; }
    var state = GUI.lvEl('state');
    state.className = 'lv-state ' + (tab.state || '');
    state.textContent = tab.state || '...';
    GUI.lvEl('meta').textContent = tab.path + '  (' + GUI.fmtBytes(tab.size) +
        ')';
    GUI.lvEl('count').textContent = GUI.lvMatcher() ?
        (tab.nmatch || 0) + ' match(es)' : '';
    GUI.lvEl('follow').classList.toggle('on', tab.follow);
    GUI.lvEl('status').textContent = tab.lines.length + ' lines' +
        (tab.truncated ? ' (start truncated)' : '') +
        (tab.done ? '' : '  - live') + (tab.subtitle ? '  |  ' +
                                         tab.subtitle : '');
};

GUI.lvClose = function (id) {
    var lv = GUI.lv;
    var tab = lv.tabs[id];
    if (!tab) { return; }
    tab.body.remove();
    delete lv.tabs[id];
    lv.order = lv.order.filter(function (other) { return other !== id; });
    if (lv.active === id) { lv.active = lv.order[lv.order.length - 1] || null; }
    if (lv.order.length === 0) { GUI.lvHide(); }
    else { GUI.lvActivate(lv.active); }
    GUI.lvUpdateReopen();
};

GUI.lvCloseAll = function () {
    GUI.lv.order.slice().forEach(GUI.lvClose);
};

GUI.lvStep = function (dir) {
    // jump to the next / previous search match
    var tab = GUI.lv.tabs[GUI.lv.active];
    if (!tab) { return; }
    var marks = tab.body.querySelectorAll('mark');
    if (marks.length === 0) { return; }
    if (tab.cur >= 0 && marks[tab.cur]) {
        marks[tab.cur].classList.remove('cur');
    }
    tab.cur = (tab.cur + dir + marks.length) % marks.length;
    marks[tab.cur].classList.add('cur');
    marks[tab.cur].scrollIntoView({block: 'center'});
    tab.follow = false;
    GUI.lvEl('count').textContent = (tab.cur + 1) + ' / ' + marks.length;
};

GUI.lvNextError = function () {
    var tab = GUI.lv.tabs[GUI.lv.active];
    if (!tab) { return; }
    var errs = tab.body.querySelectorAll('.lv-line.err');
    if (errs.length === 0) { GUI.toast('No errors found'); return; }
    var top = tab.body.scrollTop + 10;
    var target = errs[0];
    for (var it = 0; it < errs.length; it++) {
        if (errs[it].offsetTop > top) { target = errs[it]; break; }
    }
    tab.follow = false;
    tab.body.scrollTop = target.offsetTop - 40;
};

GUI.lvScrollEnd = function (bottom) {
    var tab = GUI.lv.tabs[GUI.lv.active];
    if (!tab) { return; }
    tab.body.scrollTop = bottom ? tab.body.scrollHeight : 0;
    tab.follow = bottom;
    GUI.lvUpdateHead();
};

GUI.lvToggle = function (name) {
    var btn = GUI.lvEl(name);
    btn.classList.toggle('on');
    if (name === 'wrap') {
        GUI.lvEl('bodies').classList.toggle('wrap', btn.classList.contains('on'));
    }
    if (name === 'follow') {
        var tab = GUI.lv.tabs[GUI.lv.active];
        if (tab) { tab.follow = btn.classList.contains('on');
                   if (tab.follow) { GUI.lvScrollEnd(true); } }
    }
};

GUI.lvCopyVisible = function () {
    var tab = GUI.lv.tabs[GUI.lv.active];
    if (!tab) { return; }
    var lines = [];
    tab.body.querySelectorAll('.lv-line').forEach(function (line) {
        lines.push(line.textContent);
    });
    GUI.copyText(lines.join('\n'));
};

GUI.lvCopyPath = function () {
    var tab = GUI.lv.tabs[GUI.lv.active];
    if (tab) { GUI.copyText(tab.path); }
};

document.addEventListener('DOMContentLoaded', function () {
    var search = GUI.lvEl('search');
    if (!search) { return; }
    var timer = null;
    var rerender = function () {
        clearTimeout(timer);
        timer = setTimeout(GUI.lvRenderAll, 200);
    };
    search.addEventListener('input', rerender);
    search.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter') { GUI.lvStep(ev.shiftKey ? -1 : 1); }
    });
    ['case', 'regex', 'only', 'level'].forEach(function (name) {
        GUI.lvEl(name).addEventListener('change', GUI.lvRenderAll);
    });
    document.addEventListener('keydown', function (ev) {
        if (!GUI.lv.open) { return; }
        if (ev.key === 'Escape') { GUI.lvHide(); }
        if ((ev.ctrlKey || ev.metaKey) && ev.key === 'f') {
            ev.preventDefault();
            search.focus();
            search.select();
        }
    });
});
