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

/* ============================================================== */
/* Vertical tabs + Resolve-target tab wiring                       */
/* ============================================================== */
(function () {
    'use strict';

    /* Vertical tab strip */
    var vtabs = document.querySelectorAll('.ari-htab');
    var vpanels = document.querySelectorAll('.ari-htab-panel');
    vtabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            var key = this.getAttribute('data-htab');
            vtabs.forEach(function (t) {
                t.classList.toggle(
                    'ari-htab--active',
                    t.getAttribute('data-htab') === key);
                t.setAttribute(
                    'aria-selected',
                    t.getAttribute('data-htab') === key
                        ? 'true' : 'false');
            });
            vpanels.forEach(function (p) {
                if (p.id === 'astro-tab-' + key) {
                    p.removeAttribute('hidden');
                    p.classList.add('ari-htab-panel--active');
                } else {
                    p.setAttribute('hidden', '');
                    p.classList.remove('ari-htab-panel--active');
                }
            });
        });
    });

    /* Resolve-target sub-tabs */
    var rtTabs = document.querySelectorAll(
        '#astro-tab-resolve-target .ot-find-tab');
    rtTabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            var ctrlId = this.getAttribute('aria-controls');
            rtTabs.forEach(function (t) {
                t.classList.toggle(
                    'ot-find-tab--active',
                    t === this);
                t.setAttribute(
                    'aria-selected',
                    t === this ? 'true' : 'false');
            }, this);
            document.querySelectorAll(
                '#astro-tab-resolve-target .ot-find-tab-panel'
            ).forEach(function (p) {
                if (p.id === ctrlId) {
                    p.classList.add('ot-find-tab-panel--active');
                    p.removeAttribute('hidden');
                } else {
                    p.classList.remove('ot-find-tab-panel--active');
                    p.setAttribute('hidden', '');
                }
            });
        });
    });

    /* DOM refs (resolve-target) */
    var rtLoading = document.getElementById('rt-loading');
    var rtError = document.getElementById('rt-error');
    var rtPicker = document.getElementById('rt-picker');
    var rtPickerList = document.getElementById('rt-picker-list');
    var rtTargetInfo = document.getElementById('rt-target-info');
    var rtTargetName = document.getElementById('rt-target-name');
    var rtSections = document.getElementById(
        'rt-target-info-sections');
    var rtVerifyBanner = document.getElementById('rt-verify-banner');
    var rtVerifyBtn = document.getElementById('rt-target-verify');
    var rtUploadBtn = document.getElementById('rt-target-upload');

    function _showLoading(on) {
        if (!rtLoading) return;
        rtLoading.style.display = on ? 'block' : 'none';
    }
    function _showError(msg) {
        if (!rtError) return;
        if (msg) {
            rtError.textContent = msg;
            rtError.style.display = 'block';
        } else {
            rtError.textContent = '';
            rtError.style.display = 'none';
        }
    }
    function _resetUi() {
        _showError(null);
        if (rtPicker) rtPicker.style.display = 'none';
        if (rtPickerList) rtPickerList.innerHTML = '';
        if (rtTargetInfo) rtTargetInfo.style.display = 'none';
        if (rtSections) rtSections.innerHTML = '';
        if (rtVerifyBanner) rtVerifyBanner.style.display = 'none';
        if (rtVerifyBtn) {
            rtVerifyBtn.hidden = true;
            rtVerifyBtn.disabled = false;
        }
        if (rtUploadBtn) {
            rtUploadBtn.hidden = true;
            rtUploadBtn.disabled = false;
        }
    }

    function _hasAnyMonitorPerm(perms) {
        if (!Array.isArray(perms)) return false;
        if (perms.indexOf('manage.astrometrics') !== -1) return true;
        var prefixes = [
            'monitor.', 'view.monitor_portal.', 'view.monitor.'
        ];
        for (var i = 0; i < perms.length; i++) {
            var p = String(perms[i] || '').toLowerCase();
            if (p === 'monitor') return true;
            for (var k = 0; k < prefixes.length; k++) {
                if (p.indexOf(prefixes[k]) === 0) return true;
            }
        }
        return false;
    }

    function _wireUploadButton(aperoName, entry) {
        if (!rtUploadBtn) return;
        var fresh = rtUploadBtn.cloneNode(true);
        rtUploadBtn.parentNode.replaceChild(fresh, rtUploadBtn);
        rtUploadBtn = fresh;
        rtUploadBtn.addEventListener('click', function () {
            if (!window.confirm(
                    'Upload this SIMBAD-resolved entry for "'
                    + aperoName + '" to the APERO astrometric '
                    + 'database as a pending entry?')) {
                return;
            }
            rtUploadBtn.disabled = true;
            var orig = rtUploadBtn.innerHTML;
            rtUploadBtn.innerHTML = '<i class="fa-solid fa-spinner'
                + ' fa-spin"></i> Uploading...';
            fetch('/api/astrometrics/upload-yaml', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ entry: entry })
            }).then(function (r) {
                return r.json().then(function (j) {
                    return { ok: r.ok, json: j };
                });
            }).then(function (res) {
                if (!res.ok || !res.json || !res.json.success) {
                    var err = (res.json && res.json.error)
                        || 'Upload failed';
                    window.alert('Upload failed: ' + err);
                    rtUploadBtn.disabled = false;
                    rtUploadBtn.innerHTML = orig;
                    return;
                }
                rtUploadBtn.hidden = true;
                window.alert('Uploaded as pending entry "'
                    + (res.json.apero_name || aperoName) + '".');
            }).catch(function (err) {
                window.alert('Upload failed: ' + err);
                rtUploadBtn.disabled = false;
                rtUploadBtn.innerHTML = orig;
            });
        });
    }

    function _wireVerifyButton(aperoName) {
        if (!rtVerifyBtn) return;
        // replace handler each time so we always target the
        // currently-displayed entry
        var fresh = rtVerifyBtn.cloneNode(true);
        rtVerifyBtn.parentNode.replaceChild(fresh, rtVerifyBtn);
        rtVerifyBtn = fresh;
        rtVerifyBtn.addEventListener('click', function () {
            var msg = ('You must have checked all the parameters '
                + 'and see that they look suitable.\n\nMark '
                + aperoName + ' as VERIFIED?');
            if (!window.confirm(msg)) return;
            rtVerifyBtn.disabled = true;
            var orig = rtVerifyBtn.innerHTML;
            rtVerifyBtn.innerHTML = '<i class="fa-solid fa-spinner '
                + 'fa-spin"></i> Verifying...';
            fetch('/api/astrometrics/verify', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    apero_name: aperoName,
                    instrument: ''
                })
            }).then(function (r) {
                return r.json().then(function (j) {
                    return { ok: r.ok, json: j };
                });
            }).then(function (res) {
                if (!res.ok || !res.json || !res.json.success) {
                    var err = (res.json && res.json.error)
                        || 'Verify failed';
                    window.alert('Verify failed: ' + err);
                    rtVerifyBtn.disabled = false;
                    rtVerifyBtn.innerHTML = orig;
                    return;
                }
                if (rtVerifyBanner) {
                    rtVerifyBanner.style.display = 'none';
                }
                rtVerifyBtn.hidden = true;
            }).catch(function (err) {
                window.alert('Verify failed: ' + err);
                rtVerifyBtn.disabled = false;
                rtVerifyBtn.innerHTML = orig;
            });
        });
    }

    function _refreshVerifyBanner(aperoName) {
        if (!aperoName) return;
        if (rtVerifyBanner) rtVerifyBanner.style.display = 'none';
        if (rtVerifyBtn) rtVerifyBtn.hidden = true;
        var url = '/api/astrometrics/status?name='
            + encodeURIComponent(aperoName);
        fetch(url, { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .catch(function () { return null; })
            .then(function (data) {
                if (!data || !data.success) return;
                var status = String(data.status || '').toLowerCase();
                if (status !== 'pending') return;
                if (rtVerifyBanner) {
                    rtVerifyBanner.style.display = '';
                }
                var perms = (window.AperoRI
                    && window.AperoRI.userPerms) || [];
                if (_hasAnyMonitorPerm(perms) && rtVerifyBtn) {
                    rtVerifyBtn.hidden = false;
                    _wireVerifyButton(
                        data.apero_name || aperoName);
                }
            });
    }

    /* "Resolve online" buttons stay hidden until a local Resolve
       attempt has confirmed the target is not in the on-disk APERO
       astrometric database -- that way the user is nudged to use
       the curated database first. ``failedFor`` tracks the last
       name the user tried locally so we only re-hide the buttons
       when they switch to a fresh query. */
    var failedFor = null;
    function _onlineButtons() {
        return [
            document.getElementById('rt-resolve-online-name'),
            document.getElementById('rt-resolve-online-coords')
        ].filter(function (el) { return !!el; });
    }
    function _hideOnlineButtons() {
        _onlineButtons().forEach(function (b) {
            b.hidden = true;
            b.style.display = 'none';
        });
        failedFor = null;
    }
    function _showOnlineButtons(name) {
        failedFor = (name || '').trim() || null;
        _onlineButtons().forEach(function (b) {
            b.hidden = false;
            b.style.display = '';
        });
    }
    _hideOnlineButtons();
    var nameQueryEl = document.getElementById('rt-name-query');
    if (nameQueryEl) {
        nameQueryEl.addEventListener('input', function () {
            // re-hide as soon as the user types something different
            // from the value that triggered the previous failure
            if (failedFor != null
                    && this.value.trim() !== failedFor) {
                _hideOnlineButtons();
            }
        });
    }
    function _showTarget(apero_name, payload, opts) {
        if (rtTargetName) {
            rtTargetName.textContent = apero_name || 'Unknown';
        }
        if (rtTargetInfo) rtTargetInfo.style.display = 'block';
        if (rtSections && window.AperoTargetInfo) {
            window.AperoTargetInfo.render(rtSections, payload, {
                apero_name: apero_name,
                userPerms: (window.AperoRI
                    && window.AperoRI.userPerms) || []
            });
        }
        // Show the upload button only for transient (online-resolved)
        // entries — and only for monitors.
        var entry = opts && opts.entry;
        if (entry && rtUploadBtn) {
            var perms = (window.AperoRI
                && window.AperoRI.userPerms) || [];
            if (_hasAnyMonitorPerm(perms)) {
                rtUploadBtn.hidden = false;
                _wireUploadButton(apero_name, entry);
            }
        }
        _refreshVerifyBanner(apero_name);
    }

    function _showRejectionBanner(data) {
        // If the resolve-by-name response indicates the entry is
        // currently on the rejection list, prepend a red banner to
        // the resolved target panel so the monitor knows this name
        // will be ignored by the data portal and observations will
        // fall back to FITS header values.
        if (!rtSections) return;
        if (!data || (data.status || '').toLowerCase() !== 'rejected'
        ) {
            return;
        }
        var notes = '';
        var aliases = [];
        if (data.raw && typeof data.raw === 'object') {
            notes = data.raw.NOTES || '';
            aliases = data.raw.ALIASES || [];
            if (typeof aliases === 'string') aliases = [aliases];
        }
        var banner = document.createElement('div');
        banner.className = 'ari-banner ari-banner--danger';
        var html = '<i class="fa-solid fa-ban"></i> '
            + '<strong>This name is on the rejection list.</strong> '
            + 'Observations using this object name (or any alias) '
            + 'are excluded from the data portal and will fall back '
            + 'to FITS header values.';
        if (notes) {
            html += '<div class="ari-banner__detail">'
                + '<strong>Notes:</strong> '
                + String(notes).replace(/[<>&]/g, function (c) {
                    return ({'<': '&lt;', '>': '&gt;',
                             '&': '&amp;'})[c];
                }) + '</div>';
        }
        if (aliases && aliases.length) {
            html += '<div class="ari-banner__detail">'
                + '<strong>Also rejected:</strong> '
                + aliases.map(function (a) {
                    return String(a).replace(/[<>&]/g, function (c) {
                        return ({'<': '&lt;', '>': '&gt;',
                                 '&': '&amp;'})[c];
                    });
                }).join(', ') + '</div>';
        }
        banner.innerHTML = html;
        rtSections.insertBefore(banner, rtSections.firstChild);
    }

    function _showPicker(matches) {
        if (!rtPicker || !rtPickerList) return;
        rtPickerList.innerHTML = '';
        matches.forEach(function (m) {
            var li = document.createElement('li');
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ari-astro-picker__item';
            var label = m.apero_name || '(unnamed)';
            var sep = '';
            if (typeof m.separation_arcsec === 'number') {
                sep = ' <span class="ari-tinfo-source">'
                    + m.separation_arcsec.toFixed(2)
                    + ' arcsec</span>';
            }
            btn.innerHTML = '<span><i class="fa-solid fa-star"></i>'
                + ' ' + label + '</span>' + sep;
            btn.addEventListener('click', function () {
                _showTarget(m.apero_name, m.payload,
                            m.entry ? { entry: m.entry } : null);
                rtPicker.style.display = 'none';
            });
            li.appendChild(btn);
            rtPickerList.appendChild(li);
        });
        rtPicker.style.display = 'block';
    }

    function _fetchJson(url) {
        return fetch(url, { credentials: 'same-origin' })
            .then(function (resp) {
                if (!resp.ok) {
                    throw new Error('HTTP ' + resp.status);
                }
                return resp.json();
            });
    }

    function _resolveByName() {
        var input = document.getElementById('rt-name-query');
        var name = input ? input.value.trim() : '';
        if (!name) {
            _showError('Enter a target name');
            return;
        }
        _resetUi();
        _hideOnlineButtons();
        _showLoading(true);
        _fetchJson('/api/astrometrics/resolve-by-name'
            + '?name=' + encodeURIComponent(name))
            .then(function (data) {
                _showLoading(false);
                if (!data.success) {
                    _showError(data.error || 'Resolve failed');
                    return;
                }
                if (!data.apero_name) {
                    // Reveal the "Resolve online" buttons now that
                    // the local lookup has confirmed the target is
                    // not in the APERO astrometric database.
                    _showOnlineButtons(name);
                    _showError('"' + name + '" not found in the '
                        + 'APERO astrometric database. Use '
                        + '"Resolve online" to query SIMBAD.');
                    return;
                }
                _showTarget(data.apero_name, data.payload);
                _showRejectionBanner(data);
            })
            .catch(function (err) {
                _showLoading(false);
                _showError(String(err));
            });
    }

    function _resolveByCoords() {
        var raEl = document.getElementById('rt-ra');
        var decEl = document.getElementById('rt-dec');
        var radEl = document.getElementById('rt-radius');
        var ra = raEl ? raEl.value.trim() : '';
        var dec = decEl ? decEl.value.trim() : '';
        var rad = radEl ? (radEl.value || '60') : '60';
        if (!ra || !dec) {
            _showError('Enter RA and Dec in degrees');
            return;
        }
        _resetUi();
        _showLoading(true);
        var url = '/api/astrometrics/resolve-by-coords'
            + '?ra=' + encodeURIComponent(ra)
            + '&dec=' + encodeURIComponent(dec)
            + '&radius=' + encodeURIComponent(rad);
        _fetchJson(url)
            .then(function (data) {
                _showLoading(false);
                if (!data.success) {
                    _showError(data.error || 'Resolve failed');
                    return;
                }
                var matches = data.matches || [];
                if (!matches.length) {
                    _showError('No targets within '
                        + (data.radius_arcsec || rad)
                        + ' arcsec of (' + ra + ', ' + dec + ').');
                    return;
                }
                if (matches.length === 1) {
                    _showTarget(matches[0].apero_name,
                                matches[0].payload);
                } else {
                    _showPicker(matches);
                }
            })
            .catch(function (err) {
                _showLoading(false);
                _showError(String(err));
            });
    }

    function _resolveByFilter() {
        var colEl = document.getElementById('rt-adv-column');
        var matchEl = document.getElementById('rt-adv-match');
        var valEl = document.getElementById('rt-adv-value');
        var col = colEl ? colEl.value.trim() : '';
        var matchMode = matchEl ? matchEl.value : 'auto';
        var val = valEl ? valEl.value : '';
        if (!col) {
            _showError('Pick a column to filter on');
            return;
        }
        _resetUi();
        _showLoading(true);
        var url = '/api/astrometrics/resolve-by-filter'
            + '?column=' + encodeURIComponent(col)
            + '&match=' + encodeURIComponent(matchMode)
            + '&value=' + encodeURIComponent(val);
        _fetchJson(url)
            .then(function (data) {
                _showLoading(false);
                if (!data.success) {
                    _showError(data.error || 'Filter failed');
                    return;
                }
                var matches = data.matches || [];
                if (!matches.length) {
                    _showError('No matches.');
                    return;
                }
                if (matches.length === 1) {
                    _showTarget(matches[0].apero_name,
                                matches[0].payload);
                } else {
                    _showPicker(matches);
                }
            })
            .catch(function (err) {
                _showLoading(false);
                _showError(String(err));
            });
    }

    function _populateColumns() {
        var sel = document.getElementById('rt-adv-column');
        if (!sel) return;
        _fetchJson('/api/astrometrics/columns')
            .then(function (data) {
                if (!data.success) return;
                sel.innerHTML = '';
                (data.columns || []).forEach(function (col) {
                    var opt = document.createElement('option');
                    opt.value = col;
                    opt.textContent = col;
                    sel.appendChild(opt);
                });
            })
            .catch(function () {
                sel.innerHTML = '<option value="">'
                    + '(failed to load columns)</option>';
            });
    }

    /* Bind buttons */
    var btnName = document.getElementById('rt-resolve-name');
    if (btnName) btnName.addEventListener('click', _resolveByName);
    var nameInput = document.getElementById('rt-name-query');
    if (nameInput) {
        nameInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') _resolveByName();
        });
    }
    var btnCoords = document.getElementById('rt-resolve-coords');
    if (btnCoords) {
        btnCoords.addEventListener('click', _resolveByCoords);
    }
    var btnFilter = document.getElementById('rt-resolve-filter');
    if (btnFilter) {
        btnFilter.addEventListener('click', _resolveByFilter);
    }

    function _resolveOnlineByName() {
        var input = document.getElementById('rt-name-query');
        var name = input ? input.value.trim() : '';
        if (!name) {
            _showError('Enter a target name');
            return;
        }
        _resetUi();
        _showLoading(true);
        _fetchJson('/api/astrometrics/resolve-online-by-name'
            + '?name=' + encodeURIComponent(name))
            .then(function (data) {
                _showLoading(false);
                if (!data.success) {
                    _showError(data.error || 'Resolve failed');
                    return;
                }
                if (!data.apero_name) {
                    _showNotFoundRequest(name);
                    return;
                }
                _showTarget(data.apero_name, data.payload,
                            { entry: data.entry });
            })
            .catch(function (err) {
                _showLoading(false);
                _showError(String(err));
            });
    }

    function _resolveOnlineByCoords() {
        var raEl = document.getElementById('rt-ra');
        var decEl = document.getElementById('rt-dec');
        var radEl = document.getElementById('rt-radius');
        var ra = raEl ? raEl.value.trim() : '';
        var dec = decEl ? decEl.value.trim() : '';
        var rad = radEl ? (radEl.value || '60') : '60';
        if (!ra || !dec) {
            _showError('Enter RA and Dec in degrees');
            return;
        }
        _resetUi();
        _showLoading(true);
        _fetchJson('/api/astrometrics/resolve-online-by-coords'
            + '?ra=' + encodeURIComponent(ra)
            + '&dec=' + encodeURIComponent(dec)
            + '&radius=' + encodeURIComponent(rad))
            .then(function (data) {
                _showLoading(false);
                if (!data.success) {
                    _showError(data.error || 'Resolve failed');
                    return;
                }
                var matches = data.matches || [];
                if (!matches.length) {
                    _showError('No SIMBAD targets within '
                        + rad + ' arcsec.');
                    return;
                }
                if (matches.length === 1) {
                    _showTarget(matches[0].apero_name,
                                matches[0].payload);
                } else {
                    _showPicker(matches);
                }
            })
            .catch(function (err) {
                _showLoading(false);
                _showError(String(err));
            });
    }

    function _showNotFoundRequest(name) {
        if (!rtError) return;
        rtError.innerHTML = '';
        var perms = (window.AperoRI
            && window.AperoRI.userPerms) || [];
        var isMonitor = _hasAnyMonitorPerm(perms);

        var span = document.createElement('span');
        span.textContent = '"' + name + '" was not found online. ';
        rtError.appendChild(span);

        if (isMonitor) {
            var link = document.createElement('a');
            link.href = '#';
            link.className = 'ari-link';
            link.style.marginLeft = '0.5rem';
            link.textContent = 'Open Add manually mode';
            link.addEventListener('click', function (ev) {
                ev.preventDefault();
                _openAddManually(name);
            });
            rtError.appendChild(link);
        } else {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'ari-btn ari-btn--xs ari-btn--primary';
            btn.innerHTML = '<i class="fa-solid fa-flag"></i>'
                + ' Request manual object';
            btn.style.marginLeft = '0.5rem';
            btn.addEventListener('click', function () {
                _requestManualObject(name);
            });
            rtError.appendChild(btn);
        }

        var hint = document.createElement('div');
        hint.className = 'ari-tinfo-source';
        hint.style.marginTop = '0.5rem';
        if (isMonitor) {
            hint.textContent = 'Suggestion: use Add manually to add '
                + 'this target.';
        } else {
            hint.textContent = 'Suggestion: request a manual object '
                + 'entry for monitor review.';
        }
        rtError.appendChild(hint);
        rtError.style.display = 'block';
    }

    function _openAddManually(name) {
        var tab = document.querySelector(
            '.ari-htab[data-htab="add-manually"]');
        if (!tab) return;
        tab.click();
        var input = document.getElementById('am-man-name');
        if (input) {
            input.value = name || '';
            input.focus();
        }
    }

    function _requestManualObject(name) {
        var reason = window.prompt(
            'Target "' + name + '" was not found online.\n\n'
            + 'Add optional notes for the monitor (why this should '
            + 'be added manually):', '');
        if (reason === null) return;
        var origin = window.location.pathname
            + '?resolve=' + encodeURIComponent(name);
        fetch('/api/issues/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                kind: 'astrometric',
                type: 'request.manual object',
                title: 'Manual object request: ' + name,
                reason: reason || ('Request manual object: ' + name),
                apero_name: name,
                origin_url: origin,
                visibility: 'monitor'
            })
        }).then(function (r) { return r.json(); })
        .then(function (data) {
            if (data && data.success) {
                _openAddManually(name);
                window.alert('Manual-object request #'
                    + data.issue.id + ' filed for monitor review.');
            } else {
                window.alert('Failed to file request: '
                    + ((data && data.error) || 'unknown'));
            }
        }).catch(function (err) {
            window.alert('Failed to file request: ' + err);
        });
    }

    var btnOnName = document.getElementById('rt-resolve-online-name');
    if (btnOnName) {
        btnOnName.addEventListener('click', _resolveOnlineByName);
    }
    var btnOnCoords = document.getElementById(
        'rt-resolve-online-coords');
    if (btnOnCoords) {
        btnOnCoords.addEventListener(
            'click', _resolveOnlineByCoords);
    }

    /* Populate column dropdown lazily on first resolve-target tab
       activation */
    var advTab = document.getElementById('rt-tab-advanced');
    if (advTab) {
        var loaded = false;
        advTab.addEventListener('click', function () {
            if (!loaded) {
                _populateColumns();
                loaded = true;
            }
        });
    }
}());


/* ============================================================== */
/* Astrometric database tab                                        */
/* ============================================================== */
(function () {
    'use strict';
    var loaded = false;
    var dt = null;

    function _esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function _fmt_number(v, digits) {
        if (v === null || v === undefined || v === '') return '';
        var n = Number(v);
        if (!isFinite(n)) return String(v);
        return n.toFixed(digits);
    }

    function _open_resolve_target(aperoName) {
        // Switch to the Resolve-target tab, then to its "by name"
        // sub-tab, fill the name input and trigger Resolve.
        var tab = document.querySelector(
            '.ari-htab[data-htab="resolve-target"]');
        if (tab) tab.click();
        var subTab = document.querySelector(
            '#astro-tab-resolve-target '
            + '.ot-find-tab[aria-controls="rt-tab-name"]');
        if (subTab) subTab.click();
        var input = document.getElementById('rt-name-query');
        if (input) {
            input.value = aperoName;
        }
        var btn = document.getElementById('rt-resolve-name');
        if (btn) {
            // Defer click to allow tab CSS transition to apply
            setTimeout(function () { btn.click(); }, 30);
        }
    }

    function _build_columns() {
        return [
            {
                key: 'APERO_NAME',
                label: 'APERO_NAME',
                filter: 'text',
                render: function (val) {
                    if (!val) return '';
                    var a = document.createElement('a');
                    a.href = '#';
                    a.className = 'ari-link';
                    a.textContent = val;
                    a.addEventListener('click', function (ev) {
                        ev.preventDefault();
                        _open_resolve_target(val);
                    });
                    return a;
                }
            },
            { key: 'APERO_CLASS', label: 'APERO_CLASS' },
            {
                key: 'RA', label: 'RA', type: 'number',
                render: function (v) { return _fmt_number(v, 5); }
            },
            {
                key: 'DEC', label: 'Dec', type: 'number',
                render: function (v) { return _fmt_number(v, 5); }
            },
            {
                key: 'TEFF', label: 'Teff', type: 'number',
                render: function (v) { return _fmt_number(v, 0); }
            },
            { key: 'SPT', label: 'Spectral Type' },
            {
                key: 'STATUS', label: 'Status',
                render: function (v) {
                    var s = String(v || '').toLowerCase();
                    if (!s) return '';
                    return '<span class="ari-dt__status '
                        + 'ari-dt__status--' + _esc(s) + '">'
                        + _esc(s) + '</span>';
                }
            },
            { key: 'KEYWORDS', label: 'Keywords' },
            { key: 'NOTES', label: 'Notes' }
        ];
    }

    function _load() {
        var tableEl = document.getElementById('adb-table');
        var statusEl = document.getElementById('adb-status');
        var countEl = document.getElementById('adb-count');
        if (!tableEl) return;
        if (statusEl) {
            statusEl.innerHTML = '<i class="fa-solid fa-spinner '
                + 'fa-spin"></i> Loading astrometric database...';
        }
        fetch('/api/astrometrics/list-all',
              { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    if (statusEl) {
                        statusEl.textContent = 'Failed to load: '
                            + ((data && data.error) || 'unknown');
                    }
                    return;
                }
                if (statusEl) statusEl.textContent = '';
                if (!window.AriDataTable) {
                    if (statusEl) {
                        statusEl.textContent = 'AriDataTable not '
                            + 'loaded (script order issue).';
                    }
                    return;
                }
                dt = window.AriDataTable.create({
                    table: tableEl,
                    columns: _build_columns(),
                    rows: data.rows || [],
                    dropdownThreshold: 10,
                    emptyMsg: 'No astrometric entries match.',
                    onRender: function (rendered, all) {
                        if (countEl) {
                            countEl.textContent = rendered.length
                                + ' / ' + all.length + ' entries';
                        }
                    }
                });
            })
            .catch(function (err) {
                if (statusEl) {
                    statusEl.textContent = 'Failed to load: ' + err;
                }
            });
    }

    var dbTab = document.querySelector(
        '.ari-htab[data-htab="astrom-db"]');
    if (dbTab) {
        dbTab.addEventListener('click', function () {
            if (!loaded) {
                loaded = true;
                _load();
            }
        });
    }
}());


// ===========================================================
// Rejected object names tab (monitor-gated; renders cards +
// modal "add rejection" form posting to /api/astrometrics/add-
// rejected). Tab is only present in DOM when the server-side
// page-view helper sets `astrometrics_can_manage_rejects=true`.
// ===========================================================
(function () {
    'use strict';
    var rejTab = document.querySelector(
        '.ari-htab[data-htab="rejected"]');
    if (!rejTab) return;
    var loaded = false;

    function _esc(s) {
        return String(s == null ? '' : s).replace(
            /[<>&"]/g, function (c) {
                return ({'<': '&lt;', '>': '&gt;',
                         '&': '&amp;',
                         '"': '&quot;'})[c];
            });
    }

    function _renderCards(rows) {
        var host = document.getElementById('rej-cards');
        var cnt = document.getElementById('rej-count');
        if (cnt) cnt.textContent = rows.length + ' rejected';
        if (!host) return;
        host.innerHTML = '';

        // Always-first "Add" card
        var addCard = document.createElement('div');
        addCard.className = 'rej-card rej-card--add';
        addCard.innerHTML = '<div class="rej-card__add-inner">'
            + '<i class="fa-solid fa-plus"></i>'
            + '<span>Add a new rejected name</span>'
            + '</div>';
        addCard.addEventListener('click', _openAddOverlay);
        host.appendChild(addCard);

        rows.forEach(function (row) {
            var card = document.createElement('div');
            card.className = 'rej-card';
            var aliases = (row.ALIASES || []).map(_esc).join(', ');
            var html = '<header class="rej-card__head">'
                + '<i class="fa-solid fa-ban"></i>'
                + '<span class="rej-card__name">'
                + _esc(row.APERO_NAME) + '</span>'
                + '</header>';
            if (aliases) {
                html += '<div class="rej-card__field">'
                    + '<span class="rej-card__label">Aliases:</span>'
                    + ' ' + aliases + '</div>';
            }
            if (row.NOTES) {
                html += '<div class="rej-card__field">'
                    + '<span class="rej-card__label">Notes:</span>'
                    + ' ' + _esc(row.NOTES) + '</div>';
            }
            html += '<footer class="rej-card__meta">'
                + 'added by <strong>' + _esc(row.FIRST_AUTHOR)
                + '</strong>';
            if (row.FIRST_UPDATED) {
                html += ' on ' + _esc(row.FIRST_UPDATED);
            }
            html += '</footer>';
            card.innerHTML = html;
            host.appendChild(card);
        });
    }

    function _load() {
        var statusEl = document.getElementById('rej-status');
        if (statusEl) {
            statusEl.innerHTML = '<i class="fa-solid fa-spinner '
                + 'fa-spin"></i> Loading rejected names...';
        }
        fetch('/api/astrometrics/list-rejected',
              { credentials: 'same-origin' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data || !data.success) {
                    if (statusEl) {
                        statusEl.textContent = 'Failed to load: '
                            + ((data && data.error) || 'unknown');
                    }
                    return;
                }
                if (statusEl) statusEl.textContent = '';
                _renderCards(data.rows || []);
            })
            .catch(function (err) {
                if (statusEl) {
                    statusEl.textContent = 'Failed to load: ' + err;
                }
            });
    }

    function _openAddOverlay() {
        var ov = document.getElementById('rej-add-overlay');
        if (!ov) return;
        ov.hidden = false;
        var nameEl = document.getElementById('rej-add-name');
        if (nameEl) {
            nameEl.value = '';
            nameEl.focus();
        }
        var alEl = document.getElementById('rej-add-aliases');
        if (alEl) alEl.value = '';
        var ntEl = document.getElementById('rej-add-notes');
        if (ntEl) ntEl.value = '';
        var st = document.getElementById('rej-add-status');
        if (st) st.textContent = '';
    }
    function _closeAddOverlay() {
        var ov = document.getElementById('rej-add-overlay');
        if (ov) ov.hidden = true;
    }

    function _submitAdd() {
        var nameEl = document.getElementById('rej-add-name');
        var alEl = document.getElementById('rej-add-aliases');
        var ntEl = document.getElementById('rej-add-notes');
        var st = document.getElementById('rej-add-status');
        var name = nameEl ? nameEl.value.trim() : '';
        if (!name) {
            if (st) st.textContent = 'Object name is required.';
            return;
        }
        var aliases = (alEl ? alEl.value : '')
            .split(/\r?\n/)
            .map(function (s) { return s.trim(); })
            .filter(function (s) { return s.length > 0; });
        var notes = ntEl ? ntEl.value.trim() : '';
        if (st) {
            st.innerHTML = '<i class="fa-solid fa-spinner '
                + 'fa-spin"></i> Saving...';
        }
        fetch('/api/astrometrics/add-rejected', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                apero_name: name,
                aliases: aliases,
                notes: notes
            })
        }).then(function (r) {
            return r.json().then(function (j) {
                return { ok: r.ok, body: j };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                if (st) {
                    st.textContent = 'Failed: '
                        + ((res.body && res.body.error)
                           || ('HTTP error'));
                }
                return;
            }
            _closeAddOverlay();
            _load();
        }).catch(function (err) {
            if (st) st.textContent = 'Failed: ' + err;
        });
    }

    rejTab.addEventListener('click', function () {
        if (!loaded) {
            loaded = true;
            _load();
        }
    });

    // overlay close handlers (delegated so they survive any later
    // re-render of the panel body)
    document.addEventListener('click', function (ev) {
        var t = ev.target;
        if (!t) return;
        if (t.closest && t.closest('[data-rej-overlay-close]')) {
            _closeAddOverlay();
        }
    });
    var saveBtn = document.getElementById('rej-add-save');
    if (saveBtn) saveBtn.addEventListener('click', _submitAdd);
}());


// ===========================================================
// Add manually tab (monitor-gated; posts to
// /api/astrometrics/add-manual). Tab is only present in DOM
// when the server-side page-view helper sets
// `astrometrics_can_manage_rejects=true`.
// ===========================================================
(function () {
    'use strict';
    var amTab = document.querySelector(
        '.ari-htab[data-htab="add-manually"]');
    if (!amTab) return;

    function _val(id) {
        var el = document.getElementById(id);
        return el ? String(el.value || '').trim() : '';
    }
    function _checked(id) {
        var el = document.getElementById(id);
        return !!(el && el.checked);
    }
    function _setStatus(id, html) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = html;
    }
    function _aliasesFromTextarea(id) {
        return _val(id).split(/\r?\n/)
            .map(function (s) { return s.trim(); })
            .filter(function (s) { return s.length > 0; });
    }

    // ---- Add-manual-target form ----
    var _MANUAL_NUMERIC = [
        ['am-man-ra', 'ra'],
        ['am-man-dec', 'dec'],
        ['am-man-epoch', 'epoch'],
        ['am-man-pmra', 'pmra'],
        ['am-man-pmde', 'pmde'],
        ['am-man-plx', 'plx'],
        ['am-man-rv', 'rv'],
        ['am-man-teff', 'teff']
    ];

    function _submitManual() {
        var name = _val('am-man-name');
        if (!name) {
            _setStatus('am-man-status',
                'APERO_NAME is required.');
            return;
        }
        var payload = {
            apero_name: name,
            apero_class: _val('am-man-class') || 'STAR',
            original_name: _val('am-man-orig'),
            simbad_name: _val('am-man-simbad'),
            spt: _val('am-man-spt'),
            gaia_source_id: _val('am-man-gaia'),
            aliases: _aliasesFromTextarea('am-man-aliases'),
            notes: _val('am-man-notes'),
            no_pm: _checked('am-man-nopm')
        };
        // numeric fields: only include keys that the user actually
        // typed something into (so the server can leave them
        // unset rather than store explicit nulls)
        for (var i = 0; i < _MANUAL_NUMERIC.length; i++) {
            var pair = _MANUAL_NUMERIC[i];
            var raw = _val(pair[0]);
            if (raw !== '') payload[pair[1]] = raw;
        }
        // strip empty optional strings to keep the on-disk yaml
        // clean
        ['original_name', 'simbad_name', 'spt',
         'gaia_source_id', 'notes'].forEach(function (k) {
            if (!payload[k]) delete payload[k];
        });
        _setStatus('am-man-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> '
            + 'Saving...');
        fetch('/api/astrometrics/add-manual', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(function (r) {
            return r.json().then(function (j) {
                return { ok: r.ok, body: j };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                _setStatus('am-man-status',
                    'Failed: ' + ((res.body && res.body.error)
                                  || 'HTTP error'));
                return;
            }
            _setStatus('am-man-status',
                '<i class="fa-solid fa-check"></i> '
                + 'Created pending entry for "'
                + name + '".');
            // reset all manual-form inputs
            ['am-man-name', 'am-man-orig', 'am-man-simbad',
             'am-man-ra', 'am-man-dec', 'am-man-epoch',
             'am-man-pmra', 'am-man-pmde', 'am-man-plx',
             'am-man-rv', 'am-man-teff', 'am-man-spt',
             'am-man-gaia', 'am-man-aliases', 'am-man-notes']
                .forEach(function (id) {
                    var el = document.getElementById(id);
                    if (el) el.value = '';
                });
            var nopm = document.getElementById('am-man-nopm');
            if (nopm) nopm.checked = false;
            var cls = document.getElementById('am-man-class');
            if (cls) cls.value = 'STAR';
        }).catch(function (err) {
            _setStatus('am-man-status', 'Failed: ' + err);
        });
    }

    var manBtn = document.getElementById('am-man-save');
    if (manBtn) manBtn.addEventListener('click', _submitManual);
}());
