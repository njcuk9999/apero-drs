#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:37
@author: ncook
Version 0.0.1
"""
from apero.core import constants
from apero import core
from apero.core.core import drs_file
from apero.core.core import drs_recipe
from apero.locale import drs_text
from apero.io import drs_fits


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'preprocessing.identification.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsRecipe = drs_recipe.DrsRecipe
# Get the text types
TextEntry = drs_text.TextEntry


# =============================================================================
# Define functions
# =============================================================================
def drs_infile_id(params, recipe, given_drs_file):
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
    # ID DRS FILE
    found, kind = drs_fits.id_drs_file(params, recipe, given_drs_file,
                                       nentries=1, use_input_file=True)
    # return found and drs file that matches the correct type
    return found, kind


def drs_outfile_id(params, recipe, infile, drsfileset, prefix=None):
    """
    Given a generic drs file (i.e. "pp_file") -- must have a fileset --
    identifies which sub-file (from fileset) this file is (based on the name
    of this file and the files in fileset)

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe related to this file
    :param infile: DrsFitsFile, the input drs_file
    :param drsfileset: DrsFitsFile, the drs file (with file set) to look
                           for sub-types

    :type params: ParamDict
    :type recipe: DrsRecipe
    :type infile: DrsFitsFile
    :type drsfileset: DrsFitsFile

    :returns: Whether we found the output file from give_drs_file list and
              if True returns the DrsFitsFile
    :rtype: tuple[bool, DrsFitsFile]
    """
    func_name = __NAME__ + '.drs_outfile_id()'
    # check we have entries
    if len(drsfileset.fileset) == 0:
        eargs = [drsfileset.name, func_name]
        WLOG(params, 'error', TextEntry('00-010-00001', args=eargs))
    # get the associated files with this generic drs file
    fileset = list(drsfileset.fileset)
    strfileset = list(map(lambda x: str(x.name), fileset))
    # set found to False
    found = False
    kind, inname = None, 'not set'
    # loop around files
    for fileseti in fileset:
        # remove prefix if not None
        if prefix is not None:
            inname = infile.name.split(prefix)[-1]
        else:
            inname = infile.name
        # check this file is valid
        cond = inname == fileseti.name
        # if True we have found our file
        if cond:
            found = True
            kind = fileseti.completecopy(fileseti)
            break
    # deal with not being found
    if kind is None:
        eargs = [inname, '\n\t'.join(strfileset), func_name]
        WLOG(params, 'error', TextEntry('00-010-00006', args=eargs))

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