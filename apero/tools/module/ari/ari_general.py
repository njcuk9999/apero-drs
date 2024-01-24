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
import string
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm

from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_misc
from apero.tools.module.ari import ari_core
from apero.tools.module.ari import ari_pages

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
TableFile = ari_pages.TableFile


# =============================================================================
# Define functions
# =============================================================================
def load_ari_params(params: ParamDict) -> ParamDict:
    """
    Load the ari parameters from the profile file

    :param params: ParamDict, the parameter dictionary of constants

    :return: ari_params: dict, the ari parameters
    """
    # set the function name
    func_name = __NAME__ + '.load_ari_params()'
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
    # clean user profile
    for char in string.punctuation:
        params.set('ARI_USER', value=params['ARI_USER'].replace(char, '_'),
                   source=func_name)
    # ----------------------------------------------------------------------
    # build some ARI paths for use throughout
    # ----------------------------------------------------------------------
    # over all ari directory
    ari_dir = os.path.join(params['DRS_DATA_OTHER'], 'ari',
                           str(params['ARI_USER']))
    # ARI object yaml directory
    ari_obj_yamls = os.path.join(ari_dir, 'object_yamls')
    # ARI recipe yaml directory
    ari_recipe_yamls = os.path.join(ari_dir, 'recipe_yamls')
    # ARI object page directory
    ari_obj_pages = os.path.join(ari_dir, 'object_pages')
    # ARI recipe page directory
    ari_recipe_pages = os.path.join(ari_dir, 'recipe_pages')

    # ARI default working
    dworking_rel = os.path.join('tools', 'resources', 'ari', 'working')
    dworking = drs_misc.get_relative_folder(base.__PACKAGE__, dworking_rel)
    # ----------------------------------------------------------------------
    # update parameter dictionary with these constants
    params.set('ARI_DIR', value=ari_dir, source=func_name)
    params.set('ARI_OBJ_YAMLS', value=ari_obj_yamls, source=func_name)
    params.set('ARI_RECIPE_YAMLS', value=ari_recipe_yamls, source=func_name)
    params.set('ARI_OBJ_PAGES', value=ari_obj_pages, source=func_name)
    params.set('ARI_RECIPE_PAGES', value=ari_recipe_pages, source=func_name)
    params.set('ARI_DWORKING_DIR', value=dworking, source=func_name)
    # ----------------------------------------------------------------------
    # make sure these directories exist
    for path in [ari_dir, ari_obj_yamls, ari_recipe_yamls, ari_obj_pages,
                 ari_recipe_pages]:
        if not os.path.exists(path):
            os.makedirs(path)
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
    # final step is to remove any objects that have no raw files
    new_object_classes = dict()
    # loop around objects
    for objname in list(object_classes.keys()):
        # get object class
        obj_class = object_classes[objname]
        # check if we have raw files
        if obj_class.filetypes['raw'].num > 0:
            new_object_classes[objname] = obj_class
    # -------------------------------------------------------------------------
    # return object classes
    return new_object_classes


def find_new_recipes(params: ParamDict, recipe_classes: Dict[str, AriRecipe]
                     ) -> Dict[str, AriRecipe]:
    return recipe_classes


def compile_object_data(params: ParamDict, object_classes: Dict[str, AriObject]
                        ) -> Tuple[Dict[str, AriObject], TableFile]:

    # add object pages
    ari_pages.add_obj_pages(params, object_classes)
    # make the object table page
    object_table = ari_pages.make_obj_table(params, object_classes)

    return object_classes, object_table


def compile_recipe_data(params: ParamDict, recipe_classes: Dict[str, AriRecipe]
                        ) -> Tuple[Dict[str, AriRecipe], TableFile]:

    # add the recipe pages

    # make the recipe tablepage
    recipe_table = TableFile.null_table(params)

    return recipe_classes, recipe_table



def save_yamls(params: ParamDict, object_classes: Dict[str, AriObject],
                recipe_classes: Dict[str, AriRecipe]):

    # -------------------------------------------------------------------------
    # Deal with objects
    # -------------------------------------------------------------------------
    for objname in object_classes:
        # get object class
        obj_class = object_classes[objname]
        # save yaml
        obj_class.save_to_disk(params)
    # -------------------------------------------------------------------------
    # Deal with recipes
    # -------------------------------------------------------------------------
    for recipename in recipe_classes:
        # get recipe class
        recipe_class = recipe_classes[recipename]
        # save yaml
        # recipe_class.save_to_disk(params)
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
