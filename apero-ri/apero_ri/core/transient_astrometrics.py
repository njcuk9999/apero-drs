#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Transient (in-memory) astrometric entries.

Lets a user who does **not** have ``upload.astrometrics`` permission
"resolve online" against SIMBAD/Gaia/VizieR and still render the
SED, HR diagram, finder chart, etc. for that target during their
session, without persisting the unvetted entry to the on-disk
APERO astrometric database.

Entries are scoped per-user (or to ``'anonymous'``) and expire
after :data:`DEFAULT_TTL_SECONDS` (1 hour).

A user with ``upload.astrometrics`` is expected to write directly
to the disk store via ``drs_astrometrics.upload_entry`` instead.

Created on 2026-04-23

@author: cook
"""
from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional


__NAME__ = 'apero_ri.core.transient_astrometrics'


# default time-to-live for a transient entry (seconds)
DEFAULT_TTL_SECONDS = 60 * 60  # 1 hour

# in-process store: {username: {apero_name_upper: (entry, expires)}}
_STORE: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()


def _key(name: str) -> str:
    """Normalise a target name for case-insensitive lookup."""
    return str(name or '').strip().upper()


def _user_key(username: Optional[str]) -> str:
    """Map ``None`` / empty to a stable bucket name."""
    u = (username or 'anonymous').strip()
    return u or 'anonymous'


def _purge_expired_locked(now: float) -> None:
    """Drop expired entries; caller must already hold ``_LOCK``."""
    empty_users = []
    for user, bucket in _STORE.items():
        dead = [k for k, (_, exp) in bucket.items() if exp <= now]
        for k in dead:
            bucket.pop(k, None)
        if not bucket:
            empty_users.append(user)
    for user in empty_users:
        _STORE.pop(user, None)


def put(username: Optional[str], name: str,
        entry: Dict[str, Any],
        ttl_seconds: int = DEFAULT_TTL_SECONDS) -> Dict[str, Any]:
    """Store a transient yaml-shaped astrometric entry.

    :param username: the user who owns the entry
    :param name: the target name to key by (any alias works -- both
                 the supplied ``name`` and the entry's APERO_NAME /
                 SIMBAD_NAME are indexed so subsequent lookups can
                 use any of them)
    :param entry: dict, the yaml-shaped astrometric entry
    :param ttl_seconds: lifetime in seconds (default 1h)
    :return: the entry that was stored (same instance)
    """
    if not isinstance(entry, dict) or not entry:
        return entry
    now = time.time()
    expires = now + max(60, int(ttl_seconds))
    user = _user_key(username)
    with _LOCK:
        _purge_expired_locked(now)
        bucket = _STORE.setdefault(user, {})
        # index by every name we know about
        keys = set()
        keys.add(_key(name))
        for nk in ('APERO_NAME', 'SIMBAD_NAME', 'ORIGINAL_NAME'):
            v = entry.get(nk)
            if isinstance(v, str) and v.strip():
                keys.add(_key(v))
        aliases = entry.get('ALIASES')
        if isinstance(aliases, str):
            aliases = aliases.split('|')
        if isinstance(aliases, (list, tuple)):
            for alias in aliases:
                if isinstance(alias, str) and alias.strip():
                    keys.add(_key(alias))
        for k in keys:
            if k:
                bucket[k] = (entry, expires)
    return entry


def get(username: Optional[str],
        name: str) -> Optional[Dict[str, Any]]:
    """Look up a transient entry by name (case-insensitive).

    Falls back to the ``'anonymous'`` bucket so transient entries
    created when the request was unauthenticated are still visible
    to the same user once they log in within the same session.

    :param username: the user to look up for
    :param name: the target name (any indexed alias)
    :return: the entry dict or ``None``
    """
    now = time.time()
    k = _key(name)
    if not k:
        return None
    with _LOCK:
        _purge_expired_locked(now)
        for user in (_user_key(username), 'anonymous'):
            bucket = _STORE.get(user)
            if not bucket:
                continue
            hit = bucket.get(k)
            if hit is not None:
                return hit[0]
    return None


def remove(username: Optional[str], name: str) -> bool:
    """Drop a transient entry (if any) keyed by ``name``."""
    user = _user_key(username)
    k = _key(name)
    with _LOCK:
        bucket = _STORE.get(user)
        if not bucket:
            return False
        return bucket.pop(k, None) is not None
