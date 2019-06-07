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
USE_KEYS = ['KW_ACQTIME',
            'KW_ACQTIME_DTYPE',
            'KW_ACQTIME_FMT',
            'KW_AIRMASS',
            'KW_BBAD',
            'KW_BBFLAT',
            'KW_BERV', 'KW_BERV_EST',
            'KW_BERV_MAX', 'KW_BERV_MAX_EST',
            'KW_BERV_SOURCE',
            'KW_BHOT',
            'KW_BJD', 'KW_BJD_EST',
            'KW_BNDARK',
            'KW_BNFLAT',
            'KW_BNILUM',
            'KW_BTOT',
            'KW_BUNIT',
            'KW_B_OBS_HOUR',
            'KW_CCAS',
            'KW_CCD_CONAD',
            'KW_CCD_SIGDET',
            'KW_CCF_CDELT',
            'KW_CCF_CONTRAST',
            'KW_CCF_CRVAL',
            'KW_CCF_CTYPE',
            'KW_CCF_FWHM',
            'KW_CCF_LINES',
            'KW_CCF_MASK',
            'KW_CCF_MAXCPP',
            'KW_CCF_RV',
            'KW_CCF_RVC',
            'KW_CCF_WMREF',
            'KW_CCF_RVNOISE',
            'KW_CCF_TELL',
            'KW_CDBBAD',
            'KW_CDBBACK',
            'KW_CDBBLAZE',
            'KW_CDBDARK',
            'KW_CDBFLAT',
            'KW_CDBLOCO',
            'KW_CDBORDP',
            'KW_CDBSHAPE',
            'KW_CDBSHAPEX',
            'KW_CDBSHAPEY',
            'KW_CDBTILT',
            'KW_CDBWAVE',
            'KW_CDELT1',
            'KW_CDEN',
            'KW_CMMTSEQ',
            'KW_CMPLTEXP',
            'KW_CREF',
            'KW_CRPIX1',
            'KW_CRVAL1',
            'KW_CTYPE1',
            'KW_DARK_B_DEAD',
            'KW_DARK_B_MED',
            'KW_DARK_CUT',
            'KW_DARK_DEAD',
            'KW_DARK_MED',
            'KW_DARK_R_DEAD',
            'KW_DARK_R_MED',
            'KW_DATE_OBS',
            'KW_DPRTYPE',
            'KW_DRIFT_RV',
            'KW_DRS_QC',
            'KW_DRS_QC_LOGIC',
            'KW_DRS_QC_NAME',
            'KW_DRS_QC_PASS',
            'KW_DRS_QC_VAL',
            'KW_E2DS_EXTM',
            'KW_E2DS_FUNC',
            'KW_E2DS_SNR',
            'KW_EM_LOCFILE',
            'KW_EM_MAXWAVE',
            'KW_EM_MINWAVE',
            'KW_EM_TELLX',
            'KW_EM_TELLY',
            'KW_EM_TILT',
            'KW_EM_TRASCUT',
            'KW_EM_WAVE',
            'KW_EXPTIME',
            'KW_EXTRA_SN',
            'KW_EXT_TYPE',
            'KW_FLAT_RMS',
            'KW_GAIN',
            'KW_INCCFMASK',
            'KW_INFILE1',
            'KW_INFILE2',
            'KW_INFILE3',
            'KW_INRV',
            'KW_INSTEP',
            'KW_INWIDTH',
            'KW_LOCO_BCKGRD',
            'KW_LOCO_CTR_COEFF',
            'KW_LOCO_DEG_C',
            'KW_LOCO_DEG_E',
            'KW_LOCO_DEG_W',
            'KW_LOCO_DELTA',
            'KW_LOCO_FILE',
            'KW_LOCO_FWHM_COEFF',
            'KW_LOCO_NBO',
            'KW_LOC_MAXFLX',
            'KW_LOC_RMS_CTR',
            'KW_LOC_RMS_WID',
            'KW_LOC_SMAXPTS_CTR',
            'KW_LOC_SMAXPTS_WID',
            'KW_MJDEND',
            'KW_NEXP',
            'KW_OBJBERVLIST',
            'KW_OBJDEC',
            'KW_OBJDECPM',
            'KW_OBJECT',
            'KW_OBJEQUIN',
            'KW_OBJFILELIST',
            'KW_OBJNAME',
            'KW_OBJRA',
            'KW_OBJRAPM',
            'KW_OBJWAVELIST',
            'KW_OBSTYPE',
            'KW_OUTPUT',
            'KW_PID',
            'KW_POL_BERV1',
            'KW_POL_BERV2',
            'KW_POL_BERV3',
            'KW_POL_BERV4',
            'KW_POL_BERVCEN',
            'KW_POL_BJD1',
            'KW_POL_BJD2',
            'KW_POL_BJD3',
            'KW_POL_BJD4',
            'KW_POL_BJDCEN',
            'KW_POL_ELAPTIME',
            'KW_POL_EXPTIME',
            'KW_POL_EXPTIME1',
            'KW_POL_EXPTIME2',
            'KW_POL_EXPTIME3',
            'KW_POL_EXPTIME4',
            'KW_POL_FILENAM1',
            'KW_POL_FILENAM2',
            'KW_POL_FILENAM3',
            'KW_POL_FILENAM4',
            'KW_POL_LSD_COL1',
            'KW_POL_LSD_COL2',
            'KW_POL_LSD_COL3',
            'KW_POL_LSD_COL4',
            'KW_POL_LSD_COL5',
            'KW_POL_LSD_FIT_RESOL',
            'KW_POL_LSD_FIT_RV',
            'KW_POL_LSD_MASK',
            'KW_POL_LSD_MEANPOL',
            'KW_POL_LSD_MEDABSDEVPOL',
            'KW_POL_LSD_MEDIANPOL',
            'KW_POL_LSD_NP',
            'KW_POL_LSD_NULL_MEAN',
            'KW_POL_LSD_NULL_STDDEV',
            'KW_POL_LSD_STDDEVPOL',
            'KW_POL_LSD_STOKESVQU_MEAN',
            'KW_POL_LSD_STOKESVQU_STDDEV',
            'KW_POL_LSD_V0',
            'KW_POL_LSD_VF',
            'KW_POL_MEANBJD',
            'KW_POL_METHOD',
            'KW_POL_MJDATE1',
            'KW_POL_MJDATE2',
            'KW_POL_MJDATE3',
            'KW_POL_MJDATE4',
            'KW_POL_MJDCEN',
            'KW_POL_MJDEND1',
            'KW_POL_MJDEND2',
            'KW_POL_MJDEND3',
            'KW_POL_MJDEND4',
            'KW_POL_NEXP',
            'KW_POL_STOKES',
            'KW_RDNOISE',
            'KW_REFFILE',
            'KW_REF_RV',
            'KW_TDBMAP',
            'KW_TDBOBJ',
            'KW_TDBRECON',
            'KW_TDBTEMP',
            'KW_TELLU_ABSO',
            'KW_TELLU_ADD_DPC',
            'KW_TELLU_AIRMASS',
            'KW_TELLU_AMP_PC',
            'KW_TELLU_DV_TELL1',
            'KW_TELLU_DV_TELL2',
            'KW_TELLU_FIT_DPC',
            'KW_TELLU_NPC',
            'KW_TELLU_WATER',
            'KW_TH_NAXIS1',
            'KW_TH_NAXIS2',
            'KW_WFP_DRIFT',
            'KW_WFP_FWHM',
            'KW_WFP_CONTRAST',
            'KW_WFP_MAXCPP',
            'KW_WFP_MASK',
            'KW_WFP_LINES',
            'KW_WFP_TARG_RV',
            'KW_WFP_WIDTH',
            'KW_WFP_STEP',
            'KW_WFP_FILE',
            'KW_TILT',
            'KW_UTC_OBS',
            'KW_WAVESOURCE',
            'KW_WAVE_CODE',
            'KW_WAVE_INIT',
            'KW_WAVE_LL_DEG',
            'KW_WAVE_ORD_N',
            'KW_WAVE_PARAM',
            'KW_WAVE_TIME1',
            'KW_WAVE_TIME2',
            'KW_PPVERSION',
            'KW_root_drs_flat',
            'KW_root_drs_hc',
            'KW_root_drs_loc',
            'KW_VERSION',
            'KW_WEATHER_TOWER_TEMP',
            'KW_CASS_TEMP',
            'KW_HUMIDITY',
            'KW_DRS_DATE',
            'KW_DATE_NOW',
            'KW_FIBER'
            ]

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
# noinspection PyBroadException
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
#           i.e.   KW_x = ['TEST', 1.23, 'This is a test keyword']
#
#                   USE_KEYS = ['KW_x']
#
#            you can use the:
#
#            SpirouDRS.spirouConfig.SpirouKeywords.generate_use_keys()
#
#           to generate the list of USE_KEYS (will use all KW_ stored in file)
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
# define the HEADER key for acquisition time
#     Note must set the date format in KW_ACQTIME_FMT
KW_ACQTIME = ['MJDATE', None, '']

# the format of ACQTIME as required by astropy.time
#  options are:
#          "mjd": mean julian date
#          "iso": YYYY-MM-DD HH:MM:SS.S
#          "unix": seconds since 1970-01-01 00:00:00
#          "jyear": year as a decimal number
KW_ACQTIME_FMT = ['mjd', None, '']
KW_ACQTIME_DTYPE = ['dtype', float, '']

# define the observation date HEADER key
KW_DATE_OBS = ['DATE-OBS', None, '']

# define the observation time HEADER key
KW_UTC_OBS = ['UTC-OBS', None, '']

# define the observation ra HEADER key
KW_OBJRA = ['OBJRA', None, '']

# define the observation dec HEADER key
KW_OBJDEC = ['OBJDEC', None, '']

# define the observation name
KW_OBJNAME = ['OBJNAME', None, '']

# define the observation name from "go"
KW_OBJECT = ['OBJECT', None, '']

# define the observation equinox HEADER key
KW_OBJEQUIN = ['OBJEQUIN', None, '']

# define the observation proper motion in ra HEADER key
KW_OBJRAPM = ['OBJRAPM', None, '']

# define the observation proper motion in dec HEADER key
KW_OBJDECPM = ['OBJDECPM', None, '']

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KW_RDNOISE = ['RDNOISE', None, '']

# define the gain HEADER key (used to get value only)
KW_GAIN = ['GAIN', None, '']

# define the exposure time HEADER key (used to get value only)
KW_EXPTIME = ['EXPTIME', None, '']

# define the observation type HEADER key
KW_OBSTYPE = ['OBSTYPE', None, '']

# define the science fiber type HEADER key
KW_CCAS = ['SBCCAS_P', None, '']

# define the reference fiber type HEADER key
KW_CREF = ['SBCREF_P', None, '']

# define the density HEADER key
KW_CDEN = ['SBCDEN_P', None, '']

# define polarisation HEADER key
KW_CMMTSEQ = ['CMMTSEQ', None, '']

# define the airmass HEADER key
KW_AIRMASS = ['AIRMASS', None, '']

# define the MJ end date HEADER key
KW_MJDEND = ['MJDEND', None, '']

# define the exposure number within sequence HEADER key
KW_CMPLTEXP = ['CMPLTEXP', None, '']

# define the total number of exposures HEADER key
KW_NEXP = ['NEXP', None, '']

# define the weather tower temperature HEADER key
KW_WEATHER_TOWER_TEMP = ['TEMPERAT', None, '']

# define the cassegrain temperature HEADER key
KW_CASS_TEMP = ['SB_POL_T', None, '']

# define the humidity temperature HEADER key
KW_HUMIDITY = ['RELHUMID', None, '']

# -----------------------------------------------------------------------------
# Define general keywords
# -----------------------------------------------------------------------------
# DRS version
KW_VERSION = ['VERSION', '{0}_{1}'.format(p['DRS_NAME'], p['DRS_VERSION']),
              'DRS version']

# the preprocessed DRS version
KW_PPVERSION = ['PVERSION', '{0}_{1}'.format(p['DRS_NAME'], p['DRS_VERSION']),
                'DRS Pre-Processing version']

# the release date of the DRS
KW_DRS_DATE = ['DRSVDATE', '', 'DRS Release date']

# The date when processed
KW_DATE_NOW = ['DRSPDATE', '', 'DRS Processed date']

# DRS Process ID
KW_PID = ['DRSPID', '', 'The process ID that outputted this file.']

# root keys (for use below and in finding keys later)
KW_root_drs_loc = ['LO', None, '']
KW_root_drs_flat = ['FF', None, '']
KW_root_drs_hc = ['LMP', None, '']

# Define the key to get the data fits file type
KW_DPRTYPE = ['DPRTYPE', None, 'The type of file (from pre-process)']

# define fiber type in header keywords
KW_FIBER = ['FIBER', None, 'The fiber associated with this file']

# -----------------------------------------------------------------------------
# Define cal_dark variables
# -----------------------------------------------------------------------------
# The fraction of dead pixels in the dark (in %)
KW_DARK_DEAD = ['DADEAD', 0, 'Fraction dead pixels [%]']

# The median dark level in ADU/s
KW_DARK_MED = ['DAMED', 0, 'median dark level [ADU/s]']

# The fraction of dead pixels in the blue part of the dark (in %)
KW_DARK_B_DEAD = ['DABDEAD', 0, 'Fraction dead pixels blue part [%]']

# The median dark level in the blue part of the dark in ADU/s
KW_DARK_B_MED = ['DABMED', 0, 'median dark level blue part [ADU/s]']

# The fraction of dead pixels in the red part of the dark (in %)
KW_DARK_R_DEAD = ['DARDEAD', 0, 'Fraction dead pixels red part [%]']

# The median dark level in the red part of the dark in ADU/s
KW_DARK_R_MED = ['DARMED', 0, 'median dark level red part [ADU/s]']

# The threshold of the dark level to retain in ADU
KW_DARK_CUT = ['DACUT', p['DARK_CUTLIMIT'],
               'Threshold of dark level retain [ADU/s]']

# -----------------------------------------------------------------------------
# Define cal_LOC variables
# -----------------------------------------------------------------------------

# Mean background (as percentage)
KW_LOCO_BCKGRD = [KW_root_drs_loc[0] + 'BCKGRD', 0, 'mean background [%]']

# Image conversion factor [e-/ADU]
KW_CCD_CONAD = ['CONAD', 0, 'CCD conv factor [e-/ADU]']

# Image readout noise
KW_CCD_SIGDET = ['SIGDET', 0, 'CCD Readout Noise [e-]']

# Coeff center order
KW_LOCO_CTR_COEFF = [KW_root_drs_loc[0] + 'CTR', 0, 'Coeff center']

# fit degree for order centers
KW_LOCO_DEG_C = [KW_root_drs_loc[0] + 'DEGCTR', p['IC_LOCDFITC'],
                 'degree fit ctr ord']

# fit degree for order widths
KW_LOCO_DEG_W = [KW_root_drs_loc[0] + 'DEGFWH', p['IC_LOCDFITW'],
                 'degree fit width ord']

# fit degree for profile error
KW_LOCO_DEG_E = [KW_root_drs_loc[0] + 'DEGERR', p['IC_LOCDFITP'],
                 'degree fit profile error']

# delta width (pix) for 3 convol shape model (currently not used??)
KW_LOCO_DELTA = [KW_root_drs_loc[0] + 'PRODEL', p['IC_LOC_DELTA_WIDTH'],
                 'param model 3gau']

# Coeff width order
KW_LOCO_FWHM_COEFF = [KW_root_drs_loc[0] + 'FW', 0, 'Coeff fwhm']

# Number of orders located
KW_LOCO_NBO = [KW_root_drs_loc[0] + 'NBO', 0, 'nb orders localised']

# Maximum flux in order
KW_LOC_MAXFLX = [KW_root_drs_loc[0] + 'FLXMAX', 0, 'max flux in order [ADU]']

# Maximum number of removed points allowed for location fit
KW_LOC_SMAXPTS_CTR = [KW_root_drs_loc[0] + 'CTRMAX', 0, 'max rm pts ctr']

# Maximum number of removed points allowed for width fit
#    (formally KW_LOC_Smaxpts_width)
KW_LOC_SMAXPTS_WID = [KW_root_drs_loc[0] + 'WIDMAX', 0, 'max rm pts width']

# Maximum rms allowed for location fit
KW_LOC_RMS_CTR = [KW_root_drs_loc[0] + 'RMSCTR', 0, 'max rms ctr']

# Maximum rms allowed for width fit (formally KW_LOC_rms_fwhm)
KW_LOC_RMS_WID = [KW_root_drs_loc[0] + 'RMSWID', 0, 'max rms width']

# -----------------------------------------------------------------------------
# Define cal_SLIT variables
# -----------------------------------------------------------------------------
# Tilt order keyword prefix
KW_TILT = [KW_root_drs_loc[0] + 'TILT', 0, 'Tilt order']

# -----------------------------------------------------------------------------
# Define cal_FF variables
# -----------------------------------------------------------------------------

# Signal to noise ratio for order center
KW_EXTRA_SN = ['EXTSN', 0, 'S_N order center']

# Flat field RMS for order
KW_FLAT_RMS = [KW_root_drs_flat[0] + 'RMS', 0, 'FF RMS order']

# -----------------------------------------------------------------------------
# Define cal_EXTRACT variables
# -----------------------------------------------------------------------------
# TODO: Comment this section
# localization file used
KW_LOCO_FILE = [KW_root_drs_loc[0] + 'FILE', '', 'Localization file used']

KW_E2DS_EXTM = ['EXTMETH', '', 'Extraction method']

KW_E2DS_FUNC = ['EXTFUNC', '', 'Extraction function']

KW_E2DS_SNR = ['SNR', 0, 'Signal to Noise Ratio']

KW_WAVE_TIME1 = ['WAVET1', 0, 'Wave file date+time human']
KW_WAVE_TIME2 = ['WAVET2', 0, 'Wave file date+time unix']

KW_CRPIX1 = ['CRPIX1', 0, 'Reference pixel']
KW_CRVAL1 = ['CRVAL1', 0, 'Coordinate at reference pixel [nm]']
KW_CDELT1 = ['CDELT1', 0, 'Coordinate at reference pixel [nm]']
KW_CTYPE1 = ['CTYPE1', 'nm', 'Units of coordinate']
KW_BUNIT = ['BUNIT', '', 'Units of data values']

# -----------------------------------------------------------------------------
# Define cal_BADPIX variables
# -----------------------------------------------------------------------------
# fraction of hot pixels
KW_BHOT = ['BHOT', 0, 'Frac of hot px [%]']

# fraction of bad pixels from flat
KW_BBFLAT = ['BBFLAT', 0, 'Frac of bad px from flat [%]']

# fraction of non-finite pixels in dark
KW_BNDARK = ['BNDARK', 0, 'Frac of non-finite px in dark [%]']

# fraction of non-finite pixels in flat
KW_BNFLAT = ['BNFLAT', 0, 'Frac of non-finite px in flat [%]']

# fraction of bad pixels with all criteria
KW_BBAD = ['BBAD', 0, 'Frac of bad px with all criteria [%]']

# fraction of un-illuminated pixels (from engineering flat)
KW_BNILUM = ['BNILUM', 0, 'Frac of un-illuminated pixels [%]']

# fraction of total bad pixels
KW_BTOT = ['BTOT', 0, 'Frac of bad pixels (total) [%]']

# -----------------------------------------------------------------------------
# Define BERV variables
# -----------------------------------------------------------------------------
KW_BERV = ['BERV', 0, 'Barycorrpy BC Velocity']
KW_BJD = ['BJD', 0, 'Barycorrpy BJD']
KW_BERV_MAX = ['BERVMAX', 0, 'Barycorrpy Max BC Velocity']
KW_B_OBS_HOUR = ['BCHOUR', 0, 'Observation hour used for BC']
KW_BERV_EST = ['ESTBERV', 0, 'ESTIMATED BC Velocity']
KW_BJD_EST = ['ESTBJD', 0, 'ESTIMATED BJD']
KW_BERV_MAX_EST = ['ESTBMAX', 0, 'ESTIMATED Max BC Velocity']
KW_BERV_SOURCE = ['BERVSRCE', '', 'Source of BERV (Barycorrpy/Estimate)']

# -----------------------------------------------------------------------------
# Define DRIFT variables
# -----------------------------------------------------------------------------
KW_REF_RV = ['DFTREFRV', 0, 'Reference RV [m/s]']

# -----------------------------------------------------------------------------
# Define cal_CCF variables
# -----------------------------------------------------------------------------
# TODO: Comment this section
KW_CCF_CTYPE = ['CTYPE1', '', 'Pixel coordinate system']
KW_CCF_CRVAL = ['CRVAL1', 0, 'RV CCF Value of ref pixel']
KW_CCF_CDELT = ['CDELT1', 0, 'CCF steps [km/s]']
KW_CCF_RV = ['CCFRV', 0, 'Baryc RV (no drift correction) (km/s)']
KW_CCF_FWHM = ['CCFFWHM', 0, 'FWHM of CCF (km/s)']
KW_CCF_CONTRAST = ['CCFCONT', 0, 'Contrast of  CCF (%)']
KW_CCF_MAXCPP = ['CCFMACP', 0, 'max count/pixel of CCF (e-)']
KW_CCF_MASK = ['CCFMASK', 0, 'Mask filename']
KW_CCF_LINES = ['CCFLINE', 0, 'nbr of lines used']
KW_CCF_TELL = ['CCFTELLC', 0, 'Telluric threshold for CCF rejection']
KW_CCF_WMREF = ['DVRMS', 0, 'RV photon noise uncertainty on spectrum (km/s)']
KW_CCF_RVNOISE = ['RVNOISE', 0, 'RV photon noise uncertainty on CCF (km/s)']

KW_CCF_RVC = ['CCFRVC', 0, 'Baryc RV (drift corrected) (km/s) ']
KW_DRIFT_RV = ['RVDRIFT', 0, 'RV simultaneous drift  (km/s)']

# Wavelength solution for fiber C  that is is source of the WFP keys
KW_WFP_FILE = ['WFP_FILE', None, 'WFP source file']

# -----------------------------------------------------------------------------
# Define wave variables
# -----------------------------------------------------------------------------
# the number of orders used in the TH line list                        [WAVE_AB]
KW_WAVE_ORD_N = ['TH_ORD_N', None, 'nb orders in total']

# the number of fit coefficients from the TH line list fit             [WAVE_AB]
KW_WAVE_LL_DEG = ['TH_LL_D', None, 'deg polyn fit ll(x,order)']

# the prefix to use to get the TH line list fit coefficients           [WAVE_AB]
KW_WAVE_PARAM = ['TH_LC', None, 'coeff ll(x,order)']

# the wave recipe used to produce file
KW_WAVE_CODE = ['WAVECODE', None, 'DRS Recipe used to produce wave sol']

# the input wave file used to produce file
KW_WAVE_INIT = ['WAVEINIT', None, 'The input guess wave solution']

# the x-axis dimension size for the TH line list file                  [WAVE_AB]
KW_TH_NAXIS1 = ['NAXIS1', None, '']

# the y-axis dimension size for the TH line list file                  [WAVE_AB]
KW_TH_NAXIS2 = ['NAXIS2', None, '']

# drift of the FP file used for the wavelength solution
KW_WFP_DRIFT = ['WFPDRIFT', None, 'Wavelength sol absolute CCF FP Drift [km/s]']

# FWHM of the wave FP file CCF
KW_WFP_FWHM = ['WFPFWHM', None, 'FWHM of wave sol FP CCF [km/s]']

# Contrast of the wave FP file CCF
KW_WFP_CONTRAST = ['WFPCONT', None, 'wave sol FP Contrast of CCF (%)']

# Max count/pixel of the wave FP file CCF
KW_WFP_MAXCPP = ['WFPMACPP', None, 'wave sol FP max count/pixel of CCF (e-)']

# Mask for the wave FP file CCF
KW_WFP_MASK = ['WFPMASK', None, 'wave sol FP Mask filename']

# Number of lines for the wave FP file CCF
KW_WFP_LINES = ['WFPLINE', None, 'wave sol FP nbr of lines used']

# Target RV for the wave FP file CCF
KW_WFP_TARG_RV = ['WFPTRV', None, 'wave sol FP target RV [km/s]']

# Width for the wave FP file CCF
KW_WFP_WIDTH = ['WFPWIDTH', None, 'wave sol FP CCF width [km/s]']

# Step for the wave FP file CCF
KW_WFP_STEP = ['WFPSTEP', None, 'wave sol FP CCF step [km/s]']

# -----------------------------------------------------------------------------
# Define telluric variables
# -----------------------------------------------------------------------------
# Telluric absorption prefix (i.e. ABSO_H20)                     [OBJ_FIT_TELLU]
KW_TELLU_ABSO = ['ABSO', None, 'Absorption key prefix']

# Telluric principle component amplitudes (for use with 1D list)
KW_TELLU_AMP_PC = ['AMP_PC', None, 'Principle Component Amplitudes']

# Telluric principle component derivatives
KW_TELLU_DV_TELL1 = ['DV_TELL1', None, 'Principle Component first der.']
KW_TELLU_DV_TELL2 = ['DV_TELL2', None, 'Principle Component second der.']

# Telluric keys for mk_tellu
KW_TELLU_AIRMASS = ['TAU_H20', None, 'TAPAS tau H20']
KW_TELLU_WATER = ['TAU_OTHE', None, 'TAPAS tau for o2, O3, CH4, N20, CO2']

# File list for template
KW_OBJFILELIST = ['INA', None, 'Input FILE']
KW_OBJBERVLIST = ['INB', None, 'Input BERV']
KW_OBJWAVELIST = ['INC', None, 'Input WAVE']

# Options input into tellu
KW_TELLU_NPC = ['TELLNPC', None, 'Number of Principle Components used']
KW_TELLU_FIT_DPC = ['TELLFDPC', None, 'Fit derivs instead of principle comps.']
KW_TELLU_ADD_DPC = ['TELLADPC', None, 'Add 1st+2nd derivs to principle comps.']

# -----------------------------------------------------------------------------
# Define polarimetry variables
# -----------------------------------------------------------------------------
# TODO: Comment this section
KW_POL_STOKES = ['STOKES', '', 'Stokes paremeter: Q, U, V, or I']
KW_POL_NEXP = ['POLNEXP', '', 'Number of exposures for polarimetry']
KW_POL_METHOD = ['POLMETHO', '', 'Polarimetry method']
KW_POL_EXPTIME = ['TOTETIME', '', 'Total exposure time (sec)']
KW_POL_ELAPTIME = ['ELAPTIME', '', 'Elapsed time of observation (sec)']
KW_POL_FILENAM1 = ['FILENAM1', '', 'Base filename of exposure 1']
KW_POL_FILENAM2 = ['FILENAM2', '', 'Base filename of exposure 2']
KW_POL_FILENAM3 = ['FILENAM3', '', 'Base filename of exposure 3']
KW_POL_FILENAM4 = ['FILENAM4', '', 'Base filename of exposure 4']
KW_POL_EXPTIME1 = ['EXPTIME1', '', 'EXPTIME of exposure 1 (sec)']
KW_POL_EXPTIME2 = ['EXPTIME2', '', 'EXPTIME of exposure 2 (sec)']
KW_POL_EXPTIME3 = ['EXPTIME3', '', 'EXPTIME of exposure 3 (sec)']
KW_POL_EXPTIME4 = ['EXPTIME4', '', 'EXPTIME of exposure 4 (sec)']
KW_POL_MJDATE1 = ['MJDATE1', '', 'MJD at start of exposure 1']
KW_POL_MJDATE2 = ['MJDATE2', '', 'MJD at start of exposure 2']
KW_POL_MJDATE3 = ['MJDATE3', '', 'MJD at start of exposure 3']
KW_POL_MJDATE4 = ['MJDATE4', '', 'MJD at start of exposure 4']
KW_POL_MJDEND1 = ['MJDEND1', '', 'MJDEND at end of exposure 1']
KW_POL_MJDEND2 = ['MJDEND2', '', 'MJDEND at end of exposure 2']
KW_POL_MJDEND3 = ['MJDEND3', '', 'MJDEND at end of exposure 3']
KW_POL_MJDEND4 = ['MJDEND4', '', 'MJDEND at end of exposure 4']
KW_POL_BJD1 = ['BJD1', '', 'BJD at start of exposure 1']
KW_POL_BJD2 = ['BJD2', '', 'BJD at start of exposure 2']
KW_POL_BJD3 = ['BJD3', '', 'BJD at start of exposure 3']
KW_POL_BJD4 = ['BJD4', '', 'BJD at start of exposure 4']
KW_POL_BERV1 = ['BERV1', '', 'BERV at start of exposure 1']
KW_POL_BERV2 = ['BERV2', '', 'BERV at start of exposure 2']
KW_POL_BERV3 = ['BERV3', '', 'BERV at start of exposure 3']
KW_POL_BERV4 = ['BERV4', '', 'BERV at start of exposure 4']
KW_POL_MEANBJD = ['MEANBJD', '', 'Mean BJD for polar sequence']
KW_POL_MJDCEN = ['MJDCEN', '', 'MJD at center of observation']
KW_POL_BJDCEN = ['BJDCEN', '', 'BJD at center of observation']
KW_POL_BERVCEN = ['BERVCEN', '', 'BERV at center of observation']
KW_POL_LSD_MASK = ['LSDMASK', '', 'LSD mask filename']
KW_POL_LSD_V0 = ['LSDV0', '', 'Initial velocity (km/s) for LSD profile']
KW_POL_LSD_VF = ['LSDVF', '', 'Final velocity (km/s) for LSD profile']
KW_POL_LSD_NP = ['LSDNP', '', 'Number of points for LSD profile']
KW_POL_LSD_FIT_RV = ['LSDFITRV', '', 'Radial velocity (km/s) from gaussian fit']
KW_POL_LSD_FIT_RESOL = ['LSDRESOL', '', 'Resolving power from gaussian fit']
KW_POL_LSD_MEANPOL = ['LSDMEPOL', '', 'Mean polarization of data in LSD']
KW_POL_LSD_STDDEVPOL = ['LSDSDPOL', '', 'Std dev polarization of data in LSD']
KW_POL_LSD_MEDIANPOL = ['LSDMDPOL', '', 'Median polarization of data in LSD']
KW_POL_LSD_MEDABSDEVPOL = ['LSDMAPOL', '',
                           'Med abs dev polarization of data in LSD']
KW_POL_LSD_STOKESVQU_MEAN = ['MEPOLLSD', '', 'Mean of pol LSD profile']
KW_POL_LSD_STOKESVQU_STDDEV = ['SDPOLLSD', '', 'Std dev of pol LSD profile']
KW_POL_LSD_NULL_MEAN = ['MENULLSD', '', 'Mean of null LSD profile']
KW_POL_LSD_NULL_STDDEV = ['SDNULLSD', '', 'Std dev of null LSD profile']
KW_POL_LSD_COL1 = ['LSDCOL1', '', 'Velocities (km/s)']
KW_POL_LSD_COL2 = ['LSDCOL2', '', 'Stokes I LSD profile']
KW_POL_LSD_COL3 = ['LSDCOL3', '', 'Gaussian fit to Stokes I LSD profile']
KW_POL_LSD_COL4 = ['LSDCOL4', '', 'Stokes V, U, or Q LSD profile']
KW_POL_LSD_COL5 = ['LSDCOL5', '', 'Null polarization LSD profile']

# -----------------------------------------------------------------------------
# Define cal_exposure_meter variables
# -----------------------------------------------------------------------------
# TODO: Comment this section
KW_EM_TELLX = ['TELL_X', 0.0, 'Telluric x file used (wavelengths)']
KW_EM_TELLY = ['TELL_Y', 0.0, 'Telluric y file used (transmission)']
KW_EM_LOCFILE = ['LOCFILE', 0.0, 'Loc file used (cent+fwhm fits)']
KW_EM_WAVE = ['WAVEFILE', 0.0, 'Wavelength solution file used']
KW_EM_TILT = ['TILTFILE', 0.0, 'Tilt solution file used']
KW_EM_MINWAVE = ['MINLAM', 0.0, 'Minimum lambda used in mask [nm]']
KW_EM_MAXWAVE = ['MAXLAM', 0.0, 'Maximum lambda used in mask [nm]']
KW_EM_TRASCUT = ['TRANSCUT', 0.0, 'Minimum transmission used in mask']

# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
# Note must update spirouConfig.spirouConst.QC_HEADER_KEYS if these are
#   changed
KW_DRS_QC = ['QCC', 0, 'All quality control passed']
KW_DRS_QC_VAL = ['QCC{0:03d}V', '', 'Qualtity control value']
KW_DRS_QC_NAME = ['QCC{0:03d}N', '', 'Quality control variable name']
KW_DRS_QC_LOGIC = ['QCC{0:03d}L', '', 'Quality control logic']
KW_DRS_QC_PASS = ['QCC{0:03d}P', 0, 'Quality control passed']

# -----------------------------------------------------------------------------
# Define inputs
# -----------------------------------------------------------------------------
# file inputs
KW_INFILE1 = ['INF1{0:03d}', '', 'Input file used to create output']
KW_INFILE2 = ['INF2{0:03d}', '', 'Input file used to create output (2nd)']
KW_INFILE3 = ['INF3{0:03d}', '', 'Input file used to create output (3rd)']
# calibration inputs
KW_CDBDARK = ['CDBDARK', '', 'The calibration DARK file used']
KW_CDBBAD = ['CDBBAD', '', 'The calibration BADPIX file used']
KW_CDBBACK = ['CDBBACK', '', 'The calibration BACKGROUND file used']
KW_CDBORDP = ['CDBORDP', '', 'The calibration ORDER_PROFILE file used']
KW_CDBLOCO = ['CDBLOCO', '', 'The calibration LOC file used']
KW_CDBTILT = ['CDBTILT', '', 'The calibration TILT file used']
KW_CDBSHAPE = ['CDBSHAPE', '', 'The calibration local SHAPE file used']
KW_CDBSHAPEX = ['CDBSHAPX', '', 'The calibration SHAPE X file used']
KW_CDBSHAPEY = ['CDBSHAPY', '', 'The calibration SHAPE Y file used']
KW_CDBFLAT = ['CDBFLAT', '', 'The calibration FLAT file used']
KW_CDBBLAZE = ['CDBBLAZE', '', 'The calibration BLAZE file used']
KW_CDBWAVE = ['CDBWAVE', '', 'The calibration WAVE file used']
# telluric inputs
KW_TDBMAP = ['TDBMAP', '', 'The telluric TELL_MAP file used']
KW_TDBOBJ = ['TDBOBJ', '', 'The telluric TELL_OBJ file used']
KW_TDBTEMP = ['TDBTEMP', '', 'The telluric OBJ_TEMP file used']
KW_TDBRECON = ['TDBRECON', '', 'The telluric TELL_RECON file used']
# extra drift inputs
KW_REFFILE = ['REFRFILE', '', 'Reference file used to create drift file']
# extra wave inputs
KW_WAVESOURCE = ['WAVELOC', '', 'Where the wave solution was read from']
# extra ccf inputs
KW_INCCFMASK = ['INP1MASK', '', 'Input Mask used in CCF process']
KW_INRV = ['INP1RV', '', 'Input RV used in CCF process']
KW_INWIDTH = ['INP1WID', '', 'Input width used in CCF process']
KW_INSTEP = ['INP1STEP', '', 'Input step used in CCF process']

# -----------------------------------------------------------------------------
# Define outputs
# -----------------------------------------------------------------------------
KW_OUTPUT = ['DRSOUTID', '', 'DRS output identification code']
KW_EXT_TYPE = ['DRS_EOUT', '', 'DRS Extraction input DPRTYPE']


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
    'KW_' prefix. Note should have a fresh python instance running to avoid
    unwanted variables. Only for use in creating the list USE_KEYS for this
    code!

    :return use_keys: list of strings, list of all keys with 'KW_' in their name
    """
    all_locals = np.sort(list(globals().keys()))
    use_keys = []
    for lkey in all_locals:
        if 'KW_' in lkey:
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
