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
  var recipientQueryInput = document.getElementById('upm-recipient-query');
  var recipientSuggest = document.getElementById('upm-recipient-suggest');
  var subjectInput = document.getElementById('upm-subject');
  var bodyInput = document.getElementById('upm-body');
  var sendStatus = document.getElementById('upm-send-status');

  var viewModal = document.getElementById('upm-view-modal');
  var detailEmpty = document.getElementById('upm-detail-empty');
  var detailView = document.getElementById('upm-detail-view');
  var detailBack = document.getElementById('upm-detail-back');
  var listPane = document.getElementById('upm-list-pane');
  var detailPane = document.getElementById('upm-detail-pane');
  var viewSubject = document.getElementById('upm-view-subject');
  var viewMeta = document.getElementById('upm-view-meta');
  var viewBody = document.getElementById('upm-view-body');
  var viewStatus = document.getElementById('upm-view-status');
  var viewFlag = document.getElementById('upm-view-flag');
  var viewDelete = document.getElementById('upm-view-delete');
  var viewMarkUnread = document.getElementById('upm-view-mark-unread');
  var viewReply = document.getElementById('upm-view-reply');
  var markAllReadBtn = document.getElementById('upm-mark-all-read');
  var deleteAllBtn = document.getElementById('upm-delete-all');
  var pageSizeSelect = document.getElementById('upm-page-size');
  var prevPageBtn = document.getElementById('upm-prev-page');
  var nextPageBtn = document.getElementById('upm-next-page');
  var pageInfo = document.getElementById('upm-page-info');
  var currentBox = 'inbox';
  var currentMsg = null;
  var currentItems = [];
  var currentPage = 1;
  var pendingOpenMid = null;
  var pendingComposeTo = '';
  var pendingComposeSubject = '';
  var composeUsers = [];

  try {
    var params = new URLSearchParams(window.location.search || '');
    pendingOpenMid = params.get('mid') || params.get('message_id');
    pendingComposeTo = params.get('compose') || '';
    pendingComposeSubject = params.get('subject') || '';
  } catch (e) {
    pendingOpenMid = null;
    pendingComposeTo = '';
    pendingComposeSubject = '';
  }

  function openComposeModal(recipient, subject, body) {
    setRecipient(recipient || '');
    subjectInput.value = subject || '';
    bodyInput.value = body || '';
    sendStatus.textContent = '';
    sendStatus.className = 'upm-form-status';
    sendModal.hidden = false;
    setTimeout(function () {
      if (recipient) {
        bodyInput.focus();
      } else if (recipientQueryInput) {
        recipientQueryInput.focus();
      }
    }, 50);
  }

  function normalized(s) {
    return String(s == null ? '' : s).trim().toLowerCase();
  }

  function setRecipient(username) {
    var uname = String(username || '').trim();
    if (recipientInput) recipientInput.value = uname;
    if (!recipientQueryInput) return;
    if (!uname) {
      recipientQueryInput.value = '';
      return;
    }
    var found = composeUsers.find(function (u) {
      return String(u.username || '') === uname;
    });
    if (!found) {
      recipientQueryInput.value = uname;
      return;
    }
    var full = String(found.full_name || '').trim();
    recipientQueryInput.value = full ? (uname + ' - ' + full) : uname;
  }

  function hideRecipientSuggestions() {
    if (!recipientSuggest) return;
    recipientSuggest.hidden = true;
    recipientSuggest.innerHTML = '';
  }

  function renderRecipientSuggestions(query) {
    if (!recipientSuggest) return;
    var q = normalized(query);
    if (!q) {
      hideRecipientSuggestions();
      return;
    }
    var matches = composeUsers.filter(function (u) {
      var bag = [u.username, u.full_name, u.first_names,
                 u.last_name, u.primary_institution,
                 (u.institutions || []).join(' ')]
                 .join(' ').toLowerCase();
      return bag.indexOf(q) !== -1;
    }).slice(0, 25);

    if (!matches.length) {
      recipientSuggest.innerHTML = '<div class="upm-typeahead-empty">'
        + 'No matching users.</div>';
      recipientSuggest.hidden = false;
      return;
    }

    recipientSuggest.innerHTML = matches.map(function (u) {
      var name = String(u.full_name || '').trim() || 'No name';
      return '<button type="button" class="upm-typeahead-item"'
        + ' data-username="' + escapeHtml(u.username) + '">'
        + '<span class="upm-typeahead-item__main">'
        + escapeHtml(u.username) + '</span>'
        + '<span class="upm-typeahead-item__sub">'
        + escapeHtml(name) + '</span>'
        + '</button>';
    }).join('');
    recipientSuggest.hidden = false;
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function fmtDate(value) {
    if (value == null || value === '') return '';
    var parsed = value;
    if (typeof parsed === 'string') {
      parsed = parsed.trim();
      if (!parsed) return '';
      if (/^-?\d+(\.\d+)?$/.test(parsed)) {
        parsed = Number(parsed);
      }
    }
    var dt;
    if (typeof parsed === 'number' && isFinite(parsed)) {
      if (Math.abs(parsed) < 1e12) {
        parsed = parsed * 1000;
      }
      dt = new Date(parsed);
    } else {
      dt = new Date(parsed);
    }
    if (isNaN(dt.getTime())) {
      return String(value);
    }
    return dt.toLocaleString();
  }

  function loadUsers() {
    fetch('/api/users/directory').then(function (r) {
      return r.json();
    }).then(function (j) {
      composeUsers = ((j && j.success && j.users) || []).filter(
        function (u) {
          return !u.is_self;
        }
      );
      // If compose was prefilled before users loaded, refresh
      // display label once we have directory metadata.
      if (pendingComposeTo) {
        setRecipient(pendingComposeTo);
      }
    }).catch(function () { /* non-fatal */ });
  }

  if (recipientQueryInput) {
    recipientQueryInput.addEventListener('input', function () {
      if (recipientInput) recipientInput.value = '';
      renderRecipientSuggestions(recipientQueryInput.value);
    });
    recipientQueryInput.addEventListener('focus', function () {
      renderRecipientSuggestions(recipientQueryInput.value);
    });
    recipientQueryInput.addEventListener('blur', function () {
      setTimeout(hideRecipientSuggestions, 120);
    });
    recipientQueryInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') hideRecipientSuggestions();
    });
  }

  if (recipientSuggest) {
    recipientSuggest.addEventListener('click', function (e) {
      var item = e.target.closest('.upm-typeahead-item');
      if (!item) return;
      e.preventDefault();
      setRecipient(item.dataset.username || '');
      hideRecipientSuggestions();
      if (subjectInput) subjectInput.focus();
    });
  }

  document.addEventListener('click', function (e) {
    if (!recipientSuggest || recipientSuggest.hidden) return;
    if (recipientSuggest.contains(e.target)) return;
    if (recipientQueryInput && recipientQueryInput.contains(e.target)) {
      return;
    }
    hideRecipientSuggestions();
  });

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
      var subject = m.subject || '(no subject)';
      return '<div class="upm-row' + unread
        + '" data-msg-id="' + escapeHtml(m.id)
        + '" data-box="' + box + '">'
        + '<div class="upm-row__head">'
        + '<span class="upm-row__who">' + escapeHtml(who)
        + '</span> / '
        + '<span class="upm-row__subject">'
        + escapeHtml(subject) + '</span>'
        + '</div>'
        + '<div class="upm-row__date">'
        + escapeHtml(fmtDate(m.created_at)) + '</div>'
        + '</div>';
    }).join('');
  }

  function getPageSize() {
    var fallback = 10;
    if (!pageSizeSelect) return fallback;
    var value = Number(pageSizeSelect.value || fallback);
    if (!isFinite(value) || value <= 0) return fallback;
    return value;
  }

  function getPageCount() {
    var pageSize = getPageSize();
    var total = currentItems.length;
    if (total <= 0) return 1;
    return Math.max(1, Math.ceil(total / pageSize));
  }

  function renderCurrentPage() {
    var total = currentItems.length;
    var pageSize = getPageSize();
    var pageCount = getPageCount();
    currentPage = Math.min(Math.max(currentPage, 1), pageCount);
    var start = (currentPage - 1) * pageSize;
    var end = Math.min(start + pageSize, total);
    var subset = currentItems.slice(start, end);
    renderList(currentBox, subset);
    if (prevPageBtn) prevPageBtn.disabled = currentPage <= 1;
    if (nextPageBtn) nextPageBtn.disabled = currentPage >= pageCount;
    if (pageInfo) {
      if (total <= 0) {
        pageInfo.textContent = '0 messages';
      } else {
        pageInfo.textContent = String(start + 1)
          + '-' + String(end)
          + ' of ' + String(total);
      }
    }
  }

  function updateBulkButtons(box) {
    if (markAllReadBtn) {
      markAllReadBtn.disabled = (box !== 'inbox');
    }
    if (deleteAllBtn) {
      deleteAllBtn.textContent = (box === 'sent')
        ? 'Delete all sent'
        : 'Delete all inbox';
    }
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
    updateBulkButtons(box);
    tabs.forEach(function (t) {
      var on = t.dataset.upmBox === box;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    mailbox.innerHTML = '<div class="upm-empty">Loading...</div>';
    fetch('/api/messages/list?box=' + encodeURIComponent(box))
      .then(function (r) { return r.json(); })
      .then(function (j) {
        currentItems = (j && (j.items || j.messages)) || [];
        renderCurrentPage();
        refreshUnreadBadge();
        if (pendingOpenMid) {
          var mid = pendingOpenMid;
          pendingOpenMid = null;
          openMsg(mid);
        }
      })
      .catch(function () {
        currentItems = [];
        renderCurrentPage();
        mailbox.innerHTML = '<div class="upm-empty">'
          + 'Failed to load messages.</div>';
      });
  }

  function postJson(url, payload) {
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload || {}),
    }).then(function (r) {
      return r.json();
    });
  }

  function showDetail(show) {
    if (detailView) detailView.hidden = !show;
    if (detailEmpty) detailEmpty.hidden = !!show;
    // Mobile: when a message is open we hide the list and show
    // the detail full-width; when no message is open we show the
    // list. CSS controls the actual layout via .is-showing-detail.
    if (detailPane) {
      detailPane.classList.toggle('is-active', !!show);
    }
    if (listPane) {
      listPane.classList.toggle('is-hidden-mobile', !!show);
    }
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
        if (viewMarkUnread) {
          var canMarkUnread = currentMsg.recipient === SELF;
          viewMarkUnread.hidden = !canMarkUnread;
          viewMarkUnread.disabled = !canMarkUnread
            || !currentMsg.read_at;
        }
        showDetail(true);
        // refresh list to clear unread state
        loadBox(currentBox);
        // Ask the global bell to refresh: the server clears the
        // matching 'message' notification when the recipient
        // opens the message, so the badge can drop right away
        // instead of waiting for the next 30s poll.
        try {
          window.dispatchEvent(new Event('ari:notif-refresh'));
        } catch (e) { /* IE compat - ignore */ }
      });
  }

  if (viewMarkUnread) {
    viewMarkUnread.addEventListener('click', function () {
      if (!currentMsg) return;
      viewMarkUnread.disabled = true;
      fetch('/api/messages/' + encodeURIComponent(currentMsg.id)
            + '/mark-unread', { method: 'POST' })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (!j || !j.success) {
            viewStatus.textContent = (j && j.error)
              || 'Mark unread failed.';
            viewStatus.className = 'upm-form-status is-error';
            return;
          }
          currentMsg.read_at = null;
          viewMarkUnread.disabled = true;
          viewStatus.textContent = 'Marked as unread.';
          viewStatus.className = 'upm-form-status is-success';
          loadBox(currentBox);
          try {
            window.dispatchEvent(new Event('ari:notif-refresh'));
          } catch (e) { /* ignore */ }
        })
        .catch(function () {
          viewStatus.textContent = 'Mark unread failed.';
          viewStatus.className = 'upm-form-status is-error';
        });
    });
  }

  function closeAllModals() {
    if (sendModal) sendModal.hidden = true;
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
      currentPage = 1;
      loadBox(t.dataset.upmBox);
    });
  });

  if (pageSizeSelect) {
    pageSizeSelect.addEventListener('change', function () {
      currentPage = 1;
      renderCurrentPage();
    });
  }

  if (prevPageBtn) {
    prevPageBtn.addEventListener('click', function () {
      currentPage -= 1;
      renderCurrentPage();
    });
  }

  if (nextPageBtn) {
    nextPageBtn.addEventListener('click', function () {
      currentPage += 1;
      renderCurrentPage();
    });
  }

  composeBtn.addEventListener('click', function () {
    openComposeModal('', '', '');
  });

  sendForm.addEventListener('submit', function (e) {
    e.preventDefault();
    if ((!recipientInput || !recipientInput.value)
        && recipientQueryInput && composeUsers.length) {
      var query = normalized(recipientQueryInput.value);
      var exact = composeUsers.find(function (u) {
        return normalized(u.username) === query;
      });
      if (exact) {
        setRecipient(exact.username);
      }
    }
    if (!recipientInput || !recipientInput.value) {
      sendStatus.textContent = 'Please select a recipient.';
      sendStatus.className = 'upm-form-status is-error';
      if (recipientQueryInput) recipientQueryInput.focus();
      return;
    }
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
    setRecipient(other);
    subjectInput.value = (currentMsg.subject || '')
      .replace(/^Re:\s*/i, '');
    subjectInput.value = 'Re: ' + subjectInput.value;
    bodyInput.value = '\n\n---\n'
      + (currentMsg.body || '').split('\n')
        .map(function (l) { return '> ' + l; }).join('\n');
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
          showDetail(false);
          currentMsg = null;
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

  if (detailBack) {
    detailBack.addEventListener('click', function () {
      showDetail(false);
      currentMsg = null;
    });
  }

  if (markAllReadBtn) {
    markAllReadBtn.addEventListener('click', function () {
      if (currentBox !== 'inbox') return;
      markAllReadBtn.disabled = true;
      postJson('/api/messages/mark-all-read', { box: 'inbox' })
        .then(function (j) {
          if (!j || !j.success) {
            alert((j && j.error) || 'Failed to mark all read.');
            return;
          }
          loadBox(currentBox);
        })
        .catch(function () {
          alert('Failed to mark all read.');
        })
        .finally(function () {
          updateBulkButtons(currentBox);
        });
    });
  }

  if (deleteAllBtn) {
    deleteAllBtn.addEventListener('click', function () {
      var target = currentBox === 'sent' ? 'sent' : 'inbox';
      var question = (target === 'sent')
        ? 'Delete every message in Sent?'
        : 'Delete every message in Inbox?';
      if (!confirm(question)) return;
      deleteAllBtn.disabled = true;
      postJson('/api/messages/delete-all', { box: target })
        .then(function (j) {
          if (!j || !j.success) {
            alert((j && j.error) || 'Failed to delete all.');
            return;
          }
          showDetail(false);
          currentMsg = null;
          loadBox(currentBox);
        })
        .catch(function () {
          alert('Failed to delete all.');
        })
        .finally(function () {
          updateBulkButtons(currentBox);
        });
    });
  }

  loadUsers();
  loadBox('inbox');
  if (pendingComposeTo) {
    openComposeModal(
      pendingComposeTo,
      pendingComposeSubject,
      ''
    );
  }
})();
