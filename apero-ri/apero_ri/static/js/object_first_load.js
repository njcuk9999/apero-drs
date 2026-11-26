/* ==========================================================================
   Object page: first-view loading screen.
   Each section row is ticked off only when its real request finishes
   (object_page.js calls ARI_OBJECT_FIRST_LOADER.done(step, ok)); the bar
   creeps within the current slice so it never looks frozen.
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_OBJECT_FIRST_LOAD;
    var overlay = document.getElementById('op-first-load');
    var loader = { done: function () {} };
    window.ARI_OBJECT_FIRST_LOADER = loader;
    if (!cfg || !overlay) return;

    var fill = document.getElementById('opfl-bar-fill');
    var countEl = document.getElementById('opfl-count');
    var listEl = document.getElementById('opfl-sections');
    var hintEl = document.getElementById('opfl-hint');
    var skipBtn = document.getElementById('opfl-skip');

    var keys = Object.keys(cfg.steps);
    var pending = {};
    var rows = {};
    keys.forEach(function (key) {
        pending[key] = true;
        rows[key] = cfg.steps[key].map(function (label) {
            var li = document.createElement('li');
            li.className = 'opfl-section opfl-section--active';
            var icon = document.createElement('i');
            icon.className = 'opfl-section__icon fa-solid fa-circle-notch fa-spin';
            var text = document.createElement('span');
            text.className = 'opfl-section__label';
            text.textContent = label;
            li.appendChild(icon);
            li.appendChild(text);
            listEl.appendChild(li);
            return li;
        });
    });
    var finished = 0;
    // Fraction of the next slice shown as "in progress".
    var creep = 0;
    var timers = [];
    var closed = false;

    function renderBar() {
        var slice = 1 / keys.length;
        var pct = Math.min(100, (finished + creep) * slice * 100);
        fill.style.width = pct.toFixed(1) + '%';
        countEl.textContent = Math.floor(pct) + '%';
    }

    function close() {
        if (closed) return;
        closed = true;
        timers.forEach(function (id) {
            window.clearInterval(id);
            window.clearTimeout(id);
        });
        overlay.classList.add('opfl-overlay--done');
        window.setTimeout(function () {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        }, 400);
    }

    loader.done = function (key, ok) {
        if (key === '__abort__') {
            close();
            return;
        }
        if (closed || !pending[key]) return;
        delete pending[key];
        finished += 1;
        creep = 0;
        rows[key].forEach(function (li) {
            var failed = (ok === false);
            li.className = 'opfl-section '
                + (failed ? 'opfl-section--failed' : 'opfl-section--done');
            li.firstChild.className = 'opfl-section__icon fa-solid '
                + (failed ? 'fa-triangle-exclamation' : 'fa-check');
        });
        renderBar();
        if (finished >= keys.length) {
            // Let the full bar register before fading out.
            window.setTimeout(close, 450);
        }
    };

    skipBtn.addEventListener('click', close);

    // Ease towards (never reaching) the end of the current slice.
    timers.push(window.setInterval(function () {
        creep += (0.9 - creep) * 0.03;
        renderBar();
    }, 150));
    // Never trap the user: slow sections keep their own plot spinners.
    timers.push(window.setTimeout(function () {
        hintEl.textContent = cfg.slowHint;
    }, cfg.slowAfterMs));
    timers.push(window.setTimeout(close, cfg.closeAfterMs));

    renderBar();
}());
