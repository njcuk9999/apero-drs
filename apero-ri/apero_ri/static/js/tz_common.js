/* Shared timezone helpers for calendar pages */
'use strict';

/**
 * Curated list of common IANA timezones grouped by region.
 * Covers all major UTC offsets.
 */
const ARI_TIMEZONES = [
    {group: 'UTC', zones: ['UTC']},
    {group: 'Americas', zones: [
        'America/New_York',
        'America/Chicago',
        'America/Denver',
        'America/Los_Angeles',
        'America/Anchorage',
        'America/Toronto',
        'America/Vancouver',
        'America/Montreal',
        'America/Halifax',
        'America/St_Johns',
        'America/Mexico_City',
        'America/Sao_Paulo',
        'America/Argentina/Buenos_Aires',
        'America/Santiago',
        'America/Bogota',
        'America/Lima',
    ]},
    {group: 'Europe', zones: [
        'Europe/London',
        'Europe/Paris',
        'Europe/Berlin',
        'Europe/Madrid',
        'Europe/Rome',
        'Europe/Amsterdam',
        'Europe/Brussels',
        'Europe/Zurich',
        'Europe/Vienna',
        'Europe/Stockholm',
        'Europe/Oslo',
        'Europe/Copenhagen',
        'Europe/Helsinki',
        'Europe/Warsaw',
        'Europe/Prague',
        'Europe/Athens',
        'Europe/Moscow',
        'Europe/Istanbul',
    ]},
    {group: 'Asia / Middle East', zones: [
        'Asia/Dubai',
        'Asia/Kolkata',
        'Asia/Shanghai',
        'Asia/Tokyo',
        'Asia/Seoul',
        'Asia/Singapore',
        'Asia/Hong_Kong',
        'Asia/Taipei',
        'Asia/Bangkok',
        'Asia/Jakarta',
        'Asia/Karachi',
        'Asia/Tehran',
        'Asia/Jerusalem',
    ]},
    {group: 'Pacific / Oceania', zones: [
        'Pacific/Auckland',
        'Pacific/Fiji',
        'Pacific/Honolulu',
        'Australia/Sydney',
        'Australia/Melbourne',
        'Australia/Perth',
        'Australia/Brisbane',
        'Australia/Adelaide',
    ]},
    {group: 'Africa', zones: [
        'Africa/Cairo',
        'Africa/Johannesburg',
        'Africa/Lagos',
        'Africa/Nairobi',
        'Africa/Casablanca',
    ]},
];

/**
 * Populate a <select> element with timezone options.
 * @param {HTMLSelectElement} sel - The select element to populate.
 * @param {string} selected - IANA timezone to pre-select (default 'UTC').
 */
function ariPopulateTimezoneSelect(sel, selected) {
    if (!sel) return;
    selected = selected || 'UTC';
    sel.innerHTML = '';
    for (const group of ARI_TIMEZONES) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = group.group;
        for (const tz of group.zones) {
            const opt = document.createElement('option');
            opt.value = tz;
            // Friendly label: strip continent prefix, replace _ with space
            const short = tz.includes('/') ? tz.split('/').slice(1).join('/') : tz;
            opt.textContent = short.replace(/_/g, ' ') + ' (' + _ariTzOffset(tz) + ')';
            if (tz === selected) opt.selected = true;
            optgroup.appendChild(opt);
        }
        sel.appendChild(optgroup);
    }
}

/**
 * Get a short UTC offset string for a timezone (e.g. "UTC+5:30").
 */
function _ariTzOffset(tz) {
    try {
        const now = new Date();
        const fmt = new Intl.DateTimeFormat('en-US', {
            timeZone: tz, timeZoneName: 'shortOffset'
        });
        const parts = fmt.formatToParts(now);
        const tzPart = parts.find(p => p.type === 'timeZoneName');
        return tzPart ? tzPart.value : tz;
    } catch {
        return tz;
    }
}

/**
 * Convert an event time from its stored timezone to a display timezone.
 * Returns {date, time} strings in the display timezone, or the originals
 * if conversion is not possible.
 * @param {string} date - 'YYYY-MM-DD'
 * @param {string} time - 'HH:MM' or ''
 * @param {string} fromTz - Source IANA timezone
 * @param {string} toTz - Target IANA timezone
 * @returns {{date: string, time: string}}
 */
function ariConvertEventTime(date, time, fromTz, toTz) {
    if (!date || !time || !fromTz || !toTz || fromTz === toTz) {
        return {date: date || '', time: time || ''};
    }
    try {
        // Build an ISO-like string and interpret in the source timezone
        const dtStr = `${date}T${time}:00`;
        // Use Intl to find the offset of the source timezone at this moment
        const srcDate = new Date(dtStr);
        const inSrc = new Intl.DateTimeFormat('en-CA', {
            timeZone: toTz,
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', hour12: false
        });
        // Create a Date that represents the wall time in fromTz
        // by computing the UTC equivalent
        const fromOff = _ariTzOffsetMin(srcDate, fromTz);
        const toOff = _ariTzOffsetMin(srcDate, toTz);
        const diff = toOff - fromOff; // minutes
        const converted = new Date(srcDate.getTime() + diff * 60000);
        const parts = inSrc.formatToParts(converted);
        const pMap = {};
        for (const p of parts) pMap[p.type] = p.value;
        const newDate = `${pMap.year}-${pMap.month}-${pMap.day}`;
        const h = (pMap.hour || '00').padStart(2, '0');
        const m = (pMap.minute || '00').padStart(2, '0');
        return {date: newDate, time: `${h}:${m}`};
    } catch {
        return {date: date || '', time: time || ''};
    }
}

/**
 * Get timezone offset in minutes from UTC for a given Date in a timezone.
 */
function _ariTzOffsetMin(date, tz) {
    const utcStr = date.toLocaleString('en-US', {timeZone: 'UTC'});
    const tzStr = date.toLocaleString('en-US', {timeZone: tz});
    return (new Date(tzStr) - new Date(utcStr)) / 60000;
}

/**
 * Format a short timezone abbreviation for display.
 */
function ariTzShortLabel(tz) {
    if (!tz || tz === 'UTC') return 'UTC';
    try {
        const fmt = new Intl.DateTimeFormat('en-US', {
            timeZone: tz, timeZoneName: 'short'
        });
        const parts = fmt.formatToParts(new Date());
        const tzPart = parts.find(p => p.type === 'timeZoneName');
        return tzPart ? tzPart.value : tz;
    } catch {
        return tz;
    }
}
