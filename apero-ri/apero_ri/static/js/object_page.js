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

    var spectrumGrid = document.getElementById('op-spectrum-grid');
    var finderChartEl = document.getElementById('op-finder-chart');
    var finderGenerateBtn = document.getElementById('op-finder-generate-btn');
    var finderLoading = document.getElementById('op-finder-loading');
    var finderError = document.getElementById('op-finder-error');
    var finderImages = document.getElementById('op-finder-images');
    var finderLogWrap = document.getElementById('op-finder-log-wrap');
    var finderLogPre = document.getElementById('op-finder-log');
    var finderRegen = document.getElementById('op-finder-regen');
    var tessGenerateBtn = document.getElementById('op-tess-generate-btn');
    var tessLoading = document.getElementById('op-tess-loading');
    var tessError = document.getElementById('op-tess-error');
    var tessViewer = document.getElementById('op-tess-viewer');
    var tessImg = document.getElementById('op-tess-img');
    var tessLabel = document.getElementById('op-tess-label');
    var tessPrev = document.getElementById('op-tess-prev');
    var tessNext = document.getElementById('op-tess-next');
    var tessDlLc = document.getElementById('op-tess-dl-lc');
    var tessDlPng = document.getElementById('op-tess-dl-png');
    var tessRegen = document.getElementById('op-tess-regen');
    var tessDataFiles = document.getElementById('op-tess-data-files');
    var tessLogWrap = document.getElementById('op-tess-log-wrap');
    var tessLogPre = document.getElementById('op-tess-log');
    var lblSections = document.getElementById('op-lbl-sections');
    var ccfGrid = document.getElementById('op-ccf-grid');
    var ccfMjdStartInput = document.getElementById('op-ccf-mjd-start');
    var ccfMjdEndInput = document.getElementById('op-ccf-mjd-end');
    var ccfNobsInput = document.getElementById('op-ccf-nobs');
    var ccfApplyRangeBtn = document.getElementById('op-ccf-apply-range');
    var ccfResetRangeBtn = document.getElementById('op-ccf-reset-range');
    var ccfSamplingNote = document.getElementById('op-ccf-sampling-note');
    var tsBody = document.getElementById('op-time-series-tbody');
    var tsWrap = document.getElementById('op-time-series-wrap');
    var tsTopScroll = document.getElementById('op-time-series-scroll-top');
    var tsTopSizer = document.getElementById('op-time-series-scroll-sizer');
    var allSectionsHost = document.getElementById('op-all-sections');
    var allPinnedReorder = document.getElementById('op-all-pinned-reorder');
    var debugLoading = document.getElementById('op-debug-loading');
    var debugError = document.getElementById('op-debug-error');
    var debugStatusBar = document.getElementById('op-debug-statusbar');
    var targetCsvBtn = document.getElementById('op-download-target-csv');
    var spectrumCsvBtn = document.getElementById('op-download-spectrum-csv');
    var lblCsvBtn = null;  // LBL CSV buttons are created dynamically per flavor
    var ccfCsvBtn = document.getElementById('op-download-ccf-csv');
    var tsCsvBtn = document.getElementById('op-download-time-series-csv');
    var debugCsvBtn = document.getElementById('op-download-debug-csv');
    var tsSnrYHead = document.getElementById('op-ts-head-snr-y');
    var tsSnrHHead = document.getElementById('op-ts-head-snr-h');

    var apiPayload = null;
    var dynamicLabels = {};
    var sectionPinned = [];
    var sectionSearch = {};
    var sectionTitleMap = {};
    var tabOrderMap = {};
    var vsysMs = null;
    var ccfRangeFilter = {
        mjdStart: null,
        mjdEnd: null,
        nobs: 100,
    };

    /* ------------------------------------------------------------------
       Deferred Bokeh embedding  (components-based)
       The server returns {script, div} from Bokeh components().
       When the container is visible we inject immediately; when hidden
       (e.g. inactive tab) we store the payload and inject later so the
       plot gets a proper width on first render.
    ------------------------------------------------------------------ */
    var pendingPlotEmbeds = {};   // { divId: { script, div } }
    var embeddedPlots     = {};   // divId -> true once injected
    var objectPlotsState  = {
        spectrum: 'idle',
        ccf_rv: 'idle',
        ccf_profile: 'idle',
        time_series: 'idle',
        target_info: 'idle',
    };
    var lblPlotsState     = 'idle';   // idle | loading | loaded
    var debugPlotsState   = 'idle';   // idle | loading | loaded
    var backgroundPrefetchStarted = false;
    var plotLastUpdatedByKey = {};
    var plotReloadingByKey = {};
    var yAxisZoomByDiv = {};
    var yAxisRetryByDiv = {};
    // sectionUserState tracks explicit open/close from user interaction:
    // sectionUserState[sid] = true  → user explicitly opened this section
    // sectionUserState[sid] = false → user explicitly closed this section
    // sectionUserState[sid] = undefined → follow default (pinned=open)
    var sectionUserState = {};

    function median(values) {
        if (!values.length) return null;
        var sorted = values.slice().sort(function (a, b) { return a - b; });
        var n = sorted.length;
        var m = Math.floor(n / 2);
        if (n % 2 === 0) {
            return 0.5 * (sorted[m - 1] + sorted[m]);
        }
        return sorted[m];
    }

    function stdDev(values, center) {
        if (!values.length) return 0;
        var c = (center === null || center === undefined) ? 0 : Number(center);
        var sum = 0;
        for (var i = 0; i < values.length; i += 1) {
            var d = Number(values[i]) - c;
            sum += d * d;
        }
        return Math.sqrt(sum / values.length);
    }

    function finiteMinMax(values) {
        var minv = Infinity;
        var maxv = -Infinity;
        var found = false;
        for (var i = 0; i < values.length; i += 1) {
            var v = Number(values[i]);
            if (!isFinite(v)) continue;
            if (v < minv) minv = v;
            if (v > maxv) maxv = v;
            found = true;
        }
        if (!found) return null;
        return { min: minv, max: maxv };
    }

    function sampledFiniteValues(values, maxCount) {
        var out = [];
        if (!values || !values.length) return out;
        var stride = Math.max(1, Math.ceil(values.length / maxCount));
        for (var i = 0; i < values.length; i += stride) {
            var v = Number(values[i]);
            if (isFinite(v)) out.push(v);
        }
        return out;
    }

    function extractFieldName(spec) {
        if (typeof spec === 'string' && spec) return spec;
        if (!spec || typeof spec !== 'object') return '';
        if (typeof spec.field === 'string' && spec.field) return spec.field;
        return '';
    }

    function isArrayLike(v) {
        // Accept plain arrays AND TypedArrays (Float32Array, Float64Array, etc.)
        // which Bokeh 3.x uses internally for ColumnDataSource data.
        return Array.isArray(v)
            || (v != null && typeof v === 'object'
                && typeof v.length === 'number'
                && (ArrayBuffer.isView(v)
                    || Object.prototype.toString.call(v).indexOf('Array') !== -1));
    }

    function collectNumericValues(value, out) {
        if (isArrayLike(value)) {
            for (var i = 0; i < value.length; i += 1) {
                collectNumericValues(value[i], out);
            }
            return;
        }
        var num = Number(value);
        if (isFinite(num)) {
            out.push(num);
        }
    }

    function figureSeries(figModel) {
        var points = [];
        var ys = [];
        var renderers = Array.isArray(figModel.renderers) ? figModel.renderers : [];
        for (var i = 0; i < renderers.length; i += 1) {
            var r = renderers[i];
            if (!r || !r.glyph || !r.data_source || !r.data_source.data) continue;
            var data = r.data_source.data;
            var xField = extractFieldName(r.glyph.x);
            var yFields = [];
            ['y', 'top', 'bottom', 'y0', 'y1'].forEach(function (k) {
                var field = extractFieldName(r.glyph[k]);
                if (field) yFields.push(field);
            });
            if (!xField || !yFields.length) continue;
            var xs = data[xField];
            if (!isArrayLike(xs)) continue;
            for (var f = 0; f < yFields.length; f += 1) {
                var yField = yFields[f];
                var yv = data[yField];
                if (!isArrayLike(yv)) continue;
                var n = Math.min(xs.length, yv.length);
                for (var j = 0; j < n; j += 1) {
                    var before = ys.length;
                    collectNumericValues(yv[j], ys);
                    for (var yy = before; yy < ys.length; yy += 1) {
                        points.push({ x: xs[j], y: ys[yy] });
                    }
                }
            }
        }
        return { points: points, ys: ys };
    }

    function _collectFigureViews(view, out, seen) {
        if (!view || !view.model) return;
        var id = view.model.id;
        if (id && seen[id]) return;
        if (id) seen[id] = true;
        var model = view.model;
        // A Plot model has y_range and renderers
        if (model.y_range && model.renderers != null
                && (Array.isArray(model.renderers)
                    || typeof model.renderers.length === 'number')) {
            out.push(view);
            return; // don't recurse into plot's own children
        }
        // For layout models (column, row, gridplot) walk child_views
        var cv = view.child_views;
        if (cv && typeof cv === 'object') {
            Object.keys(cv).forEach(function (k) {
                _collectFigureViews(cv[k], out, seen);
            });
        }
        // Fallback: walk views map (alternative Bokeh internals)
        var vs = view.views;
        if (vs && typeof vs === 'object' && vs !== cv) {
            Object.keys(vs).forEach(function (k) {
                _collectFigureViews(vs[k], out, seen);
            });
        }
    }

    function getContainerFigures(containerEl) {
        if (!containerEl || !window.Bokeh || !Bokeh.index) return [];
        var views = [];
        var seen = {};
        Object.keys(Bokeh.index).forEach(function (k) {
            var view = Bokeh.index[k];
            if (!view || !view.el) return;
            if (!containerEl.contains(view.el)) return;
            _collectFigureViews(view, views, seen);
        });
        return views;
    }

    // Return the ordered yaxiszoom option list for a given divId.
    // Priority: exact div_id match, then LBL prefix match, then null.
    function _getYAxisZoomOptions(divId) {
        var z = (cfg && cfg.plotYAxisZoom) ? cfg.plotYAxisZoom : null;
        if (!z) return null;
        // Exact match (static plots registered with a div_id)
        if (Object.prototype.hasOwnProperty.call(z, divId)) {
            return z[divId];
        }
        // Prefix match for dynamically created LBL velocity divs
        if (divId.indexOf('op-lbl-vel-plot-') === 0
                && Object.prototype.hasOwnProperty.call(z, 'lbl')) {
            return z['lbl'];
        }
        return null;
    }

    // Convert a single yaxiszoom entry (int or 'full') to
    // {value, label} for a <select> <option>.
    function _yaxisZoomEntry(v) {
        if (String(v) === 'full') return {value: 'full', label: 'full'};
        var n = parseInt(v, 10);
        if (isFinite(n) && n > 0) {
            return {value: n + 'sig', label: n + ' sig'};
        }
        return null;
    }

    // Build the inner HTML for the zoom <select> from a zoom options array.
    // Falls back to the legacy hard-coded set when options is empty/null.
    function _buildZoomSelectHtml(options) {
        var opts = (options && options.length > 0) ? options : [3, 5, 10, 'full'];
        var html = '';
        var first = true;
        for (var _oi = 0; _oi < opts.length; _oi++) {
            var e = _yaxisZoomEntry(opts[_oi]);
            if (!e) continue;
            html += '<option value="' + e.value + '"'
                + (first ? ' selected' : '') + '>'
                + e.label + '</option>';
            first = false;
        }
        return html;
    }

    // True if the plot opted out of the y-axis zoom widget.
    // Historically only the WRAPPER (parentElement) was checked,
    // which silently broke plots that put data-op-nozoom="1"
    // directly on the plot div itself (e.g. the SED and HR
    // diagram on the data-portal object page). When the opt-out
    // is missed, applyYAxisZoom() rewrites y_range.start/end and
    // clobbers the figure's flipped=True state -- which is why
    // the HR y-axis was correct only after a Bokeh reset click.
    function _isNozoom(plotDiv) {
        if (!plotDiv) return false;
        if (plotDiv.getAttribute &&
                plotDiv.getAttribute('data-op-nozoom') === '1') {
            return true;
        }
        var p = plotDiv.parentElement;
        return !!(p && p.getAttribute('data-op-nozoom') === '1');
    }

    function ensureYAxisControl(divId) {
        var plotDiv = document.getElementById(divId);
        if (!plotDiv) return;
        var host = plotDiv.parentElement;
        if (!host) return;
        // Wrapper OR plot div itself with data-op-nozoom="1"
        // opts this plot out entirely.
        if (_isNozoom(plotDiv)) return;
        if (host.querySelector('.op-yzoom-control[data-op-target="' + divId + '"]')) return;

        var bar = document.createElement('div');
        bar.className = 'op-yzoom-control';
        bar.setAttribute('data-op-target', divId);
        bar.innerHTML = ''
            + '<label class="op-yzoom-control__label">'
            + 'y-axis zoom:'
            + '<select class="op-yzoom-control__select">'
            + _buildZoomSelectHtml(_getYAxisZoomOptions(divId))
            + '</select>'
            + '</label>'
            + '<button type="button"'
            + ' class="op-yzoom-control__reset"'
            + ' title="Reset view (resets all sub-plots)">'
            + '\u21ba\u00a0Reset view'
            + '</button>'
            + '<span class="op-yzoom-control__status"'
            + ' aria-live="polite"></span>';
        host.insertBefore(bar, plotDiv);

        var sel = bar.querySelector('.op-yzoom-control__select');
        if (sel) {
            sel.addEventListener('change', function () {
                yAxisZoomByDiv[divId] = sel.value;
                applyYAxisZoom(divId);
            });
        }
        var _rzb = bar.querySelector('.op-yzoom-control__reset');
        if (_rzb) {
            _rzb.addEventListener('click', function () {
                resetPlotView(divId);
            });
        }
    }

    function ensureYAxisResetControl(divId) {
        // Adds a reset-only control bar for data-op-nozoom plots
        // (no zoom dropdown, just a Reset view button).
        var plotDiv = document.getElementById(divId);
        if (!plotDiv) return;
        var host = plotDiv.parentElement;
        if (!host) return;
        if (!_isNozoom(plotDiv)) return;
        var _sel = '.op-yzoom-control[data-op-target="'
            + divId + '"]';
        if (host.querySelector(_sel)) return;
        var bar = document.createElement('div');
        bar.className = 'op-yzoom-control op-yzoom-control--reset-only';
        bar.setAttribute('data-op-target', divId);
        bar.innerHTML = '<button type="button"'
            + ' class="op-yzoom-control__reset"'
            + ' title="Reset view (resets all sub-plots)">'
            + '\u21ba\u00a0Reset view'
            + '</button>';
        host.insertBefore(bar, plotDiv);
        var _rzb = bar.querySelector('.op-yzoom-control__reset');
        if (_rzb) {
            _rzb.addEventListener('click', function () {
                resetPlotView(divId);
            });
        }
    }

    function resetPlotView(divId) {
        // Reset all Bokeh sub-figures in the container to their initial
        // auto-ranges (equivalent to clicking Bokeh's own Reset button).
        // For zoom-enabled plots the selected sigma zoom is re-applied
        // automatically after Bokeh finishes resetting.
        var plotDiv = document.getElementById(divId);
        if (!plotDiv) return;
        var figures = getContainerFigures(plotDiv);
        if (figures.length > 0) {
            // Use the Bokeh view model's reset() method (most reliable).
            figures.forEach(function (view) {
                if (view && typeof view.reset === 'function') {
                    view.reset();
                }
            });
        } else {
            // Fallback: click each Bokeh reset toolbar button in the DOM.
            var _btns = plotDiv.querySelectorAll(
                'button[title="Reset"]'
            );
            for (var _bi = 0; _bi < _btns.length; _bi++) {
                _btns[_bi].click();
            }
        }
        // Re-apply sigma zoom for plots that have a zoom dropdown.
        if (!_isNozoom(plotDiv)) {
            setTimeout(function () { applyYAxisZoom(divId); }, 80);
        }
    }

    function setYAxisStatus(divId, above, below) {
        var statusEl = document.querySelector(
            '.op-yzoom-control[data-op-target="' + divId + '"] .op-yzoom-control__status'
        );
        if (!statusEl) return;
        if ((above + below) <= 0) {
            statusEl.textContent = '';
            return;
        }
        statusEl.textContent = '\u2191 ' + above + ' off-graph  \u2193 ' + below + ' off-graph';
    }

    function applyYAxisZoom(divId) {
        var plotDiv = document.getElementById(divId);
        if (!plotDiv) return false;
        var mode = String(yAxisZoomByDiv[divId] || '3sig');
        var figures = getContainerFigures(plotDiv);
        if (!figures.length) return false;

        var _sigParsed = parseFloat(mode);
        var sigMul = (mode !== 'full' && isFinite(_sigParsed) && _sigParsed > 0)
            ? _sigParsed
            : 3;

        var totalAbove = 0;
        var totalBelow = 0;
        figures.forEach(function (view) {
            var fig = view.model;
            var series = figureSeries(fig);
            var ys = series.ys;
            if (!ys.length) return;
            var mm = finiteMinMax(ys);
            if (!mm) return;
            var yMin = mm.min;
            var yMax = mm.max;
            var lo = yMin;
            var hi = yMax;

            if (mode !== 'full') {
                // Keep y-zoom responsive on large datasets.
                var sample = sampledFiniteValues(ys, 20000);
                if (!sample.length) return;
                var med = median(sample);
                var sig = stdDev(sample, med);
                var half = Math.max(sigMul * sig, 1.0e-12);
                lo = med - half;
                hi = med + half;
            }
            if (!isFinite(lo) || !isFinite(hi)) return;
            if (lo === hi) {
                lo -= 1.0;
                hi += 1.0;
            }

            fig.y_range.start = lo;
            fig.y_range.end = hi;
            if (fig.y_range && fig.y_range.change
                    && typeof fig.y_range.change.emit === 'function') {
                fig.y_range.change.emit();
            }
            if (fig.change && typeof fig.change.emit === 'function') {
                fig.change.emit();
            }
            if (view.request_render && typeof view.request_render === 'function') {
                view.request_render();
            }
            if (view.request_paint && typeof view.request_paint === 'function') {
                view.request_paint();
            }

            if (mode !== 'full') {
                for (var i = 0; i < ys.length; i += 1) {
                    if (ys[i] > hi) totalAbove += 1;
                    else if (ys[i] < lo) totalBelow += 1;
                }
            }
        });

        setYAxisStatus(divId, totalAbove, totalBelow);
        return true;
    }

    function applyYAxisZoomDeferred(divId) {
        // For nozoom plots add a reset-only control bar, then leave
        // Bokeh's own auto-range completely untouched.
        var _pel = document.getElementById(divId);
        if (_isNozoom(_pel)) {
            ensureYAxisResetControl(divId);
            return;
        }
        ensureYAxisControl(divId);
        if (!applyYAxisZoom(divId)) {
            var n = Number(yAxisRetryByDiv[divId] || 0);
            if (n >= 6) return;
            yAxisRetryByDiv[divId] = n + 1;
            setTimeout(function () { applyYAxisZoomDeferred(divId); }, 120);
            return;
        }
        yAxisRetryByDiv[divId] = 0;
    }

    function currentUtcDateLabel() {
        return new Date().toISOString().slice(0, 10);
    }

    function dateLabelFromTimestamp(rawValue) {
        var raw = String(rawValue || '').trim();
        if (!raw) return '';
        var dt = new Date(raw);
        if (Number.isNaN(dt.getTime())) return '';
        return dt.toISOString().slice(0, 10);
    }

    function payloadUpdatedDateLabel(payload) {
        if (!payload || typeof payload !== 'object') return '';
        return (
            dateLabelFromTimestamp(payload.updated_at)
            || dateLabelFromTimestamp(payload._cache_cached_at)
            || dateLabelFromTimestamp(payload.generated_at)
            || ''
        );
    }

    function refreshUpdatedLinkNode(lnk, key) {
        if (!(lnk instanceof Element)) return;
        if (plotReloadingByKey[key]) {
            lnk.textContent = 'Reloading plot...';
            lnk.title = 'Plot reload in progress';
            return;
        }
        lnk.textContent = 'Last updated ' + (plotLastUpdatedByKey[key] || '--');
        lnk.title = 'Reload ' + key + ' plot';
    }

    function setPlotLastUpdated(plotKey, dateLabel) {
        var key = String(plotKey || '').toLowerCase();
        if (!key) return;
        plotLastUpdatedByKey[key] = String(dateLabel || currentUtcDateLabel());
        document.querySelectorAll('.op-plot-updated-link').forEach(function (lnk) {
            if (!(lnk instanceof Element)) return;
            if (String(lnk.getAttribute('data-plot-key') || '').toLowerCase() !== key) return;
            refreshUpdatedLinkNode(lnk, key);
        });
    }

    function setPlotReloading(plotKey, isReloading) {
        var key = String(plotKey || '').toLowerCase();
        if (!key) return;
        plotReloadingByKey[key] = !!isReloading;
        document.querySelectorAll('.op-plot-updated-link').forEach(function (lnk) {
            if (!(lnk instanceof Element)) return;
            if (String(lnk.getAttribute('data-plot-key') || '').toLowerCase() !== key) return;
            refreshUpdatedLinkNode(lnk, key);
        });
    }

    function setGroupLastUpdated(group) {
        var g = String(group || '').toLowerCase();
        var d = currentUtcDateLabel();
        if (g === 'spectrum') {
            ['snr', 'berv', 'spec'].forEach(function (k) { setPlotLastUpdated(k, d); });
            return;
        }
        if (g === 'ccf_rv') {
            setPlotLastUpdated('ccf_rv', d);
            return;
        }
        if (g === 'ccf_profile') {
            setPlotLastUpdated('ccf_profile', d);
            return;
        }
        if (g === 'time_series') {
            ['ts_snr', 'ts_airmass'].forEach(function (k) { setPlotLastUpdated(k, d); });
        }
    }

    function ensurePlotsForTab(tabKey) {
        var key = String(tabKey || '').trim();
        if (key === 'all') {
            loadObjectPlots('target_info');
            loadObjectPlots('spectrum');
            loadObjectPlots('ccf_rv');
            loadObjectPlots('ccf_profile');
            loadObjectPlots('time_series');
            if (lblPlotsState === 'idle') loadLblPlots();
            if (debugPlotsState === 'idle') loadDebugPlots();
            return;
        }
        if (key === 'target_info') {
            loadObjectPlots('target_info');
        }
        if (key === 'spectrum') {
            loadObjectPlots('spectrum');
        }
        if (key === 'ccf') {
            loadObjectPlots('ccf_rv');
            loadObjectPlots('ccf_profile');
        }
        if (key === 'time_series') {
            loadObjectPlots('time_series');
        }
        if (key === 'lbl' && lblPlotsState === 'idle') {
            loadLblPlots();
        }
        if (key === 'debug' && debugPlotsState === 'idle') {
            loadDebugPlots();
        }
    }

    function getPlotKeyFromHref(href) {
        var text = String(href || '').trim();
        if (!text) return '';
        try {
            var url = new URL(text, window.location.origin);
            var parts = url.pathname.split('/').filter(function (p) {
                return String(p || '').trim().length > 0;
            });
            var idx = parts.indexOf('object-plot-max');
            if (idx >= 0 && parts.length > idx + 3) {
                return decodeURIComponent(parts[parts.length - 1]).toLowerCase();
            }
        } catch (err) {
            // Fall back to regex parse for malformed URLs.
        }
        var m = text.match(/\/object-plot-max\/.+\/([^/?#]+)/i);
        return m ? decodeURIComponent(m[1]).toLowerCase() : '';
    }

    function reloadPlotByKey(plotKey) {
        var key = String(plotKey || '').toLowerCase();
        if (!key) return;
        if (key === 'snr' || key === 'berv' || key === 'spec') {
            setPlotReloading(key, true);
            loadObjectPlots('spectrum', true, key);
            return;
        }
        if (key === 'ccf' || key === 'ccf_profile') {
            setPlotReloading('ccf_profile', true);
            loadObjectPlots('ccf_profile', true, 'ccf_profile');
            return;
        }
        if (key === 'ccf_rv') {
            setPlotReloading('ccf_rv', true);
            loadObjectPlots('ccf_rv', true, 'ccf_rv');
            return;
        }
        if (key === 'ts_snr' || key === 'ts_airmass') {
            setPlotReloading(key, true);
            loadObjectPlots('time_series', true, key);
            return;
        }
        if (key === 'sed' || key === 'hr') {
            setPlotReloading(key, true);
            loadObjectPlots('target_info', true, key);
            return;
        }
        if (key === 'lbl') {
            setPlotReloading(key, true);
            loadLblPlots(true, key);
            return;
        }
        if (key.indexOf('debug_') === 0) {
            setPlotReloading(key, true);
            loadDebugPlots(true, key);
        }
    }

    function ensurePlotReloadButtons() {
        document.querySelectorAll('.op-plot-max-btn').forEach(function (maxBtn) {
            if (!(maxBtn instanceof Element)) return;
            if (maxBtn.getAttribute('data-op-max-wired') !== '1') {
                maxBtn.setAttribute('data-op-max-wired', '1');
            }

            var parent = maxBtn.parentElement;
            if (!parent) return;
            if (parent.querySelector('.op-plot-reload-btn')) return;

            var reloadBtn = document.createElement('button');
            reloadBtn.type = 'button';
            reloadBtn.className = 'ari-btn ari-btn--sm ari-btn--secondary op-plot-reload-btn';
            reloadBtn.title = 'Reload plot';
            reloadBtn.style.marginLeft = '0.4rem';
            reloadBtn.innerHTML = '<i class="fa-solid fa-rotate"></i>';
            reloadBtn.addEventListener('click', function (ev) {
                ev.preventDefault();
                ev.stopPropagation();
                reloadPlotByKey(getPlotKeyFromHref(maxBtn.getAttribute('href') || ''));
            });
            parent.insertBefore(reloadBtn, maxBtn);

            if (!parent.querySelector('.op-plot-updated-link')) {
                var key = getPlotKeyFromHref(maxBtn.getAttribute('href') || '');
                var upd = document.createElement('a');
                upd.href = '#';
                upd.className = 'op-plot-updated-link';
                upd.setAttribute('data-plot-key', key);
                upd.style.marginLeft = '0.5rem';
                upd.style.fontSize = '0.78rem';
                upd.style.textDecoration = 'none';
                upd.style.color = 'var(--ari-text-muted, #6b7280)';
                refreshUpdatedLinkNode(upd, key);
                upd.addEventListener('click', function (ev) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    reloadPlotByKey(key);
                });
                parent.insertBefore(upd, reloadBtn);
            }
        });
    }

    function startBackgroundPlotPrefetch() {
        if (backgroundPrefetchStarted) return;
        backgroundPrefetchStarted = true;

        var idleCb = window.requestIdleCallback || function (cb) {
            return window.setTimeout(cb, 1200);
        };

        idleCb(function () {
            loadObjectPlots('spectrum');
            window.setTimeout(function () {
                loadObjectPlots('ccf_rv');
            }, 1200);
            window.setTimeout(function () {
                loadObjectPlots('ccf_profile');
            }, 1200);
            window.setTimeout(function () {
                loadObjectPlots('time_series');
            }, 2600);
        });
    }

    function isElementVisible(el) {
        if (!el) return false;
        var node = el;
        while (node && node !== document.body) {
            if (node.style && node.style.display === 'none') return false;
            node = node.parentElement;
        }
        return true;
    }

    /** Inject Bokeh components() HTML into a container div. */
    function injectPlot(divId, scriptHtml, divHtml) {
        var container = document.getElementById(divId);
        if (!container) return;
        container.innerHTML = divHtml || '';
        if (scriptHtml) {
            var tmp = document.createElement('div');
            tmp.innerHTML = scriptHtml;
            var scriptSrc = tmp.querySelector('script');
            if (scriptSrc) {
                var s = document.createElement('script');
                s.type = scriptSrc.type || 'text/javascript';
                s.textContent = scriptSrc.textContent;
                container.appendChild(s);
            }
        }
        embeddedPlots[divId] = true;
        applyYAxisZoomDeferred(divId);
    }

    function embedOrDefer(divId, payload, noPlotMsg, loadingId) {
        var lid = loadingId || divId.replace(/-div$/, '-loading');
        var loadingEl = document.getElementById(lid);
        var divEl = document.getElementById(divId);
        if (loadingEl) loadingEl.style.display = 'none';

        if (!payload || !payload.has_plot) {
            if (divEl) {
                divEl.innerHTML = '<div class="at-muted-hint">'
                    + escHtml(payload && payload.message ? payload.message : noPlotMsg)
                    + '</div>';
            }
            return;
        }
        if (!payload.script && !payload.div) return;

        if (divEl && isElementVisible(divEl)) {
            injectPlot(divId, payload.script, payload.div);
        } else {
            pendingPlotEmbeds[divId] = { script: payload.script, div: payload.div };
        }
    }

    function flushPendingEmbeds() {
        var ids = Object.keys(pendingPlotEmbeds);
        for (var i = 0; i < ids.length; i++) {
            var divId = ids[i];
            var divEl = document.getElementById(divId);
            if (divEl && isElementVisible(divEl) && !embeddedPlots[divId]) {
                injectPlot(divId, pendingPlotEmbeds[divId].script, pendingPlotEmbeds[divId].div);
                delete pendingPlotEmbeds[divId];
                applyYAxisZoomDeferred(divId);
            }
        }
    }

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

    function getLabel(path, fallback) {
        if (!dynamicLabels || typeof dynamicLabels !== 'object') {
            return fallback;
        }
        var node = dynamicLabels;
        var parts = String(path || '').split('.');
        for (var i = 0; i < parts.length; i += 1) {
            var p = parts[i];
            if (!p || typeof node !== 'object' || !(p in node)) {
                return fallback;
            }
            node = node[p];
        }
        var sval = String(node === null || node === undefined ? '' : node).trim();
        return sval || fallback;
    }

    function valOrDash(value) {
        if (value === null || value === undefined) return '--';
        var s = String(value).trim();
        return s === '' ? '--' : s;
    }

    function showError(msg) {
        loadingEl.style.display = 'none';
        errorEl.style.display = '';
        errorEl.textContent = msg || 'Failed to load object page data.';
        /* Hide tabs and all panels so the page looks clean */
        if (tabsWrap) tabsWrap.style.display = 'none';
        var panels = document.querySelectorAll('.op-tab-panel');
        panels.forEach(function (p) { p.style.display = 'none'; });
        if (updatedEl) updatedEl.style.display = 'none';
    }

    function persistLastObjectPage() {
        var profileId = String(cfg.profileId || '').trim();
        var objname = String(cfg.objname || '').trim();
        if (!profileId || !objname) {
            return;
        }
        var storageKey = 'ari.dp:last-object-page:' + profileId;
        var path = String(window.location.pathname || '').trim();
        var query = String(window.location.search || '');
        var payload = {
            profileId: profileId,
            objname: objname,
            url: path + query,
            updatedAt: new Date().toISOString()
        };
        try {
            localStorage.setItem(storageKey, JSON.stringify(payload));
        } catch (_err) {
            // Ignore storage failures.
        }
    }

    function syncLastOpenedObject() {
        var apiUrl = String(cfg.objectFavouriteApiLastOpened || '').trim();
        var profileId = String(cfg.profileId || '').trim();
        var objname = String(cfg.objname || '').trim();
        if (!apiUrl || !profileId || !objname) {
            return;
        }
        fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                profile_id: profileId,
                objname: objname,
            })
        }).catch(function () {
            // Silent best-effort update.
        });
    }

    function activateTab(tabKey) {
        document.querySelectorAll('#op-tabs .ari-sg-tab').forEach(function (btn) {
            btn.classList.toggle('ari-sg-tab--active', btn.dataset.tab === tabKey);
        });
        if (tabKey === 'all') {
            document.querySelectorAll('.op-tab-panel').forEach(function (panel) {
                var pid = String(panel.id || '');
                if (pid === 'op-tab-all') {
                    panel.style.display = 'none';
                    return;
                }
                panel.style.display = '';
            });
        } else {
            document.querySelectorAll('.op-tab-panel').forEach(function (panel) {
                panel.style.display = (panel.id === 'op-tab-' + tabKey) ? '' : 'none';
            });
        }
        updateSearchUiForTab(tabKey);
        if (debugStatusBar) {
            debugStatusBar.style.display = (tabKey === 'debug') ? '' : 'none';
        }
        applySectionFilter(tabKey);
        // Notify lazy-loading tab modules (e.g. file_browser.js)
        document.dispatchEvent(new CustomEvent('ARI_TAB_ACTIVATED', {detail: {tabKey: tabKey}}));
        ensurePlotsForTab(tabKey);
        // Flush deferred Bokeh embeds for now-visible containers, then
        // fire resize so existing stretch_width plots re-measure.
        setTimeout(function () {
            flushPendingEmbeds();
            window.dispatchEvent(new Event('resize'));
        }, 60);
    }

    function refreshTimeSeriesDualScroll() {
        if (!tsWrap || !tsTopScroll || !tsTopSizer) return;
        var table = document.getElementById('op-time-series-table');
        if (!table) return;
        tsTopSizer.style.width = String(table.scrollWidth) + 'px';
        var needsX = tsWrap.scrollWidth > tsWrap.clientWidth;
        tsTopScroll.style.display = needsX ? '' : 'none';
    }

    function bindTimeSeriesDualScroll() {
        if (!tsWrap || !tsTopScroll || !tsTopSizer) return;
        var syncingTop = false;
        var syncingWrap = false;

        tsTopScroll.addEventListener('scroll', function () {
            if (syncingTop) return;
            syncingWrap = true;
            tsWrap.scrollLeft = tsTopScroll.scrollLeft;
            syncingWrap = false;
        });
        tsWrap.addEventListener('scroll', function () {
            if (syncingWrap) return;
            syncingTop = true;
            tsTopScroll.scrollLeft = tsWrap.scrollLeft;
            syncingTop = false;
        });
        window.addEventListener('resize', function () {
            refreshTimeSeriesDualScroll();
        });
        refreshTimeSeriesDualScroll();
    }

    function updateSearchUiForTab(tabKey) {
        var isAll = (tabKey === 'all');
        document.querySelectorAll('.op-section-search[data-op-search-scope="tab"]').forEach(function (wrap) {
            wrap.style.display = isAll ? 'none' : '';
        });
        var allWrap = ensureAllSearchInput();
        if (allWrap) {
            allWrap.style.display = isAll ? '' : 'none';
        }
    }

    function bindTabs() {
        if (!tabsWrap) return;
        tabsWrap.querySelectorAll('.ari-sg-tab').forEach(function (btn) {
            btn.addEventListener('click', function () {
                activateTab(btn.dataset.tab);
            });
        });
    }

    function sanitizeSectionToken(value) {
        return String(value === null || value === undefined ? '' : value)
            .toLowerCase()
            .replace(/[^a-z0-9_.-]+/g, '_')
            .replace(/^_+|_+$/g, '') || 'section';
    }

    function getPanelLabel(tabKey) {
        var btn = document.querySelector('#op-tabs .ari-sg-tab[data-tab="' + tabKey + '"]');
        if (!btn) return tabKey;
        return String(btn.textContent || tabKey).replace(/\s+/g, ' ').trim();
    }

    function refreshTabOrderMap() {
        tabOrderMap = {};
        var idx = 0;
        document.querySelectorAll('#op-tabs .ari-sg-tab').forEach(function (btn) {
            var key = String(btn.getAttribute('data-tab') || '').trim();
            if (!key || key === 'all') return;
            tabOrderMap[key] = idx;
            idx += 1;
        });
    }

    function tabRank(tabKey) {
        if (Object.prototype.hasOwnProperty.call(tabOrderMap, tabKey)) {
            return tabOrderMap[tabKey];
        }
        return 999999;
    }

    function getSectionTitle(cardEl) {
        if (!cardEl) return '';
        var span = cardEl.querySelector('.at-section-card__header span');
        return String(span ? span.textContent : cardEl.textContent || '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function sectionPinnedRank(sectionId) {
        var i = sectionPinned.indexOf(sectionId);
        return i < 0 ? 999999 : i;
    }

    function isSectionPinned(sectionId) {
        return sectionPinned.indexOf(sectionId) !== -1;
    }

    function setSectionCollapsed(cardEl, collapsed) {
        if (!cardEl) return;
        var body = cardEl.querySelector('.at-section-card__body');
        cardEl.classList.toggle('op-section--collapsed', !!collapsed);
        if (body) {
            body.style.display = collapsed ? 'none' : '';
        }
        var toggleBtn = cardEl.querySelector('.op-section-btn--toggle');
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
            toggleBtn.innerHTML = collapsed
                ? '<i class="fa-solid fa-chevron-down"></i>'
                : '<i class="fa-solid fa-chevron-up"></i>';
            toggleBtn.title = collapsed ? 'Expand section' : 'Collapse section';
        }
        // When expanding a section, flush any deferred Bokeh plots inside it
        if (!collapsed) {
            setTimeout(function () {
                flushPendingEmbeds();
                window.dispatchEvent(new Event('resize'));
            }, 60);
        }
    }

    function updatePinnedButtons() {
        document.querySelectorAll('.op-section-btn--pin').forEach(function (btn) {
            var sid = btn.getAttribute('data-op-pin-id') || '';
            var pinned = isSectionPinned(sid);
            btn.classList.toggle('op-section-btn--active', pinned);
            btn.title = pinned ? 'Unpin section' : 'Pin section to top';
            btn.innerHTML = pinned
                ? '<i class="fa-solid fa-thumbtack"></i>'
                : '<i class="fa-solid fa-thumbtack" style="transform:rotate(45deg);opacity:0.45"></i>';
        });
    }

    function ensureSectionHeaderControls(cardEl, sectionId, isAllClone) {
        if (!cardEl || !sectionId) return;
        var header = cardEl.querySelector('.at-section-card__header');
        if (!header) return;

        var existing = header.querySelector('.op-section-controls');
        if (existing) {
            // Already initialised. Make sure the static maximize
            // anchor and CSV button (which the surrounding code
            // may have re-created in the header during a section
            // re-render) are absorbed into the controls group, but
            // do NOT tear the whole controls group down — that
            // race used to delete the maximize / CSV buttons on
            // every UI refresh.
            var strayCsv = header.querySelector(
                ':scope > button[id^="op-download-"][id$="-csv"], '
                + ':scope > button.op-section-btn--csv');
            if (strayCsv) {
                strayCsv.classList.remove('ari-btn--sm');
                strayCsv.classList.remove('ari-btn--secondary');
                strayCsv.classList.remove('ari-btn');
                strayCsv.classList.add('op-section-btn');
                strayCsv.classList.add('op-section-btn--csv');
                existing.appendChild(strayCsv);
            }
            var strayMax = header.querySelector(
                ':scope > .op-plot-max-btn');
            if (strayMax) {
                strayMax.classList.remove('ari-btn--sm');
                strayMax.classList.remove('ari-btn--secondary');
                strayMax.classList.remove('ari-btn');
                strayMax.classList.add('op-section-btn');
                // Insert max button before pin/toggle so order
                // stays: [max] [pin] [toggle] [csv]
                var pinExisting = existing.querySelector(
                    '.op-section-btn--pin');
                if (pinExisting) {
                    existing.insertBefore(strayMax, pinExisting);
                } else {
                    existing.appendChild(strayMax);
                }
            }
            return;
        }

        var titleSpan = header.querySelector('span');
        if (titleSpan) {
            titleSpan.style.flex = '1 1 auto';
            titleSpan.style.minWidth = '0';
        }

        var controls = document.createElement('div');
        controls.className = 'op-section-controls';
        controls.style.marginLeft = 'auto';

        // Capture CSV button — will be appended last (far right)
        var csvBtn = header.querySelector('button[id^="op-download-"][id$="-csv"], button.op-section-btn--csv');
        if (csvBtn) {
            csvBtn.style.marginLeft = '';
            csvBtn.classList.remove('ari-btn--sm');
            csvBtn.classList.remove('ari-btn--secondary');
            csvBtn.classList.remove('ari-btn');
            csvBtn.classList.add('op-section-btn');
            csvBtn.classList.add('op-section-btn--csv');
        }

        // Move existing "maximize plot" link into the controls group
        var maxBtn = header.querySelector('.op-plot-max-btn');
        if (maxBtn) {
            maxBtn.style.marginLeft = '';
            maxBtn.classList.remove('ari-btn--sm');
            maxBtn.classList.remove('ari-btn--secondary');
            maxBtn.classList.remove('ari-btn');
            maxBtn.classList.add('op-section-btn');
            controls.appendChild(maxBtn);
        }

        var pinBtn = document.createElement('button');
        pinBtn.type = 'button';
        pinBtn.className = 'op-section-btn op-section-btn--pin';
        pinBtn.setAttribute('data-op-pin-id', sectionId);
        pinBtn.innerHTML = '<i class="fa-solid fa-thumbtack" style="transform:rotate(45deg);opacity:0.45"></i>';
        pinBtn.title = 'Pin section to top';
        pinBtn.addEventListener('click', function () {
            toggleSectionPinned(sectionId);
        });

        var toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'op-section-btn op-section-btn--toggle';
        toggleBtn.addEventListener('click', function () {
            var isCollapsed = cardEl.classList.contains('op-section--collapsed');
            var nextCollapsed = !isCollapsed;
            sectionUserState[sectionId] = !nextCollapsed; // true=open, false=closed
            setSectionCollapsed(cardEl, nextCollapsed);
        });

        controls.appendChild(pinBtn);
        controls.appendChild(toggleBtn);
        // CSV button is rightmost — append after pin/toggle
        if (csvBtn) {
            controls.appendChild(csvBtn);
        }
        header.appendChild(controls);

        if (!header.hasAttribute('data-op-click-toggle')) {
            header.setAttribute('data-op-click-toggle', '1');
            header.addEventListener('click', function (ev) {
                var target = ev.target;
                if (!target) return;
                if (target.closest('.op-section-controls')) return;
                if (target.closest('button, a, input, select, textarea, label')) return;
                var isCollapsed = cardEl.classList.contains('op-section--collapsed');
                var nextCollapsed = !isCollapsed;
                sectionUserState[sectionId] = !nextCollapsed;
                setSectionCollapsed(cardEl, nextCollapsed);
            });
        }

        if (isAllClone) {
            cardEl.classList.add('op-all-section-card');
        }
    }

    function ensurePanelSearchInput(panel, tabKey) {
        if (!panel || !tabKey || tabKey === 'all') return;
        if (panel.querySelector('.op-section-search')) return;

        var wrap = document.createElement('div');
        wrap.className = 'op-section-search';
        wrap.setAttribute('data-op-search-scope', 'tab');
        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'op-section-search__input';
        input.placeholder = 'Filter sections in this tab...';
        input.value = sectionSearch[tabKey] || '';
        input.addEventListener('input', function () {
            sectionSearch[tabKey] = input.value || '';
            applySectionFilter(tabKey);
        });
        wrap.appendChild(input);
        panel.insertBefore(wrap, panel.firstChild);
    }

    function ensureAllSearchInput() {
        var contentHost = document.getElementById('op-content');
        if (!contentHost) return null;
        var existing = contentHost.querySelector('.op-section-search[data-op-search-scope="all"]');
        if (existing) return existing;

        var wrap = document.createElement('div');
        wrap.className = 'op-section-search';
        wrap.setAttribute('data-op-search-scope', 'all');
        wrap.style.display = 'none';
        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'op-section-search__input';
        input.placeholder = 'Filter all sections...';
        input.value = sectionSearch.all || '';
        input.addEventListener('input', function () {
            sectionSearch.all = input.value || '';
            applySectionFilter('all');
        });
        wrap.appendChild(input);

        var firstRealPanel = contentHost.querySelector('.op-tab-panel:not(#op-tab-all)');
        if (firstRealPanel) {
            contentHost.insertBefore(wrap, firstRealPanel);
        } else {
            contentHost.insertBefore(wrap, contentHost.firstChild);
        }
        return wrap;
    }

    function collectSectionCards() {
        var cards = [];
        document.querySelectorAll('.op-tab-panel').forEach(function (panel) {
            var panelId = panel.id || '';
            if (panelId === 'op-tab-all') return;
            var tabKey = panelId.replace(/^op-tab-/, '');
            ensurePanelSearchInput(panel, tabKey);

            panel.querySelectorAll('.at-section-card').forEach(function (card, idx) {
                var rawSid = card.getAttribute('data-op-section-id') || '';
                if (!rawSid) {
                    rawSid = tabKey + '.section_' + (idx + 1);
                }
                var sid = sanitizeSectionToken(rawSid);
                card.setAttribute('data-op-section-id', sid);
                if (!card.getAttribute('data-op-order')) {
                    card.setAttribute('data-op-order', String(idx));
                }
                ensureSectionHeaderControls(card, sid, false);
                cards.push({
                    id: sid,
                    tabKey: tabKey,
                    card: card,
                    host: card.parentElement,
                    order: parseInt(card.getAttribute('data-op-order') || '0', 10),
                    title: getSectionTitle(card),
                });
            });
        });
        return cards;
    }

    function orderSections(cards) {
        var hostMap = new Map();
        cards.forEach(function (meta) {
            var host = meta.host;
            if (!host) return;
            if (!hostMap.has(host)) hostMap.set(host, []);
            hostMap.get(host).push(meta);
        });

        hostMap.forEach(function (items, host) {
            items.sort(function (a, b) {
                var ap = sectionPinnedRank(a.id);
                var bp = sectionPinnedRank(b.id);
                if (ap !== bp) return ap - bp;
                return a.order - b.order;
            });
            items.forEach(function (meta) {
                host.appendChild(meta.card);
            });
        });
    }

    function applyDefaultCollapse(cards) {
        cards.forEach(function (meta) {
            var sid = meta.id;
            var userState = sectionUserState[sid];
            if (userState === true) {
                // User explicitly opened: keep open
                setSectionCollapsed(meta.card, false);
            } else if (userState === false) {
                // User explicitly closed: keep closed
                setSectionCollapsed(meta.card, true);
            } else {
                // No explicit user state: apply default (pinned=open)
                setSectionCollapsed(meta.card, !isSectionPinned(sid));
            }
        });
    }

    function stripElementIds(root) {
        if (!root || root.nodeType !== 1) return;
        root.removeAttribute('id');
        Array.prototype.forEach.call(root.children || [], function (child) {
            stripElementIds(child);
        });
    }

    function rebuildAllSections(cards) {
        if (!allSectionsHost) return;
        ensureAllSearchInput();
        allSectionsHost.innerHTML = '';

        var ordered = cards.slice().sort(function (a, b) {
            var ap = sectionPinnedRank(a.id);
            var bp = sectionPinnedRank(b.id);
            if (ap !== bp) return ap - bp;
            var at = tabRank(a.tabKey);
            var bt = tabRank(b.tabKey);
            if (at !== bt) return at - bt;
            return a.order - b.order;
        });

        ordered.forEach(function (meta) {
            var card = document.createElement('div');
            card.className = 'at-section-card op-all-section-card';
            card.setAttribute('data-op-origin-id', meta.id);
            card.setAttribute('data-op-section-id', meta.id);

            // Clone original header so all-tab sections match individual tabs
            var origHeader = meta.card.querySelector('.at-section-card__header');
            var head;
            if (origHeader) {
                head = origHeader.cloneNode(true);
                // Extract CSV and max buttons from stale controls before removing
                var staleControls = head.querySelector('.op-section-controls');
                if (staleControls) {
                    var csvClone = staleControls.querySelector('.op-section-btn--csv');
                    var maxClone = staleControls.querySelector('.op-plot-max-btn');
                    // Re-add them as direct children of the header so
                    // ensureSectionHeaderControls can pick them up again
                    if (csvClone) {
                        csvClone.classList.add('ari-btn');
                        head.appendChild(csvClone);
                    }
                    if (maxClone) {
                        maxClone.classList.add('op-plot-max-btn');
                        head.appendChild(maxClone);
                    }
                    staleControls.remove();
                }
                // Append tab badge to the title span
                var titleSpan = head.querySelector('span');
                if (titleSpan) {
                    titleSpan.innerHTML += ' <span class="op-all-section-tab">('
                        + escHtml(getPanelLabel(meta.tabKey)) + ')</span>';
                }
                stripElementIds(head);
            } else {
                head = document.createElement('div');
                head.className = 'at-section-card__header';
                var span = document.createElement('span');
                span.textContent = meta.title || meta.id;
                head.appendChild(span);
            }
            card.appendChild(head);

            var body = meta.card.querySelector('.at-section-card__body');
            var cloneBody = body ? body.cloneNode(true) : document.createElement('div');
            cloneBody.classList.add('at-section-card__body');
            stripElementIds(cloneBody);
            card.appendChild(cloneBody);

            // ensureSectionHeaderControls will re-create controls with fresh
            // event handlers (CSV, maximize, pin, toggle buttons)
            ensureSectionHeaderControls(card, meta.id, true);
            // Re-wire CSV button click handler on the cloned card
            wireAllTabCsvButton(card, meta.id);

            setSectionCollapsed(card, true);
            allSectionsHost.appendChild(card);
        });
    }

    /** Wire CSV download handler on a cloned all-tab card by section ID. */
    function wireAllTabCsvButton(cardEl, sectionId) {
        var btn = cardEl.querySelector('.op-section-btn--csv');
        if (!btn) return;
        var handler = csvHandlerForSection(sectionId);
        if (handler) {
            btn.addEventListener('click', handler);
        } else {
            // No handler for this section – remove the orphan button
            btn.remove();
        }
    }

    function csvHandlerForSection(sectionId) {
        if (sectionId === 'target.info') return downloadTargetCsv;
        if (sectionId === 'spectrum.info') return downloadSpectrumCsv;
        if (sectionId === 'ccf.stats') return downloadCcfCsv;
        if (sectionId === 'time_series.table') return downloadTimeSeriesCsv;
        // LBL per-flavor CSV buttons have their handlers attached during
        // renderLbl(); the cloned button won't have one, but we can look
        // up the original button's handler by re-using the section ID.
        if (sectionId.indexOf('lbl.stats.') === 0) return downloadLblFlavorCsv(sectionId);
        return null;
    }

    /** Build a handler that downloads the LBL CSV for a given flavor section. */
    function downloadLblFlavorCsv(sectionId) {
        return function () {
            // Find the original card and click its CSV button
            var orig = document.querySelector(
                '.op-tab-panel:not(#op-tab-all) .at-section-card[data-op-section-id="' + sectionId + '"] .op-section-btn--csv'
            );
            if (orig) orig.click();
        };
    }

    function savePinnedOrder(newOrder) {
        var url = cfg.objectSectionApiReorder;
        if (!url) return Promise.resolve();
        return fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ids: newOrder}),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) return;
                var payload = data.object_section || {};
                sectionPinned = Array.isArray(payload.pinned) ? payload.pinned : [];
                refreshSectionsUi();
            })
            .catch(function () {});
    }

    function renderPinnedReorder(cards) {
        if (!allPinnedReorder) return;
        if (!sectionPinned.length) {
            allPinnedReorder.style.display = 'none';
            allPinnedReorder.innerHTML = '';
            return;
        }

        sectionTitleMap = {};
        cards.forEach(function (c) {
            if (!sectionTitleMap[c.id]) {
                sectionTitleMap[c.id] = c.title || c.id;
            }
        });

        var html = '<div class="op-pin-reorder__title">'
            + '<i class="fa-solid fa-arrows-up-down-left-right"></i> '
            + 'Pinned order (drag to reorder):'
            + '</div>'
            + '<div class="op-pin-reorder__list"></div>';
        allPinnedReorder.innerHTML = html;
        allPinnedReorder.style.display = '';

        var list = allPinnedReorder.querySelector('.op-pin-reorder__list');
        if (!list) return;

        sectionPinned.forEach(function (sid) {
            var chip = document.createElement('div');
            chip.className = 'op-pin-chip';
            chip.setAttribute('data-op-pin-id', sid);
            chip.setAttribute('draggable', 'true');
            chip.innerHTML = '<span class="op-pin-chip__handle">\u2630</span>'
                + '<span>' + escHtml(sectionTitleMap[sid] || sid) + '</span>';
            list.appendChild(chip);
        });

        var dragId = '';
        list.querySelectorAll('.op-pin-chip').forEach(function (chip) {
            chip.addEventListener('dragstart', function () {
                dragId = chip.getAttribute('data-op-pin-id') || '';
                chip.classList.add('op-pin-chip--dragging');
            });
            chip.addEventListener('dragend', function () {
                chip.classList.remove('op-pin-chip--dragging');
            });
            chip.addEventListener('dragover', function (ev) {
                ev.preventDefault();
            });
            chip.addEventListener('drop', function (ev) {
                ev.preventDefault();
                var targetId = chip.getAttribute('data-op-pin-id') || '';
                if (!dragId || !targetId || dragId === targetId) return;

                var order = sectionPinned.slice();
                var from = order.indexOf(dragId);
                var to = order.indexOf(targetId);
                if (from < 0 || to < 0) return;
                order.splice(from, 1);
                order.splice(to, 0, dragId);
                savePinnedOrder(order);
            });
        });
    }

    function applySectionFilter(tabKey) {
        var query = String(sectionSearch[tabKey] || '').trim().toLowerCase();
        if (tabKey === 'all') {
            document.querySelectorAll('.op-tab-panel:not(#op-tab-all) .at-section-card[data-op-section-id]').forEach(function (card) {
                var sid = card.getAttribute('data-op-origin-id') || '';
                if (!sid) {
                    sid = card.getAttribute('data-op-section-id') || '';
                }
                var txt = (card.textContent || '').toLowerCase();
                var show = !query || txt.indexOf(query) !== -1 || sid.indexOf(query) !== -1;
                card.style.display = show ? '' : 'none';
            });
            return;
        }

        var panel = document.getElementById('op-tab-' + tabKey);
        if (!panel) return;
        panel.querySelectorAll('.at-section-card[data-op-section-id]').forEach(function (card) {
            var sid = card.getAttribute('data-op-section-id') || '';
            var txt = (getSectionTitle(card) || '').toLowerCase();
            var show = !query || txt.indexOf(query) !== -1 || sid.indexOf(query) !== -1;
            card.style.display = show ? '' : 'none';
        });
    }

    function refreshSectionsUi() {
        var cards = collectSectionCards();
        orderSections(cards);
        applyDefaultCollapse(cards);
        // All-tab now shows original tab panels directly; do not build cloned
        // synthetic cards to avoid duplicated/misplaced controls.
        if (allSectionsHost) {
            allSectionsHost.innerHTML = '';
        }
        renderPinnedReorder(cards);
        updatePinnedButtons();

        var tabKeys = {};
        cards.forEach(function (c) { tabKeys[c.tabKey] = true; });
        Object.keys(tabKeys).forEach(function (tabKey) {
            applySectionFilter(tabKey);
        });
        applySectionFilter('all');
        ensurePlotReloadButtons();
    }

    function toggleSectionPinned(sectionId) {
        var url = cfg.objectSectionApiToggle;
        if (!url) return;
        fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({section_id: sectionId}),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) return;
                var payload = data.object_section || {};
                var wasPinned = isSectionPinned(sectionId);
                sectionPinned = Array.isArray(payload.pinned) ? payload.pinned : [];
                // Pinning a section always opens it; clear any explicit closed state
                if (isSectionPinned(sectionId) && !wasPinned) {
                    sectionUserState[sectionId] = true;
                }
                refreshSectionsUi();
            })
            .catch(function () {});
    }

    function loadSectionPrefs() {
        var url = cfg.objectSectionApiGet;
        if (!url) {
            return Promise.resolve();
        }
        return fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) return;
                var payload = data.object_section || {};
                sectionPinned = Array.isArray(payload.pinned) ? payload.pinned : [];
            })
            .catch(function () {});
    }

    function parseList(value) {
        var raw = String(value === null || value === undefined ? '' : value).trim();
        if (!raw || raw === '--') {
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
                + escHtml(placeholderText || '--') + '</div>';
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
            var value = Object.prototype.hasOwnProperty.call(row, 'value')
                ? row.value : row[1];
            var filterable = !!row.filterable;
            var displayValue = valOrDash(value);

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
            if (displayValue.length > 180) {
                val.classList.add('op-kv-value--long');
            }
            if (filterable) {
                val.classList.add('op-kv-value--no-scroll');
                val.innerHTML = renderFilterableList(displayValue, '--');
            } else {
                val.innerHTML = escHtml(displayValue);
            }

            if (!filterable && displayValue === '--') {
                val.classList.add('op-kv-value--placeholder');
            }

            item.appendChild(lbl);
            item.appendChild(val);
            container.appendChild(item);
        });

        bindListFilters(container);
    }

    function renderTarget(target) {
        // Target info is rendered EXCLUSIVELY by the shared
        // AperoTargetInfo component (filterable card sections).
        // There is no plain-text / kv-grid fallback: if the
        // payload is missing or the renderer is not loaded the
        // section stays empty rather than reverting to the legacy
        // grid. See /memories/repo for context on why.
        var host = document.getElementById('op-target-info-shared');
        if (!host) return;
        if (!window.AperoTargetInfo
                || typeof window.AperoTargetInfo.render !== 'function') {
            if (window.console && window.console.error) {
                window.console.error(
                    'AperoTargetInfo missing - target info will not '
                    + 'render. Check target_info_render.js loaded.'
                );
            }
            host.innerHTML = '';
            return;
        }
        if (!target || !Array.isArray(target.sections)
                || target.sections.length === 0) {
            // Surface server-side build errors (no silent blanks).
            if (target && target.error) {
                host.innerHTML =
                    '<div class="ari-alert ari-alert--error" '
                    + 'style="padding:0.75rem 1rem;border:1px solid '
                    + 'var(--ari-danger,#d73a49);border-radius:6px;'
                    + 'background:#fff5f5;color:#86181d;">'
                    + '<strong>Target Information build failed:</strong> '
                    + String(target.error)
                        .replace(/&/g,'&amp;')
                        .replace(/</g,'&lt;')
                        .replace(/>/g,'&gt;')
                    + '</div>';
            } else {
                host.innerHTML = '';
            }
            return;
        }
        window.AperoTargetInfo.render(host, target, {
            apero_name: target.apero_name || target.object_name,
            userPerms: (window.AperoRI
                && window.AperoRI.userPerms) || []
        });
    }

    /* ------------------------------------------------------------------
       Finder chart generation (on-demand, with SSE streaming)
    ------------------------------------------------------------------ */
    function _finderResetUi() {
        if (finderGenerateBtn) {
            finderGenerateBtn.style.display = 'none';
        }
        if (finderLoading) {
            finderLoading.style.display = '';
        }
        if (finderError) {
            finderError.style.display = 'none';
        }
        if (finderImages) {
            finderImages.style.display = 'none';
        }
        if (finderLogWrap) {
            finderLogWrap.style.display = 'none';
        }
        if (finderRegen) {
            finderRegen.style.display = 'none';
        }
    }

    function _finderShowError(msg) {
        if (finderLoading) {
            finderLoading.style.display = 'none';
        }
        if (finderError) {
            finderError.textContent = msg;
            finderError.style.display = '';
        }
        if (finderGenerateBtn) {
            finderGenerateBtn.style.display = '';
        }
        if (finderRegen) {
            finderRegen.style.display = '';
        }
    }

    function _finderHandleResult(data) {
        if (finderLoading) {
            finderLoading.style.display = 'none';
        }
        if (!data || !data.success) {
            _finderShowError(
                (data && data.error)
                    ? data.error
                    : 'Failed to generate finder charts.'
            );
            return;
        }
        renderFinderImages(
            data.images || [],
            data.bands || [],
            data.titles || []
        );
        if (finderRegen) {
            finderRegen.style.display = '';
        }
    }

    function _finderAppendLog(text) {
        if (!finderLogPre) return;
        finderLogPre.textContent += text;
        finderLogPre.scrollTop = finderLogPre.scrollHeight;
    }

    /**
     * Open an EventSource to stream finder chart console
     * output in real-time.
     */
    function _finderStreamGenerate(url) {
        // show the console output panel immediately
        if (finderLogWrap) {
            finderLogWrap.style.display = '';
            finderLogWrap.open = true;
        }
        if (finderLogPre) finderLogPre.textContent = '';

        var source = new EventSource(url);

        source.onmessage = function (e) {
            var msg;
            try { msg = JSON.parse(e.data); }
            catch (_) { return; }

            if (msg.type === 'log') {
                _finderAppendLog(msg.text || '');
            } else if (msg.type === 'done') {
                source.close();
                _finderHandleResult(msg.result);
            } else if (msg.type === 'error') {
                source.close();
                _finderShowError(
                    msg.error || 'Generation failed.'
                );
            }
        };

        source.onerror = function () {
            source.close();
            _finderShowError(
                'Lost connection to server.'
            );
        };
    }

    function loadFinderCharts(force) {
        var streamUrl = cfg.finderChartStreamUrl;
        var fetchUrl = cfg.finderChartApiUrl;
        if (!fetchUrl) return;
        _finderResetUi();

        var params = '?profile_id='
            + encodeURIComponent(cfg.profileId)
            + '&objname='
            + encodeURIComponent(cfg.objname);
        if (force) params += '&_ts=' + Date.now();

        // use SSE streaming for fresh generation
        if (streamUrl
            && (force || !cfg.finderChartCached)) {
            _finderStreamGenerate(streamUrl + params);
            return;
        }
        // fall back to simple fetch (cached results)
        fetch(fetchUrl + params)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                _finderHandleResult(data);
            })
            .catch(function (err) {
                _finderShowError(
                    'Network error: ' + String(err)
                );
            });
    }

    function renderFinderImages(images, bands, titles) {
        if (!finderImages) return;
        var html = '<div style="display:flex;flex-wrap:wrap;gap:1rem;">';
        for (var i = 0; i < images.length; i++) {
            var label = titles[i] || bands[i] || ('Band ' + i);
            var maxUrl = (cfg.finderMaxUrl || '').split('?')[0]
                + '?band_idx=' + i;
            html += '<div style="flex:1 1 400px;max-width:600px;">'
                + '<div style="display:flex;align-items:center;'
                + 'justify-content:space-between;margin-bottom:0.4rem;">'
                + '<strong>' + escHtml(label) + '</strong>'
                + '<a href="' + escHtml(maxUrl) + '" '
                + 'class="ari-btn ari-btn--sm ari-btn--secondary" '
                + 'title="Maximize">'
                + '<i class="fa-solid fa-maximize"></i></a></div>'
                + '<img src="data:image/png;base64,' + images[i] + '" '
                + 'alt="Finder Chart – ' + escHtml(label) + '" '
                + 'style="width:100%;border-radius:0.4rem;'
                + 'border:1px solid var(--op-border,#d6d9de);">'
                + '</div>';
        }
        html += '</div>';
        finderImages.innerHTML = html;
        finderImages.style.display = '';
    }

    /* ------------------------------------------------------------------
       TESS rotation periods (tessilator)
    ------------------------------------------------------------------ */
    var tessSectors = [];
    var tessIdx = 0;

    function _tessResetUi() {
        if (tessGenerateBtn) tessGenerateBtn.style.display = 'none';
        if (tessRegen) tessRegen.style.display = 'none';
        if (tessLoading) tessLoading.style.display = '';
        if (tessError) tessError.style.display = 'none';
        if (tessViewer) tessViewer.style.display = 'none';
        if (tessLogWrap) tessLogWrap.style.display = 'none';
        if (tessDataFiles) tessDataFiles.style.display = 'none';
    }

    function _tessShowError(msg) {
        if (tessLoading) tessLoading.style.display = 'none';
        if (tessError) {
            tessError.textContent = msg;
            tessError.style.display = '';
        }
        if (tessGenerateBtn) {
            tessGenerateBtn.style.display = '';
        }
        if (tessRegen) {
            tessRegen.style.display = '';
        }
    }

    function _tessHandleResult(data) {
        if (tessLoading) tessLoading.style.display = 'none';
        if (!data || !data.success) {
            _tessShowError(
                (data && data.error)
                    ? data.error
                    : 'Failed to generate TESS data.'
            );
            return;
        }
        tessSectors = data.sectors || [];
        tessIdx = 0;
        renderTessSector();
        renderTessDataFiles(data.data_files || []);
        showTessLog(data.console_log || '');
    }

    /**
     * Load TESS rotation results.
     *
     * For cached results use a normal fetch.  For fresh
     * generation open an SSE stream so that console output
     * appears in real-time.
     */
    function loadTessRotation(force) {
        var streamUrl = cfg.tessRotationStreamUrl;
        var fetchUrl = cfg.tessRotationApiUrl;
        if (!fetchUrl) return;
        _tessResetUi();

        var params = '?profile_id='
            + encodeURIComponent(cfg.profileId)
            + '&objname='
            + encodeURIComponent(cfg.objname);
        if (force) params += '&_ts=' + Date.now();

        // Use SSE streaming for fresh generation
        if (streamUrl && (force || !cfg.tessRotationCached)) {
            _tessStreamGenerate(streamUrl + params);
            return;
        }
        // Fall back to simple fetch (cached results)
        fetch(fetchUrl + params)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                _tessHandleResult(data);
            })
            .catch(function (err) {
                _tessShowError('Network error: '
                    + String(err));
            });
    }

    /**
     * Open an EventSource to the SSE endpoint and stream
     * tessilator console output into the log panel.
     */
    function _tessStreamGenerate(url) {
        // Show the console output panel immediately (open)
        if (tessLogWrap) {
            tessLogWrap.style.display = '';
            tessLogWrap.open = true;
        }
        if (tessLogPre) tessLogPre.textContent = '';

        var source = new EventSource(url);

        source.onmessage = function (e) {
            var msg;
            try { msg = JSON.parse(e.data); }
            catch (_) { return; }

            if (msg.type === 'log') {
                _tessAppendLog(msg.text || '');
            } else if (msg.type === 'done') {
                source.close();
                _tessHandleResult(msg.result);
            } else if (msg.type === 'error') {
                source.close();
                _tessShowError(
                    msg.error || 'Generation failed.'
                );
            }
        };

        source.onerror = function () {
            source.close();
            _tessShowError(
                'Lost connection to server.'
            );
        };
    }

    function _tessAppendLog(text) {
        if (!tessLogPre) return;
        tessLogPre.textContent += text;
        // Auto-scroll the <pre> into view
        tessLogPre.scrollTop = tessLogPre.scrollHeight;
    }

    function renderTessSector() {
        if (!tessSectors.length) return;
        if (tessViewer) tessViewer.style.display = '';
        var s = tessSectors[tessIdx];
        var single = tessSectors.length === 1;
        if (tessImg) {
            tessImg.src = 'data:image/png;base64,'
                + s.image;
            tessImg.alt = 'TESS Sector ' + s.sector;
        }
        if (tessLabel) {
            tessLabel.textContent = single
                ? 'Sector ' + s.sector
                : 'Sector ' + s.sector
                    + ' (' + (tessIdx + 1) + ' / '
                    + tessSectors.length + ')';
        }
        // Hide nav arrows when only one sector
        if (tessPrev) {
            tessPrev.style.display = single
                ? 'none' : '';
            tessPrev.disabled = (tessIdx === 0);
        }
        if (tessNext) {
            tessNext.style.display = single
                ? 'none' : '';
            tessNext.disabled = (
                tessIdx >= tessSectors.length - 1
            );
        }
        // Periods ECSV download (shared across sectors)
        if (tessDlLc) {
            if (s.has_csv) {
                tessDlLc.style.display = '';
                tessDlLc.href =
                    cfg.tessRotationLcApiUrl
                    + '?profile_id='
                    + encodeURIComponent(cfg.profileId)
                    + '&objname='
                    + encodeURIComponent(cfg.objname)
                    + '&sector=' + s.sector;
            } else {
                tessDlLc.style.display = 'none';
            }
        }
        // Download all PNGs button
        if (tessDlPng) {
            tessDlPng.style.display =
                tessSectors.length > 0 ? '' : 'none';
        }
        // Regenerate button
        if (tessRegen) {
            tessRegen.style.display = '';
        }
    }

    if (tessPrev) {
        tessPrev.addEventListener('click', function () {
            if (tessIdx > 0) { tessIdx--; renderTessSector(); }
        });
    }
    if (tessNext) {
        tessNext.addEventListener('click', function () {
            if (tessIdx < tessSectors.length - 1) {
                tessIdx++;
                renderTessSector();
            }
        });
    }

    if (tessDlPng) {
        tessDlPng.addEventListener('click', function () {
            tessSectors.forEach(function (s) {
                var a = document.createElement('a');
                a.href = 'data:image/png;base64,'
                    + s.image;
                a.download = (cfg.objname || 'tess')
                    + '_sector_' + s.sector + '.png';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });
        });
    }

    if (tessRegen) {
        tessRegen.addEventListener('click', function () {
            loadTessRotation(true);
        });
    }

    /**
     * Render download links for TESS data files
     * (light curves, periodograms, etc.).
     */
    function renderTessDataFiles(files) {
        if (!tessDataFiles) return;
        // always include periods.ecsv
        var all = ['periods.ecsv'].concat(files || []);
        // deduplicate
        var seen = {};
        var unique = [];
        for (var i = 0; i < all.length; i++) {
            if (!seen[all[i]]) {
                seen[all[i]] = true;
                unique.push(all[i]);
            }
        }
        if (!unique.length) {
            tessDataFiles.style.display = 'none';
            return;
        }
        var baseUrl = cfg.tessRotationDataApiUrl;
        if (!baseUrl) {
            tessDataFiles.style.display = 'none';
            return;
        }
        var params = '?profile_id='
            + encodeURIComponent(cfg.profileId)
            + '&objname='
            + encodeURIComponent(cfg.objname)
            + '&filename=';
        // label mapping for known prefixes
        var html = '<div style="font-size:0.84rem;'
            + 'font-weight:600;color:var(--ari-text-muted'
            + ',#6a737d);margin-bottom:0.35rem;">'
            + '<i class="fa-solid fa-file-csv"></i> '
            + 'Data Products</div>'
            + '<div style="display:flex;flex-wrap:wrap;'
            + 'gap:0.4rem;">';
        for (var j = 0; j < unique.length; j++) {
            var fname = unique[j];
            var label = _tessFileLabel(fname);
            var href = baseUrl + params
                + encodeURIComponent(fname);
            html += '<a href="' + escHtml(href)
                + '" class="ari-btn ari-btn--sm '
                + 'ari-btn--secondary" '
                + 'title="Download ' + escHtml(fname)
                + '" download>'
                + '<i class="fa-solid fa-download">'
                + '</i> ' + escHtml(label) + '</a>';
        }
        html += '</div>';
        tessDataFiles.innerHTML = html;
        tessDataFiles.style.display = '';
    }

    /** Human-friendly label for a tessilator file. */
    function _tessFileLabel(fname) {
        if (fname === 'periods.ecsv') {
            return 'Periods (ECSV)';
        }
        if (fname.indexOf('ap_') === 0) {
            return 'Light Curve (' + fname + ')';
        }
        if (fname.indexOf('pg_') === 0) {
            return 'Periodogram (' + fname + ')';
        }
        return fname;
    }

    function showTessLog(text) {
        if (!tessLogWrap || !tessLogPre) { return; }
        var trimmed = (text || '').trim();
        if (!trimmed) {
            tessLogWrap.style.display = 'none';
            return;
        }
        tessLogPre.textContent = trimmed;
        tessLogWrap.style.display = '';
    }

     /* ------------------------------------------------------------------
         Debug plot generation (lazy-loaded)
     ------------------------------------------------------------------ */
    var debugPlotKeys = ['extsmax', 'effron', 'version', 'cdt', 'tcorr_map'];

    function loadDebugPlots(forceReload, activePlotKey) {
        if (forceReload) {
            debugPlotsState = 'idle';
        }
        if (debugPlotsState === 'loading' || debugPlotsState === 'loaded') return;
        debugPlotsState = 'loading';
        var url = cfg.debugPlotsApiUrl;
        if (!url) {
            debugPlotsState = 'idle';
            return;
        }
        if (debugLoading) debugLoading.style.display = '';
        if (debugError) debugError.style.display = 'none';

        var params = '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname);
        // Forward the active ARI theme so server-side Bokeh and
        // matplotlib figures render with the correct palette.
        try {
            var _theme = (document.documentElement.getAttribute(
                'data-theme') || 'default');
            params += '&theme=' + encodeURIComponent(_theme);
        } catch (_e) { /* ignore */ }
        if (forceReload) {
            params += '&_ts=' + encodeURIComponent(String(Date.now()));
        }
        fetch(url + params)
            .then(function (r) {
                var ctype = String(r.headers.get('content-type') || '').toLowerCase();
                if (ctype.indexOf('application/json') === -1) {
                    return r.text().then(function (txt) {
                        throw new Error('Debug plots API returned non-JSON response ('
                            + r.status + ').');
                    });
                }
                return r.json().then(function (data) {
                    if (!r.ok) {
                        var msg = (data && data.error) ? data.error
                            : ('Debug plots request failed (' + r.status + ').');
                        throw new Error(msg);
                    }
                    return data;
                });
            })
            .then(function (data) {
                if (debugLoading) debugLoading.style.display = 'none';
                if (!data || !data.success) {
                    if (activePlotKey) setPlotReloading(activePlotKey, false);
                    debugPlotsState = 'idle';
                    if (debugError) {
                        debugError.textContent = data && data.error
                            ? data.error : 'Failed to generate debug plots.';
                        debugError.style.display = '';
                    }
                    return;
                }
                renderDebugPlots(data.plots || {});
                var updated = payloadUpdatedDateLabel(data) || currentUtcDateLabel();
                debugPlotKeys.forEach(function (k) {
                    setPlotLastUpdated('debug_' + k, updated);
                });
                if (activePlotKey) setPlotReloading(activePlotKey, false);
                debugPlotsState = 'loaded';
            })
            .catch(function (err) {
                if (activePlotKey) setPlotReloading(activePlotKey, false);
                debugPlotsState = 'idle';
                if (debugLoading) debugLoading.style.display = 'none';
                if (debugError) {
                    debugError.textContent = 'Network error: ' + String(err);
                    debugError.style.display = '';
                }
            });
    }

    function renderDebugPlots(plots) {
        for (var i = 0; i < debugPlotKeys.length; i++) {
            var key = debugPlotKeys[i];
            // tcorr_map is generated on demand via its own button
            if (key === 'tcorr_map') continue;
            var cssKey = key.replace(/_/g, '-');
            var divId = 'op-debug-' + cssKey + '-div';
            var loadId = 'op-debug-' + cssKey + '-loading';
            var info = plots[key];
            // Normalise error → message for embedOrDefer
            if (info && !info.message && info.error) {
                info.message = info.error;
            }
            embedOrDefer(divId, info, 'No data available.', loadId);
        }
    }

    /* --- Telluric map generate-on-demand button ---------------------- */
    (function () {
        function initTcorrMapBtn() {
            var btn = document.getElementById('op-debug-tcorr-map-btn');
            if (!btn) return;
            btn.addEventListener('click', function () {
                var loading = document.getElementById(
                    'op-debug-tcorr-map-loading'
                );
                var genWrap = document.getElementById(
                    'op-debug-tcorr-map-generate-wrap'
                );
                var divId = 'op-debug-tcorr-map-div';
                btn.disabled = true;
                if (genWrap) genWrap.style.display = 'none';
                if (loading) loading.style.display = '';

                var url = (cfg.tcorrMapGenerateApiUrl || '')
                    + '?profile_id=' + encodeURIComponent(cfg.profileId)
                    + '&objname=' + encodeURIComponent(cfg.objname);
                try {
                    var _theme = (document.documentElement.getAttribute(
                        'data-theme') || 'default');
                    url += '&theme=' + encodeURIComponent(_theme);
                } catch (_e) { /* ignore */ }
                fetch(url)
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (loading) loading.style.display = 'none';
                        if (!data || !data.has_plot) {
                            var divEl = document.getElementById(divId);
                            if (divEl) {
                                divEl.innerHTML
                                    = '<div class="at-muted-hint">'
                                    + escHtml(
                                        data && data.message
                                            ? data.message
                                            : 'No telluric map data available.'
                                    )
                                    + '</div>';
                            }
                            if (genWrap) genWrap.style.display = '';
                            btn.disabled = false;
                            return;
                        }
                        // Use injectPlot directly (script may be empty for image)
                        injectPlot(divId, data.script || '', data.div || '');
                        setPlotLastUpdated(
                            'debug_tcorr_map',
                            currentUtcDateLabel()
                        );
                    })
                    .catch(function (err) {
                        if (loading) loading.style.display = 'none';
                        var divEl = document.getElementById(divId);
                        if (divEl) {
                            divEl.innerHTML = '<div class="at-muted-hint">'
                                + escHtml('Network error: ' + String(err))
                                + '</div>';
                        }
                        if (genWrap) genWrap.style.display = '';
                        btn.disabled = false;
                    });
            });
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initTcorrMapBtn);
        } else {
            initTcorrMapBtn();
        }
    }());

    function renderSpectrum(spec) {
        // helper: wrap a header-derived list into a row that the kv
        // renderer will turn into chips + filter when len > 5.
        function listRow(label, arr) {
            var lst = Array.isArray(arr) ? arr : [];
            return {
                label: label,
                value: lst.join('|'),
                filterable: lst.length > 0
            };
        }
        var rows = [
            ['DPRTYPES', spec.dprtypes],
            listRow('OBJECT name(s) in headers',
                    spec.object_names_in_headers),
            listRow('OB Name(s) in headers',
                    spec.ob_names_in_headers),
            listRow('PI Name(s) in headers',
                    spec.pi_names_in_headers),
            listRow('Project / Run ID(s) in headers',
                    spec.project_run_names_in_headers),
            ['Total number raw files', spec.raw_total],
            ['Number of rejected files', spec.raw_rejected],
            ['First raw files', spec.raw_first_mid],
            ['Last raw files', spec.raw_last_mid],
            ['Total number PP files', spec.pp_total],
            ['Number PP files passed QC', spec.pp_passed],
            ['Number PP files failed QC', spec.pp_failed],
            ['First pp file [Mid exposure]', spec.pp_first_mid],
            ['Last pp file [Mid exposure]', spec.pp_last_mid],
            ['Last processed [pp]', spec.pp_last_processed],
            [getLabel('spectrum.pp_version', 'Version [pp]'), spec.pp_version],
            ['Total number ext files', spec.ext_total],
            ['Number ext files passed QC', spec.ext_passed],
            ['Number ext files failed QC', spec.ext_failed],
            ['First ext file [Mid exposure]', spec.ext_first_mid],
            ['Last ext file [Mid exposure]', spec.ext_last_mid],
            ['Last processed [ext]', spec.ext_last_processed],
            [getLabel('spectrum.ext_version', 'Version [ext]'), spec.ext_version],
            ['Total number tcorr files', spec.tcorr_total],
            ['Number tcorr files passed QC', spec.tcorr_passed],
            ['Number tcorr files failed QC', spec.tcorr_failed],
            ['First tcorr file [Mid exposure]', spec.tcorr_first_mid],
            ['Last tcorr file [Mid exposure]', spec.tcorr_last_mid],
            ['Last processed [tcorr]', spec.tcorr_last_processed],
            ['Version [tcorr]', spec.tcorr_version],
            ['Median SNR Y', spec.median_snr_y],
            ['Median SNR H', spec.median_snr_h]
        ];
        renderKvGrid(spectrumGrid, rows);
    }

    function _makeLblFlavorRows(flavor) {
        return [
            ['RV Uncertainty lbl.rdb (25, 50, 75 percentile)', flavor.rv_uncertainty_percentiles],
            ['RV Absolute Deviation lbl.rdb (25, 50, 75 percentile)', flavor.rv_abs_dev_percentiles],
            ['Number of lbl.rdb Measurements', flavor.measurement_count],
            ['Number of lbl.rdb Spurious Low Points', flavor.spurious_low_points],
            ['Number of lbl.rdb Spurious High Points', flavor.spurious_high_points],
            ['Number of Nights', flavor.n_nights],
            ['Number of Reset RV Points', flavor.n_reset_rv_points],
            ['Systemic Velocity', flavor.systemic_velocity],
            ['Velocity Domain considered valid', flavor.valid_velocity_domain],
            ['LBL Version', flavor.lbl_version]
        ];
    }

    function renderLbl(lbl) {
        if (!lblSections) return;
        lblSections.innerHTML = '';

        var flavors = Array.isArray(lbl.flavors) ? lbl.flavors : [];

        // If no per-flavor data, fall back to summary card
        if (flavors.length === 0) {
            var fallbackCard = document.createElement('div');
            fallbackCard.className = 'at-section-card';
            fallbackCard.setAttribute('data-op-section-id', 'lbl.stats');
            fallbackCard.innerHTML =
                '<div class="at-section-card__header">' +
                '<span><i class="fa-solid fa-chart-line"></i> LBL Stats</span>' +
                '</div>' +
                '<div class="at-section-card__body"><div class="op-kv-grid"></div></div>';
            var grid = fallbackCard.querySelector('.op-kv-grid');
            renderKvGrid(grid, _makeLblFlavorRows(lbl));
            lblSections.appendChild(fallbackCard);
            return;
        }

        // One card per science+comparison flavor
        flavors.forEach(function (flavor, idx) {
            var flavorId = escHtml(flavor.flavor_id || flavor.rdb_filename || ('Flavor ' + (idx + 1)));
            var csvBtnId = 'op-download-lbl-csv-' + idx;
            var gridId = 'op-lbl-grid-' + idx;
            var sidToken = sanitizeSectionToken(flavor.flavor_id || flavor.rdb_filename || ('flavor_' + (idx + 1)));

            var card = document.createElement('div');
            card.className = 'at-section-card';
            card.setAttribute('data-op-section-id', 'lbl.stats.' + sidToken);
            card.innerHTML =
                '<div class="at-section-card__header">' +
                '<span><i class="fa-solid fa-chart-line"></i> LBL Stats &mdash; ' + flavorId + '</span>' +
                '<button id="' + csvBtnId + '" class="ari-btn ari-btn--sm ari-btn--secondary" ' +
                    'title="Download LBL statistics as CSV" style="margin-left:auto;">' +
                    '<i class="fa-solid fa-download"></i>' +
                '</button>' +
                '</div>' +
                '<div class="at-section-card__body"><div id="' + gridId + '" class="op-kv-grid"></div></div>';

            var grid = card.querySelector('#' + gridId);
            renderKvGrid(grid, _makeLblFlavorRows(flavor));

            // CSV download for this flavor
            var csvBtn = card.querySelector('#' + csvBtnId);
            if (csvBtn) {
                (function (f) {
                    csvBtn.addEventListener('click', function () {
                        var rows = [['Field', 'Value']].concat(_makeLblFlavorRows(f));
                        downloadCsv('lbl_stats_' + (f.flavor_id || 'flavor') + '.csv', rows);
                    });
                }(flavor));
            }

            lblSections.appendChild(card);

            var velCard = document.createElement('div');
            velCard.className = 'at-section-card';
            velCard.setAttribute('data-op-section-id', 'lbl.velocity.' + sidToken);
            var velLoadingId = 'op-lbl-vel-loading-' + sidToken;
            var velPlotDivId = 'op-lbl-vel-plot-' + sidToken;
            var lblMaxHref = '/data_portal/' + encodeURIComponent(cfg.profileId)
                + '/object-plot-max/' + encodeURIComponent(cfg.objname)
                + '/lbl?lbl_file=' + encodeURIComponent(flavor.rdb_filename || '');
            velCard.innerHTML =
                '<div class="at-section-card__header">'
                + '<span><i class="fa-solid fa-chart-line"></i> LBL Velocity Plot -- '
                + flavorId + '</span>'
                + '<button type="button" data-op-download="lbl" '
                + 'data-op-lbl-format="zip" '
                + 'class="ari-btn ari-btn--sm ari-btn--secondary op-plot-dl-btn" '
                + 'title="Download all LBL files for this object (zip)" '
                + 'style="margin-left:auto;">'
                + '<i class="fa-solid fa-download"></i></button>'
                + '<button type="button" data-op-download="lbl" '
                + 'data-op-lbl-format="tar" '
                + 'class="ari-btn ari-btn--sm ari-btn--secondary op-plot-dl-btn" '
                + 'title="Download all LBL files for this object (tar.gz)">'
                + '<i class="fa-solid fa-file-zipper"></i></button>'
                + '<a href="' + lblMaxHref + '" '
                + 'class="ari-btn ari-btn--sm ari-btn--secondary op-plot-max-btn" '
                + 'title="Maximize plot">'
                + '<i class="fa-solid fa-maximize"></i></a>'
                + '</div>'
                + '<div class="at-section-card__body">'
                + '<div id="' + velLoadingId + '" class="at-muted-hint">'
                + '<i class="fa-solid fa-spinner fa-spin"></i> Loading plot&hellip;'
                + '</div>'
                + '<div id="' + velPlotDivId + '"></div>'
                + '</div>';
            lblSections.appendChild(velCard);
        });
    }

    function renderCcf(ccf) {
        var rows = [
            ['Mask used', ccf.mask_used],
            ['CCF systemic velocity', ccf.systemic_velocity],
            ['CCF FWHM', ccf.fwhm],
            ['Number of CCF files Total', ccf.total_files],
            ['Number of CCF passed QC', ccf.passed_qc],
            ['Number CCF files failed QC', ccf.failed_qc],
            ['First ccf file [Mid exposure]', ccf.first_mid],
            ['Last ccf file [Mid exposure]', ccf.last_mid],
            ['Last processed [ccf]', ccf.last_processed],
            [getLabel('ccf.ccf_version', 'Version [ccf]'), ccf.ccf_version]
        ];
        renderKvGrid(ccfGrid, rows);
    }

    function renderTimeSeries(rows) {
        if (!tsBody) return;
        tsBody.innerHTML = '';

        if (!rows || rows.length === 0) {
            tsBody.innerHTML = '<tr><td colspan="12" class="ot-empty">No rows</td></tr>';
            refreshTimeSeriesDualScroll();
            return;
        }

        // Wire up "add all ext/tcorr" header buttons
        var addAllExtBtn   = document.getElementById('op-ts-add-all-ext');
        var addAllTcorrBtn = document.getElementById('op-ts-add-all-tcorr');
        if (addAllExtBtn) {
            addAllExtBtn.addEventListener('click', function () {
                if (window.ARI_FB_ADD_FROM_FTABLE) {
                    rows.forEach(function (r) {
                        if (r.obs_dir) window.ARI_FB_ADD_FROM_FTABLE(r.obs_dir, 'ext');
                    });
                }
            });
        }
        if (addAllTcorrBtn) {
            addAllTcorrBtn.addEventListener('click', function () {
                if (window.ARI_FB_ADD_FROM_FTABLE) {
                    rows.forEach(function (r) {
                        if (r.obs_dir) window.ARI_FB_ADD_FROM_FTABLE(r.obs_dir, 'tcorr');
                    });
                }
            });
        }

        var frag = document.createDocumentFragment();
        rows.forEach(function (r) {
            var tr = document.createElement('tr');
            tr.className = 'op-ts-row';

            var colDefs = [
                {val: r.obs_dir},
                {val: r.first_obs_mid},
                {val: r.last_obs_mid},
                {val: r.num_ext,   basketFkind: 'ext'},
                {val: r.num_tcorr, basketFkind: 'tcorr'},
                {val: r.seeing},
                {val: r.airmass},
                {val: r.mean_exptime},
                {val: r.total_exptime},
                {val: r.snr_order_15},
                {val: r.snr_order_60},
                {val: r.dprtypes}
            ];

            colDefs.forEach(function (cd) {
                var td = document.createElement('td');
                var isMissing = (cd.val === null || cd.val === undefined || cd.val === '');
                var v = isMissing ? '--' : String(cd.val);
                if (/^\d+\s*\(\d+\)/.test(v)) {
                    td.className = 'op-ts-count';
                }
                if (cd.basketFkind && r.obs_dir) {
                    var wrap = document.createElement('span');
                    wrap.className = 'op-ts-count-wrap';
                    wrap.textContent = v;
                    var bkBtn = document.createElement('button');
                    bkBtn.className = 'op-ts-basket-btn';
                    bkBtn.title = 'Add ' + cd.basketFkind + ' files from this night to basket';
                    bkBtn.innerHTML = '<i class="fa-solid fa-basket-shopping"></i>';
                    (function (obsDir, fkind) {
                        bkBtn.addEventListener('click', function (e) {
                            e.stopPropagation();
                            if (window.ARI_FB_ADD_FROM_FTABLE) {
                                window.ARI_FB_ADD_FROM_FTABLE(obsDir, fkind);
                            }
                        });
                    }(r.obs_dir, cd.basketFkind));
                    td.appendChild(wrap);
                    td.appendChild(bkBtn);
                } else {
                    td.textContent = v;
                }
                tr.appendChild(td);
            });

            frag.appendChild(tr);
        });
        tsBody.appendChild(frag);
        refreshTimeSeriesDualScroll();
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

    function renderSnrPlot(payload) {
        embedOrDefer('op-snr-plot-div', payload, 'No SNR data available.');
    }

    function renderSedPlot(payload) {
        embedOrDefer('op-sed-plot-div', payload,
            'SED unavailable for this target.');
    }

    function renderHrPlot(payload) {
        embedOrDefer('op-hr-plot-div', payload,
            'HR diagram unavailable for this target.');
    }

    function renderBervPlot(payload) {
        embedOrDefer('op-berv-plot-div', payload, 'No BERV data available.');
    }

    function renderSpecPlot(payload) {
        embedOrDefer('op-spec-plot-div', payload, 'No spectrum data available.');
    }

    function renderCcfRvPlot(payload) {
        embedOrDefer('op-ccf-rv-plot-div', payload, 'No CCF RV data available.', 'op-ccf-rv-plot-loading');
    }

    function renderCcfProfilePlot(payload) {
        embedOrDefer('op-ccf-profile-plot-div', payload, 'No CCF profile data available.', 'op-ccf-plot-loading');
        updateCcfSamplingNote(payload ? payload.sample_info : null);
    }

    function parseMjdInputValue(inputEl) {
        if (!inputEl) return null;
        var sval = String(inputEl.value || '').trim();
        if (!sval) return null;
        if (/^\d{4}-\d{2}-\d{2}$/.test(sval)) {
            var ms = Date.parse(sval + 'T00:00:00Z');
            if (!isFinite(ms)) return null;
            return (ms / 86400000.0) + 40587.0;
        }
        var v = Number(sval);
        if (!isFinite(v)) return null;
        return v;
    }

    function parseMjdEndInputValue(inputEl) {
        if (!inputEl) return null;
        var sval = String(inputEl.value || '').trim();
        if (!sval) return null;
        if (/^\d{4}-\d{2}-\d{2}$/.test(sval)) {
            var ms = Date.parse(sval + 'T23:59:59.999Z');
            if (!isFinite(ms)) return null;
            return (ms / 86400000.0) + 40587.0;
        }
        var v = Number(sval);
        if (!isFinite(v)) return null;
        return v;
    }

    function parseNobsInputValue(inputEl) {
        if (!inputEl) return 100;
        var sval = String(inputEl.value || '').trim();
        if (!sval) return 100;
        var n = parseInt(sval, 10);
        if (!isFinite(n) || n < 1) return 100;
        return n;
    }

    function mjdToIsoDate(mjd) {
        var v = Number(mjd);
        if (!isFinite(v)) return '';
        var ms = (v - 40587.0) * 86400000.0;
        var d = new Date(ms);
        if (!isFinite(d.getTime())) return '';
        return d.toISOString().slice(0, 10);
    }

    function syncCcfRangeInputs(sampleInfo) {
        if (!sampleInfo || typeof sampleInfo !== 'object') return;
        var minMjd = Number(sampleInfo.available_mjd_min);
        var maxMjd = Number(sampleInfo.available_mjd_max);
        var minDate = isFinite(minMjd) ? mjdToIsoDate(minMjd) : '';
        var maxDate = isFinite(maxMjd) ? mjdToIsoDate(maxMjd) : '';
        if (ccfMjdStartInput && minDate) {
            ccfMjdStartInput.min = minDate;
        }
        if (ccfMjdEndInput && maxDate) {
            ccfMjdEndInput.max = maxDate;
        }
        if (ccfNobsInput) {
            var maxFiles = Number(sampleInfo.max_files || 100);
            if (isFinite(maxFiles) && maxFiles >= 1) {
                ccfNobsInput.max = String(Math.max(1, Math.floor(maxFiles * 10)));
            }
        }
    }

    function updateCcfSamplingNote(sampleInfo) {
        var noteEls = [];
        document.querySelectorAll('.op-ccf-sampling-note').forEach(function (el) {
            if (el instanceof Element) noteEls.push(el);
        });
        if (ccfSamplingNote && noteEls.indexOf(ccfSamplingNote) === -1) {
            noteEls.unshift(ccfSamplingNote);
        }
        if (!noteEls.length) return;

        function setAllNotes(text) {
            noteEls.forEach(function (el) {
                el.textContent = text;
            });
        }

        if (!sampleInfo || typeof sampleInfo !== 'object') {
            setAllNotes(
                'The median CCF profile uses up to 100 files sampled uniformly in time. Change the time period here:'
            );
            return;
        }
        syncCcfRangeInputs(sampleInfo);
        var maxFiles = Number(sampleInfo.max_files || 100);
        var mode = String(sampleInfo.sampling_mode || 'all');
        var modeTxt = (mode === 'equally_spaced')
            ? ('using ' + maxFiles + ' equally time-spaced files')
            : 'using all files (<= ' + maxFiles + ')';
        setAllNotes(
            'The median CCF profile uses up to ' + maxFiles + ' files sampled uniformly in time. '
            + 'Change the time period here: ' + modeTxt + '.'
        );
    }

    function bindCcfRangeControls() {
        function applyRange() {
            var startVal = parseMjdInputValue(ccfMjdStartInput);
            var endVal = parseMjdEndInputValue(ccfMjdEndInput);
            var nobsVal = parseNobsInputValue(ccfNobsInput);
            if (startVal !== null && endVal !== null && startVal > endVal) {
                var tmp = startVal;
                startVal = endVal;
                endVal = tmp;
                if (ccfMjdStartInput) ccfMjdStartInput.value = mjdToIsoDate(startVal);
                if (ccfMjdEndInput) ccfMjdEndInput.value = mjdToIsoDate(endVal);
            }
            if (ccfNobsInput) ccfNobsInput.value = String(nobsVal);
            ccfRangeFilter.mjdStart = startVal;
            ccfRangeFilter.mjdEnd = endVal;
            ccfRangeFilter.nobs = nobsVal;
            updatePlotMaxLinks();
            loadObjectPlots('ccf_profile', true);
        }

        if (ccfApplyRangeBtn) {
            ccfApplyRangeBtn.addEventListener('click', applyRange);
        }
        if (ccfResetRangeBtn) {
            ccfResetRangeBtn.addEventListener('click', function () {
                if (ccfMjdStartInput) ccfMjdStartInput.value = '';
                if (ccfMjdEndInput) ccfMjdEndInput.value = '';
                if (ccfNobsInput) ccfNobsInput.value = '100';
                ccfRangeFilter.mjdStart = null;
                ccfRangeFilter.mjdEnd = null;
                ccfRangeFilter.nobs = 100;
                updatePlotMaxLinks();
                loadObjectPlots('ccf_profile', true);
            });
        }
        if (ccfMjdStartInput) {
            ccfMjdStartInput.addEventListener('keydown', function (ev) {
                if (ev.key === 'Enter') applyRange();
            });
        }
        if (ccfMjdEndInput) {
            ccfMjdEndInput.addEventListener('keydown', function (ev) {
                if (ev.key === 'Enter') applyRange();
            });
        }
        if (ccfNobsInput) {
            ccfNobsInput.addEventListener('keydown', function (ev) {
                if (ev.key === 'Enter') applyRange();
            });
        }
    }

    function renderTsSnrPlot(payload) {
        embedOrDefer('op-ts-snr-plot-div', payload, 'No per-night SNR data available.');
    }

    function renderTsAirmassPlot(payload) {
        embedOrDefer('op-ts-airmass-plot-div', payload, 'No per-night airmass data available.');
    }

    function loadLblPlots(forceReload, activePlotKey) {
        if (forceReload) {
            lblPlotsState = 'idle';
        }
        if (lblPlotsState === 'loading' || lblPlotsState === 'loaded') return;
        lblPlotsState = 'loading';
        var url = cfg.objectLblPlotsApiUrl;
        if (!url) {
            lblPlotsState = 'idle';
            return;
        }
        var params = '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname);
        try {
            var _theme = (document.documentElement.getAttribute(
                'data-theme') || 'default');
            params += '&theme=' + encodeURIComponent(_theme);
        } catch (_e) { /* ignore */ }
        if (forceReload) {
            params += '&_ts=' + encodeURIComponent(String(Date.now()));
        }
        fetch(url + params)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success || !data.plots) {
                    if (activePlotKey) setPlotReloading(activePlotKey, false);
                    lblPlotsState = 'idle';
                    return;
                }
                Object.keys(data.plots).forEach(function (rdb_filename) {
                    var payload = data.plots[rdb_filename];
                    var m = rdb_filename.match(/^lbl_(.+)\.rdb$/i);
                    var flavor_id = m ? m[1] : rdb_filename;
                    var sidToken = sanitizeSectionToken(flavor_id);
                    var divId = 'op-lbl-vel-plot-' + sidToken;
                    var loadId = 'op-lbl-vel-loading-' + sidToken;
                    embedOrDefer(divId, payload, 'No LBL data available.', loadId);
                });
                setPlotLastUpdated('lbl', payloadUpdatedDateLabel(data) || currentUtcDateLabel());
                if (activePlotKey) setPlotReloading(activePlotKey, false);
                lblPlotsState = 'loaded';
            })
            .catch(function () {
                if (activePlotKey) setPlotReloading(activePlotKey, false);
                lblPlotsState = 'idle';
            });
    }

    function updatePlotMaxLinks() {
        // Append vsys_ms to maximize link hrefs so the standalone page can use it
        var snrLink = document.getElementById('op-snr-plot-max-link');
        var bervLink = document.getElementById('op-berv-plot-max-link');
        var specLink = document.getElementById('op-spec-plot-max-link');
        var ccfRvLink = document.getElementById('op-ccf-rv-plot-max-link');
        var ccfProfileLink = document.getElementById('op-ccf-profile-plot-max-link');
        var suffix = '';
        if (vsysMs !== null && vsysMs !== undefined) {
            suffix += '?vsys_ms=' + encodeURIComponent(String(vsysMs));
        }
        if (ccfRangeFilter.mjdStart !== null && ccfRangeFilter.mjdStart !== undefined) {
            suffix += (suffix ? '&' : '?')
                + 'ccf_mjd_start=' + encodeURIComponent(String(ccfRangeFilter.mjdStart));
        }
        if (ccfRangeFilter.mjdEnd !== null && ccfRangeFilter.mjdEnd !== undefined) {
            suffix += (suffix ? '&' : '?')
                + 'ccf_mjd_end=' + encodeURIComponent(String(ccfRangeFilter.mjdEnd));
        }
        if (ccfRangeFilter.nobs !== null && ccfRangeFilter.nobs !== undefined) {
            suffix += (suffix ? '&' : '?')
                + 'ccf_nobs=' + encodeURIComponent(String(ccfRangeFilter.nobs));
        }
        if (snrLink) {
            var snrBase = cfg.snrMaxUrl || snrLink.getAttribute('href') || '';
            snrLink.href = snrBase.split('?')[0]
                + (vsysMs !== null && vsysMs !== undefined
                    ? '?vsys_ms=' + encodeURIComponent(String(vsysMs))
                    : '');
        }
        if (bervLink) {
            var bervBase = cfg.bervMaxUrl || bervLink.getAttribute('href') || '';
            bervLink.href = bervBase.split('?')[0]
                + (vsysMs !== null && vsysMs !== undefined
                    ? '?vsys_ms=' + encodeURIComponent(String(vsysMs))
                    : '');
        }
        if (specLink) {
            var specBase = cfg.specMaxUrl || specLink.getAttribute('href') || '';
            specLink.href = specBase.split('?')[0]
                + (vsysMs !== null && vsysMs !== undefined
                    ? '?vsys_ms=' + encodeURIComponent(String(vsysMs))
                    : '');
        }
        if (ccfRvLink) {
            var ccfRvBase = cfg.ccfRvMaxUrl || ccfRvLink.getAttribute('href') || '';
            ccfRvLink.href = ccfRvBase.split('?')[0];
        }
        if (ccfProfileLink) {
            var ccfProfBase = cfg.ccfProfileMaxUrl || ccfProfileLink.getAttribute('href') || '';
            ccfProfileLink.href = ccfProfBase.split('?')[0] + suffix;
        }
    }

    function triggerObjectDownload(kind, lblFormat) {
        var url = cfg.objectDownloadApiUrl
            || '/api/data-portal/object-download';
        var params = '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname)
            + '&kind=' + encodeURIComponent(kind);
        if (vsysMs !== null && vsysMs !== undefined) {
            params += '&vsys_ms=' + encodeURIComponent(String(vsysMs));
        }
        if (kind === 'ccf_profile') {
            if (ccfRangeFilter.mjdStart !== null
                    && ccfRangeFilter.mjdStart !== undefined) {
                params += '&ccf_mjd_start='
                    + encodeURIComponent(String(ccfRangeFilter.mjdStart));
            }
            if (ccfRangeFilter.mjdEnd !== null
                    && ccfRangeFilter.mjdEnd !== undefined) {
                params += '&ccf_mjd_end='
                    + encodeURIComponent(String(ccfRangeFilter.mjdEnd));
            }
            if (ccfRangeFilter.nobs !== null
                    && ccfRangeFilter.nobs !== undefined) {
                params += '&ccf_nobs='
                    + encodeURIComponent(String(ccfRangeFilter.nobs));
            }
        }
        if (kind === 'lbl' && lblFormat) {
            params += '&format=' + encodeURIComponent(lblFormat);
        }
        // Trigger a real browser download via a hidden anchor; lets
        // the server set Content-Disposition / filename.
        var a = document.createElement('a');
        a.href = url + params;
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        setTimeout(function () {
            try { document.body.removeChild(a); } catch (e) {}
        }, 0);
    }

    function loadObjectPlots(plotGroup, forceReload, activePlotKey) {
        var group = String(plotGroup || 'spectrum').trim().toLowerCase();
        if (!(group in objectPlotsState)) {
            return;
        }
        if (forceReload) {
            objectPlotsState[group] = 'idle';
        }
        if (objectPlotsState[group] === 'loading'
                || objectPlotsState[group] === 'loaded') {
            return;
        }
        objectPlotsState[group] = 'loading';
        var url = cfg.objectPlotsApiUrl;
        if (!url) {
            objectPlotsState[group] = 'idle';
            return;
        }

        var params = '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname)
            + '&plot_group=' + encodeURIComponent(group);
        // Forward the active ARI theme so server-side Bokeh figures
        // are themed to match the page chrome.
        try {
            var _theme = (document.documentElement.getAttribute(
                'data-theme') || 'default');
            params += '&theme=' + encodeURIComponent(_theme);
        } catch (_e) { /* ignore */ }
        if (vsysMs !== null && vsysMs !== undefined) {
            params += '&vsys_ms=' + encodeURIComponent(String(vsysMs));
        }
        if (group === 'ccf_profile') {
            if (ccfRangeFilter.mjdStart !== null && ccfRangeFilter.mjdStart !== undefined) {
                params += '&ccf_mjd_start=' + encodeURIComponent(String(ccfRangeFilter.mjdStart));
            }
            if (ccfRangeFilter.mjdEnd !== null && ccfRangeFilter.mjdEnd !== undefined) {
                params += '&ccf_mjd_end=' + encodeURIComponent(String(ccfRangeFilter.mjdEnd));
            }
            if (ccfRangeFilter.nobs !== null && ccfRangeFilter.nobs !== undefined) {
                params += '&ccf_nobs=' + encodeURIComponent(String(ccfRangeFilter.nobs));
            }
        }
        if (forceReload) {
            params += '&_ts=' + encodeURIComponent(String(Date.now()));
        }

        fetch(url + params)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    if (activePlotKey) setPlotReloading(activePlotKey, false);
                    objectPlotsState[group] = 'idle';
                    return;
                }
                if (group === 'spectrum') {
                    renderSnrPlot(data.snr || null);
                    renderBervPlot(data.berv || null);
                    renderSpecPlot(data.spec || null);
                } else if (group === 'ccf_rv') {
                    renderCcfRvPlot(data.ccf_rv || null);
                } else if (group === 'ccf_profile') {
                    renderCcfProfilePlot(data.ccf_profile || data.ccf || null);
                } else if (group === 'time_series') {
                    renderTsSnrPlot(data.ts_snr || null);
                    renderTsAirmassPlot(data.ts_airmass || null);
                } else if (group === 'target_info') {
                    renderSedPlot(data.sed || null);
                    renderHrPlot(data.hr || null);
                }
                var updated = payloadUpdatedDateLabel(data) || currentUtcDateLabel();
                if (group === 'spectrum') {
                    ['snr', 'berv', 'spec'].forEach(function (k) { setPlotLastUpdated(k, updated); });
                } else if (group === 'ccf_rv') {
                    setPlotLastUpdated('ccf_rv', updated);
                } else if (group === 'ccf_profile') {
                    setPlotLastUpdated('ccf_profile', updated);
                } else if (group === 'time_series') {
                    ['ts_snr', 'ts_airmass'].forEach(function (k) { setPlotLastUpdated(k, updated); });
                } else if (group === 'target_info') {
                    ['sed', 'hr'].forEach(function (k) { setPlotLastUpdated(k, updated); });
                } else {
                    setGroupLastUpdated(group);
                }
                if (activePlotKey) setPlotReloading(activePlotKey, false);
                refreshSectionsUi();
                objectPlotsState[group] = 'loaded';
            })
            .catch(function () {
                if (activePlotKey) setPlotReloading(activePlotKey, false);
                objectPlotsState[group] = 'idle';
                function markUnavailable(id) {
                    var el = document.getElementById(id);
                    if (el) {
                        el.innerHTML = '<span class="at-muted-hint">Plot unavailable.</span>';
                    }
                }
                if (group === 'spectrum') {
                    markUnavailable('op-snr-plot-loading');
                    markUnavailable('op-berv-plot-loading');
                    markUnavailable('op-spec-plot-loading');
                } else if (group === 'ccf_rv') {
                    markUnavailable('op-ccf-rv-plot-loading');
                } else if (group === 'ccf_profile') {
                    markUnavailable('op-ccf-plot-loading');
                } else if (group === 'time_series') {
                    markUnavailable('op-ts-snr-plot-loading');
                    markUnavailable('op-ts-airmass-plot-loading');
                }
            });
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
                dynamicLabels = data.labels || {};
                loadingEl.style.display = 'none';
                errorEl.style.display = 'none';

                // Refresh basket counter badge
                if (typeof window.ARI_BASKET_CFG !== 'undefined' && window.ARI_BASKET_CFG.summaryApiUrl) {
                    fetch(window.ARI_BASKET_CFG.summaryApiUrl)
                        .then(function (r) { return r.json(); })
                        .then(function (bd) {
                            if (!bd.success) return;
                            var cnt = bd.accessible_files || 0;
                            var badge = document.getElementById('op-basket-count');
                            if (badge) badge.textContent = cnt > 0 ? String(cnt) : '';
                            var dlCount = document.getElementById('op-dl-count');
                            if (dlCount) dlCount.textContent = String(cnt);
                            var dlSize = document.getElementById('op-dl-size');
                            if (dlSize) {
                                var bytes = bd.total_size_bytes || 0;
                                dlSize.textContent = bytes >= 1073741824
                                    ? (bytes / 1073741824).toFixed(1) + ' GB'
                                    : bytes >= 1048576
                                    ? (bytes / 1048576).toFixed(1) + ' MB'
                                    : bytes + ' B';
                            }
                            var dlLink = document.getElementById('op-dl-basket-link');
                            if (dlLink && window.ARI_BASKET_CFG.basketPageUrl) {
                                dlLink.href = window.ARI_BASKET_CFG.basketPageUrl;
                            }
                        })
                        .catch(function () {});
                }

                if (tsSnrYHead) {
                    tsSnrYHead.textContent = getLabel('time_series.snr_order_15', 'SNR[Order 15]');
                }
                if (tsSnrHHead) {
                    tsSnrHHead.textContent = getLabel('time_series.snr_order_60', 'SNR[Order 60]');
                }

                updatedEl.innerHTML = '<i class="fa-solid fa-clock"></i> Last updated: '
                    + escHtml(formatDate(data.generated_at));

                var pageUpdated = payloadUpdatedDateLabel(data);
                if (pageUpdated) {
                    ['snr', 'berv', 'spec', 'ccf', 'ts_snr', 'ts_airmass', 'lbl'].forEach(function (k) {
                        setPlotLastUpdated(k, pageUpdated);
                    });
                    ['ccf_rv', 'ccf_profile'].forEach(function (k) {
                        setPlotLastUpdated(k, pageUpdated);
                    });
                    debugPlotKeys.forEach(function (k) {
                        setPlotLastUpdated('debug_' + k, pageUpdated);
                    });
                }

                var s = data.sections || {};
                // Extract systemic velocity (m/s) for BERV plot computation
                if (s.lbl && s.lbl.vsys_ms !== null && s.lbl.vsys_ms !== undefined) {
                    vsysMs = s.lbl.vsys_ms;
                }
                updatePlotMaxLinks();
                renderTarget(s.target_info || {});
                renderSpectrum(s.spectrum || {});
                renderLbl(s.lbl || {});
                renderCcf(s.ccf || {});
                renderTimeSeries(s.time_series || []);
                refreshSectionsUi();
                // Plot payloads now load lazily when their tab is activated.
                ensurePlotsForTab('target_info');
                startBackgroundPlotPrefetch();
            })
            .catch(function (err) {
                showError('Network error: ' + String(err));
            });
    }

    function init() {
        persistLastObjectPage();
        syncLastOpenedObject();
        refreshTabOrderMap();
        bindTabs();
        bindCcfRangeControls();
        bindTimeSeriesDualScroll();
        activateTab('target_info');
        if (targetCsvBtn) {
            targetCsvBtn.addEventListener('click', downloadTargetCsv);
        }
        if (spectrumCsvBtn) {
            spectrumCsvBtn.addEventListener('click', downloadSpectrumCsv);
        }
        // LBL CSV buttons are wired per-flavor inside renderLbl()
        if (ccfCsvBtn) {
            ccfCsvBtn.addEventListener('click', downloadCcfCsv);
        }
        if (tsCsvBtn) {
            tsCsvBtn.addEventListener('click', downloadTimeSeriesCsv);
        }
        if (debugCsvBtn) {
            debugCsvBtn.addEventListener('click', downloadDebugCsv);
        }
        if (finderGenerateBtn) {
            if (cfg.finderChartCached) {
                loadFinderCharts(false);
            } else {
                finderGenerateBtn.addEventListener(
                    'click', function () {
                        loadFinderCharts(false);
                    }
                );
            }
        }
        if (finderRegen) {
            finderRegen.addEventListener(
                'click', function () {
                    loadFinderCharts(true);
                }
            );
        }
        if (tessGenerateBtn) {
            if (cfg.tessRotationCached) {
                loadTessRotation();
            } else {
                tessGenerateBtn.addEventListener(
                    'click', function () {
                        loadTessRotation(false);
                    }
                );
            }
        }
        wireVerifyBanner();
        // Delegated download-button handler for plot CSV/zip downloads.
        document.addEventListener('click', function (evt) {
            var btn = evt.target && evt.target.closest
                ? evt.target.closest('[data-op-download]')
                : null;
            if (!btn) return;
            evt.preventDefault();
            triggerObjectDownload(
                btn.getAttribute('data-op-download'),
                btn.getAttribute('data-op-lbl-format') || ''
            );
        });
        loadSectionPrefs().finally(function () {
            refreshSectionsUi();
            loadData();
        });
    }

    function _hasMonitorPerm(perms, instrument) {
        if (!Array.isArray(perms)) return false;
        if (perms.indexOf('manage.astrometrics') !== -1) return true;
        var inst = String(instrument || '').trim().toLowerCase();
        if (!inst) return false;
        var prefixes = [
            'monitor.', 'view.monitor_portal.', 'view.monitor.'
        ];
        for (var i = 0; i < perms.length; i++) {
            var p = String(perms[i] || '').toLowerCase();
            if (p === 'monitor') return true;
            for (var k = 0; k < prefixes.length; k++) {
                var pre = prefixes[k];
                if (p.indexOf(pre) === 0) {
                    var tail = p.substring(pre.length);
                    if (tail === inst || tail === 'all') return true;
                }
            }
        }
        return false;
    }

    function wireVerifyBanner() {
        var banner = document.getElementById('op-verify-banner');
        var btn = document.getElementById('op-verify-btn');
        if (!banner || !btn) return;
        var perms = (window.AperoRI && window.AperoRI.userPerms) || [];
        var instrument = banner.getAttribute('data-instrument') || '';
        var hasPerm = _hasMonitorPerm(perms, instrument);
        var name = String(cfg.objname || '').trim();
        if (!name) return;
        var url = '/api/astrometrics/status?name='
            + encodeURIComponent(name);
        fetch(url, { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .catch(function () { return null; })
            .then(function (data) {
                if (!data || !data.success) return;
                var status = String(data.status || '').toLowerCase();
                if (status !== 'pending') return;
                var aperoName = data.apero_name || name;
                banner.setAttribute('data-apero-name', aperoName);
                banner.style.display = '';
                if (hasPerm) {
                    btn.hidden = false;
                    btn.addEventListener('click', function () {
                        _onVerifyClick(banner, btn, aperoName,
                                       instrument);
                    });
                }
            });
    }

    function _onVerifyClick(banner, btn, aperoName, instrument) {
        var msg = ('You must have checked all the parameters and '
                   + 'see that they look suitable.\n\nMark '
                   + aperoName + ' as VERIFIED?');
        if (!window.confirm(msg)) return;
        btn.disabled = true;
        var origHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin">'
            + '</i> Verifying...';
        fetch('/api/astrometrics/verify', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                apero_name: aperoName,
                instrument: instrument
            })
        }).then(function (r) {
            return r.json().then(function (j) {
                return { ok: r.ok, json: j };
            });
        }).then(function (res) {
            if (!res.ok || !res.json || !res.json.success) {
                var err = (res.json && res.json.error)
                    || 'Verify failed';
                window.alert('Verify failed: ' + err);
                btn.disabled = false;
                btn.innerHTML = origHtml;
                return;
            }
            banner.style.display = 'none';
            // refresh target_info so any cached payload is rebuilt
            try { loadObjectPlots('target_info', true); }
            catch (e) { /* non-fatal */ }
        }).catch(function (err) {
            window.alert('Verify failed: ' + err);
            btn.disabled = false;
            btn.innerHTML = origHtml;
        });
    }

    init();

    // ------------------------------------------------------------------
    // Theme-change reload: when the user toggles dark/light/default the
    // server-rendered Bokeh figures need to be rebuilt with the new
    // palette. Invalidate every plot group's state and re-trigger the
    // currently-visible groups.
    // ------------------------------------------------------------------
    window.addEventListener('ari:theme-change', function () {
        try {
            Object.keys(objectPlotsState).forEach(function (g) {
                objectPlotsState[g] = 'idle';
            });
            embeddedPlots = {};
            pendingPlotEmbeds = {};
            // Re-fetch every group; loadObjectPlots will no-op for
            // groups that have already been loaded with the prior
            // theme (state is now 'idle' so they reload).
            ['spectrum', 'ccf_rv', 'ccf_profile',
             'time_series', 'target_info'].forEach(function (g) {
                try { loadObjectPlots(g, true); } catch (_e) {}
            });
        } catch (_err) { /* non-fatal */ }
    });
})();
