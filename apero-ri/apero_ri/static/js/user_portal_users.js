// user_portal_users.js - directory + send-message
(function () {
  'use strict';
  var grid = document.getElementById('upm-users-grid');
  var search = document.getElementById('upm-search');
  var countEl = document.getElementById('upm-count');
  var groupFilterWrap = document.getElementById('upm-group-filter');
  var instrumentFilterWrap = document.getElementById('upm-instrument-filter');
  var modal = document.getElementById('upm-send-modal');
  var form = document.getElementById('upm-send-form');
  var recipientInput = document.getElementById('upm-recipient');
  var subjectInput = document.getElementById('upm-subject');
  var bodyInput = document.getElementById('upm-body');
  var status = document.getElementById('upm-send-status');
  var sendTitle = document.getElementById('upm-send-title');
  var allUsers = [];
  var allGroups = [];
  var allInstruments = [];
  var activeGroup = null;
  var activeInstrument = null;

  var GROUP_PRECEDENCE_FALLBACK = [
    'super_admin', 'admin', 'moderator', 'developer',
    'monitor', 'general', 'public'
  ];

  function getGroupOrder() {
    var ordered = (allGroups && allGroups.length)
      ? allGroups.slice()
      : GROUP_PRECEDENCE_FALLBACK.slice();
    if (ordered.indexOf('public') === -1) {
      ordered.push('public');
    }
    return ordered;
  }

  function getHighestGroup(user) {
    var groups = new Set(user.groups || []);
    var precedence = getGroupOrder();
    for (var i = 0; i < precedence.length; i++) {
      if (groups.has(precedence[i])) return precedence[i];
    }
    return 'public';
  }

  function getGroupStyle(groupName) {
    var precedence = getGroupOrder();
    var idx = precedence.indexOf(groupName);
    if (idx < 0) idx = precedence.length - 1;
    var hue = (210 + idx * 37) % 360;
    return {
      cardBg: 'hsl(' + hue + ', 72%, 96%)',
      cardBorder: 'hsl(' + hue + ', 42%, 72%)'
    };
  }

  function medalIcon(medalName, title) {
    if (!medalName) return '';
    return '<i class="fa-solid fa-medal upu-medal upu-medal--' + medalName
      + '" title="' + escapeHtml(title) + ' (' + medalName + ')"></i>';
  }

  function awardsHtml(u) {
    var awards = u.awards || {};
    var icons = [];
    Object.keys(awards.instrument_medals || {}).forEach(function (inst) {
      icons.push(medalIcon(awards.instrument_medals[inst],
        inst + ' top monitor'));
    });
    if (awards.service_medal) {
      icons.push(medalIcon(awards.service_medal,
        'Service award – ' + awards.total_hours + 'h total'));
    }
    if (awards.issues_medal) {
      icons.push(medalIcon(awards.issues_medal,
        'Issue resolution award – ' + awards.issues_resolved
        + ' resolved'));
    }
    if (!icons.length) return '';
    return '<div class="upu-user-card__awards">' + icons.join('') + '</div>';
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function renderFilterPills() {
    groupFilterWrap.innerHTML = '';
    var allPill = document.createElement('button');
    allPill.type = 'button';
    allPill.className = 'upu-filter-pill'
      + (activeGroup === null ? ' upu-filter-pill--active' : '');
    allPill.textContent = 'All';
    allPill.addEventListener('click', function () {
      activeGroup = null;
      render(search.value);
    });
    groupFilterWrap.appendChild(allPill);
    getGroupOrder().forEach(function (group) {
      if (!allUsers.some(function (u) {
        return (u.groups || []).indexOf(group) !== -1;
      })) return;
      var pill = document.createElement('button');
      pill.type = 'button';
      pill.className = 'upu-filter-pill'
        + (activeGroup === group ? ' upu-filter-pill--active' : '');
      pill.textContent = group;
      pill.addEventListener('click', function () {
        activeGroup = (activeGroup === group) ? null : group;
        render(search.value);
      });
      groupFilterWrap.appendChild(pill);
    });

    instrumentFilterWrap.innerHTML = '';
    var allInstPill = document.createElement('button');
    allInstPill.type = 'button';
    allInstPill.className = 'upu-filter-pill'
      + (activeInstrument === null ? ' upu-filter-pill--active' : '');
    allInstPill.textContent = 'All';
    allInstPill.addEventListener('click', function () {
      activeInstrument = null;
      render(search.value);
    });
    instrumentFilterWrap.appendChild(allInstPill);
    allInstruments.forEach(function (inst) {
      var pill = document.createElement('button');
      pill.type = 'button';
      pill.className = 'upu-filter-pill'
        + (activeInstrument === inst ? ' upu-filter-pill--active' : '');
      pill.textContent = inst;
      pill.addEventListener('click', function () {
        activeInstrument = (activeInstrument === inst) ? null : inst;
        render(search.value);
      });
      instrumentFilterWrap.appendChild(pill);
    });
  }

  function render(filter) {
    var f = (filter || '').trim().toLowerCase();
    var rows = allUsers.filter(function (u) {
      if (activeGroup && (u.groups || []).indexOf(activeGroup) === -1) {
        return false;
      }
      if (activeInstrument
          && !(u.awards && (u.awards.instruments || [])
              .indexOf(activeInstrument) !== -1)) {
        return false;
      }
      if (!f) return true;
      var bag = [u.username, u.first_names, u.last_name,
                 u.full_name, u.email,
                 (u.institutions || []).join(' '),
                 (u.groups || []).join(' ')]
                 .join(' ').toLowerCase();
      return bag.indexOf(f) !== -1;
    });
    renderFilterPills();
    if (!rows.length) {
      grid.innerHTML = '<div class="upu-empty">No users found.</div>';
    } else {
      grid.innerHTML = rows.map(function (u) {
        var full = [u.first_names, u.last_name].filter(Boolean)
          .join(' ');
        var institution = (u.primary_institution
          || (u.institutions || [])[0] || '').trim();
        var actions = u.is_self
          ? '<span class="upu-pill">you</span>'
          : '<button type="button" class="ari-btn ari-btn--small'
            + ' upu-user-card__message upm-msg-btn" data-username="'
            + escapeHtml(u.username) + '">'
            + '<i class="fa-solid fa-envelope"></i> Message'
            + '</button>';
        var href = escapeHtml(u.profile_url || '/user_portal/users');
        var groupStyle = getGroupStyle(getHighestGroup(u));
        var style = 'background:' + groupStyle.cardBg
          + ';border-color:' + groupStyle.cardBorder + ';';
        return '<a class="upu-user-card" style="' + style + '" href="'
          + href + '">'
          + '<div class="upu-user-card__head">'
          + '<div class="upu-user-card__name">'
          + '<span class="upu-user-card__username">'
          + escapeHtml(u.username) + '</span>'
          + '<span class="upu-user-card__fullname">'
          + escapeHtml(full || 'Name not set') + '</span>'
          + '</div>'
          + actions
          + '</div>'
          + '<div class="upu-user-card__body">'
          + '<div class="upu-user-card__line">'
          + '<i class="fa-solid fa-building"></i>'
          + '<span>' + escapeHtml(institution || 'No institution')
          + '</span></div>'
            + (u.can_view_contact
              ? ('<div class="upu-user-card__line">'
                + '<i class="fa-solid fa-envelope"></i>'
                + '<span>' + escapeHtml(u.email || 'No email')
                + '</span></div>')
              : '')
          + awardsHtml(u)
          + '</div></a>';
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
    if (btn) {
      e.preventDefault();
      e.stopPropagation();
      openModal(btn.dataset.username);
      return;
    }
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

  grid.innerHTML = '<div class="upu-empty">'
    + '<i class="fa-solid fa-spinner fa-spin"></i>'
    + '<p class="upu-empty__title">Loading users…</p>'
    + '</div>';

  fetch('/api/users/directory').then(function (r) {
    return r.json();
  }).then(function (j) {
    allUsers = (j && j.success && j.users) || [];
    allGroups = (j && j.all_groups) || [];
    allInstruments = (j && j.instruments) || [];
    render('');
  }).catch(function () {
    grid.innerHTML = '<div class="upu-empty">Failed to load users.</div>';
  });
})();
