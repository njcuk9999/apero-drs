#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-12-19 at 16:44

@author: cook
"""

from SpirouDRS.spirouStartup.spirouRecipe import *

from SpirouDRS.spirouStartup import spirouStartup2
from SpirouDRS.spirouStartup import spirouRecipe
from SpirouDRS.spirouStartup import recipes_spirou
import glob



# =============================================================================
# Define variables
# =============================================================================
PATH = '/scratch/Projects/spirou/data_dev/tmp/*/*/*'
RECIPES = recipes_spirou.recipes

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def trigger(__recipe__, __files__, __filters__=None, **kwargs):

    # set up process id
    pid = spirouStartup2.assign_pid()
    # Clean WLOG
    WLOG.clean_log(pid)
    # get a recipe to test
    recipe = spirouStartup2.find_recipe(__recipe__)
    # quietly load DRS parameters (for setup)
    recipe.get_drs_params(quiet=True, pid=pid)
    # generate runs
    runs = recipe.generate_runs_from_filelist(__files__, __filters__, **kwargs)
    # return the runs
    return runs


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------

    p = spirouStartup2.get_params()
    # get list of files to test
    files = glob.glob(PATH)

    # TODO: options adding in list --> shouldn't do this!

    # ----------------------------------------------------------------------
    # log
    WLOG(p, 'info', 'Test for cal_dark')
    # trigger
    dark_runs = trigger('cal_DARK_spirou.py', files, plot=1)
    # ----------------------------------------------------------------------
    # log
    WLOG(p, 'info', 'Test for cal_extract')
    # define filters
    filters = dict(DPRTYPE=['OBJ_DARK', 'OBJ_FP'])
    # trigger
    ext_runs = trigger('cal_extract_RAW_spirou.py', files, add2calib=False)




# =============================================================================
# End of code
# =============================================================================
