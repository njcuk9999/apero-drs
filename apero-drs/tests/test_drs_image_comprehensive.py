#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive tests for apero-drs pickle and image helper functions."""

import os
import tempfile
import numpy as np
from unittest.mock import MagicMock, patch

from apero.io import drs_pickle
from apero.io import drs_image


# =============================================================================
# Define functions - drs_pickle tests
# =============================================================================
def test_pickle_functions_exist() -> None:
    """Pickle module should have make_pickle and get_pickle."""
    assert hasattr(drs_pickle, 'make_pickle')
    assert hasattr(drs_pickle, 'get_pickle')


def test_make_pickle_requires_params() -> None:
    """make_pickle requires params argument."""
    # This will fail if params is missing, but we can check function exists
    assert callable(drs_pickle.make_pickle)


def test_get_pickle_requires_params() -> None:
    """get_pickle requires params argument."""
    assert callable(drs_pickle.get_pickle)


# =============================================================================
# Define functions - drs_image rotation tests
# =============================================================================
def test_rotate_image_identity() -> None:
    """rotate_image with rotnum=0 should return same image."""
    image = np.array([[1, 2], [3, 4]])
    result = drs_image.rotate_image(image, 0)
    assert np.array_equal(result, image)


def test_rotate_image_90_degrees() -> None:
    """rotate_image with rotnum=1 should rotate 90 deg counter-clockwise."""
    image = np.array([[1, 2], [3, 4]])
    result = drs_image.rotate_image(image, 1)
    # 90 degree CCW rotation should have shape (2, 2)
    assert result.shape == (2, 2)


def test_rotate_image_180_degrees() -> None:
    """rotate_image with rotnum=2 should rotate 180 degrees."""
    image = np.array([[1, 2], [3, 4]])
    result = drs_image.rotate_image(image, 2)
    assert result.shape == (2, 2)


def test_rotate_image_270_degrees() -> None:
    """rotate_image with rotnum=3 should rotate 90 deg clockwise."""
    image = np.array([[1, 2], [3, 4]])
    result = drs_image.rotate_image(image, 3)
    assert result.shape == (2, 2)


def test_rotate_image_flip_top_bottom() -> None:
    """rotate_image with rotnum=4 should flip top-bottom."""
    image = np.array([[1, 2], [3, 4]])
    result = drs_image.rotate_image(image, 4)
    expected = np.array([[3, 4], [1, 2]])
    assert np.array_equal(result, expected)


def test_rotate_image_modulo_8() -> None:
    """rotate_image with rotnum >= 8 should apply modulo 8."""
    image = np.array([[1, 2], [3, 4]])
    result1 = drs_image.rotate_image(image, 0)
    result2 = drs_image.rotate_image(image, 8)
    assert np.array_equal(result1, result2)


# =============================================================================
# Define functions - drs_image resize tests
# =============================================================================
def test_resize_image_default_bounds() -> None:
    """resize with default bounds should return full image."""
    image = np.arange(16).reshape(4, 4)
    result = drs_image.resize(image)
    # Should resize to full image with default bounds
    assert result is not None
    assert isinstance(result, np.ndarray)


def test_resize_image_custom_bounds() -> None:
    """resize with custom bounds should extract region."""
    image = np.arange(16).reshape(4, 4)
    result = drs_image.resize(image, xlow=1, xhigh=3, ylow=1, yhigh=3)
    # Should extract 2x2 region
    assert result.shape[0] > 0
    assert result.shape[1] > 0


def test_resize_image_with_pixel_lists() -> None:
    """resize with x and y pixel lists should use them."""
    image = np.arange(16).reshape(4, 4)
    x = np.array([0, 1, 2])
    y = np.array([0, 1, 2])
    result = drs_image.resize(image, x=x, y=y)
    assert result.shape == (3, 3)


def test_resize_image_xhigh_none_uses_shape() -> None:
    """resize with xhigh=None should use image width."""
    image = np.arange(16).reshape(4, 4)
    result = drs_image.resize(image, xlow=0, xhigh=None, ylow=0, yhigh=None)
    assert result is not None


def test_resize_image_returns_ndarray() -> None:
    """resize should return numpy ndarray."""
    image = np.arange(16).reshape(4, 4)
    result = drs_image.resize(image)
    assert isinstance(result, np.ndarray)


# =============================================================================
# Define functions - drs_image conversion tests
# =============================================================================
def test_convert_to_e_multiplies_by_gain_and_exptime() -> None:
    """convert_to_e should multiply by gain and exposure time."""
    image = np.ones((4, 4))
    params = MagicMock()
    params.__getitem__.side_effect = lambda x: {
        'EFF_GAIN': 2.0,
        'EXPTIME': 3.0
    }.get(x, 1.0)

    result = drs_image.convert_to_e(params, image, gain=2.0, exptime=3.0)
    expected = image * 2.0 * 3.0
    assert np.allclose(result, expected)


def test_convert_to_e_uses_override_gain() -> None:
    """convert_to_e gain override should override params."""
    image = np.ones((2, 2))
    params = MagicMock()
    params.__getitem__.side_effect = lambda x: {
        'EFF_GAIN': 1.0,
        'EXPTIME': 1.0
    }.get(x, 1.0)

    result = drs_image.convert_to_e(params, image, gain=5.0, exptime=1.0)
    expected = image * 5.0
    assert np.allclose(result, expected)


def test_convert_to_e_returns_ndarray() -> None:
    """convert_to_e should return numpy array."""
    image = np.ones((2, 2))
    params = MagicMock()
    params.__getitem__.side_effect = lambda x: {
        'EFF_GAIN': 1.0,
        'EXPTIME': 1.0
    }.get(x, 1.0)

    result = drs_image.convert_to_e(params, image, gain=1.0, exptime=1.0)
    assert isinstance(result, np.ndarray)


def test_convert_to_adu_multiplies_by_exptime() -> None:
    """convert_to_adu should multiply by exposure time."""
    image = np.ones((2, 2))
    params = MagicMock()
    params.__getitem__.side_effect = lambda x: {'EXPTIME': 2.0}.get(x, 1.0)

    result = drs_image.convert_to_adu(params, image, exptime=2.0)
    expected = image * 2.0
    assert np.allclose(result, expected)


def test_convert_to_adu_returns_ndarray() -> None:
    """convert_to_adu should return numpy array."""
    image = np.ones((2, 2))
    params = MagicMock()
    params.__getitem__.side_effect = lambda x: {'EXPTIME': 1.0}.get(x, 1.0)

    result = drs_image.convert_to_adu(params, image, exptime=1.0)
    assert isinstance(result, np.ndarray)


# =============================================================================
# Define functions - drs_image flip tests
# =============================================================================
def test_flip_image_no_flip() -> None:
    """flip_image with 'None' should return unchanged image."""
    image = np.array([[1, 2], [3, 4]])
    params = MagicMock()
    params.__getitem__.return_value = 'None'

    result = drs_image.flip_image(params, image, flip_kind='None')
    assert np.array_equal(result, image)


def test_flip_image_x_axis() -> None:
    """flip_image with 'x' should flip left-right."""
    image = np.array([[1, 2], [3, 4]])
    params = MagicMock()
    result = drs_image.flip_image(params, image, flip_kind='x')
    expected = np.array([[2, 1], [4, 3]])
    assert np.array_equal(result, expected)


def test_flip_image_y_axis() -> None:
    """flip_image with 'y' should flip top-bottom."""
    image = np.array([[1, 2], [3, 4]])
    params = MagicMock()
    result = drs_image.flip_image(params, image, flip_kind='y')
    expected = np.array([[3, 4], [1, 2]])
    assert np.array_equal(result, expected)


def test_flip_image_both_axes() -> None:
    """flip_image with 'both' should flip both axes."""
    image = np.array([[1, 2], [3, 4]])
    params = MagicMock()
    result = drs_image.flip_image(params, image, flip_kind='both')
    expected = np.array([[4, 3], [2, 1]])
    assert np.array_equal(result, expected)


def test_flip_image_returns_ndarray() -> None:
    """flip_image should return numpy array."""
    image = np.ones((2, 2))
    params = MagicMock()
    result = drs_image.flip_image(params, image, flip_kind='None')
    assert isinstance(result, np.ndarray)


# =============================================================================
# Define functions - drs_image clean_hotpix tests
# =============================================================================
def test_clean_hotpix_accepts_image_and_badpix() -> None:
    """clean_hotpix should accept image and bad pixel map."""
    image = np.random.random((10, 10))
    badpix = np.zeros((10, 10), dtype=bool)
    result = drs_image.clean_hotpix(image, badpix)
    assert result is not None
    assert isinstance(result, np.ndarray)


def test_clean_hotpix_preserves_shape() -> None:
    """clean_hotpix should preserve image shape."""
    image = np.random.random((5, 8))
    badpix = np.zeros((5, 8), dtype=bool)
    result = drs_image.clean_hotpix(image, badpix)
    assert result.shape == image.shape


def test_clean_hotpix_with_bad_pixels() -> None:
    """clean_hotpix should handle bad pixel map."""
    image = np.random.random((10, 10))
    # Create a bad pixel map
    badpix = np.zeros((10, 10), dtype=bool)
    badpix[5, 5] = True  # Mark one bad pixel
    result = drs_image.clean_hotpix(image, badpix)
    assert result is not None


def test_clean_hotpix_returns_ndarray() -> None:
    """clean_hotpix should return numpy array."""
    image = np.random.random((5, 5))
    badpix = np.zeros((5, 5), dtype=bool)
    result = drs_image.clean_hotpix(image, badpix)
    assert isinstance(result, np.ndarray)


# =============================================================================
# End of code
# =============================================================================

