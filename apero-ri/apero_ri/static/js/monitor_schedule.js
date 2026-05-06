(function () {
    'use strict';

    const state = {
        instrument: '',
        taskInstrument: '',
        instruments: [],
        tasks: [],
        taskOverlayRows: [],
        users: [],
        currentUsername: '',
        canManage: false,
        statsVisibility: {},
        weekStart: '',
        weekStartDay: 0,
        statsRows: [],
        entryRows: [],
        entrySortDesc: true,
        entryPageSize: 10,
        entryPage: 1,
        calendarWeeks: 13,
        assignmentFilter: 'all',
        showNoHours: false,
        savingEntry: false
    };

    function el(id) {
        return document.getElementById(id);
    }

    function setStatus(text, isError) {
        const node = el('ms-status');
        if (!node) {
            return;
        }
        node.textContent = text || '';
        node.style.color = isError ? '#a61b1b' : '';
    }

    async function apiGet(path, params) {
        const usp = new URLSearchParams(params || {});
        const url = path + (usp.toString() ? ('?' + usp.toString()) : '');
        const rsp = await fetch(url, { credentials: 'same-origin' });
        const out = await rsp.json();
        if (!rsp.ok || !out.success) {
            throw new Error(out.error || ('HTTP ' + rsp.status));
        }
        return out;
    }

    async function apiPost(path, payload) {
        const rsp = await fetch(path, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload || {})
        });
        const out = await rsp.json();
        if (!rsp.ok || !out.success) {
            throw new Error(out.error || ('HTTP ' + rsp.status));
        }
        return out;
    }

    function mondayOf(dateStr) {
        const d = new Date(dateStr + 'T00:00:00');
        if (Number.isNaN(d.getTime())) {
            return '';
        }
        const day = d.getDay();
        const shift = (day + 6) % 7;
        d.setDate(d.getDate() - shift);
        return d.toISOString().slice(0, 10);
    }

    function shiftDate(dateStr, days) {
        const d = new Date(dateStr + 'T00:00:00');
        if (Number.isNaN(d.getTime())) {
            return '';
        }
        d.setDate(d.getDate() + days);
        return d.toISOString().slice(0, 10);
    }

    const _CHIP_CLASSES = [
        'ms-chip-p0', 'ms-chip-p1', 'ms-chip-p2',
        'ms-chip-p3', 'ms-chip-p4'
    ];

    function taskColorClass(taskName) {
        if (!taskName) {
            return _CHIP_CLASSES[0];
        }
        let h = 0;
        for (let i = 0; i < taskName.length; i++) {
            h = (h * 31 + taskName.charCodeAt(i)) & 0x7fffffff;
        }
        return _CHIP_CLASSES[h % _CHIP_CLASSES.length];
    }

    function firstOfMonth(dateStr) {
        const d = new Date(dateStr + 'T00:00:00');
        if (Number.isNaN(d.getTime())) {
            return '';
        }
        d.setDate(1);
        return d.toISOString().slice(0, 10);
    }

    function dateNum(dateStr) {
        const d = new Date(String(dateStr || '') + 'T00:00:00');
        const v = d.getTime();
        return Number.isNaN(v) ? 0 : v;
    }

    function sortEntries(rows) {
        const out = rows.slice();
        out.sort((a, b) => {
            const da = dateNum(a.date_start);
            const db = dateNum(b.date_start);
            const sign = state.entrySortDesc ? -1 : 1;
            if (da !== db) {
                return sign * (da - db);
            }
            const ia = Number(a.id || 0);
            const ib = Number(b.id || 0);
            return sign * (ia - ib);
        });
        return out;
    }

    function updateTaskSelect(selectId, includeAny) {
        const node = el(selectId);
        if (!node) {
            return;
        }
        const previous = node.value;
        const parts = [];
        if (includeAny) {
            parts.push('<option value="">Any task</option>');
        }
        for (const row of state.tasks) {
            if (row.active || includeAny) {
                const name = String(row.name || '');
                parts.push(
                    '<option value="' + name + '">' + name + '</option>'
                );
            }
        }
        node.innerHTML = parts.join('');
        if (previous) {
            node.value = previous;
        }
    }

    function updateUserSelect() {
        const node = el('ms-add-username');
        if (!node) {
            return;
        }
        const filterNode = el('ms-add-user-filter');
        const filterText = String(
            (filterNode && filterNode.value) || ''
        ).toLowerCase().trim();
        const prev = node.value;
        const parts = [];
        for (const row of state.users) {
            const username = String(row.username || '');
            const who = String(row.who || username);
            const hay = (username + ' ' + who).toLowerCase();
            if (filterText && hay.indexOf(filterText) === -1) {
                continue;
            }
            parts.push(
                '<option value="' + username + '">' +
                username + ' - ' + who +
                '</option>'
            );
        }
        node.innerHTML = parts.join('');
        if (prev && node.querySelector('option[value="' + prev + '"]')) {
            node.value = prev;
        }
        if (!node.value && state.currentUsername) {
            const selector = 'option[value="' + state.currentUsername + '"]';
            const currentOpt = node.querySelector(selector);
            if (currentOpt) {
                node.value = state.currentUsername;
            }
        }
        if (!node.value && state.users.length > 0) {
            const first = node.querySelector('option');
            if (first) {
                node.value = first.value;
            }
        }
        applyWhoFromUser();
    }

    function applyWhoFromUser() {
        const userNode = el('ms-add-username');
        const whoNode = el('ms-add-who');
        if (!userNode || !whoNode) {
            return;
        }
        const username = userNode.value;
        const found = state.users.find((r) => r.username === username);
        if (found) {
            whoNode.value = found.who || username;
        }
    }

    function renderInstrumentTabs() {
        const holder = el('ms-instruments');
        if (!holder) {
            return;
        }
        const html = state.instruments.map((inst) => {
            const c = inst === state.instrument ? 'ms-active' : '';
            return (
                '<button type="button" data-inst="' + inst +
                '" class="' + c + '">' + inst + '</button>'
            );
        }).join('');
        holder.innerHTML = html;
        for (const btn of holder.querySelectorAll('button[data-inst]')) {
            btn.addEventListener('click', async () => {
                const next = String(btn.dataset.inst || '');
                if (!next || next === state.instrument) {
                    return;
                }
                state.instrument = next;
                await loadMeta(true);
            });
        }
    }

    function updateTaskInstrumentSelect() {
        const node = el('ms-task-instrument');
        if (!node) {
            return;
        }
        const previous = state.taskInstrument || state.instrument;
        const html = state.instruments.map((inst) => {
            return '<option value="' + inst + '">' + inst + '</option>';
        }).join('');
        node.innerHTML = html;
        if (previous && node.querySelector('option[value="' + previous + '"]')) {
            node.value = previous;
        }
        if (!node.value && state.instruments.length > 0) {
            node.value = state.instruments[0];
        }
        state.taskInstrument = node.value || state.instrument;
    }

    async function loadTaskMeta(instrument) {
        const rsp = await apiGet('/api/monitor-schedule/meta', {
            instrument: instrument
        });
        state.taskInstrument = rsp.instrument || instrument || state.instrument;
        state.taskOverlayRows = rsp.tasks || [];
    }

    function setupSubtabs() {
        const buttons = document.querySelectorAll('.ms-subtab');
        for (const btn of buttons) {
            btn.addEventListener('click', () => {
                const tab = String(btn.dataset.msTab || 'entry');
                activatePane(tab);
            });
        }
    }

    function activatePane(name) {
        for (const btn of document.querySelectorAll('.ms-subtab')) {
            const active = String(btn.dataset.msTab || '') === name;
            btn.classList.toggle('ms-subtab--active', active);
        }
        for (const pane of document.querySelectorAll('.ms-pane')) {
            const active = String(pane.dataset.msPane || '') === name;
            pane.classList.toggle('ms-pane--active', active);
        }
        if (name === 'calendar') {
            loadCalendar().catch((err) => setStatus(err.message, true));
        }
        if (name === 'stats' || name === 'graphs') {
            loadStats().catch((err) => setStatus(err.message, true));
        }
    }

    async function loadMeta(fullRefresh) {
        setStatus('Loading schedule metadata...');
        const rsp = await apiGet('/api/monitor-schedule/meta', {
            instrument: state.instrument
        });
        state.instruments = rsp.instruments || [];
        state.instrument = rsp.instrument || state.instruments[0] || '';
        state.taskInstrument = state.instrument;
        state.tasks = rsp.tasks || [];
        state.taskOverlayRows = state.tasks.slice();
        state.users = rsp.users || [];
        state.currentUsername = String(rsp.current_username || '');
        state.statsVisibility = rsp.stats_visibility || {};
        state.canManage = !!rsp.can_manage;
        state.weekStartDay = Number(rsp.week_start_day || 0);

        renderInstrumentTabs();
        updateTaskInstrumentSelect();
        updateTaskSelect('ms-add-task', false);
        updateTaskSelect('ms-stats-task', true);
        updateUserSelect();

        const manageTasksBtn = el('ms-manage-tasks');
        const manageUsersBtn = el('ms-stats-manage-users');
        const bulkAddBtn = el('ms-bulk-add-btn');
        if (manageTasksBtn) {
            manageTasksBtn.hidden = !state.canManage;
        }
        if (manageUsersBtn) {
            manageUsersBtn.hidden = !state.canManage;
        }
        if (bulkAddBtn) {
            bulkAddBtn.hidden = !state.canManage;
        }

        if (fullRefresh) {
            await Promise.all([
                loadEntries(true),
                loadCalendar(),
                loadStats()
            ]);
        } else {
            await loadEntries(false);
        }
        setStatus('');
    }

    function currentEntryFilters() {
        const out = { instrument: state.instrument };
        for (const inp of document.querySelectorAll('.ms-filter-row input[data-f]')) {
            const key = String(inp.dataset.f || '');
            out[key] = inp.value || '';
        }
        return out;
    }

    function dateLinkCell(dateStr) {
        if (!dateStr) {
            return '';
        }
        return (
            '<button type="button" class="ms-link" data-date="' +
            dateStr + '">' + dateStr + '</button>'
        );
    }

    function renderEntryPage() {
        const body = el('ms-entry-tbody');
        if (!body) {
            return;
        }
        let rows = sortEntries(state.entryRows || []);

        // Apply entry filters (combinable)
        if (state.assignmentFilter === 'assigned') {
            rows = rows.filter((r) => Boolean(r.username));
        } else if (state.assignmentFilter === 'unassigned') {
            rows = rows.filter((r) => !r.username);
        }
        if (state.showNoHours) {
            rows = rows.filter(
                (r) => Number(r.hours || 0) === 0
            );
        }

        const pageSize = Math.max(
            1, Number(state.entryPageSize || 10)
        );
        const totalRows = rows.length;
        const totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
        if (state.entryPage > totalPages) {
            state.entryPage = totalPages;
        }
        if (state.entryPage < 1) {
            state.entryPage = 1;
        }
        const startIdx = (state.entryPage - 1) * pageSize;
        const pageRows = rows.slice(startIdx, startIdx + pageSize);

        const addRow = (
            '<tr class="ms-add-row">' +
            '<td colspan="8">' +
            '<button id="ms-open-add-overlay" class="ari-btn" ' +
            'type="button">Add entry</button>' +
            '</td></tr>'
        );

        const TODAY = new Date().toISOString().slice(0, 10);

        const rowsHtml = pageRows.map((row) => {
            const actionBtns = (
                '<div class="ms-inline-btns">' +
                '<button type="button" class="ari-btn" '
                + 'data-edit-entry="' + row.id + '">Edit</button>' +
                '<button type="button" class="ari-btn ari-btn--alt" '
                + 'data-delete-entry="' + row.id + '">Delete</button>' +
                '</div>'
            );
            const unassigned = !row.username;
            // Temporal colour class
            let tClass = '';
            const ds = String(row.date_start || '');
            const de = String(row.date_end || '');
            if (de && de < TODAY) {
                tClass = 'ms-row--past';
            } else if (ds && ds > TODAY) {
                tClass = 'ms-row--future';
            } else {
                tClass = 'ms-row--current';
            }
            const classes = [tClass, unassigned
                ? 'ms-row--unassigned' : '']
                .filter(Boolean).join(' ');
            return (
                '<tr class="' + classes + '">' +
                '<td>' + (row.task || '') + '</td>' +
                '<td>' + (row.username || '<em>unassigned</em>') +
                '</td>' +
                '<td>' + (row.who || '') + '</td>' +
                '<td>' + dateLinkCell(row.date_start) + '</td>' +
                '<td>' + dateLinkCell(row.date_end) + '</td>' +
                '<td>' + (row.hours || 0) + '</td>' +
                '<td>' + (row.comment || '') + '</td>' +
                '<td>' + actionBtns + '</td>' +
                '</tr>'
            );
        }).join('');
        body.innerHTML = addRow + rowsHtml;

        for (const btn of body.querySelectorAll('button[data-date]')) {
            btn.addEventListener('click', () => {
                state.weekStart = mondayOf(String(btn.dataset.date || ''));
                activatePane('calendar');
            });
        }

        for (const btn of body.querySelectorAll('button[data-edit-entry]')) {
            btn.addEventListener('click', async () => {
                const entryId = Number(btn.dataset.editEntry || '0');
                const found = (state.entryRows || []).find((row) => {
                    return Number(row.id || 0) === entryId;
                });
                if (!found) {
                    return;
                }
                el('ms-add-entry-id').value = String(found.id || '');
                el('ms-add-task').value = String(found.task || '');
                el('ms-add-username').value = String(found.username || '');
                applyWhoFromUser();
                el('ms-add-date-start').value = String(found.date_start || '');
                el('ms-add-date-end').value = String(found.date_end || '');
                el('ms-add-hours').value = String(found.hours || 0);
                el('ms-add-comment').value = String(found.comment || '');
                el('ms-add-title').textContent = 'Edit entry';
                el('ms-add-submit').textContent = 'Update entry';
                overlay('add', true);
            });
        }

        for (const btn of body.querySelectorAll('button[data-delete-entry]')) {
            btn.addEventListener('click', async () => {
                const entryId = Number(btn.dataset.deleteEntry || '0');
                if (!window.confirm('Delete this entry?')) {
                    return;
                }
                try {
                    await apiPost('/api/monitor-schedule/entries/delete', {
                        instrument: state.instrument,
                        entry_id: entryId
                    });
                    setStatus('Entry deleted.');
                    await Promise.all([
                        loadEntries(true),
                        loadCalendar(),
                        loadStats()
                    ]);
                } catch (err) {
                    setStatus(err.message, true);
                }
            });
        }

        const addBtn = el('ms-open-add-overlay');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                resetAddForm();
                overlay('add', true);
            });
        }

        const sortIcon = el('ms-sort-date-start-icon');
        if (sortIcon) {
            sortIcon.textContent = state.entrySortDesc ? '▼' : '▲';
        }

        const info = el('ms-entry-page-info');
        if (info) {
            const first = totalRows === 0 ? 0 : startIdx + 1;
            const last = Math.min(startIdx + pageRows.length, totalRows);
            info.textContent = (
                'Page ' + state.entryPage + ' / ' + totalPages +
                ' (' + first + '-' + last + ' of ' + totalRows + ')'
            );
        }

        const prev = el('ms-entry-prev');
        const next = el('ms-entry-next');
        if (prev) {
            prev.disabled = state.entryPage <= 1;
        }
        if (next) {
            next.disabled = state.entryPage >= totalPages;
        }
    }

    async function loadEntries(resetPage) {
        const rsp = await apiGet(
            '/api/monitor-schedule/entries/list',
            currentEntryFilters()
        );
        state.entryRows = rsp.rows || [];
        if (resetPage) {
            state.entryPage = 1;
        }
        renderEntryPage();
    }

    async function onAddEntry(evt) {
        evt.preventDefault();
        if (state.savingEntry) {
            return;
        }
        state.savingEntry = true;
        const submitBtn = el('ms-add-submit');
        if (submitBtn) {
            submitBtn.disabled = true;
        }
        const entryIdText = String(el('ms-add-entry-id').value || '').trim();
        const editing = entryIdText.length > 0;
        const payload = {
            instrument: state.instrument,
            task: el('ms-add-task').value,
            username: el('ms-add-username').value,
            who: el('ms-add-who').value,
            date_start: el('ms-add-date-start').value,
            date_end: el('ms-add-date-end').value,
            hours: Number(el('ms-add-hours').value || '0'),
            comment: el('ms-add-comment').value,
            link_user_calendar: true
        };
        if (editing) {
            payload.entry_id = Number(entryIdText);
        }
        try {
            const path = editing
                ? '/api/monitor-schedule/entries/edit'
                : '/api/monitor-schedule/entries/add';
            await apiPost(path, payload);
            overlay('add', false);
            if (editing) {
                setStatus('Entry updated successfully.');
            } else {
                setStatus('Entry added successfully.');
            }
            await Promise.all([
                loadEntries(true),
                loadCalendar(),
                loadStats()
            ]);
            resetAddForm();
        } catch (err) {
            setStatus(err.message, true);
        } finally {
            state.savingEntry = false;
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        }
    }

    function resetAddForm() {
        el('ms-add-entry-id').value = '';
        el('ms-add-title').textContent = 'Add new entry';
        el('ms-add-submit').textContent = 'Save entry';
        el('ms-add-date-start').value = '';
        el('ms-add-date-end').value = '';
        el('ms-add-hours').value = '0';
        el('ms-add-comment').value = '';
        applyWhoFromUser();
    }

    async function loadCalendar() {
        if (!state.weekStart) {
            const today = new Date().toISOString().slice(0, 10);
            state.weekStart = today;
        }
        const rsp = await apiGet(
            '/api/monitor-schedule/calendar/weeks', {
                instrument: state.instrument,
                week_start: state.weekStart,
                weeks: state.calendarWeeks
            }
        );
        const payload = rsp.payload || {};
        state.weekStart = payload.week_start || state.weekStart;
        const targetStart = payload.target_start || '';
        const targetEnd = payload.target_end || '';
        const label = el('ms-week-label');
        if (label) {
            label.textContent = (
                targetStart + ' to ' + targetEnd +
                ' (' + state.calendarWeeks + ' weeks)'
            );
        }

        const grid = el('ms-calendar-grid');
        if (!grid) {
            return;
        }

        const weeks = Array.isArray(payload.weeks)
            ? payload.weeks
            : [];
        const dayHeaders = Array.isArray(payload.day_headers)
            ? payload.day_headers
            : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

        let html = '<table class="ms-cal-table">';
        html += '<thead><tr>';
        html += '<th class="ms-cal-week-th">Week start</th>';
        for (const h of dayHeaders) {
            html += '<th class="ms-cal-day-th">' + h + '</th>';
        }
        html += '</tr></thead><tbody>';

        for (const wk of weeks) {
            const rowClass = wk.overlap_months
                ? 'ms-cal-row ms-cal-row--overlap'
                : 'ms-cal-row';
            html += '<tr class="' + rowClass + '">';
            html += (
                '<td class="ms-cal-week-cell">' +
                String(wk.week_start || '') +
                '</td>'
            );

            const days = Array.isArray(wk.days) ? wk.days : [];
            for (const day of days) {
                const dayEntries = Array.isArray(day.entries)
                    ? day.entries
                    : [];
                const seenIds = {};
                let chips = '';
                for (const entry of dayEntries) {
                    if (!entry.username) {
                        // Calendar shows assigned entries only.
                        continue;
                    }
                    const eid = String(entry.id || '');
                    if (seenIds[eid]) {
                        continue;
                    }
                    seenIds[eid] = true;
                    const cc = taskColorClass(entry.task);
                    const label2 = entry.task || '';
                    const person = (
                        entry.who || entry.username || ''
                    );
                    chips += (
                        '<span class="ms-entry-chip ' + cc +
                        '" title="' + label2 +
                        (person ? ': ' + person : '') + '">' +
                        label2 +
                        (person ? '<br><small>' + person +
                        '</small>' : '') +
                        '</span>'
                    );
                }
                html += (
                    '<td class="ms-cal-day-cell">' +
                    chips + '</td>'
                );
            }
            html += '</tr>';
        }
        html += '</tbody></table>';
        grid.innerHTML = html;
    }

    function statsParams() {
        return {
            instrument: state.instrument,
            since: el('ms-stats-since').value,
            until: el('ms-stats-until').value,
            task: el('ms-stats-task').value
        };
    }

    function renderStatsSummary(summary) {
        const hd = Number(summary.avg_hours_per_completed_day || 0);
        const hw = Number(summary.avg_hours_per_completed_week || 0);
        el('ms-kpi-hd').textContent = hd.toFixed(2);
        el('ms-kpi-hw').textContent = hw.toFixed(2);
    }

    function renderStatsRows(rows) {
        const body = el('ms-stats-tbody');
        if (!body) {
            return;
        }
        const html = rows.map((row) => (
            '<tr>' +
            '<td>' + (row.username || '') + '</td>' +
            '<td>' + (row.who || '') + '</td>' +
            '<td>' + Number(row.days_completed || 0).toFixed(2) + '</td>' +
            '<td>' + Number(row.days_proposed || 0).toFixed(2) + '</td>' +
            '<td>' + Number(row.total_days || 0).toFixed(2) + '</td>' +
            '<td>' + Number(row.hours_estimated || 0).toFixed(2) + '</td>' +
            '</tr>'
        )).join('');
        body.innerHTML = html;
    }

    function renderGraphs(rows) {
        const names = rows.map((r) => r.who || r.username || '');
        const days = rows.map((r) => Number(r.total_days || 0));
        const hours = rows.map((r) => Number(r.hours_estimated || 0));

        const hasPlotly = typeof window.Plotly !== 'undefined';
        if (!hasPlotly) {
            el('ms-graph-days').textContent = 'Plotly unavailable.';
            el('ms-graph-hours').textContent = 'Plotly unavailable.';
            return;
        }

        window.Plotly.newPlot('ms-graph-days', [{
            type: 'bar',
            x: names,
            y: days,
            marker: { color: '#2f7d32' },
            hovertemplate: '%{x}<br>%{y:.2f} days<extra></extra>'
        }], {
            margin: { t: 15, r: 10, b: 90, l: 50 },
            yaxis: { title: 'Total days' }
        }, { responsive: true });

        window.Plotly.newPlot('ms-graph-hours', [{
            type: 'bar',
            x: names,
            y: hours,
            marker: { color: '#0f766e' },
            hovertemplate: '%{x}<br>%{y:.2f} hours<extra></extra>'
        }], {
            margin: { t: 15, r: 10, b: 90, l: 50 },
            yaxis: { title: 'Hours' }
        }, { responsive: true });
    }

    async function loadStats() {
        const rsp = await apiGet('/api/monitor-schedule/stats', statsParams());
        state.statsRows = rsp.rows || [];
        state.statsVisibility = rsp.stats_visibility || state.statsVisibility;
        renderStatsSummary(rsp.summary || {});
        renderStatsRows(state.statsRows);
        renderGraphs(state.statsRows);
    }

    function renderTaskOverlay() {
        const scope = el('ms-task-scope-label');
        if (scope) {
            scope.textContent = (
                'Managing tasks for instrument: ' +
                (state.taskInstrument || state.instrument)
            );
        }
        // Sync week-start-day selector to current setting
        const wsdNode = el('ms-week-start-day');
        if (wsdNode) {
            wsdNode.value = String(state.weekStartDay);
        }
        const list = el('ms-task-list');
        if (!list) {
            return;
        }
        const html = state.taskOverlayRows.map((row) => {
            const status = row.active ? 'Active' : 'Inactive';
            const togLabel = row.active ? 'Deactivate' : 'Activate';
            return (
                '<div class="ms-card-row">' +
                '<div><strong>' + row.name + '</strong><br>' +
                (row.description || '') + ' (' + status + ')</div>' +
                '<div class="ms-inline-btns">' +
                '<button class="ari-btn" type="button" data-task-rename="' +
                row.name + '">Rename</button>' +
                '<button class="ari-btn" type="button" data-task-toggle="' +
                row.name + '" data-task-active="' +
                (row.active ? '1' : '0') + '">' +
                togLabel + '</button>' +
                '</div>' +
                '</div>'
            );
        }).join('');
        list.innerHTML = html;

        for (const btn of list.querySelectorAll('[data-task-rename]')) {
            btn.addEventListener('click', async () => {
                const oldName = String(btn.dataset.taskRename || '');
                const newName = window.prompt('New task name', oldName);
                if (!newName || newName === oldName) {
                    return;
                }
                try {
                    await apiPost('/api/monitor-schedule/tasks/rename', {
                        instrument: state.taskInstrument,
                        old_name: oldName,
                        new_name: newName
                    });
                    await loadTaskMeta(state.taskInstrument);
                    renderTaskOverlay();
                } catch (err) {
                    setStatus(err.message, true);
                }
            });
        }

        for (const btn of list.querySelectorAll('[data-task-toggle]')) {
            btn.addEventListener('click', async () => {
                const name = String(btn.dataset.taskToggle || '');
                const active = btn.dataset.taskActive === '1';
                try {
                    await apiPost('/api/monitor-schedule/tasks/set-active', {
                        instrument: state.taskInstrument,
                        name,
                        active: !active
                    });
                    await loadTaskMeta(state.taskInstrument);
                    renderTaskOverlay();
                } catch (err) {
                    setStatus(err.message, true);
                }
            });
        }
    }

    function renderUserOverlay() {
        const node = el('ms-user-list');
        if (!node) {
            return;
        }
        const html = state.users.map((u) => {
            const username = String(u.username || '');
            const visible = state.statsVisibility[username] !== false;
            return (
                '<div class="ms-card-row">' +
                '<div><strong>' + username + '</strong> - ' +
                (u.who || username) + '</div>' +
                '<div class="ms-inline-btns">' +
                '<button class="ari-btn" type="button" data-vis-user="' +
                username + '" data-visible="' +
                (visible ? '1' : '0') + '">' +
                (visible ? 'Hide' : 'Show') + '</button>' +
                '</div></div>'
            );
        }).join('');
        node.innerHTML = html;

        for (const btn of node.querySelectorAll('[data-vis-user]')) {
            btn.addEventListener('click', async () => {
                const username = String(btn.dataset.visUser || '');
                const vis = btn.dataset.visible === '1';
                try {
                    const rsp = await apiPost(
                        '/api/monitor-schedule/stats/visibility-set',
                        {
                            instrument: state.instrument,
                            username,
                            visible: !vis
                        }
                    );
                    state.statsVisibility = rsp.stats_visibility || {};
                    renderUserOverlay();
                    await loadStats();
                } catch (err) {
                    setStatus(err.message, true);
                }
            });
        }
    }

    function renderBulkOverlay() {
        const node = el('ms-bulk-task-checkboxes');
        if (!node) {
            return;
        }
        const tasks = (state.tasks || []).filter(
            (t) => t.active
        );
        if (tasks.length === 0) {
            node.innerHTML = (
                '<p class="ms-sub">No active tasks.</p>'
            );
            return;
        }
        const html = tasks.map((t) => {
            const name = String(t.name || '');
            const safeId = 'ms-bulk-ck-' + name.replace(
                /[^a-z0-9]/gi, '_'
            );
            return (
                '<label><input type="checkbox" ' +
                'class="ms-bulk-task-ck" ' +
                'id="' + safeId + '" ' +
                'value="' + name.replace(/"/g, '&quot;') +
                '"> ' + name + '</label>'
            );
        }).join('');
        node.innerHTML = html;
    }

    function overlay(name, open) {
        const map = {
            tasks: 'ms-task-overlay',
            users: 'ms-user-overlay',
            add: 'ms-add-overlay',
            bulk: 'ms-bulk-overlay'
        };
        const id = map[name] || 'ms-user-overlay';
        const node = el(id);
        if (!node) {
            return;
        }
        node.hidden = !open;
    }

    function wireEvents() {
        setupSubtabs();

        const addForm = el('ms-add-form');
        if (addForm) {
            addForm.addEventListener('submit', onAddEntry);
        }

        const refresh = el('ms-entry-refresh');
        if (refresh) {
            refresh.addEventListener('click', () => {
                loadEntries(true).catch((err) => setStatus(err.message, true));
            });
        }

        for (const inp of document.querySelectorAll('.ms-filter-row input[data-f]')) {
            inp.addEventListener('change', () => {
                loadEntries(true).catch((err) => setStatus(err.message, true));
            });
        }

        const sortBtn = el('ms-sort-date-start');
        if (sortBtn) {
            sortBtn.addEventListener('click', () => {
                state.entrySortDesc = !state.entrySortDesc;
                renderEntryPage();
            });
        }

        const pageSize = el('ms-entry-page-size');
        if (pageSize) {
            pageSize.addEventListener('change', () => {
                state.entryPageSize = Number(pageSize.value || '10');
                state.entryPage = 1;
                renderEntryPage();
            });
        }

        const prev = el('ms-entry-prev');
        const next = el('ms-entry-next');
        if (prev) {
            prev.addEventListener('click', () => {
                state.entryPage -= 1;
                renderEntryPage();
            });
        }
        if (next) {
            next.addEventListener('click', () => {
                state.entryPage += 1;
                renderEntryPage();
            });
        }

        const addUser = el('ms-add-username');
        if (addUser) {
            addUser.addEventListener('change', applyWhoFromUser);
        }
        const addUserFilter = el('ms-add-user-filter');
        if (addUserFilter) {
            addUserFilter.addEventListener('input', updateUserSelect);
        }

        const wprev = el('ms-week-prev');
        const wnext = el('ms-week-next');
        if (wprev) {
            wprev.addEventListener('click', async () => {
                state.weekStart = shiftDate(
                    state.weekStart,
                    -7 * state.calendarWeeks
                );
                await loadCalendar();
            });
        }
        if (wnext) {
            wnext.addEventListener('click', async () => {
                state.weekStart = shiftDate(
                    state.weekStart,
                    7 * state.calendarWeeks
                );
                await loadCalendar();
            });
        }

        const statsRefresh = el('ms-stats-refresh');
        if (statsRefresh) {
            statsRefresh.addEventListener('click', () => {
                loadStats().catch((err) => setStatus(err.message, true));
            });
        }

        const manageTasks = el('ms-manage-tasks');
        if (manageTasks) {
            manageTasks.addEventListener('click', async () => {
                const node = el('ms-task-instrument');
                state.taskInstrument = state.instrument;
                if (node) {
                    node.value = state.taskInstrument;
                }
                await loadTaskMeta(state.taskInstrument);
                renderTaskOverlay();
                overlay('tasks', true);
            });
        }

        const taskInstrument = el('ms-task-instrument');
        if (taskInstrument) {
            taskInstrument.addEventListener('change', async () => {
                state.taskInstrument = (
                    taskInstrument.value || state.instrument
                );
                await loadTaskMeta(state.taskInstrument);
                renderTaskOverlay();
            });
        }

        // Save week-start-day setting for the instrument
        const wsdSave = el('ms-week-start-save');
        if (wsdSave) {
            wsdSave.addEventListener('click', async () => {
                const wsdNode = el('ms-week-start-day');
                const value = wsdNode ? wsdNode.value : '0';
                try {
                    await apiPost(
                        '/api/monitor-schedule' +
                        '/instrument-settings/set',
                        {
                            instrument: state.taskInstrument,
                            key: 'week_start_day',
                            value
                        }
                    );
                    // Update state so calendar uses new setting
                    if (
                        state.taskInstrument === state.instrument
                    ) {
                        state.weekStartDay = Number(value);
                        state.weekStart = '';
                        await loadCalendar();
                    }
                    setStatus('Week start day saved.');
                } catch (err) {
                    setStatus(err.message, true);
                }
            });
        }

        const manageUsers = el('ms-stats-manage-users');
        if (manageUsers) {
            manageUsers.addEventListener('click', () => {
                renderUserOverlay();
                overlay('users', true);
            });
        }

        for (const closeBtn of document.querySelectorAll(
            '[data-close="tasks"]'
        )) {
            closeBtn.addEventListener(
                'click', () => overlay('tasks', false)
            );
        }
        for (const closeBtn of document.querySelectorAll(
            '[data-close="users"]'
        )) {
            closeBtn.addEventListener(
                'click', () => overlay('users', false)
            );
        }
        for (const closeBtn of document.querySelectorAll(
            '[data-close="add"]'
        )) {
            closeBtn.addEventListener('click', () => {
                overlay('add', false);
                resetAddForm();
            });
        }
        for (const closeBtn of document.querySelectorAll(
            '[data-close="bulk"]'
        )) {
            closeBtn.addEventListener(
                'click', () => overlay('bulk', false)
            );
        }

        // Assignment filter (Show all / assigned / unassigned)
        const assignmentFilter = el('ms-assignment-filter');
        if (assignmentFilter) {
            assignmentFilter.value = state.assignmentFilter || 'all';
            assignmentFilter.addEventListener('change', () => {
                state.assignmentFilter = (
                    assignmentFilter.value || 'all'
                );
                state.entryPage = 1;
                renderEntryPage();
            });
        }

        // Show no hours toggle
        const showNoHBtn = el('ms-show-no-hours');
        if (showNoHBtn) {
            showNoHBtn.addEventListener('click', () => {
                state.showNoHours = !state.showNoHours;
                showNoHBtn.classList.toggle(
                    'ms-active', state.showNoHours
                );
                state.entryPage = 1;
                renderEntryPage();
            });
        }

        // Bulk add entries button
        const bulkAddBtn = el('ms-bulk-add-btn');
        if (bulkAddBtn) {
            bulkAddBtn.addEventListener('click', () => {
                renderBulkOverlay();
                overlay('bulk', true);
            });
        }

        // Bulk submit
        const bulkSubmit = el('ms-bulk-submit');
        if (bulkSubmit) {
            bulkSubmit.addEventListener('click', async () => {
                const checked = document.querySelectorAll(
                    '.ms-bulk-task-ck:checked'
                );
                const tasks = Array.from(checked).map(
                    (cb) => cb.value
                );
                if (tasks.length === 0) {
                    setStatus('Select at least one task.', true);
                    return;
                }
                const dateStart = el(
                    'ms-bulk-date-start'
                ).value;
                if (!dateStart) {
                    setStatus(
                        'Start date is required.',
                        true
                    );
                    return;
                }
                const interval = el(
                    'ms-bulk-interval'
                ).value || 'week';
                const repeats = Math.max(
                    1,
                    Number(
                        el('ms-bulk-repeats').value || '1'
                    )
                );
                try {
                    bulkSubmit.disabled = true;
                    const rsp = await apiPost(
                        '/api/monitor-schedule/entries/bulk-add',
                        {
                            instrument: state.instrument,
                            tasks,
                            date_start: dateStart,
                            repeat_interval: interval,
                            repeats
                        }
                    );
                    overlay('bulk', false);
                    const n = (rsp.rows || []).length;
                    const e = (rsp.errors || []).length;
                    setStatus(
                        n + ' entr' + (n === 1 ? 'y' : 'ies') +
                        ' added' +
                        (e ? ', ' + e + ' error(s).' : '.')
                    );
                    await Promise.all([
                        loadEntries(true),
                        loadCalendar(),
                        loadStats()
                    ]);
                } catch (err) {
                    setStatus(err.message, true);
                } finally {
                    bulkSubmit.disabled = false;
                }
            });
        }

        const taskAdd = el('ms-task-add');
        if (taskAdd) {
            taskAdd.addEventListener('click', async () => {
                const name = el('ms-task-name').value;
                const description = el('ms-task-description').value;
                try {
                    await apiPost(
                        '/api/monitor-schedule/tasks/upsert', {
                            instrument: state.taskInstrument,
                            name,
                            description,
                            active: true
                        }
                    );
                    el('ms-task-name').value = '';
                    el('ms-task-description').value = '';
                    await loadTaskMeta(state.taskInstrument);
                    renderTaskOverlay();
                } catch (err) {
                    setStatus(err.message, true);
                }
            });
        }
    }

    async function bootstrap() {
        const fromServer =
            (window.AperoMonitorSchedule || {}).instruments || [];
        state.instruments = fromServer;
        state.instrument = state.instruments[0] || '';

        wireEvents();

        const pageSize = el('ms-entry-page-size');
        if (pageSize) {
            state.entryPageSize = Number(pageSize.value || '10');
        }

        const today = new Date().toISOString().slice(0, 10);
        const start = today.slice(0, 4) + '-01-01';
        if (el('ms-stats-since')) {
            el('ms-stats-since').value = start;
        }
        if (el('ms-stats-until')) {
            el('ms-stats-until').value = today;
        }

        await loadMeta(true);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            bootstrap().catch((err) => setStatus(err.message, true));
        });
    } else {
        bootstrap().catch((err) => setStatus(err.message, true));
    }
})();
