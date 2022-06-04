#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-11-02 10:09
@author: ncook
Version 0.0.1
"""
from astropy.table import Table
import numpy as np
import os
import shutil
import time
from typing import Dict, List, Optional, Tuple

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero.core.core import drs_database
from apero.core.utils import drs_startup
from apero.core.utils import drs_recipe
from apero.tools.recipes.bin import apero_processing
from apero.tools.module.processing import drs_processing

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.processing.drs_trigger.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get the parameter dictionary
ParamDict = constants.ParamDict
# get the recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get the text types
textentry = lang.textentry
# -----------------------------------------------------------------------------
# trigger table
TRIGGER_TABLE = 'trigger_table.fits'


# =============================================================================
# Define functions
# =============================================================================
def raw_files(user_indir: str, user_outdir: str, do_copy: bool = False,
              do_symlink: bool = False,
              exclude_obs_dir: Optional[List[str]] = None,
              log: bool = True, replace: bool = True):
    """
    Copy (or sym-link) the whole raw directory

    :param user_indir: str, the full, original raw directory (absolute path)
    :param user_outdir: str, proposed out raw directory (absolute path)
    :param do_copy: bool, hard copies files
    :param do_symlink: bool, symlinks files (overrides do_copy if True)
    :return:
    """

    if exclude_obs_dir is None:
        exclude_obs_dir = []

    # get raw directory
    raw_path = user_indir
    # make sure user_outdir exists
    if not os.path.exists(user_outdir):
        os.makedirs(user_outdir)
    # walk through path
    for root, dirs, files in os.walk(raw_path):
        # get uncommon path
        upath = drs_misc.get_uncommon_path(raw_path, root)
        # remove excluded directories
        if upath in exclude_obs_dir:
            continue
        # make outpath
        outdir = os.path.join(user_outdir, upath)
        # make out directory if it doesn't exist
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        # loop around files
        for filename in files:
            # only copy fits
            if not filename.endswith('.fits'):
                continue
            # construct inpath
            inpath = os.path.join(root, filename)
            # construct outpath
            outpath = os.path.join(outdir, filename)
            # copy
            if do_symlink:
                # remove outpath if it exists
                if os.path.exists(outpath):
                    if replace:
                        os.remove(outpath)
                    else:
                        continue
                # print process
                if log:
                    msg = 'Creating symlink {0}'
                    print(msg.format(outpath))
                # create symlink
                os.symlink(inpath, outpath)
            elif do_copy:
                # remove outpath if it exists
                if os.path.exists(outpath):
                    if replace:
                        os.remove(outpath)
                    else:
                        continue
                # print process
                if log:
                    msg = 'Copying file {0}'
                    print(msg.format(outpath))
                # copy file
                shutil.copy(inpath, outpath)


class Trigger:
    def __init__(self, params: ParamDict, recipe: DrsRecipe):
        # keep params
        self.params = params
        self.recipe = recipe
        # whether the trigger is active
        self.active = True
        # the exlucded directories
        self.excluded_dirs = []
        # define the time to wait to check again
        self.sleep_time = 60
        # define the path to the trigger table
        self.triggr_table = TRIGGER_TABLE
        # set the input directory (to scan)
        self.indir = params['INPUTS']['INDIR']
        # set the output path
        self.outdir = params['DRS_DATA_RAW']
        # deal with no input directory to scan
        if drs_text.null_text(self.indir, ['None', '', 'Null']):
            emsg = '--indir must be defined'
            WLOG(params, 'error', emsg)
        # define the calib and science trigger scripts
        self.calib_script = 'None'
        self.science_script = 'None'
        # start index database
        self.indexdbm = drs_database.IndexDatabase(params)
        self.indexdbm.load_db()
        # start log database
        self.logdbm = drs_database.LogDatabase(params)
        self.logdbm.load_db()
        # start object database
        self.objdbm = drs_database.ObjectDatabase(params)
        self.objdbm.load_db()

    def __call__(self):
        # ---------------------------------------------------------------------
        # step 1: sync raw directory
        #----------------------------------------------------------------------
        # print progress
        WLOG(self.params, 'info', 'Creating new symlinks')
        # update raw file symlinks
        raw_files(self.indir, self.outdir, do_copy=False, do_symlink=True,
                  exclude_obs_dir=self.excluded_dirs, replace=False, log=False)
        # ---------------------------------------------------------------------
        # step 2: update obs_dir table
        # ---------------------------------------------------------------------
        # print progress
        WLOG(self.params, 'info', 'Updating trigger status')
        # get and update status table
        table = self.status()
        # ---------------------------------------------------------------------
        # step 3: run processing
        # ---------------------------------------------------------------------
        # loop around observation directories
        for row, obs_dir in enumerate(table['OBS_DIR']):

            # deal with whether we are in calibration mode
            #    or science mode
            if not table['DONE_CALIB'][row]:
                # print progress
                msg = f'Running apero calibration processing for {obs_dir}'
                WLOG(self.params, 'info', msg)
                # run calib script
                apero_processing.main(runfile=self.calib_script,
                                      obs_dir=obs_dir, test=True)
            if not table['DONE_SCI'][row]:
                # print progress
                msg = f'Running apero science processing for {obs_dir}'
                WLOG(self.params, 'info', msg)
                # run science script
                apero_processing.main(runfile=self.science_script,
                                      obs_dir=obs_dir, test=True)
        # ---------------------------------------------------------------------
        # step 4: wait
        # ---------------------------------------------------------------------
        time.sleep(self.sleep_time)


    def status(self) -> Table:
        """
        Get and update the status of all OBS_DIRs
        """
        # step 1: load trigger status
        #       each row is an obs_dir
        #       with columns OBS_DIR, DONE_CALIB, DONE_SCI
        #       where DONE_CALIB is True if all calibrations are done
        #       TODO: how do we know?
        #       where DONE_SCI is True if all science are done
        #       TODO: how do we know?
        sobsdir, sdone_c, sdone_s = self.load_status()

        # step 2: re-index raw database
        self.params.set('UPDATE_IDATABASE_NAMES', 'raw')
        self.params.set('INCLUDE_OBS_DIRS', 'None')
        self.params.set('EXCLUDE_OBS_DIRS', 'None')
        drs_processing.update_index_db(self.params)
        # fix the header data (object name, dprtype, mjdmid and
        #     trg_type etc)
        WLOG(self.params, '', textentry('40-503-00043'))
        self.indexdbm.update_header_fix(self.recipe, objdbm=self.objdbm)
        # ----------------------------------------------------------------------
        # step 3: get list of obs_dir
        # ----------------------------------------------------------------------
        obs_dirs = self.indexdbm.database.unique('OBS_DIR',
                                                 condition='BLOCK_KIND="raw"')
        # ----------------------------------------------------------------------
        # step 4: get a list of recipes for the calib script and the sci script
        # ----------------------------------------------------------------------
        calib_recipes = get_recipes(self.params, self.calib_script,
                                    self.indexdbm)
        sci_recipes = get_recipes(self.params, self.science_script,
                                  self.indexdbm)
        # ----------------------------------------------------------------------
        # step 5: determine whether DONE_CALIB and DONE_SCI are True or False
        # ----------------------------------------------------------------------
        # loop around obs dirs
        for obs_dir in obs_dirs:
            # ------------------------------------------------------------------
            # get values of DONE_CALIB and DONE_SCI
            if obs_dir in sobsdir:
                # get location of obs_dir in lists
                pos = sobsdir.index(obs_dir)
                # get the DONE_CALIB and DONE_SCI values
                calib_done = sdone_c[pos]
                sci_done = sdone_s[pos]
            else:
                # assume calibration is done and science is not done
                calib_done = False
                sci_done = False
            # ------------------------------------------------------------------
            # if DONE_CALIB and DONE_SCI skip
            # ------------------------------------------------------------------
            if calib_done and sci_done:
                continue
            # ------------------------------------------------------------------
            # deal with no recipes for this night
            # ------------------------------------------------------------------
            # get database for this observation night
            condition = f'OBS_DIR="{obs_dir}"'
            shortnames = self.logdbm.get_entries('SHORTNAME',
                                                 condition=condition)
            shortnames = np.array(shortnames)
            # deal with no entries
            if len(shortnames) == 0:
                sobsdir.append(obs_dir)
                sdone_c.append(False)
                sdone_s.append(False)
                # condition to next obs dir
                continue
            # ------------------------------------------------------------------
            # Identify whether all calibrations have been done for this night
            # ------------------------------------------------------------------
            if not calib_done:
                # assume calibration is done
                calib_done = True
                # loop aroud calib recipes
                for calib_recipe in list(calib_recipes.keys()):
                    # query log database if recipe does not have a short name
                    #  the calibrations are not done for this night
                    if calib_recipe not in shortnames:
                        calib_done = False
                        break
            # ------------------------------------------------------------------
            # Identify if all science steps have been done
            # ------------------------------------------------------------------
            # only check if calibrations steps have for all files
            if not sci_done and calib_done:
                # assume science files are done
                sci_done = True
                # index condition
                condition = 'BLOCK_KIND="raw"'
                condition += f' AND OBS_DIR="{obs_dir}'
                # get science files condition (DPRTYPE)
                subconds = []
                for dprtype in self.params.listp('PP_OBJ_DPRTYPES',dtype=str):
                    subconds.append(f'KW_DPRTYPE="{dprtype}"')
                condition += ' AND ({0})'.format(' OR '.join(subconds))
                # get all science files
                scifiles = self.indexdbm.get_entries('FILENAME', condition=condition)
                # loop around recipes
                for sname in sci_recipes:
                    # only check recipes with file arguments
                    if sci_recipes[sname].has_file_arg():
                        # we must have the same number of science files as
                        #   runs
                        if np.sum(shortnames == sname) != len(scifiles):
                            sci_done = False
                            break
            # ------------------------------------------------------------------
            # Add obs_dir to the nights
            # ------------------------------------------------------------------
            # add night to sdict
            sobsdir.append(obs_dir)
            sdone_c.append(calib_done)
            sdone_s.append(sci_done)
        # ---------------------------------------------------------------------
        # 6. convert to table for use elsewhere
        # ---------------------------------------------------------------------
        table = Table()
        table['OBS_DIR'] = sobsdir
        table['DONE_CALIB'] = sdone_c
        table['DONE_SCI'] = sdone_s
        # ---------------------------------------------------------------------
        # return the updated table
        return table


    def load_status(self) -> Tuple[List[str], List[bool], List[bool]]:

        sdict = dict()
        # if we have a table on disk load it here
        if os.path.exists(self.triggr_table):
            table = Table.read(self.triggr_table)
            obs_dir = list(table['OBS_DIR'])
            done_calib = list(np.array(table['DONE_CALIB'], dtype=bool))
            done_sci = list(np.array(table['DONE_SCI'], dtype=bool))
        # else generate a new table
        else:
            obs_dir = []
            done_calib = []
            done_sci = []
        # return the table
        return obs_dir, done_calib, done_sci


def get_recipes(params: ParamDict, runfile: str,
                indexdbm: drs_database.IndexDatabase) -> Dict[str, DrsRecipe]:
    """
    Take a runfile and get all recipes that should be run with it

    :param params: Paramdict, the parameter dictionary of constants
    :param runfile: str, the runfile name
    :param indexdbm: index database manager class

    :returns: dictionary, where each key is a recipe short name and each value
              is a recipe class
    """
    # print progress
    msg = f'Getting recipes for {runfile}'
    WLOG(params, '', msg)
    # copy params
    iparams = params.copy()
    # deal with run file
    iparams, runtable = drs_startup.read_runfile(iparams, runfile, rkind='run',
                                                log_overwrite=True)
    # get recipe definitions module (for this instrument)
    recipemod = drs_processing._get_recipe_module(iparams, logmsg=False)
    # get all values (upper case) using map function
    rvalues = drs_processing._get_rvalues(runtable)
    # check if rvalues has a run sequence
    sequencelist = drs_processing._check_for_sequences(rvalues, recipemod)
    # --------------------------------------------------------------------------
    # store recipes in the run file
    recipe_names = dict()
    # get recipe short name from the run file and see which ones were meant
    #   to be run
    if (sequencelist is not None) and (indexdbm is not None):
        # loop around sequences
        for sequence in sequencelist:
            # generate new runs for sequence
            gargs = [iparams, sequence, indexdbm, True, False]
            srecipes = drs_processing._generate_run_from_sequence(*gargs)
            # loop around recipes in sequence
            for srecipe in srecipes:
                # get the run name (that should be in params from runfile)
                run_param = f'RUN_{srecipe.shortname}'
                # if in params and True we add this recipe to recipe_names
                if run_param in iparams and iparams[run_param]:
                    recipe_names[srecipe.shortname] = srecipe
    # now return recipe names
    return recipe_names


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Main code here
    pass

# =============================================================================
# End of code
# =============================================================================