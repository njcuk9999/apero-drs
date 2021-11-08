#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-11-08

@author: cook
"""
import numpy as np
from typing import Dict, List, Optional

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
from apero.science import preprocessing as prep
from apero.science import telluric
from apero.tools.module.database import manage_databases
from apero.tools.module.processing import drs_processing


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_precheck.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
DrsInputFile = drs_file.DrsInputFile
# Get index database
IndexDatabase = drs_database.IndexDatabase
ObjectDatabase = drs_database.ObjectDatabase
# get text entry instance
textentry = lang.textentry


# =============================================================================
# Define file checking functions
# =============================================================================
def file_check(params: ParamDict, recipe: DrsRecipe,
               indexdbm: Optional[IndexDatabase] = None):
    """
    Check the current index database for possible problems in the raw file set

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe instance, the recipe that called this function
    :param indexdbm: IndexDatabase instance or None (will load index database)

    :return: None, prints to screen
    """
    # deal with not having index database
    if indexdbm is None:
        # construct the index database instance
        indexdbm = IndexDatabase(params)
        indexdbm.load_db()
    # get unique observations directories
    uobsdirs = indexdbm.get_unique('OBS_DIR')
    # get the recipe module for this instrument
    recipemodule = recipe.recipemod.get()
    filemodule = recipe.filemod.get()
    # get the generic raw file type
    generic_raw_file = filemodule.raw_file
    # store calibs (for each observation directory)
    calib_count = dict()
    # store hot stars  (for each observation directory)
    tellu_count = dict()
    # store science targets (for each observation directory)
    science_count = dict()
    # -------------------------------------------------------------------------
    # get telluric stars and non-telluric stars
    # -------------------------------------------------------------------------
    # get all telluric stars
    tstars = telluric.get_tellu_include_list(params)
    # get all other stars
    ostars = drs_processing.get_non_telluric_stars(params, indexdbm, tstars)
    # -------------------------------------------------------------------------
    # get a list of calibration files
    # -------------------------------------------------------------------------
    # print progress
    # TODO: add to language database
    msg = 'Analysing calibration raw files on disk'
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', msg)
    WLOG(params, 'info', params['DRS_HEADER'])
    # get calibration files grouped by recipe
    calib_files = get_raw_seq_files(params, recipemodule, tstars, ostars,
                                    sequence='calib_seq')
    # loop around each night and check for all calibration files
    for uobsdir in uobsdirs:
        # assume we are not missing any calibrations
        missing = False
        # ---------------------------------------------------------------------
        # ignore the "other" directory
        if uobsdir == 'other':
            continue
        # else print observation directory
        else:
            msg = 'Processing observation directory: {0}'
            margs = [uobsdir]
            WLOG(params, 'info', msg.format(*margs), colour='magenta')
        # ---------------------------------------------------------------------
        # get all raw files for this night
        drsoutids = indexdbm.get_entries('KW_OUTPUT', obs_dir=uobsdir,
                                         block_kind='raw')
        # ---------------------------------------------------------------------
        # storage of the count for this observation directory
        calib_count[uobsdir] = dict()
        # loop around recipes
        for srecipe in calib_files:
            # -----------------------------------------------------------------
            # get run code
            runcode = 'RUN_{0}'.format(srecipe)
            # do not check recipes that do not have RUN_XXXX = True
            if runcode in params:
                if not params[runcode]:
                    continue
            # -----------------------------------------------------------------
            # storage for this recipe
            calib_count[uobsdir][srecipe] = dict()
            # loop around arguments
            for argname in calib_files[srecipe]:
                # loop around drs files
                for drsfile in calib_files[srecipe][argname]:
                    # count the number of files
                    count = np.sum(drsfile.name == drsoutids)
                    # add to count
                    calib_count[uobsdir][srecipe][drsfile.name] = count
                    # ---------------------------------------------------------
                    # print if missing
                    if count == 0:
                        msg = '\t\tMISSING {0}\t(OBS_DIR={1} RECIPE={2})'
                        margs = [drsfile, uobsdir, srecipe]
                        WLOG(params, 'warning', msg.format(*margs))
                        missing = True
        if not missing:
            msg = '\tMinimum number of calibrations found'
            WLOG(params, '', msg)
    # -------------------------------------------------------------------------
    # get a list of telluric files and science files
    # -------------------------------------------------------------------------
    msg = 'Analysing telluric and science raw files on disk'
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', msg)
    WLOG(params, 'info', params['DRS_HEADER'])
    tellu_files = get_raw_seq_files(params, recipemodule, tstars, ostars,
                                    sequence='tellu_seq')
    sci_files = get_raw_seq_files(params, recipemodule, tstars, ostars,
                                  sequence='science_seq')

    # -------------------------------------------------------------------------
    # if we are not using a telluric run don't include it
    for srecipe in tellu_files:
        # get run code
        runcode = 'RUN_{0}'.format(srecipe)
        # do not check recipes that do not have RUN_XXXX = True
        if runcode in params:
            if not params[runcode]:
                del tellu_files[srecipe]
    # report if None found
    if len(tellu_files) == 0:
        # log a warning if None found
        msg = 'No telluric RUN instances in run file "{0}". Skipping'
        margs = params['INPUTS']['RUNFILE']
        WLOG(params, 'warning', msg.format(*margs))
    # -------------------------------------------------------------------------
    # if we are not using a science run don't include it
    for srecipe in sci_files:
        # get run code
        runcode = 'RUN_{0}'.format(srecipe)
        # do not check recipes that do not have RUN_XXXX = True
        if runcode in params:
            if not params[runcode]:
                del sci_files[srecipe]
    if len(sci_files) == 0:
        # log a warning if None found
        msg = 'No science RUN instances in run file "{0}". Skipping'
        margs = params['INPUTS']['RUNFILE']
        WLOG(params, 'warning', msg.format(*margs))
    # -------------------------------------------------------------------------
    # combine file types (we don't care about recipes here)
    tfiles = _flatten_raw_seq_filelist(tellu_files, generic_raw_file)
    sfiles = _flatten_raw_seq_filelist(sci_files, generic_raw_file)
    # loop around each observation directory and check for all
    #     telluric/science files
    for uobsdir in uobsdirs:
        # add observation directory to storage
        tellu_count[uobsdir] = dict()
        science_count[uobsdir] = dict()
        # flag missing (assume missing)
        t_missing = True
        s_missing = True
        # ---------------------------------------------------------------------
        # ignore the "other" directory
        if uobsdir == 'other':
            continue
        # else print observation directory
        else:
            msg = 'Processing observation directory: {0}'
            margs = [uobsdir]
            WLOG(params, 'info', msg.format(*margs), colour='magenta')
        # ---------------------------------------------------------------------
        # get all raw files for this night
        rtable = indexdbm.get_entries('KW_OBJNAME, KW_OUTPUT', obs_dir=uobsdir,
                                      block_kind='raw')
        # mask telluric stars
        tellu_mask = np.in1d(rtable['KW_OBJNAME'], tstars)
        sci_mask = np.in1d(rtable['KW_OBJNAME'], ostars)
        # loop around telluric file types
        for drsfile in tfiles:
            # mask drsfile for tellu stars
            tmask = tellu_mask & (rtable['KW_OUTPUT'] == drsfile)
            # get count
            tcount = np.sum(tmask)
            # count tellu files
            tellu_count[uobsdir][drsfile] = tcount
            # print outs
            if tcount > 0:
                msg = '\tFound {0} {1} telluic files'
                margs = [tcount, drsfile]
                WLOG(params, '', msg.format(*margs))
                # we are not missing all telluric files
                t_missing = False

        # loop around science file types
        for drsfile in sfiles:
            # mask drsfile for science stars
            smask = sci_mask & (rtable['KW_OUTPUT'] == drsfile)
            # scount
            scount = np.sum(smask)
            # count science files
            science_count[uobsdir][drsfile] = scount
            # print outs
            if scount > 0:
                msg = '\tFound {0} {1} science files'
                margs = [scount, drsfile]
                WLOG(params, '', msg.format(*margs))
                # we are not missing all science files
                s_missing = False

        if t_missing:
            msg = '\tNo telluric files found for observation directory {0}'
            WLOG(params, 'warning', msg.format(uobsdir))
        if s_missing:
            msg = '\tNo science files found for observation directory {0}'
            WLOG(params, 'warning', msg.format(uobsdir))


def get_raw_seq_files(params: ParamDict, recipemod,
                      tstars: List[str], ostars: List[str],
                      sequence: str) -> Dict[str, Dict[str, List[DrsFitsFile]]]:
    """
    Get a dictionary of recipes where each entry is a dictionary of arguments
    where each entry is a list of possible raw files

    i.e.
        files['recipe1']['arg1'] = [raw_file_1, raw_file2]
        files['recipe1']['arg2'] = [raw_file_3, raw_file4]

    :param params: ParamDict
    :param recipemod: recipe module
    :param tstars: list of strings, the telluric stars object names
    :param ostars: list of strings, the non-telluric star object names
    :param sequence: str, the sequence name

    :return: dictionary
    """
    # print progress
    msg = 'Getting file types for sequence={0}'
    WLOG(params, '', msg.format(sequence))
    # -------------------------------------------------------------------------
    # get template list (if required)
    # -------------------------------------------------------------------------
    # get whether to recalculate templates
    _recal_templates = params['RECAL_TEMPLATES']
    # get a list of object names with templates
    template_object_list = []
    if not drs_text.null_text(_recal_templates, ['', 'None']):
        if not drs_text.true_text(_recal_templates):
            template_object_list = telluric.list_current_templates(params)
    # get the calibration sequence
    if hasattr(recipemod, sequence):
        seq = getattr(recipemod, sequence)
    else:
        return dict()
    # generate sequence
    seq.process_adds(params, tstars=list(tstars), ostars=list(ostars),
                     template_stars=template_object_list)
    # storage of calib files
    seq_files = dict()
    # get the sequence recipe list
    srecipelist = seq.sequence
    # loop around recipes
    for srecipe in srecipelist:
        # get the short name for this recipe
        srecipe_name = srecipe.shortname
        # get the standard input files for all arguments
        infiles = _get_infiles(srecipe)
        # get all raw files assoicated with these
        rawfiles = dict()
        # loop around arguments
        for argname in infiles:
            # set the raw files
            rawfiles[argname] = []
            # loop around files
            for infile in infiles[argname]:
                # get the raw files for this input file
                rawfile = _get_rawfile(infile)
                # push these into the list of files for this argument
                if isinstance(rawfile, list):
                    rawfiles[argname] += rawfile
                else:
                    rawfiles[argname].append(rawfile)
        # append raw files to a list
        seq_files[srecipe_name] = rawfiles
    # return calibration files
    return seq_files


def _flatten_raw_seq_filelist(files: Dict[str, Dict[str, List[DrsFitsFile]]],
                              generic_raw_file: DrsInputFile) -> List[str]:
    """
    Get a flattened list of raw sequence file names from the get_raw_seq_file
    dictionary return

    :param files: dictionary, the return of get_raw_seq_files
    :param generic_raw_file:  str, the generic raw file instance

    :return: list of strings, the file output ids in a flattened 1d list
    """
    flattened_files = []
    # loop around recipes
    for srecipe in files:
        # loop around arguments
        for argname in files[srecipe]:
            # loop around files
            for drsfile in files[srecipe][argname]:
                # do not include the generic raw file
                if drsfile.name == generic_raw_file.name:
                    continue
                # else add to tfiles list
                if drsfile.name not in flattened_files:
                    flattened_files.append(drsfile.name)
    # return flattened file list
    return flattened_files


def _get_infiles(srecipe: DrsRecipe):
    """
    Get all files (grouped by the argument they are required for)

    :param srecipe:
    :return:
    """

    # store input files
    infiles = dict()

    # look for files in arguments
    for argname in srecipe.args:
        # only deal with required arguments
        if not srecipe.args[argname].required:
            continue
        # get the files for this recipe's argument
        ifiles = srecipe.args[argname].files
        # if it has files then add this argument
        if len(ifiles) > 0:
            infiles[argname] = ifiles
    # look for files in keyword argumetns
    for kwargname in srecipe.kwargs:
        # only deal with required arguments
        if not srecipe.kwargs[kwargname].required:
            continue
        # get the files for this recipe's argument
        ifiles = srecipe.kwargs[kwargname].files
        # if it has files then add this argument
        if len(ifiles) > 0:
            infiles[kwargname] = ifiles
    # return the input files
    return infiles


def _get_rawfile(drsfile: DrsFitsFile):
    """
    Get the most base intype (i.e. the raw file) for an output file

    :param drsfile: DrsFile
    :return:
    """

    if isinstance(drsfile.intype, list):
        drsfiles = []
        for idrsfile in drsfile.intype:
            drsfiles.append(_get_rawfile(idrsfile))
        return drsfiles
    else:
        while drsfile.intype is not None:
            drsfile = drsfile.intype
        return drsfile


# =============================================================================
# Define object checking functions
# =============================================================================
def obj_check(params: ParamDict, indexdbm: Optional[IndexDatabase] = None):
    """
    Check the index database for unique objects and display which of these
    are not in the object database currently (and not in the rejection list)

    :param params: ParamDict, the parameter dictionary of constants
    :param indexdbm: IndexDatabase instance or None (will load index database)

    :return: None, prints to screen
    """
    # print progress
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', 'Checking current set of object names')
    WLOG(params, 'info', params['DRS_HEADER'])
    # ---------------------------------------------------------------------
    # get psuedo constants
    pconst = constants.pload()
    # deal with not having index database
    if indexdbm is None:
        # construct the index database instance
        indexdbm = IndexDatabase(params)
        indexdbm.load_db()
    # ---------------------------------------------------------------------
    # Update the object database (recommended only for full reprocessing)
    # check that we have entries in the object database
    manage_databases.object_db_populated(params)
    # update the database if required
    if params['UPDATE_OBJ_DATABASE']:
        # log progress
        WLOG(params, '', textentry('40-503-00039'))
        # update database
        manage_databases.update_object_database(params, log=False)
    # ---------------------------------------------------------------------
    # load the object database after updating
    objdbm = ObjectDatabase(params)
    objdbm.load_db()
    # ---------------------------------------------------------------------
    # get list of unique objects from index database
    uobjnames = indexdbm.get_unique('KW_OBJNAME',
                                    condition='BLOCK_KIND="raw"')
    # ---------------------------------------------------------------------
    # print progress
    # TODO: move to langauge database
    msg = 'Preparing list of unique objects from index database (N={0})'
    margs = [len(uobjnames)]
    WLOG(params, '', msg.format(*margs))
    # get the object rejection list
    reject_list = prep.get_obj_reject_list(params)
    # store list of objects not found in the database currently
    unfound_objects = []
    # loop around index database unique object names and check for them
    for uobjname in uobjnames:
        # clean the object
        uobjname = pconst.DRS_OBJ_NAME(uobjname)
        # find correct name in the database (via objname or aliases)
        correct_objname, found = objdbm.find_objname(pconst, uobjname)
        # ignore objects in the reject list
        if correct_objname in reject_list:
            continue

        # if object was not found add to list
        if not found:
            unfound_objects.append(correct_objname)
    # ---------------------------------------------------------------------
    # print any remaining objects
    # TODO: move to language database
    msg = 'Objects that will use the header for astrometrics are:'
    WLOG(params, '', msg, colour='magenta', wrap=False)
    # deal with having no unfound objects
    if len(unfound_objects) == 0:
        # print that all objects were found
        # TODO: move to language database
        msg = '\t All objects found (or in ignore list)!'
        WLOG(params, '', msg)
    # else we print the unfound objects
    else:
        # loop around objects and put on a new line
        for it, unfound_object in enumerate(unfound_objects):
            # print the object
            margs = [it + 1, unfound_object]
            WLOG(params, 'warning', '\t{0}\t{1}'.format(*margs))
        # print a note that some objects are in ignore list
        if len(reject_list) > 0:
            # TODO: move to language database
            msg = 'Note {0} objects are in the ignore list / ignore aliases'
            margs = [len(reject_list)]
            WLOG(params, 'info', msg.format(*margs))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
