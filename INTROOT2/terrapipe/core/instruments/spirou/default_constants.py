"""


Created on 2019-01-17

@author: cook
"""
from terrapipe.core.instruments.default.default_constants import *

# TODO: Note: If variables are not showing up MUST CHECK __all__ definition
# TODO:    in import * module

__NAME__ = 'config.instruments.spirou.default_constants.py'

# =============================================================================
# Spirou Constant definitions
# =============================================================================

# =============================================================================
# DRS DATA SETTINGS
# =============================================================================
# Define the data engineering path
DATA_ENGINEERING = DATA_ENGINEERING.copy(__NAME__)
DATA_ENGINEERING.value = './data/spirou/engineering/'

# Define whether to force wave solution from calibration database (instead of
#    using header wave solution if available)
CALIB_DB_FORCE_WAVESOL = CALIB_DB_FORCE_WAVESOL.copy(__NAME__)
CALIB_DB_FORCE_WAVESOL.value = False


# =============================================================================
# COMMON IMAGE SETTINGS
# =============================================================================
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
IMAGE_Y_LOW.value = 250
IMAGE_Y_HIGH = IMAGE_Y_HIGH.copy(__NAME__)
IMAGE_Y_HIGH.value = 3350


# =============================================================================
# CALIBRATION: GENERAL SETTINGS
# =============================================================================
# Define the cavity length file (located in the DRS_CALIB_DATA directory)
CAVITY_LENGTH_FILE = CAVITY_LENGTH_FILE.copy(__NAME__)
CAVITY_LENGTH_FILE.value = 'cavity_length.dat'

# Define the cavity length file format (must be astropy.table format)
CAVITY_LENGTH_FILE_FMT = CAVITY_LENGTH_FILE_FMT.copy(__NAME__)
CAVITY_LENGTH_FILE_FMT.value = 'ascii'

# Define the cavity length file column names (must be separated by commas
#   and must be equal to the number of columns in file)
CAVITY_LENGTH_FILE_COLS = CAVITY_LENGTH_FILE_COLS.copy(__NAME__)
CAVITY_LENGTH_FILE_COLS.value = 'NTH_ORDER, WAVELENGTH_COEFF'

# Define the cavity length file row the data starts
CAVITY_LENGTH_FILE_START = CAVITY_LENGTH_FILE_START.copy(__NAME__)
CAVITY_LENGTH_FILE_START.value = 0

# Define coefficent column
#    Must be in CAVITY_LENGTH_FILE_COLS
CAVITY_LENGTH_FILE_WAVECOL = CAVITY_LENGTH_FILE_WAVECOL.copy(__NAME__)
CAVITY_LENGTH_FILE_WAVECOL.value = 'WAVELENGTH_COEFF'


# =============================================================================
# CALIBRATION: FIBER SETTINGS
# =============================================================================
# Note new fiber settings musts also be added to pseudo_const
#   in the "FIBER_SETTINGS" function i.e.
#            keys = ['FIBER_FIRST_ORDER_JUMP', 'FIBER_MAX_NUM_ORDERS',
#                    'FIBER_SET_NUM_FIBERS']

#   Number of orders to skip at start of image
FIBER_FIRST_ORDER_JUMP_AB = FIBER_FIRST_ORDER_JUMP_AB.copy(__NAME__)
FIBER_FIRST_ORDER_JUMP_A = FIBER_FIRST_ORDER_JUMP_A.copy(__NAME__)
FIBER_FIRST_ORDER_JUMP_B = FIBER_FIRST_ORDER_JUMP_B.copy(__NAME__)
FIBER_FIRST_ORDER_JUMP_C = FIBER_FIRST_ORDER_JUMP_C.copy(__NAME__)
# set values
FIBER_FIRST_ORDER_JUMP_AB.value = 2
FIBER_FIRST_ORDER_JUMP_A.value = 0
FIBER_FIRST_ORDER_JUMP_B.value = 0
FIBER_FIRST_ORDER_JUMP_C.value = 1

#   Maximum number of order to use
FIBER_MAX_NUM_ORDERS_AB = FIBER_MAX_NUM_ORDERS_AB.copy(__NAME__)
FIBER_MAX_NUM_ORDERS_A = FIBER_MAX_NUM_ORDERS_A.copy(__NAME__)
FIBER_MAX_NUM_ORDERS_B = FIBER_MAX_NUM_ORDERS_B.copy(__NAME__)
FIBER_MAX_NUM_ORDERS_C = FIBER_MAX_NUM_ORDERS_C.copy(__NAME__)
# set values
FIBER_MAX_NUM_ORDERS_AB.value = 98
FIBER_MAX_NUM_ORDERS_A.value = 49
FIBER_MAX_NUM_ORDERS_B.value = 49
FIBER_MAX_NUM_ORDERS_C.value = 49

#   Number of fibers
FIBER_SET_NUM_FIBERS_AB = FIBER_SET_NUM_FIBERS_AB.copy(__NAME__)
FIBER_SET_NUM_FIBERS_A = FIBER_SET_NUM_FIBERS_A.copy(__NAME__)
FIBER_SET_NUM_FIBERS_B = FIBER_SET_NUM_FIBERS_B.copy(__NAME__)
FIBER_SET_NUM_FIBERS_C =FIBER_SET_NUM_FIBERS_C.copy(__NAME__)
# set values
FIBER_SET_NUM_FIBERS_AB.value = 2
FIBER_SET_NUM_FIBERS_A.value = 1
FIBER_SET_NUM_FIBERS_B.value = 1
FIBER_SET_NUM_FIBERS_C.value = 1

# =============================================================================
# PRE-PROCESSSING SETTINGS
# =============================================================================
# Defines the size around badpixels that is considered part of the bad pixel
PP_CORRUPT_MED_SIZE = PP_CORRUPT_MED_SIZE.copy(__NAME__)
PP_CORRUPT_MED_SIZE.value = 2

# Defines the threshold (above the full engineering flat) that selects bad 
#     (hot) pixels
PP_CORRUPT_HOT_THRES = PP_CORRUPT_HOT_THRES.copy(__NAME__)
PP_CORRUPT_HOT_THRES.value = 2

#   Define the total number of amplifiers
PP_TOTAL_AMP_NUM = PP_TOTAL_AMP_NUM.copy(__NAME__)
PP_TOTAL_AMP_NUM.value = 32

#   Define the number of dark amplifiers
PP_NUM_DARK_AMP = PP_NUM_DARK_AMP.copy(__NAME__)
PP_NUM_DARK_AMP.value = 5

#   Define the number of bins used in the dark median process
PP_DARK_MED_BINNUM = PP_DARK_MED_BINNUM.copy(__NAME__)
PP_DARK_MED_BINNUM.value = 32

#   Defines the full detector flat file (located in the data folder)
PP_FULL_FLAT = PP_FULL_FLAT.copy(__NAME__)
PP_FULL_FLAT.value = 'detector_flat_full.fits'

#   Define the number of un-illuminated reference pixels at top of image
PP_NUM_REF_TOP = PP_NUM_REF_TOP.copy(__NAME__)
PP_NUM_REF_TOP.value = 4

#   Define the number of un-illuminated reference pixels at bottom of image
PP_NUM_REF_BOTTOM = PP_NUM_REF_BOTTOM.copy(__NAME__)
PP_NUM_REF_BOTTOM.value = 4

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
PP_CORRUPT_RMS_THRES.value = 0.15

#   Define rotation angle (must be multiple of 90 degrees)
#         (in degrees counter-clockwise direction)
RAW_TO_PP_ROTATION = RAW_TO_PP_ROTATION.copy(__NAME__)
RAW_TO_PP_ROTATION.value = -90

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
IMAGE_X_BLUE_LOW.value = 4
IMAGE_X_BLUE_HIGH = IMAGE_X_BLUE_HIGH.copy(__NAME__)
IMAGE_X_BLUE_HIGH.value = 4092
IMAGE_Y_BLUE_LOW = IMAGE_Y_BLUE_LOW.copy(__NAME__)
IMAGE_Y_BLUE_LOW.value = 250
IMAGE_Y_BLUE_HIGH = IMAGE_Y_BLUE_HIGH.copy(__NAME__)
IMAGE_Y_BLUE_HIGH.value = 3350

# Defines the red resized image
IMAGE_X_RED_LOW = IMAGE_X_RED_LOW.copy(__NAME__)
IMAGE_X_RED_LOW.value = 4
IMAGE_X_RED_HIGH = IMAGE_X_RED_HIGH.copy(__NAME__)
IMAGE_X_RED_HIGH.value = 4092
IMAGE_Y_RED_LOW = IMAGE_Y_RED_LOW.copy(__NAME__)
IMAGE_Y_RED_LOW.value = 250
IMAGE_Y_RED_HIGH = IMAGE_Y_RED_HIGH.copy(__NAME__)
IMAGE_Y_RED_HIGH.value = 3350

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

#    Define whether to use SKYDARK for dark corrections
USE_SKYDARK_CORRECTION = USE_SKYDARK_CORRECTION.copy(__NAME__)
USE_SKYDARK_CORRECTION.value = False

#    If use_skydark_correction is True define whether we use
#       the SKYDARK only or use SKYDARK/DARK (whichever is closest)
USE_SKYDARK_ONLY = USE_SKYDARK_ONLY.copy(__NAME__)
USE_SKYDARK_ONLY.value = False

#    Define the allowed DPRTYPES for finding files for DARK_MASTER will
#        only find those types define by 'filetype' but 'filetype' must
#        be one of theses (strings separated by commas)
ALLOWED_DARK_TYPES = ALLOWED_DARK_TYPES.copy(__NAME__)
ALLOWED_DARK_TYPES.value = 'DARK_DARK'

#   Define the maximum time span to combine dark files over (in hours)
DARK_MASTER_MATCH_TIME = DARK_MASTER_MATCH_TIME.copy(__NAME__)
DARK_MASTER_MATCH_TIME.value = 2

#   median filter size for dark master
DARK_MASTER_MED_SIZE = DARK_MASTER_MED_SIZE.copy(__NAME__)
DARK_MASTER_MED_SIZE.value = 4


# =============================================================================
# CALIBRATION: BAD PIXEL MAP SETTINGS
# =============================================================================
#   Defines the full detector flat file (located in the data folder)
BADPIX_FULL_FLAT = BADPIX_FULL_FLAT.copy(__NAME__)
BADPIX_FULL_FLAT.value = 'detector_flat_full.fits'

#   Percentile to normalise to when normalising and median filtering
#      image [percentage]
BADPIX_NORM_PERCENTILE = BADPIX_NORM_PERCENTILE.copy(__NAME__)
BADPIX_NORM_PERCENTILE.value = 90.0


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


# =============================================================================
# CALIBRATION: BACKGROUND CORRECTION SETTINGS
# =============================================================================
#    Width of the box to produce the background mask
BKGR_BOXSIZE = BKGR_BOXSIZE.copy(__NAME__)
BKGR_BOXSIZE.value = 128

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
BKGR_KER_AMP.value = 47

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
#   Size of the order_profile smoothed box
#     (from pixel - size to pixel + size)
LOC_ORDERP_BOX_SIZE = LOC_ORDERP_BOX_SIZE.copy(__NAME__)
LOC_ORDERP_BOX_SIZE.value = 5

#   row number of image to start localisation processing at
LOC_START_ROW_OFFSET = LOC_START_ROW_OFFSET.copy(__NAME__)
LOC_START_ROW_OFFSET.value = 0

#   Definition of the central column for use in localisation
LOC_CENTRAL_COLUMN = LOC_CENTRAL_COLUMN.copy(__NAME__)
LOC_CENTRAL_COLUMN.value = 2500

#   Half spacing between orders
LOC_HALF_ORDER_SPACING = LOC_HALF_ORDER_SPACING.copy(__NAME__)
LOC_HALF_ORDER_SPACING.value = 45

# Minimum amplitude to accept (in e-)
LOC_MINPEAK_AMPLITUDE = LOC_MINPEAK_AMPLITUDE.copy(__NAME__)
LOC_MINPEAK_AMPLITUDE.value = 10    # 50

#   Order of polynomial to fit for widths
LOC_WIDTH_POLY_DEG = LOC_WIDTH_POLY_DEG.copy(__NAME__)
LOC_WIDTH_POLY_DEG.value = 4

#   Order of polynomial to fit for positions
LOC_CENT_POLY_DEG = LOC_CENT_POLY_DEG.copy(__NAME__)
LOC_CENT_POLY_DEG.value = 4

#   Define the column separation for fitting orders
LOC_COLUMN_SEP_FITTING = LOC_COLUMN_SEP_FITTING.copy(__NAME__)
LOC_COLUMN_SEP_FITTING.value = 20

#   Definition of the extraction window size (half size)
LOC_EXT_WINDOW_SIZE = LOC_EXT_WINDOW_SIZE.copy(__NAME__)
LOC_EXT_WINDOW_SIZE.value = 15  # 20 # 40 # 12

#   Definition of the gap index in the selected area
LOC_IMAGE_GAP = LOC_IMAGE_GAP.copy(__NAME__)
LOC_IMAGE_GAP.value = 0

#   Define minimum width of order to be accepted
LOC_ORDER_WIDTH_MIN = LOC_ORDER_WIDTH_MIN.copy(__NAME__)
LOC_ORDER_WIDTH_MIN.value = 10   # 5

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
LOC_MAX_RMS_WID.value = 1.0

#   Maximum fractional peak-to-peak for sigma-clip order fit (width)
LOC_MAX_PTP_WID = LOC_MAX_PTP_WID.copy(__NAME__)
LOC_MAX_PTP_WID.value = 10.0

#   Normalised amplitude threshold to accept pixels for background calculation
LOC_BKGRD_THRESHOLD = LOC_BKGRD_THRESHOLD.copy(__NAME__)
LOC_BKGRD_THRESHOLD.value = 0.15    # 0.17  # 0.18

#   Define the amount we drop from the centre of the order when
#      previous order center is missed (in finding the position)
LOC_ORDER_CURVE_DROP = LOC_ORDER_CURVE_DROP.copy(__NAME__)
LOC_ORDER_CURVE_DROP.value = 2.0

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

# =============================================================================
# CALIBRATION: SHAPE SETTINGS
# =============================================================================
#    Define the allowed DPRTYPES for finding files for DARK_MASTER will
#        only find those types define by 'filetype' but 'filetype' must
#        be one of theses (strings separated by commas)
ALLOWED_FP_TYPES = ALLOWED_FP_TYPES.copy(__NAME__)
ALLOWED_FP_TYPES.value = 'FP_FP'

#   Define the maximum time span to combine dark files over (in hours)
FP_MASTER_MATCH_TIME = FP_MASTER_MATCH_TIME.copy(__NAME__)
FP_MASTER_MATCH_TIME.value = 2

#   Define the percentile at which the FPs are normalised when getting the
#      fp master in shape master
FP_MASTER_PERCENT_THRES = FP_MASTER_PERCENT_THRES.copy(__NAME__)
FP_MASTER_PERCENT_THRES.value = 90.0

#  Define the largest standard deviation allowed for the shift in
#     x or y when doing the shape master fp linear transform
SHAPE_QC_LTRANS_RES_THRES = SHAPE_QC_LTRANS_RES_THRES.copy(__NAME__)
SHAPE_QC_LTRANS_RES_THRES.value = 0.1

#  Define the percentile which defines a true FP peak [0-100]
SHAPE_MASTER_VALIDFP_PERCENTILE = SHAPE_MASTER_VALIDFP_PERCENTILE.copy(__NAME__)
SHAPE_MASTER_VALIDFP_PERCENTILE.value = 80

#  Define the fractional flux an FP much have compared to its neighbours
SHAPE_MASTER_VALIDFP_THRESHOLD = SHAPE_MASTER_VALIDFP_THRESHOLD.copy(__NAME__)
SHAPE_MASTER_VALIDFP_THRESHOLD.value = 1.5

#  Define the number of iterations used to get the linear transform params
SHAPE_MASTER_LINTRANS_NITER = SHAPE_MASTER_LINTRANS_NITER.copy(__NAME__)
SHAPE_MASTER_LINTRANS_NITER.value = 5

#  Define the initial search box size (in pixels) around the fp peaks
SHAPE_MASTER_FP_INI_BOXSIZE = SHAPE_MASTER_FP_INI_BOXSIZE.copy(__NAME__)
SHAPE_MASTER_FP_INI_BOXSIZE.value = 11

#  Define the small search box size (in pixels) around the fp peaks
SHAPE_MASTER_FP_SMALL_BOXSIZE = SHAPE_MASTER_FP_SMALL_BOXSIZE.copy(__NAME__)
SHAPE_MASTER_FP_SMALL_BOXSIZE.value = 2

#  Define the minimum number of FP files in a group to mean group is valid
SHAPE_FP_MASTER_MIN_IN_GROUP = SHAPE_FP_MASTER_MIN_IN_GROUP.copy(__NAME__)
SHAPE_FP_MASTER_MIN_IN_GROUP.value = 3

#  Define which fiber should be used for fiber-dependent calibrations in
#     shape master
SHAPE_MASTER_FIBER = SHAPE_MASTER_FIBER.copy(__NAME__)
SHAPE_MASTER_FIBER.value = 'AB'

# The number of iterations to run the shape finding out to
SHAPE_NUM_ITERATIONS = SHAPE_NUM_ITERATIONS.copy(__NAME__)
SHAPE_NUM_ITERATIONS.value = 4

# total width of the order (combined fibers) in pixels
SHAPE_ORDER_WIDTH = SHAPE_ORDER_WIDTH.copy(__NAME__)
SHAPE_ORDER_WIDTH.value = 60

# number of sections per order to split the order into
SHAPE_NSECTIONS = SHAPE_NSECTIONS.copy(__NAME__)
SHAPE_NSECTIONS.value = 32

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
SHAPE_LARGE_ANGLE_MIN = SHAPE_LARGE_ANGLE_MIN.copy(__NAME__)
SHAPE_LARGE_ANGLE_MIN.value = -12.0

SHAPE_LARGE_ANGLE_MAX = SHAPE_LARGE_ANGLE_MAX.copy(__NAME__)
SHAPE_LARGE_ANGLE_MAX.value = 0.0

SHAPE_SMALL_ANGLE_MIN = SHAPE_SMALL_ANGLE_MIN.copy(__NAME__)
SHAPE_SMALL_ANGLE_MIN.value = -1.0

SHAPE_SMALL_ANGLE_MAX = SHAPE_SMALL_ANGLE_MAX.copy(__NAME__)
SHAPE_SMALL_ANGLE_MAX.value = 1.0

# max sigma clip (in sigma) on points within a section
SHAPE_SIGMACLIP_MAX = SHAPE_SIGMACLIP_MAX.copy(__NAME__)
SHAPE_SIGMACLIP_MAX.value = 4

# the size of the median filter to apply along the order (in pixels)
SHAPE_MEDIAN_FILTER_SIZE = SHAPE_MEDIAN_FILTER_SIZE.copy(__NAME__)
SHAPE_MEDIAN_FILTER_SIZE.value = 51

# The minimum value for the cross-correlation to be deemed good
SHAPE_MIN_GOOD_CORRELATION = SHAPE_MIN_GOOD_CORRELATION.copy(__NAME__)
SHAPE_MIN_GOOD_CORRELATION.value = 0.3

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

#  Defines whether to plot the debug plot per order (this creates many plots)
SHAPE_PLOT_PER_ORDER = SHAPE_PLOT_PER_ORDER.copy(__NAME__)
SHAPE_PLOT_PER_ORDER.value = False

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
SHAPE_UNIQUE_FIBERS.value = 'A, B, C'

#  Define whether to output debug (sanity check) files
SHAPE_DEBUG_OUTPUTS = SHAPE_DEBUG_OUTPUTS.copy(__NAME__)
SHAPE_DEBUG_OUTPUTS.value = True

# =============================================================================
# CALIBRATION: WAVE SETTINGS
# =============================================================================
# Define the line list file (located in the DRS_WAVE_DATA directory)
WAVE_LINELIST_FILE = WAVE_LINELIST_FILE.copy(__NAME__)
WAVE_LINELIST_FILE.value = 'catalogue_UNe.dat'    # 'catalogue_ThAr.dat'

# Define the line list file format (must be astropy.table format)
WAVE_LINELIST_FMT = WAVE_LINELIST_FMT.copy(__NAME__)
WAVE_LINELIST_FMT.value = 'ascii.tab'

# Define the line list file column names (must be separated by commas
#   and must be equal to the number of columns in file)
WAVE_LINELIST_COLS = WAVE_LINELIST_COLS.copy(__NAME__)
WAVE_LINELIST_COLS.value = 'll, amp, kind'

# Define the line list file row the data starts
WAVE_LINELIST_START = WAVE_LINELIST_START.copy(__NAME__)
WAVE_LINELIST_START.value = 0

# Define the line list file wavelength column and amplitude column
#    Must be in WAVE_LINELIST_COLS
WAVE_LINELIST_WAVECOL = WAVE_LINELIST_WAVECOL.copy(__NAME__)
WAVE_LINELIST_WAVECOL.value = 'll'
WAVE_LINELIST_AMPCOL = WAVE_LINELIST_AMPCOL.copy(__NAME__)
WAVE_LINELIST_AMPCOL.value = 'amp'
