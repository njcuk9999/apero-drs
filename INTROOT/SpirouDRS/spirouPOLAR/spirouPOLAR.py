#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou polarimetry module

Created on 2018-06-12 at 9:31

@author: E. Martioli

"""
from __future__ import division
import numpy as np
import os
from scipy.interpolate import UnivariateSpline
from scipy import stats

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage


# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouPOLAR.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# -----------------------------------------------------------------------------
# Get Logging function
WLOG = spirouCore.wlog
# get the default log_opt
DPROG = spirouConfig.Constants.DEFAULT_LOG_OPT()
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# get the config error
ConfigError = spirouConfig.ConfigError
# Get plotting functions
sPlt = spirouCore.sPlt


# =============================================================================
# Define user functions
# =============================================================================
def sort_polar_files(p, polardict):
    func_name = __NAME__ + '.sort_polar_files()'
    # get constants from p
    rdir = p['REDUCED_DIR']
    # set default properties
    stokes, exposure, expstatus = 'UNDEF', 0, False
    # loop over all input files
    for filename in p['ARG_FILE_NAMES']:
        # get full path of input file
        filepath = os.path.join(rdir, filename)
        # ------------------------------------------------------------------
        # Check that we can process file
        # check if file exists
        if not os.path.exists(filepath):
            wmsg = 'File {0} does not exist... skipping'
            WLOG('warning', p['LOG_OPT'], wmsg.format(filepath))
            continue
        # ------------------------------------------------------------------
        # Read E2DS input file
        data, hdr, cdr, nx, ny = spirouImage.ReadImage(p, filepath)
        # ------------------------------------------------------------------
        # get base file name
        basename = os.path.basename(filename)
        # ------------------------------------------------------------------
        # try to get polarisation header key
        if p['KW_CMMTSEQ'][0] in hdr:
            cmmtseq = hdr[p['KW_CMMTSEQ'][0]].split(" ")
            stokes, exposure = cmmtseq[0], int(cmmtseq[2][0])
            expstatus = True
        else:
            wmsg = 'File {0} has empty key="{1}", setting Stokes={2}'
            wargs = [filename, stokes]
            # Question: stokes here will be set to the last file value?
            WLOG('warning', p['LOG_OPT'], wmsg.format(*wargs))
        # ------------------------------------------------------------------
        # deal with fiber type
        fout = deal_with_fiber(p, filename, expstatus, exposure)
        fiber, expstatus, exposure, skip = fout
        # deal with skip
        if skip:
            continue
        # ------------------------------------------------------------------
        # Question: Why add some basename and skip some stokes/fiber/data etc
        # store data for this file
        polardict[filename] = dict()
        # set source
        polardict.set_source(filename, func_name)
        # add filename
        polardict[filename]["basename"] = basename
        # store header
        polardict[filename]["hdr"] = hdr
        # store header comments
        polardict[filename]["cdr"] = cdr
        # store exposure number
        polardict[filename]["exposure"] = exposure
        # store stokes parameter
        polardict[filename]["stokes"] = stokes
        # store fiber type
        polardict[filename]["fiber"] = fiber
        # store data
        polardict[filename]["data"] = data
        # set source of polar dict filename
        polardict.set_source(filename, func_name)
        # ------------------------------------------------------------------
        # log file addition
        wmsg = 'File {0}: fiber={1} Stokes={2} exposure={3}'
        wargs = [filename, fiber, stokes, str(exposure)]
        WLOG('info', p['LOG_OPT'], wmsg.format(*wargs))

    # return polarDict
    return polardict


def load_data(p, polardict, loc):
    func_name = __NAME__ + '.load_data()'
    # get constants from p
    stokesparams = p['IC_POLAR_STOKES_PARAMS']
    polarfibers = p['IC_POLAR_FIBERS']

    # First identify which stokes parameter is used in the input data
    stokes_detected = []
    # loop around filenames in polardict
    for filename in polardict.keys():
        # get this entry
        entry = polardict[filename]
        # condition 1: stokes parameter in defined parameters
        cond1 = entry['stokes'] in stokesparams
        # condition 2: stokes parameter not already detected
        cond2 = entry['stokes'] not in stokes_detected
        # if cond1 and cond2 append to detected list
        if cond1 and cond2:
            stokes_detected.append(entry['stokes'])
    # if more than one stokes parameter is identified then exit program
    if len(stokes_detected) > 1:
        wmsg = ('Identified more than one stokes parameter in the input '
                'data... exiting')
        WLOG('error', p['LOG_OPT'], wmsg)

    # set all possible combinations of fiber type and exposure number
    two_exposure_set, four_exposure_set = [], []
    for fiber in polarfibers:
        for exposure in range(1, 5):
            keystr = '{0}_{1}'.format(fiber, exposure)
            if exposure < 3:
                two_exposure_set.append(keystr)
            four_exposure_set.append(keystr)

    # detect all input combinations of fiber type and exposure number
    four_exposures_detected, two_exposures_detected = [], []
    loc['DATA'] = dict()
    # set the source of data (for param dict)
    loc.set_source('DATA', func_name)
    # loop around the filenames in polardict
    for filename in polardict.keys():
        # get this entry
        entry = polardict[filename]
        # get fiber type
        fiber = entry['fiber']
        # get exposure value
        exposure = entry['exposure']
        # constrcut key string
        keystr = '{0}_{1}'.format(fiber, exposure)
        # save the basename for 1st exposure to loc
        # if exposure is 1 and fiber is A
        if (exposure == 1) and (fiber == 'A'):
            loc['BASENAME'] = entry['basename']
            loc['HDR'] = entry['hdr']
            loc['CDR'] = entry['cdr']
            p['FIBER'] = 'A'
            # set sources
            # Question: we need the fiber for the wavelength solution
            # Question: We should be using A?
            p.set_source('FIBER', func_name)
            loc.set_sources(['BASENAME', 'HDR', 'CDR'], func_name)
        # get the data from entry
        data = entry['data']
        # set the zeros to ones (in data)
        zeros = data == 0.0
        data1 = np.where(zeros, np.ones_like(data), data)
        # save the data to loc
        loc['data'][keystr] = data1
        # add to four exposure set if correct type
        cond1 = keystr in four_exposure_set
        cond2 = keystr not in four_exposures_detected
        if cond1 and cond2:
            four_exposures_detected.append(keystr)
        # add to two exposure set if correct type
        cond1 = keystr in two_exposure_set
        cond2 = keystr not in two_exposures_detected
        if cond1 and cond2:
            two_exposures_detected.append(keystr)

    # initialize number of exposures to zero
    n_exposures = 0
    # now find out whether there is enough exposures
    # first test the 4-exposure set
    if len(four_exposures_detected) == 8:
        n_exposures = 4
    # else if the 4-exposures test fails then try 2-exposures set
    elif len(two_exposures_detected) == 4:
        n_exposures = 2
        wmsg = ('Detected only enough data for 2-exposures calculation'
                ', polarimetry is less precise than 4-exposures')
        WLOG('warning', p['LOG_OPT'], wmsg)
    # else we have insufficient data
    else:
        wmsg = ('Number of exposures in input data is not sufficient'
                ' for polarimetry calculations... exiting')
        WLOG('error', p['LOG_OPT'], wmsg)

    # set stokes parameters defined
    loc['STOKES'] = stokes_detected[0]
    # set the number of exposures detected
    loc['NEXPOSURES'] = n_exposures
    # set sources
    loc.set_sources(['STOKES', 'NEXPOSURES'], func_name)
    # return loc
    return p, loc


def calculate_polarimetry_wrapper(p, loc):

    # get parameters from p
    method = p['IC_POLAR_METHOD']
    # decide which method to use
    if method == 'Difference':
        return polarimetry_diff_method(p, loc)
    elif method == 'Ratio':
        return polarimetry_ratio_method(p, loc)
    else:
        emsg = 'Method="{0}" not valid for polarimetry calculation'
        WLOG('error', p['LOG_OPT'], emsg.format(method))
        return 1


def calculate_continuum(p, loc, in_wavelength=True):
    func_name = __NAME__ + '.calculate_continuum()'
    # get constants from p
    pol_binsize = p['IC_POLAR_CONT_BINSIZE']
    pol_overlap = p['IC_POLAR_CONT_OVERLAP']
    # get wavelength data if require
    if in_wavelength:
        wldata = loc['WAVE']
    else:
        wldata = np.ones_like(loc['POL'])
    # get the shape of pol
    ydim, xdim = loc['POL'].shape
    # ---------------------------------------------------------------------
    # flatten data (across orders)
    wl, pol, null1, null2 = [], [], [], []
    # loop around order data
    for order_num in range(ydim):
        if in_wavelength:
            wl = np.append(wl, wldata[order_num])
        else:
            wl = np.append(wl, (order_num * xdim) + np.arange(xdim))
        pol = np.append(pol, 100 * loc['POL'][order_num])
        null1 = np.append(null1, loc['NULL1'][order_num])
        null2 = np.append(null2, loc['NULL2'][order_num])
    # ---------------------------------------------------------------------
    # sort by wavelength (or pixel number)
    sortmask = np.argsort(wl)
    wl = wl[sortmask]
    pol = pol[sortmask]
    null1 = null1[sortmask]
    null2 = null2[sortmask]
    # save back to loc
    loc['FLAT_X'] = wl
    loc['FLAT_POL'] = pol
    loc['FLAT_NULL1'] = null1
    loc['FLAT_NULL2'] = null2
    # update source
    sources = ['FLAT_X', 'FLAT_POL', 'FLAT_NULL1', 'FLAT_NULL2']
    loc.set_sources(sources, func_name)
    # ---------------------------------------------------------------------
    # calculate continuum polarization
    contpol, xbin, ybin = continuum(wl, pol, binsize=pol_binsize,
                                    overlap=pol_overlap)
    # ---------------------------------------------------------------------
    # save continuum data to loc
    loc['CONT_POL'] = contpol
    loc['CONT_XBIN'] = xbin
    loc['CONT_YBIN'] = ybin
    # set source
    loc.set_sources(['CONT_POL', 'CONT_XBIN', 'CONT_YBIN'], func_name)
    # return loc
    return loc


# =============================================================================
# Define worker functions
# =============================================================================
def deal_with_fiber(p, filename, expstatus, exposure):
    # get base filename
    basefilename = os.path.basename(filename)
    # if fiber A
    if 'A.fits' in basefilename:
        fiber = 'A'
        # Question why for A and not B???
        if not expstatus:
            if exposure > 4:
                exposure = 1
        # set skip
        skip = False
    elif 'B.fits' in basefilename:
        fiber = 'B'
        # set skip
        skip = False
    elif 'AB.fits' in basefilename:
        fiber = 'AB'
        # set skip
        skip = True
        # log warning
        wmsg = 'File {0} corresponds to fiber "AB"... skipping'
        WLOG('warning', p['LOG_OPT'], wmsg.format(filename))
    elif 'C.fits' in basefilename:
        fiber = 'C'
        # set skip
        skip = True
        # log warning
        wmsg = 'File {0} corresponds to fiber "C"... skipping'
        WLOG('warning', p['LOG_OPT'], wmsg.format(filename))
    else:
        # set skip
        skip = True
        # log warning
        wmsg = 'File {0} does not match any fiber... skipping'
        WLOG('warning', p['LOG_OPT'], wmsg.format(filename))
        fiber = None

    # return fiber, expstatus, exposure and skip
    return fiber, expstatus, exposure, skip


def polarimetry_diff_method(p, loc):
    func_name = __NAME__ + '.polarimetry_diff_method()'
    name = 'polarimetryDiffMethod'
    # log start of polarimetry calculations
    wmsg = 'Running function {0} to calculate polarization'
    WLOG('info', p['LOG_OPT'], wmsg.format(name))
    # get parameters from loc
    data = loc['DATA']
    nexp = float(loc['NEXPOSURES'])
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store polarimetry variables in loc
    data_shape = loc['DATA']['A_1'].shape
    # initialize arrays to zeroes
    loc['POL'] = np.zeros(data_shape)
    loc['NULL1'] = np.zeros(data_shape)
    loc['NULL2'] = np.zeros(data_shape)
    # set source
    loc.set_sources(['POL', 'NULL1', 'NULL2'], func_name)
    # ---------------------------------------------------------------------
    # STEP 1 - calculate the quantity Gn (Eq #12-14 on page 997 of
    #          Bagnulo et al. 2009), n being the pair of exposures
    # ---------------------------------------------------------------------
    swapbeams = False
    G = []
    for i in range(1, int(nexp) + 1):
        if swapbeams:
            if i == 1 or i == 3:
                # add B part
                part1 = (data['B_{0}'.format(i)] - data['B_{0}'.format(i + 1)])
                part2 = (data['B_{0}'.format(i)] + data['B_{0}'.format(i + 1)])
                G.append(part1 / part2)
            elif i == 2 or i == 4:
                # add A part
                part1 = (data['A_{0}'.format(i - 1)] - data['A_{0}'.format(i)])
                part2 = (data['A_{0}'.format(i - 1)] + data['A_{0}'.format(i)])
                G.append(part1 / part2)
        else:
            part1 = data['B_{0}'.format(i)] - data['A_{0}'.format(i)]
            part2 = data['B_{0}'.format(i)] + data['A_{0}'.format(i)]
            G.append(part1 / part2)

    # if we have 4 exposures
    if nexp == 4:
        # -----------------------------------------------------------------
        # STEP 2 - calculate the quantity Dm (Eq #18 on page 997 of
        #          Bagnulo et al. 2009 paper) and the quantity Dms with
        #          exposure 2 and 4 swapped, m being the pair of exposures
        # -----------------------------------------------------------------
        D1, D2 = G[0] - G[1], G[2] - G[3]
        D1s, D2s = G[0] - G[3], G[2] - G[1]
        # -----------------------------------------------------------------
        # STEP 3 - calculate the degree of polarization for Stokes
        #          parameter (Eq #19 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['POL'] = (D1 + D2) / nexp
        # -----------------------------------------------------------------
        # STEP 4 - calculate the first NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['NULL1'] = (D1 - D2) / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the second NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        loc['NULL2'] = (D1s - D2s) / nexp
    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 2 - calculate the quantity Dm
        #          (Eq #18 on page 997 of Bagnulo et al. 2009) and
        #          the quantity Dms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        D1 = G[0] - G[1]
        # -----------------------------------------------------------------
        # STEP 3 - calculate the degree of polarization
        #          (Eq #19 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['POL'] = D1 / nexp
    # else we have insufficient data (should not get here)
    else:
        wmsg = ('Number of exposures in input data is not sufficient'
                ' for polarimetry calculations... exiting')
        WLOG('error', p['LOG_OPT'], wmsg)

    # set the method
    loc['METHOD'] = 'Difference'
    loc.set_source('METHOD', func_name)
    # log end of polarimetry calculations
    wmsg = 'Routine {0} run successfully'
    WLOG('info', p['LOG_OPT'], wmsg.format(name))
    # return loc
    return loc


def polarimetry_ratio_method(p, loc):
    func_name = __NAME__ + '.polarimetry_ratio_method()'
    name = 'polarimetryRatioMethod'

    # log start of polarimetry calculations
    wmsg = 'Running function {0} to calculate polarization'
    WLOG('info', p['LOG_OPT'], wmsg.format(name))
    # get parameters from loc
    data = loc['DATA']
    nexp = float(loc['NEXPOSURES'])
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store polarimetry variables in loc
    data_shape = loc['DATA']['A_1'].shape
    # initialize arrays to zeroes
    loc['POL'] = np.zeros(data_shape)
    loc['NULL1'] = np.zeros(data_shape)
    loc['NULL2'] = np.zeros(data_shape)
    # set source
    loc.set_sources(['POL', 'NULL1', 'NULL2'], func_name)

    # ---------------------------------------------------------------------
    # STEP 1 - calculate ratio of beams for each exposure
    #          (Eq #12 on page 997 of Bagnulo et al. 2009 )
    # ---------------------------------------------------------------------
    flux_ratio = []
    for i in range(1, int(nexp) + 1):
        part1 = data['B_{0}'.format(i)]
        part2 = data['A_{0}'.format(i)]
        flux_ratio.append(part1 / part2)
    # if we have 4 exposures
    if nexp == 4:
        # -----------------------------------------------------------------
        # STEP 2 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        R1, R2 = flux_ratio[0] / flux_ratio[1], flux_ratio[2] / flux_ratio[3]
        R1s, R2s = flux_ratio[0] / flux_ratio[3], flux_ratio[2] / flux_ratio[1]
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        R = (R1 * R2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 4 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['POL'] = (R - 1.0) / (R + 1.0)
        # -----------------------------------------------------------------
        # STEP 5 - calculate the quantity RN1
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        RN1 = (R1 / R2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the first NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['NULL1'] = (RN1 - 1.0) / (RN1 + 1.0)
        # -----------------------------------------------------------------
        # STEP 7 - calculate the quantity RN2
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        RN2 = (R1s / R2s) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 8 - calculate the second NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        loc['NULL2'] = (RN2 - 1.0) / (RN2 + 1.0)

    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 2 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        R1 = flux_ratio[0] / flux_ratio[1]

        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        R = R1 ** (1.0 / nexp)

        # -----------------------------------------------------------------
        # STEP 4 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['POL'] = (R - 1.0) / (R + 1.0)

    # else we have insufficient data (should not get here)
    else:
        wmsg = ('Number of exposures in input data is not sufficient'
                ' for polarimetry calculations... exiting')
        WLOG('error', p['LOG_OPT'], wmsg)

    # set the method
    loc['METHOD'] = 'Ratio'
    loc.set_source('METHOD', func_name)
    # log end of polarimetry calculations
    wmsg = 'Routine {0} run successfully'
    WLOG('info', p['LOG_OPT'], wmsg.format(name))
    # return loc
    return loc


def continuum(x, y, binsize=200, overlap=100, sigmaclip=3.0, window=3,
              mode="median", use_linear_fit=False):
    """
    Function to calculate continuum
    :param x,y input data arrays (must be of the same size)
    :param binsize number of points in each bin
    :param overlap number of points to overlap with adjacent bins
    :param sigmaclip number of times sigma to cut-off points
    :param window number of bins to use in local fit
    :param mode string to set which combine mode.
           mode accepts: "median", "mean", "max"
    :param use_linear_fit: bool, whether to use the linar fit

    :return continuum, xbin, ybin
        continuum: array of the same size as input arrays containing the
                   continuum data already interpolated to the same points
                   as input data.
        xbin,ybin: arrays containing the bins used to interpolate data for
        obtaining the continuum
    """

    # set number of bins given the input array length and the bin size
    nbins = int(np.floor(len(x) / binsize))

    # initialize arrays to store binned data
    xbin, ybin = [], []

    for i in range(nbins):
        # get first and last index within the bin
        idx0 = i * binsize - overlap
        idxf = (i + 1) * binsize + overlap
        # if it reaches the edges then it reset the indexes
        if idx0 < 0:
            idx0 = 0
        if idxf > len(x):
            idxf = len(x) - 1
        # get data within the bin
        xtmp = x[idx0:idxf]
        ytmp = y[idx0:idxf]
        # calculate mean x within the bin
        xmean = np.mean(xtmp)
        # calculate median y within the bin
        medy = np.median(ytmp)

        if medy and not np.isnan(medy):
            # calculate median deviation
            medydev = np.median(np.absolute(ytmp - medy))
            # create mask to filter data outside n*sigma range
            filtermask = (ytmp > medy) & (ytmp < medy + sigmaclip * medydev)
            # save mean x wihthin bin
            xbin.append(xmean)
            if len(ytmp[filtermask]) > 2:
                if mode == 'max':
                    # save maximum y of filtered data
                    ybin.append(np.max(ytmp[filtermask]))
                elif mode == 'median':
                    # save median y of filtered data
                    ybin.append(np.median(ytmp[filtermask]))
                elif mode == 'mean':
                    # save mean y of filtered data
                    ybin.append(np.mean(ytmp[filtermask]))
                else:
                    emsg = 'Can not recognize selected mode="{0}"...exiting'
                    WLOG('error', DPROG, emsg.format(mode))
            else:
                continue

    # Option to use a linearfit within a given window
    if use_linear_fit:
        # initialize arrays to store new bin data
        newxbin, newybin = [], []
        # append first point to avoid crazy behaviours in the edge
        newxbin.append(x[0])
        newybin.append(ybin[0])

        # loop around bins to obtain a linear fit within a given window size
        for i in range(len(xbin)):
            # set first and last index to select bins within window
            idx0 = i - window
            idxf = i + 1 + window
            # make sure it doesnt go over the edges
            if idx0 < 0: idx0 = 0
            if idxf > nbins: idxf = nbins - 1

            # perform linear fit to these data
            slope, intercept, r_value, p_value, std_err = \
                stats.linregress(xbin[idx0:idxf], ybin[idx0:idxf])

            # save data obtained from the fit
            newxbin.append(xbin[i])
            newybin.append(intercept + slope * xbin[i])

        xbin, ybin = newxbin, newybin

    # interpolate points applying an Spline to the bin data
    sfit = UnivariateSpline(xbin, ybin, s=1)

    # Resample interpolation to the original grid
    continuum = sfit(x)
    # return continuum and x and y bins
    return continuum, xbin, ybin


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
