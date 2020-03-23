#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 12:02

@author: cook
"""
import numpy as np
from astropy.table import Table, vstack
import argparse
import os
import sys
import glob
from collections import OrderedDict
import copy
import itertools

from apero.core.instruments.default import pseudo_const
from apero.core import constants
from apero.locale import drs_text
from apero.core.core import drs_log
from apero.core.core import drs_argument


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_recipe.py'
__INSTRUMENT__ = 'None'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
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
# define name of index file
INDEX_FILE = Constants['DRS_INDEX_FILE']
INDEX_FILE_NAME_COL = Constants['DRS_INDEX_FILENAME']
# -----------------------------------------------------------------------------
# Get Classes from drs_argument
DrsArgumentParser = drs_argument.DrsArgumentParser
DrsArgument = drs_argument.DrsArgument
# alias pcheck
pcheck = drs_log.find_param
# define special keys
SPECIAL_LIST_KEYS = ['SCIENCE_TARGETS', 'TELLURIC_TARGETS']


# =============================================================================
# Define Recipe Classes
# =============================================================================
class DrsRecipe(object):
    def __init__(self, instrument=None, name=None, filemod=None):
        """
        Create a DRS Recipe object

        :param name: string, name of the recipe (the .py file) relating to
                     this recipe object
        """
        # get instrument
        self.instrument = instrument
        # name
        if name is None:
            self.name = 'UnknownRecipe'
        elif name.strip().endswith('.py'):
            while name.endswith('.py'):
                name = str(name[:-3])
            self.name = str(name)
        else:
            self.name = str(name)
        # set drs file module related to this recipe
        self.filemod = filemod
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
        # get drs parameters
        self.drs_params = ParamDict()
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

    def get_drs_params(self, **kwargs):
        func_name = __NAME__ + '.DrsRecipe.get_drs_params()'
        # Get config parameters from primary file
        self.drs_params = constants.load(self.instrument)
        self.drs_pconstant = constants.pload(self.instrument)
        self.textdict = TextDict(self.instrument, self.drs_params['LANGUAGE'])
        self.helptext = HelpText(self.instrument, self.drs_params['LANGUAGE'])
        # ---------------------------------------------------------------------
        # assign parameters from kwargs
        for kwarg in kwargs:
            self.drs_params[kwarg] = kwargs[kwarg]
            self.drs_params.set_source(kwarg, func_name + ' --kwargs')
        # ---------------------------------------------------------------------
        # set recipe name
        while self.name.endswith('.py'):
            self.name = self.name[:-3]
        self.drs_params['RECIPE'] = str(self.name)
        self.drs_params.set_source('RECIPE', func_name)
        # ---------------------------------------------------------------------
        # set up array to store inputs/outputs
        self.drs_params['INPUTS'] = ParamDict()
        self.drs_params.set_sources(['INPUTS'], func_name)

    def recipe_setup(self, fkwargs=None, inargs=None):
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
        func_name = __NAME__ + '.DrsRecipe.recipe_setup()'
        # set up storage for arguments
        fmt_class = argparse.RawDescriptionHelpFormatter
        desc, epilog = self.description, self.epilog
        parser = DrsArgumentParser(recipe=self, description=desc, epilog=epilog,
                                   formatter_class=fmt_class,
                                   usage=self._drs_usage())
        # get the drs params from recipe
        drs_params = self.drs_params
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
                self.drs_params['IS_MASTER'] = True
        # ---------------------------------------------------------------------
        # add to DRS parameters
        self.drs_params['INPUTS'] = input_parameters
        self.drs_params.set_source('INPUTS', func_name)
        # push values of keys matched in input_parameters into drs_parameters
        for key in input_parameters.keys():
            if key in self.drs_params:
                self.drs_params[key] = input_parameters[key]
                self.drs_params.set_source(key, input_parameters.sources[key])

    def set_arg(self, name=None, **kwargs):
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
        try:
            argument = DrsArgument(name, kind='arg', **kwargs)
        except ArgumentError as e:
            sys.exit(0)
        # make arg parser properties
        argument.make_properties()
        # recast name
        name = argument.name
        # add to arg list
        self.args[name] = argument

    def set_kwarg(self, name=None, **kwargs):
        """
        Add a keyword argument to the recipe

        :param name: string or None, the name and reference of the argument
        :param kwargs: arguments that can be assigned to DrsArgument kwargs
        :return None:
        """
        if name is None:
            name = 'Kwarg{0}'.format(len(self.args) + 1)
        # create keyword argument
        try:
            keywordargument = DrsArgument(name, kind='kwarg', **kwargs)
        except ArgumentError as e:
            sys.exit(0)
        # make arg parser properties
        keywordargument.make_properties()
        # recast name
        name = keywordargument.name
        # set to keyword argument
        self.kwargs[name] = keywordargument

    def set_outputs(self, **kwargs):
        for kwarg in kwargs:
            self.outputs[kwarg] = kwargs[kwarg]

    def set_debug_plots(self, *args):
        for arg in args:
            self.debug_plots.append(arg)

    def set_summary_plots(self, *args):
        for arg in args:
            self.summary_plots.append(arg)

    def add_output_file(self, outfile):
        func_name = __NAME__ + '.DrsRecipe.add_output_file()'
        # get the name of the outfile
        key = outfile.basename
        # check if outfile has output_dict
        if hasattr(outfile, 'output_dict'):
            self.output_files[key] = outfile.output_dict
        else:
            # log that output file has no attribute 'output_dict'
            eargs = [outfile.name, func_name]
            emsg = TextEntry('00-008-00016', args=eargs)
            WLOG(self.drs_params, 'error', emsg)

    def main(self, **kwargs):
        """
        Run the main function associated with this recipe

        :param kwargs: kwargs passed to the main functions

        :return:
        """
        # ------------------------------------------------------------------
        # next check in parameters for path to module
        if (self.module is None) and (self.drs_params is not None):
            params = self.drs_params
            # check for parameters
            cond1 = 'INSTRUMENT' in params
            cond2 = 'DRS_INSTRUMENT_RECIPE_PATH' in params
            cond3 = 'DRS_DEFAULT_RECIPE_PATH' in params
            if cond1 and cond2 and cond3:
                instrument = params['INSTRUMENT']
                rpath = params['DRS_INSTRUMENT_RECIPE_PATH']
                dpath = params['DRS_DEFAULT_RECIPE_PATH']
                margs = [instrument, [self.name], rpath, dpath]
                modules = constants.getmodnames(*margs, path=False)
                # return module
                self.module = self._import_module(modules[0], full=True,
                                                  quiet=True)
        # ------------------------------------------------------------------
        # else make an error
        if self.module is None:
            emsg = TextEntry('00-000-00001', args=[self.name])
            WLOG(self.drs_params, 'error', emsg)
        # ------------------------------------------------------------------
        # run main
        return self.module.main(**kwargs)

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
        # return input_dir
        return self.get_dir(input_dir_pick, kind='input')

    def get_output_dir(self):
        """
        Get the input directory for this recipe based on what was set in
        initialisation (construction)

        if RAW uses DRS_DATA_RAW from drs_params
        if TMP uses DRS_DATA_WORKING from drs_params
        if REDUCED uses DRS_DATA_REDUC from drs_params

        :return input_dir: string, the input directory
        """
        # check if "input_dir" is in namespace
        output_dir_pick = self.outputdir.upper()
        # return input_dir
        return self.get_dir(output_dir_pick, kind='output')

    def copy(self, recipe):
        # get instrument
        self.instrument = str(recipe.instrument)
        # name
        self.name = str(recipe.name)
        # set drs file module related to this recipe
        self.filemod = recipe.filemod
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
        self.drs_params = recipe.drs_params.copy()
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
    def generate_runs(self, params, table, filters=None, allowedfibers=None):
        # set function name
        func_name = display_func(params, 'generate_runs', __NAME__, 'DrsRecipe')
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
        runlist = convert_to_command(self, params, runargs)
        # clear printer
        drs_log.Printer(None, None, '')
        # return the runlist
        return runlist

    def add_extra(self, params, arguments, tstars=None):
        # set function name
        func_name = display_func(params, 'add_extra', __NAME__, 'DrsRecipe')
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
                    # may not be strings (if set from params)
                    if isinstance(value, str):
                        # these must be lists
                        value = value.split(',')
                        # make sure there are no white spaces
                        value = np.char.strip(value)
                # deal with telluric targets being None
                if arguments[argname] == 'TELLURIC_TARGETS':
                    if isinstance(value, (type(None), str)):
                        if value in ['None', None, '']:
                            value = tstars

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
    # Private Methods (Not to be used externally to spirouRecipe.py)
    # =========================================================================
    def _import_module(self, name=None, full=False, quiet=False):
        func_name = __NAME__ + '.DrsRecipe._import_module()'
        # deal with no name
        if name is None:
            name = self.name
        if (name is None) or (name.upper() == 'UNKNOWNRECIPE'):
            return None
        # get local copy of module
        try:
            return constants.import_module(func_name, name, full=full,
                                           quiet=quiet)
        except Exception:
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

        --listing, --list     List the files in the given input directory

        :return None:
        """
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


    def _make_special(self, function, skip=False):
        # make debug functionality
        props = function(self.drs_params)
        name = props['name']
        try:
            spec = DrsArgument(name, kind='special', altnames=props['altnames'])
        except ArgumentError:
            sys.exit(0)
        spec.assign_properties(props)
        spec.skip = skip
        spec.helpstr = props['help']
        self.specialargs[name] = spec

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
            pos_args = ['[{0}]'.format(self.helptext['POS_ARG_TEXT'])]
        # define usage
        uargs = [self.name, ' '.join(pos_args), self.helptext['OPTIONS_TEXT']]
        usage = '{0}.py {1} [{2}]'.format(*uargs)
        return usage

    def valid_directory(self, argname, directory, return_error=False):
        # get drs parameters
        params = self.drs_params
        # ---------------------------------------------------------------------
        # Make sure directory is a string
        if type(directory) not in [str, np.str_]:
            eargs = [argname, directory, type(directory)]
            emsg = TextEntry('09-001-00003', args=eargs)
            if return_error:
                return False, emsg
            else:
                return False
        # ---------------------------------------------------------------------
        # step 1: check if directory is full absolute path
        if os.path.exists(directory):
            dmsg = TextEntry('90-001-00001', args=[argname, directory])
            dmsg += TextEntry('')
            WLOG(params, 'debug', dmsg, wrap=False)
            if return_error:
                return True, directory, None
            else:
                return False, directory
        # ---------------------------------------------------------------------
        # step 2: check if directory is in input directory
        input_dir = self.get_input_dir()
        test_path = os.path.join(input_dir, directory)
        if os.path.exists(test_path):
            dmsg = TextEntry('90-001-00017', args=[argname, directory])
            dmsg += TextEntry('')
            WLOG(params, 'debug', dmsg, wrap=False)
            if return_error:
                return True, test_path, None
            else:
                return True, test_path
        # ---------------------------------------------------------------------
        # else deal with errors
        eargs = [argname, directory, test_path]
        emsg = TextEntry('09-001-00004', args=eargs)

        return False, None, emsg

    def _valid_files(self, argname, files, directory=None, return_error=False,
                     alltypelist=None, allfilelist=None):
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
        # set function name
        func_name = display_func(params, '_valid_file', __NAME__, 'DrsRecipe')
        # deal with no current typelist (alltypelist=None)
        if alltypelist is None:
            alltypelist = []
        if allfilelist is None:
            allfilelist = []
        # get the argument that we are checking the file of
        arg = _get_arg(self, argname)
        drs_files = arg.files
        # make sure drs_files is a list
        if not isinstance(drs_files, list):
            drs_files = [drs_files]
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
        out = _check_file_location(self, argname, directory, filename)
        valid, files, error = out
        if not valid:
            if return_error:
                return False, None, None, error
            else:
                return False, None, None
        # perform file/directory check
        out = _check_if_directory(argname, files)
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
            if len(drs_files) == 0:
                # files must be set
                eargs = [argname, func_name]
                WLOG(params, 'error', TextEntry('00-006-00019', args=eargs))
            # loop around file types
            for drs_file in drs_files:
                # if in debug mode print progres
                dargs = [drs_file.name, os.path.basename(filename_it)]
                WLOG(params, 'debug', TextEntry('90-001-00008', args=dargs),
                     wrap=False)
                # -------------------------------------------------------------
                # make instance of the DrsFile
                inputdir = self.get_input_dir()
                # create an instance of this drs_file with the filename set
                file_in = drs_file.newcopy(filename=filename_it, recipe=self)
                file_in.read_file()
                # set the directory
                fdir = drs_argument.get_uncommon_path(directory, inputdir)
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
                    exargs = [self, argname, drs_file, drs_logic,
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
                        header_errors[drs_file.name] = error2b
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
                errors += _gen_header_errors(params, header_errors)
                # add file error (needed only once per filename)
                eargs = [os.path.abspath(filename_it)]
                errors += '\n' + self.textdict['09-001-00024'].format(*eargs)
                break

        # must append all files checked
        allfiles = allfilelist + checked_files

        if len(allfiles) > 1:
            errors += self.textdict['40-001-00019']
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
        elif return_error:
            return True, out_files, out_types, TextEntry(None)
        # c. if we did and don't expect an error return True without an error
        else:
            return True, out_files, out_types

    def get_dir(self, dir_string, kind='input'):
        # get parameters from recipe call
        params = self.drs_params
        # get the input directory from recipe.inputdir keyword
        if dir_string == 'RAW':
            dirpath = self.drs_params['DRS_DATA_RAW']
        elif dir_string == 'TMP':
            dirpath = self.drs_params['DRS_DATA_WORKING']
        elif dir_string == 'REDUCED':
            dirpath = self.drs_params['DRS_DATA_REDUC']
        # if not found produce error
        else:
            emsg = TextEntry('00-007-00002', args=[kind, dir_string])
            WLOG(params, 'error', emsg)
            dirpath = None
        return dirpath

    def __error__(self):
        """
        The option log for WLOG for all errors in class

        :return log_opt: string, the log_opt message for WLOG
        """
        func_name = __NAME__ + 'DrsRecipe.__error__()'

        if 'PID' not in self.drs_params:
            self.drs_params['PID'] = None
            self.drs_params.set_source('PID', func_name)
        if 'RECIPE' not in self.drs_params:
            self.drs_params['RECIPE'] = str(__NAME__.replace('.py', ''))
            self.drs_params.set_source('RECIPE', func_name)
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


class DrsRunSequence(object):
    def __init__(self, name, instrument=None):
        self.name = name
        self.instrument = instrument
        self.sequence = []
        self.adds = []
        self.arguments = dict()

    def __str__(self):
        return 'DrsRunSequence[{0}]'.format(self.name)

    def __repr__(self):
        return 'DrsRunSequence[{0}]'.format(self.name)

    def add(self, recipe, **kwargs):
        self.adds.append([recipe, dict(kwargs)])

    def process_adds(self, params, tstars=None):
        # set function name
        func_name = display_func(params, 'process_adds', __NAME__,
                                 class_name='DrsRunSequence')
        # set telluric stars (may be needed)
        self.tstars = tstars
        # get filemod and recipe mod
        pconst = constants.pload(self.instrument)
        filemod = pconst.FILEMOD()
        recipemod = pconst.RECIPEMOD()
        # storage of sequences
        self.sequence = []
        # loop around the added recipes to sequence
        for add in self.adds:
            recipe, kwargs = add
            # set up new recipe
            frecipe = DrsRecipe(self.instrument)
            # copy from given recipe
            frecipe.copy(recipe)
            # set filemod and recipemod
            frecipe.filemod = filemod
            frecipe.recipemod = recipemod
            # update short name
            frecipe.shortname = kwargs.get('name', frecipe.shortname)
            # set fiber
            frecipe.allowedfibers = kwargs.get('fiber', frecipe.allowedfibers)
            # add filters
            frecipe = self.add_filters(frecipe, kwargs)
            # update file definitions
            frecipe = self.update_args(params, frecipe, kwargs)
            # update master
            frecipe.master = kwargs.get('master', frecipe.master)
            # add to sequence storage
            self.sequence.append(frecipe)

    def add_filters(self, frecipe, kwargs):
        # add filters
        filters = dict()
        for kwarg in kwargs:
            if 'KW_' in kwarg:
                filters[kwarg] = kwargs[kwarg]
        # add to new recipe
        frecipe.filters = filters
        # return frecipe
        return frecipe

    def update_args(self, params, frecipe, fargs):
        # deal with arguments overwrite
        if 'arguments' in fargs:
            frecipe.add_extra(params, fargs['arguments'], tstars=self.tstars)
        # ------------------------------------------------------------------
        # update args - loop around positional arguments
        frecipe.args = self._update_arg(frecipe.args, fargs)
        # ------------------------------------------------------------------
        # update kwargs - loop around positional arguments
        frecipe.kwargs = self._update_arg(frecipe.kwargs, fargs)
        # ------------------------------------------------------------------
        # return recipes
        return frecipe

    def _update_arg(self, arguments, fargs):
        # loop around each argument
        for argname in arguments:
            # if positional argument in function args (fargs) then we can
            #   update the value
            if argname in fargs:
                # get the value of each key
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
                            # copy file
                            drsfilecopy = drsfile.completecopy(drsfile)
                            # append to new list
                            arguments[argname].files.append(drsfilecopy)
        # return the arguments
        return arguments


class DrsRecipeException(Exception):
    pass


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
        # noinspection PyProtectedMember
        input_dir = recipe.get_input_dir()
    # -------------------------------------------------------------------------
    # Step 1: check "filename" as full link to file (including wildcards)
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(filename)
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
        return True, output_files, []
    # -------------------------------------------------------------------------
    # Step 2: recipe.inputdir.upper() (including wildcards)
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(os.path.join(input_dir, filename))
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
        return True, output_files, []
    # -------------------------------------------------------------------------
    # Step 3: check "filename" as full link to file (including wildcards)
    #         + .fits
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(filename + '.fits')
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
        return True, output_files, []
    # -------------------------------------------------------------------------
    # Step 4: recipe.inputdir.upper() (including wildcards)
    #         + .fits
    # -------------------------------------------------------------------------
    # get glob list of files using glob
    raw_files = glob.glob(os.path.join(input_dir, filename + '.fits'))
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


def _check_if_directory(argname, files):
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
        return True, files, []


def _check_file_exclusivity(recipe, argname, drs_file, logic, outtypes,
                            alltypelist=None):
    # get drs parameters
    params = recipe.drs_params
    # deal with no alltypelist
    if alltypelist is None:
        alltypelist = list(outtypes)
    else:
        alltypelist = list(alltypelist) + list(outtypes)

    # if we have no files yet we don't need to check exclusivity
    if len(alltypelist) == 0:
        dargs = [argname, drs_file.name]
        WLOG(params, 'debug', TextEntry('90-001-00013', args=dargs),
             wrap=False)
        return True, None
    # if argument logic is set to "exclusive" we need to check that the
    #   drs_file.name is the same for this as the last file in outtypes
    if logic == 'exclusive':
        # match by name of drs_file
        cond = drs_file.name == alltypelist[-1].name
        # if condition not met return False and error
        if not cond:
            eargs = [argname, drs_file.name, alltypelist[-1].name]
            emsg = TextEntry('09-001-00008', args=eargs)
            return False, emsg
        # if condition is met return True and empty error
        else:
            dargs = [argname, drs_file.name]
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
        eargs = [argname, recipe.name]
        WLOG(params, 'error', TextEntry('00-006-00004', args=eargs),
             wrap=False)


# =============================================================================
# Define run making functions
# =============================================================================
def find_run_files(params, recipe, table, args, filters=None,
                   allowedfibers=None, **kwargs):
    # set function name
    func_name = display_func(params, 'find_run_files', __NAME__)
    # storage for valid files for each argument
    filedict = OrderedDict()
    # get constants from params
    absfile_col = pcheck(params, 'REPROCESS_ABSFILECOL', 'absfile_col',
                         kwargs, func_name)
    check_required = kwargs.get('check_required', False)
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
                    # check mask
                    testmask |= values == testvalue
                # add filter to filter mask with AND (must have all filters)
                filtermask &= testmask
        # ------------------------------------------------------------------
        # loop around drs files
        for drsfile in drsfiles:
            # copy table
            ftable = Table(table[filtermask])
            ffiles = np.array(files)[filtermask]
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
                out = drsfile.get_infile_outfilename(params, recipe, filename,
                                                     allowedfibers)
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
                # get table dictionary
                tabledict = dict(zip(ftable.colnames, ftable[it]))
                # check whether tabledict means that file is valid for this
                #   infile
                valid1 = infile.check_table_keys(params, tabledict)
                # do not continue if valid1 not True
                if not valid1:
                    continue
                # check whether filters are found
                valid2 = infile.check_table_keys(params, tabledict,
                                                 rkeys=filters)
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


def group_run_files(params, recipe, argdict, kwargdict, **kwargs):
    # set function name
    func_name = display_func(params, 'group_run_files', __NAME__)
    # get parameters from params
    file_col = pcheck(params, 'DRS_INDEX_FILENAME', 'filecol', kwargs,
                     func_name)
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
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
    runorder, rundict = _get_runorder(recipe, argdict, kwargdict)
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
                                        meantime, arg0, gtable0, file_col,
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


def convert_to_command(self, params, runargs):
    # set function name
    func_name = display_func(params, 'convert_to_command', __NAME__)
    # get args/kwargs from recipe
    args = self.args
    kwargs = self.kwargs
    # define storage
    outputs = []
    # loop around arguement
    for runarg in runargs:
        # command first arg
        command = '{0} '.format(self.name)
        # get run order
        runorder, _ = _get_runorder(self, runarg, runarg)
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
def _check_arg_path(params, arg, directory):
    # set function name
    func_name = display_func(params, '_check_arg_path', __NAME__)
    # set the path as directory if arg.path is None
    if arg.path is None:
        return directory
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
        path = constants.get_relative_folder(package, path)
    # now check that path is valid
    if not os.path.exists(path):
        # log that arg path was wrong
        eargs = [arg.name, arg.path, func_name]
        WLOG(params, 'error', TextEntry('00-006-00018', args=eargs))
    else:
        return path


def _gen_header_errors(params, header_errors):
    # set up message storage
    emsgs = TextEntry(None)
    # get text
    text = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
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
        emsgs += '\n' + text['09-001-00021'].format(drsfile)
        # loop around keys in this drs_file
        for key in header_error:
            # get this iterations entry
            entry = header_error[key]
            # get the argname
            argname = entry[1]
            # construct error message
            eargs = [key, entry[3], entry[2]]
            if not entry[0]:
                emsgs += '\n' + text['09-001-00022'].format(*eargs)
    if len(emsgs) > 0:
        emsg0 = TextEntry('09-001-00023', args=[argname])
    else:
        emsg0 = TextEntry(None)

    return emsg0 + emsgs


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


def _group_drs_files(params, drstable, **kwargs):
    # set function name
    func_name = display_func(params, '_group_drs_files', __NAME__)
    # get properties from params
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
    seq_colname = pcheck(params, 'REPROCESS_SEQCOL', 'seq_col', kwargs,
                         func_name)
    time_colname = pcheck(params, 'REPROCESS_TIMECOL', 'time_col', kwargs,
                          func_name)
    limit = kwargs.get('limit', None)
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


def _get_runorder(recipe, argdict, kwargdict):
    # set function name
    func_name = display_func(recipe.drs_params, '_get_runorder', __NAME__)
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
    return runorder, rundict


def _gen_run(params, rundict, runorder, nightname=None, meantime=None,
             arg0=None, gtable0=None, file_col=None, masternight=False):

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
    # deal with no list values
    if len(pkeys) == 0:
        combinations = [None]
    # else we assume we want every combination of arguments (otherwise it is
    #   more complicated)
    else:
        combinations = list(itertools.product(*pvalues))
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


def _find_first_filearg(params, runorder, argdict, kwargdict):
    # set function name
    func_name = display_func(params, '_find_first_filearg', __NAME__)
    # loop around the run order
    for argname in runorder:
        if argname in argdict:
            if isinstance(argdict[argname], OrderedDict):
                return argname, argdict[argname]
        elif argname in kwargdict:
            if isinstance(kwargdict[argname], OrderedDict):
                return argname, kwargdict[argname]
    return None


# def _find_next_group(argname, drstable, usedgroups, groups, ugroups):
#     # make sure argname is in usedgroups
#     if argname not in usedgroups:
#         usedgroups[argname] = []
#
#     arggroup = list(usedgroups[argname])
#     # loop around unique groups
#     for group in ugroups:
#         # if used skip
#         if group in arggroup:
#             continue
#         else:
#             # find rows in this group
#             mask = groups == group
#             # add group to used groups
#             usedgroups[argname].append(group)
#             # return masked table and usedgroups
#             return Table(drstable[mask]), usedgroups
#     # return None if all groups used
#     return None, usedgroups


def _find_next_group(argname, drstable, usedgroups, groups, ugroups):
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


def _match_group(params, argname, rundict, nightname, meantime, **kwargs):

    func_name = __NAME__ + '._match_groups()'

    # get parmaeters from params/kwargs
    file_col = pcheck(params, 'DRS_INDEX_FILENAME', 'filecol', kwargs,
                     func_name)
    night_col = pcheck(params, 'REPROCESS_NIGHTCOL', 'night_col', kwargs,
                       func_name)
    # get drsfiles
    drsfiles1 = list(rundict[argname].keys())
    # storage of valid groups [group number, drsfile, meandate]
    valid_groups = []
    # loop around drs files in argname
    for drsfile in drsfiles1:
        # get table
        ftable1 = rundict[argname][drsfile]
        # mask by night name
        mask = ftable1[night_col] == nightname
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
    # mask by group
    mask_s = np.array(table_s['GROUPS']).astype(int) == group_s
    # ----------------------------------------------------------------------
    # make sure mask has entries
    if np.sum(mask_s) == 0:
        raise DrsRecipeException('No valid groups')
    # ----------------------------------------------------------------------
    # return files for min position
    return list(table_s['OUT'][mask_s])


def vstack_cols(params, tablelist):
    """
    Take a list of Astropy Tables and stack into single Astropy Table
    Note same as io.drs_table.vstack_cols

    :param params:
    :param tablelist:
    :return:
    """
    # deal with empty list
    if len(tablelist) == 0:
        # append a None
        return None
    elif len(tablelist) == 1:
        # append the single row
        return  tablelist[0]
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
