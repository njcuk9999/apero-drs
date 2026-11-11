#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused rendering checks for download-management user links."""
from pathlib import Path
from typing import Any

import pytest
from flask import Flask, render_template
from jinja2 import ChoiceLoader, DictLoader

from apero import dev


ROOT = Path(__file__).resolve().parents[1] / 'apero_ri'


def build_preview_app() -> Flask:
    """Return an isolated template app with synthetic users and no services."""
    dev.get_base_params('SPIROU')
    app = Flask(__name__, template_folder=str(ROOT / 'templates'),
                static_folder=str(ROOT / 'static'))
    parent = '<!doctype html><html><head>'
    parent += '<meta name="viewport" content="width=device-width">'
    parent += '<link rel="stylesheet" href="/static/css/style.css">'
    parent += '</head><body>{% block doc_content %}{% endblock %}'
    parent += '</body></html>'
    loaders = [DictLoader({'general/sidebar_base.html': parent}),
               app.jinja_loader]
    app.jinja_loader = ChoiceLoader(loaders)
    app.jinja_env.globals['_'] = lambda value: value
    app.add_url_rule('/user_portal/users/<username>',
                     'user_portal_user_card_view', lambda username: username)
    app.add_url_rule('/api/settings', 'api_admin_dm_save_settings',
                     lambda: dict(success=True), methods=['POST'])
    app.add_url_rule('/api/reset', 'api_admin_dm_reset_user',
                     lambda: dict(success=True), methods=['POST'])
    app.add_url_rule('/api/users/directory', 'api_users_directory',
                     preview_directory)
    app.add_url_rule('/', 'preview', lambda: render_preview(app, True))
    return app


def preview_directory() -> dict[str, Any]:
    """Return synthetic public directory data for the browser fixture."""
    alice = dict(username='alice', full_name='Alice Example',
                 primary_institution='Example Observatory', groups=['general'],
                 can_view_contact=False, email='private@example.test')
    bob = dict(username='bob', full_name='Bob Example',
               can_view_contact=True, email='allowed@example.test')
    return dict(success=True, users=[alice, bob])


def render_preview(app: Flask, can_manage: bool) -> str:
    """Render sample usage rows for the given edit-permission state.

    :param app: Isolated Flask application used for URL generation.
    :param can_manage: Whether reset controls should be rendered.
    :return: Rendered download-management HTML.
    """
    rows = []
    for index, username in enumerate(['bob', 'alice', 'deleted']):
        rows.append(dict(username=username, total_bytes=index * 100,
                         total_files=index, last_download_at='',
                         total_size_fmt='0 B', last_download_fmt='Never'))
    settings = dict(api_rate_limit_seconds=2, basket_rate_limit_seconds=0,
                    basket_max_archive_gb=5)
    context = dict(can_manage=can_manage, settings=settings,
                   api_usage=rows, basket_usage=rows, api_total_size='0 B',
                   api_total_files=3, basket_total_size='0 B',
                   basket_total_files=3)
    with app.test_request_context('/'):
        return render_template('admin/download_management.html', **context)


@pytest.mark.parametrize('can_manage', [True, False])
def test_user_links_and_existing_controls(can_manage: bool) -> None:
    """Preserve row sorting and permission-dependent reset controls.

    :param can_manage: Whether the viewer has edit permission.
    :return: None.
    """
    output = render_preview(build_preview_app(), can_manage)
    assert output.count('class="dm-user-link"') == 6
    assert output.count('href="/user_portal/users/alice"') == 2
    assert output.count('data-dm-user="deleted"') == 2
    assert output.count('data-sort="username"') == 2
    assert output.count('data-username="alice"') == 2
    assert 'role="tooltip" hidden' in output
    assert 'download_management_users.js' in output
    assert ('onclick="dmResetUser(' in output) == can_manage
    assert "rows.forEach(function(r){ tbody.appendChild(r); });" in output


def test_template_escapes_username() -> None:
    """Keep user-controlled link text and data attributes HTML-escaped."""
    app = build_preview_app()
    template = app.jinja_env.get_template('admin/download_management.html')
    username = '<img src=x onerror=alert(1)>'
    row = dict(username=username, total_bytes=0, total_files=0,
               last_download_at='', total_size_fmt='0 B',
               last_download_fmt='Never')
    settings = dict(api_rate_limit_seconds=2, basket_rate_limit_seconds=0,
                    basket_max_archive_gb=5)
    with app.test_request_context('/'):
        output = template.render(settings=settings, can_manage=False,
                                 api_usage=[row], basket_usage=[])
    assert username not in output
    assert 'data-dm-user="&lt;img' in output