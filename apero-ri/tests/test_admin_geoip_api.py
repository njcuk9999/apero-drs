#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused tests for the running admin GeoLite installation endpoint."""
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from flask import Flask

from apero.dev import get_base_params
from aperocore.base import base
from apero_ri.application import admin_geoip_api_helpers as helpers


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_admin_geoip_api'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_PARAMS = get_base_params('SPIROU')


# =============================================================================
# Define functions
# =============================================================================
@pytest.fixture()
def geoip_client(monkeypatch: pytest.MonkeyPatch,
                 tmp_path: Path) -> tuple[Any, dict[str, Any]]:
    """Build an isolated admin GeoLite endpoint and mutable auth state.

    :param monkeypatch: Replace permission and database download helpers.
    :param tmp_path: Isolated ARI data root.
    :return: Flask client and test state.
    """
    app = Flask(__name__)
    app.secret_key = 'geoip-test-only'
    state: dict[str, Any] = dict(
        user=dict(username='admin'), installed=[])

    class Owner:
        """Minimal ARI app adapter used by the endpoint helper."""

        def _require_admin_user(self) -> tuple[Any, set[str]]:
            """Return the configured user and admin permission set."""
            return state['user'], {'view.admin'}

        def _resolve_local_data_dir(self) -> Path:
            """Return the fixture's private data directory."""
            return tmp_path

    owner = Owner()
    state['data_dir'] = tmp_path
    monkeypatch.setattr(
        helpers.setup_geoip, 'install_database',
        lambda root, account, key: state['installed'].append(
            (root, account, key)))
    app.add_url_rule(
        '/api/admin/geoip/install', 'install',
        lambda: helpers.api_install(owner), methods=['POST'])
    return app.test_client(), state


def test_admin_geoip_install_requires_admin_and_same_origin(
    geoip_client: tuple[Any, dict[str, Any]],
) -> None:
    """Reject non-admin, login-as, and cross-origin credential posts.

    :param geoip_client: Isolated API client and mutable auth state.
    :return: None.
    """
    client, state = geoip_client
    body = dict(account_id='acct', license_key='key', accept_terms=True)
    headers = {'Origin': 'http://localhost'}
    assert client.post(
        '/api/admin/geoip/install', json=body).status_code == 403
    state['user'] = None
    assert client.post('/api/admin/geoip/install', json=body,
                       headers=headers).status_code == 401
    state['user'] = dict(username='admin')
    with client.session_transaction() as current_session:
        current_session['login_as'] = 'another'
    assert client.post('/api/admin/geoip/install', json=body,
                       headers=headers).status_code == 403
    with client.session_transaction() as current_session:
        current_session.pop('login_as')
    assert client.post(
        '/api/admin/geoip/install', json=body,
        headers={'Origin': 'https://evil.example'}).status_code == 403
    assert state['installed'] == []


def test_admin_geoip_install_validates_terms_and_passes_credentials_once(
    geoip_client: tuple[Any, dict[str, Any]],
) -> None:
    """Require terms acceptance and pass credentials only to the installer.

    :param geoip_client: Isolated API client and mutable auth state.
    :return: None.
    """
    client, state = geoip_client
    headers = {'Origin': 'http://localhost'}
    body = dict(account_id='acct', license_key='secret', accept_terms=False)
    response = client.post('/api/admin/geoip/install', json=body,
                           headers=headers)
    assert response.status_code == 400
    assert state['installed'] == []

    body['accept_terms'] = True
    response = client.post('/api/admin/geoip/install', json=body,
                           headers=headers)
    assert response.status_code == 200
    assert response.json['success'] is True
    assert state['installed'] == [
        (state['data_dir'], 'acct', 'secret')]
    assert b'secret' not in response.data


def test_admin_geoip_route_is_registered() -> None:
    """Expose the direct install API through production static routes.

    :return: None.
    """
    from apero_ri.application import routes

    registered: dict[str, tuple[str, Any]] = dict()

    class Recorder:
        """Capture route registration without creating the full app."""

        _limiter = SimpleNamespace(limit=lambda rate: lambda handler: handler)

        def __getattr__(self, name: str) -> Any:
            """Return a stable callable stand-in for app methods."""
            return lambda: None

        def add_url_rule(self, rule: str, endpoint: str,
                         view_func: Any, **kwargs: Any) -> None:
            """Capture an endpoint and its handler."""
            registered[rule] = endpoint, view_func

    routes.register_static_routes(Recorder())
    endpoint, handler = registered['/api/admin/geoip/install']
    assert endpoint == 'api_admin_geoip_install'
    assert handler is not None


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
