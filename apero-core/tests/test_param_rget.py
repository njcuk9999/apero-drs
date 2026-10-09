#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for typed parameter retrieval and coded error formatting."""

import pytest

from aperocore.constants import constant_functions
from aperocore.constants import param_functions


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
    message = error.message.get_text()
    assert f'Parameter COUNT does not have data-type {int}' in message
    assert 'Please check the input yaml files.' in message
    if func is None:
        assert 'Function:' not in message
    else:
        assert '\nFunction: extract' in message