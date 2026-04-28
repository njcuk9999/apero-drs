#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-12-12 at 11:52

@author: cook
"""
import glob
import math
import os
from typing import Any, Dict, List, Optional, Tuple, Union
from tqdm import tqdm

from apero.base import base as apero_base
from apero.core import drs_file
from apero.instruments.default import instrument as instrument_mod
from apero.io import drs_fits
from apero.tools.module.visulisation import visu_info_plots as vip
from apero.utils import drs_recipe
from aperocore.constants import param_functions
from aperocore.constants import load_functions
from aperocore.core import drs_log
from apero.instruments import select
from apero.utils import drs_utils

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.visulisation.visu_info.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# get parameter dictionary
ParamDict = param_functions.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
Instrument = instrument_mod.Instrument
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
    if _use_multiprocessing_identify(params, all_files):
        valid_files, valid_identity = _collect_valid_files_mp(params,
                                                              all_files,
                                                              'wildcards')
    else:
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
    if _use_multiprocessing_plot(params, valid_files):
        _generate_info_plots_mp(params, valid_identity, valid_files,
                                source='wildcards')
    else:
        for identity, filename in tqdm(zip(valid_identity, valid_files),
                                       total=len(valid_files),
                                       desc='Plot wildcards', leave=False):
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
    if _use_multiprocessing_identify(params, all_files):
        valid_files, valid_identity = _collect_valid_files_mp(params,
                                                              all_files,
                                                              'directory')
    else:
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
    if _use_multiprocessing_plot(params, valid_files):
        _generate_info_plots_mp(params, valid_identity, valid_files,
                                source='directory')
    else:
        for identity, filename in tqdm(zip(valid_identity, valid_files),
                                       total=len(valid_files),
                                       desc='Plot directory', leave=False):
            generate_info_plot(params, identity, filename)
    # -------------------------------------------------------------------------
    return


def _use_multiprocessing_identify(params: ParamDict, all_files: List[str]) -> bool:
    if len(all_files) == 0:
        return False
    cores = drs_utils.get_cores(params)
    mode = str(params['REPROCESS_MP_FINDEX']).lower()
    return mode in ['pathos', 'pool', 'process'] and cores > 1


def _use_multiprocessing_plot(params: ParamDict, valid_files: List[str]) -> bool:
    return _use_multiprocessing_identify(params, valid_files)


def _collect_valid_files_mp(params: ParamDict, all_files: List[str],
                            source: str) -> Tuple[List[str], List[str]]:
    """Collect valid files and identities using configured multiprocessing."""
    if len(all_files) == 0:
        return [], []
    cores = drs_utils.get_cores(params)
    mode = str(params['REPROCESS_MP_FINDEX']).lower()
    if mode == 'pathos' and cores > 1:
        return _multi_process_identify_pathos(params, all_files, cores, source)
    elif mode == 'pool' and cores > 1:
        return _multi_process_identify_pool(params, all_files, cores, source)
    elif mode == 'process' and cores > 1:
        return _multi_process_identify_process(params, all_files, cores, source)
    else:
        return _multi_identify(params, all_files, source=source)


def _split_all_files(all_files: List[str], cores: int) -> List[List[str]]:
    if len(all_files) == 0:
        return []
    cores = min(cores, len(all_files))
    chunk_size = int(math.ceil(len(all_files) / cores))
    return [all_files[it:it + chunk_size]
            for it in range(0, len(all_files), chunk_size)]


def _multi_identify(params: ParamDict, all_files: List[str],
                    job: int = None, total_jobs: int = None,
                    source: str = 'files') -> Tuple[List[str], List[str]]:
    if (job is not None) and (total_jobs is not None):
        label = '{0} [{1}/{2}]'.format(source, job, total_jobs)
    else:
        label = source
    valid_files, valid_identity = [], []
    for filename in tqdm(all_files, desc='Identify ' + label, leave=False):
        identity = identify_file(params, filename)
        if identity is not None:
            valid_files.append(filename)
            valid_identity.append(identity)
    return valid_files, valid_identity


def _multi_process_identify_pathos(params: ParamDict, all_files: List[str],
                                   cores: int, source: str
                                   ) -> Tuple[List[str], List[str]]:
    try:
        from pathos.pools import ParallelPool as Pool
    except ImportError:
        WLOG(params, 'warning', 'pathos not available; using serial identify')
        return _multi_identify(params, all_files, source=source)

    grouped_files = _split_all_files(all_files, cores)
    params_per_process = []
    for g_it, grouped_file in enumerate(grouped_files):
        params_per_process.append([params, grouped_file, g_it + 1,
                                   len(grouped_files), source])
    params_per_process2 = list(zip(*params_per_process))
    pool = Pool(ncpus=min(cores, len(grouped_files)), maxtasksperchild=1)
    grouped_results = pool.map(_multi_identify, *params_per_process2)
    pool.close()
    pool.join()
    valid_files, valid_identity = [], []
    for group_files, group_identity in grouped_results:
        valid_files += list(group_files)
        valid_identity += list(group_identity)
    return valid_files, valid_identity


def _multi_process_identify_pool(params: ParamDict, all_files: List[str],
                                 cores: int, source: str
                                 ) -> Tuple[List[str], List[str]]:
    from multiprocessing import get_context

    grouped_files = _split_all_files(all_files, cores)
    params_per_process = []
    for g_it, grouped_file in enumerate(grouped_files):
        params_per_process.append([params, grouped_file, g_it + 1,
                                   len(grouped_files), source])
    with get_context('spawn').Pool(min(cores, len(grouped_files)),
                                   maxtasksperchild=1) as pool:
        grouped_results = pool.starmap(_multi_identify, params_per_process)
    valid_files, valid_identity = [], []
    for group_files, group_identity in grouped_results:
        valid_files += list(group_files)
        valid_identity += list(group_identity)
    return valid_files, valid_identity


def _process_identify_wrapper(params: ParamDict, all_files: List[str],
                              job: int, total_jobs: int, source: str, queue):
    queue.put((job, _multi_identify(params, all_files, job, total_jobs,
                                    source=source)))


def _multi_process_identify_process(params: ParamDict, all_files: List[str],
                                    cores: int, source: str
                                    ) -> Tuple[List[str], List[str]]:
    from multiprocessing import Process
    from multiprocessing import Queue

    grouped_files = _split_all_files(all_files, cores)
    queue = Queue()
    jobs = []
    for g_it, grouped_file in enumerate(grouped_files):
        args = [params, grouped_file, g_it + 1, len(grouped_files), source,
                queue]
        process = Process(target=_process_identify_wrapper, args=args)
        process.start()
        jobs.append(process)
    for proc in jobs:
        proc.join()
    ordered_results = {}
    for _ in range(len(grouped_files)):
        group_id, group_result = queue.get()
        ordered_results[group_id] = group_result
    valid_files, valid_identity = [], []
    for g_it in range(1, len(grouped_files) + 1):
        group_files, group_identity = ordered_results[g_it]
        valid_files += list(group_files)
        valid_identity += list(group_identity)
    return valid_files, valid_identity


def _split_plot_groups(valid_identity: List[str], valid_files: List[str],
                       cores: int) -> List[Tuple[List[str], List[str]]]:
    if len(valid_files) == 0:
        return []
    cores = min(cores, len(valid_files))
    chunk_size = int(math.ceil(len(valid_files) / cores))
    groups = []
    for it in range(0, len(valid_files), chunk_size):
        groups.append((valid_identity[it:it + chunk_size],
                       valid_files[it:it + chunk_size]))
    return groups


def _multi_generate_plots(params: ParamDict, valid_identity: List[str],
                          valid_files: List[str], job: int = None,
                          total_jobs: int = None, source: str = 'files') -> None:
    if (job is not None) and (total_jobs is not None):
        label = '{0} [{1}/{2}]'.format(source, job, total_jobs)
    else:
        label = source
    iterator = zip(valid_identity, valid_files)
    for identity, filename in tqdm(iterator, total=len(valid_files),
                                   desc='Plot ' + label, leave=False):
        generate_info_plot(params, identity, filename)


def _generate_info_plots_mp(params: ParamDict, valid_identity: List[str],
                            valid_files: List[str], source: str) -> None:
    if len(valid_files) == 0:
        return
    cores = drs_utils.get_cores(params)
    mode = str(params['REPROCESS_MP_FINDEX']).lower()
    if mode == 'pathos' and cores > 1:
        _multi_process_plot_pathos(params, valid_identity, valid_files,
                                   cores, source)
    elif mode == 'pool' and cores > 1:
        _multi_process_plot_pool(params, valid_identity, valid_files,
                                 cores, source)
    elif mode == 'process' and cores > 1:
        _multi_process_plot_process(params, valid_identity, valid_files,
                                    cores, source)
    else:
        _multi_generate_plots(params, valid_identity, valid_files,
                              source=source)


def _multi_process_plot_pathos(params: ParamDict, valid_identity: List[str],
                               valid_files: List[str], cores: int,
                               source: str) -> None:
    try:
        from pathos.pools import ParallelPool as Pool
    except ImportError:
        WLOG(params, 'warning', 'pathos not available; using serial plotting')
        _multi_generate_plots(params, valid_identity, valid_files,
                              source=source)
        return

    grouped = _split_plot_groups(valid_identity, valid_files, cores)
    params_per_process = []
    for g_it, (group_identity, group_files) in enumerate(grouped):
        params_per_process.append([params, group_identity, group_files,
                                   g_it + 1, len(grouped), source])
    params_per_process2 = list(zip(*params_per_process))
    pool = Pool(ncpus=min(cores, len(grouped)), maxtasksperchild=1)
    pool.map(_multi_generate_plots, *params_per_process2)
    pool.close()
    pool.join()


def _multi_process_plot_pool(params: ParamDict, valid_identity: List[str],
                             valid_files: List[str], cores: int,
                             source: str) -> None:
    from multiprocessing import get_context

    grouped = _split_plot_groups(valid_identity, valid_files, cores)
    params_per_process = []
    for g_it, (group_identity, group_files) in enumerate(grouped):
        params_per_process.append([params, group_identity, group_files,
                                   g_it + 1, len(grouped), source])
    with get_context('spawn').Pool(min(cores, len(grouped)),
                                   maxtasksperchild=1) as pool:
        pool.starmap(_multi_generate_plots, params_per_process)


def _process_plot_wrapper(params: ParamDict, valid_identity: List[str],
                          valid_files: List[str], job: int, total_jobs: int,
                          source: str) -> None:
    _multi_generate_plots(params, valid_identity, valid_files,
                          job=job, total_jobs=total_jobs, source=source)


def _multi_process_plot_process(params: ParamDict, valid_identity: List[str],
                                valid_files: List[str], cores: int,
                                source: str) -> None:
    from multiprocessing import Process

    grouped = _split_plot_groups(valid_identity, valid_files, cores)
    jobs = []
    for g_it, (group_identity, group_files) in enumerate(grouped):
        args = [params, group_identity, group_files, g_it + 1, len(grouped),
                source]
        process = Process(target=_process_plot_wrapper, args=args)
        process.start()
        jobs.append(process)
    for proc in jobs:
        proc.join()


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
    # load pconst
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)

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
        if params['INPUTS'].get('TEST', False):
            WLOG(params, 'info',
                 f'Test mode: would have generated plot for {filename} '
                 f'using {str(plot_func)}')
            return
        else:
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
