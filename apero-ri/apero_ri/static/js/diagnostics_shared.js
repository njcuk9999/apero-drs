(function () {
    'use strict';
    var root = document.querySelector('.shared-report');
    var status = document.getElementById('shared-status');
    var copy = document.getElementById('shared-copy');
    var download = document.getElementById('shared-download');
    var token = window.location.hash.slice(1);
    if (!token) { status.textContent = root.dataset.unavailable; return; }
    fetch(root.dataset.api, {headers: {'Authorization': 'Bearer ' + token}, cache: 'no-store'})
        .then(function (response) {
            if (!response.ok) throw new Error('unavailable');
            return response.json();
        })
        .then(function (data) {
            if (!data.success || !data.report) throw new Error('unavailable');
            var json = JSON.stringify(data.report, null, 2);
            var profile = [data.report.instrument, data.report.profile_id].filter(Boolean).join(' / ');
            var objname = (data.report.filters || {}).objname;
            document.getElementById('shared-profile').textContent = profile + (objname ? ' / ' + objname : '');
            status.textContent = root.dataset.ready;
            if (data.expires_at) {
                document.getElementById('shared-expiry-time').textContent = new Date(data.expires_at * 1000).toLocaleString();
                document.getElementById('shared-expiry').hidden = false;
            }
            copy.hidden = false;
            copy.onclick = async function () {
                var buffer = document.createElement('textarea');
                buffer.className = 'shared-copy-buffer';
                buffer.setAttribute('aria-hidden', 'true');
                buffer.value = json; document.body.appendChild(buffer);
                try {
                    if (navigator.clipboard && window.isSecureContext) {
                        await navigator.clipboard.writeText(json);
                    } else {
                        buffer.focus(); buffer.select();
                        if (!document.execCommand('copy')) throw new Error('copy');
                    }
                    status.textContent = root.dataset.copied;
                } catch (error) { status.textContent = root.dataset.copyFailed; }
                finally { buffer.value = ''; buffer.remove(); }
            };
            download.hidden = false;
            download.onclick = function () {
                var url = URL.createObjectURL(new Blob([json], {type: 'application/json'}));
                var link = document.createElement('a');
                link.href = url; link.download = 'apero-diagnostics.json'; link.click();
                setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
            };
        })
        .catch(function () { status.textContent = root.dataset.unavailable; });
}());