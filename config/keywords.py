#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 16:37

@author: cook



Version 0.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings


# =============================================================================
# Define Global Variables
# =============================================================================

# -----------------------------------------------------------------------------
kw_version = ['VERSION', '{0}_{1}'.format(p['DRS_NAME'], p['DRS_VERSION'])


# =============================================================================
# Define localisation variables
# =============================================================================
kw_CCD_SIGDET

kw_CCD_CONAD

kw_LOCO_BCKGRD

kw_LOCO_NBO

kw_LOCO_DEG_C

kw_LOCO_DEG_W

kw_LOCO_DEG_E

kw_LOCO_DELTA

kw_LOCO_CTR_COEFF

kw_LOCO_FWHM_COEFF

# =============================================================================
# Define functions
# =============================================================================
def get_keywords():
    """

    :return:
    """
    # List all used values here
    keys = []

    # code to get values
    values = []
    for key in keys:
        values.append(eval(keys))
    return dict(zip(keys, values))

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    kwdict = get_keywords()

# =============================================================================
# End of code
# =============================================================================
