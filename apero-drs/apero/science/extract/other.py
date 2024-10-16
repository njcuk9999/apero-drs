#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-16 at 11:18

@author: cook
"""
import os
from typing import Optional, Union

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore import drs_lang
from apero.core import drs_file
from aperocore.core import drs_log
from aperocore.core import drs_text
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.utils import drs_utils
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
ParamDict = param_functions.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsRecipe = drs_recipe.DrsRecipe
# Get Logging function
WLOG = drs_log.wlog
# Get the DrsLog Class
RecipeLog = drs_utils.RecipeLog
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
def extract_thermal_files(params, recipe, extname, thermalfile,
                          logger, **kwargs):
    func_name = __NAME__ + '.extract_thermal_files()'
    # get parameters from params/kwargs
    therm_always_extract = pcheck(params, 'THERMAL_ALWAYS_EXTRACT',
                                  'always_extract', kwargs, func_name)
    # find the extraction recipe
    extrecipe, _ = drs_startup.find_recipe(extname, params['INSTRUMENT'],
                                           mod=recipe.recipemod)
    # ----------------------------------------------------------------------
    # extract thermal files
    # ----------------------------------------------------------------------
    # Need to figure out the thermal output
    dprtype = thermalfile.get_hkey('KW_DPRTYPE', dtype=str)
    # DARK_DARK_INT extraction comes before wave solution is generated
    #   ( as wave sol requires thermal correction, therefore we only have the
    #    reference or default reference wave solution - and must force extraction
    #    to only look for reference wave solutions)
    if dprtype == 'DARK_DARK_INT':
        force_ref_wave = True
    elif dprtype == 'DARK_DARK_TEL':
        force_ref_wave = False
    else:
        force_ref_wave = False
    # get output e2ds filetype
    thfileinst = recipe.outputs['THERMAL_E2DS_FILE']
    # get outputs
    thermal_outputs = extract_files(params, recipe, thermalfile, thfileinst,
                                    therm_always_extract, extrecipe,
                                    kind='thermal', func_name=func_name,
                                    logger=logger,
                                    force_ref_wave=force_ref_wave)

    # TODO: Add sky dark here
    if dprtype == 'DARK_DARK_INT':
        thoutinst = recipe.outputs['THERMALI_FILE']
    elif dprtype == 'DARK_DARK_TEL':
        thoutinst = recipe.outputs['THERMALT_FILE']
    else:
        eargs = [dprtype, func_name]
        WLOG(params, 'error', textentry('40-016-00022', args=eargs))
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
        thermal_file = thoutinst.newcopy(params=params, fiber=fiber)
        # construct the filename from e2ds file (it is the same file)
        thermal_file.construct_filename(infile=thermalfile)
        # copy header and hdict
        thermal_file.hdict = thermal_outputs[fiber].get_header()
        thermal_file.header = thermal_outputs[fiber].get_header()
        # add data from thermal_outputs
        thermal_file.datatype = thermal_outputs[fiber].datatype
        thermal_file.data = thermal_outputs[fiber].get_data()
        # get input files
        thermal_file.infiles = [thermalfile.basename]
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


def extract_leak_files(params, recipe, extname, darkfpfile, logger,
                       **kwargs):
    func_name = __NAME__ + '.extract_leak_files()'
    # get parameters from params/kwargs
    leak_always_extract = pcheck(params, 'LEAKREF_ALWAYS_EXTRACT',
                                 'always_extract', kwargs, func_name)
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
                                   leak_always_extract, extrecipe,
                                   kind='leakage', func_name=func_name,
                                   leakcorr=False, logger=logger)
    
    # ----------------------------------------------------------------------
    # return extraction outputs
    # ----------------------------------------------------------------------
    # return dark fp outputs
    return darkfp_outputs


def extract_wave_files(params, recipe, extname, hcfile,
                       fpfile, wavefile, logger, **kwargs):
    func_name = __NAME__ + '.extract_wave_files()'
    # get parameters from params/kwargs
    wave_always_extract = pcheck(params, 'WAVE_ALWAYS_EXTRACT',
                                 'always_extract', kwargs, func_name)
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
                               kind='hc', func_name=func_name,
                               wavefile=wavefile, logger=logger)
    # ----------------------------------------------------------------------
    # extract fp files
    # ----------------------------------------------------------------------
    if fpfile is not None:
        # get output filetype
        fpfileinst = recipe.outputs['WAVE_E2DS']
        # get outputs
        fp_outputs = extract_files(params, recipe, fpfile, fpfileinst,
                                   wave_always_extract, extrecipe,
                                   kind='fp', func_name=func_name,
                                   wavefile=wavefile, logger=logger)
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
def extract_files(params: ParamDict, recipe: DrsRecipe,
                  infile: DrsFitsFile, outfile: DrsFitsFile,
                  always_extract: bool, extrecipe: Union[DrsRecipe, None],
                  kind: str = 'gen',
                  func_name: Union[str, None] = None,
                  leakcorr: Optional[bool] = None,
                  wavefile: Optional[str] = None,
                  logger: Optional[RecipeLog] = None,
                  force_ref_wave: bool = False):
    if func_name is None:
        func_name = __NAME__ + '.extract_files()'
    # get the fiber types from a list parameter
    fiber_types = drs_image.get_fiber_types(params)
    # we must index any files currently in recipe.output_files before this
    #  point as we need to use these files later on - examples are
    #  the file that were combined
    drs_startup.index_files(params, recipe)
    # ------------------------------------------------------------------
    # Get the output hc e2ds filename (and check if it exists)
    # ------------------------------------------------------------------
    # set up drs group (for logging)
    groupname = drs_startup.group_name(params, suffix='extract')
    # if we have a obs_dir then add this to the group name path
    if not drs_text.null_text(params['OBS_SUBDIR'], ['None', '', 'Null']):
        groupname = os.path.join(params['OBS_SUBDIR'], groupname)

    # ------------------------------------------------------------------
    # Get the correct observation directory
    # ------------------------------------------------------------------
    # get in and out paths (thw two places a file can be)
    inpath = params['INPATH']
    outpath = params['OUTPATH']
    # get the observation directory if infile is in the outpath
    if outpath in infile.filename:
        obs_dir = os.path.dirname(infile.filename).split(outpath)[1]
    # get the observation directory if infile is in the inpath
    elif inpath in infile.filename:
        obs_dir = os.path.dirname(infile.filename).split(inpath)[1]
    # otherwise deal with error
    else:
        emsg = 'Input file {0} not in input or output path'
        eargs = [infile.filename, inpath, outpath, func_name]
        WLOG(params, 'error', emsg.format(*eargs))
        obs_dir = ''
    # remove leading/trailing slashes
    obs_dir = obs_dir.strip(os.sep)
    # ------------------------------------------------------------------
    # Get the output hc e2ds filename (and check if it exists)
    # ------------------------------------------------------------------
    # set up the exists command
    exists = True
    # set up storage
    e2ds_files = dict()
    # loop around fiber types
    for fiber in fiber_types:
        # need to copy params and change observation directory
        tmp_params = params.copy()
        tmp_params['OBS_DIR'] = obs_dir
        # get copy file instance
        e2ds_file = outfile.newcopy(params=tmp_params, fiber=fiber)
        # construct the filename from file instance
        e2ds_file.construct_filename(infile=infile)
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
        # need to get obs_dir and block dir (above obs_dir)
        path_ins = drs_file.DrsPath(params, abspath=infile.filename)
        obs_dir = path_ins.obs_dir
        # need to handle passing keywords from main
        kwargs = drs_startup.copy_kwargs(params, extrecipe, obs_dir=obs_dir,
                                         files=[infile.basename])
        # set the program name (shouldn't be apero_extract)
        kwargs['program'] = '{0}_extract'.format(kind)
        kwargs['recipe_kind'] = '{0}-extract'.format(kind)
        kwargs['recipe_type'] = 'sub-recipe'
        kwargs['parallel'] = params['INPUTS']['PARALLEL']
        kwargs['force_ref_wave'] = force_ref_wave
        # force the input directory (combined files go to reduced dir)
        kwargs['force_indir'] = path_ins.block_kind
        # if CRUNFILE is set add it to the kwargs
        crunfile = params['INPUTS']['CRUNFILE']
        if not drs_text.null_text(crunfile, ['', 'None', 'Null']):
            kwargs['crunfile'] = crunfile
        # push data to extraction code
        data_dict = ParamDict()
        # data_dict['files'] = [infile]
        # We need to load these again
        data_dict['files'] = None
        data_dict['rawfiles'] = [infile.basename]
        data_dict['combine'] = params['INPUT_COMBINE_IMAGES']
        # add leak correction argument if set
        if leakcorr is not None and isinstance(leakcorr, bool):
            data_dict['LEAKCORR'] = leakcorr
        # add wave file correction argument if set
        if wavefile is not None and isinstance(wavefile, str):
            data_dict['WAVEFILE'] = wavefile

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
        # pipe into apero_extract
        try:
            # llout = extrecipe.main(**kwargs)
            extrecipe.main(**kwargs)
            llout = dict()
            llout['params'] = dict()
            llout['params']['LOGGER_ERROR'] = []
            llout['params']['LOGGER_WARNING'] = []
            llout['success'] = True
            # llout['passed'] = True
        except Exception as e:
            llout = dict()
            llout['params'] = dict()
            llout['params']['LOGGER_ERROR'] = [['', str(e)]]
            llout['params']['LOGGER_WARNING'] = [[]]
            llout['success'] = False
            # llout['passed'] = False
        except SystemExit as e:
            llout = dict()
            llout['params'] = dict()
            llout['params']['LOGGER_ERROR'] = [['', str(e)]]
            llout['params']['LOGGER_WARNING'] = [[]]
            llout['success'] = False
            # llout['passed'] = False
        # pipe errors and warnings
        for error in llout['params']['LOGGER_ERROR']:
            # make sure we have an error listed
            if len(error) > 0:
                # error should show it was from extraction recipe
                errormsg = '[FROM {0}] '.format(extrecipe.name.upper())
                errormsg += error[1]
                # append to logger error storage for this PID
                WLOG.logger_storage(params, 'error', ttime=error[0],
                                    mess=errormsg, program=extrecipe.shortname)
        for warn in llout['params']['LOGGER_WARNING']:
            # make sure we have a warning listed
            if len(warn) > 0:
                # warning should show it was from extraction recipe
                warnmsg = '[FROM {0}] '.format(extrecipe.name.upper())
                warnmsg += warn[1]
                # append to logger warning storage for this PID
                WLOG.logger_storage(params, 'warning', ttime=warn[0],
                                    mess=warnmsg, program=extrecipe.shortname)
        # check success
        if not llout['success']:
            eargs = [recipe.name, func_name]
            WLOG(params, 'error', textentry('09-016-00002', args=eargs))
        # # get qc
        # passed = bool(llout['passed'])

        # let's free up some memory
        del kwargs
        del data_dict
        del llout

        # # deal with hc failure
        # if not passed:
        #     # log error: extraction of file failed
        #     eargs = [kind, infile.basename, func_name]
        #     WLOG(params, 'error', textentry('09-016-00003', args=eargs))

        # # loop around fibers
        # for fiber in fiber_types:
        #     # log that we are reading file
        #     wargs = [e2ds_files[fiber]]
        #     WLOG(params, '', textentry('40-016-00023', args=wargs))
        #     # construct output key
        #     outkey = '{0}_{1}'.format(extract_type, fiber)
        #     # copy file to dictionary
        #     drsfile = llout['e2dsoutputs'][outkey]
        #     # do a complete copy of the drs file
        #     outputs[fiber] = drsfile.completecopy(drsfile)
        # # clean up
        # del llout
    # else we just need to read the header of the output file
    else:
        # update flag saying extraction file found previous
        if logger is not None:
            logger.update_flags(EXT_FOUND=True)
    # loop around fibers
    for fiber in fiber_types:
        # construct out file
        outfile = e2ds_files[fiber]
        # log that we are reading file
        wargs = [outfile.filename]
        WLOG(params, '', textentry('40-016-00021', args=wargs))
        # read file header and push into outputs
        outfile.read_file()
        # deal with quality control failure
        passed = bool(outfile.header[params['KW_DRS_QC'][0]])
        # if not passed flag error here
        if not passed:
            # log error: extraction of file failed
            eargs = [kind, infile.basename, func_name]
            WLOG(params, 'error', textentry('09-016-00003', args=eargs))
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
