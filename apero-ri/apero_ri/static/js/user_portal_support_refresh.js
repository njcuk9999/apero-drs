// user_portal_support_refresh.js
// Periodically re-fetches the support page and swaps in the
// dynamic content (.ari-up-shell wrapper) so contact info,
// admins/monitors etc. stay current without a full reload.
(function () {
  'use strict';
  var POLL_MS = 90000;
  var INDICATOR_ID = 'ups-refresh-indicator';

  function ensureIndicator() {
    if (document.getElementById(INDICATOR_ID)) return;
    var header = document.querySelector('.ari-page-header');
    if (!header) return;
    var span = document.createElement('span');
    span.id = INDICATOR_ID;
    span.style.cssText = 'font-size:0.8rem;color:'
      + 'var(--ari-text-muted,#6b7785);margin-left:0.5rem;';
    span.textContent = 'auto-updates every 90s';
    header.appendChild(span);
  }

  function updateIndicator(text) {
    var el = document.getElementById(INDICATOR_ID);
    if (el) el.textContent = text;
  }

  function refresh() {
    fetch(window.location.pathname + '?_=' + Date.now(), {
      credentials: 'same-origin',
      headers: { 'X-Requested-With': 'fetch' },
    }).then(function (r) {
      if (!r.ok) throw new Error('http ' + r.status);
      return r.text();
    }).then(function (html) {
      var doc = new DOMParser()
        .parseFromString(html, 'text/html');
      var newShell = doc.querySelector('.ari-up-shell');
      var oldShell = document.querySelector('.ari-up-shell');
      if (!newShell || !oldShell) return;
      // Preserve currently-selected tab
      var activeTabIdx = -1;
      var activeTabs = oldShell.querySelectorAll(
        '.ari-sg-tab--active');
      if (activeTabs.length) {
        var allTabs = Array.prototype.slice.call(
          oldShell.querySelectorAll('.ari-sg-tab'));
        activeTabIdx = allTabs.indexOf(activeTabs[0]);
      }
      oldShell.innerHTML = newShell.innerHTML;
      // Restore tab state
      if (activeTabIdx >= 0) {
        var newTabs = oldShell.querySelectorAll('.ari-sg-tab');
        if (newTabs[activeTabIdx]) {
          newTabs[activeTabIdx].click();
        }
      }
      updateIndicator('updated '
        + new Date().toLocaleTimeString());
    }).catch(function () {
      updateIndicator('refresh failed - retrying...');
    });
  }

  ensureIndicator();
  setInterval(refresh, POLL_MS);
})();
