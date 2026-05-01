// user_portal_notifications.js - manage page (list + prefs)
(function () {
  'use strict';
  var listEl = document.getElementById('upn-list');
  var prefsEl = document.getElementById('upn-prefs');
  var statusEl = document.getElementById('upn-prefs-status');
  var markAll = document.getElementById('upn-mark-all-read');
  var dismissAll = document.getElementById('upn-dismiss-all');
  var grantBtn = document.getElementById('upn-grant-browser');
  var browserStatus = document.getElementById('upn-browser-status');

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function fmtDate(iso) {
    if (!iso) return '';
    try { return new Date(iso).toLocaleString(); }
    catch (e) { return iso; }
  }
  var ICONS = {
    message: 'fa-envelope',
    calendar: 'fa-calendar',
    issue: 'fa-flag',
    admin_health: 'fa-heart-pulse',
    fav_object: 'fa-star',
    system: 'fa-circle-info',
  };

  function renderList(items) {
    if (!items.length) {
      listEl.innerHTML = '<div class="upm-empty">'
        + 'No notifications.</div>';
      return;
    }
    listEl.innerHTML = items.map(function (n) {
      var icon = ICONS[n.channel] || 'fa-bell';
      var unread = n.read_at ? '' : ' is-unread';
      var url = n.url || '#';
      return '<div class="upn-item' + unread
        + '" data-id="' + escapeHtml(n.id) + '">'
        + '<div class="upn-item__chan">'
        + '<i class="fa-solid ' + icon + '"></i></div>'
        + '<div><div class="upn-item__title">'
        + (url !== '#'
            ? '<a href="' + escapeHtml(url) + '">'
              + escapeHtml(n.title) + '</a>'
            : escapeHtml(n.title))
        + '</div><div class="upn-item__body">'
        + escapeHtml(n.body || '') + '</div></div>'
        + '<div class="upn-item__date">'
        + escapeHtml(fmtDate(n.created_at)) + '</div>'
        + '<div class="upn-item__actions">'
        + (n.read_at ? ''
            : '<button class="ari-btn ari-btn--small"'
              + ' data-action="read" data-id="'
              + escapeHtml(n.id) + '">'
              + '<i class="fa-solid fa-check"></i> Read</button>')
        + '<button class="ari-btn ari-btn--small ari-btn--danger"'
        + ' data-action="dismiss" data-id="'
        + escapeHtml(n.id) + '">'
        + '<i class="fa-solid fa-xmark"></i> Dismiss</button>'
        + '</div></div>';
    }).join('');
  }

  function loadList() {
    fetch('/api/notifications/list?limit=100').then(function (r) {
      return r.json();
    }).then(function (j) {
      renderList((j && (j.items || j.notifications)) || []);
    }).catch(function () {
      listEl.innerHTML = '<div class="upm-empty">'
        + 'Failed to load notifications.</div>';
    });
  }

  function renderPrefs(prefs) {
    var channels = ['message', 'calendar', 'issue',
                    'admin_health', 'fav_object'];
    prefsEl.innerHTML = channels.map(function (c) {
      var p = prefs[c] || { enabled: 1, browser_popups: 0 };
      var en = p.enabled ? 'checked' : '';
      var pop = p.browser_popups ? 'checked' : '';
      return '<div class="upn-pref" data-channel="' + c + '">'
        + '<div class="upn-pref__name">' + c.replace('_', ' ')
        + '</div>'
        + '<label class="upn-pref__row">'
        + '<input type="checkbox" data-pref="enabled" ' + en + '>'
        + ' Enabled in app</label>'
        + '<label class="upn-pref__row">'
        + '<input type="checkbox" data-pref="popup" ' + pop + '>'
        + ' Desktop popup</label></div>';
    }).join('');
  }

  function loadPrefs() {
    fetch('/api/notifications/prefs').then(function (r) {
      return r.json();
    }).then(function (j) {
      renderPrefs((j && j.prefs) || {});
    });
  }

  prefsEl.addEventListener('change', function (e) {
    var card = e.target.closest('.upn-pref');
    if (!card) return;
    var ch = card.dataset.channel;
    var enabled = card.querySelector(
      '[data-pref="enabled"]').checked ? 1 : 0;
    var popup = card.querySelector(
      '[data-pref="popup"]').checked ? 1 : 0;
    statusEl.textContent = 'Saving...';
    statusEl.className = 'upm-form-status';
    fetch('/api/notifications/prefs/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: ch, enabled: enabled, browser_popups: popup,
      }),
    }).then(function (r) { return r.json(); })
      .then(function (j) {
        if (j && j.success) {
          statusEl.textContent = 'Saved.';
          statusEl.className = 'upm-form-status is-success';
        } else {
          statusEl.textContent = (j && j.error) || 'Save failed.';
          statusEl.className = 'upm-form-status is-error';
        }
      });
  });

  listEl.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-action]');
    if (!btn) return;
    var url = btn.dataset.action === 'read'
      ? '/api/notifications/mark-read'
      : '/api/notifications/dismiss';
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: [btn.dataset.id] }),
    }).then(loadList);
  });

  markAll.addEventListener('click', function () {
    fetch('/api/notifications/mark-read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    }).then(loadList);
  });

  dismissAll.addEventListener('click', function () {
    if (!confirm('Dismiss all notifications?')) return;
    fetch('/api/notifications/dismiss', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    }).then(loadList);
  });

  function refreshBrowserPerm() {
    if (typeof Notification === 'undefined') {
      browserStatus.textContent = 'not supported';
      grantBtn.disabled = true;
      return;
    }
    browserStatus.textContent = Notification.permission;
    grantBtn.disabled = (Notification.permission === 'granted');
  }
  grantBtn.addEventListener('click', function () {
    if (typeof Notification === 'undefined') return;
    Notification.requestPermission().then(refreshBrowserPerm);
  });

  refreshBrowserPerm();
  loadPrefs();
  loadList();
})();
