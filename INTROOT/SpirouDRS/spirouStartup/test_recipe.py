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
__NAME__ = 'test.py'
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def main(directory=None, filelist=None, **kwargs):

    # TODO: New setup, including:
    # TODO:    - loading config/constants
    # TODO:    - setting paths based on config/constants
    # TODO:    - making DIRS based on inputs
    # TODO:    - showing header/paths/sys info
    # TODO:    - checking files based on inputs (all in **kwargs)

    # assign function calls
    fkwargs = dict(directory=directory, filelist=filelist, **kwargs)
    # deal with command line inputs / function call inputs
    kwargs = spirouStartup.spirouStartup2.input_setup(__NAME__, fkwargs)


    for kwarg in kwargs['INPUT']:
        print('{0} = {1}'.format(kwarg, kwargs['INPUT'][kwarg]))

    # return a copy of locally defined variables in the memory
    return dict(locals())

# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    spirouStartup.Exit(ll, has_plots=False)

# =============================================================================
# End of code
# =============================================================================
