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


# =============================================================================
# Define ArgParse Parser and Action classes
# =============================================================================
# Adapted from: https://stackoverflow.com/a/16942165
class DrsArgumentParser(argparse.ArgumentParser):
    # argparse.ArgumentParser cannot be pickled
    #   so cannot pickle DrsArgumentParser either

    def __init__(self, recipe: Any, **kwargs):
        """
        Construct the Drs Argument parser

        :param recipe: Drs Recipe - the recipe class for these arguments
        :param kwargs: keyword arguments passed to argparse.ArgumentParser
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, 'DRSArgumentParser')
        # define the recipe
        self.recipe = recipe
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
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # debug checking output
        if params['DRS_DEBUG'] > 0:
            print('')
        WLOG(params, 'debug', TextEntry('90-001-00018', args=[argname]))
        # find out whether to force input directory
        force = self.recipe.force_dirs[0]
        # check whether we have a valid directory
        out = valid_directory(params, argname, value, force=force)
        cond, directory, emsgs = out
        # if we have found directory return directory
        if cond:
            return directory
        else:
            # get input dir
            # noinspection PyProtectedMember
            input_dir = self.recipe.get_input_dir()
            # get listing message
            lmsgs = _print_list_msg(self.recipe, input_dir, dircond=True,
                                    return_string=True)
            # combine emsgs and lmsgs
            wmsgs = []
            for it in range(len(emsgs.keys)):
                wmsgs += [textdict[emsgs.keys[it]].format(*emsgs.args[it])]
            for lmsg in lmsgs:
                wmsgs += ['\n' + lmsg]
            # log messages
            WLOG(params, 'error', wmsgs)

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

    def _check_files(self, value: Any,
                     current_typelist: Union[None, List[Any]] = None,
                     current_filelist: Union[None, List[str]] = None
                     ) -> Tuple[List[str], List[Any]]:
        """
        Check the values of the files are valid - raise exception if not
        valid, else return the value

        :param value: Any, the value to test whether valid for directory
        argument
        :param current_typelist: list of DrsFile types or None
        :param current_filelist: list of string file paths or None

        :return: the valid filename and its DrsFile instance
                 (raises exception if invalid)
        :raises: drs_exceptions.LogExit
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_check_files', __NAME__,
                         self.class_name)
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            # if we have string return it in list form and one None
            if isinstance(value, str):
                return [value], [None]
            # if we have a list return it and a set of Nones
            else:
                return value, [None] * len(value)
        # ---------------------------------------------------------------------
        # check if "directory" is in namespace
        if self.directory is not None:
            directory = self.directory
        else:
            directory = getattr(self.namespace, 'directory', '')
        # get the argument name
        argname = self.dest
        # get the params from recipe
        params = self.recipe.drs_params
        # debug checking output
        WLOG(params, 'debug', TextEntry('90-001-00019', args=[argname]))
        # get recipe args and kwargs
        rargs = self.recipe.args
        rkwargs = self.recipe.kwargs
        force_input_dir = self.recipe.force_dirs[0]
        input_dir = self.recipe.inputdir
        # check if files are valid
        out = valid_files(params, argname, value, self.recipe.name,
                          rargs, rkwargs, directory,
                          alltypelist=current_typelist,
                          allfilelist=current_filelist,
                          force=force_input_dir, forced_dir=input_dir)
        cond, files, types, emsgs = out
        # if they are return files
        if cond:
            return files, types
        # else deal with errors
        else:
            # log messages
            WLOG(params, 'error', emsgs, wrap=False)

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
        # if we have a string value just check this one file but make it a
        #  one element list
        elif isinstance(values, str):
            filelist, typelist = self._check_files([values], [], [])
            files, types = filelist, typelist
        # else we have a vector of files check all of them
        elif type(values) in [list, np.ndarray]:
            files, types = [], []
            for value in values:
                filelist, typelist = self._check_files(value, types, files)
                files += filelist
                types += typelist
        # else just try to make if a one element list and check this list of
        #  files for validity
        else:
            filelist, typelist = self._check_files([values], [], [])
            files, types = filelist, typelist
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
            self.recipe.params['DRS_DEBUG'] = value
            # now update constants file
            # spirouConfig.Constants.UPDATE_PP(self.recipe.drs_params)
            # return value
            return value
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
            # now update constants file
            # spirouConfig.Constants.UPDATE_PP(self.recipe.drs_params)
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
            # now update constants file
            # spirouConfig.Constants.UPDATE_PP(self.recipe.drs_params)
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__', __NAME__,
                         self.class_name)
        # get drs parameters
        self.recipe = parser.recipe
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.params, '__call__',
                         __NAME__, self.class_name)
        # get drs parameters
        self.recipe = parser.recipe
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
                # get exception argumnets
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
def get_dir(params: ParamDict, dir_string: str, kind: str = 'input') -> str:
    """
    Get the directory based on "dir_string" (either RAW, TMP, REDUCED)
    obtained via params

    Note if dir_string is full path we do not use path from params

    :param params: ParamDict, parameter dictionary of constants
    :param dir_string: str, either 'RAW', 'TMP' or 'REDUCED' (case insensitive)
    :param kind: str, type of dir for logging (either 'input' or 'output')

    :return: str, the directory path
    """
    # check if path has been set to an absolute path (that exists)
    if os.path.exists(os.path.abspath(dir_string)):
        return os.path.abspath(dir_string)
    # get the input directory from recipe.inputdir keyword
    if dir_string.upper() == 'RAW':
        dirpath = params['DRS_DATA_RAW']
    elif dir_string.upper() == 'TMP':
        dirpath = params['DRS_DATA_WORKING']
    elif dir_string.upper() == 'REDUCED':
        dirpath = params['DRS_DATA_REDUC']
    # if not found produce error
    else:
        emsg = TextEntry('00-007-00002', args=[kind, dir_string])
        WLOG(params, 'error', emsg)
        dirpath = None
    return dirpath


def get_input_dir(params: ParamDict, directory: Union[str, None] = None,
                  force: bool = False,
                  forced_dir: Union[str, None] = str) -> Union[str, None]:
    """
    Get the input directory for this recipe based on what was set in
    initialisation (construction)

    :param params: the Parameter dictionary of constants
    :param directory: None or string - force the input dir (if it exists)
    :param force: bool if True allows force setting
    :param forced_dir: str, if set if the forced dir value to get (can be
                       a full path or 'RAW', 'TMP', 'REDUCED'

    if RAW uses DRS_DATA_RAW from drs_params
    if TMP uses DRS_DATA_WORKING from drs_params
    if REDUCED uses DRS_DATA_REDUC from drs_params

    :return input_dir: string, the input directory
    """
    # set function name
    func_name = display_func(params, 'get_input_dir', __NAME__)
    # deal with manual override of input dir
    if force and (directory is not None) and (os.path.exists(directory)):
        return directory
    # deal with no forced dir set
    if forced_dir is None:
        # raise error
        eargs = ['input', func_name]
        WLOG(params, 'error', TextEntry('00-006-00020', args=eargs))
    # deal with absolute path existing
    if force and os.path.exists(os.path.abspath(forced_dir)):
        return os.path.abspath(forced_dir)
    # check if "input_dir" is in namespace
    input_dir_pick = forced_dir.upper()
    # return input_dir
    return get_dir(params, input_dir_pick, kind='input')


def get_output_dir(params: ParamDict, directory: Union[str, None] = None,
                   force: bool = False,
                   forced_dir: Union[str, None] = str) -> Union[str, None]:
    """
    Get the input directory for this recipe based on what was set in
    initialisation (construction)

    :param params: the Parameter dictionary of constants
    :param directory: None or string - force the output dir (if it exists)
    :param force: bool if True allows force setting
    :param forced_dir: str, if set if the forced dir value to get (can be
                       a full path or 'RAW', 'TMP', 'REDUCED'

    if RAW uses DRS_DATA_RAW from drs_params
    if TMP uses DRS_DATA_WORKING from drs_params
    if REDUCED uses DRS_DATA_REDUC from drs_params

    :return input_dir: string, the input directory
    """
    # set function name
    func_name = display_func(params, 'get_output_dir', __NAME__)
    # deal with manual override of input dir
    if force and (directory is not None) and (os.path.exists(directory)):
        return directory
    # deal with no forced dir set
    if forced_dir is None:
        # raise error
        eargs = ['output', func_name]
        WLOG(params, 'error', TextEntry('00-006-00020', args=eargs))
    # deal with absolute path existing
    if force and os.path.exists(os.path.abspath(forced_dir)):
        return os.path.abspath(forced_dir)
    # check if "input_dir" is in namespace
    output_dir_pick = forced_dir.upper()
    # return input_dir
    return get_dir(params, output_dir_pick, kind='output')


def valid_directory(params: ParamDict, argname: str, directory: Any,
                    force: bool = False, forced_dir: Union[str, None] = None,
                    ) -> Tuple[bool, Union[str, None], Union[TextEntry, str, None]]:
    """
    Find out whether we have a valid directory

    :param params: ParamDict, the parameter dictionary of constants
    :param argname: str, the argumnet name "directory" came from (for error
                    logging)
    :param directory: Any, the value to test whether it is a valid directory)
    :param input_dir_func: Function, the input directory function (must return
                           a string)
    :param force: bool, if True forces the input directory (via input_dir_func)

    :return: tuple: 1. whether directory is valid, 2. the full directory path
             (if passed) or None if failed, 3. the reason for failure (or None
             if passed)
    """
    # get input directory
    input_dir = os.path.realpath(get_input_dir(params, force=force,
                                               forced_dir=forced_dir))
    # ---------------------------------------------------------------------
    # Make sure directory is a string
    if type(directory) not in [str, np.str_]:
        eargs = [argname, directory, type(directory)]
        emsg = TextEntry('09-001-00003', args=eargs)
        return False, None, emsg
    # ---------------------------------------------------------------------
    # step 1: check if directory is full absolute path
    if os.path.exists(directory):
        # log that we found the path (debug mode)
        dmsg = TextEntry('90-001-00001', args=[argname, directory])
        dmsg += TextEntry('')
        WLOG(params, 'debug', dmsg, wrap=False)
        # get the absolute path
        abspath = os.path.abspath(directory)
        # check whether abspath is consistent with input dir from recipe
        #    definitions (this can happen e.g. if in reduced instead of tmp)
        if not abspath.startswith(input_dir):
            # log that directory found not consistent with input path
            dargs = [input_dir]
            WLOG(params, 'debug', TextEntry('90-001-00035', args=dargs))
            pass
        else:
            return True, os.path.abspath(directory), None
    # ---------------------------------------------------------------------
    # step 2: check if directory is in input directory
    input_dir = get_input_dir(params, force=force, forced_dir=forced_dir)
    test_path = os.path.join(input_dir, directory)
    if os.path.exists(test_path):
        dmsg = TextEntry('90-001-00017', args=[argname, directory])
        dmsg += TextEntry('')
        WLOG(params, 'debug', dmsg, wrap=False)
        return True, os.path.abspath(test_path), None
    # ---------------------------------------------------------------------
    # else deal with errors
    eargs = [argname, directory, test_path]
    emsg = TextEntry('09-001-00004', args=eargs)
    # ---------------------------------------------------------------------
    # return False (directory did not pass), no string, and the reason for the
    #  failure
    return False, None, emsg


# define complex return for valid_file
ValidFileType = Tuple[bool, Union[List[str], None],
                      Union[List[DrsInputFile], None], Union[TextEntry, None]]


def valid_file(params: ParamDict, argname: str, filename: str,
               recipename: str, rargs: Dict[str, DrsArgument],
               rkwargs: Dict[str, DrsArgument], directory=None,
               alltypelist: Union[List[DrsInputFile], None] = None,
               allfilelist: Union[List[str], None] = None,
               force: bool = False,
               forced_dir: Union[str, None] = None) -> ValidFileType:
    """
    Test for whether a file is valid

    :param params: ParamDict - parameter dictionary of constants
    :param argname: str, the name of the argument we are testing
    :param filename: string, the filename to test
    :param recipename: str, the recipe name
    :param rargs: dictionary of DrsArguments - the positional arguments
    :param rkwargs: dictionary of DrsArguments - the optional arguments
    :param directory:

    :return cond: bool, if True file is valid, if False file is not valid
    :return filelist: list of strings, list of files found
    :return error: list of strings, if there was an error (cond = False)
                   and return_error=True, return a list of strings
                   describing the error
    """
    # set function name
    func_name = display_func(params, '_valid_file', __NAME__, 'DrsRecipe')
    # deal with no current typelist (alltypelist=None)
    if alltypelist is None:
        alltypelist = []
    if allfilelist is None:
        allfilelist = []
    # get the argument that we are checking the file of
    arg = _get_arg(rargs, rkwargs, argname)
    drsfiles = arg.files
    # get the drs logic
    drs_logic = arg.filelogic
    # deal with arg.path set
    directory = _check_arg_path(params, arg, directory)
    # ---------------------------------------------------------------------
    # Step 1: Check file location is valid
    # ---------------------------------------------------------------------
    # if debug mode print progress
    WLOG(params, 'debug', TextEntry('90-001-00002', args=[filename]),
         wrap=False)
    # perform location check
    out = _check_file_location(params, argname, directory, filename,
                               force=force, forced_dir=forced_dir)
    valid, files, error = out
    if not valid:
        return False, None, None, error
    # perform file/directory check
    out = _check_if_directory(argname, files)
    valid, files, error = out
    if not valid:
        return False, None, None, error
    # ---------------------------------------------------------------------
    # The next steps are different depending on the DRS file and
    # we may have multiple files
    out_files = []
    out_types = []
    # storage of checked files
    checked_files = []
    # storage of errors (if we have no files)
    errors = TextEntry(None)
    # loop around filename
    for filename_it in files:
        # start of with the file not being valid
        valid = False
        # storage of errors (reset)
        errors = TextEntry(None)
        header_errors = dict()
        # add to checked files
        checked_files.append(filename_it)
        # deal with not having any drs files set
        if len(drsfiles) == 0:
            # files must be set
            eargs = [argname, func_name]
            WLOG(params, 'error', TextEntry('00-006-00019', args=eargs))
        # loop around file types
        for drsfile in drsfiles:
            # if in debug mode print progres
            dargs = [drsfile.name, os.path.basename(filename_it)]
            WLOG(params, 'debug', TextEntry('90-001-00008', args=dargs),
                 wrap=False)
            # -------------------------------------------------------------
            # make instance of the DrsFile
            inputdir = get_input_dir(params, force=force, forced_dir=forced_dir)
            # create an instance of this drs_file with the filename set
            file_in = drsfile.newcopy(filename=filename_it, params=params)
            file_in.read_file()
            # set the directory
            fdir = drs_misc.get_uncommon_path(directory, inputdir)
            file_in.directory = fdir
            # -------------------------------------------------------------
            # Step 2: Check extension
            # -------------------------------------------------------------
            # check the extension
            valid1, error1 = file_in.has_correct_extension(argname=argname)
            # -------------------------------------------------------------
            # Step 3: Check file header has required keys
            # -------------------------------------------------------------
            valid2a, error2a = file_in.hkeys_exist(argname=argname)
            # -------------------------------------------------------------
            # Step 4: Check file header has correct required keys
            # -------------------------------------------------------------
            valid2b, error2b = file_in.has_correct_hkeys(argname=argname)
            # -------------------------------------------------------------
            # Step 4: Check exclusivity
            # -------------------------------------------------------------
            # only check if file correct
            if valid1 and valid2a and valid2b:
                exargs = [params, argname, drs_file, recipename, drs_logic,
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
                if error1 is not None:
                    errors += error1
            if (not valid2a) and valid1 and valid3:
                if error2a is not None:
                    errors += error2a
            if valid1 and valid2a:
                if error2b is not None:
                    header_errors[drsfile.name] = error2b
            # only add check3 if check2 was valid
            if (not valid3) and valid2a and valid2b and valid1:
                if error3 is not None:
                    errors += error3
            # check validity and append if valid
            if valid:
                dargs = [argname, os.path.basename(filename_it), file_in]
                wmsg = TextEntry('90-001-00016', args=dargs)
                WLOG(params, 'debug', wmsg, wrap=False)
                # append to out files/types
                out_files.append(filename_it)
                out_types.append(file_in)
                # break out the inner loop if valid (we don't need to
                #    check other drs_files)
                break
        # if this file is not valid we should break here
        if not valid:
            # add header errors (needed outside drs_file loop)
            errors += _gen_header_errors(header_errors)
            # add file error (needed only once per filename)
            eargs = [os.path.abspath(filename_it)]
            errors += '\n' + TextEntry('09-001-00024', args=eargs)
            break
    # must append all files checked
    allfiles = allfilelist + checked_files
    if len(allfiles) > 1:
        errors += '\n' + TextEntry('40-001-00019')
        for filename_it in allfiles:
            errors += TextEntry('\n\t\t{0}'.format(filename_it))
    # ---------------------------------------------------------------------
    # clean up errors (do not repeat same lines)
    cleaned_errors = TextEntry(None)
    for error in errors:
        if error not in cleaned_errors:
            cleaned_errors += error
    # ---------------------------------------------------------------------
    # deal with return types:
    # a. if we don't have the right number of files then we failed
    if len(out_files) != len(files):
        return False, None, None, cleaned_errors
    # b. if we did but expect an error returned return True with an error
    else:
        return True, out_files, out_types, TextEntry(None)


def valid_files(params: ParamDict, argname: str, files: Union[List[str], str],
                recipename: str, rargs: Dict[str, DrsArgument],
                rkwargs: Dict[str, DrsArgument], directory=None,
                alltypelist: Union[List[DrsInputFile], None] = None,
                allfilelist: Union[List[str], None] = None,
                force: bool = False,
                forced_dir: Union[str, None] = None) -> ValidFileType:
    """

    :param params:
    :param argname:
    :param files:
    :param recipename:
    :param rargs:
    :param rkwargs:
    :param directory:
    :param alltypelist:
    :param allfilelist:
    :param force:
    :param forced_dir:
    :return:
    """
    # deal with no current typelist (alltypelist=None)
    if alltypelist is None:
        alltypelist = []
    # deal with no current filelist (allfilelist=None)
    if allfilelist is None:
        allfilelist = []
    # deal with non-lists
    if isinstance(files, str):
        files = [files]
    elif type(files) not in [list, np.ndarray]:
        files = [files]
    # loop around files
    all_files = []
    all_types = []
    for filename in files:
        # check single file
        out = valid_file(params, argname, filename, recipename, rargs, rkwargs,
                         directory, alltypelist=alltypelist,
                         allfilelist=allfilelist, force=force,
                         forced_dir=forced_dir)
        file_valid, filelist, typelist, error = out
        # if single file is not valid return the error (and False)
        if not file_valid:
            return False, None, None, error
        # else we append filelist to all_files
        else:
            all_files += filelist
            all_types += typelist
    # if we are at this point everything passed and file is valid
    return True, all_files, all_types, None


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


# define complex typing for _check_file_location
CheckFileLocType = Tuple[bool, Union[List[str], None],  Union[TextEntry, None]]


def _check_file_location(params: ParamDict, argname: str,
                         directory: Union[str, None], filename: str,
                         force: bool = False,
                         forced_dir: Union[str, None] = None
                         ) -> CheckFileLocType:
    """
    Checks file location is valid on:
        "filename" as full link to file (including wildcards)
        "filename" + recipe.inputdir.upper() (including wildcards)
        "filename" + ".fits" as full link to file (inlcluding wildcards)
        "filename" + ".fits" + recipe.inputdir.upper() (including wildcards)

    :param params: ParamDict, parameter dictionary of constants
    :param argname: str, the argument name
    :param directory: str, the directory name if set (if None uses
    :param filename: string, the filename to test

    :return cond: Tuple - 1. bool, if True file is valid, if False file is
                  not valid 2. list of strings, list of files found, 3.
                  TextEntry, if there was an error return TextEntry describing
                  the error
    """
    output_files = []
    # get input directory
    if directory is not None:
        input_dir = str(directory)
    else:
        # noinspection PyProtectedMember
        input_dir = get_input_dir(params, force=force, forced_dir=forced_dir)
    # -------------------------------------------------------------------------
    # Step 1: check "filename" as full link to file (including wildcards)
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = np.sort(glob.glob(filename))
    # debug output
    if len(raw_files) == 0:
        dargs = [argname, filename]
        WLOG(params, 'debug', TextEntry('90-001-00003', args=dargs),
             wrap=False)
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        dargs = [argname, raw_file]
        WLOG(params, 'debug', TextEntry('90-001-00004', args=dargs),
             wrap=False)
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, None
    # -------------------------------------------------------------------------
    # Step 2: recipe.inputdir.upper() (including wildcards)
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = np.sort(glob.glob(os.path.join(input_dir, filename)))
    # debug output
    if len(raw_files) == 0:
        dargs = [argname, filename]
        WLOG(params, 'debug', TextEntry('90-001-00003', args=dargs),
             wrap=False)
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        dargs = [argname, raw_file]
        WLOG(params, 'debug', TextEntry('90-001-00005', args=dargs),
             wrap=False)
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, None
    # -------------------------------------------------------------------------
    # Step 3: check "filename" as full link to file (including wildcards)
    #         + .fits
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = np.sort(glob.glob(filename + '.fits'))
    # debug output
    if len(raw_files) == 0 and not filename.endswith('.fits'):
        dargs = [argname, filename + '.fits']
        WLOG(params, 'debug', TextEntry('90-001-00003', args=dargs),
             wrap=False)
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        dargs = [argname, raw_file]
        WLOG(params, 'debug', TextEntry('90-001-00006', args=dargs),
             wrap=False)
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, None
    # -------------------------------------------------------------------------
    # Step 4: recipe.inputdir.upper() (including wildcards)
    #         + .fits
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = np.sort(glob.glob(os.path.join(input_dir, filename + '.fits')))
    # debug output
    if len(raw_files) == 0 and not filename.endswith('.fits'):
        dargs = [argname, os.path.join(input_dir, filename + '.fits')]
        WLOG(params, 'debug', TextEntry('90-001-00003', args=dargs),
             wrap=False)
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        dargs = [argname, raw_file]
        WLOG(params, 'debug', TextEntry('90-001-00007', args=dargs),
             wrap=False)
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, None
    # -------------------------------------------------------------------------
    # Deal with cases where we didn't find file
    # -------------------------------------------------------------------------
    eargs = [argname, filename, os.path.join(input_dir, filename)]
    emsg = TextEntry('09-001-00005', args=eargs)
    if not filename.endswith('.fits'):
        fitsfile1 = filename + '.fits'
        fitsfile2 = os.path.join(input_dir, fitsfile1)
        emsg += TextEntry('\t\t"{0}"'.format(fitsfile1))
        emsg += TextEntry('\t\t"{0}"'.format(fitsfile2))
    # return False, no files and error messages
    return False, None, emsg


def _check_if_directory(argname: str, files: List[str]
                        ) -> Tuple[bool, Union[List[str], None],
                                   Union[TextEntry, None]]:
    """
    Simple check to see if each file in files is a directory and then
    checks if file in files is a file with os.path.isfile

    :param argname:
    :param files:
    :return:
    """
    # empty error entry
    emsgs = TextEntry(None)
    # loop around files
    it = 0
    for filename in files:
        # set eargs
        eargs = [argname, filename]
        # check if directory
        if os.path.isdir(filename):
            # Need to add as new line
            if len(emsgs) > 0:
                emsgs += '\n' + TextEntry('09-001-00026', args=eargs)
            else:
                emsgs += TextEntry('09-001-00026', args=eargs)
            continue
        # check if not file (or link to file)
        if not os.path.isfile(filename) and not os.path.islink(filename):
            # Need to add as new line
            if len(emsgs) > 0:
                emsgs += '\n' + TextEntry('09-001-00025', args=eargs)
            else:
                emsgs += TextEntry('09-001-00025', args=eargs)

    # if we have emsgs then we need to get the errors
    if len(emsgs) > 0:
        return False, None, emsgs
    else:
        return True, files, None


def _check_file_exclusivity(params: ParamDict, argname: str,
                            drsfile: DrsInputFile, recipename: str,
                            logic: str, otypes: List[DrsInputFile],
                            allotypes: Union[List[DrsInputFile], None] = None
                            ) -> Tuple[bool, Union[TextEntry, None]]:
    """
    Check the file exclusivity of a drsfile

    i.e. if logic = 'exclusive'
    then names of drsfile must match (i.e. from the same instance)
    i.e. if logic = 'inclusive'
    then any drsfile name allowed

    :param params: ParamDict, parameter dictionary of constants
    :param argname: str, the argument name this was called from
    :param drsfile: DrsInputFile, the drs file instance to check for exclusivity
    :param recipename: str, the name of the recipe (for logging)
    :param logic: str, either 'exclusive' or 'inclusive' if 'exclusive' checks
                  that drsfile.name matches
    :param otypes: list of DrsInputFile instances - the current set of instances
                   (combined with allotypes to check for exclusivity)
    :param allotypes: list of DrsInputfile instances - the global set of
                      instance for this argument (combiend with otypes to check
                      for exclusivity)
    :return: tuple, 1. flag whether drsfile passes (True/False), 2. the reason
             why drsfile failed (if it failed) otherwise None
    """
    # deal with no alltypelist
    if allotypes is None:
        allotypes = list(otypes)
    else:
        allotypes = list(allotypes) + list(otypes)

    # if we have no files yet we don't need to check exclusivity
    if len(allotypes) == 0:
        dargs = [argname, drsfile.name]
        WLOG(params, 'debug', TextEntry('90-001-00013', args=dargs),
             wrap=False)
        return True, None
    # if argument logic is set to "exclusive" we need to check that the
    #   drs_file.name is the same for this as the last file in outtypes
    if logic == 'exclusive':
        # match by name of drs_file
        cond = drsfile.name == allotypes[-1].name
        # if condition not met return False and error
        if not cond:
            eargs = [argname, drsfile.name, allotypes[-1].name]
            emsg = TextEntry('09-001-00008', args=eargs)
            return False, emsg
        # if condition is met return True and empty error
        else:
            dargs = [argname, drsfile.name]
            WLOG(params, 'debug', TextEntry('90-001-00014', args=dargs),
                 wrap=False)
            return True, None
    # if logic is 'inclusive' we just need to return True
    elif logic == 'inclusive':
        WLOG(params, 'debug', TextEntry('90-001-00015', args=[argname]),
             wrap=False)
        return True, None
    # else logic is wrong - raise error
    else:
        eargs = [argname, recipename]
        WLOG(params, 'error', TextEntry('00-006-00004', args=eargs),
             wrap=False)


def _gen_header_errors(header_errors: Dict[str, Dict[str, tuple]]
                       ) -> Union[TextEntry, None]:
    """
    Generate the header error text using the errors give in header_errors
    (a dctionary of drsfile names each with a dictionary of keys)
    i.e.
    header_errors[drsname1] = dict(KW_XXX=(found, argname, rvalue, value),
                                   KW_YYY=(found, argname, rvalue, value))

    where
        - found is True or False (whether header key was found)
        - argname is a str, the argument name this belongs to
        - rvalue is the required value (fails if incorrect)
        - value is value in the header

    :param header_errors: the header dictionary of dictionarys (see description
                          above)

    :return: combined TextEntry (if errors exist  or None)
    """
    # set up message storage
    emsgs = TextEntry(None)
    # set up initial argname
    argname = ''
    # check if file passed (all header_errors are True) - skip if passed
    for drsfilename in header_errors.keys():
        passed = True
        for key in header_errors[drsfilename]:
            passed &= header_errors[drsfilename][key][0]
        if passed:
            return None
    # loop around drs files in header_errors
    for drsfilename in header_errors.keys():
        # get this iterations values in this drs_file
        header_error = header_errors[drsfilename]
        # append this file
        emsgs += '\n' + TextEntry('09-001-00021', args=[drsfilename])
        # loop around keys in this drs_file
        for key in header_error:
            # get this iterations entry
            entry = header_error[key]
            # get the argname
            argname = entry[1]
            # construct error message
            eargs = [key, entry[3], entry[2]]
            if not entry[0]:
                emsgs += '\n' + TextEntry('09-001-00022', args=eargs)
    if len(emsgs) > 0:
        emsg0 = TextEntry('09-001-00023', args=[argname])
    else:
        emsg0 = TextEntry(None)
    # return TextEntry (of combined TextEntrys)
    return emsg0 + emsgs


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
