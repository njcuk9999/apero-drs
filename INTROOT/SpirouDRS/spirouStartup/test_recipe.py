#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 13:57

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings

from SpirouDRS import spirouStartup

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_DARK_spirou.py'
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):


    for kwarg in kwargs:
        print('{0} = {1}'.format(kwarg, kwargs[kwarg]))

    # return a copy of locally defined variables in the memory
    return dict(locals())

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # deal with command line inputs
    kwargs = spirouStartup.spirouStartup2.input_setup(__NAME__)
    # run main with no arguments (get from command line - sys.argv)
    ll = main(**kwargs)
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================
