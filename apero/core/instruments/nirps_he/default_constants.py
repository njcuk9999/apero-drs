"""
Default constants for NIRPS HE

Created on 2019-01-17

@author: cook
"""
from apero.base import base
from apero.core.instruments.default.default_constants import *

# Note: If variables are not showing up MUST CHECK __all__ definition
#       in import * module

__NAME__ = 'core.instruments.nirps_he.default_constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__

# =============================================================================
# NIRPS_HA Constant definitions
# =============================================================================

# =============================================================================
# DRS DATA SETTINGS
# =============================================================================
# Define the data engineering path
DATA_ENGINEERING = DATA_ENGINEERING.copy(__NAME__)
DATA_ENGINEERING.value = 'engineering/'

# Define core data path
DATA_CORE = DATA_CORE.copy(__NAME__)
DATA_CORE.value = './data/core/'

# Define whether to force wave solution from calibration database (instead of
#    using header wave solution if available)
CALIB_DB_FORCE_WAVESOL = CALIB_DB_FORCE_WAVESOL.copy(__NAME__)
CALIB_DB_FORCE_WAVESOL.value = False

# =============================================================================
# COMMON IMAGE SETTINGS
# =============================================================================
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
RAW_TO_PP_ROTATION = RAW_TO_PP_ROTATION.copy(__NAME__)
RAW_TO_PP_ROTATION.value = 5

# Define raw image size (mostly just used as a check and in places where we
#   don't have access to this information)
IMAGE_X_FULL = IMAGE_X_FULL.copy(__NAME__)
IMAGE_X_FULL.value = 4096

IMAGE_Y_FULL = IMAGE_Y_FULL.copy(__NAME__)
IMAGE_Y_FULL.value = 4096

# Define the fibers
FIBER_TYPES = FIBER_TYPES.copy(__NAME__)
FIBER_TYPES.value = 'A, B'

# Defines whether to by default combine images that are inputted at the same
#   time
INPUT_COMBINE_IMAGES = INPUT_COMBINE_IMAGES.copy(__NAME__)
INPUT_COMBINE_IMAGES.value = True

# Defines whether to, by default, flip images that are inputted
INPUT_FLIP_IMAGE = INPUT_FLIP_IMAGE.copy(__NAME__)
INPUT_FLIP_IMAGE.value = True

# Defines whether to, by default, resize images that are inputted
INPUT_RESIZE_IMAGE = INPUT_RESIZE_IMAGE.copy(__NAME__)
INPUT_RESIZE_IMAGE.value = True

# Defines the resized image
IMAGE_X_LOW = IMAGE_X_LOW.copy(__NAME__)
IMAGE_X_LOW.value = 4
IMAGE_X_HIGH = IMAGE_X_HIGH.copy(__NAME__)
IMAGE_X_HIGH.value = 4092
IMAGE_Y_LOW = IMAGE_Y_LOW.copy(__NAME__)
IMAGE_Y_LOW.value = 4
IMAGE_Y_HIGH = IMAGE_Y_HIGH.copy(__NAME__)
IMAGE_Y_HIGH.value = 4092

# Define the pixel size in km/s / pix
#    also used for the median sampling size in tellu correction
IMAGE_PIXEL_SIZE = IMAGE_PIXEL_SIZE.copy(__NAME__)
IMAGE_PIXEL_SIZE.value = 1.00

# Define mean line width expressed in pix
FWHM_PIXEL_LSF = FWHM_PIXEL_LSF.copy(__NAME__)
FWHM_PIXEL_LSF.value = 3.0

# Define the point at which the detector saturates
IMAGE_SATURATION = IMAGE_SATURATION.copy(__NAME__)
IMAGE_SATURATION.value = 60000

# Define the frame time for an image
IMAGE_FRAME_TIME = IMAGE_FRAME_TIME.copy(__NAME__)
IMAGE_FRAME_TIME.value = 5.57192

# =============================================================================
# CALIBRATION: GENERAL SETTINGS
# =============================================================================
# Define the maximum number of files that can be used in a group
GROUP_FILE_LIMIT = GROUP_FILE_LIMIT.copy(__NAME__)
GROUP_FILE_LIMIT.value = 20

# Define whether we check the calibration and observation separation
DO_CALIB_DTIME_CHECK = DO_CALIB_DTIME_CHECK.copy(__NAME__)
DO_CALIB_DTIME_CHECK.value = True

# Define the maximum time (in days) that a calibration can be separated from
#   an observation in order to use it
MAX_CALIB_DTIME = MAX_CALIB_DTIME.copy(__NAME__)
MAX_CALIB_DTIME.value = 7.0

# Define the threshold under which a file should not be combined
#  (metric is compared to the median of all files 1 = perfect, 0 = noise)
COMBINE_METRIC_THRESHOLD1 = COMBINE_METRIC_THRESHOLD1.copy(__NAME__)
COMBINE_METRIC_THRESHOLD1.value = 0.99

# Define the DPRTYPES allowed for the combine metric 1 comparison
COMBINE_METRIC1_TYPES = COMBINE_METRIC1_TYPES.copy(__NAME__)
COMBINE_METRIC1_TYPES.value = 'DARK_FLAT, FLAT_FLAT, FLAT_DARK, FP_FP, DARK_FP'

# Define the coefficients of the fit of 1/m vs d
CAVITY_1M_FILE = CAVITY_1M_FILE.copy(__NAME__)
CAVITY_1M_FILE.value = 'cavity_length_m_fit.dat'

# Define the coefficients of the fit of wavelength vs d
CAVITY_LL_FILE = CAVITY_LL_FILE.copy(__NAME__)
CAVITY_LL_FILE.value = 'cavity_length_ll_fit.dat'

# define the check FP percentile level
CALIB_CHECK_FP_PERCENTILE = CALIB_CHECK_FP_PERCENTILE.copy(__NAME__)
CALIB_CHECK_FP_PERCENTILE.value = 95

# define the check FP threshold qc parameter
CALIB_CHECK_FP_THRES = CALIB_CHECK_FP_THRES.copy(__NAME__)
CALIB_CHECK_FP_THRES.value = 100

# define the check FP center image size [px]
CALIB_CHECK_FP_CENT_SIZE = CALIB_CHECK_FP_CENT_SIZE.copy(__NAME__)
CALIB_CHECK_FP_CENT_SIZE.value = 100

# Define the TAP Gaia URL (for use in crossmatching to Gaia via astroquery)
OBJ_LIST_GAIA_URL = OBJ_LIST_GAIA_URL.copy(__NAME__)
OBJ_LIST_GAIA_URL.value = 'https://gea.esac.esa.int/tap-server/tap'

# Define the google sheet to use for crossmatch (may be set to a directory for
#   completely offline reduction)
OBJ_LIST_GOOGLE_SHEET_URL = OBJ_LIST_GOOGLE_SHEET_URL.copy(__NAME__)
OBJ_LIST_GOOGLE_SHEET_URL.value = '1dOogfEwC7wAagjVFdouB1Y1JdF9Eva4uDW6CTZ8x2FM'

# Define the google sheet objname list main list id number (may be set to a
#     csv file for completely offline reduction)
OBJ_LIST_GSHEET_MAIN_LIST_ID = OBJ_LIST_GSHEET_MAIN_LIST_ID.copy(__NAME__)
OBJ_LIST_GSHEET_MAIN_LIST_ID.value = '0'

# Define the google sheet objname list pending list id number (may be set to a
# #     csv file for completely offline reduction)
OBJ_LIST_GSHEET_PEND_LIST_ID = OBJ_LIST_GSHEET_PEND_LIST_ID.copy(__NAME__)
OBJ_LIST_GSHEET_PEND_LIST_ID.value = '623506317'

# Define the google sheet objname list reject list id number
OBJ_LIST_GSHEET_REJECT_LIST_ID = OBJ_LIST_GSHEET_REJECT_LIST_ID.copy(__NAME__)
OBJ_LIST_GSHEET_REJECT_LIST_ID.value = '2006484513'

# Define the google sheet user url object list (None for no user list)
#     (may be set to a directory for completely offline reduction)
OBJ_LIST_GSHEET_USER_URL = OBJ_LIST_GSHEET_USER_URL.copy(__NAME__)
OBJ_LIST_GSHEET_USER_URL.value = 'None'

# Define the google sheet user id object list id number (may be set to a
#      csv file for completely offline reduction)
OBJ_LIST_GSHEET_USER_ID = OBJ_LIST_GSHEET_USER_ID.copy(__NAME__)
OBJ_LIST_GSHEET_USER_ID.value = '0'

# Define whether to resolve from local database (via drs_database / drs_db)
OBJ_LIST_RESOLVE_FROM_DATABASE = OBJ_LIST_RESOLVE_FROM_DATABASE.copy(__NAME__)
OBJ_LIST_RESOLVE_FROM_DATABASE.value = True

# Define whether to resolve from gaia id (via TapPlus to Gaia) if False
#    ra/dec/pmra/pmde/plx will always come from header
OBJ_LIST_RESOLVE_FROM_GAIAID = OBJ_LIST_RESOLVE_FROM_GAIAID.copy(__NAME__)
OBJ_LIST_RESOLVE_FROM_GAIAID.value = True

# Define whether to get Gaia ID / Teff / RV from google sheets if False
#    will try to resolve if gaia ID given otherwise will use ra/dec if
#    OBJ_LIST_RESOLVE_FROM_COORDS = True else will default to header values
OBJ_LIST_RESOLVE_FROM_GLIST = OBJ_LIST_RESOLVE_FROM_GLIST.copy(__NAME__)
OBJ_LIST_RESOLVE_FROM_GLIST.value = True

# Define whether to get Gaia ID from header RA and Dec (basically if all other
#    option fails) - WARNING - this is a crossmatch so may lead to a bad
#    identification of the gaia id - not recommended
OBJ_LIST_RESOLVE_FROM_COORDS = OBJ_LIST_RESOLVE_FROM_COORDS.copy(__NAME__)
OBJ_LIST_RESOLVE_FROM_COORDS.value = False

# Define the gaia epoch to use in the gaia query
OBJ_LIST_GAIA_EPOCH = OBJ_LIST_GAIA_EPOCH.copy(__NAME__)
OBJ_LIST_GAIA_EPOCH.value = 2015.5

# Define the radius for crossmatching objects (in both lookup table and query)
#    measured in arc sec (only used if OBJ_LIST_RESOLVE_FROM_COORDS = True)
OBJ_LIST_CROSS_MATCH_RADIUS = OBJ_LIST_CROSS_MATCH_RADIUS.copy(__NAME__)
OBJ_LIST_CROSS_MATCH_RADIUS.value = 180.0

# Define the gaia parallax limit for using gaia point meansure in mas
#    (only used if OBJ_LIST_RESOLVE_FROM_COORDS = True)
OBJ_LIST_GAIA_PLX_LIM = OBJ_LIST_GAIA_PLX_LIM.copy(__NAME__)
OBJ_LIST_GAIA_PLX_LIM.value = 0.5

# Define the gaia magnitude cut (rp mag) to use in the gaia query
#    (only used if OBJ_LIST_RESOLVE_FROM_COORDS = True)
OBJ_LIST_GAIA_MAG_CUT = OBJ_LIST_GAIA_MAG_CUT.copy(__NAME__)
OBJ_LIST_GAIA_MAG_CUT.value = 15.0

# Define the google sheet to use for update the reject list
REJECT_LIST_GOOGLE_SHEET_URL = REJECT_LIST_GOOGLE_SHEET_URL.copy(__NAME__)
REJECT_LIST_GOOGLE_SHEET_URL.value = '1gvMp1nHmEcKCUpxsTxkx-5m115mLuQIGHhxJCyVoZCM'

# Define the google sheet id to use for update the reject list
REJECT_LIST_GSHEET_MAIN_LIST_ID = REJECT_LIST_GSHEET_MAIN_LIST_ID.copy(__NAME__)
REJECT_LIST_GSHEET_MAIN_LIST_ID.value = '1847598400'

# Define which twilight to use as the definition of a night observation
#    ("CIVIL", "NAUTICAL", "ASTRONOMICAL")
NIGHT_DEFINITION = NIGHT_DEFINITION.copy(__NAME__)
NIGHT_DEFINITION.value = 'NAUTICAL'
NIGHT_DEFINITION.author = base.AUTHORS['EA']

# =============================================================================
# CALIBRATION: FIBER SETTINGS
# =============================================================================
# Note new fiber settings musts also be added to pseudo_const
#   in the "FIBER_SETTINGS" function i.e.
#            keys = ['FIBER_FIRST_ORDER_JUMP', 'FIBER_MAX_NUM_ORDERS',
#                    'FIBER_SET_NUM_FIBERS']

#   Number of orders to skip at start of image
FIBER_FIRST_ORDER_JUMP_A = FIBER_FIRST_ORDER_JUMP_A.copy(__NAME__)
FIBER_FIRST_ORDER_JUMP_B = FIBER_FIRST_ORDER_JUMP_B.copy(__NAME__)
# set values
FIBER_FIRST_ORDER_JUMP_A.value = 0
FIBER_FIRST_ORDER_JUMP_B.value = 0

#   Maximum number of order to use
FIBER_MAX_NUM_ORDERS_A = FIBER_MAX_NUM_ORDERS_A.copy(__NAME__)
FIBER_MAX_NUM_ORDERS_B = FIBER_MAX_NUM_ORDERS_B.copy(__NAME__)
# set values
FIBER_MAX_NUM_ORDERS_A.value = 75
FIBER_MAX_NUM_ORDERS_B.value = 75

#   Number of fibers
FIBER_SET_NUM_FIBERS_A = FIBER_SET_NUM_FIBERS_A.copy(__NAME__)
FIBER_SET_NUM_FIBERS_B = FIBER_SET_NUM_FIBERS_B.copy(__NAME__)
# set values
FIBER_SET_NUM_FIBERS_A.value = 1
FIBER_SET_NUM_FIBERS_B.value = 1

# =============================================================================
# PRE-PROCESSSING SETTINGS
# =============================================================================
# Define object (science or telluric)
PP_OBJ_DPRTYPES = PP_OBJ_DPRTYPES.copy(__NAME__)
PP_OBJ_DPRTYPES.value = 'OBJ_DARK, OBJ_FP, OBJ_SKY, TELLU_SKY, FLUXSTD_SKY'

# Define the bad list google spreadsheet id
PP_BADLIST_SSID = PP_BADLIST_SSID.copy(__NAME__)
PP_BADLIST_SSID.value = '1gvMp1nHmEcKCUpxsTxkx-5m115mLuQIGHhxJCyVoZCM'
PP_BADLIST_SSID.author = base.AUTHORS['NJC']

# Define the bad list google workbook number
PP_BADLIST_SSWB = PP_BADLIST_SSWB.copy(__NAME__)
PP_BADLIST_SSWB.value = 0
PP_BADLIST_SSWB.author = base.AUTHORS['NJC']

# Define the bad list header key
PP_BADLIST_DRS_HKEY = PP_BADLIST_DRS_HKEY.copy(__NAME__)
PP_BADLIST_DRS_HKEY.value = None
PP_BADLIST_DRS_HKEY.author = base.AUTHORS['NJC']

# Define the bad list google spreadsheet value column
PP_BADLIST_SS_VALCOL = PP_BADLIST_SS_VALCOL.copy(__NAME__)
PP_BADLIST_SS_VALCOL.value = 'IDENTIFIER'
PP_BADLIST_SS_VALCOL.author = base.AUTHORS['NJC']

# Define the bad list google spreadsheet mask column for preprocessing
PP_BADLIST_SS_MASKCOL = PP_BADLIST_SS_MASKCOL.copy(__NAME__)
PP_BADLIST_SS_MASKCOL.value = 'PP'
PP_BADLIST_SS_MASKCOL.author = base.AUTHORS['NJC']

# Defines the box size surrounding hot pixels to use
PP_HOTPIX_BOXSIZE = PP_HOTPIX_BOXSIZE.copy(__NAME__)
PP_HOTPIX_BOXSIZE.value = 5

# Defines the size around badpixels that is considered part of the bad pixel
PP_CORRUPT_MED_SIZE = PP_CORRUPT_MED_SIZE.copy(__NAME__)
PP_CORRUPT_MED_SIZE.value = 2

# Define the fraction of the required exposure time that is required for a
#   valid observation
PP_BAD_EXPTIME_FRACTION = PP_BAD_EXPTIME_FRACTION.copy(__NAME__)
PP_BAD_EXPTIME_FRACTION.value = 0.10

# Defines the threshold in sigma that selects hot pixels
PP_CORRUPT_HOT_THRES = PP_CORRUPT_HOT_THRES.copy(__NAME__)
PP_CORRUPT_HOT_THRES.value = 10

#   Define the total number of amplifiers
PP_TOTAL_AMP_NUM = PP_TOTAL_AMP_NUM.copy(__NAME__)
PP_TOTAL_AMP_NUM.value = 32

#   Define the number of dark amplifiers
PP_NUM_DARK_AMP = PP_NUM_DARK_AMP.copy(__NAME__)
PP_NUM_DARK_AMP.value = 5

#   Define the number of bins used in the dark median process
PP_DARK_MED_BINNUM = PP_DARK_MED_BINNUM.copy(__NAME__)
PP_DARK_MED_BINNUM.value = 32

#   Defines the pp hot pixel file (located in the data folder)
PP_HOTPIX_FILE = PP_HOTPIX_FILE.copy(__NAME__)
PP_HOTPIX_FILE.value = 'hotpix_pp.csv'

#   Defines the pp amplifier bias model (located in the data folder)
PP_AMP_ERROR_MODEL = PP_AMP_ERROR_MODEL.copy(__NAME__)
PP_AMP_ERROR_MODEL.value = 'amplifier_bias_model_nirps.fits'

# Defines the pp led flat file (located in the data folder)
PP_LED_FLAT_FILE = PP_LED_FLAT_FILE.copy(__NAME__)
PP_LED_FLAT_FILE.value = 'led_flat_he.fits'

#   Define the number of un-illuminated reference pixels at top of image
PP_NUM_REF_TOP = PP_NUM_REF_TOP.copy(__NAME__)
PP_NUM_REF_TOP.value = 4

#   Define the number of un-illuminated reference pixels at bottom of image
PP_NUM_REF_BOTTOM = PP_NUM_REF_BOTTOM.copy(__NAME__)
PP_NUM_REF_BOTTOM.value = 4

#   Define the number of un-illuminated reference pixels at left of image
PP_NUM_REF_LEFT = PP_NUM_REF_LEFT.copy(__NAME__)
PP_NUM_REF_LEFT.value = 4

#   Define the number of un-illuminated reference pixels at right of image
PP_NUM_REF_RIGHT = PP_NUM_REF_RIGHT.copy(__NAME__)
PP_NUM_REF_RIGHT.value = 4

# Define the percentile value for the rms normalisation (0-100)
PP_RMS_PERCENTILE = PP_RMS_PERCENTILE.copy(__NAME__)
PP_RMS_PERCENTILE.value = 95

# Define the lowest rms value of the rms percentile allowed if the value of
#     the pp_rms_percentile-th is lower than this this value is used
PP_LOWEST_RMS_PERCENTILE = PP_LOWEST_RMS_PERCENTILE.copy(__NAME__)
PP_LOWEST_RMS_PERCENTILE.value = 10

# Defines the snr hotpix threshold to define a corrupt file
PP_CORRUPT_SNR_HOTPIX = PP_CORRUPT_SNR_HOTPIX.copy(__NAME__)
PP_CORRUPT_SNR_HOTPIX.value = 10

# Defines the RMS threshold to also catch corrupt files
PP_CORRUPT_RMS_THRES = PP_CORRUPT_RMS_THRES.copy(__NAME__)
PP_CORRUPT_RMS_THRES.value = 0.3  # was 0.15

# super-pessimistic noise estimate. Includes uncorrected common noise
PP_COSMIC_NOISE_ESTIMATE = PP_COSMIC_NOISE_ESTIMATE.copy(__NAME__)
PP_COSMIC_NOISE_ESTIMATE.value = 30.0

# define the cuts in sigma where we should look for cosmics (variance)
PP_COSMIC_VARCUT1 = PP_COSMIC_VARCUT1.copy(__NAME__)
PP_COSMIC_VARCUT1.value = 100.0
PP_COSMIC_VARCUT2 = PP_COSMIC_VARCUT2.copy(__NAME__)
PP_COSMIC_VARCUT2.value = 50.0

# define the cuts in sigma where we should look for cosmics (intercept)
PP_COSMIC_INTCUT1 = PP_COSMIC_INTCUT1.copy(__NAME__)
PP_COSMIC_INTCUT1.value = 100.0    # 50.0
PP_COSMIC_INTCUT2 = PP_COSMIC_INTCUT2.copy(__NAME__)
PP_COSMIC_INTCUT2.value = 50.0    # 10.0

# random box size [in pixels] to speed-up low-frequency band computation
PP_COSMIC_BOXSIZE = PP_COSMIC_BOXSIZE.copy(__NAME__)
PP_COSMIC_BOXSIZE.value = 64

# Define whether to skip preprocessed files that have already be processed
SKIP_DONE_PP = SKIP_DONE_PP.copy(__NAME__)
SKIP_DONE_PP.value = False

# Define dark dprtypes for threshold quality control check (PP_DARK_THRES)
PP_DARK_DPRTYPES = PP_DARK_DPRTYPES.copy(__NAME__)
PP_DARK_DPRTYPES.value = 'DARK_DARK'

# Define the threshold for a suitable DARK_DARK (above this will not be
#    processed)
PP_DARK_THRES = PP_DARK_THRES.copy(__NAME__)
PP_DARK_THRES.value = 0.5

# Define allowed preprocessing reference file types (PP DPRTYPE)
ALLOWED_PPM_TYPES = ALLOWED_PPM_TYPES.copy(__NAME__)
ALLOWED_PPM_TYPES.value = 'FLAT_FLAT'

# Define the allowed number of sigma for preprocessing reference mask
PPM_MASK_NSIG = PPM_MASK_NSIG.copy(__NAME__)
PPM_MASK_NSIG.value = 10

# Define the bin to use to correct low level frequences. This value cannot
#   be smaller than the order footprint on the array as it would lead to a set
#   of NaNs in the downsized image
PP_MEDAMP_BINSIZE = PP_MEDAMP_BINSIZE.copy(__NAME__)
PP_MEDAMP_BINSIZE.value = 32

# Define the amplitude of the flux-dependent along-readout-axis derivative
#     component
# TODO: Add calculation to static apero-utils.general.apero_statics.corr_xtalk.py
PP_CORR_XTALK_AMP_FLUX = PP_CORR_XTALK_AMP_FLUX.copy(__NAME__)
PP_CORR_XTALK_AMP_FLUX.value = 1.359371e-04
PP_CORR_XTALK_AMP_FLUX.author = base.AUTHORS['EA']

# Define amplitude of the flux-dependent along-readout-axis 1st derivative
#     component
# TODO: Add calculation to static apero-utils.general.apero_statics.corr_xtalk.py
PP_COR_XTALK_AMP_DFLUX = PP_COR_XTALK_AMP_DFLUX.copy(__NAME__)
PP_COR_XTALK_AMP_DFLUX.value = 7.727465e-04
PP_COR_XTALK_AMP_DFLUX.author = base.AUTHORS['EA']

# Define amplitude of the flux-dependent along-readout-axis 2nd derivative
#     component
# TODO: Add calculation to static apero-utils.general.apero_statics.corr_xtalk.py
PP_COR_XTALK_AMP_D2FLUX = PP_COR_XTALK_AMP_D2FLUX.copy(__NAME__)
PP_COR_XTALK_AMP_D2FLUX.value = -2.601081e-04
PP_COR_XTALK_AMP_D2FLUX.author = base.AUTHORS['EA']

# Define the partial APERO DPRTYPES which we should not do the science
#    capacitive coupling
PP_NOSCI_CAPC_DPRTYPES = PP_NOSCI_CAPC_DPRTYPES.copy(__NAME__)
PP_NOSCI_CAPC_DPRTYPES.value = 'HCONE,HCTWO'

# =============================================================================
# CALIBRATION: ASTROMETRIC DATABASE SETTINGS
# =============================================================================
# gaia col name in google sheet
GL_GAIA_COL_NAME = GL_GAIA_COL_NAME.copy(__NAME__)
GL_GAIA_COL_NAME.value = 'GAIADR2ID'
# object col name in google sheet
GL_OBJ_COL_NAME = GL_OBJ_COL_NAME.copy(__NAME__)
GL_OBJ_COL_NAME.value = 'OBJNAME'
# alias col name in google sheet
GL_ALIAS_COL_NAME = GL_ALIAS_COL_NAME.copy(__NAME__)
GL_ALIAS_COL_NAME.value = 'ALIASES'
# rv col name in google sheet
GL_RV_COL_NAME = GL_RV_COL_NAME.copy(__NAME__)
GL_RV_COL_NAME.value = 'RV'
GL_RVREF_COL_NAME = GL_RVREF_COL_NAME.copy(__NAME__)
GL_RVREF_COL_NAME.value = 'RV_REF'
# teff col name in google sheet
GL_TEFF_COL_NAME = GL_TEFF_COL_NAME.copy(__NAME__)
GL_TEFF_COL_NAME.value = 'TEFF'
GL_TEFFREF_COL_NAME = GL_TEFFREF_COL_NAME.copy(__NAME__)
GL_TEFFREF_COL_NAME.value = 'TEFF_REF'
# Reject like google columns
GL_R_ODO_COL = GL_R_ODO_COL.copy(__NAME__)
GL_R_ODO_COL.value = 'ODOMETER'
GL_R_PP_COL = GL_R_PP_COL.copy(__NAME__)
GL_R_PP_COL.value = 'PP'
GL_R_RV_COL = GL_R_RV_COL.copy(__NAME__)
GL_R_RV_COL.value = 'RV'

# =============================================================================
# CALIBRATION: DARK SETTINGS
# =============================================================================
#   Min dark exposure time
QC_DARK_TIME = QC_DARK_TIME.copy(__NAME__)
QC_DARK_TIME.value = 1.0

#   Max dark median level [ADU/s]
QC_MAX_DARKLEVEL = QC_MAX_DARKLEVEL.copy(__NAME__)
QC_MAX_DARKLEVEL.value = 0.07

#   Max fraction of dark pixels (percent)
QC_MAX_DARK = QC_MAX_DARK.copy(__NAME__)
QC_MAX_DARK.value = 1.0

#   Max fraction of dead pixels
QC_MAX_DEAD = QC_MAX_DEAD.copy(__NAME__)
QC_MAX_DEAD.value = 1.0

# Defines the blue resized image
IMAGE_X_BLUE_LOW = IMAGE_X_BLUE_LOW.copy(__NAME__)
IMAGE_X_BLUE_LOW.value = 100
IMAGE_X_BLUE_HIGH = IMAGE_X_BLUE_HIGH.copy(__NAME__)
IMAGE_X_BLUE_HIGH.value = 4000
IMAGE_Y_BLUE_LOW = IMAGE_Y_BLUE_LOW.copy(__NAME__)
IMAGE_Y_BLUE_LOW.value = 3300
IMAGE_Y_BLUE_HIGH = IMAGE_Y_BLUE_HIGH.copy(__NAME__)
IMAGE_Y_BLUE_HIGH.value = 3720

# Defines the red resized image
IMAGE_X_RED_LOW = IMAGE_X_RED_LOW.copy(__NAME__)
IMAGE_X_RED_LOW.value = 100
IMAGE_X_RED_HIGH = IMAGE_X_RED_HIGH.copy(__NAME__)
IMAGE_X_RED_HIGH.value = 4000
IMAGE_Y_RED_LOW = IMAGE_Y_RED_LOW.copy(__NAME__)
IMAGE_Y_RED_LOW.value = 780
IMAGE_Y_RED_HIGH = IMAGE_Y_RED_HIGH.copy(__NAME__)
IMAGE_Y_RED_HIGH.value = 1200

#   Define a bad pixel cut limit (in ADU/s)
DARK_CUTLIMIT = DARK_CUTLIMIT.copy(__NAME__)
DARK_CUTLIMIT.value = 5.0

#   Defines the lower and upper percentiles when measuring the dark
DARK_QMIN = DARK_QMIN.copy(__NAME__)
DARK_QMIN.value = 5
DARK_QMAX = DARK_QMAX.copy(__NAME__)
DARK_QMAX.value = 95

#   The number of bins in dark histogram
HISTO_BINS = HISTO_BINS.copy(__NAME__)
HISTO_BINS.value = 200

#   The range of the histogram in ADU/s
HISTO_RANGE_LOW = HISTO_RANGE_LOW.copy(__NAME__)
HISTO_RANGE_LOW.value = -0.2
HISTO_RANGE_HIGH = HISTO_RANGE_HIGH.copy(__NAME__)
HISTO_RANGE_HIGH.value = 0.8

#    Define the allowed DPRTYPES for finding files for DARK_REF will
#        only find those types define by 'filetype' but 'filetype' must
#        be one of theses (strings separated by commas)
ALLOWED_DARK_TYPES = ALLOWED_DARK_TYPES.copy(__NAME__)
ALLOWED_DARK_TYPES.value = 'DARK_DARK'

#   Define the maximum time span to combine dark files over (in hours)
DARK_REF_MATCH_TIME = DARK_REF_MATCH_TIME.copy(__NAME__)
DARK_REF_MATCH_TIME.value = 2

#   median filter size for dark reference
DARK_REF_MED_SIZE = DARK_REF_MED_SIZE.copy(__NAME__)
DARK_REF_MED_SIZE.value = 4

# define the maximum number of files to use in the dark reference
DARK_REF_MAX_FILES = DARK_REF_MAX_FILES.copy(__NAME__)
DARK_REF_MAX_FILES.value = 100

# define the minimimum allowed exptime for dark files to be used in
#    dark ref
DARK_REF_MIN_EXPTIME = DARK_REF_MIN_EXPTIME.copy(__NAME__)
DARK_REF_MIN_EXPTIME.value = 300

# =============================================================================
# CALIBRATION: BAD PIXEL MAP SETTINGS
# =============================================================================
#   Defines the full detector flat file (located in the data folder)
BADPIX_FULL_FLAT = BADPIX_FULL_FLAT.copy(__NAME__)
BADPIX_FULL_FLAT.value = 'QE_2000nm.fits'

#   Percentile to normalise to when normalising and median filtering
#      image [percentage]
BADPIX_NORM_PERCENTILE = BADPIX_NORM_PERCENTILE.copy(__NAME__)
BADPIX_NORM_PERCENTILE.value = 95.0

#   Define the median image in the x dimension over a boxcar of this width
BADPIX_FLAT_MED_WID = BADPIX_FLAT_MED_WID.copy(__NAME__)
BADPIX_FLAT_MED_WID.value = 7

#   Define the maximum differential pixel cut ratio
BADPIX_FLAT_CUT_RATIO = BADPIX_FLAT_CUT_RATIO.copy(__NAME__)
BADPIX_FLAT_CUT_RATIO.value = 0.5

#   Define the illumination cut parameter
BADPIX_ILLUM_CUT = BADPIX_ILLUM_CUT.copy(__NAME__)
BADPIX_ILLUM_CUT.value = 0.05

#   Define the maximum flux in ADU/s to be considered too hot to be used
BADPIX_MAX_HOTPIX = BADPIX_MAX_HOTPIX.copy(__NAME__)
BADPIX_MAX_HOTPIX.value = 5.0

#   Defines the threshold on the full detector flat file to deem pixels as good
BADPIX_FULL_THRESHOLD = BADPIX_FULL_THRESHOLD.copy(__NAME__)
BADPIX_FULL_THRESHOLD.value = 0.3

#   Defines areas that are large/small for bad pixel erosion
BADPIX_ERODE_SIZE = BADPIX_ERODE_SIZE.copy(__NAME__)
BADPIX_ERODE_SIZE.value = 5

#   Defines how much larger to make eroded bad pixel regions
BADPIX_DILATE_SIZE = BADPIX_DILATE_SIZE.copy(__NAME__)
BADPIX_DILATE_SIZE.value = 9

# =============================================================================
# CALIBRATION: BACKGROUND CORRECTION SETTINGS
# =============================================================================
#    Width of the box to produce the background mask
BKGR_BOXSIZE = BKGR_BOXSIZE.copy(__NAME__)
BKGR_BOXSIZE.value = 32

#    Do background percentile to compute minimum value (%)
BKGR_PERCENTAGE = BKGR_PERCENTAGE.copy(__NAME__)
BKGR_PERCENTAGE.value = 5.0

#    Size in pixels of the convolve tophat for the background mask
BKGR_MASK_CONVOLVE_SIZE = BKGR_MASK_CONVOLVE_SIZE.copy(__NAME__)
BKGR_MASK_CONVOLVE_SIZE.value = 7

#    If a pixel has this or more "dark" neighbours, we consider it dark
#        regardless of its initial value
BKGR_N_BAD_NEIGHBOURS = BKGR_N_BAD_NEIGHBOURS.copy(__NAME__)
BKGR_N_BAD_NEIGHBOURS.value = 3

#    Do background measurement (True or False)
BKGR_NO_SUBTRACTION = BKGR_NO_SUBTRACTION.copy(__NAME__)
BKGR_NO_SUBTRACTION.value = False

#    Kernel amplitude determined from drs_local_scatter.py
BKGR_KER_AMP = BKGR_KER_AMP.copy(__NAME__)
BKGR_KER_AMP.value = 1e9

#    Background kernel width in in x and y [pixels]
BKGR_KER_WX = BKGR_KER_WX.copy(__NAME__)
BKGR_KER_WX.value = 1
BKGR_KER_WY = BKGR_KER_WY.copy(__NAME__)
BKGR_KER_WY.value = 9

#    construct a convolution kernel. We go from -BKGR_KER_SIG to
#        +BKGR_KER_SIG sigma in each direction. Its important no to
#        make the kernel too big as this slows-down the 2D convolution.
#        Do NOT make it a -10 to +10 sigma gaussian!
BKGR_KER_SIG = BKGR_KER_SIG.copy(__NAME__)
BKGR_KER_SIG.value = 3

# =============================================================================
# CALIBRATION: LOCALISATION SETTINGS
# =============================================================================
# median-binning size in the dispersion direction. This is just used to
#     get an order-of-magnitude of the order profile along a given column
LOC_BINSIZE = LOC_BINSIZE.copy(__NAME__)
LOC_BINSIZE.value = 25
LOC_BINSIZE.author = base.AUTHORS['EA']

# the zero point percentile of a box
LOC_BOX_PERCENTILE_LOW = LOC_BOX_PERCENTILE_LOW.copy(__NAME__)
LOC_BOX_PERCENTILE_LOW.value = 25
LOC_BOX_PERCENTILE_LOW.author = base.AUTHORS['EA']

# the percentile of a box that is always an illuminated pixel
LOC_BOX_PERCENTILE_HIGH = LOC_BOX_PERCENTILE_HIGH.copy(__NAME__)
LOC_BOX_PERCENTILE_HIGH.value = 95
LOC_BOX_PERCENTILE_HIGH.author = base.AUTHORS['EA']

# the size of the percentile filter - should be a bit bigger than the
# inter-order gap
LOC_PERCENTILE_FILTER_SIZE = LOC_PERCENTILE_FILTER_SIZE.copy(__NAME__)
LOC_PERCENTILE_FILTER_SIZE.value = 100
LOC_PERCENTILE_FILTER_SIZE.author = base.AUTHORS['EA']

# the fiber dilation number of iterations this should only be used when
#     we want a combined localisation solution i.e. AB from A and B
LOC_FIBER_DILATE_ITERATIONS = LOC_FIBER_DILATE_ITERATIONS.copy(__NAME__)
LOC_FIBER_DILATE_ITERATIONS.value = 3
LOC_FIBER_DILATE_ITERATIONS.author = base.AUTHORS['EA']

# the minimum area (number of pixels) that defines an order
LOC_MIN_ORDER_AREA = LOC_MIN_ORDER_AREA.copy(__NAME__)
LOC_MIN_ORDER_AREA.value = 500
LOC_MIN_ORDER_AREA.author = base.AUTHORS['EA']

# Order of polynomial to fit for widths
LOC_WIDTH_POLY_DEG = LOC_WIDTH_POLY_DEG.copy(__NAME__)
LOC_WIDTH_POLY_DEG.value = 1
LOC_WIDTH_POLY_DEG.author = base.AUTHORS['EA']

# Order of polynomial to fit for positions
LOC_CENT_POLY_DEG = LOC_CENT_POLY_DEG.copy(__NAME__)
LOC_CENT_POLY_DEG.value = 3
LOC_CENT_POLY_DEG.author = base.AUTHORS['EA']

# range width size (used to fit the width of the orders at certain points)
LOC_RANGE_WID_SUM = LOC_RANGE_WID_SUM.copy(__NAME__)
LOC_RANGE_WID_SUM.value = 100
LOC_RANGE_WID_SUM.author = base.AUTHORS['EA']

# define the minimum detector position where the centers of the orders should
#   fall (across order direction)
LOC_YDET_MIN = LOC_YDET_MIN.copy(__NAME__)
LOC_YDET_MIN.value = 40
LOC_YDET_MIN.author = base.AUTHORS['EA']

# define the maximum detector position where the centers of the orders should
#   fall (across order direction)
LOC_YDET_MAX = LOC_YDET_MAX.copy(__NAME__)
LOC_YDET_MAX.value = 4088
LOC_YDET_MAX.author = base.AUTHORS['EA']

# define the number of width samples to use in localisation
LOC_NUM_WID_SAMPLES = LOC_NUM_WID_SAMPLES.copy(__NAME__)
LOC_NUM_WID_SAMPLES.value = 10
LOC_NUM_WID_SAMPLES.author = base.AUTHORS['EA']

# =============================================================================
# CALIBRATION: LOCALISATION SETTINGS
# =============================================================================
#   Size of the order_profile smoothed box
#     (from pixel - size to pixel + size)
LOC_ORDERP_BOX_SIZE = LOC_ORDERP_BOX_SIZE.copy(__NAME__)
LOC_ORDERP_BOX_SIZE.value = 5

#   row number of image to start localisation processing at
LOC_START_ROW_OFFSET = LOC_START_ROW_OFFSET.copy(__NAME__)
LOC_START_ROW_OFFSET.value = 0

#   Definition of the central column for use in localisation
LOC_CENTRAL_COLUMN = LOC_CENTRAL_COLUMN.copy(__NAME__)
LOC_CENTRAL_COLUMN.value = 2000    # 2500

#   Half spacing between orders
LOC_HALF_ORDER_SPACING = LOC_HALF_ORDER_SPACING.copy(__NAME__)
LOC_HALF_ORDER_SPACING.value = 300

# Minimum amplitude to accept (in e-)
LOC_MINPEAK_AMPLITUDE = LOC_MINPEAK_AMPLITUDE.copy(__NAME__)
LOC_MINPEAK_AMPLITUDE.value = 10  # 50

#   Define the jump size when finding the order position
#       (jumps in steps of this from the center outwards)
LOC_COLUMN_SEP_FITTING = LOC_COLUMN_SEP_FITTING.copy(__NAME__)
LOC_COLUMN_SEP_FITTING.value = 5

#   Definition of the extraction window size (half size)
LOC_EXT_WINDOW_SIZE = LOC_EXT_WINDOW_SIZE.copy(__NAME__)
LOC_EXT_WINDOW_SIZE.value = 10

#   Definition of the gap index in the selected area
LOC_IMAGE_GAP = LOC_IMAGE_GAP.copy(__NAME__)
LOC_IMAGE_GAP.value = 0

#   Define minimum width of order to be accepted
LOC_ORDER_WIDTH_MIN = LOC_ORDER_WIDTH_MIN.copy(__NAME__)
LOC_ORDER_WIDTH_MIN.value = 2

#   Define the noise multiplier threshold in order to accept an
#       order center as usable i.e.
#       max(pixel value) - min(pixel value) > THRES * RDNOISE
LOC_NOISE_MULTIPLIER_THRES = LOC_NOISE_MULTIPLIER_THRES.copy(__NAME__)
LOC_NOISE_MULTIPLIER_THRES.value = 50  # 30  #10 # 100.0

#   Maximum rms for sigma-clip order fit (center positions)
LOC_MAX_RMS_CENT = LOC_MAX_RMS_CENT.copy(__NAME__)
LOC_MAX_RMS_CENT.value = 0.1

#   Maximum peak-to-peak for sigma-clip order fit (center positions)
LOC_MAX_PTP_CENT = LOC_MAX_PTP_CENT.copy(__NAME__)
LOC_MAX_PTP_CENT.value = 0.300

#   Maximum frac ptp/rms for sigma-clip order fit (center positions)
LOC_PTPORMS_CENT = LOC_PTPORMS_CENT.copy(__NAME__)
LOC_PTPORMS_CENT.value = 8.0

#   Maximum rms for sigma-clip order fit (width)
LOC_MAX_RMS_WID = LOC_MAX_RMS_WID.copy(__NAME__)
LOC_MAX_RMS_WID.value = 5.0

#   Maximum fractional peak-to-peak for sigma-clip order fit (width)
LOC_MAX_PTP_WID = LOC_MAX_PTP_WID.copy(__NAME__)
LOC_MAX_PTP_WID.value = 30.0

#   Normalised amplitude threshold to accept pixels for background calculation
LOC_BKGRD_THRESHOLD = LOC_BKGRD_THRESHOLD.copy(__NAME__)
LOC_BKGRD_THRESHOLD.value = 0.15  # 0.17  # 0.18

#   Define the amount we drop from the centre of the order when
#      previous order center is missed (in finding the position)
LOC_ORDER_CURVE_DROP = LOC_ORDER_CURVE_DROP.copy(__NAME__)
LOC_ORDER_CURVE_DROP.value = 2.0

# set the sigma clipping cut off value for cleaning coefficients
LOC_COEFF_SIGCLIP = LOC_COEFF_SIGCLIP.copy(__NAME__)
LOC_COEFF_SIGCLIP.value = 5

#  Defines the fit degree to fit in the coefficient cleaning
LOC_COEFFSIG_DEG = LOC_COEFFSIG_DEG.copy(__NAME__)
LOC_COEFFSIG_DEG.value = 5

#  Define the maximum value allowed in the localisation (cuts reddest orders)
LOC_MAX_YPIX_VALUE = LOC_MAX_YPIX_VALUE.copy(__NAME__)
LOC_MAX_YPIX_VALUE.value = 4060

#   Saturation threshold for localisation
LOC_SAT_THRES = LOC_SAT_THRES.copy(__NAME__)
LOC_SAT_THRES.value = 1000  # 64536

#   Maximum points removed in location fit
QC_LOC_MAXFIT_REMOVED_CTR = QC_LOC_MAXFIT_REMOVED_CTR.copy(__NAME__)
QC_LOC_MAXFIT_REMOVED_CTR.value = 1500

#   Maximum points removed in width fit
QC_LOC_MAXFIT_REMOVED_WID = QC_LOC_MAXFIT_REMOVED_WID.copy(__NAME__)
QC_LOC_MAXFIT_REMOVED_WID.value = 105

#   Maximum rms allowed in fitting location
QC_LOC_RMSMAX_CTR = QC_LOC_RMSMAX_CTR.copy(__NAME__)
QC_LOC_RMSMAX_CTR.value = 100

#   Maximum rms allowed in fitting width
QC_LOC_RMSMAX_WID = QC_LOC_RMSMAX_WID.copy(__NAME__)
QC_LOC_RMSMAX_WID.value = 500

#   Option for archiving the location image
LOC_SAVE_SUPERIMP_FILE = LOC_SAVE_SUPERIMP_FILE.copy(__NAME__)
LOC_SAVE_SUPERIMP_FILE.value = True

# set the zoom in levels for the plots (x min value)
LOC_PLOT_CORNER_XZOOM1 = LOC_PLOT_CORNER_XZOOM1.copy(__NAME__)
LOC_PLOT_CORNER_XZOOM1.value = '0, 2044, 0, 2044'

# set the zoom in levels for the plots (x max value)
LOC_PLOT_CORNER_XZOOM2 = LOC_PLOT_CORNER_XZOOM2.copy(__NAME__)
LOC_PLOT_CORNER_XZOOM2.value = '2044, 4088, 2044, 4088'

# set the zoom in levels for the plots (top left corners)
LOC_PLOT_CORNER_YZOOM1 = LOC_PLOT_CORNER_YZOOM1.copy(__NAME__)
LOC_PLOT_CORNER_YZOOM1.value = '0, 0, 2500, 2500'

# set the zoom in levels for the plots (top right corners)
LOC_PLOT_CORNER_YZOOM2 = LOC_PLOT_CORNER_YZOOM2.copy(__NAME__)
LOC_PLOT_CORNER_YZOOM2.value = '600, 600, 3100, 3100'


# =============================================================================
# CALIBRATION: SHAPE SETTINGS
# =============================================================================
#    Define the allowed DPRTYPES for finding files for DARK_REF will
#        only find those types define by 'filetype' but 'filetype' must
#        be one of theses (strings separated by commas)
ALLOWED_FP_TYPES = ALLOWED_FP_TYPES.copy(__NAME__)
ALLOWED_FP_TYPES.value = 'FP_FP'

#   Define the maximum time span to combine dark files over (in hours)
FP_REF_MATCH_TIME = FP_REF_MATCH_TIME.copy(__NAME__)
FP_REF_MATCH_TIME.value = 2

#   Define the percentile at which the FPs are normalised when getting the
#      fp reference in shape reference
FP_REF_PERCENT_THRES = FP_REF_PERCENT_THRES.copy(__NAME__)
FP_REF_PERCENT_THRES.value = 95.0

#  Define the largest standard deviation allowed for the shift in
#     x or y when doing the shape reference fp linear transform
SHAPE_QC_LTRANS_RES_THRES = SHAPE_QC_LTRANS_RES_THRES.copy(__NAME__)
SHAPE_QC_LTRANS_RES_THRES.value = 0.22

# define the maximum number of files to use in the shape reference
SHAPE_REF_MAX_FILES = SHAPE_REF_MAX_FILES.copy(__NAME__)
SHAPE_REF_MAX_FILES.value = 100

#  Define the percentile which defines a true FP peak [0-100]
SHAPE_REF_VALIDFP_PERCENTILE = SHAPE_REF_VALIDFP_PERCENTILE.copy(__NAME__)
SHAPE_REF_VALIDFP_PERCENTILE.value = 95

#  Define the fractional flux an FP much have compared to its neighbours
SHAPE_REF_VALIDFP_THRESHOLD = SHAPE_REF_VALIDFP_THRESHOLD.copy(__NAME__)
SHAPE_REF_VALIDFP_THRESHOLD.value = 1.5

#  Define the number of iterations used to get the linear transform params
SHAPE_REF_LINTRANS_NITER = SHAPE_REF_LINTRANS_NITER.copy(__NAME__)
SHAPE_REF_LINTRANS_NITER.value = 5

#  Define the initial search box size (in pixels) around the fp peaks
SHAPE_REF_FP_INI_BOXSIZE = SHAPE_REF_FP_INI_BOXSIZE.copy(__NAME__)
SHAPE_REF_FP_INI_BOXSIZE.value = 11

#  Define the small search box size (in pixels) around the fp peaks
SHAPE_REF_FP_SMALL_BOXSIZE = SHAPE_REF_FP_SMALL_BOXSIZE.copy(__NAME__)
SHAPE_REF_FP_SMALL_BOXSIZE.value = 2

#  Define the minimum number of FP files in a group to mean group is valid
SHAPE_FP_REF_MIN_IN_GROUP = SHAPE_FP_REF_MIN_IN_GROUP.copy(__NAME__)
SHAPE_FP_REF_MIN_IN_GROUP.value = 3

#  Define which fiber should be used for fiber-dependent calibrations in
#     shape reference
SHAPE_REF_FIBER = SHAPE_REF_FIBER.copy(__NAME__)
SHAPE_REF_FIBER.value = 'A'

#  Define the shape reference dx rms quality control criteria (per order)
SHAPE_REF_DX_RMS_QC = SHAPE_REF_DX_RMS_QC.copy(__NAME__)
SHAPE_REF_DX_RMS_QC.value = 0.3

# The number of iterations to run the shape finding out to
SHAPE_NUM_ITERATIONS = SHAPE_NUM_ITERATIONS.copy(__NAME__)
SHAPE_NUM_ITERATIONS.value = 4

# The order to use on the shape plot
SHAPE_PLOT_SELECTED_ORDER = SHAPE_PLOT_SELECTED_ORDER.copy(__NAME__)
SHAPE_PLOT_SELECTED_ORDER.value = 33

# total width of the order (combined fibers) in pixels
SHAPE_ORDER_WIDTH = SHAPE_ORDER_WIDTH.copy(__NAME__)
SHAPE_ORDER_WIDTH.value = '{"A": 24, "B": 8}'

# number of sections per order to split the order into
SHAPE_NSECTIONS = SHAPE_NSECTIONS.copy(__NAME__)
SHAPE_NSECTIONS.value = 16

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
SHAPE_LARGE_ANGLE_MIN = SHAPE_LARGE_ANGLE_MIN.copy(__NAME__)
SHAPE_LARGE_ANGLE_MIN.value = -20.0

SHAPE_LARGE_ANGLE_MAX = SHAPE_LARGE_ANGLE_MAX.copy(__NAME__)
SHAPE_LARGE_ANGLE_MAX.value = 20.0

SHAPE_SMALL_ANGLE_MIN = SHAPE_SMALL_ANGLE_MIN.copy(__NAME__)
SHAPE_SMALL_ANGLE_MIN.value = -5.0

SHAPE_SMALL_ANGLE_MAX = SHAPE_SMALL_ANGLE_MAX.copy(__NAME__)
SHAPE_SMALL_ANGLE_MAX.value = 5.0

# max sigma clip (in sigma) on points within a section
SHAPE_SIGMACLIP_MAX = SHAPE_SIGMACLIP_MAX.copy(__NAME__)
SHAPE_SIGMACLIP_MAX.value = 4

# the size of the median filter to apply along the order (in pixels)
SHAPE_MEDIAN_FILTER_SIZE = SHAPE_MEDIAN_FILTER_SIZE.copy(__NAME__)
SHAPE_MEDIAN_FILTER_SIZE.value = 51

# The minimum value for the cross-correlation to be deemed good
SHAPE_MIN_GOOD_CORRELATION = SHAPE_MIN_GOOD_CORRELATION.copy(__NAME__)
SHAPE_MIN_GOOD_CORRELATION.value = 0.5

# Define the first pass (short) median filter width for dx
SHAPE_SHORT_DX_MEDFILT_WID = SHAPE_SHORT_DX_MEDFILT_WID.copy(__NAME__)
SHAPE_SHORT_DX_MEDFILT_WID.value = 9

# Define the second pass (long) median filter width for dx.
#    Used to fill NaN positions in dx that are not covered by short pass
SHAPE_LONG_DX_MEDFILT_WID = SHAPE_LONG_DX_MEDFILT_WID.copy(__NAME__)
SHAPE_LONG_DX_MEDFILT_WID.value = 9

#  Defines the largest allowed standard deviation for a given
#    per-order and per-x-pixel shift of the FP peaks
SHAPE_QC_DXMAP_STD = SHAPE_QC_DXMAP_STD.copy(__NAME__)
SHAPE_QC_DXMAP_STD.value = 5

# defines the shape offset xoffset (before and after) fp peaks
SHAPEOFFSET_XOFFSET = SHAPEOFFSET_XOFFSET.copy(__NAME__)
SHAPEOFFSET_XOFFSET.value = 30

# defines the bottom percentile for fp peak
SHAPEOFFSET_BOTTOM_PERCENTILE = SHAPEOFFSET_BOTTOM_PERCENTILE.copy(__NAME__)
SHAPEOFFSET_BOTTOM_PERCENTILE.value = 10

# defines the top percentile for fp peak
SHAPEOFFSET_TOP_PERCENTILE = SHAPEOFFSET_TOP_PERCENTILE.copy(__NAME__)
SHAPEOFFSET_TOP_PERCENTILE.value = 95

# defines the floor below which top values should be set to        
#   this fraction away from the max top value
SHAPEOFFSET_TOP_FLOOR_FRAC = SHAPEOFFSET_TOP_FLOOR_FRAC.copy(__NAME__)
SHAPEOFFSET_TOP_FLOOR_FRAC.value = 0.1

# define the median filter to apply to the hc (high pass filter)
SHAPEOFFSET_MED_FILTER_WIDTH = SHAPEOFFSET_MED_FILTER_WIDTH.copy(__NAME__)
SHAPEOFFSET_MED_FILTER_WIDTH.value = 15

# Maximum number of FP (larger than expected number                
#      (~10000 to ~25000)
SHAPEOFFSET_FPINDEX_MAX = SHAPEOFFSET_FPINDEX_MAX.copy(__NAME__)
SHAPEOFFSET_FPINDEX_MAX.value = 30000

# Define the valid length of a FP peak
SHAPEOFFSET_VALID_FP_LENGTH = SHAPEOFFSET_VALID_FP_LENGTH.copy(__NAME__)
SHAPEOFFSET_VALID_FP_LENGTH.value = 5

# Define the maximum allowed offset (in nm) that we allow for      
#     the detector)
SHAPEOFFSET_DRIFT_MARGIN = SHAPEOFFSET_DRIFT_MARGIN.copy(__NAME__)
SHAPEOFFSET_DRIFT_MARGIN.value = 20

# Define the number of iterations to do for the wave_fp            
#     inversion trick
SHAPEOFFSET_WAVEFP_INV_IT = SHAPEOFFSET_WAVEFP_INV_IT.copy(__NAME__)
SHAPEOFFSET_WAVEFP_INV_IT.value = 5

# Define the border in pixels at the edge of the detector
SHAPEOFFSET_MASK_BORDER = SHAPEOFFSET_MASK_BORDER.copy(__NAME__)
SHAPEOFFSET_MASK_BORDER.value = 30

# Define the minimum maxpeak value as a fraction of the            
#    maximum maxpeak
SHAPEOFFSET_MIN_MAXPEAK_FRAC = SHAPEOFFSET_MIN_MAXPEAK_FRAC.copy(__NAME__)
SHAPEOFFSET_MIN_MAXPEAK_FRAC.value = 0.4

# Define the width of the FP mask (+/- the center)
SHAPEOFFSET_MASK_PIXWIDTH = SHAPEOFFSET_MASK_PIXWIDTH.copy(__NAME__)
SHAPEOFFSET_MASK_PIXWIDTH.value = 3

# Define the width of the FP to extract (+/- the center)
SHAPEOFFSET_MASK_EXTWIDTH = SHAPEOFFSET_MASK_EXTWIDTH.copy(__NAME__)
SHAPEOFFSET_MASK_EXTWIDTH.value = 5

# Define the most deviant peaks - percentile from [min to max]
SHAPEOFFSET_DEVIANT_PMIN = SHAPEOFFSET_DEVIANT_PMIN.copy(__NAME__)
SHAPEOFFSET_DEVIANT_PMIN.value = 5

SHAPEOFFSET_DEVIANT_PMAX = SHAPEOFFSET_DEVIANT_PMAX.copy(__NAME__)
SHAPEOFFSET_DEVIANT_PMAX.value = 95

# Define the maximum error in FP order assignment                  
#    we assume that the error in FP order assignment could range
#    from -50 to +50 in practice, it is -1, 0 or +1 for the cases we've
#    tested to date
SHAPEOFFSET_FPMAX_NUM_ERROR = SHAPEOFFSET_FPMAX_NUM_ERROR.copy(__NAME__)
SHAPEOFFSET_FPMAX_NUM_ERROR.value = 50

# The number of sigmas that the HC spectrum is allowed to be       
#     away from the predicted (from FP) position
SHAPEOFFSET_FIT_HC_SIGMA = SHAPEOFFSET_FIT_HC_SIGMA.copy(__NAME__)
SHAPEOFFSET_FIT_HC_SIGMA.value = 3

# Define the maximum allowed maximum absolute deviation away       
#     from the error fit
SHAPEOFFSET_MAXDEV_THRESHOLD = SHAPEOFFSET_MAXDEV_THRESHOLD.copy(__NAME__)
SHAPEOFFSET_MAXDEV_THRESHOLD.value = 5

# very low thresholding values tend to clip valid points
SHAPEOFFSET_ABSDEV_THRESHOLD = SHAPEOFFSET_ABSDEV_THRESHOLD.copy(__NAME__)
SHAPEOFFSET_ABSDEV_THRESHOLD.value = 0.2

# define the names of the unique fibers (i.e. not AB) for use in
#     getting the localisation coefficients for dymap
SHAPE_UNIQUE_FIBERS = SHAPE_UNIQUE_FIBERS.copy(__NAME__)
SHAPE_UNIQUE_FIBERS.value = 'A, B'

#  Define first zoom plot for shape local zoom debug plot
#     should be a string list (xmin, xmax, ymin, ymax)
SHAPEL_PLOT_ZOOM1 = SHAPEL_PLOT_ZOOM1.copy(__NAME__)
SHAPEL_PLOT_ZOOM1.value = '1844, 2244, 0, 400'

#  Define second zoom plot for shape local zoom debug plot
#     should be a string list (xmin, xmax, ymin, ymax)
SHAPEL_PLOT_ZOOM2 = SHAPEL_PLOT_ZOOM2.copy(__NAME__)
SHAPEL_PLOT_ZOOM2.value = '1844, 2244, 2700, 3100'

# =============================================================================
# CALIBRATION: FLAT SETTINGS
# =============================================================================
#    Half size blaze smoothing window
FF_BLAZE_HALF_WINDOW = FF_BLAZE_HALF_WINDOW.copy(__NAME__)
FF_BLAZE_HALF_WINDOW.value = 50

# Minimum relative e2ds flux for the blaze computation
FF_BLAZE_THRESHOLD = FF_BLAZE_THRESHOLD.copy(__NAME__)
FF_BLAZE_THRESHOLD.value = 16.0

#    The blaze polynomial fit degree
FF_BLAZE_DEGREE = FF_BLAZE_DEGREE.copy(__NAME__)
FF_BLAZE_DEGREE.value = 10

# Define the threshold, expressed as the fraction of the maximum peak, below
#    this threshold the blaze (and e2ds) is set to NaN
FF_BLAZE_SCUT = FF_BLAZE_SCUT.copy(__NAME__)
FF_BLAZE_SCUT.value = 0.1

# Define the rejection threshold for the blaze sinc fit
FF_BLAZE_SIGFIT = FF_BLAZE_SIGFIT.copy(__NAME__)
FF_BLAZE_SIGFIT.value = 4.0

# Define the hot bad pixel percentile level (using in blaze sinc fit)
FF_BLAZE_BPERCENTILE = FF_BLAZE_BPERCENTILE.copy(__NAME__)
FF_BLAZE_BPERCENTILE.value = 95

# Define the number of times to iterate around blaze sinc fit
FF_BLAZE_NITER = FF_BLAZE_NITER.copy(__NAME__)
FF_BLAZE_NITER.value = 2

# Define the sinc fit median filter width (we want to fit the shape of the
#   order not line structures)
FF_BLAZE_SINC_MED_SIZE = FF_BLAZE_SINC_MED_SIZE.copy(__NAME__)
FF_BLAZE_SINC_MED_SIZE.value = 50

#   Define the orders not to plot on the RMS plot should be a string
#       containing a list of integers
FF_RMS_SKIP_ORDERS = FF_RMS_SKIP_ORDERS.copy(__NAME__)
FF_RMS_SKIP_ORDERS.value = '[0, 22, 23, 24, 25, 48]'

#   Maximum allowed RMS of flat field
# TODO: This needs to be changed back original value 0.10
QC_FF_MAX_RMS = QC_FF_MAX_RMS.copy(__NAME__)
QC_FF_MAX_RMS.value = 1.0

# Define the order to plot in summary plots
FF_PLOT_ORDER = FF_PLOT_ORDER.copy(__NAME__)
FF_PLOT_ORDER.value = 4

# Define the high pass filter size in pixels
FF_HIGH_PASS_SIZE = FF_HIGH_PASS_SIZE.copy(__NAME__)
FF_HIGH_PASS_SIZE.value = 501
FF_HIGH_PASS_SIZE.author = base.AUTHORS['EA']

# =============================================================================
# CALIBRATION: LEAKAGE SETTINGS
# =============================================================================
# Define the types of input file allowed by the leakage reference recipe
ALLOWED_LEAKREF_TYPES = ALLOWED_LEAKREF_TYPES.copy(__NAME__)
ALLOWED_LEAKREF_TYPES.value = 'DARK_FP'

# define whether to always extract leak reference files
#      (i.e. overwrite existing files)
LEAKREF_ALWAYS_EXTRACT = LEAKREF_ALWAYS_EXTRACT.copy(__NAME__)
LEAKREF_ALWAYS_EXTRACT.value = False

# define the type of file to use for leak reference solution
#    (currently allowed are 'E2DSFF') - must match with LEAK_EXTRACT_FILE
LEAKREF_EXTRACT_TYPE = LEAKREF_EXTRACT_TYPE.copy(__NAME__)
LEAKREF_EXTRACT_TYPE.value = 'E2DSFF'

# Define whether we want to correct leakage by default
CORRECT_LEAKAGE = CORRECT_LEAKAGE.copy(__NAME__)
CORRECT_LEAKAGE.value = True

# Define DPRTYPE in reference fiber to do correction
LEAKAGE_REF_TYPES = LEAKAGE_REF_TYPES.copy(__NAME__)
LEAKAGE_REF_TYPES.value = 'FP'

# define the maximum number of files to use in the leak reference
LEAK_REF_MAX_FILES = LEAK_REF_MAX_FILES.copy(__NAME__)
LEAK_REF_MAX_FILES.value = 20

# define the type of file to use for the leak correction (currently allowed are
#     'E2DS_FILE' or 'E2DSFF_FILE' (linked to recipe definition outputs)
#     must match with LEAKREF_EXTRACT_TYPE
LEAK_EXTRACT_FILE = LEAK_EXTRACT_FILE.copy(__NAME__)
LEAK_EXTRACT_FILE.value = 'E2DSFF_FILE'

# define the extraction files which are 2D images (i.e. order num x nbpix)
LEAK_2D_EXTRACT_FILES = LEAK_2D_EXTRACT_FILES.copy(__NAME__)
LEAK_2D_EXTRACT_FILES.value = 'E2DS_FILE, E2DSFF_FILE'

# define the extraction files which are 1D spectra
LEAK_1D_EXTRACT_FILES = LEAK_1D_EXTRACT_FILES.copy(__NAME__)
LEAK_1D_EXTRACT_FILES.value = 'S1D_W_FILE, S1D_V_FILE'

# define the thermal background percentile for the leak and leak reference
LEAK_BCKGRD_PERCENTILE = LEAK_BCKGRD_PERCENTILE.copy(__NAME__)
LEAK_BCKGRD_PERCENTILE.value = 5

# define the normalisation perentile for the leak and leak reference
LEAK_NORM_PERCENTILE = LEAK_NORM_PERCENTILE.copy(__NAME__)
LEAK_NORM_PERCENTILE.value = 90

# define the e-width of the smoothing kernel for leak reference
LEAKREF_WSMOOTH = LEAKREF_WSMOOTH.copy(__NAME__)
LEAKREF_WSMOOTH.value = 15

# define the kernal size for leak reference
LEAKREF_KERSIZE = LEAKREF_KERSIZE.copy(__NAME__)
LEAKREF_KERSIZE.value = 3

# define the lower bound percentile for leak correction
LEAK_LOW_PERCENTILE = LEAK_LOW_PERCENTILE.copy(__NAME__)
LEAK_LOW_PERCENTILE.value = 1

# define the upper bound percentile for leak correction
LEAK_HIGH_PERCENTILE = LEAK_HIGH_PERCENTILE.copy(__NAME__)
LEAK_HIGH_PERCENTILE.value = 99

# define the limit on surpious FP ratio (1 +/- limit)
LEAK_BAD_RATIO_OFFSET = LEAK_BAD_RATIO_OFFSET.copy(__NAME__)
LEAK_BAD_RATIO_OFFSET.value = 0.1

# =============================================================================
# CALIBRATION: EXTRACTION SETTINGS
# =============================================================================
#    Whether extraction code is done in quick look mode (do not use for
#       final products)
EXT_QUICK_LOOK = EXT_QUICK_LOOK.copy(__NAME__)
EXT_QUICK_LOOK.value = False

#    Start order of the extraction in apero_flat if None starts from 0
EXT_START_ORDER = EXT_START_ORDER.copy(__NAME__)
EXT_START_ORDER.value = None

#    End order of the extraction in apero_flat if None ends at last order
EXT_END_ORDER = EXT_END_ORDER.copy(__NAME__)
EXT_END_ORDER.value = None

#   Half-zone extraction width left side (formally plage1)
EXT_RANGE1 = EXT_RANGE1.copy(__NAME__)
EXT_RANGE1.value = '{"A":9, "B":2}'

#   Half-zone extraction width right side (formally plage2)
EXT_RANGE2 = EXT_RANGE2.copy(__NAME__)
EXT_RANGE2.value = '{"A":9, "B":2}'

#   Define the orders to skip extraction on (will set all order values
#      to NaN. If empty list no orders are skipped. Should be a string
#      containing a valid python list
EXT_SKIP_ORDERS = EXT_SKIP_ORDERS.copy(__NAME__)
EXT_SKIP_ORDERS.value = '[]'

#    Defines whether to run extraction with cosmic correction
EXT_COSMIC_CORRETION = EXT_COSMIC_CORRETION.copy(__NAME__)
EXT_COSMIC_CORRETION.value = True

#    Define the number of sigmas away from the median flux which we use to
#       cut cosmic rays
EXT_COSMIC_SIGCUT = EXT_COSMIC_SIGCUT.copy(__NAME__)
EXT_COSMIC_SIGCUT.value = 10

#    Defines the maximum number of iterations we use to check for cosmics
#        (for each pixel)
EXT_COSMIC_THRESHOLD = EXT_COSMIC_THRESHOLD.copy(__NAME__)
EXT_COSMIC_THRESHOLD.value = 5

#   Saturation level reached warning
QC_EXT_FLUX_MAX = QC_EXT_FLUX_MAX.copy(__NAME__)
QC_EXT_FLUX_MAX.value = 50000

# Define which extraction file to use for s1d creation
EXT_S1D_INTYPE = EXT_S1D_INTYPE.copy(__NAME__)
EXT_S1D_INTYPE.value = 'E2DSFF'
# Define which extraction file (recipe definitons) linked to EXT_S1D_INTYPE
EXT_S1D_INFILE = EXT_S1D_INFILE.copy(__NAME__)
EXT_S1D_INFILE.value = 'E2DSFF_FILE'

# Define the start s1d wavelength (in nm)
EXT_S1D_WAVESTART = EXT_S1D_WAVESTART.copy(__NAME__)
EXT_S1D_WAVESTART.value = 965

# Define the end s1d wavelength (in nm)
EXT_S1D_WAVEEND = EXT_S1D_WAVEEND.copy(__NAME__)
EXT_S1D_WAVEEND.value = 1950

#  Define the s1d spectral bin for S1D spectra (nm) when uniform in wavelength
EXT_S1D_BIN_UWAVE = EXT_S1D_BIN_UWAVE.copy(__NAME__)
EXT_S1D_BIN_UWAVE.value = 0.005

#  Define the s1d spectral bin for S1D spectra (km/s) when uniform in velocity
EXT_S1D_BIN_UVELO = EXT_S1D_BIN_UVELO.copy(__NAME__)
EXT_S1D_BIN_UVELO.value = 0.5

#  Define the s1d smoothing kernel for the transition between orders in pixels
EXT_S1D_EDGE_SMOOTH_SIZE = EXT_S1D_EDGE_SMOOTH_SIZE.copy(__NAME__)
EXT_S1D_EDGE_SMOOTH_SIZE.value = 20

#    Define dprtypes to calculate berv for (should be a string list)
EXT_ALLOWED_BERV_DPRTYPES = EXT_ALLOWED_BERV_DPRTYPES.copy(__NAME__)
EXT_ALLOWED_BERV_DPRTYPES.value = 'OBJ_FP, OBJ_DARK, OBJ_SKY, TELLU_SKY, FLUXSTD_SKY'

#    Define which BERV calculation to use ('barycorrpy' or 'estimate' or 'None')
EXT_BERV_KIND = EXT_BERV_KIND.copy(__NAME__)
EXT_BERV_KIND.value = 'barycorrpy'

#   Define the barycorrpy data directory
EXT_BERV_BARYCORRPY_DIR = EXT_BERV_BARYCORRPY_DIR.copy(__NAME__)
EXT_BERV_BARYCORRPY_DIR.value = './data/core/barycorrpy/'

#   Define the barycorrpy iers file
EXT_BERV_IERSFILE = EXT_BERV_IERSFILE.copy(__NAME__)
EXT_BERV_IERSFILE.value = 'finals2000A.all'

#   Define the barycorrpy iers a url
EXT_BERV_IERS_A_URL = EXT_BERV_IERS_A_URL.copy(__NAME__)
EXT_BERV_IERS_A_URL.value = 'ftp://cddis.gsfc.nasa.gov/pub/products/iers/finals2000A.all'

#   Define barycorrpy leap directory
EXT_BERV_LEAPDIR = EXT_BERV_LEAPDIR.copy(__NAME__)
EXT_BERV_LEAPDIR.value = './data/core/barycorrpy/'

#   Define whether to update leap seconds if older than 6 months
EXT_BERV_LEAPUPDATE = EXT_BERV_LEAPUPDATE.copy(__NAME__)
EXT_BERV_LEAPUPDATE.value = True

#    Define the accuracy of the estimate (for logging only) [m/s]
EXT_BERV_EST_ACC = EXT_BERV_EST_ACC.copy(__NAME__)
EXT_BERV_EST_ACC.value = 10.0

# Define the order to plot in summary plots
EXTRACT_PLOT_ORDER = EXTRACT_PLOT_ORDER.copy(__NAME__)
EXTRACT_PLOT_ORDER.value = 4

# Define the wavelength lower bounds for s1d plots
#     (must be a string list of floats) defines the lower wavelength in nm
EXTRACT_S1D_PLOT_ZOOM1 = EXTRACT_S1D_PLOT_ZOOM1.copy(__NAME__)
EXTRACT_S1D_PLOT_ZOOM1.value = '990, 1100, 1200, 1250, 1700'

# Define the wavelength upper bounds for s1d plots
#     (must be a string list of floats) defines the upper wavelength in nm
EXTRACT_S1D_PLOT_ZOOM2 = EXTRACT_S1D_PLOT_ZOOM2.copy(__NAME__)
EXTRACT_S1D_PLOT_ZOOM2.value = '1050, 1200, 1210, 1300, 1800'


# =============================================================================
# CALIBRATION: WAVE EA GENERAL SETTINGS
# =============================================================================
# Define wave reference fiber (controller fiber)
WAVE_REF_FIBER = WAVE_REF_FIBER.copy(__NAME__)
WAVE_REF_FIBER.value = 'A'
WAVE_REF_FIBER.author = base.AUTHORS['NJC']

# Define the initial value of FP effective cavity width 2xd in nm
WAVE_GUESS_CAVITY_WIDTH = WAVE_GUESS_CAVITY_WIDTH.copy(__NAME__)
WAVE_GUESS_CAVITY_WIDTH.value = 2.4e7
WAVE_GUESS_CAVITY_WIDTH.author = base.AUTHORS['EA']

# Define the wave solution polynomial fit degree
WAVE_WAVESOL_FIT_DEGREE = WAVE_WAVESOL_FIT_DEGREE.copy(__NAME__)
WAVE_WAVESOL_FIT_DEGREE.value = 5
WAVE_WAVESOL_FIT_DEGREE.author = base.AUTHORS['EA']

# Define the cavity fit polynomial fit degree for wave solution
#   Note default: 9 for spirou  3 for NIRPS
WAVE_CAVITY_FIT_DEGREE = WAVE_CAVITY_FIT_DEGREE.copy(__NAME__)
WAVE_CAVITY_FIT_DEGREE.value = 5
WAVE_CAVITY_FIT_DEGREE.author = base.AUTHORS['EA']

# Define the number of sigmas to use in wave sol robust fits
WAVE_NSIG_CUT = WAVE_NSIG_CUT.copy(__NAME__)
WAVE_NSIG_CUT.value = 5
WAVE_NSIG_CUT.author = base.AUTHORS['EA']

# Define the minimum number of HC lines in an order to try to find
#   absolute numbering
WAVE_MIN_HC_LINES = WAVE_MIN_HC_LINES.copy(__NAME__)
WAVE_MIN_HC_LINES.value = 5
WAVE_MIN_HC_LINES.author = base.AUTHORS['EA']

# Define the minimum number of HC lines in an order to try to find
#   absolute numbering
WAVE_MIN_FP_LINES = WAVE_MIN_FP_LINES.copy(__NAME__)
WAVE_MIN_FP_LINES.value = 5
WAVE_MIN_FP_LINES.author = base.AUTHORS['EA']

# Define the maximum offset in FP peaks to explore when FP peak counting
WAVE_MAX_FP_COUNT_OFFSET = WAVE_MAX_FP_COUNT_OFFSET.copy(__NAME__)
WAVE_MAX_FP_COUNT_OFFSET.value = 5
WAVE_MAX_FP_COUNT_OFFSET.author = base.AUTHORS['EA']

# Define the number of iterations required to converge the FP peak counting
#   offset loop
WAVE_FP_COUNT_OFFSET_ITRS = WAVE_FP_COUNT_OFFSET_ITRS.copy(__NAME__)
WAVE_FP_COUNT_OFFSET_ITRS.value = 3
WAVE_FP_COUNT_OFFSET_ITRS.author = base.AUTHORS['EA']

# Define the number of iterations required to converge on a cavity fit
#  (first time this is done)
WAVE_CAVITY_FIT_ITRS1 = WAVE_CAVITY_FIT_ITRS1.copy(__NAME__)
WAVE_CAVITY_FIT_ITRS1.value = 3
WAVE_CAVITY_FIT_ITRS1.author = base.AUTHORS['EA']

# Define the number of iterations required to check order offset
WAVE_ORDER_OFFSET_ITRS = WAVE_ORDER_OFFSET_ITRS.copy(__NAME__)
WAVE_ORDER_OFFSET_ITRS.value = 2
WAVE_ORDER_OFFSET_ITRS.author = base.AUTHORS['EA']

# Define the maximum bulk offset of lines in a order can have
WAVE_MAX_ORDER_BULK_OFFSET = WAVE_MAX_ORDER_BULK_OFFSET.copy(__NAME__)
WAVE_MAX_ORDER_BULK_OFFSET.value = 10
WAVE_MAX_ORDER_BULK_OFFSET.author = base.AUTHORS['EA']

# Define the required precision that the cavity width change must converge
#   to (will be a fraction of the error)
WAVE_CAVITY_CHANGE_ERR_THRES = WAVE_CAVITY_CHANGE_ERR_THRES.copy(__NAME__)
WAVE_CAVITY_CHANGE_ERR_THRES.value = 1.0e-2
WAVE_CAVITY_CHANGE_ERR_THRES.author = base.AUTHORS['EA']

# Define the number of iterations required to converge on a cavity fit
#  (second time this is done)
WAVE_CAVITY_FIT_ITRS2 = WAVE_CAVITY_FIT_ITRS2.copy(__NAME__)
WAVE_CAVITY_FIT_ITRS2.value = 3
WAVE_CAVITY_FIT_ITRS2.author = base.AUTHORS['EA']

# Define the odd ratio that is used in generating the weighted mean
WAVE_HC_VEL_ODD_RATIO = WAVE_HC_VEL_ODD_RATIO.copy(__NAME__)
WAVE_HC_VEL_ODD_RATIO.value = 1.0e-2
WAVE_HC_VEL_ODD_RATIO.author = base.AUTHORS['EA']

# Define orders that we cannot fit HC or FP lines to (list of strings)
WAVE_REMOVE_ORDERS = WAVE_REMOVE_ORDERS.copy(__NAME__)
WAVE_REMOVE_ORDERS.value = '44, 45'

# Define the number of iterations required to do the final fplines
#   wave solution
WAVE_FWAVESOL_ITRS = WAVE_FWAVESOL_ITRS.copy(__NAME__)
WAVE_FWAVESOL_ITRS.value = 3
WAVE_FWAVESOL_ITRS.author = base.AUTHORS['EA']

# define the wave fiber comparison plot order number
WAVE_FIBER_COMP_PLOT_ORD = WAVE_FIBER_COMP_PLOT_ORD.copy(__NAME__)
WAVE_FIBER_COMP_PLOT_ORD.value = 53
WAVE_FIBER_COMP_PLOT_ORD.author = base.AUTHORS['NJC']

# =============================================================================
# CALIBRATION: WAVE LINES REFERENCE SETTINGS
# =============================================================================
# min SNR to consider the line (for HC)
WAVEREF_NSIG_MIN_HC = WAVEREF_NSIG_MIN_HC.copy(__NAME__)
WAVEREF_NSIG_MIN_HC.value = 3
WAVEREF_NSIG_MIN_HC.author = base.AUTHORS['EA']

# min SNR to consider the line (for FP)
WAVEREF_NSIG_MIN_FP = WAVEREF_NSIG_MIN_FP.copy(__NAME__)
WAVEREF_NSIG_MIN_FP.value = 3
WAVEREF_NSIG_MIN_FP.author = base.AUTHORS['EA']

# minimum distance to the edge of the array to consider a line
WAVEREF_EDGE_WMAX = WAVEREF_EDGE_WMAX.copy(__NAME__)
WAVEREF_EDGE_WMAX.value = 20
WAVEREF_EDGE_WMAX.author = base.AUTHORS['EA']

# value in pixel (+/-) for the box size around each HC line to perform fit
WAVEREF_HC_BOXSIZE = WAVEREF_HC_BOXSIZE.copy(__NAME__)
WAVEREF_HC_BOXSIZE.value = 13
WAVEREF_HC_BOXSIZE.author = base.AUTHORS['EA']

# get valid hc dprtypes (string list separated by commas)
WAVEREF_HC_FIBTYPES = WAVEREF_HC_FIBTYPES.copy(__NAME__)
WAVEREF_HC_FIBTYPES.value = 'HCONE, HCTWO'
WAVEREF_HC_FIBTYPES.author = base.AUTHORS['NJC']

# get valid fp dprtypes (string list separated by commas)
WAVEREF_FP_FIBTYPES = WAVEREF_FP_FIBTYPES.copy(__NAME__)
WAVEREF_FP_FIBTYPES.value = 'FP'
WAVEREF_FP_FIBTYPES.author = base.AUTHORS['NJC']

# get the degree to fix reference wavelength to in hc mode
WAVEREF_FITDEG = WAVEREF_FITDEG.copy(__NAME__)
WAVEREF_FITDEG.value = 5
WAVEREF_FITDEG.author = base.AUTHORS['EA']

# define the lowest N for fp peaks
WAVEREF_FP_NLOW = WAVEREF_FP_NLOW.copy(__NAME__)
WAVEREF_FP_NLOW.value = 7500
WAVEREF_FP_NLOW.author = base.AUTHORS['EA']

# define the highest N for fp peaks
WAVEREF_FP_NHIGH = WAVEREF_FP_NHIGH.copy(__NAME__)
WAVEREF_FP_NHIGH.value = 30000
WAVEREF_FP_NHIGH.author = base.AUTHORS['EA']

# define the number of iterations required to do the FP polynomial inversion
WAVEREF_FP_POLYINV = WAVEREF_FP_POLYINV.copy(__NAME__)
WAVEREF_FP_POLYINV.value = 4
WAVEREF_FP_POLYINV.author = base.AUTHORS['EA']

# define the guess HC exponetial width [pixels]
WAVEREF_HC_GUESS_EWID = WAVEREF_HC_GUESS_EWID.copy(__NAME__)
WAVEREF_HC_GUESS_EWID.value = 1
WAVEREF_HC_GUESS_EWID.author = base.AUTHORS['EA']

# Define the fiber offset (in pixels) away from reference fiber
WAVE_FIBER_OFFSET_MOD = WAVE_FIBER_OFFSET_MOD.copy(__NAME__)
WAVE_FIBER_OFFSET_MOD.value = '{"A":0.0, "B":-20.0}'
WAVE_FIBER_OFFSET_MOD.author = base.AUTHORS['EA']

# Define the fiber scale factor from reference fiber
WAVE_FIBER_SCALE_MOD = WAVE_FIBER_SCALE_MOD.copy(__NAME__)
WAVE_FIBER_SCALE_MOD.value = '{"A":1.0, "B":0.99766}'
WAVE_FIBER_SCALE_MOD.author = base.AUTHORS['EA']

# =============================================================================
# CALIBRATION: WAVE RESOLUTION MAP SETTINGS
# =============================================================================
# define the number of bins in order direction to use in the resolution map
WAVE_RES_MAP_ORDER_BINS = WAVE_RES_MAP_ORDER_BINS.copy(__NAME__)
WAVE_RES_MAP_ORDER_BINS.value = 4
WAVE_RES_MAP_ORDER_BINS.author = base.AUTHORS['EA']

# define the number of bins in spatial direction to use in the resolution map
WAVE_RES_MAP_SPATIAL_BINS = WAVE_RES_MAP_SPATIAL_BINS.copy(__NAME__)
WAVE_RES_MAP_SPATIAL_BINS.value = 4
WAVE_RES_MAP_SPATIAL_BINS.author = base.AUTHORS['EA']

# define the low pass filter size for the HC E2DS file in the resolution map
WAVE_RES_MAP_FILTER_SIZE = WAVE_RES_MAP_FILTER_SIZE.copy(__NAME__)
WAVE_RES_MAP_FILTER_SIZE.value = 101
WAVE_RES_MAP_FILTER_SIZE.author = base.AUTHORS['EA']

# define the broad resolution map velocity cut off (in km/s)
WAVE_RES_VELO_CUTOFF1 = WAVE_RES_VELO_CUTOFF1.copy(__NAME__)
WAVE_RES_VELO_CUTOFF1.value = 20
WAVE_RES_VELO_CUTOFF1.author = base.AUTHORS['EA']

# define the tight resolution map velocity cut off (in km/s)
WAVE_RES_VELO_CUTOFF2 = WAVE_RES_VELO_CUTOFF2.copy(__NAME__)
WAVE_RES_VELO_CUTOFF2.value = 5
WAVE_RES_VELO_CUTOFF2.author = base.AUTHORS['EA']

# =============================================================================
# CALIBRATION: WAVE CCF SETTINGS
# =============================================================================
#   The value of the noise for wave dv rms calculation
#       snr = flux/sqrt(flux + noise^2)
WAVE_CCF_NOISE_SIGDET = WAVE_CCF_NOISE_SIGDET.copy(__NAME__)
WAVE_CCF_NOISE_SIGDET.value = 8.0  # 100

#   The size around a saturated pixel to flag as unusable for wave dv rms
#      calculation
WAVE_CCF_NOISE_BOXSIZE = WAVE_CCF_NOISE_BOXSIZE.copy(__NAME__)
WAVE_CCF_NOISE_BOXSIZE.value = 12

#   The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
WAVE_CCF_NOISE_THRES = WAVE_CCF_NOISE_THRES.copy(__NAME__)
WAVE_CCF_NOISE_THRES.value = 1.0e9

#   The CCF step size to use for the FP CCF
WAVE_CCF_STEP = WAVE_CCF_STEP.copy(__NAME__)
WAVE_CCF_STEP.value = 0.5

#   The CCF width size to use for the FP CCF
WAVE_CCF_WIDTH = WAVE_CCF_WIDTH.copy(__NAME__)
WAVE_CCF_WIDTH.value = 7.5

#   The target RV (CCF center) to use for the FP CCF
WAVE_CCF_TARGET_RV = WAVE_CCF_TARGET_RV.copy(__NAME__)
WAVE_CCF_TARGET_RV.value = 0.0

#  The detector noise to use for the FP CCF
WAVE_CCF_DETNOISE = WAVE_CCF_DETNOISE.copy(__NAME__)
WAVE_CCF_DETNOISE.value = 100.0

#  The filename of the CCF Mask to use for the FP CCF
#     Note this file is copied over if WAVE_CCF_UPDATE_MASK = True
WAVE_CCF_MASK = WAVE_CCF_MASK.copy(__NAME__)
WAVE_CCF_MASK.value = 'smart_fp_mask.mas'

# Define the default CCF MASK normalisation mode for FP CCF
#   options are:
#     'None'         for no normalization
#     'all'          for normalization across all orders
#     'order'        for normalization for each order
WAVE_CCF_MASK_NORMALIZATION = WAVE_CCF_MASK_NORMALIZATION.copy(__NAME__)
WAVE_CCF_MASK_NORMALIZATION.value = 'order'

# Define the wavelength units for the mask for the FP CCF
WAVE_CCF_MASK_UNITS = WAVE_CCF_MASK_UNITS.copy(__NAME__)
WAVE_CCF_MASK_UNITS.value = 'nm'

# Define the ccf mask path the FP CCF
WAVE_CCF_MASK_PATH = WAVE_CCF_MASK_PATH.copy(__NAME__)
WAVE_CCF_MASK_PATH.value = 'ccf_masks/'

# Define the CCF mask format (must be an astropy.table format)
WAVE_CCF_MASK_FMT = WAVE_CCF_MASK_FMT.copy(__NAME__)
WAVE_CCF_MASK_FMT.value = 'ascii'

#  Define the weight of the CCF mask (if 1 force all weights equal)
WAVE_CCF_MASK_MIN_WEIGHT = WAVE_CCF_MASK_MIN_WEIGHT.copy(__NAME__)
WAVE_CCF_MASK_MIN_WEIGHT.value = 0.0

#  Define the width of the template line (if 0 use natural)
WAVE_CCF_MASK_WIDTH = WAVE_CCF_MASK_WIDTH.copy(__NAME__)
WAVE_CCF_MASK_WIDTH.value = 1.7

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#      to calculate the FP CCF
WAVE_CCF_N_ORD_MAX = WAVE_CCF_N_ORD_MAX.copy(__NAME__)
WAVE_CCF_N_ORD_MAX.value = 48

#  Define whether to regenerate the fp mask (WAVE_CCF_MASK) when we
#      update the cavity width in the reference wave solution recipe
WAVE_CCF_UPDATE_MASK = WAVE_CCF_UPDATE_MASK.copy(__NAME__)
WAVE_CCF_UPDATE_MASK.value = True

# define the width of the lines in the smart mask [km/s]
WAVE_CCF_SMART_MASK_WIDTH = WAVE_CCF_SMART_MASK_WIDTH.copy(__NAME__)
WAVE_CCF_SMART_MASK_WIDTH.value = 1.0

# define the minimum wavelength for the smart mask [nm]
WAVE_CCF_SMART_MASK_MINLAM = WAVE_CCF_SMART_MASK_MINLAM.copy(__NAME__)
WAVE_CCF_SMART_MASK_MINLAM.value = 950

# define the maximum wavelength for the smart mask [nm]
WAVE_CCF_SMART_MASK_MAXLAM = WAVE_CCF_SMART_MASK_MAXLAM.copy(__NAME__)
WAVE_CCF_SMART_MASK_MAXLAM.value = 2500

# define a trial minimum FP N value (should be lower than true
#     minimum FP N value)
WAVE_CCF_SMART_MASK_TRIAL_NMIN = WAVE_CCF_SMART_MASK_TRIAL_NMIN.copy(__NAME__)
WAVE_CCF_SMART_MASK_TRIAL_NMIN.value = 9000

# define a trial maximum FP N value (should be higher than true
#     maximum FP N value)
WAVE_CCF_SMART_MASK_TRIAL_NMAX = WAVE_CCF_SMART_MASK_TRIAL_NMAX.copy(__NAME__)
WAVE_CCF_SMART_MASK_TRIAL_NMAX.value = 27000

# define the converges parameter for dwave in smart mask generation
WAVE_CCF_SMART_MASK_DWAVE_THRES = WAVE_CCF_SMART_MASK_DWAVE_THRES.copy(__NAME__)
WAVE_CCF_SMART_MASK_DWAVE_THRES.value = 1.0e-9

# define the quality control threshold from RV of CCF FP between reference
#    fiber and other fibers, above this limit fails QC [m/s]
#  For HE there is an offset between A and B - this will be a high value
# TODO: We should really think about this a bit more
WAVE_CCF_RV_THRES_QC = WAVE_CCF_RV_THRES_QC.copy(__NAME__)
# TODO: address this later - should be much lower
WAVE_CCF_RV_THRES_QC.value = 50000.0    # 0.5 (spirou value)
WAVE_CCF_RV_THRES_QC.author = base.AUTHORS['EA']

# TODO: Sort out wave constants below here
# =============================================================================
# CALIBRATION: WAVE GENERAL SETTINGS
# =============================================================================
# Define the line list file (located in the DRS_WAVE_DATA directory)
WAVE_LINELIST_FILE = WAVE_LINELIST_FILE.copy(__NAME__)
WAVE_LINELIST_FILE.value = 'catalogue_UNe_update230322.csv'  # 'catalogue_UNe.dat'
WAVE_LINELIST_FILE.author = base.AUTHORS['EA']

# Define the line list file format (must be astropy.table format)
WAVE_LINELIST_FMT = WAVE_LINELIST_FMT.copy(__NAME__)
WAVE_LINELIST_FMT.value = 'ascii.csv'   # 'ascii.tab'

# Define the line list file column names (must be separated by commas
#   and must be equal to the number of columns in file)
WAVE_LINELIST_COLS = WAVE_LINELIST_COLS.copy(__NAME__)
WAVE_LINELIST_COLS.value = 'll, amp, kind'

# Define the line list file row the data starts
WAVE_LINELIST_START = WAVE_LINELIST_START.copy(__NAME__)
WAVE_LINELIST_START.value = 1     # 0

# Define the line list file wavelength column and amplitude column
#    Must be in WAVE_LINELIST_COLS
WAVE_LINELIST_WAVECOL = WAVE_LINELIST_WAVECOL.copy(__NAME__)
WAVE_LINELIST_WAVECOL.value = 'll'
WAVE_LINELIST_AMPCOL = WAVE_LINELIST_AMPCOL.copy(__NAME__)
WAVE_LINELIST_AMPCOL.value = 'amp'

# define whether to always extract HC/FP files in the wave code (even if they
#    have already been extracted
WAVE_ALWAYS_EXTRACT = WAVE_ALWAYS_EXTRACT.copy(__NAME__)
WAVE_ALWAYS_EXTRACT.value = False

# define the type of file to use for wave solution (currently allowed are
#    'E2DS' or 'E2DSFF'
WAVE_EXTRACT_TYPE = WAVE_EXTRACT_TYPE.copy(__NAME__)
WAVE_EXTRACT_TYPE.value = 'E2DSFF'

# define the fit degree for the wavelength solution
WAVE_FIT_DEGREE = WAVE_FIT_DEGREE.copy(__NAME__)
WAVE_FIT_DEGREE.value = 5

# Define intercept and slope for a pixel shift
WAVE_PIXEL_SHIFT_INTER = WAVE_PIXEL_SHIFT_INTER.copy(__NAME__)
WAVE_PIXEL_SHIFT_INTER.value = 0.0  # 6.26637214e+00

WAVE_PIXEL_SHIFT_SLOPE = WAVE_PIXEL_SHIFT_SLOPE.copy(__NAME__)
WAVE_PIXEL_SHIFT_SLOPE.value = 0.0  # 4.22131253e-04

#  Defines echelle number of first extracted order
WAVE_T_ORDER_START = WAVE_T_ORDER_START.copy(__NAME__)
WAVE_T_ORDER_START.value = 147

#  Defines order from which the solution is calculated (first order)
WAVE_N_ORD_START = WAVE_N_ORD_START.copy(__NAME__)
WAVE_N_ORD_START.value = 0

#  Defines order to which the solution is calculated (last order)
WAVE_N_ORD_FINAL = WAVE_N_ORD_FINAL.copy(__NAME__)
WAVE_N_ORD_FINAL.value = 75

# =============================================================================
# CALIBRATION: WAVE HC SETTINGS
# =============================================================================
# Define the mode to calculate the hc wave solution
#   Should be one of the following:
#       0 - Etienne method
WAVE_MODE_HC = WAVE_MODE_HC.copy(__NAME__)
WAVE_MODE_HC.value = 0

# width of the box for fitting HC lines. Lines will be fitted from -W to +W,
#     so a 2*W+1 window
WAVE_HC_FITBOX_SIZE = WAVE_HC_FITBOX_SIZE.copy(__NAME__)
WAVE_HC_FITBOX_SIZE.value = 6

# number of sigma above local RMS for a line to be flagged as such
WAVE_HC_FITBOX_SIGMA = WAVE_HC_FITBOX_SIGMA.copy(__NAME__)
WAVE_HC_FITBOX_SIGMA.value = 2.0

# the fit degree for the wave hc gaussian peaks fit
WAVE_HC_FITBOX_GFIT_DEG = WAVE_HC_FITBOX_GFIT_DEG.copy(__NAME__)
WAVE_HC_FITBOX_GFIT_DEG.value = 5

# the RMS of line-fitted line must be between DEVMIN and DEVMAX of the peak
#     value must be SNR>5 (or 1/SNR<0.2)
WAVE_HC_FITBOX_RMS_DEVMIN = WAVE_HC_FITBOX_RMS_DEVMIN.copy(__NAME__)
WAVE_HC_FITBOX_RMS_DEVMIN.value = 0.0
WAVE_HC_FITBOX_RMS_DEVMAX = WAVE_HC_FITBOX_RMS_DEVMAX.copy(__NAME__)
WAVE_HC_FITBOX_RMS_DEVMAX.value = 0.2

# the e-width of the line expressed in pixels.
WAVE_HC_FITBOX_EWMIN = WAVE_HC_FITBOX_EWMIN.copy(__NAME__)
WAVE_HC_FITBOX_EWMIN.value = 1.0    # 0.7
WAVE_HC_FITBOX_EWMAX = WAVE_HC_FITBOX_EWMAX.copy(__NAME__)
WAVE_HC_FITBOX_EWMAX.value = 3.0   # 1.1

# define the file type for saving the initial guess at the hc peak list
WAVE_HCLL_FILE_FMT = WAVE_HCLL_FILE_FMT.copy(__NAME__)
WAVE_HCLL_FILE_FMT.value = 'ascii.rst'

# number of bright lines kept per order
#     avoid >25 as it takes super long
#     avoid <12 as some orders are ill-defined and we need >10 valid
#         lines anyway
#     20 is a good number, and I see no reason to change it
WAVE_HC_NMAX_BRIGHT = WAVE_HC_NMAX_BRIGHT.copy(__NAME__)
WAVE_HC_NMAX_BRIGHT.value = 20

# Number of times to run the fit triplet algorithm
WAVE_HC_NITER_FIT_TRIPLET = WAVE_HC_NITER_FIT_TRIPLET.copy(__NAME__)
WAVE_HC_NITER_FIT_TRIPLET.value = 3

# Maximum distance between catalog line and init guess line to accept
#     line in m/s
WAVE_HC_MAX_DV_CAT_GUESS = WAVE_HC_MAX_DV_CAT_GUESS.copy(__NAME__)
WAVE_HC_MAX_DV_CAT_GUESS.value = 60000

# The fit degree between triplets
WAVE_HC_TFIT_DEG = WAVE_HC_TFIT_DEG.copy(__NAME__)
WAVE_HC_TFIT_DEG.value = 2

# Cut threshold for the triplet line fit [in km/s]
WAVE_HC_TFIT_CUT_THRES = WAVE_HC_TFIT_CUT_THRES.copy(__NAME__)
WAVE_HC_TFIT_CUT_THRES.value = 1.0

# Minimum number of lines required per order
WAVE_HC_TFIT_MINNUM_LINES = WAVE_HC_TFIT_MINNUM_LINES.copy(__NAME__)
WAVE_HC_TFIT_MINNUM_LINES.value = 10

# Minimum total number of lines required
WAVE_HC_TFIT_MINTOT_LINES = WAVE_HC_TFIT_MINTOT_LINES.copy(__NAME__)
WAVE_HC_TFIT_MINTOT_LINES.value = 200

# this sets the order of the polynomial used to ensure continuity
#     in the  xpix vs wave solutions by setting the first term = 12,
#     we force that the zeroth element of the xpix of the wavelegnth
#     grid is fitted with a 12th order polynomial as a function of
#     order number (format = string list separated by commas)
# these values are too high and lead to stability problems in the fit
# WAVE_HC_TFIT_ORDER_FIT_CONT.value = '12, 9, 6, 2, 2'

WAVE_HC_TFIT_ORDER_FIT_CONT = WAVE_HC_TFIT_ORDER_FIT_CONT.copy(__NAME__)
WAVE_HC_TFIT_ORDER_FIT_CONT.value = '12, 8, 4, 1, 1, 1'


# Number of times to loop through the sigma clip for triplet fit
WAVE_HC_TFIT_SIGCLIP_NUM = WAVE_HC_TFIT_SIGCLIP_NUM.copy(__NAME__)
WAVE_HC_TFIT_SIGCLIP_NUM.value = 20

# Sigma clip threshold for triplet fit
WAVE_HC_TFIT_SIGCLIP_THRES = WAVE_HC_TFIT_SIGCLIP_THRES.copy(__NAME__)
WAVE_HC_TFIT_SIGCLIP_THRES.value = 3.5

# Define the distance in m/s away from the center of dv hist points
#     outside will be rejected [m/s]
WAVE_HC_TFIT_DVCUT_ORDER = WAVE_HC_TFIT_DVCUT_ORDER.copy(__NAME__)
WAVE_HC_TFIT_DVCUT_ORDER.value = 2000
WAVE_HC_TFIT_DVCUT_ALL = WAVE_HC_TFIT_DVCUT_ALL.copy(__NAME__)
WAVE_HC_TFIT_DVCUT_ALL.value = 5000

# Define the resolution and line profile map size (y-axis by x-axis)
WAVE_HC_RESMAP_SIZE = WAVE_HC_RESMAP_SIZE.copy(__NAME__)
WAVE_HC_RESMAP_SIZE.value = '5, 4'

# Define the maximum allowed deviation in the RMS line spread function
WAVE_HC_RES_MAXDEV_THRES = WAVE_HC_RES_MAXDEV_THRES.copy(__NAME__)
WAVE_HC_RES_MAXDEV_THRES.value = 8

# quality control criteria if sigma greater than this many sigma fails
WAVE_HC_QC_SIGMA_MAX = WAVE_HC_QC_SIGMA_MAX.copy(__NAME__)
WAVE_HC_QC_SIGMA_MAX.value = 8

# Defines the dv span for PLOT_WAVE_HC_RESMAP debug plot, should be a
#    string list containing a min and max dv value
WAVE_HC_RESMAP_DV_SPAN = WAVE_HC_RESMAP_DV_SPAN.copy(__NAME__)
WAVE_HC_RESMAP_DV_SPAN.value = '-15, 15'

# Defines the x limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
#   string list containing a min and max x value
WAVE_HC_RESMAP_XLIM = WAVE_HC_RESMAP_XLIM.copy(__NAME__)
WAVE_HC_RESMAP_XLIM.value = '-8.0, 8.0'

# Defines the y limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
#   string list containing a min and max y value
WAVE_HC_RESMAP_YLIM = WAVE_HC_RESMAP_YLIM.copy(__NAME__)
WAVE_HC_RESMAP_YLIM.value = '-0.05, 0.7'

# Define whether to fit line profiles with "gaussian" or "super-gaussian"
WAVE_HC_RESMAP_FITTYPE = WAVE_HC_RESMAP_FITTYPE.copy(__NAME__)
WAVE_HC_RESMAP_FITTYPE.value = 'super-gaussian'

# Define the sigma clip for line profiles for the resolution map
WAVE_HC_RESMAP_SIGCLIP = WAVE_HC_RESMAP_SIGCLIP.copy(__NAME__)
WAVE_HC_RESMAP_SIGCLIP.value = 0.2

# Define the minimum instrumental error
WAVE_FP_ERRX_MIN = WAVE_FP_ERRX_MIN.copy(__NAME__)
WAVE_FP_ERRX_MIN.value = 0.01  # 0.03

#  Define the wavelength fit polynomial order
WAVE_FP_LL_DEGR_FIT = WAVE_FP_LL_DEGR_FIT.copy(__NAME__)
WAVE_FP_LL_DEGR_FIT.value = 4  # 5   #4  # 4

#  Define the max rms for the wavelength sigma-clip fit
WAVE_FP_MAX_LLFIT_RMS = WAVE_FP_MAX_LLFIT_RMS.copy(__NAME__)
WAVE_FP_MAX_LLFIT_RMS.value = 3.0

#  Define the weight threshold (small number) below which we do not keep fp
#     lines
WAVE_FP_WEIGHT_THRES = WAVE_FP_WEIGHT_THRES.copy(__NAME__)
WAVE_FP_WEIGHT_THRES.value = 1.0e-30

# Minimum blaze threshold to keep FP peaks
WAVE_FP_BLAZE_THRES = WAVE_FP_BLAZE_THRES.copy(__NAME__)
WAVE_FP_BLAZE_THRES.value = 0.3

# Minimum FP peaks pixel separation fraction diff. from median
WAVE_FP_XDIF_MIN = WAVE_FP_XDIF_MIN.copy(__NAME__)
WAVE_FP_XDIF_MIN.value = 0.75

# Maximum FP peaks pixel separation fraction diff. from median
WAVE_FP_XDIF_MAX = WAVE_FP_XDIF_MAX.copy(__NAME__)
WAVE_FP_XDIF_MAX.value = 1.25

# Maximum fractional wavelength offset between cross-matched FP peaks
WAVE_FP_LL_OFFSET = WAVE_FP_LL_OFFSET.copy(__NAME__)
WAVE_FP_LL_OFFSET.value = 0.25

# Maximum DV to keep HC lines in combined (WAVE_NEW) solution
WAVE_FP_DV_MAX = WAVE_FP_DV_MAX.copy(__NAME__)
WAVE_FP_DV_MAX.value = 0.25

# Decide whether to refit the cavity width (will update if files do not
#   exist)
WAVE_FP_UPDATE_CAVITY = WAVE_FP_UPDATE_CAVITY.copy(__NAME__)
WAVE_FP_UPDATE_CAVITY.value = True

# Select the FP cavity fitting (WAVE_MODE_FP = 1 only)
#   Should be one of the following:
#       0 - derive using the 1/m vs d fit from HC lines
#       1 - derive using the ll vs d fit from HC lines
WAVE_FP_CAVFIT_MODE = WAVE_FP_CAVFIT_MODE.copy(__NAME__)
WAVE_FP_CAVFIT_MODE.value = 1

# Select the FP wavelength fitting (WAVE_MODE_FP = 1 only)
#   Should be one of the following:
#       0 - use fit_1d_solution function
#       1 - fit with sigma-clipping and mod 1 pixel correction
WAVE_FP_LLFIT_MODE = WAVE_FP_LLFIT_MODE.copy(__NAME__)
WAVE_FP_LLFIT_MODE.value = 1

# Minimum FP peaks wavelength separation fraction diff. from median
WAVE_FP_LLDIF_MIN = WAVE_FP_LLDIF_MIN.copy(__NAME__)
WAVE_FP_LLDIF_MIN.value = 0.75

# Maximum FP peaks wavelength separation fraction diff. from median
WAVE_FP_LLDIF_MAX = WAVE_FP_LLDIF_MAX.copy(__NAME__)
WAVE_FP_LLDIF_MAX.value = 1.25

# Sigma-clip value for sigclip_polyfit
WAVE_FP_SIGCLIP = WAVE_FP_SIGCLIP.copy(__NAME__)
WAVE_FP_SIGCLIP.value = 7

# First order for multi-order wave fp plot
WAVE_FP_PLOT_MULTI_INIT = WAVE_FP_PLOT_MULTI_INIT.copy(__NAME__)
WAVE_FP_PLOT_MULTI_INIT.value = 20

# Number of orders in multi-order wave fp plot
WAVE_FP_PLOT_MULTI_NBO = WAVE_FP_PLOT_MULTI_NBO.copy(__NAME__)
WAVE_FP_PLOT_MULTI_NBO.value = 5

# define the dprtype for generating FPLINES (string list)
WAVE_FP_DPRLIST = WAVE_FP_DPRLIST.copy(__NAME__)
WAVE_FP_DPRLIST.value = 'OBJ_FP'

# define the override for reference fiber for generating FPLINES
#    None for no override
WAVE_FP_FIBERTYPES = WAVE_FP_FIBERTYPES.copy(__NAME__)
WAVE_FP_FIBERTYPES.value = 'None'

# =============================================================================
# CALIBRATION: WAVE LITTROW SETTINGS
# =============================================================================
#  Define the order to start the Littrow fit from for the HC wave solution
WAVE_LITTROW_ORDER_INIT_1 = WAVE_LITTROW_ORDER_INIT_1.copy(__NAME__)
WAVE_LITTROW_ORDER_INIT_1.value = 0

#  Define the order to start the Littrow fit from for the FP wave solution
# TODO: Note currently used
WAVE_LITTROW_ORDER_INIT_2 = WAVE_LITTROW_ORDER_INIT_2.copy(__NAME__)
WAVE_LITTROW_ORDER_INIT_2.value = 0

#  Define the order to end the Littrow fit at for the HC wave solution
WAVE_LITTROW_ORDER_FINAL_1 = WAVE_LITTROW_ORDER_FINAL_1.copy(__NAME__)
WAVE_LITTROW_ORDER_FINAL_1.value = 75

#  Define the order to end the Littrow fit at for the FP wave solution
# TODO: Note currently used
WAVE_LITTROW_ORDER_FINAL_2 = WAVE_LITTROW_ORDER_FINAL_2.copy(__NAME__)
WAVE_LITTROW_ORDER_FINAL_2.value = 75

#  Define orders to ignore in Littrow fit (should be a string list separated
#      by commas
WAVE_LITTROW_REMOVE_ORDERS = WAVE_LITTROW_REMOVE_ORDERS.copy(__NAME__)
WAVE_LITTROW_REMOVE_ORDERS.value = ''

#  Define the littrow cut steps for the HC wave solution
WAVE_LITTROW_CUT_STEP_1 = WAVE_LITTROW_CUT_STEP_1.copy(__NAME__)
WAVE_LITTROW_CUT_STEP_1.value = 250

#  Define the littrow cut steps for the FP wave solution
WAVE_LITTROW_CUT_STEP_2 = WAVE_LITTROW_CUT_STEP_2.copy(__NAME__)
WAVE_LITTROW_CUT_STEP_2.value = 500

#  Define the fit polynomial order for the Littrow fit (fit across the orders)
#    for the HC wave solution
WAVE_LITTROW_FIG_DEG_1 = WAVE_LITTROW_FIG_DEG_1.copy(__NAME__)
WAVE_LITTROW_FIG_DEG_1.value = 8  # 5  # 4

#  Define the fit polynomial order for the Littrow fit (fit across the orders)
#    for the FP wave solution
WAVE_LITTROW_FIG_DEG_2 = WAVE_LITTROW_FIG_DEG_2.copy(__NAME__)
WAVE_LITTROW_FIG_DEG_2.value = 8  # 4

#  Define the order fit for the Littrow solution (fit along the orders)
# TODO needs to be the same as ic_ll_degr_fit
WAVE_LITTROW_EXT_ORDER_FIT_DEG = WAVE_LITTROW_EXT_ORDER_FIT_DEG.copy(__NAME__)
WAVE_LITTROW_EXT_ORDER_FIT_DEG.value = 4  # 5  # 4

#   Maximum littrow RMS value
WAVE_LITTROW_QC_RMS_MAX = WAVE_LITTROW_QC_RMS_MAX.copy(__NAME__)
WAVE_LITTROW_QC_RMS_MAX.value = 0.3

#   Maximum littrow Deviation from wave solution (at x cut points)
WAVE_LITTROW_QC_DEV_MAX = WAVE_LITTROW_QC_DEV_MAX.copy(__NAME__)
WAVE_LITTROW_QC_DEV_MAX.value = 0.9

# =============================================================================
# CALIBRATION: WAVE FP SETTINGS
# =============================================================================
# Define the mode to calculate the fp+hc wave solution
#   Should be one of the following:
#       0 - following Bauer et al 15 (previously WAVE_E2DS_EA)
#       1 - following C Lovis (previously WAVE_NEW)
WAVE_MODE_FP = WAVE_MODE_FP.copy(__NAME__)
WAVE_MODE_FP.value = 1

# Define the initial value of FP effective cavity width 2xd in nm
#   2xd = 24.5 mm = 24.5e6 nm  for SPIRou
WAVE_FP_DOPD0 = WAVE_FP_DOPD0.copy(__NAME__)
# TODO: For NIRPS d = 12mm not 12.25 --> 2.4e7
WAVE_FP_DOPD0.value = 2.4e7

#  Define the polynomial fit degree between FP line numbers and the
#      measured cavity width for each line
WAVE_FP_CAVFIT_DEG = WAVE_FP_CAVFIT_DEG.copy(__NAME__)
WAVE_FP_CAVFIT_DEG.value = 9

#  Define the FP jump size that is too large
WAVE_FP_LARGE_JUMP = WAVE_FP_LARGE_JUMP.copy(__NAME__)
WAVE_FP_LARGE_JUMP.value = 250

# index of FP line to start order cross-matching from
WAVE_FP_CM_IND = WAVE_FP_CM_IND.copy(__NAME__)
WAVE_FP_CM_IND.value = -2

# define the percentile to normalize the spectrum to (per order)
#  used to determine FP peaks (peaks must be above a normalised limit
#   defined in WAVE_FP_PEAK_LIM
WAVE_FP_NORM_PERCENTILE = WAVE_FP_NORM_PERCENTILE.copy(__NAME__)
WAVE_FP_NORM_PERCENTILE.value = 95

# define the normalised limit below which FP peaks are not used
WAVE_FP_PEAK_LIM = WAVE_FP_PEAK_LIM.copy(__NAME__)
WAVE_FP_PEAK_LIM.value = 0.1

#    Define peak to peak width that is too large (removed from FP peaks)
WAVE_FP_P2P_WIDTH_CUT = WAVE_FP_P2P_WIDTH_CUT.copy(__NAME__)
WAVE_FP_P2P_WIDTH_CUT.value = 30

# =============================================================================
# CALIBRATION: WAVE NIGHT SETTINGS
# =============================================================================
# number of iterations for hc convergence
WAVE_NIGHT_NITERATIONS1 = WAVE_NIGHT_NITERATIONS1.copy(__NAME__)
WAVE_NIGHT_NITERATIONS1.value = 4

# number of iterations for fp convergence
WAVE_NIGHT_NITERATIONS2 = WAVE_NIGHT_NITERATIONS2.copy(__NAME__)
WAVE_NIGHT_NITERATIONS2.value = 3

# starting points for the cavity corrections
WAVE_NIGHT_DCAVITY = WAVE_NIGHT_DCAVITY.copy(__NAME__)
WAVE_NIGHT_DCAVITY.value = 0

# define the sigma clip value to remove bad hc lines
WAVE_NIGHT_HC_SIGCLIP = WAVE_NIGHT_HC_SIGCLIP.copy(__NAME__)
WAVE_NIGHT_HC_SIGCLIP.value = 50

# median absolute deviation cut off
WAVE_NIGHT_MED_ABS_DEV = WAVE_NIGHT_MED_ABS_DEV.copy(__NAME__)
WAVE_NIGHT_MED_ABS_DEV.value = 5

# sigma clipping for the fit
WAVE_NIGHT_NSIG_FIT_CUT = WAVE_NIGHT_NSIG_FIT_CUT.copy(__NAME__)
WAVE_NIGHT_NSIG_FIT_CUT.value = 7

# wave night plot hist number of bins
WAVENIGHT_PLT_NBINS = WAVENIGHT_PLT_NBINS.copy(__NAME__)
WAVENIGHT_PLT_NBINS.value = 51

# wave night plot hc bin lower bound in multiples of rms
WAVENIGHT_PLT_BINL = WAVENIGHT_PLT_BINL.copy(__NAME__)
WAVENIGHT_PLT_BINL.value = -20

# wave night plot hc bin upper bound in multiples of rms
WAVENIGHT_PLT_BINU = WAVENIGHT_PLT_BINU.copy(__NAME__)
WAVENIGHT_PLT_BINU.value = 20

# =============================================================================
# OBJECT: SKY CORR SETTINGS
# =============================================================================
# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input sky files
SKYMODEL_FILETYPE = SKYMODEL_FILETYPE.copy(__NAME__)
SKYMODEL_FILETYPE.value = 'EXT_E2DS_FF'
SKYMODEL_FILETYPE.author = base.AUTHORS['NJC']

# Define the order to get the snr from (for input data qc check)
SKYMODEL_EXT_SNR_ORDERNUM =  SKYMODEL_EXT_SNR_ORDERNUM.copy(__NAME__)
SKYMODEL_EXT_SNR_ORDERNUM.value = 59
SKYMODEL_EXT_SNR_ORDERNUM.author = base.AUTHORS['EA']

# Define the minimum exptime to use a sky in the model [s]
SKYMODEL_MIN_EXPTIME =  SKYMODEL_MIN_EXPTIME.copy(__NAME__)
SKYMODEL_MIN_EXPTIME.value = 300
SKYMODEL_MIN_EXPTIME.author = base.AUTHORS['EA']

# Define the maximum number of files to have open simultaneously
SKYMODEL_MAX_OPEN_FILES = SKYMODEL_MAX_OPEN_FILES.copy(__NAME__)
SKYMODEL_MAX_OPEN_FILES.value = 10

# define the sigma that positive exursions need to have to be identified
#   as lines
SKYMODEL_LINE_SIGMA = SKYMODEL_LINE_SIGMA.copy(__NAME__)
SKYMODEL_LINE_SIGMA.value = 5
SKYMODEL_LINE_SIGMA.author = base.AUTHORS['EA']

# define the erosion size to use on a line
SKYMODEL_LINE_ERODE_SIZE = SKYMODEL_LINE_ERODE_SIZE.copy(__NAME__)
SKYMODEL_LINE_ERODE_SIZE.value = 5
SKYMODEL_LINE_ERODE_SIZE.author = base.AUTHORS['EA']

# define the dilatation size to use on a line
SKYMODEL_LINE_DILATE_SIZE = SKYMODEL_LINE_DILATE_SIZE.copy(__NAME__)
SKYMODEL_LINE_DILATE_SIZE.value = 27
SKYMODEL_LINE_DILATE_SIZE.author = base.AUTHORS['EA']

# define the number of weight iterations to use when construct sky model
#       weight vector
SKYMODEL_WEIGHT_ITERS = SKYMODEL_WEIGHT_ITERS.copy(__NAME__)
SKYMODEL_WEIGHT_ITERS.value = 5
SKYMODEL_WEIGHT_ITERS.author = base.AUTHORS['EA']

# define the erosion size for the sky model line weight calculation
SKYMODEL_WEIGHT_ERODE_SIZE = SKYMODEL_WEIGHT_ERODE_SIZE.copy(__NAME__)
SKYMODEL_WEIGHT_ERODE_SIZE.value = 3
SKYMODEL_WEIGHT_ERODE_SIZE.author = base.AUTHORS['EA']

# Define the allowed DPRTYPEs for sky correction
ALLOWED_SKYCORR_DPRTYPES = ALLOWED_SKYCORR_DPRTYPES.copy(__NAME__)
ALLOWED_SKYCORR_DPRTYPES.value = 'OBJ_SKY, TELLU_SKY, FLUXSTD_SKY'
ALLOWED_SKYCORR_DPRTYPES.author = base.AUTHORS['NJC']

# Define the number of iterations used to create sky correction weights
SKYCORR_WEIGHT_ITERATIONS = SKYCORR_WEIGHT_ITERATIONS.copy(__NAME__)
SKYCORR_WEIGHT_ITERATIONS.value = 5
SKYCORR_WEIGHT_ITERATIONS.author = base.AUTHORS['EA']

# Define the size of the fine low pass filter (must be an odd integer)
SKYCORR_LOWPASS_SIZE1 = SKYCORR_LOWPASS_SIZE1.copy(__NAME__)
SKYCORR_LOWPASS_SIZE1.value = 51
SKYCORR_LOWPASS_SIZE1.author = base.AUTHORS['EA']

# Define the size of the coarse low pass filter (msut be an odd integer)
SKYCORR_LOWPASS_SIZE2 = SKYCORR_LOWPASS_SIZE2.copy(__NAME__)
SKYCORR_LOWPASS_SIZE2.value = 101
SKYCORR_LOWPASS_SIZE2.author = base.AUTHORS['EA']

# Define the number of iterations to use for the coarse low pass filter
SKYCORR_LOWPASS_ITERATIONS = SKYCORR_LOWPASS_ITERATIONS.copy(__NAME__)
SKYCORR_LOWPASS_ITERATIONS.value = 2
SKYCORR_LOWPASS_ITERATIONS.author = base.AUTHORS['EA']

# Define the number of sigma threshold for sky corr sigma clipping
SKYCORR_NSIG_THRES = SKYCORR_NSIG_THRES.copy(__NAME__)
SKYCORR_NSIG_THRES.value = 5
SKYCORR_NSIG_THRES.author = base.AUTHORS['EA']

# =============================================================================
# OBJECT: TELLURIC SETTINGS
# =============================================================================
# Define the name of the tapas file used
TAPAS_FILE = TAPAS_FILE.copy(__NAME__)
TAPAS_FILE.value = 'tapas_all_sp.fits.gz'

# Define the format (astropy format) of the tapas file "TAPAS_FILE"
TAPAS_FILE_FMT = TAPAS_FILE_FMT.copy(__NAME__)
TAPAS_FILE_FMT.value = 'fits'

# The allowed input DPRTYPES for input telluric files
TELLU_ALLOWED_DPRTYPES = TELLU_ALLOWED_DPRTYPES.copy(__NAME__)
TELLU_ALLOWED_DPRTYPES.value = 'OBJ_DARK, OBJ_FP, OBJ_SKY, TELLU_SKY, FLUXSTD_SKY'

# the INPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input telluric files
TELLURIC_FILETYPE = TELLURIC_FILETYPE.copy(__NAME__)
TELLURIC_FILETYPE.value = 'EXT_E2DS_FF'

# the fiber required for input template files
TELLURIC_FIBER_TYPE = TELLURIC_FIBER_TYPE.copy(__NAME__)
TELLURIC_FIBER_TYPE.value = 'A'

# Define level above which the blaze is high enough to accurately
#    measure telluric
TELLU_CUT_BLAZE_NORM = TELLU_CUT_BLAZE_NORM.copy(__NAME__)
TELLU_CUT_BLAZE_NORM.value = 0.2

# Define telluric include/exclude list directory
TELLU_LIST_DIRECTORY = TELLU_LIST_DIRECTORY.copy(__NAME__)
TELLU_LIST_DIRECTORY.value = 'telluric/'

# Define telluric white list name
TELLU_WHITELIST_NAME = TELLU_WHITELIST_NAME.copy(__NAME__)
TELLU_WHITELIST_NAME.value = 'tellu_whitelist.txt'

# Define telluric black list name
TELLU_BLACKLIST_NAME = TELLU_BLACKLIST_NAME.copy(__NAME__)
TELLU_BLACKLIST_NAME.value = 'tellu_blacklist.txt'

# Force only pre-cleaning (not recommended - only for debugging)
TELLU_ONLY_PRECLEAN = TELLU_ONLY_PRECLEAN.copy(__NAME__)
TELLU_ONLY_PRECLEAN.value = False

# =============================================================================
# OBJECT: TELLURIC PRE-CLEANING SETTINGS
# =============================================================================
# define whether we do pre-cleaning
TELLUP_DO_PRECLEANING = TELLUP_DO_PRECLEANING.copy(__NAME__)
TELLUP_DO_PRECLEANING.value = True

# define whether we do finite resolution correct (if we have a template)
TELLUP_DO_FINITE_RES_CORR = TELLUP_DO_FINITE_RES_CORR.copy(__NAME__)
TELLUP_DO_FINITE_RES_CORR.value = True

# width in km/s for the ccf scan to determine the abso in pre-cleaning
TELLUP_CCF_SCAN_RANGE = TELLUP_CCF_SCAN_RANGE.copy(__NAME__)
TELLUP_CCF_SCAN_RANGE.value = 25

# TODO: Turn on OH line cleaning
TELLUP_CLEAN_OH_LINES = TELLUP_CLEAN_OH_LINES.copy(__NAME__)
TELLUP_CLEAN_OH_LINES.value = False

# Define the number of bright OH lines that will be individually adjusted
#     in amplitude. Done only on lines that are at an SNR > 1
TELLUP_OHLINE_NBRIGHT = TELLUP_OHLINE_NBRIGHT.copy(__NAME__)
TELLUP_OHLINE_NBRIGHT.value = 300

# define the OH line pca file
TELLUP_OHLINE_PCA_FILE = TELLUP_OHLINE_PCA_FILE.copy(__NAME__)
TELLUP_OHLINE_PCA_FILE.value = 'sky_PCs.fits'

# define the orders not to use in pre-cleaning fit (due to thermal
# background)
TELLUP_REMOVE_ORDS = TELLUP_REMOVE_ORDS.copy(__NAME__)
TELLUP_REMOVE_ORDS.value = '47, 48'

# define the minimum snr to accept orders for pre-cleaning fit
TELLUP_SNR_MIN_THRES = TELLUP_SNR_MIN_THRES.copy(__NAME__)
TELLUP_SNR_MIN_THRES.value = 3.0

# define the telluric trans other abso CCF file
TELLUP_OTHERS_CCF_FILE = TELLUP_OTHERS_CCF_FILE.copy(__NAME__)
TELLUP_OTHERS_CCF_FILE.value = 'trans_others_abso_ccf.mas'

# define the telluric trans water abso CCF file
TELLUP_H2O_CCF_FILE = TELLUP_H2O_CCF_FILE.copy(__NAME__)
TELLUP_H2O_CCF_FILE.value = 'trans_h2o_abso_ccf.mas'

# define dexpo convergence threshold
TELLUP_DEXPO_CONV_THRES = TELLUP_DEXPO_CONV_THRES.copy(__NAME__)
TELLUP_DEXPO_CONV_THRES.value = 1.0e-4

# define the maximum number of iterations to try to get dexpo
# convergence
TELLUP_DEXPO_MAX_ITR = TELLUP_DEXPO_MAX_ITR.copy(__NAME__)
TELLUP_DEXPO_MAX_ITR.value = 40

# define the kernel threshold in abso_expo
TELLUP_ABSO_EXPO_KTHRES = TELLUP_ABSO_EXPO_KTHRES.copy(__NAME__)
TELLUP_ABSO_EXPO_KTHRES.value = 1.0e-6

# define the gaussian width of the kernel used in abso_expo
TELLUP_ABSO_EXPO_KWID = TELLUP_ABSO_EXPO_KWID.copy(__NAME__)
TELLUP_ABSO_EXPO_KWID.value = 4.5

# define the gaussian exponent of the kernel used in abso_expo
#   a value of 2 is gaussian, a value >2 is boxy
TELLUP_ABSO_EXPO_KEXP = TELLUP_ABSO_EXPO_KEXP.copy(__NAME__)
TELLUP_ABSO_EXPO_KEXP.value = 2.20

# define the transmission threshold (in exponential form) for keeping
#   valid transmission
TELLUP_TRANS_THRES = TELLUP_TRANS_THRES.copy(__NAME__)
TELLUP_TRANS_THRES.value = -1

# define the threshold for discrepant transmission (in sigma)
TELLUP_TRANS_SIGLIM = TELLUP_TRANS_SIGLIM.copy(__NAME__)
TELLUP_TRANS_SIGLIM.value = 10

# define whether to force airmass fit to header airmass value
TELLUP_FORCE_AIRMASS = TELLUP_FORCE_AIRMASS.copy(__NAME__)
TELLUP_FORCE_AIRMASS.value = False

# set the typical water abso exponent. Compare to values in header for
#    high-snr targets later
TELLUP_D_WATER_ABSO = TELLUP_D_WATER_ABSO.copy(__NAME__)
TELLUP_D_WATER_ABSO.value = 8.0

# set the lower and upper bounds (String list) for the exponent of
#  the other species of absorbers
TELLUP_OTHER_BOUNDS = TELLUP_OTHER_BOUNDS.copy(__NAME__)
TELLUP_OTHER_BOUNDS.value = '0.8, 3.0'

# set the lower and upper bounds (string list) for the exponent of
#  water absorber
TELLUP_WATER_BOUNDS = TELLUP_WATER_BOUNDS.copy(__NAME__)
TELLUP_WATER_BOUNDS.value = '0.1, 15'

# set the plot order for the finite resolution plot (somewhere aroun 1.45 um)
TELLU_FINITE_RES_ORDER = TELLU_FINITE_RES_ORDER.copy(__NAME__)
TELLU_FINITE_RES_ORDER.value = 49
TELLU_FINITE_RES_ORDER.author = base.AUTHORS['NJC']

# =============================================================================
# OBJECT: MAKE TELLURIC SETTINGS
# =============================================================================
# value below which the blaze in considered too low to be useful
#     for all blaze profiles, we normalize to the 95th percentile.
#     That's pretty much the peak value, but it is resistent to
#     eventual outliers
MKTELLU_BLAZE_PERCENTILE = MKTELLU_BLAZE_PERCENTILE.copy(__NAME__)
MKTELLU_BLAZE_PERCENTILE.value = 95
MKTELLU_CUT_BLAZE_NORM = MKTELLU_CUT_BLAZE_NORM.copy(__NAME__)
MKTELLU_CUT_BLAZE_NORM.value = 0.1

# Define list of absorbers in the tapas fits table
TELLU_ABSORBERS = TELLU_ABSORBERS.copy(__NAME__)
TELLU_ABSORBERS.value = 'combined, h2o, o3, n2o, o2, co2, ch4'

# define the default convolution width [in pixels]
MKTELLU_DEFAULT_CONV_WIDTH = MKTELLU_DEFAULT_CONV_WIDTH.copy(__NAME__)
MKTELLU_DEFAULT_CONV_WIDTH.value = 100

# median-filter the template. we know that stellar features
#    are very broad. this avoids having spurious noise in our
#    templates [pixel]
MKTELLU_TEMP_MED_FILT = MKTELLU_TEMP_MED_FILT.copy(__NAME__)
MKTELLU_TEMP_MED_FILT.value = 15

# Define the orders to plot (not too many)
#    values should be a string list separated by commas
MKTELLU_PLOT_ORDER_NUMS = MKTELLU_PLOT_ORDER_NUMS.copy(__NAME__)
MKTELLU_PLOT_ORDER_NUMS.value = '19, 26, 35'

#   Define the order to use for SNR check when accepting tellu files
#      to the telluDB
MKTELLU_QC_SNR_ORDER = MKTELLU_QC_SNR_ORDER.copy(__NAME__)
MKTELLU_QC_SNR_ORDER.value = 33

# Defines the minimum allowed value for the recovered water vapor optical
#    depth (should not be able 1)
MKTELLU_TRANS_MIN_WATERCOL = MKTELLU_TRANS_MIN_WATERCOL.copy(__NAME__)
MKTELLU_TRANS_MIN_WATERCOL.value = 0.2

# Defines the maximum allowed value for the recovered water vapor optical
#    depth
MKTELLU_TRANS_MAX_WATERCOL = MKTELLU_TRANS_MAX_WATERCOL.copy(__NAME__)
MKTELLU_TRANS_MAX_WATERCOL.value = 99

# minimum transmission required for use of a given pixel in the TAPAS
#    and SED fitting
MKTELLU_THRES_TRANSFIT = MKTELLU_THRES_TRANSFIT.copy(__NAME__)
MKTELLU_THRES_TRANSFIT.value = 0.3

# Defines the bad pixels if the spectrum is larger than this value.
#    These values are likely an OH line or a cosmic ray
MKTELLU_TRANS_FIT_UPPER_BAD = MKTELLU_TRANS_FIT_UPPER_BAD.copy(__NAME__)
MKTELLU_TRANS_FIT_UPPER_BAD.value = 1.1

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
#      accepted to the telluDB
MKTELLU_QC_SNR_MIN = MKTELLU_QC_SNR_MIN.copy(__NAME__)
MKTELLU_QC_SNR_MIN.value = 100

# Define the allowed difference between recovered and input airmass
# TODO: Change QC once using tapas from La silla
MKTELLU_QC_AIRMASS_DIFF = MKTELLU_QC_AIRMASS_DIFF.copy(__NAME__)
MKTELLU_QC_AIRMASS_DIFF.value = 1.0

# define the sigma cut for tellu transmission model
TELLU_TRANS_MODEL_SIG = TELLU_TRANS_MODEL_SIG.copy(__NAME__)
TELLU_TRANS_MODEL_SIG.value = 5.0
TELLU_TRANS_MODEL_SIG.author = base.AUTHORS['EA']

# =============================================================================
# OBJECT: FIT TELLURIC SETTINGS
# =============================================================================
#   Define the order to use for SNR check when accepting tellu files
#      to the telluDB
FTELLU_QC_SNR_ORDER = FTELLU_QC_SNR_ORDER.copy(__NAME__)
FTELLU_QC_SNR_ORDER.value = 64

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
#      accepted to the telluDB
FTELLU_QC_SNR_MIN = MKTELLU_QC_SNR_MIN.copy(__NAME__)
FTELLU_QC_SNR_MIN.value = 3

# The number of principle components to use in PCA fit
FTELLU_NUM_PRINCIPLE_COMP = FTELLU_NUM_PRINCIPLE_COMP.copy(__NAME__)
FTELLU_NUM_PRINCIPLE_COMP.value = 5

# The number of transmission files to use in the PCA fit (use this number of
#    trans files closest in expo_H2O and expo_water
FTELLU_NUM_TRANS = FTELLU_NUM_TRANS.copy(__NAME__)
FTELLU_NUM_TRANS.value = 50

# Define whether to add the first derivative and broadening factor to the
#     principal components this allows a variable resolution and velocity
#     offset of the PCs this is performed in the pixel space and NOT the
#     velocity space as this is should be due to an instrument shift
FTELLU_ADD_DERIV_PC = FTELLU_ADD_DERIV_PC.copy(__NAME__)
FTELLU_ADD_DERIV_PC.value = True

# Define whether to fit the derivatives instead of the principal components
FTELLU_FIT_DERIV_PC = FTELLU_FIT_DERIV_PC.copy(__NAME__)
FTELLU_FIT_DERIV_PC.value = True

# The number of pixels required (per order) to be able to interpolate the
#    template on to a berv shifted wavelength grid
FTELLU_FIT_KEEP_NUM = FTELLU_FIT_KEEP_NUM.copy(__NAME__)
FTELLU_FIT_KEEP_NUM.value = 20

# The minimium transmission allowed to define good pixels (for reconstructed
#    absorption calculation)
FTELLU_FIT_MIN_TRANS = FTELLU_FIT_MIN_TRANS.copy(__NAME__)
FTELLU_FIT_MIN_TRANS.value = 0.2

# The minimum wavelength constraint (in nm) to calculate reconstructed
#     absorption
FTELLU_LAMBDA_MIN = FTELLU_LAMBDA_MIN.copy(__NAME__)
FTELLU_LAMBDA_MIN.value = 1000.0

# The maximum wavelength constraint (in nm) to calculate reconstructed
#     absorption
FTELLU_LAMBDA_MAX = FTELLU_LAMBDA_MAX.copy(__NAME__)
FTELLU_LAMBDA_MAX.value = 2100.0

# The gaussian kernel used to smooth the template and residual spectrum [km/s]
FTELLU_KERNEL_VSINI = FTELLU_KERNEL_VSINI.copy(__NAME__)
FTELLU_KERNEL_VSINI.value = 30.0

# The number of iterations to use in the reconstructed absorption calculation
FTELLU_FIT_ITERS = FTELLU_FIT_ITERS.copy(__NAME__)
FTELLU_FIT_ITERS.value = 4

# The minimum log absorption the is allowed in the molecular absorption
#     calculation
FTELLU_FIT_RECON_LIMIT = FTELLU_FIT_RECON_LIMIT.copy(__NAME__)
FTELLU_FIT_RECON_LIMIT.value = -0.5

# Define the orders to plot (not too many) for recon abso plot
#    values should be a string list separated by commas
FTELLU_PLOT_ORDER_NUMS = FTELLU_PLOT_ORDER_NUMS.copy(__NAME__)
FTELLU_PLOT_ORDER_NUMS.value = '19, 26, 35'

# Define the selected fit telluric order for debug plots (when not in loop)
FTELLU_SPLOT_ORDER = FTELLU_SPLOT_ORDER.copy(__NAME__)
FTELLU_SPLOT_ORDER.value = 30

# =============================================================================
# OBJECT: MAKE TEMPLATE SETTINGS
# =============================================================================
# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input template files
MKTEMPLATE_FILETYPE = MKTEMPLATE_FILETYPE.copy(__NAME__)
MKTEMPLATE_FILETYPE.value = 'TELLU_OBJ'

# the fiber required for input template files
MKTEMPLATE_FIBER_TYPE = MKTEMPLATE_FIBER_TYPE.copy(__NAME__)
MKTEMPLATE_FIBER_TYPE.value = 'A'

# the source of the input files (either "disk" or "telludb")
MKTEMPLATE_FILESOURCE = MKTEMPLATE_FILESOURCE.copy(__NAME__)
MKTEMPLATE_FILESOURCE.value = 'telludb'

# the order to use for signal to noise cut requirement
MKTEMPLATE_SNR_ORDER = MKTEMPLATE_SNR_ORDER.copy(__NAME__)
MKTEMPLATE_SNR_ORDER.value = 59

# The number of iterations to filter low frequency noise before medianing
#   the template "big cube" to the final template spectrum
MKTEMPLATE_E2DS_ITNUM = MKTEMPLATE_E2DS_ITNUM.copy(__NAME__)
MKTEMPLATE_E2DS_ITNUM.value = 5

# The size (in pixels) to filter low frequency noise before medianing
#   the template "big cube" to the final template spectrum
MKTEMPLATE_E2DS_LOWF_SIZE = MKTEMPLATE_E2DS_LOWF_SIZE.copy(__NAME__)
MKTEMPLATE_E2DS_LOWF_SIZE.value = 501

# The number of iterations to filter low frequency noise before medianing
#   the s1d template "big cube" to the final template spectrum
MKTEMPLATE_S1D_ITNUM = MKTEMPLATE_S1D_ITNUM.copy(__NAME__)
MKTEMPLATE_S1D_ITNUM.value = 5

# The size (in pixels) to filter low frequency noise before medianing
#   the s1d template "big cube" to the final template spectrum
MKTEMPLATE_S1D_LOWF_SIZE = MKTEMPLATE_S1D_LOWF_SIZE.copy(__NAME__)
MKTEMPLATE_S1D_LOWF_SIZE.value = 501

# Define the minimum allowed berv coverage to construct a template
#   in km/s  (default is double the resolution in km/s)
MKTEMPLATE_BERVCOR_QCMIN = MKTEMPLATE_BERVCOR_QCMIN.copy(__NAME__)
MKTEMPLATE_BERVCOR_QCMIN.value = 8.0

# Define the core SNR in order to calculate required BERV coverage
MKTEMPLATE_BERVCOV_CSNR = MKTEMPLATE_BERVCOV_CSNR.copy(__NAME__)
MKTEMPLATE_BERVCOV_CSNR.value = 100.0

# Defome the resolution in km/s for calculating BERV coverage
MKTEMPLATE_BERVCOV_RES = MKTEMPLATE_BERVCOV_RES.copy(__NAME__)
MKTEMPLATE_BERVCOV_RES.value = 4.0

# Define whether to run template making in debug mode (do not bin the
#   data when medianing)
MKTEMPLATE_DEBUG_MODE = MKTEMPLATE_DEBUG_MODE.copy(__NAME__)
MKTEMPLATE_DEBUG_MODE.value = False

# Define the max number of files to be allowed into a bin (if not in debug
#   mode)
MKTEMPLATE_MAX_OPEN_FILES = MKTEMPLATE_MAX_OPEN_FILES.copy(__NAME__)
MKTEMPLATE_MAX_OPEN_FILES.value = 50

# Define the fwhm of hot star convolution kernel size in km/s so it is half
#     the minimum v sin i of our hot stars
MKTEMPLATE_HOTSTAR_KER_VEL = MKTEMPLATE_HOTSTAR_KER_VEL.copy(__NAME__)
MKTEMPLATE_HOTSTAR_KER_VEL.value = 25

# Define the threshold for the Lucy-Richardson deconvolution steps. This is
#    the maximum  value of the 99th percentile of the feed-back term
MKTEMPLATE_DECONV_ITR_THRES = MKTEMPLATE_DECONV_ITR_THRES.copy(__NAME__)
MKTEMPLATE_DECONV_ITR_THRES.value = 1.0e-3
MKTEMPLATE_DECONV_ITR_THRES.author = base.AUTHORS['EA']

# Define the max number of iterations to run if the iteration threshold
#     is not met
MKTEMPLATE_DECONV_ITR_MAX = MKTEMPLATE_DECONV_ITR_MAX.copy(__NAME__)
MKTEMPLATE_DECONV_ITR_MAX.value = 100
MKTEMPLATE_DECONV_ITR_MAX.author = base.AUTHORS['EA']

# =============================================================================
# CALIBRATION: CCF SETTINGS
# =============================================================================
# Define the ccf mask path
CCF_MASK_PATH = CCF_MASK_PATH.copy(__NAME__)
CCF_MASK_PATH.value = 'ccf_masks/'
CCF_MASK_PATH.author = base.AUTHORS['NJC']

# Define the TEFF mask table for when CCF_DEFAULT_MASK is TEFF
CCF_TEFF_MASK_TABLE = CCF_TEFF_MASK_TABLE.copy(__NAME__)
CCF_TEFF_MASK_TABLE.value = 'teff_masks.csv'
CCF_TEFF_MASK_TABLE.datatype = 'csv'
CCF_TEFF_MASK_TABLE.author = base.AUTHORS['NJC']

# Define the default CCF MASK to use (filename or TEFF to decide based on
#    object temperature) - for TEFF setup see CCF_TEFF_MASK_TABLE file
CCF_DEFAULT_MASK = CCF_DEFAULT_MASK.copy(__NAME__)
CCF_DEFAULT_MASK.value = 'TEFF'
CCF_DEFAULT_MASK.author = base.AUTHORS['NJC']

# Define the default CCF MASK normalisation mode
#   options are:
#     'None'         for no normalization
#     'all'          for normalization across all orders
#     'order'        for normalization for each order
CCF_MASK_NORMALIZATION = CCF_MASK_NORMALIZATION.copy(__NAME__)
CCF_MASK_NORMALIZATION.value = 'order'

# Define the wavelength units for the mask
CCF_MASK_UNITS = CCF_MASK_UNITS.copy(__NAME__)
CCF_MASK_UNITS.value = 'nm'

# Define the CCF mask format (must be an astropy.table format)
CCF_MASK_FMT = CCF_MASK_FMT.copy(__NAME__)
CCF_MASK_FMT.value = 'ascii'

#  Define the weight of the CCF mask (if 1 force all weights equal)
CCF_MASK_MIN_WEIGHT = CCF_MASK_MIN_WEIGHT.copy(__NAME__)
CCF_MASK_MIN_WEIGHT.value = 0.0

#  Define the width of the template line (if 0 use natural)
CCF_MASK_WIDTH = CCF_MASK_WIDTH.copy(__NAME__)
CCF_MASK_WIDTH.value = 1.7

# Define target rv header null value
#     (values greater than absolute value are set to zero)
OBJRV_NULL_VAL = OBJRV_NULL_VAL.copy(__NAME__)
OBJRV_NULL_VAL.value = 1000

#  Define the maximum allowed ratio between input CCF STEP and CCF WIDTH
#     i.e. error will be generated if CCF_STEP > (CCF_WIDTH / RATIO)
CCF_MAX_CCF_WID_STEP_RATIO = CCF_MAX_CCF_WID_STEP_RATIO.copy(__NAME__)
CCF_MAX_CCF_WID_STEP_RATIO.value = 10.0

# Define the width of the CCF range [km/s]
CCF_DEFAULT_WIDTH = CCF_DEFAULT_WIDTH.copy(__NAME__)
CCF_DEFAULT_WIDTH.value = 300.0

# Define the computations steps of the CCF [km/s]
CCF_DEFAULT_STEP = CCF_DEFAULT_STEP.copy(__NAME__)
CCF_DEFAULT_STEP.value = 0.25

#   The value of the noise for wave dv rms calculation
#       snr = flux/sqrt(flux + noise^2)
CCF_NOISE_SIGDET = CCF_NOISE_SIGDET.copy(__NAME__)
CCF_NOISE_SIGDET.value = 8.0  # 100

#   The size around a saturated pixel to flag as unusable for wave dv rms
#      calculation
CCF_NOISE_BOXSIZE = CCF_NOISE_BOXSIZE.copy(__NAME__)
CCF_NOISE_BOXSIZE.value = 12

#   The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
CCF_NOISE_THRES = CCF_NOISE_THRES.copy(__NAME__)
CCF_NOISE_THRES.value = 1.0e9

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#      to calculate the CCF and RV
CCF_N_ORD_MAX = CCF_N_ORD_MAX.copy(__NAME__)
CCF_N_ORD_MAX.value = 71

# Allowed input DPRTYPES for input  for CCF recipe
CCF_ALLOWED_DPRTYPES = CCF_ALLOWED_DPRTYPES.copy(__NAME__)
CCF_ALLOWED_DPRTYPES.value = 'OBJ_DARK, OBJ_FP, OBJ_SKY, TELLU_SKY, FLUXSTD_SKY'

# Define the KW_OUTPUT types that are valid telluric corrected spectra
CCF_CORRECT_TELLU_TYPES = CCF_CORRECT_TELLU_TYPES.copy(__NAME__)
CCF_CORRECT_TELLU_TYPES.value = 'TELLU_OBJ'

# The transmission threshold for removing telluric domain (if and only if
#     we have a telluric corrected input file
CCF_TELLU_THRES = CCF_TELLU_THRES.copy(__NAME__)
CCF_TELLU_THRES.value = 0.5

# The half size (in pixels) of the smoothing box used to calculate what value
#    should replace the NaNs in the E2ds before CCF is calculated
CCF_FILL_NAN_KERN_SIZE = CCF_FILL_NAN_KERN_SIZE.copy(__NAME__)
CCF_FILL_NAN_KERN_SIZE.value = 10

# the step size (in pixels) of the smoothing box used to calculate what value
#   should replace the NaNs in the E2ds before CCF is calculated
CCF_FILL_NAN_KERN_RES = CCF_FILL_NAN_KERN_RES.copy(__NAME__)
CCF_FILL_NAN_KERN_RES.value = 0.1

#  Define the detector noise to use in the ccf
CCF_DET_NOISE = CCF_DET_NOISE.copy(__NAME__)
CCF_DET_NOISE.value = 100.0

# Define the fit type for the CCF fit
#     if 0 then we have an absorption line
#     if 1 then we have an emission line
CCF_FIT_TYPE = CCF_FIT_TYPE.copy(__NAME__)
CCF_FIT_TYPE.value = 0

# Define the percentile the blaze is normalised by before using in CCF calc
CCF_BLAZE_NORM_PERCENTILE = CCF_BLAZE_NORM_PERCENTILE.copy(__NAME__)
CCF_BLAZE_NORM_PERCENTILE.value = 90

# Define the minimum number of sigma the peak CCF must have to be acceptable
CCF_NSIG_THRESHOLD = CCF_NSIG_THRESHOLD.copy(__NAME__)
CCF_NSIG_THRESHOLD.value = 5
CCF_NSIG_THRESHOLD.author = base.AUTHORS['EA']

# Define the minimum number of sigma the FWHM of CCF must have to be acceptable
CCF_FWHM_SIGCUT = CCF_FWHM_SIGCUT.copy(__NAME__)
CCF_FWHM_SIGCUT.value = 8
CCF_FWHM_SIGCUT.author = base.AUTHORS['EA']

# =============================================================================
# DEBUG PLOT SETTINGS
# =============================================================================
# turn on dark image region debug plot
PLOT_DARK_IMAGE_REGIONS = PLOT_DARK_IMAGE_REGIONS.copy(__NAME__)
PLOT_DARK_IMAGE_REGIONS.value = True

# turn on dark histogram debug plot
PLOT_DARK_HISTOGRAM = PLOT_DARK_HISTOGRAM.copy(__NAME__)
PLOT_DARK_HISTOGRAM.value = True

# turn on badpix map debug plot
PLOT_BADPIX_MAP = PLOT_BADPIX_MAP.copy(__NAME__)
PLOT_BADPIX_MAP.value = True

# turn on localisation the width regions plot
PLOT_LOC_WIDTH_REGIONS = PLOT_LOC_WIDTH_REGIONS.copy(__NAME__)
PLOT_LOC_WIDTH_REGIONS.value = True

# turn on localisation fiber doublet paroty plot
PLOT_LOC_FIBER_DOUBLET_PARITY = PLOT_LOC_FIBER_DOUBLET_PARITY.copy(__NAME__)
PLOT_LOC_FIBER_DOUBLET_PARITY.value = True

# turn on localisation gap in orders plot
PLOT_LOC_GAP_ORDERS = PLOT_LOC_GAP_ORDERS.copy(__NAME__)
PLOT_LOC_GAP_ORDERS.value = True

# turn on localisation image fit plot
PLOT_LOC_IMAGE_FIT = PLOT_LOC_IMAGE_FIT.copy(__NAME__)
PLOT_LOC_IMAGE_FIT.value = True

# turn on localisation image corners plot
PLOT_LOC_IM_CORNER = PLOT_LOC_IM_CORNER.copy(__NAME__)
PLOT_LOC_IM_CORNER.value = True

# turn on localisation image regions plot
PLOT_LOC_IM_REGIONS = PLOT_LOC_IM_REGIONS.copy(__NAME__)
PLOT_LOC_IM_REGIONS.value = True

# turn on the shape dx debug plot
PLOT_SHAPE_DX = PLOT_SHAPE_DX.copy(__NAME__)
PLOT_SHAPE_DX.value = True

# turn on the shape linear transform params plot
PLOT_SHAPE_LINEAR_TPARAMS = PLOT_SHAPE_LINEAR_TPARAMS.copy(__NAME__)
PLOT_SHAPE_LINEAR_TPARAMS.value = True

# turn on the shape angle offset (all orders in loop) debug plot
PLOT_SHAPE_ANGLE_OFFSET_ALL = PLOT_SHAPE_ANGLE_OFFSET_ALL.copy(__NAME__)
PLOT_SHAPE_ANGLE_OFFSET_ALL.value = True

# turn on the shape angle offset (one selected order) debug plot
PLOT_SHAPE_ANGLE_OFFSET = PLOT_SHAPE_ANGLE_OFFSET.copy(__NAME__)
PLOT_SHAPE_ANGLE_OFFSET.value = True

# turn on the shape local zoom debug plot
PLOT_SHAPEL_ZOOM_SHIFT = PLOT_SHAPEL_ZOOM_SHIFT.copy(__NAME__)
PLOT_SHAPEL_ZOOM_SHIFT.value = True

# turn on the flat order fit edges debug plot (loop)
PLOT_FLAT_ORDER_FIT_EDGES1 = PLOT_FLAT_ORDER_FIT_EDGES1.copy(__NAME__)
PLOT_FLAT_ORDER_FIT_EDGES1.value = False

# turn on the flat order fit edges debug plot (selected order)
PLOT_FLAT_ORDER_FIT_EDGES2 = PLOT_FLAT_ORDER_FIT_EDGES2.copy(__NAME__)
PLOT_FLAT_ORDER_FIT_EDGES2.value = True

# turn on the flat blaze order debug plot (loop)
PLOT_FLAT_BLAZE_ORDER1 = PLOT_FLAT_BLAZE_ORDER1.copy(__NAME__)
PLOT_FLAT_BLAZE_ORDER1.value = False

# turn on the flat blaze order debug plot (selected order)
PLOT_FLAT_BLAZE_ORDER2 = PLOT_FLAT_BLAZE_ORDER2.copy(__NAME__)
PLOT_FLAT_BLAZE_ORDER2.value = True

# turn on thermal background (in extract) debug plot
PLOT_THERMAL_BACKGROUND = PLOT_THERMAL_BACKGROUND.copy(__NAME__)
PLOT_THERMAL_BACKGROUND.value = True

# turn on the extraction spectral order debug plot (loop)
PLOT_EXTRACT_SPECTRAL_ORDER1 = PLOT_EXTRACT_SPECTRAL_ORDER1.copy(__NAME__)
PLOT_EXTRACT_SPECTRAL_ORDER1.value = True

# turn on the extraction spectral order debug plot (selected order)
PLOT_EXTRACT_SPECTRAL_ORDER2 = PLOT_EXTRACT_SPECTRAL_ORDER2.copy(__NAME__)
PLOT_EXTRACT_SPECTRAL_ORDER2.value = True

# turn on the extraction 1d spectrum debug plot
PLOT_EXTRACT_S1D = PLOT_EXTRACT_S1D.copy(__NAME__)
PLOT_EXTRACT_S1D.value = True

# turn on the extraction 1d spectrum weight (before/after) debug plot
PLOT_EXTRACT_S1D_WEIGHT = PLOT_EXTRACT_S1D_WEIGHT.copy(__NAME__)
PLOT_EXTRACT_S1D_WEIGHT.value = True

# turn on the wave line fiber comparison plot
PLOT_WAVE_FIBER_COMPARISON = PLOT_WAVE_FIBER_COMPARISON.copy(__NAME__)
PLOT_WAVE_FIBER_COMPARISON.value = True

# turn on the wave line fiber comparison plot
PLOT_WAVE_FIBER_COMP = PLOT_WAVE_FIBER_COMP.copy(__NAME__)
PLOT_WAVE_FIBER_COMP.value = True

# turn on the wave length vs cavity width plot
PLOT_WAVE_WL_CAV = PLOT_WAVE_WL_CAV.copy(__NAME__)
PLOT_WAVE_WL_CAV.value = True

# turn on the wave diff HC histograms plot
PLOT_WAVE_HC_DIFF_HIST = PLOT_WAVE_HC_DIFF_HIST.copy(__NAME__)
PLOT_WAVE_HC_DIFF_HIST.value = True

# turn on the wave lines hc/fp expected vs measured debug plot
#  (will plot once for hc once for fp)
PLOT_WAVEREF_EXPECTED = PLOT_WAVEREF_EXPECTED.copy(__NAME__)
PLOT_WAVEREF_EXPECTED.value = True

# TODO: WAVE plots need sorting

# turn on the wave solution hc guess debug plot (in loop)
PLOT_WAVE_HC_GUESS = PLOT_WAVE_HC_GUESS.copy(__NAME__)
PLOT_WAVE_HC_GUESS.value = True

# turn on the wave solution hc brightest lines debug plot
PLOT_WAVE_HC_BRIGHTEST_LINES = PLOT_WAVE_HC_BRIGHTEST_LINES.copy(__NAME__)
PLOT_WAVE_HC_BRIGHTEST_LINES.value = True

# turn on the wave solution hc triplet fit grid debug plot
PLOT_WAVE_HC_TFIT_GRID = PLOT_WAVE_HC_TFIT_GRID.copy(__NAME__)
PLOT_WAVE_HC_TFIT_GRID.value = True

# turn on the wave solution hc resolution map debug plot
PLOT_WAVE_HC_RESMAP = PLOT_WAVE_HC_RESMAP.copy(__NAME__)
PLOT_WAVE_HC_RESMAP.value = True

# turn on the wave solution hc resolution map debug plot
PLOT_WAVE_RESMAP = PLOT_WAVE_RESMAP.copy(__NAME__)
PLOT_WAVE_RESMAP.value = True

# turn on the wave solution littrow check debug plot
PLOT_WAVE_LITTROW_CHECK1 = PLOT_WAVE_LITTROW_CHECK1.copy(__NAME__)
PLOT_WAVE_LITTROW_CHECK1.value = True

# turn on the wave solution littrow extrapolation debug plot
PLOT_WAVE_LITTROW_EXTRAP1 = PLOT_WAVE_LITTROW_EXTRAP1.copy(__NAME__)
PLOT_WAVE_LITTROW_EXTRAP1.value = True

# turn on the wave solution littrow check debug plot
PLOT_WAVE_LITTROW_CHECK2 = PLOT_WAVE_LITTROW_CHECK2.copy(__NAME__)
PLOT_WAVE_LITTROW_CHECK2.value = True

# turn on the wave solution littrow extrapolation debug plot
PLOT_WAVE_LITTROW_EXTRAP2 = PLOT_WAVE_LITTROW_EXTRAP2.copy(__NAME__)
PLOT_WAVE_LITTROW_EXTRAP2.value = True

# turn on the wave solution final fp order debug plot
PLOT_WAVE_FP_FINAL_ORDER = PLOT_WAVE_FP_FINAL_ORDER.copy(__NAME__)
PLOT_WAVE_FP_FINAL_ORDER.value = True

# turn on the wave solution fp local width offset debug plot
PLOT_WAVE_FP_LWID_OFFSET = PLOT_WAVE_FP_LWID_OFFSET.copy(__NAME__)
PLOT_WAVE_FP_LWID_OFFSET.value = True

# turn on the wave solution fp wave residual debug plot
PLOT_WAVE_FP_WAVE_RES = PLOT_WAVE_FP_WAVE_RES.copy(__NAME__)
PLOT_WAVE_FP_WAVE_RES.value = True

# turn on the wave solution fp fp_m_x residual debug plot
PLOT_WAVE_FP_M_X_RES = PLOT_WAVE_FP_M_X_RES.copy(__NAME__)
PLOT_WAVE_FP_M_X_RES.value = True

# turn on the wave solution fp interp cavity width 1/m_d hc debug plot
PLOT_WAVE_FP_IPT_CWID_1MHC = PLOT_WAVE_FP_IPT_CWID_1MHC.copy(__NAME__)
PLOT_WAVE_FP_IPT_CWID_1MHC.value = True

# turn on the wave solution fp interp cavity width ll hc and fp debug plot
PLOT_WAVE_FP_IPT_CWID_LLHC = PLOT_WAVE_FP_IPT_CWID_LLHC.copy(__NAME__)
PLOT_WAVE_FP_IPT_CWID_LLHC.value = True

# turn on the wave solution old vs new wavelength difference debug plot
PLOT_WAVE_FP_LL_DIFF = PLOT_WAVE_FP_LL_DIFF.copy(__NAME__)
PLOT_WAVE_FP_LL_DIFF.value = True

# turn on the wave solution fp multi order debug plot
PLOT_WAVE_FP_MULTI_ORDER = PLOT_WAVE_FP_MULTI_ORDER.copy(__NAME__)
PLOT_WAVE_FP_MULTI_ORDER.value = True

# turn on the wave solution fp single order debug plot
PLOT_WAVE_FP_SINGLE_ORDER = PLOT_WAVE_FP_SINGLE_ORDER.copy(__NAME__)
PLOT_WAVE_FP_SINGLE_ORDER.value = True

# turn on the wave per night iteration debug plot
PLOT_WAVENIGHT_ITERPLOT = PLOT_WAVENIGHT_ITERPLOT.copy(__NAME__)
PLOT_WAVENIGHT_ITERPLOT.value = True

# turn on the wave per night hist debug plot
PLOT_WAVENIGHT_HISTPLOT = PLOT_WAVENIGHT_HISTPLOT.copy(__NAME__)
PLOT_WAVENIGHT_HISTPLOT.value = True

# turn on the sky model region plot
PLOT_TELLU_SKYMODEL_REGION_PLOT = PLOT_TELLU_SKYMODEL_REGION_PLOT.copy(__NAME__)
PLOT_TELLU_SKYMODEL_REGION_PLOT.value = True

# turn on the sky model median plot
PLOT_TELLU_SKYMODEL_MED = PLOT_TELLU_SKYMODEL_MED.copy(__NAME__)
PLOT_TELLU_SKYMODEL_MED.value = True

# turn on the sky model median plot
PLOT_TELLU_SKYMODEL_LINEFIT = PLOT_TELLU_SKYMODEL_LINEFIT.copy(__NAME__)
PLOT_TELLU_SKYMODEL_LINEFIT.value = True

# turn on the sky correction debug plot
PLOT_TELLU_SKY_CORR_PLOT = PLOT_TELLU_SKY_CORR_PLOT.copy(__NAME__)
PLOT_TELLU_SKY_CORR_PLOT.value = True

# turn on the telluric pre-cleaning ccf debug plot
PLOT_TELLUP_WAVE_TRANS = PLOT_TELLUP_WAVE_TRANS.copy(__NAME__)
PLOT_TELLUP_WAVE_TRANS.value = True

# turn on the telluric pre-cleaning result debug plot
PLOT_TELLUP_ABSO_SPEC = PLOT_TELLUP_ABSO_SPEC.copy(__NAME__)
PLOT_TELLUP_ABSO_SPEC.value = True

# turn on the telluric OH cleaning debug plot
PLOT_TELLUP_CLEAN_OH = PLOT_TELLUP_CLEAN_OH.copy(__NAME__)
PLOT_TELLUP_CLEAN_OH.value = True

# turn on the make tellu wave flux debug plot (in loop)
PLOT_MKTELLU_WAVE_FLUX1 = PLOT_MKTELLU_WAVE_FLUX1.copy(__NAME__)
PLOT_MKTELLU_WAVE_FLUX1.value = False

# turn on the make tellu wave flux debug plot (single order)
PLOT_MKTELLU_WAVE_FLUX2 = PLOT_MKTELLU_WAVE_FLUX2.copy(__NAME__)
PLOT_MKTELLU_WAVE_FLUX2.value = True

# turn on the make tellu model plot
PLOT_MKTELLU_MODEL = PLOT_MKTELLU_MODEL.copy(__NAME__)
PLOT_MKTELLU_MODEL.value = True

# turn on the fit tellu pca component debug plot (in loop)
PLOT_FTELLU_PCA_COMP1 = PLOT_FTELLU_PCA_COMP1.copy(__NAME__)
PLOT_FTELLU_PCA_COMP1.value = False

# turn on the fit tellu pca component debug plot (single order)
PLOT_FTELLU_PCA_COMP2 = PLOT_FTELLU_PCA_COMP2.copy(__NAME__)
PLOT_FTELLU_PCA_COMP2.value = True

# turn on the fit tellu reconstructed spline debug plot (in loop)
PLOT_FTELLU_RECON_SPLINE1 = PLOT_FTELLU_RECON_SPLINE1.copy(__NAME__)
PLOT_FTELLU_RECON_SPLINE1.value = False

# turn on the fit tellu reconstructed spline debug plot (single order)
PLOT_FTELLU_RECON_SPLINE2 = PLOT_FTELLU_RECON_SPLINE2.copy(__NAME__)
PLOT_FTELLU_RECON_SPLINE2.value = True

# turn on the fit tellu wave shift debug plot (in loop)
PLOT_FTELLU_WAVE_SHIFT1 = PLOT_FTELLU_WAVE_SHIFT1.copy(__NAME__)
PLOT_FTELLU_WAVE_SHIFT1.value = False

# turn on the fit tellu wave shift debug plot (single order)
PLOT_FTELLU_WAVE_SHIFT2 = PLOT_FTELLU_WAVE_SHIFT2.copy(__NAME__)
PLOT_FTELLU_WAVE_SHIFT2.value = True

# turn on the fit tellu reconstructed absorption debug plot (in loop)
PLOT_FTELLU_RECON_ABSO1 = PLOT_FTELLU_RECON_ABSO1.copy(__NAME__)
PLOT_FTELLU_RECON_ABSO1.value = True

# turn on the fit tellu reconstructed absorption debug plot (single order)
PLOT_FTELLU_RECON_ABSO2 = PLOT_FTELLU_RECON_ABSO2.copy(__NAME__)
PLOT_FTELLU_RECON_ABSO2.value = True

# turn on the fit tellu res model debug plot
PLOT_FTELLU_RES_MODEL = PLOT_FTELLU_RES_MODEL.copy(__NAME__)
PLOT_FTELLU_RES_MODEL.value = True

# turn on the finite resolution correction debug plot
PLOT_TELLU_FINITE_RES_CORR = PLOT_TELLU_FINITE_RES_CORR.copy(__NAME__)
PLOT_TELLU_FINITE_RES_CORR.value = True

# turn on the berv coverage debug plot
PLOT_MKTEMP_BERV_COV = PLOT_MKTEMP_BERV_COV.copy(__NAME__)
PLOT_MKTEMP_BERV_COV.value = True

# turn on the template s1d deconvolution plot
PLOT_MKTEMP_S1D_DECONV = PLOT_MKTEMP_S1D_DECONV.copy(__NAME__)
PLOT_MKTEMP_S1D_DECONV.value = True

# turn on the ccf rv fit debug plot (in a loop around orders)
PLOT_CCF_RV_FIT_LOOP = PLOT_CCF_RV_FIT_LOOP.copy(__NAME__)
PLOT_CCF_RV_FIT_LOOP.value = True

# turn on the ccf rv fit debug plot (for the mean order value)
PLOT_CCF_RV_FIT = PLOT_CCF_RV_FIT.copy(__NAME__)
PLOT_CCF_RV_FIT.value = True

# turn on the ccf spectral order vs wavelength debug plot
PLOT_CCF_SWAVE_REF = PLOT_CCF_SWAVE_REF.copy(__NAME__)
PLOT_CCF_SWAVE_REF.value = False

# turn on the ccf photon uncertainty debug plot
PLOT_CCF_PHOTON_UNCERT = PLOT_CCF_PHOTON_UNCERT.copy(__NAME__)
PLOT_CCF_PHOTON_UNCERT.value = True

# =============================================================================
# POST PROCESS SETTINGS
# =============================================================================
# Define whether (by deafult) to clear reduced directory
POST_CLEAR_REDUCED = POST_CLEAR_REDUCED.copy(__NAME__)
POST_CLEAR_REDUCED.value = False

# Define whether (by default) to overwrite post processed files
POST_OVERWRITE = POST_OVERWRITE.copy(__NAME__)
POST_OVERWRITE.value = False

# Define the header keyword store to insert extension comment after
POST_HDREXT_COMMENT_KEY = POST_HDREXT_COMMENT_KEY.copy(__NAME__)
POST_HDREXT_COMMENT_KEY.value = 'KW_IDENTIFIER'

# =============================================================================
# TOOLS SETTINGS
# =============================================================================
# Define which block kinds to reindex (warning can take a long time)
#    only select block kinds that have (or could be) manually changed
REPROCESS_REINDEX_BLOCKS = REPROCESS_REINDEX_BLOCKS.copy(__NAME__)
REPROCESS_REINDEX_BLOCKS.value = 'raw,tmp,red,out'

# Define whether to use multiprocess Pool or Process
REPROCESS_MP_TYPE = REPROCESS_MP_TYPE.copy(__NAME__)
REPROCESS_MP_TYPE.value = 'process'

# Key for use in run files
REPROCESS_RUN_KEY = REPROCESS_RUN_KEY.copy(__NAME__)
REPROCESS_RUN_KEY.value = 'ID'

# Define the obs_dir column name for raw file table
REPROCESS_OBSDIR_COL = REPROCESS_OBSDIR_COL.copy(__NAME__)
REPROCESS_OBSDIR_COL.value = 'OBS_DIR'

# Define the KW_OBJTYPE allowed for a science target
REPROCESS_OBJECT_TYPES = REPROCESS_OBJECT_TYPES.copy(__NAME__)
REPROCESS_OBJECT_TYPES.value = 'OBJECT OBJECT,SKY OBJECT,FP, OBJECT,DARK'

# Define the pi name column name for raw file table
REPROCESS_PINAMECOL = REPROCESS_PINAMECOL.copy(__NAME__)
REPROCESS_PINAMECOL.value = 'KW_PI_NAME'

# Define the absolute file column name for raw file table
REPROCESS_ABSFILECOL = REPROCESS_ABSFILECOL.copy(__NAME__)
REPROCESS_ABSFILECOL.value = 'ABSPATH'

# Define the modified file column name for raw file table
REPROCESS_MODIFIEDCOL = REPROCESS_MODIFIEDCOL.copy(__NAME__)
REPROCESS_MODIFIEDCOL.value = 'LAST_MODIFIED'

# Define the sort column (from header keywords) for raw file table
REPROCESS_SORTCOL_HDRKEY = REPROCESS_SORTCOL_HDRKEY.copy(__NAME__)
REPROCESS_SORTCOL_HDRKEY.value = 'KW_ACQTIME'

# Define the raw index filename
REPROCESS_RAWINDEXFILE = REPROCESS_RAWINDEXFILE.copy(__NAME__)
REPROCESS_RAWINDEXFILE.value = 'rawindex.fits'

# define the sequence (1 of 5, 2 of 5 etc) col for raw file table
REPROCESS_SEQCOL = REPROCESS_SEQCOL.copy(__NAME__)
REPROCESS_SEQCOL.value = 'KW_CMPLTEXP'

# define the time col for raw file table
REPROCESS_TIMECOL = REPROCESS_TIMECOL.copy(__NAME__)
REPROCESS_TIMECOL.value = 'KW_ACQTIME'

# Define the rejection sql query (between identifier and reject list col)
#    must use a valid reject database column and use {identifier} in query
REPROCESS_REJECT_SQL = REPROCESS_REJECT_SQL.copy(__NAME__)
REPROCESS_REJECT_SQL.value = 'FILENAME="{identifier}"'

# Define the extra SQL science object select critera
REPROCESS_OBJ_SCI_SQL = REPROCESS_OBJ_SCI_SQL.copy(__NAME__)
REPROCESS_OBJ_SCI_SQL.value = ' AND KW_OBSTYPE LIKE "OBJECT%"'

# Define whether we try to create a latex summary pdf
#   (turn this off if you have any problems with latex/pdflatex)
SUMMARY_LATEX_PDF = SUMMARY_LATEX_PDF.copy(__NAME__)
SUMMARY_LATEX_PDF.value = True

# Define exposure meter minimum wavelength for mask
EXPMETER_MIN_LAMBDA = EXPMETER_MIN_LAMBDA.copy(__NAME__)
EXPMETER_MIN_LAMBDA.value = 1478.7

# Define exposure meter maximum wavelength for mask
EXPMETER_MAX_LAMBDA = EXPMETER_MAX_LAMBDA.copy(__NAME__)
EXPMETER_MAX_LAMBDA.value = 1823.1

# Define exposure meter telluric threshold (minimum tapas transmission)
EXPMETER_TELLU_THRES = EXPMETER_TELLU_THRES.copy(__NAME__)
EXPMETER_TELLU_THRES.value = 0.95

# Define the types of file allowed for drift measurement
DRIFT_DPRTYPES = DRIFT_DPRTYPES.copy(__NAME__)
DRIFT_DPRTYPES.value = 'FP_FP, OBJ_FP, DARK_FP'

# Define the fiber dprtype allowed for drift measurement (only FP)
DRIFT_DPR_FIBER_TYPE = DRIFT_DPR_FIBER_TYPE.copy(__NAME__)
DRIFT_DPR_FIBER_TYPE.value = 'FP'

# =============================================================================
#  End of configuration file
# =============================================================================
