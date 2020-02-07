#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

@author: cook
"""
from apero import core
from apero import locale
from apero.core import constants
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.science.calib import general
from apero.science.calib import shape

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
    Main function for cal_shape_spirou.py

    :param directory: string, the night name sub-directory
    :param files: list of strings or string, the list of fp files
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
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', it)
        # ------------------------------------------------------------------
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
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
        targs = [params, recipe, masterfp_image, image]
        transform, xres, yres = shape.get_linear_transform_params(*targs)
        # ----------------------------------------------------------------------
        # For debug purposes straighten the image
        # ----------------------------------------------------------------------
        image2 = shape.ea_transform(params, image, transform, dxmap=dxmap,
                                    dymap=dymap)
        # ----------------------------------------------------------------------
        # Quality control
        # ----------------------------------------------------------------------
        qc_params, passed = shape.shape_local_qc(params, transform, xres, yres)
        # update recipe log
        log1.add_qc(params, qc_params, passed)

        # ------------------------------------------------------------------
        # Writing shape to file
        # ------------------------------------------------------------------
        outfile = shape.write_shape_local_files(params, recipe, infile, combine,
                                                rawfiles, props, transform,
                                                image, image2, qc_params)
        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if passed:
            # add shapel transforms
            drs_database.add_file(params, outfile)
        # ------------------------------------------------------------------
        # plot a zoom in of non-shifted vs shifted
        # ------------------------------------------------------------------
        pkwargs = dict(params=params, image=image, simage=image2)
        # debug plot
        recipe.plot('SHAPEL_ZOOM_SHIFT', **pkwargs)
        # summary plot
        recipe.plot('SUM_SHAPEL_ZOOM_SHIFT', **pkwargs)
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        shape.write_shape_local_summary(recipe, params, qc_params, it,
                                        transform)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end(params)

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
