"""Helpers for storing sensitive runtime files outside normal backups."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterable


def get_ari_dir() -> Path:
    """Return the configured ARI data directory."""
    return Path(os.environ.get('ARI_DIR', os.path.expanduser('~/.ari'))).expanduser().resolve()


def get_secret_dir() -> Path:
    """Return the managed secret directory under ARI_DIR."""
    path = get_ari_dir() / 'secret'
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass
    return path


def get_secret_path(*parts: str, create_parent: bool = True) -> Path:
    """Return a path inside the managed secret directory."""
    path = get_secret_dir().joinpath(*parts)
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def protect_path(path: Path, mode: int = 0o600) -> Path:
    """Best-effort permission hardening for a secret file or directory."""
    try:
        path.chmod(mode)
    except OSError:
        pass
    return path


def _unique_paths(paths: Iterable[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        resolved = Path(path).expanduser().resolve()
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        unique.append(resolved)
    return unique


def resolve_secret_file(name: str,
                        legacy_paths: Iterable[Path] = (),
                        mode: int = 0o600) -> Path:
    """Return a managed secret file path, moving any legacy file into place."""
    target = get_secret_path(name)
    if target.exists():
        return protect_path(target, mode)

    for legacy in _unique_paths(legacy_paths):
        if legacy == target or not legacy.exists() or legacy.is_dir():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(legacy), str(target))
        except Exception:
            shutil.copy2(legacy, target)
            try:
                legacy.unlink()
            except OSError:
                pass
        return protect_path(target, mode)

    return target


def resolve_secret_subdir(name: str,
                          legacy_paths: Iterable[Path] = (),
                          mode: int = 0o700) -> Path:
    """Return a managed secret subdirectory, moving legacy contents if needed."""
    target = get_secret_path(name)
    target.mkdir(parents=True, exist_ok=True)

    for legacy in _unique_paths(legacy_paths):
        if legacy == target or not legacy.exists() or not legacy.is_dir():
            continue
        for child in legacy.iterdir():
            dest = target / child.name
            if dest.exists():
                continue
            try:
                shutil.move(str(child), str(dest))
            except Exception:
                if child.is_dir():
                    shutil.copytree(child, dest)
                    shutil.rmtree(child, ignore_errors=True)
                else:
                    shutil.copy2(child, dest)
                    try:
                        child.unlink()
                    except OSError:
                        pass
        try:
            legacy.rmdir()
        except OSError:
            pass

    return protect_path(target, mode)