#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-03-30 at 14:47

@author: cook
"""
import numpy as np

from apero import core
from apero import locale
from apero.core import constants


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_update_berv.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
Help = locale.drs_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])



# =============================================================================
# Define functions
# =============================================================================
def map_image(params, image, lprops):

    # get pconst
    pconst = constants.pload(params['INSTRUMENT'])
    # get shape from image
    nbxpix = 4096
    nbypix = 4096
    nbo = 49
    fibers = ['A', 'B', 'C']
    # define the shape of the image
    ishape = (nbypix, nbxpix)
    # get center and width coefficients
    ccoeffs = lprops['CENTERS']
    wcoeffs = lprops['WIDTHS']

    # TODO: add tmp file loading (if we have one)

    # construct a NaN filled image for output
    orderimage = np.repeat([-1], np.product(ishape)).reshape(ishape)
    suborderimage = np.repeat([-1], np.product(ishape)).reshape(ishape)
    fiberimage = np.repeat(['00'], np.product(ishape)).reshape(ishape)
    # get the indices locations
    yimage, ximage = np.indices(ishape)
    # loop around number of orders
    for order_num in range(nbo):
        # loop around orders
        for fiber in fibers:
            # get the fiber we should use for localisation
            usefiber = pconst.FIBER_LOC_TYPES(fiber)
            # get the coefficents and number of orders
            acc, nbof = pconst.FIBER_LOC_COEFF_EXT(ccoeffs[usefiber], fiber)
            ass = wcoeffs[usefiber]
            # get central positions
            cfit = np.polyval(acc[order_num], ximage)
            wfit = np.polyval(ass[order_num], ximage)
            # define the upper an dlower bounds of this order
            upper = cfit + wfit / 2
            lower = cfit + wfit / 2
            # define the mask of the pixels in this order
            mask = (yimage < upper) & (yimage > lower)
            # create the order image
            orderimage[mask] = order_num
            fiberimage[mask] = fiber

            # TODO: Question: do we need sub order image?

    # TODO: add saving map images

    # return the map images
    return orderimage, suborderimage, fiberimage


def construct_waveimage(params, image, wprops, lprops, fiberimage):

    # get pconst
    pconst = constants.pload(params['INSTRUMENT'])
    # get shape from image
    nbxpix = 4096
    nbypix = 4096
    nbo = 49
    fibers = ['A', 'B', 'C']

    # construct a NaN filled image for output
    waveimage = np.repeat([np.nan], np.product(nbypix, nbxpix))
    waveimage = waveimage.reshape((nbypix, nbxpix))
    # get the indices locations
    yimage, ximage = np.indices((nbypix, nbxpix))
    # loop around number of orders
    for order_num in range(nbo):

        # loop around orders
        for fiber in fibers:
            # get the fiber we should use for localisation
            usefiber = pconst.FIBER_LOC_TYPES(fiber)
            # get the coefficents and number of orders
            acc, nbof = pconst.FIBER_LOC_COEFF_EXT(lprops[usefiber], fiber)


            # mask for this order
            fibermask = fiberimage == fiber
            # positions where fibermask
            fiberypos, fiberxpos = np.where(fibermask)




# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":




# =============================================================================
# End of code
# =============================================================================