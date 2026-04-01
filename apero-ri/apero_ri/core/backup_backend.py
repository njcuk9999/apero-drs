#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI: cloud backup backend helpers.

Configuration is stored in {ARI_DIR}/admin/general/backup.yaml.
The backend supports unattended backup mirroring with setup-once credentials.
"""

from __future__ import annotations

import base64
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from apero_ri.core import secret_store as ss


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.backup_backend'
# Provider metadata used by the admin UI.
PROVIDER_DEFAULTS: Dict[str, Dict[str, Any]] = {
    'gdrive_oauth': {
        'label': 'Google Drive (OAuth user consent)',
        'help_url': 'https://developers.google.com/drive/api/guides/about-sdk',
        'help_steps': [
            'Create a Google Cloud project and enable the Google Drive API.',
            'Create OAuth client credentials and download the client secret JSON file.',
            'Upload the OAuth client JSON below and save settings.',
            'Click Connect Google account and complete the consent flow.',
            'Create or choose a Drive folder for backups from your account.',
            'Copy the Drive folder ID from the URL and paste it below.',
            'Run Test connection and Test backup.',
        ],
    },
    's3': {
        'label': 'Amazon S3',
        'help_url': 'https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html',
        'help_steps': [
            'Create an S3 bucket dedicated to APERO backups.',
            'Create an IAM user with least-privilege access to that bucket.',
            'Store access key ID and secret access key below.',
            'Set an optional prefix (for example apero/backups).',
            'Run Test connection, then Save settings.',
        ],
    },
    'local_only': {
        'label': 'Local only (no cloud mirror)',
        'help_url': '',
        'help_steps': [
            'No cloud provider is used.',
            'Backups are kept only on local disk under LOCAL_DATA_DIR/backups.',
        ],
    },
}

SECRET_FIELDS = {
    's3_secret_access_key': 's3_secret_access_key_enc',
}

MANAGED_SECRET_PATHS = {
    'gdrive_oauth_client_secret_file': 'gdrive_oauth_client_secret.json',
    'gdrive_oauth_token_file': 'gdrive_oauth_token.json',
    's3_credentials_file': 's3_credentials.json',
}


# =============================================================================
# Define functions
# =============================================================================
def _get_backup_config_path() -> Path:
    ari_dir = os.environ.get('ARI_DIR', os.path.expanduser('~/.ari'))
    admin_dir = Path(ari_dir) / 'admin'
    general_dir = admin_dir / 'general'
    general_dir.mkdir(parents=True, exist_ok=True)
    config_file = general_dir / 'backup.yaml'
    legacy_file = admin_dir / 'backup.yaml'
    if not config_file.exists() and legacy_file.exists():
        try:
            config_file.write_bytes(legacy_file.read_bytes())
        except Exception:
            pass
    return config_file


def _get_s3_secret_access_key_path() -> Path:
    return ss.resolve_secret_file('s3_secret_access_key.txt')


def _write_secret_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')
    ss.protect_path(path, 0o600)


def _maybe_migrate_managed_secret_path(field_name: str,
                                       path_value: str,
                                       allow_blank: bool = False) -> str:
    value = str(path_value or '').strip()
    ari_dir = ss.get_ari_dir()
    target_name = MANAGED_SECRET_PATHS[field_name]
    legacy_candidates: List[Path] = []

    if field_name == 'gdrive_oauth_token_file':
        legacy_candidates.append(ari_dir / 'admin' / 'gdrive_oauth_token.json')
    elif field_name == 'gdrive_oauth_client_secret_file':
        legacy_candidates.append(
            ari_dir / 'admin' / 'gdrive_oauth_client_secret.json')
    elif field_name == 's3_credentials_file':
        legacy_candidates.append(ari_dir / 'admin' / 's3_credentials.json')

    backups_dir = ari_dir / 'backups'
    if value:
        current = Path(value).expanduser().resolve()
        if current.parent == backups_dir and current.suffix.lower() == '.json':
            legacy_candidates.append(current)
            return str(ss.resolve_secret_file(target_name, legacy_candidates))
        if (field_name == 'gdrive_oauth_token_file'
                and current == (ari_dir / 'admin'
                                / 'gdrive_oauth_token.json')):
            legacy_candidates.append(current)
            return str(ss.resolve_secret_file(target_name, legacy_candidates))
        return str(current)

    if allow_blank:
        managed = ss.resolve_secret_file(target_name, legacy_candidates)
        return str(managed) if managed.exists() else ''
    return str(ss.resolve_secret_file(target_name, legacy_candidates))


def _migrate_backup_secret_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    cfg['gdrive_oauth_token_file'] = _maybe_migrate_managed_secret_path(
        'gdrive_oauth_token_file',
        str(cfg.get('gdrive_oauth_token_file', '') or ''),
        allow_blank=False,
    )
    cfg['gdrive_oauth_client_secret_file'] = (
        _maybe_migrate_managed_secret_path(
            'gdrive_oauth_client_secret_file',
            str(cfg.get('gdrive_oauth_client_secret_file', '') or ''),
            allow_blank=True,
        )
    )
    cfg['s3_credentials_file'] = _maybe_migrate_managed_secret_path(
        's3_credentials_file',
        str(cfg.get('s3_credentials_file', '') or ''),
        allow_blank=True,
    )

    legacy_secret = _decode_secret(
        str(cfg.get('s3_secret_access_key_enc', '') or '')).strip()
    secret_path = _get_s3_secret_access_key_path()
    if legacy_secret and not secret_path.exists():
        _write_secret_text(secret_path, legacy_secret)
    return cfg


def _encode_secret(value: str) -> str:
    return base64.b64encode(value.encode('utf-8')).decode('utf-8')


def _decode_secret(value: str) -> str:
    try:
        return base64.b64decode(value.encode('utf-8')).decode('utf-8')
    except Exception:
        return ''


def _default_config() -> Dict[str, Any]:
    return {
        'enabled': False,
        'provider': 'gdrive_oauth',
        'gdrive_oauth_client_secret_file': '',
        'gdrive_oauth_token_file': '',
        'gdrive_folder_id': '',
        's3_bucket': '',
        's3_prefix': 'apero/backups',
        's3_region': '',
        's3_endpoint_url': '',
        's3_access_key_id': '',
        's3_credentials_file': '',
        's3_secret_access_key_enc': '',
    }


def load_backup_config() -> Dict[str, Any]:
    """Load backup config from disk and merge with defaults."""
    cfg = _default_config()
    path = _get_backup_config_path()
    if not path.exists():
        return cfg

    try:
        with open(path, 'r', encoding='utf-8') as handle:
            loaded = yaml.safe_load(handle) or {}
        if isinstance(loaded, dict):
            cfg.update(loaded)
    except Exception:
        return cfg

    # Legacy migration from service-account provider to OAuth provider.
    if str(cfg.get('provider', '')).strip() == 'gdrive_service_account':
        cfg['provider'] = 'gdrive_oauth'
    if (not str(cfg.get('gdrive_oauth_client_secret_file', '')).strip()
            and str(cfg.get('gdrive_service_account_file', '')).strip()):
        cfg['gdrive_oauth_client_secret_file'] = str(
            cfg.get('gdrive_service_account_file', '')
        ).strip()

    provider = str(cfg.get('provider', 'gdrive_oauth')).strip()
    if provider not in PROVIDER_DEFAULTS:
        cfg['provider'] = 'gdrive_oauth'
    cfg = _migrate_backup_secret_config(cfg)
    return cfg


def save_backup_config(cfg: Dict[str, Any]) -> None:
    """Persist backup config to disk with lightweight secret encoding."""
    path = _get_backup_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    out_cfg = _default_config()
    out_cfg.update(cfg)
    out_cfg = _migrate_backup_secret_config(out_cfg)

    for plain_field, enc_field in SECRET_FIELDS.items():
        plain_value = out_cfg.pop(plain_field, None)
        if plain_field == 's3_secret_access_key':
            secret_path = _get_s3_secret_access_key_path()
            if plain_value is not None:
                text = str(plain_value).strip()
                if text:
                    _write_secret_text(secret_path, text)
                else:
                    secret_path.unlink(missing_ok=True)
            out_cfg.pop(enc_field, None)
            continue
        if plain_value is not None:
            text = str(plain_value).strip()
            if text:
                out_cfg[enc_field] = _encode_secret(text)

    with open(path, 'w', encoding='utf-8') as handle:
        yaml.safe_dump(out_cfg, handle, default_flow_style=False,
                       allow_unicode=True, sort_keys=True)


def get_secret(cfg: Dict[str, Any], field_name: str) -> str:
    """Return decoded secret from config if available."""
    if field_name == 's3_secret_access_key':
        secret_path = _get_s3_secret_access_key_path()
        if secret_path.exists():
            try:
                return secret_path.read_text(encoding='utf-8').strip()
            except Exception:
                return ''
    enc_field = SECRET_FIELDS.get(field_name)
    if not enc_field:
        return ''
    return _decode_secret(str(cfg.get(enc_field, '') or ''))


def format_bytes(size: int) -> str:
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f'{value:.2f} {unit}'
        value /= 1024.0
    return f'{size} B'


def _normalize_s3_prefix(prefix: str) -> str:
    pref = str(prefix or '').strip().strip('/')
    return f'{pref}/' if pref else ''


def _is_cloud_enabled(cfg: Dict[str, Any]) -> bool:
    if not bool(cfg.get('enabled', False)):
        return False
    provider = str(cfg.get('provider', 'local_only')).strip()
    return provider in {'gdrive_oauth', 's3'}


def get_gdrive_oauth_token_path(cfg: Dict[str, Any]) -> Path:
    """Return configured OAuth token file path, with secret-dir fallback."""
    token_path = str(cfg.get('gdrive_oauth_token_file', '') or '').strip()
    if token_path:
        return Path(token_path).expanduser().resolve()
    ari_dir = ss.get_ari_dir()
    return ss.resolve_secret_file(
        'gdrive_oauth_token.json',
        legacy_paths=[ari_dir / 'admin' / 'gdrive_oauth_token.json'],
    )


def save_gdrive_oauth_token(cfg: Dict[str, Any],
                            token_dict: Dict[str, Any]) -> Path:
    """Persist Google OAuth user token JSON and return its full path."""
    token_path = get_gdrive_oauth_token_path(cfg)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    with open(token_path, 'w', encoding='utf-8') as handle:
        json.dump(token_dict, handle, indent=2)
    return token_path


def has_gdrive_oauth_token(cfg: Dict[str, Any]) -> bool:
    """Whether Google OAuth token exists on disk."""
    return get_gdrive_oauth_token_path(cfg).exists()


def validate_gdrive_oauth_client_secret_payload(
        payload: Any) -> Tuple[bool, str]:
    """Validate that a Google OAuth client JSON payload is usable for web/app flow."""
    if not isinstance(payload, dict):
        return False, 'Google OAuth client secret file must contain a JSON object.'

    if 'web' in payload:
        section_name = 'web'
    elif 'installed' in payload:
        section_name = 'installed'
    else:
        return False, (
            'Google OAuth client secret JSON must contain a top-level "web" or '
            '"installed" section. Upload an OAuth client JSON, not a service-account key.'
        )

    section = payload.get(section_name, {})
    if not isinstance(section, dict):
        return False, f'Google OAuth client secret file has an invalid "{section_name}" section.'

    required_keys = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
    missing = [key for key in required_keys
               if not str(section.get(key, '')).strip()]
    if missing:
        return False, (
            'Google OAuth client secret JSON is missing required fields: '
            + ', '.join(missing)
        )

    redirect_uris = section.get('redirect_uris', [])
    if section_name == 'web' and (
            not isinstance(redirect_uris, list) or not redirect_uris):
        return False, (
            'Google OAuth web client JSON must include at least one redirect URI. '
            'Add the APERO RI callback URL in Google Cloud Console and download the JSON again.'
        )

    return True, ''


def validate_gdrive_oauth_client_secret_file(
        path_value: str) -> Tuple[bool, str]:
    """Validate that a Google OAuth client JSON file is usable for web/app flow."""
    path = Path(str(path_value or '').strip()).expanduser()
    if not str(path_value or '').strip():
        return False, 'Google OAuth client secret JSON file is required.'
    if not path.exists() or not path.is_file():
        return False, f'Google OAuth client secret file does not exist: {path}'

    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except Exception:
        return False, f'Google OAuth client secret file is not valid JSON: {path}'

    return validate_gdrive_oauth_client_secret_payload(payload)


def _provider_requirements_ok(cfg: Dict[str, Any]) -> Tuple[bool, str]:
    provider = str(cfg.get('provider', 'local_only')).strip()
    if provider == 'gdrive_oauth':
        client_secret_file = Path(
            str(cfg.get('gdrive_oauth_client_secret_file', '')).strip()
        ).expanduser()
        folder_id = str(cfg.get('gdrive_folder_id', '')).strip()
        oauth_ok, oauth_err = validate_gdrive_oauth_client_secret_file(
            str(client_secret_file))
        if not oauth_ok:
            return False, oauth_err
        if not folder_id:
            return False, 'Google Drive folder ID is required.'
        if not has_gdrive_oauth_token(cfg):
            return False, 'Google account not connected. Use Connect Google account in backup settings.'
        return True, ''

    if provider == 's3':
        bucket = str(cfg.get('s3_bucket', '')).strip()
        access_key, secret_key = _resolve_s3_credentials(cfg)
        if not bucket:
            return False, 'S3 bucket is required.'
        if not access_key:
            return False, 'S3 access key ID is required (or provide it in an S3 credentials JSON file).'
        if not secret_key:
            return False, 'S3 secret access key is required (or provide it in an S3 credentials JSON file).'
        return True, ''

    return False, 'No cloud provider configured.'


GDRIVE_OAUTH_SCOPES = ['https://www.googleapis.com/auth/drive']


def _build_google_drive_service(cfg: Dict[str, Any]):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except Exception as exc:
        raise RuntimeError(
            'Google Drive dependencies are missing. Install google-auth, google-auth-oauthlib, and google-api-python-client.'
        ) from exc

    token_path = get_gdrive_oauth_token_path(cfg)
    if not token_path.exists():
        raise RuntimeError('Google OAuth token file not found. Connect Google account first.')

    try:
        with open(token_path, 'r', encoding='utf-8') as handle:
            token_data = json.load(handle)
    except Exception as exc:
        raise RuntimeError(f'Could not read Google OAuth token file: {token_path}') from exc

    credentials = Credentials.from_authorized_user_info(
        token_data, GDRIVE_OAUTH_SCOPES)
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_gdrive_oauth_token(cfg, json.loads(credentials.to_json()))
        else:
            raise RuntimeError('Google OAuth token is invalid or expired; reconnect Google account.')

    return build('drive', 'v3', credentials=credentials,
                 cache_discovery=False)


def _gdrive_find_child_folder(service, parent_id: str,
                              name: str,
                              create_if_missing: bool = False
                              ) -> Optional[str]:
    query = (
        "mimeType='application/vnd.google-apps.folder' and trashed=false "
        f"and name='{name}' and '{parent_id}' in parents"
    )
    result = service.files().list(
        q=query,
        fields='files(id, name)',
        pageSize=1,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = result.get('files', [])
    if files:
        return files[0].get('id')

    if not create_if_missing:
        return None

    payload = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id],
    }
    folder = service.files().create(
        body=payload,
        fields='id',
        supportsAllDrives=True,
    ).execute()
    return folder.get('id')


def _gdrive_list_period(service, period_folder_id: str,
                        period: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    page_token = None
    while True:
        response = service.files().list(
            q=(f"'{period_folder_id}' in parents and trashed=false "
               "and mimeType!='application/vnd.google-apps.folder'"),
            fields='nextPageToken, files(id,name,size,modifiedTime)',
            pageSize=1000,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        for entry in response.get('files', []):
            name = str(entry.get('name', '')).strip()
            if not name:
                continue
            rel = f'{period}/{name}'
            out[rel] = {
                'provider_id': entry.get('id', ''),
                'name': name,
                'period': period,
                'relative_path': rel,
                'size_bytes': int(entry.get('size', 0) or 0),
                'mtime': entry.get('modifiedTime', ''),
            }
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    return out


def _gdrive_validate_shared_drive_target(
        service, folder_id: str) -> Dict[str, Any]:
    """Validate that target folder is accessible."""
    meta = service.files().get(
        fileId=folder_id,
        fields='id,name,mimeType,driveId',
        supportsAllDrives=True,
    ).execute()
    return meta


def _gdrive_upload_file(service, parent_id: str, file_path: Path,
                        existing_id: Optional[str] = None) -> None:
    try:
        from googleapiclient.http import MediaFileUpload
    except Exception as exc:
        raise RuntimeError(
            'Google Drive dependencies are missing. Install google-api-python-client.'
        ) from exc

    media = MediaFileUpload(
        str(file_path), mimetype='application/gzip', resumable=False)
    if existing_id:
        service.files().update(
            fileId=existing_id,
            media_body=media,
            supportsAllDrives=True,
        ).execute()
        return

    payload = {
        'name': file_path.name,
        'parents': [parent_id],
    }
    service.files().create(
        body=payload,
        media_body=media,
        fields='id',
        supportsAllDrives=True,
    ).execute()


def _build_s3_client(cfg: Dict[str, Any]):
    try:
        import boto3
    except Exception as exc:
        raise RuntimeError('boto3 is required for S3 backups.') from exc

    access_key_id, secret_access_key = _resolve_s3_credentials(cfg)
    kwargs = {
        'aws_access_key_id': access_key_id,
        'aws_secret_access_key': secret_access_key,
    }
    region = str(cfg.get('s3_region', '')).strip()
    endpoint = str(cfg.get('s3_endpoint_url', '')).strip()
    if region:
        kwargs['region_name'] = region
    if endpoint:
        kwargs['endpoint_url'] = endpoint
    return boto3.client('s3', **kwargs)


def _resolve_s3_credentials(cfg: Dict[str, Any]) -> Tuple[str, str]:
    """Resolve S3 credentials from explicit fields or optional JSON file."""
    access_key = str(cfg.get('s3_access_key_id', '')).strip()
    secret_key = get_secret(cfg, 's3_secret_access_key').strip()
    if access_key and secret_key:
        return access_key, secret_key

    file_access, file_secret = _read_s3_credentials_file(
        str(cfg.get('s3_credentials_file', '')).strip()
    )
    if not access_key:
        access_key = file_access
    if not secret_key:
        secret_key = file_secret
    return access_key, secret_key


def _read_s3_credentials_file(path_value: str) -> Tuple[str, str]:
    """Read access/secret keys from a JSON credentials file if present."""
    if not path_value:
        return '', ''

    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        return '', ''

    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except Exception:
        return '', ''

    if not isinstance(payload, dict):
        return '', ''

    root_access = str(
        payload.get('aws_access_key_id', '')
        or payload.get('AccessKeyId', '')).strip()
    root_secret = str(
        payload.get('aws_secret_access_key', '')
        or payload.get('SecretAccessKey', '')).strip()

    creds = payload.get('Credentials', {})
    if isinstance(creds, dict):
        cred_access = str(creds.get('AccessKeyId', '')).strip()
        cred_secret = str(creds.get('SecretAccessKey', '')).strip()
    else:
        cred_access = ''
        cred_secret = ''

    access_key = root_access or cred_access
    secret_key = root_secret or cred_secret
    return access_key, secret_key


def _s3_list_period(client, bucket: str, prefix: str,
                    period: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    period_prefix = f'{prefix}{period}/'
    token = None

    while True:
        kwargs: Dict[str, Any] = {
            'Bucket': bucket,
            'Prefix': period_prefix,
            'MaxKeys': 1000,
        }
        if token:
            kwargs['ContinuationToken'] = token
        response = client.list_objects_v2(**kwargs)
        for obj in response.get('Contents', []):
            key = str(obj.get('Key', '')).strip()
            if not key or key.endswith('/'):
                continue
            name = key.split('/')[-1]
            rel = f'{period}/{name}'
            out[rel] = {
                'provider_id': key,
                'name': name,
                'period': period,
                'relative_path': rel,
                'size_bytes': int(obj.get('Size', 0) or 0),
                'mtime': (obj.get('LastModified').isoformat()
                          if obj.get('LastModified') else ''),
            }

        if not response.get('IsTruncated'):
            break
        token = response.get('NextContinuationToken')

    return out


def test_backup_connection(
        cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Test configured cloud backup connection."""
    if cfg is None:
        cfg = load_backup_config()

    provider = str(cfg.get('provider', 'local_only')).strip()
    if provider == 'local_only' or not bool(cfg.get('enabled', False)):
        return {
            'ok': True,
            'error': '',
            'detail': 'Cloud mirror disabled (local-only mode).',
            'query_ms': 0,
        }

    req_ok, req_err = _provider_requirements_ok(cfg)
    if not req_ok:
        return {'ok': False, 'error': req_err, 'detail': '', 'query_ms': None}

    start = time.perf_counter()
    try:
        if provider == 'gdrive_oauth':
            service = _build_google_drive_service(cfg)
            folder_id = str(cfg.get('gdrive_folder_id', '')).strip()
            _gdrive_validate_shared_drive_target(service, folder_id)

        elif provider == 's3':
            client = _build_s3_client(cfg)
            bucket = str(cfg.get('s3_bucket', '')).strip()
            prefix = _normalize_s3_prefix(str(cfg.get('s3_prefix', '')))
            client.head_bucket(Bucket=bucket)
            client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)

        else:
            return {
                'ok': False,
                'error': f'Unsupported provider: {provider}',
                'detail': '',
                'query_ms': None,
            }

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            'ok': True,
            'error': '',
            'detail': 'Connection successful.',
            'query_ms': elapsed_ms,
        }
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {'ok': False, 'error': str(exc),
                'detail': '', 'query_ms': elapsed_ms}


def test_backup_roundtrip(
        cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run a backup probe by writing, validating, and deleting one test object."""
    if cfg is None:
        cfg = load_backup_config()

    provider = str(cfg.get('provider', 'local_only')).strip()
    if provider == 'local_only' or not bool(cfg.get('enabled', False)):
        return {
            'ok': False,
            'error': 'Cloud mirror is disabled. Enable it before running backup probe.',
            'detail': '',
            'query_ms': None,
        }

    req_ok, req_err = _provider_requirements_ok(cfg)
    if not req_ok:
        return {'ok': False, 'error': req_err, 'detail': '', 'query_ms': None}

    probe_name = f'ari_backup_probe_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}.json'
    probe_payload = ('{"probe":"apero-ri","ts":"'
                     + datetime.now(timezone.utc).isoformat()
                     + '","ok":true}\n').encode('utf-8')

    start = time.perf_counter()
    try:
        if provider == 'gdrive_oauth':
            service = _build_google_drive_service(cfg)
            root_id = str(cfg.get('gdrive_folder_id', '')).strip()
            _gdrive_validate_shared_drive_target(service, root_id)
            daily_id = _gdrive_find_child_folder(
                service, root_id, 'daily', create_if_missing=True)
            if not daily_id:
                raise RuntimeError('Could not create/find daily folder in Google Drive.')

            try:
                from googleapiclient.http import MediaInMemoryUpload
            except Exception as exc:
                raise RuntimeError(
                    'Google Drive dependencies are missing. Install google-api-python-client.'
                ) from exc

            media = MediaInMemoryUpload(
                probe_payload, mimetype='application/json', resumable=False)
            created = service.files().create(
                body={'name': probe_name, 'parents': [daily_id]},
                media_body=media,
                fields='id,size',
                supportsAllDrives=True,
            ).execute()
            probe_id = str(created.get('id', '')).strip()
            if not probe_id:
                raise RuntimeError('Probe upload to Google Drive did not return a file ID.')

            # Verify probe object is queryable immediately.
            service.files().get(
                fileId=probe_id,
                fields='id,size,name',
                supportsAllDrives=True,
            ).execute()

            service.files().delete(
                fileId=probe_id, supportsAllDrives=True).execute()

        elif provider == 's3':
            client = _build_s3_client(cfg)
            bucket = str(cfg.get('s3_bucket', '')).strip()
            prefix = _normalize_s3_prefix(str(cfg.get('s3_prefix', '')))
            probe_key = f'{prefix}daily/{probe_name}'

            client.put_object(Bucket=bucket, Key=probe_key, Body=probe_payload,
                              ContentType='application/json')
            client.head_object(Bucket=bucket, Key=probe_key)
            client.delete_object(Bucket=bucket, Key=probe_key)

        else:
            return {
                'ok': False,
                'error': f'Unsupported provider: {provider}',
                'detail': '',
                'query_ms': None,
            }

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            'ok': True,
            'error': '',
            'detail': 'Backup probe succeeded (write/read/delete).',
            'query_ms': elapsed_ms,
        }
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            'ok': False,
            'error': str(exc),
            'detail': '',
            'query_ms': elapsed_ms,
        }


def _local_backup_root(local_data_dir: Optional[Path]) -> Path:
    if local_data_dir is None:
        ari_dir = Path(os.environ.get('ARI_DIR', os.path.expanduser('~/.ari')))
        return (ari_dir / 'backups').expanduser().resolve()
    return (Path(local_data_dir).expanduser().resolve() / 'backups')


def list_local_backups(
        local_data_dir: Optional[Path] = None) -> Dict[str, Any]:
    """List local daily/weekly backups."""
    backup_root = _local_backup_root(local_data_dir)
    daily_dir = backup_root / 'daily'
    weekly_dir = backup_root / 'weekly'

    def _list_period(period: str, directory: Path) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        if not directory.exists():
            return rows
        for path in sorted(directory.glob('*.tar.gz')):
            try:
                st = path.stat()
            except OSError:
                continue
            rows.append({
                'name': path.name,
                'period': period,
                'relative_path': f'{period}/{path.name}',
                'size_bytes': int(st.st_size),
                'mtime': datetime.fromtimestamp(
                    st.st_mtime, tz=timezone.utc).isoformat(),
            })
        return rows

    daily_rows = _list_period('daily', daily_dir)
    weekly_rows = _list_period('weekly', weekly_dir)
    total_bytes = sum(row['size_bytes'] for row in daily_rows + weekly_rows)

    return {
        'backup_root': str(backup_root),
        'daily': daily_rows,
        'weekly': weekly_rows,
        'total_count': len(daily_rows) + len(weekly_rows),
        'total_bytes': total_bytes,
    }


def list_cloud_backups(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List cloud backups for configured provider."""
    if cfg is None:
        cfg = load_backup_config()

    provider = str(cfg.get('provider', 'local_only')).strip()
    if not _is_cloud_enabled(cfg):
        return {
            'configured': False,
            'provider': provider,
            'ok': True,
            'error': '',
            'query_ms': 0,
            'daily': [],
            'weekly': [],
            'total_count': 0,
            'total_bytes': 0,
        }

    req_ok, req_err = _provider_requirements_ok(cfg)
    if not req_ok:
        return {
            'configured': False,
            'provider': provider,
            'ok': False,
            'error': req_err,
            'query_ms': None,
            'daily': [],
            'weekly': [],
            'total_count': 0,
            'total_bytes': 0,
        }

    start = time.perf_counter()
    try:
        all_rows: Dict[str, Dict[str, Any]] = {}

        if provider == 'gdrive_oauth':
            service = _build_google_drive_service(cfg)
            root_id = str(cfg.get('gdrive_folder_id', '')).strip()
            daily_id = _gdrive_find_child_folder(
                service, root_id, 'daily', create_if_missing=False)
            weekly_id = _gdrive_find_child_folder(
                service, root_id, 'weekly', create_if_missing=False)
            if daily_id:
                all_rows.update(
                    _gdrive_list_period(service, daily_id, 'daily'))
            if weekly_id:
                all_rows.update(
                    _gdrive_list_period(service, weekly_id, 'weekly'))

        elif provider == 's3':
            client = _build_s3_client(cfg)
            bucket = str(cfg.get('s3_bucket', '')).strip()
            prefix = _normalize_s3_prefix(str(cfg.get('s3_prefix', '')))
            all_rows.update(_s3_list_period(client, bucket, prefix, 'daily'))
            all_rows.update(_s3_list_period(client, bucket, prefix, 'weekly'))

        else:
            return {
                'configured': False,
                'provider': provider,
                'ok': False,
                'error': f'Unsupported provider: {provider}',
                'query_ms': None,
                'daily': [],
                'weekly': [],
                'total_count': 0,
                'total_bytes': 0,
            }

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        values = sorted(all_rows.values(), key=lambda row: row['name'])
        daily = [row for row in values if row['period'] == 'daily']
        weekly = [row for row in values if row['period'] == 'weekly']
        total_bytes = sum(int(row.get('size_bytes', 0) or 0) for row in values)
        return {
            'configured': True,
            'provider': provider,
            'ok': True,
            'error': '',
            'query_ms': elapsed_ms,
            'daily': daily,
            'weekly': weekly,
            'total_count': len(values),
            'total_bytes': total_bytes,
        }
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            'configured': True,
            'provider': provider,
            'ok': False,
            'error': str(exc),
            'query_ms': elapsed_ms,
            'daily': [],
            'weekly': [],
            'total_count': 0,
            'total_bytes': 0,
        }


def _remote_map(cfg: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    cloud = list_cloud_backups(cfg)
    if not cloud.get('ok', False):
        raise RuntimeError(
        str(cloud.get('error', 'Could not list cloud backups.')))
    out: Dict[str, Dict[str, Any]] = {}
    for row in cloud.get('daily', []) + cloud.get('weekly', []):
        out[str(row.get('relative_path', ''))] = dict(row)
    return out


def sync_local_backups_to_cloud(local_data_dir: Optional[Path] = None,
                                cfg: Optional[Dict[str, Any]] = None
                                ) -> Dict[str, Any]:
    """Mirror local daily/weekly backup archives to configured cloud provider."""
    if cfg is None:
        cfg = load_backup_config()

    provider = str(cfg.get('provider', 'local_only')).strip()
    if not _is_cloud_enabled(cfg):
        return {
            'configured': False,
            'ok': True,
            'warning': 'Cloud backup is not enabled; skipping cloud mirror.',
            'provider': provider,
            'query_ms': 0,
            'uploaded': 0,
            'updated': 0,
            'deleted': 0,
            'cloud_total_bytes': 0,
            'cloud_total_count': 0,
        }

    req_ok, req_err = _provider_requirements_ok(cfg)
    if not req_ok:
        return {
            'configured': False,
            'ok': False,
            'warning': req_err,
            'provider': provider,
            'query_ms': None,
            'uploaded': 0,
            'updated': 0,
            'deleted': 0,
            'cloud_total_bytes': 0,
            'cloud_total_count': 0,
        }

    local = list_local_backups(local_data_dir)
    local_map: Dict[str, Dict[str, Any]] = {}
    backup_root = Path(local['backup_root'])

    for row in local.get('daily', []) + local.get('weekly', []):
        rel = str(row.get('relative_path', ''))
        if not rel:
            continue
        local_map[rel] = {
            'path': backup_root / rel,
            'size_bytes': int(row.get('size_bytes', 0) or 0),
        }

    start = time.perf_counter()
    uploaded = 0
    updated = 0
    deleted = 0

    try:
        remote_before = _remote_map(cfg)

        if provider == 'gdrive_oauth':
            service = _build_google_drive_service(cfg)
            root_id = str(cfg.get('gdrive_folder_id', '')).strip()
            period_folder_ids = {
                'daily': _gdrive_find_child_folder(
                    service, root_id, 'daily', create_if_missing=True),
                'weekly': _gdrive_find_child_folder(
                    service, root_id, 'weekly', create_if_missing=True),
            }

            for rel, local_row in local_map.items():
                period = rel.split('/', 1)[0]
                parent_id = period_folder_ids.get(period)
                if not parent_id:
                    continue
                remote_row = remote_before.get(rel)
                remote_id = (
                    str(remote_row.get('provider_id', ''))
                    if remote_row else None)
                if remote_row and (
                        int(remote_row.get('size_bytes', 0) or 0)
                        == local_row['size_bytes']):
                    continue
                _gdrive_upload_file(
                    service, parent_id,
                    local_row['path'], existing_id=remote_id)
                if remote_row:
                    updated += 1
                else:
                    uploaded += 1

            for rel, remote_row in remote_before.items():
                if rel in local_map:
                    continue
                remote_id = str(remote_row.get('provider_id', ''))
                if remote_id:
                    service.files().delete(fileId=remote_id,
                                           supportsAllDrives=True).execute()
                    deleted += 1

        elif provider == 's3':
            client = _build_s3_client(cfg)
            bucket = str(cfg.get('s3_bucket', '')).strip()
            prefix = _normalize_s3_prefix(str(cfg.get('s3_prefix', '')))

            for rel, local_row in local_map.items():
                remote_row = remote_before.get(rel)
                key = f'{prefix}{rel}'
                if remote_row and (
                        int(remote_row.get('size_bytes', 0) or 0)
                        == local_row['size_bytes']):
                    continue
                client.upload_file(str(local_row['path']), bucket, key)
                if remote_row:
                    updated += 1
                else:
                    uploaded += 1

            for rel, remote_row in remote_before.items():
                if rel in local_map:
                    continue
                key = str(remote_row.get('provider_id', '')).strip()
                if key:
                    client.delete_object(Bucket=bucket, Key=key)
                    deleted += 1

        else:
            return {
                'configured': True,
                'ok': False,
                'warning': f'Unsupported provider: {provider}',
                'provider': provider,
                'query_ms': None,
                'uploaded': 0,
                'updated': 0,
                'deleted': 0,
                'cloud_total_bytes': 0,
                'cloud_total_count': 0,
            }

        cloud_after = list_cloud_backups(cfg)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            'configured': True,
            'ok': bool(cloud_after.get('ok', False)),
            'warning': str(cloud_after.get('error', '') or ''),
            'provider': provider,
            'query_ms': cloud_after.get('query_ms', elapsed_ms),
            'uploaded': uploaded,
            'updated': updated,
            'deleted': deleted,
            'cloud_total_bytes': int(cloud_after.get('total_bytes', 0) or 0),
            'cloud_total_count': int(cloud_after.get('total_count', 0) or 0),
        }
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            'configured': True,
            'ok': False,
            'warning': str(exc),
            'provider': provider,
            'query_ms': elapsed_ms,
            'uploaded': uploaded,
            'updated': updated,
            'deleted': deleted,
            'cloud_total_bytes': 0,
            'cloud_total_count': 0,
        }


def _safe_relative_path(relative_path: str) -> Tuple[str, str]:
    rel = str(relative_path or '').strip().replace('\\', '/')
    parts = [part for part in rel.split('/') if part]
    if len(parts) != 2:
        raise ValueError('Invalid backup path.')
    period, name = parts
    if period not in {'daily', 'weekly'}:
        raise ValueError('Backup path must be daily/<file> or weekly/<file>.')
    if '/' in name or '..' in name:
        raise ValueError('Invalid backup file name.')
    return period, name


def delete_backup(relative_path: str,
                  target: str = 'both',
                  local_data_dir: Optional[Path] = None,
                  cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Delete one backup from local and/or cloud target."""
    if cfg is None:
        cfg = load_backup_config()

    period, name = _safe_relative_path(relative_path)
    deleted_local = False
    deleted_cloud = False

    if target in {'local', 'both'}:
        backup_root = _local_backup_root(local_data_dir)
        local_path = backup_root / period / name
        if local_path.exists():
            local_path.unlink(missing_ok=True)
            deleted_local = True

    if target in {'cloud', 'both'} and _is_cloud_enabled(cfg):
        provider = str(cfg.get('provider', 'local_only')).strip()
        if provider == 'gdrive_oauth':
            service = _build_google_drive_service(cfg)
            root_id = str(cfg.get('gdrive_folder_id', '')).strip()
            period_id = _gdrive_find_child_folder(service, root_id, period,
                                                  create_if_missing=False)
            if period_id:
                rows = _gdrive_list_period(service, period_id, period)
                rel = f'{period}/{name}'
                row = rows.get(rel)
                if row and row.get('provider_id'):
                    service.files().delete(fileId=row['provider_id'],
                                           supportsAllDrives=True).execute()
                    deleted_cloud = True
        elif provider == 's3':
            client = _build_s3_client(cfg)
            bucket = str(cfg.get('s3_bucket', '')).strip()
            prefix = _normalize_s3_prefix(str(cfg.get('s3_prefix', '')))
            key = f'{prefix}{period}/{name}'
            client.delete_object(Bucket=bucket, Key=key)
            deleted_cloud = True

    return {
        'success': True,
        'deleted_local': deleted_local,
        'deleted_cloud': deleted_cloud,
    }


def delete_all_backups(period: str = 'all',
                       target: str = 'both',
                       local_data_dir: Optional[Path] = None,
                       cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Delete all backups for one period or all periods."""
    if cfg is None:
        cfg = load_backup_config()

    periods = ['daily', 'weekly'] if period == 'all' else [period]
    if any(p not in {'daily', 'weekly'} for p in periods):
        raise ValueError('Invalid period. Use daily, weekly, or all.')

    local_deleted = 0
    cloud_deleted = 0

    if target in {'local', 'both'}:
        backup_root = _local_backup_root(local_data_dir)
        for pval in periods:
            directory = backup_root / pval
            if not directory.exists():
                continue
            for path in directory.glob('*.tar.gz'):
                path.unlink(missing_ok=True)
                local_deleted += 1

    if target in {'cloud', 'both'} and _is_cloud_enabled(cfg):
        cloud_rows = list_cloud_backups(cfg)
        if cloud_rows.get('ok', False):
            for row in (cloud_rows.get('daily', [])
                        + cloud_rows.get('weekly', [])):
                rel = str(row.get('relative_path', ''))
                if not rel:
                    continue
                rel_period = rel.split('/', 1)[0]
                if rel_period not in periods:
                    continue
                try:
                    result = delete_backup(rel, target='cloud',
                                           local_data_dir=local_data_dir,
                                           cfg=cfg)
                    if result.get('deleted_cloud', False):
                        cloud_deleted += 1
                except Exception:
                    continue

    return {
        'success': True,
        'deleted_local': local_deleted,
        'deleted_cloud': cloud_deleted,
    }


def backup_inventory(local_data_dir: Optional[Path] = None,
                     cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return combined local/cloud backup inventory."""
    if cfg is None:
        cfg = load_backup_config()

    local = list_local_backups(local_data_dir)
    cloud = list_cloud_backups(cfg)

    local_map: Dict[str, Dict[str, Any]] = {}
    for row in local.get('daily', []) + local.get('weekly', []):
        local_map[row['relative_path']] = row

    cloud_map: Dict[str, Dict[str, Any]] = {}
    for row in cloud.get('daily', []) + cloud.get('weekly', []):
        cloud_map[row['relative_path']] = row

    all_keys = sorted(set(local_map.keys()) | set(cloud_map.keys()))
    rows: List[Dict[str, Any]] = []
    for key in all_keys:
        lrow = local_map.get(key)
        crow = cloud_map.get(key)
        period = key.split('/', 1)[0] if '/' in key else ''
        name = key.split('/', 1)[1] if '/' in key else key
        rows.append({
            'relative_path': key,
            'period': period,
            'name': name,
            'local_exists': lrow is not None,
            'local_size_bytes': int((lrow or {}).get('size_bytes', 0) or 0),
            'local_mtime': (lrow or {}).get('mtime', ''),
            'cloud_exists': crow is not None,
            'cloud_size_bytes': int((crow or {}).get('size_bytes', 0) or 0),
            'cloud_mtime': (crow or {}).get('mtime', ''),
        })

    return {
        'provider': cloud.get(
            'provider', str(cfg.get('provider', 'local_only'))),
        'cloud_configured': cloud.get('configured', False),
        'cloud_ok': cloud.get('ok', False),
        'cloud_error': cloud.get('error', ''),
        'query_ms': cloud.get('query_ms', None),
        'rows': rows,
        'local_total_bytes': int(local.get('total_bytes', 0) or 0),
        'local_total_count': int(local.get('total_count', 0) or 0),
        'cloud_total_bytes': int(cloud.get('total_bytes', 0) or 0),
        'cloud_total_count': int(cloud.get('total_count', 0) or 0),
        'local_backup_root': local.get('backup_root', ''),
    }


def download_cloud_backup(relative_path: str,
                         local_data_dir: Optional[Path] = None,
                         cfg: Optional[Dict[str, Any]] = None
                         ) -> Dict[str, Any]:
    """Download a specific cloud backup to local."""
    if cfg is None:
        cfg = load_backup_config()

    if local_data_dir is None:
        local_data_dir = _resolve_local_data_dir()

    provider = str(cfg.get('provider', 'local_only')).strip()
    if not _is_cloud_enabled(cfg):
        return {'ok': False, 'error': 'Cloud backup is not enabled.'}

    req_ok, req_err = _provider_requirements_ok(cfg)
    if not req_ok:
        return {'ok': False, 'error': req_err}

    backup_root = Path(local_data_dir) / 'backups'
    local_path = backup_root / relative_path

    if local_path.exists():
        return {'ok': False, 'error': f'Local backup already exists: {relative_path}'}

    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if provider == 'gdrive_oauth':
            service = _build_google_drive_service(cfg)
            root_id = str(cfg.get('gdrive_folder_id', '')).strip()
            
            # Navigate to the file in GDrive using the relative path
            parts = Path(relative_path).parts
            current_id = root_id
            for part in parts[:-1]:
                current_id = _gdrive_find_child_folder(
                    service, current_id, part)
                if not current_id:
                    return {'ok': False, 'error': f'Cloud path not found: {relative_path}'}
            
            file_name = Path(relative_path).name
            # Find the file in the final directory
            query = f"'{current_id}' in parents and name='{file_name}' and trashed=false"
            results = service.files().list(
                q=query, spaces='drive',
                fields='files(id, name)').execute()
            files = results.get('files', [])
            
            if not files:
                return {'ok': False, 'error': f'Cloud backup not found: {relative_path}'}

            cloud_file_id = files[0]['id']
            
            # Download the file
            request = service.files().get_media(fileId=cloud_file_id)
            with open(local_path, 'wb') as h:
                import io
                from googleapiclient.http import MediaIoBaseDownload
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                fh.seek(0)
                h.write(fh.read())
            
            return {'ok': True, 'path': str(local_path)}

        elif provider == 's3':
            s3_client = _build_s3_client(cfg)
            bucket = str(cfg.get('s3_bucket', '')).strip()
            prefix = str(cfg.get('s3_prefix', 'apero/backups')).strip()
            key = f'{prefix}/{relative_path}'

            s3_client.download_file(bucket, key, str(local_path))
            return {'ok': True, 'path': str(local_path)}

        return {'ok': False, 'error': f'Unsupported provider: {provider}'}

    except Exception as e:
        if local_path.exists():
            try:
                local_path.unlink()
            except Exception:
                pass
        return {'ok': False, 'error': f'Download failed: {str(e)}'}


def sync_cloud_backups_to_local(local_data_dir: Optional[Path] = None,
                                cfg: Optional[Dict[str, Any]] = None
                                ) -> Dict[str, Any]:
    """Download all cloud backups that don't exist locally."""
    if cfg is None:
        cfg = load_backup_config()

    if local_data_dir is None:
        local_data_dir = _resolve_local_data_dir()

    provider = str(cfg.get('provider', 'local_only')).strip()
    if not _is_cloud_enabled(cfg):
        return {'ok': False, 'downloaded': 0,
                'error': 'Cloud backup is not enabled.'}

    req_ok, req_err = _provider_requirements_ok(cfg)
    if not req_ok:
        return {'ok': False, 'downloaded': 0, 'error': req_err}

    local_backups = list_local_backups(local_data_dir)
    local_map = set()
    for row in (local_backups.get('daily', [])
                + local_backups.get('weekly', [])):
        rel = str(row.get('relative_path', ''))
        if rel:
            local_map.add(rel)

    cloud_backups = list_cloud_backups(cfg)
    cloud_files = []
    for row in (cloud_backups.get('daily', [])
                + cloud_backups.get('weekly', [])):
        rel = str(row.get('relative_path', ''))
        if rel and rel not in local_map:
            cloud_files.append(rel)

    if not cloud_files:
        return {'ok': True, 'downloaded': 0, 'message': 'All cloud backups are already downloaded.'}

    downloaded = 0
    errors = []

    for rel_path in cloud_files:
        result = download_cloud_backup(rel_path, local_data_dir, cfg)
        if result.get('ok'):
            downloaded += 1
        else:
            errors.append(result.get('error', 'Unknown error'))

    if errors:
        return {
            'ok': False,
            'downloaded': downloaded,
            'error': f'Downloaded {downloaded}/{len(cloud_files)} backups. Errors: {"; ".join(errors[:3])}',
        }

    return {'ok': True, 'downloaded': downloaded, 'message': f'Downloaded {downloaded} backup(s).'}



# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
