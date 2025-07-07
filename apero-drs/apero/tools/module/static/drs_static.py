#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-26 at 09:40

@author: cook
"""
import os
import shutil
from typing import Any, Dict, List, Union

import numpy as np
from astropy.table import Table

from aperocore import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore.core import drs_text

from apero.base import base as apero_base
from apero.utils import drs_data
from apero.tools.module.setup import drs_assets

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
        emsg = 'yamlfile not found: {0}'
        eargs = [yamlfile]
        raise AperoCodedException(params, None, message=emsg.format(eargs),
                                  targs=eargs)
    # load parameters
    sparams = base.load_yaml(yamlfile)
    # return sparams
    return sparams


def save_static_file(params: ParamDict, recipe, det_path: str,
                     static_file_name: str, desc: str,
                     data_list: List[Union[np.ndarray, Table]],
                     datatype_list: List[str],
                     name_list: List[str],
                     hdr_kwargs: Dict[str, Any] = None):
    """
    Save a static file using the standard apero file instance

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: Apero recipe object
    :param det_path: str, path to save the static file
    :param static_file_name: str, name of the static file
                             (must be in recipe.outputs)
    :param desc: str, description from writing status
    :param data_list: list, list of data to be saved [np.ndarray and/or Table]
    :param datatype_list: list, list of datatypes to be saved "image" or "table"
    :param name_list: list, list of names to be saved (the EXTNAME in a fits
                      file)
    :param hdr_kwargs: dict, keyword arguments (in params) i.e. KW_XXX
                       to push into the headers

    :return None - writes to disk
    """
    # get dark file
    static_file = recipe.outputs[static_file_name].newcopy(params=params)
    # construct the filename from file instance
    static_file.construct_filename(path=det_path)
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
            static_file.add_hkey(key, hdr_kwargs[key])
    # save to disk
    static_file.write_multi(data_list=data_list,
                            datatype_list=datatype_list,
                            name_list=name_list,
                            block_kind='static',
                            runstring='None')
    # add to output files (for indexing)
    recipe.add_output_file(static_file)


def update_repo(params: ParamDict, recipe, save_path: str):
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

    # output files
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
        question = 'Update and replace {0}?'.format(out_file)
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
        # remove from recipe outputs (we don't want to index this file)
        del recipe.output_files[key]


def update_assets(params: ParamDict):
    """
    Update the assets to the remote repo

    :param params: ParamDict, parameter dictionary of constants

    :return None - updates remote assets
    """
    # Ask user if they wish to update the remote assets
    question = 'Update remote assets with all changes?'
    uinput = drs_text.user_input(question, dtype='YN')
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
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello world')

# =============================================================================
# End of code
# =============================================================================
