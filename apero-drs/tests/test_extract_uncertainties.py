#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for fixed-correction E2DSFF uncertainty propagation."""

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest
from astropy.io import fits
from astropy.table import Table

from aperocore.constants import param_functions
from apero.core import drs_file
from apero.science.calib import leak
from apero.science.calib import thermal
from apero.science.extract import gen_ext


ParamDict = param_functions.ParamDict


@pytest.mark.parametrize('enabled', [False, True])
def test_leak_subtraction_preserves_noise(
        spirou_params: ParamDict, monkeypatch: pytest.MonkeyPatch,
        enabled: bool) -> None:
    """Fixed leak subtraction must not remove measurement noise.

    :param spirou_params: Profile-free APERO test parameters.
    :param monkeypatch: Fixture isolating calibration lookup.
    :param enabled: Whether the leak correction is applied.
    :return: None.
    """
    params = spirou_params.copy()
    params['INPUTS'] = dict(LEAKCORR=enabled, EXTRACT_TYPE='standard')
    params['CAL.EXT.QUICKLOOK'] = False
    params['CAL.LEAK.REF_TYPES'] = ['FP']
    pconst = MagicMock()
    pconst.FIBER_KINDS.return_value = (['AB'], 'C')
    pconst.FIBER_DATA_TYPE.return_value = 'FP'
    monkeypatch.setattr(leak.load_functions, 'load_pconfig',
                        lambda *args: pconst)
    spectrum = np.array([[10.0, 1.0, np.nan, 5.0]])
    error = np.array([[2.0, 3.0, 4.0, 5.0]])
    corrected = np.array([[7.0, -2.0, np.nan, np.inf]])
    correction = MagicMock(return_value=(corrected, np.zeros(1), ParamDict()))
    monkeypatch.setattr(leak, 'correct_ext_dark_fp', correction)
    infile = MagicMock()

    leak_args = [params, MagicMock(), spectrum, np.ones_like(spectrum),
                 infile, 'AB', error]
    flux, noise, diagnostics, props = leak.correct_spectra_leak(*leak_args)

    expected_flux = corrected if enabled else spectrum
    expected_noise = [[2.0, 3.0, np.nan, np.nan if enabled else 5.0]]
    np.testing.assert_allclose(flux, expected_flux)
    np.testing.assert_allclose(noise, expected_noise)
    np.testing.assert_array_equal(error, [[2.0, 3.0, 4.0, 5.0]])
    assert props['LEAK_CORRECTED'] == enabled
    assert correction.call_count == int(enabled)


@pytest.mark.parametrize('mode', ['tapas', 'envelope', 'other', 'quicklook',
                                 'flat', 'disabled'])
def test_thermal_subtraction_preserves_noise(
        spirou_params: ParamDict, monkeypatch: pytest.MonkeyPatch,
        mode: str) -> None:
    """Carry uncertainties through either fixed thermal model and skips.

    :param spirou_params: Profile-free APERO test parameters.
    :param monkeypatch: Fixture isolating wave and thermal calibration.
    :param mode: Thermal method or reason to skip correction.
    :return: None.
    """
    params = spirou_params.copy()
    params['INPUTS'] = dict(EXTRACT_TYPE='flat' if mode == 'flat'
                           else 'standard')
    params['CAL.EXT.QUICKLOOK'] = mode == 'quicklook'
    params['CAL.THERM.THERMAL_CORR'] = mode != 'disabled'
    params['CAL.THERM.CORR_TYPE1'] = ['tapas']
    params['CAL.THERM.CORR_TYPE2'] = ['envelope']
    pconst = MagicMock()
    pconst.FIBER_DATA_TYPE.return_value = mode
    monkeypatch.setattr(thermal.load_functions, 'load_pconfig',
                        lambda *args: pconst)
    monkeypatch.setattr(thermal, 'WLOG', MagicMock())
    wavemap = np.ones((1, 4))
    monkeypatch.setattr(thermal.wave, 'get_wavesolution',
                        lambda *args, **kwargs: dict(WAVEMAP=wavemap))
    monkeypatch.setattr(thermal, 'get_thermal',
                        lambda *args, **kwargs: ('thermal.fits', 0.0, wavemap))
    corrected = np.array([[7.0, -2.0, np.nan, np.inf]])
    ratios = dict(ratio=2.0, ratio_used=mode)
    correction = MagicMock(return_value=(corrected, ratios))
    monkeypatch.setattr(thermal, 'tcorrect1', correction)
    monkeypatch.setattr(thermal, 'tcorrect2', correction)
    spectrum = np.array([[10.0, 1.0, np.nan, 5.0]])
    error = np.array([[2.0, 3.0, 4.0, 5.0]])
    thermal_args = [params, MagicMock(), MagicMock(), dict(DPRTYPE='OBJ'),
                    spectrum, 'AB', error]

    flux, noise, props = thermal.correct_spectrum_thermal(*thermal_args)

    enabled = mode in ('tapas', 'envelope')
    np.testing.assert_allclose(flux, corrected if enabled else spectrum)
    expected_noise = [[2.0, 3.0, np.nan, np.nan if enabled else 5.0]]
    np.testing.assert_allclose(noise, expected_noise)
    np.testing.assert_array_equal(error, [[2.0, 3.0, 4.0, 5.0]])
    assert correction.call_count == int(enabled)


@pytest.mark.parametrize('quicklook', [False, True])
@pytest.mark.parametrize('snapshot', [False, True])
def test_extraction_writes_error_extension(
        spirou_params: ParamDict, monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path, quicklook: bool, snapshot: bool) -> None:
    """Write real FITS products with flux, error, and optional tables.

    :param spirou_params: Profile-free APERO test parameters.
    :param monkeypatch: Fixture replacing unrelated metadata operations.
    :param tmp_path: Temporary directory for the output FITS product.
    :param quicklook: Whether to exercise the quick-look writer.
    :param snapshot: Whether to include a parameter snapshot table.
    :return: None.
    """
    params = spirou_params.copy()
    params['GLOBAL.PSNAPSHOT'] = snapshot
    monkeypatch.setattr(ParamDict, 'snapshot_table',
                        lambda *args, **kwargs: Table(dict(PARAM=['test'])))
    output = MagicMock()
    output.params = params
    output.filename = str(tmp_path / 'e2dsff.fits')
    output.name = 'QL_E2DS_FF' if quicklook else 'EXT_E2DS_FF'
    output.header = fits.Header()
    output.datatype = 'image'
    output.dtype = 'float64'
    output.no_save.return_value = False
    output.newcopy.return_value = output
    output.write_multi.side_effect = (
        lambda **kwargs: drs_file.DrsFitsFile.write_multi(output, **kwargs))
    recipe = MagicMock()
    recipe.outputs = dict(E2DSFF_FILE=output, Q2DSFF_FILE=output)
    monkeypatch.setattr(gen_ext, 'WLOG', MagicMock())
    monkeypatch.setattr(gen_ext.gen_calib, 'add_calibs_to_header',
                        lambda file, props: file)
    monkeypatch.setattr(gen_ext.wave, 'add_wave_keys',
                        lambda file, props: file)
    monkeypatch.setattr(gen_ext.berv, 'add_berv_keys',
                        lambda params, file, props: file)
    order_table = Table(dict(order_num=[0]))
    monkeypatch.setattr(gen_ext, 'create_order_table',
                        lambda *args: order_table)
    keys = ['EFF_RON', 'START_ORDER', 'END_ORDER', 'CAL.EXT.RANGE1',
            'CAL.EXT.RANGE2', 'COSMIC', 'COSMIC_SIGCUT', 'COSMIC_THRESHOLD',
            'SAT_LEVEL', 'LEAK_CORRECTED', 'LEAKREF_FILE', 'LEAKREF_TIME',
            'LEAKREF_REFFILE', 'LEAKREF_REFTIME', 'LEAK_BCKGRD_PERCENTILE_USED',
            'LEAK_NORM_PERCENTILE_USED', 'LEAK_LOW_PERCENTILE_USED',
            'LEAK_HIGH_PERCENTILE_USED', 'LEAK_BAD_RATIO_OFFSET_USED',
            'THERMAL_RATIO', 'THERMAL_RATIO_USED']
    eprops = dict.fromkeys(keys, 0)
    eprops['E2DSFF'] = np.array([[7.0, -2.0, np.nan]])
    eprops['E2DSFF_ERROR'] = np.array([[2.0, 3.0, np.nan]])
    eprops['SNR'] = np.array([4.0])
    eprops['FLUX_VAL'] = np.array([10.0])
    eprops['MP2P_E2DSFF'] = dict(MP2P=[1.0], BP2P=dict(H=1.0))
    loc_keys = ['ORDERPFILE', 'ORDERPTIME', 'LOCOFILE', 'LOCOTIME']
    lprops = dict.fromkeys(loc_keys, 'test')
    lprops['LOCOOBJECT'] = MagicMock()
    shape_keys = ['SHAPELFILE', 'SHAPELTIME', 'SHAPEXFILE', 'SHAPEXTIME',
                  'SHAPEYFILE', 'SHAPEYTIME']
    sprops = dict.fromkeys(shape_keys, 'test')
    sprops['SHAPEL'] = np.zeros(6)
    fbprops = dict(BLAZEFILE='test', BLAZETIME=0.0)
    common_args = [params, recipe, MagicMock(), ['raw.fits'], False, 'AB',
                   ParamDict(), lprops]

    if quicklook:
        writer_args = common_args + [eprops, sprops, fbprops, []]
        gen_ext.write_extraction_files_ql(*writer_args)
    else:
        wprops = dict(WAVEFILE='test', WAVETIME=0.0)
        writer_args = common_args + [wprops, eprops, ParamDict(), None,
                                    None, sprops, fbprops, []]
        gen_ext.write_extraction_files(*writer_args)

    with fits.open(output.filename) as hdus:
        expected_names = ['PRIMARY', output.name, 'E2DSFF_ERROR']
        if not quicklook:
            expected_names += ['ORDER_TABLE']
        if snapshot:
            expected_names += ['PARAM_TABLE']
        assert [hdu.name for hdu in hdus] == expected_names
        assert hdus[0].data is None
        np.testing.assert_allclose(hdus[output.name].data, eprops['E2DSFF'])
        np.testing.assert_allclose(hdus['E2DSFF_ERROR'].data,
                                   eprops['E2DSFF_ERROR'])
