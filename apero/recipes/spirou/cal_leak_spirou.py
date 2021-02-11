#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-07-05 at 16:46

@author: cook
"""
from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.core import drs_database
from apero.science.extract import general as extgen


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_leak_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# define extraction code to use
EXTRACT_NAME = 'cal_extract_spirou.py'


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
    Main function for cal_leak_spirou.py

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
    return drs_startup.end_main(params, llmain, recipe, success)


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
    # get allowed infile types
    allowed_filetypes = params.listp('ALLOWED_LEAK_TYPES', dtype=str)
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
        infiles = [drs_file.combine(params, recipe, infiles, math='median')]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)
    # get this instruments science fibers and reference fiber
    pconst = constants.pload()
    # science fibers should be list of strings, reference fiber should be string
    sci_fibers, ref_fiber =  pconst.FIBER_KINDS()
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
        # ------------------------------------------------------------------
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
        # ------------------------------------------------------------------
        # get this iterations file
        infile = infiles[it]
        # ------------------------------------------------------------------
        # Deal with wrong DPRTYPE
        # ------------------------------------------------------------------
        # get dprtype
        dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
        # only correction OBJ_FP
        if dprtype not in allowed_filetypes:
            # print warning
            wargs = [dprtype, ', '.join(allowed_filetypes), infile.filename]
            WLOG(params, 'warning', textentry('10-016-00021', args=wargs))
            # update recipe log file
            log1.end(params)
            # continue to next file
            continue
        # ------------------------------------------------------------------
        # Deal with wrong fiber
        # ------------------------------------------------------------------
        # get fiber
        fiber = infile.get_hkey('KW_FIBER', dtype=str)
        # only correct a science fiber
        if fiber not in sci_fibers:
            # print warning
            wargs = [fiber, ', '.join(sci_fibers), infile.filename]
            WLOG(params, 'warning', textentry('10-016-00022', args=wargs))
            # update recipe log file
            log1.end(params)
            # continue to next file
            continue
        # ------------------------------------------------------------------
        # Check for previous correction
        # ------------------------------------------------------------------
        # TODO: Eventually this should be required
        leakcorr = infile.get_hkey('KW_LEAK_CORR', required=False)
        if leakcorr is not None:
            if leakcorr in ['True', True, 1, '1']:
                # print warning
                wargs = [infile.filename]
                WLOG(params, 'warning', textentry('10-016-00023', args=wargs))
                # update recipe log file
                log1.end(params)
                # continue to next file
                continue

        # ------------------------------------------------------------------
        # Get all extracted file instances associated with infile
        # ------------------------------------------------------------------
        ext_outputs = extgen.get_extraction_files(params, recipe, infile,
                                                  EXTRACT_NAME)

        # ------------------------------------------------------------------
        # Add debugs for all uncorrected file
        # ------------------------------------------------------------------
        extgen.save_uncorrected_ext_fp(params, ext_outputs)

        # ------------------------------------------------------------------
        # Correct with dark fp
        # ------------------------------------------------------------------
        cprops = extgen.correct_dark_fp(params, ext_outputs, database=calibdbm)

        # ------------------------------------------------------------------
        # Re-calculate s1d files
        # ------------------------------------------------------------------
        cprops = extgen.dark_fp_regen_s1d(params, recipe, cprops,
                                          database=calibdbm)

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        qc_params, passed = extgen.qc_leak(params, cprops)
        log1.add_qc(params, qc_params[fiber], passed)

        # ------------------------------------------------------------------
        # Write updated extracted files
        # ------------------------------------------------------------------
        extgen.write_leak(params, recipe, ext_outputs, cprops, qc_params)

        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end(params)

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return drs_startup.return_locals(params, locals())


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
