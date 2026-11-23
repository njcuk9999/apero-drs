/* Data access request modal for User Portal / Data Access */
(function () {
    'use strict';

    if (window.__ARI_USER_DATA_ACCESS_INIT__) {
        return;
    }
    window.__ARI_USER_DATA_ACCESS_INIT__ = true;

    function init() {
        var cfg = window.ARI_USER_DATA_ACCESS || {};
        var submitInFlight = false;

        var link = document.getElementById('up-request-access-link');
        var modal = document.getElementById('up-access-request-modal');
        var instrument = document.getElementById('up-request-instrument');
        var runids = document.getElementById('up-request-runids');
        var addRunId = document.getElementById('up-request-add-runid');
        var reason = document.getElementById('up-request-reason');
        var sciGroup = document.getElementById('up-request-sci-group');
        var feedback = document.getElementById('up-request-feedback');
        var cancel = document.getElementById('up-request-cancel');
        var submit = document.getElementById('up-request-submit');

        if (!link || !modal || !instrument || !runids || !reason || !sciGroup) {
            return;
        }

        function setFeedback(message, isError) {
            if (!feedback) {
                return;
            }
            feedback.textContent = message || '';
            feedback.style.color = isError ? 'var(--ari-danger)' : '';
        }

        function addRunIdCard(value) {
            var card = document.createElement('div');
            card.className = 'ari-up-request-runid-card';

            var input = document.createElement('input');
            input.type = 'text';
            input.className = 'ari-user-search__input';
            input.placeholder = 'e.g. 111.24ZU.001';
            input.value = value || '';

            var remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'ari-btn ari-btn--danger';
            remove.innerHTML = '<i class="fa-solid fa-trash"></i>';
            remove.title = 'Remove run ID';
            remove.addEventListener('click', function () {
                card.remove();
                if (!runids.children.length) {
                    addRunIdCard('');
                }
            });

            card.appendChild(input);
            card.appendChild(remove);
            runids.appendChild(card);
        }

        function collectRunIds() {
            var out = [];
            var seen = {};
            var inputs = runids.querySelectorAll('input');
            inputs.forEach(function (input) {
                var value = String(input.value || '').trim();
                if (!value) {
                    return;
                }
                if (!seen[value]) {
                    seen[value] = true;
                    out.push(value);
                }
            });
            return out;
        }

        function populateScienceGroups() {
            var map = cfg.scienceGroupsByInstrument || {};
            var groups = map[instrument.value] || [];
            sciGroup.innerHTML = '';

            var na = document.createElement('option');
            na.value = 'N/A';
            na.textContent = 'N/A';
            sciGroup.appendChild(na);

            groups.forEach(function (groupName) {
                var opt = document.createElement('option');
                opt.value = groupName;
                opt.textContent = groupName;
                sciGroup.appendChild(opt);
            });
        }

        function resetForm() {
            runids.innerHTML = '';
            addRunIdCard('');
            reason.value = '';
            populateScienceGroups();
            sciGroup.value = 'N/A';
            submit.disabled = false;
            setFeedback('', false);
        }

        function openModal() {
            modal.style.display = 'flex';
            resetForm();
        }

        function closeModal() {
            modal.style.display = 'none';
            setFeedback('', false);
        }

        async function submitRequest() {
            if (submitInFlight) {
                return;
            }
            setFeedback('', false);
            if (!cfg.requestUrl) {
                setFeedback('Request endpoint is not configured.', true);
                return;
            }

            var runIdValues = collectRunIds();
            if (!runIdValues.length) {
                setFeedback('Please add at least one run ID.', true);
                return;
            }
            var reasonValue = String(reason.value || '').trim();
            if (!reasonValue) {
                setFeedback('Please provide a reason.', true);
                return;
            }
            if (reasonValue.length > 80) {
                setFeedback('Reason must be 80 characters or fewer.', true);
                return;
            }

            submitInFlight = true;
            submit.disabled = true;
            try {
                var resp = await fetch(cfg.requestUrl, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        instrument: instrument.value,
                        run_ids: runIdValues,
                        reason: reasonValue,
                        suggested_science_group: sciGroup.value || 'N/A'
                    })
                });
                var data = await resp.json();
                if (!resp.ok || !data.success) {
                    setFeedback(data.error || 'Failed to submit request.', true);
                    return;
                }
                setFeedback('Request submitted as issue #' + data.issue.id + '.', false);
                window.setTimeout(closeModal, 900);
            } catch (err) {
                setFeedback('Failed to submit request: ' + err.message, true);
            } finally {
                submitInFlight = false;
                submit.disabled = false;
            }
        }

        link.addEventListener('click', function (event) {
            event.preventDefault();
            openModal();
        });

        addRunId.addEventListener('click', function () {
            addRunIdCard('');
        });

        instrument.addEventListener('change', populateScienceGroups);

        cancel.addEventListener('click', closeModal);
        submit.addEventListener('click', submitRequest);

        modal.addEventListener('click', function (event) {
            if (event.target === modal) {
                closeModal();
            }
        });
    }

    document.addEventListener('DOMContentLoaded', init);
})();
