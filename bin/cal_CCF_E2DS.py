#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_CCF_E2DS_spirou.py [night_directory] [E2DSfilename] [mask] [RV] [width] [step]

# CODE DESCRIPTION HERE

Created on 2017-12-18 at 15:43

@author: cook

Last modified: 2017-12-18 at 15:48

Up-to-date with cal_CCF_E2DS_spirou AT-4 V47
"""
from __future__ import division
import numpy as np
import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage
from SpirouDRS import spirouRV
from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'cal_CCF_E2DS_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# Get Logging function
WLOG = spirouCore.wlog
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define functions
# =============================================================================
def main(night_name=None, reffile=None, mask=None, rv=None, width=None,
         step=None):
    pass
if 1:
    night_name, reffile = '20170710', 'fp_fp02a203_e2ds_AB.fits'
    mask, rv, width, step = None, None, None, None
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # deal with arguments being None (i.e. get from sys.argv)
    pos = [0, 1, 2, 3, 4]
    fmt = [str, str, float, float, float]
    name = ['reffile', 'ccf_mask', 'target_rv', 'ccf_width', 'ccf_step']
    lname = ['input_file', 'CCF_mask', 'RV', 'CCF_width', 'CCF_step']
    req = [True, True, True, False, False]
    call = [reffile, mask, rv, width, step]
    call_priority = [True, True, True, True, True]
    # now get custom arguments
    customargs = spirouStartup.GetCustomFromRuntime(pos, fmt, name, req, call,
                                                    call_priority, lname)
    # get parameters from configuration files and run time arguments
    p = spirouStartup.RunInitialStartup(night_name, customargs=customargs)
    # define default arguments (if ccf_width and ccf_step are not defined
    # in function call or run time arguments
    if 'ccf_width' not in p:
        p['ccf_width'] = p['ic_ccf_width']
    if 'ccf_step' not in p:
        p['ccf_step'] = p['ic_ccf_step']
    # ----------------------------------------------------------------------
    # Construct reference filename and get fiber type
    # ----------------------------------------------------------------------
    # get reduced directory + night name
    rdir = p['reduced_dir']
    # construct and test the reffile
    reffilename = spirouStartup.GetFile(p, rdir, p['reffile'], 'fp_fp',
                                        'DRIFT')
    # get the fiber type
    p['fiber'] = spirouStartup.GetFiberType(p, reffilename)
    fsource = __NAME__ + '/main()() & spirouStartup.GetFiberType()'
    p.set_source('fiber', fsource)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    e2ds, hdr, cdr, nbo, nx = spirouImage.ReadData(p, reffilename)
    # add to loc
    loc = ParamDict()
    loc['e2ds'] = e2ds
    loc['number_orders'] = nbo
    loc.set_sources(['e2ds', 'number_orders'], __NAME__ + '/main()')

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
    # Read wavelength solution
    # ----------------------------------------------------------------------
    # get wave image
    loc['wave'] = spirouImage.ReadWaveFile(p, hdr)
    loc.set_source('wave', __NAME__ + '/main() + /spirouImage.ReadWaveFile')

    # ----------------------------------------------------------------------
    # Read Flat file
    # ----------------------------------------------------------------------
    # get flat
    loc['flat'] = spirouImage.ReadFlatFile(p, hdr)
    loc.set_source('flat', __NAME__ + '/main() + /spirouImage.ReadFlatFile')
    # get all values in flat that are zero to 1
    loc['flat'] = np.where(loc['flat'] == 0, 1.0, loc['flat'])

    # ----------------------------------------------------------------------
    # Preliminary set up = no flat, no blaze
    # ----------------------------------------------------------------------
    # reset flat to all ones
    flat = np.ones((nbo, nx))
    # set blaze to all ones
    blaze = np.ones((nbo, nx))

    # ----------------------------------------------------------------------
    # correct extracted image for flat
    # ----------------------------------------------------------------------
    e2dsff = e2ds/flat

    # ----------------------------------------------------------------------
    # Compute photon noise uncertainty for reference file
    # ----------------------------------------------------------------------
    # set up the arguments for DeltaVrms2D
    dargs = [loc['e2ds'], loc['wave']]
    dkwargs = dict(sigdet=p['IC_DRIFT_NOISE'], size=p['IC_DRIFT_BOXSIZE'],
                   threshold=p['IC_DRIFT_MAXFLUX'])
    # run DeltaVrms2D
    dvrmsref, wmeanref = spirouRV.DeltaVrms2D(*dargs, **dkwargs)
    # save to loc
    loc['dvrmsref'], loc['wmeanref'] = dvrmsref, wmeanref
    loc.set_sources(['dvrmsref', 'wmeanref'], __NAME__ + '/main()()')
    # log the estimated RV uncertainty
    wmsg = 'On fiber {0} estimated RV uncertainty on spectrum is {1:.3f} m/s'
    WLOG('info', p['log_opt'], wmsg.format(p['fiber'], wmeanref))

    # ------------------------------------------------------------------
    # Reference plots
    # ------------------------------------------------------------------
    if p['DRS_PLOT']:
        # start interactive session if needed
        sPlt.start_interactive_session()
        # plot FP spectral order
        sPlt.drift_plot_selected_wave_ref(p, loc, y=loc['e2ds'])
        # plot photon noise uncertainty
        sPlt.drift_plot_photon_uncertainty(p, loc)

    # ------------------------------------------------------------------
    # Do correlation
    # ------------------------------------------------------------------
    # log that we are getting the template used for CCF computation
    wmsg = 'Template used for CCF computation: {0}'
    WLOG('info', p['log_opt'], wmsg.format(p['ccf_mask']))
    # get the CCF mask from file
    loc = spirouRV.GetCCFMask(p, loc)


    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been succesfully completed'
    WLOG('info', p['log_opt'], wmsg.format(p['program']))

    # return locals()

# =============================================================================
# Start of code
# =============================================================================


if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    locals = main()
# =============================================================================
# End of code
# =============================================================================
