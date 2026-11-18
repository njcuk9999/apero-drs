#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the per-check APERO-check debug log."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from astropy.io import fits
from flask import Flask, render_template

from apero_ri.apero_monitoring.core import debug_log
from apero_ri.application import apero_checks_api_helpers as ach
from apero_ri.core import ari_lang_support
from apero_ri.tasks import apero_check_task

# =============================================================================
# Define variables
# =============================================================================
PACKAGE_DIR = Path(apero_check_task.__file__).resolve().parents[1]
PRESET_NAME = 'nirps_he_v8.yaml'
PRESET_FILE = PACKAGE_DIR / 'resources' / 'aprofile_instruments' / PRESET_NAME
OBSDIR = '2026-11-15'
# DPR types of a night taken with the UN2 lamp.
UN2_NIGHT = ['DARK', 'WAVE,FP,FP', 'FLAT,DARK,LAMP', 'FLAT,LAMP,DARK',
             'WAVE,UN2,FP', 'WAVE,FP,UN2', 'WAVE,UN2,UN2']
# Old flat requirement list (as frozen into saved profiles).
OLD_REQUIRED = ['DARK', 'WAVE,FP,FP', 'WAVE,UN1,FP', 'WAVE,FP,UN1',
                'FLAT,DARK,LAMP', 'FLAT,LAMP,DARK', 'WAVE,UN1,UN1']


# =============================================================================
# Define functions
# =============================================================================
def _make_night(raw_dir: Path) -> None:
    """Write one fake raw night with the UN2 calibration DPR types."""
    night = raw_dir / OBSDIR
    night.mkdir(parents=True)
    for index, dpr_type in enumerate(UN2_NIGHT):
        header = fits.Header()
        header['HIERARCH ESO DPR TYPE'] = dpr_type
        fits.PrimaryHDU(header=header).writeto(night / f'f{index}.fits')


def _make_profile(raw_dir: Path, override: bool) -> dict:
    """Build a hydrated profile from the packaged preset."""
    preset = yaml.safe_load(PRESET_FILE.read_text(encoding='utf-8'))
    profile = copy.deepcopy(preset)
    profile['APERO_INSTRUMENT_PROFILE'] = PRESET_NAME
    profile['APERO_INSTRUMENT_PROFILE_DATA'] = copy.deepcopy(preset)
    profile['apero_profile'] = 'nirps_he_test'
    profile['paths'] = dict(raw=str(raw_dir))
    if override:
        # Simulate a saved profile that froze the old preset value.
        calib = profile['apero-checks']['calib_test']
        calib['required_dprtypes'] = list(OLD_REQUIRED)
    return profile


def _run_calib(tmp_path: Path, override: bool) -> dict:
    """Run CALIB_TEST once on the fake night and return the result."""
    raw_dir = tmp_path / 'raw'
    _make_night(raw_dir)
    profile = _make_profile(raw_dir, override)
    row = dict(obs_dir=OBSDIR, first_file='', last_file='')
    state = dict(BLANK=True, HAS_OBSDIR=True)
    dbparams = dict(DATABASE_PASSWORD='hunter2', DATABASE_HOST='db')
    run_args = ['CALIB_TEST', 'NIRPS_HE', profile, dbparams, row, state]
    return apero_check_task._run_single_obsdir_check(*run_args)


def test_traced_is_transparent_when_inactive() -> None:
    """Traced helpers behave normally and log nothing without a recorder."""
    calls = []

    @debug_log.traced
    def helper(value: int) -> int:
        calls.append(value)
        return value * 2

    assert debug_log.active() is None
    assert helper(3) == 6
    debug_log.log('ignored')
    assert calls == [3]


def test_traced_records_calls_and_redacts() -> None:
    """Traced calls record args, nesting, returns and redact secrets."""
    @debug_log.traced
    def inner(check_name: str) -> dict:
        return dict(DATABASE_PASSWORD='hunter2', value=check_name)

    @debug_log.traced
    def outer(check_name: str) -> dict:
        return inner(check_name)

    token = debug_log.start('CHECK', OBSDIR)
    try:
        outer('calib_test')
    finally:
        recorder = debug_log.stop(token)
    text = recorder.text()
    assert "-> outer(check_name='calib_test')" in text
    # The nested call is indented under the outer call.
    assert "  -> inner(check_name='calib_test')" in text
    assert 'hunter2' not in text
    assert '<redacted>' in text
    assert recorder.sections_used == ['calib_test']


def test_debug_log_diagnoses_saved_override(tmp_path: Path) -> None:
    """A frozen old requirement list is reported as a profile override."""
    result = _run_calib(tmp_path, override=True)
    text = result['debug']['text']
    assert result['passed'] is False
    assert result['debug']['passed'] is False
    assert '[calib_test] MISMATCH' in text
    assert 'saved profile overrides the preset' in text
    # Inputs, header counts and the environment are all recorded.
    assert "'WAVE,UN2,FP': 1" in text
    assert 'apero_ri version:' in text
    assert 'check_calib_test.py (modified' in text
    assert 'hunter2' not in text


def test_debug_log_clean_profile_passes(tmp_path: Path) -> None:
    """The current preset accepts UN2 and reports a config match."""
    result = _run_calib(tmp_path, override=False)
    text = result['debug']['text']
    assert result['passed'] is True
    assert '[calib_test] OK: value used matches preset file on disk' in text
    assert "group 'WAVE,UN1,FP OR WAVE,UN2,FP' matched = 'WAVE,UN2,FP'" in text


def test_write_obsdir_debug_merges_checks(tmp_path: Path) -> None:
    """Re-running one check only replaces that check's section."""
    entry_a = dict(text='log A1', passed=True, run_at='t1', duration_s=0.1)
    entry_b = dict(text='log B', passed=False, run_at='t1', duration_s=0.2)
    debug_log.write_obsdir_debug(tmp_path, OBSDIR, 'p', dict(A=entry_a))
    debug_log.write_obsdir_debug(tmp_path, OBSDIR, 'p', dict(B=entry_b))
    entry_a2 = dict(entry_a, text='log A2')
    path = debug_log.write_obsdir_debug(tmp_path, OBSDIR, 'p',
                                        dict(A=entry_a2))
    # Debug files must never be picked up by obsdir YAML scans.
    assert path.name.endswith('.json.gz')
    data = debug_log.load_obsdir_debug(path)
    assert list(data['checks']) == ['B', 'A']
    assert data['checks']['A']['text'] == 'log A2'
    only_b = debug_log.format_obsdir_debug(data, check_key='B')
    assert 'log B' in only_b and 'log A2' not in only_b
    both = debug_log.format_obsdir_debug(data)
    assert 'log B' in both and 'log A2' in both


def _call_view_debug(monkeypatch, tmp_path: Path, body: dict,
                     advanced: bool = True):
    """Call the debug API helper with a fake app and profile root."""
    flask_app = Flask(__name__)
    fake_app = SimpleNamespace(ari_groups={})
    monkeypatch.setattr(ach, '_api_user',
                        lambda app: (dict(groups=['admin']), set()))
    monkeypatch.setattr(ach, '_can_see_apero_checks_advanced',
                        lambda perms, groups: advanced)
    monkeypatch.setattr(ach, '_resolve_checks_root',
                        lambda app, profile_id: tmp_path)
    with flask_app.test_request_context(json=body):
        response = ach.api_apero_checks_view_debug(fake_app)
    if isinstance(response, tuple):
        return response[0].get_json(), response[1]
    return response.get_json(), response.status_code


def test_view_debug_api(monkeypatch, tmp_path: Path) -> None:
    """The API returns all checks for a night or just one check."""
    entries = dict(A=dict(text='log A', passed=True, run_at='t',
                          duration_s=0.1),
                   B=dict(text='log B', passed=False, run_at='t',
                          duration_s=0.1))
    debug_log.write_obsdir_debug(tmp_path, OBSDIR, 'p', entries)
    body = dict(profile_id='p', obsdir=OBSDIR)
    data, status = _call_view_debug(monkeypatch, tmp_path, body)
    assert status == 200 and data['checks'] == ['A', 'B']
    assert 'log A' in data['content'] and 'log B' in data['content']
    data, status = _call_view_debug(monkeypatch, tmp_path,
                                    dict(body, check_key='B'))
    assert status == 200
    assert 'log B' in data['content'] and 'log A' not in data['content']


@pytest.mark.parametrize('obsdir', ['../secret', '..', 'a/b'])
def test_view_debug_api_rejects_paths(monkeypatch, tmp_path: Path,
                                      obsdir: str) -> None:
    """Obsdir names cannot escape the debug folder."""
    body = dict(profile_id='p', obsdir=obsdir)
    data, status = _call_view_debug(monkeypatch, tmp_path, body)
    assert status == 400 and data['success'] is False


def test_view_debug_api_permissions(monkeypatch, tmp_path: Path) -> None:
    """Users without advanced access cannot read debug logs."""
    body = dict(profile_id='p', obsdir=OBSDIR)
    data, status = _call_view_debug(monkeypatch, tmp_path, body,
                                    advanced=False)
    assert status == 403 and data['success'] is False


def test_view_debug_api_missing(monkeypatch, tmp_path: Path) -> None:
    """A night without a debug file reports that it must be re-run."""
    body = dict(profile_id='p', obsdir=OBSDIR)
    data, status = _call_view_debug(monkeypatch, tmp_path, body)
    assert status == 404 and data.get('missing') is True


def test_debug_overlay_renders() -> None:
    """The shared overlay partial renders its wiring and payload."""
    flask_app = Flask(__name__,
                      template_folder=str(PACKAGE_DIR / 'templates'),
                      static_folder=str(PACKAGE_DIR / 'static'))
    flask_app.context_processor(ari_lang_support.context)
    payload = dict(profile_id='p', obsdir=OBSDIR, check_key='CALIB_TEST')
    with flask_app.test_request_context():
        html = render_template(
            'monitor_portal/_apero_checks_debug_overlay.html',
            api_view_debug_url='/api/monitor/apero-checks/view-debug',
            debug_button_id='ac-check-view-debug',
            debug_title='Debug log: this check only',
            debug_payload=payload,
            debug_filename='debug.txt',
        )
    assert 'id="ac-debug-overlay"' in html
    assert 'js/apero_checks_debug_log.js' in html
    assert json.dumps('CALIB_TEST') in html
    assert '"ac-check-view-debug"' in html
