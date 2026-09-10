#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_loc_spirou.py [obs dir] [files]

APERO localisation calibration recipe for SPIROU

Created on 2019-05-14 at 09:40

@author: cook
"""
from aperocore.base import base
from aperocore.constants import param_functions
from aperocore.constants import load_functions
import apero as apero_pkg
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_startup
from apero.science.calib import gen_calib
from apero.science.calib import localisation
from apero.instruments import select

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_loc_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = apero_pkg.__NAME__
__version__ = apero_pkg.__version__
__authors__ = apero_pkg.__authors__
__date__ = apero_pkg.__date__
__release__ = apero_pkg.__release__
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# Get the text types
textentry = drs_lang.textentry
# alias pcheck
pcheck = param_functions.PCheck(wlog=WLOG)


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(obs_dir=None, files=None, **kwargs):
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
    # check qc
    if 'files' in params['DATA_DICT']:
        infiles = params['DATA_DICT']['files']
    else:
        # get files
        infiles = params['INPUTS']['FILES'][1]
    # check the quality control from input files
    infiles = drs_file.check_input_qc(params, infiles, 'files')
    # get pseudo constants (shared by every fiber group below)
    pconst = load_functions.load_pconfig(select.INSTRUMENTS)
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params, recipe.shortname)
    calibdbm.load_db()
    # ----------------------------------------------------------------------
    # group input files by the fiber group they illuminate - DARK_FLAT
    #   illuminates the reference fiber (e.g. C) and FLAT_DARK illuminates
    #   the science fiber pair (e.g. AB) - both groups are now supplied in
    #   a single call so one combined loc calibration file can be produced
    #   (covering all fibers) instead of running this recipe once per fiber
    # ----------------------------------------------------------------------
    fiber_groups = dict()
    for infile in infiles:
        dprtype = infile.get_hkey('KW_DPRTYPE', dtype=str)
        fiber = pconst.FIBER_DPRTYPE(dprtype=dprtype)
        if fiber is None:
            eargs = [dprtype, recipe.name, 'FLAT_DARK or DARK_FLAT',
                     infile.basename]
            raise AperoCodedException(params, '00-013-00001', targs=eargs)
        fiber_groups.setdefault(fiber, []).append(infile)
    # fiber kinds used to flag science/reference fiber in the recipe log
    science_fiber, _ = pconst.FIBER_KINDS()
    # ----------------------------------------------------------------------
    # storage for each fiber groups outputs (used to write the combined
    #    localisation file once all fiber groups have been processed)
    all_infiles, all_images, all_rawfiles = dict(), dict(), dict()
    all_combine, all_props, all_orderps = dict(), dict(), dict()
    all_lprops, all_qc_params, all_passed = dict(), dict(), dict()
    # ----------------------------------------------------------------------
    # Loop around fiber groups (e.g. AB from FLAT_DARK, C from DARK_FLAT)
    # ----------------------------------------------------------------------
    fibers = sorted(fiber_groups.keys())
    for group_num, fiber in enumerate(fibers):
        group_infiles = fiber_groups[fiber]
        # ------------------------------------------------------------------
        # add level to recipe log
        log1 = recipe.log.add_level(params, 'num', group_num)
        # set a flag for fiber type in logging
        if fiber in science_fiber:
            log1.update_flags(SCIFIBER=True)
        else:
            log1.update_flags(REFFIBER=True)
        # ------------------------------------------------------------------
        # set up plotting (no plotting before this)
        recipe.plot.set_location(group_num)
        # print file iteration progress
        drs_startup.file_processing_update(params, group_num, len(fibers))
        # get list of filenames (for output)
        rawfiles = [group_infile.basename for group_infile in group_infiles]
        # ------------------------------------------------------------------
        # combine this fiber group's input images - a single combined image
        #   per fiber group is required to build the combined loc file
        if params['IMAGE.COMBINE_INPUT']:
            cond = drs_file.combine(params, recipe, group_infiles,
                                    math='median')
            infile = cond[0]
            combine = True
        elif len(group_infiles) == 1:
            infile = group_infiles[0]
            combine = False
        else:
            wargs = [fiber, len(group_infiles)]
            WLOG(params, 'error', 'LOC recipe requires combine=True when '
                                  'more than one {0} file is provided (got '
                                  '{1} files)'.format(*wargs))
            infile, combine = group_infiles[0], False
        # get header from file instance
        header = infile.get_header()
        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = gen_calib.calibrate_ppfile(params, recipe, infile,
                                                  database=calibdbm)
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
        # Summary plots
        # ------------------------------------------------------------------
        recipe.plot('SUM_LOC_IM_FIT', image=image, coeffs=cent_coeffs,
                    kind=fibername, width_coeffs=wid_coeffs)
        recipe.plot('SUM_LOC_IM_CORNER', image=image, params=params,
                    coeffs=cent_coeffs, width_coeffs=wid_coeffs)
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        localisation.loc_summary(recipe, group_num, params, qc_params, props,
                                 lprops)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end()
        # ------------------------------------------------------------------
        # store this fiber group's outputs for the combined write below
        # ------------------------------------------------------------------
        all_infiles[fiber] = infile
        all_images[fiber] = image
        all_rawfiles[fiber] = rawfiles
        all_combine[fiber] = combine
        all_props[fiber] = props
        all_orderps[fiber] = order_profile
        all_lprops[fiber] = lprops
        all_qc_params[fiber] = qc_params
        all_passed[fiber] = passed

    # ----------------------------------------------------------------------
    # write the combined localisation file (order profile + position/width
    #    coefficients + superposition debug image for every fiber group)
    # ----------------------------------------------------------------------
    locofile = localisation.write_localisation_files_multi(
        params, recipe, all_infiles, all_images, all_rawfiles, all_combine,
        all_props, all_orderps, all_lprops, all_qc_params)
    # all fiber groups must pass QC before we add this file to the calibDB
    passed = all(all_passed.values())
    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if passed and params['INPUTS']['DATABASE']:
        # add one calibDB entry per fiber group - all entries point at the
        #   same physical (combined) file, downstream code reads the
        #   fiber-specific extension out of it (see localisation.
        #   get_coefficients and extract.gen_ext.order_profiles)
        for fiber in fibers:
            locofile.add_hkey('KW_FIBER', value=fiber)
            calibdbm.add_calib_file(locofile)
    # ---------------------------------------------------------------------
    # if recipe is a reference and QC fail we generate an error
    # ---------------------------------------------------------------------
    if not passed and params['INPUTS']['REF']:
        eargs = [recipe.name]
        raise AperoCodedException(params, '09-000-00011', targs=eargs)
    # ----------------------------------------------------------------------
    # Construct summary document
    # ----------------------------------------------------------------------
    recipe.plot.summary_document(0)

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
