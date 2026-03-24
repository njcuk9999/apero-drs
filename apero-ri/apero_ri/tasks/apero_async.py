#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

Rules: Cannot import from apero_ri
"""
import json
import os
import socket
import subprocess
import time
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from astropy.io import fits

# =============================================================================
# Define variables
# =============================================================================
DB_UPDATE_TABLE_KEYS = (
    'ASTROM_TABLENAME',
    'CALIB_TABLENAME',
    'FINDEX_TABLENAME',
    'LOG_TABLENAME',
    'REJECT_TABLENAME',
    'TELLU_TABLENAME',
)



# =============================================================================
# Define global classes
# =============================================================================
class AperoAsyncTask:
    """Class representing an asynchronous task in APERO RI."""
    def __init__(self, name, description, status='pending'):
        # name and description
        self.name = name     
        self.description = description
        # Progress is a float between 0.0 and 1.0 representing the 
        # completion percentage
        self.progress = 0.0
        # Status can be 'pending', 'in_progress', 'completed', or 'failed'
        self.status = status
        # Long string (markdown) for writing the info page
        self.info = ''
        # list of output files this task produces (for use in the UI)
        self.output_files = []
        # last run (string "Never" or ISO timestamp of last run)
        self.last_run = 'Never'
        # number of times this task has been run
        self.run_count = 0

    def to_dict(self):
        """Convert the task to a dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'progress': self.progress,
            'info': self.info,
            'last_run': self.last_run,
            'output_files': self.output_files,
            'run_count': self.run_count,
        }
        
    def run_job(self, params: Dict[str, Any]):
        raise NotImplementedError('Subclasses must implement the '
                                  'run_job method.')

 
# =============================================================================
# Define common functions
# =============================================================================
def database_query(params: Dict[str, Any], query: str):
    """
    Execute a database query with the given parameters.

    parameters:
    - DATABASE_MODE: str, mysql+pymysql
    - DATABASE_HOST: str, the database host, e.g. localhost
    - DATABASE_USER: str, the database user, e.g. root
    - DATABASE_PASSWORD: str, the database password, e.g. password
    - DATABASE_NAME: str, the database name to connect to

    :param params: A dictionary of parameters for the query.
    :param query: The database query string to execute.
    :return: For row-returning queries, a list of dictionaries.
             For non-row-returning queries, a dictionary with ``rowcount``.
    """
    from urllib.parse import quote_plus

    from sqlalchemy import create_engine, text

    required = [
        'DATABASE_MODE',
        'DATABASE_HOST',
        'DATABASE_USER',
        'DATABASE_NAME',
    ]
    missing = [key for key in required if not params.get(key)]
    if missing:
        raise ValueError(f"Missing database parameter(s): {', '.join(missing)}")

    mode = str(params['DATABASE_MODE'])
    user = quote_plus(str(params['DATABASE_USER']))
    password = quote_plus(str(params['DATABASE_PASSWORD']))
    dbname = str(params['DATABASE_NAME'])
    host, port = _resolve_database_endpoint(params)

    db_url = f'{mode}://{user}:{password}@{host}:{port}/{dbname}'
    engine = create_engine(db_url, future=True)

    try:
        with engine.begin() as connection:
            result = connection.execute(text(query))
            if result.returns_rows:
                return [dict(row) for row in result.mappings().all()]
            return {'rowcount': result.rowcount}
    finally:
        engine.dispose()
        

def get_db_params(aparams: Dict[str, Any]):
    db_cfg = aparams.get('database', {})
    if not isinstance(db_cfg, dict):
        db_cfg = {}
    db_params = dict(db_cfg)
    for _k in (
        'DATABASE_MODE', 'DATABASE_HOST', 'DATABASE_PORT',
        'DATABASE_PASSWORD', 'DATABASE_NAME', 'DATABASE_USER',
        'DATABASE_USERNAME', 'DATABASE_USE_SSH_TUNNEL',
        'DATABASE_SSH_CONFIG_HOST', 'DATABASE_SSH_LOCAL_PORT',
        'DATABASE_SSH_REMOTE_PORT', 'LOCAL_DATA_DIR',
    ):
        if _k not in db_params and aparams.get(_k):
            db_params[_k] = aparams.get(_k)
    if 'DATABASE_USERNAME' in db_params and 'DATABASE_USER' not in db_params:
        db_params['DATABASE_USER'] = db_params['DATABASE_USERNAME']
    return db_params


def fill_dict_null(mykeys, mydict: Optional[dict] = None):
    # deal with no input dictionary
    if mydict is None:
        mydict = dict()
    # loop around keys and fill with nulls
    for key in mykeys:
        mydict[key] = None
    return mydict


def get_hdr_key(hdr: fits.Header, keyname: str,
                 hkey: Dict[str, Any]):
    header_key = hkey.get('key', 'Unknown')
    dtype = hkey.get('dtype', 'str')
    # try to open and type cast header key
    try:
        # deal with header key existing
        if header_key in hdr:
            raw_value = hdr[header_key]
            # deal with types
            if dtype == 'float':
                value = float(raw_value)
            elif dtype == 'int':
                value = int(raw_value)
            elif dtype == 'bool':
                value = bool(raw_value)
            else:
                value = str(raw_value)
        else:
            value = None
    except Exception as e:
        emsg = (f'Missing required parameter {keyname}: {header_key}'
                f'\n\tError {type(e)}: {e}')
        raise ValueError(emsg)
    # return values
    return value


# =============================================================================
# Define private functions
# =============================================================================
def _coerce_bool(value: Any) -> bool:
    """Return a predictable boolean for mixed config sources."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def _coerce_int(value: Any, field_name: str, *, default: Optional[int] = None,
                minimum: int = 1) -> int:
    """Normalize integer-like config values with a clear error message."""
    if value in (None, ''):
        if default is None:
            raise ValueError(f'Missing required value for {field_name}.')
        return int(default)
    try:
        ivalue = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f'Invalid integer for {field_name}: {value}') from None
    if ivalue < minimum:
        raise ValueError(f'{field_name} must be >= {minimum}.')
    return ivalue


def _split_host_port(host: Any, port: Any) -> Tuple[str, int]:
    """Split legacy host:port strings while supporting a separate port field."""
    host_str = str(host or '').strip()
    port_str = str(port or '').strip()
    if not host_str:
        raise ValueError('Missing required value for DATABASE_HOST.')

    parsed_host = host_str
    parsed_port: Optional[int] = None

    if host_str.count(':') == 1:
        maybe_host, maybe_port = host_str.rsplit(':', 1)
        if maybe_host and maybe_port.isdigit():
            parsed_host = maybe_host.strip()
            parsed_port = int(maybe_port)

    if port_str:
        explicit_port = _coerce_int(port_str, 'DATABASE_PORT')
        if parsed_port is not None and explicit_port != parsed_port:
            raise ValueError('DATABASE_HOST port and DATABASE_PORT do not match.')
        parsed_port = explicit_port

    if parsed_port is None:
        parsed_port = 3306
    return parsed_host, parsed_port


def _get_local_data_dir(params: Dict[str, Any]) -> Path:
    """Resolve the runtime local data dir for tunnel state files."""
    raw = (
        params.get('LOCAL_DATA_DIR')
        or os.environ.get('ARI_DIR')
        or str(Path.home() / '.ari')
    )
    return Path(str(raw)).expanduser().resolve()


def _is_local_port_open(port: int) -> bool:
    """Check whether a local TCP port already accepts connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex(('127.0.0.1', port)) == 0


def _tunnel_control_paths(params: Dict[str, Any], ssh_host: str,
                          remote_host: str, local_port: int,
                          remote_port: int) -> Tuple[Path, Path]:
    """Return stable state paths for one DB SSH tunnel definition."""
    state_root = _get_local_data_dir(params) / 'secret' / 'db_tunnels'
    state_root.mkdir(parents=True, exist_ok=True)
    signature = sha1(
        f'{ssh_host}|{remote_host}|{local_port}|{remote_port}'.encode('utf-8')
    ).hexdigest()[:16]
    return state_root / f'{signature}.sock', state_root / f'{signature}.meta'


def _check_existing_tunnel(control_path: Path, ssh_host: str) -> bool:
    """Return whether the SSH control socket still represents a live tunnel."""
    if not control_path.exists():
        return False
    result = subprocess.run(
        ['ssh', '-S', str(control_path), '-O', 'check', ssh_host],
        capture_output=True,
        text=True,
        timeout=6,
    )
    return result.returncode == 0


def _ensure_ssh_tunnel(params: Dict[str, Any]) -> Tuple[str, int]:
    """Ensure a reusable SSH local-forward exists and return local endpoint."""
    ssh_host = str(params.get('DATABASE_SSH_CONFIG_HOST') or '').strip()
    remote_host = str(params.get('DATABASE_HOST') or '').strip()
    if not ssh_host:
        raise ValueError('DATABASE_SSH_CONFIG_HOST is required when SSH tunneling is enabled.')
    if not remote_host:
        raise ValueError('DATABASE_HOST is required when SSH tunneling is enabled.')

    local_port = _coerce_int(
        params.get('DATABASE_SSH_LOCAL_PORT'),
        'DATABASE_SSH_LOCAL_PORT',
    )
    remote_port = _coerce_int(
        params.get('DATABASE_SSH_REMOTE_PORT'),
        'DATABASE_SSH_REMOTE_PORT',
        default=3306,
    )

    db_port_raw = str(params.get('DATABASE_PORT') or '').strip()
    if db_port_raw:
        db_port = _coerce_int(db_port_raw, 'DATABASE_PORT')
        if db_port != local_port:
            raise ValueError(
                'DATABASE_PORT must match DATABASE_SSH_LOCAL_PORT when SSH tunneling is enabled.'
            )

    control_path, meta_path = _tunnel_control_paths(
        params, ssh_host, remote_host, local_port, remote_port
    )

    if _check_existing_tunnel(control_path, ssh_host):
        return '127.0.0.1', local_port

    if control_path.exists():
        control_path.unlink()
    if meta_path.exists():
        meta_path.unlink()

    cmd = [
        'ssh',
        '-f',
        '-N',
        '-M',
        '-S', str(control_path),
        '-o', 'BatchMode=yes',
        '-o', 'ExitOnForwardFailure=yes',
        '-o', 'StrictHostKeyChecking=accept-new',
        '-o', 'ControlPersist=yes',
        '-o', 'ConnectTimeout=10',
        '-L', f'{local_port}:{remote_host}:{remote_port}',
        ssh_host,
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or 'Unknown SSH tunnel error').strip()
        raise RuntimeError(f'Failed to start SSH tunnel via {ssh_host}: {err}')

    for _ in range(10):
        if _check_existing_tunnel(control_path, ssh_host) or _is_local_port_open(local_port):
            meta_path.write_text(
                json.dumps({
                    'ssh_host': ssh_host,
                    'remote_host': remote_host,
                    'local_port': local_port,
                    'remote_port': remote_port,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                }, indent=2),
                encoding='utf-8',
            )
            return '127.0.0.1', local_port
        time.sleep(0.2)

    raise RuntimeError(
        f'SSH tunnel via {ssh_host} started but local port {local_port} did not become ready.'
    )


def _resolve_database_endpoint(params: Dict[str, Any]) -> Tuple[str, int]:
    """Resolve the effective DB host/port, starting an SSH tunnel if needed."""
    if _coerce_bool(params.get('DATABASE_USE_SSH_TUNNEL')):
        return _ensure_ssh_tunnel(params)
    return _split_host_port(params.get('DATABASE_HOST'), params.get('DATABASE_PORT'))


def _sql_quote(value: Any) -> str:
    """Escape a value for safe interpolation in a SQL string literal."""
    return str(value).replace("'", "''")


def get_profile_db_table_updates(aparams: Dict[str, Any],
                                 table_keys: Optional[Sequence[str]] = None
                                 ) -> Dict[str, str]:
    """Return UPDATE_TIME fingerprints for configured profile tables."""
    keys = list(table_keys or DB_UPDATE_TABLE_KEYS)
    db_params = get_db_params(aparams)
    schema = str(db_params.get('DATABASE_NAME') or '').strip()
    if not schema:
        raise ValueError('Missing required database name for update-time check.')

    db_cfg = aparams.get('database', {})
    if not isinstance(db_cfg, dict):
        db_cfg = {}

    table_names: List[Tuple[str, str]] = []
    for key in keys:
        table_name = db_cfg.get(key, aparams.get(key))
        if table_name in (None, ''):
            raise ValueError(f'Missing required parameter: database.{key}')
        table_names.append((key, str(table_name)))

    in_clause = ', '.join([f"'{_sql_quote(name)}'" for _, name in table_names])
    query = (
        'SELECT table_name, UPDATE_TIME '
        'FROM information_schema.tables '
        f"WHERE table_schema = '{_sql_quote(schema)}' "
        f'AND table_name IN ({in_clause});'
    )
    rows = database_query(db_params, query)
    by_table: Dict[str, Any] = {}
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            tname = str(row.get('table_name') or '').strip()
            if not tname:
                continue
            by_table[tname] = row.get('UPDATE_TIME')

    updates: Dict[str, str] = {}
    for key, table_name in table_names:
        raw_value = by_table.get(table_name)
        if isinstance(raw_value, datetime):
            if raw_value.tzinfo is None:
                raw_value = raw_value.replace(tzinfo=timezone.utc)
            updates[key] = raw_value.astimezone(timezone.utc).isoformat()
        elif raw_value is None:
            updates[key] = ''
        else:
            updates[key] = str(raw_value)
    return updates


def should_skip_profile_query(aparams: Dict[str, Any],
                              table_keys: Optional[Sequence[str]] = None,
                              force_run: bool = False
                              ) -> Tuple[bool, Dict[str, str], str]:
    """Return whether a profile query can be skipped based on table updates."""
    if force_run:
        current_updates = get_profile_db_table_updates(aparams, table_keys)
        return False, current_updates, 'Force run requested; bypassing DB update-time skip.'

    keys = list(table_keys or DB_UPDATE_TABLE_KEYS)
    current_updates = get_profile_db_table_updates(aparams, keys)

    stored_updates = aparams.get('database-update', {})
    if not isinstance(stored_updates, dict):
        stored_updates = {}
    missing_keys = [key for key in keys if key not in stored_updates]
    if missing_keys:
        return False, current_updates, 'No stored database-update fingerprint.'

    unchanged = all(
        str(stored_updates.get(key, '')).strip() ==
        str(current_updates.get(key, '')).strip()
        for key in keys
    )
    if unchanged:
        return True, current_updates, 'All tracked DB table update times are unchanged.'
    return False, current_updates, 'Tracked DB table update times changed.'


def save_profile_db_table_updates(instrument: str,
                                  profile_name: str,
                                  updates: Dict[str, str]) -> None:
    """Persist per-profile table update fingerprints in apero_profiles.yaml."""
    from apero_ri.core.auth import load_apero_profiles, save_apero_profiles

    profiles = load_apero_profiles()
    if not isinstance(profiles, dict):
        profiles = {}

    instrument_key = str(instrument)
    if instrument_key not in profiles:
        for candidate in profiles:
            if str(candidate).lower() == instrument_key.lower():
                instrument_key = str(candidate)
                break
    if instrument_key not in profiles or not isinstance(profiles[instrument_key], dict):
        profiles[instrument_key] = {}

    profile_key = str(profile_name)
    if profile_key not in profiles[instrument_key]:
        for candidate in profiles[instrument_key]:
            if str(candidate).lower() == profile_key.lower():
                profile_key = str(candidate)
                break
    if profile_key not in profiles[instrument_key] or not isinstance(profiles[instrument_key][profile_key], dict):
        profiles[instrument_key][profile_key] = {}

    profiles[instrument_key][profile_key]['database-update'] = dict(updates)
    save_apero_profiles(profiles)


def save_results(filename: Path, results: Any, 
                 metadata: Optional[Dict[str, Any]] = None):
    """
    Save results to a file. This can be used to store results of a task for 
    later retrieval by the UI.

    :param filename: The path to the file where results should be saved.
    :param results: The results data to save (e.g. list of dicts, or any 
                    serializable data).
    :param metadata: Optional dictionary of metadata to save alongside the results.
    """
    def _json_default(value: Any):
        """Fallback serializer for common non-JSON-native values."""
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, (datetime, )):
            return value.isoformat()
        return str(value)

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'row_count': len(results) if isinstance(results, list) else None,
        'schema_version': 1,
        'metadata': metadata or {},
        'rows': results,
    }
    
    with path.open('w', encoding='utf-8') as fobj:
        json.dump(payload, fobj, ensure_ascii=False, indent=2,
                  default=_json_default)