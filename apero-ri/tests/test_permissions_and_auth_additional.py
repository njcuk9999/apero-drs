#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Additional unit tests for auth and permissions helpers."""

from apero_ri.core import auth
from apero_ri.core import permissions


# =============================================================================
# Define functions
# =============================================================================
def _set_isolated_ari_dir(tmp_path) -> None:
    """Point auth storage to `tmp_path` and reset one-time directory guard."""
    auth.set_ari_dir(str(tmp_path))
    auth._ari_dir_ensured = False


def test_find_username_by_email_is_case_insensitive(tmp_path) -> None:
    """Email lookup should match stored addresses case-insensitively."""
    _set_isolated_ari_dir(tmp_path)
    users = {
        'alice': {
            'password': auth.hash_password('pw'),
            'groups': ['public'],
            'emails': ['Alice@Example.com'],
        }
    }
    auth.save_users(users)
    found = auth.find_username_by_email('alice@example.com')
    assert found == 'alice'


def test_authenticate_accepts_email_login(tmp_path) -> None:
    """`authenticate` should support login by email address."""
    _set_isolated_ari_dir(tmp_path)
    users = {
        'bob': {
            'password': auth.hash_password('pass123'),
            'groups': ['public'],
            'emails': ['bob@example.com'],
        }
    }
    auth.save_users(users)
    user = auth.authenticate('bob@example.com', 'pass123')
    assert user is not None
    assert user['username'] == 'bob'


def test_search_users_enforces_minimum_query_length(tmp_path) -> None:
    """User search should return empty results for short queries."""
    _set_isolated_ari_dir(tmp_path)
    auth.create_user('charlie', 'charliepass', ['public'])
    assert auth.search_users('ch') == []
    result = auth.search_users('char')
    assert len(result) == 1
    assert result[0]['username'] == 'charlie'


def test_profile_is_disabled_parses_bool_and_string_forms() -> None:
    """`_profile_is_disabled` should parse booleans and truthy strings."""
    assert auth._profile_is_disabled({'disabled': True})
    assert auth._profile_is_disabled({'DISABLED': 'yes'})
    assert not auth._profile_is_disabled({'disabled': False})
    assert not auth._profile_is_disabled({'disabled': 'no'})


def test_filter_enabled_profiles_removes_disabled_profiles() -> None:
    """Filtering should keep only enabled profile payloads."""
    profiles = {
        'SPIROU': {
            'profile_a': {'disabled': False},
            'profile_b': {'disabled': True},
        }
    }
    filtered = auth._filter_enabled_profiles(profiles)
    assert 'profile_a' in filtered['SPIROU']
    assert 'profile_b' not in filtered['SPIROU']


def test_resolve_group_permissions_handles_inheritance_and_cycles() -> None:
    """Recursive permission resolution should be cycle-safe."""
    groups = {
        'a': {'permissions': ['perm.a'], 'groups': ['b']},
        'b': {'permissions': ['perm.b'], 'groups': ['c']},
        'c': {'permissions': ['perm.c'], 'groups': ['a']},
    }
    perms = permissions.resolve_group_permissions('a', groups)
    assert perms == {'perm.a', 'perm.b', 'perm.c'}


def test_resolve_user_permissions_grants_super_admin_extras() -> None:
    """Super-admin should get all group perms and manage/login permissions."""
    groups = {
        'public': {'permissions': ['view.home'], 'groups': []},
        'admin': {'permissions': ['view.admin'], 'groups': ['public']},
    }
    perms = permissions.resolve_user_permissions(['super_admin'], groups)
    assert 'view.home' in perms
    assert 'view.admin' in perms
    assert 'manage.group.public' in perms
    assert 'login_as.admin' in perms
    assert 'add.instrument' in perms


def test_has_view_permission_accepts_prefix_matches() -> None:
    """Prefix-based page permission matching should work."""
    user_perms = {'view.monitor_portal.SPIROU'}
    assert permissions.has_view_permission('view.monitor_portal', user_perms)
    assert not permissions.has_view_permission('view.admin_portal', user_perms)


def test_page_id_helpers_map_known_paths() -> None:
    """Page id helper functions should map IDs to url/endpoint values."""
    assert permissions.page_id_to_url('home') == '/'
    assert permissions.page_id_to_url('home.monitor_portal.logs') == (
        '/monitor_portal/logs'
    )
    assert permissions.page_id_to_endpoint('home.admin') == 'home_admin'

