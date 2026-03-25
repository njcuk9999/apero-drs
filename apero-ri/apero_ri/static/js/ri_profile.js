/* =========================================================================
   Data Portal – Profile health check
   ========================================================================= */
(function () {
    'use strict';

    var cfg = window.ARI_PROFILE_PAGE;
    var healthDb = document.getElementById('health-db');
    var healthPaths = document.getElementById('health-paths');

    function lastObjectStorageKey() {
        return 'ari.dp:last-object-page:' + String(cfg.profileId || '');
    }

    function loadLastObjectEntry() {
        try {
            var raw = localStorage.getItem(lastObjectStorageKey());
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            if (!parsed || typeof parsed !== 'object') return null;
            var objname = String(parsed.objname || '').trim();
            var url = String(parsed.url || '').trim();
            if (!objname || !url) return null;
            return {
                objname: objname,
                url: url
            };
        } catch (_err) {
            return null;
        }
    }

    function upsertLastObjectCard(entry) {
        var node = document.querySelector('.ari-rp-section-card[data-key="last_object_page"]');
        if (!node || !entry) return;

        var card = node;
        if (String(node.tagName || '').toLowerCase() !== 'a') {
            var a = document.createElement('a');
            a.className = 'ari-rp-section-card ari-rp-section-card--active';
            a.setAttribute('data-key', 'last_object_page');
            a.href = entry.url;
            a.innerHTML = node.innerHTML;
            node.parentNode.replaceChild(a, node);
            card = a;
        }

        card.classList.remove('ari-rp-section-card--disabled');
        card.classList.add('ari-rp-section-card--active');
        card.setAttribute('href', entry.url);

        var h3 = card.querySelector('.ari-rp-section-card__body h3');
        if (h3) {
            h3.textContent = 'Last Object Page: ' + entry.objname;
        }
        var p = card.querySelector('.ari-rp-section-card__body p');
        if (p) {
            p.textContent = 'Re-open your most recently visited object page for this profile.';
        }
    }

    function setIndicator(el, ok, tooltip) {
        el.className = 'ari-rp-health ' +
            (ok ? 'ari-rp-health--ok' : 'ari-rp-health--fail');
        var icon = ok ? 'fa-circle-check' : 'fa-circle-xmark';
        var label = el.querySelector('.ari-rp-health__label').textContent;
        el.innerHTML = '<i class="fa-solid ' + icon + '"></i>' +
                       '<span class="ari-rp-health__label">' + label + '</span>';
        el.title = tooltip || '';
    }

    function runHealthCheck() {
        fetch(cfg.healthUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile_id: cfg.profileId }),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) {
                setIndicator(healthDb, false, data.error || 'Error');
                setIndicator(healthPaths, false, data.error || 'Error');
                return;
            }
            // Database
            var dbOk = data.database && data.database.ok;
            var dbTip = dbOk ? 'Connected' : (data.database.error || 'Failed');
            setIndicator(healthDb, dbOk, dbTip);

            // Paths
            var pathsOk = data.paths && data.paths.ok;
            var pathTip = pathsOk ? 'All paths exist' : 'Some paths missing';
            if (!pathsOk && data.paths && data.paths.details) {
                var missing = [];
                var details = data.paths.details;
                for (var k in details) {
                    if (details.hasOwnProperty(k) && !details[k]) {
                        missing.push(k);
                    }
                }
                if (missing.length > 0) {
                    pathTip = 'Missing: ' + missing.join(', ');
                }
            }
            setIndicator(healthPaths, pathsOk, pathTip);
        })
        .catch(function () {
            setIndicator(healthDb, false, 'Request failed');
            setIndicator(healthPaths, false, 'Request failed');
        });
    }

    upsertLastObjectCard(loadLastObjectEntry());
    runHealthCheck();
})();
