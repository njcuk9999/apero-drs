/* Simple tab switcher for User Portal instrument tabs */
(function () {
    function setupTabSet(tabList) {
        var tabs = Array.prototype.slice.call(
            tabList.querySelectorAll('.ari-up-tab, .ari-sg-tab[data-tab-target]')
        );
        if (!tabs.length) {
            return;
        }

        function activate(tab) {
            var targetId = tab.getAttribute('data-tab-target');
            if (!targetId) {
                return;
            }

            tabs.forEach(function (candidate) {
                var candidateTarget = candidate.getAttribute('data-tab-target');
                var panel = candidateTarget ? document.getElementById(candidateTarget) : null;
                var isActive = candidate === tab;
                candidate.classList.toggle('ari-sg-tab--active', isActive);
                candidate.setAttribute('aria-selected', isActive ? 'true' : 'false');
                if (panel) {
                    panel.classList.toggle('ari-up-panel--hidden', !isActive);
                    panel.style.display = isActive ? '' : 'none';
                    panel.hidden = !isActive;
                }
            });
        }

        tabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                activate(tab);
            });
        });

        var preActive = tabs.find(function (tab) {
            return tab.classList.contains('ari-sg-tab--active');
        });
        activate(preActive || tabs[0]);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var tabLists = document.querySelectorAll('.ari-sg-tabs[role="tablist"]');
        tabLists.forEach(setupTabSet);
    });
})();
