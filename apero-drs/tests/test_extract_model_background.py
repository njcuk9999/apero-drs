#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for APERO model-background extraction wrappers."""

import numpy as np

from aperocore.constants import param_functions
from apero.science.extract import model_background
from apero.science.extract import gen_ext
from apero.instruments.select import INSTRUMENTS


ParamDict = param_functions.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def test_model_background_correction_returns_expected_props(
        spirou_params) -> None:
    """The APERO wrapper should return corrected image/background products."""
    ygrid, xgrid = np.indices((32, 40), dtype=float)
    image = 100.0 + 0.1 * xgrid + 0.2 * ygrid
    image_straight = np.array(image)
    model_straight = np.zeros_like(image)
    order_map = np.zeros(image.shape, dtype=int)
    mb_props = model_background.model_background_correction(
        spirou_params, image, image_straight, model_straight, xgrid, ygrid,
        order_map=order_map, model_noshape=image, gain=1.0,
        ron_start=8.0, bkg_box=(7, 5))
    assert mb_props['SCI_BKGSUB'].shape == image.shape
    assert mb_props['SCI_BKGSUB_ERR'].shape == image.shape
    assert mb_props['BKG_NOSHAPE'].shape == image.shape
    assert mb_props['MASK_NOSHAPE'].shape == image.shape
    assert np.isfinite(mb_props['SCI_BKGSUB_ERR']).any()
    assert np.isfinite(mb_props['EFF_RON_FIT'])


def test_model_background_correction_keeps_electron_model_units(
        spirou_params) -> None:
    """The straight-frame model should stay in electron units."""
    image = np.full((16, 20), 10.0)
    model = np.full(image.shape, 4.0)
    mb_props = model_background.model_background_correction(
        spirou_params, image, image, model, np.indices(image.shape)[1],
        np.indices(image.shape)[0], gain=2.0, ron_start=8.0,
        bkg_box=(7, 5))
    assert np.allclose(mb_props['DIFF_STRAIGHT'], 6.0)


def test_run_all_fiber_model_keeps_zero_point_out_of_background_fit(
        spirou_params) -> None:
    """The smooth background should subtract the fiber model, not the zero point."""
    image = np.zeros((8, 12))
    profile1 = np.zeros_like(image)
    profile2 = np.zeros_like(image)
    profile1[2:5, 2:10] = 1.0
    profile2[3:6, 1:11] = 1.0
    image = 4.0 * profile1 + 7.0 * profile2 + 3.0
    geometry = ParamDict()
    geometry['INV_XMAP'] = np.tile(np.arange(12.0), (8, 1))
    geometry['INV_YMAP'] = np.tile(np.arange(8.0)[:, None], (1, 12))
    geometry['DXMAP_NO_SHAPE'] = np.zeros_like(image)
    geometry['SHAPEL'] = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    geometry['SHAPEX'] = np.zeros_like(image)
    geometry['SHAPEY'] = np.zeros_like(image)
    order_map = np.zeros((8, 12), dtype=int)
    order_map[2:4, :] = 1
    order_map[4:6, :] = 2
    order_nearest = np.array(order_map)
    order_profiles = dict(A=profile1, B=profile2)
    props = model_background.run_all_fiber_model(
        spirou_params, image, image, order_profiles, geometry, order_map,
        order_nearest, {'A': (1, 1), 'B': (2, 2)}, np.array([1]),
        np.array([7]), np.array([3]), [('A', [[1]]), ('B', [[2]])],
        'A', 'B', gain=1.0, ron=1.0)
    assert np.allclose(props['DIFF_STRAIGHT'], image - props['IMAGE_MODEL'],
                       rtol=1e-2, atol=1e-2)


def test_prepare_model_bckgrd_geo_uses_dxmap_no_shape(
        spirou_params) -> None:
    """Geometry prep should expose inverse maps and DXMAP_NO_SHAPE."""
    image_shape = (5, 6)
    ygrid, xgrid = np.indices(image_shape, dtype=float)
    sprops = ParamDict()
    sprops['SHAPEL'] = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    sprops['SHAPEX'] = np.zeros(image_shape)
    sprops['SHAPEY'] = np.zeros(image_shape)
    sprops['DXMAP_NO_SHAPE'] = xgrid
    sprops['SHAPELFILE'] = 'shape-local.fits'
    sprops['SHAPELTIME'] = 1.0
    sprops['DXMAP_NO_SHAPEFILE'] = 'shape-local.fits'
    sprops['DXMAP_NO_SHAPETIME'] = 1.0
    gprops = model_background.prepare_model_bckgrd_geo(
        spirou_params, image_shape, sprops)
    assert np.allclose(gprops['INV_XMAP'], xgrid)
    assert np.allclose(gprops['INV_YMAP'], ygrid)
    assert np.allclose(gprops['DXMAP_NO_SHAPE'], xgrid)


def test_extract_all_fibers_returns_model_products(spirou_params) -> None:
    """The APERO wrapper should expose pure all-fiber extraction outputs."""
    image = np.zeros((6, 10))
    profile1 = np.zeros_like(image)
    profile2 = np.zeros_like(image)
    profile1[2:4] = 1.0
    profile2[3:5] = 1.0
    image = 4.0 * profile1 + 7.0 * profile2
    eprops = model_background.extract_all_fibers(
        spirou_params, image, profile1, profile2, np.array([1]),
        np.array([5]), gain=1.0, ron=1.0)
    assert eprops['FLUX1'].shape == (1, 10)
    assert eprops['FLUX2'].shape == (1, 10)
    assert eprops['IMAGE_MODEL'].shape == image.shape


def test_spirou_fiber_specs_describe_reference_and_science_channels() -> None:
    """SPIROU descriptors should preserve reference and science ordering."""
    instrument = INSTRUMENTS['SPIROU']('SPIROU')
    specs = instrument.FIBER_SPECS()
    assert [spec.name for spec in specs] == ['C', 'AB', 'A', 'B']
    assert specs[0].role == 'reference'
    assert specs[1].localisation == ('A', 'B')


def test_run_all_fiber_model_uses_profiles_and_geometry(spirou_params) -> None:
    """The orchestration wrapper should produce fit and background products."""
    image = np.zeros((6, 10))
    profile1 = np.zeros_like(image)
    profile2 = np.zeros_like(image)
    profile1[2:4] = 1.0
    profile2[3:5] = 1.0
    image = 4.0 * profile1 + 7.0 * profile2
    geometry = ParamDict()
    geometry['INV_XMAP'] = np.tile(np.arange(10.0), (6, 1))
    geometry['INV_YMAP'] = np.tile(np.arange(6.0)[:, None], (1, 10))
    geometry['DXMAP_NO_SHAPE'] = np.zeros_like(image)
    geometry['SHAPEL'] = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    geometry['SHAPEX'] = np.zeros_like(image)
    geometry['SHAPEY'] = np.zeros_like(image)
    order_map = np.zeros((6, 10), dtype=int)
    order_map[1, :] = 1
    order_map[4, :] = 2
    order_nearest = np.array(order_map)
    order_profiles = dict(A=profile1, B=profile2)
    props = model_background.run_all_fiber_model(
        spirou_params, image, image, order_profiles, geometry, order_map,
        order_nearest, {'A': (1, 1), 'B': (2, 2)}, np.array([1]),
        np.array([5]), np.array([3]), [('A', [[1]]), ('B', [[2]])],
        'A', 'B', gain=1.0, ron=1.0)
    assert props['FIBER1'] == 'A'
    assert props['FIBER2'] == 'B'
    assert props['IMAGE_MODEL'].shape == image.shape
    assert props['SCI_BKGSUB'].shape == image.shape
    assert set(props['MODEL_SPECTRA']) == {'A', 'B', 'COMBINED'}
    assert set(props['BLAZE']) == {'A', 'B'}
    assert 'A' in props['SPECTRA']
    expected_grid = int(np.ceil(10 / spirou_params['CAL.EXT.SAVGOL_STEP']))
    assert props['SPECTRUM_GRID'].shape == (expected_grid,)


def test_spectra_to_eprops_adapts_new_spectrum_contract(spirou_params) -> None:
    """The new model spectrum should satisfy legacy extraction consumers."""
    model_props = ParamDict()
    model_props['SPECTRA'] = dict(A=(np.ones((2, 5)),
                                    np.full((2, 5), 0.5)))
    model_props['RON'] = 2.0
    eprops = model_background.spectra_to_eprops(
        spirou_params, model_props, 'A', nframes=1)
    for key in ('E2DS', 'E2DSFF', 'SNR', 'FLAT', 'BLAZE',
                'EFF_RON', 'E2DS_ERROR'):
        assert key in eprops
    assert eprops['E2DS'].shape == (2, 5)
    assert np.allclose(eprops['E2DSFF'], 1.0)
    assert np.allclose(eprops['E2DS_ERROR'], 0.5)


def test_qc_extraction_accepts_e2dsff_only(spirou_params) -> None:
    """Extraction QC should accept an E2DSFF-only property dictionary."""
    eprops = ParamDict()
    eprops['E2DSFF'] = np.ones((2, 4))
    qc_params, passed = gen_ext.qc_extraction(spirou_params, eprops)
    assert passed == 1
    assert qc_params[3] == [1]


def test_qc_extraction_accepts_spectra_contract(spirou_params) -> None:
    """Extraction QC should accept the new spectrum/error tuple directly."""
    spectra = (np.ones((2, 4)), np.ones((2, 4)))
    qc_params, passed = gen_ext.qc_extraction(spirou_params,
                                              spectra=spectra)
    assert passed == 1
    assert qc_params[3] == [1]


def test_create_order_table_accepts_e2dsff_only() -> None:
    """Order-table stats should be written for available image products."""
    lprops = ParamDict()
    lprops['YCENT'] = np.array([10.0, 20.0])
    lprops['CENT_COEFFS'] = np.zeros((2, 2))
    lprops['WID_COEFFS'] = np.ones((2, 1))
    wprops = ParamDict()
    wprops['NBO'] = 2
    wprops['EORDERS'] = np.array([50, 51])
    wprops['WAVEMAP'] = np.array([[1.0, 2.0], [3.0, 4.0]])
    eprops = ParamDict()
    eprops['SNR'] = np.array([10.0, 20.0])
    eprops['N_COSMIC'] = np.array([0, 1])
    eprops['FLUX_VAL'] = np.array([5.0, 6.0])
    eprops['E2DSFF'] = np.array([[1.0, 2.0], [3.0, 4.0]])
    eprops['BLAZE'] = np.ones((2, 2))
    table = gen_ext.create_order_table(lprops, wprops, eprops)
    assert 'E2DSFF_MEAN' in table.colnames
    assert 'E2DS_MEAN' not in table.colnames
    assert np.allclose(table['E2DSFF_MEAN'], [1.5, 3.5])