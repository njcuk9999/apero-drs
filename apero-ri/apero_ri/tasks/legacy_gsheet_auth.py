#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared Google Sheets access for the legacy GSheet sync tasks."""

from __future__ import annotations

import time
from typing import Any, Dict, Sequence

TOKEN_URI = 'https://oauth2.googleapis.com/token'
RETRY_STATUS = {429, 500, 502, 503, 504}
RETRY_DELAYS = (2.0, 5.0, 10.0)


def build_credentials(payload: Dict[str, Any],
                      default_scopes: Sequence[str]) -> Any:
    """Return service-account or OAuth user credentials from *payload*."""
    scopes = payload.get('scopes')
    if not isinstance(scopes, list) or not scopes:
        scopes = list(default_scopes)
    if payload.get('type') == 'service_account':
        from google.oauth2.service_account import Credentials
        return Credentials.from_service_account_info(payload, scopes=scopes)
    refresh_token = str(payload.get('refresh_token') or '').strip()
    if not refresh_token:
        raise ValueError(
            'Google credential file is neither a service account nor an '
            'OAuth user token with a refresh_token.'
        )
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=str(payload.get('token_uri') or TOKEN_URI),
        client_id=str(payload.get('client_id') or ''),
        client_secret=str(payload.get('client_secret') or ''),
        scopes=scopes,
    )
    creds.refresh(Request())
    return creds


def _is_transient(exc: Exception) -> bool:
    """Return True for Google API errors that are worth retrying."""
    response = getattr(exc, 'response', None)
    return getattr(response, 'status_code', None) in RETRY_STATUS


def open_spreadsheet(payload: Dict[str, Any], sheet_id: str,
                     default_scopes: Sequence[str]) -> Any:
    """Open *sheet_id*, retrying transient Google API failures."""
    import gspread

    client = gspread.authorize(build_credentials(payload, default_scopes))
    for delay in RETRY_DELAYS:
        try:
            return client.open_by_key(sheet_id)
        except gspread.exceptions.APIError as exc:
            if not _is_transient(exc):
                raise
        time.sleep(delay)
    return client.open_by_key(sheet_id)
