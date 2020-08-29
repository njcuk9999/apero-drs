#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-11-14 at 10:52

@author: cook
"""
import numpy as np
import os
import glob

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_database2 as drs_database
from apero.io import drs_fits
from apero.tools.module.database import create_databases

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_mkdb.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
# Define master prefix
MASTER_PREFIX = 'MASTER_'


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
    Main function for apero_mkdb.py

    :param instrument: str, the instrument name
    :param kwargs: additional keyword arguments

    :type instrument: str

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(instrument=instrument, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, instrument, fkwargs)
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
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get database type
    db_type = params['INPUTS']['KIND']
    assetdir = params['DRS_DATA_ASSETS']
    # get the pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # ----------------------------------------------------------------------
    # get the settings for each type of database
    if db_type == 'calibration':
        db_path = params['DRS_CALIB_DB']
        name = 'calibration database'
        file_set_name = 'calib_file'
        # load the calibration database
        dbmanager = drs_database.CalibrationDatabase(params)
        dbmanager.load_db()
    elif db_type == 'telluric':
        db_path = params['DRS_TELLU_DB']
        name = 'telluric database'
        file_set_name = 'tellu_file'
        # load the telluric database
        dbmanager = drs_database.TelluricDatabase(params)
        dbmanager.load_db()
    else:
        eargs = [db_type]
        WLOG(params, 'error', TextEntry('09-505-00001', args=[db_type]))
        dbmanager = None
        db_path = None
        name = None
        file_set_name = None
    # ----------------------------------------------------------------------
    # get a list of all database paths
    db_list = create_databases.list_databases(params)
    # backup database
    dbmanager.database.backup()
    # reset database
    if db_type == 'calibration':
        # reset database
        create_databases.create_calibration_database(params, pconst, db_list)
        # reload the calibration database
        dbmanager = drs_database.CalibrationDatabase(params)
        dbmanager.load_db()
    elif db_type == 'telluric':
        create_databases.create_telluric_database(pconst, db_list)
        # reload the telluric database
        dbmanager = drs_database.CalibrationDatabase(params)
        dbmanager.load_db()
    # ----------------------------------------------------------------------
    # get all fits files in the cdb path
    db_files = np.sort(glob.glob(db_path + os.sep + '*.fits'))
    # ----------------------------------------------------------------------
    # get the file mod for this instrument
    filemod = pconst.FILEMOD()
    # ----------------------------------------------------------------------
    # define storage of found files
    db_times = []
    # ----------------------------------------------------------------------
    # loop around all calib files and get the modified times
    for it, db_file in enumerate(db_files):
        # get the modified time of the file
        modtime = os.path.getmtime(db_file)
        # append to db_times
        db_times.append(modtime)
    # ----------------------------------------------------------------------
    # sort by time
    sortmask = np.argsort(db_times)
    db_files = np.array(db_files)[sortmask]
    # ----------------------------------------------------------------------
    # loop around all calib files and try to find the kinds
    for it, db_file in enumerate(db_files):
        # log progress
        wargs = [it + 1, len(db_files), os.path.basename(db_file)]
        WLOG(params, 'info', TextEntry('40-505-00001', args=wargs))
        # ------------------------------------------------------------------
        if not hasattr(filemod, file_set_name):
            eargs = [name, file_set_name, filemod, mainname]
            WLOG(params, 'error', TextEntry('00-505-00001', args=eargs))
            file_set = None
        else:
            file_set = getattr(filemod, file_set_name)
        # ------------------------------------------------------------------
        # skip default master files
        if os.path.basename(db_file).startswith(MASTER_PREFIX):
            # log skipping
            wargs = [MASTER_PREFIX]
            WLOG(params, 'info', TextEntry('40-505-00003', args=wargs))
            # skip
            continue
        # ------------------------------------------------------------------
        # make a new copy of out_file
        db_out_file = file_set.newcopy(recipe=recipe)
        # ------------------------------------------------------------------
        # try to find cdb_file
        found, kind = drs_fits.id_drs_file(params, recipe, db_out_file,
                                           filename=db_file, nentries=1,
                                           required=False)
        # ------------------------------------------------------------------
        # append to cdb_data
        if found:
            # log that we found i
            WLOG(params, '', TextEntry('40-505-00002', args=[kind]))
            # --------------------------------------------------------------
            # add the files back to the database
            if db_type == 'calibration':
                dbmanager.add_calib_file(kind, copy_files=False, verbose=False)
            elif db_type == 'telluric':
                dbmanager.add_tellu_file(kind, copy_files=False, verbose=False)

        # ------------------------------------------------------------------
        # delete file
        del kind, db_out_file

    # print note about masters
    WLOG(params, 'info', TextEntry('40-505-00004'))
    _ = input('\t')

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
