#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2020-05-13

@author: cook
"""
from apero import core
from apero import lang
from apero.core import constants
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science import extract
from apero.science import polar


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pol_spirou_new.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, exp1=None, exp2=None, exp3=None, exp4=None, **kwargs):
    """
    Main function for pol_spirou.py

    :param directory: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, exp1=exp1, exp2=exp2, exp3=exp3,
                   exp4=exp4, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return core.end_main(params, llmain, recipe, success)


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get files
    infiles = []
    infiles += params['INPUTS']['EXP1'][1]
    infiles += params['INPUTS']['EXP2'][1]
    infiles += params['INPUTS']['EXP3'][1]
    infiles += params['INPUTS']['EXP4'][1]
    # get list of filenames (for output)
    rawfiles = []
    for infile in infiles:
        rawfiles.append(infile.basename)

    # TODO: ------------------------------------------------------------------
    # TODO: Add these to constants file
    params.set('POLAR_BERV_CORRECT', value=True, source=mainname)
    params.set('POLAR_TELLU_CORRECT', value=True, source=mainname)
    params.set('POLAR_SOURCERV_CORRECT', value=True, source=mainname)

    params.set('POLAR_CCF_FILE', value='CCF_RV', source=mainname)
    params.set('POLAR_CCF_FIBER', value='AB', source=mainname)
    params.set('POLAR_CCF_MASK', value='masque_sept18_andres_trans50.mas',
               source=mainname)

    params.set('POLAR_TCORR_FILE', value='TELLU_OBJ', source=mainname)
    params.set('POLAR_RECON_FILE', value='TELLU_RECON', source=mainname)
    params.set('POLAR_TELLU_FIBER', value='AB', source=mainname)


    # TODO: ------------------------------------------------------------------

    # set the location (must do before any plotting starts)
    recipe.plot.set_location()
    # ----------------------------------------------------------------------
    # Validate polar files
    # ----------------------------------------------------------------------
    pobjects, props = polar.validate_polar_files(params, infiles)
    # get first file

    # TODO: This is unfinished

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, locals())



# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
