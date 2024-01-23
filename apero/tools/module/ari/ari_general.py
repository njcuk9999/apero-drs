#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-22 at 10:25

@author: cook
"""
import os
import platform
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.tools.module.ari import ari_core


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.tools.module.ari.ari_core.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# -----------------------------------------------------------------------------
# Get ParamDict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get ARI core classes
AriObject = ari_core.AriObject
AriRecipe = ari_core.AriRecipe
FileType = ari_core.FileType


# =============================================================================
# Define functions
# =============================================================================
def load_ari_params(params: ParamDict) -> ParamDict:
    """
    Load the ari parameters from the profile file

    :param params: ParamDict, the parameter dictionary of constants

    :return: ari_params: dict, the ari parameters
    """
    # get arguments from recipe call (via params['INPUTS'])
    profile_yaml = params['INPUTS']['profile']
    obs_dir = params['INPUTS']['obsdir']
    # ----------------------------------------------------------------------
    # load yaml file into raw_params
    if os.path.exists(profile_yaml):
        try:
            ari_params = base.load_yaml(profile_yaml)
        except Exception as e:
            emsg = 'Error loading profile file: {0}\n\t{1}'
            eargs = [profile_yaml, e]
            WLOG(params, 'error', emsg.format(*eargs))
            return params
    # otherwise log an error message
    else:
        emsg = 'Cannot find profile file: {0}'
        eargs = [profile_yaml]
        WLOG(params, 'error', emsg.format(*eargs))
        return params
    # ----------------------------------------------------------------------
    # deal with individual settings
    # ----------------------------------------------------------------------
    # the username
    if ari_params['settings']['username'] == 'None':
        ari_params['settings']['username'] = platform.node()
    # the observation directory
    if ari_params['settings']['obsdir'] == 'None':
        ari_params['settings']['obsdir'] = obs_dir
    # ----------------------------------------------------------------------
    # push values into parameter dictionary
    # ----------------------------------------------------------------------
    # push yaml values into params using the YAML_TP_PARAM translation dict
    for key in ari_core.YAML_TO_PARAM:
        if '.' in key:
            key1, key2 = key.split('.')
            try:
                value = ari_params[key1][key2]
            except Exception as e:
                emsg = 'Yaml file {0} does not contain key'
                eargs = [profile_yaml]
                WLOG(params, 'error', emsg.format(*eargs))
                return params
        else:
            try:
                value = ari_params[key]
            except Exception as e:
                emsg = 'Yaml file {0} does not contain key'
                eargs = [profile_yaml]
                WLOG(params, 'error', emsg.format(*eargs))
                return params
        # deal with param key not existing in params
        param_key = ari_core.YAML_TO_PARAM[key]
        if param_key not in params:
            emsg = 'Param key {0} does not exist'
            eargs = [param_key]
            WLOG(params, 'error', emsg.format(*eargs))
            return params
        # push value into params
        params.set(key=param_key, value=value, source=profile_yaml)
    # ----------------------------------------------------------------------
    # return the ari parameters
    return params


def load_previous_objects(params: ParamDict) -> Dict[str, AriObject]:
    # get a list of objects from astrometric database
    astrometric_obj_list = _get_object_table(params)
    # get the filetypes for these params
    filetypes = ari_core.ari_filetypes(params)
    # get has_polar criteria
    has_polar = ari_core.get_has_polar(params)
    # -------------------------------------------------------------------------
    # create objects
    obj_classes = dict()
    # loop around objects in astrometric table
    for row, objname in enumerate(astrometric_obj_list[ari_core.OBJECT_COLUMN]):
        obj_class = AriObject(objname, filetypes=filetypes)
        # add astrometric data
        obj_class.add_astrometrics(astrometric_obj_list.iloc[row])
        # set the has_polar key
        obj_class.has_polar = has_polar
        # append to storage
        obj_classes[objname] = obj_class
    # -------------------------------------------------------------------------
    # log progress
    msg = 'Getting previous state of ARI from disk'
    WLOG(params, '', msg)
    # -------------------------------------------------------------------------
    # for each object we load from disk
    for objname in list(obj_classes.keys()):
        # get object class
        obj_class = obj_classes[objname]
        # add files stats
        obj_class.load_from_disk(params)
    # -------------------------------------------------------------------------
    # sort objects by name
    obj_classes_sorted = dict()
    # loop through all objects sorted alphabetically
    for objname in np.sort(list(obj_classes.keys())):
        # get the object class for this object name
        obj_class = obj_classes[objname]
        # add to sorted list of objects
        obj_classes_sorted[objname] = obj_class
    # -------------------------------------------------------------------------
    # return object class dict (sorted by name)
    return obj_classes_sorted


def load_previous_recipes(params: ParamDict) -> Dict[str, AriRecipe]:
    return dict()


def find_new_objects(params: ParamDict, object_classes: Dict[str, AriObject]
                     ) -> Dict[str, AriObject]:
    # -------------------------------------------------------------------------
    # get the index database from file index database
    indexdbm = drs_database.FileIndexDatabase(params)
    indexdbm.load_db()
    # get the log database
    logdbm = drs_database.LogDatabase(params)
    logdbm.load_db()
    # -------------------------------------------------------------------------
    # log progress
    WLOG(params, '', 'Compiling object files stats (this may take a while)')
    # -------------------------------------------------------------------------
    # for each object we run several counts
    # loop around objects in the object table
    for objname in tqdm(list(object_classes.keys())):
        # get object class
        obj_class = object_classes[objname]
        # add files stats
        obj_class.add_files_stats(indexdbm, logdbm)
    # -------------------------------------------------------------------------
    # return object classes
    return object_classes


def find_new_recipes(params: ParamDict, recipe_classes: Dict[str, AriRecipe]
                     ) -> Dict[str, AriRecipe]:
    return recipe_classes


def compile_object_data(params: ParamDict, object_classes: Dict[str, AriObject]
                        ) -> Dict[str, AriObject]:
    return object_classes


def compile_recipe_data(params: ParamDict, recipe_classes: Dict[str, AriRecipe]
                        ) -> Dict[str, AriRecipe]:
    return recipe_classes


def write_object_pages(params: ParamDict,
                       object_classes: Dict[str, AriObject]) -> None:
    pass


def write_recipe_pages(params: ParamDict,
                       recipe_classes: Dict[str, AriRecipe]) -> None:
    pass


def compile_object_pages(params: ParamDict) -> None:
    pass


def compile_recipe_pages(params: ParamDict) -> None:
    pass


def upload(params: ParamDict) -> None:
    pass


# -----------------------------------------------------------------------------
# Object worker functions
# -----------------------------------------------------------------------------
def _get_object_table(params: ParamDict) -> pd.DataFrame:
    # -------------------------------------------------------------------------
    # set up condition for filtering
    condition = None
    # deal with filtering by object
    if params['ARI_FILTER_OBJECTS']:
        if isinstance(params['ARI_FILTER_OBJECTS_LIST'], list):
            subconditions = []
            for objname in params['ARI_FILTER_OBJECTS_LIST']:
                subconditions.append(f'OBJNAME="{objname}"')
            condition = ' OR '.join(subconditions)
            condition = f'({condition})'
        else:
            wmsg = 'filter objects is not a list. Skipping filtering.'
            WLOG(params, 'warning', wmsg, sublevel=1)
    # -------------------------------------------------------------------------
    # log progress
    WLOG(params, '', 'Loading objects from astrometric database')
    # -------------------------------------------------------------------------
    # get the astrometric database from apero
    astrodbm = drs_database.AstrometricDatabase(params)
    astrodbm.load_db()
    # -------------------------------------------------------------------------
    # get astrometric columns
    astrom_cols = ari_core.ASTROMETRIC_COLUMNS
    # log that we are loading
    # get the object table from the astrometric database
    object_table = astrodbm.get_entries(columns=','.join(astrom_cols),
                                        condition=condition)
    # return the object_table
    return object_table


# -----------------------------------------------------------------------------
# Recipe worker functions
# -----------------------------------------------------------------------------



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
