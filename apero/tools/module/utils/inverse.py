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





def calc_central_localisation(params, recipe, fiber):

    # get locofile (remove when we have a header)
    locofile = locofiles[fiber]
    # get the loco image and number of orders for this fiber
    # TODO: change when we have header
    lprops = localisation.get_coefficients(params, recipe, None,
                                           filename=locofile,
                                           fiber=fiber, merge=True)
    # store centers and widths
    centers, widths = [], []
    # loop around orders
    for order_num in range(lprops['NBO']):
        # get coefficents
        acc = lprops['CENT_COEFFS'][order_num][::-1]
        ass = lprops['WID_COEFFS'][order_num][::-1]
        # get value at xpix center of detector
        cfit = np.polyval(acc, nbxpix // 2)
        wfit = np.polyval(ass, nbxpix // 2)
        # store to file
        centers.append(cfit)
        widths.append(wfit)
    # return centers and widths
    return centers, widths


def e2ds_to_simage(e2ds, xpixels, ypixels, centers, widths,
                   fill=np.nan, simage=None):
    # get the shape of the simage
    ishape = xpixels.shape
    # define output input
    if simage is None:
        simage = np.repeat([fill], np.product(ishape)).reshape(ishape)
    # loop around orders
    for order_num in range(e2ds.shape[0]):
        # get order e2ds values
        values = e2ds[order_num]
        cfit = centers[order_num]
        wfit = widths[order_num]
        # define the mask
        mask = (ypixels < (cfit + wfit / 2))
        mask &= (ypixels > (cfit - wfit / 2))
        # update simage (set all ypix in order for each xpix)
        for xpix in xpixels[0]:
            simage[:, xpix][mask[:, xpix]] = values[xpix]
    # return simage
    return simage


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    from apero.science.calib import localisation
    from apero.science.calib import shape
    from apero.core.core import drs_recipe
    from apero.core import constants
    # TEST
    from astropy.io import fits
    workspace = '/scratch3/rali/spirou/mini_data_closest_20200328/calibDB/'
    workspace1 = '/scratch3/rali/spirou/mini_data_closest_20200328/reduced/2019-04-20/'
    locofileAB = workspace + '2019-04-20_2400399f_pp_loco_AB.fits'
    locofileC = workspace + '2019-04-20_2400550f_pp_loco_C.fits'
    shapex = fits.getdata(workspace + '2019-04-20_2400409a_pp_shapex.fits')
    shapey = fits.getdata(workspace + '2019-04-20_2400409a_pp_shapey.fits')
    waveA = fits.getdata(workspace + '2019-04-20_2400416c_pp_e2dsff_A_wavem_fp_A.fits')
    waveB = fits.getdata(workspace + '2019-04-20_2400416c_pp_e2dsff_B_wavem_fp_B.fits')
    waveC = fits.getdata(workspace + '2019-04-20_2400416c_pp_e2dsff_C_wavem_fp_C.fits')
    fpA = fits.getdata(workspace1 + '2400565a_pp_e2dsff_A.fits')
    fpB = fits.getdata(workspace1 + '2400565a_pp_e2dsff_B.fits')
    fpC = fits.getdata(workspace1 + '2400565a_pp_e2dsff_C.fits')

    locofiles = dict(A=locofileAB, B=locofileAB, C=locofileC)
    fpfiles = dict(A=fpA, B=fpB, C=fpC)
    wavefiles = dict(A=waveA, B=waveB, C=waveC)
    nbxpix = 4088
    nbypix = 3100
    nbo = 49
    fibers = ['A', 'B', 'C']
    params = constants.load('SPIROU')
    recipe = drs_recipe.make_default_recipe(params, name='test')
    ishape = (nbypix, nbxpix)
    eshape = (nbo, nbxpix)
    # get the x and y position images
    yimage, ximage = np.indices(ishape)

    # e2ds order map
    order_map = np.repeat([-1], np.product(eshape)).reshape(eshape)
    for order_num in range(nbo):
        order_map[order_num] = order_num

    x_map = np.repeat([np.nan], np.product(eshape)).reshape(eshape)
    for order_num in range(nbo):
        x_map[order_num] = np.arange(nbxpix)

    # start the maps as unset
    sorder_map = None
    sx_map = None
    sfp_map = None
    swave_map = None
    # loop around fibers
    for fiber in fibers:
        print('E2DS-->MAP: Fiber {0}'.format(fiber))
        # calculate fiber centers
        print('\t Getting centers')
        cents, wids = calc_central_localisation(params, recipe, fiber)
        # get straighted image for order map
        print('\t Getting order map')
        sorder_map = e2ds_to_simage(order_map, ximage, yimage, cents, wids,
                                    fill=-1, simage=sorder_map)
        # get straighted image for ximage map
        print('\t Getting x map')
        sx_map = e2ds_to_simage(x_map, ximage, yimage, cents, wids,
                                     fill=np.nan, simage=sx_map)
        # get straighted wave image
        print('\t Getting wave map')
        swave_map =  e2ds_to_simage(wavefiles[fiber], ximage, yimage, cents,
                                    wids, fill=np.nan, simage=swave_map)
        # get straighted fp image
        print('\t Getting fp map')
        sfp_map = e2ds_to_simage(fpfiles[fiber], ximage, yimage, cents, wids,
                                 fill=np.nan, simage=sfp_map)
    # --------------------------------------------------------------------------
    # shift by shape
    # --------------------------------------------------------------------------
    print('MAP --> IMAGE')
    # get shifted order map
    print('\tshifting order map')
    porder_map = shape.ea_transform(params, sorder_map, dxmap=-shapex,
                                    dymap=-shapey)
    # get shifted position map
    print('\tshifting x map')
    px_map = shape.ea_transform(params, sx_map, dxmap=-shapex, dymap=-shapey)
    # get shifted wave map
    print('\tshifting wave map')
    pwave_map = shape.ea_transform(params, swave_map, dxmap=-shapex,
                                   dymap=-shapey)
    # get shifted wave map
    print('\tshifting fp map')
    pfp_map = shape.ea_transform(params, sfp_map, dxmap=-shapex, dymap=-shapey)





# =============================================================================
# End of code
# =============================================================================