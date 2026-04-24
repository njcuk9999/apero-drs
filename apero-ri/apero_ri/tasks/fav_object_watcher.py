#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI - GLOBAL async task: fav-object .state watcher.

For each user with a ``favourite_objects.yaml`` file under
``{LOCAL_DATA_DIR}/users/<user>/`` the task scans every favourite
object's ``.state_<OBJ>.json`` file under
``{LOCAL_DATA_DIR}/tasks/<INSTRUMENT>/<profile>/objects/`` and
diffs a small set of monitored fields against a per-user snapshot
at ``{LOCAL_DATA_DIR}/users/<user>/.fav_state_snapshot.json``. Any
field change emits a notification via
``apero_ri.core.notifications.emit_notification`` on the
``fav_object`` channel.

Created on 2026-04-24

@author: cook
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.fav_object_watcher'

ARI_DIR = Path.home() / '.ari'

# Fields inside .state_<OBJ>.json we care about
WATCH_FIELDS: Tuple[str, ...] = (
    'last_obs_date',
    'n_obs',
    'last_run_id',
    'mtime',
    'qc_status',
)

# Module-level task metadata consumed by the registry
PARAM_LIST = ['LOCAL_DATA_DIR', 'TASK_CONFIG']
APERO_PROFILE_PARAM_LIST: List[str] = []
DEFAULT_FREQUENCY = 1.0       # hourly
DEFAULT_ENABLED = True
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = False
FILTERS: List[str] = []


# =============================================================================
# Helpers
# =============================================================================
def _load_yaml(path: Path) -> Optional[Dict[str, Any]]:
    if not _HAS_YAML or not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return _yaml.safe_load(fh) or {}
    except Exception:
        return None


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh) or {}
    except Exception:
        return None


def _save_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    try:
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink()
        except Exception:
            pass


def _list_users(users_dir: Path) -> List[str]:
    if not users_dir.exists():
        return []
    out: List[str] = []
    for child in sorted(users_dir.iterdir()):
        if child.is_dir():
            out.append(child.name)
    return out


def _load_fav_objects(user_dir: Path) -> List[Dict[str, Any]]:
    """Return list of {instrument, profile, objname} entries."""
    fav_path = user_dir / 'favourite_objects.yaml'
    data = _load_yaml(fav_path)
    if not data:
        return []
    raw = data.get('favourites') or data.get('objects') or data
    out: List[Dict[str, Any]] = []
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        items = raw.get('items') or []
    else:
        items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        inst = str(item.get('instrument') or '').strip()
        prof = str(
            item.get('profile') or item.get('profile_id') or '').strip()
        obj = str(
            item.get('objname') or item.get('apero_name') or '').strip()
        if not (inst and prof and obj):
            continue
        out.append({
            'instrument': inst,
            'profile': prof,
            'objname': obj,
        })
    return out


def _load_object_state(
    base_dir: Path, instrument: str, profile: str, objname: str,
) -> Optional[Dict[str, Any]]:
    state_path = (
        base_dir / 'tasks' / instrument / profile / 'objects'
        / f'.state_{objname}.json'
    )
    return _load_json(state_path)


def _diff_fields(
    prev: Optional[Dict[str, Any]],
    curr: Dict[str, Any],
) -> List[Tuple[str, Any, Any]]:
    """Return list of (field, old, new) for any WATCH_FIELDS that
    differ. If ``prev`` is None, returns []."""
    if not prev:
        return []
    changes: List[Tuple[str, Any, Any]] = []
    for field in WATCH_FIELDS:
        old = prev.get(field)
        new = curr.get(field)
        if old != new:
            changes.append((field, old, new))
    return changes


def _summarise_changes(changes: List[Tuple[str, Any, Any]]) -> str:
    bits = []
    for field, old, new in changes:
        bits.append(f'**{field}**: `{old}` → `{new}`')
    return '\n'.join('- ' + b for b in bits)


# =============================================================================
# Task class
# =============================================================================
class FavObjectWatcherTask(apero_async.AperoAsyncTask):
    """Watch favourite-object state files and emit notifications on
    change."""

    def __init__(self, status: str = 'pending') -> None:
        name = 'Favourite Object Watcher'
        description = (
            'Detect changes in favourite-object .state_<OBJ>.json '
            'files and emit notifications to subscribed users.'
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> None:
        """Scan every user's favourite objects and emit notifications
        for any change in WATCH_FIELDS since the last snapshot.
        """
        local_data_dir = Path(
            params.get('LOCAL_DATA_DIR', str(ARI_DIR))
        ).expanduser().resolve()

        task_logger = params.get('TASK_LOGGER')

        def tlog(message: str) -> None:
            if callable(task_logger):
                try:
                    task_logger(message)
                except Exception:
                    pass

        users_dir = local_data_dir / 'users'
        users = _list_users(users_dir)
        tlog(f'FAV_OBJECT_WATCHER scanning {len(users)} users')

        # Lazy import to avoid pulling notifications stack at module
        # import time (keeps the task registry resilient).
        try:
            from apero_ri.core import notifications as _notif
        except Exception as exc:  # noqa: BLE001
            tlog(f'notifications module unavailable: {exc}')
            self.info = (
                '## Favourite Object Watcher\n\n'
                f'Notifications module failed to import: `{exc}`\n'
            )
            return

        n_users_scanned = 0
        n_objects_scanned = 0
        n_notifications = 0
        n_first_seen = 0
        started = time.time()

        for user in users:
            user_dir = users_dir / user
            favs = _load_fav_objects(user_dir)
            if not favs:
                continue
            n_users_scanned += 1
            snap_path = user_dir / '.fav_state_snapshot.json'
            snapshot = _load_json(snap_path) or {}
            new_snapshot = dict(snapshot)
            for fav in favs:
                inst = fav['instrument']
                prof = fav['profile']
                obj = fav['objname']
                key = f'{inst}/{prof}/{obj}'
                state = _load_object_state(
                    local_data_dir, inst, prof, obj)
                if not state:
                    continue
                n_objects_scanned += 1
                # Project only watch fields
                projected = {
                    k: state.get(k) for k in WATCH_FIELDS
                }
                prev = snapshot.get(key)
                if prev is None:
                    n_first_seen += 1
                    new_snapshot[key] = projected
                    continue
                changes = _diff_fields(prev, projected)
                if not changes:
                    continue
                # emit notification
                title = f'Favourite object updated: {obj}'
                body = (
                    f'{obj} ({inst} / {prof}) changed:\n\n'
                    + _summarise_changes(changes)
                )
                url = (
                    f'/data-portal/object/{prof}/{obj}'
                )
                try:
                    _notif.emit_notification(
                        username=user,
                        channel='fav_object',
                        title=title,
                        body=body,
                        url=url,
                        meta={
                            'instrument': inst,
                            'profile': prof,
                            'objname': obj,
                            'changes': [
                                {'field': f, 'old': o, 'new': n}
                                for (f, o, n) in changes
                            ],
                        },
                    )
                    n_notifications += 1
                except Exception as exc:  # noqa: BLE001
                    tlog(
                        f'emit_notification failed for {user} {obj}'
                        f': {exc}')
                new_snapshot[key] = projected
            # Persist updated snapshot for this user
            if new_snapshot != snapshot:
                _save_json(new_snapshot, snap_path)

        dt_s = time.time() - started
        generated_at = datetime.now(timezone.utc).isoformat()
        self.info = (
            '## Favourite Object Watcher\n\n'
            f'**Generated at**: {generated_at}  \n'
            f'**Users scanned**: {n_users_scanned}  \n'
            f'**Objects scanned**: {n_objects_scanned}  \n'
            f'**Notifications emitted**: {n_notifications}  \n'
            f'**First-seen entries (no notif)**: {n_first_seen}  \n'
            f'**Elapsed**: {dt_s:.2f}s\n'
        )
        self.progress = 1.0


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('FavObjectWatcherTask module – import only.')

# =============================================================================
# End of code
# =============================================================================
