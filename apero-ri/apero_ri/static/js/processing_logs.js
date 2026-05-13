/* ============================================================
   processing_logs.js  –  Monitor portal: processing logs
   ============================================================
   Handles two modes driven by window.ARI_PROC_LOGS.mode:

     "profile"  – displays the per-profile processing run table.
                  Each PID cell is a link to the pid page.

     "pid"      – displays the per-PID recipe detail table.
                  Each log-file cell is a button that opens the
                  log file popup.
   ============================================================ */

(function () {
    "use strict";

    if (window.__ARI_PROC_LOGS_INIT__) {
        return;
    }
    window.__ARI_PROC_LOGS_INIT__ = true;

    /* ----------------------------------------------------------
       Helpers
    ---------------------------------------------------------- */
    function esc(s) {
        return String(s == null ? "" : s)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function showToast(msg) {
        var t = document.createElement("div");
        t.className = "pl-copy-toast";
        t.textContent = msg;
        document.body.appendChild(t);
        setTimeout(function () {
            t.classList.add("pl-copy-toast--fade");
            setTimeout(function () {
                if (t.parentNode) t.parentNode.removeChild(t);
            }, 450);
        }, 1800);
    }

    function copyToClipboard(text, okMsg) {
        function fallbackCopy() {
            var ta = document.createElement("textarea");
            ta.value = text;
            ta.style.position = "fixed";
            ta.style.opacity = "0";
            document.body.appendChild(ta);
            ta.select();
            try {
                document.execCommand("copy");
                showToast(okMsg);
            } catch (_) {
                showToast("Copy failed");
            }
            document.body.removeChild(ta);
        }

        if (navigator.clipboard &&
                typeof navigator.clipboard.writeText === "function") {
            navigator.clipboard.writeText(text)
                .then(function () {
                    showToast(okMsg);
                })
                .catch(function () {
                    fallbackCopy();
                });
            return;
        }

        fallbackCopy();
    }

    /* ----------------------------------------------------------
       State
    ---------------------------------------------------------- */
    var cfg = window.ARI_PROC_LOGS || {};
    var state = {
        allRows: [],
        filteredRows: [],
        columns: [],
        dropdownCols: [],
        sortCol: null,
        sortDir: "desc",  /* default: newest first */
        page: 1,
        perPage: 50,
        filters: {},
        findMatches: [],  /* array of .pl-log-line elements */
        findIdx: 0,
        currentLogfile: "",
        currentLogPath: "",
        logAutoOpened: false,
    };

    /* ----------------------------------------------------------
       DOM references (set after DOMContentLoaded)
    ---------------------------------------------------------- */
    var dom = {};

    function initDom() {
        dom.headerRow = document.getElementById("pl-header-row");
        dom.filterRow = document.getElementById("pl-filter-row");
        dom.tbody     = document.getElementById("pl-tbody");
        dom.rowSummary= document.getElementById("pl-row-summary");
        dom.perpage   = document.getElementById("pl-perpage");
        dom.pageInfo  = document.getElementById("pl-page-info");
        dom.pageInput = document.getElementById("pl-page-input");
        dom.pageTotal = document.getElementById("pl-page-total");
        dom.btnFirst  = document.getElementById("pl-btn-first");
        dom.btnPrev   = document.getElementById("pl-btn-prev");
        dom.btnNext   = document.getElementById("pl-btn-next");
        dom.btnLast   = document.getElementById("pl-btn-last");
        dom.btnClear  = document.getElementById("pl-btn-clear-filters");
        dom.btnRefresh = document.getElementById("pl-btn-refresh");
        dom.lastUpdated = document.getElementById("pl-last-updated");
        dom.scrollTop = document.getElementById("pl-scroll-top");
        dom.scrollSizer = document.getElementById("pl-scroll-sizer");

        dom.logOverlay  = document.getElementById("pl-log-overlay");
        dom.logBackdrop = document.getElementById("pl-log-backdrop");
        dom.logPanel    = document.getElementById("pl-log-panel");
        dom.logFilename = document.getElementById("pl-log-filename");
        dom.logContent  = document.getElementById("pl-log-content");
        dom.logCopyPath = document.getElementById("pl-log-copy-path");
        dom.logCopyUrl  = document.getElementById("pl-log-copy-url");
        dom.logCopy     = document.getElementById("pl-log-copy");
        dom.logClose    = document.getElementById("pl-log-close");
        dom.logFind     = document.getElementById("pl-log-find");
        dom.logFindPrev =
            document.getElementById("pl-log-find-prev");
        dom.logFindNext =
            document.getElementById("pl-log-find-next");
        dom.logFindCount =
            document.getElementById("pl-log-find-count");

        if (cfg.mode === "pid") {
            dom.groupName   = document.getElementById("pl-group-name");
        }
    }

    /* ----------------------------------------------------------
       Sorting
    ---------------------------------------------------------- */
    function sortRows(rows, col, dir) {
        if (!col) return rows;
        var factor = dir === "asc" ? 1 : -1;
        return rows.slice().sort(function (a, b) {
            var va = a[col];
            var vb = b[col];
            if (va == null && vb == null) return 0;
            if (va == null) return 1 * factor;
            if (vb == null) return -1 * factor;
            if (typeof va === "number" && typeof vb === "number") {
                return (va - vb) * factor;
            }
            return String(va).localeCompare(String(vb)) * factor;
        });
    }

    function normalizeFinishedValue(v) {
        var s = String(v == null ? "" : v).trim().toLowerCase();
        if (s === "1" || s === "true" || s === "yes") {
            return "1";
        }
        if (s === "0" || s === "false" || s === "no") {
            return "0";
        }
        return s;
    }

    function isUnfinishedFilterValue(v) {
        return normalizeFinishedValue(v) === "0";
    }

    function formatDurationSeconds(v) {
        if (v == null) {
            return "";
        }
        var n = Number(v);
        if (!isFinite(n) || n < 0) {
            return "";
        }
        var secs = Math.floor(n);
        if (secs < 60) {
            return String(secs) + "s";
        }
        if (secs < 3600) {
            var mm = Math.floor(secs / 60);
            var ss = secs % 60;
            return String(mm) + "m " + String(ss) + "s";
        }
        var hh = Math.floor(secs / 3600);
        var rem = secs % 3600;
        var m2 = Math.floor(rem / 60);
        var s2 = rem % 60;
        return String(hh) + "h " + String(m2) + "m " +
            String(s2) + "s";
    }

    /* ----------------------------------------------------------
       Filtering
    ---------------------------------------------------------- */
    function filterRows() {
        var rows = state.allRows;
        for (var col in state.filters) {
            if (!Object.prototype.hasOwnProperty.call(
                    state.filters, col)) continue;
            var fval = state.filters[col];

            var fstr = String(fval).trim().toLowerCase();
            if (!fstr) continue;
            rows = rows.filter(function (row) {
                var v = row[col];
                if (v == null) return false;
                if (col === "Finished") {
                    return normalizeFinishedValue(v) ===
                        normalizeFinishedValue(fstr);
                }
                if (state.dropdownCols.indexOf(col) >= 0) {
                    return String(v).trim().toLowerCase() === fstr;
                }
                return String(v).toLowerCase().indexOf(fstr) >= 0;
            });
        }
        state.filteredRows = sortRows(rows, state.sortCol, state.sortDir);
        state.page = 1;
        renderPage();
    }

    /* ----------------------------------------------------------
       Build header + filter row
    ---------------------------------------------------------- */
    function buildHeader() {
        if (!dom.headerRow) return;
        dom.headerRow.innerHTML = "";
        dom.filterRow.innerHTML = "";

        state.columns.forEach(function (col) {
            /* header cell */
            var th = document.createElement("th");
            th.className = "ot-th ot-th--sortable";
            th.dataset.col = col;

            var icon = "fa-sort";
            if (state.sortCol === col) {
                icon = state.sortDir === "asc"
                    ? "fa-sort-up" : "fa-sort-down";
            }
            th.innerHTML =
                esc(col) +
                " <i class=\"fa-solid " + icon + " ot-sort-icon\"></i>";
            th.addEventListener("click", function () {
                if (state.sortCol === col) {
                    state.sortDir =
                        state.sortDir === "asc" ? "desc" : "asc";
                } else {
                    state.sortCol = col;
                    state.sortDir = "asc";
                }
                state.filteredRows = sortRows(
                    state.filteredRows, state.sortCol, state.sortDir
                );
                buildHeader();
                renderPage();
            });
            dom.headerRow.appendChild(th);

            /* filter cell */
            var td = document.createElement("td");
            td.className = "ot-filter-cell";

            var isDropdown =
                state.dropdownCols.indexOf(col) >= 0;

            if (isDropdown) {
                /* build unique value list */
                var opts = {};
                state.allRows.forEach(function (row) {
                    var v = row[col];
                    if (v != null) {
                        opts[String(v)] = true;
                    }
                });
                var sel = document.createElement("select");
                sel.className = "ot-filter-select";
                sel.dataset.col = col;

                var optAll = document.createElement("option");
                optAll.value = "";
                optAll.textContent = "All";
                sel.appendChild(optAll);

                Object.keys(opts).sort().forEach(function (v) {
                    var opt = document.createElement("option");
                    opt.value = v;
                    opt.textContent = v;
                    if ((state.filters[col] || "") === v) {
                        opt.selected = true;
                    }
                    sel.appendChild(opt);
                });

                sel.addEventListener("change", function () {
                    state.filters[col] = sel.value;
                    /* If user manually changes the Finished
                       dropdown, keep the toggle in sync. */
                    if (col === "Finished") {
                        var ub = document.getElementById(
                            "pl-btn-unfinished"
                        );
                        if (ub) {
                            if (isUnfinishedFilterValue(sel.value)) {
                                ub.classList.add(
                                    "ari-btn--primary"
                                );
                                ub.classList.remove(
                                    "ari-btn--secondary"
                                );
                            } else {
                                ub.classList.remove(
                                    "ari-btn--primary"
                                );
                                ub.classList.add(
                                    "ari-btn--secondary"
                                );
                            }
                        }
                    }
                    filterRows();
                });
                td.appendChild(sel);
            } else {
                var inp = document.createElement("input");
                inp.type = "text";
                inp.className = "ot-filter-input";
                inp.placeholder = col;
                inp.dataset.col = col;
                inp.value = state.filters[col] || "";
                inp.addEventListener("input", function () {
                    state.filters[col] = inp.value;
                    filterRows();
                });
                td.appendChild(inp);
            }

            dom.filterRow.appendChild(td);
        });
    }

    /* ----------------------------------------------------------
       Cell renderer
    ---------------------------------------------------------- */
    function renderCell(col, val, row) {
        if (val == null) return "";

        /* PID column on profile page → link */
        if (cfg.mode === "profile" && col === "PID") {
            var pidUrl =
                cfg.pidBaseUrl.replace(/\/$/, "") +
                "/" + encodeURIComponent(String(val));
            return "<a href=\"" + esc(pidUrl) + "\" " +
                   "class=\"pl-pid-link\">" +
                   esc(String(val)) + "</a>";
        }

        /* Log file column → popup button */
        if (col === "Log file") {
            return "<button class=\"pl-log-link\" " +
                   "data-logfile=\"" + esc(String(val)) + "\">" +
                   "[Log file]</button>";
        }

        /* Recipe call column on pid page → runstring popup icon */
        if (cfg.mode === "pid" && col === "Recipe call") {
            return "<button class=\"pl-run-btn\" " +
                   "data-runstring=\"" + esc(String(val)) +
                   "\" title=\"View recipe call\">" +
                   "<i class=\"fa-solid fa-terminal\"></i>" +
                   "</button>";
        }

        /* Finished column */
        if (col === "Finished") {
            var finished = (val === 1 || val === true ||
                            String(val) === "1" ||
                            String(val).toLowerCase() === "true");
            if (finished) {
                return "<span class=\"pl-finished-yes\">Yes</span>";
            }
            return "<span class=\"pl-finished-no\">No</span>";
        }

        if (col === "Time taken") {
            return esc(formatDurationSeconds(val));
        }

        return esc(String(val));
    }

    /* ----------------------------------------------------------
       Render one page of rows
    ---------------------------------------------------------- */
    function renderPage() {
        if (!dom.tbody) return;

        var perPage = state.perPage;
        var total = state.filteredRows.length;
        var totalPages = perPage === 0
            ? 1
            : Math.max(1, Math.ceil(total / perPage));

        if (state.page > totalPages) state.page = totalPages;
        if (state.page < 1) state.page = 1;

        var start = perPage === 0
            ? 0
            : (state.page - 1) * perPage;
        var end = perPage === 0
            ? total
            : Math.min(start + perPage, total);

        var pageRows = state.filteredRows.slice(start, end);

        if (pageRows.length === 0) {
            dom.tbody.innerHTML =
                "<tr><td colspan=\"" + state.columns.length +
                "\" class=\"ot-loading\">No results.</td></tr>";
        } else {
            var html = "";
            pageRows.forEach(function (row) {
                html += "<tr class=\"ot-row\">";
                state.columns.forEach(function (col) {
                    html += "<td class=\"ot-cell\">" +
                        renderCell(col, row[col], row) +
                        "</td>";
                });
                html += "</tr>";
            });
            dom.tbody.innerHTML = html;
        }

        /* update pagination */
        if (dom.pageInfo) {
            dom.pageInfo.textContent =
                start + 1 + "–" + end + " of " + total;
        }
        if (dom.rowSummary) {
            dom.rowSummary.textContent =
                total + " row" + (total !== 1 ? "s" : "");
        }
        if (dom.pageTotal) dom.pageTotal.textContent = totalPages;
        if (dom.pageInput) dom.pageInput.value = state.page;

        var atFirst = state.page <= 1;
        var atLast  = state.page >= totalPages;
        if (dom.btnFirst) dom.btnFirst.disabled = atFirst;
        if (dom.btnPrev)  dom.btnPrev.disabled  = atFirst;
        if (dom.btnNext)  dom.btnNext.disabled  = atLast;
        if (dom.btnLast)  dom.btnLast.disabled  = atLast;

        /* sync horizontal scroll sizer */
        syncScrollSizer();

        /* wire log-file popup buttons */
        if (dom.logOverlay) {
            wireLogButtons();
        }
        if (cfg.mode === "pid") {
            wireRunstringButtons();
        }
    }

    /* ----------------------------------------------------------
       Horizontal scroll sync
    ---------------------------------------------------------- */
    function syncScrollSizer() {
        var wrap = document.getElementById("pl-table-wrap");
        var top  = document.getElementById("pl-scroll-top");
        var sizer = document.getElementById("pl-scroll-sizer");
        if (!wrap || !top || !sizer) return;
        sizer.style.width = wrap.scrollWidth + "px";
        top.onscroll = function () {
            wrap.scrollLeft = top.scrollLeft;
        };
        wrap.onscroll = function () {
            top.scrollLeft = wrap.scrollLeft;
        };
    }

    /* ----------------------------------------------------------
       Runstring popup
    ---------------------------------------------------------- */
    function openRunstringPopup(runstring) {
        var overlay = document.getElementById("pl-run-overlay");
        if (!overlay) return;

        /* Store original for copy */
        overlay.dataset.original = runstring;

        /* Split on whitespace */
        var parts = runstring.trim().split(/\s+/);
        var script = parts[0] || "";
        var args   = parts.slice(1);

        /* Render each token with colouring */
        function renderToken(tok) {
            /* Optional flag: -x or --word */
            if (/^--?[A-Za-z]/.test(tok)) {
                return "<span class=\"pl-rs-flag\">" +
                       esc(tok) + "</span>";
            }
            /* Bool */
            if (tok === "True" || tok === "False") {
                return "<span class=\"pl-rs-bool\">" +
                       esc(tok) + "</span>";
            }
            /* Float / int */
            if (/^-?\d+(\.\d+)?([eE][+-]?\d+)?$/.test(tok)) {
                return "<span class=\"pl-rs-number\">" +
                       esc(tok) + "</span>";
            }
            /* Quoted or looks like a string value */
            return "<span class=\"pl-rs-string\">" +
                   esc(tok) + "</span>";
        }

        var html = "<span class=\"pl-rs-script\">" +
                   esc(script) + "</span>";
        args.forEach(function (arg) {
            html += "\n\t" + renderToken(arg);
        });

        var content = document.getElementById("pl-run-content");
        if (content) content.innerHTML = html;

        overlay.style.display = "flex";
        document.body.style.overflow = "hidden";
    }

    function closeRunstringPopup() {
        var overlay = document.getElementById("pl-run-overlay");
        if (!overlay) return;
        overlay.style.display = "none";
        document.body.style.overflow = "";
    }

    function wireRunstringButtons() {
        var btns = dom.tbody.querySelectorAll("[data-runstring]");
        btns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                openRunstringPopup(btn.dataset.runstring || "");
            });
        });
    }

    function wireLogButtons() {
        var btns = dom.tbody.querySelectorAll("[data-logfile]");
        btns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                var lf = btn.dataset.logfile || "";
                openLogPopup(lf);
            });
        });
    }

    /* ----------------------------------------------------------
       Log find bar
    ---------------------------------------------------------- */
    function logScrollToMatch(el) {
        if (!el || !dom.logContent) return;
        /* Scroll within the pre container (not the window). */
        var cr = dom.logContent.getBoundingClientRect();
        var er = el.getBoundingClientRect();
        dom.logContent.scrollTop +=
            (er.top - cr.top) -
            dom.logContent.clientHeight / 2 +
            el.clientHeight / 2;
    }

    function resetLogFind() {
        state.findMatches = [];
        state.findIdx = 0;
        if (dom.logFind) dom.logFind.value = "";
        if (dom.logFindCount) dom.logFindCount.textContent = "";
        if (dom.logContent) {
            dom.logContent
                .querySelectorAll(
                    ".pl-log-match-line,.pl-log-match-current"
                )
                .forEach(function (el) {
                    el.classList.remove(
                        "pl-log-match-line",
                        "pl-log-match-current"
                    );
                });
        }
    }

    function updateLogFind() {
        if (!dom.logContent) return;
        var query = dom.logFind
            ? dom.logFind.value.trim()
            : "";

        /* Clear previous highlights */
        var lines = dom.logContent
            .querySelectorAll(".pl-log-line");
        lines.forEach(function (el) {
            el.classList.remove(
                "pl-log-match-line",
                "pl-log-match-current"
            );
        });

        if (!query) {
            state.findMatches = [];
            state.findIdx = 0;
            if (dom.logFindCount) {
                dom.logFindCount.textContent = "";
            }
            return;
        }

        var lq = query.toLowerCase();
        var matches = [];
        lines.forEach(function (el) {
            if (
                (el.textContent || "")
                    .toLowerCase()
                    .indexOf(lq) >= 0
            ) {
                el.classList.add("pl-log-match-line");
                matches.push(el);
            }
        });

        state.findMatches = matches;
        state.findIdx = 0;

        if (matches.length > 0) {
            matches[0].classList.add("pl-log-match-current");
            logScrollToMatch(matches[0]);
        }

        if (dom.logFindCount) {
            dom.logFindCount.textContent =
                matches.length === 0
                    ? "No matches"
                    : "1 / " + matches.length;
        }
    }

    function logFindNav(dir) {
        var matches = state.findMatches;
        if (!matches || matches.length === 0) return;
        matches[state.findIdx].classList.remove(
            "pl-log-match-current"
        );
        state.findIdx =
            (state.findIdx + dir + matches.length) %
            matches.length;
        matches[state.findIdx].classList.add(
            "pl-log-match-current"
        );
        logScrollToMatch(matches[state.findIdx]);
        if (dom.logFindCount) {
            dom.logFindCount.textContent =
                (state.findIdx + 1) + " / " + matches.length;
        }
    }

    function makeLogShareUrl(cleanLogfile) {
        var href = window.location.href;
        var out = href;
        try {
            var u = new URL(href);
            u.searchParams.set("log", cleanLogfile);
            out = u.toString();
        } catch (_) {
            /* Keep current href fallback for old browsers. */
            out = href;
        }
        return out;
    }

    function openLogFromUrlParam() {
        if (!dom.logOverlay || state.logAutoOpened) {
            return;
        }
        var raw = "";
        try {
            raw = new URL(window.location.href)
                .searchParams.get("log") || "";
        } catch (_) {
            raw = "";
        }
        raw = String(raw).trim();
        if (!raw) {
            return;
        }
        state.logAutoOpened = true;
        openLogPopup(raw);
    }

    function openLogPopup(cleanLogfile) {
        if (!dom.logOverlay) return;
        state.currentLogfile = String(cleanLogfile || "");
        state.currentLogPath = "";
        dom.logOverlay.dataset.currentLogfile =
            state.currentLogfile;
        dom.logOverlay.dataset.currentLogPath = "";
        dom.logOverlay.dataset.currentLogText = "";
        if (dom.logContent) {
            dom.logContent.dataset.currentLogfile =
                state.currentLogfile;
            dom.logContent.dataset.currentLogPath = "";
            dom.logContent.dataset.currentLogText = "";
        }
        dom.logContent.innerHTML =
            "<i class=\"fa-solid fa-spinner fa-spin\"></i> " +
            "Loading&hellip;";
        var fname = cleanLogfile.split("/").pop();
        dom.logFilename.textContent = fname;
        dom.logOverlay.style.display = "flex";
        document.body.style.overflow = "hidden";

        fetch(cfg.logFileUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                profile_id: cfg.profileId,
                clean_logfile: cleanLogfile,
            }),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var resolvedPath = String(
                data.log_path ||
                data.logPath ||
                data.looked_at ||
                ""
            );
            state.currentLogPath = resolvedPath;
            dom.logOverlay.dataset.currentLogPath =
                resolvedPath;
            if (dom.logContent) {
                dom.logContent.dataset.currentLogPath =
                    resolvedPath;
            }
            if (!data.exists) {
                var msg = "Log file does not exist.";
                if (data.looked_at) {
                    msg += "\n\nLooked at:\n" + 
                        data.looked_at;
                }
                dom.logContent.textContent = msg;
                return;
            }
            renderLogContent(data.content || "");
        })
        .catch(function (err) {
            dom.logContent.textContent = "Error: " + err;
        });
    }

    function renderLogContent(text) {
        /* Colour special marker lines, escape everything else.
           Each line is wrapped in a <span> with a data-line index
           so the find bar can target individual lines. */
        var html = "";
        dom.logOverlay.dataset.currentLogText = text;
        dom.logContent.dataset.currentLogText = text;
        text.split("\n").forEach(function (line, idx) {
            if (!line) {
                return;
            }
            var escaped = esc(line);
            var open =
                "<span class=\"pl-log-line\" " +
                "id=\"pll-" + idx + "\" " +
                "data-line=\"" + idx + "\">";
            if (line.indexOf("-!!|") >= 0) {
                html +=
                    open +
                    "<span class=\"pl-log-error\">" +
                    escaped + "</span></span>";
            } else if (line.indexOf("-@!|") >= 0) {
                html +=
                    open +
                    "<span class=\"pl-log-warn\">" +
                    escaped + "</span></span>";
            } else {
                html += open + escaped + "</span>";
            }
        });
        dom.logContent.innerHTML = html;
        /* Default to end of log */
        dom.logContent.scrollTop = dom.logContent.scrollHeight;
        /* Reset find bar */
        resetLogFind();
    }

    function closeLogPopup() {
        if (!dom.logOverlay) return;
        dom.logOverlay.style.display = "none";
        dom.logOverlay.dataset.currentLogfile = "";
        dom.logOverlay.dataset.currentLogPath = "";
        dom.logOverlay.dataset.currentLogText = "";
        if (dom.logContent) {
            dom.logContent.dataset.currentLogfile = "";
            dom.logContent.dataset.currentLogPath = "";
            dom.logContent.dataset.currentLogText = "";
        }
        document.body.style.overflow = "";
    }

    function setLastUpdatedText(lastUpdated) {
        if (!dom.lastUpdated) return;
        var txt = String(lastUpdated || "").trim();
        if (txt) {
            dom.lastUpdated.textContent = "Last updated " + txt;
            return;
        }
        dom.lastUpdated.textContent = "Last updated --";
    }

    function setRefreshBusy(isBusy) {
        if (!dom.btnRefresh) return;
        dom.btnRefresh.disabled = !!isBusy;
    }

    /* ----------------------------------------------------------
       Load data from server
    ---------------------------------------------------------- */
    function loadData(forceRefresh) {
        var useForceRefresh = forceRefresh === true;
        var body = {};
        if (cfg.mode === "profile") {
            body = {profile_id: cfg.profileId};
        } else {
            body = {profile_id: cfg.profileId, pid: cfg.pid};
        }
        if (useForceRefresh) {
            body.force_refresh = true;
        }
        setRefreshBusy(true);

        fetch(cfg.apiUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(body),
        })
        .then(function (r) {
            if (!r.ok) {
                return r.json().then(function (e) {
                    throw new Error(e.error || r.statusText);
                });
            }
            return r.json();
        })
        .then(function (data) {
            state.allRows      = data.rows || [];
            state.columns      = data.columns || [];
            state.dropdownCols = data.dropdown_columns || [];
            setLastUpdatedText(data.last_updated || "");

            /* default sort: Start time desc on profile page */
            if (cfg.mode === "profile") {
                state.sortCol = "Start time";
                state.sortDir = "desc";
            } else {
                state.sortCol = null;
                state.sortDir = "asc";
            }

            state.filteredRows = sortRows(
                state.allRows, state.sortCol, state.sortDir
            );
            state.filters = {};

            /* On pid page, update page title from group_name */
            if (cfg.mode === "pid" && data.group_name &&
                    dom.groupName) {
                dom.groupName.textContent = data.group_name;
            }

            buildHeader();
            renderPage();
            openLogFromUrlParam();
        })
        .catch(function (err) {
            if (dom.tbody) {
                dom.tbody.innerHTML =
                    "<tr><td colspan=\"10\" " +
                    "style=\"color:var(--ari-error,#f44);padding:1rem\">" +
                    "Error loading data: " + esc(String(err)) +
                    "</td></tr>";
            }
        })
        .then(function () {
            setRefreshBusy(false);
        });
    }

    /* ----------------------------------------------------------
       Wire events
    ---------------------------------------------------------- */
    function wireEvents() {
        if (dom.btnClear) {
            dom.btnClear.addEventListener("click", function () {
                state.filters = {};
                filterRows();
                /* reset filter inputs */
                dom.filterRow
                    .querySelectorAll("input,select")
                    .forEach(function (el) {
                        el.value = "";
                    });
                /* also reset unfinished toggle */
                var btn = document.getElementById(
                    "pl-btn-unfinished"
                );
                if (btn) {
                    btn.classList.remove("ari-btn--primary");
                    btn.classList.add("ari-btn--secondary");
                }
            });
        }

        /* Unfinished-only toggle (pid page) */
        var btnUnfinished =
            document.getElementById("pl-btn-unfinished");
        if (btnUnfinished) {
            console.log(
                "[processing_logs] unfinished button bound",
                {mode: cfg.mode}
            );
            btnUnfinished.addEventListener("click", function (event) {
                if (event && event.__ariProcLogsHandled__) {
                    console.log(
                        "[processing_logs] unfinished duplicate " +
                        "click handler ignored"
                    );
                    return;
                }
                if (event) {
                    event.__ariProcLogsHandled__ = true;
                }
                var isActive =
                    btnUnfinished.classList.contains(
                        "ari-btn--primary"
                    );
                /* Sync the Finished dropdown in the filter row */
                var finSel = dom.filterRow
                    ? dom.filterRow.querySelector(
                        '[data-col="Finished"]'
                    )
                    : null;
                console.log(
                    "[processing_logs] unfinished click",
                    {
                        isActive: isActive,
                        hasFinishedSelect: !!finSel,
                        beforeFilter: state.filters["Finished"],
                    }
                );
                if (isActive) {
                    /* Deactivate: clear filter */
                    btnUnfinished.classList.remove(
                        "ari-btn--primary"
                    );
                    btnUnfinished.classList.add(
                        "ari-btn--secondary"
                    );
                    delete state.filters["Finished"];
                    filterRows();
                    if (finSel) {
                        finSel.value = "";
                    }
                } else {
                    /* Activate: filter to Finished = 0 ("No") */
                    btnUnfinished.classList.add(
                        "ari-btn--primary"
                    );
                    btnUnfinished.classList.remove(
                        "ari-btn--secondary"
                    );
                    state.filters["Finished"] = "0";
                    filterRows();
                    if (finSel) {
                        var unfinishedOpt = "";
                        Array.from(finSel.options).forEach(function (opt) {
                            if (!unfinishedOpt &&
                                    isUnfinishedFilterValue(opt.value)) {
                                unfinishedOpt = opt.value;
                            }
                        });
                        if (!unfinishedOpt) {
                            Array.from(finSel.options).forEach(
                                function (opt) {
                                    if (!unfinishedOpt &&
                                            isUnfinishedFilterValue(
                                                opt.textContent
                                            )) {
                                        unfinishedOpt = opt.value;
                                    }
                                }
                            );
                        }
                        finSel.value = unfinishedOpt || "0";
                    }
                }
                console.log(
                    "[processing_logs] unfinished applied",
                    {
                        afterFilter: state.filters["Finished"],
                        rowsShown: state.filteredRows.length,
                        totalRows: state.allRows.length,
                    }
                );
            });
        } else {
            console.log(
                "[processing_logs] unfinished button not found",
                {mode: cfg.mode}
            );
        }

        if (dom.perpage) {
            dom.perpage.addEventListener("change", function () {
                state.perPage = parseInt(dom.perpage.value, 10) || 0;
                state.page = 1;
                renderPage();
            });
        }

        if (dom.btnRefresh) {
            dom.btnRefresh.addEventListener("click", function () {
                loadData(true);
            });
        }

        if (dom.btnFirst) {
            dom.btnFirst.addEventListener("click", function () {
                state.page = 1; renderPage();
            });
        }
        if (dom.btnPrev) {
            dom.btnPrev.addEventListener("click", function () {
                if (state.page > 1) { state.page--; renderPage(); }
            });
        }
        if (dom.btnNext) {
            dom.btnNext.addEventListener("click", function () {
                var perPage = state.perPage;
                var totalPages = perPage === 0 ? 1
                    : Math.max(1, Math.ceil(
                        state.filteredRows.length / perPage));
                if (state.page < totalPages) {
                    state.page++; renderPage();
                }
            });
        }
        if (dom.btnLast) {
            dom.btnLast.addEventListener("click", function () {
                var perPage = state.perPage;
                state.page = perPage === 0 ? 1
                    : Math.max(1, Math.ceil(
                        state.filteredRows.length / perPage));
                renderPage();
            });
        }

        if (dom.pageInput) {
            dom.pageInput.addEventListener("change", function () {
                var n = parseInt(dom.pageInput.value, 10);
                var perPage = state.perPage;
                var totalPages = perPage === 0 ? 1
                    : Math.max(1, Math.ceil(
                        state.filteredRows.length / perPage));
                if (!isNaN(n) && n >= 1 && n <= totalPages) {
                    state.page = n; renderPage();
                }
            });
        }

        /* log popup events */
        if (dom.logOverlay) {
            if (dom.logClose) {
                dom.logClose.addEventListener(
                    "click", closeLogPopup
                );
            }
            if (dom.logBackdrop) {
                dom.logBackdrop.addEventListener(
                    "click", closeLogPopup
                );
            }
            document.addEventListener("keydown", function (e) {
                if (e.key === "Escape") {
                    closeLogPopup();
                    closeRunstringPopup();
                }
            });

            /* find bar */
            if (dom.logFind) {
                dom.logFind.addEventListener(
                    "input", updateLogFind
                );
                dom.logFind.addEventListener(
                    "keydown", function (e) {
                        if (e.key === "Enter") {
                            logFindNav(
                                e.shiftKey ? -1 : 1
                            );
                        }
                    }
                );
            }
            if (dom.logFindPrev) {
                dom.logFindPrev.addEventListener(
                    "click", function () { logFindNav(-1); }
                );
            }
            if (dom.logFindNext) {
                dom.logFindNext.addEventListener(
                    "click", function () { logFindNav(1); }
                );
            }

            if (dom.logCopy) {
                dom.logCopy.addEventListener("click", function () {
                    var text = dom.logOverlay.dataset.currentLogText ||
                        (dom.logContent
                            ? (dom.logContent.dataset.currentLogText || "")
                            : "");
                    if (!text) {
                        showToast("No log content available");
                        return;
                    }
                    copyToClipboard(
                        text,
                        "Log copied to clipboard"
                    );
                });
            }

            if (dom.logCopyPath) {
                dom.logCopyPath.addEventListener("click", function () {
                    var val = dom.logOverlay.dataset.currentLogPath ||
                        dom.logOverlay.dataset.currentLogfile ||
                        state.currentLogPath ||
                        state.currentLogfile;
                    if (!val) {
                        showToast("No log path available");
                        return;
                    }
                    copyToClipboard(
                        val,
                        "Log path copied"
                    );
                });
            }

            if (dom.logCopyUrl) {
                dom.logCopyUrl.addEventListener("click", function () {
                    var lf = dom.logOverlay.dataset.currentLogfile ||
                        state.currentLogfile;
                    if (!lf) {
                        showToast("No log selected");
                        return;
                    }
                    var url = makeLogShareUrl(lf);
                    copyToClipboard(
                        url,
                        "Log viewer URL copied"
                    );
                });
            }
        }

        if (cfg.mode === "pid") {
            /* runstring popup */
            var runOverlay  =
                document.getElementById("pl-run-overlay");
            var runBackdrop =
                document.getElementById("pl-run-backdrop");
            var runClose =
                document.getElementById("pl-run-close");
            var runCopy  =
                document.getElementById("pl-run-copy");

            if (runClose) {
                runClose.addEventListener(
                    "click", closeRunstringPopup
                );
            }
            if (runBackdrop) {
                runBackdrop.addEventListener(
                    "click", closeRunstringPopup
                );
            }
            if (runCopy) {
                runCopy.addEventListener("click", function () {
                    var original =
                        runOverlay
                            ? (runOverlay.dataset.original || "")
                            : "";
                    copyToClipboard(
                        original,
                        "Recipe call copied"
                    );
                });
            }

        }
    }

    /* ----------------------------------------------------------
       Init
    ---------------------------------------------------------- */
    document.addEventListener("DOMContentLoaded", function () {
        initDom();
        wireEvents();
        loadData(false);
    });

}());
