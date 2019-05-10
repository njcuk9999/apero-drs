#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2018-09-14 at 18:19

@author: cook
"""
import numpy as np
from astropy.table import Table
import importlib
import argparse
import sys
import os
import glob
from collections import OrderedDict

from SpirouDRS import spirouCore
from SpirouDRS import spirouConfig


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_recipe.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get constants
CONSTANTS = spirouConfig.Constants
# get print colours
COLOR = CONSTANTS.Colors()
# get param dict
ParamDict = spirouConfig.ParamDict
# get the config error
ConfigError = spirouConfig.ConfigError
# define hard display limit
HARD_DISPLAY_LIMIT = spirouConfig.Constants.MAX_DISPLAY_LIMIT()
# define the print/log header divider
HEADER = spirouConfig.Constants.HEADER()
# define display strings for types
STRTYPE = OrderedDict()
STRTYPE[int] = 'int'
STRTYPE[float] = 'float'
STRTYPE[str] = 'str'
STRTYPE[complex] = 'complex'
STRTYPE[list] = 'list'
STRTYPE[np.ndarray] = 'np.ndarray'

INDEX_FILE = 'index.fits'
INDEX_FILE_NAME_COL = 'FILENAME'

DEBUG = False
# -----------------------------------------------------------------------------


# =============================================================================
# Define ArgParse Parser and Action classes
# =============================================================================
# Adapted from: https://stackoverflow.com/a/16942165
class DRSArgumentParser(argparse.ArgumentParser):
    """
    Custom argument parser designed to deal with recipe arguments
    """
    def __init__(self, recipe, **kwargs):
        # set recipe
        self.recipe = recipe
        # set blank variables for now
        self.args = None
        self.argv = None
        self.namespace = None
        # construct argparse ArgumentParser class
        argparse.ArgumentParser.__init__(self, **kwargs)

    def parse_args(self, args=None, namespace=None):
        """

        :param args:
        :param namespace:
        :return:
        """
        if args is None:
            self.args = sys.argv[1:]
        else:
            self.args = args
        # overritten functionality
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg = 'unrecognized arguments: %s'
            self.error(msg % ' '.join(argv))
        return args

    def error(self, message):
        # self.print_help(sys.stderr)
        # self.exit(2, '%s: error: %s\n' % (self.prog, message))
        # get parameterse from drs_params
        program = self.recipe.drs_params['RECIPE']
        # get parameters from drs_params
        params = self.recipe.drs_params
        # log message
        emsg1 = 'Argument Error:'
        emsg2 = '\t {0}'.format(message)
        emsg3 = '\t Use: "{0}.py --help" for help'.format(program)
        WLOG(params, 'error', [emsg1, emsg2, emsg3])

    def _print_message(self, message, file=None):
        # get parameters from drs_params
        program = self.recipe.drs_params['RECIPE']
        # construct error message
        if self.recipe.drs_params['COLOURED_LOG']:
            green, end = COLOR.GREEN1, COLOR.ENDC
            yellow, blue = COLOR.YELLOW1, COLOR.BLUE1
        else:
            green, end = COLOR.ENDC, COLOR.ENDC
            yellow, blue = COLOR.ENDC, COLOR.ENDC
        # Manually print error message (with help)
        print()
        print(green + HEADER + end)
        print(green + ' Help for: {0}.py'.format(program) + end)
        print(green + HEADER + end)
        imsgs = _get_version_info(self.recipe.drs_params, green, end)
        for imsg in imsgs:
            print(imsg)
        print()
        print(blue + self.format_help() + end)

    def format_help(self):

        hmsgs = []

        hmsgs += ['usage: ' + self.recipe._drs_usage()]

        # add description
        if self.recipe.description is not None:
            hmsgs += [self.recipe.description]

        # deal with required arguments
        hmsgs += ['', 'Required Arguments:', '']
        for arg in self.recipe.required_args:
            hmsgs.append(_help_format(arg.names, arg.helpstr, arg.options))
        # deal with optional arguments
        hmsgs += ['', '', 'Optional Arguments:', '']
        for arg in self.recipe.optional_args:
            hmsgs.append(_help_format(arg.names, arg.helpstr, arg.options))
        # deal with special arguments
        hmsgs += ['', '', 'Special Arguments:', '']
        for arg in self.recipe.special_args:
            hmsgs.append(_help_format(arg.names, arg.helpstr, arg.options))

        # add help
        helpstr = 'show this help message and exit'
        hmsgs.append(_help_format(['--help', '-h'], helpstr))

        # add epilog
        if self.recipe.epilog is not None:
            hmsgs += [self.recipe.epilog]

        # return string
        return_string = ''
        for hmsg in hmsgs:
            return_string += hmsg + '\n'

        # return messages
        return return_string

    def _has_special(self):

        # deal with help
        if '-h' in sys.argv:
            self.print_help()
            # quit after call
            self.exit()
        if '--help' in sys.argv:
            self.print_help()
            # quit after call
            self.exit()

        # Generate list of special arguments that require us to skip other
        #   arguments
        skippable = []
        for skey in self.recipe.specialargs:
            # get the DrsArgument instance
            sarg = self.recipe.specialargs[skey]
            # append to skippable if attribute "skip" is true
            if sarg.skip:
                skippable += sarg.names

        # deal with skippables
        for skip in skippable:
            if self.args is not None:
                for parg in self.args:
                    if skip in parg:
                        return True
        else:
            return False


class _CheckDirectory(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        self.parser = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _check_directory(self, value):
        out = self.recipe._valid_directory(value, return_error=True)
        cond, directory, emsgs = out
        if cond:
            return directory
        else:
            # get input dir
            input_dir = self.recipe._get_input_dir()
            # get listing message
            lmsgs = _print_list_msg(self.parser, self.recipe, input_dir,
                                    dircond=True, return_string=True)
            # log messages
            WLOG(self.recipe.drs_params, 'error', emsgs + lmsgs)

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        self.parser = parser
        # check for help
        parser._has_special()
        if type(values) == list:
            value = list(map(self._check_directory, values))[0]
        else:
            value = self._check_directory(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _CheckFiles(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        self.namespace = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _check_files(self, value, current_typelist=None, current_filelist=None):
        # check if "directory" is in namespace
        directory = getattr(self.namespace, 'directory', '')
        # get the argument name
        argname = self.dest
        # check if files are valid
        out = self.recipe._valid_files(argname, value, directory,
                                       return_error=True,
                                       alltypelist=current_typelist,
                                       allfilelist=current_filelist)
        cond, files, types, emsgs = out
        # if they are return files
        if cond:
            return files, types
        # else deal with errors
        else:
            # log messages
            WLOG(self.recipe.drs_params, 'error', emsgs, wrap=False)

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        self.parser = parser
        # store the namespace
        self.namespace = namespace
        # check for help
        skip = parser._has_special()
        if skip:
            return 0
        if type(values) in [list, np.ndarray]:
            files, types = [], []
            for value in values:
                filelist, typelist = self._check_files(value, types, files)
                files += filelist
                types += typelist
        else:
            filelist, typelist = self._check_files(values, [], [])
            files, types = filelist, typelist
        # Add the attribute
        setattr(namespace, self.dest, [files, types])


class _CheckBool(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _check_bool(self, value):
        # get parameters
        params = self.recipe.drs_params
        # conditions
        if str(value).lower() in ['yes', 'true', 't', 'y', '1']:
            return True
        elif str(value).lower() in ['no', 'false', 'f', 'n', '0']:
            return False
        else:
            emsg1 = 'Argument "{0}" must be a Boolean value (True/False)'
            WLOG(params, 'error', emsg1.format(self.dest))

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # check for help
        skip = parser._has_special()
        if skip:
            return 0
        if type(values) == list:
            value = list(map(self._check_bool, values))
        else:
            value = self._check_bool(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _CheckType(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _eval_type(self, value):
        # get parameters
        params = self.recipe.drs_params
        # get type error
        emsg = 'Argument "{0}"="{1}" should be type "{2}"'
        eargs = [self.dest, value, self.type]
        try:
            return self.type(value)
        except ValueError as _:
            WLOG(params, 'error', emsg.format(*eargs))
        except TypeError as _:
            WLOG(params, 'error', emsg.format(*eargs))

    def _check_type(self, value):
        # get parameters
        params = self.recipe.drs_params
        # check that type matches
        if type(value) is self.type:
            return value
        # check if passed as a list
        if (self.nargs == 1) and (type(value) is list):
            if len(value) == 0:
                emsg = 'Argument "{0}" should not be an empty list.'
                WLOG(params, 'error', emsg.format(self.dest))
            else:
                return self._eval_type(value[0])
        # else if we have a list we should iterate
        elif type(value) is list:
            values = []
            for it in self.nargs:
                values.append(self._eval_type(values[it]))
            if len(values) < len(value):
                wmsg = 'Argument too long (expected {0} got {1})'
                wargs = [self.nargs, len(value)]
                WLOG(params, 'warning', wmsg.format(*wargs))
            return values
        # else
        else:
            emsg = ('Argument "{0}"="{1}" list expected with {2} arguments '
                    'got type {3}')
            eargs = [self.dest, value, self.nargs, type(value)]
            WLOG(params, 'error', emsg.format(eargs))

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # check for help
        skip = parser._has_special()
        if skip:
            return 0
        if self.nargs == 1:
            value = self._check_type(values)
        elif type(values) == list:
            value = list(map(self._check_type, values))
        else:
            value = self._check_type(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _CheckOptions(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _check_options(self, value):
        # get parameters
        params = self.recipe.drs_params
        # check options
        if value in self.choices:
            return value
        else:
            emsg1 = 'Argument "{0}" must be {1}'
            eargs1 = [self.dest, ' or '.join(self.choices)]
            emsg2 = '\tCurrent value = {0}'.format(value)
            WLOG(params, 'error', [emsg1.format(*eargs1), emsg2])

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # check for help
        skip = parser._has_special()
        if skip:
            return 0
        if type(values) == list:
            value = list(map(self._check_options, values))
        else:
            value = self._check_options(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


# =============================================================================
# Define Special Actions
# =============================================================================
class _MakeListing(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        self.namespace = None
        self.parser = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _display_listing(self, namespace):
        # get input dir
        input_dir = self.recipe._get_input_dir()
        # check if "directory" is in namespace
        directory = getattr(namespace, 'directory', None)
        # deal with non set directory
        if directory is None:
            # path is just the input directory
            fulldir = input_dir
            # whether to list only directories
            dircond = True
        else:
            # create full dir path
            fulldir = os.path.join(input_dir, directory)
            # whether to list only directories
            dircond = False
        # ---------------------------------------------------------------------
        # construct listing message
        # ---------------------------------------------------------------------
        _print_list_msg(self.parser, self.recipe, fulldir, dircond,
                        list_all=False)

    def __call__(self, parser, namespace, values, option_string=None):
        # check for help
        parser._has_special()
        # store parser
        self.parser = parser
        # get drs parameters
        self.recipe = parser.recipe
        # display listing
        self._display_listing(namespace)
        # quit after call
        parser.exit()


class _MakeAllListing(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        self.namespace = None
        self.parser = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _display_listing(self, namespace):
        # get input dir
        input_dir = self.recipe._get_input_dir()
        # check if "directory" is in namespace
        directory = getattr(namespace, 'directory', None)
        # deal with non set directory
        if directory is None:
            # path is just the input directory
            fulldir = input_dir
            # whether to list only directories
            dircond = True
        else:
            # create full dir path
            fulldir = os.path.join(input_dir, directory)
            # whether to list only directories
            dircond = False
        # ---------------------------------------------------------------------
        # construct listing message
        # ---------------------------------------------------------------------
        _print_list_msg(self.parser, self.recipe, fulldir, dircond,
                        list_all=True)

    def __call__(self, parser, namespace, values, option_string=None):
        # check for help
        parser._has_special()
        # store parser
        self.parser = parser
        # get drs parameters
        self.recipe = parser.recipe
        # display listing
        self._display_listing(namespace)
        # quit after call
        parser.exit()


class _ActivateDebug(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _set_debug(self, values, recipe=None):
        # deal with using without call
        if self.recipe is None:
            self.recipe = recipe
        if values is None:
            return 1
        # test value
        try:
            # only take first value (if a list)
            if type(values) != str and hasattr(values, '__len__'):
                values = values[0]
            # try to make an integer
            value = int(values)
            # set DRS_DEBUG
            self.recipe.drs_params['DRS_DEBUG'] = value
            # now update constants file
            spirouConfig.Constants.UPDATE_PP(self.recipe.drs_params)
            # return value
            return value
        except:
            emsg = 'Argument "{0}": Debug mode = "{1}" not understood.'
            eargs = [self.dest, values]
            WLOG(self.recipe.drs_params, 'error', emsg.format(*eargs))

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # display listing
        if type(values) == list:
            value = list(map(self._set_debug, values))
        else:
            value = self._set_debug(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _DisplayVersion(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _display_version(self):
        # get params
        params = self.recipe.drs_params
        # get colours
        if params['COLOURED_LOG']:
            green, end = COLOR.GREEN1, COLOR.ENDC
        else:
            green, end = COLOR.ENDC, COLOR.ENDC
        # print start header
        print(green + HEADER + end)
        # print version info message
        imsgs = _get_version_info(params, green, end)
        for imsg in imsgs:
            print(imsg)
        # end header
        print(green + HEADER + end)

    def __call__(self, parser, namespace, values, option_string=None):
        # check for help
        parser._has_special()
        self.recipe = parser.recipe
        # display version
        self._display_version()
        # quit after call
        parser.exit()


class _DisplayInfo(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def _display_info(self):
        # get params
        params = self.recipe.drs_params
        program = params['RECIPE']
        # get colours
        if self.recipe.drs_params['COLOURED_LOG']:
            green, end = COLOR.GREEN1, COLOR.ENDC
            yellow, blue = COLOR.YELLOW1, COLOR.BLUE1
        else:
            green, end = COLOR.ENDC, COLOR.ENDC
            yellow, blue = COLOR.ENDC, COLOR.ENDC
        # print usage
        print(green + HEADER + end)
        print(green + ' Info for: {0}.py'.format(program) + end)
        print(green + HEADER + end)
        # print version info message
        imsgs = _get_version_info(params, green, end)
        for imsg in imsgs:
            print(imsg)
        print()
        print(blue + 'usage: ' + self.recipe._drs_usage() + end)
        print(blue + self.recipe.description + end)
        # print examples
        print(blue + self.recipe.epilog + end)
        # print see help
        print(green + 'use --help for more detailed help' + end)
        print()
        # end header
        print(green + HEADER + end)

    def __call__(self, parser, namespace, values, option_string=None):
        # check for help
        parser._has_special()
        self.recipe = parser.recipe
        # display version
        self._display_info()
        # quit after call
        parser.exit()


# =============================================================================
# Define Object Classes
# =============================================================================
class DrsArgument(object):
    def __init__(self, name, kind, **kwargs):
        """
        Create a DRS Argument object

        :param name: string, the name of the argument and call, for optional
                     arguments should include the "-" and "--" in front
                     ("arg.name" will not include these but "arg.argname"
                     and "arg.names" will)

        :param kwargs: currently allowed kwargs are:

            - pos: int or None, the position of a position argument, if None
                   not a positional argument (i.e. optional argument)

            - altnames: list of strings or None, the alternative calls to
                        the argument in argparse (as well as "name"), if None
                        only call to argument is "name"

            - dtype: string or type or None, the data type currently must
                     be one of the following:
                        ['files', 'file', 'directory', 'bool',
                         'options', 'switch', int, float, str, list]
                     if None set to string.
                     these control the checking of the argument in most cases.
                     int/flat/str/list are not checked

            - options: list of strings or None, sets the allowed string values
                       of the argument, if None no options are required (other
                       than those set by dtype)

            - helpstr: string or None, if not None sets the text to add to the
                       help string

            - files: list of DrsInput objects or None, if not None and dtype
                     is "files" or "file" sets the type of file to expect
                     the way the list is understood is based on "filelogic"

            - filelogic: string, either "inclusive" or "exclusive", if
                         inclusive and combination of DrsInput objects are
                         valid, if exclusive only one DrsInput in the list is
                         valid for all files i.e.
                         - if files = [A, B] and filelogic = 'inclusive'
                           the input files may all be A or all be B
                         - if files = [A, B] and filelogic = 'exclusive'
                           the input files may be either A or B
        """

        # ----------------------------------------------
        # define class constants
        # ----------------------------------------------
        # define allowed properties
        self.propkeys = ['action', 'nargs', 'type', 'choices', 'default',
                         'help']
        # define allowed dtypes
        self.allowed_dtypes = ['files', 'file', 'directory', 'bool',
                               'options', 'switch', int, float, str, list]
        # ----------------------------------------------
        # assign values from construction
        # ----------------------------------------------
        # deal with name
        # get argument name
        self.argname = str(name)
        # get full name
        self.name = name
        while self.name.startswith('-'):
            self.name = self.name[1:]
        # get kind
        if kind in ['arg', 'kwarg', 'special']:
            self.kind = kind
        else:
            emsg = '"kind" must be "arg" or "kwarg" or "special"'
            self.exception(emsg)
        # special parameter (whether to skip other arguments)
        self.skip = False
        # get position
        self.pos = kwargs.get('pos', None)
        # add names from altnames
        self.names = [self.argname] + kwargs.get('altnames', [])
        # get dtype
        self.dtype = kwargs.get('dtype', None)
        # get options
        self.options = kwargs.get('options', None)
        # get help str
        self.helpstr = kwargs.get('helpstr', '')
        # get files
        self.files = kwargs.get('files', [])
        # get limit
        self.limit = kwargs.get('limit', None)
        # get file logic
        self.filelogic = kwargs.get('filelogic', 'inclusive')
        if self.filelogic not in ['inclusive', 'exclusive']:
            emsg = ('"filelogic" must equal "inclusive" '
                    'or "exclusive" only. '
                    'Current value is "{0}"'.format(self.filelogic))
            self.exception(emsg)
        # deal with no default/default_ref for kwarg
        if kind == 'kwarg':
            if ('default' not in kwargs) and ('default_ref' not in kwargs):
                emsg = ('**kwargs must contain either "default"'
                        ' or "default_ref" for full definition of argument.')
                self.exception(emsg)
        # get default
        self.default = kwargs.get('default', None)
        # get default_ref
        self.default_ref = kwargs.get('default_ref', None)

        # get required
        self.required = kwargs.get('required', False)

        # set empty
        self.props = OrderedDict()
        self.value = None

    def make_properties(self):
        """
        Make the properties dictionary for argparser based on the
        "arg.dtype" assigned during construction.
        i.e. one of the following provides the information to fill arg.props
            ['files', 'file', 'directory', 'bool', 'options',
             'switch', int, float, str, list]

        This must be run manually once an instance of DrsArgument is
        constructed.

        :return None:
        """
        # deal with no dtype
        if self.dtype is None:
            self.dtype = str
        # make sure dtype is valid
        if self.dtype not in self.allowed_dtypes:
            a_dtypes_str = ['"{0}"'.format(i) for i in self.allowed_dtypes]
            eargs = [' or '.join(a_dtypes_str), self.dtype]
            emsg = ('DrsArgument Error: "dtype" is not valid. Must be equal'
                    ' to {0}. Current value is "{1}"'.format(*eargs))
            raise ValueError(emsg)
        # deal with dtype
        if self.dtype == 'files':
            self.props['action'] = _CheckFiles
            self.props['nargs'] = '+'
            self.props['type'] = str
            self.options = ['FILENAME1', 'FILENAME2', '...']
        elif self.dtype == 'file':
            self.props['action'] = _CheckFiles
            self.props['nargs'] = 1
            self.props['type'] = str
            self.options = ['FILENAME']
        elif self.dtype == 'directory':
            self.props['action'] = _CheckDirectory
            self.props['nargs'] = 1
            self.props['type'] = str
            self.options = ['DIRECTORY']
        elif self.dtype == 'bool':
            self.props['action'] = _CheckBool
            self.props['type'] = str
            self.props['choices'] = ['True', 'False', '1', '0']
            self.options = ['True', 'False', '1', '0']
        elif self.dtype == 'options':
            self.props['action'] = _CheckOptions
            self.props['type'] = str
            self.props['choices'] = self.options
        elif self.dtype == 'switch':
            self.props['action'] = 'store_true'
        elif type(self.dtype) is type:
            self.props['action'] = _CheckType
            self.props['type'] = self.dtype
            self.props['nargs'] = 1
            self.options = [self.name.upper()]
        else:
            self.props['type'] = str
            self.props['nargs'] = 1
            self.options = [self.name.upper()]
        # deal with default argument
        if self.default is not None:
            self.props['default'] = self.default
        # deal with required (for optional arguments)
        if self.kind != 'arg':
            self.props['required'] = self.required
        # add help string
        self.props['help'] = self.helpstr

    def assign_properties(self, props):
        """
        Assigns argparse properties from "props"

        Instead of creating properties based on dtype one can assign
        properties based on a input dictionary "props". This is useful
        when one has a defined static set or properties to pass to
        argparse. Only keys in the following list will be allowed to be passed
        to arg.props:
            ['action', 'nargs', 'type', 'choices', 'default', 'help']

        :param props: dictionary, contains pre-defined key value pairs to
                      parse to argparser keys must be in the following list:
                      ['action', 'nargs', 'type', 'choices', 'default', 'help']
        :return None:
        """
        # loop around properties
        for prop in self.propkeys:
            if prop in props:
                self.props[prop] = props[prop]

    def exception(self, message):
        log_opt = 'DrsArgument[{0}] Error'.format(self.name)
        raise Exception(log_opt + message)

    def __str__(self):
        """
        Defines the str(DrsArgument) return for DrsArgument
        :return str: the string representation of DrSArgument
                     i.e. DrsArgument[name]
        """
        return 'DrsArgument[{0}]'.format(self.name)

    def __repr__(self):
        """
        Defines the print(DrsArgument) return for DrsArgument
        :return str: the string representation of DrSArgument
                     i.e. DrsArgument[name]
        """
        return 'DrsArgument[{0}]'.format(self.name)


class DrsRecipe(object):
    def __init__(self, name=None):
        """
        Create a DRS Recipe object

        :param name: string, name of the recipe (the .py file) relating to
                     this recipe object
        """
        # name
        if name is None:
            self.name = 'Unknown'
        elif name.strip().endswith('.py'):
            self.name = name.split('.py')[0]
            while self.name.endswith('.py'):
                self.name = self.name.split('.py')[0]
        else:
            self.name = name
        # get instrument
        self.instrument = None
        # import module
        self.module = self._import_module()
        # output directory
        self.outputdir = 'reduced'
        # input directory
        self.inputdir = 'tmp'
        # input type (RAW/REDUCED)
        self.inputtype = 'raw'
        # recipe description/epilog
        self.description = 'No description defined'
        self.epilog = ''
        # run order
        self.run_order = None
        # define sets of arguments
        self.args = OrderedDict()
        self.kwargs = OrderedDict()
        self.specialargs = OrderedDict()
        # make special arguments
        self._make_specials()
        # define arg list
        self.arg_list = []
        self.str_arg_list = None
        # get drs parameters
        self.drs_params = ParamDict()
        self.input_params = OrderedDict()
        self.required_args = []
        self.optional_args = []
        self.special_args = []

    def get_drs_params(self, quiet=False, **kwargs):
        func_name = __NAME__ + '.DrsRecipe.get_drs_params()'
        const_name = 'spirouConfig.Constants'
        # Get config parameters from primary file
        try:
            self.drs_params, warn_messages = spirouConfig.ReadConfigFile()
        except ConfigError as e:
            WLOG(self.__error__(), e.level, e.message)
            self.drs_params, warn_messages = self.__error__(), []
        # ---------------------------------------------------------------------
        # assign parameters from kwargs
        for kwarg in kwargs:
            self.drs_params[kwarg] = kwargs[kwarg]
            self.drs_params.set_source(kwarg, func_name + ' --kwargs')
        # ---------------------------------------------------------------------
        # log warning messages
        if len(warn_messages) > 0:
            WLOG(self.drs_params, 'warning', warn_messages)
        # ---------------------------------------------------------------------
        # set recipe name
        while self.name.endswith('.py'):
            self.name = self.name[:-3]
        self.drs_params['RECIPE'] = self.name
        self.drs_params.set_source('RECIPE', func_name)
        # ---------------------------------------------------------------------
        # get variables from spirouConst
        self.drs_params['DRS_NAME'] = CONSTANTS.NAME()
        self.drs_params['DRS_VERSION'] = CONSTANTS.VERSION()
        self.drs_params.set_sources(['DRS_NAME', 'DRS_VERSION'], const_name)
        # get program name
        self.drs_params['PROGRAM'] = CONSTANTS.PROGRAM(self.drs_params)
        self.drs_params.set_source('PROGRAM', func_name)
        # TODO: Phase out use of LOG_OPT
        self.drs_params['LOG_OPT'] = self.drs_params['PROGRAM']
        self.drs_params.set_source('LOG_OPT', func_name)
        # check input parameters
        self.drs_params = spirouConfig.CheckCparams(self.drs_params)
        # ---------------------------------------------------------------------
        # if DRS_INTERACTIVE is not True then DRS_PLOT should be turned off too
        if not self.drs_params['DRS_INTERACTIVE']:
            self.drs_params['DRS_PLOT'] = 0
        # ---------------------------------------------------------------------
        # set up array to store inputs/outputs
        self.drs_params['INPUTS'] = OrderedDict()
        self.drs_params['OUTPUTS'] = OrderedDict()
        self.drs_params.set_sources(['INPUTS', 'OUTPUTS'], func_name)
        # ---------------------------------------------------------------------
        # load ICDP config file
        logthis = not quiet
        cargs = [self.drs_params, 'ICDP_NAME',]
        ckwargs = dict(required=True, logthis=logthis)
        self.drs_params = _load_other_config_file(*cargs, **ckwargs)
        # ---------------------------------------------------------------------
        # load keywords
        try:
            kout = spirouConfig.GetKeywordArguments(self.drs_params)
            self.drs_params, warnlogs = kout
            # print warning logs
            for warnlog in warnlogs:
                WLOG(self.drs_params, 'warning', warnlog)
        except spirouConfig.ConfigError as e:
            WLOG(self.drs_params, e.level, e.message)

    def recipe_setup(self, fkwargs):
        """
        Interface between "recipe", inputs to function ("fkwargs") and argparse
        parser (inputs from command line)

        :param fkwargs: dictionary, a dictionary where the keys match
                        arguments/keyword arguments in recipe (without -/--),
                        and the values are those to set in the output
                        (set to None for not value set)

        :return params:  dictionary, a dictionary where the keys match
                         arguments/keywords (without -/--) and values are the
                         values to be used for this recipe
        """
        # set up storage for arguments
        fmt_class = argparse.RawDescriptionHelpFormatter
        desc, epilog = self.description, self.epilog
        parser = DRSArgumentParser(self, description=desc, epilog=epilog,
                                   formatter_class=fmt_class,
                                   usage=self._drs_usage())
        # deal with function call
        self._parse_args(fkwargs)
        # ---------------------------------------------------------------------
        # add arguments from recipe
        for rarg in self.args:
            # extract out name and kwargs from rarg
            rname = self.args[rarg].names
            rkwargs = self.args[rarg].props
            # parse into parser
            parser.add_argument(*rname, **rkwargs)
        # ---------------------------------------------------------------------
        # add keyword arguments
        for rarg in self.kwargs:
            # extract out name and kwargs from rarg
            rname = self.kwargs[rarg].names
            rkwargs = self.kwargs[rarg].props
            # parse into parser
            parser.add_argument(*rname, **rkwargs)
        # add special arguments
        for rarg in self.specialargs:
            # extract out name and kwargs from rarg
            rname = self.specialargs[rarg].names
            rkwargs = self.specialargs[rarg].props
            # parse into parser
            parser.add_argument(*rname, **rkwargs)

        # get params
        params = vars(parser.parse_args(args=self.str_arg_list))
        del parser
        # update params
        self.input_params = params

    def option_manager(self):
        """
        Takes all the optional parameters and deals with them (i.e. puts them
        into self.drs_params

        :return None:
        """
        func_name = __NAME__ + '.DrsRecipe.option_manager()'
        # get drs params
        params = self.drs_params
        input_parameters = self.input_params
        # loop around options
        for key in self.kwargs:
            # get keyword argument
            kwarg = self.kwargs[key]
            # make sure kind == 'kwarg
            if kwarg.kind != 'kwarg':
                continue
            # check that kwarg is in input_parameters
            if kwarg.name not in input_parameters:
                eargs = [kwarg.name, self.name]
                emsg = 'Cannot find input "{0}" for recipe "{1}"'
                kwarg.exception(emsg.format(*eargs))
            # check that kwarg is None (should be None if we need to change it)
            if input_parameters[kwarg.name] is not None:
                # if we have the value we should pipe it into default_ref
                #  i.e. the value in the parameters file
                if kwarg.default_ref is not None:
                    param_key = kwarg.default_ref
                    value = input_parameters[kwarg.name]
                else:
                    continue
            # check that default is None
            elif kwarg.default is not None:
                value, param_key = kwarg.default, None
            # else check that we have default_ref
            elif kwarg.default_ref is None:
                eargs = [kwarg.name, self.name]
                emsg = '"default_ref" is unset for "{0}" for recipe "{1}"'
                kwarg.exception(emsg.format(*eargs))
                value, param_key = None, None
            # else check that default_ref is in drs_params (i.e. defined in a
            #   constant file)
            elif kwarg.default_ref not in params:
                eargs = [kwarg.default_ref, kwarg.name, self.name]
                emsg = ('"default_ref"="{0}" not found in constant params for '
                        ' "{1}" for recipe "{2}"')
                kwarg.exception(emsg.format(*eargs))
                value, param_key = None, None
            # else we have all we need to reset the value
            else:
                value = params[kwarg.default_ref]
                param_key = kwarg.default_ref
            # if we have reached this point then set value
            input_parameters[kwarg.name] = value
            if param_key is not None:
                input_parameters[kwarg.default_ref] = value
        # ---------------------------------------------------------------------
        # add to DRS parameters
        self.drs_params['INPUT'] = input_parameters
        self.drs_params.set_source('INPUT', func_name)
        # push values of keys matched in input_parameters into drs_parameters
        for key in input_parameters.keys():
            if key in self.drs_params:
                self.drs_params[key] = input_parameters[key]
                self.drs_params.set_source(key, func_name)

    def arg(self, name=None, **kwargs):
        """
        Add an argument to the recipe

        :param name: string or None, the name and reference of the argument
        :param kwargs: arguments that can be assigned to DrsArgument kwargs

        :return None:
        """
        # set name
        if name is None:
            name = 'Arg{0}'.format(len(self.args) + 1)
        # create argument
        argument = DrsArgument(name, kind='arg', **kwargs)
        # make arg parser properties
        argument.make_properties()
        # recast name
        name = argument.name
        # add to arg list
        self.args[name] = argument

    def kwarg(self, name=None, **kwargs):
        """
        Add a keyword argument to the recipe

        :param name: string or None, the name and reference of the argument
        :param kwargs: arguments that can be assigned to DrsArgument kwargs
        :return None:
        """
        if name is None:
            name = 'Kwarg{0}'.format(len(self.args) + 1)
        # create keyword argument
        keywordargument = DrsArgument(name, kind='kwarg', **kwargs)
        # make arg parser properties
        keywordargument.make_properties()
        # recast name
        name = keywordargument.name
        # set to keyword argument
        self.kwargs[name] = keywordargument

    def generate_runs_from_filelist(self, __files__, __filters__=None,
                                    **kwargs):
        """
        Generates a run instance (or set of run instances) based on the
        "__list__". Each file must be a absolute path. The directory (night name
        is taken from the absolute path minus the input directory given).
        Any additional non-file keyword arguments should be given after the
        file list, their names MUST match the name of that argument for correct
        assignment.

        :param __files__: list of string, absolute paths to all files to be
                         considered, non valid files will be skipped, if there
                         are no valid files the return will be empty

        :param __filters__: dictionary, keys are fits HEADER KEYS to search
                            and values are lists of strings that these HEADER
                            KEYS should have i.e.

                            __filters__ = {'DPRTYPE': ['DARK_DARK']}

                            or

                            __filters__ = {'OBJNAME': ['Gl699', 'Gl15A']}

                            or both

                            __filters__ = {'DPRTYPE': ['OBJ_FP'],
                                           'OBJNAME': ['Gl699', 'Gl15A']}

        :param kwargs: keyword arguments to pass to the function, each value
                       must match the name of that argument i.e. if the recipe
                       expects "x" as an argument
        :return:
        """
        func_name = __NAME__ + '.DrsRecipe.generate_runs_from_filelist()'
        # get input directory
        input_dir = self._get_input_dir()
        # get directories and filter out unusable file (due to wrong location)
        filelist = _dir_file_filter(input_dir, __files__)
        # from the unique directory list search for index files (should be one
        #   per file)
        dir_list = list(filelist.keys())
        index_files = _get_index_files(self, input_dir, dir_list)
        # ---------------------------------------------------------------------
        # loop around arguments
        for argname in self.args:
            # get dtype for arg
            dtype = self.args[argname].dtype
            # -----------------------------------------------------------------
            # deal with directory (If not defined set to None)
            if ('directory' not in kwargs) and (dtype == 'directory'):
                self.args[argname].value = None
            # -----------------------------------------------------------------
            # if argument is of dtype "files" or "file" then we need to
            # look for it in the index file else we need to look in
            # **kwargs
            elif dtype not in ['files', 'file']:
                self._get_non_file_arg(argname, kwargs, kind='arg')
            # -----------------------------------------------------------------
            # else we are dealing with a set of files
            else:
                self._get_file_arg(argname, index_files, filelist, dir_list,
                                   kind='arg', filters=__filters__)
        # ---------------------------------------------------------------------
        # loop around keyword arguments
        for kwargname in self.kwargs:
            # get dtype for arg
            dtype = self.kwargs[kwargname].dtype
            # -----------------------------------------------------------------
            # if argument is of dtype "files" or "file" then we need to
            # look for it in the index file else we need to look in
            # **kwargs
            if dtype not in ['files', 'file']:
                self._get_non_file_arg(kwargname, kwargs, kind='kwarg')
            # -----------------------------------------------------------------
            # else we are dealing with a set of files
            else:
                self._get_file_arg(kwargname, index_files, filelist, dir_list,
                                   kind='kwarg', filters=__filters__)

        # ---------------------------------------------------------------------
        # from the above process we now have the following:
        #    self.args[ARG].value = [argument value]
        #    self.args[ARG].value = dictionary[DrsFitsFile]
        #
        #    where ARG is for each argument in recipe
        #    where value is either a list with a single entry (for non-file
        #        arguments) or a dictionary for file arguments
        #    where each dictionary is a list of DrsFitsFile instances for all
        #        the files found in filelist
        # ---------------------------------------------------------------------
        # next we need to turn this into a set of runs
        # each run should be in the form:
        #       run[it] = "recipe arg1 arg2 ... kwarg1= kwarg2="
        # define control string
        cmd = '{0}.py'.format(self.name)
        # ---------------------------------------------------------------------
        # first deal with positional arguments
        out1 = self._generate_arg_groups(argkind='args')
        cmd_args_groups, dict_arg_groups, dirs1 = out1
        out2 = self._generate_arg_groups(argkind='kwargs')
        cmd_kwargs_groups, dict_kwarg_groups, dirs2 = out2

        # need to match directories based on dirs1 and dirs2
        cmd_groups = []
        dict_groups = []

        # if the first set in dirs1 is None we have no fileargs from "args"
        if dirs1[0] is None:
            # loop around runs (from kwargs_groups)
            for it in range(len(cmd_kwargs_groups)):
                # need to add directory onto cmd_args_group (at start)
                cmd_str = '{0} {1}'.format(dirs2[it], cmd_args_groups[0])
                # merge cmd
                cmd_groups.append(cmd_str + cmd_kwargs_groups[it])
                # merge dict
                tmp = OrderedDict(directory=dirs2[it])
                for key in dict_arg_groups[0]:
                    tmp[key] = dict_arg_groups[0][key]
                for key in dict_kwarg_groups[it]:
                    tmp[key] = dict_kwarg_groups[it][key]
                dict_groups.append(tmp)

        # if the first set in dirs2 is None we have no fileargs from "kwargs"
        elif dirs2[0] is None:
            # loop around runs (from kwargs_groups)
            for it in range(len(cmd_args_groups)):
                # merge cmd
                cmd_groups.append(cmd_args_groups[it] + cmd_kwargs_groups[0])
                # merge dict
                tmp = OrderedDict()
                for key in dict_arg_groups[it]:
                    tmp[key] = dict_arg_groups[it][key]
                for key in dict_kwarg_groups[0]:
                    tmp[key] = dict_kwarg_groups[0][key]
                dict_groups.append(tmp)

        # else we have to match directories to directores - crash for now
        else:
            emsg1 = ('Neil Error: Cannot have "files" in both positional and '
                     'optional args')
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(self.drs_params, 'error', [emsg1, emsg2])

        # ---------------------------------------------------------------------
        # Now deal with printing the runs (combine command with arguments)
        printruns = []
        # loop around the cmd_groups (combined arg + kwarg)
        for cmd_args in cmd_groups:
            # generate command
            run_it = '{0} {1}'.format(cmd, cmd_args)
            # tidy up
            while "  " in run_it:
                run_it = run_it.replace("  ", " ")
            # append to runs
            printruns.append(run_it)
        # return in form:
        #       runs[it] = "recipe arg1 arg2 ... kwarg1= kwarg2="
        return printruns, dict_groups

    def main(self, **kwargs):
        """
        Run the main function associated with this recipe

        :param kwargs: kwargs passed to the main functions

        :return:
        """

        # need to check if module is defined
        if self.module is None:
            self.module = self._import_module()
        if self.module is None:
            emsg1 = 'Dev Error: Cannot find module "{0}"'.format(self.name)
            emsg2 = '\tProblem with recipe definition'
            emsg3 = ('\tRecipe name must match recipe python file name and be '
                     'in PYTHONPATH')
            WLOG(self.drs_params, 'error', [emsg1, emsg2, emsg3])

        # run main
        return self.module.main(**kwargs)

    # =========================================================================
    # Private Methods (Not to be used externally to spirouRecipe.py)
    # =========================================================================
    def _import_module(self):
        # get local copy of module
        try:
            return importlib.import_module(self.name)
        except Exception as e:
            return None

    def _parse_args(self, dictionary=None):
        """
        Parse a dictionary of arguments into argparser in the format required
        to match up to the recipe.args/recipe.kwarg assigned to this
        DrsRecipe by calls to "recipe.arg" and "recipe.kwarg"

        :param dictionary: list of key value pairs where the keys must match
                           the names (without "-" and "--") of the arguments
                           and keyword arguments. This is then passed into
                           "recipe.str_arg_list" for parsing into argparser
                           directly (and overiding run time arguments)
        :return None:
        """
        self.str_arg_list = []
        if dictionary is None:
            return None
        for argname in self.args:
            # check if key in dictionary
            if argname not in dictionary:
                continue
            # get value(s)
            values = dictionary[argname]
            # pass this argument
            self._parse_arg(self.args[argname], values)
        for kwargname in self.kwargs:
            # check if key in dictionary
            if kwargname not in dictionary:
                continue
            # get value(s)
            values = dictionary[kwargname]
            # pass this argument
            self._parse_arg(self.kwargs[kwargname], values)
        for sname in self.specialargs:
            # copy sname
            sname1 = str(sname)
            # remove '-'
            while sname1[0] == '-':
                sname1 = sname1[1:]
            # check if key in dictionary
            if sname1 not in dictionary:
                continue
            # get value(s)
            values = dictionary[sname1]
            # pass this argument
            self._parse_arg(self.specialargs[sname], values)

        # check if we have parameters
        if len(self.str_arg_list) == 0:
            self.str_arg_list = None

    def _parse_arg(self, arg, values):
        """
        Parse argument to "recipe.str_arg_list"

        :param arg: str, the name of the argument (with "-" and "--" for
                    optional arguments)
        :param values: object, the object to push into the value of argument.
                       The string representation of this value must be
                       readable by argparser i.e. int/float/str etc
        :return None:
        """
        # check that value is not None
        if values is None:
            return
        # if we have an optional argument
        if '-' in arg.argname:
            strfmt = '{0}={1}'
        # if we have a positional argument
        else:
            strfmt = '{1}'
        # now add these arguments (as a string) to str_arg_list
        if type(values) == list:
            for value in values:
                strarg = [arg.argname, value]
                self.str_arg_list.append(strfmt.format(*strarg))
        else:
            strarg = [arg.argname, values]
            self.str_arg_list.append(strfmt.format(*strarg))

    def _make_specials(self):
        """
        Make special arguments based on pre-defined static properties
        (i.e. a valid kwargs for parser.add_argument)

        Currently adds the following special arguments:

        --listing, --list     List the files in the given input directory

        :return None:
        """
        # ---------------------------------------------------------------------
        # make debug functionality
        dprops = _make_debug()
        name = dprops['name']
        debug = DrsArgument(name, kind='special', altnames=dprops['altnames'])
        debug.assign_properties(dprops)
        debug.skip = False
        debug.helpstr = dprops['help']
        self.specialargs[name] = debug
        # ---------------------------------------------------------------------
        # make listing functionality
        lprops = _make_listing()
        name = lprops['name']
        listing = DrsArgument(name, kind='special', altnames=lprops['altnames'])
        listing.assign_properties(lprops)
        listing.skip = True
        listing.helpstr = lprops['help']
        self.specialargs[name] = listing
        # ---------------------------------------------------------------------
        # make listing all functionality
        aprops = _make_alllisting()
        name = aprops['name']
        alllist = DrsArgument(name, kind='special', altnames=aprops['altnames'])
        alllist.assign_properties(aprops)
        alllist.skip = True
        alllist.helpstr = aprops['help']
        self.specialargs[name] = alllist
        # ---------------------------------------------------------------------
        # make version functionality
        vprops = _make_version()
        name = vprops['name']
        version = DrsArgument(name, kind='special', altnames=vprops['altnames'])
        version.assign_properties(vprops)
        version.skip = True
        version.helpstr = vprops['help']
        self.specialargs[name] = version
        # ---------------------------------------------------------------------
        # make info functionality
        iprops = _make_info()
        name = iprops['name']
        info = DrsArgument(name, kind='special', altnames=iprops['altnames'])
        info.assign_properties(iprops)
        info.skip = True
        info.helpstr = iprops['help']
        self.specialargs[name] = info

    def _drs_usage(self):
        # reset required args
        self.required_args = []
        self.optional_args = []
        self.special_args = []
        # ---------------------------------------------------------------------
        # add arguments from recipe
        for rarg in self.args:
            # add to required
            self.required_args.append(self.args[rarg])
        # ---------------------------------------------------------------------
        # add keyword arguments
        for rarg in self.kwargs:
            # extract out kwargs from rarg
            rkwargs = self.kwargs[rarg].props
            # add to required
            if 'required' in rkwargs:
                if rkwargs['required']:
                    self.required_args.append(self.kwargs[rarg])
                else:
                    self.optional_args.append(self.kwargs[rarg])
            else:
                self.optional_args.append(self.kwargs[rarg])
        # add special arguments
        for rarg in self.specialargs:
            # extract out kwargs from rarg
            rkwargs = self.specialargs[rarg].props
            # add to required
            if 'required' in rkwargs:
                if rkwargs['required']:
                    self.required_args.append(self.specialargs[rarg])
                else:
                    self.special_args.append(self.specialargs[rarg])
            else:
                self.special_args.append(self.specialargs[rarg])
        # ---------------------------------------------------------------------
        # get positional arguments
        pos_args = []
        for rarg in self.required_args:
            pos_args.append(rarg.names[0])
        # deal with no positional arguments
        if len(pos_args) == 0:
            pos_args = ['[positional arguments]']
        # define usage
        uargs = [self.name, ' '.join(pos_args)]
        usage = '{0}.py {1} [options]'.format(*uargs)
        return usage

    def _valid_directory(self, directory, return_error=False):

        # ---------------------------------------------------------------------
        # Make sure directory is a string
        if type(directory) not in [str, np.str_]:
            emsg = 'directory = "{0}" is not valid (type = {1})'
            eargs = [directory, type(directory)]
            if return_error:
                return False, [emsg.format(*eargs)]
            else:
                return False
        # ---------------------------------------------------------------------
        # step 1: check if directory is full absolute path
        if os.path.exists(directory):
            if DEBUG:
                'Directory found (absolute path): {0}'.format(directory)
            if return_error:
                return True, directory, []
            else:
                return False, directory
        # ---------------------------------------------------------------------
        # step 2: check if directory is in input directory
        input_dir = self._get_input_dir()
        test_path = os.path.join(input_dir, directory)
        if os.path.exists(test_path):
            if return_error:
                return True, test_path, []
            else:
                return True, test_path
        # ---------------------------------------------------------------------
        # else deal with errors
        emsgs = ['Directory = "{0}" not found'.format(directory),
                 '\tTried:',
                 '\t\t{0}'.format(directory),
                 '\t\t{0}'.format(test_path)]
        return False, None, emsgs

    def _valid_files(self, argname, files, directory=None, return_error=False,
                     alltypelist=None, allfilelist=None):
        # deal with no current typelist (alltypelist=None)
        if alltypelist is None:
            alltypelist = []
        # deal with no current filelist (allfilelist=None)
        if allfilelist is None:
            allfilelist = []
        # deal with non-lists
        if type(files) not in [list, np.ndarray]:
            files = [files]
        # loop around files
        all_files = []
        all_types = []
        for filename in files:
            # check single file
            out = self._valid_file(argname, filename, directory, True,
                                   alltypelist=alltypelist,
                                   allfilelist=allfilelist)
            file_valid, filelist, typelist, error = out
            # if single file is not valid return the error (and False)
            if not file_valid:
                if return_error:
                    return False, None, None, error
                else:
                    return False, None, None
            # else we append filelist to all_files
            else:
                all_files += filelist
                all_types += typelist
        # if we are at this point everything passed and file is valid
        if return_error:
            return True, all_files, all_types, []
        else:
            return True, all_files, all_types, []

    def _valid_file(self, argname, filename, directory=None, return_error=False,
                    alltypelist=None, allfilelist=None):
        """
        Test for whether a file is valid for this recipe

        :param filename: string, the filename to test
        :param return_error: bool, if True returns error list

        :return cond: bool, if True file is valid, if False file is not valid
        :return filelist: list of strings, list of files found
        :return error: list of strings, if there was an error (cond = False)
                       and return_error=True, return a list of strings
                       describing the error
        """
        # get drs parameters
        params = self.drs_params
        # deal with no current typelist (alltypelist=None)
        if alltypelist is None:
            alltypelist = []
        if allfilelist is None:
            allfilelist = []
        # get the argument that we are checking the file of
        arg = _get_arg(self, argname)
        drs_files = arg.files
        drs_logic = arg.filelogic
        # ---------------------------------------------------------------------
        # Step 1: Check file location is valid
        # ---------------------------------------------------------------------
        # if debug mode print progress
        if DEBUG:
            dmsg = 'DEBUG: Checking file locations for "{0}"'
            WLOG(params, 'info', dmsg.format(filename))
        # perform check
        out = _check_file_location(self, argname, directory, filename)
        valid, files, error = out
        if not valid:
            if return_error:
                return False, None, None, error
            else:
                return False, None, None
        # ---------------------------------------------------------------------
        # The next steps are different depending on the DRS file and
        # we may have multiple files
        out_files = []
        out_types = []
        # storage of checked files
        checked_files = []
        # storage of errors (if we have no files)
        errors = []
        # loop around filename
        for filename in files:
            # start of with the file not being valid
            valid = False
            # storage of errors (reset)
            errors = []
            header_errors = dict()
            # add to checked files
            checked_files.append(filename)
            # loop around file types
            for drs_file in drs_files:
                # if in debug mode print progres
                if DEBUG:
                    dmsg = 'DEBUG: Checking drs_file="{0}" filename="{1}"'
                    dargs = [drs_file.name, os.path.basename(filename)]
                    WLOG(params, 'info', dmsg.format(*dargs))
                # -------------------------------------------------------------
                # Step 2: Check extension
                # -------------------------------------------------------------
                # get extension
                ext = drs_file.ext
                # check the extension
                exargs = [self, argname, filename]
                valid1, error1 = _check_file_extension(*exargs, ext=ext)

                # -------------------------------------------------------------
                # Step 3: Check file header is valid
                # -------------------------------------------------------------
                # this step is just for 'fits' files, if not fits
                #    files we can return here
                if ('.fits' in filename) and valid1:
                    out = _check_file_header(self, argname, drs_file, filename,
                                             directory)
                    valid2, filetype, error2 = out
                    valid2a, valid2b = valid2
                    error2a, error2b = error2
                else:
                    valid2a, valid2b = True, True
                    error2a, error2b = [], dict()
                    filetype = None
                # -------------------------------------------------------------
                # Step 4: Check exclusivity
                # -------------------------------------------------------------
                # only check if file correct
                if valid1 and valid2a and valid2b:
                    exargs = [self, filename, argname, drs_file, drs_logic,
                              out_types, alltypelist]
                    valid3, error3 = _check_file_exclusivity(*exargs)
                else:
                    valid3, error3 = True, None

                # -------------------------------------------------------------
                # Step 5: Combine
                # -------------------------------------------------------------
                valid = valid1 and valid2a and valid2b and valid3
                # choose which to print as error
                if (not valid1) and valid2a and valid2b and valid3:
                    errors += error1
                if (not valid2a) and valid1 and valid3:
                    errors += error2a
                if valid1:
                    header_errors[drs_file.name]  = error2b
                # only add check3 if check2 was valid
                if (not valid3) and valid2a and valid2b and valid1:
                    errors += error3

                # check validity and append if valid
                if valid:
                    if DEBUG:
                        dmsg = 'DEBUG: File "{0}" Passes all criteria'
                        dargs = [os.path.basename(filename)]
                        WLOG(params, 'info', dmsg.format(*dargs))

                    out_files.append(filename)
                    out_types.append(filetype)
                    # break out the inner loop if valid (we don't need to
                    #    check other drs_files)
                    break
            # if this file is not valid we should break here
            if not valid:
                # add header errors (needed outside drs_file loop)
                errors += _gen_header_errors(header_errors)
                # add file error (needed only once per filename)
                errors += ['File = {0}'.format(os.path.basename(filename))]
                break

        # must append all files checked
        allfiles = allfilelist + checked_files

        if len(allfiles) > 1:
            errors += ['', 'All files checked:']
            for filename in allfiles:
                errors+=['\t\t{0}'.format(filename)]

        # ---------------------------------------------------------------------
        # clean up errors (do not repeat same lines)
        cleaned_errors = []
        for error in errors:
            if error not in cleaned_errors:
                cleaned_errors.append(error)
        # ---------------------------------------------------------------------
        # deal with return types:
        # a. if we don't have the right number of files then we failed
        if len(out_files) != len(files):
            return False, None, None, cleaned_errors
        # b. if we did but expect an error returned return True with an error
        elif return_error:
            return True, out_files, out_types, []
        # c. if we did and don't expect an error return True without an error
        else:
            return True, out_files, out_types

    def _generate_arg_groups(self, argkind='args'):
        """
        Generate argument runs from self.args[ARG].value
        (For use after self.get_file_arg and self.get_non_file_arg for
         kind='arg')

        Expects one and only one argument with dtype "file" or "files"
        Will also deal with argument "directory being set"

        :return runs: list of runs in form:
               runs[it] = "recipe arg1 arg2 ... kwarg1= kwarg2="
        """
        func_name = __NAME__ + '.DrsRecipe._generate_arg_groups()'
        # --------------------------------------------------------------------
        # deal with kind
        if argkind == 'args':
            args = self.args
            cmdfmt = '{1} '
        elif argkind == 'kwargs':
            args = self.kwargs
            cmdfmt = '--{0} {1} '
        else:
            emsg1 = 'Dev Error: Kind="{0}" not supported'.format(argkind)
            emsg2 = '\tfunction = {0}'.format(func_name)
            WLOG(self.drs_params, 'error', [emsg1, emsg2])
            args, cmdfmt = None, ''
        # ---------------------------------------------------------------------
        # storage
        positions = OrderedDict()
        file_args = []
        directories, lengths = OrderedDict(), OrderedDict()
        arg_list, file_dates = OrderedDict(), OrderedDict()
        # ---------------------------------------------------------------------
        # find file args (use last)
        for argname in args:
            # get this instances arg
            arg = args[argname]
            # get position
            if argkind == 'args':
                pos = int(str(arg.pos).strip('+'))
            else:
                pos = argname
            # set dirs, kind and dates to None
            dirs, kind, dates = None, None, None
            # -----------------------------------------------------------------
            # deal with directory arg
            if argname == 'directory':
                values = [arg.value]
            # -----------------------------------------------------------------
            # deal with files
            elif arg.dtype in ['file', 'files']:
                # do not consider if None
                if arg.value is None:
                    continue
                # do not consider if list is empty
                if len(arg.value) == 0:
                    continue
                # Now only deal with file arg
                arg = args[argname]
                # get grouped values and directories
                #   Note groups returned in following format:
                #      group[directory][dtype][sequence] = [files]
                groups = _get_file_groups(self, arg)
                values = groups[0]
                dirs = groups[1]
                dates = groups[-1]
                file_args.append(argname)
            # -----------------------------------------------------------------
            # deal with other non-file arguments
            else:
                values = [arg.value] * len(self.args)
            # add the position to dictionary
            positions[pos] = argname
            # -----------------------------------------------------------------
            # add them to arg_list
            arg_list[argname] = values
            lengths[argname] = len(values)
            directories[argname] = dirs
            file_dates[argname] = dates
        # ---------------------------------------------------------------------
        # We need to then match the files with directories, and if there is
        #   more than one argument with files we need to match them
        if len(file_args) == 1:
            arg_list['directory'] = directories[file_args[0]]
            number_runs = len(directories[file_args[0]])
        elif len(file_args) > 1:
            margs = [self, file_args, arg_list, directories, file_dates]
            arg_list, number_runs = _match_multi_arg_lists(*margs)
        else:
            number_runs = 1
        # ---------------------------------------------------------------------
        # get directories as special
        if 'directory' in arg_list:
            outdirs = arg_list['directory']
        else:
            outdirs = [None]
        # ---------------------------------------------------------------------
        # storage for cmd arg groups
        cmd_args_groups = []
        # storage for dict arg groups
        dict_args_groups = []
        # loop around number of runs
        for it in range(number_runs):
            cmd_arg = ''
            dict_arg = dict()
            # loop around arguments (in order)
            for key in positions:
                # get position key value
                poskey = positions[key]
                # get values
                if poskey in file_args:
                    values = arg_list[poskey][it]
                else:
                    values = arg_list[poskey][0]
                # construct cmd arg
                if type(values) in [list, np.ndarray]:
                    # may have Nones (where matching failed)
                    if None in values:
                        continue
                    # construct command argument
                    cmd_arg += cmdfmt.format(poskey, ' '.join(values))
                    dict_arg[poskey] = list(values)
                else:
                    # may have Nones (where matching failed)
                    if values is None:
                        continue
                    # construct command argument
                    cmd_arg += cmdfmt.format(poskey, values)
                    dict_arg[poskey] = values
            cmd_args_groups.append(cmd_arg)
            dict_args_groups.append(dict_arg)
        # ---------------------------------------------------------------------
        return cmd_args_groups, dict_args_groups, outdirs

    def _get_non_file_arg(self, argname, kwargs, kind='arg'):
        """
        Deal with obtaining and setting the values for non file arguments

        :param argname: string, the argument name
        :param kwargs: dictionary, the keyword arguments from call (must
                       contain "argname")

        :return None:
        """
        func_name = __NAME__ + '.DrsRecipe.get_non_file_arg()'
        # get instance from self.args
        if kind == 'arg':
            arg = self.args[argname]
            arg_string = 'Argument'
        else:
            arg = self.kwargs[argname]
            arg_string = 'Keyword Argument'
        # check that argname is defined
        if argname in kwargs:
            # copy value from kwargs (as deep copy)
            value = type(kwargs[argname])(kwargs[argname])
            # update self.args
            arg.value = value
        elif kind == 'arg':
            emsg = ('DevError: {0} "{1}" is not defined in call to {2}'
                    ''.format(arg_string, argname, func_name))
            WLOG(self.drs_params, 'error', emsg)
        # update self
        if kind == 'arg':
            self.args[argname] = arg
        else:
            self.kwargs[argname] = arg

    def _get_file_arg(self, argname, index_files, filelist, dir_list,
                      kind='arg', filters=None):
        """
        Deal with obtaining and sorting the values for file arguments

        :param argname: string, the argument name
        :param index_files: list of strings, the absolute paths to the index
                            files
        :param filelist: list of strings, the basenames for all the files
        :param dir_list: list of strings, the sub-directory tree names for
                         each file in "filelist"

        :return None:
        """
        # get instance from self.args
        if kind == 'arg':
            arg = self.args[argname]
        else:
            arg = self.kwargs[argname]
        # set up the value of arg
        arg.value = []
        # for each index file find all valid files (for this argument)
        for it, index_file in enumerate(index_files):
            # get directory
            directory = dir_list[it]
            dir_filelist = filelist[directory]
            # get index
            index = _get_index_data(self.drs_params, index_file, directory)
            # apply filters
            index = _filter_index(self.drs_params, index, filters)
            # deal with no index
            if index is None:
                continue
            # else get list of valid files for this argument
            gargs = [arg, index, directory, dir_filelist]
            new_values = self._get_files_valid_for_arg(*gargs)

            if new_values is not None:
                arg.value += new_values

        # update self
        if kind == 'arg':
            self.args[argname] = arg
        else:
            self.kwargs[argname] = arg

    def _get_input_dir(self):
        """
        Get the input directory for this recipe based on what was set in
        initialisation (construction)

        if RAW uses DRS_DATA_RAW from drs_params
        if TMP uses DRS_DATA_WORKING from drs_params
        if REDUCED uses DRS_DATA_REDUC from drs_params

        :return input_dir: string, the input directory
        """
        # check if "input_dir" is in namespace
        input_dir_pick = self.inputdir.upper()
        # get parameters from recipe call
        params = self.drs_params
        # get the input directory from recipe.inputdir keyword
        if input_dir_pick == 'RAW':
            input_dir = self.drs_params['DRS_DATA_RAW']
        elif input_dir_pick == 'TMP':
            input_dir = self.drs_params['DRS_DATA_WORKING']
        elif input_dir_pick == 'REDUCED':
            input_dir = self.drs_params['DRS_DATA_REDUC']
        # if not found produce error
        else:
            emsg1 = ('Recipe definition error: "inputdir" must be either'
                     ' "RAW", "REDUCED" or "TMP".')
            emsg2 = '\tCurrently has value="{0}"'.format(input_dir_pick)
            WLOG(params, 'error', [emsg1, emsg2])
            input_dir = None
        # return input_dir
        return input_dir

    def _get_files_valid_for_arg(self, arg, index, directory, dfilelist):
        """
        Gets all files in filelist that are in "index" that meet the
        requirements of "arg.files"

        :param arg: DrsArgument, an instance of spirouRecipe.DrsArgument
        :param index: astropy.table, Table from the INDEX_FILE for this
                      directory
        :param directory: string, the sub-directory tree (night name) under
                          the input_dir
        :param dfilelist: list of strings, the base filenames of the files
                         in "directory" that we want to filter from

        :return valid_files: dictionary, the files (from "filelist" that are
                             in each arg.files. keys are the names of the
                             arg.files values are lists of the files found.
        """
        # convert filelist to a numpy array
        dfilelist = np.array(dfilelist, dtype=str)
        ifilelist = np.array(index['FILENAME'], dtype=str)
        # strip arrays
        dfilelist = np.char.strip(dfilelist, ' ')
        ifilelist = np.char.strip(ifilelist, ' ')
        # get this directories index file name
        ifile = os.path.join(directory, INDEX_FILE)
        icol = INDEX_FILE_NAME_COL
        # get input directory
        input_dir = self._get_input_dir()
        # get path of directory
        path = os.path.join(input_dir, directory)
        # get params from recipe
        params = self.drs_params
        # ---------------------------------------------------------------------
        # step 1: find all filelist entries in filelist
        # ---------------------------------------------------------------------
        mask = np.in1d(ifilelist, dfilelist)
        # deal with no entries
        if np.sum(mask) == 0:
            if DEBUG:
                wmsg = 'No matching files for index_file "{0}"'.format(ifile)
                WLOG(params, '', wmsg.format(index))
            return []
        else:
            if DEBUG:
                wargs = [np.sum(mask), ifile]
                wmsg = 'Found {0} files for index_file "{1}"'
                WLOG(params, '', wmsg.format(*wargs))
        # apply mask to index data
        indexdata = index[mask]
        # ---------------------------------------------------------------------
        # step 2: find all files that have the correct header keys
        # ---------------------------------------------------------------------
        # storage of valid files
        valid_files = []
        # loop around required file types
        for drs_file in arg.files:
            # storage for masks
            mask = np.ones(len(indexdata), dtype=bool)
            # get required keyword arguments
            rkeys = drs_file.required_header_keys
            # loop around these keys
            for rkey in rkeys:
                # get the key
                if rkey in params:
                    key = params[rkey][0]
                else:
                    key = str(rkey)
                # deal with rkey not in indexdata
                if key not in indexdata.colnames:
                    return None
                # mask by rkey value
                indexdatakey = np.array(indexdata[key], dtype=str)
                indexdatakey = np.char.strip(indexdatakey, ' ')
                mask &= indexdatakey == rkeys[rkey]
            # once all are done add to valid entries list in the form of a
            #   drs_file for each, adding attributes:
            #          - path, basename
            #          - inputdir, directory
            #          - header (from indexdata[mask][it])
            #                 where it is the row number after masking
            valid_entries = []
            used_filenames = []
            for v_it, valid_file in enumerate(indexdata[icol][mask]):
                # check that we haven't used this file already
                if valid_file in used_filenames:
                    continue
                # else add this file to valid files
                else:
                    used_filenames.append(valid_file)
                # make new drs_file instances
                tmp_file = drs_file.new()
                # get path of file
                tmp_path = os.path.join(path, directory, valid_file)
                # set filename
                tmp_file.set_filename(tmp_path, check=False)
                tmp_file.directory = directory
                tmp_file.inputdir = input_dir
                # make a header from index data table
                tmp_file.index = _make_dict_from_table(indexdata[mask][v_it])
                # append to list
                valid_entries.append(tmp_file)
            valid_files += valid_entries

            if DEBUG:
                wargs = [len(valid_files), drs_file.name]
                wmsg = '\t - Found {0} valid files for DrsFileType "{1}"'
                WLOG(params, '', wmsg.format(*wargs))

        # return valid files
        return valid_files

    def __error__(self):
        """
        The option log for WLOG for all errors in class

        :return log_opt: string, the log_opt message for WLOG
        """
        if 'PID' not in self.drs_params:
            self.drs_params['PID'] = None
        if 'RECIPE' not in self.drs_params:
            self.drs_params['RECIPE'] = __NAME__.replace('.py', '')
        # return drs_params
        return self.drs_params

    def __str__(self):
        """
        Defines the str(DrsRecipe) return for DrsRecipe
        :return str: the string representation of DrsRecipe
                     i.e. DrsRecipe[name]
        """
        return 'DrsRecipe[{0}]'.format(self.name)

    def __repr__(self):
        """
        Defines the print(DrsRecipe) return for DrsRecipe
        :return str: the string representation of DrsRecipe
                     i.e. DrsRecipe[name]
        """
        return 'DrsRecipe[{0}]'.format(self.name)


# =============================================================================
# Define file check functions
# =============================================================================
def _check_file_location(recipe, argname, directory, filename):
    """
    Checks file location is valid on:
        "filename" as full link to file (including wildcards)
        "filename" + recipe.inputdir.upper() (including wildcards)
        "filename" + ".fits" as full link to file (inlcluding wildcards)
        "filename" + ".fits" + recipe.inputdir.upper() (including wildcards)

    :param recipe: DrsRecipe instance
    :param filename: string, the filename to test

    :return cond: bool, if True file is valid, if False file is not valid
    :return filelist: list of strings, list of files found
    :return error: list of strings, if there was an error (cond = False)
                   and return_error=True, return a list of strings
                   describing the error
    """
    output_files = []
    # get drs parameters
    params = recipe.drs_params
    # get input directory
    if directory is not None:
        input_dir = str(directory)
    else:
        input_dir = recipe._get_input_dir()
    # -------------------------------------------------------------------------
    # Step 1: check "filename" as full link to file (including wildcards)
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(filename)
    # debug output
    if DEBUG and len(raw_files) == 0:
        dmsg = 'Argument "{0}": File not found: "{1}"'
        dargs = [argname, filename]
        WLOG(params, '', dmsg.format(*dargs))
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        if DEBUG:
            dmsg = 'Argument "{0}": File found (Full file path): "{1}"'
            WLOG(params, '', dmsg.format(argname, raw_file))
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, []
    # -------------------------------------------------------------------------
    # Step 2: recipe.inputdir.upper() (including wildcards)
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(os.path.join(input_dir, filename))
    # debug output
    if DEBUG and len(raw_files) == 0:
        dmsg = 'Argument "{0}": File not found: "{1}"'
        dargs = [argname, os.path.join(input_dir, filename)]
        WLOG(params, '', dmsg.format(*dargs))
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        if DEBUG:
            dmsg = 'Argument "{0}": File found (Input file path): "{1}"'
            WLOG(params, '', dmsg.format(argname, raw_file))
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, []
    # -------------------------------------------------------------------------
    # Step 3: check "filename" as full link to file (including wildcards)
    #         + .fits
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(filename + '.fits')
    # debug output
    if DEBUG and len(raw_files) == 0 and not filename.endswith('.fits'):
        dmsg = 'Argument "{0}": File not found: "{1}"'
        dargs = [argname, filename + '.fits']
        WLOG(params, '', dmsg.format(*dargs))
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        if DEBUG:
            dmsg = 'Argument "{0}": File found (Full file path + ".fits"): "{1}"'
            WLOG(params, '', dmsg.format(argname, raw_file))
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, []
    # -------------------------------------------------------------------------
    # Step 4: recipe.inputdir.upper() (including wildcards)
    #         + .fits
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(os.path.join(input_dir, filename + '.fits'))
    # debug output
    if DEBUG and len(raw_files) == 0 and not filename.endswith('.fits'):
        dmsg = 'Argument "{0}": File not found: "{1}"'
        dargs = [argname, os.path.join(input_dir, filename + '.fits')]
        WLOG(params, '', dmsg.format(*dargs))
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        if DEBUG:
            dmsg = ('Argument "{0}": File found (Input file path + ".fits"): '
                    '"{1}"')
            WLOG(params, '', dmsg.format(argname, raw_file))
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, []
    # -------------------------------------------------------------------------
    # Deal with cases where we didn't find file
    # -------------------------------------------------------------------------
    eargs = [argname, filename]
    emsgs = ['Argument "{0}": File = "{1}" was not found'.format(*eargs),
             '\tTried:',
             '\t\t"{0}"'.format(filename),
             '\t\t"{0}"'.format(os.path.join(input_dir, filename))]
    if not filename.endswith('.fits'):
        fitsfile = filename + '.fits'
        emsgs.append('\t\t"{0}"'.format(fitsfile))
        emsgs.append('\t\t"{0}"'.format(os.path.join(input_dir, fitsfile)))
    # return False, no files and error messages
    return False, None, emsgs


def _check_file_extension(recipe, argname, filename, ext=None):
    """
    If '.fits' file checks the file extension is valid.

    :param argname: string, the argument name (for error reporting)
    :param filename: list of strings, the files to check
    :param ext: string or None, the extension to check, if None skips

    :return cond: bool, True if extension valid
    :return errors: list of strings, the errors that occurred if cond=False
    """
    # get drs parameters
    params = recipe.drs_params
    # deal with no extension (ext = None)
    if ext is None:
        return True, []
    # ---------------------------------------------------------------------
    # Check extension
    valid = filename.endswith(ext)
    # if valid return True and no error
    if valid:
        if DEBUG:
            dmsg = 'Argument "{0}": Valid file extension for file "{1}"'
            dargs = [argname, os.path.basename(filename)]
            WLOG(params, '', dmsg.format(*dargs))
        return True, []
    # if False generate error and return it
    else:
        emsgs = ['Argument "{0}": Extension of file not valid'.format(argname),
                 '\t\tRequired extension = "{0}"'.format(ext)]
        return False, emsgs


def _check_file_header(recipe, argname, drs_file, filename, directory):
    # get the input directory
    inputdir = recipe._get_input_dir()
    # create an instance of this drs_file with the filename set
    file_instance = drs_file.new(filename=filename, recipe=recipe)
    file_instance.read()
    # set the directory
    file_instance.directory = _get_uncommon_path(directory, inputdir)
    # -----------------------------------------------------------------
    # use file_instances check file header method
    return file_instance.check_file_header(argname=argname, debug=DEBUG)


def _check_file_exclusivity(recipe, filename, argname, drs_file, logic,
                            outtypes, alltypelist=None):
    # get drs parameters
    params = recipe.drs_params
    # deal with no alltypelist
    if alltypelist is None:
        alltypelist = list(outtypes)
    else:
        alltypelist = list(alltypelist) + list(outtypes)

    # if we have no files yet we don't need to check exclusivity
    if len(alltypelist) == 0:
        if DEBUG:
            dmsg = ('Argument "{0}": Exclusivity check skipped for first file.'
                    '(type="{1}")')
            WLOG(params, '', dmsg.format(argname, drs_file.name))
        return True, []
    # if argument logic is set to "exclusive" we need to check that the
    #   drs_file.name is the same for this as the last file in outtypes
    if logic == 'exclusive':
        # match by name of drs_file
        cond = drs_file.name == alltypelist[-1].name
        # if condition not met return False and error
        if not cond:
            eargs = [argname, drs_file.name, alltypelist[-1].name]
            emsgs = ['Argument "{0}": File identified as "{1}"'.format(*eargs),
                     '\tHowever, previous files identified as "{2}"'
                     ''.format(*eargs),
                     '\tFiles must match (logic set to "exclusive")']
            return False, emsgs
        # if condition is met return True and empty error
        else:
            if DEBUG:
                dmsg = ('Argument "{0}": File exclusivity maintained. ("{1}"'
                        '== "{2}")')
                dargs = [argname, drs_file.name, alltypelist[-1].name]
                WLOG(params, '', dmsg.format(*dargs))
            return True, []

    # if logic is 'inclusive' we just need to return True
    if logic == 'inclusive':
        if DEBUG:
            dmsg = 'Argument "{0}": File logic is "inclusive" skipping check.'
            WLOG(params, '', dmsg.format(argname))
        return True, []
    # else logic is wrong
    else:
        emsgs = ['Dev Error: logic was wrong for argument "{0}"',
                 '\tMust be "exclusive" or "inclusive"']
        return False, emsgs


# =============================================================================
# Define run making functions
# =============================================================================
def _dir_file_filter(inputdir, infilelist):
    """
    Take an input directory "inputdir" and a file list "infilelist" and only
    keep those files that are within "inputdir" also extract the sub-directory
    tree for these files.

    :param inputdir: string, the input directory (root drs directory)
    :param infilelist: list of strings, the absolute paths of the files

    :return out_dict: dictionary, keys are the directory and values are the
                      valid input files in that directory (base filenames)
    """
    # define storage
    out_dict = OrderedDict()
    # loop around files
    for filename in infilelist:
        # remove those filenames that do not contain inputdir
        if inputdir not in filename:
            continue
        # for those that are left check that they exist
        if not os.path.exists(filename):
            continue
        # for those that exist get the directory name
        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        directory = dirname.split(inputdir)[-1]
        # make sure directory does not start with a separator
        while directory.startswith(os.sep):
            directory = directory[1:]
        # append outfilelist and outfdict
        if directory not in out_dict:
            out_dict[directory] = [basename]
        else:
            out_dict[directory].append(basename)
    # return all outputs
    return out_dict


def _get_index_files(recipe, inputdir, outudirlist):
    """
    From a list of directories "outudirlist" and an input directory root
    "inputdir" find all the current "INDEX_FILE" files, if they don't exist
    then put the entry to None

    :param inputdir: string, the root input directory
    :param outudirlist: list of strings, the unique directories (night name)

    :return index_list: list of strings, the abs path to each index file. If
                        index file does not exist value is None
    """
    # get params from recipe
    params = recipe.drs_params
    # storage for index list
    index_list = []
    # loop around directories
    for directory in outudirlist:
        # construct the link to the index file
        abspath = os.path.join(inputdir, directory, INDEX_FILE)
        # test whether it exists
        if os.path.exists(abspath):
            if DEBUG:
                dmsg = 'Found index file at {0}'
                WLOG(params, '', dmsg.format(abspath))
            index_list.append(abspath)
        else:
            if DEBUG:
                dmsg = 'Index file not found at {0}'
                WLOG(params, '', dmsg.format(abspath))
            index_list.append(None)
    # return index_list
    return index_list


def _get_index_data(p, index_file, directory):
    """
    Get the index data from "index_file" in directory "directory"

    :param p: Parameter Dictionary (used for logging)
    :param index_file: string, the index_file (absolute path)
    :param directory: string, the directory (used for logging)
    :return:
    """
    # deal with no directory
    if index_file is None:
        wmsg = ('Warning. No index file for {0}. Please run '
                'off_listing on directory'.format(directory))
        WLOG(p, 'warning', wmsg)
        return None

    # load index file
    try:
        indexdata = Table.read(index_file)
    except Exception as e:
        emsg1 = 'Error opening index file: "{0}"'.format(directory)
        emsg2 = '\tError was {0}: {1}'.format(type(e), e)
        WLOG(p, 'error', [emsg1, emsg2])
        indexdata = None
    # return index data
    return indexdata


def _filter_index(p, index, filters=None):
    """
    Filters index by filters. Filters are expected to be in a dictionary format
    in the form:
        filters = {KEY1:[VALUE1, VALUE2], KEY2:[VALUE3]}

        where KEY1 and KEY2 are string and must be in index.colnames (the
        column values of index)

        where VALUE1, VALUE2 and VALUE3 are the values allowed for each key

    :param index: astropy.table, index table containing KEY1, KEY2, ... columns
                  to be masked by filters
    :param filters: dictionary, keys are columns in index, values are the
                    values allowed for that column

    :return index_masked: astropy.table, the masked index table (using filters)
    """
    # deal with no filters
    if filters is None:
        return index
    # define mask
    mask = np.ones(len(index), dtype=bool)
    # loop around filter sets
    for rkey in filters:
        # get key and values from filter set
        values = filters[rkey]
        # if rkey is in params use this value
        if rkey in p and 'KW_' in rkey.upper():
            key = p[rkey][0]
        else:
            key = str(rkey)
        # define a mask set
        mask_set = np.zeros(len(index), dtype=bool)
        # check we have key in index columns
        if key in index.colnames:
            # debug message
            if DEBUG:
                dmsg = 'Filtering by "{0}" for values "{1}"'
                WLOG(p, '', dmsg.format(key, ' or '.join(values)))
            # loop around allowed values for filter
            for value in values:
                mask_set |= (index[key] == value)
            # apply mask_set to full mask
            mask &= mask_set
    # finally apply mask to index
    return index[mask]


# =============================================================================
# Define worker functions
# =============================================================================
def _gen_header_errors(header_errors):
    # set up message storage
    emsgs = []
    # set up initial argname
    argname = ''

    # check if file passed (all header_errors are True) - skip if passed
    for drsfile in header_errors.keys():
        passed = True
        for key in header_errors[drsfile]:
            passed &= header_errors[drsfile][key][0]
        if passed:
            return []

    # loop around drs files in header_errors
    for drsfile in header_errors.keys():
        # get this iterations values in this drs_file
        header_error = header_errors[drsfile]
        # append this file
        emsgs.append(' - File is not a "{0}" file'.format(drsfile))
        # loop around keys in this drs_file
        for key in header_error:
            # get this iterations entry
            entry = header_error[key]
            # get the argname
            argname = entry[1]
            # construct error message
            emsg = '\t {0} = "{1}" (Required: {2})'
            eargs = [key, entry[3], entry[2]]
            if not entry[0]:
                emsgs.append(emsg.format(*eargs))
    if len(emsgs) > 0:
        emsg0 = ['{0} File could not be identified - incorrect '
                 'HEADER values:'.format(argname)]
    else:
        emsg0 = []

    return emsg0 + emsgs


def _get_uncommon_path(path1, path2):
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
    common = os.path.commonpath([path2, path1]) + os.sep
    return path1.split(common)[-1]


def _get_file_list(path, limit=None, ext=None, recursive=False,
                   dir_only=False, list_all=False):
    """
    Get a list of files in a path

    :param path: string, the path to search for files
    :param limit: int, the number of files to limit the search to (stops after
                  this number of files)
    :param ext: string, the extension to limit the file search to, if None
                does not filter by extension
    :param recursive: bool, if True searches sub-directories recursively
    :param dir_only: bool, if True only lists directories (not files)
    :param list_all: bool, if True overides the limit feature and lists all
                     directories/files

    :return file_list: list of strings, the files found with extension (if not
                       None, up to the number limit
    """
    # deal with no limit - set hard limit
    if limit is None:
        limit = HARD_DISPLAY_LIMIT
    if list_all:
        limit = np.inf
    # deal with extension
    if ext is None:
        ext = ''
    # set up file list storage
    file_list = []
    # set up test of limit being reached
    limit_reached = False
    # set up level
    levelsep = '\t'
    level = ''
    # walk through directories
    for root, dirs, files in os.walk(path):
        if len(file_list) > limit:
            file_list.append(level + '...')
            return file_list
        if not recursive and root != path:
            continue
        if len(files) > 0 and recursive:
            limit += 1
        if not dir_only:
            # add root to file list (minus path)
            if root != path:
                directory = _get_uncommon_path(root, path) + os.sep
                # count number of separators in directory
                num = directory.count(os.sep)
                level = levelsep * num
                # append to list
                file_list.append(level + directory)
            # add root to file list (minus path)
            for filename in files:
                filelevel = level + levelsep
                # skip "index.fits"
                if filename == 'index.fits':
                    continue
                # do not display all (if limit reached)
                if len(file_list) > limit:
                    file_list.append(filelevel + '...')
                    limit_reached = True
                    return file_list, limit_reached
                # do not display if extension is true
                if not filename.endswith(ext):
                    continue
                # add to file list
                file_list.append(filelevel + filename)
        elif len(files) > 0:
            # add root to file list (minus path)
            if root != path:
                directory = _get_uncommon_path(root, path) + os.sep
                # append to list
                file_list.append(level + levelsep + directory)

    # if empty list add none found
    if len(file_list) == 0:
        file_list = ['No valid files found.']
    # return file_list
    return file_list, limit_reached


def _get_arg(recipe, argname):
    """
    Find an argument in the DrsRecipes argument dictionary or if not found
    find argument in the DrsRecipes keyword argument dictionary or it not found
    at all return None

    :param recipe: DrsRecipe instance
    :param argname: string, the argument/keyword argument to look for

    :return: DrsArgument instance, the argument in DrsRecipe.args or
             DrsRecipe.kwargs
    """
    if argname in recipe.args:
        arg = recipe.args[argname]
    elif argname in recipe.kwargs:
        arg = recipe.kwargs[argname]
    else:
        arg = None
    # return arg
    return arg


def _get_exposure_set(nums, bad='skip'):
    """
    Take a set of number that are assumed to represent sequences and group
    the by sequence set
        i.e. if we have 1,2,3,4,1,2,3,1,1,1,2,3,4

        group as following: 1,2,2,2,3,3,3,4,5,6,6,6,6

    :param nums: list of int/str, it integers will group the numbers
                 else will ignore and set the group to -1 if bad="skip" or
                 creates a new group if bad="new"
    :param bad: string, either "skip" or "new" decides what to do if nums is
                invalid, if "skip" sets the group to -1, if "new" creates a new
                group (with just this num in)

    :return sequence_num: list of int, the group number (starts at 1) bad values
                          in "exp_nums" set to a value of -1 if bad="skip" or
                     creates a new group if bad="new"
    """
    # set iterables
    sequence, group = 1, 0
    # set storage
    group_numbers = []
    # loop around exposure numbers
    for num in nums:
        # test that exp_num is an integer, if it is not then value is bad
        if not str(num).isdigit():
            # if bad="skip" set to group -1 and continue to next one
            if bad == 'skip':
                group_numbers.append(-1)
            # else if bad="new" start new group
            else:
                group += 1
                group_numbers.append(group)
        else:
            num = int(num)
            # if number is less than or equal to n then set the
            #    value of sequence to 1, also add one to the group number
            #    --> we have a new group
            if num <= sequence:
                sequence, group = 1, group + 1
            # if number is larger then we set sequence to this value
            #    --> we are still in the same group
            else:
                sequence = num
            group_numbers.append(group)
    # return group number
    return group_numbers


def _get_file_groups(recipe, arg):
    """

    For a file argument of dtype "file"/"files" get the files/directories/
    dtypes/exposure set numbers and dates for each file and group by
    directory/dtype/exposure set

    Must have populated arg.value with recipe.get_file_arg first

    returns groups in format:

    groups = [group_files, group_dir, group_dtype, group_exp_set, group_dates]

    where group_files is the file set for each group
    where group_dir is the group directory
    where group_dtype is the group file data type
    where group_exp_set is the group exposure sequence number
    where group_dates is the date for each file in file set for

    :param recipe: DrsRecipe instance
    :param arg: DrsArgument instance for this DrsRecipe

    :return groups, list of lists (see above)
    """
    # get parameters
    params = recipe.drs_params
    # get number of arguments
    nargs = arg.props['nargs']
    # storage
    directories, filenames, dtypes = [], [], []
    exp_nums, nexps, dates = [], [], []
    # loop around files in arg and get lists of parameters
    for value in arg.value:
        directories.append(value.directory)
        filenames.append(value.index['FILENAME'])
        exp_nums.append(value.index[params['KW_CMPLTEXP'][0]])
        nexps.append(value.index[params['KW_NEXP'][0]])
        dates.append(value.index[params['KW_ACQTIME'][0]])
        # deal with separating out files by logic
        #   i..e if "exclusive" need to separate by value.name
        #        else we don't need to so set to "FILE"
        #        (i.e. all the same)
        if arg.filelogic == 'exclusive':
            dtypes.append(value.name)
        else:
            dtypes.append('FILE')
    # -------------------------------------------------------------------------
    # sort by dates (MJDATE)
    sortmask = np.argsort(dates)
    directories = np.array(directories)[sortmask]
    filenames = np.array(filenames)[sortmask]
    exp_nums = np.array(exp_nums)[sortmask]
    # nexps = np.array(nexps)[sortmask]
    dates = np.array(dates)[sortmask]
    dtypes = np.array(dtypes)[sortmask]

    # -------------------------------------------------------------------------
    # group by directory
    group_files, group_dir, group_dtype = [], [], []
    group_exp_set, group_dates = [], []
    for gdir in np.unique(directories):
        # mask directories
        dirmask = directories == gdir
        # skip if empty
        if np.sum(dirmask) == 0:
            continue
        # ---------------------------------------------------------------------
        # group by dtype
        for gdtype in np.unique(dtypes):
            # mask dypres
            typemask = dtypes == gdtype
            # skip if empty
            if np.sum(dirmask & typemask) == 0:
                continue
            # -----------------------------------------------------------------
            # group by exposure sets
            #     i.e. if we have: 1,2,3,4,1,2,3,1,1,1,2,3,4
            #      group as following: 1,2,2,2,3,3,3,4,5,6,6,6,6
            if arg.limit == 1:
                exp_sets = np.arange(1, len(exp_nums[dirmask & typemask]) + 1)
            else:
                exp_sets = _get_exposure_set(exp_nums[dirmask & typemask],
                                             bad='new')
            # -----------------------------------------------------------------
            # group by exposure set
            for gexp in np.unique(exp_sets):
                # mask exposure set
                expmask = exp_sets == gexp
                # if we have no entries continue
                if np.sum(expmask) == 0:
                    continue
                else:
                    files = filenames[dirmask & typemask][expmask]
                    gdate = dates[dirmask & typemask][expmask]
                # deal with only allowing 1 file per set (dtype=file)
                if nargs == 1:
                    if DEBUG:
                        dmsg = '\tOnly using last entry'
                        WLOG(params, '', dmsg)
                    files = np.array([files[-1]])
                    gdate = np.array([gdate[-1]])
                # add to groups (only if we have more than one file)
                if len(files) > 0:
                    if DEBUG:
                        dmsg = 'Adding {0} files to group ({1},{2},{3})'
                        dargs = [len(files), gdir, gdtype, gexp]
                        WLOG(params, '', dmsg.format(*dargs))
                    group_files.append(files)
                    group_dir.append(gdir)
                    group_dtype.append(gdtype)
                    group_exp_set.append(gexp)
                    group_dates.append(gdate)
    # return groups
    groups = [group_files, group_dir, group_dtype, group_exp_set, group_dates]
    return groups


def _get_version_info(p, green='', end=''):

    # get name
    if 'DRS_NAME' in p:
        name = p['DRS_NAME']
    else:
        name = p['program']
    # get version
    if 'DRS_VERSION' in p:
        version = p['DRS_VERSION']
    else:
        version = __version__
    # construct version info string
    imsgs = [green + '\tNAME: {0}'.format(name),
             green + '\tVERSION: {0}'.format(version) + end,
             green + '\tAUTHORS: {0}'.format(__author__) + end,
             green + '\tLAST UPDATED: {0}'.format(__date__) + end,
             green + '\tRELEASE STATUS: {0}'.format(__release__) + end]
    return imsgs


def _help_format(keys, helpstr, options=None):

    fmtstring = ''
    sep = 19
    maxsize = 60


    # construct key string and add to output
    keystr = ','.join(keys)
    fmtstring += keystr

    # construct options string
    if options is None:
        optionstr = ''
    else:
        options = np.array(options, dtype=str)
        optionstr = '{{{0}}}'.format(','.join(options))
    # add option string
    helpstr = ' '.join([optionstr, helpstr])

    # add help
    # Assume help string is a string with escape characters

    # first remove all escape characters
    for char in ['\n', '\t']:
        helpstr = helpstr.replace(char, '')

    # remove any double spaces
    while '  ' in helpstr:
        helpstr = helpstr.replace('  ', ' ')

    # split by max number of characters allowed
    if len(helpstr) > maxsize:
        helpstrs = _textwrap(helpstr, maxsize)
    else:
        helpstrs = [helpstr]

    # add start separation
    for hstr in helpstrs:
        fmtstring += '\n' +  ' '*sep + hstr

    # return formatted string
    return fmtstring


def _textwrap(input_string, length):
    # Modified version of this: https://stackoverflow.com/a/16430754
    new_string = []
    for s in input_string.split("\n"):
        if s == "":
            new_string.append('')
        wlen = 0
        line = []
        for dor in s.split():
            if wlen + len(dor) + 1 <= length:
                line.append(dor)
                wlen += len(dor) + 1
            else:
                new_string.append(" ".join(line))
                line = [dor]
                wlen = len(dor)
        if len(line):
            new_string.append(" ".join(line))

    # add a tab to all but first line
    new_string2 = [new_string[0]]
    for it in range(1, len(new_string)):
        new_string2.append('\t' + new_string[it])

    return new_string2


def _match_multi_arg_lists(recipe, args, arg_list, directories, file_dates):
    """
    Match multiple argument lists so we have the same number of matches as
    the argument which has the most files

    Only used when we have more than one set of file arguments

    Matches based on directory (Must match directory) then selects the closest
    file to the argument which has the most "file sets"

    :param recipe: DrsRecipe instance
    :param args: list of strings, the "file"/"files" arguments in "arg_list"
    :param arg_list: dictionary, the arg_list dictionary, contains the
                     different permutations of runs in form:

                     Arg1: [value1, value1, value2]
                     Arg2: [file set 2a, file set 2b, file set 2c]
                     Arg3: [file set 3a, file set 3b]

                     where Arg1 is a "non-file" argument (dtype)
                     where Arg2 and Arg3 are "file"/"files" argument (dtype)
                     where "file set" is a basename filename, a string
                         file in "directory"

    :param directories: dictionary, same layout as arg_list but instead of
                        "file set" we have "directory" for this file set
    :param file_dates: dictionary, same layour as arg_list but instead of
                        "file set" we have "date set" - a float date and time
                        for each file (i.e. MJDATE or UNIX time)

    :return arg_list: dictionary, updated "arg_list" from input. Now all
                      "file"/"files" arguments should match in length. If any
                      matches were not found a None will be in the place of
                      a string filename.
    :return number_of_runs: int, the number of runs found (i.e. the length
                      of "file sets" in the largest "file"/"files" argument
    """

    params = recipe.drs_params
    # push args into lists
    files, dirs, dates = [], [], []
    for file_arg in args:
        files.append(arg_list[file_arg])
        dirs.append(directories[file_arg])
        dates.append(file_dates[file_arg])

    # get the indices for args
    iargs = np.arange(0, len(args), dtype=int)
    # find largest list
    largest, largest_it = None, 0
    size = 0
    for it, arg in enumerate(args):
        if len(files[it]) > size:
            size = len(files[it])
            largest, largest_it = arg, it
    # get the other args to match
    other_index = list(iargs[:largest_it]) + list(iargs[largest_it + 1:])
    # set up storage
    new_files, new_dirs = dict(), dict()
    # loop around other args
    for it in other_index:
        # set up storage
        new_files[args[it]], new_dirs[args[it]] = [], []
        # set up other arrays
        other_dirs_arr = np.array(dirs[it])
        other_dates_arr = np.array(dates[it])
        # loop around the values in the largest argument
        for jt in range(len(files[largest_it])):
            # get this iterations values
            dir_jt = dirs[largest_it][jt]
            # can be a set of dates
            if len(dates[largest_it][jt]) > 1:
                date_jt = np.mean(dates[largest_it][jt])
            else:
                date_jt = dates[largest_it][jt]
            # get all matching directories
            dirmask = other_dirs_arr == dir_jt
            # deal with no matching directories
            if np.sum(dirmask) == 0:
                if DEBUG:
                    dmsg1 = 'Cannot identify closest file (No directory match)'
                    dmsg2 = 'Target = {0}    Choices = {1}'
                    dargs = [dir_jt, other_dirs_arr]
                    WLOG(params, 'warning', [dmsg1, dmsg2.format(*dargs)])
                new_files[args[it]].append(None)
                new_dirs[args[it]].append(None)
                continue
            # get files/dirs for mask (from lists of lists)
            mask_files, mask_dirs = [], []
            for kt in range(len(dirmask)):
                if dirmask[kt]:
                    mask_files.append(files[it][kt])
                    mask_dirs.append(dirs[it][kt])
            # if we have multiple files we want the closest in time
            diff_value = []
            for oda_i in other_dates_arr[dirmask]:
                diff_value.append(np.mean(oda_i) - date_jt)
            closest = np.argmin(abs(np.array(diff_value)))
            # select this files set and dir as the correct one
            new_files[args[it]].append(mask_files[closest])
            new_dirs[args[it]].append(mask_dirs[closest])

    # append back to arg_list
    for file_arg in list(new_files.keys()):
        arg_list[file_arg] = new_files[file_arg]
        directories[file_arg] = new_dirs[file_arg]

    # set arg_list directories to largest
    arg_list['directory'] = directories[largest]
    # set the number of runs
    number_of_runs = len(directories[largest])

    # return arg list and directories
    return arg_list, number_of_runs


def _make_dict_from_table(itable):
    """
    Make dictionary from table evaluating the values as float/integers or
    strings

    :param itable: row of astropy.table - one and only one value

    :return idict: dictionary, the dictionary equivalent of the itable row
                   instance, where column names are the keys and this rows
                   values are their values
    """
    ikeys = list(itable.colnames)
    ivalues = []
    # loop around values in list
    for value in list(itable):
        try:
            # if '.' in string assume it is a float
            if '.' in str(value):
                ivalues.append(float(value))
            # else assume it is an integer
            else:
                ivalues.append(int(value))
        except ValueError:
            # handle as string (striped of white spaces)
            ivalues.append(str(value).strip(' '))
    return dict(zip(ikeys, ivalues))


def _make_listing():
    """
    Make a custom special argument that lists the files in the given
    input directory
    :return props: dictionary for argparser
    """
    props = OrderedDict()
    props['name'] = '--listing'
    props['altnames'] = ['--list']
    props['action'] = _MakeListing
    props['nargs'] = 0
    props['help'] = ('Lists the night name directories in the input directory '
                     'if used without a "directory" argument or lists the '
                     'files in the given "directory" (if defined).'
                     'Only lists up to {0} files/directories'
                     ''.format(HARD_DISPLAY_LIMIT))
    return props


def _make_alllisting():
    props = OrderedDict()
    props['name'] = '--listingall'
    props['altnames'] = ['--listall']
    props['action'] = _MakeAllListing
    props['nargs'] = 0
    props['help'] = ('Lists ALL the night name directories in the input '
                     'directory if used without a "directory" argument or '
                     'lists the files in the given "directory" (if defined)')
    return props


def _make_debug():
    """
    Make a custom special argument that switches on debug mode (as it needs to
    be done as soon as possible)
    :return:
    """
    props = OrderedDict()
    props['name'] = '--debug'
    props['altnames'] = ['--d', '--verbose']
    props['action'] = _ActivateDebug
    props['nargs'] = '?'
    props['help'] = ('Activates debug mode (Advanced mode [INTEGER] value must '
                     'be an integer greater than 0, setting the debug level)')
    return props


def _make_version():
    """
    Make a custom special argument that lists the version number
    :return props: dictionary for argparser
    """
    props = OrderedDict()
    props['name'] = '--version'
    props['altnames'] = []
    props['action'] = _DisplayVersion
    props['nargs'] = 0
    props['help'] = 'Displays the current version of this recipe.'
    return props


def _make_info():
    """
    Make a custom special argument that lists a short version of the help
    :return props: dictionary for argparser
    """
    props = OrderedDict()
    props['name'] = '--info'
    props['altnames'] = ['--i', '--usage']
    props['action'] = _DisplayInfo
    props['nargs'] = 0
    props['help'] = 'Displays the short version of the help menu'
    return props


def _load_other_config_file(p, key, logthis=True, required=False):
    """
    Load a secondary configuration file from p[key] with wrapper to deal
    with ConfigErrors (pushed to WLOG)

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
                key: "key" defined in call

    :param key: string, the key in "p" storing the location of the secondary
                configuration file
    :param logthis: bool, if True loading of this config file is logged to
                    screen/log file
    :param required: bool, if required is True then the secondary config file
                     is required for the DRS to run and a ConfigError is raised
                     (program exit)

    :return p: parameter, dictionary, the updated parameter dictionary with
               the secondary configuration files loaded into it as key/value
               pairs
    """
    # try to load config file from file
    try:
        pp, lmsgs = spirouConfig.LoadConfigFromFile(p, key, required=required,
                                                    logthis=logthis)
    except spirouConfig.ConfigError as e:
        WLOG(p, e.level, e.message)
        pp, lmsgs = ParamDict(), []

    # log messages caught in loading config file
    if len(lmsgs) > 0:
        WLOG(p, '', lmsgs)
    # return parameter dictionary
    return pp


def _print_list_msg(parser, recipe, fulldir, dircond=False,
                    return_string=False, list_all=False):
    """
    Prints the listing message (using "get_file_list")

    :param parser: DrsArgumentParser instance
    :param recipe: DrsRecipe instance
    :param fulldir: string, the full "root" (top level) directory
    :param dircond: bool, if True only prints directories (passed to
                    get_file_list)
    :param return_string: bool, if True returns string output instead of
                          printing
    :param list_all: bool, if True overrides lmit (set by HARD_DISPLAY_LIMIT)
    :return:
    """

    # generate a file list
    filelist, limitreached = _get_file_list(fulldir, recursive=True,
                                            dir_only=dircond, list_all=list_all)
    # get parameterse from drs_params
    program = recipe.drs_params['RECIPE']
    # construct error message
    if return_string:
        green, end = '', ''
        yellow, blue = '', ''
    elif recipe.drs_params['COLOURED_LOG']:
        green, end = COLOR.GREEN1, COLOR.ENDC
        yellow, blue = COLOR.YELLOW1, COLOR.BLUE1
    else:
        green, end = COLOR.ENDC, COLOR.ENDC
        yellow, blue = COLOR.ENDC, COLOR.ENDC
    # get the argument list (for use below)
    largs = list(recipe.args.keys())
    strlargs = []
    for larg in largs:
        strlargs.append('"{0}"'.format(larg))
    # get the arguments to format "wmsg"
    wargs = [HARD_DISPLAY_LIMIT, fulldir, ' or '.join(strlargs[1:])]
    # deal with different usages (before directory defined and after)
    #   and with/without limit reached
    wmsgs = []
    if limitreached:
        if dircond:
            wmsgs.append('Possible inputs for "directory"')
            wmsgs.append('\t(displaying first {0} directories in '
                         'location="{1}")'.format(*wargs))
        else:
            wmsgs.append('Possible inputs for {2}'.format(*wargs))
            wmsgs.append('\t(displaying first {0} files in '
                         'directory="{1}")'.format(*wargs))
    else:
        if dircond:
            wmsgs.append('Possible inputs for: "directory"')
            wmsgs.append('\t(displaying all directories in '
                         'location="{1}")'.format(*wargs))
        else:
            wmsgs.append('Possible inputs for: {2}'.format(*wargs))
            wmsgs.append('\t(displaying all files in '
                         'directory="{1}")'.format(*wargs))
    # loop around files and add to list
    for filename in filelist:
        wmsgs.append('\t' + filename)

    # construct print error message (with usage help)
    pmsgs = ['']

    if not return_string:
        pmsgs.append(green + HEADER + end)
        pmsgs.append(green + ' Listing for: {0}.py'.format(program) + end)
        pmsgs.append(green + HEADER + end)
        imsgs = _get_version_info(recipe.drs_params, green, end)
        pmsgs += imsgs
        pmsgs.append('')
        pmsgs.append(blue + parser.format_usage() + end)
        pmsgs.append('')
    for wmsg in wmsgs:
        pmsgs.append(green + wmsg + end)
    # deal with returning/printing
    if return_string:
        return pmsgs
    else:
        for pmsg in pmsgs:
            print(pmsg)


# =============================================================================
# End of code
# =============================================================================
