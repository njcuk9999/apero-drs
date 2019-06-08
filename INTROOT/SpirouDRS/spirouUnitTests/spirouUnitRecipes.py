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
import numpy as np
import sys
from collections import OrderedDict

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore

import cal_BADPIX_spirou
import cal_CCF_E2DS_spirou
import cal_DARK_spirou
import cal_DRIFT_E2DS_spirou
import cal_DRIFTPEAK_E2DS_spirou
import cal_DRIFTCCF_E2DS_spirou
import cal_exposure_meter
import cal_wave_mapper
import cal_extract_RAW_spirou
import cal_FF_RAW_spirou
import cal_HC_E2DS_EA_spirou
import cal_loc_RAW_spirou
import cal_SLIT_spirou
import cal_shape_spirou
import cal_WAVE_E2DS_EA_spirou
import cal_preprocess_spirou
import off_listing_RAW_spirou
import off_listing_REDUC_spirou
import obj_mk_tellu
import obj_mk_tellu_db
import obj_fit_tellu
import obj_fit_tellu_db
import obj_mk_obj_template
import visu_RAW_spirou
import visu_E2DS_spirou
import pol_spirou


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
# define valid recipes
VALID_RECIPES = ['cal_BADPIX_spirou',
                 'cal_CCF_E2DS_spirou',
                 'cal_DARK_spirou',
                 'cal_DRIFT_E2DS_spirou',
                 'cal_DRIFTPEAK_E2DS_spirou',
                 'cal_DRIFTCCF_E2DS_spirou',
                 'cal_exposure_meter',
                 'cal_wave_mapper',
                 'cal_extract_RAW_spirou',
                 'cal_FF_RAW_spirou',
                 'cal_HC_E2DS_spirou',
                 'cal_HC_E2DS_EA_spirou',
                 'cal_loc_RAW_spirou',
                 'cal_SLIT_spirou',
                 'cal_shape_spirou',
                 'cal_WAVE_E2DS_spirou',
                 'cal_WAVE_E2DS_EA_spirou',
                 'cal_WAVE_NEW_E2DS_spirou',
                 'cal_preprocess_spirou',
                 'off_listing_RAW_spirou',
                 'off_listing_REDUC_spirou',
                 'obj_mk_obj_template',
                 'obj_mk_tellu',
                 'obj_fit_tellu',
                 'obj_fit_tellu_db',
                 'obj_mk_tellu_db',
                 'obj_mk_obj_template',
                 'visu_RAW_spirou',
                 'visu_E2DS_spirou',
                 'pol_spirou']
# string type (as sometimes we have weird numpy strings
if sys.version_info.major > 2:
    PYTHON_STRINGS = [str, np.str_, np.str, np.str0]
else:
    PYTHON_STRINGS = [str, np.str_, np.str]


# =============================================================================
# Define functions
# =============================================================================
def get_versions():
    # aliases
    cdriftpeak = cal_DRIFTPEAK_E2DS_spirou
    # get versions
    vv = OrderedDict()
    vv[cal_BADPIX_spirou.__NAME__] = cal_BADPIX_spirou.__version__
    vv[cal_CCF_E2DS_spirou.__NAME__] = cal_CCF_E2DS_spirou.__version__
    vv[cal_DARK_spirou.__NAME__] = cal_DARK_spirou.__version__
    vv[cal_DRIFT_E2DS_spirou.__NAME__] = cal_DRIFT_E2DS_spirou.__version__
    vv[cdriftpeak.__NAME__] = cdriftpeak.__version__
    vv[cal_DRIFTCCF_E2DS_spirou.__NAME__] = cal_DRIFTCCF_E2DS_spirou.__version__
    vv[cal_exposure_meter.__NAME__] = cal_exposure_meter.__version__
    vv[cal_wave_mapper.__NAME__] = cal_wave_mapper.__version__
    vv[cal_extract_RAW_spirou.__NAME__] = cal_extract_RAW_spirou.__version__
    vv[cal_FF_RAW_spirou.__NAME__] = cal_FF_RAW_spirou.__version__
    # vv[cal_HC_E2DS_spirou.__NAME__] = cal_HC_E2DS_spirou.__version__
    vv[cal_HC_E2DS_EA_spirou.__NAME__] = cal_HC_E2DS_EA_spirou.__version__
    vv[cal_loc_RAW_spirou.__NAME__] = cal_loc_RAW_spirou.__version__
    vv[cal_SLIT_spirou.__NAME__] = cal_SLIT_spirou.__version__
    vv[cal_shape_spirou.__NAME__] = cal_shape_spirou.__version__
    # vv[cal_WAVE_E2DS_spirou.__NAME__] = cal_WAVE_E2DS_spirou.__version__
    vv[cal_WAVE_E2DS_EA_spirou.__NAME__] = cal_WAVE_E2DS_EA_spirou.__version__
    # vv[cal_WAVE_NEW_E2DS_spirou.__NAME__] = cal_WAVE_NEW_E2DS_spirou
    vv[cal_preprocess_spirou.__NAME__] = cal_preprocess_spirou.__version__
    vv[off_listing_RAW_spirou.__NAME__] = off_listing_RAW_spirou.__version__
    vv[off_listing_REDUC_spirou.__NAME__] = off_listing_REDUC_spirou.__version__
    vv[obj_mk_tellu.__NAME__] = obj_mk_tellu.__version__
    vv[obj_mk_tellu_db.__NAME__] = obj_mk_tellu_db.__version__
    vv[obj_fit_tellu.__NAME__] = obj_fit_tellu.__version__
    vv[obj_fit_tellu_db.__NAME__] = obj_fit_tellu_db.__version__
    vv[obj_mk_obj_template] = obj_mk_obj_template.__version__
    vv[visu_RAW_spirou.__NAME__] = visu_RAW_spirou.__version__
    vv[visu_E2DS_spirou.__NAME__] = visu_E2DS_spirou.__version__
    vv[pol_spirou.__NAME__] = pol_spirou.__version__


def wrapper(p, rname, inputs=None):
    # get name of run (should be first element in run list
    name = inputs[0]
    if name not in VALID_RECIPES:
        emsg1 = "{0} is not a valid DRS recipe".format(name)
        emsg2 = "    run = {0}".format(rname)
        WLOG(p, 'error', [emsg1, emsg2])
    # deal with no input or outputs
    if inputs is None:
        WLOG(p, 'error', 'Must define inputs')
    # if we don't have outputs then we require inputs only
    strarg = 'p, rname, inputs'
    # link to the recipe function
    recipe_function = 'unit_test_{0}({1})'.format(name.lower(), strarg)
    # return the evaulated unit test function
    try:
        varbs, name = eval(recipe_function)
    except NameError as e:
        emsg1 = 'NameError: Cannot run {0}'.format(recipe_function)
        emsg2 = '\tError reads: {0}'.format(e)
        WLOG(p, 'error', [emsg1, emsg2])
        varbs = []
    # return recipe inputs (or outputs)
    return varbs, name


# noinspection PyUnusedLocal
def run_main(p, name, args):
    # set the program name
    command = '{0}.main(**args)'.format(name)
    ll = eval(command)
    # print pid
    WLOG(p, 'info', 'PID = {0}'.format(ll['p']['PID']))
    # return locals
    return ll


def unit_test_cal_badpix_spirou(p, rname, inputs):

    """
    cal_BADPIX_spirou

    input = night_name [flat_flat_*.fits] [dark_dark_*.fits]
    output = BADPIX_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_BADPIX_spirou'
    arg_names = ['night_name', 'flatfile', 'darkfile']
    arg_types = [str, str, str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_dark_spirou(p, rname, inputs):

    """
    cal_DARK_spirou

    input = night_name files
    output = DARK_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_DARK_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_loc_raw_spirou(p, rname, inputs):

    """
    unit_test_cal_loc_raw_spirou

    input = night_name files
    output = LOC_ORDER_PROFILE_FILE, LOC_LOCO_FILE, LOC_LOCO_FILE2,
             LOC_LOCO_FILE3

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_loc_RAW_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_slit_spirou(p, rname, inputs):
    """
    unit_test_cal_slit_spirou

    input = night_name files
    output = SLIT_TILT_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file


    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_SLIT_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_shape_spirou(p, rname, inputs):
    """
    unit_test_cal_shape_spirou

    input = night_name files
    output = SLIT_SHAPE_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file


    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_shape_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_ff_raw_spirou(p, rname, inputs):
    """
    unit_test_cal_ff_raw_spirou

    input = night_name files
    output = FF_BLAZE_FILE, FF_FLAT_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_FF_RAW_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_extract_raw_spirou(p, rname, inputs):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_extract_RAW_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


# def unit_test_cal_extract_raw_spirouab(rname, inputs):
#     """
#     unit_test_cal_extract_raw_spirou
#
#     input = night_name files
#     output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES
#
#     :param rname: string, identifier for this run
#     :param inputs: list of objects, raw parameters to pass to run, if outputs
#                    is None returns parameters to pass to file
#
#     :return args: dict, the parameters to pass to the run
#     """
#     # define name and arguments
#     name = 'cal_extract_RAW_spirouAB'
#     arg_names = ['night_name', 'files']
#     arg_types = [str, list]
#
#     # get arguments
#     args = get_args(p, name, rname, inputs, arg_names, arg_types)
#     # return args
#     return args, name
#
#
# def unit_test_cal_extract_raw_spirouc(rname, inputs):
#     """
#     unit_test_cal_extract_raw_spirou
#
#     input = night_name files
#     output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES
#
#     :param rname: string, identifier for this run
#     :param inputs: list of objects, raw parameters to pass to run, if outputs
#                    is None returns parameters to pass to file
#
#     :return args: dict, the parameters to pass to the run
#     """
#     # define name and arguments
#     name = 'cal_extract_RAW_spirouC'
#     arg_names = ['night_name', 'files']
#     arg_types = [str, list]
#
#     # get arguments
#     args = get_args(p, name, rname, inputs, arg_names, arg_types)
#     # return args
#     return args, name


# def unit_test_cal_drift_raw_spirou(rname, inputs, outputs=None):
#     """
#     unit_test_cal_drift_raw_spirou
#
#     input = night_name files
#     output = DRIFT_RAW_FILE
#
#     :param rname: string, identifier for this run
#     :param inputs: list of objects, raw parameters to pass to run, if outputs
#                    is None returns parameters to pass to file
#     :param outputs: dictionary or None, output of code - locals() if not None
#                     returns output filenames
#
#     if outputs is None:
#         :return args: dict, the parameters to pass to the run
#     else:
#         :return outs: list of strings, the output filenames
#     """
#     # define name and arguments
#     name = 'cal_DRIFT_RAW_spirou'
#     arg_names = ['night_name', 'files']
#     arg_types = [str, str]
#
#     # get the inputs (if outputs is None)
#     if outputs is None:
#         # get arguments
#         args = get_args(p, name, rname, inputs, arg_names, arg_types)
#         return args, name
#     # else define the outputs
#     else:
#         outs = [Constants.DRIFT_RAW_FILE(outputs['p'])]
#         # return outs
#         return outs, name


def unit_test_cal_drift_e2ds_spirou(p, rname, inputs):
    """
    unit_test_cal_drift_e2ds_spirou

    input = night_name files
    output = DRIFT_E2DS_FITS_FILE, DRIFT_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_DRIFT_E2DS_spirou'
    arg_names = ['night_name', 'reffile']
    arg_types = [str, str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_driftpeak_e2ds_spirou(p, rname, inputs):
    """
    unit_test_cal_driftpeak_e2ds_spirou

    input = night_name files
    output = DRIFTPEAK_E2DS_FITS_FILE, DRIFTPEAK_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_DRIFTPEAK_E2DS_spirou'
    arg_names = ['night_name', 'reffile']
    arg_types = [str, str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_driftccf_e2ds_spirou(p, rname, inputs):
    """
    unit_test_cal_driftccf_e2ds_spirou

    input = night_name files
    output = DRIFT_E2DS_FITS_FILE, DRIFT_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_DRIFTCCF_E2DS_spirou'
    arg_names = ['night_name', 'reffile']
    arg_types = [str, str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_ccf_e2ds_spirou(p, rname, inputs):
    """
    unit_test_cal_ccf_e2ds_spirou

    input = night_name files
    output = DRIFTPEAK_E2DS_FITS_FILE, DRIFTPEAK_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_CCF_E2DS_spirou'
    arg_names = ['night_name', 'e2dsfile', 'mask', 'rv', 'width', 'step']
    arg_types = [str, str, str, float, int, float]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_hc_e2ds_spirou(p, rname, inputs):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_HC_E2DS_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    # return args
    return args, name


def unit_test_cal_hc_e2ds_ea_spirou(p, rname, inputs):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_HC_E2DS_EA_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    # return args
    return args, name


def unit_test_cal_wave_new_e2ds_spirou(p, rname, inputs):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_WAVE_E2DS_spirou'
    arg_names = ['night_name', 'fpfile', 'hcfiles']
    arg_types = [str, str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    # return args
    return args, name


def unit_test_cal_wave_e2ds_spirou(p, rname, inputs):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run

    """
    # define name and arguments
    name = 'cal_WAVE_E2DS_spirou'
    arg_names = ['night_name', 'fpfile', 'hcfiles']
    arg_types = [str, str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    # return args
    return args, name


def unit_test_cal_wave_e2ds_ea_spirou(p, rname, inputs):
    """
    unit_test_cal_extract_raw_spirou

    input = night_name files
    output = EXTRACT_E2DS_FILE, EXTRACT_E2DS_ALL_FILES

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run

    """
    # define name and arguments
    name = 'cal_WAVE_E2DS_EA_spirou'
    arg_names = ['night_name', 'fpfile', 'hcfiles']
    arg_types = [str, str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    # return args
    return args, name


def unit_test_cal_exposure_meter(p, rname, inputs):
    """
    unit_test_cal_exposure_meter

    input = night_name files
    output = EM_SPE_FILE, EM_WAVE_FILE, EM_MASK_FILE
                based on EM_OUTPUT_TYPE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_exposure_meter'
    arg_names = ['night_name', 'flatfile']
    arg_types = [str, str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_wave_mapper(p, rname, inputs):
    """
    unit_test_cal_wave_mapper

    input = night_name files
    output = WAVE_MAP_SPE_FILE, WAVE_MAP_SPE0_FILE, EM_WAVE_FILE
                based on EM_OUTPUT_TYPE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_wave_mapper'
    arg_names = ['night_name', 'flatfile', 'e2dsprefix']
    arg_types = [str, str, str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_cal_preprocess_spirou(p, rname, inputs):
    """
    unit_test_cal_driftpeak_e2ds_spirou

    input = night_name files
    output = DRIFTPEAK_E2DS_FITS_FILE, DRIFTPEAK_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'cal_preprocess_spirou'
    arg_names = ['night_name', 'ufiles']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_off_listing_raw_spirou(p, rname, inputs):
    """
    unit_test_cal_exposure_meter

    input = night_name files
    output = EM_SPE_FILE, EM_WAVE_FILE, EM_MASK_FILE
                based on EM_OUTPUT_TYPE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'off_listing_RAW_spirou'
    arg_names = ['night_name']
    arg_types = [str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_off_listing_reduc_spirou(p, rname, inputs):
    """
    unit_test_cal_exposure_meter

    input = night_name files
    output = EM_SPE_FILE, EM_WAVE_FILE, EM_MASK_FILE
                based on EM_OUTPUT_TYPE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run

    """
    # define name and arguments
    name = 'off_listing_REDUC_spirou'
    arg_names = ['night_name']
    arg_types = [str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_obj_mk_tellu(p, rname, inputs):
    """
    unit_test_cal_exposure_meter

    input = night_name files
    output = EM_SPE_FILE, EM_WAVE_FILE, EM_MASK_FILE
                based on EM_OUTPUT_TYPE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'obj_mk_tellu'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_obj_fit_tellu(p, rname, inputs):
    """
    unit_test_cal_exposure_meter

    input = night_name files
    output = EM_SPE_FILE, EM_WAVE_FILE, EM_MASK_FILE
                based on EM_OUTPUT_TYPE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'obj_fit_tellu'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_obj_fit_tellu_db(p, rname, inputs):
    """
    unit_test_cal_exposure_meter

    input = night_name files
    output = EM_SPE_FILE, EM_WAVE_FILE, EM_MASK_FILE
                based on EM_OUTPUT_TYPE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'obj_fit_tellu_db'
    arg_names = ['cores', 'objects']
    arg_types = [int, str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_obj_mk_tellu_db(p, rname, inputs):
    """
    unit_test_cal_exposure_meter

    input = night_name files
    output = EM_SPE_FILE, EM_WAVE_FILE, EM_MASK_FILE
                based on EM_OUTPUT_TYPE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'obj_mk_tellu_db'
    arg_names = []
    arg_types = []

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_obj_mk_obj_template(p, rname, inputs):
    """
    unit_test_obj_mk_obj_template

    input = night_name files

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'obj_mk_obj_template'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_visu_raw_spirou(p, rname, inputs):
    """
    unit_test_cal_ff_raw_spirou

    input = night_name files
    output = FF_BLAZE_FILE, FF_FLAT_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return outs: list of strings, the output filenames
    """
    # define name and arguments
    name = 'visu_RAW_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_visu_e2ds_spirou(p, rname, inputs):
    """
    unit_test_cal_driftpeak_e2ds_spirou

    input = night_name files
    output = DRIFTPEAK_E2DS_FITS_FILE, DRIFTPEAK_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    :return args: dict, the parameters to pass to the run
    """
    # define name and arguments
    name = 'visu_E2DS_spirou'
    arg_names = ['night_name', 'reffile']
    arg_types = [str, str]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def unit_test_pol_spirou(p, rname, inputs):
    """
    unit_test_cal_driftpeak_e2ds_spirou

    input = night_name files
    output = DRIFTPEAK_E2DS_FITS_FILE, DRIFTPEAK_E2DS_TBL_FILE

    :param rname: string, identifier for this run
    :param inputs: list of objects, raw parameters to pass to run, if outputs
                   is None returns parameters to pass to file

    return args: dict, the parameters to pass to the run

    """
    # define name and arguments
    name = 'pol_spirou'
    arg_names = ['night_name', 'files']
    arg_types = [str, list]

    # get arguments
    args = get_args(p, name, rname, inputs, arg_names, arg_types)
    return args, name


def get_args(p, name, rname, iargs, arg_names, arg_types):

    if len(arg_names) == 0:
        return OrderedDict()

    # we should at least have enough inputs for the arg names given
    if len(iargs) < (len(arg_names) + 1):
        emsg1 = '{0} has invalid number of arguments for {1}'
        eargs = [len(arg_names), len(iargs)]
        emsg2 = '   expected (at least) {0} got {1}'.format(*eargs)
        WLOG(p, 'error', [emsg1.format(rname, name), emsg2])
    # set up storage
    args = OrderedDict()
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
        elif (arg_types[pos] == list) and type(value) in PYTHON_STRINGS:
            args[arg_name] = [value]
        else:
            try:
                value = arg_types[pos](value)
                args[arg_name] = value
            except ValueError:
                eargs = [rname, pos, arg_name, arg_types[pos]]
                emsg1 = '{0}: Argument {1} ({2}) should be type={3}'
                emsg2 = '    got type={0}'.format(type(value))
                WLOG(p, 'error', [emsg1.format(*eargs), emsg2])
        # add to counter
        pos += 1
    # deal with the fact we may have more arguments than arg_names
    if len(iargs) > (len(arg_names) + 1):
        if arg_types[pos - 1] == list:
            # find the last value added to arg_names
            end_argument = args[arg_names[pos - 1]]
            # add the remaining arguments to this argument
            for it in range(pos + 1, len(iargs)):
                end_argument.append(iargs[it])
            # set the last argument to the end argument list
            args[arg_names[pos - 1]] = end_argument
    # return args
    return args


# =============================================================================
# End of code
# =============================================================================
