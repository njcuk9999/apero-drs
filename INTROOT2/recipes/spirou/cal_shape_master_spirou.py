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
# Define the output files
DARK_MASTER_FILE = file_definitions.out_dark_master
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
    Main function for cal_badpix_spirou.py

    :param directory: string, the night name sub-directory
    :param flatfiles: list of strings or string, the list of flat files
    :param darkfiles: list of strings or string, the list of dark files
    :param kwargs: any additional keywords

    :type directory: str
    :type files: list[str]

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
    params = core.end_main(params, success)
    # return a copy of locally defined variables in the memory
    return core.get_locals(dict(locals()), llmain)


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
    params['FIBER'] = pcheck(params, 'SHAPE_MASTER_FIBER', func=mainname)
    params.set_source('FIBER', mainname)

    # get combined hcfile
    hcfile = drs_fits.combine(params, hcfiles, math='average')
    # get combined fpfile
    fpfile = drs_fits.combine(params, fpfiles, math='average')

    # get the headers (should be the header of the first file in each)
    hcheader = hcfile.header
    fpheader = fpfile.header
    # get calibrations for this data
    drs_database.copy_calibrations(params, fpheader)
    drs_database.copy_calibrations(params, hcheader)

    # ------------------------------------------------------------------
    # Correction of fp file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', TextEntry('40-014-00001'))
    # calibrate file
    fpprops, fpimage = general.calibrate_ppfile(params, recipe, fpfile)

    # ------------------------------------------------------------------
    # Correction of hc file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', TextEntry('40-014-00002'))
    # calibrate file
    hcprops, hcimage = general.calibrate_ppfile(params, recipe, hcfile)

    # ----------------------------------------------------------------------
    # Get all preprocessed fp files
    # ----------------------------------------------------------------------
    # get all "filetype" filenames
    fargs = [fpprops['DPRTYPE'], params['ALLOWED_FP_TYPES']]
    filenames = drs_fits.find_filetypes(params, *fargs)
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
    # Get localisation coefficients for fp file
    # ----------------------------------------------------------------------
    lprops = localisation.get_coefficients(params, recipe, fpheader)

    # ----------------------------------------------------------------------
    # Get wave coefficients from master wavefile
    # ----------------------------------------------------------------------
    # get master wave filename
    mwavefile = wave.get_masterwave_filename(params)
    # get master wave map
    wprops = wave.get_wavesolution(params, recipe, filename=mwavefile)

    # ----------------------------------------------------------------------
    # Calculate dx shape map
    # ----------------------------------------------------------------------
    dxmap = shape.calculate_dxmap(params, hcimage, master_fp, wprops, lprops)


    # ----------------------------------------------------------------------
    # Calculate dy shape map
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Need to straighten the dxmap
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Need to straighten the hc data and fp data for debug
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Plotting
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Quality control
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Writing DXMAP to file
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Writing DYMAP to file
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Writing Master FP to file
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Writing DEBUG files
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------

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
