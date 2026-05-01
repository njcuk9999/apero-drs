/*
 * Astrometrics edit-lock helper.
 *
 * Exposes window.AriAstrometricsLock with:
 *   acquire(aperoName, force) -> Promise<{ok, info}>
 *   startHeartbeat(aperoName)
 *   release(aperoName)
 *   showLockedModal(aperoName, info, onForcedTakeoverDone)
 *
 * Endpoints used:
 *   POST /api/astrometrics/lock/{acquire,heartbeat,release}
 *   POST /api/messages/send  (from the "Send message" action)
 */
(function () {
    'use strict';

    var HEARTBEAT_MS = 5 * 60 * 1000;
    var _heartbeatTimer = null;
    var _heartbeatName = null;

    function _isAdmin() {
        var perms = (window.AperoRI && window.AperoRI.userPerms) || [];
        if (Array.isArray(perms) && perms.indexOf('view.admin') >= 0) {
            return true;
        }
        var groups = (window.AperoRI && window.AperoRI.userGroups) || [];
        return Array.isArray(groups)
            && groups.indexOf('super_admin') >= 0;
    }

    function _post(url, body) {
        return fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body || {})
        }).then(function (r) {
            return r.json().then(function (j) {
                return { status: r.status, ok: r.ok, body: j };
            }).catch(function () {
                return { status: r.status, ok: r.ok, body: null };
            });
        });
    }

    function acquire(aperoName, force) {
        return _post('/api/astrometrics/lock/acquire', {
            apero_name: aperoName,
            force: !!force
        }).then(function (res) {
            if (res.ok && res.body && res.body.success) {
                return { ok: true, info: res.body };
            }
            return { ok: false, info: res.body || {} };
        }).catch(function () {
            // network error: allow edit to proceed without lock
            return { ok: true, info: { error: 'lock-fetch-failed' } };
        });
    }

    function _stopHeartbeat() {
        if (_heartbeatTimer) {
            clearInterval(_heartbeatTimer);
            _heartbeatTimer = null;
        }
        _heartbeatName = null;
    }

    function startHeartbeat(aperoName) {
        _stopHeartbeat();
        if (!aperoName) return;
        _heartbeatName = aperoName;
        _heartbeatTimer = setInterval(function () {
            if (!_heartbeatName) return;
            _post('/api/astrometrics/lock/heartbeat', {
                apero_name: _heartbeatName
            });
        }, HEARTBEAT_MS);
    }

    function release(aperoName) {
        _stopHeartbeat();
        if (!aperoName) return Promise.resolve();
        return _post('/api/astrometrics/lock/release', {
            apero_name: aperoName
        }).catch(function () { /* noop */ });
    }

    function _formatAge(seconds) {
        if (seconds == null) return '';
        var s = parseInt(seconds, 10) || 0;
        if (s < 60) return s + 's';
        if (s < 3600) return Math.floor(s / 60) + 'm';
        return Math.floor(s / 3600) + 'h '
            + Math.floor((s % 3600) / 60) + 'm';
    }

    function _sendMessage(holder, aperoName) {
        var subject = 'Astrometrics: please release lock on '
            + aperoName;
        var body = ('Hi ' + holder + ',\n\n'
            + 'I would like to edit the astrometric entry for "'
            + aperoName + '" but you currently hold the edit lock.'
            + ' Could you finish or release it when convenient?'
            + '\n\nThanks.');
        return _post('/api/messages/send', {
            recipient: holder,
            subject: subject,
            body: body
        }).then(function (res) {
            if (res.ok && res.body && res.body.success) {
                alert('Message sent to ' + holder + '.');
            } else {
                alert('Failed to send message: '
                    + ((res.body && res.body.error)
                        || ('HTTP ' + res.status)));
            }
        });
    }

    function showLockedModal(aperoName, info, onTakeover) {
        info = info || {};
        var holder = String(info.holder || 'another user');
        var ageStr = _formatAge(info.age_seconds);
        var expires = info.expires_at || '';
        var overlay = document.createElement('div');
        overlay.style.cssText = (
            'position:fixed; inset:0; background:rgba(0,0,0,0.5);'
            + ' z-index:10001; display:flex; align-items:center;'
            + ' justify-content:center;'
        );
        var box = document.createElement('div');
        box.style.cssText = (
            'background:var(--ari-card-bg, #fff); color:inherit;'
            + ' border-radius:6px; padding:16px; width:min(520px, 92vw);'
            + ' box-shadow:0 6px 24px rgba(0,0,0,0.25);'
        );
        var html = '<h3 style="margin-top:0;">Entry is being edited</h3>'
            + '<p>The astrometric entry <strong>'
            + aperoName + '</strong> is currently being edited by '
            + '<strong>' + holder + '</strong>'
            + (ageStr ? (' (started ' + ageStr + ' ago)') : '')
            + '.</p>';
        if (expires) {
            html += '<p style="opacity:0.8; font-size:90%;">'
                + 'Lock auto-expires at <code>' + expires + '</code>.</p>';
        }
        html += '<div style="display:flex; gap:8px;'
            + ' justify-content:flex-end; margin-top:12px;'
            + ' flex-wrap:wrap;">'
            + '<button type="button" class="ari-btn"'
            + ' id="alm-msg">Send message to ' + holder + '</button>'
            + '<button type="button" class="ari-btn"'
            + ' id="alm-cancel">Try again later</button>';
        if (_isAdmin()) {
            html += '<button type="button"'
                + ' class="ari-btn ari-btn--danger"'
                + ' id="alm-force">Force takeover (admin)</button>';
        }
        html += '</div>';
        box.innerHTML = html;
        overlay.appendChild(box);
        document.body.appendChild(overlay);

        function _close() {
            try { document.body.removeChild(overlay); } catch (e) { /**/ }
        }
        box.querySelector('#alm-cancel')
            .addEventListener('click', _close);
        box.querySelector('#alm-msg')
            .addEventListener('click', function () {
                _sendMessage(holder, aperoName);
            });
        var fb = box.querySelector('#alm-force');
        if (fb) {
            fb.addEventListener('click', function () {
                acquire(aperoName, true).then(function (res) {
                    if (res.ok) {
                        _close();
                        if (typeof onTakeover === 'function') {
                            onTakeover();
                        }
                    } else {
                        alert('Force takeover failed: '
                            + ((res.info && res.info.error)
                                || 'unknown error'));
                    }
                });
            });
        }
    }

    // release on page unload best-effort
    window.addEventListener('beforeunload', function () {
        if (_heartbeatName) {
            try {
                navigator.sendBeacon(
                    '/api/astrometrics/lock/release',
                    new Blob(
                        [JSON.stringify({apero_name: _heartbeatName})],
                        {type: 'application/json'}
                    )
                );
            } catch (e) { /* noop */ }
        }
    });

    window.AriAstrometricsLock = {
        acquire: acquire,
        startHeartbeat: startHeartbeat,
        release: release,
        showLockedModal: showLockedModal
    };
}());
