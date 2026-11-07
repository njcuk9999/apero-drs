#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression coverage for shared legacy Google Sheets access."""

from types import SimpleNamespace

import gspread
import pytest

from apero_ri.tasks import legacy_gsheet_auth as auth


def _api_error(status):
    response = SimpleNamespace(
        status_code=status,
        json=lambda: {'error': {'code': status, 'message': 'x'}},
        text='x',
    )
    return gspread.exceptions.APIError(response)


def test_service_account_needs_no_refresh_token(monkeypatch):
    """Service-account files must not go through the OAuth refresh path."""
    from google.oauth2 import service_account
    seen = {}

    def fake_info(info, scopes):
        seen['scopes'] = scopes
        return 'sa-creds'

    monkeypatch.setattr(
        service_account.Credentials, 'from_service_account_info',
        staticmethod(fake_info),
    )
    creds = auth.build_credentials({'type': 'service_account'}, ['s'])
    assert creds == 'sa-creds' and seen['scopes'] == ['s']


def test_oauth_without_refresh_token_is_clear_error():
    with pytest.raises(ValueError, match='refresh_token'):
        auth.build_credentials({'type': 'authorized_user'}, ['s'])


def test_transient_errors_are_retried(monkeypatch):
    calls = []

    class Client:
        def open_by_key(self, key):
            calls.append(key)
            if len(calls) < 3:
                raise _api_error(503)
            return 'sheet'

    monkeypatch.setattr(auth, 'build_credentials', lambda p, s: None)
    monkeypatch.setattr(gspread, 'authorize', lambda c: Client())
    monkeypatch.setattr(auth.time, 'sleep', lambda s: None)
    assert auth.open_spreadsheet({}, 'id', []) == 'sheet'
    assert len(calls) == 3


def test_permanent_errors_are_not_retried(monkeypatch):
    calls = []

    class Client:
        def open_by_key(self, key):
            calls.append(key)
            raise _api_error(403)

    monkeypatch.setattr(auth, 'build_credentials', lambda p, s: None)
    monkeypatch.setattr(gspread, 'authorize', lambda c: Client())
    with pytest.raises(gspread.exceptions.APIError):
        auth.open_spreadsheet({}, 'id', [])
    assert len(calls) == 1
