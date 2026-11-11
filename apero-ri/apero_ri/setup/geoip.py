#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install the MaxMind GeoLite2 City database from its official endpoint."""
from __future__ import annotations

import os
from pathlib import Path
import tarfile
import tempfile
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


# =============================================================================
# Define functions
# =============================================================================
def database_path(data_dir: Path) -> Path:
    """Return the standard local cache path for the City database.

    :param data_dir: ARI local data directory.
    :return: GeoLite2 City MMDB path under the excluded cache directory.
    """
    return Path(data_dir) / 'cache' / 'geoip' / DATABASE_NAME


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