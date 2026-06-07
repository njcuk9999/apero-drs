"""Pytest configuration and fixtures for apero_ri tests.

These fixtures create an isolated application instance that:
- Uses a temporary directory instead of ~/.ari so tests never touch real data
- Runs in Flask TESTING mode with a fixed secret key
- Does not start background services or SSHFS mounts
"""

import os
import pytest


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """Create an ARIApp test instance with an isolated data directory."""
    data_dir = tmp_path_factory.mktemp("ari_data")

    # Prevent the app from touching ~/.ari or starting background threads.
    os.environ.setdefault("ARI_DATA_DIR", str(data_dir))

    from apero_ri.application.application import ARIApp

    _app = ARIApp()
    _app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key-not-for-production",
        WTF_CSRF_ENABLED=False,
        RATELIMIT_ENABLED=False,   # disable rate limiting during tests
    )
    # Point auth module at the isolated directory.
    from apero_ri.core import auth as _auth
    _auth.set_ari_dir(str(data_dir))

    yield _app


@pytest.fixture()
def client(app):
    """Return a Flask test client."""
    return app.test_client()


@pytest.fixture()
def admin_user(app):
    """Create a known admin user and return (username, password)."""
    from apero_ri.core import auth as _auth
    username, password = "testadmin", "TestPass123!"
    _auth.create_user(username, password, ["super_admin"])
    yield username, password
    # Cleanup: remove the test user
    users = _auth.load_users()
    users.pop(username, None)
    _auth.save_users(users)
