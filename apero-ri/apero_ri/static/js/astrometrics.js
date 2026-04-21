/**
 * Astrometrics page — Find object, resolve target, finder chart
 */
(function () {
    'use strict';

    /* -----------------------------------------------------------------------
       DOM references
    ----------------------------------------------------------------------- */
    var searchInput = document.getElementById('astro-search-filter');
    var sections = document.querySelectorAll('.ari-astro-section');
    var pinButtons = document.querySelectorAll('.ari-astro-section__pin-btn');
    
    // Find object tab/panel elements
    var findTabs = document.querySelectorAll('.ot-find-tab');
    var findPanels = document.querySelectorAll('.ot-find-tab-panel');
    
    // Find by name
    var foNameQuery = document.getElementById('fo-name-query');
    var foFindName = document.getElementById('fo-find-name');
    var foClearName = document.getElementById('fo-clear-find-name');
    
    // Find by coordinates
    var foRa = document.getElementById('fo-ra');
    var foDec = document.getElementById('fo-dec');
    var foSep = document.getElementById('fo-sep');
    var foCoordFormat = document.getElementById('fo-coord-format');
    var foUnit = document.getElementById('fo-unit');
    var foFindCoords = document.getElementById('fo-find-coords');
    var foClearCoords = document.getElementById('fo-clear-find-coords');
    var foRaLabel = document.getElementById('fo-ra-label');
    var foDecLabel = document.getElementById('fo-dec-label');
    
    // Find by date
    var foFirstDate = document.getElementById('fo-first-date');
    var foLastDate = document.getElementById('fo-last-date');
    var foFindDate = document.getElementById('fo-find-date');
    var foClearDate = document.getElementById('fo-clear-find-date');
    
    // Advanced search
    var foAdvProperty = document.getElementById('fo-adv-property');
    var foAdvValue = document.getElementById('fo-adv-value');
    var foFindAdvanced = document.getElementById('fo-find-advanced');
    var foClearAdvanced = document.getElementById('fo-clear-find-adv');
    
    // Results display
    var foResults = document.getElementById('fo-results');
    var foResultsContent = document.getElementById('fo-results-content');
    var foLoading = document.getElementById('fo-loading');
    var foError = document.getElementById('fo-error');

    var pinnedSections = new Set();
    var currentSearchTab = 'name';
    var lastQuery = null;

    /* -----------------------------------------------------------------------
       Tab switching
    ----------------------------------------------------------------------- */
    findTabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            var tabId = this.id;
            var panelId = this.getAttribute('aria-controls');
            
            // Update active states
            findTabs.forEach(function (t) {
                t.classList.remove('ot-find-tab--active');
                t.setAttribute('aria-selected', 'false');
            });
            findPanels.forEach(function (p) {
                p.classList.remove('ot-find-tab-panel--active');
                p.hidden = true;
            });
            
            this.classList.add('ot-find-tab--active');
            this.setAttribute('aria-selected', 'true');
            var activePanel = document.getElementById(panelId);
            if (activePanel) {
                activePanel.classList.add('ot-find-tab-panel--active');
                activePanel.hidden = false;
            }
            
            // Track current tab
            if (tabId === 'fo-tab-name') currentSearchTab = 'name';
            else if (tabId === 'fo-tab-coords') currentSearchTab = 'coords';
            else if (tabId === 'fo-tab-date') currentSearchTab = 'date';
            else if (tabId === 'fo-tab-advanced') currentSearchTab = 'advanced';
        });
    });

    /* -----------------------------------------------------------------------
       Coordinate format switching
    ----------------------------------------------------------------------- */
    if (foCoordFormat) {
        foCoordFormat.addEventListener('change', function () {
            if (this.value === 'hms') {
                foRaLabel.textContent = 'RA [HH:MM:SS]';
                foDecLabel.textContent = 'Dec [DD:MM:SS]';
            } else {
                foRaLabel.textContent = 'RA [deg]';
                foDecLabel.textContent = 'Dec [deg]';
            }
        });
    }

    /* -----------------------------------------------------------------------
       Search functions
    ----------------------------------------------------------------------- */
    function showLoading() {
        foResults.style.display = 'none';
        foError.style.display = 'none';
        foLoading.style.display = 'block';
    }

    function showError(msg) {
        foLoading.style.display = 'none';
        foResults.style.display = 'none';
        foError.style.display = 'block';
        foError.textContent = msg;
    }

    function showResults(html) {
        foLoading.style.display = 'none';
        foError.style.display = 'none';
        foResultsContent.innerHTML = html;
        foResults.style.display = 'block';
    }

    function parseResponseJson(response) {
        return response.text().then(function (text) {
            var payload = null;
            try {
                payload = JSON.parse(text);
            } catch (e) {
                throw new Error(
                    'Server returned a non-JSON response ('
                    + response.status + ')'
                );
            }
            if (!response.ok) {
                var msg = (payload && payload.error)
                    ? payload.error
                    : 'Request failed';
                throw new Error(msg);
            }
            return payload;
        });
    }

    function clearResults() {
        foResults.style.display = 'none';
        foError.style.display = 'none';
        foLoading.style.display = 'none';
    }

    function formatObjectCard(obj, profile) {
        var hasRa = (obj.ra !== null && obj.ra !== undefined)
            && !isNaN(Number(obj.ra));
        var hasDec = (obj.dec !== null && obj.dec !== undefined)
            && !isNaN(Number(obj.dec));
                var coordsText = (hasRa && hasDec)
                        ? ' (' + Number(obj.ra).toFixed(4)
                            + ', ' + Number(obj.dec).toFixed(4) + ')'
                        : '';

        return '<div class="ari-astro-result-card" data-objname="'
               + escapeHtml(obj.name) + '" data-profile="'
               + escapeHtml(profile) + '">'
                             + '<div class="ari-astro-result__summary">'
                             + '<span class="ari-astro-result__name">'
                             + escapeHtml(obj.name) + '</span>'
                             + '<span class="ari-astro-result__coords">'
                             + escapeHtml(coordsText) + '</span>'
                             + '</div>'
               + '</div>';
    }

    function formatProfileCard(profileId, profileMeta, objectsHtml) {
        var meta = profileMeta || {};
        var instrument = meta.instrument || 'Profile';
        var version = meta.apero_version || '';
        var server = meta.reduction_server || '';

        var badges = '';
        if (version) {
            badges += '<span class="ari-astro-profile-card__meta-item">'
                + '<i class="fa-solid fa-code-branch"></i> '
                + 'v' + escapeHtml(version)
                + '</span>';
        }
        if (server) {
            badges += '<span class="ari-astro-profile-card__meta-item">'
                + '<i class="fa-solid fa-server"></i> '
                + escapeHtml(server)
                + '</span>';
        }

        return '<section class="ari-astro-profile-card">'
            + '<div class="ari-astro-profile-card__header">'
            + '<span class="ari-astro-profile-card__title">['
            + escapeHtml(instrument) + ': ' + escapeHtml(profileId)
            + ']</span>'
            + '<span class="ari-astro-profile-card__meta">'
            + badges
            + '</span>'
            + '</div>'
            + '<div class="ari-astro-profile-card__body">'
            + '<div class="ari-astro-result-cards">' + objectsHtml + '</div>'
            + '</div>'
            + '</section>';
    }

    function renderSearchResults(data, headingText) {
        var profiles = data.profiles || {};
        var html = '<div class="ari-astro-results__heading">'
            + headingText + '</div>';

        for (var profileId in data.results) {
            if (!data.results.hasOwnProperty(profileId)) continue;
            var objects = data.results[profileId] || [];
            var cardsHtml = '';
            objects.forEach(function (obj) {
                cardsHtml += formatObjectCard(obj, profileId);
            });
            html += formatProfileCard(
                profileId,
                profiles[profileId] || {},
                cardsHtml
            );
        }

        showResults(html);
        attachCardClickHandlers();
    }

    function findByName() {
        var query = (foNameQuery.value || '').trim();
        if (!query) {
            showError('Please enter an object name');
            return;
        }
        
        showLoading();
        lastQuery = { type: 'name', query: query };
        
                fetch('/api/astrometrics/find-object?search_type=name&query=' + 
              encodeURIComponent(query))
                        .then(parseResponseJson)
            .then(function (data) {
                if (!data.success) {
                    showError('Error: ' + (data.error || 'Search failed'));
                    return;
                }
                
                if (!data.results || Object.keys(data.results).length === 0) {
                    showError(
                        'Object ' + query + ' not found or user does not '
                        + 'have permission to view this object'
                    );
                    return;
                }
                
                renderSearchResults(
                    data,
                    'Found in ' + Object.keys(data.results).length
                    + ' profile(s)'
                );
            })
            .catch(function (err) {
                showError('Network error: ' + err.message);
            });
    }

    function findByCoordinates() {
        var ra = foRa.value.trim();
        var dec = foDec.value.trim();
        var sep = foSep.value.trim();
        
        if (!ra || !dec || !sep) {
            showError('Please enter RA, Dec, and separation');
            return;
        }
        
        showLoading();
        var params = new URLSearchParams({
            search_type: 'coords',
            ra: ra,
            dec: dec,
            separation: sep,
            coord_format: foCoordFormat.value,
            separation_unit: foUnit.value
        });
        
        lastQuery = { type: 'coords', ra: ra, dec: dec, sep: sep };
        
        fetch('/api/astrometrics/find-object?' + params.toString())
            .then(parseResponseJson)
            .then(function (data) {
                if (!data.success) {
                    showError('Error: ' + (data.error || 'Search failed'));
                    return;
                }
                
                if (!data.results || Object.keys(data.results).length === 0) {
                    showError('No objects found at this location');
                    return;
                }

                var totalObjects = 0;
                for (var profile in data.results) {
                    if (data.results.hasOwnProperty(profile)) {
                        totalObjects += data.results[profile].length;
                    }
                }

                renderSearchResults(
                    data,
                    'Found ' + totalObjects + ' object(s) in '
                    + Object.keys(data.results).length + ' profile(s)'
                );
            })
            .catch(function (err) {
                showError('Network error: ' + err.message);
            });
    }

    function findByDate() {
        var firstDate = foFirstDate.value;
        var lastDate = foLastDate.value;
        
        if (!firstDate && !lastDate) {
            showError('Please enter at least one date');
            return;
        }
        
        showLoading();
        var params = new URLSearchParams({
            search_type: 'date'
        });
        if (firstDate) params.append('first_observed', firstDate);
        if (lastDate) params.append('last_observed', lastDate);
        
        lastQuery = { type: 'date', firstDate: firstDate, lastDate: lastDate };
        
        fetch('/api/astrometrics/find-object?' + params.toString())
            .then(parseResponseJson)
            .then(function (data) {
                if (!data.success) {
                    showError('Error: ' + (data.error || 'Search failed'));
                    return;
                }
                
                if (!data.results || Object.keys(data.results).length === 0) {
                    showError('No objects found in date range');
                    return;
                }

                var totalObjects = 0;
                for (var profile in data.results) {
                    if (data.results.hasOwnProperty(profile)) {
                        totalObjects += data.results[profile].length;
                    }
                }

                renderSearchResults(
                    data,
                    'Found ' + totalObjects + ' object(s) in '
                    + Object.keys(data.results).length + ' profile(s)'
                );
            })
            .catch(function (err) {
                showError('Network error: ' + err.message);
            });
    }

    function findAdvanced() {
        var property = (foAdvProperty.value || '').trim();
        var value = (foAdvValue.value || '').trim();
        
        if (!property || !value) {
            showError('Please enter property and value');
            return;
        }
        
        showLoading();
        var params = new URLSearchParams({
            search_type: 'advanced',
            property: property,
            value: value
        });
        
        lastQuery = { type: 'advanced', property: property, value: value };
        
        fetch('/api/astrometrics/find-object?' + params.toString())
            .then(parseResponseJson)
            .then(function (data) {
                if (!data.success) {
                    showError('Error: ' + (data.error || 'Search failed'));
                    return;
                }
                
                if (!data.results || Object.keys(data.results).length === 0) {
                    showError('No objects matching criteria found');
                    return;
                }

                var totalObjects = 0;
                for (var profile in data.results) {
                    if (data.results.hasOwnProperty(profile)) {
                        totalObjects += data.results[profile].length;
                    }
                }

                renderSearchResults(
                    data,
                    'Found ' + totalObjects + ' object(s) in '
                    + Object.keys(data.results).length + ' profile(s)'
                );
            })
            .catch(function (err) {
                showError('Network error: ' + err.message);
            });
    }

    /* -----------------------------------------------------------------------
       Card click handlers — navigate to object page
    ----------------------------------------------------------------------- */
    function attachCardClickHandlers() {
        var cards = document.querySelectorAll('.ari-astro-result-card');
        cards.forEach(function (card) {
            card.addEventListener('click', function () {
                var objname = this.getAttribute('data-objname');
                var profileId = this.getAttribute('data-profile');
                if (objname && profileId) {
                    window.location.href = '/data_portal/' + 
                        encodeURIComponent(profileId) + '/' + 
                        encodeURIComponent(objname);
                }
            });
            card.style.cursor = 'pointer';
        });
    }

    /* -----------------------------------------------------------------------
       Event listeners
    ----------------------------------------------------------------------- */
    if (foFindName) {
        foFindName.addEventListener('click', findByName);
        foNameQuery.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') findByName();
        });
    }
    
    if (foClearName) {
        foClearName.addEventListener('click', function () {
            if (foNameQuery) foNameQuery.value = '';
            clearResults();
        });
    }
    
    if (foFindCoords) {
        foFindCoords.addEventListener('click', findByCoordinates);
    }
    
    if (foClearCoords) {
        foClearCoords.addEventListener('click', function () {
            if (foRa) foRa.value = '';
            if (foDec) foDec.value = '';
            if (foSep) foSep.value = '';
            clearResults();
        });
    }
    
    if (foFindDate) {
        foFindDate.addEventListener('click', findByDate);
    }
    
    if (foClearDate) {
        foClearDate.addEventListener('click', function () {
            if (foFirstDate) foFirstDate.value = '';
            if (foLastDate) foLastDate.value = '';
            clearResults();
        });
    }
    
    if (foFindAdvanced) {
        foFindAdvanced.addEventListener('click', findAdvanced);
    }
    
    if (foClearAdvanced) {
        foClearAdvanced.addEventListener('click', function () {
            if (foAdvProperty) foAdvProperty.value = '';
            if (foAdvValue) foAdvValue.value = '';
            clearResults();
        });
    }

    /* -----------------------------------------------------------------------
       Section minimize/expand and pin functionality
    ----------------------------------------------------------------------- */
    pinButtons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            var sectionId = this.getAttribute('data-section-id');
            if (pinnedSections.has(sectionId)) {
                pinnedSections.delete(sectionId);
                this.classList.remove('ari-astro-section__pin-btn--pinned');
            } else {
                pinnedSections.add(sectionId);
                this.classList.add('ari-astro-section__pin-btn--pinned');
            }
            // Could save to API or localStorage here
        });
    });

    /* -----------------------------------------------------------------------
       Search/filter sections
    ----------------------------------------------------------------------- */
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            var filterText = this.value.toLowerCase();
            sections.forEach(function (section) {
                var title = section.querySelector('.ari-astro-section__title');
                var matches = !filterText || 
                    (title && title.textContent.toLowerCase().includes(filterText));
                section.style.display = matches ? '' : 'none';
            });
        });
    }

    /* -----------------------------------------------------------------------
       Helper: escape HTML
    ----------------------------------------------------------------------- */
    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
})();
