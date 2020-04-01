#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-03-10 at 14:13

@author: cook
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from astropy import units as u
from tqdm import tqdm
import warnings


# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def include_exclude(inlist, includes=None, excludes=None, ilogic='AND',
                    elogic='AND'):
    """
    Filter a list by a list of include and exclude strings
    (can use AND or OR) in both includes and excludes

    includes: if ilogic=='AND'  all must be in list entry
              if ilogic=='OR'   one must be in list entry

    excludes: if elogic=='AND'   all must not be in list entry
              if elogic=='OR'    one must not be in list entry

    :param inlist: list, the input list of strings to check
    :param includes: list or string, the include string(s)
    :param excludes: list or string, the exclude string(s)
    :param ilogic: string, 'AND' or 'OR' logic to use when combining includes
    :param elogic: string, 'AND' or 'OR' logic to use when combining excludes

    :type inlist: list
    :type includes: Union[None, list, str]
    :type excludes: Union[None, list, str]
    :type ilogic: str
    :type elogic: str

    :return: the filtered list of strings
    :rtype: list
    """
    # ----------------------------------------------------------------------
    if includes is None and excludes is None:
        return list(inlist)
    # ----------------------------------------------------------------------
    mask = np.ones(len(inlist)).astype(bool)
    # ----------------------------------------------------------------------
    if includes is not None:
        if isinstance(includes, str):
            includes = [includes]
        elif not isinstance(includes, list):
            raise ValueError('includes list must be a list or string')
        # loop around values
        for row, value in enumerate(inlist):
            # start off assuming we need to keep value
            if ilogic == 'AND':
                keep = True
            else:
                keep = False
            # loop around include strings
            for include in includes:
                if ilogic == 'AND':
                    if include in value:
                        keep &= True
                    else:
                        keep &= False
                else:
                    if include in value:
                        keep |= True
                    else:
                        keep |= False
            # change mask
            mask[row] = keep
    # ----------------------------------------------------------------------
    if excludes is not None:
        if isinstance(excludes, str):
            excludes = [excludes]
        elif not isinstance(excludes, list):
            raise ValueError('excludes list must be a list or string')
        # loop around values
        for row, value in enumerate(inlist):
            # start off assuming we need to keep value
            if ilogic == 'AND':
                keep = True
            else:
                keep = False
            # loop around include strings
            for exclude in excludes:
                if elogic == 'AND':
                    if exclude not in value:
                        keep &= True
                    else:
                        keep &= False
                else:
                    if exclude not in value:
                        keep |= True
                    else:
                        keep |= False
            # update mask
            mask[row] &= keep
    # ----------------------------------------------------------------------
    # return outlist
    return list(np.array(inlist)[mask])


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
