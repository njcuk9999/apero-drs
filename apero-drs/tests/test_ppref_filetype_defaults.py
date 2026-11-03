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