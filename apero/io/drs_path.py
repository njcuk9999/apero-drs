#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO path functionality

Created on 2019-03-21 at 11:36

@author: cook

Import rules:
    only from core.core.drs_log, core.io, core.math, core.constants,
    apero.lang, apero.base

    do not import from core.io.drs_image
    do not import from core.core.drs_file
    do not import from core.core.drs_argument
    do not import from core.core.drs_database
"""
import hashlib
import os
import shutil
import tarfile
from pathlib import Path
from typing import Any, List, Optional, Union

import numpy as np
from astropy import units as uu

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_exceptions
from apero.core.core import drs_log
from apero.core.core import drs_misc

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_path.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get tqdm
tqdm = base.tqdm_module()
# get the parameter dictionary
ParamDict = constants.ParamDict
# Get function string
display_func = drs_log.display_func
# Get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# Get Logging function
WLOG = drs_log.wlog
TLOG = drs_log.Printer
# Get the text types
textentry = lang.textentry


# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def get_relative_folder(params: ParamDict, package: str, folder: str) -> str:
    """
    Get the absolute path of folder defined at relative path
    folder from package (wrapper around drs_break.get_relative_folder to catch
    DrsCodedException)

    :param params: ParamDict, the parameter dictionary of constants
    :param package: string, the python package name
    :param folder: string, the relative path of the config folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    # set function
    # _ = display_func('get_relative_folder', __NAME__)
    # try to get relative directory
    try:
        data_folder = drs_misc.get_relative_folder(package, folder)
    except DrsCodedException as e:
        WLOG(params, e.level, textentry(e.codeid, args=e.targs))
        data_folder = None
    # return the absolute data_folder path
    return data_folder


def get_uncommon_path(path1: str, path2: str) -> str:
    """
    Get the uncommon path of "path1" compared to "path2"

    i.e. if path1 = /home/user/dir1/dir2/dir3/
         and path2 = /home/user/dir1/

         the output should be /dir2/dir3/

    :param path1: string, the longer root path to return (without the common
                  path)
    :param path2: string, the shorter root path to compare to

    :return uncommon_path: string, the uncommon path between path1 and path2
    """
    # set function
    # _ = display_func('get_uncommon_path', __NAME__)
    # return result from drs_misc.get_uncommon_path
    return drs_misc.get_uncommon_path(path1, path2)


def group_files_by_time(params: ParamDict, times: np.ndarray,
                        time_thres: Union[uu.Quantity, float],
                        time_unit: Union[uu.Unit, str] = 'hours') -> np.ndarray:
    """
    Take a np.array of times ('times') and sort them into groups based on
    being closer to each other than "time_thres'

    :param params: ParamDict, parameter dictionary of constants
    :param times: np.array of Time objects (if time_thres is a astropy.Quantity)
                  else a list of floats (either in 'hours' or 'days' - changable
                  using 'time_unit'
    :param time_thres: the largest separation of times for two times to be
                       grouped together
    :param time_unit: the unit of the time for 'times' and 'time_thres' must be
                      either astropy.Unit or a string ['hours' or 'days']

    :return: np.array of group numbers (the groups assigned to each element of
             'times'
    """
    # set function
    func_name = display_func('group_files_by_time', __NAME__)
    # make sure time units are correct
    cond1 = not isinstance(time_unit, str)
    cond2 = isinstance(time_thres, uu.Quantity)
    if cond1 or cond2:
        try:
            if cond2:
                time_thres = time_thres.to(uu.day)
            else:
                time_thres = (time_thres * time_unit).to(uu.day)
        except uu.UnitConversionError as e:
            eargs = [str(e), func_name]
            WLOG(params, 'error', textentry('00-008-00008', args=eargs))
        except Exception as e:
            eargs = [type(e), str(e), func_name]
            WLOG(params, 'error', textentry('00-008-00009', args=eargs))
    elif time_unit == 'hours':
        time_thres = time_thres / 24
    elif time_unit == 'days':
        pass
    else:
        eargs = [time_unit, func_name]
        WLOG(params, 'error', textentry('00-008-00010', args=eargs))
    # ID of matched multiplets of files
    matched_id = np.zeros_like(times, dtype=int)
    # loop until all files are matched with all other files taken within
    #    time_thres
    group_num, it = 1, 0
    while mp.nanmin(matched_id) == 0 and it < len(times):
        # find all non-matched dark times
        non_matched = matched_id == 0
        # find the first non-matched dark time
        first = mp.nanmin(np.where(non_matched)[0])
        # find all non-matched that are lower than threshold (in days)
        group_mask = np.abs(times[first] - times) < time_thres
        # add this group to matched_id
        matched_id[group_mask] = group_num
        # change the group number (add 1)
        group_num += 1
        # increase iterator
        it += 1
    # return the group match id
    return matched_id


def get_most_recent(filelist: List[str]) -> Union[float, None]:
    """
    Find the most recent file in a list of files and return its modified time

    :param filelist: list of strings, the file list (absolute paths)

    :return: float the modified time of the most recent file
    """
    # set function
    # _ = display_func('get_most_recent', __NAME__)
    # set most recent time to None to start
    most_recent = None
    # loop around file list
    for file_it in filelist:
        # get modified time
        file_time = os.path.getctime(file_it)
        # add to most_recent if newer
        if most_recent is None:
            most_recent = file_time
        elif file_time > most_recent:
            most_recent = file_time
    # return most recent time
    return most_recent


def makedirs(params: ParamDict, path: str):
    """
    Make directory 'path' and all sub-directories

    :param params: ParamDict, parameter dictionary of constants
    :param path: str, the directory + sub-directories to make (as one path)

    :return: None - just makes the 'path'
    """
    # set function name
    func_name = display_func('makedirs', __NAME__)
    # test if path does not already exist
    if not os.path.exists(path):
        # try to make directories
        try:
            os.makedirs(path)
        # catch all exceptions and pipe to drs error
        except Exception as e:
            eargs = [path, type(e), e, func_name]
            WLOG(params, 'error', textentry('01-010-00002', args=eargs))


def copytree(src: Union[str, Path], dst: Union[str, Path]):
    """
    Copy a file/directory tree - from path 'src' to 'dst'

    :param src: str, the source path
    :param dst: str, the desination path

    :return: None - just copies directories
    """
    # set function name
    # _ = display_func('makedirs', __NAME__)
    # loop around src path and go to every directory/sub-directory/file
    for root, dirs, files in os.walk(src, followlinks=True):
        # out root
        outroot = root.replace(str(src), str(dst))
        # deal with directory not existing
        for directory in dirs:
            dirpath = Path(outroot).joinpath(directory)
            if not dirpath.exists():
                os.mkdir(dirpath)

        # deal with files
        for filename in files:
            # get input file path
            infile = Path(root).joinpath(filename)
            outfile = Path(outroot).joinpath(filename)
            # copy file
            shutil.copy(str(infile), str(outfile))


def copyfile(params: ParamDict, src: str, dst: str, log: bool = True):
    """
    Copy a single file (catching exceptions where possible)

    :param params: ParamDict, parameter dictionary of constants
    :param src: str, the source file path
    :param dst: str, the output file path
    :param log: bool, if True logs that this file has been copied

    :return: None - just copies file
    """
    # set function name
    func_name = display_func('copyfile', __NAME__)
    # only copy if we have the source file
    if os.path.exists(src):
        # if logging then log
        if log:
            wargs = [src, dst]
            WLOG(params, '', textentry('40-000-00011', args=wargs))
        # copy using shutil
        try:
            shutil.copy(src, dst)
        except Exception as e:
            eargs = [src, dst, type(e), e, func_name]
            WLOG(params, '', textentry('00-004-00006', args=eargs))
    # else raise exception
    else:
        eargs = [src, dst, func_name]
        WLOG(params, 'error', textentry('00-004-00005', args=eargs))


def numpy_load(filename: str) -> Any:
    """
    do np.load (but with some added tries when it fails - i.e. with pickle
    or just opening the file first before raising exception

    :param filename: str, the numpy file to load

    :return: the return from np.load for 'filename'
    """
    # set function name
    func_name = display_func('numpy_load', __NAME__)
    # try the original load function
    # noinspection PyBroadException
    try:
        return np.load(filename)
    except Exception as _:
        pass
    # try the load with pickle allowed
    # noinspection PyBroadException
    try:
        return np.load(filename, allow_pickle=True)
    except Exception as _:
        pass
    # try the load, loading as a string first
    # noinspection PyBroadException
    try:
        # noinspection PyTypeChecker
        return np.load(open(filename, 'rb'))
    except Exception as _:
        pass
    # if we have got to here we cannot load filename
    eargs = [filename, func_name]
    emsg = 'NumpyLoad: Cannot load filename={0} \n\t Funcion = {1}'
    raise ValueError(emsg.format(*eargs))


def get_all_non_empty_subdirs(path: Union[Path, str],
                              relative: bool = True) -> List[str]:
    """
    Get all non-empty sub directories to "path" if relative is True only
    return the relative path to "path" else returns the full path for each
    subdirs are only returned if a file is found

    :param path: Path or str, the root path to check
    :param relative: bool, if True only returns the path relative to root "path"

    :return: List of strings, the paths (absolute or relative) of subdirectories
             that have files
    """
    # make sure path is a Path instance
    if isinstance(path, str):
        path = Path(path)
    # get all dirs in path
    all_dirs = list(path.rglob('**'))
    # storage of outputs
    subdirs = []
    # loop around all dirs
    for _dir in all_dirs:
        # we only want directories
        if _dir.is_dir():
            # get uncommon path
            if relative:
                save_path = get_uncommon_path(str(_dir), str(path))
            else:
                save_path = str(_dir)
            # flag to keep dir
            keep_dir = False
            # list contents of dir
            contents = list(_dir.glob('*'))
            # loop around contents and look for files
            for item in contents:
                if item.is_file():
                    keep_dir = True
                    break

            # if we are keeping dir add it to subdirs
            if keep_dir and save_path not in subdirs:
                subdirs.append(save_path)
    # return all valid subdirs
    return subdirs


# noinspection PyUnresolvedReferences
def listdirs(rootdir: str) -> List[str]:
    """
    Fast recursive listing of directories
    :param rootdir: str, the root path to search

    :return: list of strings, the directories under root dir
    """
    # store directories
    directories = []
    # loop around items in rootdir
    for it in os.scandir(rootdir):
        # check if it 1. is a directory 2. is not empty
        if it.is_dir():
            # add to paths
            if not nofiles(it):
                directories.append(it.path)
            # add sub directories
            directories += listdirs(it)
    # sort directories
    directories = sorted(directories)
    # return sort directories
    return directories


def get_dirs(path: str, relative=False) -> List[str]:
    """
    Get all directories under "path"

    :param path: str, the path to check for sub-directories
    :param relative: bool, if True send back relative paths otherwise return
                     absolute path

    :return: list of paths (absolute or relative)
    """
    obs_dirs = []
    for root, dirs, files in os.walk(path):
        obs_dirs.append(root)
    # if we need absolute path
    if not relative:
        return obs_dirs
    # store relative obs_dirs
    rel_obs_dirs = []
    # convert to relative paths
    for obs_dir in obs_dirs:
        # if obs_dir the path remove it
        if obs_dir == path:
            continue
        # make path finish with os.sep
        if not path.endswith(os.sep):
            testpath = path + os.sep
        else:
            testpath = path
        if obs_dir.startswith(testpath):
            rel_obs_dirs.append(obs_dir[len(testpath):])
        else:
            rel_obs_dirs.append(obs_dir)
    # return the relative paths
    return rel_obs_dirs


def nofiles(rootdir: str) -> bool:
    """
    Test wether a a rootdir is empty (if it is a directory at all)

    return True if rootdir is not a directory or is empty
    else return False

    :param rootdir: str, root directory to test

    :return: bool, True if not a directory or empty
    """
    if not os.path.isdir(rootdir):
        return True
    if len(listfiles(rootdir)) == 0:
        return True
    else:
        return False


def listfiles(rootdir) -> List[str]:
    """
    Fast listing of files in a directory
    :param rootdir: str, the root path to search
    :return:
    """
    files = []
    for it in os.scandir(rootdir):
        if it.is_file():
            files.append(it.path)
    # return file list
    return files


def recursive_path_glob(params: ParamDict,
                        path: Union[Path, str],
                        prefix: Optional[str] = None,
                        suffix: Optional[str] = None) -> List[Path]:
    """
    Recursively get all files from a directory with
    a specific prefix / suffix
    """
    valid_files = []
    # whether we need to check prefix and / or suffix
    check_prefix = prefix is not None
    check_suffix = suffix is not None

    # loading message
    TLOG(params, '', 'Analying path: {0}'.format(path))
    # use os walk to loop around files
    for root, dirs, files in os.walk(str(path)):
        TLOG(params, '', 'Analying path: {0}'.format(root))
        # get the root as a Pathlib instance
        root_instant = Path(root)
        # loop around all files
        for filename in files:
            # check file prefix
            if check_prefix:
                if not filename.startswith(prefix):
                    continue
            # check file suffix
            if check_suffix:
                if not filename.endswith(suffix):
                    continue
            # if we get to here file is valid
            valid_files.append(root_instant.joinpath(filename))
    # clear message
    TLOG(params, '', '')
    # sort valid files
    valid_files = sorted(valid_files)
    # return valid files
    return valid_files


def calculate_checksum(filename: str) -> str:
    """
    Calculate the checksum of a file

    :param filename: str, the path to the file to calculate the checksum of
    :return: str, the checksum of the file
    """
    hasher = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def make_tarfile(output_filename: str, source_dir: str):
    """
    Make a tar file from a directory

    :param output_filename: the output tar filename
    :param source_dir: str, the source directory to add to the tar file
    :return:
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def extract_tarfile(tar_filename: str, extract_dir: str):
    """
    Extract a tar file to a directory

    :param tar_filename: str, the tar file to extract
    :param extract_dir: str, the directory to extract the tar file to
    :return:
    """
    with tarfile.open(tar_filename, "r:gz") as tar:
        tar.extractall(path=extract_dir)

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
