#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Deterministic, profile-free activity storage and aggregation tests."""
from __future__ import annotations

import datetime
import hashlib
import multiprocessing
import sqlite3
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from apero.dev import get_base_params
from aperocore.base import base
from apero_ri.core import user_statistics as stats


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_user_statistics'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_PARAMS = get_base_params('SPIROU')
_DAY = datetime.date(2026, 1, 4)


# =============================================================================
# Define classes
# =============================================================================

# =============================================================================
# Define functions
# =============================================================================
def _qualify(root: Path, username: str, day: datetime.date,
             country: str = '', region: str = '') -> None:
    """Record two paths for a user/date with optional geography.

    :param root: Isolated ARI data root.
    :param username: User identity.
    :param day: Injected UTC date.
    :param country: Optional country code.
    :param region: Optional region name.
    :return: None; assert exactly the second view qualifies.
    """
    view_kwargs = dict(day=day, country=country, region=region)
    assert not stats.record_page_view(root, username, '/one', **view_kwargs)
    assert stats.record_page_view(root, username, '/two', **view_kwargs)


def test_reset_activity(tmp_path: Path) -> None:
    """Clear active and pending records without creating a missing store.

    :param tmp_path: Isolated ARI data root.
    :return: None.
    """
    assert stats.reset_activity(tmp_path) == 0
    assert not stats._path(tmp_path).exists()
    _qualify(tmp_path, 'alice', _DAY, 'CA', 'Quebec')
    stats.record_page_view(tmp_path, 'bob', '/one', day=_DAY)
    assert stats.reset_activity(tmp_path) == 2
    assert stats._path(tmp_path).exists()
    assert stats.activity_awards(tmp_path) == dict()
    assert stats.summary(tmp_path)['total_user_days'] == 0
    _qualify(tmp_path, 'alice', _DAY, 'CA', 'Quebec')


def test_qualification_privacy_and_saturation(tmp_path: Path) -> None:
    """Check refresh deduplication, hash-only storage and no active rewrites.

    :param tmp_path: Isolated storage.
    :return: None.
    """
    record = stats.record_page_view
    assert not record(tmp_path, 'alice', '/private?ip=192.0.2.1', day=_DAY)
    assert not record(tmp_path, 'alice', '/private?token=secret', day=_DAY)
    assert not record(tmp_path, 'alice', '/private#fragment', day=_DAY)
    assert stats.summary(tmp_path, '2026-01-04', '2026-01-04')['users'] == []
    assert record(tmp_path, 'alice', '/other', day=_DAY)
    path = stats._path(tmp_path)
    before = path.read_bytes()
    for _ in range(5):
        assert not record(tmp_path, 'alice', '/third', day=_DAY)
    assert path.read_bytes() == before
    with sqlite3.connect(path) as connection:
        row = connection.execute('SELECT * FROM user_days').fetchone()
    assert row == ('alice', '2026-01-04',
                   hashlib.sha256(b'/private').hexdigest(), 1, '', '')
    assert b'/private' not in before
    assert b'192.0.2.1' not in before
    assert b'secret' not in before
    assert path.stat().st_mode & 0o777 == 0o600
    assert not list(path.parent.glob('*-journal'))


def test_empty_read_only_and_utc(tmp_path: Path,
                                 monkeypatch: pytest.MonkeyPatch) -> None:
    """Check empty defaults, UTC injection and noncreating readers.

    :param tmp_path: Isolated storage.
    :param monkeypatch: Fixed UTC clock.
    :return: None.
    """
    monkeypatch.setattr(stats, '_today', lambda: _DAY)
    result = stats.summary(tmp_path)
    assert set(result) == {
        'start', 'end', 'first_day', 'last_day', 'total_user_days',
        'unique_users', 'calendar_days', 'weekly', 'countries', 'regions',
        'users'}
    assert result['start'] == result['end'] == '2026-01-04'
    assert result['first_day'] is result['last_day'] is None
    assert result['calendar_days'] == 1
    assert result['weekly'] == [dict(week='2025-12-29', user_days=0, users=0)]
    assert stats.activity_awards(tmp_path) == dict()
    assert not (tmp_path / 'admin').exists()
    assert not stats.record_page_view(tmp_path, 'alice', '/one')
    assert stats.record_page_view(tmp_path, 'alice', '/two')
    path = stats._path(tmp_path)
    before = path.stat().st_mtime_ns
    path.chmod(0o400)
    assert stats.summary(tmp_path)['total_user_days'] == 1
    assert stats.activity_awards(tmp_path)['alice']['active_days'] == 1
    assert path.stat().st_mtime_ns == before
    assert path.stat().st_mode & 0o777 == 0o400


def test_app_records_only_successful_page_navigations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Count authenticated documents, excluding polling and impersonation.

    :param tmp_path: Isolated activity data root.
    :param monkeypatch: Replace auth and GeoIP with deterministic values.
    :return: None.
    """
    from types import SimpleNamespace

    from flask import Flask, jsonify

    from apero_ri.application import ariapp_impls

    app = Flask(__name__)
    app.secret_key = 'activity-test-only'
    app.args = SimpleNamespace(data_dir=str(tmp_path / 'other'))
    app._resolve_local_data_dir = lambda: tmp_path
    monkeypatch.setattr(ariapp_impls.auth, 'get_effective_user',
                        lambda current_session: dict(username='reader'))
    database = tmp_path / 'cache' / 'geoip' / 'GeoLite2-City.mmdb'
    database.parent.mkdir(parents=True)
    database.touch()
    location = SimpleNamespace(
        country=SimpleNamespace(iso_code='CA'),
        subdivisions=SimpleNamespace(
            most_specific=SimpleNamespace(name='Quebec')))
    reader = SimpleNamespace(city=lambda address: location)
    monkeypatch.setattr(stats, '_geoip_reader',
                        lambda path, modified_ns: reader)
    monkeypatch.setenv('ARI_DIR', str(tmp_path / 'other'))
    monkeypatch.delenv('ARI_GEOIP_DB', raising=False)
    monkeypatch.setenv('ARI_PROXY_COUNT', '0')
    ariapp_impls.ariapp_configure_production_hardening(app)
    app.add_url_rule('/one', 'one', lambda: '<h1>One</h1>')
    app.add_url_rule('/two', 'two', lambda: '<h1>Two</h1>')
    app.add_url_rule('/fail', 'fail', lambda: ('Failed', 500))
    app.add_url_rule('/api/poll', 'poll', lambda: jsonify(ok=True))

    client = app.test_client()
    headers = {'Accept': 'text/html', 'Sec-Fetch-Mode': 'navigate',
               'Sec-Fetch-Dest': 'document'}
    assert client.get('/one').status_code == 200
    assert client.get('/one', headers=headers).status_code == 200
    assert client.get('/one', headers=headers).status_code == 200
    fetch_headers = {'Accept': 'text/html', 'Sec-Fetch-Mode': 'cors',
                     'Sec-Fetch-Dest': 'empty'}
    assert client.get('/two', headers=fetch_headers).status_code == 200
    assert client.get('/fail', headers=headers).status_code == 500
    assert client.get('/api/poll').status_code == 200
    assert stats.summary(tmp_path)['total_user_days'] == 0
    assert client.get('/two', headers=headers).status_code == 200
    result = stats.summary(tmp_path)
    assert result['total_user_days'] == 1
    assert result['countries'] == [
        dict(country='CA', users=1, user_days=1)]
    assert result['regions'] == [
        dict(country='CA', region='Quebec', users=1, user_days=1)]

    with client.session_transaction() as current_session:
        current_session['login_as'] = 'another_user'
    client.get('/one', headers=headers)
    client.get('/two', headers=headers)
    assert stats.summary(tmp_path)['total_user_days'] == 1


def test_aggregation_filters_and_week_boundaries(tmp_path: Path) -> None:
    """Check inclusive filtering, zero weeks and geo distinct-user counts.

    :param tmp_path: Isolated storage.
    :return: None.
    """
    _qualify(tmp_path, 'alice', _DAY, 'ca', 'Quebec')
    _qualify(tmp_path, 'alice', datetime.date(2026, 1, 5), 'CA', 'Quebec')
    _qualify(tmp_path, 'bob', datetime.date(2026, 1, 5), 'CA', 'Ontario')
    _qualify(tmp_path, 'alice', datetime.date(2026, 1, 19), 'FR', 'Paris')
    _qualify(tmp_path, 'charlie', datetime.date(2026, 1, 19))
    assert not stats.record_page_view(tmp_path, 'pending', '/one',
                                      day=datetime.date(2025, 12, 31))
    result = stats.summary(tmp_path, '2026-01-04', '2026-01-19')
    assert result['first_day'] == '2025-12-31'
    assert result['last_day'] == '2026-01-19'
    assert result['calendar_days'] == 16
    assert result['total_user_days'] == 5
    assert result['unique_users'] == 3
    assert result['users'] == [dict(username='alice', days=3),
                               dict(username='bob', days=1),
                               dict(username='charlie', days=1)]
    assert result['weekly'] == [
        dict(week='2025-12-29', user_days=1, users=1),
        dict(week='2026-01-05', user_days=2, users=2),
        dict(week='2026-01-12', user_days=0, users=0),
        dict(week='2026-01-19', user_days=2, users=2)]
    assert result['countries'] == [
        dict(country='CA', users=2, user_days=3),
        dict(country='', users=1, user_days=1),
        dict(country='FR', users=1, user_days=1)]
    assert result['regions'] == [
        dict(country='CA', region='Quebec', users=1, user_days=2),
        dict(country='', region='', users=1, user_days=1),
        dict(country='CA', region='Ontario', users=1, user_days=1),
        dict(country='FR', region='Paris', users=1, user_days=1)]
    one_day = stats.summary(tmp_path, '2026-01-05', '2026-01-05')
    assert one_day['total_user_days'] == one_day['unique_users'] == 2
    assert one_day['calendar_days'] == 1
    assert stats.summary(tmp_path)['start'] == '2025-12-31'
    outside = stats.summary(tmp_path, '2024-01-01', '2024-01-14')
    assert outside['total_user_days'] == outside['unique_users'] == 0
    assert len(outside['weekly']) == 2


@pytest.mark.parametrize('username', ['', ' ', 'a b', 'a\x00b', None,
                                      'a' * 129])
def test_invalid_usernames(tmp_path: Path, username: str) -> None:
    """Reject invalid identities without creating storage.

    :param tmp_path: Isolated storage.
    :param username: Invalid identity.
    :return: None.
    """
    assert not stats.record_page_view(tmp_path, username, '/one', day=_DAY)
    assert not (tmp_path / 'admin').exists()


@pytest.mark.parametrize('path', ['', 'relative', '//host/path',
                                  'https://host/path', '/a\x00b', None,
                                  '/x' * 8192])
def test_invalid_paths(tmp_path: Path, path: str) -> None:
    """Reject invalid page paths before storage.

    :param tmp_path: Isolated storage.
    :param path: Invalid page path.
    :return: None.
    """
    assert not stats.record_page_view(tmp_path, 'alice', path, day=_DAY)
    assert not (tmp_path / 'admin').exists()


@pytest.mark.parametrize('start,end', [
    ('bad', None), ('2026-02-30', None), ('20260101', None),
    ('2026-W01-1', None), ('', None), (None, 'bad'),
    ('2026-02-01', '2026-01-01'), (42, None)])
def test_invalid_filters(tmp_path: Path, start: str | None,
                         end: str | None) -> None:
    """Malformed and reversed filters raise without creating storage.

    :param tmp_path: Isolated storage.
    :param start: Invalid or reversed lower bound.
    :param end: Invalid or reversed upper bound.
    :return: None.
    """
    with pytest.raises(ValueError):
        stats.summary(tmp_path, start, end)
    assert not (tmp_path / 'admin').exists()


def test_geo_backfill_and_day_reset(tmp_path: Path) -> None:
    """Preserve unknown geography and backfill without requalification.

    :param tmp_path: Isolated storage.
    :return: None.
    """
    _qualify(tmp_path, 'alice', _DAY, '', '  North  \x00 Coast ')
    result = stats.summary(tmp_path, '2026-01-04', '2026-01-04')
    assert result['regions'] == [
        dict(country='', region='North Coast', users=1, user_days=1)]
    view_kwargs = dict(day=_DAY, country='ca', region='Different')
    assert not stats.record_page_view(tmp_path, 'alice', '/one', **view_kwargs)
    result = stats.summary(tmp_path, '2026-01-04', '2026-01-04')
    assert result['regions'][0]['country'] == 'CA'
    assert result['regions'][0]['region'] == 'North Coast'
    view_kwargs.update(country='FR', region='Paris')
    assert not stats.record_page_view(tmp_path, 'alice', '/two', **view_kwargs)
    assert stats.summary(tmp_path)['regions'][0]['country'] == 'CA'
    _qualify(tmp_path, 'alice', datetime.date(2026, 1, 5), 'ZZ', 'x' * 200)
    result = stats.summary(tmp_path, '2026-01-05', '2026-01-05')
    assert result['regions'][0]['country'] == ''
    assert len(result['regions'][0]['region']) == 128
    assert not stats.record_page_view(tmp_path, 'alice', '/one', day='bad')
    invalid_day = datetime.datetime(2026, 1, 4)
    invalid_kwargs = dict(day=invalid_day)
    invalid_args = (tmp_path, 'alice', '/one')
    assert not stats.record_page_view(*invalid_args, **invalid_kwargs)


def test_local_geoip_keeps_only_location(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use a local database reader and return region labels only.

    :param tmp_path: Temporary database placeholder.
    :param monkeypatch: Replace the optional MaxMind reader.
    :return: None.
    """
    from types import SimpleNamespace

    database = tmp_path / 'city.mmdb'
    database.touch()
    monkeypatch.setenv('ARI_GEOIP_DB', str(database))
    location = SimpleNamespace(
        country=SimpleNamespace(iso_code='ca'),
        subdivisions=SimpleNamespace(
            most_specific=SimpleNamespace(name='Quebec')))
    addresses = []

    class Reader:
        """Minimal local City database reader stub."""

        def city(self, address: str) -> object:
            """Capture the transient address and return location only."""
            addresses.append(address)
            return location

    monkeypatch.setattr(
        stats, '_geoip_reader', lambda path, modified_ns: Reader())
    assert stats.location_for_address('192.0.2.10', tmp_path) == (
        'CA', 'Quebec')
    assert addresses == ['192.0.2.10']
    assert stats.location_for_address('', tmp_path) == ('', '')


def test_setup_database_is_discovered_without_environment_variable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use the setup-installed cache path when no override is configured.

    :param tmp_path: Isolated ARI data directory.
    :param monkeypatch: Replace the local MMDB reader.
    :return: None.
    """
    from types import SimpleNamespace

    database = tmp_path / 'cache' / 'geoip' / 'GeoLite2-City.mmdb'
    database.parent.mkdir(parents=True)
    database.touch()
    calls = []

    class Reader:
        """Minimal GeoIP reader stand-in."""

        def city(self, address: str) -> object:
            """Return one country and region without retaining address."""
            calls.append(address)
            return SimpleNamespace(
                country=SimpleNamespace(iso_code='CA'),
                subdivisions=SimpleNamespace(
                    most_specific=SimpleNamespace(name='Quebec')))

    monkeypatch.delenv('ARI_GEOIP_DB', raising=False)
    monkeypatch.setenv('ARI_DIR', str(tmp_path / 'other'))
    monkeypatch.setattr(
        stats, '_geoip_reader', lambda path, modified_ns: Reader())
    assert stats.location_for_address('192.0.2.2', tmp_path) == (
        'CA', 'Quebec')
    assert calls == ['192.0.2.2']


def test_invalid_geoip_database_is_rejected(tmp_path: Path) -> None:
    """Reject non-MMDB content with the installed MaxMind reader.

    :param tmp_path: Temporary invalid database file.
    :return: None.
    """
    from apero_ri.setup.geoip import _validate_database

    invalid_database = tmp_path / 'not-an-mmdb'
    invalid_database.write_bytes(b'not a MaxMind database')
    with pytest.raises(RuntimeError, match='not a valid MMDB database'):
        _validate_database(invalid_database)


def test_concurrent_initialization_and_qualification(tmp_path: Path) -> None:
    """Independent worker connections qualify exactly once per user-day.

    :param tmp_path: Shared isolated storage.
    :return: None.
    """
    def record(index: int) -> bool:
        """Record a worker's page.

        :param index: Worker index selecting a page and user.
        :return: Whether this worker newly qualified the user-day.
        """
        username = 'alice' if index < 40 else 'bob'
        page = '/one' if index % 2 else '/two'
        return stats.record_page_view(tmp_path, username, page, day=_DAY)

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(record, range(80)))
    assert sum(results[:40]) == sum(results[40:]) == 1
    result = stats.summary(tmp_path, '2026-01-04', '2026-01-04')
    assert result['total_user_days'] == result['unique_users'] == 2
    with sqlite3.connect(stats._path(tmp_path)) as connection:
        query = 'SELECT COUNT(*) FROM user_days'
        assert connection.execute(query).fetchone() == (2,)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute('INSERT INTO user_days SELECT * FROM user_days')


def _process_record(values: tuple[Path, int]) -> bool:
    """Record one page using an independent spawned worker.

    :param values: Shared data root and worker task index.
    :return: Whether the worker newly qualified the user-day.
    """
    root, index = values
    page = '/one' if index % 2 else '/two'
    return stats.record_page_view(root, 'alice', page, day=_DAY)


def test_process_workers(tmp_path: Path) -> None:
    """Independent processes initialize and qualify exactly once.

    :param tmp_path: Shared isolated data root.
    :return: None.
    """
    worker_kwargs = dict(max_workers=4)
    worker_kwargs['mp_context'] = multiprocessing.get_context('spawn')
    with ProcessPoolExecutor(**worker_kwargs) as executor:
        values = [(tmp_path, index) for index in range(32)]
        results = list(executor.map(_process_record, values))
    assert sum(results) == 1
    assert stats.activity_awards(tmp_path) == dict(
        alice=dict(active_days=1, activity_medal='gold'))


def test_saturation_without_writer_lock(tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Saturated reads succeed while an independent writer holds its lock.

    :param tmp_path: Isolated storage.
    :param monkeypatch: Limit waits so an unexpected writer fails quickly.
    :return: None.
    """
    _qualify(tmp_path, 'alice', _DAY, 'CA', 'Quebec')
    monkeypatch.setattr(stats, '_TIMEOUT', 0.1)
    with sqlite3.connect(stats._path(tmp_path)) as connection:
        connection.execute('BEGIN IMMEDIATE')
        record_kwargs = dict(day=_DAY, country='CA', region='Quebec')
        record_args = (tmp_path, 'alice', '/three')
        assert not stats.record_page_view(*record_args, **record_kwargs)


def test_awards_distinct_positive_scores(tmp_path: Path) -> None:
    """Ties share medals, and candidates do not earn awards.

    :param tmp_path: Isolated storage.
    :return: None.
    """
    for username, days in [('alice', 5), ('bob', 5), ('carol', 3),
                           ('dave', 2), ('erin', 1)]:
        for offset in range(days):
            _qualify(tmp_path, username, _DAY + datetime.timedelta(days=offset))
    assert not stats.record_page_view(tmp_path, 'pending', '/one', day=_DAY)
    assert stats.activity_awards(tmp_path) == dict(
        alice=dict(active_days=5, activity_medal='gold'),
        bob=dict(active_days=5, activity_medal='gold'),
        carol=dict(active_days=3, activity_medal='silver'),
        dave=dict(active_days=2, activity_medal='bronze'),
        erin=dict(active_days=1, activity_medal=None))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================