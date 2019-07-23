# This is the main config file
from terrapipe.core.constants import constant_functions

# =============================================================================
# Define variables
# =============================================================================
# all definition
__all__ = [
    # general
    'DATA_ENGINEERING', 'CALIB_DB_FORCE_WAVESOL', 'DATA_CORE',
    # preprocessing constants
    'PP_CORRUPT_MED_SIZE', 'PP_CORRUPT_HOT_THRES', 'PP_NUM_DARK_AMP',
    'PP_FULL_FLAT', 'PP_TOTAL_AMP_NUM',
    'PP_NUM_REF_TOP', 'PP_NUM_REF_BOTTOM', 'PP_RMS_PERCENTILE',
    'PP_LOWEST_RMS_PERCENTILE', 'PP_CORRUPT_SNR_HOTPIX',
    'PP_CORRUPT_RMS_THRES', 'RAW_TO_PP_ROTATION', 'PP_DARK_MED_BINNUM',
    # image constants
    'FIBER_TYPES',
    'INPUT_COMBINE_IMAGES', 'INPUT_FLIP_IMAGE', 'INPUT_RESIZE_IMAGE',
    'IMAGE_X_LOW', 'IMAGE_X_HIGH',
    'IMAGE_Y_LOW', 'IMAGE_Y_HIGH', 'IMAGE_X_LOW', 'IMAGE_X_HIGH',
    'IMAGE_Y_LOW', 'IMAGE_Y_HIGH', 'IMAGE_X_BLUE_LOW',
    # general calib constants
    'CAVITY_LENGTH_FILE', 'CAVITY_LENGTH_FILE_FMT',
    'CAVITY_LENGTH_FILE_COLS', 'CAVITY_LENGTH_FILE_START',
    'CAVITY_LENGTH_FILE_WAVECOL',
    # qc constants
    'QC_DARK_TIME', 'QC_MAX_DEAD', 'DARK_QMIN', 'DARK_QMAX',
    'QC_MAX_DARK', 'QC_LOC_MAXFIT_REMOVED_CTR',
    'QC_LOC_MAXFIT_REMOVED_WID', 'QC_LOC_RMSMAX_CTR',
    'QC_LOC_RMSMAX_WID',
    # fiber constants
    'FIBER_FIRST_ORDER_JUMP_AB', 'FIBER_FIRST_ORDER_JUMP_A',
    'FIBER_FIRST_ORDER_JUMP_B', 'FIBER_FIRST_ORDER_JUMP_C',
    'FIBER_MAX_NUM_ORDERS_AB', 'FIBER_MAX_NUM_ORDERS_A',
    'FIBER_MAX_NUM_ORDERS_B', 'FIBER_MAX_NUM_ORDERS_C',
    'FIBER_SET_NUM_FIBERS_AB', 'FIBER_SET_NUM_FIBERS_A',
    'FIBER_SET_NUM_FIBERS_B', 'FIBER_SET_NUM_FIBERS_C',
    # dark constants
    'IMAGE_X_BLUE_HIGH', 'IMAGE_Y_BLUE_LOW', 'IMAGE_Y_BLUE_HIGH',
    'IMAGE_X_RED_LOW', 'IMAGE_X_RED_HIGH', 'IMAGE_Y_RED_LOW',
    'IMAGE_Y_RED_HIGH', 'DARK_CUTLIMIT', 'QC_MAX_DARKLEVEL',
    'HISTO_BINS', 'HISTO_RANGE_LOW', 'HISTO_RANGE_HIGH',
    'USE_SKYDARK_CORRECTION', 'USE_SKYDARK_ONLY', 'ALLOWED_DARK_TYPES',
    'DARK_MASTER_MATCH_TIME', 'DARK_MASTER_MED_SIZE',
    # badpix constants
    'BADPIX_FULL_FLAT', 'BADPIX_FLAT_MED_WID', 'BADPIX_FLAT_CUT_RATIO',
    'BADPIX_ILLUM_CUT', 'BADPIX_MAX_HOTPIX', 'BADPIX_FULL_THRESHOLD',
    'BADPIX_NORM_PERCENTILE',
    # bkgr constants
    'BKGR_BOXSIZE', 'BKGR_PERCENTAGE', 'BKGR_MASK_CONVOLVE_SIZE',
    'BKGR_N_BAD_NEIGHBOURS', 'BKGR_NO_SUBTRACTION', 'BKGR_KER_AMP',
    'BKGR_KER_WX', 'BKGR_KER_WY', 'BKGR_KER_SIG',
    # localisation constants
    'LOC_ORDERP_BOX_SIZE', 'LOC_START_ROW_OFFSET', 'LOC_CENTRAL_COLUMN',
    'LOC_HALF_ORDER_SPACING', 'LOC_MINPEAK_AMPLITUDE',
    'LOC_WIDTH_POLY_DEG', 'LOC_CENT_POLY_DEG', 'LOC_COLUMN_SEP_FITTING',
    'LOC_EXT_WINDOW_SIZE', 'LOC_IMAGE_GAP', 'LOC_ORDER_WIDTH_MIN',
    'LOC_NOISE_MULTIPLIER_THRES', 'LOC_MAX_RMS_CENT', 'LOC_MAX_PTP_CENT',
    'LOC_PTPORMS_CENT', 'LOC_MAX_RMS_WID', 'LOC_MAX_PTP_WID',
    'LOC_SAT_THRES', 'LOC_SAVE_SUPERIMP_FILE', 'LOC_BKGRD_THRESHOLD',
    'LOC_ORDER_CURVE_DROP',
    # shape constants
    'ALLOWED_FP_TYPES', 'FP_MASTER_MATCH_TIME',
    'FP_MASTER_PERCENT_THRES', 'SHAPE_QC_LTRANS_RES_THRES',
    'SHAPE_MASTER_VALIDFP_PERCENTILE', 'SHAPE_MASTER_VALIDFP_THRESHOLD',
    'SHAPE_MASTER_LINTRANS_NITER', 'SHAPE_MASTER_FP_INI_BOXSIZE',
    'SHAPE_MASTER_FP_SMALL_BOXSIZE', 'SHAPE_FP_MASTER_MIN_IN_GROUP',
    'SHAPE_MASTER_FIBER', 'SHAPE_NUM_ITERATIONS', 'SHAPE_ORDER_WIDTH',
    'SHAPE_NSECTIONS', 'SHAPE_SIGMACLIP_MAX',
    'SHAPE_LARGE_ANGLE_MIN', 'SHAPE_LARGE_ANGLE_MAX',
    'SHAPE_SMALL_ANGLE_MIN', 'SHAPE_SMALL_ANGLE_MAX',
    'SHAPE_MEDIAN_FILTER_SIZE', 'SHAPE_MIN_GOOD_CORRELATION',
    'SHAPE_SHORT_DX_MEDFILT_WID', 'SHAPE_LONG_DX_MEDFILT_WID',
    'SHAPE_QC_DXMAP_STD', 'SHAPE_PLOT_PER_ORDER',
    'SHAPEOFFSET_XOFFSET', 'SHAPEOFFSET_BOTTOM_PERCENTILE',
    'SHAPEOFFSET_TOP_PERCENTILE', 'SHAPEOFFSET_TOP_FLOOR_FRAC',
    'SHAPEOFFSET_MED_FILTER_WIDTH', 'SHAPEOFFSET_FPINDEX_MAX',
    'SHAPEOFFSET_VALID_FP_LENGTH', 'SHAPEOFFSET_DRIFT_MARGIN',
    'SHAPEOFFSET_WAVEFP_INV_IT', 'SHAPEOFFSET_MASK_BORDER',
    'SHAPEOFFSET_MIN_MAXPEAK_FRAC', 'SHAPEOFFSET_MASK_PIXWIDTH',
    'SHAPEOFFSET_MASK_EXTWIDTH', 'SHAPEOFFSET_DEVIANT_PMIN',
    'SHAPEOFFSET_DEVIANT_PMAX', 'SHAPEOFFSET_FPMAX_NUM_ERROR',
    'SHAPEOFFSET_FIT_HC_SIGMA', 'SHAPEOFFSET_MAXDEV_THRESHOLD',
    'SHAPEOFFSET_ABSDEV_THRESHOLD', 'SHAPE_UNIQUE_FIBERS',
    'SHAPE_DEBUG_OUTPUTS',
    # flat constants
    'FF_BLAZE_HALF_WINDOW', 'FF_BLAZE_THRESHOLD', 'FF_BLAZE_DEGREE',
    'FF_RMS_SKIP_ORDERS', 'QC_FF_MAX_RMS',
    # extract constants
    'EXT_START_ORDER', 'EXT_END_ORDER', 'EXT_RANGE1', 'EXT_RANGE2',
    'EXT_SKIP_ORDERS', 'EXT_COSMIC_CORRETION', 'EXT_COSMIC_SIGCUT',
    'EXT_COSMIC_THRESHOLD', 'QC_EXT_FLUX_MAX',
    'EXT_S1D_WAVESTART', 'EXT_S1D_WAVEEND', 'EXT_S1D_BIN_UWAVE',
    'EXT_S1D_BIN_UVELO', 'EXT_S1D_EDGE_SMOOTH_SIZE',
    'EXT_ALLOWED_BERV_DPRTYPES', 'EXT_BERV_EST_ACC', 'EXT_BERV_KIND',
    # thermal constants
    'THERMAL_ALWAYS_EXTRACT', 'THERMAL_CORRETION_TYPE1',
    'THERMAL_CORRETION_TYPE2', 'THERMAL_ORDER',
    'THERMAL_FILTER_WID', 'THERMAL_RED_LIMIT', 'THERMAL_BLUE_LIMIT',
    'THERMAL_THRES_TAPAS', 'THERMAL_ENVELOPE_PERCENTILE',
    # wave constants
    'WAVE_LINELIST_FILE', 'WAVE_LINELIST_FMT', 'WAVE_LINELIST_AMPCOL',
    'WAVE_LINELIST_COLS', 'WAVE_LINELIST_START', 'WAVE_LINELIST_WAVECOL',
    # telluric constants
    'TAPAS_FILE', 'TAPAS_FILE_FMT', 'TELLU_CUT_BLAZE_NORM'
]

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

# Define core data path
DATA_CORE = Const('DATA_CORE', value=None, dtype=str, source=__NAME__)

# Define whether to force wave solution from calibration database (instead of
#  using header wave solution if available)
CALIB_DB_FORCE_WAVESOL = Const('CALIB_DB_FORCE_WAVESOL', value=None,
                               dtype=bool, source=__NAME__)

# =============================================================================
# COMMON IMAGE SETTINGS
# =============================================================================
# Define the fibers
FIBER_TYPES = Const('FIBER_TYPES', dtype=str, value=None, source=__NAME__)

# Defines whether to by default combine images that are inputted at the same
# time
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
# CALIBRATION: GENERAL SETTINGS
# =============================================================================
# Define the cavity length file (located in the DRS_CALIB_DATA directory)
CAVITY_LENGTH_FILE = Const('CAVITY_LENGTH_FILE', value=None, dtype=str,
                           source=__NAME__)

# Define the cavity length file format (must be astropy.table format)
CAVITY_LENGTH_FILE_FMT = Const('CAVITY_LENGTH_FILE_FMT', value=None,
                               dtype=str, source=__NAME__)

# Define the cavity length file column names (must be separated by commas
# and must be equal to the number of columns in file)
CAVITY_LENGTH_FILE_COLS = Const('CAVITY_LENGTH_FILE_COLS', value=None,
                                dtype=str, source=__NAME__)

# Define the cavity length file row the data starts
CAVITY_LENGTH_FILE_START = Const('CAVITY_LENGTH_FILE_START', value=None,
                                 dtype=str, source=__NAME__)

# Define coefficent column (Must be in CAVITY_LENGTH_FILE_COLS)
CAVITY_LENGTH_FILE_WAVECOL = Const('CAVITY_LENGTH_FILE_WAVECOL', value=None,
                                   dtype=str, source=__NAME__)

# =============================================================================
# CALIBRATION: FIBER SETTINGS
# =============================================================================
# Number of orders to skip at start of image
FIBER_FIRST_ORDER_JUMP_AB = Const('FIBER_FIRST_ORDER_JUMP_AB', value=None,
                                  dtype=int, minimum=0, source=__NAME__)
FIBER_FIRST_ORDER_JUMP_A = Const('FIBER_FIRST_ORDER_JUMP_A', value=None,
                                 dtype=int, minimum=0, source=__NAME__)
FIBER_FIRST_ORDER_JUMP_B = Const('FIBER_FIRST_ORDER_JUMP_B', value=None,
                                 dtype=int, minimum=0, source=__NAME__)
FIBER_FIRST_ORDER_JUMP_C = Const('FIBER_FIRST_ORDER_JUMP_C', value=None,
                                 dtype=int, minimum=0, source=__NAME__)

# Maximum number of order to use
FIBER_MAX_NUM_ORDERS_AB = Const('FIBER_MAX_NUM_ORDERS_AB', value=None,
                                dtype=int, minimum=1, source=__NAME__)
FIBER_MAX_NUM_ORDERS_A = Const('FIBER_MAX_NUM_ORDERS_A', value=None,
                               dtype=int, minimum=1, source=__NAME__)
FIBER_MAX_NUM_ORDERS_B = Const('FIBER_MAX_NUM_ORDERS_B', value=None,
                               dtype=int, minimum=1, source=__NAME__)
FIBER_MAX_NUM_ORDERS_C = Const('FIBER_MAX_NUM_ORDERS_C', value=None,
                               dtype=int, minimum=1, source=__NAME__)

# Number of fibers
FIBER_SET_NUM_FIBERS_AB = Const('FIBER_SET_NUM_FIBERS_AB', value=None,
                                dtype=int, minimum=1, source=__NAME__)
FIBER_SET_NUM_FIBERS_A = Const('FIBER_SET_NUM_FIBERS_A', value=None,
                               dtype=int, minimum=1, source=__NAME__)
FIBER_SET_NUM_FIBERS_B = Const('FIBER_SET_NUM_FIBERS_B', value=None,
                               dtype=int, minimum=1, source=__NAME__)
FIBER_SET_NUM_FIBERS_C = Const('FIBER_SET_NUM_FIBERS_C', value=None,
                               dtype=int, minimum=1, source=__NAME__)

# =============================================================================
# PRE-PROCESSSING SETTINGS
# =============================================================================
# Defines the size around badpixels that is considered part of the bad pixel
PP_CORRUPT_MED_SIZE = Const('PP_CORRUPT_MED_SIZE', value=None, dtype=int,
                            minimum=0, source=__NAME__)

# Defines the threshold (above the full engineering flat) that selects bad
#   (hot) pixels
PP_CORRUPT_HOT_THRES = Const('PP_CORRUPT_HOT_THRES', value=None, dtype=int,
                             minimum=0, source=__NAME__)

# Define the total number of amplifiers
PP_TOTAL_AMP_NUM = Const('PP_TOTAL_AMP_NUM', value=None, dtype=int,
                         minimum=0, source=__NAME__)

# Define the number of dark amplifiers
PP_NUM_DARK_AMP = Const('PP_NUM_DARK_AMP', value=None, dtype=int,
                        minimum=0, source=__NAME__)

# Define the number of bins used in the dark median process         - [cal_pp]
PP_DARK_MED_BINNUM = Const('PP_DARK_MED_BINNUM', value=None, dtype=int,
                           minimum=0, source=__NAME__)

# Defines the full detector flat file (located in the data folder)
PP_FULL_FLAT = Const('PP_FULL_FLAT', value=None, dtype=str, source=__NAME__)

# Define the number of un-illuminated reference pixels at top of image
PP_NUM_REF_TOP = Const('PP_NUM_REF_TOP', value=None, dtype=int,
                       source=__NAME__)

# Define the number of un-illuminated reference pixels at bottom of image
PP_NUM_REF_BOTTOM = Const('PP_NUM_REF_BOTTOM', value=None, dtype=int,
                          source=__NAME__)

# Define the percentile value for the rms normalisation (0-100)
PP_RMS_PERCENTILE = Const('PP_RMS_PERCENTILE', value=None, dtype=int,
                          minimum=0, maximum=100, source=__NAME__)

# Define the lowest rms value of the rms percentile allowed if the value of
#   the pp_rms_percentile-th is lower than this this value is used
PP_LOWEST_RMS_PERCENTILE = Const('PP_LOWEST_RMS_PERCENTILE', value=None,
                                 dtype=float, minimum=0.0, source=__NAME__)

# Defines the snr hotpix threshold to define a corrupt file
PP_CORRUPT_SNR_HOTPIX = Const('PP_CORRUPT_SNR_HOTPIX', value=None, dtype=float,
                              minimum=0.0, source=__NAME__)

# Defines the RMS threshold to also catch corrupt files
PP_CORRUPT_RMS_THRES = Const('PP_CORRUPT_RMS_THRES', value=None, dtype=float,
                             minimum=0.0, source=__NAME__)

# Define rotation angle (must be multiple of 90 degrees)
#       (in degrees counter-clockwise direction)
RAW_TO_PP_ROTATION = Const('RAW_TO_PP_ROTATION', value=None, dtype=int,
                           minimum=0.0, maximum=360.0, source=__NAME__)

# =============================================================================
# CALIBRATION: DARK SETTINGS
# =============================================================================
# Min dark exposure time
QC_DARK_TIME = Const('QC_DARK_TIME', value=None, dtype=float, minimum=0.0,
                     source=__NAME__)

# Max dark median level [ADU/s]
QC_MAX_DARKLEVEL = Const('QC_MAX_DARKLEVEL', value=None, dtype=float,
                         source=__NAME__)

# Max fraction of dark pixels (percent)
QC_MAX_DARK = Const('QC_MAX_DARK', value=None, dtype=float, source=__NAME__)

# Max fraction of dead pixels
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

# Define a bad pixel cut limit (in ADU/s)
DARK_CUTLIMIT = Const('DARK_CUTLIMIT', value=None, dtype=float, source=__NAME__)

# Defines the lower and upper percentiles when measuring the dark
DARK_QMIN = Const('DARK_QMIN', value=None, dtype=int, source=__NAME__,
                  minimum=0, maximum=100)
DARK_QMAX = Const('DARK_QMAX', value=None, dtype=int, source=__NAME__,
                  minimum=0, maximum=100)

# The number of bins in dark histogram
HISTO_BINS = Const('HISTO_BINS', value=None, dtype=int, source=__NAME__,
                   minimum=1)

# The range of the histogram in ADU/s
HISTO_RANGE_LOW = Const('HISTO_RANGE_LOW', value=None, dtype=int,
                        source=__NAME__)
HISTO_RANGE_HIGH = Const('HISTO_RANGE_LOW', value=None, dtype=int,
                         source=__NAME__)

#  Define whether to use SKYDARK for dark corrections
USE_SKYDARK_CORRECTION = Const('USE_SKYDARK_CORRECTION', value=None,
                               dtype=bool, source=__NAME__)

#  If use_skydark_correction is True define whether we use
#     the SKYDARK only or use SKYDARK/DARK (whichever is closest)
USE_SKYDARK_ONLY = Const('USE_SKYDARK_ONLY', value=None, dtype=bool,
                         source=__NAME__)

#  Define the allowed DPRTYPES for finding files for DARK_MASTER will
#      only find those types define by 'filetype' but 'filetype' must
#      be one of theses (strings separated by commas)
ALLOWED_DARK_TYPES = Const('ALLOWED_DARK_TYPES', value=None, dtype=str,
                           source=__NAME__)

# Define the maximum time span to combine dark files over (in hours)
DARK_MASTER_MATCH_TIME = Const('DARK_MASTER_MATCH_TIME', value=None,
                               dtype=float, source=__NAME__)

# median filter size for dark master
DARK_MASTER_MED_SIZE = Const('DARK_MASTER_MED_SIZE', value=None, dtype=int,
                             source=__NAME__)

# =============================================================================
# CALIBRATION: BAD PIXEL MAP SETTINGS
# =============================================================================
# Defines the full detector flat file (located in the data folder)
BADPIX_FULL_FLAT = Const('BADPIX_FULL_FLAT', value=None, dtype=str,
                         source=__NAME__)

# Percentile to normalise to when normalising and median filtering
#    image [percentage]
BADPIX_NORM_PERCENTILE = Const('BADPIX_NORM_PERCENTILE', value=None,
                               dtype=float, source=__NAME__,
                               minimum=0.0, maximum=100.0)

# Define the median image in the x dimension over a boxcar of this width
BADPIX_FLAT_MED_WID = Const('BADPIX_FLAT_MED_WID', value=None, dtype=int,
                            source=__NAME__, minimum=0)

# Define the maximum differential pixel cut ratio
BADPIX_FLAT_CUT_RATIO = Const('BADPIX_FLAT_CUT_RATIO', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

# Define the illumination cut parameter
BADPIX_ILLUM_CUT = Const('BADPIX_ILLUM_CUT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

# Define the maximum flux in ADU/s to be considered too hot to be used
BADPIX_MAX_HOTPIX = Const('BADPIX_MAX_HOTPIX', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

# Defines the threshold on the full detector flat file to deem pixels as good
BADPIX_FULL_THRESHOLD = Const('BADPIX_FULL_THRESHOLD', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

# =============================================================================
# CALIBRATION: BACKGROUND CORRECTION SETTINGS
# =============================================================================
#  Width of the box to produce the background mask
BKGR_BOXSIZE = Const('BKGR_BOXSIZE', value=None, dtype=int,
                     source=__NAME__, minimum=0)

#  Do background percentile to compute minimum value (%)
BKGR_PERCENTAGE = Const('BKGR_PERCENTAGE', value=None, dtype=float,
                        source=__NAME__, minimum=0.0, maximum=100.0)

#  Size in pixels of the convolve tophat for the background mask
BKGR_MASK_CONVOLVE_SIZE = Const('BKGR_MASK_CONVOLVE_SIZE', value=None,
                                dtype=int, source=__NAME__, minimum=0)

#  If a pixel has this or more "dark" neighbours, we consider it dark
#      regardless of its initial value
BKGR_N_BAD_NEIGHBOURS = Const('BKGR_N_BAD_NEIGHBOURS', value=None, dtype=int,
                              source=__NAME__, minimum=0)

#  Do not correct for background measurement (True or False)
BKGR_NO_SUBTRACTION = Const('BKGR_NO_SUBTRACTION', value=None, dtype=bool,
                            source=__NAME__)

#  Kernel amplitude determined from drs_local_scatter.py
BKGR_KER_AMP = Const('BKGR_KER_AMP', value=None, dtype=float, source=__NAME__)

#  Background kernel width in in x and y [pixels]
BKGR_KER_WX = Const('BKGR_KER_WX', value=None, dtype=int, source=__NAME__)
BKGR_KER_WY = Const('BKGR_KER_WY', value=None, dtype=int, source=__NAME__)

#  construct a convolution kernel. We go from -IC_BKGR_KER_SIG to
#      +IC_BKGR_KER_SIG sigma in each direction. Its important no to
#      make the kernel too big as this slows-down the 2D convolution.
#      Do NOT make it a -10 to +10 sigma gaussian!
BKGR_KER_SIG = Const('BKGR_KER_SIG', value=None, dtype=float, source=__NAME__)

# =============================================================================
# CALIBRATION: LOCALISATION SETTINGS
# =============================================================================
# Size of the order_profile smoothed box
#   (from pixel - size to pixel + size)
LOC_ORDERP_BOX_SIZE = Const('LOC_ORDERP_BOX_SIZE', value=None, dtype=int,
                            source=__NAME__)

# row number of image to start localisation processing at
LOC_START_ROW_OFFSET = Const('LOC_START_ROW_OFFSET', value=None, dtype=int,
                             source=__NAME__, minimum=0)

# Definition of the central column for use in localisation
LOC_CENTRAL_COLUMN = Const('LOC_CENTRAL_COLUMN', value=None, dtype=int,
                           source=__NAME__, minimum=0)

# Half spacing between orders
LOC_HALF_ORDER_SPACING = Const('LOC_HALF_ORDER_SPACING', value=None,
                               dtype=int, source=__NAME__, minimum=0)

# Minimum amplitude to accept (in e-)
LOC_MINPEAK_AMPLITUDE = Const('LOC_MINPEAK_AMPLITUDE', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

# Normalised amplitude threshold to accept pixels for background calculation
LOC_BKGRD_THRESHOLD = Const('LOC_BKGRD_THRESHOLD', value=None, dtype=float,
                            source=__NAME__, minimum=0.0)

# Define the amount we drop from the centre of the order when
#    previous order center is missed (in finding the position)
LOC_ORDER_CURVE_DROP = Const('LOC_ORDER_CURVE_DROP', value=None, dtype=float,
                             source=__NAME__, minimum=0.0)

# Order of polynomial to fit for widths
LOC_WIDTH_POLY_DEG = Const('LOC_WIDTH_POLY_DEG', value=None, dtype=int,
                           source=__NAME__, minimum=1)

# Order of polynomial to fit for positions
LOC_CENT_POLY_DEG = Const('LOC_CENT_POLY_DEG', value=None, dtype=int,
                          source=__NAME__, minimum=1)

# Define the column separation for fitting orders
LOC_COLUMN_SEP_FITTING = Const('LOC_COLUMN_SEP_FITTING', value=None, dtype=int,
                               source=__NAME__, minimum=1)

# Definition of the extraction window size (half size)
LOC_EXT_WINDOW_SIZE = Const('LOC_EXT_WINDOW_SIZE', value=None, dtype=int,
                            source=__NAME__, minimum=1)

# Definition of the gap index in the selected area
LOC_IMAGE_GAP = Const('LOC_IMAGE_GAP', value=None, dtype=int, source=__NAME__,
                      minimum=0)

# Define minimum width of order to be accepted
LOC_ORDER_WIDTH_MIN = Const('LOC_ORDER_WIDTH_MIN', value=None, dtype=float,
                            source=__NAME__, minimum=0.0)

# Define the noise multiplier threshold in order to accept an
#     order center as usable i.e.
#     max(pixel value) - min(pixel value) > THRES * RDNOISE
LOC_NOISE_MULTIPLIER_THRES = Const('LOC_NOISE_MULTIPLIER_THRES', value=None,
                                   dtype=float, source=__NAME__, minimum=0.0)

# Maximum rms for sigma-clip order fit (center positions)
LOC_MAX_RMS_CENT = Const('LOC_MAX_RMS_CENT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

# Maximum peak-to-peak for sigma-clip order fit (center positions)
LOC_MAX_PTP_CENT = Const('LOC_MAX_PTP_CENT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

# Maximum frac ptp/rms for sigma-clip order fit (center positions)
LOC_PTPORMS_CENT = Const('LOC_PTPORMS_CENT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

# Maximum rms for sigma-clip order fit (width)
LOC_MAX_RMS_WID = Const('LOC_MAX_RMS_WID', value=None, dtype=float,
                        source=__NAME__, minimum=0.0)

# Maximum fractional peak-to-peak for sigma-clip order fit (width)
LOC_MAX_PTP_WID = Const('LOC_MAX_PTP_WID', value=None, dtype=float,
                        source=__NAME__, minimum=0.0)

# Saturation threshold for localisation
LOC_SAT_THRES = Const('LOC_SAT_THRES', value=None, dtype=float, source=__NAME__,
                      minimum=0.0)

# Maximum points removed in location fit
QC_LOC_MAXFIT_REMOVED_CTR = Const('QC_LOC_MAXFIT_REMOVED_CTR', value=None,
                                  dtype=int, source=__NAME__, minimum=0)

# Maximum points removed in width fit
QC_LOC_MAXFIT_REMOVED_WID = Const('QC_LOC_MAXFIT_REMOVED_WID', value=None,
                                  dtype=int, source=__NAME__, minimum=0)

# Maximum rms allowed in fitting location
QC_LOC_RMSMAX_CTR = Const('QC_LOC_RMSMAX_CTR', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

# Maximum rms allowed in fitting width
QC_LOC_RMSMAX_WID = Const('QC_LOC_RMSMAX_WID', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

# Option for archiving the location image
LOC_SAVE_SUPERIMP_FILE = Const('LOC_SAVE_SUPERIMP_FILE', value=None,
                               dtype=bool, source=__NAME__)

# =============================================================================
# CALIBRATION: SHAPE SETTINGS
# =============================================================================
#  Define the allowed DPRTYPES for finding files for SHAPE_MASTER will
#      only find those types define by 'filetype' but 'filetype' must
#      be one of theses (strings separated by commas)
ALLOWED_FP_TYPES = Const('ALLOWED_FP_TYPES', value=None, dtype=str,
                         source=__NAME__)

# Define the maximum time span to combine fp files over (in hours)
FP_MASTER_MATCH_TIME = Const('FP_MASTER_MATCH_TIME', value=None,
                             dtype=float, source=__NAME__)

# Define the percentile at which the FPs are normalised when getting the
#    fp master in shape master
FP_MASTER_PERCENT_THRES = Const('FP_MASTER_PERCENT_THRES', value=None,
                                dtype=float, minimum=0, maximum=100,
                                source=__NAME__)

#  Define the largest standard deviation allowed for the shift in
#   x or y when doing the shape master fp linear transform
SHAPE_QC_LTRANS_RES_THRES = Const('SHAPE_QC_LTRANS_RES_THRES', value=None,
                                  dtype=float, source=__NAME__)

#  Define the percentile which defines a true FP peak [0-100]
SHAPE_MASTER_VALIDFP_PERCENTILE = Const('SHAPE_MASTER_VALIDFP_PERCENTILE',
                                        value=None, dtype=float, minimum=0,
                                        maximum=100, source=__NAME__)

#  Define the fractional flux an FP much have compared to its neighbours
SHAPE_MASTER_VALIDFP_THRESHOLD = Const('SHAPE_MASTER_VALIDFP_THRESHOLD',
                                       value=None, dtype=float, minimum=0,
                                       source=__NAME__)

#  Define the number of iterations used to get the linear transform params
SHAPE_MASTER_LINTRANS_NITER = Const('SHAPE_MASTER_LINTRANS_NITER', value=None,
                                    dtype=int, minimum=1, source=__NAME__)

#  Define the initial search box size (in pixels) around the fp peaks
SHAPE_MASTER_FP_INI_BOXSIZE = Const('SHAPE_MASTER_FP_INI_BOXSIZE', value=None,
                                    dtype=int, minimum=1, source=__NAME__)

#  Define the small search box size (in pixels) around the fp peaks
SHAPE_MASTER_FP_SMALL_BOXSIZE = Const('SHAPE_MASTER_FP_SMALL_BOXSIZE',
                                      value=None, dtype=int, minimum=1,
                                      source=__NAME__)

#  Define the minimum number of FP files in a group to mean group is valid
SHAPE_FP_MASTER_MIN_IN_GROUP = Const('SHAPE_FP_MASTER_MIN_IN_GROUP', value=None,
                                     dtype=int, minimum=1, source=__NAME__)

#  Define which fiber should be used for fiber-dependent calibrations in
#   shape master
SHAPE_MASTER_FIBER = Const('SHAPE_MASTER_FIBER', value=None, dtype=str,
                           source=__NAME__)

# The number of iterations to run the shape finding out to
SHAPE_NUM_ITERATIONS = Const('SHAPE_NUM_ITERATIONS', value=None, dtype=int,
                             minimum=1, source=__NAME__)

# width of the ABC fibers (in pixels)
SHAPE_ORDER_WIDTH = Const('SHAPE_ORDER_WIDTH', value=None, dtype=int,
                          minimum=1, source=__NAME__)

# number of sections per order to split the order into
SHAPE_NSECTIONS = Const('SHAPE_NSECTIONS', value=None, dtype=int,
                        minimum=1, source=__NAME__)

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
SHAPE_LARGE_ANGLE_MIN = Const('SHAPE_LARGE_ANGLE_MIN', value=None,
                              dtype=float, source=__NAME__)
SHAPE_LARGE_ANGLE_MAX = Const('SHAPE_LARGE_ANGLE_MAX', value=None,
                              dtype=float, source=__NAME__)
SHAPE_SMALL_ANGLE_MIN = Const('SHAPE_SMALL_ANGLE_MIN', value=None,
                              dtype=float, source=__NAME__)
SHAPE_SMALL_ANGLE_MAX = Const('SHAPE_SMALL_ANGLE_MAX', value=None,
                              dtype=float, source=__NAME__)

# max sigma clip (in sigma) on points within a section
SHAPE_SIGMACLIP_MAX = Const('SHAPE_SIGMACLIP_MAX', value=None, dtype=float,
                            minimum=0.0, source=__NAME__)

# the size of the median filter to apply along the order (in pixels)
SHAPE_MEDIAN_FILTER_SIZE = Const('SHAPE_MEDIAN_FILTER_SIZE', value=None,
                                 dtype=int, minimum=0, source=__NAME__)

# The minimum value for the cross-correlation to be deemed good
SHAPE_MIN_GOOD_CORRELATION = Const('SHAPE_MIN_GOOD_CORRELATION', value=None,
                                   dtype=float, minimum=0.0, source=__NAME__)

# Define the first pass (short) median filter width for dx
SHAPE_SHORT_DX_MEDFILT_WID = Const('SHAPE_SHORT_DX_MEDFILT_WID', value=None,
                                   dtype=int, source=__NAME__)

# Define the second pass (long) median filter width for dx.
#  Used to fill NaN positions in dx that are not covered by short pass
SHAPE_LONG_DX_MEDFILT_WID = Const('SHAPE_SHORT_DX_MEDFILT_WID', value=None,
                                  dtype=int, source=__NAME__)

#  Defines the largest allowed standard deviation for a given
#  per-order and per-x-pixel shift of the FP peaks
SHAPE_QC_DXMAP_STD = Const('SHAPE_QC_DXMAP_STD', value=None, dtype=int,
                           source=__NAME__)

#  Defines whether to plot the debug plot per order (this creates many plots)
SHAPE_PLOT_PER_ORDER = Const('SHAPE_PLOT_PER_ORDER', value=None, dtype=bool,
                             source=__NAME__)

# defines the shape offset xoffset (before and after) fp peaks
SHAPEOFFSET_XOFFSET = Const('SHAPEOFFSET_XOFFSET', value=None, dtype=int,
                            source=__NAME__)

# defines the bottom percentile for fp peak
SHAPEOFFSET_BOTTOM_PERCENTILE = Const('SHAPEOFFSET_BOTTOM_PERCENTILE',
                                      value=None, dtype=float, source=__NAME__)

# defines the top percentile for fp peak
SHAPEOFFSET_TOP_PERCENTILE = Const('SHAPEOFFSET_TOP_PERCENTILE', value=None,
                                   dtype=float, source=__NAME__)

# defines the floor below which top values should be set to
# this fraction away from the max top value
SHAPEOFFSET_TOP_FLOOR_FRAC = Const('SHAPEOFFSET_TOP_FLOOR_FRAC', value=None,
                                   dtype=float, source=__NAME__)

# define the median filter to apply to the hc (high pass filter)]
SHAPEOFFSET_MED_FILTER_WIDTH = Const('SHAPEOFFSET_MED_FILTER_WIDTH',
                                     value=None, dtype=int, source=__NAME__)

# Maximum number of FP (larger than expected number
#    (~10000 to ~25000)
SHAPEOFFSET_FPINDEX_MAX = Const('SHAPEOFFSET_FPINDEX_MAX', value=None,
                                dtype=int, source=__NAME__,
                                minimum=10000, maximum=25000)

# Define the valid length of a FP peak
SHAPEOFFSET_VALID_FP_LENGTH = Const('SHAPEOFFSET_VALID_FP_LENGTH', value=None,
                                    dtype=int, source=__NAME__)

# Define the maximum allowed offset (in nm) that we allow for
#   the detector)
SHAPEOFFSET_DRIFT_MARGIN = Const('SHAPEOFFSET_DRIFT_MARGIN', value=None,
                                 dtype=float, source=__NAME__)

# Define the number of iterations to do for the wave_fp
#   inversion trick
SHAPEOFFSET_WAVEFP_INV_IT = Const('SHAPEOFFSET_WAVEFP_INV_IT',
                                  value=None, dtype=int, source=__NAME__)

# Define the border in pixels at the edge of the detector
SHAPEOFFSET_MASK_BORDER = Const('SHAPEOFFSET_MASK_BORDER', value=None,
                                dtype=int, source=__NAME__)

# Define the minimum maxpeak value as a fraction of the
#  maximum maxpeak
SHAPEOFFSET_MIN_MAXPEAK_FRAC = Const('SHAPEOFFSET_MIN_MAXPEAK_FRAC', value=None,
                                     dtype=float, source=__NAME__)

# Define the width of the FP mask (+/- the center)
SHAPEOFFSET_MASK_PIXWIDTH = Const('SHAPEOFFSET_MASK_PIXWIDTH', value=None,
                                  dtype=int, source=__NAME__)

# Define the width of the FP to extract (+/- the center)
SHAPEOFFSET_MASK_EXTWIDTH = Const('SHAPEOFFSET_MASK_EXTWIDTH', value=None,
                                  dtype=int, source=__NAME__)

# Define the most deviant peaks - percentile from [min to max]
SHAPEOFFSET_DEVIANT_PMIN = Const('SHAPEOFFSET_DEVIANT_PMIN', value=None,
                                 dtype=float, minimum=0, maximum=100,
                                 source=__NAME__)
SHAPEOFFSET_DEVIANT_PMAX = Const('SHAPEOFFSET_DEVIANT_PMAX', value=None,
                                 dtype=float, minimum=0, maximum=100,
                                 source=__NAME__)

# Define the maximum error in FP order assignment
#  we assume that the error in FP order assignment could range
#  from -50 to +50 in practice, it is -1, 0 or +1 for the cases we've
#  tested to date
SHAPEOFFSET_FPMAX_NUM_ERROR = Const('SHAPEOFFSET_FPMAX_NUM_ERROR', value=None,
                                    dtype=int, source=__NAME__)

# The number of sigmas that the HC spectrum is allowed to be
#   away from the predicted (from FP) position
SHAPEOFFSET_FIT_HC_SIGMA = Const('SHAPEOFFSET_FIT_HC_SIGMA', value=None,
                                 dtype=float, source=__NAME__)

# Define the maximum allowed maximum absolute deviation away
#   from the error fit
SHAPEOFFSET_MAXDEV_THRESHOLD = Const('SHAPEOFFSET_MAXDEV_THRESHOLD', value=None,
                                     dtype=float, source=__NAME__)

# very low thresholding values tend to clip valid points
SHAPEOFFSET_ABSDEV_THRESHOLD = Const('SHAPEOFFSET_ABSDEV_THRESHOLD', value=None,
                                     dtype=float, source=__NAME__)

# define the names of the unique fibers (i.e. not AB) for use in
#   getting the localisation coefficients for dymap
SHAPE_UNIQUE_FIBERS = Const('SHAPE_UNIQUE_FIBERS', value=None, dtype=str,
                            source=__NAME__)

#  Define whether to output debug (sanity check) files
SHAPE_DEBUG_OUTPUTS = Const('SHAPE_DEBUG_OUTPUTS', value=None, dtype=bool,
                            source=__NAME__)

# =============================================================================
# CALIBRATION: FLAT SETTINGS
# =============================================================================
#  Half size blaze smoothing window
FF_BLAZE_HALF_WINDOW = Const('FF_BLAZE_HALF_WINDOW', value=None, dtype=int,
                             source=__NAME__)

# Minimum relative e2ds flux for the blaze computation
FF_BLAZE_THRESHOLD = Const('FF_BLAZE_THRESHOLD', value=None, dtype=float,
                           source=__NAME__)

#  The blaze polynomial fit degree
FF_BLAZE_DEGREE = Const('FF_BLAZE_DEGREE', value=None, dtype=int,
                        source=__NAME__)

# Define the orders not to plot on the RMS plot should be a string
#     containing a list of integers
FF_RMS_SKIP_ORDERS = Const('FF_RMS_SKIP_ORDERS', value=None, dtype=str,
                           source=__NAME__)

# Maximum allowed RMS of flat field
QC_FF_MAX_RMS = Const('QC_FF_MAX_RMS', value=None, dtype=float, source=__NAME__)

# =============================================================================
# CALIBRATION: EXTRACTION SETTINGS
# =============================================================================
#  Start order of the extraction in cal_ff if None starts from 0
EXT_START_ORDER = Const('EXT_START_ORDER', value=None, dtype=None,
                        source=__NAME__)

#  End order of the extraction in cal_ff if None ends at last order
EXT_END_ORDER = Const('EXT_END_ORDER', value=None, dtype=None,
                      source=__NAME__)

# Half-zone extraction width left side (formally plage1)
EXT_RANGE1 = Const('EXT_RANGE1', value=None, dtype=str, source=__NAME__)

# Half-zone extraction width right side (formally plage2)
EXT_RANGE2 = Const('EXT_RANGE2', value=None, dtype=str, source=__NAME__)

# Define the orders to skip extraction on (will set all order values
#    to NaN. If None no orders are skipped. If Not None should be a
#    string (valid python list)
EXT_SKIP_ORDERS = Const('EXT_SKIP_ORDERS', value=None, dtype=str,
                        source=__NAME__)

#  Defines whether to run extraction with cosmic correction
EXT_COSMIC_CORRETION = Const('EXT_COSMIC_CORRETION', value=None, dtype=bool,
                             source=__NAME__)

#  Define the percentage of flux above which we use to cut
EXT_COSMIC_SIGCUT = Const('EXT_COSMIC_SIGCUT', value=None, dtype=float,
                          source=__NAME__)

#  Defines the maximum number of iterations we use to check for cosmics
#      (for each pixel)
EXT_COSMIC_THRESHOLD = Const('EXT_COSMIC_THRESHOLD', value=None, dtype=int,
                             source=__NAME__)

# Saturation level reached warning
QC_EXT_FLUX_MAX = Const('QC_EXT_FLUX_MAX', value=None, dtype=float,
                        source=__NAME__)

# Define the start s1d wavelength (in nm)
EXT_S1D_WAVESTART = Const('EXT_S1D_WAVESTART', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

# Define the end s1d wavelength (in nm)
EXT_S1D_WAVEEND = Const('EXT_S1D_WAVEEND', value=None, dtype=float,
                            source=__NAME__, minimum=0.0)

#  Define the s1d spectral bin for S1D spectra (nm) when uniform in wavelength
EXT_S1D_BIN_UWAVE = Const('EXT_S1D_BIN_UWAVE', value=None, dtype=float,
                            source=__NAME__, minimum=0.0)

#  Define the s1d spectral bin for S1D spectra (km/s) when uniform in velocity
EXT_S1D_BIN_UVELO = Const('EXT_S1D_BIN_UVELO', value=None, dtype=float,
                            source=__NAME__, minimum=0.0)

#  Define the s1d smoothing kernel for the transition between orders in pixels
EXT_S1D_EDGE_SMOOTH_SIZE = Const('EXT_S1D_EDGE_SMOOTH_SIZE', value=None,
                                 dtype=int, source=__NAME__, minimum=0)

#    Define dprtypes to calculate berv for
EXT_ALLOWED_BERV_DPRTYPES = Const('EXT_ALLOWED_BERV_DPRTYPES', value=None,
                                  dtype=str, source=__NAME__)

#    Define which BERV calculation to use ('barycorrpy' or 'estimate' or 'None')
EXT_BERV_KIND = Const('EXT_BERV_KIND', value=None, dtype=str, source=__NAME__,
                      options=['barycorrpy', 'estimate', 'None'])

#    Define the accuracy of the estimate (for logging only) [m/s]
EXT_BERV_EST_ACC = Const('EXT_BERV_EST_ACC', value=None, dtype=float,
                         source=__NAME__)


# =============================================================================
# CALIBRATION: THERMAL SETTINGS
# =============================================================================
# define whether to always extract thermals (i.e. overwrite existing files)
THERMAL_ALWAYS_EXTRACT = Const('THERMAL_ALWAYS_EXTRACT', value=None,
                               dtype=bool, source=__NAME__)

# define DPRTYPEs we need to correct thermal background using
#  telluric absorption (TAPAS)
THERMAL_CORRETION_TYPE1 = Const('THERMAL_CORRETION_TYPE1', value=None,
                                dtype=str, source=__NAME__)

# define DPRTYPEs we need to correct thermal background using
#   method 2
THERMAL_CORRETION_TYPE2 = Const('THERMAL_CORRETION_TYPE2', value=None,
                                dtype=str, source=__NAME__)

# define the order to perform the thermal background scaling on
THERMAL_ORDER = Const('THERMAL_ORDER', value=None, dtype=int, source=__NAME__)

# width of the median filter used for the background
THERMAL_FILTER_WID = Const('THERMAL_FILTER_WID', value=None, dtype=int,
                           source=__NAME__)

# define thermal red limit (in nm)
THERMAL_RED_LIMIT = Const('THERMAL_RED_LIMIT', value=None, dtype=float,
                          source=__NAME__)

# define thermal blue limit (in nm)
THERMAL_BLUE_LIMIT = Const('THERMAL_BLUE_LIMIT', value=None, dtype=float,
                           source=__NAME__)

# maximum tapas transmission to be considered completely opaque for the
# purpose of background determination in order 49.
THERMAL_THRES_TAPAS = Const('THERMAL_THRES_TAPAS', value=None, dtype=float,
                            source=__NAME__)

# define the percentile to measure the background for correction type 2
THERMAL_ENVELOPE_PERCENTILE = Const('THERMAL_ENVELOPE_PERCENTILE', value=None,
                                    dtype=float, source=__NAME__,
                                    minimum=0, maximum=100)


# =============================================================================
# CALIBRATION: WAVE SETTINGS
# =============================================================================
# Define the line list file (located in the DRS_WAVE_DATA directory)
WAVE_LINELIST_FILE = Const('WAVE_LINELIST_FILE', value=None, dtype=str,
                           source=__NAME__)

# Define the line list file format (must be astropy.table format)
WAVE_LINELIST_FMT = Const('WAVE_LINELIST_FMT', value=None, dtype=str,
                          source=__NAME__)

# Define the line list file column names (must be separated by commas
# and must be equal to the number of columns in file)
WAVE_LINELIST_COLS = Const('WAVE_LINELIST_COLS', value=None, dtype=str,
                           source=__NAME__)

# Define the line list file row the data starts
WAVE_LINELIST_START = Const('WAVE_LINELIST_START', value=None, dtype=str,
                            source=__NAME__)

# Define the line list file wavelength column and amplitude column
#  Must be in WAVE_LINELIST_COLS
WAVE_LINELIST_WAVECOL = Const('WAVE_LINELIST_WAVECOL', value=None, dtype=str,
                              source=__NAME__)
WAVE_LINELIST_AMPCOL = Const('WAVE_LINELIST_AMPCOL', value=None, dtype=str,
                             source=__NAME__)

# =============================================================================
# CALIBRATION: TELLURIC SETTINGS
# =============================================================================
# Define the name of the tapas file to use
TAPAS_FILE = Const('TAPAS_FILE', value=None, dtype=str, source=__NAME__)

# Define the format (astropy format) of the tapas file "TAPAS_FILE"
TAPAS_FILE_FMT = Const('TAPAS_FILE_FMT', value=None, dtype=str, source=__NAME__)

# Define level above which the blaze is high enough to accurately
#    measure telluric
TELLU_CUT_BLAZE_NORM = Const('TELLU_CUT_BLAZE_NORM', value=None, dtype=float,
                             source=__NAME__)

