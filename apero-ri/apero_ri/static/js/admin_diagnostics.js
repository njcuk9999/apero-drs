(function () {
    'use strict';
    var profiles = [], host = '', busy = false, report = null;
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
        element('progress-bar').value = percentage;
        element('progress-percent').textContent = percentage + '%';
        element('progress-stage').textContent = text[event.stage] || event.stage;
    }
    async function collect() {
        if (busy) { return; }
        var params = query(); if (!params) { return; }
        busy = true; report = null;
        element('report').textContent = '';
        element('progress').hidden = false;
        element('progress-profile').textContent = params.get('instrument') + ' / ' + params.get('profile_id');
        showProgress({stage: 'runtime', completed: 0, total: 1});
        reportStatus(text.collecting);
        element('report-form').querySelectorAll('input, select, button').forEach(function (control) { control.disabled = true; });
        try {
            var response = await fetch('/api/admin/diagnostics/stream?' + params);
            if (!response.ok) { var failure = await response.json(); throw new Error(failure.error); }
            if (!response.body) { throw new Error(text.failed); }
            var reader = response.body.getReader(), decoder = new TextDecoder(), pending = '';
            var complete = false;
            while (true) {
                var part = await reader.read();
                pending += decoder.decode(part.value || new Uint8Array(), {stream: !part.done});
                var lines = pending.split('\n'); pending = lines.pop();
                for (var index = 0; index < lines.length; index += 1) {
                    if (!lines[index]) { continue; }
                    var event = JSON.parse(lines[index]);
                    if (event.type === 'progress') { showProgress(event); }
                    if (event.type === 'error') { throw new Error(text.failed); }
                    if (event.type === 'report') {
                        report = event.report; complete = true;
                        element('report').textContent = JSON.stringify(report, null, 2);
                    }
                }
                if (part.done) { break; }
            }
            if (!complete) { throw new Error(text.failed); }
            element('progress-stage').textContent = text.ready;
            reportStatus(text.ready);
        } catch (error) {
            report = null; element('progress-stage').textContent = text.failed;
            reportStatus(error.message || text.failed);
        } finally {
            busy = false;
            element('report-form').querySelectorAll('input, select, button').forEach(function (control) { control.disabled = false; });
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
        overview().catch(function (error) { status(error.message); });
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