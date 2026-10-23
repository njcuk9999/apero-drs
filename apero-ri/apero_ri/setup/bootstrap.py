#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bootstrap helpers for first-run APERO RI setup."""

import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import yaml

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.setup.bootstrap"
BOOTSTRAP_FILE = Path.home() / ".apero_ri_bootstrap.yaml"
LEGACY_LOCAL_USER = "njcuk9999"


# =============================================================================
# Define functions
# =============================================================================
def _default_data_dir() -> Path:
    return Path.home() / ".ari"


def load_bootstrap_config() -> Dict[str, Any]:
    if not BOOTSTRAP_FILE.exists():
        return {}
    try:
        with open(BOOTSTRAP_FILE, "r", encoding="utf-8") as fobj:
            data = yaml.safe_load(fobj) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_bootstrap_config(local_data_dir: str) -> None:
    BOOTSTRAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "local_data_dir": str(Path(local_data_dir).expanduser()),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(BOOTSTRAP_FILE, "w", encoding="utf-8") as fobj:
        yaml.safe_dump(
            payload, fobj, default_flow_style=False, allow_unicode=True
        )


def resolve_local_data_dir(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env_path = os.environ.get("ARI_DIR", "").strip()
    if env_path:
        return Path(env_path).expanduser()
    cfg = load_bootstrap_config()
    cfg_path = str(cfg.get("local_data_dir", "")).strip()
    if cfg_path:
        return Path(cfg_path).expanduser()
    return _default_data_dir()


def get_setup_state_path(local_data_dir: Path) -> Path:
    return Path(local_data_dir).expanduser() / "admin" / "setup_state.yaml"


def load_setup_state(local_data_dir: Path) -> Dict[str, Any]:
    path = get_setup_state_path(local_data_dir)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fobj:
            data = yaml.safe_load(fobj) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_setup_state(
    local_data_dir: Path, admin_username: str, email_configured: bool = True
) -> None:
    path = get_setup_state_path(local_data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "completed": True,
        "admin_username": admin_username,
        "email_configured": bool(email_configured),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(path, "w", encoding="utf-8") as fobj:
        yaml.safe_dump(
            payload, fobj, default_flow_style=False, allow_unicode=True
        )


def is_setup_complete(local_data_dir: Path) -> bool:
    state = load_setup_state(local_data_dir)
    return bool(state.get("completed", False))


def _load_yaml_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fobj:
            data = yaml.safe_load(fobj) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def get_users_file(local_data_dir: Path) -> Path:
    admin_dir = Path(local_data_dir).expanduser() / "admin"
    new_path = admin_dir / "general" / "users.yaml"
    legacy_path = admin_dir / "users.yaml"
    return (
        new_path
        if new_path.exists() or not legacy_path.exists()
        else legacy_path
    )


def get_email_file(local_data_dir: Path) -> Path:
    admin_dir = Path(local_data_dir).expanduser() / "admin"
    new_path = admin_dir / "email" / "email.yaml"
    legacy_path = admin_dir / "email.yaml"
    return (
        new_path
        if new_path.exists() or not legacy_path.exists()
        else legacy_path
    )


def has_admin_user(
    local_data_dir: Path, preferred_username: Optional[str] = None
) -> bool:
    users = _load_yaml_file(get_users_file(local_data_dir))
    if preferred_username and preferred_username in users:
        groups = users.get(preferred_username, {}).get("groups", [])
        return ("admin" in groups) or ("super_admin" in groups)
    for user_data in users.values():
        if isinstance(user_data, dict) and (
            ("admin" in user_data.get("groups", []))
            or ("super_admin" in user_data.get("groups", []))
        ):
            return True
    return False


def is_legacy_local_install(local_data_dir: Path) -> bool:
    users = _load_yaml_file(get_users_file(local_data_dir))
    email_cfg = _load_yaml_file(get_email_file(local_data_dir))
    if LEGACY_LOCAL_USER not in users:
        return False
    legacy_user = users.get(LEGACY_LOCAL_USER, {})
    if ("admin" not in legacy_user.get("groups", [])) and (
        "super_admin" not in legacy_user.get("groups", [])
    ):
        return False
    if not str(legacy_user.get("primary_email", "")).strip():
        return False
    return bool(email_cfg.get("enabled", False))


def can_start_main_app(local_data_dir: Path) -> bool:
    return is_setup_complete(local_data_dir) or is_legacy_local_install(
        local_data_dir
    )


def ensure_directory_layout(local_data_dir: Path) -> None:
    base = Path(local_data_dir).expanduser()
    paths = [
        base,
        base / "admin",
        base / "admin" / "instruments",
        base / "backups",
        base / "secret",
        base / "tasks",
        base / "users",
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)

    probe = base / ".write_test.tmp"
    with open(probe, "w", encoding="utf-8") as fobj:
        fobj.write("ok")
    probe.unlink()


def _port_pids(port: int) -> List[int]:
    """
    Return pids of processes with a socket on a TCP port.

    :param port: int, TCP port

    :return: sorted list of pids (excluding this process)
    :rtype: list
    """
    pids = set()
    try:
        conns = psutil.net_connections(kind="tcp")
    except psutil.AccessDenied:
        conns = []
        # without system-wide access, only our own processes are visible
        for proc in psutil.process_iter():
            try:
                for conn in proc.net_connections(kind="tcp"):
                    if conn.laddr and conn.laddr.port == port:
                        pids.add(proc.pid)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
    for conn in conns:
        if conn.laddr and conn.laddr.port == port and conn.pid:
            pids.add(conn.pid)
    pids.discard(os.getpid())
    return sorted(pids)


def _port_free(port: int) -> bool:
    """
    Return True if a TCP port can be bound on all interfaces.

    :param port: int, TCP port

    :return: bool
    :rtype: bool
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # match the server: TIME_WAIT leftovers do not block a restart
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", port))
        except OSError:
            return False
    return True


def free_port(port: int, timeout: float = 10.0) -> bool:
    """
    Terminate (then kill) processes holding a TCP port.

    Only processes owned by the current user are touched; others are
    reported so they can be stopped manually.

    :param port: int, TCP port to release
    :param timeout: float, seconds to wait for processes / the port

    :return: bool, True if the port is free afterwards
    :rtype: bool
    """
    me = psutil.Process().username()
    procs = []
    for pid in _port_pids(port):
        try:
            proc = psutil.Process(pid)
            cmd = " ".join(proc.cmdline()) or proc.name()
            owner = proc.username()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if owner != me:
            print(f"Port {port}: pid {pid} belongs to {owner}, not "
                  f"killing it: {cmd}")
            continue
        print(f"Port {port}: stopping pid {pid}: {cmd}")
        procs.append(proc)
    for proc in procs:
        try:
            proc.terminate()
        except psutil.NoSuchProcess:
            pass
    _, alive = psutil.wait_procs(procs, timeout=timeout / 2)
    for proc in alive:
        print(f"Port {port}: pid {proc.pid} ignored SIGTERM, killing it")
        try:
            proc.kill()
        except psutil.NoSuchProcess:
            pass
    psutil.wait_procs(alive, timeout=timeout / 2)
    if not procs:
        print(f"Port {port}: no process of yours is using it")
    deadline = time.time() + timeout
    while not _port_free(port):
        if time.time() > deadline:
            print(f"Port {port}: still in use")
            return False
        time.sleep(0.25)
    return True


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
