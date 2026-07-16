#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2024-12-04 at 10:21

@author: cook
"""
import glob
import os
import pickle
import time
from typing import Any, Optional

import numpy as np

from apero.base import base
from aperocore.constants import param_functions
from aperocore.core import drs_log

# =============================================================================
# Define variables
# =============================================================================
# get param dict
ParamDict = param_functions.ParamDict
# get tqdm
tqdm = base.TQDM
# Get Logging function
WLOG = drs_log.wlog
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def make_pickle(params: ParamDict, instance: Any, prefix: str, suffix: int,
                log: bool = True):
    """
    Make a pickle file from any pickle-able object

    :param params: ParamDict, the parameter dictionary of constants
    :param instance: Any object
    :param prefix: str, the prefix of the pickle file
    :param suffix: str, the suffix of the pickle file

    :return: None, writes file to DRS_DATA_OTHER/pickles/{prefix}/
    """
    # get the output directory
    outdir = os.path.join(params['PATH.OTHER'], 'pickles', prefix)
    # make directory if it doesn't exist - safe in concurrent runs
    os.makedirs(outdir, exist_ok=True)
    # construct the filename
    filename = os.path.join(outdir, f'{str(suffix)}.apero_pickle')

    if log:
        msg = 'Pickling file: {0}'
        margs = [filename]
        WLOG(params, '', msg.format(*margs))
    # write the pickle file
    with open(filename, 'wb') as pickle_file:
        pickle.dump(instance, pickle_file)


def get_pickle(params: ParamDict, prefix: str, suffix: Optional[int] = None,
               remove: bool = False) -> Any:
    """
    Get a pickle file from DRS_DATA_OTHER/pickles/{prefix}/

    :param params: ParamDict, the parameter dictionary of constants
    :param prefix: str, the prefix of the pickle file
    :param suffix: str, the suffix of the pickle file
    :param remove: bool, if True removes prefix directory after reading

    :return: The loaded pickle file (or list of loaded pickle files)
    """
    # get the output directory
    outdir = os.path.join(params['PATH.OTHER'], 'pickles', prefix)
    # no suffix - get all files
    if suffix is None:
        # construct the filename
        files = glob.glob(os.path.join(outdir, '*.apero_pickle'))
        # sort alphabetically
        files = np.sort(files)
    else:
        # construct the filename
        files = [str(os.path.join(outdir, f'{str(suffix)}.apero_pickle'))]
    # get all pickled files
    instances = dict()
    for filename in tqdm(files):
        # get suffix
        _suffix = int(os.path.basename(filename).split('.apero_pickle')[0])
        # read the pickle file
        with open(filename, 'rb') as pickle_file:
            instances[_suffix] = pickle.load(pickle_file)
    # if we are removing files remove them now
    if remove:
        msg = 'Removing pickle directory: {0} ({1} files)'
        margs = [outdir, len(files)]
        WLOG(params, '', msg.format(*margs))
        # loop around files and remove
        for filename in files:
            os.remove(filename)
        # remove the directory too
        os.removedirs(outdir)
    # if we had a suffix just return it
    if suffix is None:
        # sort instance dictionary by keys
        out_dict = dict()
        for key in np.sort(list(instances.keys())):
            out_dict[key] = instances[key]
        # return dictionary
        return out_dict
    # otherwise return the single instance
    else:
        return instances[suffix]


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
