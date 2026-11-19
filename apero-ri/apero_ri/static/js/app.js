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

    function isVisible(element) {
        if (!element || element.hidden) {
            return false;
        }
        var style = window.getComputedStyle(element);
        return style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            element.getBoundingClientRect().width > 0;
    }

    function overlayCanClose(element) {
        var id = String(element.id || '').toLowerCase();
        var className = String(element.className || '').toLowerCase();
        if (/busy|saving|progress|loading|compile/.test(id + ' ' + className)) {
            return false;
        }
        if (element.getAttribute('aria-busy') === 'true') {
            return false;
        }
        return window.getComputedStyle(element).position === 'fixed';
    }

    function findExistingClose(overlay) {
        var selectors = [
            'button[id*="close" i]',
            'button[class*="close" i]',
            'button[data-close]'
        ];
        var candidates = overlay.querySelectorAll(selectors.join(','));
        for (var index = 0; index < candidates.length; index += 1) {
            if (isVisible(candidates[index])) {
                return candidates[index];
            }
        }
        return null;
    }

    function hasCrossClose(overlay) {
        var buttons = overlay.querySelectorAll(
            'button[id*="close" i],button[class*="close" i]'
        );
        for (var index = 0; index < buttons.length; index += 1) {
            var marker = (buttons[index].innerHTML + buttons[index].textContent)
                .toLowerCase();
            if (/xmark|fa-times|×|✕|close/.test(marker)) {
                return true;
            }
        }
        return false;
    }

    function hideOverlay(overlay) {
        overlay.style.display = 'none';
        overlay.hidden = true;
        overlay.classList.remove('open', 'show');
        overlay.dispatchEvent(new CustomEvent('ari:overlay-close'));
    }

    function enhanceOverlay(overlay) {
        if (!overlay || overlay.dataset.ariOverlayClose) {
            return;
        }
        var parentOverlay = overlay.parentElement &&
            overlay.parentElement.closest('[data-ari-overlay-close]');
        if (parentOverlay && overlay.getAttribute('role') === 'dialog') {
            return;
        }
        if (!overlayCanClose(overlay)) {
            return;
        }
        overlay.dataset.ariOverlayClose = 'ready';
        if (overlay.querySelector('.ari-overlay-auto-close') ||
                hasCrossClose(overlay)) {
            return;
        }
        var close = document.createElement('button');
        var closeLabel = window.ARI_CLOSE_OVERLAY_LABEL;
        close.type = 'button';
        close.className = 'ari-overlay-auto-close';
        close.setAttribute('aria-label', closeLabel);
        close.title = closeLabel;
        close.innerHTML = '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
        close.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            var existing = findExistingClose(overlay);
            if (existing && existing !== close) {
                existing.click();
            } else {
                hideOverlay(overlay);
            }
        });
        overlay.appendChild(close);
    }

    function enhanceOverlays(root) {
        var scope = root || document;
        var selector = [
            '[id*="overlay" i]',
            '[id*="modal" i]',
            '[class*="overlay" i]',
            '[class*="modal" i]',
            '[role="dialog"][aria-modal="true"]'
        ].join(',');
        scope.querySelectorAll(selector).forEach(enhanceOverlay);
        if (scope.matches && scope.matches(selector)) {
            enhanceOverlay(scope);
        }
    }

    enhanceOverlays();
    var overlayObserver = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    enhanceOverlays(node);
                }
            });
        });
    });
    overlayObserver.observe(document.body, {childList: true, subtree: true});

    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') {
            return;
        }
        var visible = Array.prototype.filter.call(
            document.querySelectorAll('[data-ari-overlay-close]'),
            isVisible
        );
        if (!visible.length) {
            return;
        }
        var overlay = visible[visible.length - 1];
        var close = findExistingClose(overlay) ||
            overlay.querySelector('.ari-overlay-auto-close');
        if (close) {
            event.preventDefault();
            close.click();
        }
    });
});
