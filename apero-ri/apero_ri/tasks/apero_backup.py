#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI task for backing up LOCAL_DATA_DIR."""
import os
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from apero_ri.tasks import apero_async


ARI_DIR = Path.home() / '.ari'

PARAM_LIST = ['LOCAL_DATA_DIR', 'INSTRUMENT', 'TASK_CONFIG']
APERO_PROFILE_PARAM_LIST: List[str] = []


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
        instrument = str(params.get('INSTRUMENT', 'unknown'))
        task_cfg = dict(params.get('TASK_CONFIG', {}))

        daily_copies = max(int(task_cfg.get('daily_copies', 7) or 0), 0)
        weekly_copies = max(int(task_cfg.get('weekly_copies', 4) or 0), 0)
        if daily_copies == 0 and weekly_copies == 0:
            raise ValueError('At least one retained daily or weekly copy is required.')

        backup_root = local_data_dir / 'backups' / instrument
        daily_dir = backup_root / 'daily'
        weekly_dir = backup_root / 'weekly'
        daily_dir.mkdir(parents=True, exist_ok=True)
        weekly_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc)
        generated_at = timestamp.isoformat()
        time_tag = timestamp.strftime('%Y%m%dT%H%M%SZ')
        iso_week = timestamp.isocalendar()
        week_tag = f'{iso_week.year}W{iso_week.week:02d}'
        created_files: List[Path] = []

        self.info = (
            f'## Local Data Backup\n\n'
            f'**Source**: `{local_data_dir}`  \n'
            f'**Generated at**: {generated_at}  \n'
            f'**Daily copies**: {daily_copies}  \n'
            f'**Weekly copies**: {weekly_copies}\n'
        )

        if daily_copies > 0:
            daily_path = daily_dir / f'{local_data_dir.name}_{instrument}_{time_tag}.tar.gz'
            self._create_archive(local_data_dir, backup_root, daily_path)
            self.info += f'\n### Daily backup\nCreated `{daily_path.name}`\n'
            created_files.append(daily_path)
            self.progress = 0.5 if weekly_copies > 0 else 0.8

        if weekly_copies > 0:
            weekly_path = weekly_dir / f'{local_data_dir.name}_{instrument}_{week_tag}.tar.gz'
            self._create_archive(local_data_dir, backup_root, weekly_path)
            self.info += f'\n### Weekly backup\nCreated `{weekly_path.name}`\n'
            created_files.append(weekly_path)
            self.progress = 0.8

        pruned_daily = self._prune_archives(daily_dir, daily_copies)
        pruned_weekly = self._prune_archives(weekly_dir, weekly_copies)

        manifest_rows = []
        for path in created_files:
            manifest_rows.append({
                'type': 'created',
                'path': str(path),
                'size_bytes': path.stat().st_size,
            })
        for path in pruned_daily:
            manifest_rows.append({'type': 'pruned_daily', 'path': str(path)})
        for path in pruned_weekly:
            manifest_rows.append({'type': 'pruned_weekly', 'path': str(path)})

        manifest_path = backup_root / f'backup_manifest_{time_tag}.json'
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

        self.output_files = [str(manifest_path)] + [str(path) for path in created_files]
        self.info += f'\n### Manifest\nSaved `{manifest_path.name}`\n'
        if pruned_daily or pruned_weekly:
            self.info += '\n### Pruned copies\n'
            for path in pruned_daily + pruned_weekly:
                self.info += f'- `{path.name}`\n'
        self.last_run = generated_at
        self.progress = 1.0

    @staticmethod
    def _create_archive(source_dir: Path, backup_root: Path,
                        destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(destination, 'w:gz') as handle:
            for root, dirs, files in os.walk(source_dir):
                root_path = Path(root)
                if root_path == backup_root or backup_root in root_path.parents:
                    dirs[:] = []
                    continue
                rel_root = root_path.relative_to(source_dir)
                for file_name in files:
                    file_path = root_path / file_name
                    arcname = Path(source_dir.name) / rel_root / file_name
                    handle.add(file_path, arcname=str(arcname))

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