"""Async task helper utilities extracted from ARIApp."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Tuple


def coerce_task_frequency(value: Any, default: float = 24.0) -> float:
    """Normalize a task frequency value in hours."""
    try:
        freq = float(value)
        if freq > 0:
            return freq
    except (TypeError, ValueError):
        pass
    return float(default)


def coerce_task_enabled(value: Any, default: bool = False) -> bool:
    """Normalize a task enabled flag."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        sval = value.strip().lower()
        if sval in ["true", "1", "yes", "on"]:
            return True
        if sval in ["false", "0", "no", "off", ""]:
            return False
    return bool(value)


def is_global_scope(instrument: str) -> bool:
    """Return True if this task scope is the shared global scope."""
    return str(instrument).strip() == "__GLOBAL__"


def task_keys_for_scope(instrument: str) -> List[str]:
    """Return task keys allowed in a given scope from tasks.TYPE."""
    from apero_ri import tasks as task_module

    want_type = "GLOBAL" if is_global_scope(instrument) else "INSTRUMENT"
    keys: List[str] = []
    for task_key in task_module.TASK_LIST.keys():
        ttype = (
            str(task_module.TYPE.get(task_key, "INSTRUMENT")).strip().upper()
        )
        if ttype == want_type:
            keys.append(task_key)
    return keys


def normalize_sync_profiles(raw: Any) -> Dict[str, Dict[str, str]]:
    """Normalize per-profile sync settings from task config."""
    out: Dict[str, Dict[str, str]] = {}
    if not isinstance(raw, dict):
        return out

    for profile_name, entry in raw.items():
        pname = str(profile_name or "").strip()
        if not pname or not isinstance(entry, dict):
            continue

        mode = str(entry.get("mode", "run_server") or "run_server")
        mode = mode.strip().lower()
        if mode not in ["run_server", "fetch_precomputed"]:
            mode = "run_server"
        sync_source = str(entry.get("sync_source", "") or "").strip()
        if mode == "run_server" and not sync_source:
            continue
        out[pname] = dict(mode=mode, sync_source=sync_source)
    return out


def merge_async_task_catalog(
    instrument: str, all_tasks: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], bool]:
    """Merge persisted task overrides with task catalog defaults."""
    from apero_ri import tasks as task_module

    import_errors = getattr(task_module, "IMPORT_ERRORS", {}) or {}

    stored_tasks = all_tasks.get(instrument, [])
    if not isinstance(stored_tasks, list):
        stored_tasks = []

    by_key: Dict[str, Dict[str, Any]] = {}
    for task_cfg in stored_tasks:
        if not isinstance(task_cfg, dict):
            continue
        key = str(task_cfg.get('task_key', '')).strip()
        if key and key not in by_key:
            by_key[key] = task_cfg

    merged: List[Dict[str, Any]] = []
    keys = task_keys_for_scope(instrument)
    for idx, task_key in enumerate(keys, start=1):
        task_cfg = dict(by_key.get(task_key, {}))
        task_id = str(task_cfg.get("id", "")).strip()
        if not task_id:
            task_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"ari-async-task:{instrument}:{task_key}",
                )
            )

        default_freq = coerce_task_frequency(
            task_module.FREQ.get(task_key, 24.0), 24.0
        )
        default_enabled = coerce_task_enabled(
            task_module.ENABLED.get(task_key, False), False
        )

        merged_cfg: Dict[str, Any] = {
            "id": task_id,
            "task_key": task_key,
            "frequency": coerce_task_frequency(
                task_cfg.get("frequency", default_freq), default_freq
            ),
            "active": coerce_task_enabled(
                task_cfg.get("active", default_enabled), default_enabled
            ),
            "order": idx,
        }

        if task_key == "ARI_LOCAL_DATA_BACKUP":
            try:
                daily_copies = int(task_cfg.get("daily_copies", 7) or 0)
            except (TypeError, ValueError):
                daily_copies = 7
            try:
                weekly_copies = int(task_cfg.get("weekly_copies", 4) or 0)
            except (TypeError, ValueError):
                weekly_copies = 4
            merged_cfg["daily_copies"] = max(0, daily_copies)
            merged_cfg["weekly_copies"] = max(0, weekly_copies)
            from apero_ri.tasks.apero_backup import (
                DEFAULT_BACKUP_MAX_SIZE_MB,
            )
            try:
                backup_max_mb = float(
                    task_cfg.get(
                        "backup_max_size_mb", DEFAULT_BACKUP_MAX_SIZE_MB
                    )
                )
            except (TypeError, ValueError):
                backup_max_mb = float(DEFAULT_BACKUP_MAX_SIZE_MB)
            if backup_max_mb <= 0:
                backup_max_mb = float(DEFAULT_BACKUP_MAX_SIZE_MB)
            merged_cfg["backup_max_size_mb"] = backup_max_mb
            # Pass through admin-customised exclude lists (the
            # backup task itself falls back to the apero_backup
            # module's DEFAULT_EXCLUDE_* tuples when these are
            # missing or empty).
            for _key in ("exclude_dirs", "exclude_paths"):
                _val = task_cfg.get(_key)
                if isinstance(_val, list):
                    cleaned = []
                    for _item in _val:
                        _s = str(_item or "").strip()
                        if _s and _s not in cleaned:
                            cleaned.append(_s)
                    if cleaned:
                        merged_cfg[_key] = cleaned

        if task_key == "APERO_SYNC_ASSETS":
            mode_val = (
                str(task_cfg.get("mode") or "remote").strip().lower()
            )
            # Backwards compatibility: legacy values "sync"/"upload"
            # both mean "remote" (download from rsync share). The
            # only other supported value is "local" (copy from a
            # local source directory).
            if mode_val in ("sync", "upload", "remote"):
                mode_val = "remote"
            elif mode_val != "local":
                mode_val = "remote"
            merged_cfg["mode"] = mode_val
            local_src = str(
                task_cfg.get("local_source_path") or ""
            ).strip()
            if local_src:
                merged_cfg["local_source_path"] = local_src
            merged_cfg["force_download"] = bool(
                task_cfg.get("force_download", False)
            )

        if task_key in [
            "LEGACY_ASTROM_GSHEET",
            "LEGACY_REJECT_GSHEET",
        ]:
            for _key in [
                "DRY_RUN",
                "google_secret_name",
                "sheet_id",
                "sheet_name",
                "sheet_names",
                "resolve_tolerance_arcsec",
                "created_by",
            ]:
                if _key in task_cfg:
                    merged_cfg[_key] = task_cfg.get(_key)

        if task_key == "LEGACY_CHECK_GSHEET":
            for _key in [
                "DRY_RUN",
                "google_secret_name",
                "monitoring_sheet_url",
                "override_sheet_url",
            ]:
                if _key in task_cfg:
                    merged_cfg[_key] = task_cfg.get(_key)

        if bool(task_module.MULTI_PROCESS.get(task_key, False)):
            try:
                ncores = int(task_cfg.get("ncores", 1) or 1)
            except (TypeError, ValueError):
                ncores = 1
            merged_cfg["ncores"] = max(1, ncores)
            backend = (
                str(task_cfg.get("mp_backend", "threads") or "threads")
                .strip()
                .lower()
            )
            start_method = (
                str(task_cfg.get("mp_start_method", "default") or "default")
                .strip()
                .lower()
            )
            merged_cfg["mp_backend"] = (
                backend if backend in ["threads", "processes"] else "threads"
            )
            merged_cfg["mp_start_method"] = (
                start_method
                if start_method in ["default", "spawn", "fork", "forkserver"]
                else "default"
            )
        else:
            if any(
                k in task_cfg
                for k in ["ncores", "mp_backend", "mp_start_method"]
            ):
                try:
                    ncores = int(task_cfg.get("ncores", 1) or 1)
                except (TypeError, ValueError):
                    ncores = 1
                merged_cfg["ncores"] = max(1, ncores)
                backend = (
                    str(task_cfg.get("mp_backend", "threads") or "threads")
                    .strip()
                    .lower()
                )
                start_method = (
                    str(task_cfg.get("mp_start_method", "default") or "default")
                    .strip()
                    .lower()
                )
                merged_cfg["mp_backend"] = (
                    backend
                    if backend in ["threads", "processes"]
                    else "threads"
                )
                merged_cfg["mp_start_method"] = (
                    start_method
                    if start_method
                    in ["default", "spawn", "fork", "forkserver"]
                    else "default"
                )

        if bool(task_module.LOCAL_TASK.get(task_key, False)):
            merged_cfg["sync_source"] = str(
                task_cfg.get("sync_source", "") or ""
            ).strip()
            sync_profiles = normalize_sync_profiles(
                task_cfg.get("sync_profiles", {})
            )
            if sync_profiles:
                merged_cfg["sync_profiles"] = sync_profiles
            else:
                merged_cfg.pop("sync_profiles", None)
        else:
            merged_cfg.pop("sync_source", None)
            merged_cfg.pop("sync_profiles", None)

        for field in [
            "last_run",
            "run_count",
            "output_files",
            "last_status",
            "cooldown_until",
            "filters",
        ]:
            if field in task_cfg:
                merged_cfg[field] = task_cfg.get(field)

        import_error = str(import_errors.get(task_key, "")).strip()
        if import_error:
            merged_cfg["last_status"] = "failed"

        merged.append(merged_cfg)

    original = all_tasks.get(instrument, [])
    changed = original != merged
    all_tasks[instrument] = merged
    return merged, changed
