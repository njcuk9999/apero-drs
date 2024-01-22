#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-22 at 10:25

@author: cook
"""
import os
import platform
from typing import Any, Dict, List

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.ari.ari_core.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# -----------------------------------------------------------------------------
# Get ParamDict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define classes
# =============================================================================
class AriObject:
    pass


class AriRecipe:
    pass


# =============================================================================
# Define functions
# =============================================================================
def load_ari_params(params: ParamDict) -> Dict[str, Any]:
    """
    Load the ari parameters from the profile file

    :param params: ParamDict, the parameter dictionary of constants

    :return: ari_params: dict, the ari parameters
    """
    # get arguments from recipe call (via params['INPUTS'])
    profile_yaml = params['INPUTS']['profile']
    obs_dir = params['INPUTS']['obsdir']
    # ----------------------------------------------------------------------
    # load yaml file into raw_params
    if os.path.exists(profile_yaml):
        try:
            ari_params = base.load_yaml(profile_yaml)
        except Exception as e:
            emsg = 'Error loading profile file: {0}\n\t{1}'
            eargs = [profile_yaml, e]
            WLOG(params, 'error', emsg.format(*eargs))
            return dict()
    # otherwise log an error message
    else:
        emsg = 'Cannot find profile file: {0}'
        eargs = [profile_yaml]
        WLOG(params, 'error', emsg.format(*eargs))
        return dict()
    # ----------------------------------------------------------------------
    # deal with individual settings
    # ----------------------------------------------------------------------
    # the username
    if ari_params['settings']['username'] == 'None':
        ari_params['settings']['username'] = platform.node()
    # the observation directory
    if ari_params['settings']['obsdir'] == 'None':
        ari_params['settings']['obsdir'] = obs_dir
    # ----------------------------------------------------------------------
    # return the ari parameters
    return ari_params


def load_previous_objects(params: ParamDict) -> List[AriObject]:
    return []


def load_previous_recipes(params: ParamDict) -> List[AriRecipe]:
    return []


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
