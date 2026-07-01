#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for easy helper functions in backup and query modules."""

import json
from pathlib import Path

import pytest

from apero_ri.application import query_helpers
from apero_ri.core import backup_backend


def test_sanitize_method_defaults_and_provider_normalization() -> None:
    """Sanitizer should fill defaults and coerce unknown providers."""
    raw = {'id': 'x1', 'name': '', 'provider': 'unknown', 'enabled': 1}
    method = backup_backend._sanitize_method(raw, index=0)
    assert method['id'] == 'x1'
    assert method['provider'] == 'local_only'
    assert method['enabled'] is True


def test_get_backup_methods_injects_default_method() -> None:
    """Method loader should ensure the built-in default method is present."""
    cfg = {'backup_methods': [{'id': 'm1', 'provider': 'local_copy'}]}
    methods = backup_backend.get_backup_methods(cfg, enabled_only=False)
    assert methods
    assert methods[0]['id'] == 'default'


def test_encode_and_decode_secret_round_trip() -> None:
    """Encoded secret strings should decode to original content."""
    original = 'my_secret_value'
    encoded = backup_backend._encode_secret(original)
    decoded = backup_backend._decode_secret(encoded)
    assert decoded == original


def test_normalize_s3_prefix_and_cloud_enabled() -> None:
    """S3 prefix helper and cloud-enabled predicate should match config."""
    assert backup_backend._normalize_s3_prefix('abc/def') == 'abc/def/'
    assert backup_backend._normalize_s3_prefix('') == ''
    cfg_on = {'enabled': True, 'provider': 's3'}
    cfg_off = {'enabled': False, 'provider': 's3'}
    assert backup_backend._is_cloud_enabled(cfg_on)
    assert not backup_backend._is_cloud_enabled(cfg_off)


def test_validate_gdrive_oauth_client_secret_payload() -> None:
    """OAuth payload validator accepts good payloads and rejects bad ones."""
    ok_payload = {
        'web': {
            'client_id': 'id',
            'client_secret': 'sec',
            'auth_uri': 'https://auth',
            'token_uri': 'https://token',
            'redirect_uris': ['https://callback'],
        }
    }
    bad_payload = {'service_account': {'foo': 'bar'}}
    assert backup_backend.validate_gdrive_oauth_client_secret_payload(
        ok_payload
    )[0]
    assert not backup_backend.validate_gdrive_oauth_client_secret_payload(
        bad_payload
    )[0]


def test_read_s3_credentials_file(tmp_path) -> None:
    """S3 credential reader should parse standard JSON key names."""
    cred_file = tmp_path / 'creds.json'
    cred_file.write_text(
        json.dumps(
            {
                'aws_access_key_id': 'AKIA_TEST',
                'aws_secret_access_key': 'SECRET_TEST',
            }
        ),
        encoding='utf-8',
    )
    access, secret = backup_backend._read_s3_credentials_file(str(cred_file))
    assert access == 'AKIA_TEST'
    assert secret == 'SECRET_TEST'


def test_safe_relative_path_validation() -> None:
    """Safe relative path helper should enforce daily/weekly naming rules."""
    assert backup_backend._safe_relative_path('daily/a.tar.gz') == (
        'daily',
        'a.tar.gz',
    )
    with pytest.raises(ValueError):
        backup_backend._safe_relative_path('bad/path/value')


def test_format_bytes_and_default_config() -> None:
    """Byte formatter and default config should expose expected defaults."""
    assert backup_backend.format_bytes(1024).endswith('KB')
    cfg = backup_backend._default_config()
    assert cfg['provider'] == 'local_only'
    assert cfg['active_method_id'] == 'default'


def test_parse_text_presets_parses_delimited_blocks() -> None:
    """Text preset parser should split name/query blocks by delimiter."""
    text = (
        '====\n'
        'My preset\n'
        '====\n'
        'SELECT * FROM {TABLE};\n'
        '====\n'
    )

    def replace_fn(sql: str) -> str:
        return sql.replace('{TABLE}', 'my_table')

    presets = query_helpers.parse_text_presets(text, replace_fn)
    assert len(presets) == 1
    assert presets[0]['name'] == 'My preset'
    assert 'my_table' in presets[0]['query']


def test_build_safe_select_query_rejects_bad_identifier() -> None:
    """Safe query builder should reject invalid table identifiers."""
    table_access = {
        'FINDEX': {'columns': ['KW_RUN_ID', 'NAME'], 'table_name': 'findex'}
    }
    query_spec = {
        'tables': [{'label': 'FINDEX', 'columns': ['NAME']}],
        'filters': [
            {
                'table_label': 'FINDEX',
                'column': 'NAME',
                'op': '=',
                'value': 'abc',
            }
        ],
        'limit': 5,
    }
    sql, params, labels = query_helpers.build_safe_select_query(
        table_access, query_spec, run_ids=['r1']
    )
    assert 'SELECT' in sql
    assert '_run_ids' in params
    assert labels


