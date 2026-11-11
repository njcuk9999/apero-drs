(function () {
    'use strict';
    var config = window.DM_USER_INFO;
    var card = document.getElementById('dm-user-info');
    if (!config || !card) return;
    var active = null;
    var directory = null;
    var closeTimer;

    function loadDirectory() {
        if (!directory) {
            directory = fetch(config.directoryUrl, {
                credentials: 'same-origin', cache: 'no-store'
            }).then(function (response) {
                if (!response.ok) throw new Error();
                return response.json();
            }).then(function (payload) {
                if (!payload.success || !Array.isArray(payload.users)) {
                    throw new Error();
                }
                return new Map(payload.users.map(function (user) {
                    return [user.username, user];
                }));
            }).catch(function (error) {
                directory = null;
                throw error;
            });
        }
        return directory;
    }

    function position() {
        if (!active || card.hidden) return;
        var rect = active.getBoundingClientRect();
        var left = Math.max(12, Math.min(rect.left,
            window.innerWidth - card.offsetWidth - 12));
        var top = rect.bottom + 6;
        if (top + card.offsetHeight > window.innerHeight - 12) {
            top = Math.max(12, rect.top - card.offsetHeight - 6);
        }
        top = Math.max(12, Math.min(top,
            window.innerHeight - card.offsetHeight - 12));
        card.style.left = left + 'px';
        card.style.top = top + 'px';
    }

    function hide() {
        clearTimeout(closeTimer);
        if (active) active.removeAttribute('aria-describedby');
        active = null;
        card.hidden = true;
    }

    function scheduleHide() {
        clearTimeout(closeTimer);
        closeTimer = setTimeout(function () {
            if (active && (active.matches(':hover') ||
                active === document.activeElement || card.matches(':hover'))) {
                return;
            }
            hide();
        }, 150);
    }

    function show(link) {
        clearTimeout(closeTimer);
        if (active === link) return;
        hide();
        active = link;
        link.setAttribute('aria-describedby', card.id);
        card.textContent = config.loading;
        card.hidden = false;
        position();
        loadDirectory().then(function (users) {
            if (active !== link) return;
            var user = users.get(link.dataset.dmUser);
            var lines = [];
            if (user) {
                lines.push(user.full_name || user.username);
                if (user.primary_institution) lines.push(user.primary_institution);
                if (Array.isArray(user.groups) && user.groups.length) {
                    lines.push(user.groups.join(', '));
                }
                if (user.can_view_contact === true && user.email) {
                    lines.push(user.email);
                }
            }
            card.textContent = user ? lines.join('\n') : config.unknown;
            position();
        }).catch(function () {
            if (active !== link) return;
            card.textContent = config.unavailable;
            position();
        });
    }

    document.querySelectorAll('.dm-user-link').forEach(function (link) {
        link.addEventListener('mouseenter', function () { show(link); });
        link.addEventListener('focus', function () { show(link); });
        link.addEventListener('mouseleave', scheduleHide);
        link.addEventListener('blur', scheduleHide);
    });
    card.addEventListener('mouseenter', function () { clearTimeout(closeTimer); });
    card.addEventListener('mouseleave', scheduleHide);
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') hide();
    });
    document.addEventListener('click', function (event) {
        if (active && !active.contains(event.target) &&
            !card.contains(event.target)) hide();
    });
    window.addEventListener('resize', position);
    document.addEventListener('scroll', position, true);
}());