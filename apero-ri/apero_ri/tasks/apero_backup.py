#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI task for backing up LOCAL_DATA_DIR."""
import os
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from apero_ri.tasks import apero_async


# =============================================================================
# Define variables
# =============================================================================
# Set AIR local data directory
ARI_DIR = Path.home() / '.ari'
# Set the list of parameters required for this task
PARAM_LIST = ['LOCAL_DATA_DIR', 'INSTRUMENT', 'TASK_CONFIG']
# Set the list of APERO profile parameters that this task depends on (if any)
APERO_PROFILE_PARAM_LIST: List[str] = []
# Maximum allowed size for one backup archive input (bytes)
BACKUP_MAX_SIZE = 1024 ** 3
# Set the default frequency for this task (in hours)
DEFAULT_FREQUENCY = 6.0
# Set whether this task is enabled by default in the admin portal
DEFAULT_ENABLED = True
# Set the type of task (INSTRUMENT, GLOBAL)
TASK_TYPE = 'GLOBAL'


# =============================================================================
# Define global classes
# =============================================================================
class AperoLocalDataBackupTask(apero_async.AperoAsyncTask):
    """Create retained daily and weekly backups of LOCAL_DATA_DIR."""

    def __init__(self, status='pending'):
        name = 'Local Data Backup Task'
        description = ('Create compressed backups of LOCAL_DATA_DIR and keep '
                       'daily / weekly retained copies.')
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]):
        local_data_dir = Path(
            params.get('LOCAL_DATA_DIR', str(ARI_DIR))
        ).expanduser().resolve()
        task_cfg = dict(params.get('TASK_CONFIG', {}))

        self._validate_source_dir(local_data_dir)

        estimated_size = self._estimate_archive_input_size(local_data_dir)
        if estimated_size > BACKUP_MAX_SIZE:
            warning_msg = (
                'Backup skipped: estimated archive input size '
                f'({self._format_bytes(estimated_size)}) exceeds BACKUP_MAX_SIZE '
                f'({self._format_bytes(BACKUP_MAX_SIZE)}).'
            )
            print(f'WARNING: {warning_msg}')
            self.info = f'## Local Data Backup\n\n**WARNING**: {warning_msg}\n'
            self.progress = 1.0
            raise ValueError(warning_msg)

        daily_copies = max(int(task_cfg.get('daily_copies', 7) or 0), 0)
        weekly_copies = max(int(task_cfg.get('weekly_copies', 4) or 0), 0)
        if daily_copies == 0 and weekly_copies == 0:
            raise ValueError('At least one retained daily or weekly copy is required.')

        backup_root = local_data_dir / 'backups'
        daily_dir = backup_root / 'daily'
        weekly_dir = backup_root / 'weekly'
        daily_dir.mkdir(parents=True, exist_ok=True)
        weekly_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc)
        generated_at = timestamp.isoformat()
        time_tag = timestamp.strftime('%Y%m%dT%H%M%SZ')
        day_tag = timestamp.strftime('%Y%m%d')
        iso_week = timestamp.isocalendar()
        week_tag = f'{iso_week.year}W{iso_week.week:02d}'
        archive_files: List[Path] = []
        archive_actions: Dict[Path, str] = {}

        # Reset info to empty string so this run's content doesn't accumulate with prior runs
        self.info = ''
        self.info = (
            f'## Local Data Backup\n\n'
            f'**Source**: `{local_data_dir}`  \n'
            f'**Generated at**: {generated_at}  \n'
            f'**Daily copies**: {daily_copies}  \n'
            f'**Weekly copies**: {weekly_copies}\n'
        )

        if daily_copies > 0:
            daily_path = daily_dir / f'{local_data_dir.name}_{day_tag}.tar.gz'
            daily_action = self._create_or_replace_archive(local_data_dir, daily_path)
            if daily_action == 'created':
                self.info += f'\n### Daily backup\nCreated `{daily_path.name}`\n'
            else:
                self.info += f'\n### Daily backup\nReplaced `{daily_path.name}`\n'
            archive_files.append(daily_path)
            archive_actions[daily_path] = daily_action
            self.progress = 0.5 if weekly_copies > 0 else 0.8

        if weekly_copies > 0:
            weekly_path = weekly_dir / f'{local_data_dir.name}_{week_tag}.tar.gz'
            weekly_action = self._create_or_replace_archive(local_data_dir, weekly_path)
            if weekly_action == 'created':
                self.info += f'\n### Weekly backup\nCreated `{weekly_path.name}`\n'
            else:
                self.info += f'\n### Weekly backup\nReplaced `{weekly_path.name}`\n'
            archive_files.append(weekly_path)
            archive_actions[weekly_path] = weekly_action
            self.progress = 0.8

        pruned_daily = self._prune_archives(daily_dir, daily_copies)
        pruned_weekly = self._prune_archives(weekly_dir, weekly_copies)

        manifest_rows = []
        for path in archive_files:
            manifest_rows.append({
                'type': archive_actions.get(path, 'created'),
                'path': str(path),
                'size_bytes': path.stat().st_size,
            })
        for path in pruned_daily:
            manifest_rows.append({'type': 'pruned_daily', 'path': str(path)})
        for path in pruned_weekly:
            manifest_rows.append({'type': 'pruned_weekly', 'path': str(path)})

        manifest_path = backup_root / 'backup_manifest.json'
        apero_async.save_results(
            manifest_path,
            manifest_rows,
            metadata={
                'GENERATED_AT': generated_at,
                'SOURCE_DIR': str(local_data_dir),
                'DAILY_COPIES': daily_copies,
                'WEEKLY_COPIES': weekly_copies,
            },
        )

        self.output_files = [str(manifest_path)] + [str(path) for path in archive_files]
        self.info += f'\n### Manifest\nSaved `{manifest_path.name}`\n'
        if pruned_daily or pruned_weekly:
            self.info += '\n### Pruned copies\n'
            for path in pruned_daily + pruned_weekly:
                self.info += f'- `{path.name}`\n'
        self.last_run = generated_at
        self.progress = 1.0

    @staticmethod
    def _validate_source_dir(source_dir: Path) -> None:
        if source_dir in {Path('/'), Path.home()}:
            raise ValueError(f'Unsafe backup source directory: {source_dir}')

        required_children = ['admin', 'tasks', 'users']
        missing = [name for name in required_children if not (source_dir / name).exists()]
        if missing:
            raise ValueError(
                'LOCAL_DATA_DIR does not look like an ARI data directory '
                f'(missing: {", ".join(missing)})'
            )

    @staticmethod
    def _create_or_replace_archive(source_dir: Path, destination: Path) -> str:
        if not destination.exists():
            AperoLocalDataBackupTask._create_archive(source_dir, destination)
            return 'created'

        old_path = destination.with_name(destination.name + '.old')
        old_path.unlink(missing_ok=True)
        destination.replace(old_path)
        try:
            AperoLocalDataBackupTask._create_archive(source_dir, destination)
        except Exception:
            destination.unlink(missing_ok=True)
            if old_path.exists():
                old_path.replace(destination)
            raise
        old_path.unlink(missing_ok=True)
        return 'replaced'

    @staticmethod
    def _create_archive(source_dir: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(destination, 'w:gz') as handle:
            for file_path in AperoLocalDataBackupTask._iter_source_files(source_dir):
                rel_path = file_path.relative_to(source_dir)
                arcname = Path(source_dir.name) / rel_path
                handle.add(file_path, arcname=str(arcname))

    @staticmethod
    def _iter_source_files(source_dir: Path):
        backups_dir = source_dir / 'backups'
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            if root_path == backups_dir or backups_dir in root_path.parents:
                dirs[:] = []
                continue
            for file_name in files:
                yield root_path / file_name

    @staticmethod
    def _estimate_archive_input_size(source_dir: Path) -> int:
        total = 0
        for file_path in AperoLocalDataBackupTask._iter_source_files(source_dir):
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
        return total

    @staticmethod
    def _format_bytes(size: int) -> str:
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        value = float(size)
        for unit in units:
            if value < 1024.0 or unit == units[-1]:
                return f'{value:.2f} {unit}'
            value /= 1024.0
        return f'{size} B'

    @staticmethod
    def _prune_archives(directory: Path, keep_count: int) -> List[Path]:
        if keep_count <= 0:
            paths = sorted(directory.glob('*.tar.gz'))
            for path in paths:
                path.unlink(missing_ok=True)
            return paths

        paths = sorted(
            directory.glob('*.tar.gz'),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        removed: List[Path] = []
        for old_path in paths[keep_count:]:
            old_path.unlink(missing_ok=True)
            removed.append(old_path)
        return removed