#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

@author: cook
"""
import numpy as np

from apero.base import base
from apero import lang
from apero.core import constants
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.core import drs_database
from apero.core.utils import drs_startup
from apero.core.utils import drs_utils
from apero.io import drs_table
from apero.science.calib import gen_calib
from apero.science.calib import localisation
from apero.science.calib import wave
from apero.science.calib import shape


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_shape_ref_nirps_he.py'
__INSTRUMENT__ = 'NIRPS_HE'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
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
def main(obs_dir=None, fpfiles=None, **kwargs):
    """
    Main function for apero_shape_ref_spirou.py

    :param obs_dir: string, the night name sub-directory
    :param fpfiles: list of strings or string, the list of fp files
    :param kwargs: any additional keywords

    :type obs_dir: str
    :type fpfiles: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(obs_dir=obs_dir, fpfiles=fpfiles, **kwargs)
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
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # get pconst
    pconst = constants.pload()
    # get files
    fpfiles = params['INPUTS']['FPFILES'][1]
    # check qc
    fpfiles = drs_file.check_input_qc(params, fpfiles, 'fp files')
    # get list of filenames (for output)
    rawfpfiles = []
    # for infile in hcfiles:
    for infile in fpfiles:
        rawfpfiles.append(infile.basename)

    # set fiber we should use
    fiber = pcheck(params, 'SHAPE_REF_FIBER', func=mainname)
    # get science and reference fiber
    sci_fibers, ref_fiber = pconst.FIBER_KINDS()

    # get combined fpfile
    cout = drs_file.combine(params, recipe, fpfiles, math='median')
    fpfile = cout[0]

    # get the headers (should be the header of the first file in each)
    fpheader = fpfile.get_header()
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()

    # ----------------------------------------------------------------------
    # Get localisation coefficients for fp file
    # ----------------------------------------------------------------------
    lprops_sci = localisation.get_coefficients(params, fpheader, sci_fibers[0],
                                               database=calibdbm)
    lprops_ref = localisation.get_coefficients(params, fpheader, ref_fiber,
                                               database=calibdbm)

    # ----------------------------------------------------------------------
    # Get wave coefficients from reference wavefile
    # ----------------------------------------------------------------------
    # get reference wave map
    # wprops = wave.get_wavesolution(params, recipe, fiber=fiber, reference=True,
    #                                database=calibdbm)

    # ------------------------------------------------------------------
    # Correction of fp file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', textentry('40-014-00001'))
    # calibrate file
    fpprops, fpimage = gen_calib.calibrate_ppfile(params, recipe, fpfile,
                                                  correctback=False)

    # ----------------------------------------------------------------------
    # Get all preprocessed fp files
    # ----------------------------------------------------------------------
    # check file type
    filetype = fpprops['DPRTYPE']
    if filetype not in params.listp('ALLOWED_FP_TYPES', dtype=str):
        emsg = textentry('01-001-00020', args=[filetype, mainname])
        for allowedtype in params.listp('ALLOWED_FP_TYPES', dtype=str):
            emsg += '\n\t - "{0}"'.format(allowedtype)
        WLOG(params, 'error', emsg)
    # get all "filetype" filenames
    filenames = drs_utils.find_files(params, block_kind='tmp',
                                     filters=dict(KW_DPRTYPE=filetype))
    # convert to numpy array
    filenames = np.array(filenames)

    # ----------------------------------------------------------------------
    # Obtain FP reference (from file or calculate)
    # ----------------------------------------------------------------------
    # deal with having a fp reference assigned by user
    cond1 = 'FPREF' in params['INPUTS']
    # if we have fpref defined in inputs load from file - DEBUG ONLY
    if cond1 and (params['INPUTS']['FPREF'] not in [None, 'None', '']):
        # can use from calibDB by setting to 1 or True
        if params['INPUTS']['FPREF'] in ['1', 'True']:
            filename = None
        else:
            filename = params['INPUTS']['FPREF'][0][0]
        # do stuff
        fpkwargs = dict(header=fpfile.get_header(), filename=filename,
                        database=calibdbm)
        # read fpref file
        reffp_file, REF_FP = shape.get_ref_fp(params, **fpkwargs)
        # read table
        fp_table = drs_table.read_table(params, reffp_file, fmt='fits')
    else:
        # ----------------------------------------------------------------------
        # Get all fp file properties
        # ----------------------------------------------------------------------
        fp_table = shape.construct_fp_table(params, filenames)
        # ----------------------------------------------------------------------
        # match files by date and median to produce reference fp
        # ----------------------------------------------------------------------
        cargs = [params, recipe, fpprops['DPRTYPE'], fp_table, fpimage]
        # fpcube, fp_table = shape.construct_REF_FP(*cargs)
        REF_FP, fp_table = shape.construct_ref_fp(*cargs)
        # log process (reference construction complete + number of groups added)
        # wargs = [len(fpcube)]
        # WLOG(params, 'info', textentry('40-014-00011', args=wargs))
        # sum the cube to make fp data
        # REF_FP = np.sum(fpcube, axis=0)

    # ----------------------------------------------------------------------
    # Calculate dx shape map
    # ----------------------------------------------------------------------

    # calculate the dx map for fiber A
    cargs_a = [REF_FP, lprops_sci]
    dout = shape.calculate_dxmap_nirpshe(params, recipe, *cargs_a, fiber='A')
    # TODO use max_dxmap_std, max_dxmap_info, dxrms as in spirou (QC?)
    dxmap_a, max_dxmap_std_a, max_dxmap_info_a, dxrms_a = dout
    # calculate the dx map for fiber B
    cargs_b = [REF_FP, lprops_ref]
    dout = shape.calculate_dxmap_nirpshe(params, recipe, *cargs_b, fiber='B')
    # TODO use max_dxmap_std, max_dxmap_info, dxrms as in spirou (QC?)
    dxmap_b, max_dxmap_std_b, max_dxmap_info_b, dxrms_b = dout
    # TODO: Question do we just sum dxmap_a and dxmap_b?
    dxmap = dxmap_a + dxmap_b

    # ----------------------------------------------------------------------
    # Calculate dy shape map
    # ----------------------------------------------------------------------
    dymap = shape.calculate_dymap(params, REF_FP, fpheader)

    # ----------------------------------------------------------------------
    # Need to straighten the dxmap
    # ----------------------------------------------------------------------
    # copy it first
    dxmap0 = np.array(dxmap)
    # straighten dxmap
    dxmap = shape.ea_transform(params, dxmap, dymap=dymap)

    # ----------------------------------------------------------------------
    # Need to straighten the hc data and fp data for debug
    # ----------------------------------------------------------------------
    # log progress (applying transforms)
    WLOG(params, '', textentry('40-014-00025'))
    # apply the dxmap and dymap
    fpimage2 = shape.ea_transform(params, fpimage, dxmap=dxmap, dymap=dymap)

    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    qc_params, passed = shape.shape_ref_qc(params)
    # update recipe log
    recipe.log.add_qc(qc_params, passed)

    # ------------------------------------------------------------------
    # write files
    # ------------------------------------------------------------------
    fargs = [fpfile, None, rawfpfiles, None, dxmap, dymap, REF_FP,
             fp_table, fpprops, dxmap0, fpimage, fpimage2, None, None,
             qc_params]
    outfiles = shape.write_shape_ref_files(params, recipe, *fargs)
    outfile1, outfile2, outfile3 = outfiles

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if passed and params['INPUTS']['DATABASE']:
        # add dxmap
        calibdbm.add_calib_file(outfile1)
        # add dymap
        calibdbm.add_calib_file(outfile2)
        # add reference fp file
        calibdbm.add_calib_file(outfile3)
    # ---------------------------------------------------------------------
    # if recipe is a reference and QC fail we generate an error
    # ---------------------------------------------------------------------
    if not passed:
        eargs = [recipe.name]
        WLOG(params, 'error', textentry('09-000-00011', args=eargs))
    # ------------------------------------------------------------------
    # Construct summary document
    # ------------------------------------------------------------------
    shape.write_shape_ref_summary(recipe, params, fp_table, qc_params)
    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    recipe.log.end()

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
