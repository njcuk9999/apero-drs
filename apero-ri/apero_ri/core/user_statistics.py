#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Private, transactional UTC user-day activity storage and aggregation."""
from __future__ import annotations

import datetime
import hashlib
import functools
import os
import sqlite3
import threading
import unicodedata
from contextlib import closing
from pathlib import Path
from urllib.parse import urlsplit

from aperocore.base import base
from apero_ri.core import secret_store


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.user_statistics'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_TIMEOUT = 30.0
_GEOIP_LOCK = threading.Lock()
_COUNTRIES = set(('AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE '
                  'BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC '
                  'CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ '
                  'DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB '
                  'GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM '
                  'HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE '
                  'KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU '
                  'LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT '
                  'MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM '
                  'PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU '
                  'RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV '
                  'SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ '
                  'UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM '
                  'ZW').split())
_SCHEMA = '''CREATE TABLE IF NOT EXISTS user_days (
    username TEXT NOT NULL,
    day TEXT NOT NULL,
    first_path_hash TEXT NOT NULL CHECK(length(first_path_hash) = 64),
    active INTEGER NOT NULL DEFAULT 0 CHECK(active IN (0, 1)),
    country TEXT NOT NULL DEFAULT '',
    region TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (username, day)
)'''


# =============================================================================
# Define classes
# =============================================================================

# =============================================================================
# Define functions
# =============================================================================
def _today() -> datetime.date:
    """Return today's UTC date, independently of the server timezone."""
    return datetime.datetime.now(datetime.timezone.utc).date()


def _path(data_dir: Path) -> Path:
    """Return the statistics database path.

    :param data_dir: ARI data root.
    :return: Private statistics file location.
    """
    return Path(data_dir) / 'admin' / 'general' / 'user_statistics.sqlite3'


def _reader(data_dir: Path) -> sqlite3.Connection | None:
    """Open an existing initialized store read-only, or return None.

    :param data_dir: ARI data root.
    :return: Caller-owned connection, or None for a missing store/schema.
    """
    path = _path(data_dir)
    if not path.is_file():
        return None
    uri = path.resolve().as_uri() + '?mode=ro'
    connection = sqlite3.connect(uri, timeout=_TIMEOUT, uri=True)
    try:
        query = "SELECT 1 FROM sqlite_master WHERE name = 'user_days'"
        if connection.execute(query).fetchone() is not None:
            return connection
    except BaseException:
        connection.close()
        raise
    connection.close()
    return None


def _geo(country: str, region: str) -> tuple[str, str]:
    """Normalize ISO2 country and bounded, control-free region text.

    :param country: ISO 3166-1 alpha-2 code, or unknown.
    :param region: Region label; unknown country does not discard it.
    :return: Valid country or empty string, and at most 128 region characters.
    """
    country = country.strip().upper() if isinstance(country, str) else ''
    if country not in _COUNTRIES:
        country = ''
    region = region if isinstance(region, str) else ''
    region = unicodedata.normalize('NFC', region)
    region = ''.join(char for char in region
                     if not unicodedata.category(char).startswith('C'))
    return country, ' '.join(region.split())[:128]


@functools.lru_cache(maxsize=1)
def _geoip_reader(database_path: str) -> object:
    """Open a local MaxMind City database once per worker process.

    :param database_path: Local MMDB path configured by the operator.
    :return: GeoIP2 reader retained only in process memory.
    :raises ImportError: Optional geoip extra is not installed.
    """
    from geoip2.database import Reader

    return Reader(database_path)


def location_for_address(address: str) -> tuple[str, str]:
    """Resolve an address locally and return only country and region.

    :param address: Transient client address; it is never persisted or logged.
    :return: ISO2 country and subdivision name, or empty values when disabled,
        unresolvable, or when the optional database is unavailable.
    """
    database_path = os.environ.get('ARI_GEOIP_DB', '').strip()
    if not database_path or not address:
        return '', ''
    if not Path(database_path).is_file():
        return '', ''
    try:
        with _GEOIP_LOCK:
            reader = _geoip_reader(database_path)
            location = reader.city(address)
    except Exception:
        return '', ''
    country = location.country.iso_code or ''
    region = ''
    subdivisions = location.subdivisions
    if subdivisions:
        region = subdivisions.most_specific.name or ''
    return _geo(country, region)


def _needs_geo(row: tuple, country: str, region: str) -> bool:
    """Return whether a stored row can gain compatible missing geography.

    :param row: Stored first hash, active flag, country and region.
    :param country: Normalized incoming country.
    :param region: Normalized incoming region.
    :return: Whether compatible missing geography can be backfilled.
    """
    stored_country, stored_region = row[2:4]
    if stored_country and country and stored_country != country:
        return False
    return bool((not stored_country and country)
                or (not stored_region and region))


def record_page_view(data_dir: Path, username: str, page_path: str, *,
                     day: datetime.date | None = None, country: str = '',
                     region: str = '') -> bool:
    """Qualify a user-day once two distinct page paths have been seen.

    :param data_dir: ARI data root; storage is admin/general/*.sqlite3.
    :param username: Nonempty identity, at most 128 non-whitespace characters.
    :param page_path: Absolute local path; query and fragment are discarded.
        Percent encoding and trailing slashes are caller-canonicalized.
    :param day: UTC date override; defaults to UTC today. Datetimes rejected.
    :param country: ISO2 country or unknown; missing geo may be backfilled.
    :param region: Region label, normalized and limited to 128 characters.
    :return: True only for the transaction newly qualifying this user-day.
        Invalid inputs return False without creating storage. Storage errors
        propagate to the caller. Future date overrides are allowed.
    """
    if not isinstance(username, str) or not 1 <= len(username) <= 128:
        return False
    if any(char.isspace() or unicodedata.category(char).startswith('C')
           for char in username):
        return False
    if not isinstance(page_path, str) or not 1 <= len(page_path) <= 8192:
        return False
    if any(unicodedata.category(char).startswith('C') for char in page_path):
        return False
    try:
        parsed = urlsplit(page_path)
    except ValueError:
        return False
    if parsed.scheme or parsed.netloc or not parsed.path.startswith('/'):
        return False
    if page_path.startswith('//'):
        return False
    day = _today() if day is None else day
    if type(day) is not datetime.date:
        return False
    identity = (username, day.isoformat())
    country, region = _geo(country, region)
    query = ('SELECT first_path_hash, active, country, region FROM user_days '
             'WHERE username = ? AND day = ?')
    reader = _reader(data_dir)
    if reader is not None:
        with closing(reader):
            row = reader.execute(query, identity).fetchone()
        if row and row[1] and not _needs_geo(row, country, region):
            return False
    path_hash = hashlib.sha256(parsed.path.encode('utf-8')).hexdigest()
    path = _path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_WRONLY, 0o600)
    os.close(descriptor)
    secret_store.protect_path(path)
    with closing(sqlite3.connect(path, timeout=_TIMEOUT)) as connection:
        with connection:
            connection.execute('BEGIN IMMEDIATE')
            connection.execute(_SCHEMA)
            row = connection.execute(query, identity).fetchone()
            if row is None:
                values = (*identity, path_hash, country, region)
                insert = ('INSERT INTO user_days '
                          '(username, day, first_path_hash, country, region) '
                          'VALUES (?, ?, ?, ?, ?)')
                connection.execute(insert, values)
                return False
            qualified = not row[1] and row[0] != path_hash
            if qualified or _needs_geo(row, country, region):
                compatible = not row[2] or not country or row[2] == country
                new_country = (row[2] or country) if compatible else row[2]
                new_region = (row[3] or region) if compatible else row[3]
                values = (int(bool(row[1] or qualified)), new_country,
                          new_region, *identity)
                update = ('UPDATE user_days SET active = ?, country = ?, '
                          'region = ? WHERE username = ? AND day = ?')
                connection.execute(update, values)
            return bool(qualified)


def _date(value: str | None, default: datetime.date) -> datetime.date:
    """Parse a strict ISO date filter, using default only for None.

    :param value: YYYY-MM-DD or None.
    :param default: Date for an omitted filter.
    :return: Parsed date; malformed filters raise ValueError.
    """
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError
    parsed = datetime.date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError
    return parsed


def summary(data_dir: Path, start: str | None = None,
            end: str | None = None) -> dict:
    """Aggregate qualified activity over an inclusive date range.

    :param data_dir: ARI data root; a missing store remains untouched.
    :param start: Strict ISO date, default earliest candidate or UTC today.
    :param end: Strict ISO date, default UTC today.
    :return: Selected dates, global candidate bounds (None when absent),
        qualified totals, Monday weeks including zeros, country/region
        distinct-user counts, and users sorted by days descending then name.
        Countries/regions sort by user-days descending, then their labels.
        Invalid or reversed ranges raise ValueError. Storage errors propagate.
    """
    today = _today()
    connection = _reader(data_dir)
    try:
        first_day = last_day = None
        if connection is not None:
            connection.execute('BEGIN')
            bounds = 'SELECT MIN(day), MAX(day) FROM user_days'
            first_day, last_day = connection.execute(bounds).fetchone()
        earliest = today
        if first_day:
            earliest = datetime.date.fromisoformat(first_day)
        start_day = _date(start, earliest)
        end_day = _date(end, today)
        if start_day > end_day:
            raise ValueError
        result = dict(start=start_day.isoformat(), end=end_day.isoformat())
        result.update(first_day=first_day, last_day=last_day)
        result.update(total_user_days=0, unique_users=0)
        result['calendar_days'] = (end_day - start_day).days + 1
        result.update(weekly=[], countries=[], regions=[], users=[])
        week = start_day - datetime.timedelta(days=start_day.weekday())
        last_week = end_day - datetime.timedelta(days=end_day.weekday())
        weeks = dict()
        while True:
            weeks[week.isoformat()] = dict(week=week.isoformat(),
                                          user_days=0, users=0)
            if week == last_week:
                break
            week += datetime.timedelta(days=7)
        result['weekly'] = list(weeks.values())
        if connection is None:
            return result
        filters = (result['start'], result['end'])
        selected = ' FROM user_days WHERE active = 1 AND day BETWEEN ? AND ? '
        query = 'SELECT COUNT(*), COUNT(DISTINCT username)' + selected
        totals = connection.execute(query, filters).fetchone()
        result['total_user_days'], result['unique_users'] = totals
        monday = ("date(day, '-' || ((CAST(strftime('%w', day) AS INTEGER) "
                  "+ 6) % 7) || ' days')")
        query = ('SELECT ' + monday + ', COUNT(*), COUNT(DISTINCT username)'
                 + selected + 'GROUP BY 1 ORDER BY 1')
        for week_name, user_days, users in connection.execute(query, filters):
            weeks[week_name].update(user_days=user_days, users=users)
        for key, columns in [('countries', 'country'),
                             ('regions', 'country, region')]:
            query = ('SELECT ' + columns + ', COUNT(DISTINCT username), '
                     'COUNT(*)' + selected + 'GROUP BY ' + columns
                     + ' ORDER BY COUNT(*) DESC, ' + columns)
            names = columns.split(', ') + ['users', 'user_days']
            rows = connection.execute(query, filters)
            result[key] = [dict(zip(names, row)) for row in rows]
        query = ('SELECT username, COUNT(*)' + selected
                 + 'GROUP BY username ORDER BY COUNT(*) DESC, username')
        rows = connection.execute(query, filters)
        result['users'] = [dict(username=name, days=days)
                   for name, days in rows]
        return result
    finally:
        if connection is not None:
            connection.close()


def activity_awards(data_dir: Path) -> dict:
    """Rank all-time positive user-day scores using three distinct scores.

    :param data_dir: ARI data root; no store is created on reads.
    :return: Username mapped to active_days and activity_medal. Ties share
        gold, silver, or bronze; other positive scores have medal None.
        Candidate-only users are omitted. Storage errors propagate.
    """
    connection = _reader(data_dir)
    if connection is None:
        return dict()
    with closing(connection):
        query = ('SELECT username, COUNT(*) FROM user_days WHERE active = 1 '
                 'GROUP BY username ORDER BY COUNT(*) DESC, username')
        rows = connection.execute(query).fetchall()
    scores = sorted({days for _, days in rows}, reverse=True)[:3]
    medals = dict(zip(scores, ('gold', 'silver', 'bronze')))
    return {name: dict(active_days=days, activity_medal=medals.get(days))
            for name, days in rows}


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================