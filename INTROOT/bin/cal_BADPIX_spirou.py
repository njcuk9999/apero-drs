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

from SpirouDRS import spirouDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouBACK

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
    p = spirouStartup.Begin(recipe=__NAME__)
    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1]
    fmt = [str, str]
    names = ['flatfile', 'darkfile']
    call = [flatfile, darkfile]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(p, pos, fmt, names,
                                                    calls=call)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='flatfile')

    # ----------------------------------------------------------------------
    # Construct the darkfile and flatfile
    # ----------------------------------------------------------------------
    p, flatfilename = spirouStartup.SingleFileSetup(p, filename=p['FLATFILE'],
                                                    pos=0)
    p, darkfilename = spirouStartup.SingleFileSetup(p, filename=p['DARKFILE'],
                                                    pos=1)

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
    # fix for un-preprocessed files
    # ----------------------------------------------------------------------
    fdata = spirouImage.FixNonPreProcess(p, fdata)
    ddata = spirouImage.FixNonPreProcess(p, ddata)

    # ----------------------------------------------------------------------
    # Normalise flat and median of flat
    # ----------------------------------------------------------------------
    flat_med, flat_ref = spirouImage.NormMedianFlat(p, flat_ref)

    # ----------------------------------------------------------------------
    # Locate bad pixels
    # ----------------------------------------------------------------------
    bargs = [p, flat_ref, flat_med, dark_ref]
    bad_pixel_map1, bstats1 = spirouImage.LocateBadPixels(*bargs)

    # ----------------------------------------------------------------------
    # Locate bad pixels from full detector flat
    # ----------------------------------------------------------------------
    bad_pixel_map2, bstats2 = spirouImage.LocateFullBadPixels(p, flat_ref)

    # ----------------------------------------------------------------------
    # Combine bad pixel masks
    # ----------------------------------------------------------------------
    bad_pixel_map = bad_pixel_map1 | bad_pixel_map2
    # total number of bad pixels
    btotal = (np.nansum(bad_pixel_map) / bad_pixel_map.size) * 100
    # log result
    text = 'Fraction of total bad pixels {0:.4f} %'
    WLOG(p, '', text.format(btotal))

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    if p['DRS_PLOT'] > 0:
        # start interactive plot
        sPlt.start_interactive_session(p)
        # plot the data cut
        sPlt.darkplot_datacut(p, bad_pixel_map)
        # end interactive session
        sPlt.end_interactive_session(p)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------

    # rotate the image and convert from ADU/s to e-
    flat1 = spirouImage.FlipImage(p, flat_ref)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    flat1 = spirouImage.ResizeImage(p, flat1, **bkwargs)
    # log change in data size
    wmsg = 'Image format changed to {1}x{0}'
    WLOG(p, '', wmsg.format(*flat1.shape))

    # ----------------------------------------------------------------------
    # rotate the image and convert from ADU/s to e-
    badpixelmap = spirouImage.FlipImage(p, bad_pixel_map)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'],
                   getshape=False)
    badpixelmap = spirouImage.ResizeImage(p, badpixelmap, **bkwargs)
    # log change in data size
    wmsg = 'Bad pixel map format changed to {1}x{0}'
    WLOG(p, '', wmsg.format(*badpixelmap.shape))

    # ----------------------------------------------------------------------
    # Create background map mask
    # ----------------------------------------------------------------------
    backmap = spirouBACK.MakeBackgroundMap(p, flat1, badpixelmap)

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    passed, fail_msg = True, []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # TODO: Needs doing
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if passed:
        WLOG(p, 'info', 'QUALITY CONTROL SUCCESSFUL - Well Done -')
        p['QC'] = 1
        p.set_source('QC', __NAME__ + '/main()')
    else:
        for farg in fail_msg:
            wmsg = 'QUALITY CONTROL FAILED: {0}'
            WLOG(p, 'warning', wmsg.format(farg))
        p['QC'] = 0
        p.set_source('QC', __NAME__ + '/main()')
    # add to qc header lists
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # get raw badpixel file
    raw_badp_file1 = os.path.basename(p['flatfile'])
    raw_badp_file2 = os.path.basename(p['darkfile'])
    # construct bad pixel file name
    badpixelfits, tag = spirouConfig.Constants.BADPIX_FILE(p)
    badpixelfitsname = os.path.split(badpixelfits)[-1]
    # log that we are saving bad pixel map in dir
    WLOG(p, '', 'Saving Bad Pixel Map in ' + badpixelfitsname)
    # add keys from original header files
    # Question Why only the keys from the flat file?
    # hdict = spirouImage.CopyOriginalKeys(dhdr, dcmt)
    hdict = spirouImage.CopyOriginalKeys(fhdr, fcmt)
    # add new keys
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                     values=p['FLATFILE'], dim1name='flatfile')
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE2'],
                                     values=p['DARKFILE'], dim1name='darkfile')
    hdict = spirouImage.AddKey(p, hdict, p['KW_BHOT'], value=bstats1[0])
    hdict = spirouImage.AddKey(p, hdict, p['KW_BBFLAT'], value=bstats1[1])
    hdict = spirouImage.AddKey(p, hdict, p['KW_BNDARK'], value=bstats1[2])
    hdict = spirouImage.AddKey(p, hdict, p['KW_BNFLAT'], value=bstats1[3])
    hdict = spirouImage.AddKey(p, hdict, p['KW_BBAD'], value=bstats1[4])
    hdict = spirouImage.AddKey(p, hdict, p['kw_BNILUM'], value=bstats2)
    hdict = spirouImage.AddKey(p, hdict, p['kw_BTOT'], value=btotal)
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # write to file
    badpixelmap = np.array(badpixelmap, dtype=int)
    p, spirouImage.WriteImage(p, badpixelfits, badpixelmap, hdict)

    # ----------------------------------------------------------------------
    # Save the background map
    # ----------------------------------------------------------------------
    # get raw badpixel file
    raw_badp_file1 = os.path.basename(p['flatfile'])
    raw_badp_file2 = os.path.basename(p['darkfile'])
    # construct background map file name
    backmapfits, tag = spirouConfig.Constants.BKGD_MAP_FILE(p)
    backmapfitsname = os.path.split(backmapfits)[-1]
    # log that we are saving bad pixel map in dir
    WLOG(p, '', 'Saving Bad Pixel Map in ' + backmapfitsname)
    # add keys from original header files
    # Question Why only the keys from the flat file?
    # hdict = spirouImage.CopyOriginalKeys(dhdr, dcmt)
    hdict = spirouImage.CopyOriginalKeys(fhdr, fcmt)
    # add new keys
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_OUTPUT'], value=tag)
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'],
                                     values=p['FLATFILE'], dim1name='flatfile')
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE2'],
                                     values=p['DARKFILE'], dim1name='darkfile')
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # write to file
    backmap = np.array(backmap, dtype=int)
    p, spirouImage.WriteImage(p, backmapfits, backmap, hdict)

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if p['QC']:
        # bad pixel map
        keydb = 'BADPIX'
        # copy dark fits file to the calibDB folder
        spirouDB.PutCalibFile(p, badpixelfits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, badpixelfitsname, fhdr)
        # ------------------------------------------------------------------
        # background mask
        # bad pixel map
        keydb = 'BKGRDMAP'
        # copy dark fits file to the calibDB folder
        spirouDB.PutCalibFile(p, backmapfits)
        # update the master calib DB file with new key
        spirouDB.UpdateCalibMaster(p, keydb, backmapfitsname, fhdr)

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
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================
