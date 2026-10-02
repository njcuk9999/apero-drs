/* Client-side docs search: fetch the search index once per session,
 * then filter/autocomplete entirely in the browser. Keeps the
 * server out of the per-keystroke path (the backend already pays
 * once per version to build this list; see docs.get_search_index). */
(function () {
    'use strict';

    var cache = { version: null, items: null, promise: null };

    function escapeHtml(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function currentVersion() {
        var sel = document.getElementById('sidebar-version');
        return sel ? sel.value : '';
    }

    function loadIndex(version) {
        if (cache.version === version && cache.promise) {
            return cache.promise;
        }
        var url = '/docs/_search_index.json' +
            (version ? '?v=' + encodeURIComponent(version) : '');
        cache.version = version;
        cache.promise = fetch(url)
            .then(function (resp) { return resp.json(); })
            .then(function (data) {
                cache.items = Array.isArray(data.items) ? data.items : [];
                return cache.items;
            })
            .catch(function () {
                cache.items = [];
                return cache.items;
            });
        return cache.promise;
    }

    function matchItems(items, query) {
        var q = query.trim().toLowerCase();
        if (!q) return [];
        var terms = q.split(/\s+/).filter(Boolean);
        return items.filter(function (item) {
            return terms.every(function (term) {
                return item.keywords.indexOf(term) !== -1;
            });
        }).slice(0, 15);
    }

    function render(box, items, query) {
        if (!items.length) {
            box.innerHTML = '<div class="ari-doc-search__empty">' +
                'No matching pages.</div>';
            box.hidden = false;
            return;
        }
        box.innerHTML = items.map(function (item) {
            return '<a class="ari-doc-search__item" href="' +
                escapeHtml(item.url) + '">' +
                '<span class="ari-doc-search__item-label">' +
                escapeHtml(item.label) + '</span>' +
                '<span class="ari-doc-search__item-url">' +
                escapeHtml(item.url) + '</span></a>';
        }).join('');
        box.hidden = false;
    }

    function init() {
        var input = document.getElementById('ari-doc-search-input');
        var box = document.getElementById('ari-doc-search-results');
        if (!input || !box) return;

        var debounceTimer = null;

        function runQuery() {
            var query = input.value;
            if (!query.trim()) {
                box.hidden = true;
                box.innerHTML = '';
                return;
            }
            loadIndex(currentVersion()).then(function (items) {
                render(box, matchItems(items, query), query);
            });
        }

        input.addEventListener('input', function () {
            window.clearTimeout(debounceTimer);
            debounceTimer = window.setTimeout(runQuery, 150);
        });
        input.addEventListener('focus', function () {
            if (input.value.trim()) runQuery();
        });
        document.addEventListener('click', function (ev) {
            if (!box.contains(ev.target) && ev.target !== input) {
                box.hidden = true;
            }
        });
        input.addEventListener('keydown', function (ev) {
            if (ev.key === 'Escape') {
                box.hidden = true;
                input.blur();
            } else if (ev.key === 'Enter') {
                var first = box.querySelector('.ari-doc-search__item');
                if (first) {
                    ev.preventDefault();
                    window.location.href = first.getAttribute('href');
                }
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
