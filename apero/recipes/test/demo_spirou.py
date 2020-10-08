#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
import numpy as np
import sys

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.testing import drs_dev

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'demo_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# -----------------------------------------------------------------------------
# TODO: move recipe definition to instrument set up when testing is finished
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
demo_recipe = drs_dev.TmpRecipe()
demo_recipe.name = __NAME__
demo_recipe.shortname = 'DEVTEST'
demo_recipe.instrument = __INSTRUMENT__
demo_recipe.outputdir = 'red'
demo_recipe.inputdir = 'red'
demo_recipe.inputtype = 'red'
demo_recipe.extension = 'fits'
demo_recipe.description = 'This is a demo of some APERO features'
demo_recipe.kind = 'misc'
demo_recipe.set_arg(name='mode', dtype=int, options=[1],
                    helpstr='Enter a mode (demo purposes)')
demo_recipe.set_kwarg(name='--text', dtype=str, default='None',
                      helpstr='Enter text here to print it')
# add recipe to recipe definition
RMOD.add(demo_recipe)
# demo functions (TODO: remove anywhere that is not a demo)
demo = drs_dev.Demo(constants.load(__INSTRUMENT__))


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for cal_update_berv.py

    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    # TODO: remove rmod when put into full recipe
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
    # access mode
    mode = params['INPUTS']['MODE']

    # ----------------------------------------------------------------------
    # Demo 1: Accessing inputs
    # ----------------------------------------------------------------------
    if mode == 1:
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', 'DEMO 1: ACCESSING INPUTS')
        WLOG(params, '', params['DRS_HEADER'])
        # This is how we get parameters directly from user inputs
        # See blank.set_arg and blank.set_kwarg above for user input definitions
        print('Current inputs:')
        for _input in params['INPUTS']:
            print('\t{0} = {1}'.format(_input, params['INPUTS'][_input]))
        # print gap
        print('\n\n\n')

    # ----------------------------------------------------------------------
    # Demo 2: Writing to the logger (WLOG)
    # ----------------------------------------------------------------------
    if mode == 2:
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', 'DEMO 2: WLOG')
        WLOG(params, '', params['DRS_HEADER'])
        # By default this writes to the screen and log files
        WLOG(params, '', 'Message types:')
        WLOG(params, '', '\'\':\tGeneral message')
        WLOG(params, 'info', '\'info\':\tInfo message')
        WLOG(params, 'warning', '\'warning\':\tWarning message')
        # Note that error messages will end the code
        #    (uncomment below to use)
        # WLOG(params, 'error', '\'error\':\tError message')
        # Here we have used raise_exception=False not to end code
        WLOG(params, 'error', '\'error\':\tError message',
             raise_exception=False)
        # print gap
        print('\n\n\n')

    # ----------------------------------------------------------------------
    # Demo 3: Writing Text Entries with the language database
    # ----------------------------------------------------------------------
    if mode == 3:
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', 'DEMO 3: Text Entry')
        WLOG(params, '', params['DRS_HEADER'])

        # We also have an extensive language database - these messages
        #  use codes that will print in the language of the users choice
        #  (if defined in the language database)
        wmsg = 'Location of language database: \n\t{0}'
        WLOG(params, 'info', wmsg.format(demo.get_lang_db_loc()))
        WLOG(params, '', '\t Database file: language.xls')

        # Any changes to the language database must be updated with a run of the
        # following:
        wmsg = 'Change to the database must be updated with command: \n\t{0}'
        wargs = ['tools/dev/apero_langdb.py --update']
        WLOG(params, 'warning', wmsg.format(*wargs))

        # examples of these codes are as follows:
        wargs = ['SPIROU']
        WLOG(params, 'info', 'Text Entry examples:')
        WLOG(params, '', TextEntry('40-005-00001', args=wargs))
        # same as running the following:
        wmsg = 'Listing for: {0}'
        WLOG(params, '', wmsg.format(*wargs))

        # but if the user specified french:
        demo.change_lang(params, 'FR')  # only for demo purposes DO NOT USE
        WLOG(params, '', TextEntry('00-000-99999'))
        demo.change_lang(params, 'ENG')  # only for demo purposes DO NOT USE
        WLOG(params, '', TextEntry('00-000-99999'))

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
        WLOG(params, '', 'ParamDict: print newparams:')
        print(newparams)

        # ------------------------------------------------------------------
        # there are also some very helpful functionality
        # ------------------------------------------------------------------
        # the info method
        WLOG(params, '', 'ParamDict: info of newparams[\'CONST1\']')
        newparams.info('CONST1')

        # the history method
        WLOG(params, '', 'ParamDict: history of newparams[\'CONST1\']')
        newparams.history('CONST1')
        # which is very useful in params where we read constants from multiple
        #   different places
        WLOG(params, '', 'params DRS_DATA_RAW history:')
        params.history('DRS_DATA_RAW')

        # the contains function
        WLOG(params, '', 'ParamDict: newparams contains "VAR"')
        print('VAR keys = ', newparams.contains('VAR'))
        # which is very useful for params
        print('params DRS_DATA keys = ', params.contains('DRS_DATA'))

        # the string list method - get a list from a string
        WLOG(params, '', 'ParamDict: listp method')
        print('list1 = ', newparams.listp('LIST1', dtype=int))

        # the string dict method - get a dictionary from a string
        WLOG(params, '', 'ParamDict: dictp method')
        print('dict1 = ', newparams.dictp('DICT1', dtype=float))

    # ----------------------------------------------------------------------
    # Demo 5: Calibrations
    # ----------------------------------------------------------------------
    if mode == 5:
        # for this you need a file
        pass

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
# This is the classic start up:
# TODO: Uncomment if not a demo

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
        WLOG(_params, '', 'Welcome to {0}'.format(_params['DRS_PACKAGE']))

# =============================================================================
# End of code
# =============================================================================
