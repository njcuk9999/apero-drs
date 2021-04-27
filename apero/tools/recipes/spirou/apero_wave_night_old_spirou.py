#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-12-18 at 16:57

@author: cook
"""
from apero.base import base
from apero import lang
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.core import drs_database
from apero.io import drs_image
from apero.science.calib import gen_calib
from apero.science.calib import flat_blaze
from apero.science.calib import wave_old
from apero.science import velocity
from apero.science.extract import other as extractother


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_wave_night_old_spirou.py'
__INSTRUMENT__ = 'SPIROU'
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
EXTRACT_NAME = 'apero_extract_spirou.py'


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(obs_dir=None, hcfiles=None, fpfiles=None, **kwargs):
    """
    Main function for apero_wave_night_spirou.py

    :param obs_dir: string, the night name sub-directory
    :param hcfiles: list of strings or string, the list of hc files
    :param fpfiles: list of strings or string, the list of fp files
    :param kwargs: any additional keywords

    :type obs_dir: str
    :type hcfiles: list[str]
    :type fpfiles: list[str]

    :keyword debug: int, debug level (0 for None)
    :keyword fpfiles: list of strings or string, the list of fp files (optional)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(obs_dir=obs_dir, hcfiles=hcfiles,
                   fpfiles=fpfiles, **kwargs)
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
    hcfiles = params['INPUTS']['HCFILES'][1]
    # deal with (optional fp files)
    if len(params['INPUTS']['FPFILES']) == 0:
        fpfiles = None
    else:
        fpfiles = params['INPUTS']['FPFILES'][1]
        # must check fp files pass quality control
        fpfiles = gen_calib.check_fp_files(params, fpfiles)
    # get list of filenames (for output)
    rawhcfiles, rawfpfiles = [], []
    for infile in hcfiles:
        rawhcfiles.append(infile.basename)
    # deal with (optional fp files)
    if fpfiles is not None:
        for infile in fpfiles:
            rawfpfiles.append(infile.basename)

    # deal with input hc/fp data from function
    if 'hcfiles' in params['DATA_DICT'] and 'fpfiles' in params['DATA_DICT']:
        hcfiles = params['DATA_DICT']['hcfiles']
        fpfiles = params['DATA_DICT']['fpfiles']
        rawhcfiles = params['DATA_DICT']['rawhcfiles']
        rawfpfiles = params['DATA_DICT']['rawfpfiles']
        combine = params['DATA_DICT']['combine']
    # combine input images if required
    elif params['INPUT_COMBINE_IMAGES']:
        # get combined file
        cond1 = drs_file.combine(params, recipe, hcfiles, math='median')
        hcfiles = [cond1[0]]
        cond2 = drs_file.combine(params, recipe, fpfiles, math='median')
        fpfiles = [cond2[0]]
        combine = True
    else:
        combine = False

    # get the number of infiles
    num_files = len(hcfiles)

    # warn user if lengths differ
    if len(hcfiles) != len(fpfiles):
        wargs = [len(hcfiles), len(fpfiles)]
        WLOG(params, 'error', textentry('10-017-00002', args=wargs))
    # get the number of files
    num_files = len(hcfiles)
    # get the fiber types from a list parameter (or from inputs)
    fiber_types = drs_image.get_fiber_types(params)
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
        # get this iterations files
        hcfile = hcfiles[it]
        fpfile = fpfiles[it]
        # ------------------------------------------------------------------
        # extract the hc file and fp file
        # ------------------------------------------------------------------
        # set up parameters
        eargs = [params, recipe, EXTRACT_NAME, hcfile, fpfile]
        # run extraction
        hc_outputs, fp_outputs = extractother.extract_wave_files(*eargs)

        # set up a stored cavity width
        indcavity = None
        indsource = None
        # ------------------------------------------------------------------
        # Loop around fibers
        # ------------------------------------------------------------------
        for fiber in fiber_types:
            # ------------------------------------------------------------------
            # add level to recipe log
            log2 = log1.add_level(params, 'fiber', fiber)
            # ------------------------------------------------------------------
            # log fiber process
            drs_startup.fiber_processing_update(params, fiber)
            # get hc and fp outputs
            hc_e2ds_file = hc_outputs[fiber]
            fp_e2ds_file = fp_outputs[fiber]
            # --------------------------------------------------------------
            # get master hc lines and fp lines from calibDB
            wargs = []
            wout = wave_old.get_wavelines(params, recipe, fiber,
                                          infile=hc_e2ds_file, database=calibdbm)
            mhclines, mhclsource, mfplines, mfplsource = wout
            # --------------------------------------------------------------
            # load wavelength solution (start point) for this fiber
            #    this should only be a master wavelength solution
            wprops = wave_old.get_wavesolution(params, recipe,
                                               infile=hc_e2ds_file,
                                               fiber=fiber, master=True,
                                               forcefiber=True,
                                               database=calibdbm)
            # --------------------------------------------------------------
            # define the header as being from the hc e2ds file
            hcheader = hc_e2ds_file.get_header()
            # load the blaze file for this fiber
            blaze_file, blaze = flat_blaze.get_blaze(params, hcheader, fiber,
                                                     database=calibdbm)
            # --------------------------------------------------------------
            # calculate the night wavelength solution
            wargs = [hc_e2ds_file, fp_e2ds_file, mhclines, mfplines,
                     wprops['WAVEMAP'], wprops['WAVEFILE'], fiber, indcavity]
            nprops = wave_old.night_wavesolution(params, recipe, *wargs)
            # update in dcavity
            if indcavity is None:
                indcavity = nprops['DCAVITY']
                indsource = fiber
            # add dcavity source (which fiber it came from)
            nprops['DCAVITYSRCE'] = indsource
            nprops.set_source('DCAVITYSRCE', mainname)
            # ----------------------------------------------------------
            # ccf computation
            # ----------------------------------------------------------
            # # get the FP (reference) fiber
            # pconst = constants.pload(params['INSTRUMENT'])
            # sfiber, rfiber = pconst.FIBER_CCF()
            # compute the ccf
            ccfargs = [fp_e2ds_file, fp_e2ds_file.get_data(), blaze,
                       nprops['WAVEMAP'], fiber]
            rvprops = velocity.compute_ccf_fp(params, recipe, *ccfargs)

            # merge rvprops into llprops (shallow copy)
            nprops.merge(rvprops)
            # update ccf properties for wave solution
            nprops['WFP_DRIFT'] = rvprops['MEAN_RV']
            nprops['WFP_FWHM'] = rvprops['MEAN_FWHM']
            nprops['WFP_CONTRAST'] = rvprops['MEAN_CONTRAST']
            nprops['WFP_MASK'] = rvprops['CCF_MASK']
            nprops['WFP_LINES'] = rvprops['TOT_LINE']
            nprops['WFP_TARG_RV'] = rvprops['TARGET_RV']
            nprops['WFP_WIDTH'] = rvprops['CCF_WIDTH']
            nprops['WFP_STEP'] = rvprops['CCF_STEP']
            nprops['WFP_FILE'] = wprops['WAVEFILE']
            # add the rv stats
            rvprops['RV_WAVEFILE'] = wprops['WAVEFILE']
            rvprops['RV_WAVETIME'] = wprops['WAVETIME']
            rvprops['RV_WAVESRCE'] = wprops['WAVESOURCE']
            rvprops['RV_TIMEDIFF'] = 'None'
            rvprops['RV_WAVE_FP'] = rvprops['MEAN_RV']
            rvprops['RV_SIMU_FP'] = 'None'
            rvprops['RV_DRIFT'] = 'None'
            rvprops['RV_OBJ'] = 'None'
            rvprops['RV_CORR'] = 'None'
            # set sources
            rkeys = ['RV_WAVEFILE', 'RV_WAVETIME', 'RV_WAVESRCE', 'RV_TIMEDIFF',
                     'RV_WAVE_FP', 'RV_SIMU_FP', 'RV_DRIFT', 'RV_OBJ',
                     'RV_CORR']
            wkeys = ['WFP_DRIFT', 'WFP_FWHM', 'WFP_CONTRAST', 'WFP_MASK',
                     'WFP_LINES', 'WFP_TARG_RV', 'WFP_WIDTH', 'WFP_STEP',
                     'WFP_FILE']
            nprops.set_sources(wkeys, 'velocity.compute_ccf_fp()')
            rvprops.set_sources(rkeys, mainname)
            # ----------------------------------------------------------
            # wave solution quality control
            # ----------------------------------------------------------
            qc_params, passed = wave_old.night_quality_control(params, nprops)
            # update recipe log
            log2.add_qc(qc_params, passed)

            # ----------------------------------------------------------
            # write wave solution to file
            # ----------------------------------------------------------
            wargs = [nprops, hc_e2ds_file, fp_e2ds_file, fiber, combine,
                     rawhcfiles, rawfpfiles, qc_params, wprops['WAVEINST']]
            wavefile, nprops = wave_old.night_write_wavesolution(params, recipe,
                                                                 *wargs)

            # ----------------------------------------------------------
            # Update calibDB with solution
            # ----------------------------------------------------------
            if passed and params['INPUTS']['DATABASE']:
                # copy the hc wave solution file to the calibDB
                calibdbm.add_calib_file(wavefile)

            # ----------------------------------------------------------
            # Update header of current files with FP solution
            # ----------------------------------------------------------
            if passed and params['INPUTS']['DATABASE']:
                # update the e2ds and s1d files for hc
                newhce2ds = wave_old.update_extract_files(params, recipe,
                                                          hc_e2ds_file, nprops,
                                                          EXTRACT_NAME, fiber,
                                                          calibdbm=calibdbm)
                # update the e2ds and s1d files for fp
                #  we returrn the fp e2ds file as it has an updated header
                newfpe2ds = wave_old.update_extract_files(params, recipe,
                                                          fp_e2ds_file, nprops,
                                                          EXTRACT_NAME, fiber,
                                                          calibdbm=calibdbm)
            # else just get the e2ds file from the current fp file
            else:
                newfpe2ds = fp_e2ds_file

            # ----------------------------------------------------------
            # write CCF from rv props
            # ----------------------------------------------------------
            # need to use the updated header in newfpe2ds
            velocity.write_ccf(params, recipe, newfpe2ds, rvprops, rawfpfiles,
                               combine, qc_params, fiber)

            # ----------------------------------------------------------
            # update recipe log file for fp fiber
            # ----------------------------------------------------------
            log2.end()

        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        log1.end()

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
