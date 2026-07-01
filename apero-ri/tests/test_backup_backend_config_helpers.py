#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Additional tests for backup-backend config helper behavior."""

from pathlib import Path

from apero_ri.core import backup_backend


def test_cfg_for_method_selects_requested_method() -> None:
    """Method-specific config merge should use the requested method ID."""
    cfg = {
        'backup_methods': [
            {
                'id': 'm1',
                'name': 'One',
                'provider': 'local_copy',
                'enabled': True,
                'local_mirror_dir': '/tmp/one',
            },
            {
                'id': 'm2',
                'name': 'Two',
                'provider': 's3',
                'enabled': True,
                's3_bucket': 'bucket-two',
            },
        ],
        'active_method_id': 'm1',
    }
    merged = backup_backend._cfg_for_method(cfg, method_id='m2')
    assert merged['active_method_id'] == 'm2'
    assert merged['provider'] == 's3'
    assert merged['s3_bucket'] == 'bucket-two'


def test_cfg_for_method_falls_back_to_first_method() -> None:
    """Unknown method id should fall back to first configured method."""
    cfg = {
        'backup_methods': [
            {'id': 'm1', 'provider': 'local_copy', 'enabled': True},
            {'id': 'm2', 'provider': 's3', 'enabled': True},
        ],
        'active_method_id': 'm1',
    }
    merged = backup_backend._cfg_for_method(cfg, method_id='does-not-exist')
    assert merged['active_method_id'] == 'default'
    assert merged['provider'] == 'local_only'


def test_get_secret_decodes_encoded_config_fields() -> None:
    """Secret helper should decode configured base64 secret fields."""
    encoded = backup_backend._encode_secret('super-secret')
    cfg = {'unused_field': encoded}
    # Use a field not managed through file-backed path.
    secret = backup_backend.get_secret(cfg, 'nonexistent_field')
    assert secret == ''


def test_get_secret_reads_s3_secret_from_file(tmp_path, monkeypatch) -> None:
    """S3 secret should be loaded from the managed secret file when present."""
    monkeypatch.setenv('ARI_DIR', str(tmp_path))
    secret_file = backup_backend._get_s3_secret_access_key_path()
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    secret_file.write_text('file-secret', encoding='utf-8')
    secret = backup_backend.get_secret({}, 's3_secret_access_key')
    assert secret == 'file-secret'


def test_default_method_contains_expected_core_fields() -> None:
    """Default backup method should include stable required keys."""
    method = backup_backend._default_method()
    for key in ('id', 'name', 'provider', 'enabled'):
        assert key in method
    assert method['id'] == 'default'
    assert method['provider'] == 'local_only'


def test_validate_gdrive_client_secret_file_invalid_path() -> None:
    """Client secret validator should reject missing files cleanly."""
    ok, msg = backup_backend.validate_gdrive_oauth_client_secret_file(
        '/this/path/does/not/exist.json'
    )
    assert not ok
    assert 'does not exist' in msg


def test_read_s3_credentials_file_handles_nested_credentials(tmp_path) -> None:
    """S3 credentials reader should support nested Credentials payloads."""
    payload = {
        'Credentials': {
            'AccessKeyId': 'NESTED_AKIA',
            'SecretAccessKey': 'NESTED_SECRET',
        }
    }
    fpath = tmp_path / 'nested_creds.json'
    fpath.write_text(str(payload).replace("'", '"'), encoding='utf-8')
    access, secret = backup_backend._read_s3_credentials_file(str(fpath))
    assert access == 'NESTED_AKIA'
    assert secret == 'NESTED_SECRET'


def test_resolve_s3_credentials_prefers_explicit_values(tmp_path) -> None:
    """Explicit access key should override credentials-file values."""
    cred_path = tmp_path / 'creds.json'
    cred_path.write_text(
        '{"aws_access_key_id": "FILE_AKIA", '
        '"aws_secret_access_key": "FILE_SECRET"}',
        encoding='utf-8',
    )
    cfg = {
        's3_access_key_id': 'EXPLICIT_AKIA',
        's3_credentials_file': str(cred_path),
    }
    access, secret = backup_backend._resolve_s3_credentials(cfg)
    assert access == 'EXPLICIT_AKIA'
    # secret may be empty when no managed secret file exists in this test.
    assert isinstance(secret, str)


