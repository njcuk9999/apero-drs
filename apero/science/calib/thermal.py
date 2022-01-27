#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2022-01-26

@author: cook
"""
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import warnings

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_data
from apero.core.utils import drs_recipe
from apero.core.core import drs_database
from apero.science.calib import wave
from apero.science.calib import gen_calib


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.thermal.py'
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
CalibrationDatabase = drs_database.CalibrationDatabase
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# Get function string
display_func = drs_log.display_func


# =============================================================================
# Define functions
# =============================================================================
def apply_excess_emissivity(params: ParamDict, recipe: DrsRecipe,
                            thermal_files: Dict[str, DrsFitsFile],
                            fiber_types: List[str],
                            calibdbm: CalibrationDatabase
                            ) -> Dict[str, DrsFitsFile]:
    """
    Take a dictionary of thermal files and apply
    :param params:
    :param recipe:
    :param thermal_files:
    :param fiber_types:
    :param calibdbm:
    :return:
    """
    # set function name
    func_name = display_func('apply_excess_emissivity', __NAME__)
    # -------------------------------------------------------------------------
    # get allowed dprtypes parameter
    dprtypes = params.listp('THERMAL_EXCESS_DPRTYPES', dtype=str)
    # loop around all fibers
    # if any file has the wrong dprtype skip this step
    for fiber in fiber_types:
        # get the thermal file
        thermal_file = thermal_files[fiber]
        # get dprtype
        dprtype = thermal_file.get_hkey('KW_DPRTYPE')
        # check dprtype - if not correct type continue
        if dprtype not in dprtypes:
            return thermal_files
    # -------------------------------------------------------------------------
    # load excess emissivity file
    ex_wave, ex_flux = drs_data.load_excess_emissivity(params, func=func_name)
    # create a spline for the excess emissivity
    espline = mp.iuv_spline(ex_wave, ex_flux, ext=3, k=1)

    # TODO: change fiber_types --> science fibers
    # loop around all fibers and apply excess correction
    for fiber in fiber_types:
        # get the thermal file
        thermal_file = thermal_files[fiber]
        # get the extracted data
        image = np.array(thermal_file.data)
        header = thermal_file.header
        # load the wave solution for this file
        wprops = wave.get_wavesolution(params, recipe, header,
                                       fiber=fiber,
                                       database=calibdbm,
                                       nbpix=image.shape[1])
        # spline excess emissivity onto the wave grid of the extracted file
        excess_correction = espline(wprops['WAVEMAP'])
        # correct data and push back to thermal file
        thermal_file.data = image * excess_correction

        # add thermal file back to dictionary
        thermal_files[fiber] = thermal_file
    # return thermal files
    return thermal_files


# =============================================================================
# Define thermal functions
# =============================================================================
def thermal_correction(params, recipe, header, props=None, eprops=None,
                       fiber=None, database=None, **kwargs):
    func_name = __NAME__ + '.thermal_correction()'
    # deal with props = None
    if props is None:
        props = ParamDict()
    # deal with eprops = None
    if eprops is None:
        eprops = ParamDict()
    # get properties from parameter dictionaries / kwargs
    dprtype = pcheck(params, 'DPRTYPE', 'dprtype', kwargs, func_name,
                     paramdict=props)
    tapas_thres = pcheck(params, 'THERMAL_THRES_TAPAS', 'tapas_thres', kwargs,
                         func_name)
    envelope = pcheck(params, 'THERMAL_ENVELOPE_PERCENTILE', 'envelope',
                      kwargs, func_name)
    filter_wid = pcheck(params, 'THERMAL_FILTER_WID', 'filter_wid', kwargs,
                        func_name)
    torder = pcheck(params, 'THERMAL_ORDER', 'torder', kwargs, func_name)
    red_limt = pcheck(params, 'THERMAL_RED_LIMIT', 'red_limit', kwargs,
                      func_name)
    blue_limit = pcheck(params, 'THERMAL_BLUE_LIMIT', 'blue_limit', kwargs,
                        func_name)
    e2ds = pcheck(params, 'E2DS', 'e2ds', kwargs, func_name, paramdict=eprops)
    e2dsff = pcheck(params, 'E2DSFF', 'e2dsff', kwargs, func_name,
                    paramdict=eprops)
    flat = pcheck(params, 'FLAT', paramdict=eprops)

    corrtype1 = pcheck(params, 'THERMAL_CORRETION_TYPE1', 'corrtype1', kwargs,
                       func_name, mapf='list', dtype=str)
    corrtype2 = pcheck(params, 'THERMAL_CORRETION_TYPE2', 'corrtype2', kwargs,
                       func_name, mapf='list', dtype=str)

    thermal_file = kwargs.get('thermal_file', None)
    thermal_correct = pcheck(params, 'THERMAL_CORRECT', 'thermal_correct',
                             kwargs, func_name)
    # ----------------------------------------------------------------------
    # get pconstant from p
    pconst = constants.pload()
    # ----------------------------------------------------------------------
    # get fiber dprtype
    fibertype = pconst.FIBER_DATA_TYPE(dprtype, fiber)
    # ----------------------------------------------------------------------
    # get master wave map
    # TODO: Are we sure this should be the master solution?
    wprops = wave.get_wavesolution(params, recipe, master=True,
                                   database=database)
    # get the wave solution
    wavemap = wprops['WAVEMAP']

    # ----------------------------------------------------------------------
    # deal with skipping thermal correction
    if not thermal_correct:
        # add / update eprops
        eprops['E2DS'] = e2ds
        eprops['E2DSFF'] = e2dsff
        eprops['FIBERTYPE'] = fibertype
        eprops['THERMALFILE'] = 'None'
        # update source
        keys = ['E2DS', 'E2DSFF', 'FIBERTYPE', 'THERMALFILE']
        eprops.set_sources(keys, func_name)
        # return eprops
        return eprops
    # ----------------------------------------------------------------------
    # get thermal (only if in one of the correction lists)
    if fibertype in corrtype1:
        tout = get_thermal(params, header, fiber=fiber, filename=thermal_file,
                           kind='THERMALT_E2DS', database=database,
                           required=False)
        thermalfile, thermaltime, thermal = tout
        # deal with no thermal file from THERMALT (use THERMALI)
        if thermalfile is None:
            # print warning
            wmsg = 'No telescope dark file found, trying a internal dark file'
            WLOG(params, 'warning', wmsg, sublevel=6)
            # get the internal dark e2ds
            tout = get_thermal(params, header, fiber=fiber,
                               filename=thermal_file, kind='THERMALI_E2DS',
                               database=database)
            thermalfile, thermaltime, thermal = tout
    # ----------------------------------------------------------------------
    elif fibertype in corrtype2:
        tout = get_thermal(params, header, fiber=fiber, filename=thermal_file,
                           kind='THERMALI_E2DS', database=database)
        thermalfile, thermaltime, thermal = tout
    # ----------------------------------------------------------------------
    # else set everything to blank
    else:
        thermal = None
        thermalfile = 'None'
        thermaltime = np.nan
    # ----------------------------------------------------------------------
    # thermal correction kwargs
    tkwargs = dict(header=header, fiber=fiber, wavemap=wavemap,
                   tapas_thres=tapas_thres, envelope=envelope,
                   filter_wid=filter_wid, torder=torder,
                   red_limit=red_limt, blue_limit=blue_limit,
                   thermal=thermal, database=database)
    # base thermal correction on fiber type
    if fibertype in corrtype1:
        # log progress: doing thermal correction
        wargs = [fibertype, 1]
        WLOG(params, 'info', textentry('40-016-00012', args=wargs))
        # do thermal correction
        e2ds, tprops = tcorrect1(params, recipe, e2ds, **tkwargs)
        e2dsff, tpropsff = tcorrect1(params, recipe, e2dsff, flat=flat,
                                     **tkwargs)
    elif fibertype in corrtype2:
        # log progress: doing thermal correction
        wargs = [fibertype, 1]
        WLOG(params, 'info', textentry('40-016-00012', args=wargs))
        # do thermal correction
        e2ds, tprops = tcorrect2(params, recipe, e2ds, **tkwargs)
        e2dsff, tpropsff = tcorrect2(params, recipe, e2dsff, flat=flat,
                                     **tkwargs)
    else:
        # log that we are not correcting thermal
        WLOG(params, 'info', textentry('40-016-00013', args=[fibertype]))
        thermalfile = 'None'
        thermaltime = np.nan
        # thermal ratios are set to NaN
        tprops = dict(ratio1=np.nan, ratio2=np.nan, ratio_used='None')
        tpropsff = dict(ratio1=np.nan, ratio2=np.nan, ratio_used='None')
    # ----------------------------------------------------------------------
    # add / update eprops
    eprops['E2DS'] = e2ds
    eprops['E2DSFF'] = e2dsff
    eprops['FIBERTYPE'] = fibertype
    eprops['THERMALFILE'] = thermalfile
    eprops['THERMALTIME'] = thermaltime
    eprops['THERMAL_RATIO'] = tprops['ratio']
    eprops['THERMAL_RATIO_USED'] = tprops['ratio_used']
    eprops['THERMALFF_RATIO'] = tpropsff['ratio']
    eprops['THERMALFF_RATIO_USED'] = tpropsff['ratio_used']
    # update source
    keys = ['E2DS', 'E2DSFF', 'FIBERTYPE', 'THERMALFILE', 'THERMALTIME',
            'THERMAL_RATIO', 'THERMAL_RATIO_USED',
            'THERMALFF_RATIO', 'THERMALFF_RATIO_USED']
    eprops.set_sources(keys, func_name)
    # return eprops
    return eprops


def get_thermal(params, header, fiber, kind, filename=None,
                database=None, required: bool = True
                ) -> Tuple[str, float, Union[np.ndarray, None]]:
    # get file definition
    out_thermal = drs_file.get_file_definition(params, kind, block_kind='red')
    # get key
    key = out_thermal.get_dbkey()
    # ----------------------------------------------------------------------
    # load database
    if database is None:
        calibdbm = drs_database.CalibrationDatabase(params)
        calibdbm.load_db()
    else:
        calibdbm = database
    # ------------------------------------------------------------------------
    # load calib file
    ckwargs = dict(key=key, userinputkey='THERMALFILE', filename=filename,
                   inheader=header, database=calibdbm, fiber=fiber,
                   required=required)
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, **ckwargs)
    # deal with no file and not required
    if cfile.filename is None and not required:
        return 'None', np.nan, None
    # get properties from calibration file
    thermal = cfile.data
    thermal_file = cfile.filename
    thermaltime = cfile.mjdmid
    # log which thermal file we are using
    WLOG(params, '', textentry('40-016-00027', args=[thermal_file]))
    # return the master image
    return thermal_file, thermaltime, thermal


def tcorrect1(params: ParamDict, recipe: DrsRecipe,
              image: np.ndarray, header: drs_file.Header,
              fiber: str, wavemap: np.ndarray,
              thermal: Optional[np.ndarray] = None,
              flat: Optional[np.ndarray] = None,
              database: Optional[drs_database.CalibrationDatabase] = None,
              **kwargs) -> Tuple[np.ndarray, ParamDict]:
    # get parameters from skwargs
    # TODO: remove kwargs
    tapas_thres = kwargs.get('tapas_thres', None)
    filter_wid = kwargs.get('filter_wid', None)
    torder = kwargs.get('torder', None)
    red_limit = kwargs.get('red_limit', None)
    tapas_file = kwargs.get('tapas_file', None)
    # ----------------------------------------------------------------------
    # deal with no thermal
    if thermal is None:
        # get thermal
        tout = get_thermal(params, header, fiber=fiber, kind='THERMALT_E2DS',
                           database=database)
        thermal_file, thermaltime, thermal = tout
    # ----------------------------------------------------------------------
    # if we have a flat we should apply it to the thermal
    if flat is not None:
        thermal = thermal / flat
        kind = 'FF '
    else:
        kind = ''
    # ----------------------------------------------------------------------
    # deal with rare case that thermal is all zeros
    if mp.nansum(thermal) == 0 or np.sum(np.isfinite(thermal)) == 0:
        return image
    # ----------------------------------------------------------------------
    # load tapas
    tapas, _ = drs_data.load_tapas(params, filename=tapas_file)
    wtapas, ttapas = tapas['wavelength'], tapas['trans_combined']

    # --------------------------------------------------------------------------
    # median filter the thermal (loop around orders)
    for order_num in range(thermal.shape[0]):
        thermal[order_num] = mp.lowpassfilter(thermal[order_num], filter_wid)

    # --------------------------------------------------------------------------
    # Method 1: Use tapas (for use with bright targets)
    # --------------------------------------------------------------------------
    # binary mask to be saved; this corresponds to the domain for which
    #    transmission is basically zero and we can safely use the domain
    #    to scale the thermal background. We only do this for wavelength smaller
    #    than "THERMAL_TAPAS_RED_LIMIT" nm as this is the red end of the
    #    TAPAS domain
    # --------------------------------------------------------------------------
    # splining tapas onto the order 49 wavelength grid
    sptapas = mp.iuv_spline(wtapas, ttapas, ext=3, k=1)
    # set torder mask all to False initially
    torder_mask = np.zeros_like(wavemap[torder, :], dtype=bool)
    # get the wave mask
    wavemask = wavemap[torder] < red_limit
    # get the tapas data for these wavelengths
    torder_tapas = sptapas(wavemap[torder, wavemask])
    # find those pixels lower than threshold in tapas
    torder_mask[wavemask] = torder_tapas < tapas_thres
    # we find the median scale between the observation and the thermal
    #    background in domains where there is no transmission
    thermal_torder = thermal[torder, torder_mask]
    image_torder = image[torder, torder_mask]
    ratio = mp.nanmedian(thermal_torder / image_torder)
    # -------------------------------------------------------------------------
    # scale thermal by ratio
    thermal = thermal / ratio
    # set the header parameters for thermal ratios
    strratio = 'tapas'
    # ----------------------------------------------------------------------
    # calculate final thermal profile (for correction)
    thermal = thermal / ratio
    # ----------------------------------------------------------------------
    # plot thermal background plot
    recipe.plot('THERMAL_BACKGROUND', params=params, wavemap=wavemap,
                image=image, thermal=thermal, torder=torder, tmask=torder_mask,
                fiber=fiber, kind=kind)
    # ----------------------------------------------------------------------
    # correct image
    corrected_image = image - thermal
    # ----------------------------------------------------------------------
    # save parameters to param dict
    therm_props = ParamDict()
    therm_props['ratio'] = ratio
    therm_props['ratio_used'] = strratio
    # ----------------------------------------------------------------------
    # return p and corrected image
    return corrected_image, therm_props


def tcorrect2(params: ParamDict, recipe: DrsRecipe,
              image: np.ndarray, header: drs_file.Header,
              fiber: str, wavemap: np.ndarray,
              thermal: Optional[np.ndarray] = None,
              flat: Optional[np.ndarray] = None,
              database: Optional[drs_database.CalibrationDatabase] = None,
              **kwargs) -> Tuple[np.ndarray, ParamDict]:
    # TODO: remove kwargs
    envelope_percent = kwargs.get('envelope', None)
    filter_wid = kwargs.get('filter_wid', None)
    torder = kwargs.get('torder', None)
    red_limit = kwargs.get('red_limit', None)
    blue_limit = kwargs.get('blue_limit', None)
    # thermal_file = kwargs.get('thermal_file', None)
    # get the shape
    dim1, dim2 = image.shape
    # ----------------------------------------------------------------------
    # deal with no thermal
    if thermal is None:
        # get thermal
        tout = get_thermal(params, header, fiber=fiber, kind='THERMALI_E2DS',
                           database=database)
        thermal_file, thermaltime, thermal = tout
    # ----------------------------------------------------------------------
    # if we have a flat we should apply it to the thermal
    if flat is not None:
        thermal = thermal / flat
        kind = 'FF '
    else:
        kind = ''
    # ----------------------------------------------------------------------
    # deal with rare case that thermal is all zeros
    if mp.nansum(thermal) == 0 or np.sum(np.isfinite(thermal)) == 0:
        return image
    # ----------------------------------------------------------------------
    # set up an envelope to measure thermal background in image
    envelope = np.zeros(dim2)
    # loop around all pixels
    for x_it in range(dim2):
        # define start and end points
        start = x_it - filter_wid // 2
        end = x_it + filter_wid // 2
        # deal with out of bounds
        if start < 0:
            start = 0
        if end > dim2 - 1:
            end = dim2 - 1
        # get the box for this pixel
        imagebox = image[torder, start:end]
        # get the envelope
        with warnings.catch_warnings(record=True) as _:
            envelope[x_it] = np.nanpercentile(imagebox, envelope_percent)
    # --------------------------------------------------------------------------
    # median filter the thermal (loop around orders)
    for order_num in range(thermal.shape[0]):
        thermal[order_num] = mp.lowpassfilter(thermal[order_num], filter_wid)
    # ----------------------------------------------------------------------
    # only keep wavelength in range of thermal limits
    wavemask = (wavemap[torder] > blue_limit) & (wavemap[torder] < red_limit)
    # we find the median scale between the observation and the thermal
    #    background in domains where there is no transmission
    thermal_torder = thermal[torder, wavemask]
    envelope_torder = envelope[wavemask]
    ratio = mp.nanmedian(thermal_torder / envelope_torder)
    # ----------------------------------------------------------------------
    # set parameters for header
    strratio = 'ratio1[envelope]'
    # scale thermal by ratio
    thermal = thermal / ratio
    # ----------------------------------------------------------------------
    # plot thermal background plot
    recipe.plot('THERMAL_BACKGROUND', params=params, wavemap=wavemap,
                image=image, thermal=thermal, torder=torder, tmask=wavemask,
                fiber=fiber, kind=kind)
    # ----------------------------------------------------------------------
    # correct image
    corrected_image = image - thermal
    # ----------------------------------------------------------------------
    # save parameters to param dict
    therm_props = ParamDict()
    therm_props['ratio'] = ratio
    therm_props['ratio_used'] = strratio
    # ----------------------------------------------------------------------
    # return p and corrected image
    return corrected_image, therm_props


# =============================================================================
# Start of code
# =============================================================================
if __name__ == "__main__":
    # print hello world
    print('Hello World')

# =============================================================================
# End of code
# =============================================================================
