#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Profile-free access, filter, plotting and PDF tests for user statistics."""
from types import SimpleNamespace
from typing import Any
from pathlib import Path
from datetime import date
import json

from flask import Flask
from jinja2 import ChoiceLoader, DictLoader
import pytest
import yaml

from apero.dev import get_base_params
from aperocore.base import base
from apero_ri.application import user_statistics_helpers as helpers


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_user_statistics_views'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_PARAMS = get_base_params('SPIROU')
_ROOT = Path(__file__).resolve().parents[1] / 'apero_ri'


# =============================================================================
# Define functions
# =============================================================================
@pytest.mark.parametrize('user,perms,status', [
    (None, set(), 401),
    (dict(groups=['moderator.SPIROU']), {'view.admin'}, 403),
    (dict(groups=['admin']), {helpers.PERMISSION}, 200),
])
def test_dedicated_permission(monkeypatch: pytest.MonkeyPatch,
                              user: Any, perms: set[str], status: int) -> None:
    """Reject portal-only permission before any statistics are read.

    :param monkeypatch: Authentication replacement fixture.
    :param user: Effective account or unauthenticated None.
    :param perms: Effective permissions.
    :param status: Expected HTTP status.
    :return: None.
    """
    app = Flask(__name__)
    app.secret_key = 'statistics-test-only'
    owner = SimpleNamespace(ari_groups=dict())
    monkeypatch.setattr(helpers.auth, 'get_effective_user', lambda sess: user)
    monkeypatch.setattr(helpers.permissions, 'resolve_user_permissions',
                        lambda groups, config: perms)

    def protected() -> str:
        """Exercise the shared permission gate.

        :return: A success marker after authorization.
        """
        helpers._require_statistics(owner)
        return 'ok'

    app.add_url_rule('/statistics', view_func=protected)
    assert app.test_client().get('/statistics').status_code == status


@pytest.fixture()
def statistics_app(monkeypatch: pytest.MonkeyPatch,
                   tmp_path: Path) -> tuple[Flask, dict]:
    """Build isolated routes using real core reads and real plotting.

    :param monkeypatch: Authentication and report persistence replacement.
    :param tmp_path: Empty data directory; core reads must not create a store.
    :return: Flask application and mutable access state.
    """
    from apero_ri.application.application import ARIApp
    from apero_ri.core import fail_report

    app = Flask(__name__, template_folder=str(_ROOT / 'templates'),
                static_folder=str(_ROOT / 'static'))
    app.secret_key = 'statistics-isolated'
    app.config['TESTING'] = True
    state = dict(user=dict(groups=['admin']), perms={helpers.PERMISSION},
                 stored=[])
    monkeypatch.setattr(helpers.auth, 'get_effective_user',
                        lambda sess: state['user'])
    monkeypatch.setattr(helpers.permissions, 'resolve_user_permissions',
                        lambda groups, config: state['perms'])
    monkeypatch.setattr(helpers.auth, 'load_users',
                        lambda: dict(admin=dict(), reader=dict()))
    monkeypatch.setattr(fail_report, 'store_report_pdf',
                        lambda payload, meta: state['stored'].append(payload))
    owner = SimpleNamespace(ari_groups=dict(),
                            _resolve_local_data_dir=lambda: tmp_path,
                            _build_sidebar_context=lambda *values: dict())
    loader = app.jinja_loader
    shell = ('<!doctype html><html><head><meta name="viewport" '
             'content="width=device-width, initial-scale=1">'
             '<link rel="stylesheet" href="/static/css/style.css">'
             '{% block extra_head %}{% endblock %}</head><body>'
             '{% block doc_content %}{% endblock %}'
             '{% block extra_scripts %}{% endblock %}</body></html>')
    app.jinja_env.loader = ChoiceLoader([
        DictLoader({'general/sidebar_base.html': shell}), loader])
    app.add_url_rule('/admin_portal/user_statistics',
                     'admin_user_statistics_view',
                     lambda: ARIApp._admin_user_statistics_view(owner))
    app.add_url_rule('/api/admin/user-statistics',
                     'api_admin_user_statistics',
                     lambda: ARIApp._api_admin_user_statistics(owner))
    app.add_url_rule('/api/admin/user-statistics/pdf',
                     'api_admin_user_statistics_pdf',
                     lambda: ARIApp._api_admin_user_statistics_pdf(owner))
    app.add_url_rule('/api/admin/user-statistics/reset',
                     'api_admin_user_statistics_reset',
                     lambda: ARIApp._api_admin_user_statistics_reset(owner),
                     methods=['POST'])
    return app, state


def test_reset_requires_permission_and_csrf(
    statistics_app: tuple[Flask, dict], tmp_path: Path,
) -> None:
    """Only a non-impersonating authorized session can clear activity.

    :param statistics_app: Isolated app and access state.
    :param tmp_path: Isolated activity data root.
    :return: None.
    """
    app, state = statistics_app
    client = app.test_client()
    record = helpers.user_statistics.record_page_view
    record(tmp_path, 'alice', '/one')
    record(tmp_path, 'alice', '/two')
    url = '/api/admin/user-statistics/reset'
    assert client.post(url).status_code == 403
    with client.session_transaction() as sess:
        sess['statistics_reset_csrf'] = 'test-token'
    headers = {'X-CSRF-Token': 'test-token'}
    state['perms'] = {'view.admin'}
    assert client.post(url, headers=headers).status_code == 403
    state['perms'] = {helpers.PERMISSION}
    with client.session_transaction() as sess:
        sess['login_as'] = 'someone'
    assert client.post(url, headers=headers).status_code == 403
    with client.session_transaction() as sess:
        sess.pop('login_as')
    assert helpers.user_statistics.summary(tmp_path)['total_user_days'] == 1
    response = client.post(url, headers=headers)
    assert response.status_code == 200
    assert response.json['removed'] == 1
    assert helpers.user_statistics.summary(tmp_path)['total_user_days'] == 0


@pytest.mark.parametrize('path', ['/admin_portal/user_statistics',
                                 '/api/admin/user-statistics',
                                 '/api/admin/user-statistics/pdf'])
def test_all_routes_protected(statistics_app: tuple[Flask, dict],
                              path: str) -> None:
    """Gate every route independently with the dedicated permission.

    :param statistics_app: Isolated app and access state.
    :param path: Protected route under test.
    :return: None.
    """
    app, state = statistics_app
    state['perms'] = {'view.admin'}
    assert app.test_client().get(path).status_code == 403
    state['user'] = None
    assert app.test_client().get(path).status_code == 401
    assert state['stored'] == []


def test_summary_plots_and_pdf(statistics_app: tuple[Flask, dict]) -> None:
    """Use real core zero weeks, map geometry and filtered PDF generation.

    :param statistics_app: Isolated app and access state.
    :return: None.
    """
    app, state = statistics_app
    client = app.test_client()
    query = '?start=2026-10-25&end=2026-11-11&theme=dark'
    response = client.get('/api/admin/user-statistics' + query)
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'private, no-store'
    payload = response.json
    assert payload['summary']['calendar_days'] == 18
    assert payload['summary']['registered_users'] == 2
    assert len(payload['summary']['weekly']) == 4
    assert payload['summary']['total_user_days'] == 0
    serialized = json.dumps(payload['plots'])
    assert 'MultiPolygons' in serialized
    assert 'Canada' in serialized
    assert '#161b22' in serialized
    response = client.get('/api/admin/user-statistics/pdf' + query)
    assert response.status_code == 200
    assert response.data.startswith(b'%PDF')
    assert '2026-10-25-2026-11-11.pdf' in response.headers[
        'Content-Disposition']
    assert state['stored'] == [response.data]


@pytest.mark.parametrize('query', ['start=bad',
                                  'start=2026-11-12&end=2026-11-01'])
@pytest.mark.parametrize('suffix', ['', '/pdf'])
def test_invalid_filters(statistics_app: tuple[Flask, dict], query: str,
                         suffix: str) -> None:
    """Reject invalid and reversed dates for both export and JSON routes.

    :param statistics_app: Isolated app and access state.
    :param query: Invalid date filter query string.
    :param suffix: Optional PDF route suffix.
    :return: None.
    """
    app, state = statistics_app
    url = '/api/admin/user-statistics' + suffix + '?' + query
    assert app.test_client().get(url).status_code == 400
    assert state['stored'] == []


def test_page(statistics_app: tuple[Flask, dict]) -> None:
    """Render date controls, local Bokeh resources and escaped UI config.

    :param statistics_app: Isolated app and access state.
    :return: None.
    """
    app, state = statistics_app
    response = app.test_client().get('/admin_portal/user_statistics')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="us-world"' in html
    assert 'id="us-range-start"' in html
    assert 'window.USER_STATISTICS' in html
    assert 'cdn.bokeh.org' not in html


def test_permission_registration() -> None:
    """Grant statistics only to admin and its super-admin ancestor.

    :return: None.
    """
    resources = _ROOT / 'resources'
    groups = yaml.safe_load((resources / 'groups.yaml').read_text())
    pages = yaml.safe_load((resources / 'pages.yaml').read_text())
    for group in ('admin', 'super_admin'):
        perms = helpers.permissions.resolve_user_permissions([group], groups)
        assert helpers.PERMISSION in perms
    for group in groups:
        if group not in ('admin', 'super_admin'):
            resolved = helpers.permissions.resolve_user_permissions(
                [group], groups)
            assert helpers.PERMISSION not in resolved
    assert pages[helpers.PAGE_ID]['view-permission'] == helpers.PERMISSION
    assert pages[helpers.PAGE_ID]['parent'] == 'home.admin_portal'


@pytest.mark.parametrize('language,heading', [
    ('en', 'User Statistics'), ('fr', 'Statistiques des utilisateurs'),
    ('es', 'Estadísticas de usuarios')])
def test_translations(statistics_app: tuple[Flask, dict], language: str,
                       heading: str) -> None:
    """Use request-local translations for labels and JavaScript configuration.

    :param statistics_app: Isolated app and access state.
    :param language: Browser language under test.
    :param heading: Expected translated page title.
    :return: None.
    """
    app, state = statistics_app
    response = app.test_client().get('/admin_portal/user_statistics',
                                     headers={'Accept-Language': language})
    assert heading in response.get_data(as_text=True)


def test_json_model_order(statistics_app: tuple[Flask, dict],
                          monkeypatch: pytest.MonkeyPatch) -> None:
    """Preserve definition-before-reference ordering for Bokeh documents.

    :param statistics_app: Isolated app and access state.
    :param monkeypatch: Replace plotting with an ordering sentinel.
    :return: None.
    """
    app, state = statistics_app
    monkeypatch.setattr(helpers, '_plots',
                        lambda *values: dict(z='definition', a='reference'))
    response = app.test_client().get('/api/admin/user-statistics')
    body = response.get_data(as_text=True)
    assert body.index('"z":') < body.index('"a":')


def test_populated_filters(statistics_app: tuple[Flask, dict],
                           tmp_path: Path) -> None:
    """Filter populated real activity with inclusive endpoints and unknown geo.

    :param statistics_app: Isolated app using the same temporary data root.
    :param tmp_path: Activity data root provided to the app fixture.
    :return: None.
    """
    app, state = statistics_app
    for day in (date(2026, 10, 25), date(2026, 11, 1), date(2026, 11, 11)):
        for path in ('/user_portal', '/data_portal'):
            helpers.user_statistics.record_page_view(
                tmp_path, 'reader', path, day=day, country='CA', region='QC')
    for path in ('/user_portal', '/data_portal'):
        helpers.user_statistics.record_page_view(
            tmp_path, 'unknown', path, day=date(2026, 11, 1))
    client = app.test_client()
    response = client.get('/api/admin/user-statistics'
                           '?start=2026-11-01&end=2026-11-11')
    data = response.json['summary']
    assert data['total_user_days'] == 3
    assert data['unique_users'] == 2
    assert data['calendar_days'] == 11
    assert data['first_day'] == '2026-10-25'
    assert sum(row['user_days'] for row in data['weekly']) == 3
    assert dict(country='', users=1, user_days=1) in data['countries']
    assert data['regions'][0]['region'] == 'QC'


def test_route_registration() -> None:
    """Verify production URL bindings without initializing ARI services.

    :return: None.
    """
    from apero_ri.application import routes

    rules = dict()
    handlers = dict()

    class Recorder:
        """Collect registration calls with stable placeholder delegates."""

        def __getattr__(self, name: str) -> Any:
            """Resolve a handler placeholder or no-op limiter.

            :param name: Requested application attribute.
            :return: Stable placeholder for that attribute.
            """
            if name == '_limiter':
                return SimpleNamespace(
                    limit=lambda rate: lambda handler: handler)
            if name not in handlers:
                handlers[name] = lambda: None
            return handlers[name]

        def add_url_rule(self, rule: str, endpoint: str,
                         view_func: Any, **options: Any) -> None:
            """Record one production URL binding.

            :param rule: Flask URL path.
            :param endpoint: Registered Flask endpoint name.
            :param view_func: Bound handler.
            :param options: Additional Flask registration settings.
            :return: None.
            """
            rules[rule] = endpoint, view_func

    routes.register_static_routes(Recorder())
    expected = [('/admin_portal/user_statistics', 'admin_user_statistics_view'),
                ('/api/admin/user-statistics', 'api_admin_user_statistics'),
                ('/api/admin/user-statistics/pdf',
                 'api_admin_user_statistics_pdf')]
    for path, endpoint in expected:
        assert rules[path] == (endpoint, handlers['_' + endpoint])


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================