/* ==========================================================================
   Object Groups page logic – shared object collections.
   Depends on window.ARI_OBJECT_GROUPS being set.
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_OBJECT_GROUPS || {};

    /* ── DOM refs ────────────────────────────────────────────────── */
    var loadingEl = document.getElementById('og-loading');
    var errorEl = document.getElementById('og-error');
    var container = document.getElementById(
        'og-groups-container'
    );
    var emptyEl = document.getElementById('og-empty');
    var groupCountEl = document.getElementById(
        'og-group-count'
    );
    var groupPluralEl = document.getElementById(
        'og-group-plural'
    );
    var createBtn = document.getElementById(
        'og-create-group-btn'
    );
    var filterInput = document.getElementById(
        'og-filter-input'
    );

    /* Add-objects modal */
    var addModal = document.getElementById('og-add-modal');
    var addModalClose = document.getElementById(
        'og-add-modal-close'
    );
    var addQuery = document.getElementById('og-add-query');
    var addGroupInput = document.getElementById(
        'og-add-group'
    );
    var addSingleBtn = document.getElementById(
        'og-add-single-btn'
    );
    var addBulkFile = document.getElementById(
        'og-add-bulk-file'
    );
    var addBulkBtn = document.getElementById(
        'og-add-bulk-btn'
    );
    var addBulkText = document.getElementById(
        'og-add-bulk-text'
    );
    var addTextBtn = document.getElementById(
        'og-add-text-btn'
    );
    var addBulkResult = document.getElementById(
        'og-add-bulk-result'
    );
    var addTextResult = document.getElementById(
        'og-add-text-result'
    );
    var addSingleResult = document.getElementById(
        'og-add-single-result'
    );

    /* Rename modal */
    var renameModal = document.getElementById(
        'og-rename-modal'
    );
    var renameClose = document.getElementById(
        'og-rename-modal-close'
    );
    var renameInput = document.getElementById(
        'og-rename-input'
    );
    var renameOld = document.getElementById('og-rename-old');
    var renameSubmit = document.getElementById(
        'og-rename-submit'
    );

    /* Summary overlay */
    var summaryOverlay = document.getElementById(
        'og-summary-overlay'
    );
    var summaryBackdrop = document.getElementById(
        'og-summary-backdrop'
    );
    var summaryClose = document.getElementById(
        'og-summary-close'
    );
    var summaryCloseBtn = document.getElementById(
        'og-summary-close-btn'
    );
    var summarySearch = document.getElementById(
        'og-summary-search'
    );
    var summaryRenameOpen = document.getElementById(
        'og-summary-rename-open'
    );
    var summaryRenameOverlay = document.getElementById(
        'og-summary-rename-overlay'
    );
    var summaryRenameBackdrop = document.getElementById(
        'og-summary-rename-backdrop'
    );
    var summaryRenameClose = document.getElementById(
        'og-summary-rename-close'
    );
    var summaryRenameCancel = document.getElementById(
        'og-summary-rename-cancel'
    );
    var summaryRenameApply = document.getElementById(
        'og-summary-rename-apply'
    );
    var summaryCustomOpen = document.getElementById(
        'og-summary-custom-open'
    );
    var summaryCustomOverlay = document.getElementById(
        'og-summary-custom-overlay'
    );
    var summaryCustomBackdrop = document.getElementById(
        'og-summary-custom-backdrop'
    );
    var summaryCustomClose = document.getElementById(
        'og-summary-custom-close'
    );
    var summaryCustomCancel = document.getElementById(
        'og-summary-custom-cancel'
    );
    var summaryCustomAddVar = document.getElementById(
        'og-summary-custom-add-var'
    );
    var summaryCustomName = document.getElementById(
        'og-summary-custom-name'
    );
    var summaryCustomCategory = document.getElementById(
        'og-summary-custom-category'
    );
    var summaryCustomSubcategory = document.getElementById(
        'og-summary-custom-subcategory'
    );
    var summaryCustomSearch = document.getElementById(
        'og-summary-custom-search'
    );
    var summaryCustomExpr = document.getElementById(
        'og-summary-custom-expr'
    );
    var summaryCustomExprHelpToggle = document.getElementById(
        'og-summary-custom-expr-help-toggle'
    );
    var summaryCustomExprHelp = document.getElementById(
        'og-summary-custom-expr-help'
    );
    var summaryCustomVars = document.getElementById(
        'og-summary-custom-vars'
    );
    var summaryCustomTest = document.getElementById(
        'og-summary-custom-test'
    );
    var summaryCustomSave = document.getElementById(
        'og-summary-custom-save'
    );
    var summaryCustomStatus = document.getElementById(
        'og-summary-custom-status'
    );
    var summaryRenameList = document.getElementById(
        'og-summary-rename-list'
    );
    var summaryCategory = document.getElementById(
        'og-summary-category'
    );
    var summarySubcategory = document.getElementById(
        'og-summary-subcategory'
    );
    var summaryList = document.getElementById(
        'og-summary-list'
    );
    var summarySelected = document.getElementById(
        'og-summary-selected'
    );
    var summaryStatus = document.getElementById(
        'og-summary-status'
    );
    var summaryGenerateBtn = document.getElementById(
        'og-summary-generate'
    );

    var groupsData = [];
    var canModerate = false;
    var summaryState = {
        groupName: '',
        propertyCatalog: [],
        selectedColumns: [],
        selectedAliases: {},
        customColumns: [],
        adminCustomColumns: [],
        allowedExpressionRows: [],
        customEditIndex: -1,
        customDraftVars: [],
        customTestPassed: false,
        pageUrl: '',
    };

    /* ── Helpers ─────────────────────────────────────────────────── */
    function hide(el) {
        if (el) el.style.display = 'none';
    }
    function show(el) {
        if (el) el.style.display = '';
    }
    function esc(text) {
        var d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }
    function postJson(url, body) {
        return fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        }).then(function (r) { return r.json(); });
    }
    function getJson(url) {
        return fetch(url).then(function (r) {
            return r.json();
        });
    }
    function hasSummaryColumn(propId) {
        return summaryState.selectedColumns.indexOf(propId) !== -1;
    }
    function summaryCategoryValue(item) {
        return String(item.category || item.section_title || 'other');
    }
    function summarySubcategoryValue(item) {
        return String(item.subcategory || 'general');
    }
    function summaryLblCategoryValue(item) {
        return String(item.lbl_category || '');
    }
    function summaryPropertyName(item) {
        return String(item.property_name || item.label || item.id || '');
    }
    function summaryPath(item) {
        return [
            summaryCategoryValue(item),
            summarySubcategoryValue(item),
        ].join(' / ');
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
            if (value === keep) {
                item.selected = true;
            }
            selectEl.appendChild(item);
        });
        if (keep && values.indexOf(keep) === -1) {
            selectEl.value = '';
        }
    }
    function renderSummaryFilters() {
        var categoryKeep = String(
            summaryCategory ? summaryCategory.value : ''
        );
        var subKeep = String(
            summarySubcategory ? summarySubcategory.value : ''
        );

        var categoryValues = uniqueSorted(
            summaryState.propertyCatalog.map(summaryCategoryValue)
        );
        setSelectOptions(
            summaryCategory,
            categoryValues,
            'All categories',
            categoryKeep
        );
        var selectedCategory = String(
            summaryCategory ? summaryCategory.value : ''
        );

        var subValues = uniqueSorted(
            summaryState.propertyCatalog
                .filter(function (item) {
                    return !selectedCategory
                        || summaryCategoryValue(item) === selectedCategory;
                })
                .map(summarySubcategoryValue)
        );
        setSelectOptions(
            summarySubcategory,
            subValues,
            'All sub-categories',
            subKeep
        );
    }
    function getSummaryLabel(item) {
        var alias = String(
            summaryState.selectedAliases[item.id] || ''
        ).trim();
        return alias || item.label;
    }
    function closeSummaryRenameOverlay() {
        if (summaryRenameOverlay) {
            summaryRenameOverlay.style.display = 'none';
        }
    }
    function openSummaryRenameOverlay(focusPropId) {
        if (!summaryRenameOverlay || !summaryRenameList) return;
        if (!summaryState.selectedColumns.length) {
            setSummaryStatus('Select at least one column first.', true);
            return;
        }
        summaryRenameList.innerHTML = '';
        summaryState.selectedColumns.forEach(function (propId) {
            var item = summaryState.propertyCatalog.find(
                function (entry) {
                    return entry.id === propId;
                }
            );
            if (!item) return;
            var row = document.createElement('div');
            row.className = 'ogs-rename-row';
            var original = '<div class="ogs-rename-original">'
                + '<div class="ogs-rename-original-title">'
                + esc(summaryPropertyName(item))
                + '</div><div class="ogs-rename-original-meta">'
                + esc(summaryPath(item))
                + '</div></div>';
            var input = '<input type="text" class="ari-input"'
                + ' data-prop-id="' + esc(propId) + '"'
                + ' placeholder="Optional custom column name"'
                + ' value="'
                + esc(summaryState.selectedAliases[propId] || '')
                + '">';
            row.innerHTML = original + input;
            summaryRenameList.appendChild(row);
        });
        summaryRenameOverlay.style.display = '';
        if (focusPropId) {
            var target = summaryRenameList.querySelector(
                'input[data-prop-id="' + focusPropId + '"]'
            );
            if (target) target.focus();
        }
    }
    function applySummaryRenameOverlay() {
        if (!summaryRenameList) return;
        var nextAliases = {};
        summaryRenameList.querySelectorAll('input[data-prop-id]')
            .forEach(function (input) {
                var propId = String(input.dataset.propId || '').trim();
                var value = String(input.value || '').trim();
                if (propId && value) {
                    nextAliases[propId] = value;
                }
            });
        summaryState.selectedAliases = nextAliases;
        closeSummaryRenameOverlay();
        renderSummaryPicker();
    }
    function setSummaryStatus(text, isError) {
        if (!summaryStatus) return;
        summaryStatus.textContent = text || '';
        summaryStatus.style.color = isError
            ? '#a54528' : '#4f613b';
    }
    function setSummaryCustomStatus(text, isError) {
        if (!summaryCustomStatus) return;
        summaryCustomStatus.textContent = text || '';
        summaryCustomStatus.style.color = isError
            ? '#a54528' : '#4f613b';
    }
    function moveSummaryCustomColumn(fromIndex, toIndex) {
        if (fromIndex < 0 || toIndex < 0) return;
        if (fromIndex >= summaryState.customColumns.length) return;
        if (toIndex >= summaryState.customColumns.length) return;
        if (fromIndex === toIndex) return;
        var cols = summaryState.customColumns.slice();
        var moved = cols.splice(fromIndex, 1)[0];
        cols.splice(toIndex, 0, moved);
        summaryState.customColumns = cols;
        renderSummaryPicker();
    }
    function updateSummaryCustomSaveState() {
        if (!summaryCustomSave) return;
        summaryCustomSave.disabled = !summaryState.customTestPassed;
    }
    function invalidateSummaryCustomTest() {
        summaryState.customTestPassed = false;
        updateSummaryCustomSaveState();
    }
    function getAdminCustomDefinition(propId) {
        var pid = String(propId || '').trim();
        if (!pid || pid.indexOf('admin_custom::') !== 0) {
            return null;
        }
        var name = pid.slice('admin_custom::'.length);
        var rows = Array.isArray(summaryState.adminCustomColumns)
            ? summaryState.adminCustomColumns
            : [];
        for (var i = 0; i < rows.length; i += 1) {
            var row = rows[i] || {};
            if (String(row.name || '').trim() === name) {
                return row;
            }
        }
        return null;
    }
    function cloneAdminCustomToUser(propId) {
        var source = getAdminCustomDefinition(propId);
        if (!source) {
            setSummaryStatus(
                'Admin custom definition could not be loaded.',
                true
            );
            return;
        }
        openSummaryCustomOverlay(-1, source);
    }
    function filteredCustomCatalog() {
        var cat = String(
            summaryCustomCategory ? summaryCustomCategory.value : ''
        );
        var sub = String(
            summaryCustomSubcategory ? summaryCustomSubcategory.value : ''
        );
        var rawQuery = String(
            summaryCustomSearch ? summaryCustomSearch.value : ''
        ).trim().toLowerCase();
        var query = rawQuery.length >= 3 ? rawQuery : '';
        return summaryState.propertyCatalog.filter(function (item) {
            if (cat && summaryCategoryValue(item) !== cat) {
                return false;
            }
            if (sub && summarySubcategoryValue(item) !== sub) {
                return false;
            }
            if (query) {
                var haystack = (
                    summaryPropertyName(item)
                    + ' ' + summaryCategoryValue(item)
                    + ' ' + summarySubcategoryValue(item)
                ).toLowerCase();
                if (haystack.indexOf(query) === -1) {
                    return false;
                }
            }
            return true;
        });
    }
    function renderSummaryCustomFilters() {
        var keepCat = String(
            summaryCustomCategory ? summaryCustomCategory.value : ''
        );
        var keepSub = String(
            summaryCustomSubcategory ? summaryCustomSubcategory.value : ''
        );
        var catValues = uniqueSorted(
            summaryState.propertyCatalog.map(summaryCategoryValue)
        );
        setSelectOptions(
            summaryCustomCategory,
            catValues,
            'All categories',
            keepCat
        );
        var selectedCat = String(
            summaryCustomCategory ? summaryCustomCategory.value : ''
        );
        var subValues = uniqueSorted(
            summaryState.propertyCatalog
                .filter(function (item) {
                    return !selectedCat
                        || summaryCategoryValue(item) === selectedCat;
                })
                .map(summarySubcategoryValue)
        );
        setSelectOptions(
            summaryCustomSubcategory,
            subValues,
            'All sub-categories',
            keepSub
        );
    }
    function propertyOptionHtml(propId) {
        var item = summaryState.propertyCatalog.find(function (entry) {
            return entry.id === propId;
        });
        if (!item) {
            return String(propId);
        }
        return summaryPropertyName(item) + ' [' + summaryPath(item) + ']';
    }
    function renderSummaryCustomVars() {
        if (!summaryCustomVars) return;
        summaryCustomVars.innerHTML = '';
        var options = filteredCustomCatalog();
        summaryState.customDraftVars.forEach(function (row, idx) {
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
                summaryState.customDraftVars[idx].letter = String(
                    letter.value || ''
                ).toLowerCase().replace(/[^a-z]/g, '').slice(0, 1);
                letter.value = summaryState.customDraftVars[idx].letter;
                invalidateSummaryCustomTest();
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
                if (item.id === row.propId) {
                    opt.selected = true;
                }
                select.appendChild(opt);
            });
            select.addEventListener('change', function () {
                summaryState.customDraftVars[idx].propId = String(
                    select.value || ''
                );
                invalidateSummaryCustomTest();
            });

            var del = document.createElement('button');
            del.type = 'button';
            del.className = 'ogs-card__icon';
            del.title = 'Remove variable';
            del.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
            del.addEventListener('click', function () {
                summaryState.customDraftVars.splice(idx, 1);
                invalidateSummaryCustomTest();
                renderSummaryCustomVars();
            });

            line.appendChild(letter);
            line.appendChild(select);
            line.appendChild(del);
            summaryCustomVars.appendChild(line);
        });
    }
    function renderSummaryExprHelp() {
        if (!summaryCustomExprHelp) return;
        var rows = Array.isArray(summaryState.allowedExpressionRows)
            ? summaryState.allowedExpressionRows
            : [];
        if (!rows.length) {
            summaryCustomExprHelp.innerHTML = '<div class="ogs-list__empty">'
                + 'No configured expression rules.'
                + '</div>';
            return;
        }
        var body = rows.map(function (row) {
            var expr = esc(String(row.expression || ''));
            var comment = esc(String(row.comment || ''));
            return '<tr><td><code>' + expr + '</code></td><td>'
                + comment + '</td></tr>';
        }).join('');
        summaryCustomExprHelp.innerHTML = '<table><thead><tr>'
            + '<th>Expression</th><th>Comment</th></tr></thead><tbody>'
            + body
            + '</tbody></table>';
    }
    function toggleSummaryExprHelp() {
        if (!summaryCustomExprHelp) return;
        var isHidden = summaryCustomExprHelp.style.display === 'none';
        if (isHidden) {
            renderSummaryExprHelp();
            summaryCustomExprHelp.style.display = '';
            return;
        }
        summaryCustomExprHelp.style.display = 'none';
    }
    function closeSummaryCustomOverlay() {
        if (!summaryCustomOverlay) return;
        summaryCustomOverlay.style.display = 'none';
        if (summaryCustomExprHelp) {
            summaryCustomExprHelp.style.display = 'none';
        }
        summaryState.customEditIndex = -1;
        setSummaryCustomStatus('', false);
    }
    function openSummaryCustomOverlay(editIndex, seedRow) {
        if (!summaryCustomOverlay) return;
        var isEdit = (
            typeof editIndex === 'number'
            && editIndex >= 0
            && editIndex < summaryState.customColumns.length
        );
        summaryState.customEditIndex = isEdit ? editIndex : -1;

        if (summaryCustomCategory) summaryCustomCategory.value = '';
        if (summaryCustomSubcategory) summaryCustomSubcategory.value = '';
        if (summaryCustomSearch) summaryCustomSearch.value = '';

        if (isEdit) {
            var row = summaryState.customColumns[editIndex] || {};
            if (summaryCustomName) {
                summaryCustomName.value = String(row.name || '');
            }
            if (summaryCustomExpr) {
                summaryCustomExpr.value = String(row.expression || '');
            }
            summaryState.customDraftVars = Object.keys(row.variables || {})
                .sort()
                .map(function (key) {
                    return {
                        letter: String(key || '').toLowerCase(),
                        propId: String(row.variables[key] || ''),
                    };
                });
            if (!summaryState.customDraftVars.length) {
                summaryState.customDraftVars = [
                    {letter: 'x', propId: ''},
                ];
            }
        } else if (seedRow && typeof seedRow === 'object') {
            if (summaryCustomName) {
                summaryCustomName.value = String(seedRow.name || '');
            }
            if (summaryCustomExpr) {
                summaryCustomExpr.value = String(seedRow.expression || '');
            }
            summaryState.customDraftVars = Object.keys(
                seedRow.variables || {}
            ).sort().map(function (key) {
                return {
                    letter: String(key || '').toLowerCase(),
                    propId: String(seedRow.variables[key] || ''),
                };
            });
            if (!summaryState.customDraftVars.length) {
                summaryState.customDraftVars = [
                    {letter: 'x', propId: ''},
                ];
            }
        } else {
            if (summaryCustomName) summaryCustomName.value = '';
            if (summaryCustomExpr) summaryCustomExpr.value = '';
            summaryState.customDraftVars = [
                {letter: 'x', propId: ''},
            ];
        }

        summaryState.customTestPassed = false;
        renderSummaryCustomFilters();
        renderSummaryCustomVars();
        if (summaryCustomExprHelp) {
            summaryCustomExprHelp.style.display = 'none';
        }
        updateSummaryCustomSaveState();
        setSummaryCustomStatus('', false);
        summaryCustomOverlay.style.display = '';
        if (summaryCustomName) summaryCustomName.focus();
    }
    function customDraftPayload() {
        var vars = {};
        var seen = {};
        for (var i = 0; i < summaryState.customDraftVars.length; i += 1) {
            var row = summaryState.customDraftVars[i];
            var letter = String(row.letter || '').trim().toLowerCase();
            var propId = String(row.propId || '').trim();
            if (!letter || !propId || seen[letter]) {
                return null;
            }
            if (!/^[a-z]$/.test(letter)) {
                return null;
            }
            vars[letter] = propId;
            seen[letter] = true;
        }
        return vars;
    }
    function testSummaryCustomColumn() {
        if (!cfg.summaryCustomTestApiUrl) return;
        var expression = String(
            summaryCustomExpr ? summaryCustomExpr.value : ''
        ).trim();
        var vars = customDraftPayload();
        if (!expression || !vars) {
            invalidateSummaryCustomTest();
            setSummaryCustomStatus(
                'Define variables and expression first.',
                true
            );
            return;
        }
        setSummaryCustomStatus('Testing expression...', false);
        postJson(cfg.summaryCustomTestApiUrl, {
            profile_id: cfg.profileId,
            group: summaryState.groupName,
            expression: expression,
            variables: vars,
        }).then(function (data) {
            if (!data.success) {
                invalidateSummaryCustomTest();
                setSummaryCustomStatus(data.error || 'Test failed.', true);
                return;
            }
            summaryState.customTestPassed = true;
            updateSummaryCustomSaveState();
            setSummaryCustomStatus(
                'Test OK. Result: ' + String(data.sample_result),
                false
            );
        }).catch(function () {
            invalidateSummaryCustomTest();
            setSummaryCustomStatus('Network error during test.', true);
        });
    }
    function saveSummaryCustomColumn() {
        var name = String(
            summaryCustomName ? summaryCustomName.value : ''
        ).trim();
        var expression = String(
            summaryCustomExpr ? summaryCustomExpr.value : ''
        ).trim();
        var vars = customDraftPayload();
        if (!name || !expression || !vars) {
            setSummaryCustomStatus(
                'Name, variables, and expression are required.',
                true
            );
            return;
        }
        if (!summaryState.customTestPassed) {
            setSummaryCustomStatus(
                'Run Test successfully before saving.',
                true
            );
            return;
        }
        var row = {
            name: name,
            expression: expression,
            variables: vars,
        };

        if (summaryState.customEditIndex >= 0
            && summaryState.customEditIndex < summaryState.customColumns.length) {
            summaryState.customColumns[summaryState.customEditIndex] = row;
        } else {
            var key = name.toLowerCase();
            var next = summaryState.customColumns.filter(function (entry) {
                return String(entry.name || '').toLowerCase() !== key;
            });
            next.push(row);
            summaryState.customColumns = next;
        }
        summaryState.customEditIndex = -1;
        closeSummaryCustomOverlay();
        renderSummaryPicker();
    }
    function renderBulkAddResult(host, data) {
        if (!host) return;
        if (!data.success) {
            host.textContent = data.error || 'Bulk add failed.';
            show(host);
            return;
        }
        var msg = 'Added: ' + (data.added || 0)
            + ', skipped: ' + (data.skipped || 0);
        if (data.not_found && data.not_found.length) {
            msg += ', not found: ' + data.not_found.length;
            msg += '<br><small>Unresolved: '
                + data.not_found.map(esc).join(', ')
                + '</small>';
        }
        host.innerHTML = msg;
        show(host);
    }

    /* ================================================================
       Load group list
       ================================================================ */
    function loadGroups() {
        hide(errorEl);
        hide(emptyEl);
        hide(container);
        show(loadingEl);

        var url = cfg.listApiUrl +
            '?profile_id=' +
            encodeURIComponent(cfg.profileId);

        getJson(url).then(function (data) {
            hide(loadingEl);
            if (!data.success) {
                errorEl.textContent = data.error ||
                    'Failed to load groups.';
                show(errorEl);
                return;
            }
            groupsData = data.groups || [];
            canModerate = data.can_moderate || false;
            renderGroups();
        }).catch(function () {
            hide(loadingEl);
            errorEl.textContent =
                'Network error loading groups.';
            show(errorEl);
        });
    }

    /* ================================================================
       Render groups as expandable section cards
       ================================================================ */
    function renderGroups() {
        groupCountEl.textContent = String(groupsData.length);
        groupPluralEl.textContent =
            groupsData.length === 1 ? '' : 's';

        if (!groupsData.length) {
            container.innerHTML = '';
            hide(container);
            show(emptyEl);
            return;
        }
        hide(emptyEl);
        show(container);

        var html = '';
        groupsData.forEach(function (g) {
            html += '<div class="at-section-card' +
                ' og-group-section"' +
                ' data-group="' + esc(g.name) + '">';
            html += '<div class="at-section-card__header"' +
                ' style="cursor:pointer;">';
            html += '<i class="fa-solid fa-layer-group' +
                ' ari-fav-section__icon"></i>';
            html += '<span class="ari-fav-section__name">' +
                esc(g.name) + '</span>';
            html += '<span class="ari-fav-section__count">' +
                '(' + (g.object_count || 0) + ')</span>';
            html += '<span class="at-muted-hint"' +
                ' style="margin-left:0.6em;font-size:0.8em;">' +
                'by ' + esc(g.created_by || '?') + '</span>';
            html += '<div class="op-section-controls">';
            html += '<button type="button"' +
                ' class="ari-btn ari-btn--sm' +
                ' ari-btn--secondary og-summary-btn"' +
                ' data-group="' + esc(g.name) + '"' +
                ' title="Open summary table builder">' +
                'Summary Table</button>';
            html += '<button type="button"' +
                ' class="ari-btn ari-btn--sm' +
                ' ari-btn--secondary og-add-objects-btn"' +
                ' data-group="' + esc(g.name) + '"' +
                ' title="Add objects to this group">' +
                '<i class="fa-solid fa-plus"></i></button>';
            if (g.can_edit) {
                html += ' <button type="button"' +
                    ' class="ari-btn ari-btn--sm' +
                    ' ari-btn--secondary og-rename-btn"' +
                    ' data-group="' + esc(g.name) + '"' +
                    ' title="Rename group">' +
                    '<i class="fa-solid fa-pen"></i>' +
                    '</button>';
            }
            if (g.can_delete) {
                html += ' <button type="button"' +
                    ' class="ari-btn ari-btn--sm' +
                    ' ari-btn--danger og-delete-btn"' +
                    ' data-group="' + esc(g.name) + '"' +
                    ' title="Delete group">' +
                    '<i class="fa-solid fa-trash"></i>' +
                    '</button>';
            }
            html += '<button type="button"' +
                ' class="ari-fav-section__collapse-btn' +
                ' op-section-btn og-toggle-btn"' +
                ' data-group="' + esc(g.name) + '"' +
                ' aria-expanded="false">' +
                '<i class="fa-solid fa-chevron-right">' +
                '</i></button>';
            html += '</div>';
            html += '</div>';
            html += '<div class="at-section-card__body' +
                ' og-group-body"' +
                ' data-group="' + esc(g.name) + '"' +
                ' style="display:none;">';
            html += '<div class="og-group-objects-loading' +
                ' at-muted-hint">' +
                '<i class="fa-solid fa-spinner fa-spin">' +
                '</i> Loading objects&hellip;</div>';
            html += '<div class="og-group-objects"' +
                ' style="display:none;"></div>';
            html += '</div>';
            html += '</div>';
        });
        container.innerHTML = html;
        wireGroupButtons();
        applyFilter();
    }

    /* ================================================================
       Wire button handlers
       ================================================================ */
    function wireGroupButtons() {
        /* Helper: toggle collapse for a group section */
        function toggleGroup(grp) {
            var btn = container.querySelector(
                '.og-toggle-btn[data-group="' +
                grp + '"]'
            );
            var body = container.querySelector(
                '.og-group-body[data-group="' +
                grp + '"]'
            );
            if (!btn || !body) return;
            var expanded = btn.getAttribute(
                'aria-expanded'
            ) === 'true';
            if (expanded) {
                hide(body);
                btn.setAttribute(
                    'aria-expanded', 'false'
                );
                btn.querySelector('i').className =
                    'fa-solid fa-chevron-right';
            } else {
                show(body);
                btn.setAttribute(
                    'aria-expanded', 'true'
                );
                btn.querySelector('i').className =
                    'fa-solid fa-chevron-down';
                var objHost = body.querySelector(
                    '.og-group-objects'
                );
                if (!objHost.dataset.loaded) {
                    loadGroupObjects(grp, body);
                }
            }
        }

        /* Collapse / expand via chevron button */
        container.querySelectorAll(
            '.og-toggle-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                toggleGroup(btn.dataset.group);
            });
        });

        /* Collapse / expand via header bar click */
        container.querySelectorAll(
            '.at-section-card__header'
        ).forEach(function (header) {
            header.addEventListener('click', function (ev) {
                var target = ev.target;
                if (!target) return;
                /* Ignore clicks on buttons/controls */
                if (target.closest(
                    '.op-section-controls,' +
                    'button,a,input,select,textarea'
                )) return;
                var card = header.closest(
                    '.og-group-section'
                );
                if (card) {
                    toggleGroup(card.dataset.group);
                }
            });
        });

        /* Add objects */
        container.querySelectorAll(
            '.og-add-objects-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                addGroupInput.value = btn.dataset.group;
                addQuery.value = '';
                if (addBulkText) addBulkText.value = '';
                hide(addBulkResult);
                hide(addTextResult);
                show(addModal);
                addQuery.focus();
            });
        });

        container.querySelectorAll(
            '.og-summary-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                openSummaryOverlay(btn.dataset.group || '');
            });
        });

        /* Rename */
        container.querySelectorAll(
            '.og-rename-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                renameOld.value = btn.dataset.group;
                renameInput.value = btn.dataset.group;
                show(renameModal);
                renameInput.focus();
            });
        });

        /* Delete */
        container.querySelectorAll(
            '.og-delete-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                var grp = btn.dataset.group;
                if (!confirm(
                    'Delete group "' + grp + '"' +
                    ' and all its objects?'
                )) return;
                btn.disabled = true;
                postJson(cfg.deleteApiUrl, {
                    profile_id: cfg.profileId,
                    name: grp,
                }).then(function (data) {
                    btn.disabled = false;
                    if (data.success) {
                        loadGroups();
                    } else {
                        alert(data.error ||
                            'Failed to delete group.');
                    }
                }).catch(function () {
                    btn.disabled = false;
                    alert('Network error.');
                });
            });
        });
    }

    /* ================================================================
       Load objects for a single group
       ================================================================ */
    function loadGroupObjects(groupName, bodyEl) {
        var loadingEl2 = bodyEl.querySelector(
            '.og-group-objects-loading'
        );
        var objHost = bodyEl.querySelector(
            '.og-group-objects'
        );
        show(loadingEl2);
        hide(objHost);

        var url = cfg.objectsApiUrl +
            '?profile_id=' +
            encodeURIComponent(cfg.profileId) +
            '&group=' +
            encodeURIComponent(groupName);

        getJson(url).then(function (data) {
            hide(loadingEl2);
            objHost.dataset.loaded = '1';
            if (!data.success) {
                objHost.innerHTML =
                    '<span class="at-muted-hint">' +
                    esc(data.error || 'Error') + '</span>';
                show(objHost);
                return;
            }
            renderGroupObjects(
                groupName, objHost,
                data.objects || [],
                data.can_moderate || false
            );
        }).catch(function () {
            hide(loadingEl2);
            objHost.innerHTML =
                '<span class="at-muted-hint">' +
                'Network error.</span>';
            show(objHost);
        });
    }

    function renderGroupObjects(
        groupName, host, objects, canMod
    ) {
        if (!objects.length) {
            host.innerHTML =
                '<span class="at-muted-hint">' +
                'No visible objects in this group.</span>';
            show(host);
            return;
        }
        var html = '';
        objects.forEach(function (obj) {
            var pageUrl = cfg.objectPageBaseUrl +
                encodeURIComponent(obj.objname);
            html += '<article class="ari-rp-section-card' +
                ' ari-fav-card og-object-card">';
            html += '<div class="ari-rp-section-card__icon">';
            html += '<i class="fa-solid fa-atom"></i>';
            html += '</div>';
            html += '<a href="' + esc(pageUrl) + '"' +
                ' class="ari-rp-section-card__body og-object-card__body">';
            html += '<span class="og-object-card__name">'
                + esc(obj.objname) + '</span>';
            html += '<span class="og-object-card__meta">' +
                'added by ' + esc(obj.added_by || '?') +
                '</span>';
            html += '</a>';
            if (canMod) {
                html += '<div class="ari-fav-card__actions">';
                html += '<button type="button"' +
                    ' class="ari-btn ari-btn--sm' +
                    ' ari-btn--danger og-remove-obj-btn"' +
                    ' data-group="' + esc(groupName) + '"' +
                    ' data-objname="' +
                    esc(obj.objname) + '"' +
                    ' title="Remove from group">' +
                    '<i class="fa-solid fa-trash"></i> Delete' +
                    '</button>';
                html += '</div>';
            }
            html += '</article>';
        });
        host.innerHTML = html;
        show(host);

        /* Wire remove buttons */
        host.querySelectorAll(
            '.og-remove-obj-btn'
        ).forEach(function (btn) {
            btn.addEventListener('click', function () {
                btn.disabled = true;
                postJson(cfg.removeObjectApiUrl, {
                    profile_id: cfg.profileId,
                    group: btn.dataset.group,
                    objname: btn.dataset.objname,
                }).then(function (data) {
                    btn.disabled = false;
                    if (data.success) {
                        loadGroups();
                    } else {
                        alert(data.error ||
                            'Failed to remove object.');
                    }
                }).catch(function () {
                    btn.disabled = false;
                    alert('Network error.');
                });
            });
        });
    }

    /* ================================================================
       Create group
       ================================================================ */
    if (createBtn) {
        createBtn.addEventListener('click', function () {
            var name = prompt('Enter new group name:');
            if (!name || !name.trim()) return;
            createBtn.disabled = true;
            postJson(cfg.createApiUrl, {
                profile_id: cfg.profileId,
                name: name.trim(),
            }).then(function (data) {
                createBtn.disabled = false;
                if (data.success) {
                    loadGroups();
                } else {
                    alert(data.error ||
                        'Failed to create group.');
                }
            }).catch(function () {
                createBtn.disabled = false;
                alert('Network error.');
            });
        });
    }

    /* ================================================================
       Add objects modal
       ================================================================ */
    function closeAddModal() {
        hide(addModal);
        if (addBulkText) addBulkText.value = '';
    }
    if (addModalClose) {
        addModalClose.addEventListener('click', closeAddModal);
    }
    if (addModal) {
        addModal.addEventListener('click', function (e) {
            if (e.target === addModal) closeAddModal();
        });
    }

    /* Single add */
    function showSingleResult(html, isError) {
        if (!addSingleResult) return;
        addSingleResult.innerHTML = html;
        addSingleResult.style.color = isError
            ? '#c33' : '#2a7';
        show(addSingleResult);
    }

    if (addSingleBtn) {
        addSingleBtn.addEventListener('click', function () {
            var name = addQuery.value.trim();
            var grp = addGroupInput.value;
            if (!name || !grp) return;
            addSingleBtn.disabled = true;
            if (addSingleResult) hide(addSingleResult);
            postJson(cfg.addObjectApiUrl, {
                profile_id: cfg.profileId,
                group: grp,
                objname: name,
            }).then(function (data) {
                addSingleBtn.disabled = false;
                if (data.success) {
                    var msg = 'Added <b>' +
                        esc(data.resolved_objname) +
                        '</b>';
                    if (data.nickname) {
                        msg += ' (alias for <i>' +
                            esc(data.nickname) +
                            '</i>)';
                    }
                    showSingleResult(msg, false);
                    addQuery.value = '';
                    loadGroups();
                } else if (
                    data.candidates &&
                    data.candidates.length
                ) {
                    var parts = [
                        esc(data.error || 'Ambiguous'),
                        ': ',
                    ];
                    data.candidates.forEach(
                        function (c, i) {
                            if (i) parts.push(', ');
                            parts.push(
                                '<a href="#" ' +
                                'class="og-cand" ' +
                                'data-name="' +
                                esc(c) + '">' +
                                esc(c) + '</a>'
                            );
                        }
                    );
                    showSingleResult(
                        parts.join(''), true
                    );
                } else {
                    showSingleResult(
                        esc(
                            data.error ||
                            'Failed to add object.'
                        ),
                        true
                    );
                }
            }).catch(function () {
                addSingleBtn.disabled = false;
                showSingleResult(
                    'Network error.', true
                );
            });
        });
    }

    /* Click on a candidate link fills the input */
    if (addSingleResult) {
        addSingleResult.addEventListener(
            'click', function (e) {
                var el = e.target.closest('.og-cand');
                if (!el) return;
                e.preventDefault();
                addQuery.value = el.dataset.name || '';
                hide(addSingleResult);
            }
        );
    }

    /* Bulk upload */
    if (addBulkBtn) {
        addBulkBtn.addEventListener('click', function () {
            var grp = addGroupInput.value;
            var file = addBulkFile.files[0];
            if (!grp || !file) {
                alert('Select a file first.');
                return;
            }
            addBulkBtn.disabled = true;
            hide(addBulkResult);

            var fd = new FormData();
            fd.append('profile_id', cfg.profileId);
            fd.append('group', grp);
            fd.append('file', file);

            fetch(cfg.addBulkApiUrl, {
                method: 'POST',
                body: fd,
            }).then(function (r) {
                return r.json();
            }).then(function (data) {
                addBulkBtn.disabled = false;
                renderBulkAddResult(addBulkResult, data);
                if (data.success) {
                    loadGroups();
                }
            }).catch(function () {
                addBulkBtn.disabled = false;
                addBulkResult.textContent =
                    'Network error.';
                show(addBulkResult);
            });
        });
    }

    if (addTextBtn) {
        addTextBtn.addEventListener('click', function () {
            var grp = addGroupInput.value;
            var text = String(
                addBulkText ? addBulkText.value : ''
            );
            var objnames = text.split(/\r?\n/)
                .map(function (line) {
                    return String(line || '').trim();
                })
                .filter(function (line) { return !!line; });
            if (!grp || !objnames.length) {
                alert('Paste at least one object name first.');
                return;
            }
            addTextBtn.disabled = true;
            hide(addTextResult);
            postJson(cfg.addJsonApiUrl, {
                profile_id: cfg.profileId,
                group: grp,
                objnames: objnames,
            }).then(function (data) {
                addTextBtn.disabled = false;
                renderBulkAddResult(addTextResult, data);
                if (data.success) {
                    if (addBulkText) addBulkText.value = '';
                    loadGroups();
                }
            }).catch(function () {
                addTextBtn.disabled = false;
                addTextResult.textContent = 'Network error.';
                show(addTextResult);
            });
        });
    }

    function moveSummarySelectedColumn(fromIndex, toIndex) {
        var cols = summaryState.selectedColumns.slice();
        if (fromIndex < 0 || toIndex < 0) return;
        if (fromIndex >= cols.length || toIndex >= cols.length) return;
        if (fromIndex === toIndex) return;
        var moved = cols.splice(fromIndex, 1)[0];
        cols.splice(toIndex, 0, moved);
        summaryState.selectedColumns = cols;
        renderSummaryPicker();
    }

    function renderSummarySelected() {
        if (!summarySelected) return;
        summarySelected.innerHTML = '';

        var fixedCard = document.createElement('span');
        fixedCard.className = 'ogs-card ogs-card--fixed';
        fixedCard.textContent = 'OBJNAME';
        summarySelected.appendChild(fixedCard);

        summaryState.selectedColumns.forEach(function (propId, index) {
            var item = summaryState.propertyCatalog.find(
                function (entry) {
                    return entry.id === propId;
                }
            );
            if (!item) return;
            var card = document.createElement('div');
            card.className = 'ogs-card';
            card.draggable = true;
            card.setAttribute('draggable', 'true');
            card.dataset.dragIndex = String(index);
            var metaText = summaryPath(item);
            var oneLine = getSummaryLabel(item);
            if (metaText) {
                oneLine += ' - ' + metaText;
            }
            card.innerHTML = '<span class="ogs-card__text">'
                + '<span class="ogs-card__title">'
                + esc(oneLine)
                + '</span>'
                + '</span>'
                + '<span class="ogs-card__actions">'
                + '<button type="button" class="ogs-card__icon" '
                + 'title="Move up">'
                + '<i class="fa-solid fa-arrow-up"></i></button>'
                + '<button type="button" class="ogs-card__icon" '
                + 'title="Move down">'
                + '<i class="fa-solid fa-arrow-down"></i></button>'
                + (String(propId).indexOf('admin_custom::') === 0
                    ? ('<button type="button" class="ogs-card__icon" '
                        + 'title="Edit as user custom column">'
                        + '<i class="fa-solid fa-pen-to-square"></i>'
                        + '</button>')
                    : '')
                + '<span class="ogs-card__drag" '
                + 'title="Drag to reorder">'
                + '<i class="fa-solid fa-grip-vertical"></i></span>'
                + '<button type="button" class="ogs-card__icon" '
                + 'title="Remove column">'
                + '<i class="fa-solid fa-xmark"></i></button>'
                + '</span>';
            var dragHandle = card.querySelector('.ogs-card__drag');
            if (dragHandle) {
                dragHandle.draggable = true;
                dragHandle.setAttribute('draggable', 'true');
            }
            card.addEventListener('dragstart', function (event) {
                var fromIndex = parseInt(
                    card.dataset.dragIndex || '-1',
                    10
                );
                if (isNaN(fromIndex) || fromIndex < 0) {
                    event.preventDefault();
                    return;
                }
                card.classList.add('ogs-card--dragging');
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', String(fromIndex));
            });
            if (dragHandle) {
                dragHandle.addEventListener('dragstart', function (event) {
                    var fromIndex = parseInt(
                        card.dataset.dragIndex || '-1',
                        10
                    );
                    if (isNaN(fromIndex) || fromIndex < 0) {
                        event.preventDefault();
                        return;
                    }
                    card.classList.add('ogs-card--dragging');
                    event.dataTransfer.effectAllowed = 'move';
                    event.dataTransfer.setData(
                        'text/plain',
                        String(fromIndex)
                    );
                });
            }
            card.addEventListener('dragend', function () {
                card.classList.remove('ogs-card--dragging');
                summarySelected.querySelectorAll('.ogs-card')
                    .forEach(function (el) {
                        el.classList.remove('ogs-card--drop-target');
                    });
            });
            card.addEventListener('dragover', function (event) {
                event.preventDefault();
                card.classList.add('ogs-card--drop-target');
            });
            card.addEventListener('dragleave', function () {
                card.classList.remove('ogs-card--drop-target');
            });
            card.addEventListener('drop', function (event) {
                event.preventDefault();
                card.classList.remove('ogs-card--drop-target');
                var fromIndex = parseInt(
                    event.dataTransfer.getData('text/plain'),
                    10
                );
                var toIndex = parseInt(
                    card.dataset.dragIndex || '-1',
                    10
                );
                if (isNaN(fromIndex)) return;
                if (isNaN(toIndex)) return;
                moveSummarySelectedColumn(fromIndex, toIndex);
            });
            var actionBtns = card.querySelectorAll('.ogs-card__icon');
            var upBtn = actionBtns[0];
            var downBtn = actionBtns[1];
            var editCustomBtn = null;
            var removeBtn = null;
            if (String(propId).indexOf('admin_custom::') === 0) {
                editCustomBtn = actionBtns[2] || null;
                removeBtn = actionBtns[3] || null;
            } else {
                removeBtn = actionBtns[2] || null;
            }
            if (upBtn) {
                upBtn.disabled = index === 0;
                upBtn.addEventListener('click', function () {
                    moveSummarySelectedColumn(index, index - 1);
                });
            }
            if (downBtn) {
                downBtn.disabled = index === summaryState.selectedColumns.length - 1;
                downBtn.addEventListener('click', function () {
                    moveSummarySelectedColumn(index, index + 1);
                });
            }
            if (editCustomBtn) {
                editCustomBtn.addEventListener('click', function () {
                    cloneAdminCustomToUser(propId);
                });
            }
            if (!removeBtn) {
                summarySelected.appendChild(card);
                return;
            }
            removeBtn.addEventListener('click', function () {
                summaryState.selectedColumns =
                    summaryState.selectedColumns.filter(
                        function (value) {
                            return value !== propId;
                        }
                    );
                delete summaryState.selectedAliases[propId];
                renderSummaryPicker();
            });
            summarySelected.appendChild(card);
        });

        summaryState.customColumns.forEach(function (row, cIndex) {
            var card = document.createElement('div');
            card.className = 'ogs-card';
            var varsText = Object.keys(row.variables || {})
                .sort()
                .map(function (key) {
                    return key + '→' + propertyOptionHtml(row.variables[key]);
                })
                .join(', ');
            var customLine = String(row.name || 'Custom')
                + ' - '
                + String(row.expression || '')
                + ' ('
                + varsText
                + ')';
            card.innerHTML = '<span class="ogs-card__text">'
                + '<span class="ogs-card__title">'
                + esc(customLine)
                + '</span>'
                + '</span>'
                + '<span class="ogs-card__actions">'
                + '<button type="button" class="ogs-card__icon" '
                + 'title="Move up">'
                + '<i class="fa-solid fa-arrow-up"></i></button>'
                + '<button type="button" class="ogs-card__icon" '
                + 'title="Move down">'
                + '<i class="fa-solid fa-arrow-down"></i></button>'
                + '<button type="button" class="ogs-card__icon" '
                + 'title="Edit custom column">'
                + '<i class="fa-solid fa-pen"></i></button>'
                + '<button type="button" class="ogs-card__icon" '
                + 'title="Remove custom column">'
                + '<i class="fa-solid fa-xmark"></i></button>'
                + '</span>';
            var actionBtns = card.querySelectorAll('.ogs-card__icon');
            var upBtn = actionBtns[0];
            var downBtn = actionBtns[1];
            var editBtn = actionBtns[2];
            var removeBtn = actionBtns[3];
            if (upBtn) {
                upBtn.disabled = cIndex === 0;
                upBtn.addEventListener('click', function () {
                    moveSummaryCustomColumn(cIndex, cIndex - 1);
                });
            }
            if (downBtn) {
                downBtn.disabled = cIndex === summaryState.customColumns.length - 1;
                downBtn.addEventListener('click', function () {
                    moveSummaryCustomColumn(cIndex, cIndex + 1);
                });
            }
            if (editBtn) {
                editBtn.addEventListener('click', function () {
                    openSummaryCustomOverlay(cIndex);
                });
            }
            removeBtn.addEventListener('click', function () {
                var key = String(row.name || '').toLowerCase();
                summaryState.customColumns = summaryState.customColumns
                    .filter(function (entry) {
                        return String(entry.name || '').toLowerCase() !== key;
                    });
                renderSummaryPicker();
            });
            summarySelected.appendChild(card);
        });
    }

    function renderSummaryList() {
        if (!summaryList) return;
        var rawQuery = String(
            summarySearch ? summarySearch.value : ''
        ).trim().toLowerCase();
        var query = rawQuery.length >= 3 ? rawQuery : '';
        var selectedCategory = String(
            summaryCategory ? summaryCategory.value : ''
        );
        var selectedSub = String(
            summarySubcategory ? summarySubcategory.value : ''
        );
        var shown = 0;
        var groupKey = '';
        summaryList.innerHTML = '';

        var items = summaryState.propertyCatalog.slice();
        items.sort(function (a, b) {
            var ka = [
                summaryCategoryValue(a),
                summarySubcategoryValue(a),
                summaryPropertyName(a),
            ].join('||').toLowerCase();
            var kb = [
                summaryCategoryValue(b),
                summarySubcategoryValue(b),
                summaryPropertyName(b),
            ].join('||').toLowerCase();
            if (ka < kb) return -1;
            if (ka > kb) return 1;
            return 0;
        });

        items.forEach(function (item) {
            var categoryText = summaryCategoryValue(item);
            var subText = summarySubcategoryValue(item);
            if (selectedCategory && categoryText !== selectedCategory) {
                return;
            }
            if (selectedSub && subText !== selectedSub) {
                return;
            }
            var haystack = (
                summaryPropertyName(item)
                + ' ' + categoryText
                + ' ' + subText
            ).toLowerCase();
            if (query && haystack.indexOf(query) === -1) {
                return;
            }
            var thisGroup = categoryText + ' / ' + subText;
            if (thisGroup !== groupKey) {
                groupKey = thisGroup;
                var group = document.createElement('div');
                group.className = 'ogs-list__group';
                group.textContent = thisGroup;
                summaryList.appendChild(group);
            }
            shown += 1;
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ogs-list__item';
            btn.disabled = hasSummaryColumn(item.id);
            var itemLabel = hasSummaryColumn(item.id)
                ? getSummaryLabel(item)
                : summaryPropertyName(item);
            var metaText = summaryPath(item);
            btn.innerHTML = '<span class="ogs-list__label">'
                + esc(itemLabel) + '</span>'
                + (metaText
                    ? ('<span class="ogs-list__meta">'
                        + esc(metaText)
                        + '</span>')
                    : '');
            btn.addEventListener('click', function () {
                if (hasSummaryColumn(item.id)) return;
                summaryState.selectedColumns.push(item.id);
                renderSummaryPicker();
            });
            summaryList.appendChild(btn);
        });

        if (!shown) {
            summaryList.innerHTML = '<div class="ogs-list__empty">'
                + 'No properties match this search.'
                + '</div>';
        }
    }

    function renderSummaryPicker() {
        renderSummaryFilters();
        renderSummaryList();
        renderSummarySelected();
    }

    function closeSummaryOverlay() {
        hide(summaryOverlay);
        closeSummaryCustomOverlay();
        setSummaryStatus('', false);
    }

    function openSummaryOverlay(groupName) {
        if (!groupName || !summaryOverlay) return;
        summaryState.groupName = groupName;
        setSummaryStatus('Loading summary properties...', false);
        summaryList.innerHTML = '<div class="ogs-list__empty">'
            + 'Loading properties...'
            + '</div>';
        show(summaryOverlay);
        closeSummaryRenameOverlay();
        getJson(
            cfg.summaryConfigApiUrl
            + '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&group=' + encodeURIComponent(groupName)
        ).then(function (data) {
            if (!data.success) {
                setSummaryStatus(
                    data.error || 'Failed to load summary config.',
                    true
                );
                return;
            }
            summaryState.propertyCatalog = data.property_catalog || [];
            summaryState.selectedColumns = data.selected_columns || [];
            summaryState.selectedAliases = data.selected_aliases || {};
            summaryState.customColumns = data.custom_columns || [];
            summaryState.adminCustomColumns =
                data.admin_custom_columns || [];
            summaryState.allowedExpressionRows =
                data.allowed_expression_rows || [];
            summaryState.pageUrl = data.summary_page_url || '';
            if (summaryCategory) summaryCategory.value = '';
            if (summarySubcategory) summarySubcategory.value = '';
            if (summarySearch) summarySearch.value = '';
            renderSummaryPicker();
            setSummaryStatus('', false);
            if (summarySearch) summarySearch.focus();
        }).catch(function () {
            setSummaryStatus('Network error loading properties.', true);
        });
    }

    if (summarySearch) {
        summarySearch.addEventListener('input', renderSummaryList);
    }
    if (summaryRenameOpen) {
        summaryRenameOpen.addEventListener('click', function () {
            openSummaryRenameOverlay('');
        });
    }
    if (summaryRenameApply) {
        summaryRenameApply.addEventListener(
            'click', applySummaryRenameOverlay
        );
    }
    if (summaryRenameClose) {
        summaryRenameClose.addEventListener(
            'click', closeSummaryRenameOverlay
        );
    }
    if (summaryRenameCancel) {
        summaryRenameCancel.addEventListener(
            'click', closeSummaryRenameOverlay
        );
    }
    if (summaryRenameBackdrop) {
        summaryRenameBackdrop.addEventListener(
            'click', closeSummaryRenameOverlay
        );
    }
    if (summaryCustomOpen) {
        summaryCustomOpen.addEventListener(
            'click', function () {
                openSummaryCustomOverlay(-1);
            }
        );
    }
    if (summaryCustomClose) {
        summaryCustomClose.addEventListener(
            'click', closeSummaryCustomOverlay
        );
    }
    if (summaryCustomCancel) {
        summaryCustomCancel.addEventListener(
            'click', closeSummaryCustomOverlay
        );
    }
    if (summaryCustomBackdrop) {
        summaryCustomBackdrop.addEventListener(
            'click', closeSummaryCustomOverlay
        );
    }
    if (summaryCustomAddVar) {
        summaryCustomAddVar.addEventListener('click', function () {
            summaryState.customDraftVars.push({letter: 'x', propId: ''});
            invalidateSummaryCustomTest();
            renderSummaryCustomVars();
        });
    }
    if (summaryCustomName) {
        summaryCustomName.addEventListener('input', function () {
            invalidateSummaryCustomTest();
        });
    }
    if (summaryCustomExpr) {
        summaryCustomExpr.addEventListener('input', function () {
            invalidateSummaryCustomTest();
        });
    }
    if (summaryCustomExprHelpToggle) {
        summaryCustomExprHelpToggle.addEventListener(
            'click', toggleSummaryExprHelp
        );
    }
    if (summaryCustomCategory) {
        summaryCustomCategory.addEventListener('change', function () {
            if (summaryCustomSubcategory) {
                summaryCustomSubcategory.value = '';
            }
            invalidateSummaryCustomTest();
            renderSummaryCustomFilters();
            renderSummaryCustomVars();
        });
    }
    if (summaryCustomSubcategory) {
        summaryCustomSubcategory.addEventListener('change', function () {
            invalidateSummaryCustomTest();
            renderSummaryCustomVars();
        });
    }
    if (summaryCustomSearch) {
        summaryCustomSearch.addEventListener('input', function () {
            renderSummaryCustomVars();
        });
    }
    if (summaryCustomTest) {
        summaryCustomTest.addEventListener(
            'click', testSummaryCustomColumn
        );
    }
    if (summaryCustomSave) {
        summaryCustomSave.addEventListener(
            'click', saveSummaryCustomColumn
        );
    }
    if (summaryCategory) {
        summaryCategory.addEventListener('change', function () {
            if (summarySubcategory) summarySubcategory.value = '';
            renderSummaryPicker();
        });
    }
    if (summarySubcategory) {
        summarySubcategory.addEventListener('change', renderSummaryPicker);
    }
    if (summaryClose) {
        summaryClose.addEventListener('click', closeSummaryOverlay);
    }
    if (summaryCloseBtn) {
        summaryCloseBtn.addEventListener(
            'click', closeSummaryOverlay
        );
    }
    if (summaryBackdrop) {
        summaryBackdrop.addEventListener(
            'click', closeSummaryOverlay
        );
    }
    if (summaryGenerateBtn) {
        summaryGenerateBtn.addEventListener('click', function () {
            if (!summaryState.groupName) return;
            summaryGenerateBtn.disabled = true;
            setSummaryStatus('Saving summary columns...', false);
            postJson(cfg.summaryConfigApiUrl, {
                profile_id: cfg.profileId,
                group: summaryState.groupName,
                columns: summaryState.selectedColumns,
                aliases: summaryState.selectedColumns.reduce(
                    function (acc, propId) {
                        var val = String(
                            summaryState.selectedAliases[propId] || ''
                        ).trim();
                        if (val) {
                            acc[propId] = val;
                        }
                        return acc;
                    },
                    {}
                ),
                custom_columns: summaryState.customColumns,
            }).then(function (data) {
                summaryGenerateBtn.disabled = false;
                if (!data.success) {
                    setSummaryStatus(
                        data.error || 'Failed to save summary columns.',
                        true
                    );
                    return;
                }
                window.location = data.summary_page_url;
            }).catch(function () {
                summaryGenerateBtn.disabled = false;
                setSummaryStatus('Network error.', true);
            });
        });
    }

    /* ================================================================
       Rename modal
       ================================================================ */
    function closeRenameModal() { hide(renameModal); }
    if (renameClose) {
        renameClose.addEventListener(
            'click', closeRenameModal
        );
    }
    if (renameModal) {
        renameModal.addEventListener('click', function (e) {
            if (e.target === renameModal) closeRenameModal();
        });
    }
    if (renameSubmit) {
        renameSubmit.addEventListener('click', function () {
            var oldName = renameOld.value;
            var newName = renameInput.value.trim();
            if (!oldName || !newName) return;
            renameSubmit.disabled = true;
            postJson(cfg.renameApiUrl, {
                profile_id: cfg.profileId,
                old_name: oldName,
                new_name: newName,
            }).then(function (data) {
                renameSubmit.disabled = false;
                if (data.success) {
                    closeRenameModal();
                    loadGroups();
                } else {
                    alert(data.error ||
                        'Failed to rename.');
                }
            }).catch(function () {
                renameSubmit.disabled = false;
                alert('Network error.');
            });
        });
    }

    /* Escape key closes modals */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeAddModal();
            closeRenameModal();
            closeSummaryOverlay();
        }
    });

    /* ================================================================
       Filter groups by name
       ================================================================ */
    function applyFilter() {
        if (!container) return;
        var query = (filterInput ? filterInput.value : '')
            .trim().toLowerCase();
        var sections = container.querySelectorAll(
            '.og-group-section'
        );
        var visible = 0;
        sections.forEach(function (sec) {
            var name = (sec.dataset.group || '').toLowerCase();
            if (!query || name.indexOf(query) !== -1) {
                sec.style.display = '';
                visible++;
            } else {
                sec.style.display = 'none';
            }
        });
        if (emptyEl) {
            if (visible === 0 && groupsData.length > 0) {
                emptyEl.textContent =
                    'No groups matching filter.';
                show(emptyEl);
            } else if (groupsData.length === 0) {
                show(emptyEl);
            } else {
                hide(emptyEl);
            }
        }
    }

    if (filterInput) {
        filterInput.addEventListener('input', applyFilter);
    }

    /* ── Initial load ───────────────────────────────────────────── */
    loadGroups();
}());
