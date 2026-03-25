/* ==========================================================================
   Quality-control graphs page logic
   ========================================================================== */
(function () {
    'use strict';

    var PAGE_KEY = 'ari.qc';

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
            : '<i class="fa-regular fa-thumbtack"></i>';
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
                });
            });
        });
    }

    function bindPlotMaximize() {
        document.querySelectorAll('a.qc-plot-max').forEach(function (link, idx) {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                var href = link.getAttribute('href') || '';
                if (!href) return;
                var name = 'qcPlotMax_' + String(idx);
                var features = [
                    'width=1400',
                    'height=900',
                    'resizable=yes',
                    'scrollbars=yes'
                ].join(',');
                var win = window.open(href, name, features);
                if (win) {
                    win.focus();
                } else {
                    window.location.href = href;
                }
            });
        });
    }

    function init() {
        bindSectionFilter();
        bindSectionCollapse();
        bindSectionPins();
        bindMetricTabs();
        bindPlotMaximize();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
