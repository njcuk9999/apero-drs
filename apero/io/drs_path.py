#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-21 at 11:36

@author: cook
"""
import pkg_resources
import numpy as np
from astropy import units as uu
import os
import shutil
from pathlib import Path
from typing import Union

from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_log
from apero import lang


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'io.drs_path.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.drs_text.TextEntry
# -----------------------------------------------------------------------------


# =============================================================================
# Define functions
# =============================================================================
def get_relative_folder(params, package, folder):
    """
    Get the absolute path of folder defined at relative path
    folder from package

    :param params: ParamDict, the parameter dictionary of constants
    :param package: string, the python package name
    :param folder: string, the relative path of the config folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    func_name = __NAME__ + '.get_relative_folder()'
    # get the package.__init__ file path
    try:
        init = pkg_resources.resource_filename(package, '__init__.py')
    except ImportError:
        eargs = [package, func_name]
        WLOG(params, 'error', TextEntry('00-008-00001', args=eargs))
        init = None
    # Get the config_folder from relative path
    current = os.getcwd()
    # get directory name of folder
    dirname = os.path.dirname(init)
    # change to directory in init
    os.chdir(dirname)
    # get the absolute path of the folder
    data_folder = os.path.abspath(folder)
    # change back to working dir
    os.chdir(current)
    # test that folder exists
    if not os.path.exists(data_folder):
        eargs = [os.path.basename(data_folder), os.path.dirname(data_folder),
                 func_name]
        WLOG(params, 'error', TextEntry('00-008-00002', args=eargs))
    # return the absolute data_folder path
    return data_folder


def get_uncommon_path(path1, path2):
    # get common source
    common = os.path.commonpath([path2, path1]) + os.sep
    uncommon = path2.split(common)[-1]
    return uncommon


def get_nightname(params, filepath, root=None):
    """
    Get the night name from a absolute filepath
        structure of filepath should be:
        filepath = root/night_name/filename

    :param params: ParamDict, the parameter dictionary of constants
    :param filepath: str, the absolute filepath
    :param root: str, the root directory (above night name) if None uses
                 params['INPATH']

    :type filepath: str
    :type root: str

    :return: the night name
    :rtype: str
    """
    # deal with no root
    if root is None:
        root = params['INPATH']
    # get the dirname
    if os.path.isdir(filepath):
        dirname = str(filepath)
    else:
        dirname = os.path.dirname(filepath)
    # get the night name by splitting from the root dir
    night_name = dirname.split(root)[-1]
    # remove any leading separators
    while night_name.startswith(os.sep):
        night_name = night_name[len(os.sep):]
    # get the night_name
    return night_name


def group_files_by_time(params, times, time_thres, time_unit='hours'):
    func_name = __NAME__ + '.group_files_by_time()'
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
            WLOG(params, 'error', TextEntry('00-008-00008', args=eargs))
        except Exception as e:
            eargs = [type(e), str(e), func_name]
            WLOG(params, 'error', TextEntry('00-008-00009', args=eargs))
    elif time_unit == 'hours':
        time_thres = time_thres / 24
    elif time_unit == 'days':
        pass
    else:
        eargs = [time_unit, func_name]
        WLOG(params, 'error', TextEntry('00-008-00010', args=eargs))
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


def get_most_recent(filelist):
    """
    Find the most recent file in a list of files

    :param filelist: list of strings, the file list (absolute paths)

    :return:
    """
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


def makedirs(params, path):
    # set function name
    func_name = display_func(params, 'makedirs', __NAME__)
    # test if path does not already exist
    if not os.path.exists(path):
        # try to make directories
        try:
            os.makedirs(path)
        # catch all exceptions and pipe to drs error
        except Exception as e:
            eargs = [path, type(e), e, func_name]
            WLOG(params, 'error', TextEntry('01-010-00002', args=eargs))


def copytree(src: Union[str, Path], dst: Union[str, Path]):
    for root, dirs, files in os.walk(src):
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


def copyfile(params, src, dst, log=True):
    # set function name
    func_name = __NAME__ + '.copyfile()'
    # only copy if we have the source file
    if os.path.exists(src):
        # if logging then log
        if log:
            wargs = [src, dst]
            WLOG(params, '', TextEntry('40-000-00011', args=wargs))
        # copy using shutil
        try:
            shutil.copy(src, dst)
        except Exception as e:
            eargs = [src, dst, type(e), e, func_name]
            WLOG(params, '', TextEntry('00-004-00006', args=eargs))
    # else raise exception
    else:
        eargs = [src, dst, func_name]
        WLOG(params, 'error', TextEntry('00-004-00005', args=eargs))


def numpy_load(filename):
    # set function name
    func_name = __NAME__ + '.numpy_load()'
    # try the original load function
    try:
        return np.load(filename)
    except Exception as _:
        pass
    # try the load with pickle allowed
    try:
        return np.load(filename, allow_pickle=True)
    except Exception as _:
        pass
    # try the load, loading as a string first
    try:
        return np.load(open(filename, 'rb'))
    except Exception as _:
        pass
    # if we have got to here we cannot load filename
    eargs = [filename, func_name]
    emsg = 'NumpyLoad: Cannot load filename={0} \n\t Funcion = {1}'
    raise ValueError(emsg.format(*eargs))


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
