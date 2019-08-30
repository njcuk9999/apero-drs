#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

@author: cook
"""
from __future__ import division
import numpy as np

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.core.instruments.spirou import file_definitions
from terrapipe.io import drs_fits
from terrapipe.science.calib import general
from terrapipe.science.calib import localisation
from terrapipe.science.calib import wave
from terrapipe.science.calib import shape

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_shape_spirou.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# Get Logging function
WLOG = core.wlog
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, files=None, **kwargs):
    """
    Main function for cal_shape_master_spirou.py

    :param directory: string, the night name sub-directory
    :param hcfiles: list of strings or string, the list of hc files
    :param fpfiles: list of strings or string, the list of fp files
    :param kwargs: any additional keywords

    :type directory: str
    :type hcfiles: list[str]
    :type fpfiles: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, files=files, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = core.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = core.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    params = core.end_main(llmain['params'], recipe, success)
    # return a copy of locally defined variables in the memory
    return core.get_locals(params, dict(locals()), llmain)


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # get calibration database
    cdb = drs_database.get_full_database(params, 'calibration')
    params[cdb.dbshort] = cdb
    # get files
    infiles = params['INPUTS']['FILES'][1]
    # get list of filenames (for output)
    rawfiles = []
    for infile in infiles:
        rawfiles.append(infile.basename)
    # deal with input data from function
    if 'files' in params['DATA_DICT']:
        infiles = params['DATA_DICT']['files']
        rawfiles = params['DATA_DICT']['rawfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        infiles = [drs_fits.combine(params, infiles, math='median')]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)

    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.header
        # get calibrations for this data
        drs_database.copy_calibrations(params, header)

        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = general.calibrate_ppfile(params, recipe, infile)

        # ------------------------------------------------------------------
        # Load master fp, shape dxmap and dymap
        # ------------------------------------------------------------------
        masterfp_file, masterfp_image = shape.get_master_fp(params, header)
        dxmap_file, dxmap = shape.get_shapex(params, header)
        dymap_file, dymap = shape.get_shapey(params, header)

        # ----------------------------------------------------------------------
        # Get transform parameters (transform image onto fpmaster)
        # ----------------------------------------------------------------------
        # log progress
        WLOG(params, '', TextEntry('40-014-00033'))
        # transform
        targs = [params, masterfp_image, image]
        transform, xres, yres = shape.get_linear_transform_params(*targs)

        # ----------------------------------------------------------------------
        # For debug purposes straighten the image
        # ----------------------------------------------------------------------
        image2 = shape.ea_transform(params, image, transform, dxmap=dxmap,
                                    dymap=dymap)

        # ----------------------------------------------------------------------
        # Quality control
        # ----------------------------------------------------------------------
        # set passed variable and fail message list
        fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # ------------------------------------------------------------------
        # check that transform is not None
        if transform is None:
            fail_msg.append(textdict['40-014-00034'])
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        qc_values.append('None')
        qc_names.append('Image Quality')
        qc_logic.append('Image too poor')
        # ------------------------------------------------------------------
        # check that the x and y residuals are low enough
        qc_res = params['SHAPE_QC_LTRANS_RES_THRES']
        # assess quality of x residuals
        if xres > qc_res:
            fail_msg.append(textdict['40-014-00035'].format(xres, qc_res))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        qc_values.append(xres)
        qc_names.append('XRES')
        qc_logic.append('XRES > {0}'.format(qc_res))
        # assess quality of x residuals
        if yres > qc_res:
            fail_msg.append(textdict['40-014-00036'].format(yres, qc_res))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        qc_values.append(yres)
        qc_names.append('YRES')
        qc_logic.append('YRES > {0}'.format(qc_res))
        # ------------------------------------------------------------------
        # finally log the failed messages and set QC = 1 if we pass the
        # quality control QC = 0 if we fail quality control
        if np.sum(qc_pass) == len(qc_pass):
            WLOG(params, 'info', TextEntry('40-005-10001'))
            passed = 1
        else:
            for farg in fail_msg:
                WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
            passed = 0
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

        # ------------------------------------------------------------------
        # Writing shape to file
        # ------------------------------------------------------------------
        # define outfile
        outfile = recipe.outputs['LOCAL_SHAPE_FILE'].newcopy(recipe=recipe)
        # construct the filename from file instance
        outfile.construct_filename(params, infile=infile)
        # ------------------------------------------------------------------
        # define header keys for output file
        # copy keys from input file
        outfile.copy_original_keys(infile)
        # add version
        outfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add dates
        outfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
        outfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
        # add process id
        outfile.add_hkey('KW_PID', value=params['PID'])
        # add output tag
        outfile.add_hkey('KW_OUTPUT', value=outfile.name)
        # add input files (and deal with combining or not combining)
        if combine:
            hfiles = rawfiles
        else:
            hfiles = [infile.basename]
        outfile.add_hkey_1d('KW_INFILE1', values=hfiles,
                             dim1name='hcfiles')
        # add the calibration files use
        outfile = general.add_calibs_to_header(outfile, props)
        # add qc parameters
        outfile.add_qckeys(qc_params)
        # add shape transform parameters
        outfile.add_hkey('KW_SHAPE_DX', value=transform[0])
        outfile.add_hkey('KW_SHAPE_DY', value=transform[1])
        outfile.add_hkey('KW_SHAPE_A', value=transform[2])
        outfile.add_hkey('KW_SHAPE_B', value=transform[3])
        outfile.add_hkey('KW_SHAPE_C', value=transform[4])
        outfile.add_hkey('KW_SHAPE_D', value=transform[5])
        # copy data
        outfile.data = [transform]
        # ------------------------------------------------------------------
        # log that we are saving dxmap to file
        WLOG(params, '', TextEntry('40-014-00037', args=[outfile.filename]))
        # write image to file
        outfile.write()

        # ----------------------------------------------------------------------
        # Writing DEBUG files
        # ----------------------------------------------------------------------
        if params['SHAPE_DEBUG_OUTPUTS']:
            # log progress (writing debug outputs)
            WLOG(params, '', TextEntry('40-014-00029'))
            # in file
            shapel_in_fp_file = recipe.outputs['SHAPEL_IN_FP_FILE']
            debugfile1 = shapel_in_fp_file.newcopy(recipe=recipe)
            debugfile1.construct_filename(params, infile=infile)
            debugfile1.copy_hdict(outfile)
            debugfile1.add_hkey('KW_OUTPUT', value=debugfile1.name)
            debugfile1.data = image
            debugfile1.write()
            # out file
            shapel_out_fp_file = recipe.outputs['SHAPEL_OUT_FP_FILE']
            debugfile2 = shapel_out_fp_file.newcopy(recipe=recipe)
            debugfile2.construct_filename(params, infile=infile)
            debugfile2.copy_hdict(outfile)
            debugfile2.add_hkey('KW_OUTPUT', value=debugfile2.name)
            debugfile2.data = image2
            debugfile2.write()

        # ----------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ----------------------------------------------------------------------
        if passed:
            # add shapel transforms
            drs_database.add_file(params, outfile)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return dict(locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # exit message if in debug mode
    core.end(ll, has_plots=True)

# =============================================================================
# End of code
# =============================================================================
