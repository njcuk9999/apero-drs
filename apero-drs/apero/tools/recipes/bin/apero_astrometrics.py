#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-12-09

@author: cook
"""
from aperocore.base import base
from aperocore.constants import param_functions
import apero as apero_pkg
from aperocore import drs_lang
from aperocore.core import drs_log
from apero.utils import drs_startup
from apero.tools.module.database import drs_astro_wrap
from apero.tools.module.database import manage_databases
from apero.tools.module.setup import drs_installation

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_astrometrics.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
# get text entry instance
textentry = drs_lang.textentry
# Get Logging function
WLOG = drs_log.wlog
ParamDict = param_functions.ParamDict


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
    # get the filename parameter (and modify inputs if required)
    params = drs_astro_wrap.identify_from_file(params)
    # get the raw objects
    rawobjs = params['INPUTS']['OBJECTS']
    # get the overwrite parameter
    overwrite = params['INPUTS']['OVERWRITE']
    # get the check parameter
    check = params['INPUTS']['CHECK']
    if check:
        drs_astro_wrap.check_database(params, recipe.shortname)
        return locals()
    # ----------------------------------------------------------------------
    # step 1: Is object in database?
    # ----------------------------------------------------------------------
    # query local object database
    unfound_objs, found_objs = drs_astro_wrap.query_database(params,
                                                             recipe.shortname,
                                                             rawobjs,
                                                             overwrite)
    # stop here if all objects found
    if len(found_objs) > 0:
        # check that object doesn't currently have problems
        drs_astro_wrap.check_object(params, recipe, found_objs)
    # if we have no unfound object stop here
    if len(unfound_objs) == 0:
        # log: All objects found in database
        WLOG(params, 'info', textentry('40-512-00014'))
        return locals()

    # ----------------------------------------------------------------------
    # step 2: Can we find object automatically from simbad?
    # ----------------------------------------------------------------------
    # store astrometric objects that we need to add to database
    add_objs = []
    # loop around unfound objects
    for objname in unfound_objs:
        # print header title
        WLOG(params, 'info', params['LOG.HEADER'])
        margs = [objname]
        # log: Processing: {0}
        WLOG(params, 'info', textentry('40-512-00006', args=margs))
        WLOG(params, 'info', params['LOG.HEADER'])
        # construct add object question
        question1 = '\n\nAdd OBJECT="{0}" to astrometric database?'
        # ask if we want to find object
        cond = drs_installation.ask(question1.format(objname), dtype='YN',
                                    color='m')
        print()
        # if not skip
        if not cond:
            continue
        # ---------------------------------------------------------------------
        # search in simbad for objects
        astro_objs, reason = drs_astro_wrap.query_simbad(params,
                                                         rawobjname=objname)
        # ---------------------------------------------------------------------
        # deal with 1 object
        if len(astro_objs) == 1:
            # get first object
            astro_obj = astro_objs[0]
            # ask user about object
            aout = drs_astro_wrap.ask_user(params, recipe, astro_obj)
            astro_obj, add_to_list = aout
            # finally add to list
            if add_to_list:
                # append to add list
                add_objs.append(astro_obj)
        # --------------------------------------------------------------------
        # if we cannot find in simbad try to look elsewhere
        if len(astro_objs) == 0 and 'proper motion catalog' not in reason:
            # try to look up object elsewhere
            astro_obj, reason1 = drs_astro_wrap.lookup(params, objname)
            reason += reason1
            # if astro_obj is not None we found it elsewhere
            if astro_obj is not None:
                # ask user about object
                aout = drs_astro_wrap.ask_user(params, recipe, astro_obj)
                astro_obj, add_to_list = aout
                # finally add to list
                if add_to_list:
                    # append to add list
                    add_objs.append(astro_obj)
                # add to astro_objs
                astro_objs = [astro_obj]
        # --------------------------------------------------------------------
        # if we still have no objects deal with no objects
        if len(astro_objs) == 0:
            eargs = [objname, reason]
            # warning: Invalid object "{0}". \n {1} \n Please try another alias
            WLOG(params, 'warning', textentry('10-512-00002', args=eargs),
                 sublevel=6, colour='red')
        # --------------------------------------------------------------------
        # else deal with multiple objects
        elif len(astro_objs) > 1:
            # print warning
            wargs = [objname]
            # warning: More than one object matches object "{0}" in SIMBAD.
            #     Please try another alias.
            WLOG(params, 'warning', textentry('10-512-00003', args=wargs),
                 sublevel=6)
            # print list of aliases for each object found
            WLOG(params, '', textentry('40-512-00015'), colour='yellow')
            # loop around objects found
            for a_it, astro_obj in enumerate(astro_objs):
                margs = [a_it + 1, ','.join(astro_obj.aliases.split('|'))]
                # log: Object {0}: {1}
                WLOG(params, '', textentry('40-512-00018', args=margs),
                     colour='yellow')
                WLOG(params, '', '')
        # --------------------------------------------------------------------
        # make sure we add all aliases without white space
        for astro_obj in astro_objs:
            astro_obj.all_aliases()

    # -------------------------------------------------------------------------
    # add to google sheet
    if len(add_objs) > 0:
        # print progress
        WLOG(params, 'info', params['LOG.HEADER'])
        # log: Updating pending-list online database
        WLOG(params, 'info', textentry('40-512-00007'))
        WLOG(params, 'info', params['LOG.HEADER'])
        # add all objects in add list to google-sheet
        drs_astro_wrap.add_obj_to_sheet(params, add_objs)
        # log progress
        # log: Updating object database (from google sheets)
        WLOG(params, '', textentry('40-503-00039'))
        # update database
        manage_databases.validate_astrometric_yaml_archive(params, log=False)

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
