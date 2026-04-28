/* ==========================================================================
   Quality-control graphs page logic
   ========================================================================== */
(function () {
    'use strict';

    var PAGE_KEY = 'ari.qc';
    var qcZoomModeByDiv = {};
    var qcZoomRetryByDiv = {};

    function getProfileId() {
        var ctx = window.ARI_QC_PAGE || {};
        return String(ctx.profileId || 'default');
    }

    function pinnedStorageKey() {
        return PAGE_KEY + ':' + getProfileId() + ':pinned-sections';
    }

    function loadPinnedIds() {
        try {
            var raw = localStorage.getItem(pinnedStorageKey());
            if (!raw) return [];
            var parsed = JSON.parse(raw);
            if (!Array.isArray(parsed)) return [];
            return parsed.map(function (id) { return String(id); });
        } catch (_err) {
            return [];
        }
    }

    function savePinnedIds(ids) {
        try {
            localStorage.setItem(pinnedStorageKey(), JSON.stringify(ids));
        } catch (_err) {
            // Ignore storage failures.
        }
    }

    function isPinnedId(pinnedIds, id) {
        return pinnedIds.indexOf(id) !== -1;
    }

    function setSectionPinned(card, pinned) {
        if (!card) return;
        card.classList.toggle('op-section--pinned', !!pinned);
        var pinBtn = card.querySelector('.op-section-btn--pin');
        if (!pinBtn) return;
        pinBtn.classList.toggle('op-section-btn--active', !!pinned);
        pinBtn.title = pinned ? 'Unpin section' : 'Pin section to top';
        pinBtn.setAttribute('aria-label', pinBtn.title);
        pinBtn.innerHTML = pinned
            ? '<i class="fa-solid fa-thumbtack"></i>'
            : '<i class="fa-solid fa-thumbtack" style="transform:rotate(45deg);opacity:0.45"></i>';
    }

    function reorderPinnedSections() {
        var cards = Array.prototype.slice.call(document.querySelectorAll('.qc-section-card'));
        if (!cards.length) return;
        var container = cards[0].parentElement;
        if (!container) return;

        var pinned = cards.filter(function (card) {
            return card.classList.contains('op-section--pinned');
        });
        var unpinned = cards.filter(function (card) {
            return !card.classList.contains('op-section--pinned');
        });

        pinned.concat(unpinned).forEach(function (card) {
            container.appendChild(card);
        });
    }

    function setSectionCollapsed(card, collapsed) {
        if (!card) return;
        card.classList.toggle('op-section--collapsed', !!collapsed);
        var btn = card.querySelector('.qc-section-toggle');
        if (!btn) return;
        btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        btn.title = collapsed ? 'Expand section' : 'Collapse section';
        var icon = btn.querySelector('i');
        if (icon) {
            icon.className = 'fa-solid ' + (collapsed ? 'fa-chevron-down' : 'fa-chevron-up');
        }
    }

    function bindSectionFilter() {
        var input = document.getElementById('qc-section-filter');
        if (!input) return;

        function applyFilter() {
            var q = String(input.value || '').trim().toLowerCase();
            document.querySelectorAll('.qc-section-card').forEach(function (card) {
                var key = String(card.getAttribute('data-qc-section') || '').toLowerCase();
                var txt = String(card.textContent || '').toLowerCase();
                var show = !q || key.indexOf(q) !== -1 || txt.indexOf(q) !== -1;
                card.style.display = show ? '' : 'none';
            });
        }

        input.addEventListener('input', applyFilter);
        applyFilter();
    }

    function bindSectionCollapse() {
        document.querySelectorAll('.qc-section-card').forEach(function (card) {
            var btn = card.querySelector('.qc-section-toggle');
            if (!btn) return;

            btn.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                var card = btn.closest('.qc-section-card');
                if (!card) return;
                var collapsed = card.classList.contains('op-section--collapsed');
                setSectionCollapsed(card, !collapsed);
            });

            var header = card.querySelector('.at-section-card__header');
            if (!header) return;
            header.addEventListener('click', function (event) {
                var target = event.target;
                if (!(target instanceof Element)) return;
                if (target.closest('button, a, input, select, textarea, label, .qc-metric-tabs')) {
                    return;
                }
                var collapsed = card.classList.contains('op-section--collapsed');
                setSectionCollapsed(card, !collapsed);
            });
        });
    }

    function bindSectionPins() {
        var pinnedIds = loadPinnedIds();

        document.querySelectorAll('.qc-section-card').forEach(function (card) {
            var sectionId = String(card.getAttribute('data-qc-section-id') || '');
            if (sectionId) {
                setSectionPinned(card, isPinnedId(pinnedIds, sectionId));
            }

            var pinBtn = card.querySelector('.op-section-btn--pin');
            if (!pinBtn) return;
            pinBtn.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();

                if (!sectionId) return;
                if (isPinnedId(pinnedIds, sectionId)) {
                    pinnedIds = pinnedIds.filter(function (id) {
                        return id !== sectionId;
                    });
                } else {
                    pinnedIds.push(sectionId);
                }

                savePinnedIds(pinnedIds);
                setSectionPinned(card, isPinnedId(pinnedIds, sectionId));
                reorderPinnedSections();
            });
        });

        reorderPinnedSections();
    }

    function bindMetricTabs() {
        document.querySelectorAll('.qc-metric-tabs').forEach(function (tabWrap) {
            tabWrap.querySelectorAll('.qc-metric-tab').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    var target = btn.getAttribute('data-qc-target') || '';
                    if (!target) return;

                    tabWrap.querySelectorAll('.qc-metric-tab').forEach(function (b) {
                        b.classList.toggle('qc-metric-tab--active', b === btn);
                    });

                    var sectionBody = tabWrap.closest('.at-section-card__body');
                    if (!sectionBody) return;
                    sectionBody.querySelectorAll('.qc-metric-pane').forEach(function (pane) {
                        var paneId = pane.getAttribute('data-qc-pane') || '';
                        pane.classList.toggle('qc-metric-pane--active', paneId === target);
                    });

                    setTimeout(function () {
                        refreshVisibleQcZoom();
                    }, 80);
                });
            });
        });
    }

    function bindPlotMaximize() {
        /* Navigate in the same window; "Close and return" uses history.back() */
        document.querySelectorAll('a.qc-plot-max').forEach(function (link) {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                var href = link.getAttribute('href') || '';
                if (href) window.location.href = href;
            });
        });
    }

    function extractFieldName(spec) {
        if (typeof spec === 'string' && spec) return spec;
        if (!spec || typeof spec !== 'object') return '';
        if (typeof spec.field === 'string' && spec.field) return spec.field;
        return '';
    }

    function collectNumericValues(value, out) {
        if (Array.isArray(value)) {
            for (var i = 0; i < value.length; i += 1) {
                collectNumericValues(value[i], out);
            }
            return;
        }
        var num = Number(value);
        if (isFinite(num)) out.push(num);
    }

    function median(values) {
        if (!values.length) return null;
        var sorted = values.slice().sort(function (a, b) { return a - b; });
        var n = sorted.length;
        var m = Math.floor(n / 2);
        if ((n % 2) === 0) return 0.5 * (sorted[m - 1] + sorted[m]);
        return sorted[m];
    }

    function stdDev(values, center) {
        if (!values.length) return 0;
        var c = Number(center === null || center === undefined ? 0 : center);
        var sum = 0;
        for (var i = 0; i < values.length; i += 1) {
            var d = Number(values[i]) - c;
            sum += d * d;
        }
        return Math.sqrt(sum / values.length);
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

    function figureYs(figModel) {
        var ys = [];
        var renderers = Array.isArray(figModel.renderers) ? figModel.renderers : [];
        for (var i = 0; i < renderers.length; i += 1) {
            var r = renderers[i];
            if (!r || !r.glyph || !r.data_source || !r.data_source.data) continue;
            var data = r.data_source.data;
            ['y', 'top', 'bottom', 'y0', 'y1'].forEach(function (k) {
                var field = extractFieldName(r.glyph[k]);
                if (!field) return;
                if (!(field in data)) return;
                collectNumericValues(data[field], ys);
            });
        }
        return ys;
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
        var mode = String(qcZoomModeByDiv[divId] || '3sig');
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
            var ys = figureYs(fig);
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
        if (!applyYAxisZoom(divId)) {
            var n = Number(qcZoomRetryByDiv[divId] || 0);
            if (n >= 8) return;
            qcZoomRetryByDiv[divId] = n + 1;
            setTimeout(function () { applyYAxisZoomDeferred(divId); }, 140);
            return;
        }
        qcZoomRetryByDiv[divId] = 0;
    }

    function ensureYAxisControl(plotDiv) {
        if (!plotDiv || !plotDiv.id) return;
        var divId = String(plotDiv.id || '');
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
                qcZoomModeByDiv[divId] = sel.value;
                applyYAxisZoom(divId);
            });
        }
    }

    function initQcYAxisControls() {
        document.querySelectorAll('.qc-plot-card').forEach(function (card) {
            var plotDiv = card.querySelector('div[id]');
            if (!plotDiv) return;
            ensureYAxisControl(plotDiv);
            applyYAxisZoomDeferred(plotDiv.id);
        });
    }

    function refreshVisibleQcZoom() {
        document.querySelectorAll('.qc-metric-pane--active .qc-plot-card div[id]').forEach(function (plotDiv) {
            if (!plotDiv || !plotDiv.id) return;
            ensureYAxisControl(plotDiv);
            applyYAxisZoomDeferred(plotDiv.id);
        });
    }

    function init() {
        bindSectionFilter();
        bindSectionCollapse();
        bindSectionPins();
        bindMetricTabs();
        bindPlotMaximize();
        initQcYAxisControls();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
