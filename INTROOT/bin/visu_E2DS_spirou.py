#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
visu_E2DS_spirou.py [night_directory] [*e2ds.fits]

Recipe to display e2ds file

Created on 2017-12-06 at 14:50

@author: fb

Last modified: 2018-06-01


"""
from __future__ import division
import numpy as np

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'visu_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt
plt = sPlt.plt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, reffile=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin(recipe=__NAME__)
    customargs = spirouStartup.GetCustomFromRuntime(p, [0], [str], ['reffile'],
                                                    [True], [reffile])
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsfile='reffile',
                                    mainfitsdir='reduced')

    # load the calibDB
    p = spirouStartup.LoadCalibDB(p)

    # force plotting to 1
    p['DRS_PLOT'] = 1

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    p, fpfitsfilename = spirouStartup.SingleFileSetup(p, filename=p['REFFILE'])
    # get the fiber type
    fiber1 = str(p['FIBER'])

    e2ds, hdr, nx, ny = spirouImage.ReadImage(p)
    p, blaze = spirouImage.ReadBlazeFile(p)

    # set source of wave file
    wsource = __NAME__ + '/main() + /spirouImage.GetWaveSolution'
    # Force A and B to AB solution
    if p['FIBER'] in ['A', 'B']:
        wave_fiber = 'AB'
    else:
        wave_fiber = p['FIBER']
    # get wave image
    _, wave, _ = spirouImage.GetWaveSolution(p, hdr=hdr, return_wavemap=True,
                                             fiber=wave_fiber)

    # ----------------------------------------------------------------------
    # Get basic image properties
    # ----------------------------------------------------------------------

    plt.ion()
    plt.figure()

    for i in np.arange(nx):
        plt.plot(wave[i], e2ds[i])

    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Flux e-')
    plt.title('Extracted spectra')

    plt.figure()

    for i in np.arange(nx):
        plt.plot(wave[i], e2ds[i] / blaze[i])

    plt.xlabel('Wavelength [nm]')
    plt.ylabel('Relative Flux e-')
    plt.title('Blaze corrected Extracted spectra')

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    p = spirouStartup.End(p, outputs=None)
    # return a copy of locally defined variables in the memory
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=True)

# =============================================================================
# End of code
# =============================================================================
