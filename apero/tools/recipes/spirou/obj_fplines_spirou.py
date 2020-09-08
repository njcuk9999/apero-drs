#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-05-05

@author: cook
"""
from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_database2 as drs_database
from apero.science.calib import wave
from apero.science import extract
from apero.tools.module.testing import drs_dev


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_fplines_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get constants
Constants = constants.load(__INSTRUMENT__)
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
Help = lang.core.drs_lang_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])
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
get_ext_fplines.set_outputs(EXT_FPLINES=FMOD.files.out_ext_fplines)
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
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success)


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
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    # loop around files
    for it in range(num_files):
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
        # get this iterations e2ds file
        e2dsfile = infiles[it]
        # print file stats
        args = [e2dsfile.basename, e2dsfile.get_hkey('KW_DPRTYPE'),
                e2dsfile.get_hkey('KW_OBJNAME')]
        WLOG(params, '', '\t For file {0}'.format(*args))
        WLOG(params, '', '\t DPRTYPE = {1}'.format(*args))
        WLOG(params, '', '\t OBJECT = {2}'.format(*args))
        # ------------------------------------------------------------------
        # get header from file instance
        header = e2dsfile.get_header()
        # get fiber
        fiber = e2dsfile.get_hkey('KW_FIBER', dtype=str)
        # --------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe, header, fiber=fiber,
                                       database=calibdbm)
        # --------------------------------------------------------------
        # create fplines file for required fibers
        # --------------------------------------------------------------
        rargs = [e2dsfile, wprops['WAVEMAP'], fiber]
        rfpl = extract.ref_fplines(params, recipe, *rargs,
                                   database=calibdbm)
        # write rfpl file
        if rfpl is not None:
            rargs = [rfpl, e2dsfile, e2dsfile, fiber, 'EXT_FPLINES']
            wave.write_fplines(params, recipe, *rargs)
    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
