#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 12:02

@author: cook
"""
import argparse
from astropy.table import Table
from collections import OrderedDict
import copy
import itertools
import numpy as np
import sys
from typing import Any, Dict, List, Tuple, Type, Union

from apero.base import base
from apero.base import drs_base_classes as base_class
from apero.base import drs_misc
from apero.base import drs_text
from apero.core import constants
from apero import lang
from apero.core.core import drs_log, drs_file
from apero.core.core import drs_argument

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_recipe.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# get print colours
COLOR = drs_misc.Colors()
# get param dict
ParamDict = constants.ParamDict
# get the input file
DrsInputFile = drs_file.DrsInputFile
# get the config error
ConfigError = constants.ConfigError
ArgumentError = constants.ArgumentError
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
HelpText = lang.core.drs_lang_text.HelpDict
# -----------------------------------------------------------------------------
# Get Classes from drs_argument
DrsArgumentParser = drs_argument.DrsArgumentParser
DrsArgument = drs_argument.DrsArgument
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# define special keys
SPECIAL_LIST_KEYS = ['SCIENCE_TARGETS', 'TELLURIC_TARGETS']


# =============================================================================
# Define Recipe Classes
# =============================================================================
class DrsRecipe(object):
    def __init__(self, instrument: str = 'None',
                 name: Union[str, None] = None,
                 filemod: Union[base_class.ImportModule, None] = None,
                 params: Union[ParamDict, None] = None):
        """
        Create a DRS Recipe object (one of these for each top 'user' level
        script (or recipe)

        :param instrument: string, the instrumnet this recipe is associated with
        :param name: string, name of the recipe (the .py file) relating to
                     this recipe object
        :param filemod: ?
        :param params: ParamDict, if set the parameter dictionary of constants

        :returns: None
        """
        # set class name
        self.class_name = 'DrsRecipe'
        # set function name (cannot
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # get instrument
        self.instrument = instrument
        # deal with name
        if name is None:
            self.name = 'UnknownRecipe'
        # remove any left over .py on the end
        elif name.strip().endswith('.py'):
            while name.endswith('.py'):
                name = str(name[:-3])
            self.name = str(name)
        # else name is correct
        else:
            self.name = str(name)
        # set drs file module related to this recipe
        if filemod is None:
            self.filemod = None
        else:
            self.filemod = filemod.copy()
        # get drs parameters (will be loaded later)
        if params is None:
            self.params = ParamDict()
        # most the time params should not be set here
        else:
            self.params = params
            # even rarer that instrument is ont set but params is
            if self.instrument != params['INSTRUMENT']:
                self.instrument = params['INSTRUMENT']
        # set filters
        self.filters = dict()
        self.master = False
        self.allowedfibers = None
        # shortname set to name initially
        self.shortname = str(self.name)
        # recipe kind (for logging)
        self.kind = None
        # save recipe module
        self.recipemod = None
        # import module as ImportClass (pickle-able)
        self.module = self._import_module()
        # output directory
        self.outputdir = 'reduced'
        # input directory
        self.inputdir = 'tmp'
        # input type (RAW/REDUCED)
        self.inputtype = 'raw'
        # whether to force input/outputdir
        self.force_dirs = [False, False]
        # recipe description/epilog
        self.description = 'No description defined'
        self.epilog = ''
        # define sets of arguments
        self.args = OrderedDict()
        self.kwargs = OrderedDict()
        self.specialargs = OrderedDict()
        # list of strings of extra arguments to add / overwrite set values
        self.extras = OrderedDict()
        # define arg list
        self.arg_list = []
        self.str_arg_list = None
        self.used_command = []
        self.drs_pconstant = None
        self.textdict = None
        self.helptext = None
        self.input_params = ParamDict()
        self.required_args = []
        self.optional_args = []
        self.special_args = []
        self.outputs = dict()
        self.output_files = dict()
        self.debug_plots = []
        self.summary_plots = []
        # the plotter class
        self.plot = None
        # set the log class
        self.log = None
        # set up the input validation (should be True to check arguments)
        self.input_validation = True
        # get drs params
        self.get_drs_params()
        # make special arguments
        self._make_specials()

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set function name
        _ = display_func(self.params, '__getstate__', __NAME__,
                         self.class_name)
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
        # set function name
        _ = display_func(self.params, '__setstate__', __NAME__,
                         self.class_name)
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        Defines the str(DrsRecipe) return for DrsRecipe
        :return str: the string representation of DrsRecipe
                     i.e. DrsRecipe[name]
        """
        # set function name
        _ = display_func(self.params, '__str__', __NAME__,
                         self.class_name)
        # return string representation
        return self.__str__()

    def __repr__(self) -> str:
        """
        Defines the print(DrsRecipe) return for DrsRecipe
        :return str: the string representation of DrsRecipe
                     i.e. DrsRecipe[name]
        """
        # set function name
        _ = display_func(self.params, '__repr__', __NAME__,
                         self.class_name)
        # return string representation
        return '{0}[{1}]'.format(self.class_name, self.name)

    def get_drs_params(self, **kwargs):
        """
        Get the drs parameter dictionary and pseudo constants, and pass
        the kwargs directly into params i.e. params[kwarg] = kwargs[kwarg]

        :param kwargs: key, value pairs to push into the parameter dictionary

        :return: None, update DrsRecipe.drs_params, DrsRecipe.drs_pconstant,
                 DrsRecipe.textdict, DrsRecipe.helptext
        """
        # set function name
        func_name = display_func(None, 'get_drs_params', __NAME__,
                                 self.class_name)
        # Get config parameters from primary file
        self.params = constants.load(self.instrument)
        self.drs_pconstant = constants.pload(self.instrument)
        self.textdict = TextDict(self.instrument, self.params['LANGUAGE'])
        self.helptext = HelpText(self.instrument, self.params['LANGUAGE'])
        # ---------------------------------------------------------------------
        # assign parameters from kwargs
        for kwarg in kwargs:
            self.params[kwarg] = kwargs[kwarg]
            self.params.set_source(kwarg, func_name + ' --kwargs')
        # ---------------------------------------------------------------------
        # set recipe name
        while self.name.endswith('.py'):
            self.name = self.name[:-3]
        self.params['RECIPE'] = str(self.name)
        self.params.set_source('RECIPE', func_name)
        # ---------------------------------------------------------------------
        # set up array to store inputs/outputs
        self.params['INPUTS'] = ParamDict()
        self.params.set_sources(['INPUTS'], func_name)

    def recipe_setup(self, fkwargs: Union[dict, None] = None,
                     inargs: Union[list, None] = None
                     ) -> Union[Dict[str, Any], None]:
        """
        Interface between "recipe", inputs to function ("fkwargs") and argparse
        parser (inputs from command line)

        :param fkwargs: dictionary, a dictionary where the keys match
                        arguments/keyword arguments in recipe (without -/--),
                        and the values are those to set in the output
                        (set to None for not value set)
        :param inargs: list of input arguments (matching those that sys.argv
                       would give

        :return params:  dictionary, a dictionary where the keys match
                         arguments/keywords (without -/--) and values are the
                         values to be used for this recipe
        """
        # set function name
        func_name = display_func(self.params, 'recipe_setup', __NAME__,
                                 self.class_name)
        # set up storage for arguments
        fmt_class = argparse.RawDescriptionHelpFormatter
        desc, epilog = self.description, self.epilog
        parser = DrsArgumentParser(recipe=self, description=desc, epilog=epilog,
                                   formatter_class=fmt_class,
                                   usage=self._drs_usage())
        # get the drs params from recipe
        drs_params = self.params
        # ---------------------------------------------------------------------
        # deal with args set
        if inargs is not None:
            oldargv = list(sys.argv)
            sys.argv = list(inargs)
        else:
            # deal with function call
            self._parse_args(fkwargs)
            oldargv = None
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
        # ---------------------------------------------------------------------
        # add special arguments
        for rarg in self.specialargs:
            # extract out name and kwargs from rarg
            rname = self.specialargs[rarg].names
            rkwargs = self.specialargs[rarg].props
            # parse into parser
            parser.add_argument(*rname, **rkwargs)
        # ---------------------------------------------------------------------
        # test that sys.argv is a list
        if not isinstance(sys.argv, list):
            eargs = [sys.argv, type(sys.argv), func_name]
            WLOG(drs_params, 'error', TextEntry('00-006-00013', args=eargs))
        # ---------------------------------------------------------------------
        # get params
        try:
            params = vars(parser.parse_args(args=self.str_arg_list))
        except Exception as e:
            eargs = [sys.argv, self.str_arg_list, type(e), e, func_name]
            WLOG(drs_params, 'error', TextEntry('00-006-00014', args=eargs))
            params = None
        # ---------------------------------------------------------------------
        # record the inputs (either via self.str_arg_list or sys.argv)
        if self.str_arg_list is None:
            self.used_command = list(sys.argv)
        else:
            self.used_command = [self.name] + list(self.str_arg_list)
        # ---------------------------------------------------------------------
        # set the source for the params
        source = str(parser.source)
        strsource = '{0} [{1}]'.format(func_name, source)
        # ---------------------------------------------------------------------
        # delete parser - no longer needed
        del parser
        # ---------------------------------------------------------------------
        # if args were set return params alone
        if inargs is not None:
            sys.argv = list(oldargv)
            return params
        # ---------------------------------------------------------------------
        # update params
        self.input_params = ParamDict()
        for key in list(params.keys()):
            self.input_params[key] = params[key]
            self.input_params.set_source(key, strsource)

    def option_manager(self):
        """
        Takes all the optional parameters and deals with them (i.e. puts them
        into self.drs_params

        :return None:
        """
        # set function name
        func_name = display_func(self.params, 'option_manager', __NAME__,
                                 self.class_name)
        # get drs params
        params = self.params
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
                emsg = self.textdict['00-006-00001'].format(*eargs)
                kwarg.exception(emsg)
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
                emsg = self.textdict['00-006-00002'].format(*eargs)
                kwarg.exception(emsg)
                value, param_key = None, None
            # else check that default_ref is in drs_params (i.e. defined in a
            #   constant file)
            elif kwarg.default_ref not in params:
                eargs = [kwarg.default_ref, kwarg.name, self.name]
                emsg = self.textdict['00-006-00003'].format(*eargs)
                kwarg.exception(emsg)
                value, param_key = None, None
            # else we have all we need to reset the value
            else:
                value = params[kwarg.default_ref]
                param_key = kwarg.default_ref
            # if we have reached this point then set value
            input_parameters[kwarg.name] = value
            if param_key is not None:
                input_parameters[kwarg.default_ref] = value
                # set the source
                psource = '{0} [{1}]'.format(func_name, kwarg.name)
                input_parameters.set_source(kwarg.default_ref, psource)
        # ---------------------------------------------------------------------
        if 'MASTER' in input_parameters:
            if input_parameters['MASTER'] in ['True', 1, True]:
                self.params['IS_MASTER'] = True
        # ---------------------------------------------------------------------
        # add to DRS parameters
        self.params['INPUTS'] = input_parameters
        self.params.set_source('INPUTS', func_name)
        # push values of keys matched in input_parameters into drs_parameters
        for key in input_parameters.keys():
            if key in self.params:
                self.params[key] = input_parameters[key]
                self.params.set_source(key, input_parameters.sources[key])

    def set_arg(self, name: Union[str, None] = None,
                pos: Union[int, str, None] = None,
                altnames: Union[List[str], None] = None,
                dtype: Union[str, Type, None] = None,
                options: Union[List[Any], None] = None,
                helpstr: Union[str, None] = '',
                files: Union[List[str], None] = None,
                path: Union[str, None] = None, limit: Union[int, None] = None,
                minimum: Union[int, float, None] = None,
                maximum: Union[int, float, None] = None,
                filelogic: str = 'inclusive', default: Union[Any, None] = None,
                default_ref: Union[Any, None] = None,
                required: bool = None, reprocess: bool = False):
        """
        Add an argument to the recipe

        :param name: string, the name of the argument and call, for optional
                     arguments should include the "-" and "--" in front
                     ("arg.name" will not include these but "arg.argname"
                     and "arg.names" will)

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

        :returns: None, updates DrsRecipe.args
        """
        # set function name
        _ = display_func(self.params, 'set_arg', __NAME__, self.class_name)
        # set name
        if name is None:
            name = 'Arg{0}'.format(len(self.args) + 1)
        # create argument
        try:
            argument = DrsArgument(name, kind='arg', pos=pos, altnames=altnames,
                                   dtype=dtype, options=options,
                                   helpstr=helpstr, files=files, path=path,
                                   limit=limit, minimum=minimum,
                                   maximum=maximum, filelogic=filelogic,
                                   default=default, default_ref=default_ref,
                                   required=required, reprocess=reprocess)
        except ArgumentError as _:
            sys.exit(0)
        # make arg parser properties
        argument.make_properties()
        # recast name
        name = argument.name
        # add to arg list
        self.args[name] = argument

    def set_kwarg(self, name: Union[str, None] = None,
                  altnames: Union[List[str], None] = None,
                  dtype: Union[str, Type, None] = None,
                  options: Union[List[Any], None] = None,
                  helpstr: Union[str, None] = '',
                  files: Union[List[str], None] = None,
                  path: Union[str, None] = None,
                  limit: Union[int, None] = None,
                  minimum: Union[int, float, None] = None,
                  maximum: Union[int, float, None] = None,
                  filelogic: str = 'inclusive',
                  default: Union[Any, None] = None,
                  default_ref: Union[Any, None] = None,
                  required: bool = None, reprocess: bool = False):
        """
        Add a keyword argument to the recipe

        :param name: string, the name of the argument and call, for optional
                     arguments should include the "-" and "--" in front
                     ("arg.name" will not include these but "arg.argname"
                     and "arg.names" will)

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

        :returns: None - updates DrsRecipe.kwargs
        """
        # set function name
        _ = display_func(self.params, 'set_kwarg', __NAME__,
                         self.class_name)
        # deal with no name
        if name is None:
            name = 'Kwarg{0}'.format(len(self.args) + 1)
        # create keyword argument
        try:
            keywordargument = DrsArgument(name, kind='kwarg', pos=None,
                                          altnames=altnames, dtype=dtype,
                                          options=options, helpstr=helpstr,
                                          files=files, path=path,
                                          limit=limit, minimum=minimum,
                                          maximum=maximum, filelogic=filelogic,
                                          default=default,
                                          default_ref=default_ref,
                                          required=required,
                                          reprocess=reprocess)
        except ArgumentError as _:
            sys.exit(0)
        # make arg parser properties
        keywordargument.make_properties()
        # recast name
        name = keywordargument.name
        # set to keyword argument
        self.kwargs[name] = keywordargument

    def set_outputs(self, **kwargs: DrsInputFile):
        """
        Set the output files

        :param kwargs: all keywords values should be a DrsFitsFile
                       i.e. file1=DrsInputFile()

        :return: None - updates DrsRecipe.outputs
        """
        # set function name
        _ = display_func(self.params, 'set_outputs', __NAME__,
                         self.class_name)
        # loop around kwargs
        for kwarg in kwargs:
            # check if kwarg is the drs_file.DrsInputFile (only add these)
            if isinstance(kwargs[kwarg], DrsInputFile):
                self.outputs[kwarg] = kwargs[kwarg]

    def set_debug_plots(self, *args: str):
        """
        Sets the debug plot list

        :param args: all arguments should be strings
                     i.e. file1='MY_PLOT'
        :return: None - updates DrsRecipe.debug_plots
        """
        # set function name
        _ = display_func(self.params, 'set_debug_plots', __NAME__,
                         self.class_name)
        # loop around all arguments
        for arg in args:
            # check if arg is a string (only add strings)
            if isinstance(arg, str):
                self.debug_plots.append(arg)

    def set_summary_plots(self, *args: str):
        """
        Sets the summary plot list

        :param args: all arguments should be strings
                     i.e. file1='MY_PLOT'

        :return: None - updates DrsRecipe.summary_plots
        """
        # set function name
        _ = display_func(self.params, 'set_summary_plots', __NAME__,
                         self.class_name)
        # loop around all arguments
        for arg in args:
            # check if arg is a string (only add strings)
            if isinstance(arg, str):
                self.summary_plots.append(arg)

    def add_output_file(self, outfile: DrsInputFile):
        """
        Add an output file to DrsRecipe.output_files (for the index database)

        :param outfile: DrsInputFile instance (the output file to add)

        :return: None - updates DrsRecipe.output_files
        """
        # set function name
        func_name = display_func(self.params, 'add_output_file', __NAME__,
                                 self.class_name)
        # get the name of the outfile
        key = outfile.basename
        # check if outfile has output_dict
        if hasattr(outfile, 'output_dict'):
            self.output_files[key] = outfile.output_dict
        else:
            # log that output file has no attribute 'output_dict'
            eargs = [outfile.name, func_name]
            emsg = TextEntry('00-008-00016', args=eargs)
            WLOG(self.params, 'error', emsg)

    def main(self, **kwargs) -> Dict[str, Any]:
        """
        Run the main function associated with this recipe

        :param kwargs: kwargs passed to the main functions

        :return: dictionary, a drs recipe main functions dictionary
        """
        # set function name
        func_name = display_func(self.params, 'main', __NAME__,
                                 self.class_name)
        # ------------------------------------------------------------------
        # next check in parameters for path to module
        if (self.module is None) and (self.params is not None):
            params = self.params
            # check for parameters
            cond1 = 'INSTRUMENT' in params
            cond2 = 'DRS_INSTRUMENT_RECIPE_PATH' in params
            cond3 = 'DRS_DEFAULT_RECIPE_PATH' in params
            if cond1 and cond2 and cond3:
                instrument = params['INSTRUMENT']
                rpath = params['DRS_INSTRUMENT_RECIPE_PATH']
                dpath = params['DRS_DEFAULT_RECIPE_PATH']
                margs = [instrument, [self.name], rpath, dpath]
                modules = constants.getmodnames(*margs, return_paths=False)
                # return module
                self.module = self._import_module(modules[0], full=True,
                                                  quiet=True)
        # ------------------------------------------------------------------
        # else make an error
        if self.module is None:
            emsg = TextEntry('00-000-00001', args=[self.name])
            WLOG(self.params, 'error', emsg)
        # ------------------------------------------------------------------
        # run main via import module get method (gets import module)
        if hasattr(self.module.get(), 'main'):
            return self.module.get().main(**kwargs)
        else:
            eargs = [self.module.name, self.module.path, func_name]
            emsg = TextEntry('00-000-00004', args=eargs)
            WLOG(self.params, 'error', emsg)

    def get_input_dir(self, directory: Union[str, None] = None,
                      force: bool = False) -> Union[str, None]:
        """
        Alias to drs_argument.get_input_dir

        Get the input directory for this recipe based on what was set in
        initialisation (construction)

        :param directory: None or string - force the input dir (if it exists)
        :param force: bool if True allows force setting

        if RAW uses DRS_DATA_RAW from drs_params
        if TMP uses DRS_DATA_WORKING from drs_params
        if REDUCED uses DRS_DATA_REDUC from drs_params

        :return input_dir: string, the input directory
        """
        # set function name
        _ = display_func(self.params, 'get_input_dir', __NAME__,
                         self.class_name)
        # make sure if force is True we use it
        force = self.force_dirs[0] or force
        # return alised call
        return drs_argument.get_input_dir(self.params, directory, force,
                                          forced_dir=self.inputdir)

    def get_output_dir(self, directory: Union[str, None] = None,
                       force: bool = False) -> Union[str, None]:
        """
        Alias to drs_argument.get_output_dir

        Get the input directory for this recipe based on what was set in
        initialisation (construction)

        :param directory: None or string - force the output dir (if it exists)
        :param force: bool if True allows force setting

        if RAW uses DRS_DATA_RAW from drs_params
        if TMP uses DRS_DATA_WORKING from drs_params
        if REDUCED uses DRS_DATA_REDUC from drs_params

        :return input_dir: string, the input directory
        """
        # set function name
        _ = display_func(self.params, 'get_output_dir', __NAME__,
                         self.class_name)
        # make sure if force is True we use it
        force = self.force_dirs[0] or force
        # return alised call
        return drs_argument.get_output_dir(self.params, directory, force,
                                           forced_dir=self.outputdir)

    def copy(self, recipe: 'DrsRecipe'):
        """
        Copy a "recipe" (DrsRecipe instance) over the current DrsRecipe instance

        :param recipe: DrsRecipe, the recipe to copy over current

        :return: None, update DrsRecipe attributes (based on recipe attributes)
        """
        # get instrument
        self.instrument = str(recipe.instrument)
        # name
        self.name = str(recipe.name)
        # set drs file module related to this recipe
        if recipe.filemod is None:
            self.filemod = None
        else:
            self.filemod = recipe.filemod.copy()
        # set filters
        self.filters = dict(recipe.filters)
        self.master = bool(recipe.master)
        self.allowedfibers = copy.deepcopy(recipe.allowedfibers)
        # shortname
        self.shortname = str(recipe.shortname)
        # recipe kind (for logging)
        self.kind = copy.deepcopy(recipe.kind)
        # import module
        self.module = self.module
        # output directory
        self.outputdir = str(recipe.outputdir)
        # input directory
        self.inputdir = str(recipe.inputdir)
        # whether to force input/outputdir
        self.force_dirs = [False, False]
        # input type (RAW/REDUCED)
        self.inputtype = str(recipe.inputtype)
        # recipe description/epilog
        self.description = recipe.description
        self.epilog = recipe.epilog
        # define sets of arguments (need to copy arguments)
        self.args = OrderedDict()
        for argname in recipe.args.keys():
            self.args[argname] = DrsArgument()
            self.args[argname].copy(recipe.args[argname])
        self.kwargs = OrderedDict()
        for kwargname in recipe.kwargs.keys():
            self.kwargs[kwargname] = DrsArgument()
            self.kwargs[kwargname].copy(recipe.kwargs[kwargname])
        for sargname in recipe.specialargs.keys():
            self.specialargs[sargname] = DrsArgument()
            self.specialargs[sargname].copy(recipe.specialargs[sargname])
        for arg in recipe.extras:
            self.extras[arg] = recipe.extras[arg]
        # define arg list
        self.arg_list = list(recipe.arg_list)
        # get string arg list (may be None)
        self.str_arg_list = copy.deepcopy(recipe.str_arg_list)
        self.used_command = copy.deepcopy(recipe.used_command)
        # get drs parameters
        self.params = recipe.params.copy()
        self.drs_pconstant = recipe.drs_pconstant
        self.textdict = self.textdict
        self.helptext = self.helptext
        self.input_params = ParamDict(recipe.input_params)
        self.required_args = list(recipe.required_args)
        self.optional_args = list(recipe.optional_args)
        self.special_args = list(recipe.special_args)
        # deal with copying file outputs
        if self.outputs is None:
            self.outputs = None
        else:
            self.outputs = dict()
            for output in recipe.outputs:
                oldoutput = recipe.outputs[output]
                newouput = oldoutput.completecopy(oldoutput)
                self.outputs[output] = newouput
        # copy plotter
        self.plot = recipe.plot
        # copy logger
        self.log = recipe.log
        # plot options
        self.debug_plots = list(recipe.debug_plots)
        self.summary_plots = list(recipe.summary_plots)
        # set up the input validation (should be True to check arguments)
        self.input_validation = recipe.input_validation

    # =========================================================================
    # Reprocessing methods
    # =========================================================================
    def generate_runs(self, table: Table,
                      filters: Union[Dict[str, Any], None] = None,
                      allowedfibers: Union[List[str], str, None] = None
                      ) -> List[str]:
        """
        Generate a list of run strings from a table of raw files given a set of
        filters for this DrsRecipe (i.e. use args/keywords from recipe
        definition)

        :param table: astropy.table - the raw file table (with keys from
                      OUTPUT_FILE_HEADER_KEYS)
        :param filters: None or dict - dictionary of filters where keys are
                        KW_XXX names (in params) and values are the values to
                        test in the header(s)
        :param allowedfibers: list of strings, the list if fibers that are
                              allowed for this generation

        :return: list of strings, the runs (as if recipes run from the command
                 line
        """

        # set function name
        _ = display_func(self.params, 'generate_runs', __NAME__,
                         self.class_name)
        # get parameters
        params = self.params
        # need to find files in table that match each argument
        #    filedict is a dictionary of arguments each for
        #    each drsfile (if filelogic=exclusive)
        #       i.e. filedict[argname][drsfile]
        #    else all drsfiles go to 'all'
        #       i.e. filedict[argname]['all']
        argdict = find_run_files(params, self, table, self.args,
                                 filters=filters, allowedfibers=allowedfibers)
        # same for keyword args but this time we need to check only if
        #   keyword is required, else skip (don't add optionals)
        kwargdict = find_run_files(params, self, table, self.kwargs,
                                   filters=filters, allowedfibers=allowedfibers,
                                   check_required=True)
        # now we have the file lists we need to group files and match where
        #   there are more than one argument, we then add in the other
        #   arguments and construct the runs
        runargs = group_run_files(params, self, argdict, kwargdict)
        # now we have the runargs we can convert to a runlist
        runlist = convert_to_command(params, self, runargs)
        # clear printer
        drs_log.Printer(None, None, '')
        # return the runlist
        return runlist

    def add_extra(self, arguments: Union[dict, None] = None,
                  tstars: Union[List[str], None] = None,
                  ostars: Union[List[str], None] = None):
        """
        Add extra arguments to this DrsRecipe instance
        i.e. from arguments (a dictionary of arguments where each key is the
        value that would have been used at run time
        e.g. --objname  goes tp arguments['objname'] = VALUES

        This is only really for use with the DrsRunSequence.add function (adding
        a recipe to a run sequence)

        :param arguments: dictionary of keys where each key is a valid
                          position or optional argument for this recipe
                          (see the recipe definition) and each value are those
                          value(s) that this argument is allowed to have
                          i.e. --objname --> arguments['objname'] = VALUES
                          so one can force the value of --objname
        :param tstars: list of strings, the list of telluric star object names
                       - this is required when using alias "TELLURIC_TARGETS"
                       and TELLURIC_TARGETS value = ['None', 'All', '']
                       to list all telluric targets currently definied
        :param ostars: list of strings, the list of object names that are not
                       telluric stars - this is required when using alias
                       "SCIENCE_TARGETS" and SCIENCE_TARGETS
                       value = ['None', 'All', ''] to list all non-telluric
                       'science targets' currently defined
        :return: None - updates DrsRecipe.extras (for later use)
        """
        # set function name
        func_name = display_func(self.params, 'add_extra', __NAME__,
                                 self.class_name)
        # get parameters
        params = self.params
        # load pseudo constants
        pconst = constants.pload(instrument=params['INSTRUMENT'])
        # loop around arguments
        for argname in arguments:
            # get value
            value = copy.deepcopy(arguments[argname])
            # check if value is a reference to a params value
            if isinstance(value, str):
                # see if value is in parameter dictionary already
                if value in params:
                    value = params[value]
                # deal with SPECIAL_LIST_KEYS
                if arguments[argname] in SPECIAL_LIST_KEYS:
                    # do not make null text a list of strings
                    if not drs_text.null_text(value, ['None', 'All', '']):
                        # may not be strings (if set from params)
                        if isinstance(value, str):
                            # these must be lists
                            value = value.split(',')
                            # make sure there are no white spaces
                            value = np.char.strip(value)
                            # deal with object name cleaning
                            value = list(map(pconst.DRS_OBJ_NAME, value))
                # deal with telluric targets being None
                if arguments[argname] == 'TELLURIC_TARGETS':
                    if isinstance(value, (type(None), str)):
                        # test for null text
                        if drs_text.null_text(value, ['None', 'All', '']):
                            value = tstars
                # deal with science targets being None (use all non-telluric
                #   targets)
                if arguments[argname] == 'SCIENCE_TARGETS':
                    if isinstance(value, (type(None), str)):
                        # test for null text
                        if drs_text.null_text(value, ['None', 'All', '']):
                            value = ostars
            # check for argument in args
            if argname in self.args:
                self.extras[argname] = value
            # check for argument in kwargs
            elif argname in self.kwargs:
                self.extras[argname] = value
            # else raise an error
            else:
                eargs = [argname, value, func_name]
                WLOG(params, 'error', TextEntry('00-503-00012', args=eargs))

    # =========================================================================
    # Private Methods (Not to be used externally to drs_recipe.py)
    # =========================================================================
    def _import_module(self, name: Union[str, None] = None, full: bool = False,
                       quiet: bool = False
                       ) -> Union[base_class.ImportModule, None]:
        """
        Private function to import the import_module class for this recipe

        :param name: str, the name of the recipe
        :param full: bool, if True then the name is assumed to be the full
                     module path
        :param quiet: bool, if True raises a ValueError instead of a ConfigError

        :return: the imported module instance
        """
        # set function name
        func_name = display_func(self.params, '_import_module', __NAME__,
                                 self.class_name)
        # deal with no name
        if name is None:
            name = self.name
        if (name is None) or (name.upper() == 'UNKNOWNRECIPE'):
            return None
        # get local copy of module
        # noinspection PyBroadException
        try:
            return constants.import_module(func_name, name, full=full,
                                           quiet=quiet)
        except Exception:
            return None

    def _parse_args(self, dictionary: Union[Dict[str, Any], None] = None):
        """
        Parse a dictionary of arguments into argparser in the format required
        to match up to the recipe.args/recipe.kwarg assigned to this
        DrsRecipe by calls to "recipe.arg" and "recipe.kwarg"

        :param dictionary: list of key value pairs where the keys must match
                           the names (without "-" and "--") of the arguments
                           and keyword arguments. This is then passed into
                           "recipe.str_arg_list" for parsing into argparser
                           directly (and overiding run time arguments)

        :return: None- updates DrsRecipe.str_arg_list
        """
        # set function name
        _ = display_func(self.params, '_parse_args', __NAME__, self.class_name)
        # set up storage
        self.str_arg_list = []
        # deal with no dictionary set
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

    def _parse_arg(self, arg: DrsArgument, values: Any):
        """
        Parse argument to "recipe.str_arg_list"

        :param arg: DrsArgument, the argument to parse (with "-" and "--" for
                    optional arguments)
        :param values: object, the object to push into the value of argument.
                       The string representation of this value must be
                       readable by argparser i.e. int/float/str etc

        :return: None - updates DrsRecipe.str_arg_list (appends to list)
        """
        # set function name
        _ = display_func(self.params, '_parse_arg', __NAME__, self.class_name)
        # check that value is not None
        if values is None:
            return
        # if we have an optional argument
        if '--' in arg.argname:
            strfmt = '{0}={1}'
        # if we have a positional argument
        else:
            strfmt = '{1}'
        # now add these arguments (as a string) to str_arg_list
        if isinstance(values, list):
            # add the first argument
            if '--' in arg.argname:
                self.str_arg_list.append(arg.argname)
            # add the rest as separate arguments
            for value in values:
                # finally append the string to str_arg_list
                self.str_arg_list.append(value)
        else:
            strarg = [arg.argname, values]
            self.str_arg_list.append(strfmt.format(*strarg))

    def _make_specials(self):
        """
        Make special arguments based on pre-defined static properties
        (i.e. a valid kwargs for parser.add_argument)

        Currently adds the following special arguments:

        --debug --d --verbose    Change the debug mode
        --listing --list         List the files in the given input directory
        --listingall --listall   List all the files available to use
        --version                Display the drs version
        --info --usage           Display the recipe usage information
        -- program --prog        Set the program name (for logging)
        --idebug --idb           set ipython return mode
        --master                 set whether a recipe is a master recipe
        --breakpoints --break    set whether to use breakpoints
        --breakfunc              set whether to break in a certain function
        --quiet -q               set whether to run in queit mode
        --force_indir            force the input directory of the recipe
        --force_outdir           force the output directory of the recipe

        :return None: updates DrsRecipe.specialargs
                      (via DrsRecipe._make_special)
        """
        # set function name
        _ = display_func(self.params, '_make_specials', __NAME__,
                         self.class_name)
        # get instrument and language
        instrument = self.params['INSTRUMENT']
        language = self.params['LANGUAGE']
        # get the help text dictionary
        htext = lang.core.drs_lang_text.HelpDict(instrument, language)
        # ---------------------------------------------------------------------
        # make debug functionality
        self._make_special(drs_argument.make_debug, skip=False, htext=htext)
        # ---------------------------------------------------------------------
        # make listing functionality
        self._make_special(drs_argument.make_listing, skip=True, htext=htext)
        # ---------------------------------------------------------------------
        # make listing all functionality
        self._make_special(drs_argument.make_alllisting, skip=True, htext=htext)
        # ---------------------------------------------------------------------
        # make version functionality
        self._make_special(drs_argument.make_version, skip=True, htext=htext)
        # ---------------------------------------------------------------------
        # make info functionality
        self._make_special(drs_argument.make_info, skip=True, htext=htext)
        # ---------------------------------------------------------------------
        # set program functionality
        self._make_special(drs_argument.set_program, skip=False, htext=htext)
        # ---------------------------------------------------------------------
        # set ipython return functionality
        self._make_special(drs_argument.set_ipython_return, skip=False,
                           htext=htext)
        # ---------------------------------------------------------------------
        # set is_master functionality
        self._make_special(drs_argument.is_master, skip=False, htext=htext)
        # ---------------------------------------------------------------------
        # set breakpoint functionality
        self._make_special(drs_argument.breakpoints, skip=False, htext=htext)
        # ---------------------------------------------------------------------
        # set breakfunc functionality
        self._make_special(drs_argument.make_breakfunc, skip=False, htext=htext)
        # ---------------------------------------------------------------------
        # set quiet functionality
        self._make_special(drs_argument.set_quiet, skip=False, htext=htext)
        # ---------------------------------------------------------------------
        # force input and output directories
        self._make_special(drs_argument.set_inputdir, skip=False, htext=htext)
        self._make_special(drs_argument.set_outputdir, skip=False, htext=htext)

    def _make_special(self, function: Any, skip: bool = False,
                      htext: Union[HelpText, None] = None):
        """
        Make a special argument using a special DrsArgument method (function)
        to supplies the properties of this special argument

        :param function: function, a DrsArgument method
                         (i.e. DrsArgument.make_XXX)
        :param skip: bool, force the skip to be True - if skip is True does not
                     run the recipe just runs the function and then exits
        :param htext: HelpText - the language database for help text (used
                      to set help via the function call

        :return: None - updates DrsRecipe.specialargs
        """
        # set function name
        _ = display_func(self.params, '_make_special', __NAME__,
                         self.class_name)
        # make debug functionality
        props = function(self.params, htext=htext)
        name = props['name']
        try:
            spec = DrsArgument(name, kind='special', altnames=props['altnames'])
        except ArgumentError:
            sys.exit(0)
        spec.assign_properties(props)
        spec.skip = skip
        spec.helpstr = props['help']
        self.specialargs[name] = spec

    def _drs_usage(self) -> str:
        """
        Create a string that shows this recipes usage

        i.e.

        Usage: {name} {args} {optional args}

        :return: str, the usage string (for use in --help --info etc)
        """
        # set function name
        _ = display_func(self.params, '_drs_usage', __NAME__, self.class_name)
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
            pos_args = ['[{0}]'.format(self.helptext['POS_ARG_TEXT'])]
        # define usage
        uargs = [self.name, ' '.join(pos_args), self.helptext['OPTIONS_TEXT']]
        usage = '{0}.py {1} [{2}]'.format(*uargs)
        return usage


class DrsRunSequence:
    def __init__(self, name: str, instrument: str = 'None'):
        """
        Construct a Drs Run Sequence (used in processing a set of recipes)

        :param name: str, name of sequence
        :param instrument: str, the instrument this sequence belongs to
        """
        # set class name
        self.class_name = 'DrsRunSequence'
        # set function name
        _ = display_func(None, '__init__', __NAME__, self.class_name)
        # set the name of the sequence
        self.name = name
        # set the instrument this sequence belongs to
        self.instrument = instrument
        # set up storage for recipes in this sequence (as a list)
        self.sequence = []
        # set up storage for recipes to add to sequence (before actually
        #    assigning them to the sequence as this is not instantaneous)
        self.adds = []
        # set up storage for the telluric stars list
        self.tstars = None
        # set up storage for the non-telluric stars list
        self.ostars = None

    def __getstate__(self) -> dict:
        """
        For when we have to pickle the class
        :return:
        """
        # set function name
        _ = display_func(None, '__getstate__', __NAME__, self.class_name)
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
        # set function name
        _ = display_func(None, '__setstate__', __NAME__, self.class_name)
        # update dict with state
        self.__dict__.update(state)

    def __str__(self) -> str:
        """
        Return the string representation of the class
        :return:
        """
        # set function name
        _ = display_func(None, '__str__', __NAME__, self.class_name)
        # return string representation
        return self.__repr__()

    def __repr__(self) -> str:
        """
        Return the string representation of the class
        :return:
        """
        # set function name
        _ = display_func(None, '__str__', __NAME__, self.class_name)
        # return string representation
        return '{0}[{1}]'.format(self.class_name, self.name)

    def add(self, recipe: DrsRecipe, name: Union[str, None] = None,
            master: Union[bool, None] = None, fiber: Union[str, None] = None,
            arguments: Union[Dict[str, Any], None] = None,
            filters: Union[Dict[str, Any], None] = None,
            files: Union[List[DrsInputFile], None] = None,
            rargs: Union[Dict[str, List[DrsInputFile]], None] = None,
            rkwargs: Union[Dict[str, List[DrsInputFile]], None] = None):
        """
        Add a recipe to the sequence, can overwrite default recipe behaviour
        with the name (shortname), master, fiber keys and add more specialised
        commands with:
        - arguments: a dictionary of arguments to parse directly to the recipe
                     (i.e. if a recipe has --objname add arguments['objname']
                      with the require value(s) to push
                      i.e. arguments['objname'] = 'SCIENCE_TARGETS'
        - filters: a dictionary of header keyword keys (i.e. KW_XXX) these are
                   used to filter files that can be used with this recipe
                   i.e. filter['KW_DPRTYPE'] = FLAT_FLAT would only allow
                   files with header key matching KW_DPRTYPE (from constants)
                   with the value of 'FLAT_FLAT'
        - files: a list of DrsInputfile (or DrsFitFiles/DrsNpyFiles) that can
                 be used with this recipe (usually when a recipe has the
                 "files" positional argument

        :param recipe: DrsRecipe, a DrsRecipe instance to add to the sequence
        :param name: str, the short name to give the recipe (used to distinguish
                     two nearly identical DrsRecipe instances from each other)
                     i.e. when using cal_dark (shortname=DARK) can have
                     DARK1 and DARK2 in same sequence
        :param master: bool, if True mark this recipe as a master sequence
                       affects skipping and adds the --master=True argument
        :param fiber: str, the fiber allowed for this recipe
        :param arguments: dict, a dictionary of arguments to parse directly
                          to the recipe (i.e. if a recipe has --objname add
                          arguments['objname'] with the require value(s) to push
                          i.e. arguments['objname'] = 'SCIENCE_TARGETS'
        :param filters: dict, a dictionary of header keyword keys (i.e. KW_XXX)
                        these are used to filter files that can be used with
                        this recipe i.e. filter['KW_DPRTYPE'] = FLAT_FLAT would
                        only allow  files with header key matching KW_DPRTYPE
                        (from constants) with the value of 'FLAT_FLAT'
        :param files: a list of DrsInputfile (or DrsFitFiles/DrsNpyFiles)
                      that can be used with this recipe (usually when a recipe
                      has the "files" positional argument
        :param rargs: dictionary, keys are positional argument names -
                      where positional argument is of type 'files', values
                      are a list of DrsInputFiles - the files that this
                      argument is allowed to have
        :param rkwargs: dictionary, keys are optional argument names -
                        where positional argument is of type 'files', values
                        are a list of DrsInputFiles - the files that this
                        argument is allowed to have

        :return: None - updates DrsRunSequence.adds
        """
        # set function name
        _ = display_func(recipe.params, 'add', __NAME__, self.class_name)
        # add these parameters to keyword args
        add_set = dict()
        add_set['recipe'] = recipe
        add_set['name'] = name
        add_set['master'] = master
        add_set['fiber'] = fiber
        add_set['arguments'] = arguments
        add_set['filters'] = filters
        add_set['files'] = files
        # deal with adding recipe arguments
        if rargs is None:
            rargs = dict()
        # make sure we add files to positional arguments
        if files is not None:
            rargs['files'] = files
        # now add arguments to set
        add_set['args'] = rargs
        # add kwargs (optional arguments) to set
        add_set['kwargs'] = rkwargs
        # append to to adds
        self.adds.append(add_set)

    def process_adds(self, params: ParamDict,
                     tstars: Union[List[str], None] = None,
                     ostars: Union[List[str], None] = None):
        """
        Process the DrsRunSequence.adds list (that have been added/defined
        previous) - this actually creates copies of the recipes and modifies
        them according to the settings in DrsRecipeSequence.adds

        :param params: ParamDict, the parameter dictionary of constants
        :param tstars: list of strings, the list of telluric stars (OBJECT
                       names)
        :param ostars: list of strings, the list of non-telluric stars (OBJECT
                       names)

        :return: None - updates DrsRunSequence.sequence
        """
        # set function name
        _ = display_func(params, 'process_adds', __NAME__, self.class_name)
        # set telluric stars (may be needed)
        self.tstars = tstars
        # set other stars
        self.ostars = ostars
        # get filemod and recipe mod
        pconst = constants.pload(self.instrument)
        filemod = pconst.FILEMOD()
        recipemod = pconst.RECIPEMOD()
        # storage of sequences
        self.sequence = []
        # loop around the added recipes to sequence
        for add in self.adds:
            # set up new recipe
            frecipe = DrsRecipe(self.instrument)
            # copy from given recipe
            frecipe.copy(add['recipe'])
            # set filemod and recipemod
            frecipe.filemod = filemod
            frecipe.recipemod = recipemod
            # update short name
            if add['name'] is not None:
                frecipe.shortname = add['name']
            # set fiber
            if add['fiber'] is not None:
                frecipe.allowedfibers = add['fiber']
            # add filters
            frecipe = self.add_filters(frecipe, add['files'], add['filters'])
            # update file definitions
            frecipe = self.update_args(frecipe, arguments=add['arguments'],
                                       rargs=add['args'], rkwargs=add['kwargs'])
            # update master
            if add['master'] is not None:
                frecipe.master = add['master']
            # add to sequence storage
            self.sequence.append(frecipe)

    def add_filters(self, frecipe: DrsRecipe,
                    files: Union[List[drs_file.DrsFitsFile], None] = None,
                    infilters: Union[Dict[str, Any], None] = None) -> DrsRecipe:
        """
        Add the filters to frecipe.filters (normally from DrsRunSequence.adds

        :param frecipe: DrsRecipe, the Drs recipe to add the filters to
        :param files: list of DrsFitsFile instances - if header keys are not
                      set in infilters these files are used to get a list of
                      required header keys - keys should have KW_XXX and
                      values are the test of a valid file
                      (from DrsFitsFile.required_header_keys)
        :param infilters: dictionary of keyword headers where keys should have
                          KW_XXX and values are the test of a valid file
                          overrides keys coming from 'files' input

        :return: DrsRecipe, the Drs recipe with updated DrsRecipe.filters
        """
        # set function name
        _ = display_func(None, 'add_filters', __NAME__, self.class_name)
        # add filters
        filters = dict()
        # loop around in filters and add them (if they start with KW_)
        if infilters is not None:
            for infilter in infilters:
                if 'KW_' in infilter:
                    filters[infilter] = infilters[infilter]
        # add keyword args from file arguments
        if files is not None:
            if isinstance(files, drs_file.DrsFitsFile):
                files = [files]
            # loop around files and find file filters
            file_filters = dict()
            # loop around  files and get filters from files
            for fileinst in files:
                # get rkeys
                rkeys = fileinst.required_header_keys
                # loop around rkeys and add only those not present in filters
                for key in rkeys:
                    if 'KW_' in key:
                        # need to deal with having multiple files defined
                        if key in file_filters:
                            file_filters[key].append(rkeys[key])
                        else:
                            file_filters[key] = [rkeys[key]]
            # if file filter not in filters use the file filter
            #   i.e. filters that already exist take precedence
            for key in file_filters:
                if key not in filters:
                    filters[key] = file_filters[key]
        # add to new recipe
        frecipe.filters = filters
        # return frecipe
        return frecipe

    def update_args(self, frecipe: DrsRecipe,
                    arguments: Union[Dict[str, Any], None] = None,
                    rargs: Union[Dict[str, List[DrsInputFile]], None] = None,
                    rkwargs: Union[Dict[str, List[DrsInputFile]], None] = None
                    ) -> DrsRecipe:
        """
        Update the recipes arguments (usually based on 'arguments' from
        DrsRunSequence.adds) - these are copied from the reference copy of
        the recipe via rargs and rkwargs

        :param frecipe: DrsRecipe - the recipe to update the arguments of
        :param arguments: dictionary of arguments to update the currently set
                          positional arguments (DrsRecipe.args) and the
                          optional arguments (DrsRecipe.kwargs)
        :param rargs: dictionary, keys are positional argument names, values
                      are the values to assign to each argument
        :param rkwargs: dictionary, keys are optional argument names, values
                        are the values to assign to each argument

        :return: DrsRecipe, the updated drs recipe
        """
        # set function name
        _ = display_func(None, 'update_args', __NAME__, self.class_name)
        # deal with arguments overwrite
        if arguments is not None:
            frecipe.add_extra(arguments, tstars=self.tstars,
                              ostars=self.ostars)
        # ------------------------------------------------------------------
        # update args - loop around positional arguments
        if rargs is not None:
            frecipe.args = self._update_arg(frecipe.args, rargs)
        # ------------------------------------------------------------------
        # update kwargs - loop around positional arguments
        if rkwargs is not None:
            frecipe.kwargs = self._update_arg(frecipe.kwargs, rkwargs)
        # ------------------------------------------------------------------
        # return recipes
        return frecipe

    def _update_arg(self, arguments: Dict[str, DrsArgument],
                    fargs: Dict[str, List[DrsInputFile]]
                    ) -> Dict[str, DrsArgument]:
        """
        Update either the positional args (DrsRecipe.args) or optional args
        (DrsRecipe.kwargs)

        :param arguments: dictionary of args (args or kwargs) - these are what
                          we are going to update with (if and only if they are
                          present as arguments in fargs)
        :param fargs: dictionary, keys are argument names (positional or
                      optional), values are the values to assign to each
                      argument

        :return: dictionary of args (args or kwargs) - updated correctly
        """
        # set function name
        _ = display_func(None, '_update_arg', __NAME__, self.class_name)
        # loop around each argument
        for argname in arguments:
            # if argument is found in fargs then we need to update the
            #   .files of this argument
            if argname in fargs:
                # get the value of each key
                # value here should be a list of drs file arguments or None
                value = fargs[argname]
                # if we have a file or files we need to copy them properly
                if arguments[argname].dtype in ['files', 'file']:
                    # if the value is None the frecipe arg should be set to None
                    if value is None:
                        # set the value to None
                        arguments[argname].files = None
                    else:
                        # set up empty set
                        arguments[argname].files = []
                        # loop around files
                        for drsfile in value:
                            # check that we4
                            if isinstance(drsfile, DrsInputFile):
                                # copy file
                                drsfilecopy = drsfile.completecopy(drsfile)
                                # append to new list
                                arguments[argname].files.append(drsfilecopy)
        # return the arguments
        return arguments


# TODO: Move to drs_exceptions?
# Drs Recipe Exception
class DrsRecipeException(Exception):
    pass


# =============================================================================
# Define file check functions
# =============================================================================
# TODO: Should this be used?
def make_default_recipe(params: ParamDict = None,
                        name: str = None) -> DrsRecipe:
    """
    Create a blank version of a recipe
    :param params: ParamDict, the parameter dictionary of constants
    :param name: str, the name of the recipe
    :return:
    """
    # return a 'blank' instance of the DrsRecipe
    return DrsRecipe(params=params, name=name)


# =============================================================================
# Define run making functions
# =============================================================================
# define complex type argdict
ArgDictType = Union[Dict[str, Table], OrderedDict, None]


def find_run_files(params: ParamDict, recipe: DrsRecipe,
                   table: Table, args: Dict[str, DrsArgument],
                   filters: Union[Dict[str, Any], None] = None,
                   allowedfibers: Union[List[str], str, None] = None,
                   absfile_col: Union[str, None] = None,
                   check_required: bool = False) -> Dict[str, ArgDictType]:
    """
    Given a specifc recipe and args (args or kwargs) use the other arguments
    to generate a set of astropy.table.Table for each arg (args or kwargs)
    - it does this via checking the full 'table' against all filters etc
    and returns (for each arg/kwargs)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe for which to find files (uses some
                   properties (i.e. extras and master) already set previously
    :param table: astropy.table.Table - the full table (must contain all
                  filter keys as columns
    :param args: dict, either args or kwargs - the DrsRecipe.args or
                 DrsRecipe.kwargs to use - produces a table for each key in
                 this dict
    :param filters: dict, the keys to check (should be KW_XXX) and should also
                    be columns in 'table'
    :param allowedfibers: str, the allowed fiber(s) (should be in KW_FIBER
                          column in 'table'
    :param absfile_col: str, the absolute file column name (if not set is taken
                        from params['REPROCESS_ABSFILECOL'] - recommended
    :param check_required: bool, if True checks whether parameter is required
                           (set in argument definition - in recipe definition)

    :return: a dictionary for each 'arg' key, each dictionary has a
             sub-dictionary for each unique drsfile type found (the value of
             the sub-dictionary is an astropy.table - a sub-set of the full
             table matching this argument/drsfile combination
    """
    # set function name
    func_name = display_func(params, 'find_run_files', __NAME__)
    # storage for valid files for each argument
    filedict = OrderedDict()
    # get constants from params
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', func=func_name,
                         override=absfile_col)
    # get raw filenames from table
    files = table[absfile_col]
    # debug log the number of files found
    dargs = [func_name, len(files)]
    WLOG(params, 'debug', TextEntry('90-503-00011', args=dargs))
    # loop around arguments
    for argname in args:
        # get arg instance
        arg = args[argname]
        # if check required see if parameter is required
        if check_required:
            if not arg.required and not arg.reprocess:
                continue
        # see if we are over writing argument
        if argname in recipe.extras:
            filedict[argname] = recipe.extras[argname]
            continue
        # make sure we are only dealing with dtype=files
        if arg.dtype not in ['file', 'files']:
            # deal with directory (special argument) - if we have a
            #   master night use the master night as the directory name
            if arg.dtype == 'directory' and recipe.master:
                filedict[argname] = params['MASTER_NIGHT']
            # else set the file dict value to the default value
            # TODO: Need a better option for this!!
            # TODO:   i.e. when we need values to be set from the header
            else:
                filedict[argname] = arg.default
            continue
        # add sub-dictionary for each drs file
        filedict[argname] = OrderedDict()
        # debug log: the argument being scanned
        WLOG(params, 'debug', TextEntry('90-503-00012', args=[argname]))
        # get drs file instances
        drsfiles = arg.files
        # if files are None continue
        if drsfiles is None:
            continue
        # ------------------------------------------------------------------
        # mask table by filters (if filters in table)
        filtermask = np.ones(len(table), dtype=bool)
        for tfilter in filters:
            if tfilter in table.colnames:
                # deal with filter values being list/str
                if isinstance(filters[tfilter], str):
                    testvalues = [filters[tfilter]]
                elif isinstance(filters[tfilter], list):
                    testvalues = filters[tfilter]
                else:
                    continue
                # create a test mask
                testmask = np.zeros(len(table), dtype=bool)
                # loop around test values with OR (could be any value)
                for testvalue in testvalues:
                    # check if value is string
                    if isinstance(testvalue, str):
                        values = np.char.array(table[tfilter])
                        values = values.strip().upper()
                        testvalue = testvalue.strip().upper()
                    else:
                        values = np.array(table[tfilter])

                    # criteria 1: value == testvalue
                    vcond1 = values == testvalue
                    # criteria 2: value in [None, 'None', '']
                    vcond2 = np.in1d(values, [None, 'None', ''])
                    # check mask
                    testmask |= (vcond1 | vcond2)
                # add filter to filter mask with AND (must have all filters)
                filtermask &= testmask
        # ------------------------------------------------------------------
        # loop around drs files
        for drsfile in drsfiles:
            # copy table
            ftable = Table(table[filtermask])
            ffiles = np.array(files)[filtermask]
            # set params for drsfile
            drsfile.params = params
            # debug log: the file being tested
            dargs = [drsfile.name]
            WLOG(params, 'debug', TextEntry('90-503-00013', args=dargs))
            # define storage (if not already defined)
            cond1 = drsfile.name not in filedict[argname]
            if cond1 and (arg.filelogic == 'exclusive'):
                filedict[argname][drsfile.name] = []
            elif 'all' not in filedict[argname]:
                filedict[argname]['all'] = []
            # list of valid files
            valid_infiles = []
            valid_outfiles = []
            valid_num = 0
            # loop around files
            for f_it, filename in enumerate(ffiles):
                # print statement
                pargs = [drsfile.name, f_it + 1, len(ffiles)]
                pmsg = '\t\tProcessing {0} file {1}/{2}'.format(*pargs)
                drs_log.Printer(None, None, pmsg)
                # get infile instance (i.e. raw or pp file) and assign the
                #   correct outfile (from filename)
                out = drsfile.get_infile_outfilename(recipe.name,
                                                     filename, allowedfibers)
                infile, valid, outfilename = out
                # if still valid add to list
                if valid:
                    valid_infiles.append(infile)
                    valid_outfiles.append(outfilename)
                    valid_num += 1
                else:
                    valid_infiles.append(None)
                    valid_outfiles.append(None)
            # debug log the number of valid files
            WLOG(params, 'debug', TextEntry('90-503-00014', args=[valid_num]))
            # add outfiles to table
            ftable['OUT'] = valid_outfiles
            # for the valid files we can now check infile headers
            for it in range(len(ftable)):
                # get infile
                infile = valid_infiles[it]
                # skip those that were invalid
                if infile is None:
                    continue
                # else make sure params is set
                else:
                    infile.params = params
                # get table dictionary
                tabledict = dict(zip(ftable.colnames, ftable[it]))
                # check whether tabledict means that file is valid for this
                #   infile
                valid1 = infile.check_table_keys(tabledict)
                # do not continue if valid1 not True
                if not valid1:
                    continue
                # check whether filters are found
                valid2 = infile.check_table_keys(tabledict, rkeys=filters)
                # do not continue if valid2 not True
                if not valid2:
                    continue
                # if valid then add to filedict for this argnameand drs file
                if arg.filelogic == 'exclusive':
                    filedict[argname][drsfile.name].append(ftable[it])
                else:
                    filedict[argname]['all'].append(ftable[it])
    outfiledict = OrderedDict()
    # convert each appended table to a single table per file
    for argname in filedict:
        # deal with non-list arguments
        if not isinstance(filedict[argname], OrderedDict):
            outfiledict[argname] = filedict[argname]
            continue
        else:
            # add sub dictionary
            outfiledict[argname] = OrderedDict()
        # loop around drs files
        for name in filedict[argname]:
            # get table list
            tablelist = filedict[argname][name]
            # deal with combining tablelist
            outfiledict[argname][name] = vstack_cols(params, tablelist)
    # return filedict
    return outfiledict


def group_run_files(params: ParamDict, recipe: DrsRecipe,
                    argdict: Dict[str, ArgDictType],
                    kwargdict: Dict[str, ArgDictType],
                    nightcol: Union[str, None] = None) -> List[Dict[str, Any]]:
    """
    Take the arg and kwarg dictionary of tables (argdict and kwargdict) and
    force them into groups (based on sequence number and number in sequence)
    for each positional/optional argument. Then take these sets of files
    and push them into recipe runs (one set of files for each recipe run)
    return is a list of these runs where each 'run' is a dictionary of
    arguments each with the values that specific argument should have

    i.e. cal_extract should have at least ['directory', 'files']

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe these args/kwargs are associated with
    :param argdict: dict, a dictionary of dictionaries containing a table of
                    files each - top level key is a positional argument for this
                    recipe and sub-dict key is a DrsFitsFile instance i.e.:
                    argdict[argument][drsfile] = Table
    :param kwargdict: dict, a dictionary of dictionaries containing a table of
                    files each - top level key is an optional argument for this
                    recipe and sub-dict key is a DrsFitsFile instance i.e.:
                    kwargdict[argument][drsfile] = Table
    :param nightcol: str or None, if set overrides the
                     params['REPROCESS_NIGHTCOL'] value (which sets the column
                     in the index database that has the night sub directory
                     information
    :return: a list of dictionaries, each dictionary is a different run.
             each 'run' is a dictionary of arguments each with the values that
             specific argument should have
    """
    # set function name
    func_name = display_func(params, 'group_run_files', __NAME__)
    # get parameters from params
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', func=func_name,
                       override=nightcol)
    # flag for having no file arguments
    has_file_args = False
    # ----------------------------------------------------------------------
    # first loop around arguments
    for argname in argdict:
        # get this arg
        arg = argdict[argname]
        # deal with other parameters (not 'files' or 'file')
        if recipe.args[argname].dtype not in ['file', 'files']:
            continue
        # flag that we have found a file argument
        has_file_args = True
        # get file limit
        limit = recipe.args[argname].limit
        # deal with files (should be in drs groups)
        for name in argdict[argname]:
            # check for None
            if arg[name] is None:
                continue
            # copy row as table
            intable = Table(arg[name])
            # assign individual group numbers / mean group date
            gargs = [params, intable]
            argdict[argname][name] = _group_drs_files(*gargs, limit=limit)
    # ----------------------------------------------------------------------
    # second loop around keyword arguments
    for kwargname in kwargdict:
        # get this kwarg
        kwarg = kwargdict[kwargname]
        # deal with other parameters (not 'files' or 'file')
        if recipe.kwargs[kwargname].dtype not in ['file', 'files']:
            continue
        # flag that we have found a file argument
        has_file_args = True
        # get file limit
        limit = recipe.kwargs[kwargname].limit
        # deal with files (should be in drs groups)
        for name in kwargdict[kwargname]:
            # check for None
            if kwarg[name] is None:
                continue
            # copy row as table
            intable = Table(kwarg[name])
            # assign individual group numbers / mean group date
            gargs = [params, intable]
            kwargdict[kwargname][name] = _group_drs_files(*gargs, limit=limit)
    # ----------------------------------------------------------------------
    # figure out arg/kwarg order
    runorder, rundict = _get_argposorder(recipe, argdict, kwargdict)
    # ----------------------------------------------------------------------
    # brute force approach
    runs = []
    # ----------------------------------------------------------------------
    # deal with no file found (only if we expect to have files)
    if has_file_args:
        all_none = False
        for runarg in runorder:
            # need to check required criteria
            if runarg in recipe.args:
                required = recipe.args[runarg].required
                dtype = recipe.args[runarg].dtype
            else:
                required = recipe.kwargs[runarg].required
                dtype = recipe.kwargs[runarg].dtype
            # only check if file is required and argument is a file type
            if required and dtype in ['file', 'files']:
                # if whole dict is None then all_none is True
                if rundict[runarg] is None:
                    all_none = True
                # if we have entries we have to check each of them
                else:
                    # test this run arg
                    entry_none = False
                    # loop around entries
                    for entry in rundict[runarg]:
                        # if entry is None --> entry None is True
                        if rundict[runarg][entry] is None:
                            entry_none |= True
                    # if entry_none is True then all_none is True
                    if entry_none:
                        all_none = True
        # if all none is True then return no runs
        if all_none:
            return []
    # ----------------------------------------------------------------------
    # find first file argument
    fout = _find_first_filearg(params, runorder, argdict, kwargdict)
    # if fout is None means we have no file arguments
    if fout is None:
        # get new run
        new_runs = _gen_run(params, rundict=rundict, runorder=runorder,
                            masternight=recipe.master)
        # finally add new_run to runs
        runs += new_runs
    else:
        arg0, drsfiles0 = fout
        # ----------------------------------------------------------------------
        # loop around drs files in first file argument
        for drsfilekey in drsfiles0:
            # condition to stop trying to match files
            cond = True
            # set used groups
            usedgroups = dict()
            # get drs table
            drstable = rundict[arg0][drsfilekey]
            # get group column from drstable
            groups = np.array(drstable['GROUPS']).astype(int)
            # get unique groups from groups
            ugroups = np.sort(np.unique(groups))
            # keep matching until condition met
            while cond:
                # print statement
                pmsg = '\t\tProcessing run {0}'.format(len(runs))
                drs_log.Printer(None, None, pmsg)
                # check for None
                if rundict[arg0][drsfilekey] is None:
                    break
                # get first group
                nargs = [arg0, drstable, usedgroups, groups, ugroups]
                gtable0, usedgroups = _find_next_group(*nargs)
                # check for grouptable unset --> skip
                if gtable0 is None:
                    break
                # get night name for group
                nightname = gtable0[night_col][0]
                # get mean time for group
                meantime = gtable0['MEANDATE'][0]
                # _match_groups raises exception when finished so need a
                #   try/except here to catch it
                try:
                    new_runs = _gen_run(params, rundict, runorder, nightname,
                                        meantime, arg0, gtable0,
                                        masternight=recipe.master)
                # catch exception
                except DrsRecipeException:
                    continue
                # finally add new_run to runs
                runs += new_runs
    # deal with master (should only be 1)
    if recipe.master:
        return [runs[0]]
    else:
        # return runs
        return runs


def convert_to_command(params: ParamDict, recipe: DrsRecipe,
                       runargs: List[Dict[str, Any]]) -> List[str]:
    """
    Converts our list of dictionaries (for each run) to a list of strings,
    each string representing what would be entered on the command line

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe instance this is for
    :param runargs: a list of dictionaries, each dictionary is a different run.
                    each 'run' is a dictionary of arguments each with the
                    values that specific argument should have
    :return: list of strings, each string representing what would be entered
             on the command line
    """
    # set function name
    _ = display_func(params, 'convert_to_command', __NAME__)
    # get args/kwargs from recipe
    args = recipe.args
    kwargs = recipe.kwargs
    # define storage
    outputs = []
    # loop around arguement
    for runarg in runargs:
        # command first arg
        command = '{0} '.format(recipe.name)
        # get run order
        runorder, _ = _get_argposorder(recipe, runarg, runarg)
        # loop around run order
        for argname in runorder:
            # get raw value
            rawvalue = runarg[argname]
            # deal with lists
            if isinstance(rawvalue, list):
                value = ' '.join(runarg[argname])
            else:
                value = str(rawvalue)
            # deal with arguments
            if argname in args:
                # add to command
                command += '{0} '.format(value)
            # deal with keyword arguments
            if argname in kwargs:
                # add to command
                command += '--{0} {1} '.format(argname, value)
        # append to out (removing trailing white spaces)
        outputs.append(command.strip())
    # return outputs
    return outputs


# =============================================================================
# Define worker functions
# =============================================================================
def _group_drs_files(params: ParamDict, drstable: Table,
                     night_col: Union[str, None] = None,
                     seq_col: Union[str, None] = None,
                     time_col: Union[str, None] = None,
                     limit: Union[int, None] = None) -> Table:
    """
    Take a table (astropy.table.Table) "drstable" and sort them
    by observation time - such that if the sequence number increases
    (info stored in seq_col) files should be grouped together. If next entry
    has a sequence number lower than previous seqeunce number this is a new
    group of files.
    Note "drstable" must only contain rows with same (DrsFitsFile) type of files
    i.e. they are meant to be compared as part of the same group (if the follow
    sequentially)

    :param params: ParamDict, parameter dictionary of constants
    :param drstable: astropy.table.Table - the table of files where all
                     rows should be files of the same DrsFitsFile type
                     i.e. all FLAT_FLAT
    :param night_col: str or None, if set overrides params['REPROCESS_NIGHTCOL']
                      - which sets which column in drstable has the night
                      sub-directory information
    :param seq_col: str or None, if set overrides params['REPROCESS_SEQCOL']
                    - which sets the sequence number column i.e.
                    1,2,3,4,1,2,3,1,2,3,4  is 3 groups of objects (4,3,4)
                    when sorted in time (by 'time_col')
    :param time_col: str or None, if set overrides params['REPROCESS_TIMECOL']
                    - which is the column to sort the drstable by (and thus
                    put sequences in time order) - must be a float time
                    (i.e. MJD) in order to be sortable
    :param limit: int or None, if set sets the number of files allowed to be
                  in a group - if group gets to more than this many files starts
                  a new group (i.e. may break-up sequences) however new
                  sequences should start a new group even if less than limit
                  number
    :return: astropy.table.Table - the same drstable input - but with two
             new columns 'GROUPS' - the group number for each object, and
             'MEANDATE' - the mean of time_col for that group (helps when
             trying to match groups of differing files
    """

    # set function name
    func_name = display_func(params, '_group_drs_files', __NAME__)
    # get properties from params
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', func=func_name,
                       override=night_col)
    seq_colname = pcheck(params, 'REPROCESS_SEQCOL', func=func_name,
                         override=seq_col)
    time_colname = pcheck(params, 'REPROCESS_TIMECOL', func=func_name,
                          override=time_col)
    # deal with limit unset
    if limit is None:
        limit = np.inf
    # sort drstable by time column
    sortmask = np.argsort(drstable[time_colname])
    drstable = drstable[sortmask]
    # st up empty groups
    groups = np.zeros(len(drstable))
    # get the sequence column
    sequence_col = drstable[seq_colname]
    # start the group number at 1
    group_number = 0
    # set up night mask
    valid = np.zeros(len(drstable), dtype=bool)
    # by night name
    for night in np.unique(list(drstable[night_col])):
        # deal with just this night name
        nightmask = drstable[night_col] == night
        # deal with only one file in nightmask
        if np.sum(nightmask) == 1:
            group_number += 1
            groups[nightmask] = group_number
            valid |= nightmask
            continue
        # set invalid sequence numbers to 1
        sequence_mask = sequence_col.astype(str) == ''
        sequence_col[sequence_mask] = 1
        # get the sequence number
        sequences = sequence_col[nightmask].astype(int)
        indices = np.arange(len(sequences))
        # get the raw groups
        rawgroups = np.array(-(sequences - indices) + 1)
        # set up group mask
        nightgroup = np.zeros(np.sum(nightmask))
        # loop around the unique groups and assign group number
        for rgroup in np.unique(rawgroups):
            # new group
            group_number += 1
            # set up sub group parameters
            subgroupnumber, it = 0, 0
            # get group mask
            groupmask = rawgroups == rgroup
            # get positions
            positions = np.where(groupmask)[0]
            # deal with limit per group
            if np.sum(groupmask) > limit:
                # loop around all elements in group (using groupmask)
                while it < np.sum(groupmask):
                    # find how many are in this grup
                    subgroupnumber = np.sum(nightgroup == group_number)
                    # if we are above limit then start a new group
                    if subgroupnumber >= limit:
                        group_number += 1
                    nightgroup[positions[it]] = group_number
                    # iterate
                    it += 1
            else:
                # push the group number into night group
                nightgroup[groupmask] = group_number

        # add the night group to the full group
        groups[nightmask] = nightgroup
        # add to the valid mask
        valid |= nightmask

    # add groups and valid to dict
    drstable['GROUPS'] = groups
    # mask by the valid mask
    drstable = drstable[valid]

    # now work out mean time for each group
    # start of mean dates as zeros
    meandate = np.zeros(len(drstable))
    # get groups from table
    groups = drstable['GROUPS']
    # loop around each group and change the mean date for the files
    for g_it in range(1, int(max(groups)) + 1):
        # group mask
        groupmask = (groups == g_it)
        # group mean
        groupmean = np.mean(drstable[time_colname][groupmask])
        # save group mean
        meandate[groupmask] = groupmean
    # add meandate to drstable
    drstable['MEANDATE'] = meandate
    # return the group
    return drstable


def _get_argposorder(recipe: DrsRecipe, argdict: Dict[str, ArgDictType],
                     kwargdict: Dict[str, ArgDictType]
                     ) -> Tuple[List[str], Dict[str, ArgDictType]]:
    """
    Get the arguent position order

    Take the dictionaries of arguments and figure out which order these
    positional arguments and keyword arguments should be in for this recipe
    i.e. cal_extract  directory comes before files and before optional arguments

    for positional arguments this is defined by recipe.args[{arg}].pos,
    for optional arguments they are added to the end in whichever order they
    come

    :param recipe: DrsRecipe, the recipe instance these arguments belong to
    :param argdict: dictionary of values for each of the positional arguments
                   (each key is a positional argument name, each value is the
                    value that argument should have i.e.
                    directory should have value '2019-04-20'
                    --> dict(directory='2019-04-20', files=[file1, file2])
    :param kwargdict: dictionary of values for each of the optional arguments
                      (each key is an optional argument name, each value is the
                      value that argument should have i.e.
                      --{key}={value}    --plot=1
                      --> dict(plot=1)
    :return: tuple,
             1. runorder: list of strings of argument names, in the correct
                order - the value is the name of the argument
                (i.e. DrsArgument.name),
             2. rundict: a dictionary where the keys are the argument name and
                the value are a dictionary of DrsFitFile names and the values
                of these are astropy.table.Tables containing the
                files associated with this [argument][drsfile]
    """
    # set function name
    _ = display_func(recipe.params, '_get_argposorder', __NAME__)
    # set up storage
    runorder = OrderedDict()
    # get args/kwargs from recipe
    args = recipe.args
    kwargs = recipe.kwargs
    # iterator for non-positional variables
    it = 0
    # loop around args
    for argname in args.keys():
        # must be in rundict keys
        if argname not in argdict.keys():
            continue
        # get arg
        arg = args[argname]
        # deal with non-required arguments when argdict has no values
        #    these are allowed only if arg.reprocess is True
        #    we skip adding to runorder
        if hasattr(argdict[argname], '__len__'):
            arglen = len(argdict[argname])
            if arg.reprocess and not arg.required and (arglen == 0):
                continue
        # get position or set it using iterator
        if arg.pos is not None:
            runorder[arg.pos] = argname
        else:
            runorder[1000 + it] = argname
            it += 1
    # loop around args
    for kwargname in kwargs.keys():
        # must be in rundict keys
        if kwargname not in kwargdict.keys():
            continue
        # get arg
        kwarg = kwargs[kwargname]
        # deal with non-required arguments when argdict has no values
        #    these are allowed only if arg.reprocess is True
        #    we skip adding to runorder
        if hasattr(kwargdict[kwargname], '__len__'):
            kwarglen = len(kwargdict[kwargname])
            if kwarg.reprocess and not kwarg.required and (kwarglen == 0):
                continue
        # get position or set it using iterator
        if kwarg.pos is not None:
            runorder[kwarg.pos] = kwargname
        else:
            runorder[1000 + it] = kwargname
            it += 1
    # recast run order into a numpy array of strings
    sortrunorder = np.argsort(list(runorder.keys()))
    runorder = np.array(list(runorder.values()))[sortrunorder]
    # merge argdict and kwargdict
    rundict = dict()
    for rorder in runorder:
        if rorder in argdict:
            rundict[rorder] = argdict[rorder]
        else:
            rundict[rorder] = kwargdict[rorder]
    # return run order and run dictionary
    return list(runorder), rundict


def _gen_run(params: ParamDict, rundict: Dict[str, ArgDictType],
             runorder: List[str], nightname: Union[str, None] = None,
             meantime: Union[float, None] = None,
             arg0: Union[str, None] = None, gtable0: Union[Table, None] = None,
             masternight: bool = False) -> List[Dict[str, Any]]:
    """
    Generate a recipe run dictionary of arguments based on the argument position
    order and if a secondary argument has a list of files match appriopriately
    with arg0 (using meantime) - returns a list of runs of this recipe
    where each entry is a dictionary where the key is the argument name and the
    value is the value(s) that argument can take

    :param params: ParamDict, parameter dictionary of constants
    :param rundict: a dictionary where the keys are the argument name and the
                    value are a dictionary of DrsFitFile names and the values
                    of these are astropy.table.Tables containing the
                    files associated with this [argument][drsfile]
    :param runorder: list of strings, the argument names in the correct order
    :param nightname: str or None, sets the night name (i.e. directory) for
                      this recipe run (if None set from params['NIGHTNAME']
    :param meantime: float or None, sets the mean time (as MJD) for this
                     argument (associated to a set of files) - used when we have
                     a second set of files that need to be matched to the first
                     set of files, if not set meantime = 0.0
    :param arg0: str or None, if set this is the name of the first argument
                 that contains files (name comes from DrsArgument.name)
    :param gtable0: astropy.table.Table or None, if set this is the the case
                    where argname=arg0, and thus the file set should come from
                    a list of files
    :param masternight: bool, if True this is a master recipe, and therefore
                        the nightname should be the master night, master night
                        is obtained from params['MASTER_NIGHT']

    :return: a list of runs of this recipe where each entry is a dictionary
             where the key is the argument name and the value is the value(s)
             that argument can take
    """
    # set function name
    _ = display_func(params, '_gen_run', __NAME__)
    # deal with unset values (not used)
    if arg0 is None:
        arg0 = ''
    if gtable0 is None:
        gtable0 = dict(filecol=None)
    if nightname is None:
        nightname = params['NIGHTNAME']
    if masternight:
        nightname = params['MASTER_NIGHT']
    if meantime is None:
        meantime = 0.0

    # need to find any argument that is not files but is a list
    pkeys, pvalues = [], []
    for argname in runorder:
        # only do this for numpy arrays and lists (not files)
        if isinstance(rundict[argname], (np.ndarray, list)):
            # append values to storage
            pvalues.append(list(rundict[argname]))
            pkeys.append(argname)
    # convert pkey to array
    pkeys = np.array(pkeys)
    # we assume we want every combination of arguments (otherwise it is
    #   more complicated)
    if len(pkeys) != 0:
        combinations = list(itertools.product(*pvalues))
    else:
        combinations = [None]
    # storage for new runs
    new_runs = []
    # loop around combinations
    for combination in combinations:
        # get dictionary storage
        new_run = dict()
        # loop around argnames
        for argname in runorder:
            # deal with having combinations
            if combination is not None and argname in pkeys:
                # find position in combinations
                pos = np.where(pkeys == argname)[0][0]
                # get value from combinations
                value = combination[pos]
            else:
                value = rundict[argname]
            # ------------------------------------------------------------------
            # if we are dealing with the first argument we have this
            #   groups files (gtable0)
            if argname == arg0:
                new_run[argname] = list(gtable0['OUT'])
            # if we are dealing with 'directory' set it from nightname
            elif argname == 'directory':
                new_run[argname] = nightname
            # if we are not dealing with a list of files just set value
            elif not isinstance(value, OrderedDict):
                new_run[argname] = value
            # else we are dealing with another list and must find the
            #   best files (closeest in time) to add that match this
            #   group
            else:
                margs = [params, argname, rundict, nightname, meantime]
                new_run[argname] = _match_group(*margs)
        # append new run to new runs
        new_runs.append(new_run)
    # return new_runs
    return new_runs


def _find_first_filearg(params: ParamDict, runorder: List[str],
                        argdict: Dict[str, Dict[str, Table]],
                        kwargdict: Dict[str, Dict[str, Table]]
                        ) -> Union[Tuple[str, Dict[str, Table]], None]:
    """
    Find the first file-type argument in a set of arguments
    If none exist return None, else return the argument name of the first
    file-type argument, and the values it can have (from argdict/kwargdict)

    :param params: ParamDict, parameter dictionary of constants
    :param runorder: list of strings, the argument names in the correct run
                     order
    :param argdict: dictionary of positional arguments (key = argument name,
                    value =  dictionary of Tables, where each sub-key is a
                    drsFitsFile type (str) and the values are astropy tables
    :param kwargdict: dictionary of optional arguments (key = argument name,
                    value =  dictionary of Tables, where each sub-key is a
                    drsFitsFile type (str) and the values are astropy tables
    :return: tuple, 1. the argument name of the first file argumnet,
             2. the dictionary of drs file tables for this argument
    """
    # set function name
    _ = display_func(params, '_find_first_filearg', __NAME__)
    # loop around the run order
    for argname in runorder:
        # if argument is a positional argument return the argdict dictionary
        # of tables
        if argname in argdict:
            # it could be None here (if None supplied) so check argdict is
            #   a dictionary as expected
            if isinstance(argdict[argname], OrderedDict):
                return argname, argdict[argname]
        # else if the argument is an optional argument
        elif argname in kwargdict:
            # it could be None here (if None supplied) so check kwargdict is
            #   a dictionary as expected
            if isinstance(kwargdict[argname], OrderedDict):
                return argname, kwargdict[argname]
    # if we get to here we don't have a file argument (or it had no files)
    #   therefore return None --> deal with a None call on return
    return None


def _find_next_group(argname: str, drstable: Table,
                     usedgroups: Dict[str, List[str]],
                     groups: np.ndarray, ugroups: np.ndarray
                     ) -> Tuple[Union[Table, None], Dict[str, List[str]]]:
    """
    Find the next file group in a set of arguments

    :param argname: str, the name of the argument containing the first set of
                    files
    :param drstable: Table, the astropy.table.Table containing same DrsFitsFiles
                     entries (valid for this argument)
    :param usedgroups: dictionary of lists of strings - the previously used
                       group names, where each key is an argument name, and
                       each value is a list of group names that belong to
                       that argument
    :param groups: numpy array (1D), the full list of group names (as strings)
    :param ugroups: numpy array (1D), the unique + sorted list of group names
                    (as strings)
    :return: tuple, 1. the Table corresponding to the next group of files,
             2, dictionary of lists of strings - the previously used group
             names - where each key is an argument name, and each value is a
             list of group names that belong to that argument
    """
    # set function name
    _ = display_func(None, '_find_next_group', __NAME__)
    # make sure argname is in usedgroups
    if argname not in usedgroups:
        usedgroups[argname] = []
    # get the arg group for this arg name
    arggroup = list(usedgroups[argname])
    # find all ugroups not in arggroup
    mask = np.in1d(ugroups, arggroup)
    # deal with all groups already found
    if np.sum(~mask) == 0:
        return None, usedgroups
    # get the next group
    group = ugroups[~mask][0]
    # find rows in this group
    mask = groups == group
    # add group to used groups
    usedgroups[argname].append(group)
    # return masked table and usedgroups
    return Table(drstable[mask]), usedgroups


def _match_group(params: ParamDict, argname: str,
                 rundict: Dict[str, ArgDictType],
                 nightname: Union[str, None], meantime: float,
                 nightcol: Union[str, None] = None) -> List[str]:
    """
    Find the best group  of files from 'argname' (table of files taken from
    rundict) to a specific nightname + mean time (night name matched on
    column night_col or params['REPROCESS_NIGHTCOL'], mean time matched on
    MEANDATE column)

    :param params: ParamDict, parameter dictionary of constnats
    :param argname: str, the argument name we are matching (not the one for
                    meantime) the one to get table in rundict[argname][drsfile]
    :param rundict: a dictionary where the keys are the argument name and the
                    value are a dictionary of DrsFitFile names and the values
                    of these are astropy.table.Tables containing the
                    files associated with this [argument][drsfile]
    :param nightname: str or None, if set the night name to match to
                     (do not consider any files not from the night name) -
                     nightname controlled by table in rundict[argname][*] column
                     'nightcol' or params['REPROCESS_NIGHTCOL']
    :param meantime: float, the time to match (with time in column 'MEANDATE'
                     from table in rundict[argname][*])
    :param nightcol: str or None, if set the column name in rundict[argname][*]
                     table, if not set uses params['REPROCES_NIGHTCOL']
    :return: list of strings, the filenames that match the argument with
             nightname and meantime
    """
    # set function name
    func_name = display_func(params, '_match_groups', __NAME__)
    # get parmaeters from params/kwargs
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', func=func_name,
                       override=nightcol)
    # get drsfiles
    drsfiles1 = list(rundict[argname].keys())
    # storage of valid groups [group number, drsfile, meandate]
    valid_groups = []
    # loop around drs files in argname
    for drsfile in drsfiles1:
        # get table
        ftable1 = rundict[argname][drsfile]
        # mask by night name
        if nightname is not None:
            mask = ftable1[night_col] == nightname
        else:
            mask = np.ones(len(ftable1)).astype(bool)
        # check that we have some files with this nightname
        if np.sum(mask) == 0:
            continue
        # mask table
        table = Table(ftable1[mask])
        # get unique groups
        ugroups = np.unique(table['GROUPS']).astype(int)
        # loop around groups
        for group in ugroups:
            # mask group
            groupmask = table['GROUPS'] == group
            # get mean date
            groumeandate = table['MEANDATE'][groupmask][0]
            # store in valid_groups
            valid_groups.append([group, drsfile, groumeandate])
    # if we have no valid groups we cannot continue (time to stop)
    if len(valid_groups) == 0:
        raise DrsRecipeException('No valid groups')
    # for all valid_groups find the one closest intime to meantime of first
    #   argument
    valid_groups = np.array(valid_groups)
    # get mean times
    meantimes1 = np.array(valid_groups[:, 2]).astype(float)
    # ----------------------------------------------------------------------
    # find position of closest in time
    min_pos = int(np.argmin(abs(meantimes1 - meantime)))
    # ----------------------------------------------------------------------
    # get group for minpos
    group_s = int(valid_groups[min_pos][0])
    # get drsfile for minpos
    drsfile_s = valid_groups[min_pos][1]
    # get table for minpos
    table_s = rundict[argname][drsfile_s]
    # deal with table still being None
    if table_s is None:
        raise DrsRecipeException('No valid groups')
    # mask by group
    mask_s = np.array(table_s['GROUPS']).astype(int) == group_s
    # ----------------------------------------------------------------------
    # make sure mask has entries
    if np.sum(mask_s) == 0:
        raise DrsRecipeException('No valid groups')
    # ----------------------------------------------------------------------
    # return files for min position
    return list(table_s['OUT'][mask_s])


def vstack_cols(params: ParamDict, tablelist: List[Table]
                ) -> Union[Table, None]:
    """
    Take a list of Astropy Tables and stack into single Astropy Table
    Note same as io.drs_table.vstack_cols

    :param params: ParamDict, the parameter dictionary of constants
    :param tablelist: a list of astropy.table.Table to stack

    :return: the stacked astropy.table
    """
    # set function name
    _ = display_func(params, 'vstack_cols', __NAME__)
    # deal with empty list
    if len(tablelist) == 0:
        # append a None
        return None
    elif len(tablelist) == 1:
        # append the single row
        return tablelist[0]
    else:
        # get column names
        columns = tablelist[0].colnames
        # get value dictionary
        valuedict = dict()
        for col in columns:
            valuedict[col] = []
        # loop around elements in tablelist
        for it, table_it in enumerate(tablelist):
            # loop around columns and add to valudict
            for col in columns:
                # must catch instances of astropy.table.row.Row as
                #   they are not a list
                if isinstance(table_it, Table.Row):
                    valuedict[col] += [table_it[col]]
                # else we assume they are astropy.table.Table
                else:
                    valuedict[col] += list(table_it[col])
        # push into new table
        newtable = Table()
        for col in columns:
            newtable[col] = valuedict[col]
        # vstack all rows
        return newtable


# =============================================================================
# End of code
# =============================================================================
