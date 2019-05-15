# This is the main config file
from terrapipe.constants.core import constant_functions

# =============================================================================
# Define variables
# =============================================================================
# all definition
__all__ = [# preprocessing constants
           'PP_CORRUPT_MED_SIZE', 'PP_CORRUPT_HOT_THRES', 'PP_NUM_DARK_AMP',
           'PP_FULL_FLAT', 'PP_TOTAL_AMP_NUM', 'DATA_ENGINEERING',
           'PP_NUM_REF_TOP', 'PP_NUM_REF_BOTTOM', 'PP_RMS_PERCENTILE',
           'PP_LOWEST_RMS_PERCENTILE', 'PP_CORRUPT_SNR_HOTPIX',
           'PP_CORRUPT_RMS_THRES', 'RAW_TO_PP_ROTATION', 'PP_DARK_MED_BINNUM',
           # image constants
           'INPUT_COMBINE_IMAGES', 'INPUT_FLIP_IMAGE', 'INPUT_RESIZE_IMAGE',
           'IMAGE_X_LOW', 'IMAGE_X_HIGH',
           'IMAGE_Y_LOW', 'IMAGE_Y_HIGH', 'IMAGE_X_LOW', 'IMAGE_X_HIGH',
           'IMAGE_Y_LOW', 'IMAGE_Y_HIGH', 'IMAGE_X_BLUE_LOW',
           # qc constants
           'QC_DARK_TIME', 'QC_MAX_DEAD', 'DARK_QMIN', 'DARK_QMAX',
           'QC_MAX_DARK',
           # dark constants
           'IMAGE_X_BLUE_HIGH', 'IMAGE_Y_BLUE_LOW', 'IMAGE_Y_BLUE_HIGH',
           'IMAGE_X_RED_LOW', 'IMAGE_X_RED_HIGH', 'IMAGE_Y_RED_LOW',
           'IMAGE_Y_RED_HIGH', 'DARK_CUTLIMIT', 'QC_MAX_DARKLEVEL',
           'HISTO_BINS', 'HISTO_RANGE_LOW', 'HISTO_RANGE_HIGH',
           'USE_SKYDARK_CORRECTION', 'USE_SKYDARK_ONLY',
           # badpix constants
           'BADPIX_FULL_FLAT', 'BADPIX_FLAT_MED_WID', 'BADPIX_FLAT_CUT_RATIO',
           'BADPIX_ILLUM_CUT', 'BADPIX_MAX_HOTPIX', 'BADPIX_FULL_THRESHOLD',
           'BADPIX_NORM_PERCENTILE',
           # bkgr constants
           'BKGR_BOXSIZE', 'BKGR_PERCENTAGE', 'BKGR_MASK_CONVOLVE_SIZE',
           'BKGR_N_BAD_NEIGHBOURS', 'BKGR_NO_SUBTRACTION', 'BKGR_KER_AMP',
           'BKGR_KER_WX', 'BKGR_KER_WY', 'BKGR_KER_SIG',
           # localisation constants
           'LOC_ORDERP_BOX_SIZE']

# set name
__NAME__ = 'terrapipe.constants.default.default_constants'

# Constants class
Const = constant_functions.Const

# =============================================================================
# DRS DATA SETTINGS
# =============================================================================
# Define the data engineering path
DATA_ENGINEERING = Const('DATA_ENGINEERING', value=None, dtype=str,
                         source=__NAME__)

# =============================================================================
# COMMON IMAGE SETTINGS
# =============================================================================
# Defines whether to by default combine images that are inputted at the same
#   time
INPUT_COMBINE_IMAGES = Const('INPUT_COMBINE_IMAGES', dtype=bool, value=True,
                             source=__NAME__)

# Defines whether to, by default, flip images that are inputted
INPUT_FLIP_IMAGE = Const('INPUT_FLIP_IMAGE', dtype=bool, value=True,
                         source=__NAME__)

# Defines whether to, by default, resize images that are inputted
INPUT_RESIZE_IMAGE = Const('INPUT_RESIZE_IMAGE', dtype=bool, value=True,
                           source=__NAME__)

# Defines the resized image
IMAGE_X_LOW = Const('IMAGE_X_LOW', value=None, dtype=int, minimum=0,
                    source=__NAME__)
IMAGE_X_HIGH = Const('IMAGE_X_HIGH', value=None, dtype=int, minimum=0,
                     source=__NAME__)
IMAGE_Y_LOW = Const('IMAGE_Y_LOW', value=None, dtype=int, minimum=0,
                    source=__NAME__)
IMAGE_Y_HIGH = Const('IMAGE_Y_HIGH', value=None, dtype=int, minimum=0,
                     source=__NAME__)

# =============================================================================
# PRE-PROCESSSING SETTINGS
# =============================================================================
# Defines the size around badpixels that is considered part of the bad pixel
PP_CORRUPT_MED_SIZE = Const('PP_CORRUPT_MED_SIZE', value=None, dtype=int,
                            minimum=0, source=__NAME__)

# Defines the threshold (above the full engineering flat) that selects bad
#     (hot) pixels
PP_CORRUPT_HOT_THRES = Const('PP_CORRUPT_HOT_THRES', value=None, dtype=int,
                             minimum=0, source=__NAME__)

#   Define the total number of amplifiers
PP_TOTAL_AMP_NUM = Const('PP_TOTAL_AMP_NUM', value=None, dtype=int,
                         minimum=0, source=__NAME__)

#   Define the number of dark amplifiers
PP_NUM_DARK_AMP = Const('PP_NUM_DARK_AMP', value=None, dtype=int,
                        minimum=0, source=__NAME__)

#   Define the number of bins used in the dark median process         - [cal_pp]
PP_DARK_MED_BINNUM = Const('PP_DARK_MED_BINNUM', value=None, dtype=int,
                           minimum=0, source=__NAME__)

#   Defines the full detector flat file (located in the data folder)
PP_FULL_FLAT = Const('PP_FULL_FLAT', value=None, dtype=str, source=__NAME__)

#   Define the number of un-illuminated reference pixels at top of image
PP_NUM_REF_TOP = Const('PP_NUM_REF_TOP', value=None, dtype=int,
                       source=__NAME__)

#   Define the number of un-illuminated reference pixels at bottom of image
PP_NUM_REF_BOTTOM = Const('PP_NUM_REF_BOTTOM', value=None, dtype=int,
                          source=__NAME__)

# Define the percentile value for the rms normalisation (0-100)
PP_RMS_PERCENTILE = Const('PP_RMS_PERCENTILE', value=None, dtype=int,
                          minimum=0, maximum=100, source=__NAME__)

# Define the lowest rms value of the rms percentile allowed if the value of
#     the pp_rms_percentile-th is lower than this this value is used
PP_LOWEST_RMS_PERCENTILE = Const('PP_LOWEST_RMS_PERCENTILE', value=None,
                                 dtype=float, minimum=0.0, source=__NAME__)

# Defines the snr hotpix threshold to define a corrupt file
PP_CORRUPT_SNR_HOTPIX = Const('PP_CORRUPT_SNR_HOTPIX', value=None, dtype=float,
                              minimum=0.0, source=__NAME__)

# Defines the RMS threshold to also catch corrupt files
PP_CORRUPT_RMS_THRES = Const('PP_CORRUPT_RMS_THRES', value=None, dtype=float,
                             minimum=0.0, source=__NAME__)

#   Define rotation angle (must be multiple of 90 degrees)
#         (in degrees counter-clockwise direction)
RAW_TO_PP_ROTATION = Const('RAW_TO_PP_ROTATION', value=None, dtype=int,
                           minimum=0.0, maximum=360.0, source=__NAME__)

# =============================================================================
# CALIBRATION: DARK SETTINGS
# =============================================================================
#   Min dark exposure time
QC_DARK_TIME = Const('QC_DARK_TIME', value=None, dtype=float, minimum=0.0,
                     source=__NAME__)

#   Max dark median level [ADU/s]
QC_MAX_DARKLEVEL = Const('QC_MAX_DARKLEVEL', value=None, dtype=float,
                         source=__NAME__)

#   Max fraction of dark pixels (percent)
QC_MAX_DARK = Const('QC_MAX_DARK', value=None, dtype=float, source=__NAME__)

#   Max fraction of dead pixels
QC_MAX_DEAD = Const('QC_MAX_DEAD', value=None, dtype=float, source=__NAME__)

# Defines the resized blue image
IMAGE_X_BLUE_LOW = Const('IMAGE_X_BLUE_LOW', value=None, dtype=int, minimum=0,
                         source=__NAME__)
IMAGE_X_BLUE_HIGH = Const('IMAGE_X_BLUE_HIGH', value=None, dtype=int, minimum=0,
                          source=__NAME__)
IMAGE_Y_BLUE_LOW = Const('IMAGE_Y_BLUE_LOW', value=None, dtype=int, minimum=0,
                         source=__NAME__)
IMAGE_Y_BLUE_HIGH = Const('IMAGE_Y_BLUE_HIGH', value=None, dtype=int, minimum=0,
                          source=__NAME__)

# Defines the resized red image
IMAGE_X_RED_LOW = Const('IMAGE_X_RED_LOW', value=None, dtype=int, minimum=0,
                        source=__NAME__)
IMAGE_X_RED_HIGH = Const('IMAGE_X_RED_HIGH', value=None, dtype=int, minimum=0,
                         source=__NAME__)
IMAGE_Y_RED_LOW = Const('IMAGE_Y_RED_LOW', value=None, dtype=int, minimum=0,
                        source=__NAME__)
IMAGE_Y_RED_HIGH = Const('IMAGE_Y_RED_HIGH', value=None, dtype=int, minimum=0,
                         source=__NAME__)

#   Define a bad pixel cut limit (in ADU/s)
DARK_CUTLIMIT = Const('DARK_CUTLIMIT', value=None, dtype=float, source=__NAME__)

#   Defines the lower and upper percentiles when measuring the dark
DARK_QMIN = Const('DARK_QMIN', value=None, dtype=int, source=__NAME__,
                  minimum=0, maximum=100)
DARK_QMAX = Const('DARK_QMAX', value=None, dtype=int, source=__NAME__,
                  minimum=0, maximum=100)

#   The number of bins in dark histogram
HISTO_BINS = Const('HISTO_BINS', value=None, dtype=int, source=__NAME__,
                   minimum=1)

#   The range of the histogram in ADU/s
HISTO_RANGE_LOW = Const('HISTO_RANGE_LOW', value=None, dtype=int,
                        source=__NAME__)
HISTO_RANGE_HIGH = Const('HISTO_RANGE_LOW', value=None, dtype=int,
                         source=__NAME__)

#    Define whether to use SKYDARK for dark corrections
USE_SKYDARK_CORRECTION = Const('USE_SKYDARK_CORRECTION', value=None,
                               dtype=bool, source=__NAME__)

#    If use_skydark_correction is True define whether we use
#       the SKYDARK only or use SKYDARK/DARK (whichever is closest)
USE_SKYDARK_ONLY = Const('USE_SKYDARK_ONLY', value=None, dtype=bool,
                         source=__NAME__)

# =============================================================================
# CALIBRATION: BAD PIXEL MAP SETTINGS
# =============================================================================
#   Defines the full detector flat file (located in the data folder)
BADPIX_FULL_FLAT = Const('BADPIX_FULL_FLAT', value=None, dtype=str,
                         source=__NAME__)

#   Percentile to normalise to when normalising and median filtering
#      image [percentage]
BADPIX_NORM_PERCENTILE = Const('BADPIX_NORM_PERCENTILE', value=None,
                               dtype=float, source=__NAME__,
                               minimum=0.0, maximum=100.0)

#   Define the median image in the x dimension over a boxcar of this width
BADPIX_FLAT_MED_WID = Const('BADPIX_FLAT_MED_WID', value=None, dtype=int,
                            source=__NAME__, minimum=0)

#   Define the maximum differential pixel cut ratio
BADPIX_FLAT_CUT_RATIO = Const('BADPIX_FLAT_CUT_RATIO', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

#   Define the illumination cut parameter
BADPIX_ILLUM_CUT = Const('BADPIX_ILLUM_CUT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

#   Define the maximum flux in ADU/s to be considered too hot to be used
BADPIX_MAX_HOTPIX = Const('BADPIX_MAX_HOTPIX', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

#   Defines the threshold on the full detector flat file to deem pixels as good
BADPIX_FULL_THRESHOLD = Const('BADPIX_FULL_THRESHOLD', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

# =============================================================================
# CALIBRATION: BACKGROUND CORRECTION SETTINGS
# =============================================================================
#    Width of the box to produce the background mask
BKGR_BOXSIZE = Const('BKGR_BOXSIZE', value=None, dtype=int,
                     source=__NAME__, minimum=0)

#    Do background percentile to compute minimum value (%)
BKGR_PERCENTAGE = Const('BKGR_PERCENTAGE', value=None, dtype=float,
                        source=__NAME__, minimum=0.0, maximum=100.0)

#    Size in pixels of the convolve tophat for the background mask
BKGR_MASK_CONVOLVE_SIZE = Const('BKGR_MASK_CONVOLVE_SIZE', value=None,
                                dtype=int, source=__NAME__, minimum=0)

#    If a pixel has this or more "dark" neighbours, we consider it dark
#        regardless of its initial value
BKGR_N_BAD_NEIGHBOURS = Const('BKGR_N_BAD_NEIGHBOURS', value=None, dtype=int,
                              source=__NAME__, minimum=0)

#    Do not correct for background measurement (True or False)
BKGR_NO_SUBTRACTION = Const('BKGR_NO_SUBTRACTION', value=None, dtype=bool,
                            source=__NAME__)

#    Kernel amplitude determined from drs_local_scatter.py
BKGR_KER_AMP = Const('BKGR_KER_AMP', value=None, dtype=float, source=__NAME__)

#    Background kernel width in in x and y [pixels]
BKGR_KER_WX = Const('BKGR_KER_WX', value=None, dtype=int, source=__NAME__)
BKGR_KER_WY = Const('BKGR_KER_WY', value=None, dtype=int, source=__NAME__)

#    construct a convolution kernel. We go from -IC_BKGR_KER_SIG to
#        +IC_BKGR_KER_SIG sigma in each direction. Its important no to
#        make the kernel too big as this slows-down the 2D convolution.
#        Do NOT make it a -10 to +10 sigma gaussian!
BKGR_KER_SIG = Const('BKGR_KER_SIG', value=None, dtype=float, source=__NAME__)


# =============================================================================
# CALIBRATION: LOCALISATION SETTINGS
# =============================================================================
#   Size of the order_profile smoothed box
#     (from pixel - size to pixel + size)
LOC_ORDERP_BOX_SIZE = Const('LOC_ORDERP_BOX_SIZE', value=None, dtype=int,
                            source=__NAME__)



