"""Pytest configuration and fixtures for apero_ri tests.

These fixtures create an isolated application instance that:
- Uses a temporary directory instead of ~/.ari so tests never touch real data
- Runs in Flask TESTING mode with a fixed secret key
- Does not start background services or SSHFS mounts
"""

import sys
import pytest


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """Create an ARIApp test instance with an isolated data directory."""
    data_dir = tmp_path_factory.mktemp("ari_data")

    from apero_ri.application.application import ARIApp
    from apero_ri.application import ariapp_impls

    with pytest.MonkeyPatch.context() as startup:
        startup.setattr(sys, 'argv', ['ari-test', '--data-dir', str(data_dir)])
        startup.setattr(ARIApp, '_start_admin_health_refresher',
                        lambda self: None)
        startup.setattr(ariapp_impls.task_runner, 'start_background_services',
                        lambda data_dir: None)
        _app = ARIApp()
    _app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key-not-for-production",
        WTF_CSRF_ENABLED=False,
        RATELIMIT_ENABLED=False,   # disable rate limiting during tests
    )
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
