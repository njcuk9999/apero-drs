#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 13:57

@author: cook
"""
from __future__ import division
import numpy as np

from SpirouDRS import spirouStartup
from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_badpix_spirou.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def main(directory=None, filelist=None, **kwargs):
    # assign function calls
    fkwargs = dict(directory=directory, filelist=filelist, **kwargs)
    # deal with command line inputs / function call inputs
    p = spirouStartup.spirouStartup2.input_setup(__NAME__, fkwargs)
    # display everything that comes from "INPUT"
    print_input(p)
    # return a copy of locally defined variables in the memory
    return dict(locals())


def print_input(params):
    for param in params['INPUT']:
        value = params['INPUT'][param]
        pargs = dict(name=param, value=value, kind=type(value))

        is_list = type(value) in [list, np.ndarray]

        if is_list:
            print('{name} ({kind})'.format(**pargs))
            for it in range(len(value[0])):
                args = [it, value[0][it], value[1][it]]
                print('\t[{0}]: {1} {2}'.format(*args))
        else:
            print('{name} = {value}\t({kind})'.format(**pargs))


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
