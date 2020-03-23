#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-02-04 at 16:40

@author: cook
"""
import numpy as np
import argparse
import sys
import os
import copy
from collections import OrderedDict

from apero.core.instruments.default import pseudo_const
from apero.core import constants
from apero.locale import drs_text
from apero.core.core import drs_log

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_argument.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = drs_log.wlog
display_func = drs_log.display_func
# get print colours
COLOR = pseudo_const.Colors()
# get param dict
ParamDict = constants.ParamDict
# get the config error
ConfigError = constants.ConfigError
ArgumentError = constants.ArgumentError
# Get the text types
TextEntry = drs_text.TextEntry
TextDict = drs_text.TextDict
HelpText = drs_text.HelpDict
# define display strings for types
STRTYPE = OrderedDict()
STRTYPE[int] = 'int'
STRTYPE[float] = 'float'
STRTYPE[str] = 'str'
STRTYPE[complex] = 'complex'
STRTYPE[list] = 'list'
STRTYPE[np.ndarray] = 'np.ndarray'
# define types that we can do min and max on
NUMBER_TYPES = [int, float]
# define name of index file
INDEX_FILE = Constants['DRS_INDEX_FILE']
INDEX_FILE_NAME_COL = Constants['DRS_INDEX_FILENAME']


# =============================================================================
# Define ArgParse Parser and Action classes
# =============================================================================
# Adapted from: https://stackoverflow.com/a/16942165
class DrsArgumentParser(argparse.ArgumentParser):
    def __init__(self, recipe, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, 'DRSArgumentParser')
        # define the recipe
        self.recipe = recipe
        # get the recipes parameter dictionary
        params = self.recipe.drs_params
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

    def parse_args(self, args=None, namespace=None):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, 'parse_args', __NAME__,
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

    def error(self, message):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, 'error', __NAME__,
                         'DRSArgumentParser')
        # self.print_help(sys.stderr)
        # self.exit(2, '%s: error: %s\n' % (self.prog, message))
        # get parameterse from drs_params
        program = str(self.recipe.drs_params['RECIPE'])
        # get parameters from drs_params
        params = self.recipe.drs_params
        # log message
        emsg_args = [message, program]
        emsg_obj = TextEntry('09-001-00001', args=emsg_args)
        WLOG(params, 'error', emsg_obj)

    def _print_message(self, message, file=None):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_print_message', __NAME__,
                         'DRSArgumentParser')
        # get parameters from drs_params
        params = self.recipe.drs_params
        program = str(params['RECIPE'])
        # construct error message
        if self.recipe.drs_params['DRS_COLOURED_LOG']:
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
        imsgs = _get_version_info(self.recipe.drs_params, green, end)
        for imsg in imsgs:
            print(imsg)
        print()
        print(blue + self.format_help() + end)

    def format_usage(self):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, 'format_usage', __NAME__,
                         'DRSArgumentParser')
        # noinspection PyProtectedMember
        return_string = (' ' + self.helptext['USAGE_TEXT'] + ' ' +
                         self.recipe._drs_usage())
        # return messages
        return return_string

    def format_help(self):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, 'format_help', __NAME__,
                         'DRSArgumentParser')
        # empty help message at intialization
        hmsgs = []
        # noinspection PyProtectedMember
        hmsgs += [' ' + self.helptext['USAGE_TEXT'] + ' ' +
                  self.recipe._drs_usage()]
        # add description
        if self.recipe.description is not None:
            # add header line
            hmsgs += ['', self.recipe.drs_params['DRS_HEADER']]
            # add description title
            hmsgs += [' ' + self.helptext['DESCRIPTION_TEXT']]
            # add header line
            hmsgs += [self.recipe.drs_params['DRS_HEADER'], '']
            # add description text
            hmsgs += [' ' + self.recipe.description]
            # add header line
            hmsgs += [self.recipe.drs_params['DRS_HEADER']]
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
            hmsgs += ['', self.recipe.drs_params['DRS_HEADER']]
            hmsgs += [' ' + self.helptext['EXAMPLES_TEXT']]
            hmsgs += [self.recipe.drs_params['DRS_HEADER'], '']
            hmsgs += [' ' + self.recipe.epilog]
            hmsgs += [self.recipe.drs_params['DRS_HEADER']]
        # return string
        return_string = ''
        for hmsg in hmsgs:
            return_string += hmsg + '\n'

        # return messages
        return return_string

    def _has_special(self):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_has_special', __NAME__,
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, 'DrsAction')
        # run the argument parser (super)
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """
        :param parser: 
        :param namespace: 
        :param values: 
        :param option_string: 
        
        :type parser: DrsArgumentParser
        :return: 
        """
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__call__', __NAME__, 'DrsAction')
        # raise not implemented error
        raise NotImplementedError(_('.__call__() not defined'))


class _CheckDirectory(DrsAction):
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_CheckDirectory')
        # set the recipe and parser to None
        self.recipe = None
        self.parser = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _check_directory(self, value):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_check_directory', __NAME__,
                         '_CheckDirectory')
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return value
        # ---------------------------------------------------------------------
        # get the argument name
        argname = self.dest
        # get the params from recipe
        params = self.recipe.drs_params
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # debug checking output
        if params['DRS_DEBUG'] > 0:
            print('')
        WLOG(params, 'debug', TextEntry('90-001-00018', args=[argname]))
        # noinspection PyProtectedMember
        out = self.recipe.valid_directory(argname, value, return_error=True)
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

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        self.parser = parser
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_CheckDirectory')
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_CheckFiles')
        # get the recipe, namespace and directory (if not added set to None)
        self.recipe = kwargs.get('recipe', None)
        self.namespace = kwargs.get('namespace', None)
        self.directory = kwargs.get('directory', None)
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _check_files(self, value, current_typelist=None, current_filelist=None):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_check_files', __NAME__,
                         '_CheckFiles')
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
        # check if files are valid
        # noinspection PyProtectedMember
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
            WLOG(params, 'error', emsgs, wrap=False)

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        self.parser = parser
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_CheckFiles')
        # store the namespace
        self.namespace = namespace
        # check for help
        # noinspection PyProtectedMember
        skip = parser._has_special()
        if skip:
            return 0
        elif isinstance(values, str):
            filelist, typelist = self._check_files([values], [], [])
            files, types = filelist, typelist
        elif type(values) in [list, np.ndarray]:
            files, types = [], []
            for value in values:
                filelist, typelist = self._check_files(value, types, files)
                files += filelist
                types += typelist
        else:
            filelist, typelist = self._check_files([values], [], [])
            files, types = filelist, typelist
        # Add the attribute
        setattr(namespace, self.dest, [files, types])


class _CheckBool(DrsAction):
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_CheckBool')
        # define recipe as unset
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _check_bool(self, value):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_check_bool', __NAME__,
                         '_CheckBool')
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return value
        # ---------------------------------------------------------------------
        # get parameters
        params = self.recipe.drs_params
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

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_CheckType')
        # define recipe as None
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _eval_type(self, value):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_eval_type', __NAME__,
                         '_CheckType')
        # get parameters
        params = self.recipe.drs_params
        # get type error
        eargs = [self.dest, value, self.type]
        try:
            return self.type(value)
        except ValueError as _:
            WLOG(params, 'error', TextEntry('09-001-00014', args=eargs))
        except TypeError as _:
            WLOG(params, 'error', TextEntry('09-001-00015', args=eargs))

    def _check_type(self, value):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_check_type', __NAME__,
                         '_CheckType')
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return value
        # ---------------------------------------------------------------------
        # get parameters
        params = self.recipe.drs_params
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

    def _check_limits(self, values):
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.drs_params, '_check_type',
                                 __NAME__, '_CheckType')
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return values
        # ---------------------------------------------------------------------
        # get parameters
        params = self.recipe.drs_params
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

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_check_type', __NAME__,
                         '_CheckType')
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_CheckOptions')
        # define recipe as None (overwritten by __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _check_options(self, value):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_check_options', __NAME__,
                         '_CheckOptions')
        # ---------------------------------------------------------------------
        # deal with no check
        if not self.recipe.input_validation:
            return value
        # ---------------------------------------------------------------------
        # get parameters
        params = self.recipe.drs_params
        # check options
        if value in self.choices:
            return value
        else:
            eargs = [self.dest, ' or '.join(self.choices), value]
            WLOG(params, 'error', TextEntry('09-001-00019', args=eargs))

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
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

    def _display_listing(self, namespace):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_display_listing', __NAME__,
                         '_MakeListing')
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

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_MakeListing')
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
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_MakeAllListing')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # define name space as None (overwritten in __call__)
        self.namespace = None
        # define parse as None (overwritten in __call__)
        self.parser = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _display_listing(self, namespace):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_display_listing', __NAME__,
                         '_MakeAllListing')
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

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_ActivateDebug')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _set_debug(self, values, recipe=None):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_set_debug', __NAME__,
                         '_ActivateDebug')
        # get params
        params = self.recipe.drs_params
        # deal with using without call
        if self.recipe is None:
            self.recipe = recipe
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
            self.recipe.drs_params['DRS_DEBUG'] = value
            # now update constants file
            # spirouConfig.Constants.UPDATE_PP(self.recipe.drs_params)
            # return value
            return value
        except:
            eargs = [self.dest, values]
            WLOG(params, 'error', TextEntry('09-001-00020', args=eargs))

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_ActivateDebug')
        # display listing
        if type(values) == list:
            value = list(map(self._set_debug, values))
        else:
            value = self._set_debug(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _DisplayVersion(DrsAction):
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_DisplayVersion')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _display_version(self):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_display_version', __NAME__,
                         '_DisplayVersion')
        # get params
        params = self.recipe.drs_params
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

    def __call__(self, parser, namespace, values, option_string=None):
        # set recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_DisplayVersion')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()

        # display version
        self._display_version()
        # quit after call
        parser.exit()


class _DisplayInfo(DrsAction):
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_DisplayInfo')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _display_info(self):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_display_info', __NAME__,
                         '_DisplayInfo')
        # get params
        recipe = self.recipe
        params = recipe.drs_params
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

    def __call__(self, parser, namespace, values, option_string=None):
        # set recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_SetProgram')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _set_program(self, values):
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.drs_params, '_set_program',
                                 __NAME__, '_SetProgram')
        # deal with difference datatypes for values
        if isinstance(values, list):
            strvalue = values[0]
        elif isinstance(values, np.ndarray):
            strvalue = values[0]
        else:
            strvalue = str(values)
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00031', args=[strvalue])
        WLOG(self.recipe.drs_params, 'debug', dmsg)
        # set DRS_DEBUG (must use the self version)
        self.recipe.drs_params['DRS_USER_PROGRAM'] = strvalue
        self.recipe.drs_params.set_source('DRS_USER_PROGRAM', func_name)
        self.recipe.drs_params.set_instance('DRS_USER_PROGRAM', None)
        # return strvalue
        return strvalue

    def __call__(self, parser, namespace, values, option_string=None):
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_SetProgram')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_program(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _SetIPythonReturn(DrsAction):
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_SetIPythonReturn')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _set_return(self, _):
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.drs_params, '_set_return',
                                 __NAME__, '_SetIPythonReturn')
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00032')
        WLOG(self.recipe.drs_params, 'debug', dmsg)
        # set DRS_DEBUG (must use the self version)
        self.recipe.drs_params['IPYTHON_RETURN'] = True
        self.recipe.drs_params.set_source('IPYTHON_RETURN', func_name)
        self.recipe.drs_params.set_instance('IPYTHON_RETURN', None)
        # return strvalue
        return True

    def __call__(self, parser, namespace, values, option_string=None):
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_SetIPythonReturn')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_return(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _Breakpoints(DrsAction):
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_Breakpoints')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _set_return(self, _):
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.drs_params, '_set_return',
                                 __NAME__, '_Breakpoints')
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00033')
        WLOG(self.recipe.drs_params, 'debug', dmsg)
        # set DRS_DEBUG (must use the self version)
        self.recipe.drs_params['ALLOW_BREAKPOINTS'] = True
        self.recipe.drs_params.set_source('ALLOW_BREAKPOINTS', func_name)
        self.recipe.drs_params.set_instance('ALLOW_BREAKPOINTS', None)
        # return strvalue
        return True

    def __call__(self, parser, namespace, values, option_string=None):
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_Breakpoints')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_return(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _Breakfunc(DrsAction):
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_Breakfunc')
        # set recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _set_breakfunc(self, value):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_set_breakfunc',
                         __NAME__, '_Breakfunc')
        # deal with unset value
        if value is None:
            return None
        else:
            return str(value)

    def __call__(self, parser, namespace, values, option_string=None):
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_IsMaster')
        # define recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _set_master(self, _):
        # set function name (cannot break here --> no access to inputs)
        func_name = display_func(self.recipe.drs_params, '_set_master',
                                 __NAME__, '_IsMaster')
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00033')
        WLOG(self.recipe.drs_params, 'debug', dmsg)
        # set DRS_DEBUG (must use the self version)
        self.recipe.drs_params['IS_MASTER'] = True
        self.recipe.drs_params.set_source('IS_MASTER', func_name)
        self.recipe.drs_params.set_instance('IS_MASTER', None)
        # return strvalue
        return True

    def __call__(self, parser, namespace, values, option_string=None):
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_IsMaster')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_master(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class _SetQuiet(DrsAction):
    def __init__(self, *args, **kwargs):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, '_SetQuiet')
        # set recipe as None (overwritten in __call__)
        self.recipe = None
        # force super initialisation
        DrsAction.__init__(self, *args, **kwargs)

    def _set_return(self, _):
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '_set_return', __NAME__,
                         '_SetQuiet')
        # debug message: setting program to: "strvalue"
        dmsg = TextEntry('90-001-00034')
        WLOG(self.recipe.drs_params, 'debug', dmsg)
        # return strvalue
        return True

    def __call__(self, parser, namespace, values, option_string=None):
        # get recipe from parser
        self.recipe = parser.recipe
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(self.recipe.drs_params, '__call__', __NAME__,
                         '_SetQuiet')
        # check for help
        # noinspection PyProtectedMember
        parser._has_special()
        # display version
        value = self._set_return(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


# =============================================================================
# Define Argument Class
# =============================================================================
class DrsArgument(object):
    def __init__(self, name=None, kind=None, **kwargs):
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
        # set function name (cannot break here --> no access to inputs)
        _ = display_func(None, '__init__', __NAME__, 'DrsArgument')
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
            emsg = '"kind" must be "arg" or "kwarg" or "special"'
            self.exception(emsg)
        # ------------------------------------------------------------------
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
        # define the input path for files
        self.path = kwargs.get('path', None)
        # get limit
        self.limit = kwargs.get('limit', None)
        # get limits
        self.minimum = kwargs.get('minimum', None)
        self.maximum = kwargs.get('maximum', None)
        # get file logic
        self.filelogic = kwargs.get('filelogic', 'inclusive')
        if self.filelogic not in ['inclusive', 'exclusive']:
            # Get text for default language/instrument
            text = TextDict('None', 'None')
            # get entry to log error
            ee = TextEntry('00-006-00008', args=[self.filelogic])
            self.exception(None, errorobj=[ee, text])
        # deal with no default/default_ref for kwarg
        if kind == 'kwarg':
            # get entry
            if ('default' not in kwargs) and ('default_ref' not in kwargs):
                # Get text for default language/instrument
                text = TextDict('None', 'None')
                # get entry to log error
                ee = TextEntry('00-006-00009', args=self.filelogic)
                self.exception(None, errorobj=[ee, text])
        # get default
        self.default = kwargs.get('default', None)
        # get default_ref
        self.default_ref = kwargs.get('default_ref', None)

        # get required
        if self.kind == 'arg':
            self.required = kwargs.get('required', True)
        else:
            self.required = kwargs.get('required', False)
        # get whether we need this arguement for processing scripts
        self.reprocess = kwargs.get('reprocess', False)

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
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, 'assign_properties', __NAME__, 'DrsArgument')
        # loop around properties
        for prop in self.propkeys:
            if prop in props:
                self.props[prop] = props[prop]

    def exception(self, message=None, errorobj=None):
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

    def copy(self, argument):
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, 'copy', __NAME__, 'DrsArgument')
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
                # copy attributes from drsfile
                newdrsfile = drsfile.completecopy(drsfile)
                # append to files
                self.files.append(newdrsfile)
        # else assume file is a single file (but put it into a list any way)
        else:
            drsfile = argument.files
            self.files = [drsfile.completecopy(drsfile)]
        # copy the path
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

    def __str__(self):
        """
        Defines the str(DrsArgument) return for DrsArgument
        :return str: the string representation of DrSArgument
                     i.e. DrsArgument[name]
        """
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, '__str__', __NAME__, 'DrsArgument')
        # return string representation
        return self.__repr__()

    def __repr__(self):
        """
        Defines the print(DrsArgument) return for DrsArgument
        :return str: the string representation of DrSArgument
                     i.e. DrsArgument[name]
        """
        # set function name (cannot break here --> no access to params)
        _ = display_func(None, '__str__', __NAME__, 'DrsArgument')
        # return string representation
        return 'DrsArgument[{0}]'.format(self.name)


# =============================================================================
# Worker functions
# =============================================================================
def _get_version_info(params, green='', end=''):
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


def _help_format(keys, helpstr, options=None):
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
        helpstrs = _textwrap(helpstr, maxsize)
    else:
        helpstrs = [helpstr]

    # add start separation
    for hstr in helpstrs:
        fmtstring += '\n' + ' ' * sep + hstr

    # return formatted string
    return fmtstring


def _textwrap(input_string, length):
    # set function name (cannot break here --> no access to params)
    _ = display_func(None, '_textwrap', __NAME__)
    # return text wrap
    return constants.constant_functions.textwrap(input_string, length)


def _print_list_msg(recipe, fulldir, dircond=False, return_string=False,
                    list_all=False):
    """
    Prints the listing message (using "get_file_list")

    :param recipe: DrsRecipe instance
    :param fulldir: string, the full "root" (top level) directory
    :param dircond: bool, if True only prints directories (passed to
                    get_file_list)
    :param return_string: bool, if True returns string output instead of
                          printing
    :param list_all: bool, if True overrides lmit (set by HARD_DISPLAY_LIMIT)
    :return:
    """
    # get params from recipe
    params = recipe.drs_params
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


def _get_file_list(limit, path, ext=None, recursive=False,
                   dir_only=False, list_all=False):
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

    :return file_list: list of strings, the files found with extension (if not
                       None, up to the number limit
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
                directory = get_uncommon_path(root, path) + os.sep
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
                directory = get_uncommon_path(root, path) + os.sep
                # append to list
                file_list.append(level + levelsep + directory)

    # if empty list add none found
    if len(file_list) == 0:
        file_list = ['No valid files found.']
    # return file_list
    return file_list, limit_reached


def get_uncommon_path(path1, path2):
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
    # set function name (cannot break here --> no access to params)
    _ = display_func(None, 'get_uncommon_path', __NAME__)
    # get common path
    common = os.path.commonpath([path2, path1]) + os.sep
    # return the non-common part of the path
    return path1.split(common)[-1]


# =============================================================================
# Make functions
# =============================================================================
def make_listing(params):
    """
    Make a custom special argument: Sets whether to display listing files
    up to DRS_MAX_IO_DISPLAY_LIMIT in number.

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_listing', __NAME__)
    # define the listing limit (used in listing help
    limit = params['DRS_MAX_IO_DISPLAY_LIMIT']
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def make_alllisting(params):
    """
    Make a custom special argument: Sets whether to display all listing files

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_alllisting', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def make_debug(params):
    """
    Make a custom special argument: Sets which debug mode to be in

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_debug', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def make_version(params):
    """
    Make a custom special argument: Whether to display drs version information

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_version', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def make_info(params):
    """
    Make a custom special argument: Whether to display recipe information

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_info', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def set_program(params):
    """
    Make a custom special argument: Set the program name

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'set_program', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def set_ipython_return(params):
    """
    Make a custom special argument: Set the use of ipython return after
    script ends

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'set_ipython_return', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def breakpoints(params):
    """
    Make a custom special argument: Set the use of break_point

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'breakpoints', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def is_master(params):
    """
    Make a custom special argument: Set the use of break_point

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'breakpoints', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
    # set up an output storage dictionary
    props = OrderedDict()
    # set the argument name
    props['name'] = '--master'
    # set any argument alternative names
    props['altnames'] = []
    # set the argument action function
    props['action'] = _IsMaster
    # set the number of argument to expect
    props['nargs'] = 0
    # set the help message
    props['help'] = htext['IS_MASTER_HELP']
    # return the argument dictionary
    return props


def make_breakfunc(params):
    """
    Make a custom special argument: Set a break function

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name
    _ = display_func(params, 'make_breakfunc', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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


def set_quiet(params):
    """
    Make a custom special argument: Set the quiet mode

    :param params: ParamDict, Parameter Dictionary of constants
    :type params: ParamDict

    :return: an ordered dictionary with argument parameters
    :rtype: OrderedDict
    """
    # set function name (cannot break here --> no access to params)
    _ = display_func(params, 'set_quiet', __NAME__)
    # get the help text dictionary
    htext = drs_text.HelpDict(params['INSTRUMENT'], params['LANGUAGE'])
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
