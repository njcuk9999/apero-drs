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

    /* Synthetic column: action buttons for known-errors lookup and
       GitHub issue creation. Appended to both the profile and pid tables. */
    var ACTIONS_COL = "Actions";
    var KNOWN_ERRORS_URL = "/monitor_portal/known_errors";
    var GITHUB_ISSUE_BASE_URL =
        "https://github.com/njcuk9999/apero-drs/issues/new";
    var GITHUB_ISSUE_BODY_LIMIT = 40000;
    var GITHUB_ISSUE_URL_MAX = 1800;

    /* Trailing instrument suffixes stripped from recipe names before they
       are used as the known-errors filter (longest first so e.g.
       "_nirps_he" matches before a hypothetical "_nirps"). */
    var INSTRUMENT_SUFFIXES = [
        "_nirps_he", "_nirps_ha", "_nirps", "_spirou",
    ];

    function stripInstrumentSuffix(name) {
        var out = String(name || "").trim();
        var lower = out.toLowerCase();
        for (var i = 0; i < INSTRUMENT_SUFFIXES.length; i++) {
            var suf = INSTRUMENT_SUFFIXES[i];
            if (lower.slice(-suf.length) === suf) {
                return out.slice(0, out.length - suf.length);
            }
        }
        return out;
    }

    function _issueField(label, value) {
        var text = String(value == null ? "" : value).trim();
        if (!text) return "";
        return "**" + label + ":** " + text + "\n";
    }

    function _buildGithubIssueTitle(meta) {
        var parts = ["APERO monitor log report"];
        var groupName = String(meta.groupName || "").trim();
        var pid = String(meta.pid || "").trim();
        var recipe = String(meta.recipeName || meta.shortName || "").trim();
        if (groupName) parts.push(groupName);
        if (pid) parts.push("PID " + pid);
        if (recipe) parts.push(recipe);
        return parts.join(" - ");
    }

    function _buildGithubIssueBody(meta, logText) {
        var body = [];
        body.push("APERO monitor log report");
        body.push("");
        body.push(_issueField("Profile ID", meta.profileId));
        body.push(_issueField("Group", meta.groupName));
        body.push(_issueField("PID", meta.pid));
        body.push(_issueField("Recipe name", meta.recipeName));
        body.push(_issueField("Short name", meta.shortName));
        body.push(_issueField("Recipe call", meta.recipeCall));
        body.push(_issueField("Start time", meta.startTime));
        body.push(_issueField("End time", meta.endTime));
        body.push(_issueField("Time taken", meta.timeTaken));
        body.push(_issueField("Finished", meta.finished));
        body.push(_issueField("Failed", meta.failed));
        body.push(_issueField("Total run", meta.totalRun));
        body.push(_issueField("Log file", meta.logfile));
        body.push("");
        body.push("## Log");
        body.push("```text");
        body.push(String(logText || "").replace(/\r\n/g, "\n"));
        body.push("```");

        var out = body.join("\n");
        if (out.length > GITHUB_ISSUE_BODY_LIMIT) {
            out = out.slice(0, GITHUB_ISSUE_BODY_LIMIT) +
                "\n\n[Log truncated because the issue body was too large.]";
        }
        return out;
    }

    function _buildGithubIssueSeedBody(meta, hadLogError) {
        var body = [];
        body.push("APERO monitor log report");
        body.push("");
        body.push(_issueField("Profile ID", meta.profileId));
        body.push(_issueField("Group", meta.groupName));
        body.push(_issueField("PID", meta.pid));
        body.push(_issueField("Recipe name", meta.recipeName));
        body.push(_issueField("Log file", meta.logfile));
        body.push("");
        body.push("A full issue body was copied to your clipboard by ARI.");
        body.push("Paste it below this line.");
        if (hadLogError) {
            body.push("");
            body.push("[Note] Log download failed. Paste any local details " +
                "you have.");
        }
        return body.join("\n");
    }

    function _fetchFullLogText(profileId, cleanLogfile) {
        return fetch(cfg.logFileUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                profile_id: profileId,
                clean_logfile: cleanLogfile,
                from_line: 0,
                to_line: 2147483647,
            }),
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
            if (!data.exists) {
                throw new Error("Log file does not exist");
            }
            return String(data.content || "");
        });
    }

    function _openGithubIssue(meta) {
        var profileId = String(meta.profileId || cfg.profileId || "").trim();
        var cleanLogfile = String(meta.logfile || "").trim();
        if (!profileId || !cleanLogfile) {
            showToast("Missing log file information");
            return;
        }

        var issueWindow = window.open("about:blank", "_blank");
        if (issueWindow) {
            try {
                issueWindow.document.write(
                    "<p style=\"font-family:sans-serif;padding:1rem\">" +
                    "Preparing GitHub issue..." +
                    "</p>"
                );
                issueWindow.document.close();
            } catch (_err) {}
        }

        var title = _buildGithubIssueTitle(meta);

        _fetchFullLogText(profileId, cleanLogfile)
            .then(function (logText) {
                var fullBody = _buildGithubIssueBody(meta, logText);
                copyToClipboard(
                    fullBody,
                    "Full issue details copied. Paste into GitHub body."
                );
                var body = _buildGithubIssueSeedBody(meta, false);
                var url = GITHUB_ISSUE_BASE_URL +
                    "?title=" + encodeURIComponent(title) +
                    "&body=" + encodeURIComponent(body);
                if (url.length > GITHUB_ISSUE_URL_MAX) {
                    url = GITHUB_ISSUE_BASE_URL +
                        "?title=" + encodeURIComponent(title);
                }
                if (issueWindow) {
                    issueWindow.location.href = url;
                    issueWindow.focus();
                } else {
                    window.location.href = url;
                }
            })
            .catch(function (err) {
                var body = _buildGithubIssueSeedBody(meta, true);
                var url = GITHUB_ISSUE_BASE_URL +
                    "?title=" + encodeURIComponent(title) +
                    "&body=" + encodeURIComponent(body);
                if (url.length > GITHUB_ISSUE_URL_MAX) {
                    url = GITHUB_ISSUE_BASE_URL +
                        "?title=" + encodeURIComponent(title);
                }
                if (issueWindow) {
                    issueWindow.location.href = url;
                    issueWindow.focus();
                } else {
                    window.location.href = url;
                }
                showToast("Log fetch failed: " + err);
            });
    }

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
        /* ── Server-side pagination (pid page only) ── */
        pagedMode: false,         /* true once first paged response received */
        serverTotal: 0,           /* total rows matching current filters     */
        pageCache: {},            /* key→rows cache for prefetch             */
        pageCacheTimestamp: 0,    /* invalidated when filters/sort change    */
        filterDebounceTimer: null,
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

        dom.logMaximize = document.getElementById("pl-log-maximize");

        if (cfg.mode === "pid") {
            dom.groupName   = document.getElementById("pl-group-name");
            /* Summary cards */
            dom.summaryCards = document.getElementById("pl-summary-cards");
            dom.sumGroup   = document.getElementById("pl-sum-group");
            dom.sumStart   = document.getElementById("pl-sum-start");
            dom.sumEnd     = document.getElementById("pl-sum-end");
            dom.sumTotal   = document.getElementById("pl-sum-total");
            dom.sumFailed   = document.getElementById("pl-sum-failed");
            dom.sumPassed   = document.getElementById("pl-sum-passed");
            dom.cardFailed  = document.getElementById("pl-card-failed");
            dom.cardPassed  = document.getElementById("pl-card-passed");
            dom.sumProclog = document.getElementById("pl-sum-proclog");
            /* Fail-report overlay */
            dom.reportOverlay  = document.getElementById("pl-report-overlay");
            dom.reportBackdrop =
                document.getElementById("pl-report-backdrop");
            dom.reportClose    = document.getElementById("pl-report-close");
            dom.reportBtnOpen   =
                document.getElementById("pl-btn-fail-report");
            dom.reportGenerate  =
                document.getElementById("pl-report-generate");
            dom.reportRegenerate=
                document.getElementById("pl-report-regenerate");
            dom.reportUseCached =
                document.getElementById("pl-report-use-cached");
            dom.reportRetry     = document.getElementById("pl-report-retry");
            dom.reportShare     = document.getElementById("pl-report-share");
            dom.reportDownload  =
                document.getElementById("pl-report-download");
            dom.reportBack      = document.getElementById("pl-report-back");
            dom.reportExpiry    =
                document.getElementById("pl-report-expiry");
            dom.reportErrorMsg  =
                document.getElementById("pl-report-error-msg");
            dom.reportAnalyserBody =
                document.getElementById("pl-report-analyser-body");
            dom.reportCacheBanner =
                document.getElementById("pl-report-cache-banner");
            dom.reportCacheAge  =
                document.getElementById("pl-report-cache-age");
            dom.reportDoneAge   =
                document.getElementById("pl-report-done-age");
            dom.reportSteps = {
                checking: document.getElementById("pl-report-step-checking"),
                start:    document.getElementById("pl-report-step-start"),
                loading:  document.getElementById("pl-report-step-loading"),
                done:     document.getElementById("pl-report-step-done"),
                error:    document.getElementById("pl-report-step-error"),
            };
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
            /* Synthetic column: plain header + empty filter cell. */
            if (col === ACTIONS_COL) {
                var thKE = document.createElement("th");
                thKE.className = "ot-th";
                thKE.dataset.col = col;
                thKE.textContent = col;
                dom.headerRow.appendChild(thKE);
                var tdKE = document.createElement("td");
                tdKE.className = "ot-filter-cell";
                dom.filterRow.appendChild(tdKE);
                return;
            }

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
                if (state.pagedMode) {
                    /* Sort server-side: reset to page 1. */
                    _invalidatePageCache();
                    state.page = 1;
                    loadPagedData(1, true);
                } else {
                    state.filteredRows = sortRows(
                        state.filteredRows, state.sortCol, state.sortDir
                    );
                    buildHeader();
                    renderPage();
                }
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
                
                /* For Finished column, always include 0 and 1 options */
                if (col === "Finished") {
                    opts["0"] = true;
                    opts["1"] = true;
                } else {
                    state.allRows.forEach(function (row) {
                        var v = row[col];
                        if (v != null) {
                            opts[String(v)] = true;
                        }
                    });
                }
                
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
                       dropdown, keep the toggle and cards in sync. */
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
                    if (state.pagedMode) {
                        _resetAndFetchPage();
                    } else {
                        filterRows();
                    }
                    if (col === "Finished") {
                        syncSummaryCardStates();
                    }
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
                    if (state.pagedMode) {
                        _resetAndFetchPage();
                    } else {
                        filterRows();
                    }
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
        /* Synthetic Actions column → known-errors link plus GitHub issue.
           Handled before the null check (row[col] is undefined). */
        if (col === ACTIONS_COL) {
            var recipe = stripInstrumentSuffix(
                String((row && row["Recipe name"]) || "").trim()
            );
            var keUrl = KNOWN_ERRORS_URL;
            if (recipe) {
                keUrl += "?q=" + encodeURIComponent(recipe);
            }
            var meta = {
                profileId: cfg.profileId,
                groupName: dom.groupName ? dom.groupName.textContent : "",
                pid: (cfg.mode === "pid") ? cfg.pid : (row && row.PID) || "",
                recipeName: row && row["Recipe name"],
                shortName: row && row["Short name"],
                recipeCall: row && row["Recipe call"],
                startTime: row && row["Start time"],
                endTime: row && row["End time"],
                timeTaken: row && row["Time taken"],
                finished: row && row["Finished"],
                failed: row && row["Failed"],
                totalRun: row && row["Total run"],
                logfile: row && row["Log file"],
            };
            return "<div class=\"pl-actions\">" +
                   "<a href=\"" + esc(keUrl) + "\" " +
                   "class=\"pl-action-btn pl-action-btn--known\" " +
                   "target=\"_blank\" rel=\"noopener\" " +
                   "title=\"check known errors\" " +
                   "aria-label=\"check known errors\">" +
                   "<i class=\"fa-solid fa-circle-question\"></i>" +
                   "</a>" +
                   "<button type=\"button\" " +
                   "class=\"pl-action-btn pl-action-btn--github\" " +
                   "data-github-issue=\"1\" " +
                   "data-profile-id=\"" + esc(String(meta.profileId || "")) +
                   "\" data-group-name=\"" + esc(String(meta.groupName || "")) +
                   "\" data-pid=\"" + esc(String(meta.pid || "")) +
                   "\" data-recipe-name=\"" + esc(String(meta.recipeName || "")) +
                   "\" data-short-name=\"" + esc(String(meta.shortName || "")) +
                   "\" data-recipe-call=\"" + esc(String(meta.recipeCall || "")) +
                   "\" data-start-time=\"" + esc(String(meta.startTime || "")) +
                   "\" data-end-time=\"" + esc(String(meta.endTime || "")) +
                   "\" data-time-taken=\"" + esc(String(meta.timeTaken || "")) +
                   "\" data-finished=\"" + esc(String(meta.finished || "")) +
                   "\" data-failed=\"" + esc(String(meta.failed || "")) +
                   "\" data-total-run=\"" + esc(String(meta.totalRun || "")) +
                   "\" data-logfile=\"" + esc(String(meta.logfile || "")) +
                   "\" title=\"create a github issue\" " +
                   "aria-label=\"create a github issue\">" +
                   "<i class=\"fa-brands fa-github\"></i>" +
                   "</button>" +
                   "</div>";
        }

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
        wireActionButtons();
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

    function wireActionButtons() {
        if (!dom.tbody) return;
        var btns = dom.tbody.querySelectorAll("[data-github-issue]");
        btns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                _openGithubIssue(btn.dataset);
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

    /* Current line window (0-based, half-open [from, to)). */
    var _logFromLine = 0;
    var _logToLine   = 500;
    var _logTotalLines = 0;

    function _fetchLogRange(cleanLogfile, fromLine, toLine) {
        dom.logContent.innerHTML =
            "<i class=\"fa-solid fa-spinner fa-spin\"></i> " +
            "Loading lines " + (fromLine + 1) + "–" + toLine + "&hellip;";
        fetch(cfg.logFileUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                profile_id: cfg.profileId,
                clean_logfile: cleanLogfile,
                from_line: fromLine,
                to_line: toLine,
            }),
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var resolvedPath = String(
                data.log_path || data.logPath || data.looked_at || ""
            );
            state.currentLogPath = resolvedPath;
            dom.logOverlay.dataset.currentLogPath = resolvedPath;
            if (dom.logContent) {
                dom.logContent.dataset.currentLogPath = resolvedPath;
            }
            if (!data.exists) {
                var msg = "Log file does not exist.";
                if (data.looked_at) msg += "\n\nLooked at:\n" + data.looked_at;
                dom.logContent.textContent = msg;
                return;
            }
            _logTotalLines = parseInt(data.total_lines || 0, 10);
            _logFromLine   = parseInt(data.from_line   || 0, 10);
            _logToLine     = parseInt(data.to_line     || 0, 10);
            _updateLogRangePicker();
            renderLogContent(data.content || "");
        })
        .catch(function (err) {
            dom.logContent.textContent = "Error: " + err;
        });
    }

    function _updateLogRangePicker() {
        var picker = document.getElementById("pl-log-range-picker");
        if (!picker) return;
        var fromEl = document.getElementById("pl-log-from");
        var toEl   = document.getElementById("pl-log-to");
        var totalEl = document.getElementById("pl-log-total");
        if (totalEl) totalEl.textContent = String(_logTotalLines);
        if (fromEl)  fromEl.value = String(_logFromLine + 1);
        if (toEl)    toEl.value   = String(_logToLine);
        picker.hidden = (_logTotalLines <= 500);
    }

    function openLogPopup(cleanLogfile) {
        if (!dom.logOverlay) return;
        state.currentLogfile = String(cleanLogfile || "");
        state.currentLogPath = "";
        _logFromLine = 0;
        _logToLine   = 500;
        _logTotalLines = 0;
        dom.logOverlay.dataset.currentLogfile = state.currentLogfile;
        dom.logOverlay.dataset.currentLogPath = "";
        dom.logOverlay.dataset.currentLogText = "";
        if (dom.logContent) {
            dom.logContent.dataset.currentLogfile = state.currentLogfile;
            dom.logContent.dataset.currentLogPath = "";
            dom.logContent.dataset.currentLogText = "";
        }
        var fname = cleanLogfile.split("/").pop();
        dom.logFilename.textContent = fname;
        dom.logOverlay.style.display = "flex";
        document.body.style.overflow = "hidden";
        _fetchLogRange(cleanLogfile, 0, 500);
    }

    function renderLogContent(text) {
        /* Colour special marker lines, escape everything else.
           Each line is wrapped in a <span> with a data-line index
           so the find bar can target individual lines. */
        dom.logOverlay.dataset.currentLogText = text;
        dom.logContent.dataset.currentLogText = text;
        try {
            var sel = window.getSelection();
            if (sel && !sel.isCollapsed && sel.anchorNode && dom.logContent.contains(sel.anchorNode)) return;
        } catch (_e) {}
        var html = "";
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

    /* ----------------------------------------------------------
       Group summary cards (pid page)
    ---------------------------------------------------------- */
    function renderSummaryCards(summary, groupName) {
        if (!dom.summaryCards) return;
        if (!summary) {
            dom.summaryCards.hidden = true;
            return;
        }
        function setText(el, val) {
            if (el) el.textContent = (val == null || val === "")
                ? "n/a" : String(val);
        }
        setText(dom.sumGroup, groupName || cfg.pid);
        setText(dom.sumStart, summary.start_time);
        setText(dom.sumEnd, summary.end_time);
        setText(dom.sumTotal, summary.total_time);
        setText(dom.sumFailed, summary.n_failed);
        setText(dom.sumPassed, summary.n_passed);
        setText(dom.sumProclog, summary.processing_log);
        dom.summaryCards.hidden = false;
    }

    /* ----------------------------------------------------------
       Summary card filter toggle helpers (pid page)
    ---------------------------------------------------------- */

    /* Reflect the current Finished filter value onto the card highlights
       and onto the "Unfinished only" toolbar button. */
    function syncSummaryCardStates() {
        var cur = String(state.filters["Finished"] || "");
        /* Failed card: active when filter is "0" */
        if (dom.cardFailed) {
            dom.cardFailed.classList.toggle("pl-card--active-fail",
                                            cur === "0");
        }
        /* Passed card: active when filter is "1" */
        if (dom.cardPassed) {
            dom.cardPassed.classList.toggle("pl-card--active-pass",
                                            cur === "1");
        }
        /* Keep the "Unfinished only" button in sync */
        var btnU = document.getElementById("pl-btn-unfinished");
        if (btnU) {
            if (cur === "0") {
                btnU.classList.add("ari-btn--primary");
                btnU.classList.remove("ari-btn--secondary");
            } else {
                btnU.classList.remove("ari-btn--primary");
                btnU.classList.add("ari-btn--secondary");
            }
        }
    }

    /* Set the Finished column filter to filterVal (or clear it when ""),
       sync the filter-row dropdown, the toolbar button, and card highlights. */
    function setFinishedFilter(filterVal) {
        var val = String(filterVal || "");
        if (val) {
            state.filters["Finished"] = val;
        } else {
            delete state.filters["Finished"];
        }
        /* Sync the filter-row dropdown */
        if (dom.filterRow) {
            var finSel = dom.filterRow.querySelector(
                '[data-col="Finished"]');
            if (finSel) {
                finSel.value = val;
            }
        }
        if (state.pagedMode) {
            _resetAndFetchPage();
        } else {
            filterRows();
        }
        syncSummaryCardStates();
    }

    /* ----------------------------------------------------------
       Fail report overlay (pid page)
    ---------------------------------------------------------- */
    function showReportStep(name) {
        if (!dom.reportSteps) return;
        Object.keys(dom.reportSteps).forEach(function (key) {
            var el = dom.reportSteps[key];
            if (el) el.hidden = (key !== name);
        });
    }

    /* Format age in hours to a human string. */
    function formatAgeHours(h) {
        if (h < 0) return "unknown time ago";
        if (h < 1) {
            var m = Math.round(h * 60);
            return m <= 1 ? "just now" : m + " min ago";
        }
        if (h < 24) return Math.round(h) + "h ago";
        return Math.round(h / 24) + "d ago";
    }

    /* Populate the start-step UI from a cache-status response. */
    function applyReportCacheStatus(status) {
        var cached     = status && status.cached;
        var ageHours   = cached ? (status.age_hours || 0) : -1;
        var tokenValid = cached && status.token_valid;
        var stale      = cached && ageHours >= 24;

        /* Show / configure buttons */
        if (dom.reportGenerate) {
            dom.reportGenerate.hidden   = cached;
        }
        if (dom.reportRegenerate) {
            dom.reportRegenerate.hidden = !cached;
        }
        if (dom.reportUseCached) {
            dom.reportUseCached.hidden = !tokenValid;
        }

        /* Cache banner */
        if (cached && dom.reportCacheBanner && dom.reportCacheAge) {
            var ageText = formatAgeHours(ageHours);
            dom.reportCacheAge.textContent =
                "Last generated: " + ageText;
            dom.reportCacheBanner.hidden = false;
            dom.reportCacheBanner.className =
                "pl-report-cache-banner" +
                (stale ? " pl-report-cache-banner--stale" : "");
            if (stale) {
                dom.reportCacheAge.textContent +=
                    " — report may be outdated, consider regenerating";
            }
        } else if (dom.reportCacheBanner) {
            dom.reportCacheBanner.hidden = true;
        }

        /* Wire "use cached" button for this status */
        if (dom.reportUseCached && tokenValid) {
            dom.reportUseCached.onclick = function () {
                applyReportResult({
                    download_url: status.download_url || "#",
                    share_url:    status.share_url || "",
                    filename:     status.filename || "fail_report.pdf",
                    age_hours:    ageHours,
                    error_groups: [],   /* no analyser for cached */
                    _from_cache: true,
                });
            };
        }
    }

    function openReportOverlay() {
        if (!dom.reportOverlay) return;
        showReportStep("checking");
        dom.reportOverlay.style.display = "flex";
        document.body.style.overflow = "hidden";

        /* Fetch cache status, then show start step. */
        var infoUrl = cfg.failReportInfoUrl;
        if (!infoUrl) {
            showReportStep("start");
            return;
        }
        fetch(infoUrl + "?profile_id=" +
              encodeURIComponent(cfg.profileId || "") +
              "&pid=" + encodeURIComponent(cfg.pid || ""))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                applyReportCacheStatus(data);
                showReportStep("start");
            })
            .catch(function () {
                showReportStep("start");
            });
    }

    /* Populate the done step from a generation (or cache) result. */
    function applyReportResult(data) {
        var dlUrl = data.download_url || "#";
        var dlFilename = data.filename || "fail_report.pdf";
        if (dom.reportDownload) {
            dom.reportDownload.href = dlUrl;
            dom.reportDownload.setAttribute("download", dlFilename);
            dom.reportDownload.onclick = function (e) {
                e.preventDefault();
                triggerFileDownload(dlUrl);
            };
        }
        if (dom.reportShare) {
            dom.reportShare.dataset.shareUrl = data.share_url || "";
        }
        if (dom.reportExpiry) {
            dom.reportExpiry.textContent = data.expires_hours
                ? ("Link valid for " + data.expires_hours + "h")
                : "";
        }
        /* Show age banner in done step */
        if (dom.reportDoneAge) {
            var ageH = data.age_hours;
            if (typeof ageH === "number" && ageH >= 0 && data._from_cache) {
                var stale = ageH >= 24;
                dom.reportDoneAge.textContent =
                    "Using cached report from " + formatAgeHours(ageH) +
                    (stale ? " (outdated)" : "");
                dom.reportDoneAge.hidden = false;
                dom.reportDoneAge.className =
                    "pl-report-cache-banner" +
                    (stale ? " pl-report-cache-banner--stale" : "");
            } else {
                dom.reportDoneAge.hidden = true;
            }
        }
        if (!data._from_cache) {
            renderAnalyserTable(data.error_groups || []);
            var analyser = document.getElementById("pl-report-analyser");
            if (analyser) analyser.hidden = false;
        } else {
            var analyser2 = document.getElementById("pl-report-analyser");
            if (analyser2) analyser2.hidden = true;
        }
        showReportStep("done");
    }

    function closeReportOverlay() {
        if (!dom.reportOverlay) return;
        dom.reportOverlay.style.display = "none";
        document.body.style.overflow = "";
    }

    /* Trigger a file download via a hidden iframe — works synchronously
       inside a click handler so browsers don't block it as a popup, and
       doesn't navigate away from the page.  The server must send
       Content-Disposition: attachment for the save dialog to appear. */
    function triggerFileDownload(url) {
        var iframe = document.createElement("iframe");
        iframe.style.display = "none";
        iframe.src = url;
        document.body.appendChild(iframe);
        setTimeout(function () {
            if (iframe.parentNode) {
                iframe.parentNode.removeChild(iframe);
            }
        }, 10000);
    }

    /* Mirror of fail_report.build_display_template.
       Returns {display, varUnique} where constants are inlined and
       varying vars are renumbered sequentially from 1. */
    function buildDisplayTemplate(template, varUnique) {
        var constant = {};
        var varyingKeys = [];
        Object.keys(varUnique || {}).forEach(function (k) {
            var vals = varUnique[k] || [];
            if (vals.length === 1) {
                constant[k] = vals[0];
            } else if (vals.length > 1) {
                varyingKeys.push(k);
            }
        });
        varyingKeys.sort(function (a, b) {
            return parseInt(a, 10) - parseInt(b, 10);
        });
        var renumber = {};
        varyingKeys.forEach(function (k, i) {
            renumber[k] = String(i + 1);
        });
        var display = (template || "").replace(
            /\{\{(\d+)\}\}/g,
            function (match, k) {
                if (Object.prototype.hasOwnProperty.call(constant, k)) {
                    return constant[k];
                }
                if (Object.prototype.hasOwnProperty.call(renumber, k)) {
                    return "{{" + renumber[k] + "}}";
                }
                return match;
            }
        );
        var newVarUnique = {};
        varyingKeys.forEach(function (k, i) {
            newVarUnique[String(i + 1)] = varUnique[k];
        });
        return { display: display, varUnique: newVarUnique };
    }

    function renderAnalyserTable(groups) {
        if (!dom.reportAnalyserBody) return;
        dom.reportAnalyserBody.innerHTML = "";
        if (!groups || !groups.length) {
            var tr = document.createElement("tr");
            tr.innerHTML = "<td colspan=\"4\" class=\"pl-report-empty\">" +
                "No grouped errors found.</td>";
            dom.reportAnalyserBody.appendChild(tr);
            return;
        }
        groups.forEach(function (grp, idx) {
            var raw = buildDisplayTemplate(
                grp.template || grp.message || "",
                grp.var_unique || {}
            );
            var display   = raw.display;
            var varUnique = raw.varUnique;
            var varyingKeys = Object.keys(varUnique).sort(function (a, b) {
                return parseInt(a, 10) - parseInt(b, 10);
            });
            var hasVars  = varyingKeys.length > 0;
            var toggleId = "pl-blk-" + idx;

            /* Summary row */
            var tr = document.createElement("tr");
            tr.innerHTML =
                "<td>" + (idx + 1) + "</td>" +
                "<td class=\"pl-report-num\">" + esc(grp.count) + "</td>" +
                "<td class=\"pl-report-num\">" + esc(grp.recipe_count) + "</td>" +
                "<td class=\"pl-report-msg\">" +
                    "<code class=\"pl-report-template\">" +
                        esc(display) + "</code>" +
                    (hasVars
                        ? " <button class=\"pl-blk-toggle ari-btn ari-btn--sm " +
                          "ari-btn--secondary\" data-target=\"" + toggleId + "\">" +
                          "show vars</button>"
                        : "") +
                "</td>";
            dom.reportAnalyserBody.appendChild(tr);

            /* Expandable variable-values row — show ALL values */
            if (hasVars) {
                var detailTr = document.createElement("tr");
                detailTr.id = toggleId;
                detailTr.className = "pl-blk-detail";
                detailTr.hidden = true;
                var varsHtml = varyingKeys.map(function (k) {
                    var vals = varUnique[k] || [];
                    return "<div class=\"pl-report-var\">" +
                        "<span class=\"pl-report-var__key\">{{" + esc(k) +
                        "}}</span> &rarr; " +
                        vals.map(function (v) {
                            return "<code>" + esc(v) + "</code>";
                        }).join(", ") +
                        "</div>";
                }).join("");
                detailTr.innerHTML =
                    "<td></td><td></td><td></td>" +
                    "<td class=\"pl-report-msg\">" + varsHtml + "</td>";
                dom.reportAnalyserBody.appendChild(detailTr);
            }
        });

        /* Wire toggle buttons */
        if (dom.reportAnalyserBody) {
            dom.reportAnalyserBody.addEventListener("click", function (e) {
                var btn = e.target.closest(".pl-blk-toggle");
                if (!btn) return;
                var targetId = btn.getAttribute("data-target");
                var detail = document.getElementById(targetId);
                if (!detail) return;
                detail.hidden = !detail.hidden;
                btn.textContent = detail.hidden ? "show vars" : "hide vars";
            });
        }
    }

    function generateReport() {
        showReportStep("loading");
        fetch(cfg.failReportUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                profile_id: cfg.profileId,
                pid: cfg.pid,
            }),
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
            applyReportResult(data);
        })
        .catch(function (err) {
            if (dom.reportErrorMsg) {
                dom.reportErrorMsg.textContent =
                    "Report generation failed: " + String(err);
            }
            showReportStep("error");
        });
    }

    function toggleLogMaximize() {
        if (!dom.logOverlay) return;
        var on = dom.logOverlay.classList.toggle("pl-log-overlay--max");
        if (dom.logMaximize) {
            var icon = dom.logMaximize.querySelector("i");
            if (icon) {
                icon.className = on
                    ? "fa-solid fa-compress"
                    : "fa-solid fa-expand";
            }
            dom.logMaximize.title = on
                ? "Restore the log viewer"
                : "Maximize the log viewer";
        }
    }

    function closeLogPopup() {
        if (!dom.logOverlay) return;
        dom.logOverlay.style.display = "none";
        dom.logOverlay.classList.remove("pl-log-overlay--max");
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
       Server-side pagination helpers (pid page only)
    ---------------------------------------------------------- */

    /** Build a cache key string from current page + sort + filters. */
    function _pagedCacheKey(page) {
        return JSON.stringify({
            p: page,
            pp: state.perPage,
            sc: state.sortCol,
            sd: state.sortDir,
            f: state.filters,
        });
    }

    /** Invalidate the page cache (called when filters or sort change). */
    function _invalidatePageCache() {
        state.pageCache = {};
        state.pageCacheTimestamp = Date.now();
    }

    /** Fetch one page from the server; resolve with the data object. */
    function _fetchPage(page) {
        var body = {
            profile_id: cfg.profileId,
            pid: cfg.pid,
            paged: true,
            page: page,
            per_page: state.perPage,
            sort_col: state.sortCol || "",
            sort_dir: state.sortDir || "asc",
            filters: state.filters || {},
        };
        return fetch(cfg.apiUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(body),
        }).then(function (r) {
            if (!r.ok) {
                return r.json().then(function (e) {
                    throw new Error(e.error || r.statusText);
                });
            }
            return r.json();
        });
    }

    /**
     * Load one page of results, update DOM, and pre-fetch the next page.
     * @param {number} page
     * @param {boolean} [skipCache]
     */
    function loadPagedData(page, skipCache) {
        var key = _pagedCacheKey(page);
        if (!skipCache && state.pageCache[key]) {
            _applyPagedData(state.pageCache[key], page);
            _prefetchPage(page + 1);
            return;
        }
        setRefreshBusy(true);
        _fetchPage(page)
            .then(function (data) {
                state.pageCache[key] = data;
                _applyPagedData(data, page);
                _prefetchPage(page + 1);
            })
            .catch(function (err) {
                if (dom.tbody) {
                    dom.tbody.innerHTML =
                        "<tr><td colspan=\"10\" " +
                        "style=\"color:var(--ari-error,#f44);padding:1rem\">" +
                        "Error loading page: " + esc(String(err)) +
                        "</td></tr>";
                }
            })
            .then(function () { setRefreshBusy(false); });
    }

    /** Apply a paged API response: update state, rebuild header, render. */
    function _applyPagedData(data, page) {
        state.pagedMode  = true;
        state.serverTotal = parseInt(data.total || 0, 10);
        state.page        = page;
        state.allRows     = data.rows || [];
        state.filteredRows = data.rows || [];  /* server already filtered */

        if (!state.columns.length) {
            state.columns      = data.columns || [];
            state.dropdownCols = data.dropdown_columns || [];
            if (state.columns.indexOf("Recipe name") >= 0 &&
                    state.columns.indexOf(ACTIONS_COL) < 0) {
                state.columns = state.columns.concat([ACTIONS_COL]);
            }
        }

        setLastUpdatedText(data.last_updated || "");

        if (data.group_name && dom.groupName) {
            dom.groupName.textContent = data.group_name;
        }
        renderSummaryCards(data.summary || null, data.group_name);
        buildHeader();
        _renderPagedPage();
        openLogFromUrlParam();
    }

    /** Re-render the current page (rows already in state.allRows). */
    function _renderPagedPage() {
        var total      = state.serverTotal;
        var pp         = state.perPage || 50;
        var totalPages = pp === 0 ? 1 : Math.max(1, Math.ceil(total / pp));
        var page       = state.page;

        if (dom.tbody) {
            if (!state.allRows.length) {
                dom.tbody.innerHTML =
                    "<tr><td colspan=\"" + state.columns.length +
                    "\" class=\"ot-loading\">No results.</td></tr>";
            } else {
                var html = "";
                state.allRows.forEach(function (row) {
                    html += "<tr class=\"ot-row\">";
                    state.columns.forEach(function (col) {
                        html += "<td class=\"ot-cell\">" +
                            renderCell(col, row[col], row) + "</td>";
                    });
                    html += "</tr>";
                });
                dom.tbody.innerHTML = html;
            }
        }

        if (dom.rowSummary) {
            var start = pp === 0 ? 1 : (page - 1) * pp + 1;
            var end   = pp === 0 ? total : Math.min(page * pp, total);
            dom.rowSummary.textContent =
                start + "–" + end + " of " + total + " rows";
        }
        if (dom.pageInfo)  dom.pageInfo.textContent  =
            "Page " + page + " of " + totalPages;
        if (dom.pageTotal) dom.pageTotal.textContent = String(totalPages);
        if (dom.pageInput) dom.pageInput.value        = String(page);

        var atFirst = page <= 1, atLast = page >= totalPages;
        if (dom.btnFirst) dom.btnFirst.disabled = atFirst;
        if (dom.btnPrev)  dom.btnPrev.disabled  = atFirst;
        if (dom.btnNext)  dom.btnNext.disabled  = atLast;
        if (dom.btnLast)  dom.btnLast.disabled  = atLast;

        /* wire log-file popup buttons and runstring buttons */
        if (dom.logOverlay) {
            wireLogButtons();
        }
        wireActionButtons();
        wireRunstringButtons();
    }

    /** Pre-fetch a page in the background (low-priority, no DOM update). */
    function _prefetchPage(page) {
        var key = _pagedCacheKey(page);
        if (state.pageCache[key]) return;  /* already cached */
        /* Use requestIdleCallback if available, else a short timeout. */
        var go = function () {
            if (state.pageCache[key]) return;
            _fetchPage(page).then(function (data) {
                state.pageCache[key] = data;
            }).catch(function () {});
        };
        if (typeof requestIdleCallback === "function") {
            requestIdleCallback(go, {timeout: 2000});
        } else {
            setTimeout(go, 300);
        }
    }

    /**
     * Reset to page 1 and reload (called when filter or sort changes).
     * Uses a debounce so rapid keystrokes don't flood the server.
     */
    function _resetAndFetchPage() {
        if (state.filterDebounceTimer) {
            clearTimeout(state.filterDebounceTimer);
        }
        state.filterDebounceTimer = setTimeout(function () {
            _invalidatePageCache();
            state.page = 1;
            loadPagedData(1, true);
        }, 300);
    }

    /* ----------------------------------------------------------
       Load data from server
    ---------------------------------------------------------- */
    function loadData(forceRefresh) {
        /* For the PID page: use server-side pagination so large tables
           (e.g. 391 K rows) don't transfer all data at once. */
        if (cfg.mode === "pid") {
            _invalidatePageCache();
            state.page = 1;
            loadPagedData(1, true);
            return;
        }

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
            /* Append the synthetic Actions column when recipe rows exist. */
            if (state.columns.indexOf("Recipe name") >= 0 &&
                    state.columns.indexOf(ACTIONS_COL) < 0) {
                state.columns = state.columns.concat([ACTIONS_COL]);
            }
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

            /* On pid page, render the group summary cards */
            if (cfg.mode === "pid") {
                renderSummaryCards(data.summary || null, data.group_name);
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
                /* also reset unfinished toggle and card highlights */
                var btn = document.getElementById(
                    "pl-btn-unfinished"
                );
                if (btn) {
                    btn.classList.remove("ari-btn--primary");
                    btn.classList.add("ari-btn--secondary");
                }
                syncSummaryCardStates();
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
                    syncSummaryCardStates();
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
                    syncSummaryCardStates();
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
                state.perPage = parseInt(dom.perpage.value, 10) || 50;
                if (state.pagedMode) {
                    _invalidatePageCache();
                    state.page = 1;
                    loadPagedData(1, true);
                } else {
                    state.page = 1;
                    renderPage();
                }
            });
        }

        if (dom.btnRefresh) {
            dom.btnRefresh.addEventListener("click", function () {
                if (state.pagedMode) {
                    _invalidatePageCache();
                    loadPagedData(state.page, true);
                } else {
                    loadData(true);
                }
            });
        }

        if (dom.btnFirst) {
            dom.btnFirst.addEventListener("click", function () {
                if (state.pagedMode) { loadPagedData(1); }
                else { state.page = 1; renderPage(); }
            });
        }
        if (dom.btnPrev) {
            dom.btnPrev.addEventListener("click", function () {
                if (state.pagedMode) {
                    if (state.page > 1) loadPagedData(state.page - 1);
                } else {
                    if (state.page > 1) { state.page--; renderPage(); }
                }
            });
        }
        if (dom.btnNext) {
            dom.btnNext.addEventListener("click", function () {
                if (state.pagedMode) {
                    var pp = state.perPage || 50;
                    var tp = Math.max(1, Math.ceil(state.serverTotal / pp));
                    if (state.page < tp) loadPagedData(state.page + 1);
                } else {
                    var perPage = state.perPage;
                    var totalPages = perPage === 0 ? 1
                        : Math.max(1, Math.ceil(
                            state.filteredRows.length / perPage));
                    if (state.page < totalPages) {
                        state.page++; renderPage();
                    }
                }
            });
        }
        if (dom.btnLast) {
            dom.btnLast.addEventListener("click", function () {
                if (state.pagedMode) {
                    var pp2 = state.perPage || 50;
                    var last = Math.max(1, Math.ceil(state.serverTotal / pp2));
                    loadPagedData(last);
                } else {
                    var perPage = state.perPage;
                    state.page = perPage === 0 ? 1
                        : Math.max(1, Math.ceil(
                            state.filteredRows.length / perPage));
                    renderPage();
                }
            });
        }

        if (dom.pageInput) {
            dom.pageInput.addEventListener("change", function () {
                var n = parseInt(dom.pageInput.value, 10);
                if (state.pagedMode) {
                    var pp3 = state.perPage || 50;
                    var tp3 = Math.max(1, Math.ceil(state.serverTotal / pp3));
                    if (!isNaN(n) && n >= 1 && n <= tp3) loadPagedData(n);
                } else {
                    var perPage = state.perPage;
                    var totalPages = perPage === 0 ? 1
                        : Math.max(1, Math.ceil(
                            state.filteredRows.length / perPage));
                    if (!isNaN(n) && n >= 1 && n <= totalPages) {
                        state.page = n; renderPage();
                    }
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
                    closeReportOverlay();
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

        /* Log viewer maximize toggle (pid page) */
        if (dom.logMaximize) {
            dom.logMaximize.addEventListener("click", toggleLogMaximize);
        }

        /* Log line-range picker */
        var rangeGoBtn   = document.getElementById("pl-log-range-go");
        var rangeTailBtn = document.getElementById("pl-log-range-tail");
        if (rangeGoBtn) {
            rangeGoBtn.addEventListener("click", function () {
                var fromEl = document.getElementById("pl-log-from");
                var toEl   = document.getElementById("pl-log-to");
                var from1  = Math.max(1, parseInt((fromEl && fromEl.value) || "1", 10));
                var to1    = Math.max(from1, parseInt((toEl && toEl.value) || "500", 10));
                _fetchLogRange(
                    state.currentLogfile,
                    from1 - 1,   /* convert 1-based UI to 0-based API */
                    to1
                );
            });
        }
        if (rangeTailBtn) {
            rangeTailBtn.addEventListener("click", function () {
                if (!_logTotalLines) return;
                var window500 = Math.max(0, _logTotalLines - 500);
                var fromEl = document.getElementById("pl-log-from");
                var toEl   = document.getElementById("pl-log-to");
                if (fromEl) fromEl.value = String(window500 + 1);
                if (toEl)   toEl.value   = String(_logTotalLines);
                _fetchLogRange(state.currentLogfile, window500, _logTotalLines);
            });
        }

        if (cfg.mode === "pid") {
            /* Regenerate button (same action as Generate) */
            if (dom.reportRegenerate) {
                dom.reportRegenerate.addEventListener(
                    "click", generateReport);
            }
            /* Back button on done step → return to start */
            if (dom.reportBack) {
                dom.reportBack.addEventListener("click", function () {
                    /* Re-fetch status so buttons are current */
                    fetch((cfg.failReportInfoUrl || "") +
                          "?profile_id=" +
                          encodeURIComponent(cfg.profileId || "") +
                          "&pid=" + encodeURIComponent(cfg.pid || ""))
                        .then(function (r) { return r.json(); })
                        .then(function (d) {
                            applyReportCacheStatus(d);
                        })
                        .catch(function () {})
                        .then(function () {
                            showReportStep("start");
                        });
                });
            }

            /* Summary card filter toggles */
            if (dom.cardFailed) {
                dom.cardFailed.addEventListener("click", function () {
                    var active = state.filters["Finished"] === "0";
                    setFinishedFilter(active ? "" : "0");
                });
            }
            if (dom.cardPassed) {
                dom.cardPassed.addEventListener("click", function () {
                    var active = state.filters["Finished"] === "1";
                    setFinishedFilter(active ? "" : "1");
                });
            }

            /* Fail report overlay */
            if (dom.reportBtnOpen) {
                dom.reportBtnOpen.addEventListener(
                    "click", openReportOverlay);
            }
            if (dom.reportClose) {
                dom.reportClose.addEventListener(
                    "click", closeReportOverlay);
            }
            if (dom.reportBackdrop) {
                dom.reportBackdrop.addEventListener(
                    "click", closeReportOverlay);
            }
            if (dom.reportGenerate) {
                dom.reportGenerate.addEventListener(
                    "click", generateReport);
            }
            if (dom.reportRetry) {
                dom.reportRetry.addEventListener(
                    "click", generateReport);
            }
            if (dom.reportShare) {
                dom.reportShare.addEventListener("click", function () {
                    var url = dom.reportShare.dataset.shareUrl || "";
                    if (url) {
                        copyToClipboard(url, "Share link copied");
                    }
                });
            }

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
