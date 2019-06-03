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
from collections import OrderedDict

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
# Get the parameter dictionary class
ParamDict = spirouConfig.ParamDict
# get the config error
ConfigError = spirouConfig.ConfigError


# =============================================================================
# Define user functions
# =============================================================================
def sort_polar_files(p, polardict):
    """
    Function to sort input data for polarimetry.
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            REDUCED_DIR: string, directory path where reduced data are stored
            ARG_FILE_NAMES: list, list of input filenames
            KW_CMMTSEQ: string, FITS keyword where to find polarimetry
                        information

    :param polardict: dictionary, ParamDict containing information on the
                      input data

    :return polardict: dictionary, ParamDict containing information on the
                       input data
                       adds an entry for each filename, each entry is a
                       dictionary containing:
                       - basename, hdr, cdr, exposure, stokes, fiber, data
                       for each file
    """

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
            WLOG(p, 'warning', wmsg.format(filepath))
            continue
        # ------------------------------------------------------------------
        # Read E2DS input file
        data, hdr, cdr, nx, ny = spirouImage.ReadImage(p, filepath)
        # ------------------------------------------------------------------
        # get base file name
        basename = os.path.basename(filename)
        # ------------------------------------------------------------------
        # try to get polarisation header key
        if p['KW_CMMTSEQ'][0] in hdr and hdr[p['KW_CMMTSEQ'][0]] != "":
            cmmtseq = hdr[p['KW_CMMTSEQ'][0]].split(" ")
            stokes, exposure = cmmtseq[0], int(cmmtseq[2][0])
            expstatus = True
        else:
            wmsg = 'File {0} has empty key="{1}", setting Stokes={2}'
            wargs = [filename, p['KW_CMMTSEQ'][0], stokes]

            # Question: stokes here will be set to the last file value?
            WLOG(p, 'warning', wmsg.format(*wargs))
            expstatus = False
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
        polardict[filename] = OrderedDict()
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
        WLOG(p, 'info', wmsg.format(*wargs))

    # return polarDict
    return polardict


def load_data(p, polardict, loc):
    """
    Function to load input E2DS data for polarimetry.
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            IC_POLAR_STOKES_PARAMS: list, list of stokes parameters
            IC_POLAR_FIBERS: list, list of fiber types used in polarimetry
    
    :param polardict: dictionary, ParamDict containing information on the
                      input data
        
    :param loc: parameter dictionary, ParamDict to store data
        
    :return p, loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
            FIBER: saves reference fiber used for base file in polar sequence
                   The updated data dictionary adds/updates the following:
            DATA: array of numpy arrays (2D), E2DS data from all fibers in
                  all input exposures.
            BASENAME, string, basename for base FITS file
            HDR: dictionary, header from base FITS file
            CDR: dictionary, header comments from base FITS file
            STOKES: string, stokes parameter detected in sequence
            NEXPOSURES: int, number of exposures in polar sequence
    """

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
        # condition 1: stokes parameter undefined
        cond1 = entry['stokes'].upper() == 'UNDEF'
        # condition 2: stokes parameter in defined parameters
        cond2 = entry['stokes'].upper() in stokesparams
        # condition 3: stokes parameter not already detected
        cond3 = entry['stokes'].upper() not in stokes_detected
        # if (cond1 or cond2) and cond3 append to detected list
        if (cond1 or cond2) and cond3:
            stokes_detected.append(entry['stokes'].upper())
    # if more than one stokes parameter is identified then exit program
    if len(stokes_detected) == 0:
        stokes_detected.append('UNDEF')
    elif len(stokes_detected) > 1:
        wmsg = ('Identified more than one stokes parameter in the input '
                'data... exiting')
        WLOG(p, 'error', wmsg)

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
    loc['DATA'] = OrderedDict()
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
        WLOG(p, 'warning', wmsg)
    # else we have insufficient data
    else:
        wmsg = ('Number of exposures in input data is not sufficient'
                ' for polarimetry calculations... exiting')
        WLOG(p, 'error', wmsg)

    # set stokes parameters defined
    loc['STOKES'] = stokes_detected[0]
    # set the number of exposures detected
    loc['NEXPOSURES'] = n_exposures
    # set sources
    loc.set_sources(['STOKES', 'NEXPOSURES'], func_name)
    # return loc
    return p, loc


def calculate_polarimetry_wrapper(p, loc):
    """
    Function to call functions to calculate polarimetry either using
    the Ratio or Difference methods.
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            IC_POLAR_METHOD: string, to define polar method "Ratio" or
                             "Difference"

    :param loc: parameter dictionary, ParamDict containing data
        
    :return polarfunc: function, either polarimetry_diff_method(p, loc)
                       or polarimetry_ratio_method(p, loc)
    """

    # get parameters from p
    method = p['IC_POLAR_METHOD']
    # decide which method to use
    if method == 'Difference':
        return polarimetry_diff_method(p, loc)
    elif method == 'Ratio':
        return polarimetry_ratio_method(p, loc)
    else:
        emsg = 'Method="{0}" not valid for polarimetry calculation'
        WLOG(p, 'error', emsg.format(method))
        return 1


def calculate_continuum(p, loc, in_wavelength=True):
    """
    Function to calculate the continuum polarization
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            IC_POLAR_CONT_BINSIZE: int, number of points in each sample bin
            IC_POLAR_CONT_OVERLAP: int, number of points to overlap before and
                                   after each sample bin
            IC_POLAR_CONT_TELLMASK: list of float pairs, list of telluric bands,
                                    i.e, a list of wavelength ranges ([wl0,wlf])
                                    for telluric absorption
        
    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            WAVE: numpy array (2D), e2ds wavelength data
            POL: numpy array (2D), e2ds degree of polarization data
            POLERR: numpy array (2D), e2ds errors of degree of polarization
            NULL1: numpy array (2D), e2ds 1st null polarization
            NULL2: numpy array (2D), e2ds 2nd null polarization
            STOKESI: numpy array (2D), e2ds Stokes I data
            STOKESIERR: numpy array (2D), e2ds errors of Stokes I
        
    :param in_wavelength: bool, to indicate whether or not there is wave cal

    :return loc: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            FLAT_X: numpy array (1D), flatten polarimetric x data
            FLAT_POL: numpy array (1D), flatten polarimetric pol data
            FLAT_POLERR: numpy array (1D), flatten polarimetric pol error data
            FLAT_STOKESI: numpy array (1D), flatten polarimetric stokes I data
            FLAT_STOKESIERR: numpy array (1D), flatten polarimetric stokes I
                             error data
            FLAT_NULL1: numpy array (1D), flatten polarimetric null1 data
            FLAT_NULL2: numpy array (1D), flatten polarimetric null2 data
            CONT_POL: numpy array (1D), e2ds continuum polarization data
                      interpolated from xbin, ybin points, same shape as
                      FLAT_POL
            CONT_XBIN: numpy array (1D), continuum in x polarization samples
            CONT_YBIN: numpy array (1D), continuum in y polarization samples
    """

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
    wl, pol, polerr, stokes_i, stokes_ierr = [], [], [], [], []
    null1, null2 = [], []
    # loop around order data
    for order_num in range(ydim):
        if in_wavelength:
            wl = np.append(wl, wldata[order_num])
        else:
            wl = np.append(wl, (order_num * xdim) + np.arange(xdim))
        pol = np.append(pol, loc['POL'][order_num])
        polerr = np.append(polerr, loc['POLERR'][order_num])
        stokes_i = np.append(stokes_i, loc['STOKESI'][order_num])
        stokes_ierr = np.append(stokes_ierr, loc['STOKESIERR'][order_num])
        null1 = np.append(null1, loc['NULL1'][order_num])
        null2 = np.append(null2, loc['NULL2'][order_num])
    # ---------------------------------------------------------------------
    # sort by wavelength (or pixel number)
    sortmask = np.argsort(wl)

    # save back to loc
    loc['FLAT_X'] = wl[sortmask]
    loc['FLAT_POL'] = pol[sortmask]
    loc['FLAT_POLERR'] = polerr[sortmask]
    loc['FLAT_STOKESI'] = stokes_i[sortmask]
    loc['FLAT_STOKESIERR'] = stokes_ierr[sortmask]
    loc['FLAT_NULL1'] = null1[sortmask]
    loc['FLAT_NULL2'] = null2[sortmask]
    # update source
    sources = ['FLAT_X', 'FLAT_POL', 'FLAT_POLERR', 'FLAT_STOKESI',
               'FLAT_STOKESIERR', 'FLAT_NULL1', 'FLAT_NULL2']
    loc.set_sources(sources, func_name)

    # ---------------------------------------------------------------------
    # calculate continuum polarization
    contpol, xbin, ybin = spirouCore.Continuum(loc['FLAT_X'], loc['FLAT_POL'],
                                               binsize=pol_binsize,
                                               overlap=pol_overlap,
                                               excl_bands=p[
                                                   'IC_POLAR_CONT_TELLMASK'])
    # ---------------------------------------------------------------------
    # save continuum data to loc
    loc['CONT_POL'] = contpol
    loc['CONT_XBIN'] = xbin
    loc['CONT_YBIN'] = ybin
    # set source
    loc.set_sources(['CONT_POL', 'CONT_XBIN', 'CONT_YBIN'], func_name)
    # return loc
    return loc


def calculate_stokes_i(p, loc):
    """
    Function to calculate the Stokes I polarization

    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging

    :param loc: parameter dictionary, ParamDict containing data
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
    func_name = __NAME__ + '.calculate_stokes_I()'
    name = 'CalculateStokesI'
    # log start of Stokes I calculations
    wmsg = 'Running function {0} to calculate Stokes I total flux'
    WLOG(p, 'info', wmsg.format(name))
    # get parameters from loc
    data = loc['DATA']
    nexp = float(loc['NEXPOSURES'])
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    # store Stokes I variables in loc
    data_shape = loc['DATA']['A_1'].shape
    # initialize arrays to zeroes
    loc['STOKESI'] = np.zeros(data_shape)
    loc['STOKESIERR'] = np.zeros(data_shape)
    # set source
    loc.set_sources(['STOKESI', 'STOKESIERR'], func_name)

    flux, var = [], []
    for i in range(1, int(nexp) + 1):
        # Calculate sum of fluxes from fibers A and B
        flux_ab = data['A_{0}'.format(i)] + data['B_{0}'.format(i)]
        # Save A+B flux for each exposure
        flux.append(flux_ab)

        # Calculate the variances for fiber A+B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension in the e2ds files.
        var_ab = data['A_{0}'.format(i)] + data['B_{0}'.format(i)]
        # Save varAB = sigA^2 + sigB^2, ignoring cross-correlated terms
        var.append(var_ab)

    # Sum fluxes and variances from different exposures
    for i in range(len(flux)):
        loc['STOKESI'] += flux[i]
        loc['STOKESIERR'] += var[i]

    # Calcualte errors -> sigma = sqrt(variance)
    loc['STOKESIERR'] = np.sqrt(loc['STOKESIERR'])

    # log end of Stokes I intensity calculations
    wmsg = 'Routine {0} run successfully'
    WLOG(p, 'info', wmsg.format(name))
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
            exposure += 1
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
        WLOG(p, 'warning', wmsg.format(filename))
    elif 'C.fits' in basefilename:
        fiber = 'C'
        # set skip
        skip = True
        # log warning
        wmsg = 'File {0} corresponds to fiber "C"... skipping'
        WLOG(p, 'warning', wmsg.format(filename))
    else:
        # set skip
        skip = True
        # log warning
        wmsg = 'File {0} does not match any fiber... skipping'
        WLOG(p, 'warning', wmsg.format(filename))
        fiber = None

    # return fiber, expstatus, exposure and skip
    return fiber, expstatus, exposure, skip


def polarimetry_diff_method(p, loc):
    """
    Function to calculate polarimetry using the difference method as described
    in the paper:
        Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            p['LOG_OPT']: string, option for logging
        
    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            loc['DATA']: numpy array (2D) containing the e2ds flux data for all
            exposures {1,..,NEXPOSURES}, and for all fibers {A,B}
            loc['NEXPOSURES']: number of polarimetry exposures
        
    :return loc: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            loc['POL']: numpy array (2D), degree of polarization data, which
                        should be the same shape as E2DS files, i.e, 
                        loc[DATA][FIBER_EXP]
            loc['POLERR']: numpy array (2D), errors of degree of polarization,
                           same shape as loc['POL']
            loc['NULL1']: numpy array (2D), 1st null polarization, same 
                          shape as loc['POL']
            loc['NULL2']: numpy array (2D), 2nd null polarization, same 
                          shape as loc['POL']
    """

    func_name = __NAME__ + '.polarimetry_diff_method()'
    name = 'polarimetryDiffMethod'
    # log start of polarimetry calculations
    wmsg = 'Running function {0} to calculate polarization'
    WLOG(p, 'info', wmsg.format(name))
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
    loc['POLERR'] = np.zeros(data_shape)
    loc['NULL1'] = np.zeros(data_shape)
    loc['NULL2'] = np.zeros(data_shape)
    # set source
    loc.set_sources(['POL', 'POLERR', 'NULL1', 'NULL2'], func_name)

    gg, gvar = [], []
    for i in range(1, int(nexp) + 1):
        # ---------------------------------------------------------------------
        # STEP 1 - calculate the quantity Gn (Eq #12-14 on page 997 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        part1 = data['A_{0}'.format(i)] - data['B_{0}'.format(i)]
        part2 = data['A_{0}'.format(i)] + data['B_{0}'.format(i)]
        gg.append(part1 / part2)

        # Calculate the variances for fiber A and B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension of e2ds files.
        a_var = data['A_{0}'.format(i)]
        b_var = data['B_{0}'.format(i)]

        # ---------------------------------------------------------------------
        # STEP 2 - calculate the quantity g_n^2 (Eq #A4 on page 1013 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        nomin = 2.0 * data['A_{0}'.format(i)] * data['B_{0}'.format(i)]
        denom = (data['A_{0}'.format(i)] + data['B_{0}'.format(i)]) ** 2.0
        factor1 = (nomin / denom) ** 2.0
        a_var_part = a_var / (data['A_{0}'.format(i)] ** 2.0)
        b_var_part = b_var / (data['B_{0}'.format(i)] ** 2.0)
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
        loc['POL'] = (d1 + d2) / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the first NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['NULL1'] = (d1 - d2) / nexp
        # -----------------------------------------------------------------
        # STEP 6 - calculate the second NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        loc['NULL2'] = (d1s - d2s) / nexp
        # -----------------------------------------------------------------
        # STEP 7 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1] + gvar[2] + gvar[3]
        loc['POLERR'] = np.sqrt(sum_of_gvar / (nexp ** 2.0))

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
        loc['POL'] = d1 / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1]
        loc['POLERR'] = np.sqrt(sum_of_gvar / (nexp ** 2.0))

    # else we have insufficient data (should not get here)
    else:
        wmsg = ('Number of exposures in input data is not sufficient'
                ' for polarimetry calculations... exiting')
        WLOG(p, 'error', wmsg)

    # set the method
    loc['METHOD'] = 'Difference'
    loc.set_source('METHOD', func_name)
    # log end of polarimetry calculations
    wmsg = 'Routine {0} run successfully'
    WLOG(p, 'info', wmsg.format(name))
    # return loc
    return loc


def polarimetry_ratio_method(p, loc):
    """
    Function to calculate polarimetry using the ratio method as described
    in the paper:
        Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            p['LOG_OPT']: string, option for logging
        
    :param loc: parameter dictionary, ParamDict containing data
        Must contain at least:
            loc['DATA']: numpy array (2D) containing the e2ds flux data for all
                         exposures {1,..,NEXPOSURES}, and for all fibers {A,B}
            loc['NEXPOSURES']: number of polarimetry exposures
        
    :return loc: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            loc['POL']: numpy array (2D), degree of polarization data, which
                        should be the same shape as E2DS files, i.e, 
                        loc[DATA][FIBER_EXP]
            loc['POLERR']: numpy array (2D), errors of degree of polarization,
                           same shape as loc['POL']
            loc['NULL1']: numpy array (2D), 1st null polarization, same 
                          shape as loc['POL']
            loc['NULL2']: numpy array (2D), 2nd null polarization, same 
                          shape as loc['POL']
    """
    func_name = __NAME__ + '.polarimetry_ratio_method()'
    name = 'polarimetryRatioMethod'

    # log start of polarimetry calculations
    wmsg = 'Running function {0} to calculate polarization'
    WLOG(p, 'info', wmsg.format(name))
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
    loc['POLERR'] = np.zeros(data_shape)
    loc['NULL1'] = np.zeros(data_shape)
    loc['NULL2'] = np.zeros(data_shape)
    # set source
    loc.set_sources(['POL', 'NULL1', 'NULL2'], func_name)

    flux_ratio, var_term = [], []

    # Ignore numpy warnings to avoid warning message: "RuntimeWarning: invalid
    # value encountered in power ..."
    np.warnings.filterwarnings('ignore')

    for i in range(1, int(nexp) + 1):
        # ---------------------------------------------------------------------
        # STEP 1 - calculate ratio of beams for each exposure
        #          (Eq #12 on page 997 of Bagnulo et al. 2009 )
        # ---------------------------------------------------------------------
        part1 = data['A_{0}'.format(i)]
        part2 = data['B_{0}'.format(i)]
        flux_ratio.append(part1 / part2)

        # Calculate the variances for fiber A and B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension of e2ds files.
        a_var = data['A_{0}'.format(i)]
        b_var = data['B_{0}'.format(i)]

        # ---------------------------------------------------------------------
        # STEP 2 - calculate the error quantities for Eq #A10 on page 1014 of
        #          Bagnulo et al. 2009
        # ---------------------------------------------------------------------
        var_term_part1 = a_var / (data['A_{0}'.format(i)] ** 2.0)
        var_term_part2 = b_var / (data['B_{0}'.format(i)] ** 2.0)
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
        rr = (r1 * r2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['POL'] = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the quantity RN1
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        rn1 = (r1 / r2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 7 - calculate the first NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['NULL1'] = (rn1 - 1.0) / (rn1 + 1.0)
        # -----------------------------------------------------------------
        # STEP 8 - calculate the quantity RN2
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        rn2 = (r1s / r2s) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 9 - calculate the second NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        loc['NULL2'] = (rn2 - 1.0) / (rn2 + 1.0)
        # -----------------------------------------------------------------
        # STEP 10 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        numer_part1 = (r1 * r2) ** (1.0 / 2.0)
        denom_part1 = ((r1 * r2) ** (1.0 / 4.0) + 1.0) ** 4.0
        part1 = numer_part1 / (denom_part1 * 4.0)
        sumvar = var_term[0] + var_term[1] + var_term[2] + var_term[3]
        loc['POLERR'] = np.sqrt(part1 * sumvar)

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
        rr = r1 ** (1.0 / nexp)

        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        loc['POL'] = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        # numer_part1 = R1
        denom_part1 = ((r1 ** 0.5) + 1.0) ** 4.0
        part1 = r1 / denom_part1
        sumvar = var_term[0] + var_term[1]
        loc['POLERR'] = np.sqrt(part1 * sumvar)

    # else we have insufficient data (should not get here)
    else:
        wmsg = ('Number of exposures in input data is not sufficient'
                ' for polarimetry calculations... exiting')
        WLOG(p, 'error', wmsg)

    # set the method
    loc['METHOD'] = 'Ratio'
    loc.set_source('METHOD', func_name)
    # log end of polarimetry calculations
    wmsg = 'Routine {0} run successfully'
    WLOG(p, 'info', wmsg.format(name))
    # return loc
    return loc


def polar_products_header(p, loc, polardict, qc_params):
    """
        Function to construct header keywords to be saved in the polar products
        
        :param p: parameter dictionary, ParamDict containing constants
        
        :param loc: parameter dictionary, ParamDict containing data
        
        :param polardict: dictionary, ParamDict containing information on the
        input data

        :return hdict, loc: ParamDict, ParamDict: the header parameter
        dictionary and the updated loc parameter dictionary
        
    """
    
    # add keys from original header of base file
    hdict = spirouImage.CopyOriginalKeys(loc['HDR'], loc['CDR'])
    # add version number
    hdict = spirouImage.AddKey(p, hdict, p['KW_VERSION'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_DATE'], value=p['DRS_DATE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_DATE_NOW'], value=p['DATE_NOW'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_PID'], value=p['PID'])
    # add in file
    hdict = spirouImage.AddKey(p, hdict, p['KW_CDBWAVE'], value=loc['WAVEFILE'])
    hdict = spirouImage.AddKey(p, hdict, p['KW_WAVESOURCE'],
                               value=loc['WSOURCE'])
    hdict = spirouImage.AddKey1DList(p, hdict, p['KW_INFILE1'], dim1name='file',
                                     values=p['ARG_FILE_NAMES'])
    # add qc parameters
    hdict = spirouImage.AddKey(p, hdict, p['KW_DRS_QC'], value=p['QC'])
    hdict = spirouImage.AddQCKeys(p, hdict, qc_params)
    # add stokes parameter keyword to header
    hdict = spirouImage.AddKey(p, hdict, p['kw_POL_STOKES'],
                               value=loc['STOKES'])
    # add number of exposures parameter keyword to header
    hdict = spirouImage.AddKey(p, hdict, p['kw_POL_NEXP'],
                               value=loc['NEXPOSURES'])
    # add the polarimetry method parameter keyword to header
    hdict = spirouImage.AddKey(p, hdict, p['kw_POL_METHOD'],
                               value=loc['METHOD'])
    
    mjd_first, mjd_last = 0.0, 0.0
    meanbjd, tot_exptime = 0.0, 0.0
    bjd_first, bjd_last, exptime_last = 0.0, 0.0, 0.0
    berv_first, berv_last = 0.0, 0.0
    bervmaxs = []
    
    # loop over files in polar sequence to add keywords to header of products
    for filename in polardict.keys():
        # get this entry
        entry = polardict[filename]
        # get expnum, fiber, and header
        expnum, fiber, hdr = entry['exposure'], entry['fiber'], entry['hdr']
        # Add only times from fiber A
        if fiber == 'A':
            # calcualte total exposure time
            tot_exptime += float(hdr[p['KW_EXPTIME'][0]])
            # get values for BJDCEN calculation
            if expnum == 1:
                mjd_first = float(hdr[p['KW_ACQTIME'][0]])
                bjd_first = float(hdr[p['KW_BJD'][0]])
                berv_first = float(hdr[p['KW_BERV'][0]])
            elif expnum == loc['NEXPOSURES']:
                mjd_last = float(hdr[p['KW_ACQTIME'][0]])
                bjd_last = float(hdr[p['KW_BJD'][0]])
                berv_last = float(hdr[p['KW_BERV'][0]])
                exptime_last = float(hdr[p['KW_EXPTIME'][0]])
            meanbjd += float(hdr[p['KW_BJD'][0]])
            # add exposure file name
            fileexp = p['kw_POL_FILENAM{0}'.format(expnum)]
            hdict = spirouImage.AddKey(p, hdict, fileexp, value=hdr['FILENAME'])
            # add EXPTIME for each exposure
            exptimeexp = p['kw_POL_EXPTIME{0}'.format(expnum)]
            hdict = spirouImage.AddKey(p, hdict, exptimeexp,
                                       value=hdr[p['KW_EXPTIME'][0]])
            # add MJDATE for each exposure
            mjdexp = p['kw_POL_MJDATE{0}'.format(expnum)]
            hdict = spirouImage.AddKey(p, hdict, mjdexp,
                                       value=hdr[p['KW_ACQTIME'][0]])
            # add MJDEND for each exposure
            mjdendexp = p['kw_POL_MJDEND{0}'.format(expnum)]
            hdict = spirouImage.AddKey(p, hdict, mjdendexp,
                                       value=hdr[p['KW_MJDEND'][0]])
            # add BJD for each exposure
            bjdexp = p['kw_POL_BJD{0}'.format(expnum)]
            hdict = spirouImage.AddKey(p, hdict, bjdexp,
                                       value=hdr[p['KW_BJD'][0]])
            # add BERV for each exposure
            bervexp = p['kw_POL_BERV{0}'.format(expnum)]
            hdict = spirouImage.AddKey(p, hdict, bervexp,
                                       value=hdr[p['KW_BERV'][0]])
            # append BERVMAX value of each exposure
            bervmaxs.append(float(hdr[p['KW_BERV_MAX'][0]]))

    # add total exposure time parameter keyword to header
    hdict = spirouImage.AddKey(p, hdict, p['KW_POL_EXPTIME'], value=tot_exptime)
    # update existing EXPTIME keyword
    hdict = spirouImage.AddKey(p, hdict, p['KW_EXPTIME'], value=tot_exptime)

    # add elapsed time parameter keyword to header
    elapsed_time = (bjd_last - bjd_first) * 86400. + exptime_last
    hdict = spirouImage.AddKey(p, hdict, p['KW_POL_ELAPTIME'], value=elapsed_time)

    # calculate MJD at center of polarimetric sequence
    mjdcen = mjd_first + (mjd_last - mjd_first + exptime_last/86400.)/2.0
    # add central MJD
    hdict = spirouImage.AddKey(p, hdict, p['KW_POL_MJDCEN'], value=mjdcen)
    # update existing MJD keyword
    hdict = spirouImage.AddKey(p, hdict, p['KW_ACQTIME'], value=mjdcen)

    # calculate BJD at center of polarimetric sequence
    bjdcen = bjd_first + (bjd_last - bjd_first + exptime_last/86400.)/2.0
    # add central BJD
    hdict = spirouImage.AddKey(p, hdict, p['KW_POL_BJDCEN'], value=bjdcen)
    # update existing BJD keyword
    hdict = spirouImage.AddKey(p, hdict, p['KW_BJD'], value=bjdcen)

    # calculate BERV at center by linear interpolation
    berv_slope = (berv_last - berv_first) / (bjd_last - bjd_first)
    berv_intercept = berv_first - berv_slope * bjd_first
    loc['BERVCEN'] = berv_intercept + berv_slope * bjdcen
    
    # add central BERV
    hdict = spirouImage.AddKey(p, hdict, p['kw_POL_BERVCEN'], value=loc['BERVCEN'])
    # update existing BERV keyword
    hdict = spirouImage.AddKey(p, hdict, p['kw_BERV'], value=loc['BERVCEN'])
    
    # calculate maximum bervmax
    bervmax = np.max(bervmaxs)
    # update existing BERVMAX keyword
    hdict = spirouImage.AddKey(p, hdict, p['kw_BERV_MAX'], value=bervmax)

    # add mean BJD
    meanbjd = meanbjd / loc['NEXPOSURES']
    hdict = spirouImage.AddKey(p, hdict, p['kw_POL_MEANBJD'], value=meanbjd)

    return hdict, loc


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    print("SPIRou Polar Module")

# =============================================================================
# End of code
# =============================================================================
