#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

# CODE DESCRIPTION HERE

Created on 2019-03-05 16:38
@author: ncook
Version 0.0.1
"""
import numpy as np

from apero.base import base
from apero import lang
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_database2 as drs_database
from apero.core.instruments.spirou import file_definitions
from apero.io import drs_fits
from apero.science import preprocessing


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_pp_master_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
# Raw prefix
RAW_PREFIX = file_definitions.raw_prefix


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(directory=None, **kwargs):
    """
    Main function for cal_preprocess_spirou.py

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
    fkwargs = dict(directory=directory, **kwargs)
    # ----------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # ----------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # ----------------------------------------------------------------------
    # End Message
    # ----------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success, outputs='None')


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
    # extract file type from inputs
    filetypes = params['INPUTS'].listp('FILETYPE', dtype=str)
    # get allowed dark types
    allowedtypes = params.listp('ALLOWED_PPM_TYPES', dtype=str)
    # set up plotting (no plotting before this)
    recipe.plot.set_location()

    # ----------------------------------------------------------------------
    # Get all raw master files
    # ----------------------------------------------------------------------
    infiles, rawfiles = [], []
    # check file type
    for filetype in filetypes:
        # ------------------------------------------------------------------
        # check whether filetype is in allowed types
        if filetype not in allowedtypes:
            emsg = TextEntry('01-001-00020', args=[filetype, mainname])
            for allowedtype in allowedtypes:
                emsg += '\n\t - "{0}"'.format(allowedtype)
            WLOG(params, 'error', emsg)
        # ------------------------------------------------------------------
        # check whether filetype is allowed for instrument
        rawfiletype = 'RAW_{0}'.format(filetype)
        # get definition
        fdkwargs = dict(instrument=params['INSTRUMENT'], kind='raw',
                        required=False)
        rawfile = drs_startup.get_file_definition(rawfiletype, **fdkwargs)
        # deal with defintion not found
        if rawfile is None:
            eargs = [filetype, recipe.name, mainname]
            WLOG(params, 'error', TextEntry('09-010-00001', args=eargs))
        # ------------------------------------------------------------------
        # get all "filetype" filenames
        files = drs_fits.find_files(params, recipe, kind='raw',
                                    night=params['NIGHTNAME'],
                                    KW_DPRTYPE=filetype)
        # create infiles
        for filename in files:
            infile = rawfile.newcopy(filename=filename, recipe=recipe)
            infile.read_file()
            infiles.append(infile)
            rawfiles.append(infile.basename)

    # get combined file
    infiles = [drs_fits.combine(params, recipe, infiles, math='median')]
    # get the number of infiles
    num_files = len(infiles)
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', it)
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
        # get file for this iteration
        infile = infiles[it]
        # ------------------------------------------------------------------
        # Fix the nirps header
        # ------------------------------------------------------------------
        # certain keys may not be in some spirou files
        infile = drs_fits.fix_header(params, recipe, infile)
        # ------------------------------------------------------------------
        # print progress
        WLOG(params, '', TextEntry('40-010-00014', args=[infile.name]))
        # make order mask
        mask, props = preprocessing.nirps_order_mask(params, infile.data)
        # convert to integers
        mask = np.array(mask).astype(int)
        # ------------------------------------------------------------------
        # Save mask image
        # ------------------------------------------------------------------
        outfile = recipe.outputs['PP_MASTER'].newcopy(recipe=recipe)
        # construct out filename
        outfile.construct_filename(params, infile=infile)
        # copy keys from input file
        outfile.copy_original_keys(infile)
        # add version
        outfile.add_hkey('KW_PPVERSION', value=params['DRS_VERSION'])
        # add dates
        outfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
        outfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
        # add process id
        outfile.add_hkey('KW_PID', value=params['PID'])
        # add input filename
        outfile.add_hkey_1d('KW_INFILE1', values=rawfiles, dim1name='infile')
        # set used values from mask creation
        outfile.add_hkey('KW_PPMSTR_NSIG', value=props['PPM_MASK_NSIG'])
        # ------------------------------------------------------------------
        # copy data
        outfile.data = mask
        # ------------------------------------------------------------------
        # log that we are saving rotated image
        wargs = [outfile.filename]
        WLOG(params, '', TextEntry('40-010-00015', args=wargs))
        # write image to file
        outfile.write_file()
        # add to output files (for indexing)
        recipe.add_output_file(outfile)
        # ------------------------------------------------------------------
        # add to calibration database
        # ------------------------------------------------------------------
        # copy the mask to the calibDB
        calibdbm.add_calib_file(outfile)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end(params)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, dict(locals()))


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
