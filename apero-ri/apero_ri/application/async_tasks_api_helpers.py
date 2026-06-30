"""Async task API helper functions for ARIApp."""

import json
import os
import traceback
from pathlib import Path

from apero_ri.core import task_runner
from apero_ri.core.auth import (
    load_apero_profiles,
    load_async_tasks,
    save_async_tasks,
)
from apero_ri.application import async_task_helpers
from flask import jsonify, request


def _coerce_bool(value):
    """Coerce common JSON/UI values to bool."""
    if isinstance(value, bool):
        return value
    text = str(value or '').strip().lower()
    return text in ['1', 'true', 'yes', 'on', 'y']


def _normalize_instrument_key(value):
    """Normalize instrument key for map-based task config lookups."""
    text = str(value or '').strip().upper()
    return text.replace('-', '_')


def _instrument_profile_names(instrument):
    """Return ordered APERO profile names for one instrument."""
    profiles = load_apero_profiles(enabled_only=True).get(instrument, {})
    if not isinstance(profiles, dict):
        return []
    return list(profiles.keys())


def _validate_sync_profiles(raw, instrument):
    """Validate and normalize per-profile sync settings from the client."""
    if not isinstance(raw, dict):
        raise ValueError("sync_profiles must be an object")

    allowed = set(_instrument_profile_names(instrument))
    cleaned = {}
    for profile_name, entry in raw.items():
        pname = str(profile_name or "").strip()
        if not pname:
            continue
        if pname not in allowed:
            raise ValueError(f"Unknown APERO profile: {pname}")
        if not isinstance(entry, dict):
            raise ValueError(
                f"sync_profiles.{pname} must be an object"
            )

        mode = str(entry.get("mode", "run_server") or "run_server")
        mode = mode.strip().lower()
        if mode not in ["run_server", "fetch_precomputed"]:
            raise ValueError(
                f"Invalid sync mode for profile {pname}"
            )
        sync_source = str(entry.get("sync_source", "") or "").strip()
        if mode == "fetch_precomputed" and not sync_source:
            raise ValueError(
                "Fetch pre-computed requires a directory for "
                f"profile {pname}"
            )
        if mode == "run_server" and not sync_source:
            continue
        # Validate that the sync_source actually points at a profile
        # directory containing an ``objects/`` subdir. Without this
        # check the runtime resolver silently falls back to copying
        # the whole tree at deep nested relative paths, leaving the
        # local ftable JSONs stale forever (the file browser would
        # then keep serving outdated rows).
        if mode == "fetch_precomputed":
            _validate_sync_source_path(pname, sync_source)
        cleaned[pname] = dict(mode=mode, sync_source=sync_source)
    return cleaned


def _validate_sync_source_path(pname, sync_source):
    """Ensure sync_source resolves to a dir that contains ``objects/``.

    Mirrors the candidate resolution used at run time by
    ``task_runner._resolve_sync_profile_source_dir`` but adds a hard
    requirement: the resolved profile directory must contain an
    ``objects/`` subdirectory. This refuses to save a misconfigured
    path (the symptom is silent — sync runs, copies thousands of
    files into the wrong nested destination, ftables never update).
    """
    # Expand and resolve user input
    src = Path(sync_source).expanduser()
    if not src.is_dir():
        raise ValueError(
            f"sync_source for profile {pname} is not an existing "
            f"directory on the server: {sync_source}"
        )
    # Candidate profile directories under the source. If any of these
    # contains ``objects/`` we accept it; otherwise we reject.
    candidates = [src]
    try:
        for child in src.iterdir():
            if child.is_dir():
                candidates.append(child)
                # one level deeper too (e.g. ``tasks/<instr>/<profile>``)
                try:
                    for grand in child.iterdir():
                        if grand.is_dir():
                            candidates.append(grand)
                except OSError:
                    continue
    except OSError as exc:
        raise ValueError(
            f"sync_source for profile {pname} is not readable: {exc}"
        )
    for candidate in candidates:
        if (candidate / "objects").is_dir():
            return
    raise ValueError(
        f"sync_source for profile {pname} does not contain an "
        "'objects/' subdirectory (looked in the path itself and "
        "one or two levels below). Point it at the exact profile "
        f"directory on the source server. Given: {sync_source}"
    )


LEGACY_GSHEET_TASK_KEYS = [
    'LEGACY_ASTROM_GSHEET',
    'LEGACY_REJECT_GSHEET',
    'LEGACY_CHECK_GSHEET',
]
DEFAULT_GOOGLE_SECRET_NAME = 'legacy_gsheet_oauth.json'
REQUIRED_GOOGLE_OAUTH_KEYS = [
    'client_id',
    'client_secret',
    'refresh_token',
]


def _validate_google_secret_name(value):
    """Validate oauth filename to prevent path traversal."""
    secret_name = str(value or '').strip() or DEFAULT_GOOGLE_SECRET_NAME
    if secret_name != Path(secret_name).name:
        raise ValueError('google_secret_name must be a plain filename')
    if '/' in secret_name or '\\' in secret_name:
        raise ValueError('google_secret_name cannot contain path separators')
    if not secret_name.lower().endswith('.json'):
        raise ValueError('google_secret_name must end with .json')
    return secret_name


def _normalize_google_oauth_payload(raw_payload):
    """Validate oauth payload shape and fill defaults."""
    payload = raw_payload
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception as exc:
            raise ValueError('google_oauth_upload must be valid JSON') from exc
    if not isinstance(payload, dict):
        raise ValueError('google_oauth_upload must be a JSON object')

    native_client = payload.get('installed') or payload.get('web')
    if isinstance(native_client, dict):
        for key in ['client_id', 'client_secret', 'token_uri']:
            current = str(payload.get(key) or '').strip()
            native_value = str(native_client.get(key) or '').strip()
            if not current and native_value:
                payload[key] = native_value

    refresh_token = str(payload.get('refresh_token') or '').strip()
    if not refresh_token:
        raise ValueError(
            'google_oauth_upload missing refresh_token. '
            'Run the one-time OAuth auth flow and upload JSON '
            'with client_id, client_secret, refresh_token, '
            'and token_uri.'
        )
    payload['refresh_token'] = refresh_token

    for key in REQUIRED_GOOGLE_OAUTH_KEYS:
        value = str(payload.get(key) or '').strip()
        if not value:
            raise ValueError(f'google_oauth_upload missing {key}')
        payload[key] = value

    token_uri = str(payload.get('token_uri') or '').strip()
    if not token_uri:
        token_uri = 'https://oauth2.googleapis.com/token'
    payload['token_uri'] = token_uri

    scopes = payload.get('scopes')
    if not isinstance(scopes, list) or len(scopes) == 0:
        payload['scopes'] = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
        ]
    return payload


def _legacy_admin_secret_path(app, secret_name):
    """Return LOCAL_DATA_DIR/admin/<secret_name>."""
    local_data_dir = Path(app._resolve_local_data_dir())
    admin_dir = local_data_dir / 'admin'
    return admin_dir / secret_name


def api_async_tasks_save(app):
    """Update an async task configuration from the fixed task catalog."""
    user_info, perms = app._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    task_key = data.get("task_key", "").strip()
    frequency = float(data.get("frequency", 24))
    task_id = str(data.get("id", "")).strip()
    active = _coerce_bool(data.get("active", True))
    daily_copies = int(data.get("daily_copies", 0) or 0)
    weekly_copies = int(data.get("weekly_copies", 0) or 0)
    has_backup_max_size_mb = "backup_max_size_mb" in data
    backup_max_size_mb = None
    has_ncores = "ncores" in data
    has_mp_backend = "mp_backend" in data
    has_mp_start_method = "mp_start_method" in data or "mp_start_methd" in data
    has_sync_source = "sync_source" in data
    has_sync_profiles = "sync_profiles" in data
    has_assets_mode = "assets_mode" in data
    has_dry_run = "dry_run" in data or "DRY_RUN" in data
    has_google_secret_name = "google_secret_name" in data
    has_google_oauth_upload = "google_oauth_upload" in data

    ncores = None
    mp_backend = None
    mp_start_method = None
    sync_source = None
    sync_profiles = None
    assets_mode = None
    dry_run = False
    google_secret_name = None
    google_oauth_upload = None

    if not instrument or not task_id:
        return jsonify(success=False, error="Missing fields"), 400
    if frequency <= 0:
        return jsonify(success=False, error="Frequency must be > 0"), 400
    if daily_copies < 0 or weekly_copies < 0:
        return (
            jsonify(
                success=False, error="Backup copy counts must be non-negative"
            ),
            400,
        )
    if has_backup_max_size_mb:
        try:
            backup_max_size_mb = float(data.get("backup_max_size_mb"))
        except (TypeError, ValueError):
            return (
                jsonify(
                    success=False,
                    error="backup_max_size_mb must be a number",
                ),
                400,
            )
        if backup_max_size_mb <= 0:
            return (
                jsonify(
                    success=False,
                    error="backup_max_size_mb must be > 0",
                ),
                400,
            )
    if has_ncores:
        try:
            ncores = int(data.get("ncores"))
        except (TypeError, ValueError):
            return (
                jsonify(success=False, error="NCORES must be an integer"),
                400,
            )
        if ncores <= 0:
            return jsonify(success=False, error="NCORES must be >= 1"), 400

    if has_mp_backend:
        mp_backend = str(data.get("mp_backend", "") or "").strip().lower()
        if mp_backend not in ["threads", "processes"]:
            return (
                jsonify(
                    success=False,
                    error="mp_backend must be threads or processes",
                ),
                400,
            )

    if has_mp_start_method:
        mp_start_method_raw = data.get(
            "mp_start_method", data.get("mp_start_methd", "")
        )
        mp_start_method = str(mp_start_method_raw or "").strip().lower()
        if mp_start_method not in ["default", "spawn", "fork", "forkserver"]:
            return jsonify(success=False, error="Invalid mp_start_method"), 400

    if has_sync_source:
        sync_source = str(data.get("sync_source", "") or "").strip()

    if has_sync_profiles:
        try:
            sync_profiles = _validate_sync_profiles(
                data.get("sync_profiles", {}),
                instrument,
            )
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400

    if has_assets_mode:
        assets_mode_raw = (
            str(data.get("assets_mode") or "remote").strip().lower()
        )
        # backwards compatibility: accept legacy values
        if assets_mode_raw in ("sync", "upload", "remote"):
            assets_mode_raw = "remote"
        elif assets_mode_raw == "local":
            assets_mode_raw = "local"
        else:
            assets_mode_raw = "remote"
        assets_mode = assets_mode_raw
    if has_dry_run:
        dry_run_raw = data.get("dry_run", data.get("DRY_RUN", False))
        dry_run = _coerce_bool(dry_run_raw)
    if has_google_secret_name:
        try:
            google_secret_name = _validate_google_secret_name(
                data.get("google_secret_name", DEFAULT_GOOGLE_SECRET_NAME)
            )
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400
    if has_google_oauth_upload:
        try:
            google_oauth_upload = _normalize_google_oauth_payload(
                data.get("google_oauth_upload")
            )
        except ValueError as exc:
            return jsonify(success=False, error=str(exc)), 400
    has_assets_local_source = "assets_local_source_path" in data
    assets_local_source = None
    if has_assets_local_source:
        assets_local_source = str(
            data.get("assets_local_source_path") or ""
        ).strip()

    all_tasks = load_async_tasks()
    inst_tasks, _ = app._merge_async_task_catalog(instrument, all_tasks)
    from apero_ri import tasks as task_module

    max_cores = max(int(os.cpu_count() or 1), 1)
    recommended_max_cores = max(max_cores - 1, 1)
    warnings = []

    found = False
    for t in inst_tasks:
        if t.get("id") != task_id:
            continue

        task_key = t.get("task_key", "")
        if (
            task_key == "ARI_LOCAL_DATA_BACKUP"
            and daily_copies + weekly_copies <= 0
        ):
            return (
                jsonify(
                    success=False,
                    error=(
                        "Backup task needs at least one retained "
                        "daily or weekly copy"
                    ),
                ),
                400,
            )

        t["frequency"] = frequency
        t["active"] = active
        if task_key == "ARI_LOCAL_DATA_BACKUP":
            t["daily_copies"] = daily_copies
            t["weekly_copies"] = weekly_copies
            if backup_max_size_mb is not None:
                t["backup_max_size_mb"] = backup_max_size_mb
            # Optional admin-customised exclude lists. The keys are
            # only touched when the request explicitly contains them
            # (so other code paths like toggle/reorder don't lose
            # the customisation). An EMPTY list is honoured and
            # means "remove the override / fall back to defaults".
            for _ek in ("exclude_dirs", "exclude_paths"):
                if _ek in data:
                    raw = data.get(_ek) or []
                    if not isinstance(raw, list):
                        return jsonify(
                            success=False,
                            error="{0} must be a list".format(_ek),
                        ), 400
                    cleaned = []
                    for item in raw:
                        s = str(item or "").strip()
                        if s and s not in cleaned:
                            cleaned.append(s)
                    if cleaned:
                        t[_ek] = cleaned
                    else:
                        t.pop(_ek, None)
        if task_key == "APERO_SYNC_ASSETS":
            if assets_mode is not None:
                t["mode"] = assets_mode
            if has_assets_local_source:
                if assets_local_source:
                    t["local_source_path"] = assets_local_source
                else:
                    t.pop("local_source_path", None)
            if t.get("mode") == "local" and not t.get(
                    "local_source_path"):
                return jsonify(
                    success=False,
                    error=(
                        "local mode requires a local source "
                        "directory path."
                    ),
                ), 400

        if task_key in LEGACY_GSHEET_TASK_KEYS:
            if has_dry_run:
                t["DRY_RUN"] = bool(dry_run)
            if "dry_run" in t:
                t.pop("dry_run", None)

            resolved_secret_name = google_secret_name
            if not resolved_secret_name:
                try:
                    resolved_secret_name = _validate_google_secret_name(
                        t.get(
                            "google_secret_name",
                            DEFAULT_GOOGLE_SECRET_NAME,
                        )
                    )
                except ValueError:
                    resolved_secret_name = DEFAULT_GOOGLE_SECRET_NAME

            t["google_secret_name"] = resolved_secret_name
            secret_path = _legacy_admin_secret_path(
                app,
                resolved_secret_name,
            )
            if google_oauth_upload is not None:
                secret_path.parent.mkdir(parents=True, exist_ok=True)
                with open(secret_path, "w", encoding="utf-8") as outfile:
                    json.dump(
                        google_oauth_upload,
                        outfile,
                        indent=2,
                        sort_keys=False,
                    )
                    outfile.write("\n")
                os.chmod(secret_path, 0o600)

            if t.get("active", False) and not secret_path.exists():
                return (
                    jsonify(
                        success=False,
                        error=(
                            "Missing OAuth JSON file in "
                            "LOCAL_DATA_DIR/admin/. Upload one in the "
                            "task editor before testing this task."
                        ),
                    ),
                    400,
                )

        if task_key == "LEGACY_CHECK_GSHEET":
            instrument_key = _normalize_instrument_key(instrument)
            if "monitoring_sheet_url" in data:
                mon_url = str(
                    data.get("monitoring_sheet_url") or ""
                ).strip()
                mon_map = t.get("monitoring_sheet_urls")
                if not isinstance(mon_map, dict):
                    mon_map = {}
                if mon_url:
                    mon_map[instrument_key] = mon_url
                else:
                    mon_map.pop(instrument_key, None)
                if len(mon_map) > 0:
                    t["monitoring_sheet_urls"] = mon_map
                else:
                    t.pop("monitoring_sheet_urls", None)
                # Drop global legacy key to avoid URL bleed into
                # instruments that should remain unset.
                t.pop("monitoring_sheet_url", None)
            if "override_sheet_url" in data:
                over_url = str(
                    data.get("override_sheet_url") or ""
                ).strip()
                over_map = t.get("override_sheet_urls")
                if not isinstance(over_map, dict):
                    over_map = {}
                if over_url:
                    over_map[instrument_key] = over_url
                else:
                    over_map.pop(instrument_key, None)
                if len(over_map) > 0:
                    t["override_sheet_urls"] = over_map
                else:
                    t.pop("override_sheet_urls", None)
                # Drop global legacy key to avoid URL bleed into
                # instruments that should remain unset.
                t.pop("override_sheet_url", None)

        supports_mp = bool(task_module.MULTI_PROCESS.get(task_key, False))
        supports_local_task = bool(task_module.LOCAL_TASK.get(task_key, False))
        if sync_source is not None and sync_source and not supports_local_task:
            return (
                jsonify(
                    success=False,
                    error="sync_source is only supported for LOCAL_TASK tasks",
                ),
                400,
            )
        if (
            sync_profiles is not None
            and sync_profiles
            and not supports_local_task
        ):
            return (
                jsonify(
                    success=False,
                    error=(
                        "sync_profiles is only supported for "
                        "LOCAL_TASK tasks"
                    ),
                ),
                400,
            )
        preserve_mp = (
            supports_mp
            or any(
                k in data
                for k in [
                    "ncores",
                    "mp_backend",
                    "mp_start_method",
                    "mp_start_methd",
                ]
            )
            or any(k in t for k in ["ncores", "mp_backend", "mp_start_method"])
        )
        if preserve_mp:
            existing_ncores = t.get("ncores", 1)
            existing_backend = t.get("mp_backend", "threads")
            existing_start_method = t.get("mp_start_method", "default")

            try:
                resolved_ncores = int(
                    ncores if ncores is not None else existing_ncores
                )
            except (TypeError, ValueError):
                resolved_ncores = 1
            resolved_ncores = max(1, resolved_ncores)

            resolved_backend = (
                str(mp_backend if mp_backend is not None else existing_backend)
                .strip()
                .lower()
            )
            if resolved_backend not in ["threads", "processes"]:
                resolved_backend = "threads"

            resolved_start_method = (
                str(
                    mp_start_method
                    if mp_start_method is not None
                    else existing_start_method
                )
                .strip()
                .lower()
            )
            if resolved_start_method not in [
                "default",
                "spawn",
                "fork",
                "forkserver",
            ]:
                resolved_start_method = "default"

            t["ncores"] = resolved_ncores
            t["mp_backend"] = resolved_backend
            t["mp_start_method"] = resolved_start_method
            if resolved_ncores > recommended_max_cores:
                warnings.append(
                    f"NCORES={resolved_ncores} is above recommended max "
                    f"({recommended_max_cores}) for this server."
                )
        else:
            t.pop("ncores", None)
            t.pop("mp_backend", None)
            t.pop("mp_start_method", None)

        if supports_local_task:
            if sync_profiles is not None:
                if sync_profiles:
                    t["sync_profiles"] = sync_profiles
                else:
                    t.pop("sync_profiles", None)
                t.pop("sync_source", None)
            elif sync_source is not None:
                t["sync_source"] = sync_source
            else:
                t.setdefault("sync_source", str(t.get("sync_source", "") or ""))
        else:
            t.pop("sync_source", None)
            t.pop("sync_profiles", None)
        found = True
        break

    if not found:
        return jsonify(success=False, error="Task not found"), 404

    all_tasks[instrument] = inst_tasks
    save_async_tasks(all_tasks)
    app._refresh_admin_health_after_change(user_info, perms)
    return jsonify(success=True, id=task_id, warnings=warnings)


def api_async_tasks_list(app):
    """List async task configs for an instrument with runtime state."""
    user_info, perms = app._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    instrument = request.args.get("instrument", "").strip()
    if not instrument:
        return jsonify(success=False, error="No instrument"), 400

    from apero_ri import tasks as task_module

    all_tasks = load_async_tasks()
    inst_tasks, changed = app._merge_async_task_catalog(instrument, all_tasks)
    profile_names = _instrument_profile_names(instrument)
    if changed:
        save_async_tasks(all_tasks)

    result = []
    import_errors = getattr(task_module, "IMPORT_ERRORS", {}) or {}
    for tc in inst_tasks:
        entry = dict(tc)
        entry["active"] = _coerce_bool(entry.get("active", True))
        entry["active"] = _coerce_bool(entry.get("active", True))
        tid = tc.get("id", "")
        rt = task_runner.get_task_status(tid) if tid else {"found": False}
        if not rt.get("found"):
            persisted = task_runner.get_persisted_task_info_error(tid)
            import_error = str(
                import_errors.get(tc.get("task_key", ""), "")
            ).strip()
            info_text = persisted.get("info", "") or str(
                tc.get("info", "") or ""
            )
            err_text = persisted.get("error", "") or str(
                tc.get("error", "") or ""
            )
            if import_error:
                err_text = import_error
                if not info_text:
                    info_text = (
                        "## Task Import Error\n\n"
                        f'**Task key**: `{tc.get("task_key", "")}`\n\n'
                        f"```\n{import_error}\n```\n"
                    )
            rt = {
                "found": False,
                "status": tc.get("last_status", "not_started"),
                "progress": 0,
                "subprogress": 0,
                "use_subprocess": bool(
                    task_module.USE_SUBPROCESS.get(
                        tc.get("task_key", ""), False
                    )
                ),
                "info": info_text,
                "last_run": tc.get("last_run", "Never"),
                "output_files": tc.get("output_files", []),
                "run_params": tc.get("last_run_params", {}),
                "is_current": False,
                "is_queued": False,
                "error": err_text,
                "run_count": tc.get("run_count", 0),
            }
        entry["runtime"] = rt
        task_key = entry.get("task_key", "")
        entry["task_type"] = task_module.TYPE.get(task_key, "INSTRUMENT")
        entry["local_task"] = bool(task_module.LOCAL_TASK.get(task_key, False))
        result.append(entry)

    queue_status = task_runner.get_status()
    return jsonify(
        success=True,
        tasks=result,
        queue=queue_status,
        profile_names=profile_names,
    )


def api_async_tasks_global_list(app):
    """Load global tasks from registry defaults and overrides."""
    user_info, perms = app._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    from apero_ri import tasks as task_module

    import_errors = getattr(task_module, "IMPORT_ERRORS", {}) or {}
    all_tasks = load_async_tasks()
    global_scope = "__GLOBAL__"
    global_tasks, changed = app._merge_async_task_catalog(
        global_scope, all_tasks
    )
    if changed:
        save_async_tasks(all_tasks)

    result = []
    for tc in global_tasks:
        entry = dict(tc)
        tid = tc.get("id", "")
        rt = task_runner.get_task_status(tid) if tid else {"found": False}
        if not rt.get("found"):
            persisted = task_runner.get_persisted_task_info_error(tid)
            import_error = str(
                import_errors.get(tc.get("task_key", ""), "")
            ).strip()
            info_text = persisted.get("info", "") or str(
                tc.get("info", "") or ""
            )
            err_text = persisted.get("error", "") or str(
                tc.get("error", "") or ""
            )
            if import_error:
                err_text = import_error
                if not info_text:
                    info_text = (
                        "## Task Import Error\n\n"
                        f'**Task key**: `{tc.get("task_key", "")}`\n\n'
                        f"```\n{import_error}\n```\n"
                    )
            rt = {
                "found": False,
                "status": tc.get("last_status", "not_started"),
                "progress": 0,
                "subprogress": 0,
                "use_subprocess": bool(
                    task_module.USE_SUBPROCESS.get(
                        tc.get("task_key", ""), False
                    )
                ),
                "info": info_text,
                "last_run": tc.get("last_run", "Never"),
                "output_files": tc.get("output_files", []),
                "run_params": tc.get("last_run_params", {}),
                "is_current": False,
                "is_queued": False,
                "error": err_text,
                "run_count": tc.get("run_count", 0),
            }
        entry["runtime"] = rt
        entry["task_type"] = "GLOBAL"
        entry["instrument"] = global_scope
        task_key = entry.get("task_key", "")
        entry["local_task"] = bool(task_module.LOCAL_TASK.get(task_key, False))
        if task_key == "ARI_LOCAL_DATA_BACKUP":
            try:
                from apero_ri.tasks.apero_backup import (
                    DEFAULT_EXCLUDE_DIRS as _DED,
                    DEFAULT_EXCLUDE_PATHS as _DEP,
                )
                entry["default_exclude_dirs"] = list(_DED)
                entry["default_exclude_paths"] = list(_DEP)
            except Exception:  # noqa: BLE001
                entry["default_exclude_dirs"] = []
                entry["default_exclude_paths"] = []
        result.append(entry)

    queue_status = task_runner.get_status()
    return jsonify(success=True, tasks=result, queue=queue_status)


def api_async_tasks_task_list(app):
    """Return available task classes from apero_ri.tasks.TASK_LIST."""
    user_info, perms = app._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    try:
        from apero_ri import tasks as task_module
    except Exception:
        _tb = traceback.format_exc()
        return (
            jsonify(
                success=False,
                error=f"Failed to import task catalog:\n{_tb}",
            ),
            200,
        )
    opts = []
    max_cores = max(int(os.cpu_count() or 1), 1)
    for key, cls in task_module.TASK_LIST.items():
        try:
            inst = cls()
            task_type = task_module.TYPE.get(key, "INSTRUMENT")
            name = inst.name
            description = inst.description
        except Exception:
            task_type = task_module.TYPE.get(key, "INSTRUMENT")
            name = f"{key} (Init Error)"
            description = traceback.format_exc()
        opts.append(
            {
                "key": key,
                "name": name,
                "description": description,
                "type": task_type,
                "local_task": bool(task_module.LOCAL_TASK.get(key, False)),
                "multi_process": bool(
                    task_module.MULTI_PROCESS.get(key, False)
                ),
            }
        )
    return jsonify(
        success=True,
        tasks=opts,
        multiprocessing={
            "max_cores": max_cores,
            "recommended_max_cores": max(max_cores - 1, 1),
            "backends": ["threads", "processes"],
            "start_methods": ["default", "spawn", "fork", "forkserver"],
        },
    )


def api_async_tasks_run_now(app):
    """Enqueue a single task to run immediately."""
    user_info, perms = app._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    task_id = data.get("id", "").strip()
    force_run = bool(data.get("force_run", False))
    local_data_dir = data.get("local_data_dir", "") or str(Path.home() / ".ari")
    if not instrument or not task_id:
        return jsonify(success=False, error="Missing fields"), 400

    all_tasks = load_async_tasks()
    inst_tasks, _ = app._merge_async_task_catalog(instrument, all_tasks)
    task_cfg = next((t for t in inst_tasks if t.get("id") == task_id), None)
    if not task_cfg:
        return jsonify(success=False, error="Task not found"), 404

    allowed, reason = task_runner.can_enqueue_now(task_cfg)
    if not allowed:
        return jsonify(success=False, error=reason), 409

    from apero_ri import tasks as task_module

    task_key = task_cfg.get("task_key", "")
    task_cls = task_module.TASK_LIST.get(task_key)
    if not task_cls:
        return jsonify(success=False, error="Unknown task class"), 400

    all_profiles = load_apero_profiles(enabled_only=True)
    run_task_cfg = dict(task_cfg)
    if force_run:
        run_task_cfg["force_run"] = True
    run_params = task_runner.build_run_params(
        instrument, local_data_dir, all_profiles, run_task_cfg
    )
    try:
        instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
        instance.USE_SUBPROCESS = bool(
            task_module.USE_SUBPROCESS.get(task_key, False)
        )
        instance._task_key = task_key
    except Exception:
        task_cfg["last_status"] = "failed"
        task_cfg["error"] = traceback.format_exc()
        all_tasks[instrument] = inst_tasks
        save_async_tasks(all_tasks)
        return (
            jsonify(
                success=False,
                error="Task initialization failed; see task error panel.",
            ),
            500,
        )
    task_runner.enqueue(instrument, task_id, instance, run_params, prepend=True)
    return jsonify(success=True)


def api_async_tasks_status(app):
    """Poll runtime status for a set of task ids and queue state."""
    user_info, perms = app._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    ids_param = request.args.get("ids", "").strip()
    task_ids = [i for i in ids_param.split(",") if i.strip()]
    if not task_ids:
        queue_status = task_runner.get_status()
        current_info = queue_status.get("current_info") or {}
        current_id = str(current_info.get("task_id", "")).strip()
        queue_ids = [
            str(item.get("task_id", "")).strip()
            for item in (queue_status.get("queue_info") or [])
            if isinstance(item, dict)
        ]
        task_ids = [tid for tid in [current_id] + queue_ids if tid]

    all_tasks = load_async_tasks()
    task_cfg_map: dict = {}
    for _inst, tc_list in all_tasks.items():
        for tc in tc_list:
            tid = tc.get("id", "")
            if tid:
                task_cfg_map[tid] = tc

    statuses: dict = {}
    from apero_ri import tasks as task_module

    for tid in task_ids:
        rt = task_runner.get_task_status(tid)
        if not rt.get("found"):
            tc = task_cfg_map.get(tid, {})
            task_key = str(tc.get("task_key", "") or "")
            persisted = task_runner.get_persisted_task_info_error(tid)
            import_error = str(
                task_module.IMPORT_ERRORS.get(task_key, "") or ""
            ).strip()
            info_text = persisted.get("info", "") or str(
                tc.get("info", "") or ""
            )
            err_text = persisted.get("error", "") or str(
                tc.get("error", "") or ""
            )
            if import_error:
                err_text = import_error
                if not info_text:
                    info_text = (
                        "## Task Import Error\n\n"
                        f"**Task key**: `{task_key}`\n\n"
                        f"```\n{import_error}\n```\n"
                    )
            rt = {
                "found": False,
                "status": tc.get("last_status", "not_started"),
                "progress": 0,
                "subprogress": 0,
                "use_subprocess": bool(
                    task_module.USE_SUBPROCESS.get(task_key, False)
                ),
                "info": info_text,
                "last_run": tc.get("last_run", "Never"),
                "output_files": tc.get("output_files", []),
                "run_params": tc.get("last_run_params", {}),
                "is_current": False,
                "is_queued": False,
                "error": err_text,
                "run_count": tc.get("run_count", 0),
                "log_path": "",
            }
        statuses[tid] = rt
    queue_status = task_runner.get_status()
    return jsonify(success=True, statuses=statuses, queue=queue_status)


def api_async_tasks_run_all(app):
    """Enqueue all active tasks for an instrument."""
    user_info, perms = app._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, error="Missing data"), 400

    instrument = data.get("instrument", "").strip()
    action = data.get("action", "add")
    force_run = bool(data.get("force_run", False))
    local_data_dir = data.get("local_data_dir", "") or str(Path.home() / ".ari")
    if not instrument:
        return jsonify(success=False, error="Missing instrument"), 400

    if action == "replace":
        task_runner.stop_and_clear()

    all_tasks = load_async_tasks()
    inst_tasks, _ = app._merge_async_task_catalog(instrument, all_tasks)
    inst_tasks = sorted(inst_tasks, key=lambda t: t.get("order", 999))

    from apero_ri import tasks as task_module

    all_profiles = load_apero_profiles(enabled_only=True)

    added = []
    blocked = []
    for task_cfg in inst_tasks:
        if not task_cfg.get("active", True):
            continue
        # Skip tasks that were explicitly cancelled by
        # the user – do not re-queue them automatically.
        last_st = str(
            task_cfg.get('last_status', '') or ''
        ).strip().lower()
        if last_st == 'cancelled':
            blocked.append({
                'id': task_cfg.get('id', ''),
                'reason': 'Task was cancelled.',
            })
            continue
        allowed, reason = task_runner.can_enqueue_now(task_cfg)
        if not allowed:
            blocked.append({"id": task_cfg.get("id", ""), "reason": reason})
            continue
        task_key = task_cfg.get("task_key", "")
        task_cls = task_module.TASK_LIST.get(task_key)
        if not task_cls:
            continue
        tid = task_cfg.get("id", "")
        if not tid:
            continue
        run_task_cfg = dict(task_cfg)
        if force_run:
            run_task_cfg["force_run"] = True

        run_params = task_runner.build_run_params(
            instrument, local_data_dir, all_profiles, run_task_cfg
        )
        try:
            instance = task_runner.hydrate_runtime_state(task_cls(), task_cfg)
            instance.USE_SUBPROCESS = bool(
                task_module.USE_SUBPROCESS.get(task_key, False)
            )
            instance._task_key = task_key
        except Exception:
            task_cfg["last_status"] = "failed"
            task_cfg["error"] = traceback.format_exc()
            blocked.append(
                {
                    "id": task_cfg.get("id", ""),
                    "reason": "Task initialization failed;"
                    "see task error panel.",

                }
            )
            continue
        task_runner.enqueue(instrument, tid, instance, run_params)
        added.append(tid)

    all_tasks[instrument] = inst_tasks
    save_async_tasks(all_tasks)

    return jsonify(success=True, added=added, blocked=blocked)


def api_async_tasks_read_file(app):
    """Return a preview of the first lines of an async task output file."""
    user_info, perms = app._require_async_tasks_perm()
    if not user_info:
        return jsonify(success=False, error="Unauthorized"), 401

    path = request.args.get("path", "").strip()
    preview_lines = max(int(request.args.get("lines", 50) or 50), 1)
    resolved, error_response = app._validate_async_task_file_path(path)
    if error_response is not None:
        return error_response
    if resolved is None:
        return jsonify(success=False, error="Invalid path"), 400
    try:
        raw = resolved.read_bytes()
        suffixes = {suffix.lower() for suffix in resolved.suffixes}
        if (
            suffixes.intersection({".gz", ".zip", ".fits", ".tar"})
            or b"\x00" in raw[:4096]
        ):
            return jsonify(
                success=True,
                preview=(
                    "Binary file preview is not available. "
                    "Use Download instead."
                ),
                truncated=False,
                line_count=0,
                preview_lines=preview_lines,
                is_binary=True,
                is_json=False,
                json_table=None,
                path=str(resolved),
            )

        text = raw.decode("utf-8", errors="replace")
        all_lines = text.splitlines()
        preview = "\n".join(all_lines[:preview_lines])

        json_table = None
        if resolved.suffix.lower() == ".json":
            try:
                parsed = json.loads(text)
                json_table = app._build_json_preview_table(parsed)
            except Exception:
                json_table = None

        return jsonify(
            success=True,
            preview=preview,
            truncated=len(all_lines) > preview_lines,
            line_count=len(all_lines),
            preview_lines=preview_lines,
            is_binary=False,
            is_json=json_table is not None,
            json_table=json_table,
            path=str(resolved),
        )
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500


def build_json_preview_table(data, max_rows: int = 200) -> dict:
    """Convert JSON data into a compact table payload for UI rendering."""

    def _cell(value) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _rows_to_table(
        rows_data: list, columns_hint=None, row_count_hint=None
    ) -> dict:
        columns = []
        seen = set()
        if isinstance(columns_hint, list):
            for col in columns_hint:
                scol = str(col)
                if scol not in seen:
                    seen.add(scol)
                    columns.append(scol)
        for item in rows_data:
            if isinstance(item, dict):
                for key in item.keys():
                    skey = str(key)
                    if skey not in seen:
                        seen.add(skey)
                        columns.append(skey)

        rows = []
        for item in rows_data[:max_rows]:
            if isinstance(item, dict):
                row = {col: _cell(item.get(col, "")) for col in columns}
            else:
                row = {"value": _cell(item)}
            rows.append(row)

        row_count = (
            row_count_hint
            if isinstance(row_count_hint, int)
            else len(rows_data)
        )
        if row_count < len(rows_data):
            row_count = len(rows_data)
        return {
            "columns": columns if columns else ["value"],
            "rows": rows,
            "row_count": row_count,
            "truncated": len(rows_data) > max_rows,
        }

    if isinstance(data, list):
        if all(isinstance(item, dict) for item in data):
            return _rows_to_table(data)

        rows = []
        for index, value in enumerate(data[:max_rows], start=1):
            rows.append({"index": str(index), "value": _cell(value)})
        return {
            "columns": ["index", "value"],
            "rows": rows,
            "row_count": len(data),
            "truncated": len(data) > max_rows,
        }

    if isinstance(data, dict):
        rows_payload = data.get("rows")
        if isinstance(rows_payload, list):
            return _rows_to_table(
                rows_payload,
                columns_hint=data.get("columns"),
                row_count_hint=data.get("row_count"),
            )

        items = list(data.items())
        rows = []
        for key, value in items[:max_rows]:
            rows.append({"key": str(key), "value": _cell(value)})
        return {
            "columns": ["key", "value"],
            "rows": rows,
            "row_count": len(items),
            "truncated": len(items) > max_rows,
        }

    return {
        "columns": ["value"],
        "rows": [{"value": _cell(data)}],
        "row_count": 1,
        "truncated": False,
    }
