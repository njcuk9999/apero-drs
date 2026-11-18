#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Isolated coverage for opt-in profile data-directory creation."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask
from flask.testing import FlaskClient

from apero import dev
from apero_ri.application import apero_profiles_api_helpers as helpers
from apero_ri.application import ariapp_impls


@pytest.fixture()
def path_client() -> FlaskClient:
    """Return a profile-free client with no real services or profile data."""
    dev.get_base_params('SPIROU')
    service = SimpleNamespace()
    service._require_apero_profile_perm = lambda: (dict(username='admin'), [])
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.add_url_rule(
        '/validate', methods=['GET', 'POST'],
        view_func=lambda: ariapp_impls.ariapp_api_apero_profiles_validate(
            service),
    )
    return app.test_client()


def test_creation_requires_explicit_post(
    path_client: FlaskClient, tmp_path: Path,
) -> None:
    """Neither GET flags nor normal POST validation may create directories.

    Args:
        path_client: Isolated validation API client.
        tmp_path: Temporary filesystem root.
    """
    path = tmp_path / 'missing' / 'nested'
    response = path_client.get('/validate',
                               query_string=dict(path=str(path), create=True))
    assert response.json == dict(success=True, valid=False, exists=False)
    response = path_client.post('/validate', json=dict(path=str(path)))
    assert response.json == dict(success=True, valid=False, exists=False)
    assert not path.parent.exists()

    payload = dict(path=str(path), create=True)
    for _ in range(2):
        response = path_client.post('/validate', json=payload)
        assert response.json == dict(success=True, valid=True, exists=True)
        assert path.is_dir()


def test_creation_errors_are_visible(
    path_client: FlaskClient, tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Report mkdir failures instead of returning a successful validation.

    Args:
        path_client: Isolated validation API client.
        tmp_path: Temporary filesystem root.
        monkeypatch: Fixture replacing mkdir with a denied operation.
    """
    def deny_mkdir(self: Path, **kwargs: object) -> None:
        """Raise the simulated filesystem permission error."""
        raise PermissionError('denied')

    monkeypatch.setattr(Path, 'mkdir', deny_mkdir)
    response = path_client.post(
        '/validate', json=dict(path=str(tmp_path / 'missing'), create=True))
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'denied' in response.json['error']


def test_creation_never_creates_files_or_relative_paths(
    path_client: FlaskClient, tmp_path: Path,
) -> None:
    """Reject file creation, relative paths, and an existing regular file.

    Args:
        path_client: Isolated validation API client.
        tmp_path: Temporary filesystem root.
    """
    missing_file = tmp_path / 'trigger.log'
    payload = dict(path=str(missing_file), kind='file', create=True)
    assert path_client.post('/validate', json=payload).status_code == 400
    assert not missing_file.exists()
    payload = dict(path='relative/directory', create=True)
    assert path_client.post('/validate', json=payload).status_code == 400
    missing_file.write_text('keep')
    payload = dict(path=str(missing_file), create=True)
    response = path_client.post('/validate', json=payload)
    assert response.status_code == 400
    assert missing_file.read_text() == 'keep'


def test_unauthorized_creation_has_no_side_effects(tmp_path: Path) -> None:
    """Enforce profile permissions before any filesystem mutation.

    Args:
        tmp_path: Temporary filesystem root.
    """
    service = SimpleNamespace(_require_apero_profile_perm=lambda: (None, []))
    app = Flask(__name__)
    path = tmp_path / 'missing'
    payload = dict(path=str(path), create=True)
    with app.test_request_context('/validate', method='POST', json=payload):
        _, status = ariapp_impls.ariapp_api_apero_profiles_validate(service)
    assert status == 401
    assert not path.exists()


def test_editor_labels_use_request_language() -> None:
    """Load editor text in the language selected by the browser."""
    app = Flask(__name__)
    with app.test_request_context(headers={'Accept-Language': 'fr'}):
        labels = helpers.profile_editor_labels()
    assert labels['ADVANCED'] == 'Avancé'
    assert labels['WITH'] == 'Par'
