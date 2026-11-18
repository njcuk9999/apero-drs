#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Deterministic, profile-free download award regression tests."""
from pathlib import Path

import pytest

from apero.dev import get_base_params
from aperocore.base import base
from apero_ri.core import awards
from apero_ri.core import download_tracker


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tests.test_download_awards'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__
_PARAMS = get_base_params('SPIROU')


# =============================================================================
# Define functions
# =============================================================================
def test_download_awards(tmp_path: Path,
                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Combine categories, include non-monitors and give tied scores medals.

    :param tmp_path: Isolated tracker directory.
    :param monkeypatch: Fixture restoring tracker state and statistics.
    :return: None.
    """
    monkeypatch.setattr(download_tracker, 'ARI_DIR', tmp_path)
    monkeypatch.setattr(awards, 'compute_user_hours',
                        lambda directory, instruments: dict())
    monkeypatch.setattr(awards, 'compute_resolved_issue_counts',
                        lambda directory: dict(helper=250))
    download_tracker.record_download('alice', 'api', 100, 2)
    download_tracker.record_download('alice', 'basket', 100, 3)
    download_tracker.record_download('bob', 'basket', 200, 8)
    download_tracker.record_download('carol', 'api', 50, 1)
    download_tracker.record_download('zero', 'api', 0, 0)
    result = awards.compute_awards(tmp_path, [])
    assert result['alice']['download_bytes'] == 200
    assert result['alice']['download_files'] == 5
    assert result['alice']['download_medals'] == dict(
        bytes='gold', files='silver')
    assert result['bob']['download_medals'] == dict(bytes='gold', files='gold')
    assert result['carol']['download_medals']['bytes'] == 'silver'
    assert result['zero']['download_medals'] == dict(bytes=None, files=None)
    assert result['helper']['download_files'] == 0
    assert result['helper']['issues_medal'] == 'bronze'


def test_monitor_awards_and_reset(tmp_path: Path,
                                 monkeypatch: pytest.MonkeyPatch) -> None:
    """Retain monitor medals and update awards after a tracker reset.

    :param tmp_path: Isolated tracker directory.
    :param monkeypatch: Fixture restoring tracker state and statistics.
    :return: None.
    """
    from apero_ri.application.notifications_api_helpers import (
        _user_award_summary)

    monkeypatch.setattr(download_tracker, 'ARI_DIR', tmp_path)
    monitoring = dict(monitor=dict(
        who='Monitor', total_hours=200.0,
        instruments=dict(SPIROU=dict(hours_estimated=200.0))))
    monkeypatch.setattr(awards, 'compute_user_hours',
                        lambda directory, instruments: monitoring)
    monkeypatch.setattr(awards, 'compute_resolved_issue_counts',
                        lambda directory: dict())
    for index, username in enumerate(('first', 'second', 'third', 'fourth')):
        download_tracker.record_download(username, 'api', 400 - 100 * index)
    result = awards.compute_awards(tmp_path, ['SPIROU'])
    assert result['monitor']['instrument_medals'] == dict(SPIROU='gold')
    assert result['monitor']['service_medal'] == 'gold'
    assert result['third']['download_medals']['bytes'] == 'bronze'
    assert result['fourth']['download_medals']['bytes'] is None
    summary = _user_award_summary(result, 'first')
    assert summary['download_bytes'] == 400
    assert summary['download_medals']['bytes'] == 'gold'
    download_tracker.reset_user_usage('first', 'api')
    result = awards.compute_awards(tmp_path, ['SPIROU'])
    assert 'first' not in result
    assert result['second']['download_medals']['bytes'] == 'gold'


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================