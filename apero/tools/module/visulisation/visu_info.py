#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-12-12 at 11:52

@author: cook
"""
import glob
import os
from typing import Any, Dict, List, Optional, Tuple, Union

from apero.base import base
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.io import drs_fits
from apero.core.core import drs_file
from apero.tools.module.visulisation import visu_info_plots as vip


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.visulisation.visu_info.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict
# list of known identities that can be plotted
KNOWN_IDENTITIES = dict()
KNOWN_IDENTITIES['DRS_POST_E'] = vip.plot_drs_post_e
KNOWN_IDENTITIES['DRS_POST_S'] = vip.post_drs_post_s
KNOWN_IDENTITIES['DRS_POST_T'] = vip.plot_drs_post_t
KNOWN_IDENTITIES['DRS_POST_V'] = vip.post_drs_post_v
KNOWN_IDENTITIES['DRS_POST_P'] = vip.plot_drs_post_p
KNOWN_IDENTITIES['TELLU_TEMP'] = vip.red_tellu_temp
KNOWN_IDENTITIES['TELLU_TEMP_S1DW'] = vip.red_tellu_temp_s1dw
KNOWN_IDENTITIES['TELLU_TEMP_S1DV'] = vip.red_tellu_temp_s1dv
KNOWN_IDENTITIES['LBL_FITS'] = vip.lbl_fits
KNOWN_IDENTITIES['LBL_RDB_FITS'] = vip.lbl_rdb
KNOWN_IDENTITIES['LBL_RDB'] = vip.lbl_rdb
KNOWN_IDENTITIES['LBL_RDB2'] = vip.lbl_rdb
KNOWN_IDENTITIES['LBL_RDB_DRIFT'] = vip.lbl_rdb
KNOWN_IDENTITIES['LBL_RDB2_DRIFT'] = vip.lbl_rdb
# cache for warnings (only show once per identity)
UNKNOWN_IDENTITIES = []
NO_FUNC_IDENTITIES = []


# =============================================================================
# Define functions
# =============================================================================
def process_path(params: ParamDict, path: str):
    # -------------------------------------------------------------------------
    # deal with single file
    if os.path.isfile(path):
        return process_one_file(params, path)
    # deal with wildcards in path
    if '*' in path or '?' in path or '[' in path:
        return process_wildcards(params, path)
    # -------------------------------------------------------------------------
    # deal with path not existing
    if not os.path.exists(path):
        WLOG(params, 'error', f'Path does not exist: {path}')
        return
    # deal with all other cases where path is not a directory
    if not os.path.isdir(path):
        emsg = 'Path is not a file or directory: {0}'
        eargs = [path]
        WLOG(params, 'error',  emsg.format(*eargs))
        return
    # if we get to here process as a directory
    return process_directory(params, path)


def process_one_file(params: ParamDict, filename: str):
    # identify file type
    identity = identify_file(params, filename)
    # give the identity of the file
    msg = 'File: {0} identified as: {1}'
    margs = [filename, identity]
    WLOG(params, '',  msg.format(*margs))
    # generate info plot
    generate_info_plot(params, identity, filename)
    # return here
    return


def process_wildcards(params: ParamDict, path: str):
    # remove all " and ' characters from path
    path = path.replace('"', '').replace("'", '')
    # find all files matching wildcard
    all_files = glob.glob(path, recursive=True)
    # display the number of files found
    msg = 'Found {0} files matching wildcard'
    margs = [len(all_files)]
    WLOG(params, 'info', msg.format(*margs))
    valid_files, valid_identity = [], []
    # loop around all files
    for filename in all_files:
        # identify file type
        identity = identify_file(params, filename)
        # if identity is valid then append to valid list
        if identity is not None:
            valid_files.append(filename)
            valid_identity.append(identity)
    # ---------------------------------------------------------------------
    # display the number of valid files found
    msg = 'Found {0} valid files'
    margs = [len(valid_files)]
    WLOG(params, 'info', msg.format(*margs))
    # ---------------------------------------------------------------------
    # loop around valid files and generate info plots
    for identity, filename in zip(valid_identity, valid_files):
        generate_info_plot(params, identity, filename)
    # return here
    return


def process_directory(params: ParamDict, path: str):
    # -------------------------------------------------------------------------
    # print that we are searching directory
    msg = 'Searching directory for files: {0}'
    margs = [path]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    # otherwise find files in directory
    all_files = []
    for root, dirs, files in os.walk(path, followlinks=True):
        for file in files:
            all_files.append(os.path.join(root, file))
    # -------------------------------------------------------------------------
    # display the number of files found
    msg = 'Found {0} files'
    margs = [len(all_files)]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    valid_files, valid_identity = [], []
    # loop around all files
    for filename in all_files:
        # identify file type
        identity = identify_file(params, filename)
        # if identity is valid then append to valid list
        if identity is not None:
            valid_files.append(filename)
            valid_identity.append(identity)
    # -------------------------------------------------------------------------
    # display the number of valid files found
    msg = 'Found {0} valid files'
    margs = [len(valid_files)]
    WLOG(params, 'info', msg.format(*margs))
    # -------------------------------------------------------------------------
    # loop around valid files and generate info plots
    for identity, filename in zip(valid_identity, valid_files):
        generate_info_plot(params, identity, filename)
    # -------------------------------------------------------------------------
    return


# =============================================================================
# Identify functions
# =============================================================================
def identify_file(params: ParamDict, filename: str) -> Optional[str]:
    """
    Identify the file type based on its contents or extension

    :param params: ParamDict, parameter dictionary
    :param filename: str, the name of the file to identify

    :return: str or None, identified file type or None if unknown
    """
    # -------------------------------------------------------------------------
    # # first way of identifying file: by header key KW_OUT
    # identity = identify_via_header(params, filename)
    # # if we have identity then return it
    # if identity is not None:
    #     return identity
    # -------------------------------------------------------------------------
    # second way of identifying file: by file definition
    identity = identify_via_file_definition(params, filename)
    # -------------------------------------------------------------------------
    # if we get here we return identity (which may be None)
    return identity



def identify_via_header(params: ParamDict, filename: str) -> Optional[str]:
    """
    Identify file via header keyword KW_OUTPUT (if it exists)

    :param params: ParamDict, parameter dictionary
    :param filename: str, the name of the file to identify

    :return: str or None, identified file type or None if unknown
    """
    # deal with non-fits files
    if not filename.endswith('.fits'):
        return None
    # header key to search for
    hkey = params['KW_OUTPUT'][0]
    # load header
    header = drs_fits.read_header(params, filename, ext=0)
    # if header is None then return None
    if header is None:
        return None
    # if hkey not in header
    if hkey not in header:
        return None
    # get value from header
    identity = header[hkey]
    # we only keep identities that can be plotted
    if identity in KNOWN_IDENTITIES:
        return identity
    else:
        return None


def identify_via_file_definition(params: ParamDict, filename: str) -> Optional[str]:
    """
    Identify file via header keyword KW_OUTPUT (if it exists)

    :param params: ParamDict, parameter dictionary
    :param filename: str, the name of the file to identify

    :return: str or None, identified file type or None if unknown
    """
    # update instrument
    instrument = str(base.IPARAMS['INSTRUMENT'])
    # load pconst
    pconst = constants.pload(instrument=instrument)

    # file definitions
    file_mod = pconst.FILEMOD()
    file_definitions = file_mod.get()
    # define all filesets based on reduction order
    filesets = [file_definitions.raw_file,
                file_definitions.pp_file,
                file_definitions.red_file,
                file_definitions.lbl_file,
                file_definitions.post_file]
    # most likely that if we are searching via suffix this list is flipped
    filesets = filesets[::-1]
    # loop around file sets and try to identify file
    for fileset in filesets:
        found, drsfile = drs_file.id_drs_file(params, fileset, filename,
                                              required=False, nentries=1,
                                              load_data=False)
        # if we found it great - break here and don't try any more
        if found:
            # update the name
            identity = str(drsfile.name)
            # we only keep identities that can be plotted
            if identity in KNOWN_IDENTITIES.keys():
                return identity
    else:
        return None


# =============================================================================
# Plotting functions
# =============================================================================
def generate_info_plot(params: ParamDict, identity: str, filename: str):
    """
    Generate an info plot based on identity and filename

    :param params: ParamDict, parameter dictionary
    :param identity: str, the identity of the file (KW_OUTPUT and name of
                     the file_definition)
    :param filename: str, the full path to the file to plot

    :return:
    """
    global UNKNOWN_IDENTITIES
    global NO_FUNC_IDENTITIES
    # if identity is known generate plot
    if identity in KNOWN_IDENTITIES:
        # log that we are generating info plot
        WLOG(params, '',
             f'Generating info plot for file: {filename}')
        # get plot function
        plot_func = KNOWN_IDENTITIES[identity]
        # if plot function is not defined then we return
        if plot_func is None:
            if identity not in NO_FUNC_IDENTITIES:
                WLOG(params, 'warning',
                     f'No plot function for {identity}')
                NO_FUNC_IDENTITIES.append(identity)
            return
        # otherwise call the plot function
        plot_func(params, filename, identity)
    # else
    else:

        if identity not in UNKNOWN_IDENTITIES:
            WLOG(params, 'warning',
                 f'Unknown identity: {identity}')
            UNKNOWN_IDENTITIES.append(identity)
        return


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
