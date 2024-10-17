#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-01-07 at 14:59

@author: cook
"""

from aperocore.base import base
from aperocore.core import drs_text
from aperocore.constants import load_functions
from aperocore.core import drs_log

from apero.base import base as apero_base
from apero.utils import drs_startup
from apero.tools.module.documentation import drs_documentation
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_documentation.py'
__INSTRUMENT__ = 'None'
# Get constants
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_documentation.py

    :param kwargs: any additional keywords

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


def __main__(recipe, params):

    # get instruments parameter
    instruments = params['INPUTS']['INSTRUMENTS']
    # deal with instruments options
    if drs_text.null_text(instruments, ['None', 'Null', '']):
        instruments = [params['INSTRUMENT']]
    elif instruments.upper() == 'ALL':
        instruments = apero_base.INSTRUMENTS[:-1]
    else:
        instruments = instruments.split(',')

    # add default to instruments
    instruments = ['default'] + instruments
    # -------------------------------------------------------------------------
    # get inputs
    run_all = params['INPUTS']['ALL']
    # deal with individual re-generation (or all regenerated)
    if run_all:
        run_filedef = True
        run_recipedef = True
        run_recipeseq = True
    else:
        run_filedef = params['INPUTS']['FILEDEF']
        run_recipedef = params['INPUTS']['RECIPEDEF']
        run_recipeseq = params['INPUTS']['RECIPESEQ']
    # -------------------------------------------------------------------------
    # clean auto directories (if doing all three again)
    if run_filedef and run_recipedef and run_recipeseq:
        drs_documentation.clean_auto(instruments)
    # -------------------------------------------------------------------------
    # loop around instruments
    for instrument in instruments:
        # print progress if we are doing any of the three tasks
        if run_filedef or run_recipedef or run_recipeseq:
            WLOG(params, '', params['DRS_HEADER'], colour='magenta')
            WLOG(params, 'info', 'Processing {0}'.format(instrument),
                 colour='magenta')
            WLOG(params, '', params['DRS_HEADER'], colour='magenta')
        # re-load params for this instrument
        iparams = load_functions.load_config(select.INSTRUMENTS, 
                                             instrument=instrument)
        # constants.load sets default to None we want this back to default
        if instrument == 'default':
            iparams.set('INSTRUMENT', instrument)
        # make sure the recipe is set to the correct instrument
        recipe.params.set('INSTRUMENT', instrument)
        # re-get params and recipe
        recipe.reload(instrument)
        # ---------------------------------------------------------------------
        # deal with documenting file definitions
        if run_filedef:
            # get file definitions
            drs_documentation.compile_file_definitions(iparams, recipe)
        # ---------------------------------------------------------------------
        # deal with documenting file definitions
        if run_recipedef:
            # get file definitions
            drs_documentation.compile_recipe_definitions(iparams, recipe)
        # ---------------------------------------------------------------------
        # deal with documenting the recipe sequences
        if run_recipeseq:
            # get the recipe sequences
            drs_documentation.compile_recipe_sequences(iparams, recipe)
    # ---------------------------------------------------------------------
    # get mode
    mode = params['INPUTS']['MODE']
    # compile documentation
    if params['INPUTS']['COMPILE']:
        # print progress
        WLOG(params, '', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', 'Compiling mode={0}'.format(mode),
             colour='magenta')
        WLOG(params, '', params['DRS_HEADER'], colour='magenta')
        # compile
        drs_documentation.compile_docs(params, mode=mode)
    # upload to server
    if params['INPUTS']['UPLOAD']:
        # print progress
        WLOG(params, '', params['DRS_HEADER'], colour='magenta')
        WLOG(params, 'info', 'Compiling mode={0}'.format(mode),
             colour='magenta')
        WLOG(params, '', params['DRS_HEADER'], colour='magenta')
        # upload
        drs_documentation.upload(params)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
