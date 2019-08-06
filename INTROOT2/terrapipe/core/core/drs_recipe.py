#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 12:02

@author: cook
"""
import numpy as np
from astropy.table import Table
import argparse
import os
import sys
import glob
from collections import OrderedDict

from terrapipe.core.instruments.default import pseudo_const
from terrapipe.core import constants
from terrapipe.locale import drs_text
from . import drs_log
from . import drs_argument

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'drs_recipe.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
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
DRSArgumentParser = drs_argument.DRSArgumentParser
DrsArgument = drs_argument.DrsArgument


# =============================================================================
# Define Recipe Classes
# =============================================================================
class DrsRecipe(object):
    def __init__(self, instrument=None, name=None):
        """
        Create a DRS Recipe object

        :param name: string, name of the recipe (the .py file) relating to
                     this recipe object
        """
        # get instrument
        self.instrument = instrument
        # name
        if name is None:
            self.name = 'Unknown'
        elif name.strip().endswith('.py'):
            while name.endswith('.py'):
                name = name[:-3]
            self.name = name
        else:
            self.name = name
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
        # define arg list
        self.arg_list = []
        self.str_arg_list = None
        # get drs parameters
        self.drs_params = ParamDict()
        self.drs_pconstant = None
        self.textdict = None
        self.helptext = None
        self.input_params = ParamDict()
        self.required_args = []
        self.optional_args = []
        self.special_args = []
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
        self.drs_params['RECIPE'] = self.name
        self.drs_params.set_source('RECIPE', func_name)
        # ---------------------------------------------------------------------
        # if DRS_INTERACTIVE is not True and DRS_PLOT is to the screen
        #     then DRS_PLOT should be turned off too
        if not self.drs_params['DRS_INTERACTIVE']:
            if self.drs_params['DRS_PLOT'] == 1:
                self.drs_params['DRS_PLOT'] = 0
        # ---------------------------------------------------------------------
        # set up array to store inputs/outputs
        self.drs_params['INPUTS'] = ParamDict()
        self.drs_params['OUTPUTS'] = ParamDict()
        self.drs_params.set_sources(['INPUTS', 'OUTPUTS'], func_name)

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
        parser = DRSArgumentParser(recipe=self, description=desc, epilog=epilog,
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
        # add to DRS parameters
        self.drs_params['INPUTS'] = input_parameters
        self.drs_params.set_source('INPUTS', func_name)
        # push values of keys matched in input_parameters into drs_parameters
        for key in input_parameters.keys():
            if key in self.drs_params:
                self.drs_params[key] = input_parameters[key]
                self.drs_params.set_source(key, input_parameters.sources[key])
        # ---------------------------------------------------------------------
        # if DRS_INTERACTIVE is not True then DRS_PLOT should be turned off too
        if not self.drs_params['DRS_INTERACTIVE']:
            self.drs_params['DRS_PLOT'] = 0
            psource = '{0} [{1}]'.format(func_name, 'DRS_INTERACTIVE=False')
            self.drs_params.set_source('DRS_PLOT', psource)

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
        input_dir = self.get_input_dir()
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

        # else we have to match directories to directories - crash for now
        else:
            emsg = TextEntry('00-006-00005', args=[func_name])
            WLOG(self.drs_params, 'error', emsg)

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
        # ------------------------------------------------------------------
        # need to check if module is defined
        if self.module is None:
            self.module = self._import_module(quiet=True)
        # ------------------------------------------------------------------
        # next check in parameters for path to module
        if (self.module is None) and (self.drs_params is not None):
            params = self.drs_params
            # check for parameters
            cond1 = 'INSTRUMENT' in params
            cond2 = 'INSTRUMENT_RECIPE_PATH' in params
            cond3 = 'DEFAULT_RECIPE_PATH' in params
            if cond1 and cond2 and cond3:
                instrument = params['INSTRUMENT']
                rpath = params['INSTRUMENT_RECIPE_PATH']
                dpath = params['DEFAULT_RECIPE_PATH']
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

    # =========================================================================
    # Private Methods (Not to be used externally to spirouRecipe.py)
    # =========================================================================
    def _import_module(self, name=None, full=False, quiet=False):
        # deal with no name
        if name is None:
            name = self.name
        # get local copy of module
        try:
            return constants.import_module(name, full=full, quiet=quiet)
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
            # loop around file types
            for drs_file in drs_files:
                # if in debug mode print progres
                dargs = [drs_file.name, os.path.basename(filename_it)]
                WLOG(params, 'debug', TextEntry('90-001-00008', args=dargs),
                     wrap=False)

                # -------------------------------------------------------------
                # make instance of the DrsFile
                # noinspection PyProtectedMember
                inputdir = self.get_input_dir()
                # create an instance of this drs_file with the filename set
                file_in = drs_file.newcopy(filename=filename_it, recipe=self)
                file_in.read()
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
            emsg = TextEntry('00-006-00006', args=[argkind, func_name])
            WLOG(self.drs_params, 'error', emsg)
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
            eargs = [arg_string, argname, func_name]
            emsg = TextEntry('00-006-00007', args=eargs)
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
            WLOG(params, 'debug', TextEntry('90-001-00022', args=[ifile]),
                 wrap=False)
            return []
        else:
            wargs = [np.sum(mask), ifile]
            WLOG(params, 'debug', TextEntry('90-001-00023', args=wargs),
                 wrap=False)

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
                tmp_file = drs_file.newcopy()
                # get path of file
                tmp_path = os.path.join(path, directory, valid_file)
                # set filename
                tmp_file.set_filename(tmp_path, check=False)
                tmp_file.directory = directory
                tmp_file.inputdir = input_dir
                # make a header from index data table
                tmp_file.indextable = _make_dict_from_table(indexdata[mask][v_it])
                # append to list
                valid_entries.append(tmp_file)
            valid_files += valid_entries

            wargs = [len(valid_files), drs_file.name]
            WLOG(params, 'debug', TextEntry('90-001-00024', args=wargs),
                 wrap=False)

        # return valid files
        return valid_files

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
            self.drs_params['RECIPE'] = __NAME__.replace('.py', '')
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

#
# def _check_file_extension(recipe, argname, file_instance):
#     """
#     If '.fits' file checks the file extension is valid.
#
#     :param argname: string, the argument name (for error reporting)
#     :param filename: list of strings, the files to check
#     :param ext: string or None, the extension to check, if None skips
#
#     :return cond: bool, True if extension valid
#     :return errors: list of strings, the errors that occurred if cond=False
#     """
#     # extension
#     ext = file_instance.ext
#     # filename
#     filename = file_instance
#     # get drs parameters
#     params = recipe.drs_params
#     # check
#     valid, msg = file_instance.has_correct_extension(filename=filename)
#     # if valid return True and no error
#     if valid:
#         dargs = [argname, os.path.basename(filename)]
#         WLOG(params, 'debug', TextEntry('90-001-00009', args=dargs),
#              wrap=False)
#         return True, None
#     # if False generate error and return it
#     else:
#         emsg = TextEntry('09-001-00006', args=[argname, ext])
#         return False, emsg
#
#
# def _check_file_header(recipe, argname, drs_file, filename, directory):
#     # get the input directory
#     # noinspection PyProtectedMember
#     inputdir = recipe._get_input_dir()
#     # create an instance of this drs_file with the filename set
#     file_instance = drs_file.newcopy(filename=filename, recipe=recipe)
#     file_instance.read()
#     # set the directory
#     fdir = drs_argument.get_uncommon_path(directory, inputdir)
#     file_instance.directory = fdir
#     # -----------------------------------------------------------------
#     # use file_instances check file header method
#     return file_instance.check_file_header(argname=argname)
#

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
            WLOG(params, 'debug', TextEntry('90-001-00025', args=[abspath]),
                 wrap=False)
            index_list.append(abspath)
        else:
            WLOG(params, 'debug', TextEntry('90-001-00026', args=[abspath]),
                 wrap=False)
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
        wargs = [directory, 'off_listing']
        WLOG(p, 'warning', TextEntry('10-004-00002', args=wargs))
        return None

    # load index file
    try:
        indexdata = Table.read(index_file)
    except Exception as e:
        eargs = [[directory], type(e), e]
        WLOG(p, 'error', TextEntry('00-009-00001', args=eargs))
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
            dargs = [key, ' or '.join(values)]
            WLOG(p, 'debug', TextEntry('90-001-00027', args=dargs))
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
        filenames.append(value.indextable['FILENAME'])
        exp_nums.append(value.indextable[params['KW_CMPLTEXP'][0]])
        nexps.append(value.indextable[params['KW_NEXP'][0]])
        dates.append(value.indextable[params['KW_ACQTIME'][0]])
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
                    WLOG(params, 'debug', TextEntry('90-001-00028'))
                    files = np.array([files[-1]])
                    gdate = np.array([gdate[-1]])
                # add to groups (only if we have more than one file)
                if len(files) > 0:
                    dgs = [len(files), '{0},{1},{2}'.format(gdir, gdtype, gexp)]
                    WLOG(params, 'debug', TextEntry('90-001-00029', args=dgs))
                    group_files.append(files)
                    group_dir.append(gdir)
                    group_dtype.append(gdtype)
                    group_exp_set.append(gexp)
                    group_dates.append(gdate)
    # return groups
    groups = [group_files, group_dir, group_dtype, group_exp_set, group_dates]
    return groups


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
                dargs = [dir_jt, other_dirs_arr]
                WLOG(params, 'debug', TextEntry('90-001-00030', args=dargs),
                     wrap=False)
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
            # noinspection PyTypeChecker
            new_files[args[it]].append(mask_files[closest])
            # noinspection PyTypeChecker
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


# =============================================================================
# End of code
# =============================================================================
