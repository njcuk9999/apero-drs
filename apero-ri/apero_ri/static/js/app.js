/* APERO RI – Minimal JavaScript */
var ARI = ARI || {};

/**
 * Switch documentation version – updates ?v= param and reloads.
 */
ARI.switchVersion = function (versionId) {
    var url = new URL(window.location.href);
    url.searchParams.set('v', versionId);
    window.location.href = url.toString();
};

document.addEventListener('DOMContentLoaded', function () {

    var hamburger = document.getElementById('ari-hamburger');
    var mobileMenu = document.getElementById('ari-mobile-menu');
    var backdrop = document.getElementById('ari-backdrop');

    function toggleMenu() {
        var isOpen = mobileMenu.classList.toggle('open');
        backdrop.classList.toggle('open', isOpen);
    }

    function closeMenu() {
        mobileMenu.classList.remove('open');
        backdrop.classList.remove('open');
    }

    if (hamburger) {
        hamburger.addEventListener('click', toggleMenu);
    }
    if (backdrop) {
        backdrop.addEventListener('click', closeMenu);
    }

    // Auto-dismiss flash messages after 5 seconds
    var flashes = document.querySelectorAll('.ari-flash');
    flashes.forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity 0.3s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 300);
        }, 5000);
    });
});
