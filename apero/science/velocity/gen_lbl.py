#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-21 at 12:28

@author: cook
"""

import os

import numpy as np

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.tools.recipes.bin import apero_get

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.rv.gen_lbl.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict
# Get the text types
textentry = lang.textentry


# =============================================================================
# Define functions
# =============================================================================
def run_apero_get(params: ParamDict):
    """
    Run the apero get on all profiles

    :param params: ParamDict, the parameter dictionary containing constants

    :returns: None, copies or symlinks files to params['LBL_PATH']
    """
    pconst = constants.pload()

    # TODO get from yaml file
    lbl_in_path = params['LBL_PATH']
    # APERO file definition out types
    lbl_outtypes = params['LBL_FILE_DEFS']
    # APERO DPRTYPE for lbl science files
    lbl_dprtypes = params['LBL_DPRTYPES']
    # APERO DPRTYPE for lbl template files
    lbl_template_outtypes = params['LBL_TEMPLATE_FILE_DEFS']
    # APERO DPRTYPE for lbl simultaneous FP files
    simfp_dprtypes = params['LBL_SIM_FP_DPRTYPES']
    # whether we are copying with symlinks
    lbl_symlinks = params['LBL_SYMLINKS']
    # whether we are in test mode
    testmode = params['INPUTS']['TEST']
    # do not use since
    since = None
    # get the fiber types
    lbl_scifibers, lbl_calfibers = pconst.FIBER_CCF()
    # get the output path
    outpath_objects = os.path.join(lbl_in_path, 'science')
    outpath_templates = os.path.join(lbl_in_path, 'templates')
    outpath_calib = os.path.join(lbl_in_path, 'calib')
    outpath_fp = os.path.join(lbl_in_path, 'science/FP')
    # ----------------------------------------------------------
    # check directories exist - try to make them if they don't
    # ----------------------------------------------------------
    directories = [outpath_templates, outpath_calib, outpath_objects]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
    # --------------------------------------------------------------
    # Copy to LBL directory
    # --------------------------------------------------------------
    # run apero get for objects for lbl
    apero_get.main(objnames='*', dprtypes=lbl_dprtypes,
                   outtypes=lbl_outtypes,
                   outpath=outpath_objects, fibers=lbl_scifibers,
                   symlinks=lbl_symlinks,
                   test=testmode, since=since)
    # run apero get for templates (no DPRTYPE as they could be different)
    apero_get.main(objnames='*', outtypes=lbl_template_outtypes,
                   outpath=outpath_templates, fibers=lbl_scifibers,
                   symlinks=False, nosubdir=True,
                   test=testmode, since=since)
    # run apero get for simultaneous FP
    apero_get.main(objnames='None', dprtypes=simfp_dprtypes,
                   outtypes='EXT_E2DS_FF', nosubdir=True,
                   outpath=outpath_fp, fibers=lbl_calfibers,
                   symlinks=lbl_symlinks,
                   test=testmode, since=since)
    # run apero get for extracted FP_FP
    apero_get.main(objnames='None', dprtypes='FP_FP',
                   outtypes='EXT_E2DS_FF',
                   outpath=outpath_fp, fibers=lbl_calfibers,
                   symlinks=lbl_symlinks, nosubdir=True,
                   test=testmode, since=since)
    # run apero get for calibs (wave + blaze) science fiber
    apero_get.main(objnames='None', outtypes='FF_BLAZE,WAVE_NIGHT',
                   outpath=outpath_calib, fibers=lbl_scifibers,
                   symlinks=lbl_symlinks, nosubdir=True,
                   test=testmode, since=since)
    # run apero get for calibs (wave + blaze) science fiber
    apero_get.main(objnames='None',
                   outtypes='FF_BLAZE,WAVE_NIGHT',
                   outpath=outpath_calib, fibers=lbl_calfibers,
                   symlinks=lbl_symlinks, nosubdir=True,
                   test=testmode, since=since)


def find_friend(params: ParamDict, objname: str) -> str:
    """
    Find the friend for this object (currently defined by closest teff to
    a list of friends teffs)

    :param params: ParamDict, parameter dictionary of constants
    :param objname: str, the object name to find a friend of

    :return: str, the friend name
    """
    # TODO: v0.8 change this to use the astrometric database
    #       with a FRIEND column
    # get dictionary of friends (key = objname, value = friend teff)
    friends = params.dictp('LBL_FRIENDS', dtype=float)
    friend_names = np.array(list(friends.keys()))
    friend_teffs = np.array(list(friends.values()))
    # get the teff of this object
    teff = find_teff(params, objname)
    # find the closest friend
    closest = np.abs(friend_teffs - teff).argmin()
    # return the friend name
    return friend_names[closest]


def find_teff(params: ParamDict, objname: str) -> float:
    """
    Get the Teff for this object from the astrometric database

    :param params: ParamDict, parameter dictionary of constants
    :param objname: str, the object name to find the teff of

    :return: float, the teff of this object in K
    """
    # get the astrometric database
    astromdbm = drs_database.AstrometricDatabase(params)
    # get the teff from the database
    teff = astromdbm.get_entries('TEFF',
                                 condition='OBJNAME="{0}"'.format(objname),
                                 nentries=1)
    # try to convert to a float (may be a null)
    try:
        teff = float(teff)
    except Exception as _:
        emsg = 'Not Teff found for {0}'.format(objname)
        WLOG(params, 'error', emsg)
    # return the teff
    return teff


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
