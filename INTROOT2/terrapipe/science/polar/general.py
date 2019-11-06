#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2019-10-25 at 13:25

@author: cook
"""
from __future__ import division
import numpy as np
import warnings

from terrapipe import core
from terrapipe.core import math as mp
from terrapipe import locale
from terrapipe.core import constants
from terrapipe.core.core import drs_log
from terrapipe.core.core import drs_file

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'polar.general.py'
__INSTRUMENT__ = None
# Get constants
Constants = constants.load(__INSTRUMENT__)
# Get version and author
__version__ = Constants['DRS_VERSION']
__author__ = Constants['AUTHORS']
__date__ = Constants['DRS_DATE']
__release__ = Constants['DRS_RELEASE']
# get param dict
ParamDict = constants.ParamDict
DrsFitsFile = drs_file.DrsFitsFile
# Get Logging function
WLOG = core.wlog
# Get function string
display_func = drs_log.display_func
# Get the text types
TextEntry = locale.drs_text.TextEntry
TextDict = locale.drs_text.TextDict
# alias pcheck
pcheck = core.pcheck

# =============================================================================
# Define class
# =============================================================================
class PolarObj:
    def __init__(self, **kwargs):
        self.infile = kwargs.get('infile', None)
        self.fiber = kwargs.get('fiber', 'NOFIBER')
        self.exposure = kwargs.get('exposure', 'NAN')
        self.stoke = kwargs.get('stoke', 'NAN')
        self.sequence = kwargs.get('seqs', 'NAN')
        self.sequencetot = kwargs.get('seqtot', 'NAN')
        self.data = kwargs.get('data', None)
        self.filename = kwargs.get('filename', None)
        self.basename = kwargs.get('basename', None)
        # if infile is set, set data from infile
        if self.infile is not None:
            self.data = self.infile.data
            self.filename = self.infile.filename
            self.basename = self.infile.basename
        # set name
        self.name = self.__gen_key__()

    def __gen_key__(self):
        return '{0}_{1}'.format(self.fiber, self.exposure)

    def __str__(self):
        return 'PolarObj[{0}]'.format(self.name)

    def __repr__(self):
        return 'PolarObj[{0}]'.format(self.name)


# =============================================================================
# Define functions
# =============================================================================
def validate_polar_files(params, infiles, **kwargs):
    # set function name
    func_name = display_func(params, 'validate_polar_files', __NAME__)

    # get parameters from params
    valid_fibers = pcheck(params, 'POLAR_VALID_FIBERS', 'valid_fibers', kwargs,
                          func_name, mapf='list', dtype=str)
    valid_stokes = pcheck(params, 'POLAR_VALID_STOKES', 'valid_stokes', kwargs,
                          func_name, mapf='list', dtype=str)
    # this is a constant and should not be changed
    min_files = 4
    # ----------------------------------------------------------------------
    # right now we can only do this with two fibers - break if more fibers are
    #   defined
    if len(valid_fibers) != min_files // 2:
        eargs = ['({0})'.format(','.join(valid_fibers)), 'POLAR_VALID_FIBERS',
                 func_name]
        WLOG(params, 'error', TextEntry('00-021-00001', args=eargs))
    # ----------------------------------------------------------------------
    # get the number of infiles
    num_files = len(infiles)
    # ----------------------------------------------------------------------
    # storage dictionary
    pobjects = ParamDict()
    stokes, fibers, basenames = [], [] ,[]
    # loop around files
    for it in range(num_files):
        # print file iteration progress
        core.file_processing_update(params, it, num_files)
        # ge this iterations file
        infile = infiles[it]
        # extract polar values and validate file
        pout = valid_polar_file(params, infile)
        stoke, exp, seq, seqtot, fiber, valid = pout
        # skip any invalid files
        if not valid:
            continue
        # ------------------------------------------------------------------
        # log file addition
        wargs = [infile.basename, fiber, stoke, exp, seq, seqtot]
        WLOG(params, '', TextEntry('40-021-00001', args=wargs))
        # ------------------------------------------------------------------
        # get polar object for each
        pobj = PolarObj(infile=infile, fiber=fiber, exposure=exp, stoke=stoke,
                        seq=seq, seqtot=seqtot)
        # get name
        name = pobj.name
        # push into storage dictionary
        pobjects[name] = pobj
        # set source
        pobjects.set_source(name, func_name)
        # append lists (for checks)
        stokes.append(stoke)
        fibers.append(fiber)
        basenames.append(infile.basename)
    # ----------------------------------------------------------------------
    # deal with having no files
    if len(pobjects) == 0:
        eargs = ['\n\t'.join(basenames)]
        WLOG(params, 'error', TextEntry('09-021-00001', args=eargs))
    # deal with having less than minimum number of required files
    if len(pobjects) < 4:
        eargs = [4, '\n\t'.join(basenames)]
        WLOG(params, 'error', TextEntry('09-021-00002', args=eargs))
    # ----------------------------------------------------------------------
    # make sure we do not have multiple stokes parameters
    if len(np.unique(stokes)) != 1:
        eargs = [', '.join(np.unique(stokes))]
        WLOG(params, 'error', TextEntry('09-021-00003', args=eargs))
    # ----------------------------------------------------------------------
    # find number of A and B files
    num_a = np.sum(np.array(fibers) == valid_fibers[0])
    num_b = np.sum(np.array(fibers) == valid_fibers[1])
    # make sure we have 2 or 4 A fibers and 2 or 4 B fibers
    if len(fibers) == min_files * 2:
        # make sure number of A and B files is correct length
        if (num_a == min_files) and (num_b == min_files):
            kind = min_files
        else:
            eargs = [valid_fibers[0], valid_fibers[1], num_a, num_b, min_files]
            WLOG(params, 'error', TextEntry('09-021-00004', args=eargs))
            kind = None
    elif len(fibers) == min_files:
        # make sure number of A and B files is correct length
        if (num_a == min_files // 2) and (num_b == min_files // 2):
            kind = min_files // 2
        else:
            eargs = [valid_fibers[0], valid_fibers[1], num_a, num_b,
                     min_files // 2]
            WLOG(params, 'error', TextEntry('09-021-00004', args=eargs))
            kind = None
    else:
        eargs = [valid_fibers[0], valid_fibers[1],
                ' or '.join([str(min_files * 2), str(min_files)])]
        WLOG(params, 'error', TextEntry('09-021-00005', args=eargs))
        kind = None
    # ----------------------------------------------------------------------
    # set the output parameters
    props = ParamDict()
    props['NEXPOSURES'] = kind
    props['STOKES'] = np.unique(stokes)[0]
    props['MIN_FILES'] = min_files
    props['VALID_FIBERS'] = valid_fibers
    props['VALID_STOKES'] = valid_stokes
    # set sources
    keys = ['STOKES', 'NEXPOSURES', 'MIN_FILES', 'VALID_FIBERS', 'VALID_STOKES']
    props.set_sources(keys, func_name)
    # ----------------------------------------------------------------------
    # return polar object and properties
    return pobjects, props


def calculate_polarimetry(params, pobjs, props, **kwargs):
    # set function name
    func_name = display_func(params, 'calculate_polarimetry', __NAME__)
    # get parameters from params/kwargs
    method = pcheck(params, 'POLAR_METHOD', 'method', kwargs, func_name)
    # if method is not a string then break here
    if not isinstance(method, str):
        eargs = [method]
        WLOG(params, 'error', TextEntry('09-021-00006', args=eargs))
    # decide which method to use
    if method.lower() == 'difference':
        return polar_diff_method(params, pobjs, props)
    elif method.lower() == 'ratio':
        return polar_ratio_method(params, pobjs, props)
    else:
        eargs = [method]
        WLOG(params, 'error', TextEntry('09-021-00007', args=eargs))
        return 0


def calculate_stokes_i(params, pobjs, pprops):
    """
    Function to calculate the Stokes I polarization

    :param params: ParamDict, parameter dictionary of constants
    :param pobjs: dict, dictionary of polar object instance
    :param pprops: parameter dictionary, ParamDict containing data
        Must contain at least:
            NEXPOSURES: int, number of exposures in polar sequence

    :return pprops: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
            STOKESI: numpy array (2D), the Stokes I parameters, same shape as
                     DATA
            STOKESIERR: numpy array (2D), the Stokes I error parameters, same
                        shape as DATA
    """
    # set the function
    func_name = display_func(params, 'calculate_stokes_i', __NAME__)
    # log start of polarimetry calculations
    WLOG(params, '', TextEntry('40-021-00003'))
    # get parameters from props
    nexp = pprops['NEXPOSURES']
    # get the first file for reference
    pobj = pobjs['A_1']
    # storage of stokes parameters
    stokes_i = np.zeros(pobj.infile.shape)
    stokes_i_err = np.zeros(pobj.infile.shape)
    # storage of flux and variance
    flux, var = [], []
    # loop around exposures
    for it in range(1, int(nexp) + 1):
        # get a and b data for this exposure
        data_a = pobjs['A_{0}'.format(it)].data
        data_b = pobjs['B_{0}'.format(it)].data
        # Calculate sum of fluxes from fibers A and B
        flux_ab = data_a + data_b
        # Save A+B flux for each exposure
        flux.append(flux_ab)
        # Calculate the variances for fiber A+B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension in the e2ds files.
        var_ab = data_a + data_b
        # Save varAB = sigA^2 + sigB^2, ignoring cross-correlated terms
        var.append(var_ab)

    # Sum fluxes and variances from different exposures
    for it in range(len(flux)):
        stokes_i += flux[it]
        stokes_i_err += var[it]
    # Calcualte errors -> sigma = sqrt(variance)
    stokes_i_err = np.sqrt(stokes_i_err)

    # update the polar properties with stokes parameters
    pprops['STOKESI'] = stokes_i
    pprops['STOKESIERR'] = stokes_i_err
    # set sources
    keys = ['STOKESI', 'STOKESIERR']
    pprops.set_sources(keys, func_name)
    # return properties
    return pprops


def calculate_continuum(params, pprops, wprops, **kwargs):
    """
    Function to calculate the continuum polarization

    :param params: ParamDict, parameter dictionary of constants
    :param pobjs: dict, dictionary of polar object instance
    :param pprops: parameter dictionary, ParamDict containing data
        Must contain at least:
            POL: numpy array (2D), e2ds degree of polarization data
            POLERR: numpy array (2D), e2ds errors of degree of polarization
            NULL1: numpy array (2D), e2ds 1st null polarization
            NULL2: numpy array (2D), e2ds 2nd null polarization
            STOKESI: numpy array (2D), e2ds Stokes I data
            STOKESIERR: numpy array (2D), e2ds errors of Stokes I
    :params wprops: parameter dictionary, ParamDict containing wave data

    :return pprop: parameter dictionary, the updated parameter dictionary
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
    # set the function
    func_name = display_func(params, 'calculate_continuum', __NAME__)
    # get constants from params/kwargs
    pol_binsize = pcheck(params, 'POLAR_CONT_BINSIZE', 'pol_binsize', kwargs,
                         func_name)
    pol_overlap = pcheck(params, 'POLAR_CONT_OVERLAP', 'pol_overlap', kwargs,
                         func_name)
    pol_excl_bands_l = pcheck(params, 'POLAR_CONT_TELLMASK_LOWER',
                              'pol_excl_bands_l', kwargs, func_name,
                              mapf='list', dtype=float)
    pol_excl_bands_u = pcheck(params, 'POLAR_CONT_TELLMASK_UPPER',
                              'pol_excl_bands_u', kwargs, func_name,
                              mapf='list', dtype=float)
    # get wavelength map
    wavemap = wprops['WAVEMAP']
    # combine pol_excl_bands
    pol_excl_bands = list(zip(pol_excl_bands_l, pol_excl_bands_u))
    # ---------------------------------------------------------------------
    # flatten data (across orders)
    wl = wavemap.ravel()
    pol = pprops['POL'].ravel()
    polerr = pprops['POLERR'].ravel()
    stokes_i = pprops['STOKESI'].ravel()
    stokes_i_err = pprops['STOKESIERR'].ravel()
    null1 = pprops['NULL1'].ravel()
    null2 = pprops['NULL2'].ravel()
    # ---------------------------------------------------------------------
    # sort by wavelength (or pixel number)
    sortmask = np.argsort(wl)
    flat_x = wl[sortmask]
    flat_pol = pol[sortmask]
    flat_polerr = polerr[sortmask]
    flat_stokes_i = stokes_i[sortmask]
    flat_stokes_i_err = stokes_i_err[sortmask]
    flat_null1 = null1[sortmask]
    flat_null2 = null2[sortmask]
    # ---------------------------------------------------------------------
    # calculate continuum polarization
    contpol, xbin, ybin = mp.continuum(flat_x, flat_pol,
                                       binsize=pol_binsize, overlap=pol_overlap,
                                       excl_bands=pol_excl_bands)
    # ---------------------------------------------------------------------
    # update pprops
    pprops['FLAT_X'] = flat_x
    pprops['FLAT_POL'] = flat_pol
    pprops['FLAT_POLERR'] = flat_polerr
    pprops['FLAT_STOKESI'] = flat_stokes_i
    pprops['FLAT_STOKESIERR'] = flat_stokes_i_err
    pprops['FLAT_NULL1'] = flat_null1
    pprops['FLAT_NULL2'] = flat_null2
    pprops['CONT_POL'] = contpol
    pprops['CONT_XBIN'] = xbin
    pprops['CONT_YBIN'] = ybin
    # set sources
    keys = ['FLAT_X', 'FLAT_POL', 'FLAT_POLERR', 'FLAT_STOKESI',
            'FLAT_STOKEIERR', 'FLAT_NULL1', 'FLAT_NULL2', 'CONT_POL',
            'CONT_XBIN', 'CONT_YBIN']
    pprops.set_sources(keys, func_name)
    # add constants
    pprops['CONT_BINSIZE'] = pol_binsize
    pprops['CONT_OVERLAP'] = pol_overlap
    # set constants sources
    keys = ['CONT_BINSIZE', 'CONT_OVERLAP']
    pprops.set_sources(keys, func_name)
    # return pprops
    return pprops


def quality_control(params):

    # --------------------------------------------------------------
    # set passed variable and fail message list
    fail_msg = []
    qc_values, qc_names, qc_logic, qc_pass = [], [], [], []
    # textdict = TextDict(params['INSTRUMENT'], params['LANGUAGE'])
    # --------------------------------------------------------------
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
        WLOG(params, 'info', TextEntry('40-005-10001'))
    else:
        for farg in fail_msg:
            WLOG(params, 'warning', TextEntry('40-005-10002') + farg)
    # store in qc_params
    qc_params = [qc_names, qc_values, qc_logic, qc_pass]
    # return qc_params
    return qc_params, passed


# =============================================================================
# Define worker functions
# =============================================================================
def valid_polar_file(params, infile, **kwargs):
    """
    Read and extract parameters from cmmtseq string from header key at
    KW_CMMTSEQ

    for spirou the format is as follows:
       {0} exposure {1}, sequence {2} of {3}
     where {0} is the stokes parameter
     where {1} is the exposure number
     where {2} is the sequence number
     where {3} is the total number of sequences

    :param params: ParamDict, the parameter dictionary
    :param infile: DrsFitsFile, the Drs Fits file to get the header key from

    :type params: ParamDict
    :type infile: DrsFitsFile

    :return:
    """
    # set function name
    func_name = display_func(params, 'read_cmmtseq', __NAME__)
    # assume valid at first
    valid = True
    # get values from parameters
    valid_fibers = pcheck(params, 'POLAR_VALID_FIBERS', 'valid_fibers', kwargs,
                          func_name, mapf='list', dtype=str)
    valid_stokes = pcheck(params, 'POLAR_VALID_STOKES', 'valid_stokes', kwargs,
                          func_name, mapf='list', dtype=str)
    # ----------------------------------------------------------------------
    # get cmmtseq key
    cmmtseq = infile.get_key('KW_CMMTSEQ')
    # get fiber type
    fiber = infile.get_key('KW_FIBER')
    # ----------------------------------------------------------------------
    # deal with bad file
    if cmmtseq in [None, '', 'None']:
        eargs = [params['KW_CMMTSEQ'][0], infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00004', args=eargs))
        return None, None, None, None, fiber, False
    # ----------------------------------------------------------------------
    # split to string by white spaces
    split = cmmtseq.split()
    # ----------------------------------------------------------------------
    # get stokes parameter (first letter)
    stoke_parameter = split[0]
    # ----------------------------------------------------------------------
    # get exposure number
    exposure = split[2].strip(',')
    try:
        exposure = int(exposure)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00001', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # get the sequence number
    sequence = split[4]
    try:
        sequence = int(sequence)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00002', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # get the total number of sequences
    total = split[6]
    try:
        total = int(total)
    except ValueError:
        eargs = [params['KW_CMMTSEQ'][0], cmmtseq]
        WLOG(params, 'warning', TextEntry('10-021-00003', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # deal with fiber type
    if fiber not in valid_fibers:
        eargs = [fiber, ', '.join(valid_fibers), infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00005', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # deal with stokes parameters - check parameter is valid
    if stoke_parameter not in valid_stokes:
        eargs = [stoke_parameter, ', '.join(valid_stokes), infile.filename]
        WLOG(params, 'warning', TextEntry('10-021-00006', args=eargs))
        valid = False
    # ----------------------------------------------------------------------
    # return extracted parameters
    if not valid:
        return None, None, None, None, fiber, False
    else:
        return stoke_parameter, exposure, sequence, total, fiber, valid


def polar_diff_method(params, pobjs, props):
    """
    Function to calculate polarimetry using the difference method as described
    in the paper:
        Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)

    :param params: ParamDict, parameter dictionary of constants
    :param pobjs: dict, dictionary of polar object instance
    :param props: parameter dictionary, parameter dictionary from polar
                  validation

    :type params: ParamDict
    :type pobjs: dict
    :type props: ParamDict

    :return: ParamDict of polar outputs (pol, pol_err, null1, null2, method)
    """
    # set function name
    func_name = display_func(params, 'polar_diff_method', __NAME__)
    # log start of polarimetry calculations
    WLOG(params, '', TextEntry('40-021-00002', args=['difference']))
    # get parameters from props
    nexp = props['NEXPOSURES']
    # get the first file for reference
    pobj = pobjs['A_1']
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    pol = np.zeros(pobj.infile.shape)
    pol_err = np.zeros(pobj.infile.shape)
    null1 = np.zeros(pobj.infile.shape)
    null2 = np.zeros(pobj.infile.shape)
    # ---------------------------------------------------------------------
    # loop around exposures and combine A and B
    gg, gvar = [], []
    for it in range(1, int(nexp) + 1):
        # get a and b data for this exposure
        data_a = pobjs['A_{0}'.format(it)].data
        data_b = pobjs['B_{0}'.format(it)].data
        # ---------------------------------------------------------------------
        # STEP 1 - calculate the quantity Gn (Eq #12-14 on page 997 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        part1 = data_a - data_b
        part2 = data_a + data_b
        gg.append(part1 / part2)
        # Calculate the variances for fiber A and B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension of e2ds files.
        a_var = data_a
        b_var = data_b
        # ---------------------------------------------------------------------
        # STEP 2 - calculate the quantity g_n^2 (Eq #A4 on page 1013 of
        #          Bagnulo et al. 2009), n being the pair of exposures
        # ---------------------------------------------------------------------
        nomin = 2.0 * data_a * data_b
        denom = (data_a + data_b) ** 2.0
        factor1 = (nomin / denom) ** 2.0
        a_var_part = a_var / (data_a ** 2.0)
        b_var_part = b_var / (data_b ** 2.0)
        gvar.append(factor1 * (a_var_part + b_var_part))
    # ---------------------------------------------------------------------
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
        pol = (d1 + d2) / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the first NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        null1 = (d1 - d2) / nexp
        # -----------------------------------------------------------------
        # STEP 6 - calculate the second NULL spectrum
        #          (Eq #20 on page 997 of Bagnulo et al. 2009)
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        null2 = (d1s - d2s) / nexp
        # -----------------------------------------------------------------
        # STEP 7 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1] + gvar[2] + gvar[3]
        pol_err = np.sqrt(sum_of_gvar / (nexp ** 2.0))
    # ---------------------------------------------------------------------
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
        pol = d1 / nexp
        # -----------------------------------------------------------------
        # STEP 5 - calculate the polarimetry error
        #          (Eq #A3 on page 1013 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        sum_of_gvar = gvar[0] + gvar[1]
        pol_err = np.sqrt(sum_of_gvar / (nexp ** 2.0))
    # ---------------------------------------------------------------------
    # else we have insufficient data (should not get here)
    else:
        # Log that the number of exposures is not sufficient
        eargs = [nexp, func_name]
        WLOG(params, 'error', TextEntry('09-021-00008', args=eargs))
    # ---------------------------------------------------------------------
    # populate the polar properties
    pprops = ParamDict()
    pprops['POL'] = pol
    pprops['NULL1'] = null1
    pprops['NULL2'] = null2
    pprops['POLERR'] = pol_err
    pprops['METHOD'] = 'Difference'
    pprops['NEXPOSURES'] = nexp
    # set sources
    keys = ['POL', 'NULL1', 'NULL2', 'POLERR', 'METHOD', 'NEXPOSURES']
    pprops.set_sources(keys, func_name)
    # return the properties
    return pprops


def polar_ratio_method(params, pobjs, props):
    """
    Function to calculate polarimetry using the ratio method as described
    in the paper:
        Bagnulo et al., PASP, Volume 121, Issue 883, pp. 993 (2009)


    :param params: ParamDict, parameter dictionary of constants
    :param pobjs: dict, dictionary of polar object instance
    :param props: parameter dictionary, parameter dictionary from polar
                  validation

    :type params: ParamDict
    :type pobjs: dict
    :type props: ParamDict

    :return: ParamDict of polar outputs (pol, pol_err, null1, null2, method)
    """
    # set function name
    func_name = display_func(params, 'polar_ratio_method', __NAME__)
    # log start of polarimetry calculations
    WLOG(params, '', TextEntry('40-021-00002', args=['difference']))
    # get parameters from props
    nexp = props['NEXPOSURES']
    # get the first file for reference
    pobj = pobjs['A_1']
    # ---------------------------------------------------------------------
    # set up storage
    # ---------------------------------------------------------------------
    pol = np.zeros(pobj.infile.shape)
    pol_err = np.zeros(pobj.infile.shape)
    null1 = np.zeros(pobj.infile.shape)
    null2 = np.zeros(pobj.infile.shape)
    # storage
    flux_ratio, var_term = [], []
    # loop around exposures
    for it in range(1, int(nexp) + 1):
        # get a and b data for this exposure
        data_a = pobjs['A_{0}'.format(it)].data
        data_b = pobjs['B_{0}'.format(it)].data
        # ---------------------------------------------------------------------
        # STEP 1 - calculate ratio of beams for each exposure
        #          (Eq #12 on page 997 of Bagnulo et al. 2009 )
        # ---------------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            flux_ratio.append(data_a / data_b)
        # Calculate the variances for fiber A and B, assuming Poisson noise
        # only. In fact the errors should be obtained from extraction, i.e.
        # from the error extension of e2ds files.
        a_var = data_a
        b_var = data_b
        # ---------------------------------------------------------------------
        # STEP 2 - calculate the error quantities for Eq #A10 on page 1014 of
        #          Bagnulo et al. 2009
        # ---------------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            var_term_part1 = a_var / (data_a ** 2.0)
            var_term_part2 = b_var / (data_b ** 2.0)
        var_term.append(var_term_part1 + var_term_part2)
    # ---------------------------------------------------------------------
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
        with warnings.catch_warnings(record=True) as _:
            r1 = flux_ratio[0] / flux_ratio[1]
            r2 = flux_ratio[3] / flux_ratio[2]
            r1s = flux_ratio[0] / flux_ratio[2]
            r2s = flux_ratio[3] / flux_ratio[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rr = (r1 * r2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            pol = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the quantity RN1
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rn1 = (r1 / r2) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 7 - calculate the first NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            null1 = (rn1 - 1.0) / (rn1 + 1.0)
        # -----------------------------------------------------------------
        # STEP 8 - calculate the quantity RN2
        #          (Part of Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rn2 = (r1s / r2s) ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 9 - calculate the second NULL spectrum
        #          (Eq #25-26 on page 998 of Bagnulo et al. 2009),
        #          with exposure 2 and 4 swapped
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            null2 = (rn2 - 1.0) / (rn2 + 1.0)
        # -----------------------------------------------------------------
        # STEP 10 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            numer_part1 = (r1 * r2) ** (1.0 / 2.0)
            denom_part1 = ((r1 * r2) ** (1.0 / 4.0) + 1.0) ** 4.0
            part1 = numer_part1 / (denom_part1 * 4.0)
        sumvar = var_term[0] + var_term[1] + var_term[2] + var_term[3]
        pol_err = np.sqrt(part1 * sumvar)
    # ---------------------------------------------------------------------
    # else if we have 2 exposures
    elif nexp == 2:
        # -----------------------------------------------------------------
        # STEP 3 - calculate the quantity Rm
        #          (Eq #23 on page 998 of Bagnulo et al. 2009) and
        #          the quantity Rms with exposure 2 and 4 swapped,
        #          m being the pair of exposures
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            r1 = flux_ratio[0] / flux_ratio[1]
        # -----------------------------------------------------------------
        # STEP 4 - calculate the quantity R
        #          (Part of Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            rr = r1 ** (1.0 / nexp)
        # -----------------------------------------------------------------
        # STEP 5 - calculate the degree of polarization
        #          (Eq #24 on page 998 of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        with warnings.catch_warnings(record=True) as _:
            pol = (rr - 1.0) / (rr + 1.0)
        # -----------------------------------------------------------------
        # STEP 6 - calculate the polarimetry error (Eq #A10 on page 1014
        #           of Bagnulo et al. 2009)
        # -----------------------------------------------------------------
        # numer_part1 = R1
        with warnings.catch_warnings(record=True) as _:
            denom_part1 = ((r1 ** 0.5) + 1.0) ** 4.0
            part1 = r1 / denom_part1
        sumvar = var_term[0] + var_term[1]
        pol_err = np.sqrt(part1 * sumvar)
    # ---------------------------------------------------------------------
    # else we have insufficient data (should not get here)
    else:
        # Log that the number of exposures is not sufficient
        eargs = [nexp, func_name]
        WLOG(params, 'error', TextEntry('09-021-00008', args=eargs))
    # ---------------------------------------------------------------------
    # populate the polar properties
    pprops = ParamDict()
    pprops['POL'] = pol
    pprops['NULL1'] = null1
    pprops['NULL2'] = null2
    pprops['POLERR'] = pol_err
    pprops['METHOD'] = 'Difference'
    pprops['NEXPOSURES'] = nexp
    # set sources
    keys = ['POL', 'NULL1', 'NULL2', 'POLERR', 'METHOD', 'NEXPOSURES']
    pprops.set_sources(keys, func_name)
    # return the properties
    return pprops


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
