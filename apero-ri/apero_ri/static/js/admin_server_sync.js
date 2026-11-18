/* APERO RI - Admin Portal: Server Sync page */
(function () {
    'use strict';

    var cfg = window.ARI_SERVER_SYNC || {};
    var state = {
        overview: null,
        peerId: null,
        plan: null,
        pollTimer: null,
        sshBlock: ''
    };

    // ------------------------------------------------------------------
    // helpers
    // ------------------------------------------------------------------
    function $(id) { return document.getElementById(id); }

    function esc(value) {
        return String(value === undefined || value === null ? '' : value)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function url(action, params) {
        var out = cfg.apiUrl.replace('__ACTION__', action);
        if (params) {
            var query = Object.keys(params).map(function (k) {
                return encodeURIComponent(k) + '=' +
                    encodeURIComponent(params[k]);
            }).join('&');
            out += '?' + query;
        }
        return out;
    }

    function api(action, body, params) {
        var opts = { credentials: 'same-origin', headers: {} };
        if (body !== undefined && body !== null) {
            opts.method = 'POST';
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }
        return fetch(url(action, params), opts).then(function (resp) {
            return resp.json().catch(function () {
                return { success: false, error: 'HTTP ' + resp.status };
            });
        }).then(function (data) {
            if (!data || data.success === false) {
                throw new Error((data && data.error) || 'Request failed');
            }
            return data;
        });
    }

    function toast(message, isError) {
        var el = $('ss-toast');
        el.textContent = message;
        el.className = 'ari-toast ' +
            (isError ? 'ari-toast--error' : 'ari-toast--success');
        el.style.display = 'block';
        clearTimeout(toast.timer);
        toast.timer = setTimeout(function () {
            el.style.display = 'none';
        }, isError ? 7000 : 3500);
    }

    function fail(err) { toast(err.message || String(err), true); }

    function when(value) {
        if (!value) { return '-'; }
        var date = typeof value === 'number' ? new Date(value * 1000) :
            new Date(value);
        if (isNaN(date.getTime())) { return esc(value); }
        return date.toLocaleString();
    }

    function setStatus(level, headline, details) {
        var box = $('ss-status');
        box.className = 'ari-ap-status ari-ap-status--' + level;
        $('ss-status-headline').innerHTML = headline;
        $('ss-status-details').innerHTML = (details || []).map(function (d) {
            return '<li>' + esc(d) + '</li>';
        }).join('');
    }

    function currentPeer() {
        if (!state.overview) { return null; }
        return state.overview.peers.filter(function (p) {
            return p.peer_id === state.peerId;
        })[0] || null;
    }

    function radioValue(name) {
        var el = document.querySelector('input[name="' + name + '"]:checked');
        return el ? el.value : '';
    }

    function copyText(id) {
        var text = $(id).textContent;
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(function () {
                toast('Copied');
            }, function () { fallbackCopy(text); });
        } else {
            fallbackCopy(text);
        }
    }

    function fallbackCopy(text) {
        var area = document.createElement('textarea');
        area.value = text;
        document.body.appendChild(area);
        area.select();
        try { document.execCommand('copy'); toast('Copied'); }
        catch (e) { toast('Copy failed: select and copy manually', true); }
        document.body.removeChild(area);
    }

    // ------------------------------------------------------------------
    // tabs
    // ------------------------------------------------------------------
    function showTab(name) {
        document.querySelectorAll('[data-ss-tab]').forEach(function (btn) {
            var active = btn.getAttribute('data-ss-tab') === name;
            btn.classList.toggle('ari-ab-tab--active', active);
            btn.setAttribute('aria-selected', active ? 'true' : 'false');
        });
        document.querySelectorAll('[data-ss-panel]').forEach(function (p) {
            p.hidden = p.getAttribute('data-ss-panel') !== name;
        });
        if (name === 'history') { loadHistory(); }
        if (name === 'local') { loadLocal(); }
        if (name === 'run') { renderRun(); }
    }

    // ------------------------------------------------------------------
    // overview
    // ------------------------------------------------------------------
    function loadOverview() {
        return api('overview').then(function (data) {
            state.overview = data;
            if (!state.peerId && data.peers.length) {
                state.peerId = data.peers[0].peer_id;
            }
            renderOverview();
            renderRun();
        }).catch(function (err) {
            setStatus('error', 'Could not load server sync state.',
                      [err.message]);
        });
    }

    function renderOverview() {
        var data = state.overview;
        $('ss-root-name').textContent = data.root_username || '(not set)';
        $('ss-server-name').value = data.identity.server_name || '';
        $('ss-server-id').textContent = data.identity.server_id;
        $('ss-this-url').textContent = data.this_url;
        var badge = $('ss-local-badge');
        badge.hidden = !data.pending_setup;
        badge.textContent = data.pending_setup;
        renderPeerCards();
        renderIssued();
        var details = [];
        var level = 'ok';
        var auto = data.peers.filter(function (p) { return p.auto_sync; });
        var task = (data.tasks || {}).SERVER_SYNC || {};
        if (!data.peers.length) {
            level = 'info';
            details.push('No peers configured: start with the Guide tab.');
        }
        data.peers.forEach(function (p) {
            if (!p.approved) {
                level = 'warning';
                details.push(p.label + ': needs a reviewed run (Run tab).');
            } else if (p.last_run_ok === false) {
                level = 'warning';
                details.push(p.label + ': last run had errors.');
            }
            if (p.last_conflicts) {
                details.push(p.label + ': ' + p.last_conflicts +
                             ' conflict(s) waiting for review.');
            }
        });
        if (auto.length && !task.active) {
            level = 'warning';
            details.push('Automatic sync is on for a peer but the Server ' +
                         'Sync async task is not active.');
        }
        if (data.pending_setup) {
            details.push(data.pending_setup +
                         ' synced record(s) need local setup.');
        }
        var headline = level === 'ok' ?
            '<i class="fa-solid fa-circle-check"></i> Server sync healthy.' :
            '<i class="fa-solid fa-circle-info"></i> Server sync: ' +
            data.peers.length + ' peer(s).';
        setStatus(level, headline, details);
    }

    function peerStatusChips(p) {
        var chips = [];
        chips.push('<span class="ss-chip">' + esc(p.mode === 'mirror' ?
            'mirror' : 'copy') + '</span>');
        chips.push(p.approved ?
            '<span class="ss-chip ss-chip--ok">reviewed</span>' :
            '<span class="ss-chip ss-chip--warn">needs review</span>');
        chips.push(p.auto_sync ?
            '<span class="ss-chip ss-chip--ok">auto</span>' :
            '<span class="ss-chip">manual</span>');
        if (p.last_run_ok === false) {
            chips.push('<span class="ss-chip ss-chip--err">last run failed' +
                       '</span>');
        }
        return chips.join(' ');
    }

    function renderPeerCards() {
        var list = $('ss-peer-list');
        var peers = state.overview.peers;
        if (!peers.length) {
            list.innerHTML = '<p class="ss-muted">No peers yet.</p>';
            return;
        }
        list.innerHTML = peers.map(function (p) {
            return '<div class="ss-card" data-peer="' + esc(p.peer_id) + '">' +
                '<div class="ss-card__head"><strong>' + esc(p.label) +
                '</strong> ' + peerStatusChips(p) + '</div>' +
                '<dl class="ss-dl">' +
                '<dt>URL</dt><dd><code>' + esc(p.url) + '</code></dd>' +
                '<dt>Remote</dt><dd>' + esc(p.remote_server_name || '-') +
                ' (' + esc(p.remote_version || '?') + ', token ' +
                esc(p.remote_scope || '?') + ')</dd>' +
                '<dt>Clock skew</dt><dd>' +
                esc(p.clock_skew !== undefined ?
                    Number(p.clock_skew).toFixed(1) + ' s' : '-') + '</dd>' +
                '<dt>Last contact</dt><dd>' + when(p.last_hello_at) +
                '</dd></dl>' +
                '<div class="ss-edit" hidden>' +
                '<label class="ss-field">Label <input class="ari-ap-input" ' +
                'data-f="label" value="' + esc(p.label) + '"></label>' +
                '<label class="ss-field">URL <input class="ari-ap-input" ' +
                'data-f="url" value="' + esc(p.url) + '"></label>' +
                '<label class="ss-field">New token (optional) ' +
                '<input class="ari-ap-input" type="password" data-f="token">' +
                '</label>' +
                '<label class="ss-field">Mode <select class="ari-ap-input" ' +
                'data-f="mode"><option value="mirror"' +
                (p.mode === 'mirror' ? ' selected' : '') +
                '>Complete mirror</option><option value="copy"' +
                (p.mode === 'copy' ? ' selected' : '') +
                '>Copy</option></select></label>' +
                '<button type="button" class="ari-btn ari-btn--primary ' +
                'ari-btn--sm" data-act="save">Save</button></div>' +
                '<div class="ss-actions">' +
                '<button type="button" class="ari-btn ari-btn--secondary ' +
                'ari-btn--sm" data-act="test"><i class="fa-solid ' +
                'fa-plug-circle-check"></i> Test</button>' +
                '<button type="button" class="ari-btn ari-btn--secondary ' +
                'ari-btn--sm" data-act="edit"><i class="fa-solid fa-pen">' +
                '</i> Edit</button>' +
                '<button type="button" class="ari-btn ari-btn--secondary ' +
                'ari-btn--sm" data-act="run"><i class="fa-solid ' +
                'fa-arrows-rotate"></i> Open in Run</button>' +
                '<button type="button" class="ari-btn ari-btn--danger ' +
                'ari-btn--sm" data-act="delete"><i class="fa-solid ' +
                'fa-trash"></i> Remove</button></div></div>';
        }).join('');
    }

    function onPeerCardClick(event) {
        var btn = event.target.closest('button[data-act]');
        if (!btn) { return; }
        var card = btn.closest('[data-peer]');
        var peerId = card.getAttribute('data-peer');
        var act = btn.getAttribute('data-act');
        if (act === 'edit') {
            var box = card.querySelector('.ss-edit');
            box.hidden = !box.hidden;
        } else if (act === 'save') {
            var body = { peer_id: peerId };
            card.querySelectorAll('[data-f]').forEach(function (el) {
                if (el.value) { body[el.getAttribute('data-f')] = el.value; }
            });
            api('update_peer', body).then(function () {
                toast('Peer saved');
                return loadOverview();
            }).catch(fail);
        } else if (act === 'test') {
            btn.disabled = true;
            api('test_peer', { peer_id: peerId }).then(function (data) {
                var msgs = data.hello.blocking.concat(data.hello.warnings);
                toast(msgs.length ? msgs.join(' ') : 'Connection OK (' +
                      data.hello.server_name + ')', !!data.hello.blocking.length);
                return loadOverview();
            }).catch(fail).then(function () { btn.disabled = false; });
        } else if (act === 'run') {
            state.peerId = peerId;
            showTab('run');
        } else if (act === 'delete') {
            if (!window.confirm('Remove this peer and forget its sync ' +
                                'history? Data on both servers is kept.')) {
                return;
            }
            api('delete_peer', { peer_id: peerId }).then(function () {
                if (state.peerId === peerId) { state.peerId = null; }
                toast('Peer removed');
                return loadOverview();
            }).catch(fail);
        }
    }

    function onAddPeer(event) {
        event.preventDefault();
        var body = {
            label: $('ss-add-label').value,
            url: $('ss-add-url').value,
            token: $('ss-add-token').value,
            mode: radioValue('ss-add-mode')
        };
        var btn = event.target.querySelector('button[type="submit"]');
        btn.disabled = true;
        api('add_peer', body).then(function (data) {
            event.target.reset();
            state.peerId = data.peer.peer_id;
            var warn = data.hello.warnings || [];
            toast('Peer added' + (warn.length ? ': ' + warn.join(' ') : ''),
                  false);
            return loadOverview();
        }).catch(fail).then(function () { btn.disabled = false; });
    }

    // ------------------------------------------------------------------
    // generate
    // ------------------------------------------------------------------
    function renderIssued() {
        var rows = state.overview.issued;
        $('ss-issued-body').innerHTML = rows.length ? rows.map(function (r) {
            return '<tr class="ot-row"><td data-label="Label">' +
                esc(r.label) + '</td><td data-label="Access">' +
                esc(r.scope === 'readwrite' ? 'read + write' : 'read only') +
                '</td><td data-label="Created">' + when(r.created_at) +
                ' (' + esc(r.created_by) + ')</td><td data-label="Last used">' +
                when(r.last_used_at) + (r.last_used_by ? ' by ' +
                esc(r.last_used_by) : '') + '</td><td>' +
                '<button type="button" class="ari-btn ari-btn--danger ' +
                'ari-btn--sm" data-revoke="' + esc(r.key_id) + '">Revoke' +
                '</button></td></tr>';
        }).join('') : '<tr><td colspan="5" class="ss-muted">No tokens ' +
            'issued.</td></tr>';
    }

    function onGenerate(event) {
        event.preventDefault();
        var body = { label: $('ss-gen-label').value,
                     scope: radioValue('ss-gen-scope') };
        api('issue_token', body).then(function (data) {
            $('ss-gen-token').textContent = data.token;
            $('ss-gen-url').textContent = state.overview.this_url;
            $('ss-gen-result').hidden = false;
            state.overview.issued = data.issued;
            renderIssued();
            event.target.reset();
        }).catch(fail);
    }

    function onRevoke(event) {
        var btn = event.target.closest('button[data-revoke]');
        if (!btn || !window.confirm('Revoke this token? The other server ' +
                                    'will no longer be able to sync.')) {
            return;
        }
        api('revoke_token', { key_id: btn.getAttribute('data-revoke') })
            .then(function (data) {
                state.overview.issued = data.issued;
                renderIssued();
                toast('Token revoked');
            }).catch(fail);
    }

    // ------------------------------------------------------------------
    // run tab
    // ------------------------------------------------------------------
    function renderRun() {
        if (!state.overview) { return; }
        var peers = state.overview.peers;
        $('ss-run-empty').hidden = peers.length > 0;
        $('ss-run-body').hidden = !peers.length;
        $('ss-run-peers').innerHTML = peers.map(function (p) {
            var active = p.peer_id === state.peerId;
            return '<button type="button" class="ari-sg-tab' +
                (active ? ' ari-sg-tab--active' : '') + '" role="tab" ' +
                'aria-selected="' + active + '" data-run-peer="' +
                esc(p.peer_id) + '">' + esc(p.label) + '</button>';
        }).join('');
        var peer = currentPeer();
        if (!peer) { return; }
        $('ss-run-peer-info').innerHTML =
            '<dt>Mode</dt><dd>' + (peer.mode === 'mirror' ?
                'Complete mirror (both ways, newest wins)' :
                'Copy from ' + esc(peer.label)) + '</dd>' +
            '<dt>Status</dt><dd>' + peerStatusChips(peer) + '</dd>' +
            '<dt>Last run</dt><dd>' + when(peer.last_run_at) +
            (peer.last_run_dry ? ' (analysis)' : '') + '</dd>' +
            '<dt>Last real sync</dt><dd>' + when(peer.last_sync_at) + '</dd>' +
            '<dt>Reviewed by</dt><dd>' + esc(peer.approved_by || '-') +
            ' ' + (peer.approved_at ? when(peer.approved_at) : '') + '</dd>';
        $('ss-auto-sync').checked = !!peer.auto_sync;
        $('ss-auto-sync').disabled = !peer.approved;
        $('ss-auto-hint').textContent = peer.approved ? '' :
            'Analyse, review and run a sync manually first; automatic ' +
            'sync unlocks after a successful run.';
        renderCategories(peer);
        renderTasks();
        renderRunStatus(peer.run || {});
        loadPlan();
    }

    function renderCategories(peer) {
        $('ss-categories').innerHTML = state.overview.categories.map(
            function (c) {
                var on = !!peer.categories[c.name];
                var tags = [];
                if (c.needs_setup) { tags.push('needs local setup'); }
                if (c.task_data) { tags.push('own async task'); }
                return '<label class="ss-cat"><input type="checkbox" ' +
                    'data-cat="' + esc(c.name) + '"' + (on ? ' checked' : '') +
                    '><span><strong>' + esc(c.label) + '</strong>' +
                    (tags.length ? ' <em class="ss-muted">(' +
                     esc(tags.join(', ')) + ')</em>' : '') + '<br><small>' +
                    esc(c.description) + '</small></span></label>';
            }).join('');
    }

    function onSaveCategories() {
        var cats = {};
        document.querySelectorAll('#ss-categories [data-cat]')
            .forEach(function (el) {
                cats[el.getAttribute('data-cat')] = el.checked;
            });
        api('update_peer', { peer_id: state.peerId, categories: cats })
            .then(function () {
                toast('Categories saved');
                return loadOverview();
            }).catch(fail);
    }

    function onAutoSync(event) {
        api('update_peer', { peer_id: state.peerId,
                             auto_sync: event.target.checked })
            .then(function () {
                toast(event.target.checked ? 'Automatic sync on' :
                      'Automatic sync off');
                return loadOverview();
            }).catch(function (err) {
                event.target.checked = !event.target.checked;
                fail(err);
            });
    }

    function renderTasks() {
        var tasks = state.overview.tasks || {};
        var labels = { SERVER_SYNC: 'Records (users, groups, profiles...)',
                       SERVER_SYNC_TASK_DATA: 'Task outputs (tasks/)' };
        $('ss-tasks').innerHTML = Object.keys(labels).map(function (key) {
            var t = tasks[key];
            if (!t) {
                return '<div class="ss-task"><strong>' + esc(labels[key]) +
                    '</strong><p class="ss-muted">Not registered yet: open ' +
                    'the <a href="' + esc(cfg.asyncTasksUrl) + '">Async ' +
                    'Tasks</a> page once.</p></div>';
            }
            return '<div class="ss-task" data-task="' + key + '"><strong>' +
                esc(labels[key]) + '</strong> <code>' + key + '</code>' +
                '<div class="ss-actions"><label class="ss-switch">' +
                '<input type="checkbox" data-tf="active"' +
                (t.active ? ' checked' : '') + '> Active</label>' +
                '<label class="ss-inline">Every <input class="ari-ap-input ' +
                'ss-num" type="number" min="0.05" step="0.05" ' +
                'data-tf="frequency" value="' + esc(t.frequency) + '"> h' +
                '</label><button type="button" class="ari-btn ' +
                'ari-btn--secondary ari-btn--sm" data-tf-save="1">Save' +
                '</button></div><small class="ss-muted">Last run: ' +
                esc(t.last_run || 'never') + ' &middot; status: ' +
                esc(t.last_status || '-') + '</small></div>';
        }).join('');
    }

    function onTaskSave(event) {
        var btn = event.target.closest('[data-tf-save]');
        if (!btn) { return; }
        var box = btn.closest('[data-task]');
        var body = {
            task_key: box.getAttribute('data-task'),
            active: box.querySelector('[data-tf="active"]').checked,
            frequency: box.querySelector('[data-tf="frequency"]').value
        };
        api('task_update', body).then(function (data) {
            state.overview.tasks = data.tasks;
            renderTasks();
            toast('Task updated');
        }).catch(fail);
    }

    function startRun(dryRun) {
        if (!dryRun && !window.confirm('Write changes to this server' +
                (currentPeer().mode === 'mirror' ? ' and to the peer' : '') +
                ' now? Unresolved conflicts are skipped.')) {
            return;
        }
        var body = { peer_id: state.peerId, dry_run: dryRun,
                     kind: $('ss-run-kind').value };
        api('run', body).then(function (data) {
            renderRunStatus(data.run);
            poll();
        }).catch(fail);
    }

    function renderRunStatus(run) {
        var el = $('ss-run-status');
        var busy = run.status === 'running' || run.status === 'cancelling';
        $('ss-analyse').disabled = busy;
        $('ss-run-now').disabled = busy;
        $('ss-stop').disabled = run.status === 'cancelling';
        if (!run.status) { el.innerHTML = ''; return; }
        if (run.status === 'cancelling') {
            el.textContent = 'Stopping safely. Waiting for the current ' +
                'operation to finish; automatic sync is off.';
            return;
        }
        if (run.status === 'cancelled' || run.status === 'interrupted') {
            el.textContent = run.status === 'cancelled' ?
                'Sync stopped. Completed changes are kept. Automatic ' +
                'sync is off; analyse again before restarting.' :
                'Sync interrupted: its server process exited. ' +
                'Analyse again before restarting.';
            return;
        }
        if (busy) {
            el.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> ' +
                (run.dry_run ? 'Analysing' : 'Syncing') + ' since ' +
                when(run.started_at) + '...';
            return;
        }
        var s = run.summary || {};
        var cls = s.ok ? 'ss-ok' : 'ss-err';
        var lines = [(run.dry_run ? 'Analysis' : 'Sync') + ' finished ' +
                     when(run.finished_at) + (s.seconds !== undefined ?
                     ' in ' + s.seconds + ' s' : '') + '.'];
        (s.warnings || []).forEach(function (w) {
            lines.push('Warning: ' + w);
        });
        (s.errors || []).slice(0, 20).forEach(function (e) {
            lines.push('Error: ' + e);
        });
        if (state.resolutionPeerId === state.peerId) {
            if (s.ok) {
                lines.push(s.conflicts ? s.conflicts +
                    ' conflict(s) still need a decision.' :
                    'Conflicts resolved. Run sync now to apply the changes.');
            } else {
                lines.push('Decisions saved, but conflict analysis failed. ' +
                           'Retry Analyse to refresh the list.');
            }
        }
        el.innerHTML = '<div class="' + cls + '">' + lines.map(esc)
            .join('<br>') + '</div>';
    }

    function poll() {
        clearTimeout(state.pollTimer);
        state.pollTimer = setTimeout(function () {
            api('overview').then(function (data) {
                state.overview = data;
                var peer = currentPeer();
                if (peer && peer.run && ['running', 'cancelling'].includes(
                    peer.run.status)) {
                    renderRunStatus(peer.run);
                    poll();
                } else {
                    renderOverview();
                    renderRun();
                }
            }).catch(fail);
        }, 2000);
    }

    // ------------------------------------------------------------------
    // plan / conflicts
    // ------------------------------------------------------------------
    var ACTIONS = [
        ['conflicts', 'Conflicts (need a decision)'],
        ['pull', 'Take from peer'],
        ['push', 'Send to peer'],
        ['merge', 'Merge both'],
        ['keep', 'Keep local (no change)'],
        ['skipped', 'Skipped by you']
    ];
    var RES_LABELS = { remote: 'take remote', local: 'keep local',
                       skip: 'skip always', allow: 'allow duplicate' };

    function loadPlan() {
        if (!state.peerId) { return; }
        api('plan', null, { peer_id: state.peerId }).then(function (data) {
            state.plan = data;
            renderPlan();
        }).catch(fail);
    }

    function sideText(entry) {
        if (!entry) { return 'absent'; }
        return (entry.d ? 'deleted ' : '') + when(entry.ts);
    }

    function renderPlan() {
        var data = state.plan;
        var box = $('ss-plan');
        var planCats = data.plan || {};
        // registry order (JSON responses sort keys alphabetically)
        var cats = state.overview.categories.map(function (c) {
            return c.name;
        }).filter(function (name) { return planCats[name]; });
        if (!cats.length) {
            box.innerHTML = '<p class="ss-muted">No analysis yet: click ' +
                'Analyse.</p>';
            return;
        }
        var labels = {};
        state.overview.categories.forEach(function (c) {
            labels[c.name] = c.label;
        });
        var html = '<p class="ss-muted">' + (data.plan_dry_run ?
            'Analysis' : 'Last sync') + ' from ' + when(data.plan_at) +
            '. Decisions you make below apply on the next run.</p>';
        cats.forEach(function (cat) {
            var plan = data.plan[cat];
            var res = (data.resolutions || {})[cat] || {};
            var counts = ACTIONS.map(function (a) {
                var n = (plan[a[0]] || []).length;
                return n ? '<span class="ss-chip' + (a[0] === 'conflicts' ?
                    ' ss-chip--warn' : '') + '">' + esc(a[1]) + ': ' + n +
                    '</span>' : '';
            }).filter(Boolean).join(' ');
            var hasWork = ACTIONS.some(function (a) {
                return (plan[a[0]] || []).length;
            });
            html += '<details class="ss-plan-cat"' +
                ((plan.conflicts || []).length ? ' open' : '') + '>' +
                '<summary><strong>' + esc(labels[cat] || cat) + '</strong> ' +
                (counts || '<span class="ss-chip ss-chip--ok">in sync</span>') +
                ' <span class="ss-muted">(' + (plan.agree_count || 0) +
                ' identical)</span></summary>';
            if (hasWork) {
                html += '<div class="ss-actions"><label class="ss-inline">' +
                    'Selected: <select class="ari-ap-input" data-bulk-res>' +
                    '<option value="remote">take remote</option>' +
                    '<option value="local">keep local</option>' +
                    '<option value="skip">skip always</option>' +
                    '<option value="allow">allow duplicate</option>' +
                    '<option value="clear">clear decision</option></select>' +
                    '</label><button type="button" class="ari-btn ' +
                    'ari-btn--secondary ari-btn--sm" data-bulk-apply="' +
                    esc(cat) + '">Apply to selected</button></div>';
            }
            ACTIONS.forEach(function (a) {
                var items = plan[a[0]] || [];
                if (!items.length) { return; }
                html += '<h4 class="ss-h4">' + esc(a[1]) + '</h4>' +
                    '<div class="ot-table-wrap"><table class="ot-table ' +
                    'ss-table"><thead><tr><th><input type="checkbox" ' +
                    'data-all aria-label="Select all"></th><th>Record</th>' +
                    '<th>Why</th><th>Here</th><th>Peer</th><th>Decision</th>' +
                    '</tr></thead><tbody>';
                items.slice(0, 500).forEach(function (it) {
                    html += '<tr class="ot-row' + (a[0] === 'conflicts' ?
                        ' ss-row--conflict' : '') + '"><td><input ' +
                        'type="checkbox" data-key="' + esc(it.key) + '" ' +
                        'aria-label="Select"></td><td data-label="Record">' +
                        esc(it.label) + '</td><td data-label="Why">' +
                        esc(it.reason) + '</td><td data-label="Here">' +
                        sideText(it.local) + '</td><td data-label="Peer">' +
                        sideText(it.remote) + '</td><td data-label=' +
                        '"Decision">' + esc(RES_LABELS[res[it.key]] || '-') +
                        '</td></tr>';
                });
                if (items.length > 500) {
                    html += '<tr><td colspan="6" class="ss-muted">' +
                        (items.length - 500) + ' more not shown</td></tr>';
                }
                html += '</tbody></table></div>';
            });
            html += '</details>';
        });
        box.innerHTML = html;
    }

    function onPlanClick(event) {
        var all = event.target.closest('input[data-all]');
        if (all) {
            all.closest('table').querySelectorAll('input[data-key]')
                .forEach(function (el) { el.checked = all.checked; });
            return;
        }
        var btn = event.target.closest('button[data-bulk-apply]');
        if (!btn) { return; }
        var details = btn.closest('details');
        var keys = [];
        details.querySelectorAll('input[data-key]:checked')
            .forEach(function (el) { keys.push(el.getAttribute('data-key')); });
        if (!keys.length) { toast('Select records first', true); return; }
        var body = {
            peer_id: state.peerId,
            category: btn.getAttribute('data-bulk-apply'),
            keys: keys,
            resolution: details.querySelector('[data-bulk-res]').value
        };
        btn.disabled = true;
        return api('resolve', body).then(function () {
            toast('Decisions saved. Refreshing conflict analysis...');
            var request = { peer_id: body.peer_id, dry_run: true,
                            kind: $('ss-run-kind').value };
            return api('run', request);
        }).then(function (data) {
            state.resolutionPeerId = body.peer_id;
            renderRunStatus(data.run);
            poll();
        }).catch(function (err) {
            btn.disabled = false;
            fail(err);
        });
    }

    // ------------------------------------------------------------------
    // local setup
    // ------------------------------------------------------------------
    function loadLocal() {
        api('setup_list').then(function (data) {
            renderLocal(data);
        }).catch(fail);
    }

    function renderLocal(data) {
        $('ss-ssh-path').textContent = data.ssh_config;
        $('ss-ssh-hosts').innerHTML = data.ssh_hosts.length ?
            data.ssh_hosts.map(function (h) {
                return '<span class="ss-chip">' + esc(h) + '</span>';
            }).join(' ') : '<span class="ss-muted">none</span>';
        var options = data.ssh_hosts.map(function (h) {
            return '<option value="' + esc(h) + '">';
        }).join('');
        var kinds = { profile: 'APERO profile', tunnel: 'DB SSH tunnel',
                      local_db: 'Local database', sshfs: 'SSHFS mount' };
        $('ss-local-items').innerHTML = data.items.length ?
            data.items.map(function (it, idx) {
                var fields = it.editable.map(function (f) {
                    var value = it.values[f] === null ||
                        it.values[f] === undefined ? '' : it.values[f];
                    var list = f === 'ssh_config_host' ?
                        ' list="ss-hosts-' + idx + '"' : '';
                    return '<label class="ss-field">' + esc(f) +
                        ' <input class="ari-ap-input" data-lf="' + esc(f) +
                        '" value="' + esc(value) + '"' + list + '></label>';
                }).join('');
                return '<div class="ss-card" data-kind="' + esc(it.kind) +
                    '" data-name="' + esc(it.name) + '"><div ' +
                    'class="ss-card__head"><strong>' + esc(kinds[it.kind]) +
                    ': ' + esc(it.name) + '</strong></div><p class=' +
                    '"ss-muted">' + esc(it.hint) + '</p><datalist id=' +
                    '"ss-hosts-' + idx + '">' + options + '</datalist>' +
                    '<div class="ss-grid">' + fields + '</div>' +
                    '<div class="ss-actions"><button type="button" ' +
                    'class="ari-btn ari-btn--primary ari-btn--sm" ' +
                    'data-local-save="1">' + (it.editable.length ?
                    'Save &amp; mark done' : 'Mark done') + '</button>' +
                    (it.kind === 'profile' ? ' <a class="ari-btn ' +
                    'ari-btn--secondary ari-btn--sm" href="' +
                    esc(cfg.profilesUrl) + '">Open APERO Profiles</a>' : '') +
                    '</div></div>';
            }).join('') :
            '<p class="ss-muted">Nothing to set up.</p>';
        var badge = $('ss-local-badge');
        badge.hidden = !data.items.length;
        badge.textContent = data.items.length;
    }

    function onLocalSave(event) {
        var btn = event.target.closest('button[data-local-save]');
        if (!btn) { return; }
        var card = btn.closest('[data-kind]');
        var values = {};
        card.querySelectorAll('[data-lf]').forEach(function (el) {
            values[el.getAttribute('data-lf')] = el.value;
        });
        var body = { kind: card.getAttribute('data-kind'),
                     name: card.getAttribute('data-name'),
                     values: values, done: true };
        api('setup_update', body).then(function () {
            toast('Saved');
            loadLocal();
        }).catch(fail);
    }

    function sshFields() {
        var out = {};
        $('ss-ssh-form').querySelectorAll('input[name]').forEach(function (el) {
            out[el.name] = el.value.trim();
        });
        return out;
    }

    function onSshPreview() {
        api('ssh_preview', { fields: sshFields() }).then(function (data) {
            state.sshBlock = data.block;
            $('ss-ssh-block').textContent = data.block;
            var cmd = "cat >> ~/.ssh/config <<'EOF'\n\n" + data.block +
                'EOF\nchmod 600 ~/.ssh/config';
            $('ss-ssh-command').textContent = cmd;
            $('ss-ssh-command').hidden = false;
            $('ss-ssh-append').disabled = false;
        }).catch(function (err) {
            $('ss-ssh-append').disabled = true;
            fail(err);
        });
    }

    function onSshAppend() {
        if (!window.confirm('Append this block to ~/.ssh/config on this ' +
                            'server? A backup copy is made first.\n\n' +
                            state.sshBlock)) {
            return;
        }
        api('ssh_append', { fields: sshFields(), confirm: true })
            .then(function (data) {
                toast('Added. Backup: ' + (data.backup || 'none (new file)'));
                $('ss-ssh-append').disabled = true;
                loadLocal();
            }).catch(fail);
    }

    // ------------------------------------------------------------------
    // history
    // ------------------------------------------------------------------
    function loadHistory() {
        api('history', null, { limit: 200 }).then(function (data) {
            $('ss-history-body').innerHTML = data.history.length ?
                data.history.map(function (h) {
                    var incoming = h.event === 'incoming';
                    var event = incoming ? 'received (' + h.category + ')' :
                        (h.dry_run ? 'analysis' : 'sync') +
                        (h.auto ? ' (auto)' : '');
                    var who = incoming ? h.caller : h.peer + ' by ' + h.actor;
                    var result = incoming ? h.upserts + ' upserts, ' +
                        h.deletes + ' deletes, ' + h.errors + ' errors' :
                        (h.ok ? 'ok' : 'failed') + ', ' + h.conflicts +
                        ' conflict(s)';
                    var details = incoming ? '' : (h.errors || []).concat(
                        h.warnings || []).slice(0, 3).join('; ');
                    return '<tr class="ot-row"><td data-label="When">' +
                        when(h.at) + '</td><td data-label="Event">' +
                        esc(event) + '</td><td data-label="Peer">' + esc(who) +
                        '</td><td data-label="Result">' + esc(result) +
                        '</td><td data-label="Details">' + esc(details) +
                        '</td></tr>';
                }).join('') :
                '<tr><td colspan="5" class="ss-muted">No history.</td></tr>';
        }).catch(fail);
    }

    // ------------------------------------------------------------------
    // wiring
    // ------------------------------------------------------------------
    document.querySelectorAll('[data-ss-tab]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            showTab(btn.getAttribute('data-ss-tab'));
        });
    });
    document.addEventListener('click', function (event) {
        var copy = event.target.closest('[data-ss-copy]');
        if (copy) { copyText(copy.getAttribute('data-ss-copy')); }
        var tab = event.target.closest('[data-run-peer]');
        if (tab) {
            state.peerId = tab.getAttribute('data-run-peer');
            renderRun();
        }
    });
    $('ss-save-name').addEventListener('click', function () {
        api('identity', { server_name: $('ss-server-name').value })
            .then(function () { toast('Name saved'); return loadOverview(); })
            .catch(fail);
    });
    $('ss-peer-list').addEventListener('click', onPeerCardClick);
    $('ss-add-form').addEventListener('submit', onAddPeer);
    $('ss-gen-form').addEventListener('submit', onGenerate);
    $('ss-issued-body').addEventListener('click', onRevoke);
    $('ss-save-cats').addEventListener('click', onSaveCategories);
    $('ss-auto-sync').addEventListener('change', onAutoSync);
    $('ss-tasks').addEventListener('click', onTaskSave);
    $('ss-analyse').addEventListener('click', function () {
        startRun(true);
    });
    $('ss-run-now').addEventListener('click', function () {
        startRun(false);
    });
    $('ss-stop').addEventListener('click', function () {
        api('stop', { peer_id: state.peerId }).then(function (data) {
            state.resolutionPeerId = null;
            renderRunStatus(data.run);
            toast('Stop requested. Automatic sync disabled for this peer.');
            poll();
        }).catch(fail);
    });
    $('ss-plan').addEventListener('click', onPlanClick);
    $('ss-local-items').addEventListener('click', onLocalSave);
    $('ss-ssh-preview').addEventListener('click', onSshPreview);
    $('ss-ssh-append').addEventListener('click', onSshAppend);
    $('ss-ssh-form').addEventListener('input', function () {
        $('ss-ssh-append').disabled = true;
    });
    $('ss-history-refresh').addEventListener('click', loadHistory);

    loadOverview().then(function () {
        var peer = currentPeer();
        if (peer && peer.run && ['running', 'cancelling'].includes(
            peer.run.status)) { poll(); }
    });
}());
