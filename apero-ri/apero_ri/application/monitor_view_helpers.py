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

from flask import (flash, redirect, render_template,
                   session, url_for)

from apero_ri.core.auth import (
    get_accessible_profiles,
    get_effective_user,
    get_public_permissions,
)
from apero_ri.core.permissions import resolve_user_permissions
from apero_ri.core import permissions as perms_mod
from apero_ri.application import instrument_color_helpers


__NAME__ = 'apero_ri.application.monitor_view_helpers'


_MONITOR_PERMS = {'view.monitor_portal', 'view.monitor',
                  'manage.astrometrics'}


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
                '/monitor_portal/logs/'
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

    page_id = 'home.monitor_portal.logs'
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
        'home.monitor_portal.logs.'
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
            '/monitor_portal/logs/' + profile_id
        ),
    }
    try:
        context.update(
            app._build_sidebar_context(
                'home.monitor_portal.logs', perms, user_info
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
        'home.monitor_portal.logs.'
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
                'home.monitor_portal.logs', perms, user_info
            )
        )
    except Exception:
        pass
    return render_template(
        'monitor_portal/processing_logs_pid.html',
        **context,
    )
