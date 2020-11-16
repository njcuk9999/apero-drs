#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2020-03-02 at 17:26

@author: cook
"""
from apero.base import base
from apero import lang
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
from apero.core.core import drs_database
from apero.science.extract import other as extother
from apero.science.extract import general as extgen


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_leak_master_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# define extraction code to use
EXTRACT_NAME = 'cal_extract_nirps_ha.py'


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
    Main function for cal_leak_master_spirou.py

    :param kwargs: any additional keywords

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
    # extract file type from inputs
    filetypes = params['INPUTS'].listp('FILETYPE', dtype=str)
    # get allowed dark types
    allowedtypes = params.listp('ALLOWED_LEAKM_TYPES', dtype=str)
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    # ----------------------------------------------------------------------
    # Get all dark_fp files for directory
    # ----------------------------------------------------------------------
    infiles, rawfiles = [], []
    # check file type
    for filetype in filetypes:
        # ------------------------------------------------------------------
        # check whether filetype is in allowed types
        if filetype not in allowedtypes:
            emsg = textentry('01-001-00020', args=[filetype, mainname])
            for allowedtype in allowedtypes:
                emsg += '\n\t - "{0}"'.format(allowedtype)
            WLOG(params, 'error', emsg)
        # ------------------------------------------------------------------
        # check whether filetype is allowed for instrument
        # get definition
        fdkwargs = dict(instrument=params['INSTRUMENT'], kind='tmp',
                        required=False)
        darkfpfile = drs_startup.get_file_definition(filetype, **fdkwargs)
        # deal with defintion not found
        if darkfpfile is None:
            eargs = [filetype, recipe.name, mainname]
            WLOG(params, 'error', textentry('09-010-00001', args=eargs))
        # ------------------------------------------------------------------
        # get all "filetype" filenames
        files = drs_utils.find_files(params, kind='tmp',
                                    filters=dict(KW_DPRTYPE=filetype,
                                                 DIRECTORY=params['NIGHTNAME']))
        # create infiles
        for filename in files:
            infile = darkfpfile.newcopy(filename=filename, params=params)
            infile.read_file()
            infiles.append(infile)
            rawfiles.append(infile.basename)
    # get the number of infiles
    num_files = len(infiles)
    # ----------------------------------------------------------------------
    # Deal with no files found (use master)
    if num_files == 0:
        # log that no dark fp were found for this night
        wargs = [params['NIGHTNAME']]
        WLOG(params, 'warning', textentry('10-016-00025', args=wargs))
        # update recipe log file
        recipe.log.end(params)
        # End of main code
        return drs_startup.return_locals(params, locals())
    # ----------------------------------------------------------------------
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # set up storage cube
    dark_fp_storage = dict()
    # set up storage of cprops (have to assume cprops constant for loop)
    cprops = None
    # ----------------------------------------------------------------------
    # Loop around input files
    # ----------------------------------------------------------------------
    for it in range(num_files):
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.get_header()
        # ------------------------------------------------------------------
        # Get the dark_fp output e2ds filename and extract/read file
        # ------------------------------------------------------------------
        eargs = [params, recipe, EXTRACT_NAME, infile]
        darkfp_extfiles = extother.extract_leak_files(*eargs)
        # get list of basename for dark fp extracted files
        darkfp_extnames = []
        for fiber in darkfp_extfiles:
            darkfp_extnames.append(darkfp_extfiles[fiber].basename)
        # ------------------------------------------------------------------
        # Process the extracted dark fp files for this extract
        # ------------------------------------------------------------------
        # print progress
        wargs = [', '.join(darkfp_extnames)]
        WLOG(params, '', textentry('40-016-00024', args=wargs))
        # correct dark fp
        cout = extgen.correct_master_dark_fp(params, darkfp_extfiles)
        dark_fp_extcorr, cprops = cout
        # ------------------------------------------------------------------
        # add to storage
        for fiber in dark_fp_extcorr:
            if fiber in dark_fp_storage:
                dark_fp_storage[fiber].append(dark_fp_extcorr[fiber])
            else:
                dark_fp_storage[fiber] = [dark_fp_extcorr[fiber]]

    # ------------------------------------------------------------------
    # Produce super dark fp from median of all extractions
    # ------------------------------------------------------------------
    medcubes = extgen.master_dark_fp_cube(params, recipe, dark_fp_storage)
    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    # TODO: Need to add some QC
    qc_params, passed = extgen.qc_leak_master(params, medcubes)
    # ------------------------------------------------------------------
    # Write super dark fp to file
    # ------------------------------------------------------------------
    # TODO: Need to add some parameters to header
    medcubes = extgen.write_leak_master(params, recipe, rawfiles, medcubes,
                                        qc_params, cprops)
    # ------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ------------------------------------------------------------------
    if passed:
        # loop around fibers
        for fiber in medcubes:
            # get outfile
            outfile = medcubes[fiber]
            # copy the order profile to the calibDB
            calibdbm.add_calib_file(outfile)
    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    recipe.log.end(params)
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
