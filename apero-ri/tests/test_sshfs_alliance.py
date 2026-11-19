#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for Alliance Duo SSHFS setup and command generation."""

from pathlib import Path

from apero_ri.core import sshfs_backend
from apero_ri.core import sshfs_interactive


def _alliance_mount() -> dict:
    """Return a representative Alliance SSHFS mount."""
    return {
        "name": "fir-data",
        "network_mode": "alliance",
        "connection_mode": "direct",
        "ssh_config_host": "a_fir",
        "remote_host": "fir.alliancecan.ca",
        "remote_user": "neilcook",
        "remote_path": "/home/neilcook/project",
        "local_mount": "/mnt/fir",
        "ssh_key": "fir-key",
    }


def test_standard_mount_command_is_unchanged(tmp_path: Path) -> None:
    """Standard SSH command generation should preserve the existing flags."""
    mount = {
        "connection_mode": "direct",
        "remote_host": "data.example.org",
        "remote_user": "apero",
        "remote_path": "/data",
    }
    key_path = tmp_path / "standard.key"
    command = sshfs_backend._build_mount_command_text(
        mount, key_path, tmp_path / "mount"
    )
    assert f"IdentityFile={key_path}" in command
    assert "BatchMode=yes" in command
    assert "apero@data.example.org:/data" in command
    assert "ssh -O check" not in command


def test_alliance_mount_commands_reuse_control_master(tmp_path: Path) -> None:
    """Alliance commands should initialize and reuse a ControlMaster."""
    mount = _alliance_mount()
    key_path = tmp_path / "fir-key.key"
    command = sshfs_backend._build_mount_command_text(
        mount, key_path, tmp_path / "fir"
    )
    assert "ssh -O check a_fir" in command
    assert "ssh -O exit a_fir" in command
    assert "ssh -fN a_fir" in command
    assert "sshfs -o reconnect -o BatchMode=yes" in command
    assert "ServerAliveInterval=30" in command
    assert "ServerAliveCountMax=6" in command
    assert "a_fir:/home/neilcook/project" in command
    assert "IdentityFile=" not in command


def test_alliance_ssh_config_contains_multiplexing(tmp_path: Path) -> None:
    """Alliance SSH config should include the required Duo reuse settings."""
    config = sshfs_backend._build_alliance_ssh_config(
        _alliance_mount(), tmp_path / "fir-key.key"
    )
    assert "Host a_fir" in config
    assert "HostName fir.alliancecan.ca" in config
    assert "IdentitiesOnly yes" in config
    assert "ControlMaster auto" in config
    assert "ControlPath ~/.ssh/cm-%r@%h:%p" in config
    assert "ControlPersist 12h" in config


def test_add_alliance_mount_persists_required_metadata(
    tmp_path: Path, monkeypatch
) -> None:
    """Alliance mounts should force alias mode and retain host metadata."""
    monkeypatch.setenv("ARI_DIR", str(tmp_path))
    result = sshfs_backend.add_mount(_alliance_mount())
    assert result["ok"]
    mount = sshfs_backend.load_sshfs_config()["mounts"][0]
    assert mount["network_mode"] == "alliance"
    assert mount["connection_mode"] == "ssh_config_host"
    assert mount["remote_host"] == "fir.alliancecan.ca"
    assert mount["remote_user"] == "neilcook"


def test_alliance_test_requires_active_master(
    tmp_path: Path, monkeypatch
) -> None:
    """Batch testing should stop before login when no Duo master exists."""
    monkeypatch.setenv("ARI_DIR", str(tmp_path))
    sshfs_backend.add_ssh_key("fir-key", "test-private-key")
    commands = []

    def fake_run(command, **kwargs):
        """Record the command and report an inactive master."""
        commands.append(command)

        class Result:
            returncode = 1
            stdout = ""
            stderr = "Control socket connect failed"

        return Result()

    monkeypatch.setattr(sshfs_backend.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sshfs_backend, "_throttle_ssh_target", lambda *args, **kwargs: ""
    )
    result = sshfs_backend.test_ssh_connection(
        connection_mode="ssh_config_host",
        remote_host="fir.alliancecan.ca",
        remote_user="neilcook",
        ssh_config_host="a_fir",
        remote_path="/home/neilcook/project",
        ssh_key_name="fir-key",
        network_mode="alliance",
    )
    assert not result["ok"]
    assert "ControlMaster is not active" in result["error"]
    assert commands == [["ssh", "-O", "check", "a_fir"]]


def test_interactive_alliance_test_starts_master(
    tmp_path: Path, monkeypatch
) -> None:
    """The interactive Alliance test should run only ``ssh -fN``."""
    monkeypatch.setenv("ARI_DIR", str(tmp_path))
    sshfs_backend.add_ssh_key("fir-key", "test-private-key")
    started = {}

    def fake_start_session(kind, cmd, mount_name="", env_extra=None):
        """Capture the PTY command without starting SSH."""
        started["kind"] = kind
        started["cmd"] = cmd
        return {"ok": True, "token": "test-token"}

    monkeypatch.setattr(
        sshfs_backend, "_throttle_ssh_target", lambda *args, **kwargs: ""
    )
    monkeypatch.setattr(
        sshfs_interactive, "start_session", fake_start_session
    )
    result = sshfs_interactive.start_interactive_test(
        connection_mode="ssh_config_host",
        remote_host="fir.alliancecan.ca",
        remote_user="neilcook",
        ssh_config_host="a_fir",
        remote_path="/home/neilcook/project",
        ssh_key_name="fir-key",
        network_mode="alliance",
    )
    assert result["ok"]
    assert started["kind"] == "ssh_test"
    assert started["cmd"] == ["ssh", "-fN", "a_fir"]
