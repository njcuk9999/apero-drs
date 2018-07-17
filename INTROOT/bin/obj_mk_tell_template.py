#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

obj_mk_tell_Template.py NIGHT_NAME FILES

REFFILE = FILES[0] This is the file used to get the object name and date from
the header (used for getting/setting telluric/calibration database info
(saved into telluDB under "TELL_TEMP
" keys)

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
from SpirouDRS import spirouTelluric

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
def main(night_name=None, files=None):

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    p = spirouStartup.LoadArguments(p, night_name, files,
                                    mainfitsdir='reduced')
    p = spirouStartup.InitialFileSetup(p, calibdb=True)
    # set up function name
    main_name = __NAME__ + '.main()'

    # ----------------------------------------------------------------------
    # load up first file
    # ----------------------------------------------------------------------
    # construct loc parameter dictionary for storing data
    loc = ParamDict()
    # read first file and assign values
    rdata = spirouImage.ReadImage(p, p['FITSFILENAME'])
    loc['DATA'], loc['DATAHDR'], loc['DATACDR'] = rdata[:3]
    # TODO: Question: Is this per star? If so should the original file be
    # TODO: Question:   a user input --> No input file would require objname
    # TODO: Question:   from somewhere else?
    # TODO: Add constants to constant file
    if p['KW_OBJNAME'][0] in loc['DATAHDR']:
        p['TELLU_TEMPLATE_OBJ'] = loc['DATAHDR'][p['KW_OBJNAME'][0]]
    else:
        emsg = 'HEADER key = {0} not in file = {1}'
        eargs = [p['KW_OBJNAME'][0], p['FITSFILENAME']]
        WLOG('error', p['LOG_OPT'], emsg.format(*eargs))

    # ------------------------------------------------------------------
    # Get the wave solution
    # ------------------------------------------------------------------
    loc['WAVE'] = spirouImage.GetWaveSolution(p, loc['DATA'], loc['DATAHDR'])
    # set source
    loc.set_source('WAVE', main_name)

    # ----------------------------------------------------------------------
    # Get database files
    # ----------------------------------------------------------------------
    # get current telluric maps from telluDB
    tellu_db_data = spirouDB.GetDatabaseTellMap(p)
    tellu_db_files, tellu_db_names = tellu_db_data[0], tellu_db_data[1]
    # filter by object name (only keep TELLU_TEMPLATE_OBJ objects
    tell_files = []
    for it in range(len(tellu_db_files)):
        if p['TELLU_TEMPLATE_OBJ'] in tellu_db_names[it]:
            tell_files.append(tellu_db_files[it])


    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # set up flat size
    dims = [loc['DATA'].shape[0], loc['DATA'].shape[1], len(tell_files)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_cube0 = np.repeat([np.nan], flatsize).reshape(*dims)

    # ----------------------------------------------------------------------
    # Loop around files
    # ----------------------------------------------------------------------
    for it, filename in enumerate(tell_files):
        # get base filenmae
        basefilename = os.path.basename(filename)
        # create image for storage
        image = np.repeat([np.nan], np.product(loc['DATA'].shape))
        image = image.reshape(loc['DATA'].shape)
        # Load the data for this file
        tdata, thdr, tcdr, _, _ = spirouImage.ReadImage(p, filename)
        # Get the Barycentric correction from header
        dv, _, _ = spirouTelluric.GetBERV(p, thdr)

        # log stats
        wmsg = 'Processing file {0} of {1} file={2} dv={3}'
        wargs = [it + 1, len(tell_files), basefilename]

        # loop around orders
        for order_num in range(loc['DATA'].shape[0]):
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
    # Write Cube median (the template) to file
    # ----------------------------------------------------------------------
    # TODO: move file definition to spirouConfig
    reduced_dir = p['DRS_DATA_REDUC']
    outfilename = 'Template_{0}.fits'.format(p['TELLU_TEMPLATE_OBJ'])
    outfile = os.path.join(reduced_dir, outfilename)

    # hdict is first file keys
    hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'], loc['DATACDR'])
    # write to file
    spirouImage.WriteImage(outfilename, big_cube_med, hdict)


    # ----------------------------------------------------------------------
    # Update the telluric database with the template
    # ----------------------------------------------------------------------
    spirouDB.UpdateDatabaseTellTemp(p, outfilename, loc['DATAHDR'])

    # ----------------------------------------------------------------------
    # Save cubes to file
    # ----------------------------------------------------------------------
    reduced_dir = p['DRS_DATA_REDUC']
    outfilename1 = 'BigCube_{0}.fits'.format(p['TELLU_TEMPLATE_OBJ'])
    outfile1 = os.path.join(reduced_dir, outfilename)
    outfilename2 = 'BigCube0_{0}.fits'.format(p['TELLU_TEMPLATE_OBJ'])
    outfile2 = os.path.join(reduced_dir, outfilename)

    spirouImage.WriteImageMulti(outfile1, big_cube, hdict)
    spirouImage.WriteImageMulti(outfile2, big_cube0, hdict)

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
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================





