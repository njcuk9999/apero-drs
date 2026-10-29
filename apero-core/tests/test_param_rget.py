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
    for key, value, dtype in [('COUNT', 3, int), ('RATIO', 1.5, float),
                              ('TEXT', 'text', str), ('FLAG', True, bool),
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


@pytest.mark.parametrize('view', ['params', 'sub_params'])
@pytest.mark.parametrize('use_override', [False, True])
@pytest.mark.parametrize('key, value, expected, dtype', [
    ('COUNT', 40.0, 40, int),
    ('COUNT', 40.9, 40, int),
    ('COUNT', '40', 40, int),
    ('COUNT', True, 1, int),
    ('COUNT', False, 0, int),
    ('RATIO', 40, 40.0, float),
    ('RATIO', '1.5', 1.5, float),
    ('RATIO', True, 1.0, float),
    ('FLAG', 1, True, bool),
    ('FLAG', 0, False, bool),
    ('FLAG', 1.0, True, bool),
    ('FLAG', 0.0, False, bool),
    ('FLAG', 'TRUE', True, bool),
    ('FLAG', 'False', False, bool),
    ('FLAG', '1', True, bool),
    ('FLAG', '0', False, bool),
    ('TEXT', 40, '40', str),
    ('VALUES', (1, 2), [1, 2], list),
])
def test_rget_casts_without_mutation(request, view, use_override,
                                    key, value, expected, dtype):
    """Cast stored values and overrides through either view without writes."""
    params = request.getfixturevalue(view)
    if not use_override:
        params[key] = value
    stored = params[key]
    parent = getattr(params, 'param_dict', params)
    parent.lock()
    result = params.rget(key, override=value if use_override else None)
    assert result == expected
    assert type(result) is dtype
    assert params[key] is stored


@pytest.mark.parametrize('view', ['params', 'sub_params'])
@pytest.mark.parametrize('key, value', [
    ('COUNT', None),
    ('COUNT', 'wrong'),
    ('COUNT', float('inf')),
    ('COUNT', float('nan')),
    ('COUNT', []),
    ('RATIO', None),
    ('RATIO', 'wrong'),
    ('TEXT', None),
    ('FLAG', None),
    ('FLAG', 2),
    ('FLAG', 'wrong'),
    ('FLAG', ''),
    ('VALUES', None),
    ('VALUES', 1),
])
def test_rget_rejects_uncastable_values(request, view, key, value):
    """Keep coded errors for None and failed or invalid conversions."""
    params = request.getfixturevalue(view)
    params[key] = value
    with pytest.raises(param_functions.AperoCodedException) as caught:
        params.rget(key, func='extract')
    assert caught.value.code == '00-000-00015'
    assert caught.value.targs[1] is value
    assert '\nFunction: extract' in caught.value.message.get_text()


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
    assert f'Parameter COUNT=wrong does not have data-type {int}' in message
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


def test_sub_assignment_respects_parent_lock(sub_params):
    """View assignment updates the parent and cannot bypass its lock."""
    sub_params['COUNT'] = 8
    assert sub_params.param_dict['SECTION.COUNT'] == 8
    sub_params.param_dict.lock()
    with pytest.raises(param_functions.AperoCodedException) as caught:
        sub_params['COUNT'] = 9
    assert caught.value.code == '00-003-00025'
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
    assert 'Parameter SECTION.COUNT=' in message
    assert f'does not have data-type {int}' in message
    assert ('Function:' in message) == (func is not None)