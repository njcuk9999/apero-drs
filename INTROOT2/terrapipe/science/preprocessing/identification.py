#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:37
@author: ncook
Version 0.0.1
"""
from __future__ import division
import traceback

from terrapipe import constants
from terrapipe import config
from terrapipe import locale

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'preprocessing.identification.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = config.wlog
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = config.core.drs_file.DrsFitsFile
DrsRecipe = config.core.drs_recipe.DrsRecipe
# Get the text types
TextEntry = locale.drs_text.TextEntry


# =============================================================================
# Define functions
# =============================================================================
def drs_infile_id(params, given_drs_file):
    """
    Given a generic drs file (i.e. "raw_file") -- must have a fileset --
    identifies which sub-file (from fileset) this file is (based on
    required keywords and extension)

    :param params: ParamDict, the parameter dictionary of constants
    :param given_drs_file: DrsFitsFile, the drs file (with file set) to look
                           for sub-types

    :type params: ParamDict
    :type given_drs_file: DrsFitsFile

    :returns: whether the DrsFitsFile was found and if it was a new instance
              matching the DrsFitsFile sub-type
    :rtype: tuple[bool, DrsFitsFile]
    """
    func_name = __NAME__ + '.drs_file_id()'
    # check we have entries
    if len(given_drs_file.fileset) == 0:
        eargs = [given_drs_file.name, func_name]
        WLOG(params, 'error', TextEntry('00-010-00001', args=eargs))
    # get the associated files with this generic drs file
    fileset = list(given_drs_file.fileset)
    # set found to False
    found = False
    kind = None
    # loop around files
    for drs_file in fileset:
        # copy info from given_drs_file into drs_file
        file_in = drs_file.copyother(given_drs_file,
                                     recipe=given_drs_file.recipe)
        # check this file is valid
        cond, _ = file_in.check_file()
        # if True we have found our file
        if cond:
            found = True
            kind = file_in
            break
    # return found and the drs_file instance
    return found, kind


def drs_outfile_id(params, recipe, given_drs_file):
    """
    Given a generic drs file (i.e. "pp_file") -- must have a fileset --
    identifies which sub-file (from fileset) this file is (based on the name
    of this file and the files in fileset)

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe related to this file
    :param given_drs_file: DrsFitsFile, the drs file (with file set) to look
                           for sub-types

    :type params: ParamDict
    :type recipe: DrsRecipe
    :type given_drs_file: DrsFitsFile

    :returns: Whether we found the output file from give_drs_file list and
              if True returns the DrsFitsFile
    :rtype: tuple[bool, DrsFitsFile]
    """
    func_name = __NAME__ + '.drs_outfile_id()'
    # check we have entries
    if len(given_drs_file.fileset) == 0:
        eargs = [given_drs_file.name, func_name]
        WLOG(params, 'error', TextEntry('00-010-00001', args=eargs))
    # get the associated files with this generic drs file
    fileset = list(given_drs_file.fileset)
    # set found to False
    found = False
    kind = given_drs_file
    # loop around files
    for drs_file in fileset:
        # check this file is valid
        cond = drs_file.name == drs_file.name
        # if True we have found our file
        if cond:
            found = True
            kind = drs_file
            break
    # set the recipe if found
    if found:
        kind.recipe = recipe
    # return found and the drs_file instance
    return found, kind






# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================