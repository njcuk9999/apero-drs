#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Profile-free user directory and profile download award tests."""
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
from typing import Any

import pytest
from flask import Flask
from jinja2 import ChoiceLoader, DictLoader

from apero.dev import get_base_params
from aperocore.base import base
from aperocore.drs_lang.tables import default_text
from apero_ri.application import notifications_api_helpers as api
from apero_ri.application import user_portal_view_helpers as views


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_user_download_awards'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_PARAMS = get_base_params('SPIROU')
_ROOT = Path(__file__).resolve().parents[1] / 'apero_ri'


# =============================================================================
# Define functions
# =============================================================================
@pytest.fixture()
def portal_app(monkeypatch: pytest.MonkeyPatch,
               tmp_path: Path) -> tuple[Flask, dict[str, Any]]:
    """Build isolated user routes with deterministic authentication and awards.

    :param monkeypatch: Fixture restoring replaced users and computation.
    :param tmp_path: Isolated application data directory.
    :return: Test application and mutable viewer/award state.
    """
    app = Flask(__name__, template_folder=str(_ROOT / 'templates'))
    app.secret_key = 'user-awards-test-only'
    app.config['TESTING'] = True
    app.jinja_env.filters['tl'] = str
    shell = ('{% block extra_head %}{% endblock %}'
             '{% block doc_content %}{% endblock %}'
             '{% block extra_scripts %}{% endblock %}')
    loader = app.jinja_loader
    assert loader is not None
    app.jinja_env.loader = ChoiceLoader([
        DictLoader({'general/sidebar_base.html': shell}), loader])
    entry = dict(download_bytes=4096, download_files=8,
                 download_medals=dict(bytes='gold', files='silver'),
                 total_hours=12, instruments=dict(),
                 instrument_medals=dict(), service_medal=None,
                 issues_resolved=3, issues_medal=None)
    zero = dict(entry, download_bytes=0, download_files=0,
                download_medals=dict(bytes=None, files=None))
    state = dict(user=dict(username='viewer', groups=['general']), calls=0,
                 awards=dict(reader=entry, monitor=entry, staff=entry,
                             zero=zero), fail=False)
    users = dict()
    for username, group in [('reader', 'general'), ('monitor', 'monitor'),
                            ('staff', 'admin'), ('zero', 'general'),
                            ('missing', 'general')]:
        users[username] = dict(groups=[group], first_names='Test',
                               primary_email='private@example.test',
                               emails=['private@example.test'])
    owner = SimpleNamespace(
        args=SimpleNamespace(data_dir=str(tmp_path)), ari_groups=dict(),
        _require_user=lambda: state['user'],
        _build_sidebar_context=lambda *sidebar_args: dict())

    def compute(directory: Path,
                instruments: list[str]) -> dict[str, Any]:
        """Return fixture awards without accessing a profile or database.

        :param directory: Isolated application data directory.
        :param instruments: Configured instrument list.
        :return: Deterministic awards keyed by username.
        """
        assert directory == tmp_path
        assert instruments == ['SPIROU']
        state['calls'] += 1
        if state['fail']:
            raise RuntimeError('test computation failure')
        return state['awards']

    monkeypatch.setattr(views, 'get_effective_user',
                        lambda session: state['user'])
    monkeypatch.setattr(views, 'load_users', lambda: users)
    monkeypatch.setattr(api.auth, 'load_users', lambda: users)
    monkeypatch.setattr(views, 'resolve_user_permissions',
                        lambda groups, config: {'monitor.SPIROU'}
                        if 'monitor' in groups else {'view.user'})
    monkeypatch.setattr(views.awards_core, 'compute_awards', compute)
    monkeypatch.setattr(api, '_AWARDS_CACHE', dict())
    parameters = dict(instruments=dict(value=['SPIROU']))
    monkeypatch.setattr(views.perms_mod, 'load_parameters',
                        lambda: parameters)
    app.add_url_rule('/login', 'login', lambda: 'login')
    app.add_url_rule('/users', 'user_portal_users_view',
                     lambda: views.user_portal_users_view(owner))
    app.add_url_rule('/messages', 'user_portal_messages_view',
                     lambda: 'messages')
    app.add_url_rule('/users/<username>', 'user_card',
                     lambda username: views.user_portal_user_card_view(
                         owner, username))
    app.add_url_rule('/api/users/directory', 'directory',
                     lambda: api.api_users_directory(owner))
    return app, state


def test_directory_download_summary() -> None:
    """Keep public download totals and medals without copying private fields.

    :return: None.
    """
    entry = dict(download_bytes=4096, download_files=8,
                 download_medals=dict(bytes='gold', files='silver'),
                 email='private@example.test', token='private-token')
    summary = api._user_award_summary(dict(reader=entry), 'reader')
    assert summary['download_bytes'] == 4096
    assert summary['download_files'] == 8
    assert summary['download_medals'] == entry['download_medals']
    assert 'email' not in summary
    assert 'token' not in summary
    assert summary['service_medal'] is None
    missing = api._user_award_summary(dict(), 'missing')
    assert missing['download_bytes'] == 0
    assert missing['download_files'] == 0
    assert missing['download_medals'] == dict(bytes=None, files=None)


@pytest.mark.parametrize('username', ['reader', 'monitor'])
def test_profile_download_awards(
    portal_app: tuple[Flask, dict[str, Any]], username: str,
) -> None:
    """Show download medals without granting monitoring statistics access.

    :param portal_app: Isolated application and mutable viewer state.
    :param username: Download-only user or monitor.
    :return: None.
    """
    app, state = portal_app
    response = app.test_client().get('/users/' + username)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '4096 B' in html
    assert 'upu-medal--gold' in html
    assert 'upu-medal--silver' in html
    assert ('Monitoring statistics' in html) == (username == 'monitor')
    assert 'private@example.test' not in html
    assert state['calls'] == 1


@pytest.mark.parametrize('username', ['zero', 'missing'])
def test_profile_no_download_activity(
    portal_app: tuple[Flask, dict[str, Any]], username: str,
) -> None:
    """Do not create download awards for absent or zero totals.

    :param portal_app: Isolated application and viewer state.
    :param username: Account with no positive download activity.
    :return: None.
    """
    app, state = portal_app
    html = app.test_client().get('/users/' + username).get_data(as_text=True)
    assert 'fa-download' not in html
    assert 'upu-medal--gold' not in html
    assert 'Monitoring statistics' not in html


@pytest.mark.parametrize('language', ['en', 'fr', 'es'])
def test_download_labels(
    portal_app: tuple[Flask, dict[str, Any]], language: str,
) -> None:
    """Reuse core translations per request in both profile and directory.

    :param portal_app: Isolated application and viewer state.
    :param language: Requested browser language.
    :return: None.
    """
    app, state = portal_app
    client = app.test_client()
    language_index = dict(en=1, fr=2, es=3)[language]
    labels = dict((row[0], row[language_index])
                  for row in default_text.AWARDS_UI_TEXT)
    for path in ['/users/reader', '/users']:
        response = client.get(path, headers={'Accept-Language': language})
        html = response.get_data(as_text=True)
        if path == '/users':
            import json
            payload = html.split('window.USER_DOWNLOAD_AWARD_LABELS = ')[1]
            data = json.loads(payload.split(';</script>')[0])
            assert data['bytes'] == labels['BYTES']
            assert data['files'] == labels['FILES']
            assert data['gold'] == labels['GOLD']
            assert 'v=20261111a' in html
        else:
            assert labels['BYTES'] in html
            assert labels['FILES'] in html
            assert labels['DOWNLOADS'] in html
            assert labels['GOLD'] in html


@pytest.mark.parametrize('privileged', [False, True])
def test_contact_visibility(
    portal_app: tuple[Flask, dict[str, Any]], privileged: bool,
) -> None:
    """Download awards must not widen directory or profile contact visibility.

    :param portal_app: Isolated application and viewer state.
    :param privileged: Whether the viewer belongs to an existing staff role.
    :return: None.
    """
    app, state = portal_app
    state['user']['groups'] = ['admin'] if privileged else ['general']
    client = app.test_client()
    response = client.get('/api/users/directory')
    rows = response.get_json()['users']
    reader = next(row for row in rows if row['username'] == 'reader')
    assert reader['awards']['download_bytes'] == 4096
    assert reader['awards']['download_medals']['bytes'] == 'gold'
    assert bool(reader['email']) == privileged
    assert bool(reader['emails']) == privileged
    html = client.get('/users/staff').get_data(as_text=True)
    assert ('private@example.test' in html) == privileged
    assert '4096 B' in html


def test_user_awards_require_login(
    portal_app: tuple[Flask, dict[str, Any]],
) -> None:
    """Reject signed-out users before any awards computation.

    :param portal_app: Isolated application and viewer state.
    :return: None.
    """
    app, state = portal_app
    state['user'] = None
    client = app.test_client()
    assert client.get('/api/users/directory').status_code == 401
    for path in ['/users', '/users/reader']:
        response = client.get(path)
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'
    assert state['calls'] == 0


def test_awards_failure_keeps_profile(
    portal_app: tuple[Flask, dict[str, Any]],
) -> None:
    """Keep public profile usable if award computation fails.

    :param portal_app: Isolated application and viewer state.
    :return: None.
    """
    app, state = portal_app
    state['fail'] = True
    response = app.test_client().get('/users/reader')
    assert response.status_code == 200
    assert 'fa-download' not in response.get_data(as_text=True)


def test_directory_badge_javascript() -> None:
    """Execute directory badge rendering with a deterministic DOM stub.

    :return: None.
    """
    node = shutil.which('node')
    if node is None:
        pytest.skip('Node.js is unavailable')
    script = Path(__file__).with_suffix('.cjs')
    subprocess.run([node, str(script)], check=True)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================