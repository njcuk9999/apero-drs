#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: APERO check task.

This task builds per-obsdir APERO-check YAML files for the monitor portal.
"""

import copy
import multiprocessing as mp
import os
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from apero_ri.apero_monitoring import CHECKS
from apero_ri.apero_monitoring import core as checks_core
from apero_ri.apero_monitoring import raw_common
from apero_ri.application import profile_utils
from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.apero_check_task'

# List of parameters needed for this task.
PARAM_LIST = []
PARAM_LIST.append('LOCAL_DATA_DIR')
PARAM_LIST.append('INSTRUMENT')
PARAM_LIST.append('APERO_PROFILES')
PARAM_LIST.append('APERO_PROFILE_NAMES')

# Profile parameters are hydrated from APERO profiles.
APERO_PROFILE_PARAM_LIST = []

# Run hourly by default.
DEFAULT_FREQUENCY = 1.0

# Enable the task by default.
DEFAULT_ENABLED = True

# This task runs per instrument profile.
TASK_TYPE = 'INSTRUMENT'

# The UI should expose subprocess progress for this task.
USE_SUBPROCESS = True

# The task can process obsdirs in parallel.
MULTI_PROCESS = True

# The task can also be called through apero_sync.
LOCAL_TASK = True

# Expose simple include and exclude filters for focused runs.
FILTERS = []
FILTERS.append('APERO_PROFILE_INCLUDE')
FILTERS.append('APERO_PROFILE_EXCLUDE')
FILTERS.append('OBS_DIR_INCLUDE')
FILTERS.append('OBS_DIR_EXCLUDE')

# Re-run recent nights by default for 48 hours.
DEFAULT_RECENT_HOURS = 48.0


# =============================================================================
# Define classes
# =============================================================================
class AperoCheckTask(apero_async.AperoAsyncTask):
    """Run APERO checks and write monitor-portal YAML files."""

    def __init__(self, status='pending'):
        # Set the task name shown in the UI.
        name = 'APERO Check Task'
        # Set the task description shown in the UI.
        description = (
            'Run APERO checks on raw obsdirs and write YAML files '
            'for the monitor portal.'
        )
        # Initialise the shared async-task base class.
        super().__init__(name, description, status)
        # Advertise subprocess support on the instance as well.
        self.USE_SUBPROCESS = True

    def run_job(self, params: Dict[str, Any]) -> List[dict]:
        """Run APERO checks for every selected APERO profile."""
        # Delegate the main workflow to the module helper.
        return run_checks(self, params)


# =============================================================================
# Define functions
# =============================================================================
def run_checks(task: AperoCheckTask, params: Dict[str, Any]) -> List[dict]:
    """Run APERO checks for every selected APERO profile."""
    # Reset the task info before starting a new run.
    task.info = ''
    # Build the reusable run context.
    ctx = _init_run_context(params)
    # Log the task start for local and scheduled runs.
    ctx['tlog']('APERO_CHECK_TASK start.')
    # Write the active profile-filter note if one exists.
    if ctx['profile_filter_note']:
        task.info += ctx['profile_filter_note'] + '\n'
        ctx['tlog'](ctx['profile_filter_note'])
    # Stop early when no APERO profiles are configured.
    if not ctx['profile_names']:
        task.info = 'No APERO profiles configured.'
        ctx['tlog']('No APERO profiles configured. Nothing to do.')
        return []
    # Process one profile at a time.
    run_results = []
    for profile_index, profile_name in enumerate(ctx['profile_names']):
        # Honour a cancellation request before starting the next profile.
        if ctx['stop_event'] is not None and ctx['stop_event'].is_set():
            ctx['tlog']('Cancellation requested before next profile.')
            return run_results
        # Log which profile is being processed.
        ctx['tlog'](
            f'Profile {profile_index + 1}/{len(ctx["profile_names"])}: '
            f'{profile_name}'
        )
        # Run the profile workflow.
        run_results.append(_run_profile(task, ctx, profile_name))
    # Log task completion once all profiles are done.
    ctx['tlog']('APERO_CHECK_TASK completed.')
    return run_results


def manual_run(params: Dict[str, Any],
               verbose: bool = True,
               log_file: Optional[str] = None) -> Dict[str, Any]:
    """Run the APERO-check task manually for debugging and test creation."""
    from apero_ri.tasks import apero_sync

    run_params = dict(params or {})
    task_config = dict(run_params.get('TASK_CONFIG', {}) or {})

    if 'obs_dirs' in run_params and 'obs_dirs' not in task_config:
        task_config['obs_dirs'] = run_params.pop('obs_dirs')
    if 'checks' in run_params and 'checks' not in task_config:
        task_config['checks'] = run_params.pop('checks')
    if 'create' in run_params and 'create' not in task_config:
        task_config['create'] = run_params.pop('create')

    selected_checks = _normalize_manual_names(task_config.get('checks', []))
    unknown_checks = []
    for check_name in selected_checks:
        if check_name not in CHECKS:
            unknown_checks.append(check_name)
    if unknown_checks:
        names = ', '.join(unknown_checks)
        raise ValueError(f'Unknown APERO checks requested: {names}')

    run_params['TASK_CONFIG'] = task_config
    return apero_sync.run(
        'APERO_CHECK_TASK',
        run_params,
        verbose=verbose,
        log_file=log_file,
    )


def _init_run_context(params: Dict[str, Any]) -> dict:
    """Collect commonly used values into one run-context mapping."""
    # Read the task configuration block.
    task_config = params.get('TASK_CONFIG', {})
    # Normalise task filters to uppercase string keys.
    filters = apero_async.normalize_filter_map(task_config.get('filters', {}))
    # Start from all configured APERO profile names.
    all_profiles = list(params.get('APERO_PROFILE_NAMES', []))
    # Apply optional APERO profile filters.
    profile_names = apero_async.filter_profile_names(all_profiles, filters)
    # Build a short human-readable filter note.
    profile_filter_note = apero_async.profile_filter_note(
        all_profiles, profile_names, filters
    )
    # Build multiprocessing configuration with local defaults.
    mp_cfg = _normalize_mp_config(task_config)
    # Extract the optional task logger callback.
    task_logger = params.get('TASK_LOGGER')

    def tlog(message: str) -> None:
        """Write one task log line if a logger is available."""
        if callable(task_logger):
            try:
                task_logger(message)
            except Exception:
                pass

    # Return the shared context dictionary.
    return {
        'params': params,
        'profiles': params.get('APERO_PROFILES', {}),
        'profile_names': profile_names,
        'profile_filter_note': profile_filter_note,
        'filters': filters,
        'force_run': bool(task_config.get('force_run', False)),
        'recent_hours': float(
            task_config.get('recent_hours', DEFAULT_RECENT_HOURS)
        ),
        'mp_cfg': mp_cfg,
        'tlog': tlog,
        'stop_event': params.get('STOP_EVENT'),
        'manual_obs_dirs': _normalize_manual_names(
            task_config.get('obs_dirs', params.get('obs_dirs', []))
        ),
        'manual_checks': _normalize_manual_names(
            task_config.get('checks', params.get('checks', []))
        ),
        'create_output': _normalize_create_flag(
            task_config.get('create', params.get('create', True))
        ),
        'slow_check_seconds': float(
            task_config.get('slow_check_seconds', 5.0)
        ),
    }


def _run_profile(task: AperoCheckTask,
                 ctx: dict,
                 profile_name: str) -> dict:
    """Run the APERO-check workflow for one APERO profile."""
    # Get the profile configuration block.
    aparams = ctx['profiles'][profile_name]
    # Resolve the concrete instrument for this profile.
    instrument = _resolve_profile_instrument(aparams, ctx['params'])
    # Skip profiles whose configured data paths are not accessible.
    if not ctx['manual_obs_dirs']:
        missing_paths = apero_async.check_profile_paths_accessible(aparams)
        if missing_paths:
            detail = '; '.join(
                f'{key}={value}' for key, value in missing_paths
            )
            msg = (
                f'Profile {profile_name}: skipping - one or more required '
                f'data paths are not accessible: {detail}'
            )
            ctx['tlog'](msg)
            task.info += (
                f'\n## APERO Checks for APERO Profile: {profile_name}\n\n'
                f'- **Skipped** (path check failed): {msg}\n'
            )
            return dict(profile=profile_name, skipped=True)
    # Resolve the output directory used by the monitor portal.
    root_dir = checks_core.resolve_output_root(
        str(ctx['params'].get('LOCAL_DATA_DIR', '')),
        aparams,
    )
    ctx['tlog'](
        f'Profile {profile_name}: using instrument {instrument}.'
    )
    ctx['tlog'](
        f'Profile {profile_name}: YAML root is {root_dir} '
        f'(create_output={ctx["create_output"]}).'
    )
    # Build the ordered list of checks that apply to this instrument.
    check_keys = _valid_check_keys(instrument, ctx['manual_checks'])
    ctx['tlog'](
        f'Profile {profile_name}: resolved {len(check_keys)} check(s).'
    )
    # Stop early if no check is valid for this instrument.
    if not check_keys:
        msg = f'No checks are defined for instrument {instrument}.'
        ctx['tlog'](f'Profile {profile_name}: {msg}')
        task.info += (
            f'\n## APERO Checks for APERO Profile: {profile_name}\n\n'
            f'- {msg}\n'
        )
        return dict(profile=profile_name, skipped=False, obsdirs=[])
    # Query raw obsdirs and their first/last timestamps from FINDEX.
    if ctx['manual_obs_dirs']:
        ctx['tlog'](
            f'Profile {profile_name}: using '
            f'{len(ctx["manual_obs_dirs"])} manually requested obsdir(s).'
        )
        selected_rows = _manual_obsdir_rows(aparams, ctx['manual_obs_dirs'])
    else:
        ctx['tlog'](
            f'Profile {profile_name}: collecting obsdir candidates.'
        )
        obsdir_rows = _candidate_obsdir_rows(
            aparams,
            root_dir,
            ctx['tlog'],
        )
        ctx['tlog'](
            f'Profile {profile_name}: found {len(obsdir_rows)} candidate '
            'obsdir(s) before filtering.'
        )
        selected_rows = _select_obs_dirs(
            obsdir_rows,
            root_dir,
            ctx['filters'],
            ctx['recent_hours'],
            ctx['force_run'],
            check_keys,
        )
    ctx['tlog'](
        f'Profile {profile_name}: selected {len(selected_rows)} obsdir(s) '
        'for processing.'
    )
    # Short-circuit when nothing needs reprocessing.
    if not selected_rows:
        msg = 'No obsdirs selected for processing.'
        ctx['tlog'](f'Profile {profile_name}: {msg}')
        task.info += (
            f'\n## APERO Checks for APERO Profile: {profile_name}\n\n'
            f'- {msg}\n'
        )
        return dict(profile=profile_name, skipped=False, obsdirs=[])
    # Load database parameters once for all checks in this profile.
    ctx['tlog'](
        f'Profile {profile_name}: resolving database parameters.'
    )
    dbparams = _get_db_params_safe(aparams, ctx['tlog'])
    ctx['tlog'](
        f'Profile {profile_name}: database parameters resolved '
        f'({len(dbparams)} key(s)).'
    )
    # Prepare per-obsdir YAML payloads and dependency state.
    ctx['tlog'](
        f'Profile {profile_name}: preparing YAML payloads for '
        f'{len(selected_rows)} obsdir(s).'
    )
    payloads, states = _prepare_obsdir_maps(
        selected_rows,
        root_dir,
        instrument,
        profile_name,
    )
    ctx['tlog'](
        f'Profile {profile_name}: payload preparation complete.'
    )
    report_lines = []

    def _on_obsdir_result(obsdir_result: dict) -> None:
        """Apply one obsdir result and optionally write its YAML file."""
        obs_dir = str(obsdir_result.get('obs_dir', '') or '')
        if obs_dir == '':
            return
        states[obs_dir] = dict(obsdir_result.get('state', {}) or {})
        for check_result in obsdir_result.get('results', []):
            check_key = str(check_result.get('check_key', '') or '')
            dt = float(check_result.get('duration_s', 0.0) or 0.0)
            checks_core.add_check_entry(
                payloads[obs_dir]['payload'],
                check_result.get('entry'),
                payloads[obs_dir]['existing'],
            )
            if dt >= float(ctx['slow_check_seconds']):
                ctx['tlog'](
                    f'Profile {profile_name}: slow check night={obs_dir} '
                    f'check={check_key} time={dt:.2f}s.'
                )
            report_lines.append(
                f'{obs_dir} | {check_key} | {check_result["report"]}'
            )
        if ctx['create_output']:
            try:
                filename = checks_core.write_obsdir_yaml(
                    root_dir,
                    obs_dir,
                    payloads[obs_dir]['payload'],
                )
                ctx['tlog'](
                    f'Profile {profile_name}: wrote YAML {filename} '
                    f'(night={obs_dir}).'
                )
            except Exception as exc:
                ctx['tlog'](
                    f'Profile {profile_name}: failed writing YAML for '
                    f'{obs_dir}: {exc}'
                )

    # Run complete obsdir workflows so each worker can reuse FITS headers.
    total_checks = len(check_keys)
    total_obsdirs = len(selected_rows)
    obsdir_results = _run_obsdirs(
        check_keys,
        instrument,
        aparams,
        dbparams,
        selected_rows,
        states,
        ctx,
        task,
        result_hook=_on_obsdir_result,
    )
    # Honour cancellation requests while processing worker results.
    if ctx['stop_event'] is not None and ctx['stop_event'].is_set():
        ctx['tlog'](
            f'Profile {profile_name}: cancellation requested during '
            'obsdir workflows.'
        )
        return dict(profile=profile_name, skipped=True, cancelled=True)
    # Results were already applied incrementally in _on_obsdir_result.
    # Create one shared history entry for this profile run.
    if ctx['create_output']:
        history_entry = checks_core.build_history_entry()
        # Re-write every YAML once to append a shared run-history entry.
        for row in selected_rows:
            obs_dir = row['obs_dir']
            filename = checks_core.write_obsdir_yaml(
                root_dir,
                obs_dir,
                payloads[obs_dir]['payload'],
                history_entry=history_entry,
            )
            task.output_files.append(str(filename))
            ctx['tlog'](
                f'Profile {profile_name}: finalized YAML {filename}'
            )
    else:
        ctx['tlog'](
            f'Profile {profile_name}: create_output is disabled; '
            'no YAML files will be written.'
        )
        for line in report_lines:
            ctx['tlog'](f'Profile {profile_name}: {line}')
    # Update the markdown summary for the profile.
    task.info += (
        f'\n## APERO Checks for APERO Profile: {profile_name}\n\n'
        f'- Instrument: {instrument}\n'
        f'- Checks run: {total_checks}\n'
        f'- Obsdirs processed: {total_obsdirs}\n'
        f'- Create YAML: {ctx["create_output"]}\n'
    )
    if ctx['create_output']:
        task.info += f'- Output root: {root_dir}\n'
    elif report_lines:
        task.info += '- Reports:\n'
        for line in report_lines:
            task.info += f'  - {line}\n'
    # Update the task last-run timestamp.
    task.last_run = datetime.now(timezone.utc).isoformat()
    return dict(
        profile=profile_name,
        skipped=False,
        obsdirs=[row['obs_dir'] for row in selected_rows],
        reports=report_lines,
    )


def _query_raw_obs_dirs(aparams: dict,
                        tlog: Optional[Any] = None) -> List[dict]:
    """Query raw obsdirs and first or last timestamps from FINDEX."""
    # Quote the FINDEX table name safely for SQL.
    findex = profile_utils.q_ident(
        str(profile_utils.profile_get_db(aparams, 'FINDEX_TABLENAME', ''))
    )
    if callable(tlog):
        tlog(f'Querying raw obsdirs from FINDEX table {findex}.')
    # Build a grouped raw-obsdir query.
    query = f'''
    SELECT
        fdb.OBS_DIR AS OBS_DIR,
        MIN(NULLIF(fdb.KW_DATE_OBS, '')) AS FIRST_FILE,
        MAX(NULLIF(fdb.KW_DATE_OBS, '')) AS LAST_FILE,
        MIN(fdb.LAST_MODIFIED) AS FIRST_MODIFIED,
        MAX(fdb.LAST_MODIFIED) AS LAST_MODIFIED,
        COUNT(*) AS NFILES
    FROM {findex} AS fdb
    WHERE fdb.BLOCK_KIND = 'raw'
      AND fdb.OBS_DIR IS NOT NULL
      AND fdb.OBS_DIR != ''
    GROUP BY fdb.OBS_DIR
    ORDER BY fdb.OBS_DIR
    '''
    # Run the database query through the shared async helper.
    rows = apero_async.database_query(apero_async.get_db_params(aparams),
                                      query)
    # Normalise the result rows to the structure used later in the task.
    out = [_normalise_obsdir_row(row) for row in rows if isinstance(row, dict)]
    if callable(tlog):
        tlog(f'FINDEX query returned {len(out)} obsdir row(s).')
    return out


def _candidate_obsdir_rows(aparams: dict,
                           root_dir: Path,
                           tlog: Optional[Any] = None) -> List[dict]:
    """Return merged obsdir candidates from config, DB, disk, and YAML."""
    merged = dict()
    configured_rows = _configured_obsdir_rows(aparams)
    db_rows = _query_raw_obs_dirs(aparams, tlog)
    raw_rows = _raw_dir_obsdir_rows(aparams, tlog)
    yaml_rows = _existing_yaml_obsdir_rows(root_dir, tlog)
    row_groups = [configured_rows, db_rows, raw_rows, yaml_rows]

    if callable(tlog):
        tlog(
            'Candidate sources: '
            f'configured={len(configured_rows)}, '
            f'findex={len(db_rows)}, '
            f'raw_dir={len(raw_rows)}, '
            f'existing_yaml={len(yaml_rows)}.'
        )

    for rows in row_groups:
        for row in rows:
            obs_dir = str(row.get('obs_dir', '') or '').strip()
            if obs_dir == '':
                continue
            merged[obs_dir] = _merge_obsdir_rows(merged.get(obs_dir), row)

    out = [merged[name] for name in sorted(merged)]
    if callable(tlog):
        tlog(f'Merged candidate set contains {len(out)} obsdir(s).')
    return out


def _configured_obsdir_rows(aparams: dict) -> List[dict]:
    """Return configured obsdir candidates that may not exist yet."""
    raw_cfg = (
        aparams.get('apero-checks', {})
        if isinstance(aparams, dict)
        else {}
    )
    if not isinstance(raw_cfg, dict):
        return []
    raw_cfg = raw_cfg.get('raw', {})
    if not isinstance(raw_cfg, dict):
        return []

    obs_dirs = raw_cfg.get('expected_obs_dirs', [])
    if obs_dirs in [None, 'None', '']:
        obs_dirs = raw_cfg.get('obs_dirs', [])

    rows = []
    for obs_dir in _normalize_manual_names(obs_dirs):
        rows.append(_blank_obsdir_row(obs_dir))
    return rows


def _raw_dir_obsdir_rows(aparams: dict,
                         tlog: Optional[Any] = None) -> List[dict]:
    """Return obsdir candidates discovered directly from the raw dir."""
    raw_dir = _resolve_raw_dir(aparams)
    if raw_dir is None or not raw_dir.exists() or not raw_dir.is_dir():
        return []

    try:
        children = sorted(path for path in raw_dir.iterdir() if path.is_dir())
    except Exception as exc:
        if callable(tlog):
            tlog(f'Could not list raw obsdirs in {raw_dir}: {exc}')
        return []

    rows = [_obsdir_row_from_path(path) for path in children]
    if callable(tlog):
        tlog(f'Raw directory scan found {len(rows)} obsdir subdir(s).')
    return rows


def _existing_yaml_obsdir_rows(root_dir: Path,
                               tlog: Optional[Any] = None) -> List[dict]:
    """Return obsdir candidates already known through existing YAMLs."""
    rows = []
    if not root_dir.exists() or not root_dir.is_dir():
        if callable(tlog):
            tlog(f'Existing YAML scan skipped; root does not exist: {root_dir}')
        return rows

    yaml_paths = []
    for path in root_dir.rglob('*'):
        if not path.is_file():
            continue
        if str(path.suffix or '').lower() not in ['.yaml', '.yml']:
            continue
        yaml_paths.append(path)

    for path in sorted(yaml_paths):
        data = checks_core.load_yaml_file(path)
        row = _blank_obsdir_row(str(data.get('obsdir') or path.stem))
        row['first_file'] = str(data.get('first file', '') or '').strip()
        row['last_file'] = str(data.get('last file', '') or '').strip()
        try:
            row['nfiles'] = int(data.get('nfiles', 0) or 0)
        except Exception:
            row['nfiles'] = 0
        rows.append(row)
    if callable(tlog):
        tlog(f'Existing YAML scan found {len(rows)} YAML file(s).')
    return rows


def _merge_obsdir_rows(existing: Optional[dict], new: dict) -> dict:
    """Merge two obsdir-row payloads, keeping the best known metadata."""
    out = dict(existing or {})
    obs_dir = str(new.get('obs_dir', '') or out.get('obs_dir', '') or '')
    out['obs_dir'] = obs_dir.strip()

    first_file = str(new.get('first_file', '') or '').strip()
    if first_file:
        out['first_file'] = first_file
    else:
        out['first_file'] = str(out.get('first_file', '') or '').strip()

    last_file = str(new.get('last_file', '') or '').strip()
    if last_file:
        out['last_file'] = last_file
    else:
        out['last_file'] = str(out.get('last_file', '') or '').strip()

    try:
        current_nfiles = int(out.get('nfiles', 0) or 0)
    except Exception:
        current_nfiles = 0
    try:
        new_nfiles = int(new.get('nfiles', 0) or 0)
    except Exception:
        new_nfiles = 0
    out['nfiles'] = max(current_nfiles, new_nfiles)
    return out


def _normalise_obsdir_row(row: dict) -> dict:
    """Normalise one raw-obsdir SQL row."""
    # Extract the obsdir name from the SQL row.
    obs_dir = str(row.get('OBS_DIR', '') or '').strip()
    # Derive the first-file timestamp from DATE-OBS or LAST_MODIFIED.
    first_file = _row_time_value(
        row.get('FIRST_FILE'), row.get('FIRST_MODIFIED')
    )
    # Derive the last-file timestamp from DATE-OBS or LAST_MODIFIED.
    last_file = _row_time_value(
        row.get('LAST_FILE'), row.get('LAST_MODIFIED')
    )
    # Build the normalised row dictionary.
    out = dict()
    out['obs_dir'] = obs_dir
    out['first_file'] = first_file
    out['last_file'] = last_file
    out['nfiles'] = int(row.get('NFILES', 0) or 0)
    return out


def _row_time_value(date_value: Any, modified_value: Any) -> str:
    """Return the best time string for a grouped SQL row."""
    # Prefer the DATE-OBS value when it is present.
    if str(date_value or '').strip():
        return checks_core.format_time_string(date_value)
    # Fall back to LAST_MODIFIED when DATE-OBS is missing.
    return _from_unix_time(modified_value)


def _from_unix_time(value: Any) -> str:
    """Convert a unix timestamp to the YAML time format."""
    # Return an empty string for null-like values.
    if value in [None, 'None', '']:
        return ''
    try:
        # Convert the unix timestamp to a UTC datetime.
        dtime = datetime.fromtimestamp(float(value), tz=timezone.utc)
    except Exception:
        return ''
    # Store the timestamp without timezone text to match samples.
    return dtime.strftime(checks_core.TIME_FORMAT)


def _select_obs_dirs(rows: Sequence[dict],
                     root_dir: Path,
                     filters: Dict[str, str],
                     recent_hours: float,
                     force_run: bool,
                     required_checks: Sequence[str]) -> List[dict]:
    """Select obsdirs that should be processed in this task run."""
    # Normalise optional include and exclude filters.
    include_set = _parse_name_list(filters.get('OBS_DIR_INCLUDE', ''))
    exclude_set = _parse_name_list(filters.get('OBS_DIR_EXCLUDE', ''))
    # Prepare the selected-row storage.
    selected = []
    # Loop over every grouped obsdir row from the database.
    for row in rows:
        obs_dir = str(row.get('obs_dir', '') or '').strip()
        # Skip empty obsdir names.
        if obs_dir == '':
            continue
        # Apply explicit include and exclude filters.
        lname = obs_dir.lower()
        if include_set and lname not in include_set:
            continue
        if lname in exclude_set:
            continue
        # Keep pending obsdirs under active monitoring until files appear.
        if _row_needs_presence_recheck(row):
            selected.append(dict(row))
            continue
        # Force mode reprocesses every matching obsdir.
        if force_run:
            selected.append(dict(row))
            continue
        # Missing YAML files must always be processed.
        yaml_path = checks_core.make_obsdir_filename(root_dir, obs_dir)
        if not yaml_path.exists():
            selected.append(dict(row))
            continue
        # Reprocess recent nights based on the stored YAML timestamps.
        existing = checks_core.load_yaml_file(yaml_path)
        if _yaml_missing_checks(existing, required_checks):
            selected.append(dict(row))
            continue
        if _yaml_is_recent(existing, recent_hours):
            selected.append(dict(row))
            continue
    return selected


def _yaml_missing_checks(data: dict,
                         required_checks: Sequence[str]) -> bool:
    """Return True when an existing YAML payload is missing checks."""
    passes = data.get('passes', {}) if isinstance(data, dict) else {}
    failures = data.get('failures', {}) if isinstance(data, dict) else {}
    present = set()
    if isinstance(passes, dict):
        present |= {str(key) for key in passes}
    if isinstance(failures, dict):
        present |= {str(key) for key in failures}
    for check_key in required_checks:
        if str(check_key) not in present:
            return True
    return False


def _yaml_is_recent(data: dict, recent_hours: float) -> bool:
    """Return True when the stored first or last file is recent."""
    # Convert the hour threshold to a datetime delta.
    delta = timedelta(hours=float(recent_hours))
    # Work out the UTC cutoff time.
    cutoff = datetime.now(timezone.utc) - delta
    # Test both stored timestamps.
    for key in ('first file', 'last file'):
        dtime = _parse_time_string(data.get(key, ''))
        if dtime is not None and dtime >= cutoff:
            return True
    return False


def _valid_check_keys(instrument: str,
                      selected_checks: Optional[Sequence[str]] = None
                      ) -> List[str]:
    """Return the ordered check keys valid for the current instrument."""
    # Keep the order defined in apero_ri.apero_monitoring.__init__.
    ordered = []
    selected = {
        str(name).strip().upper()
        for name in list(selected_checks or [])
        if str(name).strip()
    }
    for check_key, check_template in CHECKS.items():
        if instrument in list(getattr(check_template, 'instruments', [])):
            if selected and str(check_key).upper() not in selected:
                continue
            ordered.append(str(check_key))
    return ordered


def _resolve_profile_instrument(aparams: dict,
                                params: Optional[dict] = None) -> str:
    """Return the concrete instrument name for one APERO profile."""
    params = params or dict()
    candidates = [
        profile_utils.profile_get_general(aparams, 'instrument', ''),
        profile_utils.profile_get_general(aparams, 'INSTRUMENT', ''),
        params.get('INSTRUMENT', ''),
    ]
    for candidate in candidates:
        name = str(candidate or '').strip()
        if name:
            return name
    return 'unknown'


def _prepare_obsdir_maps(rows: Sequence[dict],
                         root_dir: Path,
                         instrument: str,
                         profile_name: str) -> Tuple[dict, dict]:
    """Prepare YAML payload and dependency-state maps for all obsdirs."""
    # Prepare the payload storage keyed by obsdir.
    payloads = dict()
    # Prepare the dependency-state storage keyed by obsdir.
    states = dict()
    # Loop over every selected obsdir row.
    for row in rows:
        obs_dir = row['obs_dir']
        # Load the existing YAML file so history can be preserved.
        filename = checks_core.make_obsdir_filename(root_dir, obs_dir)
        existing = checks_core.load_yaml_file(filename)
        # Build the fresh payload skeleton for this obsdir.
        payload = checks_core.build_obsdir_payload(
            obs_dir,
            instrument,
            profile_name,
            row.get('first_file', ''),
            row.get('last_file', ''),
            existing_data=existing,
        )
        # Store the payload and existing-data pair.
        payloads[obs_dir] = dict(payload=payload, existing=existing)
        # Initialise the dependency state for this obsdir.
        states[obs_dir] = dict()
    return payloads, states


def _run_obsdirs(check_keys: Sequence[str],
                 instrument: str,
                 aparams: dict,
                 dbparams: dict,
                 rows: Sequence[dict],
                 states: dict,
                 ctx: dict,
                 task: AperoCheckTask,
                 result_hook: Optional[Any] = None) -> List[dict]:
    """Run complete check workflows for each obsdir."""
    # Resolve whether obsdir workers should be run in parallel.
    total = len(rows)
    ncores = int(ctx['mp_cfg']['ncores'])
    backend = str(ctx['mp_cfg']['backend'])
    use_parallel = (
        MULTI_PROCESS
        and ncores > 1
        and total > 1
    )
    if use_parallel:
        ctx['tlog'](
            f'Obsdir execution mode: parallel backend={backend} '
            f'ncores={ncores} jobs={total}.'
        )
    else:
        ctx['tlog'](
            f'Obsdir execution mode: serial backend={backend} '
            f'ncores={ncores} jobs={total}.'
        )
    # Use the serial path when multiprocessing is disabled.
    if not use_parallel:
        return _run_obsdirs_serial(
            check_keys,
            instrument,
            aparams,
            dbparams,
            rows,
            states,
            ctx,
            task,
            result_hook=result_hook,
        )
    # Otherwise run obsdir workflows in the configured executor.
    return _run_obsdirs_parallel(
        check_keys,
        instrument,
        aparams,
        dbparams,
        rows,
        states,
        ctx,
        task,
        result_hook=result_hook,
    )


def _run_obsdirs_serial(check_keys: Sequence[str],
                        instrument: str,
                        aparams: dict,
                        dbparams: dict,
                        rows: Sequence[dict],
                        states: dict,
                        ctx: dict,
                        task: AperoCheckTask,
                        result_hook: Optional[Any] = None) -> List[dict]:
    """Run complete check workflows serially across all obsdirs."""
    # Prepare the ordered results list.
    results = []
    total = len(rows)
    _update_night_progress(task, ctx, 0, total)
    # Loop over obsdirs in input order.
    for index, row in enumerate(rows):
        # Honour cancellation requests between obsdirs.
        if ctx['stop_event'] is not None and ctx['stop_event'].is_set():
            ctx['tlog']('Cancellation requested during serial obsdir loop.')
            break
        job_no = index + 1
        obs_dir = str(row.get('obs_dir', '') or '')
        ctx['tlog'](
            f'Profile serial job {job_no}/{total}: night={obs_dir} '
            'starting on main process.'
        )
        # Run all checks for the current obsdir in one worker call.
        result = _run_single_obsdir_all_checks(
            check_keys,
            instrument,
            aparams,
            dbparams,
            dict(row),
            dict(states[row['obs_dir']]),
        )
        # Append the completed result.
        results.append(result)
        if callable(result_hook):
            result_hook(result)
        ctx['tlog'](
            f'Profile serial job {job_no}/{total}: night={obs_dir} '
            f'completed on worker {result.get("worker", "unknown")}.'
        )
        _update_night_progress(task, ctx, index + 1, total)
    return results


def _run_obsdirs_parallel(check_keys: Sequence[str],
                          instrument: str,
                          aparams: dict,
                          dbparams: dict,
                          rows: Sequence[dict],
                          states: dict,
                          ctx: dict,
                          task: AperoCheckTask,
                          result_hook: Optional[Any] = None) -> List[dict]:
    """Run complete check workflows in parallel across all obsdirs."""
    # Create the configured executor instance.
    executor = _make_executor(
        ctx['mp_cfg']['backend'],
        ctx['mp_cfg']['ncores'],
        ctx['mp_cfg']['start_method'],
        ctx['tlog'],
    )
    # Prepare the result storage.
    results = []
    total = len(rows)
    ncores = int(ctx['mp_cfg']['ncores'])
    workers_seen = set()
    _update_night_progress(task, ctx, 0, total)
    # Submit all obsdir jobs to the executor.
    with executor as pool:
        futures = dict()
        for index, row in enumerate(rows):
            job_no = index + 1
            obs_dir = str(row.get('obs_dir', '') or '')
            ctx['tlog'](
                f'Profile parallel job {job_no}/{total}: night={obs_dir} '
                'queued for worker pool.'
            )
            future = pool.submit(
                _run_single_obsdir_all_checks,
                list(check_keys),
                instrument,
                aparams,
                dbparams,
                dict(row),
                dict(states[row['obs_dir']]),
            )
            futures[future] = dict(job_no=job_no, obs_dir=obs_dir)
        # Collect results as workers complete.
        for index, future in enumerate(as_completed(futures)):
            # Honour cancellation requests while waiting for results.
            if ctx['stop_event'] is not None and ctx['stop_event'].is_set():
                for other in futures:
                    other.cancel()
                ctx['tlog'](
                    'Cancellation requested during parallel obsdir loop.'
                )
                break
            # Collect the worker result.
            result = future.result()
            results.append(result)
            if callable(result_hook):
                result_hook(result)
            job_info = futures.get(future, {})
            job_no = int(job_info.get('job_no', index + 1) or (index + 1))
            obs_dir = str(
                job_info.get('obs_dir', result.get('obs_dir', '')) or ''
            )
            worker = str(result.get('worker', 'unknown'))
            workers_seen.add(worker)
            ctx['tlog'](
                f'Profile parallel job {job_no}/{total}: night={obs_dir} '
                f'completed on worker {worker}.'
            )
            ctx['tlog'](
                f'Parallel workers seen: {len(workers_seen)}/{ncores} '
                f'(latest={worker}).'
            )
            _update_night_progress(task, ctx, index + 1, total)
    # Keep the final result order stable by obsdir name.
    results.sort(key=lambda item: item['obs_dir'])
    return results


def _update_night_progress(task: AperoCheckTask,
                           ctx: dict,
                           completed: int,
                           total: int) -> None:
    """Update progress from completed nights and emit one log line."""
    done = max(0, int(completed))
    all_nights = max(1, int(total))
    frac = float(min(done, all_nights)) / float(all_nights)
    task.progress = frac
    task.subprogress = frac
    percent = 100.0 * frac
    ctx['tlog'](
        f'Nights progress: {done}/{int(total)} completed '
        f'({percent:.1f}%).'
    )


def _run_single_obsdir_all_checks(check_keys: Sequence[str],
                                  instrument: str,
                                  aparams: dict,
                                  dbparams: dict,
                                  row: dict,
                                  state: dict) -> dict:
    """Run all checks for one obsdir and return YAML-ready results."""
    # Resolve the obsdir once and initialise the shared state mapping.
    obsdir = str(row.get('obs_dir', '') or '')
    current_state = dict(state)
    # Prepare the per-check result storage.
    out_results = []
    # Scope the FITS-header cache to this obsdir workflow only.
    raw_common.activate_obsdir_header_cache(obsdir)
    try:
        # Run all checks in order so dependency state stays deterministic.
        for check_key in check_keys:
            result = _run_single_obsdir_check(
                str(check_key),
                instrument,
                aparams,
                dbparams,
                row,
                current_state,
            )
            current_state[str(check_key)] = bool(result['passed'])
            out_results.append(result)
    finally:
        # Drop the obsdir-local header cache before leaving the worker.
        raw_common.clear_obsdir_header_cache()
    # Return the full obsdir result payload to the parent process.
    out = dict()
    out['obs_dir'] = obsdir
    out['worker'] = f'pid={os.getpid()}'
    out['state'] = current_state
    out['results'] = out_results
    return out


def _run_single_obsdir_check(check_key: str,
                             instrument: str,
                             aparams: dict,
                             dbparams: dict,
                             row: dict,
                             state: dict) -> dict:
    """Run one check for one obsdir and return a YAML-ready result."""
    # Clone the template so runtime state is isolated per worker.
    check_obj = copy.deepcopy(CHECKS[check_key])
    # Build the input mapping passed to the check callable.
    check_dict = dict(state)
    check_dict['obsdir'] = row.get('obs_dir', '')
    check_dict['obsdir_first_file'] = row.get('first_file', '')
    check_dict['obsdir_last_file'] = row.get('last_file', '')
    start = time.perf_counter()
    try:
        # Run the check with the requested signature.
        check_obj(
            instrument,
            str(row.get('obs_dir', '') or ''),
            aparams,
            dbparams,
            check_dict,
        )
    except Exception as exc:
        # Convert crashes into failing checks with an explicit message.
        check_obj.passed = False
        check_obj.message = f'Check crashed: {exc}'
    # Build the result mapping consumed by the parent process.
    result = dict()
    result['obs_dir'] = str(row.get('obs_dir', '') or '')
    result['check_key'] = str(check_key)
    result['passed'] = bool(check_obj.passed)
    result['entry'] = check_obj.create_yaml_entry()
    result['report'] = str(check_obj.report())
    result['duration_s'] = time.perf_counter() - start
    return result


def _get_db_params_safe(aparams: dict, tlog) -> dict:
    """Resolve DB params and fall back to an empty mapping on failure."""
    try:
        return apero_async.get_db_params(aparams)
    except Exception as exc:
        if callable(tlog):
            tlog(f'Could not resolve database params: {exc}')
        return dict()


def _manual_obsdir_rows(aparams: dict,
                        obs_dirs: Sequence[str]) -> List[dict]:
    """Build synthetic row metadata for manually selected obsdirs."""
    rows = []
    raw_dir = _resolve_raw_dir(aparams)
    for obs_dir in obs_dirs:
        row = _blank_obsdir_row(obs_dir)
        if raw_dir is None:
            rows.append(row)
            continue
        rows.append(_obsdir_row_from_path(raw_dir / str(obs_dir)))
    return rows


def _blank_obsdir_row(obs_dir: str) -> dict:
    """Return an empty row payload for one obsdir name."""
    row = dict()
    row['obs_dir'] = str(obs_dir or '').strip()
    row['first_file'] = ''
    row['last_file'] = ''
    row['nfiles'] = 0
    return row


def _obsdir_row_from_path(obs_path: Path) -> dict:
    """Build one obsdir-row payload from a raw-directory path."""
    row = _blank_obsdir_row(obs_path.name)
    files = sorted(obs_path.glob('*.fits'))
    row['nfiles'] = len(files)
    if files:
        row['first_file'] = _format_stat_time(files[0])
        row['last_file'] = _format_stat_time(files[-1])
    return row


def _resolve_raw_dir(aparams: dict) -> Optional[Path]:
    """Resolve the raw-data directory from one APERO profile mapping."""
    for key in ('PATH.RAW', 'PATH_RAW', 'raw'):
        value = profile_utils.profile_get_path(aparams, key, '')
        if str(value or '').strip():
            return Path(str(value)).expanduser()
    return None


def _format_stat_time(filename: Path) -> str:
    """Format one file modification time for synthetic manual rows."""
    try:
        dtime = datetime.fromtimestamp(
            filename.stat().st_mtime,
            tz=timezone.utc,
        )
    except Exception:
        return ''
    return dtime.strftime(checks_core.TIME_FORMAT)


def _row_needs_presence_recheck(row: dict) -> bool:
    """Return True when an obsdir still has no known raw files."""
    try:
        nfiles = int(row.get('nfiles', 0) or 0)
    except Exception:
        nfiles = 0
    first_file = str(row.get('first_file', '') or '').strip()
    last_file = str(row.get('last_file', '') or '').strip()
    return nfiles == 0 and first_file == '' and last_file == ''


def _normalize_manual_names(raw_value: Any) -> List[str]:
    """Normalise a scalar or list input into a list of names."""
    if raw_value in [None, 'None', '']:
        return []
    if isinstance(raw_value, (list, tuple, set)):
        items = list(raw_value)
    else:
        text = str(raw_value).replace(';', ',').replace('\n', ',')
        items = text.split(',')
    return [
        str(item).strip()
        for item in items
        if str(item).strip()
    ]


def _normalize_create_flag(value: Any) -> bool:
    """Normalise the create flag used by manual and scheduled runs."""
    if isinstance(value, bool):
        return value
    return str(value or 'true').strip().lower() in ['1', 'true', 'yes']


def _normalize_mp_config(task_config: dict) -> dict:
    """Normalise multiprocessing options for this task."""
    # Start with the default backend.
    backend = str(task_config.get('mp_backend', 'processes') or 'processes')
    # Clamp unsupported values to the process backend.
    if backend not in ['processes', 'threads']:
        backend = 'processes'
    # Start with the requested core count.
    if 'ncores' in task_config:
        ncores = int(task_config.get('ncores', 1) or 1)
    else:
        auto_cores = int(os.cpu_count() or 1)
        ncores = max(1, min(8, auto_cores))
    # Clamp the number of workers to at least one.
    ncores = max(1, ncores)
    # Use the default multiprocessing start method unless overridden.
    start_method = str(
        task_config.get('mp_start_method', 'default') or 'default'
    )
    return dict(backend=backend, ncores=ncores,
                start_method=start_method)


def _make_executor(backend: str,
                   ncores: int,
                   start_method: str,
                   tlog) -> Any:
    """Create the executor used for per-obsdir parallelism."""
    # Use threads when explicitly requested.
    if backend == 'threads':
        return ThreadPoolExecutor(max_workers=int(ncores))
    # Resolve an optional multiprocessing context.
    mp_context = None
    if start_method not in ['', 'default', 'None', None]:
        try:
            mp_context = mp.get_context(str(start_method))
        except Exception as exc:
            if callable(tlog):
                tlog(
                    f'Invalid mp_start_method={start_method!r}; '
                    f'falling back to default: {exc}'
                )
            mp_context = None
    # Create a process-pool executor with the resolved context.
    if mp_context is None:
        return ProcessPoolExecutor(max_workers=int(ncores))
    return ProcessPoolExecutor(max_workers=int(ncores),
                               mp_context=mp_context)


def _parse_name_list(raw_value: Any) -> set:
    """Parse a comma or semicolon separated include or exclude list."""
    # Normalise the raw input text.
    text = str(raw_value or '').strip()
    # Return an empty set when no value is supplied.
    if text == '':
        return set()
    # Split on commas, semicolons, and newlines.
    norm = text.replace(';', ',').replace('\n', ',')
    # Lower-case the values so matching is case-insensitive.
    return {
        part.strip().lower()
        for part in norm.split(',')
        if str(part).strip()
    }


def _parse_time_string(value: Any) -> Optional[datetime]:
    """Parse a stored YAML time string into a UTC datetime."""
    # Return None for null-like values.
    if value in [None, 'None', '']:
        return None
    # Normalise the input to a string.
    text = str(value).strip()
    # Try the shared APERO-check parser first.
    for parser in (_parse_iso_like_time, _parse_plain_time):
        dtime = parser(text)
        if dtime is not None:
            return dtime
    return None


def _parse_iso_like_time(text: str) -> Optional[datetime]:
    """Parse an ISO-like time string and return a UTC datetime."""
    value = text.replace('Z', '+00:00')
    try:
        dtime = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dtime.tzinfo is None:
        return dtime.replace(tzinfo=timezone.utc)
    return dtime.astimezone(timezone.utc)


def _parse_plain_time(text: str) -> Optional[datetime]:
    """Parse a plain APERO-check time string and return UTC."""
    try:
        dtime = datetime.strptime(text, checks_core.TIME_FORMAT)
    except ValueError:
        return None
    return dtime.replace(tzinfo=timezone.utc)


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    import yaml

    example_path = (
        Path(__file__).resolve().parents[1]
        / 'resources'
        / 'aprofile_instruments'
        / 'nirps_ha_v7.yaml'
    )
    with open(example_path, 'r', encoding='utf-8') as handle:
        example_profile = yaml.safe_load(handle) or dict()
    example_profile['paths'] = dict(raw='.')

    example_params = dict(
        LOCAL_DATA_DIR=str(Path.home() / '.ari'),
        INSTRUMENT='NIRPS_HA',
        APERO_PROFILES=dict(nirps_ha_example=example_profile),
        APERO_PROFILE_NAMES=['nirps_ha_example'],
        obs_dirs=['2021-01-01'],
        checks=['HAS_OBSDIR'],
        create=False,
    )
    manual_run(example_params)


# =============================================================================
# End of code
# =============================================================================
