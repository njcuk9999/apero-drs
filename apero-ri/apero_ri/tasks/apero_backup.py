#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI task for backing up LOCAL_DATA_DIR."""

import os
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from apero_ri.core import backup_backend as bb
from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.tasks.apero_backup"
# Set AIR local data directory
ARI_DIR = Path.home() / ".ari"
# Set the list of parameters required for this task
PARAM_LIST = ["LOCAL_DATA_DIR", "INSTRUMENT", "TASK_CONFIG"]
# Set the list of APERO profile parameters that this task depends on (if any)
APERO_PROFILE_PARAM_LIST: List[str] = []
# Maximum allowed size for one backup archive input (bytes)
BACKUP_MAX_SIZE = 1024**3
# Top-level directories in LOCAL_DATA_DIR to exclude from backups by default.
DEFAULT_EXCLUDE_DIRS = ("backups", "tasks", "download", "downloads", "secret")
# Specific secret-bearing config files that should not be archived.
DEFAULT_EXCLUDE_PATHS = (
    "admin/general/apero_profiles.yaml",
    "admin/general/db_access.yaml",
    "admin/apero_profiles.yaml",
    "admin/db_access.yaml",
)
# Set the default frequency for this task (in hours)
DEFAULT_FREQUENCY = 6.0
# Set whether this task is enabled by default in the admin portal
DEFAULT_ENABLED = True
# Set the type of task (INSTRUMENT, GLOBAL)
TASK_TYPE = "GLOBAL"
# Whether this task has a sub-process (for sub-processing loading bar in UI)
USE_SUBPROCESS = False
# Whether this task can be run in multi-process mode
# (if False, will always run in main process)
MULTI_PROCESS = False
# Whether this task supports local pre-built output sync/copy workflows.
LOCAL_TASK = False
# Available filters (for testing purposes)
FILTERS = []


# =============================================================================
# Define global classes
# =============================================================================
class AperoLocalDataBackupTask(apero_async.AperoAsyncTask):
    """Create retained daily and weekly backups of LOCAL_DATA_DIR."""

    def __init__(self, status="pending"):
        name = "Local Data Backup Task"
        description = (
            "Create compressed backups of LOCAL_DATA_DIR and keep "
            "daily / weekly retained copies."
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]):
        local_data_dir = (
            Path(params.get("LOCAL_DATA_DIR", str(ARI_DIR)))
            .expanduser()
            .resolve()
        )
        task_cfg = dict(params.get("TASK_CONFIG", {}))
        task_logger = params.get("TASK_LOGGER")
        stop_event = params.get("STOP_EVENT")

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        tlog("LOCAL_DATA backup start.")
        tlog(f"Source directory: {local_data_dir}")

        if stop_event is not None and stop_event.is_set():
            tlog("Cancellation requested before backup started. Exiting.")
            return

        self._validate_source_dir(local_data_dir)

        daily_copies = max(int(task_cfg.get("daily_copies", 7) or 0), 0)
        weekly_copies = max(int(task_cfg.get("weekly_copies", 4) or 0), 0)
        raw_excludes = task_cfg.get("exclude_dirs", list(DEFAULT_EXCLUDE_DIRS))
        if not isinstance(raw_excludes, list):
            raw_excludes = list(DEFAULT_EXCLUDE_DIRS)
        raw_exclude_paths = task_cfg.get(
            "exclude_paths", list(DEFAULT_EXCLUDE_PATHS)
        )
        if not isinstance(raw_exclude_paths, list):
            raw_exclude_paths = list(DEFAULT_EXCLUDE_PATHS)
        exclude_dirs = []
        for value in raw_excludes:
            name = Path(str(value)).name.strip()
            if not name:
                continue
            if name not in exclude_dirs:
                exclude_dirs.append(name)
        exclude_paths = []
        for value in raw_exclude_paths:
            rel_value = self._normalize_relative_path(value)
            if rel_value and rel_value not in exclude_paths:
                exclude_paths.append(rel_value)

        estimated_size = self._estimate_archive_input_size(
            local_data_dir, exclude_dirs, exclude_paths
        )
        tlog(
            "Estimated archive input size: "
            f"{self._format_bytes(estimated_size)} "
            f"(limit={self._format_bytes(BACKUP_MAX_SIZE)})."
        )
        if estimated_size > BACKUP_MAX_SIZE:
            warning_msg = (
                "Backup skipped: estimated archive input size "
                f"({self._format_bytes(estimated_size)}) "
                "exceeds BACKUP_MAX_SIZE "
                f"({self._format_bytes(BACKUP_MAX_SIZE)})."
            )
            print(f"WARNING: {warning_msg}")
            tlog(f"WARNING: {warning_msg}")
            self.info = f"## Local Data Backup\n\n**WARNING**: {warning_msg}\n"
            self.progress = 1.0
            raise ValueError(warning_msg)

        if daily_copies == 0 and weekly_copies == 0:
            raise ValueError(
                "At least one retained daily or weekly copy is required."
            )

        backup_root = local_data_dir / "backups"
        daily_dir = backup_root / "daily"
        weekly_dir = backup_root / "weekly"
        daily_dir.mkdir(parents=True, exist_ok=True)
        weekly_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc)
        generated_at = timestamp.isoformat()
        time_tag = timestamp.strftime("%Y%m%dT%H%M%SZ")
        day_tag = timestamp.strftime("%Y%m%d")
        iso_week = timestamp.isocalendar()
        week_tag = f"{iso_week.year}W{iso_week.week:02d}"
        archive_files: List[Path] = []
        archive_actions: Dict[Path, str] = {}

        # Reset info to empty string so this run's content doesn't accumulate
        # with prior runs
        self.info = ""
        self.info = (
            f"## Local Data Backup\n\n"
            f"**Source**: `{local_data_dir}`  \n"
            f"**Generated at**: {generated_at}  \n"
            f"**Daily copies**: {daily_copies}  \n"
            f"**Weekly copies**: {weekly_copies}  \n"
            f"**Excluded dirs**: {self._format_csv_or_none(exclude_dirs)}  \n"
            f"**Excluded paths**: {self._format_csv_or_none(exclude_paths)}\n"
        )
        tlog(
            f"Configured retention daily={daily_copies}, "
            f"weekly={weekly_copies}, "
            f"excluded_dirs={len(exclude_dirs)}, "
            f"excluded_paths={len(exclude_paths)}."
        )

        if daily_copies > 0:
            if stop_event is not None and stop_event.is_set():
                tlog(
                    "Cancellation requested before daily archive creation. "
                    "Exiting."
                )
                return
            daily_path = daily_dir / f"{local_data_dir.name}_{day_tag}.tar.gz"
            tlog(f"Creating daily archive: {daily_path.name}")
            daily_action = self._create_or_replace_archive(
                local_data_dir, daily_path, exclude_dirs, exclude_paths
            )
            tlog(f"Daily archive {daily_action}: {daily_path.name}")
            if daily_action == "created":
                self.info += (
                    f"\n### Daily backup\nCreated `{daily_path.name}`\n"
                )
            else:
                self.info += (
                    f"\n### Daily backup\nReplaced `{daily_path.name}`\n"
                )
            archive_files.append(daily_path)
            archive_actions[daily_path] = daily_action
            self.progress = 0.5 if weekly_copies > 0 else 0.8

        if weekly_copies > 0:
            if stop_event is not None and stop_event.is_set():
                tlog(
                    "Cancellation requested before weekly archive creation. "
                    "Exiting."
                )
                return
            weekly_path = (
                weekly_dir / f"{local_data_dir.name}_{week_tag}.tar.gz"
            )
            tlog(f"Creating weekly archive: {weekly_path.name}")
            weekly_action = self._create_or_replace_archive(
                local_data_dir, weekly_path, exclude_dirs, exclude_paths
            )
            tlog(f"Weekly archive {weekly_action}: {weekly_path.name}")
            if weekly_action == "created":
                self.info += (
                    f"\n### Weekly backup\nCreated `{weekly_path.name}`\n"
                )
            else:
                self.info += (
                    f"\n### Weekly backup\nReplaced `{weekly_path.name}`\n"
                )
            archive_files.append(weekly_path)
            archive_actions[weekly_path] = weekly_action
            self.progress = 0.8

        pruned_daily = self._prune_archives(daily_dir, daily_copies)
        pruned_weekly = self._prune_archives(weekly_dir, weekly_copies)
        tlog(
            f"Pruned archives: daily={
                len(pruned_daily)}, weekly={
                len(pruned_weekly)}.")

        manifest_rows = []
        for path in archive_files:
            manifest_rows.append(
                {
                    "type": archive_actions.get(path, "created"),
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                }
            )
        for path in pruned_daily:
            manifest_rows.append({"type": "pruned_daily", "path": str(path)})
        for path in pruned_weekly:
            manifest_rows.append({"type": "pruned_weekly", "path": str(path)})

        manifest_path = backup_root / "backup_manifest.json"
        apero_async.save_results(
            manifest_path,
            manifest_rows,
            metadata={
                "GENERATED_AT": generated_at,
                "SOURCE_DIR": str(local_data_dir),
                "DAILY_COPIES": daily_copies,
                "WEEKLY_COPIES": weekly_copies,
            },
        )
        tlog(f"Manifest saved: {manifest_path}")

        self.output_files = [str(manifest_path)] + [
            str(path) for path in archive_files
        ]
        self.info += f"\n### Manifest\nSaved `{manifest_path.name}`\n"
        if pruned_daily or pruned_weekly:
            self.info += "\n### Pruned copies\n"
            for path in pruned_daily + pruned_weekly:
                self.info += f"- `{path.name}`\n"

        local_inventory = bb.list_local_backups(local_data_dir=local_data_dir)
        local_count = int(local_inventory.get("total_count", 0) or 0)
        local_size = int(local_inventory.get("total_bytes", 0) or 0)
        tlog(
            f"Local backup inventory: files={local_count}, "
            f"size={bb.format_bytes(local_size)}."
        )
        self.info += (
            "\n### Local backup status\n"
            f"- Files: {local_count}\n"
            f"- Size: {bb.format_bytes(local_size)}\n"
        )

        if stop_event is not None and stop_event.is_set():
            tlog("Cancellation requested before cloud sync. Exiting.")
            return

        sync_all = bb.sync_local_backups_to_all_methods(
            local_data_dir=local_data_dir
        )
        method_results = list(sync_all.get("results", []) or [])
        if not method_results:
            warning_msg = str(
                sync_all.get("warning", "No enabled backup methods found.")
            )
            tlog(f"Cloud sync warning: {warning_msg}")
            self.info += (
                "\n### Cloud mirror status\n" f"**WARNING**: {warning_msg}\n"
            )
        else:
            self.info += "\n### Cloud mirror status\n"
            for result in method_results:
                method_name = str(result.get("method_name", "method"))
                provider = str(result.get("provider", "local_only"))
                ok = bool(result.get("ok", False))
                uploaded = int(result.get("uploaded", 0) or 0)
                updated = int(result.get("updated", 0) or 0)
                deleted = int(result.get("deleted", 0) or 0)
                cloud_count = int(result.get("cloud_total_count", 0) or 0)
                cloud_bytes = int(result.get("cloud_total_bytes", 0) or 0)
                query_ms = result.get("query_ms", None)
                warning_msg = str(result.get("warning", "") or "").strip()

                if ok:
                    tlog(
                        f"Cloud sync ok ({method_name}/{provider}): "
                        f"uploaded={uploaded}, updated={updated}, "
                        f"deleted={deleted}."
                    )
                    self.info += (
                        f"- **{method_name}** (`{provider}`): "
                        f"uploaded={uploaded}, updated={updated}, "
                        f"deleted={deleted}, cloud_files={cloud_count}, "
                        f"cloud_size={bb.format_bytes(cloud_bytes)}, "
                        f"query_ms={self._format_query_ms(query_ms)}\n"
                    )
                else:
                    tlog(
                        f"Cloud sync warning ({method_name}/{provider}): "
                        f'{warning_msg or "unknown warning"}'
                    )
                    self.info += (
                        f"- **WARNING** {method_name} (`{provider}`): "
                        f'{warning_msg or "sync failed"}\n'
                    )

            if not bool(sync_all.get("ok", True)):
                self.info += (
                    "\n**WARNING**: One or more backup methods were "
                    "skipped/failed. "
                    f'{str(sync_all.get("warning", "")).strip()}\n'
                )

        self.last_run = generated_at
        self.progress = 1.0
        tlog("LOCAL_DATA backup completed successfully.")

    @staticmethod
    def _validate_source_dir(source_dir: Path) -> None:
        if source_dir in {Path("/"), Path.home()}:
            raise ValueError(f"Unsafe backup source directory: {source_dir}")

        required_children = ["admin", "tasks", "users"]
        missing = [
            name
            for name in required_children
            if not (source_dir / name).exists()
        ]
        if missing:
            raise ValueError(
                "LOCAL_DATA_DIR does not look like an ARI data directory "
                f'(missing: {", ".join(missing)})'
            )

    @staticmethod
    def _format_csv_or_none(items: List[str]) -> str:
        """Return CSV from items or '(none)' when empty."""
        return ", ".join(items) if items else "(none)"

    @staticmethod
    def _format_query_ms(query_ms: Optional[int]) -> str:
        """Format query time for markdown status output."""
        return str(query_ms) if query_ms is not None else "n/a"

    @staticmethod
    def _create_or_replace_archive(
        source_dir: Path,
        destination: Path,
        exclude_dirs: List[str],
        exclude_paths: List[str],
    ) -> str:
        if not destination.exists():
            AperoLocalDataBackupTask._create_archive(
                source_dir, destination, exclude_dirs, exclude_paths
            )
            return "created"

        old_path = destination.with_name(destination.name + ".old")
        old_path.unlink(missing_ok=True)
        destination.replace(old_path)
        try:
            AperoLocalDataBackupTask._create_archive(
                source_dir, destination, exclude_dirs, exclude_paths
            )
        except Exception:
            destination.unlink(missing_ok=True)
            if old_path.exists():
                old_path.replace(destination)
            raise
        old_path.unlink(missing_ok=True)
        return "replaced"

    @staticmethod
    def _create_archive(
        source_dir: Path,
        destination: Path,
        exclude_dirs: List[str],
        exclude_paths: List[str],
    ) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(destination, "w:gz") as handle:
            for file_path in AperoLocalDataBackupTask._iter_source_files(
                source_dir, exclude_dirs, exclude_paths
            ):
                rel_path = file_path.relative_to(source_dir)
                arcname = Path(source_dir.name) / rel_path
                handle.add(file_path, arcname=str(arcname))

    @staticmethod
    def _iter_source_files(
        source_dir: Path, exclude_dirs: List[str], exclude_paths: List[str]
    ):
        excluded = set(exclude_dirs)
        excluded_paths = set(exclude_paths)
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            rel_parts = root_path.relative_to(source_dir).parts
            if rel_parts and rel_parts[0] in excluded:
                dirs[:] = []
                continue

            dirs[:] = [name for name in dirs if name not in excluded]
            for file_name in files:
                file_path = root_path / file_name
                rel_path = AperoLocalDataBackupTask._normalize_relative_path(
                    file_path.relative_to(source_dir)
                )
                if rel_path in excluded_paths:
                    continue
                yield file_path

    @staticmethod
    def _estimate_archive_input_size(
        source_dir: Path, exclude_dirs: List[str], exclude_paths: List[str]
    ) -> int:
        total = 0
        for file_path in AperoLocalDataBackupTask._iter_source_files(
            source_dir, exclude_dirs, exclude_paths
        ):
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
        return total

    @staticmethod
    def _format_bytes(size: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB"]
        value = float(size)
        for unit in units:
            if value < 1024.0 or unit == units[-1]:
                return f"{value:.2f} {unit}"
            value /= 1024.0
        return f"{size} B"

    @staticmethod
    def _normalize_relative_path(path_value: Any) -> str:
        parts = []
        for part in Path(str(path_value)).parts:
            if part in {"", "."}:
                continue
            if part == "..":
                return ""
            parts.append(part)
        return "/".join(parts)

    @staticmethod
    def _prune_archives(directory: Path, keep_count: int) -> List[Path]:
        if keep_count <= 0:
            paths = sorted(directory.glob("*.tar.gz"))
            for path in paths:
                path.unlink(missing_ok=True)
            return paths

        paths = sorted(
            directory.glob("*.tar.gz"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        removed: List[Path] = []
        for old_path in paths[keep_count:]:
            old_path.unlink(missing_ok=True)
            removed.append(old_path)
        return removed


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
