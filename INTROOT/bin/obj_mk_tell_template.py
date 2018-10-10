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

    # Get object name and airmass
    loc['OBJNAME'] = spirouImage.GetObjName(p, loc['DATAHDR'])
    loc.set_source('OBJNAME', main_name)
    loc['AIRMASS'] = spirouImage.GetAirmass(p, loc['DATAHDR'])
    # set source
    source = main_name + '+ spirouImage.ReadParams()'
    loc.set_sources(['OBJNAME', 'AIRMASS'], source)

    # ------------------------------------------------------------------
    # Get the wave solution
    # ------------------------------------------------------------------
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # get wave solution
    wout = spirouImage.GetWaveSolution(p, image=loc['DATA'], hdr=loc['DATAHDR'],
                                       return_wavemap=True, fiber=wave_fiber,
                                       return_filename=True)
    _, loc['WAVE'], loc['WAVEFILE'] = wout
    loc.set_sources(['WAVE', 'WAVEFILE'], main_name)

    # ----------------------------------------------------------------------
    # Get and Normalise the blaze
    # ----------------------------------------------------------------------
    p, loc = spirouTelluric.GetNormalizedBlaze(p, loc, loc['DATAHDR'])

    # ----------------------------------------------------------------------
    # Get database files
    # ----------------------------------------------------------------------
    # get current telluric maps from telluDB
    tellu_db_data = spirouDB.GetDatabaseTellObj(p, required=False)
    tellu_db_files, tellu_db_names = tellu_db_data[0], tellu_db_data[1]
    # filter by object name (only keep OBJNAME objects
    tell_files = []
    for it in range(len(tellu_db_files)):
        if loc['OBJNAME'] in tellu_db_names[it]:
            tell_files.append(tellu_db_files[it])

    # log if we have no files
    if len(tell_files) == 0:
        wmsg = 'No "TELL_OBJ" files found for object ="{0}" skipping'
        WLOG('warning', p['LOG_OPT'], wmsg.format(loc['OBJNAME']))
        # End Message
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
        # return a copy of locally defined variables in the memory
        return dict(locals())
    else:
        # log how many found
        wmsg = '{0} "TELL_OBJ" filesfround for object ="{1}"'
        WLOG('', p['LOG_OPT'], wmsg.format(len(tell_files), loc['OBJNAME']))

    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # set up flat size
    dims = [loc['DATA'].shape[0], loc['DATA'].shape[1], len(tell_files)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_cube0 = np.repeat([np.nan], flatsize).reshape(*dims)

    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=loc['MASTERWAVEFILE'],
                                       return_wavemap=True, quiet=True,
                                       fiber=wave_fiber)
    _, loc['MASTERWAVE'] = mout
    loc.set_source('MASTERWAVE', main_name)

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
        # Correct for the blaze
        tdata = tdata * loc['NBLAZE']
        # Get the Barycentric correction from header
        dv, _, _ = spirouTelluric.GetBERV(p, thdr)

        # log stats
        wmsg = 'Processing file {0} of {1} file={2} dv={3}'
        wargs = [it + 1, len(tell_files), basefilename]

        # shift to correct berv
        # TODO: Should be realivistic
        dvshift = (1 - dv / CONSTANT_C)

        image = spirouTelluric.Wave2Wave(tdata, loc['WAVE'] * dvshift,
                                         loc['MASTERWAVE'])

        # loop around orders
        for order_num in range(loc['DATA'].shape[0]):
            # normalise the tdata
            tdata[order_num, :] /= np.nanmedian(tdata[order_num, :])
            image[order_num, :] /= np.nanmedian(image[order_num, :])

        # add to cube storage
        big_cube[:, :, it] = image
        big_cube0[:, :, it] = tdata

    # make median image
    big_cube_med = np.median(big_cube, axis=2)

    # ----------------------------------------------------------------------
    # Write Cube median (the template) to file
    # ----------------------------------------------------------------------
    # get raw file name
    raw_in_file = os.path.basename(p['FITSFILENAME'])
    # construct filename
    outfile, tag = spirouConfig.Constants.TELLU_TEMPLATE_FILE(p, loc)
    outfilename = os.path.basename(outfile)

    # hdict is first file keys
    hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'], loc['DATACDR'])
    # add version number
    hdict = spirouImage.AddKey(hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(hdict, p['KW_OUTPUT'], value=tag)
    # set the input files
    hdict = spirouImage.AddKey(hdict, p['KW_BLAZFILE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(hdict, p['kw_INFILE'], value=raw_in_file)
    hdict = spirouImage.AddKey(hdict, p['KW_WAVEFILE'],
                               value=loc['WAVEFILE'])
    # write to file
    p = spirouImage.WriteImage(p, outfile, big_cube_med, hdict)

    # ----------------------------------------------------------------------
    # Update the telluric database with the template
    # ----------------------------------------------------------------------
    objname = loc['OBJNAME']
    spirouDB.UpdateDatabaseTellTemp(p, outfilename, objname, loc['DATAHDR'])
    # put file in telluDB
    spirouDB.PutTelluFile(p, outfile)

    # ----------------------------------------------------------------------
    # Save cubes to file
    # ----------------------------------------------------------------------
    reduced_dir = p['DRS_DATA_REDUC']
    outfilename1 = 'BigCube_{0}.fits'.format(loc['OBJNAME'])
    outfile1 = os.path.join(reduced_dir, outfilename)
    outfilename2 = 'BigCube0_{0}.fits'.format(loc['OBJNAME'])
    outfile2 = os.path.join(reduced_dir, outfilename)

    spirouImage.WriteImageMulti(outfile1, big_cube, hdict)
    spirouImage.WriteImageMulti(outfile2, big_cube0, hdict)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p)
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
