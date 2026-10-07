(function () {
    "use strict";

    function init() {
        const root = document.getElementById("rid-root");
        if (!root || root.dataset.initialized) return;
        root.dataset.initialized = "true";
        const config = window.ARI_RUN_IDS || {};
        const instruments = config.instruments || [];
        const columns = ["run_id", "pi", "comment"];
        const labels = {run_id: "RUN ID", pi: "PI", comment: "COMMENT"};
        const state = {
            instrument: null, rows: [], draft: null, loading: false,
            loaded: false, request: 0, filters: {}, search: "", missingPI: false,
            savingAll: false,
            importing: false, exporting: false,
            sort: "run_id", direction: "asc", page: 1, perPage: 50,
            pages: 1, url: window.location.href
        };
        const element = (name) => document.getElementById("rid-" + name);
        const text = (value) => value == null ? "" : String(value);
        const dirty = (row) => row.create || columns.some(
            (column) => row[column] !== row.original[column]
        );
        const allRows = () => state.draft ? [state.draft, ...state.rows] : state.rows;
        const saving = () => state.savingAll || state.importing || allRows().some((row) => row.busy);
        const unsaved = () => allRows().some(dirty);

        function updateSaveAll() {
            const button = element("save-all");
            button.disabled = !state.loaded || state.loading || saving() || !unsaved();
            button.querySelector("i").className = "fa-solid " + (state.savingAll ? "fa-spinner fa-spin" : "fa-floppy-disk");
            button.querySelector("span").textContent = state.savingAll ? "Saving..." : "Save All";
        }

        function notice(message, error = false) {
            const target = element("notice");
            target.textContent = message;
            target.hidden = !message;
            target.classList.toggle("rid-notice--error", error);
            target.setAttribute("role", error ? "alert" : "status");
        }

        function renderHealth(health) {
            if (!health) return;
            const status = ["ok", "warning", "error"].includes(health.status) ? health.status : "error";
            element("health").className = "ari-ap-status ari-ap-status--" + status;
            const headline = element("health-headline");
            const icon = document.createElement("i");
            icon.className = "fa-solid " + ({ok: "fa-circle-check", warning: "fa-triangle-exclamation", error: "fa-circle-xmark"}[status]);
            icon.setAttribute("aria-hidden", "true");
            headline.replaceChildren(icon, document.createTextNode(" " + text(health.message)));
            element("health-details").replaceChildren();
            (health.details || []).forEach((detail) => {
                const item = document.createElement("li");
                item.textContent = text(detail);
                element("health-details").append(item);
            });
        }

        function updateUrl() {
            const url = new URL(window.location.href);
            if (state.instrument) url.searchParams.set("instrument", state.instrument);
            const filter = state.filters.run_id;
            if (filter && filter.exact && filter.value) {
                url.searchParams.set("run_id", filter.value);
            } else {
                url.searchParams.delete("run_id");
            }
            window.history.replaceState(null, "", url);
            state.url = url.href;
        }

        function canDiscard() {
            if (saving()) {
                notice("A save is in progress. Wait before leaving this instrument.", true);
                return false;
            }
            return !unsaved() || window.confirm("Discard unsaved RUN ID edits?");
        }

        function makeRow(source, create = false) {
            const values = {};
            columns.forEach((column) => { values[column] = text(source[column]); });
            return {...values, original: {...values}, create, busy: false, error: ""};
        }

        async function requestJson(url, options) {
            const response = await fetch(url, options);
            let data;
            try {
                data = await response.json();
            } catch {
                throw new Error("Invalid server response (HTTP " + response.status + ").");
            }
            if (!response.ok || data.success !== true) {
                throw new Error(text(data.error || "Request failed (HTTP " + response.status + ")."));
            }
            return data;
        }

        function renderTabs() {
            element("tabs").querySelectorAll("button").forEach((button) => {
                const active = button.dataset.instrument === state.instrument;
                button.classList.toggle("ari-sg-tab--active", active);
                button.setAttribute("aria-selected", String(active));
                button.tabIndex = active ? 0 : -1;
                if (active) element("panel").setAttribute("aria-labelledby", button.id);
            });
        }

        async function load(instrument, runId = null) {
            state.instrument = instrument;
            state.rows = [];
            state.draft = null;
            state.filters = runId === null ? {} : {run_id: {value: runId, exact: true}};
            state.search = "";
            element("search").value = "";
            state.page = 1;
            state.loading = true;
            state.loaded = false;
            const request = ++state.request;
            element("panel").hidden = false;
            renderTabs();
            buildHeaders();
            render();
            notice("");
            updateUrl();
            try {
                const url = new URL(config.listUrl, window.location.href);
                url.searchParams.set("instrument", instrument);
                const data = await requestJson(url);
                if (!Array.isArray(data.rows)) throw new Error("The server did not return RUN ID rows.");
                if (request !== state.request) return;
                state.rows = data.rows.map((row) => makeRow(row));
                state.loaded = true;
                renderHealth(data.health);
            } catch (error) {
                if (request !== state.request) return;
                notice(error.message, true);
                renderHealth({status: "error", message: "RUN ID health could not be loaded.", details: []});
            } finally {
                if (request === state.request) {
                    state.loading = false;
                    buildHeaders();
                    render();
                }
            }
        }

        function buildHeaders() {
            element("headers").replaceChildren();
            element("filters").replaceChildren();
            columns.forEach((column) => {
                const header = document.createElement("th");
                header.scope = "col";
                header.className = "ot-th";
                const active = state.sort === column;
                header.setAttribute("aria-sort", active ? (state.direction === "asc" ? "ascending" : "descending") : "none");
                if (active) header.classList.add("ot-th--" + state.direction);
                const button = document.createElement("button");
                button.type = "button";
                button.className = "rid-sort";
                button.append(document.createTextNode(labels[column] + " "));
                const icon = document.createElement("i");
                icon.className = "fa-solid ot-th__sort-icon " + (active ? (state.direction === "asc" ? "fa-sort-up" : "fa-sort-down") : "fa-sort");
                icon.setAttribute("aria-hidden", "true");
                button.append(icon);
                button.addEventListener("click", () => {
                    state.direction = active && state.direction === "asc" ? "desc" : "asc";
                    state.sort = column;
                    state.page = 1;
                    buildHeaders();
                    render();
                    element("headers").children[columns.indexOf(column)].querySelector("button").focus();
                });
                header.append(button);
                element("headers").append(header);
                const cell = document.createElement("th");
                cell.className = "ot-filter-cell";
                const values = [...new Set(state.rows.map((row) => row.original[column]))].sort();
                const filter = state.filters[column] || {value: "", exact: false};
                const dropdown = values.length < 10;
                const control = document.createElement(dropdown ? "select" : "input");
                control.className = dropdown ? "ot-filter-select" : "ot-filter-input";
                control.setAttribute("aria-label", "Filter " + labels[column]);
                if (dropdown) {
                    const all = document.createElement("option");
                    all.value = "all";
                    all.textContent = "All";
                    control.append(all);
                    if (filter.value && !values.includes(filter.value)) values.push(filter.value);
                    values.forEach((value) => {
                        const option = document.createElement("option");
                        option.value = JSON.stringify(value);
                        option.textContent = value || "(Empty)";
                        control.append(option);
                    });
                    if (!filter.exact && filter.value) {
                        const current = document.createElement("option");
                        current.value = "current-filter";
                        current.textContent = "Contains: " + filter.value;
                        control.append(current);
                    }
                    control.value = filter.exact ? JSON.stringify(filter.value) : filter.value ? "current-filter" : "all";
                } else {
                    control.type = "search";
                    control.value = filter.value;
                    control.placeholder = filter.exact ? "Exact RUN ID" : "Filter " + labels[column];
                }
                control.addEventListener(dropdown ? "change" : "input", () => {
                    if (dropdown && control.value === "all") delete state.filters[column];
                    else if (dropdown && control.value === "current-filter") state.filters[column] = filter;
                    else state.filters[column] = {value: dropdown ? JSON.parse(control.value) : control.value, exact: dropdown};
                    state.page = 1;
                    updateUrl();
                    render();
                });
                cell.append(control);
                element("filters").append(cell);
            });
        }

        function filteredRows() {
            const query = state.search.toLocaleLowerCase();
            return state.rows.filter((row) => {
                const values = row.original;
                if (state.missingPI && values.pi.trim()) return false;
                if (query && !columns.some((column) => values[column].toLocaleLowerCase().includes(query))) return false;
                return columns.every((column) => {
                    const filter = state.filters[column];
                    if (!filter) return true;
                    return filter.exact ? values[column] === filter.value : values[column].toLocaleLowerCase().includes(filter.value.toLocaleLowerCase());
                });
            }).sort((left, right) => {
                const order = left.original[state.sort].localeCompare(right.original[state.sort], undefined, {numeric: true});
                return state.direction === "asc" ? order : -order;
            });
        }

        function iconButton(label, icon, action) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "ari-btn ari-btn--sm ari-btn--secondary rid-icon-button";
            button.title = label;
            button.setAttribute("aria-label", label);
            const glyph = document.createElement("i");
            glyph.className = "fa-solid " + icon;
            glyph.setAttribute("aria-hidden", "true");
            button.append(glyph);
            button.addEventListener("click", action);
            return button;
        }

        function renderRow(row) {
            const target = document.createElement("tr");
            target.className = "ot-row";
            target.classList.toggle("rid-row--draft", row.create);
            target.setAttribute("aria-busy", String(row.busy));
            let saveButton;
            let cancelButton;
            const updateActions = () => {
                const changed = dirty(row);
                target.classList.toggle("rid-row--dirty", changed);
                saveButton.disabled = !changed || row.busy || state.savingAll || state.importing;
                cancelButton.hidden = !changed;
                cancelButton.disabled = row.busy || state.savingAll || state.importing;
                saveButton.firstChild.className = "fa-solid " + (row.busy ? "fa-spinner fa-spin" : "fa-floppy-disk");
                saveButton.setAttribute("aria-label", row.busy ? "Saving RUN ID" : "Save RUN ID " + row.run_id);
                updateSaveAll();
            };
            columns.forEach((column) => {
                const cell = document.createElement("td");
                cell.className = "ot-cell";
                if (column === "run_id" && !row.create) {
                    const link = document.createElement("a");
                    const query = new URLSearchParams({
                        fo_tab: "run-id", fo_value: row.run_id,
                        instrument: state.instrument, fo_search: "1"
                    });
                    link.href = "/search?" + query.toString();
                    link.className = "ari-link";
                    link.textContent = row.run_id;
                    link.title = "Find objects for RUN ID " + row.run_id;
                    cell.append(link);
                } else {
                    const input = document.createElement(column === "comment" ? "textarea" : "input");
                    input.className = "rid-edit";
                    input.value = row[column];
                    input.disabled = row.busy || state.savingAll || state.importing;
                    input.setAttribute("aria-label", labels[column] + " for " + (row.create ? "new RUN ID" : row.run_id));
                    if (column === "comment") input.rows = 1;
                    else input.type = "text";
                    input.addEventListener("input", () => {
                        row[column] = input.value;
                        updateActions();
                    });
                    cell.append(input);
                }
                if (column === "comment") {
                    const editor = document.createElement("div");
                    editor.className = "rid-comment-editor";
                    editor.append(cell.firstChild);
                    const actions = document.createElement("div");
                    actions.className = "rid-row-actions";
                    saveButton = iconButton("Save RUN ID", "fa-floppy-disk", () => save(row));
                    cancelButton = iconButton("Revert edits", "fa-rotate-left", () => {
                        if (row.create) state.draft = null;
                        else Object.assign(row, row.original, {error: ""});
                        render();
                    });
                    actions.append(saveButton, cancelButton);
                    editor.append(actions);
                    cell.append(editor);
                    if (row.error) {
                        const error = document.createElement("div");
                        error.className = "rid-row-error";
                        error.setAttribute("role", "alert");
                        error.textContent = row.error;
                        cell.append(error);
                    }
                }
                target.append(cell);
            });
            updateActions();
            return target;
        }

        function render() {
            const body = element("body");
            body.replaceChildren();
            element("panel").setAttribute("aria-busy", String(state.loading));
            element("add").disabled = !state.loaded || state.loading || state.savingAll || state.importing;
            element("refresh").disabled = state.loading || saving();
            element("export").disabled = !state.loaded || state.loading || saving() || state.exporting;
            element("import-toggle").disabled = !state.loaded || state.loading || saving();
            element("import").disabled = !state.loaded || state.loading || saving();
            element("import-file").disabled = state.importing;
            element("duplicates").disabled = state.importing;
            updateSaveAll();
            const rows = filteredRows();
            state.pages = Math.max(1, state.perPage ? Math.ceil(rows.length / state.perPage) : 1);
            state.page = Math.max(1, Math.min(state.pages, state.page));
            const start = state.perPage ? (state.page - 1) * state.perPage : 0;
            const pageRows = state.perPage ? rows.slice(start, start + state.perPage) : rows;
            if (state.draft) body.append(renderRow(state.draft));
            pageRows.forEach((row) => body.append(renderRow(row)));
            if (!body.children.length) {
                const placeholder = document.createElement("tr");
                const cell = document.createElement("td");
                cell.colSpan = 3;
                cell.className = "ot-loading";
                cell.textContent = state.loading ? "Loading RUN IDs..." : !state.loaded ? "RUN IDs could not be loaded. Retry using Reload RUN IDs." : state.rows.length ? "No matching RUN IDs." : "No RUN IDs for this instrument.";
                placeholder.append(cell);
                body.append(placeholder);
            }
            element("page-info").textContent = rows.length ? (start + 1) + " - " + (start + pageRows.length) + " of " + rows.length : "0 RUN IDs";
            const changes = allRows().filter(dirty).length;
            if (changes) element("page-info").textContent += " | " + changes + " unsaved";
            element("page").value = state.page;
            element("page").max = state.pages;
            element("page").disabled = state.loading || !rows.length;
            element("page-total").textContent = state.pages;
            element("first").disabled = element("prev").disabled = state.loading || state.page === 1;
            element("next").disabled = element("last").disabled = state.loading || state.page === state.pages;
        }

        async function save(row) {
            if (row.busy || !dirty(row)) return false;
            const runId = row.create ? row.run_id.trim() : row.original.run_id;
            if (!runId) {
                row.error = "RUN ID is required.";
                render();
                return false;
            }
            if (row.create && state.rows.some((existing) => existing.original.run_id === runId)) {
                row.error = "This RUN ID already exists for this instrument.";
                render();
                return false;
            }
            row.busy = true;
            row.error = "";
            render();
            try {
                const data = await requestJson(config.saveUrl, {
                    method: "POST", headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({instrument: state.instrument, run_id: runId, pi: row.pi, comment: row.comment, create: row.create})
                });
                if (!data.row || text(data.row.run_id) !== runId) throw new Error("The server returned an unexpected RUN ID. Reload to verify the save.");
                const saved = makeRow(data.row);
                renderHealth(data.health);
                if (row.create) {
                    state.rows.unshift(saved);
                    state.draft = null;
                } else state.rows[state.rows.indexOf(row)] = saved;
                notice("Saved RUN ID " + runId + ".");
                buildHeaders();
                return true;
            } catch (error) {
                row.error = error.message;
                notice("RUN ID " + runId + " was not saved.", true);
                return false;
            } finally {
                row.busy = false;
                render();
            }
        }

        async function saveAll() {
            if (state.loading || saving()) return;
            const pending = allRows().filter(dirty);
            if (!pending.length) return;
            state.savingAll = true;
            render();
            let saved = 0;
            const failed = [];
            try {
                for (const row of pending) {
                    if (await save(row)) saved += 1;
                    else failed.push(row.run_id.trim() || "new RUN ID");
                }
                const summary = "Saved " + saved + " RUN ID(s).";
                notice(failed.length ? summary + " Not saved: " + failed.join(", ") + ". Edits retained for retry." : summary, failed.length > 0);
            } finally {
                state.savingAll = false;
                render();
            }
        }

        async function exportCsv() {
            if (!state.loaded || state.loading || saving() || state.exporting) return;
            if (unsaved() && !window.confirm("Export saved values only? Pending edits are not included.")) return;
            const instrument = state.instrument;
            const runIds = filteredRows().map((row) => row.original.run_id);
            state.exporting = true;
            render();
            try {
                const response = await fetch(config.exportUrl, {
                    method: "POST", headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({instrument, run_ids: runIds})
                });
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.error || "CSV export failed.");
                }
                const url = URL.createObjectURL(await response.blob());
                const link = document.createElement("a");
                link.href = url;
                link.download = instrument.toLowerCase() + "_run_ids.csv";
                document.body.append(link);
                link.click();
                link.remove();
                setTimeout(() => URL.revokeObjectURL(url), 1000);
                notice("Exported " + runIds.length + " filtered RUN ID(s).");
            } catch (error) {
                notice(error.message, true);
            } finally {
                state.exporting = false;
                render();
            }
        }

        async function importCsv(event) {
            event.preventDefault();
            if (!state.loaded || state.loading || saving()) return;
            if (unsaved()) {
                notice("Save or revert pending edits before importing CSV.", true);
                return;
            }
            const file = element("import-file").files[0];
            if (!file) return;
            if (file.size > 5 * 1024 * 1024) {
                notice("CSV exceeds 5 MB.", true);
                return;
            }
            const policy = element("duplicates").value;
            if (policy === "overwrite" && !window.confirm("Overwrite duplicate PI and comment values, including blanks? The last duplicate CSV row wins.")) return;
            state.importing = true;
            render();
            try {
                const content = await file.text();
                const data = await requestJson(config.importUrl, {
                    method: "POST", headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({instrument: state.instrument, csv: content, duplicate_policy: policy})
                });
                state.rows = data.rows.map((row) => makeRow(row));
                state.page = 1;
                renderHealth(data.health);
                buildHeaders();
                const summary = data.summary;
                notice("Imported CSV: " + summary.added + " added, " + summary.updated + " updated, " + summary.skipped + " skipped." + (summary.duplicates.length ? " Duplicate RUN IDs: " + summary.duplicates.join(", ") + "." : ""));
                element("import-file").value = "";
            } catch (error) {
                notice(error.message, true);
            } finally {
                state.importing = false;
                render();
            }
        }

        element("export").addEventListener("click", exportCsv);
        element("import-toggle").addEventListener("click", () => {
            const panel = element("import-panel");
            panel.hidden = !panel.hidden;
            element("import-toggle").setAttribute("aria-expanded", String(!panel.hidden));
        });
        element("import-panel").addEventListener("submit", importCsv);

        instruments.forEach((instrument, index) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "ari-sg-tab";
            button.id = "rid-tab-" + index;
            button.dataset.instrument = instrument;
            button.textContent = instrument;
            button.setAttribute("role", "tab");
            button.setAttribute("aria-controls", "rid-panel");
            button.addEventListener("click", () => {
                if (instrument !== state.instrument && canDiscard()) load(instrument);
            });
            button.addEventListener("keydown", (event) => {
                let next;
                if (event.key === "ArrowRight") next = (index + 1) % instruments.length;
                if (event.key === "ArrowLeft") next = (index + instruments.length - 1) % instruments.length;
                if (event.key === "Home") next = 0;
                if (event.key === "End") next = instruments.length - 1;
                if (next === undefined) return;
                event.preventDefault();
                if (next !== index && canDiscard()) {
                    load(instruments[next]);
                    element("tabs").children[next].focus();
                }
            });
            element("tabs").append(button);
        });
        element("add").addEventListener("click", () => {
            if (!state.draft) state.draft = makeRow({}, true);
            render();
            element("body").querySelector("input").focus();
        });
        element("save-all").addEventListener("click", saveAll);
        element("refresh").addEventListener("click", () => {
            if (!canDiscard()) return;
            const filter = state.filters.run_id;
            load(state.instrument, filter && filter.exact ? filter.value : null);
        });
        element("search").addEventListener("input", () => {
            state.search = element("search").value;
            state.page = 1;
            render();
        });
        element("missing-pi").addEventListener("change", () => {
            state.missingPI = element("missing-pi").checked;
            state.page = 1;
            render();
        });
        element("clear").addEventListener("click", () => {
            state.filters = {};
            state.search = "";
            state.missingPI = false;
            element("missing-pi").checked = false;
            element("search").value = "";
            state.page = 1;
            updateUrl();
            buildHeaders();
            render();
        });
        element("perpage").addEventListener("change", () => {
            state.perPage = Number(element("perpage").value);
            state.page = 1;
            render();
        });
        ["first", "prev", "next", "last"].forEach((name) => {
            element(name).addEventListener("click", () => {
                state.page = {first: 1, prev: state.page - 1, next: state.page + 1, last: state.pages}[name];
                render();
            });
        });
        const jump = () => {
            state.page = Math.trunc(Number(element("page").value)) || 1;
            render();
        };
        element("page").addEventListener("change", jump);
        element("page").addEventListener("keydown", (event) => {
            if (event.key === "Enter") { event.preventDefault(); jump(); }
        });
        window.addEventListener("beforeunload", (event) => {
            if (unsaved() || saving()) {
                event.preventDefault();
                event.returnValue = "";
            }
        });
        window.addEventListener("popstate", () => {
            if (!instruments.length) return;
            if (!canDiscard()) {
                window.history.replaceState(null, "", state.url);
                return;
            }
            const params = new URL(window.location.href).searchParams;
            const instrument = params.get("instrument");
            load(instruments.includes(instrument) ? instrument : instruments[0], params.get("run_id"));
        });
        if (!instruments.length) {
            notice("You don't have access to any instruments.");
            element("health").hidden = true;
            return;
        }
        const params = new URL(window.location.href).searchParams;
        const requested = params.get("instrument");
        load(instruments.includes(requested) ? requested : instruments[0], params.get("run_id"));
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
}());