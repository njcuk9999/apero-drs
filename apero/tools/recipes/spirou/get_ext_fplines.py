#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-05

@author: cook
"""
from apero import core
from apero import lang
from apero.core import constants
from apero.science.calib import wave
from apero.science import extract
from apero.tools.module.testing import drs_dev


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'get_ext_fplines.py'
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
Help = lang.drs_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# get file definitions for this instrument
FMOD = drs_dev.FileDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
get_ext_fplines = drs_dev.TmpRecipe()
get_ext_fplines.name = __NAME__
get_ext_fplines.shortname = 'GETFPL'
get_ext_fplines.instrument = __INSTRUMENT__
get_ext_fplines.outputdir = 'reduced'
get_ext_fplines.inputdir = 'reduced'
get_ext_fplines.inputtype = 'reduced'
get_ext_fplines.extension = 'fits'
get_ext_fplines.description = 'Produces an FPLINES file for an e2ds/e2dsff file'
get_ext_fplines.kind = 'misc'
get_ext_fplines.set_arg(pos=0, **RMOD.mod.directory)
get_ext_fplines.set_arg(name='files', dtype='files', pos='1+',
                        files=[FMOD.files.out_ext_e2ds,
                               FMOD.files.out_ext_e2dsff],
                        helpstr=(Help['FILES_HELP'] +
                                 'Currently allowed types: E2DS, E2DSFF'))
# add recipe to recipe definition
RMOD.add(get_ext_fplines)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, files=None, **kwargs):
    """
    Main function for exposuremeter_spirou.py

    :param directory: str or None the directory
    :param files: str or None, the list of files
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, files=files, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                rmod=RMOD)
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
    # get infile
    infiles = params['INPUTS']['FILES'][1]
    # get number of files
    num_files = len(infiles)
    # loop around files
    for it in range(num_files):
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # get this iterations e2ds file
        e2dsfile = infiles[it]
        # ------------------------------------------------------------------
        # get header from file instance
        header = e2dsfile.header
        # get fiber
        fiber = e2dsfile.get_key('KW_FIBER', dtype=str)
        # --------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe, header, fiber=fiber)
        # --------------------------------------------------------------
        # create fplines file for required fibers
        # --------------------------------------------------------------
        rargs = [e2dsfile, wprops['WAVEMAP'], fiber]
        rfpl = extract.ref_fplines(params, recipe, *rargs)
        # write rfpl file
        if rfpl is not None:
            rargs = [rfpl, e2dsfile, e2dsfile, fiber, 'EXT_FPLIST']
            wave.write_fplines(params, recipe, *rargs)
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
