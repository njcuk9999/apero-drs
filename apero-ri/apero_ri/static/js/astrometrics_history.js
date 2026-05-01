// astrometrics_history.js — front-end logic for the History tab.
// Tab is only present in the DOM when the page-view helper sets
// `astrometrics_can_view_history=true` (i.e. user has
// manage.astrometrics.history).
(function () {
    'use strict';
    var histTab = document.querySelector(
        '.ari-htab[data-htab="history"]');
    if (!histTab) return;

    var loaded = false;
    var _state = {
        page: 1,
        perPage: 50,
        q: '',
        total: 0,
        pages: 0
    };
    var _filterTimer = null;

    function _esc(s) {
        return String(s == null ? '' : s).replace(
            /[<>&"']/g, function (c) {
                return ({'<': '&lt;', '>': '&gt;',
                         '&': '&amp;', '"': '&quot;',
                         "'": '&#39;'})[c];
            });
    }

    function _fmtTime(iso) {
        if (!iso) return '';
        // Show "YYYY-MM-DD HH:MM:SS" stripping the T separator.
        return String(iso).replace('T', ' ');
    }

    function _setStatus(msg) {
        var el = document.getElementById('hist-status');
        if (el) el.innerHTML = msg || '';
    }

    function _setCount() {
        var el = document.getElementById('hist-count');
        if (!el) return;
        if (!_state.total) {
            el.textContent = '';
            return;
        }
        el.textContent = _state.total + ' edits';
    }

    function _updatePager() {
        var info = document.getElementById('hist-page-info');
        var prev = document.getElementById('hist-prev');
        var next = document.getElementById('hist-next');
        if (info) {
            if (!_state.pages) {
                info.textContent = '0 of 0';
            } else {
                info.textContent = _state.page + ' of '
                    + _state.pages;
            }
        }
        if (prev) prev.disabled = (_state.page <= 1);
        if (next) next.disabled = (_state.page >= _state.pages);
    }

    function _renderRow(rec) {
        var card = document.createElement('div');
        card.className = 'hist-card';
        var actionCls = 'hist-card__action--'
            + _esc(String(rec.action || 'edit').toLowerCase());
        var fields = (rec.fields || []).slice(0, 8);
        var moreCount = (rec.fields || []).length - fields.length;
        var fieldHtml = fields.map(function (f) {
            return '<span class="hist-card__field">'
                + _esc(f) + '</span>';
        }).join('');
        if (moreCount > 0) {
            fieldHtml += '<span class="hist-card__field">+'
                + moreCount + ' more</span>';
        }
        if (!fieldHtml) {
            fieldHtml = '<span class="hist-card__field">'
                + '(no field changes)</span>';
        }
        var renamed = '';
        if (rec.previous_apero_name
                && rec.previous_apero_name !== rec.apero_name) {
            renamed = '<span class="hist-card__field" '
                + 'title="renamed">' + _esc(rec.previous_apero_name)
                + ' &rarr; ' + _esc(rec.apero_name) + '</span>';
        }
        card.innerHTML =
            '<span class="hist-card__time" title="'
            + _esc(rec.timestamp) + '">'
            + _esc(_fmtTime(rec.timestamp)) + '</span>'
            + '<span class="hist-card__user" title="'
            + _esc(rec.user) + '">' + _esc(rec.user) + '</span>'
            + '<span class="hist-card__what">'
            + '<span class="hist-card__action ' + actionCls + '">'
            + _esc(rec.action || 'edit') + '</span>'
            + '<span class="hist-card__name">'
            + _esc(rec.apero_name) + '</span>'
            + renamed + fieldHtml + '</span>'
            + '<span class="hist-card__buttons">'
            + '<button type="button" class="hist-card__btn"'
            + ' data-hist-diff title="Show before/after diff">'
            + '<i class="fa-solid fa-eye"></i></button>'
            + '<button type="button" class="hist-card__btn"'
            + ' data-hist-restore title="Restore in editor">'
            + '<i class="fa-solid fa-rotate-left"></i></button>'
            + '</span>';
        var diffBtn = card.querySelector('[data-hist-diff]');
        if (diffBtn) {
            diffBtn.addEventListener('click', function () {
                _openDiff(rec.id);
            });
        }
        var restoreBtn = card.querySelector('[data-hist-restore]');
        if (restoreBtn) {
            restoreBtn.addEventListener('click', function () {
                _restore(rec.id, rec.apero_name);
            });
        }
        return card;
    }

    function _renderRows(rows) {
        var host = document.getElementById('hist-cards');
        if (!host) return;
        host.innerHTML = '';
        if (!rows.length) {
            host.innerHTML = '<div class="ari-section-intro">'
                + 'No history entries match.</div>';
            return;
        }
        rows.forEach(function (r) { host.appendChild(_renderRow(r)); });
    }

    function _load() {
        _setStatus('<i class="fa-solid fa-spinner fa-spin"></i> '
            + 'Loading history...');
        var params = new URLSearchParams();
        params.set('page', _state.page);
        params.set('per_page', _state.perPage);
        if (_state.q) params.set('q', _state.q);
        fetch('/api/astrometrics/history/list?' + params.toString(),
              { credentials: 'same-origin' })
            .then(function (r) {
                return r.text().then(function (txt) {
                    var j = null;
                    try { j = JSON.parse(txt); }
                    catch (e) { j = null; }
                    return { ok: r.ok, status: r.status, body: j };
                });
            })
            .then(function (res) {
                if (!res.body || !res.body.success) {
                    var msg = (res.body && res.body.error)
                        || ('HTTP ' + res.status);
                    _setStatus('Failed: ' + _esc(msg));
                    return;
                }
                _setStatus('');
                _state.total = res.body.total || 0;
                _state.pages = res.body.pages || 0;
                _state.page = res.body.page || 1;
                _state.perPage = res.body.per_page || _state.perPage;
                _setCount();
                _updatePager();
                _renderRows(res.body.rows || []);
            })
            .catch(function (err) {
                _setStatus('Failed: ' + _esc(String(err)));
            });
    }

    function _openDiff(entryId) {
        _setStatus('<i class="fa-solid fa-spinner fa-spin"></i> '
            + 'Loading snapshot...');
        fetch('/api/astrometrics/history/get?id='
              + encodeURIComponent(entryId),
              { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                _setStatus('');
                if (!data || !data.success) {
                    window.alert('Failed: '
                        + ((data && data.error) || 'unknown'));
                    return;
                }
                _showDiffOverlay(data.entry);
            })
            .catch(function (err) {
                _setStatus('Failed: ' + _esc(String(err)));
            });
    }

    function _flatJson(obj) {
        // Stable ordered key=value pairs for raw side-by-side dump.
        if (!obj || typeof obj !== 'object') return [];
        return Object.keys(obj).sort().map(function (k) {
            var v = obj[k];
            if (v && typeof v === 'object') {
                try { v = JSON.stringify(v); }
                catch (e) { v = String(v); }
            }
            return [k, v];
        });
    }

    function _showDiffOverlay(rec) {
        var overlay = document.createElement('div');
        overlay.style.cssText = 'position:fixed;inset:0;'
            + 'background:rgba(0,0,0,0.45);z-index:2600;'
            + 'display:flex;align-items:center;'
            + 'justify-content:center;';
        var box = document.createElement('div');
        box.style.cssText = 'background:#fff;border-radius:8px;'
            + 'padding:14px;width:min(1000px,94vw);'
            + 'max-height:88vh;overflow:auto;';
        var before = rec.before || {};
        var after = rec.after || {};
        var keys = {};
        Object.keys(before).forEach(function (k) { keys[k] = 1; });
        Object.keys(after).forEach(function (k) { keys[k] = 1; });
        var rows = Object.keys(keys).sort().map(function (k) {
            var b = before[k];
            var a = after[k];
            var bs = (b && typeof b === 'object')
                ? JSON.stringify(b) : String(b == null ? '' : b);
            var as = (a && typeof a === 'object')
                ? JSON.stringify(a) : String(a == null ? '' : a);
            var changed = (bs !== as);
            var bg = changed ? 'background:#fff8db;' : '';
            var bCell = changed && bs
                ? '<span style="background:#fdecea;color:#a4221a;'
                  + 'padding:1px 4px;border-radius:3px;'
                  + 'text-decoration:line-through;">'
                  + _esc(bs) + '</span>'
                : (bs ? _esc(bs) : '<i style="color:#888;">empty</i>');
            var aCell = changed && as
                ? '<span style="background:#e6f4ea;color:#1e7e34;'
                  + 'padding:1px 4px;border-radius:3px;">'
                  + _esc(as) + '</span>'
                : (as ? _esc(as) : '<i style="color:#888;">empty</i>');
            return '<tr style="' + bg + '">'
                + '<td style="padding:3px 8px;vertical-align:top;'
                + 'font-family:monospace;font-size:0.8em;">'
                + _esc(k) + '</td>'
                + '<td style="padding:3px 8px;vertical-align:top;'
                + 'font-family:monospace;font-size:0.8em;'
                + 'word-break:break-all;">' + bCell + '</td>'
                + '<td style="padding:3px 8px;vertical-align:top;'
                + 'font-family:monospace;font-size:0.8em;'
                + 'word-break:break-all;">' + aCell + '</td>'
                + '</tr>';
        }).join('');
        box.innerHTML = '<h3 style="margin:0 0 8px 0;">'
            + 'History snapshot for '
            + '<code>' + _esc(rec.apero_name) + '</code></h3>'
            + '<div style="font-size:0.85em;color:#555;'
            + 'margin-bottom:8px;">'
            + _esc(_fmtTime(rec.timestamp)) + ' &middot; '
            + 'by <strong>' + _esc(rec.user) + '</strong> &middot; '
            + _esc(rec.action || 'edit') + '</div>'
            + '<table style="width:100%;border-collapse:collapse;">'
            + '<thead><tr>'
            + '<th align="left" style="padding:4px 8px;">Field</th>'
            + '<th align="left" style="padding:4px 8px;">Before</th>'
            + '<th align="left" style="padding:4px 8px;">After</th>'
            + '</tr></thead><tbody>' + rows + '</tbody></table>'
            + '<div style="display:flex;gap:8px;margin-top:12px;'
            + 'justify-content:flex-end;">'
            + '<button type="button" data-hist-restore-from-diff'
            + ' class="ari-btn ari-btn--secondary">'
            + '<i class="fa-solid fa-rotate-left"></i> '
            + 'Restore this version</button>'
            + '<button type="button" data-hist-diff-close'
            + ' class="ari-btn ari-btn--primary">Close</button>'
            + '</div>';
        overlay.appendChild(box);
        document.body.appendChild(overlay);
        function _close() {
            try { document.body.removeChild(overlay); }
            catch (e) { /* ignore */ }
        }
        overlay.addEventListener('click', function (ev) {
            var t = ev.target;
            if (t === overlay
                    || (t.closest
                        && t.closest('[data-hist-diff-close]'))) {
                _close();
            } else if (t.closest
                    && t.closest('[data-hist-restore-from-diff]')) {
                _close();
                _restore(rec.id, rec.apero_name);
            }
        });
    }

    function _restore(entryId, aperoName) {
        // Pull the snapshot, then push the "after" payload into the
        // Add/Edit manual target form so the user can review and
        // confirm. The form's normal save path (with original_apero_name
        // = aperoName) will append a fresh history entry tagged
        // "restore".
        fetch('/api/astrometrics/history/get?id='
              + encodeURIComponent(entryId),
              { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    window.alert('Failed to load snapshot: '
                        + ((data && data.error) || 'unknown'));
                    return;
                }
                var snap = data.entry && data.entry.after;
                if (!snap || typeof snap !== 'object') {
                    window.alert(
                        'No "after" snapshot available for '
                        + 'this entry.');
                    return;
                }
                var helper = window.AriManualTargetForm;
                if (!helper || typeof helper.prefill !== 'function') {
                    window.alert(
                        'Manual editor not available '
                        + '(open the Add/Edit tab first).');
                    return;
                }
                var tab = document.querySelector(
                    '.ari-htab[data-htab="add-manually"]');
                if (tab) tab.click();
                // Force the form into update-mode pinned to the
                // current apero name so the save endpoint treats it
                // as a restoration of that target.
                var pre = JSON.parse(JSON.stringify(snap));
                pre.APERO_NAME = aperoName;
                helper.prefill(pre);
                if (typeof helper.flagRestore === 'function') {
                    helper.flagRestore(entryId);
                }
            })
            .catch(function (err) {
                window.alert('Failed: ' + err);
            });
    }

    function _wireToolbar() {
        var input = document.getElementById('hist-filter-input');
        if (input && !input.dataset.wired) {
            input.dataset.wired = '1';
            input.addEventListener('input', function () {
                if (_filterTimer) clearTimeout(_filterTimer);
                _filterTimer = setTimeout(function () {
                    _state.q = input.value || '';
                    _state.page = 1;
                    _load();
                }, 250);
            });
        }
        var per = document.getElementById('hist-per-page');
        if (per && !per.dataset.wired) {
            per.dataset.wired = '1';
            per.addEventListener('change', function () {
                _state.perPage = parseInt(per.value, 10) || 50;
                _state.page = 1;
                _load();
            });
        }
        var prev = document.getElementById('hist-prev');
        if (prev && !prev.dataset.wired) {
            prev.dataset.wired = '1';
            prev.addEventListener('click', function () {
                if (_state.page > 1) {
                    _state.page -= 1;
                    _load();
                }
            });
        }
        var next = document.getElementById('hist-next');
        if (next && !next.dataset.wired) {
            next.dataset.wired = '1';
            next.addEventListener('click', function () {
                if (_state.page < _state.pages) {
                    _state.page += 1;
                    _load();
                }
            });
        }
    }

    histTab.addEventListener('click', function () {
        _wireToolbar();
        if (!loaded) {
            loaded = true;
            _load();
        }
    });

    // Public API: let callers (e.g. after a save) refresh the list.
    window.AriAstrometricsHistory = window.AriAstrometricsHistory || {};
    window.AriAstrometricsHistory.refresh = function () {
        if (loaded) _load();
    };
}());
