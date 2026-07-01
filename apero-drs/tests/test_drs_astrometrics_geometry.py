#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Geometry and propagation tests for `apero.core.drs_astrometrics`."""

import numpy as np

from apero.core import drs_astrometrics as astro


def test_sep_arcsec_is_symmetric() -> None:
    """Angular separation should be symmetric when swapping points."""
    sep1 = astro._sep_arcsec(10.0, -5.0, 11.0, -4.5)
    sep2 = astro._sep_arcsec(11.0, -4.5, 10.0, -5.0)
    assert np.isclose(sep1, sep2)


def test_sep_arcsec_antipodal_is_about_180_degrees() -> None:
    """Antipodal coordinates should be approximately 180 degrees apart."""
    sep = astro._sep_arcsec(0.0, 0.0, 180.0, 0.0)
    assert np.isclose(sep, 180.0 * 3600.0, rtol=1e-8)


def test_propagate_no_time_delta_leaves_coordinates_unchanged() -> None:
    """With dt=0 years, propagation should keep coordinates unchanged."""
    ra0, dec0 = 123.456, -22.334
    ra1, dec1 = astro._propagate(ra0, dec0, pmra=200.0, pmdec=-50.0,
                                 dt_yr=0.0)
    assert np.isclose(ra0, ra1)
    assert np.isclose(dec0, dec1)


def test_propagate_changes_position_for_nonzero_pm_and_dt() -> None:
    """With proper motion and nonzero dt, coordinates should be updated."""
    ra0, dec0 = 123.456, -22.334
    ra1, dec1 = astro._propagate(ra0, dec0, pmra=200.0, pmdec=-50.0,
                                 dt_yr=10.0)
    assert abs(ra1 - ra0) > 1e-7
    assert abs(dec1 - dec0) > 1e-7


def test_jd_to_jyear_none_input_returns_none() -> None:
    """Julian-date conversion helper should pass through None inputs."""
    assert astro._jd_to_jyear(None) is None


