/* cal_ics.js — ICS external calendar feed management
 * Works on both user_portal/calendar and admin_portal/calendar.
 * User config  → window.ARI_CALENDAR  (icsListUrl, icsAddUrl, etc.)
 * Admin config → window.ARI_ADMIN_CAL (same keys + canManage flag)
 */
'use strict';

// ── helpers ──────────────────────────────────────────────────────────────────

function _icsConfig() {
    if (window.ARI_CALENDAR) return { cfg: window.ARI_CALENDAR, mode: 'user' };
    if (window.ARI_ADMIN_CAL) return { cfg: window.ARI_ADMIN_CAL, mode: 'admin' };
    return null;
}

function _toast(msg, ok) {
    // Re-use the existing page toast if available, otherwise console-log.
    const id = window.ARI_ADMIN_CAL
        ? 'admin-cal-toast'
        : 'cal-toast';
    const el = document.getElementById(id);
    if (!el) { (ok ? console.log : console.error)(msg); return; }
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3500);
}

async function _post(url, body) {
    const r = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    return r.json();
}

async function _get(url) {
    const r = await fetch(url);
    return r.json();
}

// ── render helpers ────────────────────────────────────────────────────────────

function _makeItem(feed, mode) {
    const div = document.createElement('div');
    div.className = 'ari-cal-ics-item';
    div.dataset.feedId = feed.id;

    const dot = document.createElement('span');
    dot.className = 'ari-cal-ics-dot';
    dot.style.background = feed.color || '#888';

    const name = document.createElement('span');
    name.className = 'ari-cal-ics-name';
    name.title = feed.url || '';
    name.textContent = feed.name || feed.url;

    const meta = document.createElement('span');
    meta.className = 'ari-cal-ics-meta';
    meta.textContent = feed.last_synced ? feed.last_synced : 'never';

    div.append(dot, name, meta);

    if (feed.last_error) {
        const err = document.createElement('span');
        err.className = 'ari-cal-ics-err';
        err.title = feed.last_error;
        err.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
        div.appendChild(err);
    }

    if (mode === 'admin' && !window.ARI_ADMIN_CAL.canManage) {
        return div;
    }

    const btnRefresh = document.createElement('button');
    btnRefresh.className =
        'ari-btn ari-btn--secondary ari-btn--sm ari-cal-ics-btn-refresh';
    btnRefresh.title = 'Refresh now';
    btnRefresh.dataset.feedId = feed.id;
    btnRefresh.innerHTML = '<i class="fa-solid fa-rotate"></i>';

    const btnDelete = document.createElement('button');
    btnDelete.className =
        'ari-btn ari-btn--danger ari-btn--sm ari-cal-ics-btn-delete';
    btnDelete.title = 'Remove feed';
    btnDelete.dataset.feedId = feed.id;
    btnDelete.innerHTML = '<i class="fa-solid fa-xmark"></i>';

    div.append(btnRefresh, btnDelete);
    return div;
}

function _renderFeeds(feeds, listEl, emptyEl, mode) {
    listEl.querySelectorAll('.ari-cal-ics-item').forEach(n => n.remove());
    if (!feeds || feeds.length === 0) {
        if (emptyEl) emptyEl.style.display = '';
        return;
    }
    if (emptyEl) emptyEl.style.display = 'none';
    feeds.forEach(f => listEl.insertBefore(
        _makeItem(f, mode),
        emptyEl || null,
    ));
}

// ── user calendar ─────────────────────────────────────────────────────────────

function _initUser() {
    const cfg = window.ARI_CALENDAR;
    if (!cfg || !cfg.icsListUrl) return;

    const listEl = document.getElementById('cal-ics-feed-list');
    const emptyEl = document.getElementById('cal-ics-empty');
    const addForm = document.getElementById('cal-ics-add-form');
    if (!listEl) return;

    // Add-form submit
    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('cal-ics-name').value.trim();
            const url  = document.getElementById('cal-ics-url').value.trim();
            const color = document.getElementById('cal-ics-color').value;
            if (!name || !url) return;
            const btn = addForm.querySelector('button[type=submit]');
            btn.disabled = true;
            btn.textContent = 'Syncing…';
            try {
                const data = await _post(cfg.icsAddUrl, { name, url, color });
                if (data.ok) {
                    _toast('Feed added and synced.', true);
                    _renderFeeds(data.feeds, listEl, emptyEl, 'user');
                    addForm.reset();
                    const wrap = addForm.closest('details');
                    if (wrap) wrap.removeAttribute('open');
                } else {
                    _toast(data.error || 'Failed to add feed.', false);
                }
            } catch {
                _toast('Network error.', false);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Add & Sync';
            }
        });
    }

    // Delegated: refresh / delete
    listEl.addEventListener('click', async (e) => {
        const refreshBtn = e.target.closest('.ari-cal-ics-btn-refresh');
        const deleteBtn  = e.target.closest('.ari-cal-ics-btn-delete');
        if (!refreshBtn && !deleteBtn) return;

        const feedId = (refreshBtn || deleteBtn).dataset.feedId;

        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fa-solid fa-rotate fa-spin"></i>';
            try {
                const data = await _post(cfg.icsRefreshUrl, { feed_id: feedId });
                if (data.ok) {
                    _toast('Feed refreshed.', true);
                    _renderFeeds(data.feeds, listEl, emptyEl, 'user');
                } else {
                    _toast(data.error || 'Refresh failed.', false);
                    refreshBtn.disabled = false;
                    refreshBtn.innerHTML =
                        '<i class="fa-solid fa-rotate"></i>';
                }
            } catch {
                _toast('Network error.', false);
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fa-solid fa-rotate"></i>';
            }
        }

        if (deleteBtn) {
            if (!confirm('Remove this external calendar?')) return;
            deleteBtn.disabled = true;
            try {
                const data = await _post(cfg.icsDeleteUrl, { feed_id: feedId });
                if (data.ok) {
                    _toast('Feed removed.', true);
                    _renderFeeds(data.feeds, listEl, emptyEl, 'user');
                } else {
                    _toast(data.error || 'Delete failed.', false);
                    deleteBtn.disabled = false;
                }
            } catch {
                _toast('Network error.', false);
                deleteBtn.disabled = false;
            }
        }
    });
}

// ── admin calendar ────────────────────────────────────────────────────────────

let _adminIcsLoaded = null; // last instrument name loaded

async function _adminIcsLoad(instrument) {
    const cfg = window.ARI_ADMIN_CAL;
    if (!cfg || !cfg.icsListUrl || !cfg.canManage) return;
    if (!instrument) return;

    const listEl = document.getElementById('admin-cal-ics-feed-list');
    const emptyEl = document.getElementById('admin-cal-ics-empty');
    const addWrap = document.getElementById('admin-ics-add-wrap');
    const instrLabel = document.getElementById('admin-ics-instr-label');
    if (!listEl) return;

    // Show/hide add form
    if (addWrap) addWrap.style.display = '';
    if (instrLabel) instrLabel.textContent = `— ${instrument}`;

    _adminIcsLoaded = instrument;

    try {
        const url = `${cfg.icsListUrl}?instrument=${encodeURIComponent(instrument)}`;
        const data = await _get(url);
        if (data.ok) {
            _renderFeeds(data.feeds, listEl, emptyEl, 'admin');
        } else {
            if (emptyEl) {
                emptyEl.textContent = data.error || 'Could not load feeds.';
                emptyEl.style.display = '';
            }
        }
    } catch {
        if (emptyEl) {
            emptyEl.textContent = 'Network error loading feeds.';
            emptyEl.style.display = '';
        }
    }
}

function _initAdmin() {
    const cfg = window.ARI_ADMIN_CAL;
    if (!cfg || !cfg.icsListUrl || !cfg.canManage) return;

    const listEl = document.getElementById('admin-cal-ics-feed-list');
    const emptyEl = document.getElementById('admin-cal-ics-empty');
    const addForm = document.getElementById('admin-cal-ics-add-form');
    if (!listEl) return;

    // Listen for instrument selector change (fired by admin_calendar.js too)
    const instrSel = document.getElementById('admin-cal-instr');
    if (instrSel) {
        instrSel.addEventListener('change', () => {
            _adminIcsLoad(instrSel.value);
        });
        // Load for currently selected instrument on page load
        if (instrSel.value) _adminIcsLoad(instrSel.value);
    }

    // Add-form submit
    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const instrument = _adminIcsLoaded;
            if (!instrument) return;
            const name  = document.getElementById('admin-ics-name').value.trim();
            const url   = document.getElementById('admin-ics-url').value.trim();
            const color = document.getElementById('admin-ics-color').value;
            if (!name || !url) return;
            const btn = addForm.querySelector('button[type=submit]');
            btn.disabled = true;
            btn.textContent = 'Syncing…';
            try {
                const data = await _post(cfg.icsAddUrl, {
                    instrument, name, url, color,
                });
                if (data.ok) {
                    _toast('Feed added and synced.', true);
                    _renderFeeds(data.feeds, listEl, emptyEl, 'admin');
                    addForm.reset();
                    document.getElementById('admin-ics-color').value = '#7b5ea7';
                    const wrap = addForm.closest('details');
                    if (wrap) wrap.removeAttribute('open');
                } else {
                    _toast(data.error || 'Failed to add feed.', false);
                }
            } catch {
                _toast('Network error.', false);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Add & Sync';
            }
        });
    }

    // Delegated: refresh / delete
    listEl.addEventListener('click', async (e) => {
        const refreshBtn = e.target.closest('.ari-cal-ics-btn-refresh');
        const deleteBtn  = e.target.closest('.ari-cal-ics-btn-delete');
        if (!refreshBtn && !deleteBtn) return;

        const instrument = _adminIcsLoaded;
        const feedId = (refreshBtn || deleteBtn).dataset.feedId;

        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fa-solid fa-rotate fa-spin"></i>';
            try {
                const data = await _post(cfg.icsRefreshUrl, {
                    instrument, feed_id: feedId,
                });
                if (data.ok) {
                    _toast('Feed refreshed.', true);
                    _renderFeeds(data.feeds, listEl, emptyEl, 'admin');
                } else {
                    _toast(data.error || 'Refresh failed.', false);
                    refreshBtn.disabled = false;
                    refreshBtn.innerHTML =
                        '<i class="fa-solid fa-rotate"></i>';
                }
            } catch {
                _toast('Network error.', false);
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fa-solid fa-rotate"></i>';
            }
        }

        if (deleteBtn) {
            if (!confirm('Remove this external calendar?')) return;
            deleteBtn.disabled = true;
            try {
                const data = await _post(cfg.icsDeleteUrl, {
                    instrument, feed_id: feedId,
                });
                if (data.ok) {
                    _toast('Feed removed.', true);
                    _renderFeeds(data.feeds, listEl, emptyEl, 'admin');
                } else {
                    _toast(data.error || 'Delete failed.', false);
                    deleteBtn.disabled = false;
                }
            } catch {
                _toast('Network error.', false);
                deleteBtn.disabled = false;
            }
        }
    });
}

// ── bootstrap ─────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    if (window.ARI_CALENDAR)  _initUser();
    if (window.ARI_ADMIN_CAL) _initAdmin();
});
