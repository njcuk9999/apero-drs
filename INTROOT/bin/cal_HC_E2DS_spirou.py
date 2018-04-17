#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_HC_E2DS_spirou.py [night_directory] [fitsfilename]

Wavelength calibration

Created on 2018-03-01 at 11:55

@author: cook
"""
from __future__ import division

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouFLAT
from SpirouDRS import spirouImage
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA

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
# cal_HC_E2DS_spirou.py 20170710 hcone_hcone02c61_e2ds_AB.fits hcone_hcone03c61_e2ds_AB.fits hcone_hcone04c61_e2ds_AB.fits hcone_hcone05c61_e2ds_AB.fits hcone_hcone06c61_e2ds_AB.fits

#def main(night_name=None, files=None):
if 1:
    night_name = '20170710'
    files = ['hcone_hcone02c61_e2ds_AB.fits', 'hcone_hcone03c61_e2ds_AB.fits',
             'hcone_hcone04c61_e2ds_AB.fits', 'hcone_hcone05c61_e2ds_AB.fits',
             'hcone_hcone06c61_e2ds_AB.fits']

    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, files, mainfitsdir='reduced')
    # setup files
    p = spirouStartup.InitialFileSetup(p, kind='cal_HC', prefixes='hc',
                                       calibdb=True)
    # get the fiber type
    p['fiber'] = spirouStartup.GetFiberType(p, p['fitsfilename'])
    p.set_source('fiber', __NAME__ + '/main()')
    # set the fiber type
    p['fib_typ'] = [p['fiber']]
    p.set_source('fib_typ', __NAME__ + '/main()')

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read and combine all files
    data, hdr, cdr, nx, ny = spirouImage.ReadImageAndCombine(p, 'add')
    # add data and hdr to loc
    loc = ParamDict()
    loc['data'], loc['hdr'] = data, hdr
    # set the source
    loc.set_sources(['data', 'hdr'], 'spirouImage.ReadImageAndCombine()')

    # ----------------------------------------------------------------------
    # Get basic parameters
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
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p)

    # ----------------------------------------------------------------------
    # Flat correction
    # ----------------------------------------------------------------------
    # log
    WLOG('', p['log_opt'], 'Applying flat correction')
    # get the flat
    loc = spirouFLAT.CorrectFlat(p, loc, hdr)

    # ----------------------------------------------------------------------
    # loop around fiber type
    # ----------------------------------------------------------------------
    for fiber in p['FIB_TYP']:
        # set fiber type for inside loop
        p['FIBER'] = fiber

        # log message for loop
        wmsg = 'Processing Wavelength Calibration for Fiber {0}'
        WLOG('info', p['log_opt'] + p['FIBER'], wmsg.format(p['FIBER']))

        # ------------------------------------------------------------------
        # First guess at solution for each order
        # ------------------------------------------------------------------
        loc = spirouTHORCA.FirstGuessSolution(p, loc)


    # ----------------------------------------------------------------------
    # start ll solution
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

def main():
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

