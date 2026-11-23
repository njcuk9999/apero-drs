#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Focused tests for optional GeoLite setup and secure local installation."""
from io import BytesIO
import datetime
import json
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


def test_download_quota_cooldown_and_request_counters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bound MaxMind calls and persist every attempted database download.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Replace network/extraction and control time.
    :return: None.
    """
    now = datetime.datetime(2026, 11, 11, 12, tzinfo=datetime.timezone.utc)
    calls = []
    monkeypatch.setattr(geoip, '_utcnow', lambda: now)
    monkeypatch.setattr(geoip, 'MAX_DAILY_DOWNLOADS', 3)
    monkeypatch.setattr(geoip, 'MIN_DOWNLOAD_INTERVAL',
                        datetime.timedelta(hours=1))

    def download(path: Path, account: str, key: str) -> None:
        calls.append((account, key))
        path.write_bytes(b'archive')

    monkeypatch.setattr(geoip, '_download_archive', download)
    monkeypatch.setattr(
        geoip, '_extract_database',
        lambda archive, output: output.write_bytes(b'mmdb'))
    monkeypatch.setattr(geoip, '_validate_database', lambda path: None)

    geoip.install_database(tmp_path, 'acct', 'key')
    with pytest.raises(RuntimeError, match='one hour'):
        geoip.install_database(tmp_path, 'acct', 'key')
    status = geoip.get_status(tmp_path)
    assert status['requests_today'] == status['total_requests'] == 1
    assert calls == [('acct', 'key')]

    monkeypatch.setattr(geoip, 'MIN_DOWNLOAD_INTERVAL',
                        datetime.timedelta(0))
    geoip.install_database(tmp_path, 'acct', 'key')
    geoip.install_database(tmp_path, 'acct', 'key')
    with pytest.raises(RuntimeError, match='limit reached'):
        geoip.install_database(tmp_path, 'acct', 'key')
    status = geoip.get_status(tmp_path)
    assert status['requests_today'] == status['total_requests'] == 3
    assert len(calls) == 3
    tomorrow = now + datetime.timedelta(days=1)
    monkeypatch.setattr(geoip, '_utcnow', lambda: tomorrow)
    status = geoip.get_status(tmp_path)
    assert status['requests_today'] == 0
    assert status['total_requests'] == 3


def test_geoip_health_absent_disabled_fresh_and_due(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pass when absent/disabled and warn only when an installed DB is due.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Fix the health clock.
    :return: None.
    """
    now = datetime.datetime(2026, 11, 11, tzinfo=datetime.timezone.utc)
    monkeypatch.setattr(geoip, '_utcnow', lambda: now)
    assert geoip.health_status(tmp_path)['status'] == 'ok'


def test_admin_health_includes_geoip_and_passes_when_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Include GeoLite's optional freshness status in Admin Health.

    :param tmp_path: Isolated ARI data root.
    :param monkeypatch: Stub unrelated admin health sources.
    :return: None.
    """
    from apero_ri.application import admin_health_helpers

    monkeypatch.setattr(admin_health_helpers, 'load_users', lambda: {})
    monkeypatch.setattr(
        admin_health_helpers.eb, 'load_email_config',
        lambda: dict(enabled=False))
    monkeypatch.setattr(
        admin_health_helpers.bb, 'load_backup_config',
        lambda: dict(active_method_id='local'))
    monkeypatch.setattr(
        admin_health_helpers.bb, 'get_backup_methods',
        lambda *args, **kwargs: [dict(
            id='local', name='Local', provider='local_only', enabled=False)])
    monkeypatch.setattr(
        admin_health_helpers.sb, 'health_check',
        lambda: dict(status='ok', message=''))
    app = SimpleNamespace(_resolve_local_data_dir=lambda: tmp_path)

    health = admin_health_helpers.build_admin_card_health_uncached(
        app, dict(username='admin'), {'view.admin'})
    assert health['home.admin_portal.geoip_database']['status'] == 'ok'
    assert health['home.admin_portal.geoip_database']['message'] == (
        'No database installed; check skipped.')

    db_path = geoip.database_path(tmp_path)
    db_path.parent.mkdir(parents=True)
    db_path.write_bytes(b'mock mmdb')
    status_path = geoip._status_path(tmp_path)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = dict(health_check_enabled=False,
                    last_success_at='2026-01-01T00:00:00+00:00')
    status_path.write_text(json.dumps(metadata), encoding='utf-8')
    assert geoip.health_status(tmp_path)['status'] == 'ok'

    geoip.set_health_check_enabled(tmp_path, True)
    assert geoip.health_status(tmp_path)['status'] == 'warning'
    status = json.loads(status_path.read_text(encoding='utf-8'))
    status['last_success_at'] = '2026-11-01T00:00:00+00:00'
    status_path.write_text(json.dumps(status), encoding='utf-8')
    assert geoip.health_status(tmp_path)['status'] == 'ok'


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