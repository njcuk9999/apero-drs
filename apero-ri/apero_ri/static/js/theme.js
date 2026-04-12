/*
 * theme.js — ARI theme switching
 * Applies immediately from localStorage, then syncs with server prefs.
 */
(function () {
    'use strict';

    var VALID_THEMES = ['default', 'light', 'dark'];
    var STORAGE_KEY = 'ari-theme';
    var SAVE_URL = '/api/user/prefs/save';

    function applyTheme(theme) {
        if (VALID_THEMES.indexOf(theme) === -1) theme = 'default';
        document.documentElement.setAttribute('data-theme', theme);
        try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
    }

    function saveTheme(theme) {
        if (VALID_THEMES.indexOf(theme) === -1) theme = 'default';
        applyTheme(theme);
        fetch(SAVE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme: theme })
        }).catch(function () {});
    }

    /* Expose globally for themes page button clicks */
    window.ariSetTheme = saveTheme;

    /* On page load — reconcile localStorage with server-rendered attr */
    (function () {
        var serverTheme = document.documentElement.getAttribute(
            'data-theme'
        ) || 'default';
        var storedTheme = '';
        try { storedTheme = localStorage.getItem(STORAGE_KEY) || ''; }
        catch (e) {}
        /*
         * If server sent a valid theme, trust it and update localStorage.
         * This keeps them in sync after a server-side change.
         */
        if (VALID_THEMES.indexOf(serverTheme) > -1) {
            try {
                localStorage.setItem(STORAGE_KEY, serverTheme);
            } catch (e) {}
        }
    }());
}());
