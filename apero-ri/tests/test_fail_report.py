#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for `apero_ri.core.fail_report` pure helpers and storage."""

from pathlib import Path

from apero_ri.core import fail_report


def test_extract_error_lines_and_blocks() -> None:
    """Error extraction should keep only contiguous `-!!|` sequences."""
    text = (
        '10:00:00-!!|recipe[1]|first\n'
        '10:00:01-!!|recipe[1]|second\n'
        '10:00:02-@@|recipe[1]|info\n'
        '10:00:03-!!|recipe[1]|third\n'
    )
    lines = fail_report.extract_error_lines(text)
    blocks = fail_report.extract_error_blocks(text)
    assert len(lines) == 3
    assert len(blocks) == 2
    assert len(blocks[0]) == 2
    assert len(blocks[1]) == 1


def test_normalize_error_message_replaces_variable_tokens() -> None:
    """Normalization should collapse variable strings into placeholders."""
    message = (
        'Failed for /tmp/a/file.txt at 2026-01-01 '
        '01:02:03 with value 42'
    )
    normalized = fail_report.normalize_error_message(message)
    assert '<PATH>' in normalized
    assert '<DATE>' in normalized or '<TIME>' in normalized
    assert '<NUM>' in normalized


def test_template_and_vars_extracts_template_slots() -> None:
    """Templating should expose numbered placeholders and captured values."""
    tmpl, values = fail_report._template_and_vars(
        'Err in /a for object [GL699]'
    )
    assert '{{1}}' in tmpl
    assert len(values) >= 1


def test_group_error_blocks_and_display_template() -> None:
    """Grouping should merge similar errors and report varying placeholders."""
    items = [
        {
            'label': 'r1',
            'error_blocks': [
                ['10:00-!!|r1|Failed opening /tmp/x/file1.dat'],
                ['10:01-!!|r1|Failed opening /tmp/x/file2.dat'],
            ],
        }
    ]
    groups = fail_report.group_error_blocks(items)
    assert len(groups) == 1
    assert groups[0]['count'] == 2
    display, varmap = fail_report.build_display_template(
        groups[0]['template'], groups[0]['var_unique']
    )
    assert isinstance(display, str)
    assert isinstance(varmap, dict)


def test_format_duration_basic_cases() -> None:
    """Duration helper should format normal and invalid inputs safely."""
    assert fail_report.format_duration(3661) == '1h 1m 1s'
    assert fail_report.format_duration(59) == '59s'
    assert fail_report.format_duration(None) == 'n/a'
    assert fail_report.format_duration(-1) == 'n/a'


def test_store_and_resolve_report_token(tmp_path, monkeypatch) -> None:
    """Stored report token resolves while report file exists and is fresh."""
    monkeypatch.setenv('ARI_DIR', str(tmp_path))
    fail_report.set_ari_dir(Path(tmp_path))
    token = fail_report.store_report_pdf(
        b'%PDF-test', {'filename': 'unit.pdf', 'profile_id': 'p1', 'pid': 'id1'}
    )
    resolved = fail_report.resolve_report_token(token)
    assert resolved is not None
    assert resolved['filename'] == 'unit.pdf'


def test_invalid_token_is_rejected() -> None:
    """Token resolver should reject malformed token values quickly."""
    assert fail_report.resolve_report_token('not-a-uuid') is None



