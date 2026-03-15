/* =========================================================================
   Data Portal – Profile health check
   ========================================================================= */
(function () {
    'use strict';

    var cfg = window.ARI_PROFILE_PAGE;
    var healthDb = document.getElementById('health-db');
    var healthPaths = document.getElementById('health-paths');

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

    runHealthCheck();
})();
