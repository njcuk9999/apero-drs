#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Additional unit tests for pure helpers in `apero.core.drs_astrometrics`."""

from apero.core import drs_astrometrics as astro


def test_nested_value_and_source_from_mixed_entry() -> None:
    """Nested helpers should read `value`/`source` only when value is a dict."""
    entry = {'RA': {'value': 1.23, 'source': 'SIMBAD'}, 'DEC': 9.87}
    assert astro._nested_value(entry, 'RA') == 1.23
    assert astro._nested_source(entry, 'RA') == 'SIMBAD'
    assert astro._nested_value(entry, 'DEC') == 9.87
    assert astro._nested_source(entry, 'DEC') is None


def test_legacy_view_maps_expected_keys() -> None:
    """`legacy_view` should expose legacy keys used by SQL-era callers."""
    entry = {
        'APERO_NAME': 'GL699',
        'RA': {'value': 269.0, 'source': 'SIMBAD'},
        'DEC': {'value': 4.0, 'source': 'SIMBAD'},
        'ALIASES': ['BARNARD'],
    }
    legacy = astro.legacy_view(entry)
    assert legacy is not None
    assert legacy['OBJNAME'] == 'GL699'
    assert legacy['RA_DEG'] == 269.0
    assert legacy['RA_SOURCE'] == 'SIMBAD'
    assert legacy['ALIASES'] == ['BARNARD']


def test_format_ra_hms_and_dec_dms_have_expected_sign_and_separators() -> None:
    """Sexagesimal formatters should return canonical delimiter/sign styles."""
    ra = astro._format_ra_hms(15.0)
    dec_pos = astro._format_dec_dms(10.5)
    dec_neg = astro._format_dec_dms(-10.5)
    assert ra is not None and ':' in ra
    assert dec_pos is not None and dec_pos.startswith('+')
    assert dec_neg is not None and dec_neg.startswith('-')


def test_galactic_and_ecliptic_helpers_return_finite_pair() -> None:
    """Coordinate-conversion helpers should return two finite values."""
    glon, glat = astro._galactic_from_radec(269.0, 4.0)
    elon, elat = astro._ecliptic_from_radec(269.0, 4.0)
    assert glon is not None and glat is not None
    assert elon is not None and elat is not None


def test_doy_label_for_start_and_end_of_year() -> None:
    """`_doy_label` should map day indexes to compact month/day labels."""
    assert astro._doy_label(0) == 'Jan 01'
    assert astro._doy_label(364) == 'Dec 31'


def test_telluric_windows_returns_none_when_inputs_missing() -> None:
    """Return `None` when telluric window helper inputs are incomplete."""
    assert astro._telluric_windows(None, 0.0, 0.0) is None
    assert astro._telluric_windows(0.0, None, 0.0) is None
    assert astro._telluric_windows(0.0, 0.0, None) is None


def test_absolute_mag_returns_none_for_invalid_parallax() -> None:
    """Absolute magnitude helper rejects non-positive parallax values."""
    assert astro._absolute_mag(10.0, 0.0) is None
    assert astro._absolute_mag(10.0, -1.0) is None


def test_absolute_mag_known_value() -> None:
    """Absolute magnitude should match the distance-modulus relation."""
    # plx=100 mas -> distance=10 pc, so M = m - 5*log10(10) + 5 = m.
    assert astro._absolute_mag(12.3, 100.0) == 12.3


def test_teff_from_gaia_colors_out_of_range_returns_none_pair() -> None:
    """Teff calibration should return None values outside valid color range."""
    t_jh, t_gaia = astro._teff_from_gaia_colors(1.0, 0.9, 10.0, 9.9)
    assert t_jh is None
    assert t_gaia is None


def test_teff_from_gaia_colors_valid_range_returns_gaia_value() -> None:
    """Within valid BP-RP range, Gaia-only Teff estimate is expected."""
    t_jh, t_gaia = astro._teff_from_gaia_colors(3.2, 1.4, None, None)
    assert t_jh is None
    assert t_gaia is not None


def test_propagate_to_epoch_no_pm_returns_input_coordinates() -> None:
    """Epoch propagation should no-op when proper motion values are absent."""
    ra, dec = astro._propagate_to_epoch(
        ra_deg=20.0,
        dec_deg=-10.0,
        pmra=None,
        pmdec=None,
        source_epoch_jyear=2000.0,
        target_epoch_jyear=2015.5,
    )
    assert ra == 20.0
    assert dec == -10.0



