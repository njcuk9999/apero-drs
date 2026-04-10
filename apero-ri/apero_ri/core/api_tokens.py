#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API token management: generation, validation, and storage.

Each user may have one active API token (a random 64-char hex string).
Tokens are stored in ``~/.ari/secret/api_tokens.json`` with the same
security hardening as share tokens (chmod 0o600).

Token file structure::

    {
      "<hex_token>": {
        "username": "alice",
        "created_at": "2026-03-27T14:30:00+00:00",
        "label": "my laptop"
      }
    }
"""

from __future__ import annotations

import json
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from apero_ri.core.secret_store import (
    get_ari_dir,
    resolve_secret_file,
)

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.api_tokens"

_TOKEN_BYTES = 32  # 32 bytes → 64 hex chars
_lock = threading.Lock()


# =============================================================================
# Low-level I/O
# =============================================================================
def _tokens_path() -> Path:
    """Return the managed path for api_tokens.json."""
    legacy = [get_ari_dir() / "admin" / "api_tokens.json"]
    return resolve_secret_file("api_tokens.json", legacy_paths=legacy)


def _load() -> Dict[str, Any]:
    path = _tokens_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(tokens: Dict[str, Any]) -> None:
    path = _tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(tokens, fh, indent=2, default=str)
    try:
        path.chmod(0o600)
    except OSError:
        pass


# =============================================================================
# Public API
# =============================================================================
def generate_token(username: str, label: str = "") -> str:
    """Generate a new API token for *username*, revoking any old one.

    Returns the new token string (64 hex chars).
    """
    with _lock:
        tokens = _load()
        # Revoke any existing tokens for this user
        tokens = {
            tok: info
            for tok, info in tokens.items()
            if info.get("username") != username
        }
        new_token = secrets.token_hex(_TOKEN_BYTES)
        tokens[new_token] = {
            "username": username,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "label": str(label or "").strip(),
        }
        _save(tokens)
    return new_token


def revoke_token(username: str) -> bool:
    """Revoke all tokens for *username*. Returns True if any were removed."""
    with _lock:
        tokens = _load()
        before = len(tokens)
        tokens = {
            tok: info
            for tok, info in tokens.items()
            if info.get("username") != username
        }
        if len(tokens) < before:
            _save(tokens)
            return True
        return False


def validate_token(token: str) -> Optional[str]:
    """Validate *token* and return the username, or None if invalid."""
    if not token or not isinstance(token, str):
        return None
    # Constant-time-ish lookup (dict is O(1) but we still want to
    # avoid timing leaks on the string itself)
    with _lock:
        tokens = _load()
    info = tokens.get(token)
    if info and isinstance(info, dict):
        return info.get("username")
    return None


def get_user_token_info(username: str) -> Optional[Dict[str, Any]]:
    """Return token metadata for *username*, or None if no token exists.

    Returns dict with keys: ``created_at``, ``label``, ``token_prefix``
    (first 8 chars for display).
    """
    with _lock:
        tokens = _load()
    for tok, info in tokens.items():
        if info.get("username") == username:
            return {
                "created_at": info.get("created_at", ""),
                "label": info.get("label", ""),
                "token_prefix": tok[:8],
            }
    return None
