#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
demo_spirou.py

A demo spirou recipe used for demonstrating how to use a top level recipe

Created on 2019-07-05 at 16:46

@author: cook
"""
import sys
from typing import Any, Dict, Tuple, Union

import numpy as np

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
import apero as apero_pkg
from aperocore import drs_lang
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.tools.module.testing import drs_dev
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'demo_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get the text types
textentry = drs_lang.textentry
# -----------------------------------------------------------------------------
# Note: move recipe definition to instrument set up when testing is finished
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
demo_recipe = drs_dev.TmpRecipe()
demo_recipe.name = __NAME__
demo_recipe.shortname = 'DEVTEST'
demo_recipe.instrument = __INSTRUMENT__
demo_recipe.in_block_str = 'red'
demo_recipe.out_block_str = 'red'
demo_recipe.extension = 'fits'
demo_recipe.description = 'This is a demo of some APERO features'
demo_recipe.kind = 'misc'
demo_recipe.set_arg(name='mode', dtype=int, options=[1],
                    helpstr='Enter a mode (demo purposes)')
demo_recipe.set_kwarg(name='--text', dtype=str, default='None',
                      helpstr='Enter text here to print it')
# add recipe to recipe definition
RMOD.add(demo_recipe)
# demo functions (Note: remove anywhere that is not a demo)
demo = drs_dev.Demo(load_functions.load_config(select.INSTRUMENTS))


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for demo_spirou.py

    :param kwargs: additional keyword arguments

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    # -------------------------------------------------------------------------
    # Note: remove rmod when put into full recipe
    # -------------------------------------------------------------------------
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


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # access mode
    mode = params['INPUTS']['MODE']

    # ----------------------------------------------------------------------
    # Demo 1: Accessing inputs
    # ----------------------------------------------------------------------
    if mode == 1:
        WLOG(params, '', params['LOG.HEADER'])
        # log: DEMO 1: ACCESSING INPUTS
        WLOG(params, '', textentry('40-522-00001'))
        WLOG(params, '', params['LOG.HEADER'])
        # This is how we get parameters directly from user inputs
        # See blank.set_arg and blank.set_kwarg above for user input definitions
        # log: Current inputs:
        print(textentry('40-522-00002'))
        for _input in params['INPUTS']:
            print('\t{0} = {1}'.format(_input, params['INPUTS'][_input]))
        # print gap
        print('\n\n\n')

    # ----------------------------------------------------------------------
    # Demo 2: Writing to the logger (WLOG)
    # ----------------------------------------------------------------------
    if mode == 2:
        WLOG(params, '', params['LOG.HEADER'])
        # log: DEMO 2: WLOG
        WLOG(params, '', textentry('40-522-00003'))
        WLOG(params, '', params['LOG.HEADER'])
        # By default this writes to the screen and log files
        # log: Message types:
        WLOG(params, '', textentry('40-522-00004'))
        # log: '':General message
        WLOG(params, '', textentry('40-522-00005'))
        # log: 'info':Info message
        WLOG(params, 'info', textentry('40-522-00006'))
        # warning: 'warning':Warning message
        WLOG(params, 'warning', textentry('10-522-00001'), sublevel=1)
        # Note that error messages will end the code
        #    (uncomment below to use)
        # Here we have used raise_exception=False not to end code
        # error: 'error':Error message
        WLOG(params, 'error', textentry('09-522-00001'), raise_exception=False)
        # print gap
        print('\n\n\n')

    # ----------------------------------------------------------------------
    # Demo 3: Writing Text Entries with the language database
    # ----------------------------------------------------------------------
    if mode == 3:
        WLOG(params, '', params['LOG.HEADER'])
        # log: DEMO 3: Text Entry
        WLOG(params, '', textentry('40-522-00007'))
        WLOG(params, '', params['LOG.HEADER'])

        # We also have an extensive language database - these messages
        #  use codes that will print in the language of the users choice
        #  (if defined in the language database)
        margs = [demo.get_lang_db_loc()]
        # log: Location of language database: \n {0}
        WLOG(params, 'info', textentry('40-522-00028', args=margs))
        # log: Database file: language.xls
        WLOG(params, '', textentry('40-522-00008'))

        # Any changes to the language database must be updated with a run of the
        # following:
        wargs = ['tools/dev/apero_langdb.py --update']
        # warning: Change to the database must be updated with command: \n {0}
        WLOG(params, 'warning', textentry('10-522-00005', args=wargs),
             sublevel=2)

        # examples of these codes are as follows:
        wargs = ['SPIROU']
        # log: Text Entry examples:
        WLOG(params, 'info', textentry('40-522-00009'))
        # log: Listing for: {0}
        WLOG(params, '', textentry('40-005-00001', args=wargs))
        # same as running the following:
        # log: Listing for: {0}
        WLOG(params, '', textentry('40-005-00001', args=wargs))

        # but if the user specified french:
        demo.change_lang(params, 'FR')  # only for demo purposes DO NOT USE
        # log: This is a test message
        WLOG(params, '', textentry('00-000-99999'))
        demo.change_lang(params, 'ENG')  # only for demo purposes DO NOT USE
        # log: This is a test message
        WLOG(params, '', textentry('00-000-99999'))

        # print gap
        print('\n\n\n')

    # ----------------------------------------------------------------------
    # Demo 4: The parameter dictionary
    # ----------------------------------------------------------------------
    # The parameter dictionary is a more powerful dictionary:
    #   - it is case insensitive
    #   - it stores where parameter was defined (if set) and recalls history
    #   - can display additional information
    #   - many extra functions to aid use
    if mode == 4:
        # set up a new one
        newparams = ParamDict()

        # add parameters
        newparams['CONST0'] = 'demo'
        newparams['CONST1'] = 0
        # set the source
        newparams.set_source('CONST0', 'demo_spirou.py.first()')
        newparams.set_source('CONST1', 'demo_spirou.py.first()')

        # add some more parameters
        newparams['CONST1'] = 1
        newparams['CONST2'] = True
        newparams['VAR1'] = np.arange(100)
        newparams['VAR2'] = float
        newparams['VAR3'] = dict(x=1, y=2, z=3)
        newparams['LIST1'] = '1, 2, 3, 4'
        newparams['DICT1'] = '{"x":"1", "y":"2", "z":"3"}'
        # add the same source
        keys = ['CONST1', 'CONST2', 'VAR1', 'VAR2', 'VAR3', 'LIST1', 'DICT1']
        newparams.set_sources(keys, 'demo_spirou.py.more()')

        # printing gives a summary of variables
        # log: ParamDict: print newparams:
        WLOG(params, '', textentry('40-522-00010'))
        print(newparams)

        # ------------------------------------------------------------------
        # there are also some very helpful functionality
        # ------------------------------------------------------------------
        # the info method
        # log: ParamDict: info of newparams['CONST1']
        WLOG(params, '', textentry('40-522-00011'))
        newparams.info('CONST1')

        # the history method
        # log: ParamDict: history of newparams['CONST1']
        WLOG(params, '', textentry('40-522-00012'))
        newparams.history('CONST1')
        # which is very useful in params where we read constants from multiple
        #   different places
        # log: params PATH.RAW history:
        WLOG(params, '', textentry('40-522-00013'))
        params.history('PATH.RAW')

        # the contains function
        # log: ParamDict: newparams contains "VAR"
        WLOG(params, '', textentry('40-522-00014'))
        margs = [newparams.contains('VAR')]
        # log: VAR keys = {0}
        print(textentry('40-522-00015', args=margs))
        # which is very useful for params
        margs = [params.contains('DRS_DATA')]
        # log: params DRS_DATA keys = {0}
        print(textentry('40-522-00016', args=margs))


    # ----------------------------------------------------------------------
    # Demo 5: Calibrations
    # ----------------------------------------------------------------------
    if mode == 5:
        # for this you need a file
        pass

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
# This is the classic start up:
# Note: Uncomment if not a demo

# if __name__ == "__main__":
#         # run main with no arguments (get from command line - sys.argv)
#         ll = main()

# This is just for demo purposes
if __name__ == "__main__":
    # setup demo
    args = demo.setup()

    # if we have arguments use classical startup
    if len(args) > 1:
        # note this is the classical content of __main__
        ll = main()
    # else just print some stuff
    else:
        # need to set up sys.argv if we want to use this
        sys.argv = ['demo', '1']
        # note to access recipe and params from __main__ do the following
        _recipe, _params = main(DEBUG0000=True)
        # simple print statement
        margs = [_params['DRS.PACKAGE']]
        # log: Welcome to {0}
        WLOG(_params, '', textentry('40-522-00017', args=margs))

# =============================================================================
# End of code
# =============================================================================
