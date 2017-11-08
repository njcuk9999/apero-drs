#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2017-10-30 at 16:37

@author: cook



Version 0.0.0
"""
from . import spirouConfig


# =============================================================================
# Define program variables (do not change)
# =============================================================================
__NAME__ = 'spirouKeywords.py'
# Get param dict
ParamDict = spirouConfig.ParamDict
# get default config file
p = spirouConfig.read_config_file()
# check input parameters
p = spirouConfig.check_params(p)
# load ICDP config file
p = spirouConfig.load_config_from_file(p, key='ICDP_NAME', required=True)

# =============================================================================
# Change these
# =============================================================================
# Keys must be deinfed here to be used (define as string)
#     run SpirouDRS.spirouConfig.test_keywords()
#     to test which variables are not currently in below list
# ---------------------------------------------------------------
# MUST UPDATE THIS IF VARIABLES ADDED
USE_KEYS = ['kw_ACQTIME_KEY',
             'kw_CCD_CONAD',
             'kw_CCD_SIGDET',
             'kw_DARK_B_DEAD',
             'kw_DARK_B_MED',
             'kw_DARK_CUT',
             'kw_DARK_DEAD',
             'kw_DARK_MED',
             'kw_DARK_R_DEAD',
             'kw_DARK_R_MED',
             'kw_LOCO_BCKGRD',
             'kw_LOCO_CTR_COEFF',
             'kw_LOCO_DEG_C',
             'kw_LOCO_DEG_E',
             'kw_LOCO_DEG_W',
             'kw_LOCO_DELTA',
             'kw_LOCO_FWHM_COEFF',
             'kw_LOCO_NBO',
             'kw_LOC_MAXFLX',
             'kw_LOC_RMS_CTR',
             'kw_LOC_RMS_WID',
             'kw_LOC_SMAXPTS_CTR',
             'kw_LOC_SMAXPTS_WID',
             'kw_TILT',
             'kw_version']
# MUST UPDATE THIS IF VARIABLES FROM CONFIG FILES USED
USE_PARAMS = ['DRS_NAME',
              'DRS_VERSION',
              'IC_LOC_DELTA_WIDTH',
              'IC_LOCDFITC',
              'IC_LOCDFITP',
              'IC_LOCDFITW']

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
#           (config.txt, constants_SPIROU.txt etc) located in the ../config
#           folder, however they should be placed as strings in USE_PARAMS
#
# -----------------------------------------------------------------------------
# General variables
# -----------------------------------------------------------------------------
# DRS version
kw_version = ['VERSION', '{0}_{1}'.format(p['DRS_NAME'], p['DRS_VERSION']),
              'DRS version']

# root keys (for use below)
root_drs_loc =  'LO'
root_drs_flat = 'FF'
root_drs_hc =   'LMP'


# define the HEADER key for acquisition time (used to get only)
kw_ACQTIME_KEY = ['ACQTIME1', None, 'Only used to get acquistition time']

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
kw_LOCO_BCKGRD = [root_drs_loc + 'BCKGRD', 0, 'mean background [%]']

# Image conversion factor [e-/ADU]
kw_CCD_CONAD = ['CONAD', 0, 'CCD conv factor [e-/ADU]']

# Image readout noise
kw_CCD_SIGDET = ['SIGDET', 0, 'CCD Readout Noise [e-]']

# Coeff center order
kw_LOCO_CTR_COEFF = [root_drs_loc + 'CTR', 0, 'Coeff center']

# fit degree for order centers
kw_LOCO_DEG_C = [root_drs_loc + 'DEGCTR',  p['IC_LOCDFITC'],
                 'degree fit ctr ord']

# fit degree for order widths
kw_LOCO_DEG_W = [root_drs_loc + 'DEGFWH', p['IC_LOCDFITW'],
                 'degree fit width ord']

# fit degree for profile error
kw_LOCO_DEG_E = [root_drs_loc + 'DEGERR', p['IC_LOCDFITP'],
                 'degree fit profile error']

# delta width (pix) for 3 convol shape model (currently not used??)
kw_LOCO_DELTA = [root_drs_loc + 'PRODEL', p['IC_LOC_DELTA_WIDTH'],
                 'param model 3gau']

# Coeff width order
kw_LOCO_FWHM_COEFF = [root_drs_loc + 'FW', 0, 'Coeff fwhm']

# Number of orders located
kw_LOCO_NBO = [root_drs_loc + 'NBO', 0, 'nb orders localised']

# Maximum flux in order
kw_LOC_MAXFLX = [root_drs_loc + 'FLXMAX', 0, 'max flux in order [ADU]']

# Maximum number of removed points allowed for location fit
kw_LOC_SMAXPTS_CTR = [root_drs_loc + 'CTRMAX', 0, 'max rm pts ctr']

# Maximum number of removed points allowed for width fit
#    (formally kw_LOC_Smaxpts_width)
kw_LOC_SMAXPTS_WID = [root_drs_loc + 'WIDMAX', 0, 'max rm pts width']

# Maximum rms allowed for location fit
kw_LOC_RMS_CTR = [root_drs_loc + 'RMSCTR', 0, 'max rms ctr']

# Maximum rms alloed for width fit (formally kw_LOC_rms_fwhm)
kw_LOC_RMS_WID = [root_drs_loc + 'RMSWID', 0, 'max rms width']

# Tilt order keyword prefix
kw_TILT = [root_drs_loc + 'TILT', 0, 'Tilt order']

# =============================================================================
# Define functions (Do not change)
# =============================================================================
def test_keywords():
    for key in locals():
        if key not in USE_KEYS:
            print('WARNING: key={0} not in USE_KEYS')


def generate_use_keys():
    import numpy as np
    all_locals = np.sort(list(globals().keys()))
    use_keys = []
    for lkey in all_locals:
        if 'kw_' in lkey:
            use_keys.append(lkey)
    return use_keys


def get_keywords(pp=None):
    """
    Get keywords defined in USE_KEYS from above (must be named exactly as in
    USE_KEYS list)

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
    if type(value) != list:
        raise spirouConfig.ConfigError('Key {0} defined in {1} is not a list. '
                                       'Please check', level='error')
    # value must be a list of length 3
    if len(value) != 3:
        emsg = 'key {0} defined in {1} is not a length 3 list (len={2})'
        raise spirouConfig.ConfigError(emsg.format(key, __NAME__, len(value)),
                                       level='error')
    # value[0] and value[2] must be strings
    if type(value[0]) != str or type(value[2]) != str:
        emsg = ('key {0} defined in {1} is not in form: \n\t'
                '[string, #value, string] \n\n\twhere #value is any value, '
                'and \n\tstring is any valid python str object.')
        raise spirouConfig.ConfigError(emsg.format(key, __NAME__),
                                       level='error')

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    kwdict = get_keywords()

# =============================================================================
# End of code
# =============================================================================
