/* ==========================================================================
   File Browser tab – object page file table with preset filters,
   group-by, multi-select and add-to-basket functionality.

   Expects window.ARI_OBJECT_PAGE to be set (apiUrl, profileId, objname, etc.)
   and window.ARI_BASKET_CFG for basket API endpoints.
   ========================================================================== */
(function () {
    'use strict';

    var pageCfg    = window.ARI_OBJECT_PAGE || {};
    var basketCfg  = window.ARI_BASKET_CFG  || {};

    /* -----------------------------------------------------------------------
       State
    ----------------------------------------------------------------------- */
    var fbAllRows      = [];   // all accessible rows returned by API
    var fbTotalRows    = 0;    // total rows (before access filter)
    var fbQueryTime    = null;
    var fbFilteredRows = [];   // after preset + column filters
    var fbGroupByCol   = '';
    var fbSortCol      = null;
    var fbSortDir      = 1;
    var fbColFilters   = {};
    var fbCheckedRows  = new Set();  // set of IDENTIFIER + FILENAME composite keys
    var fbCurrentPage  = 1;
    var fbPerPage      = 50;
    var fbLoaded       = false;
    var fbFilterTimers = {};
    var FB_FILTER_DEBOUNCE_MS = 550;

    /* Exact output types with a Bokeh plot (plots_filename.py). */
    /* Plot-type sets – populated from window.ARI_* injected by the
       template (data_portal_view_helpers.py → object_page.html).
       The inline literals below are kept as a fallback only. */
    var FB_PLOTABLE_OUTPUTS = new Set(
        (window.ARI_PLOTABLE_OUTPUTS && window.ARI_PLOTABLE_OUTPUTS.length)
            ? window.ARI_PLOTABLE_OUTPUTS
            : [
                'DRS_POST_E', 'DRS_POST_T', 'DRS_POST_S',
                'DRS_POST_P', 'DRS_POST_V',
              ]
    );

    /* KW_OUTPUT prefixes that map to the DS9-style 2D frame viewer. */
    var FB_FRAME_PREFIXES =
        (window.ARI_FRAME_PREFIXES && window.ARI_FRAME_PREFIXES.length)
            ? window.ARI_FRAME_PREFIXES
            : ['RAW_', 'DRS_PP'];

    function isPlotableOutput(kw) {
        if (FB_PLOTABLE_OUTPUTS.has(kw)) return true;
        for (var _fpi = 0; _fpi < FB_FRAME_PREFIXES.length; _fpi++) {
            if (kw.startsWith(FB_FRAME_PREFIXES[_fpi])) return true;
        }
        return false;
    }

    /* -----------------------------------------------------------------------
       Columns for the file browser table
    ----------------------------------------------------------------------- */
    var FB_COLUMNS = [
        { key: 'BLOCK_KIND',    label: 'Block',        sortable: true,  filterable: true },
        { key: 'OBS_DIR',       label: 'Obs Dir',      sortable: true,  filterable: true },
        { key: 'FILENAME',      label: 'Filename',     sortable: true,  filterable: true },
        { key: 'KW_OUTPUT',     label: 'Output Type',  sortable: true,  filterable: true },
        { key: 'KW_FIBER',      label: 'Fiber',        sortable: true,  filterable: true },
        { key: 'KW_DPRTYPE',    label: 'DPRTYPE',      sortable: true,  filterable: true },
        { key: 'KW_PI_NAME',    label: 'PI Name',      sortable: true,  filterable: true },
        { key: 'MID_OBS_TIME',  label: 'Mid Obs Time', sortable: true,  filterable: true },
        { key: 'PASSED_ALL_QC', label: 'QC',           sortable: true,  filterable: true },
        { key: 'KW_RUN_ID',     label: 'Run ID',       sortable: true,  filterable: true },
    ];

    var FB_GROUP_OPTIONS = [
        'BLOCK_KIND', 'OBS_DIR', 'KW_OUTPUT', 'KW_DPRTYPE',
    ];

    var FB_PRESETS = [
        { id: 'default',  label: 'All processed (out, QC\u22651)', preset: 'default' },
        { id: 'none',     label: 'All files',                      preset: 'none'    },
        { id: 'ext2d',    label: 'Extracted 2D spectra',          preset: 'ext2d'   },
        { id: 'tcorr2d',  label: 'Telluric corrected 2D spectra', preset: 'tcorr2d' },
        { id: 'tcorr1d',  label: 'Telluric corrected 1D spectra', preset: 'tcorr1d' },
    ];
    // Conditionally add polar preset if instrument has polarimetry
    if (window.ARI_OBJECT_PAGE && window.ARI_OBJECT_PAGE.hasPolarimetry) {
        FB_PRESETS.push({ id: 'polar', label: 'Polar spectra', preset: 'polar' });
    }
    // Always add these after polar (or instead of)
    FB_PRESETS.push(
        { id: 'ccfrv',    label: 'CCF RV',                        preset: 'ccfrv'   },
        { id: 'rdb',      label: 'rdb',                           preset: 'rdb'     },
        { id: 'lbl',      label: 'All LBL products',              preset: 'lbl'     }
    );
    var fbActivePreset = 'default';

    /* -----------------------------------------------------------------------
       DOM refs (resolved lazily since the tab is hidden on page load)
    ----------------------------------------------------------------------- */
    function el(id) { return document.getElementById(id); }

    /* -----------------------------------------------------------------------
       Helpers
    ----------------------------------------------------------------------- */
    function escHtml(str) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(str == null ? '' : str)));
        return d.innerHTML;
    }
    function valOrDash(v) {
        if (v === null || v === undefined) return '--';
        var s = String(v).trim();
        return s === '' ? '--' : s;
    }
    function rowKey(r) {
        return (r.IDENTIFIER || '') + '|' + (r.FILENAME || '');
    }
    function formatDate(iso) {
        if (!iso) return '--';
        try { return new Date(iso).toLocaleString(); }
        catch (e) { return String(iso); }
    }

    function parseStrictNumber(value) {
        var raw = String(value === null || value === undefined ? '' : value).trim();
        if (!raw || !/^-?\d+(\.\d+)?$/.test(raw)) return null;
        var num = Number(raw);
        return isNaN(num) ? null : num;
    }

    function parseDateLike(value) {
        var raw = String(value === null || value === undefined ? '' : value).trim();
        if (!raw) return null;
        var parsed = Date.parse(raw);
        return isNaN(parsed) ? null : parsed;
    }

    function normalizeBoolToken(value) {
        var raw = String(value === null || value === undefined ? '' : value)
            .trim().toLowerCase();
        if (!raw) return '';
        if (raw === '1' || raw === 'true' || raw === 't'
                || raw === 'yes' || raw === 'y') {
            return 'true';
        }
        if (raw === '0' || raw === 'false' || raw === 'f'
                || raw === 'no' || raw === 'n') {
            return 'false';
        }
        return '';
    }

    function isBooleanLikeValues(values) {
        if (!values || !values.length) return false;
        return values.every(function (v) {
            return normalizeBoolToken(v) !== '';
        });
    }

    function shouldUseDropdownFilter(colKey) {
        var cname = String(colKey || '').toLowerCase();
        if (/(date|time|timestamp|night|mjd|jd|unix|obs_time)/.test(cname)) {
            return false;
        }

        var nonBlank = fbAllRows.map(function (r) {
            return r[colKey];
        }).filter(function (v) {
            return v !== null && v !== undefined && String(v).trim() !== '';
        });

        if (!nonBlank.length) {
            return true;
        }

        if (isBooleanLikeValues(nonBlank)) {
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
            return parseDateLike(v) !== null;
        });
        if (allDateLike) {
            return false;
        }

        return true;
    }

    /* -----------------------------------------------------------------------
       Load data (called once when tab first activated)
    ----------------------------------------------------------------------- */
    function loadFbData(preset) {
        if (preset !== undefined) fbActivePreset = preset;
        var container = el('fb-container');
        if (!container) return;

        var url = (basketCfg.fileBrowserApiUrl || '/api/data-portal/file-browser')
            + '?profile_id=' + encodeURIComponent(pageCfg.profileId || '')
            + '&objname='    + encodeURIComponent(pageCfg.objname || '')
            + '&preset='     + encodeURIComponent(fbActivePreset);

        var loadingEl = el('fb-loading');
        if (loadingEl) loadingEl.style.display = '';
        var tableWrap = el('fb-table-wrap');
        if (tableWrap) tableWrap.style.display = 'none';

        fetch(url)
            .then(function (r) {
                var ctype = String(r.headers.get('content-type') || '').toLowerCase();
                if (ctype.indexOf('application/json') === -1) {
                    return r.text().then(function (_txt) {
                        throw new Error('File browser API returned non-JSON response ('
                            + r.status + ').');
                    });
                }
                return r.json().then(function (data) {
                    if (!r.ok) {
                        var msg = (data && data.error) ? data.error
                            : ('File browser request failed (' + r.status + ').');
                        throw new Error(msg);
                    }
                    return data;
                });
            })
            .then(function (data) {
                if (loadingEl) loadingEl.style.display = 'none';
                if (tableWrap) tableWrap.style.display = '';
                if (!data.success) {
                    var errEl = el('fb-error');
                    if (errEl) { errEl.textContent = data.error || 'Load error'; errEl.style.display = ''; }
                    return;
                }
                fbAllRows   = data.rows || [];
                fbTotalRows = data.total || 0;
                fbQueryTime = data.query_time || null;
                fbLoaded    = true;
                fbCheckedRows.clear();
                updateSelectionState();
                updateCounterBanner();
                fbApplyFilterSort();
            })
            .catch(function (err) {
                if (loadingEl) loadingEl.style.display = 'none';
                var errEl = el('fb-error');
                if (errEl) { errEl.textContent = 'Network error: ' + String(err); errEl.style.display = ''; }
            });
    }

    /* -----------------------------------------------------------------------
       Counter banner
    ----------------------------------------------------------------------- */
    function updateCounterBanner() {
        var filesEl = el('fb-stat-files');
        var filesSubEl = el('fb-stat-files-sub');
        var queryEl = el('fb-stat-query');
        if (!filesEl || !filesSubEl || !queryEl) return;
        var n = fbAllRows.length;
        var m = fbTotalRows;
        filesEl.textContent = String(n);
        filesSubEl.textContent = 'before access: ' + m;
        if (fbQueryTime != null) {
            queryEl.textContent = fbQueryTime.toFixed(2) + ' s';
        } else {
            queryEl.textContent = '--';
        }
    }

    function syncPresetButtons() {
        document.querySelectorAll('.fb-preset-btn').forEach(function (b) {
            b.classList.toggle('fb-preset-btn--active', b.dataset.preset === fbActivePreset);
        });
    }

    /* -----------------------------------------------------------------------
       Filter + sort
    ----------------------------------------------------------------------- */
    function fbApplyFilterSort() {
        var rows = fbAllRows.slice();

        // column filters (only for flat mode)
        if (!fbGroupByCol) {
            Object.keys(fbColFilters).forEach(function (col) {
                var q = fbColFilters[col];
                if (!q) return;
                rows = rows.filter(function (r) {
                    var cellRaw = String(r[col] == null ? '' : r[col]);
                    var cell = cellRaw.toLowerCase();
                    if (q === '__bool_true__') {
                        return normalizeBoolToken(cellRaw) === 'true';
                    }
                    if (q === '__bool_false__') {
                        return normalizeBoolToken(cellRaw) === 'false';
                    }
                    if (q === '__blank__') {
                        return cell.trim() === '';
                    }
                    return cell.indexOf(q) !== -1;
                });
            });
        }

        // sort
        if (fbSortCol) {
            var col = fbSortCol;
            rows.sort(function (a, b) {
                var av = a[col] == null ? '' : String(a[col]);
                var bv = b[col] == null ? '' : String(b[col]);
                return av < bv ? -fbSortDir : av > bv ? fbSortDir : 0;
            });
        }

        // group-by
        if (fbGroupByCol) {
            var groups = {};
            var groupOrder = [];
            rows.forEach(function (r) {
                var key = String(r[fbGroupByCol] == null ? '' : r[fbGroupByCol]);
                if (!groups[key]) {
                    groups[key] = { group_value: key, file_count: 0, rows: [] };
                    groupOrder.push(key);
                }
                groups[key].rows.push(r);
                groups[key].file_count += 1;
            });
            var grouped = groupOrder.map(function (k) { return groups[k]; });
            if (fbSortCol === 'group_value' || fbSortCol === 'file_count') {
                var sc2 = fbSortCol;
                grouped.sort(function (a, b) {
                    var av2 = String(a[sc2] == null ? '' : a[sc2]);
                    var bv2 = String(b[sc2] == null ? '' : b[sc2]);
                    return av2 < bv2 ? -fbSortDir : av2 > bv2 ? fbSortDir : 0;
                });
            }
            fbFilteredRows = grouped;
        } else {
            fbFilteredRows = rows;
        }

        fbCurrentPage = 1;
        fbUpdatePagination();
        fbRenderHeaders();
        fbRenderPage();
    }

    /* -----------------------------------------------------------------------
       Pagination
    ----------------------------------------------------------------------- */
    function fbTotalPages() {
        if (!fbPerPage) return 1;
        return Math.max(1, Math.ceil(fbFilteredRows.length / fbPerPage));
    }

    function fbPageRows() {
        if (!fbPerPage) return fbFilteredRows;
        var start = (fbCurrentPage - 1) * fbPerPage;
        return fbFilteredRows.slice(start, start + fbPerPage);
    }

    function fbUpdatePagination() {
        var tp = fbTotalPages();
        if (fbCurrentPage > tp) fbCurrentPage = tp;
        var infoEl = el('fb-page-info');
        if (infoEl) infoEl.textContent = fbFilteredRows.length + ' rows';
        var inp = el('fb-page-input');
        if (inp) inp.value = fbCurrentPage;
        var tot = el('fb-page-total');
        if (tot) tot.textContent = tp;
        var btnF = el('fb-btn-first'), btnP = el('fb-btn-prev');
        var btnN = el('fb-btn-next'),  btnL = el('fb-btn-last');
        if (btnF) btnF.disabled = fbCurrentPage <= 1;
        if (btnP) btnP.disabled = fbCurrentPage <= 1;
        if (btnN) btnN.disabled = fbCurrentPage >= tp;
        if (btnL) btnL.disabled = fbCurrentPage >= tp;
    }

    /* -----------------------------------------------------------------------
       Render headers
    ----------------------------------------------------------------------- */
    function fbRenderHeaders() {
        var hr = el('fb-header-row');
        var fr = el('fb-filter-row');
        if (!hr || !fr) return;
        hr.innerHTML = '';
        fr.innerHTML = '';

        // Select-all checkbox
        var thCheck = document.createElement('th');
        thCheck.className = 'ot-th ot-th--nonsortable bk-th-check';
        var saBox = document.createElement('input');
        saBox.type = 'checkbox';
        saBox.id = 'fb-select-all';
        saBox.title = 'Select / deselect all visible';
        saBox.addEventListener('change', function () {
            fbPageRows().forEach(function (r) {
                if (fbGroupByCol) {
                    (r.rows || []).forEach(function (gr) {
                        var k = rowKey(gr);
                        if (saBox.checked) fbCheckedRows.add(k);
                        else fbCheckedRows.delete(k);
                    });
                } else {
                    var k = rowKey(r);
                    if (saBox.checked) fbCheckedRows.add(k);
                    else fbCheckedRows.delete(k);
                }
            });
            updateSelectionState();
            fbRenderPage();
        });
        thCheck.appendChild(saBox);
        hr.appendChild(thCheck);
        var tfCheck = document.createElement('th');
        tfCheck.className = 'ot-filter-cell bk-th-check';
        fr.appendChild(tfCheck);

        var visibleCols = fbGroupByCol
            ? [{ key: 'group_value', label: fbGroupByCol.replace(/_/g, ' '), sortable: true, filterable: false },
               { key: 'file_count',  label: 'Files',                         sortable: true, filterable: false }]
            : FB_COLUMNS;

        visibleCols.forEach(function (col) {
            var th = document.createElement('th');
            if (col.sortable !== false) th.className = 'ot-th ot-th--sortable';
            else th.className = 'ot-th';
            if (fbSortCol === col.key) th.classList.add(fbSortDir > 0 ? 'ot-th--asc' : 'ot-th--desc');
            th.textContent = col.label;
            if (col.sortable !== false) {
                th.addEventListener('click', function () {
                    if (fbSortCol === col.key) fbSortDir = -fbSortDir;
                    else { fbSortCol = col.key; fbSortDir = 1; }
                    fbApplyFilterSort();
                });
            }
            hr.appendChild(th);

            var tf = document.createElement('th');
            if (col.filterable !== false && !fbGroupByCol) {
                var fbUniqueVals = fbAllRows.length
                    ? Array.from(new Set(fbAllRows.map(function (r) {
                        return r[col.key] == null ? '' : String(r[col.key]);
                    }))).sort()
                    : [];
                if (fbAllRows.length > 0 && fbUniqueVals.length <= 20
                    && shouldUseDropdownFilter(col.key)) {
                    var sel = document.createElement('select');
                    sel.className = 'ot-filter-select';
                    sel.dataset.col = col.key;
                    var optAll = document.createElement('option');
                    optAll.value = ''; optAll.textContent = '— all —';
                    sel.appendChild(optAll);
                    fbUniqueVals.forEach(function (v) {
                        var opt = document.createElement('option');
                        opt.value = v.toLowerCase();
                        opt.textContent = v === '' ? '(blank)' : v;
                        if ((fbColFilters[col.key] || '') === v.toLowerCase()) opt.selected = true;
                        sel.appendChild(opt);
                    });
                    sel.addEventListener('change', function () {
                        fbColFilters[col.key] = sel.value;
                        fbCurrentPage = 1;
                        fbApplyFilterSort();
                    });
                    tf.appendChild(sel);
                } else {
                    var inp = document.createElement('input');
                    inp.type = 'text';
                    inp.className = 'ot-filter-input';
                    inp.placeholder = 'Filter\u2026';
                    inp.dataset.col = col.key;
                    inp.value = fbColFilters[col.key] || '';
                    inp.addEventListener('input', function () {
                        fbColFilters[col.key] = inp.value.trim().toLowerCase();
                        fbCurrentPage = 1;
                        fbApplyFilterSort();
                    });
                    tf.appendChild(inp);
                }
            }
            fr.appendChild(tf);
        });
    }

    /* -----------------------------------------------------------------------
       Render rows
    ----------------------------------------------------------------------- */
    function fbRenderPage() {
        var tbody = el('fb-tbody');
        if (!tbody) return;
        var rows = fbPageRows();
        if (!rows.length) {
            tbody.innerHTML = '<tr><td colspan="20" class="ot-empty">No files found.</td></tr>';
            return;
        }
        var frag = document.createDocumentFragment();
        rows.forEach(function (r, idx) {
            if (fbGroupByCol) {
                fbRenderGroupRow(frag, r, idx);
            } else {
                fbRenderFlatRow(frag, r, idx);
            }
        });
        tbody.innerHTML = '';
        tbody.appendChild(frag);
    }

    function fbRenderFlatRow(frag, r, idx) {
        var tr = document.createElement('tr');
        tr.className = 'bk-row ' + (idx % 2 === 0 ? 'bk-row--odd' : 'bk-row--even');
        var td0 = document.createElement('td');
        td0.className = 'bk-cell-check';
        var cb = document.createElement('input');
        cb.type = 'checkbox';
        var k = rowKey(r);
        cb.checked = fbCheckedRows.has(k);
        cb.addEventListener('change', function () {
            if (cb.checked) fbCheckedRows.add(k);
            else fbCheckedRows.delete(k);
            updateSelectionState();
        });
        td0.appendChild(cb);
        tr.appendChild(td0);

        FB_COLUMNS.forEach(function (col) {
            var td = document.createElement('td');
            var v = r[col.key];
            if (col.key === 'FILENAME' && isPlotableOutput(r.KW_OUTPUT || '')) {
                var link = document.createElement('a');
                link.href = '#';
                link.className = 'fb-fn-plot-link';
                link.textContent = valOrDash(v);
                link.title = 'Click to view plot';
                link.addEventListener('click', function (e) {
                    e.preventDefault();
                    openFilenamePlot(r);
                });
                td.appendChild(link);
            } else if (col.key === 'MID_OBS_TIME') {
                td.textContent = formatDate(v);
            } else if (col.key === 'PASSED_ALL_QC') {
                td.textContent = v == null ? '--' : (parseInt(v) === 1 ? '\u2713' : '\u2717');
                td.className = parseInt(v) === 1 ? 'bk-qc-pass' : 'bk-qc-fail';
            } else {
                td.textContent = valOrDash(v);
            }
            tr.appendChild(td);
        });
        frag.appendChild(tr);
    }

    function fbRenderGroupRow(frag, grp, idx) {
        var tr = document.createElement('tr');
        tr.className = 'bk-group-row ' + (idx % 2 === 0 ? 'bk-row--odd' : 'bk-row--even');
        var td0 = document.createElement('td');
        td0.className = 'bk-cell-check';
        var cb = document.createElement('input');
        cb.type = 'checkbox';
        var allChecked = grp.rows.every(function (gr) { return fbCheckedRows.has(rowKey(gr)); });
        cb.checked = allChecked;
        cb.title = 'Select all files in this group';
        cb.addEventListener('change', function () {
            grp.rows.forEach(function (gr) {
                var k = rowKey(gr);
                if (cb.checked) fbCheckedRows.add(k);
                else fbCheckedRows.delete(k);
            });
            updateSelectionState();
        });
        td0.appendChild(cb);
        tr.appendChild(td0);

        var tdVal = document.createElement('td');
        tdVal.textContent = valOrDash(grp.group_value);
        tdVal.className = 'bk-group-val';
        tr.appendChild(tdVal);

        var tdCount = document.createElement('td');
        tdCount.textContent = grp.file_count;
        tr.appendChild(tdCount);

        // "Add group to basket" button
        var tdBtn = document.createElement('td');
        var addBtn = document.createElement('button');
        addBtn.className = 'ari-btn ari-btn--sm ari-btn--primary fb-add-btn';
        addBtn.title = 'Add all files in this group to basket';
        addBtn.innerHTML = '<i class="fa-solid fa-basket-shopping"></i>';
        addBtn.addEventListener('click', function () {
            addRowsToBasket(grp.rows);
        });
        tdBtn.appendChild(addBtn);
        tr.appendChild(tdBtn);

        frag.appendChild(tr);
    }

    /* -----------------------------------------------------------------------
       Selection state
    ----------------------------------------------------------------------- */
    function updateSelectionState() {
        var count = fbCheckedRows.size;
        var addBtn = el('fb-btn-add-to-basket');
        if (addBtn) {
            addBtn.disabled = count === 0;
            addBtn.textContent = count > 0 ? 'Add to basket (' + count + ')' : 'Add to basket';
        }
    }

    /* -----------------------------------------------------------------------
       Add to basket
    ----------------------------------------------------------------------- */
    function addRowsToBasket(rows) {
        if (!rows || !rows.length) return;
        var entries = rows.map(function (r) {
            return {
                profile_id:  pageCfg.profileId || '',
                instrument:  pageCfg.instrument || '',
                objname:     pageCfg.objname || '',
                block_kind:  r.BLOCK_KIND  || '',
                obs_dir:     r.OBS_DIR     || '',
                filename:    r.FILENAME    || '',
                kw_output:   r.KW_OUTPUT   || '',
                kw_run_id:   r.KW_RUN_ID   || '',
                kw_dprtype:  r.KW_DPRTYPE  || '',
                kw_fiber:    r.KW_FIBER    || '',
                kw_pi_name:  r.KW_PI_NAME  || '',
                mid_obs_time:r.MID_OBS_TIME || '',
                passed_all_qc: r.PASSED_ALL_QC,
                identifier:  r.IDENTIFIER || '',
            };
        });

        fetch(basketCfg.addApiUrl || '/api/data-portal/basket/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ entries: entries }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    updateBasketCounter(data.basket_count || 0);
                    fbCheckedRows.clear();
                    updateSelectionState();
                    fbRenderPage();
                    var msg = data.added + ' file(s) added to basket'
                        + (data.skipped ? ' (' + data.skipped + ' already in basket)' : '') + '.';
                    showFbToast(msg);
                } else {
                    alert('Failed to add to basket: ' + (data.error || 'unknown'));
                }
            })
            .catch(function (err) { alert('Request failed: ' + String(err)); });
    }

    function addSelectedToBasket() {
        var toAdd;
        if (fbGroupByCol) {
            toAdd = [];
            fbFilteredRows.forEach(function (grp) {
                grp.rows.forEach(function (r) {
                    if (fbCheckedRows.has(rowKey(r))) toAdd.push(r);
                });
            });
        } else {
            toAdd = fbAllRows.filter(function (r) { return fbCheckedRows.has(rowKey(r)); });
        }
        addRowsToBasket(toAdd);
    }

    function addAllVisibleToBasket() {
        var toAdd;
        if (fbGroupByCol) {
            toAdd = [];
            fbFilteredRows.forEach(function (grp) {
                grp.rows.forEach(function (r) { toAdd.push(r); });
            });
        } else {
            toAdd = fbFilteredRows.slice();
        }
        if (!toAdd.length) return;
        if (!confirm('Add ' + toAdd.length + ' file(s) to basket?')) return;
        addRowsToBasket(toAdd);
    }

    /* -----------------------------------------------------------------------
       Basket counter badge (shown in tab bar)
    ----------------------------------------------------------------------- */
    function updateBasketCounter(count) {
        var badge = el('op-basket-count');
        if (badge) badge.textContent = count > 0 ? String(count) : '';
    }

    /* -----------------------------------------------------------------------
       Toast notification
    ----------------------------------------------------------------------- */
    function showFbToast(msg) {
        var toast = document.createElement('div');
        toast.className = 'fb-toast';
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(function () { toast.classList.add('fb-toast--show'); }, 10);
        setTimeout(function () {
            toast.classList.remove('fb-toast--show');
            setTimeout(function () { document.body.removeChild(toast); }, 400);
        }, 3000);
    }

    /* -----------------------------------------------------------------------
       Wire up add-from-time-series helper (called by object_page.js)
    ----------------------------------------------------------------------- */
    window.ARI_FB_ADD_FROM_FTABLE = function (obsDir, fkind) {
        if (!pageCfg.profileId || !pageCfg.objname) return;
        var url = '/api/data-portal/basket/add-from-ftable'
            + '?profile_id=' + encodeURIComponent(pageCfg.profileId)
            + '&objname='    + encodeURIComponent(pageCfg.objname)
            + '&obs_dir='    + encodeURIComponent(obsDir || '')
            + '&fkind='      + encodeURIComponent(fkind || 'ext');
        fetch(url, { method: 'POST',
                     headers: { 'Content-Type': 'application/json' },
                     body: JSON.stringify({}) })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    updateBasketCounter(data.basket_count || 0);
                    showFbToast(data.added + ' file(s) added to basket.');
                }
            })
            .catch(function () {});
    };

    /* -----------------------------------------------------------------------
       Bind preset buttons
    ----------------------------------------------------------------------- */
    function bindPresets() {
        document.querySelectorAll('.fb-preset-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var selectedPreset = btn.dataset.preset || 'default';
                if (selectedPreset === fbActivePreset) {
                    fbActivePreset = 'none';
                } else {
                    fbActivePreset = selectedPreset;
                }
                syncPresetButtons();
                loadFbData(fbActivePreset);
            });
        });
        syncPresetButtons();
    }

    /* -----------------------------------------------------------------------
       Bind group-by, pagination, clear-filters, add-to-basket
    ----------------------------------------------------------------------- */
    function bindControls() {
        var gbSel = el('fb-groupby');
        if (gbSel) {
            gbSel.addEventListener('change', function () {
                fbGroupByCol = gbSel.value;
                fbSortCol = null;
                fbCurrentPage = 1;
                fbCheckedRows.clear();
                updateSelectionState();
                fbApplyFilterSort();
            });
        }

        var clearF = el('fb-btn-clear-filters');
        if (clearF) {
            clearF.addEventListener('click', function () {
                fbColFilters = {};
                document.querySelectorAll('#fb-filter-row .ot-filter-input').forEach(function (inp) {
                    inp.value = '';
                });
                fbCurrentPage = 1;
                fbApplyFilterSort();
            });
        }

        var addBtn = el('fb-btn-add-to-basket');
        if (addBtn) addBtn.addEventListener('click', addSelectedToBasket);

        var addAllBtn = el('fb-btn-add-all-visible');
        if (addAllBtn) addAllBtn.addEventListener('click', addAllVisibleToBasket);

        var clearSel = el('fb-btn-clear-selection');
        if (clearSel) {
            clearSel.addEventListener('click', function () {
                fbCheckedRows.clear();
                updateSelectionState();
                fbRenderPage();
            });
        }

        var pp = el('fb-perpage');
        if (pp) {
            pp.addEventListener('change', function () {
                fbPerPage = parseInt(pp.value) || 0;
                fbCurrentPage = 1;
                fbApplyFilterSort();
            });
        }

        var pi = el('fb-page-input');
        if (pi) {
            pi.addEventListener('change', function () {
                var v = parseInt(pi.value) || 1;
                fbCurrentPage = Math.max(1, Math.min(v, fbTotalPages()));
                fbRenderPage();
                fbUpdatePagination();
            });
        }

        var bf = el('fb-btn-first');
        var bp = el('fb-btn-prev');
        var bn = el('fb-btn-next');
        var bl = el('fb-btn-last');
        if (bf) bf.addEventListener('click', function () { fbCurrentPage = 1; fbRenderPage(); fbUpdatePagination(); });
        if (bp) bp.addEventListener('click', function () { fbCurrentPage = Math.max(1, fbCurrentPage - 1); fbRenderPage(); fbUpdatePagination(); });
        if (bn) bn.addEventListener('click', function () { fbCurrentPage = Math.min(fbTotalPages(), fbCurrentPage + 1); fbRenderPage(); fbUpdatePagination(); });
        if (bl) bl.addEventListener('click', function () { fbCurrentPage = fbTotalPages(); fbRenderPage(); fbUpdatePagination(); });
    }

    /* -----------------------------------------------------------------------
       Tab activation hook – load data on first view
    ----------------------------------------------------------------------- */
    document.addEventListener('ARI_TAB_ACTIVATED', function (e) {
        if (!e.detail || !e.detail.tabKey) return;
        if ((e.detail.tabKey === 'file_browser' || e.detail.tabKey === 'all')
                && !fbLoaded) {
            loadFbData();
        }
    });

    /* -----------------------------------------------------------------------
       Init (bind controls; actual data loads when tab is first visited)
    ----------------------------------------------------------------------- */
    bindPresets();
    /* -----------------------------------------------------------------------
       Filename-click plot modal
    ----------------------------------------------------------------------- */
    function openFilenamePlot(r) {
        var modal     = document.getElementById('fn-plot-modal');
        var titleEl   = document.getElementById('fn-plot-title');
        var divEl     = document.getElementById('fn-plot-div');
        var loadingEl = document.getElementById('fn-plot-loading');
        var errorEl   = document.getElementById('fn-plot-error');
        if (!modal) return;

        // Reset state
        if (divEl)     { divEl.innerHTML = ''; }
        if (errorEl)   { errorEl.textContent = ''; errorEl.style.display = 'none'; }
        if (loadingEl) { loadingEl.style.display = ''; }
        if (titleEl)   { titleEl.textContent = r.FILENAME || ''; }
        modal.style.display = 'flex';

        var url = '/api/data-portal/filename-plot'
            + '?profile_id=' + encodeURIComponent(pageCfg.profileId || '')
            + '&block_kind=' + encodeURIComponent(r.BLOCK_KIND || '')
            + '&obs_dir='    + encodeURIComponent(r.OBS_DIR    || '')
            + '&filename='   + encodeURIComponent(r.FILENAME   || '')
            + '&kw_output='  + encodeURIComponent(r.KW_OUTPUT  || '')
            + '&kw_fiber='   + encodeURIComponent(r.KW_FIBER   || 'AB')
            + '&kw_run_id='  + encodeURIComponent(r.KW_RUN_ID  || '');

        fetch(url)
            .then(function (resp) { return resp.json(); })
            .then(function (data) {
                if (loadingEl) { loadingEl.style.display = 'none'; }
                if (!data.success || !data.has_plot) {
                    if (errorEl) {
                        errorEl.textContent = data.message || data.error || 'No plot available.';
                        errorEl.style.display = '';
                    }
                    return;
                }
                if (titleEl && data.title) { titleEl.textContent = data.title; }
                if (!divEl) return;
                // Inject the Bokeh components() HTML (div + script).
                // Using components avoids the embed_item reference error
                // that can occur in long-running server processes.
                divEl.innerHTML = data.div || '';
                if (data.script) {
                    var tmp = document.createElement('div');
                    tmp.innerHTML = data.script;
                    var scriptSrc = tmp.querySelector('script');
                    if (scriptSrc) {
                        var s = document.createElement('script');
                        s.type = scriptSrc.type || 'text/javascript';
                        s.textContent = scriptSrc.textContent;
                        divEl.appendChild(s);
                    }
                }
                setTimeout(function () {
                    window.dispatchEvent(new Event('resize'));
                }, 150);
            })
            .catch(function (err) {
                if (loadingEl) { loadingEl.style.display = 'none'; }
                if (errorEl) {
                    errorEl.textContent = 'Request failed: ' + String(err);
                    errorEl.style.display = '';
                }
            });
    }

    bindControls();

    // Also populate group-by dropdown options
    var gbSel = el('fb-groupby');
    if (gbSel) {
        FB_GROUP_OPTIONS.forEach(function (col) {
            var opt = document.createElement('option');
            opt.value = col;
            opt.textContent = col.replace(/_/g, ' ');
            gbSel.appendChild(opt);
        });
    }

}());
