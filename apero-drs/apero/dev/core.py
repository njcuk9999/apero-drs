#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Developer functions that avoid some conditions of the loading the full
APERO package

Created on 2026-09-02 13:35


@author: cook
"""
import os
import shutil
import tempfile
from typing import Any, Dict, Optional

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions

# =============================================================================
# Define variables
# =============================================================================
# TODO: Remove these
TMP_DB_HOST = 'localhost'
TMP_DB_PASS = 'password'
TMP_DB_USER = 'apero'
TMP_DB_NAME = 'apero'
TMP_DB_TYPE = 'mysql+pymysql'
TMP_PROFILE_NAME = 'dev_profile'

# =============================================================================
# Define functions
# =============================================================================
def drs_uconfig(instrument: str):
    """
    Make a temporary DRS_CONFIG directory for testing purposes

    Avoids having to install APERO (temporarily)

    Most functions will need this (to test DRS_CONFIG is loaded)

    :param instrument: str, APERO instrument (e.g. SPIROU, NIRPS_HE)
    """
    # normalize and validate instrument against APERO setup choices
    instrument = _validate_instrument(instrument)

    # basic check to skip if DRS_UCONFIG is already set and usable
    uconfig = os.environ.get(base.USER_ENV, None)
    if _has_minimal_uconfig(uconfig):
        return

    # create temporary directories for the generated setup profile
    temp_root = tempfile.mkdtemp(prefix='apero_dev_')
    tmp_cfg_root = os.path.join(temp_root, 'config')
    tmp_data_root = os.path.join(temp_root, 'data')
    os.makedirs(tmp_cfg_root, exist_ok=True)
    os.makedirs(tmp_data_root, exist_ok=True)

    # build non-interactive setup params and resolve CONFIG_PATH
    params, sargs = _build_setup_params(instrument,
                                        tmp_cfg_root,
                                        tmp_data_root)

    # set DRS_UCONFIG before setup generation as requested
    os.environ[base.USER_ENV] = str(params['CONFIG_PATH'])

    # mirror run_setup mapping for apero.* keys needed by create_yamls
    for argname in sargs:
        apero_name = sargs[argname].apero_name
        if apero_name is not None:
            params[apero_name] = params[argname]

    # generate directories and yaml files without interactive setup steps
    from apero.setup.core import drs_setup
    drs_setup.create_paths(params, sargs)
    drs_setup.create_yamls(params)
    drs_setup.create_user_configs(params, sargs)

    # copy assets into temporary PATH.ASSETS (best effort)
    assets_path = params.get('ASSETSDIR', None)
    if isinstance(assets_path, str):
        _copy_assets(assets_path)


def get_base_params(instrument: str):
    """
    Load the apero constants for an instrument

    :param instrument: str, the apero instrument name (e.g. SPIROU)

    :return: ParamDict, the apero constants
    """
    # test and create temporary apero config files/directories required
    drs_uconfig(instrument)
    # now we can import from apero-drs (not before drs_uconfig)
    from apero.instruments import select
    # return the parameters as they are in the config
    return load_functions.load_config(select.INSTRUMENTS, instrument)


# =============================================================================
# Define private (worker) functions
# =============================================================================
def _has_minimal_uconfig(uconfig: Optional[str]) -> bool:
    """
    Check whether a DRS_UCONFIG path looks usable

    :param uconfig: str or None, candidate DRS_UCONFIG directory

    :return: bool, True if required yaml files already exist
    """
    if not isinstance(uconfig, str):
        return False
    if not os.path.isdir(uconfig):
        return False
    files = ['install.yaml', 'database.yaml', 'user_config.yaml',
             'user_constants.yaml', 'user_keywords.yaml']
    for filename in files:
        path = os.path.join(uconfig, filename)
        if not os.path.exists(path):
            return False
    return True


def _validate_instrument(instrument: str) -> str:
    """
    Validate the instrument name against APERO setup instrument choices

    :param instrument: str, candidate APERO instrument name

    :return: str, normalized and validated instrument name
    """
    instrument = str(instrument).strip().upper()
    if instrument in ['', 'NONE']:
        raise ValueError('drs_uconfig requires a valid instrument string')

    from apero.setup.core import drs_setup
    valid = list(drs_setup.INSTRUMENTS)
    if instrument not in valid:
        emsg = 'Invalid instrument "{0}". Must be one of: {1}'
        raise ValueError(emsg.format(instrument, ', '.join(valid)))
    return instrument


def _build_setup_params(instrument: str,
                        config_root: str,
                        data_root: str) -> tuple[Any, Dict[str, Any]]:
    """
    Build setup params for a non-interactive temporary profile creation

    :param instrument: str, APERO instrument name
    :param config_root: str, parent path for generated DRS_UCONFIG profile
    :param data_root: str, base path for generated DRS_DATA sub-directories

    :return: tuple, (setup params, setup argument dictionary)
    """
    from apero.setup.core import drs_setup
    from apero.setup.core import setup_constants

    sargs = setup_constants.SARGS
    params = param_functions.ParamDict()

    # seed params with all defaults used by setup constants
    for sname in sargs:
        sarg = sargs[sname]
        params.set(sarg.name, sarg.default_value, source='default')

    # fixed non-interactive values for developer bootstrap
    params.set('name', TMP_PROFILE_NAME, source='dev_functions')
    params.set('config_path', config_root, source='dev_functions')
    params.set('INSTRUMENT', instrument, source='dev_functions')
    params.set('DATADIR', data_root, source='dev_functions')

    params.set('DATABASE_MODE', TMP_DB_TYPE, source='dev_functions')
    params.set('DATABASE_HOST', TMP_DB_HOST, source='dev_functions')
    params.set('DATABASE_USER', TMP_DB_USER, source='dev_functions')
    params.set('DATABASE_PASS', TMP_DB_PASS, source='dev_functions')
    params.set('DATABASE_NAME', TMP_DB_NAME, source='dev_functions')
    params.set('DATABASE_USE_SSL', False, source='dev_functions')

    # this helper should never prompt and should only build local files
    params.set('UPDATE', False, source='dev_functions')
    params.set('CLEAN_START', False, source='dev_functions')
    params.set('CLEAN_PROMPT', False, source='dev_functions')
    params.set('DISABLE_DEMO_PROMPT', True, source='dev_functions')
    params.set('FORCE_DIR_CREATE', True, source='dev_functions')

    # apply DATADIR sets to all data sub-directories used by APERO
    _apply_set_values(params, sargs, 'DATADIR')
    # resolve CONFIG_PATH so it includes the profile name
    params = drs_setup.fix_config_path(params)
    return params, sargs


def _apply_set_values(params: Any,
                      sargs: Dict[str, Any],
                      sname: str):
    """
    Apply setup 'sets' rules for an argument into params

    :param params: ParamDict-like object, setup parameters
    :param sargs: dict, setup argument dictionary
    :param sname: str, argument name with a sets definition
    """
    if sname not in sargs:
        return
    sarg = sargs[sname]
    if sarg.sets is None:
        return
    for key in sarg.sets:
        value = sarg.sets[key].format(**params)
        params.set(key, value, source=f'set[{sname}]')


def _copy_assets(target_path: str):
    """
    Copy assets into the temporary DRS_DATA assets directory

    :param target_path: str, destination assets directory
    """
    # try repo assets first, then source-profile PATH.ASSETS
    candidates = _asset_sources()
    for source in candidates:
        cond1 = isinstance(source, str)
        cond2 = os.path.isdir(source)
        if not cond1 or not cond2:
            continue
        # skip empty folders so we keep searching for a useful source
        if len(os.listdir(source)) == 0:
            continue
        shutil.copytree(source, target_path, dirs_exist_ok=True)
        return


def _asset_sources() -> list:
    """
    Return candidate source directories for assets

    :return: list of strings, possible asset source paths
    """
    paths = []
    # candidate 1: packaged assets tree used by setup/assets tools
    apero_root = os.path.dirname(os.path.dirname(__file__))
    paths.append(os.path.join(apero_root, 'apero-assets'))
    # candidate 2: repository data assets (if present and non-empty)
    repo_root = os.path.dirname(apero_root)
    paths.append(os.path.join(repo_root, 'apero-data', 'assets'))
    return paths


# =============================================================================
# End of code
# =============================================================================
