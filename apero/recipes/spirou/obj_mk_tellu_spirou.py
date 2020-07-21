#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
obj_mk_tellu [night_directory] [files]

Creates a flattened transmission spectrum from a hot star observation.
The continuum is set to 1 and regions with too many tellurics for continuum
estimates are set to NaN and should not used for RV. Overall, the domain with
a valid transmission mask corresponds to the YJHK photometric bandpasses.
The transmission maps have the same shape as e2ds files. Ultimately, we will
want to retrieve a transmission profile for the entire nIR domain for generic
science that may be done in the deep water bands. The useful domain for RV
measurements will (most likely) be limited to the domain without very strong
absorption, so the output transmission files meet our pRV requirements in
terms of wavelength coverage. Extension of the transmission maps to the
domain between photometric bandpasses is seen as a low priority item.

Usage:
  obj_mk_tellu night_name telluric_file_name.fits


Outputs:
  telluDB: TELL_MAP file - telluric transmission map for input file
        file also saved in the reduced folder
        input file + '_trans.fits'

  telluDB: TELL_CONV file - convolved molecular file (for specific
                            wavelength solution) if it doesn't already exist
        file also saved in the reduced folder
        wavelength solution + '_tapas_convolved.npy'

Created on 2019-09-03 at 14:58

@author: cook
"""
import numpy as np

from apero import core
from apero import lang
from apero.core import constants
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.science.calib import wave
from apero.science import extract
from apero.science import telluric

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'obj_mk_tellu_spirou.py'
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
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict


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
    Main function for obj_mk_tellu_spirou.py

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
        infiles = [drs_fits.combine(params, recipe, infiles, math='median')]
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
        # get this iterations file
        infile = infiles[it]
        # get header from file instance
        header = infile.header
        # get image
        image = infile.data
        # ------------------------------------------------------------------
        # check that file has valid DPRTYPE
        # ------------------------------------------------------------------
        dprtype = infile.get_key('KW_DPRTYPE', dtype=str)
        # if dprtype is incorrect skip
        if dprtype not in params.listp('TELLU_ALLOWED_DPRTYPES'):
            # join allowed dprtypes
            allowed_dprtypes = ', '.join(params.listp('TELLU_ALLOWED_DPRTYPES'))
            # log that we are skipping
            wargs = [dprtype, recipe.name, allowed_dprtypes, infile.basename]
            WLOG(params, 'warning', TextEntry('10-019-00001', args=wargs))
            # end log correctly
            log1.end(params)
            # continue
            continue
        # ------------------------------------------------------------------
        # check that file objname is not in blacklist / is in whitelist
        # ------------------------------------------------------------------
        objname = infile.get_key('KW_OBJNAME', dtype=str)
        # get black list
        blacklist, _ = telluric.get_blacklist(params)
        whitelist, _ = telluric.get_whitelist(params)
        # if objname in blacklist then skip
        if objname in blacklist:
            # log that we are skipping
            wargs = [infile.basename, params['KW_OBJNAME'][0], objname]
            WLOG(params, 'warning', TextEntry('10-019-00002', args=wargs))
            # end log correctly
            log1.end(params)
            # continue
            continue
        elif objname not in whitelist:
            # log that we are skipping
            args = [objname]
            WLOG(params, 'warning', TextEntry('10-019-00009', args=args))
            # end log correctly
            log1.end(params)
            # continue
            continue
        else:
            # log that file is validated
            args = [objname, dprtype]
            WLOG(params, 'info', TextEntry('40-019-00048', args=args))
        # ------------------------------------------------------------------
        # get fiber from infile
        fiber = infile.get_fiber(header=header)
        # ------------------------------------------------------------------
        # load master wavelength solution for this fiber
        # get pseudo constants
        pconst = constants.pload(params['INSTRUMENT'])
        # deal with fibers that we don't have
        usefiber = pconst.FIBER_WAVE_TYPES(fiber)
        # ------------------------------------------------------------------
        # load master wavelength solution
        mprops = wave.get_wavesolution(params, recipe, header, master=True,
                                       fiber=fiber, infile=infile)
        # ------------------------------------------------------------------
        # load wavelength solution for this fiber
        wprops = wave.get_wavesolution(params, recipe, header, fiber=fiber,
                                       infile=infile)

        # ------------------------------------------------------------------
        # telluric pre-cleaning
        # ------------------------------------------------------------------
        tpreprops = telluric.tellu_preclean(params, recipe, infile, wprops,
                                            fiber, rawfiles, combine)
        # get variables out of tpreprops
        image1 = tpreprops['CORRECTED_E2DS']
        # ------------------------------------------------------------------
        # Normalize image by peak blaze
        # ------------------------------------------------------------------
        nargs = [image1, header, fiber]
        image, nprops = telluric.normalise_by_pblaze(params, *nargs)
        # ------------------------------------------------------------------
        # Get barycentric corrections (BERV)
        # ------------------------------------------------------------------
        bprops = extract.get_berv(params, infile, dprtype=dprtype)
        # ------------------------------------------------------------------
        # Get template file (if available)
        # ------------------------------------------------------------------
        tout = telluric.load_templates(params, header, objname, fiber)
        template, template_file = tout
        # ------------------------------------------------------------------
        # Calculate telluric absorption
        # ------------------------------------------------------------------
        cargs = [recipe, image1, template, template_file, header, mprops,
                 wprops, bprops, tpreprops]
        tellu_props = telluric.calculate_tellu_res_absorption(params, *cargs)
        # ------------------------------------------------------------------
        # Quality control
        # ------------------------------------------------------------------
        pargs = [tellu_props, infile, tpreprops]
        qc_params, passed = telluric.mk_tellu_quality_control(params, *pargs)
        # update recipe log
        log1.add_qc(params, qc_params, passed)

        # ------------------------------------------------------------------
        # Save transmission map to file
        # ------------------------------------------------------------------
        targs = [infile, rawfiles, fiber, combine, mprops,
                 nprops, tellu_props, tpreprops, qc_params]
        transfile = telluric.mk_tellu_write_trans_file(params, recipe, *targs)
        # ------------------------------------------------------------------
        # Add transmission map to telluDB
        # ------------------------------------------------------------------
        if np.all(qc_params[3]):
            # copy the transmission map to telluDB
            drs_database.add_file(params, transfile)
        # ------------------------------------------------------------------
        # Construct summary document
        # ------------------------------------------------------------------
        telluric.mk_tellu_summary(recipe, it, params, qc_params, tellu_props,
                                  fiber)
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
