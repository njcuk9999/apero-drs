/* ==========================================================================
   Object page: first-view loading screen.
   Progress advances only when real requests finish (object_page.js calls
   ARI_OBJECT_FIRST_LOADER.done(step)); the bar creeps within the current
   slice and the status line cycles through what is being built.
   ========================================================================== */
(function () {
    'use strict';

    var cfg = window.ARI_OBJECT_FIRST_LOAD;
    var overlay = document.getElementById('op-first-load');
    var loader = { done: function () {} };
    window.ARI_OBJECT_FIRST_LOADER = loader;
    if (!cfg || !overlay) return;

    var fill = document.getElementById('opfl-bar-fill');
    var stepEl = document.getElementById('opfl-step');
    var countEl = document.getElementById('opfl-count');
    var skipBtn = document.getElementById('opfl-skip');

    var keys = Object.keys(cfg.steps);
    var pending = {};
    keys.forEach(function (key) { pending[key] = true; });
    var finished = 0;
    // Fraction of the current step's slice shown as "in progress".
    var creep = 0;
    var phraseIndex = 0;
    var timers = [];
    var closed = false;

    function pendingPhrases() {
        var phrases = [];
        keys.forEach(function (key) {
            if (pending[key]) phrases = phrases.concat(cfg.steps[key]);
        });
        return phrases;
    }

    function renderBar() {
        var slice = 1 / keys.length;
        var pct = (finished + creep) * slice * 100;
        fill.style.width = Math.min(100, pct).toFixed(1) + '%';
        countEl.textContent = finished + ' / ' + keys.length;
    }

    function nextPhrase() {
        var phrases = pendingPhrases();
        if (!phrases.length) return;
        phraseIndex = (phraseIndex + 1) % phrases.length;
        stepEl.textContent = phrases[phraseIndex] + '\u2026';
        // Restart the fade so each new phrase eases in.
        stepEl.classList.remove('opfl-step--swap');
        void stepEl.offsetWidth;
        stepEl.classList.add('opfl-step--swap');
    }

    function close() {
        if (closed) return;
        closed = true;
        timers.forEach(function (id) { window.clearInterval(id); });
        overlay.classList.add('opfl-overlay--done');
        window.setTimeout(function () {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        }, 400);
    }

    loader.done = function (key) {
        if (key === '__abort__') {
            close();
            return;
        }
        if (closed || !pending[key]) return;
        delete pending[key];
        finished += 1;
        creep = 0;
        renderBar();
        if (finished >= keys.length) {
            // Let the full bar register before fading out.
            window.setTimeout(close, 350);
        } else {
            nextPhrase();
        }
    };

    skipBtn.addEventListener('click', close);

    // Ease towards (never reaching) the end of the current slice.
    timers.push(window.setInterval(function () {
        creep += (0.9 - creep) * 0.03;
        renderBar();
    }, 150));
    timers.push(window.setInterval(nextPhrase, 1900));

    phraseIndex = -1;
    nextPhrase();
    renderBar();
}());
