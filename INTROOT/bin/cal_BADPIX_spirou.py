#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_BADPIX_spirou.py [night_directory] [flat_flat_*.fits] [dark_dark_*.fits]

Recipe to generate the bad pixel map

Created on 2017-12-06 at 14:50

@author: cook

Last modified: 2017-12-11 at 15:23

Up-to-date with cal_BADPIX_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_BADPIX_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, flatfile=None, darkfile=None):
    """
    cal_BADPIX_spirou.py main function, if arguments are None uses
    arguments from run time i.e.:
        cal_BADPIX_spirou.py [night_directory] [flatfile] [darkfile]

    :param night_name: string or None, the folder within data raw directory
                                containing files (also reduced directory) i.e.
                                /data/raw/20170710 would be "20170710" but
                                /data/raw/AT5/20180409 would be "AT5/20180409"
    :param flatfile: string, the flat file to use
    :param darkfile: string, the dark file to use

    :return ll: dictionary, containing all the local variables defined in
                main
    """
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1]
    fmt = [str, str]
    names = ['flatfile', 'darkfile']
    call = [flatfile, darkfile]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(pos, fmt, names, calls=call)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='flatfile')

    # ----------------------------------------------------------------------
    # Construct the darkfile and flatfile
    # ----------------------------------------------------------------------
    # get raw directory + night name
    raw_dir = p['raw_dir']
    # construct and test the flatfile
    flatfilename = spirouStartup.GetFile(p, raw_dir, p['flatfile'], 'flat_flat',
                                         'FLAT')
    # construct and test the darkfile
    darkfilename = spirouStartup.GetFile(p, raw_dir, p['darkfile'], 'dark_dark',
                                         'DARK')

    # ----------------------------------------------------------------------
    # Read the darkfile and flatfile
    # ----------------------------------------------------------------------
    # Read the flat file
    fdata = spirouImage.ReadImage(p, flatfilename, kind='FLAT')
    flat_ref, fhdr, fcmt, nx1, ny1 = fdata
    # Read the dark file
    ddata = spirouImage.ReadImage(p, darkfilename, kind='DARK')
    dark_ref, dhdr, dcmt, nx2, ny2 = ddata

    # ----------------------------------------------------------------------
    # Normalise flat and median of flat
    # ----------------------------------------------------------------------
    # TODO: method = new
    flat_med, flat_ref = spirouImage.NormMedianFlat(p, flat_ref)

    # ----------------------------------------------------------------------
    # Locate bad pixels
    # ----------------------------------------------------------------------
    bargs = [p, flat_ref, flat_med, dark_ref]
    bad_pixel_map1, bstats = spirouImage.LocateBadPixels(*bargs)

    # ----------------------------------------------------------------------
    # Locate bad pixels from full detector flat
    # ----------------------------------------------------------------------
    bad_pixel_map2 = spirouImage.LocateFullBadPixels(p, flat_ref)

    # ----------------------------------------------------------------------
    # Combine bad pixel masks
    # ----------------------------------------------------------------------
    bad_pixel_map = bad_pixel_map1 | bad_pixel_map2

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()
        # plot the data cut
        sPlt.darkplot_datacut(bad_pixel_map)
        # end interactive session
        sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    badpixelmap = spirouImage.FlipImage(bad_pixel_map)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    badpixelmap = spirouImage.ResizeImage(badpixelmap, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], ('Image format changed to '
                            '{0}x{1}').format(*badpixelmap.shape[::-1]))

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    # TODO: Needs doing
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG('info', p['log_opt'], 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG('info', p['log_opt'], wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # construct bad pixel file name
    badpixelfits = spirouConfig.Constants.BADPIX_FILE(p)
    badpixelfitsname = os.path.split(badpixelfits)[-1]
    # log that we are saving bad pixel map in dir
    WLOG('', p['log_opt'], 'Saving Bad Pixel Map in ' + badpixelfitsname)
    # add keys from original header files
    # Question Why only the keys from the flat file?
    # hdict = spirouImage.CopyOriginalKeys(dhdr, dcmt)
    hdict = spirouImage.CopyOriginalKeys(fhdr, fcmt)
    # add new keys
    hdict = spirouImage.AddKey(hdict, p['kw_BHOT'], value=bstats[0])
    hdict = spirouImage.AddKey(hdict, p['kw_BBFLAT'], value=bstats[1])
    hdict = spirouImage.AddKey(hdict, p['kw_BNDARK'], value=bstats[2])
    hdict = spirouImage.AddKey(hdict, p['kw_BNFLAT'], value=bstats[3])
    hdict = spirouImage.AddKey(hdict, p['kw_BBAD'], value=bstats[4])

    # write to file
    badpixelmap = np.array(badpixelmap, dtype=int)
    spirouImage.WriteImage(badpixelfits, badpixelmap, hdict)

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        keydb = 'BADPIX'
        # copy dark fits file to the calibDB folder
        spirouCDB.PutFile(p, badpixelfits)
        # update the master calib DB file with new key
        spirouCDB.UpdateMaster(p, keydb, badpixelfitsname, fhdr)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))
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
