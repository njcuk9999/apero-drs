#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for small image helpers in ``apero.io.drs_image``."""

from pathlib import Path

import numpy as np
import pytest

_APERO_DATA_DIR = Path.cwd() / 'apero-data'
for _subdir in [
    'raw',
    'reduced',
    'out',
    'calibDB',
    'telluDB',
    'msg',
    'working',
    'plot',
    'runs',
    'assets',
    'other',
    'lbldata',
]:
    (_APERO_DATA_DIR / _subdir).mkdir(parents=True, exist_ok=True)

from apero.io import drs_image


# =============================================================================
# Define functions
# =============================================================================
@pytest.mark.parametrize('rotnum', list(range(9)))
def test_rotate_image_matches_documented_orientations(rotnum: int) -> None:
    """`rotate_image` should follow the documented eight-way rotation map."""
    image = np.array([[1, 2, 3], [4, 5, 6]])
    expected = {
        0: image,
        1: np.rot90(image, 1),
        2: np.rot90(image, 2),
        3: np.rot90(image, -1),
        4: np.flipud(image),
        5: np.rot90(np.flipud(image), 1),
        6: np.rot90(np.flipud(image), 2),
        7: np.rot90(np.flipud(image), -1),
        8: image,
    }[rotnum]

    result = drs_image.rotate_image(image, rotnum)

    assert np.array_equal(result, expected)


def test_resize_supports_bounds_and_explicit_pixel_lists() -> None:
    """`resize` should support both bound-based and explicit indexing."""
    image = np.arange(16).reshape(4, 4)

    bounded = drs_image.resize(image, xlow=1, xhigh=3, ylow=0, yhigh=2)
    indexed = drs_image.resize(
        image,
        x=np.array([3, 1]),
        y=np.array([2, 0]),
    )

    assert np.array_equal(bounded, np.array([[1, 2], [5, 6]]))
    assert np.array_equal(indexed, np.array([[11, 9], [3, 1]]))


def test_resize_rejects_zero_width_ranges() -> None:
    """Equal low/high bounds should raise an exception."""
    image = np.arange(9).reshape(3, 3)

    with pytest.raises(Exception):
        drs_image.resize(image, xlow=1, xhigh=1)


def test_flip_image_applies_expected_axis_flips() -> None:
    """`flip_image` should honor the documented flip modes."""
    image = np.array([[1, 2], [3, 4]])
    params = {}

    assert np.array_equal(
        drs_image.flip_image(params, image, flip_kind='None'),
        image,
    )
    assert np.array_equal(
        drs_image.flip_image(params, image, flip_kind='both'),
        np.array([[4, 3], [2, 1]]),
    )
    assert np.array_equal(
        drs_image.flip_image(params, image, flip_kind='x'),
        np.array([[2, 1], [4, 3]]),
    )
    assert np.array_equal(
        drs_image.flip_image(params, image, flip_kind='y'),
        np.array([[3, 4], [1, 2]]),
    )


def test_get_fiber_types_handles_default_all_and_single_modes() -> None:
    """`get_fiber_types` should resolve explicit and implicit fiber choices."""
    params = {
        'IMAGE.FIBER_TYPES': ['AB', 'A', 'B'],
        'INPUTS': {'FIBER': 'ALL'},
    }

    assert drs_image.get_fiber_types(params) == ['AB', 'A', 'B']
    assert drs_image.get_fiber_types(params, fiber='B') == ['B']
    assert drs_image.get_fiber_types(
        params,
        fibertypes=['CUSTOM'],
    ) == ['CUSTOM']


def test_npy_filelist_and_npy_fileclean_round_trip(tmp_path: Path) -> None:
    """Temporary numpy-file helpers should save and then remove files."""
    array = np.array([[1.0, 2.0], [3.0, 4.0]])
    filenames, subdir = drs_image.npy_filelist(
        'test',
        7,
        array,
        filenames=None,
        subdir='cache',
        outdir=str(tmp_path),
    )
    saved_path = Path(filenames[0])

    assert subdir == 'cache'
    assert saved_path.is_file()
    assert np.array_equal(np.load(saved_path), array)

    drs_image.npy_fileclean(
        filenames,
        subdir=subdir,
        outdir=str(tmp_path),
    )

    assert not saved_path.exists()
    assert not (tmp_path / subdir).exists()


def test_med_comb_clean_filename_only_replaces_basename_dots() -> None:
    """Filename cleaning should preserve the directory path unchanged."""
    filename = '/tmp/a.b/c.d.fits'
    result = drs_image.med_comb_clean_filename(filename)

    assert result == '/tmp/a.b/c_d_fits'



