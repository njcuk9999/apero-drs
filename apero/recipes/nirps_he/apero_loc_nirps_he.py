#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_loc_nirps_he.py [obs dir] [files]

APERO localisation calibration recipe for NIRPS HE

Created on 2019-05-14 at 09:40

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_startup
from apero.science.calib import gen_calib
from apero.science.calib import localisation

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_loc_nirps_he.py'
__INSTRUMENT__ = 'NIRPS_HE'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict

# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(obs_dir: Optional[str] = None, files: Optional[List[str]] = None,
         **kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_loc

    :param obs_dir: string, the night name sub-directory
    :param files: list of strings or string, the list of files to process
    :param kwargs: any additional keywords

    :type obs_dir: str
    :type files: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(obs_dir=obs_dir, files=files, **kwargs)
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


def __main__(recipe: DrsRecipe, params: ParamDict) -> Dict[str, Any]:
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe: DrsRecipe, the recipe class using this function
    :param params: ParamDict, the parameter dictionary of constants

    :return: dictionary containing the local variables
    """
    # ----------------------------------------------------------------------
    # Main Code
    # ----------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # check qc
    if 'files' in params['DATA_DICT']:
        infiles = params['DATA_DICT']['files']
    else:
        # get files
        infiles = params['INPUTS']['FILES'][1]
    # check the quality control from input files
    infiles = drs_file.check_input_qc(params, infiles, 'files')
    # loc is run twice we need to check that all input files can be used
    #  together and we are not mixing both types
    infiles = drs_file.check_input_dprtypes(params, recipe, infiles)
    # get list of filenames (for output)
    rawfiles = []
    for infile in infiles:
        rawfiles.append(infile.basename)
    # deal with input data from function
    if 'files' in params['DATA_DICT']:
        rawfiles = params['DATA_DICT']['rawfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        cond = drs_file.combine(params, recipe, infiles, math='median',
                                same_type=False)
        infiles = [cond[0]]
        combine = True
    else:
        combine = False
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
        # ------------------------------------------------------------------
        # set up plotting (no plotting before this)
        recipe.plot.set_location(it)
        # print file iteration progress
        drs_startup.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.get_header()
        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = gen_calib.calibrate_ppfile(params, recipe, infile,
                                                  database=calibdbm)
        # ------------------------------------------------------------------
        # Identify fiber type
        # ------------------------------------------------------------------
        # get pconst
        pconst = constants.pload()
        # identify fiber type based on data type
        fiber = pconst.FIBER_DPRTYPE(dprtype=props['DPRTYPE'])
        if fiber is None:
            eargs = [props['DPRTYPE'], recipe.name, 'FLAT_DARK or DARK_FLAT',
                     infile.basename]
            WLOG(params, 'error', textentry('00-013-00001', args=eargs))
            fiber = None

        # set a flag for fiber type in logging
        science_fiber, _ = pconst.FIBER_KINDS()
        if fiber in science_fiber:
            log1.update_flags(SCIFIBER=True)
        else:
            log1.update_flags(REFFIBER=True)
        # ------------------------------------------------------------------
        # Construct image order_profile
        # ------------------------------------------------------------------
        order_profile = localisation.calculate_order_profile(params, image)
        # ------------------------------------------------------------------
        # Localization of orders on central column
        # ------------------------------------------------------------------
        # find and fit localisation
        _fibers = pconst.FIBER_LOCALISATION(fiber)
        ldict = dict()
        for _fiber in _fibers:
            lout = localisation.calc_localisation(params, recipe, image, _fiber)
            ldict[_fiber] = lout
        # deal with merging coefficients and formatting for use as they
        #   were in older codes (may be redundant in future)
        m_out = localisation.merge_coeffs(params, ldict, image.shape[1])
        cent_coeffs, wid_coeffs, fibername = m_out
        # ------------------------------------------------------------------
        # Localisation stats (for header and quality control)
        # ------------------------------------------------------------------
        lprops = localisation.loc_stats(params, fiber, cent_coeffs, wid_coeffs,
                                        order_profile)
        # ------------------------------------------------------------------
        # Plot the image and fit points
        # ------------------------------------------------------------------
        # plot image above saturation threshold
        # plot first and final fit over image
        recipe.plot('LOC_IMAGE_FIT', image=image, coeffs=cent_coeffs,
                    kind=fibername, width_coeffs=wid_coeffs)
        recipe.plot('LOC_IM_CORNER', image=image, params=params,
                    coeffs=cent_coeffs, width_coeffs=wid_coeffs)
        # ------------------------------------------------------------------
        # Plot of RMS for positions and widths
        # ------------------------------------------------------------------
        # recipe.plot('LOC_ORD_VS_RMS', rnum=rorder_num, fiber=fiber,
        #             rms_center=cent_rms, rms_fwhm=wid_rms)

        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        qc_params, passed = localisation.loc_quality_control(params, lprops)
        # update recipe log
        log1.add_qc(qc_params, passed)

        # ------------------------------------------------------------------
        # write files
        # ------------------------------------------------------------------
        fargs = [infile, image, rawfiles, combine, fiber, props, order_profile,
                 lprops, qc_params]
        outfiles = localisation.write_localisation_files(params, recipe, *fargs)
        orderpfile, loco1file = outfiles

        # ------------------------------------------------------------------
        # Move to calibDB and update calibDB
        # ------------------------------------------------------------------
        if passed and params['INPUTS']['DATABASE']:
            # copy the order profile to the calibDB
            calibdbm.add_calib_file(orderpfile)
            # copy the loco file to the calibDB
            calibdbm.add_calib_file(loco1file)
        # ---------------------------------------------------------------------
        # if recipe is a reference and QC fail we generate an error
        # ---------------------------------------------------------------------
        if not passed and params['INPUTS']['REF']:
            eargs = [recipe.name]
            WLOG(params, 'error', textentry('09-000-00011', args=eargs))
        # ------------------------------------------------------------------
        # Summary plots
        # ------------------------------------------------------------------
        recipe.plot('SUM_LOC_IM_FIT', image=image, coeffs=cent_coeffs,
                    kind=fibername, width_coeffs=wid_coeffs)
        recipe.plot('SUM_LOC_IM_CORNER', image=image, params=params,
                    coeffs=cent_coeffs, width_coeffs=wid_coeffs)
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        localisation.loc_summary(recipe, it, params, qc_params, props, lprops)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end()

    # ----------------------------------------------------------------------
    # End of main code
    # ----------------------------------------------------------------------
    return locals()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # run main with no arguments (get from command line - sys.argv)
    ll = main()

# =============================================================================
# End of code
# =============================================================================
