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
    var finderChartEl = document.getElementById('op-finder-chart');
    var finderGenerateBtn = document.getElementById('op-finder-generate-btn');
    var finderLoading = document.getElementById('op-finder-loading');
    var finderError = document.getElementById('op-finder-error');
    var finderImages = document.getElementById('op-finder-images');
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
    };
    var lblPlotsState     = 'idle';   // idle | loading | loaded
    var debugPlotsState   = 'idle';   // idle | loading | loaded
    var backgroundPrefetchStarted = false;
    var plotLastUpdatedByKey = {};
    var plotReloadingByKey = {};
    var yAxisZoomByDiv = {};
    var yAxisRetryByDiv = {};

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

    function getContainerFigures(containerEl) {
        if (!containerEl || !window.Bokeh || !Bokeh.index) return [];
        var views = [];
        Object.keys(Bokeh.index).forEach(function (k) {
            var view = Bokeh.index[k];
            if (!view || !view.model || !view.el) return;
            if (!containerEl.contains(view.el)) return;
            var model = view.model;
            if (!model.y_range || !Array.isArray(model.renderers)) return;
            views.push(view);
        });
        return views;
    }

    function ensureYAxisControl(divId) {
        var plotDiv = document.getElementById(divId);
        if (!plotDiv) return;
        var host = plotDiv.parentElement;
        if (!host) return;
        if (host.querySelector('.op-yzoom-control[data-op-target="' + divId + '"]')) return;

        var bar = document.createElement('div');
        bar.className = 'op-yzoom-control';
        bar.setAttribute('data-op-target', divId);
        bar.innerHTML = ''
            + '<label class="op-yzoom-control__label">'
            + 'y-axis zoom:'
            + '<select class="op-yzoom-control__select">'
            + '<option value="3sig" selected>3 sig</option>'
            + '<option value="5sig">5 sig</option>'
            + '<option value="10sig">10 sig</option>'
            + '<option value="full">full</option>'
            + '</select>'
            + '</label>'
            + '<span class="op-yzoom-control__status" aria-live="polite"></span>';
        host.insertBefore(bar, plotDiv);

        var sel = bar.querySelector('.op-yzoom-control__select');
        if (sel) {
            sel.addEventListener('change', function () {
                yAxisZoomByDiv[divId] = sel.value;
                applyYAxisZoom(divId);
            });
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

        var sigMul = 3;
        if (mode === '5sig') sigMul = 5;
        if (mode === '10sig') sigMul = 10;

        var totalAbove = 0;
        var totalBelow = 0;
        figures.forEach(function (view) {
            var fig = view.model;
            var series = figureSeries(fig);
            var ys = series.ys;
            if (!ys.length) return;
            var yMin = Math.min.apply(null, ys);
            var yMax = Math.max.apply(null, ys);
            var lo = yMin;
            var hi = yMax;

            if (mode !== 'full') {
                var med = median(ys);
                var sig = stdDev(ys, med);
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
            loadObjectPlots('spectrum');
            loadObjectPlots('ccf_rv');
            loadObjectPlots('ccf_profile');
            loadObjectPlots('time_series');
            if (lblPlotsState === 'idle') loadLblPlots();
            if (debugPlotsState === 'idle') loadDebugPlots();
            return;
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
            return;
        }

        var controls = document.createElement('div');
        controls.className = 'op-section-controls';

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
            setSectionCollapsed(cardEl, !isCollapsed);
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
                setSectionCollapsed(cardEl, !isCollapsed);
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
            setSectionCollapsed(meta.card, !isSectionPinned(meta.id));
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
                sectionPinned = Array.isArray(payload.pinned) ? payload.pinned : [];
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
        var rows = [
            ['Target Name', target.object_name],
            ['RA', valOrDash(target.ra_deg) + ' [deg] (' + valOrDash(target.ra_source) + ')'],
            ['Dec', valOrDash(target.dec_deg) + ' [deg] (' + valOrDash(target.dec_source) + ')'],
            ['Teff', valOrDash(target.teff_k) + ' [K] (' + valOrDash(target.teff_source) + ')'],
            ['Spectral Type', valOrDash(target.spectral_type) + ' (' + valOrDash(target.spectral_type_source) + ')'],
            ['Proper Motion (RA)', valOrDash(target.pmra) + ' [mas/yr]'],
            ['Proper Motion (Dec)', valOrDash(target.pmdec) + ' [mas/yr]'],
            ['Parallax', valOrDash(target.parallax) + ' [mas]'],
            ['Radial Velocity', valOrDash(target.radial_velocity) + ' [km/s] (' + valOrDash(target.radial_velocity_source) + ')'],
            { label: 'Aliases', value: target.aliases, filterable: true },
            { label: 'OBJECT name(s) in headers', value: target.object_names_in_headers, filterable: true },
            { label: getLabel('target_info.ob_names_in_headers', 'OB Name(s) in headers'), value: target.ob_names_in_headers, filterable: true },
            { label: getLabel('target_info.pi_names_in_headers', 'PI name(s) in header'), value: target.pi_names_in_headers, filterable: true },
            { label: 'Project/Run name(s) in headers', value: target.project_run_names_in_headers, filterable: true }
        ];

        renderKvGrid(targetGrid, rows);
    }

    /* ------------------------------------------------------------------
       Finder chart generation (on-demand)
    ------------------------------------------------------------------ */
    function loadFinderCharts() {
        var url = cfg.finderChartApiUrl;
        if (!url) return;
        if (finderGenerateBtn) finderGenerateBtn.style.display = 'none';
        if (finderLoading) finderLoading.style.display = '';
        if (finderError) finderError.style.display = 'none';
        if (finderImages) finderImages.style.display = 'none';

        var params = '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname);
        fetch(url + params)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (finderLoading) finderLoading.style.display = 'none';
                if (!data || !data.success) {
                    if (finderError) {
                        finderError.textContent = data && data.error
                            ? data.error : 'Failed to generate finder charts.';
                        finderError.style.display = '';
                    }
                    if (finderGenerateBtn) finderGenerateBtn.style.display = '';
                    return;
                }
                renderFinderImages(data.images || [], data.bands || [],
                                   data.titles || []);
            })
            .catch(function (err) {
                if (finderLoading) finderLoading.style.display = 'none';
                if (finderError) {
                    finderError.textContent = 'Network error: ' + String(err);
                    finderError.style.display = '';
                }
                if (finderGenerateBtn) finderGenerateBtn.style.display = '';
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
        var rows = [
            ['DPRTYPES', spec.dprtypes],
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
                    '<i class="fa-solid fa-download"></i> CSV' +
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
                + '<a href="' + lblMaxHref + '" '
                + 'class="ari-btn ari-btn--sm ari-btn--secondary op-plot-max-btn" '
                + 'title="Maximize plot" style="margin-left:auto;">'
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
                loadFinderCharts();
            } else {
                finderGenerateBtn.addEventListener('click', loadFinderCharts);
            }
        }
        loadSectionPrefs().finally(function () {
            refreshSectionsUi();
            loadData();
        });
    }

    init();
})();
