#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Isolated API tests for moving APERO profiles between instruments."""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml
from flask import Flask

from apero_ri.application import apero_profiles_api_helpers as helpers
from apero_ri.core import auth


@pytest.fixture()
def profile_api(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> SimpleNamespace:
    """Build an isolated save API backed by a temporary profile YAML file."""
    profile_file = tmp_path / 'apero_profiles.yaml'
    monkeypatch.setattr(auth, 'APERO_PROFILES_FILE', profile_file)
    monkeypatch.setattr(auth, 'ADMIN_DIR', tmp_path)
    monkeypatch.setattr(auth, 'ensure_ari_directory', lambda: None)
    monkeypatch.setattr(auth, '_profiles_cache', dict())
    params = dict(instruments=dict(value=['SPIROU', 'NIRPS']))
    monkeypatch.setattr(helpers, 'load_parameters', lambda: params)
    monkeypatch.setattr(helpers.audit_log, 'record', lambda **kwargs: None)
    service = SimpleNamespace()
    service._require_apero_profile_perm = lambda: (dict(username='admin'), [])
    service._normalize_db_source = lambda value: value
    service._load_local_db_definitions = lambda: dict(local=dict(port=3306))
    service._refresh_admin_health_after_change = lambda *args: None
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.add_url_rule(
        '/save', view_func=lambda: helpers.api_apero_profiles_save(
            service, tmp_path
        ), methods=['POST'],
    )
    payload: dict[str, Any] = dict()
    payload['instrument'] = 'NIRPS'
    payload['original_instrument'] = 'SPIROU'
    payload['name'] = 'default_v08'
    payload['apero_version'] = '0.8.012'
    payload['reduction_server'] = 'reduction.example'
    payload['DATABASE_SOURCE'] = 'local'
    payload['DATABASE_LOCAL_NAME'] = 'local'
    payload['DATABASE_USERNAME'] = 'user'
    payload['DATABASE_PASSWORD'] = ' password with spaces '
    payload['DATABASE_NAME'] = 'database'
    payload['SCIENCE_FIBER'] = 'AB'
    payload['SCIENCE_TYPES'] = ['OBJ_FP']
    for key in ['ASTROM', 'CALIB', 'FINDEX', 'LOG', 'TELLU', 'REJECT']:
        payload[f'{key}_TABLENAME'] = key.lower()
    for key in ['RAW', 'PP', 'RED', 'CALIB', 'OUT', 'TELLU', 'LOG',
                'LBL', 'CHECK', 'OTHER']:
        payload[f'PATH_{key}'] = str(tmp_path / key.lower())
    preset_dir = tmp_path / 'resources' / 'aprofile_instruments'
    preset_dir.mkdir(parents=True)
    (preset_dir / 'preset.yaml').write_text('general: {}\n')
    payload['APERO_INSTRUMENT_PROFILE'] = 'preset.yaml'
    source = dict(DISPLAY_ORDER=3, groups=['team'], disabled=True)
    source['general'] = dict(INSTRUMENT='SPIROU', instrument='SPIROU',
                             custom='retained')
    source['database'] = dict(custom='database-setting')
    source['paths'] = dict(custom='path-setting')
    source['custom'] = dict(setting=['retained'])
    profiles = dict(SPIROU=dict(default_v08=source),
                    NIRPS=dict(other=dict(DISPLAY_ORDER=7)))
    auth.save_apero_profiles(profiles)
    return SimpleNamespace(client=app.test_client(), payload=payload,
                           profiles=profiles, path=profile_file)


def test_move_removes_source_and_preserves_settings(
    profile_api: SimpleNamespace,
) -> None:
    """Persist exactly one profile at the destination with its settings."""
    response = profile_api.client.post('/save', json=profile_api.payload)
    assert response.status_code == 200
    assert response.json == dict(success=True)
    stored = yaml.safe_load(profile_api.path.read_text())
    assert 'default_v08' not in stored['SPIROU']
    moved = stored['NIRPS']['default_v08']
    assert moved['general']['INSTRUMENT'] == 'NIRPS'
    assert moved['general']['instrument'] == 'NIRPS'
    assert moved['general']['custom'] == 'retained'
    assert moved['groups'] == ['team']
    assert moved['disabled'] is True
    assert moved['custom'] == dict(setting=['retained'])
    assert moved['database']['custom'] == 'database-setting'
    assert moved['paths']['custom'] == 'path-setting'
    assert moved['database']['DATABASE_PASSWORD'] == ' password with spaces '
    assert moved['DISPLAY_ORDER'] == 8
    assert stored['NIRPS']['other'] == dict(DISPLAY_ORDER=7)
    cached = auth.load_apero_profiles(hydrate=False, include_temporary=True)
    assert cached == stored
    assert sum('default_v08' in items for items in stored.values()) == 1


@pytest.mark.parametrize(
    'failure,status',
    [('duplicate', 409), ('missing', 404), ('instrument', 400),
     ('groups', 400), ('preset', 400)],
)
def test_failed_move_does_not_change_profiles(
    profile_api: SimpleNamespace, failure: str, status: int,
) -> None:
    """Reject invalid moves without changing persisted or cached profiles."""
    if failure == 'duplicate':
        profile_api.profiles['NIRPS']['default_v08'] = dict(groups=['other'])
    elif failure == 'missing':
        del profile_api.profiles['SPIROU']['default_v08']
    elif failure == 'instrument':
        profile_api.payload['instrument'] = 'UNKNOWN'
    elif failure == 'groups':
        profile_api.payload['groups'] = []
    elif failure == 'preset':
        profile_api.payload['APERO_INSTRUMENT_PROFILE'] = 'missing.yaml'
    auth.save_apero_profiles(profile_api.profiles)
    before = profile_api.path.read_bytes()
    cached = auth.load_apero_profiles(hydrate=False, include_temporary=True)
    snapshot = deepcopy(cached)
    response = profile_api.client.post('/save', json=profile_api.payload)
    assert response.status_code == status
    assert response.json['success'] is False
    assert response.json['error']
    assert profile_api.path.read_bytes() == before
    assert cached == snapshot


@pytest.mark.parametrize('explicit_source', [True, False])
def test_same_instrument_edit_stays_in_place(
    profile_api: SimpleNamespace, explicit_source: bool,
) -> None:
    """Keep normal edits working with and without the source field."""
    profile_api.payload['instrument'] = 'SPIROU'
    if not explicit_source:
        profile_api.payload.pop('original_instrument')
    response = profile_api.client.post('/save', json=profile_api.payload)
    assert response.status_code == 200
    stored = yaml.safe_load(profile_api.path.read_text())
    assert 'default_v08' in stored['SPIROU']
    assert 'default_v08' not in stored['NIRPS']
    assert stored['SPIROU']['default_v08']['DISPLAY_ORDER'] == 3
    assert stored['SPIROU']['default_v08']['groups'] == ['team']
    assert stored['SPIROU']['default_v08']['disabled'] is True


def test_move_to_empty_instrument(profile_api: SimpleNamespace) -> None:
    """Create the destination bucket without leaving a source copy."""
    del profile_api.profiles['NIRPS']
    auth.save_apero_profiles(profile_api.profiles)
    response = profile_api.client.post('/save', json=profile_api.payload)
    assert response.status_code == 200
    stored = yaml.safe_load(profile_api.path.read_text())
    assert stored['SPIROU'] == dict()
    assert stored['NIRPS']['default_v08']['DISPLAY_ORDER'] == 1


def test_new_profile_save_still_creates(profile_api: SimpleNamespace) -> None:
    """Creating a profile without a source must not move another profile."""
    profile_api.payload.pop('original_instrument')
    profile_api.payload['name'] = 'new_profile'
    profile_api.payload['groups'] = ['team']
    response = profile_api.client.post('/save', json=profile_api.payload)
    assert response.status_code == 200
    stored = yaml.safe_load(profile_api.path.read_text())
    assert 'default_v08' in stored['SPIROU']
    assert 'new_profile' in stored['NIRPS']
