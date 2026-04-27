// user_portal_users.js - directory + send-message
(function () {
  'use strict';
  var tbody = document.querySelector('#upm-users-table tbody');
  var search = document.getElementById('upm-search');
  var countEl = document.getElementById('upm-count');
  var modal = document.getElementById('upm-send-modal');
  var form = document.getElementById('upm-send-form');
  var recipientInput = document.getElementById('upm-recipient');
  var subjectInput = document.getElementById('upm-subject');
  var bodyInput = document.getElementById('upm-body');
  var status = document.getElementById('upm-send-status');
  var sendTitle = document.getElementById('upm-send-title');
  var allUsers = [];

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function render(filter) {
    var f = (filter || '').trim().toLowerCase();
    var rows = allUsers.filter(function (u) {
      if (!f) return true;
      var bag = [u.username, u.first_names, u.last_name,
                 u.email, (u.groups || []).join(' ')]
                 .join(' ').toLowerCase();
      return bag.indexOf(f) !== -1;
    });
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="upm-empty">'
        + 'No users found.</td></tr>';
    } else {
      tbody.innerHTML = rows.map(function (u) {
        var full = [u.first_names, u.last_name].filter(Boolean)
          .join(' ');
        var email = u.email
          ? '<a href="mailto:' + escapeHtml(u.email) + '">'
            + escapeHtml(u.email) + '</a>'
          : '<span class="upm-empty">—</span>';
        var groups = (u.groups || []).map(function (g) {
          return '<span class="ari-pill">' + escapeHtml(g)
            + '</span>';
        }).join(' ');
        var actions = u.is_self
          ? '<span class="upm-empty">(you)</span>'
          : '<button type="button" class="ari-btn ari-btn--small'
            + ' upm-msg-btn" data-username="'
            + escapeHtml(u.username) + '">'
            + '<i class="fa-solid fa-envelope"></i> Message'
            + '</button>';
        return '<tr><td>' + escapeHtml(u.username) + '</td>'
          + '<td>' + escapeHtml(full || '—') + '</td>'
          + '<td>' + email + '</td>'
          + '<td>' + (groups || '—') + '</td>'
          + '<td>' + actions + '</td></tr>';
      }).join('');
    }
    countEl.textContent = rows.length + ' user'
      + (rows.length === 1 ? '' : 's');
  }

  function openModal(username) {
    recipientInput.value = username;
    subjectInput.value = '';
    bodyInput.value = '';
    status.textContent = '';
    status.className = 'upm-form-status';
    sendTitle.textContent = 'Send message to ' + username;
    modal.hidden = false;
    setTimeout(function () { bodyInput.focus(); }, 50);
  }

  function closeModal() { modal.hidden = true; }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.upm-msg-btn');
    if (btn) { openModal(btn.dataset.username); return; }
    if (e.target.matches('[data-upm-close]')) { closeModal(); }
  });

  search.addEventListener('input', function () {
    render(search.value);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    status.textContent = 'Sending...';
    status.className = 'upm-form-status';
    fetch('/api/messages/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recipient: recipientInput.value,
        subject: subjectInput.value,
        body: bodyInput.value,
      }),
    }).then(function (r) { return r.json(); })
      .then(function (j) {
        if (j && j.success) {
          status.textContent = 'Message sent.';
          status.className = 'upm-form-status is-success';
          setTimeout(closeModal, 800);
        } else {
          status.textContent = (j && j.error) || 'Send failed.';
          status.className = 'upm-form-status is-error';
        }
      })
      .catch(function () {
        status.textContent = 'Network error.';
        status.className = 'upm-form-status is-error';
      });
  });

  fetch('/api/users/directory').then(function (r) {
    return r.json();
  }).then(function (j) {
    allUsers = (j && j.success && j.users) || [];
    render('');
  }).catch(function () {
    tbody.innerHTML = '<tr><td colspan="5" class="upm-empty">'
      + 'Failed to load users.</td></tr>';
  });
})();
