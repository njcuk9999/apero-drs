#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for helper-level functions in `apero.io.drs_fits`."""

from pathlib import Path

import numpy as np
from astropy.io import fits

from apero.io import drs_fits


def test_header_nan_check_converts_float_special_values() -> None:
    """Header NaN check should map NaN/INF values to string sentinels."""
    fn = drs_fits.Header._Header__nan_check
    assert fn(np.nan) == 'NaN'
    assert fn(np.inf) == 'INF'
    assert fn(-np.inf) == '-INF'


def test_header_nan_check_reconstructs_float_when_dtype_float() -> None:
    """With dtype=float, NaN-like strings should map back to float values."""
    fn = drs_fits.Header._Header__nan_check
    assert np.isnan(fn('NaN', dtype=float))
    assert fn('INF', dtype=float) == np.inf
    assert fn('-INF', dtype=float) == -np.inf


def test_check_dtype_for_header_handles_basic_types(tmp_path) -> None:
    """Header dtype helper should normalize bool/int/float/other values."""
    fpath = tmp_path / 'file.txt'
    fpath.write_text('x', encoding='utf-8')
    assert drs_fits.check_dtype_for_header(True) == 1
    assert drs_fits.check_dtype_for_header(False) == 0
    assert drs_fits.check_dtype_for_header(5) == 5
    assert drs_fits.check_dtype_for_header(np.nan) == 'NaN'
    assert drs_fits.check_dtype_for_header(np.inf) == 'INF'
    assert drs_fits.check_dtype_for_header(str(fpath)) == 'file.txt'


def test_find_named_extensions_by_exact_name(tmp_path) -> None:
    """Extension finder should return indices matching exact EXTNAME."""
    fname = tmp_path / 'x.fits'
    phdu = fits.PrimaryHDU()
    hdu1 = fits.ImageHDU(name='SCIENCE')
    hdu2 = fits.ImageHDU(name='CALIB')
    fits.HDUList([phdu, hdu1, hdu2]).writeto(fname)
    out = drs_fits.find_named_extensions(str(fname), name='SCIENCE')
    assert out == [1]


def test_find_named_extensions_by_prefix(tmp_path) -> None:
    """Extension finder should return indices with matching name prefix."""
    fname = tmp_path / 'y.fits'
    phdu = fits.PrimaryHDU()
    hdu1 = fits.ImageHDU(name='SCI_A')
    hdu2 = fits.ImageHDU(name='SCI_B')
    hdu3 = fits.ImageHDU(name='CAL')
    fits.HDUList([phdu, hdu1, hdu2, hdu3]).writeto(fname)
    out = drs_fits.find_named_extensions(str(fname), startswith='SCI_')
    assert out == [1, 2]

