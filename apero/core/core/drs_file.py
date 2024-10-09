#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO DrsPath and DrsInputFile functionality

Mostly classes to support the path and input file definitions

Created on 2019-01-19 at 12:03

@author: cook

Import rules:

- apero.base.*
- apero.lang.*
- apero.core.core.drs_misc
- apero.core.core.drs_text
- apero.core.core.drs_exceptions
- apero.io.drs_fits
- apero.math.*

    do not import from core.utils.drs_recipe
    do not import from core.core.drs_argument
"""
import os
import string
import textwrap
import time
import warnings
from collections import OrderedDict
from copy import deepcopy
from hashlib import blake2b
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np
import pandas as pd
from astropy.table import Table, vstack
from scipy.stats import pearsonr

from apero.base import base
from apero.base import drs_base
from apero.core.constants import param_functions
from apero.core.constants import constant_functions
from apero.core.constants import load_functions
from apero.core.instruments.default import instrument as instrument_mod
from apero.base import drs_lang
from apero.core import math as mp
from apero.core.constants import path_definitions as pathdef
from apero.core.base import drs_exceptions
from apero.core.base import drs_base_classes as base_class
from apero.core.base import drs_text
from apero.core.base import drs_misc
from apero.core.core import drs_out_file as out
from apero.core.base import drs_log
from apero.io import drs_fits
from apero.io import drs_path
from apero.io import drs_table

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_file.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get display func
display_func = drs_misc.display_func
# get time object
Time = base.Time
# alias pcheck
pcheck = param_functions.PCheck()
# get parameter dictionary
ParamDict = param_functions.ParamDict
# Get the logger
WLOG = drs_log.wlog
# get header classes from io.drs_fits
Header = drs_fits.Header
FitsHeader = drs_fits.fits.Header
# Get the text types
textentry = drs_lang.textentry
Text = drs_lang.Text
# recipe control path
INSTRUMENT_PATH = base.CONST_PATH
CORE_PATH = base.CORE_PATH
PDB_RC_FILE = base.PDB_RC_FILE
# get Keyword instance
Keyword = constant_functions.Keyword
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
DrsCodedWarning = drs_exceptions.DrsCodedWarning
# get header comment card from drs_fits
HCC = drs_fits.HeaderCommentCards
# get default psuedo constants class
Instrument = instrument_mod.Instrument
# get numpy masked constant
MaskedConstant = np.ma.core.MaskedConstant
# Get pandas like database class
PandasLikeDatabase = base_class.PandasLikeDatabaseDuckDB
# -----------------------------------------------------------------------------
# define complex typing
QCParamList = Union[Tuple[List[str], List[Any], List[str], List[int]],
List[Union[List[str], List[int], List[Any]]]]
# -----------------------------------------------------------------------------
# path definitions
BlockPath = pathdef.BlockPath
# get out file class
OutFileTypes = Union[out.OutFile, out.GeneralOutFile, out.NpyOutFile,
out.DebugOutFile, out.BlankOutFile, out.CalibOutFile,
out.RefCalibOutFile, out.SetOutFile, out.LBLOutFile,
out.PostOutFile, None]
# get printable characters
printable = set(string.printable)


# =============================================================================
# Define DrsPath class
# =============================================================================
class DrsPath:
    blocks: List[BlockPath] = None
    classname: str = 'DrsPath'

    def __init__(self, params: ParamDict,
                 abspath: Union[Path, str, None] = None,
                 block_kind: Union[str, None] = None,
                 block_path: Union[str, None] = None,
                 obs_dir: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 _update: bool = True,
                 check: bool = True):
        """
        Class for controlling paths in the drs (and sorting them into raw,
        tmp, reduced etc)

        :param params: ParamDict, parameter dictionary of constants
        :param abspath: str, the absolute path
        :param block_kind: str, the block kind (e.g. raw/tmp/red)
        :param block_path: str, the path to the block kind
        :param obs_dir: str, the observation directory
        """
        self.params = params

        # define properties once block kind is set
        self.block_name = None
        self.block_fileset = None
        # absolute path must be a real path (not a symbolic link)
        if abspath is not None:
            self.abspath = abspath
        else:
            self.abspath = None
        self.block_kind = block_kind
        self.block_path = block_path
        self.block_has_obs = False
        self.obs_dir = obs_dir
        self.basename = basename
        # tell the user what kind of path this is
        #  1. block: abspath = block_path
        #            block_kind set
        #            obs_dir, basename not set
        #  2. obs:   abspath = block_path + obs_dir
        #            block_kind, obs_dir set
        #            basename not set
        #  3. base:  abspath = block_path + obs_dir + filename
        #            block_kind, obs_dir, basename set
        self.path_kind = None
        # set up the directories
        self.blocks = self.get_blocks(params, check=check)
        # update kind dir and sub dir
        if _update:
            self.update()

    @staticmethod
    def get_blocks(params: ParamDict, check: bool = True) -> List[BlockPath]:
        """
        Definition of blocks (return as list)

        :param params: ParamDict, parameter dictionary of constants
        :param check: bool, if True raises exception when path does not
                      exist on disk
        :return:
        """
        blocks = []
        for block in pathdef.BLOCKS:
            blocks.append(block(params, check=check))

        return blocks

    @staticmethod
    def get_block_names(blocks: Union[List[BlockPath], None] = None,
                        params: Union[ParamDict, None] = None,
                        block_filter: Union[str, None] = None) -> List[str]:
        """
        Get the block names

        :param blocks: List of BlockPath instances (i.e. self.blocks) or None
        :param params: ParamDict, when we don't have blocks require params
        :param block_filter: str, either 'indexing' or 'logging', whether we
                             should filter block kinds by a specific type

        :return: list of strings, the block names
        """
        if blocks is None:
            if params is not None:
                blocks = DrsPath.get_blocks(params)
            else:
                raise ValueError('params must be given when class not '
                                 'constructed')
        # get blocks
        names = []
        for block in blocks:
            # deal with block filter
            if block_filter is not None:
                # if block filter is an attribute of block
                if hasattr(block, block_filter):
                    # if this attribute is True then add to names
                    if getattr(block, block_filter):
                        names.append(block.name)
            # if we don't have a block filter just add all blocks
            else:
                names.append(block.name)
        return names

    @staticmethod
    def strip_path(params: ParamDict, path: str) -> Tuple[str, bool]:
        """
        Strip a path of any block path and return that stripped directory

        :param params: ParamDict, parameter dictionary of constants
        :param path: str, path to strip

        :return: tuple, 1. the stripped path (sub-dir), 2. whether path was
                 stripped
        """
        # get all blocks
        blocks = DrsPath.get_blocks(params)
        # loop around blocks
        for block in blocks:
            blockpath = block.path
            if not blockpath.endswith(os.sep):
                blockpath = blockpath + os.sep
            if path.startswith(blockpath):
                return path.replace(blockpath, ''), True
        else:
            return path, False

    def __str__(self) -> str:
        """
        String representation of DrsPath

        :return:
        """
        # get the basic name
        _str = 'DrsPath'
        # add the block kind (if set)
        if self.block_kind is not None:
            _str += '[{0}]'.format(self.block_kind.upper())
        else:
            _str += '[]'
        # add the path kind (if set)
        if self.path_kind is not None:
            _str += '[{0}]'.format(self.path_kind.upper())
        return _str

    def __repr__(self) -> str:
        """
        String representation of DrsPath

        :return:
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

    def copy(self) -> 'DrsPath':
        """
        Copy the DrsPath
        :return:
        """
        new = DrsPath(self.params, self.abspath, self.block_kind,
                      self.block_path, self.obs_dir, self.basename)
        return new

    def update(self, obs_dir: Union[str, None] = None,
               basename: Union[str, None] = None):
        """
        Update values (if one changes others may change)
        :return:
        """
        # set function name
        func_name = drs_misc.display_func('update', __NAME__, self.classname)
        # deal with updating parameters
        if obs_dir is not None:
            self.obs_dir = obs_dir
        if basename is not None:
            self.basename = basename
        # need to clean up obs_dir (should not contain block path or path from
        #   block kind)
        self._clean_obs_dir()
        # update absolute path
        self._update_abspath()
        # if we have absolute path use it
        if self.abspath is not None:
            self._from_abspath()
        # if we have block path use it
        elif self.block_path is not None:
            self._from_block_path()
        # if we have block kind use it
        elif self.block_kind is not None:
            self._from_block_kind()
        # else we have a problem
        else:
            # log error: DrsPath requires at least abspath/block_kind/block_name
            emsg = textentry('00-004-00007')
            raise DrsCodedException('00-004-00007', message=emsg, level='error',
                                    func_name=func_name)
        # now we have block kind we can set other properties
        for block in self.blocks:
            if self.block_kind.lower() == block.name.lower():
                # set the block name
                self.block_name = block.name.lower()
                # set the block file set
                self.block_fileset = block.fileset

    def block_names(self) -> List[str]:
        """
        Get a list of block names
        :return:
        """
        return self.get_block_names(blocks=self.blocks)

    def blocks_with_obs_dirs(self) -> List[str]:
        """
        Get all block names that have obs_dirs
        :return:
        """
        names = []
        for block in self.blocks:
            if block.has_obs_dirs:
                names.append(block.name)
        return names

    def to_path(self) -> Path:
        """
        Get the path instance for the absolute path
        :return:
        """
        # set function name
        func_name = drs_misc.display_func('to_path', __NAME__, self.classname)
        # deal with abspath not set
        if self.abspath is not None:
            return Path(self.abspath)
        else:
            # Log error: DrsPath does not have absolute path set
            emsg = textentry('00-004-00008')
            raise DrsCodedException('00-004-00008', message=emsg, level='error',
                                    func_name=func_name)

    def _clean_obs_dir(self):
        """
        obs dir should not be a full path (i.e. should not contain
        block_path or a path coming from block kind)

        thus we need to clean obs dir before the next steps

        :return:
        """
        # don't clean if not set
        if self.obs_dir is None:
            return
        # if we have block_kind
        if self.block_kind is not None:
            # set block path from block kind
            _ = self._set_block_path_from_block_kind()
        # remove block path from obs_dir
        if self.block_path is not None:
            # if we have block path remove it from obs_dir
            if self.block_path in self.obs_dir:
                # get the length of the block path
                blen = len(self.block_path)
                # take off the start of obs dir
                obs_dir = self.obs_dir[blen:]
                # make sure obs dir does not start with the os separator
                while obs_dir.startswith(os.sep):
                    obs_dir = obs_dir[1:]

    def _update_abspath(self):
        """
        Assuming obs dir is clean make the absolute path if:
        1. block path, obs dir are set and basename is None
        2. block path, obs dir and basename are set

        else abspath is not updated
        :return:
        """
        if self.obs_dir is not None or self.basename is not None:
            if self.obs_dir is None:
                return
            elif self.basename is None and self.block_path is not None:
                self.abspath = os.path.join(self.block_path, self.obs_dir)
            elif self.block_path is not None:
                self.abspath = os.path.join(self.block_path, self.obs_dir,
                                            self.basename)

    def _from_abspath(self):
        """
        Scans through our directories and see's if abspath belongs to one of
        the block directories (defined in self.blocks)

        :return:
        """
        # set function name
        func_name = drs_misc.display_func('_from_abspath', __NAME__,
                                          self.classname)
        # deal with abspath not set
        if self.abspath is None:
            return
        # assume we haven't found directory
        found = False
        # loop around directories and see if absolute path belongs to one
        for block in self.blocks:
            # look for directory path in absolute path
            if str(block.path) in str(self.abspath):
                # set dirkind
                self.block_kind = str(block.name)
                # set dirpath
                self.block_path = str(block.path)
                # set has_obs
                self.block_has_obs = block.has_obs_dirs
                # flag that we have found directory
                found = True
                # break here (we don't need to continue)
                break
        # if we have found the directory look for sub-directory
        if found:
            # deal with abspath and dirpath being the same
            if self.abspath == self.block_path:
                self.path_kind = 'block'
                return
            # look for uncommon path
            rest = drs_misc.get_uncommon_path(self.abspath, self.block_path)
            # if we don't require obs then the rest is the basename
            if not self.block_has_obs:
                self.basename = rest
                self.path_kind = 'base'
            # else if the rest is a file we need to split between basename and
            #   obs_dir
            elif os.path.isfile(self.abspath):
                self.obs_dir = os.path.dirname(rest)
                self.basename = os.path.basename(rest)
                self.path_kind = 'base'
                return
            # else we just have obs_dir
            else:
                self.obs_dir = rest
                self.path_kind = 'obs'
                return
        else:
            # log error: DrsPath abspath = {0} must be related to a valid block
            eargs = [self.abspath]
            # add block error
            eargs += [self._blocks_error()]
            # log error
            emsg = textentry('00-004-00009', args=eargs)
            raise DrsCodedException('00-004-00009', message=emsg, level='error',
                                    func_name=func_name)

    def _blocks_error(self) -> str:
        """
        Add to block errors (emsg and eargs)

        :return: tuple, 1. updated emsg, 2. update eargs
        """
        # add the possible block types
        emsg = ''
        for block in self.blocks:
            emsg += '\n\t\t{0}: {1}'.format(block.name, block.path)
        return emsg

    def _from_block_path(self):
        """
        Set abspath and block_kind from block_path
        :return:
        """
        # set function name
        func_name = drs_misc.display_func('_from_block_path', __NAME__,
                                          self.classname)
        # deal with abspath not set
        if self.block_path is None:
            return
        # assume we haven't found directory
        found = False
        # loop around directories and see if absolute path belongs to one
        for block in self.blocks:
            if block.path == self.block_path:
                # set dirkind
                self.block_kind = str(block.name)
                # flag that we have found directory
                found = True
                # break here (we don't need to continue)
                break
        # now we want to set absolute path
        if found:
            # if we have an obs_dir and no basename add the obs_dir to the
            #     absolute path
            if self.obs_dir is not None and self.basename is None:
                self.abspath = os.path.join(str(self.block_path), self.obs_dir)
                self.path_kind = 'obs'
            # if we have a basename and a obs_dir add it to abspath
            elif self.basename is not None:
                # if we have not got a obs dir assume we don't need one
                if self.obs_dir is None:
                    self.obs_dir = ''
                self.abspath = os.path.join(str(self.block_path), self.obs_dir,
                                            self.basename)
                self.path_kind = 'base'
            # else we just have a block
            else:
                self.abspath = str(self.block_path)
                self.path_kind = 'block'
        else:
            # Log error: DrsPath: {0} is not a valid block path
            eargs = [self.block_path]
            # add block error
            eargs += [self._blocks_error()]
            # log error
            emsg = textentry('00-004-00010', args=eargs)
            raise DrsCodedException('00-004-00010', message=emsg, level='error',
                                    func_name=func_name)

    def _set_block_path_from_block_kind(self) -> bool:
        """
        Set the block path from block kind

        :return: True if block_path is set
        """
        # do not update block path if already set
        if self.block_path is not None:
            return True
        # deal with block kind not set
        if self.block_kind is None:
            return False
        # assume we haven't found directory
        found = False
        # loop around directories and see if absolute path belongs to one
        for block in self.blocks:
            if block.name.upper() == self.block_kind.upper():
                # set dirkind
                self.block_path = str(block.path)
                # flag that we have found directory
                found = True
                # break here (we don't need to continue)
                break
        # return found
        return found

    def _from_block_kind(self):
        """
        Set abspath and block_path from block_kind
        :return:
        """
        # set function name
        func_name = drs_misc.display_func('_from_block_kind', __NAME__,
                                          self.classname)
        # set block path from block kind
        found = self._set_block_path_from_block_kind()
        # now we want to set absolute path
        if found:
            # if we have an obs_dir and no basename add the obs_dir to the
            #     absolute path
            if self.obs_dir is not None and self.basename is None:
                self.abspath = os.path.join(str(self.block_path), self.obs_dir)
                self.path_kind = 'obs'
            # if we have a basename and a obs_dir add it to abspath
            elif self.basename is not None:
                # if we have not got a obs dir assume we don't need one
                if self.obs_dir is None:
                    self.obs_dir = ''
                self.abspath = os.path.join(str(self.block_path), self.obs_dir,
                                            self.basename)
                self.path_kind = 'base'
            # else we just have a block
            else:
                self.abspath = str(self.block_path)
                self.path_kind = 'block'
        else:
            # Log error: DrsPath: {0} is not a valid block kind
            eargs = [self.block_kind]
            # add block error
            eargs += [self._blocks_error()]
            # log error
            emsg = textentry('00-004-00011', args=eargs)
            raise DrsCodedException('00-004-00011', message=emsg, level='error',
                                    func_name=func_name)

    def get_block(self):
        """
        Get the block for this instances block kind

        :return:
        """
        # deal with no block kind
        if self.block_kind is None:
            return None
        # loop around blocks
        for block in self.blocks:
            if block.name == self.block_kind:
                return block


# =============================================================================
# Define File classes
# =============================================================================
class DrsInputFile:
    def __init__(self, name, filetype: str = '',
                 suffix: str = '',
                 remove_insuffix: Union[bool, None] = None,
                 prefix: str = '',
                 fibers: Union[List[str], None] = None,
                 fiber: Union[str, None] = None,
                 params: Union[ParamDict, None] = None,
                 filename: Union[str, None] = None,
                 intype: Any = None,
                 path: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 inputdir: Union[str, None] = None,
                 obs_dir: Union[str, None] = None,
                 data: Union[np.ndarray, None] = None,
                 header: Union[drs_fits.Header, None] = None,
                 fileset: Union[list, None] = None,
                 filesetnames: Union[List[str], None] = None,
                 outclass: OutFileTypes = None,
                 inext: Union[str, None] = None,
                 dbname: Union[str, None] = None,
                 dbkey: Union[str, None] = None,
                 rkeys: Union[dict, None] = None,
                 numfiles: Union[int, None] = None,
                 shape: Union[int, None] = None,
                 hdict: Union[drs_fits.Header, None] = None,
                 output_dict: Union[OrderedDict, None] = None,
                 datatype: Union[str, None] = None,
                 dtype: Union[type, None] = None,
                 is_combined: Union[bool, None] = None,
                 combined_list: Union[list, None] = None,
                 infiles: Union[list, None] = None,
                 s1d: Union[list, None] = None,
                 hkeys: Union[Dict[str, str], None] = None,
                 instrument: Optional[str] = None,
                 nosave: Optional[bool] = False,
                 description: Union[str, None] = None,
                 inpath: Union[str, None] = None,
                 required: Union[bool, None] = None):
        """
        Create a DRS Input File object

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants 
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - may be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param obs_dir: string, the observation directory of the file without
                        the filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param infiles: list, the list of input files (if output file)
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys:  passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        :param instrument: str, the instrument this file definition is for
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality
        :param required: bool, if True this file is always expectedt to exist
                         if recipe ran correctly

        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # set class name
        self.class_name = 'DrsInputFile'
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # define a name
        self.name = name
        # define the extension
        self.filetype = filetype
        self.suffix = suffix
        self.remove_insuffix = remove_insuffix
        self.prefix = prefix
        self.filename = filename
        self.intype = intype
        self.description = description
        # get fiber type (if set)
        self.fibers = fibers
        self.fiber = fiber
        # allow instance to be associated with a set of parameters
        self.params = params
        # set empty file attributes
        self.filename = filename
        self.path = path
        self.basename = basename
        self.inputdir = inputdir
        self.obs_dir = obs_dir
        self.data = data
        self.header = header
        if fileset is None:
            self.fileset = []
        else:
            self.fileset = fileset
        if filesetnames is None:
            self.filesetnames = []
        else:
            self.filesetnames = filesetnames
        self.outclass = outclass

        # following keys are not used in this class
        self.inext = inext
        self.dbname = dbname
        self.dbkey = dbkey
        if rkeys is None:
            self.required_header_keys = dict()
        else:
            self.required_header_keys = rkeys
        self.numfiles = numfiles
        self.shape = shape
        self.hdict = hdict
        # get the storage dictionary for output parameters
        if output_dict is None:
            self.output_dict = OrderedDict()
        else:
            self.output_dict = output_dict
        self.datatype = datatype
        self.dtype = dtype
        self.is_combined = is_combined
        self.combined_list = combined_list
        if infiles is None:
            self.infiles = []
        else:
            self.infiles = infiles
        self.s1d = s1d
        # just set hkeys
        self.header_keys = hkeys
        # set the instrument
        self.instrument = instrument
        # allow instance to be associated with a filename
        self.set_filename(filename)
        # set the inpath (used to force finding an input file only)
        self.inpath = inpath
        # set a flag that no save is active
        self.nosave = nosave
        # required flag
        if required is None:
            self.required = True
        else:
            self.required = required

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

    def __str__(self) -> str:
        """
        Defines the str(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        # _ = display_func('__str__', __NAME__, self.class_name)
        # return the string representation of DrsInputFile
        return '{0}[{1}]'.format(self.class_name, self.name)

    def __repr__(self) -> str:
        """
        Defines the print(DrsInputFile) return for DrsInputFile

        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        # _ = display_func('__repr__', __NAME__, self.class_name)
        # return the string representation of DrsInputFile
        return 'DrsInputFile[{0}]'.format(self.name)

    def summary(self, params: ParamDict,
                pconst: Optional[Instrument]) -> Dict[str, str]:
        """
        Create a dictionary sumamry representation of the file definition

        :param params: ParamDict, the paramater dictionary of constants
        :param pconst: PseudoConst, the psuedo constants class

        :return: dictionary, the parameters that define this file definition
        """
        # deal with no pconst given
        if pconst is None:
            pconst = load_functions.load_pconfig()
        # ---------------------------------------------------------------------
        # get header columns
        header_columns = list(pconst.FILEDEF_HEADER_KEYS())
        header_names = []
        # ---------------------------------------------------------------------
        # get real names for header columns
        for hdr_col in header_columns:
            if hdr_col in params:
                header_names.append(params[hdr_col][0])
            else:
                header_names.append(hdr_col)
        # ---------------------------------------------------------------------
        # construct all columns
        columns = []
        values = []
        # ---------------------------------------------------------------------
        # add name
        columns.append('name')
        values.append(self.name)
        # ---------------------------------------------------------------------
        # add description
        columns += ['description']
        if self.description is not None:
            values.append(self.description)
        else:
            values.append('--')
        # ---------------------------------------------------------------------
        # add header columns
        for it, hdr_col in enumerate(header_columns):
            columns.append('HDR[{0}]'.format(header_names[it]))
            if hdr_col in self.required_header_keys:
                values.append(self.required_header_keys[hdr_col])
            else:
                values.append('--')
        # ---------------------------------------------------------------------
        # add file type and suffix
        columns += ['file type', 'suffix']
        if drs_text.null_text(self.filetype, ['None', '', 'Null']):
            values.append('--')
        else:
            values.append(self.filetype)
        if drs_text.null_text(self.suffix, ['None', '', 'Null']):
            values.append('--')
        else:
            values.append(self.suffix)
        # ---------------------------------------------------------------------
        # add basename
        columns += ['basename']
        if self.basename is None:
            values.append('--')
        else:
            values.append(self.basename)
        # ---------------------------------------------------------------------
        # add fibers
        columns += ['fibers']
        if self.fibers is not None:
            values.append(', '.join(self.fibers))
        else:
            values.append('--')
        # ---------------------------------------------------------------------
        # add database columns
        columns += ['dbname', 'dbkey']
        if drs_text.null_text(self.dbname, ['None', '', 'Null']):
            values.append('--')
        else:
            values.append(self.dbname)
        if drs_text.null_text(self.dbkey, ['None', '', 'Null']):
            values.append('--')
        else:
            values.append(self.dbkey)
        # ---------------------------------------------------------------------
        # add input file link
        columns += ['input file']
        if self.intype is not None:
            if isinstance(self.intype, list):
                names = list(map(lambda x: x.name, self.intype))
                values.append(', '.join(names))
            elif isinstance(self.intype, DrsInputFile):
                values.append(self.intype.name)
        else:
            values.append('--')
        # ---------------------------------------------------------------------
        # return a dictionary of values
        return dict(zip(columns, values))

    def set_filename(self, filename: str):
        """
        Set the filename, basename and directory name from an absolute path

        :param filename: string, absolute path to the file

        :return None:
        """
        # set function name
        # _ = display_func('set_filename', __NAME__, self.class_name)
        # skip if filename is None
        if filename is None:
            return
        # set filename, basename and directory name
        self.filename = str(os.path.abspath(filename))
        self.basename = os.path.basename(filename)
        self.path = os.path.dirname(filename)

    def check_filename(self):
        """
        Check filename - does nothing for DrsInputFile - but classes that
        inherit from this use this method - note for DrsInputFile we
        cannot check filename - other than that it is set

        :return:
        """
        # set function name
        # _ = display_func('check_filename', __NAME__, self.class_name)
        # check that filename isn't None
        if self.filename is None:
            func = self.__repr__()
            eargs = [func, func + '.set_filename()']
            self.__error__(textentry('00-001-00002', args=eargs))

    def file_exists(self) -> bool:
        """
        Check if filename exists (normally after check_filename is set)

        :return: True if file exists
        """
        # set function name
        # _ = display_func('set_filename', __NAME__, self.class_name)
        # assume file does not exist
        found = False
        # if filename is set check filename exists
        if self.filename is not None:
            # if filename is string check filename exists
            if isinstance(self.filename, str):
                # update found
                found = os.path.exists(self.filename)
        # return whether file was found
        return found

    def set_params(self, params: ParamDict):
        """
        Set the associated parameter dictionary for the file

        :param params: ParamDict, the parameter dictionary of constants
        :return: None
        """
        # set function name
        # _ = display_func('set_params', __NAME__, self.class_name)
        # set the params
        self.params = params

    def no_save(self) -> bool:
        """
        Check for the no save special argument
        """
        # check for INPUTS in params
        if 'INPUTS' in self.params:
            # check for NOSAVE argument in inputs
            if 'NOSAVE' in self.params['INPUTS']:
                # check whether NOSAVE is set to True
                if drs_text.true_text(self.params['INPUTS']['NOSAVE']):
                    self.nosave = True
                    return True
        # it not return False
        return False

    def newcopy(self, name: Union[str, None] = None,
                filetype: Union[str, None] = None,
                suffix: Union[str, None] = None,
                remove_insuffix: Union[bool, None] = None,
                prefix: Union[str, None] = None,
                fibers: Union[List[str], None] = None,
                fiber: Union[str, None] = None,
                params: Union[ParamDict, None] = None,
                filename: Union[str, None] = None,
                intype: Any = None,
                path: Union[str, None] = None,
                basename: Union[str, None] = None,
                inputdir: Union[str, None] = None,
                obs_dir: Union[str, None] = None,
                data: Union[np.ndarray, None] = None,
                header: Union[drs_fits.Header, None] = None,
                fileset: Union[list, None] = None,
                filesetnames: Union[List[str], None] = None,
                outclass: OutFileTypes = None,
                inext: Union[str, None] = None,
                dbname: Union[str, None] = None,
                dbkey: Union[str, None] = None,
                rkeys: Union[dict, None] = None,
                numfiles: Union[int, None] = None,
                shape: Union[int, None] = None,
                hdict: Union[drs_fits.Header, None] = None,
                output_dict: Union[OrderedDict, None] = None,
                datatype: Union[str, None] = None,
                dtype: Union[type, None] = None,
                is_combined: Union[bool, None] = None,
                combined_list: Union[list, None] = None,
                infiles: Union[list, None] = None,
                s1d: Union[list, None] = None,
                hkeys: Union[Dict[str, str], None] = None,
                instrument: Optional[str] = None,
                nosave: Optional[bool] = None,
                description: Optional[str] = None,
                inpath: Union[str, None] = None):
        """
        Create a new copy of DRS Input File object - unset parameters come
        from current instance of Drs Input File

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param obs_dir: string, the observation directory of the file without
                        the filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param infiles: list, the list of input files (if output file)
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        :param instrument: str, the instrument this file definition is
                           associated with
        :param nosave: bool, if True this drs file should not be saved to disk
                       even when asking for a write function
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality

        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # set function name
        # _ = display_func('newcopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsInputFile, self, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            obs_dir, data, header, fileset, filesetnames,
                            outclass, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, infiles, s1d, hkeys,
                            instrument, nosave, description, inpath)

    def check_params(self, func):
        """
        Check that params is set - if not return an error
        :return:
        """
        # set function name
        if func is not None:
            func_name = func
        else:
            func_name = display_func('check_params', __NAME__,
                                     self.class_name)
        # ---------------------------------------------------------------------
        # check that params isn't None
        if self.params is None:
            func = self.__repr__()
            eargs = [func, self.filename, func_name]
            self.__error__(textentry('00-001-00003', args=eargs))

    def __error__(self, messages: Union[Text, str]):
        """
        Raise an Logger message (level = error)
        :param messages: string of the messages to add
        :return: None
        """
        # set function name
        # _ = display_func('__error__', __NAME__, self.class_name)
        # run the log method: error mode
        self.__log__(messages, 'error')

    def __warning__(self, messages: Union[Text, str]):
        """
        Log a Logger message (level = warning)
        :param messages:  string of the messages to add
        :return: None
        """
        # set function name
        # _ = display_func('__warning__', __NAME__, self.class_name)
        # run the log method: warning mode
        self.__log__(messages, 'warning')

    def __message__(self, messages: Union[Text, str]):
        """
        Log a Logger message (level = '')
        :param messages:  string of the messages to add
        :return:
        """
        # set function name
        # _ = display_func('__message__', __NAME__, self.class_name)
        # print and log via wlogger
        drs_base.base_printer('None', message=messages, level='')

    def __log__(self, messages: Union[Text, str], kind: str):
        """
        Generate a logger message for level = kind
        :param messages: string of the messages to add
        :param kind: str, level of the log message
        :return:
        """
        # set function name
        # _ = display_func('__log__', __NAME__, self.class_name)
        # format initial error message
        m0args = [kind.capitalize(), self.__repr__()]
        message0 = '{0}: {1} '.format(*m0args)
        # append initial error message to messages
        messages = message0 + messages
        # print and log via wlogger
        drs_base.base_printer('None', message=messages, level=kind)

    def addset(self, drsfile: Any):
        """
        For generic Input files only
        Add to a list of associated drs files (fileset) and the names to
        filesetnames

        :param drsfile: DrsInputFile, DrsFitsFile etc, file instance to add to
                        file set
        :return:
        """
        # set function name
        # _ = display_func('addset', __NAME__, self.class_name)
        # append drs file to file set
        self.fileset.append(drsfile)
        # apeend drs file name to file set name list
        self.filesetnames.append(drsfile.name)

    def copyother(self, drsfile, name: Union[str, None] = None,
                  filetype: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  fibers: Union[List[str], None] = None,
                  fiber: Union[str, None] = None,
                  params: Union[ParamDict, None] = None,
                  filename: Union[str, None] = None,
                  intype: Any = None,
                  path: Union[str, None] = None,
                  basename: Union[str, None] = None,
                  inputdir: Union[str, None] = None,
                  obs_dir: Union[str, None] = None,
                  data: Union[np.ndarray, None] = None,
                  header: Union[drs_fits.Header, None] = None,
                  fileset: Union[list, None] = None,
                  filesetnames: Union[List[str], None] = None,
                  outclass: OutFileTypes = None,
                  inext: Union[str, None] = None,
                  dbname: Union[str, None] = None,
                  dbkey: Union[str, None] = None,
                  rkeys: Union[dict, None] = None,
                  numfiles: Union[int, None] = None,
                  shape: Union[int, None] = None,
                  hdict: Union[drs_fits.Header, None] = None,
                  output_dict: Union[OrderedDict, None] = None,
                  datatype: Union[str, None] = None,
                  dtype: Union[type, None] = None,
                  is_combined: Union[bool, None] = None,
                  combined_list: Union[list, None] = None,
                  infiles: Union[list, None] = None,
                  s1d: Union[list, None] = None,
                  hkeys: Union[Dict[str, str], None] = None,
                  instrument: Optional[str] = None,
                  nosave: Optional[bool] = None,
                  description: Union[str, None] = None,
                  inpath: Union[str, None] = None):
        """
        Copy most keys from drsfile (other arguments override attributes coming
        from drfile (or self)

        :param drsfile: drs file instance, the file to copy parameters from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param obs_dir: string, the observation directory of the file without
                        the filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param infiles: list, the list of input files (if output file)
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
                               # set the instrument
        :param instrument: str, the instrument this file definition is 
                           assoicated with
        :param nosave: bool, if True this drs file should not be saved to disk
                       even when asking for a write function
        :param description: str, the description of the file (for documentation)
                :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality
        """
        # set function name
        # _ = display_func('copyother', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsInputFile, self, drsfile, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            obs_dir, data, header, fileset, filesetnames,
                            outclass, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, infiles, s1d, hkeys,
                            instrument, nosave, description, inpath)

    def completecopy(self, drsfile,
                     name: Union[str, None] = None,
                     filetype: Union[str, None] = None,
                     suffix: Union[str, None] = None,
                     remove_insuffix: Union[bool, None] = None,
                     prefix: Union[str, None] = None,
                     fibers: Union[List[str], None] = None,
                     fiber: Union[str, None] = None,
                     params: Union[ParamDict, None] = None,
                     filename: Union[str, None] = None,
                     intype: Any = None,
                     path: Union[str, None] = None,
                     basename: Union[str, None] = None,
                     inputdir: Union[str, None] = None,
                     obs_dir: Union[str, None] = None,
                     data: Union[np.ndarray, None] = None,
                     header: Union[drs_fits.Header, None] = None,
                     fileset: Union[list, None] = None,
                     filesetnames: Union[List[str], None] = None,
                     outclass: OutFileTypes = None,
                     inext: Union[str, None] = None,
                     dbname: Union[str, None] = None,
                     dbkey: Union[str, None] = None,
                     rkeys: Union[dict, None] = None,
                     numfiles: Union[int, None] = None,
                     shape: Union[int, None] = None,
                     hdict: Union[drs_fits.Header, None] = None,
                     output_dict: Union[OrderedDict, None] = None,
                     datatype: Union[str, None] = None,
                     dtype: Union[type, None] = None,
                     is_combined: Union[bool, None] = None,
                     combined_list: Union[list, None] = None,
                     infiles: Union[list, None] = None,
                     s1d: Union[list, None] = None,
                     hkeys: Union[Dict[str, str], None] = None,
                     instrument: Optional[str] = None,
                     nosave: Optional[bool] = None,
                     description: Union[str, None] = None,
                     inpath: Union[str, None] = None):
        """
        Copy all keys from drsfile (unless other arguments set - these override
        copy from drsfile)

        :param drsfile: drs file instance, the file to copy parameters from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param obs_dir: string, the observation directory of the file without
                        the filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param infiles: list, the list of input files (if output file)
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        :param instrument: str, instrument this file definition is associated
                           with
        :param nosave: bool, if True this drs file should not be saved to disk
                       even when asking for a write function
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
               in - this is in exceptional cases and overrides normal
               functionality
        """
        # set function name
        # _ = display_func('completecopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsInputFile, drsfile, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            obs_dir, data, header, fileset, filesetnames,
                            outclass, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, infiles, s1d, hkeys,
                            instrument, nosave, description, inpath)

    # -------------------------------------------------------------------------
    # file checking
    # -------------------------------------------------------------------------
    def check_another_file(self, input_file: Union['DrsInputFile']
                           ) -> Tuple[bool, Union[str, dict, None]]:
        """
        Checks that another file is consistent with this file type

        :param input_file: DrsInputFile
        :returns: True or False and the reason why (if False)
        """
        # set function name
        # _ = display_func('check_another_file', __NAME__,
        #                  self.class_name)
        # 1. check extension
        cond1, msg1 = self.has_correct_extension(input_file.inext)
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.hkeys_exist(None)
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_hkeys(None)
        if not cond2:
            return False, msg3
        # if 1, 2 and 3 pass return True
        return True, None

    def check_file(self) -> Tuple[bool, Union[str, dict, None]]:
        """
        Checks that this file is correct

        :returns: True or False and the reason why (if False)
        """
        # set function name
        # _ = display_func('check_file', __NAME__, self.class_name)
        # 1. check extension
        cond1, msg1 = self.has_correct_extension()
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.hkeys_exist()
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_hkeys()
        if not cond3:
            return False, msg3
        # if 1, 2 and 3 pass return True
        return True, None

    def has_correct_extension(self, filename: Union[str, None] = None,
                              filetype: Union[str, None] = None,
                              argname: Union[str, None] = None
                              ) -> Tuple[bool, Union[str, None]]:
        """
        Placeholder - cannot check header for DrsInputFile

        :param filename: None or filename the filename to check (if None sets
                         this from self.filename [Not used in DrsInputFile]
        :param filetype: None or file type (extension) - if None sets from
                         self.filetype [Not used in DrsInputFile]
        :param argname: str, the name of the argument we are checking the
                        extension of [Not used in DrsInputFile]

        :return: True and no reason (None)
        """
        # set function name
        # _ = display_func('has_correct_extension', __NAME__,
        #                  self.class_name)
        # do nothing
        _ = filename
        _ = filetype
        _ = argname
        # always return True and None (abstract placeholder)
        return True, None

    def hkeys_exist(self, header: Union[drs_fits.Header, None] = None,
                    filename: Union[str, None] = None,
                    argname: Union[str, None] = None) -> Tuple[bool, None]:
        """
        Placeholder - cannot check header for DrsInputFile
        always returns True and no error message

        :param header: drs_fits.Header - the header file to check
                       [Not used in DrsInputFile]
        :param filename: None or filename the filename to check (if None sets
                         this from self.filename [Not used in DrsInputFile]
        :param argname: str, the name of the argument we are checking the
                        extension of [Not used in DrsInputFile]

        :return: True and no reason (None)
        """
        # set function name
        # _ = display_func('hkeys_exist', __NAME__, self.class_name)
        # do nothing
        _ = filename
        _ = header
        _ = argname
        # always return True and None (abstract placeholder)
        return True, None

    def has_correct_hkeys(self, header: Union[drs_fits.Header, None] = None,
                          argname: Union[str, None] = None,
                          log: bool = True, filename: Union[str, None] = None,
                          ) -> Tuple[bool, Union[dict, None]]:
        """
        Placeholder - cannot check header for DrsInputFile

        :param header: drs_fits.Header - the header file to check
                       [Not used in DrsInputFile]
        :param argname: str, the name of the argument we are checking the
                        extension of [Not used in DrsInputFile]
        :param log: bool, log checking [Not used in DrsInputFile]
        :param filename: None or filename the filename to check (if None sets
                         this from self.filename [Not used in DrsInputFile]
                         
        :return: True and no reason (None)
        """
        # set function name
        # _ = display_func('has_correct_hkeys', __NAME__, self.class_name)
        # do nothing
        _ = filename
        _ = header
        _ = argname
        _ = log
        # always return True and None (abstract placeholder)
        return True, None

    # -------------------------------------------------------------------------
    # read/write methods
    # -------------------------------------------------------------------------
    def read_file(self, ext: Union[int, None] = None, check: bool = False,
                  copy: bool = False):
        """
        Does nothing - abstract at this point - cannot read a generic file

        :param ext: int or None, the data extension to open
        :param check: bool, if True checks if data is already read and does
                      not read again, to overwrite/re-read set "check" to False
        :param copy: bool, if True make sure data is copied to HDU (i.e. can
                     close after even if numpy array is still used) numpy
                     array is stored in DrsFitsFile.data
        :return None:
        """
        # set function name
        # _ = display_func('read_file', __NAME__, self.class_name)
        # do nothing else (no current read option for generic input files)
        _ = ext
        _ = check
        _ = copy

    def write_file(self, kind: str,
                   runstring: Union[str, None] = None):
        """
        Does nothing - abstract at this point - cannot write a generic file

        :return: None
        """
        # set function name
        # _ = display_func('write_file', __NAME__, self.class_name)
        # do nothing else (no current write option for generic input files)
        _ = kind, runstring

    # -------------------------------------------------------------------------
    # user functions
    # -------------------------------------------------------------------------
    def construct_filename(self, infile: Union['DrsInputFile', None] = None,
                           outfile: Union['DrsInputFile', None] = None,
                           fiber: Union[str, None] = None,
                           path: Union[str, None] = None,
                           func: Union[str, None] = None,
                           remove_insuffix: Union[bool, None] = None,
                           prefix: Union[str, None] = None,
                           suffix: Union[str, None] = None,
                           check: bool = True,
                           filename: Union[str, None] = None):
        """
        Constructs the filename from the parameters defined at instance
        definition and using the infile (if required). If check is True, checks
        the infile type against "intype". Uses "outclass" in instance definition
        to set the suffices/prefixes/fiber etc

        :param infile: Drsfile, the input DrsFile
        :param outfile: DrsFitsFile, output file - must be defined
        :param fiber: str, the fiber - must be set if infile.fibers is populated
        :param path: str, the path the file should have
        :param func: str, the function name if set (for errors)
        :param remove_insuffix: bool if set removes input suffix if not set
                                defaults to the outfile.remove_insuffix
        :param prefix: str, if set the prefix of the file (defaults to
                       outfile.prefix)
        :param suffix: str, if set the suffix of the file (defaults to
                       outfile.suffix)
        :param filename: str or None, only used for specific out fcuntions
                         (like set_file)

        :param check: bool, whether to check infile.name against self.intype

        :return: None, Sets self.filename and self.basename to the
                       correct values
        """
        # set function name
        func_name = display_func('construct_filename', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # deal with not outfile
        if outfile is None:
            outfile = self
        # if we have a function use it
        if self.outclass is not None:
            try:
                abspath = self.outclass.construct(params, infile, outfile,
                                                  fiber, path, func,
                                                  remove_insuffix, prefix,
                                                  suffix, filename)
            except DrsCodedException as e:
                level = e.get('level', 'error')
                eargs = e.get('targs', None)
                emsg = textentry(e.codeid, args=eargs)
                raise DrsCodedException(e.codeid, level=level, targs=eargs,
                                        message=emsg, func_name=func_name)
            self.filename = abspath
            self.basename = os.path.basename(abspath)
        # else raise an error
        else:
            eargs = [self.__repr__(), func_name]
            emsg = textentry('00-008-00004', args=eargs)
            raise DrsCodedException('00-008-00004', level='error', targs=eargs,
                                    message=emsg, func_name=func_name)
        # check that we are allowed to use infile (if set)
        if infile is not None and check:
            if self.intype is not None:
                # get required names
                reqfiles = self.generate_reqfiles()
                reqstr = ' or '.join(reqfiles)
                # see if infile is in reqfiles
                if infile.name not in reqfiles:
                    eargs = [infile.name, reqstr, self.filename, func_name]
                    emsg = textentry('00-008-00017', args=eargs)
                    raise DrsCodedException('00-008-00017', level='error',
                                            targs=eargs, message=emsg,
                                            func_name=func_name)

    def generate_reqfiles(self) -> List[str]:
        """
        Takes DrsInputFile.intype and works out all the combinations of
        file names that are valid for this "intype" (i.e. if we have a
        fileset in one of the "intypes" we should add all files from this set)

        :return: list of DrsInputFile names (drsfile.name) to know which names
                 are valid
        :rtype list:
        """
        # set function name
        # _ = display_func('generate_reqfiles', __NAME__,
        #                  self.class_name)
        # deal with intype being unset
        if self.intype is None:
            return []
        # set out list storage
        required_names = []
        # deal with having a list of files
        if isinstance(self.intype, list):
            # loop around intypes
            for intype in self.intype:
                # deal with intype having fileset (set of files associated
                #   with this file)
                if len(intype.filesetnames) != 0:
                    required_names += list(intype.filesetnames)
                    required_names.append(intype.name)
                else:
                    required_names.append(intype.name)
        elif isinstance(self.intype, DrsInputFile):
            intype = self.intype
            # deal with intype having fileset (set of files associated
            #   with this file)
            if len(intype.filesetnames) != 0:
                required_names += list(intype.filesetnames)
                required_names.append(intype.name)
            else:
                required_names.append(intype.name)
        # clean up required name list by only keeping unique names
        required_names = list(np.unique(required_names))
        # return required names
        return required_names

    def reconstruct_filename(self, outext: Union[str, None] = None,
                             prefix: Union[str, None] = None,
                             suffix: Union[str, None] = None,
                             inext: Union[str, None] = None,
                             fiber: Union[str, None] = None):
        """
        Reconstructs the output filename based on the current filename (that is
        then striped back to the original input file name) and then added
        based on the input settings

        remove is based on the current DrsInputFile.filename,
        DrsInputFile.basename, DrsInputFile.prefix, DrsInputFile.suffix,
        DrsInputFile.fiber, DrsInputFile.filetype

        :param outext: str, the outfile extension (to add)
        :param prefix: str, if set the prefix of the file
        :param suffix: str, if set the suffix of the file
        :param inext: str, the infile extension (to remove)
        :param fiber: str, the fiber to add (if set)

        :return: None, updates DrsInputFile.filename,  DrsInputFile.basename,
                 DrsInputFile.prefix, DrsInputFile.suffix, DrsInputFile.fiber,
                 DrsInputFile.inext
        """
        # set function name
        func_name = display_func('reconstruct_filename', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        _ = self.params
        # get current path and filename
        currentpath = os.path.dirname(self.filename)
        currentfile = self.basename
        # ----------------------------------------------------------------------
        # deal with non set value
        if prefix is None:
            prefix = self.prefix
        if suffix is None:
            suffix = self.suffix
        if inext is None:
            inext = self.filetype
        if fiber is None:
            fiber = self.fiber
        # ----------------------------------------------------------------------
        # create infilename
        # ----------------------------------------------------------------------
        # remove inext
        if self.inext is not None and currentfile.endswith(self.inext):
            currentfile = currentfile[:-len(self.inext)]
        # remove fiber
        if self.fiber is not None and currentfile.endswith('_' + self.fiber):
            currentfile = currentfile[:-len('_' + self.fiber)]
        # remove prefix
        if self.prefix is not None and currentfile.startswith(self.prefix):
            currentfile = currentfile[len(self.prefix):]
        # remove suffix
        if self.suffix is not None and currentfile.endswith(self.suffix):
            currentfile = currentfile[:-len(self.suffix)]
        # add back the inext
        if inext is not None and not currentfile.endswith(inext):
            currentfile = currentfile + inext
        # ----------------------------------------------------------------------
        # get re-constructed out file name
        outfilename = out.get_outfilename(currentfile, prefix, suffix,
                                          inext, outext, fiber)
        # ----------------------------------------------------------------------
        # update self
        self.prefix = prefix
        self.suffix = suffix
        self.inext = inext
        self.fiber = fiber
        self.filename = os.path.join(currentpath, outfilename)
        self.basename = outfilename

    def output_dictionary(self, block_kind: str,
                          runstring: Union[str, None] = None):
        """
        Generate the output dictionary (for use while writing)
        Uses OUTPUT_FILE_HEADER_KEYS and DrsFile.hdict to generate an
        output dictionary for this file (for use in indexing)

        Requires DrsFile.filename and DrsFile.params to be set

        :return None:
        """
        # set function name
        func_name = display_func('output_dictionary', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        pconst = load_functions.load_pconfig()
        # get required keys for index database
        iheader_cols = pconst.FILEINDEX_HEADER_COLS()
        hkeys = list(iheader_cols.names)
        # htypes = list(iheader_cols.dtypes)
        # deal with absolute path of file
        self.output_dict['ABSPATH'] = str(self.filename)
        # deal with night name of file
        self.output_dict['OBS_DIR'] = str(self.params['OBS_DIR'])
        # deal with basename of file
        self.output_dict['FILENAME'] = str(self.basename)
        # deal with kind
        self.output_dict['BLOCK_KIND'] = str(block_kind)
        # deal with last modified time for file
        if Path(self.filename).exists():
            last_mod = Path(self.filename).lstat().st_mtime
            used = 1
        else:
            last_mod = np.nan
            used = 0
        self.output_dict['LAST_MODIFIED'] = last_mod
        # deal with the run string (string that can be used to re-run the
        #     recipe to reproduce this file)
        if runstring is None:
            self.output_dict['RUNSTRING'] = 'None'
            # deal with recipe
            self.output_dict['RECIPE'] = 'Unknown'
        else:
            self.output_dict['RUNSTRING'] = str(runstring)
            # deal with recipe
            self.output_dict['RECIPE'] = str(runstring).split()[0]
        # add the infiles
        self.output_dict['INFILES'] = '|'.join(self.infiles)
        # add whether this row should be used be default (always 1)
        #    if file does not exist we do set this to zero though (as a flag)
        self.output_dict['USED'] = used
        # add the raw fix (all files here should be raw fixed)
        self.output_dict['RAWFIX'] = 1
        # loop around the keys and find them in hdict (or add null character if
        #     not found)
        for it, key in enumerate(hkeys):
            # no header for npy files
            self.output_dict[key] = 'None'


class DrsFitsFile(DrsInputFile):
    def __init__(self, name, filetype: str = '.fits',
                 suffix: str = '',
                 remove_insuffix: Union[bool, None] = None,
                 prefix: str = '',
                 fibers: Union[List[str], None] = None,
                 fiber: Union[str, None] = None,
                 params: Union[ParamDict, None] = None,
                 filename: Union[str, None] = None,
                 intype: Any = None,
                 path: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 inputdir: Union[str, None] = None,
                 obs_dir: Union[str, None] = None,
                 data: Union[np.ndarray, None] = None,
                 header: Union[drs_fits.Header, None] = None,
                 fileset: Union[list, None] = None,
                 filesetnames: Union[List[str], None] = None,
                 outclass: Union[Any, None] = None,
                 inext: Union[str, None] = '.fits',
                 dbname: Union[str, None] = None,
                 dbkey: Union[str, None] = None,
                 rkeys: Union[dict, None] = None,
                 numfiles: Union[int, None] = 0,
                 shape: Union[tuple, None] = None,
                 hdict: Union[drs_fits.Header, None] = None,
                 output_dict: Union[OrderedDict, None] = None,
                 datatype: Union[str, None] = 'image',
                 dtype: Union[type, None] = None,
                 is_combined: Union[bool, None] = False,
                 combined_list: Union[list, None] = None,
                 infiles: Union[list, None] = None,
                 s1d: Union[list, None] = None,
                 hkeys: Union[Dict[str, str], None] = None,
                 instrument: Optional[str] = None,
                 nosave: Optional[bool] = False,
                 description: Union[str, None] = None,
                 inpath: Union[str, None] = None,
                 required: Union[bool, None] = None):
        """
        Create a DRS Input File object

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param obs_dir: string, the observation directory of the file without
                        the filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the
        :param inext: str, the input file extension
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric)
        :param dbkey: str, the database key
        :param rkeys: dict, the required header keys
        :param numfiles: int, the number of files represented by this file
                         instance
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on writing
        :param output_dict: dict, storage for data going to index database
        :param datatype: str, the fits image type 'image' or 'header'
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits images)
        :param is_combined: bool, if True this file represents a combined set
                            of files
        :param combined_list: list, the list of combined files that make this
                              file instance
        :param infiles: list, the list of input files (if output file)
        :param s1d: list, a list of s1d images attached to this file instance
                    (for use with extraction file instances)

        :param hkeys: passed to required header keys (i.e. must be a DRS
                      Header key reference -- "KW_HEADERKEY")
        :param instrument: str, the instrument this file definition is for
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality
        :param required: bool, if True this file is always expectedt to exist
                         if recipe ran correctly

        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # set class name
        self.class_name = 'DrsFitsFile'
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # define a name
        self.name = name
        # get super init
        DrsInputFile.__init__(self, name, filetype, suffix, remove_insuffix,
                              prefix, fibers, fiber, params, filename, intype,
                              path, basename, inputdir, obs_dir, data, header,
                              fileset, filesetnames, outclass, inext, dbname,
                              dbkey, rkeys, numfiles, shape, hdict,
                              output_dict, datatype, dtype, is_combined,
                              combined_list, infiles, s1d, hkeys, instrument,
                              nosave, description, inpath, required)
        # if ext in kwargs then we have a file extension to check
        self.filetype = filetype
        # set the input extension type
        self.inext = inext
        # get the input type (another DrsFitsFile that was or will be used
        #   to create this one i.e. for pp intype is a raw drs fits file,
        #   for out intype is most likely a pp drs fits file)
        self.intype = intype
        # get fiber types allowed for this drs fits file
        self.fibers = fibers
        # get the specific fiber linked to this drs fits file
        self.fiber = fiber
        # get the function used for writing output file
        self.outclass = outclass
        # get the database name (only set if intended to go into a database)
        self.dbname = dbname
        # get the raw database key name (only set if intended to go into a
        #    database) - this is the one set in constants
        self.raw_dbkey = dbkey
        # get the current database key -- this can change i.e. adding of a
        #   fiber to the end -- for the default set key see raw_dbkey
        self.dbkey = None
        if dbkey is not None:
            self.dbkey = str(dbkey)
        # add required header keys storage
        if rkeys is None:
            self.required_header_keys = dict()
        else:
            self.required_header_keys = rkeys
        # if we don't have any required keys pushed in we get these using
        #   the get_header_keys method (kwargs is passed to allow setting
        #   individual keys when drs fits instance is constructed)
        if len(self.required_header_keys) == 0:
            self.get_header_keys(hkeys)
        # get the fits data array (or set it to None)
        self.data = data
        # get the fits header (or set it to None)
        self.header = header
        # update fiber parameter from header
        if self.header is not None:
            self.fiber = self.get_hkey('KW_FIBER', dtype=str, required=False)
        # get the number of files associated with this drs fits file
        self.numfiles = numfiles
        # get the shape of the fits data array (self.data)
        self.shape = shape
        # get the hdict (header dictionary storage) that will be passed to
        #   self.header - if not passed this is set as an empty header
        #   kept separate from self.header until all keys are added
        #   (to allow clean up + checking to occur only once)
        if hdict is None:
            self.hdict = drs_fits.Header()
        else:
            self.hdict = hdict
        # get the storage dictionary for output parameters
        if output_dict is None:
            self.output_dict = OrderedDict()
        else:
            self.output_dict = output_dict
        # get the data type for this drs fits file (either image or table)
        if datatype is None:
            self.datatype = 'image'
        else:
            self.datatype = datatype
        # get the dtype internally for fits image files (i.e. float or int)
        self.dtype = None
        # get the data array (for multi-extension fits)
        self.data_array = None
        # get the name array (for multi-extension fits)
        self.name_array = None
        # get the header array (fro multi-extnesion fits)
        self.header_array = None
        # flag whether file is a combined file
        self.is_combined = is_combined
        if combined_list is None:
            self.combined_list = []
        else:
            self.combined_list = combined_list
        # list the input files (if this is an output file)
        self.infiles = []
        # list s1d files linked to this file
        if s1d is None:
            self.s1d = []
        else:
            self.s1d = s1d
        # set the required flag
        self.required = required

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

    def __str__(self) -> str:
        """
        Defines the str(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        # _ = display_func('__str__', __NAME__, self.class_name)
        # return the string output
        return self.string_output()

    def __repr__(self) -> str:
        """
        Defines the print(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        # _ = display_func('__repr__', __NAME__, self.class_name)
        # return the string output
        return self.string_output()

    def get_header_keys(self, hkeys: Union[Dict[str, str], None]):
        """
        The rest of the kwargs from dictionary, search for keys starting with
        "KW_" and push them into required_header_keys (these are used to
        identify which keys in a header are required for a fits file to be this
        file instance kind

        :param hkeys: dict, a dictionary where the values are header key values
                      to id this file instance (compared to a fits header)

        :return: None
        """
        # set function name
        # _ = display_func('get_header_keys', __NAME__,
        #                  self.class_name)
        # deal with no hkeys
        if hkeys is None:
            hkeys = dict()
        # add values to the header
        for hkey in hkeys:
            if 'KW_' in hkey.upper():
                self.required_header_keys[hkey] = hkeys[hkey]

    def newcopy(self, name: Union[str, None] = None,
                filetype: Union[str, None] = None,
                suffix: Union[str, None] = None,
                remove_insuffix: Union[bool, None] = None,
                prefix: Union[str, None] = None,
                fibers: Union[List[str], None] = None,
                fiber: Union[str, None] = None,
                params: Union[ParamDict, None] = None,
                filename: Union[str, None] = None,
                intype: Any = None,
                path: Union[str, None] = None,
                basename: Union[str, None] = None,
                inputdir: Union[str, None] = None,
                obs_dir: Union[str, None] = None,
                data: Union[np.ndarray, None] = None,
                header: Union[drs_fits.Header, None] = None,
                fileset: Union[list, None] = None,
                filesetnames: Union[List[str], None] = None,
                outclass: OutFileTypes = None,
                inext: Union[str, None] = None,
                dbname: Union[str, None] = None,
                dbkey: Union[str, None] = None,
                rkeys: Union[dict, None] = None,
                numfiles: Union[int, None] = None,
                shape: Union[int, None] = None,
                hdict: Union[drs_fits.Header, None] = None,
                output_dict: Union[OrderedDict, None] = None,
                datatype: Union[str, None] = None,
                dtype: Union[type, None] = None,
                is_combined: Union[bool, None] = None,
                combined_list: Union[list, None] = None,
                infiles: Union[list, None] = None,
                s1d: Union[list, None] = None,
                hkeys: Union[Dict[str, str], None] = None,
                instrument: Optional[str] = None,
                nosave: Optional[bool] = None,
                description: Optional[str] = None,
                inpath: Union[str, None] = None,
                required: Union[bool, None] = None):
        """
        Create a new copy of DRS Input File object - unset parameters come
        from current instance of Drs Input File

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param obs_dir: string, the observation directory of the file without
                        the filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param infiles: list, the list of input files (if output file)
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        :param instrument: str, the instrument this file definition is
                           associated with
        :param nosave: bool, if True this drs file should not be saved to disk
                       even when asking for a write function
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality
        :param required: bool, if True this file is always expectedt to exist
                         if recipe ran correctly

        - Parent class for Drs Fits File object (DrsFitsFile)
        """
        # set function name
        # _ = display_func('newcopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsFitsFile, self, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            obs_dir, data, header, fileset, filesetnames,
                            outclass, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, infiles, s1d, hkeys,
                            instrument, nosave, description, inpath, required)

    def string_output(self) -> str:
        """
        String output for DrsFitsFile. If fiber is not None this also
        contains the fiber type

        i.e. DrsFitsFile[{name}_{fiber}] or DrsFitsFile[{name}]
        :return string: str, the string to print
        """
        # set function name
        # _ = display_func('string_output', __NAME__, self.class_name)
        # if we don't have the fiber print the drs fits file string
        if self.fiber is None:
            return '{0}[{1}]'.format(self.class_name, self.name)
        # if we have the fiber add it and print the drs fits file string
        else:
            return '{0}[{1}_{2}]'.format(self.class_name, self.name, self.fiber)

    def set_required_key(self, key: str, value: Any):
        """
        Set a required key

        :param key: str, the key to set
        :param value: value to put into required keys rkeys[key] = value
        :return:
        """
        # set function name
        # _ = display_func('set_required_key', __NAME__,
        #                  self.class_name)
        # if we have a keyword (prefix 'KW_')
        if 'KW_' in key:
            # set required header keys
            self.required_header_keys[key] = value

    def copyother(self, drsfile, name: Union[str, None] = None,
                  filetype: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  fibers: Union[List[str], None] = None,
                  fiber: Union[str, None] = None,
                  params: Union[ParamDict, None] = None,
                  filename: Union[str, None] = None,
                  intype: Any = None,
                  path: Union[str, None] = None,
                  basename: Union[str, None] = None,
                  inputdir: Union[str, None] = None,
                  obs_dir: Union[str, None] = None,
                  data: Union[np.ndarray, None] = None,
                  header: Union[drs_fits.Header, None] = None,
                  fileset: Union[list, None] = None,
                  filesetnames: Union[List[str], None] = None,
                  outclass: OutFileTypes = None,
                  inext: Union[str, None] = None,
                  dbname: Union[str, None] = None,
                  dbkey: Union[str, None] = None,
                  rkeys: Union[dict, None] = None,
                  numfiles: Union[int, None] = None,
                  shape: Union[int, None] = None,
                  hdict: Union[drs_fits.Header, None] = None,
                  output_dict: Union[OrderedDict, None] = None,
                  datatype: Union[str, None] = None,
                  dtype: Union[type, None] = None,
                  is_combined: Union[bool, None] = None,
                  combined_list: Union[list, None] = None,
                  infiles: Union[list, None] = None,
                  s1d: Union[list, None] = None,
                  hkeys: Union[Dict[str, str], None] = None,
                  instrument: Optional[str] = None,
                  nosave: Optional[bool] = None,
                  description: Union[str, None] = None,
                  inpath: Union[str, None] = None,
                  required: Union[bool, None] = None):
        """
        Copy most keys from drsfile (other arguments override attributes coming
        from drfile (or self)

        :param drsfile: drs file instance, the file to copy parameters from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param obs_dir: string, the observation directory of the file without
                        the filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param infiles: list, the list of input files (if output file)
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        :param instrument: str, the instrument this file definition is
                           associated with
        :param nosave: bool, if True this drs file should not be saved to disk
                       even when asking for a write function
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
               in - this is in exceptional cases and overrides normal
               functionality
        :param required: bool, if True this file is always expectedt to exist
                         if recipe ran correctly
        """
        # set function name
        func_name = display_func('copyother', __NAME__,
                                 self.class_name)
        # check params has been set
        self.check_params(func_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsFitsFile, self, drsfile, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            obs_dir, data, header, fileset, filesetnames,
                            outclass, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, infiles, s1d, hkeys,
                            instrument, nosave, description, inpath, required)

    def completecopy(self, drsfile,
                     name: Union[str, None] = None,
                     filetype: Union[str, None] = None,
                     suffix: Union[str, None] = None,
                     remove_insuffix: Union[bool, None] = None,
                     prefix: Union[str, None] = None,
                     fibers: Union[List[str], None] = None,
                     fiber: Union[str, None] = None,
                     params: Union[ParamDict, None] = None,
                     filename: Union[str, None] = None,
                     intype: Any = None,
                     path: Union[str, None] = None,
                     basename: Union[str, None] = None,
                     inputdir: Union[str, None] = None,
                     obs_dir: Union[str, None] = None,
                     data: Union[np.ndarray, None] = None,
                     header: Union[drs_fits.Header, None] = None,
                     fileset: Union[list, None] = None,
                     filesetnames: Union[List[str], None] = None,
                     outclass: OutFileTypes = None,
                     inext: Union[str, None] = None,
                     dbname: Union[str, None] = None,
                     dbkey: Union[str, None] = None,
                     rkeys: Union[dict, None] = None,
                     numfiles: Union[int, None] = None,
                     shape: Union[int, None] = None,
                     hdict: Union[drs_fits.Header, None] = None,
                     output_dict: Union[OrderedDict, None] = None,
                     datatype: Union[str, None] = None,
                     dtype: Union[type, None] = None,
                     is_combined: Union[bool, None] = None,
                     combined_list: Union[list, None] = None,
                     infiles: Union[list, None] = None,
                     s1d: Union[list, None] = None,
                     hkeys: Union[Dict[str, str], None] = None,
                     instrument: Optional[str] = None,
                     nosave: Optional[bool] = None,
                     description: Union[str, None] = None,
                     inpath: Union[str, None] = None,
                     required: Union[bool, None] = None):
        """
        Copy all keys from drsfile (unless other arguments set - these override
        copy from drsfile)

        :param drsfile: drs file instance, the file to copy parameters from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: string, the suffix to add when making an output filename
                       from an input filename
        :param remove_insuffix: bool, if True removes input file suffix before
                       adding output file suffix
        :param prefix: string, the prefix to add when maing an output fulename
                       from an input filename
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: ParamDict, the parameter dictionary of constants
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: DrsInputFile, an DrsFile instance associated with the
                       input file that generates this file (as an output)
                       i.e. if this is a pp file the intype would be a raw file
        :param path: string, the path to save the file to (when writing)
                     this may be left blank and defaults to the recipe default
                     (recommended in most cases) - ma be relative
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: string, the input directory (associated with an input
                         file, when this is an output file)
        :param obs_dir: string, the observation directory of the file without
                        the filename (based on the fully generated filename)
        :param data: np.array - when loaded the data is stored here
        :param header: drs_fits.Header - when loaded the header is stored here
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: dict, the required header keys [not used in DrsInputFile]
        :param numfiles: int, the number of files represented by this file
                         instance [not used in DrsInputFile]
        :param shape: tuple, the numpy array shape for data (if present)
        :param hdict: drs_fits.Header - the header dictionary - temporary
                      storage key value pairs to add to header on
                      writing [not used in DrsInputFile]
        :param output_dict: dict, storage for data going to index
                      database [not used in DrsInputFile]
        :param datatype: str, the fits image type 'image' or
                         'header'  [not used in DrsInputFile]
        :param dtype: type, float or int - the type of data in the fits file
                      (mostly required for fits
                      images) [not used in DrsInputFile]
        :param is_combined: bool, if True this file represents a combined set
                            of files [not used in DrsInputFile]
        :param combined_list: list, the list of combined files that make this
                              file instance [not used in DrsInputFile]
        :param infiles: list, the list of input files (if output file)
        :param s1d: list, a list of s1d images attached to this file instance
                          (for use with extraction file
                           instances) [not used in DrsInputFile]
        :param hkeys: passed to required header keys (i.e. must be a DRS
                       Header key reference -- "KW_HEADERKEY")
                       [not used in DrsInputFile]
        :param instrument: str, the instrument this file definition is
                   associated with
        :param nosave: bool, if True this drs file should not be saved to disk
                       even when asking for a write function
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
               in - this is in exceptional cases and overrides normal
               functionality
        :param required: bool, if True this file is always expectedt to exist
                         if recipe ran correctly
        """
        # set function name
        # _ = display_func('completecopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsFitsFile, drsfile, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            obs_dir, data, header, fileset, filesetnames,
                            outclass, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, infiles, s1d, hkeys,
                            instrument, nosave, description, inpath, required)

    # -------------------------------------------------------------------------
    # file checking
    # -------------------------------------------------------------------------
    def check_file(self) -> Tuple[bool, Union[dict, str, None]]:
        """
        Checks that this file is correct

        :returns: True or False and the reason why (if False)
        """
        # set function name
        # _ = display_func('check_file', __NAME__, self.class_name)
        # 1. check extension
        cond1, msg1 = self.has_correct_extension()
        if not cond1:
            return False, msg1
        # 2. check file header keys exist
        cond2, msg2 = self.hkeys_exist()
        if not cond2:
            return False, msg2
        # 3. check file header keys are correct
        cond3, msg3 = self.has_correct_hkeys()
        if not cond3:
            return False, msg3
        # 4. check if we have a fiber defined
        self.has_fiber()
        # if 1, 2 and 3 pass return True
        return True, None

    def has_correct_extension(self, filename: Union[str, None] = None,
                              filetype: Union[str, None] = None,
                              argname: Union[str, None] = None
                              ) -> Tuple[bool, Union[str, None]]:
        """
        Check whether the filetype (file extension) is correct

        :param filename: None or filename the filename to check (if None sets
                         this from self.filename
        :param filetype: None or file type (extension) - if None sets from
                         self.filetype
        :param argname: str, the name of the argument we are checking the
                        extension of

        :return: True or False for correct extension and the reason why if False
        """
        # set function name
        func_name = display_func('has_correct_extension', __NAME__,
                                 self.class_name)
        # deal with no input extension
        if filetype is None:
            filetype = self.filetype
        # deal with no input filename
        if filename is None:
            filename = self.filename
            basename = self.basename
        else:
            basename = os.path.basename(filename)
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = textentry('40-001-00018')
        # -----------------------------------------------------------------
        # check params has been set
        self.check_params(func_name)
        # get parameters
        params = self.params
        # -----------------------------------------------------------------
        # check extension
        if filetype is None:
            msg = textentry('09-000-00003', args=[basename])
            cond = True
        elif filename.endswith(filetype):
            msg = textentry('09-000-00004', args=[basename, filetype])
            cond = True
        else:
            msg = textentry('09-000-00005', args=[basename, filetype])
            cond = False
        # if valid return True and no error
        if cond:
            dargs = [argname, os.path.basename(filename)]
            return True, msg
        # if False generate error and return it
        else:
            emsg = textentry('09-001-00006', args=[argname, filetype])
            return False, emsg

    def hkeys_exist(self, header: Union[drs_fits.Header, None] = None,
                    filename: Union[str, None] = None,
                    argname: Union[str, None] = None
                    ) -> Tuple[bool, Union[str, None]]:
        """
        Check whether the header keys exist in the header

        :param header: drs_fits.Header - the header file to check
        :param filename: None or filename the filename to check (if None sets
                         this from self.filename
        :param argname: str, the name of the argument we are checking the
                        extension of

        :return: True or False for correct header keys and the reason why
                 if False
        """
        # set function name
        func_name = display_func('hkeys_exist', __NAME__,
                                 self.class_name)
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True)
            # get header
            header = self.header
        # deal with no input filename
        if filename is None:
            basename = self.basename
        else:
            basename = os.path.basename(filename)
        # -----------------------------------------------------------------
        # check params has been set
        self.check_params(func_name)
        # get parameters
        params = self.params
        pconst = load_functions.load_pconfig()
        # get the list of allowed required header keys
        allowed_keys = pconst.FILEDEF_HEADER_KEYS()
        # get the required header keys
        rkeys = self.required_header_keys
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = textentry('40-001-00018')
        # -----------------------------------------------------------------
        # Check that required keys are in header
        for drskey in rkeys:
            # check we are allowed to use this key (by instrument definition)
            if drskey not in allowed_keys:
                eargs = [self.name, drskey, 'FILEDEF_HEADER_KEYS()',
                         ','.join(allowed_keys), func_name]
                emsg = textentry('00-006-00022', args=eargs)
                raise DrsCodedException('00-006-00022', level='error',
                                        message=emsg, targs=eargs)

            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
                source = params.sources[drskey]
            else:
                key = drskey
                source = func_name
            # deal with empty key
            if (key is None) or key == '':
                eargs = [key, drskey, source]
                emsg = textentry('00-006-00011', args=eargs)
                raise DrsCodedException('00-006-00011', level='error',
                                        message=emsg, targs=eargs)
            # check if key is in header
            if key not in header:
                eargs = [argname, key]
                emsg = textentry('09-001-00007', args=eargs)
                return False, emsg
            else:
                dargs = [argname, key, basename]
        # if we have got to this point return True (success) and no error
        #   messages
        return True, None

    def has_correct_hkeys(self, header: Union[drs_fits.Header, None] = None,
                          argname: Union[str, None] = None,
                          log: bool = True, filename: Union[str, None] = None,
                          ) -> Tuple[bool, Dict[str, tuple]]:
        """
        Check whether the header keys exist in the header

        :param header: drs_fits.Header - the header file to check
        :param filename: None or filename the filename to check (if None sets
                         this from self.filename
        :param argname: str, the name of the argument we are checking the
                        extension of
        :param log: bool, if True logs that we have correct keys

        :return: True or False for correct header keys and the reason why
                 if False, and a dictionary of header keywords where each value
                 is in the form of a tuple: (found, argname, rvalue, value)
                 where
                 - found is True or False (whether header key was found)
                 - argname is a str, the argument name this belongs to
                 - rvalue is the required value (fails if incorrect)
                 - value is value in the header
        """
        # set function name
        func_name = display_func('has_correct_hkeys', __NAME__,
                                 self.class_name)
        # -----------------------------------------------------------------
        # check params has been set
        self.check_params(func_name)
        # get parameters
        params = self.params
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True)
            # get header
            header = self.header
        # get short hand to required header keys
        rkeys = self.required_header_keys
        # -----------------------------------------------------------------
        # deal with no argument name
        if argname is None:
            argname = textentry('40-001-00018')
        # -----------------------------------------------------------------
        # search for correct value for each header key
        found = True
        # storage
        errors = dict()
        # -----------------------------------------------------------------
        # loop around required keys
        for drskey in rkeys:
            # check whether header key is in param dict (i.e. from a
            #    keywordstore) or whether we have to use the key as is
            if drskey in params:
                key = params[drskey][0]
            else:
                key = drskey
            # check that key is in header
            if key not in header:
                # set filename (for error reporting)
                if filename is None:
                    filename = self.filename
                # get error arguments
                eargs = [key, filename, func_name]
                # log error: Required header key "{0}" not found'
                emsg = textentry('00-001-00058', args=eargs)
                raise DrsCodedException('00-001-00058', level='error',
                                        message=emsg, targs=eargs)
            # get value and required value
            value = str(header[key]).strip()
            rvalue = str(rkeys[drskey]).strip()
            # check if key is valid
            if rvalue != value:
                dargs = [argname, key, rvalue]
                found = False
            else:
                dargs = [argname, key, rvalue]
            # store info
            errors[key] = (found, argname, rvalue, value)
        # return found (bool) and errors
        return found, errors

    def has_fiber(self, header: Union[drs_fits.Header, None] = None):
        """
        Checks for fiber key in header and sets self.fiber based on this key
        if fiber key not found in header self.fiber is None

        :param header: drs_fits.Header - the header file to check
        :return: None
        """
        # set function name
        func_name = display_func('has_fiber', __NAME__,
                                 self.class_name)
        # -----------------------------------------------------------------
        # check whether fiber already set (in which case ignore)
        if self.fiber is not None:
            return
        # -----------------------------------------------------------------
        # check params has been set
        self.check_params(func_name)
        # deal with no input header
        if header is None:
            # check file has been read
            self.check_read(header_only=True)
            # get header
            header = self.header
        # get parameters
        params = self.params
        # -----------------------------------------------------------------
        kw_fiber = params['KW_FIBER'][0]
        # -----------------------------------------------------------------
        # deal with fiber
        if kw_fiber in self.header:
            fiber = header[kw_fiber]
        else:
            fiber = None
        # update fiber value
        if fiber is not None:
            self.fiber = fiber

    # -------------------------------------------------------------------------
    # table checking
    # -------------------------------------------------------------------------
    # TODO: this function needs to change when using checksum
    def get_infile_outfilename(self, recipename: str,
                               infilename: Union[str, Path],
                               allowfibers: Union[List[str], str, None] = None,
                               ext: Union[str, None] = '.fits'
                               ) -> Tuple['DrsFitsFile', bool, Union[str, None]]:
        """
        Get the DrsFitsFile.intype DrsFitsFile output instance based on the
        infilename (string) and whether it is valid infilename for the intype
        i.e. if intype = ppfile  then infilename should be a pp file

        :param recipename: string, the recipe name (for error handling)
        :param infilename: string, the input file to use to create the output
                           filename
        :param allowfibers: list of strings or string, the fiber or fibers
                            allowed for the output file created
        :param ext: string, the input file filetype (i.e. a fits file)
        :returns: a tuple of three things, 1. the output DrsFitsFile instance,
                  2. whether infilename was valid for the given input file
                  (if False output DrsFitsFile may be None) 3. the output
                  filename generated (also in output DrsFitsFile.filename)
        """
        # set function name
        func_name = display_func('get_infile_outfilename',
                                 __NAME__, self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # ------------------------------------------------------------------
        # 1. need to assign an input type for our raw file
        if self.intype is not None:
            # deal with in type being list
            if isinstance(self.intype, list):
                intype = self.intype[0]
            else:
                intype = self.intype
            # get new copy
            infile = intype.newcopy(params=params)
        else:
            infile = DrsFitsFile('DRS_RAW_TEMP')
        # ------------------------------------------------------------------
        # storage of files
        chain_files = []
        # need to go back through the file history and update filename
        cintype = self.completecopy(infile)
        # loop until we have no intype (raw file)
        while cintype is not None:
            # add to chain
            chain_files.append(self.completecopy(cintype))
            if hasattr(cintype, 'intype'):
                # deal with in type being list
                if isinstance(cintype.intype, list):
                    cintype = cintype.intype[0]
                else:
                    cintype = cintype.intype
            else:
                break
        # ------------------------------------------------------------------
        # set the file name to the infilename
        filename = str(infilename)
        bottomfile = chain_files[-1]
        # now we have chain we can project file (assuming last element in the
        #   chain is the raw file)
        for cintype in chain_files[::-1][1:]:
            bottomfile.filename = filename
            bottomfile.basename = os.path.basename(filename)
            # check whether we need fiber
            if bottomfile.fibers is not None:
                fiber = allowfibers
            else:
                fiber = None
            # make sure cintype has params
            cintype.params = params
            # get out file name
            cout = cintype.check_table_filename(recipename, bottomfile,
                                                fullpath=True,
                                                allowedfibers=fiber)
            valid, outfilename = cout
            # set the filename to the outfilename
            filename = outfilename
            bottomfile = cintype
        # ------------------------------------------------------------------
        # infile is the bottom file
        infile.filename = filename
        infile.basename = os.path.basename(filename)
        infile.filetype = ext
        # ------------------------------------------------------------------
        # get outfilename (final)
        valid, outfilename = self.check_table_filename(recipename, infile,
                                                       allowfibers)
        # ------------------------------------------------------------------
        # return infile
        return infile, valid, outfilename

    def get_infile_infilename(self, filename: Union[str, None],
                              fiber: Union[str, None]) -> str:
        """
        Get an the input file from an input filename string (i.e. the input
        of an input)

        :param filename: str, the infile filename
        :param fiber: str, the fiber associated with the infile (or None)

        :return: str, the input filename for the given the infile
                 (the input of the input)
        """
        # set function name
        func_name = display_func('get_infile_infilename', __NAME__,
                                 self.class_name)
        # deal with no filename
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                # log error: Filename must be set or given
                eargs = [func_name]
                emsg = textentry('00-004-00011', args=eargs)
                raise DrsCodedException('00-004-00012', level='error',
                                        message=emsg, targs=eargs)
        # deal with fiber being set
        if fiber is not None:
            fiberstr = '_{0}'.format(fiber)
        else:
            fiberstr = ''
        # get base name
        basename = os.path.basename(filename)
        # if we have an intype we can remove a suffix
        if self.intype is not None:
            # get suffix
            suffix = self.intype.suffix
            # get extension
            if self.inext is not None:
                inext = self.inext
            else:
                inext = '.' + basename.split('.')[-1]
            # create new filename
            nargs = [basename.split(suffix)[0], suffix, fiberstr, inext]
            newfile = '{0}{1}{2}{3}'.format(*nargs)
            # return new filename
            return newfile
        else:
            # else return the original filename
            return basename

    def check_table_filename(self, recipename: str,
                             infile: 'DrsFitsFile',
                             allowedfibers: Union[List[str], str, None] = None,
                             fullpath: bool = False
                             ) -> Tuple[bool, Union[str, None]]:
        """
        Checks whether an "infile" (DrsFitsFile) is the same kind as this
        DrsFitsFile and returns the output filename (based on infile.filename)

        :param recipename: str, the recipe where this function was called
        :param infile: DrsFitsFile, the FitsFile instance to check
        :param allowedfibers: list of strings or string, the fiber or fibers
                            allowed for the output file created
        :param fullpath: bool, if True returns the absolute path, else returns
                         just the filename

        :return: tuple of length 2, 1. whether the infile is valid, 2.
                 the output path of the infile (if infile is valid else None)
        """
        # set function name
        func_name = display_func('check_table_filename', __NAME__,
                                 'DrsFitsFile')
        # get parameters
        self.check_params(func_name)
        params = self.params
        # ------------------------------------------------------------------
        # deal with fibers
        if allowedfibers is not None:
            if isinstance(allowedfibers, str):
                fibers = [allowedfibers]
            else:
                fibers = list(allowedfibers)
        elif self.fibers is None:
            fibers = [None]
        else:
            fibers = self.fibers
        # set initial value of out filename
        outfilename = infile.filename
        # loop around fibers
        for fiber in fibers:
            # 2. need to assign an output filename for out file
            if self.outclass is not None:
                try:
                    outfilename = self.outclass.construct(params,
                                                          infile=infile,
                                                          outfile=self,
                                                          fiber=fiber)
                except DrsCodedException as e:
                    level = e.get('level', 'error')
                    eargs = e.get('targs', None)
                    emsg = textentry(e.codeid, args=eargs)
                    raise DrsCodedException(e.codeid, level=level, message=emsg,
                                            targs=eargs)
            else:
                eargs = [self.name, recipename, func_name]
                emsg = textentry('09-503-00009', args=eargs)
                raise DrsCodedException('09-503-00009', level='error',
                                        message=emsg, targs=eargs)
        # ------------------------------------------------------------------
        # assume file is valid
        valid = True
        # ------------------------------------------------------------------
        # check extension
        if outfilename.endswith(self.filetype):
            # remove extension to test suffix
            filename = outfilename[:-len(self.filetype)]
        else:
            filename = None
            valid = False
            # debug log that extension was incorrect
            dargs = [self.filetype, filename]
            WLOG(params, 'debug', textentry('90-008-00004', args=dargs))

        # ------------------------------------------------------------------
        # check suffix (after extension removed)
        if (self.suffix is not None) and valid:
            # if we have no fibers file should end with suffix
            if fibers == [None]:
                if not filename.endswith(self.suffix):
                    valid = False
                    # debug log that extension was incorrect
                    dargs = [self.suffix, filename]
                    WLOG(params, 'debug', textentry('90-008-00005', args=dargs))
            # ------------------------------------------------------------------
            # if we have fibers then file should end with one of them and
            # the suffix
            elif len(fibers) > 0:
                # have to set up a new valid that should be True if any
                #  fiber is present
                valid1 = False
                # loop around fibers
                for fiber in fibers:
                    if filename.endswith('{0}_{1}'.format(self.suffix, fiber)):
                        valid1 |= True
                # if valid1 is False debug log that fibers were not found
                if not valid1:
                    dargs = [', '.join(fibers), filename]
                    WLOG(params, 'debug', textentry('90-008-00006', args=dargs))
                # put valid1 back into valid
                valid &= valid1
        # ------------------------------------------------------------------
        # return valid (True if filename is valid False otherwise)
        if fullpath:
            return valid, outfilename
        else:
            return valid, os.path.basename(outfilename)

    def check_table_keys(self, filedict: dict,
                         rkeys: Union[dict, None] = None) -> bool:
        """
        Checks whether a dictionary contains the required key/value pairs
        to belong to this DrsFile

        :param filedict: dictionary, the dictionary of key/value pairs to
                         check against rkeys (or DrsFitsFile.rkeys if unset)
        :param rkeys: dictionary or None, if set use this as DrsFitsFile.rkeys

        :return: bool, True if dictionary of keys is valid for DrsFitsFile.rkeys
        """
        # set function name
        func_name = display_func('check_table_keys', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # ------------------------------------------------------------------
        # get required keys
        if rkeys is None:
            rkeys = self.required_header_keys
        # assume file is valid
        valid = True
        # loop around required keys
        for key in rkeys:
            # key needs to be in table
            if key in filedict:
                # get rvalue
                rvalues = rkeys[key]
                # set up aux valid
                valid1 = False
                # get this value
                filedictvalue = filedict[key]
                # check if rvalue is list
                if isinstance(rvalues, str):
                    rvalues = [rvalues]
                # deal with boolean values
                elif isinstance(rvalues, bool):
                    if rvalues:
                        rvalues = '1'
                    else:
                        rvalues = '0'
                # deal with null values
                if filedictvalue in [None, 'None', '']:
                    valid1 |= True
                    continue
                # special condition on KW_OUTPUT - raw files should not be
                #   judged based on this condition
                elif key == 'KW_OUTPUT':
                    if filedictvalue.startswith('RAW_'):
                        valid1 |= True
                        continue
                # deal with masked values
                if isinstance(filedictvalue, MaskedConstant):
                    valid1 |= True
                    continue
                # make sure there are no white spaces and all upper case
                if isinstance(filedictvalue, str):
                    filedictvalue = filedictvalue.strip().upper()
                # loop around
                for rvalue in rvalues:
                    # else make sure there are no end white spaces and all
                    #   upper case for the required value
                    rvalueclean = rvalue.strip().upper()
                    # if key is in file dictionary then we should check it
                    if filedictvalue == rvalueclean:
                        valid1 |= True
                # modify valid value
                valid &= valid1
                dargs = [key, valid, filedict['OUT'], rvalues]
                WLOG(params, 'debug', textentry('90-008-00003', args=dargs))
                # if we haven't found a key the we can stop here
                if not valid:
                    return False
            else:
                # Log that key was not found
                dargs = [key, filedict['OUT'], ', '.join(list(filedict.keys()))]
                WLOG(params, 'warning', textentry('90-008-00002', args=dargs),
                     sublevel=2)
        # return valid
        return valid

    # -------------------------------------------------------------------------
    # fits file methods
    # -------------------------------------------------------------------------
    def read_file(self, ext: Union[int, None] = None, check: bool = False,
                  copy: bool = False):
        """
        Read this fits file data and header

        :param ext: int or None, the data extension to open
        :param check: bool, if True checks if data is already read and does
                      not read again, to overwrite/re-read set "check" to False
        :param copy: bool, if True make sure data is copied to HDU (i.e. can
                     close after even if numpy array is still used) numpy
                     array is stored in DrsFitsFile.data (slower but safer)

        :return None:
        """
        # set function name
        # _ = display_func('read_file', __NAME__, self.class_name)
        # check if we have data set
        if check:
            cond1 = self.data is not None
            cond2 = self.header is not None
            if cond1 and cond2:
                return True
        else:
            cond1, cond2 = False, False
        # get params
        params = self.params
        # check that filename is set
        self.check_filename()

        # get data format
        if self.datatype == 'image':
            fmt = 'fits-image'
        elif self.datatype == 'table':
            fmt = 'fits-table'
        # default to fits-image
        else:
            fmt = 'fits-image'
        # ---------------------------------------------------------------------
        # read the fits file
        # ---------------------------------------------------------------------
        # we need to decide what to load, otherwise changes made to self.data
        #   and self.header will be lost previous to this
        # if cond1 is True we just need the header
        if cond1:
            _hdr = drs_fits.readfits(params, self.filename, getdata=False,
                                     gethdr=True, fmt=fmt, ext=ext)
            dout = [self.data, _hdr]
        # if cond2 is True we just need the data
        elif cond2:
            _data = drs_fits.readfits(params, self.filename, getdata=True,
                                      gethdr=False, fmt=fmt, ext=ext)
            dout = [_data, self.header]
        # otherwise we load both
        else:
            dout = drs_fits.readfits(params, self.filename, getdata=True,
                                     gethdr=True, fmt=fmt, ext=ext)
        # deal with copying
        if copy:
            if self.datatype == 'table':
                self.data = Table(dout[0])
            else:
                self.data = np.array(dout[0])
        else:
            self.data = dout[0]
        self.header = drs_fits.Header.from_fits_header(dout[1])
        # update fiber parameter from header
        if self.header is not None:
            self.fiber = self.get_hkey('KW_FIBER', dtype=str, required=False)
        # set number of data sets to 1
        self.numfiles = 1
        # set the shape
        if (self.data is not None) and (self.datatype == 'image'):
            self.shape = self.data.shape
        elif self.data is not None:
            self.shape = [len(self.data)]

    def read_data(self, ext: Union[int, None] = None, log: bool = True,
                  copy: bool = False,
                  return_data: bool = False,
                  extname: Union[str, None] = None
                  ) -> Union[None, np.ndarray, Table]:
        """
        Read an image from DrsFitsFile.filename into DrsFitsFile.data

        :param ext: int, the extension to read
        :param log: bool, if True logs that file was read (via
                    drs_fits.readfits)
        :param copy: bool, if True copieds the data before setting it (allows
                     HDU to be closed when opening many files (slower but
                     safer)
        :param return_data: bool, if True returns data, if False updates
                            self.data
        :param extname: str, the extension name to read

        :return: None or [np.ndarray/Table] if return_data = True
        """
        # set function name
        # _ = display_func('read_data', __NAME__, self.class_name)
        # check that filename is set
        self.check_filename()
        # get params
        params = self.params
        # get data
        data = drs_fits.readfits(params, self.filename, ext=ext,
                                 extname=extname, log=log)
        # set number of data sets to 1
        self.numfiles = 1
        # assign to object
        if copy:
            if self.datatype == 'table':
                data = Table(data)
            else:
                data = np.array(data)
        # deal with returning data over update self.data
        if return_data:
            return data
        else:
            self.data = data
        # set shape
        if hasattr(self.data, 'shape'):
            self.shape = self.data.shape
        else:
            self.shape = None

    def read_header(self, ext: Union[int, None] = None, log: bool = True,
                    copy: bool = False):
        """
        Read a header from DrsFitsFile.filename into DrsFitsFile.header

        :param ext: int, the extension to read
        :param log: bool, if True logs that file was read (via
                    drs_fits.readfits)
        :param copy: bool, if True copieds the header before setting it (allows
                     HDU to be closed when opening many files (slower but
                     safer)
        :return: None
        """
        # set function name
        # _ = display_func('read_header', __NAME__, self.class_name)
        # check that filename is set
        self.check_filename()
        # get params
        params = self.params
        # get header
        header = drs_fits.read_header(params, self.filename, ext=ext, log=log)
        # assign to object
        if copy:
            self.header = drs_fits.Header(header)
        else:
            self.header = header
        # update fiber parameter from header
        if self.header is not None:
            self.fiber = self.get_hkey('KW_FIBER', dtype=str, required=False)

    def check_read(self, header_only: bool = False, data_only: bool = False,
                   load: bool = True) -> int:
        """
        Check whether data and header (from a fits file) have been read
        if load is True and they haven't been read them read them

        data is loaded into DrsFitsFile.data
        header is loaded into DrsFitsFile.header

        :param header_only: bool, if True only read/check header
        :param data_only: bool, if True only read/check data
        :param load: bool, if True load header and / or data

        :return: None
        """
        # set function name
        # _ = display_func('check_read', __NAME__, self.class_name)
        # ---------------------------------------------------------------------
        # deal with header only
        # ---------------------------------------------------------------------
        # deal with only wanting to check if header is read
        if header_only:
            if self.header is None:
                if load:
                    self.read_header()
                    return 1
                # raise exception
                func = self.__repr__()
                eargs = [func, func + '.read_file()']
                self.__error__(textentry('00-001-00004', args=eargs))
                return 0
            else:
                return 1
        # ---------------------------------------------------------------------
        # deal with data only
        # ---------------------------------------------------------------------
        if data_only:
            if self.data is None:
                if load:
                    self.read_data()
                    return 1
                # raise exception
                func = self.__repr__()
                eargs = [func, func + '.read_file()']
                self.__error__(textentry('00-001-00004', args=eargs))
                return 0
            else:
                return 1
        # ---------------------------------------------------------------------
        # deal with both data and header
        # ---------------------------------------------------------------------
        if self.header is None and self.data is None:
            self.read_file()
            return 1
        if self.header is None:
            self.read_header()
            return 1
        if self.data is None:
            self.read_data()
            return 1
        # if we get here we are good - both data and read are loaded
        return 1

    def get_data(self, copy: bool = False,
                 extensions: Union[List[int], None] = None,
                 extnames: Union[List[str], None] = None
                 ) -> Union[np.ndarray, Table, list, dict, None]:
        """
        return the data array

        :param copy: bool, if True deep copies the data
        :param extensions: None or list of ints - if set load multiple
                           extensions - in the order given
        :param extnames: None or list of strings - if set load multiple
                            extensions - in the order given

        :return: the data (numpy array or Table) or list of data from each
                 extension
        """
        # set function name
        # _ = display_func('get_data', __NAME__, self.class_name)
        # check whether extensions is populated
        if extensions is not None:
            # storage of incoming data
            datalist = []
            # loop around extensions
            for extension in extensions:
                # get this extensions data
                data = self.read_data(ext=extension, copy=copy,
                                      return_data=True)
                # add to list
                datalist.append(data)
            # return datalist
            return datalist
        # check whether extension names is populated
        if extnames is not None:
            # storage of incoming data
            datalist = dict()
            # loop around extensions
            for extname in extnames:
                # get this extensions data
                data = self.read_data(extname=extname, copy=copy,
                                      return_data=True)
                # add to list
                datalist[extname] = data
            # return datalist
            return datalist

        # check data exists
        if self.data is None:
            self.check_read(data_only=True)
        # deal with copying data
        if copy:
            if self.datatype == 'table':
                return Table(self.data)
            else:
                return np.array(self.data)
        else:
            return self.data

    def get_header(self, copy: bool = False) -> Union[drs_fits.Header, None]:
        """
        return the header

        :param copy: bool, if True deep copies the header
        :return: the header (drs_fits.Header)
        """
        # set function name
        # _ = display_func('get_header', __NAME__, self.class_name)
        # check header exists
        if self.header is None:
            self.check_read(header_only=True)
        # deal with copying header
        if copy:
            return self.header.copy()
        else:
            return self.header

    def read_multi(self, ext: Union[int, None] = None,
                   check: bool = False) -> Union[bool, None]:
        """
        Read multiple extensions from a fits file
        sets the primary ext to DrsFitsFile.data and additional ones to
        DrsFitsFile.data_array
        and similarly primary header to DrsFitsFile.header and additional ones
        to DrsfitsFile.header_array

        :param ext: int or None, the primary extension
        :param check: if True this is just a check that DrsFitsFile.data and
                      DrsFitsFile.header exist
        :return: normally just sets DrsFitsFile attributes, but if check is True
                 returns bool, True if data/header are set, False otherwise
        """
        # set function name
        # _ = display_func('read_multi', __NAME__, self.class_name)
        # check if we have data set
        if check:
            cond1 = self.data is not None
            cond2 = self.header is not None
            if cond1 and cond2:
                return True
            else:
                return False
        # get params
        params = self.params
        # check that filename is set
        self.check_filename()
        # get data format
        if ext is not None:
            rout = drs_fits.readfits(params, self.filename, getdata=True,
                                     ext=ext, gethdr=True, fmt='fits-image')
            dout, hout = rout
            names = None
        else:
            rout = drs_fits.readfits(params, self.filename, getdata=True,
                                     gethdr=True, fmt='fits-multi',
                                     return_names=True)
            dout, hout, names = rout
        # need to deal with no data in primary (should be default)
        if dout[0] is None:
            self.data = dout[1]
            self.data_array = dout[2:]
            self.name_array = names[1:]
        else:
            self.data = dout[0]
            self.data_array = dout[1:]
            self.name_array = names
        # set primary header
        self.header = drs_fits.Header.from_fits_header(hout[0])
        # update fiber parameter from header
        if self.header is not None:
            self.fiber = self.get_hkey('KW_FIBER', dtype=str, required=False)
        # set number of data sets to 1
        self.numfiles = 1
        # append headers (as copy)
        self.header_array = []
        for header in hout:
            self.header_array.append(drs_fits.Header.from_fits_header(header))
        # set the shape
        if self.data is not None:
            self.shape = self.data.shape

    def update_header_with_hdict(self):
        """
        Updates header with hdict entries
        :return:
        """

        # set function name
        # _ = display_func('update_header_with_hdict', __NAME__,
        #                  self.class_name)
        # deal with unset header
        if self.header is None:
            if isinstance(self.hdict, drs_fits.Header):
                self.header = self.hdict.copy()
                return
            self.header = drs_fits.Header()
        # add keys from hdict
        for key in self.hdict:
            # deal with COMMENT cards
            if isinstance(self.hdict[key], HCC):
                for value in str(self.hdict[key]).split('\n'):
                    self.header[key] = value
                continue
            # get value that is printable
            comment = self._only_printable(str(self.hdict.comments[key]))
            # try to set header
            try:
                # deal with NaNS
                if self.hdict[key] in [np.nan, 'nan', 'NAN']:
                    self.header[key] = ('NAN', comment)
                # just set them to  header[key] = (VALUE, COMMENT)
                else:
                    self.header[key] = (self.hdict[key], comment)
            # try to deal with FITS header values must contain standard
            # printable ASCII characters
            except ValueError as _:
                value = self._only_printable(self.hdict[key])
                self.header[key] = (value, comment)

    def _only_printable(self, value: str):
        """
        Fix for FITS header values must contain standard printable
        ASCII characters

        :param value: str, the string to enter

        :return: A string without non-ascii characters
        """
        return ''.join(filter(lambda x: x in printable, str(value)))

    def write_file(self, block_kind: str,
                   runstring: Union[str, None] = None):
        """
        Write a single Table/numpy array to disk useing DrsFitsFile.data,
        DrsFitsfile.header to write to DrsFitsFile.filename

        also used to update output_dictionary for index database

        :param block_kind: str, the kind of file (raw, tmp, red)
        :param runstring: str or None, if set sets the input run string that
                          can be used to re-run the recipe to get this output

        :return: None
        """
        # set function name
        func_name = display_func('write_file', __NAME__,
                                 self.class_name)
        # get params
        params = self.params
        # deal with no save
        if self.no_save():
            wmsg = 'NOSAVE active - file not written to disk'
            WLOG(self.params, 'warning', wmsg)
            return
        # ---------------------------------------------------------------------
        # check that filename is set
        self.check_filename()
        # copy keys from hdict into header
        self.update_header_with_hdict()
        # ---------------------------------------------------------------------
        # set extension names
        names = [None, self.name]
        # make lists of data + header (primary should not have data)
        datalist = [None, self.data]
        # header should go in primary and others should be blank
        headerlist = [self.header, None]
        # datatype list
        datatypelist = [None, self.datatype]
        # dtype list
        dtypelist = [None, self.dtype]
        # write to file
        drs_fits.writefits(params, self.filename, datalist, headerlist,
                           names, datatypelist, dtypelist, func=func_name)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary(block_kind, runstring)

    def write_multi(self, block_kind: str,
                    data_list: List[Union[Table, np.ndarray]],
                    header_list: Union[List[drs_fits.Header], None] = None,
                    name_list: Union[List[str], None] = None,
                    datatype_list: Union[List[str], None] = None,
                    dtype_list: Union[List[Union[Type, None]], None] = None,
                    runstring: Union[str, None] = None):
        """
        Write a set of Tables/numpy arrays to disk useing DrsFitsFile.data,
        DrsFitsfile.header to write to DrsFitsFile.filename
        also requires a list of addition numpy arrays/Tables (and optionally
        a list of headers) - must supply data_type list if a mix of numpy
        array and Tables (defaults to all being numpy arrays --> FitsImage)

        also used to update output_dictionary for index database

        :param block_kind: str, the kind of file (raw, tmp, red)
        :param data_list: list of numpy arrays or astropy Tables - MUST NOT
                          INCLUDE first entry (set by DrsFitsFile.data)
                          if all are numpy arrays do not need to set
                          datatype_list if mixed or Table then must set
        :param header_list: optional list of headers (not including primary
                            this is set by DrsFitsFile.header) if not set
                            these are the same as DrsFitsFile.header
        :param name_list: optional list of names for each extension
                          can be the length of data list or one larger
                          (to override name of self.data)
        :param datatype_list: list of strings (or unset) these can either be
                              'image' or 'table' and must be set for each
                            numpy array / table in the list (must be same length
                            as data list)
        :param dtype_list: list of types - if set tries to force each extension
                           to this data type (only works for numpy arrays)
                           set individual elements to None if you don't want
                           to force data type for that entry
        :param runstring: str or None, if set sets the input run string that
                          can be used to re-run the recipe to get this output

        :return: None
        """
        # set function name
        func_name = display_func('write_multi', __NAME__,
                                 self.class_name)
        # get params
        params = self.params
        # deal with no save
        if self.no_save():
            wmsg = 'NOSAVE active - file not written to disk'
            WLOG(self.params, 'warning', wmsg)
            return
        # ---------------------------------------------------------------------
        # check that filename is set
        self.check_filename()
        # copy keys from hdict into header
        self.update_header_with_hdict()
        # ---------------------------------------------------------------------
        # deal with header list being empty
        if header_list is None:
            header_list = []
            for it in range(len(data_list)):
                header_list.append(None)
        # ---------------------------------------------------------------------
        # deal with datatype_list being empty
        if datatype_list is None:
            datatype_list = []
            for it in range(len(data_list)):
                if isinstance(data_list[it], Table):
                    datatype_list.append('table')
                else:
                    datatype_list.append('image')
        # deal with dtype being empty
        if dtype_list is None:
            dtype_list = [None] * len(data_list)
        # ---------------------------------------------------------------------
        # deal with name list
        if name_list is None:
            names = [self.name] * (len(data_list) + 1)
        elif len(name_list) == len(data_list) + 1:
            names = list(name_list)
        elif len(name_list) == len(data_list):
            names = [self.name] + list(name_list)
        else:
            names = [self.name] * (len(data_list) + 1)
        # add primary hdu (no name)
        names = [None] + names
        # ---------------------------------------------------------------------
        # get data and header lists - primary should not have data
        data_list = [None, self.data] + data_list
        # variable header list tells us what should be that match up between
        #    headers and data
        if len(header_list) == len(data_list) - 2:
            header_list = [self.header, None] + header_list
        elif len(header_list) == len(data_list) - 1:
            header_list = [self.header] + header_list
        # ---------------------------------------------------------------------
        datatype_list = [None, self.datatype] + datatype_list
        dtype_list = [None, self.dtype] + dtype_list
        # writefits to file
        drs_fits.writefits(params, self.filename, data_list, header_list,
                           names, datatype_list, dtype_list, func=func_name)
        # ---------------------------------------------------------------------
        # write output dictionary
        self.output_dictionary(block_kind, runstring)

    def get_fiber(self, header: Union[drs_fits.Header, None] = None
                  ) -> Union[str, None]:
        """
        Get the fiber from the header (if it exists) - if not forcing header
        header must be loaded before using this

        :param header: None (uses DrsFitsFile.header) or force a different
                       header
        :return: str or None - if found in header returns the fiber name else
                 returns None
        """
        # set function name
        # _ = display_func('get_fiber', __NAME__, self.class_name)
        # get params
        params = self.params
        # must have fibers defined to be able to get a fiber
        if self.fibers is None:
            return None
        # get fiber header key
        key = params['KW_FIBER'][0]
        # deal with case where no header was given
        if header is None:
            if self.header is not None:
                if key in self.header:
                    return str(self.header[key])
        else:
            if key in header:
                return str(header[key])
        # if we still don't have fiber search in file name for fiber
        for fiber in self.fibers:
            if '_{0}'.format(fiber) in self.basename:
                return fiber
        # if we still don't have fiber then return None
        return None

    def output_dictionary(self, block_kind: str,
                          runstring: Union[str, None] = None):
        """
        Generate the output dictionary (for use while writing)
        Uses OUTPUT_FILE_HEADER_KEYS and DrsFile.hdict to generate an
        output dictionary for this file (for use in indexing)

        Requires DrsFile.filename and DrsFile.params to be set

        :params block_kind: str, the block kind (raw/tmp/red)
        :params runstring: str, the run string that created this recipe run

        :return None:
        """
        # set function name
        func_name = display_func('output_dictionary', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        params = self.params
        pconst = load_functions.load_pconfig()
        # get required keys for index database
        iheader_cols = pconst.FILEINDEX_HEADER_COLS()
        hkeys = list(iheader_cols.names)
        htypes = []
        for col in hkeys:
            htypes.append(iheader_cols.get_datatype(col))
        # ---------------------------------------------------------------------
        # deal with absolute path of file
        self.output_dict['ABSPATH'] = str(self.filename)
        # deal with night name of file
        self.output_dict['OBS_DIR'] = str(self.params['OBS_DIR'])
        # deal with basename of file
        self.output_dict['FILENAME'] = str(self.basename)
        # deal with kind
        self.output_dict['BLOCK_KIND'] = str(block_kind)
        # deal with last modified time for file
        if Path(self.filename).exists():
            last_mod = Path(self.filename).lstat().st_mtime
            used = 1
        else:
            last_mod = np.nan
            used = 0
        self.output_dict['LAST_MODIFIED'] = last_mod
        # deal with the run string (string that can be used to re-run the
        #     recipe to reproduce this file)
        if runstring is None:
            self.output_dict['RUNSTRING'] = 'None'
            # deal with recipe
            self.output_dict['RECIPE'] = 'Unknown'
        else:
            self.output_dict['RUNSTRING'] = str(runstring)
            # deal with recipe
            self.output_dict['RECIPE'] = str(runstring).split()[0]
        # add the infiles
        self.output_dict['INFILES'] = '|'.join(self.infiles)
        # add whether this row should be used be default (always 1)
        self.output_dict['USED'] = used
        # add the raw fix (all files here should be raw fixed)
        self.output_dict['RAWFIX'] = 1
        # ---------------------------------------------------------------------
        # loop around the keys and find them in hdict (or add null character if
        #     not found)
        for it, key in enumerate(hkeys):
            # deal with header key stores
            if key in params:
                dkey = params[key][0]
            else:
                dkey = str(key)
            # get dtype
            dtype = htypes[it]
            # set found
            found = False
            # add key if in hdict (priority)
            if (self.hdict is not None) and dkey in self.hdict:
                # noinspection PyBroadException
                try:
                    self.output_dict[key] = dtype(self.hdict[dkey])
                    found = True
                except Exception as _:
                    self.output_dict[key] = 'None'
            if (self.header is not None) and dkey in self.header and not found:
                # noinspection PyBroadException
                try:
                    self.output_dict[key] = dtype(self.header[dkey])
                    found = True
                except Exception as _:
                    self.output_dict[key] = 'None'
            if not found:
                self.output_dict[key] = 'None'

    def combine(self, infiles: List['DrsFitsFile'],
                math: Union[str, None] = 'sum',
                same_type: bool = True,
                path: Union[str, None] = None,
                test_similarity: bool = True) -> Tuple['DrsFitsFile', Table]:
        """
        Combine a set of DrsFitsFiles into a single file using the "math"
        operation (i.e. sum, mean, median etc)

        :param infiles: a list of DrsFitsFile instances, to be combined
        :param math: str, the way to mathematically combine files
                     valid options are: sum, average, mean, median, med,
                     add, +, subtract, -, divide, /, multiple, times, *
                     if none does not combine files
        :param same_type: bool, if True input DrsFitsFile must be the same
                          type (DrsFitsFile.name identical) to combine otherwise
                          exception is raised
        :param path: None or str, update the path for the output combined
                     DrsFitsFile (added to new filename)
        :param test_similarity: bool, if True tests similarity of files before
                                 combining (if False does not test)

        :return: a tuple, 1. new DrsFitsFile instance of the combined file,
                 2. the combined table
        """
        # set function name
        func_name = display_func('combine', __NAME__,
                                 self.class_name)
        # define usable math
        available_math = ['sum', 'average', 'mean', 'median', 'med',
                          'add', '+', 'subtract', '-', 'divide', '/',
                          'multiply', 'times', '*', 'None']
        # --------------------------------------------------------------------
        # check that params is set
        self.check_params(func_name)
        params = self.params
        # check that data is read
        self.check_read()
        # get combine metric types
        comb_metric_1_types = params['COMBINE_METRIC1_TYPES']
        # set new data to this files data
        data = np.array(self.data)
        # --------------------------------------------------------------------
        # cube
        datacube0 = [data]
        headers0 = [Header.from_fits_header(self.header)]
        basenames0 = [self.basename]
        # combine data into cube
        for infile in infiles:
            # check data is read for infile
            infile.check_read()
            # check that infile matches in name to self
            if (self.name != infile.name) and same_type:
                eargs = [func_name]
                raise drs_log.AperoCodedException(params, '00-001-00021',
                                                  targs=eargs)
            # add to cube
            datacube0.append(infile.data)
            basenames0.append(infile.basename)
            headers0.append(Header.from_fits_header(infile.header))
        # --------------------------------------------------------------------
        # Quality control on data
        # --------------------------------------------------------------------
        # make datacube an numpy array
        datacube0 = np.array(datacube0)

        # make a median of all files (for quality control only)
        median0 = mp.nanmedian(datacube0, axis=0)
        image1 = median0.ravel()
        # cube data (filter)
        datacube, headers = [], []
        basenames, basenames_used = [], []
        basecolnames = []
        # store count of rejected files
        reject_count = 0
        # loop around all files
        for row in range(len(datacube0)):
            # get header and basename for this row
            header = headers0[row]
            basename = basenames0[row]
            # deal with metric 1
            if not test_similarity:
                metric = np.nan
                metric_threshold = np.nan
                passed = True
            elif self.get_hkey('KW_DPRTYPE', dtype=str) in comb_metric_1_types:
                # compute metric 1
                cout = combine_metric_1(params, row, image1, datacube0)
                metric, metric_threshold, passed = cout
            # else a proxy metric - passes test
            else:
                metric = np.nan
                metric_threshold = np.nan
                passed = True
            # store metric to header
            header['CMETRIC'] = metric
            header['CTHRES'] = 'THRES {0} = {1}'.format(row, metric_threshold)
            # now for the quality control
            if not passed:
                # set header value (for table)
                header['CPASS'] = 'FILE {0} = FAILED'.format(row)
                # log warning
                wargs = [basename]
                # warning level 3: File was rejected from combining process
                WLOG(params, 'warning', textentry('10-003-00001', args=wargs),
                     sublevel=3)
                # add to reject count
                reject_count += 1
            else:
                # set header value (for table)
                header['CPASS'] = 'FILE {0} = PASSED'.format(row)
                # add database (of good data only)
                datacube.append(datacube0[row])
                # add used basenames (for DrsFitsFile)
                basenames_used.append(basename)
            # add all headers (we want to keep all information)
            headers.append(header)
            # add all basenames (for when we combine headers)
            basenames.append(basename)
            # add basename column names (no extension)
            basecolnames.append(basename.replace('.fits', ''))
        # log how many files were rejected (if any)
        if reject_count > 0:
            wargs = [reject_count]
            # warning level 4: {0} file(s) were rejected from combining process
            WLOG(params, 'warning', textentry('10-003-00002', args=wargs),
                 sublevel=4)
        # need to deal with no files left
        if len(datacube) == 0:
            # storage for stat message (pushed into error message)
            stat_str = ''
            # loop around all headers
            for it in range(len(headers)):
                # get arguments
                sargs = [basenames[it], headers[it][params['KW_DPRTYPE'][0]],
                         headers[it]['CMETRIC']]
                # build stats message for this file
                smsg = '\n\t{0} ({1}) METRIC={2}'
                stat_str += smsg.format(*sargs)
            # log error
            raise drs_log.AperoCodedException(params, '00-001-00054',
                                              targs=[stat_str])

        # --------------------------------------------------------------------
        # make data cube
        # --------------------------------------------------------------------
        # make datacube an numpy array
        datacube = np.array(datacube)
        # --------------------------------------------------------------------
        # deal with math
        # --------------------------------------------------------------------
        # log what we are doing
        WLOG(params, '', textentry('40-999-00004', args=[math]))
        # if we want to sum the data
        if math in ['sum', 'add', '+']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nansum(datacube, axis=0)
        # else if we want to subtract the data
        elif math in ['subtract', '-']:
            for im in range(1, len(datacube)):
                data -= datacube[im]
        # else if we want to divide the data
        elif math in ['divide', '/']:
            for im in range(1, len(datacube)):
                data /= datacube[im]
        # else if we want to multiple the data
        elif math in ['multiple', 'times', '*']:
            for im in range(1, len(datacube)):
                data *= datacube[im]
        # elif if mean/average
        elif math in ['average', 'mean']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nanmean(datacube, axis=0)
        # elif if median
        elif math in ['median', 'med']:
            with warnings.catch_warnings(record=True) as _:
                data = mp.nanmedian(datacube, axis=0)
        elif math in ['None', None, 'Null']:
            data = np.zeros_like(datacube[0])
        # else we have an error in math
        else:
            eargs = [math, ', '.join(available_math), func_name]
            raise drs_log.AperoCodedException(params, '00-001-00042',
                                              targs=eargs)

        # --------------------------------------------------------------------
        # Need to setup a new filename - based on all input files
        #   - this essentially is a checksum
        # --------------------------------------------------------------------
        # generate a hash based on basename
        checksum = generate_arg_checksum(basenames, 5)
        # make sure checksum is capitalized
        checksum = checksum.upper()
        # add a possible suffix from the filename
        pconst = load_functions.load_pconfig()
        suffix = pconst.COMBINE_FILE_SUFFIX(basenames, self.suffix)
        # add the checksum + the suffix + the file extension
        basename = checksum + suffix + self.inext
        # update path and filename
        if path is None:
            path = self.path
        # set the filename to the path + basename
        filename = os.path.join(path, basename)
        # --------------------------------------------------------------------
        # Need to create new header and combine header table
        # --------------------------------------------------------------------
        chout = combine_headers(params, headers, basecolnames, math)
        self.header, self.hdict, combinetable = chout

        # --------------------------------------------------------------------
        # construct keys for new DrsFitsFile
        # --------------------------------------------------------------------
        newinfile = DrsFitsFile(self.name, self.filetype, self.suffix,
                                self.remove_insuffix, self.prefix, self.fibers,
                                self.fiber, self.params, filename, self.intype,
                                path, basename, self.inputdir, self.obs_dir,
                                data, self.header, self.fileset,
                                self.filesetnames, self.outclass, self.inext,
                                self.dbname, self.dbkey,
                                self.required_header_keys, self.numfiles,
                                data.shape, self.hdict, self.output_dict,
                                self.datatype, self.dtype, True,
                                list(basenames), self.s1d)

        # return newinfile and table
        return newinfile, combinetable

    # -------------------------------------------------------------------------
    # fits file header methods
    # -------------------------------------------------------------------------
    def get_hkey(self, key, has_default=False, default=None,
                 required=True, dtype: Type = float,
                 listtype: Union[Type, None] = None) -> Any:
        """
        Looks for a key in DrsFitsFile.header, if has_default is
        True sets value of key to 'default' if not found else if "required"
        logs an error

        :param key: string, key in the dictionary to find first looks in
                            DrsFile.header directly then checks
        :param has_default: bool, if True uses "default" as the value if key
                            not found
        :param default: object, value of the key if not found and
                        has_default is True
        :param required: bool, if True key is required and causes error is
                         missing if False and key not found value is None
        :param dtype: type, the data type for output
        :param listtype: if type is a list this is the type of the list elements

        :return: the value from the header for key
        """
        # set function name
        func_name = display_func('read_header_key', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        # check that data is read
        self.check_read(header_only=True)
        # check key is valid
        drskey = self._check_key(key)
        # NIRPS-CHANGE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # deal with no drs key
        if len(drskey) == 0:
            if has_default:
                return default
            else:
                return None
        # if we have a default key try to get key else use default value
        if has_default:
            value = self.header.get(drskey, default)
        # else we must look for the value manually and handle the exception
        else:
            if drskey in self.header:
                value = self.header[drskey]
            else:
                # if we do not require this keyword don't generate an error
                #   just return None
                if not required:
                    return None
                # else generate an error
                else:
                    if key == drskey:
                        eargs = [drskey, self.filename, func_name]
                        emsg = textentry('09-000-00006', args=eargs)
                    else:
                        eargs = [drskey, self.filename, key, func_name]
                        emsg = textentry('09-000-00007', args=eargs)
                    self.__error__(emsg)
                    value = None
        # deal with booleans
        if isinstance(value, str):
            # if dtype is a bool try to push to a boolean
            if dtype == bool or dtype == 'bool':
                if value.upper() in ['1', 'TRUE', 'T']:
                    value = True
                else:
                    value = False
        # deal with input lists
        if isinstance(value, str):
            # if dtype is a list
            if dtype == list:
                # try to split the value as a list
                value = value.split(',')
                value = list(np.char.array(value).strip())
                # cast to required list type
                if listtype is not None and isinstance(listtype, type):
                    value = list(map(lambda x: listtype(x), value))
        # try to convert to dtype else just return as string
        try:
            value = dtype(value)
        except ValueError:
            value = str(value)
        except TypeError:
            value = str(value)
        # return value
        return value

    def get_hkeys(self, keys: List[str], has_default: bool = False,
                  defaults: Union[List[Any], None] = None) -> List[Any]:
        """
        Looks for a set of keys in DrsFile.header, if has_default is
        True sets value of key to 'default' if not found else if "required"
        logs an error

        :param keys: list of string, key in the dictionary to find
        :param has_default: bool, if True uses "default" as the value if key
                            not found
        :param defaults: object, value of the key if not found and
                        has_default is True

        :return value: object, value of DrsFile.header[key] or default (if
                       has_default=True)
        """
        # set function name
        func_name = display_func('read_header_keys', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        # check that data is read
        self.check_read(header_only=True)
        # make sure keys is a list
        try:
            keys = list(keys)
        except TypeError:
            self.__error__(textentry('00-001-00005', args=[func_name]))
        # if defaults is None --> list of Nones else make sure defaults
        #    is a list
        if defaults is None:
            defaults = list(np.repeat([None], len(keys)))
        else:
            try:
                defaults = list(defaults)
                if len(defaults) != len(keys):
                    self.__error__(textentry('00-001-00006', args=[func_name]))
            except TypeError:
                self.__error__(textentry('00-001-00007', args=[func_name]))
        # loop around keys and look up each key
        values = []
        for k_it, key in enumerate(keys):
            # get the value for key
            v = self.get_hkey(key, has_default, default=defaults[k_it])
            # append value to values list
            values.append(v)
        # return values
        return values

    def get_hkey_1d(self, key: str, dim1: Union[int, None] = None,
                    dtype: Type = float, start: int = 0,
                    excludes: Union[None, List[str], str] = None,
                    includes: Union[None, List[str], str] = None,
                    elogic: str = 'AND', ilogic: str = 'AND') -> np.ndarray:
        """
        Read a set of header keys that were created from a 1D list

        :param key: string, prefix of HEADER key to construct 1D list from
                     key[row number]
        :param dim1: int, the number of elements in dimension 1
                     (number of rows) if unset tries to guess number of rows
        :param dtype: type, the type to force the data to be (i.e. float, int)
        :param start: int, the start index for the 1d list (normally 0)
        :param excludes: List of strings or string, sub-strings to exclude
                         from matched header keys - requires using {} in the
                         key in place of missing text
        :param includes: List of strings or string, sub-strings to include
                         from matched header keys - requires using {} in the
                         key in place of missing text
        :param elogic: string, either 'AND' or 'OR' for combining multiple
                       excludes
        :param ilogic: string, either 'AND' or 'OR' for combining multiple
                       includes

        :return values: numpy array (1D), the values force to type = dtype
        """
        # set function name
        func_name = display_func('get_hkey_1d', __NAME__,
                                 self.class_name)
        # check that data is read
        self.check_read(header_only=True)
        # check key is valid
        drskey = self._check_key(key)
        # ------------------------------------------------------------------
        # deal with no dim1 key
        if dim1 is None:
            # use wild card to try to find keys
            wildkey = drskey.split('{')[0] + '*' + drskey.split('}')[-1]
            # use wild card in header
            rawwildvalues = list(self.header[wildkey].keys())
            # deal with includes/excludes
            ieargs = [rawwildvalues, includes, excludes, ilogic, elogic]
            wildvalues = drs_text.include_exclude(*ieargs)
            # deal with no wild card values found
            if wildvalues is None:
                eargs = [wildkey, dim1, self.basename, func_name]
                self.__error__(textentry('09-000-00008', args=eargs))
            # else get the length of dim1
            else:
                dim1 = len(wildvalues)
        # ------------------------------------------------------------------
        # create 1d list
        values = []
        # loop around the 2D array
        for it in range(start, dim1 + start):
            # construct the key name
            keyname = test_for_formatting(drskey, it)
            # try to get the values
            try:
                # set the value
                values.append(dtype(self.header[keyname]))
            except KeyError:
                eargs = [keyname, dim1, self.basename, func_name]
                self.__error__(textentry('09-000-00008', args=eargs))
                values = None
        # return values
        return np.array(values)

    def get_hkey_2d(self, key: str, dim1: int, dim2: int,
                    dtype: Type = float) -> np.ndarray:
        """
        Read a set of header keys that were created from a 2D list

        :param key: string, prefix of HEADER key to construct 2D list from
                     key[number]
               where number = (row number * number of columns) + column number
               where column number = dim2 and row number = range(0, dim1)
        :param dim1: int, the number of elements in dimension 1
                     (number of rows)
        :param dim2: int, the number of columns in dimension 2
                     (number of columns)
        :param dtype: type, the type to force the data to be (i.e. float, int)

        :return values: numpy array (2D), the values force to type = dtype
        """
        # set function name
        func_name = display_func('get_hkey_2d', __NAME__,
                                 self.class_name)
        # check that data is read
        self.check_read(header_only=True)
        # check key is valid
        drskey = self._check_key(key)
        # create 2d list
        values = np.zeros((dim1, dim2), dtype=dtype)
        # loop around the 2D array
        dim1, dim2 = values.shape
        for it in range(dim1):
            for jt in range(dim2):
                # construct the key name
                keyname = test_for_formatting(drskey, it * dim2 + jt)
                # try to get the values
                try:
                    # set the value
                    values[it][jt] = dtype(self.header[keyname])
                except KeyError:
                    eargs = [keyname, drskey, dim1, dim2, self.basename,
                             func_name]
                    self.__error__(textentry('09-000-00009', args=eargs))
        # return values
        return values

    def _check_key(self, key: str) -> str:
        """
        Checks whether a key comes from a keywordstore (stored inside parameter
        dictionary: DrsFitsFile.params)

        :param key: str, the key to check - if key is in paramdict then
                    key = params[key] - if output is a list (keyword store)
                    we assume key = key[0]

        :return: str, either the key, params[key], key[0], params[key][0]
        """
        # set function name
        # _ = display_func('_check_key', __NAME__, self.class_name)
        # get drs parameters
        drs_params = self.params
        # need to check drs_params for key (if key is not in header)
        if (key not in self.header) and (key in drs_params):
            store = drs_params[key]
            # see if we have key store
            if isinstance(store, list) and len(store) == 3:
                drskey = str(store[0])
                source = 'store[0]'
            # if we dont assume we have a string
            else:
                drskey = str(store)
                source = 'store'
        else:
            drskey = str(key)
            source = 'input'
        # debug log message
        dargs = [key, drskey, source]
        WLOG(drs_params, 'debug', textentry('90-008-00001', args=dargs))
        # return drskey
        return drskey

    def copy_original_keys(self, drs_file: 'DrsFitsFile' = None,
                           forbid_keys: bool = True,
                           root: Union[str, None] = None,
                           allkeys: bool = False,
                           group: Union[str, None] = None,
                           exclude_groups: Union[str, List[str], None] = None):
        """
        Copies keys from hdr dictionary to DrsFile.hdict,
        if forbid_keys is True some keys will not be copied
        (defined in spirouConfig.Constants.FORBIDDEN_COPY_KEYS())

        adds keys in form: hdict[key] = (value, comment)

        :param drs_file: DrsFile instance, the file to be used to copy the
                         header keys from (must have read this file to generate
                         the header)

        :param forbid_keys: bool, if True uses the forbidden copy keys
                            (defined in
                               spirouConfig.Constants.FORBIDDEN_COPY_KEYS()
                            to remove certain keys from those being copied,
                            if False copies all keys from input header

        :param root: string, if we have "root" then only copy keywords that
                     start with this string (prefix)

        :param allkeys: bool, if True return all keys from header

        :param group: string, if not None sets the group to use (will only
                      copy this groups header keys)

        :param exclude_groups: string or list or strings, if not None sets the
                              group or groups not to include in copy

        :return None:
        """
        # set function name
        # _ = display_func('copy_original_keys', __NAME__,
        #                  self.class_name)
        # deal with exclude groups
        if exclude_groups is not None:
            if isinstance(exclude_groups, str):
                exclude_groups = [exclude_groups]
        # get drs_file header/comments
        if drs_file is None:
            self.check_read(header_only=True)
            fileheader = self.header
        else:
            # check that data/header is read
            drs_file.check_read(header_only=True)
            fileheader = drs_file.header
        # remove nan values
        fileheader = self.deal_with_nans(fileheader)
        # get cards to copy
        _cards = self.copy_cards(fileheader.cards, root, exclude_groups, group,
                                 forbid_keys, allkeys)
        # deal with appending to a hidct that isn't empty
        if self.hdict is None:
            self.hdict = drs_fits.Header(_cards)
        else:
            for _card in _cards:
                self.hdict.append(_card)

    def copy_cards(self, cards: drs_fits.Header.cards,
                   root: Union[str, None] = None,
                   exclude_groups: Union[str, List[str], None] = None,
                   group: Union[str, None] = None,
                   forbid_keys: bool = True, allkeys: bool = False
                   ) -> drs_fits.Header.cards:
        """
        Copy header cards in the correct way

        :param cards: astropy.io.fits.header.Cards instance
        :param root: str, if we have "root" then only copy keywords that
                     start with this string (prefix)
        :param exclude_groups: string or list or strings, if not None sets the
                              group or groups not to include in copy
        :param group: string, if not None sets the group to use (will only
                      copy this groups header keys)
        :param forbid_keys: bool, if True uses the forbidden copy keys
                            (defined in
                               spirouConfig.Constants.FORBIDDEN_COPY_KEYS()
                            to remove certain keys from those being copied,
                            if False copies all keys from input header
        :param allkeys: bool, if True return all keys from header

        :return: astropy.io.fits.header.Cards instance - updated
        """
        # set function name
        func_name = display_func('copy_cards', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # generate instances from params
        keyword_inst = constant_functions.Keyword
        keyworddict = params.get_instanceof(keyword_inst, nameattr='key')

        # filter function
        def __keep_card(card: drs_fits.fits.header.Card) -> bool:
            """
            Filter function to sort out whether to keep a card returns
            True if we should keep a card False if we shoudn't

            :param card: a astropy.io.fits.header.Card instance

            :return: True if we should keep a card False if we shoudn't
            """
            key = card[0]
            if root is not None:
                if not key.startswith(root):
                    return False
            # deal with exclude groups
            if exclude_groups is not None:
                # loop around keys
                for exgrp in exclude_groups:
                    # check if key is in keyword dict and return the
                    #    corresponding key (mkey) if found
                    cond, mkey = _check_keyworddict(key, keyworddict)
                    # if key is in keyword dict look if group matches
                    if cond:
                        keygroup = keyworddict[mkey].group
                        # if key group is None skip check
                        if keygroup is None:
                            continue
                        # if key group is equal to exclude group then return
                        #    False  i.e. don't keep
                        if keygroup.upper() == exgrp.upper():
                            return False
            # deal with group (have to get keyword instance from keyworddict
            #    then check if it has a group then see if group = keygroup)
            if group is not None:
                # check if key is in keyword dict and return the corresponding
                #    key (mkey) if found
                cond, mkey = _check_keyworddict(key, keyworddict)
                # if key is in keyword dict look if group matches
                if cond:
                    keygroup = keyworddict[mkey].group
                    # if key group is None skip it
                    if keygroup is None:
                        return False
                    # if key group does not match group skip it
                    if keygroup.upper() != group.upper():
                        return False
                # if we have a group but key is not in keyword dict we
                # return False --> we don't want this key
                else:
                    return False
            # skip if key is forbidden key
            if forbid_keys and (key in params['FORBIDDEN_COPY_KEYS']):
                return False
            # skip if key is drs forbidden key (unless allkeys)
            elif (key in params['FORBIDDEN_DRS_KEY']) and (not allkeys):
                return False
            # skip if key added temporarily in code (denoted by @@@)
            elif '@@@' in key:
                return False
            # skip QC keys (unless allkeys)
            elif is_forbidden_prefix(params, key) and (not allkeys):
                return False
            else:
                return True

        # filter and create new header
        _copy_cards = filter(__keep_card, cards)
        # return cards for copy
        return _copy_cards

    @staticmethod
    def deal_with_nans(header: drs_fits.Header) -> drs_fits.Header:
        """
        Replace nan values with np.nan

        :param header: drs_fits.Header

        :return: update header
        """
        # check header type and convert to one that can handle nans
        if isinstance(header, drs_fits.fits.Header):
            header = drs_fits.Header(header)
        # deal with nan values
        for key in header:
            try:
                _ = header[key]
            except drs_fits.fits.VerifyError:
                header[key] = np.nan
        # return updated header
        return header

    def add_hkey(self, key: Union[str, None] = None,
                 keyword: Union[list, None] = None, value: Any = None,
                 comment: Union[str, None] = None,
                 fullpath: bool = False):
        """
        Add a new key to DrsFile.hdict from kwstore. If kwstore is None
        and key and comment are defined these are used instead.

            Each keywordstore is in form:
                [key, value, comment]    where key and comment are strings
            DrsFile.hdict is updated with hdict[key] = (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param keyword: if key not set use the keywordstore
                        keyword must be in the format:
                        keyword = [key, value, comment]
        :param value: object or None, if any python object (other than None)
                      will set the value of hdict[key] to (value, comment)
        :param comment: string or None, if kwstore not define this is the
                        comment to set in hdict[key] = (value, comment)
        :param fullpath: bool, if true header keys retain the full path
                         if False filenames are cut down to just the filename
                         (os.path.basename)

        :return: None (but updates DrsFitsFile.hdict)
        """
        # set function name
        func_name = display_func('add_hkey', __NAME__,
                                 self.class_name)
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # if key is set use it (it should be from parameter dictionary
        if key is not None:
            if isinstance(key, str) and (key in params):
                kwstore = params[key]
            elif isinstance(key, list) or isinstance(key, tuple):
                kwstore = list(key)
            else:
                eargs = [key, func_name]
                self.__error__(textentry('00-001-00008', args=eargs))
                kwstore = None
        else:
            kwstore = [keyword, value, comment]
        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            okey, dvalue, comment = self.get_keywordstore(tuple(kwstore),
                                                          func_name)
        else:
            okey, dvalue, comment = key, None, comment

        # set the value to default value if value is None
        if value is None:
            value = dvalue

        # deal with paths (should only contain filename for header)
        if isinstance(value, str):
            if os.path.isfile(value) and (not fullpath):
                value = os.path.basename(value)

        # add to the hdict dictionary in form (value, comment)
        self.hdict[okey] = (value, comment)

    def add_hkeys(self, keys: Union[List[str], None] = None,
                  kwstores: Union[List[list], None] = None,
                  values: Union[List[Any], None] = None,
                  comments: Union[List[str], None] = None):
        """
        Add a set of new key to DrsFile.hdict from keywordstores. If kwstores
        is None and keys and comments are defined these are used instead.

        Each kwstores is in form:
                [key, value, comment]    where key and comment are strings


        :param keys: list of strings, if kwstores is None this is the list
                         of keys (must be same size as "comments")
        :param kwstores: list of lists, list of "keyword list" lists
                              each "keyword list" must be in form:
                              [string, value, string]
        :param values: list of objects or None, if any python object
                       (other than None) will replace the values in kwstores
                       (i.e. kwstore[1]) with value[i], if None uses the
                       value = kwstore[1] for each kwstores
        :param comments: list of string, if kwstores is None this is the list
                         of comments (must be same size as "keys")

        :return None:
        """
        # set function name
        func_name = display_func('add_hkeys', __NAME__,
                                 self.class_name)
        # deal with no keywordstore
        if (kwstores is None) and (keys is None or comments is None):
            self.__error__(textentry('00-001-00009', args=[func_name]))
        # deal with kwstores set
        if kwstores is not None:
            # make sure kwstores is a list of list
            if not isinstance(kwstores, list):
                self.__error__(textentry('00-001-00010', args=[func_name]))
            # loop around entries
            for k_it, kwstore in enumerate(kwstores):
                self.add_hkey(keyword=kwstore, value=values[k_it])
        # else we assume keys and comments
        else:
            if not isinstance(keys, list):
                self.__error__(textentry('00-001-00011', args=[func_name]))
            if not isinstance(comments, list):
                self.__error__(textentry('00-001-00012', args=[func_name]))
            if len(keys) != len(comments):
                self.__error__(textentry('00-001-00013', args=[func_name]))
            # loop around entries
            for k_it in range(len(keys)):
                self.add_hkey(key=keys[k_it], value=values[k_it],
                              comment=comments[k_it])

    def add_hkey_1d(self, key: Union[str, None] = None,
                    values: Union[List[Any], np.ndarray, None] = None,
                    keyword: Union[List[list], None] = None,
                    comment: Union[str, None] = None,
                    dim1name: Union[str, None] = None):
        """
        Add a new 1d list to key using the "kwstore"[0] or "key" as prefix
        in form:
            keyword = kwstore + row number
            keyword = key + row number
        and pushes it into DrsFile.hdict in form:
            hdict[keyword] = (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param values: numpy array or 1D list of keys or None
                       if numpy array or 1D list will create a set of keys
                       in form keyword = kwstore + row number
                      where row number is the position in values
                      with value = values[row number][column number]
        :param keyword: string, if key is None uses key and comment in form
                   keyword = key + row number
        :param comment: string, the comment to go into the header
                        hdict[keyword] = (value, comment)
        :param dim1name: string, the name for dimension 1 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}

        :return None: updates DrsFitsFile.hdict
        """
        # set function name
        func_name = display_func('add_hkey_1d', __NAME__,
                                 self.class_name)
        # deal with no keywordstore
        if (key is None) and (keyword is None or comment is None):
            self.__error__(textentry('00-001-00014', args=[func_name]))
        # deal with no dim1name
        if dim1name is None:
            dim1name = 'dim1'
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # if key is set use it (it should be from parameter dictionary
        if key is not None:
            if isinstance(key, str) and (key in params):
                kwstore = params[key]
            elif isinstance(key, list):
                kwstore = list(key)
            else:
                eargs = [key, func_name]
                self.__error__(textentry('00-001-00008', args=eargs))
                kwstore = None
        else:
            kwstore = [keyword, None, comment]

        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            okey, dvalue, comment = self.get_keywordstore(tuple(kwstore),
                                                          func_name)
        else:
            okey, dvalue, comment = keyword, None, comment
        # set the value to default value if value is None
        if values is None:
            values = [dvalue]
        # convert to a numpy array
        values = np.array(values)
        # get the length of dimension 1
        dim1 = len(values)
        # loop around the 1D array
        for it in range(dim1):
            # construct the key name
            keyname = test_for_formatting(okey, it)
            # get the value
            value = values[it]
            # deal with paths (should only contain filename for header)
            if isinstance(value, str):
                if os.path.isfile(value):
                    value = os.path.basename(value)
            # construct the comment name
            comm = '{0} {1}={2}'.format(comment, dim1name, it)
            # add to header dictionary
            self.hdict[keyname] = (value, comm)

    def add_hkey_2d(self, key: Union[str, None] = None,
                    keyword: Union[List[list], None] = None,
                    values: Union[np.ndarray, None] = None,
                    comment: Union[str, None] = None,
                    dim1name: Union[str, None] = None,
                    dim2name: Union[str, None] = None):
        """
        Add a new 2d list to key using the "kwstore"[0] or "key" as prefix
        in form:
            keyword = kwstore + row number
            keyword = key + row number

        where number = (row number * number of columns) + column number

        and pushes it into DrsFile.hdict in form:
            hdict[keyword] = (value, comment)

        :param key: string or None, if kwstore not defined this is the key to
                    set in hdict[key] = (value, comment)
        :param values: numpy array or None
                       if numpy array will create a set of keys
                       in form keyword = kwstore + row number
                      where row number is the position in values
                      with value = values[row number][column number]
        :param keyword: string, if key is None uses key and comment in form
                   keyword = key + row number
        :param comment: string, the comment to go into the header
                        hdict[keyword] = (value, comment)
        :param dim1name: string, the name for dimension 1 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}
        :param dim2name: string, the name for dimension 2 (rows), used in
                         FITS rec HEADER comments in form:
                             comment = kwstore[2] dim1name={row number}
                             or
                             comment = "comment" dim1name={row number}

        :return None: updates DrsFitsFile.hdict
        """
        # set function name
        func_name = display_func('add_hkey_2d', __NAME__,
                                 self.class_name)
        # deal with no dim names
        if dim1name is None:
            dim1name = 'dim1'
        if dim2name is None:
            dim2name = 'dim2'
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # if key is set use it (it should be from parameter dictionary
        if key is not None:
            if isinstance(key, str) and (key in params):
                kwstore = params[key]
            elif isinstance(key, list):
                kwstore = list(key)
            else:
                eargs = [key, func_name]
                self.__error__(textentry('00-001-00008', args=eargs))
                kwstore = None
        else:
            kwstore = [keyword, None, comment]
        # extract keyword, value and comment and put it into hdict
        if kwstore is not None:
            key, dvalue, comment = self.get_keywordstore(tuple(kwstore),
                                                         func_name)
        else:
            key, dvalue, comment = key, None, comment
        # set the value to default value if value is None
        if values is None:
            values = [dvalue]
        # convert to a numpy array
        values = np.array(values)
        # get the length of dimension 1
        dim1, dim2 = values.shape
        # loop around the 1D array
        for it in range(dim1):
            for jt in range(dim2):
                # construct the key name
                keyname = test_for_formatting(key, it * dim2 + jt)
                # get the value
                value = values[it, jt]
                # deal with paths (should only contain filename for header)
                if isinstance(value, str):
                    if os.path.isfile(value):
                        value = os.path.basename(value)
                # construct the comment name
                cargs = [comment, dim1name, it, dim2name, jt]
                comm = '{0} {1}={2} {3}={4}'.format(*cargs)
                # add to header dictionary
                self.hdict[keyname] = (value, comm)

    def add_core_hkeys(self, params: Optional[ParamDict] = None):
        """
        Add the core header keys to the header (every DRS fits file should
        have at least these)

        :param params: Optional ParamDict, if we have the parameter dictionary
                       use it to get the parameters, otherwise guess them

        :return: None, updates the header
        """
        if params is None:
            params = dict()
        # ----------------------------------------------------------------------
        # add version
        version = params.get('DRS_VERSION', __version__)
        self.add_hkey('KW_VERSION', value=version)
        # ----------------------------------------------------------------------
        # add drs date
        drs_date = params.get('DRS_DATE', __date__)
        self.add_hkey('KW_DRS_DATE', value=drs_date)
        # ----------------------------------------------------------------------
        # add date now
        date_now = params.get('DATE_NOW', base.Time.now().iso)
        self.add_hkey('KW_DRS_DATE_NOW', value=date_now)
        # ----------------------------------------------------------------------
        # add process id
        pid = params.get('PID', 'Unknown')
        self.add_hkey('KW_PID', value=pid)
        # ----------------------------------------------------------------------
        # add output tag
        self.add_hkey('KW_OUTPUT', value=self.name)
        # ----------------------------------------------------------------------
        # add config run.ini file (if given)
        if 'INPUTS' in params:
            crunfile = params['INPUTS'].get('CRUNFILE', 'Not set')
        else:
            crunfile = 'Not set'
        self.add_hkey('KW_CRUNFILE', value=crunfile)

    def add_qckeys(self, qcparams: Union[QCParamList, None] = None):
        """
        Add the quality control keys to the header, if None passed a single
        empty qc parameter is added with 'None' for all values

        :param qcparams: List of list containing:
                            [quality control names,
                             quality control values,
                             quality control logic,
                             quality control pass/fail]

        :return: None, updates DrsFitsFile.hdict
        """
        # set function name
        func_name = display_func('add_qckeys', __NAME__,
                                 self.class_name)
        # get parameters
        qc_kws = ['KW_DRS_QC_NAME', 'KW_DRS_QC_VAL', 'KW_DRS_QC_LOGIC',
                  'KW_DRS_QC_PASS']
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # deal with qcparams = None
        if qcparams is None:
            qc_names, qc_values, qc_logic, qc_pass = [], [], [], []
            # add to qc header lists
            qc_pass.append(1)
            qc_values.append('None')
            qc_names.append('None')
            qc_logic.append('None')
            # store in qc_params
            qcparams = [qc_names, qc_values, qc_logic, qc_pass]
        # check lengths are the same
        lengths = []
        for qcparam in qcparams:
            lengths.append(len(qcparam))
        strlengths = map(lambda x: str(x), lengths)
        # loop around lengths and test that they are the same
        for length in lengths:
            if lengths[0] != length:
                eargs = [', '.join(strlengths), func_name]
                raise drs_log.AperoCodedException(params, '00-001-00019',
                                                  targs=eargs)
        # loop around values and add to hdict
        for it in range(lengths[0]):
            # loop around qc parameters
            for jt, keystr in enumerate(qc_kws):
                keyws = params[keystr]
                # extract keyword, value and comment and put it into hdict
                key, dvalue, comment = self.get_keywordstore(keyws, func_name)
                value = qcparams[jt][it]
                # add to the hdict dictionary in form (value, comment)
                self.hdict[key.format(it + 1)] = (value, comment)
        # add a final criteria that says whether everything passed or not
        qc_all = params['KW_DRS_QC'][0]
        self.hdict[qc_all] = np.all(qcparams[3])

    def get_qckeys(self) -> QCParamList:
        """
        Get the quality control header keys from the header
        Note values will be pushed to strings (and may need to change data
        type after return)

        :return: List of list containing:
                            [quality control names,
                             quality control values,
                             quality control logic,
                             quality control pass/fail]
        """
        # set function name
        func_name = display_func('get_qckeys', __NAME__,
                                 self.class_name)
        # check for kwstore in params
        self.check_params(func_name)
        params = self.params
        # get qc all value
        qc_all = params['KW_DRS_QC'][0]
        # get qc_values
        qc_values = self.get_hkey_1d('KW_DRS_QC_VAL', dtype=str,
                                     start=1, excludes=qc_all)
        qc_names = self.get_hkey_1d('KW_DRS_QC_NAME', dtype=str,
                                    start=1, excludes=qc_all)
        qc_logic = self.get_hkey_1d('KW_DRS_QC_LOGIC', dtype=str,
                                    start=1, excludes=qc_all)
        qc_pass = self.get_hkey_1d('KW_DRS_QC_PASS', dtype=int,
                                   start=1, excludes=qc_all)
        # push into qc params
        qc_params = (list(qc_names), list(qc_values), list(qc_logic),
                     list(qc_pass))
        # return qc params
        return qc_params

    def get_keywordstore(self, kwstore: Tuple[str, Any, str],
                         func_name=None) -> Tuple[str, Any, str]:
        """
        Deal with extraction of key, value and comment from kwstore
        the kwstore should be a list in the following form:

        [name, value, comment]     with types [string, object, string]

        :param kwstore: list, keyword list must be in form:
                          [string, value, string]
        :param func_name: string or None, if not None defined where the
                          kwstore function is being called, if None
                          is set to here (spirouFITS.extract_key_word_store())

        :return key: string, the name/key of the HEADER (key/value/comment)
        :return value: object, any object to be put into the HEADER value
                       (under HEADER key="key")
        :return comment: string, the comment associated with the HEADER key
        """
        # deal with no func_name
        if func_name is None:
            # set function name
            func_name = display_func('get_keywordstore', __NAME__,
                                     self.class_name)
        # extract keyword, value and comment and put it into hdict
        # noinspection PyBroadException
        try:
            key, dvalue, comment = kwstore
        except Exception as _:
            eargs = [kwstore, func_name]
            self.__error__(textentry('00-001-00016', args=eargs))
            key, dvalue, comment = None, None, None
        # return values
        return key, dvalue, comment

    def copy_hdict(self, drsfile: Optional['DrsFitsFile'] = None,
                   hdict: Optional[dict] = None):
        """
        Copy a hdict entry from drsfile (a DrsFitsFile instance)

        :param drsfile: DrsFitsFile instance (containing drsfile.hdict)
        :param hdict: dict, the header dictionary to be copied 
                      (if drsfile is None)
        
        :return: None, updates DrsFitsFile.hdict
        """
        # set function name
        # _ = display_func('copy_hdict', __NAME__, self.class_name)
        # set this instance to the hdict instance of another drs fits file
        if drsfile is not None and drsfile.nosave:
            return
        elif drsfile is not None:
            self.hdict = drsfile.hdict.copy()
        elif hdict is not None:
            self.hdict = hdict.copy()

    def copy_header(self, drsfile: Optional['DrsFitsFile'] = None,
                    header: Optional[Header] = None):
        """
        Copy a header entry from drsfile (a DrsFitsFile instance)
        
        :param drsfile: DrsFitsFile instance (containing drsfile.hdict)
        :param header: fits Header - the header to be copied (if drsfile
                       is None)
        
        :return: None, updates self.header
        """
        # set function name
        # _ = display_func('copy_header', __NAME__, self.class_name)
        # set this instance to the header instance of another drs fits file
        if drsfile is not None and drsfile.nosave:
            return
        elif drsfile is not None:
            self.header = drsfile.header.copy()
        elif header is not None:
            self.header = header.copy()

    # -------------------------------------------------------------------------
    # database methods
    # -------------------------------------------------------------------------
    def get_dbkey(self) -> Union[str, None]:
        """
        Returns the database key for DrsFitsFile

        :return: str or None, if set returns the string name for the database
                 key
        """
        # set function name
        # _ = display_func('get_dbkey', __NAME__, self.class_name)
        # deal with dbkey not set
        if self.raw_dbkey is None or self.dbkey is None:
            return None
        # set db key from raw dbkey
        self.dbkey = str(self.raw_dbkey)
        # make dbkey uppdercase
        if self.dbkey is not None:
            self.dbkey = self.dbkey.upper()
        # return dbkey
        return self.dbkey

    def update_param_table(self, name: str, param_kind: str,
                           values: Union[str, list]):
        """
        Tries to add a string representation of "values" to any param table
        in the file

        :param name:  str, variable name (for param table)
        :param param_kind: str, the param kind (calib/tellu/index/log)
        :param values: either a string with values separated by commas or a list
                       that will be converted to strings separated by commas

        :return: None, updates self.filename (last extension(s))
        """
        # set function name
        func_name = display_func('update_param_table', self.class_name)
        # deal with values as list
        if isinstance(values, list):
            input_string = ','.join(list(map(lambda x: str(x), values)))
        else:
            input_string = str(values)
        # make a description
        desc = '{0} database entry (for reproduction)'.format(param_kind)
        # new table row
        newrow = Table()
        newrow['NAME'] = [str(name)]
        newrow['KIND'] = [str(param_kind)]
        newrow['VALUE'] = [str(input_string)]
        newrow['SOURCE'] = [str(func_name)]
        newrow['DESCRIPTION'] = [str(desc)]
        newrow['COUNT'] = [str(1)]
        # find all extensions with a param table in
        exts = drs_fits.find_named_extensions(self.filename,
                                              startswith='PARAM_')
        # loop around each extension and add to table
        for ext in exts:
            # read table
            table = drs_fits.readfits(self.params, self.filename,
                                      fmt='fits-table', ext=ext, log=False)
            # add row to table
            newtable = vstack([table, newrow])
            # update file
            drs_fits.update_extension(self.params, self.filename, ext,
                                      data=newtable, fmt='fits-table')


class DrsNpyFile(DrsInputFile):
    def __init__(self, name, filetype: str = '.npy',
                 suffix: str = '',
                 remove_insuffix: Union[bool, None] = None,
                 prefix: str = '',
                 fibers: Union[List[str], None] = None,
                 fiber: Union[str, None] = None,
                 params: Union[ParamDict, None] = None,
                 filename: Union[str, None] = None,
                 intype: Any = None,
                 path: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 inputdir: Union[str, None] = None,
                 obs_dir: Union[str, None] = None,
                 data: Union[np.ndarray, None] = None,
                 header: Union[drs_fits.Header, None] = None,
                 fileset: Union[list, None] = None,
                 filesetnames: Union[List[str], None] = None,
                 outclass: OutFileTypes = None,
                 inext: Union[str, None] = '.npy',
                 dbname: Union[str, None] = None,
                 dbkey: Union[str, None] = None,
                 rkeys: Union[dict, None] = None,
                 numfiles: Union[int, None] = None,
                 shape: Union[int, None] = None,
                 hdict: Union[drs_fits.Header, None] = None,
                 output_dict: Union[OrderedDict, None] = None,
                 datatype: Union[str, None] = None,
                 dtype: Union[type, None] = None,
                 is_combined: Union[bool, None] = None,
                 combined_list: Union[list, None] = None,
                 infiles: Union[list, None] = None,
                 s1d: Union[list, None] = None,
                 hkeys: Union[Dict[str, str], None] = None,
                 instrument: Optional[str] = None,
                 nosave: Optional[bool] = False,
                 description: Union[str, None] = None,
                 inpath: Union[str, None] = None,
                 required: Union[bool, None] = None):
        """
        Create a DRS Npy File Input object

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: NOT USED FOR NPY FILE CLASS
        :param remove_insuffix: NOT USED FOR NPY FILE CLASS
        :param prefix: NOT USED FOR NPY FILE CLASS
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: NOT USED FOR NPY FILE CLASS
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: NOT USED FOR NPY FILE CLASS
        :param path: NOT USED FOR NPY FILE CLASS
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: NOT USED FOR NPY FILE CLASS
        :param obs_dir: NOT USED FOR NPY FILE CLASS
        :param data: np.array - when loaded the data is stored here
        :param header: NOT USED FOR NPY FILE CLASS
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: NOT USED FOR NPY FILE CLASS
        :param numfiles: NOT USED FOR NPY FILE CLASS
        :param shape: NOT USED FOR NPY FILE CLASS
        :param hdict: NOT USED FOR NPY FILE CLASS
        :param output_dict: NOT USED FOR NPY FILE CLASS
        :param datatype: NOT USED FOR NPY FILE CLASS
        :param dtype: NOT USED FOR NPY FILE CLASS
        :param is_combined: NOT USED FOR NPY FILE CLASS
        :param combined_list: NOT USED FOR NPY FILE CLASS
        :param infiles: NOT USED FOR NPY FILE CLASS
        :param s1d: NOT USED FOR NPY FILE CLASS
        :param hkeys: NOT USED FOR NPY FILE CLASS
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality
        :param required: bool, if True this file is always expectedt to exist
                 if recipe ran correctly
        """
        # set class name
        self.class_name = 'DrsNpyFile'
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # define a name
        self.name = name
        _ = infiles
        # get super init
        DrsInputFile.__init__(self, name, filetype, suffix, remove_insuffix,
                              prefix, fibers, fiber, params, filename, intype,
                              path, basename, inputdir, obs_dir, data, header,
                              fileset, filesetnames, outclass, inext, dbname,
                              dbkey, rkeys, numfiles, shape, hdict,
                              output_dict, datatype, dtype, is_combined,
                              combined_list, infiles, s1d, hkeys, instrument,
                              nosave, description, inpath, required)
        # these keys are not set in DrsInputFile
        self.inext = inext
        # get tag
        self.dbname = dbname
        self.raw_dbkey = dbkey
        self.dbkey = None
        if dbkey is not None:
            self.dbkey = str(dbkey)

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

    def __str__(self) -> str:
        """
        Defines the str(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        # _ = display_func('__str__', __NAME__, self.class_name)
        # return string output
        return self.string_output()

    def __repr__(self) -> str:
        """
        Defines the print(DrsFitsFile) return for DrsFitsFile
        :return str: the string representation of DrsFitsFile
                     i.e. DrsFitsFile[name] or DrsFitsFile[name_fiber]
        """
        # set function name
        # _ = display_func('__repr__', __NAME__, self.class_name)
        # return string output
        return self.string_output()

    def read_file(self, ext: Union[int, None] = None, check: bool = False,
                  copy: bool = False):
        """
        Read a npy file (using advance np.load via drs_path.numpy_load)

        :param ext: NOT USED FOR NPY FILE CLASS
        :param check: NOT USED FOR NPY FILE CLASS
        :param copy: NOT USED FOR NPY FILE CLASS
        :return None:
        """
        # not used
        _ = ext, check, copy
        # set function name
        func_name = display_func('read_file', __NAME__,
                                 self.class_name)
        # get parameters
        self.check_params(func_name)
        params = self.params
        # if filename is set
        if self.filename is not None:
            # set up attempts
            attempts = 0
            # loop 10 times - simple lock to wait to be able to load file
            while attempts < 10:
                try:
                    # read file
                    self.data = drs_path.numpy_load(self.filename)
                    # if successful break while loop
                    break
                except Exception as e:
                    # if we have tried a few times don't continue and
                    #   raise error
                    if attempts == 9:
                        eargs = [type(e), e, self.filename, func_name]
                        emsg = textentry('00-008-00018', args=eargs)
                        raise DrsCodedException('00-008-00018', level='error',
                                                targs=eargs, message=emsg)
                    # some time file is locked by other process
                    else:
                        # file locking trying again in 5s
                        wmsg = textentry('10-001-00011', args=[self.filename])
                        DrsCodedWarning('10-001-00011', level='warning',
                                        targs=[self.filename], message=wmsg)
                        # sleep 5 seconds and then try again
                        time.sleep(5)
                        # add to the attempts and loop again
                        attempts += 1
        # cause error if file name is not set
        else:
            raise drs_log.AperoCodedException(params, '00-008-00013',
                                              targs=[func_name])

    def check_read(self, header_only: bool = False, data_only: bool = False,
                   load: bool = True):
        """
        Check whether data have been read
        if load is True and they haven't been read them read them

        data is loaded into DrsFitsFile.data

        :param header_only: not used for Npy File
        :param data_only: bool, if True only read/check data
        :param load: bool, if True load header and / or data

        :return: None
        """
        # set function name
        # _ = display_func('check_read', __NAME__, self.class_name)
        # header only is not used
        _ = header_only
        # ---------------------------------------------------------------------
        # deal with data only
        # ---------------------------------------------------------------------
        if data_only:
            if self.data is None:
                if load:
                    return self.read_file()
                # raise exception
                func = self.__repr__()
                eargs = [func, func + '.read_file()']
                self.__error__(textentry('00-001-00004', args=eargs))
                return 0
            else:
                return 1
        # ---------------------------------------------------------------------
        # deal with both data and header
        # ---------------------------------------------------------------------
        if self.data is None:
            self.read_file()
            return 1
        # if we got here we are good - data has been read
        return 1

    def get_data(self, copy: bool = False,
                 extensions=None) -> Union[np.ndarray, Table, None]:
        """
        return the data array

        :param copy: bool, if True deep copies the data
        :param extensions: not used for npy file

        :return: the data (numpy array)
        """
        # set function name
        # _ = display_func('get_data', __NAME__, self.class_name)
        # we don't use extensions
        _ = extensions
        # check data exists
        if self.data is None:
            self.check_read(data_only=True)
        # deal with copying data
        if copy:
            return np.array(self.data)
        else:
            return self.data

    def write_npy(self, block_kind: str, runstring: Union[str, None] = None):
        """
        Write a npy file (using np.save)

        also used to update output_dictionary for index database

        :param block_kind: not used for npy
        :param runstring: not used for npy

        :return: None
        """
        # set function name
        func_name = display_func('write_file', __NAME__,
                                 self.class_name)
        # block kind and runstring are not used
        _ = block_kind, runstring
        # get parameters
        self.check_params(func_name)
        params = self.params
        # deal with no save
        if self.no_save():
            wmsg = 'NOSAVE active - file not written to disk'
            WLOG(self.params, 'warning', wmsg)
            return
        # if filename is not set raise error
        if self.filename is None:
            raise drs_log.AperoCodedException(params, '00-008-00013',
                                              targs=[func_name])
        if self.data is not None:
            try:
                # save to file
                np.save(self.filename, self.data)
            except Exception as e:
                eargs = [type(e), e, self.filename, func_name]
                raise drs_log.AperoCodedException(params, '00-008-00015',
                                                  targs=eargs)
        else:
            eargs = [self.filename, func_name]
            raise drs_log.AperoCodedException(params, '00-008-00014',
                                              targs=eargs)

    def string_output(self) -> str:
        """
        String output for DrsFitsFile. If fiber is not None this also
        contains the fiber type

        i.e. DrsFitsFile[{name}_{fiber}] or DrsFitsFile[{name}]
        :return string: str, the string to print
        """
        # set function name
        # _ = display_func('string_output', __NAME__,
        #                  self.class_name)
        # if we do not have a fiber print the string representation of drs npy
        if self.fiber is None:
            return 'DrsNpyFile[{0}]'.format(self.name)
        # if we do add fiber to the string representation
        else:
            return 'DrsNpyFile[{0}_{1}]'.format(self.name, self.fiber)

    def newcopy(self, name: Union[str, None] = None,
                filetype: Union[str, None] = None,
                suffix: Union[str, None] = None,
                remove_insuffix: Union[bool, None] = None,
                prefix: Union[str, None] = None,
                fibers: Union[List[str], None] = None,
                fiber: Union[str, None] = None,
                params: Union[ParamDict, None] = None,
                filename: Union[str, None] = None,
                intype: Any = None,
                path: Union[str, None] = None,
                basename: Union[str, None] = None,
                inputdir: Union[str, None] = None,
                obs_dir: Union[str, None] = None,
                data: Union[np.ndarray, None] = None,
                header: Union[drs_fits.Header, None] = None,
                fileset: Union[list, None] = None,
                filesetnames: Union[List[str], None] = None,
                outclass: OutFileTypes = None,
                inext: Union[str, None] = None,
                dbname: Union[str, None] = None,
                dbkey: Union[str, None] = None,
                rkeys: Union[dict, None] = None,
                numfiles: Union[int, None] = None,
                shape: Union[int, None] = None,
                hdict: Union[drs_fits.Header, None] = None,
                output_dict: Union[OrderedDict, None] = None,
                datatype: Union[str, None] = None,
                dtype: Union[type, None] = None,
                is_combined: Union[bool, None] = None,
                combined_list: Union[list, None] = None,
                infiles: Union[list, None] = None,
                s1d: Union[list, None] = None,
                hkeys: Union[Dict[str, str], None] = None,
                instrument: Optional[str] = None,
                nosave: Optional[bool] = None,
                description: Optional[str] = None,
                inpath: Union[str, None] = None):
        """
        Create a new copy of DRS Npy File object - unset parameters come
        from current instance of Drs Input File

        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: NOT USED FOR NPY FILE CLASS
        :param remove_insuffix: NOT USED FOR NPY FILE CLASS
        :param prefix: NOT USED FOR NPY FILE CLASS
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: set params
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: NOT USED FOR NPY FILE CLASS
        :param path: NOT USED FOR NPY FILE CLASS
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: NOT USED FOR NPY FILE CLASS
        :param obs_dir: NOT USED FOR NPY FILE CLASS
        :param data: np.array - when loaded the data is stored here
        :param header: NOT USED FOR NPY FILE CLASS
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: NOT USED FOR NPY FILE CLASS
        :param numfiles: NOT USED FOR NPY FILE CLASS
        :param shape: NOT USED FOR NPY FILE CLASS
        :param hdict: NOT USED FOR NPY FILE CLASS
        :param output_dict: NOT USED FOR NPY FILE CLASS
        :param datatype: NOT USED FOR NPY FILE CLASS
        :param dtype: NOT USED FOR NPY FILE CLASS
        :param is_combined: NOT USED FOR NPY FILE CLASS
        :param combined_list: NOT USED FOR NPY FILE CLASS
        :param infiles: list, the list of input files (if output file)
        :param s1d: NOT USED FOR NPY FILE CLASS
        :param hkeys: NOT USED FOR NPY FILE CLASS
        :param instrument: str, the instrument this file definition is
                   associated with
        :param nosave: bool, if True this drs file should not be saved to disk
               even when asking for a write function
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality
        """
        # set function name
        # _ = display_func('newcopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsNpyFile, self, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            obs_dir, data, header, fileset, filesetnames,
                            outclass, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, s1d, hkeys, instrument,
                            nosave, description)

    def completecopy(self, drsfile: 'DrsNpyFile',
                     name: Union[str, None] = None,
                     filetype: Union[str, None] = None,
                     suffix: Union[str, None] = None,
                     remove_insuffix: Union[bool, None] = None,
                     prefix: Union[str, None] = None,
                     fibers: Union[List[str], None] = None,
                     fiber: Union[str, None] = None,
                     params: Union[ParamDict, None] = None,
                     filename: Union[str, None] = None,
                     intype: Any = None,
                     path: Union[str, None] = None,
                     basename: Union[str, None] = None,
                     inputdir: Union[str, None] = None,
                     obs_dir: Union[str, None] = None,
                     data: Union[np.ndarray, None] = None,
                     header: Union[drs_fits.Header, None] = None,
                     fileset: Union[list, None] = None,
                     filesetnames: Union[List[str], None] = None,
                     outclass: OutFileTypes = None,
                     inext: Union[str, None] = None,
                     dbname: Union[str, None] = None,
                     dbkey: Union[str, None] = None,
                     rkeys: Union[dict, None] = None,
                     numfiles: Union[int, None] = None,
                     shape: Union[int, None] = None,
                     hdict: Union[drs_fits.Header, None] = None,
                     output_dict: Union[OrderedDict, None] = None,
                     datatype: Union[str, None] = None,
                     dtype: Union[type, None] = None,
                     is_combined: Union[bool, None] = None,
                     combined_list: Union[list, None] = None,
                     infiles: Union[list, None] = None,
                     s1d: Union[list, None] = None,
                     hkeys: Union[Dict[str, str], None] = None,
                     instrument: Optional[str] = None,
                     nosave: Optional[bool] = None,
                     description: Optional[str] = None,
                     inpath: Union[str, None] = None):
        """
        Copy all keys from drsfile (unless other arguments set - these override
        copy from drsfile)

        :param drsfile: DrsNpyFile instance, the instance to copy parameters
                        from
        :param name: string, the name of the DRS input file
        :param filetype: string, the file type i.e. ".fits"
        :param suffix: NOT USED FOR NPY FILE CLASS
        :param remove_insuffix: NOT USED FOR NPY FILE CLASS
        :param prefix: NOT USED FOR NPY FILE CLASS
        :param fibers: list of strings, the possible fibers this file can be
                       associated with, should be None if it is not associated
                       with a specific fiber
        :param fiber: string, the specific fiber that this file is associated
                      with
        :param params: NOT USED FOR NPY FILE CLASS
        :param filename: string, the filename to give to this file (may override
                         other options)
        :param intype: NOT USED FOR NPY FILE CLASS
        :param path: NOT USED FOR NPY FILE CLASS
        :param basename: string, the basename (i.e. filename without path) for
                         the file
        :param inputdir: NOT USED FOR NPY FILE CLASS
        :param obs_dir: NOT USED FOR NPY FILE CLASS
        :param data: np.array - when loaded the data is stored here
        :param header: NOT USED FOR NPY FILE CLASS
        :param fileset: List of DrsFile instances - this file can be used as
                        a container for a set of DrsFiles
        :param filesetnames: List of strings, the names of each DrsFile same
                             as doing list(map(lambda x: x.name, fileset))
        :param outclass: OutClass, the associated outclass
        :param inext: str, the input file extension [not used in DrsInputFile]
        :param dbname: str, the database name this file can go in
                    (i.e. cailbration or telluric) [not used in DrsInputFile]
        :param dbkey: str, the database key [not used in DrsInputFile]
        :param rkeys: NOT USED FOR NPY FILE CLASS
        :param numfiles: NOT USED FOR NPY FILE CLASS
        :param shape: NOT USED FOR NPY FILE CLASS
        :param hdict: NOT USED FOR NPY FILE CLASS
        :param output_dict: NOT USED FOR NPY FILE CLASS
        :param datatype: NOT USED FOR NPY FILE CLASS
        :param dtype: NOT USED FOR NPY FILE CLASS
        :param is_combined: NOT USED FOR NPY FILE CLASS
        :param combined_list: NOT USED FOR NPY FILE CLASS
        :param infiles: NOT USED FOR NPY FILE CLASS
        :param s1d: NOT USED FOR NPY FILE CLASS
        :param hkeys: NOT USED FOR NPY FILE CLASS
        :param instrument: str, the instrument this file definition is
                   associated with
        :param nosave: bool, if True this drs file should not be saved to disk
               even when asking for a write function
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality
        """
        # set function name
        # _ = display_func('completecopy', __NAME__, self.class_name)
        # copy this instances values (if not overwritten)
        return _copydrsfile(DrsNpyFile, drsfile, None, name, filetype, suffix,
                            remove_insuffix, prefix, fibers, fiber, params,
                            filename, intype, path, basename, inputdir,
                            obs_dir, data, header, fileset, filesetnames,
                            outclass, inext, dbname, dbkey, rkeys, numfiles,
                            shape, hdict, output_dict, datatype, dtype,
                            is_combined, combined_list, infiles, s1d, hkeys,
                            instrument, nosave, description, inpath)

    # -------------------------------------------------------------------------
    # database methods
    # -------------------------------------------------------------------------
    def get_dbkey(self) -> Union[str, None]:
        """
        Returns the database key for DrsFitsFile

        :return: str or None, if set returns the string name for the database
                 key
        """
        # set function name
        # _ = display_func('get_dbkey', __NAME__, self.class_name)
        # deal with dbkey not set
        if self.raw_dbkey is None or self.dbkey is None:
            return None
        # set db key from raw dbkey
        self.dbkey = str(self.raw_dbkey)
        # make dbkey uppdercase
        if self.dbkey is not None:
            self.dbkey = self.dbkey.upper()
        # return dbkey
        return self.dbkey


class DrsFileGroup:
    """
    A way to group a set of Drs Files
    """

    def __init__(self, name: str, files: List[DrsInputFile]):
        """
        Construct a new drs file group
        :param name: str, the name of the file group
        :param files: list, the list of drs input files in the group
        """
        self.name = name
        self.files = files

    def copy(self) -> 'DrsFileGroup':
        """
        Copy a drs file group
        :return: 
        """
        return DrsFileGroup(self.name, self.files)


class DrsOutFileExtension:
    # set class name
    class_name: str = 'DrsOutFileExtension'

    def __init__(self, name: str,
                 drsfile: Union[DrsFileGroup, DrsFitsFile, str],
                 pos: int,
                 fiber: Union[str, None] = None,
                 block_kind: Union[str, None] = None,
                 hkeys: Union[dict, None] = None,
                 link: Union[list, str, None] = None,
                 hlink: Union[str, None] = None,
                 header_only: bool = False,
                 data_only: bool = False,
                 remove_drs_hkeys: bool = False,
                 remove_std_hkeys: bool = False,
                 clear_file: bool = False,
                 tag: Union[str, None] = None,
                 extname: Union[str, None] = None,
                 hdr_extname: Union[str, None] = None,
                 datatype: Union[str, None] = None):
        """
        Properties for an extension of a POST PROCESS file

        :param name: str, the name of this extension
        :param drsfile: DrsFitsFile, a fits file to add
        :param pos: position within the fits file
        :param fiber: str or None, if set defines the fiber to use
        :param block_kind: str, the block kind (e.g. raw/tmp/raw)
        :param link: str, if set this must be a previously defined extension
                     name
        :param hlink: str, the header key from link extension to use for
                      filename for this extension
        :param header_only: bool, if True only adds the header (not the data)
        :param data_only: bool, if True only adds the data (not the header)
        :param remove_drs_hkeys: bool , if True removes drs header keys flagged
                                 to be remove (else does not remove keys)
        :param remove_std_hkeys: bool, if True removes a list of standard keys
                                 from this extensions header
        :param clear_file: bool, if True this extensions file should be marked
                           for removal (if user adds --clear)
        :param tag: str or None, if set this is the EXTNAME given to this
                    extension in the output fits file (if None uses "name")
        :param extname: str, if set this is the extension name from the
                        file to take the image/table from
        :param hdr_extname: str, if set this forces taking the header from
                            the extension named here (otherwise uses primary)
        :param datatype: str, force 'image' or 'table' for extension

        :return:
        """
        # set basic parameters
        self.name = name
        self.drsfile = drsfile
        self.pos = pos
        self.fiber = fiber
        self.block_kind = block_kind
        self.hkeys = hkeys
        self.link = link
        self.hlink = hlink
        self.header_only = header_only
        self.data_only = data_only
        self.remove_drs_hkeys = remove_drs_hkeys
        self.remove_std_hkeys = remove_std_hkeys
        self.clear_file = clear_file
        self.tag = tag
        self.extname = extname
        self.hdr_extname = hdr_extname
        # to be filled
        self.filename = None
        self.header = None
        self.data = None
        self.datatype = datatype
        # table parameters
        self.table_drsfiles = []
        self.table_in_colnames = []
        self.table_out_colnames = []
        self.table_units = []
        self.table_fibers = []
        self.table_required = []
        self.table_kind = []
        self.table_clears = []
        self.table_clear_files = []

    def summary(self, extkey: int
                ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """
        Summary entries for ext name, ext input, col name, col input columns
        of summary table

        :param extkey: int, the key position in extensions dictionary

        :return: Tuple,
        """
        # define storage for outputting
        ext_name, ext_input = [], []
        col_name, col_input = [], []
        # ---------------------------------------------------------------------
        # get extension tag
        if self.tag is not None:
            etag = self.tag
        else:
            etag = self.name
        # ---------------------------------------------------------------------
        # drs file can be a DrsFileGroup, a string, or a DrsInputFile
        #    deal with these individually
        # ---------------------------------------------------------------------
        if isinstance(self.drsfile, DrsFileGroup):
            # deal with primary extension slightly differently named
            if extkey == 0:
                ext_name.append('Primary: {0}'.format(etag))
            else:
                ext_name.append('{0}'.format(etag))
            ext_input.append(self.drsfile.name)
            col_name.append('--')
            col_input.append('--')
        elif isinstance(self.drsfile, str):
            # -----------------------------------------------------------------
            # deal with tables (columns) --> table
            # -----------------------------------------------------------------
            if self.drsfile == 'table':
                # set column names
                col_name = list(self.table_out_colnames)
                # set column input files
                col_input = list(map(lambda x: x.name, self.table_drsfiles))
                # loop around ext name and inputs and make correct length
                for col in range(len(col_name)):
                    # first time we have extension name
                    if col == 0:
                        ext_name.append(etag)
                    # else we have a space (for columns)
                    else:
                        ext_name.append('--')
                    # extension input is null
                    ext_input.append('--')
        # -----------------------------------------------------------------
        # deal with standard extensions (no columns) --> image
        # -----------------------------------------------------------------
        elif isinstance(self.drsfile, DrsInputFile):
            # deal with primary extension slightly differently named
            if extkey == 0:
                ext_name.append('Primary: {0}'.format(etag))
            else:
                ext_name.append('{0}'.format(etag))
            ext_input.append(self.drsfile.name)
            col_name.append('--')
            col_input.append('--')
        # -----------------------------------------------------------------
        # return table column lists
        return ext_name, ext_input, col_name, col_input

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

    def __str__(self) -> str:
        """
        Defines the str(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        # _ = display_func('__str__', __NAME__, self.class_name)
        # return the string representation of DrsInputFile
        return '{0}[{1}]'.format(self.class_name, self.name)

    def __repr__(self) -> str:
        """
        Defines the print(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        # _ = display_func('__repr__', __NAME__, self.class_name)
        # return the string representation of DrsInputFile
        return 'DrsOutExt[{0}]'.format(self.name)

    def add_table_column(self, drsfile: DrsFitsFile,
                         incol: str, outcol: str, fiber: Union[str, None],
                         units: Union[str, None], required: bool = True,
                         block_kind: str = 'red', clear_file: bool = False):
        """
        Add a table column to an extension

        :param drsfile: drs fits file instance - must be a fits bin table
        :param incol: str, the input column name
        :param outcol: str, the output column name
        :param fiber: str or None, if set sets the fiber name
        :param units: str or None, if set sets the units for a columns
        :param required: bool, if False column is not required
        :param block_kind: str, the block kind (raw/tmp/red/out)
        :param clear_file: bool, sets whether the file that creates this column
                           should be cleared if/when we are clearing red files

        :return:
        """
        self.table_drsfiles.append(drsfile)
        self.table_in_colnames.append(incol)
        self.table_out_colnames.append(outcol)
        self.table_units.append(units)
        self.table_fibers.append(fiber)
        self.table_required.append(required)
        self.table_kind.append(block_kind)
        self.table_clears.append(clear_file)

    def copy(self):
        """
        Copies the extension to a new extension
        """
        # deep copy each parameter
        kwargs = dict()
        kwargs['name'] = deepcopy(self.name)
        if isinstance(self.drsfile, DrsInputFile):
            kwargs['drsfile'] = self.drsfile.newcopy()
        elif isinstance(self.drsfile, DrsFileGroup):
            kwargs['drsfile'] = self.drsfile.copy()
        else:
            kwargs['drsfile'] = deepcopy(self.drsfile)
        kwargs['pos'] = int(self.pos)
        kwargs['fiber'] = deepcopy(self.fiber)
        kwargs['block_kind'] = deepcopy(self.block_kind)
        kwargs['hkeys'] = deepcopy(self.hkeys)
        kwargs['link'] = deepcopy(self.link)
        kwargs['hlink'] = deepcopy(self.hlink)
        kwargs['header_only'] = bool(self.header_only)
        kwargs['data_only'] = bool(self.data_only)
        kwargs['remove_drs_hkeys'] = bool(self.remove_drs_hkeys)
        kwargs['remove_std_hkeys'] = bool(self.remove_std_hkeys)
        kwargs['clear_file'] = bool(self.clear_file)
        kwargs['tag'] = deepcopy(self.tag)
        kwargs['extname'] = deepcopy(self.extname)
        kwargs['hdr_extname'] = deepcopy(self.hdr_extname)
        kwargs['datatype'] = deepcopy(self.datatype)
        # create new copy
        new = DrsOutFileExtension(**kwargs)
        # table parameters
        new.table_drsfiles = deepcopy(self.table_drsfiles)
        new.table_in_colnames = deepcopy(self.table_in_colnames)
        new.table_out_colnames = deepcopy(self.table_out_colnames)
        new.table_units = deepcopy(self.table_units)
        new.table_fibers = deepcopy(self.table_fibers)
        new.table_required = deepcopy(self.table_required)
        new.table_kind = deepcopy(self.table_kind)
        new.table_clears = deepcopy(self.table_clears)
        # return new copy
        return new

    def set_infile(self, params: ParamDict, row: Union[int, None] = None,
                   table: Union[Table, None] = None,
                   filename: Union[str, None] = None):
        """
        Set infile name from "filename" or from "row" in table (note table
        must have column "ABSPATH"

        :param params: ParamDict, the parameter dictionary of constants
        :param row: int or None, the row in "table" to set the filename
        :param table: Table or None, the table to get the row from
        :param filename: str or None, the filename to set the filename from

        :return: None - updates self.filename, self.datatype
        """
        if filename is not None:
            self.filename = filename
        else:
            self.filename = table['ABSPATH'][row]
        # deal with setting data type (unless already set which overrides)
        if self.drsfile == 'table':
            self.datatype = 'table'
        elif self.datatype is None:
            # deal with no data type
            # if self.drsfile is a single DrsFitsFile data type is easy
            if isinstance(self.drsfile, DrsFitsFile):
                self.datatype = self.drsfile.datatype
            # if we have multiple drsfiles we have to find the correct one
            #   it must be one of these by definition
            elif isinstance(self.drsfile, DrsFileGroup):
                # loop around all drs files
                for drsfile in self.drsfile.files:
                    # check we have a drs file
                    if isinstance(drsfile, DrsFitsFile):
                        # make a copy of the drs file
                        tmpdrsfile = drsfile.newcopy()
                        # set the drs file with the filename found in index db
                        tmpdrsfile.set_filename(self.filename)
                        # set params
                        tmpdrsfile.params = params
                        # check if this drs file is correct for filename
                        correct, _ = tmpdrsfile.check_file()
                        # if correct we set the drs file name
                        if correct:
                            self.datatype = drsfile.datatype
                            break
                    else:
                        continue
            # worst case we don't have a data type - do we need an exception
            #   here?
            else:
                self.datatype = None

    def load_infile(self, params: ParamDict):
        """
        Load infile for this extension

        :param params: ParamDict, parameter dictionary of constants
        :return:
        """
        # ---------------------------------------------------------------------
        # get data format
        if self.datatype == 'image':
            fmt = 'fits-image'
        elif self.datatype == 'table':
            fmt = 'fits-table'
        # default to fits-image
        else:
            fmt = 'fits-image'
        # ---------------------------------------------------------------------
        # deal with data only / header only
        if self.data_only:
            # want to read data from extname if set
            self.data = drs_fits.readfits(params, self.filename, True, False,
                                          fmt, extname=self.extname)
        elif self.header_only:
            # don't want to read header from self.extname (so use primary if
            #   hdr_extname is None -- the default, otherwise use hdr_extname)
            self.header = drs_fits.readfits(params, self.filename, False, True,
                                            fmt, extname=self.hdr_extname)
        else:
            # want to read data from extname if set
            self.data = drs_fits.readfits(params, self.filename, True, False,
                                          fmt, extname=self.extname)
            # don't want to read header from self.extname (so use primary if
            #   hdr_extname is None -- the default, otherwise use hdr_extname)
            self.header = drs_fits.readfits(params, self.filename, False, True,
                                            fmt, extname=self.hdr_extname)

    def make_table(self, params: ParamDict, ptable: Any, linkkind: str,
                   criteria: str, mode: str) -> Tuple[bool, textentry]:
        """
        Make a custom table for post files (using the info given when defined
        via DrsOutFile.add_column)

        :param params: ParamDict, parameter dictionary of constants
        :param ptable: index database instance
        :param linkkind: str, the link kind (column in index database)
        :param criteria: str, the link criteria (value of column in index
                         database)
        :param mode: str, either science, calibration or telluric (decides
                     how we try to get column filename)

        :return: None, updates self.data and self.datatype
        """
        # set function name
        func_name = display_func('make_table', __NAME__, self.class_name)
        # get allowed header keys
        pconst = load_functions.load_pconfig()
        iheader_cols = pconst.FILEINDEX_HEADER_COLS()
        rkeys = list(iheader_cols.names)
        # define table column parameters
        drsfiles = self.table_drsfiles
        incolumns = self.table_in_colnames
        outcolumns = self.table_out_colnames
        units = self.table_units
        fibers = self.table_fibers
        col_required = self.table_required
        block_kinds = self.table_kind
        all_clears = self.table_clears
        # ---------------------------------------------------------------------
        # define storage for values
        values = []
        use_cols = []
        use_units = []
        filenames = []
        clears = []
        # define storage for open tables (key = filename) so we don't open them
        #   more times than we need
        tables = dict()
        # header
        header = None
        # ---------------------------------------------------------------------
        # loop around columns and populate
        for col in range(len(outcolumns)):
            # deal with calibration mode
            if mode == 'calibration':
                eargs = [mode, self.pos, self.name, col]
                reason = textentry('00-090-00015', args=eargs)
                return False, reason
            # -----------------------------------------------------------------
            elif mode == 'telluric':
                eargs = [mode, self.pos, self.name, col]
                reason = textentry('00-090-00015', args=eargs)
                return False, reason
            # -----------------------------------------------------------------
            # if in science mode we query the index database (or ptable from
            #   index database) and return a row (or rows) associated with
            #   this entry --> from this we can set filename
            # -------------------------------------------------------------
            # add the hlink criteria
            condition = '{0}="{1}"'.format(linkkind, criteria)
            # set up index database condition
            # add kind (raw/tmp/red/out)
            condition += ' AND BLOCK_KIND="{0}"'.format(block_kinds[col])
            # -------------------------------------------------------------
            # get hkeys for this drsfile
            hkeys = drsfiles[col].required_header_keys
            # add hkeys from file
            if hkeys is not None and isinstance(hkeys, dict):
                # loop around each valid header key in index database
                for h_it, hkey in enumerate(rkeys):
                    # if we have the key in our header keys
                    if hkey in hkeys:
                        # get data type
                        dtype = iheader_cols.get_datatype(hkey)
                        # try to case and add to condition
                        hargs = [hkey, dtype, hkeys[hkey]]
                        # add to condition
                        condition += index_hkey_condition(*hargs)
            # add fiber
            if not drs_text.null_text(fibers[col], ['None', '']):
                condition += ' AND KW_FIBER="{0}"'.format(fibers[col])
            # -------------------------------------------------------------
            # first get entries from index database
            entries = ptable.get_index_entries('*', condition=condition)
            # -----------------------------------------------------------------
            # deal with no entries and column not required
            if len(entries) == 0 and not col_required[col]:
                continue
            # deal with no entries and column required
            elif len(entries) == 0:
                # log error and return: Column file for EXT={0} ({1}) not
                #     found. Condition = {2}
                eargs = [self.pos, self.name, condition, func_name]
                reason = textentry('00-090-00007', args=eargs)
                return False, reason
            else:
                # else take the first entry
                filename = entries['ABSPATH'][0]
                # append filenames
                filenames.append(filename)
            # -----------------------------------------------------------------
            # check for filename in storage
            if filename in tables:
                table = tables[filename]
            # if we haven't previously loaded table load it now
            else:
                # load table
                table = drs_table.read_table(params, filename, fmt='fits')
                # save to tables for caching
                tables[filename] = table
            # -----------------------------------------------------------------
            # read header
            if header is None:
                header = drs_fits.read_header(params, filename)
            # -----------------------------------------------------------------
            # check for column in table
            if incolumns[col] not in table.colnames:
                # log error and return: Column for EXT={0} ({1}) not found.
                #     Filename = {2} \n\t Column name = {3}
                eargs = [self.pos, self.name, filename, incolumns[col],
                         func_name]
                reason = textentry('00-090-00008', args=eargs)
                return False, reason
            # -----------------------------------------------------------------
            # get rows for this column
            row_values = np.array(table[incolumns[col]])
            # deal with wrong length
            if len(values) > 0:
                if len(values[0]) != len(row_values):
                    # log error and return Column for EXT={0} ({1}) wrong
                    #     length.  Filename = {2} \n\t Column name = {3}
                    eargs = [self.pos, self.name, filename, incolumns[col],
                             incolumns[0], len(values[0]), filenames[0],
                             incolumns[col], len(row_values), filenames[col],
                             func_name]
                    reason = textentry('00-090-00009', args=eargs)
                    return False, reason
            # -----------------------------------------------------------------
            # load column into values
            values.append(row_values)
            # save columns
            use_cols.append(outcolumns[col])
            # save units
            use_units.append(units[col])
            # save clear value for this col
            clears.append(all_clears[col])
        # ---------------------------------------------------------------------
        # print tables added
        for filename in tables:
            margs = [os.path.basename(filename)]
            WLOG(params, '', textentry('40-090-00007', args=margs),
                 colour='magenta')
        # ---------------------------------------------------------------------
        # deal with which files to clear
        # loop around filenames
        for col, filename in enumerate(filenames):
            # only do this if this column was flagged to clear file
            if clears[col]:
                # add to list for clearing later
                self.table_clear_files.append(filename)
        # ---------------------------------------------------------------------
        # make out table
        outtable = drs_table.make_table(use_cols, values,
                                        units=use_units)
        # ---------------------------------------------------------------------
        # load into data
        self.data = outtable
        self.datatype = 'table'
        self.header = header
        # ---------------------------------------------------------------------
        return True, None


# define exclude keys type optional dictionary keys=str, values=str/list[str]
EXCLUDE_KEYS_TYPE = Optional[Dict[str, Union[str, List[str]]]]


class DrsOutFile(DrsInputFile):
    # set class name
    class_name: str = 'DrsOutFile'

    def __init__(self, name: str, filetype: str,
                 suffix: Union[str, None] = None,
                 outclass: OutFileTypes = None,
                 inext=None, required: bool = True,
                 exclude_keys: EXCLUDE_KEYS_TYPE = None,
                 instrument: Optional[str] = None,
                 description: Union[str, None] = None,
                 inpath: Union[str, None] = None):
        """
        Drs class for post-processed output files

        :param name: str, a name for this out file
        :param filetype: str, the file type (i.e. .fits) for this file
        :param suffix: str, the output file suffix and extension
        :param outclass: PostOutFile, the associated outclass
        :param inext: str, any suffix/extension in the input filename to remove
        :param required: bool, whether this file is require (i.e. generate
                         error when we can't create it) if False skips on
                         error
        :param instrument: str, the instrument this file definition is
                           associated with
        :param description: str, the description of the file (for documentation)
        :param inpath: str or None, if set is a directory to look for the file
                       in - this is in exceptional cases and overrides normal
                       functionality
        """
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # define a name
        self.name = name
        # get super init
        DrsInputFile.__init__(self, name, filetype, suffix, outclass=outclass,
                              inext=inext, instrument=instrument, inpath=inpath,
                              required=required)
        # store extensions
        self.extensions = dict()
        self.header_add = dict()
        # specific data
        self.out_filename = None
        self.out_dirname = None
        self.out_required = required
        self.description = description
        # exceptions to be skipped without error
        self.exclude_keys = exclude_keys
        # store infiles
        self.infiles = []
        # store reduced files
        self.clear_files = []

    def summary(self, params: ParamDict,
                pconst: Optional[Instrument]) -> Dict[str, str]:
        """
        Custom summary for out files

        :param params: ParamDict, the paramater dictionary of constants
        :param pconst: PseudoConst, the psuedo constants class

        :return: dictionary, the parameters that define this file definition
        """
        # define the columns and values for returned dictionary
        columns = []
        values = []
        # we don't use params or pconst here but they are used in parent
        #   function - so we keep them here
        _ = params, pconst
        # ---------------------------------------------------------------------
        # add name of out file
        columns += ['name']
        values += [self.name]
        # ---------------------------------------------------------------------
        # add description
        columns += ['description']
        if self.description is not None:
            values.append(self.description)
        else:
            values.append('--')
        # ---------------------------------------------------------------------
        # get header keys
        header_keys = dict()
        for extnum in self.extensions:
            # get extension
            extension = self.extensions[extnum]
            # if we have hkeys add them to header keys dict
            if extension.hkeys is not None:
                for hkey in extension.hkeys:
                    header_keys[hkey] = ' |br| '.join(extension.hkeys[hkey])
        # get columns for header keys
        for hkey in header_keys:
            # add the column names
            columns.append('HDR[{0}]'.format(hkey))
            # add the value names
            values.append(header_keys[hkey])
        # ---------------------------------------------------------------------
        # add suffix
        columns += ['suffix']
        values += [self.suffix]
        # ---------------------------------------------------------------------
        # get extension names
        ext_names, ext_inputs = '', ''
        col_names, col_inputs = '', ''
        # loop around extensions
        for extnum in self.extensions:
            # get extension
            extension = self.extensions[extnum]
            # -----------------------------------------------------------------
            ext_name, ext_input, col_name, col_input = extension.summary(extnum)
            # add rows to entry
            for col in range(len(col_name)):
                ext_names += ' |br| {0}'.format(ext_name[col])
                ext_inputs += ' |br| {0}'.format(ext_input[col])
                col_names += ' |br| {0}'.format(col_name[col])
                col_inputs += ' |br| {0}'.format(col_input[col])
        # ---------------------------------------------------------------------
        # add extensions
        columns += ['ext name', 'ext input', 'col names', 'col input']
        values += [ext_names, ext_inputs, col_names, col_inputs]
        # ---------------------------------------------------------------------
        # return a dictionary of values
        return dict(zip(columns, values))

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

    def __str__(self) -> str:
        """
        Defines the str(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        # _ = display_func('__str__', __NAME__, self.class_name)
        # return the string representation of DrsInputFile
        return '{0}[{1}]'.format(self.class_name, self.name)

    def __repr__(self) -> str:
        """
        Defines the print(DrsInputFile) return for DrsInputFile
        :return str: the string representation of DrsInputFile
                     i.e. DrsInputFile[name]
        """
        # set function name
        # _ = display_func('__repr__', __NAME__, self.class_name)
        # return the string representation of DrsInputFile
        return 'DrsOutFile[{0}]'.format(self.name)

    def add_ext(self, name: str,
                drsfile: Union[DrsFileGroup, DrsFitsFile, str],
                pos: int, fiber: Union[str, None] = None,
                block_kind: Union[str, None] = None,
                hkeys: Union[dict, None] = None,
                link: Union[list, str, None] = None,
                hlink: Union[str, None] = None,
                header_only: bool = False, data_only: bool = False,
                remove_drs_hkeys: bool = False,
                remove_std_hkeys: bool = True,
                clear_file: bool = False,
                tag: Union[str, None] = None,
                extname: Union[str, None] = None,
                hdr_extname: Union[str, None] = None,
                datatype: Union[str, None] = None):
        """
        Add a fits extension

        First extension is the primary one and all others must be linked to
        this primary one

        :param name: str, the name of this extension
        :param drsfile: DrsFitsFile, a fits file to add
        :param fiber: str, the fiber
        :param block_kind: str, the block kind (i.e. (raw/tmp/red)
        :param hkeys: dict or None, if set is the dictionary of header keys
                      to add to fits extension
        :param pos: position within the fits file
        :param fiber: str or None, if set defines the fiber to use
        :param link: str, if set this must be a previously defined extension
                     name
        :param hlink: str, the header key from link extension to use for
                      filename for this extension
        :param header_only: bool, if True only adds the header (not the data)
        :param data_only: bool, if True only adds the data (not the header)
        :param remove_drs_hkeys: bool , if True removes drs header keys flagged
                                 to be remove (else does not remove keys)
        :param remove_std_hkeys: bool, if True removes a list of standard keys
                                 from this extensions header
        :param clear_file: bool, if True adds extension to list of files to
                           remove from disk if we are clearing reduced directory
                           after saving post process file
        :param tag: str, the extension name tag to give this extension in the
                    final post process file
        :param extname: str, if set this is the extension name from the
                        input file to take the image/table from
        :param hdr_extname: str, if set this forces taking the header from
                            the extension named here (otherwise uses primary)
        :param datatype: str, force 'image' or 'table' for extension

        :return:
        """
        # set function name
        func_name = display_func('__str__', __NAME__,
                                 self.class_name)
        # position must be an integer
        if not isinstance(pos, int):
            raise DrsCodedException('00-001-00053', level='error',
                                    targs=[pos, func_name])
        # add new extension instance
        self.extensions[pos] = DrsOutFileExtension(name, drsfile, pos, fiber,
                                                   block_kind, hkeys, link,
                                                   hlink, header_only,
                                                   data_only,
                                                   remove_drs_hkeys,
                                                   remove_std_hkeys,
                                                   clear_file, tag,
                                                   extname, hdr_extname,
                                                   datatype)

    def add_column(self, extname: str, drsfile: DrsFitsFile,
                   incol: str, outcol: str, fiber: Union[str, None],
                   units: Union[str, None] = None, required: bool = True,
                   block_kind: str = 'red', clear_file: bool = False):
        """
        If an extension is a table add a column from a table fits file

        :param extname: str, the extension name
        :param drsfile: drs fits file instance - must be a fits bin table
        :param incol: str, the input column name
        :param outcol: str, the output column name
        :param fiber: str or None, if set set the fiber name
        :param units: str or None, if set sets the units for a columns
        :param required: bool, if False column is not required
        :param block_kind: str, the blcok kind (raw/tmp/red/out)
        :param clear_file: bool, sets whether the file that creates this column
                           should be cleared if/when we are clearing red files
        :return:
        """
        # get extension
        extension = self.extensions[self._pos_from_name(extname)]
        # check extension is a DrsOutFileExtension
        if isinstance(extension, DrsOutFileExtension):
            # check for drsfile == table
            if extension.drsfile != 'table':
                raise ValueError('Extension is not a table')
            # add the table
            extension.add_table_column(drsfile, incol, outcol, fiber, units,
                                       required, block_kind, clear_file)

    def add_hkey(self, key: str, inheader: str, outheader: str):
        """
        Flag that we need to add/replace a header key from "inheader"
        to "outheader" (both of these should be extension names added by
        add_ext)

        :param key: str, the header key to add (raw name or keyword store name
                    in params)
        :param inheader: str, the input extension (copy header key from this
                         extensions header)
        :param outheader: str, the output extension (copy header key to this
                          extensions header)

        :return:
        """
        self.header_add[key] = [inheader, outheader]

    def _pos_from_name(self, name):
        # get positions
        positions = list(self.extensions.keys())
        # get DrsOutExtension instances
        instances = list(self.extensions.values())
        # get the names for each position
        names = list(map(lambda x: x.name, instances))
        # make a translation dictionary
        translate = dict(zip(names, positions))
        # return the position for this name
        if name not in translate:
            return None
        else:
            return translate[name]

    def find_files(self, pos: int, findexdbm: Any,
                   refcond: Union[str, None]) -> pd.DataFrame:
        """
        Find files that match the extension parameters in the index database

        :param pos: int, the position in the extension list
        :param findexdbm: Index database, the index database
        :param refcond: str, the reference condition

        :return: pandas data frame containing the table of files
        """
        # get extension 0
        extension = self.extensions[pos]
        # get the index table for first extension
        table0 = findexdbm.get_entries('*', block_kind=extension.kind,
                                       hkeys=extension.hkeys,
                                       condition=refcond)
        # return table
        return table0

    def copy(self) -> 'DrsOutFile':
        """
        Copy a Drs Out File
        
        creates a new DrsOutFile and deep copies attributes into it
        
        :return: new DrsOutFile deep copy of 'self'
        """
        # set function name
        # _ = display_func('__init__', __NAME__, self.class_name)
        # get new copy of drs out file
        new = DrsOutFile(self.name, self.filetype, self.suffix, self.outclass,
                         self.inext)
        # copy extensions
        for ext in self.extensions:
            new.extensions[ext] = self.extensions[ext].copy()
        # copy header adds
        for key in self.header_add:
            new.header_add[key] = list(self.header_add[key])
        # copy whether required
        new.out_required = bool(self.out_required)
        # specific data
        new.out_filename = deepcopy(self.out_filename)
        new.out_dirname = deepcopy(self.out_dirname)
        new.out_required = deepcopy(self.out_required)
        # exceptions to be skipped without error
        new.exclude_keys = deepcopy(self.exclude_keys)
        # store infiles
        new.infiles = deepcopy(self.infiles)
        # store reduced files
        new.clear_files = deepcopy(self.clear_files)
        # copy instrument
        new.instrument = deepcopy(self.instrument)
        # copy description
        new.description = deepcopy(self.description)
        # return new copy
        return new

    def has_header(self) -> Tuple[np.ndarray, List[str]]:
        """
        Checks for header in each extension
        
        :return: tuple, 1. True or False for each header, 2. the name of each
                 extension (as defined in header)
        """
        # assume no headers are loaded
        value = np.zeros(len(self.extensions), dtype=bool)
        names = []
        # check for loaded headers
        for it, pos in enumerate(self.extensions):
            if self.extensions[pos].header is not None:
                value[it] = True
                names.append(self.extensions[pos].name)
        # return value
        return value, names

    def process_links(self, params: ParamDict, findexdbm: Any,
                      calibdbm: Any, telludbm: Any,
                      required: bool = True) -> Tuple[bool, Union[Text, None]]:
        """
        Process the linked extensions

        :param params: ParamDict, parameter dictionary of constants
        :param findexdbm: Index Database instance
        :param calibdbm: Calibration Database instance
        :param telludbm: Telluric Database instance
        :param required: bool, whether file is required or not

        :return: bool, whether we successfully linked all extensions
        """
        # set function name
        func_name = display_func('process_links', __NAME__, self.class_name)
        # get allowed header keys
        pconst = load_functions.load_pconfig()
        iheader_cols = pconst.FILEINDEX_HEADER_COLS()
        rkeys = list(iheader_cols.names)
        # must have primary filename set
        if self.extensions[0].filename is None:
            # log error and return
            reason = textentry('00-090-00001', args=func_name)
            return False, reason
        # ---------------------------------------------------------------------
        # get full database (will need it multiple times and should not
        #   change between reads) and store it as a pandas table
        pcond = '(BLOCK_KIND="tmp") OR (BLOCK_KIND="red")'
        # set observation directory to "All"
        obs_dir = textentry('ALL_TEXT')
        # add to obs_dir if present (as we will only need files from this
        #   observation directory)
        if not drs_text.null_text(params['OBS_DIR'], ['None', '', 'Null']):
            pcond += ' AND (OBS_DIR="{0}")'.format(params['OBS_DIR'])
            obs_dir = str(params['OBS_DIR'])
        # this may take some time print message:
        #     Loading full database. OBS_DIR={0}. Please wait...'
        margs = [obs_dir]
        WLOG(params, '', textentry('40-090-00003', args=margs))
        # start a clock (reading large database is slow - give user feedback)
        start = time.time()
        pdataframe = findexdbm.get_entries('*', condition=pcond)
        # ptable = PandasLikeDatabase(pdataframe)
        ptable = PandasLikeDatabase(pdataframe)
        # end the clock  (reading large database is slow - give user feedback)
        end = time.time()
        # log full database loaded in X s
        WLOG(params, '', textentry('40-090-00004', args=[end - start]))
        # get index columns
        # index_cols = ptable.colnames()
        idbcols = pconst.FILEINDEX_DB_COLUMNS()
        index_cols = list(idbcols.names)

        # ---------------------------------------------------------------------
        # get information about loaded files
        has_hdr, valid_names = self.has_header()
        # loop around extensions
        for pos in self.extensions:
            # get ext
            ext = self.extensions[pos]
            # cannot link primary extension
            if pos == 0:
                # get message arguments
                margs = [pos, ext.name, 'primary']
                # log progress
                if ext.header_only:
                    msg = textentry('40-090-00005', args=margs)
                else:
                    msg = textentry('40-090-00006', args=margs)
                WLOG(params, '', msg)
                # add filename
                margs = [os.path.basename(ext.filename)]
                WLOG(params, '', textentry('40-090-00007', args=margs),
                     colour='magenta')
                # skip to next extension
                continue
            # -----------------------------------------------------------------
            # get extension name
            name = ext.name
            # get drsfile hkeys
            if isinstance(ext.drsfile, str):
                hkeys = None
            elif isinstance(ext.drsfile, list):
                hkeys = dict()
                for drsfile in ext.drsfile:
                    if isinstance(drsfile, DrsFitsFile):
                        # get required keys
                        tmp_hkeys = drsfile.required_header_keys
                        # loop around keys
                        for key in tmp_hkeys:
                            # deal with key already existing
                            if key in hkeys:
                                hkeys[key].append(tmp_hkeys[key])
                            # deal with no key existing
                            else:
                                hkeys[key] = [tmp_hkeys[key]]
            elif isinstance(ext.drsfile, DrsFitsFile):
                hkeys = ext.drsfile.required_header_keys
            else:
                hkeys = dict()
            # -----------------------------------------------------------------
            # get link position
            if ext.link not in valid_names:
                # log message and return: Link name={0} not valid for
                #      extension {1} ({2}) \n\t Valid link names: {3}
                eargs = [ext.link, pos, name, ', '.join(valid_names),
                         func_name]
                reason = textentry('00-090-00002', args=eargs)
                return False, reason
            # -----------------------------------------------------------------
            # get the link parameters
            linkext = self.extensions[self._pos_from_name(ext.link)]
            # need the linkext header
            linkhdr = linkext.header
            # get the hlink
            hlink = ext.hlink
            # -----------------------------------------------------------------
            # check for calibration / telluric entry
            if hlink.startswith('CALIB::'):
                mode, dbkey = 'calibration', hlink.split('CALIB::')[-1]
            elif hlink.startswith('TELLU::'):
                mode, dbkey = 'telluric', hlink.split('TELLU::')[-1]
            else:
                mode, dbkey = 'science', None
            # -----------------------------------------------------------------
            # if in calib/tellu mode try to find file in calib/tellu file
            # -----------------------------------------------------------------
            # deal with calibration mode
            if mode == 'calibration':
                # try to find the calibration entry that matches the link header
                cout = calibdbm.get_calib_file(dbkey, header=linkhdr,
                                               fiber=ext.fiber, required=False)
                # get the calibration filename
                cfilename = cout[0]
                # deal with no filename found
                if cfilename is None:
                    eargs = [dbkey, ext.pos, ext.name, linkext.pos,
                             linkext.name, linkext.filename, func_name]
                    reason = textentry('00-090-00013', args=eargs)
                    return False, reason
                # get criteria from calibration filename
                criteria = str(cfilename)
                # set link kind
                linkkind = None
                # add table
                exttable = Table()
                exttable['ABSPATH'] = [cfilename]
            # -----------------------------------------------------------------
            elif mode == 'telluric':
                # try to find the telluric entry that matches the link header
                tfilename = telludbm.get_tellu_file(dbkey, header=linkhdr,
                                                    fiber=ext.fiber,
                                                    required=False)
                # deal with no filename found
                if tfilename is None:
                    eargs = [dbkey, ext.pos, ext.name, linkext.pos,
                             linkext.name, linkext.filename, func_name]
                    reason = textentry('00-090-00014', args=eargs)
                    return False, reason
                # get criteria from telluric filename
                criteria = str(tfilename)
                # set link kind
                linkkind = None
                # add table
                exttable = Table()
                exttable['ABSPATH'] = [tfilename]
            # -----------------------------------------------------------------
            # if in science mode we query the index database (or ptable from
            #   index database) and return a row (or rows) associated with
            #   this entry --> from this we can set filename
            # -----------------------------------------------------------------
            else:
                # need to check for hlink in params
                if hlink not in params:
                    # log message and return: Header link key={0} not valid for
                    #     link name={1}\n\tlink file={2}\n\tFunction = {3}
                    eargs = [ext.hlink, ext.link, linkext.filename, func_name]
                    reason = textentry('00-090-00003', args=eargs)
                    return False, reason
                # -------------------------------------------------------------
                # get the header key associated with hlink
                hdrhlink = params[hlink][0]
                # need to check for params[hlink] in header
                if hdrhlink not in linkhdr:
                    # log message and return: Header link key={0} is not valid
                    #     for link name={1}\n\theader key "{2}" not found
                    #     \n\tlink file={3}\n\tFunction={4}
                    eargs = [ext.hlink, ext.link, hdrhlink, linkext.filename,
                             func_name]
                    reason = textentry('00-090-00004', args=eargs)
                    return False, reason
                # -------------------------------------------------------------
                # use the hlink to get the link criteria
                criteria = linkhdr[hdrhlink]
                # we need to figure out whether we have a database criteria
                #    link  or whether the link will be a filename
                if hlink in index_cols:
                    linkkind = str(hlink)
                else:
                    linkkind = 'FILENAME'
                # -------------------------------------------------------------
                # look for critera in index database (to get absolute path
                # and to filter by fiber
                # -------------------------------------------------------------
                # add the hlink criteria
                condition = '{0}="{1}"'.format(linkkind, criteria)
                # add kind condition
                condition += ' AND BLOCK_KIND="{0}"'.format(ext.block_kind)
                # add hkey conditions
                if hkeys is not None and isinstance(hkeys, dict):
                    # loop around each valid header key in index database
                    for h_it, hkey in enumerate(rkeys):
                        # if we have the key in our header keys
                        if hkey in hkeys:
                            # get data type
                            dtype = iheader_cols.get_datatype(hkey)
                            # try to case and add to condition
                            hargs = [hkey, dtype, hkeys[hkey]]
                            # add to condition
                            condition += index_hkey_condition(*hargs)
                # add fiber condition (if present)
                if ext.fiber is not None:
                    condition += ' AND KW_FIBER="{0}"'.format(ext.fiber)
                # get entries
                exttable = ptable.get_index_entries('*', condition=condition)
                # deal with no entries and not required
                if len(exttable) == 0 and not required:
                    # print warning: File not found for ext {0} ({1})'
                    margs = [pos, name]
                    reason = textentry('10-090-00003', args=margs)
                    return False, reason
                # deal with no entries and required
                if len(exttable) == 0:
                    # log and return: No entries for extension {0} ({1})
                    #    \n\t condition = {2}
                    eargs = [pos, name, condition, func_name]
                    reason = textentry('00-090-00005', args=eargs)
                    return False, reason

            # -----------------------------------------------------------------
            # deal with drsfile as a custom table
            # -----------------------------------------------------------------
            if ext.drsfile == 'table':
                try:
                    # use first row that has a runstring (if any)
                    extrow = decide_on_table_row(exttable)
                    # add extension file properties
                    ext.set_infile(params, extrow, exttable)
                    # log progress: Adding EXT={0} ({1}) [TABLE]'
                    margs = [pos, name, mode]
                    WLOG(params, '', textentry('40-090-00008', args=margs))
                    # make the table
                    success, reason = ext.make_table(params, ptable, linkkind,
                                                     criteria, mode)
                    # deal with not being able to make table
                    if not success:
                        return False, reason
                    # deal with reduced data
                    self._add_to_clear_files(ext)
                except Exception as e:
                    eargs = ['table', pos, name, ext.filename, type(e), str(e),
                             func_name]
                    # log and return: Could not add extension
                    reason = textentry('00-090-00006', args=eargs)
                    return False, reason
            # -----------------------------------------------------------------
            # else take the first entry
            # -----------------------------------------------------------------
            else:
                try:
                    # use first row that has a runstring (if any)
                    extrow = decide_on_table_row(exttable)
                    # add extension file properties
                    ext.set_infile(params, extrow, exttable)
                    # load the extension file
                    ext.load_infile(params)
                    # deal with reduced data
                    self._add_to_clear_files(ext)
                    # log progress: Adding EXT={0} ({1}) [Header only]
                    margs = [pos, name, mode]
                    if ext.header_only:
                        msg = textentry('40-090-00005', args=margs)
                    else:
                        msg = textentry('40-090-00006', args=margs)
                    WLOG(params, '', msg)
                    # add filename
                    msg = '\t\tFile: {0}'
                    margs = [os.path.basename(ext.filename)]
                    WLOG(params, '', msg.format(*margs), colour='magenta')
                except Exception as e:
                    eargs = ['image', pos, name, ext.filename, type(e), str(e),
                             func_name]
                    # log and return: Could not add extension
                    reason = textentry('00-090-00006', args=eargs)
                    return False, reason
            # -----------------------------------------------------------------
            # finally update the loaded files
            has_hdr, valid_names = self.has_header()
        # ---------------------------------------------------------------------
        # return that we linked successfully
        return True, None

    def process_header(self, params: ParamDict):
        """
        Process the headers now they are all present

        :param params: ParamDict, parameter dictionary of constants
        
        :return: None, updates keys/values in self
        """
        # deal with removing drs keys
        self._remove_drs_keys(params)
        # deal with removing standard keys from primary header
        self._remove_standard_keys(params)
        # deal with adding keys from one header to another
        self._add_header_keys(params)
        # remove keys that are in primary and in extensions
        # TODO: Add back in with a skip for certain files?
        # self._remove_duplicate_keys(params)
        # add extension names as comments
        self._add_extensions_names_to_primary(params)

    def check_header_skip(self, ext: int = 0) -> bool:
        """
        Check whether we should skip this file due to an exclude key
        matching a value that should be skipped (i.e. exclude_keys was set)

        :param ext: int, the extension to check

        :return: bool, True if we should skip file, False otherwise
        """
        # deal with no exclude keys
        if self.exclude_keys is None:
            return False
        # deal with exclude keys - make all entry values a list
        exclude_keys = self.exclude_keys
        for ekey in exclude_keys:
            if isinstance(exclude_keys[ekey], str):
                exclude_keys[ekey] = [exclude_keys[ekey]]
        # ---------------------------------------------------------------------
        # if we don't have extension just return
        if ext not in self.extensions:
            return False
        # ---------------------------------------------------------------------
        # if we don't have header just return here
        if self.extensions[ext].header is None:
            return False
        # ---------------------------------------------------------------------
        # load the header for this extension
        header = self.extensions[ext].header
        # assume file is not going to be skipped
        skip = False
        # loop around exclude keys
        for ekey in exclude_keys:
            # need to look up key in params
            if ekey in self.params:
                drsekey = self.params[ekey][0]
            else:
                drsekey = str(ekey)
            # if key is in header check value
            if drsekey in header:
                # loop around all keys in exclude keys
                for evalue in exclude_keys[ekey]:
                    if header[drsekey] == evalue:
                        # set skip to True
                        skip = True
                        # log that we are skipping file
                        msg = '\tSkipping {0} for {1} ({2} = {3})'
                        margs = [self.extensions[ext].filename,
                                 self.name, drsekey, evalue]
                        WLOG(self.params, '', msg.format(*margs))
        # return whether we should skip file
        return skip

    def set_db_infiles(self, block_kind: str, database: Any):
        """
        Set the "infiles" for use in indexing - this takes the
        index database entry for extension 1 (or 0 if 1 not present) and
        puts the "INFILES" column into self.infiles

        :param block_kind: str, which block kind (raw/tmp/red etc) are the
                           infile coming from
        :param database: IndexDatabase, the database instance

        :return: None, updates self.infiles
        """
        # get filename to crossmatch with database
        if len(self.extensions) > 1:
            filename = self.extensions[1].filename
        else:
            filename = self.extensions[0].filename
        # observation directory
        obs_dir = self.obs_dir
        # condition on database
        ctxt = 'BLOCK_KIND="{0}" AND OBS_DIR="{1}" AND FILENAME="{2}"'
        cargs = [block_kind, obs_dir, os.path.basename(filename)]
        condition = ctxt.format(*cargs)
        # get database entries
        dkwargs = dict(condition=condition, return_pandas=True)
        # try to get infiles from database
        table = database.database.get('*', **dkwargs)
        # deal with no entries
        if len(table) == 0:
            rawinfiles = []
        # else just keep last entry
        else:
            rawinfiles = str(table['INFILES'].iloc[-1]).split(',')
        # clean entries
        infiles = []
        for rawinfile in rawinfiles:
            if not drs_text.null_text(rawinfile, ['None', 'Null', '']):
                infiles.append(rawinfile)
        # set the infiles
        self.infiles = list(infiles)

    def _add_header_keys(self, params: ParamDict):
        """
        Add header keys from one extension to another

        :param params ParamDict, the parameter dictionary of constants

        :return:
        """
        # loop around all header keys
        for key in self.header_add:
            # get the in extension
            inext = self.header_add[key][0]
            outext = self.header_add[key][1]
            inpos = self._pos_from_name(inext)
            outpos = self._pos_from_name(outext)
            # -----------------------------------------------------------------
            # deal with header keys that are keyword stores in params
            if key in params:
                drs_key = params[key][0]
            else:
                drs_key = str(key)
            # -----------------------------------------------------------------
            # make sure we have the in/out extensions for this key
            if inpos is None:
                # Cannot add hkey {0} (in extension {1} does not exist)
                eargs = [drs_key, inext, 'inpos']
                raise drs_log.AperoCodedException(params, '00-090-00011',
                                                  targs=eargs)
            if outpos is None:
                # Cannot add hkey {0} (out extension {1} does not exist)
                eargs = [drs_key, inext, 'outpos']
                raise drs_log.AperoCodedException(params, '00-090-00011',
                                                  targs=eargs)

            # -----------------------------------------------------------------
            # make sure we have the in header for this key
            if self.extensions[inpos].header is None:
                # Cannot add hkey {0} (in header {1} does not exist)
                eargs = [drs_key, inext, 'inheader=None']
                raise drs_log.AperoCodedException(params, '00-090-00011',
                                                  targs=eargs)
            else:
                inheader = self.extensions[inpos].header
            # make sure we have the out header for this key
            if self.extensions[outpos].header is None:
                # Cannot add hkey {0} (out header {1} does not exist)
                eargs = [drs_key, inext, 'outheader=None']
                raise drs_log.AperoCodedException(params, '00-090-00011',
                                                  targs=eargs)
            else:
                outheader = self.extensions[outpos].header
            # -----------------------------------------------------------------
            # get key from in header and push into out header
            if drs_key not in inheader:
                # Cannot add hkey {0} (in header {1} does not have header key
                eargs = [drs_key, inext]
                raise drs_log.AperoCodedException(params, '00-090-00012',
                                                  targs=eargs)
            # get value
            value = inheader[drs_key]
            comment = inheader.comments[drs_key]
            # push into outheader
            outheader[drs_key] = (value, comment)
            # push it back into header
            self.extensions[outpos].header = outheader

    def _remove_drs_keys(self, params: ParamDict):
        """
        For each extension if remove_drs_keys is True we need to go through
        and remove drs keys that are flagged for removal

        :param params ParamDict, the parameter dictionary of constants

        :return:
        """
        # get all Keyword parameters
        keywords = []
        # ---------------------------------------------------------------------
        # loop around all param instances
        for key in params.instances:
            if isinstance(params.instances[key], Keyword):
                # add all keyword instances to storage
                keywords.append(params.instances[key])
        # ---------------------------------------------------------------------
        # get drs keys that are flagged for removal
        remove_keys = []
        # loop around all keyword instances
        for keyword in keywords:
            # check post exclude key
            if keyword.post_exclude:
                # add just the keyword key name to storage
                remove_keys.append(keyword.key)
        # ---------------------------------------------------------------------
        # loop around extensions
        for pos in self.extensions:
            # make sure extension has header
            if self.extensions[pos].header is None:
                continue
            # get header
            header = self.extensions[pos].header
            # see if this extension is flagged for drs header key removal
            if self.extensions[pos].remove_drs_hkeys:
                # loop around remove keys
                for key in remove_keys:
                    # need to deal with format keys
                    if '{' in key:
                        key = key.split('{')[0] + '*'
                    # get keys
                    hkey = header.get(key, None)
                    # need to deal with the return types of get here
                    #    (str or None or header card)
                    if isinstance(hkey, drs_fits.fits.Header):
                        hkeys = list(hkey.keys())
                    # if not a header instance we just add the key
                    elif hkey is not None:
                        hkeys = [key]
                    # if none don't do anything
                    else:
                        hkeys = []
                    # remove these keys (in a loop)
                    for hkey in hkeys:
                        if hkey in header:
                            # delete key
                            del header[key]
                # push header back to extension
                self.extensions[pos].header = header

    def _remove_standard_keys(self, params: ParamDict):
        """
        Remove standard keys from a header if extension was flagged as having
        remove_std_hkeys

        :param pconst: PsuedoConst, the instrument pseudo constants

        :return:
        """
        # get standard keys from pconst
        remove_keys = params['FORBIDDEN_OUT_KEYS']
        # loop around each extension
        for pos in self.extensions:
            # make sure extension has header
            if self.extensions[pos].header is None:
                continue
            # get header
            header = self.extensions[pos].header
            # see if this extension is flagged for drs header key removal
            if self.extensions[pos].remove_std_hkeys:
                # loop around remove keys
                for key in remove_keys:
                    # make sure key is in extension
                    if key in header:
                        # delete key
                        del header[key]
                # push header back to extension
                self.extensions[pos].header = header

    def _remove_duplicate_keys(self, params: ParamDict):
        """
        Remove keys that are both in primary and extension

        :param params ParamDict, the parameter dictionary of constants
        :param pconst: PsuedoConst, the instrument pseudo constants

        :return:
        """
        # get keys not to check
        skip_keys = params['NON_CHECK_DUPLICATE_KEYS']
        # get primary extension
        header0 = self.extensions[0].header
        # loop around extensions
        for pos in self.extensions:
            # skip extension 0
            if pos == 0:
                continue
            # get extension header
            header = self.extensions[pos].header
            # deal with no header
            if header is None:
                continue
            # loop around header0 and look for duplicates
            for key in header0:
                # skip some
                if key in skip_keys:
                    continue
                # check if key is identical
                if header.get(key) == header0[key]:
                    # remove key
                    del header[key]
                # else give warning that a primary key changed value
                #  (this shouldn't happen)
                else:
                    # log warning: Header key {0} expected in extension but
                    #    value changed
                    wargs = [key, pos, self.extensions[pos].name]
                    # header key changed - this is should not happen but
                    #   isn't a big problem
                    WLOG(params, 'warning',
                         textentry('10-090-00004', args=wargs), sublevel=2)

    def _add_extensions_names_to_primary(self, params: ParamDict):
        """
        Add extensions as comments to primary header

        :param params:
        :return:
        """
        # get primary header
        header = self.extensions[0].header
        # get key to add comment near
        hdrkey = params['POST_HDREXT_COMMENT_KEY']
        # if hdrkey is in params then we have a keyword store and need just to
        #   get the keyword store name
        if hdrkey in params:
            hdrkey = params[hdrkey][0]
        # make comment
        description = 'This file contains the following extensions: '
        # get the names of all (non primary) extensions
        names = []
        for pos in self.extensions:
            # TODO: This may not be .name but .commentname (from Chris)
            # do not add primary extension
            if pos == 0:
                continue
            # add name to names
            if self.extensions[pos].tag is not None:
                names.append(self.extensions[pos].tag)
            else:
                names.append(self.extensions[pos].name)
        # add extensions
        description += ', '.join(names)
        # add to header
        for line in textwrap.wrap(description, 71):
            header.insert(hdrkey, ('COMMENT', line))
        # finally add the number of extensions to the primary header
        nextend_comment = 'Number of standard extensions'
        header['NEXTEND'] = (len(self.extensions) - 1, nextend_comment)
        # add header back to extensions
        self.extensions[0].header = header

    def _add_to_clear_files(self, ext: DrsOutFileExtension):
        """
        Check whether file is flagged to be cleaned and add it to the list
        to remove (only removed at the end of the processes)

        :param ext: DrsOutFileExtension - the extension instance

        :return: None - updates self.reduced_files if required
        """
        # see if our filename startswith reduced_directory
        if ext.clear_file:
            # check that filename is not already in the list
            if ext.filename not in self.clear_files:
                if ext.filename is not None:
                    # make sure filename does not contain sym links
                    filename = ext.filename
                    # add to clear files
                    self.clear_files.append(filename)
        # deal with table column clear files
        if len(ext.table_clear_files) > 0:
            # loop around clear files
            for filename in ext.table_clear_files:
                # check that filename is not already in the list
                if filename not in self.clear_files:
                    self.clear_files.append(filename)

    def write_file(self, block_kind: str, runstring: Union[str, None] = None):
        # set function name
        func_name = display_func('write_file', __NAME__,
                                 self.class_name)
        # deal with no save
        if self.no_save():
            wmsg = 'NOSAVE active - file not written to disk'
            WLOG(self.params, 'warning', wmsg)
            return
        # construct data list
        data_list = []
        for ext in self.extensions:
            data_list.append(self.extensions[ext].data)
        # construct header list
        header_list = []
        for ext in self.extensions:
            header_list.append(self.extensions[ext].header)
        # construct data type list
        datatype_list = []
        for ext in self.extensions:
            datatype_list.append(self.extensions[ext].datatype)
        # names of extensions
        names = []
        for ext in self.extensions:
            if self.extensions[ext].tag is not None:
                names.append(self.extensions[ext].tag)
            else:
                names.append(self.extensions[ext].name)
        # deal with dtypes
        dtypelist = [None] * len(names)
        # must make sure dirname exists
        if not os.path.exists(self.out_dirname):
            os.makedirs(self.out_dirname)
        # writefits to file
        drs_fits.writefits(self.params, self.out_filename, data_list,
                           header_list, names, datatype_list, dtypelist,
                           func=func_name)
        # write output dictionary
        self.output_dictionary(block_kind, runstring)

    def output_dictionary(self, block_kind: str,
                          runstring: Union[str, None] = None,
                          recipe: Union[Any, None] = None):
        """
        Generate the output dictionary (for use while writing)
        Uses OUTPUT_FILE_HEADER_KEYS and DrsFile.hdict to generate an
        output dictionary for this file (for use in indexing)

        Requires DrsFile.filename and DrsFile.params to be set

        :params block_kind: str, the block kind (raw/tmp/red)
        :params runstring: str, the run string that created this recipe run

        :return None:
        """
        # set function name
        func_name = display_func('output_dictionary', __NAME__,
                                 self.class_name)
        # check that params is set
        self.check_params(func_name)
        params = self.params
        pconst = load_functions.load_pconfig()
        # get required keys for index database
        iheader_cols = pconst.FILEINDEX_HEADER_COLS()
        hkeys = list(iheader_cols.names)
        # deal with absolute path of file
        self.output_dict['ABSPATH'] = str(self.filename)
        # deal with night name of file
        self.output_dict['OBS_DIR'] = str(self.params['OBS_DIR'])
        # deal with basename of file
        self.output_dict['FILENAME'] = str(self.basename)
        # deal with kind
        self.output_dict['BLOCK_KIND'] = str(block_kind)
        # deal with last modified time for file
        if Path(self.filename).exists():
            last_mod = Path(self.filename).lstat().st_mtime
            used = 1
        else:
            last_mod = np.nan
            used = 0
        self.output_dict['LAST_MODIFIED'] = last_mod
        # deal with the run string (string that can be used to re-run the
        #     recipe to reproduce this file)
        if runstring is None:
            self.output_dict['RUNSTRING'] = 'None'
            # deal with recipe
            self.output_dict['RECIPE'] = 'Unknown'
        else:
            self.output_dict['RUNSTRING'] = str(runstring)
            # deal with recipe
            self.output_dict['RECIPE'] = str(runstring).split()[0]
        # add the infiles
        self.output_dict['INFILES'] = '|'.join(self.infiles)
        # add whether this row should be used be default (always 1)
        self.output_dict['USED'] = used
        # add the raw fix (all files here should be raw fixed)
        self.output_dict['RAWFIX'] = 1
        # get primary header
        header = self.extensions[0].header
        # some keys have to be set manually
        manual_keys = dict()
        manual_keys['KW_PID'] = params['PID']
        manual_keys['KW_VERSION'] = params['DRS_VERSION']
        manual_keys['KW_FIBER'] = 'None'
        manual_keys['KW_OUTPUT'] = self.name
        # ---------------------------------------------------------------------
        # loop around the keys and find them in hdict (or add null character if
        #     not found)
        for it, key in enumerate(hkeys):
            # deal with header key stores
            if key in params:
                dkey = params[key][0]
            else:
                dkey = str(key)
            # get dtype
            dtype = iheader_cols.get_datatype(key)
            # set found
            found = False
            # add key if in hdict (priority)
            if dkey in header:
                # noinspection PyBroadException
                try:
                    self.output_dict[key] = dtype(header[dkey])
                    found = True
                except Exception as _:
                    self.output_dict[key] = 'None'
            if not found:
                self.output_dict[key] = 'None'
        # copy over the manual keys
        for manual_key in manual_keys:
            self.output_dict[manual_key] = manual_keys[manual_key]


# =============================================================================
# User DrsFile functions
# =============================================================================
def check_input_qc(params: ParamDict, drsfiles: List[DrsFitsFile],
                   filekind: str, required: bool = True) -> List[DrsFitsFile]:
    """
    Check the input files pass quality control
    (unless we are not forcing qc to be correct)

    :param params: ParamDict, parameter dictionary of constants
    :param drsfiles: DrsFitsFile or list of DrsFitsFile, the files to test
                     (only tests files with headers)
    :param filekind: str, filename for print outs
    :param required: bool, if False does not raise error on no files

    :raises: DrsException if no files pass qc
    :return: updated list of DrsInputFile - if some files pass qc will return
             only these to be used
    """
    # do not check if flag is false
    if 'INPUTS' in params:
        if 'NO_IN_QC' in params['INPUTS']:
            if drs_text.true_text(params['INPUTS']['NO_IN_QC']):
                return drsfiles
    # -------------------------------------------------------------------------
    # print progress
    WLOG(params, '', textentry('40-005-10004', args=[filekind]))
    # -------------------------------------------------------------------------
    # storage for return
    valid_drsfiles = []
    bad_drsfiles = dict()
    # loop around all files
    for drsfile in drsfiles:
        # ---------------------------------------------------------------------
        # do not check non-fits files
        if not isinstance(drsfile, DrsFitsFile):
            valid_drsfiles.append(drsfile)
            continue
        # ---------------------------------------------------------------------
        # if we don't have a header we assume this file is bad
        if not hasattr(drsfile, 'header'):
            reason = 'No header attribute'
            bad_drsfiles[drsfile.filename] = reason
            continue
        # ---------------------------------------------------------------------
        # if header is not populated we assume this file is bad
        if not isinstance(drsfile.header, (Header, FitsHeader)):
            reason = 'Header not loaded'
            bad_drsfiles[drsfile.filename] = reason
            continue
        # ---------------------------------------------------------------------
        # if there is no qc key we assume file passes
        if not params['KW_DRS_QC'][0] in drsfile.header:
            valid_drsfiles.append(drsfile)
            continue
        # ---------------------------------------------------------------------
        if drsfile.header[params['KW_DRS_QC'][0]]:
            valid_drsfiles.append(drsfile)
            continue
        else:
            reason = '{0} = False'.format(params['KW_DRS_QC'][0])
            bad_drsfiles[drsfile.filename] = reason
            continue
    # -------------------------------------------------------------------------
    # deal with files failing input qc test
    # print error message if we have no files
    if len(valid_drsfiles) == 0 and required:
        # print msg: no valid input {0} files after QC test:
        emsg = textentry('09-001-00033', args=[filekind])
        # loop around bad files
        for bad_drsfile in bad_drsfiles:
            eargs1 = [bad_drsfile, bad_drsfiles[bad_drsfile]]
            emsg += '\n\t - {0}: {1}'.format(*eargs1)
        # report error: No valid files after QC
        raise drs_log.AperoCodedException(params, '09-001-00033',
                                          message=emsg)

    elif len(valid_drsfiles) != len(drsfiles):
        # print warning msg: Some input {0} failed QC test - Removing:
        wargs = [filekind]
        wmsg = textentry('10-001-00013', args=wargs)
        # loop around bad files
        for bad_drsfile in bad_drsfiles:
            wargs1 = [bad_drsfile, bad_drsfiles[bad_drsfile]]
            wmsg += '\n\t\t - {0}: {1}'.format(*wargs1)
        # report error: No valid files after QC
        WLOG(params, 'warning', wmsg.format(*wargs), sublevel=3)
    else:
        # print msg: All input {0} files passed QC'
        WLOG(params, '', textentry('40-005-10005', args=[filekind]))
    # -------------------------------------------------------------------------
    # deal with return
    return valid_drsfiles


def check_input_dprtypes(params: ParamDict, recipe: Any,
                         infiles: List[DrsFitsFile]) -> List[DrsFitsFile]:
    """
    Check that the input dprtypes conform to one of the models within the
    recipe

    This is done by checking the DPRTYPE header key
    if all files are in the file model group then we force the DPRTYPE to be
    the file model reference DPRTYPE, otherwise if all the files are in none
    of the file models we raise an error

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: Recipe, the recipe instance that called this function
    :param infiles: List of DrsFitsFile, the input files to check

    :raises: DrsException if not file model is valid for all files
    :return: List of DrsFitsFile, the input files (with updated DPRTYPEs)
    """
    # TODO: This still does not stop the user from using the wrong files
    #       for FLAT_FLAT as they could just use all DARK_FLAT or all FLAT_DARK
    #       for now required_ref is used but as long as we have FLAT in both
    #       channels it should work
    #       Also there is no reference to different exposure times / nd filters
    #       etc - so maybe we need to do something more advanced here
    # deal with no file model
    if len(recipe.file_model) == 0:
        return infiles
    # get the dprtype header key
    dprtype_hkey = params['KW_DPRTYPE'][0]
    dprtype_hcomment = params['KW_DPRTYPE'][2]
    # storage for an error message
    error_msgs = []
    # storage validity of all file models
    validity = []
    # -------------------------------------------------------------------------
    # if we have files loop around the dictionary.
    #    The dictionary key is the DPRTYPE we will force in the headers
    #    we expect all infiles to only be in one of these groups
    #    an error must be generated if this is not the case
    for ref_dprtype in recipe.file_model:
        # flag that all files are valid for one of the file models
        valid = True
        # store dprtypes
        dprtypes = []
        # get the names of the infiles
        ref_names = list(map(lambda x: x.name, recipe.file_model[ref_dprtype]))
        # loop around the infiles
        for infile in infiles:
            # if infile is not a class in ref_infiles we have a problem
            if infile.name not in ref_names:
                # this file is invalid
                valid &= False
                # TODO: Add to language database
                emsg = ('Input file {0} not in recipe file model'
                        '\n\tValid files are: {1}')
                eargs = [infile.name, ', '.join(ref_names)]
                # append to error messages
                error_msgs.append(emsg.format(*eargs))
            # only if valid do we try changing the dprtype
            if valid:
                # read the header
                infile.read_header()
                # append original dprtype to dprtypes
                dprtypes.append(str(infile.header[dprtype_hkey]))
                # force the dprtype to the reference dprtype
                #    (just for use in this recipe run not permanently)
                infile.header[dprtype_hkey] = (ref_dprtype, dprtype_hcomment)

        # append to validity
        validity.append(valid)
        # we have to raise exception if ref_dprtype is not in dprtypes but
        #   all files are valid individually
        if valid and ref_dprtype not in dprtypes:
            # TODO: Add to language database
            emsg = ('Reference DPRTYPE {0} not in input files '
                    '\n\tCurrent DPRTYPES are: {1}')
            eargs = [ref_dprtype, ', '.join(dprtypes)]
            raise drs_log.AperoCodedException(params, None,
                                              message=emsg.format(*eargs))

        elif valid:
            # storage of first (ref file type)
            file0 = None
            # store all other files
            others = []
            # loop around all files and find one example of a ref file
            for pos in range(len(dprtypes)):
                if dprtypes[pos] == ref_dprtype and file0 is None:
                    file0 = infiles[pos]
                else:
                    others.append(infiles[pos])
            # order files with the first file being a ref file type
            infiles = [file0] + others
    # -------------------------------------------------------------------------
    # deal with no valid models
    if np.sum(validity) == 0:
        # loop round and print errors
        emsgs = ''
        for emsg in error_msgs:
            emsg += emsg
        # raise the error
        # TODO: Add to language database
        raise drs_log.AperoCodedException(params, None, emsgs)
    # deal with multiple valid models
    elif np.sum(validity) > 1:
        # TODO: Add to language database
        emsg = 'Multiple valid file models. File DPRTYPEs need checking'
        raise drs_log.AperoCodedException(params, None, emsg)
    # -------------------------------------------------------------------------
    # return the infiles
    return infiles


def get_file_definition(params: ParamDict, name: str,
                        block_kind: str = 'raw',
                        instrument: Union[str, None] = None,
                        return_all: bool = False,
                        fiber: Union[str, None] = None, required: bool = True
                        ) -> Union[DrsFitsFile, List[DrsFitsFile], None]:
    """
    Finds a given recipe in the instruments definitions

    :param params: ParamDict, the parameter dictionary of constants
    :param name: string, the DrsInputFile name
    :param instrument: string, the instrument name
    :param block_kind: string, the type of file to look for ('raw',
                       'tmp', 'red')
    :param return_all: bool, whether to return all instances of this file or
                       just the last entry (if False)
    :param fiber: string, some files require a fiber to choose the correct file
                  (i.e. to add a suffix)
    :param required: bool, if False then does not throw error when no files
                     found (only use if checking for return = None)

    :param instrument: string, the instrument name
    :type instrument: str
    :param block_kind: string, the type of file to look for ('raw',
                       'tmp', 'red')
    :type return_all: bool
    :type fiber: str

    :exception SystemExit: on caught errors

    :returns: if found the DrsRecipe, else raises SystemExit if required = True
              else returns None
    :rtype: Union[DrsFitsFile, List[DrsFitsFile], None]
    """
    # set function name
    func_name = display_func('get_file_definition', __NAME__)
    # deal with instrument
    if instrument is None:
        if 'INSTRUMENT' in base.IPARAMS:
            instrument = base.IPARAMS['INSTRUMENT']
            ipath = INSTRUMENT_PATH
        else:
            ipath = CORE_PATH
            instrument = None
    elif instrument == 'None':
        ipath = CORE_PATH
        instrument = None
    else:
        ipath = INSTRUMENT_PATH
    # deal with no name or no instrument
    if name == 'None' or name is None:
        if required:
            eargs = [name, 'unknown', func_name]
            raise drs_log.AperoCodedException(params, '00-008-00011',
                                              targs=eargs)
        return None
    # deal with fiber (needs removing)
    if fiber is not None:
        suffix = '_{0}'.format(fiber)
        if name.endswith(suffix):
            name = name[:-(len(suffix))]
    # else we have a name and an instrument
    margs = [instrument, ['file_definitions.py'], ipath, CORE_PATH]
    modules = param_functions.get_module_names(*margs, return_paths=False)
    # load module
    mod = constant_functions.import_module(func_name, modules[0], full=True)
    # get a list of all recipes from modules
    block = DrsPath(params, block_kind=block_kind)
    # get the file set for this block kind
    all_files = getattr(mod.get(), block.block_fileset).fileset
    # try to locate this recipe
    found_files = []
    for filet in all_files:
        if name.upper() in filet.name and return_all:
            found_files.append(filet)
        elif name == filet.name:
            found_files.append(filet)
    # deal with no files found and no instrument
    if instrument is None and len(found_files) == 0:
        empty = DrsFitsFile('Empty')
        return empty
    # deal with no files found and not required
    if (len(found_files) == 0) and (not required):
        return None
    # deal with no files found and required - raise error
    elif len(found_files) == 0:
        eargs = [name, modules[0], func_name]
        raise drs_log.AperoCodedException(params, '00-008-00011',
                                          targs=eargs)
    # return the found files
    if return_all:
        return found_files
    else:
        return found_files[-1]


def get_another_fiber_file(params: ParamDict, outfile: DrsFitsFile,
                           fiber: str, in_block_kind: str = 'tmp',
                           out_block_kind: str = 'red',
                           getdata: bool = False,
                           gethdr: bool = False) -> DrsFitsFile:
    """
    Using an "outfile" with a specific fiber get another fibers DrsFitsFile
    instance, we need to set the "in_block_kind" to the input block kind of the
    "outfile" and need to set the "out_block_kind" to the block kind of the
    "outfile", we also need to set the fiber we need

    :param params: ParamDict, parameter dictionary of constants
    :param outfile: DrsFitsFile, the original fits file
    :param fiber: str, the fiber to find
    :param in_block_kind: str, the outfiles input file block kind
                          i.e. for _e2dsff its input is _pp  block kind='tmp'
    :param out_block_kind: str, the outfiles block kind
                          i.e. for _e2dsff its block kind='red'
    :param getdata: bool, if True loads the data
    :param gethdr: bool, if True loads the header

    :return: DrsFitsFile, like outfile but with the fiber "fiber"
    """
    # need a fresh copy of the outfile
    fresh_outfile = get_file_definition(params, outfile.name,
                                        block_kind=out_block_kind)
    # see whether we need fiber for intype
    if fresh_outfile.intype.fibers is not None:
        infiber = fiber
    else:
        infiber = None
    # get the infile for the input of outfile
    inbasename = fresh_outfile.get_infile_infilename(filename=outfile.filename,
                                                     fiber=infiber)
    # get block for outfile
    outblock = DrsPath(params, abspath=outfile.filename)
    # get in block
    inblock = DrsPath(params, block_kind=in_block_kind)
    # get full path (base on in_block_kind)
    infilename = os.path.join(inblock.block_path, outblock.obs_dir, inbasename)
    # get a new copy of the infile
    infile = fresh_outfile.intype.newcopy(params=params, fiber=infiber)
    infile.set_filename(infilename)
    # make a new copy of this instance
    outfile2 = fresh_outfile.newcopy(params=params, fiber=fiber)
    # construct filename
    outfile2.construct_filename(infile=infile)
    # load data if required
    if getdata:
        # log message: Reading data for file
        margs = [outfile2.filename]
        WLOG(params, '', textentry('40-004-00005', args=margs))
        outfile2.read_data()
    # load header if required
    if gethdr:
        # log message: Reading header for file: {0}'
        margs = [outfile2.filename]
        WLOG(params, '', textentry('40-004-00006', args=margs))
        outfile2.read_header()
    # return outfile
    return outfile2


def combine(params: ParamDict, recipe: Any,
            infiles: List[DrsFitsFile], math: str = 'average',
            same_type: bool = True, save: bool = True,
            test_similarity: bool = True
            ) -> Union[Tuple[DrsFitsFile, Table], Tuple[None, None]]:
    """
    Takes a list of infiles and combines them (infiles must be DrsFitsFiles)
    combines using the math given.

    Allowed math:
        'sum', 'add', '+'
        'average', 'mean'
        'subtract', '-'
        'divide', '/'
        'multiply', 'times', '*'

    Note 'infiles' must be all the same DrsFitsFile type to combine by default,
    use 'same_type=False' to override this option

    Note the header is copied from infiles[0]

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe associated with the call to this
                   function
    :param infiles: list of DrsFiles, list of DrsFitsFiles to combine
    :param math: str, the math allowed (see above)
    :param same_type: bool, if True all infiles must have the same DrsFitFile
                      dtype
    :param save: bool, if True saves to disk otherwise returns DrsFitsFile
    :param test_similarity: bool, if True tests the similarity of the files
                            before combining

    :type params: ParamDict
    :type infiles: list[DrsFitsFile]
    :type math: str
    :type same_type: bool

    :return: Returns the combined DrsFitFile (header same as infiles[0]) or
             if no infiles were given returns None
    :rtype: DrsFitsFile
    """
    # set function name
    func_name = display_func('combine', __NAME__)
    # if we have a string assume we have 1 file and skip combine
    if isinstance(infiles, DrsFitsFile):
        return infiles, Table()
    # make sure infiles is a list
    if not isinstance(infiles, list):
        raise drs_log.AperoCodedException(params, '00-001-00020',
                                          targs=[func_name])
    # if we have only one file (or none) skip combine
    if len(infiles) == 1:
        return infiles[0], Table()
    elif len(infiles) == 0:
        return None, None
    # check that all infiles are the same DrsFileType
    if same_type:
        for it, infile in enumerate(infiles):
            if infile.name != infiles[0].name:
                eargs = [infiles[0].name, it, infile.name, func_name]
                raise drs_log.AperoCodedException(params, '00-001-00021',
                                                  targs=eargs)
    # get output path from params
    outpath = str(params['OUTPATH'])
    # check if outpath is set
    if outpath is None:
        raise drs_log.AperoCodedException(params, '01-001-00023',
                                          targs=[func_name])
    # get the absolute path (for combined output)
    if params['OBS_DIR'] is None:
        obs_dir = ''
    else:
        obs_dir = params['OBS_DIR']
    # combine outpath and out directory
    abspath = os.path.join(outpath, obs_dir)
    # read all infiles (must be done before combine)
    basenames = []
    for infile in infiles:
        # read the infile
        infile.read_file(check=True)
        # get the base name for each infile
        basenames.append(infile.basename)
    # make new infile using math
    infile0 = infiles[0].newcopy(params=params)
    outfile, outtable = infile0.combine(infiles[1:], math, same_type,
                                        path=abspath,
                                        test_similarity=test_similarity)
    # update params in outfile
    outfile.params = params
    # update the number of files
    if math in ['sum', '+', 'add']:
        outfile.numfiles = len(infiles)
    else:
        outfile.numfiles = 1
    # define multi lists
    data_list = [outtable]
    datatype_list = ['table']
    name_list = ['COMBINE_TABLE']
    # add input files
    outfile.infiles = list(basenames)
    # add core values (that should be in all headers)
    outfile.add_core_hkeys(params)
    # deal with writing to disk (default)
    if save:
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=outfile)]
            name_list += ['PARAM_TABLE']
            datatype_list += ['table']
        # write to disk
        WLOG(params, '', textentry('40-001-00025', args=[outfile.filename]))
        outfile.write_multi(data_list=data_list, name_list=name_list,
                            datatype_list=datatype_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(outfile)

    # return combined infile
    return outfile, outtable


def combine_metric_1(params: ParamDict, row: int, image1: np.ndarray,
                     datacube0: np.ndarray) -> Tuple[float, float, bool]:
    """
    Simple pearson's R test on a row of the datacube (image) comparing it to
    image1 (the median of the whole datacube)

    For use with DARK_FLAT, FLAT_FLAT, FLAT_DARK, FP_FP only

    :param params: ParamDict, parameter dictionary of constants
    :param row: int, the row of the datacube to use
    :param image1: np.ndarray (2D), the median image of the data cube
    :param datacube0: np.ndarray (3D), the data cube of images

    :return: tuple, 1. The result of the Pearson R test (float),
             2. The metric criteria used for pass/fail (float),
             3. whether passed/failed (bool)
    """
    # normalize data by square
    image_row = np.array(datacube0[row])
    # calculate the metric by which to grade input files
    image2 = image_row.ravel()
    good = np.isfinite(image1) * np.isfinite(image2)
    metric, _ = pearsonr(image1[good], image2[good])
    # get metric threshold
    metric_threshold = params['COMBINE_METRIC_THRESHOLD1']
    # define whether metric passed
    passed = metric > metric_threshold
    # return metric, threshold and passed criteria
    return metric, metric_threshold, passed


def combine_headers(params: ParamDict, headers: List[Header],
                    names: List[str], math: str):
    """
    Takes a list of headers and combines them in the proper fashion (for the
    output combined file)

    Any keys that do not change are kept in main header
    Any keys that are flagged with combine_methods are combined

    All other keys (that change) are added to a combined_table

    :param params: ParamDict, the parameter dictionary of constants
    :param headers: list of headers - the headers to combine
    :param names: list of strings, the names of the header files
    :param math: str, the math mode to combine image (used for certain
                 combine_methods)
    :return:
    """
    # -------------------------------------------------------------------------
    # step 1. find header keys that need combining
    # -------------------------------------------------------------------------
    ckeys, cmethods = [], []
    # need to get keywords with combine methods
    for key in params:
        # get parameter
        param = params.instances[key]
        # test for Keyword instance
        if not isinstance(param, Keyword):
            continue
        # test for combine method
        if param.combine_method is not None:
            ckeys.append(params[key][0])
            cmethods.append(param.combine_method)

    # -------------------------------------------------------------------------
    # step 2. identify all header keys across all files
    # -------------------------------------------------------------------------
    # identify unique keys in all headers
    all_header_keys = []
    all_comments = []
    # loop around headers
    for header in headers:
        # loop around keys in this header
        for key in header:
            if key not in all_header_keys:
                all_header_keys.append(key)
                all_comments.append(header.comments[key])
    # -------------------------------------------------------------------------
    # step 3: get all header keys and see which are identical
    # -------------------------------------------------------------------------
    # storage of all keys
    all_dict = dict()
    type_dict = dict()
    # add full filename
    all_dict['INPUT_FILENAME'] = names
    table_keys = ['INPUT_FILENAME']
    table_comments = ['COMMENT']
    constant_keys = []
    # loop around unique header keys
    for k_it, key in enumerate(all_header_keys):
        # skip forbidden keys
        if key in params['FORBIDDEN_OUT_KEYS']:
            continue
        # storage of values
        values = []

        comment_card = False
        # loop around headers
        for h_it, header in enumerate(headers):
            if key in header:
                value = header[key]
                # deal with header comment cards
                if isinstance(value, drs_fits.HeaderCommentCards):
                    comment_card = True
                values.append(value)
            else:
                values.append(None)
        # if keys are identified as being combined add them to table_keys
        #  even if they are constant
        if key in ckeys:
            table_keys.append(key)
            table_comments.append(all_comments[k_it])
        # identify if values are all the same
        if comment_card:
            constant_keys.append(key)
        elif len(set(values)) == 1:
            constant_keys.append(key)
        else:
            table_keys.append(key)
            table_comments.append(all_comments[k_it])
        # add values to all_dict
        all_dict[key] = values
        type_dict[key] = comment_card
    # -------------------------------------------------------------------------
    # step 4: for those keys that have been flagged as needing combining
    #         combine them with the combine_method
    # -------------------------------------------------------------------------
    # storage of new header dictionary
    new_header_dict = dict()
    # loop around keys that need combining
    for c_it, ckey in enumerate(ckeys):
        # skip if not in header (for some reason)
        if ckey not in all_dict:
            continue
        # combine values
        new_header_dict[ckey] = combine_hkey(all_dict[ckey], cmethods[c_it],
                                             math)
    # -------------------------------------------------------------------------
    # step 5: add keys that are constant
    # -------------------------------------------------------------------------
    # add keys that don't change
    for ckey in constant_keys:
        # skip if already present (i.e. they have been combined)
        if ckey in new_header_dict:
            continue
        # add keys to new header dict
        new_header_dict[ckey] = all_dict[ckey][0]
    # -------------------------------------------------------------------------
    # step 6: make a table from header keys that change
    # -------------------------------------------------------------------------
    # filter out keys which are not in table_keys

    table_dict = dict()

    for cit, ckey in enumerate(list(table_keys)):
        table_dict[ckey] = list(all_dict[ckey]) + [table_comments[cit]]

    # table_dict = dict()
    # for row in range(len(headers)):
    #     table_dict[names[row]] = []
    #     for ckey in table_keys:
    #         table_dict[names[row]].append(all_dict[ckey][row])
    # convert to a table
    combine_table = Table()
    # add the keys as the first column
    # combine_table['KEYS'] = table_keys
    # add the columns
    for col in table_dict:
        combine_table[col] = np.array(table_dict[col]).astype(str)
    # add the comments
    # combine_table['COMMENTS'] = table_comments
    # -------------------------------------------------------------------------
    # step 7: make new hdict and header
    # -------------------------------------------------------------------------
    new_hdict = Header()
    # loop around all keys in the correct order
    for k_it, key in enumerate(all_header_keys):
        # only add keys that are in new_header_dict
        if key in new_header_dict and type_dict[key]:
            for value in str(new_header_dict[key]).split('\n'):
                new_hdict[key] = value
        elif key in new_header_dict:
            # add the value and the comment
            new_hdict[key] = (new_header_dict[key], all_comments[k_it])
    # copy into the new header
    new_header = new_hdict.copy()
    # -------------------------------------------------------------------------
    # step 8: return header/hdict/table
    # -------------------------------------------------------------------------
    return new_header, new_hdict, combine_table


def combine_hkey(values: List[Any], method: str, math: str) -> Any:
    """
    Combine header keys using method given in Keyword setup

    :param values: a list of values to combine with given method
    :param method: str, the method to combine
    :param math: str, if method = flux this is the math to use with it

    :return: Any, single value of the combined type or None if not combinable
    """
    # deal with method == math (set method == to the math directly)
    if method == 'math':
        method = str(math)
    # noinspection PyBroadException
    try:
        if method in ['mean', 'average']:
            return mp.nanmean(values)
        if method in ['median', 'med']:
            return mp.nanmedian(values)
        if method in ['sum', 'add']:
            return mp.nansum(values)
        if method in ['minimum', 'min']:
            return mp.nanmin(values)
        if method in ['maximum', 'max']:
            return mp.nanmax(values)
        # flux correction has to use the math from combining the image
        if method == 'flux':
            # if we want to sum the data
            if math in ['sum', 'add', '+']:
                return mp.nansum(values) * np.sqrt(len(values))
            elif math in ['average', 'mean']:
                return mp.nanmean(values) / np.sqrt(len(values))
            # elif if median
            elif math in ['median', 'med']:
                return mp.nanmedian(values) / np.sqrt(len(values))
            # deal with math == None
            elif math == 'None':
                return values[0]
            # else return an empty value
            else:
                return None
        # if header key is a noise
        if method == 'noise':
            # if we want to sum the data
            if math in ['sum', 'add', '+']:
                return np.sqrt(np.nansum(np.array(values) ** 2))
            elif math in ['average', 'mean']:
                return np.sqrt(np.nansum(np.array(values) ** 2)) / len(values)
            # elif if median
            elif math in ['median', 'med']:
                return np.sqrt(np.nansum(np.array(values) ** 2)) / len(values)
            # deal with math == None
            elif math == 'None':
                return values[0]
            # else return an empty value
            else:
                return None
        # if method is in None --> return None
        if method in [None, 'None', '']:
            return None
        # if we get to this point return the method as the value
        return method
    # if for any reason this fails return None
    except Exception as _:
        return None


def fix_header(params: ParamDict, recipe: Any,
               infile: Union[DrsFitsFile, None] = None,
               header: Union[Header, FitsHeader, None] = None,
               check_aliases: bool = False, objdbm: Any = None
               ) -> Union[DrsFitsFile, Tuple[FitsHeader, Header]]:
    """
    Instrument specific header fixes are define in pseudo_const.py for an
    instrument and called here (function in pseudo_const.py is HEADER_FIXES)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe instance associated with calling this function
    :param infile: DrsFitsFile or None, the Drs file instance containing the
                   header to fix - if not set must have header set
    :param header: Header - if set fixes this header (if not set uses infile)
                   if both set 'header' takes precedence over infile.header
    :param check_aliases: bool, if True checks objname for aliases (this should
                   only be used when aliases are not going to be checked or
                   have not been checked before) i.e. this should be set to
                   False in preprocessing but true for precheck/processing
                   where we deal with raw files
    :param objdbm: drs_database.ObjectDatabase - the object database class to
                   check aliases in (if check_aliases is True)

    :return: if infile is set return the infile with the updated infile.header,
             else return hdict and header (both fits.Header instances)
    """
    # set function name
    # _ = display_func('fix_header', __NAME__)
    # deal with no header
    if header is None:
        header = infile.get_header()
        hdict = infile.hdict
        filename = infile.filename
        has_infile = True
    else:
        has_infile = False
        hdict = Header()
        filename = None
    # load pseudo constants
    pconst = load_functions.load_pconfig()
    # use pseudo constant to apply any header fixes required (specific to
    #   a specific instrument) and update the header
    header, hdict = pconst.HEADER_FIXES(params=params, recipe=recipe,
                                        header=header, hdict=hdict,
                                        filename=filename,
                                        check_aliases=check_aliases,
                                        objdbm=objdbm)
    # if the input was an infile return the infile back
    if has_infile:
        # return the updated infile
        infile.header = header
        infile.hdict = hdict
        return infile
    # else return the header (assuming input was a header only)
    else:
        # else return the header
        return header, hdict


def id_drs_file(params: ParamDict,
                drs_file_sets: Union[List[DrsFitsFile], DrsFitsFile],
                filename: Union[List[str], str, None] = None,
                nentries: Union[int, None] = None,
                required: bool = True, use_input_file: bool = False
                ) -> Tuple[bool, Union[DrsFitsFile, List[DrsFitsFile]]]:
    """
    Identify the drs file (or set of drs files) each with DrsFitsFile.name
    and DrsFitsFile.filename (or 'filename') set (important must have filename
    to be able to read header) - uses the DrsFitsFile.fileset to search for a
    specific DrsFitsFile that this filename / header describes.
    If nentries = 1 returns the first DrsFitsFile that statisfies header,
    otherwise returns all DrsFitsFile(s) that statisfy the header.

    :param params: ParamDict, the parameter dictionary of constants
    :param drs_file_sets: List[DrsFitsFile] or DrsFitsFile - the file instance
                          containing the filename, fileset (set of DrsinputFiles
                          for this group i.e. raw files) etc
                          if DrsFitsFile.filename is not set then 'filename'
                          must be set (raises error elsewise)
    :param filename: str or None, if DrsFitsFile (or instance in
                     List[DrsFitsFile]) does not have filename set it from here
                     this filename is the file that the header is read from
    :param nentries: int or None, if equal to 1 returns just the first
                     DrsFitsFile.fileset entry which matches the header - else
                     returns all DrsFitsFile(s) that match header
    :param required: bool, if True raises an error when filename/header combo
                     does not match a DrsFitsFile in any of the fileset(s)
    :param use_input_file: bool, if True set the data and header from the
                           inpit file (i.e. the DrsFitsFile with the fileset)
    :return: tuple, 1. bool, whether file was found,
                    2. the DrsFitsFile matching (if entries=1) else all the
                       DrsFitsFile(s) matching i.e. List[DrsFitsFile]
    """
    # set function
    func_name = display_func('id_drs_file', __NAME__)
    # get pconst
    pconst = load_functions.load_pconfig()
    # ----------------------------------------------------------------------
    # deal with list vs no list for drs_file_sets
    if isinstance(drs_file_sets, list):
        pass
    else:
        drs_file_sets = [drs_file_sets]
    # ----------------------------------------------------------------------
    # storage
    found = False
    kinds = []
    names = []
    file_set = None
    # ----------------------------------------------------------------------
    # loop around file set
    for file_set in drs_file_sets:
        # get the names of the file_set
        names.append(file_set.name)
        # ------------------------------------------------------------------
        # check we have entries
        if len(file_set.fileset) == 0:
            continue
        # ------------------------------------------------------------------
        # check we have a params set for file_set
        file_set.params = params
        # ------------------------------------------------------------------
        # check we ahve a file set
        if file_set.filename is None:
            if filename is None:
                raise drs_log.AperoCodedException(params, '00-001-00057',
                                                  targs=[func_name])
            else:
                file_set.set_filename(filename)
        # ------------------------------------------------------------------
        # get the associated files with this generic drs file
        fileset = list(file_set.fileset)
        # ------------------------------------------------------------------
        # loop around files
        for drsfile in fileset:
            # set params
            drsfile.params = params
            # --------------------------------------------------------------
            # debug
            dargs = [str(drsfile)]
            WLOG(params, 'debug', textentry('90-010-00001', args=dargs))
            # --------------------------------------------------------------
            # copy info from given_drsfile into drsfile
            file_in = drsfile.copyother(file_set, params=params,
                                        header=file_set.header)
            # --------------------------------------------------------------
            # load the header for this kind
            if file_in.header is None:
                # noinspection PyBroadException
                try:
                    # need to read the file header for this specific drs file
                    file_in.read_header(log=False)
                    # copy in hdict from file_set
                    # - this is the only way to get keys added from file that is
                    #   read above
                    if file_set.hdict is not None:
                        for key in file_set.hdict:
                            # noinspection PyUnresolvedReferences
                            file_in.header[key] = file_set.hdict[key]

                # if exception occurs continue to next file
                #    (this is not the correct file)
                except Exception as _:
                    continue
                except SystemExit as _:
                    continue
            # --------------------------------------------------------------
            # check this file is valid
            cond, _ = file_in.check_file()
            # --------------------------------------------------------------
            # if True we have found our file
            if cond:
                # ----------------------------------------------------------
                found = True
                # ----------------------------------------------------------
                # load the data for this kind
                cond1 = file_set.data is not None
                cond2 = file_set.header is not None
                # use the data if flagged and if possible (cond1 & cond2)
                if use_input_file and cond1 and cond2:
                    # shallow copy data
                    file_in.data = file_set.data
                    # copy over header
                    file_in.header = file_set.header
                else:
                    file_in.read_data()
                # ----------------------------------------------------------
                # append to list
                kinds.append(file_in)
                # ----------------------------------------------------------
                # if we only want one entry break here
                if nentries == 1:
                    break
    # ----------------------------------------------------------------------
    # deal with no files found
    if len(kinds) == 0 and required:
        # get header keys for info purposes (file definition keys)
        keys = pconst.FILEDEF_HEADER_KEYS()
        argstr = ''
        # loop around keys and add to error (if they exist)
        #   if they don't the value will be set to None
        for key in keys:
            # set value to None
            value = None
            # if file set is not None and header is not None
            #   then we can try to get key from file_set
            if file_set is not None and file_set.header is not None:
                value = file_set.get_hkey(key, required=False)
            argstr += '\t{0}: {1}\n'.format(key, value)

        eargs = [' '.join(names), file_set.filename, argstr, func_name]
        raise drs_log.AperoCodedException(params, '00-010-00001', targs=eargs)
    # ----------------------------------------------------------------------
    # return found and the drsfile instance
    if len(kinds) == 0:
        return found, kinds
    elif nentries is None:
        return found, kinds
    elif nentries == 1:
        return found, kinds[0]
    else:
        return found, kinds[:nentries]


def get_mid_obs_time(params: ParamDict,
                     header: Union[Header, FitsHeader, None] = None,
                     infile: Union[DrsFitsFile, None] = None,
                     out_fmt: Union[str, None] = None
                     ) -> Tuple[Union[Time, str, float], str]:
    """
    Get the mid point observation time from header and push it into the
    required format

    :param params: Paramdict, parameter dictionary of constants
    :param header: Header or astropy.fits.Header - the header instance to
                   read the MIDMJD from
    :param infile: DrsFitsFile - if Header is not set get it from infile
    :param out_fmt: str, the output format of the data (mjd, jd, iso, human,
                    unix, decimal year) - if set to None returns a astropy.Time
                    instance of the time
    :return: depending on out_fmt - returns a tuple, 1. the mid point of an
             observation (Time, str, float), 2. the method used to get the time
             [now always 'header' - calculated in preprocessing fix_header]
    """
    # set function name
    func_name = display_func('get_mid_obs_time', __NAME__)
    # get obs_time
    outkey = params['KW_MID_OBS_TIME'][0]
    # get format from params
    timefmt = params.instances['KW_MID_OBS_TIME'].datatype
    # get data type from params
    timetype = params.instances['KW_MID_OBS_TIME'].dataformat
    # if infile is set get header from infile
    if infile is not None and header is None:
        header = infile.get_header()
    # deal with header still being None
    if header is None:
        eargs = [func_name]
        raise drs_log.AperoCodedException(params, '00-001-00051', targs=eargs)
    # get raw value from header
    rawtime = header[outkey]
    # get time object
    obstime = Time(timetype(rawtime), format=timefmt)
    # set the method for getting mid obs time
    method = 'header'
    dbname = 'header_time'
    # return time in requested format
    if out_fmt is None:
        return obstime, method
    elif out_fmt == 'mjd':
        return float(obstime.mjd), method
    elif out_fmt == 'jd':
        return float(obstime.jd), method
    elif out_fmt == 'iso' or out_fmt == 'human':
        return obstime.iso, method
    elif out_fmt == 'unix':
        return float(obstime.unix), method
    elif out_fmt == 'decimalyear':
        return float(obstime.decimalyear), method
    else:
        kinds = ['None', 'human', 'iso', 'unix', 'mjd', 'jd', 'decimalyear']
        eargs = [dbname, ' or '.join(kinds), out_fmt, func_name]
        raise drs_log.AperoCodedException(params, '00-001-00030', targs=eargs)


def locate_calibfiber_file(params: ParamDict, infile: DrsFitsFile):
    """
    Locate a reference fiber file for science fiber file

    :param params:
    :param infile:
    :return:
    """
    # deal with infile being telluric file (we do not have reference file
    #   for telluric files) --> must use the telluric files "intype file"
    if infile.name == 'TELLU_OBJ':
        instance = infile.intype
        # need to get filename of input file
        inbasename = infile.get_infile_infilename(filename=infile.filename,
                                                  fiber=infile.fiber)
        # get absolute path
        infilename = os.path.join(infile.path, inbasename)
        # set filename
        instance.set_filename(infilename)
    else:
        instance = infile

    pconst = load_functions.load_pconfig()

    sci_fibers, ref_fiber = pconst.FIBER_KINDS()

    # switch fiber and read file
    outfile = get_another_fiber_file(params, instance, fiber=ref_fiber,
                                     in_block_kind='tmp',
                                     out_block_kind='red',
                                     getdata=True, gethdr=True)
    # return outfile
    return outfile


# =============================================================================
# Worker functions
# =============================================================================
def index_hkey_condition(name: str, datatype: type,
                         hkey: Union[List[str], str]) -> str:
    """
    Deal with generating a condition from a hkey (list or str)
    
    :param name: str, the name of the header key (column name as in database)
    :param datatype: type, the data type to force data to
    :param hkey: list of str or str, the header key(s) as a column name to
                 add to condition 
                 
    :return: str, the updated WHERE condition (starts with an AND)
    """
    # must deal with hkeys as lists
    if isinstance(hkey, list):
        # store sub-conditions
        subconditions = []
        # loop around elements in hkey
        for sub_hkey in hkey:
            # cast value into data type
            value = datatype(sub_hkey)
            # add to sub condition
            subconditions.append('{0}="{1}"'.format(name, value))
        # make full condition based on sub conditions
        condition = ' AND ({0})'.format(' OR '.join(subconditions))
        # return condition
        return condition
    else:
        # cast value into data type
        value = datatype(hkey)
        # return condition
        return ' AND {0}="{1}"'.format(name, value)


def generate_arg_checksum(source: Union[List[str], str],
                          ndigits: int = 10) -> str:
    """
    Take a list of strings or a string and generate a unique hash from
    them

    :param source: list of strings or string - the string to generate the hash
                   from
    :param ndigits: int, the size of the hash (in characters) default is 10

    :return: str, the hash
    """
    # set function name
    # _ = display_func('generate_arg_checksum', __NAME__)
    # flatten list into string
    if isinstance(source, list):
        source = ' '.join(source)
    # need to encode string
    encoded = source.encode('utf')
    # we want a hash of 10 characters
    digest = blake2b(encoded, digest_size=ndigits)
    # create hash
    _hash = digest.hexdigest()
    # return hash
    return str(_hash)


def decide_on_table_row(table: Union[Table, pd.DataFrame]) -> int:
    """
    If we have multiple rows and need one this is how we decide which one
    currently we look for columns:
        "RUNSTRING" - row returned is the first with a valid value

    if none of the above columns are found we return 0

    :param table: astropy.table.Table or pandas.DataFrame - the table to choose
                  a row of

    :return: int, the row of the table to use
    """
    # get columns
    if isinstance(table, Table):
        columns = list(table.colnames)
    elif isinstance(table, pd.DataFrame):
        columns = list(table.columns)
    else:
        columns = []
    # base on runstring
    if 'RUNSTRING' in columns:
        for row in range(len(table)):
            if table['RUNSTRING'][row] is not None:
                return row
    # if we have got to here we use the first row
    return 0


def test_for_formatting(key: str, number: Union[int, float]) -> str:
    """
    Specific test of a string that may either be:

    key   or {key}{number}

    e.g. if key = XXX{0}  --> XXX{number}
    e.g. if key = XXX --> XXX

    Note if XXX{0:.3f} number must be a float

    :param key: str, the key to test (and return if no formatting present)
    :param number: int or float, depending on format of key (and key present)
    :return: str, the ouput either modified (if with formatting) or "key"
    """
    # set function name
    # _ = display_func('test_for_formatting', __NAME__)
    # test the formatting by entering a number as format
    test_str = key.format(number)
    # if they are the same after test return key with the key and number in
    if test_str == key:
        return '{0}{1}'.format(key, number)
    # else we just return the test string
    else:
        return test_str


def is_forbidden_prefix(params: ParamDict, key: str) -> bool:
    """
    Boolean check of the Pseudo Constants class for FORBIDDEN_HEADER_PREFIXES
    if key starts with forbidden header prefixes False is returned, otherwise
    True is return

    :param params: ParamDict, parameter dictionary of constants
    :param key: str, the key to check

    :return: bool, True if key does not start with any forbidden header prefix,
             False if it does
    """
    # set function name
    # _ = display_func('is_forbidden_prefix', __NAME__)
    # assume key is not forbidden
    cond = False
    # if prefix is forbidden and key starts with this prefix -->
    #   set cond to true (key is not forbidden)
    for prefix in params['FORBIDDEN_HEADER_PREFIXES']:
        if key.startswith(prefix):
            cond = True
    # return condition on whether key is forbidden
    return cond


def _check_keyworddict(key: str,
                       keyworddict: dict) -> Tuple[bool, Union[str, None]]:
    """
    Some keys have formatting i.e. LOCE{0:04d} and thus for these we need to
    check their prefix matches the key (else we just check whole key)

    This ONLY works under the assumption that all format keys look as following:

        AAAA{0:4d}

        BBB{0:2d}

    (i.e. a string followed by a single formatting)

    :param key: string, key in header to check
    :param keyworddict: dictionary, the keyword dictionary to check (from
                        keyword definitions)

    :type key: str
    :type keyworddict: dict

    :return:
    """
    # set function name
    # _ = display_func('_check_keyworddict', __NAME__)
    # loop around keys in keyword dict
    for mkey in keyworddict:
        # check if we have not formatting (assuming int/float)
        # noinspection PyBroadException
        try:
            if mkey.format(0) == mkey:
                # if key is found then we stop here
                if key == mkey:
                    return True, mkey
                # we can skip to next key
                else:
                    continue
        # if it breaks assume we have a none int/float format
        except Exception as _:
            pass
        # else remove the formatting (assume it start with a '{'
        prefix = mkey.split('{')[0]
        # if key is found we stop here
        if key.startswith(prefix):
            return True, mkey
        else:
            continue
    # if we have checked every key then key is not found
    return False, None


def _copydrsfile(drsfileclass,
                 instance1: DrsInputFile,
                 instance2: Union[DrsInputFile, None],
                 name: Union[str, None] = None,
                 filetype: Union[str, None] = None,
                 suffix: Union[str, None] = None,
                 remove_insuffix: Union[bool, None] = None,
                 prefix: Union[str, None] = None,
                 fibers: Union[List[str], None] = None,
                 fiber: Union[str, None] = None,
                 params: Union[ParamDict, None] = None,
                 filename: Union[str, None] = None,
                 intype: Any = None,
                 path: Union[str, None] = None,
                 basename: Union[str, None] = None,
                 inputdir: Union[str, None] = None,
                 obs_dir: Union[str, None] = None,
                 data: Union[np.ndarray, None] = None,
                 header: Union[drs_fits.Header, None] = None,
                 fileset: Union[list, None] = None,
                 filesetnames: Union[List[str], None] = None,
                 outclass: OutFileTypes = None,
                 inext: Union[str, None] = None,
                 dbname: Union[str, None] = None,
                 dbkey: Union[str, None] = None,
                 rkeys: Union[dict, None] = None,
                 numfiles: Union[int, None] = None,
                 shape: Union[int, None] = None,
                 hdict: Union[drs_fits.Header, None] = None,
                 output_dict: Union[OrderedDict, None] = None,
                 datatype: Union[str, None] = None,
                 dtype: Union[type, None] = None,
                 is_combined: Union[bool, None] = None,
                 combined_list: Union[list, None] = None,
                 infiles: Union[list, None] = None,
                 s1d: Union[list, None] = None,
                 hkeys: Union[Dict[str, str], None] = None,
                 instrument: Optional[str] = None,
                 nosave: Optional[bool] = None,
                 description: Union[str, None] = None,
                 inpath: Union[str, None] = None,
                 required: Union[bool, None] = None):
    """
    Global copier of file instance

    instance1 = self normally
    instance2 = another file instance (if required)

    :param drsfileclass: the class to use to create new instance
    :param instance1: the class we are copying basic details from
    :param instance2: None or the class we are copying fits file data from
                      (including filename etc)

    :param name: string, the name of the DRS input file
    :param filetype: string, the file type i.e. ".fits"
    :param suffix: string, the suffix to add when making an output filename
                   from an input filename
    :param remove_insuffix: bool, if True removes input file suffix before
                   adding output file suffix
    :param prefix: string, the prefix to add when maing an output fulename
                   from an input filename
    :param fibers: list of strings, the possible fibers this file can be
                   associated with, should be None if it is not associated
                   with a specific fiber
    :param fiber: string, the specific fiber that this file is associated
                  with
    :param params: ParamDict, the parameter dictionary of constants
    :param filename: string, the filename to give to this file (may override
                     other options)
    :param intype: DrsInputFile, an DrsFile instance associated with the
                   input file that generates this file (as an output)
                   i.e. if this is a pp file the intype would be a raw file
    :param path: string, the path to save the file to (when writing)
                 this may be left blank and defaults to the recipe default
                 (recommended in most cases) - ma be relative
    :param basename: string, the basename (i.e. filename without path) for
                     the file
    :param inputdir: string, the input directory (associated with an input
                     file, when this is an output file)
    :param obs_dir: string, the observation directory of the file without
                    the filename (based on the fully generated filename)
    :param data: np.array - when loaded the data is stored here
    :param header: drs_fits.Header - when loaded the header is stored here
    :param fileset: List of DrsFile instances - this file can be used as
                    a container for a set of DrsFiles
    :param filesetnames: List of strings, the names of each DrsFile same
                         as doing list(map(lambda x: x.name, fileset))
    :param outclass: OutClass, the associated outclass
    :param inext: str, the input file extension [not used in DrsInputFile]
    :param dbname: str, the database name this file can go in
                (i.e. cailbration or telluric) [not used in DrsInputFile]
    :param dbkey: str, the database key [not used in DrsInputFile]
    :param rkeys: dict, the required header keys [not used in DrsInputFile]
    :param numfiles: int, the number of files represented by this file
                     instance [not used in DrsInputFile]
    :param shape: tuple, the numpy array shape for data (if present)
    :param hdict: drs_fits.Header - the header dictionary - temporary
                  storage key value pairs to add to header on
                  writing [not used in DrsInputFile]
    :param output_dict: dict, storage for data going to index
                  database [not used in DrsInputFile]
    :param datatype: str, the fits image type 'image' or
                     'header'  [not used in DrsInputFile]
    :param dtype: type, float or int - the type of data in the fits file
                  (mostly required for fits
                  images) [not used in DrsInputFile]
    :param is_combined: bool, if True this file represents a combined set
                        of files [not used in DrsInputFile]
    :param combined_list: list, the list of combined files that make this
                          file instance [not used in DrsInputFile]
    :param infiles: list, the list of input files (if output file)
    :param s1d: list, a list of s1d images attached to this file instance
                      (for use with extraction file
                       instances) [not used in DrsInputFile]
    :param hkeys: passed to required header keys (i.e. must be a DRS
                   Header key reference -- "KW_HEADERKEY")
                   [not used in DrsInputFile]
    :param instrument: str, the instrument this file definition is associated
                       with
    :param description: str, the description of the file (for documentation)
    :param inpath: str or None, if set is a directory to look for the file
                   in - this is in exceptional cases and overrides normal
                   functionality
    :param required: bool, if True this file is always expectedt to exist
                     if recipe ran correctly

    - Parent class for Drs Fits File object (DrsFitsFile)
    """
    # deal with no instance2
    if instance2 is None:
        instance2 = instance1
    # set function name
    # _ = display_func('newcopy', __NAME__)
    # copy this instances values (if not overwritten)
    # set name if not set
    if name is None:
        name = deepcopy(instance1.name)
    # set filetype
    if filetype is None:
        filetype = deepcopy(instance1.filetype)
    # set suffix
    if suffix is None:
        suffix = deepcopy(instance1.suffix)
    # set remove insuffix
    if remove_insuffix is None:
        remove_insuffix = deepcopy(instance1.remove_insuffix)
    # set prefix
    if prefix is None:
        prefix = deepcopy(instance1.prefix)
    # set filename
    if filename is None:
        filename = deepcopy(instance2.filename)
    # set intype
    if intype is None:
        intype = instance2.intype
    # set fiber
    if fiber is None:
        fiber = deepcopy(instance1.fiber)
    # set fibers
    if fibers is None:
        fibers = deepcopy(instance1.fibers)
    # set params
    if params is None:
        params = instance1.params
    # set path
    if path is None:
        path = deepcopy(instance2.path)
    # set basename
    if basename is None:
        basename = deepcopy(instance2.basename)
    # set inputdir
    if inputdir is None:
        inputdir = deepcopy(instance2.basename)
    # set directory
    if obs_dir is None:
        obs_dir = deepcopy(instance2.obs_dir)
    # set data
    if data is None:
        data = deepcopy(instance2.data)
    # set header
    if header is None:
        # deep copy drs_fits.Header
        if isinstance(instance2.header, drs_fits.Header):
            header = instance2.header.copy()
            # deep copy astropy.io.fits.Header
        elif isinstance(instance2.header, drs_fits.fits.Header):
            header = instance2.header.copy()
        else:
            header = None
    # set fileset
    if fileset is None:
        if instance1.fileset is None:
            fileset = None
        elif isinstance(instance1.fileset, list):
            # set up new file set storage
            fileset = []
            # loop around file sets
            for fileseti in instance1.fileset:
                fileset.append(fileseti.completecopy(fileseti))
        else:
            fileset = instance1.fileset
    # set filesetnames
    if filesetnames is None:
        filesetnames = deepcopy(instance1.filesetnames)
    # set outclass
    if outclass is None:
        if instance1.outclass is not None:
            outclass = instance1.outclass.copy()
        else:
            outclass = None
    # set inext
    if inext is None:
        inext = deepcopy(instance2.inext)
    # set dbname
    if dbname is None:
        dbname = deepcopy(instance1.dbname)
    # set dbkey
    if dbkey is None:
        dbkey = deepcopy(instance1.dbkey)
    # set rkeys
    if rkeys is None:
        rkeys = deepcopy(instance1.required_header_keys)
    # set numfiles
    if numfiles is None:
        numfiles = deepcopy(instance2.numfiles)
    # set shape
    if shape is None:
        shape = deepcopy(instance2.shape)
    # set hdict
    if hdict is None:
        # deep copy drs_fits.Header
        if isinstance(instance2.hdict, drs_fits.Header):
            hdict = instance2.hdict.copy()
        # deep copy astropy.io.fits.Header
        elif isinstance(instance2.hdict, drs_fits.fits.Header):
            hdict = instance2.hdict.copy()
        else:
            hdict = None
    # set output dict
    if output_dict is None:
        output_dict = deepcopy(instance2.output_dict)
    # set data type
    if datatype is None:
        datatype = deepcopy(instance2.datatype)
    # set dtype
    if dtype is None:
        dtype = deepcopy(instance2.dtype)
    # set is_combined
    if is_combined is None:
        is_combined = deepcopy(instance2.is_combined)
    # set combined_list
    if combined_list is None:
        combined_list = deepcopy(instance2.combined_list)
    # set input files
    if infiles is None:
        infiles = deepcopy(instance2.infiles)
    # set s1d
    if s1d is None:
        s1d = instance2.s1d
    # copy file specific header keys (from required header keys)
    new_hkeys = dict()
    if hkeys is not None:
        for key in instance1.required_header_keys:
            if key not in hkeys:
                new_hkeys[key] = str(instance1.required_header_keys[key])
            else:
                new_hkeys[key] = str(hkeys[key])
    # set instrument
    if instrument is None:
        instrument = deepcopy(instance2.instrument)
    # set nosave
    if nosave is None:
        nosave = deepcopy(instance2.nosave)
    # set description
    if description is None:
        description = deepcopy(instance2.description)
    # set in path
    if inpath is None:
        inpath = deepcopy(instance2.inpath)
    # copy required
    if required is None:
        required = deepcopy(instance2.required)
    # return new instance
    return drsfileclass(name, filetype, suffix, remove_insuffix, prefix,
                        fibers, fiber, params, filename, intype, path,
                        basename, inputdir, obs_dir, data, header,
                        fileset, filesetnames, outclass, inext, dbname,
                        dbkey, rkeys, numfiles, shape, hdict,
                        output_dict, datatype, dtype, is_combined,
                        combined_list, infiles, s1d, new_hkeys, instrument,
                        nosave, description, inpath, required)

# =============================================================================
# End of code
# =============================================================================
