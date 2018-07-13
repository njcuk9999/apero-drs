#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2018-07-13 05:16
@author: ncook
Version 0.0.1
"""
from __future__ import division
import numpy as np
from astropy import constants
import os
from scipy.interpolate import InterpolatedUnivariateSpline as IUVSpline

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'obj_mk_tell_template.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Custom parameter dictionary
ParamDict = spirouConfig.ParamDict
# Get sigma FWHM
SIG_FWHM = spirouCore.spirouMath.fwhm
# Get plotting functions
sPlt = spirouCore.sPlt
# get speed of light
# noinspection PyUnresolvedReferences
CONSTANT_C = constants.c.value


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name)
    p = spirouStartup.InitialFileSetup(p, calibdb=True, no_files=True)

    # TODO: Add constants to constant file
    p['TELLU_TEMPLATE_OBJ'] = 'Gl699'

    p['TELLU_TEMPLATE_KEEP_LIMIT'] = 0.5

    p['TELLU_TEMPLATE_MED_LOW'] = 2048 - 128
    p['TELLU_TEMPLATE_MED_HIGH'] = 2048 + 128


    # ----------------------------------------------------------------------
    # Get database files
    # ----------------------------------------------------------------------
    # get current telluric maps from telluDB
    tellu_db_data = spirouDB.GetDatabaseTellMap(p)
    tellu_db_files, tellu_db_names = tellu_db_data[0]
    # filter by object name (only keep TELLU_TEMPLATE_OBJ objects
    files = []
    for it in range(len(tellu_db_files)):
        if p['TELLU_TEMPLATE_OBJ'] in tellu_db_names[it]:
            files.append(tellu_db_files[it])

    # ----------------------------------------------------------------------
    # load up first file
    # ----------------------------------------------------------------------
    # construct loc parameter dictionary for storing data
    loc = ParamDict()
    # define fits filename as first file
    p['FITSFILENAME'] = files[0]
    # read first file and assign values
    rdata = spirouImage.ReadImage(p, files[0])
    loc['DATA'], loc['DATAHDR'], loc['DATACDR'] = rdata[:3]

    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # set up flat size
    dims = [loc['DATA'].shape[0], loc['DATA'].shape[1], len(files)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_cube0 = np.repeat([np.nan], flatsize).reshape(*dims)

    # ----------------------------------------------------------------------
    # Loop around files
    # ----------------------------------------------------------------------
    for it, filename in enumerate(files):
        # get base filenmae
        basefilename = os.path.basename(filename)
        # create image for storage
        image = np.repeat([np.nan], np.product(loc['DATA'].shape))
        image = image.reshape(loc['DATA'].shape)
        # Load the data for this file
        tdata, thdr, tcdr, _, _ = spirouImage.ReadImage(p, filename)
        # Check for BERV key in header
        if p['KW_BERV'][0] not in thdr:
            emsg = 'HEADER error, file="{0}". Keyword {1} not found'
            eargs = [filename, p['KW_BERV'][0]]
            WLOG('error', p['LOG_OPT'], emsg.format(*eargs))
        # Get the Barycentric correction from header
        dv = thdr[p['KW_BERV'][0]]

        # log stats
        wmsg = 'Processing file {0} of {1} file={2} dv={3}'
        wargs = [it + 1, len(files), basefilename]

        # loop around orders
        for order_num in range(loc['DATA'][0]):
            # find nans
            keep = np.isfinite(tdata[order_num, :])
            # normalise the tdata
            tdata[order_num, :] /= np.median(tdata[order_num, :][keep])
            # update nan mask
            keep = np.isfinite(tdata[order_num, :])
            # if we have more than half our values spline otherwise disregard
            if np.sum(keep) > (p['TELLU_TEMPLATE_KEEP_LIMIT'] * len(keep)):
                # get wavelengths for keep mask
                keepwave = loc['WAVE'][order_num][keep]
                # get spectrum for keep mask
                keepsp = tdata[order_num][keep]
                # get spline fit
                spline = IUVSpline(keepwave, keepsp, k=2, ext=1)
                # get dv shift
                dvshift = (1 - dv / CONSTANT_C)
                # fit all points with the spline fit and add shift
                image[order_num, :] = spline(loc['WAVE'][order_num]) * dvshift
                # set zero values to NaN
                zeromask = image[order_num, :] == 0
                image[order_num, :][zeromask] = np.nan
                # renomalise the image to the median over defined area
                start = p['TELLU_TEMPLATE_MED_LOW']
                end = p['TELLU_TEMPLATE_MED_HIGH']
                image[order_num, :] /= np.nanmedian(image[order_num, start:end])
            # else just set whole order to NaNs
            else:
                image[order_num, :] = np.nan

        # add to cube storage
        big_cube[:, :, it] = image
        big_cube0[:, :, it] = tdata

    # make median image
    big_cube_med = np.median(big_cube, axis=2)

    # ----------------------------------------------------------------------
    # Save cubes to file
    # ----------------------------------------------------------------------

    # TODO: move to spirou
    # TODO: move file definitions to spirouConfig
    fits.writeto('tmp.fits', big_cube, clobber=True)
    fits.writeto('tmp0.fits', big_cube0, clobber=True)

    # TODO: move file definition to spirouConfig
    reduced_dir = p['DRS_DATA_REDUC']
    outfilename = 'Template_{0}.fits'.format(p['TELLU_TEMPLATE_OBJ'])
    outfile = os.path.join(reduced_dir, outfilename)

    # hdict is first file keys
    hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'], loc['DATACDR'])
    # write to file
    spirouImage.WriteImage(outfilename, big_cube_med, hdict)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================





