#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for utility functions in ``apero.tools.module.error.error_html``."""

from astropy.table import Table
import pytest

from apero.tools.module.error import error_html


# =============================================================================
# Define functions
# =============================================================================
def test_apero_group_to_date_and_pid_to_time_parsing() -> None:
    """Group/PID parsing should return date/time strings for valid tokens."""
    group = 'APERO-PROC-00016406414334182270-Q163'
    pid = 'PID-00016406414334182270-Q163'

    group_date = error_html.apero_group_to_date(group)
    pid_time = error_html.pid_to_time(pid)

    assert pid_time is not None
    assert group_date == pid_time.split()[0]
    assert len(pid_time) >= 19
    with pytest.raises(ValueError):
        error_html.apero_group_to_date('APERO-00016406414334182270-Q163')
    assert error_html.pid_to_time('bad_pid') is None
    assert error_html.pid_to_time(None) is None


def test_python_str_to_html_str_replaces_newlines_and_tabs() -> None:
    """String cleanup should translate line breaks and tabs to HTML tokens."""
    value = 'line1\n\tline2'

    result = error_html.python_str_to_html_str(value)

    assert result == 'line1<br>&nbsp;&nbsp;&nbsp;&nbsp;line2'


def test_table_to_outlist_adds_crunfiles_from_runstring_patterns() -> None:
    """`table_to_outlist` should derive CRUNFILES from RUNSTRING entries."""
    table = Table()
    table['RUNSTRING'] = [
        '--flag x crunfile=alpha.yaml --other',
        '--flag x crunfile beta.ini --other',
        '--flag x --other',
    ]
    table['STATUS'] = ['OK', 'WARN', 'FAIL']

    outlist, outcols, outtypes = error_html.table_to_outlist(
        table,
        in_col_names=['RUNSTRING', 'STATUS'],
        out_col_names=['RUNSTRING', 'STATUS'],
        out_types=['str', 'str'],
    )

    assert 'CRUNFILES' in outcols
    assert outtypes[outcols.index('CRUNFILES')] == 'str'
    assert outlist[1]['CRUNFILES'] == 'alpha'
    assert outlist[2]['CRUNFILES'] == 'beta'
    assert outlist[3]['CRUNFILES'] == 'None'


def test_full_page_html_includes_css_links_for_string_and_list() -> None:
    """`full_page_html` should render one or many css link tags."""
    one_css = error_html.full_page_html(css='single.css')
    many_css = error_html.full_page_html(css=['a.css', 'b.css'])

    assert 'href="single.css"' in one_css
    assert 'href="a.css"' in many_css
    assert 'href="b.css"' in many_css
    assert '<!DOCTYPE html>' in many_css

