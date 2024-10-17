#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:39

@author: cook
"""
from apero.constants import path_definitions
from apero.tools.module.setup import drs_reset
from apero.utils import drs_startup
from aperocore import drs_lang
from aperocore.base import base
from aperocore.core import drs_log

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_remove.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = drs_lang.textentry


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
    # get log and warn from inputs
    rawobsdir = params['INPUTS']['obsdir']
    blockstr = params['INPUTS']['blocks']
    fileprefix = params['INPUTS']['file_prefix']
    filesuffix = params['INPUTS']['file_suffix']
    objnamestr = params['INPUTS']['objnames']
    warn = not params['INPUTS']['nowarn']
    # ---------------------------------------------------------------------
    # if any are set to 'None' then set to None
    if fileprefix == 'None':
        fileprefix = None
    if filesuffix == 'None':
        filesuffix = None
    # ---------------------------------------------------------------------
    # deal with non test mode - ask the user
    if not params['INPUTS']['test'] and warn:
        msg = ('Warning this will remove files from disk and the database '
               'are you sure you want to continue?')
        # get user input
        user_input = input(msg + '\n\t[Y]es or [N]o')
        if 'Y' not in user_input.upper():
            params['INPUTS'].set('test', value=True)
        else:
            params['INPUTS'].set('test', value=False)
    # ---------------------------------------------------------------------
    # make sure we don't have a list of observation directories
    if rawobsdir == 'None':
        obsdir = None
    elif ',' in rawobsdir:
        obsdir = []
        # loop around object names
        for rawobsdir_it in rawobsdir.split(','):
            # get object name
            obsdir_it = rawobsdir_it.strip()
            # append to objnames
            obsdir.append(obsdir_it)
    elif isinstance(rawobsdir, str):
        obsdir = str(rawobsdir)
    else:
        obsdir = None
    # ---------------------------------------------------------------------
    # deal with blocks
    blocks = []
    if blockstr not in [None, 'None', 'Null', '']:
        # loop around blocks
        for raw_block in blockstr.split(','):
            # get block name
            block_name = raw_block.strip()
            # append to blocks
            blocks.append(block_name)
        # get valid blocks from instance
        valid_blocks = list(map(lambda block: block.name,
                                path_definitions.BLOCKS))
        # check if all blocks are valid
        for block in blocks:
            # generate an error for invalid block
            if block not in valid_blocks:
                emsg = ('Block "{0}" is not a valid block name.'
                        ' Please check --blocks argument.')
                WLOG(params, 'error', emsg.format(block))
            # do not allow block to be raw
            if block == 'raw':
                emsg = ('block contains "raw". We cannot remove raw files. '
                        'Please check --blocks argument.')
                WLOG(params, 'error', emsg)
    # ----------------------------------------------------------------------
    # object names
    objnames = []
    if objnamestr not in [None, 'None', 'Null', '']:
        # loop around object names
        for objname in objnamestr.split(','):
            # get object name
            obj_name = objname.strip()
            # append to objnames
            objnames.append(obj_name)
    # ----------------------------------------------------------------------
    # Must check that we are not inside an apero directory (for safety)
    drs_reset.check_cwd(params)
    # ----------------------------------------------------------------------
    # get a list of files to remove (using the file index database)
    filetable1, condition1 = drs_reset.get_filelist(params, obsdir, blocks,
                                                    fileprefix, filesuffix,
                                                    objnames)
    # if we are remove raw file entries from database we have to run this
    #  query again
    if params['INPUTS']['RAWDB']:
        filetable2, condition2 = drs_reset.get_filelist(params, obsdir, blocks,
                                                        fileprefix, filesuffix,
                                                        objnames,
                                                        include_raw=True)
    # if we are not removing raw files from the database then use the same
    # as before
    else:
        filetable2, condition2 = filetable1, condition1
    # ----------------------------------------------------------------------
    # remove the files from disk
    disk_entries = drs_reset.remove_files_from_disk(params, filetable1)

    # ----------------------------------------------------------------------
    # remove files from database
    db_entries = drs_reset.remove_files_from_databases(params, filetable2,
                                                       condition2)

    # ----------------------------------------------------------------------
    if params['INPUTS']['test']:
        msg1 = 'Would have removed {0} files from disk'
        msg2 = 'Would have removed {0} entries from database {1}'
    else:
        msg1 = 'Removed {0} files from disk'
        msg2 = 'Removed {0} entries from database {1}'

    # print stats on removed files
    WLOG(params, 'info', msg1.format(disk_entries))
    # print stats on removed database entries
    for db_key in db_entries:
        WLOG(params, 'info', msg2.format(db_entries[db_key], db_key))

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
