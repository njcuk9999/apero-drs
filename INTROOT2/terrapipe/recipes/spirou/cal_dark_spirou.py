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
from terrapipe.io import drs_image
from terrapipe.science.calib import dark


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_dark_spirou.py'
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
    Main function for cal_dark_spirou.py

    :param directory: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

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
        # get data from file instance
        image = np.array(infile.data)
        # ------------------------------------------------------------------
        # Get basic image properties
        # ------------------------------------------------------------------
        # get image readout noise
        sigdet = infile.get_key('KW_RDNOISE')
        # get expsoure time
        exptime = infile.get_key('KW_EXPTIME')
        # get gain
        gain = infile.get_key('KW_GAIN')
        # get data type
        dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
        # ------------------------------------------------------------------
        # Dark exposure time check
        # ------------------------------------------------------------------
        # log the Dark exposure time
        WLOG(params, 'info', 'Dark Time = {0:.3f} s'.format(exptime))
        # Quality control: make sure the exposure time is longer than
        #                  qc_dark_time
        if exptime < params['QC_DARK_TIME']:
            emsg = 'Dark exposure time too short (< {0:.1f} s)'
            WLOG(params, 'error', emsg.format(params['QC_DARK_TIME']))
        # ------------------------------------------------------------------
        # Resize and rotate image
        # ------------------------------------------------------------------
        # convert NaNs to zeros
        nanmask = ~np.isfinite(image)
        image0 = np.where(nanmask, np.zeros_like(image), image)
        # resize blue image
        bkwargs = dict(xlow=params['IMAGE_X_BLUE_LOW'],
                       xhigh=params['IMAGE_X_BLUE_HIGH'],
                       ylow=params['IMAGE_Y_BLUE_LOW'],
                       yhigh=params['IMAGE_Y_BLUE_HIGH'])
        imageblue = drs_image.resize(params, image0, **bkwargs)
        # resize red image
        bkwargs = dict(xlow=params['IMAGE_X_RED_LOW'],
                       xhigh=params['IMAGE_X_RED_HIGH'],
                       ylow=params['IMAGE_Y_RED_LOW'],
                       yhigh=params['IMAGE_Y_RED_HIGH'])
        imagered = drs_image.resize(params, image0, **bkwargs)
        # ------------------------------------------------------------------
        # Dark Measurement
        # ------------------------------------------------------------------
        # Log that we are doing dark measurement
        WLOG(params, '', TextEntry('40-011-00001'))
        # measure dark for whole frame
        out1 = dark.measure_dark(params, image, '40-011-00003')
        hist_full, med_full, dadead_full = out1
        # measure dark for blue part
        out2 = dark.measure_dark(params, imageblue, '40-011-00004')
        hist_blue, med_blue, dadead_blue = out2
        # measure dark for rede part
        out3 = dark.measure_dark(params, imagered, '40-011-00005')
        hist_red, med_red, dadead_red = out3
        # ------------------------------------------------------------------
        # Identification of bad pixels
        # ------------------------------------------------------------------
        # Question bad pixel detection is done in cal_BAD_pix
        # Question:   shouldn't this be used instead of a separate badpix here?
        out = dark.measure_dark_badpix(params, image, nanmask)
        baddark, dadeadall = out
        # ------------------------------------------------------------------
        # Plots
        # ------------------------------------------------------------------
        # TODO: fill in plot section

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        # set passed variable and fail message list
        fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
        textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
        # ------------------------------------------------------------------
        # check that med < qc_max_darklevel
        if med_full > params['QC_MAX_DARKLEVEL']:
            # add failed message to fail message list
            fargs = [med_full, params['QC_MAX_DARKLEVEL']]
            fail_msg.append(textdict['40-011-00008'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(med_full)
        qc_names.append('MED_FULL')
        qc_logic.append('MED_FULL > {0:.2f}'.format(params['QC_MAX_DARKLEVEL']))
        # ------------------------------------------------------------------
        # check that fraction of dead pixels < qc_max_dead
        if dadeadall > params['QC_MAX_DEAD']:
            # add failed message to fail message list
            fargs = [dadeadall, params['QC_MAX_DEAD']]
            fail_msg.append(textdict['40-011-00009'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(dadeadall)
        qc_names.append('DADEADALL')
        qc_logic.append('DADEADALL > {0:.2f}'.format(params['QC_MAX_DEAD']))
        # ----------------------------------------------------------------------
        # checl that the precentage of dark pixels < qc_max_dark
        if baddark > params['QC_MAX_DARK']:
            fargs = [params['DARK_CUTLIMIT'], baddark, params['QC_MAX_DARK']]
            fail_msg.append(textdict['40-011-00010'].format(*fargs))
            qc_pass.append(0)
        else:
            qc_pass.append(1)
        # add to qc header lists
        qc_values.append(baddark)
        qc_names.append('baddark')
        qc_logic.append('baddark > {0:.2f}'.format(params['QC_MAX_DARK']))
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
        # Save dark to file
        # ------------------------------------------------------------------
        # define outfile
        if dprtype == 'DARK_DARK':
            outfile = recipe.outputs['DARK_FILE'].newcopy(recipe=recipe)
        elif dprtype == 'SKY_DARK':
            outfile = recipe.outputs['SKY_FILE'].newcopy(recipe=recipe)
        else:
            outfile = None
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
        outfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='darkfile')
        # add qc parameters
        outfile.add_qckeys(qc_params)
        # add blue/red/full detector parameters
        outfile.add_hkey('KW_DARK_DEAD', value=dadead_full)
        outfile.add_hkey('KW_DARK_MED', value=med_full)
        outfile.add_hkey('KW_DARK_B_DEAD', value=dadead_blue)
        outfile.add_hkey('KW_DARK_B_MED', value=med_blue)
        outfile.add_hkey('KW_DARK_R_DEAD', value=dadead_red)
        outfile.add_hkey('KW_DARK_R_MED', value=med_red)
        # add the cut limit
        outfile.add_hkey('KW_DARK_CUT', value=params['DARK_CUTLIMIT'])
        # ------------------------------------------------------------------
        # Set to zero dark value > dark_cutlimit
        cutmask = image0 > params['DARK_CUTLIMIT']
        image0c = np.where(cutmask, np.zeros_like(image0), image0)
        # copy data
        outfile.data = image0c
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        WLOG(params, '', TextEntry('40-011-00012', args=[outfile.filename]))
        # write image to file
        outfile.write()
        # add to output files (for indexing)
        recipe.add_output_file(outfile)
        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if passed:
            drs_database.add_file(params, outfile)

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

# =============================================================================
# End of code
# =============================================================================
