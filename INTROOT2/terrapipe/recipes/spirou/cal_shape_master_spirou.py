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
__NAME__ = 'cal_shape_master_spirou.py'
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
def main(directory=None, hcfiles=None, fpfiles=None, **kwargs):
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
    fkwargs = dict(directory=directory, hcfiles=hcfiles,
                   fpfiles=fpfiles, **kwargs)
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
    return core.end_main(params, llmain, recipe, success)


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
    # get files
    hcfiles = params['INPUTS']['HCFILES'][1]
    fpfiles = params['INPUTS']['FPFILES'][1]
    # get list of filenames (for output)
    rawhcfiles, rawfpfiles = [], []
    for infile in hcfiles:
        rawhcfiles.append(infile.basename)
    for infile in fpfiles:
        rawfpfiles.append(infile.basename)

    # set fiber we should use
    fiber = pcheck(params, 'SHAPE_MASTER_FIBER', func=mainname)

    # get combined hcfile
    hcfile = drs_fits.combine(params, hcfiles, math='median')
    # get combined fpfile
    fpfile = drs_fits.combine(params, fpfiles, math='median')

    # get the headers (should be the header of the first file in each)
    hcheader = hcfile.header
    fpheader = fpfile.header
    # get calibrations for this data
    drs_database.copy_calibrations(params, fpheader)
    drs_database.copy_calibrations(params, hcheader)

    # ----------------------------------------------------------------------
    # Get localisation coefficients for fp file
    # ----------------------------------------------------------------------
    lprops = localisation.get_coefficients(params, recipe, fpheader, fiber)

    # ----------------------------------------------------------------------
    # Get wave coefficients from master wavefile
    # ----------------------------------------------------------------------
    # get master wave filename
    mwavefile = wave.get_masterwave_filename(params, fiber)
    # get master wave map
    wprops = wave.get_wavesolution(params, recipe, filename=mwavefile)

    # ------------------------------------------------------------------
    # Correction of fp file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', TextEntry('40-014-00001'))
    # calibrate file
    fpprops, fpimage = general.calibrate_ppfile(params, recipe, fpfile,
                                                correctback=False)

    # ------------------------------------------------------------------
    # Correction of hc file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', TextEntry('40-014-00002'))
    # calibrate file
    hcprops, hcimage = general.calibrate_ppfile(params, recipe, hcfile,
                                                correctback=False)

    # ----------------------------------------------------------------------
    # Get all preprocessed fp files
    # ----------------------------------------------------------------------
    # check file type
    filetype = fpprops['DPRTYPE']
    if filetype not in params['ALLOWED_FP_TYPES']:
        emsg = TextEntry('01-001-00020', args=[filetype, mainname])
        for allowedtype in params['ALLOWED_FP_TYPES']:
            emsg += '\n\t - "{0}"'.format(allowedtype)
        WLOG(params, 'error', emsg)
    # get all "filetype" filenames
    filenames = drs_fits.find_files(params, kind='tmp', KW_DPRTYPE=filetype)
    # convert to numpy array
    filenames = np.array(filenames)

    # ----------------------------------------------------------------------
    # Get all fp file properties
    # ----------------------------------------------------------------------
    fp_table = shape.construct_fp_table(params, filenames)

    # ----------------------------------------------------------------------
    # match files by date and median to produce master fp
    # ----------------------------------------------------------------------
    cargs = [params, recipe, fpprops['DPRTYPE'], fp_table, fpimage]
    fpcube, fp_table = shape.construct_master_fp(*cargs)

    # log process (master construction complete + number of groups added)
    wargs = [len(fpcube)]
    WLOG(params, 'info', TextEntry('40-014-00011', args=wargs))
    # sum the cube to make fp data
    master_fp = np.sum(fpcube, axis=0)

    # ----------------------------------------------------------------------
    # Calculate dx shape map
    # ----------------------------------------------------------------------
    dout = shape.calculate_dxmap(params, hcimage, master_fp, wprops, lprops)
    dxmap, max_dxmap_std, max_dxmap_info = dout
    # if dxmap is None we shouldn't continue as quality control have failed
    if dxmap is None:
        fargs = [max_dxmap_info[0], max_dxmap_info[1], max_dxmap_std,
                 max_dxmap_info[2]]
        WLOG(params, 'warning', TextEntry('10-014-00003', args=fargs))
        # return a copy of locally defined variables in the memory
        return core.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # Calculate dy shape map
    # ----------------------------------------------------------------------
    dymap = shape.calculate_dymap(params, recipe, master_fp, fpheader)

    # ----------------------------------------------------------------------
    # Need to straighten the dxmap
    # ----------------------------------------------------------------------
    # copy it first
    dxmap0 = np.array(dxmap)
    # straighten dxmap
    dxmap = shape.ea_transform(params, dxmap, dymap=dymap)

    # ----------------------------------------------------------------------
    # Need to straighten the hc data and fp data for debug
    # ----------------------------------------------------------------------
    # log progress (applying transforms)
    WLOG(params, '', TextEntry('40-014-00025'))
    # apply the dxmap and dymap
    hcimage2 = shape.ea_transform(params, hcimage, dxmap=dxmap, dymap=dymap)
    fpimage2 = shape.ea_transform(params, fpimage, dxmap=dxmap, dymap=dymap)

    # ----------------------------------------------------------------------
    # Plotting
    # ----------------------------------------------------------------------
    if params['DRS_PLOT'] > 0:
        # TODO fill in plot section
        # # plots setup: start interactive plot
        # sPlt.start_interactive_session(p)
        # # plot the shape process for one order
        # sPlt.slit_shape_angle_plot(p, loc)
        # # end interactive section
        # sPlt.end_interactive_session(p)
        pass

    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    # TODO: Decide on some extra quality control?
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # no quality control currently
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
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

    # ----------------------------------------------------------------------
    # Writing DXMAP to file
    # ----------------------------------------------------------------------
    # define outfile
    outfile1 = recipe.outputs['DXMAP_FILE'].newcopy(recipe=recipe)
    # construct the filename from file instance
    outfile1.construct_filename(params, infile=fpfile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    outfile1.copy_original_keys(fpfile)
    # add version
    outfile1.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    outfile1.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    outfile1.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    outfile1.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    outfile1.add_hkey('KW_OUTPUT', value=outfile1.name)
    # add input files (and deal with combining or not combining)
    outfile1.add_hkey_1d('KW_INFILE1', values=rawhcfiles, dim1name='hcfiles')
    outfile1.add_hkey_1d('KW_INFILE2', values=rawfpfiles, dim1name='fpfiles')
    # add the calibration files use
    outfile1 = general.add_calibs_to_header(outfile1, fpprops)
    # add qc parameters
    outfile1.add_qckeys(qc_params)
    # copy data
    outfile1.data = dxmap
    # ------------------------------------------------------------------
    # log that we are saving dxmap to file
    WLOG(params, '', TextEntry('40-014-00026', args=[outfile1.filename]))
    # write image to file
    outfile1.write_multi(data_list=[fp_table])
    # add to output files (for indexing)
    recipe.add_output_file(outfile1)
    # ----------------------------------------------------------------------
    # Writing DYMAP to file
    # ----------------------------------------------------------------------
    # define outfile
    outfile2 = recipe.outputs['DYMAP_FILE'].newcopy(recipe=recipe)
    # construct the filename from file instance
    outfile2.construct_filename(params, infile=fpfile)
    # copy header from outfile1
    outfile2.copy_hdict(outfile1)
    # set output key
    outfile2.add_hkey('KW_OUTPUT', value=outfile2.name)
    # copy data
    outfile2.data = dymap
    # log that we are saving dymap to file
    WLOG(params, '', TextEntry('40-014-00027', args=[outfile2.filename]))
    # write image to file
    outfile2.write_multi(data_list=[fp_table])
    # add to output files (for indexing)
    recipe.add_output_file(outfile2)
    # ----------------------------------------------------------------------
    # Writing Master FP to file
    # ----------------------------------------------------------------------
    # define outfile
    outfile3 = recipe.outputs['FPMASTER_FILE'].newcopy(recipe=recipe)
    # construct the filename from file instance
    outfile3.construct_filename(params, infile=fpfile)
    # copy header from outfile1
    outfile3.copy_hdict(outfile1)
    # set output key
    outfile3.add_hkey('KW_OUTPUT', value=outfile3.name)
    # copy data
    outfile3.data = master_fp
    # log that we are saving master_fp to file
    WLOG(params, '', TextEntry('40-014-00028', args=[outfile3.filename]))
    # write image to file
    outfile3.write_multi(data_list=[fp_table])
    # add to output files (for indexing)
    recipe.add_output_file(outfile3)
    # ----------------------------------------------------------------------
    # Writing DEBUG files
    # ----------------------------------------------------------------------
    if params['SHAPE_DEBUG_OUTPUTS']:
        # log progress (writing debug outputs)
        WLOG(params, '', TextEntry('40-014-00029'))
        # ------------------------------------------------------------------
        # deal with the unstraighted dxmap
        # ------------------------------------------------------------------
        debugfile0 = recipe.outputs['SHAPE_BDXMAP_FILE'].newcopy(recipe=recipe)
        debugfile0.construct_filename(params, infile=fpfile)
        debugfile0.copy_hdict(outfile1)
        debugfile0.add_hkey('KW_OUTPUT', value=debugfile0.name)
        debugfile0.data = dxmap0
        debugfile0.write_multi(data_list=[fp_table])
        # add to output files (for indexing)
        recipe.add_output_file(debugfile0)
        # ------------------------------------------------------------------
        # for the fp files take the header from outfile1
        # ------------------------------------------------------------------
        # in file
        debugfile1 = recipe.outputs['SHAPE_IN_FP_FILE'].newcopy(recipe=recipe)
        debugfile1.construct_filename(params, infile=fpfile)
        debugfile1.copy_hdict(outfile1)
        debugfile1.add_hkey('KW_OUTPUT', value=debugfile1.name)
        debugfile1.data = fpimage
        debugfile1.write_multi(data_list=[fp_table])
        # add to output files (for indexing)
        recipe.add_output_file(debugfile1)
        # out file
        debugfile2 = recipe.outputs['SHAPE_OUT_FP_FILE'].newcopy(recipe=recipe)
        debugfile2.construct_filename(params, infile=fpfile)
        debugfile2.copy_hdict(outfile1)
        debugfile2.add_hkey('KW_OUTPUT', value=debugfile2.name)
        debugfile2.data = fpimage2
        debugfile2.write_multi(data_list=[fp_table])
        # add to output files (for indexing)
        recipe.add_output_file(debugfile2)
        # ------------------------------------------------------------------
        # for hc files copy over the fp parameters with the hc parameters
        # ------------------------------------------------------------------
        # in file
        debugfile3 = recipe.outputs['SHAPE_IN_HC_FILE'].newcopy(recipe=recipe)
        debugfile3.construct_filename(params, infile=hcfile)
        debugfile3.copy_original_keys(hcfile)
        # add version
        debugfile3.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
        # add dates
        debugfile3.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
        debugfile3.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
        # add process id
        debugfile3.add_hkey('KW_PID', value=params['PID'])
        # add output tag
        debugfile3.add_hkey('KW_OUTPUT', value=debugfile3.name)
        # add input files (and deal with combining or not combining)
        debugfile3.add_hkey_1d('KW_INFILE1', values=rawhcfiles,
                               dim1name='hcfiles')
        debugfile3.add_hkey_1d('KW_INFILE2', values=rawfpfiles,
                               dim1name='fpfiles')
        # add the calibration files use
        debugfile3 = general.add_calibs_to_header(debugfile3, fpprops)
        # add qc parameters
        debugfile3.add_qckeys(qc_params)
        # add data
        debugfile3.data = hcimage
        debugfile3.write_multi(data_list=[fp_table])
        # add to output files (for indexing)
        recipe.add_output_file(debugfile3)
        # out file
        debugfile4 = recipe.outputs['SHAPE_OUT_HC_FILE'].newcopy(recipe=recipe)
        debugfile4.construct_filename(params, infile=hcfile)
        debugfile4.copy_hdict(debugfile4)
        debugfile4.add_hkey('KW_OUTPUT', value=debugfile4.name)
        debugfile4.data = hcimage2
        debugfile4.write_multi(data_list=[fp_table])
        # add to output files (for indexing)
        recipe.add_output_file(debugfile4)
    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if passed:
        # add dxmap
        drs_database.add_file(params, outfile1)
        # add dymap
        drs_database.add_file(params, outfile2)
        # add master fp file
        drs_database.add_file(params, outfile3)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return core.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()
    # Post main plot clean up
    core.post_main(ll['params'], plotting=ll['plotter'])

# =============================================================================
# End of code
# =============================================================================
