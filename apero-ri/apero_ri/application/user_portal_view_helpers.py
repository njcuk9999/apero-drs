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

from flask import (flash, redirect, render_template,
                   session, url_for)

from apero_ri.core.auth import get_effective_user
from apero_ri.core.auth import load_users
from apero_ri.core.permissions import resolve_user_permissions


__NAME__ = 'apero_ri.application.user_portal_view_helpers'


def _require_logged_in(app, page_id, page_label, page_icon,
                       template):
    """Shared boilerplate for the three user-portal sub-pages."""
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
    return render_template(template, **context)


def user_portal_users_view(app):
    """Render the users directory page."""
    return _require_logged_in(
        app,
        page_id='home.user_portal.users',
        page_label='Users',
        page_icon='fa-solid fa-users',
        template='user_portal/users.html',
    )


def user_portal_messages_view(app):
    """Render the messages inbox page."""
    return _require_logged_in(
        app,
        page_id='home.user_portal.messages',
        page_label='Messages',
        page_icon='fa-solid fa-envelope',
        template='user_portal/messages.html',
    )


def user_portal_notifications_view(app):
    """Render the notifications + preferences page."""
    return _require_logged_in(
        app,
        page_id='home.user_portal.notifications',
        page_label='Notifications',
        page_icon='fa-solid fa-bell',
        template='user_portal/notifications.html',
    )


def user_portal_user_card_view(app, username):
    """Render a dedicated user profile card page."""
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
