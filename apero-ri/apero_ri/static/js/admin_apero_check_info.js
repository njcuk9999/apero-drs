(function () {
    'use strict';

    var cfg = window.ARI_APERO_CHECK_INFO || {};
    var checkKey = String(cfg.checkKey || '').trim().toUpperCase();
    var ignoreBtn = document.getElementById('aci-toggle-ignore');
    var overrideBtn = document.getElementById('aci-toggle-override');
    var deleteBtn = document.getElementById('aci-delete-test-all-yamls');
    var deleteScope = document.getElementById('aci-delete-profile-scope');
    var saveStatus = document.getElementById('aci-save-status');

    var state = {
        ignored: normalizeList(cfg.ignoredChecks),
        override: normalizeList(cfg.overrideAllowed),
        saving: false,
    };

    function normalizeList(values) {
        var seen = {};
        return (Array.isArray(values) ? values : [])
            .map(function (item) {
                return String(item || '').trim().toUpperCase();
            })
            .filter(function (item) {
                if (!item || seen[item]) {
                    return false;
                }
                seen[item] = true;
                return true;
            })
            .sort();
    }

    function isIgnored() {
        return state.ignored.indexOf(checkKey) >= 0;
    }

    function isOverrideAllowed() {
        return state.override.indexOf(checkKey) >= 0;
    }

    function setStatus(message, error) {
        if (!saveStatus) {
            return;
        }
        saveStatus.textContent = String(message || '');
        saveStatus.style.color = error ? '#b91c1c' : '';
    }

    function setSaving(flag) {
        state.saving = !!flag;
        if (ignoreBtn) {
            ignoreBtn.disabled = state.saving;
        }
        if (overrideBtn) {
            overrideBtn.disabled = state.saving;
        }
        if (deleteBtn) {
            deleteBtn.disabled = state.saving;
        }
        if (deleteScope) {
            deleteScope.disabled = state.saving;
        }
    }

    function updateButtonLabels() {
        if (ignoreBtn) {
            ignoreBtn.textContent = isIgnored()
                ? 'Unignore check'
                : 'Ignore check';
            ignoreBtn.className = isIgnored()
                ? 'ari-btn ari-btn--secondary'
                : 'ari-btn ari-btn--primary';
        }
        if (overrideBtn) {
            overrideBtn.textContent = isOverrideAllowed()
                ? 'Disallow override'
                : 'Allow override';
            overrideBtn.className = isOverrideAllowed()
                ? 'ari-btn ari-btn--secondary'
                : 'ari-btn ari-btn--primary';
        }
    }

    function replaceKey(list, enabled) {
        var next = list.filter(function (item) {
            return item !== checkKey;
        });
        if (enabled) {
            next.push(checkKey);
        }
        return normalizeList(next);
    }

    function savePolicy(previousIgnored, previousOverride) {
        if (!cfg.saveUrl) {
            return Promise.resolve();
        }
        setSaving(true);
        setStatus('Saving policy changes...', false);
        return fetch(cfg.saveUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ignored_checks: state.ignored,
                override_allowed: state.override,
            }),
        })
            .then(function (resp) {
                return resp.json();
            })
            .then(function (data) {
                if (!data.success) {
                    throw new Error(data.error || 'Could not save policy');
                }
                state.ignored = normalizeList(data.ignored_checks || []);
                state.override = normalizeList(data.override_allowed || []);
                updateButtonLabels();
                setStatus('Policy saved.', false);
                window.setTimeout(function () {
                    setStatus('', false);
                    window.location.reload();
                }, 250);
            })
            .catch(function (err) {
                state.ignored = previousIgnored;
                state.override = previousOverride;
                updateButtonLabels();
                setStatus(err && err.message, true);
            })
            .finally(function () {
                setSaving(false);
            });
    }

    function deleteTestFromYamls() {
        if (!cfg.deleteTestUrl || !checkKey) {
            return;
        }
        var selectedScope = 'all';
        if (deleteScope) {
            selectedScope = String(deleteScope.value || 'all').trim();
        }
        var scopeText = selectedScope === 'all'
            ? 'all APERO profiles'
            : selectedScope;
        var ok = window.confirm(
            'Delete test ' + checkKey + ' from YAML files in ' + scopeText
            + '?\n\nThis removes the test row from failures/passes.'
        );
        if (!ok) {
            return;
        }

        setSaving(true);
        setStatus('Deleting test from YAML files...', false);
        fetch(cfg.deleteTestUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                check_key: checkKey,
                profile_scope: selectedScope,
            }),
        })
            .then(function (resp) {
                return resp.json();
            })
            .then(function (data) {
                if (!data.success) {
                    throw new Error(
                        data.error || 'Could not delete test from YAML files'
                    );
                }
                var msg = 'Deleted from ' + String(
                    data.yaml_files_updated || 0
                ) + ' YAML file(s); scanned ' + String(
                    data.yaml_files_scanned || 0
                ) + '.';
                setStatus(msg, false);
            })
            .catch(function (err) {
                setStatus(err && err.message, true);
            })
            .finally(function () {
                setSaving(false);
            });
    }

    function toggleIgnored() {
        var previousIgnored = state.ignored.slice();
        var previousOverride = state.override.slice();
        state.ignored = replaceKey(state.ignored, !isIgnored());
        updateButtonLabels();
        savePolicy(previousIgnored, previousOverride);
    }

    function toggleOverride() {
        var previousIgnored = state.ignored.slice();
        var previousOverride = state.override.slice();
        state.override = replaceKey(state.override, !isOverrideAllowed());
        updateButtonLabels();
        savePolicy(previousIgnored, previousOverride);
    }

    function activateTab(index) {
        var tabs = document.querySelectorAll('[data-aci-tab]');
        var panels = document.querySelectorAll('[data-aci-panel]');
        tabs.forEach(function (tab) {
            var tabIndex = String(tab.getAttribute('data-aci-tab') || '');
            tab.classList.toggle('is-active', tabIndex === index);
        });
        panels.forEach(function (panel) {
            var panelIndex = String(
                panel.getAttribute('data-aci-panel') || ''
            );
            panel.classList.toggle('is-active', panelIndex === index);
        });
    }

    function onTabClick(event) {
        var button = event.target.closest('[data-aci-tab]');
        if (!button) {
            return;
        }
        activateTab(String(button.getAttribute('data-aci-tab') || '0'));
    }

    updateButtonLabels();

    if (ignoreBtn) {
        ignoreBtn.addEventListener('click', toggleIgnored);
    }
    if (overrideBtn) {
        overrideBtn.addEventListener('click', toggleOverride);
    }
    if (deleteBtn) {
        deleteBtn.addEventListener('click', deleteTestFromYamls);
    }

    var tabsWrap = document.getElementById('aci-logic-tabs');
    if (tabsWrap) {
        tabsWrap.addEventListener('click', onTabClick);
    }
}());
