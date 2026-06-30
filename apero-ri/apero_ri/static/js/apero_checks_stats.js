/**
 * apero_checks_stats.js
 *
 * Stats page for APERO checks – obs-dir and per-check histograms.
 * Fetches data from the /api/monitor/apero-checks/<profile_id>/stats
 * endpoint (URL passed via the script tag's data-api-url attribute).
 *
 * Depends on Chart.js 4.x loaded in the page head.
 */
(function () {
    'use strict';

    // -----------------------------------------------------------------------
    // State
    // -----------------------------------------------------------------------
    const state = {
        // Raw API payload
        data: null,
        // Current bin mode per tab
        obsdirBin: 'month',
        checksBin: 'month',
        // Visible series per tab (default: only failed)
        obsdirSeries: new Set(['failed']),
        checksSeries: new Set(['failed']),
        // Selected check key for the checks histogram
        selectedCheck: '',
        // Sort state for per-check summary table
        checksSortKey: 'check_key',
        checksSortDir: 'asc',
        // Chart.js instances
        obsdirChart: null,
        checksChart: null,
    };

    // -----------------------------------------------------------------------
    // Chart colours
    // -----------------------------------------------------------------------
    const SERIES_COLORS = {
        passed: { bg: 'rgba(34,197,94,0.55)', border: '#16a34a' },
        failed: { bg: 'rgba(239,68,68,0.55)', border: '#dc2626' },
        overridden: { bg: 'rgba(245,158,11,0.55)', border: '#d97706' },
        monitored: { bg: 'rgba(124,58,237,0.55)', border: '#7c3aed' },
    };
    const SERIES_ORDER = ['passed', 'failed', 'overridden', 'monitored'];

    // -----------------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------------

    /** Build Chart.js datasets from a list of histogram rows. */
    function buildDatasets(histRows, visibleSeries) {
        const labels = histRows.map((r) => r.bin);
        const datasets = [];
        for (const key of SERIES_ORDER) {
            if (!visibleSeries.has(key)) continue;
            const col = SERIES_COLORS[key];
            datasets.push({
                label: key.charAt(0).toUpperCase() + key.slice(1),
                data: histRows.map((r) => r[key] || 0),
                backgroundColor: col.bg,
                borderColor: col.border,
                borderWidth: 1,
                borderRadius: 3,
            });
        }
        return { labels, datasets };
    }

    /** Create or update a Chart.js bar chart on a canvas element. */
    function upsertChart(existingChart, canvasId, histRows, visibleSeries) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return existingChart;

        const { labels, datasets } = buildDatasets(histRows, visibleSeries);

        if (typeof Chart === 'undefined') {
            // Chart.js failed to load; show a plain text fallback.
            canvas.style.display = 'none';
            let msg = canvas.parentElement
                .querySelector('.acs-chart-fallback');
            if (!msg) {
                msg = document.createElement('p');
                msg.className = 'acs-chart-fallback';
                msg.style.cssText = (
                    'color:var(--ari-text-muted);font-size:0.88rem;'
                    + 'padding:0.5rem 0;'
                );
                canvas.parentElement.appendChild(msg);
            }
            msg.textContent = (
                'Chart.js could not be loaded. '
                + 'Histogram unavailable.'
            );
            return existingChart;
        }

        if (existingChart) {
            existingChart.data.labels = labels;
            existingChart.data.datasets = datasets;
            existingChart.update();
            return existingChart;
        }

        return new Chart(canvas, {
            type: 'bar',
            data: { labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { mode: 'index', intersect: false },
                },
                scales: {
                    x: { stacked: false },
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                    },
                },
            },
        });
    }

    // -----------------------------------------------------------------------
    // UI population
    // -----------------------------------------------------------------------

    function populateObsdirSummary(obsdirData) {
        const counts = obsdirData.counts || {};
        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val != null ? String(val) : '–';
        };
        set('acs-od-total', counts.total);
        set('acs-od-passed', counts.passed);
        set('acs-od-failed', counts.failed);
        set('acs-od-overridden', counts.overridden);
        set('acs-od-monitored', counts.monitored);
    }

    function renderObsdirChart() {
        if (!state.data) return;
        const rows = state.data.obsdir.histogram || [];
        state.obsdirChart = upsertChart(
            state.obsdirChart,
            'acs-obsdir-chart',
            rows,
            state.obsdirSeries,
        );
    }

    function populateChecksTable(checksData) {
        const tbody = document.getElementById('acs-checks-table-body');
        if (!tbody) return;
        const checkKeys = checksData.check_keys || [];
        const checks = checksData.checks || {};
        if (checkKeys.length === 0) {
            tbody.innerHTML =
                '<tr><td colspan="6" style="color:var(--ari-text-muted)">'
                + 'No checks found.</td></tr>';
            return;
        }

        const tableRows = checkKeys.map((key) => {
            const c = checks[key] || {};
            return {
                check_key: key,
                name: c.name || key,
                passed: Number(c.passed || 0),
                failed: Number(c.failed || 0),
                overridden: Number(c.overridden || 0),
                monitored: Number(c.monitored || 0),
            };
        });

        const sortKey = state.checksSortKey || 'check_key';
        const sortDir = state.checksSortDir === 'desc' ? -1 : 1;
        tableRows.sort((left, right) => {
            const a = left[sortKey];
            const b = right[sortKey];
            const aNum = typeof a === 'number' ? a : Number.NaN;
            const bNum = typeof b === 'number' ? b : Number.NaN;
            let cmp = 0;
            if (!Number.isNaN(aNum) && !Number.isNaN(bNum)) {
                cmp = aNum === bNum ? 0 : (aNum < bNum ? -1 : 1);
            } else {
                const aStr = String(a || '').toLowerCase();
                const bStr = String(b || '').toLowerCase();
                cmp = aStr.localeCompare(bStr);
            }
            if (cmp === 0) {
                cmp = String(left.check_key)
                    .toLowerCase()
                    .localeCompare(String(right.check_key).toLowerCase());
            }
            return sortDir * cmp;
        });

        const rows = [];
        for (const row of tableRows) {
            rows.push(
                '<tr>'
                + `<td data-col="check_key"><code>${_esc(row.check_key)}</code></td>`
                + `<td data-col="name">${_esc(row.name)}</td>`
                + `<td data-col="passed" style="color:#16a34a;font-weight:600">${row.passed}</td>`
                + `<td data-col="failed" style="color:#dc2626;font-weight:600">${row.failed}</td>`
                + `<td data-col="overridden" style="color:#d97706;font-weight:600">${row.overridden}</td>`
                + `<td data-col="monitored" style="color:#7c3aed;font-weight:600">${row.monitored}</td>`
                + '</tr>',
            );
        }
        tbody.innerHTML = rows.join('');
        updateChecksTableSortUi();
    }

    function updateChecksTableSortUi() {
        document.querySelectorAll('.acs-check-table__sort').forEach((btn) => {
            const sortKey = btn.dataset.sortKey;
            const icon = btn.querySelector('.acs-check-table__sort-icon');
            const active = sortKey === state.checksSortKey;
            const dir = active ? state.checksSortDir : 'none';
            btn.dataset.sortDir = dir;
            btn.setAttribute(
                'aria-sort',
                dir === 'asc' ? 'ascending'
                    : (dir === 'desc' ? 'descending' : 'none'),
            );
            if (!icon) return;
            icon.className = 'fa-solid acs-check-table__sort-icon '
                + (dir === 'asc' ? 'fa-caret-up'
                    : (dir === 'desc' ? 'fa-caret-down' : 'fa-sort'));
        });
    }

    function populateCheckDropdown(checksData) {
        const sel = document.getElementById('acs-check-select');
        if (!sel) return;
        const checkKeys = checksData.check_keys || [];
        const checks = checksData.checks || {};
        // Remove all options beyond the placeholder
        while (sel.options.length > 1) sel.remove(1);
        for (const key of checkKeys) {
            const name = (checks[key] || {}).name || key;
            const opt = document.createElement('option');
            opt.value = key;
            opt.textContent = `${key} – ${name}`;
            sel.appendChild(opt);
        }
        // Auto-select first check if available
        if (checkKeys.length > 0 && !state.selectedCheck) {
            state.selectedCheck = checkKeys[0];
            sel.value = checkKeys[0];
        } else if (state.selectedCheck) {
            sel.value = state.selectedCheck;
        }
    }

    function renderChecksChart() {
        if (!state.data) return;
        const key = state.selectedCheck;
        const histMap = state.data.checks.histogram_by_check || {};
        const rows = key ? (histMap[key] || []) : [];
        state.checksChart = upsertChart(
            state.checksChart,
            'acs-checks-chart',
            rows,
            state.checksSeries,
        );
    }

    /** Simple HTML escape for inserting values into innerHTML. */
    function _esc(str) {
        return String(str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    // -----------------------------------------------------------------------
    // Data fetching
    // -----------------------------------------------------------------------

    function _deriveApiBaseFromPath() {
        const path = String(window.location.pathname || '');
        const m = path.match(
            /^\/monitor_portal\/apero_checks\/([^/]+)\/stats\/?$/,
        );
        if (!m) return '';
        const profileId = m[1];
        return `/api/monitor/apero-checks/${profileId}/stats`;
    }

    function buildApiUrl(binBy) {
        const scriptEl = document.querySelector('script[data-api-url]');
        let base = scriptEl ? scriptEl.getAttribute('data-api-url') : '';
        base = String(base || '').trim();
        if (!base) {
            base = _deriveApiBaseFromPath();
        }
        return `${base}?bin_by=${encodeURIComponent(binBy)}`;
    }

    function showLoading(visible) {
        const el = document.getElementById('acs-loading-indicator');
        if (el) el.style.display = visible ? '' : 'none';

        // Extra in-tab indicator so users can see loading in obs-dir panel.
        const obsdirEl = document.getElementById('acs-obsdir-loading');
        if (obsdirEl) obsdirEl.style.display = visible ? '' : 'none';
    }

    function showError(msg) {
        const loading = document.getElementById('acs-loading-indicator');
        const obsdirLoading = document.getElementById('acs-obsdir-loading');
        const errEl = document.getElementById('acs-error-indicator');
        if (loading) loading.style.display = 'none';
        if (obsdirLoading) obsdirLoading.style.display = 'none';
        if (errEl) {
            errEl.style.display = msg ? '' : 'none';
            errEl.textContent = msg || '';
        }
    }

    function fetchStats(binBy) {
        showLoading(true);
        showError('');
        const url = buildApiUrl(binBy);
        if (!url || url.startsWith('?bin_by=')) {
            showError('Failed to build stats API URL for this page.');
            return;
        }
        fetch(url, { credentials: 'same-origin' })
            .then((resp) => {
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                return resp.json();
            })
            .then((payload) => {
                if (!payload.success) {
                    throw new Error(payload.error || 'API error');
                }
                state.data = payload;
                showLoading(false);
                populateObsdirSummary(payload.obsdir);
                try { renderObsdirChart(); } catch (_e) { /* Chart.js absent */ }
                populateChecksTable(payload.checks);
                populateCheckDropdown(payload.checks);
                try { renderChecksChart(); } catch (_e) { /* Chart.js absent */ }
            })
            .catch((err) => {
                showError(
                    `Failed to load stats: ${err.message} (URL: ${url})`,
                );
            });
    }

    // -----------------------------------------------------------------------
    // Event wiring
    // -----------------------------------------------------------------------

    function wireTabs() {
        document.querySelectorAll('.acs-tab-btn').forEach((btn) => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.acs-tab-btn')
                    .forEach((b) => b.classList.remove('active'));
                document.querySelectorAll('.acs-tab-panel')
                    .forEach((p) => p.classList.remove('active'));
                btn.classList.add('active');
                const panelId = `acs-panel-${btn.dataset.tab}`;
                const panel = document.getElementById(panelId);
                if (panel) panel.classList.add('active');
                // Resize charts when tab becomes visible
                if (btn.dataset.tab === 'obsdir' && state.obsdirChart) {
                    state.obsdirChart.resize();
                }
                if (btn.dataset.tab === 'checks' && state.checksChart) {
                    state.checksChart.resize();
                }
            });
        });
    }

    function wireBinButtons() {
        document.querySelectorAll('.acs-bin-group').forEach((group) => {
            const target = group.dataset.target; // 'obsdir' or 'checks'
            group.querySelectorAll('.acs-bin-btn').forEach((btn) => {
                btn.addEventListener('click', () => {
                    group.querySelectorAll('.acs-bin-btn')
                        .forEach((b) => b.classList.remove('active'));
                    btn.classList.add('active');
                    const binBy = btn.dataset.bin;
                    if (target === 'obsdir') {
                        state.obsdirBin = binBy;
                    } else {
                        state.checksBin = binBy;
                    }
                    // Re-fetch with the new bin; use whichever bin applies
                    // to the currently-focused tab, or just re-fetch both.
                    // Since the API takes a single bin_by, use the active
                    // tab's preference as the fetch parameter.
                    const activeBin = target === 'obsdir'
                        ? state.obsdirBin
                        : state.checksBin;
                    fetchStats(activeBin);
                });
            });
        });
    }

    function wireToggleButtons() {
        document.querySelectorAll('.acs-toggle-group').forEach((group) => {
            const target = group.dataset.target;
            group.querySelectorAll('.acs-toggle-btn').forEach((btn) => {
                btn.addEventListener('click', () => {
                    btn.classList.toggle('active');
                    const series = btn.dataset.series;
                    const set = target === 'obsdir'
                        ? state.obsdirSeries
                        : state.checksSeries;
                    if (set.has(series)) {
                        set.delete(series);
                    } else {
                        set.add(series);
                    }
                    if (target === 'obsdir') {
                        renderObsdirChart();
                    } else {
                        renderChecksChart();
                    }
                });
            });
        });
    }

    function wireCheckDropdown() {
        const sel = document.getElementById('acs-check-select');
        if (!sel) return;
        sel.addEventListener('change', () => {
            state.selectedCheck = sel.value;
            renderChecksChart();
        });
    }

    function wireChecksTableSort() {
        document.querySelectorAll('.acs-check-table__sort').forEach((btn) => {
            btn.addEventListener('click', () => {
                const nextKey = btn.dataset.sortKey || 'check_key';
                if (state.checksSortKey === nextKey) {
                    state.checksSortDir =
                        state.checksSortDir === 'asc' ? 'desc' : 'asc';
                } else {
                    state.checksSortKey = nextKey;
                    state.checksSortDir = (
                        nextKey === 'check_key' || nextKey === 'name'
                    ) ? 'asc' : 'desc';
                }
                if (state.data && state.data.checks) {
                    populateChecksTable(state.data.checks);
                }
            });
        });
        updateChecksTableSortUi();
    }

    // -----------------------------------------------------------------------
    // Boot
    // -----------------------------------------------------------------------

    function init() {
        wireTabs();
        wireBinButtons();
        wireToggleButtons();
        wireCheckDropdown();
        wireChecksTableSort();
        // Initial fetch using default bin mode (month)
        fetchStats('month');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
