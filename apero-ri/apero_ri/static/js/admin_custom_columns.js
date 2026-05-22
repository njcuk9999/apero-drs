(function () {
    'use strict';

    var cfg = window.ARI_ADMIN_CUSTOM_COLUMNS || {};

    var addBtn = document.getElementById('acc-add');
    var testAllBtn = document.getElementById('acc-test-all');
    var saveBtn = document.getElementById('acc-save');
    var statusEl = document.getElementById('acc-status');
    var tableBody = document.getElementById('acc-rows');
    var profileSelect = document.getElementById('acc-profile');
    var testObjectInput = document.getElementById('acc-test-object');

    var overlay = document.getElementById('acc-custom-overlay');
    var overlayBackdrop = document.getElementById('acc-custom-backdrop');
    var overlayClose = document.getElementById('acc-custom-close');
    var overlayCancel = document.getElementById('acc-custom-cancel');
    var overlayApply = document.getElementById('acc-custom-apply');
    var overlayTest = document.getElementById('acc-custom-test');

    var inputName = document.getElementById('acc-custom-name');
    var inputExpr = document.getElementById('acc-custom-expr');
    var inputCat = document.getElementById('acc-custom-category');
    var inputSub = document.getElementById('acc-custom-subcategory');
    var inputSearch = document.getElementById('acc-custom-search');
    var inputVars = document.getElementById('acc-custom-vars');
    var addVarBtn = document.getElementById('acc-custom-add-var');
    var overlayStatus = document.getElementById('acc-custom-status');

    var state = {
        rows: [],
        propertyCatalog: [],
        profiles: [],
        profileId: '',
        defaultTestObject: '',
        editIndex: -1,
        draftVars: [],
        testPassed: false,
    };

    function buildProfilesUrl() {
        if (!cfg.apiUrl) return '';
        var sep = cfg.apiUrl.indexOf('?') === -1 ? '?' : '&';
        return cfg.apiUrl + sep + 'profiles_only=1';
    }

    function buildApiUrl() {
        if (!cfg.apiUrl) return '';
        var pid = String(state.profileId || '').trim();
        if (!pid) return cfg.apiUrl;
        var sep = cfg.apiUrl.indexOf('?') === -1 ? '?' : '&';
        return cfg.apiUrl + sep + 'profile_id=' + encodeURIComponent(pid);
    }

    function esc(text) {
        var d = document.createElement('div');
        d.textContent = String(text || '');
        return d.innerHTML;
    }

    function setStatus(text, isError) {
        if (!statusEl) return;
        statusEl.textContent = String(text || '');
        statusEl.style.color = isError ? '#a54528' : '#4f613b';
    }

    function setOverlayStatus(text, isError) {
        if (!overlayStatus) return;
        overlayStatus.textContent = String(text || '');
        overlayStatus.style.color = isError ? '#a54528' : '#4f613b';
    }

    function getJson(url) {
        return fetch(url).then(function (r) {
            return r.json();
        });
    }

    function postJson(url, body) {
        return fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body),
        }).then(function (r) {
            return r.json();
        });
    }

    function renderProfileOptions() {
        if (!profileSelect) return;
        profileSelect.innerHTML = '';
        if (!state.profiles.length) {
            var none = document.createElement('option');
            none.value = '';
            none.textContent = 'No accessible profiles';
            profileSelect.appendChild(none);
            profileSelect.disabled = true;
            return;
        }

        state.profiles.forEach(function (row) {
            var option = document.createElement('option');
            option.value = String(row.profile_id || '');
            option.textContent = String(
                row.label || row.profile_id || ''
            );
            if (option.value === state.profileId) option.selected = true;
            profileSelect.appendChild(option);
        });
        if (
            !state.profileId
            || !state.profiles.some(function (row) {
                return String(row.profile_id || '') === state.profileId;
            })
        ) {
            state.profileId = String(
                state.profiles[0].profile_id || ''
            );
            profileSelect.value = state.profileId;
        }
        profileSelect.disabled = false;
    }

    function syncTestObjectInput() {
        if (!testObjectInput) return;
        testObjectInput.value = String(state.defaultTestObject || '');
    }

    function summaryCategoryValue(item) {
        return String(item.category || item.section_title || 'other');
    }

    function summarySubcategoryValue(item) {
        return String(item.subcategory || 'general');
    }

    function summaryPropertyName(item) {
        return String(item.property_name || item.label || item.id || '');
    }

    function summaryPath(item) {
        var cat = summaryCategoryValue(item);
        var sub = summarySubcategoryValue(item);
        return sub ? cat + ' / ' + sub : cat;
    }

    function uniqueSorted(values) {
        var out = [];
        values.forEach(function (val) {
            if (!val || out.indexOf(val) !== -1) return;
            out.push(val);
        });
        out.sort();
        return out;
    }

    function setSelectOptions(selectEl, values, placeholder, keepValue) {
        if (!selectEl) return;
        var keep = String(keepValue || '');
        selectEl.innerHTML = '';
        var opt = document.createElement('option');
        opt.value = '';
        opt.textContent = placeholder;
        selectEl.appendChild(opt);
        values.forEach(function (value) {
            var item = document.createElement('option');
            item.value = value;
            item.textContent = value;
            if (value === keep) item.selected = true;
            selectEl.appendChild(item);
        });
        if (keep && values.indexOf(keep) === -1) {
            selectEl.value = '';
        }
    }

    function renderOverlayFilters() {
        var keepCat = String(inputCat ? inputCat.value : '');
        var keepSub = String(inputSub ? inputSub.value : '');
        var catValues = uniqueSorted(
            state.propertyCatalog.map(summaryCategoryValue)
        );
        setSelectOptions(inputCat, catValues, 'All categories', keepCat);
        var selectedCat = String(inputCat ? inputCat.value : '');
        var subValues = uniqueSorted(
            state.propertyCatalog
                .filter(function (item) {
                    return !selectedCat
                        || summaryCategoryValue(item) === selectedCat;
                })
                .map(summarySubcategoryValue)
        );
        setSelectOptions(
            inputSub,
            subValues,
            'All sub-categories',
            keepSub
        );
    }

    function filteredCatalog() {
        var cat = String(inputCat ? inputCat.value : '');
        var sub = String(inputSub ? inputSub.value : '');
        var rawQuery = String(inputSearch ? inputSearch.value : '')
            .trim()
            .toLowerCase();
        var query = rawQuery.length >= 1 ? rawQuery : '';
        return state.propertyCatalog.filter(function (item) {
            if (cat && summaryCategoryValue(item) !== cat) return false;
            if (sub && summarySubcategoryValue(item) !== sub) return false;
            if (query) {
                var hay = (
                    summaryPropertyName(item)
                    + ' ' + summaryCategoryValue(item)
                    + ' ' + summarySubcategoryValue(item)
                ).toLowerCase();
                if (hay.indexOf(query) === -1) return false;
            }
            return true;
        });
    }

    function renderDraftVars() {
        if (!inputVars) return;
        inputVars.innerHTML = '';
        var options = filteredCatalog();
        state.draftVars.forEach(function (row, idx) {
            var line = document.createElement('div');
            line.className = 'ogs-rename-row ogs-rename-row--triple';

            var letter = document.createElement('input');
            letter.type = 'text';
            letter.className = 'ari-input';
            letter.maxLength = 1;
            letter.placeholder = 'x';
            letter.value = row.letter || '';
            letter.style.maxWidth = '4rem';
            letter.addEventListener('input', function () {
                state.draftVars[idx].letter = String(letter.value || '')
                    .toLowerCase()
                    .replace(/[^a-z]/g, '')
                    .slice(0, 1);
                letter.value = state.draftVars[idx].letter;
                state.testPassed = false;
            });

            var select = document.createElement('select');
            select.className = 'ari-input';
            var blank = document.createElement('option');
            blank.value = '';
            blank.textContent = 'Select property';
            select.appendChild(blank);
            options.forEach(function (item) {
                var opt = document.createElement('option');
                opt.value = item.id;
                opt.textContent = summaryPropertyName(item)
                    + ' [' + summaryPath(item) + ']';
                if (item.id === row.propId) opt.selected = true;
                select.appendChild(opt);
            });
            select.addEventListener('change', function () {
                state.draftVars[idx].propId = String(select.value || '');
                state.testPassed = false;
            });

            var del = document.createElement('button');
            del.type = 'button';
            del.className = 'ogs-card__icon';
            del.title = 'Remove variable';
            del.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
            del.addEventListener('click', function () {
                state.draftVars.splice(idx, 1);
                state.testPassed = false;
                renderDraftVars();
            });

            line.appendChild(letter);
            line.appendChild(select);
            line.appendChild(del);
            inputVars.appendChild(line);
        });
    }

    function varsPayload() {
        var vars = {};
        var seen = {};
        for (var i = 0; i < state.draftVars.length; i += 1) {
            var row = state.draftVars[i];
            var letter = String(row.letter || '').trim().toLowerCase();
            var propId = String(row.propId || '').trim();
            if (!letter || !propId || seen[letter]) return null;
            if (!/^[a-z]$/.test(letter)) return null;
            vars[letter] = propId;
            seen[letter] = true;
        }
        return vars;
    }

    function closeOverlay() {
        if (!overlay) return;
        overlay.style.display = 'none';
        state.editIndex = -1;
        setOverlayStatus('', false);
    }

    function openOverlay(editIndex) {
        if (!overlay) return;
        var isEdit = typeof editIndex === 'number'
            && editIndex >= 0
            && editIndex < state.rows.length;
        state.editIndex = isEdit ? editIndex : -1;

        if (inputCat) inputCat.value = '';
        if (inputSub) inputSub.value = '';
        if (inputSearch) inputSearch.value = '';

        if (isEdit) {
            var row = state.rows[editIndex] || {};
            if (inputName) inputName.value = String(row.name || '');
            if (inputExpr) inputExpr.value = String(row.expression || '');
            state.draftVars = Object.keys(row.variables || {})
                .sort()
                .map(function (key) {
                    return {
                        letter: String(key || '').toLowerCase(),
                        propId: String(row.variables[key] || ''),
                    };
                });
            if (!state.draftVars.length) {
                state.draftVars = [{letter: 'x', propId: ''}];
            }
        } else {
            if (inputName) inputName.value = '';
            if (inputExpr) inputExpr.value = '';
            state.draftVars = [{letter: 'x', propId: ''}];
        }

        state.testPassed = false;
        renderOverlayFilters();
        renderDraftVars();
        setOverlayStatus('', false);
        overlay.style.display = '';
    }

    function testDraft() {
        if (!cfg.testUrl) return;
        var expression = String(inputExpr ? inputExpr.value : '').trim();
        var vars = varsPayload();
        var profileId = String(state.profileId || '').trim();
        if (!profileId) {
            setOverlayStatus('Select a profile first.', true);
            state.testPassed = false;
            return;
        }
        if (!expression || !vars) {
            setOverlayStatus(
                'Define variables and expression first.',
                true
            );
            state.testPassed = false;
            return;
        }
        setOverlayStatus('Testing expression...', false);
        postJson(cfg.testUrl, {
            profile_id: profileId,
            default_test_object: String(state.defaultTestObject || '').trim(),
            expression: expression,
            variables: vars,
        }).then(function (data) {
            if (!data.success) {
                state.testPassed = false;
                setOverlayStatus(data.error || 'Test failed.', true);
                return;
            }
            state.testPassed = true;
            setOverlayStatus(
                'Test OK on ' + String(data.sample_object || 'sample')
                + '. Result: ' + String(data.sample_result),
                false
            );
        }).catch(function () {
            state.testPassed = false;
            setOverlayStatus('Network error during test.', true);
        });
    }

    function testAllRows() {
        var profileId = String(state.profileId || '').trim();
        if (!cfg.testUrl || !profileId) {
            setStatus('Select a profile first.', true);
            return;
        }
        if (!state.rows.length) {
            setStatus('No custom columns to test.', true);
            return;
        }
        setStatus('Testing all custom columns...', false);
        postJson(cfg.testUrl, {
            profile_id: profileId,
            default_test_object: String(state.defaultTestObject || '').trim(),
            test_all: true,
            rows: state.rows,
        }).then(function (data) {
            var results = Array.isArray(data.results) ? data.results : [];
            var failed = results.filter(function (row) {
                return !row.success;
            });
            if (!results.length) {
                setStatus('No custom columns were tested.', true);
                return;
            }
            if (failed.length) {
                setStatus(
                    String(results.length - failed.length)
                    + ' passed, ' + String(failed.length)
                    + ' failed. First failure: '
                    + String(failed[0].name || 'column') + ' - '
                    + String(failed[0].error || 'Test failed.'),
                    true
                );
                return;
            }
            setStatus(
                'All ' + String(results.length)
                + ' custom columns passed.',
                false
            );
        }).catch(function () {
            setStatus('Network error while testing all columns.', true);
        });
    }

    function testSingleRow(index) {
        var profileId = String(state.profileId || '').trim();
        if (!cfg.testUrl || !profileId) {
            setStatus('Select a profile first.', true);
            return;
        }
        if (index < 0 || index >= state.rows.length) {
            setStatus('Invalid row selected.', true);
            return;
        }
        var row = state.rows[index] || {};
        setStatus(
            'Testing ' + String(row.name || 'custom column') + '...',
            false
        );
        postJson(cfg.testUrl, {
            profile_id: profileId,
            default_test_object: String(state.defaultTestObject || '').trim(),
            expression: String(row.expression || ''),
            variables: row.variables || {},
        }).then(function (data) {
            if (!data.success) {
                setStatus(
                    String(row.name || 'Column') + ' failed: '
                    + String(data.error || 'Test failed.'),
                    true
                );
                return;
            }
            setStatus(
                String(row.name || 'Column')
                + ' OK on ' + String(data.sample_object || 'sample')
                + '. Result: ' + String(data.sample_result),
                false
            );
        }).catch(function () {
            setStatus('Network error during row test.', true);
        });
    }

    function applyDraft() {
        var name = String(inputName ? inputName.value : '').trim();
        var expression = String(inputExpr ? inputExpr.value : '').trim();
        var vars = varsPayload();
        if (!name || !expression || !vars) {
            setOverlayStatus(
                'Name, variables, and expression are required.',
                true
            );
            return;
        }
        if (!state.testPassed) {
            setOverlayStatus('Run Test successfully before applying.', true);
            return;
        }

        var row = {
            name: name,
            expression: expression,
            variables: vars,
        };

        if (state.editIndex >= 0 && state.editIndex < state.rows.length) {
            state.rows[state.editIndex] = row;
        } else {
            var key = name.toLowerCase();
            var next = state.rows.filter(function (entry) {
                return String(entry.name || '').toLowerCase() !== key;
            });
            next.push(row);
            state.rows = next;
        }
        state.editIndex = -1;
        closeOverlay();
        renderTable();
        saveRows('Saved custom column.');
    }

    function mappingText(row) {
        var vars = row.variables || {};
        var keys = Object.keys(vars).sort();
        if (!keys.length) return '';
        return keys.map(function (key) {
            var propId = String(vars[key] || '');
            var item = state.propertyCatalog.find(function (entry) {
                return String(entry.id || '') === propId;
            });
            if (!item) {
                return key + '->' + propId;
            }
            return key + '->' + summaryPropertyName(item)
                + ' [' + summaryPath(item) + ']';
        }).join('\n');
    }

    function highlightPythonExpr(expr) {
        var text = String(expr || '');
        if (!text) return '<span class="acc-expr-empty">--</span>';

        var pattern = /("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\b(?:and|or|not|if|else|in|is|True|False|None)\b|\b(?:abs|round|len|min|max|int|float|str|bool|Time)\b|\b(?:math|np|astropy)\b)/g;
        var out = '';
        var last = 0;
        var match;

        while ((match = pattern.exec(text)) !== null) {
            var start = match.index;
            var token = match[0] || '';
            if (start > last) {
                out += esc(text.slice(last, start));
            }
            var cls = 'acc-expr-token--name';
            if (/^['"]/.test(token)) {
                cls = 'acc-expr-token--string';
            } else if (/^\d/.test(token)) {
                cls = 'acc-expr-token--number';
            } else if (/^(and|or|not|if|else|in|is|True|False|None)$/.test(token)) {
                cls = 'acc-expr-token--kw';
            } else if (/^(abs|round|len|min|max|int|float|str|bool|Time)$/.test(token)) {
                cls = 'acc-expr-token--builtin';
            } else if (/^(math|np|astropy)$/.test(token)) {
                cls = 'acc-expr-token--module';
            }
            out += '<span class="' + cls + '">' + esc(token) + '</span>';
            last = start + token.length;
        }

        if (last < text.length) {
            out += esc(text.slice(last));
        }

        return out;
    }

    function renderTable() {
        if (!tableBody) return;
        if (!state.rows.length) {
            tableBody.innerHTML = '<tr><td colspan="4" class="at-muted-hint">'
                + 'No custom columns defined yet.</td></tr>';
            return;
        }
        tableBody.innerHTML = '';
        state.rows.forEach(function (row, index) {
            var tr = document.createElement('tr');
            var mapText = mappingText(row) || '--';
            var exprHtml = highlightPythonExpr(String(row.expression || ''));
            tr.innerHTML = '<td>' + esc(String(row.name || '')) + '</td>'
                + '<td><span class="acc-expr-code">'
                + exprHtml
                + '</span>'
                + '</td>'
                + '<td><span class="acc-vars-cell">'
                + esc(mapText)
                + '</span></td>'
                + '<td><div class="acc-action-icons">'
                + '<button type="button" class="ari-btn ari-btn--secondary ari-btn--sm"'
                + ' data-action="edit" data-index="' + String(index) + '"'
                + ' title="Edit custom column">'
                + '<i class="fa-solid fa-pen"></i></button>'
                + '<button type="button" class="ari-btn ari-btn--secondary ari-btn--sm"'
                + ' data-action="test" data-index="' + String(index) + '"'
                + ' title="Test custom column">'
                + '<i class="fa-solid fa-vial"></i></button>'
                + '<button type="button" class="ari-btn ari-btn--danger ari-btn--sm"'
                + ' data-action="remove" data-index="' + String(index) + '"'
                + ' title="Remove custom column">'
                + '<i class="fa-solid fa-trash"></i></button>'
                + '</div></td>';
            tableBody.appendChild(tr);
        });

        tableBody.querySelectorAll('button[data-action="edit"]')
            .forEach(function (btn) {
                btn.addEventListener('click', function () {
                    var idx = Number(btn.dataset.index || -1);
                    if (idx < 0 || idx >= state.rows.length) return;
                    openOverlay(idx);
                });
            });

        tableBody.querySelectorAll('button[data-action="remove"]')
            .forEach(function (btn) {
                btn.addEventListener('click', function () {
                    var idx = Number(btn.dataset.index || -1);
                    if (idx < 0 || idx >= state.rows.length) return;
                    state.rows.splice(idx, 1);
                    renderTable();
                });
            });

        tableBody.querySelectorAll('button[data-action="test"]')
            .forEach(function (btn) {
                btn.addEventListener('click', function () {
                    var idx = Number(btn.dataset.index || -1);
                    testSingleRow(idx);
                });
            });
    }

    function loadRows() {
        var apiUrl = buildApiUrl();
        if (!apiUrl) return;
        setStatus('Loading custom columns...', false);
        getJson(apiUrl).then(function (data) {
            if (!data.success) {
                setStatus(data.error || 'Failed to load custom columns.', true);
                return;
            }
            state.profiles = Array.isArray(data.profiles)
                ? data.profiles
                : state.profiles;
            state.profileId = String(
                data.profile_id || state.profileId || ''
            );
            state.defaultTestObject = String(
                data.default_test_object || ''
            );
            renderProfileOptions();
            syncTestObjectInput();
            state.rows = Array.isArray(data.rows) ? data.rows : [];
            state.propertyCatalog = Array.isArray(data.property_catalog)
                ? data.property_catalog
                : [];
            renderTable();
            setStatus(
                'Loaded ' + String(state.rows.length)
                + ' custom columns.',
                false
            );
        }).catch(function () {
            setStatus('Network error while loading custom columns.', true);
        });
    }

    function saveRows(successMessage) {
        var apiUrl = buildApiUrl();
        if (!apiUrl) return;
        var profileId = String(state.profileId || '').trim();
        if (!profileId) {
            setStatus('Select a profile before saving.', true);
            return;
        }
        setStatus('Saving custom columns...', false);
        postJson(apiUrl, {
            profile_id: profileId,
            default_test_object: String(state.defaultTestObject || '').trim(),
            rows: state.rows,
        }).then(function (data) {
            if (!data.success) {
                setStatus(data.error || 'Save failed.', true);
                return;
            }
            state.profiles = Array.isArray(data.profiles)
                ? data.profiles
                : state.profiles;
            state.profileId = String(
                data.profile_id || state.profileId || ''
            );
            state.defaultTestObject = String(
                data.default_test_object || state.defaultTestObject || ''
            );
            renderProfileOptions();
            syncTestObjectInput();
            state.rows = Array.isArray(data.rows) ? data.rows : state.rows;
            state.propertyCatalog = Array.isArray(data.property_catalog)
                ? data.property_catalog
                : state.propertyCatalog;
            renderTable();
            setStatus(successMessage || 'Saved successfully.', false);
        }).catch(function () {
            setStatus('Network error while saving custom columns.', true);
        });
    }

    function loadProfiles() {
        var profilesUrl = buildProfilesUrl();
        if (!profilesUrl) return;
        setStatus('Loading profiles...', false);
        getJson(profilesUrl).then(function (data) {
            if (!data.success) {
                setStatus(data.error || 'Failed to load profiles.', true);
                return;
            }
            state.profiles = Array.isArray(data.profiles)
                ? data.profiles
                : [];
            state.profileId = String(data.profile_id || state.profileId || '');
            state.defaultTestObject = String(
                data.default_test_object || ''
            );
            renderProfileOptions();
            syncTestObjectInput();
            if (!state.profileId) {
                setStatus('No accessible profiles.', true);
                renderTable();
                return;
            }
            setStatus('Profiles loaded.', false);
            loadRows();
        }).catch(function () {
            setStatus('Network error while loading profiles.', true);
        });
    }

    if (addBtn) {
        addBtn.addEventListener('click', function () {
            openOverlay(-1);
        });
    }
    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            saveRows();
        });
    }
    if (testAllBtn) {
        testAllBtn.addEventListener('click', testAllRows);
    }
    if (overlayClose) {
        overlayClose.addEventListener('click', closeOverlay);
    }
    if (overlayCancel) {
        overlayCancel.addEventListener('click', closeOverlay);
    }
    if (overlayBackdrop) {
        overlayBackdrop.addEventListener('click', closeOverlay);
    }
    if (overlayApply) {
        overlayApply.addEventListener('click', applyDraft);
    }
    if (overlayTest) {
        overlayTest.addEventListener('click', testDraft);
    }
    if (addVarBtn) {
        addVarBtn.addEventListener('click', function () {
            state.draftVars.push({letter: 'x', propId: ''});
            state.testPassed = false;
            renderDraftVars();
        });
    }
    if (inputExpr) {
        inputExpr.addEventListener('input', function () {
            state.testPassed = false;
        });
    }
    if (inputName) {
        inputName.addEventListener('input', function () {
            state.testPassed = false;
        });
    }
    if (inputCat) {
        inputCat.addEventListener('change', function () {
            if (inputSub) inputSub.value = '';
            state.testPassed = false;
            renderOverlayFilters();
            renderDraftVars();
        });
    }
    if (inputSub) {
        inputSub.addEventListener('change', function () {
            state.testPassed = false;
            renderDraftVars();
        });
    }
    if (inputSearch) {
        inputSearch.addEventListener('input', function () {
            renderDraftVars();
        });
    }
    if (profileSelect) {
        profileSelect.addEventListener('change', function () {
            state.profileId = String(profileSelect.value || '').trim();
            loadRows();
        });
    }
    if (testObjectInput) {
        testObjectInput.addEventListener('change', function () {
            state.defaultTestObject = String(
                testObjectInput.value || ''
            ).trim();
            saveRows('Saved test object.');
        });
    }

    loadProfiles();
}());
