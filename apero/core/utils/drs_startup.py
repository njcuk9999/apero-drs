#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-01-19 at 13:37

@author: cook
"""
import warnings
from collections import OrderedDict
import importlib
import numpy as np
import os
from signal import signal, SIGINT
import sys
import traceback
from typing import Any, Dict, List, Tuple, Union

from apero.base import base
from apero.core.core import drs_base_classes as base_class
from apero.core.core import drs_exceptions
from apero.core.core import drs_misc
from apero.core.core import drs_text
from apero import lang
from apero.core import constants
from apero.core.core import drs_argument
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_utils
from apero.core.core import drs_database
from apero.io import drs_lock
from apero import plotting

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'drs_startup.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Astropy Time and Time Delta
Time, TimeDelta = base.AstropyTime, base.AstropyTimeDelta
# Get Logging function
WLOG = drs_log.wlog
TLOG = drs_log.Printer
# get print colours
COLOR = drs_misc.Colors()
# get param dict
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
DrsInputFile = drs_file.DrsInputFile
# Get function string
display_func = drs_log.display_func
# get the Drs Exceptions
DrsCodedException = drs_exceptions.DrsCodedException
# Get the text types
textentry = lang.textentry
# recipe control path
INSTRUMENT_PATH = base.CONST_PATH
CORE_PATH = base.CORE_PATH
PDB_RC_FILE = base.PDB_RC_FILE
CURRENT_PATH = ''
# Run keys
RUN_KEYS = dict()
RUN_KEYS['RUN_NAME'] = 'Run Unknown'
RUN_KEYS['SEND_EMAIL'] = False
RUN_KEYS['EMAIL_ADDRESS'] = None
RUN_KEYS['RUN_OBS_DIR'] = None
RUN_KEYS['EXCLUDE_OBS_DIRS'] = None
RUN_KEYS['INCLUDE_OBS_DIRS'] = None
RUN_KEYS['PI_NAMES'] = None
RUN_KEYS['MASTER_OBS_DIR'] = None
RUN_KEYS['UPDATE_OBJ_DATABASE'] = False
RUN_KEYS['CORES'] = 1
RUN_KEYS['STOP_AT_EXCEPTION'] = False
RUN_KEYS['TEST_RUN'] = False
RUN_KEYS['TRIGGER_RUN'] = False
RUN_KEYS['USE_ODO_REJECTLIST'] = True
RUN_KEYS['RECAL_TEMPLATES'] = False
RUN_KEYS['USE_ENGINEERING'] = False
RUN_KEYS['TELLURIC_TARGETS'] = None
RUN_KEYS['SCIENCE_TARGETS'] = None


# =============================================================================
# Define functions
# =============================================================================
def setup(name: str = 'None', instrument: str = 'None',
          fkwargs: Union[Dict[str, Any], None] = None, quiet: bool = False,
          threaded: bool = False, enable_plotter: bool = True,
          rmod: Any = None) -> Tuple[DrsRecipe, ParamDict]:
    """
    Recipe setup script for recipe "name" and "instrument"

    :param name: string, the name of the recipe, if 'None', assumes there is no
                   recipe set
    :param instrument: string, the instrument name, if 'None' assumes there is
                       no instrument set
    :param fkwargs: dictionary or None, argument keywords
    :param quiet: bool, if True does not print out setup text
    :param threaded: bool, if True we have a parallel process so do not
                     catch SIGINT as normal
    :param enable_plotter: bool, if True do not enable plotter
    :param rmod: object, a custom recipe defintion to use (for testing
                 purposes only)

    :type name: str
    :type instrument: str
    :type fkwargs: dict
    :type quiet: bool
    :type threaded: bool
    :type enable_plotter: bool

    :exception SystemExit: on caught errors

    :returns: returns the recipe instance (DrsRecipe) and parameter
              dictionary for constants (ParamDict)
    :rtype: Tuple[DrsRecipe, ParamDict]
    """
    # set function name
    func_name = display_func('setup', __NAME__)
    # catch sigint (if not threaded) -- if threaded can only be in main thread
    if not threaded:
        signal(SIGINT, constants.catch_sigint)
    # deal with no keywords
    if fkwargs is None:
        fkwargs = dict()
    # deal with quiet in fkwargs
    if 'quiet' in fkwargs:
        if fkwargs['quiet'] in [True, 'True', 1]:
            quiet = True
        del fkwargs['quiet']
    # set up process id
    pid, htime = _assign_pid()
    # Clean WLOG
    WLOG.clean_log(pid)
    # get filemod and recipe mod
    #  must set instrument here as we could need 'None' (for some tools that
    #  are above the instrument level)
    pconst = constants.pload(instrument=instrument)
    filemod = pconst.FILEMOD()
    # deal with rmod coming from call
    if rmod is None:
        recipemod = pconst.RECIPEMOD()
    else:
        recipemod = rmod
    # find recipe
    recipe, recipemod = find_recipe(name, instrument, mod=recipemod)
    # -------------------------------------------------------------------------
    # check that instrument is valid (i.e. input instrument is None or matches
    #    base.IPARAMS)
    if 'INSTRUMENT' in base.IPARAMS:
        if not drs_text.null_text(instrument, ['None']):
            if instrument != base.IPARAMS['INSTRUMENT']:
                emsg = 'Cannot use {0} for instrument {1}'
                eargs = [name, base.IPARAMS['INSTRUMENT']]
                WLOG(None, 'error', emsg.format(*eargs))
        else:
            # update instrument
            instrument = str(base.IPARAMS['INSTRUMENT'])
            # update recipe instrument
            recipe.instrument = str(instrument)
            # need to update filemod and recipe mod
            pconst = constants.pload()
            # update filemod
            filemod = pconst.FILEMOD()
            # deal with rmod coming from call
            if rmod is None:
                recipemod = pconst.RECIPEMOD()
            else:
                recipemod = rmod
    # -------------------------------------------------------------------------
    # set file module and recipe module
    recipe.filemod = filemod.copy()
    recipe.recipemod = recipemod
    # clean params
    recipe.params = ParamDict()
    # set recipemod
    recipe.recipemod = recipemod
    # quietly load DRS parameters (for setup)
    recipe.get_drs_params(quiet=True, pid=pid, date_now=htime)
    # set input and output blocks
    recipe.input_block = drs_file.DrsPath(recipe.params,
                                          block_kind=recipe.in_block_str)
    recipe.output_block = drs_file.DrsPath(recipe.params,
                                           block_kind=recipe.out_block_str)
    # -------------------------------------------------------------------------
    # need to deal with drs group
    if 'DRS_GROUP' in fkwargs:
        drsgroup = fkwargs['DRS_GROUP']
        del fkwargs['DRS_GROUP']
    else:
        drsgroup = None
    # set DRS_GROUP
    recipe.params.set('DRS_GROUP', drsgroup, source=func_name)
    recipe.params.set('DRS_RECIPE_TYPE', recipe.recipe_type, source=func_name)
    recipe.params.set('DRS_RECIPE_KIND', recipe.recipe_kind, source=func_name)
    # set master
    recipe.params.set('IS_MASTER', recipe.master, source=func_name)
    # -------------------------------------------------------------------------
    # need to set debug mode now
    recipe = _set_debug_from_input(recipe, fkwargs)
    # -------------------------------------------------------------------------
    # need to look for observation directory in arguments
    recipe = _set_obsdir_from_input(recipe, fkwargs)
    # -------------------------------------------------------------------------
    # need to see if we are forcing input and output block directories
    recipe = _set_force_dirs(recipe, fkwargs)
    # -------------------------------------------------------------------------
    # do not need to display if we have special keywords
    quiet = _quiet_keys_present(recipe, quiet, fkwargs)
    # -------------------------------------------------------------------------
    # deal with parallel argument (must be pushed before other arguments)
    if _parallel_key_present(fkwargs):
        recipe.params['INPUTS']['PARALLEL'] = True
    else:
        recipe.params['INPUTS']['PARALLEL'] = False
    # -------------------------------------------------------------------------
    # display (print only no log)
    if (not quiet) and ('instrument' not in recipe.args):
        # display title
        _display_drs_title(recipe.params, drsgroup, printonly=True)
    # -------------------------------------------------------------------------
    # display loading message
    TLOG(recipe.params, '', 'Loading Arguments. Please wait...')
    # -------------------------------------------------------------------------
    # load index database manager
    indexdb = drs_database.IndexDatabase(recipe.params, check=False)
    # interface between "recipe", "fkwargs" and command line (via argparse)
    recipe.recipe_setup(indexdb, fkwargs)
    # -------------------------------------------------------------------------
    # deal with options from input_parameters
    recipe.option_manager()
    # update default params
    # WLOG.update_param_dict(recipe.drs_params)
    # -------------------------------------------------------------------------
    # clear loading message
    TLOG(recipe.params, '', '')
    # -------------------------------------------------------------------------
    # create runstring and log args/kwargs/skwargs (must be done after
    #    option_manager)
    recipe.set_inputs()
    # -------------------------------------------------------------------------
    # read parameters from run file (if defined in CRUNFILE from user args)
    if 'CRUNFILE' in recipe.params['INPUTS']:
        # get run file from inputs
        runfile = recipe.params['INPUTS']['CRUNFILE']
        # deal with run file
        if not drs_text.null_text(runfile):
            recipe.params, _ = read_runfile(recipe.params, runfile,
                                            log_overwrite=False)
    # -------------------------------------------------------------------------
    # display
    if not quiet:
        # display initial parameterisation
        if recipe.params['DRS_DEBUG'] == 42:
            _display_ee(recipe.params)
        # display initial parameterisation
        _display_initial_parameterisation(recipe.params, printonly=True)
        # print out of the parameters used
        _display_run_time_arguments(recipe, fkwargs, printonly=True)
    # -------------------------------------------------------------------------
    # We must have DRS_DATA_MSG_FULL (the full path for this recipe)
    drs_data_msg_full = drs_log.get_drs_data_msg(recipe.params, reset=True,
                                                 group=drsgroup)
    recipe.params['DRS_DATA_MSG_FULL'] = drs_data_msg_full
    recipe.params.set_source('DRS_DATA_MSG_FULL', func_name)
    # -------------------------------------------------------------------------
    # update params in log
    WLOG.pin = recipe.params.copy()
    # copy params
    params = recipe.params.copy()
    # -------------------------------------------------------------------------
    # deal with setting obs_dir, inputdir and outputdir
    if recipe.input_block is not None:
        params['INPATH'] = recipe.input_block.abspath
    else:
        params['INPATH'] = ''
    if recipe.output_block is not None:
        params['OUTPATH'] = recipe.output_block.abspath
    else:
        params['OUTPATH'] = ''
    # deal with having a obs_dir set
    params['OBS_DIR'] = ''
    if 'OBS_DIR' in params['INPUTS']:
        # assume this is the input obs dir
        if recipe.obs_dir is not None:
            params['OBS_DIR'] = recipe.obs_dir.obs_dir

    params.set_sources(['INPATH', 'OUTPATH', 'OBS_DIR'], func_name)
    # set outfiles storage
    params['OUTFILES'] = OrderedDict()
    params.set_source('OUTFILES', func_name)
    # -------------------------------------------------------------------------
    cond1 = not drs_text.null_text(instrument, ['None', ''])
    cond2 = params['INPATH'] is not None
    cond3 = params['OUTPATH'] is not None
    cond4 = params['OBS_DIR'] is not None
    if cond1 and cond2 and cond4:
        inpath = str(params['INPATH'])
        obs_dir = str(params['OBS_DIR'])
        _make_dirs(params, os.path.join(inpath, obs_dir))
    if cond1 and cond3 and cond4:
        outpath = str(params['OUTPATH'])
        obs_dir = str(params['OBS_DIR'])
        _make_dirs(params, os.path.join(outpath, obs_dir))
    # -------------------------------------------------------------------------
    # deal with data passed from call to main function
    if 'DATA_DICT' in fkwargs:
        # log process: data being passed from call
        iargs = [', '.join(list(fkwargs['DATA_DICT'].keys()))]
        WLOG(params, 'info', textentry('40-001-00021', args=iargs))
        # push into params
        params['DATA_DICT'] = fkwargs['DATA_DICT']
    else:
        params['DATA_DICT'] = ParamDict()
    # -------------------------------------------------------------------------
    # lock parameter dictionary (cannot add items after this point)
    params.lock()
    # update params in log / and recipes after locking
    recipe.params = params.copy()
    WLOG.pin = params.copy()
    # -------------------------------------------------------------------------
    # need to update files with new params
    _update_input_params(params, recipe.args)
    _update_input_params(params, recipe.kwargs)
    # -------------------------------------------------------------------------
    # push display into log (before was print only)
    if not quiet:
        # display title
        _display_drs_title(recipe.params, drsgroup, logonly=True)
        # display initial parameterisation
        _display_initial_parameterisation(recipe.params, logonly=True)
        # display system info (log only)
        _display_system_info(recipe.params, logonly=True)
        # print out of the parameters used
        _display_run_time_arguments(recipe, fkwargs, logonly=True)
    # -------------------------------------------------------------------------
    # add in the plotter
    if enable_plotter:
        recipe.plot = plotting.Plotter(params, recipe)
    # -------------------------------------------------------------------------
    # add the recipe log
    cond1 = not drs_text.null_text(instrument, ['None', ''])
    cond2 = params['DRS_RECIPE_TYPE'] != 'nolog-tool'
    if cond1 and cond2:
        recipe.log = drs_utils.RecipeLog(recipe.name, recipe.shortname,
                                         params, logger=WLOG)
        # add log file to log (only used to save where the log is)
        logfile = drs_log.get_logfilepath(WLOG, params)
        recipe.log.set_log_file(logfile)
        recipe.log.block_kind = str(recipe.out_block_str)
        recipe.log.recipe_kind = str(recipe.recipe_kind)
        # add user input parameters to log
        recipe.log.runstring = recipe.runstring
        recipe.log.args = recipe.largs
        recipe.log.kwargs = recipe.lkwargs
        recipe.log.skwargs = recipe.lskwargs
        # set lock function (lock file is OBS_DIR + _log
        # recipe.log.set_lock_func(drs_lock.locker)
        # write recipe log
        recipe.log.write_logfile()
    # -------------------------------------------------------------------------
    # return arguments
    return recipe, params


def run(func: Any, recipe: DrsRecipe,
        params: ParamDict) -> Tuple[Dict[str, Any], bool]:
    """
    Runs the function "func" that must have arguments "recipe" and "params"
    and nothing else.

    i.e. func(recipe, params)
    or   __main__(recipe, params)

    :param func: function, with arguments "recipe" and "params"
    :param recipe: DrsRecipe, the drs recipe to use with "func"
    :param params: Paramdict, the constant parameter dictionary

    :type recipe: DrsRecipe
    :type params: ParamDict

    :returns: the local variables (in a dictionary) and whether drs was
              successful. If DEBUG0000 in keywords
    :rtype: tuple[dict, bool]
    """
    # set function name
    _ = display_func('run', __NAME__)
    # run main bulk of code (catching all errors)
    if params['DRS_DEBUG'] > 0:
        llmain = func(recipe, params)
        llmain['e'], llmain['tb'] = None, None
        success = True
    else:
        try:
            llmain = func(recipe, params)
            llmain['e'], llmain['tb'] = None, None
            success = True
        except KeyboardInterrupt as e:
            # get trace back
            string_trackback = traceback.format_exc()
            # on Ctrl + C was not a success
            success = False
            # print the error
            WLOG(params, 'error', 'SIGINT or CTRL-C detected. Exiting',
                 raise_exception=False, wrap=False, printonly=True)
            # log the error
            WLOG(params, 'error', string_trackback,
                 raise_exception=False, wrap=False, logonly=True)
            # save params to llmain
            llmain = dict(e=e, tb=string_trackback, params=params,
                          recipe=recipe)
            # add error to log file
            if params['DRS_RECIPE_TYPE'] != 'nolog-tool':
                recipe.log.add_error('KeyboardInterrupt', '')
            # reset the lock directory
            drs_lock.reset_lock_dir(params)
        except drs_exceptions.LogExit as e:
            # get trace back
            string_trackback = traceback.format_exc()
            # on LogExit was not a success
            success = False
            # log the error
            WLOG(params, 'error', string_trackback,
                 raise_exception=False, wrap=False, logonly=True)
            # save params to llmain
            llmain = dict(e=e, tb=string_trackback, params=params,
                          recipe=recipe)
            # add error to log file
            if params['DRS_RECIPE_TYPE'] != 'nolog-tool':
                recipe.log.add_error(type(e), str(e))
            # reset the lock directory
            drs_lock.reset_lock_dir(params)
        except drs_exceptions.DrsCodedException as e:
            # get trace back
            string_trackback = traceback.format_exc()
            # on LogExit was not a success
            success = False
            # log the error
            WLOG(params, 'error', string_trackback,
                 raise_exception=False, wrap=False, logonly=False)
            # save params to llmain
            llmain = dict(e=e, tb=string_trackback, params=params,
                          recipe=recipe)
            # add error to log file
            if params['DRS_RECIPE_TYPE'] != 'nolog-tool':
                recipe.log.add_error(type(e), str(e))
            # reset the lock directory
            drs_lock.reset_lock_dir(params)
        except drs_exceptions.DebugExit as e:
            WLOG(params, 'error', e.errormessage, raise_exception=False)
            # on debug exit was not a success
            success = False
            # save params to llmain
            llmain = dict(e=e, tb='', params=params, recipe=recipe)
            # add error to log file
            if params['DRS_RECIPE_TYPE'] != 'nolog-tool':
                recipe.log.add_error('Debug Exit', '')
            # reset the lock directory
            drs_lock.reset_lock_dir(params)
        except Exception as e:
            # get the trace back
            string_trackback = traceback.format_exc()
            # on LogExit was not a success
            success = False
            # construct the error with a trace back
            emsg = textentry('01-010-00001', args=[type(e)])
            emsg += '\n\n' + textentry(string_trackback)
            WLOG(params, 'error', emsg, raise_exception=False, wrap=False)
            # save params to llmain
            llmain = dict(e=e, tb=string_trackback, params=params,
                          recipe=recipe)
            # add error to log file
            if params['DRS_RECIPE_TYPE'] != 'nolog-tool':
                recipe.log.add_error(type(e), str(e))
            # reset the lock directory
            drs_lock.reset_lock_dir(params)
        except SystemExit as e:
            # get the trace back
            string_trackback = traceback.format_exc()
            # on LogExit was not a success
            success = False
            # construct the error with a trace back
            emsg = textentry('01-010-00001', args=[type(e)])
            emsg += '\n\n' + textentry(string_trackback)
            WLOG(params, 'error', emsg, raise_exception=False, wrap=False)
            # save params to llmain
            llmain = dict(e=e, tb=string_trackback, params=params,
                          recipe=recipe)
            # add error to log file
            if params['DRS_RECIPE_TYPE'] != 'nolog-tool':
                recipe.log.add_error(type(e), str(e))
            # reset the lock directory
            drs_lock.reset_lock_dir(params)
    # return llmain and success
    return llmain, success


def return_locals(params: ParamDict, ll: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deal with returning into ipython (if params['IPYTHON_RETURN'] is True)

    :param params: ParamDict, parameter dictionary of constants
    :param ll: dictionary, the local namespace in dictionary form - normally
               called with locals()

    :return: dictionary, the lcoal namespace in dictionary form
    """
    # set function name
    _ = display_func('return_locals', __NAME__)
    # else return ll
    return ll


def end_main(params: ParamDict, llmain: Union[Dict[str, Any], None],
             recipe: DrsRecipe, success: bool, outputs: str = 'red',
             end: bool = True, quiet: bool = False,
             keys: Union[List[str], None] = None) -> Dict[str, Any]:
    """
    Function to deal with the end of a recipe.main script
        1. indexes outputs
        2. Logs end messages
        3. Clears logs and warnings

    :param params: ParamDict, the parameter dictionary containing constants
    :param llmain: dict, the global outputs of the namespace where called
    :param recipe: DrsRecipe, the recipe instance for this recipe
    :param success: bool, if True program has successfully completed else
                    it has not
    :param outputs: string, the type of outputs i.e:
        - 'None'  (for no outputs)
        - 'raw'
        - 'tmp'
        - 'red'
        - 'out'
    :param end: bool, if we should run full end routines
    :param quiet: bool, if we should not print out standard output
    :param keys: list of string, any variable in main function can be named here
                 and will be returned on completion

    :type params: ParamDict
    :type llmain: Union[dict, None]
    :type recipe: DrsRecipe
    :type success: bool
    :type outputs: str
    :type end: bool
    :type quiet: bool
    :type keys: Union[None, List[str]]

    :exception SystemExit: on caught errors

    :return: the updated parameter dictionary
    :rtype: ParamDict
    """
    # set function name
    func_name = display_func('end_main', __NAME__)
    # -------------------------------------------------------------------------
    # get params/plotter from llmain if present
    #     (from __main__ function not main)
    if llmain is not None:
        if 'params' in llmain:
            params = llmain['params']

    # -------------------------------------------------------------------------
    # get quiet from inputs
    if 'QUIET' in params['INPUTS']:
        quiet = params['INPUTS'].get('QUIET', False)
        # deal with quiet being unset
        if quiet is None:
            quiet = False
    # -------------------------------------------------------------------------
    if outputs not in [None, 'None', '']:
        # index files
        index_files(params, recipe)
    # -------------------------------------------------------------------------
    # log end message
    if end:
        # log the success (or failure)
        if success and (not quiet):
            iargs = [str(params['RECIPE'])]
            WLOG(params, 'info', params['DRS_HEADER'])
            WLOG(params, 'info', textentry('40-003-00001', args=iargs))
            WLOG(params, 'info', params['DRS_HEADER'])
        elif not quiet:
            wargs = [str(params['RECIPE'])]
            WLOG(params, 'info', params['DRS_HEADER'], colour='red')
            WLOG(params, 'warning', textentry('40-003-00005', args=wargs),
                 colour='red', sublevel=8)
            WLOG(params, 'info', params['DRS_HEADER'], colour='red')
        # ---------------------------------------------------------------------
        # deal with logging (if log exists in recipe)
        if success and recipe.log is not None:
                recipe.log.end()
        elif recipe.log is not None:
            recipe.log.end(success=False)
        # ---------------------------------------------------------------------
        # unlock parameter dictionary
        params.unlock()
        # add the logger messages to params
        params = WLOG.output_param_dict(params)
        # update params in log / and recipes after locking
        recipe.params = params.copy()
        WLOG.pin = params.copy()
        # lock parameter dictionary (cannot add items after this point)
        params.lock()
        # ---------------------------------------------------------------------
        # finally clear out the log in WLOG
        WLOG.clean_log(params['PID'])
        # ---------------------------------------------------------------------
        # deal with clearing warnings
        drs_exceptions.clear_warnings()
    # -------------------------------------------------------------------------
    # deal with closing graphs
    # -------------------------------------------------------------------------
    if end:
        end_plotting(params, recipe)

    # -------------------------------------------------------------------------
    # return ll (the output dictionary)
    # -------------------------------------------------------------------------
    if end:
        # out storage (i.e. ll)
        outdict = dict()
        # copy params
        outdict['params'] = params.copy()
        # copy recipe
        newrecipe = DrsRecipe()
        newrecipe.copy(recipe)
        outdict['recipe'] = newrecipe
        if 'tb' in llmain:
            outdict['trace'] = llmain['tb']
        # copy success
        outdict['success'] = bool(success)
        # copy qc passed
        if 'passed' in llmain:
            outdict['passed'] = bool(llmain['passed'])
        else:
            outdict['passed'] = True
        # special (shallow) copy from apero_extract
        if 'e2dsoutputs' in llmain:
            outdict['e2dsoutputs'] = llmain['e2dsoutputs']
        # deal with special keys
        if keys is not None:
            for key in keys:
                if key in llmain:
                    outdict[key] = llmain[key]
        # return outdict
        return outdict


def index_files(params, recipe):
    # load index database
    indexdb = drs_database.IndexDatabase(params)
    indexdb.load_db()
    # get pconstants
    pconst = constants.pload()
    # load index header keys
    iheader_cols = pconst.INDEX_HEADER_COLS()
    rkeys = list(iheader_cols.names)
    # loop around output_files
    for okey in recipe.output_files:
        # get output dict for okey
        output = recipe.output_files[okey]
        # set up drs path
        outfile = recipe.output_block.copy()
        # update parameters
        outfile.abspath = str(output['ABSPATH'])
        outfile.obs_dir = str(output['OBS_DIR'])
        outfile.basename = str(output['FILENAME'])
        # get parameters for add entry
        block_kind = str(output['BLOCK_KIND'])
        recipename = str(output['RECIPE'])
        runstring = str(output['RUNSTRING'])
        infiles = str(output['INFILES'])
        used = int(output['USED'])
        rawfix = int(output['RAWFIX'])
        # store header keys
        hkeys = dict()
        # loop around required index database header keys
        for rkey in rkeys:
            if rkey in output:
                # deal with null entries
                if drs_text.null_text(output[rkey], ['None', '', 'Null']):
                    hkeys[rkey] = 'Null'
                else:
                    hkeys[rkey] = output[rkey]
            else:
                hkeys[rkey] = 'Null'
        # finally add to database
        indexdb.add_entry(outfile, block_kind, recipename, runstring, infiles,
                          hkeys, used, rawfix)


def copy_kwargs(params: ParamDict, recipe: Union[DrsRecipe, None] = None,
                recipename: Union[str, None] = None,
                recipemod: Union[base_class.ImportModule, None] = None,
                **kwargs) -> Dict[str, Any]:
    """
    Copy input arguments (positional and optional) from "recipe" main to a
    dictionary (for later use)

    i.e. if we had recipe1.main(arg1, arg2, arg3) we want to produce
    dict(arg1=arg1, arg2=arg2, arg3=arg3) for recipe 2

    however we probably want to update some kwargs thus any other argument
    will overwrite previous arguments

    i.e. if call to recipe1 is: recipe1.main(arg1, arg2, arg3)

         and call to this function is: copy_kwargs(recipe, arg2='test')

         output is: dict(arg1=arg1, arg2='test', arg3=arg3)

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe to copy keywords from (if not set
                   must set recipename -- and then we find the recipe instance)
    :param recipename: str, if 'recipe' not set uses the name to search for
                       a recipe instance (using find_recipe) - this is then
                       the recipe the keywords are copied from
    :param recipemod: ImportModule instance of the recipe definitions import
                      module - this avoids loading the module again
                      (if already loaded) - can be not set (and loads module)
    :param kwargs: override the keys in recipe that are copied to the
                   dictionary - used when using the recipe args for a new
                   run (with some arguments updated)

    :return: dictionary of args i.e. dict(arg1=arg1, arg2='test', arg3=arg3)
    """
    # set function name
    func_name = display_func('copy_kwargs', __NAME__)
    # deal with no recipe
    if recipe is None and recipename is None:
        WLOG(params, 'error', textentry('00-001-00040', args=func_name))
    elif recipe is None:
        recipe, _ = find_recipe(recipename, params['INSTRUMENT'], recipemod)
    # get inputs for
    inputs = params['INPUTS']
    # get recipe arguments/kwarg arguments
    mainargs = recipe.args
    mainkwargs = recipe.kwargs
    # storage for output keyword arguments
    outkwargs = dict()
    # loop around arguments and decide where to get value from
    for arg in mainargs:
        # if in kwargs overwrite value with new value
        if arg in kwargs:
            outkwargs[arg] = kwargs[arg]
        # else if it is in inputs use recipe.main value
        elif arg.upper() in inputs:
            # deal with files being a tuple of (str, DrsFile)
            if mainargs[arg].dtype in ['file', 'files']:
                value = inputs[arg][0]
            else:
                value = inputs[arg]
            # deal with None values
            if value == 'None':
                value = None
            # add to outkwargs
            outkwargs[arg] = value
    # loop around arguments and decide where to get value from
    for kwarg in mainkwargs:
        # if in kwargs overwrite value with new value
        if kwarg in kwargs:
            outkwargs[kwarg] = kwargs[kwarg]
        # else if it is in inputs use recipe.main value
        elif kwarg.upper() in inputs:
            # deal with files being a tuple of (str, DrsFile)
            if mainkwargs[kwarg].dtype in ['file', 'files']:
                value = inputs[kwarg]
                if type(value) in [list, np.ndarray]:
                    value = value[0]
            else:
                value = inputs[kwarg]
            # deal with None values
            if value == 'None':
                value = None
            # add to outkwargs
            outkwargs[kwarg] = value
    # now return out keyword arguments
    return outkwargs


def file_processing_update(params: ParamDict, it: int, num_files: int):
    """
    Printout via wlog of the file process
    i.e. Process file {it+1} of {num_files}

    :param params: ParamDict, the parameter dictionary of constants
    :param it: int, the current iteration (starts at zero but display it + 1)
    :param num_files: int, the total number of files to process (it + 1 of
                      total)

    :return: None, logs via WLOG
    """
    # set function name
    _ = display_func('file_processing_update', __NAME__)
    # log
    WLOG(params, '', params['DRS_HEADER'])
    eargs = [it + 1, num_files]
    WLOG(params, '', textentry('40-001-00020', args=eargs))
    WLOG(params, '', params['DRS_HEADER'])


def fiber_processing_update(params: ParamDict, fiber: str):
    """
    Printout via wlog of which fiber we are processing
    i.e. Process fiber {fiber}

    :param params: ParamDict, the parameter dictionary of constants
    :param fiber: str, the fiber name for this iteration

    :return: None, logs via WLOG
    """
    # set function name
    _ = display_func('fiber_processing_update', __NAME__)
    # log
    WLOG(params, '', params['DRS_HEADER'])
    WLOG(params, '', textentry('40-001-00022', args=[fiber]))
    WLOG(params, '', params['DRS_HEADER'])


def end_plotting(params: ParamDict, recipe: Union[DrsRecipe, None]):
    """
    Closes all currently opened plots (via DrsRecipe.plot.close_plots)
    required as plt is not defined unless inside DrsRecipe.plot)

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, if set is the recipe instance with the ability
                   to close plots via DrsRecipe.plot.close_plots() - if
                   None just loads matplotlib.pyplot as plt and plt.close('all')

    :return: None
    """
    # set function name
    _ = display_func('end_plotting', __NAME__)
    # only do this is we don't have a recipe
    if recipe is None or not hasattr(recipe, 'plot'):
        WLOG(params, 'debug', textentry('90-100-00004'))
        import matplotlib.pyplot as plt
        plt.close('all')
        return
    # get the plotter from recipe
    plotter = recipe.plot
    if plotter is not None:
        WLOG(params, 'debug', textentry('90-100-00005'))
        if len(plotter.debug_graphs) > 0:
            plotter.close_plots()


def group_name(params: ParamDict, suffix: str = 'group') -> str:
    """
    Constructs the group name APEROG-{PID}_{RECIPE}_{SUFFIX}

    :param params: ParamDict, the parameter dictionary of constants
    :param suffix: str, the suffix to add to the group name (defaults
                   to 'group')

    :return: str, the group name APEROG-{PID}_{RECIPE}_{SUFFIX}
    """
    # set function name
    _ = display_func('group_name', __NAME__)
    # ----------------------------------------------------------------------
    # deal with no PID
    if 'PID' not in params:
        pid = 'UNKNOWN-PID'
    else:
        pid = str(params['PID'])
    # ----------------------------------------------------------------------
    # deal with no recipe
    if 'RECIPE' not in params:
        recipename = 'UNKNOWN-RECIPE'
    else:
        recipename = str(params['RECIPE'].replace('.py', ''))
    # ----------------------------------------------------------------------
    args = [pid, recipename, suffix]
    # construct group name
    groupname = 'APEROG-{0}_{1}_{2}'.format(*args)
    # return group name
    return groupname


def read_runfile(params: ParamDict, runfile: str,
                 rkind: str = 'start',
                 log_overwrite: bool = False) -> Tuple[ParamDict, OrderedDict]:
    """
    Read a provided run file and update params / return the run file sequence

    :param params: ParamDict, the parameter dictionary of constants
    :param runfile: str, the path to the run file
    :param rkind: str, either 'start' for startup or 'run' for processing mode
    :param log_overwrite: bool, if True prevents messages about overwriting
                          param keys

    :return:
    """
    func_name = __NAME__ + '.read_runfile()'
    # ----------------------------------------------------------------------
    # get properties from params
    run_key = params['REPROCESS_RUN_KEY']
    run_dir = params['DRS_DATA_RUN']
    # ----------------------------------------------------------------------
    # check if run file exists
    if not os.path.exists(runfile):
        # construct run file
        runfile = os.path.join(run_dir, runfile)
        # check that it exists
        if not os.path.exists(runfile):
            WLOG(params, 'error', textentry('09-503-00002', args=[runfile]))
    # ----------------------------------------------------------------------
    # now try to load run file
    try:
        keys, values = np.genfromtxt(runfile, delimiter='=', comments='#',
                                     unpack=True, dtype=str)
    except Exception as e:
        # log error
        eargs = [runfile, type(e), e, func_name]
        WLOG(params, 'error', textentry('09-503-00003', args=eargs))
        keys, values = [], []
    # ----------------------------------------------------------------------
    # table storage
    runtable = OrderedDict()
    keytable = OrderedDict()
    # ----------------------------------------------------------------------
    # unlock params
    if params.locked:
        relock = True
        params.unlock()
    else:
        relock = False
    # ----------------------------------------------------------------------
    # sort out keys into id keys and values for params
    for it in range(len(keys)):
        # get this iterations values
        key = keys[it].upper().strip()
        value = values[it].strip()
        # find the id keys
        if key.startswith(run_key):
            # attempt to read id string
            try:
                runid = int(key.replace(run_key, ''))
            except Exception as e:
                eargs = [key, value, run_key, type(e), e, func_name]
                WLOG(params, 'error', textentry('09-503-00004', args=eargs))
                runid = None
            # check if we already have this column
            if runid in runtable:
                wargs = [runid, keytable[runid], runtable[runid],
                         keys[it], values[it][:40] + '...']
                WLOG(params, 'warning', textentry('10-503-00001', args=wargs),
                     sublevel=2)
            # add to table
            runtable[runid] = value
            keytable[runid] = key
        # else add to parameter dictionary
        else:
            # deal with special strings
            if value.upper() == 'TRUE':
                value = True
            elif value.upper() == 'FALSE':
                value = False
            elif value.upper() == 'NONE':
                value = None
            # log if we are overwriting value
            if key in params:
                # don't log if log overwrite is set to True
                if log_overwrite:
                    continue
                # only log if value was not null before
                if not drs_text.null_text(params[key], ['', 'None']):
                    wargs = [key, params[key], value]
                    wmsg = textentry('10-503-00002', args=wargs)
                    WLOG(params, 'warning', wmsg, sublevel=2)
            # add to params
            params[key] = value
            params.set_source(key, func_name)
    # ----------------------------------------------------------------------
    if rkind == 'run':
        # push default values (in case we don't have values in run file
        for key in RUN_KEYS:
            if key not in params:
                # print that we are using default settings (not a warning)
                wargs = [key, RUN_KEYS[key]]
                WLOG(params, '', textentry('10-503-00005', args=wargs))
                # push keys to params
                params[key] = RUN_KEYS[key]
                params.set_source(key, __NAME__ + '.RUN_KEYS')

        # ---------------------------------------------------------------------
        # deal with arguments from command line (params['INPUTS'])
        # ---------------------------------------------------------------------
        # set observation directory
        if 'OBS_DIR' in params['INPUTS']:
            # get night name
            _obs_dir = params['INPUTS']['OBS_DIR']
            # deal with none nulls
            if not drs_text.null_text(_obs_dir, ['None', '', 'All']):
                params['OBS_DIR'] = _obs_dir
        # make sure observation directory is str or None
        if drs_text.null_text(params['OBS_DIR'], ['None', '', 'All']):
            params['OBS_DIR'] = None
        # ---------------------------------------------------------------------
        # exclude observation directories
        if 'EXCLUDE_OBS_DIRS' in params['INPUTS']:
            # get night name blacklist
            _ex_obs_dirs = params['INPUTS']['EXCLUDE_OBS_DIRS']
            # deal with non-null value
            if not drs_text.null_text(_ex_obs_dirs, ['None', '', 'All']):
                exclude = params['INPUTS'].listp('EXCLUDE_OBS_DIRS')
                params['EXCLUDE_OBS_DIRS'] = exclude
        # ---------------------------------------------------------------------
        # include observation directories
        if 'INCLUDE_OBS_DIRS' in params['INPUTS']:
            # get night name whitelist
            _inc_obs_dirs = params['INPUTS']['INCLUDE_OBS_DIRS']
            # deal with non-null value
            if not drs_text.null_text(_inc_obs_dirs, ['None', '', 'All']):
                include = params['INPUTS'].listp('INCLUDE_OBS_DIRS')
                params['INCLUDE_OBS_DIRS'] = include
        # ---------------------------------------------------------------------
        # add pi name list
        if 'PI_NAMES' in params['INPUTS']:
            # get list of pi names
            _pinames = params['INPUTS']['PI_NAMES']
            # deal with non-null value
            if not drs_text.null_text(_pinames, ['None', '', 'All']):
                params['PI_NAMES'] = params['INPUTS'].listp('PI_NAMES')
        # ---------------------------------------------------------------------
        # deal with having a file specified
        params['FILENAME'] = None
        if 'FILENAME' in params['INPUTS']:
            # get filename arg
            _filename = params['INPUTS']['FILENAME']
            # deal with non-null value
            if not drs_text.null_text(_filename, ['None', '', 'All']):
                # if it is a string treat it as a list of string (just a string
                #   works too)
                if isinstance(params['INPUTS']['FILENAME'], str):
                    params['FILENAME'] = params['INPUTS'].listp('FILENAME')
                # should really get here but set it to the _filename value
                # anyway
                else:
                    params['FILENAME'] = _filename
        # ---------------------------------------------------------------------
        # deal with getting test run from user input
        if 'TEST' in params['INPUTS']:
            # get the value of test
            _test = params['INPUTS']['TEST']
            # deal with non null value
            if not drs_text.null_text(_test, ['', 'None']):
                # test for true value
                params['TEST_RUN'] = drs_text.true_text(_test)
        # ---------------------------------------------------------------------
        # deal with getting trigger run from user input
        if 'TRIGGER' in params['INPUTS']:
            # get the value of trigger
            _trigger = params['INPUTS']['TRIGGER']
            # deal with non null values
            if not drs_text.null_text(_trigger, ['', 'None']):
                # test for true value
                params['TRIGGER_RUN'] = drs_text.true_text(_trigger)

            # if trigger if defined night name must be as well
            if params['OBS_DIR'] is None and params['TRIGGER_RUN']:
                # cause an error if obs_dir not set
                WLOG(params, 'error', textentry('09-503-00010'))
        # ---------------------------------------------------------------------
        # switch for setting science targets (from user inputs)
        if 'SCIENCE_TARGETS' in params['INPUTS']:
            # get the value of science_targets
            _science_targets = params['INPUTS']['SCIENCE_TARGETS']
            # deal with non null value
            if not drs_text.null_text(_science_targets, ['', 'None']):
                # remove leading/trailing speechmarks
                sargs = [_science_targets, ['"', "'"]]
                _science_targets = drs_text.cull_leading_trailing(*sargs)
                # set science targets
                params['SCIENCE_TARGETS'] = _science_targets
        # ---------------------------------------------------------------------
        # switch for setting telluric target list (from user inputs)
        if 'TELLURIC_TARGETS' in params['INPUTS']:
            # get the value of telluric targets
            _tellu_targets = params['INPUTS']['TELLURIC_TARGETS']
            # deal with non null value
            if not drs_text.null_text(_tellu_targets, ['', 'None']):
                # remove leading/trailing speechmarks
                targs = [_tellu_targets, ['"', "'"]]
                _tellu_targets = drs_text.cull_leading_trailing(*targs)
                # set telluric targets
                params['TELLURIC_TARGETS'] = _tellu_targets
        # ---------------------------------------------------------------------
        # switch whether we update object database (from user inputs)
        if 'UPDATE_OBJDB' in params['INPUTS']:
            # get the value of update obj database from inputs
            _update_objdb = params['INPUTS']['UPDATE_OBJDB']
            # deal with non null values only
            if not drs_text.null_text(_update_objdb, ['', 'None']):
                # get True/False
                _update_objdb = drs_text.true_text(_update_objdb)
                # set value
                params['UPDATE_OBJ_DATABASE'] = _update_objdb
    # -------------------------------------------------------------------------
    # relock params
    if relock:
        params.lock()
    # -------------------------------------------------------------------------
    # return parameter dictionary and runtable
    return params, runtable


# =============================================================================
# Define display functions
# =============================================================================
def _quiet_keys_present(recipe: DrsRecipe, quiet: bool,
                        fkwargs: Dict[str, Any]) -> bool:
    """
    Decides whether displaying is necessary based on whether we have special
    keys in fkwargs or sys.argv (input from command line)

    :param recipe: DrsRecipe instance, the recipe to act on
    :param fkwargs: dictionary, the input keywords from python call to recipe
    :param quiet: bool, the current status of quiet flag (True or False)

    :type recipe: DrsRecipe
    :type fkwargs: dict
    :type quiet: bool

    :returns: bool, the updated status of quiet flag
    :rtype: bool
    """
    # set function name
    _ = display_func('_quiet_keys_present', __NAME__)
    # get the special keys
    skeys = _get_recipe_keys(recipe.specialargs, add=['--help', '-h'])
    # see if we have a key
    if len(skeys) > 0:
        for skey in skeys:
            found_key = _search_for_key(skey, fkwargs)
            if found_key:
                quiet = True
    # deal with quiet key (special case)
    if _search_for_key('quiet', fkwargs):
        if 'quiet' in fkwargs and fkwargs['quiet'] is None:
            quiet = False
        else:
            quiet = True

    # return the updated quiet flag
    return quiet


def _parallel_key_present(fkwargs) -> bool:
    """
    Hack a way to get parallel argument before argparse

    :param fkwargs: dictionary, the input keywords from python call to recipe

    :return: bool, True if in parallel
    """
    # set function name
    _ = display_func('_parallel_key_present', __NAME__)
    # search for parallel
    parallel = False
    if _search_for_key('parallel', fkwargs):
        if 'parallel' in fkwargs and fkwargs['parallel'] is not None:
            parallel = fkwargs['parallel']
        else:
            # make sys.argv a string
            str_argv = ' '.join(sys.argv)
            # get rest of args
            argrest = str_argv.split('parallel')[-1].strip().upper()
            if argrest.startswith('=TRUE') or argrest.startswith('=1'):
                parallel = True
            elif argrest.startswith('TRUE') or argrest.startswith('1'):
                parallel = True
            else:
                parallel = False
    # return the updated quiet flag
    return parallel


def _display_drs_title(params: ParamDict, group: Union[str, None] = None,
                       printonly: bool = False, logonly: bool = False):
    """
    Display title for this execution

    :param params: ParamDict, parameter dictionary of constants
    :param group: str, the group name (can be None)
    :param printonly: bool, if True prints the title only
    :param logonly: bool, if True logs the title only (no printing)

    :returns: None
    """
    # set function name
    _ = display_func('_display_drs_title', __NAME__)
    # get colours
    colors = COLOR
    # create title
    title = ' * '
    title += colors.RED1 + ' {0} ' + colors.okgreen + '@{1}'
    title += ' (' + colors.BLUE1 + 'V{2}' + colors.okgreen + ')'
    title += colors.ENDC
    title = title.format(params['INSTRUMENT'], params['PID'],
                         params['DRS_VERSION'])

    # Log title
    _display_title(params, title, group, printonly, logonly)
    # print only
    if not logonly:
        _display_logo(params)


def _display_title(params: ParamDict, title: str,
                   group: Union[str, None] = None, printonly: bool = False,
                   logonly: bool = False):
    """
    Display any title between HEADER bars via the WLOG command

    :param params: ParamDict, parameter dictionary of constants
    :param title: string, title string

    :type params: ParamDict
    :type title: str

    :returns: None
    """
    # set function name
    _ = display_func('_display_title', __NAME__)
    # print and log
    WLOG(params, '', params['DRS_HEADER'], wrap=False, printonly=printonly,
         logonly=logonly)
    # add title
    WLOG(params, '', ' *\n{0}\n *'.format(title), wrap=False,
         printonly=printonly, logonly=logonly)
    # add group if defined
    if group is not None:
        WLOG(params, '', ' * \tGroup: {0}'.format(group), wrap=False,
             printonly=printonly, logonly=logonly)
    # end header
    WLOG(params, '', params['DRS_HEADER'], wrap=False,
         printonly=printonly, logonly=logonly)


def _display_logo(params: ParamDict):
    """
    Display the instrument logo

    :param params: ParamDict, the parameter dictionary of constants

    :return: None
    """
    # set function name
    _ = display_func('_display_logo', __NAME__)
    # get colours
    colors = COLOR
    # get pconstant
    pconstant = constants.pload()
    # noinspection PyPep8
    logo = pconstant.LOGO()
    for line in logo:
        WLOG(params, '', colors.RED1 + line + colors.ENDC, wrap=False,
             printonly=True)
    WLOG(params, '', params['DRS_HEADER'], wrap=False, printonly=True)


def _display_ee(params: ParamDict):
    """
    Display the logo text

    :param params: ParamDict, the parameter dictionary containing constants

    p must contain at least:
        - INSTRUMENT: string, the instrument name
        - DRS_HEADER: string, the header characters

    :type params: ParamDict

    :returns: None
    """
    # set function name
    _ = display_func('_display_ee', __NAME__)
    # get colours
    colors = COLOR
    # get pconstant
    pconstant = constants.pload()
    # noinspection PyPep8
    logo = pconstant.SPLASH()
    for line in logo:
        WLOG(params, '', colors.RED1 + line + colors.ENDC, wrap=False,
             printonly=True)
    WLOG(params, '', params['DRS_HEADER'], printonly=True)


def _display_initial_parameterisation(params: ParamDict,
                                      printonly: bool = False,
                                      logonly: bool = False):
    """
    Display initial parameterisation for this execution

    :param params: parameter dictionary, ParamDict containing constants

    :type params: ParamDict

    params must contain at least:
      - DRS_DATA_RAW: string, the directory that the raw data should
        be saved to/read from

      - DRS_DATA_REDUC: string, the directory that the reduced data
        should be saved to/read from

      - DRS_CALIB_DB: string, the directory that the calibration
        files should be saved to/read from

      - DRS_DATA_MSG: string, the directory that the log messages
        should be saved to

      - PRINT_LEVEL: string, Level at which to print, values can be:

          * 'all' - to print all events
          * 'info' - to print info/warning/error events
          * 'warning' - to print warning/error events
          * 'error' - to print only error events

      - LOG_LEVEL: string, Level at which to log, values can be:

          * 'all' - to print all events
          * 'info' - to print info/warning/error events
          * 'warning' - to print warning/error events
          * 'error' - to print only error events

      - DRS_PLOT: int, plotting mode

          * 0: no plotting
          * 1: basic plotting to screen (interactive)
          * 2: plotting saved to file (DRS_DATA_PLOT)

      - DRS_USED_DATE: string, the DRS USED DATE (not really used)

      - DRS_DATA_WORKING: (optional) string, the temporary working
        directory

      - DRS_DEBUG: int, Whether to run in debug mode

           * 0: no debug
           * 1: basic debugging on errors
           * 2: recipes specific (plots and some code runs)

    :return: None
    """
    # set function name
    _ = display_func('_display_initial_parameterisation', __NAME__)
    # Add initial parameterisation
    wmsgs = textentry('\n\tDRS_DATA_RAW: {}'.format(params['DRS_DATA_RAW']))
    wmsgs += textentry('\n\tDRS_DATA_REDUC: {}'
                       ''.format(params['DRS_DATA_REDUC']))
    wmsgs += textentry('\n\tDRS_DATA_WORKING: {}'
                       ''.format(params['DRS_DATA_WORKING']))
    wmsgs += textentry('\n\tDRS_CALIB_DB: {}'.format(params['DRS_CALIB_DB']))
    wmsgs += textentry('\n\tDRS_TELLU_DB: {}'.format(params['DRS_TELLU_DB']))
    wmsgs += textentry('\n\tDRS_DATA_ASSETS: {}'
                       ''.format(params['DRS_DATA_ASSETS']))
    wmsgs += textentry('\n\tDRS_DATA_MSG: {}'.format(params['DRS_DATA_MSG']))
    wmsgs += textentry('\n\tDRS_DATA_RUN: {}'.format(params['DRS_DATA_RUN']))
    wmsgs += textentry('\n\tDRS_DATA_PLOT: {}'.format(params['DRS_DATA_PLOT']))
    # add config sources
    for source in np.sort(params['DRS_CONFIG']):
        wmsgs += textentry('\n\tDRS_CONFIG: {0}'.format(source))
    # add database settings
    wmsgs = _display_database_settings(params, wmsgs)
    # add others
    wmsgs += textentry('\n\tPRINT_LEVEL: {}'.format(params['DRS_PRINT_LEVEL']))
    wmsgs += textentry('\n\tLOG_LEVEL: {}'.format(params['DRS_LOG_LEVEL']))
    wmsgs += textentry('\n\tDRS_PLOT: {}'.format(params['DRS_PLOT']))
    if params['DRS_DEBUG'] > 0:
        wargs = ['DRS_DEBUG', params['DRS_DEBUG']]
        wmsgs += '\n' + textentry('40-001-00009', args=wargs)
    # log to screen and file
    WLOG(params, 'info', textentry('40-001-00006'), printonly=printonly,
         logonly=logonly)
    WLOG(params, 'info', wmsgs, wrap=False, printonly=printonly,
         logonly=logonly)
    WLOG(params, '', params['DRS_HEADER'], printonly=printonly,
         logonly=logonly)


def _display_database_settings(params: ParamDict,
                               wmsgs: lang.Text) -> lang.Text:
    """
    Display database settings

    :param params: ParamDict, the parameter dictionary of constants
    :param wmsgs: the current lang.Text instance

    :return: lang.Text, the updated lang.Text instance
    """
    dparams = base.DPARAMS

    # -------------------------------------------------------------------------
    # SQLITE DISPLAY
    # -------------------------------------------------------------------------
    if dparams['USE_SQLITE3']:
        # get sub dictionary
        aparams = dparams['SQLITE3']
        # add database type
        wmsgs += textentry('\n\tDATABASE: SQLITE3')
        # loop around database names
        for dbname in base.DATABASE_NAMES:
            # get database key
            dbkey = dbname.upper()
            # get database path
            if aparams[dbkey]['PATH'] in params:
                path = params[aparams[dbkey]['PATH']]
            else:
                path = aparams[dbkey]['PATH']
            # construct full path to database
            fullpath = os.path.join(path, aparams[dbkey]['NAME'])
            # add to wmsgs
            dargs = [dbkey, fullpath]
            wmsgs += textentry('\n\tDATABASE-{0}: {1}'.format(*dargs))
    # -------------------------------------------------------------------------
    # MYSQL DISPLAY
    # -------------------------------------------------------------------------
    elif dparams['USE_MYSQL']:
        # get sub dictionary
        aparams = dparams['MYSQL']
        # add database type
        wmsgs += textentry('\n\tDATABASE: MYSQL')
        # loop around database names
        for dbname in base.DATABASE_NAMES:
            # get database key
            dbkey = dbname.upper()
            # construct table name
            tablename = '{0}_{1}_DB'.format(dbkey, aparams[dbkey]['PROFILE'])
            # add to wmsgs
            dargs = [dbkey, aparams['DATABASE'], aparams['HOST'],
                     tablename]
            wmsgs += textentry('\n\tDATABASE-{0}: {1}@{2}:{3}'.format(*dargs))
    # return lang.text updated (or not if no database was used)
    return wmsgs


def _display_system_info(params: ParamDict, logonly: bool = True,
                         return_message: bool = False
                         ) -> Union[textentry, str, None]:
    """
    Display system information via the WLOG command

    :param params: dictionary, parameter dictionary
    :param logonly: bool, if True will only display in the log (not to screen)
                    default=True, if False prints to both log and screen

    :param return_message: bool, if True returns the message to the call, if
                           False logs the message using WLOG

    :type params: ParamDict
    :type logonly: bool
    :type return_message: bool

    :returns: None, unless return_message = True, then returns the message
              string and does not print/log
    """
    # set function name
    _ = display_func('_display_system_info', __NAME__)
    # noinspection PyListCreation
    messages = ' ' + textentry('40-001-00010')
    messages += '\n' + textentry(params['DRS_HEADER'])
    # add version /python dist keys
    messages = _sort_version(messages)
    # add os keys
    messages += '\n' + textentry('40-001-00011', args=[sys.executable])
    messages += '\n' + textentry('40-001-00012', args=[sys.platform])

    messages += textentry(_display_python_modules())

    # add arguments (from sys.argv)
    messages += textentry('40-000-00018')
    for it, arg in enumerate(sys.argv):
        arg_msg = '\t Arg {0} = \'{1}\''.format(it + 1, arg)
        messages += '\n' + textentry(arg_msg)
    # add ending header
    messages += '\n' + textentry(params['DRS_HEADER'])
    if return_message:
        return messages
    else:
        WLOG(params, 'debug', messages, printonly=True)
        # return messages for logger
        WLOG(params, '', messages, logonly=logonly)


def _display_run_time_arguments(recipe, fkwargs=None, printonly=False,
                                logonly=False):
    """
    Display for arguments used (got from p['INPUT'])

    :param recipe: DrsRecipe instance
    :param fkwargs: dictionary or None, key/value pairs from run time call
                    if None does not use

    :type recipe: DrsRecipe
    :type fkwargs: dict

    :returns: None

    """
    # set function name
    _ = display_func('_display_run_time_arguments', __NAME__)
    # storage for logging strings
    log_strings = ''
    # get parameters
    params = recipe.params
    # get special keys
    skeys = _get_recipe_keys(recipe.specialargs, remove_prefix='-',
                             add=['--help', '-h'])
    pkeys = _keys_present(recipe, fkwargs, remove_prefix='-')
    # make keys upper case
    skeys = list(map(lambda x: x.upper(), skeys))
    pkeys = list(map(lambda x: x.upper(), pkeys))
    # loop around inputs
    for argname in params['INPUTS']:
        # if we have a special input ignore
        if argname in skeys:
            continue
        # if keys aren't present in sys.argv/fkwargs do not add them
        if argname not in pkeys:
            continue
        # get value of argument
        value = params['INPUTS'][argname]
        # value is either a list or a single value
        if type(value) not in [list, np.ndarray]:
            # generate this arguments log string
            log_string = '\n\t--{0}: {1}'.format(argname, str(value))
            log_strings += log_string
        # else we have a list
        else:
            # get value
            indexvalues = _get_arg_strval(value)
            # loop around index values
            for index, indexvalue in enumerate(indexvalues):
                # add to log strings
                largs = [argname, index, indexvalue]
                log_strings += '\n\t--{0}[{1}]: {2}'.format(*largs)
    # -------------------------------------------------------------------------
    # log to screen and log file
    if len(log_strings) > 0:
        WLOG(params, 'info', textentry('40-001-00017'), printonly=printonly,
             logonly=logonly)
        WLOG(params, 'info', textentry(log_strings), wrap=False,
             printonly=printonly, logonly=logonly)
        WLOG(params, '', textentry(params['DRS_HEADER']), printonly=printonly,
             logonly=logonly)


def _display_python_modules() -> str:
    """
    Print the current versions of the python modules (for logging only)
    (from requirements_current.txt)

    :return: string, a string representation of the python modules
    """

    # load user requirements
    packages, versions = np.loadtxt(base.RECOMM_USER, dtype=str,
                                    delimiter='==', unpack=True)
    # storage
    storage = textentry('40-000-00017')
    # loop around packages and get versions
    for p_it, package in enumerate(packages):
        try:
            with warnings.catch_warnings(record=True) as _:
                mod = importlib.import_module(package)
            # if we have version for module
            if hasattr(mod, '__version__'):
                # get current version
                version = mod.__version__
                # get required version
                rversion = versions[p_it]
                # add to string storage (for return)
                pargs = [package, version, rversion]
                storage += '\n\t{0}: {1}  (req: {2})'.format(*pargs)
        except Exception as _:
            continue

    # return string
    return storage


# =============================================================================
# Exit functions
# =============================================================================
def _find_interactive() -> bool:
    """
    Find whether user is using an interactive session

    i.e. True if:
        ipython code.py
        ipython >> run code.py
        python -i code.py

    False if
        python code.py
        code.py

    Note cannot distinguish between ipython from shell (so assumed interactive)

    :return: True if interactive
    :rtype: bool
    """
    # set function name
    _ = display_func('_find_interactive', __NAME__)
    # if system flags this as an interactive session
    cond1 = sys.flags.interactive
    # if sys has ps1 as an attribute
    cond2 = hasattr(sys, 'ps1')
    # if sys.stdderr.isatty = False
    cond3 = not sys.stderr.isatty()
    # if any of these are True we have an interactive session
    return cond1 or cond2 or cond3


# noinspection PyUnresolvedReferences
def _find_ipython() -> bool:
    """
    Find whether user is using ipython or python

    :return: True if using ipython, false otherwise
    :rtype: bool
    """
    # set function name
    _ = display_func('_find_ipython', __NAME__)
    # see if we are in ipython
    try:
        # noinspection PyStatementEffect
        __IPYTHON__  # Note python wont define this, ipython will
        return True
    except NameError:
        return False


# =============================================================================
# Worker functions
# =============================================================================
def _update_input_params(params, args):
    # loop around arguments
    for argname in args:
        # if argument isn't in params['INPUTS'] we don't need to worry about it
        if argname in params['INPUTS']:
            # get arg instance from args
            arg = args[argname]
            # we only need to update file arguments
            if arg.dtype not in ['file', 'files']:
                continue
            # only update for Drs input file instances
            if isinstance(arg, DrsInputFile):
                # get params file instances (DrsInputFile)
                pargs = params['INPUTS'][argname][1]
                # loop around file instances and update params witha copy
                for parg in pargs:
                    # update params
                    pargs[parg].params = params.copy()


def _assign_pid() -> Tuple[str, str]:
    """
    Assign a process id based on the time now and return it and the
    time now

    :return: the process id and the human time at creation
    :rtype: Tuple[str, str]
    """
    # set function name
    _ = display_func('_assign_pid', __NAME__)
    # get unix char code
    unixtime, humantime, rval = drs_misc.unix_char_code()
    # write pid
    pid = 'PID-{0:020d}-{1}'.format(int(unixtime), rval)
    # return pid and human time
    return pid, humantime


def find_recipe(name: str = 'None', instrument: str = 'None',
                mod: Union[base_class.ImportModule, None] = None
                ) -> Tuple[DrsRecipe, Union[base_class.ImportModule, None]]:
    """
    Finds a given recipe in the instruments definitions

    :param name: string, the recipe name
    :param instrument: string, the instrument name
    :param mod:

    :type name: str
    :type instrument: str

    :exception SystemExit: on caught errors

    :returns: if found the DrsRecipe and the import module for recipe
              definitions, else raises SystemExit or returns empty recipe and
              None for the mod

    :rtype: DrsRecipe and the ImportModule class for recipe definitions
    """
    # set function name
    func_name = display_func('find_recipe', __NAME__)
    # deal with no instrument
    if instrument == 'None' or instrument is None:
        ipath = CORE_PATH
        instrument = None
    else:
        ipath = INSTRUMENT_PATH
    # deal with no name or no instrument
    if name == 'None' or name is None:
        empty = drs_recipe.DrsRecipe(name='Empty', instrument=instrument)
        return empty, None
    # deal with needing to get mod
    if isinstance(mod, base_class.ImportModule):
        mod = mod.get()
    # else we have a name and an instrument
    if mod is None:
        margs = [instrument, ['recipe_definitions.py'], ipath, CORE_PATH]
        modules = constants.getmodnames(*margs, return_paths=False)
        # load module
        mod = constants.import_module(func_name, modules[0], full=True)
    # get a list of all recipes from modules
    all_recipes = mod.recipes
    # try to locate this recipe
    found_recipe = None
    for recipe in all_recipes:
        if recipe.name == name:
            found_recipe = recipe
        elif recipe.name + '.py' == name:
            found_recipe = recipe
        elif recipe.name.strip('.py') == name:
            found_recipe = recipe

    if instrument is None and found_recipe is None:
        empty = drs_recipe.DrsRecipe(name='Empty', instrument='None')
        return empty, None
    if found_recipe is None:
        # may not have access to this
        # TODO: is this needed?
        try:
            WLOG(None, 'error', textentry('00-007-00001', args=[name]))
        except Exception as _:
            raise DrsCodedException('00-007-00001', 'error', targs=[name],
                                    func_name=func_name)
    # make a copy of found recipe to return
    copy_recipe = DrsRecipe()
    copy_recipe.copy(found_recipe)
    # return
    return copy_recipe, mod


def _get_arg_strval(value: Any):
    """
    Get the string value representation of "value" (specifically for a listof
    DrsFitsFiles)

    :param value: object, the value to be printed
    :return out: string, the string representation of "object"
    """
    # set function name
    _ = display_func('_get_arg_strval', __NAME__)
    # if we done have list return value
    if not hasattr(value, '__len__'):
        return value

    # if list is empty --> return
    if len(value) == 0:
        return value

    # if we don't have a list of lists --> 1D array --> return
    if len(value) == 1:
        return value
    # if not a list of numpy array return value 1
    if type(value[1]) not in [list, np.ndarray]:
        return value

    # if we have a list of list we may have a DrsFile return
    if isinstance(value[1][0], DrsFitsFile):
        out = []
        for it in range(len(value[0])):
            filename = os.path.basename(value[0][it])
            kind = value[1][it].name
            out.append('[{0}] {1}'.format(kind, filename))
        return out
    elif isinstance(value[1][0], DrsInputFile):
        out = []
        for it in range(len(value[0])):
            filename = os.path.basename(value[0][it])
            kind = value[1][it].name
            out.append('[{0}] {1}'.format(kind, filename))
        return out
    else:
        return []


def _get_recipe_keys(args: Dict[str, drs_argument.DrsArgument],
                     remove_prefix: Union[str, None] = None,
                     add: Union[List[str], None] = None,
                     allow_skips: bool = True) -> List[str]:
    """
    Obtain the recipe keys from reipce "args"

    :param args: Dictionary containing key, value pairs where keys are the
                 argument names and values are instances of DrsArgument
    :param remove_prefix: string or None, a prefix to remove from keys if None
                          removes nothing
    :param add: list of strings or None, if not None each string is added to
                output "keys" as additional extra keys to check
    :param allow_skips: bool, if True allows special args to skip, if False
                        does not skip any special args

    :return keys: list of strings, the defined recipe keys (may be stipped of
                  a prefix if remove_prefix is not None)
    """
    # set function name
    _ = display_func('_get_recipe_keys', __NAME__)
    # get the special keys
    keys = []
    # loop around arguments in args (positional, optional or special)
    for argname in args:
        arg = args[argname]
        # deal with skips (skips should not be added to keys here - unless
        #   allow_skips is set to False)
        if allow_skips and arg.kind == 'special':
            if arg.skip:
                keys += arg.names
        else:
            keys += arg.names

    # add additional keys (manually)
    if add is not None:
        keys += add
    # deal with removing prefixes
    if remove_prefix is not None:
        # set up storage
        old_keys = list(keys)
        keys = []
        for key in old_keys:
            # remove prefix
            while key[0] == remove_prefix:
                key = key[1:]
            # append to skeys
            keys.append(key)
    # return keys
    return keys


def _keys_present(recipe: DrsRecipe,
                  fkwargs: Union[Dict[str, Any], None] = None,
                  remove_prefix: Union[str, None] = None) -> List[str]:
    """
    Returns a list of keys present in argument parsing (i.e. from sys.argv/or
    "fkwargs" - that is from call to function)

    :param recipe: DrsRecipe instance
    :param fkwargs: dictionary or None, the call dictionary to search (as well
                    as sys.argv)
    :param remove_prefix: string or None, a prefix to remove from keys if None
                          removes nothing
    :return keys: list of strings, the present keys (may be stipped of a prefix
                  if remove_prefix is not None)
    """
    # set function name
    _ = display_func('_keys_present', __NAME__)
    # deal with no fkwargs
    if fkwargs is None:
        fkwargs = dict()
    # get they keys to check for
    arg_keys = _get_recipe_keys(recipe.args)
    kwarg_keys = _get_recipe_keys(recipe.kwargs, remove_prefix='-')
    skeys = _get_recipe_keys(recipe.specialargs, add=['--help', '-h'],
                             allow_skips=False, remove_prefix='-')

    # need all positional keys
    keys = arg_keys
    # search for optional/special keys
    search_keys = kwarg_keys + skeys
    if len(search_keys) > 0:
        for search_key in search_keys:
            if _search_for_key(search_key, fkwargs):
                keys.append(search_key)
    # deal with removing prefixes
    if remove_prefix is not None:
        # set up storage
        old_keys = list(keys)
        keys = []
        for key in old_keys:
            # remove prefix
            while key[0] == remove_prefix:
                key = key[1:]
            # append to skeys
            keys.append(key)
    # return found keys
    return keys


def _search_for_key(key: str,
                    fkwargs: Union[Dict[str, Any], None] = None) -> bool:
    """
    Search for a key in sys.argv (list of strings) and fkwargs (dictionary)
    in order to quickly tell if key was present when parsing arguments

    :param key: string, the key to look for
    :param fkwargs: dictionary or None, contains keywords from call

    :return cond: bool, True if key found in fkwargs/sys.argv, False otherwise
    """
    # set function name
    _ = display_func('_search_for_key', __NAME__)
    # deal with no fkwargs
    if fkwargs is None:
        fkwargs = dict()
    # search in fkwargs
    cond1 = key in fkwargs.keys()
    # search in sys.argv list of strings
    cond2 = False
    for argv in sys.argv:
        if key == argv.split('=')[0].replace('-', ''):
            cond2 = True
    # return True if found and False otherwise
    if cond1 | cond2:
        return True
    else:
        return False


def _set_debug_from_input(recipe: DrsRecipe,
                          fkwargs: Union[Dict[str, Any], None] = None
                          ) -> DrsRecipe:
    """
    Set the debug parameter by searching fkwargs (from function call) and/or
    sys.argv (user input) looking for --debug.
    Updates recipe.params['DRS_DEBUG']

    :param recipe: DrsRecipe instance
    :param fkwargs: dictionary: keys to check from function call
    :type recipe: DrsRecipe
    :type fkwargs: dict

    :returns: the DrsRecipe with updated parameter dictionary
    :rtype: DrsRecipe
    """
    # set function name
    func_name = display_func('_set_debug_from_input', __NAME__)
    # set debug key
    debug_key = '--debug'
    # assume debug is not there
    debug_mode = None
    pos = None
    # check sys.argv
    for it, arg in enumerate(sys.argv):
        if debug_key in arg:
            if '=' in arg:
                pos = None
                debug_mode = arg.split('=')[-1]
            else:
                pos = it
                debug_mode = None
    # deal with position
    if pos is None:
        pass
    elif (pos + 1) == len(sys.argv):
        debug_mode = 0
    elif pos is not None:
        debug_mode = sys.argv[pos + 1]

    # check fkwargs
    for kwarg in fkwargs:
        if 'debug' in kwarg:
            debug_mode = fkwargs[kwarg]
    # try to find value of debug mode
    if debug_mode is not None:
        try:
            debug_mode = int(debug_mode)
        except ValueError:
            debug_mode = 1
        except TypeError:
            debug_mode = 1
    # set DRS_DEBUG
    if debug_mode is not None:
        # set the drs debug level to 1
        recipe.params['DRS_DEBUG'] = debug_mode
        recipe.params.set_source('DRS_DEBUG', func_name)
    # return recipe
    return recipe


def _set_obsdir_from_input(recipe: DrsRecipe,
                           fkwargs: Union[Dict[str, Any], None] = None
                           ) -> DrsRecipe:
    """
    Get observation directory from inputs
    """
    # set function name
    func_name = display_func('_set_obsdir_from_input', __NAME__)
    # set default value for obs_dir (blank string)
    obs_dir = ''
    check = True
    # -------------------------------------------------------------------------
    # check in fkwargs
    if check and ('obs_dir' in fkwargs):
        value = fkwargs['obs_dir']
        if not drs_text.null_text(value, ['None', '', 'Null']):
            obs_dir = str(value)
            check = False
    # -------------------------------------------------------------------------
    # check in args
    if check and ('obs_dir' in recipe.args):
        try:
            # get position of obs_dir in arguments
            pos = int(recipe.args['obs_dir'].pos) + 1
            # get obs_dir from sys.argv
            if len(sys.argv) >= pos:
                obs_dir = sys.argv[pos]
        except Exception as _:
            pass
    # -------------------------------------------------------------------------
    # check keywords
    if check and ('obs_dir' in recipe.kwargs):
        # set debug key
        key = '--obs_dir'
        # assume debug is not there
        value = None
        pos = None
        # check sys.argv
        for it, arg in enumerate(sys.argv):
            if key in arg:
                if '=' in arg:
                    pos = None
                    value = arg.split('=')[-1]
                else:
                    pos = it
                    value = None
        # deal with position
        if pos is not None:
            value = sys.argv[pos + 1]
        # set to obs_dir only if not None
        if value is not None:
            obs_dir = str(value)
    # -------------------------------------------------------------------------
    # make sure obs dir is not a full path
    obs_subdir, stripped = drs_file.DrsPath.strip_path(recipe.params, obs_dir)
    if not stripped:
        obs_subdir = os.path.basename(obs_dir)
    # deal with no sub dir
    if len(obs_subdir) == 0:
        obs_subdir = 'other'
    # -------------------------------------------------------------------------
    # deal with having a obs_dir set
    recipe.params['OBS_SUBDIR'] = obs_subdir
    # set source
    recipe.params.set_sources(['OBS_SUBDIR'], func_name)
    # return recipe
    return recipe


def _set_force_dirs(recipe: DrsRecipe,
                    fkwargs: Union[Dict[str, Any], None] = None) -> DrsRecipe:
    """
    Decides whether we need to force the input and outdir based on user inputs

    :param recipe: DrsRecipe instance
    :param fkwargs: dictionary: keys to check from function call
    :return:
    """
    # set function name
    _ = display_func('_set_force_dirs', __NAME__)
    # ----------------------------------------------------------------------
    # set debug key
    in_block_key = '--force_indir'
    # assume debug is not there
    in_block_str = None
    pos = None
    # check sys.argv
    for it, arg in enumerate(sys.argv):
        if in_block_key in arg:
            if '=' in arg:
                pos = None
                in_block_str = arg.split('=')[-1]
                # Setting {0}={1} from sys.argv[{2}] ({3})
                dargs = ['recipe.inputdir', in_block_str, in_block_key, '=']
                dmsg = textentry('90-008-00013', args=dargs)
                WLOG(recipe.params, 'debug', dmsg)
            else:
                pos = it
                in_block_str = None
    # deal with position
    if pos is None:
        pass
    elif pos is not None:
        in_block_str = sys.argv[pos + 1]
        # Setting {0}={1} from sys.argv[{2}] ({3})
        dargs = ['recipe.inputdir', in_block_str, in_block_key, 'white-space']
        dmsg = textentry('90-008-00013', args=dargs)
        WLOG(recipe.params, 'debug', dmsg)
    # check fkwargs
    for kwarg in fkwargs:
        if 'force_indir' in kwarg:
            in_block_str = fkwargs[kwarg]
            # Setting {0}={1} from fkwargs[{2}]
            dargs = ['recipe.inputdir', in_block_str, kwarg]
            dmsg = textentry('90-008-00014', args=dargs)
            WLOG(recipe.params, 'debug', dmsg)
    # ----------------------------------------------------------------------
    # set recipe.inputdir
    if in_block_str is not None:
        # get block names
        block_names = drs_file.DrsPath.get_block_names(params=recipe.params)
        # must check that block str is not a block kind
        if in_block_str not in block_names:
            # only set this if block str is an actual path
            if os.path.exists(os.path.abspath(in_block_str)):
                in_block_str = os.path.abspath(in_block_str)
            # set the input dir
            recipe.inputdir = drs_file.DrsPath(recipe.params,
                                               block_path=in_block_str)
            # update the in block kind str
            recipe.in_block_str = recipe.inputdir.block_kind
        # else set the recipe in_block_str to the block defined in in_block_str
        else:
            # set the input dir
            recipe.inputdir = drs_file.DrsPath(recipe.params,
                                               block_kind=in_block_str)
            # update the in block kind str
            recipe.in_block_str = recipe.inputdir.block_kind
    # ----------------------------------------------------------------------
    # set debug key
    out_block_key = '--force_outdir'
    # assume debug is not there
    out_block_str = None
    pos = None
    # check sys.argv
    for it, arg in enumerate(sys.argv):
        if out_block_key in arg:
            if '=' in arg:
                pos = None
                out_block_str = arg.split('=')[-1]
                # Setting {0}={1} from sys.argv[{2}] ({3})
                dargs = ['recipe.outputdir', out_block_str, out_block_key, '=']
                dmsg = textentry('90-008-00013', args=dargs)
                WLOG(recipe.params, 'debug', dmsg)
            else:
                pos = it
                out_block_str = None
    # deal with position
    if pos is None:
        pass
    elif pos is not None:
        out_block_str = sys.argv[pos + 1]
        # Setting {0}={1} from sys.argv[{2}] ({3})
        dargs = ['recipe.outputdir', out_block_str, out_block_key,
                 'white-space']
        dmsg = textentry('90-008-00013', args=dargs)
        WLOG(recipe.params, 'debug', dmsg)
    # check fkwargs
    for kwarg in fkwargs:
        if 'force_outdir' in kwarg:
            out_block_str = fkwargs[kwarg]
            # Setting {0}={1} from fkwargs[{2}]
            dargs = ['recipe.outputdir', out_block_str, kwarg]
            dmsg = textentry('90-008-00014', args=dargs)
            WLOG(recipe.params, 'debug', dmsg)
    # set recipe.outputdir
    if out_block_str is not None:
        if os.path.exists(os.path.abspath(out_block_str)):
            out_block_str = os.path.abspath(out_block_str)
        # set the output dir instance
        recipe.outputdir = drs_file.DrsPath(recipe.params,
                                            block_kind=out_block_str)
        # update the out block kind str
        recipe.out_block_str = recipe.outputdir.block_kind
    # ----------------------------------------------------------------------
    # return recipe
    return recipe


def _sort_version(messages: Union[str, None] = None) -> Union[List[str]]:
    """
    Obtain and sort version info

    :param messages: list of strings or None, if defined is a
                     list of messages that version_info is added to, else new
                     list of strings is created

    :return messages: list of strings updated or created
                      (if messages is None)
    """
    # set function name
    _ = display_func('_sort_version', __NAME__)
    # deal with no messages
    if messages is None:
        messages = []
    # get version info
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro

    version = '{0}.{1}.{2}'.format(major, minor, micro)

    # add version info to messages
    messages += '\n' + textentry('40-001-00013', args=[version])

    # add distribution if possible
    try:
        build = sys.version.split('|')[1].strip()
        messages += '\n' + textentry('40-001-00014', args=[build])
    except IndexError:
        pass

    # add date information if possible
    try:
        date = sys.version.split('(')[1].split(')')[0].strip()
        messages += '\n' + textentry('40-001-00015', args=[date])
    except IndexError:
        pass

    # add Other info information if possible
    try:
        other = sys.version.split('[')[1].split(']')[0].strip()
        messages += '\n' + textentry('40-001-00016', args=[other])
    except IndexError:
        pass

    # return updated messages
    return messages


def _make_dirs(params: ParamDict, path: str):
    """
    Check and if it doesn't exist make the directory 'path'
    (locking path as necessary)

    :param params: ParamDict, parameter dictionary of constants
    :param path: str, the path to check and make

    :return: None
    """
    # set function name
    _ = display_func('_make_dirs', __NAME__)
    # first check if path already exists
    if os.path.exists(path):
        # return
        return
    # ----------------------------------------------------------------------
    # make sure that directory exists in path
    if not os.path.exists(os.path.dirname(path)):
        _make_dirs(params, os.path.dirname(path))
    # ----------------------------------------------------------------------
    # define a synchoronized lock for indexing (so multiple instances do not
    #  run at the same time)
    lockfile = os.path.basename(path)
    # start a lock
    lock = drs_lock.Lock(params, lockfile)

    # make locked makedirs function
    @drs_lock.synchronized(lock, params['PID'] + lockfile)
    def locked_makedirs():
        # check again path already exists
        if os.path.exists(path):
            return
        # log making directory
        WLOG(params, '', textentry('40-001-00023', args=[path]))
        # make directory
        try:
            os.makedirs(path)
        except Exception as e_:
            # log error
            string_trackback = traceback.format_exc()
            emsg = textentry('01-000-00001', args=[path, type(e_)])
            emsg += '\n\n' + textentry(string_trackback)
            WLOG(params, 'error', emsg, raise_exception=True, wrap=False)
    # -------------------------------------------------------------------------
    # try to run locked makedirs
    try:
        locked_makedirs()
    except KeyboardInterrupt as e:
        lock.reset()
        raise e
    except Exception as e:
        # reset lock
        lock.reset()
        raise e


# =============================================================================
# End of code
# =============================================================================
