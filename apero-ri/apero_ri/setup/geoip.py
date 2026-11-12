#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install the MaxMind GeoLite2 City database from its official endpoint."""
from __future__ import annotations

import os
import json
from pathlib import Path
import tarfile
import tempfile
import threading
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from apero_ri.base import base


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.setup.geoip'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
DATABASE_NAME = 'GeoLite2-City.mmdb'
DOWNLOAD_URL = (
    'https://download.maxmind.com/geoip/databases/'
    'GeoLite2-City/download'
)
MAX_ARCHIVE_BYTES = 250 * 1024 * 1024
MAX_DATABASE_BYTES = 500 * 1024 * 1024
MAX_DAILY_DOWNLOADS = 3
MIN_DOWNLOAD_INTERVAL = timedelta(hours=1)
UPDATE_AFTER_DAYS = 30
_STATUS_LOCK = threading.Lock()


# =============================================================================
# Define functions
# =============================================================================
def _utcnow() -> datetime:
    """Return the current UTC time for download accounting."""
    return datetime.now(timezone.utc)


def database_path(data_dir: Path) -> Path:
    """Return the standard local cache path for the City database.

    :param data_dir: ARI local data directory.
    :return: GeoLite2 City MMDB path under the excluded cache directory.
    """
    return Path(data_dir) / 'cache' / 'geoip' / DATABASE_NAME


def _status_path(data_dir: Path) -> Path:
    """Return the durable metadata path for attempts and health settings."""
    return Path(data_dir) / 'admin' / 'general' / 'geoip_status.json'


def _load_status(data_dir: Path) -> dict[str, Any]:
    """Load stored download and health metadata with safe defaults."""
    path = _status_path(data_dir)
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(value, dict):
            return value
    except (OSError, ValueError):
        pass
    return dict(total_requests=0, requests_date='', requests_today=0,
                last_attempt_at='', last_success_at='',
                health_check_enabled=True)


def _save_status(data_dir: Path, status: dict[str, Any]) -> None:
    """Atomically persist metadata without storing MaxMind credentials."""
    path = _status_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(status, sort_keys=True), encoding='utf-8')
    try:
        temporary.chmod(0o600)
    except OSError:
        pass
    os.replace(temporary, path)
    try:
        path.chmod(0o600)
    except OSError:
        pass


def set_health_check_enabled(data_dir: Path, enabled: bool) -> dict[str, Any]:
    """Persist whether GeoLite freshness is included in admin health.

    :param data_dir: ARI local data directory.
    :param enabled: Whether an installed database can report stale status.
    :return: Updated GeoLite download and health metadata.
    """
    with _STATUS_LOCK:
        status = _load_status(data_dir)
        status['health_check_enabled'] = bool(enabled)
        _save_status(data_dir, status)
    return status


def set_proxy_count(data_dir: Path, count: int) -> None:
    """Persist the trusted proxy count for the next server startup.

    :param data_dir: ARI local data directory.
    :param count: Number of trusted forwarding proxies, from zero to ten.
    :return: None.
    :raises ValueError: The count is not an integer in the supported range.
    """
    if type(count) is not int or not 0 <= count <= 10:
        raise ValueError('Invalid proxy count')
    with _STATUS_LOCK:
        status = _load_status(data_dir)
        status['proxy_count'] = count
        _save_status(data_dir, status)


def proxy_count(data_dir: Path) -> int:
    """Return the saved proxy count or the legacy environment default.

    :param data_dir: ARI local data directory.
    :return: Trusted proxy count; invalid settings default to zero.
    """
    status = _load_status(data_dir)
    value = status.get('proxy_count')
    if value is None:
        try:
            value = int(os.environ.get('ARI_PROXY_COUNT', '0'))
        except ValueError:
            return 0
    if type(value) is not int or not 0 <= value <= 10:
        return 0
    return value


def get_status(data_dir: Path) -> dict[str, Any]:
    """Return database preview, update time, quota counters and health state.

    :param data_dir: ARI local data directory.
    :return: Local-only status; no GeoIP lookup or network request is made.
    """
    status = _load_status(data_dir)
    today = _utcnow().date().isoformat()
    path = database_path(data_dir)
    preview = None
    modified_at = ''
    if path.is_file():
        try:
            from geoip2.database import Reader

            reader: Any = Reader(str(path))
            metadata = reader.metadata()
            preview = dict(
                database_type=metadata.database_type,
                build_date=datetime.fromtimestamp(
                    metadata.build_epoch, timezone.utc).isoformat(),
                ip_version=metadata.ip_version,
                node_count=metadata.node_count,
                record_size=metadata.record_size,
                languages=list(metadata.languages or []),
            )
            reader.close()
            modified_at = datetime.fromtimestamp(
                path.stat().st_mtime, timezone.utc).isoformat()
        except Exception:
            preview = None
        if not status.get('last_success_at') and modified_at:
            status['last_success_at'] = modified_at
    status.update(
        installed=path.is_file(),
        database_path=str(path),
        file_modified_at=modified_at,
        preview=preview,
        health_check_enabled=bool(
            status.get('health_check_enabled', True)),
        total_requests=int(status.get('total_requests', 0) or 0),
        requests_today=(
            int(status.get('requests_today', 0) or 0)
            if status.get('requests_date') == today else 0),
        requests_date=today,
        last_attempt_at=str(status.get('last_attempt_at', '') or ''),
        last_success_at=str(status.get('last_success_at', '') or ''),
    )
    return status


def health_status(data_dir: Path) -> dict[str, str]:
    """Return a local-only freshness health result for admin health checks.

    Missing databases and an explicitly disabled check are non-errors.

    :param data_dir: ARI local data directory.
    :return: status/message pair for the admin health page.
    """
    status = get_status(data_dir)
    if not status['installed']:
        return dict(
            status='ok', message='No database installed; check skipped.')
    if not status['health_check_enabled']:
        return dict(
            status='ok', message='GeoLite freshness check is disabled.')
    last_success = str(status.get('last_success_at') or
                       status.get('file_modified_at') or '')
    if not last_success:
        return dict(
            status='warning',
            message=(
                'GeoLite database is installed, but update time is unknown.'
            ),
        )
    try:
        updated = datetime.fromisoformat(last_success)
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
    except ValueError:
        return dict(
            status='warning',
            message='GeoLite database update time is invalid.',
        )
    age = _utcnow() - updated.astimezone(timezone.utc)
    if age > timedelta(days=UPDATE_AFTER_DAYS):
        return dict(
            status='warning',
            message=(
                'GeoLite database was last updated {days} days ago; '
                'consider updating it.'
            ).format(days=age.days),
        )
    return dict(
        status='ok',
        message='GeoLite database is within the update window.',
    )


def install_database(data_dir: Path, account_id: str,
                     license_key: str) -> Path:
    """Download, validate, and atomically install the latest City database.

    Credentials are sent only as HTTPS Basic Auth and are never persisted.

    :param data_dir: ARI local data directory.
    :param account_id: MaxMind account ID.
    :param license_key: MaxMind license key with GeoLite download access.
    :return: Installed MMDB path.
    :raises ValueError: Credentials or archive are invalid.
    :raises RuntimeError: Download, archive, or MMDB validation failed.
    """
    account_id = str(account_id or '').strip()
    license_key = str(license_key or '').strip()
    if not account_id or not license_key:
        raise ValueError('MaxMind account ID and license key are required.')

    now = _utcnow()
    today = now.date().isoformat()
    with _STATUS_LOCK:
        status = _load_status(data_dir)
        if status.get('requests_date') != today:
            status['requests_date'] = today
            status['requests_today'] = 0
        last_attempt = str(status.get('last_attempt_at') or '')
        request_count = int(status.get('requests_today', 0) or 0)
        if request_count >= MAX_DAILY_DOWNLOADS:
            raise RuntimeError(
            'GeoLite download limit reached for today; '
            'try again tomorrow.')
        if last_attempt:
            try:
                previous = datetime.fromisoformat(last_attempt)
                if previous.tzinfo is None:
                    previous = previous.replace(tzinfo=timezone.utc)
                elapsed = now - previous.astimezone(timezone.utc)
                if elapsed < MIN_DOWNLOAD_INTERVAL:
                    raise RuntimeError(
                        'Please wait one hour between GeoLite '
                        'download attempts.')
            except ValueError:
                pass
        status['requests_today'] = int(status.get('requests_today', 0) or 0) + 1
        status['total_requests'] = (
            int(status.get('total_requests', 0) or 0) + 1)
        status['last_attempt_at'] = now.isoformat()
        _save_status(data_dir, status)

    destination = database_path(data_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.parent.chmod(0o700)
    except OSError:
        pass

    with tempfile.TemporaryDirectory(dir=destination.parent) as temp_dir:
        work_dir = Path(temp_dir)
        archive_path = work_dir / 'geolite.tar.gz'
        staged_path = work_dir / DATABASE_NAME
        _download_archive(archive_path, account_id, license_key)
        _extract_database(archive_path, staged_path)
        _validate_database(staged_path)
        staged_path.chmod(0o600)
        os.replace(staged_path, destination)
    with _STATUS_LOCK:
        status = _load_status(data_dir)
        status['last_success_at'] = _utcnow().isoformat()
        _save_status(data_dir, status)
    return destination


def _download_archive(path: Path, account_id: str, license_key: str) -> None:
    """Stream the HTTPS archive to a private temporary file.

    :param path: Temporary archive destination.
    :param account_id: MaxMind account ID for Basic Auth.
    :param license_key: MaxMind license key for Basic Auth.
    :return: None.
    :raises RuntimeError: The response is unsuccessful or exceeds the cap.
    """
    params = dict(suffix='tar.gz')
    try:
        with requests.get(
            DOWNLOAD_URL,
            params=params,
            auth=(account_id, license_key),
            allow_redirects=True,
            stream=True,
            timeout=(10, 120),
        ) as response:
            response.raise_for_status()
            length = response.headers.get('Content-Length')
            if length and int(length) > MAX_ARCHIVE_BYTES:
                raise RuntimeError('GeoLite archive exceeds the size limit.')
            written = 0
            with path.open('wb') as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    written += len(chunk)
                    if written > MAX_ARCHIVE_BYTES:
                        raise RuntimeError(
                            'GeoLite archive exceeds the size limit.')
                    output.write(chunk)
    except requests.RequestException as exc:
        raise RuntimeError(
            'MaxMind download failed. Check credentials and connectivity.'
        ) from exc


def _extract_database(archive_path: Path, output_path: Path) -> None:
    """Extract only a bounded regular MMDB file from the gzip archive.

    :param archive_path: Downloaded tar.gz file.
    :param output_path: Private staged MMDB path.
    :return: None.
    :raises RuntimeError: The archive is malformed or has no valid MMDB.
    """
    try:
        with tarfile.open(archive_path, mode='r:gz') as archive:
            members = [member for member in archive.getmembers()
                       if Path(member.name).name == DATABASE_NAME]
            if len(members) != 1:
                raise RuntimeError('GeoLite archive has no unique City MMDB.')
            member = members[0]
            valid_size = 1 <= member.size <= MAX_DATABASE_BYTES
            if not member.isfile() or not valid_size:
                raise RuntimeError('GeoLite City MMDB has an invalid size.')
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError('GeoLite City MMDB could not be read.')
            written = 0
            with source, output_path.open('wb') as output:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > member.size:
                        raise RuntimeError('GeoLite City MMDB is malformed.')
                    output.write(chunk)
            if written != member.size:
                raise RuntimeError('GeoLite City MMDB is truncated.')
    except (OSError, tarfile.TarError) as exc:
        message = 'MaxMind returned an invalid database archive.'
        raise RuntimeError(message) from exc


def _validate_database(path: Path) -> None:
    """Verify the staged file is readable as a MaxMind database.

    :param path: Staged database path.
    :return: None.
    :raises RuntimeError: The file is not a valid MMDB database.
    """
    try:
        from geoip2.database import Reader

        reader: Any = Reader(str(path))
        reader.close()
    except Exception as exc:
        message = 'Downloaded file is not a valid MMDB database.'
        raise RuntimeError(message) from exc


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================