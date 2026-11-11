#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the extracted assets archive version marker."""

import io
import shutil
import tarfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from apero.tools.module.setup import drs_assets
from apero.tools.module.setup import drs_reset


@pytest.mark.parametrize('local_archive', [False, True])
def test_extraction_records_actual_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    spirou_params: Any, local_archive: bool
) -> None:
    """Record the extracted archive instead of an old bundled marker."""
    assets = tmp_path / 'assets'
    assets.mkdir()
    archive = assets / '1794397857_110257_assets.tar.gz'
    with tarfile.open(archive, 'w:gz') as bundle:
        old_version = b'old_version\n'
        member = tarfile.TarInfo('version.txt')
        member.size = len(old_version)
        bundle.addfile(member, io.BytesIO(old_version))
    params = spirou_params.copy()
    params['INPUTS'] = dict(INDIR=str(assets))
    monkeypatch.setattr(drs_assets.drs_data, 'construct_path',
                        lambda *args: str(tmp_path))
    manifest = dict(setup=dict(tarfile=archive.name))
    monkeypatch.setattr(drs_assets.base, 'load_yaml', lambda path: manifest)
    monkeypatch.setattr(drs_assets, 'WLOG', lambda *args, **kwargs: None)

    if local_archive:
        drs_assets.update_local_assets(params, str(archive))
    else:
        drs_assets.update_local_assets(params)

    marker = assets / 'version.txt'
    assert marker.read_text(encoding='utf-8') == '1794397857_110257\n'


def test_failed_extraction_clears_previous_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spirou_params: Any
) -> None:
    """Do not retain a misleading marker after an interrupted extraction."""
    assets = tmp_path / 'assets'
    assets.mkdir()
    archive = assets / 'broken_assets.tar.gz'
    archive.write_bytes(b'not an archive')
    marker = assets / 'version.txt'
    marker.write_text('old\n', encoding='utf-8')
    params = spirou_params.copy()
    params['INPUTS'] = dict(INDIR=str(assets))
    monkeypatch.setattr(drs_assets.drs_data, 'construct_path',
                        lambda *args: str(tmp_path))
    monkeypatch.setattr(drs_assets.base, 'load_yaml', lambda path: dict())
    monkeypatch.setattr(drs_assets, 'WLOG', lambda *args, **kwargs: None)

    with pytest.raises(drs_assets.AperoCodedException):
        drs_assets.update_local_assets(params, str(archive))

    assert not marker.exists()


def test_upload_checksums_skip_only_root_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spirou_params: Any
) -> None:
    """Do not publish the generated marker as an asset checksum."""
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'apero-assets.txt').write_text('assets', encoding='utf-8')
    (source / 'version.txt').write_text('old', encoding='utf-8')
    nested = source / 'spirou'
    nested.mkdir()
    (nested / 'version.txt').write_text('data', encoding='utf-8')
    params = spirou_params.copy()
    params['AURLS.UPLOAD_MODE'] = 'ssh'
    saved = []
    monkeypatch.setattr(drs_assets.drs_data, 'construct_path',
                        lambda *args: str(tmp_path))
    monkeypatch.setattr(drs_assets.base, 'write_yaml',
                        lambda data, path: saved.append(data))
    monkeypatch.setattr(drs_assets, 'WLOG', lambda *args, **kwargs: None)
    monkeypatch.setattr(drs_assets, 'upload_assets_ssh',
                        lambda *args: None)
    monkeypatch.setattr(drs_assets.drs_path, 'make_tarfile',
                        lambda *args, **kwargs: None)

    drs_assets.update_remote_assets(params, str(source))

    assert 'version.txt' not in saved[0]['data']
    assert 'spirou/version.txt' in saved[0]['data']


@pytest.mark.parametrize('existing_marker,needs_update',
                         [(False, False), (True, False), (True, True)])
def test_reset_copies_version_to_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    spirou_params: Any, existing_marker: bool, needs_update: bool
) -> None:
    """Reset extracts missing provenance once and copies the current marker."""
    source = tmp_path / 'source'
    profile = tmp_path / 'profile'
    source.mkdir()
    profile.mkdir()
    marker = source / 'version.txt'
    if existing_marker:
        marker.write_text('current\n', encoding='utf-8')
    (profile / 'version.txt').write_text('previous\n', encoding='utf-8')
    instrument = str(spirou_params['OBS.INSTRUMENT']).lower()
    for dirname in [instrument] + drs_reset.COMMON_ASSET_DIRS:
        (source / dirname).mkdir()
    params = spirou_params.copy()
    params['PATH.ASSETS'] = str(profile)
    params['IPATH.RESET_ASSETS'] = str(source)
    monkeypatch.setattr(drs_reset.drs_data, 'construct_path',
                        lambda params, unused, path: str(path))
    monkeypatch.setattr(drs_reset.manage_databases, 'list_databases',
                        lambda *args: None)
    monkeypatch.setattr(drs_reset.load_functions, 'load_pconfig',
                        lambda *args: None)
    monkeypatch.setattr(drs_assets, 'check_local_assets',
                        lambda params: needs_update)
    updates = []

    def update(params: Any) -> None:
        """Record extraction and create its version marker."""
        updates.append(True)
        marker.write_text('current\n', encoding='utf-8')

    def reset_dir(params: Any, name: str, destination: str,
                  origin: str, **kwargs: Any) -> None:
        """Copy defaults and verify the stale marker is not backed up."""
        if kwargs.get('backup'):
            assert not (profile / 'version.txt').exists()
        shutil.copytree(origin, destination, dirs_exist_ok=True)

    monkeypatch.setattr(drs_assets, 'update_local_assets', update)
    monkeypatch.setattr(drs_reset, 'reset_dbdir', reset_dir)
    recipe: Any = SimpleNamespace(shortname='reset')
    drs_reset.reset_assets(params, recipe, reset_dbs=False)

    assert updates == ([True] if needs_update or not existing_marker else [])
    assert (profile / 'version.txt').read_text(encoding='utf-8') == 'current\n'