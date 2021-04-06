#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-25 at 13:25

@author: cook
"""
import numpy as np
from scipy import interpolate
from scipy import stats
from scipy import signal
from scipy.interpolate import UnivariateSpline
import warnings
from typing import Tuple, List, Union

from apero.base import base
from apero.core import math as mp
from apero import lang
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
from apero.io import drs_table
from apero.science.calib import flat_blaze
from apero.science.calib import wave
from apero.science import extract

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'polar.gen_calib.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsRecipe = drs_recipe.DrsRecipe
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define misc functions
# =============================================================================
def set_polar_exposures(params: ParamDict) -> List[DrsFitsFile]:
    """
    Function to figure out order of exposures based on the
    rhomb positions in the header

    Stokes I (spectroscopic mode)
    P16 P16 1/2/3/4

    Stokes U
    P16 P2 1
    P16 P14 2
    P4 P2 3
    P4 P14 4

    Stokes Q
    P2 P14 1
    P2 P2 2
    P14 P14 3
    P14 P2 4

    Stokes V
    P14 P16 1
    P2 P16 2
    P2 P4 3
    P14 P4 4

    :param params: ParamDict, the parameter dictionary

    :return: list of DrsFitsFile instances - one for each of the 4 exposures
    """
    # set function name
    display_func('set_polar_exposures', __NAME__)
    # check input exposures
    if drs_text.null_text(params['INPUTS']['EXPOSURES'], ['None', '']):
        input_exposures = []
    else:
        input_exposures = params['INPUTS']['EXPOSURES'][1]
    # -------------------------------------------------------------------------
    # set up storage for the exposures
    exposures = [None, None, None, None]
    exp_pos = 0
    # loop around exposures
    for exp in input_exposures:
        # get the rhomb positions for this exposure
        rhomb1 = exp.get_hkey('KW_POLAR_KEY_1')
        rhomb2 = exp.get_hkey('KW_POLAR_KEY_2')
        # ---------------------------------------------------------------------
        # spectroscopy mode
        cond0 = rhomb1 == 'P16' and rhomb2 == 'P16'
        # exposure 1 identifiers
        cond1a = rhomb1 == 'P16' and rhomb2 == 'P2'
        cond1b = rhomb1 == 'P2' and rhomb2 == 'P14'
        cond1c = rhomb1 == 'P14' and rhomb2 == 'P16'
        # exposure 2 identifiers
        cond2a = rhomb1 == 'P16' and rhomb2 == 'P14'
        cond2b = rhomb1 == 'P2' and rhomb2 == 'P2'
        cond2c = rhomb1 == 'P2' and rhomb2 == 'P16'
        # exposure 3 identifiers
        cond3a = rhomb1 == 'P4' and rhomb2 == 'P2'
        cond3b = rhomb1 == 'P14' and rhomb2 == 'P14'
        cond3c = rhomb1 == 'P2' and rhomb2 == 'P4'
        # exposure 4 identifiers
        cond4a = rhomb1 == 'P4' and rhomb2 == 'P14'
        cond4b = rhomb1 == 'P14' and rhomb2 == 'P2'
        cond4c = rhomb1 == 'P14' and rhomb2 == 'P4'
        # ---------------------------------------------------------------------
        # normal message
        msg = 'Exposure {0} in polarimetric mode, set exposure number {1}'
        # spectroscopic mode
        if cond0:
            # add to position
            exposures[exp_pos] = exp
            # update the position
            exp_pos += 1
            # TODO: move to language database
            wmsg = ('Exposure {0} in spectroscopic mode, set exposure '
                    'number = {1}')
            wargs = [exp.basename, exp_pos]
            WLOG(params, 'warning', wmsg.format(*wargs))
        # exposure 1
        elif cond1a or cond1b or cond1c:
            # add to position 1
            exposures[0] = exp
            # TODO: move to language database
            WLOG(params, '', msg.format(exp.basename, 1))
        # exposure 2
        elif cond2a or cond2b or cond2c:
            # add to position 1
            exposures[1] = exp
            # TODO: move to language database
            WLOG(params, '', msg.format(exp.basename, 2))
        # exposure 3
        elif cond3a or cond3b or cond3c:
            # add to position 1
            exposures[2] = exp
            # TODO: move to language database
            WLOG(params, '', msg.format(exp.basename, 3))
        # exposure 3
        elif cond4a or cond4b or cond4c:
            # add to position 1
            exposures[3] = exp
            # TODO: move to language database
            WLOG(params, '', msg.format(exp.basename, 4))
        # else unknown mode - raise error
        else:
            # TODO: move to language database
            emsg = 'Exposure {0} must have keys {1} and {2}'
            eargs = [exp_pos, params['KW_POLAR_KEY_1'][0],
                     params['KW_POLAR_KEY_2'][1]]
            WLOG(params, 'error', emsg.format(*eargs))
        # stop if we already have 4 exposures
        if exp_pos > 3:
            break
    # -------------------------------------------------------------------------
    # Get each individual exposure from input arguments exps
    # loop around the EXP keys
    for it in range(1, 5):
        # get the EXP1, EXP2, EXP3, EXP4 key from inmputs
        exp_input = params['INPUTS']['EXP{0}'.format(it)]
        # only override if we have a value
        if not drs_text.null_text(exp_input, ['None', '']):
            # get drs instance
            exp = exp_input[1][0]
            # TODO: move to language database
            msg = 'Setting exposure 1 in polarimetry sequence to {0}'
            margs = [exp.basename]
            WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # lets make sure out full list is populated with DrsFitsFiles
    for it, exp in enumerate(exposures):
        if not isinstance(exp, DrsFitsFile):
            # TODO: move to language database
            emsg = 'Exposure {0} has not been set correctly'
            WLOG(params, 'error', emsg.format(it + 1))
    # -------------------------------------------------------------------------
    # return the list of exposures
    return exposures


def apero_load_data(params: ParamDict, recipe: DrsRecipe,
                    inputs: List[DrsFitsFile]) -> ParamDict:
    """
    Load the data for the inputted exposures

    data to save per exposure

    A_{N}  B_{N}  where N = 1,2,3,4

    1. "WAVE"           = wave solution of AB fiber
    2. "RAWFLUXDATA"    = flux / blaze
    3. "RAWFLUXERRDATA" = np.sqrt(flux) / blaze
    4. "FLUXDATA"       = interp flux / interp blaze onto same wave as exp1
    5. "FLUXERRDATA"    = np.sqrt(interp flux ) / interp blaze onto same wave
                          as exp1

    # other things to save
    # - STOKES:   CMMTSEQ.split(' ')[0]
    # - EXPOSURE:  CMMTSEQ.split(' ')[1]  or UNDEF
    # - NEXPOSURES:   4

    # data to save once
    # OBJNAME:   from header of exp 1:  OBJECT (should be DRSOBJN)
    # OBJTEMP:   from header of exp 1:  OBJ_TEMP -> deal with no key = 0.0

    returns a class storing these


    :param params:
    :param recipe:
    :param inputs:
    :return:
    """
    # set function name
    func_name = display_func('apero_load_data', __NAME__)
    # load pseudo constants
    pconst = constants.pload()
    # -------------------------------------------------------------------------
    # get from parameters
    polar_fibers = params.listp('POLAR_FIBERS', dtype=str)
    stokesparams = params.listp('POLAR_STOKES_PARAMS', dtype=str)
    berv_correct = params['POLAR_BERV_CORRECT']
    source_rv_correct = params['POLAR_SOURCE_RV_CORRECT']
    # -------------------------------------------------------------------------
    # set up storage
    polar_dict = ParamDict()
    # exposure that we are keeping (these keys are used in the dictionaries)
    polar_dict['EXPOSURES'] = []
    polar_dict['N_EXPOSURES'] = 0
    # stokes parameters for each exposure
    polar_dict['STOKES'] = dict()
    # exposure number for each exposure
    polar_dict['EXPOSURE_NUMBERS'] = dict()
    # wave solution common to all non-raw data
    polar_dict['GLOBAL_WAVEMAP'] = None
    polar_dict['GLOBAL_WAVEFILE'] = None
    polar_dict['GLOBAL_WAVETIME'] = None
    # the inputs in dictionary form
    polar_dict['INPUTS'] = dict()
    # raw flux and flux error
    polar_dict['RAW_WAVEMAP'] = dict()
    polar_dict['RAW_WAVEFILE'] = dict()
    polar_dict['RAW_WAVETIME'] = dict()
    polar_dict['RAW_FLUX'] = dict()
    polar_dict['RAW_FLUXERR'] = dict()
    # flux and flux error on common wave solution grid
    polar_dict['FLUX'] = dict()
    polar_dict['FLUXERR'] = dict()
    # set sources
    keys = ['EXPOSURES', 'N_EXPOSURES', 'EXPOSURE_NUMBERS', 'STOKES', 'INPUTS',
            'GLOBAL_WAVEMAP', 'GLOBAL_WAVEFILE', 'GLOBAL_WAVETIME',
            'RAW_WAVEMAP', 'RAW_WAVEFILE', 'RAW_WAVETIME',
            'RAW_FLUX', 'RAW_FLUXERR', 'FLUX', 'FLUXERR']
    polar_dict.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # TODO: What about from a CCF file?
    # set source rv
    if source_rv_correct:
        source_rv = float(params['INPUTS']['OBJRV'])
    else:
        source_rv = 0.0

    # -------------------------------------------------------------------------
    # Load calibration database
    # -------------------------------------------------------------------------
    calibdb = drs_database.CalibrationDatabase(params)
    calibdb.load_db()
    # -------------------------------------------------------------------------
    # determine the number of this exposure
    # -------------------------------------------------------------------------
    # set a counter (for exposure number when not given in header)
    count, stoke = 1, 'UNDEF'
    # store stokes for each fiber and exposure numbers
    stokes, exp_nums, basenames = [], [], []
    # loop around exposures and work out stokes parameters
    for expfile in inputs:
        # get the stokes type and exposure number from header
        stoke, exp_num = pconst.GET_STOKES_FROM_HEADER(params, expfile.header,
                                                       WLOG)
        # deal with being unable to get stokes from header
        if stoke is None:
            exp_num = int(count)
            count += 1
        # make sure stokes fiber is valid (or set to UNDEF elsewise)
        if stoke not in stokesparams:
            stoke = 'UNDEF'
        # add to storage
        stokes.append(str(stoke))
        exp_nums.append(int(exp_num))
        basenames.append(expfile.basename)
    # deal with multiple stokes parameters
    if len(np.unique(stokes)) != 1:
        emsg = 'Identified more than one stokes parameters in input data.'
        for it in range(len(stokes)):
            emsg += '\n\tFile {0}\tExp {1}\tStokes:{2}'
            emsg = emsg.format(basenames[it], exp_nums[it], stokes[it])
    # -------------------------------------------------------------------------
    # Deal with setting global wave solution
    # -------------------------------------------------------------------------
    # loop around exposures and load fibers
    for it, expfile in enumerate(inputs):
        # ---------------------------------------------------------------------
        # store the wave solution for exposure 1
        if exp_nums[it] == 1:
            # get the exposure 1 wave solution (will be the global solution)
            wprops = wave.get_wavesolution(params, recipe, fiber=expfile.fiber,
                                           infile=expfile, database=calibdb)
            # -----------------------------------------------------------------
            # apply a berv correction if requested
            if berv_correct:
                # get all berv properties from expfile
                bprops = extract.get_berv(params, expfile, log=False)
                # get BERV (need to use both types of BERV measurement)
                berv = bprops['USE_BERV']
                # need the source RV
                dv = berv - source_rv
                # calculate proper wave shift
                dvshift = mp.relativistic_waveshift(dv, units='km/s')
                # apply to wave solution
                wavemap = np.array(wprops['WAVEMAP']) * dvshift
            else:
                wavemap = np.array(wprops['WAVEMAP'])
            # -----------------------------------------------------------------
            # add the global wave solution to polar dict
            polar_dict['GLOBAL_WAVEMAP'] = wavemap
            # add the global wave filename solution to polar dict
            polar_dict['GLOBAL_WAVEFILE'] = str(wprops['WAVEFILE'])
            # add the global wave time solution to polar dict
            polar_dict['GLOBAL_WAVETIME'] = str(wprops['WAVETIME'])
    # -------------------------------------------------------------------------
    # Load all exposures for each polar fiber
    # -------------------------------------------------------------------------
    # loop around exposures and load fibers
    for it, expfile in enumerate(inputs):
        # ---------------------------------------------------------------------
        # loop around fibers
        # ---------------------------------------------------------------------
        for fiber in polar_fibers:
            # -----------------------------------------------------------------
            # work out key
            key_str = '{0}_{1}'.format(fiber, exp_nums[it])
            # log that we are loading data for this key
            # TODO: move to language database
            WLOG(params, 'info', 'Loading data for {0}'.format(key_str))
            # -----------------------------------------------------------------
            # add key to polar dict list
            polar_dict['EXPOSURES'].append(key_str)
            # add exposure numbers to polar dict
            polar_dict['EXPOSURE_NUMBERS'][key_str] = exp_nums[it]
            # add the stokes parameter for this exposure
            polar_dict['STOKES'][key_str] = stokes[it]
            # -----------------------------------------------------------------
            # need to deal with telluric files differently than e2ds files
            if expfile.name == 'TELLU_OBJ':
                gkwargs = dict(outfile=expfile, fiber=fiber,
                               in_block_kind='red', out_block_kind='red',
                               getdata=True, gethdr=True)
            else:
                gkwargs = dict(outfile=expfile, fiber=fiber,
                               in_block_kind='tmp', out_block_kind='red',
                               getdata=True, gethdr=True)
            # -----------------------------------------------------------------
            # need to locate the correct file for this fiber
            infile = drs_file.get_another_fiber_file(params, **gkwargs)
            # -----------------------------------------------------------------
            # load the blaze file
            _, blaze = flat_blaze.get_blaze(params, infile.header, fiber,
                                            database=calibdb)
            # -----------------------------------------------------------------
            # load wave for file
            wprops = wave.get_wavesolution(params, recipe, fiber=fiber,
                                           infile=infile, database=calibdb)
            # -----------------------------------------------------------------
            # apply a berv correction if requested
            if berv_correct:
                # get all berv properties from expfile
                bprops = extract.get_berv(params, expfile, log=False)
                # get BERV (need to use both types of BERV measurement)
                berv = bprops['USE_BERV']
                # need the source RV
                dv = berv - source_rv
                # calculate proper wave shift
                dvshift = mp.relativistic_waveshift(dv, units='km/s')
                # apply to wave solution
                wavemap = np.array(wprops['WAVEMAP']) * dvshift
            else:
                wavemap = np.array(wprops['WAVEMAP'])
            # -----------------------------------------------------------------
            # add the global wave solution to polar dict
            polar_dict['RAW_WAVEMAP'][key_str] = wavemap
            # add the global wave filename solution to polar dict
            polar_dict['RAW_WAVEFILE'][key_str] = str(wprops['WAVEFILE'])
            # add the global wave time solution to polar dict
            polar_dict['RAW_WAVETIME'][key_str] = str(wprops['WAVETIME'])
            # -----------------------------------------------------------------
            # get the raw data
            raw_flux = np.array(infile.data / blaze)
            # get the raw data errors
            with warnings.catch_warnings(record=True) as _:
                raw_fluxerr = np.sqrt(infile.data)
            # -----------------------------------------------------------------
            # get global wave
            gwavemap = polar_dict['GLOBAL_WAVEMAP']
            # get interpolated data
            flux, fluxerr = get_interp_flux(wavemap0=wavemap, flux0=raw_flux,
                                            blaze0=blaze, wavemap1=gwavemap)
            # -----------------------------------------------------------------
            # add rawflux, rawfluxerr, flux, fluxerror to polar dict
            polar_dict['RAW_FLUX'][key_str] = raw_flux
            polar_dict['RAW_FLUXERR'][key_str] = raw_fluxerr
            polar_dict['FLUX'][key_str] = flux
            polar_dict['FLUXERR'][key_str] = fluxerr
    # -------------------------------------------------------------------------
    # make sure we have the correct number of exposures
    if len(polar_dict['EXPOSURES']) == 8:
        polar_dict['N_EXPOSURES'] = 4
    else:
        emsg = ('Number of exposures in input data is not sufficient for'
                ' polarimetry calculations')
        WLOG(params, 'error', emsg)
    # -------------------------------------------------------------------------
    # return the polar dictionary
    return polar_dict


# =============================================================================
# Define science functions
# =============================================================================
def calculate_polarimetry(params: ParamDict, pprops: ParamDict,
                          polar_method: Union[str, None] = None) -> ParamDict:
    """
    Function to call functions to calculate polarimetry either using
    the Ratio or Difference methods.

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            IC_POLAR_METHOD: string, to define polar method "Ratio" or
                             "Difference"

    :param pprops: parameter dictionary, ParamDict containing data

    :return polarfunc: function, either polarimetry_diff_method(p, loc)
                       or polarimetry_ratio_method(p, loc)
    """
    # set function name
    func_name = display_func('calculate_polarimetry', __NAME__)
    # get parameters from params
    method = pcheck(params, 'POLAR_METHOD', func_name, override=polar_method)
    # decide which method to use
    if method == 'Difference':
        return polarimetry_diff_method(params, pprops)
    elif method == 'Ratio':
        return polarimetry_ratio_method(params, pprops)
    else:
        # TODO: move to language database
        emsg = 'Method="{0}" not valid for polarimetry calculation'
        WLOG(params, 'error', emsg.format(method))


def polarimetry_diff_method(params: ParamDict, props: ParamDict,
                            interp_flux: Union[bool, None] = None):
    """
    Function to calculate polarimetry using the difference method as described
    in the paper:
        Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)

    :param params: parameter dictionary, ParamDict containing constants

    :param props: parameter dictionary, ParamDict containing data
        Must contain at least:
            props['RAWFLUXDATA']: numpy array (2D) containing the e2ds flux
                                data for all exposures {1,..,NEXPOSURES},
                                and for all fibers {A,B}
            props['RAWFLUXERRDATA']: numpy array (2D) containing the e2ds flux
                                   error data for all exposures
                                   {1,..,NEXPOSURES}, and for all fibers {A,B}
            props['NEXPOSURES']: number of polarimetry exposures

    :return pprops: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            props['POL']: numpy array (2D), degree of polarization data, which
                        should be the same shape as E2DS files, i.e,
                        loc[DATA][FIBER_EXP]
            props['POLERR']: numpy array (2D), errors of degree of polarization,
                           same shape as loc['POL']
            props['NULL1']: numpy array (2D), 1st null polarization, same
                          shape as loc['POL']
            props['NULL2']: numpy array (2D), 2nd null polarization, same
                          shape as loc['POL']
    """
    # set function name
    name = 'polarimetry_diff_method'
    func_name = display_func(name, __NAME__)
    # get variables from params
    polar_interpolate_flux = pcheck(params, 'POLAR_INTERPOLATE_FLUX',
                                    func=func_name, override=interp_flux)
    # get parameters from loc
    if polar_interpolate_flux:
        data, errdata = props['FLUX'], props['FLUXERR']
    else:
        data, errdata = props['RAW_FLUX'], props['RAW_FLUXERR']
    # get the number of exposures
    nexp = float(props['N_EXPOSURES'])
    # log start of polarimetry calculations
    # TODO: move to language database
    wmsg = 'Running function {0} to calculate polarization'
    WLOG(params, '', wmsg.format(name))
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store polarimetry variables in loc
    data_shape = props['RAW_FLUX']['A_1'].shape
    # initialize arrays to zeroes
    pol_arr = np.zeros(data_shape)
    pol_err_arr = np.zeros(data_shape)
    null1_arr = np.zeros(data_shape)
    null2_arr = np.zeros(data_shape)
    # storage
    gg, gvar = [], []
    # loop around exposures
    for exp in range(1, int(nexp) + 1):
        # get exposure names
        a_exp = 'A_{0}'.format(exp)
        b_exp = 'B_{0}'.format(exp)
        # ---------------------------------------------------------------------
        # STEP 1 - calculate the quantity Gn (Eq #12-14 on page 997 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        part1 = data[a_exp] - data[b_exp]
        part2 = data[a_exp] + data[b_exp]
        gg.append(part1 / part2)

        # Calculate the variances for fiber A and B:
        a_var = errdata[a_exp] ** 2
        b_var = errdata[b_exp] ** 2

        # ---------------------------------------------------------------------
        # STEP 2 - calculate the quantity g_n^2 (Eq #A4 on page 1013 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        nomin = 2.0 * data[a_exp] * data[b_exp]
        denom = (data[a_exp] + data[b_exp]) ** 2.0
        factor1 = (nomin / denom) ** 2.0
        a_var_part = a_var / (data[a_exp] ** 2)
        b_var_part = b_var / (data[b_exp] ** 2)
        gvar.append(factor1 * (a_var_part + b_var_part))

    # if we have 4 exposures
    if nexp == 4:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Dm (Eq #18 on page 997 of
        #          Bagnulo et al. 2009 paper) and the quantity Dms with
        #          exposures 2 and 4 swapped, m being the pair of exposures
        #          Ps. Notice that SPIRou design is such that the angles of
        #          the exposures that correspond to different angles of the
        #          retarder are obtained in the order (1)->(2)->(4)->(3),
        #          which explains the swap between G[3] and G[2].
        # -----------------------------------------------------------------
        d1, d2 = gg[0] - gg[1], gg[3] - gg[2]
        d1s, d2s = gg[0] - gg[2], gg[3] - gg[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the degree of polarization for Stokes
        #          parameter (Eq #19 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol_arr = (d1 + d2) / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the first NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        null1_arr = (d1 - d2) / nexp
        # -----------------------------------------------------------------
        # STEP 6 - calculate the second NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        null2_arr = (d1s - d2s) / nexp
        # -----------------------------------------------------------------
        # STEP 7 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1] + gvar[2] + gvar[3]
        pol_err_arr = np.sqrt(sum_of_gvar / (nexp ** 2.0))

    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Dm
        #          (Eq #18 on page 997 of Bagnulo et al. 2009) and
        #          the quantity Dms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        d1 = gg[0] - gg[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the degree of polarization
        #          (Eq #19 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol_arr = d1 / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1]
        pol_err_arr = np.sqrt(sum_of_gvar / (nexp ** 2.0))

    # else we have insufficient data (should not get here)
    else:
        # TODO: move to language database
        wmsg = ('Number of exposures in input data is not sufficient'
                ' for polarimetry calculations... exiting')
        WLOG(params, 'error', wmsg)
    # -------------------------------------------------------------------------
    # add to props (for output)
    # -------------------------------------------------------------------------
    # set the method
    props['METHOD'] = 'Difference'
    props['POL'] = pol_arr
    props['POLERR'] = pol_err_arr
    props['NULL1'] = null1_arr
    props['NULL2'] = null2_arr
    # set sources
    props.set_sources(['METHOD', 'POL', 'POLERR', 'NULL1', 'NULL2'], func_name)
    # log end of polarimetry calculations
    # TODO: move to language database
    wmsg = 'Routine {0} run successfully'
    WLOG(params, 'info', wmsg.format(name))
    # -------------------------------------------------------------------------
    # return loc
    return props


def polarimetry_ratio_method(params: ParamDict, props: ParamDict,
                             interp_flux: Union[bool, None] = None
                             ) -> ParamDict:
    """
    Function to calculate polarimetry using the ratio method as described
    in the paper:
        Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)

    :param params: parameter dictionary, ParamDict containing constants

    :param props: parameter dictionary, ParamDict containing data
        Must contain at least:
        props['RAWFLUXDATA']: numpy array (2D) containing the e2ds flux data
                              for all exposures {1,..,NEXPOSURES}, and for all
                              fibers {A,B}
        props['RAWFLUXERRDATA']: numpy array (2D) containing the e2ds flux
                                 error data for all exposures {1,..,NEXPOSURES},
                                 and for all fibers {A,B}
        props['NEXPOSURES']: number of polarimetry exposures

    :return props: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            props['POL']: numpy array (2D), degree of polarization data, which
                        should be the same shape as E2DS files, i.e,
                        loc[DATA][FIBER_EXP]
            props['POLERR']: numpy array (2D), errors of degree of polarization,
                           same shape as loc['POL']
            props['NULL1']: numpy array (2D), 1st null polarization, same
                          shape as loc['POL']
            props['NULL2']: numpy array (2D), 2nd null polarization, same
                          shape as loc['POL']
    """
    # set function name
    name = 'polarimetry_ratio_method'
    func_name = display_func(name, __NAME__)
    # get variables from params
    polar_interpolate_flux = pcheck(params, 'POLAR_INTERPOLATE_FLUX',
                                    func=func_name, override=interp_flux)
    # log start of polarimetry calculations
    # TODO: move to lanugage database
    wmsg = 'Running function {0} to calculate polarization'
    WLOG(params, '', wmsg.format(name))
    # get parameters from loc
    if polar_interpolate_flux:
        data, errdata = props['FLUX'], props['FLUXERR']
    else:
        data, errdata = props['RAW_FLUX'], props['RAW_FLUXERR']
    # get the number of exposures
    nexp = float(props['N_EXPOSURES'])
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store polarimetry variables in loc
    data_shape = props['RAW_FLUX']['A_1'].shape
    # initialize arrays to zeroes
    pol_arr = np.zeros(data_shape)
    pol_err_arr = np.zeros(data_shape)
    null1_arr = np.zeros(data_shape)
    null2_arr = np.zeros(data_shape)
    # storage
    flux_ratio, var_term = [], []
    # loop around exposures
    for exp in range(1, int(nexp) + 1):
        # get exposure names
        a_exp = 'A_{0}'.format(exp)
        b_exp = 'B_{0}'.format(exp)
        # ---------------------------------------------------------------------
        # STEP 1 - calculate ratio of beams for each exposure
        #          (Eq #12 on page 997 of Bagnulo et al. 2009 )
        # ---------------------------------------------------------------------
        flux_ratio.append(data[a_exp] / data[b_exp])
        # Calculate the variances for fiber A and B:
        a_var = errdata[a_exp] ** 2
        b_var = errdata[b_exp] ** 2
        # ---------------------------------------------------------------------
        # STEP 2 - calculate the error quantities for Eq #A10 on page 1014 of
        #          Bagnulo et al. 2009
        # ---------------------------------------------------------------------
        var_term_part1 = a_var / (data[a_exp] ** 2)
        var_term_part2 = b_var / (data[b_exp] ** 2)
        var_term.append(var_term_part1 + var_term_part2)

    # if we have 4 exposures
    if nexp == 4:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        #          Ps. Notice that SPIRou design is such that the angles of
        #          the exposures that correspond to different angles of the
        #          retarder are obtained in the order (1)->(2)->(4)->(3),which
        #          explains the swap between flux_ratio[3] and flux_ratio[2].
        # -----------------------------------------------------------------
        r1, r2 = flux_ratio[0] / flux_ratio[1], flux_ratio[3] / flux_ratio[2]
        r1s, r2s = flux_ratio[0] / flux_ratio[2], flux_ratio[3] / flux_ratio[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rr = (r1 * r2) ** (1.0 / (2 * nexp))
        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol_arr = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the quantity RN1
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rn1 = (r1 / r2) ** (1.0 / (2 * nexp))
        # -----------------------------------------------------------------
        # STEP 7 - calculate the first NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        null1_arr = (rn1 - 1.0) / (rn1 + 1.0)
        # -----------------------------------------------------------------
        # STEP 8 - calculate the quantity RN2
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rn2 = (r1s / r2s) ** (1.0 / (2 * nexp))
        # -----------------------------------------------------------------
        # STEP 9 - calculate the second NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        null2_arr = (rn2 - 1.0) / (rn2 + 1.0)
        # -----------------------------------------------------------------
        # STEP 10 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            numer_part1 = (r1 * r2) ** (1.0 / 2.0)
            denom_part1 = ((r1 * r2) ** (1.0 / 4.0) + 1.0) ** 4.0
        part1 = numer_part1 / (denom_part1 * 4.0)
        sumvar = var_term[0] + var_term[1] + var_term[2] + var_term[3]
        pol_err_arr = np.sqrt(part1 * sumvar)

    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        r1 = flux_ratio[0] / flux_ratio[1]

        # -----------------------------------------------------------------
        # STEP 4 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        rr = r1 ** (1.0 / (2 * nexp))

        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        pol_arr = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        # numer_part1 = R1
        denom_part1 = ((r1 ** 0.5) + 1.0) ** 4.0
        part1 = r1 / denom_part1
        sumvar = var_term[0] + var_term[1]
        pol_err_arr = np.sqrt(part1 * sumvar)

    # else we have insufficient data (should not get here)
    else:
        # TODO: move to language database
        wmsg = ('Number of exposures in input data is not sufficient'
                ' for polarimetry calculations... exiting')
        WLOG(params, 'error', wmsg)
    # set the method
    props['METHOD'] = 'Ratio'
    props['POL'] = pol_arr
    props['POLERR'] = pol_err_arr
    props['NULL1'] = null1_arr
    props['NULL2'] = null2_arr
    # set sources
    props.set_sources(['METHOD', 'POL', 'POLERR', 'NULL1', 'NULL2'], func_name)
    # log end of polarimetry calculations
    # TODO: move to language database
    wmsg = 'Routine {0} run successfully'
    WLOG(params, 'info', wmsg.format(name))
    # return loc
    return props


def calculate_stokes_i(params: ParamDict, props: ParamDict,
                       interp_flux: Union[bool, None] = None) -> ParamDict:
    """
    Function to calculate the Stokes I polarization

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging

    :param props: parameter dictionary, ParamDict containing data
        Must contain at least:
            DATA: array of numpy arrays (2D), E2DS data from all fibers in
                  all input exposures.
            NEXPOSURES: int, number of exposures in polar sequence

    :return loc: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            STOKESI: numpy array (2D), the Stokes I parameters, same shape as
                     DATA
            STOKESIERR: numpy array (2D), the Stokes I error parameters, same
                        shape as DATA
    """
    # set function name
    name = 'calculate_stokes_i'
    func_name = display_func(name, __NAME__)
    # log start of Stokes I calculations
    wmsg = 'Running function {0} to calculate Stokes I total flux'
    WLOG(params, '', wmsg.format(name))
    # get parameters from params
    polar_interpolate_flux = pcheck(params, 'POLAR_INTERPOLATE_FLUX',
                                    func=func_name, override=interp_flux)
    # get parameters from props
    if polar_interpolate_flux:
        data, errdata = props['FLUX'], props['FLUXERR']
    else:
        data, errdata = props['RAW_FLUX'], props['RAW_FLUXERR']
    # get the number of exposures
    nexp = float(props['N_EXPOSURES'])
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store Stokes I variables in loc
    data_shape = props['RAW_FLUX']['A_1'].shape
    # initialize arrays to zeroes
    stokesi_arr = np.zeros(data_shape)
    stokesierr_arr = np.zeros(data_shape)
    # storage for flux and variance
    flux, var = [], []
    # loop around exposure
    for exp in range(1, int(nexp) + 1):
        # get exposure names
        a_exp = 'A_{0}'.format(exp)
        b_exp = 'B_{0}'.format(exp)

        # Calculate sum of fluxes from fibers A and B
        flux_ab = data[a_exp] + data[b_exp]
        # Save A+B flux for each exposure
        flux.append(flux_ab)
        # Calculate the variances for fiber A+B
        #    -> varA+B = sigA * sigA + sigB * sigB
        var_ab = errdata[a_exp] ** 2 + errdata[b_exp] ** 2
        # Save varAB = sigA^2 + sigB^2, ignoring cross-correlated terms
        var.append(var_ab)
    # Sum fluxes and variances from different exposures
    for i in range(len(flux)):
        stokesi_arr += flux[i]
        stokesierr_arr += var[i]

    stokesi_arr = np.sum(flux, axis=1)
    stokesierr_arr = np.sum(var, axis=1)

    # Calcualte errors -> sigma = sqrt(variance)
    stokesierr_arr = np.sqrt(stokesierr_arr)

    # add to output
    props['STOKESI'] = stokesi_arr
    props['STOKESIERR'] = stokesierr_arr
    # set sources
    keys = ['STOKESI', 'STOKESIERR']
    props.set_sources(keys, func_name)

    # log end of Stokes I intensity calculations
    wmsg = 'Routine {0} run successfully'
    WLOG(params, '', wmsg.format(name))

    # return loc
    return props


def get_interp_flux(wavemap0: np.ndarray, flux0: np.ndarray,
                    blaze0: np.ndarray, wavemap1: np.ndarray
                    ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Work out the interpolated flux from grid "wavemap0" to a grid "wavemap1"

    :param wavemap0: np.array, the initial wave grid of the flux data
    :param flux0: np.array, the initial flux values
    :param blaze0: np.array, the initial blaze values
    :param wavemap1: np.array, the final wave grid to interpolate to

    :return: tuple, 1. the flux on wavemap1, 2. the flux error on wavemap1
    """
    # output flux and flux error maps
    flux1 = np.full_like(flux0, np.nan)
    fluxerr1 = np.full_like(flux0, np.nan)
    # loop around each order (per order spline)
    for order_num in range(wavemap0.shape[0]):
        # only keep clean data
        clean = np.isfinite(flux0[order_num])
        # get order values
        ordwave0 = wavemap0[order_num][clean]
        ordflux0 = flux0[order_num][clean]
        ordblaze0 = blaze0[order_num][clean]
        ordwave1 = wavemap1[order_num]
        # get spline of flux and blaze in original positions
        flux_tck = interpolate.splrep(ordwave0, ordflux0, s=0)
        blaze_tck = interpolate.splrep(ordwave0, ordblaze0, s=0)
        # mask the global wavemap (1) so it lies within the bounds of the
        #  the local wavemap (0)
        wlmask = ordwave1 > np.min(ordwave0)
        wlmask &= ordwave1 < np.max(ordwave0)
        # apply the spline to the output wave grid (masked)
        ordblaze1 = interpolate.splev(ordwave1[wlmask], blaze_tck, der=0)
        ordflux1 = interpolate.splev(ordwave1[wlmask], flux_tck, der=0)
        # push into flux1 array
        flux1[order_num][wlmask] = ordflux1 / ordblaze1
        # calculate fluxerr1 and push into array
        with warnings.catch_warnings(record=True) as _:
            fluxerr1[order_num][wlmask] = np.sqrt(ordflux1 / ordblaze1)
    # ---------------------------------------------------------------------
    return flux1, fluxerr1


def calculate_continuum(params: ParamDict, recipe: DrsRecipe, props: ParamDict,
                        in_wavelength: bool = True) -> ParamDict:
    """
    Function to calculate the continuum flux and continuum polarization

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
            POLAR_CONT_BINSIZE: int, number of points in each sample bin
            POLAR_CONT_OVERLAP: int, number of points to overlap before and
                                after each sample bin
            POLAR_CONT_TELLMASK: list of float pairs, list of telluric bands,
                                 i.e, a list of wavelength ranges ([wl0,wlf])
                                 for telluric absorption

    :param recipe: DrsRecipe, the recipe calling this function (use to access
                   the plotting)

    :param props: parameter dictionary, ParamDict containing data
        Must contain at least:
            GLOBAL_WAVEMAP: numpy array (2D), e2ds wavelength data
            POL: numpy array (2D), e2ds degree of polarization data
            POLERR: numpy array (2D), e2ds errors of degree of polarization
            NULL1: numpy array (2D), e2ds 1st null polarization
            NULL2: numpy array (2D), e2ds 2nd null polarization
            STOKESI: numpy array (2D), e2ds Stokes I data
            STOKESIERR: numpy array (2D), e2ds errors of Stokes I

    :param in_wavelength: bool, to indicate whether or not there is wave cal

    :return props: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            FLAT_X: numpy array (1D), flatten polarimetric x data
            FLAT_POL: numpy array (1D), flatten polarimetric pol data
            FLAT_POLERR: numpy array (1D), flatten polarimetric pol error data
            FLAT_STOKESI: numpy array (1D), flatten polarimetric stokes I data
            FLAT_STOKESIERR: numpy array (1D), flatten polarimetric stokes I
                             error data
            FLAT_NULL1: numpy array (1D), flatten polarimetric null1 data
            FLAT_NULL2: numpy array (1D), flatten polarimetric null2 data
            CONT_FLUX: numpy array (1D), e2ds continuum flux data
                       interpolated from xbin, ybin points, same shape as FLAT_STOKESI
            CONT_FLUX_XBIN: numpy array (1D), continuum in x flux samples
            CONT_FLUX_YBIN: numpy array (1D), continuum in y flux samples

            CONT_POL: numpy array (1D), e2ds continuum polarization data
                      interpolated from xbin, ybin points, same shape as
                      FLAT_POL
            CONT_POL_XBIN: numpy array (1D), continuum in x polarization samples
            CONT_POL_YBIN: numpy array (1D), continuum in y polarization samples
    """
    # set the function name
    func_name = __NAME__ + '.calculate_continuum()'
    # -------------------------------------------------------------------------
    # get constants from p
    pol_binsize = params['POLAR_CONT_BINSIZE']
    pol_overlap = params['POLAR_CONT_OVERLAP']
    # stokes fit parameters
    stokesi_detection_alg = params['STOKESI_CONTINUUM_DETECTION_ALGORITHM']
    stokei_iraf_cont_fit_func = params['STOKESI_IRAF_CONT_FIT_FUNCTION']
    stokes_iraf_cont_func_ord = params['STOKESI_IRAF_CONT_FUNCTION_ORDER']
    # polar fit parameters
    polar_detection_alg = params['POLAR_CONTINUUM_DETECTION_ALGORITHM']
    polar_iraf_cont_fit_func = params['POLAR_IRAF_CONT_FIT_FUNCTION']
    polar_iraf_cont_func_ord = params['POLAR_IRAF_CONT_FUNCTION_ORDER']
    # other parameters
    norm_stokes_i = params['POLAR_NORMALIZE_STOKES_I']
    cont_poly_fit = params['POLAR_CONT_POLYNOMIAL_FIT']
    cont_deg_poly = params['POLAR_CONT_DEG_POLYNOMIAL']
    remove_continuum = params['POLAR_REMOVE_CONTINUUM']
    # -------------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    telluric_bands = pconst.GET_POLAR_TELLURIC_BANDS()
    # -------------------------------------------------------------------------
    # get the shape of pol
    ydim, xdim = props['POL'].shape
    # get wavelength data if require
    if in_wavelength:
        xdata = props['GLOBAL_WAVEMAP'].ravel()
    else:
        xdata = np.arange(ydim * xdim)
    # -------------------------------------------------------------------------
    # flatten data (across orders)
    pol = props['POL'].ravel()
    polerr = props['POLERR'].ravel()
    stokes_i = props['STOKESI'].ravel()
    stokes_ierr = props['STOKESIERR'].ravel()
    null1 = props['NULL1'].ravel()
    null2 = props['NULL2'].ravel()
    # -------------------------------------------------------------------------
    # sort by wavelength (or pixel number)
    sortmask = np.argsort(xdata)
    # sort data
    xdata = xdata[sortmask]
    pol = pol[sortmask]
    polerr = polerr[sortmask]
    stokes_i = stokes_i[sortmask]
    stokes_ierr = stokes_ierr[sortmask]
    null1 = null1[sortmask]
    null2 = null2[sortmask]
    # set xbin and ybin for output (filled by moving median method)
    flux_xbin, flux_ybin = None, None
    pol_xbin, pol_ybin = None, None
    # -------------------------------------------------------------------------
    # calculate continuum flux using moving median
    if stokesi_detection_alg == 'MOVING_MEDIAN':
        # calculate continuum flux
        cout = _continuum(params, xdata, stokes_i, binsize=pol_binsize,
                          overlap=pol_overlap, window=6, mode="max",
                          use_linear_fit=True, telluric_bands=telluric_bands)
        contflux, flux_xbin, flux_ybin = cout
        # calculate conntinuum flux using IRAF algorithm
    elif stokesi_detection_alg == 'IRAF':
        contflux = _fit_continuum(params, recipe, xdata, stokes_i,
                                  function=stokei_iraf_cont_fit_func,
                                  degree=stokes_iraf_cont_func_ord,
                                  niter=5, rej_low=3.0, rej_high=3.0, grow=1,
                                  med_filt=0, percentile_low=0.,
                                  percentile_high=100.0,
                                  min_points=10, verbose=False)
    # else raise error
    else:
        # TODO: move to language database
        emsg = 'Stokes I continuum detection algorithm invalid'
        emsg += '\n\t Must be "MOVING_MEDIAN" or "IRAF"\n\tCurrent: {0}'
        WLOG(params, 'error', emsg.format(stokesi_detection_alg))
        contflux = None
    # -------------------------------------------------------------------------
    # normalize flux by continuum
    if norm_stokes_i:
        stokes_i = stokes_i / contflux
        stokes_ierr = stokes_ierr / contflux
    # -------------------------------------------------------------------------
    # calculate polarization flux using moving median
    if polar_detection_alg == 'MOVING_MEDIAN':
        # calculate continuum polarization
        cpout = _continuum_polarization(params, xdata, pol, binsize=pol_binsize,
                                        overlap=pol_overlap, mode='median',
                                        use_polynomail_fit=cont_poly_fit,
                                        deg_poly_fit=cont_deg_poly,
                                        telluric_bands=telluric_bands)
        contpol, pol_xbin, pol_ybin = cpout
    # calculate polarization flux using IRAF algorithm
    elif polar_detection_alg == 'IRAF':
        contpol = _fit_continuum(params, recipe, xdata, pol,
                                 function=polar_iraf_cont_fit_func,
                                 degree=polar_iraf_cont_func_ord, niter=5,
                                 rej_low=3.0, rej_high=3.0, grow=1,
                                 med_filt=0, percentile_low=0.0,
                                 percentile_high=100.0, min_points=10,
                                 verbose=False)
    # else raise error
    else:
        # TODO: move to language database
        emsg = 'Stokes I continuum detection algorithm invalid'
        emsg += '\n\t Must be "MOVING_MEDIAN" or "IRAF"\n\tCurrent: {0}'
        WLOG(params, 'error', emsg.format(polar_detection_alg))
        contpol = None
    # -------------------------------------------------------------------------
    # remove continuum polarization
    if remove_continuum:
        pol = pol - contpol
    # -------------------------------------------------------------------------
    # save back to props
    props['FLAT_X'] = xdata
    props['FLAT_POL'] = pol
    props['FLAT_POLERR'] = polerr
    props['FLAT_STOKESI'] = stokes_i
    props['FLAT_STOKESIERR'] = stokes_ierr
    props['FLAT_NULL1'] = null1
    props['FLAT_NULL2'] = null2
    # save bin information
    props['CONT_FLUX_XBIN'] = flux_xbin
    props['CONT_FLUX_YBIN'] = flux_ybin
    props['CONT_POL_XBIN'] = pol_xbin
    props['CONT_POL_YBIN'] = pol_ybin
    # save continuum data to loc
    props['CONT_FLUX'] = contflux
    props['CONT_POL'] = contpol
    # key sources
    keys = ['FLAT_X', 'FLAT_POL', 'FLAT_POLERR', 'FLAT_STOKESI',
            'FLAT_STOKESIERR', 'FLAT_NULL1', 'FLAT_NULL2',
            'CONT_FLUX_XBIN', 'CONT_FLUX_YBIN', 'CONT_POL_XBIN',
            'CONT_POL_YBIN', 'CONT_FLUX', 'CONT_POL']
    props.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # return udpated property param dict
    return props


# =============================================================================
# Define quality control and writing functions
# =============================================================================
def quality_control(params):
    # ----------------------------------------------------------------------
    # set passed variable and fail message list
    fail_msg = []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # ----------------------------------------------------------------------
    # TODO: Need some quality control
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # find out whether everything passed
    passed = np.sum(qc_pass) == len(qc_pass)
    # --------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    #     quality control QC = 0 if we fail quality control
    if passed:
        WLOG(params, 'info', textentry('40-005-10001'))
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params, passed


def write_files(params, recipe, pobjects, rawfiles, pprops, lprops, wprops,
                polstats, s1dprops, qc_params):
    # use the first file as reference
    pobj = pobjects['A_1']
    # get the infile from pobj
    infile = pobj.infile

    # ----------------------------------------------------------------------
    # Store pol in file
    # ----------------------------------------------------------------------
    # get a new copy of the pol file
    polfile = recipe.outputs['POL_DEG_FILE'].newcopy(params=params)
    # construct the filename from file instance
    polfile.construct_filename(infile=infile)
    # define header keys for output file
    # copy keys from input file
    polfile.copy_original_keys(infile)
    # add version
    polfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    polfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    polfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    polfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    polfile.add_hkey('KW_OUTPUT', value=polfile.name)
    # add input files
    polfile.add_hkey_1d('KW_INFILE1', values=rawfiles, dim1name='file')
    # ----------------------------------------------------------------------
    # add the wavelength solution used
    polfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    # ----------------------------------------------------------------------
    # add qc parameters
    polfile.add_qckeys(qc_params)
    # ----------------------------------------------------------------------
    # add the stokes parameters
    polfile.add_hkey('KW_POL_STOKES', value=pprops['STOKES'])
    polfile.add_hkey('KW_POL_NEXP', value=pprops['NEXPOSURES'])
    polfile.add_hkey('KW_POL_METHOD', value=pprops['METHOD'])
    # ----------------------------------------------------------------------
    # add polar statistics
    polfile.add_hkey_1d('KW_POL_FILES', values=polstats['FILES'],
                        dim1name='exposure')
    polfile.add_hkey_1d('KW_POL_EXPS', values=polstats['EXPS'],
                        dim1name='exposure')
    polfile.add_hkey_1d('KW_POL_MJDS', values=polstats['MJDS'],
                        dim1name='exposure')
    polfile.add_hkey_1d('KW_POL_MJDENDS', values=polstats['MJDENDS'],
                        dim1name='exposure')
    polfile.add_hkey_1d('KW_POL_BJDS', values=polstats['BJDS'],
                        dim1name='exposure')
    polfile.add_hkey_1d('KW_POL_BERVS', values=polstats['BERVS'],
                        dim1name='exposure')
    polfile.add_hkey('KW_POL_EXPTIME', value=polstats['TOTAL_EXPTIME'])
    polfile.add_hkey('KW_POL_ELAPTIME', value=polstats['ELAPSED_TIME'])
    polfile.add_hkey('KW_POL_MJDCEN', value=polstats['MJD_CEN'])
    polfile.add_hkey('KW_POL_BJDCEN', value=polstats['BJD_CEN'])
    polfile.add_hkey('KW_POL_BERVCEN', value=polstats['BERV_CEN'])
    polfile.add_hkey('KW_POL_MEANBJD', value=polstats['MEAN_BJD'])
    # update exposure time
    polfile.add_hkey('KW_EXPTIME', value=polstats['TOTAL_EXPTIME'])
    # update acqtime
    # TODO: This should be MJD_MID?
    polfile.add_hkey('KW_ACQTIME', value=polstats['MJD_CEN'])
    # update bjd
    # TODO: This should be either BJD or BJD_EST based on BERVSRCE
    polfile.add_hkey('KW_BJD', value=polstats['BJD_CEN'])
    # update berv
    # TODO: this should be either BERV or BERV_EST based on BERVSRCE
    polfile.add_hkey('KW_BERV', value=polstats['BERV_CEN'])
    # update bervmax
    # TODO: this should be either BERVMAX or BERVMAXEST based on BERVSRCE
    polfile.add_hkey('KW_BERVMAX', value=polstats['BERVMAX'])
    # ----------------------------------------------------------------------
    # add constants
    polfile.add_hkey('KW_USED_MIN_FILES', value=pprops['MIN_FILES'])
    polfile.add_hkey_1d('KW_USED_VALID_FIBERS', values=pprops['VALID_FIBERS'],
                        dim1name='entry')
    polfile.add_hkey_1d('KW_USED_VALID_STOKES', values=pprops['VALID_STOKES'],
                        dim1name='entry')
    polfile.add_hkey('KW_USED_CONT_BINSIZE', value=pprops['CONT_BINSIZE'])
    polfile.add_hkey('KW_USED_CONT_OVERLAP', value=pprops['CONT_OVERLAP'])
    # ----------------------------------------------------------------------
    # set data
    polfile.data = pprops['POL']
    # ----------------------------------------------------------------------
    # log that we are saving pol file
    WLOG(params, '', textentry('40-021-00005', args=[polfile.filename]))
    # define multi lists
    data_list = [pprops['POLERR']]
    name_list = ['POL_ERR']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=polfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    polfile.write_multi(data_list=data_list, name_list=name_list,
                        block_kind=recipe.out_block_str,
                        runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(polfile)

    # ----------------------------------------------------------------------
    # Store null1 in file
    # ----------------------------------------------------------------------
    # get a new copy of the pol file
    null1file = recipe.outputs['POL_NULL1'].newcopy(params=params)
    # construct the filename from file instance
    null1file.construct_filename(infile=infile)
    # copy header from corrected e2ds file
    null1file.copy_hdict(polfile)
    # add output tag
    null1file.add_hkey('KW_OUTPUT', value=null1file.name)
    # set data
    null1file.data = pprops['NULL1']
    # log that we are saving null1 file
    WLOG(params, '', textentry('40-021-00006', args=[null1file.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=null1file)]
        name_list += ['PARAM_TABLE']
    # write image to file
    null1file.write_multi(data_list=data_list, name_list=name_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(null1file)

    # ----------------------------------------------------------------------
    # Store null2 in file
    # ----------------------------------------------------------------------
    # get a new copy of the pol file
    null2file = recipe.outputs['POL_NULL2'].newcopy(params=params)
    # construct the filename from file instance
    null2file.construct_filename(infile=infile)
    # copy header from corrected e2ds file
    null2file.copy_hdict(polfile)
    # add output tag
    null2file.add_hkey('KW_OUTPUT', value=null2file.name)
    # set data
    null2file.data = pprops['NULL2']
    # log that we are saving null1 file
    WLOG(params, '', textentry('40-021-00007', args=[null2file.filename]))
    # define multi lists
    data_list, name_list = [], []
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=null2file)]
        name_list += ['PARAM_TABLE']
    # write image to file
    null2file.write_multi(data_list=data_list, name_list=name_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(null2file)

    # ----------------------------------------------------------------------
    # Store null2 in file
    # ----------------------------------------------------------------------
    # get a new copy of the pol file
    stokesfile = recipe.outputs['POL_STOKESI'].newcopy(params=params)
    # construct the filename from file instance
    stokesfile.construct_filename(infile=infile)
    # copy header from corrected e2ds file
    stokesfile.copy_hdict(polfile)
    # add output tag
    stokesfile.add_hkey('KW_OUTPUT', value=stokesfile.name)
    # add the stokes parameters
    stokesfile.add_hkey('KW_POL_STOKES', value='I')
    # set data
    stokesfile.data = pprops['STOKESI']
    # log that we are saving pol file
    WLOG(params, '', textentry('40-021-00008', args=[stokesfile.filename]))
    # define multi lists
    data_list = [pprops['STOKESIERR']]
    name_list = ['STOKES_I_ERR']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=stokesfile)]
        name_list += ['PARAM_TABLE']
    # write image to file
    stokesfile.write_multi(data_list=data_list, name_list=name_list,
                           block_kind=recipe.out_block_str,
                           runstring=recipe.runstring)
    # add to output files (for indexing)STOKES_I
    recipe.add_output_file(stokesfile)

    # ----------------------------------------------------------------------
    # Store s1d files
    # ----------------------------------------------------------------------
    for s1dkey in s1dprops:
        # get a new copy of the pol file
        s1dfile = recipe.outputs[s1dkey].newcopy(params=params)
        # construct the filename from file instance
        s1dfile.construct_filename(infile=infile)
        # copy header from corrected e2ds file
        s1dfile.copy_hdict(polfile)
        # add output tag
        s1dfile.add_hkey('KW_OUTPUT', value=s1dfile.name)
        # copy data
        s1dfile.data = s1dprops[s1dkey]['S1DTABLE']
        # must change the datatpye to 'table'
        s1dfile.datatype = 'table'
        # log that we are saving s1d table
        wargs = [s1dkey, s1dfile.filename]
        WLOG(params, '', textentry('40-021-00010', args=wargs))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=s1dfile)]
            name_list += ['PARAM_TABLE']
        # write image to file
        s1dfile.write_multi(data_list=data_list, name_list=name_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(s1dfile)

    # ----------------------------------------------------------------------
    # Store lsd file
    # ----------------------------------------------------------------------
    if lprops['LSD_ANALYSIS']:
        # ------------------------------------------------------------------
        # make lsd table
        columns = ['velocities', 'stokesI', 'stokesI_model', 'stokesVQU',
                   'Null']
        values = [lprops['LSD_VELOCITIES'], lprops['LSD_STOKES_I'],
                  lprops['LSD_STOKES_I_MODEL'], lprops['LSD_STOKES_VQU'],
                  lprops['LSD_NULL']]
        comments = ['LSD_VELOCITIES', 'LSD_STOKESI', 'LSD_STOKESI_MODEL',
                    'LSD_STOKESVQU', 'LSD_NULL']
        # construct table
        lsd_table = drs_table.make_table(params, columns=columns, values=values)
        # ------------------------------------------------------------------
        # get a new copy of the pol file
        lsd_file = recipe.outputs['POL_LSD'].newcopy(params=params)
        # construct the filename from file instance
        lsd_file.construct_filename(infile=infile)
        # copy header from corrected e2ds file
        lsd_file.copy_hdict(polfile)
        # add output tag
        lsd_file.add_hkey('KW_OUTPUT', value=lsd_file.name)
        # ------------------------------------------------------------------
        # add lsd data
        lsd_file.add_hkey('KW_POLAR_LSD_MASK', value=lprops['LSD_MASK'])
        lsd_file.add_hkey('KW_POLAR_LSD_FIT_RV',
                          value=lprops['LSD_STOKES_I_FIT_RV'])
        lsd_file.add_hkey('KW_POLAR_LSD_FIT_RESOL',
                          value=lprops['LSD_STOKES_FIT_RESOL'])
        lsd_file.add_hkey('KW_POLAR_LSD_MEANPOL', value=lprops['LSD_POL_MEAN'])
        lsd_file.add_hkey('KW_POLAR_LSD_STDPOL', value=lprops['LSD_POL_STD'])
        lsd_file.add_hkey('KW_POLAR_LSD_MEDPOL', value=lprops['LSD_POL_MEDIAN'])
        lsd_file.add_hkey('KW_POLAR_LSD_MEDABSDEV',
                          value=lprops['LSD_POL_MED_ABS_DEV'])
        lsd_file.add_hkey('KW_POLAR_LSD_MEANSVQU',
                          value=lprops['LSD_STOKES_VQU_MEAN'])
        lsd_file.add_hkey('KW_POLAR_LSD_STDSVQU',
                          value=lprops['LSD_STOKES_VQU_STD'])
        lsd_file.add_hkey('KW_POLAR_LSD_MEANNULL',
                          value=lprops['LSD_NULL_MEAN'])
        lsd_file.add_hkey('KW_POLAR_LSD_STDNULL', value=lprops['LSD_NULL_STD'])
        # add information about the meaning of the data columns
        lsd_file.add_hkey('KW_POL_LSD_COL1', value=comments[0])
        lsd_file.add_hkey('KW_POL_LSD_COL2', value=comments[1])
        lsd_file.add_hkey('KW_POL_LSD_COL3', value=comments[2])
        lsd_file.add_hkey('KW_POL_LSD_COL4', value=comments[3])
        lsd_file.add_hkey('KW_POL_LSD_COL5', value=comments[4])
        # add lsd constants
        lsd_file.add_hkey('KW_POLAR_LSD_MLDEPTH',
                          value=lprops['LSD_MIN_LINEDEPTH'])
        lsd_file.add_hkey('KW_POLAR_LSD_VINIT', value=lprops['LSD_VINIT'])
        lsd_file.add_hkey('KW_POLAR_LSD_VFINAL', value=lprops['LSD_VFINAL'])
        lsd_file.add_hkey('KW_POLAR_LSD_NORM', value=lprops['LSD_NORM'])
        lsd_file.add_hkey('KW_POLAR_LSD_NBIN1', value=lprops['LSD_NBIN1'])
        lsd_file.add_hkey('KW_POLAR_LSD_NLAP1', value=lprops['LSD_NOVERLAP1'])
        lsd_file.add_hkey('KW_POLAR_LSD_NSIG1', value=lprops['LSD_NSIGCLIP1'])
        lsd_file.add_hkey('KW_POLAR_LSD_NWIN1', value=lprops['LSD_NWINDOW1'])
        lsd_file.add_hkey('KW_POLAR_LSD_NMODE1', value=lprops['LSD_NMODE1'])
        lsd_file.add_hkey('KW_POLAR_LSD_NLFIT1', value=lprops['LSD_NLFIT1'])
        lsd_file.add_hkey('KW_POLAR_LSD_NPOINTS', value=lprops['LSD_NPOINTS'])
        lsd_file.add_hkey('KW_POLAR_LSD_NBIN2', value=lprops['LSD_NBIN2'])
        lsd_file.add_hkey('KW_POLAR_LSD_NLAP2', value=lprops['LSD_NOVERLAP2'])
        lsd_file.add_hkey('KW_POLAR_LSD_NSIG2', value=lprops['LSD_NSIGCLIP2'])
        lsd_file.add_hkey('KW_POLAR_LSD_NWIN2', value=lprops['LSD_NWINDOW2'])
        lsd_file.add_hkey('KW_POLAR_LSD_NMODE2', value=lprops['LSD_NMODE2'])
        lsd_file.add_hkey('KW_POLAR_LSD_NLFIT2', value=lprops['LSD_NLFIT2'])
        # ------------------------------------------------------------------
        # set data
        lsd_file.data = lsd_table
        # update the data type
        lsd_file.datatype = 'table'
        # log that we are saving lsd file
        WLOG(params, '', textentry('40-021-00009', args=[lsd_file.filename]))
        # define multi lists
        data_list, name_list = [], []
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=lsd_file)]
            name_list += ['PARAM_TABLE']
        # write image to file
        lsd_file.write_multi(data_list=data_list, name_list=name_list,
                             block_kind=recipe.out_block_str,
                             runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(lsd_file)


# =============================================================================
# Define worker functions
# =============================================================================
ContinuumReturn = Tuple[np.ndarray, np.ndarray, np.ndarray]


def _continuum(params: ParamDict, xarr: np.ndarray, yarr: np.ndarray,
               binsize: int = 200, overlap: int = 100,
               sigmaclip: float = 3.0, window: int = 3,
               mode: str = "median", use_linear_fit: bool = False,
               telluric_bands: Union[List[float], None] = None,
               outx: Union[np.ndarray, None] = None) -> ContinuumReturn:
    """
    Function to calculate continuum

    :param params: ParamDict, parameter dictionary of constants
    :param xarr: numpy array (1D), input data x data
    :param yarr: numpy array (1D), input data y data (x and y must be of the
                 same size)
    :param binsize: int, number of points in each bin
    :param overlap: int, number of points to overlap with adjacent bins
    :param sigmaclip: float, number of times sigma to cut-off points
    :param window: int, number of bins to use in local fit
    :param mode: string, set combine mode, where mode accepts "median", "mean",
                 "max"
    :param use_linear_fit: bool, whether to use the linar fit
    :param telluric_bands: list of float pairs, list of IR telluric bands, i.e,
                           a list of wavelength ranges ([wl0,wlf]) for telluric
                           absorption
    :param outx: numpy array (1D), the output grid to resample the points onto
                 if None this is xarr

    :return continuum, xbin, ybin
        continuum: numpy array (1D) of the same size as input arrays containing
                   the continuum data already interpolated to the same points
                   as input data.
        xbin,ybin: numpy arrays (1D) containing the bins used to interpolate
                   data for obtaining the continuum
    """
    # set function name
    func_name = display_func('_continuum', __NAME__)
    # -------------------------------------------------------------------------
    # deal with telluric bands
    if telluric_bands is None:
        telluric_bands = []
    # -------------------------------------------------------------------------
    # set output x array to input array (if output x array is None)
    if outx is None:
        outx = xarr
    # -------------------------------------------------------------------------
    # set number of bins given the input array length and the bin size
    nbins = int(np.floor(len(xarr) / binsize)) + 1
    # -------------------------------------------------------------------------
    # initialize arrays to store binned data
    xbin, ybin = [], []
    # loop around bins
    for ibin in range(nbins):
        # get first and last index within the bin
        idx0 = ibin * binsize - overlap
        idxf = (ibin + 1) * binsize + overlap
        # if it reaches the edges then reset indexes
        if idx0 < 0:
            idx0 = 0
        if idxf >= len(xarr):
            idxf = len(xarr) - 1
        # get data within the bin
        xbin_tmp = np.array(xarr[idx0:idxf])
        ybin_tmp = np.array(yarr[idx0:idxf])
        # create mask of telluric bands
        telluric_mask = np.zeros_like(xbin_tmp).astype(bool)
        # loop around each band in tellurics
        for band in telluric_bands:
            # just make sure each band entry is a list (it should be)
            if isinstance(band, list):
                telluric_mask += (xbin_tmp > band[0]) & (xbin_tmp < band[1])
        # ---------------------------------------------------------------------
        # mask data within telluric bands
        xtmp = xbin_tmp[~telluric_mask]
        ytmp = ybin_tmp[~telluric_mask]
        # ---------------------------------------------------------------------
        # create mask to get rid of NaNs
        nanmask = np.isfinite(ytmp)
        # first bin cannot use mean / median
        if ibin == 0 and not use_linear_fit:
            xbin.append(xarr[0] - np.abs(xarr[1] - xarr[0]))
            # create mask to get rid of NaNs
            ybin.append(np.nanmedian(yarr[:binsize]))
        # ---------------------------------------------------------------------
        # if we have more than 2 points we can use mean / median
        if len(xtmp[nanmask]) > 2:
            # calculate mean x within the bin
            xmean = np.nanmean(xtmp)
            # calculate median y within the bin
            medy = np.nanmedian(ytmp)
            # calculate median deviation
            medydev = np.nanmedian(np.abs(ytmp - medy))
            # create mask to filter data outside n*sigma range
            filtermask = (ytmp[nanmask] > medy)
            filtermask &= (ytmp[nanmask] < medy + sigmaclip * medydev)
            # if we still have over 2 points we can use mean / median
            if len(ytmp[nanmask][filtermask]) > 2:
                # save mean x with in bin
                xbin.append(xmean)
                # do a median
                if mode == 'max':
                    # save maximum y of filtered data
                    ybin.append(np.nanmax(ytmp[filtermask]))
                elif mode == 'median':
                    # save median y of filtered data
                    ybin.append(np.nanmedian(ytmp[filtermask]))
                elif mode == 'mean':
                    # save mean y of filtered data
                    ybin.append(np.nanmean(ytmp[filtermask]))
                else:
                    # TODO: move to language database
                    emsg = 'Can not recognize selected mode="{0}"'
                    emsg += '\n\tFunction = {1}'
                    eargs = [mode, func_name]
                    WLOG(params, 'error', emsg.format(*eargs))
        # ---------------------------------------------------------------------
        # if we are dealing with last bin
        if ibin == nbins - 1 and not use_linear_fit:
            xbin.append(xarr[-1] + np.abs(xarr[-1] - xarr[-2]))
            # create mask to get rid of NaNs
            ybin.append(np.nanmedian(yarr[-binsize:]))
    # -------------------------------------------------------------------------
    # Option to use a linearfit within a given window
    if use_linear_fit:
        # initialize arrays to store new bin data
        newxbin, newybin = [], []
        # loop around bins to obtain a linear fit within a given window size
        for ibin in range(len(xbin)):
            # set first and last index to select bins within window
            idx0 = ibin - window
            idxf = ibin + 1 + window
            # make sure it doesnt go over the edges
            if idx0 < 0: idx0 = 0
            if idxf > nbins: idxf = nbins - 1

            # perform linear fit to these data
            lout = stats.linregress(xbin[idx0:idxf], ybin[idx0:idxf])
            slope, intercept, r_value, p_value, std_err = lout
            # if dealing with the first bin
            if ibin == 0:
                # append first point to avoid crazy behaviours in the edge
                newxbin.append(xarr[0] - np.abs(xarr[1] - xarr[0]))
                newybin.append(intercept + slope * newxbin[0])
            # save data obtained from the fit
            newxbin.append(xbin[ibin])
            newybin.append(intercept + slope * xbin[ibin])
            # if dealing with the last bin
            if ibin == len(xbin) - 1:
                # save data obtained from the fit
                newxbin.append(xarr[-1] + np.abs(xarr[-1] - xarr[-2]))
                newybin.append(intercept + slope * newxbin[-1])
        # set x bin and y bin to the new bin values
        xbin, ybin = newxbin, newybin
    # -------------------------------------------------------------------------
    # interpolate points applying an Spline to the bin data
    sfit = UnivariateSpline(xbin, ybin, s=0)
    # sfit.set_smoothing_factor(0.5)
    # Resample interpolation to the original grid
    cont = np.array(sfit(outx))
    # convert xbin and ybin to arrays
    xbin, ybin = np.array(xbin), np.array(ybin)
    # return continuum and x and y bins
    return cont, xbin, ybin


def _fit_continuum(params: ParamDict, recipe: DrsRecipe, wavemap: np.ndarray,
                   spec: np.ndarray, function: str = 'polynomial',
                   degree: int = 3, niter: int = 5, rej_low: float = 2.0,
                   rej_high: float = 2.5, grow=1, med_filt: int = 0,
                   percentile_low: float = 0.0, percentile_high: float = 100.0,
                   min_points: int = 10, verbose: bool = False) -> np.ndarray:
    """
    Continuum fitting re-implemented from IRAF's 'continuum' function
    in non-interactive mode only but with additional options.

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe used to call this function, used
                   to push to plotting function
    :param wavemap: np.array(float) abscissa values
                    (wavelengths, velocities, ...)
    :param spec: array(float) spectrum values
    :param function: str function to fit to the continuum among 'polynomial',
                     'spline3'
    :param degree: int, fit function order:
                   'polynomial': degree (not number of parameters as in IRAF)
                   'spline3': number of knots
    :param niter: int, number of iterations of non-continuum points
                  see also 'min_points' parameter
    :param rej_low: float, rejection threshold in unit of residual standard
                    deviation for point below the continuum
    :param rej_high: float, same as rej_low for point above the continuum
    :param grow: int, number of neighboring points to reject
    :param med_filt: int, median filter the spectrum on 'med_filt' pixels
                     prior to fit improvement over IRAF function 'med_filt'
                     must be an odd integer
                     if value is zero this is not used
    :param percentile_low: float,  reject point below below 'percentile_low'
                           percentile prior to fit improvement over IRAF
                           function  "percentile_low' must be a float between
                           0.0 and 100.0
    :param percentile_high: float  same as percentile_low but reject points in
                            percentile above 'percentile_high'

    :param min_points: int, stop rejection iterations when the number of points
                       to fit is less than 'min_points'

    :param verbose: bool, if true fit information is printed on STDOUT:
                    * number of fit points
                    * RMS residual

    :returns: np.ndarray, the fitted continuum
    """
    # set function name
    func_name = display_func('_fit_continuum', __NAME__)
    # set up a mask - keep array
    mspec = np.ones_like(spec).astype(bool)
    # mask 1st and last point: avoid error when no point is masked [not in IRAF]
    mspec[0] = False
    mspec[-1] = False
    # -------------------------------------------------------------------------
    # mask pixels that are NaNs
    mspec &= np.isfinite(spec)
    # -------------------------------------------------------------------------
    # apply median filtering prior to fit
    # [opt] [not in IRAF]
    if med_filt > 0:
        fspec = signal.medfilt(spec, kernel_size=med_filt)
    else:
        fspec = np.array(spec)
    # -------------------------------------------------------------------------
    # consider only a fraction of the points within percentile range
    # [opt] [not in IRAF]
    lowmask = fspec > np.percentile(fspec, percentile_low)
    highmask = fspec < np.percentile(fspec, percentile_high)
    # add to mspec mask (False out of limits)
    mspec &= lowmask & highmask
    # -------------------------------------------------------------------------
    # perform 1st fit as polynomial
    if function == 'polynomial':
        # calculate polynomial fit on valid points
        coeff = np.polyfit(wavemap[mspec], spec[mspec], degree)
        # get the continuum (from the fit) for all points
        cont = np.polyval(coeff, wavemap)
    # perform 1st fit as spline
    elif function == 'spline3':
        # calculate knots to use in spline
        wavediff = wavemap[-1] - wavemap[0]
        dwavemap = np.arange(degree + 1)[1:] * wavediff / (degree + 1)
        knots = wavemap[0] + dwavemap
        # calculate spline on valid points
        spl = interpolate.splrep(wavemap[mspec], spec[mspec], k=3, t=knots)
        # interpolate over all points
        cont = interpolate.splev(wavemap, spl)
    else:
        # TODO: move to language database
        emsg = 'Function = "{0}" not valid for {1}'
        eargs = [function, func_name]
        WLOG(params, 'error', emsg.format(*eargs))
        cont = None
    # -------------------------------------------------------------------------
    # iteration loop: reject outliers and fit again
    if niter > 0:
        for it in range(niter):
            res = fspec - cont
            sigm = np.std(res[mspec])
            # mask outliers
            mspec1 = np.array(mspec)
            mspec1 &= (res > -rej_low * sigm) & (res < rej_high * sigm)
            # make masked array to do clumping
            maspec1 = np.ma.masked_array(spec, mask=~mspec1)
            # exclude neighbors cf IRAF's continuum parameter 'grow'
            if grow > 0:
                for maskslice in np.ma.clump_masked(maspec1):
                    # get start and stop
                    start = maskslice.start
                    stop = maskslice.stop
                    # loop around all pixels before start and reject these
                    #    pixels too
                    for ii in range(start - grow, start):
                        if ii >= 0:
                            mspec1[ii] = False
                    # loop around all pixels after stop and reject these
                    #                     #    pixels too
                    for ii in range(stop + 1, stop + grow + 1):
                        if ii < len(mspec1):
                            mspec1[ii] = False
            # stop rejection process when min_points is reached
            # [opt] [not in IRAF]
            if np.sum(~mspec1) < min_points:
                if verbose:
                    # TODO: move to language database
                    wmsg = 'Minimum points {0} reached - stopping rejection.'
                    WLOG(params, 'warning', wmsg.format(min_points))
                break
            # copy mask 1 back to primary mask
            mspec = np.array(mspec1)
            # fit again - using polynomial
            if function == 'polynomial':
                # calculate polynomial fit on valid points
                coeff = np.polyfit(wavemap[mspec], spec[mspec], degree)
                # get the continuum (from the fit) for all points
                cont = np.polyval(coeff, wavemap)
            # fit again - using spline
            elif function == 'spline3':

                # calculate knots to use in spline
                wavediff = wavemap[-1] - wavemap[0]
                dwavemap = np.arange(degree + 1)[1:] * wavediff / (degree + 1)
                knots = wavemap[0] + dwavemap
                # calculate spline on valid points
                spl = interpolate.splrep(wavemap[mspec], spec[mspec], k=3,
                                         t=knots)
                # interpolate over all points
                cont = interpolate.splev(wavemap, spl)
            else:
                # TODO: move to language database
                emsg = 'Function = "{0}" not valid for {1}'
                eargs = [function, func_name]
                WLOG(params, 'error', emsg.format(*eargs))
                cont = None
    # compute residual and rms
    res = fspec - cont
    # compute the standard deviation of valid points
    sigm = np.nanstd(res[mspec])
    # print out if verbose
    if verbose:
        # TODO: move to language database
        msg = '\tnfit={0}/{1}\n\tfit RMS={2:.3e}'
        margs = [np.sum(~mspec), len(mspec), sigm]
        WLOG(params, '', msg.format(*margs))
    # compute residual and rms between original spectrum and model
    # different from above when median filtering is applied
    ores = spec - cont
    # get the original spectrum standard deviation
    osigm = np.nanstd(ores[mspec])
    # print out the unfiltered RMS (if we use the median filter)
    if med_filt > 0 and verbose:
        # TODO: move to language database
        msg = '\tUnfiltered RMS={0:.3e}'
        WLOG(params, '', msg.format(osigm))
    # -------------------------------------------------------------------------
    # produce the debug plot for fit continuum
    recipe.plot('POLAR_FIT_CONT', wavemap=wavemap, mask=mspec, spec=spec,
                fspec=fspec, med_filt=med_filt, cont=cont, niter=niter,
                rej_low=rej_low, rej_high=rej_high, sigm=sigm, res=res,
                ores=ores)
    # -------------------------------------------------------------------------
    # return the continuum
    return cont


def _continuum_polarization(params: ParamDict, xarr: np.ndarray,
                            yarr: np.ndarray, binsize: int = 200,
                            overlap: int = 100, mode: str = "median",
                            use_polynomail_fit: bool = True,
                            deg_poly_fit: int = 3,
                            telluric_bands: Union[List[float], None] = None
                            ) -> ContinuumReturn:
    """
    Function to calculate continuum polarization

    :param params: ParamDict, parameter dictionary of constants
    :param xarr: numpy array (1D), input data x data
    :param yarr: numpy array (1D), input data y data (x and y must be of the
                 same size)
    :param binsize: int, number of points in each bin
    :param overlap: int, number of points to overlap with adjacent bins
    :param mode: string, set combine mode, where mode accepts "median", "mean",
                 "max"
    :param telluric_bands: list of float pairs, list of IR telluric bands, i.e,
                           a list of wavelength ranges ([wl0,wlf]) for telluric
                           absorption

    :return continuum, xbin, ybin
        continuum: numpy array (1D) of the same size as input arrays containing
                   the continuum data already interpolated to the same points
                   as input data.
        xbin,ybin: numpy arrays (1D) containing the bins used to interpolate
                   data for obtaining the continuum
    """
    # TODO: this function is almost identical to _continuum
    # TODO:   Question: Can we combine?
    # set function name
    func_name = display_func('_continuum_polarization', __NAME__)
    # -------------------------------------------------------------------------
    # deal with no telluric bands
    if telluric_bands is None:
        telluric_bands = []
    # -------------------------------------------------------------------------
    # set number of bins given the input array length and the bin size
    nbins = int(np.floor(len(xarr) / binsize)) + 1
    # -------------------------------------------------------------------------
    # initialize arrays to store binned data
    xbin, ybin = [], []
    # loop around bins
    for ibin in range(nbins):
        # get first and last index within the bin
        idx0 = ibin * binsize - overlap
        idxf = (ibin + 1) * binsize + overlap
        # if it reaches the edges then reset indexes
        if idx0 < 0:
            idx0 = 0
        if idxf >= len(xarr):
            idxf = len(xarr) - 1
        # ---------------------------------------------------------------------
        # get data within the bin
        xbin_tmp = np.array(xarr[idx0:idxf])
        ybin_tmp = np.array(yarr[idx0:idxf])
        # ---------------------------------------------------------------------
        # create mask of telluric bands
        telluric_mask = np.zeros_like(xbin_tmp).astype(bool)
        # loop around each band in tellurics
        for band in telluric_bands:
            # just make sure each band entry is a list (it should be)
            if isinstance(band, list):
                telluric_mask += (xbin_tmp > band[0]) & (xbin_tmp < band[1])
        # ---------------------------------------------------------------------
        # mask data within telluric bands
        xtmp = xbin_tmp[~telluric_mask]
        ytmp = ybin_tmp[~telluric_mask]
        # ---------------------------------------------------------------------
        # create mask to get rid of NaNs
        nanmask = np.isfinite(ytmp)
        # deal with first bin
        if ibin == 0:
            # append to xbin
            xbin.append(xarr[0] - np.abs(xarr[1] - xarr[0]))
            # create mask to get rid of NaNs
            ybin.append(np.nanmedian(yarr[:binsize]))
        # ---------------------------------------------------------------------
        # if we have over 2 points we can use mean / median
        if len(xtmp[nanmask]) > 2:
            # calculate mean x within the bin
            xmean = np.nanmean(xtmp)
            # save mean x with in bin
            xbin.append(xmean)
            # do a median
            if mode == 'median':
                # save median y of filtered data
                ybin.append(np.nanmedian(ytmp))
            elif mode == 'mean':
                # save mean y of filtered data
                ybin.append(np.nanmean(ytmp))
            else:
                # TODO: move to language database
                emsg = 'Can not recognize selected mode="{0}"'
                emsg += '\n\tFunction = {1}'
                eargs = [mode, func_name]
                WLOG(params, 'error', emsg.format(*eargs))
        # ---------------------------------------------------------------------
        if ibin == nbins - 1:
            xbin.append(xarr[-1] + np.abs(xarr[-1] - xarr[-2]))
            # create mask to get rid of NaNs
            ybin.append(np.nanmedian(yarr[-binsize:]))
    # -------------------------------------------------------------------------
    # the continuum may be obtained either by polynomial fit or by cubic
    # interpolation
    if use_polynomail_fit:
        # Option to use a polynomial fit
        # Fit polynomial function to sample points
        pfit = np.polyfit(xbin, ybin, deg_poly_fit)
        # Evaluate polynomial in the original grid
        cont = np.polyval(pfit, xarr)
    else:
        # option to interpolate points applying a cubic spline to the
        # continuum data
        sfit = interpolate.interp1d(xbin, ybin, kind='cubic')
        # Resample interpolation to the original grid
        cont = sfit(xarr)
    # -------------------------------------------------------------------------
    # make sure continuum return is an array
    cont = np.array(cont)
    # convert xbin and ybin to arrays
    xbin, ybin = np.array(xbin), np.array(ybin)
    # -------------------------------------------------------------------------
    # return continuum polarization and x and y bins
    return cont, xbin, ybin


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
