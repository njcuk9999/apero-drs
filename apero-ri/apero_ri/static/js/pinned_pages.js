/* Pinned pages management page */
(function () {
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

    async function reorderPins(ids) {
        var response = await fetch('/api/user/pins/reorder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: ids })
        });
        var payload = await response.json();
        if (!payload.success) {
            throw new Error(payload.error || 'Failed to reorder pinned pages');
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

            var dragHandle = document.createElement('button');
            dragHandle.type = 'button';
            dragHandle.className = 'ari-pinned-row__drag js-pin-drag';
            dragHandle.setAttribute('title', 'Drag to reorder');
            dragHandle.setAttribute('aria-label', 'Drag to reorder ' + label);
            dragHandle.setAttribute('draggable', 'true');

            var dragIcon = document.createElement('i');
            dragIcon.className = 'fa-solid fa-grip-vertical';
            dragIcon.setAttribute('aria-hidden', 'true');
            dragHandle.appendChild(dragIcon);

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
            button.setAttribute('title', 'Remove pin');
            button.setAttribute('aria-label', 'Remove pin for ' + label);

            var buttonIcon = document.createElement('i');
            buttonIcon.className = 'fa-solid fa-xmark';
            buttonIcon.setAttribute('aria-hidden', 'true');
            button.appendChild(buttonIcon);

            row.appendChild(dragHandle);
            row.appendChild(link);
            row.appendChild(button);
            container.appendChild(row);
        });
    }

    function getRenderedOrder(container) {
        return Array.prototype.map.call(
            container.querySelectorAll('.ari-pinned-row[data-page-id]'),
            function (row) {
                return row.getAttribute('data-page-id') || '';
            }
        ).filter(function (value) { return !!value; });
    }

    function getDragAfterRow(container, y) {
        var rows = container.querySelectorAll('.ari-pinned-row:not(.is-dragging)');
        var best = { offset: Number.NEGATIVE_INFINITY, element: null };
        Array.prototype.forEach.call(rows, function (row) {
            var rect = row.getBoundingClientRect();
            var offset = y - rect.top - rect.height / 2;
            if (offset < 0 && offset > best.offset) {
                best = { offset: offset, element: row };
            }
        });
        return best.element;
    }

    document.addEventListener('DOMContentLoaded', async function () {
        var container = document.getElementById('pinned-pages-list');
        if (!container) {
            return;
        }

        var dragState = {
            active: false,
            startOrderKey: ''
        };

        var savingOrder = false;

        async function persistOrderIfChanged() {
            var currentOrder = getRenderedOrder(container);
            var key = currentOrder.join('|');
            if (!currentOrder.length || key === dragState.startOrderKey) {
                return;
            }
            if (savingOrder) {
                return;
            }

            savingOrder = true;
            container.classList.add('is-saving');
            try {
                var pins = await reorderPins(currentOrder);
                renderPins(container, pins);
            } catch (err) {
                window.alert(err.message || 'Could not save pin order.');
            } finally {
                savingOrder = false;
                container.classList.remove('is-saving');
            }
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

        container.addEventListener('dragstart', function (event) {
            var handle = event.target.closest('.js-pin-drag');
            if (!handle) {
                return;
            }
            var row = handle.closest('.ari-pinned-row');
            if (!row) {
                return;
            }

            dragState.active = true;
            dragState.startOrderKey = getRenderedOrder(container).join('|');
            row.classList.add('is-dragging');

            if (event.dataTransfer) {
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', row.getAttribute('data-page-id') || '');
            }
        });

        container.addEventListener('dragover', function (event) {
            if (!dragState.active) {
                return;
            }
            event.preventDefault();

            var dragging = container.querySelector('.ari-pinned-row.is-dragging');
            if (!dragging) {
                return;
            }

            var afterRow = getDragAfterRow(container, event.clientY);
            if (!afterRow) {
                container.appendChild(dragging);
                return;
            }
            if (afterRow !== dragging) {
                container.insertBefore(dragging, afterRow);
            }
        });

        container.addEventListener('drop', function (event) {
            if (dragState.active) {
                event.preventDefault();
            }
        });

        container.addEventListener('dragend', function (event) {
            var row = event.target.closest('.ari-pinned-row');
            if (row) {
                row.classList.remove('is-dragging');
            }
            if (!dragState.active) {
                return;
            }
            dragState.active = false;
            persistOrderIfChanged();
        });

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
