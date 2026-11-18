#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for suggested APERO version calculation."""

from apero.tools.recipes.dev.apero_version import suggest_version_from_dates


def test_suggest_version_counts_distinct_commit_days() -> None:
    """Each distinct commit day should add one subversion."""
    commit_dates = [
        '2026-11-01',
        '2026-11-01',
        '2026-11-02',
        '2026-11-05',
    ]

    suggested_tag = suggest_version_from_dates(
        '0.8.120', commit_dates
    )

    assert suggested_tag == '0.8.123'


def test_suggest_version_advances_when_no_commits_exist() -> None:
    """A suggestion should still be the next version if there are no commits."""
    suggested_tag = suggest_version_from_dates('0.8.120', [])

    assert suggested_tag == '0.8.121'
