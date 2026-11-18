#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run APERO RI profile tasks as a final APERO processing tool."""

import os
from importlib import resources
from pathlib import Path
from typing import Any, Dict

import yaml

import apero as apero_pkg
from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log
from aperocore import drs_lang
from apero.utils import drs_startup
from apero.utils.drs_recipe import DrsRecipe

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri_task.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
WLOG = drs_log.wlog
textentry = drs_lang.textentry
ParamDict = param_functions.ParamDict
AperoCodedException = drs_log.AperoCodedException

# =============================================================================
# Define functions
# =============================================================================
def main(**kwargs: Any) -> Any:
    """Set up, run, and close the APERO RI task wrapper."""
    recipe_args = dict(**kwargs)
    recipe, params = drs_startup.setup(
        __NAME__, __INSTRUMENT__, recipe_args, enable_plotter=False)
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    local_vars, success = drs_startup.run(__main__, recipe, params)
    return drs_startup.end_main(
        params, local_vars, recipe, success, outputs='None')


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """Run profile-scoped local tasks for the active APERO profile.

    :param recipe: APERO recipe context.
    :param params: Active APERO profile parameters.
    :return: Local execution state used by the APERO recipe wrapper.
    """
    profile_override = params['INPUTS'].get('PROFILE')
    uconfig = os.environ.get(params['DRS.USERENV'], '')
    profile_name = Path(uconfig).name
    task_results = dict()
    if not profile_override and not profile_name:
        WLOG(params, 'warning', textentry('APERO_RI_TASK_NO_PROFILE'))
        return dict(task_results=task_results)

    try:
        from apero_ri import tasks as task_module
        from apero_ri.tasks import apero_sync
    except ModuleNotFoundError as e:
        if e.name != 'apero_ri':
            raise
        message = textentry('APERO_RI_TASK_NOT_INSTALLED')
        if profile_override:
            raise AperoCodedException(params, None, message=message) from e
        WLOG(params, 'warning', message)
        return dict(task_results=task_results)
    except ImportError as e:
        emsg = ('APERO RI is not installed. Please install it to run this '
                'task. \n{0}:{1}')
        eargs = [type(e), str(e)]
        raise AperoCodedException(params, None, message=emsg, targs=eargs)
    # get the instrument and local data directory
    instrument = str(params['OBS.INSTRUMENT'])
    local_data_dir = str(Path(params['PATH.OTHER']) / 'apero-ri')
    if profile_override:
        profile_path = Path(profile_override).expanduser().resolve()
        profile_name = profile_path.stem
        run_input = str(profile_path)
        run_task = apero_sync.run_for_profile
        run_kwargs = dict(local_data_dir=local_data_dir,
                          instrument=instrument, verbose=True)
    else:
        profile = _build_profile(params, instrument)
        run_input = dict(LOCAL_DATA_DIR=local_data_dir, INSTRUMENT=instrument,
                         APERO_PROFILES={profile_name: profile},
                         APERO_PROFILE_NAMES=[profile_name])
        run_task = apero_sync.run
        run_kwargs = dict(verbose=True)
    # run all profile-scoped tasks
    for task_key in apero_sync.local_task_keys():
        if task_module.TYPE.get(task_key) != 'PROFILE':
            continue
        run_args = [task_key, run_input]
        # run the task and store the result
        result = run_task(*run_args, **run_kwargs)
        task_results[task_key] = result
        if result.get('status') != 'completed':

            emsg = ('APERO RI task {0} failed for profile {1}. '
                    'Error: {2}')
            eargs = [task_key, profile_name, result.get('error')]
            raise AperoCodedException(params, None, message=emsg, targs=eargs)
    return dict(task_results=task_results)


def _build_profile(params: ParamDict, instrument: str) -> Dict[str, Any]:
    """Build a local ARI profile without writing credentials to disk.

    :param params: Active APERO profile parameters.
    :param instrument: APERO instrument code.
    :return: Profile mapping for the local task runner.
    """
    config_dir = resources.files('apero_ri') / 'resources'
    preset_dir = config_dir / 'aprofile_instruments'
    preset_path = preset_dir / f'{instrument.lower()}_v8.yaml'
    profile = yaml.safe_load(preset_path.read_text(encoding='utf-8'))
    general = profile['general']
    general['INSTRUMENT'] = instrument
    general['SCIENCE_FIBER'] = general['science_fiber']
    general['SCIENCE_TYPES'] = list(params['PP.OBJ_DPRTYPES'])

    paths = dict()
    for path in ('RAW', 'PP', 'RED', 'CALIB', 'OUT', 'TELLU', 'LOG', 'LBL',
                 'OTHER', 'ASSETS'):
        paths[f'PATH_{path}'] = str(params[f'PATH.{path}'])
    profile['paths'] = paths

    settings = base.DPARAMS
    database = dict(DATABASE_MODE=settings['TYPE'],
                    DATABASE_HOST=settings['HOST'],
                    DATABASE_USER=settings['USER'],
                    DATABASE_PASSWORD=settings['PASSWD'] or '',
                    DATABASE_NAME=settings['DATABASE'],
                    DATABASE_PORT=settings.get('PORT',
                                               base.DEFAULT_DATABASE_PORT))
    for kind in ('CALIB', 'FINDEX', 'LOG', 'TELLU'):
        table = settings[kind]
        name = table['NAME']
        database[f'{kind}_TABLENAME'] = (name if name.endswith('_db')
                                        else table['TABLE'])
    profile['database'] = database
    return profile


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    main()

# =============================================================================
# End of code
# =============================================================================