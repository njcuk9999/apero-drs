/* Pinned pages management page */
(function () {
    function pinIconSvg(withSlash) {
        var slash = withSlash
            ? '<line x1="3" y1="13" x2="13" y2="3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></line>'
            : '';
        return '' +
            '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">' +
            '<circle cx="8" cy="3.2" r="2.2" fill="currentColor"></circle>' +
            '<path d="M5.6 6.2h4.8l-1.4 3.2h-2z" fill="currentColor"></path>' +
            '<rect x="7.3" y="9" width="1.4" height="5.2" rx="0.7" fill="currentColor"></rect>' +
            slash +
            '</svg>';
    }

    async function fetchPins() {
        var response = await fetch('/api/user/pins/list');
        var payload = await response.json();
        if (!payload.success) {
            throw new Error(payload.error || 'Failed to load pinned pages');
        }
        return payload.pins || [];
    }

    async function removePin(pageId) {
        var response = await fetch('/api/user/pins/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ page_id: pageId })
        });
        var payload = await response.json();
        if (!payload.success) {
            throw new Error(payload.error || 'Failed to remove pinned page');
        }
        return payload.pins || [];
    }

    function renderEmpty(container) {
        container.innerHTML =
            '<p class="ari-page-subtitle">No pinned pages yet. Use the Pin button next to page titles.</p>';
    }

    function renderPins(container, pins) {
        container.innerHTML = '';
        if (!pins.length) {
            renderEmpty(container);
            return;
        }

        pins.forEach(function (pin) {
            var pageId = String(pin.page_id || '');
            var label = String(pin.label || pin.page_id || 'Pinned Page');
            var url = String(pin.url || '/');
            var iconClass = String(pin.icon || 'fa-solid fa-bookmark');

            var row = document.createElement('div');
            row.className = 'ari-pinned-row';
            row.setAttribute('data-page-id', pageId);

            var link = document.createElement('a');
            link.className = 'ari-pinned-row__link';
            link.href = url;

            var icon = document.createElement('i');
            icon.className = iconClass;
            icon.setAttribute('aria-hidden', 'true');
            link.appendChild(icon);

            var text = document.createElement('span');
            text.className = 'ari-pinned-row__label';
            text.textContent = label;
            link.appendChild(text);

            var button = document.createElement('button');
            button.type = 'button';
            button.className = 'ari-pinned-row__unpin js-unpin';
            button.setAttribute('data-page-id', pageId);
            button.setAttribute('title', 'Unpin');
            button.setAttribute('aria-label', 'Unpin ' + label);

            var buttonIcon = document.createElement('span');
            buttonIcon.className = 'ari-pin-icon';
            buttonIcon.setAttribute('aria-hidden', 'true');
            buttonIcon.innerHTML = pinIconSvg(true);
            button.appendChild(buttonIcon);

            row.appendChild(link);
            row.appendChild(button);
            container.appendChild(row);
        });
    }

    document.addEventListener('DOMContentLoaded', async function () {
        var container = document.getElementById('pinned-pages-list');
        if (!container) {
            return;
        }

        try {
            var pins = await fetchPins();
            renderPins(container, pins);
        } catch (err) {
            container.innerHTML =
                '<p class="ari-flash ari-flash--danger">' +
                (err.message || 'Could not load pinned pages.') +
                '</p>';
            return;
        }

        container.addEventListener('click', async function (event) {
            var button = event.target.closest('.js-unpin');
            if (!button) {
                return;
            }

            var pageId = button.getAttribute('data-page-id') || '';
            if (!pageId) {
                return;
            }

            button.disabled = true;
            try {
                var pins = await removePin(pageId);
                renderPins(container, pins);
            } catch (err) {
                window.alert(err.message || 'Could not remove pin.');
                button.disabled = false;
            }
        });
    });
})();
