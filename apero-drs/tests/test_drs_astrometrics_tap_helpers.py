#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mocked tests for TAP/JSON/CSV helper utilities in drs_astrometrics."""

from urllib.error import URLError

from apero.core import drs_astrometrics as astro


class _FakeResponse:
    """Small context-manager response object for urlopen monkeypatching."""

    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def test_tap_get_returns_none_on_network_error(monkeypatch) -> None:
    """`_tap_get` should swallow urllib errors and return None."""
    import urllib.request

    def _raise_urlerror(*args, **kwargs):  # noqa: ANN002, ANN003
        raise URLError('network down')

    monkeypatch.setattr(urllib.request, 'urlopen', _raise_urlerror)
    out = astro._tap_get('https://example', 'select 1')
    assert out is None


def test_gaia_csv_parses_simple_payload(monkeypatch) -> None:
    """`_gaia_csv` should parse CSV bytes from TAP into row dictionaries."""

    def _fake_tap_get(*args, **kwargs):  # noqa: ANN002, ANN003
        return b'col1,col2\n1,2\n'

    monkeypatch.setattr(astro, '_tap_get', _fake_tap_get)
    rows = astro._gaia_csv('SELECT 1')
    assert rows is not None
    assert rows[0]['col1'] == '1'
    assert rows[0]['col2'] == '2'


def test_simbad_json_returns_none_on_invalid_json(monkeypatch) -> None:
    """`_simbad_json` should return None when response is not valid JSON."""

    def _fake_tap_get(*args, **kwargs):  # noqa: ANN002, ANN003
        return b'not-json'

    monkeypatch.setattr(astro, '_tap_get', _fake_tap_get)
    assert astro._simbad_json('SELECT 1') is None


def test_vizier_json_uses_uppercase_param_route(monkeypatch) -> None:
    """`_vizier_json` should parse payload through the TAP helper path."""

    def _fake_tap_get(*args, **kwargs):  # noqa: ANN002, ANN003
        return b'{"data": [[1, 2]]}'

    monkeypatch.setattr(astro, '_tap_get', _fake_tap_get)
    payload = astro._vizier_json('SELECT 1')
    assert payload is not None
    assert payload['data'][0] == [1, 2]


def test_tap_get_success_path_reads_response_bytes(monkeypatch) -> None:
    """`_tap_get` should return bytes from a successful urlopen call."""
    import urllib.request

    def _fake_urlopen(req, timeout=30):  # noqa: ANN001
        return _FakeResponse(b'ok')

    monkeypatch.setattr(urllib.request, 'urlopen', _fake_urlopen)
    out = astro._tap_get('https://example', 'select 1')
    assert out == b'ok'

