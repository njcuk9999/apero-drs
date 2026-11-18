#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Config YAML saves must never expose an empty file to readers."""
import threading
import time
from pathlib import Path

from apero_ri.core import auth


# =============================================================================
# Define functions
# =============================================================================
def test_async_tasks_never_read_empty_during_save(monkeypatch,
                                                  tmp_path: Path) -> None:
    """Concurrent loads always see a complete async_tasks.yaml."""
    monkeypatch.setattr(auth, 'ASYNC_TASKS_FILE',
                        tmp_path / 'async_tasks' / 'async_tasks.yaml')
    monkeypatch.setattr(auth, 'ensure_ari_directory', lambda: None)
    rows = [dict(id=f'id{i}', task_key=f'K{i}', active=True, order=i)
            for i in range(40)]
    tasks = {'__GLOBAL__': rows}
    auth.save_async_tasks(tasks)
    stop = threading.Event()

    def writer() -> None:
        """Save the same tasks repeatedly until stopped."""
        while not stop.is_set():
            auth.save_async_tasks(tasks)

    threads = [threading.Thread(target=writer) for _ in range(2)]
    for thread in threads:
        thread.start()
    bad = 0
    start = time.time()
    try:
        while time.time() - start < 1.0:
            data = auth.load_async_tasks()
            if len(data.get('__GLOBAL__', [])) != len(rows):
                bad += 1
    finally:
        stop.set()
        for thread in threads:
            thread.join()
    assert bad == 0
    # No temporary files are left behind.
    leftovers = list(auth.ASYNC_TASKS_FILE.parent.glob('*.tmp'))
    assert leftovers == []


def test_atomic_write_keeps_permissions(tmp_path: Path) -> None:
    """Replacing a credentials file keeps its restrictive permissions."""
    path = tmp_path / 'db_access.yaml'
    path.write_text('old: 1\n', encoding='utf-8')
    path.chmod(0o600)
    auth._write_yaml_atomic(path, dict(new=2))
    assert path.read_text(encoding='utf-8') == 'new: 2\n'
    assert path.stat().st_mode & 0o777 == 0o600
