#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 12:02

@author: cook
"""
import argparse
from collections import OrderedDict
import copy
import numpy as np
from pathlib import Path
import sys
from typing import Any, Dict, List, Type, Union

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_base_classes as base_class
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero.core.core import drs_exceptions
from apero.core.core import drs_log, drs_file
from apero.core.core import drs_argument
from apero.core.core import drs_database


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
# Get the text types
textentry = lang.textentry
# Get exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# get index database
IndexDatabase = drs_database.IndexDatabase
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
    # define typing for attributes
    filemod: base_class.ImportModule

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
        # get pconst
        self.pconst = constants.pload(self.instrument)
        # set drs file module related to this recipe
        if filemod is None:
            self.filemod = self.pconst.FILEMOD()
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
        # switch for RECAL_TEMPLATES
        #    (should be False unless added in sequences)
        self.template_required = False
        # shortname set to name initially
        self.shortname = str(self.name)
        # recipe kind (for logging)
        self.kind = None
        # save recipe module
        self.recipemod = None
        # import module as ImportClass (pickle-able)
        self.module = self._import_module()
        # input/output directory
        self.inputdir = None
        self.outputdir = None
        # input type ('raw', 'tmp', 'red') - used to get path when input/
        #    outputdir is None (default way to get these paths)
        self.inputtype = 'raw'
        self.outputtype = 'red'
        # run string (i.e. {recipe} arg1 arg2 --kwarg1 --kwarg2)
        self.runstring = None
        # recipe description/epilog
        self.description = 'No description defined'
        self.epilog = ''
        # define sets of arguments
        self.args = OrderedDict()
        self.kwargs = OrderedDict()
        self.specialargs = OrderedDict()
        # args for logging
        self.largs = ''
        self.lkwargs = ''
        self.lskwargs = ''
        # list of strings of extra arguments to add / overwrite set values
        self.extras = OrderedDict()
        # define arg list
        self.arg_list = []
        self.str_arg_list = None
        self.used_command = []
        self.drs_pconstant = None
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
        # exclude keys
        exclude = ['pconst', 'filemod']
        # set state to __dict__
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
        # set function name
        _ = display_func(self.params, '__setstate__', __NAME__,
                         self.class_name)
        # update dict with state
        self.__dict__.update(state)
        # get pconst
        self.pconst = constants.pload(self.instrument)
        # set drs file module related to this recipe
        self.filemod = self.pconst.FILEMOD()

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

    def recipe_setup(self, indexdb: IndexDatabase,
                     fkwargs: Union[dict, None] = None,
                     inargs: Union[list, None] = None
                     ) -> Union[Dict[str, Any], None]:
        """
        Interface between "recipe", inputs to function ("fkwargs") and argparse
        parser (inputs from command line)

        :param indexdb: IndexDatabase, index database instance
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
        parser = DrsArgumentParser(recipe=self, indexdb=indexdb,
                                   description=desc, epilog=epilog,
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
            WLOG(drs_params, 'error', textentry('00-006-00013', args=eargs))
        # ---------------------------------------------------------------------
        # get params
        try:
            params = vars(parser.parse_args(args=self.str_arg_list))
        except Exception as e:
            eargs = [sys.argv, self.str_arg_list, type(e), e, func_name]
            WLOG(drs_params, 'error', textentry('00-006-00014', args=eargs))
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
                emsg = textentry('00-006-00001', args=eargs)
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
                emsg = textentry('00-006-00002', args=eargs)
                kwarg.exception(emsg)
                value, param_key = None, None
            # else check that default_ref is in drs_params (i.e. defined in a
            #   constant file)
            elif kwarg.default_ref not in params:
                eargs = [kwarg.default_ref, kwarg.name, self.name]
                emsg = textentry('00-006-00003', args=eargs)
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
        except DrsCodedException as e:
            WLOG(None, 'error', e.get_text())
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
        except DrsCodedException as e:
            WLOG(None, 'error', e.get_text())
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

    def set_inputs(self):
        """
        Set the recipes input arguments (rargs), input keyword arguments
        (rkwargs) and special keyword arguments (rskwargs) - usually from
        recipe.args, recipe.kwargs, recipe.rskwargs

        :return:
        """
        # set function name
        _ = drs_misc.display_func(None, 'set_inputs', __NAME__,
                                  self.class_name)
        # deal with not having inputs
        if 'INPUTS' not in self.params:
            return
        # get inputs
        inputs = self.params['INPUTS']
        # get args/kwargs/skwargs
        rargs = self.args
        rkwargs = self.kwargs
        rskwargs = self.specialargs
        # start run string
        if self.name.endswith('.py'):
            self.runstring = '{0} '.format(self.name)
        else:
            self.runstring = '{0}.py '.format(self.name)
        # ------------------------------------------------------------------
        # deal with arguments
        self.largs = self._input_str(inputs, rargs, kind='arg')
        # ------------------------------------------------------------------
        # deal with kwargs
        self.lkwargs = self._input_str(inputs, rkwargs, kind='kwargs')
        # ------------------------------------------------------------------
        # deal with special kwargs
        self.lskwargs = self._input_str(inputs, rskwargs, kind='skwargs')
        # strip the runstring
        self.runstring.strip()

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
            emsg = textentry('00-008-00016', args=eargs)
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
            emsg = textentry('00-000-00001', args=[self.name])
            WLOG(self.params, 'error', emsg)
        # ------------------------------------------------------------------
        # run main via import module get method (gets import module)
        if hasattr(self.module.get(), 'main'):
            return self.module.get().main(**kwargs)
        else:
            eargs = [self.module.name, self.module.path, func_name]
            emsg = textentry('00-000-00004', args=eargs)
            WLOG(self.params, 'error', emsg)

    def get_input_dir(self) -> str:
        """
        Alias to drs_argument.get_input_dir

        Get the input directory for this recipe based on what was set in
        initialisation (construction)

        if RAW uses DRS_DATA_RAW from drs_params
        if TMP uses DRS_DATA_WORKING from drs_params
        if REDUCED uses DRS_DATA_REDUC from drs_params

        :return input_dir: string, the input directory
        """
        # set function name
        _ = display_func(self.params, 'get_input_dir', __NAME__,
                         self.class_name)
        # return input directory
        return drs_file.get_dir(self.params, self.inputtype, self.inputdir,
                                kind='input')

    def get_output_dir(self) -> str:
        """
        Alias to drs_argument.get_output_dir

        Get the input directory for this recipe based on what was set in
        initialisation (construction)

        if RAW uses DRS_DATA_RAW from drs_params
        if TMP uses DRS_DATA_WORKING from drs_params
        if REDUCED uses DRS_DATA_REDUC from drs_params

        :return input_dir: string, the input directory
        """
        # set function name
        _ = display_func(self.params, 'get_output_dir', __NAME__,
                         self.class_name)
        # return input directory
        return drs_file.get_dir(self.params, self.outputtype, self.outputdir,
                                kind='output')

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
        # switch for RECAL_TEMPLATES
        #    (should be False unless added in sequences)
        self.template_required = bool(recipe.template_required)
        # shortname
        self.shortname = str(recipe.shortname)
        # recipe kind (for logging)
        self.kind = copy.deepcopy(recipe.kind)
        # import module
        self.module = self.module
        # output directory
        self.outputdir = copy.deepcopy(recipe.outputdir)
        # input directory
        self.inputdir = copy.deepcopy(recipe.inputdir)
        # input type (raw/tmp/red)
        self.inputtype = str(recipe.inputtype)
        # output type (raw/tmp/red)
        self.outputtype = str(recipe.outputtype)
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
    def add_extra(self, arguments: Union[dict, None] = None,
                  tstars: Union[List[str], None] = None,
                  ostars: Union[List[str], None] = None,
                  template_stars: Union[List[str], None] = None):
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

            # need to filter list with template objects (if required)
            if self.template_required:
                # only if argname is in special list keys
                if arguments[argname] in SPECIAL_LIST_KEYS:
                    # need a new list of objects
                    objnames = list(value)
                    # reset value list
                    value = []
                    # loop around objnames
                    for objname in objnames:
                        # we want to reject those in template stars
                        if value not in template_stars:
                            value.append(objname)
            # check for argument in args
            if argname in self.args:
                self.extras[argname] = value
            # check for argument in kwargs
            elif argname in self.kwargs:
                self.extras[argname] = value
            # else raise an error
            else:
                eargs = [argname, value, func_name]
                WLOG(params, 'error', textentry('00-503-00012', args=eargs))

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
        # ---------------------------------------------------------------------
        # make debug functionality
        self._make_special(drs_argument.make_debug, skip=False)
        # ---------------------------------------------------------------------
        # make listing functionality
        self._make_special(drs_argument.make_listing, skip=True)
        # ---------------------------------------------------------------------
        # make listing all functionality
        self._make_special(drs_argument.make_alllisting, skip=True)
        # ---------------------------------------------------------------------
        # make version functionality
        self._make_special(drs_argument.make_version, skip=True)
        # ---------------------------------------------------------------------
        # make info functionality
        self._make_special(drs_argument.make_info, skip=True)
        # ---------------------------------------------------------------------
        # set program functionality
        self._make_special(drs_argument.set_program, skip=False)
        # ---------------------------------------------------------------------
        # set ipython return functionality
        self._make_special(drs_argument.set_ipython_return, skip=False)
        # ---------------------------------------------------------------------
        # set is_master functionality
        self._make_special(drs_argument.is_master, skip=False)
        # ---------------------------------------------------------------------
        # set breakpoint functionality
        self._make_special(drs_argument.breakpoints, skip=False)
        # ---------------------------------------------------------------------
        # set breakfunc functionality
        self._make_special(drs_argument.make_breakfunc, skip=False)
        # ---------------------------------------------------------------------
        # set quiet functionality
        self._make_special(drs_argument.set_quiet, skip=False)
        # ---------------------------------------------------------------------
        # force input and output directories
        self._make_special(drs_argument.set_inputdir, skip=False)
        self._make_special(drs_argument.set_outputdir, skip=False)

    def _make_special(self, function: Any, skip: bool = False):
        """
        Make a special argument using a special DrsArgument method (function)
        to supplies the properties of this special argument

        :param function: function, a DrsArgument method
                         (i.e. DrsArgument.make_XXX)
        :param skip: bool, force the skip to be True - if skip is True does not
                     run the recipe just runs the function and then exits

        :return: None - updates DrsRecipe.specialargs
        """
        # set function name
        _ = display_func(self.params, '_make_special', __NAME__,
                         self.class_name)
        # make debug functionality
        props = function(self.params)
        name = props['name']
        try:
            spec = DrsArgument(name, kind='special', altnames=props['altnames'])
        except DrsCodedException as e:
            WLOG(None, 'error', e.get_text())
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
            pos_args = ['[{0}]'.format(textentry('POS_ARG_TEXT'))]
        # define usage
        uargs = [self.name, ' '.join(pos_args), textentry('OPTIONS_TEXT')]
        usage = '{0}.py {1} [{2}]'.format(*uargs)
        return usage

    def _input_str(self, inputs: Union[ParamDict, dict],
                   argdict: Dict[str, Any], kind: str = 'arg') -> str:
        """
        From the user inputs add an entry for all args in argdict

        :param inputs: dictionary of arguments from the user (normally from
                       param['INPUTS']
        :param argdict: dictionary of arguments from the recipe defintion
                        arguments should be drs_argument.DrsArgument instances
        :param kind: str, either 'arg', 'kwarg', or 'skwarg' - changes how
                     the input string is made kwarg and skwarg have the
                     --{name}=value and arg is just {name}=value
        :return: str, the recreated input string as would be typed by the user
        """
        # set function name
        _ = drs_misc.display_func(None, '_input_str', __NAME__, self.class_name)
        # setup input str
        inputstr = ''
        # deal with kind
        if kind == 'arg':
            prefix = ''
        else:
            prefix = '--'
        # deal with arguments
        for argname in argdict:
            # get arg
            arg = argdict[argname]
            # strip prefix (may or may not have one)
            argname = argname.strip(prefix)
            # get input arg
            iarg = inputs[argname.strip(prefix)]
            # add prefix (add prefix whether it had one or not)
            argname = prefix + argname
            # deal with file arguments
            if arg.dtype in ['file', 'files']:
                if not isinstance(iarg, list):
                    continue
                # get string and drsfile
                strfiles = iarg[0]
                drsfiles = iarg[1]
                # deal with having string (force to list)
                if isinstance(strfiles, str):
                    strfiles = [strfiles]
                    drsfiles = [drsfiles]

                # add argname to run string
                if kind != 'arg':
                    self.runstring += '{0} '.format(argname)
                # loop around fiels and add them
                for f_it in range(len(strfiles)):
                    # add to list
                    fargs = [argname, f_it, strfiles[f_it], drsfiles[f_it].name]
                    inputstr += '{0}[1]={2} [{3}] || '.format(*fargs)
                    # add to run string
                    if strfiles[f_it] in ['None', None, '']:
                        continue
                    else:
                        basefile = Path(strfiles[f_it]).name
                        self.runstring += '{0} '.format(basefile)
            else:
                inputstr += '{0}={1} || '.format(argname, iarg)
                # skip Nones
                if iarg in ['None', None, '']:
                    continue
                # add to run string
                if isinstance(iarg, str):
                    iarg = Path(iarg).name
                if kind != 'arg':
                    self.runstring += '{0}={1} '.format(argname, iarg)
                else:
                    self.runstring += '{0} '.format(iarg)

        # return the input string
        return inputstr.strip().strip('||').strip()


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
            rkwargs: Union[Dict[str, List[DrsInputFile]], None] = None,
            template_required: bool = False):
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

        Note all filters apply to RAW files only - do not add filters for keys
        that are created in the drs (with the exception of KW_DPRTYPE)

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
        :param template_required: bool, if True means this recipe is turned
                        off if RECAL_TEMPLATES is True (run.ini files)

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
        add_set['template_required'] = template_required
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
                     ostars: Union[List[str], None] = None,
                     template_stars: Union[List[str], None] = None):
        """
        Process the DrsRunSequence.adds list (that have been added/defined
        previous) - this actually creates copies of the recipes and modifies
        them according to the settings in DrsRecipeSequence.adds

        :param params: ParamDict, the parameter dictionary of constants
        :param tstars: list of strings, the list of telluric stars (OBJECT
                       names)
        :param ostars: list of strings, the list of non-telluric stars (OBJECT
                       names)
        :param template_stars: list of strings, the list of stars that
                               currently have a template

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
            # set params
            frecipe.params = params
            # set filemod and recipemod
            frecipe.filemod = filemod
            frecipe.recipemod = recipemod
            # update short name
            if add['name'] is not None:
                frecipe.shortname = add['name']
            # set fiber
            if add['fiber'] is not None:
                frecipe.allowedfibers = add['fiber']
            # set template required
            if drs_text.true_text(add['template_required']):
                frecipe.template_required = True
            # add filters
            frecipe = self.add_filters(frecipe, infilters=add['filters'])
            # update file definitions
            frecipe = self.update_args(frecipe, arguments=add['arguments'],
                                       rargs=add['args'], rkwargs=add['kwargs'],
                                       template_stars=template_stars)
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
                    rkwargs: Union[Dict[str, List[DrsInputFile]], None] = None,
                    template_stars: Union[List[str], None] = None) -> DrsRecipe:
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
        :param template_stars: list of strings, the list of stars that
                               currently have a template

        :return: DrsRecipe, the updated drs recipe
        """
        # set function name
        _ = display_func(None, 'update_args', __NAME__, self.class_name)
        # deal with arguments overwrite
        if arguments is not None:
            frecipe.add_extra(arguments, tstars=self.tstars,
                              ostars=self.ostars,
                              template_stars=template_stars)
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
# End of code
# =============================================================================
