#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pure image shape-transform functions

The functions in this module operate only on numpy arrays and numerical
transform parameters. They do not load APERO profiles or depend on apero-drs.

Created on 2026-09-14

@author: cook
"""
from typing import Optional, Tuple

import numpy as np
from scipy.ndimage import map_coordinates

from aperocore.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.calib.shape_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def _transform_coordinates(shape: Tuple[int, int],
                            lin_transform_vect: Optional[np.ndarray],
                            dxmap: Optional[np.ndarray],
                            dymap: Optional[np.ndarray]
                            ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate the source coordinates used by the forward transform

    :param shape: tuple, (rows, columns) of the destination image
    :param lin_transform_vect: array of six values (dx, dy, A, B, C, D),
                               or None for the identity transform
    :param dxmap: array, x displacement at each destination pixel, or None
    :param dymap: array, y displacement at each destination pixel, or None

    :return: tuple, source x and y coordinate arrays
    """
    if lin_transform_vect is None:
        lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    dx0, dy0, a, b, c, d = np.asarray(lin_transform_vect, dtype=float)
    yy, xx = np.indices(shape, dtype=float)
    xcoord = dx0 + xx * a + yy * b
    ycoord = dy0 + xx * c + yy * d
    if dxmap is not None:
        xcoord = xcoord + dxmap
    if dymap is not None:
        ycoord = ycoord + dymap
    return xcoord, ycoord


def ea_transform(image: np.ndarray,
                 lin_transform_vect: Optional[np.ndarray] = None,
                 dxmap: Optional[np.ndarray] = None,
                 dymap: Optional[np.ndarray] = None,
                 order: int = 2) -> np.ndarray:
    """
    Apply a linear transform and optional displacement maps to an image

    The output grid is used as the coordinate grid. Each output pixel reads
    the input image at the transformed coordinate, matching scipy's backward
    interpolation convention and APERO's original ``ea_transform``.

    :param image: numpy array (2D), image to transform
    :param lin_transform_vect: array of six values (dx, dy, A, B, C, D),
                               or None for the identity transform
    :param dxmap: numpy array (2D) or None, x displacement map
    :param dymap: numpy array (2D) or None, y displacement map
    :param order: int, spline interpolation order

    :return: numpy array (2D), transformed image with NaNs propagated
    """
    image = np.asarray(image, dtype=float)
    for name, value in [('dxmap', dxmap), ('dymap', dymap)]:
        if value is not None and np.shape(value) != image.shape:
            emsg = '{0} must have the same shape as image'
            raise ValueError(emsg.format(name))
    if lin_transform_vect is None and dxmap is None and dymap is None:
        return np.array(image, copy=True)
    xcoord, ycoord = _transform_coordinates(image.shape,
                                            lin_transform_vect,
                                            dxmap, dymap)
    valid = np.isfinite(image)
    filled = np.where(valid, image, 0.0)
    result = map_coordinates(filled, [ycoord, xcoord], order=order,
                             cval=np.nan, output=float, mode='constant')
    weights = map_coordinates(valid.astype(float), [ycoord, xcoord],
                              order=order, cval=0.0, output=float,
                              mode='constant')
    with np.errstate(invalid='ignore', divide='ignore'):
        result = result / weights
    result[weights < 0.5] = np.nan
    return result


def inverse_coordinates(shape: Tuple[int, int],
                        lin_transform_vect: Optional[np.ndarray] = None,
                        dxmap: Optional[np.ndarray] = None,
                        dymap: Optional[np.ndarray] = None,
                        niter: int = 6
                        ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Solve source coordinates for the reverse shape transform

    For each output pixel, solve ``target = affine(source) + map(source)``
    by fixed-point iteration. The displacement maps are sampled at the
    current source estimate using nearest-boundary linear interpolation.

    :param shape: tuple, (rows, columns) of the reverse-transform output
    :param lin_transform_vect: array of six values (dx, dy, A, B, C, D),
                               or None for the identity transform
    :param dxmap: numpy array (2D) or None, x displacement map
    :param dymap: numpy array (2D) or None, y displacement map
    :param niter: int, number of fixed-point iterations

    :return: tuple, source x and y coordinates for every output pixel
    """
    if lin_transform_vect is None:
        lin_transform_vect = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    dx0, dy0, a, b, c, d = np.asarray(lin_transform_vect, dtype=float)
    if dxmap is None:
        dxmap = np.zeros(shape, dtype=float)
    if dymap is None:
        dymap = np.zeros(shape, dtype=float)
    if np.shape(dxmap) != shape or np.shape(dymap) != shape:
        raise ValueError('displacement maps must have the requested shape')
    yy, xx = np.indices(shape, dtype=float)
    xcoord, ycoord = np.array(xx), np.array(yy)
    for _ in range(int(niter)):
        map_x = map_coordinates(dxmap, [ycoord, xcoord], order=1,
                                mode='nearest')
        map_y = map_coordinates(dymap, [ycoord, xcoord], order=1,
                                mode='nearest')
        residual_x = xx - (dx0 + xcoord * a + ycoord * b + map_x)
        residual_y = yy - (dy0 + xcoord * c + ycoord * d + map_y)
        xcoord = xcoord + residual_x
        ycoord = ycoord + residual_y
    return xcoord, ycoord


def ea_transform_reverse(image: np.ndarray,
                         lin_transform_vect: Optional[np.ndarray] = None,
                         dxmap: Optional[np.ndarray] = None,
                         dymap: Optional[np.ndarray] = None,
                         niter: int = 6, order: int = 2
                         ) -> np.ndarray:
    """
    Reverse an ``ea_transform`` without cached state

    The input image is sampled at coordinates obtained by solving the inverse
    transform on the output image grid. NaNs are propagated using the same
    weighted interpolation as ``ea_transform``.

    :param image: numpy array (2D), image in the forward-transform frame
    :param lin_transform_vect: array of six values (dx, dy, A, B, C, D),
                               or None for the identity transform
    :param dxmap: numpy array (2D) or None, x displacement map
    :param dymap: numpy array (2D) or None, y displacement map
    :param niter: int, number of fixed-point iterations
    :param order: int, spline interpolation order

    :return: numpy array (2D), image in the reverse-transform frame
    """
    image = np.asarray(image, dtype=float)
    if lin_transform_vect is None and dxmap is None and dymap is None:
        return np.array(image, copy=True)
    xcoord, ycoord = inverse_coordinates(image.shape, lin_transform_vect,
                                          dxmap, dymap, niter)
    valid = np.isfinite(image)
    filled = np.where(valid, image, 0.0)
    result = map_coordinates(filled, [ycoord, xcoord], order=order,
                             cval=np.nan, output=float, mode='constant')
    weights = map_coordinates(valid.astype(float), [ycoord, xcoord],
                              order=order, cval=0.0, output=float,
                              mode='constant')
    with np.errstate(invalid='ignore', divide='ignore'):
        result = result / weights
    result[weights < 0.5] = np.nan
    return result


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
