#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get files with specific filters

Created on 2021-06-11

@author: cook
"""
import os
import shutil
from typing import Dict, List, Tuple

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_text
from apero.core.utils import drs_startup


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_get.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
ParamDict = constants.ParamDict


# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs):
    """
    Main function for apero_explorer.py

    :param instrument: str, the instrument name
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
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       enable_plotter=False)
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



def basic_filter(params: ParamDict, kw_objnames: List[str],
                 filters: Dict[str, List[str]], user_outdir: str,
                 do_copy: bool = True, do_symlink: bool = False
                 ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    The basic filter function - copies files into OBJNAME directories
    based on the

    :param params: ParamDict, the parameter dictionary of constants
    :param kw_objnames: list of strings, the object names to filter
    :param filters: dictionary of list of strings, each entry is a specific
                    filter from the index database
                    i.e.
                    filters['KW_DPRTYPE'] = ['OBJ_FP', 'OBJ_DARK']
    :param user_outdir: str, the output directory
    :param do_copy: bool, if True copies files (else just prints)
    :param do_symlink: bool, if True creates symlink instead of copying files

    :return: Tuple, 1. dict, for each objname a list of input file locations
                    2. dict, for each objname a list of output file locations
    """
    # TODO: move all strings to language database
    # -------------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    # -------------------------------------------------------------------------
    # load index database
    WLOG(params, '', 'Loading database...')
    indexdb = drs_database.IndexDatabase(params)
    indexdb.load_db()
    # -------------------------------------------------------------------------
    # create master condition
    master_condition = ''
    # loop around filters
    for _filter in filters:
        subconditions = []
        # get filter items
        filter_items = filters[_filter]
        # skip Nones
        if drs_text.null_text(filter_items, ['None', '', 'Null']):
            continue
        # loop around object names
        for item in filter_items:
            # skip Nones
            if drs_text.null_text(item, ['None', '', 'Null']):
                continue
            # add to sub conditions
            subcondition = '({0}="{1}")'.format(_filter, item)
            subconditions.append(subcondition)
        # deal with no valid sub-conditions
        if len(subconditions) == 0:
            continue
        # add to condition
        if len(master_condition) == 0:
            master_condition += '({0})'.format(' OR '.join(subconditions))
        else:
            master_condition += ' AND ({0})'.format(' OR '.join(subconditions))
    # -------------------------------------------------------------------------
    # separate list for each object name
    # -------------------------------------------------------------------------
    # storage of inpaths
    database_inpaths = dict()
    # loop around input object names
    for kw_objname in kw_objnames:
        # clean object name (as best we can)
        clean_obj_name = pconst.DRS_OBJ_NAME(kw_objname)
        WLOG(params, '', 'Processing KW_OBJNAME={0}'.format(clean_obj_name))
        # write condition for this object
        if drs_text.null_text(kw_objname, ['None', '', 'Null']):
            obj_condition = None
        else:
            obj_condition = '(KW_OBJNAME="{0}")'.format(clean_obj_name)
        # deal with having an object condition
        condition = ''
        if obj_condition is not None:
            condition += str(obj_condition)
        # deal with having a master condition
        if len(master_condition) > 0:
            # deal with not having an object condition (don't need the AND)
            if obj_condition is None:
                condition += str(master_condition)
            # deal with having an object condition (need an AND)
            else:
                condition += ' AND {0}'.format(master_condition)
        # deal with no condition still (set condition to None)
        if len(condition) == 0:
            condition = None
        # get inpaths
        inpaths = indexdb.get_entries('ABSPATH', condition=condition)
        # load into file storage
        if len(inpaths) > 0:
            WLOG(params, '', '\tFound {0} entries'.format(len(inpaths)))
            database_inpaths[clean_obj_name] = inpaths
        else:
            WLOG(params, '', '\tFound no entries')
    # -------------------------------------------------------------------------
    # Now get outpaths (if infile exists)
    # -------------------------------------------------------------------------
    # storage of inpaths/outpaths
    all_inpaths = dict()
    all_outpaths = dict()
    # loop around objects with files
    for objname in database_inpaths:
        # output directory for objname
        outdir = os.path.join(user_outdir, objname)
        # print progress
        WLOG(params, '', 'Adding outpaths for KW_OBJNAME={0}'.format(objname))
        # add object name to storage
        all_inpaths[objname] = []
        all_outpaths[objname] = []
        # loop around all files for this object
        for filename in database_inpaths[objname]:
            # if object exists
            if os.path.exists(filename):
                # get paths
                inpath = filename
                basename = os.path.basename(filename)
                outpath = os.path.join(outdir, basename)
                # add to storage
                all_inpaths[objname].append(inpath)
                all_outpaths[objname].append(outpath)
        # make a directory for this object (if it doesn't exist)
        if len(all_outpaths[objname]) != 0:
            # print progress
            msg = '\tAdded {0} outpaths'
            margs = [len(all_outpaths[objname])]
            WLOG(params, '', msg.format(*margs))
            # create output directory if it doesn't exist
            if not os.path.exists(outdir) and do_copy:
                os.mkdir(outdir)
    # -------------------------------------------------------------------------
    # Copy files
    # -------------------------------------------------------------------------
    for objname in all_inpaths:
        WLOG(params, '', '')
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', 'COPY OBJNAME={0}'.format(objname))
        WLOG(params, '', params['DRS_HEADER'])
        WLOG(params, '', '')
        # loop around files
        for row in range(len(all_inpaths[objname])):
            # get in and out path
            inpath = all_inpaths[objname][row]
            outpath = all_outpaths[objname][row]
            # print string
            copyargs = [row + 1, len(all_inpaths[objname]), outpath]
            copystr = '[{0}/{1}] --> {2}'.format(*copyargs)
            # print copy string
            WLOG(params, '', copystr, wrap=False)
            # copy
            if do_symlink:
                os.symlink(inpath, outpath)
            elif do_copy:
                shutil.copy(inpath, outpath)

    return all_inpaths, all_outpaths


def __main__(recipe, params):
    """
    Main function - using user inputs (or gui inputs) filters files and
    copies them to a new location

    :param instrument: string, the instrument name
    :type: str
    :return: returns the local namespace as a dictionary
    :rtype: dict
    """
    # get inputs from user
    inputs = params['INPUTS']
    use_gui = params['INPUTS']['GUI']
    if use_gui:
        WLOG(params, 'warning', 'Not Implemented yet',
             sublevel=2)
        return drs_startup.return_locals(params, locals())
    # get filters from user inputs
    kw_objnames = inputs.listp('objnames', dtype=str, required=False)
    kw_dprtypes = inputs.listp('dprtypes', dtype=str, required=False)
    kw_outputs = inputs.listp('outtypes', dtype=str, required=False)
    kw_fibers = inputs.listp('fibers', dtype=str, required=False)
    # get outpath from user inputs
    user_outdir = params['INPUTS']['OUTPATH']
    if drs_text.null_text(user_outdir, ['None', '', 'Null']):
        user_outdir = os.getcwd()
    # get copy criteria from user inputs
    do_copy = not params['INPUTS']['TEST']
    # get sym link criteria from user inputs
    do_symlink = params['INPUTS']['SYMLINKS']
    # check for None
    if drs_text.null_text(kw_objnames, ['None', '', 'Null']):
        kw_objnames = None
    if drs_text.null_text(kw_dprtypes, ['None', '', 'Null']):
        kw_dprtypes = None
    if drs_text.null_text(kw_outputs, ['None', '', 'Null']):
        kw_outputs = None
    if drs_text.null_text(kw_fibers, ['None', '', 'Null']):
        kw_fibers = None
    # push filters into dictionary (not object names these are special)
    filters = dict()
    filters['KW_DPRTYPE'] = kw_dprtypes
    filters['KW_OUTPUT'] = kw_outputs
    filters['KW_FIBER'] = kw_fibers
    # run basic filter
    indict, outdict = basic_filter(params, kw_objnames, filters, user_outdir,
                                   do_copy, do_symlink)
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
