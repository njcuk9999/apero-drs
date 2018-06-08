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
if __name__ == '__main__':
    night_name = '20170710'
    files = ['hcone_neil_test_e2ds_AB.fits']

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
    p['FIBER'] = spirouStartup.GetFiberType(p, p['FITSFILENAME'])
    p.set_source('FIBER', __NAME__ + '/main()')
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # set find line mode
    find_lines_mode = p['HC_FIND_LINES_MODE']

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read and combine all files
    p, data, hdr, cdr = spirouImage.ReadImageAndCombine(p, 'add')
    # add data and hdr to loc
    loc = ParamDict()
    loc['DATA'], loc['HDR'] = data, hdr
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
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p)

    # ----------------------------------------------------------------------
    # Flat correction
    # ----------------------------------------------------------------------
    # log
    WLOG('', p['LOG_OPT'], 'Applying flat correction')
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
        WLOG('info', p['LOG_OPT'] + p['FIBER'], wmsg.format(p['FIBER']))

        # ------------------------------------------------------------------
        # First guess at solution for each order
        # ------------------------------------------------------------------
        # FIXME: Cannot get same number of lines identified
        # Question: Tried with python gaussian fitting
        # Question: Tried with Fortran fitgaus.fitgaus
        loc = spirouTHORCA.FirstGuessSolution(p, loc, mode=find_lines_mode)

        # # TODO: Remove this (loads old DRS data)
        # import numpy as np
        # loc['ALL_LINES_1'] = np.load('/home/cook/spirou_config_H2RG/'
        #                              'spirou_old_th_lines.py.npy',
        #                              encoding='bytes')

        # ------------------------------------------------------------------
        # Detect bad fit filtering and saturated lines
        # ------------------------------------------------------------------
        # log message
        wmsg = 'On fiber {0} cleaning list of identified lines'
        WLOG('', p['LOG_OPT'], wmsg.format(fiber))
        # clean lines
        loc = spirouTHORCA.DetectBadLines(p, loc, iteration=1)

        # ------------------------------------------------------------------
        # Fit wavelength solution on identified lines
        # ------------------------------------------------------------------
        # log message
        wmsg = 'On fiber {0} fitting wavelength solution on identified lines:'
        WLOG('', p['LOG_OPT'] + fiber, wmsg.format(fiber))
        # fit lines
        fkwargs = dict(ll=loc['LL_INIT'], iteration=1)
        loc = spirouTHORCA.Fit1DSolution(p, loc, **fkwargs)

        # ------------------------------------------------------------------
        # calculate Littrow solution
        # ------------------------------------------------------------------
        ckwargs = dict(ll=loc['LL_OUT_1'], iteration=1, log=False)
        loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

        # ------------------------------------------------------------------
        # extrapolate Littrow solution
        # ------------------------------------------------------------------
        ekwargs = dict(ll=loc['LL_OUT_1'], iteration=1)
        loc = spirouTHORCA.ExtrapolateLittrowSolution(p, loc, **ekwargs)

        # ------------------------------------------------------------------
        # Plot littrow solution
        # ------------------------------------------------------------------
        if p['DRS_PLOT']:
            # start interactive plot
            sPlt.start_interactive_session()
            # plot littrow x pixels against fitted wavelength solution
            sPlt.wave_littrow_extrap_plot(loc, iteration=1)

        # ------------------------------------------------------------------
        # Second guess at solution for each order (using Littrow)
        # ------------------------------------------------------------------
        loc = spirouTHORCA.SecondGuessSolution(p, loc, mode=find_lines_mode)

        # ------------------------------------------------------------------
        # Detect bad fit filtering and saturated lines (using Littrow)
        # ------------------------------------------------------------------
        # log message
        wmsg = 'On fiber {0} cleaning list of identified lines (second pass)'
        WLOG('', p['LOG_OPT'], wmsg.format(fiber))
        # clean lines
        loc = spirouTHORCA.DetectBadLines(p, loc, iteration=2)

        # ------------------------------------------------------------------
        # Fit wavelength solution on identified lines (using Littrow)
        # ------------------------------------------------------------------
        # log message
        wmsg = ('On fiber {0} fitting wavelength solution on identified '
                'lines: (second pass)')
        WLOG('', p['LOG_OPT'] + fiber, wmsg.format(fiber))
        # fit lines
        ll = loc['LITTROW_EXTRAP_SOL_1'][:p['CAL_HC_N_ORD_FINAL_2']]
        loc = spirouTHORCA.Fit1DSolution(p, loc, ll,  iteration=2)

        # ------------------------------------------------------------------
        # Littrow test
        # ------------------------------------------------------------------
        ckwargs = dict(ll=loc['LL_OUT_2'], iteration=2, log=True)
        loc = spirouTHORCA.CalcLittrowSolution(p, loc, **ckwargs)

        # ------------------------------------------------------------------
        # Plot wave solution littrow check
        # ------------------------------------------------------------------
        if p['DRS_PLOT']:
            # plot littrow x pixels against fitted wavelength solution
            sPlt.wave_littrow_check_plot(p, loc, iteration=2)
            # end interactive session
            sPlt.end_interactive_session()

    # ----------------------------------------------------------------------
    # Join 0-24 and 25-36 solutions
    # ----------------------------------------------------------------------
    loc = spirouTHORCA.JoinOrders(p, loc)

    # ----------------------------------------------------------------------
    # archive result in e2ds spectra
    # ----------------------------------------------------------------------

    # log progress
    wargs = []
    wmsg = 'Write wavelength solution for Fiber {0} in {1}'
    WLOG('', p['LOG_OPT'], wmsg.format(*wargs))

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
    WLOG('info', p['LOG_OPT'], wmsg.format(p['PROGRAM']))
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

