#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-25 at 13:25

@author: cook
"""
from astropy.table import Table
from astropy import units as uu
import numpy as np
import os
from scipy import interpolate
from scipy import stats
from scipy import signal
from scipy.interpolate import UnivariateSpline
from typing import Any, List, Tuple, Union
import warnings

from apero.base import base
from apero.core import math as mp
from apero import lang
from apero.core import constants
from apero.core.core import drs_database
from apero.core.core import drs_log
from apero.core.core import drs_file
from apero.core.core import drs_text
from apero.core.utils import drs_recipe
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
    2. "RAW_FLUX"    = flux / blaze
    3. "RAW_FLUXERR" = np.sqrt(flux) / blaze
    4. "FLUX"       = interp flux / interp blaze onto same wave as exp1
    5. "FLUXERR"    = np.sqrt(interp flux ) / interp blaze onto same wave
                          as exp1

    # other things to save
    # - STOKES:   CMMTSEQ.split(' ')[0]
    # - EXPOSURE:  CMMTSEQ.split(' ')[1]  or UNDEF
    # - NEXPOSURES:   4

    # data to save once
    # - OBJNAME:   from header of exp 1:  OBJECT (should be DRSOBJN)
    # - OBJTEMP:   from header of exp 1:  OBJ_TEMP -> deal with no key = 0.0

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
    # save global stokes value
    polar_dict['GLOBAL_STOKES'] = None
    # wave solution common to all non-raw data
    polar_dict['GLOBAL_WAVEMAP'] = None
    polar_dict['GLOBAL_WAVEFILE'] = None
    polar_dict['GLOBAL_WAVETIME'] = None
    # save a blaze file
    polar_dict['GLOBAL_BLAZE'] = None
    polar_dict['GLOBAL_BLAZEFILE'] = None
    # save timing and berv information
    polar_dict['EXPTIMES'] = dict()
    polar_dict['MJDATES'] = dict()
    polar_dict['MJDMIDS'] = dict()
    polar_dict['MJDENDS'] = dict()
    polar_dict['BERVS'] = dict()
    polar_dict['BJDS'] = dict()
    polar_dict['BERV_USED_ESTIMATE'] = dict()
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
    keys = ['INPUTS', 'EXPTIMES', 'MJDATES', 'MJDMIDS', 'MJDENDS',
            'BERVS', 'BJDS', 'BERV_USED_ESTIMATE',
            'EXPOSURES', 'N_EXPOSURES', 'EXPOSURE_NUMBERS', 'STOKES',
            'GLOBAL_WAVEMAP', 'GLOBAL_WAVEFILE', 'GLOBAL_WAVETIME',
            'GLOBAL_BLAZE', 'GLOBAL_BLAZEFILE', 'GLOBAL_STOKES',
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
    objnames, objtemps = [], []
    # loop around exposures and work out stokes parameters
    for expfile in inputs:
        # get the stokes type and exposure number from header
        stoke, exp_num = pconst.GET_STOKES_FROM_HEADER(params, expfile.header,
                                                       WLOG)
        # get the objname
        objname = expfile.get_hkey('KW_OBJNAME', dtype=str)
        # get the obj temperatures
        objtemp = expfile.get_hkey('KW_OBJ_TEMP', dtype=float, required=False)
        if objtemp is None:
            objtemp = 0.0
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
        objnames.append(objname)
        objtemps.append(objtemp)
    # -------------------------------------------------------------------------
    # deal with multiple stokes parameters
    if len(np.unique(stokes)) != 1:
        # TODO: move to language database
        emsgs = 'Identified more than one stokes parameters in input data.'
        for it in range(len(stokes)):
            emsg = '\n\tFile {0}\tExp {1}\tStokes:{2}'
            emsg = emsg.format(basenames[it], exp_nums[it], stokes[it])
            emsgs += emsg
        WLOG(params, 'error', emsgs)
    else:
        polar_dict['GLOBAL_STOKES'] = stokes[0]
    # -------------------------------------------------------------------------
    # deal with multiple object names
    if len(np.unique(objnames)) != 1:
        # TODO: move to language database
        emsgs = 'Object name from header ({0}) not consistent between files'
        emsgs = emsgs.format(params['KW_OBJNAME'][0])
        for it in range(len(objnames)):
            emsg = '\n\tFile {0}\t{1}={2}'
            eargs = [basenames[it], params['KW_OBJNAME'][0], objnames[it]]
            emsg = emsg.format(*eargs)
            emsgs += emsg
        WLOG(params, 'error', emsgs)
    # set object name
    object_name = objnames[0]
    # -------------------------------------------------------------------------
    # deal with multiple temperatures
    if len(np.unique(objtemps)) != 1:
        wmsgs = 'Object temperatures do not match - taking finite median'
        for it in range(len(objtemps)):
            wmsg = '\n\tFile {0}\t{1}={2}'
            wargs = [basenames[it], params['KW_OBJ_TEMP'][0], objtemps[it]]
            wmsg = wmsg.format(*wargs)
            wmsgs += wmsg
        WLOG(params, 'warning', wmsgs)
        # set the object temperature
        object_temperature = np.nanmedian(objtemps)
    else:
        # set the object temperature
        object_temperature = objtemps[0]
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
            # -----------------------------------------------------------------
            # load the blaze file
            bout = flat_blaze.get_blaze(params, expfile.header,
                                        expfile.fiber, database=calibdb)
            blazefile, blaze = bout
            # add the global wave solution to polar dict
            polar_dict['GLOBAL_BLAZE'] = blaze
            polar_dict['GLOBAL_BLAZEFILE'] = blazefile

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
                # get parameters
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
            # add the input for this key
            polar_dict['INPUTS'][key_str] = infile.newcopy(params=params)
            # -----------------------------------------------------------------
            # load the blaze file
            _, blaze = flat_blaze.get_blaze(params, infile.header, fiber,
                                            database=calibdb)
            # get normalized blaze data
            # TODO: Question: why is this blaze normalized but the blaze you
            # TODO: Question: save later is not? polar_dict['GLOBAL_BLAZE']
            blaze = blaze / np.nanmax(blaze)
            # -----------------------------------------------------------------
            # load wave for file
            wprops = wave.get_wavesolution(params, recipe, fiber=fiber,
                                           infile=infile, database=calibdb)
            # -----------------------------------------------------------------
            # add timings to polar dictionary
            # -----------------------------------------------------------------
            # add exposure time
            exptime = expfile.get_hkey('KW_EXPTIME', dtype=float)
            polar_dict['EXPTIMES'][key_str] = exptime
            # add mjdate
            mjdate = expfile.get_hkey('KW_MJDATE', dtype=float)
            polar_dict['MJDATES'][key_str] = mjdate
            # add mid exposure time
            mjdmid = expfile.get_hkey('KW_MID_OBS_TIME', dtype=float)
            polar_dict['MJDMIDS'][key_str] = mjdmid
            # add mjdend
            mjdend = expfile.get_hkey('KW_MJDEND', dtype=float)
            polar_dict['MJDENDS'][key_str] = mjdend
            # -----------------------------------------------------------------
            # deal with BERV and BJD
            # -----------------------------------------------------------------
            # get all berv properties from expfile
            bprops = extract.get_berv(params, expfile, log=False)
            # apply a berv correction if requested
            if berv_correct:
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
            # add berv properties to polar dictionary
            polar_dict['BERVS'][key_str] = bprops['USE_BERV']
            polar_dict['BJDS'][key_str] = bprops['USE_BJD']
            polar_dict['BERV_USED_ESTIMATE'][key_str] = bprops['USED_ESTIMATE']
            # -----------------------------------------------------------------
            # add the global wave solution to polar dict
            polar_dict['RAW_WAVEMAP'][key_str] = wavemap
            # add the global wave filename solution to polar dict
            polar_dict['RAW_WAVEFILE'][key_str] = str(wprops['WAVEFILE'])
            # add the global wave time solution to polar dict
            polar_dict['RAW_WAVETIME'][key_str] = str(wprops['WAVETIME'])
            # -----------------------------------------------------------------
            # get the raw data
            raw_flux = np.array(infile.data) / blaze
            # get the raw data errors
            with warnings.catch_warnings(record=True) as _:
                raw_fluxerr = np.sqrt(np.array(infile.data))
            # TODO: Question: here you sqrt(flux)/blaze after sqrt(flux/blaze)
            raw_fluxerr = raw_fluxerr / blaze
            # -----------------------------------------------------------------
            # get global wave
            gwavemap = polar_dict['GLOBAL_WAVEMAP']
            # get interpolated data
            flux, fluxerr = get_interp_flux(wavemap0=wavemap,
                                            flux0=np.array(infile.data),
                                            blaze0=blaze, wavemap1=gwavemap)
            # -----------------------------------------------------------------
            # add raw_flux, raw_fluxerr, flux, fluxerror to polar dict
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
    # add object name and temperature to polar dictionary
    polar_dict['OBJECT_NAME'] = object_name
    polar_dict['OBJECT_TEMPERATURE'] = object_temperature
    # set source
    polar_dict.set_sources(['OBJECT_NAME', 'OBJECT_TEMPERATURE'], func_name)
    # -------------------------------------------------------------------------
    # return the polar dictionary
    return polar_dict


def calculate_polar_times(props: ParamDict) -> ParamDict:
    """
    Calculate the mean times for the polar sequence

    :param props: ParamDict, the parameter dictionary of data

    :return: ParamDict, the updated "props" parameter dictionary of data
    """
    # set function name
    func_name = display_func('calculate_polar_times', __NAME__)
    # get exposures from props
    exposures = props['INPUTS']
    # storage for use
    fluxes = dict()
    exptimes, mjdates, mjdmids, mjdends, bjds, bervs = [], [], [], [], [], []
    # -------------------------------------------------------------------------
    # get the timings from props for all exposures add to storage
    for key_str in exposures:
        # get exposure number for this key string
        exposure_num = key_str.split('_')[-1]
        # get mean flux
        if exposure_num in fluxes:
            fluxes[exposure_num].append(props['RAW_FLUX'][key_str])
            # the rest of the parameters are only added once per exposure
            continue
        else:
            fluxes[exposure_num] = [props['RAW_FLUX'][key_str]]
        # add exposure time
        exptimes.append(props['EXPTIMES'][key_str])
        # add mjdate
        mjdates.append(props['MJDATES'][key_str])
        # add mid exposure time
        mjdmids.append(props['MJDMIDS'][key_str])
        # add mjend
        mjdends.append(props['MJDENDS'][key_str])
        # add bjd
        bjds.append(props['BJDS'][key_str])
        # add bervs
        bervs.append(props['BERVS'][key_str])
    # -------------------------------------------------------------------------
    # convert to arrays
    exptimes, mjdates = np.array(exptimes), np.array(mjdates)
    mjdmids, mjdends = np.array(mjdmids), np.array(mjdends)
    bjds, bervs = np.array(bjds), np.array(bervs)
    # -------------------------------------------------------------------------
    # calculate mean flux for each exposure
    mean_fluxes = []
    for exp_num in fluxes:
        mean_fluxes.append(np.nanmean(fluxes[exp_num]))
    # -------------------------------------------------------------------------
    # calculate total exposure time
    total_time = np.nansum(exptimes)
    # -------------------------------------------------------------------------
    # calculate elapsed time (in days)
    elapsed_time = (np.max(bjds) - np.min(bjds)) * uu.day
    # convert to seconds
    elapsed_time = elapsed_time.to(uu.s).value
    # add half first exptime and half last exptime to get full elapsed time
    elapsed_time += (exptimes[0] / 2) + (exptimes[-1] / 2)
    # -------------------------------------------------------------------------
    # MJDMID
    # -------------------------------------------------------------------------
    # calculate the flux-weighted MJDMID of polarimetric sequence
    mjd_fw_cen = np.sum(mean_fluxes * mjdmids) / np.sum(mean_fluxes)
    # calculate the MJD at center of polarimetric sequence
    mjdstart = mjdmids[0] - (exptimes[0] * uu.day / 2).to(uu.s).value
    mjdend = mjdmids[-1] + (exptimes[-1] * uu.day / 2).to(uu.s).value
    mjdcen = mjdstart + (mjdend - mjdstart) / 2
    # calculate the mean MJD
    mean_mjd = np.mean(mjdmids)
    # -------------------------------------------------------------------------
    # BERV and BJD
    # -------------------------------------------------------------------------
    # calculate the flux-weighted bjd of polarimetric sequence
    bjd_fw_cen = np.sum(mean_fluxes * bjds) / np.sum(mean_fluxes)
    # calculate the BJD at center of polarmetric sequence
    bjdstart = bjds[0] - (exptimes[0] * uu.day / 2).to(uu.s).value
    bjdend = bjds[-1] + (exptimes[-1] * uu.day / 2).to(uu.s).value
    bjdcen = bjdstart + (bjdend - bjdstart) / 2
    # linear interpolation
    berv_slope = (bervs[-1] - bervs[0]) / (bjds[-1] - bjds[0])
    berv_intercept = bervs[0] - berv_slope * bjds[0]
    bervcen = (berv_slope * bjdcen) + berv_intercept
    # calculate mean berv
    mean_berv = np.nanmean(bervs)
    # calculate mean bjd
    mean_bjd = np.nanmean(bjds)
    # -------------------------------------------------------------------------
    # add to props
    props['ELAPSED_TIME'] = elapsed_time
    props['MJDCEN'] = mjdcen
    props['BJDCEN'] = bjdcen
    props['BERVCEN'] = bervcen
    props['MEANMJD'] = mean_mjd
    props['MEANBJD'] = mean_bjd
    props['TOTEXPTIME'] = total_time
    props['MJDFWCEN'] = mjd_fw_cen
    props['BJDFWCEN'] = bjd_fw_cen
    props['MEANBERV'] = mean_berv
    # set sources
    keys = ['ELAPSED_TIME', 'MJDCEN', 'BJDCEN', 'BERVCEN', 'MEANBJD', 'MEANMJD',
            'MEANBJD', 'TOTEXPTIME', 'MJDFWCEN', 'BJDFWCEN', 'MEANBERV']
    props.set_sources(keys, func_name)
    # -------------------------------------------------------------------------
    # return update parameter dictionary of properties
    return props


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
    :param polar_method: str or None, if set overrides POLAR_METHOD from
                         parameter dictionary

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
            props['RAW_FLUX']: numpy array (2D) containing the e2ds flux
                                data for all exposures {1,..,NEXPOSURES},
                                and for all fibers {A,B}
            props['RAW_FLUXERR']: numpy array (2D) containing the e2ds flux
                                   error data for all exposures
                                   {1,..,NEXPOSURES}, and for all fibers {A,B}
            props['NEXPOSURES']: number of polarimetry exposures

    :param interp_flux: bool or None, if set overrides POLAR_INTERPOLATE_FLUX
                        from parameter dictionary

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
        props['RAW_FLUX']: numpy array (2D) containing the e2ds flux data
                              for all exposures {1,..,NEXPOSURES}, and for all
                              fibers {A,B}
        props['RAW_FLUXERR']: numpy array (2D) containing the e2ds flux
                                 error data for all exposures {1,..,NEXPOSURES},
                                 and for all fibers {A,B}
        props['NEXPOSURES']: number of polarimetry exposures

    :param interp_flux: bool or None, if set overrides POLAR_INTERPOLATE_FLUX
                        from parameter dictionary

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

    :param interp_flux: bool or None, if set overrides POLAR_INTERPOLATE_FLUX
                        from parameter dictionary

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

    stokesi_arr = np.sum(flux, axis=0)
    stokesierr_arr = np.sum(var, axis=0)

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
            # TODO: Question: here you sqrt(flux/blaze) before sqrt(flux)/blaze
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
    # print progress
    # TODO: move to language database
    msg = 'Calculating Stokes I using {0}'
    margs = [stokesi_detection_alg]
    WLOG(params, '', msg.format(*margs))
    # -------------------------------------------------------------------------
    # calculate continuum flux using moving median
    if stokesi_detection_alg == 'MOVING_MEDIAN':
        # calculate continuum flux
        cout = continuum(params, xdata, stokes_i, binsize=pol_binsize,
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
    # print progress
    # TODO: move to language database
    msg = 'Calculating polar using {0}'
    margs = [polar_detection_alg]
    WLOG(params, '', msg.format(*margs))
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


def remove_continuum_polarization(props: ParamDict) -> ParamDict:
    """
        Function to remove the continuum polarization

        :param props: parameter dictionary, ParamDict containing data

        Must contain at least:
            WAVE: numpy array (2D), e2ds wavelength data
            POL: numpy array (2D), e2ds degree of polarization data
            POLERR: numpy array (2D), e2ds errors of degree of polarization
            FLAT_X: numpy array (1D), flatten polarimetric x data
            CONT_POL: numpy array (1D), e2ds continuum polarization data

        :return props: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                POL: numpy array (2D), e2ds degree of polarization data
                ORDER_CONT_POL: numpy array (2D), e2ds degree of continuum
                polarization data
    """
    # set function name
    func_name = display_func('remove_continuum_polarization', __NAME__)
    # get arrays
    xdata = props['FLAT_X']
    pol = props['POL']
    wavemap = props['GLOBAL_WAVEMAP']
    cont_pol = props['CONT_POL']
    # get the shape of pol
    ydim, xdim = props['POL'].shape
    # initialize continuum empty array
    order_cont_pol = np.full((ydim, xdim), np.nan)
    # ---------------------------------------------------------------------
    # interpolate and remove continuum (across orders)
    # loop around order data
    for order_num in range(ydim):
        # get wavelengths for current order
        ordwave = wavemap[order_num]
        # get polarimetry for current order
        ordpol = pol[order_num]
        # get wavelength at edges of order
        wl0, wlf = ordwave[0], ordwave[-1]
        # create mask to get only continuum data within wavelength range
        # TODO: Question - this doesn't work with in_wavelength = False
        wlmask = (xdata >= wl0) & (xdata <= wlf)
        # get continuum data within order range
        wl_cont = xdata[wlmask]
        pol_cont = cont_pol[wlmask]
        # interpolate points applying a cubic spline to the continuum data
        pol_interp = interpolate.interp1d(wl_cont, pol_cont, kind='cubic')
        # create continuum vector at same wavelength sampling as polar data
        cont_vector = pol_interp(ordwave)
        # save continuum with the same shape as input pol
        order_cont_pol[order_num] = cont_vector
        # remove continuum from data
        ordpol = ordpol - cont_vector
        # update pol array
        pol[order_num] = ordpol
    # -------------------------------------------------------------------------
    # update POL
    props['POL'] = pol
    props.append_source('POL', func_name)
    # Add ORDER_CONT_POL
    props.set('ORDER_CONT_POL', value=order_cont_pol, source=func_name)
    # -------------------------------------------------------------------------
    return props


def normalize_stokes_i(props: ParamDict) -> ParamDict:
    """
        Function to normalize Stokes I by the continuum flux

        :param props: parameter dictionary, ParamDict containing data
            Must contain at least:
                WAVE: numpy array (2D), e2ds wavelength data
                STOKESI: numpy array (2D), e2ds degree of polarization data
                POLERR: numpy array (2D), e2ds errors of degree of polarization
                FLAT_X: numpy array (1D), flatten polarimetric x data
                CONT_POL: numpy array (1D), e2ds continuum polarization data

        :return loc: parameter dictionary, the updated parameter dictionary
            Adds/updates the following:
                STOKESI: numpy array (2D), e2ds Stokes I data
                STOKESIERR: numpy array (2D), e2ds Stokes I error data
                ORDER_CONT_FLUX: numpy array (2D), e2ds flux continuum data
        """
    # set function name
    func_name = display_func('normalize_stokes_i', __NAME__)
    # get arrays
    xdata = props['FLAT_X']
    stokesi = props['STOKESI']
    stokesierr = props['STOKESIERR']
    wavemap = props['GLOBAL_WAVEMAP']
    cont_flux = props['CONT_FLUX']
    # get the shape of pol
    ydim, xdim = stokesi.shape
    # initialize continuum empty array
    order_cont_flux = np.full(stokesi.shape, np.nan)
    # ---------------------------------------------------------------------
    # interpolate and remove continuum (across orders)
    # loop around order data
    for order_num in range(ydim):
        # get wavelengths for current order
        ordwave = wavemap[order_num]
        # get wavelength at edges of order
        wl0, wlf = ordwave[0], ordwave[-1]
        # get polarimetry for current order
        flux = stokesi[order_num]
        fluxerr = stokesierr[order_num]
        # create mask to get only continuum data within wavelength range
        # TODO: Question - this doesn't work with in_wavelength = False
        wlmask = (xdata >= wl0) & (xdata <= wlf)
        # get continuum data within order range
        wl_cont = xdata[wlmask]
        flux_cont = cont_flux[wlmask]
        # interpolate points applying a cubic spline to the continuum data
        flux_interp = interpolate.interp1d(wl_cont, flux_cont, kind='cubic')
        # create continuum vector at same wavelength sampling as polar data
        _continuum = flux_interp(ordwave)
        # save continuum with the same shape as input pol
        order_cont_flux[order_num] = _continuum
        # normalize stokes I by the continuum
        stokesi[order_num] = flux / _continuum
        # normalize stokes I by the continuum
        stokesierr[order_num] = fluxerr / _continuum
    # -------------------------------------------------------------------------
    # update stokesi and stokesierr
    props['STOKESI'] = stokesi
    props['STOKESIERR'] = stokesierr
    # add to sources
    props.append_source('STOKESI', func_name)
    props.append_source('STOKESIERR', func_name)
    # -------------------------------------------------------------------------
    # add order cont flux
    props.set('ORDER_CONT_FLUX', order_cont_flux, source=func_name)
    # -------------------------------------------------------------------------
    # return props
    return props


def clean_polarimetry_data(props: ParamDict, sigclip: bool = False,
                           nsig: int = 3, overwrite: bool = False) -> ParamDict:
    """
    Function to clean polarimetry data.

    :param props: parameter dictionary, ParamDict to store data
        Must contain at least:
            GLOBAL_WAVEMAP: numpy array (2D), wavelength data
            STOKESI: numpy array (2D), Stokes I data
            STOKESIERR: numpy array (2D), errors of Stokes I
            POL: numpy array (2D), degree of polarization data
            POLERR: numpy array (2D), errors of degree of polarization
            NULL1 :numpy array (2D), 1st null polarization
            NULL2 :numpy array (2D), 2nd null polarization
            CONT_FLUX:
            CONT_POL:

    :param sigclip: bool, switch if True does the sigma clip
    :param nsig: int, the number of sigmas to clip at
    :param overwrite: bool, if True updates original arrays with NaNs where
                      values are sigma clipped in CLEAN_ data

    :return loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
            CLEAN_GLOBAL_WAVEMAP: numpy array (1D), wavelength data
            CLEAN_STOKESI: numpy array (1D), Stokes I data
            CLEAN_STOKESIERR: numpy array (1D), errors of Stokes I
            CLEAN_POL: numpy array (1D), degree of polarization data
            CLEAN_POLERR: numpy array (1D), errors of polarization
            CLEAN_NULL1: numpy array (1D), 1st null polarization
            CLEAN_NULL2: numpy array (1D), 2nd null polarization

            if overwrite is True, updates:
                GLOBAL_WAVEMAP: numpy array (1D), wavelength data
                STOKESI: numpy array (1D), Stokes I data
                STOKESIERR: numpy array (1D), errors of Stokes I
                POL: numpy array (1D), degree of polarization data
                POLERR: numpy array (1D), errors of polarization
                NULL1: numpy array (1D), 1st null polarization
                NULL2: numpy array (1D), 2nd null polarization


    """
    # set function name
    func_name = display_func('clean_polarimetry_data', __NAME__)
    # -------------------------------------------------------------------------
    # get input arrays
    wavemap = props['GLOBAL_WAVEMAP']
    stokesi, stokesierr = props['STOKESI'], props['STOKESIERR']
    pol, polerr = props['POL'], props['POLERR']
    null1, null2 = props['NULL1'], props['NULL2']
    cont_pol, cont_flux = props['ORDER_CONT_POL'], props['ORDER_CONT_FLUX']
    # -------------------------------------------------------------------------
    # get shape
    ydim, xdim = pol.shape
    # -------------------------------------------------------------------------
    # store clean data
    clean_wavemap = []
    clean_stokesi, clean_stokesierr = [], []
    clean_pol, clean_polerr = [], []
    clean_null1, clean_null2 = [], []
    clean_cont_pol, clean_cont_flux = [], []
    # -------------------------------------------------------------------------
    # loop over each order
    for order_num in range(ydim):
        # mask NaN values
        mask = np.isfinite(stokesi[order_num])
        mask &= np.isfinite(stokesierr[order_num])
        mask &= np.isfinite(pol[order_num]) & np.isfinite(polerr[order_num])
        mask &= np.isfinite(null1[order_num]) & np.isfinite(null2[order_num])
        # make values where stokes I is positive
        mask &= stokesi[order_num] > 0
        # ---------------------------------------------------------------------
        # if user wants to sigma clip do add the sigma clip to mask
        if sigclip:
            # calcualte meidan of the polar array
            median_pol = np.median(pol[order_num][mask])
            # calculate the median sigma
            # TODO: Question: where does 0.67499 come from?
            meddiff = pol[order_num][mask] - median_pol
            medsig_pol = np.median(np.abs(meddiff)) / 0.67499
            # add this to mask
            mask &= pol[order_num] > (median_pol - (nsig * medsig_pol))
            mask &= pol[order_num] < (median_pol + (nsig * medsig_pol))
        # ---------------------------------------------------------------------
        # append this cleaned data on to our clean storage
        # do this as lists (more efficient than numpy)
        clean_wavemap += list(wavemap[order_num][mask])
        clean_stokesi += list(stokesi[order_num][mask])
        clean_stokesierr += list(stokesierr[order_num][mask])
        clean_pol += list(pol[order_num][mask])
        clean_polerr += list(polerr[order_num][mask])
        clean_null1 += list(null1[order_num][mask])
        clean_null2 += list(null2[order_num][mask])
        clean_cont_pol += list(cont_pol[order_num][mask])
        clean_cont_flux += list(cont_flux[order_num][mask])
        # deal with updating original arrays
        if overwrite:
            wavemap[order_num][~mask] = np.nan
            pol[order_num][~mask] = np.nan
            polerr[order_num][~mask] = np.nan
            stokesi[order_num][~mask] = np.nan
            stokesierr[order_num][~mask] = np.nan
            null1[order_num][~mask] = np.nan
            null2[order_num][~mask] = np.nan
    # -------------------------------------------------------------------------
    # sort by wavelength (or pixel number)
    sortmask = np.argsort(clean_wavemap)
    # save FLAT_X back to props
    props['FLAT_X'] = np.array(clean_wavemap)[sortmask]
    props.append_source('FLAT_X', func_name)
    # save FLAT_POL back to props
    props['FLAT_POL'] = np.array(clean_pol)[sortmask]
    props.append_source('FLAT_POL', func_name)
    # save FLAT_POLERR back to props
    props['FLAT_POLERR'] = np.array(clean_polerr)[sortmask]
    props.append_source('FLAT_POLERR', func_name)
    # save FLAT_STOKESI back to props
    props['FLAT_STOKESI'] = np.array(clean_stokesi)[sortmask]
    props.append_source('FLAT_STOKESI', func_name)
    # save FLAT_STOKESIERR back to props
    props['FLAT_STOKESIERR'] = np.array(clean_stokesierr)[sortmask]
    props.append_source('FLAT_STOKESIERR', func_name)
    # save FLAT_NULL1 back to props
    props['FLAT_NULL1'] = np.array(clean_null1)[sortmask]
    props.append_source('FLAT_NULL1', func_name)
    # save FLAT_NULL2 back to props
    props['FLAT_NULL2'] = np.array(clean_null2)[sortmask]
    props.append_source('FLAT_NULL2', func_name)
    # save CONT_POL back to props
    props['CONT_POL'] = np.array(clean_cont_pol)[sortmask]
    props.append_source('CONT_POL', func_name)
    # save CONT_FLUX back to props
    props['CONT_FLUX'] = np.array(clean_cont_flux)[sortmask]
    props.append_source('CONT_FLUX', func_name)
    # -------------------------------------------------------------------------
    # return props
    return props


# =============================================================================
# Define quality control and writing functions
# =============================================================================
def make_s1d(params: ParamDict, recipe: DrsRecipe,
             props: ParamDict) -> ParamDict:
    """
    Make the 1D spectra from the 2D spectra in props

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe:
    :param props:
    :return:
    """
    # set function name
    func_name = display_func('make_s1d', __NAME__)
    # get wavemap and blaze from props
    wavemap = props['GLOBAL_WAVEMAP']
    blaze = props['GLOBAL_BLAZE']
    # define the s1d file types to produce
    s1dtypes = ['STOKESI', 'POL', 'NULL1', 'NULL2']
    # get error maps (for each s1d file type)
    e2dserrs = dict(STOKESI=props['STOKESIERR'], POL=props['POLERR'],
                    NULL1=None, NULL2=None)
    # store s1d props
    s1dprops = ParamDict()
    # loop around the s1d files
    for s1dfile in s1dtypes:
        # loop around s1d grids
        for grid in ['wave', 'velocity']:
            # store s1d
            skey = 'S1D{0}_{1}'.format(grid[0].upper(), s1dfile)
            # log progress
            # TODO: Move to language database
            msg = 'Creating {0} file'
            margs = [skey]
            WLOG(params, 'info', msg.format(*margs))
            # get e2ds
            e2ds = np.array(props[s1dfile])
            # need to uncorrect for the blaze
            e2ds = e2ds * blaze
            # compute s1d
            sargs = [wavemap, e2ds, blaze]
            sprops = extract.e2ds_to_s1d(params, recipe, *sargs, wgrid=grid,
                                         s1dkind=s1dfile,
                                         e2dserr=e2dserrs[s1dfile])
            s1dprops[skey] = sprops
            s1dprops.set_source(skey, func_name)
            # -----------------------------------------------------------------
            # plot only for wave grid
            if grid == 'wave':
                # plot the debug plot
                recipe.plot('EXTRACT_S1D', params=params, props=sprops,
                            fiber=None, kind=s1dfile)
                # plot the summary plot
                recipe.plot('SUM_EXTRACT_S1D', params=params, props=sprops,
                            fiber=None, kind=s1dfile)
    # -------------------------------------------------------------------------
    # return s1d props
    return s1dprops


def quality_control(params) -> Tuple[List[List[Any]], bool]:
    """
    Quality control for the polar recipe
    - currently blank

    :param params: ParamDict, the parameter dictionary of constants

    :return: tuple, 1. list of quality control parameters for header, 2. whether
             quality control passed or failed
    """
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


WriteOut = Tuple[DrsFitsFile, DrsFitsFile, Table]


def write_files(params: ParamDict, recipe: DrsRecipe, props: ParamDict,
                inputs: List[DrsFitsFile], s1dprops: ParamDict,
                qc_params: List[List[Any]]) -> WriteOut:
    """
    Write the POL, STOKESI, NULL1, NULL2 data to disk

    :param params: ParamDict, the parameter dictionary of constants
    :param recipe: DrsRecipe, the reicpe that called this function
    :param props: ParamDict, the parameter dictionary of data
    :param inputs: list, the input dictionary of DrsFitsFiles
    :param s1dprops: ParamDict, the parameter dictionary for s1d files
    :param qc_params: list of lists, the quality control criteria lists

    :return: None - writes files to disk
    """
    # set the function name
    _ = display_func('write_files', __NAME__)
    # get data from props
    pol_data = props['POL']
    polerr_data = props['POLERR']
    stokesi_data = props['STOKESI']
    stokesierr_data = props['STOKESIERR']
    null1_data = props['NULL1']
    null2_data = props['NULL2']
    # ----------------------------------------------------------------------
    # get the raw files inputted by user
    rawfiles1 = []
    for drsfile in inputs:
        # extract the basename from raw file
        rawfiles1.append(drsfile.basename)
    # get the files used in polarimetry
    rawfiles2 = []
    for key_str in props['INPUTS']:
        # get drs file for this input
        drsfile = props['INPUTS'][key_str]
        # extract the basename from raw file
        rawfiles2.append(drsfile.basename)
    # ----------------------------------------------------------------------
    # get first file - for reference
    infile0 = inputs[0]
    # ----------------------------------------------------------------------
    # Create combined
    # ----------------------------------------------------------------------
    cout = drs_file.combine(params, recipe, inputs, math='None', save=False)
    cfile, ctable = cout

    # ----------------------------------------------------------------------
    # Write pol to file to disk
    # ----------------------------------------------------------------------
    # get a new copy of the pol file
    polfile = recipe.outputs['POL_DEG_FILE'].newcopy(params=params)
    # construct the filename from file instance
    polfile.construct_filename(infile=cfile)
    # define header keys for output file
    # copy keys from input file
    polfile.copy_original_keys(cfile)
    # add version
    polfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    polfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    polfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    polfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    polfile.add_hkey('KW_OUTPUT', value=polfile.name)
    # must set the KW_IDENTIFIER (equal to the first file)
    identifier0 = infile0.get_hkey('KW_IDENTIFIER', dtype=str)
    polfile.add_hkey('KW_IDENTIFIER', value=identifier0)
    # add input files
    polfile.add_hkey_1d('KW_INFILE1', values=rawfiles1, dim1name='file')
    polfile.add_hkey_1d('KW_INFILE2', values=rawfiles2, dim1name='file')
    # add wave and blaze used
    polfile.add_hkey('KW_CDBWAVE', value=props['GLOBAL_WAVEFILE'])
    polfile.add_hkey('KW_CDBBLAZE', value=props['GLOBAL_BLAZEFILE'])
    # add qc parameters
    polfile.add_qckeys(qc_params)
    # add polar header keys
    polfile = add_polar_keywords(params, props, polfile)
    # add data
    polfile.data = pol_data
    # log that we are saving pol file
    WLOG(params, '', textentry('40-021-00005', args=[polfile.filename]))
    # define multi lists
    data_list = [polerr_data, ctable]
    datatype_list = ['image', 'table']
    name_list = ['POL_ERR', 'POL_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=polfile)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write image to file
    polfile.write_multi(data_list=data_list, name_list=name_list,
                        datatype_list=datatype_list,
                        block_kind=recipe.out_block_str,
                        runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(polfile)
    # ----------------------------------------------------------------------
    # Write Stokes I to file to disk
    # ----------------------------------------------------------------------
    # get a new copy of the pol file
    stokesfile = recipe.outputs['POL_STOKESI'].newcopy(params=params)
    # construct the filename from file instance
    stokesfile.construct_filename(infile=cfile)
    # copy header from pol file
    stokesfile.copy_hdict(polfile)
    # add output tag
    stokesfile.add_hkey('KW_OUTPUT', value=stokesfile.name)
    # add data
    stokesfile.data = stokesi_data
    # log that we are saving pol file
    WLOG(params, '', textentry('40-021-00008', args=[stokesfile.filename]))
    # define multi lists
    data_list = [stokesierr_data, ctable]
    datatype_list = ['image', 'table']
    name_list = ['STOKESI_ERR', 'POL_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=stokesfile)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write image to file
    stokesfile.write_multi(data_list=data_list, name_list=name_list,
                           datatype_list=datatype_list,
                           block_kind=recipe.out_block_str,
                           runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(stokesfile)
    # ----------------------------------------------------------------------
    # Write null 1 data to disk
    # ----------------------------------------------------------------------
    # get a new copy of the pol file
    null1file = recipe.outputs['POL_NULL1'].newcopy(params=params)
    # construct the filename from file instance
    null1file.construct_filename(infile=cfile)
    # copy header from pol file
    null1file.copy_hdict(polfile)
    # add output tag
    null1file.add_hkey('KW_OUTPUT', value=null1file.name)
    # add data
    null1file.data = null1_data
    # log that we are saving null 1 file
    WLOG(params, '', textentry('40-021-00006', args=[null1file.filename]))
    # define multi lists
    data_list = [ctable]
    datatype_list = ['table']
    name_list = ['POL_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=null1file)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write image to file
    null1file.write_multi(data_list=data_list, name_list=name_list,
                          datatype_list=datatype_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(null1file)
    # ----------------------------------------------------------------------
    # Write null 2 data to disk
    # ----------------------------------------------------------------------
    # get a new copy of the pol file
    null2file = recipe.outputs['POL_NULL2'].newcopy(params=params)
    # construct the filename from file instance
    null2file.construct_filename(infile=cfile)
    # copy header from pol file
    null2file.copy_hdict(polfile)
    # add output tag
    null2file.add_hkey('KW_OUTPUT', value=null2file.name)
    # add data
    null2file.data = null2_data
    # log that we are saving null 2file
    WLOG(params, '', textentry('40-021-00007', args=[null2file.filename]))
    # define multi lists
    data_list = [ctable]
    datatype_list = ['table']
    name_list = ['POL_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=null2file)]
        name_list += ['PARAM_TABLE']
        datatype_list += ['table']
    # write image to file
    null2file.write_multi(data_list=data_list, name_list=name_list,
                          datatype_list=datatype_list,
                          block_kind=recipe.out_block_str,
                          runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(null2file)
    # ----------------------------------------------------------------------
    # Write the s1d files to disk
    # ----------------------------------------------------------------------
    # loop around all keys
    for s1dkey in s1dprops:
        # get a new copy of the pol file
        s1dfile = recipe.outputs[s1dkey].newcopy(params=params)
        # construct the filename from file instance
        s1dfile.construct_filename(infile=cfile)
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
        data_list = [ctable]
        datatype_list = ['table']
        name_list = ['POL_TABLE']
        # snapshot of parameters
        if params['PARAMETER_SNAPSHOT']:
            data_list += [params.snapshot_table(recipe, drsfitsfile=null2file)]
            name_list += ['PARAM_TABLE']
            datatype_list += ['table']
        # write image to file
        s1dfile.write_multi(data_list=data_list, name_list=name_list,
                            block_kind=recipe.out_block_str,
                            runstring=recipe.runstring)
        # add to output files (for indexing)
        recipe.add_output_file(s1dfile)

    # add LSD files
    return polfile, cfile, ctable


def add_polar_keywords(params: ParamDict, props: ParamDict,
                       outfile: DrsFitsFile) -> DrsFitsFile:
    """
    Add polar header keys to "outfile"

    :param params: ParamDict, the parameter dictionary of constants
    :param props: ParamDict, the parameter dictionary of data
    :param outfile: DrsFitsFile, the output DrsFitsFile instance

    :return: outfile: DrsFitsFile, the updated DrsFitsFile (hdict updated)
    """
    # -------------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    # get the telluric bands
    telluric_bands = pconst.GET_POLAR_TELLURIC_BANDS()
    # load the telluric bands into a 1D list of strings '{LOW},{HIGH}
    str_telluric_bands = []
    for band in telluric_bands:
        str_telluric_bands.append('{0},{1}'.format(*band))
    # -------------------------------------------------------------------------
    # add elapsed time of observation (in seconds)
    outfile.add_hkey('KW_POL_ELAPTIME', value=props['ELAPSED_TIME'])
    # add MJD at center of observation
    outfile.add_hkey('KW_POL_MJDCEN', value=props['MJDCEN'])
    # add BJD at center of observation
    outfile.add_hkey('KW_POL_BJDCEN', value=props['BJDCEN'])
    # add BERV at center of observation
    outfile.add_hkey('KW_POL_BERVCEN', value=props['BERVCEN'])
    # add mean MJD for polar sequence
    outfile.add_hkey('KW_POL_MEAN_MJD', value=props['MEANMJD'])
    # add mean BJD for polar sequence
    outfile.add_hkey('KW_POL_MEAN_BJD', value=props['MEANBJD'])
    # add stokes parameter
    outfile.add_hkey('KW_POL_STOKES', value=props['GLOBAL_STOKES'])
    # add number of exposures for polarimetry
    outfile.add_hkey('KW_POL_NEXP', value=props['N_EXPOSURES'])
    # add the total exposure time (in seconds)
    outfile.add_hkey('KW_POL_EXPTIME', value=props['TOTEXPTIME'])
    # add flux weighted MJD of the exposures'
    outfile.add_hkey('KW_POL_MJD_FW_CEN', value=props['MJDFWCEN'])
    # add flux weighted BJD of the exposures'
    outfile.add_hkey('KW_POL_BJD_FW_CEN', value=props['BJDFWCEN'])
    # add mean BERV of the exposures
    outfile.add_hkey('KW_POL_MEAN_BERV', value=props['MEANBERV'])
    # -------------------------------------------------------------------------
    # add properties / switches from constants
    # -------------------------------------------------------------------------
    # add the polarimetry method
    outfile.add_hkey('KW_POL_METHOD', value=params['POLAR_METHOD'])
    # define whether we corrected for BERV
    outfile.add_hkey('KW_POL_CORR_BERV', value=params['POLAR_BERV_CORRECT'])
    # define whether we corrected for source RV
    outfile.add_hkey('KW_POL_CORR_SRV', value=params['POLAR_SOURCE_RV_CORRECT'])
    # define whether we normalized stokes I by continuum
    outfile.add_hkey('KW_POL_NORM_STOKESI',
                     value=params['POLAR_NORMALIZE_STOKES_I'])
    # define whether we interp flux to correct for shifts between exposures
    outfile.add_hkey('KW_POL_INTERP_FLUX',
                     value=params['POLAR_INTERPOLATE_FLUX'])
    # define whether we apply polarimetric sigma-clip cleaning
    outfile.add_hkey('KW_POL_SIGCLIP',
                     value=params['POLAR_CLEAN_BY_SIGMA_CLIPPING'])
    # define the number of sigma swithin which to apply sigma clipping
    outfile.add_hkey('KW_POL_NSIGMA', value=params['POLAR_NSIGMA_CLIPPING'])
    # define whether we removed continuum polarization
    outfile.add_hkey('KW_POL_REMOVE_CONT',
                     value=params['POLAR_REMOVE_CONTINUUM'])
    # define the stokes I continuum detection algorithm
    outfile.add_hkey('KW_POL_SCONT_DET_ALG',
                     value=params['STOKESI_CONTINUUM_DETECTION_ALGORITHM'])
    # define the polar continuum detection algorithm
    outfile.add_hkey('KW_POL_PCONT_DET_ALG',
                     value=params['POLAR_CONTINUUM_DETECTION_ALGORITHM'])
    # define whether we used polynomial fit for continuum polarization
    outfile.add_hkey('KW_POL_CONT_POLYFIT',
                     value=params['POLAR_CONT_POLYNOMIAL_FIT'])
    # define polynomial degree of fit continuum polarization
    outfile.add_hkey('KW_POL_CONT_DEG_POLY',
                     value=params['POLAR_CONT_DEG_POLYNOMIAL'])
    # define the iraf function that was used to fit stokes I continuum
    outfile.add_hkey('KW_POL_S_IRAF_FUNC',
                     value=params['STOKESI_IRAF_CONT_FIT_FUNCTION'])
    # define the iraf function that was used to fit polar continuum
    outfile.add_hkey('KW_POL_P_IRAF_FUNC',
                     value=params['POLAR_IRAF_CONT_FIT_FUNCTION'])
    # define the degree of the polynomial used to fit stokes I continuum
    outfile.add_hkey('KW_POL_S_IRAF_DEGREE',
                     value=params['STOKESI_IRAF_CONT_FUNCTION_ORDER'])
    # define the degree of the polynomial used to fit polar continuum
    outfile.add_hkey('KW_POL_P_IRAF_DEGREE',
                     value=params['POLAR_IRAF_CONT_FUNCTION_ORDER'])
    # define the polar continuum bin size used
    outfile.add_hkey('KW_POL_CONT_BINSIZE', value=params['POLAR_CONT_BINSIZE'])
    # define the polar continuum overlap size used
    outfile.add_hkey('KW_POL_CONT_OVERLAP', value=params['POLAR_CONT_OVERLAP'])
    # define the telluric mask parameters (1D list)
    outfile.add_hkey_1d('KW_POL_CONT_TELLMASK', values=str_telluric_bands,
                        dim1name='wave range')
    # -------------------------------------------------------------------------
    # return polfile with hdict updated
    return outfile


# =============================================================================
# Define worker functions
# =============================================================================
ContinuumReturn = Tuple[np.ndarray, np.ndarray, np.ndarray]


def continuum(params: ParamDict, xarr: np.ndarray, yarr: np.ndarray,
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
    func_name = display_func('continuum', __NAME__)
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
            xmean = np.mean(xtmp[nanmask])
            # calculate median y within the bin
            medy = np.median(ytmp[nanmask])
            # calculate median deviation
            medydev = np.median(np.abs(ytmp[nanmask] - medy))
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
                    ybin.append(np.max(ytmp[nanmask][filtermask]))
                elif mode == 'median':
                    # save median y of filtered data
                    ybin.append(np.median(ytmp[nanmask][filtermask]))
                elif mode == 'mean':
                    # save mean y of filtered data
                    ybin.append(np.mean(ytmp[nanmask][filtermask]))
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
            if idx0 < 0:
                idx0 = 0
            if idxf > nbins:
                idxf = nbins - 1
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
            localnanmask = np.isfinite(yarr)
            ybin.append(np.nanmedian(yarr[localnanmask][:binsize]))
        # ---------------------------------------------------------------------
        # if we have over 2 points we can use mean / median
        if len(xtmp[nanmask]) > 2:
            # calculate mean x within the bin
            xmean = np.mean(xtmp[nanmask])
            # save mean x with in bin
            xbin.append(xmean)
            # do a median
            if mode == 'median':
                # save median y of filtered data
                ybin.append(np.median(ytmp[nanmask]))
            elif mode == 'mean':
                # save mean y of filtered data
                ybin.append(np.mean(ytmp[nanmask]))
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
            localnanmask = np.isfinite(yarr)
            ybin.append(np.nanmedian(yarr[localnanmask][-binsize:]))
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
