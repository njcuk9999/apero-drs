#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_DARK_spirou.py [night_directory] [fitsfilename]

Prepares the dark files for SPIRou

Created on 2017-10-11 at 10:45

@author: cook

Version 0.0.1

Last modified: 2017-10-11 at 10:49
"""
import sys
import numpy as np

import startup
import general_functions as gf

# =============================================================================
# Define variables
# =============================================================================
WLOG = startup.log.logger
# -----------------------------------------------------------------------------


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    pp = startup.RunInitialStartup()
    # run specific start up
    pp = startup.RunStartup(pp, kind='dark', prefixes=['dark_dark'])

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, nx, ny = gf.ReadImage(pp, framemath='average')
    # get ccd sig det value
    pp['ccdsigdet'] = float(gf.GetKey(pp, hdr, 'RDNOISE', hdr['@@@hname']))
    # get exposure time
    pp['exptime'] = float(gf.GetKey(pp, hdr, 'EXPTIME', hdr['@@@hname']))
    # get gain
    pp['gain'] = float(gf.GetKey(pp, hdr, 'GAIN', hdr['@@@hname']))
    # log the Dark exposure time
    WLOG('info', pp['log_opt'], 'Dark Time = {0:.3f} [s]'.format(pp['exptime']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if pp['exptime'] < pp['QC_DARK_TIME']:
        WLOG('error', pp['log_opt'], 'Dark exposure time too short')
        sys.exit(1)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # convert NaN to zeros
    data[np.isfinite(data)] = 0.0
    # resize blue image
    bkwargs = dict(xlow=pp['IC_CCDX_BLUE_LOW'], xhigh=pp['IC_CCDX_BLUE_HIGH'],
                   ylow=pp['IC_CCDY_BLUE_LOW'], yhigh=pp['IC_CCDY_BLUE_HIGH'])
    datablue, nx2, ny2 = gf.ResizeImage(data, **bkwargs)
    # Make sure we have data in the blue image
    if nx2 == 0 or ny2 == 0:
        WLOG('error', pp['log_opt'], 'IC_CCD(X/Y)_BLUE_(LOW/HIGH) remove '
                                     'all pixels from image.')
        sys.exit(1)
    # resize red image
    rkwargs = dict(xlow=pp['IC_CCDX_RED_LOW'], xhigh=pp['IC_CCDX_RED_HIGH'],
                   ylow=pp['IC_CCDY_RED_LOW'], yhigh=pp['IC_CCDY_RED_HIGH'])
    datared, nx3, ny3 = gf.ResizeImage(data, **rkwargs)
    # Make sure we have data in the red image
    if nx3 == 0 or ny3 == 0:
        WLOG('error', pp['log_opt'], 'IC_CCD(X/Y)_RED_(LOW/HIGH) remove '
                                     'all pixels from image.')
        sys.exit(1)

    # ----------------------------------------------------------------------
    # Dark Measurement
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Identification of bad pixels
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Plots
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Save dark to calibDB
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # Save bad pixel mask
    # ----------------------------------------------------------------------
    # TODO: code

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', pp['log_opt'], ('Recipe {0} has been succesfully completed'
                                 '').format(pp['program']))

# =============================================================================
# End of code
# =============================================================================
