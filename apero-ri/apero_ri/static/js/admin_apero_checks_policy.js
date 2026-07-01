(function () {
    'use strict';

    var cfg = window.ARI_APERO_CHECKS_POLICY || {};
    var sectionsApiUrl = String(cfg.sectionsApiUrl || '');
    var checkInfoBaseUrl = String(cfg.checkInfoBaseUrl || '');
    var rerunNightUrl = String(cfg.rerunNightUrl || '');
    var rerunCheckUrl = String(cfg.rerunCheckUrl || '');
    var advancedRunUrl = String(cfg.advancedRunUrl || '');
    var cleanResetUrl = String(cfg.cleanResetUrl || '');
    var queuePageUrlTemplate = String(cfg.queuePageUrlTemplate || '');
    var obsdirsListUrlTemplate = String(cfg.obsdirsListUrlTemplate || '');
    var excludedObsdirsListUrl = String(cfg.excludedObsdirsListUrl || '');
    var excludedObsdirsRemoveUrl = String(cfg.excludedObsdirsRemoveUrl || '');

    var excludedFilter = document.getElementById('acp-excluded-filter');
    var excludedLoading = document.getElementById('acp-excluded-loading');
    var excludedList = document.getElementById('acp-excluded-list');
    var excludedObsdirsCache = {};

    var healthWrap = document.getElementById('acp-health-wrap');
    var catalogFilter = document.getElementById('acp-catalog-filter');
    var catalogLoading = document.getElementById('acp-catalog-loading');
    var catalogWrap = document.getElementById('acp-check-catalog');
    var catalogRawWrap = document.getElementById('acp-check-catalog-raw');
    var catalogRedWrap = document.getElementById('acp-check-catalog-red');
    var summaryLoading = document.getElementById('acp-summary-loading');
    var summaryWrap = document.getElementById('acp-profile-summaries');
    /* Event delegation: clicks on profile-summary state chips open the overlay */
    if (summaryWrap) {
        summaryWrap.addEventListener('click', function (e) {
            var chip = e.target.closest('[data-state][data-profile-id]');
            if (!chip) return;
            var state     = chip.getAttribute('data-state');
            var profileId = chip.getAttribute('data-profile-id');
            if (state && profileId && window.ACI_RESULTS_OVERLAY) {
                ACI_RESULTS_OVERLAY.open(state, '', profileId);
            }
        });
    }
    var updatedEl = document.getElementById('acp-last-updated');
    var runProfile = document.getElementById('acp-run-profile');
    var runAllChecks = document.getElementById('acp-run-all-checks');
    var runCheckSearch = document.getElementById('acp-run-check-search');
    var runCheckAvailable = document.getElementById('acp-run-check-available');
    var runCheckAdd = document.getElementById('acp-run-check-add');
    var runCheckAddAll = document.getElementById('acp-run-check-add-all');
    var runCheckAddAllRaw = document.getElementById(
        'acp-run-check-add-all-raw'
    );
    var runCheckAddAllRed = document.getElementById(
        'acp-run-check-add-all-red'
    );
    var runCheckRemove = document.getElementById('acp-run-check-remove');
    var runCheckClear = document.getElementById('acp-run-check-clear');
    var runCheckSelected = document.getElementById('acp-run-check-selected');
    var runAllNights = document.getElementById('acp-run-all-nights');
    var runObsdirSearch = document.getElementById('acp-run-obsdir-search');
    var runObsdirAvailable = document.getElementById('acp-run-obsdir-available');
    var runObsdirRefresh = document.getElementById('acp-run-obsdir-refresh');
    var runObsdirAdd = document.getElementById('acp-run-obsdir-add');
    var runObsdirAddAll = document.getElementById('acp-run-obsdir-add-all');
    var runObsdirAddAllNights = document.getElementById(
        'acp-run-obsdir-add-all-nights'
    );
    var runObsdirRemove = document.getElementById('acp-run-obsdir-remove');
    var runObsdirClear = document.getElementById('acp-run-obsdir-clear');
    var runObsdirSelected = document.getElementById('acp-run-obsdir-selected');
    var runSubmit = document.getElementById('acp-run-submit');
    var runQueueLink = document.getElementById('acp-run-queue-link');
    var runCleanReset = document.getElementById('acp-run-clean-reset');
    var runNcores = document.getElementById('acp-run-ncores');
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
        if (!catalogWrap || !catalogRawWrap || !catalogRedWrap) return;
        catalogRawWrap.innerHTML = '';
        catalogRedWrap.innerHTML = '';
        if (!Array.isArray(cards) || !cards.length) {
            catalogRawWrap.innerHTML = '<span class="acp-note">'
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

        var rawHtml = '';
        var redHtml = '';
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
            var isRed = String(item.check_type || '') === 'red';
            var html = '';
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
            if (isRed) {
                redHtml += html;
            } else {
                rawHtml += html;
            }
        });
        catalogRawWrap.innerHTML = rawHtml || '<span class="acp-note">No checks found.</span>';
        catalogRedWrap.innerHTML = redHtml || '<span class="acp-note">No checks found.</span>';
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
            var pid = escHtml(row.profile_id);
            html += '<div class="acp-summary__counts">';
            function chip(state, cls, label, count) {
                if (!count) {
                    return '<span class="acp-chip ' + cls + '">'
                        + label + ': 0</span>';
                }
                return '<button class="acp-chip ' + cls
                    + ' acp-chip--clickable" type="button"'
                    + ' data-state="' + state + '"'
                    + ' data-profile-id="' + pid + '"'
                    + ' title="Click to see ' + label.toLowerCase()
                    + ' nights for ' + pid + '">'
                    + label + ': ' + escHtml(count) + '</button>';
            }
            html += chip('passed',    'acp-chip--passed',    'Passed',    counts.passed    || 0);
            html += chip('overridden','acp-chip--overridden','Overridden', counts.overridden|| 0);
            html += chip('monitored', 'acp-chip--monitored', 'Monitored', counts.monitored || 0);
            html += chip('mixed',     'acp-chip--mixed',     'Overridden and monitored', counts.mixed || 0);
            html += chip('failed',    'acp-chip--failed',    'Failed',    counts.failed    || 0);
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
        // Preserve the in-progress run form across periodic catalog
        // refreshes (loadSections() re-runs on tab-visibility changes and
        // bfcache restores) — only reset selections if the previously
        // chosen profile no longer exists.
        var previousSelection = String(runProfile.value || '').trim();
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
        var stillExists = previousSelection && profileRowsCache.some(
            function (row) {
                return String((row || {}).profile_id || '').trim()
                    === previousSelection;
            }
        );
        if (stillExists) {
            runProfile.value = previousSelection;
        } else {
            runCheckKeysSelected = [];
            runObsdirsSelected = [];
        }
        renderRunCheckOptions();
        renderRunObsdirOptions();
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
        return checkKeysForInstrumentAndType(instrument, '');
    }

    function checkKeysForInstrumentAndType(instrument, checkType) {
        var keys = [];
        var seen = Object.create(null);
        var wanted = String(instrument || '').trim();
        var wantedType = String(checkType || '').trim().toLowerCase();
        checksCatalogCache.forEach(function (item) {
            var checkKey = String((item || {}).check_key || '').trim();
            var insts = Array.isArray((item || {}).instruments)
                ? item.instruments
                : [];
            var itemType = String((item || {}).check_type || '')
                .trim().toLowerCase();
            if (!checkKey || seen[checkKey]) {
                return;
            }
            if (wantedType && itemType !== wantedType) {
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
        if (runCheckAddAllRaw) runCheckAddAllRaw.disabled = disableChecks;
        if (runCheckAddAllRed) runCheckAddAllRed.disabled = disableChecks;
        if (runCheckRemove) runCheckRemove.disabled = disableChecks;
        if (runCheckClear) runCheckClear.disabled = disableChecks;

        if (runObsdirSearch) runObsdirSearch.disabled = disableObsdirs;
        if (runObsdirAvailable) runObsdirAvailable.disabled = disableObsdirs;
        if (runObsdirRefresh) runObsdirRefresh.disabled = !hasProfile;
        if (runObsdirAdd) runObsdirAdd.disabled = disableObsdirs;
        if (runObsdirAddAll) runObsdirAddAll.disabled = disableObsdirs;
        if (runObsdirAddAllNights) {
            runObsdirAddAllNights.disabled = !hasProfile || allObsdirs;
        }
        if (runObsdirRemove) runObsdirRemove.disabled = disableObsdirs;
        if (runObsdirClear) runObsdirClear.disabled = disableObsdirs;

        if (runSubmit) runSubmit.disabled = !hasProfile;
        if (runCleanReset) runCleanReset.disabled = !hasProfile;
        
        updateQueueLink(hasProfile ? String(runProfile.value || '').trim() : '');
    }

    function updateQueueLink(profileId) {
        if (!runQueueLink) return;
        if (!profileId || !queuePageUrlTemplate) {
            runQueueLink.style.display = 'none';
            return;
        }
        var url = queuePageUrlTemplate.replace(
            '__PROFILE_ID__',
            encodeURIComponent(profileId)
        );
        runQueueLink.href = url;
        runQueueLink.style.display = '';
    }

    function getObsdirsListUrl(profileId) {
        var token = '__PROFILE_ID__';
        if (!obsdirsListUrlTemplate || !profileId) return '';
        return obsdirsListUrlTemplate.replace(token, encodeURIComponent(
            String(profileId)
        ));
    }

    function fetchProfileObsdirs(profileId) {
        // Use the dedicated obsdirs-list endpoint, which returns every
        // obs-dir name directly from the YAML directory listing — not
        // paged/capped like the card endpoint (which tops out at 100
        // cards per page).
        var url = getObsdirsListUrl(profileId);
        if (!url) {
            return Promise.resolve([]);
        }
        return fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success
                    || !Array.isArray(data.obsdirs)) {
                    return [];
                }
                return data.obsdirs.slice();
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
        var ncores;
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

            ncores = 0;
            if (runNcores) {
                var raw = parseInt(runNcores.value || '', 10);
                if (!isNaN(raw) && raw > 0) {
                    ncores = raw;
                }
            }

            setRunStatus(
                'Queueing 1 batch run ('
                    + obsdirs.length + ' obs-dir(s), '
                    + (checks.length ? checks.length + ' check(s)' : 'all checks')
                    + (ncores ? ', cores=' + ncores : ', cores=auto')
                    + ')...'
            );

            payload = {
                profile_id: profileId,
                obs_dirs: obsdirs,
                checks: checks,
            };
            if (ncores > 0) {
                payload.ncores = ncores;
            }

            try {
                res = await fetch(advancedRunUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                }).then(function (r) { return r.json(); });

                if (res && res.success) {
                    setRunStatus(
                        'Queued 1 batch task (task_id='
                            + String(res.task_id || '').slice(0, 24)
                            + '...) — '
                            + obsdirs.length + ' obs-dir(s), '
                            + (checks.length
                                ? checks.length + ' check(s)'
                                : 'all checks')
                            + (ncores
                                ? ', cores=' + ncores
                                : ', cores=auto')
                    );
                } else {
                    setRunStatus(
                        'Failed: '
                            + String((res && res.error) || 'Unknown error')
                    );
                }
            } catch (err) {
                setRunStatus('Request failed: ' + String(err));
            }
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

    var buildStatusUrl  = String(cfg.buildStatusUrl || '');
    var _buildPollTimer = null;
    var _buildBannerEl  = null;

    function _getOrCreateBuildBanner() {
        if (_buildBannerEl) return _buildBannerEl;
        _buildBannerEl = document.createElement('div');
        _buildBannerEl.id = 'acp-build-banner';
        _buildBannerEl.className = 'acp-build-banner';
        _buildBannerEl.hidden = true;
        var header = document.querySelector('.ari-page-header') ||
                     document.body.firstElementChild;
        if (header && header.parentNode) {
            header.parentNode.insertBefore(_buildBannerEl, header.nextSibling);
        } else {
            document.body.insertBefore(_buildBannerEl, document.body.firstChild);
        }
        return _buildBannerEl;
    }

    function _showBuildBanner(step, pct) {
        var el = _getOrCreateBuildBanner();
        var barWidth = Math.round(Math.max(4, Math.min(100, pct || 0)));
        el.innerHTML =
            '<span class="acp-build-banner__icon">' +
            '<i class="fa-solid fa-spinner fa-spin"></i></span>' +
            '<span class="acp-build-banner__text">' +
            (step || 'Building index…') + '</span>' +
            '<span class="acp-build-banner__bar-wrap">' +
            '<span class="acp-build-banner__bar" style="width:' +
            barWidth + '%"></span></span>';
        el.hidden = false;
    }

    function _hideBuildBanner() {
        var el = _getOrCreateBuildBanner();
        el.hidden = true;
        if (_buildPollTimer) {
            clearTimeout(_buildPollTimer);
            _buildPollTimer = null;
        }
    }

    function _pollBuildStatus() {
        if (!buildStatusUrl) return;
        fetch(buildStatusUrl)
            .then(function (r) { return r.json(); })
            .then(function (st) {
                if (!st.success) return;
                if (st.is_building) {
                    _showBuildBanner(st.step, st.pct);
                    _buildPollTimer = setTimeout(_pollBuildStatus, 3000);
                } else {
                    // Build finished — refresh the catalog data.
                    _hideBuildBanner();
                    loadSections();
                }
            })
            .catch(function () {
                _buildPollTimer = setTimeout(_pollBuildStatus, 5000);
            });
    }

    function renderExcludedFilterOptions() {
        if (!excludedFilter) return;
        var instruments = Object.keys(excludedObsdirsCache).sort();
        var current = excludedFilter.value || 'all';
        var html = '<option value="all">All instruments</option>';
        instruments.forEach(function (inst) {
            html += '<option value="' + escHtml(inst) + '">'
                + escHtml(inst) + '</option>';
        });
        excludedFilter.innerHTML = html;
        excludedFilter.disabled = instruments.length === 0;
        if (instruments.indexOf(current) >= 0 || current === 'all') {
            excludedFilter.value = current;
        }
    }

    function removeExcludedObsdir(instrument, obsdir) {
        if (!excludedObsdirsRemoveUrl) return;
        if (!window.confirm(
            'Remove “' + obsdir + '” from the excluded list for '
            + instrument + '?\n\nIt will be checked again the next time '
            + 'the APERO Check task runs.'
        )) {
            return;
        }
        fetch(excludedObsdirsRemoveUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instrument: instrument, obsdir: obsdir }),
        }).then(function (resp) {
            return resp.json().then(function (data) {
                if (!resp.ok || data.success === false) {
                    throw new Error(data.error || 'Request failed');
                }
                return data;
            });
        }).then(function (data) {
            excludedObsdirsCache = data.excluded_obsdirs || {};
            renderExcludedFilterOptions();
            renderExcludedList();
        }).catch(function (err) {
            window.alert(String(err || 'Could not remove exclusion.'));
        });
    }

    function renderExcludedList() {
        if (!excludedList) return;
        var selected = excludedFilter
            ? String(excludedFilter.value || 'all')
            : 'all';
        var instruments = Object.keys(excludedObsdirsCache).sort();
        if (selected !== 'all') {
            instruments = instruments.filter(function (inst) {
                return inst === selected;
            });
        }
        if (instruments.length === 0) {
            excludedList.innerHTML = '<div class="acp-note">'
                + 'No excluded directories.</div>';
            return;
        }
        var html = '';
        instruments.forEach(function (inst) {
            var obsdirs = (excludedObsdirsCache[inst] || []).slice().sort();
            html += '<h4 style="margin:0.65rem 0 0.4rem;">'
                + escHtml(inst) + '</h4><div class="acp-grid">';
            obsdirs.forEach(function (obsdir) {
                html += '<div class="acp-card">'
                    + '<div class="acp-card__title acp-card__title--singleline" '
                    + 'title="' + escHtml(obsdir) + '">'
                    + escHtml(obsdir) + '</div>'
                    + '<div class="acp-card__meta">'
                    + '<button type="button" class="ari-btn ari-btn--sm '
                    + 'ari-btn--secondary acp-excluded-remove-btn" '
                    + 'data-instrument="' + escHtml(inst) + '" '
                    + 'data-obsdir="' + escHtml(obsdir) + '">'
                    + '<i class="fa-solid fa-rotate-left"></i> Restore'
                    + '</button>'
                    + '</div></div>';
            });
            html += '</div>';
        });
        excludedList.innerHTML = html;
    }

    if (excludedList) {
        excludedList.addEventListener('click', function (e) {
            var btn = e.target.closest('.acp-excluded-remove-btn');
            if (!btn) return;
            removeExcludedObsdir(
                btn.getAttribute('data-instrument'),
                btn.getAttribute('data-obsdir')
            );
        });
    }
    if (excludedFilter) {
        excludedFilter.addEventListener('change', renderExcludedList);
    }

    function loadExcludedObsdirs() {
        if (!excludedObsdirsListUrl) {
            if (excludedLoading) {
                excludedLoading.textContent = 'Failed to load section.';
            }
            return;
        }
        fetch(excludedObsdirsListUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    if (excludedLoading) {
                        excludedLoading.textContent =
                            data.error || 'Failed to load section.';
                    }
                    return;
                }
                excludedObsdirsCache = data.excluded_obsdirs || {};
                renderExcludedFilterOptions();
                renderExcludedList();
                if (excludedLoading) {
                    excludedLoading.style.display = 'none';
                }
            })
            .catch(function () {
                if (excludedLoading) {
                    excludedLoading.textContent = 'Failed to load section.';
                }
            });
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

                // If the server returned stale / still-building data,
                // start polling so the UI refreshes when the build finishes.
                if (data.is_building) {
                    _pollBuildStatus();
                } else {
                    _hideBuildBanner();
                }
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
    if (runCheckAddAllRaw) {
        runCheckAddAllRaw.addEventListener('click', function () {
            var instrument = profileInstrument(
                String((runProfile && runProfile.value) || '').trim()
            );
            runCheckKeysSelected = addValuesTo(
                runCheckKeysSelected,
                checkKeysForInstrumentAndType(instrument, 'raw')
            );
            renderRunCheckOptions();
        });
    }
    if (runCheckAddAllRed) {
        runCheckAddAllRed.addEventListener('click', function () {
            var instrument = profileInstrument(
                String((runProfile && runProfile.value) || '').trim()
            );
            runCheckKeysSelected = addValuesTo(
                runCheckKeysSelected,
                checkKeysForInstrumentAndType(instrument, 'red')
            );
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
    if (runObsdirAddAllNights) {
        runObsdirAddAllNights.addEventListener('click', function () {
            // Reuse the "Run all obs-dirs" checkbox semantics: at submit
            // time this queries every available obs-dir rather than just
            // the individually-selected list, so it always reflects the
            // full current set (including any added after this click).
            if (runAllNights) {
                runAllNights.checked = true;
            }
            syncRunControlState();
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
    loadExcludedObsdirs();

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