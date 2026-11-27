(function () {
    'use strict';
    var profiles = [], host = '', busy = false;
    var activeJob = null, pollTimer = null;
    var text = window.ARI_DIAGNOSTICS_TEXT;
    function element(id) { return document.getElementById('diag-' + id); }
    function status(message) { element('status').textContent = message || ''; }
    function selected() {
        return Array.from(element('profiles').querySelectorAll('input:checked')).map(function (input) {
            return profiles[Number(input.value)];
        });
    }
    async function api(action, body) {
        var options = body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : {};
        var response = await fetch('/api/admin/diagnostics/' + action, options);
        var data = await response.json().catch(function () { return {}; });
        if (!response.ok || !data.success) {
            throw new Error(data.error || (response.status === 429 ? text.rateLimit : text.failed));
        }
        return data;
    }
    async function overview() {
        var data = await api('overview');
        var oldProfile = profiles[Number(element('report-profile').value)];
        profiles = data.profiles; host = data.host;
        element('profiles').replaceChildren();
        element('report-profile').replaceChildren();
        profiles.forEach(function (profile, index) {
            var label = document.createElement('label'), input = document.createElement('input');
            input.type = 'checkbox'; input.value = index; label.className = 'diag-check';
            label.append(input, document.createTextNode(profile.instrument + ' / ' + profile.profile_id));
            element('profiles').append(label);
            var option = document.createElement('option'); option.value = index;
            option.textContent = profile.instrument + ' / ' + profile.profile_id;
            element('report-profile').append(option);
            if (oldProfile && oldProfile.instrument === profile.instrument && oldProfile.profile_id === profile.profile_id) {
                option.selected = true;
            }
        });
        if (oldProfile && !profiles.some(function (profile) {
            return profile.instrument === oldProfile.instrument && profile.profile_id === oldProfile.profile_id;
        })) { reportStatus(''); }
        element('grants').replaceChildren();
        data.grants.forEach(function (grant) {
            var row = document.createElement('tr'); row.className = 'ot-row';
            [grant.label, grant.profiles.map(function (pair) { return pair.join(' / '); }).join(', '), grant.expires_at, grant.state].forEach(function (value) {
                var cell = document.createElement('td'); cell.className = 'ot-cell'; cell.textContent = value; row.append(cell);
            });
            var actions = document.createElement('td'); actions.className = 'ot-cell';
            var button = document.createElement('button'); button.className = 'ari-btn ari-btn--secondary';
            button.title = 'Revoke'; button.setAttribute('aria-label', 'Revoke'); button.disabled = grant.state !== 'active';
            var icon = document.createElement('i'); icon.className = 'fa-solid fa-ban'; button.append(icon);
            button.onclick = async function () {
                try { await api('revoke', {id: grant.id}); await overview(); } catch (error) { status(error.message); }
            };
            actions.append(button); row.append(actions); element('grants').append(row);
        });
    }
    function query() {
        var profile = profiles[Number(element('report-profile').value)];
        if (!profile) { return null; }
        return new URLSearchParams({instrument: profile.instrument, profile_id: profile.profile_id,
            objname: element('object').value.trim(), pid: element('pid').value.trim(),
            logs: element('logs').checked ? '1' : '0', database: element('database').checked ? '1' : '0'});
    }
    function shellQuote(value) { return "'" + value.replace(/'/g, "'\\''") + "'"; }
    function copyInput(input) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(input.value);
        }
        input.focus(); input.select();
        if (document.execCommand('copy')) { return Promise.resolve(); }
        return Promise.reject(new Error(text.copy));
    }
    function reportStatus(message) { element('report-status').textContent = message || ''; }
    function savedStatus(message) { element('saved-status').textContent = message || ''; }
    function table() { return document.querySelector('.diag-saved-table'); }
    function shareUrl(token) {
        // the viewer reads the capability from the fragment, never the query
        var url = new URL(table().dataset.shareView, window.location.href);
        url.hash = token;
        return url.href;
    }
    function wgetCommand(token) {
        // the token travels in a header so it stays out of server access logs
        var url = new URL(table().dataset.downloadApi, window.location.href);
        return 'wget --content-disposition --header='
            + shellQuote('Authorization: Bearer ' + token) + ' ' + shellQuote(url.href);
    }
    function copyText(value) {
        // copyInput expects an input-like element; use an off-screen buffer
        var buffer = document.createElement('textarea');
        buffer.className = 'diag-copy-buffer';
        buffer.setAttribute('aria-hidden', 'true');
        buffer.value = value;
        document.body.appendChild(buffer);
        return copyInput(buffer).finally(function () { buffer.value = ''; buffer.remove(); });
    }
    function showProgress(event) {
        var percentage = event.total > 0 ? Math.floor(event.completed * 100 / event.total) : 0;
        var stage = String(event.stage || ''), colon = stage.indexOf(':');
        var name = colon < 0 ? stage : stage.slice(0, colon);
        element('progress-bar').value = percentage;
        element('progress-percent').textContent = percentage + '%';
        var elapsed = Number.isFinite(event.stage_elapsed_s)
            ? ' (' + event.stage_elapsed_s + ' s)' : '';
        element('progress-stage').textContent = (text[name] || name)
            + (colon < 0 ? '' : ' - ' + stage.slice(colon + 1)) + elapsed;
    }
    function setBusy(value) {
        busy = value;
        element('report-form').querySelectorAll('input, select, button').forEach(function (control) { control.disabled = value; });
    }
    function actionButton(icon, label, handler) {
        var button = document.createElement('button');
        button.type = 'button'; button.className = 'ari-btn ari-btn--sm ari-btn--secondary';
        button.title = label; button.setAttribute('aria-label', label);
        var glyph = document.createElement('i'); glyph.className = 'fa-solid ' + icon;
        glyph.setAttribute('aria-hidden', 'true');
        button.append(glyph);
        button.onclick = async function () {
            // block double clicks while one row action is in flight
            button.disabled = true;
            try { await handler(); } catch (error) { savedStatus(error.message || text.failed); }
            finally { button.disabled = false; }
        };
        return button;
    }
    async function fetchReport(job) {
        var data = await api('job?id=' + encodeURIComponent(job.id));
        if (!data.report) { throw new Error(text.failed); }
        return data.report;
    }
    function reportName(job) {
        return ('apero-diagnostics-' + job.instrument + '-' + job.profile_id)
            .replace(/[^A-Za-z0-9_.-]+/g, '_') + '.json';
    }
    function savedRow(job) {
        var row = document.createElement('tr'); row.className = 'ot-row';
        var collected = (job.completed_at || job.created) * 1000;
        var cells = [job.instrument + ' / ' + job.profile_id, job.options.objname || '',
            job.options.pid || '', new Date(collected).toLocaleString(),
            new Date(job.expires_at * 1000).toLocaleString(),
            job.share_token ? text.shareActive : text.shareNone];
        cells.forEach(function (value, index) {
            var cell = document.createElement('td'); cell.className = 'ot-cell';
            if (index === 2) cell.classList.add('diag-col-pid');
            if (index === 4) cell.classList.add('diag-col-expires');
            cell.textContent = value; row.append(cell);
        });
        var actions = document.createElement('td'); actions.className = 'ot-cell';
        var group = document.createElement('div'); group.className = 'diag-row-actions';
        group.append(
            actionButton('fa-copy', text.copyReport, async function () {
                var report = await fetchReport(job);
                await copyText(JSON.stringify(report, null, 2)).catch(function () {
                    throw new Error(text.copyReportFailed);
                });
                savedStatus(text.copiedReport);
            }),
            actionButton('fa-download', text.downloadReport, async function () {
                var report = await fetchReport(job);
                var blob = new Blob([JSON.stringify(report, null, 2)], {type: 'application/json'});
                var url = URL.createObjectURL(blob), link = document.createElement('a');
                link.href = url; link.download = reportName(job); link.click();
                setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
            }));
        if (job.share_token) {
            group.append(
                actionButton('fa-link', text.copyShare, async function () {
                    await copyText(shareUrl(job.share_token));
                    savedStatus(text.copiedShare);
                }),
                actionButton('fa-terminal', text.copyWget, async function () {
                    await copyText(wgetCommand(job.share_token));
                    savedStatus(text.copiedWget);
                }),
                actionButton('fa-ban', text.revokeShare, async function () {
                    await api('revoke-share', {id: job.id});
                    savedStatus(text.shareRevoked);
                    await refreshSaved();
                }));
        } else {
            group.append(actionButton('fa-share-nodes', text.createShare, async function () {
                await api('share', {id: job.id});
                savedStatus(text.shareCreated);
                await refreshSaved();
            }));
        }
        group.append(actionButton('fa-trash', text.deleteReport, async function () {
            if (!window.confirm(text.deleteConfirm)) return;
            await api('delete', {id: job.id});
            savedStatus(text.deleted);
            await refreshSaved();
        }));
        actions.append(group); row.append(actions);
        return row;
    }
    async function refreshSaved() {
        // the listing already carries share tokens, so rows render instantly
        var data = await api('saved');
        var jobs = data.jobs || [];
        var body = element('saved');
        body.replaceChildren();
        if (!jobs.length) {
            var row = document.createElement('tr'), cell = document.createElement('td');
            cell.className = 'ot-loading'; cell.colSpan = 7; cell.textContent = text.noSaved;
            row.append(cell); body.append(row);
            return;
        }
        jobs.forEach(function (job) { body.append(savedRow(job)); });
    }
    function restoreJob(job) {
        var index = profiles.findIndex(function (profile) {
            return profile.instrument === job.instrument && profile.profile_id === job.profile_id;
        });
        if (index < 0) { return false; }
        element('report-profile').value = String(index);
        element('object').value = job.options.objname;
        element('pid').value = job.options.pid;
        element('logs').checked = job.options.include_logs;
        element('database').checked = job.options.include_database;
        element('progress').hidden = false;
        element('progress-profile').textContent = job.instrument + ' / ' + job.profile_id;
        showProgress(job);
        activeJob = job.id;
        return true;
    }
    async function pollJob(jobId) {
        if (activeJob !== jobId) { return; }
        try {
            var data = await api('job?id=' + encodeURIComponent(jobId));
            if (activeJob !== jobId) { return; }
            showProgress(data.job);
            if (data.job.status === 'running') {
                setBusy(true); reportStatus(text.collecting);
                pollTimer = window.setTimeout(function () { pollJob(jobId); }, 2000);
                return;
            }
            setBusy(false);
            if (data.job.status === 'completed') {
                element('progress-stage').textContent = text.ready;
                reportStatus(text.ready);
                refreshSaved().catch(function (error) { savedStatus(error.message); });
                return;
            }
            var message = data.job.status === 'interrupted' ? text.interrupted : text.failed;
            element('progress-stage').textContent = message;
            reportStatus(message);
        } catch (error) {
            setBusy(false);
            element('progress-stage').textContent = text.disconnected;
            reportStatus(text.disconnected);
        }
    }
    async function resume() {
        // only reattach to a collection that is still running
        var data = await api('latest');
        if (!data.job || data.job.status !== 'running' || !restoreJob(data.job)) { return; }
        setBusy(true);
        reportStatus(text.collecting);
        await pollJob(data.job.id);
    }
    async function collect() {
        if (busy) { return; }
        var params = query(); if (!params) { return; }
        if (pollTimer) { window.clearTimeout(pollTimer); pollTimer = null; }
        activeJob = null;
        setBusy(true);
        element('progress').hidden = false;
        element('progress-profile').textContent = params.get('instrument') + ' / ' + params.get('profile_id');
        showProgress({stage: 'runtime', completed: 0, total: 1});
        reportStatus(text.collecting);
        try {
            var body = {instrument: params.get('instrument'), profile_id: params.get('profile_id'),
                objname: params.get('objname'), pid: params.get('pid'),
                include_logs: params.get('logs') === '1', include_database: params.get('database') === '1'};
            var data = await api('start', body);
            if (!restoreJob(data.job)) { throw new Error(text.failed); }
            await pollJob(data.job.id);
        } catch (error) {
            element('progress-stage').textContent = text.failed;
            reportStatus(error.message || text.failed);
            setBusy(false);
        }
    }
    document.addEventListener('DOMContentLoaded', function () {
        overview().then(refreshSaved).then(resume).catch(function (error) { status(error.message); });
        element('grant-form').onsubmit = async function (event) {
            event.preventDefault();
            var grantStatus = element('grant-status');
            var scope = selected();
            // a key needs an explicit scope; say so next to the button
            if (!scope.length) {
                grantStatus.textContent = text.selectProfile;
                var first = element('profiles').querySelector('input');
                if (first) { first.focus(); }
                return;
            }
            grantStatus.textContent = '';
            try {
                var data = await api('issue', {profiles: scope.map(function (profile) { return [profile.instrument, profile.profile_id]; }),
                    hours: Number(element('hours').value), label: element('label').value});
                element('key').value = data.grant.token;
                element('command').value = 'apero_ri_debug --host=' + shellQuote(host) + ' --key';
                element('issued').hidden = false; await overview(); status('');
            } catch (error) { grantStatus.textContent = error.message; }
        };
        ['key', 'command'].forEach(function (name) {
            element('copy-' + name).onclick = function () {
                copyInput(element(name)).catch(function (error) { status(error.message); });
            };
        });
        element('profiles').addEventListener('change', function () { element('grant-status').textContent = ''; });
        element('report-form').onsubmit = function (event) { event.preventDefault(); collect(); };
    });
}());