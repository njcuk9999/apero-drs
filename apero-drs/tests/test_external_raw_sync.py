#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for external raw directory mirroring."""

import os
from pathlib import Path
from typing import Any

import pytest

from apero.tools.module.processing import drs_processing


def _quiet_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable logging and progress output for deterministic sync tests."""
    monkeypatch.setattr(drs_processing, 'WLOG', lambda *args, **kwargs: None)
    monkeypatch.setattr(drs_processing, 'tqdm',
                        lambda items, **kwargs: items)


def _sync_params(external: Path, raw: Path, other: Path,
                 link_type: str = 'symlink') -> dict[str, Any]:
    """Build the minimal parameter mapping consumed by external raw sync."""
    return {
        'PATH.EXTERNAL_RAW': str(external),
        'PATH.RAW': str(raw),
        'PATH.OTHER': str(other),
        'IPATH.EXTERNAL_RAW_TYPE': link_type,
    }


def test_sync_skips_directory_symlink_loop_and_prunes_stale_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Stop ancestor loops and remove stale managed files only."""
    _quiet_sync(monkeypatch)
    external = tmp_path / 'external'
    raw = tmp_path / 'raw'
    other = tmp_path / 'other'
    nested = external / 'night'
    nested.mkdir(parents=True)
    raw.mkdir()
    (raw / 'unmanaged.txt').write_text('keep', encoding='utf-8')
    source = nested / 'keep.fits'
    stale_source = external / 'stale.fits'
    nested_stale_source = external / 'removed' / 'day' / 'stale.fits'
    source.write_text('data', encoding='utf-8')
    stale_source.write_text('old', encoding='utf-8')
    nested_stale_source.parent.mkdir(parents=True)
    nested_stale_source.write_text('old', encoding='utf-8')
    (nested / 'loop').symlink_to(external, target_is_directory=True)

    params = _sync_params(external, raw, other)
    drs_processing.sync_external_raw(params)

    linked_file = raw / 'night' / 'keep.fits'
    stale_file = raw / 'stale.fits'
    nested_stale_file = raw / 'removed' / 'day' / 'stale.fits'
    assert linked_file.is_symlink()
    assert linked_file.resolve() == source
    assert stale_file.is_symlink()
    assert nested_stale_file.is_symlink()
    assert not (raw / 'night' / 'loop').exists()
    assert not (raw / 'night' / 'loop').is_symlink()

    stale_source.unlink()
    nested_stale_source.unlink()
    nested_stale_source.parent.rmdir()
    nested_stale_source.parent.parent.rmdir()
    drs_processing.sync_external_raw(params)

    assert not os.path.lexists(stale_file)
    assert not os.path.lexists(nested_stale_file)
    assert not (raw / 'removed' / 'day').exists()
    assert (raw / 'unmanaged.txt').read_text(encoding='utf-8') == 'keep'
    assert linked_file.is_symlink()


def test_hardlink_sync_removes_stale_managed_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hard-linked managed files are pruned after source removal."""
    _quiet_sync(monkeypatch)
    external = tmp_path / 'external'
    raw = tmp_path / 'raw'
    other = tmp_path / 'other'
    external.mkdir()
    raw.mkdir()
    source = external / 'data.fits'
    source.write_bytes(b'data')
    params = _sync_params(external, raw, other, link_type='hardlink')

    drs_processing.sync_external_raw(params)

    destination = raw / source.name
    assert destination.is_file()
    assert os.stat(destination).st_ino == os.stat(source).st_ino
    source.unlink()
    drs_processing.sync_external_raw(params)
    assert not os.path.lexists(destination)