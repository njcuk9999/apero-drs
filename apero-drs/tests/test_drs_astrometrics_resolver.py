#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mock-based tests for astrometric resolver helper paths."""

from apero.core import drs_astrometrics as astro


def test_resolve_from_gaia_name_rejects_non_gaia_labels() -> None:
    """Gaia-name resolver should return None for non-Gaia input strings."""
    assert astro._resolve_from_gaia_name('GL699') is None


def test_resolve_from_gaia_name_maps_vizier_row(monkeypatch) -> None:
    """Gaia-name resolver should map VizieR row fields into result dict."""

    def _fake_vizier(adql, timeout=30, url=None):  # noqa: ANN001
        return {'data': [[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]}

    monkeypatch.setattr(astro, '_vizier_json', _fake_vizier)
    out = astro._resolve_from_gaia_name('Gaia DR3 123456')
    assert out is not None
    assert out['simbad_main_id'] == 'Gaia DR3 123456'
    assert out['gaia_source_id'] == '123456'
    assert out['ra_deg'] == '10'
    assert out['dec_deg'] == '20'


def test_resolve_from_name_falls_back_to_gaia_when_simbad_none(
    monkeypatch,
) -> None:
    """Top-level resolver should fallback to Gaia-name path on SIMBAD miss."""

    def _fake_simbad(*args, **kwargs):  # noqa: ANN002, ANN003
        return None

    fallback = {'simbad_main_id': 'Gaia DR3 9'}

    def _fake_gaia_name(name, vizier_url=None):  # noqa: ANN001
        return fallback

    monkeypatch.setattr(astro, '_simbad_json', _fake_simbad)
    monkeypatch.setattr(astro, '_resolve_from_gaia_name', _fake_gaia_name)
    out = astro._resolve_from_name('Gaia DR3 9')
    assert out == fallback


def test_fetch_wise_by_designation_handles_missing_rows(monkeypatch) -> None:
    """WISE fetch helper should return None when VizieR yields no rows."""

    def _fake_vizier(adql, timeout=30, url=None):  # noqa: ANN001
        return {'data': []}

    monkeypatch.setattr(astro, '_vizier_json', _fake_vizier)
    out = astro._fetch_wise_by_designation('J1234+5678')
    assert out is None


def test_fetch_wise_by_designation_returns_tuple_for_valid_row(
    monkeypatch,
) -> None:
    """WISE fetch helper should return tuple when row has all fields."""

    def _fake_vizier(adql, timeout=30, url=None):  # noqa: ANN001
        row = ['id', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return {'data': [row]}

    monkeypatch.setattr(astro, '_vizier_json', _fake_vizier)
    out = astro._fetch_wise_by_designation('J1234+5678')
    assert isinstance(out, tuple)
    assert len(out) == 11

