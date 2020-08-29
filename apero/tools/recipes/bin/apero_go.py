#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-02-27 at 10:56

@author: cook
"""
import os
import sys

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.utils import drs_startup


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_go.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(instrument=None, **kwargs):
    """
    Main function for apero_listing.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # get args from sys.argv
    args = sys.argv
    # make sure we have an instrument argument
    if len(args) < 2:
        print('Error: Must define an instrument')
    # deal with instrument from call
    if instrument is None:
        instrument = args[1]
    # get parameters for this instrument
    import time
    start = time.time()
    params = constants.load(instrument)
    end = time.time()
    # add inputs
    params['INPUTS'] = dict()
    for it, arg in enumerate(args[1:]):
        if it == 0:
            params['INPUTS']['INSTRUMENT'] = arg

        if arg.startswith('--'):
            key = arg.strip('--').upper()
            params['INPUTS'][key] = True

    # run the __main__ function
    __main__(None, params)


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
    # default value
    props = dict()
    props['path'] = None
    props['chdir'] = False

    storage = dict()
    # ----------------------------------------------------------------------
    # --data option
    # ----------------------------------------------------------------------
    # deal with --data keyword
    if 'DATA' in params['INPUTS']:
        if params['INPUTS']['DATA']:
            value = os.path.dirname(params['DRS_DATA_RAW'])
            # set change dir to True
            if os.path.exists(value):
                props['chdir'] = True
                props['path'] = value
            # append to storage
            storage['Data Directory'] = value

    # ----------------------------------------------------------------------
    # --raw option
    # ----------------------------------------------------------------------
    # deal with --data keyword
    props, storage = get_path(params, storage, props, 'RAW', 'DRS_DATA_RAW')

    # ----------------------------------------------------------------------
    # --tmp option
    # ----------------------------------------------------------------------
    # deal with --data keyword
    props, storage = get_path(params, storage, props, 'TMP', 'DRS_DATA_WORKING')

    # ----------------------------------------------------------------------
    # --red option
    # ----------------------------------------------------------------------
    # deal with --red keyword
    props, storage = get_path(params, storage, props, 'RED', 'DRS_DATA_REDUC')

    # ----------------------------------------------------------------------
    # --calib option
    # ----------------------------------------------------------------------
    # deal with --calib keyword
    props, storage = get_path(params, storage, props, 'CALIB', 'DRS_CALIB_DB')

    # ----------------------------------------------------------------------
    # --tellu option
    # ----------------------------------------------------------------------
    # deal with --tellu keyword
    props, storage = get_path(params, storage, props, 'TELLU', 'DRS_TELLU_DB')

    # ----------------------------------------------------------------------
    # --msg option
    # ----------------------------------------------------------------------
    # deal with --msg keyword
    props, storage = get_path(params, storage, props, 'MSG', 'DRS_DATA_MSG')

    # ----------------------------------------------------------------------
    # --plot option
    # ----------------------------------------------------------------------
    # deal with --plot keyword
    props, storage = get_path(params, storage, props, 'PLOT', 'DRS_DATA_PLOT')

    # ----------------------------------------------------------------------
    # Deal with multiple arguments --> print
    # ----------------------------------------------------------------------
    if len(storage) > 1:
        for item in storage:
            print('{0}: {1}'.format(item, storage[item]))
        multiple = True
    else:
        multiple = False

    # ----------------------------------------------------------------------
    # Change of path
    # ----------------------------------------------------------------------
    # deal with a change of path
    if props['chdir'] and props['path'] is not None and not multiple:
        print(props['path'])

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


def get_path(params, storage, props, input_key, param_key):

    # check for input key
    if input_key in params['INPUTS']:
        # if is set to True then populate variables
        if params['INPUTS'][input_key]:
            # get the value from params
            value = params[param_key]
            # check path
            if os.path.exists(value):
                props['chdir'] = True
                props['path'] = value
            # update storage
            storage[param_key] = value
    # return props and storage
    return props, storage


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================

