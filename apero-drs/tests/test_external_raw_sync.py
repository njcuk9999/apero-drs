#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for external raw directory mirroring."""

import os
from pathlib import Path
from typing import Any

import pytest

from apero.tools.module.processing import drs_processing
from apero.setup.core import drs_setup
from apero.tools.module.setup import drs_assets


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


@pytest.mark.parametrize('source_mode', ['symlink', 'hardlink', None, 'missing'])
def test_setup_populates_raw_after_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    spirou_params: drs_setup.ParamDict, source_mode: str | None
) -> None:
    """Setup mirrors configured raw files after cleanup, before completion.

    :param tmp_path: temporary directory for raw files and setup config
    :param monkeypatch: fixture isolating setup side effects
    :param spirou_params: profile-free APERO parameters from apero.dev
    :param source_mode: link mode, disabled source, or missing directory
    :return: None
    """
    _quiet_sync(monkeypatch)
    external = tmp_path / 'external'
    raw = tmp_path / 'raw'
    config = tmp_path / 'config'
    config.mkdir()
    if source_mode != 'missing':
        external.mkdir()
        (external / 'data.fits').write_bytes(b'raw data')
    link_type = source_mode if source_mode in ['symlink', 'hardlink'] else None
    profile = spirou_params.copy()
    profile['PATH.EXTERNAL_RAW'] = str(external) if source_mode else None
    profile['PATH.RAW'] = str(raw)
    profile['PATH.OTHER'] = str(tmp_path / 'other')
    profile['IPATH.EXTERNAL_RAW_TYPE'] = link_type
    setup_params = drs_setup.ParamDict()
    setup_params['CONFIG_PATH'] = str(config)
    setup_params['NAME'] = 'test_setup'
    events = []

    def noop(*args: Any, **kwargs: Any) -> None:
        """Suppress setup side effects outside raw synchronization.

        :param args: ignored positional arguments
        :param kwargs: ignored keyword arguments
        :return: None
        """

    def cleanup(params: drs_setup.ParamDict) -> None:
        """Record cleanup before synchronization.

        :param params: setup parameters
        :return: None
        """
        events.append('cleanup')
        assert not raw.exists()

    def log(params: Any, level: str, message: Any, **kwargs: Any) -> None:
        """Record setup completion for ordering assertions.

        :param params: setup logging parameters
        :param level: logging level
        :param message: language database message
        :param kwargs: additional logging options
        :return: None
        """
        if message.tkey == '40-510-00042':
            events.append('complete')
            if link_type:
                assert (raw / 'data.fits').read_bytes() == b'raw data'

    original_sync = drs_processing.sync_external_raw

    def sync(params: drs_setup.ParamDict) -> None:
        """Run the real sync and record its setup ordering.

        :param params: loaded APERO profile parameters
        :return: None
        """
        assert params is profile
        events.append('sync')
        original_sync(params)

    for name in ['create_paths', 'create_yamls', 'create_user_configs',
                 'create_setup_files', 'create_install_script']:
        monkeypatch.setattr(drs_setup, name, noop)
    monkeypatch.setattr(drs_setup, 'clean_install', cleanup)
    monkeypatch.setattr(drs_setup, 'WLOG', log)
    monkeypatch.setattr(drs_processing, 'sync_external_raw', sync)
    monkeypatch.setattr(drs_assets, 'check_local_assets', lambda params: False)
    monkeypatch.setattr(drs_setup.base, 'DPARAMS', drs_setup.base.DPARAMS)
    monkeypatch.setattr(drs_setup.base, 'IPARAMS', drs_setup.base.IPARAMS)
    monkeypatch.setattr(drs_setup.base, 'load_database_yaml', lambda: dict())
    monkeypatch.setattr(drs_setup.base, 'load_install_yaml', lambda: dict())
    monkeypatch.setattr(drs_setup.load_functions, 'load_config',
                        lambda *args, **kwargs: profile)
    monkeypatch.setenv(drs_setup.base.USER_ENV, str(config))

    drs_setup.run_setup(setup_params, dict())

    assert events == ['cleanup', 'sync', 'complete']
    if link_type == 'symlink':
        assert (raw / 'data.fits').is_symlink()
    elif link_type == 'hardlink':
        assert os.path.samefile(raw / 'data.fits', external / 'data.fits')
    else:
        assert not raw.exists()