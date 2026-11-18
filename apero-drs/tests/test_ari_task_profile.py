#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for the APERO-side ARITASK profile selection."""

from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from apero.instruments.default.recipe_definitions import ari_task
from apero.tools.recipes.bin import apero_ri_task


@pytest.fixture
def runner(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Record dispatch without running any RI task or opening a database.

    :param monkeypatch: Test patch fixture.
    :return: Recording substitute for the local task runner.
    """
    tasks = pytest.importorskip('apero_ri.tasks')
    sync = pytest.importorskip('apero_ri.tasks.apero_sync')
    task_types = {'OBJECT': 'PROFILE', 'GLOBAL': 'GLOBAL'}
    monkeypatch.setattr(tasks, 'TYPE', task_types)
    monkeypatch.setattr(sync, 'local_task_keys', lambda: ['OBJECT', 'GLOBAL'])
    run = Mock(return_value=dict(status='completed'))
    monkeypatch.setattr(sync, 'run', run)
    return run


def test_default_profile_uses_current_apero_settings(
    spirou_params: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    runner: Mock,
) -> None:
    """Dispatch current profile values without creating a YAML file.

    :param spirou_params: APERO developer profile parameters.
    :param tmp_path: Isolated task data root.
    :param monkeypatch: Test patch fixture.
    :param runner: Recording local task runner.
    :return: None.
    """
    object_query = pytest.importorskip('apero_ri.tasks.apero_object_query')
    params = dict(spirou_params, INPUTS={})
    params['PATH.OTHER'] = str(tmp_path)
    monkeypatch.setenv(params['DRS.USERENV'], str(tmp_path / 'mini'))
    settings = dict(TYPE='mysql+pymysql', HOST='localhost', USER='test',
                    PASSWD='', DATABASE='mini', PORT=3307)
    for kind in ('CALIB', 'FINDEX', 'LOG', 'TELLU'):
        settings[kind] = dict(NAME='legacy_db', TABLE=f'{kind}_TABLE')
    settings['FINDEX']['NAME'] = 'findex'
    monkeypatch.setattr(apero_ri_task.base, 'DPARAMS', settings)

    apero_ri_task.__main__(None, params)
    task, payload = runner.call_args.args
    assert task == 'OBJECT'
    profile = payload['APERO_PROFILES']['mini']
    assert profile['paths']['PATH_OTHER'] == str(tmp_path)
    assert profile['database']['DATABASE_PORT'] == 3307
    assert profile['database']['CALIB_TABLENAME'] == 'legacy_db'
    assert object_query._check_required(profile)['FINDEX_TABLENAME'] == (
        'FINDEX_TABLE'
    )

    params['PATH.RAW'] = str(tmp_path / 'new_raw')
    settings['HOST'] = 'other-host'
    apero_ri_task.__main__(None, params)
    revised = runner.call_args.args[1]['APERO_PROFILES']['mini']
    assert revised['paths']['PATH_RAW'] == params['PATH.RAW']
    assert revised['database']['DATABASE_HOST'] == 'other-host'
    assert list(tmp_path.iterdir()) == []
    assert runner.call_count == 2


def test_explicit_yaml_bypasses_default_profile(
    spirou_params: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    runner: Mock,
) -> None:
    """Use the supplied file as-is and preserve its profile name.

    :param spirou_params: APERO developer profile parameters.
    :param tmp_path: Temporary directory holding the user override.
    :param monkeypatch: Test patch fixture.
    :param runner: Recording local task runner.
    :return: None.
    """
    profile_path = tmp_path / 'custom.yaml'
    contents = 'general:\n  SCIENCE_FIBER: CUSTOM\n'
    profile_path.write_text(contents, encoding='utf-8')
    recipe = deepcopy(ari_task)
    cli_args = [recipe.name, f'--profile={profile_path}']
    inputs = recipe.recipe_setup(None, inargs=cli_args)
    params = spirou_params.copy()
    params['INPUTS'] = apero_ri_task.ParamDict()
    for key, value in inputs.items():
        params['INPUTS'][key] = value
    builder = Mock(side_effect=AssertionError('Default must not be built'))
    monkeypatch.setattr(apero_ri_task, '_build_profile', builder)

    apero_ri_task.__main__(None, params)

    profile = runner.call_args.args[1]['APERO_PROFILES']['custom']
    assert profile['general']['SCIENCE_FIBER'] == 'CUSTOM'
    assert profile_path.read_text(encoding='utf-8') == contents
    builder.assert_not_called()