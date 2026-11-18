#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Queue rows keep every night and check of batch APERO-check runs."""
from pathlib import Path

from apero_ri.application import apero_checks_api_helpers as ach
from apero_ri.core import task_runner

# =============================================================================
# Define variables
# =============================================================================
NIGHTS = ['2026-11-10', '2026-11-11', '2026-11-12', '2026-11-13',
          '2026-11-14', '2026-11-15']


# =============================================================================
# Define functions
# =============================================================================
def test_task_meta_keeps_every_night_and_check() -> None:
    """Running/queued metadata lists all requested nights and checks."""
    task_cfg = dict(obs_dirs=list(NIGHTS), checks=['calib_test', 'astrom'],
                    filters=dict(APERO_PROFILE_INCLUDE='nirps_he_rali'))
    meta = ach._manual_task_meta_from_task_cfg(task_cfg)
    assert meta['obsdirs'] == NIGHTS
    assert meta['check_keys'] == ['CALIB_TEST', 'ASTROM']
    # The first items stay available for single-value consumers.
    assert meta['obsdir'] == NIGHTS[0]
    assert meta['check_key'] == 'CALIB_TEST'
    assert meta['mode'] == 'single_check'


def test_task_meta_full_profile_run() -> None:
    """A run without obsdirs is reported as a full-profile re-run."""
    meta = ach._manual_task_meta_from_task_cfg(dict(filters=dict()))
    assert meta['mode'] == 'full_profile'
    assert meta['obsdirs'] == [] and meta['check_keys'] == []


def test_profile_history_keeps_lists(monkeypatch, tmp_path: Path) -> None:
    """History entries store every night and check of a batch run."""
    history_file = tmp_path / 'history.jsonl'
    monkeypatch.setattr(task_runner, '_profile_history_file_path',
                        lambda profile_id: history_file)
    hargs = dict(profile_id='p', task_id='manual_apero_check__p__batch',
                 task_name='APERO Check Task', status='completed',
                 obsdir=NIGHTS[0], check_key='CALIB_TEST',
                 task_mode='check', obsdirs=list(NIGHTS),
                 check_keys=['CALIB_TEST'])
    task_runner.append_profile_check_history(**hargs)
    rows = task_runner.get_profile_check_history('p')
    assert rows[0]['obsdirs'] == NIGHTS
    assert rows[0]['check_keys'] == ['CALIB_TEST']
