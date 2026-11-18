(function () {
    "use strict";
    window.ARI_SEARCH_MATCH = function (items, query) {
        const terms = (String(query).toLowerCase().match(/"[^"]+"|\S+/g) || [])
            .map((term) => term.replace(/^"|"$/g, ""));
        if (!terms.length) return [];
        return items.filter((item) => terms.every((term) =>
            String(item.keywords || "").toLowerCase().includes(term)));
    };
}());