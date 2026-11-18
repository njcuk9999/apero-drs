#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run APERO RI profile tasks as a final APERO processing tool."""

import os
from pathlib import Path
from typing import Any, Dict

import apero as apero_pkg
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
    # the APERO profile name is the DRS_UCONFIG directory name
    uconfig = os.environ.get(params['DRS.USERENV'], '')
    profile_name = Path(uconfig.rstrip(os.sep)).name.strip()
    profile_path = (Path(params['PATH.OTHER']) / 'ari-config'
                    / f'{profile_name}.yaml')

    if not profile_name or not profile_path.is_file():
        message = textentry(
            'APERO_RI_TASK_NO_PROFILE', args=[profile_name or 'unknown'])
        WLOG(params, 'warning', message)
        return locals()

    try:
        from apero_ri import tasks as task_module
        from apero_ri.tasks import apero_sync
    except ImportError as e:
        emsg = ('APERO RI is not installed. Please install it to run this '
                'task. \n{0}:{1}')
        eargs = [type(e), str(e)]
        raise AperoCodedException(params, None, message=emsg, targs=eargs)
    # get the instrument and local data directory
    instrument = str(params['OBS.INSTRUMENT'])
    local_data_dir = str(Path(params['PATH.OTHER']) / 'apero-ri')
    # run all profile-scoped tasks
    task_results = dict()
    for task_key in apero_sync.local_task_keys():
        if task_module.TYPE.get(task_key) != 'PROFILE':
            continue
        run_args = [task_key, str(profile_path)]
        run_kwargs = dict(local_data_dir=local_data_dir,
                          instrument=instrument,
                          verbose=True)
        # run the task and store the result
        result = apero_sync.run_for_profile(*run_args, **run_kwargs)
        task_results[task_key] = result
        if result.get('status') != 'completed':

            emsg = ('APERO RI task {0} failed for profile {1}. '
                    'Error: {2}')
            eargs = [task_key, profile_name, result.get('error')]
            raise AperoCodedException(params, None, message=emsg, targs=eargs)
    # end of function return local workspace
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    main()

# =============================================================================
# End of code
# =============================================================================