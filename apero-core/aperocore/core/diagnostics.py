#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bounded, credential-redacted inspection helpers for diagnostic reports."""

import json
import math
import os
import platform
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

from aperocore.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.core.diagnostics'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
FILE_LIMIT = 8 * 1024 * 1024
ROW_LIMIT = 100
SENSITIVE = re.compile(
    r'password|passwd|passphrase|secret|token|credential|authorization|'
    r'api.?key|access.?key|(^|_)pwd$|^pass$|'
    r'cookie|private.?key|(^|_)kwargs$|(^|_)runstring$|(^|_)command(s)?$|'
    r'pre_gui_commands|^args$|^cmd$|^environment$', re.IGNORECASE)
ASSIGNMENT = re.compile(
    r'(?i)([\w-]*(?:password|passwd|passphrase|token|secret|credential|'
    r'api.?key|access.?key|pwd)'
    r'[\w-]*\s*[=:]\s*)(?:"[^"]*"|\x27[^\x27]*\x27|[^\s,;]+)')

# =============================================================================
# Define functions
# =============================================================================
def secret_values(value: Any) -> list[str]:
    """Find configured secrets for removing echoes in logs and errors.

    :param value: Nested configuration mapping or sequence.
    :return: Sensitive string values, longest first.
    """
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if SENSITIVE.search(str(key)) and isinstance(item, str) and item:
                found.add(item)
            else:
                found.update(secret_values(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.update(secret_values(item))
    return sorted(found, key=len, reverse=True)


def redact(value: Any, known_secrets: list[str] | None = None) -> Any:
    """Remove credential fields and credential-shaped string fragments.

    :param value: JSON-like diagnostic data.
    :param known_secrets: Configured secrets that may appear in free text.
    :return: JSON-serializable redacted copy.
    """
    known_secrets = known_secrets or []
    if isinstance(value, dict):
        return {str(key): '[REDACTED]' if SENSITIVE.search(str(key)) else
                redact(item, known_secrets) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [redact(item, known_secrets) for item in value]
    if value is None or isinstance(value, (bool, int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        return value
    text = str(value)
    for secret in known_secrets:
        text = text.replace(secret, '[REDACTED]')
    text = re.sub(r'(?i)(Bearer\s+)\S+', r'\1[REDACTED]', text)
    text = re.sub(r'(://)[^/@\s]+:[^/@\s]+@', r'\1[REDACTED]@', text)
    text = re.sub(r'ari_diag_[A-Za-z0-9_-]+', '[REDACTED]', text)
    return ASSIGNMENT.sub(r'\1[REDACTED]', text)


def runtime() -> dict[str, Any]:
    """Describe the current runtime without exporting the environment.

    :return: Host, executable, version, and package provenance metadata.
    """
    packages = dict()
    for name in ('aperocore', 'apero', 'apero_ri', 'lbl', 'numpy',
                 'astropy', 'flask', 'bokeh', 'sqlalchemy'):
        try:
            distribution = metadata.distribution(name)
            packages[name] = dict(version=distribution.version,
                                  location=str(distribution.locate_file('')))
        except metadata.PackageNotFoundError:
            packages[name] = dict(installed=False)
    sources = dict()
    for name in ('aperocore', 'apero', 'apero_ri'):
        module = sys.modules.get(name)
        if module is not None:
            sources[name] = dict(path=getattr(module, '__file__', None),
                                 version=getattr(module, '__version__', None))
    checkout = dict()
    try:
        prefix = ['git', '-C', str(Path(__file__).parent)]
        commit = subprocess.run(prefix + ['rev-parse', 'HEAD'],
                                capture_output=True, text=True, timeout=3,
                                check=True)
        status = subprocess.run(prefix + ['status', '--short',
                                           '--untracked-files=no'],
                                capture_output=True, text=True, timeout=3,
                                check=True)
        checkout = dict(commit=commit.stdout.strip(),
                         tracked_changes=status.stdout.splitlines()[:100])
    except (OSError, subprocess.SubprocessError):
        checkout = dict(available=False)
    return dict(host=socket.gethostname(), platform=platform.platform(),
                python=sys.version, executable=sys.executable,
                generated_at=datetime.now(timezone.utc).isoformat(),
                packages=packages, imported_sources=sources,
                core_checkout=checkout)


def file_info(path: Path) -> dict[str, Any]:
    """Inspect metadata without reading a file or following a symlink.

    :param path: Configured path or an enumerated child.
    :return: Existence, permissions, size, and modification metadata.
    """
    result = dict(path=str(path))
    try:
        info = path.lstat()
        result.update(exists=True, symlink=path.is_symlink(),
                      directory=path.is_dir(), bytes=info.st_size,
                      modified_at=info.st_mtime, mode=oct(info.st_mode & 0o777),
                      readable=os.access(path, os.R_OK),
                      writable=os.access(path, os.W_OK))
    except OSError as error:
        result.update(exists=False, error_type=type(error).__name__)
    return result


def inventory(root: Path, limit: int = ROW_LIMIT) -> dict[str, Any]:
    """List a bounded first level of an approved directory.

    :param root: Configured data or cache directory.
    :param limit: Maximum number of child entries to inspect.
    :return: Root metadata, children, and an explicit truncation flag.
    """
    result = dict(root=file_info(root), entries=[], truncated=False)
    try:
        with os.scandir(root) as entries:
            for index, entry in enumerate(entries):
                if index >= limit:
                    result['truncated'] = True
                    break
                result['entries'].append(file_info(Path(entry.path)))
    except OSError as error:
        result['error_type'] = type(error).__name__
    return result


def read_json(path: Path, root: Path) -> dict[str, Any]:
    """Read bounded JSON only within an approved root, never a symlink.

    :param path: Selected diagnostic artifact.
    :param root: Approved containing directory.
    :return: Parsed payload or explicit unavailable/truncated metadata.
    """
    result = file_info(path)
    try:
        if path.is_symlink() or not path.resolve().is_relative_to(
                root.resolve()):
            return dict(result, skipped='outside_root_or_symlink')
        with path.open('rb') as handle:
            raw = handle.read(FILE_LIMIT + 1)
        if len(raw) > FILE_LIMIT:
            return dict(result, truncated=True, limit_bytes=FILE_LIMIT)
        return dict(result, data=json.loads(raw))
    except (OSError, ValueError) as error:
        return dict(result, error_type=type(error).__name__)


def log_tail(path: Path, root: Path) -> dict[str, Any]:
    """Read a bounded tail from a selected log inside its configured root.

    :param path: Log selected by trusted recipe or queue metadata.
    :param root: Configured log root.
    :return: Tail text and metadata, or explicit rejection information.
    """
    result = file_info(path)
    try:
        if path.is_symlink() or not path.resolve().is_relative_to(
                root.resolve()):
            return dict(result, skipped='outside_root_or_symlink')
        with path.open('rb') as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - 65536))
            raw = handle.read(65536)
        return dict(result, text=raw.decode('utf-8', errors='replace'),
                    truncated=size > 65536)
    except OSError as error:
        return dict(result, error_type=type(error).__name__)


def database_rows(url: Any, query: str, bindings: dict) -> list[dict]:
    """Execute a trusted SELECT with connection and server-side time limits.

    :param url: SQLAlchemy URL for the configured database.
    :param query: Collector-owned SELECT statement.
    :param bindings: Bound diagnostic filters.
    :return: At most 101 rows; unsupported drivers are rejected.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import make_url

    url = make_url(url)
    is_select = query.lstrip().upper().startswith('SELECT ')
    if url.drivername != 'mysql+pymysql' or not is_select:
        raise ValueError('unsupported_diagnostic_query_or_driver')
    options = dict(connect_args=dict(connect_timeout=5, read_timeout=15,
                                     write_timeout=5))
    engine = create_engine(url, **options)
    try:
        with engine.connect() as connection:
            result = connection.execute(text('SELECT VERSION()'))
            version = str(result.scalar())
            setting = ('MAX_STATEMENT_TIME=10' if 'mariadb' in version.lower()
                       else 'MAX_EXECUTION_TIME=10000')
            connection.execute(text('SET SESSION ' + setting))
            result = connection.execute(text(query), bindings)
            return [dict(row) for row in result.mappings().fetchmany(101)]
    finally:
        engine.dispose()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================