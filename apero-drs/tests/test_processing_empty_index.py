#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for processing warnings when index filters match no rows."""

from types import SimpleNamespace
from unittest import mock

import pytest

from apero.dev import get_base_params
from apero.tools.module.processing import drs_processing


@pytest.mark.parametrize('continue_run', [True, False])
def test_empty_index_warning(
    monkeypatch: pytest.MonkeyPatch, continue_run: bool,
) -> None:
    """Check the empty-index warning uses the current logging API.

    :param monkeypatch: Fixture replacing database and interactive boundaries.
    :param continue_run: Whether the user continues after the warning.
    :return: None.
    """
    params = get_base_params('NIRPS_HE')
    params['INPUTS'] = dict(VERIFY=False)
    params.pop('TRIGGER_RUN', None)
    indexdb = mock.Mock()
    indexdb.database.count.return_value = 0
    indexdb.get_entries.return_value = []
    definition = SimpleNamespace(process_adds=mock.Mock(), sequence=[])
    sequence = ['TEST', definition]
    condition = 'OBS_DIR="missing-night"'
    logger = mock.create_autospec(drs_processing.WLOG.__call__)
    prompt = mock.Mock(return_value=continue_run)
    monkeypatch.setattr(drs_processing, 'WLOG', logger)
    monkeypatch.setattr(drs_processing, 'prompt', prompt)
    pconfig = mock.Mock(return_value=mock.Mock())
    monkeypatch.setattr(drs_processing.load_functions, 'load_pconfig', pconfig)
    run_kwargs = dict(tstars=[], ostars=[], ref_condition=condition)
    if continue_run:
        result = drs_processing.gen_run_from_seq(
            params, sequence, indexdb, **run_kwargs)
        assert result == ([], dict(counts=dict(), used=dict()))
        indexdb.get_entries.assert_called_once_with(
            columns='*', condition=condition)
    else:
        with pytest.raises(SystemExit):
            drs_processing.gen_run_from_seq(
                params, sequence, indexdb, **run_kwargs)
        indexdb.get_entries.assert_not_called()
    indexdb.database.count.assert_called_once_with(condition=condition)
    prompt.assert_called_once_with(params)
    warning_call = logger.call_args_list[0]
    assert warning_call.args[1] == 'warning'
    message = str(warning_call.args[2])
    assert 'No rows in database' in message
    assert condition in message
    assert 'gen_run_from_seq()' in message
    assert warning_call.kwargs == dict(sublevel=8)