/* admin_assets.js - Admin: Assets Management (hosted APERO asset tars) */
(function () {
    'use strict';

    var cfg = window.ARI_ADMIN_ASSETS || {};
    var pathInput = document.getElementById('am-path');
    var saveBtn = document.getElementById('am-save');
    var statusEl = document.getElementById('am-status');
    var unsetEl = document.getElementById('am-unset');
    var bodyEl = document.getElementById('am-body');
    var publicEl = document.getElementById('am-public');
    var publicUrlEl = document.getElementById('am-public-url');

    function fmtSize(bytes) {
        var units = ['B', 'KB', 'MB', 'GB', 'TB'];
        var val = Number(bytes) || 0;
        var idx = 0;
        while (val >= 1024 && idx < units.length - 1) {
            val /= 1024;
            idx += 1;
        }
        return val.toFixed(idx === 0 ? 0 : 1) + ' ' + units[idx];
    }

    function fmtAge(seconds) {
        var s = Math.max(0, Number(seconds) || 0);
        if (s < 3600) { return Math.round(s / 60) + ' min'; }
        if (s < 86400) { return (s / 3600).toFixed(1) + ' h'; }
        return (s / 86400).toFixed(1) + ' d';
    }

    function setStatus(msg) {
        statusEl.textContent = msg || '';
    }

    function messageRow(text) {
        bodyEl.innerHTML = '';
        var tr = document.createElement('tr');
        var td = document.createElement('td');
        td.colSpan = 5;
        td.className = 'at-muted-hint';
        td.textContent = text;
        tr.appendChild(td);
        bodyEl.appendChild(tr);
    }

    function renderFiles(files) {
        if (!files.length) {
            messageRow('No asset files hosted yet.');
            return;
        }
        bodyEl.innerHTML = '';
        files.forEach(function (f) {
            var tr = document.createElement('tr');
            [f.name, fmtSize(f.size_bytes), fmtAge(f.age_s),
             String(f.modified || '').replace('T', ' ').slice(0, 19)]
                .forEach(function (text) {
                    var td = document.createElement('td');
                    td.textContent = text;
                    tr.appendChild(td);
                });
            var act = document.createElement('td');
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ari-btn ari-btn--danger ari-btn--sm';
            btn.innerHTML = '<i class="fa-solid fa-trash"></i> Delete';
            btn.addEventListener('click', function () {
                deleteFile(f.name);
            });
            act.appendChild(btn);
            tr.appendChild(act);
            bodyEl.appendChild(tr);
        });
    }

    function postJson(url, payload) {
        return fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        }).then(function (r) { return r.json(); });
    }

    function load() {
        fetch(cfg.statusUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    messageRow(data.error || 'Failed to load assets.');
                    return;
                }
                pathInput.value = data.assets_path || '';
                publicEl.checked = data.public_download !== false;
                publicUrlEl.textContent = data.public_url || '';
                unsetEl.style.display = data.configured ? 'none' : '';
                if (!data.configured) {
                    messageRow('Set an assets directory to list files.');
                    return;
                }
                renderFiles(data.files || []);
            })
            .catch(function () { messageRow('Failed to load assets.'); });
    }

    function deleteFile(name) {
        if (!window.confirm('Delete ' + name + ' from disk? ' +
                            'This cannot be undone.')) {
            return;
        }
        postJson(cfg.deleteUrl, {filename: name}).then(function (data) {
            setStatus(data.success ? 'Deleted ' + name : data.error);
            load();
        });
    }

    saveBtn.addEventListener('click', function () {
        setStatus('Saving...');
        postJson(cfg.configUrl, {assets_path: pathInput.value,
                                 public_download: publicEl.checked})
            .then(function (data) {
                setStatus(data.success ? 'Saved.' : data.error);
                load();
            })
            .catch(function () { setStatus('Save failed.'); });
    });

    load();
}());
