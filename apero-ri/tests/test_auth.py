"""Tests for authentication utilities in apero_ri.core.auth."""

import pytest
from apero_ri.core import auth


# =============================================================================
# Password hashing
# =============================================================================

def test_hash_password_returns_string():
    h = auth.hash_password("secret")
    assert isinstance(h, str)
    assert ":" in h


def test_hash_password_unique_salts():
    h1 = auth.hash_password("same")
    h2 = auth.hash_password("same")
    assert h1 != h2, "Same password should produce different hashes (different salts)"


def test_verify_password_correct():
    pw = "correct-horse-battery-staple"
    assert auth.verify_password(pw, auth.hash_password(pw))


def test_verify_password_wrong():
    h = auth.hash_password("right")
    assert not auth.verify_password("wrong", h)


def test_verify_password_truncated_hash():
    assert not auth.verify_password("anything", "notavalidhash")


def test_verify_password_empty():
    assert not auth.verify_password("", "")


# =============================================================================
# Default user generation
# =============================================================================

def test_ensure_default_user_creates_admin(tmp_path):
    auth.set_ari_dir(str(tmp_path))
    auth.ensure_default_user()
    users = auth.load_users()
    admins = [u for u, d in users.items() if auth.user_has_admin_privileges(d.get("groups", []))]
    assert admins, "At least one admin account should exist after ensure_default_user()"


def test_ensure_default_user_no_duplicate(tmp_path):
    auth.set_ari_dir(str(tmp_path))
    auth.ensure_default_user()
    auth.ensure_default_user()  # second call should be a no-op
    users = auth.load_users()
    assert len(users) == 1, "Should not create duplicate accounts"


def test_default_user_password_not_hardcoded(tmp_path, capsys):
    """Verify the generated password is random and printed to stdout."""
    auth.set_ari_dir(str(tmp_path))
    auth.ensure_default_user()
    captured = capsys.readouterr()
    assert "Password" in captured.out
    # Extract the printed password and verify it works
    for line in captured.out.splitlines():
        if "Password" in line:
            password = line.split(":", 1)[-1].strip()
            assert len(password) >= 16, "Generated password should be at least 16 chars"
            break


# =============================================================================
# User management
# =============================================================================

def test_create_and_authenticate(tmp_path):
    auth.set_ari_dir(str(tmp_path))
    auth.create_user("alice", "alicepass", ["public"])
    user = auth.authenticate("alice", "alicepass")
    assert user is not None
    assert user["username"] == "alice"


def test_authenticate_wrong_password(tmp_path):
    auth.set_ari_dir(str(tmp_path))
    auth.create_user("bob", "bobpass", ["public"])
    assert auth.authenticate("bob", "wrongpass") is None


def test_authenticate_nonexistent_user(tmp_path):
    auth.set_ari_dir(str(tmp_path))
    assert auth.authenticate("ghost", "anything") is None


def test_user_is_super_admin():
    assert auth.user_is_super_admin(["super_admin"])
    assert not auth.user_is_super_admin(["admin"])
    assert not auth.user_is_super_admin([])
    assert not auth.user_is_super_admin(None)


def test_user_has_admin_privileges():
    assert auth.user_has_admin_privileges(["admin"])
    assert auth.user_has_admin_privileges(["super_admin"])
    assert not auth.user_has_admin_privileges(["public"])
    assert not auth.user_has_admin_privileges([])
