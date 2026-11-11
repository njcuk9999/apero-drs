#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused tests for optional GeoLite setup and secure local installation."""
from io import BytesIO
from pathlib import Path
import tarfile
from types import SimpleNamespace
from typing import Any

import pytest

from apero.dev import get_base_params
from aperocore.base import base
from apero_ri.setup import geoip


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_setup_geoip'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_PARAMS = get_base_params('SPIROU')


# =============================================================================
# Define functions
# =============================================================================
def _archive_bytes() -> bytes:
    """Build a small gzip tar with one City MMDB fixture member.

    :return: Compressed test archive bytes.
    """
    buffer = BytesIO()
    payload = b'test-mmdb-payload'
    with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
        member = tarfile.TarInfo(
            f'GeoLite2-City_20261111/{geoip.DATABASE_NAME}')
        member.size = len(payload)
        archive.addfile(member, BytesIO(payload))
    return buffer.getvalue()


def test_install_database_uses_auth_and_replaces_atomically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Download authenticated archive without retaining credentials.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Replace network and MMDB validation.
    :return: None.
    """
    calls: list[dict[str, Any]] = []
    payload = _archive_bytes()

    class Response:
        """Small requests response stub for streamed content."""

        headers = {'Content-Length': str(len(payload))}

        def __enter__(self) -> 'Response':
            return self

        def __exit__(self, *values: object) -> None:
            return None

        def raise_for_status(self) -> None:
            return None

        def iter_content(self, chunk_size: int) -> list[bytes]:
            return [payload]

    def get(url: str, **kwargs: Any) -> Response:
        calls.append(dict(url=url, **kwargs))
        return Response()

    monkeypatch.setattr(geoip.requests, 'get', get)
    monkeypatch.setattr(geoip, '_validate_database', lambda path: None)
    destination = geoip.database_path(tmp_path)
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b'old database')

    result = geoip.install_database(tmp_path, 'account-123', 'secret-key')

    assert result == destination
    assert destination.read_bytes() == b'test-mmdb-payload'
    assert destination.stat().st_mode & 0o777 == 0o600
    assert destination.parent.stat().st_mode & 0o777 == 0o700
    assert calls[0]['url'] == geoip.DOWNLOAD_URL
    assert calls[0]['params'] == dict(suffix='tar.gz')
    assert calls[0]['auth'] == ('account-123', 'secret-key')
    stored = b''.join(path.read_bytes() for path in tmp_path.rglob('*')
                      if path.is_file())
    assert b'secret-key' not in stored
    assert b'account-123' not in stored


def test_bad_archive_preserves_installed_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject invalid archives without replacing an installed database.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Replace the network response.
    :return: None.
    """
    class Response:
        """Response stub containing malformed archive bytes."""

        headers = {'Content-Length': '8'}

        def __enter__(self) -> 'Response':
            return self

        def __exit__(self, *values: object) -> None:
            return None

        def raise_for_status(self) -> None:
            return None

        def iter_content(self, chunk_size: int) -> list[bytes]:
            return [b'not-tar!']

    monkeypatch.setattr(
        geoip.requests, 'get', lambda *args, **kwargs: Response())
    destination = geoip.database_path(tmp_path)
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b'previous database')

    with pytest.raises(RuntimeError, match='invalid database archive'):
        geoip.install_database(tmp_path, 'account-123', 'secret-key')
    assert destination.read_bytes() == b'previous database'


def test_setup_geoip_form_and_csrf(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Expose the opt-in form and reject requests without its CSRF token.

    :param tmp_path: Isolated setup data root.
    :param monkeypatch: Stub setup state, email config, and download.
    :return: None.
    """
    from apero_ri.setup import setup_app

    calls: list[tuple[Path, str, str]] = []
    monkeypatch.setattr(setup_app.auth, 'set_ari_dir', lambda path: None)
    monkeypatch.setattr(setup_app.eb, 'load_email_config', lambda: {})
    monkeypatch.setattr(
        setup_app, 'load_setup_state',
        lambda data_dir: dict(completed=True, admin_username='admin'))
    monkeypatch.setattr(
        setup_app.setup_geoip, 'install_database',
        lambda root, account, key: calls.append((root, account, key)))
    app = setup_app.create_setup_app(tmp_path)
    client = app.test_client()
    response = client.get('/complete', headers={'Accept-Language': 'fr'})
    assert response.status_code == 200
    assert b'name="account_id"' in response.data
    assert b'name="license_key"' in response.data
    assert 'Statistiques facultatives' in response.get_data(as_text=True)
    with client.session_transaction() as current_session:
        token = current_session['setup_geoip_token']

    response = client.post('/geoip/install', data=dict(
        csrf_token='invalid', account_id='account-123',
        license_key='secret-key', accept_terms='yes'))
    assert response.status_code == 302
    assert calls == []
    response = client.post('/geoip/install', data=dict(
        csrf_token=token, account_id='account-123',
        license_key='secret-key'))
    assert response.status_code == 302
    assert calls == []
    response = client.post(
        '/geoip/install', data=dict(
            csrf_token=token, account_id='account-123',
            license_key='secret-key', accept_terms='yes'),
        environ_base={'REMOTE_ADDR': '192.0.2.1'},
    )
    assert response.status_code == 302
    assert calls == []
    response = client.post('/geoip/install', data=dict(
        csrf_token=token, account_id='account-123',
        license_key='secret-key', accept_terms='yes'))
    assert response.status_code == 302
    assert calls == [(tmp_path, 'account-123', 'secret-key')]


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================