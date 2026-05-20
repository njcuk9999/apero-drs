#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Interactive PTY-based SSH/SSHFS session manager.

Spawns SSH or SSHFS processes inside pseudo-terminals so that password
prompts, Duo 2FA challenges, and other interactive authentication can
be relayed to the browser and answered by the admin user.

Sessions are short-lived (configurable timeout), identified by an opaque
token, and cleaned up automatically.
"""

# =============================================================================
# Imports
# =============================================================================
from __future__ import annotations

import errno
import fcntl
import os
import secrets
import shlex
import struct
import termios
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = "apero_ri.core.sshfs_interactive"

# Maximum time (seconds) a session can remain idle before auto-cleanup.
SESSION_IDLE_TIMEOUT = 120
# Maximum absolute lifetime of any session.
SESSION_MAX_LIFETIME = 300
# How often the reaper thread checks for expired sessions.
REAPER_INTERVAL = 10
# Maximum output buffer size per session (bytes).
OUTPUT_BUFFER_MAX = 65536


# =============================================================================
# Session class
# =============================================================================
@dataclass
class InteractiveSession:
    """Represents a single PTY-backed subprocess session."""

    token: str
    pid: int
    fd: int  # master side of the PTY
    kind: str  # 'ssh_test' | 'sshfs_mount'
    mount_name: str  # empty for test sessions
    created_at: float = field(default_factory=time.monotonic)
    last_activity: float = field(default_factory=time.monotonic)
    output_buffer: bytearray = field(default_factory=bytearray)
    read_cursor: int = 0  # how far the client has consumed
    finished: bool = False
    exit_code: Optional[int] = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def touch(self):
        self.last_activity = time.monotonic()


# =============================================================================
# Session store (module-level singleton)
# =============================================================================
_sessions: Dict[str, InteractiveSession] = {}
_sessions_lock = threading.Lock()
_reaper_started = False


def _start_reaper():
    """Start the background reaper thread (once)."""
    global _reaper_started
    if _reaper_started:
        return
    _reaper_started = True
    t = threading.Thread(
        target=_reaper_loop, daemon=True, name="sshfs-pty-reaper"
    )
    t.start()


def _reaper_loop():
    """Periodically clean up expired sessions."""
    while True:
        time.sleep(REAPER_INTERVAL)
        now = time.monotonic()
        with _sessions_lock:
            expired = [
                token
                for token, s in _sessions.items()
                if (
                    now - s.last_activity > SESSION_IDLE_TIMEOUT
                    or now - s.created_at > SESSION_MAX_LIFETIME
                )
            ]
        for token in expired:
            close_session(token)


# =============================================================================
# PTY reader thread
# =============================================================================
def _reader_thread(session: InteractiveSession):
    """Read output from the PTY master fd and append to the session buffer."""
    fd = session.fd
    while True:
        try:
            data = os.read(fd, 4096)
        except OSError as exc:
            if exc.errno in (errno.EIO, errno.EBADF):
                break
            continue
        if not data:
            break
        with session.lock:
            session.output_buffer.extend(data)
            # Trim if too large (keep tail)
            if len(session.output_buffer) > OUTPUT_BUFFER_MAX:
                excess = len(session.output_buffer) - OUTPUT_BUFFER_MAX
                del session.output_buffer[:excess]
                session.read_cursor = max(0, session.read_cursor - excess)
            session.touch()

    # Process has likely exited — collect exit status
    try:
        _, status = os.waitpid(session.pid, os.WNOHANG)
        session.exit_code = (
            os.WEXITSTATUS(status) if os.WIFEXITED(status) else -1
        )
    except ChildProcessError:
        session.exit_code = -1
    session.finished = True


# =============================================================================
# Public API
# =============================================================================
def start_session(
    kind: str,
    cmd: List[str],
    mount_name: str = "",
    env_extra: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Fork a new PTY-backed process for *cmd*.

    :param kind: 'ssh_test' or 'sshfs_mount'
    :param cmd: command + args list (e.g. ['ssh', '-i', ...])
    :param mount_name: associated mount name (for sshfs_mount kind)
    :param env_extra: optional extra environment variables
    :return: dict with 'ok', 'token', etc.
    """
    _start_reaper()

    # Limit concurrent sessions
    with _sessions_lock:
        if len(_sessions) >= 5:
            return {
                "ok": False,
                "error": "Too many active interactive sessions.",
            }

    token = secrets.token_urlsafe(24)

    # Build a sanitised environment
    child_env = dict(os.environ)
    child_env["TERM"] = "dumb"
    if env_extra:
        child_env.update(env_extra)

    try:
        pid, fd = os.forkpty()
    except OSError as exc:
        return {"ok": False, "error": f"Failed to create PTY: {exc}"}

    if pid == 0:
        # ── child process ──
        try:
            os.execvpe(cmd[0], cmd, child_env)
        except Exception:
            os._exit(127)

    # ── parent process ──
    # Make the master fd non-blocking for reads
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    session = InteractiveSession(
        token=token,
        pid=pid,
        fd=fd,
        kind=kind,
        mount_name=mount_name,
    )

    with _sessions_lock:
        _sessions[token] = session

    # Start reader thread
    reader = threading.Thread(
        target=_reader_thread,
        args=(session,),
        daemon=True,
        name=f"pty-reader-{token[:8]}",
    )
    reader.start()

    return {"ok": True, "token": token}


def poll_session(token: str) -> Dict[str, Any]:
    """
    Return new output since the last poll, plus session status.

    :return: dict with 'ok', 'output' (str), 'finished', 'exit_code'
    """
    with _sessions_lock:
        session = _sessions.get(token)
    if not session:
        return {"ok": False, "error": "Session not found or expired."}

    with session.lock:
        session.touch()
        new_data = bytes(session.output_buffer[session.read_cursor:])
        session.read_cursor = len(session.output_buffer)

    # Decode, replacing non-UTF-8 bytes
    text = new_data.decode("utf-8", errors="replace")
    # Strip common ANSI escape sequences for cleaner browser display
    import re

    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    text = re.sub(r"\x1b\].*?\x07", "", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    return {
        "ok": True,
        "output": text,
        "finished": session.finished,
        "exit_code": session.exit_code,
    }


def send_input(token: str, data: str) -> Dict[str, Any]:
    """
    Send keystrokes to the PTY process.

    :param data: text to write (caller appends \\n for Enter)
    :return: dict with 'ok'
    """
    with _sessions_lock:
        session = _sessions.get(token)
    if not session:
        return {"ok": False, "error": "Session not found or expired."}

    if session.finished:
        return {"ok": False, "error": "Session has already exited."}

    try:
        os.write(session.fd, data.encode("utf-8"))
        with session.lock:
            session.touch()
        return {"ok": True}
    except OSError as exc:
        return {"ok": False, "error": f"Write failed: {exc}"}


def close_session(token: str) -> Dict[str, Any]:
    """
    Terminate and clean up an interactive session.
    """
    with _sessions_lock:
        session = _sessions.pop(token, None)
    if not session:
        return {"ok": True, "message": "Session already closed."}

    # Kill the child process
    import signal

    try:
        os.kill(session.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass

    # Close the PTY master fd
    try:
        os.close(session.fd)
    except OSError:
        pass

    # Reap the child
    try:
        os.waitpid(session.pid, os.WNOHANG)
    except ChildProcessError:
        pass

    return {"ok": True, "message": "Session closed."}


def close_all_sessions() -> Dict[str, Any]:
    """Terminate and clean up all active interactive sessions."""
    with _sessions_lock:
        tokens = list(_sessions.keys())

    for token in tokens:
        close_session(token)

    return {
        "ok": True,
        "closed": len(tokens),
    }


def list_sessions() -> List[Dict[str, Any]]:
    """Return summary of active sessions (for debugging)."""
    now = time.monotonic()
    with _sessions_lock:
        return [
            {
                "token": s.token[:8] + "...",
                "kind": s.kind,
                "mount_name": s.mount_name,
                "age_seconds": round(now - s.created_at, 1),
                "idle_seconds": round(now - s.last_activity, 1),
                "finished": s.finished,
            }
            for s in _sessions.values()
        ]


# =============================================================================
# High-level helpers for SSHFS management
# =============================================================================
def start_interactive_test(
    connection_mode: str,
    remote_host: str,
    remote_user: str,
    ssh_config_host: str,
    remote_path: str,
    ssh_key_name: str,
) -> Dict[str, Any]:
    """
    Start an interactive SSH test session (PTY-backed).

    Unlike the non-interactive test_ssh_connection(), this allows
    the user to respond to password/2FA prompts in the browser.
    """
    from apero_ri.core.sshfs_backend import (
        _get_ssh_keys_dir,
        _normalize_connection_mode,
        _throttle_ssh_target,
    )

    connection_mode = _normalize_connection_mode(connection_mode)
    remote_host = str(remote_host or "").strip()
    remote_user = str(remote_user or "").strip() or "root"
    ssh_config_host = str(ssh_config_host or "").strip()
    remote_path = str(remote_path or "").strip()
    ssh_key_name = str(ssh_key_name or "").strip()

    if not ssh_key_name:
        return {"ok": False, "error": "SSH key is required."}

    key_path = _get_ssh_keys_dir() / f"{ssh_key_name}.key"
    if not key_path.exists():
        return {"ok": False, "error": f'SSH key "{ssh_key_name}" not found.'}

    if connection_mode == "ssh_config_host":
        if not ssh_config_host:
            return {"ok": False, "error": "SSH config host is required."}
        target = ssh_config_host
    else:
        if not remote_host:
            return {"ok": False, "error": "Remote host is required."}
        target = f"{remote_user}@{remote_host}"

    throttle_error = _throttle_ssh_target(target, action="interactive SSH test")
    if throttle_error:
        return {"ok": False, "error": throttle_error}

    # Build a multi-step test command:
    # 1) echo SSH_OK (proves login)
    # 2) if remote_path provided, test -d and ls | head -1
    if remote_path:
        remote_cmd = (
            "echo SSH_OK && "
            f"test -d {shlex.quote(remote_path)} && "
            f"echo PATH_OK && "
            f"ls -1 {shlex.quote(remote_path)} 2>/dev/null | head -1"
        )
    else:
        remote_cmd = "echo SSH_OK"

    cmd = [
        "ssh",
        "-i",
        str(key_path),
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=15",
        "-t",
        "-t",  # force PTY allocation
        target,
        remote_cmd,
    ]

    result = start_session(kind="ssh_test", cmd=cmd)
    if result.get("ok"):
        result["cmd"] = shlex.join(cmd)
    return result


def start_interactive_mount(mount_name: str) -> Dict[str, Any]:
    """
    Start an interactive SSHFS mount session (PTY-backed).

    This allows responding to password/2FA prompts for the mount.
    Without ``-f`` sshfs will daemonize after successful authentication,
    causing the PTY child to exit (code 0) while the FUSE mount
    persists via the background daemon – the same pattern used by
    ``start_interactive_ssh_tunnel()`` for database tunnels.
    """
    from apero_ri.core.sshfs_backend import (
        _get_ssh_keys_dir,
        _resolve_connection_target,
        _throttle_ssh_target,
        load_sshfs_config,
        save_sshfs_config,
    )

    cfg = load_sshfs_config()
    mount = next(
        (m for m in cfg.get("mounts", []) if m.get("name") == mount_name),
        None,
    )
    if not mount:
        return {"ok": False, "error": f'Mount "{mount_name}" not found.'}

    if mount.get("status") == "mounted":
        import subprocess as _sp

        local_mount_path = mount.get("local_mount", "")
        mq = _sp.run(
            ["mountpoint", "-q", local_mount_path],
            capture_output=True,
            timeout=5,
        )
        if mq.returncode == 0:
            return {
                "ok": True,
                "message": f'Mount "{mount_name}" is already mounted.',
            }
        # Stale config — reset and continue with mount
        mount["status"] = "unmounted"
        mount["mounted_at"] = None
        save_sshfs_config(cfg)

    ssh_key = mount.get("ssh_key", "")
    key_path = _get_ssh_keys_dir() / f"{ssh_key}.key"
    if not key_path.exists():
        return {"ok": False, "error": f'SSH key "{ssh_key}" not found.'}

    local_mount = Path(mount.get("local_mount", ""))
    from apero_ri.core.sshfs_backend import _prepare_mount_dir

    prep_log: list = []
    try:
        _prepare_mount_dir(local_mount, prep_log)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Cannot prepare mount directory: {exc}",
            "log": prep_log,
        }

    target_info = _resolve_connection_target(mount)
    remote_target = target_info["sshfs_target"]
    if not remote_target:
        return {"ok": False, "error": "Mount target is incomplete."}

    throttle_error = _throttle_ssh_target(
        target_info.get("display_target", ""),
        action=f"interactive mount {mount_name}",
    )
    if throttle_error:
        return {"ok": False, "error": throttle_error}

    # sshfs command WITHOUT BatchMode — allows interactive auth.
    # No -f flag: sshfs daemonizes after auth succeeds, so the PTY
    # child exits (code 0) while the FUSE mount persists.
    cmd = [
        "sshfs",
        "-o",
        f"IdentityFile={key_path}",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=15",
        "-o",
        "ServerAliveInterval=15,ServerAliveCountMax=3",
        remote_target,
        str(local_mount),
    ]

    result = start_session(kind="sshfs_mount", cmd=cmd, mount_name=mount_name)
    if result.get("ok"):
        result["cmd"] = shlex.join(cmd)
        if prep_log:
            result["prep_log"] = prep_log
    return result


def finalise_interactive_mount(mount_name: str) -> Dict[str, Any]:
    """
    After an interactive mount session succeeds mark it as mounted.

    Called once the health-check or mountpoint -q confirms the mount
    is actually live.
    """
    from datetime import datetime, timezone

    from apero_ri.core.sshfs_backend import load_sshfs_config, save_sshfs_config

    cfg = load_sshfs_config()
    mount = next(
        (m for m in cfg.get("mounts", []) if m.get("name") == mount_name),
        None,
    )
    if not mount:
        return {"ok": False, "error": f'Mount "{mount_name}" not found.'}

    mount["status"] = "mounted"
    mount["mounted_at"] = datetime.now(tz=timezone.utc).isoformat()
    save_sshfs_config(cfg)
    return {"ok": True, "message": f'Mount "{mount_name}" marked as mounted.'}


# =============================================================================
# Interactive SSH tunnel for database connections
# =============================================================================
def start_interactive_ssh_tunnel(
    ssh_config_host: str,
    local_port: int,
    remote_host: str,
    remote_port: int = 3306,
    local_data_dir: str = "",
) -> Dict[str, Any]:
    """
    Start an interactive SSH tunnel session (PTY-backed).

    Unlike the non-interactive ``_ensure_ssh_tunnel()`` in apero_async
    (which uses ``BatchMode=yes``), this spawns the SSH tunnel inside a
    PTY so the admin can respond to password, Duo 2FA, or other
    keyboard-interactive authentication prompts in the browser.

    Uses the *same* control socket path as ``_ensure_ssh_tunnel()`` so
    that once the user authenticates, the tunnel is discoverable by all
    subsequent non-interactive database operations.  The ``-f`` flag
    causes SSH to fork to the background after successful authentication,
    which exits the PTY process (exit code 0) while the tunnel keeps
    running via the control socket with ``ControlPersist=yes``.
    """
    from hashlib import sha1

    from apero_ri.core.sshfs_backend import _throttle_ssh_target

    ssh_config_host = str(ssh_config_host or "").strip()
    remote_host = str(remote_host or "").strip()
    if not ssh_config_host:
        return {"ok": False, "error": "SSH config host is required."}
    if not remote_host:
        return {"ok": False, "error": "Remote (database) host is required."}

    throttle_error = _throttle_ssh_target(
        ssh_config_host,
        action="interactive SSH tunnel",
    )
    if throttle_error:
        return {"ok": False, "error": throttle_error}

    # ── Compute the same control-socket path as _ensure_ssh_tunnel ──
    data_dir = str(local_data_dir or "").strip()
    if not data_dir:
        data_dir = os.environ.get("ARI_DIR", str(Path.home() / ".ari"))
    state_root = Path(data_dir).expanduser().resolve() / "secret" / "db_tunnels"
    state_root.mkdir(parents=True, exist_ok=True)
    signature = sha1(
        f"{ssh_config_host}|{remote_host}|{local_port}|{remote_port}".encode(
            "utf-8"
        )
    ).hexdigest()[:16]
    control_path = state_root / f"{signature}.sock"

    # Remove stale socket so SSH can create a fresh one
    if control_path.exists():
        try:
            import subprocess as _sp

            chk = _sp.run(
                [
                    "ssh",
                    "-S",
                    str(control_path),
                    "-O",
                    "check",
                    ssh_config_host,
                ],
                capture_output=True,
                text=True,
                timeout=6,
            )
            if chk.returncode == 0:
                return {
                    "ok": False,
                    "error": "An SSH tunnel is already running for this "
                    'configuration.  Use "Test Connection" directly.',
                }
        except Exception:
            pass
        control_path.unlink(missing_ok=True)

    cmd = [
        "ssh",
        "-f",  # background after auth succeeds
        "-N",  # no remote command — tunnel only
        "-M",  # control-master mode
        "-S",
        str(control_path),  # control socket (matches _ensure_ssh_tunnel)
        "-o",
        "ExitOnForwardFailure=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ControlPersist=yes",
        "-o",
        "ConnectTimeout=15",
        "-t",
        "-t",  # force PTY for interactive auth
        "-L",
        f"{local_port}:{remote_host}:{remote_port}",
        ssh_config_host,
    ]

    return start_session(kind="ssh_tunnel", cmd=cmd)


# =============================================================================
# End of code
# =============================================================================
