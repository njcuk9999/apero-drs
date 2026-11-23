(function () {
    "use strict";
    const root = document.getElementById("search-root");
    if (!root) return;
    const element = (name) => document.getElementById("search-" + name);
    const cache = new Map();
    let matches = [];
    let shown = 0;
    let request = 0;
    function activate(category) {
        element("description").textContent = category === "objects"
            ? "Find an astrophysical object or observation across all data you have access to."
            : "Find documentation and site pages you have access to by word or phrase.";
        ["objects", "pages"].forEach((name) => {
            const active = name === category;
            element(name).hidden = !active;
            element("tab-" + name).setAttribute("aria-selected", String(active));
            element("tab-" + name).classList.toggle("ari-sg-tab--active", active);
        });
    }
    ["objects", "pages"].forEach((name) => element("tab-" + name).addEventListener("click", () => activate(name)));
    function renderMore() {
        const query = element("page-query").value.toLowerCase().trim();
        matches.slice(shown, shown + 30).forEach((item) => {
            const link = document.createElement("a");
            link.className = "search-result";
            const resultUrl = new URL(item.url, location.origin);
            if (item.category === "Documentation") resultUrl.searchParams.set("v", element("version").value);
            link.href = resultUrl.pathname + resultUrl.search + resultUrl.hash;
            const title = document.createElement("div");
            title.className = "search-result-title";
            title.textContent = item.label;
            const meta = document.createElement("div");
            meta.className = "search-result-meta";
            meta.textContent = (item.category || "Documentation") + " · " + item.url;
            const excerpt = document.createElement("div");
            excerpt.className = "search-result-excerpt";
            const content = String(item.keywords || "").replace(/<!--[\s\S]*?-->/g, " ").replace(/\s+/g, " ");
            const terms = (query.match(/"[^"]+"|\S+/g) || []).map((term) => term.replace(/^"|"$/g, ""));
            const positions = terms.map((term) => content.indexOf(term)).filter((position) => position >= 0);
            const position = positions.length ? Math.min(...positions) : 0;
            const start = Math.max(0, position - 65);
            excerpt.textContent = (start ? "... " : "") + content.slice(start, start + 250) + (content.length > start + 250 ? " ..." : "");
            link.append(title, meta, excerpt);
            element("page-results").append(link);
        });
        shown = Math.min(matches.length, shown + 30);
        element("more").hidden = shown >= matches.length;
    }
    async function search(event) {
        if (event) event.preventDefault();
        const query = element("page-query").value.trim();
        const token = ++request;
        element("page-results").replaceChildren();
        element("more").hidden = true;
        if (!query) { element("page-status").textContent = ""; return; }
        element("page-status").textContent = "Searching...";
        const scope = element("scope").value;
        const version = element("version").value;
        const url = new URL(location.href);
        url.searchParams.set("tab", "pages");
        url.searchParams.set("q", query);
        url.searchParams.set("scope", scope);
        url.searchParams.set("v", version);
        history.replaceState(null, "", url);
        try {
            const key = scope + "|" + version;
            if (!cache.has(key)) {
                const response = await fetch("/api/search/index?scope=" + encodeURIComponent(scope) + "&v=" + encodeURIComponent(version));
                if (!response.ok) throw new Error("Search could not be loaded.");
                const data = await response.json();
                cache.set(key, data.items || []);
            }
            if (token !== request) return;
            matches = window.ARI_SEARCH_MATCH(cache.get(key), query);
            shown = 0;
            element("page-status").textContent = matches.length + " matching page(s)";
            renderMore();
        } catch (error) {
            if (token === request) element("page-status").textContent = error.message;
        }
    }
    element("page-form").addEventListener("submit", search);
    element("scope").addEventListener("change", () => { if (element("page-query").value.trim()) search(); });
    element("version").addEventListener("change", () => { if (element("page-query").value.trim()) search(); });
    element("more").addEventListener("click", renderMore);
    const params = new URL(location.href).searchParams;
    if (params.get("tab") === "pages" || params.has("q")) {
        activate("pages");
        element("page-query").value = params.get("q") || "";
        element("scope").value = params.get("scope") === "site" ? "site" : "docs";
        if (params.get("v")) element("version").value = params.get("v");
        if (element("page-query").value) search();
    }
}());