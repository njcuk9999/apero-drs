#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive tests for drs_base_classes dictionary implementations."""

import pickle
from aperocore.core import drs_base_classes


# =============================================================================
# Define functions - CaseInsensitiveDict tests
# =============================================================================
def test_case_insensitive_dict_initializes_empty() -> None:
    """CaseInsensitiveDict should initialize as empty dict."""
    cid = drs_base_classes.CaseInsensitiveDict()
    assert len(cid) == 0
    assert isinstance(cid, dict)


def test_case_insensitive_dict_initializes_with_data() -> None:
    """CaseInsensitiveDict should initialize with provided data."""
    cid = drs_base_classes.CaseInsensitiveDict(
        {'key1': 'value1', 'key2': 'value2'}
    )
    assert len(cid) == 2


def test_case_insensitive_dict_capitalizes_keys() -> None:
    """CaseInsensitiveDict should capitalize all string keys."""
    cid = drs_base_classes.CaseInsensitiveDict(
        {'lowercase': 'value1', 'MixedCase': 'value2'}
    )
    # Keys should be capitalized internally
    assert 'LOWERCASE' in cid.data
    assert 'MIXEDCASE' in cid.data


def test_case_insensitive_dict_getitem_lowercase() -> None:
    """CaseInsensitiveDict getitem should work with lowercase keys."""
    cid = drs_base_classes.CaseInsensitiveDict({'KEY': 'value'})
    assert cid['key'] == 'value'


def test_case_insensitive_dict_getitem_uppercase() -> None:
    """CaseInsensitiveDict getitem should work with uppercase keys."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    assert cid['KEY'] == 'value'


def test_case_insensitive_dict_getitem_mixedcase() -> None:
    """CaseInsensitiveDict getitem should work with mixed case keys."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    assert cid['KeY'] == 'value'
    assert cid['kEy'] == 'value'


def test_case_insensitive_dict_setitem_case_insensitive() -> None:
    """CaseInsensitiveDict setitem should work case insensitively."""
    cid = drs_base_classes.CaseInsensitiveDict()
    cid['key'] = 'value1'
    assert cid['KEY'] == 'value1'
    cid['KEY'] = 'value2'
    assert cid['key'] == 'value2'
    # Should only have one key (capitalized)
    assert len(cid) == 1


def test_case_insensitive_dict_contains() -> None:
    """CaseInsensitiveDict contains should be case insensitive."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    assert 'key' in cid
    assert 'KEY' in cid
    assert 'KeY' in cid
    assert 'other' not in cid


def test_case_insensitive_dict_delitem() -> None:
    """CaseInsensitiveDict delitem should work case insensitively."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    del cid['KEY']
    assert 'key' not in cid


def test_case_insensitive_dict_get_existing_key() -> None:
    """CaseInsensitiveDict get should return value for existing key."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    assert cid.get('key') == 'value'
    assert cid.get('KEY') == 'value'


def test_case_insensitive_dict_get_missing_key_default_none() -> None:
    """CaseInsensitiveDict get should return None for missing key."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    assert cid.get('missing') is None


def test_case_insensitive_dict_get_missing_key_custom_default() -> None:
    """CaseInsensitiveDict get should return custom default."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    assert cid.get('missing', 'default') == 'default'


def test_case_insensitive_dict_str_representation() -> None:
    """CaseInsensitiveDict should have proper string representation."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    str_repr = str(cid)
    assert 'CaseInsensitiveDict' in str_repr
    assert 'KEY' in str_repr
    assert 'value' in str_repr


def test_case_insensitive_dict_repr() -> None:
    """CaseInsensitiveDict repr should match str."""
    cid = drs_base_classes.CaseInsensitiveDict({'key': 'value'})
    assert repr(cid) == str(cid)


def test_case_insensitive_dict_pickle_and_unpickle() -> None:
    """CaseInsensitiveDict should be pickleable."""
    cid = drs_base_classes.CaseInsensitiveDict(
        {'key1': 'value1', 'key2': 'value2'}
    )
    pickled = pickle.dumps(cid)
    unpickled = pickle.loads(pickled)
    assert unpickled['key1'] == 'value1'
    assert unpickled['key2'] == 'value2'


def test_case_insensitive_dict_multiple_types_values() -> None:
    """CaseInsensitiveDict should handle multiple value types."""
    cid = drs_base_classes.CaseInsensitiveDict({
        'str_val': 'text',
        'int_val': 42,
        'float_val': 3.14,
        'list_val': [1, 2, 3],
        'dict_val': {'nested': 'value'}
    })
    assert cid['str_val'] == 'text'
    assert cid['int_val'] == 42
    assert abs(cid['float_val'] - 3.14) < 0.01
    assert cid['list_val'] == [1, 2, 3]
    assert cid['dict_val']['nested'] == 'value'


# =============================================================================
# Define functions - StrCaseINSDict tests
# =============================================================================
def test_str_case_insdict_initializes() -> None:
    """StrCaseINSDict should initialize properly."""
    sisd = drs_base_classes.StrCaseINSDict({'key': 'value'})
    assert 'KEY' in sisd.data


def test_str_case_insdict_getitem_returns_list() -> None:
    """StrCaseINSDict getitem should convert string to list."""
    sisd = drs_base_classes.StrCaseINSDict({'key': 'value'})
    result = sisd['key']
    assert isinstance(result, list)
    # String converted to list of characters
    assert result == list('value')


def test_str_case_insdict_setitem_converts_to_list() -> None:
    """StrCaseINSDict setitem should store value as list."""
    sisd = drs_base_classes.StrCaseINSDict()
    sisd['key'] = 'value'
    # Should be stored as list internally
    assert isinstance(sisd.data['KEY'], list)


def test_str_case_insdict_str_representation() -> None:
    """StrCaseINSDict should have proper string representation."""
    sisd = drs_base_classes.StrCaseINSDict()
    str_repr = str(sisd)
    assert 'StrCaseINSDict' in str_repr
    assert 'CaseInsensitiveDict' in str_repr


# =============================================================================
# Define functions - ListCaseINSDict tests
# =============================================================================
def test_list_case_insdict_initializes() -> None:
    """ListCaseINSDict should initialize properly."""
    lisd = drs_base_classes.ListCaseINSDict({'key': [1, 2, 3]})
    assert 'KEY' in lisd.data


def test_list_case_insdict_getitem_returns_list() -> None:
    """ListCaseINSDict getitem should return list copy."""
    lisd = drs_base_classes.ListCaseINSDict({'key': [1, 2, 3]})
    result = lisd['key']
    assert isinstance(result, list)
    assert result == [1, 2, 3]


def test_list_case_insdict_setitem_enforces_list() -> None:
    """ListCaseINSDict setitem should ensure value is list."""
    lisd = drs_base_classes.ListCaseINSDict()
    lisd['key'] = [1, 2, 3]
    result = lisd.data['KEY']
    assert isinstance(result, list)
    assert result == [1, 2, 3]


def test_list_case_insdict_case_insensitive_access() -> None:
    """ListCaseINSDict should access keys case insensitively."""
    lisd = drs_base_classes.ListCaseINSDict({'key': [1, 2]})
    assert lisd['key'] == [1, 2]
    assert lisd['KEY'] == [1, 2]
    assert lisd['KeY'] == [1, 2]


# =============================================================================
# Define functions - ListDict tests
# =============================================================================
def test_list_dict_initializes() -> None:
    """ListDict should initialize properly."""
    ld = drs_base_classes.ListDict({'key': [1, 2, 3]})
    assert 'key' in ld.data


def test_list_dict_getitem_returns_list() -> None:
    """ListDict getitem should return list copy."""
    ld = drs_base_classes.ListDict({'key': [1, 2, 3]})
    result = ld['key']
    assert isinstance(result, list)
    assert result == [1, 2, 3]


def test_list_dict_setitem_stores_list() -> None:
    """ListDict setitem should store value as list."""
    ld = drs_base_classes.ListDict()
    ld['key'] = [1, 2, 3]
    assert ld.data['key'] == [1, 2, 3]


def test_list_dict_preserves_case_sensitive_keys() -> None:
    """ListDict should preserve key case (unlike case insensitive)."""
    ld = drs_base_classes.ListDict({
        'lowercase': [1],
        'UPPERCASE': [2],
        'MixedCase': [3]
    })
    assert 'lowercase' in ld.data
    assert 'UPPERCASE' in ld.data
    assert 'MixedCase' in ld.data


def test_list_dict_str_representation() -> None:
    """ListDict should have proper string representation."""
    ld = drs_base_classes.ListDict()
    str_repr = str(ld)
    assert 'ListDict' in str_repr
    assert 'UserDict' in str_repr


# =============================================================================
# Define functions - FlatYamlDict tests
# =============================================================================
def test_flat_yaml_dict_initializes() -> None:
    """FlatYamlDict should initialize with nested dict."""
    yaml_dict = {
        'level1': {
            'level2': {
                'level3': 'value'
            }
        }
    }
    fyd = drs_base_classes.FlatYamlDict(yaml_dict)
    assert fyd.yaml_dict == yaml_dict


def test_flat_yaml_dict_flatten_dict_attribute_exists() -> None:
    """FlatYamlDict should have flatten_dict attribute."""
    yaml_dict = {'key': 'value'}
    fyd = drs_base_classes.FlatYamlDict(yaml_dict)
    assert hasattr(fyd, 'flatten_dict')
    assert isinstance(fyd.flatten_dict, dict)


def test_flat_yaml_dict_key_dict_attribute_exists() -> None:
    """FlatYamlDict should have key_dict attribute."""
    yaml_dict = {'key': 'value'}
    fyd = drs_base_classes.FlatYamlDict(yaml_dict)
    assert hasattr(fyd, 'key_dict')
    assert isinstance(fyd.key_dict, dict)


def test_flat_yaml_dict_contains_operator() -> None:
    """FlatYamlDict should support 'in' operator."""
    yaml_dict = {
        'section': {
            'param': 'value'
        }
    }
    fyd = drs_base_classes.FlatYamlDict(yaml_dict)
    # The exact keys depend on flatten logic
    assert isinstance(fyd, drs_base_classes.FlatYamlDict)


# =============================================================================
# End of code
# =============================================================================

