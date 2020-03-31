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

from apero.science.calib import localisation
from apero.science.calib import shape
from apero.core.core import drs_recipe

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
def drs_image_shape(params):
    # get image shape from params
    ylow, yhigh = params['IMAGE_Y_LOW'], params['IMAGE_Y_HIGH']
    xlow, xhigh = params['IMAGE_X_LOW'], params['IMAGE_X_HIGH']
    # return the y and x size --> shape
    return (yhigh - ylow, xhigh - xlow)


def calc_central_localisation(params, recipe, fiber, header=None,
                              filename=None):
    # get the loco image and number of orders for this fiber
    lprops = localisation.get_coefficients(params, recipe, header,
                                           filename=filename,
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


def simage_to_drs(simage, shapex2, shapey):
    pimage = shape.ea_transform(params, simage, dymap=-shapey)
    pimage = shape.ea_transform(params, pimage, dxmap=-shapex2)
    return pimage


def drs_to_pp(params, image, fill=0.0):
    # get full image dimensions (from constants)
    full_y, full_x = params['IMAGE_Y_FULL'], params['IMAGE_X_FULL']
    # get the cut down image size
    ylow, yhigh = params['IMAGE_Y_LOW'], params['IMAGE_Y_HIGH']
    xlow, xhigh = params['IMAGE_X_LOW'], params['IMAGE_X_HIGH']
    # construct shape of output image
    oshape = (full_y, full_x)
    # make zero filled map
    outmap = np.repeat([fill], np.product(oshape)).reshape(oshape)
    # add map to pp out map
    outmap[ylow:yhigh, xlow:xhigh] = image
    # now flip it
    outmap = outmap[::-1, ::-1]
    # return outmap
    return outmap


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # TEST
    from astropy.io import fits
    workspace = '/scratch3/rali/spirou/mini_data/calibDB/'
    workspace1 = '/scratch3/rali/spirou/mini_data/reduced/2019-04-20/'
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
    orderpAB = fits.getdata(workspace + '2019-04-20_2400399f_pp_order_profile_AB.fits')
    orderpC = fits.getdata(workspace + '2019-04-20_2400394f_pp_order_profile_C.fits')

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


    # transform the shape maps
    shapex2 = shape.ea_transform(params, shapex, dymap=-shapey)

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
        # get locofile (remove when we have a header)
        locofile = locofiles[fiber]
        # calculate fiber centers
        print('\t Getting centers')
        cents, wids = calc_central_localisation(params, recipe, fiber,
                                                filename=locofile)
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
                                 fill=0.0, simage=sfp_map)

    # --------------------------------------------------------------------------
    # shift by shape
    # --------------------------------------------------------------------------
    print('MAP --> IMAGE')
    # get shifted order map
    print('\tshifting order map')
    porder_map = simage_to_drs(sorder_map, shapex2, shapey)

    # get shifted position map
    print('\tshifting x map')
    px_map = simage_to_drs(sx_map, shapex2, shapey)

    # get shifted wave map
    print('\tshifting wave map')
    pwave_map = simage_to_drs(swave_map, shapex2, shapey)

    # get shifted wave map
    print('\tshifting fp map')
    pfp_map = simage_to_drs(sfp_map, shapex2, shapey)

    # --------------------------------------------------------------------------
    # apply order profile (after de-straightening)
    # --------------------------------------------------------------------------
    # calculate order profile for full image
    orderp = orderpAB / np.nanmax(orderpAB)
    orderp += orderpC / np.nanmax(orderpC)
    # apply this to maps
    pfp_map = pfp_map * orderp


    # temporary save to pp format (for testing)
    pfp_map[np.isnan(pfp_map)] = 0.0

    outmap = drs_to_pp(params, pfp_map)
    # save it to file
    fits.writeto('outmap.fits', outmap, overwrite=True)



# =============================================================================
# End of code
# =============================================================================