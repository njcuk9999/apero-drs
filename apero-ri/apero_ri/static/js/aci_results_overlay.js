/* aci_results_overlay.js
 * Shared "check results" overlay used by:
 *   - admin_portal/apero_check_info?check={CHECK}   (single-check mode)
 *   - admin_portal/apero_checks_policy               (profile-summary mode)
 *
 * Call ACI_RESULTS_OVERLAY.init(cfg) once after DOMContentLoaded, then
 * ACI_RESULTS_OVERLAY.open(state, checkKey, profileId) to open the overlay.
 *
 * cfg keys:
 *   checkResultsUrl  – endpoint URL
 *   overlayId        – id of the overlay <div>         (default 'aci-results-overlay')
 *   checkInfoBaseUrl – base URL for check-info links   (optional)
 */

/* global window, document, fetch, setTimeout, clearTimeout */
window.ACI_RESULTS_OVERLAY = (function () {
    'use strict';

    var _cfg = {};
    var _overlay = null, _backdrop = null, _closeBtn = null,
        _refreshBtn = null, _title = null, _loading = null,
        _content = null, _tbody = null, _summary = null,
        _pageInfo = null, _pageTotal = null, _pageInput = null,
        _filterInp = null, _perpage = null,
        _btnFirst = null, _btnPrev = null, _btnNext = null, _btnLast = null;

    var _state = null, _checkKey = '', _profileId = '';
    var _allRows = [], _filteredRows = [], _page = 1, _pp = 50;
    var _hasCheckCol = false;
    var _pollTimer = null;

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function cancelPoll() {
        if (_pollTimer) { clearTimeout(_pollTimer); _pollTimer = null; }
    }

    /* ── Table rendering ── */
    function renderPage() {
        var total = _filteredRows.length;
        var pp = _pp === 0 ? total : _pp;
        var totalPages = Math.max(1, pp ? Math.ceil(total / pp) : 1);
        if (_page > totalPages) _page = totalPages;
        if (_page < 1) _page = 1;
        var start = pp ? (_page - 1) * pp : 0;
        var end   = pp ? Math.min(start + pp, total) : total;
        var slice = _filteredRows.slice(start, end);

        var html = '';
        slice.forEach(function (row, idx) {
            var bg = (start + idx) % 2 === 0
                ? 'background:var(--ari-card-bg)'
                : 'background:var(--ari-bg,#f9fafb)';
            var link = row.obsdir_url
                ? '<a class="ari-link" href="' + esc(row.obsdir_url) +
                  '" target="_blank" rel="noopener">' +
                  '<i class="fa-solid fa-arrow-up-right-from-square"></i></a>'
                : '';
            var checkCell = '';
            if (_hasCheckCol) {
                var ck = esc(row.check_key || '');
                var ciUrl = _cfg.checkInfoBaseUrl
                    ? _cfg.checkInfoBaseUrl + '?check=' + encodeURIComponent(row.check_key || '')
                    : '';
                checkCell = ciUrl
                    ? '<td class="ot-cell"><a class="ari-link" href="' + esc(ciUrl) +
                      '">' + ck + '</a></td>'
                    : '<td class="ot-cell">' + ck + '</td>';
            }
            html += '<tr class="ot-row" style="' + bg + '">'
                + '<td class="ot-cell">' + esc(row.profile_id) + '</td>'
                + '<td class="ot-cell">' + esc(row.obsdir) + '</td>'
                + checkCell
                + '<td class="ot-cell">' + link + '</td>'
                + '</tr>';
        });
        if (_tbody) _tbody.innerHTML = html ||
            '<tr><td class="ot-cell" colspan="4" style="color:var(--ari-text-muted);padding:1rem;">No results.</td></tr>';

        var showing = total ? (start + 1) + '–' + end + ' of ' + total : '0';
        if (_pageInfo) _pageInfo.textContent = showing;
        if (_summary) _summary.textContent = total + ' result(s)';
        if (_pageTotal) _pageTotal.textContent = String(totalPages);
        if (_pageInput) _pageInput.value = String(_page);
        var atFirst = _page <= 1, atLast = _page >= totalPages;
        if (_btnFirst) _btnFirst.disabled = atFirst;
        if (_btnPrev)  _btnPrev.disabled  = atFirst;
        if (_btnNext)  _btnNext.disabled  = atLast;
        if (_btnLast)  _btnLast.disabled  = atLast;
    }

    function applyFilter() {
        var q = (_filterInp ? _filterInp.value : '').trim().toLowerCase();
        _filteredRows = q
            ? _allRows.filter(function (r) {
                  return ([r.profile_id, r.obsdir, r.check_key || '']
                      .join(' ')).toLowerCase().indexOf(q) >= 0;
              })
            : _allRows.slice();
        _page = 1;
        renderPage();
    }

    /* ── Header rebuilding (called when _hasCheckCol changes) ── */
    function buildHeader() {
        var headerRow = document.querySelector('#aci-results-table .ot-header-row');
        if (!headerRow) return;
        var checkTh = _hasCheckCol
            ? '<th class="ot-th ot-th--nonsortable">Check</th>' : '';
        headerRow.innerHTML =
            '<th class="ot-th ot-th--nonsortable">Profile</th>' +
            '<th class="ot-th ot-th--nonsortable">Obs-dir</th>' +
            checkTh +
            '<th class="ot-th ot-th--nonsortable">Link</th>';
    }

    /* ── Fetch & poll ── */
    function fetchResults(state, checkKey, profileId, forceRefresh) {
        var url = _cfg.checkResultsUrl
            + '?state=' + encodeURIComponent(state);
        if (checkKey)    url += '&check_key='  + encodeURIComponent(checkKey);
        if (profileId)   url += '&profile_id=' + encodeURIComponent(profileId);
        if (forceRefresh) url += '&force_refresh=1';

        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (_state !== state) return; // stale
                if (data.is_building) {
                    var step = String(data.build_step || 'Building index…');
                    var pct  = Math.round(data.build_pct || 0);
                    var bar  = Math.max(4, Math.min(100, pct));
                    if (_loading) _loading.innerHTML =
                        '<div style="display:flex;flex-direction:column;gap:.65rem;padding:.5rem 0;">' +
                        '<div><i class="fa-solid fa-spinner fa-spin"></i> ' + esc(step) + '</div>' +
                        '<div style="background:var(--ari-border);border-radius:999px;height:.45rem;overflow:hidden;width:100%;">' +
                        '<div style="background:var(--ari-primary);height:100%;border-radius:999px;width:' + bar + '%;transition:width .4s ease;"></div></div>' +
                        '<div style="font-size:.82rem;color:var(--ari-text-muted);">' + pct + '%</div></div>';
                    _pollTimer = setTimeout(function () {
                        fetchResults(state, checkKey, profileId, false);
                    }, 3000);
                    return;
                }
                _hasCheckCol = !!data.has_check_column;
                buildHeader();
                _allRows = data.rows || [];
                _pp = _perpage ? parseInt(_perpage.value, 10) : 50;
                applyFilter();
                if (_loading) _loading.hidden = true;
                if (_content) _content.hidden = false;
            })
            .catch(function () {
                if (_state !== state) return;
                if (_tbody) _tbody.innerHTML =
                    '<tr><td colspan="4" style="color:var(--ari-danger,red);padding:1rem">Failed to load results.</td></tr>';
                if (_loading) _loading.hidden = true;
                if (_content) _content.hidden = false;
            });
    }

    /* ── Public API ── */
    function open(state, checkKey, profileId) {
        if (!_overlay) return;
        cancelPoll();
        _state = state;
        _checkKey = checkKey || '';
        _profileId = profileId || '';

        // Build a descriptive title.
        var label = state.charAt(0).toUpperCase() + state.slice(1);
        if (_checkKey) label += ' — ' + _checkKey;
        if (_profileId) label += ' (' + _profileId + ')';
        if (_title) _title.textContent = label;

        if (_loading) {
            _loading.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Loading…';
            _loading.hidden = false;
        }
        if (_content) _content.hidden = true;
        _allRows = [];
        _filteredRows = [];
        if (_filterInp) _filterInp.value = '';

        _overlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        fetchResults(state, _checkKey, _profileId, false);
    }

    function close() {
        cancelPoll();
        _state = null;
        if (_overlay) _overlay.style.display = 'none';
        document.body.style.overflow = '';
    }

    function init(cfg) {
        _cfg = cfg || {};
        var id = _cfg.overlayId || 'aci-results-overlay';
        _overlay    = document.getElementById(id);
        _backdrop   = document.getElementById('aci-results-backdrop');
        _closeBtn   = document.getElementById('aci-results-close');
        _refreshBtn = document.getElementById('aci-results-refresh');
        _title      = document.getElementById('aci-results-title');
        _loading    = document.getElementById('aci-results-loading');
        _content    = document.getElementById('aci-results-content');
        _tbody      = document.getElementById('aci-res-tbody');
        _summary    = document.getElementById('aci-res-summary');
        _pageInfo   = document.getElementById('aci-res-page-info');
        _pageTotal  = document.getElementById('aci-res-page-total');
        _pageInput  = document.getElementById('aci-res-page-input');
        _filterInp  = document.getElementById('aci-res-filter');
        _perpage    = document.getElementById('aci-res-perpage');
        _btnFirst   = document.getElementById('aci-res-first');
        _btnPrev    = document.getElementById('aci-res-prev');
        _btnNext    = document.getElementById('aci-res-next');
        _btnLast    = document.getElementById('aci-res-last');

        if (_backdrop) _backdrop.addEventListener('click', close);
        if (_closeBtn) _closeBtn.addEventListener('click', close);
        if (_refreshBtn) {
            _refreshBtn.addEventListener('click', function () {
                if (!_state) return;
                cancelPoll();
                if (_loading) {
                    _loading.innerHTML =
                        '<i class="fa-solid fa-spinner fa-spin"></i> Refreshing…';
                    _loading.hidden = false;
                }
                if (_content) _content.hidden = true;
                fetchResults(_state, _checkKey, _profileId, true);
            });
        }
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') close();
        });

        function go(n) { _page = n; renderPage(); }
        if (_btnFirst) _btnFirst.addEventListener('click', function () { go(1); });
        if (_btnLast)  _btnLast.addEventListener('click', function () {
            go(Math.max(1, Math.ceil(_filteredRows.length / (_pp || 1))));
        });
        if (_btnPrev)  _btnPrev.addEventListener('click', function () { go(_page - 1); });
        if (_btnNext)  _btnNext.addEventListener('click', function () { go(_page + 1); });
        if (_pageInput) _pageInput.addEventListener('change', function () {
            go(parseInt(_pageInput.value, 10) || 1);
        });
        if (_perpage) _perpage.addEventListener('change', function () {
            _pp = parseInt(_perpage.value, 10);
            _page = 1;
            renderPage();
        });
        if (_filterInp) _filterInp.addEventListener('input', applyFilter);
    }

    return { init: init, open: open, close: close };
}());
