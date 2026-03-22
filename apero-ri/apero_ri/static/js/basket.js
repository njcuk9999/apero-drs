/* ==========================================================================
   Download Basket page – sortable, filterable, downloadable file table
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_BASKET || {};

    /* -----------------------------------------------------------------------
       State
    ----------------------------------------------------------------------- */
    var allRows      = [];
    var filteredRows = [];
    var columns      = [];
    var colFilters   = {};
    var sortCol      = null;
    var sortDir      = 1;
    var checkedIds   = new Set();
    var currentPage  = 1;
    var perPage      = 50;
    var groupByCol   = '';
    var pollTimer    = null;
    var activeJobId  = null;

    /* -----------------------------------------------------------------------
       Columns shown for flat basket view
    ----------------------------------------------------------------------- */
    var BASKET_COLUMNS = [
        { key: 'objname',      label: 'Object',       sortable: true,  filterable: true },
        { key: 'obs_dir',      label: 'Obs Dir',      sortable: true,  filterable: true },
        { key: 'filename',     label: 'Filename',     sortable: true,  filterable: true },
        { key: 'block_kind',   label: 'Block Kind',   sortable: true,  filterable: true },
        { key: 'kw_output',    label: 'Output Type',  sortable: true,  filterable: true },
        { key: 'kw_dprtype',   label: 'DPRTYPE',      sortable: true,  filterable: true },
        { key: 'kw_fiber',     label: 'Fiber',        sortable: true,  filterable: true },
        { key: 'kw_pi_name',   label: 'PI Name',      sortable: true,  filterable: true },
        { key: 'mid_obs_time', label: 'Mid Obs Time', sortable: true,  filterable: true },
        { key: 'passed_all_qc',label: 'QC Passed',    sortable: true,  filterable: true },
        { key: 'kw_run_id',    label: 'Run ID',       sortable: true,  filterable: true },
        { key: 'added_at',     label: 'Added',        sortable: true,  filterable: false },
    ];

    var GROUP_OPTIONS = [
        'objname', 'obs_dir', 'block_kind', 'kw_output',
        'kw_dprtype', 'kw_fiber', 'kw_pi_name', 'kw_run_id',
    ];

    /* -----------------------------------------------------------------------
       DOM refs
    ----------------------------------------------------------------------- */
    var totalCountEl       = document.getElementById('bk-total-count');
    var totalSizeEl        = document.getElementById('bk-total-size');
    var missingWarnEl      = document.getElementById('bk-missing-warn');
    var missingCountEl     = document.getElementById('bk-missing-count');
    var btnRemoveSelected  = document.getElementById('bk-btn-remove-selected');
    var btnClearAll        = document.getElementById('bk-btn-clear-all');
    var groupbySelect      = document.getElementById('bk-groupby');
    var btnClearFilters    = document.getElementById('bk-btn-clear-filters');
    var perpageSelect      = document.getElementById('bk-perpage');

    /* row-index offset for current page (for row number column) */
    var pageRowOffset = 0;
    var headerRow          = document.getElementById('bk-header-row');
    var filterRow          = document.getElementById('bk-filter-row');
    var tbody              = document.getElementById('bk-tbody');
    var pageInfo           = document.getElementById('bk-page-info');
    var pageInput          = document.getElementById('bk-page-input');
    var pageTotal          = document.getElementById('bk-page-total');
    var btnFirst           = document.getElementById('bk-btn-first');
    var btnPrev            = document.getElementById('bk-btn-prev');
    var btnNext            = document.getElementById('bk-btn-next');
    var btnLast            = document.getElementById('bk-btn-last');
    var dlSizeNote         = document.getElementById('bk-dl-size-note');
    var emailRow           = document.getElementById('bk-email-row');
    var btnCompile         = document.getElementById('bk-btn-compile');
    var btnRefreshJobs     = document.getElementById('bk-btn-refresh-jobs');
    var btnClearJobs       = document.getElementById('bk-btn-clear-jobs');
    var jobsUsageEl        = document.getElementById('bk-jobs-usage');
    var jobsList           = document.getElementById('bk-jobs-list');
    var overlay            = document.getElementById('bk-compile-overlay');
    var overlayMsg         = document.getElementById('bk-overlay-msg');
    var overlayHint        = document.getElementById('bk-overlay-hint');
    var overlayDismiss     = document.getElementById('bk-overlay-dismiss');
    var downloadsOverQuota = false;
    var downloadUsageBytes = 0;
    var downloadLimitBytes = 0;

    /* -----------------------------------------------------------------------
       Helpers
    ----------------------------------------------------------------------- */
    function escHtml(str) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(str == null ? '' : str)));
        return d.innerHTML;
    }

    function formatBytes(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        var units = ['B', 'KB', 'MB', 'GB', 'TB'];
        var i = Math.floor(Math.log2(bytes) / 10);
        i = Math.min(i, units.length - 1);
        return (bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0) + ' ' + units[i];
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

    function shouldUseDropdownFilter(colKey) {
        var cname = String(colKey || '').toLowerCase();
        if (/(date|time|timestamp|night|mjd|jd|unix|obs_time)/.test(cname)) {
            return false;
        }

        var nonBlank = allRows.map(function (r) {
            return r[colKey];
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
            return parseDateLike(v) !== null;
        });
        if (allDateLike) {
            return false;
        }

        return true;
    }

    function valOrDash(v) {
        if (v === null || v === undefined) return '--';
        var s = String(v).trim();
        return s === '' ? '--' : s;
    }

    /* -----------------------------------------------------------------------
       Load basket data
    ----------------------------------------------------------------------- */
    function loadBasket() {
        var url = cfg.basketApiUrl
            + '?profile_id=' + encodeURIComponent(cfg.profileId || '');
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) { return; }
                allRows = data.entries || [];
                buildGroupByOptions();
                applyFilterSort();
                updateSummaryBar(data.summary);
                updateCompileBtn();
                loadJobs();
            })
            .catch(function () {});
    }

    function updateSummaryBar(summary) {
        if (!summary) return;
        if (totalCountEl) totalCountEl.textContent = summary.accessible_files || 0;
        if (totalSizeEl)  totalSizeEl.textContent  = formatBytes(summary.total_size_bytes || 0);
        var missing = summary.missing_files || 0;
        if (missingWarnEl) missingWarnEl.style.display = missing > 0 ? '' : 'none';
        if (missingCountEl) missingCountEl.textContent = missing;
        // Show email option if > 1GB
        var large = (summary.total_size_bytes || 0) > 1024 * 1024 * 1024;
        if (emailRow) emailRow.style.display = large ? '' : 'none';
        if (dlSizeNote) {
            if (large) {
                dlSizeNote.style.display = '';
                dlSizeNote.textContent = '\u26a0\ufe0f Large download ('
                    + formatBytes(summary.total_size_bytes)
                    + '). Consider using "Compile and email" for files over 1 GB.';
            } else {
                dlSizeNote.style.display = 'none';
            }
        }
    }

    /* -----------------------------------------------------------------------
       Group-by dropdown population
    ----------------------------------------------------------------------- */
    function buildGroupByOptions() {
        if (!groupbySelect) return;
        // keep first "none" option
        while (groupbySelect.options.length > 1) {
            groupbySelect.remove(1);
        }
        GROUP_OPTIONS.forEach(function (col) {
            var col_def = BASKET_COLUMNS.find(function (c) { return c.key === col; });
            var label = col_def ? col_def.label : col;
            var opt = document.createElement('option');
            opt.value = col;
            opt.textContent = label;
            groupbySelect.appendChild(opt);
        });
    }

    /* -----------------------------------------------------------------------
       Render headers (supporting groupBy)
    ----------------------------------------------------------------------- */
    function renderHeaders() {
        if (!headerRow || !filterRow) return;
        headerRow.innerHTML = '';
        filterRow.innerHTML = '';

        // Checkbox select-all header
        var thCheck = document.createElement('th');
        thCheck.className = 'ot-th ot-th--nonsortable bk-th-check';
        var selectAll = document.createElement('input');
        selectAll.type = 'checkbox';
        selectAll.id = 'bk-select-all';
        selectAll.title = 'Select / deselect all visible';
        selectAll.addEventListener('change', function () {
            pageRows().forEach(function (r) {
                var id = r.id || r.group_value;
                if (selectAll.checked) {
                    if (groupByCol) {
                        (r.rows || []).forEach(function (gr) { if (gr.id) checkedIds.add(gr.id); });
                    } else {
                        if (id) checkedIds.add(id);
                    }
                } else {
                    if (groupByCol) {
                        (r.rows || []).forEach(function (gr) { if (gr.id) checkedIds.delete(gr.id); });
                    } else {
                        if (id) checkedIds.delete(id);
                    }
                }
            });
            updateSelectionState();
            renderPage();
        });
        thCheck.appendChild(selectAll);
        headerRow.appendChild(thCheck);
        filterRow.appendChild(document.createElement('th')); // blank filter cell

        // Row-number header (flat view only)
        if (!groupByCol) {
            var thNum = document.createElement('th');
            thNum.className = 'ot-th ot-th--nonsortable bk-th-rownum';
            thNum.textContent = '#';
            headerRow.appendChild(thNum);
            filterRow.appendChild(document.createElement('th'));
        }

        var visibleCols = groupByCol
            ? [{ key: 'group_value', label: groupByCol.replace(/_/g, ' ').toUpperCase() },
               { key: 'file_count', label: 'Files', sortable: true, filterable: false }]
            : BASKET_COLUMNS;

        visibleCols.forEach(function (col) {
            var th = document.createElement('th');
            th.className = 'ot-th';
            if (col.sortable !== false) th.classList.add('ot-th--sortable');
            if (sortCol === col.key) {
                th.classList.add(sortDir > 0 ? 'ot-th--asc' : 'ot-th--desc');
            }
            th.textContent = col.label;
            if (col.sortable !== false) {
                th.addEventListener('click', function () {
                    if (sortCol === col.key) {
                        sortDir = -sortDir;
                    } else {
                        sortCol = col.key;
                        sortDir = 1;
                    }
                    applyFilterSort();
                });
            }
            headerRow.appendChild(th);

            var tf = document.createElement('th');
            if (col.filterable !== false && !groupByCol) {
                var uniqueVals = allRows.length
                    ? Array.from(new Set(allRows.map(function (r) {
                        return r[col.key] == null ? '' : String(r[col.key]);
                    }))).sort()
                    : [];
                if (allRows.length > 0 && uniqueVals.length <= 20
                    && shouldUseDropdownFilter(col.key)) {
                    var sel = document.createElement('select');
                    sel.className = 'ot-filter-select';
                    sel.dataset.col = col.key;
                    var optAll = document.createElement('option');
                    optAll.value = ''; optAll.textContent = '— all —';
                    sel.appendChild(optAll);
                    uniqueVals.forEach(function (v) {
                        var opt = document.createElement('option');
                        opt.value = v.toLowerCase();
                        opt.textContent = v === '' ? '(blank)' : v;
                        if ((colFilters[col.key] || '') === v.toLowerCase()) opt.selected = true;
                        sel.appendChild(opt);
                    });
                    sel.addEventListener('change', function () {
                        colFilters[col.key] = sel.value;
                        currentPage = 1;
                        applyFilterSort();
                    });
                    tf.appendChild(sel);
                } else {
                    var inp = document.createElement('input');
                    inp.type = 'text';
                    inp.className = 'ot-filter-input';
                    inp.placeholder = 'Filter\u2026';
                    inp.dataset.col = col.key;
                    inp.value = colFilters[col.key] || '';
                    inp.addEventListener('input', function () {
                        colFilters[col.key] = inp.value.trim().toLowerCase();
                        currentPage = 1;
                        applyFilterSort();
                    });
                    tf.appendChild(inp);
                }
            }
            filterRow.appendChild(tf);
        });
    }

    /* -----------------------------------------------------------------------
       Filter + sort
    ----------------------------------------------------------------------- */
    function applyFilterSort() {
        var rows = allRows.slice();

        // column filters (flat only)
        if (!groupByCol) {
            Object.keys(colFilters).forEach(function (col) {
                var q = colFilters[col];
                if (!q) return;
                rows = rows.filter(function (r) {
                    return String(r[col] == null ? '' : r[col])
                        .toLowerCase().indexOf(q) !== -1;
                });
            });
        }

        // sort
        if (sortCol) {
            var col = sortCol;
            rows.sort(function (a, b) {
                var av = a[col] == null ? '' : String(a[col]);
                var bv = b[col] == null ? '' : String(b[col]);
                return av < bv ? -sortDir : av > bv ? sortDir : 0;
            });
        }

        // grouping
        if (groupByCol) {
            var groups = {};
            var groupOrder = [];
            rows.forEach(function (r) {
                var key = String(r[groupByCol] == null ? '' : r[groupByCol]);
                if (!groups[key]) {
                    groups[key] = { group_value: key, file_count: 0, rows: [] };
                    groupOrder.push(key);
                }
                groups[key].rows.push(r);
                groups[key].file_count += 1;
            });
            var grouped = groupOrder.map(function (k) { return groups[k]; });
            if (sortCol === 'group_value' || sortCol === 'file_count') {
                var sc = sortCol;
                grouped.sort(function (a, b) {
                    var av = String(a[sc] == null ? '' : a[sc]);
                    var bv = String(b[sc] == null ? '' : b[sc]);
                    return av < bv ? -sortDir : av > bv ? sortDir : 0;
                });
            }
            filteredRows = grouped;
        } else {
            filteredRows = rows;
        }

        updatePagination();
        renderHeaders();
        renderPage();
        updateCompileBtn();
    }

    /* -----------------------------------------------------------------------
       Compile-button state
    ----------------------------------------------------------------------- */
    function updateCompileBtn() {
        if (btnCompile) {
            btnCompile.disabled = allRows.length === 0 || downloadsOverQuota;
            btnCompile.title = downloadsOverQuota
                ? 'Cannot compile while stored downloads exceed 5 GB. Remove old compilations first.'
                : 'Start compilation';
        }
    }

    /* -----------------------------------------------------------------------
       Pagination helpers
    ----------------------------------------------------------------------- */
    function totalPages() {
        if (!perPage) return 1;
        return Math.max(1, Math.ceil(filteredRows.length / perPage));
    }

    function pageRows() {
        if (!perPage) return filteredRows;
        var start = (currentPage - 1) * perPage;
        return filteredRows.slice(start, start + perPage);
    }

    function updatePagination() {
        var tp = totalPages();
        if (currentPage > tp) currentPage = tp;
        pageRowOffset = perPage ? (currentPage - 1) * perPage : 0;
        if (pageInfo) {
            var n = filteredRows.length;
            pageInfo.textContent = n + ' row' + (n !== 1 ? 's' : '');
        }
        if (pageInput) pageInput.value = currentPage;
        if (pageTotal) pageTotal.textContent = tp;
        if (btnFirst) btnFirst.disabled = currentPage <= 1;
        if (btnPrev)  btnPrev.disabled  = currentPage <= 1;
        if (btnNext)  btnNext.disabled  = currentPage >= tp;
        if (btnLast)  btnLast.disabled  = currentPage >= tp;
    }

    /* -----------------------------------------------------------------------
       Render table rows
    ----------------------------------------------------------------------- */
    function renderPage() {
        if (!tbody) return;
        var rows = pageRows();
        if (!rows.length) {
            tbody.innerHTML = '<tr><td colspan="20" class="ot-empty">No files in basket.</td></tr>';
            return;
        }
        var frag = document.createDocumentFragment();

        rows.forEach(function (r, idx) {
            if (groupByCol) {
                renderGroupRow(frag, r, pageRowOffset + idx);
            } else {
                renderFlatRow(frag, r, pageRowOffset + idx);
            }
        });
        tbody.innerHTML = '';
        tbody.appendChild(frag);
    }

    function renderFlatRow(frag, r, rowIdx) {
        var tr = document.createElement('tr');
        tr.className = 'bk-row ' + (rowIdx % 2 === 0 ? 'bk-row--odd' : 'bk-row--even');
        // Checkbox
        var td0 = document.createElement('td');
        td0.className = 'bk-cell-check';
        var cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = checkedIds.has(r.id);
        cb.addEventListener('change', function () {
            if (cb.checked) checkedIds.add(r.id);
            else checkedIds.delete(r.id);
            updateSelectionState();
        });
        td0.appendChild(cb);
        tr.appendChild(td0);
        // Row number
        var tdNum = document.createElement('td');
        tdNum.className = 'bk-cell-rownum';
        tdNum.textContent = rowIdx + 1;
        tr.appendChild(tdNum);
        // Data columns
        BASKET_COLUMNS.forEach(function (col) {
            var td = document.createElement('td');
            var v = r[col.key];
            if (col.key === 'added_at' || col.key === 'mid_obs_time') {
                td.textContent = formatDate(v);
            } else if (col.key === 'passed_all_qc') {
                td.textContent = v == null ? '--' : (parseInt(v) === 1 ? '\u2713' : '\u2717');
                td.className = parseInt(v) === 1 ? 'bk-qc-pass' : 'bk-qc-fail';
            } else {
                td.textContent = valOrDash(v);
            }
            tr.appendChild(td);
        });
        frag.appendChild(tr);
    }

    function renderGroupRow(frag, grp, rowIdx) {
        var tr = document.createElement('tr');
        tr.className = 'bk-group-row ' + (rowIdx % 2 === 0 ? 'bk-row--odd' : 'bk-row--even');
        // checkbox – selects all in group
        var td0 = document.createElement('td');
        var cb = document.createElement('input');
        cb.type = 'checkbox';
        var allChecked = grp.rows.every(function (gr) { return checkedIds.has(gr.id); });
        cb.checked = allChecked;
        cb.title = 'Select / deselect all files in this group';
        cb.addEventListener('change', function () {
            grp.rows.forEach(function (gr) {
                if (cb.checked) checkedIds.add(gr.id);
                else checkedIds.delete(gr.id);
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

        frag.appendChild(tr);
    }

    function updateSelectionState() {
        var count = checkedIds.size;
        if (btnRemoveSelected) btnRemoveSelected.disabled = count === 0;
        if (btnRemoveSelected) {
            btnRemoveSelected.textContent = count > 0
                ? 'Remove selected (' + count + ')'
                : 'Remove selected';
        }
    }

    /* -----------------------------------------------------------------------
       Remove selected
    ----------------------------------------------------------------------- */
    function removeSelected() {
        var ids = Array.from(checkedIds);
        if (!ids.length) return;
        if (!confirm('Remove ' + ids.length + ' item(s) from basket?')) return;
        fetch(cfg.removeApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: ids }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    checkedIds.clear();
                    updateSelectionState();
                    loadBasket();
                }
            })
            .catch(function () {});
    }

    function clearAll() {
        if (!confirm('Remove ALL files from the basket?')) return;
        fetch(cfg.clearApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile_id: cfg.profileId }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    checkedIds.clear();
                    updateSelectionState();
                    loadBasket();
                }
            })
            .catch(function () {});
    }

    /* -----------------------------------------------------------------------
       Compile / download
    ----------------------------------------------------------------------- */
    function getFormat() {
        var radios = document.querySelectorAll('input[name="bk-fmt"]');
        for (var i = 0; i < radios.length; i++) {
            if (radios[i].checked) return radios[i].value;
        }
        return 'zip';
    }

    function getDlMode() {
        var radios = document.querySelectorAll('input[name="bk-dl-mode"]');
        for (var i = 0; i < radios.length; i++) {
            if (radios[i].checked) return radios[i].value;
        }
        return 'now';
    }

    function getChunkSize() {
        var inp = document.getElementById('bk-chunk-size');
        if (!inp || !inp.value) return null;
        var v = parseFloat(inp.value);
        return isNaN(v) || v <= 0 ? null : v;
    }

    function getLowQcRows() {
        return allRows.filter(function (row) {
            var raw = row ? row.passed_all_qc : null;
            var num = Number(raw);
            return !isNaN(num) && num < 1;
        });
    }

    function confirmLowQcDownload() {
        var lowQcRows = getLowQcRows();
        if (!lowQcRows.length) {
            return true;
        }
        var sample = lowQcRows.slice(0, 3).map(function (row) {
            return String(row.filename || row.obs_dir || row.objname || 'unknown file');
        });
        var msg = 'Warning: your basket includes ' + lowQcRows.length
            + ' file(s) with QC < 1.\n\n'
            + 'Examples:\n- ' + sample.join('\n- ') + '\n\n'
            + 'Do you want to continue with this download?';
        return window.confirm(msg);
    }

    function startCompile() {
        if (!allRows.length) {
            alert('Your basket is empty.');
            return;
        }
        // Double-check: ensure we have files before compiling
        var fileCount = allRows.length;
        if (fileCount === 0) {
            alert('Error: No files in basket to compile.');
            return;
        }
        // Confirm file count and low-QC status
        var msg = 'Compile ' + fileCount + ' file(s) for download?';
        if (!window.confirm(msg)) {
            return;
        }
        if (!confirmLowQcDownload()) {
            return;
        }
        if (btnCompile) btnCompile.disabled = true;
        var mode = getDlMode();
        var emailMode = mode === 'email';

        showOverlay('Sending compilation request\u2026', '');

        fetch(cfg.compileApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fmt: getFormat(),
                chunk_size_gb: getChunkSize(),
                email_on_done: emailMode,
                profile_id: cfg.profileId,
            }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    hideOverlay();
                    if (btnCompile) btnCompile.disabled = false;
                    alert('Could not start compilation: ' + (data.error || 'unknown error'));
                    return;
                }
                activeJobId = data.job_id;
                if (emailMode) {
                    hideOverlay();
                    alert('Compilation started. You will receive an email when your download is ready.');
                    loadJobs();
                } else {
                    overlayMsg.textContent = 'Compiling your download\u2026 please wait.';
                    overlayHint.textContent = 'Job ID: ' + data.job_id;
                    startPolling(data.job_id);
                }
            })
            .catch(function (err) {
                hideOverlay();
                if (btnCompile) btnCompile.disabled = false;
                alert('Request failed: ' + String(err));
            });
    }

    function startPolling(jobId) {
        if (pollTimer) clearInterval(pollTimer);
        pollTimer = setInterval(function () { pollJob(jobId); }, 2000);
    }

    function pollJob(jobId) {
        fetch(cfg.statusApiUrl + '/' + encodeURIComponent(jobId))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success || !data.job) return;
                var job = data.job;
                if (job.status === 'running') {
                    overlayMsg.textContent = 'Compiling\u2026 (' + job.accessible_count + ' files)';
                } else if (job.status === 'done') {
                    clearInterval(pollTimer);
                    pollTimer = null;
                    hideOverlay();
                    loadJobs();
                    if (btnCompile) btnCompile.disabled = allRows.length === 0;
                    offerDownload(job);
                } else if (job.status === 'error') {
                    clearInterval(pollTimer);
                    pollTimer = null;
                    hideOverlay();
                    if (btnCompile) btnCompile.disabled = allRows.length === 0;
                    alert('Compilation failed: ' + (job.error || 'unknown'));
                    loadJobs();
                }
            })
            .catch(function () {});
    }

    function offerDownload(job) {
        var chunks = job.chunks || [];
        if (!chunks.length) {
            if (job.no_files) {
                alert('No accessible files were found on disk.\n'
                    + 'Check that PATH_OUT (and other paths) are configured '
                    + 'correctly in the profile settings.');
            } else {
                alert('Compilation complete but no output files were produced.');
            }
            return;
        }
        // Auto-trigger download for each chunk
        chunks.forEach(function (chunk) {
            var a = document.createElement('a');
            a.href = cfg.downloadBaseUrl + '/' + encodeURIComponent(job.job_id)
                + '/' + chunk.index;
            a.download = chunk.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
        // After successful download, offer to clear the basket
        setTimeout(function () {
            if (confirm('Downloads completed. Clear downloaded files from basket?')) {
                clearAll();
            }
        }, 1000);
    }

    /* -----------------------------------------------------------------------
       Overlay helpers
    ----------------------------------------------------------------------- */
    function showOverlay(msg, hint) {
        if (!overlay) return;
        if (overlayMsg) overlayMsg.textContent = msg;
        if (overlayHint) overlayHint.textContent = hint || '';
        if (overlayDismiss) overlayDismiss.style.display = 'none';
        overlay.style.display = '';
    }

    function hideOverlay() {
        if (overlay) overlay.style.display = 'none';
    }

    /* -----------------------------------------------------------------------
       Jobs list
    ----------------------------------------------------------------------- */
    function loadJobs() {
        fetch(cfg.jobsApiUrl + '?profile_id=' + encodeURIComponent(cfg.profileId || ''))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) return;
                downloadsOverQuota = !!data.quota_reached;
                downloadUsageBytes = (data.download_usage && data.download_usage.total_bytes) || 0;
                downloadLimitBytes = data.download_limit_bytes || 0;
                if (dlSizeNote && downloadsOverQuota) {
                    dlSizeNote.style.display = '';
                    dlSizeNote.textContent = '\u26a0\ufe0f Download storage is full ('
                        + formatBytes(downloadUsageBytes) + ' / '
                        + formatBytes(downloadLimitBytes || 0)
                        + '). Remove entries in Recent compilations before creating new downloads.';
                }
                if (jobsUsageEl) {
                    var q = downloadLimitBytes || 0;
                    jobsUsageEl.textContent = 'Storage usage: '
                        + formatBytes(downloadUsageBytes) + ' / '
                        + formatBytes(q)
                        + (downloadsOverQuota ? ' (quota reached)' : '');
                }
                updateCompileBtn();
                renderJobs(data.jobs || []);
            })
            .catch(function () {});
    }

    function removeJob(jobId) {
        if (!jobId) return;
        if (!confirm('Remove this compilation from Recent compilations?')) return;
        fetch(cfg.jobsRemoveApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: jobId }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    alert('Could not remove compilation: ' + (data.error || 'unknown error'));
                    return;
                }
                loadJobs();
            })
            .catch(function (err) {
                alert('Request failed: ' + String(err));
            });
    }

    function clearJobs() {
        if (!confirm('Remove all completed/failed compilations?')) return;
        fetch(cfg.jobsClearApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    alert('Could not clear compilations: ' + (data.error || 'unknown error'));
                    return;
                }
                if (data.skipped) {
                    alert('Removed ' + (data.removed || 0)
                        + ' compilation(s). ' + data.skipped
                        + ' running job(s) were kept.');
                }
                loadJobs();
            })
            .catch(function (err) {
                alert('Request failed: ' + String(err));
            });
    }

    function statusBadge(status) {
        var color = { pending: '#999', running: '#d97706', done: '#16a34a', error: '#dc2626' };
        var icon  = { pending: 'fa-clock', running: 'fa-gear fa-spin', done: 'fa-check', error: 'fa-xmark' };
        var c = color[status] || '#999';
        var i = icon[status] || 'fa-question';
        return '<span style="color:' + c + '"><i class="fa-solid ' + i + '"></i>&nbsp;'
            + escHtml(status) + '</span>';
    }

    function renderJobs(jobs) {
        if (!jobsList) return;
        if (!jobs.length) {
            jobsList.innerHTML = '<p class="at-muted-hint">No recent jobs.</p>';
            return;
        }
        var html = '<table class="bk-jobs-table"><thead><tr>'
            + '<th>Created</th><th>Status</th><th>Files</th>'
            + '<th>Size</th><th>Format</th><th>Downloads</th>'
            + '</tr></thead><tbody>';
        jobs.forEach(function (job) {
            html += '<tr>';
            html += '<td>' + escHtml(formatDate(job.created_at)) + '</td>';
            html += '<td>' + statusBadge(job.status) + '</td>';
            html += '<td>' + escHtml(job.accessible_count || 0) + '</td>';
            html += '<td>' + escHtml(formatBytes(job.total_size_bytes || 0)) + '</td>';
            html += '<td>' + escHtml(job.fmt || '--') + '</td>';
            html += '<td>';
            if (job.status === 'done') {
                (job.chunks || []).forEach(function (chunk) {
                    html += '<a class="ari-btn ari-btn--sm ari-btn--primary bk-dl-link" '
                        + 'href="' + escHtml(cfg.downloadBaseUrl + '/' + job.job_id + '/' + chunk.index) + '" '
                        + 'download="' + escHtml(chunk.filename) + '">'
                        + '<i class="fa-solid fa-download"></i>&nbsp;'
                        + escHtml(chunk.filename)
                        + ' (' + escHtml(formatBytes(chunk.size_bytes)) + ')'
                        + '</a> ';
                });
                html += '<button class="ari-btn ari-btn--sm ari-btn--danger bk-job-remove" '
                    + 'data-job-id="' + escHtml(job.job_id || '') + '" '
                    + 'title="Remove this compilation">'
                    + '<i class="fa-solid fa-trash-can"></i> Remove'
                    + '</button>';
            } else if (job.status === 'error') {
                html += '<button class="ari-btn ari-btn--sm ari-btn--danger bk-job-remove" '
                    + 'data-job-id="' + escHtml(job.job_id || '') + '" '
                    + 'title="Remove this compilation">'
                    + '<i class="fa-solid fa-trash-can"></i> Remove'
                    + '</button>';
            } else {
                html += '--';
            }
            html += '</td>';
            html += '</tr>';
        });
        html += '</tbody></table>';
        jobsList.innerHTML = html;
    }

    /* -----------------------------------------------------------------------
       Event bindings
    ----------------------------------------------------------------------- */
    if (btnRemoveSelected) btnRemoveSelected.addEventListener('click', removeSelected);
    if (btnClearAll)       btnClearAll.addEventListener('click', clearAll);
    if (btnCompile)        btnCompile.addEventListener('click', startCompile);
    if (btnRefreshJobs)    btnRefreshJobs.addEventListener('click', loadJobs);
    if (btnClearJobs)      btnClearJobs.addEventListener('click', clearJobs);
    if (overlayDismiss)    overlayDismiss.addEventListener('click', hideOverlay);
    if (jobsList) {
        jobsList.addEventListener('click', function (ev) {
            var btn = ev.target.closest('.bk-job-remove');
            if (!btn) return;
            removeJob(btn.getAttribute('data-job-id') || '');
        });
    }

    if (groupbySelect) {
        groupbySelect.addEventListener('change', function () {
            groupByCol = groupbySelect.value;
            sortCol = null;
            currentPage = 1;
            checkedIds.clear();
            updateSelectionState();
            applyFilterSort();
        });
    }

    if (btnClearFilters) {
        btnClearFilters.addEventListener('click', function () {
            colFilters = {};
            document.querySelectorAll('#bk-filter-row .ot-filter-input').forEach(function (inp) {
                inp.value = '';
            });
            currentPage = 1;
            applyFilterSort();
        });
    }

    if (perpageSelect) {
        perpageSelect.addEventListener('change', function () {
            perPage = parseInt(perpageSelect.value) || 0;
            currentPage = 1;
            applyFilterSort();
        });
    }

    if (pageInput) {
        pageInput.addEventListener('change', function () {
            var v = parseInt(pageInput.value) || 1;
            currentPage = Math.max(1, Math.min(v, totalPages()));
            renderPage();
            updatePagination();
        });
    }
    if (btnFirst) btnFirst.addEventListener('click', function () { currentPage = 1; renderPage(); updatePagination(); });
    if (btnPrev)  btnPrev.addEventListener('click',  function () { currentPage = Math.max(1, currentPage - 1); renderPage(); updatePagination(); });
    if (btnNext)  btnNext.addEventListener('click',  function () { currentPage = Math.min(totalPages(), currentPage + 1); renderPage(); updatePagination(); });
    if (btnLast)  btnLast.addEventListener('click',  function () { currentPage = totalPages(); renderPage(); updatePagination(); });

    /* -----------------------------------------------------------------------
       Expose basket-update function for other page scripts
    ----------------------------------------------------------------------- */
    window.ARI_BASKET_UPDATE = function () { loadBasket(); };

    /* -----------------------------------------------------------------------
       Init
    ----------------------------------------------------------------------- */
    loadBasket();
}());
