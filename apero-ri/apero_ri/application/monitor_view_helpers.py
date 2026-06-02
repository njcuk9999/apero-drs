#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Monitor portal view helpers.

Currently exposes:
    monitor_issues_view(app)
        Renders the issues management page (monitor+ only).

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from html.parser import HTMLParser

from flask import (flash, redirect, render_template, request,
                   session, url_for)

from apero_ri.core.auth import (
    get_accessible_profiles,
    get_effective_user,
    get_public_permissions,
)
from apero_ri.apero_monitoring.checks import CHECKS as MONITOR_CHECKS
from apero_ri.core.docs import render_markdown
from apero_ri.core import apero_checks as checks_core
from apero_ri.core.permissions import resolve_user_permissions
from apero_ri.core import permissions as perms_mod
from apero_ri.application import instrument_color_helpers


__NAME__ = 'apero_ri.application.monitor_view_helpers'


ALLIANCE_STATUS_URL = 'https://status.alliancecan.ca/'
CANFAR_STATUS_URL = 'https://canfar.statuspage.io/'


_MONITOR_PERMS = {'view.monitor_portal', 'view.monitor',
                  'manage.astrometrics'}


def _can_manage_apero_profiles(perms):
    """Return True when user can manage APERO profiles."""
    return 'manage.apero_profile' in set(perms or set())


def _can_see_apero_checks_advanced(perms, groups):
    """Return True when user can see APERO-check advanced options."""
    if _can_manage_apero_profiles(perms):
        return True
    allow_roles = {'moderator', 'developer', 'admin', 'superadmin'}
    for item in groups or []:
        value = str(item or '').strip().lower()
        if value in allow_roles:
            return True
        parts = [p for p in re.split(r'[\s._:/-]+', value) if p]
        if set(parts) & allow_roles:
            return True
    return False


def _can_manage_sci_groups(perms):
    """Return True when user can manage any science group."""
    pset = set(perms or set())
    if 'manage.sci_group' in pset:
        return True
    return any(
        isinstance(item, str) and item.startswith('manage.sci_group.')
        for item in pset
    )


def _monitor_docs_url() -> str:
    """Return the root monitoring documentation URL."""
    return url_for('doc_dynamic_view', page_ref='monitor')


def _monitor_check_docs_url(check_key: str) -> str:
    """Return the documentation URL for one monitor check."""
    clean_key = str(check_key or '').strip()
    slug = clean_key.lower()
    check_obj = MONITOR_CHECKS.get(clean_key)
    if check_obj is not None:
        obj_name = str(getattr(check_obj, 'name', '') or '').strip()
        if obj_name:
            slug = obj_name.lower()
    if not slug:
        return _monitor_docs_url()
    return url_for('doc_dynamic_view', page_ref=f'monitor/checks/{slug}')


def _monitor_profile_logic_payload(
    check_key: str,
    profile_data: dict,
) -> dict:
    """Return profile-specific logic markdown/html for one check."""
    check_obj = MONITOR_CHECKS.get(str(check_key or '').strip())
    if check_obj is None:
        return dict(markdown='', html='')

    simple_check = getattr(check_obj, 'simple_check', None)
    if simple_check is None:
        return dict(markdown='', html='')

    from apero_ri.apero_monitoring.core import raw_common

    cfg = raw_common.get_check_value(
        profile_data,
        simple_check.config_section,
        ['tests', simple_check.test_key],
        dict(),
    )
    if not isinstance(cfg, dict):
        cfg = dict()

    values = simple_check._display_cfg()
    values['enabled'] = raw_common.to_bool(
        cfg.get('enabled', True),
        default=True,
    )
    values.update(simple_check._runtime_logic_values(cfg, profile_data))

    logic_markdown = str(simple_check.get_logic_markdown(values) or '').strip()
    logic_html = render_markdown(logic_markdown) if logic_markdown else ''
    return dict(markdown=logic_markdown, html=logic_html)


def _has_any_monitor_perm(perms):
    """Return True if user has any monitor-level permission.

    Accepts the legacy flat perms (view.monitor_portal,
    view.monitor, manage.astrometrics) AND the per-instrument
    pattern monitor.{INSTRUMENT} (e.g. monitor.SPIROU,
    monitor.NIRPS_HE). Hierarchical perms like
    view.monitor_portal.SPIROU are also accepted.
    """
    pset = set(perms or ())
    if _MONITOR_PERMS & pset:
        return True
    for p in pset:
        if not isinstance(p, str):
            continue
        if p.startswith('monitor.'):
            return True
        if p.startswith('view.monitor_portal.'):
            return True
        if p.startswith('view.monitor.'):
            return True
    return False


def _monitor_instruments(perms, groups, ari_groups):
    instruments = set()
    valid = set(
        perms_mod.load_parameters().get('instruments', {})
        .get('value', [])
    )
    for perm in set(perms or set()):
        if not isinstance(perm, str):
            continue
        if perm.startswith('monitor.'):
            suffix = perm.split('.', 1)[1].strip().upper()
            if suffix in valid:
                instruments.add(suffix)
        if perm.startswith('view.monitor_portal.'):
            suffix = perm.rsplit('.', 1)[-1].strip().upper()
            if suffix in valid:
                instruments.add(suffix)
    if ('monitor' in set(perms or set())
            or 'view.monitor_portal' in set(perms or set())
            or 'manage.astrometrics' in set(perms or set())):
        instruments |= set(
            perms_mod.get_user_instruments(groups, ari_groups)
        )
    return sorted(list(instruments))


class _AllianceStatusParser(HTMLParser):
    """Collect visible tables, links, and paragraphs from the status page."""

    def __init__(self):
        super().__init__()
        self.tables = []
        self.links = []
        self.paragraphs = []
        self.text_chunks = []
        self._table = None
        self._row = None
        self._cell = None
        self._cell_tag = None
        self._paragraph = None
        self._link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table':
            self._table = []
        elif tag == 'tr' and self._table is not None:
            self._row = []
        elif tag in {'td', 'th'} and self._row is not None:
            self._cell = []
            self._cell_tag = tag
        elif tag == 'p':
            self._paragraph = []
        elif tag == 'a':
            self._link = {
                'href': attrs.get('href', ''),
                'text': [],
            }

    def handle_data(self, data):
        self.text_chunks.append(data)
        if self._cell is not None:
            self._cell.append(data)
        if self._paragraph is not None:
            self._paragraph.append(data)
        if self._link is not None:
            self._link['text'].append(data)

    def handle_endtag(self, tag):
        if tag in {'td', 'th'} and self._cell is not None:
            cell_text = ''.join(self._cell).strip()
            cell_text = re.sub(r'\s*question\s*$', '', cell_text, flags=re.I)
            self._row.append(cell_text)
            self._cell = None
            self._cell_tag = None
        elif tag == 'tr' and self._row is not None:
            if self._table is not None:
                self._table.append(self._row)
            self._row = None
        elif tag == 'table' and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None
        elif tag == 'p' and self._paragraph is not None:
            text = ' '.join(''.join(self._paragraph).split()).strip()
            if text:
                self.paragraphs.append(text)
            self._paragraph = None
        elif tag == 'a' and self._link is not None:
            href = str(self._link.get('href', '') or '').strip()
            text = ' '.join(''.join(self._link.get('text', [])).split()).strip()
            if text or href:
                self.links.append({'href': href, 'text': text})
            self._link = None


def _scrape_alliance_status_page():
    """Fetch and parse the Digital Research Alliance status page."""
    from urllib.parse import urljoin
    from urllib.request import Request, urlopen

    req = Request(
        ALLIANCE_STATUS_URL,
        headers={'User-Agent': 'APERO RI status page'},
    )
    with urlopen(req, timeout=20) as handle:
        html = handle.read().decode('utf-8', errors='replace')

    parser = _AllianceStatusParser()
    parser.feed(html)

    icon_tokens = re.findall(
        r'\b(check|warning_amber|power_off)\b',
        html.lower(),
    )

    visible_text = ' '.join(''.join(parser.text_chunks).split())

    tables = []
    for raw_table in parser.tables:
        if not raw_table:
            continue
        headers = raw_table[0]
        rows = []
        for raw_row in raw_table[1:]:
            if not raw_row:
                continue
            padded = list(raw_row) + [''] * max(0, len(headers) - len(raw_row))
            rows.append({
                headers[i] if i < len(headers) else f'col_{i}': padded[i]
                for i in range(len(padded))
            })
        tables.append({'headers': headers, 'rows': rows})

    tables.sort(key=lambda item: len(item.get('rows', [])), reverse=True)
    service_table = tables[0] if tables else {'headers': [], 'rows': []}

    summary = ''
    for phrase in (
        'Partially degraded service',
        'Operational',
        'Available with conditions',
        'Outage',
        'Decommissioned',
    ):
        idx = visible_text.lower().find(phrase.lower())
        if idx >= 0:
            summary = visible_text[idx: idx + 180].strip()
            break
    if not summary:
        for text in parser.paragraphs:
            lower = text.lower()
            if (
                'degraded service' in lower
                or 'operational' in lower
                or 'outage' in lower
                or 'available with conditions' in lower
            ):
                summary = text
                break
    if not summary and parser.paragraphs:
        summary = parser.paragraphs[0]

    events = []
    seen_events = set()
    for link in parser.links:
        href = str(link.get('href') or '').strip()
        text = str(link.get('text') or '').strip()
        if 'view_incident' not in href:
            continue
        full_url = urljoin(ALLIANCE_STATUS_URL, href)
        if full_url in seen_events:
            continue
        seen_events.add(full_url)
        events.append({
            'text': text or full_url,
            'url': full_url,
        })

    overall = 'Unknown'
    if summary:
        overall = summary.split('.')[0].strip()

    return {
        'title': 'Digital Research Alliance of Canada',
        'url': ALLIANCE_STATUS_URL,
        'summary': summary,
        'overall_status': overall,
        'icon_tokens': icon_tokens,
        'service_table': service_table,
        'scheduled_events': events,
        'fetched_at': datetime.now(timezone.utc).strftime(
            '%Y-%m-%d %H:%M UTC'
        ),
    }


def _status_level_from_tokens(tokens):
    """Return ok/warning/critical based on status icon tokens."""
    cleaned = []
    for token in list(tokens or []):
        value = str(token or '').strip().lower()
        if value:
            cleaned.append(value)
    if not cleaned:
        return 'warning'
    if 'power_off' in cleaned:
        return 'critical'
    for token in cleaned:
        if token != 'check':
            return 'warning'
    return 'ok'


def _extract_first_past_incident_text(text):
    """Extract the most recent 'Past Incidents' body text snippet."""
    normalized = ' '.join(str(text or '').split())
    lower = normalized.lower()
    marker = lower.find('past incidents')
    if marker >= 0:
        normalized = normalized[marker:]

    date_pattern = (
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+'
        r'\\d{1,2},\\s+\\d{4}'
    )
    first_date = re.search(date_pattern, normalized)
    if first_date is None:
        return ''

    tail = normalized[first_date.end():].strip()
    second_date = re.search(date_pattern, tail)
    if second_date is None:
        snippet = tail
    else:
        snippet = tail[:second_date.start()]
    snippet = ' '.join(snippet.split()).strip()
    return snippet


def _scrape_canfar_status_page():
    """Fetch and parse the CANFAR status page."""
    from urllib.parse import urljoin
    from urllib.request import Request, urlopen

    req = Request(
        CANFAR_STATUS_URL,
        headers={'User-Agent': 'APERO RI status page'},
    )
    with urlopen(req, timeout=20) as handle:
        html = handle.read().decode('utf-8', errors='replace')

    parser = _AllianceStatusParser()
    parser.feed(html)

    visible_text = ' '.join(''.join(parser.text_chunks).split())
    recent_entry = _extract_first_past_incident_text(visible_text)
    has_no_incidents_today = (
        'no incidents reported today' in recent_entry.lower()
    )

    incidents = []
    seen = set()
    for link in parser.links:
        href = str(link.get('href') or '').strip()
        text = str(link.get('text') or '').strip()
        if '/incidents/' not in href:
            continue
        full_url = urljoin(CANFAR_STATUS_URL, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        incidents.append({
            'text': text or full_url,
            'url': full_url,
        })

    level = 'ok' if has_no_incidents_today else 'warning'
    if has_no_incidents_today:
        overall = 'No incidents reported today'
    else:
        overall = 'Recent incidents present'

    return {
        'title': 'CANFAR',
        'url': CANFAR_STATUS_URL,
        'summary': recent_entry,
        'overall_status': overall,
        'status_level': level,
        'most_recent_entry': recent_entry,
        'scheduled_events': incidents,
        'fetched_at': datetime.now(timezone.utc).strftime(
            '%Y-%m-%d %H:%M UTC'
        ),
    }


def monitor_issues_view(app):
    """Render the monitor portal issues management page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    visibility = 'admin' if 'manage.astrometrics' in perms \
        else 'monitor'

    page_id = 'home.monitor_portal.issues'
    context = {
        'page_id': page_id,
        'page_label': 'Issues',
        'page_icon': 'fa-solid fa-flag',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'visibility': visibility,
    }
    # Build the sidebar/nav tree the same way other pages do so the
    # sidebar_base.html template renders a populated navbar instead
    # of a blank shell.
    try:
        context.update(
            app._build_sidebar_context(page_id, perms, user_info)
        )
    except Exception:
        # If sidebar construction fails for any reason, still render
        # the page with the previously-set static defaults rather
        # than 500'ing.
        pass
    return render_template('monitor_portal/issues.html',
                           **context)


def monitor_known_errors_view(app):
    """Render the monitor portal known errors page.

    Read access is public. Write actions are controlled by the
    API permission checks and the `can_edit` UI flag.
    """
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()
    can_edit = _has_any_monitor_perm(perms)

    page_id = 'home.monitor_portal.known_errors'
    context = {
        'page_id': page_id,
        'page_label': 'Known errors',
        'page_icon': 'fa-solid fa-bug',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'can_edit': can_edit,
    }
    try:
        context.update(
            app._build_sidebar_context(page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template('monitor_portal/known_errors.html',
                           **context)


def monitor_status_view(app):
    """Render status index cards linking to individual status pages."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()

    page_id = 'home.monitor_portal.status'
    cards = []
    errors = []

    try:
        alliance = _scrape_alliance_status_page()
        level = _status_level_from_tokens(alliance.get('icon_tokens', []))
        cards.append({
            'title': 'Digital Research Alliance of Canada',
            'subtitle': alliance.get('overall_status', ''),
            'status_level': level,
            'fetched_at': alliance.get('fetched_at', ''),
            'url': '/monitor_portal/status/alliance',
        })
    except Exception as exc:
        errors.append(
            'Alliance status fetch failed: ' + str(exc)
        )
        cards.append({
            'title': 'Digital Research Alliance of Canada',
            'subtitle': 'Unavailable',
            'status_level': 'warning',
            'fetched_at': datetime.now(timezone.utc).strftime(
                '%Y-%m-%d %H:%M UTC'
            ),
            'url': '/monitor_portal/status/alliance',
        })

    try:
        canfar = _scrape_canfar_status_page()
        cards.append({
            'title': 'CANFAR',
            'subtitle': canfar.get('overall_status', ''),
            'status_level': canfar.get('status_level', 'warning'),
            'fetched_at': canfar.get('fetched_at', ''),
            'url': '/monitor_portal/status/canfar',
        })
    except Exception as exc:
        errors.append('CANFAR status fetch failed: ' + str(exc))
        cards.append({
            'title': 'CANFAR',
            'subtitle': 'Unavailable',
            'status_level': 'warning',
            'fetched_at': datetime.now(timezone.utc).strftime(
                '%Y-%m-%d %H:%M UTC'
            ),
            'url': '/monitor_portal/status/canfar',
        })

    context = {
        'page_id': page_id,
        'page_label': 'Status',
        'page_icon': 'fa-solid fa-signal',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'status_cards': cards,
        'status_error': ' | '.join(errors),
    }
    try:
        context.update(
            app._build_sidebar_context(page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template('monitor_portal/status.html', **context)


def monitor_status_alliance_view(app):
    """Render detailed Digital Research Alliance status content."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()

    page_id = 'home.monitor_portal.status'
    try:
        section = _scrape_alliance_status_page()
        error = ''
    except Exception as exc:
        section = {
            'title': 'Digital Research Alliance of Canada',
            'url': ALLIANCE_STATUS_URL,
            'summary': '',
            'overall_status': 'Unavailable',
            'service_table': {'headers': [], 'rows': []},
            'scheduled_events': [],
            'fetched_at': datetime.now(timezone.utc).strftime(
                '%Y-%m-%d %H:%M UTC'
            ),
        }
        error = str(exc)

    context = {
        'page_id': page_id,
        'page_label': 'Status',
        'page_icon': 'fa-solid fa-signal',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'status_title': 'Digital Research Alliance of Canada',
        'status_section': section,
        'status_error': error,
        'status_back_url': '/monitor_portal/status',
        'status_has_table': True,
    }
    try:
        context.update(
            app._build_sidebar_context(page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template('monitor_portal/status_detail.html', **context)


def monitor_status_canfar_view(app):
    """Render detailed CANFAR status content."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()

    page_id = 'home.monitor_portal.status'
    try:
        section = _scrape_canfar_status_page()
        error = ''
    except Exception as exc:
        section = {
            'title': 'CANFAR',
            'url': CANFAR_STATUS_URL,
            'summary': '',
            'overall_status': 'Unavailable',
            'status_level': 'warning',
            'most_recent_entry': '',
            'scheduled_events': [],
            'fetched_at': datetime.now(timezone.utc).strftime(
                '%Y-%m-%d %H:%M UTC'
            ),
        }
        error = str(exc)

    context = {
        'page_id': page_id,
        'page_label': 'Status',
        'page_icon': 'fa-solid fa-signal',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'status_title': 'CANFAR',
        'status_section': section,
        'status_error': error,
        'status_back_url': '/monitor_portal/status',
        'status_has_table': False,
    }
    try:
        context.update(
            app._build_sidebar_context(page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template('monitor_portal/status_detail.html', **context)


def monitor_portal_index_view(app):
    """Render the monitor portal index page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    page_id = 'home.monitor_portal'
    # Read pages fresh from disk so newly-added pages are included
    # without requiring a server restart.
    live_pages = perms_mod.load_pages()
    cards = perms_mod.get_visible_cards(
        page_id,
        perms,
        live_pages,
        logged_in=(user_info is not None),
    )
    # Append Astrometrics as an extra card (it lives outside the
    # monitor_portal tree but is useful from this page).
    astro_def = live_pages.get('home.astrometrics')
    if astro_def and perms_mod.has_view_permission(
        astro_def.get('view-permission', ''), perms
    ):
        cards.append({
            'id': 'home.astrometrics',
            'label': astro_def['label'],
            'icon': astro_def.get('icon', ''),
            'url': '/astrometrics',
            'has_children': False,
        })
    docs_def = live_pages.get('home.docs')
    if docs_def and perms_mod.has_view_permission(
        docs_def.get('view-permission', ''), perms
    ):
        cards.append({
            'id': 'home.monitor_portal.docs',
            'label': 'Monitoring docs',
            'icon': 'fa-solid fa-chart-line',
            'url': '/docs/monitor',
            'has_children': False,
        })
    # Build sidebar context
    sidebar_ctx = {}
    try:
        sidebar_ctx = app._build_sidebar_context(
            page_id, perms, user_info
        )
    except Exception:
        pass
    context = {
        'page_id': page_id,
        'page_label': 'Monitor Portal',
        'page_icon': 'fa-solid fa-chart-line',
        'cards': cards,
    }
    context.update(sidebar_ctx)

    return render_template('monitor_portal/index.html',
                           **context)


def monitor_schedule_view(app):
    """Render the monitor portal schedule page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    groups = user_info.get('groups', []) if user_info else []
    instruments = _monitor_instruments(perms, groups, app.ari_groups)
    if len(instruments) == 0:
        flash('No instrument monitor permissions were found.', 'warning')
        return redirect(url_for('monitor_issues_view'))

    page_id = 'home.monitor_portal.schedule'
    context = {
        'page_id': page_id,
        'page_label': 'Schedule',
        'page_icon': 'fa-solid fa-calendar-week',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'monitor_instruments': instruments,
    }
    try:
        context.update(
            app._build_sidebar_context(page_id, perms, user_info)
        )
    except Exception:
        pass

    return render_template('monitor_portal/schedule.html',
                           **context)


# ==========================================================================
# Processing logs views
# ==========================================================================

def _accessible_profile_cards(app, user_info, perms):
    """Return profile card list and instrument info for monitor users.

    Filters `get_accessible_profiles` to instruments the current
    monitor user has access to, then builds the card list used by
    the processing-logs index template.
    """
    groups = user_info.get('groups', []) if user_info else []
    allowed_instruments = set(
        _monitor_instruments(perms, groups, app.ari_groups)
    )
    colors = app._instrument_colors()
    accessible = get_accessible_profiles(user_info, app.ari_groups)

    cards = []
    seen_instr = set()
    for prof in accessible:
        instr = prof['instrument']
        if allowed_instruments and instr not in allowed_instruments:
            continue
        seen_instr.add(instr)
        color = colors.get(
            instr,
            instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
        )
        cards.append({
            'instrument': instr,
            'profile_id': prof['profile_id'],
            'url': (
                '/monitor_portal/proc_logs/'
                + prof['profile_id']
            ),
            'color': color,
            'apero_version': prof['data'].get(
                'apero_version', ''
            ),
            'reduction_server': prof['data'].get(
                'reduction_server', ''
            ),
        })

    shown = sorted(seen_instr)
    return cards, shown, colors


def monitor_processing_logs_view(app):
    """Render the processing logs index page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    cards, shown, colors = _accessible_profile_cards(
        app, user_info, perms
    )

    page_id = 'home.monitor_portal.proc_logs'
    context = {
        'page_id': page_id,
        'page_label': 'Processing Logs',
        'page_icon': 'fa-solid fa-scroll',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'profile_cards': cards,
        'shown_instruments': shown,
        'instrument_colors': colors,
        'can_manage_apero_profiles': _can_manage_apero_profiles(perms),
    }
    try:
        context.update(
            app._build_sidebar_context(page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template(
        'monitor_portal/processing_logs.html', **context
    )


def monitor_processing_logs_profile_view(app, profile_id):
    """Render per-profile processing log table page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    page_id = (
        'home.monitor_portal.proc_logs.'
        + str(profile_id)
    )
    context = {
        'page_id': page_id,
        'page_label': 'Processing Logs',
        'page_icon': 'fa-solid fa-scroll',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'profile_id': profile_id,
        'api_url': '/api/monitor/processing-logs',
        'log_file_url': (
            '/api/monitor/processing-logs/logfile'
        ),
        'pid_base_url': (
            '/monitor_portal/proc_logs/' + profile_id
        ),
    }
    try:
        context.update(
            app._build_sidebar_context(
                'home.monitor_portal.proc_logs', perms, user_info
            )
        )
    except Exception:
        pass
    return render_template(
        'monitor_portal/processing_logs_profile.html',
        **context,
    )


def monitor_processing_logs_pid_view(app, profile_id, pid):
    """Render per-PID recipe detail page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    page_id = (
        'home.monitor_portal.proc_logs.'
        + str(profile_id)
    )
    context = {
        'page_id': page_id,
        'page_label': 'Processing Logs',
        'page_icon': 'fa-solid fa-scroll',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'profile_id': profile_id,
        'pid': pid,
        'api_url': '/api/monitor/processing-logs/pid',
        'log_file_url': (
            '/api/monitor/processing-logs/logfile'
        ),
    }
    try:
        context.update(
            app._build_sidebar_context(
                'home.monitor_portal.proc_logs', perms, user_info
            )
        )
    except Exception:
        pass
    return render_template(
        'monitor_portal/processing_logs_pid.html',
        **context,
    )


def _checks_profile_cards(app, user_info, perms):
    """Return profile cards for the APERO checks landing page."""
    groups = user_info.get('groups', []) if user_info else []
    allowed_instruments = set(
        _monitor_instruments(perms, groups, app.ari_groups)
    )
    colors = app._instrument_colors()
    accessible = get_accessible_profiles(user_info, app.ari_groups)

    cards = []
    seen_instr = set()
    for prof in accessible:
        instr = prof['instrument']
        if allowed_instruments and instr not in allowed_instruments:
            continue
        seen_instr.add(instr)
        color = colors.get(
            instr,
            instrument_color_helpers.DEFAULT_INSTRUMENT_COLOR,
        )
        cards.append({
            'instrument': instr,
            'profile_id': prof['profile_id'],
            'url': (
                '/monitor_portal/apero_checks/'
                + prof['profile_id']
            ),
            'color': color,
            'apero_version': prof['data'].get('apero_version', ''),
            'reduction_server': prof['data'].get(
                'reduction_server', ''
            ),
        })

    shown = sorted(seen_instr)
    return cards, shown, colors


def monitor_apero_checks_view(app):
    """Render the APERO checks landing page."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    cards, shown, colors = _checks_profile_cards(app, user_info, perms)
    page_id = 'home.monitor_portal.apero_checks'
    sidebar_page_id = 'home.monitor_portal.apero_checks'
    context = {
        'page_id': page_id,
        'page_label': 'APERO Checks',
        'page_icon': 'fa-solid fa-square-check',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'profile_cards': cards,
        'shown_instruments': shown,
        'instrument_colors': colors,
        'can_manage_apero_profiles': _can_manage_apero_profiles(perms),
        'can_manage_science_groups': _can_manage_sci_groups(perms),
    }
    try:
        context.update(
            app._build_sidebar_context(sidebar_page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template('monitor_portal/apero_checks.html', **context)


def _checks_root_for_profile(app, profile_data, overrides=None):
    """Resolve the checks YAML root for one profile."""
    local_data_dir = app._resolve_local_data_dir()
    cfg = checks_core.load_config(local_data_dir)
    configured = overrides or cfg.get('checks_root') or ''
    return checks_core.resolve_checks_root(
        local_data_dir=local_data_dir,
        profile_data=profile_data,
        configured_root=configured,
    )


def _normalize_apero_checks_args(args):
    """Normalise monitor APERO-check page arguments."""
    q_page = args.get('page', '1')
    q_per_page = args.get('per_page', '10')
    q_type = str(args.get('type', 'all') or 'all').strip().lower()
    q_obsdir_filter = str(
        args.get('obsdir_filter', '') or ''
    ).strip()
    q_obsdir_sort = str(
        args.get('obsdir_sort', 'desc') or 'desc'
    ).strip().lower()
    q_result_filter = str(
        args.get('result_filter', 'all') or 'all'
    ).strip().lower()
    show_overridden = str(
        args.get('show_overridden', '1') or '1'
    ).strip() in {'1', 'true', 'yes'}
    show_monitored = str(
        args.get('show_monitored', '1') or '1'
    ).strip() in {'1', 'true', 'yes'}
    show_passed = str(
        args.get('show_passed', '1') or '1'
    ).strip() in {'1', 'true', 'yes'}
    if q_type not in {'all', 'raw', 'red'}:
        q_type = 'all'
    if q_result_filter not in {'all', 'passed', 'failed'}:
        q_result_filter = 'all'
    if q_obsdir_sort not in {'asc', 'desc'}:
        q_obsdir_sort = 'desc'
    try:
        page_num = max(1, int(q_page))
    except (TypeError, ValueError):
        page_num = 1
    try:
        per_page = max(1, int(q_per_page))
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in {10, 50, 100}:
        per_page = 10
    out = dict()
    out['page_num'] = page_num
    out['per_page'] = per_page
    out['type_filter'] = q_type
    out['result_filter'] = q_result_filter
    out['obsdir_filter'] = q_obsdir_filter
    out['obsdir_sort'] = q_obsdir_sort
    out['show_overridden'] = show_overridden
    out['show_monitored'] = show_monitored
    out['show_passed'] = show_passed
    return out


def _obsdir_matches_filter(obsdir: str, obsdir_filter: str) -> bool:
    """Return True when an obsdir matches the filter string."""
    pattern = str(obsdir_filter or '').strip()
    if pattern == '':
        return True
    value = str(obsdir or '').strip()
    try:
        return re.search(pattern, value, re.IGNORECASE) is not None
    except re.error:
        return pattern.lower() in value.lower()


def _filter_apero_check_paths(files, obsdir_filter, obsdir_sort):
    """Apply obsdir filter and sorting to APERO-check YAML paths."""
    paths = []
    for path in files:
        if not _obsdir_matches_filter(path.stem, obsdir_filter):
            continue
        paths.append(path)
    reverse = obsdir_sort == 'desc'
    paths.sort(key=lambda item: item.stem, reverse=reverse)
    return paths


def _build_apero_check_summary(
    path,
    profile_id,
    instrument,
    type_filter,
    show_overridden,
    show_monitored,
    show_passed,
    ignored_checks,
):
    """Build one obsdir card payload from a YAML file."""
    try:
        loaded = checks_core.load_check_file(path)
        return checks_core.build_obsdir_summary(
            loaded,
            type_filter=type_filter,
            show_overridden=show_overridden,
            show_monitored=show_monitored,
            show_passed=show_passed,
            ignored_checks=ignored_checks,
        )
    except Exception as exc:
        fail = dict()
        fail['name'] = 'YAML_PARSE'
        fail['type'] = 'raw'
        fail['message'] = str(exc)
        fail['override'] = dict()
        fail['monitor'] = dict()

        summary = dict()
        summary['obsdir'] = str(path.stem)
        summary['instrument'] = str(instrument)
        summary['profile'] = str(profile_id)
        summary['path'] = str(path)
        raw_last = checks_core._iso_from_mtime(str(path))
        summary['last_run'] = checks_core.format_last_run_display(raw_last)
        summary['history'] = []
        summary['visible_failures'] = [('parse_error', fail)]
        summary['visible_failure_count'] = 1
        summary['visible_passes'] = []
        summary['visible_pass_count'] = 0
        summary['ignored_failures'] = []
        summary['status'] = 'failed'
        return summary


def _build_apero_check_minimal(path):
    """Build a minimal obsdir card using file metadata only."""
    raw_last = checks_core._iso_from_mtime(str(path))
    last_run = checks_core.format_last_run_display(raw_last)
    return {
        'obsdir': path.stem,
        'last_run': last_run,
        'status': 'failed',
    }


def _build_apero_check_minimal_with_status(path, ignored_checks):
    """Build minimal obsdir card and evaluate pass/fail quickly."""
    card = _build_apero_check_minimal(path)
    ignored_set = set(ignored_checks or [])
    try:
        loaded = checks_core.load_check_file(path)
        failures = loaded.get('failures', {})
        passes = loaded.get('passes', {})
        has_overridden = False
        has_monitored = False
        has_active_failure = False
        for key, failure in failures.items():
            if key in ignored_set:
                continue
            is_overridden = bool(failure.get('override'))
            is_monitored = bool(failure.get('monitor'))
            has_overridden = has_overridden or is_overridden
            has_monitored = has_monitored or is_monitored
            if is_overridden or is_monitored:
                continue
            has_active_failure = True
            break
        for key, passed in passes.items():
            if key in ignored_set:
                continue
            has_overridden = has_overridden or bool(passed.get('override'))
            has_monitored = has_monitored or bool(passed.get('monitor'))
        if has_overridden:
            card['status'] = 'overridden'
        elif has_monitored:
            card['status'] = 'monitored'
        elif has_active_failure:
            card['status'] = 'failed'
        else:
            card['status'] = 'ok'
        card['has_overridden'] = has_overridden
        card['has_monitored'] = has_monitored
    except Exception:
        card['status'] = 'failed'
        card['has_overridden'] = False
        card['has_monitored'] = False
    return card


def _loaded_has_marker(loaded: dict,
                       ignored_checks,
                       marker: str) -> bool:
    """Return True when any non-ignored check has marker metadata."""
    ignored_set = set(ignored_checks or [])
    for bucket in ('failures', 'passes'):
        checks = loaded.get(bucket, {})
        for key, value in checks.items():
            if key in ignored_set:
                continue
            if bool((value or {}).get(marker)):
                return True
    return False


def _status_banner_state(base_state: str,
                         has_monitored: bool,
                         has_overridden: bool) -> str:
    """Resolve banner visual state with monitor/override priority."""
    if has_overridden:
        return 'overridden'
    if has_monitored:
        return 'monitored'
    if str(base_state or '').strip().lower() == 'passed':
        return 'passed'
    return 'failed'


def _monitoring_override_rows(loaded: dict, ignored_checks) -> list:
    """Build table rows for active monitor/override check markers."""
    rows = []
    ignored_set = set(ignored_checks or [])
    buckets = ('failures', 'passes')
    for bucket in buckets:
        checks = loaded.get(bucket, {})
        if not isinstance(checks, dict):
            continue
        for check_key, value in checks.items():
            if check_key in ignored_set:
                continue
            data = value if isinstance(value, dict) else dict()
            for event_key, event_label in (
                ('monitor', 'Monitor'),
                ('override', 'Override'),
            ):
                event = data.get(event_key)
                if not event:
                    continue
                if isinstance(event, dict):
                    comment = str(event.get('comment') or '').strip()
                    date = str(event.get('date') or '').strip()
                    user = str(event.get('user') or '').strip()
                else:
                    comment = ''
                    date = ''
                    user = ''
                rows.append(
                    dict(
                        event=event_key,
                        event_label=event_label,
                        check_type=str(data.get('type') or '').strip(),
                        check_name=str(
                            data.get('name')
                            or check_key
                        ).strip(),
                        comment=comment,
                        date=date,
                        user=user,
                    )
                )
    rows.sort(
        key=lambda item: (
            str(item.get('date') or ''),
            str(item.get('check_type') or ''),
            str(item.get('check_name') or ''),
            str(item.get('event') or ''),
        ),
        reverse=True,
    )
    return rows


def _apply_apero_check_result_filter(cards, result_filter):
    """Filter APERO-check cards by computed visible result status."""
    mode = str(result_filter or 'all').strip().lower()
    if mode == 'all':
        return list(cards)
    if mode == 'passed':
        return [
            card for card in cards
            if str(card.get('status') or 'ok') == 'ok'
        ]
    if mode == 'failed':
        return [
            card for card in cards
            if str(card.get('status') or 'ok') == 'failed'
        ]
    return list(cards)


def _get_apero_check_page_payload(
    app,
    profile_data,
    profile_id,
    instrument,
    page_num,
    per_page,
    type_filter,
    result_filter,
    obsdir_filter,
    obsdir_sort,
    show_overridden,
    show_monitored,
    show_passed,
    pages_to_load=1,
):
    """Return paged APERO-check cards and page metadata."""
    checks_root = _checks_root_for_profile(app, profile_data)
    local_data_dir = app._resolve_local_data_dir()
    checks_cfg = checks_core.load_config(local_data_dir)
    ignored_checks = checks_core.load_ignored_checks(local_data_dir)
    override_allowed = checks_core.load_override_allowed(local_data_dir)
    files = checks_core.list_yaml_files(checks_root)
    filtered_paths = _filter_apero_check_paths(
        files, obsdir_filter, obsdir_sort
    )
    # Fast path: default result filter does not need full-card precompute.
    mode = str(result_filter or 'all').strip().lower()
    if mode == 'all':
        total_cards = len(filtered_paths)
        total_pages = max(1, (total_cards + per_page - 1) // per_page)
        page_num = max(1, min(page_num, total_pages))
        pages_to_load = max(1, min(int(pages_to_load or 1), 2))
        page_cards = dict()
        last_page = min(total_pages, page_num + pages_to_load - 1)
        for current_page in range(page_num, last_page + 1):
            start = (current_page - 1) * per_page
            end = start + per_page
            paths = filtered_paths[start:end]
            cards = []
            for path in paths:
                cards.append(
                    _build_apero_check_summary(
                        path,
                        profile_id,
                        instrument,
                        type_filter,
                        show_overridden,
                        show_monitored,
                        show_passed,
                        ignored_checks,
                    )
                )
            page_cards[current_page] = cards
    else:
        all_cards = []
        for path in filtered_paths:
            all_cards.append(
                _build_apero_check_summary(
                    path,
                    profile_id,
                    instrument,
                    type_filter,
                    show_overridden,
                    show_monitored,
                    show_passed,
                    ignored_checks,
                )
            )
        filtered_cards = _apply_apero_check_result_filter(
            all_cards,
            mode,
        )
        total_cards = len(filtered_cards)
        total_pages = max(1, (total_cards + per_page - 1) // per_page)
        page_num = max(1, min(page_num, total_pages))
        pages_to_load = max(1, min(int(pages_to_load or 1), 2))
        page_cards = dict()
        last_page = min(total_pages, page_num + pages_to_load - 1)
        for current_page in range(page_num, last_page + 1):
            start = (current_page - 1) * per_page
            end = start + per_page
            cards = filtered_cards[start:end]
            page_cards[current_page] = cards
    payload = dict()
    payload['checks_root'] = str(checks_root)
    payload['checks_config'] = checks_cfg
    payload['ignored_checks'] = ignored_checks
    payload['override_allowed'] = override_allowed
    payload['page'] = page_num
    payload['per_page'] = per_page
    payload['total_cards'] = total_cards
    payload['total_pages'] = total_pages
    payload['pages'] = page_cards
    return payload


def _get_apero_check_page_payload_minimal(
    app,
    profile_data,
    per_page,
    page_num,
    obsdir_filter,
    obsdir_sort,
    result_filter,
):
    """Return paged minimal obsdir cards (file metadata only)."""
    checks_root = _checks_root_for_profile(app, profile_data)
    ignored_checks = checks_core.load_ignored_checks(
        app._resolve_local_data_dir()
    )
    files = checks_core.list_yaml_files(checks_root)
    filtered_paths = _filter_apero_check_paths(
        files, obsdir_filter, obsdir_sort
    )
    mode = str(result_filter or 'all').strip().lower()
    if mode == 'all':
        total_cards = len(filtered_paths)
        total_pages = max(
            1, (total_cards + per_page - 1) // per_page
        )
        page_num = max(1, min(page_num, total_pages))
        start = (page_num - 1) * per_page
        end = start + per_page
        paths = filtered_paths[start:end]
        cards = [
            _build_apero_check_minimal_with_status(p, ignored_checks)
            for p in paths
        ]
    else:
        all_cards = [
            _build_apero_check_minimal_with_status(p, ignored_checks)
            for p in filtered_paths
        ]
        filtered_cards = _apply_apero_check_result_filter(
            all_cards,
            mode,
        )
        total_cards = len(filtered_cards)
        total_pages = max(
            1, (total_cards + per_page - 1) // per_page
        )
        page_num = max(1, min(page_num, total_pages))
        start = (page_num - 1) * per_page
        end = start + per_page
        cards = filtered_cards[start:end]
    return {
        'checks_root': str(checks_root),
        'page': page_num,
        'per_page': per_page,
        'total_cards': total_cards,
        'total_pages': total_pages,
        'cards': cards,
    }


def monitor_apero_checks_profile_view(app, profile_id):
    """Render the APERO checks obsdir card page for one profile."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    groups = user_info.get('groups', []) if user_info else []
    prof = None
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            prof = item
            break
    if prof is None:
        flash('Profile not found or access denied.', 'warning')
        return redirect(url_for('monitor_apero_checks_view'))

    page_args = _normalize_apero_checks_args(request.args)

    profile_data = prof['data']
    payload = _get_apero_check_page_payload_minimal(
        app,
        profile_data,
        page_args['per_page'],
        page_args['page_num'],
        page_args['obsdir_filter'],
        page_args['obsdir_sort'],
        page_args['result_filter'],
    )

    page_id = f'home.monitor_portal.apero_checks.{profile_id}'
    sidebar_page_id = 'home.monitor_portal.apero_checks'
    context = {
        'page_id': page_id,
        'page_label': f'APERO Checks - {profile_id}',
        'page_icon': 'fa-solid fa-square-check',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'profile_id': profile_id,
        'profile_cards': payload['cards'],
        'current_page': payload['page'],
        'total_pages': payload['total_pages'],
        'total_cards': payload['total_cards'],
        'per_page': payload['per_page'],
        'obsdir_filter': page_args['obsdir_filter'],
        'obsdir_sort': page_args['obsdir_sort'],
        'result_filter': page_args['result_filter'],
        'checks_root': payload['checks_root'],
        'monitor_doc_url': _monitor_docs_url(),
        'can_manage_apero_profiles': _can_manage_apero_profiles(perms),
    }
    try:
        context.update(
            app._build_sidebar_context(sidebar_page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template(
        'monitor_portal/apero_checks_profile_compact.html',
        **context,
    )


def monitor_apero_checks_queue_view(app, profile_id):
    """Render APERO-check queue and history page for one profile."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    prof = None
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            prof = item
            break
    if prof is None:
        flash('Profile not found or access denied.', 'warning')
        return redirect(url_for('monitor_apero_checks_view'))

    page_id = f'home.monitor_portal.apero_checks.{profile_id}.queue'
    sidebar_page_id = 'home.monitor_portal.apero_checks'
    context = {
        'page_id': page_id,
        'page_label': f'APERO Checks Queue - {profile_id}',
        'page_icon': 'fa-solid fa-list-check',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'profile_id': profile_id,
        'instrument': str(prof.get('instrument') or ''),
        'can_manage_checks': _can_manage_apero_profiles(perms),
    }
    try:
        context.update(
            app._build_sidebar_context(sidebar_page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template(
        'monitor_portal/apero_checks_queue.html',
        **context,
    )


def monitor_apero_checks_obsdir_view(app, profile_id, obsdir):
    """Render APERO-check information page for one obsdir YAML."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    prof = None
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            prof = item
            break
    if prof is None:
        flash('Profile not found or access denied.', 'warning')
        return redirect(url_for('monitor_apero_checks_view'))

    profile_data = prof['data']
    checks_root = _checks_root_for_profile(app, profile_data)
    path = checks_root / f'{obsdir}.yaml'
    if not path.exists():
        path = checks_root / f'{obsdir}.yml'
    if not path.exists():
        flash('APERO check YAML not found.', 'warning')
        return redirect(url_for('monitor_apero_checks_profile_view',
                                profile_id=profile_id))

    loaded = checks_core.load_check_file(path)
    page_args = _normalize_apero_checks_args(request.args)
    history = []
    for key, value in loaded.get('history', {}).items():
        row = dict(value)
        row['id'] = key
        history.append(row)
    history.sort(key=lambda item: item.get('date', ''))

    ignored_checks = checks_core.load_ignored_checks(
        app._resolve_local_data_dir()
    )
    summary = checks_core.build_obsdir_summary(
        loaded,
        type_filter=page_args['type_filter'],
        show_overridden=page_args['show_overridden'],
        show_monitored=page_args['show_monitored'],
        show_passed=page_args['show_passed'],
        ignored_checks=ignored_checks,
    )
    base_summary = checks_core.build_obsdir_summary(
        loaded,
        type_filter='all',
        show_overridden=True,
        show_monitored=True,
        show_passed=True,
        ignored_checks=ignored_checks,
    )
    failure_cards = []
    for failure_key, failure in summary.get('visible_failures', []):
        failure_cards.append({
            'key': failure_key,
            'name': failure.get('name', failure_key),
            'type': failure.get('type', ''),
            'message': failure.get('message', ''),
            'override': failure.get('override', {}),
            'monitor': failure.get('monitor', {}),
            'is_overridden': bool(failure.get('override')),
            'is_monitored': bool(failure.get('monitor')),
        })
    pass_cards = []
    for pass_key, check in summary.get('visible_passes', []):
        pass_cards.append({
            'key': pass_key,
            'name': check.get('name', pass_key),
            'type': check.get('type', ''),
            'message': check.get('message', ''),
            'is_passed': True,
        })
    result_state = str(base_summary.get('result_state') or 'failed')
    result_label = str(
        base_summary.get('status_label')
        or ('Passed' if result_state == 'passed' else 'Failed')
    )
    has_overridden = bool(base_summary.get('override_count', 0))
    has_monitored = bool(base_summary.get('monitor_count', 0))
    banner_state = _status_banner_state(
        result_state,
        has_monitored,
        has_overridden,
    )
    if result_state == 'passed' and has_overridden and has_monitored:
        override_count = int(base_summary.get('override_count', 0) or 0)
        monitor_count = int(base_summary.get('monitor_count', 0) or 0)
        if override_count == monitor_count:
            banner_state = 'overridden_monitored'
        elif override_count > monitor_count:
            banner_state = 'overridden'
        else:
            banner_state = 'monitored'
    monitoring_rows = _monitoring_override_rows(loaded, ignored_checks)

    page_id = f'home.monitor_portal.apero_checks.{profile_id}.{obsdir}'
    sidebar_page_id = 'home.monitor_portal.apero_checks'
    can_advanced = _can_see_apero_checks_advanced(
        perms,
        user_info.get('groups', []) if user_info else [],
    )
    can_delete = _can_manage_apero_profiles(perms)
    context = {
        'page_id': page_id,
        'page_label': f'APERO Checks - {profile_id}',
        'page_icon': 'fa-solid fa-square-check',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'profile_id': profile_id,
        'obsdir': obsdir,
        'checks_file': str(path),
        'result_state': result_state,
        'result_label': result_label,
        'banner_state': banner_state,
        'last_run': summary.get('last_run', ''),
        'check_history': history,
        'failure_cards': failure_cards,
        'pass_cards': pass_cards,
        'ignored_checks': sorted(ignored_checks),
        'type_filter': page_args['type_filter'],
        'show_overridden': page_args['show_overridden'],
        'show_monitored': page_args['show_monitored'],
        'show_passed': page_args['show_passed'],
        'current_page': page_args['page_num'],
        'per_page': page_args['per_page'],
        'obsdir_filter': page_args['obsdir_filter'],
        'obsdir_sort': page_args['obsdir_sort'],
        'can_advanced_checks': can_advanced,
        'can_delete_checks': can_delete,
        'monitor_doc_url': _monitor_docs_url(),
        'monitoring_rows': monitoring_rows,
        'api_rerun_night_url': url_for('api_apero_checks_rerun_night'),
        'api_issue_url': url_for('api_apero_checks_create_issue'),
        'api_view_yaml_url': url_for('api_apero_checks_view_yaml'),
    }
    try:
        context.update(
            app._build_sidebar_context(sidebar_page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template(
        'monitor_portal/apero_checks_obsdir_info.html',
        **context,
    )


def monitor_apero_checks_check_view(
    app,
    profile_id,
    obsdir,
    check_key,
):
    """Render APERO-check information page for one check key."""
    user_info = get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups
        )
    else:
        perms = get_public_permissions()
    if not _has_any_monitor_perm(perms):
        flash('Monitor access required.', 'warning')
        return redirect(url_for('login'))

    prof = None
    for item in get_accessible_profiles(user_info, app.ari_groups):
        if item['profile_id'] == profile_id:
            prof = item
            break
    if prof is None:
        flash('Profile not found or access denied.', 'warning')
        return redirect(url_for('monitor_apero_checks_view'))

    profile_data = prof['data']
    checks_root = _checks_root_for_profile(app, profile_data)
    path = checks_root / f'{obsdir}.yaml'
    if not path.exists():
        path = checks_root / f'{obsdir}.yml'
    if not path.exists():
        flash('APERO check YAML not found.', 'warning')
        return redirect(
            url_for(
                'monitor_apero_checks_obsdir_view',
                profile_id=profile_id,
                obsdir=obsdir,
            )
        )

    loaded = checks_core.load_check_file(path)
    key = str(check_key or '').strip()
    ignored_checks = set(
        checks_core.load_ignored_checks(app._resolve_local_data_dir())
    )
    if key in ignored_checks:
        flash('This check is ignored by policy.', 'warning')
        return redirect(
            url_for(
                'monitor_apero_checks_obsdir_view',
                profile_id=profile_id,
                obsdir=obsdir,
            )
        )

    failure = loaded.get('failures', {}).get(key)
    passed = loaded.get('passes', {}).get(key)
    if not isinstance(failure, dict) and not isinstance(passed, dict):
        flash('APERO check key not found.', 'warning')
        return redirect(
            url_for(
                'monitor_apero_checks_obsdir_view',
                profile_id=profile_id,
                obsdir=obsdir,
            )
        )

    page_id = (
        f'home.monitor_portal.apero_checks.{profile_id}.{obsdir}.{key}'
    )
    sidebar_page_id = 'home.monitor_portal.apero_checks'
    data = failure if isinstance(failure, dict) else passed
    kind = 'failed' if isinstance(failure, dict) else 'passed'
    check_is_overridden = bool(data.get('override'))
    check_is_monitored = bool(data.get('monitor'))
    banner_state = _status_banner_state(
        kind,
        check_is_monitored,
        check_is_overridden,
    )
    override_allowed = checks_core.load_override_allowed(
        app._resolve_local_data_dir()
    )
    context = {
        'page_id': page_id,
        'page_label': f'APERO Checks - {profile_id}',
        'page_icon': 'fa-solid fa-square-check',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'profile_id': profile_id,
        'obsdir': obsdir,
        'check_key': key,
        'check_data': data,
        'check_kind': kind,
        'banner_state': banner_state,
        'checks_file': str(path),
        'last_run': checks_core.format_last_run_display(
            checks_core._latest_history_date(loaded.get('history', {}))
            or checks_core._iso_from_mtime(str(path))
        ),
        'override_allowed': override_allowed,
        'can_manage_checks': _can_manage_apero_profiles(perms),
        'doc_url': _monitor_check_docs_url(key),
        'api_update_url': url_for('api_apero_checks_update_failure'),
        'api_rerun_check_url': url_for('api_apero_checks_rerun_single_check'),
        'api_view_yaml_url': url_for('api_apero_checks_view_yaml'),
    }
    context.update(
        {
            'check_logic_markdown': '',
            'check_logic_html': '',
        }
    )
    try:
        logic_payload = _monitor_profile_logic_payload(key, profile_data)
        context['check_logic_markdown'] = str(
            logic_payload.get('markdown') or ''
        )
        context['check_logic_html'] = str(logic_payload.get('html') or '')
    except Exception:
        pass
    try:
        context.update(
            app._build_sidebar_context(sidebar_page_id, perms, user_info)
        )
    except Exception:
        pass
    return render_template(
        'monitor_portal/apero_checks_check_info.html',
        **context,
    )
