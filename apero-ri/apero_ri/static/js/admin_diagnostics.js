(function () {
    'use strict';
    var profiles = [], host = '', busy = false, report = null;
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
        var data = await response.json();
        if (!response.ok || !data.success) { throw new Error(data.error || String(response.status)); }
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
        })) { invalidate(); }
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
    function reportStatus(message) { element('report-status').textContent = message; }
    function invalidate() {
        if (report) {
            report = null;
            element('report').textContent = '';
            element('progress').hidden = true;
            reportStatus(text.changed);
        }
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
            if (data.job.status === 'completed' && data.report) {
                report = data.report;
                element('report').textContent = JSON.stringify(report, null, 2);
                element('progress-stage').textContent = text.ready;
                reportStatus(text.ready);
                return;
            }
            report = null;
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
        var data = await api('latest');
        if (!data.job || !restoreJob(data.job)) { return; }
        setBusy(true);
        reportStatus(text.collecting);
        await pollJob(data.job.id);
    }
    async function collect() {
        if (busy) { return; }
        var params = query(); if (!params) { return; }
        if (pollTimer) { window.clearTimeout(pollTimer); pollTimer = null; }
        activeJob = null; report = null;
        setBusy(true);
        element('report').textContent = '';
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
            report = null; element('progress-stage').textContent = text.failed;
            reportStatus(error.message || text.failed);
            setBusy(false);
        }
    }
    async function downloadReport() {
        if (busy) { reportStatus(text.collecting); return; }
        if (!report) { reportStatus(text.first); return; }
        reportStatus(text.download);
        try {
            var json = JSON.stringify(report, null, 2);
            var blob = new Blob([json], {type: 'application/json'});
            var name = 'apero-diagnostics.json';
            if (typeof CompressionStream === 'function') {
                var compressed = blob.stream().pipeThrough(new CompressionStream('gzip'));
                blob = await new Response(compressed).blob();
                name += '.gz';
            }
            var url = URL.createObjectURL(blob), link = document.createElement('a');
            link.href = url; link.download = name; link.click();
            setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
            reportStatus(text.ready);
        } catch (error) { reportStatus(error.message || text.failed); }
    }
    document.addEventListener('DOMContentLoaded', function () {
        overview().then(resume).catch(function (error) { status(error.message); });
        element('grant-form').onsubmit = async function (event) {
            event.preventDefault();
            try {
                var scope = selected();
                var data = await api('issue', {profiles: scope.map(function (profile) { return [profile.instrument, profile.profile_id]; }),
                    hours: Number(element('hours').value), label: element('label').value});
                element('key').value = data.grant.token;
                element('command').value = 'apero_ri_debug --host=' + shellQuote(host) + ' --key';
                element('issued').hidden = false; await overview(); status('');
            } catch (error) { status(error.message); }
        };
        ['key', 'command'].forEach(function (name) {
            element('copy-' + name).onclick = function () {
                copyInput(element(name)).catch(function (error) { status(error.message); });
            };
        });
        element('report-form').onsubmit = function (event) { event.preventDefault(); collect(); };
        element('report-form').addEventListener('input', invalidate);
        element('report-form').addEventListener('change', invalidate);
        element('export').onclick = downloadReport;
    });
}());