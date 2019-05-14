#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 11:36

@author: cook
"""
import pkg_resources
import os

from terrapipe import constants
from terrapipe.config import drs_log
from terrapipe import locale


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io,drs_path.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def get_relative_folder(params, package, folder):
    """
    Get the absolute path of folder defined at relative path
    folder from package

    :param package: string, the python package name
    :param folder: string, the relative path of the config folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    func_name = __NAME__ + '.get_relative_folder()'
    # get the package.__init__ file path
    try:
        init = pkg_resources.resource_filename(package, '__init__.py')
    except ImportError:
        eargs = [package, func_name]
        WLOG(params, 'error', TextEntry('00-008-00001', args=eargs))
        init = None
    # Get the config_folder from relative path
    current = os.getcwd()
    # get directory name of folder
    dirname = os.path.dirname(init)
    # change to directory in init
    os.chdir(dirname)
    # get the absolute path of the folder
    data_folder = os.path.abspath(folder)
    # change back to working dir
    os.chdir(current)
    # test that folder exists
    if not os.path.exists(data_folder):
        eargs = [os.path.basename(data_folder), os.path.dirname(data_folder),
                 func_name]
        WLOG(params, 'error', TextEntry('00-008-00002', args=eargs))
    # return the absolute data_folder path
    return data_folder


def get_uncommon_path(path1, path2):
    # get common source
    common = os.path.commonpath([path2, path1]) + os.sep
    uncommon = path2.split(common)[-1]
    return uncommon






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
