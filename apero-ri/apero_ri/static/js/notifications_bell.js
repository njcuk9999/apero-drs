// notifications_bell.js - global header bell + 30s poller +
// optional desktop popups (when channel pref allows + browser
// permission granted).
(function () {
  'use strict';
  var bell = document.getElementById('ari-notif-bell');
  if (!bell) return; // bell may be hidden (anonymous user)
  var badge = document.getElementById('ari-notif-badge');
  var panel = document.getElementById('ari-notif-panel');
  var listEl = document.getElementById('ari-notif-panel-list');
  var POLL_MS = 30000;
  var seenIds = new Set();
  var firstPoll = true;

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function setBadge(n) {
    if (!badge) return;
    if (!n || n <= 0) { badge.textContent = ''; return; }
    badge.textContent = n > 99 ? '99+' : String(n);
  }

  function renderPanel(items) {
    if (!items || !items.length) {
      listEl.innerHTML = '<div class="upm-empty">'
        + 'No new notifications.</div>';
      return;
    }
    listEl.innerHTML = items.map(function (n) {
      var unread = n.read_at ? '' : ' is-unread';
      var url = n.url || '/user_portal/notifications';
      return '<a class="ari-notif-panel__item' + unread + '"'
        + ' href="' + escapeHtml(url) + '"'
        + ' data-id="' + escapeHtml(n.id) + '">'
        + '<div class="ari-notif-panel__title">'
        + escapeHtml(n.title) + '</div>'
        + '<div class="ari-notif-panel__body">'
        + escapeHtml(n.body || '') + '</div></a>';
    }).join('');
  }

  function showDesktop(item) {
    if (typeof Notification === 'undefined') return;
    if (Notification.permission !== 'granted') return;
    try {
      var n = new Notification(item.title || 'ARI', {
        body: item.body || '',
        tag: 'ari-' + item.id,
      });
      n.onclick = function () {
        window.focus();
        if (item.url) window.location.href = item.url;
      };
    } catch (e) { /* ignore */ }
  }

  function pollUnread() {
    fetch('/api/notifications/unread-count', {
      credentials: 'same-origin',
    }).then(function (r) {
      if (!r.ok) throw new Error('http ' + r.status);
      return r.json();
    }).then(function (j) {
      if (!j || !j.success) return;
      // Bell badge counts notifications only. Each new message
      // also emits a notification, so the message would otherwise
      // be counted twice (once as notif, once as unread message).
      setBadge(j.unread || 0);
      // also fetch recent items so we can fire desktop popups
      // for items we have not seen yet
      return fetch('/api/notifications/list?limit=10').then(
        function (r) { return r.json(); });
    }).then(function (j) {
      if (!j || !j.success) return;
      var items = j.items || j.notifications || [];
      if (panel && panel.classList.contains('is-open')) {
        renderPanel(items);
      }
      if (firstPoll) {
        items.forEach(function (it) { seenIds.add(it.id); });
        firstPoll = false;
        return;
      }
      items.forEach(function (it) {
        if (seenIds.has(it.id)) return;
        seenIds.add(it.id);
        if (!it.read_at) showDesktop(it);
      });
    }).catch(function () { /* network blip - ignore */ });
  }

  function togglePanel() {
    if (!panel) return;
    var open = panel.classList.toggle('is-open');
    if (open) {
      listEl.innerHTML = '<div class="upm-empty">Loading...</div>';
      fetch('/api/notifications/list?limit=10').then(function (r) {
        return r.json();
      }).then(function (j) {
        renderPanel(
          (j && (j.items || j.notifications)) || []);
      });
    }
  }

  bell.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    togglePanel();
  });

  document.addEventListener('click', function (e) {
    if (!panel || !panel.classList.contains('is-open')) return;
    if (panel.contains(e.target) || bell.contains(e.target)) {
      return;
    }
    panel.classList.remove('is-open');
  });

  // "Clear all" button in the dropdown header: dismisses every
  // notification for the current user.
  var clearBtn = document.getElementById('ari-notif-clear-all');
  if (clearBtn) {
    clearBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      clearBtn.disabled = true;
      fetch('/api/notifications/dismiss', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: [] }),
      }).then(function (r) { return r.json(); })
        .then(function () {
          setBadge(0);
          renderPanel([]);
          pollUnread();
        })
        .catch(function () { /* ignore */ })
        .then(function () { clearBtn.disabled = false; });
    });
  }

  // Allow other pages (e.g. the messages page after a message has
  // been opened and its matching notification cleared on the
  // server) to ask the bell to refresh immediately rather than
  // waiting for the 30s poll.
  window.addEventListener('ari:notif-refresh', function () {
    pollUnread();
  });

  pollUnread();
  setInterval(pollUnread, POLL_MS);
})();
