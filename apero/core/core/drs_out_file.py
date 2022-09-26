#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO Output file functionality

Created on 2019-03-21 at 18:35

@author: cook
"""
import os
from typing import Any, Tuple, Union

from apero.base import base
from apero.core.core import drs_exceptions
from apero.core.core import drs_misc
from apero.core.constants import param_functions

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'core.core.drs_out_file.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# get parameter dictionary
ParamDict = param_functions.ParamDict
# get display func
display_func = drs_misc.display_func


# =============================================================================
# Define file classes
# - Note should all have the same inputs and return
# =============================================================================
class OutFile:
    """
    Do not use OutFile directly - use one of the children classes
    """
    def __init__(self):
        """
        Construct the generic output file class
        """
        self.classname = 'OutFile'
        self.reference = False
        self.debug = False
        self.calib = False
        self.tellu = False

    def copy(self) -> 'OutFile':
        """
        Return a new instance (copy) of the OutFile class

        :return: OutFile, a new copy of the outfile
        """
        new = OutFile()
        return new

    def construct(self, params: ParamDict, infile: Any, outfile: Any,
                  fiber: Union[str, None] = None, path: Union[str, None] = None,
                  func: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  filename: Union[str, None] = None) -> str:
        """
        Construct a general absolute filename from infile/outfile

        :param params: ParamDict, parameter dictionary of constants
        :param infile: DrsFitsFile, input file - must be defined
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
        :param filename: not used for general file

        :return: the aboslute path to the file
        """
        # set function name
        func_name = display_func('general_file', __NAME__, self.classname)
        # not used
        _ = filename
        # set function name from args
        if func is not None:
            func_name = '{0} [{1}]'.format(func, func_name)
        # deal with kwargs that are required
        if infile is None:
            raise DrsCodedException('00-001-00017', level='error',
                                    targs=[func_name], func_name=func_name)
        if outfile is None:
            raise DrsCodedException('00-001-00018', level='error',
                                    targs=[func_name], func_name=func_name)
        # try to get fiber from outfile
        if fiber is None:
            fiber = outfile.fiber
        # deal with fiber being required but still unset
        if outfile.fibers is not None and fiber is None:
            eargs = [outfile, func_name]
            raise DrsCodedException('00-001-00032', level='error',
                                    targs=eargs, func_name=func_name)
        # set infile basename
        inbasename = infile.basename
        # infile basename should not be None
        if inbasename is None:
            # raise error: infile.basename must be set when defining infile
            eargs = [infile.name, func_name]
            raise DrsCodedException('00-004-00017', level='error', targs=eargs)
        # get condition to remove input file prefix
        if remove_insuffix is None:
            remove_insuffix = outfile.remove_insuffix
        # if remove in suffix is True then remove it from inbasename
        if remove_insuffix and (infile.suffix is not None):
            # get the infile suffix
            insuffix = str(infile.suffix)
            # check for fibers
            if infile.fibers is not None:
                for infiber in infile.fibers:
                    insuffix = str(infile.suffix)
                    insuffix = '{0}_{1}'.format(insuffix, infiber.upper())
                    # check that infile suffix is not None
                    if insuffix in inbasename:
                        inbasename = inbasename.replace(insuffix, '')
            elif insuffix in inbasename:
                inbasename = inbasename.replace(insuffix, '')

        # get kwargs where default dependent on required arguments
        if prefix is None:
            prefix = outfile.prefix
        if suffix is None:
            suffix = outfile.suffix
        # construct out filename
        inext = infile.filetype
        outext = outfile.filetype
        outfilename = get_outfilename(inbasename, prefix=prefix,
                                      suffix=suffix, inext=inext, outext=outext,
                                      fiber=fiber)
        # deal with no given path (default)
        if path is None:
            # get output path from params
            if 'OUTPATH' in params:
                outpath = params['OUTPATH']
            else:
                outpath = None
            # check if outpath is set
            if outpath is None:
                raise DrsCodedException('01-001-00023', level='error',
                                        targs=[func_name], func_name=func_name)
            # get output night name from params
            if params['OBS_DIR'] is None:
                obs_dir = ''
            else:
                obs_dir = params['OBS_DIR']
            # make sure night name folder exists (create it if not)
            make_obs_dir(obs_dir, outpath)
            # construct absolute path
            abspath = os.path.join(outpath, obs_dir, outfilename)
        else:
            abspath = os.path.join(path, outfilename)
        # return absolute path
        return abspath


class GeneralOutFile(OutFile):
    def __init__(self):
        """
        Construct the General output file class - this is used in most
        non-special cases
        """
        super().__init__()
        self.classname = 'GeneralOutFile'

    def copy(self) -> 'GeneralOutFile':
        """
        Copy the genera output file
        :return:
        """
        new = GeneralOutFile()
        return new

    def construct(self, params: ParamDict, infile: Any, outfile: Any,
                  fiber: Union[str, None] = None, path: Union[str, None] = None,
                  func: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  filename: Union[str, None] = None) -> str:
        """
        Construct a general absolute filename from infile/outfile

        :param params: ParamDict, paremeter dictionary of constants
        :param infile: DrsFitsFile, input file - must be defined
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
        :param filename: not used for general file

        :return: the aboslute path to the file
        """
        # set function name
        func_name = display_func('general_file', __NAME__, self.classname)
        # not used
        _ = filename
        # set function name from args
        if func is not None:
            func_name = '{0} [{1}]'.format(func, func_name)
        # deal with kwargs that are required
        if infile is None:
            raise DrsCodedException('00-001-00017', level='error',
                                    targs=[func_name], func_name=func_name)
        if outfile is None:
            raise DrsCodedException('00-001-00018', level='error',
                                    targs=[func_name], func_name=func_name)
        # try to get fiber from outfile
        if fiber is None:
            fiber = outfile.fiber
        # deal with fiber being required but still unset
        if outfile.fibers is not None and fiber is None:
            eargs = [outfile, func_name]
            raise DrsCodedException('00-001-00032', level='error',
                                    targs=eargs, func_name=func_name)
        # set infile basename
        inbasename = infile.basename
        # get condition to remove input file prefix
        if remove_insuffix is None:
            remove_insuffix = outfile.remove_insuffix
        # if remove in suffix is True then remove it from inbasename
        if remove_insuffix and (infile.suffix is not None):
            # get the infile suffix
            insuffix = str(infile.suffix)
            # check for fibers
            if infile.fibers is not None:
                for infiber in infile.fibers:
                    insuffix = str(infile.suffix)
                    insuffix = '{0}_{1}'.format(insuffix, infiber.upper())
                    # check that infile suffix is not None
                    if insuffix in inbasename:
                        inbasename = inbasename.replace(insuffix, '')
            elif insuffix in inbasename:
                inbasename = inbasename.replace(insuffix, '')

        # get kwargs where default dependent on required arguments
        if prefix is None:
            prefix = outfile.prefix
        if suffix is None:
            suffix = outfile.suffix
        # construct out filename
        inext = infile.filetype
        outext = outfile.filetype
        outfilename = get_outfilename(inbasename, prefix=prefix,
                                      suffix=suffix, inext=inext, outext=outext,
                                      fiber=fiber)
        # deal with no given path (default)
        if path is None:
            # get output path from params
            if 'OUTPATH' in params:
                outpath = params['OUTPATH']
            else:
                outpath = None
            # check if outpath is set
            if outpath is None:
                raise DrsCodedException('01-001-00023', level='error',
                                        targs=[func_name], func_name=func_name)
            # get output night name from params
            if params['OBS_DIR'] is None:
                obs_dir = ''
            else:
                obs_dir = params['OBS_DIR']
            # make sure night name folder exists (create it if not)
            make_obs_dir(obs_dir, outpath)
            # construct absolute path
            abspath = os.path.join(outpath, obs_dir, outfilename)
        else:
            abspath = os.path.join(path, outfilename)
        # return absolute path
        return abspath


class NpyOutFile(GeneralOutFile):
    """
    Output file for numpy save files (npy files)
    """
    def __init__(self):
        """
        Construct the numpy save file output class
        """
        super().__init__()
        self.classname = 'NpyOutFile'

    def copy(self) -> 'NpyOutFile':
        """
        Copy the numpy save file output class
        :return:
        """
        new = NpyOutFile()
        return new

    def construct(self, params: ParamDict, infile: Any, outfile: Any,
                  fiber: Union[str, None] = None, path: Union[str, None] = None,
                  func: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  filename: Union[str, None] = None) -> str:
        """
        Construct a NPY filename from infile/outfile

        :param params: ParamDict, paremeter dictionary of constants
        :param infile: DrsFitsFile, input file - must be defined
        :param outfile: DrsFitsFile, output file - must be defined
        :param func: str, the function name if set (for errors)
        :param fiber: not used for npy_file
        :param remove_insuffix: not used for npy_file
        :param path: not used for npy_file
        :param prefix: not used for npy_file
        :param suffix: not used for npy_file
        :param filename: not used for npy_file

        :return: the aboslute path to the file
        """
        # set function name
        func_name = display_func('npy_file', __NAME__)
        # deal with unused
        _ = fiber, path, remove_insuffix, prefix, suffix, filename
        # set function name from args
        if func is not None:
            func_name = '{0} [{1}]'.format(func, func_name)

        # get out file and report error if not set
        if outfile is None:
            raise DrsCodedException('00-001-00018', level='error',
                                    targs=[func_name], func_name=func_name)
        # make sure filetype is .npy
        filetype = outfile.filetype
        if '.npy' not in filetype:
            raise DrsCodedException('00-001-00033', level='error',
                                    targs=[filetype], func_name=func_name)
        # update keywords func name
        return super().construct(params, infile, outfile, func=func_name)


class DebugOutFile(GeneralOutFile):
    """
    Output file for debug files (fits files)
    """
    def __init__(self):
        """
        Construct the output file for debug files
        """
        super().__init__()
        self.debug = True
        self.classname = 'DebugOutFile'

    def copy(self) -> 'DebugOutFile':
        """
        Copy the output file for debug files
        :return:
        """
        new = DebugOutFile()
        return new

    def construct(self, params: ParamDict, infile: Any, outfile: Any,
                  fiber: Union[str, None] = None, path: Union[str, None] = None,
                  func: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  filename: Union[str, None] = None) -> str:
        """
        Construct a debug filename from infile/outfile

        :param params: ParamDict, paremeter dictionary of constants
        :param infile: DrsFitsFile, input file - must be defined
        :param outfile: DrsFitsFile, output file - must be defined
        :param func: str, the function name if set (for errors)
        :param prefix: str, if set the prefix of the file (defaults to
                       outfile.prefix)
        :param fiber: not used for debug_file
        :param path: not used for debug_file
        :param remove_insuffix: not used for debug_file
        :param suffix: not used for debug_file
        :param filename: not used for debug_file

        :return: the aboslute path to the file
        """
        # set function name
        func_name = display_func('npy_file', __NAME__, self.classname)
        # deal with not used
        _ = fiber, path, remove_insuffix, suffix, filename
        # set function name from args
        if func is not None:
            func_name = '{0} [{1}]'.format(func, func_name)
        # deal with no prefix
        if prefix is None:
            prefix = outfile.prefix
        # get out file and report error if not set
        if outfile is not None:
            prefix = 'DEBUG_' + prefix
        else:
            prefix = 'DEBUG_'
        # return absolute path
        return super().construct(params, infile, outfile, prefix=prefix,
                                 func=func_name)


class BlankOutFile(OutFile):
    """
    Blank output file - output file matches input file
    """
    def __init__(self):
        """
        Construct the blank output file
        """
        super().__init__()
        self.classname = 'BlankOutFile'

    def copy(self) -> 'BlankOutFile':
        """
        Make a copy of the output file
        :return:
        """
        new = BlankOutFile()
        return new

    def construct(self, params: ParamDict, infile: Any, outfile: Any,
                  fiber: Union[str, None] = None, path: Union[str, None] = None,
                  func: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  filename: Union[str, None] = None) -> str:
        """
        Construct an output file that matches the input file (blank output)

        :param params: ParamDict, paremeter dictionary of constants
        :param infile: DrsFitsFile, input file - must be defined
        :param outfile: DrsFitsFile, output file - must be defined
        :param func: str, the function name if set (for errors)
        :param prefix: str, if set the prefix of the file (defaults to
                       outfile.prefix)
        :param fiber: not used for debug_file
        :param path: not used for debug_file
        :param remove_insuffix: not used for debug_file
        :param suffix: not used for debug_file
        :param filename: not used for debug_file

        :return: the aboslute path to the file
        """
        # set function name
        func_name = display_func('blank', __NAME__)
        # deal with not used
        _ = fiber, path, remove_insuffix, prefix, suffix, filename
        # set function name from args
        if func is None:
            func_name = '{0} [{1}]'.format(func, func_name)
        # deal with kwargs that are required
        if infile is None:
            _ = outfile
            raise DrsCodedException('00-001-00017', level='error',
                                    targs=[func_name], func_name=func_name)
        # return absolute path
        return infile.filename


class SetOutFile(OutFile):
    """
    Output file where output filename is set manually
    """
    def __init__(self):
        """
        Construct the output file where output filename is set manually
        """
        super().__init__()
        self.classname = 'SetOutFile'

    def copy(self) -> 'SetOutFile':
        """
        Copy the output file where output filename is set manually
        :return:
        """
        new = SetOutFile()
        return new

    def construct(self, params: ParamDict, infile: Any, outfile: Any,
                  fiber: Union[str, None] = None, path: Union[str, None] = None,
                  func: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  filename: Union[str, None] = None) -> str:
        """
        Construct an absolute filename based on the filename, can replace
        suffix

        :param params: ParamDict, paremeter dictionary of constants
        :param infile: DrsFitsFile, input file - must be defined
        :param outfile: DrsFitsFile, output file - must be defined
        :param path: str, the path the file should have
        :param func: str, the function name if set (for errors)
        :param suffix: str, if set the suffix of the file (defaults to
                       outfile.suffix)
        :param filename: str, the filename to give the file
        :param fiber: not used for set_file
        :param remove_insuffix: not used for set_file
        :param prefix: not used for set file

        :return: the aboslute path to the file
        """
        # set function name
        func_name = display_func('set_file', __NAME__)
        # deal with not used
        _ = remove_insuffix, prefix
        # set function name from args
        if func is None:
            func_name = '{0} [{1}]'.format(func, func_name)
        # deal with no outfile set
        if outfile is None:
            _ = infile
            raise DrsCodedException('00-001-00018', level='error',
                                    targs=[func_name], func_name=func_name)
        # get filename from outfile if None
        if filename is None:
            filename = outfile.basename
        # deal with no file name set and filename must be a basename (no path)
        if filename is None:
            raise DrsCodedException('00-001-00041', level='error',
                                    targs=[func_name], func_name=func_name)
        else:
            filename = os.path.basename(filename)
        # get extension
        if suffix is None:
            outext = outfile.filetype
        else:
            outext = suffix + outfile.filetype
        # check for extension and set filename
        if filename.endswith(outext):
            outfilename = str(filename)
        else:
            outfilename = filename + outext
        # deal with no given path (default)
        if path is None:
            # get output path from params
            outpath = params['OUTPATH']
            # check if outpath is set
            if outpath is None:
                raise DrsCodedException('01-001-00023', level='error',
                                        targs=[func_name], func_name=func_name)
            # get output night name from params
            obs_dir = params['OBS_DIR']
            # make sure night name folder exists (create it if not)
            make_obs_dir(obs_dir, outpath)
            # construct absolute path
            abspath = os.path.join(outpath, obs_dir, outfilename)
        else:
            abspath = os.path.join(path, outfilename)
        # return absolute path
        return abspath


# noinspection PyMethodOverriding
class PostOutFile(OutFile):
    """
    Post process output file class
    """
    def __init__(self):
        """
        Construct the post process output file
        """
        super().__init__()
        self.classname = 'PostOutFile'

    def copy(self) -> 'PostOutFile':
        """
        Copy the post process output file
        :return:
        """
        new = PostOutFile()
        return new

    def construct(self, params: ParamDict, drsfile: Any, identifier: str,
                  obs_dir: Union[str, None] = None) -> Tuple[str, str]:
        """
        Generate a post processed filename

        :param params: ParamDict, the parameter dictionary of constants
        :param drsfile: DrsOutFile instance, the drs out file associated with this
                        post processed file
        :param identifier: str, an identifier to the required output filename
        :param obs_dir: str, the observation directory
        :return:
        """
        # set function name
        # _ = display_func('post_file', __NAME__)
        # ---------------------------------------------------------------------
        # set filename to identifer
        filename = str(identifier)
        # ---------------------------------------------------------------------
        # remove input suffix (extension) from identifier
        if drsfile.inext is not None:
            if filename.endswith(drsfile.inext):
                filename = filename[:-len(drsfile.inext)]
        # ---------------------------------------------------------------------
        # add output suffix
        filename = filename + drsfile.suffix
        # ---------------------------------------------------------------------
        if obs_dir is None:
            obs_dir = ''
        # construct path
        path = os.path.join(params['DRS_DATA_OUT'], obs_dir)
        # add path to filename
        filename = os.path.join(path, filename)
        # ---------------------------------------------------------------------
        # return filename
        return filename, path


# =============================================================================
# Specific type classes
# =============================================================================
class CalibOutFile(GeneralOutFile):
    """
    Calibration output file
    """
    def __init__(self):
        """
        Construct a calibration file output
        """
        super().__init__()
        self.classname = 'CalibOutFile'
        self.calib = True

    def copy(self) -> 'CalibOutFile':
        """
        Copy a calirbation file output
        :return:
        """
        new = CalibOutFile()
        return new

    def construct(self, params: ParamDict, infile: Any, outfile: Any,
                  fiber: Union[str, None] = None, path: Union[str, None] = None,
                  func: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  filename: Union[str, None] = None) -> str:
        """
        Construct a calibration absolute filename from infile/outfile

        :param params: ParamDict, paremeter dictionary of constants
        :param infile: DrsFitsFile, input file - must be defined
        :param outfile: DrsFitsFile, output file - must be defined
        :param fiber: str, the fiber - must be set if infile.fibers is populated
        :param path: str, the path the file should have (if not set, set to
                     params['OUTPATH']  with params['OBS_DIR'] if set)
        :param func: str, the function name if set (for errors)
        :param remove_insuffix: bool if set removes input suffix if not set
                                defaults to the outfile.remove_insuffix
        :param suffix: str, if set the suffix of the file (defaults to
                       outfile.suffix)
        :param prefix: not used for calib_file
        :param filename: not used for calib_File

        :return: the aboslute path to the file
        """
        # set function name
        func_name = display_func('general_file', __NAME__)
        # set function name from args
        if func is not None:
            func_name = '{0} [{1}]'.format(func, func_name)
        # get observation directory
        # obs_dir = kwargs.get('obs_dir', None)
        # get prefix
        if outfile is not None:
            # prefix = _calibration_prefix(params, obs_dir) + outfile.prefix
            prefix = outfile.prefix
        # return general file with prefix updated
        return super().construct(params, infile, outfile, fiber,
                                 path, func_name, remove_insuffix,
                                 prefix, suffix, filename)


class TelluOutFile(GeneralOutFile):
    """
    A telluric output file class
    """
    def __init__(self):
        """
        Construct a telluric output file
        """
        super().__init__()
        self.classname = 'TelluOutFile'
        self.tellu = True

    def copy(self) -> 'TelluOutFile':
        """
        Copy a telluric output file
        :return:
        """
        new = TelluOutFile()
        return new

    def construct(self, params: ParamDict, infile: Any, outfile: Any,
                  fiber: Union[str, None] = None, path: Union[str, None] = None,
                  func: Union[str, None] = None,
                  remove_insuffix: Union[bool, None] = None,
                  prefix: Union[str, None] = None,
                  suffix: Union[str, None] = None,
                  filename: Union[str, None] = None) -> str:
        """
        Construct a telluric absolute filename from infile/outfile

        :param params: ParamDict, paremeter dictionary of constants
        :param infile: DrsFitsFile, input file - must be defined
        :param outfile: DrsFitsFile, output file - must be defined
        :param fiber: str, the fiber - must be set if infile.fibers is populated
        :param path: str, the path the file should have (if not set, set to
                     params['OUTPATH']  with params['OBS_DIR'] if set)
        :param func: str, the function name if set (for errors)
        :param remove_insuffix: bool if set removes input suffix if not set
                                defaults to the outfile.remove_insuffix
        :param suffix: str, if set the suffix of the file (defaults to
                       outfile.suffix)
        :param prefix: not used for calib_file
        :param filename: not used for calib_File

        :return: the aboslute path to the file
        """
        # set function name
        func_name = display_func('general_file', __NAME__)
        # set function name from args
        if func is not None:
            func_name = '{0} [{1}]'.format(func, func_name)
        # get observation directory
        # obs_dir = kwargs.get('obs_dir', None)
        # get prefix
        if outfile is not None:
            # prefix = _calibration_prefix(params, obs_dir) + outfile.prefix
            prefix = outfile.prefix
        # return general file with prefix updated
        return super().construct(params, infile, outfile, fiber,
                                 path, func_name, remove_insuffix,
                                 prefix, suffix, filename)


class RefCalibOutFile(CalibOutFile):
    """
    A reference calibration output file
    """
    def __init__(self):
        """
        Construct a reference calibration output file
        """
        super().__init__()
        self.classname = 'RefCalibOutFile'
        self.calib = True
        self.reference = True

    def copy(self) -> 'RefCalibOutFile':
        """
        Copy a reference calibration output file
        :return:
        """
        new = RefCalibOutFile()
        return new


class RefTelluOutFile(CalibOutFile):
    """
    A reference telluric output file
    """
    def __init__(self):
        """
        Copy a reference telluric output file
        """
        super().__init__()
        self.classname = 'RefTelluOutFile'
        self.tellu = True
        self.reference = True

    def copy(self) -> 'RefTelluOutFile':
        """
        Copy a reference telluric output file
        :return:
        """
        new = RefTelluOutFile()
        return new


class TelluSetOutFile(SetOutFile):
    """
    Special telluric output file where filename is set manually
    """
    def __init__(self):
        """
        Construct the special set-filename telluric output file
        """
        super().__init__()
        self.classname = 'TelluSetOutFile'
        self.tellu = True

    def copy(self) -> 'TelluSetOutFile':
        """
        Copy the special set-filename telluric output file
        :return:
        """
        new = TelluSetOutFile()
        return new


# =============================================================================
# Define user functions
# =============================================================================
def get_outfilename(infilename: str, prefix: Union[str, None] = None,
                    suffix: Union[str, None] = None,
                    inext: Union[str, None] = None,
                    outext: Union[str, None] = None,
                    fiber: Union[str, None] = None) -> str:
    """
    Get the output filename from a input filename (with inext) and add a
    prefix/suffix fiber etc

    :param infilename: str, the infile name
    :param prefix: str, if set the prefix of the file
    :param suffix: str, if set the suffix of the file
    :param inext: str, the infile extension (to remove)
    :param outext: str, the outfile extension (to add)
    :param fiber: str, the fiber to add (if set)

    :return: str, the filename correct for prefix/suffix/fiber etc
    """
    # set function name
    func_name = display_func('get_outfilename', __NAME__)
    # make sure infilename is a basename not a path
    infilename = os.path.basename(infilename)
    # deal with fiber
    if fiber is not None:
        suffix = '{0}_{1}'.format(suffix, fiber.upper())
    # remove extension
    if inext is None:
        inext = infilename.split('.')[-1]
    # strip filename of extenstion
    if infilename.endswith(inext):
        outfilename = str(infilename[:-len(inext)])
    else:
        eargs = [infilename, inext, func_name]
        raise DrsCodedException('00-001-00031', level='error',
                                targs=eargs, func_name=func_name)
    # add prefix and suffix
    if prefix is not None:
        outfilename = '{0}{1}'.format(prefix, outfilename)
    if suffix is not None:
        outfilename = '{0}{1}'.format(outfilename, suffix)
    # add back extention or add new one
    if outext is None:
        if not suffix.endswith(inext):
            outfilename = '{0}{1}'.format(outfilename, inext)
    elif not suffix.endswith(outext):
        outfilename = '{0}{1}'.format(outfilename, outext)
    # return filename
    return outfilename


def make_obs_dir(obs_dir: Union[str, None], path: str) -> str:
    """
    Make a directory with a night directory given - and also add the directory
    if needed

    :param obs_dir: str or None, if set add this to the directory path
    :param path: str, the absolute path (above obs_dir level)

    :return: str, the path with the night name added (if set)
    """
    # set function name
    func_name = display_func('get_outfilename', __NAME__)
    # deal with no night name set
    if obs_dir is None:
        return path
    # make full path
    full_path = os.path.join(path, obs_dir)

    rel_path = os.path.join(os.path.curdir, obs_dir)

    # if full path exists then just return
    if os.path.exists(full_path):
        return full_path
    # else try to create it
    else:
        try:
            # save current path
            cwd = os.getcwd()
            # change to path
            os.chdir(path)
            # attempt to make folders
            os.makedirs(rel_path)
            # change back to current path
            os.chdir(cwd)
        except Exception as e:
            eargs = [rel_path, path, type(e), e, func_name]
            raise DrsCodedException('09-003-00002', level='error',
                                    targs=eargs, func_name=func_name)
    # try to see if path exists one last time
    if os.path.exists(full_path):
        return full_path
    else:
        eargs = [rel_path, path, func_name]
        raise DrsCodedException('09-003-00003', level='error',
                                targs=eargs, func_name=func_name)


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
