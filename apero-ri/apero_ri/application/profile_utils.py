"""Profile and DB helper functions for ARIApp."""

from typing import Any


def q_ident(name: str) -> str:
    """Quote SQL identifier path safely (schema/table)."""
    return ".".join(f"`{part}`" for part in name.split("."))


def profile_get_db(cfg: dict, key: str, default: Any = "") -> Any:
    """Get a DB key from nested ``database`` with flat fallback."""
    db_cfg = cfg.get("database", {}) if isinstance(cfg, dict) else {}
    if not isinstance(db_cfg, dict):
        db_cfg = {}
    if key in db_cfg:
        value = db_cfg.get(key)
        return default if value is None else value
    if isinstance(cfg, dict):
        value = cfg.get(key, default)
        return default if value is None else value
    return default


def profile_get_path(cfg: dict, key: str, default: Any = "") -> Any:
    """Get a path key from nested ``paths`` with flat fallback."""
    paths_cfg = cfg.get("paths", {}) if isinstance(cfg, dict) else {}
    if not isinstance(paths_cfg, dict):
        paths_cfg = {}
    if key in paths_cfg:
        value = paths_cfg.get(key)
        return default if value is None else value
    if isinstance(cfg, dict):
        value = cfg.get(key, default)
        return default if value is None else value
    return default


def profile_get_general(cfg: dict, key: str, default: Any = "") -> Any:
    """Get a general key from nested ``general`` with flat fallback."""
    general_cfg = cfg.get("general", {}) if isinstance(cfg, dict) else {}
    if not isinstance(general_cfg, dict):
        general_cfg = {}
    if key in general_cfg:
        value = general_cfg.get(key)
        return default if value is None else value
    if isinstance(cfg, dict):
        value = cfg.get(key, default)
        return default if value is None else value
    return default
