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
    var rtEditBtn = document.getElementById('rt-target-edit');
    var rtVerifyBtn = document.getElementById('rt-target-verify');
    var rtUploadBtn = document.getElementById('rt-target-upload');
    var rtCurrentEntry = null;

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
        if (rtEditBtn) {
            rtEditBtn.hidden = true;
            rtEditBtn.disabled = false;
        }
        if (rtVerifyBtn) {
            rtVerifyBtn.hidden = true;
            rtVerifyBtn.disabled = false;
        }
        if (rtUploadBtn) {
            rtUploadBtn.hidden = true;
            rtUploadBtn.disabled = false;
        }
        rtCurrentEntry = null;
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

    function _wireEditButton(aperoName, entry) {
        if (!rtEditBtn || !entry) return;
        // replace handler each time
        var fresh = rtEditBtn.cloneNode(true);
        rtEditBtn.parentNode.replaceChild(fresh, rtEditBtn);
        rtEditBtn = fresh;
        rtEditBtn.addEventListener('click', function () {
            // Switch to Add-manually tab
            var tab = document.querySelector(
                '.ari-htab[data-htab="add-manually"]');
            if (tab) tab.click();
            // prefill the form with current entry
            if (window.AriManualTargetForm
                    && typeof window.AriManualTargetForm
                    .prefill === 'function') {
                window.AriManualTargetForm.prefill(entry);
            }
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
                disableInlineEdit: true,
                userPerms: (window.AperoRI
                    && window.AperoRI.userPerms) || []
            });
        }
        // Show edit button for any resolved entry — but only when
        // the user has manage.astrometrics. Without it the backend
        // would refuse, so the button just confuses people.
        var entry = (opts && (opts.entry || opts.raw)) || null;
        var _userPermsList = (window.AperoRI
            && window.AperoRI.userPerms) || [];
        var canEditAstrom = _userPermsList.indexOf(
            'manage.astrometrics') !== -1;
        if (entry && rtEditBtn) {
            if (canEditAstrom) {
                rtEditBtn.hidden = false;
                rtCurrentEntry = entry;
                _wireEditButton(apero_name, entry);
            } else {
                rtEditBtn.hidden = true;
            }
        }
        // Show the upload button only for transient (online-resolved)
        // entries — and only for monitors.
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
                _showTarget(data.apero_name, data.payload,
                            { entry: data.entry });
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
                                matches[0].payload,
                                { entry: matches[0].entry });
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
                                matches[0].payload,
                                { entry: matches[0].entry });
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
            {
                key: 'KEYWORDS', label: 'Keywords',
                render: function (v) {
                    if (Array.isArray(v)) return v.join(', ');
                    return v == null ? '' : String(v);
                }
            },
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
    // expose internal hook for tab activation re-wiring
    
    var userPerms = (window.AperoRI && window.AperoRI.userPerms) || [];
    var canEditRejected = userPerms.indexOf(
        'manage.astrometrics') !== -1;
    var _allRows = [];
    var _filterText = '';

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
        if (cnt) {
            if (_filterText
                && rows.length !== _allRows.length) {
                cnt.textContent = rows.length + ' of '
                    + _allRows.length + ' rejected';
            } else {
                cnt.textContent = rows.length + ' rejected';
            }
        }
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
            var aliasArr = (row.ALIASES || []);
            var aliases = aliasArr.map(_esc).join(', ');
            var aliasesPlain = aliasArr.join(', ');
            var html = '<header class="rej-card__head" title="'
                + _esc(row.APERO_NAME) + '">'
                + '<i class="fa-solid fa-ban"></i>'
                + '<span class="rej-card__name">'
                + _esc(row.APERO_NAME) + '</span>'
                + '</header>';
            if (aliases) {
                html += '<div class="rej-card__field" title="'
                    + _esc(aliasesPlain) + '">'
                    + '<span class="rej-card__label">Aliases:</span>'
                    + ' ' + aliases + '</div>';
            }
            if (row.NOTES) {
                html += '<div class="rej-card__field" title="'
                    + _esc(String(row.NOTES)) + '">'
                    + '<span class="rej-card__label">Notes:</span>'
                    + ' ' + _esc(row.NOTES) + '</div>';
            }
            var metaPlain = 'added by ' + (row.FIRST_AUTHOR || '')
                + (row.FIRST_UPDATED
                    ? (' on ' + row.FIRST_UPDATED) : '');
            html += '<div class="rej-card__meta" title="'
                + _esc(metaPlain) + '">'
                + 'by <strong>' + _esc(row.FIRST_AUTHOR)
                + '</strong>';
            if (row.FIRST_UPDATED) {
                html += ' ' + _esc(row.FIRST_UPDATED);
            }
            html += '</div>';
            html += '<div class="rej-card__actions">'
                + '<button type="button" class="rej-card__action"'
                + ' data-rej-open-manual title="Open in Add manually">'
                + '<i class="fa-solid fa-pen-to-square"></i>'
                + '</button>';
            if (canEditRejected) {
                html += '<button type="button" class="rej-card__action"'
                    + ' data-rej-edit title="Edit rejected entry">'
                    + '<i class="fa-solid fa-pen"></i>'
                    + '</button>'
                    + '<button type="button" '
                    + 'class="rej-card__action rej-card__action--danger"'
                    + ' data-rej-delete title="Delete rejected entry">'
                    + '<i class="fa-solid fa-trash"></i>'
                    + '</button>';
            }
            html += '</div>';
            card.innerHTML = html;
            var openBtn = card.querySelector('[data-rej-open-manual]');
            if (openBtn) {
                openBtn.addEventListener('click', function () {
                    _openManualEditor(row);
                });
            }
            if (canEditRejected) {
                var editBtn = card.querySelector('[data-rej-edit]');
                if (editBtn) {
                    editBtn.addEventListener('click', function () {
                        _openAddOverlay(row);
                    });
                }
                var delBtn = card.querySelector('[data-rej-delete]');
                if (delBtn) {
                    delBtn.addEventListener('click', function () {
                        _deleteRejected(row);
                    });
                }
            }
            host.appendChild(card);
        });
    }

    function _setOverlayMode(mode, row) {
        var modeEl = document.getElementById('rej-add-mode');
        var origEl = document.getElementById('rej-add-original');
        var titleEl = document.getElementById('rej-overlay-title');
        var saveLabelEl = document.getElementById(
            'rej-overlay-save-label');
        if (modeEl) modeEl.value = mode;
        if (origEl) {
            origEl.value = (row && row.APERO_NAME)
                ? String(row.APERO_NAME) : '';
        }
        if (titleEl) {
            titleEl.innerHTML = (mode === 'edit')
                ? '<i class="fa-solid fa-pen"></i> '
                    + 'Edit rejected object name'
                : '<i class="fa-solid fa-ban"></i> '
                    + 'Add a rejected object name';
        }
        if (saveLabelEl) {
            saveLabelEl.textContent = (mode === 'edit')
                ? 'Save changes'
                : 'Save rejection';
        }
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
                _allRows = data.rows || [];
                _applyFilter();
            })
            .catch(function (err) {
                if (statusEl) {
                    statusEl.textContent = 'Failed to load: ' + err;
                }
            });
    }

    function _matches(row, q) {
        if (!q) return true;
        var name = String(row.APERO_NAME || '').toLowerCase();
        if (name.indexOf(q) !== -1) return true;
        var aliases = row.ALIASES || [];
        for (var i = 0; i < aliases.length; i++) {
            if (String(aliases[i] || '').toLowerCase()
                    .indexOf(q) !== -1) {
                return true;
            }
        }
        return false;
    }

    function _applyFilter() {
        var q = (_filterText || '').trim().toLowerCase();
        var rows = !q
            ? _allRows.slice()
            : _allRows.filter(function (r) {
                return _matches(r, q);
            });
        _renderCards(rows);
    }

    function _wireFilter() {
        var input = document.getElementById('rej-filter-input');
        var clear = document.getElementById('rej-filter-clear');
        if (!input || input.dataset.wired) return;
        input.dataset.wired = '1';
        input.addEventListener('input', function () {
            _filterText = input.value || '';
            if (clear) clear.hidden = !_filterText;
            _applyFilter();
        });
        if (clear) {
            clear.addEventListener('click', function () {
                input.value = '';
                _filterText = '';
                clear.hidden = true;
                _applyFilter();
                input.focus();
            });
        }
    }

    function _openAddOverlay(row) {
        var ov = document.getElementById('rej-add-overlay');
        if (!ov) return;
        ov.hidden = false;
        _setOverlayMode(row ? 'edit' : 'add', row || null);
        var nameEl = document.getElementById('rej-add-name');
        if (nameEl) {
            nameEl.value = row ? String(row.APERO_NAME || '') : '';
            nameEl.focus();
        }
        var alEl = document.getElementById('rej-add-aliases');
        if (alEl) {
            alEl.value = row && Array.isArray(row.ALIASES)
                ? row.ALIASES.join('\n')
                : '';
        }
        var ntEl = document.getElementById('rej-add-notes');
        if (ntEl) ntEl.value = row ? String(row.NOTES || '') : '';
        var st = document.getElementById('rej-add-status');
        if (st) st.textContent = '';
    }

    function _closeAddOverlay() {
        var ov = document.getElementById('rej-add-overlay');
        if (ov) ov.hidden = true;
    }

    function _openManualEditor(row) {
        var tab = document.querySelector(
            '.ari-htab[data-htab="add-manually"]');
        if (tab) tab.click();
        var helper = window.AriManualTargetForm;
        if (helper && typeof helper.prefill === 'function') {
            helper.prefill({
                APERO_NAME: row.APERO_NAME,
                APERO_CLASS: 'OTHER',
                ORIGINAL_NAME: row.ORIGINAL_NAME,
                ALIASES: row.ALIASES,
                NOTES: row.NOTES
            });
        } else {
            var nameEl = document.getElementById('am-man-name');
            if (nameEl) nameEl.value = row.APERO_NAME || '';
        }
    }

    function _deleteRejected(row) {
        var name = String((row && row.APERO_NAME) || '');
        if (!name) return;
        if (!window.confirm('Delete rejected entry for "'
                            + name + '"?')) {
            return;
        }
        var st = document.getElementById('rej-status');
        if (st) {
            st.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> '
                + 'Deleting "' + _esc(name) + '"...';
        }
        fetch('/api/astrometrics/delete-rejected', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ apero_name: name })
        }).then(function (r) {
            return r.json().then(function (j) {
                return { ok: r.ok, body: j };
            });
        }).then(function (res) {
            if (!res.body || !res.body.success) {
                if (st) {
                    st.textContent = 'Delete failed: '
                        + ((res.body && res.body.error)
                           || 'HTTP error');
                }
                return;
            }
            if (st) st.textContent = '';
            _load();
        }).catch(function (err) {
            if (st) st.textContent = 'Delete failed: ' + err;
        });
    }

    function _submitAddOrEdit() {
        var nameEl = document.getElementById('rej-add-name');
        var alEl = document.getElementById('rej-add-aliases');
        var ntEl = document.getElementById('rej-add-notes');
        var st = document.getElementById('rej-add-status');
        var mode = 'add';
        var orig = '';
        var modeEl = document.getElementById('rej-add-mode');
        if (modeEl && modeEl.value === 'edit') mode = 'edit';
        var origEl = document.getElementById('rej-add-original');
        if (origEl) orig = String(origEl.value || '').trim();
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
        var url = (mode === 'edit')
            ? '/api/astrometrics/update-rejected'
            : '/api/astrometrics/add-rejected';
        var body = {
            apero_name: name,
            aliases: aliases,
            notes: notes
        };
        if (mode === 'edit') body.old_apero_name = orig;
        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
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
        _wireFilter();
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
    if (saveBtn) {
        saveBtn.addEventListener('click', _submitAddOrEdit);
    }
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

    function _setValue(id, value) {
        var el = document.getElementById(id);
        if (!el) return;
        el.value = _toInputString(value);
    }

    function _toInputString(value) {
        if (value === null || value === undefined) return '';
        if (Array.isArray(value)) {
            return value.map(function (v) {
                return _toInputString(v);
            }).join('\n');
        }
        if (typeof value === 'object') {
            if (Object.prototype.hasOwnProperty.call(value, 'value')) {
                return _toInputString(value.value);
            }
            try {
                return JSON.stringify(value);
            } catch (e) {
                return '';
            }
        }
        return String(value);
    }

    function _entryValue(entry, key, altKey) {
        var val = null;
        if (entry && Object.prototype.hasOwnProperty.call(entry, key)) {
            val = entry[key];
        } else if (altKey && entry
                && Object.prototype.hasOwnProperty.call(entry, altKey)) {
            val = entry[altKey];
        }
        if (val && typeof val === 'object'
                && Object.prototype.hasOwnProperty.call(val, 'value')) {
            return val.value;
        }
        return val;
    }

    var _EXTRA_FIELD_SPECS = [
        { key: 'RA_J2000_DEG', label: 'RA (J2000) [deg]',
            type: 'number', editable: false },
        { key: 'DEC_J2000_DEG', label: 'Dec (J2000) [deg]',
            type: 'number', editable: false },
        { key: 'RA_HMS', label: 'RA (J2000) HMS', type: 'text',
            editable: false },
        { key: 'DEC_DMS', label: 'Dec (J2000) DMS', type: 'text',
            editable: false },
        { key: 'GALACTIC_LON', label: 'Galactic longitude l [deg]',
            type: 'number', editable: false },
        { key: 'GALACTIC_LAT', label: 'Galactic latitude b [deg]',
            type: 'number', editable: false },
        { key: 'ECLIPTIC_LON', label: 'Ecliptic longitude [deg]',
            type: 'number', editable: false },
        { key: 'ECLIPTIC_LAT', label: 'Ecliptic latitude [deg]',
            type: 'number', editable: false },
        { key: 'V_SKY', label: 'v_sky [km/s]', type: 'number',
            editable: false },
        { key: 'V3D', label: 'v_3D [km/s]', type: 'number',
            editable: false },
        { key: 'U', label: 'U (galactic) [km/s]', type: 'number',
            editable: false },
        { key: 'V', label: 'V (galactic) [km/s]', type: 'number',
            editable: false },
        { key: 'W', label: 'W (galactic) [km/s]', type: 'number',
            editable: false },
        { key: 'G_MAG', label: 'G [mag]', type: 'number',
            editable: true },
        { key: 'GBP_MAG', label: 'G_BP [mag]', type: 'number',
            editable: true },
        { key: 'GRP_MAG', label: 'G_RP [mag]', type: 'number',
            editable: true },
        { key: 'J_MAG', label: 'J [mag]', type: 'number',
            editable: true },
        { key: 'H_MAG', label: 'H [mag]', type: 'number',
            editable: true },
        { key: 'KS_MAG', label: 'Ks [mag]', type: 'number',
            editable: true },
        { key: 'W1_MAG', label: 'W1 [mag]', type: 'number',
            editable: true },
        { key: 'W2_MAG', label: 'W2 [mag]', type: 'number',
            editable: true },
        { key: 'W3_MAG', label: 'W3 [mag]', type: 'number',
            editable: true },
        { key: 'W4_MAG', label: 'W4 [mag]', type: 'number',
            editable: true },
        { key: 'FE_H', label: '[Fe/H] [dex]', type: 'number',
            editable: false },
        { key: 'GAIA_MH_GSPPHOT', label: '[M/H] Gaia GSP-Phot [dex]',
            type: 'number', editable: false },
        { key: 'R_STAR_MKS', label: 'R* (M_Ks) [Rsun]',
            type: 'number', editable: false },
        { key: 'R_STAR_MKS_FEH', label: 'R* (M_Ks+[Fe/H]) [Rsun]',
            type: 'number', editable: false },
        { key: 'GAIA_RADIUS_FLAME', label: 'R* Gaia FLAME [Rsun]',
            type: 'number', editable: false },
        { key: 'MASS_STAR_MANN15', label: 'M* Mann+15 [Msun]',
            type: 'number', editable: false },
        { key: 'MASS_STAR_DELFOSSE00',
            label: 'M* Delfosse+00 [Msun]', type: 'number',
            editable: false },
        { key: 'GAIA_MASS_FLAME', label: 'M* Gaia FLAME [Msun]',
            type: 'number', editable: false },
        { key: 'LOG_G', label: 'log g [cgs]', type: 'number',
            editable: false },
        { key: 'GAIA_LOGG_GSPPHOT',
            label: 'log g Gaia GSP-Phot [cgs]', type: 'number',
            editable: false },
        { key: 'L_STAR', label: 'L* [Lsun]', type: 'number',
            editable: false },
        { key: 'GAIA_LUM_FLAME', label: 'L* Gaia FLAME [Lsun]',
            type: 'number', editable: false },
        { key: 'VSINI', label: 'v sin(i) [km/s]', type: 'number',
            editable: true },
        { key: 'TEFF_GAIA_JH', label: 'Teff (Gaia+JH) [K]',
            type: 'number', editable: false },
        { key: 'TEFF_GAIA', label: 'Teff (Gaia) [K]',
            type: 'number', editable: false },
        { key: 'GAIA_TEFF_GSPPHOT',
            label: 'Teff Gaia GSP-Phot [K]', type: 'number',
            editable: false },
        { key: 'TELLURIC_VSYS_PLUS_VBARY_MIN',
            label: 'Telluric v_sys+v_bary min [km/s]', type: 'number',
            editable: false },
        { key: 'TELLURIC_VSYS_PLUS_VBARY_MAX',
            label: 'Telluric v_sys+v_bary max [km/s]', type: 'number',
            editable: false },
        { key: 'TELLURIC_LIMIT_WINDOWS',
            label: 'Telluric limit windows', type: 'text',
            editable: false }
    ];
    var _EXTRA_FIELD_IDS = [];
    var _manualOriginalEntry = null;
    var _manualOriginalAperoName = '';
    var _manualRestoreFlag = '';

    function _escapeHtml(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g,
            function (ch) {
                return ({
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;'
                })[ch];
            });
    }

    function _entryMapFromPayload(payload) {
        var out = {};
        out.APERO_NAME = _toInputString(payload.apero_name);
        out.APERO_CLASS = _toInputString(payload.apero_class);
        out.ORIGINAL_NAME = _toInputString(payload.original_name);
        out.SIMBAD_NAME = _toInputString(payload.simbad_name);
        out.EPOCH = _toInputString(payload.epoch);
        out.RA = _toInputString(payload.ra);
        out.DEC = _toInputString(payload.dec);
        out.PMRA = _toInputString(payload.pmra);
        out.PMDE = _toInputString(payload.pmde);
        out.PLX = _toInputString(payload.plx);
        out.RV = _toInputString(payload.rv);
        out.TEFF = _toInputString(payload.teff);
        out.SPT = _toInputString(payload.spt);
        out.GAIA_SOURCE_ID = _toInputString(payload.gaia_source_id);
        out.ALIASES = Array.isArray(payload.aliases)
            ? payload.aliases.join('\n')
            : _toInputString(payload.aliases);
        out.KEYWORDS = Array.isArray(payload.keywords)
            ? payload.keywords.join('\n')
            : _toInputString(payload.keywords);
        out.NOTES = _toInputString(payload.notes);
        out.NO_PM = payload.no_pm ? 'true' : 'false';
        var extra = payload.extra_fields || {};
        Object.keys(extra).forEach(function (k) {
            out[String(k || '').toUpperCase()] = _toInputString(extra[k]);
        });
        return out;
    }

    function _entryMapFromOriginal(entry) {
        var out = {};
        if (!entry) return out;
        out.APERO_NAME = _toInputString(_entryValue(entry, 'APERO_NAME'));
        out.APERO_CLASS = _toInputString(_entryValue(entry, 'APERO_CLASS'));
        out.ORIGINAL_NAME = _toInputString(
            _entryValue(entry, 'ORIGINAL_NAME'));
        out.SIMBAD_NAME = _toInputString(_entryValue(entry, 'SIMBAD_NAME'));
        out.EPOCH = _toInputString(_entryValue(entry, 'EPOCH', 'epoch'));
        out.RA = _toInputString(_entryValue(entry, 'RA', 'ra'));
        out.DEC = _toInputString(_entryValue(entry, 'DEC', 'dec'));
        out.PMRA = _toInputString(_entryValue(entry, 'PMRA', 'pmra'));
        out.PMDE = _toInputString(_entryValue(entry, 'PMDE', 'pmde'));
        out.PLX = _toInputString(_entryValue(entry, 'PLX', 'plx'));
        out.RV = _toInputString(_entryValue(entry, 'RV', 'rv'));
        out.TEFF = _toInputString(_entryValue(entry, 'TEFF', 'teff'));
        out.SPT = _toInputString(_entryValue(entry, 'SPT'));
        out.GAIA_SOURCE_ID = _toInputString(
            _entryValue(entry, 'GAIA_SOURCE_ID'));
        var aliases = _entryValue(entry, 'ALIASES');
        out.ALIASES = Array.isArray(aliases)
            ? aliases.join('\n') : _toInputString(aliases);
        var keywords = _entryValue(entry, 'KEYWORDS');
        out.KEYWORDS = Array.isArray(keywords)
            ? keywords.join('\n') : _toInputString(keywords);
        out.NOTES = _toInputString(_entryValue(entry, 'NOTES'));
        out.NO_PM = _entryValue(entry, 'NO_PM') ? 'true' : 'false';
        _EXTRA_FIELD_IDS.forEach(function (pair) {
            if (!pair[2]) return;
            out[pair[1]] = _toInputString(_entryValue(entry, pair[1]));
        });
        return out;
    }

    function _buildChanges(oldMap, newMap) {
        var keys = {};
        Object.keys(oldMap || {}).forEach(function (k) { keys[k] = true; });
        Object.keys(newMap || {}).forEach(function (k) { keys[k] = true; });
        var out = [];
        Object.keys(keys).sort().forEach(function (k) {
            var prev = _toInputString(oldMap[k]);
            var next = _toInputString(newMap[k]);
            if (prev !== next) {
                out.push({ key: k, previous: prev, next: next });
            }
        });
        return out;
    }

    function _showManualDiffOverlay(changes) {
        var _LIST_DIFF_KEYS = { ALIASES: 1, KEYWORDS: 1 };
        function _splitListVal(s) {
            if (s == null) return [];
            return String(s).split(/\r?\n/)
                .map(function (x) { return x.trim(); })
                .filter(function (x) { return x.length > 0; });
        }
        function _chip(text, kind) {
            var styles = {
                kept: 'background:#f1f3f5;color:#495057;'
                    + 'border:1px solid #dee2e6;',
                removed: 'background:#fdecea;color:#a4221a;'
                    + 'border:1px solid #f5c2c0;'
                    + 'text-decoration:line-through;',
                added: 'background:#e6f4ea;color:#1e7e34;'
                    + 'border:1px solid #b6dcc1;',
                edited: 'background:#fff8db;color:#7a5d00;'
                    + 'border:1px solid #f1d97a;font-style:italic;'
            };
            var st = styles[kind] || styles.kept;
            return '<span style="display:inline-block;'
                + 'padding:2px 8px;border-radius:10px;margin:2px 3px;'
                + 'font-size:0.85em;' + st + '">'
                + _escapeHtml(text || '(empty)') + '</span>';
        }
        function _renderListDiff(prevArr, nextArr) {
            var nextSet = {};
            nextArr.forEach(function (v) { nextSet[v] = true; });
            var prevSet = {};
            prevArr.forEach(function (v) { prevSet[v] = true; });
            var wasHtml = prevArr.length
                ? prevArr.map(function (v) {
                    return _chip(v,
                        nextSet[v] ? 'kept' : 'removed');
                }).join('')
                : '<span style="color:#888;font-style:italic;">'
                    + '(empty)</span>';
            var nowHtml = nextArr.length
                ? nextArr.map(function (v) {
                    return _chip(v,
                        prevSet[v] ? 'kept' : 'added');
                }).join('')
                : '<span style="color:#888;font-style:italic;">'
                    + '(empty)</span>';
            return { was: wasHtml, now: nowHtml };
        }
        function _renderScalarDiff(prev, next) {
            var emptyStyle = 'color:#888;font-style:italic;';
            var wasHtml = prev
                ? '<span style="background:#fff8db;color:#7a5d00;'
                    + 'padding:2px 6px;border-radius:4px;'
                    + 'font-style:italic;">'
                    + _escapeHtml(prev).replace(/\n/g, '<br>')
                    + '</span>'
                : '<span style="' + emptyStyle + '">(empty)</span>';
            var nowHtml = next
                ? '<span style="background:#fff8db;color:#7a5d00;'
                    + 'padding:2px 6px;border-radius:4px;'
                    + 'font-style:italic;">'
                    + _escapeHtml(next).replace(/\n/g, '<br>')
                    + '</span>'
                : '<span style="' + emptyStyle + '">(empty)</span>';
            // pure add → green; pure remove → red strikethrough
            if (!prev && next) {
                nowHtml = '<span style="background:#e6f4ea;'
                    + 'color:#1e7e34;padding:2px 6px;'
                    + 'border-radius:4px;">'
                    + _escapeHtml(next).replace(/\n/g, '<br>')
                    + '</span>';
            } else if (prev && !next) {
                wasHtml = '<span style="background:#fdecea;'
                    + 'color:#a4221a;padding:2px 6px;'
                    + 'border-radius:4px;'
                    + 'text-decoration:line-through;">'
                    + _escapeHtml(prev).replace(/\n/g, '<br>')
                    + '</span>';
            }
            return { was: wasHtml, now: nowHtml };
        }
        function _renderDiffCells(c) {
            var key = String(c.key || '').toUpperCase();
            if (_LIST_DIFF_KEYS[key]) {
                return _renderListDiff(
                    _splitListVal(c.previous),
                    _splitListVal(c.next));
            }
            return _renderScalarDiff(c.previous || '',
                                     c.next || '');
        }

        return new Promise(function (resolve) {
            var overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.inset = '0';
            overlay.style.background = 'rgba(0,0,0,0.45)';
            overlay.style.zIndex = '2500';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';

            var hasChanges = !!(changes && changes.length);
            var rows = '';
            if (hasChanges) {
                rows = changes.map(function (c) {
                    var cells = _renderDiffCells(c);
                    return '<tr>'
                        + '<td style="padding:6px 8px;'
                        + ' vertical-align:top;">'
                        + '<code>' + _escapeHtml(c.key)
                        + '</code></td>'
                        + '<td style="padding:6px 8px;'
                        + ' vertical-align:top;">'
                        + cells.was + '</td>'
                        + '<td style="padding:6px 8px;'
                        + ' vertical-align:top;">'
                        + cells.now + '</td>'
                        + '</tr>';
                }).join('');
            }
            var title = hasChanges
                ? 'Confirm target changes'
                : 'No changes were made';
            var body = hasChanges
                ? '<p style="margin:0 0 8px 0;">Review changes to '
                    + 'the original target. Unchanged fields are hidden.</p>'
                    + '<div style="max-height:300px; overflow:auto;">'
                    + '<table style="width:100%; border-collapse:collapse;">'
                    + '<thead><tr><th align="left">Field</th>'
                    + '<th align="left">Was</th><th align="left">Now</th>'
                    + '</tr></thead><tbody>' + rows + '</tbody></table></div>'
                : '<p style="margin:0 0 8px 0;">No changes were made. '
                    + 'You can still confirm to continue.</p>';

            var box = document.createElement('div');
            box.style.background = '#fff';
            box.style.borderRadius = '8px';
            box.style.padding = '14px';
            box.style.width = 'min(820px, 92vw)';
            box.style.maxHeight = '86vh';
            box.style.overflow = 'auto';
            box.innerHTML = '<h3 style="margin:0 0 8px 0;">'
                + _escapeHtml(title) + '</h3>' + body
                + '<div style="display:flex; gap:8px; margin-top:12px;">'
                + '<button type="button" data-manual-diff-cancel '
                + 'class="ari-btn ari-btn--secondary">Cancel</button>'
                + '<button type="button" data-manual-diff-confirm '
                + 'class="ari-btn ari-btn--primary">Confirm</button>'
                + '</div>';

            overlay.appendChild(box);
            document.body.appendChild(overlay);

            function _close(ok) {
                try {
                    document.body.removeChild(overlay);
                } catch (e) {
                    // ignore
                }
                resolve(!!ok);
            }
            overlay.addEventListener('click', function (ev) {
                var t = ev.target;
                if (!t) return;
                if (t === overlay || t.closest('[data-manual-diff-cancel]')) {
                    _close(false);
                } else if (t.closest('[data-manual-diff-confirm]')) {
                    _close(true);
                }
            });
        });
    }

    function _initExtraFieldInputs() {
        var host = document.getElementById('am-man-extra-fields');
        if (!host) return;
        host.innerHTML = '';
        _EXTRA_FIELD_IDS = [];
        _EXTRA_FIELD_SPECS.forEach(function (spec) {
            var id = 'am-man-extra-'
                + String(spec.key || '').toLowerCase();
            var editable = (spec.editable !== false);
            _EXTRA_FIELD_IDS.push([id, spec.key, editable]);
            var label = document.createElement('label');
            label.className = 'ot-find-field';
            var span = document.createElement('span');
            span.className = 'ot-find-field__label';
            span.textContent = spec.label;
            if (!editable) {
                span.classList.add('am-calc-label');
            }
            label.appendChild(span);
            var input = document.createElement('input');
            input.id = id;
            input.className = 'ot-find-input';
            input.type = 'text';
            input.placeholder = 'None';
            if (spec.type === 'number') {
                input.inputMode = 'decimal';
            }
            if (!editable) {
                input.readOnly = true;
                input.classList.add('am-calc-input');
                input.setAttribute('aria-readonly', 'true');
            }
            label.appendChild(input);
            host.appendChild(label);
        });
    }

    function _markComputedFieldsPending() {
        _EXTRA_FIELD_IDS.forEach(function (pair) {
            var editable = !!pair[2];
            if (editable) return;
            var el = document.getElementById(pair[0]);
            if (!el) return;
            el.value = 'Recomputed automatically on save';
        });
    }

    function _bindComputedDependencies() {
        var deps = [
            'am-man-ra', 'am-man-dec', 'am-man-epoch',
            'am-man-pmra', 'am-man-pmde', 'am-man-plx',
            'am-man-rv'
        ];
        deps.forEach(function (id) {
            var el = document.getElementById(id);
            if (!el) return;
            el.addEventListener('input', _markComputedFieldsPending);
        });
    }

    function _setManualSubmitMode(isUpdate) {
        var btn = document.getElementById('am-man-save');
        if (!btn) return;
        if (isUpdate) {
            btn.classList.remove('ari-btn--primary');
            btn.classList.add('am-btn-update');
            btn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> '
                + 'Update target';
            return;
        }
        btn.classList.remove('am-btn-update');
        btn.classList.add('ari-btn--primary');
        btn.innerHTML = '<i class="fa-solid fa-plus"></i> '
            + 'Save manual target';
    }

    function _toggleNoPmInputs() {
        var noPm = _checked('am-man-nopm');
        ['am-man-pmra', 'am-man-pmde'].forEach(function (id) {
            var el = document.getElementById(id);
            if (!el) return;
            el.disabled = !!noPm;
        });
    }

    function _bindNoPmToggle() {
        var chk = document.getElementById('am-man-nopm');
        if (!chk) return;
        chk.addEventListener('change', function () {
            _toggleNoPmInputs();
            _markComputedFieldsPending();
        });
        _toggleNoPmInputs();
    }

    function _prefill(entry) {
        entry = entry || {};
        _manualOriginalEntry = JSON.parse(JSON.stringify(entry));
        _manualOriginalAperoName = _toInputString(
            _entryValue(entry, 'APERO_NAME'));
        _setValue('am-man-name', _entryValue(entry, 'APERO_NAME'));
        _setValue('am-man-orig',
            _entryValue(entry, 'ORIGINAL_NAME'));
        _setValue('am-man-simbad',
            _entryValue(entry, 'SIMBAD_NAME'));
        _setValue('am-man-spt', _entryValue(entry, 'SPT'));
        _setValue('am-man-gaia',
            _entryValue(entry, 'GAIA_SOURCE_ID'));
        _setValue('am-man-notes', _entryValue(entry, 'NOTES'));
        _setValue('am-man-aliases', Array.isArray(
            entry.ALIASES) ? entry.ALIASES.join('\n')
            : (entry.ALIASES || ''));
        var kw = _entryValue(entry, 'KEYWORDS');
        _setValue('am-man-keywords', Array.isArray(kw)
            ? kw.join('\n')
            : (kw == null ? '' : String(kw)));
        _setValue('am-man-ra', _entryValue(entry, 'RA', 'ra'));
        _setValue('am-man-dec', _entryValue(entry, 'DEC', 'dec'));
        _setValue('am-man-epoch',
            _entryValue(entry, 'EPOCH', 'epoch'));
        _setValue('am-man-pmra',
            _entryValue(entry, 'PMRA', 'pmra'));
        _setValue('am-man-pmde',
            _entryValue(entry, 'PMDE', 'pmde'));
        _setValue('am-man-plx', _entryValue(entry, 'PLX', 'plx'));
        _setValue('am-man-rv', _entryValue(entry, 'RV', 'rv'));
        _setValue('am-man-teff', _entryValue(entry, 'TEFF', 'teff'));
        var nopm = document.getElementById('am-man-nopm');
        if (nopm) nopm.checked = !!entry.NO_PM;
        _EXTRA_FIELD_IDS.forEach(function (pair) {
            _setValue(pair[0], _entryValue(entry, pair[1]));
        });
        var cls = document.getElementById('am-man-class');
        var nextClass = String(entry.APERO_CLASS || 'STAR');
        if (cls) {
            cls.value = nextClass;
            if (cls.value !== nextClass) cls.value = 'OTHER';
        }
        var st = document.getElementById('am-man-status');
        if (st) {
            st.innerHTML = '<i class="fa-solid fa-circle-info"></i> '
                + 'Loaded values. Adjust as needed and save.';
        }
        _setManualSubmitMode(!!_manualOriginalAperoName);
        _toggleNoPmInputs();
        var nameEl = document.getElementById('am-man-name');
        if (nameEl) nameEl.focus();
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

    function _collectManualPayload() {
        var name = _val('am-man-name');
        if (!name) {
            _setStatus('am-man-status',
                'APERO_NAME is required.');
            return null;
        }
        var payload = {
            apero_name: name,
            apero_class: _val('am-man-class') || 'STAR',
            original_name: _val('am-man-orig'),
            simbad_name: _val('am-man-simbad'),
            spt: _val('am-man-spt'),
            gaia_source_id: _val('am-man-gaia'),
            aliases: _aliasesFromTextarea('am-man-aliases'),
            keywords: _aliasesFromTextarea('am-man-keywords'),
            notes: _val('am-man-notes'),
            no_pm: _checked('am-man-nopm')
        };
        for (var i = 0; i < _MANUAL_NUMERIC.length; i++) {
            var pair = _MANUAL_NUMERIC[i];
            if (payload.no_pm && (pair[1] === 'pmra'
                                  || pair[1] === 'pmde')) {
                continue;
            }
            var raw = _val(pair[0]);
            if (raw !== '') payload[pair[1]] = raw;
        }
        var extraFields = {};
        _EXTRA_FIELD_IDS.forEach(function (pair) {
            if (!pair[2]) return;
            var raw = _val(pair[0]);
            if (raw !== '') extraFields[pair[1]] = raw;
        });
        if (Object.keys(extraFields).length > 0) {
            payload.extra_fields = extraFields;
        }
        ['original_name', 'simbad_name', 'spt',
         'gaia_source_id', 'notes'].forEach(function (k) {
            if (!payload[k]) delete payload[k];
        });
        return payload;
    }

    function _applyRecomputedEntry(entry) {
        if (!entry) return;
        _EXTRA_FIELD_IDS.forEach(function (pair) {
            if (pair[2]) return;
            _setValue(pair[0], _entryValue(entry, pair[1]));
        });
    }

    function _recomputeManual() {
        var payload = _collectManualPayload();
        if (!payload) return;
        _setStatus('am-man-status',
            '<i class="fa-solid fa-spinner fa-spin"></i> '
            + 'Recomputing values...');
        fetch('/api/astrometrics/recompute-manual', {
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
            _applyRecomputedEntry(res.body.entry);
            _setStatus('am-man-status',
                '<i class="fa-solid fa-check"></i> '
                + 'Computed values refreshed.');
        }).catch(function (err) {
            _setStatus('am-man-status', 'Failed: ' + err);
        });
    }

    function _submitManual() {
        var payload = _collectManualPayload();
        if (!payload) return;
        var name = payload.apero_name;
        var oldMap = _entryMapFromOriginal(_manualOriginalEntry);
        var newMap = _entryMapFromPayload(payload);
        var isEditMode = !!_manualOriginalAperoName;
        if (isEditMode) {
            payload.allow_update = true;
            payload.original_apero_name = _manualOriginalAperoName;
        }
        if (_manualRestoreFlag) {
            payload.source = 'restore';
            payload.restore_history_id = _manualRestoreFlag;
        }
        var changes = isEditMode ? _buildChanges(oldMap, newMap) : [];

        function _doSubmit() {
            _setStatus('am-man-status',
                '<i class="fa-solid fa-spinner fa-spin"></i> '
                + 'Saving (recomputing derived values)...');
            fetch('/api/astrometrics/add-manual', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
            }).then(function (r) {
                return r.text().then(function (txt) {
                    var j = null;
                    try { j = JSON.parse(txt); }
                    catch (e) { j = null; }
                    return { ok: r.ok, status: r.status,
                             body: j, raw: txt };
                });
            }).then(function (res) {
                if (!res.body || !res.body.success) {
                    var msg;
                    if (res.body && res.body.error) {
                        msg = res.body.error;
                    } else if (res.status === 401) {
                        msg = 'Login required (session expired?)';
                    } else if (res.status === 403) {
                        msg = 'Forbidden (missing permission)';
                    } else if (res.status >= 500) {
                        msg = 'Server error (HTTP ' + res.status
                            + '). Check server logs.';
                    } else {
                        msg = 'HTTP ' + res.status;
                    }
                    _setStatus('am-man-status', 'Failed: ' + msg);
                    return;
                }
                var mode = (res.body.mode || 'created').toLowerCase();
                var verb = (mode === 'updated') ? 'Updated' : 'Created';
                _setStatus('am-man-status',
                    '<i class="fa-solid fa-check"></i> '
                    + verb + ' pending entry for "'
                    + name + '".');
                // reset all manual-form inputs
                ['am-man-name', 'am-man-orig', 'am-man-simbad',
                 'am-man-ra', 'am-man-dec', 'am-man-epoch',
                 'am-man-pmra', 'am-man-pmde', 'am-man-plx',
                 'am-man-rv', 'am-man-teff', 'am-man-spt',
                 'am-man-gaia', 'am-man-aliases', 'am-man-keywords',
                 'am-man-notes']
                    .forEach(function (id) {
                        var el = document.getElementById(id);
                        if (el) el.value = '';
                    });
                _EXTRA_FIELD_IDS.forEach(function (pair) {
                    var el = document.getElementById(pair[0]);
                    if (el) el.value = '';
                });
                var nopm = document.getElementById('am-man-nopm');
                if (nopm) nopm.checked = false;
                var cls = document.getElementById('am-man-class');
                if (cls) cls.value = 'STAR';
                _manualOriginalEntry = null;
                _manualOriginalAperoName = '';
                _manualRestoreFlag = '';
                _setManualSubmitMode(false);
                _toggleNoPmInputs();
            }).catch(function (err) {
                _setStatus('am-man-status', 'Failed: ' + err);
            });
        }

        if (!isEditMode) {
            _doSubmit();
            return;
        }
        _showManualDiffOverlay(changes).then(function (ok) {
            if (!ok) return;
            _doSubmit();
        });
    }

    _initExtraFieldInputs();
    _bindComputedDependencies();
    _bindNoPmToggle();
    _setManualSubmitMode(false);
    var recBtn = document.getElementById('am-man-recompute');
    if (recBtn) recBtn.addEventListener('click', _recomputeManual);
    var manBtn = document.getElementById('am-man-save');
    if (manBtn) manBtn.addEventListener('click', _submitManual);
    window.AriManualTargetForm = window.AriManualTargetForm || {};
    window.AriManualTargetForm.prefill = _prefill;
    window.AriManualTargetForm.flagRestore = function (entryId) {
        _manualRestoreFlag = String(entryId || '');
    };
}());
