#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CODE DESCRIPTION HERE

Created on 2020-08-2020-08-14 12:48

@author: cook
"""
import numpy as np
import os

from apero.base import base
from apero.base import drs_text
from apero import lang
from apero.core import constants
from apero.core.core import drs_log
from apero.core.utils import drs_startup
from apero.core.utils import drs_database2 as drs_database
from apero.io import drs_fits
from apero.io import drs_table
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science import velocity
from apero.tools.module.testing import drs_dev

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'cal_drift_spirou.py'
__INSTRUMENT__ = 'SPIROU'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get constants
Constants = constants.load(__INSTRUMENT__)
# get param dict
ParamDict = constants.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
TextEntry = lang.core.drs_lang_text.TextEntry
TextDict = lang.core.drs_lang_text.TextDict
Help = lang.core.drs_lang_text.HelpDict(__INSTRUMENT__, Constants['LANGUAGE'])
# -----------------------------------------------------------------------------
# set up recipe definitions (overwrites default one)
RMOD = drs_dev.RecipeDefinition(instrument=__INSTRUMENT__)
# get file definitions for this instrument
FMOD = drs_dev.FileDefinition(instrument=__INSTRUMENT__)
# define a recipe for this tool
cal_drift = drs_dev.TmpRecipe()
cal_drift.name = __NAME__
cal_drift.shortname = 'DRIFT'
cal_drift.instrument = __INSTRUMENT__
cal_drift.outputdir = 'reduced'
cal_drift.inputdir = 'reduced'
cal_drift.inputtype = 'reduced'
cal_drift.extension = 'fits'
cal_drift.description = 'Calculates the drift in a set of FP_FP files'
cal_drift.kind = 'misc'
cal_drift.set_debug_plots('CCF_RV_FIT_LOOP', 'CCF_RV_FIT')
cal_drift.set_summary_plots()
cal_drift.set_kwarg(name='--fibers', dtype=str, default='None',
                    helpstr='List of fiber(s) to process '
                            '(comma separated no spaces) i.e. A,B')
cal_drift.set_kwarg(name='--dprtype', dtype=str, default='None',
                    helpstr='DPRTYPE of file to use (e.g. FP_FP)')
cal_drift.set_kwarg(name='--filetype', dtype=str, default='None',
                    helpstr='file type of file to use (e.g. EXT_E2DS_FF)')
cal_drift.set_kwarg(name='--nights', dtype=str, default='None',
                    helpstr='List of night(s) to process'
                            '(comma separated no spaces) i.e. NIGHT1,NIGHT2')
# add recipe to recipe definition
RMOD.add(cal_drift)
# -----------------------------------------------------------------------------
# the output filename (must contain fiber parameter)
OUTPUT_FILENAME = 'cal_drift_{0}.fits'
# define the default file type
DEFAULT_DPRTYPE = 'FP_FP'
DEFAULT_FILETYPE = 'EXT_E2DS_FF'


# =============================================================================
# Define functions
# =============================================================================
# All recipe code goes in _main
#    Only change the following from here:
#     1) function calls  (i.e. main(arg1, arg2, **kwargs)
#     2) fkwargs         (i.e. fkwargs=dict(arg1=arg1, arg2=arg2, **kwargs)
#     3) config_main  outputs value   (i.e. None, pp, reduced)
# Everything else is controlled from recipe_definition
def main(**kwargs):
    """
    Main function for exposuremeter_spirou.py

    :param kwargs: additional keyword arguments

    :keyword debug: int, debug level (0 for None)

    :returns: dictionary of the local space
    :rtype: dict
    """
    # assign function calls (must add positional)
    fkwargs = dict(**kwargs)
    # -------------------------------------------------------------------------
    # deal with command line inputs / function call inputs
    recipe, params = drs_startup.setup(__NAME__, __INSTRUMENT__, fkwargs,
                                       rmod=RMOD)
    # solid debug mode option
    if kwargs.get('DEBUG0000', False):
        return recipe, params
    # -------------------------------------------------------------------------
    # run main bulk of code (catching all errors)
    llmain, success = drs_startup.run(__main__, recipe, params)
    # -------------------------------------------------------------------------
    # End Message
    # -------------------------------------------------------------------------
    return drs_startup.end_main(params, llmain, recipe, success)


def __main__(recipe, params):
    """
    Main code: should only call recipe and params (defined from main)

    :param recipe:
    :param params:
    :return:
    """
    # -------------------------------------------------------------------------
    # Main Code
    # -------------------------------------------------------------------------
    mainname = __NAME__ + '._main()'
    # set up plotting (no plotting before this)
    recipe.plot.set_location()
    # get pseudo constants
    pconst = constants.pload(params['INSTRUMENT'])
    # load the calibration database
    calibdbm = drs_database.CalibrationDatabase(params)
    calibdbm.load_db()
    # get the fibers
    sfibers, rfiber = pconst.FIBER_KINDS()
    dfibers = sfibers + [rfiber]
    fibers = list(dfibers)
    # if we have fibers from user use them
    if 'fibers' in params['INPUTS']:
        if not drs_text.null_text(params['INPUTS']['fibers'], ['None', '']):
            fibers = params['INPUTS']['fibers'].split(',')
            # strip fibers of whitespace
            fibers = np.char.array(fibers).strip()
            # check fibers are correct
            for fiber in fibers:
                if fiber not in dfibers:
                    # log error
                    emsg = ('User input error: fiber={0} is invalid.'
                            '\n\tMust be {1}')
                    eargs = [fiber, ' or '.join(dfibers)]
                    WLOG(params, 'error', emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # deal with other user inputs
    # -------------------------------------------------------------------------
    # get all nights
    allnights = os.listdir(params['DRS_DATA_REDUC'])
    # get nights from user (or set to None)
    nights = [None]
    if 'nights' in params['INPUTS']:
        if not drs_text.null_text(params['INPUTS']['nights'], ['None', '']):
            nights = params['INPUTS']['nights'].split(',')
            # set night name to the last night
            params.set(key='NIGHTNAME', value=nights[-1], source=mainname)
    # deal with no night name set
    if params['NIGHTNAME'] == '':
        # set night name (we have no info about filename)
        params.set(key='NIGHTNAME', value='other', source=mainname)
    # ------------------------------------------------------------------------
    # get the DPRTYPE
    dprtype = str(DEFAULT_DPRTYPE)
    if 'dprtype' in params['INPUTS']:
        if not drs_text.null_text(params['INPUTS']['dprtype'], ['None', '']):
            dprtype = params['INPUTS']['dprtype']
    if dprtype not in params.listp('ALLOWED_FP_TYPES', dtype=str):
        emsg = TextEntry('01-001-00020', args=[dprtype, mainname])
        for allowedtype in params.listp('ALLOWED_FP_TYPES', dtype=str):
            emsg += '\n\t - "{0}"'.format(allowedtype)
        WLOG(params, 'error', emsg)
    # ------------------------------------------------------------------------
    # get the file type (e.g. EXT_E2DS_FF
    filetype = str(DEFAULT_FILETYPE)
    if 'filetype' in params['INPUTS']:
        if not drs_text.null_text(params['INPUTS']['filetype'], ['None', '']):
            filetype = params['INPUTS']['filetype']

    # -------------------------------------------------------------------------
    # loop around fibers
    # -------------------------------------------------------------------------
    for fb_it, fiber in enumerate(fibers):
        # ---------------------------------------------------------------------
        WLOG(params, 'info', params['DRS_HEADER'])
        pargs = [fiber, fb_it + 1, len(fibers)]
        WLOG(params, 'info', 'Processing fiber {0} ({1} of {2})'.format(*pargs))
        WLOG(params, 'info', params['DRS_HEADER'])
        # ---------------------------------------------------------------------
        # Get all FP_FP e2ds files
        # ---------------------------------------------------------------------
        # get all "filetype" filenames
        filenames = []
        for night in nights:
            # check night names are value
            if night is not None:
                # print progress
                WLOG(params, 'info', 'Searching night = {0}'.format(night))
                # deal with invalid night
                if night not in allnights:
                    emsg = 'Night = "{0}" is not a valid reduced sub-directory'
                    WLOG(params, 'error', emsg.format(night))
            # find files for this night (or None)
            files = drs_fits.find_files(params, recipe, kind='reduced',
                                        KW_DPRTYPE=dprtype, KW_OUTPUT=filetype,
                                        KW_FIBER=fiber, night=night)
            # append to list of files
            filenames += list(files)
        # convert to numpy array
        filenames = np.array(filenames)
        # ---------------------------------------------------------------------
        # find file instance in set (verify user input)
        drsfile = drs_startup.get_file_definition(filetype,
                                                  params['INSTRUMENT'],
                                                  kind='red')
        # ---------------------------------------------------------------------
        # storage for table
        basenames, mjdmids, mean_rvs, mean_contrasts = [], [], [], []
        mean_fwhms, mean_tot_lines, dvrms_sps, dv_rms_ccs = [], [], [], []
        wavetimes, wavefiles, wavesrces, paths = [], [], [], []
        # ---------------------------------------------------------------------
        # loop around files
        for f_it, filename in enumerate(filenames):
            # -----------------------------------------------------------------
            WLOG(params, 'info', params['DRS_HEADER'])
            pargs = [f_it + 1, len(filenames)]
            WLOG(params, 'info', 'Processing file {0} of {1}'.format(*pargs))
            WLOG(params, 'info', params['DRS_HEADER'])
            # -----------------------------------------------------------------
            # make a new copy of infile
            infile = drsfile.newcopy(filename=filename, params=params)
            # read file
            infile.read_file()
            # get header
            header = infile.get_header()
            # -----------------------------------------------------------------
            # load wavelength solution for this fiber
            wprops = wave.get_wavesolution(params, recipe, header, fiber=fiber,
                                           database=calibdbm)
            # -----------------------------------------------------------------
            # load the blaze file for this fiber
            blaze_file, blaze = flat_blaze.get_blaze(params, header, fiber)

            # =================================================================
            # FP CCF COMPUTATION
            # =================================================================
            # choose which wprops to use
            wprops = ParamDict(wprops)
            # compute the ccf
            ccfargs = [infile, infile.get_data(), blaze,
                       wprops['WAVEMAP'], fiber]
            rvprops = velocity.compute_ccf_fp(params, recipe, *ccfargs,
                                              sum_plot=False)
            # -----------------------------------------------------------------
            # push rvprops to storage
            basenames.append(infile.basename)
            mjdmids.append(infile.get_hkey('KW_MID_OBS_TIME'))
            mean_rvs.append(rvprops['MEAN_RV'])
            mean_contrasts.append(rvprops['MEAN_CONTRAST'])
            mean_fwhms.append(rvprops['MEAN_FWHM'])
            mean_tot_lines.append(rvprops['TOT_LINE'])
            dvrms_sps.append(rvprops['TOT_SPEC_RMS'])
            dv_rms_ccs.append(rvprops['MEAN_RV_NOISE'])
            wavetimes.append(wprops['WAVETIME'])
            wavefiles.append(wprops['WAVEFILE'])
            wavesrces.append(wprops['WAVESOURCE'])
            paths.append(infile.filename)
        # ---------------------------------------------------------------------
        # convert storage to table
        columnnames = ['FILENAME', 'MJDMID', 'RV', 'CONTRAST', 'FWHM',
                       'TOTLINES', 'DVRMS_SP', 'DVRMS_CC', 'WAVETIME',
                       'WAVEFILE', 'WAVESOURCE', 'PATH']
        columnvalues = [basenames, mjdmids, mean_rvs, mean_contrasts,
                        mean_fwhms, mean_tot_lines, dvrms_sps, dv_rms_ccs,
                        wavetimes, wavefiles, wavesrces, paths]
        # make table
        table = drs_table.make_table(params, columnnames, columnvalues)
        # ---------------------------------------------------------------------
        # construct filename
        cargs = [params['DRS_DATA_REDUC'], params['NIGHTNAME'],
                 OUTPUT_FILENAME.format(fiber)]
        out_filename = os.path.join(*cargs)
        # log that we are saving file
        WLOG(params, '', 'Writing file: {0}'.format(out_filename))
        # save the table to file
        drs_table.write_table(params, table, out_filename, fmt='fits')

    # -------------------------------------------------------------------------
    # End of main code
    # -------------------------------------------------------------------------
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
