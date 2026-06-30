/* =========================================================================
   Admin Login-As page logic
   ========================================================================= */
(function () {
    'use strict';

    const cfg = window.ARI_LOGIN_AS;
    const searchInput = document.getElementById('login-as-search');
    const searchStatus = document.getElementById('search-status');
    const resultsContainer = document.getElementById('login-as-results');
    const banner = document.getElementById('impersonation-banner');
    const bannerTarget = document.getElementById('impersonation-target');
    const btnClear = document.getElementById('btn-clear-impersonation');
    const toast = document.getElementById('toast');

    let allUsers = [];
    let realUser = null;

    /* -- Toast helper ---------------------------------------------------- */
    function showToast(msg, type) {
        toast.textContent = msg;
        toast.className = 'ari-toast ari-toast--' + type;
        toast.style.display = 'block';
        clearTimeout(toast._timer);
        toast._timer = setTimeout(function () {
            toast.style.display = 'none';
        }, 3000);
    }

    /* -- Banner ---------------------------------------------------------- */
    function updateBanner(username) {
        if (username) {
            bannerTarget.textContent = username;
            banner.style.display = 'flex';
        } else {
            banner.style.display = 'none';
        }
    }

    /* -- Load all users on init ------------------------------------------ */
    function loadAll() {
        searchStatus.textContent = 'Loading users...';
        fetch(cfg.searchUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    searchStatus.textContent = data.error || 'Error';
                    return;
                }
                updateBanner(data.current_login_as || null);
                allUsers = data.users;
                realUser = data.real_user;
                renderFiltered();
            })
            .catch(function () {
                searchStatus.textContent = 'Failed to load users.';
            });
    }

    /* -- Filter (local, instant) ----------------------------------------- */
    function renderFiltered() {
        var q = searchInput.value.trim().toLowerCase();
        var filtered = allUsers;
        if (q) {
            filtered = allUsers.filter(function (u) {
                return u.username.toLowerCase().indexOf(q) !== -1;
            });
        }
        if (filtered.length === 0) {
            resultsContainer.innerHTML = '';
            searchStatus.textContent = allUsers.length === 0
                ? 'No impersonatable users.' : 'No matching users.';
            return;
        }
        searchStatus.textContent = filtered.length + ' user(s).';
        renderResults(filtered, realUser);
    }

    function renderResults(users, realUser) {
        resultsContainer.innerHTML = '';
        users.forEach(function (u) {
            var card = document.createElement('div');
            card.className = 'ari-user-result-card ari-login-as-card';
            card.style.cursor = 'pointer';
            card.innerHTML =
                '<div class="ari-user-result-card__avatar">' +
                    '<i class="fa-solid fa-user"></i>' +
                '</div>' +
                '<div class="ari-user-result-card__info">' +
                    '<div class="ari-user-result-card__name">' +
                        escapeHtml(u.username) +
                    '</div>' +
                    '<div class="ari-user-result-card__groups">' +
                        escapeHtml(u.groups.join(', ')) +
                    '</div>' +
                '</div>' +
                '<div class="ari-login-as-card__hint">' +
                    '<i class="fa-solid fa-user-secret"></i>' +
                '</div>';

            card.addEventListener('click', function () {
                setLoginAs(u.username);
            });

            resultsContainer.appendChild(card);
        });
    }

    /* -- Set / Clear ----------------------------------------------------- */
    function setLoginAs(username) {
        fetch(cfg.setUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success) {
                showToast('Logged in as ' + username, 'success');
                setTimeout(function () {
                    window.location.href = cfg.homeUrl;
                }, 1200);
            } else {
                showToast(data.error || 'Failed', 'error');
            }
        })
        .catch(function () {
            showToast('Request failed', 'error');
        });
    }

    function clearLoginAs() {
        fetch(cfg.clearUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success) {
                updateBanner(null);
                showToast('Reverted to your account', 'success');
            } else {
                showToast(data.error || 'Failed', 'error');
            }
        })
        .catch(function () {
            showToast('Request failed', 'error');
        });
    }

    /* -- Escape helper --------------------------------------------------- */
    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    /* -- Events ---------------------------------------------------------- */
    searchInput.addEventListener('input', function () {
        renderFiltered();
    });

    btnClear.addEventListener('click', clearLoginAs);

    /* -- Init: load all users -------------------------------------------- */
    loadAll();
})();
