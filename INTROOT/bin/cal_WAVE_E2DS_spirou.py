#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_WAVE_E2DS_spirou.py [night_directory] [HCfitsfilename] [FPfitsfilename]

Wavelength calibration incorporating the FP lines

Created on 2018-02-09 at 10:57

@author: cook
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_WAVE_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
# Get parameter dictionary
ParamDict = spirouConfig.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, hcfiles=None, fpfile=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    if hcfiles is None or fpfile is None:
        names, types = ['fpfile', 'hcfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime([0, 1], types, names,
                                                        last_multi=True)
    else:
        customargs = dict(hcfiles=hcfiles, fpfile=fpfile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs)
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Construct filenames and get fiber type
    # ----------------------------------------------------------------------
    # get reduced directory + night name
    rdir = p['reduced_dir']
    # construct and test the hcfile
    fpfitsfilename = spirouStartup.GetFile(p, rdir, p['fpfile'], 'fp', 'FP')
    # construct and test fpfile
    hcfilenames = spirouStartup.GetFiles(p, rdir, p['hcfiles'], 'hc', 'HC')
    # set the hcfilename to the first hcfilenames
    hcfitsfilename = hcfilenames[0]

    # get the fiber type
    fiber1 = spirouStartup.GetFiberType(p, fpfitsfilename)
    fiber2 = spirouStartup.GetFiberType(p, hcfilenames[0])
    if fiber1 == fiber2:
        p['fiber'] = fiber1
        fsource = __NAME__ + '/main() & spirouStartup.GetFiberType()'
        p.set_source('fiber', fsource)
    else:
        emsg = 'Fiber not matching for {0} and {1}, should be the same'
        eargs = [hcfitsfilename, fpfitsfilename]
        WLOG('error', p['log_opt'], emsg.format(*eargs))

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read and combine all HC files except the last (fpfitsfilename)
    rargs = [p, 'add', hcfitsfilename, hcfilenames[1:]]
    data, hdr, cdr, nx, ny = spirouImage.ReadImageAndCombine(*rargs)
    # read last file (fpfitsfilename)
    data3, hdr3, cdr3, nx3, ny3 = spirouImage.ReadImage(p, fpfitsfilename)

    # ----------------------------------------------------------------------
    # Get basic image properties for reference file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hdr, name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, hdr, name='acqtime', kind='unix')
    bjdref = p['acqtime']
    # set sigdet and conad keywords (sigdet is changed later)
    p['kw_CCD_SIGDET'][1] = p['sigdet']
    p['kw_CCD_CONAD'][1] = p['gain']

    # ----------------------------------------------------------------------
    # start ll solution
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Instrumental drift computation
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # calculate wavelength solution
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # find ll on spectrum
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # detect bad fit filtering and saturated lines
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # fit llsol
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # extrapolate Littrow solution
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # repeat the line search loop
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # FP solution
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Littrow test
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Join 0-24 and 25-36 solutions
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # archive result in e2ds spectra
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Save to result table
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Save th_line tbl file
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Compute CCF
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Update the calibration data base
    # ----------------------------------------------------------------------

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
