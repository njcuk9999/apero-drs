(function () {
    'use strict';

    var cfg = window.ARI_APERO_CHECKS_POLICY || {};
    var sectionsApiUrl = String(cfg.sectionsApiUrl || '');
    var checkInfoBaseUrl = String(cfg.checkInfoBaseUrl || '');

    var healthWrap = document.getElementById('acp-health-wrap');
    var catalogFilter = document.getElementById('acp-catalog-filter');
    var catalogLoading = document.getElementById('acp-catalog-loading');
    var catalogWrap = document.getElementById('acp-check-catalog');
    var summaryLoading = document.getElementById('acp-summary-loading');
    var summaryWrap = document.getElementById('acp-profile-summaries');
    var updatedEl = document.getElementById('acp-last-updated');

    function escHtml(value) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(String(value || '')));
        return d.innerHTML;
    }

    function renderHealth(health) {
        if (!healthWrap) return;
        if (!health || typeof health !== 'object') {
            healthWrap.style.display = 'none';
            healthWrap.innerHTML = '';
            return;
        }
        var status = String(health.status || 'info');
        var icon = 'fa-circle-info';
        if (status === 'ok') icon = 'fa-circle-check';
        if (status === 'warning') icon = 'fa-triangle-exclamation';
        if (status === 'error') icon = 'fa-circle-xmark';

        var html = '';
        html += '<div class="ari-ap-status ari-ap-status--' + escHtml(status)
            + '">';
        html += '<div class="ari-ap-status__headline">';
        html += '<i class="fa-solid ' + escHtml(icon) + '"></i> ';
        html += escHtml(health.message || '');
        html += '</div>';
        var details = health.details;
        if (Array.isArray(details) && details.length) {
            html += '<ul class="ari-ap-status__details" '
                + 'style="margin-top:0.35rem;">';
            details.forEach(function (item) {
                html += '<li>' + escHtml(item) + '</li>';
            });
            html += '</ul>';
        }
        html += '</div>';
        healthWrap.innerHTML = html;
        healthWrap.style.display = '';
    }

    function checkInfoUrl(checkKey) {
        var sep = checkInfoBaseUrl.indexOf('?') === -1 ? '?' : '&';
        return checkInfoBaseUrl + sep
            + 'check=' + encodeURIComponent(String(checkKey || ''));
    }

    function renderCatalog(cards) {
        if (!catalogWrap) return;
        catalogWrap.innerHTML = '';
        if (!Array.isArray(cards) || !cards.length) {
            catalogWrap.innerHTML = '<span class="acp-note">'
                + 'No checks found.'
                + '</span>';
            return;
        }

        var instruments = [];
        cards.forEach(function (item) {
            var insts = Array.isArray(item.instruments)
                ? item.instruments : [];
            insts.forEach(function (inst) {
                var text = String(inst || '').trim();
                if (!text) return;
                if (instruments.indexOf(text) === -1) {
                    instruments.push(text);
                }
            });
        });
        instruments.sort();
        if (catalogFilter) {
            catalogFilter.innerHTML = '<option value="all">'
                + 'All instruments</option>';
            instruments.forEach(function (inst) {
                var opt = document.createElement('option');
                opt.value = inst;
                opt.textContent = inst;
                catalogFilter.appendChild(opt);
            });
            catalogFilter.disabled = false;
        }

        var html = '';
        cards.forEach(function (item) {
            var classes = [
                'acp-card',
                'acp-check-card',
                'acp-check-card--' + escHtml(item.dominant_state || 'neutral'),
                'acp-check-card--' + escHtml(item.check_type || 'all'),
            ];
            if (item.is_ignored) {
                classes.push('acp-check-card--ignored');
            }
            html += '<a class="' + classes.join(' ') + '"';
            html += ' href="' + escHtml(checkInfoUrl(item.check_key)) + '"';
            html += ' data-acp-check="' + escHtml(item.check_key) + '"';
            html += ' data-acp-instruments="'
                + escHtml((item.instruments || []).join(',')) + '"';
            html += ' data-acp-state="'
                + escHtml(item.dominant_state || '') + '"';
            html += ' data-acp-ignored="'
                + (item.is_ignored ? 'true' : 'false') + '"';
            html += ' data-acp-override="'
                + (item.override_allowed ? 'true' : 'false') + '"';
            html += ' title="' + escHtml(item.check_name) + '">';
            html += '<div>';
            html += '<div class="acp-card__title acp-card__title--singleline">';
            html += escHtml(item.check_name || '');
            if (item.has_missing_metadata) {
                html += ' <i class="fa-solid fa-triangle-exclamation '
                    + 'acp-missing-icon" '
                    + 'title="Missing documentation metadata"></i>';
            }
            html += '</div>';
            html += '<div class="acp-card__subtitle">'
                + escHtml(item.check_human_name || '') + '</div>';
            html += '</div>';
            html += '<div class="acp-card__meta" style="align-items:flex-end;">';
            if (item.override_allowed) {
                html += '<span class="acp-chip acp-chip--override-allowed">'
                    + 'Override allowed</span>';
            }
            if (item.is_ignored) {
                html += '<span class="acp-chip acp-chip--ignored">Ignored</span>';
            }
            var total = ((item.counts || {}).total || 0);
            html += '<span class="acp-chip">Total: ' + escHtml(total) + '</span>';
            html += '</div>';
            html += '</a>';
        });
        catalogWrap.innerHTML = html;
    }

    function renderProfileSummaries(rows) {
        if (!summaryWrap) return;
        summaryWrap.innerHTML = '';
        if (!Array.isArray(rows) || !rows.length) {
            summaryWrap.innerHTML = '<span class="acp-note">'
                + 'No profiles found.'
                + '</span>';
            return;
        }

        var html = '';
        rows.forEach(function (row) {
            var counts = row.counts || {};
            html += '<details>';
            html += '<summary>';
            html += '<span><strong>Summary ' + escHtml(row.profile_id)
                + '</strong> <span class="acp-note">('
                + escHtml(row.instrument) + ')</span></span>';
            html += '<span class="acp-note">'
                + escHtml(counts.total || 0) + ' nights</span>';
            html += '</summary>';
            html += '<div class="acp-summary__counts">';
            html += '<span class="acp-chip acp-chip--passed">Passed: '
                + escHtml(counts.passed || 0) + '</span>';
            html += '<span class="acp-chip acp-chip--overridden">'
                + 'Overridden: ' + escHtml(counts.overridden || 0) + '</span>';
            html += '<span class="acp-chip acp-chip--monitored">'
                + 'Monitored: ' + escHtml(counts.monitored || 0) + '</span>';
            html += '<span class="acp-chip acp-chip--mixed">'
                + 'Overridden and monitored: '
                + escHtml(counts.mixed || 0) + '</span>';
            html += '<span class="acp-chip acp-chip--failed">'
                + 'Failed: ' + escHtml(counts.failed || 0) + '</span>';
            html += '</div>';
            html += '<div class="acp-summary__body">Checks root: '
                + escHtml(row.checks_root || '') + '</div>';
            html += '</details>';
        });
        summaryWrap.innerHTML = html;
    }

    function applyCatalogFilter() {
        var selected;
        var cards;
        if (!catalogWrap || !catalogFilter) {
            return;
        }
        selected = String(catalogFilter.value || 'all').trim();
        cards = catalogWrap.querySelectorAll('[data-acp-check]');
        cards.forEach(function (card) {
            var raw;
            var instruments;
            if (selected === 'all') {
                card.style.display = '';
                return;
            }
            raw = String(card.getAttribute('data-acp-instruments') || '');
            instruments = raw.split(',').filter(Boolean);
            if (instruments.indexOf(selected) >= 0) {
                card.style.display = '';
                return;
            }
            card.style.display = 'none';
        });
    }

    function setLoading(text) {
        if (catalogLoading) {
            catalogLoading.textContent = text;
            catalogLoading.style.display = '';
        }
        if (summaryLoading) {
            summaryLoading.textContent = text;
            summaryLoading.style.display = '';
        }
    }

    function hideLoading() {
        if (catalogLoading) {
            catalogLoading.style.display = 'none';
        }
        if (summaryLoading) {
            summaryLoading.style.display = 'none';
        }
    }

    function loadSections() {
        if (!sectionsApiUrl) {
            setLoading('Failed to load section.');
            return;
        }
        setLoading('Loading section...');
        fetch(sectionsApiUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    setLoading(data.error || 'Failed to load section.');
                    return;
                }
                renderHealth(data.checks_health || null);
                renderCatalog(data.checks_catalog || []);
                renderProfileSummaries(data.profile_summaries || []);
                if (updatedEl) {
                    updatedEl.textContent = String(
                        data.policy_last_updated || 'n/a'
                    );
                }
                hideLoading();
                applyCatalogFilter();
            })
            .catch(function () {
                setLoading('Failed to load section.');
            });
    }

    if (catalogFilter) {
        catalogFilter.addEventListener('change', applyCatalogFilter);
    }

    loadSections();
}());