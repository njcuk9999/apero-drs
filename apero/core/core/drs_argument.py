#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-02-04 at 16:40

@author: cook
"""
import argparse
from collections import OrderedDict
import copy
import glob
import numpy as np
import os
import sys
from typing import Any, IO, Dict, List, Tuple, Type, Union

from apero.base import base
from apero.base import drs_break
from apero.base import drs_exceptions
from apero.base import drs_misc
from apero.base import drs_text
from apero.core import constants
from apero import lang
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_database
from apero.io import drs_fits


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_argument.py'
__INSTRUMENT__ = 'None'
# Get version and author
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
display_func = drs_log.display_func
# get print colours
COLOR = drs_misc.Colors()
# get param dict
ParamDict = constants.ParamDict
# get DrsInputFile (for typing)
DrsInputFile = drs_file.DrsInputFile
# get index database
IndexDatabase = drs_database.IndexDatabase
# get the config error
ConfigError = drs_exceptions.ConfigError
ArgumentError = drs_exceptions.ArgumentError
DrsCodedException = drs_exceptions.DrsCodedException
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
HelpText = lang.core.drs_lang_text.HelpDict
# define display strings for types
STRTYPE = base.STRTYPE
NUMBER_TYPES = base.NUMBER_TYPES

# define complex typing for file return
ValidFileType = Tuple[List[Union[Any, str]],
                      List[Union[DrsInputFile, None]]]


# =============================================================================
# Define ArgParse Parser and Action classes
# =============================================================================
# Adapted from: https://stackoverflow.com/a/16942165
class DrsArgumentParser(argparse.ArgumentParser):
    # argparse.ArgumentParser cannot be pickled
    #   so cannot pickle DrsArgumentParser either

    def __init__(self, recipe: Any, indexdb: IndexDatabase, **kwargs):
        """
        Construct the Drs Argument parser

        :param recipe: Drs Recipe - the recipe class for these arguments
        :param kwargs: keyword arguments passed to argparse.ArgumentParser
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, 'DRSArgumentParser')
        # define the recipe
        self.recipe = recipe
        self.indexdb = indexdb
        # get the recipes parameter dictionary
        params = self.recipe.params
        # get the text dictionary
        self.textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # get the help dictionary
        self.helptext = HelpText(params['INSTRUMENT'], params['LANGUAGE'])
        # set up the arguments
        self.args = None
        # set up the sys.argv storage
        self.argv = None
        # set up the source of the args (either main or sys.argv when set)
        self.source = None
        # set up the name space
        self.namespace = None
        # run the argument parser (super)
        argparse.ArgumentParser.__init__(self, **kwargs)

    def parse_args(self, args: Union[None, list] = None,
                   namespace: argparse.Namespace = None) -> argparse.Namespace:
        """
        Parse the arguments (from sys.argv for args) and push them into a
        parameter - overrides class from argparser.Parser

        :param args: a list of string arguments (similar to output of sys.argv)
                     used to override arguments coming from sys.argv (default)
        :param namespace: argparse Namespace instance - parsed
        :return: a argparse Namespace instance with the arguments loaded in
                 (after checking) use  params = vars(return) to force into
                 a dictionary of key/value pairs
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, 'parse_args', __NAME__,
                         'DRSArgumentParser')
        # deal with no args passed (get from sys.argv)
        if args is None:
            # first arg is the recipe name
            self.args = sys.argv[1:]
            # set the source to sys.argv
            self.source = 'sys.argv'
        # if we have args passed store them
        else:
            # shallow copy of args
            self.args = args
            # set the source to recipe.main()
            self.source = self.recipe.name + '.main()'
        # overritten functionality
        args, argv = self.parse_known_args(self.args, namespace)
        # deal with argv being set
        if argv:
            self.error(self.textdict['09-001-00002'].format(' '.join(argv)))
        return args

    def error(self, message: str):
        """
        Prints a usage message incorporating the message to stderr and
        exits. (Overrides argparse.Parser.error

        raises an exit via WLOG error
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, 'error', __NAME__,
                         'DRSArgumentParser')
        # self.print_help(sys.stderr)
        # self.exit(2, '%s: error: %s\n' % (self.prog, message))
        # get parameterse from drs_params
        program = str(self.recipe.params['RECIPE'])
        # get parameters from drs_params
        params = self.recipe.params
        # log message
        emsg_args = [message, program]
        emsg_obj = TextEntry('09-001-00001', args=emsg_args)
        WLOG(params, 'error', emsg_obj)

    def _print_message(self, message: str, file: Union[None, IO] = None):
        """
        Custom help text displayed after an error occurs overrides
        functionality of argparse.Parser._print_message

        :param message: str, required for super but not used here
        :param file: file instance, required for super but not used here

        :return: None
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_print_message', __NAME__,
                         'DRSArgumentParser')
        # get parameters from drs_params
        params = self.recipe.params
        program = str(params['RECIPE'])
        # construct error message
        if self.recipe.params['DRS_COLOURED_LOG']:
            green, end = COLOR.GREEN1, COLOR.ENDC
            yellow, blue = COLOR.YELLOW1, COLOR.BLUE1
        else:
            green, end = COLOR.ENDC, COLOR.ENDC
            yellow, blue = COLOR.ENDC, COLOR.ENDC
        # Manually print error message (with help text)
        print()
        print(green + params['DRS_HEADER'] + end)
        helptitletext = self.textdict['40-002-00001'].format(program)
        print(green + ' ' + helptitletext + end)
        print(green + params['DRS_HEADER'] + end)
        imsgs = _get_version_info(self.recipe.params, green, end)
        for imsg in imsgs:
            print(imsg)
        print()
        print(blue + self.format_help() + end)

    def format_usage(self) -> str:
        """
        Set how to use this recipe based on arguments added (overrides
        argparse.Parser.format_usage)

        :return: string representation of the usage for printing
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, 'format_usage', __NAME__,
                         'DRSArgumentParser')
        # noinspection PyProtectedMember
        return_string = (' ' + self.helptext['USAGE_TEXT'] + ' ' +
                         self.recipe._drs_usage())
        # return messages
        return return_string

    def format_help(self) -> str:
        """
        Generates the string used for the help menu (used from the --help or -h
        argument)

        :return: str, the help string to display
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, 'format_help', __NAME__,
                         'DRSArgumentParser')
        # empty help message at intialization
        hmsgs = []
        # noinspection PyProtectedMember
        hmsgs += [' ' + self.helptext['USAGE_TEXT'] + ' ' +
                  self.recipe._drs_usage()]
        # add description
        if self.recipe.description is not None:
            # add header line
            hmsgs += ['', self.recipe.params['DRS_HEADER']]
            # add description title
            hmsgs += [' ' + self.helptext['DESCRIPTION_TEXT']]
            # add header line
            hmsgs += [self.recipe.params['DRS_HEADER'], '']
            # add description text
            hmsgs += [' ' + self.recipe.description]
            # add header line
            hmsgs += [self.recipe.params['DRS_HEADER']]
        # deal with required (positional) arguments
        hmsgs += ['', self.textdict['40-002-00002'], '']
        # loop around each required (positional) arguments
        for arg in self.recipe.required_args:
            # add to help message list
            hmsgs.append(_help_format(arg.names, arg.helpstr, arg.options))
        # deal with optional arguments
        hmsgs += ['', '', self.textdict['40-002-00003'], '']
        # loop around each optional argument
        for arg in self.recipe.optional_args:
            # add to help message list
            hmsgs.append(_help_format(arg.names, arg.helpstr, arg.options))
        # deal with special arguments
        hmsgs += ['', '', self.textdict['40-002-00004'], '']
        # loop around each special argument
        for arg in self.recipe.special_args:
            # add to help mesasge list
            hmsgs.append(_help_format(arg.names, arg.helpstr, arg.options))
        # add help
        helpstr = self.textdict['40-002-00005']
        hmsgs.append(_help_format(['--help', '-h'], helpstr))
        # add epilog
        if self.recipe.epilog is not None:
            hmsgs += ['', self.recipe.params['DRS_HEADER']]
            hmsgs += [' ' + self.helptext['EXAMPLES_TEXT']]
            hmsgs += [self.recipe.params['DRS_HEADER'], '']
            hmsgs += [' ' + self.recipe.epilog]
            hmsgs += [self.recipe.params['DRS_HEADER']]
        # return string
        return_string = ''
        for hmsg in hmsgs:
            return_string += hmsg + '\n'

        # return messages
        return return_string

    def _has_special(self) -> bool:
        """
        Deals with (1) when -h and --help are triggered --> print help and then
        exit elsewise finds whether recipe has special arguments definited

        :return: If recipe has special arguments returns True, else returns
                 false
        :raises: _sys.exit if -h or --help in sys.argv
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_has_special', __NAME__,
                         'DRSArgumentParser')
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
        # if we have reached this point we do not have a special argument
        return False


class DrsAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        """
        Construct the base DrsAction class (Abstract should not be used)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = 'DrsAction'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # run the argument parser (super)
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Define an Abstract call to Action (required for overwriting)
        Should call setattr(namespace, destination, value) to set
        destination = value  in the namespace

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to use to set destination
        :param option_string: None in most cases but used to get options
                              for testing the value if required

        :return: None
        """
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(None, '__call__', __NAME__, self.class_name)
        # raise not implemented error
        raise NotImplementedError('{0} not defined'.format(func_name))


class _CheckDirectory(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Check Directory action (for checking a directory argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set the class name
        self.class_name = '_CheckDirectory'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # set the recipe and parser to None
        self.recipe = kwargs.get('recipe', None)
        self.indexdb = kwargs.get('indexdb', None)
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_CheckDirectory[DrsAction]'

    def _check_directory(self, value: Any) -> str:
        """
        Check the value of the directory is valid - raise exception if not
        valid, else return the value

        :param value: Any, the value to test whether valid for directory
        argument

        :return: str: the valid directory (raises exception if invalid)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_check_directory', __NAME__,
                         self.class_name)
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return value
        # ---------------------------------------------------------------------
        # get the argument name
        argname = self.dest
        # get the params from recipe
        params = self.recipe.params
        # debug checking output
        if params['DRS_DEBUG'] > 0:
            print('')
        WLOG(params, 'debug', TextEntry('90-001-00018', args=[argname]))
        # check whether we have a valid directory
        directory = valid_directory(params, self.indexdb, argname, value,
                                    kind=self.recipe.inputtype,
                                    forced_dir=self.recipe.inputdir)
        # if we have found directory return directory
        return directory


    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _CheckDirectory() - sets the _CheckDirectory.dest
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        self.indexdb = parser.indexdb
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        if type(values) == list:
            value = list(map(self._check_directory, values))[0]
        else:
            value = self._check_directory(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _CheckFiles(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Check Files action (for checking a files argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set the class name
        self.class_name = '_CheckFiles'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # get the recipe, namespace and directory (if not added set to None)
        self.recipe = kwargs.get('recipe', None)
        self.indexdb = kwargs.get('indexdb', None)
        self.namespace = kwargs.get('namespace', None)
        self.directory = kwargs.get('directory', None)
        self.parser = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = ['parser']
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__:
            if key not in exclude:
                state[key] = item
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
        # set parser to None (Is this a problem?)
        self.parser = None

    def __str__(self) -> str:
        """
        String representation of this class
        :return:
        """
        return '_CheckFiles[DrsAction]'

    def _check_files(self, value: Any) -> ValidFileType:
        """
        Check the values of the files are valid - raise exception if not
        valid, else return the value

        :param value: Any, the value to test whether a valid file/files

        :return: the valid filename and its DrsFile instance
                 (raises exception if invalid)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_check_files', __NAME__,
                         self.class_name)
        # ---------------------------------------------------------------------
        # deal with single string -> list of strings
        if isinstance(value, str):
            values = [value]
        # else push into a list of strings
        else:
            values = list(map(lambda x: str(x), value))
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return values, [None] * len(values)
        # ---------------------------------------------------------------------
        # check if "directory" is in namespace
        if self.directory is not None:
            directory = self.directory
        else:
            directory = getattr(self.namespace, 'directory', '')
        # get the argument name
        argname = self.dest
        # get the params from recipe
        params = self.recipe.params
        # debug checking output
        WLOG(params, 'debug', TextEntry('90-001-00019', args=[argname]))
        # get recipe args and kwargs
        rargs = self.recipe.args
        rkwargs = self.recipe.kwargs
        input_type = self.recipe.inputtype
        input_dir = self.recipe.inputdir
        # ---------------------------------------------------------------------
        # storage of files and types
        files, types = [], []
        # loop around files
        for _value in values:
            # get the filename if valid (else crash)
            out = valid_file(params, self.indexdb, input_type, argname, _value,
                              rargs, rkwargs, directory, types, input_dir)
            # append to storage
            files += out[0]
            types += out[1]
        # if they are return files
        return files, types


    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _CheckFiles() - sets the _CheckFiles.dest
        to value if valid else raises exception

        _CheckFiles.dest = [filename, DrsFile instance]

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        self.indexdb = parser.indexdb
        self.parser = parser
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # store the namespace
        self.namespace = namespace
        # check for help
        # noinspection PyProtectedMember
        skip = parser._has_special()
        if skip:
            return 0
        # check values and return a list of files and file types
        files, types = self._check_files(values)
        # Add the attribute
        setattr(namespace, self.dest, [files, types])


class _CheckBool(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Check Boolean action (for checking a boolean argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_CheckBool'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_CheckBool')
        # define recipe as unset
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_CheckBool[DrsAction]'

    def _check_bool(self, value) -> bool:
        """
        Check the value of the boolean is valid - raise exception if not
        valid, else return the value

        Casts to string and accepts 'yes', 'true', 't', 'y', '1' as True
        Casts to string and accepts 'no', 'false', 'f', 'n', '0' as False
        with an upper/lower character cases

        :param value: Any, the value to test whether valid for directory
        argument

        :return: bool, the proper type casted value
                 (raises exception if invalid for a boolean)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_check_bool', __NAME__,
                         '_CheckBool')
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return value
        # ---------------------------------------------------------------------
        # get parameters
        params = self.recipe.params
        # get the argument name
        argname = self.dest
        # debug progress
        WLOG(params, 'debug', TextEntry('90-001-00020', args=[argname]),
             wrap=False)
        # conditions
        if str(value).lower() in ['yes', 'true', 't', 'y', '1']:
            # debug print
            dargs = [argname, value, 'True']
            dmsg = TextEntry('90-001-00021', args=dargs)
            dmsg += TextEntry('')
            WLOG(params, 'debug', dmsg, wrap=False)
            return True
        elif str(value).lower() in ['no', 'false', 'f', 'n', '0']:
            # debug print
            dargs = [argname, value, 'False']
            dmsg = TextEntry('90-001-00021', args=dargs)
            dmsg += TextEntry('')
            WLOG(params, 'debug', dmsg, wrap=False)
            return False
        else:
            eargs = [self.dest, value]
            WLOG(params, 'error', TextEntry('09-001-00013', args=eargs))

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _CheckBool() - sets the _CheckBool.dest
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check boolean argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         '_CheckBool')
        # check for help
        # noinspection PyProtectedMember
        skip = parser._has_special()
        if skip:
            return 0
        if type(values) == list:
            value = list(map(self._check_bool, values))
        else:
            value = self._check_bool(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _CheckType(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Check Type action (for checking a type argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_CheckType'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        # set parser to None (Is this a problem?)
        self.parser = None

    def __str__(self) -> str:
        """
        String representation of this class
        :return:
        """
        return '_CheckType[DrsAction]'

    def _check_type(self, value: Any) -> Any:
        """
        Check the value of the type is valid - raise exception if not
        valid, else return the value

        :param value: Any, the value to test whether valid for directory
        argument

        :return: Any, based on the type required (raises exception if invalid)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_check_type', __NAME__,
                         self.class_name)
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return value
        # ---------------------------------------------------------------------
        # get parameters
        params = self.recipe.params
        # check that type matches
        if type(value) is self.type:
            return value
        # check if passed as a list
        if (self.nargs == 1) and (type(value) is list):
            if len(value) == 0:
                emsg = TextEntry('09-001-00016', args=[self.dest])
                WLOG(params, 'error', emsg)
            else:
                return self._eval_type(value[0])
        # else if we have a list we should iterate
        elif type(value) is list:
            values = []
            for it in self.nargs:
                values.append(self._eval_type(values[it]))
            if len(values) < len(value):
                eargs = [self.dest, self.nargs, len(value)]
                WLOG(params, 'error', TextEntry('09-001-00017', args=eargs))
            return values
        # else
        else:
            eargs = [self.dest, self.nargs, type(value), value]
            WLOG(params, 'error', TextEntry('09-001-00018', args=eargs))

    def _eval_type(self, value: Any) -> Any:
        """
        Try to cast the value into self.type

        :param value: Any, value to try to change to self.type
        :return: Any, the value type-casted into self.type type
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_eval_type', __NAME__,
                         self.class_name)
        # get parameters
        params = self.recipe.params
        # get type error
        eargs = [self.dest, value, self.type]
        try:
            return self.type(value)
        except ValueError as _:
            WLOG(params, 'error', TextEntry('09-001-00014', args=eargs))
        except TypeError as _:
            WLOG(params, 'error', TextEntry('09-001-00015', args=eargs))

    def _check_limits(self, values: Any) -> Union[List[Any], Any]:
        """
        Checks the limits (maximum and minimum) of a value or set of values
        (maximum and minimum obtained from Argument definition)

        :param values: Any, the input values to test
        :return: Any, the same values as input (unless outside max and/or min)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.params, '_check_type',
                                 __NAME__, self.class_name)
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return values
        # ---------------------------------------------------------------------
        # get parameters
        params = self.recipe.params
        # get the argument name
        argname = self.dest
        # ---------------------------------------------------------------------
        # find argument
        if argname in self.recipe.args:
            arg = self.recipe.args[argname]
        elif argname in self.recipe.kwargs:
            arg = self.recipe.kwargs[argname]
        elif argname in self.recipe.special_args:
            arg = self.recipe.special_args[argname]
        else:
            eargs = [argname, func_name]
            WLOG(params, 'error', TextEntry('00-006-00011', args=eargs))
            arg = None
        # ---------------------------------------------------------------------
        # skip this step if minimum/maximum are both None
        if arg.minimum is None and arg.maximum is None:
            return values
        if arg.dtype not in NUMBER_TYPES:
            return values
        # ---------------------------------------------------------------------
        # make sure we have a list
        if type(values) not in [list, np.ndarray]:
            is_list = False
            values = [values]
        else:
            is_list = True
        # ---------------------------------------------------------------------
        # get the minimum and maximum values
        minimum, maximum = arg.minimum, arg.maximum
        # make sure we can push values to required dtype (unless None)
        if minimum is not None:
            try:
                minimum = arg.dtype(minimum)
            except ValueError as e:
                eargs = [argname, 'minimum', minimum, type(e), e]
                WLOG(params, 'error', TextEntry('00-006-00012', args=eargs))
        if maximum is not None:
            try:
                maximum = arg.dtype(maximum)
            except ValueError as e:
                eargs = [argname, 'maximum', maximum, type(e), e]
                WLOG(params, 'error', TextEntry('00-006-00012', args=eargs))
        # ---------------------------------------------------------------------
        # loop round files and check values
        for value in values:
            # deal with case where minimum and maximum should be checked
            if minimum is not None and maximum is not None:
                if (value < minimum) or (value > maximum):
                    eargs = [argname, value, minimum, maximum]
                    emsg = TextEntry('09-001-00029', args=eargs)
                    WLOG(params, 'error', emsg)
            # deal with case where just minimum is checked
            elif minimum is not None:
                if value < minimum:
                    eargs = [argname, value, minimum]
                    emsg = TextEntry('09-001-00027', args=eargs)
                    WLOG(params, 'error', emsg)
            # deal with case where just maximum is checked
            elif maximum is not None:
                if value > maximum:
                    eargs = [argname, value, maximum]
                    emsg = TextEntry('09-001-00028', args=eargs)
                    WLOG(params, 'error', emsg)
        # ---------------------------------------------------------------------
        # return (based on whether it is a list or not)
        if is_list:
            return values
        else:
            return values[0]

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _CheckType() - sets the _CheckType.dest
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_check_type', __NAME__,
                         self.class_name)
        # check for help
        # noinspection PyProtectedMember
        skip = parser._has_special()
        if skip:
            return 0
        if self.nargs == 1:
            value = self._check_type(values)
        elif type(values) == list:
            value = list(map(self._check_type, values))
        else:
            value = self._check_type(values)
        # check the limits are correct
        value = self._check_limits(value)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _CheckOptions(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Check Options action (for checking a options argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_CheckOptions')
        # define recipe as None (overwritten by __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_CheckOptions[DrsAction]'

    def _check_options(self, value: Any) -> Any:
        """
        Check the value of the options are valid - raise exception if not
        valid, else return the value

        :param value: Any, the value to test whether valid for directory
        argument

        :return: str: the valid directory (raises exception if invalid)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_check_options', __NAME__,
                         '_CheckOptions')
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return value
        # ---------------------------------------------------------------------
        # get parameters
        params = self.recipe.params
        # check options
        if value in self.choices:
            return value
        else:
            eargs = [self.dest, ' or '.join(self.choices), value]
            WLOG(params, 'error', TextEntry('09-001-00019', args=eargs))

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _CheckOptions() - sets the _CheckOptions.dest
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         '_CheckOptions')
        # check for help
        # noinspection PyProtectedMember
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
class _MakeListing(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Make Listing action (for checking a directory argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_MakeListing'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_MakeListing')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # define name space as None (overwritten in __call__)
        self.namespace = None
        # define parser as None (overwritten in __call__)
        self.parser = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = ['parser']
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__:
            if key not in exclude:
                state[key] = item
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
        # set parser to None (Is this a problem?)
        self.parser = None

    def __str__(self) -> str:
        """
        String representation of this class
        :return:
        """
        return '_MakeListing[DrsAction]'

    def _display_listing(self, namespace: argparse.Namespace):
        """
        Display the listing for an input_dir and directory
        (taken from namespace)

        :return: str: the valid directory (raises exception if invalid)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_display_listing', __NAME__,
                         self.class_name)
        # get input dir
        # noinspection PyProtectedMember
        input_dir = self.recipe.get_input_dir()
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
        _print_list_msg(self.recipe, fulldir, dircond, list_all=False)

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _MakeListing() - displays a directory listing
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # store parser
        self.parser = parser
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display listing
        self._display_listing(namespace)
        # quit after call
        parser.exit()


class _MakeAllListing(DrsAction):
    """
    Construct the Make All Listings action (for checking a directory argument)

    :param args: arguments passed to argparse.Action.__init__
    :param kwargs: keyword arguments passed to argparse.Action.__init__
    """
    def __init__(self, *args, **kwargs):
        # set class name
        self.class_name = '_MakeAllListing'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # define name space as None (overwritten in __call__)
        self.namespace = None
        # define parse as None (overwritten in __call__)
        self.parser = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # what to exclude from state
        exclude = ['parser']
        # need a dictionary for pickle
        state = dict()
        for key, item in self.__dict__:
            if key not in exclude:
                state[key] = item
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
        # set parser to None (Is this a problem?)
        self.parser = None

    def __str__(self) -> str:
        """
        String representation of this class
        :return:
        """
        return '_MakeListing[DrsAction]'

    def _display_listing(self, namespace: argparse.Namespace):
        """
        Display the listing for an input_dir and directory
        (taken from namespace)

        :return: str: the valid directory (raises exception if invalid)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_display_listing', __NAME__,
                         self.class_name)
        # get input dir
        # noinspection PyProtectedMember
        input_dir = self.recipe.get_input_dir()
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
        _print_list_msg(self.recipe, fulldir, dircond, list_all=True)

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _MakeAllListing() - displays all directory listings
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         '_MakeAllListing')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # store parser
        self.parser = parser
        # display listing
        self._display_listing(namespace)
        # quit after call
        parser.exit()


class _ActivateDebug(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Activate Debug action (for activating debug mode)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_ActivateDebug'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set state to __dict__
        state = dict(self.__dict__)
        # return dictionary state (for pickle)
        return state

    def __setstate__(self, state: dict):
        """
        For when we have to unpickle the class

        :param state: dictionary from pickle
        :return:
        """
        # update dict with state
        self.__dict__.update(state)
        # set parser to None (Is this a problem?)
        self.parser = None

    def __str__(self) -> str:
        """
        String representation of this class
        :return:
        """
        return '_ActivateDebug[DrsAction]'

    def _set_debug(self, values: Any) -> int:
        """
        Set the debug mode based on value

        :param values: Any value to ttest whether it is a debug mode
        :return: int, the debug mode found
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_set_debug', __NAME__,
                         self.class_name)
        # get params
        params = self.recipe.params
        # deal with a value of None
        if values is None:
            return 1
        # test value
        # noinspection PyPep8,PyBroadException
        try:
            # only take first value (if a list)
            if type(values) != str and hasattr(values, '__len__'):
                values = values[0]
            # try to make an integer
            value = int(values)
            # set DRS_DEBUG (must use the self version)
            self.recipe.params.set('DRS_DEBUG', value)
            # return value
            return value
        except drs_exceptions.DrsCodedException as e:
            WLOG(params, 'error', TextEntry(e.codeid, args=e.targs))
        except Exception as _:
            eargs = [self.dest, values]
            WLOG(params, 'error', TextEntry('09-001-00020', args=eargs))

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _ActivateDebug() - sets the debug mode
        to value else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # display listing
        if type(values) == list:
            value = list(map(self._set_debug, values))
        else:
            value = self._set_debug(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _ForceInputDir(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Force Input Directory action (for forcing the input
        directory to a user argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        self.class_name = '_ForceInputDir'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_ForceInputDir[DrsAction]'

    def _force_input_dir(self, values: Any) -> Union[str, None]:
        """
        If value is a valid string sets _ForceInputDir.dest to the string
        representation of values[0] if list or otherwise = values
        raises exception if cannot convert to string

        :param values: Any, the value(s) to be converted to a string
        :return: None or str, if value can go to a string and is not None
                 returns string representation of values[0] if list or values
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_force_input_dir', __NAME__,
                         self.class_name)
        # get params
        params = self.recipe.params
        # deal with value of None
        if values is None:
            return None
        # test value
        # noinspection PyPep8,PyBroadException
        try:
            # only take first value (if a list)
            if type(values) != str and hasattr(values, '__len__'):
                values = values[0]
            # try to make an string
            value = str(values)
            # return value
            return value
        except Exception as _:
            eargs = [self.dest, values]
            WLOG(params, 'error', TextEntry('09-001-00020', args=eargs))

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _ForceInputDir() - sets the _ForceInputDir.dest
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check boolean argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # display listing
        if type(values) == list:
            value = list(map(self._force_input_dir, values))[0]
        else:
            value = self._force_input_dir(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _ForceOutputDir(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Force Input Directory action (for forcing the output
        directory to a user argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_ForceOutputDir'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_ForceOutputDir[DrsAction]'

    def _force_output_dir(self, values: Any) -> Union[str, None]:
        """
        If value is a valid string sets _ForceOutputDir.dest to the string
        representation of values[0] if list or otherwise = values
        raises exception if cannot convert to string

        :param values: Any, the value(s) to be converted to a string
        :return: None or str, if value can go to a string and is not None
                 returns string representation of values[0] if list or values
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_force_output_dir', __NAME__,
                         '_ForceOutputDir')
        # get params
        params = self.recipe.params
        # deal with None value
        if values is None:
            return None
        # test value
        # noinspection PyPep8,PyBroadException
        try:
            # only take first value (if a list)
            if type(values) != str and hasattr(values, '__len__'):
                values = values[0]
            # try to make an string
            value = str(values)
            # return value
            return value
        except Exception as _:
            eargs = [self.dest, values]
            WLOG(params, 'error', TextEntry('09-001-00020', args=eargs))

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _ForceOutputDir() - sets the _ForceOutputDir.dest
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check boolean argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         '_ForceOutputDir')
        # display listing
        if type(values) == list:
            value = list(map(self._force_output_dir, values))[0]
        else:
            value = self._force_output_dir(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _DisplayVersion(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Display Version action (for display version number)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_DisplayVersion'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_DisplayVersion[DrsAction]'

    def _display_version(self):
        """
        Display the version info print out
        :return:
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_display_version', __NAME__,
                         self.class_name)
        # get params
        params = self.recipe.params
        # get colours
        if params['DRS_COLOURED_LOG']:
            green, end = COLOR.GREEN1, COLOR.ENDC
        else:
            green, end = COLOR.ENDC, COLOR.ENDC
        # print start header
        print(green + params['DRS_HEADER'] + end)
        # print version info message
        imsgs = _get_version_info(params, green, end)
        for imsg in imsgs:
            print(imsg)
        # end header
        print(green + params['DRS_HEADER'] + end)

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _DisplayVersion() - display the version info

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check boolean argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        """
        # set recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()

        # display version
        self._display_version()
        # quit after call
        parser.exit()


class _DisplayInfo(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Display Info action (for display version number)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_DisplayInfo'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_DisplayInfo[DrsAction]'

    def _display_info(self):
        """
        Display the info print out
        :return:
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_display_info', __NAME__,
                         self.class_name)
        # get params
        recipe = self.recipe
        params = recipe.params
        etext = recipe.textdict
        htext = recipe.helptext
        program = str(params['RECIPE'])
        # get colours
        if params['DRS_COLOURED_LOG']:
            green, end = COLOR.GREEN1, COLOR.ENDC
            yellow, blue = COLOR.YELLOW1, COLOR.BLUE1
        else:
            green, end = COLOR.ENDC, COLOR.ENDC
            yellow, blue = COLOR.ENDC, COLOR.ENDC
        # print usage
        print(green + params['DRS_HEADER'] + end)
        print(green + etext['40-002-00006'].format(program + '.py') + end)
        print(green + params['DRS_HEADER'] + end)
        # print version info message
        imsgs = _get_version_info(params, green, end)
        for imsg in imsgs:
            print(imsg)
        print()
        # noinspection PyProtectedMember
        print(blue + ' ' + etext['40-002-00007'] + recipe._drs_usage() + end)
        # print description
        print()
        print(blue + params['DRS_HEADER'] + end)
        print(blue + ' ' + htext['DESCRIPTION_TEXT'] + end)
        print(blue + params['DRS_HEADER'] + end)
        print()
        print(blue + ' ' + recipe.description + end)
        # print examples
        print()
        print(blue + params['DRS_HEADER'] + end)
        print(blue + ' ' + htext['EXAMPLES_TEXT'] + end)
        print(blue + params['DRS_HEADER'] + end)
        print()
        print(blue + ' ' + recipe.epilog + end)
        print(blue + params['DRS_HEADER'] + end)
        # print see help
        print(green + etext['40-002-00008'] + end)
        print()
        # end header
        print(green + params['DRS_HEADER'] + end)

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _DisplayInfo() - display the info print out

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check boolean argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        """
        # set recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         '_DisplayInfo')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        self._display_info()
        # quit after call
        parser.exit()


class _SetProgram(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Set Program action (for setting the drs program from an
        argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_SetProgram'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_SetProgram[DrsAction]'

    def _set_program(self, values: Any) -> str:
        """
        Set the program name from the values (if we can convert to a string)
        elsewise raise an error

        :param values: Any, the value to set the program name to
        :return: str, the string representation of values (for program name)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.params, '_set_program',
                                 __NAME__, self.class_name)
        # deal with difference datatypes for values
        if isinstance(values, list):
            strvalue = values[0]
        elif isinstance(values, np.ndarray):
            strvalue = values[0]
        else:
            strvalue = str(values)
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00031', args=[strvalue])
        WLOG(self.recipe.params, 'debug', dmsg)
        # set DRS_DEBUG (must use the self version)
        self.recipe.params['DRS_USER_PROGRAM'] = strvalue
        self.recipe.params.set_source('DRS_USER_PROGRAM', func_name)
        self.recipe.params.set_instance('DRS_USER_PROGRAM', None)
        # return strvalue
        return strvalue

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _SetProgram() - sets the drs program name
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check boolean argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_program(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _SetIPythonReturn(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Set IPython Return action (for setting IPYTHON_RETURN)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_SetIPythonReturn'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_SetIPythonReturn[DrsAction]'

    def _set_return(self) -> True:
        """
        Set the IPYTHON_RETURN value to True if argument is present

        :return: True and params['IPYTHON_RETURN'] = True
        """
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.params, '_set_return',
                                 __NAME__, self.class_name)
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00032')
        WLOG(self.recipe.params, 'debug', dmsg)
        # set DRS_DEBUG (must use the self version)
        self.recipe.params['IPYTHON_RETURN'] = True
        self.recipe.params.set_source('IPYTHON_RETURN', func_name)
        self.recipe.params.set_instance('IPYTHON_RETURN', None)
        # return strvalue
        return True

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _SetIPythonReturn() - sets the _SetIPythonReturn.dest
        to True if argument is present

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        """
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_return()
        # Add the attribute
        setattr(namespace, self.dest, value)


class _Breakpoints(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Breakpoints action (for activating break points with
        argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_Breakpoints'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_Breakpoints[DrsAction]'

    def _set_return(self) -> True:
        """
        Set the ALLOW_BREAKPOINTS value to True if argument is present

        :return: True and params['ALLOW_BREAKPOINTS'] = True
        """
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.params, '_set_return',
                                 __NAME__, self.class_name)
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00033')
        WLOG(self.recipe.params, 'debug', dmsg)
        # set DRS_DEBUG (must use the self version)
        self.recipe.params['ALLOW_BREAKPOINTS'] = True
        self.recipe.params.set_source('ALLOW_BREAKPOINTS', func_name)
        self.recipe.params.set_instance('ALLOW_BREAKPOINTS', None)
        # return strvalue
        return True

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _Breakpoints() - sets the _Breakpoints.dest
        to True if argument is present

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        """
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         '_Breakpoints')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_return()
        # Add the attribute
        setattr(namespace, self.dest, value)


class _Breakfunc(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Break at Function action (for breaking at a display
        function)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_Breakfunc'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_Breakfunc')
        # set recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_Breakfunc[DrsAction]'

    def _set_breakfunc(self, value: Any) -> Union[None, str]:
        """
        Set the breakfunction value to the string representation of "value"

        :param value: Any, value to turn to string representation of value

        :return: str: the valid directory (raises exception if invalid)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_set_breakfunc',
                         __NAME__, self.class_name)
        # deal with unset value
        if value is None:
            return None
        else:
            return str(value)

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _Breakfunc() - sets the _Breakfunc.dest
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # display listing
        if type(values) == list:
            value = list(map(self._set_breakfunc, values))
        else:
            value = self._set_breakfunc(values)
        # make sure value is not a list
        if isinstance(value, list):
            value = value[0]
        # Add the attribute
        setattr(namespace, self.dest, value)


class _IsMaster(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Is Master action (for setting a recipe to a master
        via an argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_IsMaster'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # set recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_IsMaster[DrsAction]'

    def _set_master(self, value: Any) -> Union[str, None]:
        """
        Sets the master value to string representation of value

        :param value: Any, value to turn to string representation of value

        :return: str: the valid directory (raises exception if invalid)
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_set_master',
                         __NAME__, self.class_name)
        # deal with unset value
        if value is None:
            return None
        else:
            return str(value)

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _IsMaster() - sets the _IsMaster.dest
        to value if valid else raises exception

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__',
                         __NAME__, self.class_name)
        # display listing
        if type(values) == list:
            value = list(map(self._set_master, values))
        else:
            value = self._set_master(values)
        # make sure value is not a list
        if isinstance(value, list):
            value = value[0]
        # Add the attribute
        setattr(namespace, self.dest, value)


class _SetQuiet(DrsAction):
    def __init__(self, *args, **kwargs):
        """
        Construct the Set Quiet action (make a recipe quiet via argument)

        :param args: arguments passed to argparse.Action.__init__
        :param kwargs: keyword arguments passed to argparse.Action.__init__
        """
        # set class name
        self.class_name = '_SetQuiet'
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_SetQuiet')
        # set recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

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
        String representation of this class
        :return:
        """
        return '_SetQuiet[DrsAction]'

    def _set_return(self) -> True:
        """
        Return True (and a debug message)

        :return: True
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '_set_return', __NAME__,
                         self.class_name)
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00034')
        WLOG(self.recipe.params, 'debug', dmsg)
        # return strvalue
        return True

    def __call__(self, parser: DrsArgumentParser,
                 namespace: argparse.Namespace, values: Any,
                 option_string: Any = None):
        """
        Call the action _SetQuiet() - sets the _SetQuiet.dest to True if
        argument is present

        :param parser: DrsArgumentParser instance
        :param namespace: argparse.Namespace instance
        :param values: Any, the values to check directory argument
        :param option_string: None in most cases but used to get options
                              for testing the value if required
        :return: None
        :raises: drs_exceptions.LogExit
        """
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_return()
        # Add the attribute
        setattr(namespace, self.dest, value)


# =============================================================================
# Define Argument Class
# =============================================================================
class DrsArgument(object):
    def __init__(self, name: Union[str, None] = None,
                 kind: Union[str, None] = None,
                 pos: Union[int, str, None] = None,
                 altnames: Union[List[str], None] = None,
                 dtype: Union[str, Type, None] = None,
                 options: Union[List[Any], None] = None,
                 helpstr: Union[str, None] = '',
                 files: Union[List[DrsInputFile], None] = None,
                 path: Union[str, None] = None,
                 limit: Union[int, None] = None,
                 minimum: Union[int, float, None] = None,
                 maximum: Union[int, float, None] = None,
                 filelogic: str = 'inclusive', default: Union[Any, None] = None,
                 default_ref: Union[str, None] = None,
                 required: bool = None, reprocess: bool = False):
        """
        Create a DRS Argument object

        :param name: string, the name of the argument and call, for optional
                     arguments should include the "-" and "--" in front
                     ("arg.name" will not include these but "arg.argname"
                     and "arg.names" will)

        :param kind: string the argument kind (argument or keyword argument)

        :param pos: int or None, the position of a position argument, if None
                   not a positional argument (i.e. optional argument)

        :param altnames: list of strings or None, the alternative calls to
                        the argument in argparse (as well as "name"), if None
                        only call to argument is "name"

        :param dtype: string or type or None, the data type currently must
                     be one of the following:
                        ['files', 'file', 'directory', 'bool',
                         'options', 'switch', int, float, str, list]
                     if None set to string.
                     these control the checking of the argument in most cases.
                     int/flat/str/list are not checked

        :param options: list of strings or None, sets the allowed string values
                       of the argument, if None no options are required (other
                       than those set by dtype)

        :param helpstr: string or None, if not None sets the text to add to the
                       help string

        :param files: list of DrsInput objects or None, if not None and dtype
                     is "files" or "file" sets the type of file to expect
                     the way the list is understood is based on "filelogic"

        :param path: str, if set overwrites any directory parameter
                     Note path can be a parameter in ParamDict

        :param limit: int, file limit for processing

        :param minimum: int, float, the minimum value for this argument

        :param maximum: int, float, the maximum value for this argument

        :param filelogic: string, either "inclusive" or "exclusive", if
                         inclusive and combination of DrsInput objects are
                         valid, if exclusive only one DrsInput in the list is
                         valid for all files i.e.
                         - if files = [A, B] and filelogic = 'inclusive'
                           the input files may all be A or all be B
                         - if files = [A, B] and filelogic = 'exclusive'
                           the input files may be either A or B

        :param default: the default value to give the argument if unset,
                        either this or defaulf_ref must be set for kwargs

        :param default_ref: str, the key in the constant parameter dictionary
                            where the default value it set, either this or
                            defaulf_ref must be set for kwargs

        :param required: bool, if True this is a required argument and must
                         be used as an argument or exception raised

        :param reprocess: bool, if True this argument will be used in processing
                          script as a required argument (but does not raise an
                          exception when recipe used individually)

        """
        # set class name
        self.class_name = 'DrsArgument'
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(None, '__init__', __NAME__, self.class_name)
        # ------------------------------------------------------------------
        # define class constants
        # ------------------------------------------------------------------
        # define allowed properties
        self.propkeys = ['action', 'nargs', 'type', 'choices', 'default',
                         'help']
        # define allowed dtypes
        self.allowed_dtypes = ['files', 'file', 'directory', 'bool',
                               'options', 'switch', int, float, str, list]
        # ------------------------------------------------------------------
        # deal with no name or kind (placeholder for copy)
        if name is None:
            name = 'UnknownArg'
        if kind is None:
            kind = 'arg'
        # ------------------------------------------------------------------
        # assign values from construction
        # ------------------------------------------------------------------
        # deal with name
        # get argument name
        self.argname = str(name)
        # get full name
        self.name = name
        while self.name.startswith('-'):
            self.name = self.name[1:]
        # ------------------------------------------------------------------
        # check name is correct for kind
        if kind == 'arg':
            self.kind = kind
            # check argname
            if self.argname.startswith('-'):
                # Get text for default language/instrument
                text = TextDict('None', 'None')
                # get entry to log error
                ee = TextEntry('00-006-00015', args=[self.argname])
                self.exception(None, errorobj=[ee, text])
        elif kind == 'kwarg':
            self.kind = kind
            # check argname
            if not self.argname.startswith('-'):
                # Get text for default language/instrument
                text = TextDict('None', 'None')
                # get entry to log error
                ee = TextEntry('00-006-00016', args=[self.argname])
                self.exception(None, errorobj=[ee, text])
        elif kind == 'special':
            self.kind = kind
            # check argname
            if not self.argname.startswith('-'):
                # Get text for default language/instrument
                text = TextDict('None', 'None')
                # get entry to log error
                ee = TextEntry('00-006-00017', args=[self.argname])
                self.exception(None, errorobj=[ee, text])
        else:
            self.kind = kind
            emsg = '"kind" must be "arg" or "kwarg" or "special"'
            self.exception(emsg)
        # ------------------------------------------------------------------
        # special parameter (whether to skip other arguments)
        self.skip = False
        # get position
        self.pos = pos
        # add names from altnames
        if altnames is None:
            altnames = []
        self.names = [self.argname] + altnames
        # get dtype
        self.dtype = dtype
        # get options
        self.options = options
        # get help str
        self.helpstr = helpstr
        # ---------------------------------------------------------------------
        # get files
        self.files = []
        if files is None:
            pass
        # deal with files having a length (i.e. a list)
        elif hasattr(files, '__len__'):
            for drsfile in files:
                if isinstance(drsfile, DrsInputFile):
                    # copy attributes from drsfile
                    newdrsfile = drsfile.completecopy(drsfile)
                    # append to files
                    self.files.append(newdrsfile)
                else:
                    # get exception argumnets
                    eargs = [self.name, 'DrsInputFile', func_name]
                    # raise exception
                    raise DrsCodedException('00-006-00021', level='error',
                                            targs=eargs, func_name=func_name)
        # else assume file is a single file (but put it into a list any way)
        else:
            drsfile = files
            if isinstance(drsfile, DrsInputFile):
                self.files = [drsfile.completecopy(drsfile)]
            else:
                # get exception arguments
                eargs = [self.name, 'DrsInputFile', func_name]
                # raise exception
                raise DrsCodedException('00-006-00021', level='error',
                                        targs=eargs, func_name=func_name)
        # ---------------------------------------------------------------------
        # define the override input path for files (defaults to directory)
        #    Note path can be a parameter in param dict
        self.path = path
        # get limit
        self.limit = limit
        # get limits
        self.minimum = minimum
        self.maximum = maximum
        # get file logic
        self.filelogic = filelogic
        if self.filelogic not in ['inclusive', 'exclusive']:
            # Get text for default language/instrument
            text = TextDict('None', 'None')
            # get entry to log error
            ee = TextEntry('00-006-00008', args=[self.filelogic])
            self.exception(None, errorobj=[ee, text])
        # deal with no default/default_ref for kwarg
        if kind == 'kwarg':
            # get entry
            if (default is None) and (default_ref is None):
                # Get text for default language/instrument
                text = TextDict('None', 'None')
                # get entry to log error
                ee = TextEntry('00-006-00009', args=self.filelogic)
                self.exception(None, errorobj=[ee, text])
        # get default
        self.default = default
        # get default_ref
        self.default_ref = default_ref
        # get required
        if self.kind == 'arg':
            if required is None:
                self.required = True
            else:
                self.required = required
        else:
            if required is None:
                self.required = False
            else:
                self.required = required
        # get whether we need this arguement for processing scripts
        self.reprocess = reprocess
        # set empty
        self.props = OrderedDict()
        self.value = None

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
        Defines the str(DrsArgument) return for DrsArgument
        :return str: the string representation of DrSArgument
                     i.e. DrsArgument[name]
        """
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, '__str__', __NAME__, self.class_name)
        # return string representation
        return self.__repr__()

    def __repr__(self) -> str:
        """
        Defines the print(DrsArgument) return for DrsArgument
        :return str: the string representation of DrSArgument
                     i.e. DrsArgument[name]
        """
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, '__str__', __NAME__, self.class_name)
        # return string representation
        return 'DrsArgument[{0}]'.format(self.name)

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
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, 'make_properties', __NAME__, 'DrsArgument')
        # deal with no dtype
        if self.dtype is None:
            self.dtype = str
        # make sure dtype is valid
        if self.dtype not in self.allowed_dtypes:
            # Get text for default language/instrument
            text = TextDict('None', 'None')
            # make error
            a_dtypes_str = ['"{0}"'.format(i) for i in self.allowed_dtypes]
            eargs = [' or '.join(a_dtypes_str), self.dtype]
            ee = TextEntry('00-006-00010', args=eargs)
            self.exception(None, errorobj=[ee, text])
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

    def assign_properties(self, props: dict):
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
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, 'assign_properties', __NAME__, 'DrsArgument')
        # loop around properties
        for prop in self.propkeys:
            if prop in props:
                self.props[prop] = props[prop]

    def copy(self, argument: 'DrsArgument'):
        """
        Copies another DrsArgument into this DrsArgument

        :param argument: a DrsArgument instance
        :return: None
        """
        # set function name (cannot break here --> no access to params)
        func_name = display_func(None, 'copy', __NAME__, 'DrsArgument')
        # get argument name
        self.argname = str(argument.argname)
        # get full name
        self.name = str(argument.name)
        # get kind
        self.kind = str(argument.kind)
        # special parameter (whether to skip other arguments)
        self.skip = bool(argument.skip)
        # get position
        if argument.pos is None:
            self.pos = None
        else:
            self.pos = str(argument.pos)
        # add names from altnames
        self.names = list(argument.names)
        # get dtype
        self.dtype = copy.deepcopy(argument.dtype)
        # get options
        if argument.options is None:
            self.options = None
        else:
            self.options = list(argument.options)
        # get help str
        self.helpstr = copy.deepcopy(argument.helpstr)
        # get files
        self.files = []
        # deal with files as a list
        if isinstance(argument.files, list):
            for drsfile in argument.files:
                if isinstance(drsfile, DrsInputFile):
                    # copy attributes from drsfile
                    newdrsfile = drsfile.completecopy(drsfile)
                    # append to files
                    self.files.append(newdrsfile)
                else:
                    # get exception argumnets
                    eargs = [self.name, 'DrsInputFile', func_name]
                    # raise exception
                    raise DrsCodedException('00-006-00021', level='error',
                                            targs=eargs, func_name=func_name)
        # else assume file is a single file (but put it into a list any way)
        else:
            drsfile = argument.files
            if isinstance(drsfile, DrsInputFile):
                self.files = [drsfile.completecopy(drsfile)]
            else:
                # get exception argumnets
                eargs = [self.name, 'DrsInputFile', func_name]
                # raise exception
                raise DrsCodedException('00-006-00021', level='error',
                                        targs=eargs, func_name=func_name)
        # copy the override input path
        #    Note path can be a parameter in param dict
        self.path = copy.deepcopy(argument.path)
        # get limit
        if argument.limit is None:
            self.limit = None
        else:
            self.limit = int(argument.limit)
        # get limits
        self.minimum = copy.deepcopy(argument.minimum)
        self.maximum = copy.deepcopy(argument.maximum)
        # get file logic
        self.filelogic = str(argument.filelogic)
        # get default
        self.default = copy.deepcopy(argument.default)
        # get default_ref
        self.default_ref = copy.deepcopy(argument.default_ref)
        # get required
        self.required = bool(argument.required)
        self.reprocess = bool(argument.reprocess)
        # set empty
        self.props = copy.deepcopy(argument.props)
        self.value = copy.deepcopy(argument.value)

    def exception(self, message: Union[str, None] = None,
                  errorobj: Any = None):
        """
        Internal exception generator --> raises an Argument Error with
        message including a logging code for debug purposes

        :param message: str, the error message to print
        :param errorobj: an error exception instance
        :return: None
        :raises: drs_exceptions.ArgumentError
        """
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, 'exception', __NAME__, 'DrsArgument')
        # deal with required (positional) argument
        if self.kind == 'arg':
            log_opt = 'A[{0}] '.format(self.name)
        # deal with optional argument
        elif self.kind == 'kwarg':
            log_opt = 'K[{0}] '.format(self.name)
        # deal with special optional argument
        elif self.kind == 'special':
            log_opt = 'S[{0}] '.format(self.name)
        # deal with anything else (should not get here)
        else:
            log_opt = 'X[{0}] '.format(self.name)
        # if we have an error object then raise an argument error with
        #   the error object
        if errorobj is not None:
            errorobj[0] = log_opt + errorobj[0]
            raise ArgumentError(errorobj=errorobj)
        # else raise the argument error with just the message
        else:
            raise ArgumentError(message)



# =============================================================================
# Check functions
# =============================================================================
def valid_directory(params: ParamDict, indexdb: IndexDatabase,
                    argname: str, directory: Any, kind: str,
                    forced_dir: Union[str, None] = None) -> str:
    """
    Find out whether we have a valid directory

    :param params: ParamDict, the parameter dictionary of constants
    :param indexdb: IndexDatabase, the index database instance
    :param argname: str, the argumnet name "directory" came from (for error
                    logging)
    :param directory: Any, the value to test whether it is a valid directory)
    :param kind: str, either raw, tmp, red (where the directory should be
                 located unless force is True)
    :param forced_dir: if set this is the forced directory to use, if not set
                       uses kind to determine path

    :return: tuple: 1. whether directory is valid, 2. the full directory path
             (if passed) or None if failed, 3. the reason for failure (or None
             if passed)
    """
    # set function name
    func_name = display_func(params, 'valid_directory', __NAME__)

    # get input directory
    input_dir = drs_file.get_dir(params, kind, dirpath=forced_dir)

    # -------------------------------------------------------------------------
    # 1. check directory is a valid string
    # -------------------------------------------------------------------------
    try:
        directory = str(directory)
    except Exception as _:
        eargs = [argname, directory, type(directory)]
        WLOG(params, 'error', TextEntry('09-001-00003', args=eargs))

    # clean up
    directory = directory.strip()

    # -------------------------------------------------------------------------
    # deal with database
    # -------------------------------------------------------------------------
    # deal with instrument == 'None'
    if indexdb.instrument == 'None':
        eargs = [argname, indexdb.name, func_name]
        WLOG(params, 'error', TextEntry('09-001-00032', args=eargs))
    elif indexdb.database is None:
        # try to load database
        indexdb.load_db()
    # update database with entries
    indexdb.update_entries(kind=kind, force_dir=forced_dir)
    # set up condition
    condition = 'KIND=="{0}"'.format(kind)
    # load directory names
    directories = indexdb.database.unique('DIRECTORY', condition=condition)

    # -------------------------------------------------------------------------
    # 2. check for directory in database
    # -------------------------------------------------------------------------
    # may need to remove input_path from directory
    if input_dir in directory:
        # remove input dir from directory
        directory = directory.split(input_dir)[-1]
        # remove os separator from directory (at start)
        while directory.startswith(os.sep):
            directory = directory[len(os.sep):]

    # return if found
    if directory in directories:
        # need full path of directory
        return os.path.realpath(os.path.join(input_dir, directory))

    # -------------------------------------------------------------------------
    # 3. directory is not correct - raise error
    # -------------------------------------------------------------------------
    abspath = indexdb.deal_with_filename(kind=kind, force_dir=forced_dir)
    eargs = [argname, directory, str(abspath)]
    WLOG(params, 'error', TextEntry('09-001-00004', args=eargs))


def valid_file(params: ParamDict, indexdb: IndexDatabase, kind: str,
               argname: str, filename: str, rargs: Dict[str, DrsArgument],
               rkwargs: Dict[str, DrsArgument], directory,
               types: List[DrsInputFile],
               forced_dir: Union[str, None] = None) -> ValidFileType:
    """
    Test for whether a file is valid

    :param params: ParamDict - parameter dictionary of constants
    :param indexdb: IndexDatabase instance, the index database
    :param kind: str, the input directory kind: 'raw', 'tmp', 'red'
    :param argname: str, the name of the argument we are testing
    :param filename: string, the filename to test
    :param rargs: dictionary of DrsArguments - the positional arguments
    :param rkwargs: dictionary of DrsArguments - the optional arguments
    :param directory: str, the directory for this recipe run
    :param types: List[DrsInputFile] - the drs file types for all files
                  currently found
    :param forced_dir: str, if set the path to use for files, else uses
                       kind to determine path
    """
    # set function name
    func_name = display_func(params, '_valid_file', __NAME__)
    # get the argument that we are checking the file of
    arg = _get_arg(rargs, rkwargs, argname)
    drsfiles = arg.files
    # get the drs logic
    drs_logic = arg.filelogic
    # deal with arg.path set
    directory = _check_arg_path(params, arg, directory)
    # ---------------------------------------------------------------------
    # Step 1: Check filename is a valid string
    # ---------------------------------------------------------------------
    try:
        filename = str(filename)
    except Exception as _:
        eargs = [argname, filename, type(filename)]
        WLOG(params, 'error', TextEntry('09-001-00005', args=eargs))
    # clean up
    filename = filename.strip()
    # -------------------------------------------------------------------------
    # deal with database
    # -------------------------------------------------------------------------
    # deal with instrument == 'None'
    if indexdb.instrument == 'None':
        eargs = [argname, indexdb.name, func_name]
        WLOG(params, 'error', TextEntry('09-001-00032', args=eargs))
    elif indexdb.database is None:
        # try to load database
        indexdb.load_db()
    # update database with entries
    indexdb.update_entries(kind=kind, force_dir=forced_dir)
    # set up condition
    condition = 'KIND=="{0}"'.format(kind)
    condition += ' AND DIRECTORY=="{0}"'.format(os.path.basename(directory))
    # deal with wildcards
    if '*' in filename:
        # make filename sql-like
        filename = filename.replace('*', '%')
        # make a path cond
        pathcond = 'PATH LIKE "{0}"'
    else:
        # make a path cond
        pathcond = 'PATH == "{0}"'
    # ---------------------------------------------------------------------
    # Step 2: Check whether filename itself is in database
    # ---------------------------------------------------------------------
    # check for filename in paths
    condition1 = condition + ' AND ' + pathcond.format(filename)
    # count number of paths that meet this condition
    if indexdb.database.count(condition=condition1) > 0:
        # now check fits keys (or pass if not fits)
        filenames, filetypes = _check_fits_keys(params, drsfiles, indexdb,
                                                condition1, argname, kind,
                                                directory, forced_dir)
        # now check drs logic [if exclusive must be same file type]
        _check_file_logic(params, argname, drs_logic, filetypes, types)
        # return filename and filetype
        return filenames, filetypes

    # ---------------------------------------------------------------------
    # Step 3: Check whether directory + filename is in database
    # ---------------------------------------------------------------------
    # get absolute path
    abspath = os.path.join(directory, filename)
    # check for filename in paths
    condition1 = condition + 'AND ' + pathcond.format(abspath)
    # count number of paths that meet this condition
    if indexdb.database.count(condition=condition1) > 0:
        # now check fits keys (or pass if not fits)
        filenames, filetypes = _check_fits_keys(params, drsfiles, indexdb,
                                                condition1, argname, kind,
                                                directory, forced_dir)
        # now check drs logic [if exclusive must be same file type]
        _check_file_logic(params, argname, drs_logic, filetypes, types)
        # return filename and filetype
        return filenames, filetypes

    # ---------------------------------------------------------------------
    # Step 4: Filename is invalid
    # ---------------------------------------------------------------------
    # if we have reached this point we cannot file filename
    eargs = [argname, filename, abspath]
    WLOG(params, 'error', TextEntry('09-001-00005', args=eargs))


def _check_fits_keys(params: ParamDict, drsfiles: List[DrsInputFile],
                     indexdb: IndexDatabase, condition: str,
                     argname: str, kind: str, directory: str,
                     forced_dir: Union[str, None] = None
                     ) -> Tuple[List[str], List[DrsInputFile]]:
    """

    :param params:
    :param drsfiles:
    :param indexdb:
    :param condition:
    :param forced_dir:
    :return:
    """
    # set function name
    func_name = display_func(params, '_check_fits_keys', __NAME__)
    # get data for this condition (must be greater than 0)
    table = indexdb.get_entries('*', condition=condition)
    # storage for output
    files, types = [], []
    # loop around rows in table
    for row in range(len(table)):
        # store that row is valid
        row_valid = False
        # ---------------------------------------------------------------------
        # create fake header from table
        header = drs_fits.Header()
        for key in table.keys():
            if 'KW_' not in key:
                continue
            if key in params:
                drs_key = params[key][0]
            else:
                drs_key = str(key)
            # push into temporary header
            header[drs_key] = table[key].iloc[row]
        # ---------------------------------------------------------------------
        # get filename
        filename_it = table['PATH'].iloc[row]
        # make instance of the DrsFile
        input_dir = drs_file.get_dir(params, kind, dirpath=forced_dir)
        # ---------------------------------------------------------------------
        # find file in possible file types
        # ---------------------------------------------------------------------
        # no error to start with
        error = None
        # loop around file types
        for drsfile in drsfiles:
            # if in debug mode print progres
            dargs = [drsfile.name, os.path.basename(filename_it)]
            WLOG(params, 'debug', TextEntry('90-001-00008', args=dargs),
                 wrap=False)
            # -------------------------------------------------------------
            # create an instance of this drs_file with the filename set
            file_in = drsfile.newcopy(filename=filename_it, params=params)
            file_in.get_header()
            # set the directory
            file_in.directory = drs_misc.get_uncommon_path(directory, input_dir)
            # -------------------------------------------------------------
            # Step 1: Check extension
            # -------------------------------------------------------------
            # check the extension
            valid, error = file_in.has_correct_extension(argname=argname)
            if not valid:
                continue
            # -------------------------------------------------------------
            # Step 2: Check file header has required keys
            # -------------------------------------------------------------
            valid, error = file_in.hkeys_exist(header=header, argname=argname)
            if not valid:
                continue
            # -------------------------------------------------------------
            # Step 3: Check file header has correct required keys
            # -------------------------------------------------------------
            valid, error = file_in.has_correct_hkeys(header=header,
                                                     argname=argname)
            if not valid:
                continue
            # -------------------------------------------------------------
            # Step 4: if valid save for later
            # -------------------------------------------------------------
            if valid:
                # get the header
                file_in.get_header()
                # add to lists
                files.append(file_in.filename)
                types.append(file_in)
                # flag that row is valid
                row_valid = True
                # now stop looping through drs files
                break
        # if at the end of all drsfiles this row is not valid print the error
        if not row_valid and error is not None:
            WLOG(params, 'error', error)
    # finally return the list of files
    return files, types


def _check_file_logic(params, argname, logic, filetypes, types):

    # deal with types being an empty list
    if len(types) == 0:
        return
    # else check exclusive logic
    if logic == 'exclusive':
        # loop around newly identified files
        for filetype in filetypes:
            # all files in types should be correct so we just need to
            #   check the name of each of our new ones against the last
            #   file in types
            if filetype.name != types[-1].name:
                # raise error if not
                eargs = [argname, filetype.name, types.name[-1]]
                WLOG(params, 'error', TextEntry('09-001-00008', args=eargs))


# =============================================================================
# Worker functions
# =============================================================================


def _get_version_info(params: ParamDict, green: str = '',
                      end: str = '') -> List[str]:
    """
    Get a list of strings of the version info

    :param params: ParamDict, the constants parameter dictionary
    :param green: str, the code for green text (from Colors())
    :param end: str, the code for reset text end character (from Colors())
    :return: a list of strings for the print out
    """
    # set function name (cannot break here --> no access to params)
    _ = display_func(params, '_get_version_info', __NAME__)
    # get name
    if 'DRS_NAME' in params:
        name = str(params['DRS_NAME'])
    else:
        name = str(params['RECIPE'])
    # get version
    if 'DRS_VERSION' in params:
        version = str(params['DRS_VERSION'])
    else:
        version = __version__

    # get text strings
    text = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    namestr = text['40-001-00001']
    versionstr = text['40-001-00002']
    authorstr = text['40-001-00003']
    authors = ', '.join(__author__)
    datestr = text['40-001-00004']
    releasestr = text['40-001-00005']
    # construct version info string
    imsgs = [green + '\t{0}: {1}'.format(namestr, name),
             green + '\t{0}: {1}'.format(versionstr, version) + end,
             green + '\t{0}: {1}'.format(authorstr, authors) + end,
             green + '\t{0}: {1}'.format(datestr, __date__) + end,
             green + '\t{0}: {1}'.format(releasestr, __release__) + end]
    return imsgs


def _help_format(keys: List[str], helpstr: str,
                 options: Union[List[Any], None] = None) -> str:
    """
    The help formater - returns a string representation of the argument

    :param keys: list of strings, the argument names to add
    :param helpstr: str, the help string to add
    :param options: list of Any, the options to add (must be convertable to
                    list of strings)
    :return: str, the help text
    """
    # set function name (cannot break here --> no access to params)
    _ = display_func(None, '_help_format', __NAME__)
    # set up empty format string
    fmtstring = ''
    # set separation size
    sep = 19
    # set maximum size
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
        helpstrs = drs_text.textwrap(helpstr, maxsize)
    else:
        helpstrs = [helpstr]

    # add start separation
    for hstr in helpstrs:
        fmtstring += '\n' + ' ' * sep + hstr

    # return formatted string
    return fmtstring


def _print_list_msg(recipe: Any, fulldir: str, dircond: bool = False,
                    return_string: bool = False,
                    list_all: bool = False) -> Union[None, List[str]]:
    """
    Prints the listing message (using "get_file_list")

    :param recipe: DrsRecipe instance
    :param fulldir: string, the full "root" (top level) directory
    :param dircond: bool, if True only prints directories (passed to
                    get_file_list)
    :param return_string: bool, if True returns string output instead of
                          printing
    :param list_all: bool, if True overrides lmit (set by HARD_DISPLAY_LIMIT)

    :return: if return_strings is True return list msg instead of printing
    """
    # get params from recipe
    params = recipe.params
    # set function name
    _ = display_func(params, '_print_list_msg', __NAME__)
    # get text
    text = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    helptext = HelpText(params['INSTRUMENT'], params['LANGUAGE'])
    # get limit
    mlimit = params['DRS_MAX_IO_DISPLAY_LIMIT']
    # generate a file list
    filelist, limitreached = _get_file_list(mlimit, fulldir, recursive=True,
                                            dir_only=dircond, list_all=list_all)
    # get parameterse from drs_params
    program = str(params['RECIPE'])
    # construct error message
    if return_string:
        green, end = '', ''
        # yellow, blue = '', ''
    elif params['DRS_COLOURED_LOG']:
        green, end = COLOR.GREEN1, COLOR.ENDC
        # yellow, blue = COLOR.YELLOW1, COLOR.BLUE1
    else:
        green, end = COLOR.ENDC, COLOR.ENDC
        # yellow, blue = COLOR.ENDC, COLOR.ENDC
    # get the file argument list (for use below)
    fileargs = []
    for argname in recipe.args:
        arg = recipe.args[argname]
        if arg.dtype in ['file', 'files']:
            fileargs.append(argname)
    for kwargname in recipe.kwargs:
        kwarg = recipe.kwargs[kwargname]
        if kwarg.dtype in ['file', 'files'] and kwarg.required:
            fileargs.append(kwargname)
    # get the arguments to format "wmsg"
    ortext = helptext['OR_TEXT']
    wargs = [mlimit, fulldir, (' {0} '.format(ortext)).join(fileargs)]
    # deal with different usages (before directory defined and after)
    #   and with/without limit reached
    wmsgs = []
    if limitreached:
        if dircond:
            wmsgs.append(text['40-005-00002'].format(*wargs))
        else:
            wmsgs.append(text['40-005-00003'].format(*wargs))
    else:
        if dircond:
            wmsgs.append(text['40-005-00004'].format(*wargs))
        else:
            wmsgs.append(text['40-005-00005'].format(*wargs))
    # loop around files and add to list
    for filename in filelist:
        wmsgs.append('\t' + filename)

    # construct print error message (with usage help)
    pmsgs = ['']

    # print info
    if not return_string:
        pmsgs.append(green + params['DRS_HEADER'] + end)
        pmsgs.append(green + ' ' + text['40-005-00001'].format(program) + end)
        pmsgs.append(green + params['DRS_HEADER'] + end)
    #     imsgs = _get_version_info(params, green, end)
    #     pmsgs += imsgs
    #     pmsgs.append('')
    #     pmsgs.append(blue + parser.format_usage() + end)
    #     pmsgs.append('')
    for wmsg in wmsgs:
        pmsgs.append(green + wmsg + end)
    # deal with returning/printing
    if return_string:
        return pmsgs
    else:
        for pmsg in pmsgs:
            print(pmsg)


def _get_file_list(limit: int, path: str, ext: Union[str, None] = None,
                   recursive: bool = False, dir_only: bool = False,
                   list_all: bool = False) -> Tuple[np.ndarray, bool]:
    """
    Get a list of files in a path

    :param limit: int, the number of files to limit the search to (stops after
                  this number of files)
    :param path: string, the path to search for files
    :param ext: string, the extension to limit the file search to, if None
                does not filter by extension
    :param recursive: bool, if True searches sub-directories recursively
    :param dir_only: bool, if True only lists directories (not files)
    :param list_all: bool, if True overides the limit feature and lists all
                     directories/files

    :return file_list: tuple, np.array the files found with extension (if not
                       None, up to the number limit) and bool whether the limit
                       was reached
    """
    # set function name (cannot break here --> no access to params)
    _ = display_func(None, '_get_file_list', __NAME__)
    # deal with no limit - set hard limit
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
    for root, dirs, files in os.walk(path, followlinks=True):
        if len(file_list) > limit:
            file_list.append(level + '...')
            return np.array(file_list), True
        if not recursive and root != path:
            continue
        if len(files) > 0 and recursive:
            limit += 1
        if not dir_only:
            # add root to file list (minus path)
            if root != path:
                directory = drs_misc.get_uncommon_path(root, path) + os.sep
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
                    return np.array(file_list), limit_reached
                # do not display if extension is true
                if not filename.endswith(ext):
                    continue
                # add to file list
                file_list.append(filelevel + filename)
        elif len(files) > 0:
            # add root to file list (minus path)
            if root != path:
                directory = drs_misc.get_uncommon_path(root, path) + os.sep
                # append to list
                file_list.append(level + levelsep + directory)

    # if empty list add none found
    if len(file_list) == 0:
        file_list = ['No valid files found.']
    # return file_list
    return np.sort(file_list), limit_reached


def _get_arg(rargs: Dict[str, DrsArgument],
             rkwargs: Dict[str, DrsArgument], argname: str) -> DrsArgument:
    """
    Find an argument in the DrsRecipes argument dictionary or if not found
    find argument in the DrsRecipes keyword argument dictionary or it not found
    at all return None

    :param recipe: DrsRecipe instance

    :params rargs: dictionary of positional arguments (from recipe.args)
    :params rkwargs: dictionary of optional arguments (from recipe.kwargs)
    :param argname: string, the argument/keyword argument to look for

    :return: DrsArgument instance, the argument in DrsRecipe.args or
             DrsRecipe.kwargs
    """
    if argname in rargs:
        arg = rargs[argname]
    elif argname in rkwargs:
        arg = rkwargs[argname]
    else:
        arg = None
    # return arg
    return arg


def _check_arg_path(params: ParamDict, arg: DrsArgument,
                    directory: str) -> str:
    """
    Check if an override path is set (via DrsArgument.path) if it isn't
    then we stick with "directory" as our path to the file
    Note DrsArgument.path can be a parameter in param dict

    :param params: Paramdict
    :param arg:
    :param directory:
    :return:
    """
    # set function name
    func_name = display_func(params, '_check_arg_path', __NAME__)
    # set the path as directory if arg.path is None
    if arg.path is None:
        return os.path.abspath(directory)
    # deal with arg.path being a link to a constant
    if arg.path in params:
        path = params[arg.path]
    # else assume arg.path is a path
    else:
        path = arg.path
    # path may be relative to main drs package to get full path
    if not os.path.exists(path):
        # get package name
        package = params['DRS_PACKAGE']
        # get absolute path
        path = drs_break.get_relative_folder(package, path)
    # make path absolute
    path = os.path.abspath(path)
    # now check that path is valid
    if not os.path.exists(path):
        # log that arg path was wrong
        eargs = [arg.name, arg.path, func_name]
        WLOG(params, 'error', TextEntry('00-006-00018', args=eargs))
    else:
        return path


# =============================================================================
# Make functions
# =============================================================================
def make_listing(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Sets whether to display listing files
    up to DRS_MAX_IO_DISPLAY_LIMIT in number.

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_listing', __NAME__)
    # define the listing limit (used in listing help
    limit = params['DRS_MAX_IO_DISPLAY_LIMIT']
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--listing'
    # set any argument alternative names
    props['altnames'] = ['--list']
    # set the argument action function
    props['action'] = _MakeListing
    # set the number of argument to expect
    props['nargs'] = 0
    # set the help message
    props['help'] = htext['LISTING_HELP'].format(limit)
    # return the argument dictionary
    return props


def make_alllisting(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Sets whether to display all listing files

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_alllisting', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--listingall'
    # set any argument alternative names
    props['altnames'] = ['--listall']
    # set the argument action function
    props['action'] = _MakeAllListing
    # set the number of argument to expect
    props['nargs'] = 0
    # set the help message
    props['help'] = htext['ALLLISTING_HELP']
    # return the argument dictionary
    return props


def make_debug(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Sets which debug mode to be in

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_debug', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--debug'
    # set any argument alternative names
    props['altnames'] = ['--d', '--verbose']
    # set the argument action function
    props['action'] = _ActivateDebug
    # set the number of argument to expect
    props['nargs'] = '?'
    # set the help message
    props['help'] = htext['DEBUG_HELP']
    # return the argument dictionary
    return props


def set_inputdir(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Sets input directory

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'set_inputdir', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--force_indir'
    # set any argument alternative names
    props['altnames'] = []
    # set the argument action function
    props['action'] = _ForceInputDir
    # set the number of argument to expect
    props['nargs'] = 1
    # set the help message
    props['help'] = htext['SET_INPUT_DIR_HELP']
    # return the argument dictionary
    return props


def set_outputdir(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Sets output directory

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'set_outputdir', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--force_outdir'
    # set any argument alternative names
    props['altnames'] = []
    # set the argument action function
    props['action'] = _ForceOutputDir
    # set the number of argument to expect
    props['nargs'] = 1
    # set the help message
    props['help'] = htext['SET_OUTPUT_DIR_HELP']
    # return the argument dictionary
    return props


def make_version(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Whether to display drs version information

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_version', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--version'
    # set any argument alternative names
    props['altnames'] = []
    # set the argument action function
    props['action'] = _DisplayVersion
    # set the number of argument to expect
    props['nargs'] = 0
    # set the help message
    props['help'] = htext['VERSION_HELP']
    # return the argument dictionary
    return props


def make_info(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Whether to display recipe information

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_info', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--info'
    # set any argument alternative names
    props['altnames'] = ['--usage']
    # set the argument action function
    props['action'] = _DisplayInfo
    # set the number of argument to expect
    props['nargs'] = 0
    # set the help message
    props['help'] = htext['INFO_HELP']
    # return the argument dictionary
    return props


def set_program(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Set the program name

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'set_program', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--program'
    # set any argument alternative names
    props['altnames'] = ['--prog']
    # set the argument action function
    props['action'] = _SetProgram
    # set the number of argument to expect
    props['nargs'] = 1
    # set the help message
    props['help'] = htext['SET_PROGRAM_HELP']
    # return the argument dictionary
    return props


def set_ipython_return(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Set the use of ipython return after
    script ends

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'set_ipython_return', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--idebug'
    # set any argument alternative names
    props['altnames'] = ['--idb']
    # set the argument action function
    props['action'] = _SetIPythonReturn
    # set the number of argument to expect
    props['nargs'] = 0
    # set the help message
    props['help'] = htext['SET_IPYTHON_RETURN_HELP']
    # return the argument dictionary
    return props


def breakpoints(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Set the use of break_point

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'breakpoints', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--breakpoints'
    # set any argument alternative names
    props['altnames'] = ['--break']
    # set the argument action function
    props['action'] = _Breakpoints
    # set the number of argument to expect
    props['nargs'] = 0
    # set the help message
    props['help'] = htext['BREAKPOINTS_HELP']
    # return the argument dictionary
    return props


def is_master(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Set the use of break_point

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'is_master', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--master'
    # set any argument alternative names
    props['altnames'] = []
    # set the argument action function
    props['action'] = _IsMaster
    # set the number of argument to expect
    props['nargs'] = 1
    # set the help message
    props['help'] = htext['IS_MASTER_HELP']
    # return the argument dictionary
    return props


def make_breakfunc(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Set a break function

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_breakfunc', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--breakfunc'
    # set any argument alternative names
    props['altnames'] = ['--bf']
    # set the argument action function
    props['action'] = _Breakfunc
    # set the number of argument to expect
    props['nargs'] = 1
    # set the help message
    props['help'] = htext['BREAKFUNC_HELP']
    # return the argument dictionary
    return props


def set_quiet(params: ParamDict, htext: HelpText) -> OrderedDict:
    """
    Make a custom special argument: Set the quiet mode

    :param params: ParamDict, Parameter Dictionary of constants
    :param htext: HelpText, the help text instance (text from lang database)

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name (cannot break here --> no access to params)
    _ = display_func(params, 'set_quiet', __NAME__)
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--quiet'
    # set any argument alternative names
    props['altnames'] = ['--q']
    # set the argument action function
    props['action'] = _SetQuiet
    # set the number of argument to expect
    props['nargs'] = 0
    # set the help message
    props['help'] = htext['QUIET_HELP']
    # return the argument dictionary
    return props


# =============================================================================
# End of code
# =============================================================================
