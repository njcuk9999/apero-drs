#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-08-12 at 17:16

@author: cook
"""
import os
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from astropy import constants as cc
from astropy import units as uu
from astropy.table import Table

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_database
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.core import drs_text
from apero.core.instruments.default import pseudo_const
from apero.core.utils import drs_data
from apero.core.utils import drs_recipe
from apero.core.utils import drs_utils
from apero.io import drs_fits
from apero.io import drs_table
from apero.science.calib import flat_blaze
from apero.science.calib import gen_calib
from apero.science.telluric.core_tellu import load_tellu_file, wave_to_wave
from apero.science.telluric import sky_corr
from apero.science import extract

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.telluric.gen_calib.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
DrsRecipe = drs_recipe.DrsRecipe
# get calibration database
CalibDatabase = drs_database.CalibrationDatabase
TelluDatabase = drs_database.TelluricDatabase
FileIndexDatabase = drs_database.FileIndexDatabase
DPseudoConsts = pseudo_const.DefaultPseudoConstants
# Get function string
display_func = drs_log.display_func
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)
# Speed of light
# noinspection PyUnresolvedReferences
speed_of_light_ms = cc.c.to(uu.m / uu.s).value
# noinspection PyUnresolvedReferences
speed_of_light = cc.c.to(uu.km / uu.s).value


# =============================================================================
# Define functions
# =============================================================================
def id_hot_star(params: ParamDict, objname: str) -> bool:
    # get all telluric stars
    tstars = get_tellu_include_list(params)
    # return whether objname is a hot-star
    return objname in tstars


def get_tellu_include_list(params: ParamDict,
                           assets_dir: Union[str, None] = None,
                           tellu_dir: Union[str, None] = None,
                           tellu_include_file: Union[str, None] = None,
                           all_objects: Optional[List[str]] = None
                           ) -> List[str]:
    func_name = __NAME__ + '.get_whitelist()'
    # get pseudo constants
    pconst = constants.pload()
    # get object database
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', func=func_name,
                      override=assets_dir)
    relfolder = pcheck(params, 'TELLU_LIST_DIRECTORY', func=func_name,
                       override=tellu_dir)
    tfilename = pcheck(params, 'TELLU_WHITELIST_NAME', func=func_name,
                       override=tellu_include_file)
    # get absolulte filename
    whitelistfile = os.path.join(assetdir, relfolder, tfilename)
    # load the white list
    whitelist = drs_data.load_text_file(params, whitelistfile, func_name,
                                        dtype=str)
    # must clean names
    whitelist, _ = objdbm.find_objnames(pconst, whitelist, allow_empty=True)

    # deal with all objects filter
    if all_objects is not None:
        mask = np.isin(whitelist, all_objects)
        whitelist = list(np.array(whitelist)[mask])
    # return the whitelist
    return whitelist


def get_tellu_exclude_list(params: ParamDict,
                           assets_dir: Union[str, None] = None,
                           tellu_dir: Union[str, None] = None,
                           tellu_exclude_file: Union[str, None] = None
                           ) -> Tuple[List[str], str]:
    func_name = __NAME__ + '.get_blacklist()'
    # get pseudo constants
    pconst = constants.pload()
    # get object database
    objdbm = drs_database.AstrometricDatabase(params)
    objdbm.load_db()
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', func=func_name,
                      override=assets_dir)
    relfolder = pcheck(params, 'TELLU_LIST_DIRECTORY', func=func_name,
                       override=tellu_dir)
    tfilename = pcheck(params, 'TELLU_BLACKLIST_NAME', func=func_name,
                       override=tellu_exclude_file)
    # get absolulte filename
    blacklistfile = os.path.join(assetdir, relfolder, tfilename)
    # load the white list
    blacklist = drs_data.load_text_file(params, blacklistfile, func_name,
                                        dtype=str)
    # must clean names and deal with aliases
    blacklist, _ = objdbm.find_objnames(pconst, blacklist, allow_empty=True)
    # return the whitelist
    return blacklist, blacklistfile


def get_blaze_props(params, header, fiber) -> ParamDict:
    # set function
    func_name = display_func('get_blaze_props', __NAME__)
    # load the blaze file for this fiber
    bout = flat_blaze.get_blaze(params, header, fiber)
    blaze_file, blaze_time, blaze = bout
    # ----------------------------------------------------------------------
    # parameter dictionary
    nprops = ParamDict()
    nprops['BLAZE'] = blaze
    nprops['BLAZE_FILE'] = blaze_file
    nprops['BLAZE_TIME'] = blaze_time
    # set sources
    keys = ['BLAZE', 'BLAZE_FILE', 'BLAZE_TIME']
    nprops.set_sources(keys, func_name)
    # return the normalised image and the properties
    return nprops


def normalise_by_pblaze(params, image, header, fiber, **kwargs):
    func_name = __NAME__ + '.normalise_by_pblaze()'
    # get properties from params/kwargs
    blaze_p = pcheck(params, 'MKTELLU_BLAZE_PERCENTILE', 'blaze_p', kwargs,
                     func_name)
    cut_blaze_norm = pcheck(params, 'MKTELLU_CUT_BLAZE_NORM', 'cut_blaze_norm',
                            kwargs, func_name)
    # ----------------------------------------------------------------------
    # copy the image
    image1 = np.array(image)
    # ----------------------------------------------------------------------
    # load the blaze file for this fiber
    bout = flat_blaze.get_blaze(params, header, fiber)
    blaze_file, blaze_time, blaze = bout
    # copy blaze
    blaze_norm = np.array(blaze)
    # loop through blaze orders, normalize blaze by its peak amplitude
    for order_num in range(image1.shape[0]):
        # normalize the spectrum
        spo, bzo = image1[order_num], blaze[order_num]
        # normalise image
        image1[order_num] = spo / mp.nanpercentile(spo, blaze_p)
        # normalize the blaze
        blaze_norm[order_num] = bzo / mp.nanpercentile(bzo, blaze_p)
    # ----------------------------------------------------------------------
    # find where the blaze is bad
    with warnings.catch_warnings(record=True) as _:
        badblaze = blaze_norm < cut_blaze_norm
    # ----------------------------------------------------------------------
    # set bad blaze to NaN
    blaze_norm[badblaze] = np.nan
    # set to NaN values where spectrum is zero
    zeromask = image1 == 0
    image1[zeromask] = np.nan
    # divide spectrum by blaze
    with warnings.catch_warnings(record=True) as _:
        image1 = image1 / blaze_norm
    # ----------------------------------------------------------------------
    # parameter dictionary
    nprops = ParamDict()
    nprops['BLAZE'] = blaze
    nprops['NBLAZE'] = blaze_norm
    nprops['BLAZE_PERCENTILE'] = blaze_p
    nprops['BLAZE_CUT_NORM'] = cut_blaze_norm
    nprops['BLAZE_FILE'] = blaze_file
    nprops['BLAZE_TIME'] = blaze_time
    # set sources
    keys = ['BLAZE', 'NBLAZE', 'BLAZE_PERCENTILE', 'BLAZE_CUT_NORM',
            'BLAZE_FILE', 'BLAZE_TIME']
    nprops.set_sources(keys, func_name)
    # return the normalised image and the properties
    return image1, nprops


def get_non_tellu_objs(params: ParamDict, fiber, filetype=None,
                       dprtypes=None, robjnames: List[str] = None,
                       findexdbm: Union[FileIndexDatabase, None] = None):
    """
    Get the objects of "filetype" and that are not telluric objects
    :param params: ParamDict - the parameter dictionary of constants
    :param fiber:
    :param filetype:
    :param dprtypes:
    :param robjnames: list of strings - a list of all object names (only return
                      if found and in this list
    :param findexdbm:

    :return:
    """
    # get the telluric star names (we don't want to process these)
    objnames = get_tellu_include_list(params)
    objnames = list(objnames)
    # deal with filetype being string
    if isinstance(filetype, str):
        filetype = filetype.split(',')
        filetype = np.char.array(filetype).strip()
    # deal with dprtypes being string
    if isinstance(dprtypes, str):
        dprtypes = dprtypes.split(',')
        dprtypes = np.char.array(dprtypes).strip()
    # construct kwargs
    fkwargs = dict()
    if filetype is not None:
        fkwargs['KW_OUTPUT'] = filetype
    if dprtypes is not None:
        fkwargs['KW_DPRTYPE'] = dprtypes
    if fiber is not None:
        fkwargs['KW_FIBER'] = fiber
    # find files (and return pandas dataframe of all columns
    dataframe = drs_utils.find_files(params, block_kind='red', filters=fkwargs,
                                     columns='*', findexdbm=findexdbm)
    # convert data frame to table
    obj_table = Table.from_pandas(dataframe)
    obj_filenames = obj_table['ABSPATH']
    # filter out telluric stars
    obj_stars, obj_names = [], []
    # loop around object table and only keep non-telluric stars
    for row in range(len(obj_table)):
        # get object name
        iobjname = obj_table['KW_OBJNAME'][row]
        # if required object name is set
        if robjnames is not None:
            if iobjname in robjnames:
                obj_stars.append(obj_filenames[row])
                if iobjname not in obj_names:
                    obj_names.append(iobjname)
        # if in telluric list skip
        elif iobjname not in objnames:
            obj_stars.append(obj_filenames[row])
            if iobjname not in obj_names:
                obj_names.append(iobjname)
    # return absolute path names and object names
    return obj_stars, obj_names


def get_tellu_objs(params: ParamDict, key: str,
                   objnames: Union[List[str], str, None] = None,
                   database: Union[TelluDatabase, None] = None) -> List[str]:
    """
    Get objects defined by "key" from telluric database (in list objname)

    :param params: ParamDict, the parameter dictionary of constants
    :param key: str, the database key to filter telluric database entries by
    :param objnames: str or list of strings, the object names to filter
                     the telluric database 'OBJECT' column by
    :param database: TelluricDatabase instance or None, if set does not have to
                     load database

    :return: list of strings, the absolute filenames for database entries of
             KEY == 'key' and OBJECT in 'objnames'
    """
    # _ = display_func('get_tellu_objs', __NAME__)
    # ----------------------------------------------------------------------
    # deal with objnames
    if objnames is None:
        objnames = []
    if isinstance(objnames, str):
        objnames = [objnames]
    # ----------------------------------------------------------------------
    # deal with not having database
    if database is None:
        database = TelluDatabase(params)
        # load database
        database.load_db()
    # ----------------------------------------------------------------------
    # get all obj_entries from the telluric database
    table = database.get_tellu_entry('FILENAME, OBJECT', key=key)
    # ----------------------------------------------------------------------
    # deal with no objects found
    if len(table) == 0:
        return []
    # ----------------------------------------------------------------------
    # filter by objnames (set by input)
    mask = np.zeros(len(table)).astype(bool)
    for objname in objnames:
        mask |= np.array(table['OBJECT'] == objname)
    # get base filenames with this mask
    # noinspection PyTypeChecker
    filenames = list(table['FILENAME'][mask])
    # ----------------------------------------------------------------------
    # make path absolute
    absfilenames = []
    for filename in filenames:
        # construct absolute path
        absfilename = database.filedir.joinpath(filename)
        # check exists
        if absfilename.exists():
            absfilenames.append(str(absfilename))
    # ----------------------------------------------------------------------
    # display how many files found
    margs = [len(absfilenames), key]
    WLOG(params, '', textentry('40-019-00039', args=margs))
    return absfilenames


def get_sp_linelists(params, **kwargs):
    func_name = __NAME__ + '.get_sp_linelists()'
    # get parameters from params/kwargs
    relfolder = pcheck(params, 'TELLU_LIST_DIRECTORY', 'directory', kwargs,
                       func_name)
    othersfile = pcheck(params, 'TELLUP_OTHERS_CCF_FILE', 'filename', kwargs,
                        func_name)
    waterfile = pcheck(params, 'TELLUP_H2O_CCF_FILE', 'filename', kwargs,
                       func_name)
    # load the others file list
    mask_others, _ = drs_data.load_ccf_mask(params, mask_dir=relfolder,
                                            filename=othersfile)
    mask_water, _ = drs_data.load_ccf_mask(params, mask_dir=relfolder,
                                           filename=waterfile)
    # load pseudo constants
    pconst = constants.pload()
    # mask out some regions based on instrument
    # TODO: remove once tapas always comes from specific instrument
    mask_water, mask_others = pconst.TAPAS_INST_CORR(mask_water, mask_others)
    # return masks
    return mask_others, mask_water


def mask_bad_regions(params: ParamDict,
                     image: np.ndarray, wavemap: np.ndarray,
                     pconst: Optional[DPseudoConsts] = None,
                     bad_regions: Optional[Tuple[float, float]] = None
                     ) -> np.ndarray:
    """
    Mask bad regions based on the wave map

    :param params: ParamDict, parameter dictionary of constants
    :param image: np.ndarray (1D or 2D), the 1D or 2D vector to fill with NaNs
                  in the bad_regions area (defined by wavemap)
    :param wavemap: np.ndarray (1D or 2D), must match shape of image, the
                    wavemap to mask by
    :param pconst: Optional Pconst, the pseudo constants instance for this
                   instrument, if not given and bad_regions is None, loaded
                   from constants.pload()
    :param bad_regions: Optional tuple of (float, float), the bad regions
                        each tuple entry is a wave start and wave end (in units
                        of the wavemap) if set to None this is loaded from
                        pconst.TELLU_BAD_WAVEREGIONS()

    :return: np.ndarray (1D or 2D), the image, filled with NaNs in the
             bad_regions
    """
    # set function name
    func_name = display_func('mask_bad_regions', __NAME__)
    # -------------------------------------------------------------------------
    # get bad wavelength regimes
    if bad_regions is None:
        # if pconst is not loaded load it
        if pconst is None:
            pconst = constants.pload()
        # get the bad regions from TELLU_BAD_WAVEREGIONS()
        bad_regions = pconst.TELLU_BAD_WAVEREGIONS()
    # deal with no bad regions
    if len(bad_regions) == 0:
        return image
    # -------------------------------------------------------------------------
    # we can deal with 1D and 2D files
    if len(image.shape) not in [1, 2]:
        # TODO: Add to language database
        emsg = ('Can only mask bad regions in 1D and 2D images. '
                '\n\tImage shape: {0}'
                '\n\tFunction: {1}')
        eargs = [image.shape, func_name]
        WLOG(params, 'error', emsg.format(*eargs))
    if image.shape != wavemap.shape:
        # TODO: Add to language database
        emsg = ('Image and wavelength grid must have same dimensions'
                '\n\tImage shape: {0} \n\tWavemap shape: {1}'
                '\n\tFunction: {2}')
        eargs = [image.shape, wavemap.shape, func_name]
        WLOG(params, 'error', emsg.format(*eargs))
    # -------------------------------------------------------------------------
    # loop around bad regions and mask them
    for bad_region in bad_regions:
        # get the start and end points of the tuple
        wavestart, waveend = bad_region
        # if e2ds we need to
        if len(image.shape) == 2:
            for order_num in range(image.shape[0]):
                # mask wavelength per order
                mask_order = wavemap[order_num] > wavestart
                mask_order &= wavemap[order_num] < waveend
                # set these regions to NaN
                image[order_num][mask_order] = np.nan
        # else we have 1D
        else:
            # mask by wavelength
            mask_order = wavemap > wavestart
            mask_order &= wavemap < waveend
            # set these regions to NaN
            image[mask_order] = np.nan
    # -------------------------------------------------------------------------
    # return image - NaN filled
    return image


# =============================================================================
# pre-cleaning functions
# =============================================================================
def tellu_preclean(params, recipe, infile, wprops, fiber, rawfiles, combine,
                   template_props: ParamDict, refprops: ParamDict,
                   bprops: ParamDict,
                   sky_props: Optional[ParamDict] = None,
                   calibdbm: Union[CalibDatabase, None] = None,
                   telludbm: Union[TelluDatabase, None] = None, **kwargs):
    """
    Main telluric pre-cleaning functionality.

    Pass an e2ds  image and return the telluric-corrected data.
    This is a rough model fit and we will need to perform PCA correction on
    top of it.

    Will fit both water and all dry components of the absorption separately.

    Underlying idea: We correct with a super naive tapas fit and iterate
    until the CCF of the telluric absorption falls to zero. We have 2 degrees
    of freedom, the dry and water components of the atmosphere.
    The instrument profile is defined by two additional parameters
    [ww -> FWHM, ex_gau -> kernel shape parameter].

    Again, this is just a cleanup PRIOR to PCA correction, so if the code is
    not perfect in it's correction, this is fine as we will empirically
    determine the residuals and fit them in a subsequent step.

    we set bounds to the limits of the reasonable domain for both parameters.

    :param params:
    :param recipe:
    :param infile:
    :param wprops:
    :param fiber:
    :param rawfiles:
    :param combine:
    :param calibdbm:
    :param telludbm:

    :return:
    """
    # set the function name
    func_name = __NAME__ + '.tellu_preclean()'
    # ----------------------------------------------------------------------
    # get parameters from parameter dictionary
    do_precleaning = pcheck(params, 'TELLUP_DO_PRECLEANING', 'do_precleaning',
                            kwargs, func_name)
    default_water_abso = pcheck(params, 'TELLUP_D_WATER_ABSO',
                                'default_water_abso', kwargs, func_name)
    ccf_scan_range = pcheck(params, 'TELLUP_CCF_SCAN_RANGE', 'ccf_scan_range',
                            kwargs, func_name)
    clean_ohlines = pcheck(params, 'TELLUP_CLEAN_OH_LINES', 'clean_ohlines',
                           kwargs, func_name)
    remove_orders = pcheck(params, 'TELLUP_REMOVE_ORDS', 'remove_orders',
                           kwargs, func_name, mapf='list', dtype=int)
    snr_min_thres = pcheck(params, 'TELLUP_SNR_MIN_THRES', 'snr_min_thres',
                           kwargs, func_name)
    dexpo_thres = pcheck(params, 'TELLUP_DEXPO_CONV_THRES', 'dexpo_thres',
                         kwargs, func_name)
    max_iterations = pcheck(params, 'TELLUP_DEXPO_MAX_ITR', 'max_iterations',
                            kwargs, func_name)
    ker_width = pcheck(params, 'TELLUP_ABSO_EXPO_KWID', 'ker_width', kwargs,
                       func_name)
    ker_shape = pcheck(params, 'TELLUP_ABSO_EXPO_KEXP', 'ker_shape', kwargs,
                       func_name)
    trans_thres = pcheck(params, 'TELLUP_TRANS_THRES', 'trans_thres', kwargs,
                         func_name)
    trans_siglim = pcheck(params, 'TELLUP_TRANS_SIGLIM', 'trans_siglim', kwargs,
                          func_name)
    force_airmass = pcheck(params, 'TELLUP_FORCE_AIRMASS', 'force_airmass',
                           kwargs, func_name)
    others_bounds = pcheck(params, 'TELLUP_OTHER_BOUNDS', 'others_bounds',
                           kwargs, func_name, mapf='list', dtype=float)
    water_bounds = pcheck(params, 'TELLUP_WATER_BOUNDS', 'water_bounds', kwargs,
                          func_name, mapf='list', dtype=float)
    ker_thres = pcheck(params, 'TELLUP_ABSO_EXPO_KTHRES', 'ker_thres', kwargs,
                       func_name)
    wavestart = pcheck(params, 'EXT_S1D_WAVESTART', 'wavestart', kwargs,
                       func_name)
    waveend = pcheck(params, 'EXT_S1D_WAVEEND', 'waveend', kwargs, func_name)
    dvgrid = pcheck(params, 'EXT_S1D_BIN_UVELO', 'dvgrid', kwargs, func_name)
    ccf_control_radius = 2 * params['IMAGE_PIXEL_SIZE']
    # ----------------------------------------------------------------------
    # load database
    if calibdbm is None:
        calibdbm = CalibDatabase(params)
        calibdbm.load_db()
    if telludbm is None:
        telludbm = TelluDatabase(params)
    # ----------------------------------------------------------------------
    # get image and header from infile
    header = infile.get_header()
    # get airmass from header
    hdr_airmass = infile.get_hkey('KW_AIRMASS', dtype=float)
    # copy e2ds input image
    image_e2ds_ini = infile.get_data(copy=True)
    # get shape of the e2ds
    nbo, nbpix = image_e2ds_ini.shape
    # get wave map for the input e2ds
    wave_e2ds = wprops['WAVEMAP']
    # ----------------------------------------------------------------------
    # get pconst
    pconst = constants.pload()
    # ------------------------------------------------------------------------
    # get res_e2ds file instance
    res_e2ds = drs_file.get_file_definition(params, 'WAVEM_RES_E2DS',
                                            block_kind='red')
    # get calibration key
    key = res_e2ds.get_dbkey()
    # define the fiber to use (this is the one that was used in the wave ref
    #   code to make the resolution map)
    usefiber = params['WAVE_REF_FIBER']
    # load loco file
    cfile = gen_calib.CalibFile()
    cfile.load_calib_file(params, key, header, database=calibdbm,
                          fiber=usefiber, return_filename=True)
    # get properties from calibration file
    res_e2ds_path = cfile.filename
    # construct new infile instance and read data/header
    res_e2ds = res_e2ds.newcopy(filename=res_e2ds_path, params=params,
                                fiber=usefiber)
    datalist = res_e2ds.get_data(copy=True, extnames=['E2DS_FWHM', 'E2DS_EXPO'])
    # get the data from the data list
    res_e2ds_fwhm = datalist['E2DS_FWHM']
    res_e2ds_expo = datalist['E2DS_EXPO']
    # get the res table
    res_table = drs_table.read_table(params, res_e2ds_path, fmt='fits',
                                     hdu='S1DV')
    # get the fwhm and expo from the table
    res_s1d_fwhm = np.array(res_table['flux_res_fwhm'])
    res_s1d_expo = np.array(res_table['flux_res_expo'])
    # ----------------------------------------------------------------------
    # run the snr qc without values (to push into storage)
    sqc_value, sqc_name, sqc_logic, sqc_pass = qc_p2pscat_bands(params)
    # ----------------------------------------------------------------------
    # define storage of quality control
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # need to add dummy values for these qc
    # 1. snr < snr_min_thres (pos = 0)
    qc_values.append(sqc_value)
    qc_names.append(sqc_name)
    qc_logic.append(sqc_logic)
    qc_pass.append(qc_pass)
    # 2. ccf is NaN (pos = 1)
    qc_values.append('N.A')
    qc_names.append('APPROX_RV [PREV, NOW]')
    qc_logic.append('APP_RV[NOW] > APP_RV[PREV]')
    qc_pass.append(np.nan)
    # 3. exponent for others out of bounds (pos = 2 and 3)
    qc_values += [np.nan, np.nan]
    qc_names += ['EXPO_OTHERS/AIRMASS L', 'EXPO_OTHERS/AIRMASS U']
    qc_logic += ['EXPO_OTHERS/AIRMASS L < {0}'.format(others_bounds[0]),
                 'EXPO_OTHERS/AIRMASS U > {0}'.format(others_bounds[1])]
    qc_pass += [np.nan, np.nan]
    # 4. exponent for water  out of bounds (pos 4 and 5)
    qc_values += [np.nan, np.nan]
    qc_names += ['EXPO_WATER/AIRMASS L', 'EXPO_WATER/AIRMASS U']
    qc_logic += ['EXPO_WATER/AIRMASS L < {0}'.format(water_bounds[0]),
                 'EXPO_WATER/AIRMASS U > {0}'.format(water_bounds[1])]
    qc_pass += [np.nan, np.nan]
    # 5. max iterations exceeded (pos = 6)
    qc_values.append(np.nan)
    qc_names.append('ITERATIONS')
    qc_logic.append('ITERATIONS = {0}'.format(max_iterations - 1))
    qc_pass.append(np.nan)
    # dev note: if adding a new one must add tfailmsgs for all uses in qc
    #  (mk_tellu and fit_tellu)
    # ----------------------------------------------------------------------
    # remove OH lines if required
    if clean_ohlines and sky_props is None:
        image_e2ds, sky_model = clean_ohline_pca(params, recipe,
                                                 image_e2ds_ini, wave_e2ds)
        # this one is for saving in the pclean
        sky_model_save = np.array(sky_model)
    # if we did the sky cleaning before pre-cleaning use this
    elif sky_props is not None:
        image_e2ds = np.array(image_e2ds_ini)
        # this needs to be zeros (sky model already applied)
        sky_model = np.zeros_like(image_e2ds_ini)
        # this one is for saving in the pclean
        sky_model_save = sky_props['SKY_CORR_SCI']
    # else just copy the image and set the sky model to zeros
    else:
        image_e2ds = np.array(image_e2ds_ini)
        # both sky models need to be zero (no sky model to apply)
        sky_model = np.zeros_like(image_e2ds_ini)
        sky_model_save = np.zeros_like(image_e2ds_ini)
    # ----------------------------------------------------------------------
    if not do_precleaning:
        # log progress
        WLOG(params, '', textentry('10-019-00008'))
        # populate qc params
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # populate parameter dictionary
        props = ParamDict()
        props['CORRECTED_E2DS'] = image_e2ds
        props['TRANS_MASK'] = np.ones_like(image_e2ds_ini).astype(bool)
        props['ABSO_E2DS'] = np.ones_like(image_e2ds_ini)
        props['SKY_MODEL'] = sky_model_save
        props['PRE_SKYCORR_IMAGE'] = image_e2ds_ini
        props['EXPO_WATER'] = np.nan
        props['EXPO_OTHERS'] = np.nan
        props['DV_WATER'] = np.nan
        props['DV_OTHERS'] = np.nan
        props['QC_PARAMS'] = qc_params
        # set sources
        keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
                'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'QC_PARAMS',
                'SKY_MODEL', 'PRE_SKYCORR_IMAGE']
        props.set_sources(keys, func_name)
        # ------------------------------------------------------------------
        # add constants used (can come from kwargs)
        props['TELLUP_DO_PRECLEANING'] = do_precleaning
        props['TELLUP_D_WATER_ABSO'] = default_water_abso
        props['TELLUP_CCF_SCAN_RANGE'] = ccf_scan_range
        props['TELLUP_CLEAN_OH_LINES'] = clean_ohlines
        props['TELLUP_REMOVE_ORDS'] = remove_orders
        props['TELLUP_SNR_MIN_THRES'] = snr_min_thres
        props['TELLUP_DEXPO_CONV_THRES'] = dexpo_thres
        props['TELLUP_DEXPO_MAX_ITR'] = max_iterations
        props['TELLUP_ABSO_EXPO_KWID'] = ker_width
        props['TELLUP_ABSO_EXPO_KEXP'] = ker_shape
        props['TELLUP_TRANS_THRES'] = trans_thres
        props['TELLUP_TRANS_SIGLIM'] = trans_siglim
        props['TELLUP_FORCE_AIRMASS'] = force_airmass
        props['TELLUP_OTHER_BOUNDS'] = others_bounds
        props['TELLUP_WATER_BOUNDS'] = water_bounds
        props['TELLUP_ABSO_EXPO_KTHRES'] = ker_thres
        props['TELLUP_WAVE_START'] = wavestart
        props['TELLUP_WAVE_END'] = waveend
        props['TELLUP_DVGRID'] = dvgrid
        # set sources
        keys = ['TELLUP_D_WATER_ABSO', 'TELLUP_CCF_SCAN_RANGE',
                'TELLUP_CLEAN_OH_LINES', 'TELLUP_REMOVE_ORDS',
                'TELLUP_SNR_MIN_THRES', 'TELLUP_DEXPO_CONV_THRES',
                'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KWID',
                'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
                'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS',
                'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS',
                'TELLUP_ABSO_EXPO_KTHRES', 'TELLUP_WAVE_START',
                'TELLUP_WAVE_END', 'TELLUP_DVGRID', 'TELLUP_DO_PRECLEANING']
        props.set_sources(keys, func_name)
        # ------------------------------------------------------------------
        # return props
        return props
    # ----------------------------------------------------------------------
    # we ravel the wavelength grid to make it a 1d array of increasing
    #     wavelength. We will trim the overlapping domain between orders
    keep = np.ones_like(wave_e2ds).astype(bool)
    # keep track of where orders are
    orders, _ = np.indices(wave_e2ds.shape)
    # loop around 2nd to last-1 order and compare -1th and +1th order
    for order_num in range(1, nbo - 1):
        # get wavelengths not in order before tellu_preclean
        before = wave_e2ds[order_num] > wave_e2ds[order_num - 1][::-1]
        # get wavelengths not in order after
        after = wave_e2ds[order_num] < wave_e2ds[order_num + 1][::-1]
        # combine mask
        keep[order_num] = before & after
    # set whole first order to zeros (rejected)
    keep[0] = np.zeros(nbpix).astype(bool)
    # set whole last order to zeros (rejected)
    keep[-1] = np.zeros(nbpix).astype(bool)
    # ----------------------------------------------------------------------
    # construct a mask of the photometric band pass
    bands = pconst.MEAS_SNR_PHOT_BANDS()
    # a mask of just the photometric bands
    band_mask = np.zeros_like(wave_e2ds).astype(bool)
    # loop around bands
    for band in bands:
        # get the band range
        band_range = bands[band]
        # construct a mask for this band
        mask_band = (wave_e2ds > band_range[0]) & (wave_e2ds < band_range[1])
        band_mask |= mask_band
    # ----------------------------------------------------------------------
    # force into 1D and apply keep map
    flatkeep = keep.ravel()
    wavemap = wave_e2ds.ravel()[flatkeep]
    spectrum = image_e2ds.ravel()[flatkeep]
    spectrum_ini = image_e2ds_ini.ravel()[flatkeep]
    res_fwhm = res_e2ds_fwhm.ravel()[flatkeep]
    res_expo = res_e2ds_expo.ravel()[flatkeep]
    orders = orders.ravel()[flatkeep]
    band_mask = band_mask.ravel()[flatkeep]
    # deal with having a template
    if template_props['HAS_TEMPLATE']:
        template1 = np.array(template_props['TEMP_S2D'])
        template2 = template1.ravel()[flatkeep]
        # template? measure dv_abso
        force_dv_abso = False
    else:
        # no template? force expo_others to airmass
        force_airmass = False
        # template1 = np.ones_like(wave_e2ds)
        template2 = np.ones_like(wavemap)
    # ----------------------------------------------------------------------
    # load tapas in correct format
    spl_others, spl_water = load_tapas_spl(params, recipe, header,
                                           database=telludbm)
    # ----------------------------------------------------------------------
    # Calculate measured pixel to pixel scatter
    p2p_props = extract.measure_p2p_scat(params, wave_e2ds, image_e2ds_ini)
    p2p_dict = p2p_props['BP2P']


    # ----------------------------------------------------------------------
    # run the snr qc without values (to push into storage)
    sqc_value, sqc_name, sqc_logic, sqc_pass = qc_p2pscat_bands(params,
                                                                p2p_dict)
    # push into qc_params
    qc_values[0] = sqc_value
    qc_names[0] = sqc_name
    qc_logic[0] = sqc_logic
    qc_pass[0] = sqc_pass
    # make sure the median snr is above the min snr requirement
    if not bool(sqc_pass):
        # make qc_paramsfor return
        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # return qc_exit_tellu_preclean
        return qc_exit_tellu_preclean(params, recipe, image_e2ds,
                                      image_e2ds_ini, infile,
                                      wave_e2ds, qc_params, sky_model_save,
                                      res_e2ds_fwhm, res_e2ds_expo,
                                      template_props, wave_e2ds, res_s1d_fwhm,
                                      res_s1d_expo, database=telludbm)

    # ----------------------------------------------------------------------
    # get SNR for each order from header
    nbo, nbpix = infile.shape
    snr = infile.get_hkey_1d('KW_EXT_SNR', nbo, dtype=float)
    # mask all orders below min snr
    for order_num in range(nbo):
        # only mask if snr below threshold
        if snr[order_num] < snr_min_thres:
            # find order mask (we only want to remove values in this order
            order_mask = orders == order_num
            # apply low snr mask to spectrum
            spectrum[order_mask] = np.nan
    # for numerical stability, remove NaNs. Setting to zero biases a bit
    # the CCF, but this should be OK after we converge
    # spectrum[~np.isfinite(spectrum)] = 0.0
    # spectrum[spectrum < 0.0] = 0.0
    # ----------------------------------------------------------------------
    # we start the water at 4
    expo_water = 4.0
    # we start the dry component at the airmass
    expo_others = hdr_airmass
    # keep track of consecutive exponents and test convergence
    dexpo = np.inf
    # storage for the slopes from fit
    slope_water_list = []
    slope_others_list = []
    # storage for the exponential from fit
    expo_water_list = []
    expo_others_list = []
    # storage for plotting
    dexpos = []
    mean_rd_water, emean_rd_water = [], []
    mean_rd_others, emean_rd_others = [], []
    # ----------------------------------------------------------------------
    # first guess at the velocity of absorption is 0 km/s
    dv_abso = 0.0
    # set the iteration number
    iteration = 0
    # just so we have outputs
    dv_water, dv_others = np.nan, np.nan
    trans = np.ones_like(wavemap)
    # set up a qc flag
    flag_qc = False
    # log progress
    WLOG(params, '', textentry('40-019-00040'))
    # ----------------------------------------------------------------------
    # get reference trans
    trans_others = get_abso_expo(wavemap, hdr_airmass, 0.0, spl_others,
                                 spl_water, res_fwhm=res_fwhm,
                                 res_expo=res_expo, dv_abso=dv_abso,
                                 wavestart=wavestart,
                                 waveend=waveend, dvgrid=dvgrid)
    trans_water = get_abso_expo(wavemap, 0.0, 4.0, spl_others, spl_water,
                                res_fwhm=res_fwhm, res_expo=res_expo,
                                dv_abso=dv_abso, wavestart=wavestart,
                                waveend=waveend, dvgrid=dvgrid)

    # remove low transmissions - not useful here
    trans_others[trans_others < 0.1] = np.nan
    trans_water[trans_water < 0.1] = np.nan
    # take the log of other and water
    with warnings.catch_warnings(record=True) as _:
        log_others = np.log(trans_others)
        log_water = np.log(trans_water)
    # define a vector for the running sigma
    running_sigma = np.full_like(log_others, np.nan)

    # # TODO: Add to params
    # abs_bin_size = 0.1
    # abs_bin_range = [-1, 0]

    # mask the fluorescent bands
    fluorescent_mask = np.zeros_like(wavemap, dtype=bool)
    for fband in pconst.TELLU_FLUORESCENCE():
        reject = (wavemap > fband[0]) & (wavemap < fband[1])
        fluorescent_mask[reject] = True

    # define the mask for good regions of domain - in photometric bands
    #   and not in regions where fluorescent is known to happen
    emask = band_mask & ~fluorescent_mask
    emask_water = emask & (log_water > -1) & (log_water < -0.025)
    emask_others = emask & (log_others > -1) & (log_others < -0.025)


    # # get the bins for absorption
    # abs_bins = np.arange(abs_bin_range[0], abs_bin_range[1], abs_bin_size)
    # water_bins, other_bins = [], []
    # for ibin in range(len(abs_bins)):
    #
    #     # get the water bins
    #     water_mask = abs(log_water - abs_bins[ibin]) < abs_bin_size/2
    #     water_pos = np.where(water_mask & band_mask)[0]
    #     water_bins.append(water_pos)
    #     # get the other bins
    #     other_mask = abs(log_others - abs_bins[ibin]) < abs_bin_size/2
    #     # add the fluorescent mask
    #     other_mask &= ~fluorescent_mask
    #     other_pos = np.where(other_mask & band_mask)[0]
    #     other_bins.append(other_pos)

    # store approx rv and approx rv err
    approx_rvs = []
    approx_rv = 0
    rv_converged = False
    # loop around until convergence or 20th iteration
    while (dexpo > dexpo_thres) and (iteration < max_iterations):
        # set up a qc flag
        flag_qc = False
        # log progress
        args = [iteration, dexpo, expo_water, expo_others, dv_abso * 1000]
        WLOG(params, '', textentry('40-019-00041', args=args))
        # get the absorption spectrum
        trans = get_abso_expo(wavemap, expo_others, expo_water,
                              spl_others, spl_water, res_fwhm=res_fwhm,
                              res_expo=res_expo, dv_abso=dv_abso,
                              wavestart=wavestart,
                              waveend=waveend, dvgrid=dvgrid)
        # avoid division by very small values
        trans[trans < 0.01] = 0.01
        # divide spectrum by transmission
        spectrum_tmp = spectrum / (trans * template2)
        # low pass the spectrum
        with warnings.catch_warnings(record=True) as _:
            lowpass = mp.lowpassfilter(spectrum_tmp)
            spectrum_tmp_lowpass = spectrum_tmp / lowpass
        # log this low passed spectrum
        with warnings.catch_warnings(record=True) as _:
            log_spec_tmp_lowpass = np.log(spectrum_tmp_lowpass)

        mad = mp.lowpassfilter(abs(log_spec_tmp_lowpass))
        running_sigma = mad / mp.normal_fraction()
        # to avoid suspiciously small values we set the minimum to half the
        # median of valid log_spec_tmp_lowpass values
        min_sigma = np.nanmedian(running_sigma[np.isfinite(spectrum_tmp_lowpass)]) / 2
        running_sigma[running_sigma < min_sigma] = min_sigma
        # storage
        # mean_res_depth_water = np.zeros(len(abs_bins))
        # mean_res_depth_others = np.zeros(len(abs_bins))
        # err_res_depth_water = np.zeros(len(abs_bins))
        # err_res_depth_others = np.zeros(len(abs_bins))
        #
        # mean_res_depth_water1 = np.zeros(len(abs_bins))
        # mean_res_depth_others1 = np.zeros(len(abs_bins))
        # err_res_depth_water1 = np.zeros(len(abs_bins))
        # err_res_depth_others1 = np.zeros(len(abs_bins))
        #
        # for ibin in range(len(abs_bins)):
        #
        #     # measure the mean residual depth in water
        #     water_flux_in_bin = log_spec_tmp_lowpass[water_bins[ibin]]
        #     water_err_in_bin = running_sigma[water_bins[ibin]]
        #
        #     odd_out = mp.odd_ratio_mean(water_flux_in_bin, water_err_in_bin)
        #     water_in_bin_med = mp.nanmedian(water_flux_in_bin)
        #     water_in_bin_err = mp.estimate_sigma(water_flux_in_bin)
        #
        #     mean_res_depth_water[ibin] = water_in_bin_med
        #     err_res_depth_water[ibin] = water_in_bin_err
        #
        #     mean_res_depth_water1[ibin] = odd_out[0]
        #     err_res_depth_water1[ibin] = odd_out[1]
        #
        #     # measure the mean residual depth in others
        #     others_flux_in_bin = log_spec_tmp_lowpass[other_bins[ibin]]
        #     others_err_in_bin = running_sigma[other_bins[ibin]]
        #     odd_out = mp.odd_ratio_mean(others_flux_in_bin, others_err_in_bin)
        #     others_in_bin_med = mp.nanmedian(others_flux_in_bin)
        #     others_in_bin_err = mp.estimate_sigma(others_flux_in_bin)
        #
        #     mean_res_depth_others[ibin] = others_in_bin_med
        #     err_res_depth_others[ibin] = others_in_bin_err
        #
        #     mean_res_depth_others1[ibin] = odd_out[0]
        #     err_res_depth_others1[ibin] = odd_out[1]

        # # re-normalize to the mean
        # mean_res_depth_water -= np.nanmean(mean_res_depth_water)
        # mean_res_depth_others -= np.nanmean(mean_res_depth_others)
        #
        # mean_res_depth_water1 -= np.nanmean(mean_res_depth_water1)
        # mean_res_depth_others1 -= np.nanmean(mean_res_depth_others1)


        # fitting the slope of residual amplitude of water
        # fit_water = np.polyfit(abs_bins, mean_res_depth_water, deg=1,
        #                        w=1/err_res_depth_water)
        fit_water = mp.polyfit_odd_ratio(log_water[emask_water],
                                         log_spec_tmp_lowpass[emask_water],
                                         running_sigma[emask_water], 1)
        slope_water = fit_water[0]
        # append to storage
        slope_water_list.append(slope_water)
        expo_water_list.append(expo_water)
        # fitting the slope of the residual amplitude of others
        # fit_others = np.polyfit(abs_bins, mean_res_depth_others, deg=1,
        #                         w=1/err_res_depth_others)
        fit_others = mp.polyfit_odd_ratio(log_others[emask_others],
                                          log_spec_tmp_lowpass[emask_others],
                                          running_sigma[emask_others], 1)
        slope_others = fit_others[0]
        # append to storage
        slope_others_list.append(slope_others)
        expo_others_list.append(expo_others)
        # storage for plotting
        dexpos.append(np.array(dexpo))
        # mean_rd_water.append(np.array(mean_res_depth_water))
        # emean_rd_water.append(np.array(err_res_depth_water))
        # mean_rd_others.append(np.array(mean_res_depth_others))
        # emean_rd_others.append(np.array(err_res_depth_others))
        # if iteration zero we just add the slopes to the expo

        expo_water += (slope_water * expo_water)
        expo_others += (slope_others * expo_others)

        if iteration == 0:
            # finally add one to the iterator
            iteration += 1
            continue
        # ---------------------------------------------------------------------
        # only if we have more than one iteration
        # ---------------------------------------------------------------------
        # find the place where the water residuals null to zero (intercept)
        # expo_water_fit = np.polyfit(slope_water_list,
        #                            expo_water_list, deg=1)
        # expo_water = expo_water_fit[1]
        # find the place where the others residuals null to zero (intercept)
        # expo_others_fit = np.polyfit(slope_others_list,
        #                             expo_others_list, deg=1)
        # expo_others = expo_others_fit[1]
        # convergence check
        water_part = (expo_water_list[-1] - expo_water_list[-2])
        others_part = (expo_others_list[-1] - expo_others_list[-2])
        dexpo = np.sqrt(water_part**2 + others_part**2)
        # -----------------------------------------------------------------
        # if we have a template we can measure an approximate RV
        #  we can then use this to better shift the template to the data
        if template_props['HAS_TEMPLATE'] and not rv_converged:
            # get the gradient to the wave (and turn it in to a velocity)
            grad_wave = speed_of_light_ms * np.gradient(np.log(wavemap))
            # get the velocity derivative per pixel
            with warnings.catch_warnings(record=True) as _:
                velo_deriv = np.gradient(np.log(template2))/grad_wave
            # project this onto the spectrum
            with warnings.catch_warnings(record=True) as _:
                velo_proj = log_spec_tmp_lowpass/velo_deriv
                err_proj = running_sigma/velo_deriv
            # only do odd ratio mean on really clean bits of the telluric
            # spectrum
            btellu = trans > 0.9
            # find the approx velocity and its error
            app_vel, app_vel_err = mp.odd_ratio_mean(velo_proj[btellu],
                                                     err_proj[btellu])
            # we add this to the approximate rv shift
            approx_rvs.append(app_vel)
            approx_rv = approx_rv - app_vel
            approx_rv_err = float(app_vel_err)

            # TODO: Add to language database
            msg = ('\t\tApprox Rv shift: {0:.2f}+/-{1:.2f} '
                   'increment: {2:.4f} [m/s]')
            margs = [approx_rv, approx_rv_err, app_vel]
            WLOG(params, '', msg.format(*margs))

            # If we have multiple rv measurements we need to check whether it
            # is converging
            if len(approx_rvs) > 2:
                # we have two tests of convergence
                converging1 = abs(approx_rvs[-1]) < abs(approx_rvs[-2])
                converging2 = abs(approx_rvs[-1]) < app_vel_err
                # if neither test is converging we are diverging
                if not (converging1 or converging2):
                    # TODO: Add to language database
                    wmsg = 'RV shift not converging. Stopping RV shift.'
                    WLOG(params, 'warning', wmsg)
                    # set these values to values that will work
                    approx_rv, approx_rv_err, app_vel = 0, np.nan, 0
                    # we say its converged but it hasn't we just can't fit RV on
                    # this observation
                    rv_converged = True
                    # TODO: Add to language database
                    msg = ('\t\tSetting Approx Rv shift: {0:.2f}+/-{1:.2f} '
                           'increment: {2:.4f} [m/s]')
                    margs = [approx_rv, approx_rv_err, app_vel]
                    WLOG(params, '', msg.format(*margs))
            # shift the template
            template_props = shift_template(params, recipe, None,
                                            template_props, refprops,
                                            wprops, bprops,
                                            rvoffset=approx_rv,
                                            rvoffseterr=approx_rv_err,
                                            log=False)
            # update template 1 and 2 to use in next loop
            template1 = np.array(template_props['TEMP_S2D'])
            template2 = template1.ravel()[flatkeep]

            # test whether the rv has converged
            if abs(app_vel / app_vel_err) < 0.1:
                rv_converged = True
        # ------------------------------------------------------------------
        # finally add one to the iterator
        iteration += 1
    # ----------------------------------------------------------------------
    # update qc[1] qc as this is not the first iteration
    #    we have a template
    # if template_props['HAS_TEMPLATE']:
    #     # get the prev, now approx rv values
    #     qc_v = f'{approx_rvs[-2]:.4f}, {approx_rvs[-1]:.4f}'
    #     # if approx rvs have diverged then we fail QC
    #     if abs(approx_rvs[-1]) > abs(approx_rvs[-2]):
    #         qc_values[1] = qc_v
    #         qc_pass[1] = 0
    #     else:
    #         qc_values[1] = qc_v
    #         qc_pass[1] = 1
    # else:
    # qc values only if not the first iteration and with a template
    qc_values[1] = 'N.A.'
    qc_pass[1] = 1
    # ----------------------------------------------------------------------
    # deal with lower bounds for other species
    if expo_others/hdr_airmass < others_bounds[0]:
        # update qc params
        qc_values[2] = float(expo_others)/hdr_airmass
        qc_pass[2] = 0
        # flag qc as failed and break
        flag_qc = True
    else:
        qc_values[2] = float(expo_others)/hdr_airmass
        qc_pass[2] = 1
    # deal with upper bounds for other species
    if expo_others/hdr_airmass > others_bounds[1]:
        # update qc params
        qc_values[3] = float(expo_others)/hdr_airmass
        qc_pass[3] = 0
        # flag qc as failed and break
        flag_qc = True
    else:
        qc_values[3] = float(expo_others)/hdr_airmass
        qc_pass[3] = 1
    # --------------------------------------------------------------
    # deal with lower bounds for water
    if expo_water/hdr_airmass < water_bounds[0]:
        # update qc params
        qc_values[4] = float(expo_water)/hdr_airmass
        qc_pass[4] = 0
        # flag qc as failed and break
        flag_qc = True
    else:
        qc_values[4] = float(expo_water)/hdr_airmass
        qc_pass[4] = 1
    # deal with upper bounds for water
    if expo_water/hdr_airmass > water_bounds[1]:
        # update qc params
        qc_values[5] = float(expo_water)/hdr_airmass
        qc_pass[5] = 0
        # flag qc as failed and break
        flag_qc = True
    else:
        qc_values[5] = float(expo_water)/hdr_airmass
        qc_pass[5] = 1
    # ----------------------------------------------------------------------
    # deal with iterations hitting the max (no convergence)
    if iteration >= (max_iterations - 1):
        # update qc params
        qc_values[6] = iteration
        qc_pass[6] = 0
        flag_qc = True
    else:
        qc_values[6] = iteration
        qc_pass[6] = 1
    # ----------------------------------------------------------------------
    # deal with the qc flags
    if flag_qc:
        # log that qc flagged
        for qit in range(len(qc_pass)):
            if qc_pass[qit] == 0:
                wargs = [qc_logic[qit], qc_names[qit], qc_values[qit]]
                WLOG(params, 'warning', textentry('10-019-00010', args=wargs),
                     sublevel=8)

        qc_params = [qc_names, qc_values, qc_logic, qc_pass]
        # return qc_exit_tellu_preclean
        return qc_exit_tellu_preclean(params, recipe, image_e2ds,
                                      image_e2ds_ini, infile,
                                      wave_e2ds, qc_params, sky_model_save,
                                      res_e2ds_fwhm, res_e2ds_expo,
                                      template_props, wave_e2ds, res_s1d_fwhm,
                                      res_s1d_expo, database=telludbm)
    # ----------------------------------------------------------------------
    # plot the slope fit mean res plot
    recipe.plot('TELLUP_MEAN_RES',
                log_water=log_water, log_others=log_others,
                log_spec_tmp_lowpass=log_spec_tmp_lowpass,
                running_sigma=running_sigma,
                emask_water=emask_water,
                emask_others=emask_others,
                n_iterations=iteration,
                objname=infile.get_hkey('KW_OBJNAME', dtype=str),
                dprtype=infile.get_hkey('KW_DPRTYPE', dtype=str))
    recipe.plot('SUM_TELLUP_MEAN_RES',
                log_water=log_water, log_others=log_others,
                log_spec_tmp_lowpass=log_spec_tmp_lowpass,
                running_sigma=running_sigma,
                emask_water=emask_water,
                emask_others=emask_others,
                n_iterations=iteration,
                objname=infile.get_hkey('KW_OBJNAME', dtype=str),
                dprtype=infile.get_hkey('KW_DPRTYPE', dtype=str))
    # plot to show absorption spectrum
    # TODO: add switch to change labels based on template = None
    recipe.plot('TELLUP_ABSO_SPEC', trans=trans, wave=wavemap,
                thres=trans_thres, spectrum=spectrum / template2,
                spectrum_ini=spectrum_ini / template2,
                objname=infile.get_hkey('KW_OBJNAME', dtype=str),
                dprtype=infile.get_hkey('KW_DPRTYPE', dtype=str),
                clean_ohlines=clean_ohlines)
    recipe.plot('SUM_TELLUP_ABSO_SPEC', trans=trans, wave=wavemap,
                thres=trans_thres, spectrum=spectrum / template2,
                spectrum_ini=spectrum_ini / template2,
                objname=infile.get_hkey('KW_OBJNAME', dtype=str),
                dprtype=infile.get_hkey('KW_DPRTYPE', dtype=str),
                clean_ohlines=clean_ohlines)
    # ----------------------------------------------------------------------
    # create qc_params (all passed now but we have updated values)
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # ----------------------------------------------------------------------
    # get the final absorption spectrum to be used on the science data.
    #     No trimming done on the wave grid
    abso_e2ds = np.zeros_like(wave_e2ds)
    for order_num in range(wave_e2ds.shape[0]):
        owavestep = np.nanmedian(np.gradient(wave_e2ds[order_num]))
        # wave start and end need to be extended a little bit to avoid
        #     edge effects
        owavestart = np.nanmin(wave_e2ds[order_num]) - 10 * owavestep
        owaveend = np.nanmax(wave_e2ds[order_num]) + 10 * owavestep

        abso_tmp = get_abso_expo(wave_e2ds[order_num], expo_others, expo_water,
                                 spl_others, spl_water,
                                 res_fwhm=res_e2ds_fwhm[order_num],
                                 res_expo=res_e2ds_expo[order_num],
                                 dv_abso=0.0, wavestart=owavestart,
                                 waveend=owaveend, dvgrid=dvgrid)
        # push back into e2ds
        abso_e2ds[order_num] = abso_tmp
    # all absorption deeper than exp(trans_thres) is considered too deep to
    #    be corrected. We set values there to NaN
    mask = abso_e2ds < np.exp(trans_thres)
    # set deep lines to NaN
    abso_e2ds[mask] = np.nan
    # ----------------------------------------------------------------------
    # if we have a template and used skyprops we recalculate the sky correction
    # here
    sky_cond1 = sky_props is not None and sky_props['SKY_CORR_REF'] is None
    sky_cond2 = template_props['HAS_TEMPLATE']
    if sky_cond1 and sky_cond2:
        # load the blaze file for this fiber
        _, _, blaze = flat_blaze.get_blaze(params, header, fiber)
        # make the forward model
        fmodel = template_props['TEMP_S2D'] * abso_e2ds * blaze
        ratio_fmodel = image_e2ds_ini / fmodel
        # loop around order
        for order_num in range(fmodel.shape[0]):
            blazepeak = blaze[order_num] > 0.5
            # We construct a forward model of the spectrum combining the
            # template (properly RV shifted above) with telluric abso
            # (pre-clean) and the blaze. This model will be subtracted
            # from the science frame to measure sky line residuals.
            # The residuals may be under or over corrections. This is why
            # we allow for positive or negative amplitudes of line subtraction
            # within the correct_sky_no_ref function.
            fmodel_fac = np.nanmedian(ratio_fmodel[order_num][blazepeak])
            fmodel[order_num] = fmodel[order_num] *  fmodel_fac
        # correct sky using model and B fiber
        scprops = sky_corr.correct_sky_no_ref(params, recipe, infile,
                                              wprops, rawfiles, combine,
                                              calibdbm, telludbm, fmodel=fmodel)
        # now correct the original e2ds file
        corrected_e2ds = scprops[f'CORR_EXT_{infile.fiber}'] / abso_e2ds
    else:
        # now correct the original e2ds file
        corrected_e2ds = (image_e2ds_ini - sky_model) / abso_e2ds
    # ----------------------------------------------------------------------
    # correct for finite resolution effects
    # ----------------------------------------------------------------------
    # check whether user wants to do finite resolution corrections
    #   from the inputs and then from params
    if not drs_text.null_text(params['INPUTS']['FINITERES']):
        do_finite_res_corr = params['INPUTS']['FINITERES']
    else:
        do_finite_res_corr = params['TELLUP_DO_FINITE_RES_CORR']
    # correct if conditions are met
    if template_props['HAS_TEMPLATE'] and do_finite_res_corr:
        # copy the original corrected e2ds
        corrected_e2ds0 = np.array(corrected_e2ds)
        # calculate the finite resolution e2ds matrix
        finite_res_e2ds = finite_res_correction(params, template_props,
                                                wave_e2ds, res_s1d_fwhm,
                                                res_s1d_expo, expo_others,
                                                expo_water, spl_others,
                                                spl_water, dvgrid)
        # correction the spectrum
        corrected_e2ds = corrected_e2ds / finite_res_e2ds
        # add a flag that finite resolution correction was performed
        finite_res_corr = True
        # plot the finite resolution correction plot
        recipe.plot('TELLU_FINITE_RES_CORR', params=params, wavemap=wave_e2ds,
                    e2ds0=corrected_e2ds0, e2ds1=corrected_e2ds,
                    corr=finite_res_e2ds, abso_e2ds=abso_e2ds)
    else:
        finite_res_e2ds = np.ones_like(corrected_e2ds)
        # add a flag that finite resolution correction was not performed
        finite_res_corr = False
    # ----------------------------------------------------------------------
    # populate parameter dictionary
    props = ParamDict()
    props['CORRECTED_E2DS'] = corrected_e2ds
    props['TRANS_MASK'] = mask
    props['ABSO_E2DS'] = abso_e2ds
    props['SKY_MODEL'] = sky_model_save
    props['PRE_SKYCORR_IMAGE'] = image_e2ds_ini
    props['FINITE_RES_CORRECTED'] = finite_res_corr
    props['EXPO_WATER'] = expo_water
    props['EXPO_OTHERS'] = expo_others
    props['DV_WATER'] = dv_water
    props['DV_OTHERS'] = dv_others
    props['QC_PARAMS'] = qc_params
    props['SPL_TAPAS_WATER'] = spl_water
    props['SPL_TAPAS_OTHERS'] = spl_others
    # set sources
    keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
            'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'QC_PARAMS', 'SKY_MODEL',
            'PRE_SKYCORR_IMAGE',  'FINITE_RES_CORRECTED', 'SPL_TAPAS_WATER',
            'SPL_TAPAS_OTHERS']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    props['TELLUP_DO_PRECLEANING'] = do_precleaning
    props['TELLUP_D_WATER_ABSO'] = default_water_abso
    props['TELLUP_CCF_SCAN_RANGE'] = ccf_scan_range
    props['TELLUP_CLEAN_OH_LINES'] = clean_ohlines
    props['TELLUP_REMOVE_ORDS'] = remove_orders
    props['TELLUP_SNR_MIN_THRES'] = snr_min_thres
    props['TELLUP_DEXPO_CONV_THRES'] = dexpo_thres
    props['TELLUP_DEXPO_MAX_ITR'] = max_iterations
    props['TELLUP_ABSO_EXPO_KWID'] = ker_width
    props['TELLUP_ABSO_EXPO_KEXP'] = ker_shape
    props['TELLUP_TRANS_THRES'] = trans_thres
    props['TELLUP_TRANS_SIGLIM'] = trans_siglim
    props['TELLUP_FORCE_AIRMASS'] = force_airmass
    props['TELLUP_OTHER_BOUNDS'] = others_bounds
    props['TELLUP_WATER_BOUNDS'] = water_bounds
    props['TELLUP_ABSO_EXPO_KTHRES'] = ker_thres
    props['TELLUP_WAVE_START'] = wavestart
    props['TELLUP_WAVE_END'] = waveend
    props['TELLUP_DVGRID'] = dvgrid
    props['TELLU_FINITE_RES'] = finite_res_e2ds
    # set sources
    keys = ['TELLUP_D_WATER_ABSO', 'TELLUP_CCF_SCAN_RANGE',
            'TELLUP_CLEAN_OH_LINES', 'TELLUP_REMOVE_ORDS',
            'TELLUP_SNR_MIN_THRES', 'TELLUP_DEXPO_CONV_THRES',
            'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KWID',
            'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
            'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS',
            'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS',
            'TELLUP_ABSO_EXPO_KTHRES', 'TELLUP_WAVE_START',
            'TELLUP_WAVE_END', 'TELLUP_DVGRID', 'TELLUP_DO_PRECLEANING',
            'TELLU_FINITE_RES']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # save pre-cleaned file
    tellu_preclean_write(params, recipe, infile, rawfiles, fiber, combine,
                         props, wprops, sky_props, database=telludbm)
    # ----------------------------------------------------------------------
    # return props
    return props, template_props


def clean_ohline_pca(params, recipe, image, wavemap, **kwargs):
    # load ohline principle components
    func_name = __NAME__ + '.clean_ohline_pca()'
    # -------------------------------------------------------------------------
    # get parameters from params/kwargs
    assetdir = pcheck(params, 'DRS_DATA_ASSETS', 'assetsdir', kwargs, func_name)
    relfolder = pcheck(params, 'TELLU_LIST_DIRECTORY', 'directory', kwargs,
                       func_name)
    filename = pcheck(params, 'TELLUP_OHLINE_PCA_FILE', 'filename', kwargs,
                      func_name)
    nbright = pcheck(params, 'TELLUP_OHLINE_NBRIGHT', 'nbright', kwargs,
                     func_name)
    # -------------------------------------------------------------------------
    # log progress
    WLOG(params, '', textentry('40-019-00042'))
    # -------------------------------------------------------------------------
    # get shape of the e2ds
    nbo, nbpix = image.shape
    # -------------------------------------------------------------------------
    # load principle components data file
    ohfile = os.path.join(assetdir, relfolder, filename)
    ohpcdata = drs_data.load_fits_file(params, ohfile, func_name)
    # -------------------------------------------------------------------------
    # get the number of components
    n_components = ohpcdata.shape[1] - 1
    # get the ohline wave grid
    ohwave = ohpcdata[:, 0].reshape(nbo, nbpix)
    # get the principal components
    ohpcas = ohpcdata[:, 1:].reshape(nbo, nbpix, n_components)
    # ----------------------------------------------------------------------
    # replace NaNs in the science data with zeros to avoid problems in the
    #   fitting below
    ribbon_e2ds = np.array(image).ravel()
    ribbon_e2ds[~np.isfinite(ribbon_e2ds)] = 0
    # make the PCs a ribbon that is N_pc * (nbo  * nbpix)
    ribbons_pcs = np.zeros([n_components, len(ribbon_e2ds)])

    # lead the PCs and transform to the night grid
    for ncomp in range(n_components):
        # get spectrum + 1000 (as OH PCAS use 0 as a flag)
        ohspec = ohpcas[:, :, ncomp] + 1000.0
        # shift the principle component from ohwave grid to input e2ds wave grid
        ohpcshift = wave_to_wave(params, ohspec, ohwave, wavemap)
        # remove the + 1000 (so we still have the 0 flag)
        ohpcshift = ohpcshift - 1000.0
        # push into ribbons
        ribbons_pcs[ncomp] = ohpcshift.ravel()
    # -------------------------------------------------------------------------
    # output for the sky model
    sky_model = np.zeros_like(ribbon_e2ds)
    # here we could have a loop, that's why the sky_model is within the
    #    fitting function.
    # work out the grad of the diff
    vector = np.gradient(ribbon_e2ds - sky_model)
    sample = np.gradient(ribbons_pcs, axis=1)
    # linear minimisation of the ribbon's derivative to the science
    #     data derivative
    amps, model = mp.linear_minimization(vector, sample)
    # -------------------------------------------------------------------------
    # reconstruct the sky model with the amplitudes derived above
    for ncomp in range(n_components):
        sky_model += ribbons_pcs[ncomp] * amps[ncomp]
    # sky model cannot be negative
    with warnings.catch_warnings(record=True) as _:
        sky_model[sky_model < 0] = 0
    # -------------------------------------------------------------------------
    # e-width of the region over which we measure the residuals of brighter lines
    # to adjust them
    ew_weight = 2.5 * params['FWHM_PIXEL_LSF']
    # region of which we will compute the weight falloff of a bright sky line
    width = int(ew_weight * 4)
    # sky amplitude correction
    amp_sky = np.ones_like(sky_model)
    # weight vector to have a seamless falloff of the sky weight
    wrange = np.arange(-width + 0.5, width + 0.5)
    weight = np.exp(-0.5 * wrange ** 2 / ew_weight ** 2)
    # mask to know where we looked for a bright line
    mask = np.zeros_like(ribbon_e2ds)
    # keep a mask of what has actually been masked
    # mask_plot = np.zeros_like(ribbon_e2ds) + np.nan
    mask_limits = []
    # number of masked lines
    masked_lines = 0
    # -------------------------------------------------------------------------
    # loop around brightest OH lines
    for it in range(nbright):
        # find brightest sky pixel that has not yet been looked at
        imax = mp.nanargmax(sky_model + mask)
        # keep track of where we looked
        mask[imax - width:imax + width] = np.nan
        # segment of science spectrum minus current best guess of sky
        tmp1 = (ribbon_e2ds - sky_model * amp_sky)[imax - width:imax + width]
        # segment of sky sp
        tmp2 = (sky_model * amp_sky)[imax - width:imax + width]
        # work out the gradients
        gtmp1 = np.gradient(tmp1)
        gtmp2 = np.gradient(tmp2)
        # find rms of derivative of science vs sky line
        snr_line = (mp.nanstd(gtmp2) / mp.nanstd(gtmp1))
        # if above 1 sigma, we adjust
        if snr_line > 1:
            # dot product of derivative vs science sp
            part1 = mp.nansum(gtmp1 * gtmp2 * weight ** 2)
            part2 = mp.nansum(gtmp2 ** 2 * weight ** 2)
            amp = part1 / part2
            # do not deal with absorption features (sky must be emission)
            if amp < -1:
                amp = 0
            # modify the amplitude of the sky
            amp_sky[imax - width:imax + width] *= (amp * weight + 1)
            # mask_plot[imax-width:imax+width] = 0
            # for plotting and the min and max area masked
            mask_limits.append([imax - width, imax + width])
            # add to the line count
            masked_lines += 1
    # -------------------------------------------------------------------------
    # log how many lines were masked: OH Cleaning: Num of masked lines
    WLOG(params, '', textentry('40-019-00052', args=[masked_lines]))
    # store previous sky model
    sky_model0 = np.array(sky_model)
    # update sky model
    sky_model *= amp_sky
    # push sky_model into correct shape
    sky_model = sky_model.reshape(nbo, nbpix)
    # -------------------------------------------------------------------------
    # Plot the clean oh plot
    recipe.plot('TELLUP_CLEAN_OH', wave=wavemap, image=image,
                skymodel0=sky_model0, skymodel=sky_model,
                mask_limits=mask_limits)
    # -------------------------------------------------------------------------
    # return the cleaned image and sky model
    return image - sky_model, sky_model


def get_abso_expo(wavemap, expo_others, expo_water, spl_others,
                  spl_water, res_fwhm, res_expo, dv_abso, wavestart,
                  waveend, dvgrid, no_convolve: bool = False):
    """
    Returns an absorption spectrum from exponents describing water and 'others'
    in absorption

    :param wavemap: numpy nd array, wavelength grid onto which the spectrum is
                    splined
    :param expo_others: float, optical depth of all species other than water
    :param expo_water: float, optical depth of water
    :param spl_others: spline function from tapas of other species
    :param spl_water: spline function from tapas of water
    :param res_fwhm: fwhm map from the resolution map
    :param res_expo: exponent map from the resolution map
    :param dv_abso: velocity of the absorption
    :param wavestart:
    :param waveend:
    :param dvgrid: float, the s1d bin grid (constant in velocity)
    :param no_convolve: bool, if True no convolution performed (important for
                        finite resolution effect)

    :return:
    """
    # set the function name
    # _ = display_func('get_abso_expo', __NAME__)
    # ----------------------------------------------------------------------
    # for some test one may give 0 as exponents and for this we just return
    #    a flat vector
    if (expo_others == 0) and (expo_water == 0):
        return np.ones_like(wavemap)
    # ----------------------------------------------------------------------
    # define the convolution kernel for the model. This shape factor can be
    #    modified if needed
    #   divide by fwhm of a gaussian of exp = 2.0
    # width = ww / mp.fwhm()
    # # defining the convolution kernel x grid, defined over 4 fwhm
    # kernel_width = int(ww * 4)
    # dd = np.arange(-kernel_width, kernel_width + 1.0, 1.0)
    # # normalization of the kernel
    # ker = np.exp(-0.5 * np.abs(dd / width) ** ex_gau)
    # # shorten then kernel to keep only pixels that are more than 1e-6 of peak
    # ker = ker[ker > ker_thres * np.max(ker)]
    # # normalize the kernel
    # ker /= np.sum(ker)
    # ----------------------------------------------------------------------
    # create a magic grid onto which we spline our transmission, same as
    #   for the s1d_v in km/s
    magic_grid = mp.get_magic_grid(wavestart, waveend, dvgrid * 1000)
    # spline onto magic grid
    sp_others = spl_others(magic_grid)
    sp_water = spl_water(magic_grid)
    # spline the res fwhm and res expo
    sp_fwhm_magic = mp.iuv_spline(wavemap, res_fwhm, k=1, ext=3)
    sp_expo_magic = mp.iuv_spline(wavemap, res_expo, k=1, ext=3)
    # push res fwhm and res expo onto magic grid
    res_fwhm_magic = sp_fwhm_magic(magic_grid)
    res_expo_magic = sp_expo_magic(magic_grid)
    # ----------------------------------------------------------------------
    # for numerical stability, we may have values very slightly below 0 from
    #     the spline above. negative values don't work with fractional exponents
    sp_others[sp_others < 0.0] = 0.0
    sp_water[sp_water < 0.0] = 0.0
    # ----------------------------------------------------------------------
    # applying optical depths
    trans_others = sp_others ** expo_others
    trans_water = sp_water ** expo_water
    # getting the full absorption at full resolution
    trans = trans_others * trans_water
    # deal with no convolution option (important for finite resolution effect)
    if no_convolve:
        trans_convolved = np.array(trans)
    else:
        trans_convolved = variable_res_conv(magic_grid, trans, res_fwhm_magic,
                                            res_expo_magic)
    # ----------------------------------------------------------------------
    # spline that onto the input grid and allow a velocity shift
    magic_shift = magic_grid * (1 + dv_abso / speed_of_light)
    magic_spline = mp.iuv_spline(magic_shift, trans_convolved)
    # if this is a 2d array from an e2ds we loop on the orders
    if len(wavemap.shape) == 2:
        out_vector = np.zeros(wavemap.shape)
        # loop around orders and populate
        for order_num in range(wavemap.shape[0]):
            out_vector[order_num] = magic_spline(wavemap[order_num])
    # else just spline the full wave grid
    else:
        out_vector = magic_spline(wavemap)
    # ----------------------------------------------------------------------
    # cannot spline outside magic grid
    # ----------------------------------------------------------------------
    # get bounds of magic grid
    min_magic = mp.nanmin(magic_grid)
    max_magic = mp.nanmax(magic_grid)
    # set all out of bound values to NaN
    mask = (wavemap < min_magic) | (wavemap > max_magic)
    out_vector[mask] = np.nan
    # ----------------------------------------------------------------------
    # return out vector
    return out_vector


def variable_res_conv(wavemap: np.ndarray, spectrum: np.ndarray,
                      res_fwhm: np.ndarray, res_expo: np.ndarray,
                      ker_thres: float = 1e-4, ) -> np.ndarray:
    """
    Convolve with a variable kernel in resolution space

    :param wavemap: np.ndarray, wavelength grid
    :param spectrum: np.ndarray, spectrum to be convolved
    :param res_fwhm: np.ndarray, fwhm at each pixel, same shape as wave and
                     spectrum
    :param res_expo: np.ndarray, expoenent parameter for the PSF, expo=2
                     would be gaussian
    :param ker_thres: float, optional, amplitude of kernel at which we stop
                      convolution

    :return: np.ndarray, the convolved spectrum
    """
    # get shape of spectrum (2D or 1D)
    shape0 = spectrum.shape
    # -------------------------------------------------------------------------
    # if we have an e2ds ravel
    if len(shape0) == 2:
        res_fwhm = res_fwhm.ravel()
        res_expo = res_expo.ravel()
        wavemap = wavemap.ravel()
        spectrum = spectrum.ravel()
    # -------------------------------------------------------------------------
    # convolved outputs
    sumker = np.zeros_like(spectrum)
    spectrum2 = np.zeros_like(spectrum)
    # -------------------------------------------------------------------------
    # get the width of the scanning of the kernel. Default is 3 FWHM
    scale1 = np.max(res_fwhm)
    scale2 = np.median(np.gradient(wavemap) / wavemap) * speed_of_light
    range_scan = 20 * (scale1 / scale2)
    # round scan range to pixel level
    range_scan = int(np.ceil(range_scan))
    # mask nan pixels
    valid_pix = np.isfinite(spectrum)
    # set to zero the pixels that are NaNs
    spectrum[~valid_pix] = 0.0
    # convert non valid pixels to floats
    valid_pix = valid_pix.astype(float)
    # sorting by distance to center of kernel
    range2 = np.arange(-range_scan, range_scan)
    range2 = range2[np.argsort(abs(range2))]
    # calculate the super gaussian width
    ew = (res_fwhm / 2) / (2 * np.log(2)) ** (1 / res_expo)
    # -------------------------------------------------------------------------
    # loop around each offset scanning the sum and constructing local kernels
    for offset in range2:
        # get the dv offset
        dv = speed_of_light * (wavemap / np.roll(wavemap, offset) - 1)
        # calculate the kernel at this offset
        ker = mp.super_gauss_fast(dv, ew, res_expo)
        # stop convolving when threshold reached
        if np.max(ker) < ker_thres:
            break
        # no weight if the pixel was a NaN value
        ker = ker * valid_pix
        # add this kernel to the convolved spectrum
        spectrum2 = spectrum2 + np.roll(spectrum, offset) * ker
        # save the kernel
        sumker = sumker + ker
    # -------------------------------------------------------------------------
    # normalize convovled spectrum to kernel sum
    with warnings.catch_warnings(record=True) as _:
        spectrum2 = spectrum2 / sumker
    # reshape if necessary
    if len(shape0) == 2:
        spectrum2 = spectrum2.reshape(shape0)
    # return convolved spectrum
    return spectrum2


def finite_res_correction(params: ParamDict, template_props: ParamDict,
                          wave_e2ds: np.ndarray,
                          res_s1d_fwhm: np.ndarray, res_s1d_expo: np.ndarray,
                          expo_others: float, expo_water: float,
                          spl_others: Any, spl_water: Any, dvgrid: float,
                          threshold: Optional[float] = None
                          ) -> np.ndarray:
    """
    Produce an e2ds finite resolution correction matrix

    :param params: ParamDict, parameter dictionary of constants
    :param template_props: ParamDict, parameter dictionary of template
                           properties
    :param wave_e2ds: np.ndarray (2D), the e2ds wavelength solution
    :param res_s1d_fwhm: np.ndarray (1D), the resolution FWHM for each pixel of
                         the s1d
    :param res_s1d_expo: np.ndarray (1D), the resolution expo for each pixel of
                         the s1d
    :param expo_others: float, optical depth of all species other than water
    :param expo_water: float, optical depth of water
    :param spl_others: spline function from tapas of other species
    :param spl_water: spline function from tapas of water
    :param dvgrid: float, the s1d bin grid (constant in velocity)
    :param threshold: float, the transmission threshold (in exponential form)
                      for keeping valid finite res correction

    :return: np.ndarray (2D), the e2ds finite resolution correction
    """
    # set function name
    func_name = display_func('finite_res_correction', __NAME__)
    # get threshold
    thres = pcheck(params, 'TELLUP_TRANS_THRES', func=func_name,
                   override=threshold)
    # -------------------------------------------------------------------------
    # spline with slopes in domains that are not defined. We cannot have a NaN
    # in these maps.
    # -------------------------------------------------------------------------
    # pixel positions
    index = np.arange(len(res_s1d_fwhm))
    # valid map for FWHM
    fwhm_valid = np.isfinite(res_s1d_fwhm)
    # spline for FWHM
    spline_fwhm = mp.iuv_spline(index[fwhm_valid], res_s1d_fwhm[fwhm_valid],
                                k=1, ext=3)
    # map back onto original fwhm vector
    res_s1d_fwhm = spline_fwhm(index)
    # valid map for expo
    expo_valid = np.isfinite(res_s1d_expo)
    # spline for expo
    spline_expo = mp.iuv_spline(index[expo_valid], res_s1d_expo[expo_valid],
                                k=1, ext=3)
    # map back on to original expo vector
    res_s1d_expo = spline_expo(index)

    # get the deconvolved s1d template
    s1d_wave = np.array(template_props['TEMP_S1D_TABLE']['wavelength'])
    # get the deconvovled s1d template
    s1d_deconv = template_props['TEMP_S1D_TABLE']['deconv']
    # get start and end of wavelength gvrid. We add 10 wavelength steps in
    #   either direction to avoid numerical problems
    s1d_wave_step = np.nanmedian(np.gradient(s1d_wave))
    s1d_wavestart = np.min(s1d_wave) - 10 * s1d_wave_step
    s1d_waveend = np.max(s1d_wave) + 10 * s1d_wave_step
    # get the absorption spectrum prior to convolution
    #   we need the s1d_abso at full resolution. To do this, we simply
    #   set the res_s1d_fwhm to a delta function
    s1d_abso = get_abso_expo(s1d_wave, expo_others, expo_water,
                             spl_others, spl_water, res_fwhm=res_s1d_fwhm,
                             res_expo=res_s1d_expo, dv_abso=0.0,
                             wavestart=s1d_wavestart, waveend=s1d_waveend,
                             dvgrid=dvgrid, no_convolve=True)
    # spectrum as we observe it. Absorption happens at infinite resolution
    finite_error_numer = variable_res_conv(s1d_wave,
                                           s1d_deconv * s1d_abso,
                                           res_s1d_fwhm, res_s1d_expo)
    # telluric spectrum as we observe it, infinite resolution abso gets
    #     convolved
    finite_error_denom = variable_res_conv(s1d_wave, s1d_abso,
                                           res_s1d_fwhm, res_s1d_expo)
    # spectrum as we wish we had observed it. Convolved but unaffected by
    #    tellurics
    pristine_conv_s1d = variable_res_conv(s1d_wave, s1d_deconv,
                                          res_s1d_fwhm, res_s1d_expo)
    # spectrum as we correct it for tellurics. Numerator is the observed
    #    denominator is the telluric abso convolved and ratio is the
    #    corrected spectrum with finite-resolution errors in
    s1d_with_error = finite_error_numer / finite_error_denom
    # ratio of 'contaminated' to 'pristine' to find the fractional error
    #    injected in the data
    finite_err_ratio = s1d_with_error / pristine_conv_s1d
    # filter out bad finite res correction
    logfinite_err_ratio = abs(np.log(finite_err_ratio))
    valid_finite_res = logfinite_err_ratio < abs(thres)
    # spline that error to we can propagate it onto the e2ds grid
    valid = np.isfinite(finite_err_ratio) & valid_finite_res
    spl_finite_res = mp.iuv_spline(s1d_wave[valid], finite_err_ratio[valid],
                                   k=1, ext=3)
    # propagate the finite error onto the e2ds grid
    finite_res_e2ds = np.zeros_like(wave_e2ds)
    # loop around each order
    for order_num in range(wave_e2ds.shape[0]):
        finite_res_e2ds[order_num] = spl_finite_res(wave_e2ds[order_num])
    # return the finite res e2ds correction matrix
    return finite_res_e2ds


def qc_exit_tellu_preclean(params, recipe, image, image_e2ds_ini, infile,
                           wavemap, qc_params, sky_model, res_e2ds_fwhm,
                           res_e2ds_expo, template_props, wave_e2ds,
                           res_s1d_fwhm, res_s1d_expo, database=None, **kwargs):
    """
    Provides an exit point for tellu_preclean via a quality control failure

    :param params:
    :param recipe:
    :param image:
    :param infile:
    :param wavemap:
    :param qc_params:
    :param sky_model:
    :param database:

    :return:
    """
    # set the function name
    func_name = __NAME__ + '.qc_exit_tellu_preclean()'
    # ----------------------------------------------------------------------
    # get parameters from parameter dictionary
    do_precleaning = pcheck(params, 'TELLUP_DO_PRECLEANING', 'do_precleaning',
                            kwargs, func_name)
    default_water_abso = pcheck(params, 'TELLUP_D_WATER_ABSO',
                                'default_water_abso', kwargs, func_name)
    ccf_scan_range = pcheck(params, 'TELLUP_CCF_SCAN_RANGE', 'ccf_scan_range',
                            kwargs, func_name)
    clean_ohlines = pcheck(params, 'TELLUP_CLEAN_OH_LINES', 'clean_ohlines',
                           kwargs, func_name)

    remove_orders = pcheck(params, 'TELLUP_REMOVE_ORDS', 'remove_orders',
                           kwargs, func_name, mapf='list', dtype=int)
    snr_min_thres = pcheck(params, 'TELLUP_SNR_MIN_THRES', 'snr_min_thres',
                           kwargs, func_name)
    dexpo_thres = pcheck(params, 'TELLUP_DEXPO_CONV_THRES', 'dexpo_thres',
                         kwargs, func_name)
    max_iterations = pcheck(params, 'TELLUP_DEXPO_MAX_ITR', 'max_iterations',
                            kwargs, func_name)
    ker_width = pcheck(params, 'TELLUP_ABSO_EXPO_KWID', 'ker_width', kwargs,
                       func_name)
    ker_shape = pcheck(params, 'TELLUP_ABSO_EXPO_KEXP', 'ker_shape', kwargs,
                       func_name)
    trans_thres = pcheck(params, 'TELLUP_TRANS_THRES', 'trans_thres', kwargs,
                         func_name)
    trans_siglim = pcheck(params, 'TELLUP_TRANS_SIGLIM', 'trans_siglim', kwargs,
                          func_name)
    force_airmass = pcheck(params, 'TELLUP_FORCE_AIRMASS', 'force_airmass',
                           kwargs, func_name)
    others_bounds = pcheck(params, 'TELLUP_OTHER_BOUNDS', 'others_bounds',
                           kwargs, func_name, mapf='list', dtype=float)
    water_bounds = pcheck(params, 'TELLUP_WATER_BOUNDS', 'water_bounds', kwargs,
                          func_name, mapf='list', dtype=float)
    ker_thres = pcheck(params, 'TELLUP_ABSO_EXPO_KTHRES', 'ker_thres', kwargs,
                       func_name)
    wavestart = pcheck(params, 'EXT_S1D_WAVESTART', 'wavestart', kwargs,
                       func_name)
    waveend = pcheck(params, 'EXT_S1D_WAVEEND', 'waveend', kwargs, func_name)
    dvgrid = pcheck(params, 'EXT_S1D_BIN_UVELO', 'dvgrid', kwargs, func_name)
    # ----------------------------------------------------------------------
    # get image and header from infile
    image_e2ds = np.array(image)
    header = infile.get_header()
    # get airmass from header
    hdr_airmass = infile.get_hkey('KW_AIRMASS', dtype=float)
    # ----------------------------------------------------------------------
    # load tapas in correct format
    spl_others, spl_water = load_tapas_spl(params, recipe, header,
                                           database=database)
    # ----------------------------------------------------------------------
    # force expo values
    expo_others = float(hdr_airmass)
    expo_water = float(default_water_abso)
    # ----------------------------------------------------------------------
    # get the final absorption spectrum to be used on the science data.
    #     No trimming done on the wave grid
    abso_e2ds = np.zeros_like(wavemap)
    for order_num in range(wavemap.shape[0]):
        owavestep = np.nanmedian(np.gradient(wavemap[order_num]))
        # wave start and end need to be extended a little bit to avoid
        #     edge effects
        owavestart = np.nanmin(wavemap[order_num]) - 10 * owavestep
        owaveend = np.nanmax(wavemap[order_num]) + 10 * owavestep

        abso_tmp = get_abso_expo(wavemap[order_num], expo_others, expo_water,
                                 spl_others, spl_water,
                                 res_fwhm=res_e2ds_fwhm[order_num],
                                 res_expo=res_e2ds_expo[order_num],
                                 dv_abso=0.0, wavestart=owavestart,
                                 waveend=owaveend, dvgrid=dvgrid)
        # push back into e2ds
        abso_e2ds[order_num] = abso_tmp
    # ----------------------------------------------------------------------
    # mask transmission below certain threshold
    mask = abso_e2ds < np.exp(trans_thres)
    # correct e2ds
    corrected_e2ds = image_e2ds / abso_e2ds
    # mask poor tranmission regions
    corrected_e2ds[mask] = np.nan
    # ----------------------------------------------------------------------
    # correct for finite resolution effects
    # ----------------------------------------------------------------------
    # check whether user wants to do finite resolution corrections
    #   from the inputs and then from params
    if not drs_text.null_text(params['INPUTS']['FINITERES']):
        do_finite_res_corr = params['INPUTS']['FINITERES']
    else:
        do_finite_res_corr = params['TELLUP_DO_FINITE_RES_CORR']
    # correct if conditions are met
    if template_props['HAS_TEMPLATE'] and do_finite_res_corr:
        # copy the original corrected e2ds
        corrected_e2ds0 = np.array(corrected_e2ds)
        # calculate the finite resolution e2ds matrix
        finite_res_e2ds = finite_res_correction(params, template_props,
                                                wave_e2ds, res_s1d_fwhm,
                                                res_s1d_expo, expo_others,
                                                expo_water, spl_others,
                                                spl_water, dvgrid)
        # correction the spectrum
        corrected_e2ds = corrected_e2ds / finite_res_e2ds
        # add a flag that finite resolution correction was performed
        finite_res_corr = True
        # plot the finite resolution correction plot
        recipe.plot('TELLU_FINITE_RES_CORR', params=params, wavemap=wave_e2ds,
                    e2ds0=corrected_e2ds0, e2ds1=corrected_e2ds,
                    corr=finite_res_e2ds, abso_e2ds=abso_e2ds)
    else:
        finite_res_e2ds = np.ones_like(corrected_e2ds)
        # add a flag that finite resolution correction was not performed
        finite_res_corr = False
    # ----------------------------------------------------------------------
    # populate parameter dictionary
    props = ParamDict()
    props['CORRECTED_E2DS'] = corrected_e2ds
    props['TRANS_MASK'] = mask
    props['ABSO_E2DS'] = abso_e2ds
    props['SKY_MODEL'] = sky_model
    props['PRE_SKYCORR_IMAGE'] = image_e2ds_ini
    props['FINITE_RES_CORRECTED'] = finite_res_corr
    props['EXPO_WATER'] = expo_water
    props['EXPO_OTHERS'] = expo_others
    props['DV_WATER'] = np.nan
    props['DV_OTHERS'] = np.nan
    props['QC_PARAMS'] = qc_params
    props['SPL_TAPAS_WATER'] = spl_water
    props['SPL_TAPAS_OTHERS'] = spl_others
    # set sources
    keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
            'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'QC_PARAMS',
            'SKY_MODEL', 'PRE_SKYCORR_IMAGE',
            'FINITE_RES_CORRECTED', 'SPL_TAPAS_WATER', 'SPL_TAPAS_OTHERS']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    props['TELLUP_DO_PRECLEANING'] = do_precleaning
    props['TELLUP_D_WATER_ABSO'] = default_water_abso
    props['TELLUP_CCF_SCAN_RANGE'] = ccf_scan_range
    props['TELLUP_CLEAN_OH_LINES'] = clean_ohlines
    props['TELLUP_REMOVE_ORDS'] = remove_orders
    props['TELLUP_SNR_MIN_THRES'] = snr_min_thres
    props['TELLUP_DEXPO_CONV_THRES'] = dexpo_thres
    props['TELLUP_DEXPO_MAX_ITR'] = max_iterations
    props['TELLUP_ABSO_EXPO_KWID'] = ker_width
    props['TELLUP_ABSO_EXPO_KEXP'] = ker_shape
    props['TELLUP_TRANS_THRES'] = trans_thres
    props['TELLUP_TRANS_SIGLIM'] = trans_siglim
    props['TELLUP_FORCE_AIRMASS'] = force_airmass
    props['TELLUP_OTHER_BOUNDS'] = others_bounds
    props['TELLUP_WATER_BOUNDS'] = water_bounds
    props['TELLUP_ABSO_EXPO_KTHRES'] = ker_thres
    props['TELLUP_WAVE_START'] = wavestart
    props['TELLUP_WAVE_END'] = waveend
    props['TELLUP_DVGRID'] = dvgrid
    props['TELLU_FINITE_RES'] = finite_res_e2ds
    # set sources
    keys = ['TELLUP_D_WATER_ABSO', 'TELLUP_CCF_SCAN_RANGE',
            'TELLUP_CLEAN_OH_LINES', 'TELLUP_REMOVE_ORDS',
            'TELLUP_SNR_MIN_THRES', 'TELLUP_DEXPO_CONV_THRES',
            'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KWID',
            'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
            'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS',
            'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS',
            'TELLUP_ABSO_EXPO_KTHRES', 'TELLUP_WAVE_START',
            'TELLUP_WAVE_END', 'TELLUP_DVGRID', 'TELLUP_DO_PRECLEANING',
            'TELLU_FINITE_RES']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return props
    return props, template_props


def qc_p2pscat_bands(params: ParamDict, p2p_dict: Dict[str, float] = None
                     ) -> Tuple[float, str, str, float]:
        """
        Define the quality control (QC) bands for peak-to-peak scatter
        calculation

        :param params: ParamDict, the parameter dictionary of constants
        :param p2p_dict: dict, the dictionary of peak-to-peak scatter values

        :return: tuple of strings, the QC bands
        """
        # load pconst
        pconst = constants.pload()
        # get the bands
        bands = pconst.MEAS_SNR_PHOT_BANDS()
        # set up the combined SNR variable
        bvariable = 'SNR{0}'.format(''.join(list(bands.keys())))
        # get limit from params
        p2p_min_thres = params['TELLUP_SNR_MIN_THRES']
        # set up return
        qc_value = np.nan
        qc_name = bvariable
        qc_logic = '{0} < {1}'.format(bvariable, p2p_min_thres)
        qc_pass = np.nan
        # if we have a snr_dict then we load the values here
        if p2p_dict is not None:
            # assume we fail
            qc_pass = 0
            tmp_value = -np.inf
            # loop around bands
            for band in bands:
                p2p = p2p_dict.get(band, np.nan)
                # try next band if p2p is NaN
                if np.isnan(p2p):
                    continue
                # if one of the bands is above the threshold we pass
                elif p2p > p2p_min_thres:
                    qc_value = p2p
                    qc_name = 'P2P{0}'.format(band)
                    qc_logic =  '{0} < {1}'.format(bvariable, p2p_min_thres)
                    qc_pass = 1
                    break
                elif p2p > tmp_value:
                    qc_value = float(p2p)
                    qc_name = 'P2P{0}'.format(band)
                    qc_logic =  '{0} < {1}'.format(bvariable, p2p_min_thres)
                    qc_pass = 0
        # check if we still don't have a qc_value
        if np.isnan(qc_value):
            # if we get to here it means all bands were nan
            qc_value = 'All bands are NaN'
        # ----------------------------------------------------------------------
        # return the qc parameters
        return qc_value, qc_name, qc_logic, qc_pass


def tellu_preclean_write(params, recipe, infile, rawfiles, fiber, combine,
                         props, wprops, sky_props: Optional[ParamDict] = None,
                         database: Union[TelluDatabase, None] = None):
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    tpclfile = recipe.outputs['TELLU_PCLEAN'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    tpclfile.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # copy keys from input file
    tpclfile.copy_original_keys(infile)
    # add core values (that should be in all headers)
    tpclfile.add_core_hkeys(params)
    # add input files (and deal with combining or not combining)
    if combine:
        infiles = rawfiles
    else:
        infiles = [infile.basename]
    tpclfile.add_hkey_1d('KW_INFILE1', values=infiles, dim1name='file')
    # add infiles to outfile
    tpclfile.infiles = list(infiles)
    # add  calibration files used
    tpclfile.add_hkey('KW_CDBWAVE', value=wprops['WAVEFILE'])
    # ----------------------------------------------------------------------
    # get sky corr images
    if sky_props is None:
        sky_corr_sci = np.ones_like(props['CORRECTED_E2DS'])
        sky_corr_cal = np.ones_like(props['CORRECTED_E2DS'])
    else:
        sky_corr_sci = sky_props['SKY_CORR_SCI']
        # sky corr for ref can be empty - fill it with ones
        if sky_props['SKY_CORR_REF'] is None:
            sky_corr_cal = np.ones_like(props['CORRECTED_E2DS'])
        else:
            sky_corr_cal = sky_props['SKY_CORR_REF']
    # set images
    dimages = [props['CORRECTED_E2DS'], props['TRANS_MASK'].astype(float),
               props['ABSO_E2DS'], props['SKY_MODEL'],
               props['TELLU_FINITE_RES'], sky_corr_sci, sky_corr_cal]
    # add extention info
    kws1 = ['EXTDESC1', 'CORRECTED', 'Corrected image']
    kws2 = ['EXTDESC2', 'TRANS_MASK', 'Transmission mask image']
    kws3 = ['EXTDESC3', 'ABSO_E2DS', 'Absorption e2ds image']
    kws4 = ['EXTDESC4', 'PCA_SKY', 'PCA Sky model image']
    kws5 = ['EXTDESC5', 'FINITE_RES', 'Finite resolution correction']
    kws6 = ['EXTDESC6', 'SKYCORR_SCI', 'Sky file correction (sci)']
    kws7 = ['EXTDESC7', 'SKYCORR_CAL', 'Sky file correction (cal)']
    # set names of extensions (for headers)
    names = ['CORRECTED', 'TRANS_MASK', 'ABSO_E2DS', 'PCA_SKY', 'FINITE_RES',
             'SKYCORR_SCI', 'SKYCORR_CAL']
    # add to hdict
    tpclfile.add_hkey(key=kws1)
    tpclfile.add_hkey(key=kws2)
    tpclfile.add_hkey(key=kws3)
    tpclfile.add_hkey(key=kws4)
    tpclfile.add_hkey(key=kws5)
    tpclfile.add_hkey(key=kws6)
    tpclfile.add_hkey(key=kws7)
    # ----------------------------------------------------------------------
    # need to write these as header keys
    tpclfile.add_hkey('KW_TELLUP_EXPO_WATER', value=props['EXPO_WATER'])
    tpclfile.add_hkey('KW_TELLUP_EXPO_OTHERS', value=props['EXPO_OTHERS'])
    tpclfile.add_hkey('KW_TELLUP_DV_WATER', value=props['DV_WATER'])
    tpclfile.add_hkey('KW_TELLUP_DV_OTHERS', value=props['DV_OTHERS'])
    # ----------------------------------------------------------------------
    # get qc names/values/logic/pass from qc params
    qc_names, qc_values, qc_logic, qc_pass = props['QC_PARAMS']
    # first add number of QCs
    qkw = ['TQCCNUM', len(qc_names), 'Number of tellu pre-clean qcs']
    tpclfile.add_hkey(key=qkw)
    # now add the keys
    for qc_it in range(len(qc_names)):
        # add name
        qkwn = ['TQCCN{0}'.format(qc_it), qc_names[qc_it],
                'Pre-clean QCC Name {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwn)
        # add value
        qkwv = ['TQCCV{0}'.format(qc_it), qc_values[qc_it],
                'Pre-clean QCC Value {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwv)
        # add logic
        qkwl = ['TQCCL{0}'.format(qc_it), qc_logic[qc_it],
                'Pre-clean QCC Logic {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwl)
        # add pass
        qkwp = ['TQCCP{0}'.format(qc_it), qc_pass[qc_it],
                'Pre-clean QCC Pass {0}'.format(qc_it)]
        tpclfile.add_hkey(key=qkwp)
    # ----------------------------------------------------------------------
    # We also need to set the QCC_ALL param (otherwise this file will
    #   not match other products)
    passed_all_qc = np.all(props['QC_PARAMS'][3])
    tpclfile.add_hkey('KW_DRS_QC',  value=passed_all_qc)
    # We will have a special QCC param to link to the TQCC params
    tpclfile.add_qckeys([['TQCCN'], ['TQCCVN'], ['TQCCLN'], [passed_all_qc]])
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    tpclfile.add_hkey('KW_TELLUP_DO_PRECLEAN',
                      value=props['TELLUP_DO_PRECLEANING'])
    tpclfile.add_hkey('KW_TELLUP_DFLT_WATER',
                      value=props['TELLUP_D_WATER_ABSO'])
    tpclfile.add_hkey('KW_TELLUP_CCF_SRANGE',
                      value=props['TELLUP_CCF_SCAN_RANGE'])
    tpclfile.add_hkey('KW_TELLUP_CLEAN_OHLINES',
                      value=props['TELLUP_CLEAN_OH_LINES'])
    tpclfile.add_hkey('KW_TELLUP_REMOVE_ORDS',
                      value=props['TELLUP_REMOVE_ORDS'], mapf='list')
    tpclfile.add_hkey('KW_TELLUP_SNR_MIN_THRES',
                      value=props['TELLUP_SNR_MIN_THRES'])
    tpclfile.add_hkey('KW_TELLUP_DEXPO_CONV_THRES',
                      value=props['TELLUP_DEXPO_CONV_THRES'])
    tpclfile.add_hkey('KW_TELLUP_DEXPO_MAX_ITR',
                      value=props['TELLUP_DEXPO_MAX_ITR'])
    tpclfile.add_hkey('KW_TELLUP_ABSOEXPO_KTHRES',
                      value=props['TELLUP_ABSO_EXPO_KTHRES'])
    tpclfile.add_hkey('KW_TELLUP_WAVE_START', value=props['TELLUP_WAVE_START'])
    tpclfile.add_hkey('KW_TELLUP_WAVE_END', value=props['TELLUP_WAVE_END'])
    tpclfile.add_hkey('KW_TELLUP_DVGRID', value=props['TELLUP_DVGRID'])
    tpclfile.add_hkey('KW_TELLUP_ABSOEXPO_KWID',
                      value=props['TELLUP_ABSO_EXPO_KWID'])
    tpclfile.add_hkey('KW_TELLUP_ABSOEXPO_KEXP',
                      value=props['TELLUP_ABSO_EXPO_KEXP'])
    tpclfile.add_hkey('KW_TELLUP_TRANS_THRES',
                      value=props['TELLUP_TRANS_THRES'])
    tpclfile.add_hkey('KW_TELLUP_TRANS_SIGL',
                      value=props['TELLUP_TRANS_SIGLIM'])
    tpclfile.add_hkey('KW_TELLUP_FORCE_AIRMASS',
                      value=props['TELLUP_FORCE_AIRMASS'])
    tpclfile.add_hkey('KW_TELLUP_OTHER_BOUNDS',
                      value=props['TELLUP_OTHER_BOUNDS'], mapf='list')
    tpclfile.add_hkey('KW_TELLUP_WATER_BOUNDS',
                      value=props['TELLUP_WATER_BOUNDS'], mapf='list')
    # ----------------------------------------------------------------------
    # print progress
    WLOG(params, '', textentry('40-019-00044', args=[tpclfile.filename]))
    # define multi lists
    data_list = dimages[1:]
    name_list = names
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=tpclfile)]
        name_list += ['PARAM_TABLE']
    # write to file
    tpclfile.data = dimages[0]
    tpclfile.write_multi(data_list=data_list, name_list=name_list,
                         block_kind=recipe.out_block_str,
                         runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(tpclfile)
    # ----------------------------------------------------------------------
    # load database only if not already loaded
    if database is None:
        database = TelluDatabase(params)
        # load the database
        database.load_db()
    # ----------------------------------------------------------------------
    # copy the pre-cleaned file to telluDB
    database.add_tellu_file(tpclfile)


def read_tellu_preclean(params, recipe, infile, fiber, database=None):
    """
    Read all TELLU_PCLEAN files and if infile is one of them load the images
    and properties, else return None

    :param params:
    :param recipe:
    :param infile:
    :param fiber:
    :param database:

    :return:
    """

    # get infile object name
    objname = infile.get_hkey('KW_OBJNAME')

    # ------------------------------------------------------------------
    # get the tellu preclean map key
    # ----------------------------------------------------------------------
    out_pclean = drs_file.get_file_definition(params, 'TELLU_PCLEAN',
                                              block_kind='red', fiber=fiber)
    # get key
    pclean_key = out_pclean.get_dbkey()
    # load tellu file, header and abspaths
    pclean_filenames = load_tellu_file(params, pclean_key,
                                       infile.get_header(),
                                       n_entries='*', get_image=False,
                                       required=False, fiber=fiber,
                                       objname=objname, return_filename=True,
                                       database=database)
    # if we don't have the file return None
    if pclean_filenames is None:
        return None
    # ------------------------------------------------------------------
    # get copy of instance of wave file (WAVE_HCMAP)
    tpclfile = recipe.outputs['TELLU_PCLEAN'].newcopy(params=params,
                                                      fiber=fiber)
    # construct the filename from file instance
    tpclfile.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # only keep basenames
    pclean_basenames = []
    for pclean_filename in pclean_filenames:
        pclean_basenames.append(os.path.basename(pclean_filename))
    # see if file is in database
    if tpclfile.basename not in pclean_basenames:
        return None
    # else we need the location of the file
    else:
        # find the first occurance of this basename in the list
        pos = np.where(tpclfile.basename == np.array(pclean_basenames))[0][0]
        # use this to set the absolute path of the filename (as this file
        #  must be from the telluric database)
        tpclfile.set_filename(pclean_filenames[pos])
    # ----------------------------------------------------------------------
    # log progress
    # log: Reading pre-cleaned file from: {0}
    WLOG(params, '', textentry('40-019-00043', args=[tpclfile.filename]))
    # ----------------------------------------------------------------------
    # start a parameter dictionary
    props = ParamDict()
    # else we read the multi-fits file
    tpclfile.read_multi()
    # ----------------------------------------------------------------------
    # read qc parameters
    qc_names, qc_values, qc_logic, qc_pass = [], [], [], []
    # first add number of QCs
    num_qcs = tpclfile.get_hkey('TQCCNUM', dtype=int)
    # now add the keys
    for qc_it in range(num_qcs):
        # add name
        qc_names.append(tpclfile.get_hkey('TQCCN{0}'.format(qc_it), dtype=str))
        # add value
        value = tpclfile.get_hkey('TQCCV{0}'.format(qc_it), dtype=str)
        # evaluate vaule
        # noinspection PyBroadException
        try:
            qc_values.append(eval(value))
        except Exception as _:
            qc_values.append(value)
        # add logic
        qc_logic.append(tpclfile.get_hkey('TQCCL{0}'.format(qc_it), dtype=str))
        # add pass
        qc_pass.append(tpclfile.get_hkey('TQCCP{0}'.format(qc_it), dtype=int))
    # push into props
    props['QC_PARAMS'] = [qc_names, qc_values, qc_logic, qc_pass]
    # ----------------------------------------------------------------------
    # push arrays into parameter dictionary
    props['CORRECTED_E2DS'] = tpclfile.data
    props['TRANS_MASK'] = tpclfile.data_array[0].astype(bool)
    props['ABSO_E2DS'] = tpclfile.data_array[1]
    props['SKY_MODEL'] = tpclfile.data_array[2]
    # ----------------------------------------------------------------------
    # push into props
    props['EXPO_WATER'] = tpclfile.get_hkey('KW_TELLUP_EXPO_WATER', dtype=float)
    props['EXPO_OTHERS'] = tpclfile.get_hkey('KW_TELLUP_EXPO_OTHERS',
                                             dtype=float)
    props['DV_WATER'] = tpclfile.get_hkey('KW_TELLUP_DV_WATER', dtype=float)
    props['DV_OTHERS'] = tpclfile.get_hkey('KW_TELLUP_DV_OTHERS', dtype=float)
    # set sources
    keys = ['CORRECTED_E2DS', 'TRANS_MASK', 'ABSO_E2DS', 'EXPO_WATER',
            'EXPO_OTHERS', 'DV_WATER', 'DV_OTHERS', 'QC_PARAMS', 'SKY_MODEL']
    props.set_sources(keys, 'header')
    # ----------------------------------------------------------------------
    # add constants used (can come from kwargs)
    props['TELLUP_DO_PRECLEANING'] = tpclfile.get_hkey('KW_TELLUP_DO_PRECLEAN',
                                                       dtype=bool)
    props['TELLUP_D_WATER_ABSO'] = tpclfile.get_hkey('KW_TELLUP_DFLT_WATER',
                                                     dtype=float)
    props['TELLUP_CCF_SCAN_RANGE'] = tpclfile.get_hkey('KW_TELLUP_CCF_SRANGE',
                                                       dtype=float)
    kw_clean_oh = 'KW_TELLUP_CLEAN_OHLINES'
    props['TELLUP_CLEAN_OH_LINES'] = tpclfile.get_hkey(kw_clean_oh, dtype=bool)
    props['TELLUP_REMOVE_ORDS'] = tpclfile.get_hkey('KW_TELLUP_REMOVE_ORDS',
                                                    dtype=list, listtype=int)
    props['TELLUP_SNR_MIN_THRES'] = tpclfile.get_hkey('KW_TELLUP_SNR_MIN_THRES',
                                                      dtype=float)
    kw_dexpo = 'KW_TELLUP_DEXPO_CONV_THRES'
    props['TELLUP_DEXPO_CONV_THRES'] = tpclfile.get_hkey(kw_dexpo, dtype=float)
    props['TELLUP_DEXPO_MAX_ITR'] = tpclfile.get_hkey('KW_TELLUP_DEXPO_MAX_ITR',
                                                      dtype=int)
    kw_kthres = 'KW_TELLUP_ABSOEXPO_KTHRES'
    props['TELLUP_ABSO_EXPO_KTHRES'] = tpclfile.get_hkey(kw_kthres, dtype=float)
    props['TELLUP_WAVE_START'] = tpclfile.get_hkey('KW_TELLUP_WAVE_START',
                                                   dtype=float)
    props['TELLUP_WAVE_END'] = tpclfile.get_hkey('KW_TELLUP_WAVE_END',
                                                 dtype=float)
    props['TELLUP_DVGRID'] = tpclfile.get_hkey('KW_TELLUP_DVGRID', dtype=float)
    kw_ae_kwid = 'KW_TELLUP_ABSOEXPO_KWID'
    props['TELLUP_ABSO_EXPO_KWID'] = tpclfile.get_hkey(kw_ae_kwid, dtype=float)
    kw_ae_kexp = 'KW_TELLUP_ABSOEXPO_KEXP'
    props['TELLUP_ABSO_EXPO_KEXP'] = tpclfile.get_hkey(kw_ae_kexp, dtype=float)
    props['TELLUP_TRANS_THRES'] = tpclfile.get_hkey('KW_TELLUP_TRANS_THRES',
                                                    dtype=float)
    props['TELLUP_TRANS_SIGLIM'] = tpclfile.get_hkey('KW_TELLUP_TRANS_SIGL',
                                                     dtype=float)
    props['TELLUP_FORCE_AIRMASS'] = tpclfile.get_hkey('KW_TELLUP_FORCE_AIRMASS',
                                                      dtype=bool)
    props['TELLUP_OTHER_BOUNDS'] = tpclfile.get_hkey('KW_TELLUP_OTHER_BOUNDS',
                                                     dtype=list, listtype=float)
    props['TELLUP_WATER_BOUNDS'] = tpclfile.get_hkey('KW_TELLUP_WATER_BOUNDS',
                                                     dtype=list, listtype=float)
    # set the source from header
    keys = ['TELLUP_D_WATER_ABSO', 'TELLUP_CCF_SCAN_RANGE',
            'TELLUP_CLEAN_OH_LINES', 'TELLUP_REMOVE_ORDS',
            'TELLUP_SNR_MIN_THRES', 'TELLUP_DEXPO_CONV_THRES',
            'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KWID',
            'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
            'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS',
            'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS',
            'TELLUP_ABSO_EXPO_KTHRES', 'TELLUP_WAVE_START',
            'TELLUP_WAVE_END', 'TELLUP_DVGRID', 'TELLUP_DO_PRECLEANING']
    props.set_sources(keys, 'header')
    # ----------------------------------------------------------------------
    # return props
    return props


# =============================================================================
# Database functions
# =============================================================================
def load_templates(params: ParamDict,
                   header: Union[drs_fits.Header, None] = None,
                   objname: Union[str, None] = None,
                   fiber: Union[str, None] = None,
                   database: Union[TelluDatabase, None] = None) -> ParamDict:
    """
    Load the most recent template from the telluric database for 'objname'

    :param params: ParamDict, the parameter dictionary of constnats
    :param header: fits.Header or None -
    :param objname:
    :param fiber:
    :param database:
    :return:
    """
    # set function name
    func_name = display_func('load_templates', __NAME__)
    # get file definition
    out_temp = drs_file.get_file_definition(params, 'TELLU_TEMP',
                                            block_kind='red', fiber=fiber)
    # -------------------------------------------------------------------------
    # deal with user not using template
    if 'USE_TEMPLATE' in params['INPUTS']:
        if not params['INPUTS']['USE_TEMPLATE']:
            # store template properties
            temp_props = ParamDict()
            temp_props['HAS_TEMPLATE'] = False
            temp_props['TEMP_S2D'] = None
            temp_props['TEMP_FILE'] = 'None'
            temp_props['TEMP_NUM'] = 0
            temp_props['TEMP_HASH'] = 'None'
            temp_props['TEMP_TIME'] = 'None'
            temp_props['TEMP_S1D_TABLE'] = None
            temp_props['TEMP_S1D_FILE'] = 'None'
            temp_props['APPROX_RV'] = np.nan
            temp_props['APPROX_RV_ERR'] = np.nan
            # set source
            tkeys = ['TEMP_FILE', 'TEMP_NUM', 'TEMP_HASH', 'TEMP_TIME',
                     'APPROX_RV', 'APPROX_RV_ERR']
            temp_props.set_sources(tkeys, func_name)
            # return null entries
            return temp_props
    # -------------------------------------------------------------------------
    # set template filename to None
    template_filename = None
    # deal with user defining a template
    if 'TEMPLATE' in params['INPUTS']:
        if not drs_text.null_text(params['INPUTS']['TEMPLATE']):
            # set template filename
            template_filename = params['INPUTS']['TEMPLATE']
            # if template filename does not exist check in the telluric database
            if os.path.exists(template_filename):
                # get template path
                template_path = params['DRS_TELLU_DB']
                # add to template filename
                template_filename = os.path.join(template_path,
                                                 template_filename)
                # check if file exists
                if not os.path.exists(template_filename):
                    # log error
                    eargs = [os.path.basename(template_filename),
                             template_filename]
                    WLOG(params, 'error', textentry('09-019-00005', args=eargs))

    # -------------------------------------------------------------------------
    # get key
    temp_key = out_temp.get_dbkey()
    # -------------------------------------------------------------------------
    # log status
    WLOG(params, '', textentry('40-019-00045', args=[temp_key]))
    # load tellu file, header and abspaths
    temp_out = load_tellu_file(params, temp_key, header,
                               filename=template_filename, n_entries=1,
                               required=False, fiber=fiber, objname=objname,
                               database=database, mode=None, get_header=True)
    temp_image, temp_header, temp_2d_filename = temp_out
    # -------------------------------------------------------------------------
    # deal with no files in database
    if temp_image is None:
        # log that we found no templates in database
        WLOG(params, '', textentry('40-019-00003'))
        # store template properties
        temp_props = ParamDict()
        temp_props['HAS_TEMPLATE'] = False
        temp_props['TEMP_S2D'] = None
        temp_props['TEMP_FILE'] = 'None'
        temp_props['TEMP_NUM'] = 0
        temp_props['TEMP_HASH'] = 'None'
        temp_props['TEMP_TIME'] = 'None'
        temp_props['TEMP_S1D_TABLE'] = None
        temp_props['TEMP_S1D_FILE'] = 'None'
        temp_props['APPROX_RV'] = np.nan
        temp_props['APPROX_RV_ERR'] = np.nan
        # set source
        tkeys = ['TEMP_FILE', 'TEMP_NUM', 'TEMP_HASH', 'TEMP_TIME',
                 'APPROX_RV', 'APPROX_RV_ERR']
        temp_props.set_sources(tkeys, func_name)
        # return null entries
        return temp_props
    # -------------------------------------------------------------------------
    # get res_e2ds file instance
    s1d_template = drs_file.get_file_definition(params, 'TELLU_TEMP_S1DV',
                                                block_kind='red')
    # get calibration key
    s1d_key = s1d_template.get_dbkey()
    # load tellu file, header and abspaths
    temp_out = load_tellu_file(params, s1d_key, header, n_entries=1,
                               required=False, fiber=fiber,
                               objname=objname,
                               database=database, mode=None,
                               get_header=True, kind='table')
    s1d_table, _, temp_1d_filename = temp_out
    # -------------------------------------------------------------------------
    # Need to deal with case where there is no s1d table
    # deal with no files in database
    if s1d_table is None:
        # TODO: Add to language database
        # log that we found no templates in database
        emsg = ('2D Template exists ({0}) but S1D template does not. '
                'Something went wrong in template creation.')
        eargs = [temp_2d_filename]
        WLOG(params, 'error', emsg.format(*eargs))
        # return null entries
        return ParamDict()
    # -------------------------------------------------------------------------
    # log which template we are using
    wargs = [temp_2d_filename]
    WLOG(params, 'info', textentry('40-019-00005', args=wargs))
    wargs = [temp_1d_filename]
    WLOG(params, 'info', textentry('40-019-00005', args=wargs))
    # -------------------------------------------------------------------------
    # store template properties
    temp_props = ParamDict()
    temp_props['HAS_TEMPLATE'] = True
    temp_props['TEMP_S2D'] = temp_image
    temp_props['TEMP_FILE'] = temp_2d_filename
    temp_props['TEMP_NUM'] = temp_header[params['KW_MKTEMP_NFILES'][0]]
    temp_props['TEMP_HASH'] = temp_header[params['KW_MKTEMP_HASH'][0]]
    temp_props['TEMP_TIME'] = temp_header[params['KW_MKTEMP_TIME'][0]]
    temp_props['TEMP_S1D_TABLE'] = s1d_table
    temp_props['TEMP_S1D_FILE'] = temp_1d_filename
    temp_props['APPROX_RV'] = np.nan
    temp_props['APPROX_RV_ERR'] = np.nan
    # we need a copy of the s2d, s1d (so if we modify we can reset)
    temp_props['ORIG_TEMP_S2D'] = np.array(temp_props['TEMP_S2D'])
    temp_props['ORIG_TEMP_S1D_TABLE'] = Table(s1d_table)
    # set source
    tkeys = ['TEMP_S2D', 'TEMP_FILE', 'TEMP_NUM', 'TEMP_HASH', 'TEMP_TIME',
             'TEMP_S1D_TABLE', 'TEMP_S1D_FILE', 'APPROX_RV', 'APPROX_RV_ERR',
             'ORIG_TEMP_S2D', 'ORIG_TEMP_S1D_TABLE']
    temp_props.set_sources(tkeys, func_name)
    # only return most recent template
    return temp_props


def shift_template(params: ParamDict, recipe: DrsRecipe,
                   image: Optional[np.ndarray],
                   tprops: ParamDict,
                   refprops: ParamDict, wprops: ParamDict,
                   bprops: ParamDict, rvoffset: float = 0.0,
                   rvoffseterr: float = 0.0, log: bool = True) -> ParamDict:
    # set function name
    func_name = display_func('shift_template', __NAME__)
    # ------------------------------------------------------------------
    # no template - do nothing
    if not tprops['HAS_TEMPLATE']:
        return tprops
    # ------------------------------------------------------------------
    # reset the 2d and 1d templates (to their pre-shifted values)
    tprops['TEMP_S2D'] = np.array(tprops['ORIG_TEMP_S2D'])
    tprops['TEMP_S1D_TABLE'] = Table(tprops['ORIG_TEMP_S1D_TABLE'])
    # ------------------------------------------------------------------
    # get data from property dictionaries
    # ------------------------------------------------------------------
    # Get the Barycentric correction from berv props
    dv = bprops['USE_BERV'] - (rvoffset / 1000.0)
    # deal with bad berv (nan or None)
    if dv in [np.nan, None] or not isinstance(dv, (int, float)):
        eargs = [dv, func_name]
        if log:
            WLOG(params, 'error', textentry('09-016-00004', args=eargs))
    # Get the reference wavemap from reference wave props
    wavemap_ref = refprops['WAVEMAP']
    wavefile_ref = os.path.basename(refprops['WAVEFILE'])
    # Get the current wavemap from wave props
    wavemap = wprops['WAVEMAP']
    wavefile = os.path.basename(wprops['WAVEFILE'])
    # ------------------------------------------------------------------
    # Interpolate at shifted wavelengths (if we have a e2dsimage)
    # ------------------------------------------------------------------
    # Log that we are shifting the template
    if log:
        WLOG(params, '', textentry('40-019-00017'))
    # interpolate at shifted values
    dvshift = mp.relativistic_waveshift(dv, units='km/s')
    # ------------------------------------------------------------------
    # Shift the e2ds to correct wave frame
    # ------------------------------------------------------------------
    # log the shifting of PCA components
    if log:
        wargs = [wavefile_ref, wavefile]
        WLOG(params, '', textentry('40-019-00021', args=wargs))
    # shift template e2ds
    template_e2ds = wave_to_wave(params, tprops['TEMP_S2D'],
                                 wavemap_ref / dvshift,
                                 wavemap, reshape=True)
    # push into 2D vector shape = 1 by len(s1d_table)
    tmp_wave = np.array([tprops['TEMP_S1D_TABLE']['wavelength']])
    tmp_s1d = np.array([tprops['TEMP_S1D_TABLE']['flux']])
    tmp_s1d_deconv = np.array([tprops['TEMP_S1D_TABLE']['deconv']])
    # shift template s1d
    template_s1d = wave_to_wave(params, tmp_s1d,
                                          tmp_wave / dvshift,
                                          tmp_wave, reshape=False)
    template_s1d_deconv = wave_to_wave(params, tmp_s1d_deconv,
                                                 tmp_wave / dvshift,
                                                 tmp_wave, reshape=False)
    # debug plot - reconstructed spline (in loop)
    if image is not None:
        recipe.plot('FTELLU_RECON_SPLINE1', image=image, wavemap=wavemap,
                    template=template_e2ds.ravel(), order=None)
        # debug plot - reconstructed spline (selected order)
        recipe.plot('FTELLU_RECON_SPLINE2', image=image, wavemap=wavemap,
                    template=template_e2ds.ravel(),
                    order=params['FTELLU_SPLOT_ORDER'])
    # -------------------------------------------------------------------------
    # push back into template props
    tprops['TEMP_S2D'] = template_e2ds
    tprops['TEMP_S1D_TABLE']['flux'] = template_s1d
    tprops['TEMP_S1D_TABLE']['deconv'] = template_s1d_deconv
    # deal with rv offset
    tprops['APPROX_RV'] = rvoffset
    tprops['APPROX_RV_ERR'] = rvoffseterr
    # -------------------------------------------------------------------------
    # return the updated e2ds (if present)
    return tprops


def get_transmission_files(params, header, fiber, database=None):
    # get file definition
    out_trans = drs_file.get_file_definition(params, 'TELLU_TRANS',
                                             block_kind='red', fiber=fiber)
    # get key
    trans_key = out_trans.get_dbkey()
    # log status
    WLOG(params, '', textentry('40-019-00046', args=[trans_key]))
    # load tellu file, header and abspaths
    trans_filenames = load_tellu_file(params, trans_key, header, fiber=fiber,
                                      n_entries='*', get_image=False,
                                      database=database, return_filename=True)
    # storage for valid files/images/times
    valid_filenames = np.unique(trans_filenames)
    # return all valid sorted in time
    return list(valid_filenames)


def get_trans_model(params: ParamDict, header: drs_fits.Header, fiber: str,
                    database: Optional[drs_database.TelluricDatabase] = None
                    ) -> ParamDict:
    # set function name
    func_name = display_func('get_trans_model', __NAME__)
    # get file definition
    out_trans = drs_file.get_file_definition(params, 'TRANS_MODEL',
                                             block_kind='red', fiber=fiber)
    # get key
    trans_key = out_trans.get_dbkey()
    # log status
    WLOG(params, '', textentry('40-019-00046', args=[trans_key]))
    # load tellu file, header and abspaths
    trans_model = load_tellu_file(params, trans_key, header, fiber=fiber,
                                  n_entries=1, get_image=False,
                                  database=database, return_filename=True)
    # load extensions
    exts = drs_fits.readfits(params, trans_model, getdata=True,
                             fmt='fits-multi')
    # push into parameter dictionary
    tprops = ParamDict()
    tprops['ZERO_RES'] = exts[1]
    tprops['WATER_RES'] = exts[2]
    tprops['OTHERS_RES'] = exts[3]
    tprops['TRANS_TABLE'] = exts[4]
    # set source
    keys = ['ZERO_RES', 'WATER_RES', 'OTHERS_RES', 'TRANS_TABLE']
    tprops.set_sources(keys, func_name)
    # return all valid sorted in time
    return tprops


# =============================================================================
# Tapas functions
# =============================================================================
def load_conv_tapas(params, recipe, header, refprops, fiber, database=None,
                    absorbers: Union[List[str], None] = None,
                    fwhm_lsf: Union[float, None] = None,
                    only_load: bool = False):
    func_name = __NAME__ + '.load_conv_tapas()'
    # get parameters from params/kwargs
    tellu_absorbers = pcheck(params, 'TELLU_ABSORBERS', func=func_name,
                             mapf='list', dtype=str, override=absorbers)
    fwhm_pixel_lsf = pcheck(params, 'FWHM_PIXEL_LSF', func=func_name,
                            override=fwhm_lsf)
    # ----------------------------------------------------------------------
    # deal with database not being loaded
    if database is None:
        database = TelluDatabase(params)
        # load database
        database.load_db()
    # ----------------------------------------------------------------------
    # Load any convolved files from database
    # ----------------------------------------------------------------------
    # get file definition
    if 'TELLU_CONV' in recipe.outputs:
        # get file definition
        out_tellu_conv = recipe.outputs['TELLU_CONV'].newcopy(params=params,
                                                              fiber=fiber)
        # get key
        conv_key = out_tellu_conv.get_dbkey()
    else:
        # get file definition
        out_tellu_conv = drs_file.get_file_definition(params, 'TELLU_CONV',
                                                      block_kind='red',
                                                      fiber=fiber)
        out_tellu_conv.params = params
        # get key
        conv_key = out_tellu_conv.get_dbkey()
    # load tellu file
    conv_paths = load_tellu_file(params, conv_key, header, n_entries='*',
                                 get_image=False, required=False,
                                 fiber=fiber, return_filename=True,
                                 database=database)
    if conv_paths is None:
        conv_paths = []
    # construct the filename from file instance
    out_tellu_conv.construct_filename(infile=refprops['WAVEINST'],
                                      path=params['DRS_TELLU_DB'],
                                      fiber=fiber)
    # if our npy file already exists then we just need to read it
    if out_tellu_conv.filename in conv_paths:
        # log that we are loading tapas convolved file
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', textentry('40-019-00001', args=wargs))
        # ------------------------------------------------------------------
        # Load the convolved TAPAS atmospheric transmission from file
        # ------------------------------------------------------------------
        # load npy file
        out_tellu_conv.read_file(params)
        # push data into array
        tapas_all_species = out_tellu_conv.get_data(copy=True)
    # else we need to load tapas and generate the convolution
    else:
        # ------------------------------------------------------------------
        # Load the raw TAPAS atmospheric transmission
        # ------------------------------------------------------------------
        tapas_raw_table, tapas_raw_filename = drs_data.load_tapas(params)
        # ------------------------------------------------------------------
        # Convolve with reference wave solution
        # ------------------------------------------------------------------
        tapas_all_species = _convolve_tapas(params, tapas_raw_table, refprops,
                                            tellu_absorbers, fwhm_pixel_lsf)
        # ------------------------------------------------------------------
        # Save convolution for later use
        # ------------------------------------------------------------------
        out_tellu_conv.data = tapas_all_species
        # log saving
        wargs = [out_tellu_conv.filename]
        WLOG(params, '', textentry('40-019-00002', args=wargs))
        # save
        out_tellu_conv.write_npy(block_kind=recipe.out_block_str,
                                 runstring=recipe.runstring)
        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
        if not only_load:
            # npy file must set header/hdict (to update)
            out_tellu_conv.header = header
            out_tellu_conv.hdict = header
            # copy the order profile to the calibDB
            database.add_tellu_file(out_tellu_conv)

    # ------------------------------------------------------------------
    # get the tapas_water and tapas_others data
    # ------------------------------------------------------------------
    # water is the second column
    tapas_water = tapas_all_species[1, :]
    # other is defined as the product of the other columns
    tapas_other = np.prod(tapas_all_species[2:, :], axis=0)

    # return the tapas info in a ParamDict
    tapas_props = ParamDict()
    tapas_props['TAPAS_ALL_SPECIES'] = tapas_all_species
    tapas_props['TAPAS_WATER'] = tapas_water
    tapas_props['TAPAS_OTHER'] = tapas_other
    tapas_props['TAPAS_FILE'] = out_tellu_conv.filename
    tapas_props['TELLU_ABSORBERS'] = tellu_absorbers
    tapas_props['FWHM_PIXEL_LSF'] = fwhm_pixel_lsf
    # set source
    keys = ['TAPAS_ALL_SPECIES', 'TAPAS_WATER', 'TAPAS_OTHER',
            'TAPAS_FILE', 'TELLU_ABSORBERS', 'FWHM_PIXEL_LSF']
    tapas_props.set_sources(keys, func_name)
    # return tapas props
    return tapas_props


def load_tapas_spl(params, recipe, header, database=None):
    # get file definition
    tellu_tapas = drs_file.get_file_definition(params, 'TELLU_TAPAS',
                                               block_kind='red')
    # make new copy of the file definition
    out_tellu_tapas = tellu_tapas.newcopy(params=params)
    # get key
    conv_key = out_tellu_tapas.get_dbkey()
    # load tellu file
    conv_paths = load_tellu_file(params, conv_key, n_entries='*',
                                 get_image=False, required=False,
                                 return_filename=True)
    # construct the filename from file instance
    out_tellu_tapas.construct_filename(path=params['DRS_TELLU_DB'])
    # ----------------------------------------------------------------------
    # if our npy file already exists then we just need to read it
    if (conv_paths is not None) and (out_tellu_tapas.filename in conv_paths):
        out_tellu_tapas.read_file()
        # push into arrays
        tmp_tapas = out_tellu_tapas.get_data(copy=True)
        tapas_wave = tmp_tapas[0]
        trans_others = tmp_tapas[1]
        trans_water = tmp_tapas[2]
    # else we need to load it from file
    else:
        # ------------------------------------------------------------------
        # Load the raw TAPAS atmospheric transmission
        # ------------------------------------------------------------------
        tapas_raw, tapas_raw_filename = drs_data.load_tapas(params)
        # push into arrays
        tapas_wave = tapas_raw['wavelength']
        trans_others = (tapas_raw['trans_ch4'] * tapas_raw['trans_o3'] *
                        tapas_raw['trans_n2o'] * tapas_raw['trans_o2'] *
                        tapas_raw['trans_co2'])
        trans_water = tapas_raw['trans_h2o']
        # push into numpy array
        tmp_tapas = np.zeros([3, len(tapas_wave)])
        tmp_tapas[0] = tapas_wave
        tmp_tapas[1] = trans_others
        tmp_tapas[2] = trans_water
        # ------------------------------------------------------------------
        # Save tapas file for later use
        # ------------------------------------------------------------------
        # log saving
        args = [out_tellu_tapas.filename]
        WLOG(params, '', textentry('40-019-00047', args=[args]))
        # save to disk
        out_tellu_tapas.data = tmp_tapas
        out_tellu_tapas.write_npy(block_kind=recipe.out_block_str,
                                  runstring=recipe.runstring)
        # ------------------------------------------------------------------
        # Move to telluDB and update telluDB
        # ------------------------------------------------------------------
        # npy file must set header/hdict (to update)
        out_tellu_tapas.header = header
        out_tellu_tapas.hdict = header
        # deal with no database
        if database is None:
            database = TelluDatabase(params)
            # load the database
            database.load_db()
        # copy the order profile to the telluDB
        database.add_tellu_file(out_tellu_tapas, copy_files=False,
                                objname='None', airmass='None',
                                tau_water='None', tau_others='None')
    # ----------------------------------------------------------------------
    # need to spline others and water
    spl_others = mp.iuv_spline(tapas_wave, trans_others, k=1, ext=3)
    spl_water = mp.iuv_spline(tapas_wave, trans_water, k=1, ext=3)
    # return splines
    return spl_others, spl_water


# =============================================================================
# Worker functions
# =============================================================================
def _convolve_tapas(params, tapas_table, refprops, tellu_absorbers,
                    fwhm_pixel_lsf):
    # get reference wave data
    wavemap_ref = refprops['WAVEMAP']
    ydim = refprops['NBO']
    xdim = refprops['NBPIX']
    # ----------------------------------------------------------------------
    # generate kernel for convolution
    # ----------------------------------------------------------------------
    # get the number of kernal pixels
    npix_ker = int(np.ceil(3 * fwhm_pixel_lsf * 3.0 / 2) * 2 + 1)
    # set up the kernel exponent
    kernel = np.arange(npix_ker) - npix_ker // 2
    # kernal is the a gaussian
    kernel = np.exp(-0.5 * (kernel / (fwhm_pixel_lsf / mp.fwhm())) ** 2)
    # we only want an approximation of the absorption to find the continuum
    #    and estimate chemical abundances.
    #    there's no need for a varying kernel shape
    kernel /= mp.nansum(kernel)
    # ----------------------------------------------------------------------
    # storage for output
    tapas_all_species = np.zeros([len(tellu_absorbers), xdim * ydim])
    # ----------------------------------------------------------------------
    # loop around each molecule in the absorbers list
    #    (must be in
    for n_species, molecule in enumerate(tellu_absorbers):
        # log process
        wmsg = 'Processing molecule: {0}'
        WLOG(params, '', wmsg.format(molecule))
        # get wavelengths
        lam = tapas_table['wavelength']
        # get molecule transmission
        trans = tapas_table['trans_{0}'.format(molecule)]
        # interpolate with Univariate Spline
        tapas_spline = mp.iuv_spline(lam, trans)
        # log the mean transmission level
        wmsg = '\tMean Trans level: {0:.3f}'.format(np.mean(trans))
        WLOG(params, '', wmsg)
        # convolve all tapas absorption to the SPIRou approximate resolution
        for iord in range(ydim):
            # get the order position
            start = iord * xdim
            end = (iord * xdim) + xdim
            # interpolate the values at these points
            svalues = tapas_spline(wavemap_ref[iord, :])
            # convolve with a gaussian function
            nvalues = np.convolve(np.ones_like(svalues), kernel, mode='same')
            cvalues = np.convolve(svalues, kernel, mode='same') / nvalues
            # add to storage
            tapas_all_species[n_species, start: end] = cvalues
    # deal with non-real values (must be between 0 and 1
    tapas_all_species[tapas_all_species > 1] = 1
    tapas_all_species[tapas_all_species < 0] = 0

    # return tapas_all_species
    return tapas_all_species


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
