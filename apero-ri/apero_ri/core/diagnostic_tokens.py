#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Short-lived, read-only diagnostic grants, independent of user API tokens."""

import fcntl
import hashlib
import json
import os
import secrets
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator

from apero_ri.base import base
from apero_ri.core import secret_store

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.diagnostic_tokens'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
MAX_HOURS = 24

# =============================================================================
# Define functions
# =============================================================================
@contextmanager
def _store() -> Iterator[dict]:
    """Lock and atomically update the private grant store.

    :return: Mutable grants indexed by SHA-256 token digest.
    """
    root = secret_store.get_ari_dir() / 'secret'
    root.mkdir(parents=True, exist_ok=True)
    path = root / 'diagnostic_tokens.json'
    lock_path = root / '.diagnostic_tokens.lock'
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, 'r+') as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        data = json.loads(path.read_text()) if path.exists() else dict()
        yield data
        with tempfile.NamedTemporaryFile(mode='w', dir=root,
                                         delete=False) as temporary:
            temporary_path = temporary.name
            try:
                json.dump(data, temporary)
                temporary.flush()
                os.fsync(temporary.fileno())
                os.replace(temporary_path, path)
            finally:
                if os.path.exists(temporary_path):
                    os.unlink(temporary_path)


def issue(actor: str, profiles: list[list[str]], hours: int = MAX_HOURS,
          label: str = '') -> dict[str, Any]:
    """Issue an expiring grant for explicit instrument/profile pairs.

    :param actor: Issuing administrator username.
    :param profiles: Selected [instrument, profile ID] pairs.
    :param hours: Lifetime in whole hours, between 1 and 24.
    :param label: Administrator's identifying label.
    :return: Grant metadata and the token, shown only on creation.
    """
    if type(hours) is not int or not 1 <= hours <= MAX_HOURS:
        raise ValueError('invalid_diagnostic_grant_lifetime')
    if not profiles or len(profiles) > 100:
        raise ValueError('invalid_diagnostic_profile_count')
    for pair in profiles:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError('invalid_profile_scope')
        if not all(isinstance(value, str) and value for value in pair):
            raise ValueError('invalid_profile_scope')
    now = datetime.now(timezone.utc)
    token = 'ari_diag_' + secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode()).hexdigest()
    grant = dict(id=secrets.token_hex(12), actor=actor, label=label[:120],
                 profiles=profiles, created_at=now.isoformat(),
                 expires_at=(now + timedelta(hours=hours)).isoformat(),
                 revoked=False)
    with _store() as data:
        data[digest] = grant
    return dict(grant, token=token)


def validate(token: str) -> dict[str, Any] | None:
    """Validate a grant without accepting session or general API tokens.

    :param token: Bearer credential supplied in an authorization header.
    :return: Active grant metadata, or None.
    """
    if not token.startswith('ari_diag_') or len(token) > 128:
        return None
    digest = hashlib.sha256(token.encode()).hexdigest()
    with _store() as data:
        grant = data.get(digest)
        if not grant or grant.get('revoked'):
            return None
        expires = datetime.fromisoformat(grant['expires_at'])
        if expires <= datetime.now(timezone.utc):
            return None
        return dict(grant)


def list_grants() -> list[dict[str, Any]]:
    """List metadata without revealing tokens or stored digests.

    :return: Grants ordered newest first with their current state.
    """
    now = datetime.now(timezone.utc)
    with _store() as data:
        grants = []
        for value in data.values():
            grant = dict(value)
            expired = datetime.fromisoformat(grant['expires_at']) <= now
            grant['state'] = ('revoked' if grant['revoked'] else
                              'expired' if expired else 'active')
            grants.append(grant)
    return sorted(grants, key=lambda grant: grant['created_at'], reverse=True)


def revoke(grant_id: str) -> bool:
    """Immediately revoke a grant by its public identifier.

    :param grant_id: Identifier from the grant listing.
    :return: Whether a matching grant was found.
    """
    with _store() as data:
        for grant in data.values():
            if grant['id'] == grant_id:
                grant['revoked'] = True
                return True
    return False


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================