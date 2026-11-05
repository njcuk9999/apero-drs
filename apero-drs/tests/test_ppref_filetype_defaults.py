#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check PPREF default types through option management and recipe dispatch."""

import importlib
from unittest import mock

import pytest

from apero.dev import get_base_params
from aperocore.constants import param_functions
from apero.utils import drs_recipe


@pytest.mark.parametrize('instrument', ['SPIROU', 'NIRPS_HA', 'NIRPS_HE'])
def test_ppref_default_is_list(instrument: str) -> None:
    """Resolve the PPREF default without converting it into characters.

    :param instrument: Instrument whose default constants are loaded.
    :return: None.
    """
    params = get_base_params(instrument)
    assert params['PP.REF_FILETYPE'] == ['FLAT_FLAT']
    recipe_kwargs = dict(instrument=instrument, name='ppref_test',
                         params=params, filemod=mock.Mock())
    recipe = drs_recipe.DrsRecipe(**recipe_kwargs)
    option_kwargs = dict(name='--filetype', dtype='List[str]',
                         default_ref='PP.REF_FILETYPE')
    recipe.set_kwarg(**option_kwargs)
    recipe.input_params = param_functions.ParamDict()
    recipe.input_params['FILETYPE'] = None
    recipe.option_manager()
    assert recipe.params['INPUTS']['FILETYPE'] == ['FLAT_FLAT']


@pytest.mark.parametrize('instrument', ['NIRPS_HA', 'NIRPS_HE'])
def test_ppref_default_reaches_raw_file_lookup(
    monkeypatch: pytest.MonkeyPatch, instrument: str,
) -> None:
    """Pass the complete default file type to the raw-file lookup boundary.

    :param monkeypatch: Fixture replacing raw-file lookup before database use.
    :param instrument: NIRPS mode whose PPREF recipe is exercised.
    :return: None.
    """
    params = get_base_params(instrument)
    params['INPUTS'] = dict(FILETYPE=params['PP.REF_FILETYPE'])
    module_name = ('apero.recipes.{0}.apero_pp_ref_{0}'
                   .format(instrument.lower()))
    module = importlib.import_module(module_name)
    boundary = mock.Mock(side_effect=RuntimeError('raw lookup boundary'))
    monkeypatch.setattr(module.drs_file, 'get_file_definition', boundary)
    recipe = mock.Mock()
    with pytest.raises(RuntimeError, match='raw lookup boundary'):
        module.__main__(recipe, params)
    boundary.assert_called_once_with(params, 'RAW_FLAT_FLAT',
                                     block_kind='raw', required=False)


@pytest.mark.parametrize('instrument', ['NIRPS_HA', 'NIRPS_HE'])
def test_ppref_led_flat_reference_dates(
    monkeypatch: pytest.MonkeyPatch, instrument: str,
) -> None:
    """Reach LED creation using the current reference-date parameter names.

    :param monkeypatch: Fixture replacing science, database, and file I/O.
    :param instrument: NIRPS mode whose full PPREF orchestration is exercised.
    :return: None.
    """
    params = get_base_params(instrument)
    params['INPUTS'] = dict(FILETYPE=params['PP.REF_FILETYPE'])
    params['OBS_DIR'] = 'test-night'
    params['GLOBAL.PSNAPSHOT'] = False
    module_name = ('apero.recipes.{0}.apero_pp_ref_{0}'
                   .format(instrument.lower()))
    module = importlib.import_module(module_name)
    infile = mock.Mock()
    infile.name = 'FLAT_FLAT'
    infile.basename = 'test.fits'
    recipe = mock.Mock()
    outfile = mock.Mock()
    outfile.filename = 'test_mask.fits'
    recipe.outputs = dict(PP_REF=mock.Mock())
    recipe.outputs['PP_REF'].newcopy.return_value = outfile
    rawfile = mock.Mock()
    rawfile.newcopy.return_value = infile
    monkeypatch.setattr(module.drs_file, 'get_file_definition',
                        mock.Mock(return_value=rawfile))
    monkeypatch.setattr(module.drs_utils, 'find_files',
                        mock.Mock(return_value=['test.fits']))
    monkeypatch.setattr(module.drs_file, 'fix_header',
                        mock.Mock(return_value=infile))
    monkeypatch.setattr(module.drs_file, 'combine',
                        mock.Mock(return_value=(infile,)))
    database = mock.Mock()
    monkeypatch.setattr(module.drs_database, 'CalibrationDatabase',
                        mock.Mock(return_value=database))
    monkeypatch.setattr(module, 'WLOG', mock.Mock())
    monkeypatch.setattr(module.drs_startup, 'file_processing_update',
                        mock.Mock())
    mask_result = ([[1]], dict())
    mask_result[1]['PP.PPM_MASK_NSIG'] = 3
    monkeypatch.setattr(module.preprocessing, 'nirps_order_mask',
                        mock.Mock(return_value=mask_result))
    led_file = mock.Mock()
    create_led = mock.Mock(return_value=led_file)
    monkeypatch.setattr(module.preprocessing, 'create_led_flat', create_led)
    module.__main__(recipe, params)
    led_args = [params, recipe, module.file_definitions.raw_led_led,
                module.file_definitions.raw_dark_dark,
                params['REF.FIND_STARTDATE'], params['REF.FIND_ENDDATE'],
                params['REF.FIND_TIMECOL']]
    create_led.assert_called_once_with(*led_args)
    database.add_calib_file.assert_any_call(led_file)