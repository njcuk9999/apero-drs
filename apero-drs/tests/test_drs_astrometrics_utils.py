#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for pure utility helpers in `apero.core.drs_astrometrics`."""

from apero.core import drs_astrometrics


def test_clean_object_handles_signs_and_spaces() -> None:
    """`clean_object` should normalize signs, spaces, and case."""
    raw_name = ' Gl 699 + A '
    cleaned = drs_astrometrics.clean_object(raw_name)
    assert cleaned == 'GL_699_P_A'


def test_clean_object_null_input_returns_null_literal() -> None:
    """`clean_object` should return `'Null'` for null-like values."""
    assert drs_astrometrics.clean_object(None) == 'Null'
    assert drs_astrometrics.clean_object(' none ') == 'Null'


def test_name_search_variants_starts_with_canonical_value() -> None:
    """The first variant should be the canonical cleaned object name."""
    variants = drs_astrometrics.name_search_variants('Gl 699 +A')
    assert variants
    assert variants[0] == drs_astrometrics.clean_object('Gl 699 +A')


def test_name_search_variants_returns_empty_for_null_like_values() -> None:
    """Null-like names should not generate search variants."""
    assert drs_astrometrics.name_search_variants(None) == []
    assert drs_astrometrics.name_search_variants('  ') == []


def test_is_null_accepts_none_and_known_text_tokens() -> None:
    """`_is_null` should detect both None and string null markers."""
    assert drs_astrometrics._is_null(None)
    assert drs_astrometrics._is_null('Null')
    assert drs_astrometrics._is_null('nan')
    assert not drs_astrometrics._is_null(0)


def test_nv_and_pf_normalize_values() -> None:
    """`_nv` and `_pf` should normalize empty and numeric-like values."""
    assert drs_astrometrics._nv('  abc  ') == 'abc'
    assert drs_astrometrics._nv('null') is None
    assert drs_astrometrics._pf('3.5') == 3.5
    assert drs_astrometrics._pf('not-a-number') is None


def test_to_sync_url_adds_sync_only_when_needed() -> None:
    """`_to_sync_url` should preserve sync URLs and normalize base URLs."""
    default = 'https://example.org/tap/sync'
    assert drs_astrometrics._to_sync_url(None, default) == default
    assert drs_astrometrics._to_sync_url('https://host/tap', default) == (
        'https://host/tap/sync'
    )
    assert drs_astrometrics._to_sync_url('https://host/tap/sync', default) == (
        'https://host/tap/sync'
    )


def test_safe_filename_appends_yaml_extension() -> None:
    """`_safe_filename` should return a sanitized name with `.yaml` suffix."""
    filename = drs_astrometrics._safe_filename('Gl 699')
    assert filename == 'GL_699.yaml'


def test_sep_arcsec_is_zero_for_identical_coordinates() -> None:
    """Angular separation should be zero when both points are identical."""
    sep = drs_astrometrics._sep_arcsec(10.0, 20.0, 10.0, 20.0)
    assert abs(sep) < 1e-12


def test_propagate_returns_input_when_pm_missing() -> None:
    """`_propagate` should be a no-op when proper motion is unavailable."""
    ra_out, dec_out = drs_astrometrics._propagate(15.0, -30.0, None, 1.0, 5.0)
    assert ra_out == 15.0
    assert dec_out == -30.0


def test_parse_gaia_name_extracts_release_and_source_id() -> None:
    """`_parse_gaia_name` should parse Gaia DR names in canonical format."""
    parsed = drs_astrometrics._parse_gaia_name('Gaia DR3 123456')
    assert parsed == ('dr3', '123456')
    assert drs_astrometrics._parse_gaia_name('not gaia') is None


def test_extract_wisea_designation_handles_prefix() -> None:
    """`_extract_wisea_designation` should strip WISEA prefix only."""
    design = drs_astrometrics._extract_wisea_designation('WISEA J1234+5678')
    assert design == 'J1234+5678'
    assert drs_astrometrics._extract_wisea_designation('Gaia DR3 1') is None

