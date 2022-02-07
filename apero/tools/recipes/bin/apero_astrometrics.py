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
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.utils import drs_startup
from apero.tools.module.database import manage_databases
from apero.tools.module.setup import drs_installation
from apero.tools.module.database import drs_astrometrics

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_astrometric.py'
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
    # get the overwrite parameter
    overwrite = params['INPUTS']['OVERWRITE']
    # ----------------------------------------------------------------------
    # step 1: Is object in database?
    # ----------------------------------------------------------------------
    # query local object database
    unfound_objs = drs_astrometrics.query_database(params, rawobjs, overwrite)
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
        # ---------------------------------------------------------------------
        # search in simbad for objects
        astro_objs, reason = drs_astrometrics.query_simbad(params,
                                                           rawobjname=objname)
        # ---------------------------------------------------------------------
        # deal with 1 object
        if len(astro_objs) == 1:
            # get first object
            astro_obj = astro_objs[0]
            # display the properties for this object
            astro_obj.display_properties()
            # construct the object correction question
            question2 = 'Does the data for this object look correct?'
            cond2 = drs_installation.ask(question2, dtype='YN')
            print()
            # -----------------------------------------------------------------
            # if correct add to add list
            if cond2:
                # -------------------------------------------------------------
                # but first check whether main name
                question3 = (f'Modify main object name="{astro_obj.name}"'
                             '(will set DRSOBJN) all other '
                             'names will added to aliases')
                cond3 = drs_installation.ask(question3, dtype='YN')
                # if user want to modify name let them
                if cond3:
                    # ask for new name
                    question4 = f'Enter new main name for "{astro_obj.name}"'
                    rawuname = drs_installation.ask(question4, dtype=str)
                    # clean object name
                    pconst = constants.pload()
                    # must add the old name to the aliases
                    astro_obj.aliases += f'|{astro_obj.objname}'
                    # update the name and objname
                    astro_obj.name = pconst.DRS_OBJ_NAME(rawuname)
                    astro_obj.objname = astro_obj.name
                    # log change of name
                    WLOG(params, '', f'\t Object name set to: {astro_obj.name}')
                # -------------------------------------------------------------
                # now add object to database
                msg = 'Adding {0} to object list'.format(astro_obj.name)
                WLOG(params, '', msg)
                # append to add list
                add_objs.append(astro_obj)
            # else print that we are not adding object to database
            else:
                WLOG(params, '', 'Not adding object to database')
        elif len(astro_objs) == 0:
            emsg = ('Cannot find object "{0}" in SIMBAD. \n\t{1}'
                    '\n\tPlease try another alias')
            eargs = [objname, reason]
            WLOG(params, 'warning', emsg.format(*eargs), sublevel=6)

        else:
            # print warning
            emsg = ('More than one object matches object "{0}" in SIMBAD. '
                    'Please try another alias.')
            WLOG(params, 'warning', emsg.format(objname), sublevel=6)
            # print list of aliases for each object found
            msg = 'List of aliases:'
            WLOG(params, '', msg, colour='yellow')
            # loop around objects found
            for a_it, astro_obj in enumerate(astro_objs):
                msg = 'Object {0}: {1}'
                margs = [a_it + 1, ','.join(astro_obj.aliases.split('|'))]
                WLOG(params, '', msg.format(*margs), colour='yellow')
                WLOG(params, '', '')
    # -------------------------------------------------------------------------
    # get index database
    indexdbm = drs_database.IndexDatabase(params)
    # check for Teff (from files on disk with this objname / aliases)
    for astro_obj in add_objs:
        astro_obj.check_teff(params, indexdbm)
    # -------------------------------------------------------------------------
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
