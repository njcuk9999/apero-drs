/* ==========================================================================
   Object page logic - tabbed sections with API-backed content
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_OBJECT_PAGE || {};

    var tabsWrap = document.getElementById('op-tabs');
    var loadingEl = document.getElementById('op-loading');
    var errorEl = document.getElementById('op-error');
    var updatedEl = document.getElementById('op-last-updated');

    var targetGrid = document.getElementById('op-target-grid');
    var spectrumGrid = document.getElementById('op-spectrum-grid');
    var lblGrid = document.getElementById('op-lbl-grid');
    var ccfGrid = document.getElementById('op-ccf-grid');
    var tsBody = document.getElementById('op-time-series-tbody');
    var debugMessageEl = document.getElementById('op-debug-message');
    var targetCsvBtn = document.getElementById('op-download-target-csv');
    var spectrumCsvBtn = document.getElementById('op-download-spectrum-csv');
    var lblCsvBtn = document.getElementById('op-download-lbl-csv');
    var ccfCsvBtn = document.getElementById('op-download-ccf-csv');
    var tsCsvBtn = document.getElementById('op-download-time-series-csv');
    var debugCsvBtn = document.getElementById('op-download-debug-csv');

    var apiPayload = null;

    function escHtml(str) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(str)));
        return d.innerHTML;
    }

    function formatDate(iso) {
        if (!iso) return 'Unknown';
        try {
            return new Date(iso).toLocaleString();
        } catch (e) {
            return String(iso);
        }
    }

    function showError(msg) {
        loadingEl.style.display = 'none';
        errorEl.style.display = '';
        errorEl.textContent = msg || 'Failed to load object page data.';
    }

    function activateTab(tabKey) {
        document.querySelectorAll('#op-tabs .ari-sg-tab').forEach(function (btn) {
            btn.classList.toggle('ari-sg-tab--active', btn.dataset.tab === tabKey);
        });
        document.querySelectorAll('.op-tab-panel').forEach(function (panel) {
            panel.style.display = (panel.id === 'op-tab-' + tabKey) ? '' : 'none';
        });
    }

    function bindTabs() {
        if (!tabsWrap) return;
        tabsWrap.querySelectorAll('.ari-sg-tab').forEach(function (btn) {
            btn.addEventListener('click', function () {
                activateTab(btn.dataset.tab);
            });
        });
    }

    function parseList(value) {
        var raw = String(value === null || value === undefined ? '' : value);
        if (!raw || raw.indexOf('[PLACEHOLDER]') !== -1) {
            return [];
        }
        return raw
            .split(/[|,]/)
            .map(function (s) { return s.trim(); })
            .filter(function (s) { return s.length > 0; });
    }

    function renderFilterableList(value, placeholderText) {
        var entries = parseList(value);
        if (!entries.length) {
            return '<div class="op-kv-value op-kv-value--placeholder">'
                + escHtml(placeholderText || '[PLACEHOLDER]') + '</div>';
        }

        var inputId = 'op-filter-' + Math.random().toString(36).slice(2);
        var listId = 'op-list-' + Math.random().toString(36).slice(2);

        var html = '';
        html += '<input class="op-list-filter" id="' + inputId + '" type="text" '
            + 'placeholder="Filter values..." data-target="' + listId + '">';
        html += '<div class="op-list-values" id="' + listId + '">';
        entries.forEach(function (entry) {
            html += '<span class="op-list-chip" data-value="' + escHtml(entry.toLowerCase()) + '">'
                + escHtml(entry) + '</span>';
        });
        html += '</div>';
        return html;
    }

    function bindListFilters(container) {
        if (!container) return;
        container.querySelectorAll('.op-list-filter').forEach(function (input) {
            input.addEventListener('input', function () {
                var targetId = input.getAttribute('data-target');
                var target = document.getElementById(targetId);
                if (!target) return;
                var q = String(input.value || '').trim().toLowerCase();
                target.querySelectorAll('.op-list-chip').forEach(function (chip) {
                    var v = chip.getAttribute('data-value') || '';
                    chip.style.display = (!q || v.indexOf(q) !== -1) ? '' : 'none';
                });
            });
        });
    }

    function renderKvGrid(container, rows) {
        if (!container) return;
        container.innerHTML = '';

        rows.forEach(function (row) {
            var label = row.label || row[0];
            var value = row.value || row[1];
            var filterable = !!row.filterable;

            var item = document.createElement('div');
            item.className = 'op-kv-item';
            if (String(label) === 'Aliases') {
                item.classList.add('op-kv-item--aliases');
            }

            var lbl = document.createElement('div');
            lbl.className = 'op-kv-label';
            lbl.textContent = label;

            var val = document.createElement('div');
            val.className = 'op-kv-value';
            if (String(value).length > 180) {
                val.classList.add('op-kv-value--long');
            }
            if (filterable) {
                val.classList.add('op-kv-value--no-scroll');
                val.innerHTML = renderFilterableList(value, '[PLACEHOLDER]');
            } else {
                val.innerHTML = escHtml(value);
            }

            if (!filterable && String(value).indexOf('[PLACEHOLDER]') !== -1) {
                val.classList.add('op-kv-value--placeholder');
            }

            item.appendChild(lbl);
            item.appendChild(val);
            container.appendChild(item);
        });

        bindListFilters(container);
    }

    function renderTarget(target) {
        var rows = [
            ['Target Name', target.object_name || '[PLACEHOLDER]'],
            ['RA', String(target.ra_deg || '[PLACEHOLDER]') + ' [deg] (' + String(target.ra_source || '[PLACEHOLDER]') + ')'],
            ['Dec', String(target.dec_deg || '[PLACEHOLDER]') + ' [deg] (' + String(target.dec_source || '[PLACEHOLDER]') + ')'],
            ['Finder chart', target.finder_chart || '[PLACEHOLDER]'],
            ['Teff', String(target.teff_k || '[PLACEHOLDER]') + ' [K] (' + String(target.teff_source || '[PLACEHOLDER]') + ')'],
            ['Spectral Type', String(target.spectral_type || '[PLACEHOLDER]') + ' (' + String(target.spectral_type_source || '[PLACEHOLDER]') + ')'],
            ['Proper Motion (RA)', String(target.pmra || '[PLACEHOLDER]') + ' [mas/yr]'],
            ['Proper Motion (Dec)', String(target.pmdec || '[PLACEHOLDER]') + ' [mas/yr]'],
            ['Parallax', String(target.parallax || '[PLACEHOLDER]') + ' [mas]'],
            ['Radial Velocity', String(target.radial_velocity || '[PLACEHOLDER]') + ' [km/s] (' + String(target.radial_velocity_source || '[PLACEHOLDER]') + ')'],
            { label: 'Aliases', value: target.aliases || '[PLACEHOLDER]', filterable: true },
            { label: 'OBJECT name(s) in headers', value: target.object_names_in_headers || '[PLACEHOLDER]', filterable: true },
            { label: 'OB Name(s) in headers', value: target.ob_names_in_headers || '[PLACEHOLDER]', filterable: true },
            { label: 'PI name(s) in headers', value: target.pi_names_in_headers || '[PLACEHOLDER]', filterable: true },
            { label: 'Project/Run name(s) in headers', value: target.project_run_names_in_headers || '[PLACEHOLDER]', filterable: true }
        ];

        renderKvGrid(targetGrid, rows);
    }

    function renderSpectrum(spec) {
        var rows = [
            ['DPRTYPES', spec.dprtypes || '[PLACEHOLDER]'],
            ['Total number raw files', spec.raw_total || '[PLACEHOLDER]'],
            ['Number of rejected files', spec.raw_rejected || '[PLACEHOLDER]'],
            ['First raw files', spec.raw_first_mid || '[PLACEHOLDER]'],
            ['Last raw files', spec.raw_last_mid || '[PLACEHOLDER]'],
            ['Total number PP files', spec.pp_total || '[PLACEHOLDER]'],
            ['Number PP files passed QC', spec.pp_passed || '[PLACEHOLDER]'],
            ['Number PP files failed QC', spec.pp_failed || '[PLACEHOLDER]'],
            ['First pp file [Mid exposure]', spec.pp_first_mid || '[PLACEHOLDER]'],
            ['Last pp file [Mid exposure]', spec.pp_last_mid || '[PLACEHOLDER]'],
            ['Last processed [pp]', spec.pp_last_processed || '[PLACEHOLDER]'],
            ['Version [pp]', spec.pp_version || '[PLACEHOLDER]'],
            ['Total number ext files', spec.ext_total || '[PLACEHOLDER]'],
            ['Number ext files passed QC', spec.ext_passed || '[PLACEHOLDER]'],
            ['Number ext files failed QC', spec.ext_failed || '[PLACEHOLDER]'],
            ['First ext file [Mid exposure]', spec.ext_first_mid || '[PLACEHOLDER]'],
            ['Last ext file [Mid exposure]', spec.ext_last_mid || '[PLACEHOLDER]'],
            ['Last processed [ext]', spec.ext_last_processed || '[PLACEHOLDER]'],
            ['Version [ext]', spec.ext_version || '[PLACEHOLDER]'],
            ['Total number tcorr files', spec.tcorr_total || '[PLACEHOLDER]'],
            ['Number tcorr files passed QC', spec.tcorr_passed || '[PLACEHOLDER]'],
            ['Number tcorr files failed QC', spec.tcorr_failed || '[PLACEHOLDER]'],
            ['First tcorr file [Mid exposure]', spec.tcorr_first_mid || '[PLACEHOLDER]'],
            ['Last tcorr file [Mid exposure]', spec.tcorr_last_mid || '[PLACEHOLDER]'],
            ['Last processed [tcorr]', spec.tcorr_last_processed || '[PLACEHOLDER]'],
            ['Version [tcorr]', spec.tcorr_version || '[PLACEHOLDER]'],
            ['Median SNR Y', spec.median_snr_y || '[PLACEHOLDER]'],
            ['Median SNR H', spec.median_snr_h || '[PLACEHOLDER]']
        ];
        renderKvGrid(spectrumGrid, rows);
    }

    function renderLbl(lbl) {
        var rows = [
            ['RV Uncertainty lbl.rdb (25, 50, 75 percentile)', lbl.rv_uncertainty_percentiles || '[PLACEHOLDER]'],
            ['RV Absolute Deviation lbl.rdb (25, 50, 75 percentile)', lbl.rv_abs_dev_percentiles || '[PLACEHOLDER]'],
            ['Number of lbl.rdb Measurements', lbl.measurement_count || '[PLACEHOLDER]'],
            ['Number of lbl.rdb Spurious Low Points', lbl.spurious_low_points || '[PLACEHOLDER]'],
            ['Number of lbl.rdb Spurious High Points', lbl.spurious_high_points || '[PLACEHOLDER]'],
            ['Number of Nights', lbl.n_nights || '[PLACEHOLDER]'],
            ['Number of Reset RV Points', lbl.n_reset_rv_points || '[PLACEHOLDER]'],
            ['Systemic Velocity', lbl.systemic_velocity || '[PLACEHOLDER]'],
            ['Velocity Domain considered valid', lbl.valid_velocity_domain || '[PLACEHOLDER]'],
            ['LBL Version', lbl.lbl_version || '[PLACEHOLDER]']
        ];
        renderKvGrid(lblGrid, rows);
    }

    function renderCcf(ccf) {
        var rows = [
            ['Mask used', ccf.mask_used || '[PLACEHOLDER]'],
            ['CCF systemic velocity', ccf.systemic_velocity || '[PLACEHOLDER]'],
            ['CCF FWHM', ccf.fwhm || '[PLACEHOLDER]'],
            ['Number of CCF files Total', ccf.total_files || '[PLACEHOLDER]'],
            ['Number of CCF passed QC', ccf.passed_qc || '[PLACEHOLDER]'],
            ['Number CCF files failed QC', ccf.failed_qc || '[PLACEHOLDER]'],
            ['First ccf file [Mid exposure]', ccf.first_mid || '[PLACEHOLDER]'],
            ['Last ccf file [Mid exposure]', ccf.last_mid || '[PLACEHOLDER]'],
            ['Last processed [ccf]', ccf.last_processed || '[PLACEHOLDER]'],
            ['Version [ccf]', ccf.ccf_version || '[PLACEHOLDER]']
        ];
        renderKvGrid(ccfGrid, rows);
    }

    function renderTimeSeries(rows) {
        if (!tsBody) return;
        tsBody.innerHTML = '';

        if (!rows || rows.length === 0) {
            tsBody.innerHTML = '<tr><td colspan="12" class="ot-empty">No rows</td></tr>';
            return;
        }

        var frag = document.createDocumentFragment();
        rows.forEach(function (r) {
            var tr = document.createElement('tr');
            tr.className = 'op-ts-row';
            var cols = [
                r.obs_dir,
                r.first_obs_mid,
                r.last_obs_mid,
                r.num_ext,
                r.num_tcorr,
                r.seeing,
                r.airmass,
                r.mean_exptime,
                r.total_exptime,
                r.snr_order_15,
                r.snr_order_60,
                r.dprtypes
            ];
            cols.forEach(function (c) {
                var td = document.createElement('td');
                var isMissing = (c === null || c === undefined || c === '');
                var v = isMissing ? '\u2014' : String(c);
                if (/^\d+\s*\(\d+\)/.test(v)) {
                    td.className = 'op-ts-count';
                }
                td.textContent = v;
                tr.appendChild(td);
            });
            frag.appendChild(tr);
        });
        tsBody.appendChild(frag);
    }

    function csvEscape(cell) {
        var s = String(cell === null || cell === undefined ? '' : cell);
        return '"' + s.replace(/"/g, '""') + '"';
    }

    function downloadCsv(filename, rows) {
        var csv = rows.map(function (row) {
            return row.map(csvEscape).join(',');
        }).join('\n');
        var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function sectionObjectToRows(obj) {
        var rows = [['field', 'value']];
        Object.keys(obj || {}).forEach(function (k) {
            rows.push([k, obj[k]]);
        });
        return rows;
    }

    function downloadTargetCsv() {
        if (!apiPayload || !apiPayload.sections || !apiPayload.sections.target_info) {
            return;
        }

        var t = apiPayload.sections.target_info;
        downloadCsv(
            'target_info_' + String(cfg.objname || 'object') + '.csv',
            sectionObjectToRows(t)
        );
    }

    function downloadSpectrumCsv() {
        if (!apiPayload || !apiPayload.sections || !apiPayload.sections.spectrum) return;
        downloadCsv(
            'spectrum_' + String(cfg.objname || 'object') + '.csv',
            sectionObjectToRows(apiPayload.sections.spectrum)
        );
    }

    function downloadLblCsv() {
        if (!apiPayload || !apiPayload.sections || !apiPayload.sections.lbl) return;
        downloadCsv(
            'lbl_' + String(cfg.objname || 'object') + '.csv',
            sectionObjectToRows(apiPayload.sections.lbl)
        );
    }

    function downloadCcfCsv() {
        if (!apiPayload || !apiPayload.sections || !apiPayload.sections.ccf) return;
        downloadCsv(
            'ccf_' + String(cfg.objname || 'object') + '.csv',
            sectionObjectToRows(apiPayload.sections.ccf)
        );
    }

    function downloadTimeSeriesCsv() {
        var ts = (apiPayload && apiPayload.sections && apiPayload.sections.time_series)
            ? apiPayload.sections.time_series : [];
        if (!ts.length) {
            downloadCsv('time_series_' + String(cfg.objname || 'object') + '.csv', [['message', 'No rows']]);
            return;
        }
        var headers = Object.keys(ts[0]);
        var rows = [headers];
        ts.forEach(function (row) {
            rows.push(headers.map(function (h) { return row[h]; }));
        });
        downloadCsv('time_series_' + String(cfg.objname || 'object') + '.csv', rows);
    }

    function downloadDebugCsv() {
        var dbg = (apiPayload && apiPayload.sections && apiPayload.sections.debug)
            ? apiPayload.sections.debug : { message: 'Coming soon' };
        downloadCsv(
            'debug_' + String(cfg.objname || 'object') + '.csv',
            sectionObjectToRows(dbg)
        );
    }

    function loadData() {
        var url = cfg.apiUrl
            + '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname);

        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    showError(data.error || 'Failed to load object data');
                    return;
                }

                apiPayload = data;
                loadingEl.style.display = 'none';
                errorEl.style.display = 'none';

                updatedEl.innerHTML = '<i class="fa-solid fa-clock"></i> Last updated: '
                    + escHtml(formatDate(data.generated_at));

                var s = data.sections || {};
                renderTarget(s.target_info || {});
                renderSpectrum(s.spectrum || {});
                renderLbl(s.lbl || {});
                renderCcf(s.ccf || {});
                renderTimeSeries(s.time_series || []);
                debugMessageEl.textContent = (s.debug && s.debug.message) ? s.debug.message : 'Coming soon';
            })
            .catch(function (err) {
                showError('Network error: ' + String(err));
            });
    }

    function init() {
        bindTabs();
        activateTab('target_info');
        if (targetCsvBtn) {
            targetCsvBtn.addEventListener('click', downloadTargetCsv);
        }
        if (spectrumCsvBtn) {
            spectrumCsvBtn.addEventListener('click', downloadSpectrumCsv);
        }
        if (lblCsvBtn) {
            lblCsvBtn.addEventListener('click', downloadLblCsv);
        }
        if (ccfCsvBtn) {
            ccfCsvBtn.addEventListener('click', downloadCcfCsv);
        }
        if (tsCsvBtn) {
            tsCsvBtn.addEventListener('click', downloadTimeSeriesCsv);
        }
        if (debugCsvBtn) {
            debugCsvBtn.addEventListener('click', downloadDebugCsv);
        }
        loadData();
    }

    init();
})();
