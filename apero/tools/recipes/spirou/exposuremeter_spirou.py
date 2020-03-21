#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-28 at 16:47

@author: cook
"""
from __future__ import division

from apero import core
from apero import locale
from apero.core import constants
from apero.io import drs_fits
from apero.core.core import drs_database
from apero.science.calib import general
from apero.tools.module.testing import drs_dev

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_update_berv.py'
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
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
Help = locale.drs_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
exposuremeter = drs_dev.TmpRecipe()
exposuremeter.name = __NAME__
exposuremeter.shortname = 'EXPMTR'
exposuremeter.instrument = __INSTRUMENT__
exposuremeter.outputdir = 'reduced'
exposuremeter.inputdir = 'tmp'
exposuremeter.inputtype = 'tmp'
exposuremeter.extension = 'fits'
exposuremeter.description = 'Produces an exposuremeter map'
exposuremeter.kind = 'misc'
exposuremeter.set_arg(pos=0, name='directory', dtype='directory',
                      helpstr=Help['DIRECTORY_HELP'])
exposuremeter.set_kwarg(name='--intype', dtype=str, default='FLAT_FLAT',
                        helpstr=('[STR] Input pp file type (e.g. FLAT_FLAT or '
                                 'DARK_DARK_TEL)'))
# add recipe to recipe definition
RMOD.add(exposuremeter)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, **kwargs):
    """
    Main function for exposuremeter_spirou.py

    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, **kwargs)
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
    mainname = __NAME__ + '._main()'
    # extract file type from inputs
    filetype = params['INPUTS']['INTYPE'].upper().strip()
    # find file instance in set (verify user input)
    drsfile = core.get_file_definition(filetype, params['INSTRUMENT'],
                                       kind='tmp')
    # get all "filetype" filenames
    files = drs_fits.find_files(params, recipe, kind='tmp', KW_DPRTYPE=filetype,
                                night=params['NIGHTNAME'])
    # make a new copy of infile
    infile = drsfile.newcopy(filename=files[-1], recipe=recipe)
    # read file
    infile.read_file()
    # get calibrations for this data
    drs_database.copy_calibrations(params, infile.header)

    # ------------------------------------------------------------------
    # Correction of file
    # ------------------------------------------------------------------
    # TODO: Do I need this -- work back from outputs
    props, image = general.calibrate_ppfile(params, recipe, infile)

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