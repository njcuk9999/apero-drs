// user_portal_messages.js - inbox / sent / view / compose / flag
(function () {
  'use strict';
  var page = document.querySelector('.upm-page');
  var SELF = (page && page.dataset.username) || '';
  var mailbox = document.getElementById('upm-mailbox');
  var inboxBadge = document.getElementById('upm-inbox-badge');
  var tabs = document.querySelectorAll('.upm-tab[data-upm-box]');
  var composeBtn = document.getElementById('upm-compose-btn');
  var sendModal = document.getElementById('upm-send-modal');
  var sendForm = document.getElementById('upm-send-form');
  var recipientInput = document.getElementById('upm-recipient');
  var subjectInput = document.getElementById('upm-subject');
  var bodyInput = document.getElementById('upm-body');
  var sendStatus = document.getElementById('upm-send-status');
  var datalist = document.getElementById('upm-user-list');

  var viewModal = document.getElementById('upm-view-modal');
  var viewSubject = document.getElementById('upm-view-subject');
  var viewMeta = document.getElementById('upm-view-meta');
  var viewBody = document.getElementById('upm-view-body');
  var viewStatus = document.getElementById('upm-view-status');
  var viewFlag = document.getElementById('upm-view-flag');
  var viewDelete = document.getElementById('upm-view-delete');
  var viewReply = document.getElementById('upm-view-reply');
  var currentBox = 'inbox';
  var currentMsg = null;

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

  function loadUsers() {
    fetch('/api/users/directory').then(function (r) {
      return r.json();
    }).then(function (j) {
      var users = (j && j.success && j.users) || [];
      datalist.innerHTML = users.filter(function (u) {
        return !u.is_self;
      }).map(function (u) {
        return '<option value="' + escapeHtml(u.username)
          + '">' + escapeHtml(
            [u.first_names, u.last_name].filter(Boolean).join(' '))
          + '</option>';
      }).join('');
    }).catch(function () { /* non-fatal */ });
  }

  function renderList(box, msgs) {
    if (!msgs.length) {
      mailbox.innerHTML = '<div class="upm-empty">'
        + 'No messages.</div>';
      return;
    }
    mailbox.innerHTML = msgs.map(function (m) {
      var who = box === 'inbox' ? m.sender : m.recipient;
      var unread = (box === 'inbox' && !m.read_at)
        ? ' is-unread' : '';
      return '<div class="upm-row' + unread
        + '" data-msg-id="' + escapeHtml(m.id)
        + '" data-box="' + box + '">'
        + '<div class="upm-row__who">' + escapeHtml(who) + '</div>'
        + '<div class="upm-row__subject">'
        + escapeHtml(m.subject || '(no subject)') + '</div>'
        + '<div class="upm-row__date">'
        + escapeHtml(fmtDate(m.created_at)) + '</div>'
        + '</div>';
    }).join('');
  }

  function refreshUnreadBadge() {
    fetch('/api/notifications/unread-count').then(function (r) {
      return r.json();
    }).then(function (j) {
      if (!j || !j.success) return;
      var n = j.unread_messages || 0;
      inboxBadge.textContent = n > 0 ? String(n) : '';
    }).catch(function () {});
  }

  function loadBox(box) {
    currentBox = box;
    tabs.forEach(function (t) {
      var on = t.dataset.upmBox === box;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    mailbox.innerHTML = '<div class="upm-empty">Loading...</div>';
    fetch('/api/messages/list?box=' + encodeURIComponent(box))
      .then(function (r) { return r.json(); })
      .then(function (j) {
        renderList(box, (j && j.messages) || []);
        refreshUnreadBadge();
      })
      .catch(function () {
        mailbox.innerHTML = '<div class="upm-empty">'
          + 'Failed to load messages.</div>';
      });
  }

  function openMsg(id) {
    fetch('/api/messages/' + encodeURIComponent(id))
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j || !j.success) {
          alert((j && j.error) || 'Failed to load message');
          return;
        }
        currentMsg = j.message;
        viewSubject.textContent = currentMsg.subject
          || '(no subject)';
        viewMeta.innerHTML = '<strong>From:</strong> '
          + escapeHtml(currentMsg.sender) + ' &nbsp; '
          + '<strong>To:</strong> '
          + escapeHtml(currentMsg.recipient) + ' &nbsp; '
          + '<strong>Sent:</strong> '
          + escapeHtml(fmtDate(currentMsg.created_at))
          + (j.flag
              ? ' &nbsp; <span class="ari-pill">'
                + 'Flagged as issue #'
                + escapeHtml(j.flag.issue_id || '?')
                + '</span>'
              : '');
        viewBody.textContent = currentMsg.body || '';
        viewStatus.textContent = '';
        viewStatus.className = 'upm-form-status';
        viewModal.hidden = false;
        // refresh list to clear unread state
        loadBox(currentBox);
      });
  }

  function closeAllModals() {
    sendModal.hidden = true;
    viewModal.hidden = true;
  }

  document.addEventListener('click', function (e) {
    if (e.target.matches('[data-upm-close]')) {
      closeAllModals();
      return;
    }
    var row = e.target.closest('.upm-row');
    if (row) { openMsg(row.dataset.msgId); return; }
  });

  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      loadBox(t.dataset.upmBox);
    });
  });

  composeBtn.addEventListener('click', function () {
    recipientInput.value = '';
    subjectInput.value = '';
    bodyInput.value = '';
    sendStatus.textContent = '';
    sendStatus.className = 'upm-form-status';
    sendModal.hidden = false;
    setTimeout(function () { recipientInput.focus(); }, 50);
  });

  sendForm.addEventListener('submit', function (e) {
    e.preventDefault();
    sendStatus.textContent = 'Sending...';
    sendStatus.className = 'upm-form-status';
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
          sendStatus.textContent = 'Message sent.';
          sendStatus.className = 'upm-form-status is-success';
          setTimeout(function () {
            sendModal.hidden = true;
            loadBox(currentBox);
          }, 600);
        } else {
          sendStatus.textContent = (j && j.error)
            || 'Send failed.';
          sendStatus.className = 'upm-form-status is-error';
        }
      });
  });

  viewReply.addEventListener('click', function () {
    if (!currentMsg) return;
    var other = currentMsg.sender === SELF
      ? currentMsg.recipient : currentMsg.sender;
    recipientInput.value = other;
    subjectInput.value = (currentMsg.subject || '')
      .replace(/^Re:\s*/i, '');
    subjectInput.value = 'Re: ' + subjectInput.value;
    bodyInput.value = '\n\n---\n'
      + (currentMsg.body || '').split('\n')
        .map(function (l) { return '> ' + l; }).join('\n');
    viewModal.hidden = true;
    sendModal.hidden = false;
    setTimeout(function () { bodyInput.focus(); }, 50);
  });

  viewDelete.addEventListener('click', function () {
    if (!currentMsg) return;
    if (!confirm('Delete this message?')) return;
    fetch('/api/messages/' + encodeURIComponent(currentMsg.id)
          + '/delete', { method: 'POST' })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (j && j.success) {
          viewModal.hidden = true;
          loadBox(currentBox);
        } else {
          viewStatus.textContent = (j && j.error)
            || 'Delete failed.';
          viewStatus.className = 'upm-form-status is-error';
        }
      });
  });

  viewFlag.addEventListener('click', function () {
    if (!currentMsg) return;
    if (!confirm('Flag this message into the Issues tracker?'
                 + ' A monitor will be able to review it.'))
      return;
    fetch('/api/messages/' + encodeURIComponent(currentMsg.id)
          + '/flag-as-issue', { method: 'POST' })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (j && j.success) {
          viewStatus.textContent = j.issue_id
            ? 'Flagged as issue #' + j.issue_id
            : 'Flagged.';
          viewStatus.className = 'upm-form-status is-success';
        } else {
          viewStatus.textContent = (j && j.error)
            || 'Flag failed.';
          viewStatus.className = 'upm-form-status is-error';
        }
      });
  });

  loadUsers();
  loadBox('inbox');
})();
