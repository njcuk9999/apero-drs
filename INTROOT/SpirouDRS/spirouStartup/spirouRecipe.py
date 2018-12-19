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
import argparse
import sys
import os
import glob
from collections import OrderedDict

from SpirouDRS import spirouCore
from SpirouDRS import spirouConfig
from . import spirouFile

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_recipe.py'
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
HARD_DISPLAY_LIMIT = 99
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

DEBUG = True
# -----------------------------------------------------------------------------


# =============================================================================
# Define ArgParse Parser and Action classes
# =============================================================================
# Adapted from: https://stackoverflow.com/a/16942165
class DRSArgumentParser(argparse.ArgumentParser):
    def __init__(self, recipe, **kwargs):
        self.recipe = recipe
        argparse.ArgumentParser.__init__(self, **kwargs)

    def error(self, message):
        # self.print_help(sys.stderr)
        # self.exit(2, '%s: error: %s\n' % (self.prog, message))

        # get parameters from drs_params
        params = self.recipe.drs_params
        # construct error message
        underline = COLOR.UNDERLINE
        if self.recipe.drs_params['COLOURED_LOG']:
            red, end = COLOR.RED1, COLOR.ENDC
            yellow, blue = COLOR.YELLOW1, COLOR.BLUE1
        else:
            red, end = COLOR.ENDC, COLOR.ENDC
            yellow, blue = COLOR.ENDC, COLOR.ENDC
        # Manually print error message (with help)
        print()
        print(red + underline + 'Argument Error:' + end)
        print()
        print(COLOR.warning + message + end)
        print()
        print(blue + self.format_help() + end)
        # log message (without print)
        emsg1 = '\nArgument Error:'
        emsg2 = '\t {0}'.format(message)
        WLOG(params, 'error', [emsg1, emsg2], logonly=True)

    def _print_message(self, message, file=None):
        # get parameterse from drs_params
        program = self.recipe.drs_params['RECIPE']
        # construct error message
        underline = COLOR.UNDERLINE
        if self.recipe.drs_params['COLOURED_LOG']:
            green, end = COLOR.GREEN1, COLOR.ENDC
            yellow, blue = COLOR.YELLOW1, COLOR.BLUE1
        else:
            green, end = COLOR.ENDC, COLOR.ENDC
            yellow, blue = COLOR.ENDC, COLOR.ENDC
        # Manually print error message (with help)
        print()
        print(green + underline + 'Help for: {0}.py'.format(program) + end)
        print()
        print(blue + self.format_help() + end)

    def has_help(self):
        if '-h' in sys.argv:
            self.print_help()
            # quit after call
            self.exit()
        if '--help' in sys.argv:
            self.print_help()
            # quit after call
            self.exit()
        if '--listing' in sys.argv:
            return True
        else:
            return False


class CheckDirectory(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_directory(self, value):
        out = self.recipe.valid_directory(value, return_error=True)
        cond, directory, emsgs = out
        if cond:
            return directory
        else:
            WLOG(self.recipe.drs_params, 'error', emsgs)


    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # check for help
        skip = parser.has_help()
        if skip:
            return 0
        if type(values) == list:
            value = list(map(self.check_directory, values))[0]
        else:
            value = self.check_directory(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class CheckFiles(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        self.namespace = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_files(self, value, current_typelist=None):
        # check if "directory" is in namespace
        directory = getattr(self.namespace, 'directory', '')
        # get the argument name
        argname = self.dest
        # check if files are valid
        out = self.recipe.valid_files(argname, value, directory,
                                      return_error=True,
                                      alltypelist=current_typelist)
        cond, files, types, emsgs = out
        # if they are return files
        if cond:
            return files, types
        # else deal with errors
        else:
            WLOG(self.recipe.drs_params, 'error', emsgs)

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # store the namespace
        self.namespace = namespace
        # check for help
        skip = parser.has_help()
        if skip:
            return 0
        if type(values) in [list, np.ndarray]:
            files, types = [], []
            for value in values:
                filelist, typelist = self.check_files(value, types)
                files += filelist
                types += typelist
        else:
            filelist, typelist = self.check_files(values, [])
            files, types = filelist, typelist
        # Add the attribute
        setattr(namespace, self.dest, [files, types])


class CheckBool(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_bool(self, value):
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
        skip = parser.has_help()
        if skip:
            return 0
        if type(values) == list:
            value = list(map(self.check_bool, values))
        else:
            value = self.check_bool(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class CheckType(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def eval_type(self, value):
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

    def check_type(self, value):
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
                return self.eval_type(value[0])
        # else if we have a list we should iterate
        elif type(value) is list:
            values = []
            for it in self.nargs:
                values.append(self.eval_type(values[it]))
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
        skip = parser.has_help()
        if skip:
            return 0
        if self.nargs == 1:
            value = self.check_type(values)
        elif type(values) == list:
            value = list(map(self.check_type, values))
        else:
            value = self.check_type(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class CheckOptions(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def check_options(self, value):
        # get parameters
        params = self.recipe.drs_params
        # check options
        if value in self.choices:
            return value
        else:
            emsg1 = 'Arguement "{0}" must be {1}'
            eargs1 = [self.dest, ' or '.join(self.choices)]
            emsg2 = '\tCurrent value = {0}'.format(value)
            WLOG(params, 'error', [emsg1.format(*eargs1), emsg2])

    def __call__(self, parser, namespace, values, option_string=None):
        # get drs parameters
        self.recipe = parser.recipe
        # check for help
        skip = parser.has_help()
        if skip:
            return 0
        if type(values) == list:
            value = list(map(self.check_options, values))
        else:
            value = self.check_options(values)
        # Add the attribute
        setattr(namespace, self.dest, value)


class MakeListing(argparse.Action):
    def __init__(self, *args, **kwargs):
        self.recipe = None
        self.namespace = None
        # force super initialisation
        argparse.Action.__init__(self, *args, **kwargs)

    def display_listing(self, namespace):
        # get input dir
        input_dir = self.recipe.get_input_dir()
        # check if "directory" is in namespace
        directory = getattr(namespace, 'directory', '')
        # deal with non set directory
        if directory is None:
            directory = ''
        # create full dir path
        fulldir = os.path.join(input_dir, directory)
        # generate a file list
        filelist = get_file_list(fulldir, recursive=True)
        # construct log message
        wmsg = 'Displaying first {0} files in directory="{1}"'
        wmsgs = ['', wmsg.format(HARD_DISPLAY_LIMIT, fulldir), '']
        for filename in filelist:
            wmsgs.append('\t' + filename)
        WLOG(self.recipe.drs_params, '', wmsgs)

    def __call__(self, parser, namespace, values, option_string=None):
        # check for help
        parser.has_help()
        # get drs parameters
        self.recipe = parser.recipe
        # display listing
        self.display_listing(namespace)
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
            self.props['action'] = CheckFiles
            self.props['nargs'] = '+'
            self.props['type'] = str
        elif self.dtype == 'file':
            self.props['action'] = CheckFiles
            self.props['nargs'] = 1
            self.props['type'] = str
        elif self.dtype == 'directory':
            self.props['action'] = CheckDirectory
            self.props['nargs'] = 1
            self.props['type'] = str
        elif self.dtype == 'bool':
            self.props['action'] = CheckBool
            self.props['type'] = str
            self.props['choices'] = ['True', 'False', '1', '0']
        elif self.dtype == 'options':
            self.props['action'] = CheckOptions
            self.props['type'] = str
            self.props['choices'] = self.options
        elif self.dtype == 'switch':
            self.props['action'] = 'store_true'
        elif type(self.dtype) is type:
            self.props['action'] = CheckType
            self.props['type'] = self.dtype
            self.props['nargs'] = 1
        else:
            self.props['type'] = str
            self.props['nargs'] = 1
        # deal with default argument
        if self.default is not None:
            self.props['default'] = self.default
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
        # output directory
        self.outputdir = 'reduced'
        # input directory
        self.inputdir = 'tmp'
        # input type (RAW/REDUCED)
        self.inputtype = 'raw'
        # recipe description
        self.description = 'No description defined'
        # run order
        self.run_order = None
        # define sets of arguments
        self.args = OrderedDict()
        self.kwargs = OrderedDict()
        self.specialargs = OrderedDict()
        # make special arguments
        self.make_specials()
        # define arg list
        self.arg_list = []
        self.str_arg_list = None
        # get drs parameters
        self.drs_params = ParamDict()
        self.input_params = OrderedDict()

    def recipe_setup(self, fkwargs):
        """
        Interface between "recipe", inputs to function ("fkwargs") and argparse
        parser (inputs from command line)

        :param recipe: DrsRecipe instance, the Drs Recipe object
        :param fkwargs: dictionary, a dictionary where the keys match
                        arguments/keyword arguments in recipe (without -/--), and
                        the values are those to set in the output
                        (set to None for not value set)

        :return params:  dictionary, a dictionary where the keys match arguments/
                         keywords (without -/--) and values are the values to be
                         used for this recipe
        """
        # set up storage for arguments
        desc = self.description
        parser = DRSArgumentParser(self, description=desc)
        # deal with function call
        self.parse_args(fkwargs)
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
        Takes all the optional parameters and deals with them.

        :param recipe:
        :param input_parameters:
        :return:
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
        :param dtype: type or None, the type expected for the argument (will
                      raise error if not this type)

        :param default: object or None, the default value for the keyword
                        argument
        :param helpstr: string or  None, the help string
        :param options: list of strings or None: the options allowed for
                        keyword argument
        :param altnames: list of strings or None: alternative names for the
                         reference of the argument

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

    def parse_args(self, dictionary):
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
            self.parse_arg(self.args[argname], values)
        for kwargname in self.kwargs:
            # check if key in dictionary
            if kwargname not in dictionary:
                continue
            # get value(s)
            values = dictionary[kwargname]
            # pass this argument
            self.parse_arg(self.kwargs[kwargname], values)
        # check if we have parameters
        if len(self.str_arg_list) == 0:
            self.str_arg_list = None

    def parse_arg(self, arg, values):
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

    def make_specials(self):
        """
        Make special arguments based on pre-defined static properties
        (i.e. a valid kwargs for parser.add_argument)

        Currently adds the following special arguments:

        --listing, --list     List the files in the given input directory

        :return None:
        """
        # make listing functionality
        listingprops = make_listing()
        name = listingprops['name']
        listing = DrsArgument(name, kind='special',
                              altnames=listingprops['altnames'])
        listing.assign_properties(listingprops)
        self.specialargs[name] = listing

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
        self.drs_params = load_other_config_file(self.drs_params, 'ICDP_NAME',
                                                 required=True, logthis=logthis)
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

    def valid_directory(self, directory, return_error=False):

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
        input_dir = self.get_input_dir()
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

    def valid_files(self, argname, files, directory=None, return_error=False,
                    alltypelist=None):
        # deal with no current typelist (alltypelist=None)
        if alltypelist is None:
            alltypelist = []
        # deal with non-lists
        if type(files) not in [list, np.ndarray]:
            files = [files]
        # loop around files
        all_files = []
        all_types = []
        for filename in files:
            # check single file
            out = self.valid_file(argname, filename, directory, True,
                                  alltypelist=alltypelist)
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

    def valid_file(self, argname, filename, directory=None, return_error=False,
                   alltypelist=None):
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
        # get the argument that we are checking the file of
        arg = get_arg(self, argname)
        drs_files = arg.files
        drs_logic = arg.filelogic
        # storage of errors
        errors = []
        # ---------------------------------------------------------------------
        # Step 1: Check file location is valid
        # ---------------------------------------------------------------------
        # if debug mode print progress
        if DEBUG:
            dmsg = 'DEBUG: Checking file locations for "{0}"'
            WLOG(params, 'info', dmsg.format(filename))
        # perform check
        out = check_file_location(self, argname, directory, filename)
        valid, files, error = out
        if not valid:
            if return_error:
                return False, None, None, error
            else:
                return False, None, None
        errors += error

        # ---------------------------------------------------------------------
        # The next steps are different depending on the DRS file and
        # we may have multiple files
        out_files = []
        out_types = []
        # loop around filename
        for filename in files:
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
                valid1, error = check_file_extension(*exargs, ext=ext)
                errors += error
                # -------------------------------------------------------------
                # Step 3: Check file header is valid
                # -------------------------------------------------------------
                # this step is just for 'fits' files, if not fits
                #    files we can return here
                if '.fits' in ext:
                    out = check_file_header(self, argname, drs_file, filename,
                                            directory)
                    valid2, filetype, error = out
                    errors += error
                else:
                    valid2 = True
                    filetype = None
                # -------------------------------------------------------------
                # Step 4: Check exclusivity
                # -------------------------------------------------------------
                exargs = [self, filename, argname, drs_file, drs_logic,
                          out_types, alltypelist]
                valid3, error = check_file_exclusivity(*exargs)
                errors += error

                # -------------------------------------------------------------
                # Step 5: Check exclusivity
                # -------------------------------------------------------------
                valid = valid1 and valid2 and valid3
                # check validity and append if valid
                if valid:
                    out_files.append(filename)
                    out_types.append(filetype)
                    # break out the inner loop if valid (we don't need to
                    #    check other drs_files)
                    break
        # ---------------------------------------------------------------------
        # deal with return types:
        # a. if we don't have the right number of files then we failed
        if len(out_files) != len(files):
            return False, None, None, errors
        # b. if we did but expect an error returned return True with an error
        elif return_error:
            return True, out_files, out_types, []
        # c. if we did and don't expect an error return True without an error
        else:
            return True, out_files, out_types

    def generate_runs_from_filelist(self, __list__, __filters__=None,
                                    **kwargs):
        """
        Generates a run instance (or set of run instances) based on the
        "__list__". Each file must be a absolute path. The directory (night name
        is taken from the absolute path minus the input directory given).
        Any additional non-file keyword arguments should be given after the
        file list, their names MUST match the name of that argument for correct
        assignment.

        :param __list__: list of string, absolute paths to all files to be
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
        input_dir = self.get_input_dir()
        # get directories and filter out unusable file (due to wrong location)
        filelist = dir_file_filter(input_dir, __list__)
        # from the unique directory list search for index files (should be one
        #   per file)
        dir_list = list(filelist.keys())
        index_files = get_index_files(self, input_dir, dir_list)
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
                self.get_non_file_arg(argname, kwargs, kind='arg')
            # -----------------------------------------------------------------
            # else we are dealing with a set of files
            else:
                self.get_file_arg(argname, index_files, filelist, dir_list,
                                  kind='arg', filters=__filters__)
        # ---------------------------------------------------------------------
        # loop around keyword arguments
        for kwargname in self.kwargs:
            # get dtype for arg
            dtype = self.kwargs[kwargname].dtype
            # -----------------------------------------------------------------
            # just get arg from kwargs
            self.get_non_file_arg(kwargname, kwargs, kind='kwarg')

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
        cmd_args_groups = self.generate_arg_groups()
        # ---------------------------------------------------------------------
        # now deal with keyword arguments
        cmd_kwargs = ''
        for kwarg in self.kwargs:
            # get kwarg value
            value = self.kwargs[kwarg].value
            # construct command
            if value is not None:
                cmd_kwargs += '--{0}={1} '.format(kwarg, value)
        # ---------------------------------------------------------------------
        runs = []
        for cmd_args in cmd_args_groups:
            # generate command
            run_it = '{0} {1} {2}'.format(cmd, cmd_args, cmd_kwargs)
            # append to runs
            runs.append(run_it)
        # return in form:
        #       runs[it] = "recipe arg1 arg2 ... kwarg1= kwarg2="
        return runs

    def generate_arg_groups(self):
        """
        Generate argument runs from self.args[ARG].value
        (For use after self.get_file_arg and self.get_non_file_arg for
         kind='arg')

        Expects one and only one argument with dtype "file" or "files"
        Will also deal with argument "directory being set"

        :return runs: list of runs in form:
               runs[it] = "recipe arg1 arg2 ... kwarg1= kwarg2="
        """
        # get parameters
        params = self.drs_params
        # set up filearg
        filearg, dirarg = None, None

        # storage
        cmd_args_groups = []

        # find file args (use last)
        for argname in self.args:
            # get this instances arg
            arg = self.args[argname]
            # deal with directory arg
            if argname == 'directory':
                dirarg = arg.value
            # deal with files
            elif arg.dtype in ['file', 'files']:
                filearg = argname

            # TODO: Got to here:
            # TODO:     Only works currently for 1 argument
            # TODO:     Need to extend this to have multiple file arguments
            # TODO:     Or have a different mechanism
            # TODO:   e.g. cannot work on cal_badpix currently

        # ---------------------------------------------------------------------
        # Now only deal with file arg
        arg = self.args[filearg]
        # ---------------------------------------------------------------------
        # storage
        directories, filenames = [], []
        exp_nums, nexps = [], []
        # loop around files in arg and get lists of parameters
        for value in arg.value:
            directories.append(value.directory)
            filenames.append(value.index['FILENAME'])
            exp_nums.append(value.index[params['KW_CMPLTEXP'][0]])
            nexps.append(value.index[params['KW_NEXP'][0]])
        # ---------------------------------------------------------------------
        # group by exposure sets  i.e. if we have 1,2,3,4,1,2,3,1,1,1,2,3,4
        #                     group as following: 1,2,2,2,3,3,3,4,5,6,6,6,6
        exp_sets = get_exposure_set(exp_nums)
        # ---------------------------------------------------------------------
        # group by directory
        groups = OrderedDict()
        for group_dir in np.unique(directories):
            # each exposure set goes into a directory key/value pair
            groups[group_dir] = []
            # group by exposure set
            for group_exp in set(exp_sets):
                # loop around files in arg
                for it, filename in enumerate(filenames):
                    # get this iterations values
                    dir_it = directories[it]
                    exp_set = exp_sets[it]
                    # deal with bad group
                    if exp_set != -1:
                        # get group condition
                        cond1 = dir_it == group_dir
                        cond2 = exp_set == group_exp
                        # add to group if conditions met
                        if cond1 and cond2:
                            groups[group_dir].append(filename)
        # ---------------------------------------------------------------------
        # now we have the groups we can create the runs

        # loop around group directories
        for key in list(groups.keys()):
            # deal with overriding the directory (from kwargs input)
            if dirarg is not None:
                directory = str(dirarg)
            else:
                directory = str(key)
            # deal with no files
            if len(groups[key]) == 0:
                continue
            # deal with individual files
            if arg.limit == 1:
                for filename in groups[key]:
                    cmd_args_group = '{0} {1}'.format(directory, filename)
                    # append to cmd_arg_groups
                    cmd_args_groups.append(cmd_args_group)
            else:
                # deal with files in groups
                files = ' '.join(groups[key])
                # construct cmd arg group
                cmd_args_group = '{0} {1}'.format(directory, files)
                # append to cmd_arg_groups
                cmd_args_groups.append(cmd_args_group)
        # ---------------------------------------------------------------------
        # return cmd_args_groups
        return cmd_args_groups

    def get_non_file_arg(self, argname, kwargs, kind='arg'):
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
            arg.value = [value]
        elif kind == 'arg':
            emsg = ('DevError: {0} "{1}" is not defined in call to {2}'
                    ''.format(arg_string, argname, func_name))
            WLOG(self.drs_params, 'error', emsg)
        # update self
        if kind == 'arg':
            self.args[argname] = arg
        else:
            self.kwargs[argname] = arg

    def get_file_arg(self, argname, index_files, filelist, dir_list,
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
            index = get_index_data(self.drs_params, index_file, directory)
            # apply filters
            index = filter_index(self.drs_params, index, filters)
            # deal with no index
            if index is None:
                continue
            # else get list of valid files for this argument
            gargs = [arg, index, directory, dir_filelist]
            arg.value += self.get_files_valid_for_arg(*gargs)
        # update self
        if kind == 'arg':
            self.args[argname] = arg
        else:
            self.kwargs[argname] = arg

    def get_input_dir(self):
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

    def get_files_valid_for_arg(self, arg, index, directory, dfilelist):
        """
        Gets all files in filelist that are in "index" that meet the
        requirements of "arg.files"

        :param arg: DrsArgument, an instance of spirouRecipe.DrsArgument
        :param index: astropy.table, Table from the INDEX_FILE for this
                      directory
        :param directory: string, the sub-directory tree (night name) under
                          the input_dir
        :param filelist: list of strings, the base filenames of the files
                         in "directory" that we want to filter from

        :return valid_files: dictionary, the files (from "filelist" that are
                             in each arg.files. keys are the names of the
                             arg.files values are lists of the files found.
        """
        # convert filelist to a numpy array
        dfilelist = np.array(dfilelist, dtype=str)
        ifilelist = np.array(index['FILENAME'], dtype=str)
        # get this directories index file name
        ifile = os.path.join(directory, INDEX_FILE)
        icol = INDEX_FILE_NAME_COL
        # get input directory
        input_dir = self.get_input_dir()
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
                    emsg = 'DevError: Key "{0}" not in index file {1}'
                    eargs = [key, ifile]
                    WLOG(params, 'error', emsg.format(*eargs))
                # mask by rkey value
                mask &= indexdata[key] == rkeys[rkey]
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
                tmp_file.index = make_dict_from_table(indexdata[mask][v_it])
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
def check_file_location(recipe, argname, directory, filename):
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
        input_dir = recipe.get_input_dir()
    # -------------------------------------------------------------------------
    # Step 1: check "filename" as full link to file (including wildcards)
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(filename)
    # debug output
    if DEBUG and len(raw_files) == 0:
        dmsg = 'Argument {0}: File not found: "{1}"'
        dargs = [argname, filename]
        WLOG(params, '', dmsg.format(*dargs))
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        if DEBUG:
            dmsg = 'Argument {0}: File found (Full file path): "{1}"'
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
        dmsg = 'Argument {0}: File not found: "{1}"'
        dargs = [argname, os.path.join(input_dir, filename)]
        WLOG(params, '', dmsg.format(*dargs))
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        if DEBUG:
            dmsg = 'Argument {0}: File found (Input file path): "{1}"'
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
        dmsg = 'Argument {0}: File not found: "{1}"'
        dargs = [argname, filename + '.fits']
        WLOG(params, '', dmsg.format(*dargs))
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        if DEBUG:
            dmsg = 'Argument {0}: File found (Full file path + ".fits"): "{1}"'
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
        dmsg = 'Argument {0}: File not found: "{1}"'
        dargs = [argname, os.path.join(input_dir, filename + '.fits')]
        WLOG(params, '', dmsg.format(*dargs))
    # if we have file(s) then add them to output files
    for raw_file in raw_files:
        if DEBUG:
            dmsg = 'Argument {0}: File found (Input file path + ".fits"): "{1}"'
            WLOG(params, '', dmsg.format(argname, raw_file))
        output_files.append(raw_file)
    # check if we are finished here
    if len(output_files) > 0:
        return True, output_files, []
    # -------------------------------------------------------------------------
    # Deal with cases where we didn't find file
    # -------------------------------------------------------------------------
    eargs = [argname, filename]
    emsgs = ['Argument {0}: File = "{1}" was not found'.format(*eargs),
             '\tTried:',
             '\t\t"{0}"'.format(filename),
             '\t\t"{0}"'.format(os.path.join(input_dir, filename))]
    if not filename.endswith('.fits'):
        fitsfile = filename + '.fits'
        emsgs.append('\t\t"{0}"'.format(fitsfile))
        emsgs.append('\t\t"{0}"'.format(os.path.join(input_dir, fitsfile)))
    # return False, no files and error messages
    return False, None, emsgs


def check_file_extension(recipe, argname, filename, ext=None):
    """
    If '.fits' file checks the file extension is valid.

    :param argname: string, the argument name (for error reporting)
    :param files: list of strings, the files to check
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
            dmsg = 'Argument {0}: Valid file extension for file "{1}"'
            dargs = [argname, filename]
            WLOG(params, '', dmsg.format(*dargs))
        return True, []
    # if False generate error and return it
    else:
        emsgs = ['Argument {0}: Extension of file {1} not valid',
                 '\t\tRequired extension = {0}'.format(ext)]
        return False, emsgs


def check_file_header(recipe, argname, drs_file, filename, directory):
    # get the input directory
    inputdir = recipe.get_input_dir()
    # create an instance of this drs_file with the filename set
    file_instance = drs_file.new(filename=filename, recipe=recipe)
    file_instance.read()
    # set the directory
    file_instance.directory = get_uncommon_path(directory, inputdir)
    # -----------------------------------------------------------------
    # use file_instances check file header method
    return file_instance.check_file_header(argname=argname, debug=DEBUG)


def check_file_exclusivity(recipe, filename, argname, drs_file, logic,
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
            dmsg = ('Argument {0}: Exclusivity check skipped for first file.'
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
            emsgs = ['Argument {0}: File identified as "{1}" however other'
                     ' files identified as "{2}"'.format(*eargs),
                     '\t\tFiles must match (logic set to "exclusive")',
                     '\t\tFilename = {0}'.format(filename)]
            return False, emsgs
        # if condition is met return True and empty error
        else:
            if DEBUG:
                dmsg = ('Argument {0}: File exclusivity maintained. ("{1}"'
                        '== "{2}")')
                dargs = [argname, drs_file.name, alltypelist[-1].name]
                WLOG(params, '', dmsg.format(*dargs))
            return True, []

    # if logic is 'inclusive' we just need to return True
    if logic == 'inclusive':
        if DEBUG:
            dmsg = 'Argument {0}: File logic is "inclusive" skipping check.'
            WLOG(params, '', dmsg.format(argname))
        return True, []
    # else logic is wrong
    else:
        emsgs = ['Dev Error: logic was wrong for argument {0}',
                 '\tMust be "exclusive" or "inclusive"']
        return False, emsgs


# =============================================================================
# Define run making functions
# =============================================================================
def dir_file_filter(inputdir, infilelist):
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


def get_index_files(recipe, inputdir, outudirlist):
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


def get_index_data(p, index_file, directory):
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


def filter_index(p, index, filters=None):
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
def get_dir_list(dirroot, limit):
    dir_list = []
    for root, dirs, files in os.walk(dirroot):
        # skip dirs that are empty (or full of directories)
        if len(files) == 0:
            continue
        # do not display all
        if len(dir_list) > limit:
            dir_list.append('...')
            return dir_list
        # find the relative root of directories compared to ARG_FILE_DIR
        relroot = get_uncommon_path(root, dirroot)
        # append relative roots
        dir_list.append(relroot)
    # if empty list add none found
    if len(dir_list) == 0:
        dir_list = ['No valid directories found.']
    # return night_dirs
    return dir_list


def get_uncommon_path(path1, path2):
    common = os.path.commonpath([path2, path1]) + os.sep
    return path1.split(common)[-1]


def get_file_list(path, limit=None, ext=None, recursive=False):
    # deal with no limit - set hard limit
    if limit is None:
        limit = HARD_DISPLAY_LIMIT
    # deal with extension
    if ext is None:
        ext = ''
    # set up file list storage
    file_list = []
    # walk through directories
    for root, dirs, files in os.walk(path):
        if len(file_list) > limit:
            file_list.append('...')
            return file_list
        if not recursive and root != path:
            continue
        if len(files) > 0 and recursive:
            # add root to file list
            file_list.append('\t' + root)
            limit += 1
        for filename in files:
            # do not display all (if limit reached)
            if len(file_list) > limit:
                file_list.append('...')
                return file_list
            # do not display if extension is true
            if not filename.endswith(ext):
                continue
            # add to file list
            file_list.append('\t\t' + filename)
    # if empty list add none found
    if len(file_list) == 0:
        file_list = ['No valid files found.']
    # return file_list
    return file_list


def get_arg(recipe, argname):
    if argname in recipe.args:
        arg = recipe.args[argname]
    elif argname in recipe.kwargs:
        arg = recipe.kwargs[argname]
    else:
        arg = None
    # return arg
    return arg


def get_exposure_set(nums):
    """
    Take a set of number that are assumed to represent sequences and group
    the by sequence set
        i.e. if we have 1,2,3,4,1,2,3,1,1,1,2,3,4

        group as following: 1,2,2,2,3,3,3,4,5,6,6,6,6

    :param exp_nums: list of int/str, it integers will group the numbers
                     else will ignore and set the group to -1
    :return sequence_num: list of int, the group number (starts at 1) bad values
                          in "exp_nums" set to a value of -1
    """
    # set iterables
    sequence, group = 1, 0
    # set storage
    group_numbers = []
    # loop around exposure numbers
    for num in nums:
        # test that exp_num is an integer, if it is not then set to group
        # -1 and continue to next one
        if not str(num).isdigit():
            group_numbers.append(-1)
        else:
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


def make_dict_from_table(itable):
    """
    Make dictionary from table evaluating the
    :param itable:
    :return:
    """
    ikeys = list(itable.colnames)
    ivalues = []
    for value in list(itable):
        try:
            if '.' in str(value):
                ivalues.append(float(value))
            else:
                ivalues.append(int(value))
        except ValueError:
            ivalues.append(value)
    return dict(zip(ikeys, ivalues))


def make_listing():
    """
    Make a custom special argument that lists the files in the given
    input directory
    :return props: dictionary for argparser
    """
    props = OrderedDict()
    props['name'] = '--listing'
    props['altnames'] = ['--list']
    props['action'] = MakeListing
    props['nargs'] = 0
    props['help'] = 'List the files in the given input directory'
    return props


def load_other_config_file(p, key, logthis=True, required=False):
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


def print_check_error(p, argname, idnum, filename, recipename, errors,
                      value):
    # construct main error message
    eargs = [argname, idnum, filename, recipename]
    emsgs = ['Arg "{0}"[{1}]: File "{2}" not valid for recipe "{3}"'
             ''.format(*eargs)]
    # add addition error information
    for error in errors:
        emsgs.append('\t' + error)
    # add warning for wildcards
    if '*' in value:
        wmsg = 'Arg "{0}"[{1}]: Wildcards found in "{0}"'
        WLOG(p, 'warning', wmsg.format(argname, idnum, value))
    # log error
    WLOG(p, 'error', emsgs, wrap=False)

# =============================================================================
# End of code
# =============================================================================
