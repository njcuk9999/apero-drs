#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-21 at 12:28

@author: cook
"""

import os
import shutil
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_astrometrics
from apero.core import drs_file
from aperocore.core import drs_log
from aperocore.core import drs_text
from apero.utils import drs_recipe
from apero.io import drs_fits
from apero.tools.recipes.bin import apero_get
from apero.instruments import select
from apero.base import base as apero_base
from apero.science.calib import wave
from apero.science.preprocessing import gen_pp


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.rv.gen_lbl.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
# Get Input File class
DrsInputFile = drs_file.DrsInputFile
# Get the text types
textentry = drs_lang.textentry
# LBL directories
LBL_DIRS = ['calib', 'lblrdb', 'lblreftable', 'log', 'masks', 'models',
            'plots', 'science', 'templates']
# Get tqdm from base
TQDM = base.tqdm_module()


# =============================================================================
# Define functions
# =============================================================================
def do_skip(params: ParamDict, recipe_test: str) -> bool:
    """
    Determine whether to skip this recipe

    :param params: ParamDict, the parameter dictionary containing constants
    :param recipe_test: str, the recipe name to test for skipping

    :return: bool, whether to skip this recipe
    """
    # get skip done from parameters
    if recipe_test in params['OBJ.LBL.SKIP_DONE']:
        skip_done = True
    else:
        skip_done = False
    # overwrite skip done if given in inputs
    if 'INPUTS' in params:
        return params['INPUTS'].get('SKIP_DONE', skip_done)
    else:
        return skip_done


def run_mkdirs(params: ParamDict):
    # get the lbl path
    lbl_in_path = params['PATH.LBL']
    # loop around directories
    for directory in LBL_DIRS:
        # construct path
        path = os.path.join(lbl_in_path, directory)
        # check if path exists and make directory if not
        if not os.path.exists(path):
            os.makedirs(path)


def run_apero_get(params: ParamDict):
    """
    Run the apero get on all profiles

    :param params: ParamDict, the parameter dictionary containing constants

    :returns: None, copies or symlinks files to params['PATH.LBL']
    """
    # pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # get the lbl path
    lbl_in_path = params['PATH.LBL']
    # APERO file definition out types
    lbl_outtypes = params['OBJ.LBL.FILE_DEFS']
    # APERO DPRTYPE for lbl science files
    lbl_dprtypes = params['OBJ.LBL.DPRTYPES']
    # APERO DPRTYPE for lbl template files
    lbl_template_outtypes = params['OBJ.LBL.TEMPLATE_FILE_DEFS']
    # APERO DPRTYPE for lbl simultaneous FP files
    simfp_dprtypes = params['OBJ.LBL.SIM_FP_DPRTYPES']
    # whether we are copying with symlinks
    lbl_symlinks = params['OBJ.LBL.SYMLINKS']
    # whether we are in test mode
    testmode = params['INPUTS']['TEST']
    # do not use since
    since = None
    # get the fiber types
    lbl_scifibers, lbl_calfibers = params['CAL.FIBER.CCF']
    # get the output path
    outpath_objects = os.path.join(lbl_in_path, 'science')
    outpath_templates = os.path.join(lbl_in_path, 'templates')
    outpath_calib = os.path.join(lbl_in_path, 'calib')
    outpath_fp = os.path.join(lbl_in_path, 'science/FP')
    # -------------------------------------------------------------------------
    # deal with object names
    # -------------------------------------------------------------------------
    objnames = 'None'
    if 'OBJNAMES' in params['INPUTS']:
        if not drs_text.null_text(params['INPUTS'], ['None', '', 'Null']):
            objnames = params['INPUTS']['OBJNAMES'].split(',')
    # ----------------------------------------------------------
    # check directories exist - try to make them if they don't
    # ----------------------------------------------------------
    directories = [outpath_templates, outpath_calib, outpath_objects]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
    # --------------------------------------------------------------
    # Copy to LBL directory
    # --------------------------------------------------------------
    # run apero get for objects for lbl
    apero_get.main(objnames=objnames,
                   dbkind='tellu', keynames='TELLU_OBJ',
                   outpath=outpath_objects, fibers=lbl_scifibers,
                   symlinks=lbl_symlinks,
                   test=testmode, since=since)
    # TODO: Put this back in once using better templates in APERO
    # run apero get for templates (no DPRTYPE as they could be different)
    # apero_get.main(objnames='*', outtypes=lbl_template_outtypes,
    #                outpath=outpath_templates, fibers=lbl_scifibers,
    #                symlinks=False, nosubdir=True,
    #                test=testmode, since=since)
    # run apero get for simultaneous FP
    apero_get.main(objnames=objnames, dprtypes=simfp_dprtypes,
                   block_kind='red',
                   outtypes='EXT_E2DS_FF',
                   nosubdir=True,
                   outpath=outpath_fp, fibers=lbl_calfibers,
                   symlinks=False,
                   test=testmode, since=since)
    # run apero get for extracted FP_FP
    # TODO: This is a problem if "red" is removed
    apero_get.main(objnames='None', dprtypes='FP_FP',
                   block_kind='red',
                   outtypes='EXT_E2DS_FF',
                   outpath=outpath_fp, fibers=lbl_calfibers,
                   symlinks=lbl_symlinks, nosubdir=True,
                   test=testmode, since=since)
    # run apero get for calibs (wave + blaze) science fiber
    apero_get.main(dbkind='calib',
                   keynames='BLAZE,WAVE,WAVESOL_REF,WAVESOL_DEFAULT',
                   outpath=outpath_calib, fibers=lbl_scifibers,
                   symlinks=lbl_symlinks, nosubdir=True,
                   test=testmode, since=since)
    # run apero get for calibs (wave + blaze) science fiber
    apero_get.main(dbkind='calib',
                   keynames='BLAZE,WAVE,WAVESOL_REF,WAVESOL_DEFAULT',
                   outpath=outpath_calib, fibers=lbl_calfibers,
                   symlinks=lbl_symlinks, nosubdir=True,
                   test=testmode, since=since)
    # get the static wave solutions
    apero_wave_static(params, [lbl_scifibers] + [lbl_calfibers],
                      outpath_calib, symlinks=lbl_symlinks)


def apero_wave_static(params: ParamDict, fibers: List[str],
                      outpath: str, symlinks: bool = False):
    """
    Copy the APERO static wave files to the LBL directory

    :param params: ParamDict, the parameter dictionary containing constants
    :param fibers: list, the fibers to copy static files for
    :param outpath: str, the output path to copy files to

    :return: None, copies files to outpath
    """
    # get the static wave solutions
    for fiber in fibers:
        # get static wavelength filename
        filename = wave.get_static_wavesol(params, fiber)
        # print progress
        msg = 'Copying static wave solution for fiber {0}: {1}'
        margs = [fiber, filename]
        WLOG(params, '', msg.format(*margs))
        # deal with no file found
        if not os.path.exists(filename):
            emsg = 'Expected static wave solution does not exist: {0}'
            eargs = [filename]
            raise AperoCodedException(params, None, message=emsg.format(eargs),
                                      targs=eargs)
        # manually copy or symlink to outpath directory
        destfile = os.path.join(outpath, os.path.basename(filename))
        if not os.path.exists(destfile):
            if symlinks:
                os.symlink(filename, destfile)
            else:
                shutil.copy2(filename, destfile)


def find_friend(params: ParamDict, shortname: str, objname: str) -> str:
    """
    Find the friend for this object (currently defined by closest teff to
    a list of friends teffs)

    :param params: ParamDict, parameter dictionary of constants
    :param objname: str, the object name to find a friend of

    :return: str, the friend name
    """
    # TODO: v0.8 change this to use the astrometric database
    #       with a FRIEND column
    # get dictionary of friends (key = objname, value = friend teff)
    friends = params['OBJ.LBL.FRIENDS']
    friend_names = np.array(list(friends.keys()))
    friend_teffs = np.array(list(friends.values()))
    # get the teff of this object
    teff = find_teff(params, shortname, objname)
    # find the closest friend
    closest = np.abs(friend_teffs - teff).argmin()
    # return the friend name
    return friend_names[closest]


def find_teff(params: ParamDict, shortname: str, objname: str) -> float:
    """
    Get the Teff for this object from the astrometric database

    :param params: ParamDict, parameter dictionary of constants
    :param objname: str, the object name to find the teff of

    :return: float, the teff of this object in K
    """
    # get the astrometric database (yaml-backed)
    astromdbm = drs_astrometrics.AstrometricDatabase(params, shortname)
    # resolve the entry by any name and pull TEFF from the yaml schema
    entry = astromdbm.get_entry(objname)
    # deal with no etff
    if entry is None:
        teff = None
    else:
        # TEFF lives at entry['TEFF']['value'] (nested) in the yaml schema
        teff = drs_astrometrics.LEGACY_COL_MAP['TEFF'](entry)
    # try to convert to a float (may be None)
    # noinspection PyBroadException
    try:
        teff = float(teff)
    except Exception as _:
        # TODO: Add to language database
        emsg = 'No Teff found for {0}'.format(objname)
        raise AperoCodedException(params, message=emsg)
    # return the teff
    return teff


def add_output(params: ParamDict, recipe: DrsRecipe,
               header_fits_file: Union[str, None],
               drsfile: DrsInputFile,
               inprefix: Optional[str] = None,
               insuffix: Optional[str] = None,
               objname: Optional[str] = None,
               tempname: Optional[str] = None):
    """
    Add an output file to the file index database

    :param params: ParamDict, paremeter dictionary of constants
    :param recipe: DrsRecipe, the recipe instance that called this function
    :param header_fits_file: str or None, the header fits file to use
    :param drsfile: DrsInputFile, the input file definition
    :param inprefix: str or None, the file prefix identifier
                     i.e. {identifier}_pp_e2dsff_tcorr_AB_
    :param insuffix: str or None, the file suffix to add (optional)
    :param objname: str, the object name
    :param tempname: str, the template name
    :return:
    """
    # get file index database
    findexdbm = drs_database.FileIndexDatabase(params, recipe.shortname)
    # deal with wrong drsfile (drsfile.outclass must have lbl_file attribute)
    if not hasattr(drsfile.outclass, 'lbl_file'):
        # TODO: Add to language database
        emsg = 'File definition {0} must have an lbl outclass (lbl_ofile)'
        eargs = [drsfile.name]
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)
    # get kwargs for lbl_file
    kwargs = dict()
    kwargs['objname'] = objname
    kwargs['tempname'] = tempname
    kwargs['inprefix'] = inprefix
    kwargs['insuffix'] = insuffix
    # construct the base filename
    filename = drsfile.outclass.lbl_file(params, drsfile, **kwargs)
    # if file does not exist do not add to the file index database
    if not os.path.exists(filename) and drsfile.required:
        # TODO: Add to language database
        emsg = 'Expected {0} does not exist: {1}'
        eargs = [drsfile.name, filename]
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)
    elif not os.path.exists(filename):
        # TODO: Add to language database
        wmsg = 'Skipping {0}, does not exist and not required: {1}'
        wargs = [drsfile.name, filename]
        WLOG(params, 'warning', wmsg.format(*wargs), sublevel=1)
        return
    # convert absolute path to a drs path
    basefile = drs_file.DrsPath(params, abspath=filename)
    # print progres
    # TODO: Add to language database
    msg = 'Adding {0} to file index database: {1}'
    margs = [drsfile.name, filename]
    WLOG(params, '', msg.format(*margs))
    # construct hkeys
    hkeys = fake_hkeys(params, filename, header_fits_file,
                       drsfile, objname, tempname)
    # add file to index database
    findexdbm.add_entry(basefile, 'lbl', recipe.name,
                        runstring=recipe.runstring, hkeys=hkeys)
    # update the files on disk with the hkeys
    # (this will add the hkeys to the header if they don't exist and
    #  update the values if they do)
    drs_fits.update_fits(params, filename, hkeys)



def lbl_ref_qc(params: ParamDict) -> Tuple[List[list], int]:
    """
    The lbl ref qc

    :param params: ParamDict, parameter dictionary of constants

    :return: tuple, 1. the qc lists, 2. if passed 1 else 0
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # no quality control currently
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def lbl_mask_qc(params: ParamDict) -> Tuple[List[list], int]:
    """
    The lbl mask qc

    :param params: ParamDict, parameter dictionary of constants

    :return: tuple, 1. the qc lists, 2. if passed 1 else 0
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # no quality control currently
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def lbl_compute_qc(params: ParamDict) -> Tuple[List[list], int]:
    """
    The lbl compute qc

    :param params: ParamDict, parameter dictionary of constants

    :return: tuple, 1. the qc lists, 2. if passed 1 else 0
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # no quality control currently
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def lbl_compile_qc(params: ParamDict) -> Tuple[List[list], int]:
    """
    The lbl compile qc

    :param params: ParamDict, parameter dictionary of constants

    :return: tuple, 1. the qc lists, 2. if passed 1 else 0
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # no quality control currently
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def fake_hkeys(params: ParamDict, filename: str,
               header_fits_file: Union[str, None],
               drsfile: DrsInputFile,
               objname: Optional[str] = None,
               tempname: Optional[str] = None) -> Dict[str, Any]:
    # set function name
    func_name = __NAME__ + '.fake_hkeys()'
    # get rkeys from pseudo constants
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    iheader_cols = pconst.FILEINDEX_HEADER_COLS()
    rkeys = list(iheader_cols.names)
    # key to add to hkeys (if required by instrument)
    pkeys = dict()
    # if we are dealing with a fits file can get keys from the header
    if filename.endswith('.fits') and header_fits_file is None:
        header_fits_file = filename
    # deal with header_fits_file being None
    if header_fits_file is None:
        # TODO: Add to language database
        emsg = ('Must provide a header_fits_file argument for non-fits file.'
                '\n\tfilename = {0}\n\tfunction = {1}')
        eargs = [filename, func_name]
        raise AperoCodedException(params, message=emsg.format(*eargs),
                                  targs=eargs)
    # get header from selected
    hdr = drs_fits.read_header(params, header_fits_file)
    for key in rkeys:
        # deal with drs keys
        if key in params:
            drskey = params[key][0]
        else:
            drskey = str(key)
        # get key from header
        if drskey in list(hdr.keys()):
            pkeys[key] = hdr[drskey]
    # overwrite objectnames (if objname and tempname are valid)
    if objname is not None and tempname is not None and len(tempname) > 0:
        obj_temp = f'LBL[{objname}_{tempname}]'
        pkeys['KW_OBJECTNAME'] = obj_temp
        pkeys['KW_OBJECTNAME2'] = obj_temp
    else:
        obj_temp = f'LBL[{objname}]'
        pkeys['KW_OBJECTNAME'] = obj_temp
        pkeys['KW_OBJECTNAME2'] = obj_temp

    # need to add KW_DPRTYPE, KW_PI_NAME, KW_RUN_ID, KW_FIBER

    # get apero release date
    areldate = gen_pp.get_areldate(params, hdr, release_type='lbl')
    pkeys['KW_ARELDATE'] = areldate

    # overwrite keys
    pkeys['KW_OBJNAME'] = objname
    pkeys['KW_INSTRUMENT'] = params['OBS.INSTRUMENT']
    pkeys['KW_OUTPUT'] = drsfile.name
    pkeys['KW_PID'] = params['PID']
    pkeys['KW_DRS_DATE_NOW'] = params['DATE_NOW']
    # return pkeys
    return pkeys


# TODO: When dtemp is automatically in LBL this will not need to check
#       files on disk (that currently need to be copied manually)
def dtemp(params: ParamDict) -> Union[Dict[str, str], None]:
    """
    Add the DTEMP RESPROJ_TABLES

    :param params: ParamDict, parameter dictionary of constants

    :return:
    """
    # get the dictionary of dtemp files
    dtemp_keys = params['OBJ.LBL.DTEMP']
    # get the model directory
    models_dir = os.path.join(params['PATH.LBL'], 'models')

    # deal with models directory not existing
    if not os.path.exists(models_dir):
        WLOG(params, 'warning', 'No DTEMP files found. Skipping.', sublevel=1)
        return None
    # storage for output files
    valid_dtemp_files = dict()
    # get files in models directory
    model_dir_files = os.listdir(models_dir)
    # loop around files
    for dtemp_key in dtemp_keys:
        if dtemp_keys[dtemp_key] in model_dir_files:
            valid_dtemp_files[dtemp_key] = dtemp_keys[dtemp_key]
    # deal with no files found
    if len(valid_dtemp_files) == 0:
        WLOG(params, 'warning', 'No DTEMP files found. Skipping.', sublevel=1)
        return None
    else:
        msg = '{0} DTEMP files found.'
        margs = [len(valid_dtemp_files)]
        WLOG(params, 'info', msg.format(*margs))
        return valid_dtemp_files


def add_log(params: ParamDict, lblinstance: Any):
    """
    Add the LBL log (from the lbl instance) to the apero logs
    this is a fudge as all time stamps will be "now" not when they were run

    :param params: ParamDict, parameter dictionary of constants
    :param lblinstance: return on lbl_xxx.main() call

    :return: None, just logs to parent log file
    """
    # TODO: This may be too slow if LBL log is large
    WLOG(params, 'info', 'Adding LBL log to apero log')
    for msg in TQDM(lblinstance.get('logmsg', [])):
        WLOG(params, '', msg, logonly=True)


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================