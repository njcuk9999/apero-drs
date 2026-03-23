(function () {
  'use strict';

  const cfg = window.ARI_ADMIN_USER_DB_ACCESS || {};

  const profileSelect = document.getElementById('udba-profile-select');
  const profileHealth = document.getElementById('udba-profile-health');
  const statusBox = document.getElementById('udba-status');
  const statusHeadline = document.getElementById('udba-status-headline');
  const statusDetails = document.getElementById('udba-status-details');
  const refreshBtn = document.getElementById('udba-refresh');
  const workspace = document.getElementById('udba-workspace');
  const empty = document.getElementById('udba-empty');
  const sectionsEl = document.getElementById('udba-sections');
  const saveBtn = document.getElementById('udba-save');
  const saveLabel = document.getElementById('udba-save-label');
  const saveSpinner = document.getElementById('udba-save-spinner');
  const runCheckBtn = document.getElementById('udba-run-check');
  const checkLabel = document.getElementById('udba-check-label');
  const checkSpinner = document.getElementById('udba-check-spinner');
  const checkPanel = document.getElementById('udba-check-panel');
  const checkDetails = document.getElementById('udba-check-details');
  const toast = document.getElementById('udba-toast');

  let profiles = [];
  let currentProfile = null;
  let currentSections = [];
  let healthReport = (cfg && cfg.initialHealthReport && typeof cfg.initialHealthReport === 'object')
    ? cfg.initialHealthReport
    : null;

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function updateTopStatus(level, headline, detailLines) {
    if (!statusBox || !statusHeadline || !statusDetails) return;
    const normLevel = (level === 'ok' || level === 'warning' || level === 'error') ? level : 'info';
    const icon = normLevel === 'ok'
      ? 'fa-circle-check'
      : (normLevel === 'warning' ? 'fa-triangle-exclamation'
      : (normLevel === 'error' ? 'fa-circle-xmark' : 'fa-circle-info'));

    statusBox.classList.remove(
      'ari-ap-status--info',
      'ari-ap-status--ok',
      'ari-ap-status--warning',
      'ari-ap-status--error'
    );
    statusBox.classList.add('ari-ap-status--' + normLevel);
    statusHeadline.innerHTML = '<i class="fa-solid ' + icon + '"></i> ' + headline;

    const details = Array.isArray(detailLines)
      ? detailLines.filter((x) => String(x || '').trim())
      : [];
    if (details.length) {
      statusDetails.style.display = '';
      statusDetails.innerHTML = details
        .map((line) => '<li>' + String(line)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;') + '</li>')
        .join('');
    } else {
      statusDetails.style.display = 'none';
      statusDetails.innerHTML = '';
    }
  }

  function applyOverallProfileHealth() {
    if (healthReport && healthReport.status) {
      updateTopStatus(
        String(healthReport.status || 'info'),
        String(healthReport.status || '') === 'ok'
          ? 'User DB access rules look healthy.'
          : (String(healthReport.status || '') === 'warning'
            ? 'User DB access rules need attention.'
            : (String(healthReport.status || '') === 'error'
              ? 'User DB access health check failed.'
              : 'Configure group and column access to APERO database tables by profile.')),
        [String(healthReport.message || '').trim()].filter((x) => x)
      );
      return;
    }

    if (!profiles.length) {
      updateTopStatus(
        'info',
        'Configure group and column access to APERO database tables by profile.',
        ['No APERO profiles are available for your current permissions.']
      );
      return;
    }

    const withTables = profiles.filter((p) => p && p.has_tables !== false);
    if (!withTables.length) {
      updateTopStatus(
        'warning',
        'User DB access rules need attention.',
        ['No APERO profiles with configured table names were found for DB-access checks.']
      );
      return;
    }

    const warnings = withTables.filter((p) => p.health !== 'ok').length;
    if (warnings > 0) {
      updateTopStatus(
        'warning',
        'User DB access rules need attention.',
        [warnings + ' of ' + withTables.length + ' profile(s) have incomplete DB table access rules.']
      );
      return;
    }

    updateTopStatus(
      'ok',
      'User DB access rules look healthy.',
      ['All ' + withTables.length + ' profile(s) have complete DB table access rules.']
    );
  }

  function setProfileSelectTone(profile) {
    if (!profileSelect) return;
    profileSelect.classList.remove('udba-select--ok', 'udba-select--warning');
    if (!profile) return;
    profileSelect.classList.add(profile.health === 'warning'
      ? 'udba-select--warning'
      : 'udba-select--ok');
  }

  function showToast(msg, kind) {
    if (!toast) return;
    toast.textContent = msg;
    toast.className = 'ari-toast';
    if (kind === 'error') {
      toast.classList.add('ari-toast--error');
    } else {
      toast.classList.add('ari-toast--success');
    }
    toast.style.display = 'block';
    setTimeout(() => {
      toast.style.display = 'none';
    }, 3000);
  }

  function setSaving(saving) {
    if (!saveBtn) return;
    saveBtn.disabled = !!saving;
    saveLabel.style.display = saving ? 'none' : '';
    saveSpinner.style.display = saving ? '' : 'none';
  }

  function setChecking(checking) {
    if (!runCheckBtn || !checkLabel || !checkSpinner) return;
    runCheckBtn.disabled = !!checking;
    checkLabel.style.display = checking ? 'none' : '';
    checkSpinner.style.display = checking ? '' : 'none';
  }

  function renderHealthDiagnostics(report, selectedRow) {
    if (!checkPanel || !checkDetails) return;
    const rep = report || {};
    const status = ['ok', 'warning', 'error'].includes(String(rep.status || ''))
      ? String(rep.status)
      : 'info';

    checkPanel.classList.remove('ari-ap-status--info', 'ari-ap-status--ok', 'ari-ap-status--warning', 'ari-ap-status--error');
    checkPanel.classList.add('ari-ap-status--' + status);

    const lines = [];
    if (rep.message) lines.push(String(rep.message));

    const checked = Number(rep.checked_profiles || 0);
    const warnings = Number(rep.warning_profiles || 0);
    lines.push('Profiles checked: ' + checked + '. Profiles with warnings: ' + warnings + '.');

    if (selectedRow && selectedRow.instrument && selectedRow.profile_id) {
      const profLabel = selectedRow.instrument + ' / ' + selectedRow.profile_id;
      lines.push('Selected profile (' + profLabel + '): ' + String(selectedRow.message || 'No details.'));
    }

    const profileWarnings = Array.isArray(rep.profiles)
      ? rep.profiles.filter((row) => row && row.status === 'warning')
      : [];
    for (const row of profileWarnings.slice(0, 6)) {
      const label = String(row.instrument || '') + ' / ' + String(row.profile_id || '');
      lines.push(label + ': ' + String(row.message || 'incomplete rules'));
    }
    if (profileWarnings.length > 6) {
      lines.push('... and ' + (profileWarnings.length - 6) + ' more profile warning(s).');
    }

    checkDetails.innerHTML = lines.map((line) => '<li>' + escapeHtml(line) + '</li>').join('');
  }

  function currentProfileQuery() {
    if (!currentProfile) return '';
    return new URLSearchParams({
      instrument: String(currentProfile.instrument || ''),
      profile_id: String(currentProfile.profile_id || '')
    }).toString();
  }

  function runHealthCheck() {
    if (!cfg.healthUrl) return Promise.resolve();
    const qs = currentProfileQuery();
    const url = qs ? (cfg.healthUrl + '?' + qs) : cfg.healthUrl;

    setChecking(true);
    return apiGet(url)
      .then((res) => {
        healthReport = res.report || healthReport;
        const selected = res.selected || null;
        if (healthReport) {
          applyOverallProfileHealth();
          renderHealthDiagnostics(healthReport, selected);
        }
      })
      .catch((err) => {
        showToast(err.message || 'Failed to run health check', 'error');
      })
      .finally(() => {
        setChecking(false);
      });
  }

  function apiGet(url) {
    return fetch(url, { credentials: 'same-origin' }).then(async (r) => {
      const json = await r.json().catch(() => ({}));
      if (!r.ok || !json.success) {
        throw new Error(json.error || 'Request failed');
      }
      return json;
    });
  }

  function apiPost(url, payload) {
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(async (r) => {
      const json = await r.json().catch(() => ({}));
      if (!r.ok || !json.success) {
        throw new Error(json.error || 'Request failed');
      }
      return json;
    });
  }

  function renderProfileOptions() {
    profileSelect.innerHTML = '';
    if (!profiles.length) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'No profiles available';
      profileSelect.appendChild(opt);
      profileSelect.disabled = true;
      workspace.style.display = 'none';
      empty.style.display = '';
      return;
    }

    profileSelect.disabled = false;
    empty.style.display = 'none';

    const first = document.createElement('option');
    first.value = '';
    first.textContent = 'Select a profile...';
    profileSelect.appendChild(first);

    for (const p of profiles) {
      const key = `${p.instrument}::${p.profile_id}`;
      const opt = document.createElement('option');
      const warning = p.health === 'warning';
      const icon = warning ? ' [warning]' : ' [ok]';
      opt.value = key;
      opt.textContent = `${p.instrument} / ${p.profile_id}${icon}`;
      opt.style.color = warning ? '#b91c1c' : '#166534';
      opt.style.fontWeight = '600';
      profileSelect.appendChild(opt);
    }
  }

  function applyHealth(profile) {
    if (!profile) {
      profileHealth.style.display = 'none';
      setProfileSelectTone(null);
      return;
    }
    setProfileSelectTone(profile);
    if (profile.health === 'warning') {
      profileHealth.style.display = '';
      profileHealth.className = 'ari-ap-validation ari-ap-validation--invalid';
      profileHealth.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Warning: one or more tables have no groups or no selected columns.';
      return;
    }
    profileHealth.style.display = '';
    profileHealth.className = 'ari-ap-validation ari-ap-validation--valid';
    profileHealth.innerHTML = '<i class="fa-solid fa-circle-check"></i> Access configuration is complete for all configured tables.';
  }

  function cardButton(text, selected, editable, kind) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'udba-card';

    const icon = document.createElement('i');
    icon.className = 'fa-solid';
    icon.setAttribute('aria-hidden', 'true');
    icon.classList.add(selected ? 'fa-check' : 'fa-xmark');

    const label = document.createElement('span');
    label.textContent = text;

    btn.appendChild(icon);
    btn.appendChild(label);

    if (kind === 'group') {
      btn.classList.add(selected ? 'udba-card--group-on' : 'udba-card--group-off');
    }
    if (kind === 'column') {
      btn.classList.add(selected ? 'udba-card--column-on' : 'udba-card--column-off');
    }
    if (!editable) {
      btn.classList.add('udba-card--disabled');
      btn.disabled = true;
    }
    btn.dataset.selected = selected ? '1' : '0';
    return btn;
  }

  function setCardSelectedState(btn, selected, kind) {
    btn.dataset.selected = selected ? '1' : '0';
    if (kind === 'group') {
      btn.classList.toggle('udba-card--group-on', selected);
      btn.classList.toggle('udba-card--group-off', !selected);
    }
    if (kind === 'column') {
      btn.classList.toggle('udba-card--column-on', selected);
      btn.classList.toggle('udba-card--column-off', !selected);
    }
    const icon = btn.querySelector('i.fa-solid');
    if (icon) {
      icon.classList.toggle('fa-check', selected);
      icon.classList.toggle('fa-xmark', !selected);
    }
  }

  function renderSections() {
    sectionsEl.innerHTML = '';

    if (!currentSections.length) {
      const p = document.createElement('div');
      p.className = 'ari-sg-empty-small';
      p.textContent = 'No APERO table names are configured on this profile.';
      sectionsEl.appendChild(p);
      return;
    }

    for (const sec of currentSections) {
      const wrap = document.createElement('div');
      wrap.className = 'udba-section';
      wrap.dataset.table = sec.table;

      const header = document.createElement('div');
      header.className = 'udba-section__header';
      header.innerHTML = `<h4>${sec.table}</h4><div class="udba-section__tablename">${sec.table_name}</div>`;

      const groupLabel = document.createElement('div');
      groupLabel.className = 'udba-label';
      groupLabel.textContent = 'Group access';

      const groupsRow = document.createElement('div');
      groupsRow.className = 'udba-row';
      for (const g of sec.groups) {
        const b = cardButton(g.name, !!g.selected, !!g.editable, 'group');
        b.dataset.group = g.name;
        b.addEventListener('click', () => {
          const on = b.dataset.selected === '1';
          setCardSelectedState(b, !on, 'group');
        });
        groupsRow.appendChild(b);
      }

      const colLabel = document.createElement('div');
      colLabel.className = 'udba-label';
      colLabel.textContent = 'Visible columns';

      const colsRow = document.createElement('div');
      colsRow.className = 'udba-row';

      if (sec.columns_error) {
        const err = document.createElement('div');
        err.className = 'ari-ap-validation ari-ap-validation--invalid';
        err.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> ${sec.columns_error}`;
        colsRow.appendChild(err);
      } else if (!sec.columns.length) {
        const info = document.createElement('div');
        info.className = 'ari-ap-validation ari-ap-validation--invalid';
        info.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> No columns found in this table.';
        colsRow.appendChild(info);
      } else {
        for (const c of sec.columns) {
          const b = cardButton(c.name, !!c.selected, true, 'column');
          b.dataset.column = c.name;
          b.addEventListener('click', () => {
            const on = b.dataset.selected === '1';
            setCardSelectedState(b, !on, 'column');
          });
          colsRow.appendChild(b);
        }
      }

      wrap.appendChild(header);
      wrap.appendChild(groupLabel);
      wrap.appendChild(groupsRow);
      wrap.appendChild(colLabel);
      wrap.appendChild(colsRow);
      sectionsEl.appendChild(wrap);
    }
  }

  function readUiPayload() {
    const groups = {};
    const columns = {};

    for (const sec of sectionsEl.querySelectorAll('.udba-section')) {
      const table = sec.dataset.table;
      if (!table) continue;

      const selectedGroups = [];
      for (const g of sec.querySelectorAll('[data-group]')) {
        if (g.dataset.selected === '1') {
          selectedGroups.push(g.dataset.group);
        }
      }

      const selectedColumns = [];
      for (const c of sec.querySelectorAll('[data-column]')) {
        if (c.dataset.selected === '1') {
          selectedColumns.push(c.dataset.column);
        }
      }

      groups[table] = selectedGroups;
      columns[table] = selectedColumns;
    }

    return { groups, columns };
  }

  function onProfileChange() {
    const key = profileSelect.value;
    if (!key) {
      currentProfile = null;
      currentSections = [];
      workspace.style.display = 'none';
      applyHealth(null);
      return;
    }

    const [instrument, profile_id] = key.split('::');
    currentProfile = profiles.find((p) => p.instrument === instrument && p.profile_id === profile_id) || null;
    applyHealth(currentProfile);

    const q = new URLSearchParams({ instrument, profile_id }).toString();
    apiGet(`${cfg.detailsUrl}?${q}`)
      .then((res) => {
        currentSections = Array.isArray(res.sections) ? res.sections : [];
        renderSections();
        workspace.style.display = '';
        if (healthReport && Array.isArray(healthReport.profiles)) {
          const selected = healthReport.profiles.find((row) =>
            row && row.instrument === instrument && row.profile_id === profile_id
          ) || null;
          renderHealthDiagnostics(healthReport, selected);
        }
      })
      .catch((err) => {
        workspace.style.display = 'none';
        currentSections = [];
        showToast(err.message || 'Failed to load profile details', 'error');
      });
  }

  function loadProfiles() {
    workspace.style.display = 'none';
    currentProfile = null;
    currentSections = [];

    apiGet(cfg.profilesUrl)
      .then((res) => {
        profiles = Array.isArray(res.profiles) ? res.profiles : [];
        renderProfileOptions();
        applyHealth(null);
        applyOverallProfileHealth();
        return runHealthCheck();
      })
      .catch((err) => {
        profiles = [];
        renderProfileOptions();
        updateTopStatus(
          'error',
          'User DB access health check failed.',
          [err.message || 'Failed to load profiles']
        );
        showToast(err.message || 'Failed to load profiles', 'error');
      });
  }

  function saveCurrent() {
    if (!currentProfile) {
      showToast('Choose a profile first.', 'error');
      return;
    }

    const payload = readUiPayload();
    setSaving(true);
    apiPost(cfg.saveUrl, {
      instrument: currentProfile.instrument,
      profile_id: currentProfile.profile_id,
      groups: payload.groups,
      columns: payload.columns
    })
      .then(() => {
        showToast('User DB access saved.', 'success');
        return apiGet(cfg.profilesUrl);
      })
      .then((res) => {
        profiles = Array.isArray(res.profiles) ? res.profiles : profiles;
        const key = `${currentProfile.instrument}::${currentProfile.profile_id}`;
        renderProfileOptions();
        profileSelect.value = key;
        currentProfile = profiles.find((p) => p.instrument === currentProfile.instrument && p.profile_id === currentProfile.profile_id) || currentProfile;
        applyHealth(currentProfile);
        applyOverallProfileHealth();
        return runHealthCheck();
      })
      .catch((err) => {
        showToast(err.message || 'Failed to save', 'error');
      })
      .finally(() => {
        setSaving(false);
      });
  }

  function injectStyles() {
    const css = `
      .udba-sections { display: grid; gap: 1rem; }
      .udba-section { border: 1px solid #d4d7df; border-radius: 0.75rem; padding: 0.9rem; background: #fff; }
      .udba-section__header { display:flex; justify-content:space-between; align-items:center; gap: 0.75rem; margin-bottom: 0.6rem; }
      .udba-section__header h4 { margin: 0; font-size: 1rem; }
      .udba-section__tablename { color: #4f5663; font-size: 0.86rem; }
      .udba-label { font-size: 0.86rem; color: #445; margin: 0.6rem 0 0.35rem; font-weight: 600; }
      .udba-row { display:flex; flex-wrap: wrap; gap: 0.45rem; }
      .udba-card {
        display: inline-flex;
        align-items: center;
        gap: 0.38rem;
        border: 1px solid transparent;
        border-radius: 999px;
        padding: 0.34rem 0.72rem;
        font-size: 0.82rem;
        cursor: pointer;
      }
      .udba-card--group-on { background: #7e4ccf; color: #fff; border-color: #6e40b8; }
      .udba-card--group-off { background: #fff1e6; color: #a44f00; border-color: #efc8a7; }
      .udba-card--column-on { background: #0f4fa2; color: #fff; border-color: #0d4389; }
      .udba-card--column-off { background: #edf2fa; color: #455b84; border-color: #c9d4ea; }
      .udba-card--disabled { opacity: 0.45; cursor: not-allowed; }
      #udba-check-panel .ari-ap-status__details { margin-top: 0.4rem; }
      #udba-profile-select.udba-select--ok {
        border-color: #17803d;
        background: #ecfdf3;
        color: #14532d;
      }
      #udba-profile-select.udba-select--warning {
        border-color: #b91c1c;
        background: #fef2f2;
        color: #7f1d1d;
      }
    `;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }

  function init() {
    if (!profileSelect || !sectionsEl) return;
    injectStyles();
    const initial = (cfg && cfg.initialHealth && typeof cfg.initialHealth === 'object')
      ? cfg.initialHealth
      : null;
    if (initial) {
      const initialMsg = String(initial.message || '').trim();
      updateTopStatus(
        String(initial.status || 'info'),
        String(initial.status || '') === 'ok'
          ? 'User DB access rules look healthy.'
          : (String(initial.status || '') === 'warning'
            ? 'User DB access rules need attention.'
            : (String(initial.status || '') === 'error'
              ? 'User DB access health check failed.'
              : 'Configure group and column access to APERO database tables by profile.')),
        initialMsg ? [initialMsg] : []
      );
    }
    if (healthReport) {
      renderHealthDiagnostics(healthReport, null);
    }
    loadProfiles();
    profileSelect.addEventListener('change', onProfileChange);
    refreshBtn.addEventListener('click', loadProfiles);
    if (runCheckBtn) runCheckBtn.addEventListener('click', runHealthCheck);
    saveBtn.addEventListener('click', saveCurrent);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
