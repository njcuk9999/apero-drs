#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - User portal view helpers.

Render small server-side pages for the new notifications + messages
+ users-directory features. The pages themselves are mostly
JavaScript shells that call the corresponding /api/... endpoints.

Created on 2026-04-24

@author: cook
"""
from __future__ import annotations

from typing import Any

from flask import (flash, redirect, render_template,
                   session, url_for)

from pathlib import Path

from aperocore.drs_lang import textentry
from aperocore.drs_lang.tables import default_text
from apero_ri.core import ari_lang_support
from apero_ri.core.auth import get_effective_user
from apero_ri.core.auth import load_users
from apero_ri.core.permissions import resolve_user_permissions
from apero_ri.core import permissions as perms_mod
from apero_ri.core import awards as awards_core
from apero_ri.application.monitor_view_helpers import _has_any_monitor_perm


__NAME__ = 'apero_ri.application.user_portal_view_helpers'


def _download_award_labels() -> dict[str, str]:
    """Return existing award labels in the current request's language.

    :return: Localized download headings and medal names.
    """
    language = ari_lang_support.get_language()
    labels = dict()
    for key, english, french, spanish in default_text.AWARDS_UI_TEXT:
        if key not in ('DOWNLOADS', 'BYTES', 'FILES',
                       'GOLD', 'SILVER', 'BRONZE'):
            continue
        translations = dict(en=english, fr=french, es=spanish)
        label = textentry('AWARDS_' + key, message=translations[language])
        labels[key.lower()] = str(label)
    return labels


def _require_logged_in(
    app: Any,
    page_id: str,
    page_label: str,
    page_icon: str,
    template: str,
) -> Any:
    """Render a user-portal page for the current logged-in user.

    :param app: ARI application providing permissions and sidebar context.
    :param page_id: Registered page identifier used for sidebar context.
    :param page_label: Page title displayed in the rendered template.
    :param page_icon: Icon class displayed with the page title.
    :param template: Template path to render.
    :returns: Rendered response, or a redirect when login is required.
    """
    user_info = get_effective_user(session)
    if not user_info:
        flash('Login required.', 'warning')
        return redirect(url_for('login'))
    try:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    except Exception:
        perms = set()

    context = {
        'page_id': page_id,
        'page_label': page_label,
        'page_icon': page_icon,
        'sidebar_root': 'home.user_portal',
        'sidebar_label': 'User Portal',
        'sidebar_icon': 'fa-solid fa-user',
        'sidebar_url': '/user_portal',
        'username': user_info.get('username'),
    }
    try:
        context.update(
            app._build_sidebar_context(page_id, perms, user_info))
    except Exception:
        pass
    if template == 'user_portal/users.html':
        context['download_award_labels'] = _download_award_labels()
    return render_template(template, **context)


def user_portal_users_view(app: Any) -> Any:
    """Render the users directory page."""
    return _require_logged_in(
        app,
        page_id='home.user_portal.users',
        page_label='Users',
        page_icon='fa-solid fa-users',
        template='user_portal/users.html',
    )


def user_portal_messages_view(app: Any) -> Any:
    """Render the messages inbox page."""
    return _require_logged_in(
        app,
        page_id='home.user_portal.messages',
        page_label='Messages',
        page_icon='fa-solid fa-envelope',
        template='user_portal/messages.html',
    )


def user_portal_notifications_view(app: Any) -> Any:
    """Render the notifications + preferences page."""
    return _require_logged_in(
        app,
        page_id='home.user_portal.notifications',
        page_label='Notifications',
        page_icon='fa-solid fa-bell',
        template='user_portal/notifications.html',
    )


def user_portal_user_card_view(app: Any, username: str) -> Any:
    """Render a dedicated user profile card page.

    :param app: ARI application providing groups and sidebar configuration.
    :param username: Target account whose public profile is requested.
    :return: Rendered profile, or redirect for login or an unknown user.
    """
    user_info = get_effective_user(session)
    if not user_info:
        flash('Login required.', 'warning')
        return redirect(url_for('login'))

    try:
        perms = resolve_user_permissions(
            user_info['groups'], app.ari_groups)
    except Exception:
        perms = set()

    viewer_groups = user_info.get('groups', [])
    if not isinstance(viewer_groups, list):
        viewer_groups = []
    viewer_group_set = {
        str(group).strip().lower()
        for group in viewer_groups
        if str(group).strip()
    }
    viewer_can_view_contact = bool(
        viewer_group_set.intersection(
            {'super_admin', 'admin', 'moderator', 'developer'}
        )
    )

    users = load_users() or {}
    record = users.get(username)
    if not isinstance(record, dict):
        flash('User not found.', 'warning')
        return redirect(url_for('user_portal_users_view'))

    emails = record.get('emails', [])
    if not isinstance(emails, list):
        emails = []
    emails = [str(e).strip() for e in emails if str(e).strip()]

    institutions = record.get('institutions', [])
    if not isinstance(institutions, list):
        institutions = []
    institutions = [
        str(inst).strip()
        for inst in institutions
        if str(inst).strip()
    ]

    first_names = str(record.get('first_names', '')).strip()
    last_name = str(record.get('last_name', '')).strip()

    target_user = {
        'username': username,
        'first_names': first_names,
        'last_name': last_name,
        'full_name': ' '.join(
            [x for x in [first_names, last_name] if x]
        ),
        'groups': record.get('groups', []),
        'instruments': record.get('instruments', []),
        'primary_email': str(record.get('primary_email', '')).strip(),
        'emails': emails,
        'primary_institution': str(
            record.get('primary_institution', '')
        ).strip(),
        'institutions': institutions,
        'last_login': record.get('last_login'),
        'created_at': record.get('created_at'),
        'is_self': (username == user_info.get('username')),
        'viewer_can_view_contact': viewer_can_view_contact,
    }

    monitor_stats = None
    download_stats = None
    try:
        target_perms = resolve_user_permissions(
            record.get('groups', []), app.ari_groups)
    except Exception:
        target_perms = set()
    try:
        data_dir = Path(app.args.data_dir or str(Path.home() / '.ari'))
        instruments = perms_mod.load_parameters().get(
            'instruments', {}).get('value', [])
        all_awards = awards_core.compute_awards(data_dir, instruments)
        entry = all_awards.get(username)
        if entry and (entry.get('download_bytes', 0) > 0
                      or entry.get('download_files', 0) > 0):
            download_stats = entry
        if _has_any_monitor_perm(target_perms):
            monitor_stats = all_awards.get(username, {
                'username': username,
                'who': target_user['full_name'] or username,
                'total_hours': 0.0,
                'instruments': {},
                'instrument_medals': {},
                'service_medal': None,
                'issues_resolved': 0,
                'issues_medal': None,
            })
    except Exception:
        monitor_stats = None
        download_stats = None

    context = {
        'page_id': 'home.user_portal.users',
        'page_label': 'User Card',
        'page_icon': 'fa-solid fa-id-card',
        'sidebar_root': 'home.user_portal',
        'sidebar_label': 'User Portal',
        'sidebar_icon': 'fa-solid fa-user',
        'sidebar_url': '/user_portal',
        'username': user_info.get('username'),
        'target_user': target_user,
        'monitor_stats': monitor_stats,
        'download_stats': download_stats,
        'download_award_labels': _download_award_labels(),
    }
    try:
        context.update(
            app._build_sidebar_context(
                'home.user_portal.users', perms, user_info
            )
        )
    except Exception:
        pass
    return render_template('user_portal/user_card.html', **context)
