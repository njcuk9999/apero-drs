(function () {
    "use strict";
    const config = window.USER_STATISTICS;
    const ui = config.labels;
    const byId = id => document.getElementById("us-" + id);
    const start = byId("start"), end = byId("end");
    const rangeStart = byId("range-start"), rangeEnd = byId("range-end");
    const status = byId("status"), exportButton = byId("export");
    const day = 86400000;
    let boundsStart = 0, controller, sequence = 0, timer;
    let renderQueue = Promise.resolve();
    const roots = [];

    function query() {
        const params = new URLSearchParams();
        if (start.value) params.set("start", start.value);
        if (end.value) params.set("end", end.value);
        params.set("theme", document.documentElement.dataset.theme || "default");
        return params;
    }

    function message(text, error) {
        status.textContent = text;
        status.classList.toggle("us-status--error", !!error);
    }

    function table(kind, rows, columns) {
        const body = byId(kind);
        body.replaceChildren();
        if (!rows.length) {
            const cell = document.createElement("td");
            cell.colSpan = columns.length;
            cell.className = "ot-loading";
            cell.textContent = ui.EMPTY;
            const row = body.insertRow();
            row.append(cell);
        }
        rows.forEach(entry => {
            const row = body.insertRow();
            row.className = "ot-row";
            columns.forEach(key => {
                const cell = row.insertCell();
                cell.className = "ot-cell";
                cell.textContent = entry[key] === "" ? ui.UNKNOWN : entry[key];
            });
        });
    }

    function synchronize(data) {
        start.value = data.start;
        end.value = data.end;
        const today = new Date().toISOString().slice(0, 10);
        const lower = [data.first_day || data.start, data.start].sort()[0];
        const upper = [data.last_day || data.end, data.end, today].sort().pop();
        boundsStart = Date.parse(lower);
        const maximum = Math.round((Date.parse(upper) - boundsStart) / day);
        [rangeStart, rangeEnd].forEach(input => {
            input.max = maximum;
            input.disabled = maximum === 0;
        });
        rangeStart.value = Math.round((Date.parse(data.start) - boundsStart) / day);
        rangeEnd.value = Math.round((Date.parse(data.end) - boundsStart) / day);
        rangeStart.setAttribute("aria-valuetext", data.start);
        rangeEnd.setAttribute("aria-valuetext", data.end);
    }

    async function refresh() {
        const current = ++sequence;
        if (controller) controller.abort();
        controller = new AbortController();
        exportButton.disabled = true;
        if (start.value && end.value && start.value > end.value) {
            message(ui.INVALID, true);
            return;
        }
        message(ui.LOADING);
        byId("filters").setAttribute("aria-busy", "true");
        try {
            const response = await fetch(config.api + "?" + query(), {
                signal: controller.signal, credentials: "same-origin", cache: "no-store"
            });
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.error || ui.ERROR);
            if (current !== sequence) return;
            const data = payload.summary;
            synchronize(data);
            ["total_user_days", "unique_users", "registered_users", "calendar_days"].forEach(key => {
                byId(key).textContent = Number(data[key]).toLocaleString();
            });
            table("countries", data.countries, ["country", "users", "user_days"]);
            table("regions", data.regions, ["country", "region", "users", "user_days"]);
            renderQueue = renderQueue.catch(() => {}).then(async () => {
                if (current !== sequence) return;
                roots.splice(0).forEach(root => {
                    const view = Bokeh.index[root];
                    if (!view) return;
                    const plotDocument = view.model.document;
                    view.remove();
                    if (plotDocument) {
                        plotDocument.clear();
                        const index = Bokeh.documents.indexOf(plotDocument);
                        if (index >= 0) Bokeh.documents.splice(index, 1);
                    }
                });
                for (const kind of ["weekly", "world"]) {
                    if (current !== sequence) return;
                    byId(kind).replaceChildren();
                    await Bokeh.embed.embed_item(payload.plots[kind]);
                    roots.push(payload.plots[kind].root_id);
                }
            });
            await renderQueue;
            if (current !== sequence) return;
            message(data.total_user_days ? data.start + " / " + data.end : ui.EMPTY);
            exportButton.disabled = false;
        } catch (error) {
            if (error.name !== "AbortError" && current === sequence) message(ui.ERROR, true);
        } finally {
            if (current === sequence) byId("filters").removeAttribute("aria-busy");
        }
    }

    function schedule() {
        exportButton.disabled = true;
        sequence += 1;
        if (controller) controller.abort();
        clearTimeout(timer);
        timer = setTimeout(refresh, 180);
    }

    byId("filters").addEventListener("submit", event => event.preventDefault());
    [start, end].forEach(input => input.addEventListener("change", schedule));
    [rangeStart, rangeEnd].forEach(input => input.addEventListener("input", () => {
        if (+rangeStart.value > +rangeEnd.value) {
            if (input === rangeStart) rangeEnd.value = rangeStart.value;
            else rangeStart.value = rangeEnd.value;
        }
        start.value = new Date(boundsStart + Number(rangeStart.value) * day).toISOString().slice(0, 10);
        end.value = new Date(boundsStart + Number(rangeEnd.value) * day).toISOString().slice(0, 10);
        rangeStart.setAttribute("aria-valuetext", start.value);
        rangeEnd.setAttribute("aria-valuetext", end.value);
        schedule();
    }));
    exportButton.addEventListener("click", () => {
        const params = query();
        params.delete("theme");
        byId("download").src = config.pdf + "?" + params;
    });
    document.addEventListener("ari:theme-change", schedule);
    const initial = new URLSearchParams(location.search);
    start.value = initial.get("start") || "";
    end.value = initial.get("end") || "";
    refresh();
}());