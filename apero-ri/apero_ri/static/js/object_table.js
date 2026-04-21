/* ==========================================================================
   Object Table page logic — sortable, filterable, paginated data table
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_OBJ_TABLE;
    var minNameChars = Math.max(1, Number((cfg && cfg.minNameChars) || 1));

    /* -----------------------------------------------------------------------
       State
    ----------------------------------------------------------------------- */
    var allRows      = [];       // rows returned from API (already filtered)
    var filteredRows = [];       // after column filters applied
    var columns      = [];       // ordered column list (no RUN_ID)
    var hiddenCols   = {};       // col -> true when hidden
    var sortCol      = null;     // currently sorted column (null = unsorted)
    var sortDir      = 1;        // 1 = asc, -1 = desc
    var colFilters   = {};       // col -> filter string
    var columnMeta   = {};       // col -> {sortable, filterable, removable, default, type}
    var currentPage  = 1;
    var perPage      = 50;       // 0 = show all

    /* -----------------------------------------------------------------------
       DOM refs
    ----------------------------------------------------------------------- */
    var lastUpdatedEl  = document.getElementById('ot-last-updated');
    var rowSummaryEl   = document.getElementById('ot-row-summary');

    var btnColumns     = document.getElementById('ot-btn-columns');
    var btnClearFilter = document.getElementById('ot-btn-clear-filters');
    var perpageSelect  = document.getElementById('ot-perpage');

    var colPanel       = document.getElementById('ot-col-panel');
    var colToggles     = document.getElementById('ot-col-toggles');
    var colClose       = document.getElementById('ot-col-close');
    var colAll         = document.getElementById('ot-col-all');
    var colNone        = document.getElementById('ot-col-none');

    var scrollTopEl    = document.getElementById('ot-scroll-top');
    var scrollSizer    = document.getElementById('ot-scroll-sizer');
    var tableWrap      = document.getElementById('ot-table-wrap');
    var tableEl        = document.getElementById('ot-table');
    var headerRow      = document.getElementById('ot-header-row');
    var filterRow      = document.getElementById('ot-filter-row');
    var tbody          = document.getElementById('ot-tbody');

    var pageInfo       = document.getElementById('ot-page-info');
    var pageInput      = document.getElementById('ot-page-input');
    var pageTotal      = document.getElementById('ot-page-total');
    var btnFirst       = document.getElementById('ot-btn-first');
    var btnPrev        = document.getElementById('ot-btn-prev');
    var btnNext        = document.getElementById('ot-btn-next');
    var btnLast        = document.getElementById('ot-btn-last');

    // Optional Find Object controls (present on object_table page)
    var findTabName   = document.getElementById('fo-tab-name');
    var findTabCoords = document.getElementById('fo-tab-coords');
    var findTabDate = document.getElementById('fo-tab-date');
    var findTabAdvanced = document.getElementById('fo-tab-advanced');
    var findTabGroup = document.getElementById('fo-tab-group');
    var findPanelName = document.getElementById('fo-panel-name');
    var findPanelCoords = document.getElementById('fo-panel-coords');
    var findPanelDate = document.getElementById('fo-panel-date');
    var findPanelAdvanced = document.getElementById('fo-panel-advanced');
    var findPanelGroup = document.getElementById('fo-panel-group');
    var findNameInput  = document.getElementById('fo-name-query');
    var findRaInput    = document.getElementById('fo-ra');
    var findDecInput   = document.getElementById('fo-dec');
    var findRaLabel    = document.getElementById('fo-ra-label');
    var findDecLabel   = document.getElementById('fo-dec-label');
    var findSepInput   = document.getElementById('fo-sep');
    var findCoordFormatSelect = document.getElementById('fo-coord-format');
    var findUnitSelect = document.getElementById('fo-unit');
    var findCoordsBtn  = document.getElementById('fo-find-coords');
    var findDateFirstInput = document.getElementById('fo-date-first');
    var findDateLastInput = document.getElementById('fo-date-last');
    var findDateApplyBtn = document.getElementById('fo-date-apply');
    var findAdvancedColumnSelect = document.getElementById('fo-adv-column');
    var findAdvancedInputsContainer = document.getElementById('fo-adv-inputs');
    var findAdvancedApplyBtn = document.getElementById('fo-adv-apply');
    var findGroupSelect = document.getElementById('fo-group-select');
    var findGroupApplyBtn = document.getElementById('fo-group-apply');
    var findGroupClearBtn = document.getElementById('fo-group-clear');
    var findClearBtn   = document.getElementById('fo-clear-find');
    var findStatusEl   = document.getElementById('fo-status');

    // Send-to-Group overlay refs
    var stgOverlay   = document.getElementById('stg-overlay');
    var stgBackdrop  = document.getElementById('stg-backdrop');
    var stgClose     = document.getElementById('stg-close');
    var stgCount     = document.getElementById('stg-count');
    var stgSelect    = document.getElementById('stg-group-select');
    var stgNewName   = document.getElementById('stg-new-name');
    var stgCreateBtn = document.getElementById('stg-create-btn');
    var stgSendBtn   = document.getElementById('stg-send-btn');
    var stgStatus    = document.getElementById('stg-status');
    var btnSendToGroup = document.getElementById('ot-btn-send-to-group');

    var hasFindControls = !!(
        findTabName && findTabCoords && findTabDate && findTabAdvanced
        && findTabGroup
        && findPanelName && findPanelCoords
        && findPanelDate && findPanelAdvanced
        && findPanelGroup
        && findNameInput && findRaInput && findDecInput && findSepInput
        && findRaLabel && findDecLabel
        && findCoordFormatSelect && findUnitSelect
        && findCoordsBtn
        && findDateFirstInput && findDateLastInput && findDateApplyBtn
        && findAdvancedColumnSelect && findAdvancedInputsContainer
        && findAdvancedApplyBtn && findClearBtn
    );
    var activeFindTab = 'name';
    var coordSearchRequested = false;
    // Active group filter: list of objnames in selected group
    var groupFilterNames = null;
    var dateFilterApplied = {
        first: '',
        last: '',
    };
    var advancedFilterApplied = {
        column: '',
        colType: '',
        contains: '',
        from: '',
        to: '',
    };
    var lastRequestId  = 0;

    /* -----------------------------------------------------------------------
       Helpers
    ----------------------------------------------------------------------- */
    function escHtml(str) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(str)));
        return d.innerHTML;
    }

    function formatDate(iso) {
        if (!iso) return '—';
        try {
            return new Date(iso).toLocaleString();
        } catch (e) {
            return iso;
        }
    }

    function normalizeColumnMeta(rawMeta) {
        var out = {};
        if (!rawMeta || typeof rawMeta !== 'object') {
            return out;
        }
        Object.keys(rawMeta).forEach(function (key) {
            var meta = rawMeta[key] || {};
            out[key] = {
                sortable: meta.sortable !== false,
                filterable: meta.filterable !== false,
                removable: meta.removable !== false,
                default: meta.default !== false,
                hidden: meta.hidden === true,
                type: meta.type ? String(meta.type).toLowerCase()
                    : meta.coltype ? String(meta.coltype).toLowerCase()
                    : 'string',
                advanced_search: meta.advanced_search === true,
            };
        });
        return out;
    }

    function setFindStatus(text, isError) {
        if (!hasFindControls || !findStatusEl) return;
        findStatusEl.textContent = text;
        findStatusEl.classList.toggle('ot-find-status--error', !!isError);
    }

    function setFindTab(tab) {
        if (!hasFindControls) return;
        activeFindTab = tab;

        var _tabs = [
            ['name', findTabName, findPanelName],
            ['coords', findTabCoords, findPanelCoords],
            ['date', findTabDate, findPanelDate],
            ['advanced', findTabAdvanced, findPanelAdvanced],
            ['group', findTabGroup, findPanelGroup],
        ];
        _tabs.forEach(function (item) {
            var key = item[0];
            var tabBtn = item[1];
            var panel = item[2];
            var active = key === activeFindTab;
            tabBtn.classList.toggle('ot-find-tab--active', active);
            tabBtn.setAttribute('aria-selected', active ? 'true' : 'false');
            panel.classList.toggle('ot-find-tab-panel--active', active);
            panel.hidden = !active;
        });

        coordSearchRequested = false;
        if (activeFindTab === 'name') {
            if (String(findNameInput.value || '').trim().length >= minNameChars) {
                setFindStatus('Searching by name...', false);
            } else {
                setFindStatus('Type object name to search aliases.', false);
            }
        } else if (activeFindTab === 'coords') {
            setFindStatus('Enter RA, Dec, and separation, then click Find.', false);
        } else if (activeFindTab === 'date') {
            setFindStatus('Set first/last observed dates and click Apply.', false);
        } else if (activeFindTab === 'group') {
            setFindStatus('Choose a group and click Apply.', false);
        } else {
            setFindStatus('Choose a property, enter text, and click Apply.', false);
        }
    }

    function populateAdvancedColumns() {
        if (!hasFindControls) return;
        var current = String(findAdvancedColumnSelect.value || '');
        var opts = columns.filter(function (col) {
            return (columnMeta[col] || {}).advanced_search === true;
        });
        findAdvancedColumnSelect.innerHTML = '';

        var placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = 'Select a property';
        findAdvancedColumnSelect.appendChild(placeholder);

        opts.forEach(function (col) {
            var opt = document.createElement('option');
            opt.value = col;
            opt.textContent = col;
            findAdvancedColumnSelect.appendChild(opt);
        });

        if (current && opts.indexOf(current) !== -1) {
            findAdvancedColumnSelect.value = current;
            advancedBindInputs();
        } else {
            findAdvancedInputsContainer.innerHTML = '';
        }
    }

    function advancedBindInputs() {
        if (!hasFindControls) return;
        findAdvancedInputsContainer.innerHTML = '';
        var col = String(findAdvancedColumnSelect.value || '').trim();
        if (!col) return;
        var meta = columnMeta[col] || {};
        var type = String(meta.type || 'string');

        function makeField(labelText, inputId, inputType, placeholder, step) {
            var lbl = document.createElement('label');
            lbl.className = 'ot-find-field';
            var span = document.createElement('span');
            span.className = 'ot-find-field__label';
            span.textContent = labelText;
            var inp = document.createElement('input');
            inp.id = inputId;
            inp.className = 'ot-find-input';
            inp.type = inputType;
            if (placeholder) inp.placeholder = placeholder;
            if (step) inp.step = step;
            lbl.appendChild(span);
            lbl.appendChild(inp);
            return lbl;
        }

        if (type === 'number' || type === 'int' || type === 'float') {
            findAdvancedInputsContainer.appendChild(
                makeField('From', 'fo-adv-from', 'number', '', 'any'));
            findAdvancedInputsContainer.appendChild(
                makeField('To', 'fo-adv-to', 'number', '', 'any'));
        } else if (type === 'date' || type === 'datetime' || type === 'night') {
            findAdvancedInputsContainer.appendChild(
                makeField('From', 'fo-adv-from', 'date', '', ''));
            findAdvancedInputsContainer.appendChild(
                makeField('To', 'fo-adv-to', 'date', '', ''));
        } else {
            findAdvancedInputsContainer.appendChild(
                makeField('Contains', 'fo-adv-contains', 'text',
                          'Type value to match', ''));
        }
    }

    function getAdvancedFilterState() {
        var col = String(findAdvancedColumnSelect.value || '').trim();
        if (!col) {
            return { column: '', colType: '', contains: '', from: '', to: '' };
        }
        var meta = columnMeta[col] || {};
        var type = String(meta.type || 'string');

        if (type === 'number' || type === 'int' || type === 'float'
                || type === 'date' || type === 'datetime' || type === 'night') {
            var fromEl = document.getElementById('fo-adv-from');
            var toEl   = document.getElementById('fo-adv-to');
            return {
                column: col,
                colType: type,
                contains: '',
                from: fromEl ? String(fromEl.value || '').trim() : '',
                to:   toEl   ? String(toEl.value   || '').trim() : '',
            };
        }
        var containsEl = document.getElementById('fo-adv-contains');
        return {
            column: col,
            colType: type,
            contains: containsEl ? String(containsEl.value || '').trim() : '',
            from: '',
            to: '',
        };
    }

    function clearFindInputs() {
        if (!hasFindControls) return;
        findNameInput.value = '';
        findRaInput.value = '';
        findDecInput.value = '';
        findSepInput.value = '';
        findCoordFormatSelect.value = 'deg';
        findUnitSelect.value = 'arcsec';
        findDateFirstInput.value = '';
        findDateLastInput.value = '';
        findAdvancedColumnSelect.value = '';
        if (findAdvancedInputsContainer) findAdvancedInputsContainer.innerHTML = '';
        if (findGroupSelect) findGroupSelect.value = '';
        dateFilterApplied = { first: '', last: '' };
        advancedFilterApplied = { column: '', colType: '', contains: '', from: '', to: '' };
        groupFilterNames = null;
        coordSearchRequested = false;
        syncCoordInputFormatUi();
    }

    function parseNumberInput(el) {
        if (!el) return null;
        var raw = String(el.value || '').trim();
        if (!raw) return null;
        var v = Number(raw);
        return isNaN(v) ? null : v;
    }

    function parseSexagesimal(raw, allowSign) {
        var txt = String(raw || '').trim();
        if (!txt) return null;
        txt = txt
            .replace(/[hHdD]/g, ':')
            .replace(/[mM]/g, ':')
            .replace(/[sS]/g, '')
            .replace(/\s+/g, ':')
            .replace(/:+/g, ':');

        var sign = 1;
        if (txt.charAt(0) === '+') {
            txt = txt.slice(1);
        } else if (txt.charAt(0) === '-') {
            if (!allowSign) return null;
            sign = -1;
            txt = txt.slice(1);
        }

        var parts = txt.split(':').filter(function (p) {
            return p !== '';
        });
        if (parts.length < 2 || parts.length > 3) return null;

        var a = Number(parts[0]);
        var b = Number(parts[1]);
        var c = (parts.length === 3) ? Number(parts[2]) : 0;
        if ([a, b, c].some(function (v) { return isNaN(v); })) return null;
        if (b < 0 || b >= 60 || c < 0 || c >= 60) return null;

        return {
            sign: sign,
            a: Math.abs(a),
            b: b,
            c: c,
        };
    }

    function parseRaToDeg(raw, format) {
        if (format === 'deg') {
            return Number(raw);
        }
        var sx = parseSexagesimal(raw, false);
        if (!sx) return null;
        var hours = sx.a + (sx.b / 60) + (sx.c / 3600);
        if (!(hours >= 0 && hours <= 24)) return null;
        return hours * 15;
    }

    function parseDecToDeg(raw, format) {
        if (format === 'deg') {
            return Number(raw);
        }
        var sx = parseSexagesimal(raw, true);
        if (!sx) return null;
        var deg = sx.a + (sx.b / 60) + (sx.c / 3600);
        deg *= sx.sign;
        if (!(deg >= -90 && deg <= 90)) return null;
        return deg;
    }

    function syncCoordInputFormatUi() {
        if (!hasFindControls) return;
        var mode = String(findCoordFormatSelect.value || 'deg').toLowerCase();
        if (mode === 'hms') {
            findRaLabel.textContent = 'RA [HH:MM:SS]';
            findDecLabel.textContent = 'Dec [DD:MM:SS]';
            findRaInput.placeholder = 'e.g. 21:52:29.92';
            findDecInput.placeholder = 'e.g. +28:47:36.7';
        } else {
            findRaLabel.textContent = 'RA [deg]';
            findDecLabel.textContent = 'Dec [deg]';
            findRaInput.placeholder = 'e.g. 328.1243';
            findDecInput.placeholder = 'e.g. 28.7933';
        }
    }

    function buildApiQuery() {
        var params = new URLSearchParams();
        params.set('profile_id', cfg.profileId);

        if (!hasFindControls) {
            return { params: params, valid: true };
        }

        if (activeFindTab === 'name') {
            var nameQuery = String(findNameInput.value || '').trim();
            if (nameQuery.length >= minNameChars) {
                params.set('find_only', '1');
                params.set('name_query', nameQuery);
                setFindStatus('Searching by name...', false);
            } else {
                // No name criterion means show full table, not empty result.
                setFindStatus('Type object name to search aliases.', false);
            }
            return { params: params, valid: true };
        }

        if (activeFindTab === 'date'
                || activeFindTab === 'advanced'
                || activeFindTab === 'group') {
            return { params: params, valid: true };
        }

        // Coordinate tab is manual: only filter after explicit Find.
        if (!coordSearchRequested) {
            setFindStatus('Enter RA, Dec, and separation, then click Find.', false);
            return { params: params, valid: true };
        }

        var raRaw = String(findRaInput.value || '').trim();
        var decRaw = String(findDecInput.value || '').trim();
        var sepRaw = String(findSepInput.value || '').trim();
        if (!(raRaw && decRaw && sepRaw)) {
            setFindStatus('Provide RA, Dec, and separation before clicking Find.', true);
            return { params: params, valid: false };
        }

        var cfmt = String(findCoordFormatSelect.value || 'deg').toLowerCase();
        var ra = parseRaToDeg(raRaw, cfmt);
        var dec = parseDecToDeg(decRaw, cfmt);
        var sep = parseNumberInput(findSepInput);
        if (!isFinite(ra) || !isFinite(dec) || sep === null || sep < 0) {
            if (cfmt === 'hms') {
                setFindStatus('Use RA HH:MM:SS, Dec DD:MM:SS, and numeric separation.', true);
            } else {
                setFindStatus('RA, Dec, and separation must be valid numbers.', true);
            }
            return { params: params, valid: false };
        }

        params.set('find_only', '1');
        params.set('ra', String(ra));
        params.set('dec', String(dec));
        params.set('separation', String(sep));
        params.set('separation_unit', findUnitSelect.value || 'arcsec');
        setFindStatus('Searching by coordinates...', false);
        return { params: params, valid: true };
    }

    function getColumnMeta(col) {
        return columnMeta[col] || {};
    }

    function isColumnSortable(col) {
        var meta = getColumnMeta(col);
        return meta.sortable !== false;
    }

    function isColumnFilterable(col) {
        var meta = getColumnMeta(col);
        return meta.filterable !== false;
    }

    function isColumnRemovable(col) {
        // Keep the object identifier always visible.
        if (col === 'OBJNAME') return false;
        var meta = getColumnMeta(col);
        return meta.removable !== false;
    }

    function isColumnDefaultVisible(col) {
        var meta = getColumnMeta(col);
        return meta.default !== false;
    }

    function isColumnForcedHidden(col) {
        var meta = getColumnMeta(col);
        return meta.hidden === true;
    }

    function parseStrictNumber(value) {
        var raw = String(value === null || value === undefined ? '' : value).trim();
        if (!raw || !/^-?\d+(\.\d+)?$/.test(raw)) {
            return null;
        }
        var num = Number(raw);
        return isNaN(num) ? null : num;
    }

    function parseNightDate(value) {
        var raw = String(value === null || value === undefined ? '' : value).trim();
        if (!raw) return null;
        if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
            return Date.parse(raw + 'T00:00:00Z');
        }
        if (/^\d{8}$/.test(raw)) {
            var y = raw.slice(0, 4);
            var m = raw.slice(4, 6);
            var d = raw.slice(6, 8);
            return Date.parse(y + '-' + m + '-' + d + 'T00:00:00Z');
        }
        var parsed = Date.parse(raw);
        return isNaN(parsed) ? null : parsed;
    }

    function normalizeForSort(col, value) {
        var meta = getColumnMeta(col);
        var type = String(meta.type || '').toLowerCase();

        if (type === 'count') {
            // "N (M)" — sort by N (user-accessible count)
            var cm = /^\s*(\d+)/.exec(
                String(value === null || value === undefined ? '' : value)
            );
            return {
                kind: 'number',
                value: cm ? parseInt(cm[1], 10) : -1,
            };
        }

        if (type === 'date' || type === 'datetime' || type === 'night') {
            var ts = parseNightDate(value);
            if (ts !== null) {
                return { kind: 'number', value: ts };
            }
        }

        if (type === 'number' || type === 'int' || type === 'float') {
            var forcedNum = parseStrictNumber(value);
            if (forcedNum !== null) {
                return { kind: 'number', value: forcedNum };
            }
        }

        var autoNum = parseStrictNumber(value);
        if (autoNum !== null) {
            return { kind: 'number', value: autoNum };
        }

        return {
            kind: 'string',
            value: String(value === null || value === undefined ? '' : value).toLowerCase(),
        };
    }

    function shouldUseDropdownFilter(col) {
        var meta = getColumnMeta(col);
        var type = String(meta.type || '').toLowerCase();
        var cname = String(col || '').toLowerCase();

        if (type === 'number' || type === 'int' || type === 'float'
            || type === 'date' || type === 'datetime' || type === 'night') {
            return false;
        }

        if (/(date|time|timestamp|night|mjd|jd|unix|obs_time)/.test(cname)) {
            return false;
        }

        var nonBlank = allRows.map(function (r) {
            return r[col];
        }).filter(function (v) {
            return v !== null && v !== undefined && String(v).trim() !== '';
        });

        if (!nonBlank.length) {
            return true;
        }

        var allNumeric = nonBlank.every(function (v) {
            return parseStrictNumber(v) !== null;
        });
        if (allNumeric) {
            return false;
        }

        var allCountLike = nonBlank.every(function (v) {
            return /^\s*\d+\s*\(\s*\d+\s*\)\s*$/.test(String(v));
        });
        if (allCountLike) {
            return false;
        }

        var allDateLike = nonBlank.every(function (v) {
            return parseNightDate(v) !== null;
        });
        if (allDateLike) {
            return false;
        }

        return true;
    }

    /* -----------------------------------------------------------------------
       Load data from API
    ----------------------------------------------------------------------- */
    function loadData() {
        var requestId = ++lastRequestId;
        var queryBuild = buildApiQuery();
        if (!queryBuild.valid) {
            // Keep current table visible; only update finder status.
            return;
        }

        tbody.innerHTML = '<tr><td class="ot-loading" colspan="20">'
            + '<i class="fa-solid fa-spinner fa-spin"></i> Loading data&hellip;'
            + '</td></tr>';

        fetch(cfg.apiUrl + '?' + queryBuild.params.toString())
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (requestId !== lastRequestId) {
                    return;
                }
                if (!data.success) {
                    tbody.innerHTML = '<tr><td class="ot-error" colspan="20">'
                        + escHtml(data.error || 'Failed to load data') + '</td></tr>';
                    if (hasFindControls) {
                        setFindStatus(data.error || 'Search failed.', true);
                    }
                    return;
                }

                allRows  = data.rows    || [];
                columns  = data.columns || [];
                columnMeta = normalizeColumnMeta(data.column_meta || {});
                populateAdvancedColumns();

                // Enforce hard exclusion for metadata-hidden columns.
                columns = columns.filter(function (col) {
                    return !isColumnForcedHidden(col);
                });
                allRows = allRows.map(function (row) {
                    var clean = {};
                    Object.keys(row || {}).forEach(function (k) {
                        if (!isColumnForcedHidden(k)) {
                            clean[k] = row[k];
                        }
                    });
                    return clean;
                });

                // Initialize per-column visibility from metadata defaults.
                hiddenCols = {};
                columns.forEach(function (col) {
                    hiddenCols[col] = !isColumnDefaultVisible(col);
                    if (!isColumnRemovable(col)) {
                        hiddenCols[col] = false;
                    }
                });

                // Metadata
                if (data.generated_at) {
                    lastUpdatedEl.innerHTML =
                        '<i class="fa-solid fa-clock"></i> Last updated: '
                        + escHtml(formatDate(data.generated_at));
                } else {
                    lastUpdatedEl.innerHTML =
                        '<i class="fa-solid fa-circle-exclamation"></i> No data generated yet';
                }

                // Show "no data" message when the JSON exists but is empty
                if (data.message && allRows.length === 0) {
                    tbody.innerHTML = '<tr><td class="ot-empty" colspan="20">'
                        + escHtml(data.message) + '</td></tr>';
                    if (hasFindControls) {
                        setFindStatus(data.message, false);
                    }
                    updatePagination();
                    return;
                }

                if (hasFindControls) {
                    setFindStatus('Showing ' + allRows.length + ' matching objects.', false);
                }

                buildHeaders();
                applyFilterSort();
            })
            .catch(function (err) {
                if (requestId !== lastRequestId) {
                    return;
                }
                tbody.innerHTML = '<tr><td class="ot-error" colspan="20">'
                    + 'Network error: ' + escHtml(String(err)) + '</td></tr>';
                if (hasFindControls) {
                    setFindStatus('Network error while searching.', true);
                }
            });
    }

    function debounce(fn, waitMs) {
        var timer = null;
        return function () {
            if (timer) {
                window.clearTimeout(timer);
            }
            timer = window.setTimeout(function () {
                fn();
            }, waitMs);
        };
    }

    /* -----------------------------------------------------------------------
       Build header cells and column-toggle panel
    ----------------------------------------------------------------------- */
    function buildHeaders() {
        // Populate column toggle panel
        colToggles.innerHTML = '';
        columns.forEach(function (col) {
            if (!isColumnRemovable(col)) {
                hiddenCols[col] = false;
            }

            var label = document.createElement('label');
            label.className = 'ot-col-toggle';

            var cb = document.createElement('input');
            cb.type    = 'checkbox';
            cb.checked = !hiddenCols[col];
            cb.dataset.col = col;
            if (!isColumnRemovable(col)) {
                cb.disabled = true;
                hiddenCols[col] = false;
            }
            cb.addEventListener('change', function () {
                if (!isColumnRemovable(col)) {
                    this.checked = true;
                    hiddenCols[col] = false;
                    return;
                }
                hiddenCols[col] = !this.checked;
                renderHeaders();
                renderPage();
            });

            label.appendChild(cb);
            label.appendChild(document.createTextNode(' ' + col));
            colToggles.appendChild(label);
        });

        renderHeaders();
    }

    function renderHeaders() {
        headerRow.innerHTML = '';
        filterRow.innerHTML = '';

        var visible = columns.filter(function (c) { return !hiddenCols[c]; });

        visible.forEach(function (col) {
            /* --- sort header --- */
            var th = document.createElement('th');
            th.className  = 'ot-th';
            th.dataset.col = col;

            var sortable = isColumnSortable(col);
            if (!sortable) {
                th.classList.add('ot-th--nonsortable');
            }

            var lbl = document.createElement('span');
            lbl.className   = 'ot-th__label';
            lbl.textContent = col;

            var icn = document.createElement('span');
            icn.className = 'ot-th__sort-icon';
            if (!sortable) {
                icn.innerHTML = '<i class="fa-solid fa-minus ot-sort-idle"></i>';
            } else if (col === sortCol) {
                icn.innerHTML = sortDir === 1
                    ? '<i class="fa-solid fa-sort-up"></i>'
                    : '<i class="fa-solid fa-sort-down"></i>';
                th.classList.add(sortDir === 1 ? 'ot-th--asc' : 'ot-th--desc');
            } else {
                icn.innerHTML = '<i class="fa-solid fa-sort ot-sort-idle"></i>';
            }

            th.appendChild(lbl);
            th.appendChild(icn);
            th.addEventListener('click', function () {
                if (!isColumnSortable(col)) {
                    return;
                }
                if (sortCol === col) {
                    sortDir = -sortDir;
                } else {
                    sortCol = col;
                    sortDir = 1;
                }
                currentPage = 1;
                renderHeaders();
                applyFilterSort();
            });
            headerRow.appendChild(th);

            /* --- filter input --- */
            var ftd = document.createElement('th');
            ftd.className = 'ot-filter-cell';
            if (isColumnFilterable(col)) {
                var otUniqueVals = allRows.length
                    ? Array.from(new Set(allRows.map(function (r) {
                        return r[col] == null ? '' : String(r[col]);
                    }))).sort()
                    : [];
                if (allRows.length > 0 && otUniqueVals.length <= 20
                    && shouldUseDropdownFilter(col)) {
                    var sel = document.createElement('select');
                    sel.className = 'ot-filter-select';
                    sel.dataset.col = col;
                    sel.title = 'Filter ' + col;
                    var optAll = document.createElement('option');
                    optAll.value = ''; optAll.textContent = '— all —';
                    sel.appendChild(optAll);
                    otUniqueVals.forEach(function (v) {
                        var opt = document.createElement('option');
                        opt.value = v.toLowerCase();
                        opt.textContent = v === '' ? '(blank)' : v;
                        if ((colFilters[col] || '').toLowerCase() === v.toLowerCase()) opt.selected = true;
                        sel.appendChild(opt);
                    });
                    sel.addEventListener('change', function () {
                        colFilters[col] = sel.value;
                        currentPage = 1;
                        applyFilterSort();
                    });
                    ftd.appendChild(sel);
                } else {
                    var inp = document.createElement('input');
                    inp.type        = 'text';
                    inp.className   = 'ot-filter-input';
                    inp.placeholder = '\u2315';
                    inp.value       = colFilters[col] || '';
                    inp.dataset.col = col;
                    inp.title       = 'Filter ' + col;
                    inp.addEventListener('input', function () {
                        colFilters[col] = this.value;
                        currentPage = 1;
                        applyFilterSort();
                    });
                    ftd.appendChild(inp);
                }
            }
            filterRow.appendChild(ftd);
        });

        syncScrollMirror();
    }

    /* -----------------------------------------------------------------------
       Filter + sort
    ----------------------------------------------------------------------- */
    function applyFilterSort() {
        filteredRows = allRows.filter(function (row) {
            // Group tab filter: only show objects in the group
            if (activeFindTab === 'group'
                    && groupFilterNames !== null) {
                var objName = String(
                    row['OBJNAME'] || ''
                ).toUpperCase();
                if (!groupFilterNames[objName]) {
                    return false;
                }
            }

            if (activeFindTab === 'advanced') {
                var advCol = String(advancedFilterApplied.column || '');
                if (advCol) {
                    var advColType = String(advancedFilterApplied.colType || 'string');
                    if (advColType === 'number' || advColType === 'int' || advColType === 'float') {
                        var advFromNum = advancedFilterApplied.from !== ''
                            ? Number(advancedFilterApplied.from) : null;
                        var advToNum = advancedFilterApplied.to !== ''
                            ? Number(advancedFilterApplied.to) : null;
                        if ((advFromNum !== null && !isNaN(advFromNum))
                                || (advToNum !== null && !isNaN(advToNum))) {
                            var advCellNum = parseStrictNumber(row[advCol]);
                            if (advCellNum === null) return false;
                            if (advFromNum !== null && !isNaN(advFromNum)
                                    && advCellNum < advFromNum) return false;
                            if (advToNum !== null && !isNaN(advToNum)
                                    && advCellNum > advToNum) return false;
                        }
                    } else if (advColType === 'date' || advColType === 'datetime'
                            || advColType === 'night') {
                        var advFromDate = advancedFilterApplied.from
                            ? Date.parse(advancedFilterApplied.from + 'T00:00:00Z') : null;
                        var advToDate = advancedFilterApplied.to
                            ? Date.parse(advancedFilterApplied.to + 'T23:59:59Z') : null;
                        if ((advFromDate !== null && !isNaN(advFromDate))
                                || (advToDate !== null && !isNaN(advToDate))) {
                            var advCellDate = parseNightDate(row[advCol]);
                            if (advCellDate === null) return false;
                            if (advFromDate !== null && !isNaN(advFromDate)
                                    && advCellDate < advFromDate) return false;
                            if (advToDate !== null && !isNaN(advToDate)
                                    && advCellDate > advToDate) return false;
                        }
                    } else {
                        var advQuery = String(advancedFilterApplied.contains || '')
                            .trim().toLowerCase();
                        if (advQuery) {
                            var advCell = (row[advCol] === null || row[advCol] === undefined)
                                ? '' : String(row[advCol]).toLowerCase();
                            if (advCell.indexOf(advQuery) === -1) return false;
                        }
                    }
                }
            }

            if (activeFindTab === 'date') {
                var firstStr = String(dateFilterApplied.first || '').trim();
                var lastStr = String(dateFilterApplied.last || '').trim();
                if (firstStr || lastStr) {
                    var dateRaw = row['last obs'] || row['latest obs'] || '';
                    var dateTs = parseNightDate(dateRaw);
                    if (dateTs === null) {
                        return false;
                    }
                    var firstTs = firstStr ? Date.parse(firstStr + 'T00:00:00Z') : null;
                    var lastTs = lastStr ? Date.parse(lastStr + 'T23:59:59Z') : null;
                    if (firstTs !== null && !isNaN(firstTs) && dateTs < firstTs) {
                        return false;
                    }
                    if (lastTs !== null && !isNaN(lastTs) && dateTs > lastTs) {
                        return false;
                    }
                }
            }

            for (var col in colFilters) {
                if (!isColumnFilterable(col)) {
                    continue;
                }
                var fv = colFilters[col];
                if (!fv) continue;
                var cell = (row[col] === null || row[col] === undefined)
                    ? '' : String(row[col]);
                if (cell.toLowerCase().indexOf(fv.toLowerCase()) === -1) {
                    return false;
                }
            }
            return true;
        });

        if (sortCol && isColumnSortable(sortCol)) {
            filteredRows.sort(function (a, b) {
                var av = (a[sortCol] === null || a[sortCol] === undefined)
                    ? '' : a[sortCol];
                var bv = (b[sortCol] === null || b[sortCol] === undefined)
                    ? '' : b[sortCol];

                var va = normalizeForSort(sortCol, av);
                var vb = normalizeForSort(sortCol, bv);

                if (va.kind === 'number' && vb.kind === 'number') {
                    return sortDir * (va.value - vb.value);
                }

                var sa = String(va.value);
                var sb = String(vb.value);
                if (sa < sb) return -sortDir;
                if (sa > sb) return  sortDir;
                return 0;
            });
        } else if (sortCol && !isColumnSortable(sortCol)) {
            sortCol = null;
            sortDir = 1;
        }

        updatePagination();
        renderPage();
    }

    /* -----------------------------------------------------------------------
       Render one page of rows
    ----------------------------------------------------------------------- */
    function renderPage() {
        var visible = columns.filter(function (c) { return !hiddenCols[c]; });
        var total   = filteredRows.length;

        var start = 0;
        var end   = total;
        if (perPage > 0) {
            start = (currentPage - 1) * perPage;
            end   = Math.min(start + perPage, total);
        }
        var pageRows = filteredRows.slice(start, end);

        tbody.innerHTML = '';

        if (pageRows.length === 0) {
            var tr = document.createElement('tr');
            var td = document.createElement('td');
            td.colSpan   = visible.length || 1;
            td.className = allRows.length === 0 ? 'ot-empty' : 'ot-empty';
            td.textContent = allRows.length === 0
                ? 'No data available for this profile.'
                : 'No rows match the current filters.';
            tr.appendChild(td);
            tbody.appendChild(tr);
            syncScrollMirror();
            return;
        }

        var frag = document.createDocumentFragment();
        pageRows.forEach(function (row) {
            var tr = document.createElement('tr');
            tr.className = 'ot-row';

            visible.forEach(function (col) {
                var td = document.createElement('td');
                td.className = 'ot-cell';

                var val = row[col];
                if (val === null || val === undefined || val === '') {
                    td.innerHTML = '<span class="ot-null">\u2014</span>';
                } else if (col === 'OBJNAME') {
                    var a = document.createElement('a');
                    a.href      = '/data_portal/'
                        + encodeURIComponent(cfg.profileId)
                        + '/' + encodeURIComponent(String(val));
                    a.className = 'ot-obj-link';
                    a.textContent = String(val);
                    a.title = 'Open object page';
                    td.appendChild(a);
                } else if (getColumnMeta(col).type === 'count') {
                    var parts = /^(\d+)\s*\((\d+)\)$/.exec(String(val).trim());
                    if (parts) {
                        var nAcc = parseInt(parts[1], 10);
                        var nTot = parseInt(parts[2], 10);
                        td.innerHTML = nAcc < nTot
                            ? '<span class="ot-count-partial" title="'
                                + nAcc + ' accessible out of ' + nTot + ' total">'  
                                + escHtml(val) + '</span>'
                            : '<span class="ot-count-full" title="All '
                                + nTot + ' files accessible">' + escHtml(val) + '</span>';
                    } else {
                        td.textContent = String(val);
                    }
                } else {
                    td.textContent = String(val);
                }
                tr.appendChild(td);
            });

            frag.appendChild(tr);
        });
        tbody.appendChild(frag);

        syncScrollMirror();
    }

    /* -----------------------------------------------------------------------
       Pagination
    ----------------------------------------------------------------------- */
    function updatePagination() {
        var total      = filteredRows.length;
        var totalPages = (perPage > 0)
            ? Math.max(1, Math.ceil(total / perPage))
            : 1;

        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1)         currentPage = 1;

        var start = (perPage > 0) ? (currentPage - 1) * perPage + 1 : 1;
        var end   = (perPage > 0) ? Math.min(currentPage * perPage, total) : total;
        if (total === 0) { start = 0; end = 0; }

        var allTotal = allRows.length;
        var suffix   = (total < allTotal)
            ? ' (filtered from ' + allTotal + ')'
            : '';
        pageInfo.textContent = 'Showing '
            + (total === 0 ? 0 : start) + '\u2013' + end
            + ' of ' + total + ' rows' + suffix;

        rowSummaryEl.textContent = total + ' of ' + allTotal + ' objects';

        pageInput.value = currentPage;
        pageInput.max   = totalPages;
        pageTotal.textContent = totalPages;

        btnFirst.disabled = (currentPage <= 1);
        btnPrev.disabled  = (currentPage <= 1);
        btnNext.disabled  = (currentPage >= totalPages);
        btnLast.disabled  = (currentPage >= totalPages);
    }

    /* -----------------------------------------------------------------------
       Dual scroll mirror
    ----------------------------------------------------------------------- */
    function syncScrollMirror() {
        scrollSizer.style.width = tableEl.scrollWidth + 'px';
    }

    var _scrollSync = false;
    scrollTopEl.addEventListener('scroll', function () {
        if (_scrollSync) return;
        _scrollSync = true;
        tableWrap.scrollLeft = scrollTopEl.scrollLeft;
        _scrollSync = false;
    });
    tableWrap.addEventListener('scroll', function () {
        if (_scrollSync) return;
        _scrollSync = true;
        scrollTopEl.scrollLeft = tableWrap.scrollLeft;
        _scrollSync = false;
        syncScrollMirror();
    });

    /* -----------------------------------------------------------------------
       Pagination event listeners
    ----------------------------------------------------------------------- */
    btnFirst.addEventListener('click', function () {
        currentPage = 1;
        updatePagination();
        renderPage();
    });
    btnPrev.addEventListener('click', function () {
        currentPage = Math.max(1, currentPage - 1);
        updatePagination();
        renderPage();
    });
    btnNext.addEventListener('click', function () {
        var total = filteredRows.length;
        var tp    = (perPage > 0) ? Math.ceil(total / perPage) : 1;
        currentPage = Math.min(tp, currentPage + 1);
        updatePagination();
        renderPage();
    });
    btnLast.addEventListener('click', function () {
        var total = filteredRows.length;
        currentPage = (perPage > 0) ? Math.max(1, Math.ceil(total / perPage)) : 1;
        updatePagination();
        renderPage();
    });
    pageInput.addEventListener('change', function () {
        var v = parseInt(this.value, 10);
        if (!isNaN(v)) {
            currentPage = v;
            updatePagination();
            renderPage();
        }
    });
    perpageSelect.addEventListener('change', function () {
        perPage     = parseInt(this.value, 10) || 0;
        currentPage = 1;
        updatePagination();
        renderPage();
    });

    /* -----------------------------------------------------------------------
       Column toggle panel
    ----------------------------------------------------------------------- */
    btnColumns.addEventListener('click', function (e) {
        e.stopPropagation();
        colPanel.style.display = (colPanel.style.display === 'none')
            ? 'block' : 'none';
    });
    colClose.addEventListener('click', function () {
        colPanel.style.display = 'none';
    });
    document.addEventListener('click', function (e) {
        if (!colPanel.contains(e.target) && e.target !== btnColumns) {
            colPanel.style.display = 'none';
        }
    });
    colAll.addEventListener('click', function () {
        hiddenCols = {};
        columns.forEach(function (col) {
            hiddenCols[col] = false;
        });
        colToggles.querySelectorAll('input[type=checkbox]').forEach(function (cb) {
            cb.checked = true;
        });
        renderHeaders();
        renderPage();
    });
    colNone.addEventListener('click', function () {
        columns.forEach(function (col) {
            hiddenCols[col] = isColumnRemovable(col);
        });
        colToggles.querySelectorAll('input[type=checkbox]').forEach(function (cb) {
            cb.checked = !hiddenCols[cb.dataset.col];
        });
        renderHeaders();
        renderPage();
    });

    /* -----------------------------------------------------------------------
       Clear filters
    ----------------------------------------------------------------------- */
    btnClearFilter.addEventListener('click', function () {
        colFilters = {};
        filterRow.querySelectorAll('input.ot-filter-input').forEach(
            function (inp) { inp.value = ''; }
        );
        currentPage = 1;
        applyFilterSort();
    });

    if (hasFindControls) {
        var debouncedLoad = debounce(function () {
            currentPage = 1;
            loadData();
        }, 250);

        findTabName.addEventListener('click', function () {
            setFindTab('name');
            currentPage = 1;
            loadData();
        });
        findTabCoords.addEventListener('click', function () {
            setFindTab('coords');
            currentPage = 1;
            loadData();
        });
        findTabDate.addEventListener('click', function () {
            setFindTab('date');
            currentPage = 1;
            loadData();
        });
        findTabAdvanced.addEventListener('click', function () {
            setFindTab('advanced');
            currentPage = 1;
            loadData();
        });

        findNameInput.addEventListener('input', function () {
            if (activeFindTab !== 'name') {
                return;
            }
            debouncedLoad();
        });

        findCoordsBtn.addEventListener('click', function () {
            coordSearchRequested = true;
            currentPage = 1;
            loadData();
        });

        findDateApplyBtn.addEventListener('click', function () {
            var first = String(findDateFirstInput.value || '').trim();
            var last = String(findDateLastInput.value || '').trim();
            dateFilterApplied = { first: first, last: last };
            currentPage = 1;
            applyFilterSort();
            setFindStatus('Date filter applied.', false);
        });

        findAdvancedColumnSelect.addEventListener('change', function () {
            advancedFilterApplied = { column: '', colType: '', contains: '', from: '', to: '' };
            advancedBindInputs();
        });

        findAdvancedApplyBtn.addEventListener('click', function () {
            advancedFilterApplied = getAdvancedFilterState();
            currentPage = 1;
            applyFilterSort();
            setFindStatus('Advanced filter applied.', false);
        });

        [findRaInput, findDecInput, findSepInput].forEach(function (el) {
            el.addEventListener('input', function () {
                if (activeFindTab === 'coords') {
                    coordSearchRequested = false;
                    setFindStatus('Enter RA, Dec, and separation, then click Find.', false);
                }
            });
        });
        findCoordFormatSelect.addEventListener('change', function () {
            coordSearchRequested = false;
            syncCoordInputFormatUi();
            if (activeFindTab === 'coords') {
                setFindStatus('Enter RA, Dec, and separation, then click Find.', false);
            }
        });
        findUnitSelect.addEventListener('change', function () {
            if (activeFindTab === 'coords') {
                coordSearchRequested = false;
                setFindStatus('Enter RA, Dec, and separation, then click Find.', false);
            }
        });

        findClearBtn.addEventListener('click', function () {
            clearFindInputs();
            setFindTab(activeFindTab);
            currentPage = 1;
            loadData();
        });

        setFindTab('name');
        syncCoordInputFormatUi();
    }

    /* -----------------------------------------------------------------------
       Group tab: populate dropdown from groups API
    ----------------------------------------------------------------------- */
    var groupsApiBase = (cfg && cfg.groupsApiBase) || '';

    function fetchGroupsList(selectEl, callback) {
        if (!groupsApiBase || !selectEl) return;
        var url = groupsApiBase + '/list?profile_id='
            + encodeURIComponent(cfg.profileId);
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                selectEl.innerHTML = '';
                // placeholder option
                var ph = document.createElement('option');
                ph.value = '';
                ph.textContent = '— select group —';
                selectEl.appendChild(ph);
                if (!data.success || !data.groups) return;
                data.groups.forEach(function (g) {
                    var opt = document.createElement('option');
                    opt.value = g.name;
                    opt.textContent = g.name
                        + ' (' + g.object_count + ')';
                    selectEl.appendChild(opt);
                });
                if (callback) callback(data.groups);
            })
            .catch(function () {
                selectEl.innerHTML = '';
                var err = document.createElement('option');
                err.value = '';
                err.textContent = 'Failed to load groups';
                selectEl.appendChild(err);
            });
    }

    function fetchGroupObjects(groupName, callback) {
        if (!groupsApiBase || !groupName) {
            callback([]);
            return;
        }
        var url = groupsApiBase + '/objects?profile_id='
            + encodeURIComponent(cfg.profileId)
            + '&group='
            + encodeURIComponent(groupName);
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    callback([]);
                    return;
                }
                var names = (data.objects || []).map(
                    function (o) { return o.objname; }
                );
                callback(names);
            })
            .catch(function () { callback([]); });
    }

    // Populate group dropdown on tab select
    if (hasFindControls && findTabGroup) {
        findTabGroup.addEventListener('click', function () {
            setFindTab('group');
            fetchGroupsList(findGroupSelect);
            currentPage = 1;
            loadData();
        });

        if (findGroupApplyBtn) {
            findGroupApplyBtn.addEventListener('click', function () {
                var gName = String(
                    findGroupSelect.value || ''
                ).trim();
                if (!gName) {
                    groupFilterNames = null;
                    currentPage = 1;
                    applyFilterSort();
                    setFindStatus('No group selected.', true);
                    return;
                }
                setFindStatus('Loading group...', false);
                fetchGroupObjects(gName, function (names) {
                    // Build lookup set
                    groupFilterNames = {};
                    names.forEach(function (n) {
                        groupFilterNames[
                            String(n).toUpperCase()
                        ] = true;
                    });
                    currentPage = 1;
                    applyFilterSort();
                    var msg = 'Group "' + gName
                        + '": ' + names.length
                        + ' objects. Showing '
                        + filteredRows.length
                        + ' matching rows.';
                    setFindStatus(msg, false);
                });
            });
        }

        if (findGroupClearBtn) {
            findGroupClearBtn.addEventListener('click', function () {
                groupFilterNames = null;
                if (findGroupSelect) findGroupSelect.value = '';
                currentPage = 1;
                applyFilterSort();
                setFindStatus('Group filter cleared.', false);
            });
        }
    }

    /* -----------------------------------------------------------------------
       Send to Group overlay
    ----------------------------------------------------------------------- */
    function stgShow() {
        if (!stgOverlay) return;
        // Update count of objects to send
        var count = filteredRows.length;
        if (stgCount) {
            stgCount.textContent = 'Add '
                + count + ' filtered object'
                + (count !== 1 ? 's' : '')
                + ' to the selected group.';
        }
        if (stgStatus) stgStatus.textContent = '';
        if (stgNewName) stgNewName.value = '';
        // Populate group dropdown
        fetchGroupsList(stgSelect);
        stgOverlay.style.display = '';
    }

    function stgHide() {
        if (stgOverlay) stgOverlay.style.display = 'none';
    }

    if (btnSendToGroup) {
        btnSendToGroup.addEventListener('click', stgShow);
    }
    if (stgClose) {
        stgClose.addEventListener('click', stgHide);
    }
    if (stgBackdrop) {
        stgBackdrop.addEventListener('click', stgHide);
    }

    // Create new group inside overlay
    if (stgCreateBtn && stgNewName && stgSelect) {
        stgCreateBtn.addEventListener('click', function () {
            var name = String(stgNewName.value || '').trim();
            if (!name) {
                if (stgStatus) {
                    stgStatus.textContent = 'Enter a name.';
                }
                return;
            }
            if (stgStatus) {
                stgStatus.textContent = 'Creating...';
            }
            fetch(groupsApiBase + '/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    profile_id: cfg.profileId,
                    name: name,
                }),
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    if (stgStatus) {
                        stgStatus.textContent = data.error
                            || 'Create failed.';
                    }
                    return;
                }
                // Refresh dropdown and select new group
                fetchGroupsList(stgSelect, function () {
                    stgSelect.value = name;
                });
                stgNewName.value = '';
                if (stgStatus) {
                    stgStatus.textContent = 'Created "'
                        + name + '".';
                }
            })
            .catch(function () {
                if (stgStatus) {
                    stgStatus.textContent = 'Network error.';
                }
            });
        });
    }

    // Send filtered objects to selected group
    if (stgSendBtn) {
        stgSendBtn.addEventListener('click', function () {
            var gName = String(
                stgSelect ? stgSelect.value : ''
            ).trim();
            if (!gName) {
                if (stgStatus) {
                    stgStatus.textContent = 'Select a group.';
                }
                return;
            }
            // Collect OBJNAME from filtered rows
            var names = filteredRows.map(function (r) {
                return r['OBJNAME'] || '';
            }).filter(function (n) { return !!n; });
            if (!names.length) {
                if (stgStatus) {
                    stgStatus.textContent = 'No objects to send.';
                }
                return;
            }
            if (stgStatus) {
                stgStatus.textContent = 'Sending '
                    + names.length + ' objects...';
            }
            stgSendBtn.disabled = true;

            fetch(groupsApiBase + '/add-objects-json', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    profile_id: cfg.profileId,
                    group: gName,
                    objnames: names,
                }),
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                stgSendBtn.disabled = false;
                if (!data.success) {
                    if (stgStatus) {
                        stgStatus.textContent = data.error
                            || 'Send failed.';
                    }
                    return;
                }
                var parts = [];
                if (data.added) {
                    parts.push(data.added + ' added');
                }
                if (data.skipped) {
                    parts.push(data.skipped + ' already in group');
                }
                if (data.not_found && data.not_found.length) {
                    parts.push(
                        data.not_found.length + ' not found'
                    );
                }
                if (stgStatus) {
                    stgStatus.textContent = 'Done: '
                        + parts.join(', ') + '.';
                }
            })
            .catch(function () {
                stgSendBtn.disabled = false;
                if (stgStatus) {
                    stgStatus.textContent = 'Network error.';
                }
            });
        });
    }

    /* -----------------------------------------------------------------------
       Window resize: re-sync scroll mirror width
    ----------------------------------------------------------------------- */
    window.addEventListener('resize', syncScrollMirror);

    /* -----------------------------------------------------------------------
       Init
    ----------------------------------------------------------------------- */
    loadData();

}());
