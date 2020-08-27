#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-23 at 13:01

@author: cook
"""
import numpy as np

from apero import core
from apero import lang
from apero.core import constants
from apero.core.core import drs_database
from apero.io import drs_fits
from apero.io import drs_table
from apero.science.calib import general
from apero.science.calib import localisation
from apero.science.calib import wave
from apero.science.calib import shape


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_shape_master_spirou.py'
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
TextEntry = lang.drs_text.TextEntry
TextDict = lang.drs_text.TextDict
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
def main(directory=None, hcfiles=None, fpfiles=None, **kwargs):
    """
    Main function for cal_shape_master_spirou.py

    :param directory: string, the night name sub-directory
    :param hcfiles: list of strings or string, the list of hc files
    :param fpfiles: list of strings or string, the list of fp files
    :param kwargs: any additional keywords

    :type directory: str
    :type hcfiles: list[str]
    :type fpfiles: list[str]

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(directory=directory, hcfiles=hcfiles,
                   fpfiles=fpfiles, **kwargs)
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
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # get files
    hcfiles = params['INPUTS']['HCFILES'][1]
    fpfiles = params['INPUTS']['FPFILES'][1]
    # must check fp files pass quality control
    fpfiles = general.check_fp_files(params, fpfiles)
    # get list of filenames (for output)
    rawhcfiles, rawfpfiles = [], []
    for infile in hcfiles:
        rawhcfiles.append(infile.basename)
    for infile in fpfiles:
        rawfpfiles.append(infile.basename)

    # set fiber we should use
    fiber = pcheck(params, 'SHAPE_MASTER_FIBER', func=mainname)

    # get combined hcfile
    hcfile = drs_fits.combine(params, recipe, hcfiles, math='median')
    # get combined fpfile
    fpfile = drs_fits.combine(params, recipe, fpfiles, math='median')

    # get the headers (should be the header of the first file in each)
    hcheader = hcfile.header
    fpheader = fpfile.header
    # get calibrations for this data
    drs_database.copy_calibrations(params, fpheader)
    drs_database.copy_calibrations(params, hcheader)

    # ----------------------------------------------------------------------
    # Get localisation coefficients for fp file
    # ----------------------------------------------------------------------
    lprops = localisation.get_coefficients(params, recipe, fpheader, fiber)

    # ----------------------------------------------------------------------
    # Get wave coefficients from master wavefile
    # ----------------------------------------------------------------------
    # get master wave filename
    mwavefile = wave.get_masterwave_filename(params, fiber)
    # get master wave map
    wprops = wave.get_wavesolution(params, recipe, filename=mwavefile)

    # ------------------------------------------------------------------
    # Correction of fp file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', TextEntry('40-014-00001'))
    # calibrate file
    fpprops, fpimage = general.calibrate_ppfile(params, recipe, fpfile,
                                                correctback=False)

    # ------------------------------------------------------------------
    # Correction of hc file
    # ------------------------------------------------------------------
    # log process
    WLOG(params, 'info', TextEntry('40-014-00002'))
    # calibrate file
    hcprops, hcimage = general.calibrate_ppfile(params, recipe, hcfile,
                                                correctback=False)

    # ----------------------------------------------------------------------
    # Get all preprocessed fp files
    # ----------------------------------------------------------------------
    # check file type
    filetype = fpprops['DPRTYPE']
    if filetype not in params.listp('ALLOWED_FP_TYPES', dtype=str):
        emsg = TextEntry('01-001-00020', args=[filetype, mainname])
        for allowedtype in params.listp('ALLOWED_FP_TYPES', dtype=str):
            emsg += '\n\t - "{0}"'.format(allowedtype)
        WLOG(params, 'error', emsg)
    # get all "filetype" filenames
    filenames = drs_fits.find_files(params, recipe, kind='tmp',
                                    KW_DPRTYPE=filetype)
    # convert to numpy array
    filenames = np.array(filenames)

    # ----------------------------------------------------------------------
    # Obtain FP master (from file or calculate)
    # ----------------------------------------------------------------------
    # deal with having a fp master assigned by user
    cond1 = 'FPMASTER' in params['INPUTS']
    # if we have fpmaster defined in inputs load from file - DEBUG ONLY
    if cond1 and (params['INPUTS']['FPMASTER'] not in [None, 'None', '']):
        # can use from calibDB by setting to 1 or True
        if params['INPUTS']['FPMASTER'] in ['1', 'True']:
            filename = None
        else:
            filename = params['INPUTS']['FPMASTER'][0][0]
        # do stuff
        fpkwargs = dict(header=fpfile.header, filename=filename)
        # read fpmaster file
        masterfp_file, master_fp = shape.get_master_fp(params, **fpkwargs)
        # read table
        fp_table = drs_table.read_table(params, masterfp_file, fmt='fits')
    else:
        # ----------------------------------------------------------------------
        # Get all fp file properties
        # ----------------------------------------------------------------------
        fp_table = shape.construct_fp_table(params, filenames)
        # ----------------------------------------------------------------------
        # match files by date and median to produce master fp
        # ----------------------------------------------------------------------
        cargs = [params, recipe, fpprops['DPRTYPE'], fp_table, fpimage]
        # fpcube, fp_table = shape.construct_master_fp(*cargs)
        master_fp, fp_table = shape.construct_master_fp(*cargs)
        # log process (master construction complete + number of groups added)
        # wargs = [len(fpcube)]
        # WLOG(params, 'info', TextEntry('40-014-00011', args=wargs))
        # sum the cube to make fp data
        # master_fp = np.sum(fpcube, axis=0)

    # ----------------------------------------------------------------------
    # Calculate dx shape map
    # ----------------------------------------------------------------------
    cargs = [hcimage, master_fp, wprops, lprops]
    dout = shape.calculate_dxmap(params, recipe, *cargs)
    dxmap, max_dxmap_std, max_dxmap_info, dxrms = dout
    # if dxmap is None we shouldn't continue as quality control have failed
    if dxmap is None:
        fargs = [max_dxmap_info[0], max_dxmap_info[1], max_dxmap_std,
                 max_dxmap_info[2]]
        WLOG(params, 'warning', TextEntry('10-014-00003', args=fargs))
        # return a copy of locally defined variables in the memory
        return core.return_locals(params, locals())

    # ----------------------------------------------------------------------
    # Calculate dy shape map
    # ----------------------------------------------------------------------
    dymap = shape.calculate_dymap(params, recipe, master_fp, fpheader)

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
    WLOG(params, '', TextEntry('40-014-00025'))
    # apply the dxmap and dymap
    hcimage2 = shape.ea_transform(params, hcimage, dxmap=dxmap, dymap=dymap)
    fpimage2 = shape.ea_transform(params, fpimage, dxmap=dxmap, dymap=dymap)

    # ------------------------------------------------------------------
    # Quality control
    # ------------------------------------------------------------------
    qc_params, passed = shape.shape_master_qc(params, dxrms)
    # update recipe log
    recipe.log.add_qc(params, qc_params, passed)

    # ------------------------------------------------------------------
    # write files
    # ------------------------------------------------------------------
    fargs = [fpfile, hcfile, rawfpfiles, rawhcfiles, dxmap, dymap, master_fp,
             fp_table, fpprops, dxmap0, fpimage, fpimage2, hcimage, hcimage2,
             qc_params]
    outfiles = shape.write_shape_master_files(params, recipe, *fargs)
    outfile1, outfile2, outfile3 = outfiles

    # ----------------------------------------------------------------------
    # Move to calibDB and update calibDB
    # ----------------------------------------------------------------------
    if passed:
        # add dxmap
        drs_database.add_file(params, outfile1)
        # add dymap
        drs_database.add_file(params, outfile2)
        # add master fp file
        drs_database.add_file(params, outfile3)
    # ------------------------------------------------------------------
    # Construct summary document
    # ------------------------------------------------------------------
    shape.write_shape_master_summary(recipe, params, fp_table, qc_params)
    # ------------------------------------------------------------------
    # update recipe log file
    # ------------------------------------------------------------------
    recipe.log.end(params)

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
