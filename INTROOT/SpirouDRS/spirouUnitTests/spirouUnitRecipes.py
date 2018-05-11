#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recipe identities to run unit tests.

Each recipe identities should start with "unit_test_" followed by the full
recipe name (without the .py extension)

Each recipe identity should return a list of sorted arguments (Ready for the
recipe call) and the expected output filenames of each recipe

Created on 2018-05-01 at 13:06

@author: cook
"""
from __future__ import division

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

import cal_BADPIX_spirou
import cal_CCF_E2DS_spirou
import cal_DARK_spirou
import cal_DRIFT_RAW_spirou
import cal_DRIFT_E2DS_spirou
import cal_DRIFTPEAK_E2DS_spirou
import cal_extract_RAW_spirou
import cal_extract_RAW_spirouAB
import cal_extract_RAW_spirouC
import cal_FF_RAW_spirou
import cal_HC_E2DS_spirou
import cal_loc_RAW_spirou
import cal_SLIT_spirou


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouUnitTests.unit_test_functions.py'
# get constants file
Constants = spirouConfig.Constants
# Get version and author
__version__ = Constants.VERSION()
__author__ = Constants.AUTHORS()
__date__ = Constants.LATEST_EDIT()
__release__ = Constants.RELEASE()
# Get Logging function
WLOG = spirouCore.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# define valid recipes
VALID_RECIPES = ['cal_BADPIX_spirou',
                 'cal_CCF_E2DS_spirou',
                 'cal_DARK_spirou',
                 'cal_DRIFT_RAW_spirou',
                 'cal_DRIFT_E2DS_spirou',
                 'cal_DRIFTPEAK_E2DS_spirou',
                 'cal_extract_RAW_spirou',
                 'cal_extract_RAW_spirouAB',
                 'cal_extract_RAW_spirouC',
                 'cal_FF_RAW_spirou',
                 'cal_HC_E2DS_spirou',
                 'cal_loc_RAW_spirou',
                 'cal_SLIT_spirou']


# =============================================================================
# Define functions
# =============================================================================
def get_versions():
    # aliases
    cdriftpeak = cal_DRIFTPEAK_E2DS_spirou
    # get versions
    vv = dict()
    vv[cal_BADPIX_spirou.__NAME__] = cal_BADPIX_spirou.__version__
    vv[cal_CCF_E2DS_spirou.__NAME__] = cal_CCF_E2DS_spirou.__version__
    vv[cal_DARK_spirou.__NAME__] = cal_DARK_spirou.__version__
    vv[cal_DRIFT_RAW_spirou.__NAME__] = cal_DRIFT_RAW_spirou.__version__
    vv[cal_DRIFT_E2DS_spirou.__NAME__] = cal_DRIFT_E2DS_spirou.__version__
    vv[cdriftpeak.__NAME__] = cdriftpeak.__version__
    vv[cal_extract_RAW_spirou.__NAME__] = cal_extract_RAW_spirou.__version__
    vv[cal_extract_RAW_spirouAB.__NAME__] = cal_extract_RAW_spirouAB.__version__
    vv[cal_extract_RAW_spirouC.__NAME__] = cal_extract_RAW_spirouC.__version__
    vv[cal_FF_RAW_spirou.__NAME__] = cal_FF_RAW_spirou.__version__
    vv[cal_HC_E2DS_spirou.__NAME__] = cal_HC_E2DS_spirou.__version__
    vv[cal_loc_RAW_spirou.__NAME__] = cal_loc_RAW_spirou.__version__
    vv[cal_SLIT_spirou.__NAME__] = cal_SLIT_spirou.__version__


def wrapper(p, rname, inputs=None, outputs=None):
    # get name of run (should be first element in run list
    name = inputs[0]
    if name not in VALID_RECIPES:
        emsg1 = "{0} is not a valid DRS recipe".format(name)
        emsg2 = "    run = {0}".format(rname)
        WLOG('error', p['LOG_OPT'], [emsg1, emsg2])
    # deal with no input or outputs
    if inputs is None and outputs is None:
        WLOG('error', p['LOG_OPT'], 'Must define inputs')
    # if we don't have outputs then we require inputs only
    strarg = 'rname, inputs, outputs'
    # link to the recipe function
    recipe_function = 'unit_test_{0}({1})'.format(name.lower(), strarg)
    # return the evaulated unit test function
    try:
        varbs, name = eval(recipe_function)
    except NameError:
        WLOG('error', p['LOG_OPT'], 'Cannot run {0}'.format(recipe_function))
        varbs = []
    # return recipe inputs (or outputs)
    return varbs, name


def run_main(p, name, args):
    # set the program name
    command = '{0}.main(**args)'.format(name)
    ll = eval(command)
    # return locals
    return ll


def unit_test_cal_badpix_spirou(rname, inputs, outputs=None):

    """
    cal_BADPIX_spirou

    input = night_name [flat_flat_*.fits] [dark_dark_*.fits]
    output = BADPIX_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_BADPIX_spirou'
    arg_names = ['night_name', 'flatfile', 'darkfile']
    arg_types = [str, str, str]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = [Constants.BADPIX_FILE(outputs['p'])]
        # return outs
        return outs, name


def unit_test_cal_dark_spirou(rname, inputs, outputs=None):

    """
    cal_DARK_spirou

    input = night_name files
    output = DARK_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_DARK_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = [Constants.DARK_FILE(outputs['p'])]
        # return outs
        return outs, name


def unit_test_cal_loc_raw_spirou(rname, inputs, outputs=None):

    """
    unit_test_cal_loc_raw_spirou

    input = night_name files
    output = LOC_ORDER_PROFILE_FILE, LOC_LOCO_FILE, LOC_LOCO_FILE2,
             LOC_LOCO_FILE3

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_loc_RAW_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = [Constants.LOC_ORDER_PROFILE_FILE(outputs['p']),
                Constants.LOC_LOCO_FILE(outputs['p']),
                Constants.LOC_LOCO_FILE2(outputs['p']),
                Constants.LOC_LOCO_FILE3(outputs['p'])]
        # return outs
        return outs, name


def unit_test_cal_slit_spirou(rname, inputs, outputs=None):
    """
    unit_test_cal_slit_spirou

    input = night_name files
    output = SLIT_TILT_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_SLIT_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = [Constants.SLIT_TILT_FILE(outputs['p'])]
        # return outs
        return outs, name


def unit_test_cal_ff_raw_spirou(rname, inputs, outputs=None):
    """
    unit_test_cal_ff_raw_spirou

    input = night_name files
    output = FF_BLAZE_FILE, FF_FLAT_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_FF_RAW_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = []
        for fiber in outputs['p']['fib_type']:
            outs.append(Constants.FF_BLAZE_FILE(outputs['p'], fiber))
            outs.append(Constants.FF_FLAT_FILE(outputs['p'], fiber))
        # return outs
        return outs, name


def unit_test_cal_extract_raw_spirou(rname, inputs, outputs=None):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_extract_RAW_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = []
        for fiber in outputs['p']['fib_type']:
            outs.append(Constants.EXTRACT_E2DS_FILE(outputs['p'], fiber))
            outs.append(Constants.EXTRACT_E2DS_ALL_FILES(outputs['p'], fiber))
        # return outs
        return outs, name


def unit_test_cal_extract_raw_spirouab(rname, inputs, outputs=None):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_extract_RAW_spirouAB'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args =  get_args(name, rname, inputs, arg_names, arg_types)
        # return args
        return args, name
    # else define the outputs
    else:
        outs = []
        for fiber in outputs['p']['fib_type']:
            outs.append(Constants.EXTRACT_E2DS_FILE(outputs['p'], fiber))
            outs.append(Constants.EXTRACT_E2DS_ALL_FILES(outputs['p'], fiber))
        # return outs
        return outs, name


def unit_test_cal_extract_raw_spirouc(rname, inputs, outputs=None):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_extract_RAW_spirouC'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args =  get_args(name, rname, inputs, arg_names, arg_types)
        # return args
        return args, name
    # else define the outputs
    else:
        outs = []
        for fiber in outputs['p']['fib_type']:
            outs.append(Constants.EXTRACT_E2DS_FILE(outputs['p'], fiber))
            outs.append(Constants.EXTRACT_E2DS_ALL_FILES(outputs['p'], fiber))
        # return outs
        return outs, name


def unit_test_cal_drift_raw_spirou(rname, inputs, outputs=None):
    """
    unit_test_cal_drift_raw_spirou

    input = night_name files
    output = DRIFT_RAW_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_DRIFT_RAW_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, str]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = [Constants.DRIFT_RAW_FILE(outputs['p'])]
        # return outs
        return outs, name


def unit_test_cal_drift_e2ds_spirou(rname, inputs, outputs=None):
    """
    unit_test_cal_drift_e2ds_spirou

    input = night_name files
    output = DRIFT_E2DS_FITS_FILE, DRIFT_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_DRIFT_E2DS_spirou'
    arg_names = ['night_name', 'reffile']
    arg_types = [str, str]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = [Constants.DRIFT_E2DS_FITS_FILE(outputs['p']),
                Constants.DRIFT_E2DS_TBL_FILE(outputs['p'])]
        # return outs
        return outs, name


def unit_test_cal_driftpeak_e2ds_spirou(rname, inputs, outputs=None):
    """
    unit_test_cal_driftpeak_e2ds_spirou

    input = night_name files
    output = DRIFTPEAK_E2DS_FITS_FILE, DRIFTPEAK_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_DRIFTPEAK_E2DS_spirou'
    arg_names = ['night_name', 'reffile']
    arg_types = [str, str]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = [Constants.DRIFTPEAK_E2DS_FITS_FILE(outputs['p']),
                Constants.DRIFTPEAK_E2DS_TBL_FILE(outputs['p'])]
        # return outs
        return outs, name


def unit_test_cal_ccf_e2ds_spirou(rname, inputs, outputs=None):
    """
    unit_test_cal_ccf_e2ds_spirou

    input = night_name files
    output = DRIFTPEAK_E2DS_FITS_FILE, DRIFTPEAK_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file
    :param outputs: dictionary or None, output of code - locals() if not None
                    returns output filenames

    if outputs is None:
        :return args: dict, the parameters to pass to the run
    else:
        :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'cal_CCF_E2DS_spirou'
    arg_names = ['night_name', 'e2dsfile', 'mask', 'rv', 'width', 'step']
    arg_types = [str, str, str, float, int, float]

    # get the inputs (if outputs is None)
    if outputs is None:
        # get arguments
        args = get_args(name, rname, inputs, arg_names, arg_types)
        return args, name
    # else define the outputs
    else:
        outs = [Constants.CCF_FITS_FILE(outputs['p']),
                Constants.CCF_TABLE_FILE(outputs['p'])]
        # return outs
        return outs, name


def get_args(name, rname, iargs, arg_names, arg_types):

    # we should at least have enough inputs for the arg names given
    if len(iargs) < (len(arg_names) + 1):
        emsg1 = '{0} has invalid number of arguments for {1}'
        eargs = [len(arg_names), len(iargs)]
        emsg2 = '   expected (at least) {0} got {1}'.format(*eargs)
        WLOG('error', DPROG, [emsg1.format(rname, name), emsg2])
    # set up storage
    args = dict()
    # set up counter
    pos = 0
    # loop around
    while pos < len(arg_names):
        # get the argument name
        arg_name = arg_names[pos]
        # get the value
        value = iargs[pos + 1]

        # check type and set
        if type(value) == arg_types[pos]:
            args[arg_name] = value
        elif (arg_types[pos] == list) and type(value) == str:
            args[arg_name] = [value]
        else:
            try:
                value = arg_types[pos](value)
                args[arg_name] = value
            except ValueError:
                eargs = [rname, pos, arg_name, arg_types[pos]]
                emsg1 = '{0}: Argument {1} ({2}) should be type={3}'
                emsg2 = '    got type={0}'.format(type(value))
                WLOG('error', DPROG, [emsg1.format(*eargs), emsg2])
        # add to counter
        pos += 1
    # deal with the fact we may have more arguments than arg_names
    if len(iargs) > (len(arg_names) + 1):
        if arg_types[pos - 1] == list:
            # find the last value added to arg_names
            end_argument = args[arg_names[pos - 1]]
            # add the remaining arguments to this argument
            for it in range(pos, len(iargs)):
                end_argument.append(iargs[it])
            # set the last argument to the end argument list
            args[arg_names[pos - 1]] = end_argument
    # return args
    return args


# =============================================================================
# End of code
# =============================================================================
