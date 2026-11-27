"""Tests for the interactive demo filter menu in load_functions."""
import builtins

from aperocore.constants import load_functions


class FakeDemo:
    """Minimal demo: only get_info is used by the filter."""

    def __init__(self, obj, keywords):
        self.info = dict(title=obj, object=obj, keywords=keywords)

    def get_info(self):
        return dict(self.info)


def _demos():
    return dict(a=FakeDemo('WASP 39b', ['transit']),
                b=FakeDemo('HAT-P-11b', ['transit']),
                c=FakeDemo('LHS-1140', ['eclipse']))


def _run(monkeypatch, answers):
    answers = iter(answers)
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(answers))
    return load_functions._filter_demo_choices(None, _demos())


def test_choices_are_numbered_with_counts():
    choices = load_functions._collect_filter_choices(_demos())
    assert choices == [('object', 'HAT-P-11b', 1), ('object', 'LHS-1140', 1),
                       ('object', 'WASP 39b', 1),
                       ('keywords', 'eclipse', 1),
                       ('keywords', 'transit', 2)]


def test_enter_keeps_all(monkeypatch):
    assert sorted(_run(monkeypatch, [''])) == ['a', 'b', 'c']


def test_numbers_same_field_are_alternatives(monkeypatch):
    # 1 = HAT-P-11b, 3 = WASP 39b
    assert sorted(_run(monkeypatch, ['1 3'])) == ['a', 'b']


def test_numbers_different_fields_must_all_match(monkeypatch):
    # 2 = LHS-1140, 5 = transit -> nothing, then 5 alone
    assert sorted(_run(monkeypatch, ['2 5', '5'])) == ['a', 'b']


def test_words_search_all_fields(monkeypatch):
    assert sorted(_run(monkeypatch, ['wasp transit'])) == ['a']


def test_single_value_fields_skip_menu(monkeypatch):
    demos = dict(a=FakeDemo('WASP 39b', ['transit']))
    monkeypatch.setattr(builtins, 'input', lambda prompt='': 1 / 0)
    assert load_functions._filter_demo_choices(None, demos) == demos
