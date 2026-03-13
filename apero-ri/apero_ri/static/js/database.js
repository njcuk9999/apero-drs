/**
 * ARI Reduction Interface — instrument filter for profile cards.
 */
(function () {
    'use strict';

    if (!window.ARI) window.ARI = {};

    ARI.Database = {
        /**
         * Show only cards matching the selected instrument.
         * @param {string} instrument - Instrument name or 'all'.
         */
        filter: function (instrument) {
            var cards = document.querySelectorAll('.ari-db-card');
            var buttons = document.querySelectorAll('.ari-db-filter__btn');

            buttons.forEach(function (btn) {
                if (btn.dataset.instrument === instrument) {
                    btn.classList.add('ari-db-filter__btn--active');
                } else {
                    btn.classList.remove('ari-db-filter__btn--active');
                }
            });

            cards.forEach(function (card) {
                if (instrument === 'all' ||
                    card.dataset.instrument === instrument) {
                    card.classList.remove('ari-db-card--hidden');
                } else {
                    card.classList.add('ari-db-card--hidden');
                }
            });
        },
    };
})();
