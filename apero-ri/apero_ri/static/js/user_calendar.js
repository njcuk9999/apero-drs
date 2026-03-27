/* global ARI_CALENDAR, ariPopulateTimezoneSelect, ariConvertEventTime, ariTzShortLabel */
'use strict';

let _events = [];
let _year = new Date().getFullYear();
let _month = new Date().getMonth(); // 0-based
let _editId = null;
let _listPage = 1;
let _listPerPage = 8;
let _userTz = (window.ARI_CALENDAR || {}).userTimezone || 'UTC';

const _MONTH_NAMES = ['January','February','March','April','May','June',
                      'July','August','September','October','November','December'];
const _DAY_NAMES = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

async function _api(url, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    return (await fetch(url, opts)).json();
}

function _toast(msg, ok = true) {
    const el = document.getElementById('cal-toast');
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function _esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function _sortEvents(a, b) {
    const aKey = `${a.date || ''}T${a.time || '00:00'}`;
    const bKey = `${b.date || ''}T${b.time || '00:00'}`;
    if (aKey < bKey) return -1;
    if (aKey > bKey) return 1;
    return String(a.title || '').localeCompare(String(b.title || ''));
}

function _formatEventWhen(ev) {
    if (!ev.date) return '';
    const evTz = ev.timezone || 'UTC';
    // Convert to user's timezone if the event has a time
    if (ev.time && evTz !== _userTz) {
        const conv = ariConvertEventTime(ev.date, ev.time, evTz, _userTz);
        const date = new Date(`${conv.date}T${conv.time || '00:00'}`);
        const dateStr = date.toLocaleDateString(undefined, {
            weekday: 'short', month: 'short', day: 'numeric'
        });
        const tzLabel = ariTzShortLabel(_userTz);
        return `${dateStr}, ${conv.time} ${tzLabel}`;
    }
    const date = new Date(`${ev.date}T${ev.time || '00:00'}`);
    const dateStr = date.toLocaleDateString(undefined, {
        weekday: 'short', month: 'short', day: 'numeric'
    });
    if (ev.time) {
        const tzLabel = ariTzShortLabel(evTz);
        return `${dateStr}, ${ev.time} ${tzLabel}`;
    }
    return dateStr;
}

function _renderEventList(expanded) {
    const listEl = document.getElementById('cal-event-list');
    const subEl = document.getElementById('cal-list-subtitle');
    const infoEl = document.getElementById('cal-list-page-info');
    const prevBtn = document.getElementById('cal-list-prev');
    const nextBtn = document.getElementById('cal-list-next');
    if (!listEl || !subEl || !infoEl || !prevBtn || !nextBtn) return;

    const events = expanded.slice().sort(_sortEvents);
    subEl.textContent = `${events.length} event${events.length === 1 ? '' : 's'} in ${_MONTH_NAMES[_month]} ${_year}`;

    const totalPages = Math.max(1, Math.ceil(events.length / _listPerPage));
    _listPage = Math.min(Math.max(1, _listPage), totalPages);
    const start = (_listPage - 1) * _listPerPage;
    const pageEvents = events.slice(start, start + _listPerPage);

    if (!pageEvents.length) {
        listEl.innerHTML = '<div class="ari-cal-empty-list">No events in this month.</div>';
    } else {
        listEl.innerHTML = pageEvents.map(ev => `
            <article class="ari-cal-event-card" data-id="${_esc(ev.id)}">
                <div class="ari-cal-event-card__head">
                    <div class="ari-cal-event-card__title">${_esc(ev.title || 'Untitled')}</div>
                    <div class="ari-cal-event-card__when">${_esc(_formatEventWhen(ev))}</div>
                </div>
                <div class="ari-cal-event-card__meta">
                    <span class="ari-cal-event-card__badge">${_esc(ev.category || 'event')}</span>
                    ${ev._recurring ? '<span>Recurring</span>' : ''}
                    ${ev._source ? '<span>Instrument event</span>' : ''}
                </div>
                <div class="ari-cal-event-card__actions">
                    ${ev._source ? '' : `
                        <button class="ari-btn ari-btn--secondary ari-btn--sm js-cal-list-edit" data-id="${_esc(ev.id)}">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                        <button class="ari-btn ari-btn--danger ari-btn--sm js-cal-list-delete" data-id="${_esc(ev.id)}">
                            <i class="fa-solid fa-trash"></i> Delete
                        </button>`}
                </div>
            </article>
        `).join('');
    }

    infoEl.textContent = `Page ${_listPage} of ${totalPages}`;
    prevBtn.disabled = _listPage <= 1;
    nextBtn.disabled = _listPage >= totalPages;

    listEl.querySelectorAll('.js-cal-list-edit').forEach(btn => {
        btn.addEventListener('click', () => {
            const ev = _events.find(item => item.id === btn.dataset.id);
            if (ev) _openModal(ev);
        });
    });

    listEl.querySelectorAll('.js-cal-list-delete').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id || '';
            if (!id || !confirm('Delete this event?')) return;
            const r = await _api(ARI_CALENDAR.deleteUrl, 'POST', { id });
            if (r.success) {
                _events = _events.filter(e => e.id !== id);
                _renderMonth();
                _toast('Event deleted.');
            } else {
                _toast(r.error || 'Error', false);
            }
        });
    });
}

/** Expand recurring events within a given year/month */
function _expandMonth(events, year, month) {
    const result = [];
    const first = new Date(year, month, 1);
    const last = new Date(year, month + 1, 0);
    for (const ev of events) {
        if (!ev.date) continue;
        const base = new Date(ev.date + 'T00:00:00');
        const rec = ev.recurrence || 'none';
        if (rec === 'none') {
            if (base >= first && base <= last) result.push(ev);
        } else {
            // Walk from base, generating occurrences in this month
            let cur = new Date(base);
            // Skip forward to at least first of target month
            while (cur < first) {
                if (rec === 'daily') cur.setDate(cur.getDate() + 1);
                else if (rec === 'weekly') cur.setDate(cur.getDate() + 7);
                else if (rec === 'monthly') cur.setMonth(cur.getMonth() + 1);
                else if (rec === 'yearly') cur.setFullYear(cur.getFullYear() + 1);
                else break;
            }
            while (cur <= last) {
                result.push({...ev, date: cur.toISOString().slice(0, 10), _recurring: true});
                if (rec === 'daily') cur.setDate(cur.getDate() + 1);
                else if (rec === 'weekly') cur.setDate(cur.getDate() + 7);
                else if (rec === 'monthly') cur.setMonth(cur.getMonth() + 1);
                else if (rec === 'yearly') cur.setFullYear(cur.getFullYear() + 1);
                else break;
            }
        }
    }
    return result;
}

function _renderMonth() {
    document.getElementById('cal-month-label').textContent =
        `${_MONTH_NAMES[_month]} ${_year}`;

    const expanded = _expandMonth(_events, _year, _month);

    // Index by date string
    const byDate = {};
    for (const ev of expanded) {
        (byDate[ev.date] = byDate[ev.date] || []).push(ev);
    }

    const firstDay = new Date(_year, _month, 1).getDay();
    const daysInMonth = new Date(_year, _month + 1, 0).getDate();
    const todayStr = new Date().toISOString().slice(0, 10);

    let html = `<div class="ari-cal-weekdays">
        ${_DAY_NAMES.map(d => `<div class="ari-cal-wd">${d}</div>`).join('')}
    </div><div class="ari-cal-days">`;

    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
        html += '<div class="ari-cal-cell ari-cal-cell--empty"></div>';
    }

    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${_year}-${String(_month + 1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
        const isToday = dateStr === todayStr;
        const dayEvents = byDate[dateStr] || [];
        const evHtml = dayEvents.slice(0, 3).map(ev => {
            let label = ev.title;
            if (ev.time) {
                const evTz = ev.timezone || 'UTC';
                if (evTz !== _userTz) {
                    const conv = ariConvertEventTime(ev.date, ev.time, evTz, _userTz);
                    label = `${conv.time} ${ev.title}`;
                } else {
                    label = `${ev.time} ${ev.title}`;
                }
            }
            return `<div class="ari-cal-event ${ev._source ? 'ari-cal-event--instr' : ''}"
                  style="background:${_esc(ev.color || '#4a90d9')}"
                  data-id="${_esc(ev.id)}"
                  title="${_esc(label)}">${_esc(label)}</div>`;
        }).join('');
        const more = dayEvents.length > 3 ? `<div class="ari-cal-more">+${dayEvents.length - 3} more</div>` : '';
        html += `<div class="ari-cal-cell ${isToday ? 'ari-cal-cell--today' : ''}" data-date="${dateStr}">
            <span class="ari-cal-day-num">${d}</span>
            <div class="ari-cal-day-events">${evHtml}${more}</div>
        </div>`;
    }

    html += '</div>';
    const grid = document.getElementById('cal-grid');
    grid.innerHTML = html;

    // Click on an event
    grid.querySelectorAll('.ari-cal-event').forEach(el => {
        el.addEventListener('click', e => {
            e.stopPropagation();
            const ev = _events.find(ev => ev.id === el.dataset.id);
            if (ev && !ev._source) _openModal(ev);
        });
    });

    // Click on a day cell to add event
    grid.querySelectorAll('.ari-cal-cell:not(.ari-cal-cell--empty)').forEach(el => {
        el.addEventListener('click', () => {
            _openModal(null, el.dataset.date);
        });
    });

    _renderEventList(expanded);
}

function _openModal(event, defaultDate = '') {
    _editId = event ? event.id : null;
    const title = document.getElementById('cal-modal-title');
    const deleteBtn = document.getElementById('cal-modal-delete');
    title.textContent = event ? 'Edit Event' : 'New Event';
    deleteBtn.style.display = event ? 'inline-flex' : 'none';
    document.getElementById('cal-modal-event-title').value = event ? event.title : '';
    document.getElementById('cal-modal-date').value = event ? event.date : defaultDate;
    document.getElementById('cal-modal-time').value = event ? (event.time || '') : '';
    const tzSel = document.getElementById('cal-modal-timezone');
    ariPopulateTimezoneSelect(tzSel, event ? (event.timezone || _userTz) : _userTz);
    document.getElementById('cal-modal-category').value = event ? (event.category || 'personal') : 'personal';
    document.getElementById('cal-modal-recurrence').value = event ? (event.recurrence || 'none') : 'none';
    document.getElementById('cal-modal-status').value = event ? (event.status || 'confirmed') : 'confirmed';
    document.getElementById('cal-modal-color').value = event ? (event.color || '#4a90d9') : '#4a90d9';
    document.getElementById('cal-modal').style.display = 'flex';
}

async function _loadEvents() {
    const instr = (document.getElementById('cal-instr-select') || {}).value || '';
    const url = instr
        ? `${ARI_CALENDAR.listUrl}?instrument=${encodeURIComponent(instr)}`
        : ARI_CALENDAR.listUrl;
    const r = await _api(url);
    if (r.success) { _events = r.events || []; _listPage = 1; _renderMonth(); }
    else _toast(r.error || 'Failed to load events', false);
}

document.addEventListener('DOMContentLoaded', () => {
    // Populate timezone preference selector
    const tzPrefSel = document.getElementById('cal-tz-pref');
    if (tzPrefSel) {
        ariPopulateTimezoneSelect(tzPrefSel, _userTz);
        tzPrefSel.addEventListener('change', async () => {
            _userTz = tzPrefSel.value;
            // Persist server-side
            await _api(ARI_CALENDAR.prefsSaveUrl, 'POST', {timezone: _userTz});
            _renderMonth();
            _toast('Timezone updated to ' + _userTz);
        });
    }

    _loadEvents();

    const instrSel = document.getElementById('cal-instr-select');
    if (instrSel) instrSel.addEventListener('change', _loadEvents);

    document.getElementById('cal-prev').addEventListener('click', () => {
        _month--; if (_month < 0) { _month = 11; _year--; } _listPage = 1; _renderMonth();
    });
    document.getElementById('cal-next').addEventListener('click', () => {
        _month++; if (_month > 11) { _month = 0; _year++; } _listPage = 1; _renderMonth();
    });
    document.getElementById('cal-today').addEventListener('click', () => {
        _year = new Date().getFullYear();
        _month = new Date().getMonth();
        _listPage = 1;
        _renderMonth();
    });
    document.getElementById('cal-list-per-page').addEventListener('change', e => {
        _listPerPage = Math.max(1, parseInt(e.target.value || '8', 10));
        _listPage = 1;
        _renderMonth();
    });
    document.getElementById('cal-list-prev').addEventListener('click', () => {
        if (_listPage > 1) { _listPage -= 1; _renderMonth(); }
    });
    document.getElementById('cal-list-next').addEventListener('click', () => {
        _listPage += 1;
        _renderMonth();
    });
    document.getElementById('cal-add-btn').addEventListener('click', () => _openModal(null));
    document.getElementById('cal-modal-cancel').addEventListener('click', () => {
        document.getElementById('cal-modal').style.display = 'none';
    });
    document.getElementById('cal-modal').addEventListener('click', e => {
        if (e.target.id === 'cal-modal') e.target.style.display = 'none';
    });

    document.getElementById('cal-modal-save').addEventListener('click', async () => {
        const eventTitle = document.getElementById('cal-modal-event-title').value.trim();
        const date = document.getElementById('cal-modal-date').value;
        if (!eventTitle || !date) { _toast('Title and date are required.', false); return; }
        const body = {
            id: _editId || '',
            title: eventTitle,
            date,
            time: document.getElementById('cal-modal-time').value,
            timezone: document.getElementById('cal-modal-timezone').value,
            category: document.getElementById('cal-modal-category').value,
            recurrence: document.getElementById('cal-modal-recurrence').value,
            status: document.getElementById('cal-modal-status').value,
            color: document.getElementById('cal-modal-color').value,
        };
        const r = await _api(ARI_CALENDAR.saveUrl, 'POST', body);
        if (r.success) {
            const saved = r.event;
            const idx = _events.findIndex(e => e.id === saved.id);
            if (idx >= 0) _events[idx] = saved; else _events.push(saved);
            _renderMonth();
            document.getElementById('cal-modal').style.display = 'none';
            _toast(_editId ? 'Event updated.' : 'Event added.');
        } else { _toast(r.error || 'Error', false); }
    });

    document.getElementById('cal-modal-delete').addEventListener('click', async () => {
        if (!_editId || !confirm('Delete this event?')) return;
        const r = await _api(ARI_CALENDAR.deleteUrl, 'POST', { id: _editId });
        if (r.success) {
            _events = _events.filter(e => e.id !== _editId);
            _renderMonth();
            document.getElementById('cal-modal').style.display = 'none';
            _toast('Event deleted.');
        } else { _toast(r.error || 'Error', false); }
    });
});
