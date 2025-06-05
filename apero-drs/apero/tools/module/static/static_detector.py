#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-06-02 at 11:37

@author: cook
"""
import os
import warnings
from typing import Any, Dict, List, Tuple

import numpy as np
from astropy.table import Table
from scipy.ndimage import zoom as scizoom

from aperocore import math as mp
from aperocore.constants import param_functions
from aperocore.core import drs_log

from apero.base import base as apero_base
from apero.io import drs_fits
from apero.tools.module.static import drs_static


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tools.module.static.static_detector.py'
__INSTRUMENT__ = 'None'
# Get version and author
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# get param dict
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# get exceptions
AperoCodedException = drs_log.AperoCodedException
# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def main(params: ParamDict, recipe, sparams: Dict[str, Any]):
    # get input file definitions
    in_path = sparams['inpath']
    dark_files = sparams['detector']['raw_dark_files']
    led_files = sparams['detector']['raw_led_files']
    engineering_flat_file = sparams['detector']['engineering_flat']
    flat_bin_size = sparams['detector']['binsize']
    frac_flat_bad = sparams['detector']['frac_flat_bad']
    dark_threshold = sparams['detector']['dark_threshold']
    # -------------------------------------------------------------------------
    # check that in path exists
    if not os.path.exists(in_path):
        emsg = 'Invalid in_path: {0}, please fix in yaml file: {1}'
        eargs = [in_path, params['INPUTS']['yamlfile']]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # -------------------------------------------------------------------------
    # sort out detector path (this is where we are saving things to)
    det_path = str(os.path.join(params['PATH.ASSETS'], 
                                params['TOOLS.STATIC.DET_PATH']))
    if not os.path.exists(det_path):
        os.makedirs(det_path)
    # -------------------------------------------------------------------------
    # Step 1: Create median dark
    static_dark = create_median_dark(params, recipe, in_path, det_path, 
                                     dark_files)
    # -------------------------------------------------------------------------
    # Step 2: Create median LED frame
    static_led = create_median_led(params, recipe, in_path, det_path, 
                                   static_dark, led_files, 
                                   engineering_flat_file)
    # -------------------------------------------------------------------------
    # Step 3: Create detector high-passed flat field
    static_flat = create_high_pass_flat(params, recipe, det_path,
                                        static_led, flat_bin_size,
                                        frac_flat_bad)
    # -------------------------------------------------------------------------
    # Step 4: Create amplifier bias model
    # -------------------------------------------------------------------------
    recon_amp, dark0 = create_dark_curr(params, recipe, in_path, det_path,
                                        dark_files)
    # -------------------------------------------------------------------------
    # Step 5: Create hot pixel reference file
    # -------------------------------------------------------------------------
    create_hotpix_map(params, recipe, det_path, dark0, static_flat,
                      dark_threshold)
    # -------------------------------------------------------------------------
    # Plots
    # -------------------------------------------------------------------------
    recipe.plot('STATIC_DET', dark0=dark0,
                n_amp=params['PP.TOTAL_AMP_NUM'], recon_amp=recon_amp)
    recipe.plot('SUM_STATIC_DET', dark0=dark0,
                n_amp=params['PP.TOTAL_AMP_NUM'], recon_amp=recon_amp)
    # -------------------------------------------------------------------------
    # Update repo
    # -------------------------------------------------------------------------
    drs_static.update_repo(params, recipe, det_path)


# =============================================================================
# Define create functions
# =============================================================================
def create_median_dark(params: ParamDict, recipe, in_path: str,  det_path: str,
                       in_dark_files: List[str]) -> np.ndarray:
    """
    Create a median dark image form the longest exposures only
    
    :param params: Parameter dictionary of constants
    :param recipe: Recipe object
    :param in_path: str, path to input file directory
    :param det_path: str, directory to save files to
    :param dark_files: List of dark image files
    
    :return np.ndarray - median dark image
    """
    # print progres
    msg = 'Creating median dark image'
    WLOG(params, 'info', msg)
    # -------------------------------------------------------------------------
    # add path to dark_files and check they exist
    dark_files = []
    for in_dark_file in in_dark_files:
        # get absolute path to dark file
        dark_file = str(os.path.join(in_path, in_dark_file))
        if not os.path.exists(dark_file):
            emsg = 'Invalid input dark file: {0}, please fix in yaml file: {1}'
            eargs = [dark_file, params['INPUTS']['yamlfile']]
            raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                      targs=eargs)
        # append to dark_files
        dark_files.append(dark_file)
    # -------------------------------------------------------------------------
    # convert list of dark files to a numpy array
    dark_files = np.array(dark_files).astype(str)
    # Pre-allocate array for exposure times of dark frames
    exptimes = np.zeros(len(dark_files))
    mjdtimes = np.zeros(len(dark_files))
    # Loop through all dark files to extract their exposure times from
    #    FITS headers
    for it, dark_file in enumerate(dark_files):
        # print reading of files
        msg = 'Reading dark frame: {0}'
        margs = [dark_file]
        WLOG(params, '', msg.format(*margs))
        hdr = drs_fits.read_header(params, str(dark_file))
        exptimes[it] = float(hdr[params['KW_EXPTIME'][0]])
        mjdtimes[it] = float(hdr[params['KW_MJDEND'][0]])
    # If the median dark frame does not exist, create it from the longest
    # exposure darks
    # TODO: Add to language database
    msg = 'Computing median dark frame from the longest exposure times'
    WLOG(params, '', msg)
    # Select only the longest exposure darks
    long_mask = exptimes == np.max(exptimes)
    long_darks = dark_files[long_mask]
    long_exptimes = exptimes[long_mask]
    long_mjds = mjdtimes[long_mask]
    # -------------------------------------------------------------------------
    # Get image shape from first file
    dark0, hdr0 = drs_fits.readfits(params, str(long_darks[0]), getdata=True,
                                    gethdr=True)
    # -------------------------------------------------------------------------
    # get basic properties of the first file
    size = dark0.shape
    # -------------------------------------------------------------------------
    # Allocate cube for stacking
    cube_dark = np.zeros((len(long_darks), size[0], size[1]), dtype=float)
    cube_dict = dict(FILENAME=[], EXPTIME=[], MJD=[])
    # Read each dark frame into the cube
    for it, long_dark_file in enumerate(long_darks):
        # get dark file
        ldark = drs_fits.readfits(params, str(long_dark_file), getdata=True)
        # push into cube
        cube_dark[it] = ldark
        # get table entries
        cube_dict['FILENAME'].append(os.path.basename(str(long_dark_file)))
        cube_dict['EXPTIME'].append(long_exptimes[it])
        cube_dict['MJD'].append(long_mjds[it])
    # -------------------------------------------------------------------------
    # Take the median across the stack
    with warnings.catch_warnings(record=True) as _:
        dark = np.nanmedian(cube_dark, axis=0)
    # convert cube_dict to astropy table
    dark_table = Table(cube_dict)
    # -------------------------------------------------------------------------
    drs_static.save_static_file(params, recipe, det_path, 'STATIC_DARK',
                                desc='median dark frame',
                                data_list=[dark, dark_table],
                                datatype_list=['image', 'table'],
                                name_list=['STATIC_DARK', 'STATIC_DARK_TABLE'])
    # -------------------------------------------------------------------------
    # return dark
    return dark


def create_median_led(params: ParamDict, recipe,
                      in_path: str, det_path: str, dark: np.ndarray,
                      in_led_files: List[str], engineering_flat: str
                      ) -> np.ndarray:
    """
    Create a median led image

    :param params: Parameter dictionary of constants
    :param recipe: Recipe object
    :param in_path: str, path to input file directory
    :param det_path: str, directory to save files to
    :param dark: np.ndarray - median dark image
    :param in_led_files: List of LED files
    :param engineering_flat: str, an engineering flat file to use (if no led
                             files given or on disk)

    :return np.ndarray - median dark image
    """
    # print progres
    msg = 'Creating median LED image'
    WLOG(params, 'info', msg)
    # -------------------------------------------------------------------------
    # first lets decide whether we are creating leds or using an engineering
    # flat
    # -------------------------------------------------------------------------
    no_leds = False
    # storage of led file absolute paths
    led_files = []
    wmsg = ''
    # deal with no led files
    if in_led_files in [None, '', 'None', 'Null']:
        no_leds = True
        wmsg = 'No LED files provided - Attempting to use Engineering flat'
        WLOG(params, 'warning', wmsg, sublevel=6)
    elif isinstance(in_led_files, list):
        if len(in_led_files) < 3:
            no_leds = True
            wmsg = 'We require at least 3 LED files to process'
            WLOG(params, 'warning', wmsg, sublevel=6)
        # add path to dark_files and check they exist
        for in_led_file in in_led_files:
            # get absolute path to dark file
            led_file = str(os.path.join(in_path, in_led_file))
            if not os.path.exists(led_file):
                no_leds = True
                wmsg = ('Invalid input LED file: {0}, '
                        'please fix in yaml file: {1}')
                margs = [led_file, params['INPUTS']['yamlfile']]
                WLOG(params, 'warning', wmsg.format(*margs), sublevel=6)
                break
            # append to dark_files
            led_files.append(led_file)
    # -------------------------------------------------------------------------
    # Case 1: No LEDs (error) and we have engineering flat
    # -------------------------------------------------------------------------
    if no_leds and engineering_flat not in ['None', None, '']:
        
        # make full path to engineering flat
        eng_flat_file = os.path.join(in_path, engineering_flat)
        if not os.path.exists(eng_flat_file):
            emsg = ('LED error and engineering flat not found: {0}.'
                    'Please correct LED error or provide an engineering flat in '
                    ' the yaml file {1}. \n\tLED Error: {2}')
            eargs = [eng_flat_file, params['INPUTS']['yamlfile'], wmsg]
            raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                      targs=eargs)
        # read the engineering flat file
        eng_flat = drs_fits.readfits(params, eng_flat_file)
        # create a flat table
        flat_table = Table([[engineering_flat]], names=['FILENAME'])
        # add a header key for satif flat mode
        hdr_kwargs = dict(KW_STATIC_FLAT_SOURCE='ENGINEERING FLAT')
        # save static file
        drs_static.save_static_file(params, recipe, det_path, 'STATIC_LED',
                                    desc='engineering flat',
                                    data_list=[eng_flat, flat_table],
                                    datatype_list=['image', 'table'],
                                    name_list=['STATIC_LED', 'STATIC_LED_TABLE'],
                                    hdr_kwargs=hdr_kwargs)
        # return the engineering flat
        return eng_flat
    # -------------------------------------------------------------------------
    # Case 2: No LEDs (error) and we don't have an engineering flat
    # -------------------------------------------------------------------------
    elif no_leds:
        emsg = ('LED error and no engineering flat defined in yaml. '
                'Please correct LED error or provide an engineering flat in '
                ' the yaml file {0}. \n\tLED Error: {1}')
        eargs = [params['INPUTS']['yamlfile'], wmsg]
        raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                  targs=eargs)
    # -------------------------------------------------------------------------
    # Case 3: Use LEDS
    # -------------------------------------------------------------------------
    # Get image shape from first file
    led0, hdr0 = drs_fits.readfits(params, str(led_files[0]), getdata=True,
                                    gethdr=True)
    # -------------------------------------------------------------------------
    # get basic properties of the first file
    size = led0.shape
    # -------------------------------------------------------------------------
    # Allocate cube for stacking
    cube_led = np.zeros((len(led_files), size[0], size[1]), dtype=float)
    # Read each dark frame into the cube
    for it, led_file in enumerate(led_files):
        # get dark file
        led_data, led_hdr = drs_fits.readfits(params, str(led_file), 
                                              getdata=True,  gethdr=True)
        # Subtract dark from each LED frame
        led_corr = led_data - dark  
        # Normalize by median value and store in cube
        cube_led[it] = led_corr / mp.nanmedian(led_corr)
    # Take median across all LED frames
    led = np.nanmedian(cube_led, axis=0)
    # create a flat table
    led_table = Table([engineering_flat], names=['FILENAME'])
    # add a header key for satif flat mode
    hdr_kwargs = dict(KW_STATIC_FLAT_SOURCE='LED FILES')
    # save static file and return flat
    drs_static.save_static_file(params, recipe, det_path, 'STATIC_LED',
                                desc='led frame',
                                data_list=[led, led_table],
                                datatype_list=['image', 'table'],
                                name_list=['STATIC_LED', 'STATIC_LED_TABLE'],
                                hdr_kwargs=hdr_kwargs)
    # -------------------------------------------------------------------------
    # return the led image
    return led
    

def create_high_pass_flat(params: ParamDict, recipe,
                          det_path: str, led: np.ndarray,
                          binsize: int,
                          frac_flat_bad: float) -> np.ndarray:
    """
    Creates high pass of the LED frame
    
    :param params: ParamDict, parameter dictionary of constants
    :param recipe: AperoRecipe object
    :param det_path: str, directory to save files to
    :param led: np.ndarray, the LED frame created with "create_median_led"
    :param binsize: int, the number of bins to use in large scale flat fielding
    :param frac_flat_bad: float, fractional threshold for flat field bad
                          pixels (relative deviation from 1)
    
    :return np.ndarray, the high passed flat
    """
    # print progres
    msg = 'Creating high-passed flat field image'
    WLOG(params, 'info', msg)
    # -------------------------------------------------------------------------
    # copy led into flat
    flat = np.array(led)
    # Compute robust statistics
    p16, p84 = mp.nanpercentile(flat, [16, 84])
    # get robust standard deviation
    sig = (p84 - p16) / 2
    # Identify bad pixels in the flat field (outliers and negatives)
    bad_pix = (flat < p16 - 3*sig) | (flat > p84 + 3*sig) | (flat < 0)
    # set bad pixels to nan
    flat[bad_pix] = np.nan
    # normalize by the median
    flat = flat / mp.nanmedian(flat)
    # -------------------------------------------------------------------------
    # Prepare for iterative large-scale flat correction
    binned_image = np.zeros((flat.shape[0] // binsize, flat.shape[1] // binsize))
    # storage for previous iteration's binned image
    prev_image = np.zeros_like(binned_image)
    # convergence metric
    sig_step = np.inf
    # iteration counter
    iteration = 0
    # -------------------------------------------------------------------------
    # Iteratively divide by a smoothed version of the flat to remove
    # large-scale structure
    while (sig_step > 1e-4):
        # print progress
        msg = '\tIteration {0}, previous step: {1:.4e}'
        margs = [iteration, sig_step]
        WLOG(params, '', msg.format(*margs))
        # median bin the image
        binned_image = mp.medbin(flat, flat.shape[0] // binsize,
                                 flat.shape[1] // binsize)
        # Upsample binned image
        recon = scizoom(binned_image, binsize, order=1)
        # Divide by smoothed image
        flat /= recon
        # Check for convergence
        sig_step = mp.nanmedian(np.abs(binned_image - prev_image))
        # Store for next iteration
        prev_image = np.array(binned_image)
        iteration += 1
    # -------------------------------------------------------------------------
    # Pixels too far from 1 are bad
    bad_pix = np.abs(flat - 1) > frac_flat_bad
    # mask bad pixels
    flat[bad_pix] = np.nan
    # save static file and return flat
    drs_static.save_static_file(params, recipe, det_path, 'STATIC_LED',
                                desc='led frame',
                                data_list=[flat],
                                datatype_list=['image'],
                                name_list=['STATIC_FLAT'])
    # return the flat
    return flat



def create_dark_curr(params: ParamDict, recipe, in_path: str,  det_path: str,
                     in_dark_files: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create amplifier dark current model

    :param params: Parameter dictionary of constants
    :param recipe: Recipe object
    :param in_path: str, path to input file directory
    :param det_path: str, directory to save files to
    :param dark_files: List of dark image files

    :return np.ndarray - median dark image
    """
    # print progres
    msg = 'Creating amplifier dark current image'
    WLOG(params, 'info', msg)
    # -------------------------------------------------------------------------
    # add path to dark_files and check they exist
    dark_files = []
    for in_dark_file in in_dark_files:
        # get absolute path to dark file
        dark_file = str(os.path.join(in_path, in_dark_file))
        if not os.path.exists(dark_file):
            emsg = 'Invalid input dark file: {0}, please fix in yaml file: {1}'
            eargs = [dark_file, params['INPUTS']['yamlfile']]
            raise AperoCodedException(params, None, message=emsg.format(*eargs),
                                      targs=eargs)
        # append to dark_files
        dark_files.append(dark_file)
    # -------------------------------------------------------------------------
    # Get image shape from first file
    dark0, dhdr0 = drs_fits.readfits(params, str(dark_files[0]), getdata=True,
                                     gethdr=True)
    # -------------------------------------------------------------------------
    # get basic properties of the first file
    size = dark0.shape
    # get the number of amplifiers from parameters
    n_amp = params['PP.TOTAL_AMP_NUM']
    # set up the storage vectors
    cube_amps = np.zeros((len(dark_files), size[0], size[1] // n_amp),
                         dtype=float)
    intercept = np.zeros((size[0], size[1] // n_amp), dtype=float)
    slope = np.zeros((size[0], size[1] // n_amp), dtype=float)
    # Pre-allocate array for exposure times and dates of dark frames
    exptimes = np.zeros(len(dark_files))
    mjdtimes = np.zeros(len(dark_files))
    # ---------------------------------------------------------------------
    # loop around files
    for it, dark_file in enumerate(dark_files):
        # read the dark file
        dark, dhdr = drs_fits.readfits(params, dark_file, getdata=True,
                                       gethdr=True)
        # get the exposure time and mjd time
        exptimes[it] = float(dhdr[params['KW_EXPTIME'][0]])
        mjdtimes[it] = float(dhdr[params['KW_MJDEND'][0]])
        # Size of each amplifier region
        amp_size = size[0] // n_amp
        # ---------------------------------------------------------------------
        # store the amps for this dark image
        cubeamp = np.zeros((n_amp, size[0], size[1] // n_amp))
        # loop aroun amplifiers
        for i_amp in range(n_amp):
            # Extract amplifier region
            slice = dark[:, i_amp * amp_size:(i_amp + 1) * amp_size]
            # Normalize by median
            slice -= np.nanmedian(slice)
            if i_amp % 2 == 0:
                # Even amplifiers: no flip
                slice2 = slice
            else:
                # Odd amplifiers: flip horizontally
                slice2 = slice[:, ::-1]
            # Store in cube
            cubeamp[i_amp, :, :] = slice2
        # ---------------------------------------------------------------------
        # fold into amplifier regions and store in cube
        cube_amps[it] = mp.nanmedian(cubeamp, axis=0)
    # -------------------------------------------------------------------------
    # we need to fit across exptime time so we need at least two different
    # exposure times
    uexptimes = np.unique(exptimes)
    min_exp = np.min(uexptimes)
    max_exp = np.max(uexptimes)
    # get the shortest allowed longest exposure time
    shortest_long = params['TOOLS.STATIC.SHORTEST_LONG_DARK_EXPTIME']
    # deal with the longest exposure being too short
    if max_exp < shortest_long:
        emsg = ('Max DARK exposure time found = {0} s. '
                'Must have EXPTIME >= {1} s')
        eargs = [max_exp, shortest_long]
        raise AperoCodedException(params, None, emsg.format(*eargs),
                                  targs=eargs)
    # deal with only one unique exposure time
    if uexptimes.size < 2:
        # print warning
        wmsg = ('Single DARK exposure time found. Using fall back method to '
                'calculate intercept and setting slope=0')
        WLOG(params, 'warning', wmsg, sublevel=2)
        # intercept is the median of the cube
        intercept = mp.nanmedian(cube_amps, axis=0)
        # slope is zero
        slope = np.zeros_like(intercept)
        # set the combine mode
        combine_mode = 'INT[MED] SLOPE[0]'
    # check that there is at least a factor of 2 between min and max
    #    unique exposure times
    elif max_exp / min_exp < 2:
        emsg = ('Multiple DARK exposure times given but they do not differ '
                'by at least a factor of two:\n\tmin={0} s\n\tmax={1} s')
        eargs = [min_exp, max_exp]
        raise AperoCodedException(params, None, emsg.format(*eargs),
                                  targs=eargs)
    else:
        # For each pixel in the amplifier-folded image, fit a line
        #    (dark current vs. exposure time)
        for x_it in range(size[1] // n_amp):
            # print progress
            msg = '\tFitting dark frames Amplifier pixel {0}/{1}'
            margs = [x_it + 1, size[1] // n_amp]
            WLOG(params, '', msg.format(*margs))
            # loop around all y-pixels
            for y_it in range(size[0]):
                # linear fit exposure times vs the amplitudes
                coeffs = np.polyfit(exptimes, cube_amps[:, y_it, x_it], 1)
                # push into the offset (bias)
                intercept[y_it, x_it] = coeffs[1]
                # push into the slop (dark current rate)
                slope[y_it, x_it] = coeffs[0]
        # set the combine mode
        combine_mode = 'FIT[EXPTIME]'
    # -------------------------------------------------------------------------
    # convert cube_dict to astropy table
    flat_table = Table([dark_files, exptimes, mjdtimes],
                       names=['FILENAME', 'EXPTIME', 'MJD'])
    # make header dictionary
    hdr_kwargs = dict(KW_STATIC_DARKCURR_CMODE=combine_mode)
    # -------------------------------------------------------------------------
    # write static flat
    drs_static.save_static_file(params, recipe, det_path, 'STATIC_DARK_CURR',
                                desc='dark current slope and intercept',
                                data_list=[slope, intercept, flat_table],
                                datatype_list=['image', 'image', 'table'],
                                name_list=['slope', 'intercept',
                                           'static_flat_table'],
                                hdr_kwargs=hdr_kwargs)
    # -------------------------------------------------------------------------
    # Reconstruct amplifier dark current map for the
    recon_amp = intercept + slope * dhdr0[params['KW_EXPTIME'][0]]
    # # Prepare full-size reconstructed dark map
    # recon_map = np.zeros_like(dark0)
    # # loop around amplifiers and fill in the recon map
    # for amp in range(n_amp):
    #     # even amplifiers: no flip
    #     if amp % 2 == 0:
    #         flip = 1
    #     else:
    #         flip = -1
    #     # fill in the amplifier region with the reconstructed amp map
    #     start = amp * size[1] // n_amp
    #     end = (amp + 1) * (size[1] // n_amp)
    #     recon_map[:, start:end] = recon_amp[:, ::flip]
    # return the recon amplifier drak current map
    return recon_amp, dark0


def create_hotpix_map(params: ParamDict, recipe, det_path: str,
                      dark0: np.ndarray, flat: np.ndarray,
                      dark_threshold: float):
    """
    Create hotpix map

    :param params: Parameter dictionary of constants
    :param recipe: Recipe object
    :param det_path: str, directory to save files to
    :param dark_files: List of dark image files

    :return np.ndarray - median dark image
    """
    # Identify hot pixels: those with dark current above threshold and
    #    not NaN in the flat
    hot_pixels = np.where((dark0 > dark_threshold) & (np.isnan(flat) == False))

    # get the y and x pixel positions of the hot_pixels
    ypix, xpix = hot_pixels

    # compute robust standard deviation of the dark frames
    p16, p84 = mp.nanpercentile(dark0, [16, 84])
    sigma = (p84 - p16) / 2

    # Normalize hot pixel values by standard deviation
    nsig = dark0[hot_pixels] / sigma

    # Create table of hot pixel coordinates
    hotpix = Table([nsig, xpix, ypix], names=['nsig', 'xpix', 'ypix'])
    # -------------------------------------------------------------------------
    # write static flat
    drs_static.save_static_file(params, recipe, det_path, 'STATIC_HOTPIX',
                                desc='hotpix',
                                data_list=[hotpix],
                                datatype_list=['table'],
                                name_list=['hotpix'])



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
