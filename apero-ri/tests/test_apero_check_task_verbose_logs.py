#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Regression tests for verbose APERO-check task logging."""

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
