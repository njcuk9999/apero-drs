#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
apero_shape_ref_nirps_ha.py [obs dir] [HC_HC files] [FP_FP files]

APERO shape reference calibration recipe for SPIROU

Created on 2019-03-23 at 13:01

@author: cook
"""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from aperocore.base import base
from aperocore.constants import param_functions
from aperocore import drs_lang
from apero.core import drs_database
from apero.core import drs_file
from aperocore.core import drs_log
from apero.utils import drs_recipe
from apero.utils import drs_startup
from apero.utils import drs_utils
from apero.io import drs_table
from apero.science.calib import gen_calib
from apero.science.calib import localisation
from apero.science.calib import shape
from apero.science.calib import wave

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_shape_ref_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = param_functions.ParamDict
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
def main(obs_dir: Optional[str] = None, hcfiles: Optional[List[str]] = None,
         fpfiles: Optional[List[str]] = None,
         **kwargs) -> Union[Dict[str, Any], Tuple[DrsRecipe, ParamDict]]:
    """
    Main function for apero_shape_ref_spirou.py

    :param obs_dir: string, the night name sub-directory
    :param hcfiles: list of strings or string, the list of hc files
    :param fpfiles: list of strings or string, the list of fp files
    :param kwargs: any additional keywords

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
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
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # get files
    hcfiles = params['INPUTS']['HCFILES'][1]
    fpfiles = params['INPUTS']['FPFILES'][1]
    # check qc
    hcfiles = drs_file.check_input_qc(params, hcfiles, 'hc files')
    fpfiles = drs_file.check_input_qc(params, fpfiles, 'fp files')
    # get list of filenames (for output)
    rawhcfiles, rawfpfiles = [], []
    for infile in hcfiles:
        rawhcfiles.append(infile.basename)
    for infile in fpfiles:
        rawfpfiles.append(infile.basename)

    # set fiber we should use
    fiber = pcheck(params, 'SHAPE_REF_FIBER', func=mainname)

    # get combined hcfile
    cout1 = drs_file.combine(params, recipe, hcfiles, math='median')
    hcfile = cout1[0]
    # get combined fpfile
    cout2 = drs_file.combine(params, recipe, fpfiles, math='median')
    fpfile = cout2[0]

    # get the headers (should be the header of the first file in each)
    hcheader = hcfile.get_header()
    fpheader = fpfile.get_header()
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()

    # ----------------------------------------------------------------------
    # Get localisation coefficients for fp file
    # ----------------------------------------------------------------------
    lprops = localisation.get_coefficients(params, fpheader, fiber,
                                           database=calibdbm)

    # ----------------------------------------------------------------------
    # Get wave coefficients from reference wavefile
    # ----------------------------------------------------------------------
    # get reference wave map
    wprops = wave.get_wavesolution(params, recipe, fiber=fiber, ref=True,
                                   database=calibdbm, rlog=recipe.log)

    # ------------------------------------------------------------------
    # Correction of fp file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', textentry('40-014-00001'))
    # calibrate file
    fpprops, fpimage = gen_calib.calibrate_ppfile(params, recipe, fpfile,
                                                  correctback=False)

    # ------------------------------------------------------------------
    # Correction of hc file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', textentry('40-014-00002'))
    # calibrate file
    hcprops, hcimage = gen_calib.calibrate_ppfile(params, recipe, hcfile,
                                                  correctback=False)

    # ----------------------------------------------------------------------
    # Get all preprocessed fp files
    # ----------------------------------------------------------------------
    # check file type
    filetype = fpprops['DPRTYPE']
    if filetype not in params['ALLOWED_FP_TYPES']:
        emsg = textentry('01-001-00020', args=[filetype, mainname])
        for allowedtype in params['ALLOWED_FP_TYPES']:
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
        reffp_file, ref_fp = shape.get_ref_fp(params, **fpkwargs)
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
        ref_fp, fp_table = shape.construct_ref_fp(*cargs)
        # log process (reference construction complete + number of groups added)
        # wargs = [len(fpcube)]
        # WLOG(params, 'info', textentry('40-014-00011', args=wargs))
        # sum the cube to make fp data
        # ref_fp = np.sum(fpcube, axis=0)

    # ----------------------------------------------------------------------
    # Calculate dx shape map
    # ----------------------------------------------------------------------
    cargs = [hcimage, ref_fp, lprops, fiber]
    dout = shape.calculate_dxmap(params, recipe, *cargs)
    dxmap, max_dxmap_std, max_dxmap_info, dxrms = dout
    # if dxmap is None we shouldn't continue as quality control have failed
    if dxmap is None:
        fargs = [max_dxmap_info[0], max_dxmap_info[1], max_dxmap_std,
                 max_dxmap_info[2]]
        WLOG(params, 'warning', textentry('10-014-00003', args=fargs),
             sublevel=6)
        # quality control
        qc_values = [max_dxmap_std]
        qc_names = ['max_dxmap_std']
        qc_logic = ['max_dxmap_std > {0:.5f}'.format(max_dxmap_info[2])]
        qc_pass = [0]
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # update recipe log
        recipe.log.add_qc(qc_params, False)
        # ------------------------------------------------------------------
        # update recipe log file
        # ------------------------------------------------------------------
        recipe.log.end()

        # return a copy of locally defined variables in the memory
        return locals()
    else:
        # no quality control currently
        qc_values = [max_dxmap_std]
        qc_names = ['max_dxmap_std']
        qc_logic = ['max_dxmap_std > {0:.5f}'.format(max_dxmap_info[2])]
        qc_pass = [1]
        # store in qc_params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]

    # ----------------------------------------------------------------------
    # Calculate dy shape map
    # ----------------------------------------------------------------------
    dymap = shape.calculate_dymap(params, ref_fp, fpheader)

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
    hcimage2 = shape.ea_transform(params, hcimage, dxmap=dxmap, dymap=dymap)
    fpimage2 = shape.ea_transform(params, fpimage, dxmap=dxmap, dymap=dymap)

    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    qc_params, passed = shape.shape_ref_qc(params, dxrms, qc_params)
    # update recipe log
    recipe.log.add_qc(qc_params, passed)

    # ------------------------------------------------------------------
    # write files
    # ------------------------------------------------------------------
    fargs = [fpfile, hcfile, rawfpfiles, rawhcfiles, dxmap, dymap, ref_fp,
             fp_table, fpprops, dxmap0, fpimage, fpimage2, hcimage, hcimage2,
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
