#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drs_dependencies

Lists the dependencies the DRS currently has

Created on 2017-11-27 at 13:08

@author: cook
"""
import os
import pkg_resources

from SpirouDRS import spirouCore
from SpirouDRS import spirouStartup
from SpirouDRS import spirouConfig

# =============================================================================
# Define variables
# =============================================================================
# define DRS path
DRSPATH = pkg_resources.resource_filename('SpirouDRS', '')
PATH = os.path.dirname(DRSPATH)
# Get Logging function
WLOG = spirouCore.wlog
# get print log
printl = spirouCore.PrintLog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()


# =============================================================================
# Define functions
# =============================================================================
def get_python_cached_files(path):
    pyfiles = []
    for path, dirs, files in os.walk(path):
        for filename in files:
            # set up abs path
            abspath = os.path.join(path, filename)
            # make sure they are python cached files
            if filename.endswith('.pyc'):
                pyfiles.append(abspath)
    return pyfiles


def main(return_locals=False):
    # ----------------------------------------------------------------------
    # title
    spirouStartup.DisplayTitle(' * DRS Dependencies')
    # list the version of python found
    spirouStartup.DisplaySysInfo(logonly=False)
    # get all python files
    WLOG('', DPROG, 'Getting python cached files')
    python_files = get_python_cached_files(PATH)
    # get all import statements
    if len(python_files) == 0:
        WLOG('warning', DPROG, 'No .pyc files found!')
    else:
        wmsg = 'Removing python cached files (from {0})'
        WLOG('warning', DPROG, wmsg.format(PATH))
        for python_file in python_files:
            basepath = os.path.relpath(python_file, PATH)
            WLOG('', DPROG, '\tRemoving {0}'.format(basepath))
            os.remove(python_file)

    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    wmsg = 'Recipe {0} has been successfully completed'
    WLOG('info', DPROG, wmsg.format(DPROG))
    # return a copy of locally defined variables in the memory
    if return_locals:
        return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main(return_locals=True)
    # exit message
    spirouStartup.Exit(ll)

# =============================================================================
# End of code
# =============================================================================
