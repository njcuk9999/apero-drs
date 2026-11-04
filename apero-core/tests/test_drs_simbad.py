#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for SIMBAD mirror selection in aperocore.core.drs_simbad."""
from typing import List

import pytest

from aperocore.core import drs_simbad


@pytest.fixture(autouse=True)
def _clear_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Give every test an empty per-process selection cache."""
    monkeypatch.setattr(drs_simbad, '_SELECTED_URL', dict())


def test_select_falls_back_to_first_responding_mirror(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """A down main server should select the next responding mirror."""
    checked: List[str] = []

    def _fake_is_up(url: str, timeout: float) -> bool:
        checked.append(url)
        return 'harvard' in url

    monkeypatch.setattr(drs_simbad, 'simbad_tap_is_up', _fake_is_up)
    urls = ['https://main/sim-tap', 'https://harvard/sim-tap']
    assert drs_simbad.select_simbad_url(urls) == urls[1]
    # second call is served from the cache (no new checks)
    assert drs_simbad.select_simbad_url(urls) == urls[1]
    assert checked == urls


def test_select_returns_main_when_all_down(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """With no responding server the main url is returned."""
    monkeypatch.setattr(drs_simbad, 'simbad_tap_is_up',
                        lambda url, timeout: False)
    urls = ['https://main/sim-tap', 'https://mirror/sim-tap']
    assert drs_simbad.select_simbad_url(urls) == urls[0]


def test_select_single_url_is_not_checked(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """A single url has no fallback, so no network check is made."""

    def _fail(url: str, timeout: float) -> bool:
        raise AssertionError('should not be called')

    monkeypatch.setattr(drs_simbad, 'simbad_tap_is_up', _fail)
    assert drs_simbad.select_simbad_url(['https://only']) == 'https://only'


def test_select_rejects_empty_list() -> None:
    """An empty url list is a configuration error."""
    with pytest.raises(ValueError):
        drs_simbad.select_simbad_url([])


def test_simbad_server_extracts_host() -> None:
    """Host names are extracted from full urls and bare hosts."""
    url = 'https://simbad.harvard.edu/simbad/sim-tap'
    assert drs_simbad.simbad_server(url) == 'simbad.harvard.edu'
    assert drs_simbad.simbad_server('simbad.harvard.edu') == (
        'simbad.harvard.edu')
