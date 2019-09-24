#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-09-19 at 13:16

@author: cook
"""
from __future__ import division
import numpy as np

from terrapipe import core
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_database
from terrapipe.io import drs_fits
from terrapipe.science.calib import flat_blaze
from terrapipe.science.calib import wave
from terrapipe.science import extract
from terrapipe.science import velocity

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_ccf_spirou.py'
__INSTRUMENT__ = 'SPIROU'
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
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
    Main function for cal_extract_spirou.py

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
        # get header from file instance
        header = infile.header
        # ------------------------------------------------------------------
        # check that file has valid DPRTYPE
        # ------------------------------------------------------------------
        dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
        # if dprtype is incorrect skip
        if dprtype not in params.listp('CCF_ALLOWED_DPRTYPES'):
            # join allowed dprtypes
            allowed_dprtypes = ', '.join(params.listp('CCF_ALLOWED_DPRTYPES'))
            # log that we are skipping
            wargs = [dprtype, recipe.name, allowed_dprtypes, infile.basename]
            WLOG(params, 'warning', TextEntry('10-019-00001', args=wargs))
            # continue
            continue
        # flag whether calibration fiber is FP
        has_fp =  dprtype.upper().split('_')[1] == 'FP'
        # ------------------------------------------------------------------
        # get fiber from infile
        fiber = infile.get_fiber(header=header)
        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        bprops = extract.get_berv(params, infile, dprtype=dprtype)
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe, header, fiber=fiber,
                                       infile=infile)
        # ------------------------------------------------------------------
        # Get blaze
        # ------------------------------------------------------------------
        blazefile, blaze = flat_blaze.get_blaze(params, header, fiber)

        # ------------------------------------------------------------------
        #   Remove domain with telluric > 50%
        # ------------------------------------------------------------------
        outtype = infile.get_key('KW_OUTPUT', dtype=str)

        if outtype in params['CCF_CORRECT_TELLU_TYPES']:
            # remove telluric domain below a defined threshold
            #    and return the infile (with infile.data updated)
            targs = [infile, fiber]
            image = velocity.remove_telluric_domain(params, recipe, *targs)
        else:
            image = infile.data

        # ------------------------------------------------------------------
        #   Remove and fill NaN values (with smooth convolved values)
        # ------------------------------------------------------------------
        image = velocity.fill_e2ds_nans(params, image)

        # ------------------------------------------------------------------
        # Compute CCF on science channel
        # ------------------------------------------------------------------
        cargs = [image, blaze, wprops, bprops, fiber]
        rv_props1 = velocity.compute_ccf_science(params, *cargs)

        # ------------------------------------------------------------------
        # Compute CCF on reference fiber (FP only)
        # ------------------------------------------------------------------
        # TODO: Add code here

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        # TODO: Add code here

        # ------------------------------------------------------------------
        # archive ccf to table
        # ------------------------------------------------------------------
        # TODO: Add code here

        # ------------------------------------------------------------------
        # archive ccf from science fiber
        # ------------------------------------------------------------------
        # TODO: Add code here

        # ------------------------------------------------------------------
        # archive ccf from reference fiber
        # ------------------------------------------------------------------
        # TODO: Add code here

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
    core.post_main(ll['params'], has_plots=True)

# =============================================================================
# End of code
# =============================================================================
