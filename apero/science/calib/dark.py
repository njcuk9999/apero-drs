#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-03-25 at 12:29

@author: cook
"""
import numpy as np
import os
import warnings

from apero.base import base
from apero.core import constants
from apero.core import math as mp
from apero import lang
from apero.core.core import drs_log, drs_file
from apero.core.utils import drs_startup
from apero.io import drs_fits
from apero.io import drs_path
from apero.io import drs_image
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
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = drs_log.wlog
# Get the text types
textentry = lang.textentry
# alias pcheck
pcheck = constants.PCheck(wlog=WLOG)


# =============================================================================
# Define dark functions
# =============================================================================
def measure_dark(params, image, entry_key, **kwargs):
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

    :return: hist numpy.histogram tuple (hist, bin_edges),
             med: float, the median value of the non-Nan image values,
             dadead: float, the fraction of dead pixels as a percentage

          where:
              hist : numpy array (1D) The values of the histogram.
              bin_edges : numpy array (1D) of floats, the bin edges
    """
    func_name = __NAME__ + '.measure_dark()'
    # check that params contains required parameters
    dark_qmin = pcheck(params, 'DARK_QMIN', 'dark_qmin', kwargs, func_name)
    dark_qmax = pcheck(params, 'DARK_QMAX', 'dark_qmax', kwargs, func_name)
    hbins = pcheck(params, 'HISTO_BINS', 'hbins', kwargs, func_name)
    hrangelow = pcheck(params, 'HISTO_RANGE_LOW', 'hlow', kwargs, func_name)
    hrangehigh = pcheck(params, 'HISTO_RANGE_HIGH', 'hhigh', kwargs, func_name)
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


def measure_dark_badpix(params, image, nanmask, **kwargs):
    """
    Measure the bad pixels (non-dark pixels and NaN pixels)

    :param params: parameter dictionary, ParamDict containing constants
            Must contain at least:
                DARK_CUT_LIMIT
    :param image: numpy array (2D), the image
    :param nanmask: numpy array (2D), the make of non-finite values
    :return:
    """
    func_name = __NAME__ + '.measure_dark_badpix()'
    # get constants from params/kwargs
    darkcutlimit = pcheck(params, 'DARK_CUTLIMIT', 'darkcutlimit', kwargs,
                           func_name)
    # get number of bad dark pixels (as a fraction of total pixels)
    with warnings.catch_warnings(record=True) as w:
        baddark = 100.0 * np.sum(image > darkcutlimit)
        baddark /= np.product(image.shape)
    # log the fraction of bad dark pixels
    wargs = [darkcutlimit, baddark]
    WLOG(params, 'info', textentry('40-011-00006', args=wargs))
    # define mask for values above cut limit or NaN
    with warnings.catch_warnings(record=True) as w:
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


def correction(params, image, nfiles, darkfile, return_dark=False):
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

    :return corrected_image: numpy array (2D), the dark corrected image
                             only returned if return_dark = True:
    :return darkimage: numpy array (2D), the dark
    """
    func_name = __NAME__ + '.correct_for_dark()'
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
# Define master dark functions
# =============================================================================
def construct_dark_table(params, filenames, **kwargs):
    # define function
    func_name = __NAME__ + '.construct_dark_table()'
    # get parameters from params
    time_thres = pcheck(params, 'DARK_MASTER_MATCH_TIME', 'time_thres', kwargs,
                        func_name)
    # define storage for table columns
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
        # get keys from hdr
        acqtime, acqmethod = drs_file.get_mid_obs_time(params, hdr,
                                                       out_fmt='mjd')
        exptime = hdr[params['KW_EXPTIME'][0]]
        ppversion = hdr[params['KW_PPVERSION'][0]]
        wt_temp = hdr[params['KW_WEATHER_TOWER_TEMP'][0]]
        cass_temp = hdr[params['KW_CASS_TEMP'][0]]
        humidity = hdr[params['KW_HUMIDITY'][0]]
        dprtype = hdr[params['KW_DPRTYPE'][0]]
        # append to lists
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
    values = [obs_dirs, basenames, filenames, dark_time, dark_exp,
              dark_pp_version, dark_wt_temp, dark_cass_temp, dark_humidity,
              dprtypes, matched_id]
    # make table using columns and values
    dark_table = drs_table.make_table(params, columns, values)
    # return table
    return dark_table


def construct_master_dark(params, recipe, dark_table, **kwargs):
    func_name = __NAME__ + '.construct_master_dark'
    # get constants from p
    med_size = pcheck(params, 'DARK_MASTER_MED_SIZE', 'med_size', kwargs,
                      func_name)
    # get col data from dark_table
    filenames = dark_table['FILENAME']
    dark_times = dark_table['MJDATE']
    filetypes = dark_table['DPRTYPE']
    matched_id = dark_table['GROUP']
    # get the most recent position
    lastpos = np.argmax(dark_times)
    # get temporary output dir
    outdir = os.path.dirname(filenames[lastpos])
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
        master_dark = drs_image.large_image_combine(params, group_dark_files,
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
    # return master dark and the reference file
    return master_dark, infile


# =============================================================================
# write files and qc functions
# =============================================================================
def master_qc(params):
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
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def write_master_files(params, recipe, reffile, master_dark, dark_table,
                       qc_params):
    # define outfile
    outfile = recipe.outputs['DARK_MASTER_FILE'].newcopy(params=params)
    # construct the filename from file instance
    outfile.construct_filename(infile=reffile)
    # ------------------------------------------------------------------
    # define header keys for output file
    # copy keys from input file
    outfile.copy_original_keys(reffile)
    # add version
    outfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    outfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    outfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    outfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    outfile.add_hkey('KW_OUTPUT', value=outfile.name)
    # add qc parameters
    outfile.add_qckeys(qc_params)
    # ------------------------------------------------------------------
    # copy data
    outfile.data = master_dark
    # log that we are saving master dark to file
    WLOG(params, '', textentry('40-011-10006', args=[outfile.filename]))
    # define multi lists
    data_list, name_list = [dark_table], ['DARK_TABLE']
    # snapshot of parameters
    if params['PARAMETER_SNAPSHOT']:
        data_list += [params.snapshot_table(recipe, drsfitsfile=outfile)]
        name_list =['PARAM_TABLE']
    else:
        data_list, name_list = [], []
    # write data and header list to file
    outfile.write_multi(block_kind=recipe.out_block_str, name_list=name_list,
                        data_list=data_list, runstring=recipe.runstring)
    # add to output files (for indexing)
    recipe.add_output_file(outfile)
    # return out file
    return outfile


def master_summary(recipe, params, qc_params, dark_table):
    # add stats
    recipe.plot.add_stat('KW_VERSION', value=params['DRS_VERSION'])
    recipe.plot.add_stat('KW_DRS_DATE', value=params['DRS_DATE'])
    recipe.plot.add_stat('NDMASTER', value=len(dark_table),
                         comment='Number DARK in Master')
    # construct summary (outside fiber loop)
    recipe.plot.summary_document(0, qc_params)


def dark_qc(params, med_full, dadeadall, baddark):
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
            WLOG(params, 'warning', textentry('40-005-10002') + farg)
        passed = 0
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params and passed
    return qc_params, passed


def dark_write_files(params, recipe, dprtype, infile, combine, rawfiles,
                     dadead_full, med_full, dadead_blue, med_blue,
                     dadead_red, med_red, qc_params, image0):
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
    # add version
    outfile.add_hkey('KW_VERSION', value=params['DRS_VERSION'])
    # add dates
    outfile.add_hkey('KW_DRS_DATE', value=params['DRS_DATE'])
    outfile.add_hkey('KW_DRS_DATE_NOW', value=params['DATE_NOW'])
    # add process id
    outfile.add_hkey('KW_PID', value=params['PID'])
    # add output tag
    outfile.add_hkey('KW_OUTPUT', value=outfile.name)
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


def dark_summary(recipe, it, params, dadead_full, med_full, dadead_blue,
                 med_blue, dadead_red, med_red, qc_params):
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
