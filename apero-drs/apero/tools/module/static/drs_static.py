#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Static calibration general functionality

Deal with:
- loading static calibration yaml file
- saving the static files
- updating the assets repository (with static calibrations)
- processing a static night (for wave calibration we require extracted HC/FP)

Created on 2025-05-26 at 09:40

@author: cook
"""
import os
import shutil
import time
from typing import Any, Dict, List, Union

import numpy as np
from astropy.table import Table

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text

from apero.base import base as apero_base
from apero.core.drs_file import DrsFitsFile
from apero.io import drs_fits
from apero.utils import drs_data
from apero.tools.module.setup import drs_assets

from apero.tools.recipes.bin import apero_processing
from apero.tools.recipes.bin import apero_remove
from apero.utils.drs_startup import find_recipe


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.static.static_detector.py'
__INSTRUMENT__ = 'None'
# Get version and author
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException

# =============================================================================
# Define functions
# =============================================================================
def load(params: ParamDict) -> Dict[str, Any]:
    """
    Load the static parameters yaml file
    """
    # get yaml file
    yamlfile = params['INPUTS']['yamlfile']
    # deal with bad yaml file
    if not os.path.exists(yamlfile):
        # try to add the default path
        default_path = os.path.join(params['PATH.OTHER'], 'static')
        # if path exists try the yaml file there
        if os.path.exists(default_path):
            yamlfile = os.path.join(default_path, os.path.basename(yamlfile))
        # if still doesn't exist raise error
        if not os.path.exists(yamlfile):
            # Raise an error that we cannot find the yaml file
            emsg = 'yamlfile not found. Tried \n\t{0}\n\t{1}'
            eargs = [params['INPUTS']['yamlfile'], yamlfile]
            raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                      targs=eargs)
    # load parameters
    sparams = base.load_yaml(yamlfile)
    # print progress
    msg = 'Loaded static parameters from {0}'
    WLOG(params, '', msg.format(yamlfile))
    # return sparams
    return sparams


def save_static_file(params: ParamDict, recipe, static_file: DrsFitsFile, 
                     desc: str,
                     data_list: List[Union[np.ndarray, Table]],
                     datatype_list: List[str] = None,
                     name_list: List[str] = None,
                     hdr_kwargs: Dict[str, Any] = None,
                     header_list: List[Dict[str, Any]] = None):
    """
    Save a static file using the standard apero file instance

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the apero recipe instance
    :param static_file: DrsInputFile, the apero static file
    :param desc: str, description from writing status
    :param data_list: list, list of data to be saved [np.ndarray and/or Table]
    :param datatype_list: list, list of datatypes to be saved "image" or "table"
    :param name_list: list, list of names to be saved (the EXTNAME in a fits
                      file)
    :param hdr_kwargs: dict, keyword arguments (in params) i.e. KW_XXX
                       to push into the headers
    :param header_list: list, list of headers to be saved to each extension

    :return None - writes to disk
    """
    # set function name
    func_name = __NAME__ + '.save_static_file()'
    # -------------------------------------------------------------------------
    # if names_list is None get from static_file definition
    if name_list is None:
        name_list = static_file.get_hdulist_names()
    # if datatype_list is None get from static_file definition
    if datatype_list is None:
        datatype_list = static_file.get_hdulist_datatypes()
    # -------------------------------------------------------------------------
    # print progress
    msg = 'Writing {0}: {1}'
    margs = [desc, static_file.filename]
    WLOG(params, '', msg.format(*margs))
    # add core values (that should be in all headers)
    static_file.add_core_hkeys(params)
    # add instrument
    static_file.add_hkey('KW_INSTRUMENT', params['OBS.INSTRUMENT'])
    # add any other header keywords
    if hdr_kwargs is not None:
        for key in hdr_kwargs:
            # get the value
            value = hdr_kwargs[key]
            # if value is a dictionary we assume it is 1D or 2D (and follows
            # the correct format)
            if isinstance(value, dict):
                # deal with keys
                for rkey in ['DIM', 'VALUES']:
                    # deal with key not in value
                    if rkey not in value:
                        emsg = ('If hdr_kwargs[{0}] is a dict it must '
                                'have a {1} key \n\t Function: {2}')
                        eargs = [key, rkey, func_name]
                        raise AperoCodedException(params, None,
                                                message=emsg.format(*eargs),
                                                targs=eargs)
                # deal with the 1D case
                if value['DIM'] == 1:
                    static_file.add_hkey_1d(key, values=value['VALUES'],
                                            dim1name=value.get('DIM1', None))
                # deal with the 2D case
                elif value['DIM'] == 2:
                    static_file.add_hkey_2d(key, values=value['VALUES'],
                                            dim1name=value.get('DIM1', None),
                                            dim2name=value.get('DIM2', None))    
            else:
                # add single value
                static_file.add_hkey(key, hdr_kwargs[key])
    # save to disk
    static_file.write_multi(data_list=data_list,
                            datatype_list=datatype_list,
                            name_list=name_list,
                            block_kind='static',
                            runstring='None', header_list=header_list)
    # add to output files (for indexing)
    recipe.add_output_file(static_file)


def update_repo(params: ParamDict, recipe, save_path: str,
                outdir: str = ''):
    """
    Update the local github repository for APERO with the new version of the
    files (up to now they have been saved to the installation path not the
    python module path)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: Apero recipe object
    :param save_path: str, path the static files were saved to

    :return None - copies writen files
    """
    # Step 1. use recipe.output_files and change det_path to assets path
    # Step 2. copy files to APERO local python module directory
    # Step 3. remove files from recipe.output_files (don't want to index)
    # get path to yaml file
    _asset_path = params['IPATH.RESET_ASSETS']
    # get the absolute path to the assets dir
    abs_asset_path = drs_data.construct_path(params, '', _asset_path)
    # get the instrument
    instrument = params['OBS.INSTRUMENT'].lower()
    # -------------------------------------------------------------------------
    # add outdir if set to abs_asset_path
    abs_asset_path = os.path.join(abs_asset_path, instrument, outdir)
    # make sure abs_asset_path exists
    os.makedirs(abs_asset_path, exist_ok=True)
    # ------------------------------------------------------------------------
    # get the keys of the output files
    output_keys = list(recipe.output_files.keys())
    # loop around files
    for key in output_keys:
        # get the basename
        basename = recipe.output_files[key]['FILENAME']
        # get the in path
        in_path = recipe.output_files[key]['PATH']
        in_file = str(os.path.join(in_path, basename))
        # skip anything that does not exist (shouldn't happen, but just in case)
        if not os.path.exists(in_path):
            continue
        # get the out path
        out_path = in_path.replace(save_path, abs_asset_path)
        out_file = str(os.path.join(out_path, basename))
        # Get user to confirm removal of file
        question = '\n\nUpdate and replace {0}?'.format(out_file)
        uinput = drs_text.user_input(question, dtype='YN')
        # only if user confirms removal of this file
        if uinput:
            # remove old file
            if os.path.exists(out_file):
                os.remove(out_file)
            # print progress
            msg = 'Replacing {0}'
            margs = [out_file]
            WLOG(params, '', msg.format(*margs))
            # copy file
            shutil.copy(in_file, out_file)
        # to avoid input issues on some systems
        time.sleep(0.25)
        # remove from recipe outputs (we don't want to index this file)
        del recipe.output_files[key]


def update_assets(params: ParamDict):
    """
    Update the assets to the remote repo

    :param params: ParamDict, parameter dictionary of constants

    :return None - updates remote assets
    """
    # Ask user if they wish to update the remote assets
    question = '\n\nUpdate REMOTE assets with all changes?'
    uinput = drs_text.user_input(question, dtype='YN', color='m')
    # deal with no --> return
    if not uinput:
        return
    # get path to yaml file
    _asset_path = params['IPATH.RESET_ASSETS']
    # get the absolute path to the assets dir
    abs_asset_path = drs_data.construct_path(params, '', _asset_path)
    # upload assets
    drs_assets.update_remote_assets(params, abs_asset_path)



# =============================================================================
# Define proxy night functions
# =============================================================================
def proxy_processing(params: ParamDict, recipe, sparams: Dict[str, Any],
                     cal_path: str, ofiles: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proxy preprocess function for static wavelength calibration

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the apero recipe instance
    :param sparams: dict, static parameters from yaml file

    :return None - writes to disk
    """
    # print progress
    WLOG(params, 'info', 'Processing static night (to extract HC and FP)')
    # get the raw files
    raw_files = dict()
    raw_files['DARK'] = sparams['files']['raw_dark_files']
    raw_files['DARK_FLAT'] = sparams['files']['raw_dark_flat_files']
    raw_files['FLAT_DARK'] = sparams['files']['raw_flat_dark_files']
    raw_files['FLAT_FLAT'] = sparams['files']['raw_flat_files']

    if isinstance(sparams['files']['raw_hc_file'], list):
        raw_files['HCONE_HCONE'] = sparams['files']['raw_hc_file']
    else:
        raw_files['HCONE_HCONE'] = [sparams['files']['raw_hc_file']]
    if isinstance(sparams['files']['raw_fp_file'], list):
        raw_files['FP_FP'] = sparams['files']['raw_fp_file']
    else:
        raw_files['FP_FP'] = [sparams['files']['raw_fp_file']]
    # ------------------------------------------------------------------------
    # get the input directory from sparams
    input_dir = os.path.dirname(sparams['inpath'])
    # create fake night directory
    raw_night_dir = os.path.join(params['PATH.RAW'], 'STATIC')
    # ------------------------------------------------------------------------
    # delete night directory if it exists
    if os.path.exists(raw_night_dir):
        shutil.rmtree(raw_night_dir)
    os.makedirs(raw_night_dir, exist_ok=True)
    # ------------------------------------------------------------------------
    # copy raw files to night directory (as symbolic links)
    for key in raw_files:
        for raw_file in raw_files[key]:
            # get the in file
            in_file = os.path.join(input_dir, raw_file)

            # deal with file not found
            if not os.path.exists(in_file):
                emsg = 'Raw {0} file not found: {1}'
                eargs = [key, in_file]
                raise AperoCodedException(params, None,
                                          message=emsg.format(*eargs),
                                          targs=eargs)

            # get the out file
            out_file = os.path.join(raw_night_dir, raw_file)
            # create symbolic link
            os.symlink(in_file, out_file)
    # ------------------------------------------------------------------------
    # run the static run yaml file
    _ = apero_processing.main('static_run.yaml')
    # ------------------------------------------------------------------------
    # copy out the data we require (for HC and FP)
    # ------------------------------------------------------------------------
    ofiles = get_q2ds_files(params, recipe, sparams, cal_path, ofiles)
    # return the output files
    return ofiles


def get_q2ds_files(params: ParamDict, recipe, sparams: Dict[str, Any],
                    cal_path: str, ofiles: Dict[str, Any]) -> Dict[str, Any]:
    # print progress
    WLOG(params, 'info', 'Loading static night extracted HC and FP files')
    # get the raw files
    raw_files = dict()
    raw_files['DARK'] = sparams['files']['raw_dark_files']
    raw_files['DARK_FLAT'] = sparams['files']['raw_dark_flat_files']
    raw_files['FLAT_DARK'] = sparams['files']['raw_flat_dark_files']
    raw_files['FLAT_FLAT'] = sparams['files']['raw_flat_files']
    raw_files['HCONE_HCONE'] = [sparams['files']['raw_hc_file']]
    raw_files['FP_FP'] = [sparams['files']['raw_fp_file']]
        # get the instrument name
    instrument = params['OBS.INSTRUMENT'].lower()
    # ------------------------------------------------------------------------
    # create fake night directory
    raw_night_dir = os.path.join(params['PATH.RAW'], 'STATIC')
    red_night_dir = os.path.join(params['PATH.RED'], 'STATIC')
    # ------------------------------------------------------------------------
    # copy out the data we require (for HC and FP)
    # ------------------------------------------------------------------------
    q2ds_files = dict()
    # we require the HCONE_HCONE and FP_FP files
    # we rename the .fits to _e2dsff_{sci_fiber}.fits
    for key in ['HCONE_HCONE', 'FP_FP']:
        # get the raw file
        raw_file = raw_files[key][0]
        # replace .fits with _e2dsff_{sci_fiber}.fits
        sci_fiber = sparams['wavelength']['wave_fiber']
        # get basename e2dsff file (including fiber)
        sci_basename = raw_file.replace('.fits',
                                        '_pp_q2dsff_{0}.fits'.format(sci_fiber))
        # get the in file
        in_file = os.path.join(red_night_dir, sci_basename)
        # deal with file not found
        if not os.path.exists(in_file):
            emsg = ('{0} file not found: {1}. Please make sure that '
                    'apero_processing (via wavelength.run_generate_night) '
                    'has been run successfully')
            eargs = [key, in_file]
            raise AperoCodedException(params, None,
                                      message=emsg.format(*eargs),
                                      targs=eargs)
        # get the out file
        out_file = os.path.join(cal_path, sci_basename)
        # print that we are copying
        msg = 'Copying {0} file: {1} to {2}'
        margs = [key, in_file, out_file]
        WLOG(params, '', msg.format(*margs))
        # copy file
        shutil.copy(in_file, out_file)
        # add to storage
        q2ds_files[key] = out_file
    # ------------------------------------------------------------------------
    # get the recipe defintion for apero_extract
    ext_recipe, _ = find_recipe(f'apero_extract_{instrument}.py', instrument,
                                recipe.recipemod)
    q2dsff_fileinst = getattr(ext_recipe, 'outputs')['Q2DSFF_FILE']
    # ------------------------------------------------------------------------
    # construct the DrsFitsFile instances for HC and FP
    hc_q2ds = q2dsff_fileinst.newcopy(filename=q2ds_files['HCONE_HCONE'],
                                      params=params, fiber=sci_fiber)
    fp_q2ds = q2dsff_fileinst.newcopy(filename=q2ds_files['FP_FP'],
                                      params=params, fiber=sci_fiber)
    # ------------------------------------------------------------------------
    # store the HCONE_HCONE and FP_FP files in recipe output files
    ofiles['STATIC_HC_Q2DS'] = hc_q2ds
    ofiles['STATIC_FP_Q2DS'] = fp_q2ds
    # ------------------------------------------------------------------------
    # deal with user wanting to remove the processed static data
    if sparams['wavelength']['remove_processed']:
        # remove all mentions of the static night directory using apero remove
        apero_remove.main(obsdir='STATIC', rawdb=True, nowarn=True)
        # remove the raw data too
        if os.path.exists(raw_night_dir):
            shutil.rmtree(raw_night_dir)
        # remove the reduced data too
        if os.path.exists(red_night_dir):
            shutil.rmtree(red_night_dir)
    # return the output files
    return ofiles


def get_hc_cat_file(params: ParamDict, recipe, sparams: Dict[str, Any],
                    cal_path: str, ofiles: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the static HC catalogue file

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the apero recipe instance
    :param sparams: dict, static parameters from yaml file
    :param cal_path: str, path to save the static files to
    :param ofiles: dict, dictionary of output files

    :return ofiles: dict, updated dictionary of output files
    """
    # print progress
    WLOG(params, 'info', 'Obtaining HC catalogue')
    # get static file
    static_file = recipe.outputs['STATIC_HC_CAT'].newcopy(params=params)
    # construct the filename from file instance
    static_file.construct_filename(path=cal_path)
    # return the output files
    ofiles['STATIC_HC_CAT'] = static_file
    # return the output files
    return ofiles


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello world')

# =============================================================================
# End of code
# =============================================================================
