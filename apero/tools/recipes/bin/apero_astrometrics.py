#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-12-09

@author: cook
"""
from apero import lang
from apero.base import base
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.tools.module.database import manage_databases
from apero.tools.module.setup import drs_installation
from apero.tools.module.database import drs_astrometrics

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_astrometrics.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get text entry instance
textentry = lang.textentry
# Get Logging function
WLOG = drs_log.wlog


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
    Main function for apero_reset.py

    :param kwargs: additional keyword arguments
    :keyword debug: int, debug level (0 for None)

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
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    # get the raw objects
    rawobjs = params['INPUTS'].listp('OBJECTS', dtype=str)

    # ----------------------------------------------------------------------
    # step 1: Is object in database?
    # ----------------------------------------------------------------------
    # query local object database
    unfound_objs = drs_astrometrics.query_database(params, rawobjs)
    # stop here if all objects found
    if len(unfound_objs) == 0:
        msg = 'All objects found in database'
        WLOG(params, 'info', msg)
        return drs_startup.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # step 2: Can we find object automatically from simbad?
    # ----------------------------------------------------------------------
    # store astrometric objects that we need to add to database
    add_objs = []
    # loop around unfound objects
    for objname in unfound_objs:
        # construct add object question
        question1 = '\n\nAdd OBJECT="{0}" to astrometric database?'
        # ask if we want to find object
        cond = drs_installation.ask(question1.format(objname), dtype='YN')
        print()
        # if not skip
        if not cond:
            continue
        # search in simbad for objects
        astro_objs = drs_astrometrics.query_simbad(params, rawobjname=objname)
        # deal with 1 object
        if len(astro_objs) == 1:
            # get first object
            astro_obj = astro_objs[0]
            # display the properties for this object
            astro_obj.display_properties()
            # construct the object correction question
            question2 = 'Does the data for this object look correct?'
            cond = drs_installation.ask(question2, dtype='YN')
            print()
            # if correct add to add list
            if cond:
                msg = 'Adding {0} to object list'.format(astro_obj.name)
                WLOG(params, '', msg)
                # append to add list
                add_objs.append(astro_obj)
            # else print that we are not adding object to database
            else:
                WLOG(params, '', 'Not adding object to database')

    # add to google sheet
    if len(add_objs) > 0:
        # add all objects in add list to google-sheet
        drs_astrometrics.add_obj_to_sheet(params, add_objs)
        # log progress
        WLOG(params, '', textentry('40-503-00039'))
        # update database
        manage_databases.update_object_database(params, log=False)

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
