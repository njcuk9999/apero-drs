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
    var tsBody = document.getElementById('op-time-series-tbody');
    var allSectionsHost = document.getElementById('op-all-sections');
    var allPinnedReorder = document.getElementById('op-all-pinned-reorder');
    var debugLoading = document.getElementById('op-debug-loading');
    var debugError = document.getElementById('op-debug-error');
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

    /* ------------------------------------------------------------------
       Deferred Bokeh embedding  (components-based)
       The server returns {script, div} from Bokeh components().
       When the container is visible we inject immediately; when hidden
       (e.g. inactive tab) we store the payload and inject later so the
       plot gets a proper width on first render.
    ------------------------------------------------------------------ */
    var pendingPlotEmbeds = {};   // { divId: { script, div } }
    var embeddedPlots     = {};   // divId -> true once injected

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

    function activateTab(tabKey) {
        document.querySelectorAll('#op-tabs .ari-sg-tab').forEach(function (btn) {
            btn.classList.toggle('ari-sg-tab--active', btn.dataset.tab === tabKey);
        });
        document.querySelectorAll('.op-tab-panel').forEach(function (panel) {
            panel.style.display = (panel.id === 'op-tab-' + tabKey) ? '' : 'none';
        });
        applySectionFilter(tabKey);
        // Notify lazy-loading tab modules (e.g. file_browser.js)
        document.dispatchEvent(new CustomEvent('ARI_TAB_ACTIVATED', {detail: {tabKey: tabKey}}));
        // Flush deferred Bokeh embeds for now-visible containers, then
        // fire resize so existing stretch_width plots re-measure.
        setTimeout(function () {
            flushPendingEmbeds();
            window.dispatchEvent(new Event('resize'));
        }, 60);
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

        // Move existing CSV download button into the controls group
        var csvBtn = header.querySelector('button.ari-btn');
        if (csvBtn) {
            csvBtn.style.marginLeft = '';
            csvBtn.classList.remove('ari-btn--sm');
            csvBtn.classList.remove('ari-btn--secondary');
            csvBtn.classList.remove('ari-btn');
            csvBtn.classList.add('op-section-btn');
            csvBtn.classList.add('op-section-btn--csv');
            controls.appendChild(csvBtn);
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
        if (!allSectionsHost) return;
        var allPanel = document.getElementById('op-tab-all');
        if (!allPanel) return;
        if (allPanel.querySelector('.op-section-search')) return;

        var wrap = document.createElement('div');
        wrap.className = 'op-section-search';
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

        var hostParent = allSectionsHost.parentElement;
        if (hostParent) {
            hostParent.insertBefore(wrap, allSectionsHost);
        }
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
            setSectionCollapsed(meta.card, false);
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
            if (!allSectionsHost) return;
            allSectionsHost.querySelectorAll('.at-section-card[data-op-origin-id]').forEach(function (card) {
                var sid = card.getAttribute('data-op-origin-id') || '';
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
        rebuildAllSections(cards);
        renderPinnedReorder(cards);
        updatePinnedButtons();

        var tabKeys = {};
        cards.forEach(function (c) { tabKeys[c.tabKey] = true; });
        Object.keys(tabKeys).forEach(function (tabKey) {
            applySectionFilter(tabKey);
        });
        applySectionFilter('all');
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
       Debug plot generation (auto-loaded)
    ------------------------------------------------------------------ */
    var debugPlotKeys = ['extsmax', 'effron', 'version', 'cdt', 'tcorr_map'];

    function loadDebugPlots() {
        var url = cfg.debugPlotsApiUrl;
        if (!url) return;
        if (debugLoading) debugLoading.style.display = '';
        if (debugError) debugError.style.display = 'none';

        var params = '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname);
        fetch(url + params)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (debugLoading) debugLoading.style.display = 'none';
                if (!data || !data.success) {
                    if (debugError) {
                        debugError.textContent = data && data.error
                            ? data.error : 'Failed to generate debug plots.';
                        debugError.style.display = '';
                    }
                    return;
                }
                renderDebugPlots(data.plots || {});
            })
            .catch(function (err) {
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
            var cssKey = key.replace(/_/g, '-');
            var plotDiv = document.getElementById('op-debug-' + cssKey + '-div');
            var info = plots[key];
            var loadingEl = document.getElementById('op-debug-' + cssKey + '-loading');
            if (loadingEl) loadingEl.style.display = 'none';
            if (!plotDiv) continue;
            if (!info || !info.has_plot || !info.image) {
                plotDiv.innerHTML = '<div class="at-muted-hint">'
                    + escHtml(info && info.error ? info.error : 'No data available')
                    + '</div>';
                continue;
            }
            var maxH = (key === 'cdt' || key === 'tcorr_map') ? '700px' : '400px';
            plotDiv.innerHTML = '<img src="data:image/png;base64,' + info.image
                + '" alt="' + escHtml(info.title || key) + '" '
                + 'style="width:100%;max-height:' + maxH + ';object-fit:contain;'
                + 'border-radius:0.4rem;'
                + 'border:1px solid var(--op-border,#d6d9de);">';
        }
    }

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

    function renderCcfPlot(payload) {
        embedOrDefer('op-ccf-plot-div', payload, 'No CCF data available.');
    }

    function renderTsSnrPlot(payload) {
        embedOrDefer('op-ts-snr-plot-div', payload, 'No per-night SNR data available.');
    }

    function renderTsAirmassPlot(payload) {
        embedOrDefer('op-ts-airmass-plot-div', payload, 'No per-night airmass data available.');
    }

    function loadLblPlots() {
        var url = cfg.objectLblPlotsApiUrl;
        if (!url) return;
        var params = '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname);
        fetch(url + params)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success || !data.plots) return;
                Object.keys(data.plots).forEach(function (rdb_filename) {
                    var payload = data.plots[rdb_filename];
                    var m = rdb_filename.match(/^lbl_(.+)\.rdb$/i);
                    var flavor_id = m ? m[1] : rdb_filename;
                    var sidToken = sanitizeSectionToken(flavor_id);
                    var divId = 'op-lbl-vel-plot-' + sidToken;
                    var loadId = 'op-lbl-vel-loading-' + sidToken;
                    embedOrDefer(divId, payload, 'No LBL data available.', loadId);
                });
            })
            .catch(function () {});
    }

    function updatePlotMaxLinks() {
        // Append vsys_ms to maximize link hrefs so the standalone page can use it
        if (vsysMs === null || vsysMs === undefined) return;
        var snrLink = document.getElementById('op-snr-plot-max-link');
        var bervLink = document.getElementById('op-berv-plot-max-link');
        var specLink = document.getElementById('op-spec-plot-max-link');
        var ccfLink = document.getElementById('op-ccf-plot-max-link');
        var suffix = '?vsys_ms=' + encodeURIComponent(String(vsysMs));
        if (snrLink) {
            var snrBase = cfg.snrMaxUrl || snrLink.getAttribute('href') || '';
            snrLink.href = snrBase.split('?')[0] + suffix;
        }
        if (bervLink) {
            var bervBase = cfg.bervMaxUrl || bervLink.getAttribute('href') || '';
            bervLink.href = bervBase.split('?')[0] + suffix;
        }
        if (specLink) {
            var specBase = cfg.specMaxUrl || specLink.getAttribute('href') || '';
            specLink.href = specBase.split('?')[0] + suffix;
        }
        if (ccfLink) {
            var ccfBase = cfg.ccfMaxUrl || ccfLink.getAttribute('href') || '';
            ccfLink.href = ccfBase.split('?')[0] + suffix;
        }
    }

    function loadObjectPlots() {
        var url = cfg.objectPlotsApiUrl;
        if (!url) return;

        var params = '?profile_id=' + encodeURIComponent(cfg.profileId)
            + '&objname=' + encodeURIComponent(cfg.objname);
        if (vsysMs !== null && vsysMs !== undefined) {
            params += '&vsys_ms=' + encodeURIComponent(String(vsysMs));
        }

        fetch(url + params)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) return;
                renderSnrPlot(data.snr || null);
                renderBervPlot(data.berv || null);
                renderSpecPlot(data.spec || null);
                renderCcfPlot(data.ccf || null);
                renderTsSnrPlot(data.ts_snr || null);
                renderTsAirmassPlot(data.ts_airmass || null);
                refreshSectionsUi();
            })
            .catch(function () {
                // Silently hide loading spinners on error
                var snrLoading = document.getElementById('op-snr-plot-loading');
                var bervLoading = document.getElementById('op-berv-plot-loading');
                var specLoading = document.getElementById('op-spec-plot-loading');
                var ccfLoading = document.getElementById('op-ccf-plot-loading');
                var tsSnrLoading = document.getElementById('op-ts-snr-plot-loading');
                var tsAirmassLoading = document.getElementById('op-ts-airmass-plot-loading');
                if (snrLoading) snrLoading.innerHTML = '<span class="at-muted-hint">Plot unavailable.</span>';
                if (bervLoading) bervLoading.innerHTML = '<span class="at-muted-hint">Plot unavailable.</span>';
                if (specLoading) specLoading.innerHTML = '<span class="at-muted-hint">Plot unavailable.</span>';
                if (ccfLoading) ccfLoading.innerHTML = '<span class="at-muted-hint">Plot unavailable.</span>';
                if (tsSnrLoading) tsSnrLoading.innerHTML = '<span class="at-muted-hint">Plot unavailable.</span>';
                if (tsAirmassLoading) tsAirmassLoading.innerHTML = '<span class="at-muted-hint">Plot unavailable.</span>';
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
                // Load plots after main data is ready
                loadObjectPlots();
                loadLblPlots();
                loadDebugPlots();
            })
            .catch(function (err) {
                showError('Network error: ' + String(err));
            });
    }

    function init() {
        persistLastObjectPage();
        refreshTabOrderMap();
        bindTabs();
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
