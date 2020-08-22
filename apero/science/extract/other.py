#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-16 at 11:18

@author: cook
"""
import os

from apero.base import base
from apero import core
from apero.core import constants
from apero import lang
from apero.core.utils import drs_file, drs_startup
from apero.core.core import drs_log
from apero.io import drs_image

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.other.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def extract_thermal_files(params, recipe, extname, thermalfile, **kwargs):
    func_name = __NAME__ + '.extract_thermal_files()'
    # get parameters from params/kwargs
    therm_always_extract = pcheck(params, 'THERMAL_ALWAYS_EXTRACT',
                                  'always_extract', kwargs, func_name)
    therm_extract_type = pcheck(params, 'THERMAL_EXTRACT_TYPE', 'extract_type',
                                kwargs, func_name)
    # find the extraction recipe
    extrecipe, _ = drs_startup.find_recipe(extname, params['INSTRUMENT'],
                                           mod=recipe.recipemod)
    # ----------------------------------------------------------------------
    # extract thermal files
    # ----------------------------------------------------------------------
    # get output e2ds filetype
    thfileinst = recipe.outputs['THERMAL_E2DS_FILE']
    # get outputs
    thermal_outputs = extract_files(params, recipe, thermalfile, thfileinst,
                                    therm_always_extract, extrecipe,
                                    therm_extract_type, kind='thermal',
                                    func_name=func_name)

    # Need to figure out the thermal output
    dprtype = thermalfile.get_key('KW_DPRTYPE', dtype=str)
    # TODO: Add sky dark here
    if dprtype == 'DARK_DARK_INT':
        thoutinst = recipe.outputs['THERMALI_FILE']
    elif dprtype == 'DARK_DARK_TEL':
        thoutinst = recipe.outputs['THERMALT_FILE']
    else:
        eargs = [dprtype, func_name]
        WLOG(params, 'error', TextEntry('40-016-00022', args=eargs))
        thoutinst = None

    # ----------------------------------------------------------------------
    # Need to push properties to thermal e2ds file (thermal_outputs are
    #     regular e2ds files)
    # ----------------------------------------------------------------------
    # thermal e2ds file list storage
    thermal_files = dict()
    # loop around fibers
    for fiber in thermal_outputs:
        # get copy file instance
        thermal_file = thoutinst.newcopy(recipe=recipe, fiber=fiber)
        # construct the filename from e2ds file (it is the same file)
        thermal_file.construct_filename(params, infile=thermalfile)
        # copy header and hdict
        thermal_file.hdict = thermal_outputs[fiber].header
        thermal_file.header = thermal_outputs[fiber].header
        # add data from thermal_outputs
        thermal_file.datatype = thermal_outputs[fiber].datatype
        thermal_file.data = thermal_outputs[fiber].data
        # update drs out id
        thermal_file.hdict[params['KW_OUTPUT'][0]] = thermal_file.name
        thermal_file.header[params['KW_OUTPUT'][0]] = thermal_file.name
        # append to list
        thermal_files[fiber] = thermal_file

    # ----------------------------------------------------------------------
    # return extraction outputs
    # ----------------------------------------------------------------------
    # return thermal outputs
    return thermal_files


def extract_leak_files(params, recipe, extname, darkfpfile, **kwargs):
    func_name = __NAME__ + '.extract_leak_files()'
    # get parameters from params/kwargs
    therm_always_extract = pcheck(params, 'LEAKM_ALWAYS_EXTRACT',
                                  'always_extract', kwargs, func_name)
    therm_extract_type = pcheck(params, 'LEAKM_EXTRACT_TYPE', 'extract_type',
                                kwargs, func_name)
    # find the extraction recipe
    extrecipe, _ = drs_startup.find_recipe(extname, params['INSTRUMENT'],
                                           mod=recipe.recipemod)
    # ----------------------------------------------------------------------
    # extract thermal files
    # ----------------------------------------------------------------------
    # get output e2ds filetype
    fileinst = recipe.outputs['LEAK_E2DS_FILE']
    # get outputs
    darkfp_outputs = extract_files(params, recipe, darkfpfile, fileinst,
                                    therm_always_extract, extrecipe,
                                    therm_extract_type, kind='leakage',
                                    func_name=func_name)
    
    # ----------------------------------------------------------------------
    # return extraction outputs
    # ----------------------------------------------------------------------
    # return dark fp outputs
    return darkfp_outputs


def extract_wave_files(params, recipe, extname, hcfile,
                       fpfile, **kwargs):
    func_name = __NAME__ + '.extract_wave_files()'
    # get parameters from params/kwargs
    wave_always_extract = pcheck(params, 'WAVE_ALWAYS_EXTRACT',
                                 'always_extract', kwargs, func_name)
    wave_extract_type = pcheck(params, 'WAVE_EXTRACT_TYPE', 'extract_type',
                               kwargs, func_name)
    # find the extraction recipe
    extrecipe, _ = drs_startup.find_recipe(extname, params['INSTRUMENT'],
                                           mod=recipe.recipemod)
    # get the fiber types from a list parameter
    fiber_types = drs_image.get_fiber_types(params)
    # ----------------------------------------------------------------------
    # extract hc files
    # ----------------------------------------------------------------------
    # get output filetype
    hcfileinst = recipe.outputs['WAVE_E2DS']
    # get outputs
    hc_outputs = extract_files(params, recipe, hcfile, hcfileinst,
                               wave_always_extract, extrecipe,
                               wave_extract_type, kind='hc',
                               func_name=func_name)
    # ----------------------------------------------------------------------
    # extract fp files
    # ----------------------------------------------------------------------
    if fpfile is not None:
        # get output filetype
        fpfileinst = recipe.outputs['WAVE_E2DS']
        # get outputs
        fp_outputs = extract_files(params, recipe, fpfile, fpfileinst,
                                   wave_always_extract, extrecipe,
                                   wave_extract_type, kind='fp',
                                   func_name=func_name)
    else:
        # make storage for fp outputs
        fp_outputs = dict()
        # loop around fiber types
        for fiber in fiber_types:
            fp_outputs[fiber] = None
    # ----------------------------------------------------------------------
    # return extraction outputs
    # ----------------------------------------------------------------------
    # return hc and fp outputs
    return hc_outputs, fp_outputs


# =============================================================================
# Define worker functions
# =============================================================================
def extract_files(params, recipe, infile, outfile, always_extract,
                  extrecipe, extract_type, kind='gen', func_name=None):
    if func_name is None:
        func_name = __NAME__ + '.extract_files()'
    # get the fiber types from a list parameter
    fiber_types = drs_image.get_fiber_types(params)

    # ------------------------------------------------------------------
    # Get the output hc e2ds filename (and check if it exists)
    # ------------------------------------------------------------------
    # set up drs group (for logging)
    groupname = core.group_name(params, suffix='extract')
    # ------------------------------------------------------------------
    # Get the output hc e2ds filename (and check if it exists)
    # ------------------------------------------------------------------
    # set up the exists command
    exists = True
    # set up storage
    e2ds_files = dict()
    # loop around fiber types
    for fiber in fiber_types:
        # get copy file instance
        e2ds_file = outfile.newcopy(recipe=recipe, fiber=fiber)
        # construct the filename from file instance
        e2ds_file.construct_filename(params, infile=infile)
        # check whether e2ds file exists
        if os.path.exists(e2ds_file.filename):
            exists = exists and True
        else:
            exists = exists and False
        # append to storage
        e2ds_files[fiber] = e2ds_file

    # ------------------------------------------------------------------
    # extract the hc (AB, A, B and C) or read hc e2ds header
    # ------------------------------------------------------------------
    # storage of outputs
    outputs = dict()
    # only extract if required
    if always_extract or (not exists):
        # need to get nightname and dir name (above night name)
        nightname = os.path.dirname(infile.filename)
        dirname = os.path.dirname(nightname)
        # need to handle passing keywords from main
        kwargs = core.copy_kwargs(params, extrecipe, directory=nightname,
                                  files=[infile.basename])
        # set the program name (shouldn't be cal_extract)
        kwargs['program'] = '{0}_extract'.format(kind)
        # force the input directory (combined files go to reduced dir)
        kwargs['force_indir'] = dirname
        # push data to extractiong code
        data_dict = ParamDict()
        data_dict['files'] = [infile]
        data_dict['rawfiles'] = [infile.basename]
        data_dict['combine'] = params['INPUT_COMBINE_IMAGES']
        kwargs['DATA_DICT'] = data_dict
        # ------------------------------------------------------------------
        # deal with adding group name
        if groupname is not None:
            # if we don't have a group already
            if params['DRS_GROUP'] is None:
                kwargs['DRS_GROUP'] = groupname
            # if we do have a sub-folder
            else:
                groupname = os.path.join(params['DRS_GROUP'], groupname)
                kwargs['DRS_GROUP'] = groupname
        # ------------------------------------------------------------------
        # pipe into cal_extract
        llout = extrecipe.main(**kwargs)
        # check success
        if not llout['success']:
            eargs = [recipe.name, func_name]
            WLOG(params, 'error', TextEntry('09-016-00002', args=eargs))
        # get qc
        passed = llout['passed']
        # deal with hc failure
        if not passed:
            # log error: extraction of file failed
            eargs = [kind, infile.basename, func_name]
            WLOG(params, 'error', TextEntry('09-016-00003', args=eargs))

        # loop around fibers
        for fiber in fiber_types:
            # log that we are reading file
            wargs = [e2ds_files[fiber]]
            WLOG(params, '', TextEntry('40-016-00023', args=wargs))
            # construct output key
            outkey = '{0}_{1}'.format(extract_type, fiber)
            # copy file to dictionary
            outputs[fiber] = llout['e2dsoutputs'][outkey]
    # else we just need to read the header of the output file
    else:
        # loop around fibers
        for fiber in fiber_types:
            # construct out file
            outfile = e2ds_files[fiber]
            # log that we are reading file
            wargs = [outfile.filename]
            WLOG(params, '', TextEntry('40-016-00021', args=wargs))
            # read file header and push into outputs
            outfile.read_file()
            # copy file to dictionary
            outputs[fiber] = outfile.completecopy(outfile)
    # return dictionary of outputs (one key for each fiber)
    return outputs


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
