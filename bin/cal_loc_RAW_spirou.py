#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal_loc_RAW_spirou.py

# CODE DESCRIPTION HERE

Created on 2017-10-12 at 15:21

@author: cook



Version 0.0.1
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
import sys
import warnings

import startup
import general_functions as gf

# =============================================================================
# Define variables
# =============================================================================
WLOG = startup.log.logger
# -----------------------------------------------------------------------------
INTERACTIVE_PLOTS = True
# These must exist in a config file
FIBER_PARAMS = 'nbfib', 'ic_first_order_jump', 'ic_locnbmaxo', 'qc_loc_nbo'

# =============================================================================
# Define functions
# =============================================================================
def fiber_params(p, fiber):
    """
    Takes the parameters defined in FIBER_PARAMS from parameter dictionary
    (i.e. from config files) and adds the correct parameter to a fiber
    parameter dictionary

    :param p: dictionary, parameter dictionary
    :param fiber: string, the fiber type (and suffix used in confiruation file)
                  i.e. for fiber AB fiber="AB" and nbfib_AB should be present
                  in config if "nbfib" is in FIBER_PARAMS
    :return fparam: dictionary, the fiber parameter dictionary
    """
    # set up the fiber parameter directory
    fparam = dict()
    # loop around keys in FIBER_PARAMS
    for key in FIBER_PARAMS:
        # construct the parameter key (must ex
        configkey = '{0}_{1}'.format(key, fiber).upper()
        if configkey not in p:
            WLOG('error', p['log_opt'], ('Config Error: Key {0} does not exist '
                                         'in parameter dictionary'
                                         '').format(configkey))
            sys.exit(1)
        fparam[key] = p[configkey]
    return fparam

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Set up
    # ----------------------------------------------------------------------
    # get parameters from configuration files and run time arguments
    p = startup.RunInitialStartup()
    # run specific start up
    params2add = dict()
    params2add['dark_flat'] = fiber_params(p, 'C')
    params2add['flat_dark'] = fiber_params(p, 'AB')
    p = startup.RunStartup(p, kind='localisation',
                           prefixes=['dark_flat', 'flat_dark'],
                           add_to_p=params2add, calibdb=True)

    # ----------------------------------------------------------------------
    # Read image file
    # ----------------------------------------------------------------------
    # read the image data
    data, hdr, cdr, nx, ny = gf.ReadImage(p, framemath='add')
    # get ccd sig det value
    p['ccdsigdet'] = float(gf.GetKey(p, hdr, 'RDNOISE', hdr['@@@hname']))
    # get exposure time
    p['exptime'] = float(gf.GetKey(p, hdr, 'EXPTIME', hdr['@@@hname']))
    # get gain
    p['gain'] = float(gf.GetKey(p, hdr, 'GAIN', hdr['@@@hname']))
    # log the Dark exposure time
    WLOG('info', p['log_opt'], 'Dark Time = {0:.3f} [s]'.format(p['exptime']))
    # Quality control: make sure the exposure time is longer than qc_dark_time
    if p['exptime'] < p['QC_DARK_TIME']:
        WLOG('error', p['log_opt'], 'Dark exposure time too short')
        sys.exit(1)

    # ----------------------------------------------------------------------
    # Correction of DARK
    # ----------------------------------------------------------------------
    datac = gf.CorrectForDark(p, data, hdr)

    # ----------------------------------------------------------------------
    # Resize image
    # ----------------------------------------------------------------------
    # rotate the image and conver from ADU/s to e-
    data = datac[::-1, ::-1] * p['exptime'] * p['gain']
    # convert NaN to zeros
    nanmask = ~np.isfinite(data)
    data0 = np.where(nanmask, 0.0, data)
    # resize image
    bkwargs = dict(xlow=p['IC_CCDX_LOW'], xhigh=p['IC_CCDX_HIGH'],
                   ylow=p['IC_CCDY_LOW'], yhigh=p['IC_CCDY_HIGH'])
    data2, nx2, ny2 = gf.ResizeImage(data, **bkwargs)
    # log change in data size
    WLOG('', p['log_opt'], 'Image format changed to {0}x{1}'.format(nx2, ny2))

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    WLOG('info', p['log_opt'], ('Recipe {0} has been succesfully completed'
                                 '').format(p['program']))

# =============================================================================
# End of code
# =============================================================================
