#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spirou keywords module

FITS rec header keywords (for reading headers and writing headers)

Created on 2017-10-30 at 16:37

@author: cook

Import rules: Only from spirouConfig
"""
from __future__ import division
import numpy as np

from . import spirouConfig


# =============================================================================
# Define program variables (do not change)
# =============================================================================
__NAME__ = 'spirouKeywords.py'
# Get version and author
__version__ = spirouConfig.Constants.VERSION()
__author__ = spirouConfig.Constants.AUTHORS()
__date__ = spirouConfig.Constants.LATEST_EDIT()
__release__ = spirouConfig.Constants.RELEASE()
# Get param dict
ParamDict = spirouConfig.ParamDict
# get default config file
p, _ = spirouConfig.read_config_file()
# get variables from spirouConst
p['DRS_NAME'] = spirouConfig.Constants.NAME()
p['DRS_VERSION'] = spirouConfig.Constants.VERSION()
p.set_sources(['DRS_NAME', 'DRS_VERSION'], 'spirouConfig.Constants')
# check input parameters
p = spirouConfig.check_params(p)


# =============================================================================
# Change these
# =============================================================================
# Keys must be deinfed here to be used (define as string)
#     run SpirouDRS.spirouConfig.test_keywords()
#     to test which variables are not currently in below list
# ---------------------------------------------------------------
# MUST UPDATE THIS IF VARIABLES ADDED
USE_KEYS = ['kw_ACQTIME_KEY',
            'kw_ACQTIME_KEY_JUL',
            'kw_AIRMASS',
            'kw_BADPFILE1',
            'kw_BADPFILE2',
            'kw_BBAD',
            'kw_BBFLAT',
            'kw_BERV',
            'kw_BERV_MAX',
            'kw_BHOT',
            'kw_BJD',
            'kw_BLAZFILE',
            'kw_BNDARK',
            'kw_BNFLAT',
            'kw_BNILUM',
            'kw_BTOT',
            'kw_BUNIT',
            'kw_CCAS',
            'kw_CCD_CONAD',
            'kw_CCD_SIGDET',
            'kw_CCF_CDELT',
            'kw_CCF_CONTRAST',
            'kw_CCF_CRVAL',
            'kw_CCF_CTYPE',
            'kw_CCF_FWHM',
            'kw_CCF_LINES',
            'kw_CCF_MASK',
            'kw_CCF_MAXCPP',
            'kw_CCF_RV',
            'kw_CCF_RVC',
            'kw_CDELT1',
            'kw_CDEN',
            'kw_CMMTSEQ',
            'kw_CREF',
            'kw_CRPIX1',
            'kw_CRVAL1',
            'kw_CTYPE1',
            'kw_DARKFILE',
            'kw_DARK_B_DEAD',
            'kw_DARK_B_MED',
            'kw_DARK_CUT',
            'kw_DARK_DEAD',
            'kw_DARK_MED',
            'kw_DARK_R_DEAD',
            'kw_DARK_R_MED',
            'kw_DATE_OBS',
            'kw_DPRTYPE',
            'kw_E2DS_EXTM',
            'kw_E2DS_FUNC',
            'kw_E2DS_SNR',
            'kw_EM_LOCFILE',
            'kw_EM_MAXWAVE',
            'kw_EM_MINWAVE',
            'kw_EM_TELLX',
            'kw_EM_TELLY',
            'kw_EM_TILT',
            'kw_EM_TRASCUT',
            'kw_EM_WAVE',
            'kw_EXPTIME',
            'kw_EXTFILE',
            'kw_EXTRA_SN',
            'kw_EXT_TYPE',
            'kw_FLATFILE',
            'kw_FLAT_RMS',
            'kw_FPFILE',
            'kw_GAIN',
            'kw_HCFILE',
            'kw_INFILE',
            'kw_LOCOFILE',
            'kw_LOCO_BCKGRD',
            'kw_LOCO_CTR_COEFF',
            'kw_LOCO_DEG_C',
            'kw_LOCO_DEG_E',
            'kw_LOCO_DEG_W',
            'kw_LOCO_DELTA',
            'kw_LOCO_FILE',
            'kw_LOCO_FWHM_COEFF',
            'kw_LOCO_NBO',
            'kw_LOC_MAXFLX',
            'kw_LOC_RMS_CTR',
            'kw_LOC_RMS_WID',
            'kw_LOC_SMAXPTS_CTR',
            'kw_LOC_SMAXPTS_WID',
            'kw_OBJDEC',
            'kw_OBJDECPM',
            'kw_OBJEQUIN',
            'kw_OBJNAME',
            'kw_OBJRA',
            'kw_OBJRAPM',
            'kw_OBSTYPE',
            'kw_OUTPUT',
            'kw_POL_EXPTIME',
            'kw_POL_ELAPTIME',
            'kw_POL_METHOD',
            'kw_POL_NEXP',
            'kw_POL_STOKES',
            'kw_POL_FILENAM1',
            'kw_POL_FILENAM2',
            'kw_POL_FILENAM3',
            'kw_POL_FILENAM4',
            'kw_POL_EXPTIME1',
            'kw_POL_EXPTIME2',
            'kw_POL_EXPTIME3',
            'kw_POL_EXPTIME4',
            'kw_POL_LSD_COL1',
            'kw_POL_LSD_COL2',
            'kw_POL_LSD_COL3',
            'kw_POL_LSD_COL4',
            'kw_POL_LSD_COL5',
            'kw_POL_LSD_FIT_RESOL',
            'kw_POL_LSD_FIT_RV',
            'kw_POL_LSD_MASK',
            'kw_POL_LSD_NP',
            'kw_POL_LSD_V0',
            'kw_POL_LSD_VF',
            'kw_POL_METHOD',
            'kw_POL_MJDATE1',
            'kw_POL_MJDATE2',
            'kw_POL_MJDATE3',
            'kw_POL_MJDATE4',
            'kw_POL_MJDEND1',
            'kw_POL_MJDEND2',
            'kw_POL_MJDEND3',
            'kw_POL_MJDEND4',
            'kw_POL_BJD1',
            'kw_POL_BJD2',
            'kw_POL_BJD3',
            'kw_POL_BJD4',
            'kw_POL_BERV1',
            'kw_POL_BERV2',
            'kw_POL_BERV3',
            'kw_POL_BERV4',
            'kw_POL_MEANBJD',
            'kw_POL_BJDCEN',
            'kw_POL_BERVCEN',
            'kw_POL_LSD_MASK',
            'kw_POL_LSD_V0',
            'kw_POL_LSD_VF',
            'kw_POL_LSD_NP',
            'kw_POL_LSD_FIT_RV',
            'kw_POL_LSD_FIT_RESOL',
            'kw_POL_LSD_COL1',
            'kw_POL_LSD_COL2',
            'kw_POL_LSD_COL3',
            'kw_POL_LSD_COL4',
            'kw_POL_LSD_COL5',
            'kw_POL_NEXP',
            'kw_POL_STOKES',
            'kw_RDNOISE',
            'kw_REFFILE',
            'kw_TELLU_ABSO',
            'kw_TELLU_AMP_PC',
            'kw_TELLU_DV_TELL1',
            'kw_TELLU_DV_TELL2',
            'kw_TH_NAXIS1',
            'kw_TH_NAXIS2',
            'kw_TILT',
            'kw_TILTFILE',
            'kw_UTC_OBS',
            'kw_WAVEFILE',
            'kw_WAVE_LL_DEG',
            'kw_WAVE_ORD_N',
            'kw_WAVE_PARAM',
            'kw_WAVE_TIME1',
            'kw_WAVE_TIME2',
            'kw_drs_QC',
            'kw_ppversion',
            'kw_root_drs_flat',
            'kw_root_drs_hc',
            'kw_root_drs_loc',
            'kw_version']


# MUST UPDATE THIS IF VARIABLES FROM CONFIG FILES USED
USE_PARAMS = ['DRS_NAME',
              'DRS_VERSION',
              'IC_IMAGE_TYPE',
              'IC_LOC_DELTA_WIDTH',
              'IC_LOCDFITC',
              'IC_LOCDFITP',
              'IC_LOCDFITW',
              'DARK_CUTLIMIT']

# load ICDP config file
try:
    p, _ = spirouConfig.load_config_from_file(p, key='ICDP_NAME', required=True,
                                              logthis=False)
except Exception:
    for param in USE_PARAMS:
        p[param] = '0'
# check that we have all parameters (do not change)
spirouConfig.check_config(p, USE_PARAMS)

# -----------------------------------------------------------------------------
# Variable definition
# -----------------------------------------------------------------------------
#   Note 1: Must be in form   variable = [string, #value, string]
#
#          where #value is any valid python object and string is any valid
#          python string
#
#   Note 2: for variable to be used in any code it must be defined in
#          "USE_KEYS"   above  as a string
#
#           i.e.   kw_x = ['TEST', 1.23, 'This is a test keyword']
#
#                   USE_KEYS = ['kw_x']
#
#            you can use the:
#
#            SpirouDRS.spirouConfig.SpirouKeywords.generate_use_keys()
#
#           to generate the list of USE_KEYS (will use all kw_ stored in file)
#
#
#   Note 2: This is NOT the best place to set values, these variables are
#           mainly used to add to a FITS rec header ONLY, #value can and will
#           be overwritten in the code
#
#   Note 3: Some keywords are just here to get data from the header only.
#           These should be commented but the #value will be set to None
#           to distinguish from header keywords that are put in the header
#
#   Note 4: You may use variables in the config files
#           (config.py, constants_SPIROU.py etc) located in the ../config
#           folder, however they should be placed as strings in USE_PARAMS
#
# -----------------------------------------------------------------------------
# Required header keys (main fits file)
# -----------------------------------------------------------------------------
# define the HEADER key for acquisition time (used to get value only)
#   in format YYYY-mm-dd-HH-MM-SS.ss
# TODO: This switch will be obsolete after H2RG testing is over
if p['IC_IMAGE_TYPE'] == 'H4RG':
    kw_ACQTIME_KEY = ['DATE', None, '']
else:
    kw_ACQTIME_KEY = ['ACQTIME1', None, '']

# define the HEADER key for acquisition time (used to get value only)
#   in unix time format (time since 1970-01-01-00-00-00)
# TODO: This switch will be obsolete after H2RG testing is over
if p['IC_IMAGE_TYPE'] == 'H4RG':
    kw_ACQTIME_KEY_JUL = ['MJDATE', None, '']
else:
    kw_ACQTIME_KEY_JUL = ['ACQTIME', None, '']

# define the observation date HEADER key
kw_DATE_OBS = ['DATE-OBS', None, '']

# define the observation time HEADER key
kw_UTC_OBS = ['UTC-OBS', None, '']

# define the observation ra HEADER key
kw_OBJRA = ['OBJRA', None, '']

# define the observation dec HEADER key
kw_OBJDEC = ['OBJDEC', None, '']

# define the observation name
kw_OBJNAME = ['OBJNAME', None, '']

# define the observation equinox HEADER key
kw_OBJEQUIN = ['OBJEQUIN', None, '']

# define the observation proper motion in ra HEADER key
kw_OBJRAPM = ['OBJRAPM', None, '']

# define the observation proper motion in dec HEADER key
kw_OBJDECPM = ['OBJDECPM', None, '']

# define the read noise HEADER key a.k.a sigdet (used to get value only)
kw_RDNOISE = ['RDNOISE', None, '']

# define the gain HEADER key (used to get value only)
kw_GAIN = ['GAIN', None, '']

# define the exposure time HEADER key (used to get value only)
kw_EXPTIME = ['EXPTIME', None, '']

# define the observation type HEADER key
kw_OBSTYPE = ['OBSTYPE', None, '']

# define the science fiber type HEADER key
kw_CCAS = ['SBCCAS_P', None, '']

# define the reference fiber type HEADER key
kw_CREF = ['SBCREF_P', None, '']

# define the density HEADER key
kw_CDEN = ['SBCDEN_P', None, '']

# define polarisation HEADER key
kw_CMMTSEQ = ['CMMTSEQ', None, '']

# define the airmass HEADER key
kw_AIRMASS = ['AIRMASS', None, '']

# -----------------------------------------------------------------------------
# Define general keywords
# -----------------------------------------------------------------------------
# DRS version
kw_version = ['VERSION', '{0}_{1}'.format(p['DRS_NAME'], p['DRS_VERSION']),
              'DRS version']

kw_ppversion = ['PVERSION', '{0}_{1}'.format(p['DRS_NAME'], p['DRS_VERSION']),
                'DRS Pre-Processing version']

# root keys (for use below and in finding keys later)
kw_root_drs_loc = ['LO', None, '']
kw_root_drs_flat = ['FF', None, '']
kw_root_drs_hc = ['LMP', None, '']

# Define the key to get the data fits file type
kw_DPRTYPE = ['DPRTYPE', None, 'The type of file (from pre-process)']

# -----------------------------------------------------------------------------
# Define cal_dark variables
# -----------------------------------------------------------------------------
# The fraction of dead pixels in the dark (in %)
kw_DARK_DEAD = ['DADEAD', 0, 'Fraction dead pixels [%]']

# The median dark level in ADU/s
kw_DARK_MED = ['DAMED', 0, 'median dark level [ADU/s]']

# The fraction of dead pixels in the blue part of the dark (in %)
kw_DARK_B_DEAD = ['DABDEAD', 0, 'Fraction dead pixels blue part [%]']

# The median dark level in the blue part of the dark in ADU/s
kw_DARK_B_MED = ['DABMED', 0, 'median dark level blue part [ADU/s]']

# The fraction of dead pixels in the red part of the dark (in %)
kw_DARK_R_DEAD = ['DARDEAD', 0, 'Fraction dead pixels red part [%]']

# The median dark level in the red part of the dark in ADU/s
kw_DARK_R_MED = ['DARMED', 0, 'median dark level red part [ADU/s]']

# The threshold of the dark level to retain in ADU
kw_DARK_CUT = ['DACUT', p['DARK_CUTLIMIT'],
               'Threshold of dark level retain [ADU/s]']

# -----------------------------------------------------------------------------
# Define cal_LOC variables
# -----------------------------------------------------------------------------

# Mean background (as percentage)
kw_LOCO_BCKGRD = [kw_root_drs_loc[0] + 'BCKGRD', 0, 'mean background [%]']

# Image conversion factor [e-/ADU]
kw_CCD_CONAD = ['CONAD', 0, 'CCD conv factor [e-/ADU]']

# Image readout noise
kw_CCD_SIGDET = ['SIGDET', 0, 'CCD Readout Noise [e-]']

# Coeff center order
kw_LOCO_CTR_COEFF = [kw_root_drs_loc[0] + 'CTR', 0, 'Coeff center']

# fit degree for order centers
kw_LOCO_DEG_C = [kw_root_drs_loc[0] + 'DEGCTR',  p['IC_LOCDFITC'],
                 'degree fit ctr ord']

# fit degree for order widths
kw_LOCO_DEG_W = [kw_root_drs_loc[0] + 'DEGFWH', p['IC_LOCDFITW'],
                 'degree fit width ord']

# fit degree for profile error
kw_LOCO_DEG_E = [kw_root_drs_loc[0] + 'DEGERR', p['IC_LOCDFITP'],
                 'degree fit profile error']

# delta width (pix) for 3 convol shape model (currently not used??)
kw_LOCO_DELTA = [kw_root_drs_loc[0] + 'PRODEL', p['IC_LOC_DELTA_WIDTH'],
                 'param model 3gau']

# Coeff width order
kw_LOCO_FWHM_COEFF = [kw_root_drs_loc[0] + 'FW', 0, 'Coeff fwhm']

# Number of orders located
kw_LOCO_NBO = [kw_root_drs_loc[0] + 'NBO', 0, 'nb orders localised']

# Maximum flux in order
kw_LOC_MAXFLX = [kw_root_drs_loc[0] + 'FLXMAX', 0, 'max flux in order [ADU]']

# Maximum number of removed points allowed for location fit
kw_LOC_SMAXPTS_CTR = [kw_root_drs_loc[0] + 'CTRMAX', 0, 'max rm pts ctr']

# Maximum number of removed points allowed for width fit
#    (formally kw_LOC_Smaxpts_width)
kw_LOC_SMAXPTS_WID = [kw_root_drs_loc[0] + 'WIDMAX', 0, 'max rm pts width']

# Maximum rms allowed for location fit
kw_LOC_RMS_CTR = [kw_root_drs_loc[0] + 'RMSCTR', 0, 'max rms ctr']

# Maximum rms allowed for width fit (formally kw_LOC_rms_fwhm)
kw_LOC_RMS_WID = [kw_root_drs_loc[0] + 'RMSWID', 0, 'max rms width']

# -----------------------------------------------------------------------------
# Define cal_SLIT variables
# -----------------------------------------------------------------------------
# Tilt order keyword prefix
kw_TILT = [kw_root_drs_loc[0] + 'TILT', 0, 'Tilt order']

# -----------------------------------------------------------------------------
# Define cal_FF variables
# -----------------------------------------------------------------------------

# Signal to noise ratio for order center
kw_EXTRA_SN = ['EXTSN', 0, 'S_N order center']

# Flat field RMS for order
kw_FLAT_RMS = [kw_root_drs_flat[0] + 'RMS', 0, 'FF RMS order']

# -----------------------------------------------------------------------------
# Define cal_EXTRACT variables
# -----------------------------------------------------------------------------
# TODO: Comment this section
# localization file used
kw_LOCO_FILE = [kw_root_drs_loc[0] + 'FILE', '', 'Localization file used']

kw_E2DS_EXTM = ['EXTMETH', '', 'Extraction method']

kw_E2DS_FUNC = ['EXTFUNC', '', 'Extraction function']

kw_E2DS_SNR = ['SNR', 0, 'Signal to Noise Ratio']

kw_WAVE_TIME1 = ['WAVET1', 0, 'Wave file date+time human']
kw_WAVE_TIME2 = ['WAVET2', 0, 'Wave file date+time unix']

kw_CRPIX1 = ['CRPIX1', 0, 'Reference pixel']
kw_CRVAL1 = ['CRVAL1', 0, 'Coordinate at reference pixel [nm]']
kw_CDELT1 = ['CDELT1', 0, 'Coordinate at reference pixel [nm]']
kw_CTYPE1 = ['CTYPE1', 'nm', 'Units of coordinate']
kw_BUNIT = ['BUNIT', '', 'Units of data values']

# -----------------------------------------------------------------------------
# Define cal_BADPIX variables
# -----------------------------------------------------------------------------
# fraction of hot pixels
kw_BHOT = ['BHOT', 0, 'Frac of hot px [%]']

# fraction of bad pixels from flat
kw_BBFLAT = ['BBFLAT', 0, 'Frac of bad px from flat [%]']

# fraction of non-finite pixels in dark
kw_BNDARK = ['BNDARK', 0, 'Frac of non-finite px in dark [%]']

# fraction of non-finite pixels in flat
kw_BNFLAT = ['BNFLAT', 0, 'Frac of non-finite px in flat [%]']

# fraction of bad pixels with all criteria
kw_BBAD = ['BBAD', 0, 'Frac of bad px with all criteria [%]']

# fraction of un-illuminated pixels (from engineering flat)
kw_BNILUM = ['BNILUM', 0, 'Frac of un-illuminated pixels [%]']

# fraction of total bad pixels
kw_BTOT = ['BTOT', 0, 'Frac of bad pixels (total) [%]']

# -----------------------------------------------------------------------------
# Define cal_CCF variables
# -----------------------------------------------------------------------------
# TODO: Comment this section
kw_CCF_CTYPE = ['CTYPE1', '', 'Pixel coordinate system']
kw_CCF_CRVAL = ['CRVAL1', 0, 'Value of ref pixel']
kw_CCF_CDELT = ['CDELT1', 0, 'CCF steps [km/s]']
kw_CCF_RV = ['CCFRV', 0, 'Baryc RV (no drift correction) (km/s)']
kw_CCF_RVC = ['CCFRVC', 0, 'Baryc RV (drift corrected) (km/s) ']
kw_CCF_FWHM = ['CCFFWHM', 0, 'FWHM of CCF (km/s)']
kw_CCF_CONTRAST = ['CCFCONTR', 0, 'Contrast of  CCF (%)']
kw_CCF_MAXCPP = ['CCFMACPP', 0, 'max count/pixel of CCF (e-)']
kw_CCF_MASK = ['CCFMASK', 0, 'Mask filename']
kw_CCF_LINES = ['CCFLINES', 0, 'nbr of lines used']
kw_BERV = ['BERV', 0, 'Barycorrpy BC Velocity']
kw_BJD = ['BJD', 0, 'Barycorrpy BJD']
kw_BERV_MAX = ['BERVMAX', 0, 'Barycorrpy Max BC Velocity']


# -----------------------------------------------------------------------------
# Define wave variables
# -----------------------------------------------------------------------------
# the number of orders used in the TH line list                        [WAVE_AB]
kw_WAVE_ORD_N = ['TH_ORD_N', None, 'nb orders in total']

# the number of fit coefficients from the TH line list fit             [WAVE_AB]
kw_WAVE_LL_DEG = ['TH_LL_D', None, 'deg polyn fit ll(x,order)']

# the prefix to use to get the TH line list fit coefficients           [WAVE_AB]
kw_WAVE_PARAM = ['TH_LC', None, 'coeff ll(x,order)']

# the x-axis dimension size for the TH line list file                  [WAVE_AB]
kw_TH_NAXIS1 = ['NAXIS1', None, '']

# the y-axis dimension size for the TH line list file                  [WAVE_AB]
kw_TH_NAXIS2 = ['NAXIS2', None, '']


# -----------------------------------------------------------------------------
# Define telluric variables
# -----------------------------------------------------------------------------
# Telluric absorption prefix (i.e. ABSO_H20)                     [OBJ_FIT_TELLU]
kw_TELLU_ABSO = ['ABSO', None, 'Absorption key prefix']

# Telluric principle component amplitudes (for use with 1D list)
kw_TELLU_AMP_PC = ['AMP_PC', None, 'Principle Component Amplitudes']

# Telluric principle component derivatives
kw_TELLU_DV_TELL1 = ['DV_TELL1', None, 'Principle Component first der.']
kw_TELLU_DV_TELL2 = ['DV_TELL2', None, 'Principle Component second der.']

# -----------------------------------------------------------------------------
# Define polarimetry variables
# -----------------------------------------------------------------------------
# TODO: Comment this section
kw_POL_STOKES = ['STOKES', '', 'Stokes paremeter: Q, U, V, or I']
kw_POL_NEXP = ['POLNEXP', '', 'Number of exposures for polarimetry']
kw_POL_METHOD = ['POLMETHO', '', 'Polarimetry method']
kw_POL_EXPTIME = ['TOTETIME', '', 'Total exposure time (sec)']
kw_POL_ELAPTIME = ['ELAPTIME', '', 'Elapsed time of observation (sec)']
kw_POL_FILENAM1 = ['FILENAM1', '', 'Base filename of exposure 1']
kw_POL_FILENAM2 = ['FILENAM2', '', 'Base filename of exposure 2']
kw_POL_FILENAM3 = ['FILENAM3', '', 'Base filename of exposure 3']
kw_POL_FILENAM4 = ['FILENAM4', '', 'Base filename of exposure 4']
kw_POL_EXPTIME1 = ['EXPTIME1', '', 'EXPTIME of exposure 1 (sec)']
kw_POL_EXPTIME2 = ['EXPTIME2', '', 'EXPTIME of exposure 2 (sec)']
kw_POL_EXPTIME3 = ['EXPTIME3', '', 'EXPTIME of exposure 3 (sec)']
kw_POL_EXPTIME4 = ['EXPTIME4', '', 'EXPTIME of exposure 4 (sec)']
kw_POL_MJDATE1 = ['MJDATE1', '', 'MJD at start of exposure 1']
kw_POL_MJDATE2 = ['MJDATE2', '', 'MJD at start of exposure 2']
kw_POL_MJDATE3 = ['MJDATE3', '', 'MJD at start of exposure 3']
kw_POL_MJDATE4 = ['MJDATE4', '', 'MJD at start of exposure 4']
kw_POL_MJDEND1 = ['MJDEND1', '', 'MJDEND at end of exposure 1']
kw_POL_MJDEND2 = ['MJDEND2', '', 'MJDEND at end of exposure 2']
kw_POL_MJDEND3 = ['MJDEND3', '', 'MJDEND at end of exposure 3']
kw_POL_MJDEND4 = ['MJDEND4', '', 'MJDEND at end of exposure 4']
kw_POL_BJD1 = ['BJD1', '', 'BJD at start of exposure 1']
kw_POL_BJD2 = ['BJD2', '', 'BJD at start of exposure 2']
kw_POL_BJD3 = ['BJD3', '', 'BJD at start of exposure 3']
kw_POL_BJD4 = ['BJD4', '', 'BJD at start of exposure 4']
kw_POL_BERV1 = ['BERV1', '', 'BERV at start of exposure 1']
kw_POL_BERV2 = ['BERV2', '', 'BERV at start of exposure 2']
kw_POL_BERV3 = ['BERV3', '', 'BERV at start of exposure 3']
kw_POL_BERV4 = ['BERV4', '', 'BERV at start of exposure 4']
kw_POL_MEANBJD = ['MEANBJD', '', 'Mean BJD for polar sequence']
kw_POL_BJDCEN = ['BJDCEN', '', 'BJD at center of observation']
kw_POL_BERVCEN = ['BERVCEN', '', 'BERV at center of observation']
kw_POL_LSD_MASK = ['LSDMASK', '', 'LSD mask filename']
kw_POL_LSD_V0 = ['LSDV0', '', 'Initial velocity (km/s) for LSD profile']
kw_POL_LSD_VF = ['LSDVF', '', 'Final velocity (km/s) for LSD profile']
kw_POL_LSD_NP = ['LSDNP', '', 'Number of points for LSD profile']
kw_POL_LSD_FIT_RV = ['LSDFITRV', '', 'Radial velocity (km/s) from gaussian fit']
kw_POL_LSD_FIT_RESOL = ['LSDRESOL', '', 'Resolving power from gaussian fit']
kw_POL_LSD_COL1 = ['LSDCOL1', '', 'Velocities (km/s)']
kw_POL_LSD_COL2 = ['LSDCOL2', '', 'Stokes I LSD profile']
kw_POL_LSD_COL3 = ['LSDCOL3', '', 'Gaussian fit to Stokes I LSD profile']
kw_POL_LSD_COL4 = ['LSDCOL4', '', 'Stokes V, U, or Q LSD profile']
kw_POL_LSD_COL5 = ['LSDCOL5', '', 'Null polarization LSD profile']

# -----------------------------------------------------------------------------
# Define cal_exposure_meter variables
# -----------------------------------------------------------------------------
# TODO: Comment this section
kw_EM_TELLX = ['TELL_X', 0.0, 'Telluric x file used (wavelengths)']
kw_EM_TELLY = ['TELL_Y', 0.0, 'Telluric y file used (transmission)']
kw_EM_LOCFILE = ['LOCFILE', 0.0, 'Loc file used (cent+fwhm fits)']
kw_EM_WAVE = ['WAVEFILE', 0.0, 'Wavelength solution file used']
kw_EM_TILT = ['TILTFILE', 0.0, 'Tilt solution file used']
kw_EM_MINWAVE = ['MINLAM', 0.0, 'Minimum lambda used in mask [nm]']
kw_EM_MAXWAVE = ['MAXLAM', 0.0, 'Maximum lambda used in mask [nm]']
kw_EM_TRASCUT = ['TRANSCUT', 0.0, 'Minimum transmission used in mask']


# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
kw_drs_QC = ['QC', 'PASSED', 'QCcontr']


# -----------------------------------------------------------------------------
# Define output
# -----------------------------------------------------------------------------
kw_DARKFILE = ['DARKFILE', '', 'DARK_DARK file used for correction']
kw_BADPFILE1 = ['BADFILE1', '', 'FLAT_FLAT file used for BADPIX corr']
kw_BADPFILE2 = ['BADFILE2', '', 'DARK_DARK file used for BADPIX corr']
kw_LOCOFILE = ['LOCOFILE', '', 'DARK_FLAT/FLAT_DARK file used for localisation']
kw_TILTFILE = ['TILTFILE', '', 'FP_FP file use for TILT']
kw_BLAZFILE = ['BLAZFILE', '', 'FLAT_FLAT file used for blaze file']
kw_FLATFILE = ['FLATFILE', '', 'FLAT_FLAT file used for flat file']
kw_EXTFILE = ['EXTRFILE', '', 'Input file used to create extraction']
kw_REFFILE = ['REFRFILE', '', 'Reference file used to create drift file']
kw_WAVEFILE = ['WAVEFILE', 0.0, 'Wavelength solution file used']
kw_INFILE = ['INFILE', '', 'Input file userd to create output']
kw_HCFILE = ['HCFILE', '', 'HC file used to create output']
kw_FPFILE = ['FPFILE', '', 'FP file used to create output']

kw_OUTPUT = ['DRSOUTID', '', 'DRS output identification code']
kw_EXT_TYPE = ['DRS_EOUT', '', 'DRS Extraction input DPRTYPE']


# =============================================================================
# Define functions (Do not change)
# =============================================================================
def test_keywords():
    """
    Test which keys are in USE_KEYS (prints warnings about these keys)

    :return None:
    """
    for key in locals():
        if key not in USE_KEYS:
            print('WARNING: key={0} not in USE_KEYS')


def generate_use_keys():
    """
    Generate sorted USE_KEYS list from all variables in the memory with
    'kw_' prefix. Note should have a fresh python instance running to avoid
    unwanted variables. Only for use in creating the list USE_KEYS for this
    code!

    :return use_keys: list of strings, list of all keys with 'kw_' in their name
    """
    all_locals = np.sort(list(globals().keys()))
    use_keys = []
    for lkey in all_locals:
        if 'kw_' in lkey:
            use_keys.append(lkey)
    return use_keys


def get_keywords(pp=None):
    """
    Get keywords defined in spirouKeywords.USE_KEYS
    (must be named exactly as in USE_KEYS list)

    :param pp: parameter dictionary or None, if not None then keywords are added
               to the specified ParamDict else a new ParamDict is created

    :return pp: if pp is None returns a new dictionary of keywords
                else adds USE_KEYS as keys with value = eval(key)
    """
    # if we have no previous dictionary create it
    if pp is None:
        pp = ParamDict()
    # loop around each key in USE_KEY
    warnlog = []
    for key in USE_KEYS:
        try:
            # try to evaluate key (will throw NameError if it doesn't exist)
            value = eval(key)
        except NameError:
            # Catch the NameError and throw ConfigError (for log)
            emsg = ('The value {0} in USE_KEYS is not matched by a '
                    'variable in {1}. Please check.')
            eargs = [key, __NAME__]
            raise spirouConfig.ConfigError(emsg.format(*eargs), level='error')
        # check that keyword is a list and define properly
        #  format should be: [string, object, string]
        check_keyword_format(key, value)
        # warn if we are overwritting previous key
        if key in pp:
            wmsg = 'Warning key {0} from {1} overwritten in {2}'
            warnlog.append(wmsg.format(key, pp.get_source(key), __NAME__))
        # finally add to dictionary
        pp[key] = value
        # add source
        pp.set_source(key, __NAME__)
    # return pp and warning log
    return pp, warnlog


def check_keyword_format(key, value):
    """
    Checks that the format of each keyword is correct and generates a
    ConfigError if incorrect

    format must be [string, value, string]
                   [name, value, comment]

    :param key: string, keyword key to test
    :param value: object, object to test format

    :return None:
    """
    if type(value) != list:
        emsg = 'Key {0} defined in {1} is not a list. Please check'
        raise spirouConfig.ConfigError(emsg.format(key, __NAME__),
                                       level='error')
    # value must be a list of length 3
    if len(value) != 3:
        emsg = 'key {0} defined in {1} is not a length 3 list (len={2})'
        raise spirouConfig.ConfigError(emsg.format(key, __NAME__, len(value)),
                                       level='error')
    # value[0] and value[2] must be strings
    if type(value[0]) != str or type(value[2]) != str:
        emsg1 = 'key {0} defined in {1} is not in form:'.format(key, __NAME__)
        emsg2 = '    [string, #value, string]'
        emsg3 = ('    where #value is any value and string is any valid python'
                 ' string object.')
        raise spirouConfig.ConfigError([emsg1, emsg2, emsg3], level='error')


def get_keyword_values_from_header(pp, hdict, keys, filename=None):
    """
    Gets a keyword or keywords from a header or dictionary

    :param pp: parameter dictionary, ParamDict containing constants
                if "key" (element in "keys") is in pp and it is a
                keyword list then this is used as the key instead of "key"

    :param hdict: dictionary, raw dictionary or FITS rec header file containing
                  all the keys in "keys" (spirouConfig.ConfigError raised if
                  any key does not exist)
    :param keys: list of strings or list of lists, the keys to find in "hdict"
                 OR a list of keyword lists ([key, value, comment])
    :param filename: string or None, if defined when an error is caught the
                     filename is logged, this filename should be where the
                     fits rec header is from (or where the dictionary was
                     compiled from) - if not from a file this should be left
                     as None

    :return values: list, the values in the header for the keys
                    (size = len(keys))
    """
    # deal with a non-list set of keys
    if type(keys) not in [list, np.ndarray]:
        keys = [keys]

    # try to get values
    values = []
    for key in keys:
        # see if key is a keyword list
        if key in pp:
            if type(pp[key]) in [list, np.ndarray]:
                key = pp[key][0]
        # try to get key from hdict
        try:
            values.append(hdict[key])
        # if we cannot find the key then raise a config error
        except ValueError:
            if filename is not None:
                emsg = 'key "{0}" is required in the HEADER of file {1}'
                eargs = [key, filename]
            else:
                emsg = 'key "{0}" is required in the "hdict"'
                eargs = [key]
            raise spirouConfig.ConfigError(emsg.format(*eargs), level='error')
    # return values
    return values


# =============================================================================
# End of code
# =============================================================================
