#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused, profile-free shared awards route and template tests."""
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from flask import Flask
from jinja2 import ChoiceLoader, DictLoader
import yaml

from apero.dev import get_base_params
from aperocore.base import base


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_awards_views'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_PARAMS = get_base_params('SPIROU')
_ROOT = Path(__file__).resolve().parents[1] / 'apero_ri'


# =============================================================================
# Define functions
# =============================================================================
@pytest.fixture()
def awards_app(monkeypatch: pytest.MonkeyPatch,
               tmp_path: Path) -> tuple[Flask, dict[str, Any]]:
    """Build isolated awards routes with deterministic core results.

    :param monkeypatch: Fixture for replacing authentication and computation.
    :param tmp_path: Isolated data directory.
    :return: Flask application and mutable authentication/call state.
    """
    from apero_ri.application import monitor_view_helpers as helpers
    from apero_ri.application.application import ARIApp

    app = Flask(__name__, template_folder=str(_ROOT / 'templates'))
    app.secret_key = 'awards-test-only'
    app.config['TESTING'] = True
    app.jinja_env.filters['tl'] = str
    base_template = (
        '<!doctype html><html><head>'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<link rel="stylesheet" href="/static/css/style.css">'
        '{% block extra_head %}{% endblock %}</head><body>'
        '{% block doc_content %}{% endblock %}'
        '{% block extra_scripts %}{% endblock %}</body></html>')
    loader = app.jinja_loader
    assert loader is not None
    app.jinja_env.loader = ChoiceLoader([
        DictLoader({'general/sidebar_base.html': base_template}), loader,
    ])
    owner: Any = SimpleNamespace(
        args=SimpleNamespace(data_dir=str(tmp_path)), ari_groups=dict())
    state: dict[str, Any] = dict(
        user=dict(username='reader', groups=['general.SPIROU']),
        permissions={'view.user'}, calls=0, contexts=[])

    def sidebar(page_id: str, perms: set[str],
                user: dict[str, Any]) -> dict[str, Any]:
        """Capture sidebar context for permission and portal assertions.

        :param page_id: Registered page identifier.
        :param perms: Effective permission set.
        :param user: Effective authenticated user.
        :return: Empty supplemental sidebar context.
        """
        state['contexts'].append(page_id)
        return dict()

    def compute(data_dir: Path,
                instruments: list[str]) -> dict[str, Any]:
        """Return deterministic awards without files or a database.

        :param data_dir: Expected isolated data directory.
        :param instruments: Configured instrument names.
        :return: Mock core awards, including a download-only user.
        """
        assert data_dir == tmp_path
        assert instruments == ['SPIROU', 'NIRPS']
        state['calls'] += 1
        entry = dict(username='reader', who='Reader', total_hours=123.456,
                     service_medal='silver', issues_resolved=600,
                     issues_medal='silver', download_bytes=4096,
                     download_files=80,
                     download_medals=dict(bytes='gold', files='bronze'),
                     instruments=dict(SPIROU=dict(hours_estimated=12.345)),
                     instrument_medals=dict(SPIROU='gold'))
        downloader = dict(username='</script><script>bad()</script>',
                          download_bytes=8192, download_files=20,
                          download_medals=dict(bytes='silver', files=None))
        return dict(reader=entry, downloader=downloader)

    owner._build_sidebar_context = sidebar
    monkeypatch.setattr(helpers, 'get_effective_user',
                        lambda session: state['user'])
    monkeypatch.setattr(helpers, 'resolve_user_permissions',
                        lambda groups, config: state['permissions'])
    monkeypatch.setattr(helpers, 'get_public_permissions', lambda: set())
    state['accounts'] = dict()
    monkeypatch.setattr(helpers, 'load_users', lambda: state['accounts'])
    parameters = dict(instruments=dict(value=['SPIROU', 'NIRPS']))
    monkeypatch.setattr(helpers.perms_mod, 'load_parameters',
                        lambda: parameters)
    monkeypatch.setattr(helpers.awards_core, 'compute_awards', compute)
    app.add_url_rule('/login', 'login', lambda: 'login')
    app.add_url_rule('/monitor_portal/become_monitor', 'become_monitor_view',
                     lambda: 'monitor')
    app.add_url_rule('/user_portal/awards', 'user_awards_view',
                     lambda: ARIApp._user_awards_view(owner))
    app.add_url_rule('/monitor_portal/awards', 'monitor_awards_view',
                     lambda: ARIApp._monitor_awards_view(owner))
    return app, state


def test_user_awards_access(awards_app: tuple[Flask, dict[str, Any]]) -> None:
    """Enforce view.user before computing awards.

    :param awards_app: Isolated application and authentication state.
    :return: None.
    """
    app, state = awards_app
    client = app.test_client()
    assert client.get('/user_portal/awards').status_code == 200
    assert state['contexts'] == ['home.user_portal.awards']
    state['permissions'] = {'view.home'}
    assert client.get('/user_portal/awards').status_code == 403
    state['user'] = None
    response = client.get('/user_portal/awards')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'
    assert state['calls'] == 1


def test_monitor_awards_access(
    awards_app: tuple[Flask, dict[str, Any]],
) -> None:
    """Preserve monitor restrictions independently of user permissions.

    :param awards_app: Isolated application and authentication state.
    :return: None.
    """
    app, state = awards_app
    client = app.test_client()
    response = client.get('/monitor_portal/awards')
    assert response.status_code == 302
    assert response.headers['Location'] == '/monitor_portal/become_monitor'
    assert state['calls'] == 0
    state['permissions'] = {'monitor.SPIROU'}
    assert client.get('/monitor_portal/awards').status_code == 200
    assert state['contexts'] == ['home.monitor_portal.awards']
    assert client.get('/user_portal/awards').status_code == 403
    state['user'] = None
    assert client.get('/monitor_portal/awards').status_code == 302
    assert state['calls'] == 1


@pytest.mark.parametrize('portal', ['user_portal', 'monitor_portal'])
@pytest.mark.parametrize('account, expected', [
    (dict(first_names=' Ada ', last_name=' Lovelace '), 'Ada Lovelace'),
    (dict(first_names='Ada', last_name=''), 'Ada'),
    (dict(first_names=None, last_name='Lovelace'), 'Lovelace'),
    (dict(first_names=' ', last_name=None), 'reader'),
    (dict(), 'reader'),
])
def test_awards_account_names(
    awards_app: tuple[Flask, dict[str, Any]], portal: str,
    account: dict[str, Any], expected: str,
) -> None:
    """Use current account names instead of schedule names or usernames.

    :param awards_app: Isolated application and authentication state.
    :param portal: Portal serving the shared awards page.
    :param account: Account name fields, potentially absent or blank.
    :param expected: Expected display name in the leaderboard payload.
    :return: None.
    """
    app, state = awards_app
    state['permissions'] = {'view.user', 'monitor.SPIROU'}
    state['accounts']['reader'] = account
    downloader = '</script><script>bad()</script>'
    state['accounts'][downloader] = dict(
        first_names='Download', last_name='User')
    html = app.test_client().get(f'/{portal}/awards').get_data(as_text=True)
    payload = html.split('<script id="aw-data" type="application/json">')[1]
    rows = json.loads(payload.split('</script>')[0])
    assert rows[0]['who'] == expected
    assert rows[1]['who'] == 'Download User'


def test_awards_template_payload(
    awards_app: tuple[Flask, dict[str, Any]],
) -> None:
    """Keep download fields, instrument sections, and safely embedded JSON.

    :param awards_app: Isolated application and authentication state.
    :return: None.
    """
    app, state = awards_app
    html = app.test_client().get('/user_portal/awards').get_data(as_text=True)
    assert html.count('data-aw-kind="instrument"') == 2
    assert 'data-aw-instrument="SPIROU"' in html
    assert 'data-aw-instrument="NIRPS"' in html
    assert 'id="aw-downloads"' in html
    assert 'data-aw-kind="bytes"' in html
    assert 'data-aw-kind="files"' in html
    assert 'data-aw-kind="service"' in html
    assert '</script><script>bad()' not in html
    payload = html.split('<script id="aw-data" type="application/json">')[1]
    rows = json.loads(payload.split('</script>')[0])
    assert rows[0]['download_medals'] == dict(bytes='gold', files='bronze')
    assert rows[0]['download_bytes'] == 4096
    assert rows[0]['download_files'] == 80
    assert rows[0]['service_medal'] == 'silver'
    assert rows[0]['issues_medal'] == 'silver'
    assert rows[0]['instruments'] == dict(SPIROU=12.35)
    assert rows[1]['total_hours'] == 0


@pytest.mark.parametrize('language, heading', [
    ('en', 'Downloads'), ('fr', 'Téléchargements'), ('es', 'Descargas'),
])
def test_awards_request_language(
    awards_app: tuple[Flask, dict[str, Any]], language: str, heading: str,
) -> None:
    """Translate section and JavaScript labels per request.

    :param awards_app: Isolated application and authentication state.
    :param language: Requested browser language.
    :param heading: Expected localized downloads heading.
    :return: None.
    """
    app, state = awards_app
    response = app.test_client().get('/user_portal/awards',
                                     headers={'Accept-Language': language})
    assert heading in response.get_data(as_text=True)


def test_awards_navigation_permissions() -> None:
    """Register both portals and inherit user access without public grants.

    :return: None.
    """
    from apero_ri.core.permissions import resolve_user_permissions

    resources = _ROOT / 'resources'
    pages = yaml.safe_load((resources / 'pages.yaml').read_text())
    groups = yaml.safe_load((resources / 'groups.yaml').read_text())
    page = pages['home.user_portal.awards']
    assert page['parent'] == 'home.user_portal'
    assert page['view-permission'] == 'view.user'
    assert page['side-nav']['show'] is True
    assert pages['home.monitor_portal.awards']['view-permission'] == 'monitor'
    for group in ['general.SPIROU', 'general.NIRPS', 'monitor.SPIROU']:
        assert 'view.user' in resolve_user_permissions([group], groups)
    assert 'view.user' not in resolve_user_permissions(['public'], groups)


def test_awards_url_registration() -> None:
    """Verify production route registration selects the correct delegates.

    :return: None.
    """
    from apero_ri.application import routes

    rules = dict()
    handlers: dict[str, Any] = dict()

    class Recorder:
        """Record URL rules without constructing an RI application."""

        def __getattr__(self, name: str) -> Any:
            """Return a stable stand-in for an application handler.

            :param name: Requested application handler name.
            :return: Callable stand-in.
            """
            if name == '_limiter':
                return SimpleNamespace(
                    limit=lambda rate: lambda handler: handler)
            if name not in handlers:
                handlers[name] = lambda: None
            return handlers[name]

        def add_url_rule(self, rule: str, endpoint: str,
                         view_func: Any, **options: Any) -> None:
            """Capture a production route registration.

            :param rule: URL path.
            :param endpoint: Flask endpoint name.
            :param view_func: Application handler.
            :param options: Additional Flask registration options.
            :return: None.
            """
            rules[rule] = (endpoint, view_func)

    routes.register_data_portal_routes(Recorder())
    assert rules['/user_portal/awards'] == (
        'user_awards_view', handlers['_user_awards_view'])
    assert rules['/monitor_portal/awards'] == (
        'monitor_awards_view', handlers['_monitor_awards_view'])


def test_awards_standalone_preview(
    awards_app: tuple[Flask, dict[str, Any]], tmp_path: Path,
) -> None:
    """Render a temporary standalone page for isolated browser validation.

    :param awards_app: Isolated application and authentication state.
    :param tmp_path: Temporary preview directory.
    :return: None.
    """
    app, state = awards_app
    response = app.test_client().get('/user_portal/awards')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    static_url = (_ROOT / 'static').as_uri() + '/'
    html = html.replace('/static/', static_url)
    preview = tmp_path / 'awards-preview.html'
    preview.write_text(html, encoding='utf-8')
    assert html.count('class="aw-board"') == 6
    print(f'Awards browser preview: {preview}')


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================