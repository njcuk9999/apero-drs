#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO dark calibration functionality

Created on 2019-03-25 at 12:29

@author: cook
"""
import os
import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
from astropy.table import Table

from apero import lang
from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero.core.core import drs_file
from apero.core.core import drs_log
from apero.core.utils import drs_recipe
from apero.core.utils import drs_utils
from apero.io import drs_fits
from apero.io import drs_image
from apero.io import drs_path
from apero.io import drs_table

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'science.calib.dark.py'
__INSTRUMENT__ = 'None'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Get Logging function
WLOG = drs_log.wlog
# Get Recipe class
DrsRecipe = drs_recipe.DrsRecipe
# Get parameter class
ParamDict = constants.ParamDict
# Get fits file class
DrsFitsFile = drs_file.DrsFitsFile
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define dark functions
# =============================================================================
def measure_dark(params: ParamDict, image: np.ndarray, entry_key: str,
                 dark_qmin: Optional[int] = None,
                 dark_qmax: Optional[int] = None,
                 histo_bins: Optional[int] = None,
                 histo_low: Optional[int] = None,
                 histo_high: Optional[int] = None
                 ) -> Tuple[np.ndarray, float, float]:
    """
    Measure the dark pixels in "image"

    :param params: parameter dictionary, ParamDict containing constants
        Must contain at least:
                log_opt: string, log option, normally the program name
                DARK_QMIN: int, The lower percentile (0 - 100)
                DARK_QMAX: int, The upper percentile (0 - 100)
                HISTO_BINS: int,  The number of bins in dark histogram
                HISTO_RANGE_LOW: float, the lower extent of the histogram
                                 in ADU/s
                HISTO_RANGE_HIGH: float, the upper extent of the histogram
                                  in ADU/s

    :param image: numpy array (2D), the image
    :param entry_key: string, the entry key (for logging)
    :param dark_qmin: int, optional, the lower percentile when measuring the
                      dark, overrides params['DARK_QMIN']
    :param dark_qmax: int, optional, the upper percentile when measuring the
                      dark, overrides params['DARK_QMAX']
    :param histo_bins: int, optional, the numberof bins in dark histogram,
                       overrides params['HISTO_BINS']
    :param histo_low: int, optional, the lower range of the histogram in ADU/s,
                      overrides params['HISTO_RANGE_LOW']
    :param histo_high: int, optional, the upper range of the histogram in ADU/s,
                       overrides params['HIST_RANGE_HIGH']

    :returns: tuple, 1. hist numpy.histogram tuple (hist, bin_edges),
             2. med: float, the median value of the non-Nan image values,
             3. dadead: float, the fraction of dead pixels as a percentage

          where:
              hist : numpy array (1D) The values of the histogram.
              bin_edges : numpy array (1D) of floats, the bin edges
    """
    # set the function name
    func_name = __NAME__ + '.measure_dark()'
    # check that params contains required parameters
    dark_qmin = pcheck(params, 'DARK_QMIN', func=func_name, override=dark_qmin)
    dark_qmax = pcheck(params, 'DARK_QMAX', func=func_name, override=dark_qmax)
    hbins = pcheck(params, 'HISTO_BINS', func=func_name, override=histo_bins)
    hrangelow = pcheck(params, 'HISTO_RANGE_LOW', func=func_name,
                       override=histo_low)
    hrangehigh = pcheck(params, 'HISTO_RANGE_HIGH', func=func_name,
                        override=histo_high)
    # get the textdict
    image_name = textentry(entry_key)
    # make sure image is a numpy array
    # noinspection PyBroadException
    try:
        image = np.array(image)
    except Exception as e:
        eargs = [type(e), e, func_name]
        WLOG(params, 'error', textentry('00-001-00026', args=eargs))
    # flatten the image
    fimage = image.flat
    # get the finite (non-NaN) mask
    fimage = fimage[np.isfinite(fimage)]
    # get the number of NaNs
    imax = image.size - len(fimage)
    # get the median value of the non-NaN data
    med = mp.nanmedian(fimage)
    # get the 5th and 95th percentile qmin
    qmin, qmax = np.percentile(fimage, [dark_qmin, dark_qmax])
    # get the histogram for flattened data
    histo = np.histogram(fimage, bins=hbins, range=(hrangelow, hrangehigh),
                         density=True)
    # get the fraction of dead pixels as a percentage
    dadead = imax * 100 / np.product(image.shape)
    # log the dark statistics
    wargs = [image_name, dadead, med, dark_qmin, dark_qmax, qmin, qmax]
    WLOG(params, 'info', textentry('40-011-00002', args=wargs))
    # return the parameter dictionary with new values
    return np.array(histo), float(med), float(dadead)


def measure_dark_badpix(params: ParamDict, image: np.ndarray,
                        nanmask: np.ndarray,
                        dark_cutlimit: Optional[float] = None
                        ) -> Tuple[float, float]:
    """
    Measure the bad pixels (non-dark pixels and NaN pixels)

    :param params: parameter dictionary, ParamDict containing constants
            Must contain at least:
                DARK_CUT_LIMIT
    :param image: numpy array (2D), the image
    :param nanmask: numpy array (2D), the make of non-finite values
    :param dark_cutlimit: float, optional, define the bad pixel cut limit in
                          ADU/s, overrides params['DARK_CUTLIMIT']

    :return: tuple, 1. the percentage of bad dark pixels
             2. the percentage of bad dark pixels abouve cut limit
    """
    func_name = __NAME__ + '.measure_dark_badpix()'
    # get constants from params/kwargs
    darkcutlimit = pcheck(params, 'DARK_CUTLIMIT', func=func_name,
                          override=dark_cutlimit)
    # get number of bad dark pixels (as a fraction of total pixels)
    with warnings.catch_warnings(record=True) as _:
        baddark = 100.0 * np.sum(image > darkcutlimit)
        baddark /= np.product(image.shape)
    # log the fraction of bad dark pixels
    wargs = [darkcutlimit, baddark]
    WLOG(params, 'info', textentry('40-011-00006', args=wargs))
    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as _:
        datacutmask = ~((image > darkcutlimit) | nanmask)
    # get number of pixels above cut limit or NaN
    n_bad_pix = np.product(image.shape) - np.sum(datacutmask)
    # work out fraction of dead pixels + dark > cut, as percentage
    dadeadall = n_bad_pix * 100 / np.product(image.shape)
    # log fraction of dead pixels + dark > cut
    wargs = [darkcutlimit, dadeadall]
    WLOG(params, 'info', textentry('40-011-00007', args=wargs))
    # return dadeadall
    return baddark, dadeadall


def correction(params: ParamDict, image: np.ndarray, nfiles: int,
               darkfile: str, return_dark: bool = False
               ) -> Union[np.ndarray, Tuple[np.ndarray, str]]:
    """
    Corrects "image" for "dark" using calibDB file (header must contain
    value of p['ACQTIME_KEY'] as a keyword)

    :param params: parameter dictionary, ParamDict containing constants
    :param image: numpy array (2D), the image
    :param nfiles: int, number of files that created image (need to
                   multiply by this to get the total dark)
    :param darkfile: str, the absolute path to the dark calibration file
    :param return_dark: bool, if True return the dark as well as the corrected
                        image

    :returns: darkimage: numpy array (2D), the dark or tuple:
              1. darkimage, 2. the dark used for correction
    """
    _ = __NAME__ + '.correct_for_dark()'
    # -------------------------------------------------------------------------
    # do dark using correct file
    darkimage, dhdr = drs_fits.readfits(params, darkfile, gethdr=True)
    # Read dark file
    wargs = ['DARK_FILE', darkfile]
    WLOG(params, '', textentry('40-011-00011', args=wargs))
    corrected_image = image - (darkimage * nfiles)
    # -------------------------------------------------------------------------
    # finally return datac
    if return_dark:
        return corrected_image, darkimage
    else:
        return corrected_image


# =============================================================================
# Define reference dark functions
# =============================================================================
def construct_dark_table(params: ParamDict, filenames: List[str],
                         match_time: Optional[float] = None,
                         max_files: Optional[int] = None,
                         min_exptime: Optional[float] = None,
                         mode: str = 'pp') -> Table:
    """
    Construct the dark file table - consisting of all darks to use in
    dark reference calibration

    :param params: ParamDict, parameter dictionary of constants
    :param filenames: list of strings, all dark files possible to use
    :param match_time: float or None, optional, the maximum time (in hours)
                       to group files by, overrides
                       params['DARK_REF_MATCH_TIME']
    :param max_files: int or None, optional, the maximum number of files to use
                      in the dark reference calibration
    :param mode: str, 'raw' or 'pp' - changes the keywords which are used

    :return: astropy table, the filled dark file table
    """
    # define function
    func_name = __NAME__ + '.construct_dark_table()'
    # get parameters from params
    time_thres = pcheck(params, 'DARK_REF_MATCH_TIME', func=func_name,
                        override=match_time)
    max_num_files = pcheck(params, 'DARK_REF_MAX_FILES', func=func_name,
                           override=max_files)
    dark_ref_min_exptime = pcheck(params, 'DARK_REF_MIN_EXPTIME',
                                  func=func_name, override=min_exptime)
    # define storage for table columns
    dark_files = []
    dark_time, dark_exp, dark_pp_version = [], [], []
    basenames, obs_dirs, dprtypes = [], [], []
    dark_wt_temp, dark_cass_temp, dark_humidity = [], [], []
    # log that we are reading all dark files
    WLOG(params, '', textentry('40-011-10001'))
    # loop through file headers
    for it in range(len(filenames)):
        # get the basename from filenames
        basename = os.path.basename(filenames[it])
        # get the path inst
        path_inst = drs_file.DrsPath(params, abspath=filenames[it])
        # get the observation directory
        obs_dir = path_inst.obs_dir
        # read the header
        hdr = drs_fits.read_header(params, filenames[it])
        # ---------------------------------------------------------------------
        # get keys from hdr
        # ---------------------------------------------------------------------
        # deal with mid_obs_time (will not be set in raw files)
        if mode == 'pp':
            acqtime, _ = drs_file.get_mid_obs_time(params, hdr, out_fmt='mjd')
        else:
            acqtime = hdr[params['KW_MJDATE'][0]]
        # get exposure time
        exptime = hdr[params['KW_EXPTIME'][0]]
        # get pp version (will not be set in raw files)
        ppversion = hdr.get(params['KW_PPVERSION'][0], 'None')
        # do not consider dark exp time below this value
        if exptime < dark_ref_min_exptime:
            continue
        # TODO: Cannot get this value from headers currently [NIRPS]
        wt_temp = hdr.get(params['KW_WEATHER_TOWER_TEMP'][0], np.nan)
        # TODO: Cannot get this value from headers currently [NIRPS]
        cass_temp = hdr.get(params['KW_CASS_TEMP'][0], np.nan)
        # TODO: Cannot get this value from headers currently [NIRPS]
        humidity = hdr.get(params['KW_HUMIDITY'][0], np.nan)
        # deal with DPRTYPE (will not be set in raw files)
        if mode == 'pp':
            dprtype = hdr.get(params['KW_DPRTYPE'][0])
        else:
            dprtype = 'DARK_DARK'
        # append to lists
        dark_files.append(filenames[it])
        dark_time.append(float(acqtime))
        dark_exp.append(float(exptime))
        dark_pp_version.append(ppversion)
        basenames.append(basename)
        obs_dirs.append(obs_dir)
        dark_wt_temp.append(float(wt_temp))
        dark_cass_temp.append(float(cass_temp))
        dark_humidity.append(float(humidity))
        dprtypes.append(str(dprtype))

    # ----------------------------------------------------------------------
    # Only use a certain number of files to limit time taken
    # ----------------------------------------------------------------------
    dark_time = np.array(dark_time)
    time_mask = drs_utils.uniform_time_list(dark_time, max_num_files)
    # mask all lists (as numpy arrays)
    dark_files = np.array(dark_files)[time_mask]
    dark_time = np.array(dark_time)[time_mask]
    dark_exp = np.array(dark_exp)[time_mask]
    dark_pp_version = np.array(dark_pp_version)[time_mask]
    basenames = np.array(basenames)[time_mask]
    obs_dirs = np.array(obs_dirs)[time_mask]
    dprtypes = np.array(dprtypes)[time_mask]
    dark_wt_temp = np.array(dark_wt_temp)[time_mask]
    dark_cass_temp = np.array(dark_cass_temp)[time_mask]
    dark_humidity = np.array(dark_humidity)[time_mask]

    # ----------------------------------------------------------------------
    # match files by date
    # ----------------------------------------------------------------------
    # log progress
    WLOG(params, '', textentry('40-011-10002', args=[time_thres]))
    # match files by time
    matched_id = drs_path.group_files_by_time(params, np.array(dark_time),
                                              time_thres)

    # ----------------------------------------------------------------------
    # Make table
    # ----------------------------------------------------------------------
    # convert lists to table
    columns = ['OBS_DIR', 'BASENAME', 'FILENAME', 'MJDATE', 'EXPTIME',
               'PPVERSION', 'WT_TEMP', 'CASS_TEMP', 'HUMIDITY', 'DPRTYPE',
               'GROUP']
    values = [obs_dirs, basenames, dark_files, dark_time, dark_exp,
              dark_pp_version, dark_wt_temp, dark_cass_temp, dark_humidity,
              dprtypes, matched_id]
    # make table using columns and values
    dark_table = drs_table.make_table(params, columns, values)
    # return table
    return dark_table


def construct_ref_dark(params: ParamDict, dark_table: Table,
                       ref_med_size: Optional[int] = None
                       ) -> Tuple[np.ndarray, DrsFitsFile]:
    """
    Construct the reference dark calibration from the dark file table

    :param params: ParamDict, parameter dictionary of constants
    :param dark_table: astropy Table, the dark file table
    :param ref_med_size: int or None, optional, the median filter size for
                         dark reference calibration

    :return: tuple, 1. the reference dark, 2. dark file class
    """
    func_name = __NAME__ + '.construct_ref_dark'
    # get constants from p
    med_size = pcheck(params, 'DARK_REF_MED_SIZE', func=func_name,
                      override=ref_med_size)
    # get col data from dark_table
    filenames = dark_table['FILENAME']
    dark_times = dark_table['MJDATE']
    filetypes = dark_table['DPRTYPE']
    matched_id = dark_table['GROUP']
    # get the most recent position
    lastpos = np.argmax(dark_times)
    # get temporary output dir
    outdir = os.path.dirname(filenames[lastpos])
    # cannot and should not use the raw directory
    outdir = outdir.replace(params['DRS_DATA_RAW'], params['DRS_DATA_WORKING'])
    # -------------------------------------------------------------------------
    # Read individual files and sum groups
    # -------------------------------------------------------------------------
    # log process
    WLOG(params, 'info', textentry('40-011-10003'))
    # Find all unique groups
    u_groups = np.unique(matched_id)
    # storage of group dark files (for large image median)
    group_dark_files = []
    darkm_subdir = None
    # loop through groups
    for g_it, group_num in enumerate(u_groups):
        # log progress group g_it + 1 of len(u_groups)
        wargs = [g_it + 1, len(u_groups)]
        WLOG(params, '', textentry('40-011-10004', args=wargs))
        # find all files for this group
        dark_ids = filenames[matched_id == group_num]
        # load this groups files into a cube
        groupdark = drs_image.large_image_combine(params, dark_ids,
                                                  math='median',
                                                  outdir=outdir, fmt='fits')
        # -------------------------------------------------------------------
        # Must must must subtract the low frequencies
        #     --> left with a high f dark
        tmp = []
        for jt in range(-med_size, med_size + 1):
            if jt != 0:
                tmp.append(np.roll(groupdark, [0, jt]))
        # low frequency image
        with warnings.catch_warnings(record=True) as _:
            lf_dark = mp.nanmedian(tmp, axis=0)
        groupdark -= lf_dark
        # -------------------------------------------------------------------

        # save files for medianing later
        nargs = ['group_darkm_cube', g_it, groupdark, group_dark_files,
                 darkm_subdir, outdir]
        group_dark_files, darkm_subdir = drs_image.npy_filelist(params, *nargs)
    # ----------------------------------------------------------------------
    # produce the large median (write ribbons to disk to save space)
    with warnings.catch_warnings(record=True) as _:
        ref_dark = drs_image.large_image_combine(params, group_dark_files,
                                                 math='median',
                                                 outdir=outdir, fmt='npy')
    # clean up npy dir
    drs_image.npy_fileclean(params, group_dark_files, darkm_subdir, outdir)
    # -------------------------------------------------------------------------
    # get file type of last file
    filetype = filetypes[lastpos]
    # get infile from filetype
    infile = drs_file.get_file_definition(params, filetype, block_kind='tmp')
    # construct new infile instance and read data
    infile = infile.newcopy(filename=filenames[lastpos], params=params)
    infile.read_file()
    # -------------------------------------------------------------------------
    # return reference dark and the reference file
    return ref_dark, infile


# =============================================================================
# write files and qc functions
# =============================================================================
def reference_qc(params: ParamDict) -> Tuple[List[list], int]:
    """
    The dark reference quality control

    :param params: ParamDict, parameter dictionary of constants

    :return: tuple, 1. the qc lists, 2. if passed 1 else 0
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # no quality control currently
    qc_values.append('None')
    qc_names.append('None')
    qc_logic.append('None')
    qc_pass.append(1)
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def write_reference_files(params: ParamDict, recipe: DrsRecipe,
                          reffile: DrsFitsFile, ref_dark: np.ndarray,
                          dark_table: Table, qc_params: List[list]
                          ) -> DrsFitsFile:
    """
    Write the dark reference file to disk

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
    :param reffile: DrsFitsFile, an input dark file class
    :param ref_dark: numpy (2D) array, the reference dark calibration image
    :param dark_table: astropy Table, the dark file table
    :param qc_params: list of lists, the quality control lists

    :return: DrsFitsFile, the output dark reference calibration fits file class
    """
    # define outfile
    outfile = recipe.outputs['DARK_REF_FILE'].newcopy(params=params)
    # construct the filename from file instance
    outfile.construct_filename(infile=reffile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    outfile.copy_original_keys(reffile)
    # add core values (that should be in all headers)
    outfile.add_core_hkeys(params)
    # add qc parameters
    outfile.add_qckeys(qc_params)
    # ------------------------------------------------------------------
    # copy data
    outfile.data = ref_dark
    # log that we are saving reference dark to file
    WLOG(params, '', textentry('40-011-10006', args=[outfile.filename]))
    # define multi lists
    data_list, name_list = [dark_table], ['DARK_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=outfile)]
        name_list += ['PARAM_TABLE']
    else:
        data_list, name_list = [], []
    # write data and header list to file
    outfile.write_multi(block_kind=recipe.out_block_str, name_list=name_list,
                        data_list=data_list, runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(outfile)
    # return out file
    return outfile


def reference_summary(recipe: DrsRecipe, params: ParamDict,
                      qc_params: List[list], dark_table: Table):
    """
    Write the dark reference calibration summary document

    :param recipe: DrsRecipe, the recipe that called this function
    :param params: ParamDict, parameter dictionary of constants
    :param qc_params: list of lists, the quality control lists
    :param dark_table: astropy Table, the dark file table

    :return: None, writes summary document
    """
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('ND_REF', value=len(dark_table),
                         comment='Number DARK in reference')
    # construct summary (outside fiber loop)
    recipe.plot.summary_document(0, qc_params)


def dark_qc(params: ParamDict, med_full: float, dadeadall: float,
            baddark: float) -> Tuple[List[list], int]:
    """
    Dark quality control

    :param params: ParamDict, parameter dictionary of constants
    :param med_full: float, the median value of the non-Nan image values
    :param dadeadall: float, the fraction of dead pixels as a percentage
    :param baddark: float, the percentage of bad dark pixels

    :return: tuple, 1. the qc lists, 2. int 1 if passed 0 if failed
    """
    # set passed variable and fail message list
    fail_msg, qc_values, qc_names, qc_logic, qc_pass = [], [], [], [], []
    # ------------------------------------------------------------------
    # check that med < qc_max_darklevel
    if med_full > params['QC_MAX_DARKLEVEL']:
        # add failed message to fail message list
        fargs = [med_full, params['QC_MAX_DARKLEVEL']]
        fail_msg.append(textentry('40-011-00008', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(med_full)
    qc_names.append('MED_FULL')
    qc_logic.append('MED_FULL > {0:.2f}'.format(params['QC_MAX_DARKLEVEL']))
    # ------------------------------------------------------------------
    # check that fraction of dead pixels < qc_max_dead
    if dadeadall > params['QC_MAX_DEAD']:
        # add failed message to fail message list
        fargs = [dadeadall, params['QC_MAX_DEAD']]
        fail_msg.append(textentry('40-011-00009', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(dadeadall)
    qc_names.append('DADEADALL')
    qc_logic.append('DADEADALL > {0:.2f}'.format(params['QC_MAX_DEAD']))
    # ----------------------------------------------------------------------
    # checl that the precentage of dark pixels < qc_max_dark
    if baddark > params['QC_MAX_DARK']:
        fargs = [params['DARK_CUTLIMIT'], baddark, params['QC_MAX_DARK']]
        fail_msg.append(textentry('40-011-00010', args=fargs))
        qc_pass.append(0)
    else:
        qc_pass.append(1)
    # add to qc header lists
    qc_values.append(baddark)
    qc_names.append('baddark')
    qc_logic.append('baddark > {0:.2f}'.format(params['QC_MAX_DARK']))
    # ------------------------------------------------------------------
    # finally log the failed messages and set QC = 1 if we pass the
    # quality control QC = 0 if we fail quality control
    if np.sum(qc_pass) == len(qc_pass):
        WLOG(params, 'info', textentry('40-005-10001'))
        passed = 1
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', textentry('40-005-10002') + farg,
                 sublevel=6)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def dark_write_files(params: ParamDict, recipe: DrsRecipe, dprtype: str,
                     infile: DrsFitsFile, combine: bool, rawfiles: List[str],
                     dadead_full: float, med_full: float, dadead_blue: float,
                     med_blue: float, dadead_red: float, med_red: float,
                     qc_params: List[list], image0: np.ndarray) -> DrsFitsFile:
    """
    Write the dark file to disk

    :param params: ParamDict, parameter dictionary of constants
    :param recipe: DrsRecipe, the recipe that called this function
    :param dprtype: str, the data product type (DARK_DARK_INT DARK_DARK_TEL)
    :param infile: DrsFitsFile, the input dark file
    :param combine: bool, if True input dark files were combined
    :param rawfiles: list of strings, the list of input files
    :param dadead_full: float, the fraction of dead pixels as a percentage
                        across whole detector
    :param med_full: float,  the median value of the non-Nan image values across
                     whole detector
    :param dadead_blue: float, the fraction of dead pixels as a percentage in
                        blue region
    :param med_blue: float,  the median value of the non-Nan image values in
                     blue region
    :param dadead_red: float, the fraction of dead pixels as a percentage in
                       red region
    :param med_red: float,  the median value of the non-Nan image values in red
                    region
    :param qc_params: list of lists, the qc lists
    :param image0: numpy (2D) array: the final dark image

    :return: DrsFitsFile, the output dark calibration fits file class
    """
    # define outfile
    if dprtype == 'DARK_DARK_INT':
        outfile = recipe.outputs['DARK_INT_FILE'].newcopy(params=params)
    elif dprtype == 'DARK_DARK_TEL':
        outfile = recipe.outputs['DARK_TEL_FIEL'].newcopy(params=params)
    elif dprtype == 'DARK_DARK_SKY':
        outfile = recipe.outputs['DARK_SKY_FILE'].newcopy(params=params)
    else:
        outfile = None
    # construct the filename from file instance
    outfile.construct_filename(infile=infile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    outfile.copy_original_keys(infile)
    # add core values (that should be in all headers)
    outfile.add_core_hkeys(params)
    # add input files (and deal with combining or not combining)
    if combine:
        hfiles = rawfiles
    else:
        hfiles = [infile.basename]
    outfile.add_hkey_1d('KW_INFILE1', values=hfiles, dim1name='darkfile')
    # add qc parameters
    outfile.add_qckeys(qc_params)
    # add blue/red/full detector parameters
    outfile.add_hkey('KW_DARK_DEAD', value=dadead_full)
    outfile.add_hkey('KW_DARK_MED', value=med_full)
    outfile.add_hkey('KW_DARK_B_DEAD', value=dadead_blue)
    outfile.add_hkey('KW_DARK_B_MED', value=med_blue)
    outfile.add_hkey('KW_DARK_R_DEAD', value=dadead_red)
    outfile.add_hkey('KW_DARK_R_MED', value=med_red)
    # add the cut limit
    outfile.add_hkey('KW_DARK_CUT', value=params['DARK_CUTLIMIT'])
    # ------------------------------------------------------------------
    # Set to zero dark value > dark_cutlimit
    cutmask = image0 > params['DARK_CUTLIMIT']
    image0c = np.where(cutmask, np.zeros_like(image0), image0)
    # copy data
    outfile.data = image0c
    # ------------------------------------------------------------------
    # log that we are saving rotated image
    WLOG(params, '', textentry('40-011-00012', args=[outfile.filename]))
    # write image to file
    outfile.write_file()
    # add to output files (for indexing)
    recipe.add_output_file(outfile)
    # return outfile
    return outfile


def dark_summary(recipe: DrsRecipe, it: int, params: ParamDict,
                 dadead_full: float, med_full: float, dadead_blue: float,
                 med_blue: float, dadead_red: float, med_red: float,
                 qc_params: List[list]):
    """
    Write the dark calibration summary document

    :param recipe: DrsRecipe, the recipe that called this function
    :param it: int, the iteration
    :param params: ParamDict, parameter dictionary of constants
    :param dadead_full: float, the fraction of dead pixels as a percentage
                        across whole detector
    :param med_full: float,  the median value of the non-Nan image values across
                     whole detector
    :param dadead_blue: float, the fraction of dead pixels as a percentage in
                        blue region
    :param med_blue: float,  the median value of the non-Nan image values in
                     blue region
    :param dadead_red: float, the fraction of dead pixels as a percentage in
                       red region
    :param med_red: float,  the median value of the non-Nan image values in red
                    region
    :param qc_params: list of lists, the qc lists

    :return: None, writes summary document
    """
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('KW_DARK_DEAD', value=dadead_full)
    recipe.plot.add_stat('KW_DARK_MED', value=med_full)
    recipe.plot.add_stat('KW_DARK_B_DEAD', value=dadead_blue)
    recipe.plot.add_stat('KW_DARK_B_MED', value=med_blue)
    recipe.plot.add_stat('KW_DARK_R_DEAD', value=dadead_red)
    recipe.plot.add_stat('KW_DARK_R_MED', value=med_red)
    recipe.plot.add_stat('KW_DARK_CUT', value=params['DARK_CUTLIMIT'])
    # construct summary
    recipe.plot.summary_document(it, qc_params)


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
