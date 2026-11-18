/* Persist and apply reusable cards/list collection preferences. */
(function () {
    'use strict';

    function saveSettings(control) {
        var status = control.querySelector('.ari-view-controls__status');
        var data = {
            page_view: {
                page_id: control.dataset.pageId,
                view: control.dataset.view,
                sort: control.dataset.sort
            }
        };
        if (status) status.textContent = control.dataset.saving;
        fetch(control.dataset.saveUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        }).then(function (response) {
            if (!response.ok) throw new Error('Could not save view preference');
            if (status) status.textContent = control.dataset.saved;
        }).catch(function () {
            if (status) status.textContent = control.dataset.saveFailed;
        });
    }

    function apply(control, collection) {
        collection.classList.toggle(
            'ari-view-collection--cards',
            control.dataset.view === 'cards'
        );
        collection.classList.toggle(
            'ari-view-collection--list',
            control.dataset.view === 'list'
        );
        control.querySelectorAll('[data-ari-view]').forEach(function (button) {
            var active = button.dataset.ariView === control.dataset.view;
            button.classList.toggle('ari-btn--primary', active);
            button.classList.toggle('ari-btn--secondary', !active);
            button.setAttribute('aria-pressed', active ? 'true' : 'false');
        });

        var direction = control.dataset.sort === 'desc' ? -1 : 1;
        var items = Array.from(collection.children);
        items.sort(function (left, right) {
            var leftLabel = left.dataset.sortLabel || left.textContent;
            var rightLabel = right.dataset.sortLabel || right.textContent;
            return leftLabel.trim().localeCompare(
                rightLabel.trim(), undefined, {sensitivity: 'base'}
            ) * direction;
        });
        items.forEach(function (item) { collection.appendChild(item); });
    }

    document.querySelectorAll('[data-ari-view-controls]').forEach(
        function (control) {
            var section = control.closest('[data-ari-view-section]');
            var collection = section
                ? section.querySelector('[data-ari-view-collection]')
                : null;
            if (!collection) return;

            control.querySelectorAll('[data-ari-view]').forEach(
                function (button) {
                    button.addEventListener('click', function () {
                        control.dataset.view = button.dataset.ariView;
                        apply(control, collection);
                        saveSettings(control);
                    });
                }
            );
            var sort = control.querySelector('[data-ari-sort]');
            if (sort) {
                sort.addEventListener('change', function () {
                    control.dataset.sort = sort.value;
                    apply(control, collection);
                    saveSettings(control);
                });
            }
            apply(control, collection);
        }
    );
}());
