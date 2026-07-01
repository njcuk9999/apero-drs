#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for helper utilities in tools documentation and inverse modules."""

import numpy as np

from apero.tools.module.documentation import drs_markdown
from apero.tools.module.utils import inverse


# =============================================================================
# Define functions
# =============================================================================
def test_markdown_page_adds_reference_title_and_sections() -> None:
    """`MarkDownPage` should build expected line blocks for headings."""
    page = drs_markdown.MarkDownPage('main_page')
    page.add_title('Main Title')
    page.add_section('Section A')
    page.add_sub_section('Section B')

    assert '.. _main_page:' in page.lines
    assert 'Main Title' in page.lines
    assert 'Section A' in page.lines
    assert 'Section B' in page.lines
    assert any(len(line) >= 80 for line in page.lines if line.startswith('#'))


def test_markdown_enable_multiline_table_is_idempotent() -> None:
    """Enabling multiline table twice should only inject one directive block."""
    page = drs_markdown.MarkDownPage('page')
    page.enable_multiline_table()
    page.enable_multiline_table()

    assert page.lines.count('.. |br| raw:: html') == 1


def test_markdown_link_helpers_generate_expected_rst_links() -> None:
    """Helper formatters should produce reference/download link directives."""
    ref = drs_markdown.make_url('value', 'target')
    dl = drs_markdown.make_download('value', 'file.txt')

    assert ref == ':ref:`value <target>`'
    assert dl == ':download:`value <file.txt>`'


def test_drs_image_shape_returns_cutout_dimensions() -> None:
    """Image shape helper should return y/x dimensions from bounds."""
    params = {
        'IMAGE.Y_LOW': 10,
        'IMAGE.Y_HIGH': 22,
        'IMAGE.X_LOW': 3,
        'IMAGE.X_HIGH': 8,
    }

    assert inverse.drs_image_shape(params) == (12, 5)


def test_drs_to_pp_inserts_cutout_then_flips_image(monkeypatch) -> None:
    """`drs_to_pp` should place image in bounds and flip both axes."""
    params = {
        'IMAGE.Y_FULL': 4,
        'IMAGE.X_FULL': 5,
        'IMAGE.Y_LOW': 1,
        'IMAGE.Y_HIGH': 3,
        'IMAGE.X_LOW': 1,
        'IMAGE.X_HIGH': 4,
    }
    image = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

    if not hasattr(inverse.np, 'product'):
        monkeypatch.setattr(inverse.np, 'product', np.prod, raising=False)

    out = inverse.drs_to_pp(params, image, fill=-1.0)

    expected = np.full((4, 5), -1.0)
    expected[1:3, 1:4] = image
    expected = expected[::-1, ::-1]
    assert np.array_equal(out, expected)


def test_e2ds_to_simage_maps_values_by_order_mask(monkeypatch) -> None:
    """`e2ds_to_simage` should copy per-x order values into masked rows."""
    e2ds = np.array([[10.0, 20.0, 30.0]])
    ypix, xpix = np.indices((4, 3))

    if not hasattr(inverse.np, 'product'):
        monkeypatch.setattr(inverse.np, 'product', np.prod, raising=False)

    out = inverse.e2ds_to_simage(
        e2ds, xpix, ypix, centers=[1.5], widths=[2.0], fill=0.0
    )

    assert np.array_equal(out[1], np.array([10.0, 20.0, 30.0]))
    assert np.array_equal(out[2], np.array([10.0, 20.0, 30.0]))
    assert np.array_equal(out[0], np.zeros(3))

