#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-01-23 at 15:52

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
def _add_obj_page(it: int, key: str, params: ParamDict,
                  object_classes: Dict[str, AriObject],
                  return_dict: Any = None) -> Dict[int, Any]:
    # get object
    object_class = object_classes[key]
    # deal with no return_dict
    if return_dict is None:
        return_dict = dict()
    # get the object name for this row
    objname = object_class.objname
    # ------------------------------------------------------------------
    # print progress
    msg = '\tCreating page for {0} [{1} of {2}]'
    margs = [objname, it + 1, len(object_classes)]
    WLOG(params, '', msg.format(*margs))
    # ---------------------------------------------------------------------
    # populate the header dictionary for this object instance
    # wlog(params, '', f'\t\tPopulating header dictionary')
    object_class.populate_header_dict()

    # TODO: Got to here (Line 2743 of simple_ari.py)


def _add_obj_pages(params: ParamDict, object_classes: Dict[str, AriObject]):

    # -------------------------------------------------------------------------
    # deal with no entries in object table
    if len(object_classes) == 0:
        # print progress
        WLOG(params, '', 'No objects found in object table')
        # return empty table
        return object_classes
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, 'info', 'Creating object pages')
    # set up the arguments for the multiprocessing
    args = [0, '', params, object_classes]
    # get the number of cores
    n_cores = params['ARI_NCORES']
    if n_cores is None:
        raise ValueError('Must define N_CORES in settings or profile')
    # storage for results
    results_dict = dict()
    # -------------------------------------------------------------------------
    # deal with running on a single core
    if n_cores == 1:
        # change the object column to a url
        for it, key in enumerate(object_classes):
            # combine arguments
            itargs = [it, key] + args[2:]
            # run the pool
            results = _add_obj_page(*itargs)
            # push result to result storage
            results_dict[key] = results[it]
    # -------------------------------------------------------------------------
    # deal with running on a single core
    if n_cores == 1:
        # change the object column to a url
        for it, key in enumerate(object_classes):
            # combine arguments
            itargs = [it, key] + args[2:]
            # run the pool
            results = _add_obj_page(*itargs)
            # push result to result storage
            results_dict[key] = results[it]
    # -------------------------------------------------------------------------
    elif n_cores > 1:
        if ari_core.MULTI == 'POOL':
            from multiprocessing import get_context
            # list of params for each entry
            params_per_process = []
            for it, key in enumerate(object_classes):
                itargs = [it, key] + args[2:]
                params_per_process.append(itargs)
            # start parellel jobs
            with get_context('spawn').Pool(n_cores, maxtasksperchild=1) as pool:
                results = pool.starmap(_add_obj_page, params_per_process)
            # fudge back into return dictionary
            for row in range(len(results)):
                objname = results[row]['OBJNAME']
                # push into results dict
                results_dict[objname] = results[row]
        else:
            from multiprocessing import Process, Manager
            # split up groups
            group_iterations, group_keys = [], []
            all_iterations = list(range(len(object_classes)))
            all_keys = list(object_classes.keys())
            ngroups = int(np.ceil(len(object_classes)/n_cores))
            for group_it in range(ngroups):
                start = group_it * n_cores
                end = (group_it * n_cores) + n_cores
                iterations = all_iterations[start:end]
                keys = all_keys[start:end]
                # push into storage
                group_iterations.append(iterations)
                group_keys.append(keys)
            # start the process manager
            manager = Manager()
            return_dict = manager.dict()
            # do the multiprocessing
            for group_it in range(ngroups):
                jobs = []
                # loop around jobs in group
                for group_jt in range(len(group_iterations[group_it])):
                    group_args = [group_iterations[group_it][group_jt],
                                  group_keys[group_it][group_jt]] + args[2:]
                    group_args += [return_dict]
                    # get parallel process
                    process = Process(target=_add_obj_page, args=group_args)
                    process.start()
                    jobs.append(process)
                # do not continue until finished
                for pit, proc in enumerate(jobs):
                    proc.join()
                # fudge back into return dictionary
                for row in return_dict.keys():
                    objname = str(return_dict[row]['OBJNAME'])
                    results_dict[objname] = dict(return_dict[row])
    # -------------------------------------------------------------------------
    # update object classes with results
    # -------------------------------------------------------------------------
    # replace object name with the object name + object url
    for key in object_classes:
        if key in results_dict:
            # get the object class for this key
            object_class = object_classes[key]
            # -----------------------------------------------------------------
            # update results
            # -----------------------------------------------------------------
            # This is where we add any results coming back from add_obj_page
            object_class.objurl = results_dict[key]['OBJURL']
            object_class.objpageref = results_dict[key]['OBJPAGEREF']
    # -------------------------------------------------------------------------
    # return the object table
    return object_classes



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
