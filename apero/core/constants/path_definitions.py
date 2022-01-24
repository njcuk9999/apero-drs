#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Definitions of path classes (information on the paths should only come from
here)

Created on 2021-07-15

@author: cook
"""
import os
from typing import Any, List, Tuple, Union

from apero import lang
from apero.base import base
from apero.core.constants import param_functions
from apero.core.core import drs_exceptions


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'path_definitions.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get time object
Time = base.Time
# Get the text types
textentry = lang.textentry
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get the Drs Exceptions
DrsCodedException = drs_exceptions.DrsCodedException
DrsCodedWarning = drs_exceptions.DrsCodedWarning
# -----------------------------------------------------------------------------
# define complex typing
QCParamList = Union[Tuple[List[str], List[Any], List[str], List[int]],
                    List[Union[List[str], List[int], List[Any]]]]


# =============================================================================
# Define Path classes
# =============================================================================
class BlockPath:

    description: lang.Text = None
    name: str = None
    key: str = None
    argname: str = None

    def __init__(self, params: ParamDict, name: str, key: str,
                 indexing: bool, logging: bool):
        """
        Construct the block path

        :param params: ParamDict, the parameter dictionary of constants
        :param name: str, the name of the block path
        :param key: str, the key in params where block path absolute path
                    stored
        :param indexing: bool, if True this block is indexed
        :param logging: bool, if True this block is logged
        """
        # convert block path to real path (remove symbolic links)
        try:
            block_path = params[key]
            # check that block path exists
            if not os.path.exists(block_path):
                emsg = 'BlockPathError: Key {0} does not exist\n\tPath={1}'
                eargs = [key, params[key]]

                raise drs_exceptions.DrsCodedException('', 'error',
                                                       targs=eargs,
                                                       message=emsg)
        except Exception as e:
            emsg = 'BlockPathError: Key {0}\n\tPath={1}\n\t{2}: {3}'
            eargs = [key, params[key], type(e), str(e)]
            raise drs_exceptions.DrsCodedException('', 'error',
                                                   targs=eargs,
                                                   message=emsg)
        # now set path
        self.key = key
        self.path = block_path
        self.name = name
        self.has_obs_dirs = False
        self.fileset = None
        self.indexing = indexing
        self.logging = logging

    def __str__(self) -> str:
        """
        String Representation of the BlockPath

        :return: str, the string representation of the block path
        """
        return 'BlockPath[{0}]'.format(self.name)

    def __repr__(self) -> str:
        """
        String Representation of the BlockPath

        :return: str, the string representation of the block path
        """
        return self.__str__()

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)


class RawPath(BlockPath):

    description: lang.Text = textentry('DATA_RAW_DESC')
    name: str = 'raw'
    key: str = 'DRS_DATA_RAW'
    argname: str = 'rawdir'

    def __init__(self, params):
        """
        Construct the raw block path (input data)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=True,
                         logging=False)
        self.fileset = 'raw_file'
        self.has_obs_dirs = True


class TmpPath(BlockPath):

    description: lang.Text = textentry('DATA_TMP_DESC')
    name: str = 'tmp'
    key: str = 'DRS_DATA_WORKING'
    argname: str = 'tmpdir'

    def __init__(self, params):
        """
        Construct the tmp block path (preprocessing data)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=True,
                         logging=True)
        self.fileset = 'pp_file'
        self.has_obs_dirs = True


class ReducedPath(BlockPath):

    description: lang.Text = textentry('DATA_REDUC_DESC')
    name: str = 'red'
    key: str = 'DRS_DATA_REDUC'
    argname: str = 'reddir'

    def __init__(self, params):
        """
        Construct the reduced block path (reduced data)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=True,
                         logging=True)
        self.has_obs_dirs = True
        self.fileset = 'red_file'


class CalibPath(BlockPath):

    description: lang.Text = textentry('DATA_CALIB_DESC')
    name: str = 'calib'
    key: str = 'DRS_CALIB_DB'
    argname: str = 'calibdir'

    def __init__(self, params):
        """
        Construct the calibration block path (calibration data)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=False,
                         logging=False)
        self.has_obs_dirs = False
        self.fileset = 'calib_file'


class TelluPath(BlockPath):

    description: lang.Text = textentry('DATA_TELLU_DESC')
    name: str = 'tellu'
    key: str = 'DRS_TELLU_DB'
    argname: str = 'telludir'

    def __init__(self, params):
        """
        Construct the telluric block path (telluric data)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=False,
                         logging=False)
        self.has_obs_dirs = False
        self.fileset = 'tellu_file'


class OutPath(BlockPath):

    description: lang.Text = textentry('DATA_OUT_DESC')
    name: str = 'out'
    key: str = 'DRS_DATA_OUT'
    argname: str = 'outdir'

    def __init__(self, params):
        """
        Construct the postprocess path (post processed data)

        :param params: ParamDict, the parameter dictionary of constants
        """
        # TODO: no PARAM_SNAPSHOT --> can't redo log
        super().__init__(params, self.name, self.key, indexing=True,
                         logging=False)
        self.has_obs_dirs = True
        self.fileset = 'out_file'


class AssetPath(BlockPath):

    description: lang.Text = textentry('DATA_ASSETS_DESC')
    name: str = 'asset'
    key: str = 'DRS_DATA_ASSETS'
    argname: str = 'assetsdir'

    def __init__(self, params):
        """
        Construct the assets block path (default data supplied with apero)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=False,
                         logging=False)
        self.has_obs_dirs = False


class PlotPath(BlockPath):

    description: lang.Text = textentry('DATA_PLOT_DESC')
    name: str = 'plot'
    key: str = 'DRS_DATA_PLOT'
    argname: str = 'plotdir'

    def __init__(self, params):
        """
        Construct the plot block path (default data supplied with apero)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=False,
                         logging=False)
        self.has_obs_dirs = False


class RunPath(BlockPath):

    description: lang.Text = textentry('DATA_RUN_DESC')
    name: str = 'run'
    key: str = 'DRS_DATA_RUN'
    argname: str = 'rundir'

    def __init__(self, params):
        """
        Construct the run block path (default data supplied with apero)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=False,
                         logging=False)
        self.has_obs_dirs = False


class LogPath(BlockPath):

    description: lang.Text = textentry('DATA_LOG_DESC')
    name: str = 'msg'
    key: str = 'DRS_DATA_MSG'
    argname: str = 'logdir'

    def __init__(self, params):
        """
        Construct the log block path (default data supplied with apero)

        :param params: ParamDict, the parameter dictionary of constants
        """
        super().__init__(params, self.name, self.key, indexing=False,
                         logging=False)
        self.has_obs_dirs = False


# define the block kinds as a list of classes
BLOCKS = [RawPath, TmpPath, ReducedPath, CalibPath, TelluPath, OutPath,
          AssetPath, PlotPath, RunPath, LogPath]


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
