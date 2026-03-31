/* global ARI_ADMIN_CAL */
'use strict';

let _events = [];
let _year = new Date().getFullYear();
let _month = new Date().getMonth();
let _editId = null;

const _MONTH_NAMES = ['January','February','March','April','May','June',
                      'July','August','September','October','November','December'];
const _DAY_NAMES = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

function _currentInstrument() {
    const sel = document.getElementById('admin-cal-instr');
    return sel ? sel.value : '';
}

async function _api(url, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    return (await fetch(url, opts)).json();
}

function _toast(msg, ok = true) {
    const el = document.getElementById('admin-cal-toast');
    el.textContent = msg;
    el.className = `ari-toast ari-toast--${ok ? 'success' : 'error'}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function _esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

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
            let cur = new Date(base);
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
    document.getElementById('admin-cal-month-label').textContent =
        `${_MONTH_NAMES[_month]} ${_year}`;
    const expanded = _expandMonth(_events, _year, _month);
    const byDate = {};
    for (const ev of expanded) {
        (byDate[ev.date] = byDate[ev.date] || []).push(ev);
    }
    const firstDay = new Date(_year, _month, 1).getDay();
    const daysInMonth = new Date(_year, _month + 1, 0).getDate();
    const todayStr = new Date().toISOString().slice(0, 10);
    let html = `<div class="ari-cal-weekdays">${_DAY_NAMES.map(d => `<div class="ari-cal-wd">${d}</div>`).join('')}</div><div class="ari-cal-days">`;
    for (let i = 0; i < firstDay; i++) html += '<div class="ari-cal-cell ari-cal-cell--empty"></div>';
    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${_year}-${String(_month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
        const isToday = dateStr === todayStr;
        const dayEvents = byDate[dateStr] || [];
        const evHtml = dayEvents.slice(0, 3).map(ev => {
            const tzLabel = (ev.time && ev.timezone && ev.timezone !== 'UTC')
                ? ` (${ariTzShortLabel(ev.timezone)})` : (ev.time ? ' (UTC)' : '');
            const label = ev.time ? `${ev.time}${tzLabel} ${ev.title}` : ev.title;
            return `<div class="ari-cal-event" style="background:${_esc(ev.color||'#7b5ea7')}"
                  data-id="${_esc(ev.id)}" title="${_esc(label)}">${_esc(label)}</div>`;
        }).join('');
        const more = dayEvents.length > 3 ? `<div class="ari-cal-more">+${dayEvents.length-3} more</div>` : '';
        html += `<div class="ari-cal-cell ${isToday ? 'ari-cal-cell--today' : ''}" data-date="${dateStr}">
            <span class="ari-cal-day-num">${d}</span>
            <div class="ari-cal-day-events">${evHtml}${more}</div>
        </div>`;
    }
    html += '</div>';
    const grid = document.getElementById('admin-cal-grid');
    grid.innerHTML = html;

    if (ARI_ADMIN_CAL.canManage) {
        grid.querySelectorAll('.ari-cal-event').forEach(el => {
            el.addEventListener('click', e => {
                e.stopPropagation();
                const ev = _events.find(ev => ev.id === el.dataset.id);
                if (ev) _openModal(ev);
            });
        });
        grid.querySelectorAll('.ari-cal-cell:not(.ari-cal-cell--empty)').forEach(el => {
            el.addEventListener('click', () => _openModal(null, el.dataset.date));
        });
    }
}

function _openModal(event, defaultDate = '') {
    if (!ARI_ADMIN_CAL.canManage) return;
    _editId = event ? event.id : null;
    document.getElementById('admin-cal-modal-title').textContent = event ? 'Edit Event' : 'New Instrument Event';
    document.getElementById('admin-cal-modal-delete').style.display = event ? 'inline-flex' : 'none';
    document.getElementById('admin-cal-modal-event-title').value = event ? event.title : '';
    document.getElementById('admin-cal-modal-date').value = event ? event.date : defaultDate;
    document.getElementById('admin-cal-modal-time').value = event ? (event.time || '') : '';
    const tzSel = document.getElementById('admin-cal-modal-timezone');
    ariPopulateTimezoneSelect(tzSel, event ? (event.timezone || 'UTC') : 'UTC');
    document.getElementById('admin-cal-modal-recurrence').value = event ? (event.recurrence || 'none') : 'none';
    document.getElementById('admin-cal-modal-status').value = event ? (event.status || 'confirmed') : 'confirmed';
    document.getElementById('admin-cal-modal-color').value = event ? (event.color || '#7b5ea7') : '#7b5ea7';
    document.getElementById('admin-cal-modal').style.display = 'flex';
}

async function _loadEvents() {
    const instr = _currentInstrument();
    if (!instr) return;
    const r = await _api(`${ARI_ADMIN_CAL.listUrl}?instrument=${encodeURIComponent(instr)}`);
    if (r.success) { _events = r.events || []; _renderMonth(); }
    else _toast(r.error || 'Failed to load', false);
}

document.addEventListener('DOMContentLoaded', () => {
    _loadEvents();

    const instrSel = document.getElementById('admin-cal-instr');
    if (instrSel) instrSel.addEventListener('change', _loadEvents);

    document.getElementById('admin-cal-prev').addEventListener('click', () => {
        _month--; if (_month < 0) { _month = 11; _year--; } _renderMonth();
    });
    document.getElementById('admin-cal-next').addEventListener('click', () => {
        _month++; if (_month > 11) { _month = 0; _year++; } _renderMonth();
    });
    document.getElementById('admin-cal-today').addEventListener('click', () => {
        _year = new Date().getFullYear(); _month = new Date().getMonth(); _renderMonth();
    });

    const addBtn = document.getElementById('admin-cal-add-btn');
    if (addBtn) addBtn.addEventListener('click', () => _openModal(null));

    const cancelBtn = document.getElementById('admin-cal-modal-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', () => {
        document.getElementById('admin-cal-modal').style.display = 'none';
    });

    const modal = document.getElementById('admin-cal-modal');
    if (modal) modal.addEventListener('click', e => {
        if (e.target.id === 'admin-cal-modal') e.target.style.display = 'none';
    });

    const saveBtn = document.getElementById('admin-cal-modal-save');
    if (saveBtn) saveBtn.addEventListener('click', async () => {
        const title = document.getElementById('admin-cal-modal-event-title').value.trim();
        const date = document.getElementById('admin-cal-modal-date').value;
        if (!title || !date) { _toast('Title and date are required.', false); return; }
        const body = {
            id: _editId || '',
            instrument: _currentInstrument(),
            title,
            date,
            time: document.getElementById('admin-cal-modal-time').value,
            timezone: document.getElementById('admin-cal-modal-timezone').value,
            recurrence: document.getElementById('admin-cal-modal-recurrence').value,
            status: document.getElementById('admin-cal-modal-status').value,
            color: document.getElementById('admin-cal-modal-color').value,
        };
        const r = await _api(ARI_ADMIN_CAL.saveUrl, 'POST', body);
        if (r.success) {
            const idx = _events.findIndex(e => e.id === r.event.id);
            if (idx >= 0) _events[idx] = r.event; else _events.push(r.event);
            _renderMonth();
            document.getElementById('admin-cal-modal').style.display = 'none';
            _toast(_editId ? 'Event updated.' : 'Event added.');
        } else { _toast(r.error || 'Error', false); }
    });

    const deleteBtn = document.getElementById('admin-cal-modal-delete');
    if (deleteBtn) deleteBtn.addEventListener('click', async () => {
        if (!_editId || !confirm('Delete this event?')) return;
        const r = await _api(ARI_ADMIN_CAL.deleteUrl, 'POST', {
            instrument: _currentInstrument(), id: _editId
        });
        if (r.success) {
            _events = _events.filter(e => e.id !== _editId);
            _renderMonth();
            document.getElementById('admin-cal-modal').style.display = 'none';
            _toast('Event deleted.');
        } else { _toast(r.error || 'Error', false); }
    });
});
