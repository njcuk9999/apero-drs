#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Async task settings and per-task runtime state are stored separately."""

from pathlib import Path

import pytest
import yaml

from apero_ri.core import auth


# =============================================================================
# Define functions
# =============================================================================
@pytest.fixture()
def ari_root(tmp_path: Path) -> Path:
    """Point auth storage at an isolated directory for one test.

    :param tmp_path: Temporary directory.
    :return: Isolated ARI root.
    """
    original = auth.ARI_DIR
    auth.set_ari_dir(str(tmp_path))
    try:
        yield tmp_path
    finally:
        auth.set_ari_dir(str(original))


def _row(task_id: str, **fields: object) -> dict:
    """Build one task settings row.

    :param task_id: Task identifier.
    :param fields: Extra settings or runtime fields.
    :return: Task row.
    """
    return dict(dict(id=task_id, task_key='APERO_QC_STATS', active=True,
                     frequency=6.0), **fields)


def test_runtime_state_never_reaches_settings_file(ari_root: Path) -> None:
    """Saving merged rows writes settings only; state lives per task.

    :param ari_root: Isolated ARI root.
    :return: None.
    """
    auth.save_async_tasks(dict(SPIROU=[_row('t1')]))
    auth.save_task_state('t1', last_status='completed', run_count=3,
                         last_run_params=dict(INSTRUMENT='SPIROU'))
    merged = auth.load_async_tasks()
    row = merged['SPIROU'][0]
    assert row['last_status'] == 'completed' and row['run_count'] == 3
    # a settings edit on merged rows must not copy runtime into the YAML
    row['frequency'] = 12.0
    auth.save_async_tasks(merged)
    stored = yaml.safe_load(auth.ASYNC_TASKS_FILE.read_text())
    assert stored == dict(SPIROU=[_row('t1', frequency=12.0)])
    # partial updates keep the other fields; only the latest run is kept
    auth.save_task_state('t1', last_status='failed')
    state = auth.load_task_state('t1')
    assert state['last_status'] == 'failed' and state['run_count'] == 3
    with pytest.raises(ValueError):
        auth.save_task_state('t1', frequency=1.0)


def test_previous_settings_copy_rotates_only_on_change(ari_root: Path) -> None:
    """One previous settings copy is kept and replaced on real changes.

    :param ari_root: Isolated ARI root.
    :return: None.
    """
    previous = auth.async_tasks_previous_file()
    auth.save_async_tasks(dict(SPIROU=[_row('t1')]))
    auth.save_async_tasks(dict(SPIROU=[_row('t1', active=False)]))
    assert yaml.safe_load(previous.read_text()) == dict(
        SPIROU=[_row('t1')])
    # saving identical settings must not overwrite the useful backup
    auth.save_async_tasks(dict(SPIROU=[_row('t1', active=False)]))
    assert yaml.safe_load(previous.read_text()) == dict(
        SPIROU=[_row('t1')])
    # runtime-only changes are not settings changes
    auth.save_async_tasks(dict(SPIROU=[_row('t1', active=False,
                                            last_status='done')]))
    assert yaml.safe_load(previous.read_text()) == dict(
        SPIROU=[_row('t1')])


def test_migration_moves_state_and_drops_nested_history(
    ari_root: Path,
) -> None:
    """Old files with run state and nested params are split once.

    :param ari_root: Isolated ARI root.
    :return: None.
    """
    # an old-layout row whose params nest the previous run
    nested = dict(TASK_CONFIG=_row('t1', last_run_params=dict(
        TASK_CONFIG=_row('t1', last_run_params=dict(deep=True)))))
    old = dict(SPIROU=[_row('t1', last_run='2026-11-27', run_count=2,
                            last_status='completed',
                            last_run_params=nested)])
    auth.ASYNC_TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    auth.ASYNC_TASKS_FILE.write_text(yaml.safe_dump(old))
    assert auth.migrate_async_task_state() == 1
    stored = yaml.safe_load(auth.ASYNC_TASKS_FILE.read_text())
    assert stored == dict(SPIROU=[_row('t1')])
    state = auth.load_task_state('t1')
    assert state['run_count'] == 2 and state['last_run'] == '2026-11-27'
    # only this run's params survive, without the runs nested inside
    assert 'last_run_params' not in state['last_run_params']['TASK_CONFIG']
    backup = auth.ASYNC_TASKS_FILE.with_name('async_tasks.yaml.pre_split')
    assert yaml.safe_load(backup.read_text()) == old
    # a second start finds nothing to migrate
    assert auth.migrate_async_task_state() == 0


# =============================================================================
# End of code
# =============================================================================
