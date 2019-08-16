#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-16 at 11:18

@author: cook
"""
from __future__ import division
import os

from terrapipe import core
from terrapipe.core import constants
from terrapipe import locale
from terrapipe.core.core import drs_file
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_startup
from terrapipe.io import drs_image

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.extract.other.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
def extract_thermal_files(params, recipe, extname, thermalfile, **kwargs):
    func_name = __NAME__ + '.extract_thermal_files()'
    # get parameters from params/kwargs
    therm_always_extract = pcheck(params, 'WAVE_ALWAYS_EXTRACT',
                                  'always_extract', kwargs, func_name)
    therm_extract_type = pcheck(params, 'WAVE_EXTRACT_TYPE', 'extract_type',
                                kwargs, func_name)
    # get nightname
    nightname = params['INPUTS']['DIRECTORY']
    # find the extraction recipe
    extrecipe, _ = drs_startup.find_recipe(extname, params['INSTRUMENT'],
                                           mod=recipe.recipemod)
    # ----------------------------------------------------------------------
    # extract hc files
    # ----------------------------------------------------------------------
    # get output filetype
    thfileinst = recipe.outputs['THERMAL_E2DS_FILE']
    # get outputs
    thermal_outputs = extract_files(params, recipe, thermalfile, thfileinst,
                                    therm_always_extract, extrecipe, nightname,
                                    therm_extract_type, kind='thermal',
                                    func_name=func_name)
    # ----------------------------------------------------------------------
    # return extraction outputs
    # ----------------------------------------------------------------------
    # return hc and fp outputs
    return thermal_outputs


def extract_wave_files(params, recipe, extname, hcfile,
                       fpfile, **kwargs):
    func_name = __NAME__ + '.extract_wave_files()'
    # get parameters from params/kwargs
    wave_always_extract = pcheck(params, 'WAVE_ALWAYS_EXTRACT',
                                 'always_extract', kwargs, func_name)
    wave_extract_type = pcheck(params, 'WAVE_EXTRACT_TYPE', 'extract_type',
                               kwargs, func_name)
    # get nightname
    nightname = params['INPUTS']['DIRECTORY']
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
                               wave_always_extract, extrecipe, nightname,
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
                                   wave_always_extract, extrecipe, nightname,
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
                  extrecipe, nightname, extract_type, kind='gen',
                  func_name=None):
    if func_name is None:
        func_name = __NAME__ + '.extract_files()'
    # get the fiber types from a list parameter
    fiber_types = drs_image.get_fiber_types(params)
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

        # need to handle passing keywords from main
        kwargs = core.copy_kwargs(params, extrecipe, directory=nightname,
                                  files=[infile.basename])
        # set the program name (shouldn't be cal_extract)
        kwargs['program'] = '{0}_extract'.format(kind)
        # push data to extractiong code
        data_dict = ParamDict()
        data_dict['files'] = [infile]
        data_dict['rawfiles'] = [infile.basename]
        data_dict['combine'] = params['INPUT_COMBINE_IMAGES']
        kwargs['DATA_DICT'] = data_dict
        # pipe into cal_extract
        llout = extrecipe.main(**kwargs)
        # check success
        if not llout['success']:
            eargs = [recipe.name, func_name]
            WLOG(params, 'error', TextEntry('09-016-00002', args=eargs))
        # get qc
        passed = llout['params']['QC']
        # deal with hc failure
        if not passed:
            # log error: extraction of file failed
            eargs = [kind, infile.basename, func_name]
            WLOG(params, 'error', TextEntry('09-016-00003', args=eargs))

        # loop around fibers
        for fiber in fiber_types:
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
            outfile.read()
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
