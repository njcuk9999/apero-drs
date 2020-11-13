#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-24 10:36

only import from apero.base.base and apero.base.drs_exceptions

@author: cook
"""
import os
import shutil
from pathlib import Path
import pkg_resources
from typing import Any, Union

from apero.base import base
from apero.base import drs_base
from apero.base import drs_exceptions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.base.drs_break.py'
__PACKAGE__ = base.__PACKAGE__
__INSTRUMENT__ = 'None'
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# define current path
CURRENT_PATH = os.getcwd()


# =============================================================================
# Basic breakpoint/debug functions
# =============================================================================
def break_point(params: Any = None, allow: Union[None, bool] = None,
                level: int = 2):
    """
    Break and go into pdb (python debugger)/ipdb (ipython debugger)

    :param params: if not None is a ParamDict or dictionary containing the key
                   'ALLOW_BREAKPOINTS' (a boolean similar to allow)
    :param allow: bool, switch to turn on/off the break points
    :param level: int, the level above where the break point was called to
                  go into the ipdb/pdb debugger
    :return:
    """
    # set function name (cannot break inside break function)
    _ = str(__NAME__) + '.break_point()'
    # if we don't have parameters load them from config file
    if params is None:
        params = dict()
        # force to True
        params['ALLOW_BREAKPOINTS'] = True
    # if allow is not set
    if allow is None:
        allow = params['ALLOW_BREAKPOINTS']
    # if still not allowed the return
    if not allow:
        return
    # copy pdbrc
    _copy_pdb_rc(level=level)
    # catch bdb quit
    # noinspection PyPep8
    try:
        _execute_ipdb()
    except Exception:
        emsg = 'USER[00-000-00000]: Debugger breakpoint exit.'
        raise drs_exceptions.DebugExit(emsg)
    finally:
        # delete pdbrc
        _remove_pdb_rc()


def get_relative_folder(package: Union[None, str],
                        folder: Union[str, Path]) -> str:
    """
    Get the absolute path of folder defined at relative path
    folder from package

    :param package: string, the python package name
    :param folder: string, the relative path of the config folder

    :return data: string, the absolute path and filename of the default config
                  file
    """
    # set function name
    func_name = str(__NAME__) + '.get_relative_folder()'
    # try base function
    return drs_base.base_func(drs_base.base_get_relative_folder, func_name,
                              package, folder)


# =============================================================================
# Define worker functions
# =============================================================================
def _copy_pdb_rc(level: int = 0):
    """
    Copy the .pdbrc file to the current directory
    (needed to start pdb/ipdb with correct setup)
    :param level:
    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '_copy_pdb_rc()'
    # set global CURRENT_PATH
    global CURRENT_PATH
    # get package
    package = __PACKAGE__
    # get path
    path = base.PDB_RC_FILE
    filename = base.PDB_RC_FILENAME
    # get current path
    CURRENT_PATH = os.getcwd()
    # get absolute path
    oldsrc = get_relative_folder(package, path)
    tmppath = oldsrc + '_tmp'
    # get newsrc
    newsrc = os.path.join(CURRENT_PATH, filename)
    # read the lines
    with open(oldsrc, 'r') as f:
        lines = f.readlines()
    # deal with levels
    if level == 0:
        upkey = ''
    else:
        upkey = 'up\n' * level
    # loop around lines and replace
    newlines = []
    for line in lines:
        newlines.append(line.format(up=upkey))
    # write the lines
    with open(tmppath, 'w') as f:
        f.writelines(newlines)
    # copy
    shutil.copy(tmppath, newsrc)
    # remove tmp file
    os.remove(tmppath)


def _remove_pdb_rc():
    """
    Remove .pdbrc file from current CURRENT_PATH

    :return:
    """
    # set function name (cannot break here --> no access to inputs)
    _ = str(__NAME__) + '_remove_pdb_rc()'
    # get file name
    filename = base.PDB_RC_FILENAME
    # get newsrc
    newsrc = os.path.join(CURRENT_PATH, filename)
    # remove
    if os.path.exists(newsrc):
        os.remove(newsrc)


def _execute_ipdb():
    """
    start debugger (either ipdb if installed or pdb elsewise)

    :return:
    """
    # set function name (cannot break here --> within break function)
    _ = str(__NAME__) + '._execute_ipdb()'
    # start ipdb
    # noinspection PyBroadException
    try:
        # import ipython debugger
        # noinspection PyUnresolvedReferences
        import ipdb
        # set the ipython trace
        ipdb.set_trace()
    except Exception as _:
        # import python debugger (standard python module)
        import pdb
        # set the python trace
        pdb.set_trace()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
