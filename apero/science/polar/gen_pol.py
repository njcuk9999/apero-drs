#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-25 at 13:25

@author: cook
"""
import numpy as np
import warnings
from typing import Tuple, List, Union

from apero.base import base
from apero.core import math as mp
from apero import lang
from apero.core import constants
from apero.core.core import drs_log, drs_file
from apero.core.core import drs_misc
from apero.core.utils import drs_startup
from apero.core.core import drs_text
from apero.io import drs_table
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
# Define class
# =============================================================================


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


def apero_load_data(params: ParamDict, inputs: List[DrsFitsFile]):

    # loop around exposures

        # need A and B

        # load blaze for file

        # load wave for file


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
        data, errdata = props['FLUXDATA'], props['FLUXERRDATA']
    else:
        data, errdata = props['RAWFLUXDATA'], props['RAWFLUXERRDATA']
    # get the number of exposures
    nexp = float(props['NEXPOSURES'])
    # log start of polarimetry calculations
    # TODO: move to language database
    wmsg = 'Running function {0} to calculate polarization'
    WLOG(params, '', wmsg.format(name))
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store polarimetry variables in loc
    data_shape = props['RAWFLUXDATA']['A_1'].shape
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
        data, errdata = props['FLUXDATA'], props['FLUXERRDATA']
    else:
        data, errdata = props['RAWFLUXDATA'], props['RAWFLUXERRDATA']
    # get the number of exposures
    nexp = float(props['NEXPOSURES'])
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store polarimetry variables in loc
    data_shape = props['RAWFLUXDATA']['A_1'].shape
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
        data, errdata = props['FLUXDATA'], props['FLUXERRDATA']
    else:
        data, errdata = props['RAWFLUXDATA'], props['RAWFLUXERRDATA']
    # get the number of exposures
    nexp = float(props['NEXPOSURES'])
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store Stokes I variables in loc
    data_shape = props['FLUXDATA']['A_1'].shape
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
        var_ab = errdata[a_exp] ** 2 + errdata[b_exp]**2
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
