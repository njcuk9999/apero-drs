/* eslint-disable no-undef */
/**
 * APERO RI - shared target-info section renderer.
 *
 * Renders the JSON payload produced by
 * apero_ri/components/target_info_sections.py into a container.
 * Used by:
 *   - the astrometrics page (Resolve target tab)
 *   - the data-portal object page (Target info tab)
 *
 * Public API exposed on window.AperoTargetInfo:
 *
 *   render(container, payload, opts)
 *     container : HTMLElement  -- where to render
 *     payload   : object       -- {sections: [...]}
 *     opts      : object       -- optional callbacks/state:
 *       - userPerms  : array<string> of perms the current user holds
 *       - apero_name : str canonical name used by edit endpoint
 *       - onEdit     : function(key, currentValue, row, sectionId)
 *                      called when the user clicks the edit pencil
 *       - onFlag     : function(key, currentValue, row, sectionId)
 *                      called when the user clicks the flag icon
 *       - mountChartsCb : function(sectionId, hostEl, chartType)
 *                      invoked once each chart card is in the DOM
 *
 *   applyPermissionVisibility(container, perms)
 *     Show/hide elements with data-perm based on the user's perms.
 *
 * Section behaviour:
 *   - Click the section header to collapse/expand the body.
 *   - Click the pin icon to pin/unpin the section to the top of
 *     the container (sticky positioning).
 *   - Long-list values (arrays with > FILTER_THRESHOLD entries)
 *     get an inline filter input.
 *   - Citations are numbered [1], [2], ... per payload and a
 *     footnote list is appended below each section that uses
 *     them.
 */
(function () {
    "use strict";

    // -----------------------------------------------------------------
    // PHASE 2 ANTI-REVERT GUARD.
    // If this file ever gets accidentally duplicated (a recurring
    // bug where the legacy plain-text renderer was appended to the
    // end of the file and overwrote window.AperoTargetInfo with a
    // white-text fallback), the second IIFE will hit this guard and
    // bail out immediately, leaving the rich card renderer in place.
    // DO NOT REMOVE. See /memories/repo for context.
    // -----------------------------------------------------------------
    if (window.__AperoTargetInfoLoaded) {
        if (window.console && window.console.warn) {
            window.console.warn(
                "AperoTargetInfo: duplicate target_info_render.js " +
                "load detected; ignoring (keeping rich renderer)."
            );
        }
        return;
    }
    window.__AperoTargetInfoLoaded = true;

    var FA_DEFAULT_DATA_ICON = "fa-solid fa-table-list";
    var FA_DEFAULT_CHART_ICON = "fa-solid fa-chart-area";
    var FILTER_THRESHOLD = 5;
    // localStorage key prefix for collapse state (per section id)
    var LS_COLLAPSE_PREFIX = "ari-tinfo-collapsed:";
    var LS_PIN_PREFIX = "ari-tinfo-pinned:";

    function escapeHtml(value) {
        if (value === null || value === undefined) return "";
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function isMissing(v) {
        if (v === null || v === undefined) return true;
        if (typeof v === "string" && v.trim() === "") return true;
        if (typeof v === "number" && !isFinite(v)) return true;
        return false;
    }

    // ---- citation registry -----------------------------------------
    // Numbered registry built per render() call so [1]..[N] are
    // stable and unique across the whole payload.
    function makeCitationRegistry() {
        var byText = {};
        var order = [];
        return {
            assign: function (text) {
                if (!text) return null;
                if (Object.prototype.hasOwnProperty.call(byText, text)) {
                    return byText[text];
                }
                var n = order.length + 1;
                byText[text] = n;
                order.push(text);
                return n;
            },
            list: function () { return order.slice(); }
        };
    }

    function formatScalar(v, precision) {
        if (typeof v === "number" && precision !== null
                && precision !== undefined) {
            try { return v.toFixed(precision); }
            catch (_) { return String(v); }
        }
        return String(v);
    }

    function formatValue(row) {
        var v = row.value;
        if (isMissing(v)) {
            return { html: "<em>no data</em>", missing: true,
                     isList: false, listItems: null };
        }
        if (Array.isArray(v)) {
            // long lists rendered as filterable chip-list (handled
            // separately so they get their own DOM container)
            return {
                html: "",
                missing: false,
                isList: true,
                listItems: v.slice()
            };
        }
        return { html: escapeHtml(formatScalar(v, row.precision)),
                 missing: false, isList: false, listItems: null };
    }

    // ---- per-row HTML builder --------------------------------------
    // Layout (single line, hover-reveals action icons):
    //   {label}[ref]: {value} {unit} (source) [edit] [flag]
    function makeRowHtml(row, sectionId, citeReg, rowIndex) {
        var fmt = formatValue(row);
        var labelHtml = escapeHtml(row.label || row.key || "");
        // numbered citation marker rendered next to the label
        if (row.citation_text) {
            var n = citeReg.assign(row.citation_text);
            if (n !== null) {
                labelHtml += ' <sup class="ari-tinfo-cite"'
                    + ' data-cite-n="' + n + '"'
                    + ' title="' + escapeHtml(row.citation_text) + '">'
                    + "[" + n + "]" + "</sup>";
            }
        }

        // build the value segment (everything after the colon)
        var valueInner;
        var isList = false;
        if (fmt.isList) {
            isList = true;
            var items = fmt.listItems;
            var filterable = items.length > FILTER_THRESHOLD;
            var listId = ("ari-list-" + sectionId + "-" + rowIndex)
                .replace(/[^a-z0-9_-]/gi, "_");
            var filterHtml = "";
            if (filterable) {
                filterHtml = ''
                    + '<input type="search" class="ari-tinfo-list-filter"'
                    + ' data-target-list="' + listId + '"'
                    + ' placeholder="Filter ' + items.length
                    + ' entries..."/>';
            }
            var chips = items.map(function (it) {
                return '<span class="ari-tinfo-chip">'
                    + escapeHtml(it) + "</span>";
            }).join("");
            valueInner = filterHtml
                + '<div class="ari-tinfo-chiplist" id="' + listId + '">'
                + chips
                + "</div>"
                + '<span class="ari-tinfo-list-count">'
                + items.length + " entries"
                + "</span>";
        } else {
            valueInner = '<span class="ari-tinfo-value">'
                + fmt.html + "</span>";
            if (row.units && !fmt.missing) {
                valueInner += ' <span class="ari-tinfo-units">'
                    + escapeHtml(row.units) + "</span>";
            }
            if (row.source) {
                valueInner += ' <span class="ari-tinfo-source"'
                    + ' title="Source">('
                    + escapeHtml(row.source) + ")</span>";
            }
        }

        // hover-reveal action buttons (icons only, fade in on row hover)
        var actions = "";
        if (row.editable) {
            actions += '<button type="button"'
                + ' class="ari-tinfo-row-btn ari-tinfo-edit-btn"'
                + ' data-edit-key="' + escapeHtml(row.key || "") + '"'
                + ' data-perm="manage.astrometrics" hidden'
                + ' title="Edit this value (moderators only)">'
                + '<i class="fa-solid fa-pen"></i></button>';
        }
        if (row.flaggable) {
            actions += '<button type="button"'
                + ' class="ari-tinfo-row-btn ari-tinfo-flag-btn"'
                + ' data-flag-key="' + escapeHtml(row.key || "") + '"'
                + ' title="Flag this value as wrong">'
                + '<i class="fa-solid fa-flag"></i></button>';
        }

        var rowClass = "ari-tinfo-row";
        if (isList) rowClass += " ari-tinfo-row--list";
        if (fmt.missing) rowClass += " ari-tinfo-row--missing";
        return ''
            + '<div class="' + rowClass + '"'
            + ' data-row-key="' + escapeHtml(row.key || "") + '">'
            + '<span class="ari-tinfo-row__label">'
            + labelHtml + ":</span>"
            + '<span class="ari-tinfo-row__value">'
            + valueInner + "</span>"
            + '<span class="ari-tinfo-row__actions">'
            + actions + "</span>"
            + "</div>";
    }

    // ---- citation footnote block -----------------------------------
    function makeCitesFooter(sectionCites) {
        if (!sectionCites.length) return "";
        var items = sectionCites.map(function (entry) {
            return '<li class="ari-tinfo-cite-item">'
                + '<span class="ari-tinfo-cite-n">[' + entry.n
                + "]</span> "
                + escapeHtml(entry.text)
                + "</li>";
        }).join("");
        return '<ol class="ari-tinfo-cites">' + items + "</ol>";
    }

    // collect citations used in this section's rows (in [n] order)
    function collectSectionCites(rows, citeReg) {
        var seen = {};
        var out = [];
        rows.forEach(function (row) {
            if (!row.citation_text) return;
            var n = citeReg.assign(row.citation_text);
            if (n === null) return;
            if (Object.prototype.hasOwnProperty.call(seen, n)) return;
            seen[n] = true;
            out.push({ n: n, text: row.citation_text });
        });
        out.sort(function (a, b) { return a.n - b.n; });
        return out;
    }

    function renderDataSection(section, citeReg) {
        var icon = section.icon || FA_DEFAULT_DATA_ICON;
        var rows = section.rows || [];
        var rowsHtml = rows.map(function (r, i) {
            return makeRowHtml(r, section.id, citeReg, i);
        }).join("");
        var desc = "";
        if (section.description) {
            desc = '<p class="ari-tinfo-section__desc">'
                + escapeHtml(section.description) + "</p>";
        }
        var citesHtml = makeCitesFooter(
            collectSectionCites(rows, citeReg));
        return wrapSection(section, icon, "data",
            desc + '<div class="ari-tinfo-rows">'
            + rowsHtml + "</div>" + citesHtml);
    }

    function renderChartSection(section) {
        var icon = section.icon || FA_DEFAULT_CHART_ICON;
        var chartId = section.chart_id
            || ("chart-" + (section.id || "x"));
        var ctype = section.chart_type || "";
        var desc = "";
        if (section.description) {
            desc = '<p class="ari-tinfo-section__desc">'
                + escapeHtml(section.description) + "</p>";
        }
        // No "Generate" button: charts auto-render on mount
        // (see bindDefaultChartActions). The status/error
        // affordances are still present so the renderer can
        // surface progress and errors inline.
        var widget = ''
            + '<div class="ari-tinfo-chart"'
            + ' id="' + escapeHtml(chartId) + '"'
            + ' data-chart-type="' + escapeHtml(ctype) + '">'
            + '<div class="ari-tinfo-chart__controls"'
            + ' style="display:flex; gap:0.5rem;'
            + ' align-items:center; margin-bottom:0.5rem;">'
            + '<span class="ari-tinfo-chart__status"'
            + ' data-chart-status'
            + ' style="color:var(--ari-text-muted);"></span>'
            + "</div>"
            + '<div class="ari-tinfo-chart__error"'
            + ' data-chart-error'
            + ' style="display:none; color:var(--ari-danger);'
            + ' margin-bottom:0.5rem;"></div>'
            + '<div class="ari-tinfo-chart__images"'
            + ' data-chart-images'
            + ' style="display:block; width:100%;"></div>'
            + '<details class="ari-tinfo-chart__log-wrap"'
            + ' data-chart-log-wrap style="display:none;'
            + ' margin-top:0.5rem;">'
            + '<summary>Log</summary>'
            + '<pre data-chart-log style="max-height:240px;'
            + ' overflow:auto; white-space:pre-wrap;'
            + ' background:var(--ari-bg-soft);'
            + ' padding:0.5rem; border-radius:4px;'
            + ' font-size:12px;"></pre>'
            + "</details>"
            + "</div>";
        return wrapSection(section, icon, "chart", desc + widget);
    }

    function wrapSection(section, icon, kind, body) {
        var collapsed = readBool(LS_COLLAPSE_PREFIX + section.id);
        var classes = ["ari-tinfo-section"];
        if (collapsed) classes.push("ari-tinfo-section--collapsed");
        var chartAttr = "";
        if (kind === "chart") {
            chartAttr = ' data-chart-type="'
                + escapeHtml(section.chart_type || "") + '"';
        }
        return ''
            + '<section class="' + classes.join(" ") + '"'
            + ' data-section-id="' + escapeHtml(section.id) + '"'
            + ' data-section-kind="' + kind + '"'
            + chartAttr + ">"
            + '<header class="ari-tinfo-section__header"'
            + ' data-section-toggle>'
            + '<i class="ari-tinfo-section__chevron'
            + ' fa-solid fa-chevron-down"></i>'
            + '<i class="' + escapeHtml(icon)
            + ' ari-tinfo-section__icon"></i>'
            + '<span class="ari-tinfo-section__title">'
            + escapeHtml(section.title) + "</span>"
            + "</header>"
            + '<div class="ari-tinfo-section__body">' + body + "</div>"
            + "</section>";
    }

    function readBool(key) {
        try {
            return window.localStorage.getItem(key) === "1";
        } catch (_) { return false; }
    }

    function writeBool(key, val) {
        try {
            if (val) window.localStorage.setItem(key, "1");
            else window.localStorage.removeItem(key);
        } catch (_) { /* ignore */ }
    }

    // ---- interactive bindings --------------------------------------
    function bindSectionInteractions(container, opts) {
        // collapse / expand on header click (but not pin button)
        container.addEventListener("click", function (ev) {
            var pinBtn = ev.target.closest("[data-section-pin]");
            if (pinBtn) {
                var sec = pinBtn.closest(".ari-tinfo-section");
                if (!sec) return;
                var id = sec.getAttribute("data-section-id");
                var nowPinned = !sec.classList.contains(
                    "ari-tinfo-section--pinned");
                sec.classList.toggle(
                    "ari-tinfo-section--pinned", nowPinned);
                pinBtn.setAttribute("title",
                    nowPinned ? "Unpin" : "Pin to top");
                writeBool(LS_PIN_PREFIX + id, nowPinned);
                ev.stopPropagation();
                return;
            }
            var hdr = ev.target.closest("[data-section-toggle]");
            if (!hdr) return;
            // ignore clicks inside row buttons/inputs
            if (ev.target.closest("button, input, a")) return;
            var section = hdr.closest(".ari-tinfo-section");
            if (!section) return;
            var sid = section.getAttribute("data-section-id");
            var nowCol = !section.classList.contains(
                "ari-tinfo-section--collapsed");
            section.classList.toggle(
                "ari-tinfo-section--collapsed", nowCol);
            writeBool(LS_COLLAPSE_PREFIX + sid, nowCol);
        });

        // long-list filter inputs
        container.addEventListener("input", function (ev) {
            var inp = ev.target.closest(".ari-tinfo-list-filter");
            if (!inp) return;
            var listId = inp.getAttribute("data-target-list");
            var list = container.querySelector("#" + CSS.escape(listId));
            if (!list) return;
            var needle = inp.value.trim().toLowerCase();
            var chips = list.querySelectorAll(".ari-tinfo-chip");
            var shown = 0;
            chips.forEach(function (chip) {
                var hay = chip.textContent.toLowerCase();
                var match = !needle || hay.indexOf(needle) >= 0;
                chip.style.display = match ? "" : "none";
                if (match) shown += 1;
            });
            var counter = inp.parentElement.querySelector(
                ".ari-tinfo-list-count");
            if (counter) {
                counter.textContent = shown + " / " + chips.length
                    + " entries";
            }
        });

        // edit button click
        container.addEventListener("click", function (ev) {
            var btn = ev.target.closest(".ari-tinfo-edit-btn");
            if (!btn) return;
            ev.stopPropagation();
            ev.preventDefault();
            var key = btn.getAttribute("data-edit-key");
            var rowEl = btn.closest("[data-row-key]");
            if (typeof opts.onEdit === "function") {
                opts.onEdit(key, rowEl, btn);
            } else {
                _defaultInlineEdit(container, key, rowEl, opts);
            }
        });

        // flag button click
        container.addEventListener("click", function (ev) {
            var btn = ev.target.closest(".ari-tinfo-flag-btn");
            if (!btn) return;
            ev.stopPropagation();
            ev.preventDefault();
            var key = btn.getAttribute("data-flag-key");
            var rowEl = btn.closest("[data-row-key]");
            if (typeof opts.onFlag === "function") {
                opts.onFlag(key, rowEl, btn);
            } else {
                _defaultFlagIssue(key, rowEl, opts);
            }
        });
    }

    function _defaultFlagIssue(key, rowEl, opts) {
        var apero = (opts && opts.apero_name) || '';
        var valueSpan = rowEl
            ? rowEl.querySelector('.ari-tinfo-value')
            : null;
        var current = valueSpan
            ? valueSpan.innerText.replace(/\s+/g, ' ').trim()
            : '';
        var reason = window.prompt(
            'Why is the value of "' + key + '" wrong?\n'
            + 'Current value: ' + current + '\n\n'
            + '(Issue will be reviewed by a moderator.)',
            '');
        if (reason === null) return;
        reason = String(reason).trim();
        if (!reason) {
            window.alert('Flag cancelled (empty reason).');
            return;
        }
        fetch('/api/issues/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                kind: 'flag',
                reason: reason,
                apero_name: apero || null,
                field: key,
                value: current,
                visibility: 'monitor'
            })
        }).then(function (r) {
            return r.json();
        }).then(function (data) {
            if (data && data.success) {
                window.alert('Issue #' + data.issue.id
                    + ' filed. Thank you!');
            } else {
                window.alert('Failed to file issue: '
                    + ((data && data.error) || 'unknown'));
            }
        }).catch(function (err) {
            window.alert('Failed to file issue: ' + err);
        });
    }

    // ---- default inline editor (used when no opts.onEdit given) ----
    function _defaultInlineEdit(container, key, rowEl, opts) {
        if (!rowEl) return;
        var valueCell = rowEl.querySelector(".ari-tinfo-row__value");
        if (!valueCell) return;
        // grab the existing scalar value text
        var valueSpan = valueCell.querySelector(".ari-tinfo-value");
        var current = valueSpan
            ? valueSpan.innerText.replace(/\s+/g, " ").trim()
            : valueCell.innerText.replace(/\s+/g, " ").trim();
        var originalHtml = valueCell.innerHTML;
        valueCell.innerHTML = ''
            + '<input type="text" class="ari-tinfo-edit-input"'
            + ' value="' + escapeHtml(current) + '"/>'
            + ' <button type="button"'
            + ' class="ari-tinfo-edit-save">Save</button>'
            + ' <button type="button"'
            + ' class="ari-tinfo-edit-cancel">Cancel</button>';
        var input = valueCell.querySelector(".ari-tinfo-edit-input");
        var saveBtn = valueCell.querySelector(".ari-tinfo-edit-save");
        var cancelBtn = valueCell.querySelector(
            ".ari-tinfo-edit-cancel");
        input.focus();
        input.select();

        cancelBtn.addEventListener("click", function () {
            valueCell.innerHTML = originalHtml;
        });
        saveBtn.addEventListener("click", function () {
            var newVal = input.value;
            if (typeof opts.onSave === "function") {
                opts.onSave(key, newVal, rowEl);
                return;
            }
            var apero = opts.apero_name;
            var url = (opts.updateUrl
                || "/api/astrometrics/update-field");
            if (!apero) {
                window.alert("No apero_name in opts; cannot save.");
                return;
            }
            var body = { apero_name: apero,
                         key: key,
                         value: newVal };
            fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            }).then(function (r) {
                if (!r.ok) throw new Error("HTTP " + r.status);
                return r.json();
            }).then(function (resp) {
                if (resp && resp.error) {
                    window.alert("Save failed: " + resp.error);
                    return;
                }
                if (typeof opts.onSaved === "function") {
                    opts.onSaved(key, newVal, resp);
                } else {
                    valueCell.innerHTML = '<span class="ari-tinfo-value">'
                        + escapeHtml(newVal) + '</span>';
                }
            }).catch(function (err) {
                window.alert("Save failed: " + err);
            });
        });
    }

    function applyPermissionVisibility(container, perms) {
        if (!container || !perms) return;
        var nodes = container.querySelectorAll("[data-perm]");
        nodes.forEach(function (el) {
            var needed = el.getAttribute("data-perm");
            if (perms.indexOf(needed) >= 0) {
                el.removeAttribute("hidden");
            } else {
                el.setAttribute("hidden", "");
            }
        });
    }

    function render(container, payload, opts) {
        if (!container) return;
        opts = opts || {};
        var sections = (payload && payload.sections) || [];
        if (!sections.length) {
            container.innerHTML = '<p class="ari-section-intro">'
                + "No target information available." + "</p>";
            return;
        }
        var citeReg = makeCitationRegistry();
        var html = "";
        sections.forEach(function (sec) {
            if (sec.kind === "data") {
                html += renderDataSection(sec, citeReg);
            } else if (sec.kind === "chart") {
                html += renderChartSection(sec);
            }
        });
        container.innerHTML = html;

        bindSectionInteractions(container, opts);

        if (opts.userPerms) {
            applyPermissionVisibility(container, opts.userPerms);
        }
        if (typeof opts.mountChartsCb === "function") {
            sections.forEach(function (sec) {
                if (sec.kind !== "chart") return;
                var hostId = sec.chart_id;
                if (!hostId) return;
                var host = document.getElementById(hostId);
                if (host) {
                    opts.mountChartsCb(sec.id, host, sec.chart_type);
                }
            });
        } else {
            bindDefaultChartActions(container, opts);
        }
    }

    var CHART_API = {
        finder: "/api/data-portal/finder-chart",
        rotation: "/api/data-portal/tess-rotation",
        sed: "/api/astrometrics/sed",
        hr_diagram: "/api/astrometrics/hr-diagram"
    };

    function setChartStatus(host, msg) {
        var el = host.querySelector('[data-chart-status]');
        if (el) el.textContent = msg || '';
    }

    function setChartError(host, msg) {
        var el = host.querySelector('[data-chart-error]');
        if (!el) return;
        if (msg) {
            el.textContent = msg;
            el.style.display = '';
        } else {
            el.textContent = '';
            el.style.display = 'none';
        }
    }

    /**
     * Inject a Bokeh {script, div} payload into the chart host.
     * The div is written first, then the script is evaluated so
     * Bokeh.embed.embed_item targets the now-present root id.
     */
    function renderChartBokeh(host, payload) {
        var box = host.querySelector('[data-chart-images]');
        if (!box) return;
        // Force the host to a block-level full-width container
        // so Bokeh's stretch_width sizing mode can compute a
        // non-zero width. Without this the embed lays out at 0
        // px and the x-axis collapses ("no x-extent").
        box.style.display = 'block';
        box.style.width = '100%';
        box.innerHTML = '';
        var div = String(payload.div || '');
        var script = String(payload.script || '');
        if (!div && !script) {
            box.innerHTML = '<p style="color:'
                + 'var(--ari-text-muted);">No plot returned.</p>';
            return;
        }
        var wrap = document.createElement('div');
        wrap.style.width = '100%';
        wrap.style.display = 'block';
        wrap.innerHTML = div;
        box.appendChild(wrap);
        if (script) {
            // Strip the surrounding <script> wrapper and execute
            // inline so Bokeh sees the freshly inserted root.
            var m = script.match(
                /<script[^>]*>([\s\S]*?)<\/script>/i);
            var code = m ? m[1] : script;
            try {
                // eslint-disable-next-line no-new-func
                (new Function(code))();
            } catch (err) {
                setChartError(host,
                    'Bokeh embed failed: '
                        + (err && err.message ? err.message : err));
            }
        }
    }

    function renderChartImages(host, payload) {
        var box = host.querySelector('[data-chart-images]');
        if (!box) return;
        box.innerHTML = '';
        var imgs = [];
        if (payload && Array.isArray(payload.images)) {
            payload.images.forEach(function (b64, idx) {
                var t = (payload.titles && payload.titles[idx])
                    || (payload.bands && payload.bands[idx])
                    || '';
                imgs.push({src: b64, title: t});
            });
        } else if (payload && payload.image) {
            imgs.push({src: payload.image,
                       title: payload.title || ''});
        } else if (payload && Array.isArray(payload.sectors)) {
            payload.sectors.forEach(function (s) {
                if (s && s.image) {
                    imgs.push({
                        src: s.image,
                        title: 'Sector ' + (s.sector || '?')
                    });
                }
            });
        }
        if (!imgs.length) {
            box.innerHTML = '<p style="color:'
                + 'var(--ari-text-muted);">No image returned.</p>';
            return;
        }
        imgs.forEach(function (im) {
            var fig = document.createElement('figure');
            fig.style.margin = '0';
            fig.style.maxWidth = '480px';
            var img = document.createElement('img');
            var src = im.src || '';
            if (src && !src.startsWith('data:')) {
                src = 'data:image/png;base64,' + src;
            }
            img.src = src;
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
            img.style.border = '1px solid var(--ari-border)';
            img.style.borderRadius = '4px';
            fig.appendChild(img);
            if (im.title) {
                var cap = document.createElement('figcaption');
                cap.style.fontSize = '12px';
                cap.style.color = 'var(--ari-text-muted)';
                cap.style.textAlign = 'center';
                cap.textContent = im.title;
                fig.appendChild(cap);
            }
            box.appendChild(fig);
        });
    }

    function appendChartLog(host, text) {
        if (!text) return;
        var wrap = host.querySelector('[data-chart-log-wrap]');
        var pre = host.querySelector('[data-chart-log]');
        if (!pre || !wrap) return;
        wrap.style.display = '';
        pre.textContent += String(text);
        pre.scrollTop = pre.scrollHeight;
    }

    function runChartFetch(host, ctype, opts) {
        var name = (opts && opts.apero_name) || '';
        if (!name) {
            setChartError(host, 'No target name available.');
            return;
        }
        var url = CHART_API[ctype];
        if (!url) {
            setChartError(host, 'Unknown chart type: ' + ctype);
            return;
        }
        setChartError(host, '');
        setChartStatus(host, 'Generating...');
        var qs = '?name=' + encodeURIComponent(name)
            + '&_ts=' + Date.now();
        var btn = host.querySelector('[data-chart-action="run"]');
        if (btn) btn.disabled = true;
        fetch(url + qs).then(function (r) {
            return r.json();
        }).then(function (data) {
            if (!data || data.success === false) {
                setChartError(host,
                    (data && data.error) || 'Failed.');
                setChartStatus(host, '');
                return;
            }
            // Bokeh payload (shared with object-page builders)
            // takes precedence over legacy image payload.
            if (data.script || data.div) {
                renderChartBokeh(host, data);
            } else {
                renderChartImages(host, data);
            }
            if (data.log) appendChartLog(host, data.log);
            setChartStatus(host, 'Done.');
        }).catch(function (err) {
            setChartError(host,
                'Network error: ' + (err && err.message
                    ? err.message : err));
            setChartStatus(host, '');
        }).then(function () {
            if (btn) btn.disabled = false;
        });
    }

    function bindDefaultChartActions(container, opts) {
        // Auto-fetch every chart-section host as soon as it is
        // bound. There is no "Generate" button anymore -- the
        // chart renders on its own on page load (matching the
        // data-portal object page behaviour).
        var hosts = container.querySelectorAll(
            '.ari-tinfo-chart[data-chart-type]');
        hosts.forEach(function (host) {
            var ctype = host.getAttribute('data-chart-type');
            if (!ctype) return;
            // Defer to the next animation frame so the host is
            // measurable (Bokeh stretch_width needs a non-zero
            // container width to compute the x range).
            window.requestAnimationFrame(function () {
                runChartFetch(host, ctype, opts);
            });
        });
    }

    window.AperoTargetInfo = {
        render: render,
        applyPermissionVisibility: applyPermissionVisibility,
    };
}());
