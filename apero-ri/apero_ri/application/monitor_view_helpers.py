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
    get_effective_user, get_public_permissions)
from apero_ri.core.permissions import resolve_user_permissions


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

    context = {
        'page_id': 'home.monitor_portal.issues',
        'page_label': 'Issues',
        'page_icon': 'fa-solid fa-flag',
        'sidebar_root': 'home.monitor_portal',
        'sidebar_label': 'Monitor Portal',
        'sidebar_icon': 'fa-solid fa-chart-line',
        'sidebar_url': '/monitor_portal',
        'visibility': visibility,
    }
    return render_template('monitor_portal/issues.html',
                           **context)
