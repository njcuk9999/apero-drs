#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Astrometrics "Unresolved objects" page and sidebar ordering."""
import sys
from pathlib import Path

import pytest
import yaml

from apero_ri.core import permissions

# =============================================================================
# Define variables
# =============================================================================
OBSDIR = '2026-11-15'
# ASTROM failure as written by the check (two unresolved names).
ASTROM_FAILURE = dict(
    name='Astrometric Object Name Check', type='raw', message='failed',
    details=dict(unresolved=[
        dict(name='TOI260', header_key='OBJECT', n_files=3,
             files=['NIRPS_a.fits'], resolver='name not found'),
        dict(name='ALREADY_DONE', header_key='OBJECT', n_files=1,
             files=['NIRPS_b.fits'], resolver=''),
    ]))


# =============================================================================
# Define functions
# =============================================================================
@pytest.fixture()
def client(monkeypatch, tmp_path: Path):
    """ARI test client with one monitor user and one NIRPS_HE profile."""
    from apero_ri.application import application as app_module
    from apero_ri.application import astrometrics_unresolved_helpers as auh
    from apero_ri.application import page_view_helpers as pvh

    from apero_ri.core import task_runner
    from apero_ri.core import user_data

    ari_dir = tmp_path / 'ari'
    monkeypatch.setattr(sys, 'argv', ['ari', '--data-dir', str(ari_dir)])
    monkeypatch.setenv('ARI_DATA_DIR', str(ari_dir))
    monkeypatch.setenv('ARI_DIR', str(ari_dir))
    # Keep the test off the real ARI directory: no scheduler, no health
    #   refresher, no per-user preference files.
    monkeypatch.setattr(task_runner, 'start_background_services',
                        lambda *args, **kwargs: None)
    monkeypatch.setattr(app_module.ARIApp, '_start_admin_health_refresher',
                        lambda self: None)
    monkeypatch.setattr(user_data, 'load_user_prefs',
                        lambda username: dict())
    app = app_module.ARIApp()
    app.config.update(TESTING=True, RATELIMIT_ENABLED=False)
    monkeypatch.setattr(app, '_resolve_local_data_dir', lambda: ari_dir)
    # Checks root holding one night with an ASTROM failure.
    checks_root = tmp_path / 'acheck'
    checks_root.mkdir()
    payload = dict(obsdir=OBSDIR, passes={},
                   failures=dict(ASTROM=ASTROM_FAILURE))
    (checks_root / f'{OBSDIR}.yaml').write_text(yaml.safe_dump(payload))
    # Astrometric database where ALREADY_DONE has been resolved since.
    astrom = Path(app._resolve_local_data_dir()) / 'apero-assets'
    pending = astrom / 'astrometrics' / 'pending'
    pending.mkdir(parents=True)
    entry = dict(APERO_NAME='ALREADY_DONE', ALIASES=[], STATUS='pending')
    (pending / 'ALREADY_DONE.yaml').write_text(yaml.safe_dump(entry))
    profile = dict(profile_id='nirps_he_rali', instrument='NIRPS',
                   data=dict(general=dict(instrument='NIRPS_HE'),
                             paths=dict(PATH_CHECK=str(checks_root))))
    monkeypatch.setattr(auh, 'get_accessible_profiles',
                        lambda user, groups: [profile])
    monkeypatch.setattr(
        auh.checks_index, 'get_check_results',
        lambda pid, key, state: ([dict(obsdir=OBSDIR)]
                                 if state == 'failed' else []))
    user = dict(username='mon', groups=['monitor.NIRPS'])
    monkeypatch.setattr(pvh, 'get_effective_user', lambda session: user)
    return app.test_client()


def test_unresolved_page_lists_names(client) -> None:
    """Unresolved names are listed with a resolve link; resolved dropped."""
    response = client.get('/astrometrics/unresolved')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'TOI260' in html
    assert 'NIRPS_HE' in html
    assert 'rt_name=TOI260&amp;rt_run=1' in html
    # ALREADY_DONE resolves in the astrometric database now.
    assert 'ALREADY_DONE' not in html
    assert '1 resolved since the check ran' in html


def test_unresolved_page_needs_permission(client, monkeypatch) -> None:
    """Users without view.astrometrics.unresolved are redirected."""
    from apero_ri.application import page_view_helpers as pvh

    user = dict(username='gen', groups=['general.NIRPS'])
    monkeypatch.setattr(pvh, 'get_effective_user', lambda session: user)
    response = client.get('/astrometrics/unresolved')
    assert response.status_code == 302


def test_astrometrics_page_still_renders(client) -> None:
    """The astrometrics landing page renders after gaining a child."""
    response = client.get('/astrometrics')
    assert response.status_code == 200
    assert 'rt-name-query' in response.get_data(as_text=True)


def test_sidebar_children_follow_card_sort() -> None:
    """Sidebar children are sorted by label in the parent's direction."""
    pages = {
        'home.p': dict(label='Parent', parent='home'),
        'home.p.b': dict(label='beta', parent='home.p'),
        'home.p.a': dict(label='Alpha', parent='home.p'),
        'home.p.c': dict(label='gamma', parent='home.p'),
    }
    for page in pages.values():
        page['side-nav'] = dict(show=True)
        page['view-permission'] = 'view.test'
    tree_args = ['home.p', {'view.test'}, pages, 'home.p']
    asc = permissions.get_sidebar_tree(
        *tree_args, sort_direction=lambda parent: 'asc')
    desc = permissions.get_sidebar_tree(
        *tree_args, sort_direction=lambda parent: 'desc')
    assert [item['label'] for item in asc] == ['Alpha', 'beta', 'gamma']
    assert [item['label'] for item in desc] == ['gamma', 'beta', 'Alpha']
    # Without a sort callback pages.yaml order is kept.
    kept = permissions.get_sidebar_tree(*tree_args)
    assert [item['label'] for item in kept] == ['beta', 'Alpha', 'gamma']
