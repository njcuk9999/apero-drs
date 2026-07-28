#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for verbose APERO-check task logging."""

from apero_ri.apero_monitoring.checks import check_astrometrics
from apero_ri.tasks import apero_check_task


def test_format_verbose_check_log_includes_report_lines() -> None:
    """Verbose check logs should include the detailed report body."""
    result = {
        "report": "QC for obsdir 2024-01-02\nPassed QC:\n\tfoo\nFailed QC:\n\tbar",
        "passed": False,
    }

    lines = apero_check_task._format_verbose_check_log(
        "2024-01-02",
        "ASTROM",
        "FAIL",
        1.23,
        result,
    )

    assert lines[0].startswith("2024-01-02 | ASTROM | FAIL | 1.23s")
    assert any("QC for obsdir 2024-01-02" in line for line in lines)
    assert any("\tfoo" in line for line in lines)
    assert any("\tbar" in line for line in lines)


def test_astrom_check_builds_report_without_crashing(monkeypatch, tmp_path) -> None:
    """ASTROM should build a report even when no failures are present."""
    obs_path = tmp_path / 'obsdir'
    obs_path.mkdir()
    fits_path = obs_path / 'test.fits'
    fits_path.write_bytes(b'')

    aparams = {
        'apero-checks': {
            'astrom_test': {
                'enabled': True,
                'obj_name_keys': ['OBJECT'],
                'sci_suffix': '.fits',
                'dprtypes': [],
            },
        },
    }

    def fake_get_check_value(aparams_dict, check_name, keys, default=None):
        if keys == ['obj_name_keys']:
            return ['OBJECT']
        if keys == ['sci_suffix']:
            return '.fits'
        if keys == ['dprtypes']:
            return []
        return default

    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'is_check_enabled',
        lambda *args, **kwargs: True,
    )
    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'list_obsdir_files',
        lambda *args, **kwargs: (obs_path, [fits_path]),
    )
    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'get_check_value',
        fake_get_check_value,
    )
    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'get_header_key',
        lambda *args, **kwargs: 'DPRTYPE',
    )
    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'read_primary_header',
        lambda *args, **kwargs: {'OBJECT': 'M31', 'DPRTYPE': 'SCI'},
    )
    monkeypatch.setattr(
        check_astrometrics,
        '_resolve_astrom',
        lambda name: ('APERO-M31', None),
    )

    passed, report = check_astrometrics.check_function(
        'SPIROU',
        'obsdir',
        aparams,
        {},
    )

    assert passed is True
    assert 'Summary:' in report
    assert 'APERO-M31' in report


def test_astrom_check_reports_preflight_and_failure_reason(
    monkeypatch,
    tmp_path,
) -> None:
    """ASTROM should report resolver preflight and failure reasons."""
    obs_path = tmp_path / 'obsdir'
    obs_path.mkdir()
    fits_path = obs_path / 'test.fits'
    fits_path.write_bytes(b'')

    aparams = {
        'apero-checks': {
            'astrom_test': {
                'enabled': True,
                'obj_name_keys': ['OBJECT'],
                'sci_suffix': '.fits',
                'dprtypes': [],
            },
        },
    }

    def fake_get_check_value(aparams_dict, check_name, keys, default=None):
        if keys == ['obj_name_keys']:
            return ['OBJECT']
        if keys == ['sci_suffix']:
            return '.fits'
        if keys == ['dprtypes']:
            return []
        return default

    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'is_check_enabled',
        lambda *args, **kwargs: True,
    )
    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'list_obsdir_files',
        lambda *args, **kwargs: (obs_path, [fits_path]),
    )
    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'get_check_value',
        fake_get_check_value,
    )
    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'get_header_key',
        lambda *args, **kwargs: 'DPRTYPE',
    )
    monkeypatch.setattr(
        check_astrometrics.raw_common,
        'read_primary_header',
        lambda *args, **kwargs: {'OBJECT': 'M31', 'DPRTYPE': 'SCI'},
    )
    monkeypatch.setattr(
        check_astrometrics,
        '_resolve_astrom',
        lambda name: (None, 'resolver backend down'),
    )

    passed, report = check_astrometrics.check_function(
        'SPIROU',
        'obsdir',
        aparams,
        {},
    )

    assert passed is False
    assert 'resolver_preflight=' in report
    assert 'resolver backend down' in report
