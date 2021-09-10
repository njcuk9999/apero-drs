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
from apero.io import drs_image
from apero.science.calib import flat_blaze
from apero.science.calib import gen_calib
from apero.science.calib import localisation
from apero.science.calib import shape
from apero.science.calib import wave
from apero.science import extract

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_extract_nirps_ha.py'
__INSTRUMENT__ = 'NIRPS_HA'
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
    Main function for apero_extract_spirou.py

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
        cond = drs_file.combine(params, recipe, infiles, math='median')
        infiles = [cond[0]]
        combine = True
    else:
        combine = False
    # get the number of infiles
    num_files = len(infiles)

    # get quick look mode
    quicklook = params['EXT_QUICK_LOOK']
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

        # ------------------------------------------------------------------
        # deal with skipping files defined by inputs OBJNAME and DPRTYPE
        skip, skip_conditions = gen_calib.check_files(params, infile)
        if skip:
            if 'DPRTYPE' in skip_conditions[0]:
                wargs = skip_conditions[1]
                WLOG(params, 'warning', textentry('10-016-00012', args=wargs))
            if 'OBJNAME' in skip_conditions[0]:
                wargs = skip_conditions[2]
                WLOG(params, 'warning', textentry('10-016-00013', args=wargs))
            # write log here
            log1.write_logfile()
            # skip this file
            continue
        # ------------------------------------------------------------------
        # get header from file instance
        header = infile.get_header()
        # get the fiber types needed
        fibertypes = drs_image.get_fiber_types(params)
        # ------------------------------------------------------------------
        # Load shape components
        # ------------------------------------------------------------------
        shapexfile, shapex = shape.get_shapex(params, header, database=calibdbm)
        shapeyfile, shapey = shape.get_shapey(params, header, database=calibdbm)
        shapelocalfile, shapelocal = shape.get_shapelocal(params, header,
                                                          database=calibdbm)

        # ------------------------------------------------------------------
        # Correction of file
        # ------------------------------------------------------------------
        props, image = gen_calib.calibrate_ppfile(params, recipe, infile,
                                                  database=calibdbm)

        # ------------------------------------------------------------------
        # Load and straighten order profiles
        # ------------------------------------------------------------------
        sargs = [infile, fibertypes, shapelocal, shapex, shapey,
                 shapelocalfile]
        orderps, orderpfiles = extract.order_profiles(params, recipe, *sargs,
                                                      database=calibdbm)

        # ------------------------------------------------------------------
        # Apply shape transformations
        # ------------------------------------------------------------------
        # log progress (straightening orderp)
        WLOG(params, 'info', textentry('40-016-00004'))
        # straighten image
        image2 = shape.ea_transform(params, image, shapelocal, dxmap=shapex,
                                    dymap=shapey)
        # ------------------------------------------------------------------
        # Calculate Barycentric correction
        # ------------------------------------------------------------------
        if not quicklook:
            bprops = extract.get_berv(params, infile, header)
        else:
            bprops = None

        # storage for return
        e2dsoutputs = dict()
        # ------------------------------------------------------------------
        # Fiber loop
        # ------------------------------------------------------------------
        # loop around fiber types
        for fiber in fibertypes:
            # ------------------------------------------------------------------
            # add level to recipe log
            log2 = log1.add_level(params, 'fiber', fiber)
            # ------------------------------------------------------------------
            # log process: processing fiber
            wargs = [fiber, ', '.join(fibertypes)]
            WLOG(params, 'info', textentry('40-016-00014', args=wargs))
            # --------------------------------------------------------------
            # load wavelength solution for this fiber
            if not quicklook:
                wprops = wave.get_wavesolution(params, recipe, header,
                                               fiber=fiber,
                                               database=calibdbm,
                                               nbpix=image.shape[1])
            else:
                wprops = ParamDict()
            # --------------------------------------------------------------
            # load the localisation properties for this fiber
            lprops = localisation.get_coefficients(params, recipe, header,
                                                   fiber=fiber, merge=True,
                                                   database=calibdbm)
            # get the localisation center coefficients for this fiber
            lcoeffs = lprops['CENT_COEFFS']
            # shift the coefficients
            lcoeffs2 = shape.ea_transform_coeff(image2, lcoeffs, shapelocal)
            # --------------------------------------------------------------
            # load the flat file for this fiber
            flat_file, flat = flat_blaze.get_flat(params, header, fiber,
                                                  database=calibdbm)
            # --------------------------------------------------------------
            # load the blaze file for this fiber
            blaze_file, blaze = flat_blaze.get_blaze(params, header, fiber,
                                                     database=calibdbm)
            # --------------------------------------------------------------
            # get the number of frames used
            nframes = infile.numfiles
            # --------------------------------------------------------------
            # get the order profile for this fiber
            orderp = orderps[fiber]
            orderpfile = orderpfiles[fiber]
            # --------------------------------------------------------------
            # log progress: extracting image
            WLOG(params, 'info', textentry('40-016-00011'))
            # extract spectrum
            eprops = extract.extract2d(params, image2, orderp, lcoeffs2,
                                       nframes, props, fiber=fiber)
            # leak correction
            eprops = extract.manage_leak_correction(params, eprops, infile,
                                                    fiber)
            # flat correction for e2dsff
            eprops = extract.flat_blaze_correction(eprops, flat, blaze)
            # --------------------------------------------------------------
            if not quicklook:
                s1dextfile = params['EXT_S1D_INTYPE']
                # create 1d spectra (s1d) of the e2ds file
                sargs = [wprops['WAVEMAP'], eprops[s1dextfile], eprops['BLAZE']]
                swprops = extract.e2ds_to_s1d(params, recipe, *sargs,
                                              wgrid='wave', fiber=fiber,
                                              s1dkind=s1dextfile)
                svprops = extract.e2ds_to_s1d(params, recipe, *sargs,
                                              wgrid='velocity', fiber=fiber,
                                              s1dkind=s1dextfile)
            else:
                swprops, svprops = None,  None

            # --------------------------------------------------------------
            # Plots
            # --------------------------------------------------------------
            sorder = params['EXTRACT_PLOT_ORDER']
            # plot (in a loop) order fit + e2ds (on original image)
            recipe.plot('FLAT_ORDER_FIT_EDGES1', params=params, image1=image,
                        image2=image2, order=None, coeffs1=lcoeffs,
                        coeffs2=lcoeffs2, fiber=fiber)
            # plot for sorder order fit + e2ds (on original image)
            recipe.plot('FLAT_ORDER_FIT_EDGES2', params=params, image1=image,
                        image2=image2, order=sorder, coeffs1=lcoeffs,
                        coeffs2=lcoeffs2, fiber=fiber)
            # plot non-quick look graphs
            if not quicklook:
                # plot (in a loop) the fitted blaze and calculated flat with the
                #     e2ds image
                recipe.plot('EXTRACT_SPECTRAL_ORDER1', order=None,
                            eprops=eprops,
                            wave=wprops['WAVEMAP'], fiber=fiber)
                # plot for sorder the fitted blaze and calculated flat with the
                #     e2ds image
                recipe.plot('EXTRACT_SPECTRAL_ORDER2', order=sorder,
                            eprops=eprops,
                            wave=wprops['WAVEMAP'], fiber=fiber)
                # plot the s1d plot
                recipe.plot('EXTRACT_S1D', params=params, props=svprops,
                            fiber=fiber, kind='E2DSFF')
            # --------------------------------------------------------------
            # Quality control
            # --------------------------------------------------------------
            qc_params, passed = extract.qc_extraction(params, eprops)
            # update recipe log
            log2.add_qc(qc_params, passed)

            # --------------------------------------------------------------
            # write files
            # --------------------------------------------------------------
            if quicklook:
                fargs = [params, recipe, infile, rawfiles, combine, fiber,
                         orderpfile, props, lprops, eprops, shapelocalfile,
                         shapexfile, shapeyfile, shapelocal, flat_file,
                         blaze_file, qc_params]
                outfiles = extract.write_extraction_files_ql(*fargs)
                e2dsfile, e2dsfffile = outfiles
            else:
                fargs = [params, recipe, infile, rawfiles, combine, fiber,
                         orderpfile, props, lprops, wprops, eprops, bprops,
                         swprops, svprops, shapelocalfile, shapexfile,
                         shapeyfile, shapelocal, flat_file, blaze_file,
                         qc_params]
                outfiles = extract.write_extraction_files(*fargs)
                e2dsfile, e2dsfffile = outfiles

            # --------------------------------------------------------------
            # create fplines file for required fibers
            # --------------------------------------------------------------
            if not quicklook:
                rargs = [e2dsfile, wprops['WAVEMAP'], fiber]
                rfpl = extract.ref_fplines(params, recipe, *rargs,
                                           database=calibdbm)
                # write rfpl file
                if rfpl is not None:
                    rargs = [rfpl, e2dsfile, e2dsfile, fiber, 'EXT_FPLINES']
                    wave.write_fplines(params, recipe, *rargs)

            # --------------------------------------------------------------
            # add files to outputs
            # --------------------------------------------------------------
            if not quicklook:
                ekeys = ['E2DS', 'E2DSFF']
                efiles = [e2dsfile, e2dsfffile]
                # loop around keys to add
                for key, efile in zip(ekeys, efiles):
                    # construct output key
                    outkey = '{0}_{1}'.format(key, fiber)
                    # copy file to dictionary
                    e2dsoutputs[outkey] = efile.completecopy(efile)
            # ------------------------------------------------------------------
            # Summary plots
            # ------------------------------------------------------------------
            if not quicklook:
                sorder = params['EXTRACT_PLOT_ORDER']
                # plot (in a loop) order fit + e2ds (on original image)
                recipe.plot('SUM_FLAT_ORDER_FIT_EDGES', params=params,
                            image1=image, image2=image2, order=sorder,
                            coeffs1=lcoeffs, coeffs2=lcoeffs2, fiber=fiber)
                # plot for sorder the fitted blaze and calculated flat with the
                #     e2ds image
                recipe.plot('SUM_EXTRACT_SP_ORDER', order=sorder,
                            wave=wprops['WAVEMAP'], eprops=eprops, fiber=fiber)
                # plot the s1d plot
                recipe.plot('SUM_EXTRACT_S1D', params=params, props=svprops,
                            fiber=fiber)
            # ------------------------------------------------------------------
            # Construct summary document
            # ------------------------------------------------------------------
            if not quicklook:
                extract.extract_summary(recipe, params, qc_params, e2dsfile,
                                        shapelocal, eprops, fiber)
            # ------------------------------------------------------------------
            # update recipe log file
            # ------------------------------------------------------------------
            log2.end()

        # construct summary (outside fiber loop)
        if not quicklook:
            recipe.plot.summary_document(it)

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
