#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cal_WAVE_E2DS_spirou.py [night_directory] [FPfitsfilename] [HCfiles]

Wavelength calibration incorporating the FP lines

Created on 2018-02-09 at 10:57

@author: cook
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouCDB
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouFLAT
from SpirouDRS import spirouImage
from SpirouDRS import spirouRV
from SpirouDRS import spirouStartup
from SpirouDRS import spirouTHORCA

import cal_HC_E2DS_spirou

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
def main(night_name=None, fpfile=None, hcfiles=None):
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from config files/run time args/load paths + calibdb
    p = spirouStartup.Begin()
    if hcfiles is None or fpfile is None:
        names, types = ['fpfile', 'hcfiles'], [str, str]
        customargs = spirouStartup.GetCustomFromRuntime([0, 1], types, names,
                                                        last_multi=True,
                                                        recipe=__NAME__)
    else:
        customargs = dict(hcfiles=hcfiles, fpfile=fpfile)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.LoadArguments(p, night_name, customargs=customargs,
                                    mainfitsdir='reduced',
                                    mainfitsfile='hcfiles')

    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    p, fpfitsfilename = spirouStartup.SingleFileSetup(p, recipe=__NAME__,
                                                      filename=p['FPFILE'])
    fiber1 = str(p['FIBER'])
    p, hcfilenames = spirouStartup.MultiFileSetup(p, recipe=__NAME__,
                                                  files=p['HCFILES'])
    fiber2 = str(p['FIBER'])
    # set the hcfilename to the first hcfilenames
    hcfitsfilename = hcfilenames[0]

    # ----------------------------------------------------------------------
    # Once we have checked the e2dsfile we can load calibDB
    # ----------------------------------------------------------------------
    # as we have custom arguments need to load the calibration database
    p = spirouStartup.LoadCalibDB(p)

    # ----------------------------------------------------------------------
    # Have to check that the fibers match
    # ----------------------------------------------------------------------
    if fiber1 == fiber2:
        p['FIBER'] = fiber1
        fsource = __NAME__ + '/main() & spirouStartup.GetFiberType()'
        p.set_source('FIBER', fsource)
    else:
        emsg = 'Fiber not matching for {0} and {1}, should be the same'
        eargs = [hcfitsfilename, fpfitsfilename]
        WLOG('error', p['LOG_OPT'], emsg.format(*eargs))
    # set the fiber type
    p['FIB_TYP'] = [p['FIBER']]
    p.set_source('FIB_TYP', __NAME__ + '/main()')

    # set find line mode
    find_lines_mode = p['HC_FIND_LINES_MODE']

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read and combine all HC files except the last (fpfitsfilename)
    rargs = [p, 'add', hcfitsfilename, hcfilenames[1:]]
    p, hcdata, hchdr, hccdr = spirouImage.ReadImageAndCombine(*rargs)
    # read last file (fpfitsfilename)
    fpdata, fphdr, fpcdr, _, _ = spirouImage.ReadImage(p, fpfitsfilename)

    # add data and hdr to loc
    loc = ParamDict()
    loc['HCDATA'], loc['HCHDR'], loc['HCCDR'] = hcdata, hchdr, hccdr
    loc['FPDATA'], loc['FPHDR'], loc['FPCDR'] = fpdata, fphdr, fpcdr
    # set the source
    sources = ['HCDATA', 'HCHDR', 'HCCDR']
    loc.set_sources(sources, 'spirouImage.ReadImageAndCombine()')
    sources = ['FPDATA', 'FPHDR', 'FPCDR']
    loc.set_sources(sources, 'spirouImage.ReadImage()')

    # ----------------------------------------------------------------------
    # Get basic image properties for reference file
    # ----------------------------------------------------------------------
    # get sig det value
    p = spirouImage.GetSigdet(p, hchdr, name='sigdet')
    # get exposure time
    p = spirouImage.GetExpTime(p, hchdr, name='exptime')
    # get gain
    p = spirouImage.GetGain(p, hchdr, name='gain')
    # get acquisition time
    p = spirouImage.GetAcqTime(p, hchdr, name='acqtime', kind='unix')
    bjdref = p['ACQTIME']
    # set sigdet and conad keywords (sigdet is changed later)
    p['KW_CCD_SIGDET'][1] = p['SIGDET']
    p['KW_CCD_CONAD'][1] = p['GAIN']
    # get lamp parameters
    p = spirouTHORCA.GetLampParams(p)

    # ----------------------------------------------------------------------
    # Obtain the flat
    # ----------------------------------------------------------------------
    # get the flat
    loc = spirouFLAT.GetFlat(p, loc, hchdr)

    # ----------------------------------------------------------------------
    # Read blaze
    # ----------------------------------------------------------------------
    # get tilts
    loc['BLAZE'] = spirouImage.ReadBlazeFile(p, hchdr)
    loc.set_source('BLAZE', __NAME__ + '/main() + /spirouImage.ReadBlazeFile')

    # correct the data with the flat
    # TODO: Should this be used?
    # log
    # WLOG('', p['LOG_OPT'], 'Applying flat correction')
    # loc['HCDATA'] = loc['HCDATA']/loc['FLAT']
    # loc['FPDATA'] = loc['FPDATA']/loc['FLAT']

    # ----------------------------------------------------------------------
    # Start plotting session
    # ----------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive plot
        sPlt.start_interactive_session()

    # ----------------------------------------------------------------------
    # loop around fiber type
    # ----------------------------------------------------------------------
    for fiber in p['FIB_TYP']:
        # set fiber type for inside loop
        p['FIBER'] = fiber

        # ------------------------------------------------------------------
        # Instrumental drift computation (if previous solution exists)
        # ------------------------------------------------------------------
        # get key
        keydb = 'HCREF_{0}'.format(p['FIBER'])
        # check for key in calibDB
        if keydb in p['CALIBDB'].keys():
            # log process
            wmsg = ('Doing Instrumental drift computation from previous '
                    'calibration')
            WLOG('', p['LOG_OPT'] + p['FIBER'], wmsg)
            # calculate instrument drift
            loc = spirouTHORCA.CalcInstrumentDrift(p, loc)

        # ------------------------------------------------------------------
        # Wave solution
        # ------------------------------------------------------------------
        # log message for loop
        wmsg = 'Processing Wavelength Calibration for Fiber {0}'
        WLOG('info', p['LOG_OPT'] + p['FIBER'], wmsg.format(p['FIBER']))

        # ------------------------------------------------------------------
        # Part 1 of cal_HC
        # ------------------------------------------------------------------
        p, loc = cal_HC_E2DS_spirou.part1(p, loc, mode=find_lines_mode)

        # ------------------------------------------------------------------
        # FP solution
        # ------------------------------------------------------------------
        # log message
        wmsg = 'Calcaulting FP wave solution'
        WLOG('', p['LOG_OPT'], wmsg)
        # calculate FP wave solution
        spirouTHORCA.FPWaveSolution(p, loc, mode=find_lines_mode)

        # ------------------------------------------------------------------
        # FP solution plots
        # ------------------------------------------------------------------
        if p['DRS_PLOT']:
            # Plot the FP extracted spectrum against wavelength solution
            sPlt.wave_plot_final_fp_order(p, loc, iteration=1)
            # Plot the measured FP cavity width offset against line number
            sPlt.wave_local_width_offset_plot(loc)
            # Plot the FP line wavelength residuals
            sPlt.wave_fp_wavelength_residuals(loc)

        # ------------------------------------------------------------------
        # Part 2 of cal_HC
        # ------------------------------------------------------------------
        # set params for part2
        p['QC_RMS_LITTROW_MAX'] = p['QC_WAVE_RMS_LITTROW_MAX']
        p['QC_DEV_LITTROW_MAX'] = p['QC_WAVE_DEV_LITTROW_MAX']
        # run part 2
        p, loc = cal_HC_E2DS_spirou.part2(p, loc)

    # ----------------------------------------------------------------------
    # End plotting session
    # ----------------------------------------------------------------------
    # end interactive session
    sPlt.end_interactive_session()

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
