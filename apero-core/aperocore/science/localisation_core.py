#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Order localisation science functions

Pure numpy helpers that turn a set of per-trace order centers/widths into an
integer map of which trace owns each detector pixel, and the label range
each fiber group occupies in that map.

Created on 2025-11-25 at 09:40

@author: cook
"""
from typing import List, Tuple

import numpy as np

from aperocore.base import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'aperocore.science.localisation_core'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__


# =============================================================================
# Define functions
# =============================================================================
def build_order_position_map(shape: Tuple[int, int],
                             fiber_centers: List[np.ndarray],
                             fiber_widths: List[np.ndarray]
                             ) -> Tuple[np.ndarray, np.ndarray,
                                       List[Tuple[int, int]]]:
    """
    Integer map of which trace owns each pixel of a detector image

    0 means the pixel belongs to no trace. Fiber groups are numbered in the
    order they are given: the first fiber group's traces are labelled 1 to
    ntrace1, the second group's traces continue from ntrace1 + 1, and so on.

    Where two traces overlap, a pixel goes to whichever trace centre is
    nearer, rather than to whichever trace happened to be written last.

    :param shape: tuple, (ny, nx), the shape of the detector image
    :param fiber_centers: list of numpy arrays, one 2D array (ntrace, nx)
                          per fiber group, the y center of each trace at
                          each column x
    :param fiber_widths: list of numpy arrays, one 1D array (ntrace,) per
                         fiber group, the (full) width of each trace

    :return: tuple, 1. the integer map of trace labels (0 = none), 2. the
             label range (first, last) of each fiber group (in the order
             given), 3. an integer map of the nearest trace to each pixel,
             whether or not the pixel actually falls inside that trace
    """
    ny, nx = shape
    omap = np.zeros(shape, dtype=np.int32)
    # nearest trace whatever the distance, which says which trace a pixel
    #   between two traces belongs to
    nearest = np.zeros(shape, dtype=np.int32)
    nearest_d = np.full(shape, np.inf)
    # distance to the owning trace, so an overlap can be arbitrated
    closest = np.full(shape, np.inf)
    ranges = []
    offset = 0
    # loop around fiber groups (e.g. 'AB' then 'C')
    for centers, widths in zip(fiber_centers, fiber_widths):
        centers = np.asarray(centers, dtype=float)
        widths = np.asarray(widths, dtype=float)
        ntrace = centers.shape[0]
        ranges.append((offset + 1, offset + ntrace))
        # loop around each trace of this fiber group
        for itrace in range(ntrace):
            cen = centers[itrace]
            half = widths[itrace] / 2.0
            # only the rows this trace can reach
            ylo = int(max(np.floor(np.nanmin(cen) - half), 0))
            yhi = int(min(np.ceil(np.nanmax(cen) + half) + 1, ny))
            if yhi <= ylo:
                continue
            rows = np.arange(ylo, yhi)[:, np.newaxis]
            dist = np.abs(rows - cen[np.newaxis, :])
            # nearest trace, no width condition
            closer = dist < nearest_d[ylo:yhi]
            subn = nearest[ylo:yhi]
            subn[closer] = offset + itrace + 1
            nearest[ylo:yhi] = subn
            subnd = nearest_d[ylo:yhi]
            subnd[closer] = dist[closer]
            nearest_d[ylo:yhi] = subnd
            # the trace that owns the pixel, which needs the width
            take = (dist <= half) & (dist < closest[ylo:yhi])
            sub = omap[ylo:yhi]
            sub[take] = offset + itrace + 1
            omap[ylo:yhi] = sub
            subd = closest[ylo:yhi]
            subd[take] = dist[take]
            closest[ylo:yhi] = subd
        offset += ntrace
    return omap, nearest, ranges


def order_ranges_from_widths(fiber_widths: List[np.ndarray]
                             ) -> List[Tuple[int, int]]:
    """
    Label range each fiber group occupies, without building the full map

    Same numbering scheme as build_order_position_map: the first fiber
    group's traces are labelled 1 to ntrace1, the second group continues
    from there, and so on. Useful when the map itself is cached and only the
    ranges are needed.

    :param fiber_widths: list of numpy arrays, one 1D array (ntrace,) per
                         fiber group, the width of each trace (only the
                         number of traces is used here)

    :return: list of tuple, the (first, last) label of each fiber group, in
             the order given
    """
    ranges = []
    offset = 0
    for widths in fiber_widths:
        ntrace = len(widths)
        ranges.append((offset + 1, offset + ntrace))
        offset += ntrace
    return ranges


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
