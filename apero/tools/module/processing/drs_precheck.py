#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2021-11-08

@author: cook
"""
from typing import Dict, List, Optional, Tuple

import numpy as np
from astropy.table import Table
from tqdm import tqdm

from apero.base import base
from apero.core import constants
from apero.core import lang
from apero.core import math as mp
from apero.core.core import drs_argument
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
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
DrsArgument = drs_argument.DrsArgument
DrsFitsFile = drs_file.DrsFitsFile
DrsInputFile = drs_file.DrsInputFile
# Get index database
FileIndexDatabase = drs_database.FileIndexDatabase
ObjectDatabase = drs_database.AstrometricDatabase
# get text entry instance
textentry = lang.textentry


# =============================================================================
# Define file checking functions
# =============================================================================
def calib_check(params: ParamDict, recipe: DrsRecipe, tstars: List[str],
                ostars: List[str], uobsdirs: np.ndarray, condition: str,
                findexdbm: FileIndexDatabase, log: bool = True
                ) -> Tuple[Dict[str, dict], Dict[str, list], List[str]]:
    """
    Check for calibration files

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: Recipe, the recipe instance that called this function
    :param tstars: list of hot (telluric) stars
    :param ostars: list of science targets
    :param uobsdirs: numpy array of strings, the unique observation directories
    :param condition: str, the SQL condition to use
    :param findexdbm: FileIndexDatabase, the file index database
    :param log: bool, if True prints messages to screen (default True)

    :return: tuple, 1. the calibration count for each obsdir
                    2. the calibration times for each obsdir
                    3. a list of bad calibration nights
    """
    # store calibs (for each observation directory)
    calib_count = dict()
    calib_times = dict()
    bad_calib_nights = []
    # get the recipe module for this instrument
    recipemodule = recipe.recipemod.get()
    # print progress
    if log:
        WLOG(params, 'info', params['DRS_HEADER'])
        WLOG(params, 'info', textentry('40-503-00047'))
        WLOG(params, 'info', params['DRS_HEADER'])
    # get calibration files grouped by recipe
    cout = get_raw_seq_files(params, recipemodule, tstars, ostars,
                             sequence='calib_seq', log=log)
    calib_files, calib_recipes, calib_args = cout
    # loop around each night and check for all calibration files
    for uobsdir in uobsdirs:
        uobsdir = str(uobsdir)
        # assume we are not missing any calibrations
        missing = False
        # ---------------------------------------------------------------------
        # ignore the "other" directory
        if uobsdir == 'other':
            continue
        # else print observation directory
        elif log:
            # print msg: Processing observation directory: {0}
            WLOG(params, 'info', textentry('40-503-00048', args=[uobsdir]),
                 colour='magenta')
        # ---------------------------------------------------------------------
        # get all raw files for this night
        itable = findexdbm.get_entries('KW_OUTPUT,KW_MID_OBS_TIME',
                                       obs_dir=uobsdir, condition=condition)
        # get columns
        drsoutids = itable['KW_OUTPUT']
        mjdmids = itable['KW_MID_OBS_TIME']
        # ---------------------------------------------------------------------
        # storage of the count for this observation directory
        calib_count[uobsdir] = dict()
        calib_times[uobsdir] = []
        # loop around recipes
        for recipe_name in calib_files:
            # -----------------------------------------------------------------
            # get run code
            runcode = 'RUN_{0}'.format(recipe_name)
            # get recipe
            srecipe = calib_recipes[recipe_name]
            # do not check recipes that do not have RUN_XXXX = True
            if runcode in params:
                if not params[runcode]:
                    continue
            # -----------------------------------------------------------------
            # storage for this recipe
            calib_count[uobsdir][recipe_name] = dict()
            # loop around arguments
            for argname in calib_files[recipe_name]:
                # get argument instance
                arg = calib_args[recipe_name][argname]
                # deal with exclusive files
                if arg.filelogic == 'exclusive':
                    # loop around drs files
                    for drsfile in calib_files[recipe_name][argname]:
                        # mask of current files
                        dmask = drsfile.name == drsoutids
                        # count the number of files
                        count = np.sum(dmask)
                        # add to count
                        calib_count[uobsdir][recipe_name][drsfile.name] = count
                        # get the time for this drs file
                        if count > 0:
                            calib_times[uobsdir] += list(np.unique(mjdmids[dmask]))
                        # ---------------------------------------------------------
                        # print if missing
                        if count == 0 and srecipe.calib_required:
                            if log:
                                # print warning: MISSING {0} OBS_DIR={1}
                                #                RECIPE={2})
                                wargs = [drsfile, uobsdir, recipe_name]
                                wmsg = textentry('10-503-00025', args=wargs)
                                WLOG(params, 'warning', wmsg, sublevel=2)
                            missing = True
                # deal with inclusive files (combine drsfiles)
                else:
                    # store drs file names (for reporting)
                    drsfiles = []
                    # set up mask (added via OR statement)
                    dmask = np.zeros(len(drsoutids), dtype=bool)
                    # loop around drs files
                    for drsfile in calib_files[recipe_name][argname]:
                        # add to inclusive files
                        drsfiles += [drsfile.name]
                        # mask of current files
                        dmask |= (drsfile.name == drsoutids)
                    # combine drs file names
                    drsfilenames = ','.join(drsfiles)
                    # count the number of files
                    count = np.sum(dmask)
                    # add to count
                    calib_count[uobsdir][recipe_name][drsfilenames] = count
                    # get the time for this drs file
                    calib_times[uobsdir] += list(np.unique(mjdmids[dmask]))
                    # print if missing
                    if count == 0 and srecipe.calib_required:
                        if log:
                            # print warning: MISSING {0} OBS_DIR={1} RECIPE={2})
                            wargs = [drsfilenames, uobsdir, recipe_name]
                            wmsg = textentry('10-503-00025', args=wargs)
                            WLOG(params, 'warning', wmsg, sublevel=2)
                        missing = True
        if not missing:
            # print msg: Minimum number of calibrations found
            if log:
                WLOG(params, '', textentry('40-503-00049'))
        else:
            bad_calib_nights.append(uobsdir)
    # -------------------------------------------------------------------------
    return calib_count, calib_times, bad_calib_nights


SciTelluCheckReturn = Tuple[Dict[str, dict], Dict[str, dict],
                            Dict[str, np.ndarray], List[str]]


def sci_tellu_check(params: ParamDict, recipe: DrsRecipe, tstars: List[str],
                    ostars: List[str], uobsdirs: np.ndarray,
                    findexdbm: FileIndexDatabase, log: bool = True
                    ) -> SciTelluCheckReturn:
    """
    Check for science/telluric (hotstar) files

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: Recipe, the recipe instance that called this function
    :param tstars: list of hot (telluric) stars
    :param ostars: list of science targets
    :param uobsdirs: numpy array of strings, the unique observation directories
    :param findexdbm: FileIndexDatabase, the file index database
    :param log: bool, if True prints messages to screen (default True)

    :return: tuple, 1. the science file count for each obsdir
                    2. the telluric (hotstar) file count for each obsdir
                    2. the science file times for each obsdir
                    3. a list of engineering nights
    """
    # store hot stars  (for each observation directory)
    tellu_count = dict()
    # store science targets (for each observation directory)
    science_count = dict()
    # store a list of possible bad nights
    engineering_nights = []
    sci_times = dict()
    # get the recipe module for this instrument
    recipemodule = recipe.recipemod.get()
    filemodule = recipe.filemod.get()
    # get the generic raw file type
    generic_raw_file = filemodule.raw_file
    # -------------------------------------------------------------------------
    # get a list of telluric files and science files
    # -------------------------------------------------------------------------
    # print msg: Analysing telluric and science raw files on disk
    if log:
        WLOG(params, 'info', params['DRS_HEADER'])
        WLOG(params, 'info', textentry('40-503-00050'))
        WLOG(params, 'info', params['DRS_HEADER'])
    # get telluric raw files
    tout = get_raw_seq_files(params, recipemodule, tstars, ostars,
                             sequence='tellu_seq')
    tellu_files, tellu_recipes, tellu_args = tout
    # get science raw files
    sout = get_raw_seq_files(params, recipemodule, tstars, ostars,
                             sequence='science_seq')
    sci_files, sci_recipes, sci_args = sout
    # -------------------------------------------------------------------------
    # if we are not using a telluric run don't include it
    rm_list = []
    for srecipe in tellu_files:
        # get run code
        runcode = 'RUN_{0}'.format(srecipe)
        # do not check recipes that do not have RUN_XXXX = True
        if runcode in params:
            if not params[runcode]:
                rm_list.append(srecipe)
    # remove bad recipes from tellu_files
    for srecipe in rm_list:
        del tellu_files[srecipe]
    # report if None found
    if len(tellu_files) == 0 and log:
        # log a warning if None found:
        #   No telluric RUN instances in run file "{0}". Skipping
        wargs = [params['INPUTS']['RUNFILE']]
        WLOG(params, 'warning', textentry('10-503-00026', args=wargs),
             sublevel=2)
    # -------------------------------------------------------------------------
    # if we are not using a science run don't include it
    rm_list = []
    for srecipe in sci_files:
        # get run code
        runcode = 'RUN_{0}'.format(srecipe)
        # do not check recipes that do not have RUN_XXXX = True
        if runcode in params:
            if not params[runcode]:
                rm_list.append(srecipe)
    # remove bad recipes from tellu_files
    for srecipe in rm_list:
        del sci_files[srecipe]
    if len(sci_files) == 0 and log:
        # log a warning if None found:
        #   No science RUN instances in run file "{0}". Skipping
        wargs = [params['INPUTS']['RUNFILE']]
        WLOG(params, 'warning', textentry('10-503-00027', args=wargs),
             sublevel=2)
    # -------------------------------------------------------------------------
    # combine file types (we don't care about recipes here)
    tfiles = _flatten_raw_seq_filelist(tellu_files, generic_raw_file)
    sfiles = _flatten_raw_seq_filelist(sci_files, generic_raw_file)
    # loop around each observation directory and check for all
    #     telluric/science files
    for uobsdir in uobsdirs:
        uobsdir = str(uobsdir)
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
        elif log:
            margs = [uobsdir]
            WLOG(params, 'info', textentry('40-503-00048', args=margs),
                 colour='magenta')
        # ---------------------------------------------------------------------
        # get all raw files for this night
        rtable = findexdbm.get_entries('KW_OBJNAME, KW_OUTPUT,KW_MID_OBS_TIME',
                                       obs_dir=uobsdir, block_kind='raw')
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
                # print msg: Found {0} {1} telluic files'
                if log:
                    margs = [tcount, drsfile]
                    WLOG(params, '', textentry('40-503-00051', args=margs))
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
                # print msg: Found {0} {1} science files
                margs = [scount, drsfile]
                WLOG(params, '', textentry('40-503-00052', args=margs))
                # we are not missing all science files
                s_missing = False

        if t_missing and log:
            # print msg: No telluric files found for observation directory {0}
            WLOG(params, 'warning', textentry('10-503-00028', args=[uobsdir]),
                 sublevel=2)
        if s_missing and log:
            # print msg: No science files found for observation directory {0}
            WLOG(params, 'warning', textentry('10-503-00029', args=[uobsdir]),
                 sublevel=2)
        # deal with assumed engineering observation directories
        #     (no science or tellu)
        if t_missing and s_missing:
            engineering_nights.append(uobsdir)
            sci_times[uobsdir] = np.array([])
        else:
            sci_times[uobsdir] = np.array(rtable['KW_MID_OBS_TIME'])

    return science_count, tellu_count, sci_times, engineering_nights


def file_check(params: ParamDict, recipe: DrsRecipe,
               findexdbm: Optional[FileIndexDatabase] = None):
    """
    Check the current index database for possible problems in the raw file set

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe instance, the recipe that called this function
    :param findexdbm: IndexDatabase instance or None (will load index database)

    :return: None, prints to screen
    """
    # deal with not having index database
    if findexdbm is None:
        # construct the index database instance
        findexdbm = FileIndexDatabase(params)
        findexdbm.load_db()
    # -------------------------------------------------------------------------
    # get odometer reject list (if required)
    # -------------------------------------------------------------------------
    # get whether the user wants to use reject list
    _use_odo_reject = params['USE_REJECTLIST']
    # get the odometer reject list
    odo_reject_list = []
    if not drs_text.null_text(_use_odo_reject, ['', 'None']):
        if drs_text.true_text(_use_odo_reject):
            odo_reject_list = prep.get_file_reject_list(params)
    # -------------------------------------------------------------------------
    # get the conditions based on params
    # -------------------------------------------------------------------------
    condition, _ = drs_processing.gen_global_condition(params, findexdbm,
                                                       odo_reject_list)
    # get unique observations directories
    uobsdirs = findexdbm.get_unique('OBS_DIR', condition=condition)
    # sort uobsdirs alphabetically
    uobsdirs = np.sort(uobsdirs)
    # -------------------------------------------------------------------------
    # get telluric stars and non-telluric stars
    # -------------------------------------------------------------------------
    # get a list of all objects from the file index database
    all_objects = drs_processing.get_uobjs_from_findex(params, findexdbm)
    # get all telluric stars
    tstars = telluric.get_tellu_include_list(params, all_objects=all_objects)
    # get all other stars
    ostars = drs_processing.get_non_telluric_stars(params, all_objects, tstars)
    # -------------------------------------------------------------------------
    # get a list of telluric files and science files
    # -------------------------------------------------------------------------
    sout = sci_tellu_check(params, recipe, tstars, ostars, uobsdirs, findexdbm)
    science_count, tellu_count, sci_times, engineering_nights = sout
    # -------------------------------------------------------------------------
    # get a list of calibration files
    # -------------------------------------------------------------------------
    cout = calib_check(params, recipe, tstars, ostars, uobsdirs,
                       condition, findexdbm)
    calib_count, calib_times, bad_calib_nights = cout
    # -------------------------------------------------------------------------
    # Work out possible bad obs directories
    # -------------------------------------------------------------------------
    # calculate mean obs directory times
    all_obs_dir = []
    mean_times = []
    for obs_dir in calib_times:
        if len(calib_times[obs_dir]) == 0:
            # need to work out a time from science files
            if len(sci_times[obs_dir]) > 0:
                mean_times.append(mp.nanmean(sci_times[obs_dir]))
            else:
                mean_times.append(np.nan)
        else:
            mean_times.append(mp.nanmean(calib_times[obs_dir]))
        all_obs_dir.append(obs_dir)
    # convert to numpy arrays
    all_obs_dir, mean_times = np.array(all_obs_dir), np.array(mean_times)
    bad_calib_nights = np.array(bad_calib_nights)
    # storage for bad nights
    bad_nights = []
    # loop around flagged bad calibration files
    for obs_dir in bad_calib_nights:
        # skip engineering nights
        if obs_dir in engineering_nights:
            continue
        # get the mean time for this observation directory
        mean_time_it = mean_times[obs_dir == all_obs_dir][0]
        # mask out other bad nights (shouldn't include these)
        obs_mask = ~(np.in1d(all_obs_dir, bad_calib_nights))
        # find all other obs dirs with in MAX_CALIB_DTIME of this night
        diff = abs(mean_times[obs_mask] - mean_time_it)[1:]
        # check whether there is another night within given time frame
        #   give +/- 0.5 days due to start and end of calibrations
        if np.sum(diff < params['MAX_CALIB_DTIME'] + 0.5) == 0:
            bad_nights.append(obs_dir)
    # -------------------------------------------------------------------------
    # print msg: file check summary
    WLOG(params, 'info', params['DRS_HEADER'])
    WLOG(params, 'info', textentry('40-503-00053'))
    WLOG(params, 'info', params['DRS_HEADER'])
    # -------------------------------------------------------------------------
    # finally print a list of possible bad nights
    if len(bad_nights) > 0:
        # print msg: The following observation directories will causes errors:
        WLOG(params, 'warning', textentry('10-503-00030'), colour='red',
             sublevel=8)
        # display bad directories
        WLOG(params, 'warning', '{0}'.format(', '.join(bad_nights)),
             colour='red', sublevel=8)
    if len(engineering_nights) > 0:
        # print msg: The following observation directories will be skipped as
        #            engineering directories
        WLOG(params, 'warning', textentry('10-503-00031'), sublevel=3)
        # display engineering directories
        WLOG(params, 'warning', '{0}'.format(', '.join(engineering_nights)),
             sublevel=3)

    if len(bad_nights) == 0 and len(engineering_nights) == 0:
        WLOG(params, '', textentry('40-503-00054'))
    else:
        WLOG(params, '', textentry('40-503-00054'))


RawSeqReturn = Tuple[Dict[str, Dict[str, List[DrsFitsFile]]],
                     Dict[str, DrsRecipe], Dict[str, Dict[str, DrsArgument]]]


def get_raw_seq_files(params: ParamDict, recipemod,
                      tstars: List[str], ostars: List[str],
                      sequence: str, log: bool = True) -> RawSeqReturn:
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
    :param log: bool, if True prints messages to screen (default True)

    :return: dictionary
    """
    # print progress: Getting file types for sequence={0}
    if log:
        WLOG(params, '', textentry('40-503-00056', args=[sequence]))
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
        return dict(), dict(), dict()
    # generate sequence
    seq.process_adds(params, tstars=list(tstars), ostars=list(ostars),
                     template_stars=template_object_list, logmsg=log)
    # storage of calib files
    seq_files = dict()
    seq_instances = dict()
    seq_args = dict()
    # get the sequence recipe list
    srecipelist = seq.sequence
    # loop around recipes
    for srecipe in srecipelist:
        # get the short name for this recipe
        srecipe_name = srecipe.shortname
        # get the standard input files for all arguments
        infiles, inargs = _get_infiles(srecipe)
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
        seq_instances[srecipe_name] = srecipe
        seq_args[srecipe_name] = inargs
    # return calibration files
    return seq_files, seq_instances, seq_args


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


GetInFileReturn = Tuple[Dict[str, List[DrsFitsFile]], Dict[str, DrsArgument]]


def _get_infiles(srecipe: DrsRecipe) -> GetInFileReturn:
    """
    Get all files (grouped by the argument they are required for)

    :param srecipe:
    :return:
    """
    # store input files
    infiles = dict()
    inargs = dict()
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
            inargs[argname] = srecipe.args[argname]
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
            inargs[kwargname] = srecipe.kwargs[kwargname]
    # return the input files
    return infiles, inargs


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
def obj_check(params: ParamDict, findexdbm: Optional[FileIndexDatabase] = None,
              log: bool = True) -> Table:
    """
    Check the index database for unique objects and display which of these
    are not in the object database currently (and not in the rejection list)

    :param params: ParamDict, the parameter dictionary of constants
    :param findexdbm: IndexDatabase instance or None (will load index database)
    :param log: bool, if True prints messages to screen (default True)

    :return: None, prints to screen
    """
    # print progress
    if log:
        WLOG(params, 'info', params['DRS_HEADER'])
        WLOG(params, 'info', 'Checking current set of object names')
        WLOG(params, 'info', params['DRS_HEADER'])
    # ---------------------------------------------------------------------
    # get psuedo constants
    pconst = constants.pload()
    # deal with not having index database
    if findexdbm is None:
        # construct the index database instance
        findexdbm = FileIndexDatabase(params)
        findexdbm.load_db()
    # ---------------------------------------------------------------------
    # Update the object database (recommended only for full reprocessing)
    # check that we have entries in the object database
    manage_databases.object_db_populated(params)
    # update the database if required
    if params['UPDATE_OBJ_DATABASE']:
        # log progress
        if log:
            WLOG(params, '', textentry('40-503-00039'))
        # update database
        manage_databases.update_object_database(params, log=False)
    # ---------------------------------------------------------------------
    # load the object database after updating
    objdbm = ObjectDatabase(params)
    objdbm.load_db()
    # ---------------------------------------------------------------------
    # Update the reject database (recommended only for full reprocessing)
    # check that we have entries in the object database
    has_entries = manage_databases.reject_db_populated(params)
    # update the database if required
    if params['UPDATE_REJECT_DATABASE'] or not has_entries:
        manage_databases.update_reject_database(params, log=log)
    # ---------------------------------------------------------------------
    # only find science / hot star objects
    sci_dprtypes = params['PP_OBJ_DPRTYPES']
    subconditions = []
    for sci_dprtype in sci_dprtypes:
        subconditions.append(f'KW_DPRTYPE="{sci_dprtype}"')
    # construct full condition
    condition = 'BLOCK_KIND="raw" AND ({0})'.format(' OR '.join(subconditions))
    # get list of unique objects from index database
    uobjnames = findexdbm.get_unique('KW_OBJNAME', condition=condition)
    # ---------------------------------------------------------------------
    # print progress: Preparing list of unique objects from file index database
    if log:
        margs = [len(uobjnames)]
        WLOG(params, '', textentry('40-503-00057', args=margs))
    # get the object rejection list
    reject_list = prep.get_obj_reject_list(params)
    # store list of objects not found in the database currently
    unfound_objects = []
    # loop around index database unique object names and check for them
    for uobjname in uobjnames:
        # find correct name in the database (via objname or aliases)
        correct_objname, found = objdbm.find_objname(pconst, uobjname)
        # ignore objects in the reject list
        if correct_objname in reject_list:
            continue

        # if object was not found add to list
        if not found:
            unfound_objects.append(correct_objname)
    # ---------------------------------------------------------------------
    # get original names for objects
    orig_names = []
    last_runid = []
    last_pi_name = []
    last_obs_date = []
    # Print progress: Finding all original names for each unfound object
    if log:
        WLOG(params, 'info', textentry('40-503-00058'))
    # loop around
    for unfound_object in tqdm(unfound_objects):
        # condition for this target
        condition = 'KW_OBJNAME="{0}" AND BLOCK_KIND="raw"'
        condition = condition.format(unfound_object)
        # get all original names for this target
        orig_name = findexdbm.get_unique('KW_OBJECTNAME', condition=condition)
        # append to list
        orig_names.append(list(orig_name))
        # -----------------------------------------------------------------
        # get the runid, piname and obs date for the most recent raw file with
        #   this name
        # define the columns to get from the file index database
        columns = 'KW_RUN_ID,KW_PI_NAME,OBS_DIR'
        # get the most recent raw file with this object name
        last_obj = findexdbm.database.get(columns, condition=condition,
                                          sort_by='KW_MID_OBS_TIME',
                                          sort_descending=True,
                                          max_rows=1)
        # push into the last_runid, last_pi_name and last_obs_date lists
        last_runid.append(last_obj[0][0])
        last_pi_name.append(last_obj[0][1])
        last_obs_date.append(last_obj[0][2])

    # ---------------------------------------------------------------------
    # print any remaining objects
    if log:
        # print msg: Objects that will use the header for astrometrics are:
        WLOG(params, '', textentry('40-503-00059'), colour='magenta',
             wrap=False)
        # deal with having no unfound objects
        if len(unfound_objects) == 0:
            # print that all objects were found
            # print msg: All objects found (or in ignore list)!
            WLOG(params, '', textentry('40-503-00060'))
        # else we print the unfound objects
        else:
            # loop around objects and put on a new line
            for it in range(len(unfound_objects)):
                # print the object
                msg = ('\t{0}\t{1:30s}\t(APERO: {2})'
                       '\tLAST[{3}, {4}, {5}]')
                margs = [it + 1, ' or '.join(orig_names[it]),
                         unfound_objects[it],
                         last_runid[it], last_pi_name[it],
                         last_obs_date[it]]
                WLOG(params, 'warning', msg.format(*margs), sublevel=8)
            # print a note that some objects are in ignore list
            if len(reject_list) > 0:
                # print msg: Note {0} objects are in the ignore list/ignore
                # aliases
                margs = [len(reject_list)]
                WLOG(params, 'info', textentry('40-503-00061', args=margs))

    # create a table of unfound objects
    unfound_table = Table()
    unfound_table['Original Names'] = orig_names
    unfound_table['Apero Name'] = unfound_objects
    unfound_table['Last Run ID'] = last_runid
    unfound_table['Last PI Name'] = last_pi_name
    unfound_table['Last Obs Date'] = last_obs_date
    # return the unfound table
    return unfound_table


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
