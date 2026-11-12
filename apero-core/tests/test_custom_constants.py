"""Tests for registering custom constants."""

import pytest

from aperocore.constants.constant_functions import Const, ConstantsDict


class CustomConst(Const):
    def validate(self, test_value=None, quiet=False, source=None):
        return 'custom validation'


@pytest.mark.parametrize('group', [None, 'GENERAL', 'WLC.INPUTS'])
def test_addc_matches_add_and_preserves_custom_class(group):
    standard = ConstantsDict('test')
    custom = ConstantsDict('test')
    kwargs = dict(value=0.5, dtype=float, minimum=0, maximum=1,
                  source='test', user=True, active=True, group=group,
                  description='A threshold', tex_arg=True)
    standard.add('THRESHOLD', **kwargs)
    assert custom.addc('THRESHOLD', const_class=CustomConst, **kwargs) is None

    key = 'THRESHOLD' if group is None else f'{group}.THRESHOLD'
    assert list(custom.storage) == list(standard.storage) == [key]
    assert isinstance(custom.get(key), CustomConst)
    assert vars(custom.get(key)) == vars(standard.get(key))
    assert custom.get(key).validate() == 'custom validation'


def test_addc_accepts_positional_arguments_and_failed_construction():
    constants = ConstantsDict('test')
    constants.addc('VALUE', 2, int, source='test', const_class=CustomConst)
    assert constants['VALUE'] == 2
    with pytest.raises(TypeError):
        constants.addc('VALUE', source='test', unknown=True,
                       const_class=CustomConst)
    assert constants['VALUE'] == 2
    copied = constants.copy(source='test')
    copied.addc('ANOTHER', 3, int, source='test', const_class=CustomConst)
    assert isinstance(copied.get('ANOTHER'), CustomConst)
