#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for typed parameter retrieval and coded error formatting."""

import pytest

from aperocore.constants import constant_functions
from aperocore.constants import param_functions
from aperocore.drs_lang import drs_lang_text


@pytest.fixture
def params():
    """Return a parameter dictionary with typed and untyped values."""
    result = param_functions.ParamDict()
    for key, value, dtype in [('COUNT', 3, int), ('FLAG', True, bool),
                              ('VALUES', [1], list), ('UNTYPED', 'any', None)]:
        instance = constant_functions.Const(key, dtype=dtype, source=__file__)
        result.set(key, value, instance=instance)
    result['NO_INSTANCE'] = 'plain'
    return result


@pytest.mark.parametrize('key, expected', [('count', 3), ('FLAG', True),
                                          ('VALUES', [1]), ('UNTYPED', 'any'),
                                          ('NO_INSTANCE', 'plain')])
def test_rget_returns_value(params, key, expected):
    """Return correctly typed values and tolerate absent type metadata."""
    assert params.rget(key) == expected


@pytest.mark.parametrize('key, override', [('COUNT', 0), ('FLAG', False),
                                          ('VALUES', [])])
def test_rget_override_does_not_mutate(params, key, override):
    """Use non-None overrides, including falsey values, without mutation."""
    stored = params[key]
    params.lock()
    assert params.rget(key, override=override) == override
    assert params[key] == stored


def test_rget_none_override_uses_stored_value(params):
    """A None override means that the stored parameter is selected."""
    assert params.rget('COUNT', override=None) == 3


def test_rget_missing_optional(params):
    """An optional missing key returns None without creating a parameter."""
    assert params.rget('MISSING') is None
    assert 'MISSING' not in params


def test_rget_missing_required(params):
    """A required missing key raises the existing missing-parameter error."""
    with pytest.raises(param_functions.AperoCodedException) as caught:
        params.rget('MISSING', required=True)
    assert caught.value.code == '00-003-00024'


def test_rget_override_supplies_missing_required(params):
    """An override can supply a required value without a stored parameter."""
    assert params.rget('MISSING', override=4, required=True) == 4


@pytest.mark.parametrize('func', [None, 'extract'])
@pytest.mark.parametrize('use_override', [False, True])
def test_rget_type_error(params, func, use_override):
    """Validate stored values and overrides with optional function context."""
    if use_override:
        override = 'wrong'
    else:
        params.set('COUNT', 'wrong')
        override = None
    with pytest.raises(param_functions.AperoCodedException) as caught:
        params.rget('count', override=override, func=func)
    error = caught.value
    assert error.code == '00-000-00015'
    assert isinstance(error.message, drs_lang_text.Text)
    message = error.message.get_text()
    assert f'Parameter COUNT does not have data-type {int}' in message
    assert 'Please check the input yaml files.' in message
    if func is None:
        assert 'Function:' not in message
    else:
        assert '\nFunction: extract' in message


@pytest.fixture
def sub_params(params):
    """Return a prefix view with typed and untyped parent entries."""
    for key in params.keys():
        params.set(f'SECTION.{key}', params[key],
                   instance=params.instances.get(key))
    return params.get('SECTION')


def test_sub_rget_case_insensitive_and_tracks_use(sub_params):
    """Delegate reads through the parent's case handling and usage counter."""
    parent = sub_params.param_dict
    assert sub_params.rget('count') == 3
    assert 'SECTION.COUNT' in parent.used
    before = parent.used['SECTION.COUNT']
    assert sub_params.rget('COUNT') == 3
    assert parent.used['SECTION.COUNT'] == before + 1


def test_sub_rget_observes_parent_changes(sub_params):
    """The view reads live parent values rather than copied entries."""
    sub_params.param_dict.set('SECTION.COUNT', 8)
    assert sub_params.rget('COUNT') == 8


@pytest.mark.parametrize('key', ['UNTYPED', 'NO_INSTANCE'])
def test_sub_rget_without_dtype(sub_params, key):
    """Missing data-type metadata does not constrain the selected value."""
    assert sub_params.rget(key, override=[]) == []


@pytest.mark.parametrize('key, override', [('COUNT', 0), ('FLAG', False),
                                          ('VALUES', [])])
def test_sub_rget_override(sub_params, key, override):
    """Falsey overrides are selected without modifying the locked parent."""
    stored = sub_params[key]
    sub_params.param_dict.lock()
    assert sub_params.rget(key, override=override) == override
    assert sub_params[key] == stored


def test_sub_rget_missing(sub_params):
    """Forward optional and required missing-key behavior to the parent."""
    assert sub_params.rget('MISSING') is None
    assert sub_params.rget('MISSING', override=4, required=True) == 4
    with pytest.raises(param_functions.AperoCodedException) as caught:
        sub_params.rget('MISSING', required=True)
    assert caught.value.code == '00-003-00024'
    assert caught.value.targs == ['SECTION.MISSING']


@pytest.mark.parametrize('func', [None, 'extract'])
@pytest.mark.parametrize('use_override', [False, True])
def test_sub_rget_type_error(sub_params, func, use_override):
    """Type errors identify the full parent key and forward function context."""
    if use_override:
        override = 'wrong'
    else:
        sub_params.param_dict.set('SECTION.COUNT', None)
        override = None
    with pytest.raises(param_functions.AperoCodedException) as caught:
        sub_params.rget('count', override=override, func=func)
    assert caught.value.code == '00-000-00015'
    assert isinstance(caught.value.message, drs_lang_text.Text)
    message = caught.value.message.get_text()
    assert 'Parameter SECTION.COUNT does not have data-type' in message
    assert ('Function:' in message) == (func is not None)