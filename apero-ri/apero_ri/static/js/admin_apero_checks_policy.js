(function () {
    'use strict';

    var cfg = window.ARI_APERO_CHECKS_POLICY || {};
    var sectionsApiUrl = String(cfg.sectionsApiUrl || '');
    var checkInfoBaseUrl = String(cfg.checkInfoBaseUrl || '');
    var rerunNightUrl = String(cfg.rerunNightUrl || '');
    var rerunCheckUrl = String(cfg.rerunCheckUrl || '');
    var cleanResetUrl = String(cfg.cleanResetUrl || '');
    var profilePageUrlTemplate = String(cfg.profilePageUrlTemplate || '');

    var healthWrap = document.getElementById('acp-health-wrap');
    var catalogFilter = document.getElementById('acp-catalog-filter');
    var catalogLoading = document.getElementById('acp-catalog-loading');
    var catalogWrap = document.getElementById('acp-check-catalog');
    var summaryLoading = document.getElementById('acp-summary-loading');
    var summaryWrap = document.getElementById('acp-profile-summaries');
    var updatedEl = document.getElementById('acp-last-updated');
    var runProfile = document.getElementById('acp-run-profile');
    var runAllChecks = document.getElementById('acp-run-all-checks');
    var runCheckSearch = document.getElementById('acp-run-check-search');
    var runCheckAvailable = document.getElementById('acp-run-check-available');
    var runCheckAdd = document.getElementById('acp-run-check-add');
    var runCheckAddAll = document.getElementById('acp-run-check-add-all');
    var runCheckRemove = document.getElementById('acp-run-check-remove');
    var runCheckClear = document.getElementById('acp-run-check-clear');
    var runCheckSelected = document.getElementById('acp-run-check-selected');
    var runAllNights = document.getElementById('acp-run-all-nights');
    var runObsdirSearch = document.getElementById('acp-run-obsdir-search');
    var runObsdirAvailable = document.getElementById('acp-run-obsdir-available');
    var runObsdirRefresh = document.getElementById('acp-run-obsdir-refresh');
    var runObsdirAdd = document.getElementById('acp-run-obsdir-add');
    var runObsdirAddAll = document.getElementById('acp-run-obsdir-add-all');
    var runObsdirRemove = document.getElementById('acp-run-obsdir-remove');
    var runObsdirClear = document.getElementById('acp-run-obsdir-clear');
    var runObsdirSelected = document.getElementById('acp-run-obsdir-selected');
    var runSubmit = document.getElementById('acp-run-submit');
    var runCleanReset = document.getElementById('acp-run-clean-reset');
    var runStatus = document.getElementById('acp-run-status');
    var profileRowsCache = [];
    var checksCatalogCache = [];
    var runCheckKeysAvailable = [];
    var runCheckKeysSelected = [];
    var runObsdirsAvailable = [];
    var runObsdirsSelected = [];

    function escHtml(value) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(value || '')));
        return d.innerHTML;
    }

    function renderHealth(health) {
        if (!healthWrap) return;
        if (!health || typeof health !== 'object') {
            healthWrap.style.display = 'none';
            healthWrap.innerHTML = '';
            return;
        }
        var status = String(health.status || 'info');
        var icon = 'fa-circle-info';
        if (status === 'ok') icon = 'fa-circle-check';
        if (status === 'warning') icon = 'fa-triangle-exclamation';
        if (status === 'error') icon = 'fa-circle-xmark';

        var html = '';
        html += '<div class="ari-ap-status ari-ap-status--' + escHtml(status)
            + '">';
        html += '<div class="ari-ap-status__headline">';
        html += '<i class="fa-solid ' + escHtml(icon) + '"></i> ';
        html += escHtml(health.message || '');
        html += '</div>';
        var details = health.details;
        if (Array.isArray(details) && details.length) {
            html += '<ul class="ari-ap-status__details" '
                + 'style="margin-top:0.35rem;">';
            details.forEach(function (item) {
                html += '<li>' + escHtml(item) + '</li>';
            });
            html += '</ul>';
        }
        html += '</div>';
        healthWrap.innerHTML = html;
        healthWrap.style.display = '';
    }

    function checkInfoUrl(checkKey) {
        var sep = checkInfoBaseUrl.indexOf('?') === -1 ? '?' : '&';
        return checkInfoBaseUrl + sep
            + 'check=' + encodeURIComponent(String(checkKey || ''));
    }

    function renderCatalog(cards) {
        if (!catalogWrap) return;
        catalogWrap.innerHTML = '';
        if (!Array.isArray(cards) || !cards.length) {
            catalogWrap.innerHTML = '<span class="acp-note">'
                + 'No checks found.'
                + '</span>';
            return;
        }

        var instruments = [];
        cards.forEach(function (item) {
            var insts = Array.isArray(item.instruments)
                ? item.instruments : [];
            insts.forEach(function (inst) {
                var text = String(inst || '').trim();
                if (!text) return;
                if (instruments.indexOf(text) === -1) {
                    instruments.push(text);
                }
            });
        });
        instruments.sort();
        if (catalogFilter) {
            catalogFilter.innerHTML = '<option value="all">'
                + 'All instruments</option>';
            instruments.forEach(function (inst) {
                var opt = document.createElement('option');
                opt.value = inst;
                opt.textContent = inst;
                catalogFilter.appendChild(opt);
            });
            catalogFilter.disabled = false;
        }

        var html = '';
        cards.forEach(function (item) {
            var classes = [
                'acp-card',
                'acp-check-card',
                'acp-check-card--' + escHtml(item.dominant_state || 'neutral'),
                'acp-check-card--' + escHtml(item.check_type || 'all'),
            ];
            if (item.is_ignored) {
                classes.push('acp-check-card--ignored');
            }
            html += '<a class="' + classes.join(' ') + '"';
            html += ' href="' + escHtml(checkInfoUrl(item.check_key)) + '"';
            html += ' data-acp-check="' + escHtml(item.check_key) + '"';
            html += ' data-acp-instruments="'
                + escHtml((item.instruments || []).join(',')) + '"';
            html += ' data-acp-state="'
                + escHtml(item.dominant_state || '') + '"';
            html += ' data-acp-ignored="'
                + (item.is_ignored ? 'true' : 'false') + '"';
            html += ' data-acp-override="'
                + (item.override_allowed ? 'true' : 'false') + '"';
            html += ' title="' + escHtml(item.check_name) + '">';
            html += '<div>';
            html += '<div class="acp-card__title acp-card__title--singleline">';
            html += escHtml(item.check_name || '');
            if (item.has_missing_metadata) {
                html += ' <i class="fa-solid fa-triangle-exclamation '
                    + 'acp-missing-icon" '
                    + 'title="Missing documentation metadata"></i>';
            }
            html += '</div>';
            html += '<div class="acp-card__subtitle">'
                + escHtml(item.check_human_name || '') + '</div>';
            html += '</div>';
            html += '<div class="acp-card__meta" style="align-items:flex-end;">';
            if (item.override_allowed) {
                html += '<span class="acp-chip acp-chip--override-allowed">'
                    + 'Override allowed</span>';
            }
            if (item.is_ignored) {
                html += '<span class="acp-chip acp-chip--ignored">Ignored</span>';
            }
            var total = ((item.counts || {}).total || 0);
            html += '<span class="acp-chip">Total: ' + escHtml(total) + '</span>';
            html += '</div>';
            html += '</a>';
        });
        catalogWrap.innerHTML = html;
    }

    function renderProfileSummaries(rows) {
        if (!summaryWrap) return;
        summaryWrap.innerHTML = '';
        if (!Array.isArray(rows) || !rows.length) {
            summaryWrap.innerHTML = '<span class="acp-note">'
                + 'No profiles found.'
                + '</span>';
            return;
        }

        var html = '';
        rows.forEach(function (row) {
            var counts = row.counts || {};
            html += '<details>';
            html += '<summary>';
            html += '<span><strong>Summary ' + escHtml(row.profile_id)
                + '</strong> <span class="acp-note">('
                + escHtml(row.instrument) + ')</span></span>';
            html += '<span class="acp-note">'
                + escHtml(counts.total || 0) + ' nights</span>';
            html += '</summary>';
            html += '<div class="acp-summary__counts">';
            html += '<span class="acp-chip acp-chip--passed">Passed: '
                + escHtml(counts.passed || 0) + '</span>';
            html += '<span class="acp-chip acp-chip--overridden">'
                + 'Overridden: ' + escHtml(counts.overridden || 0) + '</span>';
            html += '<span class="acp-chip acp-chip--monitored">'
                + 'Monitored: ' + escHtml(counts.monitored || 0) + '</span>';
            html += '<span class="acp-chip acp-chip--mixed">'
                + 'Overridden and monitored: '
                + escHtml(counts.mixed || 0) + '</span>';
            html += '<span class="acp-chip acp-chip--failed">'
                + 'Failed: ' + escHtml(counts.failed || 0) + '</span>';
            html += '</div>';
            html += '<div class="acp-summary__body">Checks root: '
                + escHtml(row.checks_root || '') + '</div>';
            html += '</details>';
        });
        summaryWrap.innerHTML = html;
    }

    function setRunStatus(msg) {
        if (!runStatus) return;
        runStatus.textContent = String(msg || '');
    }

    function uniqueStrings(values) {
        var out = [];
        var seen = Object.create(null);
        (Array.isArray(values) ? values : []).forEach(function (item) {
            var value = String(item || '').trim();
            if (!value || seen[value]) return;
            seen[value] = true;
            out.push(value);
        });
        return out;
    }

    function filterValues(values, query) {
        var q = String(query || '').trim().toLowerCase();
        if (!q) {
            return values.slice();
        }
        return values.filter(function (value) {
            return String(value || '').toLowerCase().indexOf(q) >= 0;
        });
    }

    function selectedOptions(selectEl) {
        var out = [];
        if (!selectEl) return out;
        Array.prototype.forEach.call(selectEl.options || [], function (opt) {
            if (!opt || !opt.selected) return;
            out.push(String(opt.value || ''));
        });
        return uniqueStrings(out);
    }

    function renderAvailableSelect(selectEl, values) {
        if (!selectEl) return;
        selectEl.innerHTML = '';
        values.forEach(function (value) {
            var opt = document.createElement('option');
            opt.value = value;
            opt.textContent = value;
            selectEl.appendChild(opt);
        });
    }

    function renderSelectedChips(container, values, emptyLabel, kind) {
        if (!container) return;
        if (!Array.isArray(values) || values.length === 0) {
            container.innerHTML = '<span class="acp-run-selected__empty">'
                + escHtml(emptyLabel)
                + '</span>';
            return;
        }
        var html = '';
        values.forEach(function (value) {
            html += '<span class="acp-run-chip">';
            html += '<span>' + escHtml(value) + '</span>';
            html += '<button type="button"'
                + ' data-acp-remove-kind="' + escHtml(kind) + '"'
                + ' data-acp-remove-value="' + escHtml(value) + '"'
                + ' aria-label="Remove">';
            html += '<i class="fa-solid fa-xmark"></i>';
            html += '</button>';
            html += '</span>';
        });
        container.innerHTML = html;
    }

    function removeValuesFrom(list, values) {
        var removeSet = Object.create(null);
        uniqueStrings(values).forEach(function (value) {
            removeSet[value] = true;
        });
        return uniqueStrings(list).filter(function (value) {
            return !removeSet[value];
        });
    }

    function addValuesTo(list, values) {
        return uniqueStrings((Array.isArray(list) ? list : []).concat(values));
    }

    function renderRunProfiles(rows) {
        if (!runProfile || !runSubmit) return;
        profileRowsCache = Array.isArray(rows) ? rows.slice() : [];
        runProfile.innerHTML = '<option value="">Select profile</option>';
        profileRowsCache.forEach(function (row) {
            var profileId = String((row || {}).profile_id || '').trim();
            if (!profileId) return;
            var instrument = String((row || {}).instrument || '').trim();
            var opt = document.createElement('option');
            opt.value = profileId;
            opt.textContent = profileId + (instrument
                ? ' (' + instrument + ')'
                : '');
            runProfile.appendChild(opt);
        });
        runProfile.disabled = profileRowsCache.length === 0;
        runSubmit.disabled = profileRowsCache.length === 0;
        if (runCleanReset) {
            runCleanReset.disabled = profileRowsCache.length === 0;
        }
        renderRunCheckOptions();
    }

    function setRunButtonsDisabled(disabled) {
        var off = !!disabled;
        if (runSubmit) {
            runSubmit.disabled = off;
        }
        if (runCleanReset) {
            runCleanReset.disabled = off;
        }
    }

    function profileInstrument(profileId) {
        var idx;
        var row;
        var value = String(profileId || '').trim();
        if (!value) return '';
        for (idx = 0; idx < profileRowsCache.length; idx += 1) {
            row = profileRowsCache[idx] || {};
            if (String(row.profile_id || '').trim() !== value) {
                continue;
            }
            return String(row.instrument || '').trim();
        }
        return '';
    }

    function normalizeInstrument(value) {
        return String(value || '')
            .trim()
            .toUpperCase()
            .replace(/-/g, '_');
    }

    function instrumentMatches(wanted, candidate) {
        var w = normalizeInstrument(wanted);
        var c = normalizeInstrument(candidate);
        if (!w) {
            return true;
        }
        if (w === c) {
            return true;
        }
        // Keep NIRPS generic labels compatible with HE/HA check labels.
        if (w === 'NIRPS' && c.indexOf('NIRPS_') === 0) {
            return true;
        }
        if (c === 'NIRPS' && w.indexOf('NIRPS_') === 0) {
            return true;
        }
        return false;
    }

    function checkKeysForInstrument(instrument) {
        var keys = [];
        var seen = Object.create(null);
        var wanted = String(instrument || '').trim();
        checksCatalogCache.forEach(function (item) {
            var checkKey = String((item || {}).check_key || '').trim();
            var insts = Array.isArray((item || {}).instruments)
                ? item.instruments
                : [];
            if (!checkKey || seen[checkKey]) {
                return;
            }
            if (wanted && !insts.some(function (inst) {
                return instrumentMatches(wanted, inst);
            })) {
                return;
            }
            seen[checkKey] = true;
            keys.push(checkKey);
        });
        keys.sort();
        return keys;
    }

    function renderRunCheckOptions() {
        var selectedProfile;
        var instrument;
        var filtered;
        selectedProfile = String((runProfile && runProfile.value) || '').trim();
        instrument = profileInstrument(selectedProfile);
        runCheckKeysAvailable = checkKeysForInstrument(instrument);
        runCheckKeysSelected = removeValuesFrom(
            runCheckKeysSelected,
            runCheckKeysSelected.filter(function (key) {
                return runCheckKeysAvailable.indexOf(key) === -1;
            })
        );
        filtered = filterValues(
            runCheckKeysAvailable,
            runCheckSearch ? runCheckSearch.value : ''
        );
        renderAvailableSelect(runCheckAvailable, filtered);
        renderSelectedChips(
            runCheckSelected,
            runCheckKeysSelected,
            'All checks',
            'check'
        );
        syncRunControlState();
    }

    function renderRunObsdirOptions() {
        var filtered = filterValues(
            runObsdirsAvailable,
            runObsdirSearch ? runObsdirSearch.value : ''
        );
        renderAvailableSelect(runObsdirAvailable, filtered);
        renderSelectedChips(
            runObsdirSelected,
            runObsdirsSelected,
            'All obs-dirs',
            'obsdir'
        );
        syncRunControlState();
    }

    function syncRunControlState() {
        var hasProfile = !!String((runProfile && runProfile.value) || '').trim();
        var allChecks = !!(runAllChecks && runAllChecks.checked);
        var allObsdirs = !!(runAllNights && runAllNights.checked);
        var disableChecks = !hasProfile || allChecks;
        var disableObsdirs = !hasProfile || allObsdirs;

        if (runCheckSearch) runCheckSearch.disabled = disableChecks;
        if (runCheckAvailable) runCheckAvailable.disabled = disableChecks;
        if (runCheckAdd) runCheckAdd.disabled = disableChecks;
        if (runCheckAddAll) runCheckAddAll.disabled = disableChecks;
        if (runCheckRemove) runCheckRemove.disabled = disableChecks;
        if (runCheckClear) runCheckClear.disabled = disableChecks;

        if (runObsdirSearch) runObsdirSearch.disabled = disableObsdirs;
        if (runObsdirAvailable) runObsdirAvailable.disabled = disableObsdirs;
        if (runObsdirRefresh) runObsdirRefresh.disabled = !hasProfile;
        if (runObsdirAdd) runObsdirAdd.disabled = disableObsdirs;
        if (runObsdirAddAll) runObsdirAddAll.disabled = disableObsdirs;
        if (runObsdirRemove) runObsdirRemove.disabled = disableObsdirs;
        if (runObsdirClear) runObsdirClear.disabled = disableObsdirs;

        if (runSubmit) runSubmit.disabled = !hasProfile;
        if (runCleanReset) runCleanReset.disabled = !hasProfile;
    }

    function getProfilePageUrl(profileId) {
        var token = '__PROFILE_ID__';
        if (!profilePageUrlTemplate || !profileId) return '';
        return profilePageUrlTemplate.replace(token, encodeURIComponent(
            String(profileId)
        ));
    }

    function fetchProfileObsdirs(profileId) {
        var base = getProfilePageUrl(profileId);
        var url;
        if (!base) {
            return Promise.resolve([]);
        }
        url = base + '?page=1&per_page=10000&pages=1&result_filter=all';
        return fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var out = [];
                var seen = Object.create(null);
                var pages;
                var firstPage;
                if (!data || !data.success) {
                    return out;
                }
                pages = data.pages || {};
                firstPage = pages['1'] || pages[1] || [];
                (Array.isArray(firstPage) ? firstPage : []).forEach(function (
                    card
                ) {
                    var obs = String((card || {}).obsdir || '').trim();
                    if (!obs || seen[obs]) return;
                    seen[obs] = true;
                    out.push(obs);
                });
                return out;
            });
    }

    async function loadProfileObsdirs(profileId) {
        runObsdirsAvailable = [];
        runObsdirsSelected = [];
        renderRunObsdirOptions();
        if (!profileId) {
            return;
        }
        setRunStatus('Loading obs-dirs for ' + profileId + '...');
        try {
            runObsdirsAvailable = await fetchProfileObsdirs(profileId);
            runObsdirsAvailable.sort();
            renderRunObsdirOptions();
            setRunStatus(
                'Loaded ' + runObsdirsAvailable.length + ' obs-dir(s).'
            );
        } catch (err) {
            runObsdirsAvailable = [];
            runObsdirsSelected = [];
            renderRunObsdirOptions();
            setRunStatus('Failed to load obs-dirs for selected profile.');
        }
    }

    function queueRun(payload, checkKey) {
        var url = checkKey ? rerunCheckUrl : rerunNightUrl;
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        }).then(function (r) { return r.json(); });
    }

    async function handleRunSubmit() {
        var profileId;
        var checks;
        var obsdirs = [];
        var ok = 0;
        var failed = 0;
        var i;
        var j;
        var total;
        var payload;
        var res;
        if (!runProfile || !runSubmit) return;
        profileId = String(runProfile.value || '').trim();
        checks = [];
        if (!profileId) {
            setRunStatus('Select a profile first.');
            return;
        }

        setRunButtonsDisabled(true);
        try {
            if (runAllNights && runAllNights.checked) {
                obsdirs = runObsdirsAvailable.slice();
            } else {
                obsdirs = runObsdirsSelected.slice();
            }
            if (!obsdirs.length) {
                setRunStatus('No obs-dirs found to queue.');
                return;
            }

            if (!(runAllChecks && runAllChecks.checked)) {
                checks = runCheckKeysSelected.slice();
                if (!checks.length) {
                    setRunStatus('No checks selected.');
                    return;
                }
            }

            total = obsdirs.length * (checks.length || 1);
            setRunStatus('Queueing ' + total + ' run(s)...');

            for (i = 0; i < obsdirs.length; i += 1) {
                if (!checks.length) {
                    payload = {
                        profile_id: profileId,
                        obsdir: obsdirs[i],
                    };
                    try {
                        res = await queueRun(payload, '');
                        if (res && res.success) {
                            ok += 1;
                        } else {
                            failed += 1;
                        }
                    } catch (err) {
                        failed += 1;
                    }
                    continue;
                }

                for (j = 0; j < checks.length; j += 1) {
                    payload = {
                        profile_id: profileId,
                        obsdir: obsdirs[i],
                        check_key: checks[j],
                    };
                    try {
                        res = await queueRun(payload, checks[j]);
                        if (res && res.success) {
                            ok += 1;
                        } else {
                            failed += 1;
                        }
                    } catch (err2) {
                        failed += 1;
                    }
                }
            }
            setRunStatus(
                'Queued: ' + ok + ' | Failed: ' + failed
                    + (checks.length
                        ? ' | Mode: selected checks x obs-dirs'
                        : ' | Mode: all checks per obs-dir')
            );
        } finally {
            setRunButtonsDisabled(false);
            syncRunControlState();
        }
    }

    function cleanReset(profileId) {
        return fetch(cleanResetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                profile_id: profileId,
            }),
        }).then(function (r) { return r.json(); });
    }

    async function handleCleanReset() {
        var profileId;
        var confirmed;
        if (!runProfile) return;
        profileId = String(runProfile.value || '').trim();
        if (!profileId) {
            setRunStatus('Select a profile first.');
            return;
        }
        if (!cleanResetUrl) {
            setRunStatus('Clean reset is not available.');
            return;
        }
        confirmed = window.confirm(
            'Clean reset will delete all APERO-check YAML files for '
                + profileId
                + ' and queue a full rerun of all nights. Continue?'
        );
        if (!confirmed) {
            return;
        }

        setRunButtonsDisabled(true);
        setRunStatus('Running clean reset for ' + profileId + '...');
        try {
            var data = await cleanReset(profileId);
            if (!data || !data.success) {
                setRunStatus(
                    'Clean reset failed: '
                        + String((data && data.error) || 'Unknown error')
                );
                return;
            }
            setRunStatus(
                'Clean reset complete: deleted '
                    + String(data.deleted || 0)
                    + ' YAML file(s), queued task '
                    + String(data.task_id || '')
            );
            loadSections();
        } catch (err) {
            setRunStatus('Clean reset failed.');
        } finally {
            setRunButtonsDisabled(false);
        }
    }

    function applyCatalogFilter() {
        var selected;
        var cards;
        if (!catalogWrap || !catalogFilter) {
            return;
        }
        selected = String(catalogFilter.value || 'all').trim();
        cards = catalogWrap.querySelectorAll('[data-acp-check]');
        cards.forEach(function (card) {
            var raw;
            var instruments;
            if (selected === 'all') {
                card.style.display = '';
                return;
            }
            raw = String(card.getAttribute('data-acp-instruments') || '');
            instruments = raw.split(',').filter(Boolean);
            if (instruments.indexOf(selected) >= 0) {
                card.style.display = '';
                return;
            }
            card.style.display = 'none';
        });
    }

    function setLoading(text) {
        if (catalogLoading) {
            catalogLoading.textContent = text;
            catalogLoading.style.display = '';
        }
        if (summaryLoading) {
            summaryLoading.textContent = text;
            summaryLoading.style.display = '';
        }
    }

    function hideLoading() {
        if (catalogLoading) {
            catalogLoading.style.display = 'none';
        }
        if (summaryLoading) {
            summaryLoading.style.display = 'none';
        }
    }

    function loadSections() {
        if (!sectionsApiUrl) {
            setLoading('Failed to load section.');
            return;
        }
        setLoading('Loading section...');
        fetch(sectionsApiUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    setLoading(data.error || 'Failed to load section.');
                    return;
                }
                renderHealth(data.checks_health || null);
                renderCatalog(data.checks_catalog || []);
                checksCatalogCache = Array.isArray(data.checks_catalog)
                    ? data.checks_catalog.slice()
                    : [];
                renderProfileSummaries(data.profile_summaries || []);
                renderRunProfiles(data.profile_summaries || []);
                renderRunCheckOptions();
                if (updatedEl) {
                    updatedEl.textContent = String(
                        data.policy_last_updated || 'n/a'
                    );
                }
                hideLoading();
                applyCatalogFilter();
                syncRunControlState();
            })
            .catch(function () {
                setLoading('Failed to load section.');
            });
    }

    if (catalogFilter) {
        catalogFilter.addEventListener('change', applyCatalogFilter);
    }
    if (runSubmit) {
        runSubmit.addEventListener('click', function () {
            handleRunSubmit();
        });
    }
    if (runCleanReset) {
        runCleanReset.addEventListener('click', function () {
            handleCleanReset();
        });
    }
    if (runProfile) {
        runProfile.addEventListener('change', function () {
            runCheckKeysSelected = [];
            runObsdirsSelected = [];
            renderRunCheckOptions();
            loadProfileObsdirs(String(runProfile.value || '').trim());
            syncRunControlState();
        });
    }
    if (runAllChecks) {
        runAllChecks.addEventListener('change', function () {
            syncRunControlState();
            renderRunCheckOptions();
        });
    }
    if (runAllNights) {
        runAllNights.addEventListener('change', function () {
            syncRunControlState();
            renderRunObsdirOptions();
        });
    }

    if (runCheckSearch) {
        runCheckSearch.addEventListener('input', renderRunCheckOptions);
    }
    if (runObsdirSearch) {
        runObsdirSearch.addEventListener('input', renderRunObsdirOptions);
    }

    if (runCheckAdd) {
        runCheckAdd.addEventListener('click', function () {
            runCheckKeysSelected = addValuesTo(
                runCheckKeysSelected,
                selectedOptions(runCheckAvailable)
            );
            renderRunCheckOptions();
        });
    }
    if (runCheckAddAll) {
        runCheckAddAll.addEventListener('click', function () {
            var visible = [];
            Array.prototype.forEach.call(
                (runCheckAvailable && runCheckAvailable.options) || [],
                function (opt) {
                    if (!opt) return;
                    visible.push(String(opt.value || ''));
                }
            );
            runCheckKeysSelected = addValuesTo(runCheckKeysSelected, visible);
            renderRunCheckOptions();
        });
    }
    if (runCheckRemove) {
        runCheckRemove.addEventListener('click', function () {
            runCheckKeysSelected = removeValuesFrom(
                runCheckKeysSelected,
                selectedOptions(runCheckAvailable)
            );
            renderRunCheckOptions();
        });
    }
    if (runCheckClear) {
        runCheckClear.addEventListener('click', function () {
            runCheckKeysSelected = [];
            renderRunCheckOptions();
        });
    }

    if (runObsdirRefresh) {
        runObsdirRefresh.addEventListener('click', function () {
            var profileId = String((runProfile && runProfile.value) || '').trim();
            loadProfileObsdirs(profileId);
        });
    }
    if (runObsdirAdd) {
        runObsdirAdd.addEventListener('click', function () {
            runObsdirsSelected = addValuesTo(
                runObsdirsSelected,
                selectedOptions(runObsdirAvailable)
            );
            renderRunObsdirOptions();
        });
    }
    if (runObsdirAddAll) {
        runObsdirAddAll.addEventListener('click', function () {
            var visible = [];
            Array.prototype.forEach.call(
                (runObsdirAvailable && runObsdirAvailable.options) || [],
                function (opt) {
                    if (!opt) return;
                    visible.push(String(opt.value || ''));
                }
            );
            runObsdirsSelected = addValuesTo(runObsdirsSelected, visible);
            renderRunObsdirOptions();
        });
    }
    if (runObsdirRemove) {
        runObsdirRemove.addEventListener('click', function () {
            runObsdirsSelected = removeValuesFrom(
                runObsdirsSelected,
                selectedOptions(runObsdirAvailable)
            );
            renderRunObsdirOptions();
        });
    }
    if (runObsdirClear) {
        runObsdirClear.addEventListener('click', function () {
            runObsdirsSelected = [];
            renderRunObsdirOptions();
        });
    }

    function onChipRemoveClick(event) {
        var target = event.target;
        var button = target && target.closest
            ? target.closest('[data-acp-remove-kind]')
            : null;
        var kind;
        var value;
        if (!button) return;
        kind = String(button.getAttribute('data-acp-remove-kind') || '');
        value = String(button.getAttribute('data-acp-remove-value') || '');
        if (!value) return;
        if (kind === 'check') {
            runCheckKeysSelected = removeValuesFrom(runCheckKeysSelected, [value]);
            renderRunCheckOptions();
            return;
        }
        if (kind === 'obsdir') {
            runObsdirsSelected = removeValuesFrom(runObsdirsSelected, [value]);
            renderRunObsdirOptions();
        }
    }
    if (runCheckSelected) {
        runCheckSelected.addEventListener('click', onChipRemoveClick);
    }
    if (runObsdirSelected) {
        runObsdirSelected.addEventListener('click', onChipRemoveClick);
    }

    renderRunCheckOptions();
    renderRunObsdirOptions();
    syncRunControlState();
    loadSections();

    // Re-fetch catalog when navigating back from a check-info page.
    // `pageshow` with persisted=true fires when the browser restores from
    // the back-forward cache (bfcache) without re-running the IIFE.
    window.addEventListener('pageshow', function (evt) {
        if (evt.persisted) {
            loadSections();
        }
    });

    // Fallback: some browsers use Page Visibility instead of bfcache.
    // Re-load when the page becomes visible again after being hidden.
    var _hiddenWhileAway = false;
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            _hiddenWhileAway = true;
        } else if (_hiddenWhileAway) {
            _hiddenWhileAway = false;
            loadSections();
        }
    });
}());