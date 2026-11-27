/* ==========================================================================
   aperocore gui - file picker and viewers

   GUI.pickFile(opts)      open-file dialog (server side directories);
                           resolves the chosen path (or null)
   GUI.viewFile(path)      open the right viewer for a file:
                             FITS  -> HDU list, header (searchable), image
                                      preview (scale / colour map / plane),
                                      table rows
                             image -> lightbox
                             text  -> text viewer
   GUI.lightbox(items, i)  full screen image viewer with next / previous
                           (items with a pickled figure: matplotlib's toolbar, GUI.mpl)
                           (arrow keys), zoom and download
   ========================================================================== */
var GUI = window.GUI || {};
window.GUI = GUI;

GUI.FILE_ICONS = {dir: '&#128193;', image: '&#128444;', fits: '&#128301;',
                  text: '&#128196;', other: '&#128462;'};

/* ---- file picker -------------------------------------------------------- */
GUI.pickFile = function (opts) {
    // opts = {title, start, ext: ['.yaml'], any: bool (any directory),
    //         dirs: bool (choose a directory)}
    opts = opts || {};
    return new Promise(function (resolve) {
        var chosen = null;
        var answered = false;
        var current = null;
        var body = '<div class="fb-path"><input type="text" id="fb-path-in" ' +
            'placeholder="directory or file path" spellcheck="false">' +
            '<button id="fb-go">Go</button><button id="fb-up">&#8593; Up' +
            '</button><button id="fb-home">Home</button></div>' +
            '<div class="fb-crumbs" id="fb-crumbs"></div>' +
            '<div class="fb-list"><table><tbody id="fb-body"></tbody></table>' +
            '</div><div class="muted small" id="fb-note" ' +
            'style="margin-top:6px"></div>';
        var finish = function (value, close) {
            answered = true;
            close();
            resolve(value);
        };
        GUI.dialog({id: 'file-picker', title: opts.title || 'Choose a file',
                    body: body,
                    onclose: function () { if (!answered) { resolve(null); } },
                    buttons: [{grow: true, html: opts.ext ? 'Showing: ' +
                               GUI.esc(opts.ext.join(', ')) : ''},
                              {label: 'Cancel', onclick: function (close) {
                                  finish(null, close); }},
                              {label: opts.dirs ? 'Choose this directory' :
                               'Open', cls: 'primary', id: 'fb-ok',
                               onclick: function (close) {
                                   var value = opts.dirs ? current : chosen;
                                   if (!value) {
                                       GUI.toast('Choose a file first');
                                       return;
                                   }
                                   finish(value, close);
                               }}]});
        var load = function (path) {
            var params = {path: path || '', any: opts.any ? 1 : 0,
                          ext: (opts.ext || []).join(',')};
            GUI.get('api/fs/list', params).then(function (data) {
                current = data.path;
                document.getElementById('fb-path-in').value = data.path;
                var crumbs = data.path.split('/').filter(Boolean);
                var html = '<a data-p="/">/</a>';
                var acc = '';
                crumbs.forEach(function (part) {
                    acc += '/' + part;
                    html += '<a data-p="' + GUI.esc(acc) + '">' +
                        GUI.esc(part) + '</a>/';
                });
                var crumbEl = document.getElementById('fb-crumbs');
                crumbEl.innerHTML = html;
                crumbEl.querySelectorAll('a').forEach(function (a) {
                    a.onclick = function () { load(a.getAttribute('data-p')); };
                });
                document.getElementById('fb-up').disabled = !data.parent;
                document.getElementById('fb-up').onclick = function () {
                    load(data.parent);
                };
                var tbody = document.getElementById('fb-body');
                tbody.innerHTML = '';
                data.entries.forEach(function (ent) {
                    if (opts.dirs && ent.kind !== 'dir') { return; }
                    var tr = document.createElement('tr');
                    tr.className = 'clickable';
                    tr.innerHTML = '<td class="fb-icon">' +
                        GUI.FILE_ICONS[ent.kind] + '</td><td class="fb-name">' +
                        GUI.esc(ent.name) + '</td><td class="num small muted">' +
                        GUI.fmtBytes(ent.size) + '</td><td class="small ' +
                        'muted nowrap">' + GUI.fmtTime(ent.mtime) + '</td>';
                    tr.onclick = function () {
                        if (ent.kind === 'dir') { load(ent.path); return; }
                        chosen = ent.path;
                        tbody.querySelectorAll('tr').forEach(function (row) {
                            row.classList.remove('chosen');
                        });
                        tr.classList.add('chosen');
                    };
                    tr.ondblclick = function () {
                        if (ent.kind !== 'dir') {
                            chosen = ent.path;
                            document.getElementById('fb-ok').click();
                        }
                    };
                    tbody.appendChild(tr);
                });
                document.getElementById('fb-note').textContent =
                    data.entries.length + ' item(s)' +
                    (data.truncated ? ' (truncated)' : '') +
                    (data.error ? ' - ' + data.error : '');
            }).catch(GUI.fail);
        };
        document.getElementById('fb-go').onclick = function () {
            load(document.getElementById('fb-path-in').value);
        };
        document.getElementById('fb-path-in').onkeydown = function (ev) {
            if (ev.key === 'Enter') { document.getElementById('fb-go').click(); }
        };
        document.getElementById('fb-home').onclick = function () {
            GUI.get('api/fs/roots').then(function (data) {
                load(opts.any ? data.home : (data.roots[0] || data.home));
            });
        };
        load(opts.start || '');
    });
};

/* ---- viewers ------------------------------------------------------------ */
GUI.fileKind = function (path) {
    var lower = String(path).toLowerCase();
    if (/\.(png|jpe?g|gif|svg|webp)$/.test(lower)) { return 'image'; }
    if (/\.(fits|fit|fts)(\.gz)?$/.test(lower)) { return 'fits'; }
    return 'text';
};

GUI.viewFile = function (path, opts) {
    var kind = GUI.fileKind(path);
    if (kind === 'image') {
        GUI.lightbox([{path: path, name: GUI.basename(path)}], 0);
    } else if (kind === 'fits') {
        GUI.viewFits(path);
    } else {
        GUI.viewText(path, opts);
    }
};

GUI.viewText = function (path, opts) {
    opts = opts || {};
    GUI.get('api/fs/text', {path: path, any: opts.any ? 1 : 0})
        .then(function (data) {
            var body = data.error ? '<div class="notice bad">' +
                GUI.esc(data.error) + '</div>' :
                '<pre class="text-view">' + GUI.esc(data.text) + '</pre>' +
                (data.truncated ? '<p class="muted">(truncated)</p>' : '');
            GUI.dialog({id: 'text-viewer', title: path, wide: false,
                        body: body,
                        tools: '<button class="small" onclick="GUI.copyText(' +
                               GUI.esc(JSON.stringify(path)) + ')">Copy path' +
                               '</button>'});
        }).catch(GUI.fail);
};

GUI.viewFits = function (path) {
    GUI.get('api/fits/info', {path: path}).then(function (info) {
        if (info.error) { GUI.toast(info.error, 'bad'); return; }
        var hdus = info.hdus.map(function (hdu) {
            var meta = hdu.type.replace('HDU', '') + (hdu.shape ?
                ' [' + hdu.shape.join(' x ') + ']' : '');
            return '<div class="fv-hdu" data-hdu="' + hdu.index + '">' +
                '<div class="hdu-name">' + hdu.index + ': ' +
                GUI.esc(hdu.name) + '</div><div class="hdu-meta">' +
                GUI.esc(meta) + '</div></div>';
        }).join('');
        var body = '<div class="fv-layout"><div class="fv-hdus">' + hdus +
            '</div><div class="fv-main"><div class="controltabbar">' +
            '<button data-fv="header" class="active">Header</button>' +
            '<button data-fv="image">Image</button>' +
            '<button data-fv="table">Table</button>' +
            '<span style="flex:1"></span><input type="search" id="fv-filter" ' +
            'placeholder="Filter header keys / values"></div>' +
            '<div id="fv-content"></div></div></div>';
        GUI.dialog({id: 'fits-viewer', title: path, wide: true, body: body,
                    tools: '<a class="small" href="' + GUI.rawUrl(path,
                           '&download=1') + '">Download</a>'});
        var state = {hdu: 0, view: 'header', plane: 0, scale: 'zscale',
                     cmap: 'gray', tstart: 0};
        // start on the first HDU with data
        for (var it = 0; it < info.hdus.length; it++) {
            if (info.hdus[it].image || info.hdus[it].table) {
                state.hdu = it; break;
            }
        }
        var dlg = document.getElementById('fits-viewer');
        var render = function () {
            var hdu = info.hdus[state.hdu];
            dlg.querySelectorAll('.fv-hdu').forEach(function (el) {
                el.classList.toggle('active',
                    Number(el.getAttribute('data-hdu')) === state.hdu);
            });
            dlg.querySelectorAll('[data-fv]').forEach(function (btn) {
                var view = btn.getAttribute('data-fv');
                btn.classList.toggle('active', view === state.view);
                btn.disabled = (view === 'image' && !hdu.image) ||
                    (view === 'table' && !hdu.table);
            });
            var content = document.getElementById('fv-content');
            document.getElementById('fv-filter').style.display =
                state.view === 'header' ? '' : 'none';
            if (state.view === 'header') {
                var filter = document.getElementById('fv-filter').value
                    .toLowerCase();
                content.innerHTML = '<table class="fv-header"><tbody>' +
                    hdu.header.filter(function (card) {
                        return !filter || (card[0] + ' ' + card[1] + ' ' +
                            card[2]).toLowerCase().indexOf(filter) >= 0;
                    }).map(function (card) {
                        return '<tr><td class="k">' + GUI.esc(card[0]) +
                            '</td><td>' + GUI.esc(card[1]) + '</td>' +
                            '<td class="c">' + GUI.esc(card[2]) + '</td></tr>';
                    }).join('') + '</tbody></table>';
            } else if (state.view === 'image') {
                var nplanes = 1;
                if (hdu.shape && hdu.shape.length > 2) {
                    nplanes = hdu.shape.slice(0, -2).reduce(function (a, b) {
                        return a * b; }, 1);
                }
                var src = 'api/fits/image?path=' + encodeURIComponent(path) +
                    '&hdu=' + state.hdu + '&plane=' + state.plane +
                    '&scale=' + state.scale + '&cmap=' + state.cmap;
                content.innerHTML = '<div class="field-row" style="margin:' +
                    '0 0 8px 0"><label class="inline">Scale <select ' +
                    'id="fv-scale">' + ['zscale', 'p99', 'p95', 'minmax',
                    'log'].map(function (s) {
                        return '<option' + (s === state.scale ? ' selected' :
                            '') + '>' + s + '</option>'; }).join('') +
                    '</select></label><label class="inline">Colour map ' +
                    '<select id="fv-cmap">' + ['gray', 'viridis', 'magma',
                    'inferno', 'plasma', 'cividis'].map(function (c) {
                        return '<option' + (c === state.cmap ? ' selected' :
                            '') + '>' + c + '</option>'; }).join('') +
                    '</select></label>' + (nplanes > 1 ? '<label ' +
                    'class="inline">Plane <input type="number" min="1" max="' +
                    nplanes + '" value="' + (state.plane + 1) + '" id="fv-plane"' +
                    ' style="width:80px"> / ' + nplanes + '</label>' : '') +
                    '<span class="muted small" id="fv-img-note">loading...' +
                    '</span></div><img class="fv-image" id="fv-img" alt="">';
                var img = document.getElementById('fv-img');
                img.onload = function () {
                    document.getElementById('fv-img-note').textContent = '';
                };
                img.onerror = function () {
                    GUI.get(src).catch(function (err) {
                        document.getElementById('fv-img-note').textContent =
                            err.message;
                    });
                };
                img.src = src;
                document.getElementById('fv-scale').onchange = function () {
                    state.scale = this.value; render(); };
                document.getElementById('fv-cmap').onchange = function () {
                    state.cmap = this.value; render(); };
                var plane = document.getElementById('fv-plane');
                if (plane) { plane.onchange = function () {
                    state.plane = Math.max(0, Number(this.value) - 1);
                    render(); }; }
            } else {
                content.innerHTML = '<p class="muted">loading...</p>';
                GUI.get('api/fits/table', {path: path, hdu: state.hdu,
                                           start: state.tstart, rows: 100})
                    .then(function (data) {
                        var end = data.start + data.rows.length;
                        content.innerHTML = '<div class="field-row" ' +
                            'style="margin-bottom:8px"><button id="fv-prev">' +
                            '&laquo; Prev</button><span class="muted">rows ' +
                            (data.start + 1) + '-' + end + ' of ' +
                            data.total + '</span><button id="fv-next">Next ' +
                            '&raquo;</button></div><div class="table-wrap">' +
                            '<table><thead><tr><th>#</th>' +
                            data.columns.map(function (c) {
                                return '<th>' + GUI.esc(c) + '</th>';
                            }).join('') + '</tr></thead><tbody>' +
                            data.rows.map(function (row, it) {
                                return '<tr><td class="muted">' +
                                    (data.start + it + 1) + '</td>' +
                                    row.map(function (v) {
                                        return '<td class="mono small nowrap">' +
                                            GUI.esc(v) + '</td>';
                                    }).join('') + '</tr>';
                            }).join('') + '</tbody></table></div>';
                        document.getElementById('fv-prev').disabled =
                            data.start === 0;
                        document.getElementById('fv-next').disabled =
                            end >= data.total;
                        document.getElementById('fv-prev').onclick =
                            function () { state.tstart = Math.max(0,
                                data.start - 100); render(); };
                        document.getElementById('fv-next').onclick =
                            function () { state.tstart = end; render(); };
                    }).catch(function (err) {
                        content.innerHTML = '<div class="notice bad">' +
                            GUI.esc(err.message) + '</div>';
                    });
            }
        };
        dlg.querySelectorAll('.fv-hdu').forEach(function (el) {
            el.onclick = function () {
                state.hdu = Number(el.getAttribute('data-hdu'));
                state.plane = 0;
                state.tstart = 0;
                var hdu = info.hdus[state.hdu];
                if (state.view === 'image' && !hdu.image) {
                    state.view = 'header'; }
                if (state.view === 'table' && !hdu.table) {
                    state.view = 'header'; }
                render();
            };
        });
        dlg.querySelectorAll('[data-fv]').forEach(function (btn) {
            btn.onclick = function () {
                state.view = btn.getAttribute('data-fv');
                render();
            };
        });
        document.getElementById('fv-filter').oninput = render;
        render();
    }).catch(GUI.fail);
};

/* ---- lightbox ----------------------------------------------------------- */
GUI.lb = {items: [], index: 0};

GUI.lightbox = function (items, index) {
    // items = [{path, name, info, title, description, details, figure}] -
    //   title / description / details (list of [label, text]) fill the
    //   side panel; figure = a pickled matplotlib figure (.mplfig) makes
    //   the image interactive (matplotlib's toolbar, see GUI.mpl)
    GUI.lb.items = items;
    GUI.lb.index = index || 0;
    document.getElementById('lightbox').classList.add('open');
    GUI.lbShow();
};

GUI.lbShow = function () {
    var lb = GUI.lb;
    var item = lb.items[lb.index];
    if (!item) { return; }
    var img = document.getElementById('lb-img');
    img.classList.remove('zoom');
    document.getElementById('lb-body').classList.remove('zoomed');
    img.src = GUI.rawUrl(item.path);
    document.getElementById('lb-title').textContent = item.path;
    document.getElementById('lb-foot').textContent = (lb.index + 1) + ' / ' +
        lb.items.length + (item.info ? '   |   ' + item.info : '') +
        '   (arrow keys: previous / next, click: zoom, Esc: close)';
    document.getElementById('lb-download').href = GUI.rawUrl(item.path,
                                                             '&download=1');
    // the description panel (only when the item is described)
    var desc = document.getElementById('lb-desc');
    var details = item.details || [];
    var described = !!(item.title || item.description || details.length);
    document.getElementById('lightbox').classList.toggle('has-desc',
                                                         described);
    desc.innerHTML = described ? (item.title ? '<h3>' +
        GUI.esc(item.title) + '</h3>' : '') + '<div class="lb-desc-text">' +
        (item.description ? GUI.esc(item.description) : '<span ' +
         'class="lb-desc-none">No description saved for this plot.</span>') +
        '</div>' + (details.length ? '<dl>' + details.map(function (pair) {
            return '<dt>' + GUI.esc(pair[0]) + '</dt><dd>' +
                GUI.esc(pair[1]) + '</dd>';
        }).join('') + '</dl>' : '') : '';
    document.querySelectorAll('.lb-nav').forEach(function (btn) {
        btn.style.display = lb.items.length > 1 ? '' : 'none';
    });
    // the static png shows until matplotlib's figure is ready
    GUI.mpl.open(item);
};

GUI.lbStep = function (dir) {
    var lb = GUI.lb;
    if (lb.items.length === 0) { return; }
    lb.index = (lb.index + dir + lb.items.length) % lb.items.length;
    GUI.lbShow();
};

GUI.lbClose = function () {
    document.getElementById('lightbox').classList.remove('open');
    GUI.mpl.close();
};

GUI.lbZoom = function () {
    // interactive figures zoom with matplotlib's toolbar instead
    if (GUI.mpl.session) { return; }
    var img = document.getElementById('lb-img');
    img.classList.toggle('zoom');
    document.getElementById('lb-body').classList.toggle('zoomed',
        img.classList.contains('zoom'));
};

document.addEventListener('keydown', function (ev) {
    var box = document.getElementById('lightbox');
    if (!box || !box.classList.contains('open')) { return; }
    if (ev.key === 'Escape') { GUI.lbClose(); }
    // inside an interactive figure the keys are matplotlib's (e.g. the
    //   arrow keys are back / forward, g grid, l / k log scales)
    var holder = document.getElementById('lb-mpl');
    if (holder && holder.contains(ev.target)) { return; }
    if (ev.key === 'ArrowRight') { GUI.lbStep(1); }
    if (ev.key === 'ArrowLeft') { GUI.lbStep(-1); }
});

/* ---- interactive figures (matplotlib's own toolbar) --------------------- */
// a pickled figure runs in matplotlib's browser backend on the server and
//   is shown with matplotlib's mpl.js (zoom / pan / home / back /
//   forward, shared axes, coordinates, key shortcuts). mpl.js expects a
//   websocket: GUI.mpl.socket posts its messages (api/figure/send) and
//   long-polls matplotlib's replies (api/figure/poll)
GUI.mpl = {session: null, fig: null, token: 0, loading: null};

GUI.mpl.load = function () {
    // load matplotlib's css / mpl.js once
    if (window.mpl && window.mpl.figure) { return Promise.resolve(); }
    if (GUI.mpl.loading) { return GUI.mpl.loading; }
    var css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'api/figure/mpl.css';
    document.head.appendChild(css);
    GUI.mpl.loading = new Promise(function (resolve, reject) {
        var script = document.createElement('script');
        script.src = 'api/figure/mpl.js';
        script.onload = function () { resolve(); };
        script.onerror = function () {
            GUI.mpl.loading = null;
            reject(new Error('cannot load matplotlib (mpl.js)'));
        };
        document.head.appendChild(script);
    });
    return GUI.mpl.loading;
};

GUI.mpl.socket = function (sid, token) {
    // a websocket-like object for mpl.js over http
    var ws = {readyState: 1, outbox: [], sending: false};
    var alive = function () { return token === GUI.mpl.token; };
    ws.flush = function () {
        if (ws.sending || ws.outbox.length === 0 || !alive()) { return; }
        ws.sending = true;
        var messages = ws.outbox;
        ws.outbox = [];
        GUI.post('api/figure/send', {id: sid, messages: messages})
            .catch(function () { return null; })
            .then(function () { ws.sending = false; ws.flush(); });
    };
    ws.send = function (message) {
        // only the latest of consecutive mouse moves matters
        var last = ws.outbox[ws.outbox.length - 1];
        var move = '"type":"motion_notify"';
        if (last && last.indexOf(move) >= 0 && message.indexOf(move) >= 0) {
            ws.outbox[ws.outbox.length - 1] = message;
        } else {
            ws.outbox.push(message);
        }
        ws.flush();
    };
    ws.close = function () { ws.readyState = 3; };
    ws.poll = function () {
        if (!alive()) { return; }
        GUI.apiFetch('api/figure/poll?id=' + encodeURIComponent(sid) +
                     '&wait=10', {timeout: 25000}).then(function (data) {
            if (!alive()) { return; }
            data.messages.forEach(function (message) {
                ws.onmessage({data: message});
            });
            // after matplotlib's first messages (its initial size)
            if (ws.onfirst && data.messages.length) {
                var first = ws.onfirst;
                ws.onfirst = null;
                first();
            }
            ws.poll();
        }).catch(function (err) {
            if (!alive()) { return; }
            if (String(err.message).indexOf('closed') >= 0) {
                ws.readyState = 3;
                GUI.toast('Figure closed - reopen it to interact', 'bad');
                return;
            }
            setTimeout(ws.poll, 1000);
        });
    };
    return ws;
};

GUI.mpl.open = function (item) {
    // show a lightbox item with matplotlib's toolbar (item.figure)
    var mplx = GUI.mpl;
    mplx.close();
    if (!item || !item.figure) { return; }
    var token = mplx.token;
    var box = document.getElementById('lightbox');
    mplx.load().then(function () {
        return GUI.post('api/figure/open', {path: item.figure}, 60000);
    }).then(function (data) {
        if (token !== mplx.token) {
            GUI.post('api/figure/close', {id: data.id});
            return;
        }
        mplx.session = data.id;
        var holder = document.getElementById('lb-mpl');
        holder.innerHTML = '';
        var ws = mplx.socket(data.id, token);
        var ondownload = function (figure) {
            var link = document.createElement('a');
            link.href = figure.canvas.toDataURL();
            link.download = (item.name || 'figure').replace(/\.png$/, '') +
                '-view.png';
            link.click();
        };
        var fig = new window.mpl.figure(data.id, ws, ondownload, holder);
        mplx.fig = fig;
        box.classList.add('interactive');
        ws.onopen();
        // fill the space available (like maximising a plot window): mpl.js
        //   asks matplotlib for the new size when its canvas div resizes
        ws.onfirst = function () {
            var body = document.getElementById('lb-body');
            var width = Math.floor(body.clientWidth * 0.94);
            var height = Math.floor(body.clientHeight * 0.94) - 60;
            if (fig.canvas_div && width > 200 && height > 150) {
                fig.canvas_div.style.width = width + 'px';
                fig.canvas_div.style.height = height + 'px';
            }
        };
        ws.poll();
        setTimeout(function () {
            if (fig.canvas_div) { fig.canvas_div.focus(); }
        }, 50);
    }).catch(function (err) {
        if (token !== mplx.token) { return; }
        // keep the static png
        GUI.toast('Interactive figure not available: ' + err.message,
                  'bad');
    });
};

GUI.mpl.close = function () {
    // stop the current interactive figure (back to the static png)
    var mplx = GUI.mpl;
    mplx.token += 1;
    if (mplx.session) {
        GUI.post('api/figure/close', {id: mplx.session})
            .catch(function () { return null; });
    }
    mplx.session = null;
    mplx.fig = null;
    var holder = document.getElementById('lb-mpl');
    if (holder) { holder.innerHTML = ''; }
    var box = document.getElementById('lightbox');
    if (box) { box.classList.remove('interactive'); }
};
