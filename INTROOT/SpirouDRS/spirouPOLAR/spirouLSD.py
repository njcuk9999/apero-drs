#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou Least-Squares Deconvolution (LSD) analysis module

Created on 2018-08-08 at 14:53

@author: E. Martioli

"""
from __future__ import division
import numpy as np
from scipy import constants
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

import os

from SpirouDRS import spirouConfig
from SpirouDRS import spirouCore
from SpirouDRS import spirouImage

# =============================================================================
# Define variables
# =============================================================================
# Name of program
__NAME__ = 'spirouLSD.py'
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

def lsd_analysis_wrapper(p, loc):
    """
        Function to call functions to perform Least Squares Deconvolution (LSD)
        analysis on the polarimetry data.
        
        :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
        LOG_OPT: string, option for logging
        
        :param loc: parameter dictionary, ParamDict containing data
        
        :return loc: parameter dictionary, the updated parameter dictionary
        Adds/updates the following:
        
        """
    func_name = __NAME__ + '.lsd_analysis_wrapper()'
    name = 'LSDAnalysis'

    # log start of LSD analysis calculations
    wmsg = 'Running function {0} to perform LSD analysis'
    WLOG('info', p['LOG_OPT'], wmsg.format(name))

    # load spectral lines
    loc = load_lsd_spectral_lines(p, loc)
 
    # get wavelength ranges covering spectral lines in the ccf mask
    loc = get_wl_ranges(p, loc)

    # prepare polarimetry data
    loc = prepare_polarimetry_data(p, loc)
    
    # call function to perform lsd analysis
    loc = lsd_analysis(p, loc)
    
    return loc


def load_lsd_spectral_lines(p, loc):
    """
    Function to load spectral lines data for LSD analysis.
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            IC_POLAR_LSD_CCFLINES: string, file containing spectral lines data
            IC_POLAR_LSD_WLRANGES: array of float pairs for wavelength ranges
            IC_POLAR_LSD_MIN_LINEDEPTH: float, line depth threshold
    :param loc: parameter dictionary, ParamDict to store data
        
    :return loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
        loc['LSD_LINES_WLC']: numpy array (1D), central wavelengths
        loc['LSD_LINES_ZNUMBER']: numpy array (1D), atomic number (Z)
        loc['LSD_LINES_DEPTH']: numpy array (1D), line depths
        loc['LSD_LINES_POL_WEIGHT']: numpy array (1D), line weights =
                                     depth * lande * wlc
    """
    
    func_name = __NAME__ + '.load_lsd_spectral_lines()'
    
    # get package name and relative path
    package = spirouConfig.Constants.PACKAGE()
    relfolder = spirouConfig.Constants.LSD_MASK_DIR()
    # get absolute folder path from package and relfolder
    absfolder = spirouConfig.GetAbsFolderPath(package, relfolder)
    # strip filename
    filename = p['IC_POLAR_LSD_CCFLINES']
    # get absolute path and filename
    abspath = os.path.join(absfolder, filename)
    # if path exists use it
    if os.path.exists(abspath):
        wmsg = 'Line mask used for LSD computation: {0}'
        WLOG('info', p['LOG_OPT'], wmsg.format(abspath))
        # load spectral lines data from file
        wlcf,znf,depthf,landef = np.loadtxt(abspath,delimiter='  ',skiprows=1,
                                            usecols=(0,1,2,3), unpack=True)
    # else raise error
    else:
        emsg1 = 'LSD Line mask file: "{0}" not found, unable to proceed'
        emsg2 = '    function = {0}'.format(func_name)
        WLOG('error', p['LOG_OPT'], [emsg1.format(filename),emsg2])

    # initialize data vectors
    wlc,zn,depth,lande = [], [], [], []
    # loop over spectral ranges to select only spectral lines within ranges
    for wlrange in p['IC_POLAR_LSD_WLRANGES'] :
        # set initial and final wavelengths in range
        wl0, wlf = wlrange[0], wlrange[1]
        # create wavelength mask to limit wavelength range
        mask = np.where(np.logical_and(wlcf > wl0, wlcf < wlf))
        wlc = np.append(wlc,wlcf[mask])
        zn = np.append(zn,znf[mask])
        depth = np.append(depth,depthf[mask])
        lande = np.append(lande,landef[mask])
    
    # PS. Below it applies a line depth mask, however the cut in line depth
    # should be done according to the SNR. This will be studied and implemented
    # later. E. Martioli, Aug 10 2018.
    
    # create mask to cut lines with depth lower than IC_POLAR_LSD_MIN_LINEDEPTH
    dmask = np.where(depth > p['IC_POLAR_LSD_MIN_LINEDEPTH'])
    # apply mask to the data
    wlc, zn, depth, lande = wlc[dmask], zn[dmask], depth[dmask], lande[dmask]

    # calculate weights for calculation of polarimetric Z-profile
    weight = wlc * depth * lande
    weight = weight / np.max(weight)

    # store data into loc dict
    loc['LSD_LINES_WLC'] = wlc
    loc['LSD_LINES_ZNUMBER'] = zn
    loc['LSD_LINES_DEPTH'] = depth
    loc['LSD_LINES_POL_WEIGHT'] = weight

    return loc

def get_wl_ranges(p, loc) :
    
    """
    Function to generate a list of spectral ranges covering all spectral
    lines in the CCF mask, where the width of each individual range is
    defined by the LSD velocity vector
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            IC_POLAR_LSD_V0: initial velocity for LSD profile
            IC_POLAR_LSD_VF: final velocity for LSD profile

    :param loc: parameter dictionary, ParamDict to store data
        loc['LSD_LINES_WLC']: numpy array (1D), central wavelengths
        
    :return loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
        loc['LSD_LINES_WLRANGES']: array of float pairs for wavelength ranges
       
    """
    func_name = __NAME__ + '.get_wl_ranges()'

    # speed of light in km/s
    c = constants.c / 1000.
    # set initial and final velocity
    v0, vf = p['IC_POLAR_LSD_V0'], p['IC_POLAR_LSD_VF']
    # define vector of spectral ranges covering only regions around lines
    wlranges_tmp = []
    for w in loc['LSD_LINES_WLC'] :
        dwl = w*(vf-v0)/(2.*c)
        wl0 = w - dwl
        wlf = w + dwl
        wlranges_tmp.append([wl0,wlf])
    # initialize final vector of spectral ranges
    loc['LSD_LINES_WLRANGES'] = []
    # initialize current wl0 and wlf
    current_wl0, current_wlf = wlranges_tmp[0][0],wlranges_tmp[0][1]
    # merge overlapping ranges
    for r in wlranges_tmp :
        if r[0] <= current_wlf :
            current_wlf = r[1]
        else :
            loc['LSD_LINES_WLRANGES'].append([current_wl0, current_wlf])
            current_wl0 = r[0]
            current_wlf = r[1]
    # append last range
    loc['LSD_LINES_WLRANGES'].append([current_wl0, current_wlf])

    return loc


def prepare_polarimetry_data(p, loc):
    """
    Function to prepare polarimetry data for LSD analysis.
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            IC_POLAR_LSD_NORMALIZE: bool, normalize Stokes I data
                
    :param loc: parameter dictionary, ParamDict to store data
        Must contain at least:
            loc['WAVE']: numpy array (2D), wavelength data
            loc['STOKESI']: numpy array (2D), Stokes I data
            loc['STOKESIERR']: numpy array (2D), errors of Stokes I
            loc['POL']: numpy array (2D), degree of polarization data
            loc['POLERR']: numpy array (2D), errors of degree of polarization
            loc['NULL2']: numpy array (2D), 2nd null polarization

    :return loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
            loc['LSD_WAVE']: numpy array (1D), wavelength data
            loc['LSD_STOKESI']: numpy array (1D), Stokes I data
            loc['LSD_STOKESIERR']: numpy array (1D), errors of Stokes I
            loc['LSD_POL']: numpy array (1D), degree of polarization data
            loc['LSD_POLERR']: numpy array (1D), errors of polarization
            loc['LSD_NULL']: numpy array (1D), 2nd null polarization
        
    """
    
    func_name = __NAME__ + '.prepare_polarimetry_data()'

    # get the shape of pol
    ydim, xdim = loc['POL'].shape
    # get wavelength ranges to be considered in each spectral order
    ordermask = get_order_ranges()
    # initialize output data vectors
    loc['LSD_WAVE'], loc['LSD_STOKESI'], loc['LSD_STOKESIERR'] = [], [], []
    loc['LSD_POL'], loc['LSD_POLERR'], loc['LSD_NULL'] = [], [], []
    # loop over each order
    for order_num in range(ydim) :
        # mask NaN values
        nanmask = np.where(np.logical_and(~np.isnan(loc['STOKESI'][order_num]),
                                          ~np.isnan(loc['POL'][order_num])))
          
        wl_tmp = loc['WAVE'][order_num][nanmask]
        pol_tmp = loc['POL'][order_num][nanmask]
        polerr_tmp = loc['POLERR'][order_num][nanmask]
        flux_tmp = loc['STOKESI'][order_num][nanmask]
        fluxerr_tmp = loc['STOKESIERR'][order_num][nanmask]
        null_tmp = loc['NULL2'][order_num][nanmask]

        # set order wavelength limits
        wl0, wlf = ordermask[order_num][0], ordermask[order_num][1]
        # create wavelength mask
        mask = np.where(np.logical_and(wl_tmp > wl0, wl_tmp < wlf))
        
        # test if order is not empty
        if len(wl_tmp[mask]) :
            # get masked data
            wl, flux, fluxerr = wl_tmp[mask], flux_tmp[mask], fluxerr_tmp[mask]
            pol, polerr, null = pol_tmp[mask], polerr_tmp[mask], null_tmp[mask]
            
            if p['IC_POLAR_LSD_NORMALIZE'] :
                # measure continuum
                continuum,xbin,ybin = spirouCore.Continuum(wl, flux, binsize=50,
                                                          overlap=25, window=2,
                                                          mode="median",
                                                          use_linear_fit=True)
                # normalize flux
                flux = flux/continuum
            
            # append data to output vector
            loc['LSD_WAVE'] = np.append(loc['LSD_WAVE'],wl)
            loc['LSD_STOKESI'] = np.append(loc['LSD_STOKESI'],flux)
            loc['LSD_STOKESIERR'] = np.append(loc['LSD_STOKESIERR'],fluxerr)
            loc['LSD_POL'] = np.append(loc['LSD_POL'],pol)
            loc['LSD_POLERR'] = np.append(loc['LSD_POLERR'],polerr)
            loc['LSD_NULL'] = np.append(loc['LSD_NULL'],null)

    # sort data by wavelength
    indices = loc['LSD_WAVE'].argsort()
    loc['LSD_WAVE'] = loc['LSD_WAVE'][indices]
    loc['LSD_STOKESI'] = loc['LSD_STOKESI'][indices]
    loc['LSD_STOKESIERR'] = loc['LSD_STOKESIERR'][indices]
    loc['LSD_POL'] = loc['LSD_POL'][indices]
    loc['LSD_POLERR'] = loc['LSD_POLERR'][indices]
    loc['LSD_NULL'] = loc['LSD_NULL'][indices]

    # initialize temporary data vectors
    wl, flux, fluxerr, pol, polerr, null = [], [], [], [], [], []
    # loop over spectral ranges to select only spectral regions of interest
    for wlrange in loc['LSD_LINES_WLRANGES'] :
        # set initial and final wavelengths in range
        wl0, wlf = wlrange[0], wlrange[1]
        
        # create wavelength mask to limit wavelength range
        wlmask = np.where(np.logical_and(loc['LSD_WAVE'] > wl0,
                                         loc['LSD_WAVE'] < wlf))
        wl = np.append(wl,loc['LSD_WAVE'][wlmask])
        flux = np.append(flux,loc['LSD_STOKESI'][wlmask])
        fluxerr = np.append(fluxerr,loc['LSD_STOKESIERR'][wlmask])
        pol = np.append(pol,loc['LSD_POL'][wlmask])
        polerr = np.append(polerr,loc['LSD_POLERR'][wlmask])
        null = np.append(null,loc['LSD_NULL'][wlmask])

    # update loc data vectors
    loc['LSD_WAVE'] = wl
    loc['LSD_STOKESI'] = flux
    loc['LSD_STOKESIERR'] = fluxerr
    loc['LSD_POL'] = pol
    loc['LSD_POLERR'] = polerr
    loc['LSD_NULL'] = null

    return loc


def lsd_analysis(p, loc):
    """
    Function to perform Least Squares Deconvolution (LSD) analysis.
        
    :param p: parameter dictionary, ParamDict containing constants
        Must contain at least:
            LOG_OPT: string, option for logging
            
    :param loc: parameter dictionary, ParamDict to store data
        Must contain at least:
            loc['IC_POLAR_LSD_V0']: initial velocity for LSD profile
            loc['IC_POLAR_LSD_VF']: final velocity for LSD profile
            loc['IC_POLAR_LSD_NP']: number of points in the LSD profile
            loc['LSD_WAVE']: numpy array (1D), wavelength data
            loc['LSD_STOKESI']: numpy array (1D), Stokes I data
            loc['LSD_STOKESIERR']: numpy array (1D), errors of Stokes I
            loc['LSD_POL']: numpy array (1D), degree of polarization data
            loc['LSD_POLERR']: numpy array (1D), errors of polarization
            loc['LSD_NULL']: numpy array (1D), 2nd null polarization
            loc['LSD_LINES_WLC']: numpy array (1D), central wavelengths
            loc['LSD_LINES_DEPTH']: numpy array (1D), line depths
            loc['LSD_LINES_POL_WEIGHT']: numpy array (1D), line weights =
                                         depth * lande * wlc
        
    :return loc: parameter dictionaries,
        The updated parameter dictionary adds/updates the following:
            loc['LSD_VELOCITIES']: numpy array (1D), LSD profile velocities
            loc['LSD_STOKESI']: numpy array (1D), LSD profile for Stokes I
            loc['LSD_STOKESI_MODEL']: numpy array (1D), LSD gaussian model 
                                      profile for Stokes I
            loc['LSD_STOKESVQU']: numpy array (1D), LSD profile for Stokes 
                                  Q,U,V polarimetry spectrum
            loc['LSD_NULL']: numpy array (1D), LSD profile for null
                                  polarization spectrum
        
    """
    
    func_name = __NAME__ + '.lsd_analysis()'
    
    # initialize variables to define velocity vector of output LSD profile
    v0,vf,m = p['IC_POLAR_LSD_V0'], p['IC_POLAR_LSD_VF'], p['IC_POLAR_LSD_NP']
    
    # create velocity vector for output LSD profile
    loc['LSD_VELOCITIES'] = np.linspace(v0, vf, m)
    
    # create line pattern matrix for flux LSD
    M, Mp = line_pattern_matrix(loc['LSD_WAVE'],loc['LSD_LINES_WLC'],
                                loc['LSD_LINES_DEPTH'],
                                loc['LSD_LINES_POL_WEIGHT'],
                                loc['LSD_VELOCITIES'])
    
    # calculate flux LSD profile
    loc['LSD_STOKESI'] = calculate_lsd_profile(loc['LSD_WAVE'],
                                               loc['LSD_STOKESI'],
                                               loc['LSD_STOKESIERR'],
                                               loc['LSD_VELOCITIES'], M,
                                               normalize=True)

    # fit gaussian to the measured flux LSD profile
    loc['LSD_STOKESI_MODEL'], loc['LSD_FIT_RV'], loc['LSD_FIT_RESOL'] = fit_gaussian_to_lsd_profile(loc['LSD_VELOCITIES'],loc['LSD_STOKESI'])
    
    # calculate polarimetry LSD profile
    loc['LSD_STOKESVQU'] = calculate_lsd_profile(loc['LSD_WAVE'], loc['LSD_POL'],
                               loc['LSD_POLERR'], loc['LSD_VELOCITIES'], Mp)

    # calculate null polarimetry LSD profile
    loc['LSD_NULL'] = calculate_lsd_profile(loc['LSD_WAVE'], loc['LSD_NULL'],
                                loc['LSD_POLERR'], loc['LSD_VELOCITIES'], Mp)

    return loc

def line_pattern_matrix(wl, wlc, depth, weight, vels) :
    """
    Function to calculate the line pattern matrix M given in Eq (4) of paper
    Donati et al. (1997), MNRAS 291, 658-682
    
    :param wl: numpy array (1D), input wavelength data (size n = spectrum size)
    :param wlc: numpy array (1D), central wavelengths (size = number of lines)
    :param depth: numpy array (1D), line depths (size = number of lines)
    :param weight: numpy array (1D), line polar weights (size = number of lines)
    :param vels: numpy array (1D), , LSD profile velocity vector (size = m)
    
    :return M, Mp
        M: numpy array (2D) of size n x m, line pattern matrix for flux LSD.
        Mp: numpy array (2D) of size n x m, line pattern matrix for polar LSD.
    """

    #set number of points and velocity (km/s) limits in LSD profile
    m, v0, vf = len(vels), vels[0], vels[-1]

    # speed of light in km/s
    c = constants.c / 1000.
    
    # set number of spectral points
    n = len(wl)
    
    # initialize line pattern matrix for flux LSD
    M = np.zeros((n, m))
                           
    # initialize line pattern matrix for polar LSD
    Mp = np.zeros((n, m))

    # set first i=0 -> trick to improve speed
    i0 = 0
    # set values of line pattern matrix M
    for l in range(len(wlc)) :
        noi0=True
        for i in range(i0,n) :
            #Calculate line velocity: v = c Δλ / λ
            v = c * (wl[i] - wlc[l]) / wlc[l]
            if v0 <= v <= vf :
                # below is a trick to improve speed
                if noi0 :
                    # next spectral line starts with first i of previous line
                    # warning: list of CCF lines must be sorted by wavelength
                    i0 = i
                    noi0=False
                for j in range(m-1) :
                    if vels[j] <= v < vels[j+1] :
                        Mp[i][j] += weight[l]
                        M[i][j] += depth[l]
                        if M[i][j] > 1.0 :
                            M[i][j] = 1.0
                        break
            elif v > vf :
                break
    return M, Mp


def calculate_lsd_profile(wl, flux, fluxerr, vels, M, normalize=False) :
    """
    Function to calculate the LSD profile Z given in Eq (4) of paper
    Donati et al. (1997), MNRAS 291, 658-682
    
    :param wl: numpy array (1D), input wavelength data (size = n)
    :param flux: numpy array (1D), input flux or polarimetry data (size = n)
    :param fluxerr: numpy array (1D), input flux or polarimetry error data 
                    (size = n)
    :param vels: numpy array (1D), , LSD profile velocity vector (size = m)
    :param M: numpy array (2D) of size n x m, line pattern matrix for LSD.
    :param normalize: bool, to calculate a continuum and normalize profile
    
    :return Z: numpy array (1D) of size m, LSD profile.
    """

    # set number of spectral points
    n = len(wl)

    # First calculate transpose of M
    MT = np.matrix.transpose(M)

    # Initialize matrix for dot product between MT . S^2
    MTxS2 = np.zeros_like(MT)
    
    # Then calculate dot product between MT . S^2, where S^2=covariance matrix
    for j in range(np.shape(MT)[0]) :
        MTxS2[j] = MT[j] / fluxerr**2

    # calculate autocorrelation, i.e., MT . S^2 . M
    MTxS2xM = MTxS2.dot(M)

    # calculate the inverse of autocorrelation using numpy pinv method
    MTxS2xM_inv = np.linalg.pinv(MTxS2xM)

    # calculate cross correlation term, i.e. MT . S^2 . Y
    XCorrTerm = MTxS2.dot(flux)

    # calculate velocity profile
    Z = MTxS2xM_inv.dot(XCorrTerm)
    # recover last point
    Z[-1] = np.median(Z[-6:-2])

    if normalize :
        # calculate continuum of LSD profile to remove trend
        cont_Z, xbin, ybin = spirouCore.Continuum(vels,Z, binsize=20, overlap=5,
                                                  sigmaclip=3.0, window=2,
                                                  mode="median",
                                                  use_linear_fit=False)
        # calculate normalized and detrended LSD profile
        Z /= cont_Z

    return Z

def fit_gaussian_to_lsd_profile(vels, Z) :
    """
        Function to fit gaussian to LSD Stokes I profile.
        
        :param vels: numpy array (1D), input velocity data
        :param Z: numpy array (1D), input LSD profile data
        
        :return Zgauss, outRV, outresolution:
            Zgauss:     numpy array (1D), gaussian fit to LSD profile (same size
                        as input vels and Z
            RV:         float, velocity of minimum obtained from gaussian fit
            resolution: float, spectral resolution obtained from sigma of 
                        gaussian fit
        """

    # set speed of light in km/s
    c = constants.c / 1000.
    
    # obtain velocity at minimum, amplitude, and sigma for initial guess
    rvel = vels[np.argmin(Z)]
    amplitude = 1.0 - np.min(Z)
    resolvingPower = 50000.
    sig = c/(resolvingPower*2.3548)
    
    # set gaussian function
    gaussian = lambda x,a,x0,sigma : a*np.exp(-(x-x0)**2/(2.*sigma**2))
    
    # get inverted profile
    Zinv = 1.0 - Z

    # fit gaussian profile
    popt,pcov = curve_fit(gaussian,vels,Zinv,p0=[amplitude,rvel,sig])
    
    # initialize output profile vector
    Zgauss = np.zeros_like(vels)
    
    for i in range(len(Zgauss)) :
        # calculate gaussian model profile
        Zgauss[i] = gaussian(vels[i],*popt)
    
    # invert fit profile
    Zgauss = 1.0 - Zgauss

    # calculate full width at half maximum (fwhm)
    fwhm = 2.35482 * popt[2]
    # calculate resolving power from mesasured fwhm
    resolvingPower = c/fwhm
    
    # set radial velocity directly from fitted v_0
    RV = popt[1]
    
    return Zgauss, RV, resolvingPower


def get_order_ranges():
    """
    Function to provide the valid wavelength ranges for each order in SPIrou.
        
    :param: None
        
    :return orders: array of float pairs for wavelength ranges
    """
    orders = [[963.6,986.0],[972.0,998.4],[986.3,1011],[1000.1,1020],
              [1015,1035],[1027.2,1050],[1042,1065],[1055,1078],[1070,1096],
              [1084,1112.8],[1098,1128],[1113,1146],[1131,1162],[1148,1180],
              [1166,1198],[1184,1216],[1202,1235],[1222,1255],[1243,1275],
              [1263,1297],[1284,1320],[1306,1342],[1328,1365],[1352,1390],
              [1377,1415],[1405,1440],[1429,1470],[1456,1497],[1485,1526],
              [1515,1557],[1545,1590],[1578,1623],[1609,1657],[1645,1692],
              [1681,1731],[1722,1770],[1760,1810],[1800,1855],[1848,1900],
              [1890,1949],[1939,1999],[1991,2050],[2044.5,2105],[2104,2162],
              [2161,2226],[2225,2293],[2291,2362],[2362,2430],[2440,2510]]
    return orders


def output_lsd_image(p, loc, hdict) :
    """
    Function to set up and save output FITS image to store LSD analyis.
        
    :param p: parameter dictionary, ParamDict containing constants
    :param loc: parameter dictionary, ParamDict to store data
        Must contain at least:
            loc['LSDDATA']: numpy array (2D), LSD analysis data
        
    :return lsdfits, lsdfitsfitsname:
        lsdfits:         string, output full path
        lsdfitsfitsname: string, output filename
    """
        
    # construct file names
    lsdfits = spirouConfig.Constants.LSD_POL_FILE(p, loc)
    lsdfitsfitsname = os.path.split(lsdfits)[-1]

    # save all data into a single array for output FITS
    loc['LSDDATA'] = []
    loc['LSDDATA'] = np.append(loc['LSDDATA'],loc['LSD_VELOCITIES'])
    loc['LSDDATA'] = np.append(loc['LSDDATA'],loc['LSD_STOKESI'])
    loc['LSDDATA'] = np.append(loc['LSDDATA'],loc['LSD_STOKESI_MODEL'])
    loc['LSDDATA'] = np.append(loc['LSDDATA'],loc['LSD_STOKESVQU'])
    loc['LSDDATA'] = np.append(loc['LSDDATA'],loc['LSD_NULL'])

    # add LSD parameters keywords to header
    # add input parameters for LSD analysis
    hdict = spirouImage.AddKey(hdict, p['KW_POL_STOKES'], value=loc['STOKES'])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_MASK'],
                               value=p['IC_POLAR_LSD_CCFLINES'])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_V0'],
                               value=p['IC_POLAR_LSD_V0'])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_VF'],
                               value=p['IC_POLAR_LSD_VF'])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_NP'],
                               value=p['IC_POLAR_LSD_NP'])
                               
    # add fitted values from gaussian fit to Stokes I LSD
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_FIT_RV'],
                               value=loc['LSD_FIT_RV'])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_FIT_RESOL'],
                               value=loc['LSD_FIT_RESOL'])
                               
    # add information about the meaning of data columns
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_COL1'],
                               value=p['IC_POLAR_LSD_DATAINFO'][0])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_COL2'],
                               value=p['IC_POLAR_LSD_DATAINFO'][1])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_COL3'],
                               value=p['IC_POLAR_LSD_DATAINFO'][2])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_COL4'],
                               value=p['IC_POLAR_LSD_DATAINFO'][3])
    hdict = spirouImage.AddKey(hdict, p['kw_POL_LSD_COL5'],
                               value=p['IC_POLAR_LSD_DATAINFO'][4])

    # Store LSD analysis data in file
    spirouImage.WriteImage(lsdfits, loc['LSDDATA'], hdict)

    return lsdfits, lsdfitsfitsname

# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    print("SPIRou Least-Squares Deconvolution Module")

# =============================================================================
# End of code
# =============================================================================
