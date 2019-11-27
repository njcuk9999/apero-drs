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

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouDB
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'obj_mk_obj_template.py'
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
    loc['DATA'], loc['DATAHDR'] = rdata[:2]

    # Get output key
    loc['OUTPUT'] = loc['DATAHDR'][p['KW_OUTPUT'][0]]
    # set source
    source = main_name + '+ spirouImage.ReadParams()'
    loc.set_source('OUTPUT', source)

    # ----------------------------------------------------------------------
    # Get database files
    # ----------------------------------------------------------------------
    # get current telluric maps from telluDB
    files, output_codes = [], []
    # filter by object name (only keep OBJNAME objects) and only keep
    #   unique filenames
    use_files = []
    for it in range(len(files)):
        # check that OUTPUT is correct
        cond1 = p['KW_OUTPUT'] in output_codes[it]
        # check that filename is not already used
        cond2 = files[it] not in use_files
        # append to file list if criteria correct
        if cond1 and cond2:
            use_files.append(files[it])

    # log if we have no files
    if len(use_files) == 0:
        wmsg = 'No files found for OUTPUT ="{0}" skipping'
        WLOG(p, 'warning', wmsg.format(loc['KW_OUTPUT']))
        # End Message
        wmsg = 'Recipe {0} has been successfully completed'
        WLOG(p, 'info', wmsg.format(p['PROGRAM']))
        # return a copy of locally defined variables in the memory
        return dict(locals())
    else:
        # log how many found
        wmsg = 'N={0} files found for OUTPUT="{1}"'
        WLOG(p, '', wmsg.format(len(use_files), loc['OUTPUT']))

    # ----------------------------------------------------------------------
    # Set up storage for cubes (NaN arrays)
    # ----------------------------------------------------------------------
    # set up flat size
    dims = [loc['DATA'].shape[0], loc['DATA'].shape[1], len(use_files)]
    flatsize = np.product(dims)
    # create NaN filled storage
    big_cube = np.repeat([np.nan], flatsize).reshape(*dims)
    big_cube0 = np.repeat([np.nan], flatsize).reshape(*dims)

    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
        # get master wave map
        loc['MASTERWAVEFILE'] = spirouDB.GetDatabaseMasterWave(p)
    # read master wave map
    mout = spirouImage.GetWaveSolution(p, filename=loc['MASTERWAVEFILE'],
                                       return_wavemap=True, quiet=True,
                                       fiber=wave_fiber)
    loc['MASTERWAVEPARAMS'], loc['MASTERWAVE'], loc['WSOURCE'] = mout
    keys = ['MASTERWAVEPARAMS', 'MASTERWAVE', 'MASTERWAVEFILE', 'WSOURCE']
    loc.set_sources(keys, main_name)

    # ----------------------------------------------------------------------
    # Loop through input files
    # ----------------------------------------------------------------------
    base_filelist, berv_list = [], []
    # loop through files
    for it, filename in enumerate(use_files):
        # get base filenmae
        basefilename = os.path.basename(filename)
        # append basename to file list
        base_filelist.append(basefilename)
        # ------------------------------------------------------------------
        # Load the data for this file
        tdata, thdr, _, _ = spirouImage.ReadImage(p, filename)
        # ------------------------------------------------------------------
        # log stats
        wmsg = 'Processing file {0} of {1} file={2}'
        wargs = [it + 1, len(use_files), basefilename]
        WLOG(p, '', wmsg.format(*wargs))
        # ------------------------------------------------------------------
        # add to cube storage
        big_cube0[:, :, it] = tdata

    # ----------------------------------------------------------------------
    # Save cubes to file
    # ----------------------------------------------------------------------
    # get raw file name
    raw_in_file = os.path.basename(p['FITSFILENAME'])
    # construct file names
    outfile = raw_in_file.replace('.fits', '_stack.fits')
    tag = loc['OUTPUT'] + '_STACK'
    # log big cube 1
    wmsg1 = 'Saving bigcube to file {0}'.format(os.path.basename(outfile))

    # hdict is first file keys
    hdict = spirouImage.CopyOriginalKeys(loc['DATAHDR'])
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    # set the input files
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBBLAZE'], value=p['BLAZFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'],
                               value=loc['MASTERWAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    # add file list to header
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_OBJFILELIST'],
                                     values=base_filelist)
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_OBJBERVLIST'],
                                     values=berv_list)
    # add wave solution coefficients
    hdict = spirouImage.AddKey2DList(p, hdict, p['KW_WAVE_PARAM'],
                                     values=loc['MASTERWAVEPARAMS'])
    # log big cube 0
    wmsg = 'Saving bigcube0 to file {0}'.format(os.path.basename(outfile))
    # save big cube 0
    big_cube_s0 = np.swapaxes(big_cube0, 1, 2)
    p = spirouImage.WriteImageMulti(p, outfile, big_cube_s0, hdict)

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
