"""
Default constants for NO INSTRUMENT

This is the default constants config file

Created on 2019-01-17

@author: cook
"""

# This is the main config file
import numpy as np

from aperocore.base import base
from aperocore.constants import constant_functions
from apero.base import base as apero_base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.instruments.default.constants.py'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# Constants class
Const = constant_functions.Const
CDict = constant_functions.ConstantsDict(__NAME__)


# set the title for output yaml files
CDict.title = CDict.yaml_title('APERO[{INSTRUMENT}] constants file',
                               setup_program='apero_setup.py',
                               version=__version__, date=__date__)


# =============================================================================
# DRS DATA SETTINGS
# =============================================================================
cgroup = 'DATA'
CDict.add_group(cgroup, description='DRS DATA SETTINGS')

# Define the data engineering path
CDict.add('DATA_ENGINEERING', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the data engineering path')

# =============================================================================
# COMMON IMAGE SETTINGS
# =============================================================================
cgroup = 'IMAGE'
CDict.add_group(cgroup, description='COMMON IMAGE SETTINGS')

# Define the rotation of the pp files in relation to the raw files
#     nrot = 0 -> same as input
#     nrot = 1 -> 90deg counter-clock-wise
#     nrot = 2 -> 180deg
#     nrot = 3 -> 90deg clock-wise
#     nrot = 4 -> flip top-bottom
#     nrot = 5 -> flip top-bottom and rotate 90 deg counter-clock-wise
#     nrot = 6 -> flip top-bottom and rotate 180 deg
#     nrot = 7 -> flip top-bottom and rotate 90 deg clock-wise
#     nrot >=8 -> performs a modulo 8 anyway
CDict.add('RAW_PP_ROT', dtype=int, value=None,
          source=__NAME__, group=cgroup,
          options=[0, 1, 2, 3, 4, 5, 6, 7],
          description='Define the rotation of the pp files in '
                      'relation to the raw files, '
                      '\n\tnrot = 0 -> same as input, '
                      '\n\tnrot = 1 -> 90deg counter-clock-'
                      'wise, '
                      '\n\tnrot = 2 -> 180deg, '
                      '\n\tnrot = 3 -> 90deg clock-wise,  '
                      '\n\tnrot = 4 -> flip top-bottom, '
                      '\n\tnrot = 5 -> flip top-bottom and '
                      'rotate 90 deg counter-clock-wise'
                      '\n\tnrot = 6 -> flip top-bottom and '
                      'rotate 180 deg, '
                      '\n\tnrot = 7 -> flip top-bottom and '
                      'rotate 90 deg clock-wise, '
                      '\n\tnrot >=8 -> performs a modulo '
                      '8 anyway')

# Measured detector gain in all places that use gain
CDict.add('EFFGAIN', dtype=float, value=None, source=__NAME__,
          group=cgroup, minimum=0,
          description='Measured detector gain in all places that use '
                      'gain')

# Define raw image size (mostly just used as a check and in places where we
#   don't have access to this information) in x dim
CDict.add('X_FULL', dtype=int, value=None, source=__NAME__,
          group=cgroup,
          description=('Define raw image size (mostly just used as '
                       'a check and in places where we dont have '
                       'access to this information) in x dim'))

# Define raw image size (mostly just used as a check and in places where we
#   don't have access to this information) in y dim
CDict.add('Y_FULL', dtype=int, value=None, source=__NAME__,
          group=cgroup,
          description=('Define raw image size (mostly just used as '
                       'a check and in places where we dont have '
                       'access to this information) in y dim'))

# Define the fibers
CDict.add('FIBER_TYPES', dtype=list, dtypei=str,
          value=None, source=__NAME__,
          group=cgroup, description='Define the fibers')

# Defines whether to by default combine images that are inputted at the same
# time
CDict.add('COMBINE_INPUT', dtype=bool, value=True,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='Defines whether to by default combine'
                      ' images that are inputted at the '
                      'same time')

# Defines whether to, by default, flip images that are inputted
CDict.add('FLIP_INPUT', dtype=bool, value=True,
          source=__NAME__, group=cgroup,
          description=('Defines whether to, by default, '
                       'flip images that are inputted'))

# Defines how to flip the image
CDict.add('FLIP_METHOD', dtype=str, value=None,
          options=['None', 'x', 'y', 'both'],
          source=__NAME__, group=cgroup,
          description=('Defines default method to '
                       'flip images that are inputted'))

# Defines whether to, by default, resize images that are inputted
CDict.add('RESIZE_IMAGE', dtype=bool, value=True,
          source=__NAME__, group=cgroup,
          description=('Defines whether to, by default, '
                       'resize images that are inputted'))

# Defines the resized image
CDict.add('X_LOW', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup,
          description='Defines the resized image')
CDict.add('X_HIGH', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')
CDict.add('Y_LOW', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')
CDict.add('Y_HIGH', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')

# Define the pixel size in km/s / pix
#    also used for the median sampling size in tellu correction
CDict.add('PIXEL_SIZE', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define the pixel size in km/s / pix '
                       'also used for the median sampling '
                       'size in tellu correction'))

# Define whether we apply an upper bound when calibrating pp images
# This sets values above saturate / frmtime
CDict.add('APPLY_UPPER_BOUND', value=True, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('Define whether we apply an upper bound when '
                       'calibrating pp images. This sets values above '
                       'saturate / frmtime'))

# Define whether we apply a lower bound when calibrating pp images
# This sets values below  -10 * (sigdet * gain) / frmtime to nans
CDict.add('APPLY_LOWER_BOUND', value=True, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('Define whether we apply a lower bound when '
                       'calibrating pp images. This sets values below '
                       '-10 * (sigdet * gain) / frmtime to nans'))

# Define mean line width expressed in pix
CDict.add('FWHM_PIXEL_LSF', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define mean line width expressed in pix')

# Define the point at which the detector saturates
CDict.add('SATURATION', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define the point at which the detector '
                      'saturates')

# Define the frame time for an image
CDict.add('FRAME_TIME', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define the frame time for an image')

# Define all polar rhomb positions
CDict.add('POLAR_RHOMB_POS', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define all polar rhomb positions')


# =========================================================================
# GENERAL REFERENCE FILE SETTINGS
# =========================================================================
cgroup = 'REF'
CDict.add_group(cgroup, description='REF: GENERAL REF FILE SETTINGS')

# Define the time column (in the database) to use for filtering reference
# files by (start date and end date format must match this)
CDict.add('FIND_TIMECOL', value=None, dtype=str, active=True, user=True,
          source=__NAME__, group=cgroup,
          description='Define the time column (in the database) to use for '
                      'filtering reference files by (start date and end date '
                      'format must match this)')

# Define the start date for reference calibrations (date format must match
# that in REF.FIND_TIMECOL). This is used as the first date allowed for
# reference files (i.e. any file before this date will be ignored)
CDict.add('FIND_STARTDATE', value=None, dtype=str, active=True,
          user=True, source=__NAME__, group=cgroup,
          description='Define the start date for reference calibrations '
                      '(date format must match that in REF.FIND_TIMECOL). '
                      'This is used as the first date allowed for reference '
                      'files (i.e. any file before this date will be ignored)')

# Define the end date for reference calibrations (date format must match that in
# REF_FIND_TIME_COL). This is used as the last date allowed for reference files
# (i.e. any file after this date will be ignored)
CDict.add('FIND_ENDDATE', value=None, dtype=str, active=True,
          user=True, source=__NAME__, group=cgroup,
          description='Define the end date for reference calibrations '
                      '(date format must match that in REF.FIND_TIMECOL). '
                      'This is used as the last date allowed for reference '
                      'files (i.e. any file after this date will be ignored)')

# =========================================================================
# HEADER SETTINGS
# =========================================================================
cgroup = 'HEADER'
CDict.add_group(cgroup, description='DRS.HEADER: HEADER SETTINGS')

# post process do not check these duplicate keys
CDict.add('NON_CHECK_DUPLICATE_KEYS',
          value=['SIMPLE', 'EXTEND', 'NEXTEND'],
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='post process do not check these '
                      'duplicate keys')

# Post process primary extension should not have these keys
CDict.add('FORBIDDEN_OUT_KEYS',
          value=['BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2',
                 'XTENSION'],
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Post process primary extension should '
                      'not have these keys')

# Defines the keys in a HEADER file not to copy when copying over all
# HEADER keys to a new fits file
CDict.add('FORBIDDEN_COPY_KEYS',
          value=['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1',
                 'NAXIS2', 'EXTEND', 'COMMENT', 'CRVAL1',
                 'CRPIX1', 'CDELT1', 'CRVAL2', 'CRPIX2',
                 'CDELT2', 'BSCALE', 'BZERO', 'PHOT_IM',
                 'FRAC_OBJ', 'FRAC_SKY', 'FRAC_BB',
                 'NEXTEND'],
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Defines the keys in a HEADER file not '
                      'to copy when copying over all HEADER '
                      'keys to a new fits file')

# Define the QC keys prefixes that should not be copied (i.e. they are
# just for the input file not the output file)
CDict.add('FORBIDDEN_HEADER_PREFIXES',
          value=['QCC', 'INF1', 'INF2', 'INF3', 'INP1'],
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define the QC keys prefixes '
                      'that should not be copied '
                      '(i.e. they are just for the '
                      'input file not the output file)')

# Define a list of keys that should not be copied from headers to new headers
CDict.add('FORBIDDEN_DRS_KEY',
          value=['WAVELOC', 'REFRFILE', 'DRSPID', 'VERSION',
                 'DRSOUTID'],
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define a list of keys that should not '
                      'be copied from headers to new headers')

# =============================================================================
# CALIBRATION: GENERAL SETTINGS
# =============================================================================
cgroup = 'CAL.GEN'
CDict.add_group(cgroup, description='CALIBRATION.GENERAL: '
                                    'CALIBRATION: GENERAL SETTINGS')

# Define the maximum number of files that can be used in a group
CDict.add('GROUP_FILE_LIMIT', value=None, dtype=int,
          source=__NAME__, group=cgroup, minimum=1,
          description='Define the maximum number of files that '
                      'can be used in a group')

# Define the maximum time (in days) that a calibration can be separated from
#   an observation in order to use it
CDict.add('MAX_DTIME', value=None, dtype=float,
          source=__NAME__, group=cgroup, minimum=1.0,
          description='Define the maximum time (in days) that a '
                      'calibration can be separated from an '
                      'observation in order to use it')

# Define whether we check the calibration and observation separation
CDict.add('DTIME_CHECK', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description='Define whether we check the '
                      'calibration and observation '
                      'separation')

# define whether the user wants to bin the calibration times to a specific
#   day fraction (i.e. midnight, midday) using CALIB_DB_DAYFRAC
CDict.add('BIN_IN_TIME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('define whether the user wants to '
                       'bin the calibration times to a '
                       'specific day fraction (i.e. midnight,'
                       ' midday) using CALIB_DB_DAYFRAC'))

# Define the the fraction of the day to bin to (0 = midnight  before
#     observation, 0.5 = noon, and 1.0 = midnight after
CDict.add('DAYFRAC', value=None, dtype=float,
          source=__NAME__, group=cgroup, minimum=0.0,
          maximum=1.0,
          description=('Define the the fraction of the day to '
                       '(0 = midnight  before observation, '
                       ' 0.5 = noon, and 1.0 = midnight after'))

# Define the threshold under which a file should not be combined
#  (metric is compared to the median of all files 1 = perfect, 0 = noise)
CDict.add('CMETRIC1_THRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0, maximum=1,
          description=('Define the threshold under '
                       'which a file should not be '
                       'combined (metric is compared '
                       'to the median of all files 1 '
                       '= perfect, 0 = noise)'))

# Define the DPRTYPES allowed for the combine metric 1 comparison
CDict.add('CMETRIC1_TYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('Define the DPRTYPES allowed for '
                       'the combine metric 1 comparison'))

# Assuming that the FPs peaks cover a certain fraction of the frame
# (5% in SPIRou+NIRPS, 1% in ILocater), we check that the 1-FP_coverage is
# far higher (defined as N times the readout noise in reference pixels;
# variable name X) than the median of frame.
CDict.add('CHECKFP_PERCENTILE', value=None,
          dtype=int, minimum=0, source=__NAME__,
          group=cgroup,
          description='Assuming that the FPs peaks cover a certain fraction '
                      'of the frame (5% in SPIRou+NIRPS, 1% in ILocater), '
                      'we check that the 1-FP_coverage is far higher '
                      '(defined as N times the readout noise in reference '
                      'pixels; variable name X) than the median of frame.')

# define the check FP threshold qc parameter
CDict.add('CHECK_FP_THRES', value=None,
          dtype=float, minimum=0.0, source=__NAME__,
          group=cgroup,
          description='define the check FP threshold qc parameter')

# define the check FP center image size [px]
CDict.add('CHECK_FP_CENT_SIZE', value=None,
          dtype=int, minimum=0, source=__NAME__,
          group=cgroup,
          description='define the check FP center image size [px]')

# Define whether to force wave solution from calibration database (instead of
#  using header wave solution if available)
CDict.add('FORCE_WAVESOL', value=None, dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='Define whether to force wave solution from '
                      'calibration database (instead of using header wave '
                      'solution if available)')

# =============================================================================
# CALIBRATION: FIBER SETTINGS
# =============================================================================
cgroup = 'CAL.FIBER'
CDict.add_group(cgroup, description='CAL.FIBER: CALIBRATION FIBER SETTINGS')

# Number of orders to skip at start of image
CDict.add('FIRST_ORDER_JUMP', value=None, dtype=dict, dtypei=int,
          source=__NAME__, group=cgroup,
          description='Number of orders to skip at start of image')

# Maximum number of order to use
CDict.add('MAX_NUM_ORDERS', value=None,
          dtype=dict, dtypei=int, source=__NAME__, group=cgroup,
          description='Maximum number of order to use')

# Number of fibers
CDict.add('SET_NUM_FIBERS', value=None,
          dtype=dict, dtypei=int, source=__NAME__,
          group=cgroup, description='Number of fibers')

# Get the science and reference fiber to use in the CCF process
CDict.add('CCF', value=None, dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Get the science and reference fiber to use in '
                      'the CCF process')

# List the individual fiber names
CDict.add('INDIVIDUAL', value=None, dtype=list,
          dtypei=str, source=__NAME__, group=cgroup,
          description='List the individual fiber names')

# List the sky fibers to use for the science channel and the calib channel
CDict.add('SKYFIBERS', value=None, dtype=list,
          source=__NAME__, group=cgroup,
          description='List the sky fibers to use for the science '
                      'channel and the calib channel')

# =============================================================================
# PRE-PROCESSSING SETTINGS
# =============================================================================
cgroup = 'PP'
CDict.add_group(cgroup, description='PP: PRE-PROCESSSING SETTINGS')

# Define object (science or telluric)
CDict.add('OBJ_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define object (science or telluric)')

# Defines the box size surrounding hot pixels to use
CDict.add('HOTPIX_BOXSIZE', value=None, dtype=int,
          minimum=1, source=__NAME__, group=cgroup,
          description=('Defines the box size surrounding '
                       'hot pixels to use'))

# Defines the size around badpixels that is considered part of the bad pixel
CDict.add('CORRUPT_MED_SIZE', value=None, dtype=int,
          minimum=1, source=__NAME__, group=cgroup,
          description=('Defines the size around badpixels '
                       'that is considered part of the '
                       'bad pixel'))

# Define the fraction of the required exposure time that is required for a
#   valid observation
CDict.add('BAD_EXPTIME_FRACTION', value=None,
          dtype=float, minimum=0, source=__NAME__,
          group=cgroup,
          description=('Define the fraction of the '
                       'required exposure time that '
                       'is required for a valid '
                       'observation'))

# Defines the threshold in sigma that selects hot pixels
CDict.add('CORRUPT_HOT_THRES', value=None, dtype=int,
          minimum=0, source=__NAME__, group=cgroup,
          description=('Defines the threshold in sigma that '
                       'selects hot pixels'))

# Define the total number of amplifiers
CDict.add('TOTAL_AMP_NUM', value=None, dtype=int,
          minimum=0, source=__NAME__, group=cgroup,
          description='Define the total number of amplifiers')

# Define the number of dark amplifiers
CDict.add('NUM_DARK_AMP', value=None, dtype=int,
          minimum=0, source=__NAME__, group=cgroup,
          description='Define the number of dark amplifiers')

# Define the number of bins used in the dark median process
CDict.add('DARK_MED_BINNUM', value=None, dtype=int,
          minimum=0, source=__NAME__, group=cgroup,
          description=('Define the number of bins used in the '
                       'dark median process - [apero_preprocess]'))

#   Defines the pp hot pixel file (located in the data folder)
CDict.add('HOTPIX_FILE', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Defines the pp hot pixel file (located in '
                      'the data folder)')

#   Defines the pp hot pixel file type
CDict.add('HOTPIX_FILE_FMT', value='csv', dtype=str, source=__NAME__,
          group=cgroup, options=['fits', 'csv'],
          description='Defines the pp hot pixel file type (fits or csv)')

#   Defines the pp amplifier bias model (located in the data folder)
CDict.add('AMP_ERROR_MODEL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Defines the pp amplifier bias model '
                      '(located in the data folder)')

# Defines the pp led flat file (located in the data folder)
# TODO: Note used??
CDict.add('LED_FLAT_FILE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Defines the pp led flat file '
                      '(located in the data folder)')

# Define the number of un-illuminated reference pixels at top of image
CDict.add('NUM_REF_TOP', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Define the number of un-illuminated '
                       'reference pixels at top of image'))

# Define the number of un-illuminated reference pixels at bottom of image
CDict.add('NUM_REF_BOTTOM', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Define the number of un-illuminated '
                       'reference pixels at bottom of image'))

# Define the number of un-illuminated reference pixels at left of image
CDict.add('NUM_REF_LEFT', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Define the number of un-illuminated '
                       'reference pixels at left of image'))

# Define the number of un-illuminated reference pixels at right of image
CDict.add('NUM_REF_RIGHT', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Define the number of un-illuminated '
                       'reference pixels at right of image'))

# Define the percentile value for the rms normalisation (0-100)
CDict.add('RMS_PERCENTILE', value=None, dtype=int,
          minimum=0, maximum=100, source=__NAME__, group=cgroup,
          description=('Define the percentile value for the '
                       'rms normalisation (0-100)'))

# Define the lowest rms value of the rms percentile allowed if the value of
#   the pp_rms_percentile-th is lower than this this value is used
CDict.add('LOWEST_RMS_PERCENTILE', value=None,
          dtype=float, minimum=0.0, source=__NAME__,
          group=cgroup,
          description=('Define the lowest rms value of '
                       'the rms percentile allowed if '
                       'the value of the '
                       'pp_rms_percentile-th is lower '
                       'than this this value is used'))

# Defines the snr hotpix threshold to define a corrupt file
CDict.add('CORRUPT_SNR_HOTPIX', value=None, dtype=float,
          minimum=0.0, source=__NAME__, group=cgroup,
          description=('Defines the snr hotpix threshold '
                       'to define a corrupt file'))

# Defines the RMS threshold to also catch corrupt files
CDict.add('CORRUPT_RMS_THRES', value=None, dtype=float,
          minimum=0.0, source=__NAME__, group=cgroup,
          description=('Defines the RMS threshold to also '
                       'catch corrupt files'))

# super-pessimistic noise estimate. Includes uncorrected common noise
CDict.add('COSMIC_NOISE_EST', value=None,
          dtype=float, minimum=0.0, source=__NAME__,
          group=cgroup,
          description=('super-pessimistic noise '
                       'estimate. Includes uncorrected '
                       'common noise'))

# define the cuts in sigma where we should look for cosmics (variance)
CDict.add('COSMIC_VARCUT1', value=None, dtype=float,
          minimum=0.0, source=__NAME__, group=cgroup,
          description=('define the cuts in sigma where we '
                       'should look for cosmics (variance)'))

# define the cuts in sigma where we should look for cosmics (variance)
CDict.add('COSMIC_VARCUT2', value=None, dtype=float,
          minimum=0.0, source=__NAME__, group=cgroup,
          description=('define the cuts in sigma where we '
                       'should look for cosmics (variance)'))

# define the cuts in sigma where we should look for cosmics (intercept)
CDict.add('COSMIC_INTCUT1', value=None, dtype=float,
          minimum=0.0, source=__NAME__, group=cgroup,
          description=('define the cuts in sigma where we '
                       'should look for cosmics (intercept)'))

# define the cuts in sigma where we should look for cosmics (intercept)
CDict.add('COSMIC_INTCUT2', value=None, dtype=float,
          minimum=0.0, source=__NAME__, group=cgroup,
          description=('define the cuts in sigma where we '
                       'should look for cosmics (intercept)'))

# random box size [in pixels] to speed-up low-frequency band computation
CDict.add('COSMIC_BOXSIZE', value=None, dtype=int,
          minimum=0.0, source=__NAME__, group=cgroup,
          description=('random box size [in pixels] to '
                       'speed-up low-frequency band '
                       'computation'))

# Define whether to skip preprocessed files that have already be processed
CDict.add('SKIP_DONE', value=None, dtype=bool,
          source=__NAME__, user=True, active=False, group=cgroup,
          description='Define whether to skip preprocessed files '
                      'that have already be processed')

# Define dark dprtypes for threshold quality control check (PP_DARK_THRES)
CDict.add('DARK_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, active=False, group=cgroup,
          description='Define dark dprtypes for threshold '
                      'quality control check (PP_DARK_THRES)')

# Define the threshold for a suitable dark dprtypes (above this will not be
#    processed)
CDict.add('DARK_THRES', value=None, dtype=float,
          source=__NAME__, active=False, group=cgroup,
          description='Define the threshold for a suitable dark '
                      'dprtypes (above this will not be processed)')

# Define allowed preprocess reference file types (PP DPRTYPE)
CDict.add('ALLOWED_PPM_TYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define allowed preprocess reference '
                      'filetypes (PP DPRTYPE)')

# Define the allowed number of sigma for preprocessing reference mask
CDict.add('PPM_MASK_NSIG', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define allowed preprocess reference mask '
                      'number of sigma')

# Define the bin to use to correct low level frequences. This value cannot
#   be smaller than the order footprint on the array as it would lead to a set
#   of NaNs in the downsized image
CDict.add('MEDAMP_BINSIZE', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='Define the bin to use to correct low '
                      'level frequences. This value cannot be '
                      'smaller than the order footprint on the '
                      'array as it would lead to a set of NaNs '
                      'in the downsized image')

# Define the amplitude of the flux-dependent along-readout-axis derivative
#     component
CDict.add('CX_AMP_FLUX', value=None,
          dtype=float, minimum=0.0, source=__NAME__,
          group=cgroup,
          description='Define the amplitude of the '
                      'flux-dependent along-readout-axis '
                      'derivative component')

# Define amplitude of the flux-dependent along-readout-axis 1st derivative
#     component
CDict.add('CX_AMP_DFLUX', value=None,
          dtype=float, minimum=0.0, source=__NAME__,
          group=cgroup,
          description='Define amplitude of the '
                      'flux-dependent along-readout-axis '
                      '2nd derivative component')

# Define amplitude of the flux-dependent along-readout-axis 2nd derivative
#     component
CDict.add('CX_AMP_D2FLUX', value=None,
          dtype=float, minimum=0.0, source=__NAME__,
          group=cgroup,
          description='Define amplitude of the '
                      'flux-dependent along-readout-axis '
                      '2nd derivative component')

# Define the partial APERO DPRTYPES which we should not do the science
#    capacitive coupling
CDict.add('NOSCI_CAPC_DPRTYPES', value=None,
          dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the partial APERO DPRTYPES '
                      'which we should not do the '
                      'science capacitive coupling')

# Define the default file type for pp_ref (used as --filtetype argument)
CDict.add('REF_FILETYPE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the default file type for pp_ref '
                      '(used as --filtetype argument)')

# =============================================================================
# CALIBRATION: DARK SETTINGS
# =============================================================================
cgroup = 'CAL.DARK'
CDict.add_group(cgroup, description='CALIBRATION.DARK: '
                                    'CALIBRATION: DARK SETTINGS')

# Min dark exposure time
CDict.add('QC_DARK_TIME', value=None, dtype=float, minimum=0.0,
          source=__NAME__, group=cgroup,
          description='Min dark exposure time')

# Max dark median level [ADU/s]
CDict.add('QC_MAX_DARKLEVEL', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Max dark median level [ADU/s]')

# Max fraction of dark pixels (percent)
CDict.add('QC_MAX_DARK', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description='Max fraction of dark pixels (percent)')

# Max fraction of dead pixels
CDict.add('QC_MAX_DEAD', value=None, dtype=float, source=__NAME__,
          group=cgroup, description='Max fraction of dead pixels')

# Defines the resized blue image
CDict.add('X_BLUE_LOW', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup,
          description='Defines the resized blue image')
CDict.add('X_BLUE_HIGH', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')
CDict.add('Y_BLUE_LOW', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')
CDict.add('Y_BLUE_HIGH', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')

# Defines the resized red image
CDict.add('X_RED_LOW', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup,
          description='Defines the resized red image')
CDict.add('X_RED_HIGH', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')
CDict.add('Y_RED_LOW', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')
CDict.add('Y_RED_HIGH', value=None, dtype=int, minimum=0,
          source=__NAME__, group=cgroup, description='')

# Define a bad pixel cut limit (in ADU/s)
CDict.add('CUTLIMIT', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description='Define a bad pixel cut limit (in ADU/s)')

# Defines the lower and upper percentiles when measuring the dark
CDict.add('QMIN', value=None, dtype=int, source=__NAME__,
          minimum=0, maximum=100, group=cgroup,
          description=('Defines the lower and upper percentiles when '
                       'measuring the dark'))
CDict.add('QMAX', value=None, dtype=int, source=__NAME__,
          minimum=0, maximum=100, group=cgroup, description='')

# The number of bins in dark histogram
CDict.add('HISTO_BINS', value=None, dtype=int, source=__NAME__,
          minimum=1, group=cgroup,
          description='The number of bins in dark histogram')

# The range of the histogram in ADU/s
CDict.add('HISTO_RANGE_LOW', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='The minimum of the histogram in ADU/s')
CDict.add('HISTO_RANGE_HIGH', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='The maximum of the histogram in ADU/s')

#  Define whether to use SKYDARK for dark corrections
CDict.add('USE_SKYDARK_CORR', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description=('Define whether to use SKYDARK for '
                       'dark corrections'))

#  If use_skydark_correction is True define whether we use
#     the SKYDARK only or use SKYDARK/DARK (whichever is closest)
CDict.add('USE_SKYDARK_ONLY', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('If use_skydark_correction is True define'
                       ' whether we use the SKYDARK only or use '
                       'SKYDARK/DARK (whichever is closest)'))

#  Define the allowed DPRTYPES for finding files for DARK_REF will
#      only find those types define by 'filetype' but 'filetype' must
#      be one of theses
CDict.add('ALLOWED_TYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('Define the allowed DPRTYPES for '
                       'finding files for DARK_REF will '
                       'only find those types define by '
                       'filetype but filetype must be one '
                       'of theses'))

# Define the file type to use by default in the dark reference code
# Must be a list even if only one given
CDict.add('REF_FILETYPE', value=None, dtype=list, dtypei=str, source=__NAME__,
          group=cgroup,
          description=('Define the file types to use by default in the '
                       'dark reference code. '
                       'Must be a list even if only one given.'))

# Define the maximum time span to combine dark files over (in hours)
CDict.add('REF_MTIME', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the maximum time span to '
                       'combine dark files over (in '
                       'hours)'))

# median filter size for dark reference
CDict.add('REF_MEDSIZE', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='median filter size for dark reference')

# define the maximum number of files to use in the dark reference
CDict.add('REF_MAXFILES', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='define the maximum number of files '
                      'to use in the dark reference')

# define the minimimum allowed exptime for dark files to be used in
#    dark ref
CDict.add('REF_MIN_EXPTIME', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='define the minimimum allowed exptime '
                      'for dark files to be used in')

# =============================================================================
# CALIBRATION: BAD PIXEL MAP SETTINGS
# =============================================================================
cgroup = 'CAL.BPIX'
CDict.add_group(cgroup, description='CALIBRATION.BAD_PIXEL_MAP: '
                                    'CALIBRATION: BAD PIXEL MAP SETTINGS')

# Defines the full detector flat file (located in the data folder)
CDict.add('FULL_FLAT', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Defines the full detector flat file '
                       '(located in the data folder)'))

# Percentile to normalise to when normalising and median filtering
#    image [percentage]
CDict.add('NORM_PERCENTILE', value=None,
          dtype=float, source=__NAME__,
          minimum=0.0, maximum=100.0, group=cgroup,
          description=('Percentile to normalise to when '
                       'normalising and median filtering '
                       'image [percentage]'))

# Define the median image in the x dimension over a boxcar of this width
CDict.add('FLAT_MED_WID', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Define the median image in the x '
                       'dimension over a boxcar of this '
                       'width'))

# Define the maximum differential pixel cut ratio
CDict.add('FLAT_CUT_RATIO', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the maximum differential '
                       'pixel cut ratio'))

# Define the illumination cut parameter
CDict.add('ILLUM_CUT', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description='Define the illumination cut parameter')

# Define the maximum flux in ADU/s to be considered too hot to be used
CDict.add('MAX_HOTPIX', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the maximum flux in ADU/s to '
                       'be considered too hot to be used'))

# Defines the threshold on the full detector flat file to deem pixels as good
CDict.add('FULL_THRES', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Defines the threshold on the full '
                       'detector flat file to deem pixels '
                       'as good'))

#   Defines areas that are large/small for bad pixel erosion
CDict.add('ERODE_SIZE', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('Defines areas that are large/small '
                       'for bad pixel erosion'))

#   Defines how much larger to make eroded bad pixel regions
CDict.add('DILATE_SIZE', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('Defines how much larger to make '
                       'eroded bad pixel regions'))

# =============================================================================
# CALIBRATION: BACKGROUND CORRECTION SETTINGS
# =============================================================================
cgroup = 'CAL.BCORR'
CDict.add_group(cgroup, description='CALIBRATION.BACKGROUND_CORRECTION: '
                                    'CALIBRATION: BACKGROUND CORRECTION '
                                    'SETTINGS')

#  Width of the box to produce the background mask
CDict.add('BKGR_BOXSIZE', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Width of the box to produce the background '
                       'mask'))

#  Do background percentile to compute minimum value (%)
CDict.add('BKGR_PERCENTAGE', value=None, dtype=float,
          source=__NAME__, minimum=0.0, maximum=100.0,
          group=cgroup,
          description=('Do background percentile to compute '
                       'minimum value (%)'))

#  Size in pixels of the convolve tophat for the background mask
CDict.add('BKGR_MASK_CSIZE', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description=('Size in pixels of the convolve '
                       'tophat for the background mask'))

#  If a pixel has this or more "dark" neighbours, we consider it dark
#      regardless of its initial value
CDict.add('NBAD_NEIGHBOURS', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('If a pixel has this or more "dark" '
                       'neighbours, we consider it dark '
                       'regardless of its initial value'))

#  Do not correct for background measurement (True or False)
CDict.add('NO_CORR', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('Do not correct for background '
                       'measurement (True or False)'))

#  Kernel amplitude determined from drs_local_scatter.py
#    If zero the scattering is skipped
CDict.add('KER_AMP', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description=('Kernel amplitude determined from '
                       'drs_local_scatter.py, '
                       'If zero the scattering is skipped'))

#  Background kernel width in x and y [pixels]
CDict.add('KER_WX', value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description='Background kernel width in x [pixels]')
CDict.add('KER_WY', value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description='Background kernel width in y [pixels]')

#  construct a convolution kernel. We go from -IC_BKGR_KER_SIG to
#      +IC_BKGR_KER_SIG sigma in each direction. Its important no to
#      make the kernel too big as this slows-down the 2D convolution.
#      Do NOT make it a -10 to +10 sigma gaussian!
CDict.add('KER_SIG', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description='construct a convolution kernel. We go from '
                      '-IC_KER_SIG to +IC_KER_SIG sigma '
                      'in each direction. Its important no to make '
                      'the kernel too big as this slows-down the '
                      '2D convolution. Do NOT make it a -10 to +10 '
                      'sigma gaussian!')

# =============================================================================
# CALIBRATION: LOCALISATION SETTINGS
# =============================================================================
cgroup = 'CAL.LOC'
CDict.add_group(cgroup, description='CALIBRATION.LOCALISATION: '
                                    'CALIBRATION: LOCALISATION SETTINGS')

# median-binning size in the dispersion direction. This is just used to
#     get an order-of-magnitude of the order profile along a given column
CDict.add('BINSIZE', value=None, dtype=int, source=__NAME__,
          group=cgroup, minimum=1,
          description='median-binning size in the dispersion '
                      'direction. This is just used to get an '
                      'order-of-magnitude of the order profile '
                      'along a given column')

# the zero point percentile of a box
CDict.add('BOX_PTILE_LOW', value=None,
          dtype=int, minimum=0, source=__NAME__,
          group=cgroup,
          description='the zero point percentile of a '
                      'box')

# the percentile of a box that is always an illuminated pixel
CDict.add('BOX_PTILE_HIGH', value=None,
          dtype=int, minimum=0, source=__NAME__,
          group=cgroup,
          description='the percentile of a box that is '
                      'always an illuminated pixel')

# the size of the percentile filter - should be a bit bigger than the
# inter-order gap
CDict.add('PTILE_FILTER_SIZE', value=None,
          minimum=1, dtype=int,
          source=__NAME__, group=cgroup,
          description='the size of the pecentile '
                      'filter - should be a bit '
                      'bigger than the inter-order '
                      'gap')

# the fiber dilation number of iterations this should only be used when
#     we want a combined localisation solution i.e. AB from A and B
CDict.add('FIBER_DILATE_ITRS', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=1,
          description='the fiber dilation number of '
                      'iterations this should only '
                      'be  used when we want a '
                      'combined  localisation '
                      'solution i.e. AB from A and B')

# the minimum area (number of pixels) that defines an order
CDict.add('MIN_ORDER_AREA', value=None, minimum=1,
          dtype=int, source=__NAME__, group=cgroup,
          description='the minimum area (number of pixels) '
                      'that defines an order')

# Order of polynomial to fit for widths
CDict.add('WID_POLYDEG', value=None, minimum=1,
          dtype=int, source=__NAME__, group=cgroup,
          description='Order of polynomial to fit for widths')

# Order of polynomial to fit for positions
CDict.add('CENT_POLYDEG', value=None, minimum=1,
          dtype=int, source=__NAME__, group=cgroup,
          description='Order of polynomial to fit for '
                      'positions')

# range width size (used to fit the width of the orders at certain points)
CDict.add('RANGE_WID_SUM', value=None, minimum=1,
          dtype=int, source=__NAME__, group=cgroup,
          description='range width size (used to fit the width '
                      'of the orders at certain points)')

# define the minimum detector position where the centers of the orders should
#   fall (across order direction)
CDict.add('YDET_MIN', value=None, dtype=int, source=__NAME__,
          group=cgroup, minimum=0,
          description='define the minimum detector position where '
                      'the centers of the orders should fall '
                      '(across order direction)')

# define the maximum detector position where the centers of the orders should
#   fall (across order direction)
CDict.add('YDET_MAX', value=None, dtype=int, source=__NAME__,
          group=cgroup, minimum=0,
          description='define the maximum detector position where '
                      'the centers of the orders should fall '
                      '(across order direction)')

# define the number of width samples to use in localisation
CDict.add('NUM_WID_SAMPLES', value=None, dtype=int,
          source=__NAME__, group=cgroup, minimum=1,
          description='define the number of width samples to '
                      'use in localisation')

# Size of the order_profile smoothed box
#   (from pixel - size to pixel + size)
CDict.add('ORDERP_BOXSIZE', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Size of the order_profile smoothed '
                       'box (from pixel - size to pixel '
                       '+ size)'))

# row number of image to start localisation processing at
CDict.add('START_ROW_OFFSET', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('row number of image to start '
                       'localisation processing at'))

# Definition of the central column for use in localisation
CDict.add('MIDDLE_PIXEL_COL', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Definition of the central column '
                       'for use in localisation'))

# Half spacing between orders
CDict.add('HALF_ORDER_SPACING', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description='Half spacing between orders')

# Minimum amplitude to accept (in e-)
CDict.add('MINPEAK_AMP', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Minimum amplitude to accept '
                       '(in e-)'))

# Normalised amplitude threshold to accept pixels for background calculation
CDict.add('BKGRD_THRES', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Normalised amplitude threshold to '
                       'accept pixels for background '
                       'calculation'))

# Define the amount we drop from the centre of the order when
#    previous order center is missed (in finding the position)
CDict.add('ORDER_CURVE_DROP', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the amount we drop from the '
                       'centre of the order when previous '
                       'order center is missed (in finding '
                       'the position)'))

# set the sigma clipping cut off value for cleaning coefficients
CDict.add('COEFF_SIGCLIP', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description=('set the sigma clipping cut off value '
                       'for cleaning coefficients'))

#  Defines the fit degree to fit in the coefficient cleaning
CDict.add('COEFFSIG_DEG', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('Defines the fit degree to fit in the '
                       'coefficient cleaning'))

#  Define the maximum value allowed in the localisation (cuts bluest orders)
CDict.add('MAX_YPIX_VAL', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description='Define the maximum value allowed in '
                      'the localisation (cuts bluest orders)')

#   Define the jump size when finding the order position
#       (jumps in steps of this from the center outwards)
CDict.add('COL_SEP_FITTING', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('Define the jump size when finding '
                       'the order position (jumps in '
                       'steps of this from the center '
                       'outwards)'))

# Definition of the extraction window size (half size)
CDict.add('EXT_WIN_SIZE', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('Definition of the extraction window '
                       'size (half size)'))

# Definition of the gap index in the selected area
CDict.add('IMAGE_GAP', value=None, dtype=int, source=__NAME__,
          minimum=0, group=cgroup,
          description=('Definition of the gap index in the '
                       'selected area'))

# Define minimum width of order to be accepted
CDict.add('ORDER_WID_MIN', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define minimum width of order to be '
                       'accepted'))

# Define the noise multiplier threshold in order to accept an
#     order center as usable i.e.
#     max(pixel value) - min(pixel value) > THRES * RDNOISE
CDict.add('NOISE_MULT_THRES', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Define the noise multiplier '
                       'threshold in order to accept '
                       'an order center as usable '
                       'i.e. max(pixel value) - '
                       'min(pixel value) > '
                       'THRES * RDNOISE'))

# Maximum rms for sigma-clip order fit (center positions)
CDict.add('MAX_RMS_CENT', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum rms for sigma-clip order fit '
                       '(center positions)'))

# Maximum peak-to-peak for sigma-clip order fit (center positions)
CDict.add('MAX_PTP_CENT', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum peak-to-peak for sigma-clip '
                       'order fit (center positions)'))

# Maximum frac ptp/rms for sigma-clip order fit (center positions)
CDict.add('PTP_RMS_CENT', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum frac ptp/rms for sigma-clip '
                       'order fit (center positions)'))

# Maximum rms for sigma-clip order fit (width)
CDict.add('MAX_RMS_WID', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum rms for sigma-clip order fit '
                       '(width)'))

# Maximum fractional peak-to-peak for sigma-clip order fit (width)
CDict.add('MAX_PTP_WID', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum fractional peak-to-peak for '
                       'sigma-clip order fit (width)'))

# Saturation threshold for localisation
CDict.add('SAT_THRES', value=None, dtype=float, source=__NAME__,
          minimum=0.0, group=cgroup,
          description='Saturation threshold for localisation')

# Maximum points removed in location fit
CDict.add('QL_MAXFIT_RM_CTR', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description=('Maximum points removed in '
                       'location fit'))

# Maximum points removed in width fit
CDict.add('QL_MAXFIT_RM_WID', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description=('Maximum points removed '
                       'in width fit'))

# Maximum rms allowed in fitting location
CDict.add('QC_RMSMAX_CTR', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum rms allowed in fitting '
                       'location'))

# Maximum rms allowed in fitting width
CDict.add('QC_RMSMAX_WID', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum rms allowed in fitting '
                       'width'))

# Option for archiving the location image
CDict.add('SAVE_SUPERIM_FILE', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description=('Option for archiving the '
                       'location image'))

# set the zoom in levels for the plots (xmin values)
CDict.add('PLOT_CX_ZOOM1', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('set the zoom in levels for '
                       'the plots (xmin values)'))

# set the zoom in levels for the plots (xmax values)
CDict.add('PLOT_CX_ZOOM2', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('set the zoom in levels for the '
                       'plots (xmax values)'))

# set the zoom in levels for the plots (ymin values)
CDict.add('PLOT_CY_ZOOM1', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('set the zoom in levels for the '
                       'plots (ymin values)'))

# set the zoom in levels for the plots (ymax values)
CDict.add('PLOT_CY_ZOOM2', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('set the zoom in levels for the '
                       'plots (ymax values)'))

# =============================================================================
# CALIBRATION: SHAPE SETTINGS
# =============================================================================
cgroup = 'CAL.SHAPE'
CDict.add_group(cgroup, description='CALIBRATION.SHAPE: '
                                    'CALIBRATION: SHAPE SETTINGS')

#  Define the allowed DPRTYPES for finding files for SHAPE_REF will
#      only find those types define by 'filetype' but 'filetype' must
#      be one of theses
CDict.add('ALLOWED_FP_TYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('Define the allowed DPRTYPES for finding '
                       'files for SHAPE_REF will only find '
                       'those types define by filetype but '
                       'filetype must be one of theses '))

# Define the maximum time span to combine fp files over (in hours)
CDict.add('FP_REF_MATCH_TIME', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the maximum time span to '
                       'combine fp files over (in hours)'))

# Define the percentile at which the FPs are normalised when getting the
#    fp reference in shape reference recipe
CDict.add('FP_REF_PERCENT_THRES', value=None,
          dtype=float, minimum=0, maximum=100,
          source=__NAME__, group=cgroup,
          description=('Define the percentile at which '
                       'the FPs are normalised when '
                       'getting the fp reference in shape '
                       'reference recipe'))

#  Define the largest standard deviation allowed for the shift in
#   x or y when doing the shape reference fp linear transform
CDict.add('QC_LTRANS_RTHRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the largest standard '
                       'deviation allowed for the '
                       'shift in x or y when doing the '
                       'shape reference fp linear '
                       'transform'))

# define the maximum number of files to use in the shape reference recipe
CDict.add('REF_MAX_FILES', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('define the maximum number of '
                       'files to use in the shape '
                       'reference recipe'))

#  Define the percentile which defines a true FP peak [0-100]
CDict.add('REF_VALIDFP_PTILE',
          value=None, dtype=float, minimum=0,
          maximum=100, source=__NAME__,
          group=cgroup,
          description=('Define the percentile '
                       'which defines a true FP '
                       'peak [0-100]'))

#  Define the fractional flux an FP much have compared to its neighbours
CDict.add('REF_VALIDFP_THRES',
          value=None, dtype=float, minimum=0,
          source=__NAME__, group=cgroup,
          description=('Define the fractional '
                       'flux an FP much have '
                       'compared to its neighbours'))

#  Define the number of iterations used to get the linear transform params
CDict.add('REF_LINTRANS_NITER', value=None,
          dtype=int, minimum=1, source=__NAME__,
          group=cgroup,
          description=('Define the number of '
                       'iterations used to get the '
                       'linear transform params'))

#  Define the initial search box size (in pixels) around the fp peaks
CDict.add('REF_FP_IBOXSIZE', value=None,
          dtype=int, minimum=1, source=__NAME__,
          group=cgroup,
          description=('Define the initial search '
                       'box size (in pixels) around '
                       'the fp peaks'))

#  Define the small search box size (in pixels) around the fp peaks
CDict.add('REF_FP_SBOXSIZE',
          value=None, dtype=int, minimum=1,
          source=__NAME__, group=cgroup,
          description=('Define the small search '
                       'box size (in pixels) '
                       'around the fp peaks'))

#  Define the minimum number of FP files in a group to mean group is valid
CDict.add('FP_REF_MIN_INGROUP', value=None,
          dtype=int, minimum=1, source=__NAME__,
          group=cgroup,
          description=('Define the minimum number '
                       'of FP files in a group to '
                       'mean group is valid'))

#  Define which fiber should be used for fiber-dependent calibrations in
#   shape reference recipe
CDict.add('REF_FIBER', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define which fiber should be used '
                       'for fiber-dependent calibrations '
                       'in shape reference'))

#  Define the shape reference dx rms quality control criteria (per order)
CDict.add('REF_DX_RMS_QC', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define the shape reference dx rms'
                      'quality control criteria (per '
                      'order)')

# The number of iterations to run the shape finding out to
CDict.add('NUM_ITER', value=None, dtype=int,
          minimum=1, source=__NAME__, group=cgroup,
          description=('The number of iterations to run '
                       'the shape finding out to'))

# The order to use on the shape plot
CDict.add('PLOT_SORDER', value=None,
          dtype=int, minimum=0, source=__NAME__,
          group=cgroup,
          description=('The order to use on the '
                       'shape plot'))

# The fit order to fit to the slope of the shape of the fibers
CDict.add('FIT_SLOPE_DEG', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description='width of the ABC fibers (in pixels)')

# number of sections per order to split the order into
CDict.add('NSECTIONS', value=None, dtype=int,
          minimum=1, source=__NAME__, group=cgroup,
          description='The fit order to fit to the slope of the shape '
                      'of the fibers')

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
CDict.add('LANGLE_MIN', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('the range of angles (in degrees) '
                       'for the first iteration (large) '
                       'and subsequent iterations (small)'))

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
CDict.add('LANGLE_MAX', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('the range of angles (in degrees) '
                       'for the first iteration (large) '
                       'and subsequent iterations (small)'))

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
CDict.add('SANGLE_MIN', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('the range of angles (in degrees) '
                       'for the first iteration (large) '
                       'and subsequent iterations (small)'))

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
CDict.add('SANGLE_MAX', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('the range of angles (in degrees) '
                       'for the first iteration (large) '
                       'and subsequent iterations (small)'))

# max sigma clip (in sigma) on points within a section
CDict.add('SIGCLIP_MAX', value=None, dtype=float,
          minimum=0.0, source=__NAME__, group=cgroup,
          description=('max sigma clip (in sigma) on points '
                       'within a section'))

# the size of the median filter to apply along the order (in pixels)
CDict.add('MED_FILT_SIZE', value=None,
          dtype=int, minimum=0, source=__NAME__,
          group=cgroup,
          description=('the size of the median filter '
                       'to apply along the order '
                       '(in pixels)'))

# The minimum value for the cross-correlation to be deemed good
CDict.add('MIN_GOOD_CORR', value=None,
          dtype=float, minimum=0.0, source=__NAME__,
          group=cgroup,
          description=('The minimum value for the '
                       'cross-correlation to be '
                       'deemed good'))

# Define the first pass (short) median filter width for dx
CDict.add('SHORT_DX_MEDFILT_WID', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the first pass (short) '
                       'median filter width for dx'))

# Define the second pass (long) median filter width for dx.
#  Used to fill NaN positions in dx that are not covered by short pass
CDict.add('LONG_DX_MEDFILT_WID', value=None,
          dtype=int, source=__NAME__, group=cgroup)

#  Defines the largest allowed standard deviation for a given
#  per-order and per-x-pixel shift of the FP peaks
CDict.add('QC_DXMAP_STD', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Defines the largest allowed standard '
                       'deviation for a given per-order and '
                       'per-x-pixel shift of the FP peaks'))

# defines the shape offset xoffset (before and after) fp peaks
CDict.add('XOFFSET', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('defines the shape offset xoffset '
                       '(before and after) fp peaks'))

# defines the bottom percentile for fp peak
CDict.add('OFF_BTM_PTILE',
          value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description=('defines the bottom '
                       'percentile for fp peak'))

# defines the top percentile for fp peak
CDict.add('OFF_TOP_PTILE', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('defines the top percentile '
                       'for fp peak'))

# defines the floor below which top values should be set to
# this fraction away from the max top value
CDict.add('OFF_TOP_FLOOR_FRAC', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('defines the floor below which '
                       'top values should be set to '
                       'this fraction away from the '
                       'max top value'))

# define the median filter to apply to the hc (high pass filter)]
CDict.add('OFF_MED_FILT_WID',
          value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description=('define the median filter to '
                       'apply to the hc (high pass '
                       'filter)]'))

# Maximum number of FP (larger than expected number
#    (~10000 to ~25000)
CDict.add('OFF_FPINDEX_MAX', value=None,
          dtype=int, source=__NAME__,
          minimum=10000, maximum=25000, group=cgroup,
          description=('Maximum number of FP (larger '
                       'than expected number (~10000 to '
                       '~25000)'))

# Define the valid length of a FP peak
CDict.add('OFF_VALID_FP_LEN', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the valid length of a'
                       ' FP peak'))

# Define the maximum allowed offset (in nm) that we allow for
#   the detector)
CDict.add('OFF_DRIFT_MARGIN', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the maximum allowed '
                       'offset (in nm) that we allow '
                       'for the detector)'))

# Define the number of iterations to do for the wave_fp
#   inversion trick
CDict.add('OFF_WAVEFP_INV_IT',
          value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description=('Define the number of '
                       'iterations to do for the '
                       'wave_fp inversion trick'))

# Define the border in pixels at the edge of the detector
CDict.add('OFF_MASK_BORDER', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the border in pixels at '
                       'the edge of the detector'))

# Define the minimum maxpeak value as a fraction of the
#  maximum maxpeak
CDict.add('OFF_MM_PEAK_FRAC', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the minimum maxpeak '
                       'value as a fraction of the '
                       'maximum maxpeak'))

# Define the width of the FP mask (+/- the center)
CDict.add('OFF_MASK_PWIDTH', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the width of the FP '
                       'mask (+/- the center)'))

# Define the width of the FP to extract (+/- the center)
CDict.add('OFF_MASK_EXTWID', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the width of the FP to '
                       'extract (+/- the center)'))

# Define the most deviant peaks - percentile from [min to max]
CDict.add('OFF_DEV_PMIN', value=None,
          dtype=float, minimum=0, maximum=100,
          source=__NAME__, group=cgroup,
          description=('Define the most deviant peaks - '
                       'percentile from [min to max]'))
CDict.add('OFF_DEV_PMAX', value=None,
          dtype=float, minimum=0, maximum=100,
          source=__NAME__, group=cgroup,
          description='')

# Define the maximum error in FP order assignment
#  we assume that the error in FP order assignment could range
#  from -50 to +50 in practice, it is -1, 0 or +1 for the cases we've
#  tested to date
CDict.add('OFF_FPMAX_NUMERR', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the maximum error in '
                       'FP order assignment we '
                       'assume that the error in FP '
                       'order assignment could range '
                       'from -50 to +50 in practice, '
                       'it is -1, 0 or +1 for the '
                       'cases weve tested to date'))

# The number of sigmas that the HC spectrum is allowed to be
#   away from the predicted (from FP) position
CDict.add('OFF_FIT_HC_SIG', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('The number of sigmas that the '
                       'HC spectrum is allowed to be '
                       'away from the predicted (from '
                       'FP) position'))

# Define the maximum allowed maximum absolute deviation away
#   from the error fit
CDict.add('OFF_MAXDEV_THRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the maximum allowed '
                       'maximum absolute deviation '
                       'away from the error fit'))

# very low thresholding values tend to clip valid points
CDict.add('OFF_ABSDEV_THRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('very low thresholding '
                       'values tend to clip valid '
                       'points'))

# define the names of the unique fibers (i.e. not AB) for use in
#   getting the localisation coefficients for dymap
CDict.add('UFIBERS', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('define the names of the unique '
                       'fibers (i.e. not AB) for use in '
                       'getting the localisation '
                       'coefficients for dymap'))

#  Define first zoom plot for shape local zoom debug plot
#     should be a string list (xmin, xmax, ymin, ymax)
CDict.add('LOCAL_PZOOM1', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('Define first zoom plot for shape local '
                       'zoom debug plot should be a string '
                       'list (xmin, xmax, ymin, ymax)'))

#  Define second zoom plot for shape local zoom debug plot
#     should be a string list (xmin, xmax, ymin, ymax)
CDict.add('LOCAL_PZOOM2', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('Define second zoom plot for shape '
                       'local zoom debug plot should be a '
                       'string list (xmin, xmax, ymin, ymax)'))

# =============================================================================
# CALIBRATION: FLAT SETTINGS
# =============================================================================
cgroup = 'CAL.FLAT'
CDict.add_group(cgroup, description='CALIBRATION.FLAT: '
                                    'CALIBRATION: FLAT SETTINGS')

# TODO: is blaze_size needed with sinc function?
# Half size blaze smoothing window
CDict.add('HALF_WINDOW', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='Half size blaze smoothing window')

# TODO: is blaze_cut needed with sinc function?
# Minimum relative e2ds flux for the blaze computation
CDict.add('BLAZE_THRES', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Minimum relative e2ds flux for the '
                       'blaze computation'))

# TODO: is blaze_deg needed with sinc function?
# The blaze polynomial fit degree
CDict.add('BLAZE_DEG', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='The blaze polynomial fit degree')

# Define the threshold, expressed as the fraction of the maximum peak, below
#    this threshold the blaze (and e2ds) is set to NaN
CDict.add('BLAZE_SCUT', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define the threshold, expressed as the '
                       'fraction of the maximum peak, below this '
                       'threshold the blaze (and e2ds) is set to '
                       'NaN'))

# Define the rejection threshold for the blaze sinc fit
CDict.add('BLAZE_SIGFIT', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define the rejection threshold for the '
                       'blaze sinc fit'))

# Define the hot bad pixel percentile level (using in blaze sinc fit)
CDict.add('BLAZE_BPTILE', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define the hot bad pixel percentile '
                       'level (using in blaze sinc fit)'))

# Define the number of times to iterate around blaze sinc fit
CDict.add('BLAZE_NITER', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup)

# Define the sinc fit median filter width (we want to fit the shape of the
#   order not line structures)
CDict.add('BLAZE_SINC_MED_SIZE', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup)

# Define the orders not to plot on the RMS plot should be a string
#     containing a list of integers
CDict.add('RMS_SKIP_ORDERS', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('Define the orders not to plot on the '
                       'RMS plot should be a string '
                       'containing a list of integers'))

# Maximum allowed RMS of flat field
CDict.add('QC_MAX_RMS', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description='Maximum allowed RMS of flat field')

# Define the order to plot in summary plots
CDict.add('PLOT_ORDER', value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description='Define the order to plot in summary plots')

# Define the high pass filter size in km/s
CDict.add('HIGHPASS_SIZE', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='Define the high pass filter size in '
                      'km/s')

# Define the number of pixels left and right of the center of the image to
# look at the flux at the edge of the orders
CDict.add('QC_FLUX_EDGE_MIDSIZE', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='Define the number of pixels  left and right of the '
                      'center of the image to look at the flux at the edge of '
                      'the orders')

# Define the fraction of flux allowed to be rejected from the combined left
# and right edges of an order (QC parameter in flat recipe)
CDict.add('QC_FLUX_EDGE_LIMIT', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description='Define the fraction of flux allowed to be rejected from '
                      'the combined left and right edges of an order '
                      '(QC parameter in flat recipe)')

# Define orders not to include in flux edge limit check
CDict.add('QC_FLUX_EDGE_IGNORE', value=None,  dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description='Define orders not to include in flux edge limit check')

# =============================================================================
# CALIBRATION: LEAKAGE SETTINGS
# =============================================================================
cgroup = 'CAL.LEAK'
# Define the types of input file allowed by the leakage reference recipe
CDict.add('ALLOWED_REF_TYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('Define the types of input file '
                       'allowed by the leakage reference '
                       'recipe'))

# define whether to always extract leak reference files
#      (i.e. overwrite existing files)
CDict.add('ALWAYS_EXTRACT', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('define whether to always extract '
                       'leak reference files (i.e. overwrite '
                       'existing files)'))

# define the type of file to use for leak reference solution
#    (currently allowed are 'E2DSFF') - must match with LEAK_EXTRACT_FILE
CDict.add('REF_EXT_TYPES', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('define the type of file to use for '
                       'leak reference solution (currently '
                       'allowed are E2DSFF) - must match with '
                       'LEAK_EXTRACT_FILE'))

# Define whether we want to correct leakage by default
CDict.add('CORRECT_LEAK', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define whether we want to correct '
                      'leakage by default')

# Define DPRTYPE in reference fiber to do correction
CDict.add('REF_TYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define DPRTYPE in reference fiber to do '
                      'correction')

# define the maximum number of files to use in the leak reference
CDict.add('REF_MAX_FILES', value=None, dtype=int,
          source=__NAME__, group=cgroup, minimum=0,
          description='define the maximum number of files to '
                      'use in the leak reference')

# define the type of file to use for the leak correction (currently allowed are
#     'E2DS_FILE' or 'E2DSFF_FILE' (linked to recipe definition outputs)
#     must match with LEAKREF_EXTRACT_TYPE
CDict.add('EXT_FILE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('define the type of file to use for the '
                       'leak correction (currently allowed are '
                       'E2DS_FILE or E2DSFF_FILE (linked to '
                       'recipe definition outputs) must match '
                       'with LEAKREF_EXTRACT_TYPE'))

# define the extraction files which are 2D images (i.e. order num x nbpix)
CDict.add('EXT2D_FILES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('define the extraction files which '
                       'are 2D images (i.e. order num x '
                       'nbpix)'))

# define the extraction files which are 1D spectra
CDict.add('EXT1D_FILES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('define the extraction files which '
                       'are 1D spectra'))

# define the thermal background percentile for the leak and leak reference
CDict.add('BCKGRD_PTILE', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('define the thermal background '
                       'percentile for the leak and '
                       'leak reference'))

# define the normalisation percentile for the leak and leak reference
CDict.add('NORM_PTILE', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('define the normalisation percentile '
                       'for the leak and leak reference'))

# define the e-width of the smoothing kernel for leak reference
CDict.add('REF_WSMOOTH', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('define the e-width of the smoothing kernel '
                       'for leak reference'))

# define the kernel size for leak reference
CDict.add('REF_KERSIZE', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description='define the kernel size for leak reference')

# define the lower bound percentile for leak correction
CDict.add('LOW_PTILE', value=None, dtype=float,
          source=__NAME__, minimum=0.0, maximum=100.0,
          group=cgroup,
          description=('define the lower bound percentile '
                       'for leak correction'))

# define the upper bound percentile for leak correction
CDict.add('HIGH_PTILE', value=None, dtype=float,
          source=__NAME__, minimum=0.0, maximum=100.0,
          group=cgroup)

# define the limit on surpious FP ratio (1 +/- limit)
CDict.add('BAD_RATIO_OFFSET', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('define the limit on surpious FP '
                       'ratio (1 +/- limit)'))

# =============================================================================
# CALIBRATION: EXTRACTION SETTINGS
# =============================================================================
cgroup = 'CAL.EXT'
CDict.add_group(cgroup, description='CALIBRATION.EXTRACTION: '
                                    'CALIBRATION: EXTRACTION SETTINGS')

#    Whether extraction code is done in quick look mode (do not use for
#       final products)
CDict.add('QUICKLOOK', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('Whether extraction code is done in quick '
                       'look mode (do not use for final '
                       'products)'))

#  Start order of the extraction in apero_flat if None starts from 0
CDict.add('START_ORDER', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Start order of the extraction in apero_flat '
                       'if None starts from 0'))

#  End order of the extraction in apero_flat if None ends at last order
CDict.add('END_ORDER', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('End order of the extraction in apero_flat if '
                       'None ends at last order'))

# Half-zone extraction width left side (formally plage1)
CDict.add('RANGE1', value=None,
          dtype=dict, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('Half-zone extraction width left side '
                       '(formally plage1)'))

# Half-zone extraction width right side (formally plage2)
CDict.add('RANGE2', value=None,
          dtype=dict, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('Half-zone extraction width right side '
                       '(formally plage2)'))

# Define the orders to skip extraction on (will set all order values
#    to NaN. If None no orders are skipped. If Not None should be a
#    string (valid python list)
CDict.add('SKIP_ORDERS', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('Define the orders to skip extraction on '
                       '(will set all order values to NaN. If '
                       'None no orders are skipped. If Not None '
                       'should be a string (valid python list)'))

#  Defines whether to run extraction with cosmic correction
CDict.add('COSMIC_CORR', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('Defines whether to run extraction '
                       'with cosmic correction'))

#  Define the percentage of flux above which we use to cut
CDict.add('COSMIC_SIGCUT', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define the number of sigmas away from '
                       'the median flux which we use to cut '
                       'cosmic rays'))

#  Defines the maximum number of iterations we use to check for cosmics
#      (for each pixel)
CDict.add('COSMIC_THRES', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Defines the maximum number of '
                       'iterations we use to check for '
                       'cosmics (for each pixel)'))

# Saturation level reached warning
CDict.add('QC_FLUX_MAX', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Saturation level reached warning')

# Define which extraction file to use for s1d creation
CDict.add('S1D_INTYPE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define which extraction file to use for '
                       's1d creation'))
# Define which extraction file (recipe definitons) linked to EXT_S1D_INTYPE
CDict.add('S1D_INFILE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define which extraction file (recipe '
                       'definitons) linked to EXT_S1D_INTYPE'))

# Define the start s1d wavelength (in nm)
CDict.add('S1D_WAVESTART', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the start s1d wavelength '
                       '(in nm)'))

# Define the end s1d wavelength (in nm)
CDict.add('S1D_WAVEEND', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description='Define the end s1d wavelength (in nm)')

#  Define the s1d spectral bin for S1D spectra (nm) when uniform in wavelength
CDict.add('S1D_BIN_UWAVE', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the s1d spectral bin for S1D '
                       'spectra (nm) when uniform in '
                       'wavelength'))

#  Define the s1d spectral bin for S1D spectra (km/s) when uniform in velocity
CDict.add('S1D_BIN_UVEL', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the s1d spectral bin for '
                       'S1D spectra (km/s) when uniform in '
                       'velocity'))

#  Define the s1d smoothing kernel for the transition between orders in pixels
CDict.add('S1D_EDGE_SSIZE', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description=('Define the s1d smoothing kernel '
                       'for the transition between '
                       'orders in pixels'))

#    Define dprtypes to calculate berv for
CDict.add('ALLOWED_BERV_DPRTYPES', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description=('Define dprtypes to calculate '
                       'berv for'))

#    Define which BERV calculation to use ('barycorrpy' or 'estimate' or 'None')
CDict.add('BERV_KIND', value=None, dtype=str, source=__NAME__,
          options=['barycorrpy', 'estimate', 'None'], group=cgroup,
          description=('Define which BERV calculation to use '
                       '(barycorrpy or estimate or None)'))

#   Define the barycorrpy iers file
CDict.add('BERV_IERS_FILE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the barycorrpy iers file')

#   Define the barycorrpy iers a url
CDict.add('BERV_IERS_AURL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the barycorrpy iers a url')

#   Define barycorrpy leap directory
CDict.add('BERV_LEAPDIR', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define barycorrpy leap directory')

#   Define whether to update leap seconds if older than 6 months
CDict.add('BERV_LEAPUPDATE', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('Define whether to update leap '
                       'seconds if older than 6 months'))

#    Define the accuracy of the estimate (for logging only) [m/s]
CDict.add('BERV_EST_ACC', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define the accuracy of the estimate '
                       '(for logging only) [m/s]'))

# Define the order to plot in summary plots
CDict.add('PLOT_ORDER', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Define the order to plot in '
                       'summary plots'))

# Define the wavelength lower bounds for s1d plots
#     (must be a string list of floats) defines the lower wavelength in nm
CDict.add('S1D_PLOT_ZOOM1', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description=('Define the wavelength lower '
                       'bounds for s1d plots (must be a '
                       'string list of floats) defines '
                       'the lower wavelength in nm'))

# Define the wavelength upper bounds for s1d plots
#     (must be a string list of floats) defines the upper wavelength in nm
CDict.add('S1D_PLOT_ZOOM2', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description=('Define the wavelength upper '
                       'bounds for s1d plots (must be a '
                       'string list of floats) defines '
                       'the upper wavelength in nm'))

# Photometric bands to use in peak-2-peak calculation (and their definitions)
CDict.add('MEAS_SNR_PHOT_BANDS', value=apero_base.PHOT_BANDS,
          dtype=dict, source=__NAME__, group=cgroup,
          description='Photometric bands to use in peak-2-peak calculation '
                       '(and their definitions)')

# =============================================================================
# CALIBRATION: THERMAL SETTINGS
# =============================================================================
cgroup = 'CAL.THERM'
CDict.add_group(cgroup, description='CALIBRATION.THERMAL: '
                                    'CALIBRATION: THERMAL SETTINGS')

# whether to apply the thermal correction to extractions
CDict.add('THERMAL_CORR', value=None, dtype=bool,
          source=__NAME__, user=True, active=False, group=cgroup,
          description='whether to apply the thermal correction '
                      'to extractions')

# define whether to always extract thermals (i.e. overwrite existing files)
CDict.add('ALWAYS_EXTRACT', value=None,
          dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='define whether to always extract '
                      'thermals (i.e. overwrite existing '
                      'files)')

# define the type of file to use for wave solution (currently allowed are
#    'E2DS' or 'E2DSFF')
CDict.add('EXTRACT_TYPE', value=None, dtype=str,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='define the type of file to use for '
                      'wave solution (currently allowed '
                      'are "E2DS" or "E2DSFF")')

# define DPRTYPEs we need to correct thermal background using
#  telluric absorption (TAPAS)
CDict.add('CORR_TYPE1', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('define DPRTYPEs we need to '
                       'correct thermal background using '
                       'telluric absorption (TAPAS)'))

# define DPRTYPEs we need to correct thermal background using
#   method 2
CDict.add('CORR_TYPE2', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('define DPRTYPEs we need to '
                       'correct thermal background '
                       'using method 2'))

# define the order to perform the thermal background scaling on
CDict.add('SCALE_ORDER', value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description=('define the order to perform the thermal '
                       'background scaling on'))

# width of the median filter used for the background
CDict.add('FILT_WID', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('width of the median filter used for '
                       'the background'))

# define thermal limit - below this we do not correct thermal emission
#   because we know from first principles that it should be too small
CDict.add('MIN_WAVE_LIM', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description='define thermal limit - below this '
                      'we do not correct thermal emission '
                      'because we know from first principles '
                      'that it should be too small')

# define thermal red limit (in nm)
CDict.add('RED_WAVE_LIM', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='define thermal red limit (in nm)')

# define thermal blue limit (in nm)
CDict.add('BLUE_WAVE_LIM', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='define thermal blue limit (in nm)')

# maximum tapas transmission to be considered completely opaque for the
# purpose of background determination in last order.
CDict.add('THRES_TAPAS', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('maximum tapas transmission to be '
                       'considered completely opaque for '
                       'the purpose of background '
                       'determination in last order.'))

# define the percentile to measure the background for correction type 2
CDict.add('ENVELOPE_PTILE', value=None,
          dtype=float, source=__NAME__,
          minimum=0, maximum=100, group=cgroup,
          description=('define the percentile to '
                       'measure the background for '
                       'correction type 2'))

# define the order to plot on the thermal debug plot
CDict.add('PLOT_START_ORDER', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('define the order to plot on the '
                       'thermal debug plot'))

# define the dprtypes for which to apply the excess emissivity file
CDict.add('EXCESS_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('define the dprtypes for which '
                       'to apply the excess emissivity '
                       'file'))

# define the thermal emissivity file
CDict.add('EXCESS_EMISSIVITY_FILE',
          value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='define the thermal '
                      'emissivity file')

# =============================================================================
# CALIBRATION: WAVE GENERAL SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.GEN'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_GENERAL: '
                                    'CALIBRATION: WAVE EA GENERAL SETTINGS')

# Define the coefficients of the fit of wavelength vs d
CDict.add('CAVITY_LL_FILE', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description=('Define the coefficients of the fit of '
                       'wavelength vs d'))

# Define wave reference fiber (controller fiber)
CDict.add('REF_FIBER', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define wave reference fiber (controller '
                      'fiber)')

# Define the initial value of FP effective cavity width 2xd in nm
CDict.add('GUESS_CAVITY_WID', value=None,
          dtype=float, minimum=0,
          source=__NAME__, group=cgroup,
          description='Define the initial value of FP '
                      'effective cavity width 2xd in nm')

# Define the wave solution polynomial fit degree
CDict.add('WAVESOL_FIT_DEG', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=0, maximum=20,
          description='Define the wave solution '
                      'polynomial fit degree')

# Define the cavity fit polynomial fit degree for wave solution
#   Note default: 9 for spirou  3 for NIRPS
CDict.add('CAVITY_FIT_DEG', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=0, maximum=20,
          description='Define the cavity fit polynomial '
                      'fit degree for wave solution')

# Define the number of sigmas to use in wave sol robust fits
CDict.add('NSIG_CUT', value=None, dtype=int, source=__NAME__,
          group=cgroup, minimum=0, maximum=20,
          description='Define the number of sigmas to use in wave '
                      'sol robust fits')

# Define the minimum number of HC lines in an order to try to find
#   absolute numbering
CDict.add('MIN_HC_LINES', value=None, dtype=int,
          source=__NAME__, group=cgroup, minimum=1,
          description='Define the minimum number of HC lines '
                      'in an order to try to find absolute '
                      'numbering')

# Define the minimum number of FP lines in an order to try to find
#   absolute numbering
CDict.add('MIN_FP_LINES', value=None, dtype=int,
          source=__NAME__, group=cgroup, minimum=1,
          description='Define the minimum number of FP lines '
                      'in an order to try to find absolute '
                      'numbering')

# Define the maximum offset in FP peaks to explore when FP peak counting
CDict.add('MAX_FP_COUNT_OFFSET', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=1,
          description='Define the maximum offset in FP '
                      'peaks to explore when FP peak '
                      'counting')

# Define the number of iterations required to converge the FP peak counting
#   offset loop
CDict.add('FP_COUNT_OFFSET_ITRS', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=1,
          description='Define the number of iterations '
                      'required to converge the FP '
                      'peak counting offset loop')

# Define the number of iterations required to converge on a cavity fit
#  (first time this is done)
CDict.add('CAVITY_FIT_ITRS1', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=1,
          description='Define the number of iterations '
                      'required to converge on a cavity '
                      'fit (first time this is done)')

# Define the number of iterations required to check order offset
CDict.add('ORDER_OFFSET_ITRS', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=1,
          description='Define the number of iterations '
                      'required to check order offset')

# Define the maximum bulk offset of lines in a order can have
CDict.add('MAX_ORDER_BULKOFFSET', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=1,
          description='Define the maximum bulk '
                      'offset of lines in a order '
                      'can have')

# Define the required precision that the cavity width change must converge
#   to (will be a fraction of the error)
CDict.add('DCAVITY_ERR_THRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0,
          description='Define the required precision'
                      ' that the cavity width change'
                      ' must converge  to (will be '
                      'a fraction of the error)')

# Define the number of iterations required to converge on a cavity fit
#  (second time this is done)
CDict.add('CAVITY_FIT_ITRS2', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=1,
          description='Define the number of iterations '
                      'required to converge on a cavity '
                      'fit (second time this is done)')

# Define the odd ratio that is used in generating the weighted mean
CDict.add('HC_VEL_ODDRATIO', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0,
          description='Define the odd ratio that is used '
                      'in generating the weighted mean')

# Define orders that we cannot fit HC or FP lines to (list of strings)
CDict.add('REMOVE_ORDERS', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description='Define orders that we cannot fit HC '
                      'or FP lines to (list of strings)')

# Define the number of iterations required to do the final fplines
#   wave solution
CDict.add('FWAVESOL_ITRS', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          minimum=0,
          description='Define the number of iterations '
                      'required to do the final fplines '
                      'wave solution')

# define the wave fiber comparison plot order number
CDict.add('FIBER_COMP_PLOT_ORD', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description=('define the wave fiber '
                       'comparison plot order number'))

# Define the HC catalogue file
CDict.add('HC_CAT_FILE', value=None, dtype=str, source=__NAME__, group=cgroup,
          description='Define the HC catalogue file')

# Define the line list file (located in the DRS_WAVE_DATA directory)
CDict.add('LINELIST_FILE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the line list file (located in '
                       'the DRS_WAVE_DATA directory)'))

# Define the line list file format (must be astropy.table format)
CDict.add('LINELIST_FMT', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the line list file format (must '
                       'be astropy.table format)'))

# Define the line list file column names
# and must be equal to the number of columns in file)
CDict.add('LINELIST_COLS', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('Define the line list file column '
                       'names and must be equal to the number '
                       'of columns in file)'))

# Define the line list file row the data starts
CDict.add('LINELIST_START', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Define the line list file row the '
                       'data starts'))

# Define the line list file wavelength column and amplitude column
#  Must be in WAVE_LINELIST_COLS
CDict.add('LINELIST_WAVECOL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the line list file '
                       'wavelength column and amplitude '
                       'column Must be in '
                       'WAVE_LINELIST_COLS'))
CDict.add('LINELIST_AMPCOL', value=None, dtype=str,
          source=__NAME__, group=cgroup, description='')

# define whether to always extract HC/FP files in the wave code (even if they
#    have already been extracted
CDict.add('ALWAYS_EXTRACT', value=None, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='define whether to always extract '
                      'HC/FP files in the wave code '
                      '(even if they')

# define the type of file to use for wave solution (currently allowed are
#    'E2DS' or 'E2DSFF'
CDict.add('EXTRACT_TYPE', value=None, dtype=str,
          source=__NAME__, options=['E2DS', 'E2DSFF'],
          user=True, active=False, group=cgroup,
          description='define the type of file to use for '
                      'wave solution (currently allowed '
                      'are "E2DS" or "E2DSFF"')

# Define intercept and slope for a pixel shift
CDict.add('PIXEL_SHIFT_INTER', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define intercept and slope for a '
                       'pixel shift'))
CDict.add('PIXEL_SHIFT_SLOPE', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='')

#  Defines echelle of first extracted order
CDict.add('TORDER_START', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Defines echelle of first extracted '
                       'order'))

#  Defines order from which the solution is calculated
CDict.add('NORD_START', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Defines order from which the solution '
                       'is calculated'))

#  Defines order to which the solution is calculated
CDict.add('NORD_FINAL', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('Defines order to which the solution is '
                       'calculated'))


# =============================================================================
# CALIBRATION: WAVE LINES REFERENCE SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.LL'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_LINES_REFERENCE: '
                                    'CALIBRATION: WAVE LINES REFERENCE '
                                    'SETTINGS')

# min SNR to consider the line (for HC)
CDict.add('NSIG_MIN_HC', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description='min SNR to consider the line')

# min SNR to consider the line (for FP)
CDict.add('NSIG_MIN_FP', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description='min SNR to consider the line')

# minimum distance to the edge of the array to consider a line
CDict.add('REF_EDGE_WMAX', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('minimum distance to the edge of the '
                       'array to consider a line'))

# value in pixel (+/-) for the box size around each HC line to perform fit
CDict.add('REF_HC_BOXSIZE', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('value in pixel (+/-) for the box size '
                       'around each HC line to perform fit'))

# get valid hc dprtypes
CDict.add('REF_HC_FIBTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='get valid hc dprtypes')

# get valid fp dprtypes
CDict.add('REF_FP_FIBTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup)

# get the degree to fix reference wavelength to in hc mode
CDict.add('REF_FITDEG', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('get the degree to fix reference wavelength '
                       'to in hc mode'))

# define the lowest N for fp peaks
CDict.add('REF_FP_NLOW', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description='define the lowest N for fp peaks')

# define the highest N for fp peaks
CDict.add('REF_FP_NHIGH', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description='define the highest N for fp peaks')

# define the number of iterations required to do the FP polynomial inversion
CDict.add('REF_FP_POLYINV', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('define the number of iterations '
                       'required to do the FP polynomial '
                       'inversion'))

# define the guess HC exponetial width [pixels]
CDict.add('REF_HC_GUESS_EWID', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description=('define the guess HC exponetial '
                       'width [pixels]'))

# Define the fiber offset (in pixels) away from reference fiber
CDict.add('FIBER_OFFSET_MOD', value=None,
          dtype=dict, dtypei=float,
          source=__NAME__, group=cgroup,
          description='Define the fiber offset (in pixels) '
                      'away from reference fiber')

# Define the fiber scale factor from reference fiber
CDict.add('FIBER_SCALE_MOD', value=None,
          dtype=dict, dtypei=float,
          source=__NAME__, group=cgroup,
          description='Define the fiber scale factor '
                      'from reference fiber')

# =============================================================================
# CALIBRATION: WAVE RESOLUTION MAP SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.RESMAP'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_RES_MAP: '
                                    'CALIBRATION: WAVE RESOLUTION MAP SETTINGS')

# define the number of bins in order direction to use in the resolution map
CDict.add('ORDER_BINS', value=None, dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description='define the number of bins in '
                      'order direction to use in the '
                      'resolution map')

# define the number of bins in spatial direction to use in the resolution map
CDict.add('SPATIAL_BINS', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description='define the number of bins in '
                      'spatial direction to use in the '
                      'resolution map')

# define the low pass filter size for the HC E2DS file in the resolution map
CDict.add('FILT_SIZE', value=None,
          dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description='define the low pass filter size '
                      'for the HC E2DS file in the '
                      'resolution map')

# define the broad resolution map velocity cut off (in km/s)
CDict.add('VEL_CUTOFF1', value=None,
          dtype=float, source=__NAME__, minimum=0,
          group=cgroup,
          description='define the broad resolution map '
                      'velocity cut off (in km/s)')

# define the tight resolution map velocity cut off (in km/s)
CDict.add('VEL_CUTOFF2', value=None,
          dtype=float, source=__NAME__, minimum=0,
          group=cgroup,
          description='define the tight resolution map '
                      'velocity cut off (in km/s)')

# =============================================================================
# CALIBRATION: WAVE CCF SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.CCF'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_CCF: '
                                    'CALIBRATION: WAVE CCF SETTINGS')

#   The value of the noise for wave dv rms calculation
#       snr = flux/sqrt(flux + noise^2)
CDict.add('NOISE_SIGDET', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,

          description=('The value of the noise for wave '
                       'dv rms calculation '
                       '\n\tsnr = flux/sqrt(flux + '
                       'noise^2)'))

#   The size around a saturated pixel to flag as unusable for wave dv rms
#      calculation
CDict.add('NOISE_BOXSIZE', value=None, dtype=int,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('The size around a saturated pixel '
                       'to flag as unusable for wave dv '
                       'rms calculation'))

#   The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
CDict.add('NOISE_THRES', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('The maximum flux for a good '
                       '(unsaturated) pixel for wave dv '
                       'rms calculation'))

#   The CCF step size to use for the FP CCF
CDict.add('STEP', value=None, dtype=float, source=__NAME__,
          minimum=0.0, group=cgroup,
          description='The CCF step size to use for the FP CCF')

#   The CCF width size to use for the FP CCF
CDict.add('WIDTH', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description='The CCF width size to use for the FP CCF')

#   The target RV (CCF center) to use for the FP CCF
CDict.add('TARGET_RV', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('The target RV (CCF center) to use for '
                       'the FP CCF'))

#  The detector noise to use for the FP CCF
CDict.add('DETNOISE', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('The detector noise to use for the '
                       'FP CCF'))

#  The filename of the CCF Mask to use for the FP CCF
CDict.add('MASK', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description=('The filename of the CCF Mask to use for '
                       'the FP CCF'))

# Define the default CCF MASK normalisation mode for FP CCF
#   options are:
#     'None'         for no normalization
#     'all'          for normalization across all orders
#     'order'        for normalization for each order
CDict.add('MASK_NORM', value=None,
          dtype=str, options=['None', 'all', 'order'],
          source=__NAME__, group=cgroup,
          description=('Define the default CCF MASK '
                       'normalisation mode for FP CCF '
                       '\noptions are: '
                       '\n\tNone for no normalization '
                       '\n\tall for normalization '
                       'across all orders'
                       '\n\torder for normalization '
                       'for each order'))

# Define the wavelength units for the mask for the FP CCF
CDict.add('MASK_UNITS', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the wavelength units for '
                       'the mask for the FP CCF'))

# Define the ccf mask path the FP CCF
CDict.add('MASK_PATH', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the ccf mask path the FP CCF')

# Define the CCF mask format (must be an astropy.table format)
CDict.add('MASK_FMT', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the CCF mask format (must be an '
                       'astropy.table format)'))

#  Define the weight of the CCF mask (if 1 force all weights equal)
CDict.add('MASK_MIN_WEIGHT', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the weight of the CCF '
                       'mask (if 1 force all weights '
                       'equal)'))

#  Define the width of the template line (if 0 use natural)
CDict.add('MASK_WIDTH', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define the width of the template '
                       'line (if 0 use natural)'))

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#      to calculate the FP CCF
CDict.add('NORD_MAX', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('Define the number of orders (from '
                       'zero to ccf_num_orders_max) to use '
                       'to calculate the FP CCF'))

#  Define whether to regenerate the fp mask (WAVE_CCF_MASK) when we
#      update the cavity width in the reference wave solution recipe
CDict.add('UPDATE_MASK', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('Define whether to regenerate the '
                       'fp mask (WAVE_CCF_MASK) when we '
                       'update the cavity width in the '
                       'reference wave solution recipe'))

# define the width of the lines in the smart mask [km/s]
CDict.add('SMART_MASK_WID', value=None,
          dtype=float, source=__NAME__,
          minimum=0, group=cgroup,
          description=('define the width of the lines '
                       'in the smart mask [km/s]'))

# define the minimum wavelength for the smart mask [nm]
CDict.add('SMART_MASK_MINLAM', value=None,
          dtype=float, source=__NAME__,
          minimum=0, group=cgroup,
          description=('define the minimum wavelength '
                       'for the smart mask [nm]'))

# define the maximum wavelength for the smart mask [nm]
CDict.add('SMART_MASK_MAXLAM', value=None,
          dtype=float, source=__NAME__,
          minimum=0, group=cgroup,
          description=('define the maximum wavelength '
                       'for the smart mask [nm]'))

# define a trial minimum FP N value (should be lower than true
#     minimum FP N value)
CDict.add('SMART_MASK_TRIAL_NMIN',
          value=None, dtype=int, source=__NAME__,
          minimum=0, group=cgroup,
          description='define a trial minimum FP '
                      'N value (should be lower '
                      'than true minimum FP N '
                      'value)')

# define a trial maximum FP N value (should be higher than true
#     maximum FP N value)
CDict.add('SMART_MASK_TRIAL_NMAX',
          value=None, dtype=int, source=__NAME__,
          minimum=0, group=cgroup,
          description=('define a trial maximum FP '
                       'N value (should be higher '
                       'than true maximum FP N '
                       'value)'))

# define the converges parameter for dwave in smart mask generation
CDict.add('SMART_MASK_DWAVE_THRES',
          value=None, dtype=float,
          source=__NAME__, minimum=0,
          group=cgroup,
          description=('define the converges '
                       'parameter for dwave '
                       'in smart mask '
                       'generation'))

# define the quality control threshold from RV of CCF FP between reference
#    fiber and other fibers, above this limit fails QC [m/s]
CDict.add('RV_THRES_QC', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description=('define the quality control '
                       'threshold from RV of CCF FP between '
                       'reference fiber and other fibers, '
                       'above this limit fails QC [m/s]'))

# =============================================================================
# CALIBRATION: WAVE HC SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.HC'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_HC: '
                                    'CALIBRATION: WAVE HC SETTINGS')

# Define the mode to calculate the hc wave solution
CDict.add('MODE', value=None, dtype=int, source=__NAME__,
          options=[0], user=True, active=False, group=cgroup,
          description='Define the mode to calculate the hc '
                      'wave solution')

# width of the box for fitting HC lines. Lines will be fitted from -W to +W,
#     so a 2*W+1 window
CDict.add('HC_FITBOX_SIZE', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('width of the box for fitting HC '
                       'lines. Lines will be fitted from -W '
                       'to +W, so a 2*W+1 window'))

# number of sigma above local RMS for a line to be flagged as such
CDict.add('FITBOX_SIGMA', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('number of sigma above local RMS for '
                       'a line to be flagged as such'))

# the fit degree for the wave hc gaussian peaks fit
CDict.add('FITBOX_GFIT_DEG', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('the fit degree for the wave hc '
                       'gaussian peaks fit'))

# the RMS of line-fitted line must be between DEVMIN and DEVMAX of the peak
#     value must be SNR>5 (or 1/SNR<0.2)
CDict.add('FITBOX_RMS_DEVMIN', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('the RMS of line-fitted line '
                       'must be between DEVMIN and '
                       'DEVMAX of the peak value must '
                       'be SNR>5 (or 1/SNR<0.2)'))
CDict.add('FITBOX_RMS_DEVMAX', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup, description='')

# the e-width of the line expressed in pixels.
CDict.add('FITBOX_EWMIN', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('the e-width of the line expressed '
                       'in pixels.'))
CDict.add('FITBOX_EWMAX', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description='')

# define the file type for saving the initial guess at the hc peak list
CDict.add('LL_FILEFMT', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('define the file type for saving the '
                        'initial guess at the hc peak list'))

# number of bright lines kept per order
#     avoid >25 as it takes super long
#     avoid <12 as some orders are ill-defined and we need >10 valid
#         lines anyway
#     20 is a good number, and we see no reason to change it
CDict.add('NMAX_BRIGHT', value=None, dtype=int,
          source=__NAME__, minimum=10, maximum=30,
          group=cgroup,
          description=('number of bright lines kept per '
                       'order avoid >25 as it takes super '
                       'long avoid <12 as some orders are '
                       'ill-defined and we need >10 valid '
                       'lines anyway 20 is a good number, '
                       'and we see no reason to change it'))

# Number of times to run the fit triplet algorithm
CDict.add('NITER_FIT_TRIPLET', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description=('Number of times to run the fit '
                       'triplet algorithm'))

# Maximum distance between catalog line and init guess line to accept
#     line in m/s
CDict.add('MAX_DV_CATLL_GUESS', value=None,
          dtype=int, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Maximum distance between '
                       'catalog line and init guess '
                       'line to accept line in m/s'))

# The fit degree between triplets
CDict.add('TFIT_DEG', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description='The fit degree between triplets')

# Cut threshold for the triplet line fit [in km/s]
CDict.add('TFIT_CUT_THRES', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Cut threshold for the triplet '
                       'line fit [in km/s]'))

# Minimum number of lines required per order
CDict.add('TFIT_MIN_NLINES', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description=('Minimum number of lines '
                       'required per order'))

# Minimum total number of lines required
CDict.add('TFIT_MIN_TLINES', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description=('Minimum total number of '
                       'lines required'))

# this sets the order of the polynomial used to ensure continuity
#     in the  xpix vs wave solutions by setting the first term = 12,
#     we force that the zeroth element of the xpix of the wavelegnth
#     grid is fitted with a 12th order polynomial as a function of
#     order number
CDict.add('TFIT_ORDER_FIT_CONT', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('this sets the order of the '
                       'polynomial used to ensure '
                       'continuity in the xpix vs '
                       'wave solutions by setting '
                       'the first term = 12, we '
                       'force that the zeroth '
                       'element of the xpix of the '
                       'wavelegnth grid is fitted '
                       'with a 12th order polynomial '
                       'as a function of order '
                       'number'))

# Number of times to loop through the sigma clip for triplet fit
CDict.add('TFIT_SIGCLIP_NUM', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description=('Number of times to loop through '
                       'the sigma clip for triplet fit'))

# Sigma clip threshold for triplet fit
CDict.add('TFIT_SIGCLIP_THRES', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Sigma clip threshold for '
                       'triplet fit'))

# Define the distance in m/s away from the center of dv hist points
#     outside will be rejected [m/s]
CDict.add('TFIT_DVCUT_ORDER', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Define the distance in m/s away '
                       'from the center of dv hist '
                       'points outside will be rejected '
                       '[m/s]'))
CDict.add('TFIT_DVCUT_ALL', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup, description='')

# Define the resolution and line profile map size (y-axis by x-axis)
CDict.add('RESMAP_SIZE', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description=('Define the resolution and line '
                       'profile map size (y-axis by x-axis)'))

# Define the maximum allowed deviation in the RMS line spread function
CDict.add('RES_MAXDEV_THRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the maximum allowed '
                       'deviation in the RMS line '
                       'spread function'))

# quality control criteria if sigma greater than this many sigma fails
CDict.add('QC_SIG_MAX', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('quality control criteria if sigma '
                       'greater than this many sigma fails'))

# Defines the dv span for PLOT_WAVE_HC_RESMAP debug plot, should be a
#    string list containing a min and max dv value
CDict.add('RESMAP_DVSPAN', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description=('Defines the dv span for '
                       'PLOT_WAVE_HC_RESMAP debug plot, '
                       'should be a string list '
                       'containing a min and max dv '
                       'value'))

# Defines the x limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
#   string list containing a min and max x value
CDict.add('RESMAP_XLIM', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description=('Defines the x limits for '
                       'PLOT_WAVE_HC_RESMAP debug plot, '
                       'should be a string list containing '
                       'a min and max x value'))

# Defines the y limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
#   string list containing a min and max y value
CDict.add('RESMAP_YLIM', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description=('Defines the y limits for '
                       'PLOT_WAVE_HC_RESMAP debug plot, '
                       'should be a string list containing a '
                       'min and max y value'))

# Define whether to fit line profiles with "gaussian" or "super-gaussian"
CDict.add('RESMAP_FITTYPE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define whether to fit line '
                      'profiles with "gaussian" or '
                      '"super-gaussian"')

# Define the sigma clip for line profiles for the resolution map
CDict.add('RESMAP_SIGCLIP', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='Define the sigma clip for line '
                      'profiles for the resolution map')

# =============================================================================
# CALIBRATION: WAVE LITTROW SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.LIT'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_LITTROW: '
                                    'CALIBRATION: WAVE LITTROW SETTINGS')

#  Define the order to start the Littrow fit from for the HC wave solution
CDict.add('ORDER_INIT1', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the order to start the '
                       'Littrow fit from for the HC '
                       'wave solution'))

#  Define the order to start the Littrow fit from for the FP wave solution
# TODO: Note currently used
CDict.add('ORDER_INIT2', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the order to start the '
                       'Littrow fit from for the FP '
                       'wave solution'))

#  Define the order to end the Littrow fit at for the HC wave solution
CDict.add('ORDER_FINAL1', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the order to end the '
                       'Littrow fit at for the HC '
                       'wave solution'))

#  Define the order to end the Littrow fit at for the FP wave solution
# TODO: Note currently used
CDict.add('ORDER_FINAL2', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the order to end the '
                       'Littrow fit at for the FP '
                       'wave solution'))

#  Define orders to ignore in Littrow fit
CDict.add('REMOVE_ORDERS', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description=('Define orders to ignore in '
                       'Littrow fit'))

#  Define the littrow cut steps for the HC wave solution
CDict.add('CUT_STEP1', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the littrow cut steps for '
                       'the HC wave solution'))

#  Define the littrow cut steps for the FP wave solution
CDict.add('CUT_STEP2', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the littrow cut steps for '
                       'the FP wave solution'))

#  Define the fit polynomial order for the Littrow fit (fit across the orders)
#    for the HC wave solution
CDict.add('FIG_DEG1', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the fit polynomial order '
                       'for the Littrow fit (fit across '
                       'the orders) for the HC wave '
                       'solution'))

#  Define the fit polynomial order for the Littrow fit (fit across the orders)
#    for the FP wave solution
CDict.add('FIG_DEG2', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the fit polynomial order '
                       'for the Littrow fit (fit across '
                       'the orders) for the FP wave '
                       'solution'))

#  Define the order fit for the Littrow solution (fit along the orders)
# TODO needs to be the same as ic_ll_degr_fit
CDict.add('EXT_ORDER_FIT_DEG',
          value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description=('Define the order fit for '
                       'the Littrow solution (fit '
                       'along the orders) TODO '
                       'needs to be the same as '
                       'ic_ll_degr_fit'))

#   Maximum littrow RMS value
CDict.add('QC_RMS_MAX', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='Maximum littrow RMS value')

#   Maximum littrow Deviation from wave solution (at x cut points)
CDict.add('QC_DEV_MAX', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Maximum littrow Deviation from '
                       'wave solution (at x cut points)'))

# =============================================================================
# CALIBRATION: WAVE FP SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.FP'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_FP: '
                                    'CALIBRATION: WAVE FP SETTINGS')

# Define the mode to calculate the fp wave solution
CDict.add('MODE', value=None, dtype=int, source=__NAME__,
          options=[0, 1], user=True, active=False, group=cgroup,
          description='Define the mode to calculate the fp '
                      'wave solution')

# Define the initial value of FP effective cavity width 2xd in nm
CDict.add('DOPD0', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the initial value of FP effective '
                       'cavity width 2xd in nm'))

#  Define the polynomial fit degree between FP line numbers and the
#      measured cavity width for each line
CDict.add('CAVFIT_DEG', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Define the polynomial fit degree '
                       'between FP line numbers and the '
                       'measured cavity width for each line'))

#  Define the FP jump size that is too large
CDict.add('LARGE_JUMP', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Define the FP jump size that is too '
                       'large'))

# index of FP line to start order cross-matching from
CDict.add('CROSSM_INDEX', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('index of FP line to cross-match from'))

# define the percentile to normalize the spectrum to (per order)
#  used to determine FP peaks (peaks must be above a normalised limit
#   defined in WAVE_FP_PEAK_LIM
CDict.add('NORM_PTILE', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('define the percentile to '
                       'normalize the spectrum to '
                       '(per order) used to determine FP '
                       'peaks (peaks must be above a '
                       'normalised limit defined in '
                       'WAVE_FP_PEAK_LIM'))

# define the normalised limit below which FP peaks are not used
CDict.add('PEAK_LIM', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('define the normalised limit below which '
                       'FP peaks are not used'))

#    Define pixel to pixel width that is too large (removed from FP peaks)
CDict.add('P2P_WID_CUT', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Define pixel to pixel width that is '
                       'too large (removed from FP peaks)'))

# Define the minimum instrumental error
CDict.add('ERR_XMIN', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description='Define the minimum instrumental error')

#  Define the wavelength fit polynomial order
CDict.add('LL_DEGR_FIT', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Define the wavelength fit polynomial '
                       'order'))

#  Define the max rms for the wavelength sigma-clip fit
CDict.add('MAX_LLFIT_RMS', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Define the max rms for the '
                       'wavelength sigma-clip fit'))

#  Define the weight threshold (small number) below which we do not keep fp
#     lines
CDict.add('WEIGHT_THRES', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the weight threshold (small '
                       'number) below which we do not keep '
                       'fp lines'))

# Minimum blaze threshold to keep FP peaks
CDict.add('BLAZE_THRES', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Minimum blaze threshold to keep '
                       'FP peaks'))

# Minimum FP peaks pixel separation fraction diff. from median
CDict.add('XDIF_MIN', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Minimum FP peaks pixel separation '
                       'fraction diff. from median'))

# Maximum FP peaks pixel separation fraction diff. from median
CDict.add('XDIF_MAX', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum FP peaks pixel separation '
                       'fraction diff. from median'))

# Maximum fract. wavelength offset between cross-matched FP peaks
CDict.add('LL_OFFSET', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum fract. wavelength offset '
                       'between cross-matched FP peaks'))

# Maximum DV to keep HC lines in combined (WAVE_NEW) solution
CDict.add('DV_MAX', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum DV to keep HC lines in combined '
                       '(WAVE_NEW) solution'))

# Decide whether to refit the cavity width (will update if files do not
#   exist)
CDict.add('UPDATE_CAVITY', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('Decide whether to refit the cavity '
                       'width (will update if files do not '
                       'exist)'))

# Select the FP cavity fitting (WAVE_MODE_FP = 1 only)
#   Should be one of the following:
#       0 - derive using the 1/m vs d fit from HC lines
#       1 - derive using the ll vs d fit from HC lines
# noinspection SqlDialectInspection
CDict.add('CAVFIT_MODE', value=None, dtype=int,
          source=__NAME__, options=[0, 1], group=cgroup,
          description=('Select the FP cavity fitting '
                       '(WAVE_MODE_FP = 1 only) Should be '
                       'one of the following: 0 - derive '
                       'using the 1/m vs d fit from HC '
                       'lines 1 - derive using the ll vs '
                       'd fit from HC lines'))

# Select the FP wavelength fitting (WAVE_MODE_FP = 1 only)
#   Should be one of the following:
#       0 - use fit_1d_solution function
#       1 - fit with sigma-clipping and mod 1 pixel correction
CDict.add('LLFIT_MODE', value=None, dtype=int,
          source=__NAME__, options=[0, 1], group=cgroup,
          description=('Select the FP wavelength fitting '
                       '(WAVE_MODE_FP = 1 only) Should be '
                       'one of the following: '
                       '\n\t0 - use fit_1d_solution function '
                       '\n\t1 - fit with sigma-clipping and '
                       'mod 1 pixel correction'))

# Minimum FP peaks wavelength separation fraction diff. from median
CDict.add('LLDIF_MIN', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Minimum FP peaks wavelength separation '
                       'fraction diff. from median'))

# Maximum FP peaks wavelength separation fraction diff. from median
CDict.add('LLDIF_MAX', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Maximum FP peaks wavelength separation '
                       'fraction diff. from median'))

# Sigma-clip value for sigclip_polyfit
CDict.add('SIGCLIP', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description='Sigma-clip value for sigclip_polyfit')

# First order for multi-order wave fp plot
CDict.add('PLOT_MULTI_INIT', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description=('First order for multi-order wave '
                       'fp plot'))

# Number of orders in multi-order wave fp plot
CDict.add('PLOT_MULTI_NBO', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('Number of orders in multi-order '
                       'wave fp plot'))

# define the dprtype for generating FPLINES (string list)
CDict.add('DPRLIST', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('define the dprtype for generating '
                       'FPLINES (string list)'))

# define the override for reference fiber for generating FPLINES
#    None for no override
CDict.add('FIBER_TYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='define the override for reference '
                      'fiber for generating FPLINES (None for '
                      'no override)')

# =============================================================================
# CALIBRATION: WAVE NIGHT SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.NIGHT'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_NIGHT: '
                                    'CALIBRATION: WAVE NIGHT SETTINGS')

# number of iterations for hc convergence
CDict.add('NIGHT_NITER1', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description=('number of iterations for hc '
                       'convergence'))

# number of iterations for fp convergence
CDict.add('NIGHT_NITER2', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description=('number of iterations for fp '
                       'convergence'))

# starting point for the cavity corrections
CDict.add('DCAVITY', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('starting point for the cavity '
                       'corrections'))

# define the sigma clip value to remove bad hc lines
CDict.add('HC_SIGCLIP', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('define the sigma clip value to '
                       'remove bad hc lines'))

# median absolute deviation cut off
CDict.add('MED_ABSDEV', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('median absolute deviation '
                       'cut off'))

# sigma clipping for the fit
CDict.add('NSIG_FIT_CUT', value=None,
          dtype=float, source=__NAME__, minimum=1,
          group=cgroup,
          description='sigma clipping for the fit')

# wave night plot hist number of bins
CDict.add('PLT_NBINS', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('wave night plot hist number of '
                       'bins'))

# wave night plot hc bin lower bound in multiples of rms
CDict.add('PLT_BINL', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description=('wave night plot hc bin lower bound '
                       'in multiples of rms'))

# wave night plot hc bin upper bound in multiples of rms
CDict.add('PLT_BINU', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description=('wave night plot hc bin upper bound in '
                       'multiples of rms'))


# =============================================================================
# OBJ.LIST: OBJECT LIST SETTINGS
# =============================================================================
cgroup = 'OBJ.LIST'
CDict.add_group(cgroup, description='CALIBRATION.WAVE_NIGHT: '
                                    'CALIBRATION: WAVE NIGHT SETTINGS')

# Define the SIMBAD TAP url
CDict.add('SIMBAD_TAPURL', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the SIMBAD TAP url')

# Define the TAP Gaia URL (for use in crossmatching to Gaia via astroquery)
CDict.add('GAIA_URL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the TAP Gaia URL (for use in '
                       'crossmatching to Gaia via astroquery)'))

# Define the google sheet to use for crossmatch (may be set to a directory for
#   completely offline reduction)
CDict.add('GSHEET_URL', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description=('Define the google sheet to use '
                       'for crossmatch'))

# Define the google sheet objname list main list id number (may be set to a
#     csv file for completely offline reduction)
CDict.add('GSHEET_MAINLIST_ID', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description='Define the google sheet objname '
                      'list main list id number')

# Define the google sheet objname list pending list id number (may be set to a
# #     csv file for completely offline reduction)
CDict.add('GSHEET_PENDLIST_ID', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description='Define the google sheet '
                      'objname list pending list '
                      'id number')

# Define the google sheet objname list reject list id number
CDict.add('GSHEET_REJECTLIST_ID',
          value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the google sheet '
                      'objname list reject list '
                      'id number')

# Define the bad list header key
CDict.add('REJECT_DRS_HKEY', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the bad list header key')

# Define the bad list google spreadsheet value column
CDict.add('REJECT_VALCOL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the bad list google '
                      'spreadsheet value column')

# Define the bad list google spreadsheet mask column for preprocessing
CDict.add('REJECT_MASKCOL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the bad list google '
                      'spreadsheet mask column for '
                      'preprocessing')


# Define the google sheet bibcode id number
CDict.add('GSHEET_BIBCODE_UD',
          value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the google sheet '
                      'bibcode id number')

# Define the google sheet user url object list (None for no user list)
#     (may be set to a directory for completely offline reduction)
CDict.add('GSHEET_USER_URL', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description='Define the google sheet user url '
                      'object list (None for no user '
                      'list)')

# Define the google sheet user id object list id number (may be set to a
#      csv file for completely offline reduction)
CDict.add('GSHEET_USER_ID', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description='Define the google sheet user id '
                      'object list id number')

# Define whether to resolve from local database (via drs_database / drs_db)
CDict.add('RESOLVE_FROM_DB',
          value=None, dtype=bool, source=__NAME__,
          group=cgroup,
          description=('Define whether to resolve '
                       'from local database '
                       '(via drs_database / '
                       'drs_db)'))

# Define whether to resolve from gaia id (via TapPlus to Gaia) if False
#    ra/dec/pmra/pmde/plx will always come from header
CDict.add('RESOLVE_FROM_GAIAID',
          value=None, dtype=bool, source=__NAME__,
          group=cgroup,
          description=('Define whether to resolve '
                       'from gaia id (via TapPlus '
                       'to Gaia) if False ra/dec/'
                       'pmra/pmde/plx will always '
                       'come from header'))

# Define whether to get Gaia ID / Teff / RV from google sheets if False
#    will try to resolve if gaia ID given otherwise will use ra/dec if
#    OBJ_LIST_RESOLVE_FROM_COORDS = True else will default to header values
CDict.add('RESOLVE_FROM_GLIST',
          value=None, dtype=bool, source=__NAME__,
          group=cgroup,
          description=('Define whether to get Gaia '
                       'ID / Teff / RV from google '
                       'sheets if False will try to '
                       'resolve if gaia ID given '
                       'otherwise will use ra/dec if '
                       'OBJ_LIST_RESOLVE_FROM_COORDS '
                       '= True else will default to '
                       'header values'))

# Define whether to get Gaia ID from header RA and Dec (basically if all other
#    option fails) - WARNING - this is a crossmatch so may lead to a bad
#    identification of the gaia id - not recommended
CDict.add('RESOLVE_FROM_COORDS',
          value=None, dtype=bool, source=__NAME__,
          group=cgroup,
          description=('Define whether to get '
                       'Gaia ID from header RA '
                       'and Dec (basically if all '
                       'other option fails) - '
                       'WARNING - this is a '
                       'crossmatch so may lead to a '
                       'bad identification of the '
                       'gaia id - not recommended'))

# Define the gaia epoch to use in the gaia query
CDict.add('GAIA_EPOCH', value=None, dtype=float,
          source=__NAME__, minimum=2000.0, maximum=2100.0,
          group=cgroup,
          description=('Define the gaia epoch to use in '
                       'the gaia query'))

# Define the radius for crossmatching objects (in both lookup table and query)
#   in arcseconds
CDict.add('CM_RADIUS', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Define the radius for '
                       'crossmatching objects (in '
                       'both lookup table and '
                       'query) in arcseconds'))

# Define the gaia parallax limit for using gaia point
CDict.add('GAIA_PLX_LIM', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the gaia parallax limit '
                       'for using gaia point'))

# Define the gaia magnitude cut to use in the gaia query
CDict.add('GAIA_MAGCUT', value=None, dtype=float,
          source=__NAME__, minimum=10.0, maximum=25.0,
          group=cgroup,
          description=('Define the gaia magnitude cut to '
                       'use in the gaia query'))

# Define the google sheet to use for update the reject list
CDict.add('RLIST_GSHEET_URL', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description=('Define the google sheet to use '
                       'for crossmatch'))

# Define the google sheet id to use for update the reject list
CDict.add('RLIST_GSHEET_MAINLIST_ID', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description='Define the google sheet '
                      'objname list main list id '
                      'number')

# Define the google sheet name to use for the reject list
CDict.add('RLIST_GSHEET_SHEETNAME',
          value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description='Define the google sheet name'
                      ' to use for the reject list')

# gaia col name in google sheet
CDict.add('GAIA_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='gaia col name in google sheet')
# object col name in google sheet
CDict.add('OBJ_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='object col name in google sheet')
# alias col name in google sheet
CDict.add('ALIAS_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='alias col name in google sheet')
# rv col name in google sheet
CDict.add('RV_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='rv col name in google sheet')
CDict.add('RVREF_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup, description='')
# teff col name in google sheet
CDict.add('TEFF_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='teff col name in google sheet')
CDict.add('TEFFREFF_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='teff source reference col name in google sheet')
# Reject like google columns
CDict.add('REJECT_IDENT_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Reject "idenfier" col name in  google sheet')
CDict.add('REJECT_PP_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Reject "pp" col name in google sheet')
CDict.add('REJECT_RV_COLNAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Reject "rv" col name in google sheet')

# =============================================================================
# OBJECT: SKY CORR SETTINGS
# =============================================================================
cgroup = 'OBJ.SKY_CORR'
CDict.add_group(cgroup, description='OBJECT.SKY_CORR: '
                                    'OBJECT: SKY CORR SETTINGS')

# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input sky files
CDict.add('SKYMODEL_FILETYPE', value=None, dtype=str,
          source=__NAME__,
          description='the OUTPUT type (KW_OUTPUT header key) '
                      'and DrsFitsFile name required for '
                      'input sky files')

# Define the order to get the snr from (for input data qc check)
CDict.add('MODEL_EXT_SNR_ORDER', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description='Define the order to get the '
                      'snr from (for input data qc '
                      'check)')

# Define the minimum exptime to use a sky in the model [s]
CDict.add('MODEL_MIN_EXPTIME', value=None,
          dtype=float, source=__NAME__, minimum=0,
          group=cgroup,
          description='Define the minimum exptime to use a '
                      'sky in the model [s]')

# Define the maximum number of files to have open simultaneously
CDict.add('MODEL_MAX_OPEN_FILES', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description='Define the maximum number of '
                      'files to have open simultaneously')

# define the sigma that positive exursions need to have to be identified
#   as lines
CDict.add('MODEL_LINE_SIG', value=None,
          dtype=float, source=__NAME__, minimum=0,
          group=cgroup,
          description='define the sigma that positive '
                      'exursions need to have to be '
                      'identified as lines')

# define the erosion size to use on a line
CDict.add('MODEL_LINE_ERODE_SIZE', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description='define the erosion size to use '
                      'on a line')

# define the dilatation size to use on a line
CDict.add('MODEL_LINE_DILATE_SIZE', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description='define the dilatation size to '
                      'use on a line')

# define the number of weight iterations to use when construct sky model
#       weight vector
CDict.add('MODEL_WEIGHT_ITERS', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description='define the number of weight '
                      'iterations to use when construct '
                      'sky model weight vector')

# define the erosion size for the sky model line weight calculation
CDict.add('MODEL_WEIGHT_ERODE_SIZE', value=None,
          dtype=int, source=__NAME__, minimum=0,
          group=cgroup,
          description='define the erosion size for '
                      'the sky model line weight '
                      'calculation')

# Define the allowed DPRTYPEs for sky correction
CDict.add('ALLOWED_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define the allowed DPRTYPEs for'
                      ' sky correction')

# Define the number of iterations used to create sky correction weights
CDict.add('WEIGHT_ITERS', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description='Define the number of iterations '
                      'used to create sky correction '
                      'weights')

# Define the size of the fine low pass filter (must be an odd integer)
CDict.add('LOWPASS_SIZE1', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description='Define the size of the fine low '
                      'pass filter (must be an odd '
                      'integer)')

# Define the size of the coarse low pass filter (msut be an odd integer)
CDict.add('LOWPASS_SIZE2', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description='Define the size of the coarse low '
                      'pass filter (msut be an odd '
                      'integer)')

# Define the number of iterations to use for the coarse low pass filter
CDict.add('LOWPASS_ITRS', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description='Define the number of iterations'
                      ' to use for the coarse low '
                      'pass filter')

# Define the number of sigma threshold for sky corr sigma clipping
CDict.add('NSIG_THRES', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='Define the number of sigma threshold '
                      'for sky corr sigma clipping')

# Define the flux ratio of sky lines that can not be corrected for
CDict.add('RATIO_THRES', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define the flux ratio of sky lines '
                      'that can not be corrected for')

# =============================================================================
# OBJECT: TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJ.TELL.GEN'
CDict.add_group(cgroup, description='OBJECT.TELLURIC: '
                                    'OBJECT: TELLURIC SETTINGS')

# Define the name of the tapas file to use
CDict.add('TAPAS_FILE', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the name of the tapas file to use')

# Define the format (astropy format) of the tapas file "TAPAS_FILE"
CDict.add('TAPAS_FILE_FMT', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description=('Define the format (astropy format) of the '
                       'tapas file "TAPAS_FILE"'))

# The allowed input DPRTYPES for input telluric files
CDict.add('ALLOWED_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('The allowed input DPRTYPES for '
                       'input telluric files'))

# the INPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
# input telluric files
CDict.add('FILETYPE', value=None, dtype=str, source=__NAME__, group=cgroup,
          description='the INPUT type (KW_OUTPUT header key) and '
                      'DrsFitsFile name required for input telluric files')

# the fiber required for input template files
CDict.add('FIBER_TYPE', value=None, dtype=str, source=__NAME__, group=cgroup,
          description='the fiber required for input template files')

# Define level above which the blaze is high enough to accurately
#    measure telluric
CDict.add('CUT_BLAZE_NORM', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define level above which the blaze '
                       'is high enough to accurately '
                       'measure telluric'))

# Define telluric include/exclude list directory
CDict.add('LIST_DIR', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define telluric include/exclude list '
                       'directory'))

# Define telluric white list name
CDict.add('ALLOWLIST_NAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define telluric white list name')

# Define telluric black list name
CDict.add('REJECTLIST_NAME', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define telluric black list name')

# Force only pre-cleaning (not recommended - only for debugging)
CDict.add('ONLY_PRECLEAN', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description='Force only pre-cleaning (not '
                      'recommended - only for debugging)')

# Whether to fit line of sight velocity in telluric pre-cleaning
CDict.add('ABSO_FIT_LOSVEL', value=False,
          dtype=bool, source=__NAME__, group=cgroup,
          description='whether to fit line of sight '
                      'velocity in telluric '
                      'pre-cleaning')

# Define bad wavelength regions to mask before correcting tellurics
CDict.add('BAD_WAVE_REGIONS', value=[],
          dtype=list, dtypei=list,
          source=__NAME__, group=cgroup,
          description='Define bad wavelength regions to '
                      'mask before correcting tellurics')

# Define regions where fluorescence of oxygen lines that biases the
# telluric absorption calculation (when observation are taken early in the
# night)
CDict.add('FLUORESCENCE', value=[],
          dtype=list, dtypei=list, source=__NAME__, group=cgroup,
          description='Define regions where fluorescence of oxygen '
                      'lines that biases the telluric absorption '
                      'calculation (when observation are taken early '
                      'in the night)')

# =============================================================================
# OBJECT: TELLURIC PRE-CLEANING SETTINGS
# =============================================================================
cgroup = 'OBJ.TELL.PCLEAN'
CDict.add_group(cgroup, description='OBJECT.TELLURIC_PRECLEANING: '
                                    'OBJECT: TELLURIC PRE-CLEANING SETTINGS')

# define whether we do pre-cleaning
CDict.add('DO_PRECLEANING', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description='define whether we do pre-cleaning')

# define whether we do finite resolution correct (if we have a template)
CDict.add('DO_FINITE_RES_CORR', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description='define whether we do finite '
                      'resolution correct (if we have '
                      'a template)')

# width in km/s for the ccf scan to determine the abso in pre-cleaning
CDict.add('CCF_SCAN_RANGE', value=None, dtype=float,
          source=__NAME__, group=cgroup, minimum=0.0,
          description=('width in km/s for the ccf scan to '
                       'determine the abso in '
                       'pre-cleaning'))

# define whether to clean OH lines
CDict.add('CLEAN_OHLINES', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description='define whether to clean OH lines')

# Define the number of bright OH lines that will be individually adjusted
#     in amplitude. Done only on lines that are at an SNR > 1
CDict.add('OHLINE_N_BRIGHT', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='Define the number of bright OH '
                      'lines that will be individually '
                      'adjusted in amplitude. Done only on '
                      'lines that are at an SNR > 1')

# define the OH line pca file
CDict.add('OHLINE_PCA_FILE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='define the OH line pca file')

# define the orders not to use in pre-cleaning fit (due to thermal
# background)
CDict.add('REMOVE_ORDERS', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('define the orders not to use in '
                       'pre-cleaning fit (due to thermal '
                       'background)'))

# define the minimum snr to accept orders for pre-cleaning fit
CDict.add('SNR_MIN_THRES', value=None, dtype=float,
          source=__NAME__, group=cgroup, minimum=0.0,
          description=('define the minimum snr to accept '
                       'orders for pre-cleaning fit'))

# define dexpo convergence threshold
CDict.add('DEXPO_CONV_THRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0.0,
          description=('define dexpo convergence '
                       'threshold'))

# define the maximum number of iterations to try to get dexpo
# convergence
CDict.add('DEXPO_MAX_ITR', value=None, dtype=int,
          source=__NAME__, group=cgroup, minimum=1,
          description=('define the maximum number of '
                       'iterations to try to get dexpo '
                       'convergence'))

# define the kernel threshold in abso_expo
CDict.add('ABSO_EXPO_KTHRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0.0,
          description=('define the kernel threshold in '
                       'abso_expo'))

# define the gaussian width of the kernel used in abso_expo
CDict.add('ABSO_EXPO_KWID', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0.0,
          description=('define the gaussian width of the '
                       'kernel used in abso_expo'))

# define the gaussian exponent of the kernel used in abso_expo
#   a value of 2 is gaussian, a value >2 is boxy
CDict.add('ABSO_EXP_KEXP', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0.0,
          description=('define the gaussian exponent of '
                       'the kernel used in abso_expo a '
                       'value of 2 is gaussian, a '
                       'value >2 is boxy'))

# define the transmission threshold (in exponential form) for keeping
#   valid transmission
CDict.add('TRANS_THRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('define the transmission threshold '
                       '(in exponential form) for keeping '
                       'valid transmission'))

# define the threshold for discrepant transmission (in sigma)
CDict.add('TRANS_SIGLIM', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0.0,
          description=('define the threshold for discrepant '
                       'transmission (in sigma)'))

# define whether to force airmass fit to header airmass value
CDict.add('FORCE_AIRMASS', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description=('define whether to force airmass '
                       'fit to header airmass value'))

# set the typical water abso exponent. Compare to values in header for
#    high-snr targets later
CDict.add('DWATER_ABSO', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          minimum=0.0,
          description=('set the typical water abso exponent. '
                       'Compare to values in header for '
                       'high-snr targets later'))

# set the lower and upper bounds (String list) for the exponent of
#  the other species of absorbers as a ratio to the airmass
#  i.e. value/airmass compared to bound
CDict.add('OTHER_BOUNDS', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description='set the lower and upper bounds '
                      '(String list) for the exponent of '
                      'the other species of absorbers as a '
                      'ratio to the airmass i.e. '
                      'value/airmass compared to bound')

# set the lower and upper bounds (string list) for the exponent of
#  water absorber as a ratio to the airmass i.e. value/airmass compared to bound
CDict.add('WATER_BOUNDS', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description='set the lower and upper bounds '
                      '(string list) for the exponent of '
                      'water absorber as a ratio to the '
                      'airmass i.e. value/airmass compared '
                      'to bound')

# set the plot order for the finite resolution plot
CDict.add('FINITE_RES_ORDER', value=None, dtype=int,
          minimum=0, source=__NAME__, group=cgroup,
          description='set the plot order for the finite '
                      'resolution plot')

# =============================================================================
# OBJECT: MAKE TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJ.TELL.MAKE'
CDict.add_group(cgroup, description='OBJECT.MAKE_TELLURIC: '
                                    'OBJECT: MAKE TELLURIC SETTINGS')

# value below which the blaze in considered too low to be useful
#     for all blaze profiles, we normalize to the 95th percentile.
#     That's pretty much the peak value, but it is resistent to
#     eventual outliers
CDict.add('BLAZE_PTILE', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('value below which the blaze in '
                       'considered too low to be useful '
                       'for all blaze profiles, we '
                       'normalize to the 95th '
                       'percentile. Thats pretty much '
                       'the peak value, but it is '
                       'resistent to eventual outliers'))
CDict.add('CUT_BLAZE_NORM', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='')

# Define list of absorbers in the tapas fits table
CDict.add('ABSORBERS', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('Define list of absorbers in the tapas '
                       'fits table'))

# define the default convolution width [in pixels]
CDict.add('DEF_CONV_WID', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('define the default convolution'
                       ' width [in pixels]'))

# median-filter the template. we know that stellar features
#    are very broad. this avoids having spurious noise in our
#    templates [pixel]
CDict.add('TEMP_MED_FILT', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('median-filter the template. we '
                       'know that stellar features are '
                       'very broad. this avoids having '
                       'spurious noise in our templates '
                       '[pixel]'))

# Define the orders to plot (not too many)
CDict.add('PLOT_ORDER_NUM', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('Define the orders to plot '
                       '(not too many)'))

# Set an upper limit for the allowed line-of-sight optical depth of water
CDict.add('TAU_WATER_ULIMIT', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Set an upper limit for the '
                       'allowed line-of-sight optical '
                       'depth of water'))

#   Define the order to use for SNR check when accepting tellu files
#      to the telluDB
CDict.add('QC_SNR_ORDER', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Define the order to use for SNR '
                       'check when accepting tellu files '
                       'to the telluDB'))

# Defines the maximum allowed value for the recovered water vapor optical
#    depth
CDict.add('TRANS_MAX_WATERCOL', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Defines the maximum allowed '
                       'value for the recovered water '
                       'vapor optical depth'))

# Defines the minimum allowed value for the recovered water vapor optical
#    depth (should not be able 1)
CDict.add('TRANS_MIN_WATERCOL', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Defines the minimum allowed '
                       'value for the recovered water '
                       'vapor optical depth (should '
                       'not be able 1)'))

# minimum transmission required for use of a given pixel in the TAPAS
#    and SED fitting
CDict.add('THRES_TRANSFIT', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('minimum transmission required '
                       'for use of a given pixel in the '
                       'TAPAS and SED fitting'))

# Defines the bad pixels if the spectrum is larger than this value.
#    These values are likely an OH line or a cosmic ray
CDict.add('TRANS_FIT_UBAD', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Defines the bad pixels if '
                       'the spectrum is larger '
                       'than this value. These '
                       'values are likely an OH line '
                       'or a cosmic ray'))

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
#      accepted to the telluDB
CDict.add('QC_SNR_MIN', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the minimum SNR for order '
                       '"QC_TELLU_SNR_ORDER" that will be '
                       'accepted to the telluDB'))

# Define the allowed difference between recovered and input airmass
CDict.add('QC_AIRMASS_DIFF', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('Define the allowed difference '
                       'between recovered and input '
                       'airmass'))

# define the sigma cut for tellu transmission model
CDict.add('TRANSMODEL_SIG', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('define the sigma cut for tellu '
                       'transmission model'))

# =============================================================================
# OBJECT: FIT TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJ.TELLU.FIT'
CDict.add_group(cgroup, description='OBJECT.FIT_TELLURIC: '
                                    'OBJECT: FIT TELLURIC SETTINGS')

#   Define the order to use for SNR check when accepting tellu files
#      to the telluDB
CDict.add('QC_SNR_ORDER', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('Define the order to use for SNR '
                       'check when accepting tellu files '
                       'to the telluDB'))

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
#      accepted to the telluDB
CDict.add('QC_SNR_MIN', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup,
          description=('Define the minimum SNR for order '
                       '"QC_TELLU_SNR_ORDER" that will be '
                       'accepted to the telluDB'))

# The number of principle components to use in PCA fit
CDict.add('NUM_PCA', value=None,
          dtype=int, source=__NAME__, minimum=1,
          user=True, active=False, group=cgroup,
          description='The number of principle '
                      'components to use in PCA fit')

# The number of transmission files to use in the PCA fit (use this number of
#    trans files closest in expo_H2O and expo_water
CDict.add('NUM_TRANS', value=None, dtype=int,
          source=__NAME__, minimum=1,
          user=True, active=False, group=cgroup,
          description='The number of transmission files to use '
                      'in the PCA fit (use this number of '
                      'trans files closest in expo_H2O and '
                      'expo_water')

# Define whether to add the first derivative and broadening factor to the
#     principal components this allows a variable resolution and velocity
#     offset of the PCs this is performed in the pixel space and NOT the
#     velocity space as this is should be due to an instrument shift
CDict.add('ADD_DERIV_PCA', value=None, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='Define whether to add the first '
                      'derivative and broadening factor to '
                      'the principal components this allows '
                      'a variable resolution and velocity '
                      'offset of the PCs this is performed '
                      'in the pixel space and NOT the '
                      'velocity space as this is should be '
                      'due to an instrument shift')

# Define whether to fit the derivatives instead of the principal components
CDict.add('FIT_DERIV_PCA', value=None, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='Define whether to fit the derivatives '
                      'instead of the principal components')

# The number of pixels required (per order) to be able to interpolate the
#    template on to a berv shifted wavelength grid
CDict.add('FIT_KEEP_NUM', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('The number of pixels required (per '
                       'order) to be able to interpolate the '
                       'template on to a berv shifted '
                       'wavelength grid'))

# The minimium transmission allowed to define good pixels (for reconstructed
#    absorption calculation)
CDict.add('FIT_MIN_TRANS', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('The minimium transmission allowed '
                       'to define good pixels (for '
                       'reconstructed absorption '
                       'calculation)'))

# The minimum wavelength constraint (in nm) to calculate reconstructed
#     absorption
CDict.add('LAMBDA_MIN', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('The minimum wavelength constraint '
                       '(in nm) to calculate reconstructed '
                       'absorption'))

# The maximum wavelength constraint (in nm) to calculate reconstructed
#     absorption
CDict.add('LAMBDA_MAX', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('The maximum wavelength constraint '
                       '(in nm) to calculate reconstructed '
                       'absorption'))

# The gaussian kernel used to smooth the template and residual spectrum [km/s]
CDict.add('KERNEL_VSINI', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('The gaussian kernel used to smooth '
                       'the template and residual spectrum '
                       '[km/s]'))

# The number of iterations to use in the reconstructed absorption calculation
CDict.add('FIT_ITERS', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description=('The number of iterations to use in the '
                       'reconstructed absorption calculation'))

# The minimum log absorption the is allowed in the molecular absorption
#     calculation
CDict.add('FIT_RECON_LIM', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('The minimum log absorption the is '
                       'allowed in the molecular '
                       'absorption calculation'))

# Define the orders to plot (not too many) for recon abso plot
CDict.add('PLOT_ORDER_NUMS', value=None,
          dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description=('Define the orders to plot (not '
                       'too many) for recon abso plot '))

# Define the selected fit telluric order for debug plots (when not in loop)
CDict.add('SPLOT_ORDER', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description=('Define the selected fit telluric '
                       'order for debug plots (when not in '
                       'loop)'))

# =============================================================================
# OBJECT: MAKE TEMPLATE SETTINGS
# =============================================================================
cgroup = 'OBJ.TELLU.TEMPLATE'
CDict.add_group(cgroup, description='OBJECT.MAKE_TEMPLATE: '
                                    'OBJECT: MAKE TEMPLATE SETTINGS')

# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input template files
CDict.add('FILETYPE', value=None, dtype=str,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='the OUTPUT type (KW_OUTPUT header key) '
                      'and DrsFitsFile name required for input '
                      'template files')

# the fiber required for input template files
CDict.add('FIBER_TYPE', value=None, dtype=str,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='the fiber required for input '
                      'template files')

# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input template files
CDict.add('FILETYPE', value=None, dtype=str,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='the OUTPUT type (KW_OUTPUT header '
                      'key) and DrsFitsFile name required '
                      'for input template files')

# the fiber required for input template files
CDict.add('FIBER_TYPE', value=None, dtype=str,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='the fiber required for input '
                      'template files')

# the order to use for signal to noise cut requirement
CDict.add('FILESOURCE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          options=['telludb', 'disk'],
          description=('the order to use for signal to '
                       'noise cut requirement'))

# the order to use for signal to noise cut requirement
CDict.add('SNR_ORDER', value=None, dtype=int,
          source=__NAME__, minimum=0, group=cgroup,
          description=('the order to use for signal to '
                       'noise cut requirement'))

# The number of iterations to filter low frequency noise before medianing
#   the template "big cube" to the final template spectrum
CDict.add('E2DS_ITNUM', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('The number of iterations to filter '
                       'low frequency noise before '
                       'medianing the template "big cube" '
                       'to the final template spectrum'))

# The size (in pixels) to filter low frequency noise before medianing
#   the template "big cube" to the final template spectrum
CDict.add('E2DS_LOWF_SIZE', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description=('The size (in pixels) to filter '
                       'low frequency noise before '
                       'medianing the template "big '
                       'cube" to the final template '
                       'spectrum'))

# The number of iterations to filter low frequency noise before medianing
#   the s1d template "big cube" to the final template spectrum
CDict.add('S1D_ITNUM', value=None, dtype=int,
          source=__NAME__, minimum=1, group=cgroup,
          description=('The number of iterations to filter '
                       'low frequency noise before '
                       'medianing the s1d template "big '
                       'cube" to the final template '
                       'spectrum'))

# The size (in pixels) to filter low frequency noise before medianing
#   the s1d template "big cube" to the final template spectrum
CDict.add('S1D_LOWF_SIZE', value=None,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description=('The size (in pixels) to filter '
                       'low frequency noise before '
                       'medianing the s1d template '
                       '"big cube" to the final '
                       'template spectrum'))

# Define the minimum allowed berv coverage to construct a template
#   in km/s  (default is double the resolution in km/s)
CDict.add('BERVCOR_QCMIN', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Define the minimum allowed berv '
                       'coverage to construct a '
                       'template in km/s (default '
                       'is double the resolution in '
                       'km/s)'))

# Define the core SNR in order to calculate required BERV coverage
CDict.add('BERVCOV_CSNR', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Define the core SNR in order to '
                       'calculate required BERV '
                       'coverage'))

# Define the resolution in km/s for calculating BERV coverage
CDict.add('BERVCOV_RES', value=None,
          dtype=float, source=__NAME__, minimum=0.0,
          group=cgroup,
          description=('Defome the resolution in km/s for '
                       'calculating BERV coverage'))

# Define whether to run template making in debug mode (do not bin the
#   data when medianing)
CDict.add('DEBUG_MODE', value=False,
          dtype=bool, source=__NAME__,
          group=cgroup,
          description='Define whether to run template '
                      'making in debug mode (do not bin '
                      'the data when medianing)')

# Define the max number of files to be allowed into a bin (if not in debug
#   mode)
CDict.add('MAX_OPEN_FILES', value=50,
          dtype=int, source=__NAME__, minimum=1,
          group=cgroup,
          description='Define the max number of files '
                      'to be allowed into a bin '
                      '(if not in debug mode)')

# Define the fwhm of hot star convolution kernel size in km/s so it is half
#     the minimum v sin i of our hot stars
CDict.add('HOTSTAR_KER_VEL', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='Define the fwhm of hot star '
                      'convolution kernel size in '
                      'km/s  so it is half the '
                      'minimum v sin i of our hot '
                      'stars')

# Define the threshold for the Lucy-Richardson deconvolution steps. This is
#    the maximum  value of the 99th percentile of the feed-back term
CDict.add('DECONV_ITR_THRES', value=None,
          dtype=float, source=__NAME__, minimum=0,
          group=cgroup,
          description='Define the threshold for the '
                      'Lucy-Richardson deconvolution '
                      'steps. This is the maximum '
                      'value of the 99th percentile '
                      'of the feed-back term')

# Define the max number of iterations to run if the iteration threshold
#     is not met
CDict.add('DECONV_ITR_MAX', value=None,
          dtype=float, source=__NAME__, minimum=0,
          group=cgroup,
          description='Define the max number of '
                      'iterations to run if the '
                      'iteration threshold is not '
                      'met')

# =============================================================================
# CALIBRATION: CCF SETTINGS
# =============================================================================
cgroup = 'OBJ.CCF'
CDict.add_group(cgroup, description='OBJECT.CCF: '
                                    'OBJECT: CCF SETTINGS')

# Define the ccf mask path
CDict.add('MASK_PATH', value=None, dtype=str, source=__NAME__,
          group=cgroup, description='Define the ccf mask path')

# Define the TEFF mask table for when CCF_DEFAULT_MASK is TEFF
CDict.add('TEFF_MASK_TABLE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='# Define the TEFF mask table for '
                      'when CCF_DEFAULT_MASK is TEFF')

# Define target rv the null value for CCF (only change if changing code)
CDict.add('NO_RV_VAL', value=np.nan, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define target rv the null value for CCF'
                       ' (only change if changing code)'))

# Define target rv header null value
#     (values greater than absolute value are set to zero)
CDict.add('RV_NULL_VAL', value=1000, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define target rv header null value '
                       '(values greater than absolute value '
                       'are set to zero)'))

# Define the default CCF MASK to use (filename or TEFF to decide based on
#    object temperature) - for TEFF setup see CCF_TEFF_MASK_TABLE file
CDict.add('DEFAULT_MASK', value=None, dtype=str,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='Define the default CCF MASK to use '
                      '(filename or TEFF to decide based on '
                      'object temperature) - for TEFF setup '
                      'see CCF_TEFF_MASK_TABLE file')

# Define the default CCF MASK normalisation mode
#   options are:
#     'None'         for no normalization
#     'all'          for normalization across all orders
#     'order'        for normalization for each order
CDict.add('MASK_NORM', value=None,
          dtype=str, options=['None', 'all', 'order'],
          source=__NAME__, group=cgroup)

# Define the wavelength units for the mask
CDict.add('MASK_UNITS', value=None, dtype=str,
          source=__NAME__,
          options=['AA', 'Angstrom', 'nm', 'nanometer', 'um',
                   'micron', 'mm', 'millimeter', 'cm',
                   'centimeter', 'm', 'meter'],
          user=True, active=False, group=cgroup,
          description='Define the wavelength units for the mask')

# Define the CCF mask format (must be an astropy.table format)
CDict.add('MASK_FMT', value=None, dtype=str, source=__NAME__,
          group=cgroup)

#  Define the weight of the CCF mask (if 1 force all weights equal)
CDict.add('MASK_MIN_WEIGHT', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup)

#  Define the width of the template line (if 0 use natural)
CDict.add('MASK_WID', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup)

#  Define the maximum allowed ratio between input CCF STEP and CCF WIDTH
#     i.e. error will be generated if CCF_STEP > (CCF_WIDTH / RATIO)
CDict.add('WID_STEP_RATIO', value=None,
          dtype=float, source=__NAME__, minimum=1.0,
          group=cgroup,
          description=('Define the maximum allowed '
                       'ratio between input CCF STEP '
                       'and CCF WIDTH i.e. error will '
                       'be generated if CCF_STEP > '
                       '(CCF_WIDTH / RATIO)'))

# Define the width of the CCF range [km/s]
CDict.add('DEFAULT_WID', value=None, dtype=float,
          source=__NAME__, minimum=0.0,
          user=True, active=False, group=cgroup,
          description='Define the width of the CCF '
                      'range [km/s]')

# Define the computations steps of the CCF [km/s]
CDict.add('DEFAULT_STEP', value=None, dtype=float,
          source=__NAME__, minimum=0.0,
          user=True, active=False, group=cgroup,
          description='Define the computations steps of'
                      ' the CCF [km/s]')

#   The value of the noise for wave dv rms calculation
#       snr = flux/sqrt(flux + noise^2)
CDict.add('NOISE_SIGDET', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup)

#   The size around a saturated pixel to flag as unusable for wave dv rms
#      calculation
CDict.add('NOISE_BOXSIZE', value=None, dtype=int,
          source=__NAME__, minimum=0.0, group=cgroup)

#   The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
CDict.add('NOISE_THRES', value=None, dtype=float,
          source=__NAME__, minimum=0.0, group=cgroup)

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#      to calculate the CCF and RV
CDict.add('N_ORD_MAX', value=None, dtype=int, source=__NAME__,
          minimum=1, group=cgroup)

# Allowed input DPRTYPES for input for CCF recipe
CDict.add('ALLOWED_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='Allowed input DPRTYPES for input '
                      'for CCF recipe')

# Valid DPRTYPES for FP in calibration fiber
CDict.add('VALID_FP_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='Valid DPRTYPES for FP in calibration '
                      'fiber')

# Define the KW_OUTPUT types that are valid telluric corrected spectra
CDict.add('CORRECT_TELLU_TYPES', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description=('Define the KW_OUTPUT types that '
                       'are valid telluric corrected '
                       'spectra'))

# The transmission threshold for removing telluric domain (if and only if
#     we have a telluric corrected input file
CDict.add('TELLU_THRES', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('The transmission threshold for removing '
                       'telluric domain (if and only if we have'
                       ' a telluric corrected input file'))

# The half size (in pixels) of the smoothing box used to calculate what value
#    should replace the NaNs in the E2ds before CCF is calculated
CDict.add('FILL_NAN_KERN_SIZE', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('The half size (in pixels) of the '
                       'smoothing box used to calculate '
                       'what value should replace the '
                       'NaNs in the E2ds before CCF is '
                       'calculated'))

# the step size (in pixels) of the smoothing box used to calculate what value
#   should replace the NaNs in the E2ds before CCF is calculated
CDict.add('FILL_NAN_KERN_RES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description=('the step size (in pixels) of the '
                       'smoothing box used to calculate '
                       'what value should replace the '
                       'NaNs in the E2ds before CCF is '
                       'calculated'))

#  Define the detector noise to use in the ccf
CDict.add('DET_NOISE', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description=('Define the detector noise to use in '
                       'the ccf'))

# Define the fit type for the CCF fit
#     if 0 then we have an absorption line
#     if 1 then we have an emission line
CDict.add('FIT_TYPE', value=None, dtype=int, source=__NAME__,
          options=[0, 1], group=cgroup,
          description=('Define the fit type for the CCF fit if 0 '
                       'then we have an absorption line if 1 then '
                       'we have an emission line'))

# Define the percentile the blaze is normalised by before using in CCF calc
CDict.add('BLAZE_NORM_PTILE', value=None,
          dtype=float, source=__NAME__, minimum=0,
          maximum=100, group=cgroup,
          description=('Define the percentile the '
                       'blaze is normalised by before '
                       'using in CCF calc'))

# Define the minimum number of sigma the peak CCF must have to be acceptable
CDict.add('NSIG_THRES', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description='Define the minimum number of sigma the '
                      'peak CCF must have to be acceptable')

# Define the minimum number of sigma the FWHM of CCF must have to be acceptable
CDict.add('FWHM_SIGCUT', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description='Define the minimum number of sigma the '
                      'FWHM of CCF must have to be acceptable')

# Define the top cut of the bisector cut (percent)
CDict.add('BIS_CUT_TOP', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description='Define the top cut of the bisector cut '
                      '(percent)')

# Define the bottom cut of the bisector cut (percent)
CDict.add('BIS_CUT_BOTTOM', value=None, dtype=float,
          source=__NAME__, minimum=0, group=cgroup,
          description='Define the bottom cut of the bisector'
                      ' cut (percent)')

# =============================================================================
# GENERAL POLARISATION SETTINGS
# =============================================================================
cgroup = 'OBJ.POL.GEN'
CDict.add_group(cgroup, description='OBJECT.POLARISATION: '
                                    'OBJECT: POLARISATION SETTINGS')

# Define all possible fibers used for polarimetry
CDict.add('FIBERS', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define all possible fibers used for '
                      'polarimetry')

# Define all possible stokes parameters
CDict.add('STOKES_PARAMS', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description='Define all possible stokes parameters')

# Whether or not to correct for BERV shift before calculate polarimetry
CDict.add('BERV_CORRECT', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description='Whether or not to correct for BERV '
                      'shift before calculate polarimetry')

# Whether or not to correct for SOURCE RV shift before calculate polarimetry
CDict.add('SOURCE_RV_CORRECT', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description='Whether or not to correct for '
                      'SOURCE RV shift before calculate '
                      'polarimetry')

#  Define the polarimetry method
#    currently must be either:
#         - Ratio
#         - Difference
CDict.add('METHOD', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the polarimetry method currently '
                      'must be either: - Ratio - Difference')

# Whether or not to interpolate flux values to correct for wavelength
#   shifts between exposures
CDict.add('INTERPOLATE_FLUX', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description='Whether or not to interpolate flux '
                      'values to correct for wavelength '
                      'shifts between exposures')

# Select stokes I continuum detection algorithm:
#     'IRAF' or 'MOVING_MEDIAN'
CDict.add('STOKESI_CONT_DET_ALG', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          options=['IRAF', 'MOVING_MEDIAN'],
          description='Select stokes I continuum '
                      'detection algorithm: '
                      'IRAF or MOVING_MEDIAN')

# Select stokes I continuum detection algorithm:
#     'IRAF' or 'MOVING_MEDIAN'
CDict.add('CONT_DEL_ALG', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          options=['IRAF', 'MOVING_MEDIAN'],
          description='Select stokes I continuum '
                      'detection algorithm: '
                      'IRAF or MOVING_MEDIAN')

# Normalize Stokes I (True or False)
CDict.add('NORM_STOKES_I', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description='Normalize Stokes I (True or '
                      'False)')

# Remove continuum polarization
CDict.add('REMOVE_CONT', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description='Remove continuum polarization')

# Apply polarimetric sigma-clip cleanning (Works better if continuum
#     is removed)
CDict.add('CLEAN_BY_SIGCLIP',
          value=None, dtype=bool, source=__NAME__,
          group=cgroup,
          description='Apply polarimetric sigma-'
                      'clip cleanning (Works '
                      'better if continuum is '
                      'removed)')

# Define number of sigmas within which apply clipping
CDict.add('NSIGCLIP', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define number of sigmas within '
                      'which apply clipping')

# Define the reddest wavelength to use throughout polar code
CDict.add('REDDEST_THRES', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='Define the reddest wavelength to '
                      'use throughout polar code')

# Define regions where telluric absorption is high
CDict.add('TELLU_BANDS', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description='Define regions where telluric '
                      'absorption is high')

# Define regions to select lines in the LSD analysis
CDict.add('GET_LSD_LINE_REGIONS', value=None,
          dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description='Define regions to select lines in '
                      'the LSD analysis')

# Define the valid wavelength ranges for each order in SPIrou.
CDict.add('GET_LSD_ORDER_RANGES', value=None,
          dtype=list, dtypei=list,
          source=__NAME__, group=cgroup,
          description='Define the valid wavelength ranges '
                      'for each order in SPIrou.')

# =============================================================================
# POLAR POLY MOVING MEDIAN SETTINGS
# =============================================================================
cgroup = 'OBJ.POL.MMED'
CDict.add_group(cgroup, description='OBJECT.POLAR_POLY_MOVING_MEDIAN: '
                                    'OBJECT: POLAR POLY MOVING MEDIAN SETTINGS')

# Define the polarimetry continuum bin size
CDict.add('CONT_BINSIZE', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='Define the polarimetry continuum bin '
                      'size')
# Define the polarimetry continuum overlap size
CDict.add('CONT_OVERLAP', value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='Define the polarimetry continuum '
                      'overlap size')

# Fit polynomial to continuum polarization?
#    If False it will use a cubic interpolation instead of polynomial fit
CDict.add('CONT_POLYFIT', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description='Fit polynomial to continuum '
                      'polarization? If False it will '
                      'use a cubic interpolation '
                      'instead of polynomial fit')

# Define degree of polynomial to fit continuum polarization
CDict.add('CONT_POLY_DEG', value=None,
          dtype=int, source=__NAME__, group=cgroup,
          description='Define degree of polynomial to '
                      'fit continuum polarization')

# =============================================================================
# POLAR IRAF SETTINGS
# =============================================================================
cgroup = 'OBJ.POL.IRAF'
CDict.add_group(cgroup, description='OBJECT.POLAR_IRAF: '
                                    'OBJECT: POLAR IRAF SETTINGS')

# function to fit to the stokes I continuum: must be 'polynomial' or
#    'spline3'
CDict.add('CONT_FITFUNC_STOKESI', value=None,
          dtype=str, options=['polynomial', 'spline3'],
          source=__NAME__, group=cgroup,
          description='function to fit to the stokes '
                      'I continuum must be polynomial '
                      'or spline3')

# function to fit to the polar continuum: must be 'polynomial' or 'spline3'
CDict.add('CONT_FITFUNC_POLAR', value=None,
          dtype=str, options=['polynomial', 'spline3'],
          source=__NAME__, group=cgroup,
          description='function to fit to the polar '
                      'continuum: must be polynomial '
                      'or spline3')

# stokes i continuum fit function order: 'polynomial': degree or 'spline3':
#    number of knots
CDict.add('CONT_FUNC_ORDER_STOKESI',
          value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='polar continuum fit function '
                      'order, polynomial: degree, '
                      'spline3: number of knots')

# polar continuum fit function order: 'polynomial': degree or 'spline3':
#    number of knots
CDict.add('CONT_FUNC_ORDER_POLAR',
          value=None, dtype=int,
          source=__NAME__, group=cgroup,
          description='stokes i continuum fit function'
                      ' order, polynomial: degree, '
                      'spline3: number of knots')

# =============================================================================
# POLAR LSD SETTINGS
# =============================================================================
cgroup = 'OBJ.POL.LSD'
CDict.add_group(cgroup, description='OBJECT.POLAR_LSD: '
                                    'OBJECT: POLAR LSD SETTINGS')

#  Define the spectral lsd mask directory for lsd polar calculations
CDict.add('LSD_DIR', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the spectral lsd mask directory for '
                      'lsd polar calculations')

#  Define the file regular expression key to lsd mask files
#  for "marcs_t3000g50_all" this should be:
#     - filekey = 'marcs_t*g
#  for "t4000_g4.0_m0.00" it should be:
#     - filekey = 't*_g'
CDict.add('LSD_FILE_KEY',
          value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the file regular expression key '
                      'to lsd mask files for '
                      'marcs_t3000g50_all this should be: '
                      'filekey = marcs_t*g for '
                      't4000_g4.0_m0.00 it should be: filekey '
                      '= t*_g')

# Define minimum lande of lines to be used in the LSD analyis
CDict.add('LSD_MIN_LANDE', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define minimum lande of lines to be '
                      'used in the LSD analyis')

# Define maximum lande of lines to be used in the LSD analyis
CDict.add('LSD_MAX_LANDE', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define maximum lande of lines to be '
                      'used in the LSD analyis')

# If mask lines are in air-wavelength then they will have to be
#     converted from air to vacuum
CDict.add('LSD_CCFLINES_AIRWAVE', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description='If mask lines are in air-'
                      'wavelength then they will '
                      'have to be converted from air '
                      'to vacuum')

# Define minimum line depth to be used in the LSD analyis
CDict.add('LSD_MIN_LINEDEPTH', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='Define minimum line depth to be '
                      'used in the LSD analyis')

# Define maximum line depth to be used in the LSD analyis
CDict.add('LSD_MAX_LINEDEPTH', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='Define maximum line depth to be '
                      'used in the LSD analyis')

# Define initial velocity (km/s) for output LSD profile
CDict.add('V0', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description='Define initial velocity (km/s) for output '
                      'LSD profile')

#  Define final velocity (km/s) for output LSD profile
CDict.add('VF', value=None, dtype=float, source=__NAME__,
          group=cgroup,
          description='Define final velocity (km/s) for output LSD '
                      'profile')

# Define number of points for output LSD profile
CDict.add('NP', value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description='Define number of points for output '
                      'LSD profile')

# Renormalize data before LSD analysis
CDict.add('NORMALIZE', value=None, dtype=bool,
          source=__NAME__, group=cgroup,
          description='Renormalize data before LSD analysis')

# Remove edges of LSD profile
CDict.add('REMOVE_EDGES', value=None,
          dtype=bool, source=__NAME__, group=cgroup,
          description='Remove edges of LSD profile')

# Define the guess at the resolving power for lsd profile fit
CDict.add('RES_POWER_GUESS', value=None,
          dtype=float, source=__NAME__, group=cgroup,
          description='Define the guess at the '
                      'resolving power for lsd profile '
                      'fit')

# =============================================================================
# LBL SETTINGS
# =============================================================================
cgroup = 'OBJ.LBL'
CDict.add_group(cgroup, description='OBJECT.LBL: LBL SETTINGS')

# Whether to reset the whole of LBL before processing
CDict.add('RESET', value=False, dtype=bool, source=__NAME__, user=True,
          active=True, group=cgroup,
          description='Whether to completely reset the whole of LBL before '
                      'processing')

# Define the file definition type (DRSOUTID) for LBL input files
CDict.add('FILE_DEFS', value=None, dtype=str, source=__NAME__,
          user=False, active=True, group=cgroup,
          description='Define the file definition type (DRSOUTID) '
                      'for LBL input files')

# Define the dprtype for science files for LBL
CDict.add('DPRTYPES', value=None, dtype=list, dtypei=str,
          source=__NAME__,
          user=False, active=True, group=cgroup,
          description='Define the dprtype for science files for LBL')

# Define the file definition type (DRSOUTID) for lbl input template
CDict.add('TEMPLATE_FILE_DEFS', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, user=False,
          active=True, group=cgroup,
          description='Define the file definition type '
                      '(DRSOUTID) for lbl input template')

# Define the DPRTYPE for simultaneous FP files for lbl input
CDict.add('SIM_FP_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, user=False, active=True,
          group=cgroup,
          description='Define the DPRTYPE for simultaneous '
                      'FP files for lbl input')

# Define whether the LBL directory should use symlinks
CDict.add('SYMLINKS', value=False, dtype=bool, source=__NAME__,
          user=True, active=True, group=cgroup,
          description='Define whether the LBL directory should use '
                      'symlinks')

# Define the dictionary of friend and friend teffs for LBL
CDict.add('FRIENDS', value=None,
          dtype=dict, dtypei=int,
          source=__NAME__,
          user=False, active=True, group=cgroup,
          description='Define the dictionary of friend and friend '
                      'teffs for LBL')

# Define the specific data types (where objname is the data type) for LBL
CDict.add('SPECIFIC_DTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, user=False,
          active=True, group=cgroup,
          description='Define the specific data types '
                      '(where objname is the data type) '
                      'for LBL')

# Define objnames for which we should recalculate template if it doesn't
#   exist (must include FP)
CDict.add('RECAL_TEMPLATES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, user=False, active=True,
          group=cgroup,
          description='Define objnames for which we should '
                      'recalculate template if it doesn\'t '
                      'exist (must include FP)')

# Define which recipes should skip done files
#   e.g. LBL_COMPUTE,LBL_COMPILE,LBL_MASK
CDict.add('SKIP_DONE', value=None,
          dtype=list, dtypei=str,
          source=__NAME__,
          user=False, active=True, group=cgroup,
          description='Define which recipes should skip done files'
                      'e.g.  LBL_COMPUTE,LBL_COMPILE,LBL_MASK')

# Define which object names should be run through LBL compute in parellel
#   i.e. break in to Ncore chunks
CDict.add('MULTI_OBJLIST', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, user=False, active=True,
          group=cgroup,
          description='Define which object names should be '
                      ' run through LBL compute in parellel '
                      ' i.e. break in to Ncore chunks ')

# Define the DTEMP gradient files
CDict.add('DTEMP', value=None,
          dtype=dict, dtypei=str,
          source=__NAME__, user=False, active=True, group=cgroup,
          description='Define the DTEMP gradient files')

# =============================================================================
# POST PROCESS SETTINGS
# =============================================================================
cgroup = 'OBJ.POST'
CDict.add_group(cgroup, description='OBJECT.POST_PROCESS: POST PROCESS SETTINGS')

# Define whether (by deafult) to clear reduced directory
CDict.add('CLEAR_RED', value=False,
          dtype=bool, source=__NAME__, user=True, active=True,
          group=cgroup,
          description='Define whether (by deafult) to '
                      'clear reduced directory')

# Define whether (by default) to overwrite post processed files
CDict.add('OVERWRITE', value=False,
          dtype=bool, source=__NAME__, user=True, active=True,
          group=cgroup,
          description='Define whether (by default) to '
                      'overwrite post processed files')

# Define the header keyword store to insert extension comment after
CDict.add('HDREXT_COMMKEY', value=None,
          dtype=str, source=__NAME__, user=False,
          active=False, group=cgroup,
          description='Define the header keyword store '
                      'to insert extension comment after')


# =============================================================================
# DEBUG OUTPUT FILE SETTINGS
# =============================================================================
cgroup = 'DEBUG.OUTFILE'
CDict.add_group(cgroup, description='DEBUG.OUTPUT_FILE: '
                                    'DEBUG OUTPUT FILE SETTINGS')

# Whether to save background debug file (large 0.5 GB per file)
#   one of these per extraction (lots)
CDict.add('BCKGRD_FILE', value=True,
          dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='Whether to save background debug '
                      'file (large 0.5 GB per file) one '
                      'of these per extraction (lots)')

# Whether to save the E2DSLL file (around 0.05 to 0.1 GB per file)
#   one of these per fiber (lots)
CDict.add('E2DSLL_FILE', value=True,
          dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='Whether to save the E2DSLL file '
                      '(around 0.05 to 0.1 GB per file) '
                      'one of these per fiber (lots)')

# Whether to save the shape in and out debug files (around 0.1 GB per file)
#   but only one set of these per night
CDict.add('SHAPE_FILES', value=True,
          dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='Whether to save the shape in and '
                      'out debug files (around 0.1 GB per '
                      'file) but only one set of these '
                      'per night')

# Whether to save the uncorrected for FP C fiber leak files
#      (around 0.01 GB per file) one of these per fiber
CDict.add('UNCORR_EXT_FILES', value=True,
          dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='Whether to save the uncorrected '
                      'for FP C fiber leak files (around '
                      '0.01 GB per file) one of these per '
                      'fiber')

# =============================================================================
# DEBUG PLOT SETTINGS
# =============================================================================
cgroup = 'DEBUG.PLOT'
CDict.add_group(cgroup, description='DEBUG.PLOT: DEBUG PLOT SETTINGS')

# turn on dark image region debug plot
CDict.add('DARK_IMAGE_REGIONS', value=False,
          dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on dark image region '
                      'debug plot')

# turn on dark histogram debug plot
CDict.add('DARK_HISTOGRAM', value=False, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on dark histogram debug plot')

# turn on badpix map debug plot
CDict.add('BADPIX_MAP', value=False, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on badpix map debug plot')

# turn on localisation the width regions plot
CDict.add('LOC_WIDTH_REGIONS', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on localisation the width '
                      'regions plot')

# turn on localisation fiber doublet paroty plot
CDict.add('LOC_FIBER_DOUBLET_PARITY',
          value=False, dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on localisation fiber '
                      'doublet paroty plot')

# turn on localisation gap in orders plot
CDict.add('LOC_GAP_ORDERS', value=False, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on localisation gap in orders '
                      'plot')

# turn on localisation image fit plot
CDict.add('LOC_IMAGE_FIT', value=False, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on localisation image fit plot')

# turn on localisation image corners plot
CDict.add('LOG_IM_CORNER', value=False, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on localisation image corners '
                      'plot')

# turn on localisation image regions plot
CDict.add('LOC_IM_REGIONS', value=False, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on localisation image regions '
                      'plot')

# turn on the shape dx debug plot
CDict.add('SHAPE_DX', value=False, dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on the shape dx debug plot')

# turn on the shape angle offset (all orders in loop) debug plot
CDict.add('SHAPE_ANGLE_OFFSET_ALL', value=False,
          dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on the shape angle '
                      'offset (all orders in loop) '
                      'debug plot')

# turn on the shape angle offset (one selected order) debug plot
CDict.add('SHAPE_ANGLE_OFFSET', value=False,
          dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on the shape angle offset '
                      '(one selected order) debug plot')

# turn on the shape local zoom plot
CDict.add('SHAPEL_ZOOM_SHIFT', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the shape local zoom plot')

# turn on the shape linear transform params plot
CDict.add('SHAPE_LINEAR_TPARAMS', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the shape linear '
                      'transform params plot')

# turn on the flat order fit edges debug plot (loop)
CDict.add('FLAT_ORDER_FIT_EDGES1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the flat order fit '
                      'edges debug plot (loop)')

# turn on the flat order fit edges debug plot (selected order)
CDict.add('FLAT_ORDER_FIT_EDGES2', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the flat order fit '
                      'edges debug plot (selected '
                      'order)')

# turn on the flat blaze order debug plot (loop)
CDict.add('FLAT_BLAZE_ORDER1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the flat blaze order '
                      'debug plot (loop)')

# turn on the flat blaze order debug plot (selected order)
CDict.add('FLAT_BLAZE_ORDER2', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the flat blaze order debug '
                      'plot (selected order)')

# turn on the flat edge plot
CDict.add('FLAT_EDGE_ORDERS', value=False, dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on the flat edge plot')

# turn on thermal background (in extract) debug plot
CDict.add('THERMAL_BACKGROUND', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on thermal background '
                      '(in extract) debug plot')

# turn on the extraction spectral order debug plot (loop)
CDict.add('EXTRACT_SPECTRAL_ORDER1',
          value=False, dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on the extraction '
                      'spectral order debug plot '
                      '(loop)')

# turn on the extraction spectral order debug plot (selected order)
CDict.add('EXTRACT_SPECTRAL_ORDER2',
          value=False, dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on the extraction '
                      'spectral order debug plot '
                      '(selected order)')

# turn on the extraction 1d spectrum debug plot
CDict.add('EXTRACT_S1D', value=False, dtype=bool,
          source=__NAME__, user=True, active=False, group=cgroup,
          description='turn on the extraction 1d spectrum'
                      ' debug plot')

# turn on the extraction 1d spectrum weight (before/after) debug plot
CDict.add('EXTRACT_S1D_WEIGHT', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the extraction 1d spectrum'
                      ' weight (before/after) debug plot')

# turn on the wave line fiber comparison plot
CDict.add('WAVE_FIBER_COMPARISON', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave line fiber '
                      'comparison plot')

# turn on the wave line fiber comparison plot
CDict.add('WAVE_FIBER_COMP', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave line fiber comparison plot')

# turn on the wave length vs cavity width plot
CDict.add('WAVE_WL_CAV', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave length vs cavity width plot')

# turn on the wave length vs cavity width plot
CDict.add('WL_CAV_PLOT', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave length vs cavity '
                      'width plot')

# turn on the wave diff HC histograms plot
CDict.add('WAVE_HC_DIFF_HIST', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave diff HC histograms plot')

# turn on the wave slinky e-width plot
CDict.add('WAVE_SLINKY_EW_COV', value=False, dtype=bool,
          source=__NAME__, user=True, active=False, group=cgroup,
          description='turn on the wave slinky e-width plot')

# turn on the wave slinky fit plot
CDict.add('WAVE_SLINKY_FIT', value=False, dtype=bool,
          source=__NAME__, user=True, active=False, group=cgroup,
          description='turn on the wave slinky fit plot')

# TODO: WAVE plots need sorting

# turn on the wave solution hc guess debug plot (in loop)
CDict.add('WAVE_HC_GUESS', value=False,
          dtype=bool, source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on the wave solution hc guess '
                      'debug plot (in loop)')

# turn on the wave solution hc brightest lines debug plot
CDict.add('WAVE_HC_BRIGHTEST_LINES',
          value=False, dtype=bool, source=__NAME__,
          user=True, active=False, group=cgroup,
          description='turn on the wave solution hc '
                      'brightest lines debug plot')

# turn on the wave solution hc triplet fit grid debug plot
CDict.add('WAVE_HC_TFIT_GRID', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution hc '
                      'triplet fit grid debug plot')

# turn on the wave solution hc resolution map debug plot
CDict.add('WAVE_RESMAP', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution hc '
                      'resolution map debug plot')

# turn on the wave solution hc resolution map debug plot
CDict.add('WAVE_HC_RESMAP', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution hc '
                      'resolution map debug plot')

# turn on the wave solution littrow check debug plot
CDict.add('WAVE_LITTROW_CHECK1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution littrow'
                      ' check debug plot')

# turn on the wave solution littrow extrapolation debug plot
CDict.add('WAVE_LITTROW_EXTRAP1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution '
                      'littrow extrapolation '
                      'debug plot')

# turn on the wave solution littrow check debug plot
CDict.add('WAVE_LITTROW_CHECK2', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution '
                      'littrow check debug plot')

# turn on the wave solution littrow extrapolation debug plot
CDict.add('WAVE_LITTROW_EXTRAP2', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution '
                      'littrow extrapolation debug '
                      'plot')

# turn on the wave solution final fp order debug plot
CDict.add('WAVE_FP_FINAL_ORDER', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution final '
                      'fp order debug plot')

# turn on the wave solution fp local width offset debug plot
CDict.add('WAVE_FP_LWID_OFFSET', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution fp '
                      'local width offset debug plot')

# turn on the wave solution fp wave residual debug plot
CDict.add('WAVE_FP_WAVE_RES', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution fp wave '
                      'residual debug plot')

# turn on the wave solution fp fp_m_x residual debug plot
CDict.add('WAVE_FP_M_X_RES', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution fp '
                      'fp_m_x residual debug plot')

# turn on the wave solution fp interp cavity width 1/m_d hc debug plot
CDict.add('WAVE_FP_IPT_CWID_1MHC', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution fp '
                      'interp cavity width 1/m_d hc '
                      'debug plot')

# turn on the wave solution fp interp cavity width ll hc and fp debug plot
CDict.add('WAVE_FP_IPT_CWID_LLHC', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution fp '
                      'interp cavity width ll hc and '
                      'fp debug plot')

# turn on the wave solution old vs new wavelength difference debug plot
CDict.add('WAVE_FP_LL_DIFF', value=False, dtype=bool,
          source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on the wave solution old vs '
                      'new wavelength difference debug plot')

# turn on the wave solution fp multi order debug plot
CDict.add('WAVE_FP_MULTI_ORDER', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution fp '
                      'multi order debug plot')

# turn on the wave solution fp single order debug plot
CDict.add('WAVE_FP_SINGLE_ORDER', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave solution fp '
                      'single order debug plot')

# turn on the wave lines hc/fp expected vs measured debug plot
#  (will plot once for hc once for fp)
CDict.add('WAVEREF_EXPECTED', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave lines hc/fp '
                      'expected vs measured debug plot'
                      '(will plot once for hc once for fp)')

# turn on the wave per night iteration debug plot
CDict.add('WAVENIGHT_ITERPLOT', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave per night '
                      'iteration debug plot')

# turn on the wave per night hist debug plot
CDict.add('WAVENIGHT_HISTPLOT', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the wave per night '
                      'hist debug plot')
# turn on the sky model region plot
CDict.add('TELLU_SKYMODEL_REGION_PLOT',
          value=False, dtype=bool,
          source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the sky model '
                      'region plot')

# turn on the sky model median plot
CDict.add('TELLU_SKYMODEL_MED',
          value=False, dtype=bool,
          source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the sky model '
                      'median plot')

# turn on the sky model median plot
CDict.add('TELLU_SKYMODEL_LINEFIT',
          value=False, dtype=bool,
          source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the sky model '
                      'median plot')

# turn on the sky correction debug plot
CDict.add('TELLU_SKY_CORR_PLOT', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the sky correction '
                      'debug plot')

# turn on the telluric pre-cleaning ccf debug plot
CDict.add('TELLUP_MEAN_RES', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the telluric pre-cleaning '
                      'slope mean res debug plot')

# turn on the telluric pre-cleaning ccf debug plot
CDict.add('TELLUP_WAVE_TRANS', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the telluric pre-cleaning '
                      'ccf debug plot')

# turn on the telluric pre-cleaning result debug plot
CDict.add('TELLUP_ABSO_SPEC', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the telluric pre-cleaning '
                      'result debug plot')

# turn on the telluric OH cleaning debug plot
CDict.add('TELLUP_CLEAN_OH', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the telluric OH cleaning '
                      'debug plot')

# turn on the make tellu wave flux debug plot (in loop)
CDict.add('MKTELLU_WAVE_FLUX1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the make tellu wave flux '
                      'debug plot (in loop)')

# turn on the make tellu wave flux debug plot (single order)
CDict.add('MKTELLU_WAVE_FLUX2', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the make tellu wave flux '
                      'debug plot (single order)')

# turn on the make tellu model plot
CDict.add('MKTELLU_MODEL', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the make tellu model plot')

# turn on the fit tellu pca component debug plot (in loop)
CDict.add('FTELLU_PCA_COMP1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu pca component'
                      ' debug plot (in loop)')

# turn on the fit tellu pca component debug plot (single order)
CDict.add('FTELLU_PCA_COMP2', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu pca component '
                      'debug plot (single order)')

# turn on the fit tellu reconstructed spline debug plot (in loop)
CDict.add('FTELLU_RECON_SPLINE1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu '
                      'reconstructed spline debug '
                      'plot (in loop)')

# turn on the fit tellu reconstructed spline debug plot (single order)
CDict.add('FTELLU_RECON_SPLINE2', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu '
                      'reconstructed spline debug '
                      'plot (single order)')

# turn on the fit tellu wave shift debug plot (in loop)
CDict.add('FTELLU_WAVE_SHIFT1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu wave shift'
                      ' debug plot (in loop)')

# turn on the fit tellu wave shift debug plot (single order)
CDict.add('FTELLU_WAVE_SHIFT1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu wave shift '
                      'debug plot (single order)')

# turn on the fit tellu reconstructed absorption debug plot (in loop)
CDict.add('FTELLU_RECON_ABSO1', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu '
                      'reconstructed absorption debug '
                      'plot (in loop)')

# turn on the fit tellu reconstructed absorption debug plot (single order)
CDict.add('FTELLU_RECON_ABSO2', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu '
                      'reconstructed absorption debug '
                      'plot (single order)')

# turn on the fit tellu res model debug plot
CDict.add('FTELLU_RES_MODEL', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the fit tellu res model '
                      'debug plot')

# turn on the finite resolution correction debug plot
CDict.add('TELLU_FINITE_RES_CORR', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the finite resolution '
                      'correction debug plot')

# turn on the berv coverage debug plot
CDict.add('MKTEMP_BERV_COV', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the berv coverage '
                      'debug plot')

# turn on the template s1d deconvolution plot
CDict.add('MKTEMP_S1D_DECONV', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the template s1d '
                      'deconvolution plot')

# turn on the ccf rv fit debug plot (in a loop around orders)
CDict.add('CCF_RV_FIT_LOOP', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the ccf rv fit debug '
                      'plot (in a loop around orders)')

# turn on the ccf rv fit debug plot (for the mean order value)
CDict.add('CCF_RV_FIT', value=False,
          dtype=bool, source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on the ccf rv fit debug plot '
                      '(for the mean order value)')

# turn on the ccf spectral order vs wavelength debug plot
CDict.add('CCF_SWAVE_REF', value=False,
          dtype=bool, source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on the ccf spectral order vs '
                      'wavelength debug plot')

# turn on the ccf photon uncertainty debug plot
CDict.add('CCF_PHOTON_UNCERT', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the ccf photon uncertainty '
                      'debug plot')

# turn on the polar fit continuum plot
CDict.add('POLAR_FIT_CONT', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the polar fit continuum '
                      'plot')

# turn on the polar continuum debug plot
CDict.add('POLAR_CONTINUUM', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the polar continuum '
                      'debug plot')

# turn on the polar results debug plot
CDict.add('POLAR_RESULTS', value=False,
          dtype=bool, source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on the polar results debug plot')

# turn on the polar stokes i debug plot
CDict.add('POLAR_STOKES_I', value=False,
          dtype=bool, source=__NAME__, user=True,
          active=False, group=cgroup,
          description='turn on the polar stokes i debug plot')

# turn on the polar lsd debug plot
CDict.add('POLAR_LSD', value=False,
          dtype=bool, source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on the polar lsd debug plot')

# turn on the static detector debug plot
CDict.add('STATIC_DET', value=False,
          dtype=bool, source=__NAME__, user=True, active=False,
          group=cgroup,
          description='turn on the static detector debug plot')

# =============================================================================
# TOOLS REPROCESS SETTINGS
# =============================================================================
cgroup = 'TOOLS.REPROCESS'
CDict.add_group(cgroup, description='TOOLS.REPROCESS: REPROCESS SETTINGS')

# Define which block kinds to reindex (warning can take a long time)
#    only select block kinds that have (or could be) manually changed
CDict.add('REINDEX_BLOCKS', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          user=True, active=True,
          description='Define which block kinds to '
                      'reindex (warning can take a '
                      'long time) only select block '
                      'kinds that have (or could be) '
                      'manually changed')

# Define whether to use multiprocess "pool" or "process" or use "linear"
#     mode when parallelising recipes
CDict.add('MP_TYPE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          user=True, active=True,
          options=['pool', 'process'],
          description='Define whether to use multiprocess '
                      '"pool" or "process" or use "linear" '
                      'mode when parallelising recipes')

# Define whether to use multiprocess "pool" or "process" or use "linear"
#     mode when validating recipes
CDict.add('MP_TYPE_VAL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          user=True, active=True,
          options=['linear', 'pool', 'process', 'pathos'],
          description='Define whether to use multiprocess '
                      '"pool" or "process" or use "linear" '
                      'mode when validating recipes')

# Define whether to use multiprocess "pool" or "process" or use "linear"
#     mode when reading raw headers for the file index
CDict.add('MP_FINDEX', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          user=True, active=True,
          options=['linear', 'pool', 'process', 'pathos'],
          description='Define whether to use multiprocess '
                      '"pool" or "process" or use "linear" '
                      'mode when reading raw headers for the file index')

# Define multiprocessing mode for log database update
CDict.add('MP_LOGDB', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          user=True, active=True,
          options=['linear', 'pool', 'process', 'pathos'],
          description='Define whether to use multiprocess '
                      '"pool" or "process" or use "linear" '
                      'mode when updating log database')

# Define multiprocessing mode for calibration/telluric database update
CDict.add('MP_CALIB', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          user=True, active=True,
          options=['linear', 'pool', 'process', 'pathos'],
          description='Define whether to use multiprocess '
                      '"pool" or "process" or use "linear" '
                      'mode when updating log database')

# Key for use in run files
CDict.add('RUN_KEY', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Key for use in run files')

# Define the obs_dir column name for raw file table
CDict.add('OBSDIR_COL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the obs_dir column name '
                       'for raw file table'))

# Define the KW_OBJTYPE allowed for a science target
CDict.add('OBJECT_TYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('Define the KW_OBJTYPE allowed for '
                       'a science target'))

# Define the pi name column name for raw file table
CDict.add('PI_NAME_COL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the pi name column name for '
                       'raw file table'))

# Define the modified file column name for raw file table
CDict.add('MODIFIED_COL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the modified file column '
                       'name for raw file table'))

# Define the sort column (from header keywords) for raw file table
CDict.add('SORTCOL_HDRKEY', value=None,
          dtype=str, source=__NAME__, group=cgroup,
          description=('Define the sort column (from '
                       'header keywords) for raw file '
                       'table'))

# Define the raw index filename
CDict.add('RAW_INDEX_FILE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the raw index filename')

# define the sequence (1 of 5, 2 of 5 etc) col for raw file table
CDict.add('SEQ_COL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('define the sequence (1 of 5, 2 of 5 '
                       'etc) col for raw file table'))

# define the time col for raw file table
CDict.add('TIME_COL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('define the time col for raw file '
                       'table'))

# Define the rejection sql query (between identifier and reject list col)
#    must use a valid reject database column and use {identifier} in query
CDict.add('REJECT_SQL', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the rejection sql query '
                      '(between identifier and reject '
                      'list col) must use a valid reject '
                      'database column and use {identifier} '
                      'in query')

# Define the number of targets to remove (max) per query
CDict.add('REMOVE_NGROUP', value=20, dtype=int,
          source=__NAME__, group=cgroup,
          description='Define the number of targets to remove (max) per query')

# Define the extra SQL science object select critera
CDict.add('OBJ_SCI_SQL', value='', dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the extra SQL science '
                      'object select critera')


# =============================================================================
# TOOLS: GENERAL SETTINGS
# =============================================================================
cgroup = 'TOOLS.GEN'
CDict.add_group(cgroup, description='TOOLS.GENERAL: GENERAL TOOL SETTINGS')

# define the default database to remake
CDict.add('REMAKE_DB_DEFALUT', value='calibration',
          dtype=str, source=__NAME__, group=cgroup,
          description=('define the default database to '
                       'remake'))

# Define whether we try to create a latex summary pdf
#   (turn this off if you have any problems with latex/pdflatex)
CDict.add('SUMMARY_LATEX_PDF', value=True, dtype=bool,
          source=__NAME__, group=cgroup, active=False,
          user=True,
          description='Define whether we try to create a latex '
                      'summary pdf (turn this off if you have '
                      'any problems with latex/pdflatex)')

# Define exposure meter minimum wavelength for mask
CDict.add('EXPMETER_MIN_LAMBDA', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define exposure meter minimum '
                       'wavelength for mask'))

# Define exposure meter maximum wavelength for mask
CDict.add('EXPMETER_MAX_LAMBDA', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define exposure meter maximum '
                       'wavelength for mask'))

# Define exposure meter telluric threshold (minimum tapas transmission)
CDict.add('EXPMETER_TELLU_THRES', value=None, dtype=float,
          source=__NAME__, group=cgroup,
          description=('Define exposure meter telluric '
                       'threshold (minimum tapas '
                       'transmission)'))

# Define the types of file allowed for drift measurement
CDict.add('DRIFT_DPRTYPES', value=None,
          dtype=list, dtypei=str,
          source=__NAME__, group=cgroup,
          description=('Define the types of file allowed for '
                       'drift measurement'))

# Define the fiber dprtype allowed for drift measurement (only FP)
CDict.add('DRIFT_DPR_FIBER_TYPE', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description=('Define the fiber dprtype allowed '
                       'for drift measurement (only FP)'))

# =============================================================================
# ARI SETTINGS
# =============================================================================
cgroup = 'TOOLS.ARI'
CDict.add_group(cgroup, description='TOOLS.ARI: ARI SETTINGS')

# Define the ari instrument (may be different from the apero instrument)
CDict.add('INSTRUMENT', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the ari instrument (may be different'
                      ' from the apero instrument)')
# Define the ari user name
CDict.add('USER', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the ari user name')

# Define the ari number of cores
CDict.add('NCORES', value=None, dtype=int, source=__NAME__,
          group=cgroup,
          description='Define the ari number of cores')

# Define the ari spectrum wavelength ranges in nm
CDict.add('WAVE_RANGES', value=None, dtype=dict,
          source=__NAME__, group=cgroup,
          description='Define the ari spectrum wavelength '
                      'ranges in nm')

# Wavelength range of interest for debug telluric correction map
ARI_TCORR_MAP_WAVE_RANGE = Const('ARI_TCORR_MAP_WAVE_RANGE', value=None,
                                 dtype=list, source=__NAME__, group=cgroup,
                                 description='Wavelength range of interest for '
                                             'debug telluric correction map')

# Define the ari ssh properties to copy the website to
CDict.add('SSH_COPY', value=None, dtype=dict, source=__NAME__,
          group=cgroup,
          description='Define the ari ssh properties to copy the '
                      'website to')

# Define whether to protect the ari pages with a password
CDict.add('PROTECT', value=True, dtype=bool, source=__NAME__,
          group=cgroup,
          description='Whether to protect the ari pages with a password')

# Define the ari group (For login access to pages)
CDict.add('GROUP', value=None, dtype=str, source=__NAME__,
          group=cgroup,
          description='Define the ari group (For login access to '
                      'pages)')

# Define whether to reset the ari working directory
CDict.add('RESET', value=False, dtype=bool, source=__NAME__,
          group=cgroup,
          description='Define whether to reset the ari working '
                      'directory')

# Define whether to filter by objects
CDict.add('FILTER_OBJECTS', value=None, dtype=str,
          source=__NAME__, group=cgroup,
          description='Define whether to filter by objects')

# Define the list of objects to filter in ari
CDict.add('FILTER_OBJECTS_LIST', value=None,
          dtype=list, source=__NAME__, group=cgroup,
          description='Define the list of objects to '
                      'filter in ari')

# Define the header key props for ari
CDict.add('HEADER_PROPS', value=None, dtype=dict,
          source=__NAME__, group=cgroup,
          description='Define the header key props for ari')

# Define the finding charts dictionary for ari
CDict.add('FINDING_CHARTS', value=None, dtype=dict,
          source=__NAME__, group=cgroup,
          description='Define the finding charts dictionary '
                      'for ari')

# Define the ARI orders for calib plot
CDict.add('CAL_ORDERS', value=None, dtype=list, dtypei=int,
          source=__NAME__, group=cgroup,
          description='Define the ARI orders for calib plot')

# Define the ARI reset directory (relative paths to copy into the "other"
#   directory on installation/reset)
ari_reset_dict = dict()
ari_reset_dict['sphinx-setup'] = ('tools/resources/ari/working',
                                  'ari')
ari_reset_dict['ari-setup'] = ('tools/resources/ari/ari-config',
                               'ari-config')
ari_reset_dict['ari-home'] = ('tools/resources/ari/ari-home', 'ari-home')
CDict.add('RESET_DICT', value=ari_reset_dict,
          dtype=dict, source=__NAME__, group=cgroup,
          description='Define the ARI reset directory (relative '
                      'paths to copy into the "other" directory '
                      'on installation/reset)')

# =============================================================================
# STATIC SETTINGS
# =============================================================================
cgroup = 'TOOLS.STATIC'
CDict.add_group(cgroup, description='TOOLS.STATIC: STATIC SETTINGS')

# Define the sub-directory in PATH.ASSETS to put new static calibrations in
CDict.add('DET_PATH', value='engineering', dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the sub-directory in PATH.ASSETS to put new '
                      'static calibrations in')

# Define the sub-directory in PATH.ASSETS to put new static calibrations in
CDict.add('CAL_PATH', value='calib', dtype=str,
          source=__NAME__, group=cgroup,
          description='Define the sub-directory in PATH.ASSETS to put new '
                      'static calibrations in')

# Define the shortest allowed longest exposure time for the DARKs provided
#    [in s]
CDict.add('SHORTEST_LONG_DARK_EXPTIME', value=600, dtype=float,
          source=__NAME__, group=cgroup,
          description='Define the shortest allowed longest exposure time '
                      'for the DARKs provided [in s]')

# =============================================================================
# INFO VISUALIZATION SETTINGS
# =============================================================================
cgroup = 'TOOLS.INFO_VISU'

# zoom 1 value for info visu plots
CDict.add('Z1', value=None, dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description='(Min, Max) zoom 1 value for info visu plots')

# zoom 2 value for info visu plots
CDict.add('Z2', value=None, dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description='(Min, Max) zoom 2 value for info visu plots')

# zoom 3 value for info visu plots
CDict.add('Z3', value=None, dtype=list, dtypei=float,
          source=__NAME__, group=cgroup,
          description='(Min, Max) zoom 3 value for info visu plots')

# Plot order for LBL etc in info plots
CDict.add('EXT_ORDER', value=None, dtype=int, source=__NAME__, group=cgroup,
          description='Plot order for LBL etc in info plots')

# =============================================================================
#  End of configuration file
# =============================================================================