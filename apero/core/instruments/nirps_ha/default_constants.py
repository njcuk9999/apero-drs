"""


Created on 2019-01-17

@author: cook
"""
from apero.core.instruments.default.default_constants import *

# Note: If variables are not showing up MUST CHECK __all__ definition
#       in import * module

__NAME__ = 'core.instruments.nirps_ha.default_constants.py'

# =============================================================================
# Spirou Constant definitions
# =============================================================================

# =============================================================================
# DRS DATA SETTINGS
# =============================================================================
# Define the data engineering path
DATA_ENGINEERING = DATA_ENGINEERING.copy(__NAME__)
DATA_ENGINEERING.value = './data/nirps_ha/engineering/'

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

# =============================================================================
# CALIBRATION: GENERAL SETTINGS
# =============================================================================
# Define the coefficients of the fit of 1/m vs d
CAVITY_1M_FILE = CAVITY_1M_FILE.copy(__NAME__)
CAVITY_1M_FILE.value = 'cavity_length_m_fit.dat'

# Define the coefficients of the fit of wavelength vs d
CAVITY_LL_FILE = CAVITY_LL_FILE.copy(__NAME__)
CAVITY_LL_FILE.value = 'cavity_length_ll_fit.dat'

# Define the object list file name
OBJ_LIST_FILE = OBJ_LIST_FILE.copy(__NAME__)
OBJ_LIST_FILE.value = 'object_query_list.fits'

# Define the object query list format
OBJ_LIST_FILE_FMT = OBJ_LIST_FILE_FMT.copy(__NAME__)
OBJ_LIST_FILE_FMT.value = 'fits'

# Define the radius for crossmatching objects (in both lookup table and query)
OBJ_LIST_CROSS_MATCH_RADIUS = OBJ_LIST_CROSS_MATCH_RADIUS.copy(__NAME__)
OBJ_LIST_CROSS_MATCH_RADIUS.value = 60.0

# Define the TAP Gaia URL (for use in crossmatching to Gaia via astroquery)
OBJ_LIST_GAIA_URL = OBJ_LIST_GAIA_URL.copy(__NAME__)
OBJ_LIST_GAIA_URL.value = 'http://gea.esac.esa.int/tap-server/tap'

# Define the TAP SIMBAD URL (for use in crossmatching OBJNAME via astroquery)
OBJ_LIST_SIMBAD_URL = OBJ_LIST_SIMBAD_URL.copy(__NAME__)
OBJ_LIST_SIMBAD_URL.value = 'http://gea.esac.esa.int/tap-server/tap'

# Define the gaia magnitude cut (rp mag) to use in the gaia query
OBJ_LIST_GAIA_MAG_CUT = OBJ_LIST_GAIA_MAG_CUT.copy(__NAME__)
OBJ_LIST_GAIA_MAG_CUT.value = 15.0

# Define the gaia epoch to use in the gaia query
OBJ_LIST_GAIA_EPOCH = OBJ_LIST_GAIA_EPOCH.copy(__NAME__)
OBJ_LIST_GAIA_EPOCH.value = 2015.5

# Define the gaia parallax limit for using gaia point
OBJ_LIST_GAIA_PLX_LIM = OBJ_LIST_GAIA_PLX_LIM.copy(__NAME__)
OBJ_LIST_GAIA_PLX_LIM.value = 5

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
FIBER_MAX_NUM_ORDERS_A.value = 69
FIBER_MAX_NUM_ORDERS_B.value = 69

#   Number of fibers
FIBER_SET_NUM_FIBERS_A = FIBER_SET_NUM_FIBERS_A.copy(__NAME__)
FIBER_SET_NUM_FIBERS_B = FIBER_SET_NUM_FIBERS_B.copy(__NAME__)
# set values
FIBER_SET_NUM_FIBERS_A.value = 1
FIBER_SET_NUM_FIBERS_B.value = 1

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
PP_FULL_FLAT.value = 'QE_2000nm.fits'

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

# Define whether to skip preprocessed files that have already be processed
SKIP_DONE_PP = SKIP_DONE_PP.copy(__NAME__)
SKIP_DONE_PP.value = False

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

#    Define the allowed DPRTYPES for finding files for DARK_MASTER will
#        only find those types define by 'filetype' but 'filetype' must
#        be one of theses (strings separated by commas)
ALLOWED_DARK_TYPES = ALLOWED_DARK_TYPES.copy(__NAME__)
ALLOWED_DARK_TYPES.value = 'DARK_DARK_TEL, DARK_DARK_INT'

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
LOC_CENTRAL_COLUMN.value = 2400

#   Half spacing between orders
LOC_HALF_ORDER_SPACING = LOC_HALF_ORDER_SPACING.copy(__NAME__)
LOC_HALF_ORDER_SPACING.value = 300

# Minimum amplitude to accept (in e-)
LOC_MINPEAK_AMPLITUDE = LOC_MINPEAK_AMPLITUDE.copy(__NAME__)
LOC_MINPEAK_AMPLITUDE.value = 10  # 50

#   Order of polynomial to fit for widths
LOC_WIDTH_POLY_DEG = LOC_WIDTH_POLY_DEG.copy(__NAME__)
LOC_WIDTH_POLY_DEG.value = 4

#   Order of polynomial to fit for positions
LOC_CENT_POLY_DEG = LOC_CENT_POLY_DEG.copy(__NAME__)
LOC_CENT_POLY_DEG.value = 6

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
LOC_COEFF_SIGCLIP.value = 7

#  Defines the fit degree to fit in the coefficient cleaning
LOC_COEFFSIG_DEG = LOC_COEFFSIG_DEG.copy(__NAME__)
LOC_COEFFSIG_DEG.value = 7

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
FP_MASTER_PERCENT_THRES.value = 95.0

#  Define the largest standard deviation allowed for the shift in
#     x or y when doing the shape master fp linear transform
SHAPE_QC_LTRANS_RES_THRES = SHAPE_QC_LTRANS_RES_THRES.copy(__NAME__)
SHAPE_QC_LTRANS_RES_THRES.value = 0.22

#  Define the percentile which defines a true FP peak [0-100]
SHAPE_MASTER_VALIDFP_PERCENTILE = SHAPE_MASTER_VALIDFP_PERCENTILE.copy(__NAME__)
SHAPE_MASTER_VALIDFP_PERCENTILE.value = 95

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
SHAPE_MASTER_FIBER.value = 'A'

# The number of iterations to run the shape finding out to
SHAPE_NUM_ITERATIONS = SHAPE_NUM_ITERATIONS.copy(__NAME__)
SHAPE_NUM_ITERATIONS.value = 4

# The order to use on the shape plot
SHAPE_PLOT_SELECTED_ORDER = SHAPE_PLOT_SELECTED_ORDER.copy(__NAME__)
SHAPE_PLOT_SELECTED_ORDER.value = 33

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

#  Define whether to output debug (sanity check) files
SHAPE_DEBUG_OUTPUTS = SHAPE_DEBUG_OUTPUTS.copy(__NAME__)
SHAPE_DEBUG_OUTPUTS.value = True

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

#   Define the orders not to plot on the RMS plot should be a string
#       containing a list of integers
FF_RMS_SKIP_ORDERS = FF_RMS_SKIP_ORDERS.copy(__NAME__)
FF_RMS_SKIP_ORDERS.value = '[0, 22, 23, 24, 25, 48]'

#   Maximum allowed RMS of flat field
QC_FF_MAX_RMS = QC_FF_MAX_RMS.copy(__NAME__)
QC_FF_MAX_RMS.value = 0.10

# Define the order to plot in summary plots
FF_PLOT_ORDER = FF_PLOT_ORDER.copy(__NAME__)
FF_PLOT_ORDER.value = 4

# =============================================================================
# CALIBRATION: EXTRACTION SETTINGS
# =============================================================================
#    Start order of the extraction in cal_ff if None starts from 0
EXT_START_ORDER = EXT_START_ORDER.copy(__NAME__)
EXT_START_ORDER.value = None

#    End order of the extraction in cal_ff if None ends at last order
EXT_END_ORDER = EXT_END_ORDER.copy(__NAME__)
EXT_END_ORDER.value = None

#   Half-zone extraction width left side (formally plage1)
EXT_RANGE1 = EXT_RANGE1.copy(__NAME__)
EXT_RANGE1.value = '{"A":5, "B":5}'

#   Half-zone extraction width right side (formally plage2)
EXT_RANGE2 = EXT_RANGE2.copy(__NAME__)
EXT_RANGE2.value = '{"A":5, "B":5}'

#   Define the orders to skip extraction on (will set all order values
#      to NaN. If empty list no orders are skipped. Should be a string
#      containing a valid python list
EXT_SKIP_ORDERS = EXT_SKIP_ORDERS.copy(__NAME__)
EXT_SKIP_ORDERS.value = '[]'

#    Defines whether to run extraction with cosmic correction
EXT_COSMIC_CORRETION = EXT_COSMIC_CORRETION.copy(__NAME__)
EXT_COSMIC_CORRETION.value = True

#    Define the percentage of flux above which we use to cut
EXT_COSMIC_SIGCUT = EXT_COSMIC_SIGCUT.copy(__NAME__)
EXT_COSMIC_SIGCUT.value = 0.25

#    Defines the maximum number of iterations we use to check for cosmics
#        (for each pixel)
EXT_COSMIC_THRESHOLD = EXT_COSMIC_THRESHOLD.copy(__NAME__)
EXT_COSMIC_THRESHOLD.value = 5

#   Saturation level reached warning
QC_EXT_FLUX_MAX = QC_EXT_FLUX_MAX.copy(__NAME__)
QC_EXT_FLUX_MAX.value = 50000

# Define the start s1d wavelength (in nm)
EXT_S1D_WAVESTART = EXT_S1D_WAVESTART.copy(__NAME__)
EXT_S1D_WAVESTART.value = 965

# Define the end s1d wavelength (in nm)
EXT_S1D_WAVEEND = EXT_S1D_WAVEEND.copy(__NAME__)
EXT_S1D_WAVEEND.value = 1808

#  Define the s1d spectral bin for S1D spectra (nm) when uniform in wavelength
EXT_S1D_BIN_UWAVE = EXT_S1D_BIN_UWAVE.copy(__NAME__)
EXT_S1D_BIN_UWAVE.value = 0.005

#  Define the s1d spectral bin for S1D spectra (km/s) when uniform in velocity
EXT_S1D_BIN_UVELO = EXT_S1D_BIN_UVELO.copy(__NAME__)
EXT_S1D_BIN_UVELO.value = 1.0

#  Define the s1d smoothing kernel for the transition between orders in pixels
EXT_S1D_EDGE_SMOOTH_SIZE = EXT_S1D_EDGE_SMOOTH_SIZE.copy(__NAME__)
EXT_S1D_EDGE_SMOOTH_SIZE.value = 20

#    Define dprtypes to calculate berv for (should be a string list)
EXT_ALLOWED_BERV_DPRTYPES = EXT_ALLOWED_BERV_DPRTYPES.copy(__NAME__)
EXT_ALLOWED_BERV_DPRTYPES.value = 'OBJ_FP, OBJ_DARK'

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
# CALIBRATION: THERMAL SETTINGS
# =============================================================================
# define whether to always extract thermals (i.e. overwrite existing files)
THERMAL_ALWAYS_EXTRACT = THERMAL_ALWAYS_EXTRACT.copy(__NAME__)
THERMAL_ALWAYS_EXTRACT.value = False

# define the type of file to use for wave solution (currently allowed are
#    'E2DS' or 'E2DSFF'
THERMAL_EXTRACT_TYPE = THERMAL_EXTRACT_TYPE.copy(__NAME__)
THERMAL_EXTRACT_TYPE.value = 'E2DSFF'

# define DPRTYPEs we need to correct thermal background using
#    telluric absorption (TAPAS)  (must be a string list separated by a comma)
THERMAL_CORRETION_TYPE1 = THERMAL_CORRETION_TYPE1.copy(__NAME__)
THERMAL_CORRETION_TYPE1.value = 'OBJ'

# define DPRTYPEs we need to correct thermal background using
#     method 2 (must be a string list separated by a comma)
THERMAL_CORRETION_TYPE2 = THERMAL_CORRETION_TYPE2.copy(__NAME__)
THERMAL_CORRETION_TYPE2.value = 'FP, HC, FLAT'

# define the order to perform the thermal background scaling on
THERMAL_ORDER = THERMAL_ORDER.copy(__NAME__)
THERMAL_ORDER.value = 48

# width of the median filter used for the background
THERMAL_FILTER_WID = THERMAL_FILTER_WID.copy(__NAME__)
THERMAL_FILTER_WID.value = 101

# define thermal red limit (in nm)
THERMAL_RED_LIMIT = THERMAL_RED_LIMIT.copy(__NAME__)
THERMAL_RED_LIMIT.value = 2500

# define thermal blue limit (in nm)
THERMAL_BLUE_LIMIT = THERMAL_BLUE_LIMIT.copy(__NAME__)
THERMAL_BLUE_LIMIT.value = 2450

# maximum tapas transmission to be considered completely opaque for the
# purpose of background determination in order 49.
THERMAL_THRES_TAPAS = THERMAL_THRES_TAPAS.copy(__NAME__)
THERMAL_THRES_TAPAS.value = 0.010

# define the percentile to measure the background for correction type 2
THERMAL_ENVELOPE_PERCENTILE = THERMAL_ENVELOPE_PERCENTILE.copy(__NAME__)
THERMAL_ENVELOPE_PERCENTILE.value = 10

# define the order to plot on the thermal debug plot
THERMAL_PLOT_START_ORDER = THERMAL_PLOT_START_ORDER.copy(__NAME__)
THERMAL_PLOT_START_ORDER.value = 40

# =============================================================================
# CALIBRATION: WAVE GENERAL SETTINGS
# =============================================================================
# Define the line list file (located in the DRS_WAVE_DATA directory)
WAVE_LINELIST_FILE = WAVE_LINELIST_FILE.copy(__NAME__)
WAVE_LINELIST_FILE.value = 'catalogue_UNe.dat'  # 'catalogue_ThAr.dat'

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
WAVE_T_ORDER_START.value = 79

#  Defines order from which the solution is calculated (first order)
WAVE_N_ORD_START = WAVE_N_ORD_START.copy(__NAME__)
WAVE_N_ORD_START.value = 0

#  Defines order to which the solution is calculated (last order)
WAVE_N_ORD_FINAL = WAVE_N_ORD_FINAL.copy(__NAME__)
WAVE_N_ORD_FINAL.value = 47

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
WAVE_HC_FITBOX_EWMIN.value = 0.7
WAVE_HC_FITBOX_EWMAX = WAVE_HC_FITBOX_EWMAX.copy(__NAME__)
WAVE_HC_FITBOX_EWMAX.value = 1.1

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
WAVE_FP_UPDATE_CAVITY.value = False

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


# =============================================================================
# CALIBRATION: WAVE LITTROW SETTINGS
# =============================================================================
#  Define the order to start the Littrow fit from
WAVE_LITTROW_ORDER_INIT_1 = WAVE_LITTROW_ORDER_INIT_1.copy(__NAME__)
WAVE_LITTROW_ORDER_INIT_1.value = 0
WAVE_LITTROW_ORDER_INIT_2 = WAVE_LITTROW_ORDER_INIT_2.copy(__NAME__)
WAVE_LITTROW_ORDER_INIT_2.value = 1

#  Define the order to end the Littrow fit at
WAVE_LITTROW_ORDER_FINAL_1 = WAVE_LITTROW_ORDER_FINAL_1.copy(__NAME__)
WAVE_LITTROW_ORDER_FINAL_1.value = 47
WAVE_LITTROW_ORDER_FINAL_2 = WAVE_LITTROW_ORDER_FINAL_2.copy(__NAME__)
WAVE_LITTROW_ORDER_FINAL_2.value = 47

#  Define orders to ignore in Littrow fit (should be a string list separated
#      by commas
WAVE_LITTROW_REMOVE_ORDERS = WAVE_LITTROW_REMOVE_ORDERS.copy(__NAME__)
WAVE_LITTROW_REMOVE_ORDERS.value = ''

#  Define the littrow cut steps
WAVE_LITTROW_CUT_STEP_1 = WAVE_LITTROW_CUT_STEP_1.copy(__NAME__)
WAVE_LITTROW_CUT_STEP_1.value = 250
WAVE_LITTROW_CUT_STEP_2 = WAVE_LITTROW_CUT_STEP_2.copy(__NAME__)
WAVE_LITTROW_CUT_STEP_2.value = 500

#  Define the fit polynomial order for the Littrow fit (fit across the orders)
WAVE_LITTROW_FIG_DEG_1 = WAVE_LITTROW_FIG_DEG_1.copy(__NAME__)
WAVE_LITTROW_FIG_DEG_1.value = 8  # 5  # 4
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
WAVE_FP_DOPD0.value = 2.44962434814043e7  # 2.44999e7  # 2.45e7

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

#    Define the border size (edges in x-direction) for the FP fitting algorithm
WAVE_FP_BORDER_SIZE = WAVE_FP_BORDER_SIZE.copy(__NAME__)
WAVE_FP_BORDER_SIZE.value = 3

#    Define the box half-size (in pixels) to fit an individual FP peak to
#        - a gaussian will be fit to +/- this size from the center of
#          the FP peak
WAVE_FP_FPBOX_SIZE = WAVE_FP_FPBOX_SIZE.copy(__NAME__)
WAVE_FP_FPBOX_SIZE.value = 3

#    Define the sigma above the median that a peak must have  - [cal_drift-peak]
#        to be recognised as a valid peak (before fitting a gaussian)
#        must be a string dictionary and must have an fp key
WAVE_FP_PEAK_SIG_LIM = WAVE_FP_PEAK_SIG_LIM.copy(__NAME__)
WAVE_FP_PEAK_SIG_LIM.value = '{"fp": 1.0, "hc": 7.0}'

#    Define the minimum spacing between peaks in order to be recognised
#        as a valid peak (before fitting a gaussian)
WAVE_FP_IPEAK_SPACING = WAVE_FP_IPEAK_SPACING.copy(__NAME__)
WAVE_FP_IPEAK_SPACING.value = 5

#    Define the expected width of FP peaks - used to "normalise" peaks
#        (which are then subsequently removed if > drift_peak_norm_width_cut
WAVE_FP_EXP_WIDTH = WAVE_FP_EXP_WIDTH.copy(__NAME__)
WAVE_FP_EXP_WIDTH.value = 1.0  # 0.9  # 0.8

#    Define the "normalised" width of FP peaks that is too large normalised
#        width = FP FWHM - WAVE_FP_EXP_WIDTH
#        cut is essentially:
#           FP FWHM < (WAVE_FP_EXP_WIDTH + WAVE_FP_NORM_WIDTH_CUT)
WAVE_FP_NORM_WIDTH_CUT = WAVE_FP_NORM_WIDTH_CUT.copy(__NAME__)
WAVE_FP_NORM_WIDTH_CUT.value = 0.25  # 0.2

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
WAVE_CCF_MASK = WAVE_CCF_MASK.copy(__NAME__)
WAVE_CCF_MASK.value = 'fp.mas'

# Define the wavelength units for the mask for the FP CCF
WAVE_CCF_MASK_UNITS = WAVE_CCF_MASK_UNITS.copy(__NAME__)
WAVE_CCF_MASK_UNITS.value = 'nm'

# Define the ccf mask path the FP CCF
WAVE_CCF_MASK_PATH = WAVE_CCF_MASK_PATH.copy(__NAME__)
WAVE_CCF_MASK_PATH.value = './data/spirou/ccf/'

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


# =============================================================================
# CALIBRATION: WAVE MASTER REFERENCE SETTINGS
# =============================================================================
# min SNR to consider the line
WAVEREF_NSIG_MIN = WAVEREF_NSIG_MIN.copy(__NAME__)
WAVEREF_NSIG_MIN.value = 15

# minimum distance to the edge of the array to consider a line
WAVEREF_EDGE_WMAX = WAVEREF_EDGE_WMAX.copy(__NAME__)
WAVEREF_EDGE_WMAX.value = 20

# value in pixel (+/-) for the box size around each HC line to perform fit
WAVEREF_HC_BOXSIZE = WAVEREF_HC_BOXSIZE.copy(__NAME__)
WAVEREF_HC_BOXSIZE.value = 5

# get valid hc dprtypes (string list separated by commas)
WAVEREF_HC_FIBTYPES = WAVEREF_HC_FIBTYPES.copy(__NAME__)
WAVEREF_HC_FIBTYPES.value = 'HCONE, HCTWO'

# get valid fp dprtypes (string list separated by commas)
WAVEREF_FP_FIBTYPES = WAVEREF_FP_FIBTYPES.copy(__NAME__)
WAVEREF_FP_FIBTYPES.value = 'FP'

# get the degree to fix master wavelength to in hc mode
WAVEREF_FITDEG = WAVEREF_FITDEG.copy(__NAME__)
WAVEREF_FITDEG.value = 5

# define the lowest N for fp peaks
WAVEREF_FP_NLOW = WAVEREF_FP_NLOW.copy(__NAME__)
WAVEREF_FP_NLOW.value = 9000

# define the highest N for fp peaks
WAVEREF_FP_NHIGH = WAVEREF_FP_NHIGH.copy(__NAME__)
WAVEREF_FP_NHIGH.value = 30000

# define the number of iterations required to do the Fp polynomial inversion
WAVEREF_FP_POLYINV = WAVEREF_FP_POLYINV.copy(__NAME__)
WAVEREF_FP_POLYINV.value = 4

# =============================================================================
# CALIBRATION: WAVE NIGHT SETTINGS
# =============================================================================
# high-order wavelength solution correction cannot be smaller than 2,
#   we remove 0 and 1
WAVE_NIGHT_HIGHF_CORR_DEG = WAVE_NIGHT_HIGHF_CORR_DEG.copy(__NAME__)
WAVE_NIGHT_HIGHF_CORR_DEG.value = 7

# number of iterations for convergence
WAVE_NIGHT_NITERATIONS = WAVE_NIGHT_NITERATIONS.copy(__NAME__)
WAVE_NIGHT_NITERATIONS.value = 30

# starting points for the cavity corrections
WAVE_NIGHT_DCAVITY = WAVE_NIGHT_DCAVITY.copy(__NAME__)
WAVE_NIGHT_DCAVITY.value = 0

# min SNR for incluing in the model
WAVE_NIGHT_NSIG_MIN = WAVE_NIGHT_NSIG_MIN.copy(__NAME__)
WAVE_NIGHT_NSIG_MIN.value = 30

# red cut off for fit constaint [nm]
WAVE_NIGHT_REDEND_CUTOFF = WAVE_NIGHT_REDEND_CUTOFF.copy(__NAME__)
WAVE_NIGHT_REDEND_CUTOFF.value = 2350

# size in nm of the median bin of residuals for higher-order correction
WAVE_NIGHT_DWAVE_BIN = WAVE_NIGHT_DWAVE_BIN.copy(__NAME__)
WAVE_NIGHT_DWAVE_BIN.value = 50

# min number of lines to be included in a median bin for high-order
# correction
WAVE_NIGHT_NMIN_LINES = WAVE_NIGHT_NMIN_LINES.copy(__NAME__)
WAVE_NIGHT_NMIN_LINES.value = 100

# sigma clipping for the fit
WAVE_NIGHT_NSIG_FIT_CUT = WAVE_NIGHT_NSIG_FIT_CUT.copy(__NAME__)
WAVE_NIGHT_NSIG_FIT_CUT.value = 5

# wave night plot hc bin lower bound [nm]
WAVENIGHT_PLT_HCBINL = WAVENIGHT_PLT_HCBINL.copy(__NAME__)
WAVENIGHT_PLT_HCBINL.value = 900

# wave night plot hc bin upper bound [nm]
WAVENIGHT_PLT_HCBINU = WAVENIGHT_PLT_HCBINU.copy(__NAME__)
WAVENIGHT_PLT_HCBINU.value = 2500

# wave night plot hc bin size [nm]
WAVENIGHT_PLT_HCBINSZ = WAVENIGHT_PLT_HCBINSZ.copy(__NAME__)
WAVENIGHT_PLT_HCBINSZ.value = 50

# wave night plot fp histogram 2d number of x bins
WAVENIGHT_PLT_FPBX = WAVENIGHT_PLT_FPBX.copy(__NAME__)
WAVENIGHT_PLT_FPBX.value = 100

# wave night plot fp histogram 2d number of y bins
WAVENIGHT_PLT_FPBY = WAVENIGHT_PLT_FPBY.copy(__NAME__)
WAVENIGHT_PLT_FPBY.value = 10

# wave night plot fp line bin size
WAVENIGHT_PLT_FPLB = WAVENIGHT_PLT_FPLB.copy(__NAME__)
WAVENIGHT_PLT_FPLB.value = 200

# wave night plot amplifier size (for modulo amplifier  structures)
WAVENIGHT_PLT_AMPSIZE = WAVENIGHT_PLT_AMPSIZE.copy(__NAME__)
WAVENIGHT_PLT_AMPSIZE.value = 256

# wave night plot max +/- dv to keep in the histogram plots
WAVENIGHT_PLT_MAXDV = WAVENIGHT_PLT_MAXDV.copy(__NAME__)
WAVENIGHT_PLT_MAXDV.value = 50

# wave night plot modulo amplifier step (bin) size
WAVENIGHT_PLT_DVSTEP = WAVENIGHT_PLT_DVSTEP.copy(__NAME__)
WAVENIGHT_PLT_DVSTEP.value = 10

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
TELLU_ALLOWED_DPRTYPES.value = 'OBJ_DARK, OBJ_FP'

# the INPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input telluric files
TELLURIC_FILETYPE = TELLURIC_FILETYPE.copy(__NAME__)
TELLURIC_FILETYPE.value = 'EXT_E2DS_FF'

# the fiber required for input template files
TELLURIC_FIBER_TYPE = TELLURIC_FIBER_TYPE.copy(__NAME__)
TELLURIC_FIBER_TYPE.value = 'AB'

# Define level above which the blaze is high enough to accurately
#    measure telluric
TELLU_CUT_BLAZE_NORM = TELLU_CUT_BLAZE_NORM.copy(__NAME__)
TELLU_CUT_BLAZE_NORM.value = 0.2

# Define telluric black/white list directory
TELLU_LIST_DIRECOTRY = TELLU_LIST_DIRECOTRY.copy(__NAME__)
TELLU_LIST_DIRECOTRY.value = './data/spirou/telluric/'

# Define telluric white list name
TELLU_WHITELIST_NAME = TELLU_WHITELIST_NAME.copy(__NAME__)
TELLU_WHITELIST_NAME.value = 'tellu_whitelist.txt'

# Define telluric black list name
TELLU_BLACKLIST_NAME = TELLU_BLACKLIST_NAME.copy(__NAME__)
TELLU_BLACKLIST_NAME.value = 'tellu_blacklist.txt'

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
MKTELLU_DEFAULT_CONV_WIDTH.value = 900

# define the finer convolution width [in pixels]
MKTELLU_FINER_CONV_WIDTH = MKTELLU_FINER_CONV_WIDTH.copy(__NAME__)
MKTELLU_FINER_CONV_WIDTH.value = 100

# define which orders are clean enough of tellurics to use the finer
#     convolution width (should be a string list separated by commas)
MKTELLU_CLEAN_ORDERS = MKTELLU_CLEAN_ORDERS.copy(__NAME__)
MKTELLU_CLEAN_ORDERS.value = '2, 3, 5, 6, 7, 8, 9, 14, 15, 19, 20, 28, 29, 30, 31, 32, 33, 34, 35, 43, 44'

# median-filter the template. we know that stellar features
#    are very broad. this avoids having spurious noise in our
#    templates [pixel]
MKTELLU_TEMP_MED_FILT = MKTELLU_TEMP_MED_FILT.copy(__NAME__)
MKTELLU_TEMP_MED_FILT.value = 15

# threshold in absorbance where we will stop iterating the absorption
#     model fit
MKTELLU_DPARAMS_THRES = MKTELLU_DPARAMS_THRES.copy(__NAME__)
MKTELLU_DPARAMS_THRES.value = 0.001

# max number of iterations, normally converges in about 12 iterations
MKTELLU_MAX_ITER = MKTELLU_MAX_ITER.copy(__NAME__)
MKTELLU_MAX_ITER.value = 50

# minimum transmission required for use of a given pixel in the TAPAS
#    and SED fitting
MKTELLU_THRES_TRANSFIT = MKTELLU_THRES_TRANSFIT.copy(__NAME__)
MKTELLU_THRES_TRANSFIT.value = 0.3

# Defines the bad pixels if the spectrum is larger than this value.
#    These values are likely an OH line or a cosmic ray
MKTELLU_TRANS_FIT_UPPER_BAD = MKTELLU_TRANS_FIT_UPPER_BAD.copy(__NAME__)
MKTELLU_TRANS_FIT_UPPER_BAD.value = 1.1

# Defines the minimum allowed value for the recovered water vapor optical
#    depth (should not be able 1)
MKTELLU_TRANS_MIN_WATERCOL = MKTELLU_TRANS_MIN_WATERCOL.copy(__NAME__)
MKTELLU_TRANS_MIN_WATERCOL.value = 0.2

# Defines the maximum allowed value for the recovered water vapor optical
#    depth
MKTELLU_TRANS_MAX_WATERCOL = MKTELLU_TRANS_MAX_WATERCOL.copy(__NAME__)
MKTELLU_TRANS_MAX_WATERCOL.value = 99

# Defines the minimum number of good points required to normalise the
#    spectrum, if less than this we don't normalise the spectrum by its
#    median
MKTELLU_TRANS_MIN_NUM_GOOD = MKTELLU_TRANS_MIN_NUM_GOOD.copy(__NAME__)
MKTELLU_TRANS_MIN_NUM_GOOD.value = 100

# Defines the percentile used to gauge which transmission points should
#    be used to median (above this percentile is used to median)
MKTELLU_TRANS_TAU_PERCENTILE = MKTELLU_TRANS_TAU_PERCENTILE.copy(__NAME__)
MKTELLU_TRANS_TAU_PERCENTILE.value = 95

# sigma-clipping of the residuals of the difference between the
# spectrum divided by the fitted TAPAS absorption and the
# best guess of the SED
MKTELLU_TRANS_SIGMA_CLIP = MKTELLU_TRANS_SIGMA_CLIP.copy(__NAME__)
MKTELLU_TRANS_SIGMA_CLIP.value = 20.0

# median-filter the trans data measured in pixels
MKTELLU_TRANS_TEMPLATE_MEDFILT = MKTELLU_TRANS_TEMPLATE_MEDFILT.copy(__NAME__)
MKTELLU_TRANS_TEMPLATE_MEDFILT.value = 31

# Define the threshold for "small" values that do not add to the weighting
MKTELLU_SMALL_WEIGHTING_ERROR = MKTELLU_SMALL_WEIGHTING_ERROR.copy(__NAME__)
MKTELLU_SMALL_WEIGHTING_ERROR.value = 0.01

# Define the orders to plot (not too many)
#    values should be a string list separated by commas
MKTELLU_PLOT_ORDER_NUMS = MKTELLU_PLOT_ORDER_NUMS.copy(__NAME__)
MKTELLU_PLOT_ORDER_NUMS.value = '19, 26, 35'

# Set an upper limit for the allowed line-of-sight optical depth of water
MKTELLU_TAU_WATER_ULIMIT = MKTELLU_TAU_WATER_ULIMIT.copy(__NAME__)
MKTELLU_TAU_WATER_ULIMIT.value = 99

# set a lower and upper limit for the allowed line-of-sight optical depth
#    for other absorbers (upper limit equivalent to airmass limit)
# line-of-sight optical depth for other absorbers cannot be less than one
#      (that's zenith) keep the limit at 0.2 just so that the value gets
#      propagated to header and leaves open the possibility that during
#      the convergence of the algorithm, values go slightly below 1.0
MKTELLU_TAU_OTHER_LLIMIT = MKTELLU_TAU_OTHER_LLIMIT.copy(__NAME__)
MKTELLU_TAU_OTHER_LLIMIT.value = 0.2

# line-of-sight optical depth for other absorbers cannot be greater than 5
#       that would be an airmass of 5 and SPIRou cannot observe there
MKTELLU_TAU_OTHER_ULIMIT = MKTELLU_TAU_OTHER_ULIMIT.copy(__NAME__)
MKTELLU_TAU_OTHER_ULIMIT.value = 5.0

# bad values and small values are set to this value (as a lower limit to
#   avoid dividing by small numbers or zero
MKTELLU_SMALL_LIMIT = MKTELLU_SMALL_LIMIT.copy(__NAME__)
MKTELLU_SMALL_LIMIT.value = 1.0e-9

#   Define the order to use for SNR check when accepting tellu files
#      to the telluDB
MKTELLU_QC_SNR_ORDER = MKTELLU_QC_SNR_ORDER.copy(__NAME__)
MKTELLU_QC_SNR_ORDER.value = 33

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
#      accepted to the telluDB
MKTELLU_QC_SNR_MIN = MKTELLU_QC_SNR_MIN.copy(__NAME__)
MKTELLU_QC_SNR_MIN.value = 100

# Define the allowed difference between recovered and input airmass
MKTELLU_QC_AIRMASS_DIFF = MKTELLU_QC_AIRMASS_DIFF.copy(__NAME__)
MKTELLU_QC_AIRMASS_DIFF.value = 0.3

# Define the MKO H-band limit limit [nm]
#    from http://www.ifa.hawaii.edu/~tokunaga/MKO-NIR_filter_set.html
MKTELLU_HBAND_LOWER = MKTELLU_HBAND_LOWER.copy(__NAME__)
MKTELLU_HBAND_LOWER.value = 1490

# Define the MKO H-band upper limit [nm]
#    from http://www.ifa.hawaii.edu/~tokunaga/MKO-NIR_filter_set.html
MKTELLU_HBAND_UPPER = MKTELLU_HBAND_UPPER.copy(__NAME__)
MKTELLU_HBAND_UPPER.value = 1780

# =============================================================================
# OBJECT: FIT TELLURIC SETTINGS
# =============================================================================
# The number of principle components to use in PCA fit
FTELLU_NUM_PRINCIPLE_COMP = FTELLU_NUM_PRINCIPLE_COMP.copy(__NAME__)
FTELLU_NUM_PRINCIPLE_COMP.value = 5

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
MKTEMPLATE_FIBER_TYPE.value = 'AB'

# the order to use for signal to noise cut requirement
MKTEMPLATE_SNR_ORDER = MKTEMPLATE_SNR_ORDER.copy(__NAME__)
MKTEMPLATE_SNR_ORDER.value = 33

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

# =============================================================================
# CALIBRATION: CCF SETTINGS
# =============================================================================
# Define the ccf mask path
CCF_MASK_PATH = CCF_MASK_PATH.copy(__NAME__)
CCF_MASK_PATH.value = './data/spirou/ccf/'

# Define the default CCF MASK to use
CCF_DEFAULT_MASK = CCF_DEFAULT_MASK.copy(__NAME__)
CCF_DEFAULT_MASK.value = 'gl581_Sep18_cleaned.mas'

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

#  Define the maximum allowed ratio between input CCF STEP and CCF WIDTH
#     i.e. error will be generated if CCF_STEP > (CCF_WIDTH / RATIO)
CCF_MAX_CCF_WID_STEP_RATIO = CCF_MAX_CCF_WID_STEP_RATIO.copy(__NAME__)
CCF_MAX_CCF_WID_STEP_RATIO.value = 10.0

# Define the width of the CCF range [km/s]
CCF_DEFAULT_WIDTH = CCF_DEFAULT_WIDTH.copy(__NAME__)
CCF_DEFAULT_WIDTH.value = 300.0

# Define the computations steps of the CCF [km/s]
CCF_DEFAULT_STEP = CCF_DEFAULT_STEP.copy(__NAME__)
CCF_DEFAULT_STEP.value = 0.5

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
CCF_N_ORD_MAX.value = 48

# Allowed input DPRTYPES for input  for CCF recipe
CCF_ALLOWED_DPRTYPES = CCF_ALLOWED_DPRTYPES.copy(__NAME__)
CCF_ALLOWED_DPRTYPES.value = 'OBJ_DARK, OBJ_FP'

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

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#     to calculate the CCF and RV
CCF_N_ORD_MAX = CCF_N_ORD_MAX.copy(__NAME__)
CCF_N_ORD_MAX.value = 48

# =============================================================================
# OBJECT: POLARISATION SETTINGS
# =============================================================================
#  Define all possible fibers used for polarimetry
#     (define as a string list)
POLAR_VALID_FIBERS = POLAR_VALID_FIBERS.copy(__NAME__)
POLAR_VALID_FIBERS.value = 'A, B'

#  Define all possible stokes parameters  used for polarimetry
#      (define as a string list)
POLAR_VALID_STOKES = POLAR_VALID_STOKES.copy(__NAME__)
POLAR_VALID_STOKES.value = 'V, Q, U'

#  Define the polarimetry calculation method
#    currently must be either:
#         - Ratio
#         - Difference
POLAR_METHOD = POLAR_METHOD.copy(__NAME__)
POLAR_METHOD.value = 'Ratio'

#  Define the polarimetry continuum bin size (for plotting)
POLAR_CONT_BINSIZE = POLAR_CONT_BINSIZE.copy(__NAME__)
POLAR_CONT_BINSIZE.value = 1000

#  Define the polarimetry continuum overlap size (for plotting)
POLAR_CONT_OVERLAP = POLAR_CONT_OVERLAP.copy(__NAME__)
POLAR_CONT_OVERLAP.value = 0

#  Define the telluric mask for calculation of continnum lower limits
#    (string list)
POLAR_CONT_TELLMASK_LOWER = POLAR_CONT_TELLMASK_LOWER.copy(__NAME__)
POLAR_CONT_TELLMASK_LOWER.value = '930, 1109, 1326, 1782, 1997, 2047'

#  Define the telluric mask for calculation of continnum upper limits
#    (string list)
POLAR_CONT_TELLMASK_UPPER = POLAR_CONT_TELLMASK_UPPER.copy(__NAME__)
POLAR_CONT_TELLMASK_UPPER.value = '967, 1167, 1491, 1979, 2027, 2076'

#  Perform LSD analysis
POLAR_LSD_ANALYSIS = POLAR_LSD_ANALYSIS.copy(__NAME__)
POLAR_LSD_ANALYSIS.value = True

#  Define the spectral lsd mask directory for lsd polar calculations
POLAR_LSD_PATH = POLAR_LSD_PATH.copy(__NAME__)
POLAR_LSD_PATH.value = './data/spirou/lsd/'

#  Define the file regular expression key to lsd mask files
POLAR_LSD_FILE_KEY = POLAR_LSD_FILE_KEY.copy(__NAME__)
POLAR_LSD_FILE_KEY.value = 'marcs_t*g50_all'

#  Define mask for selecting lines to be used in the LSD analysis
#      lower bounds (string list)
POLAR_LSD_WL_LOWER = POLAR_LSD_WL_LOWER.copy(__NAME__)
POLAR_LSD_WL_LOWER.value = '983, 1163, 1280, 1490, 1975, 2030'

#  Define mask for selecting lines to be used in the LSD analysis
#      upper bounds (string list)
POLAR_LSD_WL_UPPER = POLAR_LSD_WL_UPPER.copy(__NAME__)
POLAR_LSD_WL_UPPER.value = '1116, 1260, 1331, 1790, 1995, 2047.5'

# Define minimum line depth to be used in the LSD analyis
POLAR_LSD_MIN_LINEDEPTH = POLAR_LSD_MIN_LINEDEPTH.copy(__NAME__)
POLAR_LSD_MIN_LINEDEPTH.value = 0.175

#  Define initial velocity (km/s) for output LSD profile
POLAR_LSD_VINIT = POLAR_LSD_VINIT.copy(__NAME__)
POLAR_LSD_VINIT.value = -150.0

#  Define final velocity (km/s) for output LSD profile
POLAR_LSD_VFINAL = POLAR_LSD_VFINAL.copy(__NAME__)
POLAR_LSD_VFINAL.value = 150.0

#  Define the order wavelength mask filename
POLAR_LSD_ORDER_MASK = POLAR_LSD_ORDER_MASK.copy(__NAME__)
POLAR_LSD_ORDER_MASK.value = 'lsd_order_mask.dat'

#  Define whether to normalise by stokei by the continuum in lsd process
POLAR_LSD_NORM = POLAR_LSD_NORM.copy(__NAME__)
POLAR_LSD_NORM.value = True

#  Define the normalise by continuum lsd binsize
#     used in the normalization with POLAR_LSD_NORM = True
POLAR_LSD_NBIN1 = POLAR_LSD_NBIN1.copy(__NAME__)
POLAR_LSD_NBIN1.value = 30

#  Define the normalise by continuum lsd overlap with adjacent bins
#     used in the normalization with POLAR_LSD_NORM = True
POLAR_LSD_NOVERLAP1 = POLAR_LSD_NOVERLAP1.copy(__NAME__)
POLAR_LSD_NOVERLAP1.value = 15

#  Define the normalise by continuum lsd sigma clip value
#     used in the normalization with POLAR_LSD_NORM = True
POLAR_LSD_NSIGCLIP1 = POLAR_LSD_NSIGCLIP1.copy(__NAME__)
POLAR_LSD_NSIGCLIP1.value = 3

#  Define the normalise by continuum lsd window size (local fit size)
#     used in the normalization with POLAR_LSD_NORM = True
POLAR_LSD_NWINDOW1 = POLAR_LSD_NWINDOW1.copy(__NAME__)
POLAR_LSD_NWINDOW1.value = 2

#  Define the normalise by continuum lsd mode (mean/median/max)
#     used in the normalization with POLAR_LSD_NORM = True
POLAR_LSD_NMODE1 = POLAR_LSD_NMODE1.copy(__NAME__)
POLAR_LSD_NMODE1.value = 'median'

#  Define whether to use a linear fit in the normalise by continuum lsd calc
#     used in the normalization with POLAR_LSD_NORM = True
POLAR_LSD_NLFIT1 = POLAR_LSD_NLFIT1.copy(__NAME__)
POLAR_LSD_NLFIT1.value = True

#  Define number of points for output LSD profile
POLAR_LSD_NPOINTS = POLAR_LSD_NPOINTS.copy(__NAME__)
POLAR_LSD_NPOINTS.value = 201

#  Define the normalise by continuum lsd binsize
#    used in the profile calculation
POLAR_LSD_NBIN2 = POLAR_LSD_NBIN2.copy(__NAME__)
POLAR_LSD_NBIN2.value = 20

#  Define the normalise by continuum lsd overlap with adjacent bins
#    used in the profile calculation
POLAR_LSD_NOVERLAP2 = POLAR_LSD_NOVERLAP2.copy(__NAME__)
POLAR_LSD_NOVERLAP2.value = 5

#  Define the normalise by continuum lsd sigma clip value
#    used in the profile calculation
POLAR_LSD_NSIGCLIP2 = POLAR_LSD_NSIGCLIP2.copy(__NAME__)
POLAR_LSD_NSIGCLIP2.value = 3

#  Define the normalise by continuum lsd window size (local fit size)
#    used in the profile calculation
POLAR_LSD_NWINDOW2 = POLAR_LSD_NWINDOW2.copy(__NAME__)
POLAR_LSD_NWINDOW2.value = 2

#  Define the normalise by continuum lsd mode (mean/median/max)
#    used in the profile calculation
POLAR_LSD_NMODE2 = POLAR_LSD_NMODE2.copy(__NAME__)
POLAR_LSD_NMODE2.value = 'median'

#  Define whether to use a linear fit in the normalise by continuum lsd calc
#    used in the profile calculation
POLAR_LSD_NLFIT2 = POLAR_LSD_NLFIT2.copy(__NAME__)
POLAR_LSD_NLFIT2.value = False


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

# turn on the localisation cent min max debug plot
PLOT_LOC_MINMAX_CENTS = PLOT_LOC_MINMAX_CENTS.copy(__NAME__)
PLOT_LOC_MINMAX_CENTS.value = True

# turn on the localisation cent/thres debug plot
PLOT_LOC_MIN_CENTS_THRES = PLOT_LOC_MIN_CENTS_THRES.copy(__NAME__)
PLOT_LOC_MIN_CENTS_THRES.value = True

# turn on the localisation finding orders debug plot
PLOT_LOC_FINDING_ORDERS = PLOT_LOC_FINDING_ORDERS.copy(__NAME__)
PLOT_LOC_FINDING_ORDERS.value = False

# turn on the image above saturation threshold debug plot
PLOT_LOC_IM_SAT_THRES = PLOT_LOC_IM_SAT_THRES.copy(__NAME__)
PLOT_LOC_IM_SAT_THRES.value = True

# turn on the localisation fit residuals plot (warning: done many times)
PLOT_LOC_FIT_RESIDUALS = PLOT_LOC_FIT_RESIDUALS.copy(__NAME__)
PLOT_LOC_FIT_RESIDUALS.value = False

# turn on the order number vs rms debug plot
PLOT_LOC_ORD_VS_RMS = PLOT_LOC_ORD_VS_RMS.copy(__NAME__)
PLOT_LOC_ORD_VS_RMS.value = True

# turn on the localisation check coeffs debug plot
PLOT_LOC_CHECK_COEFFS = PLOT_LOC_CHECK_COEFFS.copy(__NAME__)
PLOT_LOC_CHECK_COEFFS.value = True

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

# turn on the wave lines hc/fp expected vs measured debug plot
#  (will plot once for hc once for fp)
PLOT_WAVEREF_EXPECTED = PLOT_WAVEREF_EXPECTED.copy(__NAME__)
PLOT_WAVEREF_EXPECTED.value = True

# turn on the wave per night iteration debug plot
PLOT_WAVENIGHT_ITERPLOT = PLOT_WAVENIGHT_ITERPLOT.copy(__NAME__)
PLOT_WAVENIGHT_ITERPLOT.value = True

# turn on the wave per night diff debug plot
PLOT_WAVENIGHT_DIFFPLOT = PLOT_WAVENIGHT_DIFFPLOT.copy(__NAME__)
PLOT_WAVENIGHT_DIFFPLOT.value = True

# turn on the wave per night hist debug plot
PLOT_WAVENIGHT_HISTPLOT = PLOT_WAVENIGHT_HISTPLOT.copy(__NAME__)
PLOT_WAVENIGHT_HISTPLOT.value = True

# turn on the make tellu wave flux debug plot (in loop)
PLOT_MKTELLU_WAVE_FLUX1 = PLOT_MKTELLU_WAVE_FLUX1.copy(__NAME__)
PLOT_MKTELLU_WAVE_FLUX1.value = False

# turn on the make tellu wave flux debug plot (single order)
PLOT_MKTELLU_WAVE_FLUX2 = PLOT_MKTELLU_WAVE_FLUX2.copy(__NAME__)
PLOT_MKTELLU_WAVE_FLUX2.value = True

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
PLOT_FTELLU_RECON_ABSO1.value = False

# turn on the fit tellu reconstructed absorption debug plot (single order)
PLOT_FTELLU_RECON_ABSO2 = PLOT_FTELLU_RECON_ABSO2.copy(__NAME__)
PLOT_FTELLU_RECON_ABSO2.value = True

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

# turn on the polar continuum debug plot
PLOT_POLAR_CONTINUUM = PLOT_POLAR_CONTINUUM.copy(__NAME__)
PLOT_POLAR_CONTINUUM.value = True

# turn on the polar results debug plot
PLOT_POLAR_RESULTS = PLOT_POLAR_RESULTS.copy(__NAME__)
PLOT_POLAR_RESULTS.value = True

# turn on the polar stokes i debug plot
PLOT_POLAR_STOKES_I = PLOT_POLAR_STOKES_I.copy(__NAME__)
PLOT_POLAR_STOKES_I.value = True

# turn on the polar lsd debug plot
PLOT_POLAR_LSD = PLOT_POLAR_LSD.copy(__NAME__)
PLOT_POLAR_LSD.value = True

# =============================================================================
# TOOLS SETTINGS
# =============================================================================
# Key for use in run files
REPROCESS_RUN_KEY = REPROCESS_RUN_KEY.copy(__NAME__)
REPROCESS_RUN_KEY.value = 'ID'

# Define the night name column name for raw file table
REPROCESS_NIGHTCOL = REPROCESS_NIGHTCOL.copy(__NAME__)
REPROCESS_NIGHTCOL.value = '__NIGHTNAME'

# Define the absolute file column name for raw file table
REPROCESS_ABSFILECOL = REPROCESS_ABSFILECOL.copy(__NAME__)
REPROCESS_ABSFILECOL.value = '__ABSFILE'

# Define the modified file column name for raw file table
REPROCESS_MODIFIEDCOL = REPROCESS_MODIFIEDCOL.copy(__NAME__)
REPROCESS_MODIFIEDCOL.value = '__MODIFIED'

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

# Define whether we try to create a latex summary pdf
#   (turn this off if you have any problems with latex/pdflatex)
SUMMARY_LATEX_PDF = SUMMARY_LATEX_PDF.copy(__NAME__)
SUMMARY_LATEX_PDF.value = True


# =============================================================================
#  End of configuration file
# =============================================================================