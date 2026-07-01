#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `apero_ri.core.download_tracker`."""

from datetime import datetime, timedelta, timezone

from apero_ri.core import download_tracker as tracker


def test_settings_round_trip(tmp_path) -> None:
    """Saving tracker settings should persist normalized numeric values."""
    tracker.set_ari_dir(tmp_path)
    saved = tracker.save_settings({'api_rate_limit_seconds': 3.5})
    loaded = tracker.load_settings()
    assert saved['api_rate_limit_seconds'] == 3.5
    assert loaded['api_rate_limit_seconds'] == 3.5


def test_record_and_get_user_usage(tmp_path) -> None:
    """Recorded usage should accumulate bytes and file counts."""
    tracker.set_ari_dir(tmp_path)
    tracker.record_download('alice', 'api', file_bytes=100, file_count=2)
    tracker.record_download('alice', 'api', file_bytes=50, file_count=1)
    usage = tracker.get_user_usage('alice', 'api')
    assert usage['total_bytes'] == 150
    assert usage['total_files'] == 3
    assert usage['last_download_at']


def test_list_and_reset_usage(tmp_path) -> None:
    """Listing should include users and reset should remove one entry."""
    tracker.set_ari_dir(tmp_path)
    tracker.record_download('alice', 'basket', file_bytes=100)
    tracker.record_download('bob', 'basket', file_bytes=50)
    all_rows = tracker.list_all_usage('basket')
    assert len(all_rows) == 2
    tracker.reset_user_usage('alice', 'basket')
    usage = tracker.get_user_usage('alice', 'basket')
    assert usage['total_bytes'] == 0


def test_check_rate_limit_returns_wait_time_when_recent(tmp_path) -> None:
    """Rate-limit check should return remaining seconds for recent activity."""
    tracker.set_ari_dir(tmp_path)
    tracker.save_settings({'api_rate_limit_seconds': 10})
    tracker.record_download('alice', 'api', file_bytes=1)
    wait = tracker.check_rate_limit('alice', 'api')
    assert wait is not None
    assert 0 <= wait <= 10


def test_check_rate_limit_handles_old_timestamp(tmp_path) -> None:
    """Rate-limit check should allow action when last download is old enough."""
    tracker.set_ari_dir(tmp_path)
    tracker.save_settings({'api_rate_limit_seconds': 1})
    data = tracker._load()
    data['api_usage']['alice'] = {
        'total_bytes': 1,
        'total_files': 1,
        'last_download_at': (
            datetime.now(timezone.utc) - timedelta(seconds=20)
        ).isoformat(),
    }
    tracker._save(data)
    assert tracker.check_rate_limit('alice', 'api') is None


def test_format_bytes_handles_negative_and_units() -> None:
    """Byte formatter should clamp negatives and provide readable units."""
    assert tracker.format_bytes(-1) == '0 B'
    assert tracker.format_bytes(1024).endswith('KB')

