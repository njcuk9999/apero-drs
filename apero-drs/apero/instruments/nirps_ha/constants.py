"""
Default constants for NIRPS HA


Created on 2019-01-17

@author: cook
"""
from aperocore.base import base
from apero.instruments.default import constants
from apero.base import base as apero_base

__NAME__ = 'apero.instruments.nirps_ha.constants.py'
__PACKAGE__ = apero_base.__PACKAGE__
__version__ = apero_base.__version__
__authors__ = apero_base.__authors__
__date__ = apero_base.__date__
__release__ = apero_base.__release__
# copy the storage
CDict = constants.CDict.copy(source=__NAME__)

# =============================================================================
# NIRPS_HA Constant definitions
# =============================================================================

# =============================================================================
# DRS DATA SETTINGS
# =============================================================================
cgroup = 'DATA'
# Define the data engineering path
CDict.set('DATA_ENGINEERING', value='engineering/', source=__NAME__,
          group=cgroup)

# =============================================================================
# COMMON IMAGE SETTINGS
# =============================================================================
cgroup = 'IMAGE'
# Define the rotation of the pp files in relation to the raw files
# nrot = 0 -> same as input
# nrot = 1 -> 90deg counter-clock-wise
# nrot = 2 -> 180deg
# nrot = 3 -> 90deg clock-wise
# nrot = 4 -> flip top-bottom
# nrot = 5 -> flip top-bottom and rotate 90 deg counter-clock-wise
# nrot = 6 -> flip top-bottom and rotate 180 deg
# nrot = 7 -> flip top-bottom and rotate 90 deg clock-wise
# nrot >=8 -> performs a modulo 8 anyway
CDict.set('RAW_PP_ROT', value=5, source=__NAME__, group=cgroup)

# Measured detector gain in all places that use gain
CDict.set('EFFGAIN', value=1.15, source=__NAME__, group=cgroup)

# Define raw image size (mostly just used as a check and in places where we
# don't have access to this information)
CDict.set('X_FULL', value=4096, source=__NAME__, group=cgroup)
CDict.set('Y_FULL', value=4096, source=__NAME__, group=cgroup)

# Define the fibers
CDict.set('FIBER_TYPES', value=['A', 'B'], source=__NAME__, group=cgroup)

# Defines whether to by default combine images that are inputted at the same
# time
CDict.set('COMBINE_INPUT', value=True, source=__NAME__, group=cgroup)

# Defines whether to, by default, flip images that are inputted
CDict.set('FLIP_INPUT', value=True, source=__NAME__, group=cgroup)

# Defines whether to, by default, resize images that are inputted
CDict.set('RESIZE_IMAGE', value=True, source=__NAME__, group=cgroup)

# Defines the resized image
CDict.set('X_LOW', value=4, source=__NAME__, group=cgroup)
CDict.set('X_HIGH', value=4092, source=__NAME__, group=cgroup)
CDict.set('Y_LOW', value=4, source=__NAME__, group=cgroup)
CDict.set('Y_HIGH', value=4092, source=__NAME__, group=cgroup)

# Define the pixel size in km/s / pix
# also used for the median sampling size in tellu correction
CDict.set('PIXEL_SIZE', value=1.00, source=__NAME__, group=cgroup)

# Define mean line width expressed in pix
CDict.set('FWHM_PIXEL_LSF', value=3.0, source=__NAME__, group=cgroup)

# Define the point at which the detector saturates
CDict.set('SATURATION', value=60000, source=__NAME__, group=cgroup)

# Define the frame time for an image
CDict.set('FRAME_TIME', value=5.57192, source=__NAME__, gruop=cgroup, group=cgroup)

# =============================================================================
# CALIBRATION: GENERAL SETTINGS
# =============================================================================
cgroup = 'CAL.GEN'
# Define the maximum number of files that can be used in a group
CDict.set('GROUP_FILE_LIMIT', value=20, source=__NAME__, group=cgroup)

# Define the maximum time (in days) that a calibration can be separated from
# an observation in order to use it
CDict.set('MAX_DTIME', value=7.0, source=__NAME__, group=cgroup)

# Define whether we check the calibration and observation separation
CDict.set('DTIME_CHECK', value=True, source=__NAME__, group=cgroup)

# Define whether the user wants to bin the calibration times to a specific
# day fraction (i.e. midnight, midday) using CALIB_DB_DAYFRAC
CDict.set('BIN_IN_TIME', value=True, source=__NAME__, group=cgroup)

# Define the fraction of the day to bin to (0 = midnight before
# observation, 0.5 = noon, and 1.0 = midnight after)
CDict.set('DAYFRAC', value=0.0, source=__NAME__, group=cgroup)

# Define the threshold under which a file should not be combined
# (metric is compared to the median of all files 1 = perfect, 0 = noise)
CDict.set('CMETRIC1_THRES', value=0.99, source=__NAME__, group=cgroup)

# Define the DPRTYPES allowed for the combine metric 1 comparison
CDict.set('CMETRIC1_TYPES',
          value=['DARK_FLAT', 'FLAT_FLAT', 'FLAT_DARK', 'FP_FP', 'DARK_FP'],
          source=__NAME__, group=cgroup)

# Define the check FP percentile level
CDict.set('CHECKFP_PERCENTILE', value=95, source=__NAME__, group=cgroup)

# Define the check FP threshold qc parameter
CDict.set('CALIB_CHECK_FP_THRES', value=100, source=__NAME__, group=cgroup)

# Define the check FP center image size [px]
CDict.set('CHECK_FP_CENT_SIZE', value=100, source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: FIBER SETTINGS
# =============================================================================
cgroup = 'CAL.FIBER'
# Number of orders to skip at start of image
CDict.set('FIRST_ORDER_JUMP', value=dict(A=0, B=0, group=cgroup),
          source=__NAME__, group=cgroup)

# Maximum number of order to use
CDict.set('FIBER_MAX_NUM_ORDERS', value=dict(A=75, B=75),
          source=__NAME__, group=cgroup)

# Number of fibers
CDict.set('FIBER_SET_NUM_FIBERS', value=dict(A=1, B=1),
          source=__NAME__, group=cgroup)

# Get the science and reference fiber to use in the CCF process
CDict.set('CCF', value=['A', 'B'], source=__NAME__, group=cgroup)

# List the individual fiber names
CDict.set('INDIVIDUAL', value=['A', 'B'], source=__NAME__, group=cgroup)

# List the sky fibers to use for the science channel and the calib channel
CDict.set('SKYFIBERS', value=['A', 'B'], source=__NAME__, group=cgroup)

# =============================================================================
# PRE-PROCESSSING SETTINGS
# =============================================================================
cgroup = 'PP'
# Define object (science or telluric)
CDict.set('OBJ_DPRTYPES',
          value=['OBJ_DARK', 'OBJ_FP', 'OBJ_SKY', 'TELLU_SKY', 'FLUXSTD_SKY'],
          source=__NAME__, group=cgroup)

# Defines the box size surrounding hot pixels to use
CDict.set('HOTPIX_BOXSIZE', value=5, source=__NAME__, group=cgroup)

# Defines the size around badpixels that is considered part of the bad pixel
CDict.set('CORRUPT_MED_SIZE', value=2, source=__NAME__, group=cgroup)

# Define the fraction of the required exposure time that is required for a
# valid observation
CDict.set('BAD_EXPTIME_FRACTION', value=0.10, source=__NAME__, group=cgroup)

# Defines the threshold in sigma that selects hot pixels
CDict.set('CORRUPT_HOT_THRES', value=10, source=__NAME__, group=cgroup)

# Define the total number of amplifiers
CDict.set('TOTAL_AMP_NUM', value=32, source=__NAME__, group=cgroup)

# Define the number of dark amplifiers
CDict.set('NUM_DARK_AMP', value=5, source=__NAME__, group=cgroup)

# Define the number of bins used in the dark median process
CDict.set('DARK_MED_BINNUM', value=32, source=__NAME__, group=cgroup)

# Defines the pp hot pixel file (located in the data folder)
CDict.set('HOTPIX_FILE', value='hotpix_pp.csv', source=__NAME__, group=cgroup)

# Defines the pp amplifier bias model (located in the data folder)
CDict.set('AMP_ERROR_MODEL', value='amplifier_bias_model_nirps.fits',
          source=__NAME__, group=cgroup)

# Defines the pp led flat file (located in the data folder)
CDict.set('LED_FLAT_FILE', value='led_flat_ha.fits', source=__NAME__,
          group=cgroup)

# Define the number of un-illuminated reference pixels at top of image
CDict.set('NUM_REF_TOP', value=4, source=__NAME__, group=cgroup)

# Define the number of un-illuminated reference pixels at bottom of image
CDict.set('NUM_REF_BOTTOM', value=4, source=__NAME__, group=cgroup)

# Define the number of un-illuminated reference pixels at left of image
CDict.set('NUM_REF_LEFT', value=4, source=__NAME__, group=cgroup)

# Define the number of un-illuminated reference pixels at right of image
CDict.set('NUM_REF_RIGHT', value=4, source=__NAME__, group=cgroup)

# Define the percentile value for the rms normalisation (0-100)
CDict.set('RMS_PERCENTILE', value=95, source=__NAME__, group=cgroup)

# Define the lowest rms value of the rms percentile allowed if the value
# of the pp_rms_percentile-th is lower than this this value is used
CDict.set('LOWEST_RMS_PERCENTILE', value=10, source=__NAME__, group=cgroup)

# Defines the snr hotpix threshold to define a corrupt file
CDict.set('CORRUPT_SNR_HOTPIX', value=10, source=__NAME__, group=cgroup)

# Defines the RMS threshold to also catch corrupt files
CDict.set('CORRUPT_RMS_THRES', value=0.3, source=__NAME__, group=cgroup)

# Super-pessimistic noise estimate. Includes uncorrected common noise
CDict.set('COSMIC_NOISE_EST', value=30.0, source=__NAME__, group=cgroup)

# Define the cuts in sigma where we should look for cosmics (variance)
CDict.set('COSMIC_VARCUT1', value=100.0, source=__NAME__, group=cgroup)
CDict.set('COSMIC_VARCUT2', value=50.0, source=__NAME__, group=cgroup)

# Define the cuts in sigma where we should look for cosmics (intercept)
CDict.set('COSMIC_INTCUT1', value=100.0, source=__NAME__, group=cgroup)
CDict.set('COSMIC_INTCUT2', value=50.0, source=__NAME__, group=cgroup)

# random box size [in pixels] to speed-up low-frequency band computation
CDict.set('COSMIC_BOXSIZE', value=64, source=__NAME__, group=cgroup)

# Define whether to skip preprocessed files that have already be processed
CDict.set('SKIP_DONE', value=False, source=__NAME__, group=cgroup)

# Define dark dprtypes for threshold quality control check (PP_DARK_THRES)
CDict.set('DARK_DPRTYPES', 
          value=['DARK_DARK'], 
          source=__NAME__, group=cgroup)

# Define the threshold for a suitable DARK_DARK (above this will not
# be processed)
CDict.set('DARK_THRES', value=0.5, source=__NAME__, group=cgroup)

# Define allowed preprocessing reference file types (PP DPRTYPE)
CDict.set('ALLOWED_PPM_TYPES', value=['FLAT_FLAT'], source=__NAME__, group=cgroup)

# Define the allowed number of sigma for preprocessing reference mask
CDict.set('PPM_MASK_NSIG', value=10, source=__NAME__, group=cgroup)

# Define the bin to use to correct low level frequences. This value cannot
# be smaller than the order footprint on the array as it would lead to a set
# of NaNs in the downsized image
CDict.set('MEDAMP_BINSIZE', value=32, source=__NAME__, group=cgroup)

# Define the amplitude of the flux-dependent along-readout-axis
# derivative component
# TODO: Add calculation to static apero-utils.general.apero_statics.corr_xtalk.py
CDict.set('CX_AMP_FLUX', value=1.359371e-04, source=__NAME__, 
          author='EA', group=cgroup)

# Define amplitude of the flux-dependent along-readout-axis 1st
# derivative component
# TODO: Add calculation to static apero-utils.general.apero_statics.corr_xtalk.py
CDict.set('CX_AMP_DFLUX', value=7.727465e-04, source=__NAME__, 
          author='EA', group=cgroup)

# Define amplitude of the flux-dependent along-readout-axis 2nd
# derivative component
# TODO: Add calculation to static apero-utils.general.apero_statics.corr_xtalk.py
CDict.set('CX_AMP_D2FLUX', value=-2.601081e-04, source=__NAME__, 
          author='EA', group=cgroup)

# Define the partial APERO DPRTYPES which we should not do the science
# capacitive coupling
CDict.set('NOSCI_CAPC_DPRTYPES', value=['HCONE', 'HCTWO'], source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: DARK SETTINGS
# =============================================================================
cgroup = 'CAL.DARK'
# Min dark exposure time
CDict.set('QC_DARK_TIME', value=1.0, source=__NAME__, group=cgroup)
# Max dark median level [ADU/s]
CDict.set('QC_MAX_DARKLEVEL', value=0.07, source=__NAME__, group=cgroup)
# Max fraction of dark pixels (percent)
CDict.set('QC_MAX_DARK', value=1.0, source=__NAME__, group=cgroup)
# Max fraction of dead pixels
CDict.set('QC_MAX_DEAD', value=1.0, source=__NAME__, group=cgroup)

# Defines the blue resized image
CDict.set('X_BLUE_LOW', value=100, source=__NAME__, group=cgroup)
CDict.set('X_BLUE_HIGH', value=4000, source=__NAME__, group=cgroup)
CDict.set('Y_BLUE_LOW', value=3300, source=__NAME__, group=cgroup)
CDict.set('Y_BLUE_HIGH', value=3720, source=__NAME__, group=cgroup)

# Defines the red resized image
CDict.set('X_RED_LOW', value=100, source=__NAME__, group=cgroup)
CDict.set('X_RED_HIGH', value=4000, source=__NAME__, group=cgroup)
CDict.set('Y_RED_LOW', value=780, source=__NAME__, group=cgroup)
CDict.set('Y_RED_HIGH', value=1200, source=__NAME__, group=cgroup)

# Define a bad pixel cut limit (in ADU/s)
CDict.set('CUTLIMIT', value=5.0, source=__NAME__, group=cgroup)
# Defines the lower and upper percentiles when measuring the dark
CDict.set('QMIN', value=5, source=__NAME__, group=cgroup)
CDict.set('QMAX', value=95, source=__NAME__, group=cgroup)
# The number of bins in dark histogram
CDict.set('HISTO_BINS', value=200, source=__NAME__, group=cgroup)
# The range of the histogram in ADU/s
CDict.set('HISTO_RANGE_LOW', value=-0.2, source=__NAME__, group=cgroup)
CDict.set('HISTO_RANGE_HIGH', value=0.8, source=__NAME__, group=cgroup)

# Define the allowed DPRTYPES for finding files for DARK_REF
CDict.set('ALLOWED_TYPES', value=['DARK_DARK'], 
          source=__NAME__, group=cgroup)
# Define the maximum time span to combine dark files over (in hours)
CDict.set('REF_MTIME', value=2, source=__NAME__, group=cgroup)
# Median filter size for dark reference
CDict.set('REF_MEDSIZE', value=4, source=__NAME__, group=cgroup)
# Define the maximum number of files to use in the dark reference
CDict.set('REF_MAXFILES', value=100, source=__NAME__, group=cgroup)
# Define the minimum allowed exptime for dark files to be used in dark ref
CDict.set('REF_MIN_EXPTIME', value=300, source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: BAD PIXEL MAP SETTINGS
# =============================================================================
cgroup = 'CAL.BPIX'
# Defines the full detector flat file (located in the data folder)
CDict.set('FULL_FLAT', value='QE_2000nm.fits', source=__NAME__, group=cgroup)

# Percentile to normalise to when normalising and median filtering
# image [percentage]
CDict.set('NORM_PERCENTILE', value=95.0, source=__NAME__, group=cgroup)

# Define the median image in the x dimension over a boxcar of this width
CDict.set('FLAT_MED_WID', value=7, source=__NAME__, group=cgroup)

# Define the maximum differential pixel cut ratio
CDict.set('FLAT_CUT_RATIO', value=0.5, source=__NAME__, group=cgroup)

# Define the illumination cut parameter
CDict.set('ILLUM_CUT', value=0.05, source=__NAME__, group=cgroup)

# Define the maximum flux in ADU/s to be considered too hot to be used
CDict.set('MAX_HOTPIX', value=5.0, source=__NAME__, group=cgroup)

# Defines the threshold on the full detector flat file to deem pixels as good
CDict.set('FULL_THRES', value=0.3, source=__NAME__, group=cgroup)

# Defines areas that are large/small for bad pixel erosion
CDict.set('ERODE_SIZE', value=5, source=__NAME__, group=cgroup)

# Defines how much larger to make eroded bad pixel regions
CDict.set('DILATE_SIZE', value=9, source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: BACKGROUND CORRECTION SETTINGS
# =============================================================================
cgroup = 'CAL.BCORR'
# Width of the box to produce the background mask
CDict.set('BKGR_BOXSIZE', value=128, source=__NAME__, group=cgroup)

# The background percentile to compute minimum value (%)
CDict.set('BKGR_PERCENTAGE', value=5.0, source=__NAME__, group=cgroup)

# Size in pixels of to convolve tophat for the background mask
CDict.set('BKGR_MASK_CSIZE', value=7, source=__NAME__, group=cgroup)

# If a pixel has this or more "dark" neighbours, we consider it dark
# regardless of its initial value
CDict.set('NBAD_NEIGHBOURS', value=3, source=__NAME__, group=cgroup)

# Do background measurement (True or False)
CDict.set('NO_CORR', value=False, source=__NAME__, group=cgroup)

# Background kernel amplitude. If zero the scattering is skipped
CDict.set('KER_AMP', value=0, source=__NAME__, group=cgroup)

# Background kernel width in x and y [pixels]
CDict.set('KER_WX', value=1, source=__NAME__, group=cgroup)
CDict.set('KER_WY', value=9, source=__NAME__, group=cgroup)

# Construct a convolution kernel. We go from -BKGR_KER_SIG to +BKGR_KER_SIG
# sigma in each direction.
# It's important not to make the kernel too big as this slows down
# the 2D convolution.
# Do NOT make it a -10 to +10 sigma gaussian!
CDict.set('KER_SIG', value=3, source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: LOCALISATION SETTINGS
# =============================================================================
cgroup = 'CAL.LOC'
# median-binning size in the dispersion direction. This is just used to
# get an order-of-magnitude of the order profile along a given column
CDict.set('BINSIZE', value=25, source=__NAME__, author='EA', group=cgroup)

# the zero point percentile of a box
CDict.set('BOX_PTILE_LOW', value=25, source=__NAME__, author='EA', group=cgroup)

# the percentile of a box that is always an illuminated pixel
CDict.set('BOX_PTILE_HIGH', value=95, source=__NAME__, author='EA', group=cgroup)

# the size of the percentile filter - should be a bit bigger than the
# inter-order gap
CDict.set('PTILE_FILTER_SIZE', value=100, source=__NAME__, author='EA', group=cgroup)

# the fiber dilation number of iterations this should only be used when
# we want a combined localisation solution i.e. AB from A and B
CDict.set('FIBER_DILATE_ITRS', value=3, source=__NAME__, author='EA', group=cgroup)

# the minimum area (number of pixels) that defines an order
CDict.set('MIN_ORDER_AREA', value=500, source=__NAME__, author='EA', group=cgroup)

# Order of polynomial to fit for widths
CDict.set('WID_POLYDEG', value=1, source=__NAME__, author='EA', group=cgroup)

# Order of polynomial to fit for positions
CDict.set('CENT_POLYDEG', value=3, source=__NAME__, author='EA', group=cgroup)

# range width size (used to fit the width of the orders at certain points)
CDict.set('RANGE_WID_SUM', value=100, source=__NAME__, author='EA', group=cgroup)

# Define the minimum detector position where the centers of the orders should
# fall (across order direction)
CDict.set('YDET_MIN', value=40, source=__NAME__, author='EA', group=cgroup)

# Define the maximum detector position where the centers of the orders should
# fall (across order direction)
CDict.set('YDET_MAX', value=4088, source=__NAME__, author='EA', group=cgroup)

# Define the number of width samples to use in localisation
CDict.set('NUM_WID_SAMPLES', value=10, source=__NAME__, author='EA', group=cgroup)

# Size of the order_profile smoothed box
# (from pixel - size to pixel + size)
CDict.set('ORDERP_BOXSIZE', value=5, source=__NAME__, author='EA', group=cgroup)

# row number of image to start localisation processing at
CDict.set('START_ROW_OFFSET', value=0, source=__NAME__, author='EA', group=cgroup)

# Definition of the central column for use in localisation
CDict.set('MIDDLE_PIXEL_COL', value=2000, source=__NAME__, author='EA', group=cgroup)

# Half spacing between orders
CDict.set('HALF_ORDER_SPACING', value=300, source=__NAME__, group=cgroup)

# Minimum amplitude to accept
CDict.set('MINPEAK_AMP', value=10, source=__NAME__, group=cgroup)

# Define the jump size when finding the order position
# (jumps in steps of this from the center outwards)
CDict.set('COL_SEP_FITTING', value=5, source=__NAME__, group=cgroup)

# Definition of the extraction window size (half size)
CDict.set('EXT_WIN_SIZE', value=10, source=__NAME__, group=cgroup)

# Definition of the gap index in the selected area
CDict.set('IMAGE_GAP', value=0, source=__NAME__, group=cgroup)

# Define minimum width of order to be accepted
CDict.set('ORDER_WID_MIN', value=2, source=__NAME__, group=cgroup)

# Define the noise multiplier threshold in order to accept an
# order center as usable i.e.
# max(pixel value) - min(pixel value) > THRES * RDNOISE
CDict.set('NOISE_MULT_THRES', value=50, source=__NAME__, group=cgroup)

# Maximum rms for sigma-clip order fit (center positions)
CDict.set('MAX_RMS_CENT', value=0.1, source=__NAME__, group=cgroup)

# Maximum peak-to-peak for sigma-clip order fit (center positions)
CDict.set('MAX_PTP_CENT', value=0.300, source=__NAME__, group=cgroup)

# Maximum frac ptp/rms for sigma-clip order fit (center positions)
CDict.set('PTP_RMS_CENT', value=8.0, source=__NAME__, group=cgroup)

# Maximum rms for sigma-clip order fit (width)
CDict.set('MAX_RMS_WID', value=5.0, source=__NAME__, group=cgroup)

# Maximum fractional peak-to-peak for sigma-clip order fit (width)
CDict.set('MAX_PTP_WID', value=30.0, source=__NAME__, group=cgroup)

# Normalised amplitude threshold to accept pixels for background calculation
CDict.set('BKGRD_THRES', value=0.15, source=__NAME__, group=cgroup)

# Define the amount we drop from the centre of the order when
# previous order center is missed (in finding the position)
CDict.set('ORDER_CURVE_DROP', value=2.0, source=__NAME__, group=cgroup)

# set the sigma clipping cut off value for cleaning coefficients
CDict.set('COEFF_SIGCLIP', value=5, source=__NAME__, group=cgroup)

# Defines the fit degree to fit in the coefficient cleaning
CDict.set('COEFFSIG_DEG', value=5, source=__NAME__, group=cgroup)

# Define the maximum value allowed in the localisation (cuts reddest orders)
CDict.set('MAX_YPIX_VAL', value=4060, source=__NAME__, group=cgroup)

# Saturation threshold for localisation
CDict.set('SAT_THRES', value=1000, source=__NAME__, group=cgroup)

# Maximum points removed in location fit
CDict.set('QL_MAXFIT_RM_CTR', value=1500, source=__NAME__, group=cgroup)

# Maximum points removed in width fit
CDict.set('QL_MAXFIT_RM_WID', value=105, source=__NAME__, group=cgroup)

# Maximum rms allowed in fitting location
CDict.set('QC_RMSMAX_CTR', value=100, source=__NAME__, group=cgroup)

# Maximum rms allowed in fitting width
CDict.set('QC_RMSMAX_WID', value=500, source=__NAME__, group=cgroup)

# Option for archiving the location image
CDict.set('SAVE_SUPERIM_FILE', value=True, source=__NAME__, group=cgroup)

# set the zoom in levels for the plots (x min value)
CDict.set('PLOT_CX_ZOOM1', value=[0, 2044, 0, 2044], source=__NAME__, group=cgroup)

# set the zoom in levels for the plots (x max value)
CDict.set('PLOT_CX_ZOOM2', value=[2044, 4088, 2044, 4088],
          source=__NAME__, group=cgroup)

# set the zoom in levels for the plots (top left corners)
CDict.set('PLOT_CY_ZOOM1', value=[0, 0, 2500, 2500], source=__NAME__, group=cgroup)

# set the zoom in levels for the plots (top right corners)
CDict.set('PLOT_CY_ZOOM2', value=[600, 600, 3100, 3100],
          source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: SHAPE SETTINGS
# =============================================================================
cgroup = 'CAL.SHAPE'
# Define the allowed DPRTYPES for finding files for DARK_REF will
# only find those types define by 'filetype' but 'filetype' must
# be one of theses
CDict.set('ALLOWED_FP_TYPES', value=['FP_FP'], source=__NAME__, group=cgroup)

# Define the maximum time span to combine fp files over (in hours)
CDict.set('FP_REF_MATCH_TIME', value=2, source=__NAME__, group=cgroup)

# Define the percentile at which the FPs are normalised when getting the
# fp reference in shape reference
CDict.set('FP_REF_PERCENT_THRES', value=95.0, source=__NAME__, group=cgroup)

# Define the largest standard deviation allowed for the shift in
# x or y when doing the shape reference fp linear transform
CDict.set('QC_LTRANS_RTHRES', value=0.22, source=__NAME__, group=cgroup)

# Define the maximum number of files to use in the shape reference
CDict.set('REF_MAX_FILES', value=100, source=__NAME__, group=cgroup)

# Define the percentile which defines a true FP peak [0-100]
CDict.set('REF_VALIDFP_PTILE', value=95, source=__NAME__, group=cgroup)

# Define the fractional flux an FP must have compared to its neighbours
CDict.set('REF_VALIDFP_THRES', value=1.5, source=__NAME__, group=cgroup)

# Define the number of iterations used to get the linear transform params
CDict.set('REF_LINTRANS_NITER', value=5, source=__NAME__, group=cgroup)

# Define the initial search box size (in pixels) around the fp peaks
CDict.set('REF_FP_IBOXSIZE', value=11, source=__NAME__, group=cgroup)

# Define the small search box size (in pixels) around the fp peaks
CDict.set('REF_FP_SBOXSIZE', value=2, source=__NAME__, group=cgroup)

# Define the minimum number of FP files in a group to mean group is valid
CDict.set('FP_REF_MIN_INGROUP', value=3, source=__NAME__, group=cgroup)

# Define which fiber should be used for fiber-dependent calibrations in
# shape reference
CDict.set('REF_FIBER', value='A', source=__NAME__, group=cgroup)

# Define the shape reference dx rms quality control criteria (per order)
CDict.set('REF_DX_RMS_QC', value=0.3, source=__NAME__, group=cgroup)

# Define the number of iterations to run the shape finding out to
CDict.set('NUM_ITER', value=4, source=__NAME__, group=cgroup)

# Define the order to use on the shape plot
CDict.set('PLOT_SORDER', value=64, source=__NAME__, group=cgroup)

# The fit order to fit to the slope of the shape of the fibers
CDict.set('FIT_SLOPE_DEG', value=1,
          source=__NAME__, group=cgroup)

# Define the number of sections per order to split the order into
CDict.set('NSECTIONS', value=32, source=__NAME__, group=cgroup)

# Define the range of angles (in degrees) for the first iteration (large)
CDict.set('LANGLE_MIN', value=-12.0, source=__NAME__, group=cgroup)
CDict.set('LANGLE_MAX', value=0.0, source=__NAME__, group=cgroup)

# Define the range of angles (in degrees) for subsequent iterations (small)
CDict.set('SANGLE_MIN', value=-1.0, source=__NAME__, group=cgroup)
CDict.set('SANGLE_MAX', value=1.0, source=__NAME__, group=cgroup)

# Define the max sigma clip (in sigma) on points within a section
CDict.set('SIGCLIP_MAX', value=4, source=__NAME__, group=cgroup)

# Define the size of the median filter to apply along the order (in pixels)
CDict.set('MED_FILT_SIZE', value=51, source=__NAME__, group=cgroup)

# Define the minimum value for the cross-correlation to be deemed good
CDict.set('MIN_GOOD_CORR', value=0.5, source=__NAME__, group=cgroup)

# Define the first pass (short) median filter width for dx
CDict.set('SHORT_DX_MEDFILT_WID', value=9, source=__NAME__, group=cgroup)

# Define the second pass (long) median filter width for dx.
# Used to fill NaN positions in dx that are not covered by short pass
CDict.set('LONG_DX_MEDFILT_WID', value=9, source=__NAME__, group=cgroup)

# Defines the largest allowed standard deviation for a given
# per-order and per-x-pixel shift of the FP peaks
CDict.set('QC_DXMAP_STD', value=5, source=__NAME__, group=cgroup)

# Define the shape offset xoffset (before and after) fp peaks
CDict.set('XOFFSET', value=30, source=__NAME__, group=cgroup)

# Define the bottom percentile for fp peak
CDict.set('OFF_BTM_PTILE', value=10, source=__NAME__, group=cgroup)

# Define the top percentile for fp peak
CDict.set('OFF_TOP_PTILE', value=95, source=__NAME__, group=cgroup)

# Define the floor below which top values should be set to this fraction
# away from the max top value
CDict.set('OFF_TOP_FLOOR_FRAC', value=0.1, source=__NAME__, group=cgroup)

# Define the median filter to apply to the hc (high pass filter)
CDict.set('OFF_MED_FILT_WID', value=15, source=__NAME__, group=cgroup)

# Define the maximum number of FP (larger than expected number)
CDict.set('OFF_FPINDEX_MAX', value=30000, source=__NAME__, group=cgroup)

# Define the valid length of a FP peak
CDict.set('OFF_VALID_FP_LEN', value=5, source=__NAME__, group=cgroup)

# Define the maximum allowed offset (in nm) that we allow for the detector
CDict.set('OFF_DRIFT_MARGIN', value=20, source=__NAME__, group=cgroup)

# Define the number of iterations to do for the wave_fp inversion trick
CDict.set('OFF_WAVEFP_INV_IT', value=5, source=__NAME__, group=cgroup)

# Define the border in pixels at the edge of the detector
CDict.set('OFF_MASK_BORDER', value=30, source=__NAME__, group=cgroup)

# Define the minimum maxpeak value as a fraction of the maximum maxpeak
CDict.set('OFF_MM_PEAK_FRAC', value=0.4, source=__NAME__, group=cgroup)

# Define the width of the FP mask (+/- the center)
CDict.set('OFF_MASK_PWIDTH', value=3, source=__NAME__, group=cgroup)

# Define the width of the FP to extract (+/- the center)
CDict.set('OFF_MASK_EXTWID', value=5, source=__NAME__, group=cgroup)

# Define the most deviant peaks - percentile from [min to max]
CDict.set('OFF_DEV_PMIN', value=5, source=__NAME__, group=cgroup)
CDict.set('OFF_DEV_PMAX', value=95, source=__NAME__, group=cgroup)

# Define the maximum error in FP order assignment
# we assume that the error in FP order assignment could range
# from -50 to +50 in practice, it is -1, 0 or +1 for the cases we've
# tested to date
CDict.set('OFF_FPMAX_NUMERR', value=50, source=__NAME__, group=cgroup)

# Define the number of sigmas that the HC spectrum is allowed to be away from
# the predicted (from FP) position
CDict.set('OFF_FIT_HC_SIG', value=3, source=__NAME__, group=cgroup)

# Define the maximum allowed maximum absolute deviation away from the error fit
CDict.set('OFF_MAXDEV_THRES', value=5, source=__NAME__, group=cgroup)

# Define the very low thresholding values tend to clip valid points
CDict.set('OFF_ABSDEV_THRES', value=0.2, source=__NAME__, group=cgroup)

# Define the names of the unique fibers for use in getting the localisation
# coefficients for dymap
CDict.set('UFIBERS', value='A, B', source=__NAME__, group=cgroup)

# Define first zoom plot for shape local zoom debug plot
# should be a string list (xmin, xmax, ymin, ymax)
CDict.set('LOCAL_PZOOM1', value=[1844, 2244, 0, 400], source=__NAME__, group=cgroup)

# Define second zoom plot for shape local zoom debug plot
# should be a string list (xmin, xmax, ymin, ymax)
CDict.set('LOCAL_PZOOM2', value=[1844, 2244, 2700, 3100], source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: FLAT SETTINGS
# =============================================================================
cgroup = 'CAL.FLAT'
# Half size blaze smoothing window
CDict.set('HALF_WINDOW', value=50, source=__NAME__, group=cgroup)

# Minimum relative e2ds flux for the blaze computation
CDict.set('BLAZE_THRES', value=16.0, source=__NAME__, group=cgroup)

# The blaze polynomial fit degree
CDict.set('BLAZE_DEG', value=10, source=__NAME__, group=cgroup)

# Define the threshold, expressed as the fraction of the maximum peak,
# below this threshold the blaze (and e2ds) is set to NaN
CDict.set('BLAZE_SCUT', value=0.1, source=__NAME__, group=cgroup)

# Define the rejection threshold for the blaze sinc fit
CDict.set('BLAZE_SIGFIT', value=4.0, source=__NAME__, group=cgroup)

# Define the hot bad pixel percentile level (using in blaze sinc fit)
CDict.set('BLAZE_BPTILE', value=95, source=__NAME__, group=cgroup)

# Define the number of times to iterate around blaze sinc fit
CDict.set('BLAZE_NITER', value=2, source=__NAME__, group=cgroup)

# Define the sinc fit median filter width (we want to fit the shape of
# the order not line structures)
CDict.set('BLAZE_SINC_MED_SIZE', value=50, source=__NAME__, group=cgroup)

# Define the orders not to plot on the RMS plot should be a string
# containing a list of integers
CDict.set('RMS_SKIP_ORDERS', value=[0, 22, 23, 24, 25, 48], source=__NAME__, group=cgroup)

# Maximum allowed RMS of flat field
CDict.set('QC_MAX_RMS', value=1.0, source=__NAME__, group=cgroup)

# Define the order to plot in summary plots
CDict.set('PLOT_ORDER', value=4, source=__NAME__, group=cgroup)

# Define the high pass filter size in pixels
CDict.set('HIGHPASS_SIZE', value=501, source=__NAME__, author='EA', group=cgroup)


# =============================================================================
# CALIBRATION: LEAKAGE SETTINGS
# =============================================================================
cgroup = 'CAL.LEAK'
# Define the types of input file allowed by the leakage reference recipe
CDict.set('ALLOWED_REF_TYPES', value=['DARK_FP'], source=__NAME__, group=cgroup)

# Define whether to always extract leak reference files (i.e. overwrite
# existing files)
CDict.set('ALWAYS_EXTRACT', value=False, source=__NAME__, group=cgroup)

# Define the type of file to use for leak reference solution
# (currently allowed are 'E2DSFF') - must match with LEAK_EXTRACT_FILE
CDict.set('REF_EXT_TYPES', value='E2DSFF', source=__NAME__, group=cgroup)

# Define whether we want to correct leakage by default
CDict.set('CORRECT_LEAK', value=True, source=__NAME__, group=cgroup)

# Define DPRTYPE in reference fiber to do correction
CDict.set('REF_TYPES', value=['FP'], source=__NAME__, group=cgroup)

# Define the maximum number of files to use in the leak reference
CDict.set('REF_MAX_FILES', value=20, source=__NAME__, group=cgroup)

# Define the type of file to use for the leak correction (currently allowed are
# 'E2DS_FILE' or 'E2DSFF_FILE' (linked to recipe definition outputs)
# must match with LEAKREF_EXTRACT_TYPE
CDict.set('EXT_FILE', value='E2DSFF_FILE', source=__NAME__, group=cgroup)

# Define the extraction files which are 2D images (i.e. order num x nbpix)
CDict.set('EXT2D_FILES', value=['E2DS_FILE', 'E2DSFF_FILE'],
          source=__NAME__, group=cgroup)

# Define the extraction files which are 1D spectra
CDict.set('EXT1D_FILES', value=['S1D_W_FILE', 'S1D_V_FILE'],
          source=__NAME__, group=cgroup)

# Define the thermal background percentile for the leak and leak reference
CDict.set('BCKGRD_PTILE', value=5, source=__NAME__, group=cgroup)

# Define the normalisation percentile for the leak and leak reference
CDict.set('NORM_PTILE', value=90, source=__NAME__, group=cgroup)

# Define the e-width of the smoothing kernel for leak reference
CDict.set('REF_WSMOOTH', value=15, source=__NAME__, group=cgroup)

# Define the kernel size for leak reference
CDict.set('REF_KERSIZE', value=3, source=__NAME__, group=cgroup)

# Define the lower bound percentile for leak correction
CDict.set('LOW_PTILE', value=1, source=__NAME__, group=cgroup)

# Define the upper bound percentile for leak correction
CDict.set('HIGH_PTILE', value=99, source=__NAME__, group=cgroup)

# Define the limit on spurious FP ratio (1 +/- limit)
CDict.set('BAD_RATIO_OFFSET', value=0.1, source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: EXTRACTION SETTINGS
# =============================================================================
cgroup = 'CAL.EXT'
# Whether extraction code is done in quick look mode (do not use for
# final products)
CDict.set('QUICKLOOK', value=False, source=__NAME__, group=cgroup)

# Start order of the extraction in apero_flat if None starts from 0
CDict.set('START_ORDER', value=None, source=__NAME__, group=cgroup)

# End order of the extraction in apero_flat if None ends at last order
CDict.set('END_ORDER', value=None, source=__NAME__, group=cgroup)

# Half-zone extraction width left side (formally plage1)
CDict.set('RANGE1', value={"A": 2, "B": 2}, 
          source=__NAME__, group=cgroup)

# Half-zone extraction width right side (formally plage2)
CDict.set('RANGE2', value={"A": 2, "B": 2}, 
          source=__NAME__, group=cgroup)

# Define the orders to skip extraction on (will set all order values
# to NaN. If empty list no orders are skipped. Should be a string
# containing a valid python list
CDict.set('SKIP_ORDERS', value=[], source=__NAME__, group=cgroup)

# Defines whether to run extraction with cosmic correction
CDict.set('COSMIC_CORR', value=True, source=__NAME__, group=cgroup)

# Define the number of sigmas away from the median flux which we use to
# cut cosmic rays
CDict.set('COSMIC_SIGCUT', value=10, source=__NAME__, group=cgroup)

# Defines the maximum number of iterations we use to check for cosmics
# (for each pixel)
CDict.set('COSMIC_THRES', value=5, source=__NAME__, group=cgroup)

# Saturation level reached warning
CDict.set('QC_FLUX_MAX', value=50000, source=__NAME__, group=cgroup)

# Define which extraction file to use for s1d creation
CDict.set('S1D_INTYPE', value='E2DSFF', source=__NAME__, group=cgroup)
# Define which extraction file (recipe definitions) linked to EXT_S1D_INTYPE
CDict.set('S1D_INFILE', value='E2DSFF_FILE', source=__NAME__, group=cgroup)

# Define the start s1d wavelength (in nm)
CDict.set('S1D_WAVESTART', value=965, source=__NAME__, group=cgroup)

# Define the end s1d wavelength (in nm)
CDict.set('S1D_WAVEEND', value=1950, source=__NAME__, group=cgroup)

# Define the s1d spectral bin for S1D spectra (nm) when uniform in wavelength
CDict.set('S1D_BIN_UWAVE', value=0.005, source=__NAME__, group=cgroup)

# Define the s1d spectral bin for S1D spectra (km/s) when uniform in velocity
CDict.set('S1D_BIN_UVEL', value=0.5, source=__NAME__, group=cgroup)

# Define the s1d smoothing kernel for the transition between orders in pixels
CDict.set('S1D_EDGE_SSIZE', value=20, source=__NAME__, group=cgroup)

# Define dprtypes to calculate berv for (should be a string list)
CDict.set('ALLOWED_BERV_DPRTYPES',
          value=['OBJ_FP', 'OBJ_DARK', 'OBJ_SKY', 'TELLU_SKY', 'FLUXSTD_SKY'],
          source=__NAME__, group=cgroup)

# Define which BERV calculation to use ('barycorrpy' or 'estimate' or 'None')
CDict.set('BERV_KIND', value='barycorrpy', source=__NAME__, group=cgroup)

# Define the barycorrpy iers file
CDict.set('BERV_IERS_FILE', value='finals2000A.all', source=__NAME__, group=cgroup)

# Define the barycorrpy iers a url
CDict.set('BERV_IERS_AURL',
          value='ftp://cddis.gsfc.nasa.gov/pub/products/iers/finals2000A.all',
          source=__NAME__, group=cgroup)

# Define barycorrpy leap directory
CDict.set('BERV_LEAPDIR', value='./data/core/barycorrpy/', source=__NAME__, group=cgroup)

# Define whether to update leap seconds if older than 6 months
CDict.set('BERV_LEAPUPDATE', value=True, source=__NAME__, group=cgroup)

# Define the accuracy of the estimate (for logging only) [m/s]
CDict.set('BERV_EST_ACC', value=10.0, source=__NAME__, group=cgroup)

# Define the order to plot in summary plots
CDict.set('PLOT_ORDER', value=4, source=__NAME__, group=cgroup)

# Define the wavelength lower bounds for s1d plots
# (must be a string list of floats) defines the lower wavelength in nm
CDict.set('S1D_PLOT_ZOOM1', value=[990, 1100, 1200, 1250, 1700],
          source=__NAME__, group=cgroup)

# Define the wavelength upper bounds for s1d plots
# (must be a string list of floats) defines the upper wavelength in nm
CDict.set('S1D_PLOT_ZOOM2', value=[1050, 1200, 1210, 1300, 1800],
          source=__NAME__, group=cgroup)

# define custom bands
PHOT_BANDS = dict()
PHOT_BANDS['Y'] = apero_base.PHOT_BANDS['Y']
PHOT_BANDS['J'] = apero_base.PHOT_BANDS['J']
PHOT_BANDS['H'] = apero_base.PHOT_BANDS['H']

# Photometric bands to use in peak-2-peak calculation (and their definitions)
CDict.add('MEAS_SNR_PHOT_BANDS', value=PHOT_BANDS,
          dtype=dict, source=__NAME__, group=cgroup,
          description='Photometric bands to use in peak-2-peak calculation '
                       '(and their definitions)')

# =============================================================================
# CALIBRATION: WAVE GENERAL SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.GEN'
# Define the coefficients of the fit of 1/m vs d
CDict.set('CAVITY_1M_FILE', value='cavity_length_m_fit.dat', source=__NAME__, group=cgroup)

# Define the coefficients of the fit of wavelength vs d
CDict.set('CAVITY_LL_FILE', value='cavity_length_ll_fit.dat', source=__NAME__, group=cgroup)

# Define wave reference fiber (controller fiber)
CDict.set('REF_FIBER', value='A', source=__NAME__, group=cgroup)

# Define the initial value of FP effective cavity width 2xd in nm
CDict.set('GUESS_CAVITY_WID', value=2.4e7, source=__NAME__, author='EA', group=cgroup)

# Define the wave solution polynomial fit degree
CDict.set('WAVESOL_FIT_DEG', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the cavity fit polynomial fit degree for wave solution
CDict.set('CAVITY_FIT_DEG', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the number of sigmas to use in wave sol robust fits
CDict.set('NSIG_CUT', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the minimum number of HC lines in an order to try to find
# absolute numbering
CDict.set('MIN_HC_LINES', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the minimum number of FP lines in an order to try to find
# absolute numbering
CDict.set('MIN_FP_LINES', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the maximum offset in FP peaks to explore when FP peak counting
CDict.set('MAX_FP_COUNT_OFFSET', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the number of iterations required to converge the FP peak counting
# offset loop
CDict.set('FP_COUNT_OFFSET_ITRS', value=3, source=__NAME__, author='EA', group=cgroup)

# Define the number of iterations required to converge on a cavity fit
# (first time this is done)
CDict.set('CAVITY_FIT_ITRS1', value=3, source=__NAME__, author='EA', group=cgroup)

# Define the number of iterations required to check order offset
CDict.set('ORDER_OFFSET_ITRS', value=2, source=__NAME__, author='EA', group=cgroup)

# Define the maximum bulk offset of lines in an order can have
CDict.set('MAX_ORDER_BULKOFFSET', value=10, source=__NAME__, author='EA', group=cgroup)

# Define the required precision that the cavity width change must converge
# to (will be a fraction of the error)
CDict.set('DCAVITY_ERR_THRES', value=1.0e-2, source=__NAME__, author='EA', group=cgroup)

# Define the number of iterations required to converge on a cavity fit
# (second time this is done)
CDict.set('CAVITY_FIT_ITRS2', value=3, source=__NAME__, author='EA', group=cgroup)

# Define the odd ratio that is used in generating the weighted mean
CDict.set('HC_VEL_ODDRATIO', value=1.0e-2, source=__NAME__, author='EA', group=cgroup)

# Define orders that we cannot fit HC or FP lines to (list of strings)
CDict.set('REMOVE_ORDERS', value=[44, 45], source=__NAME__, group=cgroup)

# Define the number of iterations required to do the final fplines wave solution
CDict.set('FWAVESOL_ITRS', value=3, source=__NAME__, author='EA', group=cgroup)

# Define the wave fiber comparison plot order number
CDict.set('FIBER_COMP_PLOT_ORD', value=53, source=__NAME__, group=cgroup)

# Define the line list file (located in the DRS_WAVE_DATA directory)
CDict.set('LINELIST_FILE', value='catalogue_UNe_update230322.csv',
          source=__NAME__, author='EA', group=cgroup)  # 'catalogue_UNe.dat'

# Define the line list file format (must be astropy.table format)
CDict.set('LINELIST_FMT', value='ascii.csv', source=__NAME__,
          author='EA', group=cgroup)  # 'ascii.tab'

# Define the line list file column names
# and must be equal to the number of columns in file)
CDict.set('LINELIST_COLS', value=['ll', 'amp', 'kind'], source=__NAME__,
          author='EA', group=cgroup)

# Define the line list file row the data starts
CDict.set('LINELIST_START', value=1, source=__NAME__, author='EA', group=cgroup)  # 0

# Define the line list file wavelength column and amplitude column
# Must be in WAVE_LINELIST_COLS
CDict.set('LINELIST_WAVECOL', value='ll', source=__NAME__, author='EA', group=cgroup)
CDict.set('LINELIST_AMPCOL', value='amp', source=__NAME__, author='EA', group=cgroup)

# Define whether to always extract HC/FP files in the wave code (even if they
# have already been extracted
CDict.set('ALWAYS_EXTRACT', value=False, source=__NAME__, author='EA', group=cgroup)

# Define the type of file to use for wave solution (currently allowed are
# 'E2DS' or 'E2DSFF'
CDict.set('EXTRACT_TYPE', value='E2DSFF', source=__NAME__, author='EA', group=cgroup)

# Define intercept and slope for a pixel shift
CDict.set('PIXEL_SHIFT_INTER', value=0.0, source=__NAME__,
          author='EA', group=cgroup)  # 6.26637214e+00

CDict.set('PIXEL_SHIFT_SLOPE', value=0.0, source=__NAME__,
          author='EA', group=cgroup)  # 4.22131253e-04

# Defines echelle number of first extracted order
CDict.set('TORDER_START', value=147, source=__NAME__, author='EA', group=cgroup)

# Defines order from which the solution is calculated (first order)
CDict.set('NORD_START', value=0, source=__NAME__, author='EA', group=cgroup)

# Defines order to which the solution is calculated (last order)
CDict.set('NORD_FINAL', value=75, source=__NAME__, author='EA', group=cgroup)

# =============================================================================
# CALIBRATION: WAVE LINES REFERENCE SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.LL'
# min SNR to consider the line (for HC)
CDict.set('NSIG_MIN_HC', value=3, source=__NAME__, author='EA', group=cgroup)

# min SNR to consider the line (for FP)
CDict.set('NSIG_MIN_FP', value=3, source=__NAME__, author='EA', group=cgroup)

# minimum distance to the edge of the array to consider a line
CDict.set('REF_EDGE_WMAX', value=20, source=__NAME__, author='EA', group=cgroup)

# value in pixel (+/-) for the box size around each HC line to perform fit
CDict.set('REF_HC_BOXSIZE', value=13, source=__NAME__, author='EA', group=cgroup)

# get valid hc dprtypes
CDict.set('REF_HC_FIBTYPES', value=['HCONE', 'HCTWO'], source=__NAME__, group=cgroup)

# get valid fp dprtypes
CDict.set('REF_FP_FIBTYPES', value=['FP'], source=__NAME__, group=cgroup)

# get the degree to fix reference wavelength to in hc mode
CDict.set('REF_FITDEG', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the lowest N for fp peaks
CDict.set('REF_FP_NLOW', value=7500, source=__NAME__, author='EA', group=cgroup)

# Define the highest N for fp peaks
CDict.set('REF_FP_NHIGH', value=30000, source=__NAME__, author='EA', group=cgroup)

# Define the number of iterations required to do the FP polynomial inversion
CDict.set('REF_FP_POLYINV', value=4, source=__NAME__, author='EA', group=cgroup)

# Define the guess HC exponential width [pixels]
CDict.set('REF_HC_GUESS_EWID', value=1, source=__NAME__, author='EA', group=cgroup)

# Define the fiber offset (in pixels) away from reference fiber
CDict.set('FIBER_OFFSET_MOD',
          value={"A": 0.0, "B": 0.0},
          source=__NAME__, author='EA', group=cgroup)

# Define the fiber scale factor from reference fiber
CDict.set('FIBER_SCALE_MOD',
          value={"A": 1.0, "B": 1.0},
          source=__NAME__, author='EA', group=cgroup)

# =============================================================================
# CALIBRATION: WAVE RESOLUTION MAP SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.RESMAP'
# Define the number of bins in order direction to use in the resolution map
CDict.set('ORDER_BINS', value=4, source=__NAME__, author='EA', group=cgroup)

# Define the number of bins in spatial direction to use in the resolution map
CDict.set('SPATIAL_BINS', value=4, source=__NAME__, author='EA', group=cgroup)

# Define the low pass filter size for the HC E2DS file in the resolution map
CDict.set('FILT_SIZE', value=101, source=__NAME__, author='EA', group=cgroup)

# Define the broad resolution map velocity cut off (in km/s)
CDict.set('VEL_CUTOFF1', value=20, source=__NAME__, author='EA', group=cgroup)

# Define the tight resolution map velocity cut off (in km/s)
CDict.set('VEL_CUTOFF2', value=5, source=__NAME__, author='EA', group=cgroup)

# =============================================================================
# CALIBRATION: WAVE CCF SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.CCF'
# The value of the noise for wave dv rms calculation
# snr = flux/sqrt(flux + noise^2)
CDict.set('NOISE_SIGDET', value=8.0, source=__NAME__, author='EA', group=cgroup)

# The size around a saturated pixel to flag as unusable for wave dv rms
# calculation
CDict.set('NOISE_BOXSIZE', value=12, source=__NAME__, author='EA', group=cgroup)

# The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
CDict.set('NOISE_THRES', value=1.0e9, source=__NAME__, author='EA', group=cgroup)

# The CCF step size to use for the FP CCF
CDict.set('STEP', value=0.5, source=__NAME__, author='EA', group=cgroup)

# The CCF width size to use for the FP CCF
CDict.set('WIDTH', value=7.5, source=__NAME__, author='EA', group=cgroup)

# The target RV (CCF center) to use for the FP CCF
CDict.set('TARGET_RV', value=0.0, source=__NAME__, author='EA', group=cgroup)

# The detector noise to use for the FP CCF
CDict.set('DETNOISE', value=100.0, source=__NAME__, author='EA', group=cgroup)

# The filename of the CCF Mask to use for the FP CCF
# Note this file is copied over if WAVE_CCF_UPDATE_MASK = True
CDict.set('MASK', value='smart_fp_mask.mas', source=__NAME__,
          author='EA', group=cgroup)

# Define the default CCF MASK normalisation mode for FP CCF
# options are:
# 'None'         for no normalization
# 'all'          for normalization across all orders
# 'order'        for normalization for each order
CDict.set('MASK_NORM', value='order', source=__NAME__,
          author='EA', group=cgroup)

# Define the wavelength units for the mask for the FP CCF
CDict.set('MASK_UNITS', value='nm', source=__NAME__, author='EA', group=cgroup)

# Define the ccf mask path the FP CCF
CDict.set('MASK_PATH', value='ccf_masks/', source=__NAME__,
          author='EA', group=cgroup)

# Define the CCF mask format (must be an astropy.table format)
CDict.set('MASK_FMT', value='ascii', source=__NAME__,
          author='EA', group=cgroup)

# Define the weight of the CCF mask (if 1 force all weights equal)
CDict.set('MASK_MIN_WEIGHT', value=0.0, source=__NAME__,
          author='EA', group=cgroup)

# Define the width of the template line (if 0 use natural)
CDict.set('MASK_WIDTH', value=1.7, source=__NAME__,
          author='EA', group=cgroup)

# Define the number of orders (from zero to ccf_num_orders_max) to use
# to calculate the FP CCF
CDict.set('NORD_MAX', value=48, source=__NAME__,
          author='EA', group=cgroup)

# Define whether to regenerate the fp mask (WAVE_CCF_MASK) when we
# update the cavity width in the reference wave solution recipe
CDict.set('UPDATE_MASK', value=True, source=__NAME__,
          author='EA', group=cgroup)

# Define the width of the lines in the smart mask [km/s]
CDict.set('SMART_MASK_WID', value=1.0, source=__NAME__,
          author='EA', group=cgroup)

# Define the minimum wavelength for the smart mask [nm]
CDict.set('SMART_MASK_MINLAM', value=950, source=__NAME__,
          author='EA', group=cgroup)

# Define the maximum wavelength for the smart mask [nm]
CDict.set('SMART_MASK_MAXLAM', value=2500, source=__NAME__,
          author='EA', group=cgroup)

# Define a trial minimum FP N value (should be lower than true
# minimum FP N value)
CDict.set('SMART_MASK_TRIAL_NMIN', value=9000, source=__NAME__,
          author='EA', group=cgroup)

# Define a trial maximum FP N value (should be higher than true
# maximum FP N value)
CDict.set('SMART_MASK_TRIAL_NMAX', value=27000, source=__NAME__,
          author='EA', group=cgroup)

# Define the converges parameter for dwave in smart mask generation
CDict.set('SMART_MASK_DWAVE_THRES', value=1.0e-9, source=__NAME__,
          author='EA', group=cgroup)

# Define the quality control threshold from RV of CCF FP between reference
# fiber and other fibers, above this limit fails QC [m/s]
# For HE there is an offset between A and B - this will be a high value
# TODO: We should really think about this a bit more
CDict.set('RV_THRES_QC', value=20.0, source=__NAME__, group=cgroup)
# TODO: address this later - should be much lower


# =============================================================================
# CALIBRATION: WAVE HC SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.HC'
# Define the mode to calculate the hc wave solution
# Should be one of the following:
# 0 - Etienne method
CDict.set('MODE', value=0, source=__NAME__, author='EA')

# width of the box for fitting HC lines. Lines will be fitted from -W to +W,
# so a 2*W+1 window
CDict.set('HC_FITBOX_SIZE', value=6, source=__NAME__, author='EA', group=cgroup)

# number of sigma above local RMS for a line to be flagged as such
CDict.set('FITBOX_SIGMA', value=2.0, source=__NAME__, author='EA', group=cgroup)

# the fit degree for the wave hc gaussian peaks fit
CDict.set('FITBOX_GFIT_DEG', value=5, source=__NAME__, author='EA', group=cgroup)

# the RMS of line-fitted line must be between DEVMIN and DEVMAX of the peak
# value must be SNR>5 (or 1/SNR<0.2)
CDict.set('FITBOX_RMS_DEVMIN', value=0.0, source=__NAME__,
          author='EA', group=cgroup)
CDict.set('FITBOX_RMS_DEVMAX', value=0.2, source=__NAME__,
          author='EA', group=cgroup)

# the e-width of the line expressed in pixels.
CDict.set('FITBOX_EWMIN', value=1.0, source=__NAME__,
          author='EA', group=cgroup)  # 0.7
CDict.set('FITBOX_EWMAX', value=3.0, source=__NAME__,
          author='EA', group=cgroup)  # 1.1

# Define the file type for saving the initial guess at the hc peak list
CDict.set('LL_FILEFMT', value='ascii.rst', source=__NAME__,
          author='EA', group=cgroup)

# number of bright lines kept per order
# avoid >25 as it takes super long
# avoid <12 as some orders are ill-defined and we need >10 valid
# lines anyway
# 20 is a good number, and I see no reason to change it
CDict.set('NMAX_BRIGHT', value=20, source=__NAME__, author='EA', group=cgroup)

# Number of times to run the fit triplet algorithm
CDict.set('NITER_FIT_TRIPLET', value=3, source=__NAME__,
          author='EA', group=cgroup)

# Maximum distance between catalog line and init guess line to accept
# line in m/s
CDict.set('MAX_DV_CATLL_GUESS', value=60000, source=__NAME__,
          author='EA', group=cgroup)

# The fit degree between triplets
CDict.set('TFIT_DEG', value=2, source=__NAME__, author='EA', group=cgroup)

# Cut threshold for the triplet line fit [in km/s]
CDict.set('TFIT_CUT_THRES', value=1.0, source=__NAME__,
          author='EA', group=cgroup)

# Minimum number of lines required per order
CDict.set('TFIT_MIN_NLINES', value=10, source=__NAME__,
          author='EA', group=cgroup)

# Minimum total number of lines required
CDict.set('TFIT_MIN_TLINES', value=200, source=__NAME__,
          author='EA', group=cgroup)

# this sets the order of the polynomial used to ensure continuity
#     in the  xpix vs wave solutions by setting the first term = 12,
#     we force that the zeroth element of the xpix of the wavelegnth
#     grid is fitted with a 12th order polynomial as a function of
#     order number (format = string list separated by commas)
# these values are too high and lead to stability problems in the fit
# WAVE_HC_TFIT_ORDER_FIT_CONT.value = '12, 9, 6, 2, 2'

CDict.set('TFIT_ORDER_FIT_CONT', value=[12, 8, 4, 1, 1, 1],
          source=__NAME__, author='EA', group=cgroup)

# Number of times to loop through the sigma clip for triplet fit
CDict.set('TFIT_SIGCLIP_NUM', value=20, source=__NAME__,
          author='EA', group=cgroup)

# Sigma clip threshold for triplet fit
CDict.set('TFIT_SIGCLIP_THRES', value=3.5, source=__NAME__,
          author='EA', group=cgroup)

# Define the distance in m/s away from the center of dv hist points
# outside will be rejected [m/s]
CDict.set('TFIT_DVCUT_ORDER', value=2000, source=__NAME__,
          author='EA', group=cgroup)
CDict.set('TFIT_DVCUT_ALL', value=5000, source=__NAME__,
          author='EA', group=cgroup)

# Define the resolution and line profile map size (y-axis by x-axis)
CDict.set('RESMAP_SIZE', value=[5, 4], source=__NAME__,
          author='EA', group=cgroup)

# Define the maximum allowed deviation in the RMS line spread function
CDict.set('RES_MAXDEV_THRES', value=8, source=__NAME__,
          author='EA', group=cgroup)

# Quality control criteria if sigma greater than this many sigma fails
CDict.set('QC_SIG_MAX', value=8, source=__NAME__,
          author='EA', group=cgroup)

# Defines the dv span for PLOT_WAVE_HC_RESMAP debug plot, should be a
# string list containing a min and max dv value
CDict.set('RESMAP_DVSPAN', value=[-15, 15], source=__NAME__,
          author='EA', group=cgroup)

# Defines the x limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
# string list containing a min and max x value
CDict.set('RESMAP_XLIM', value=[-8.0, 8.0], source=__NAME__,
          author='EA', group=cgroup)

# Defines the y limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
# string list containing a min and max y value
CDict.set('RESMAP_YLIM', value=[-0.05, 0.7], source=__NAME__,
          author='EA', group=cgroup)

# Define whether to fit line profiles with "gaussian" or "super-gaussian"
CDict.set('RESMAP_FITTYPE', value='super-gaussian', source=__NAME__,
          group=cgroup)

# Define the sigma clip for line profiles for the resolution map
CDict.set('RESMAP_SIGCLIP', value=0.2, source=__NAME__,
          author='EA', group=cgroup)

# =============================================================================
# CALIBRATION: WAVE LITTROW SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.LIT'
# Define the order to start the Littrow fit from for the HC wave solution
CDict.set('ORDER_INIT1', value=0, source=__NAME__, group=cgroup)

# Define the order to start the Littrow fit from for the FP wave solution
# TODO: Note currently used
CDict.set('ORDER_INIT2', value=0, source=__NAME__, group=cgroup)

# Define the order to end the Littrow fit at for the HC wave solution
CDict.set('ORDER_FINAL1', value=75, source=__NAME__, group=cgroup)

# Define the order to end the Littrow fit at for the FP wave solution
# TODO: Note currently used
CDict.set('ORDER_FINAL2', value=75, source=__NAME__, group=cgroup)

# Define orders to ignore in Littrow fit
CDict.set('REMOVE_ORDERS', value=[], source=__NAME__, group=cgroup)

# Define the littrow cut steps for the HC wave solution
CDict.set('CUT_STEP1', value=250, source=__NAME__, group=cgroup)

# Define the littrow cut steps for the FP wave solution
CDict.set('CUT_STEP2', value=500, source=__NAME__, group=cgroup)

# Define the fit polynomial order for the Littrow fit (fit across the orders)
# for the HC wave solution
CDict.set('FIG_DEG1', value=8, source=__NAME__, group=cgroup)  # 5  # 4

# Define the fit polynomial order for the Littrow fit (fit across the orders)
# for the FP wave solution
CDict.set('FIG_DEG2', value=8, source=__NAME__, group=cgroup)  # 4

# Define the order fit for the Littrow solution (fit along the orders)
# TODO needs to be the same as ic_ll_degr_fit
CDict.set('EXT_ORDER_FIT_DEG', value=4, source=__NAME__, group=cgroup)  # 5  # 4

# Maximum littrow RMS value
CDict.set('QC_RMS_MAX', value=0.3, source=__NAME__, group=cgroup)

# Maximum littrow Deviation from wave solution (at x cut points)
CDict.set('QC_DEV_MAX', value=0.9, source=__NAME__, group=cgroup)

# =============================================================================
# CALIBRATION: WAVE FP SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.FP'
# Define the mode to calculate the fp+hc wave solution
# Should be one of the following:
# 0 - following Bauer et al 15 (previously WAVE_E2DS_EA)
# 1 - following C Lovis (previously WAVE_NEW)
CDict.set('MODE', value=1, source=__NAME__, group=cgroup)

# Define the initial value of FP effective cavity width 2xd in nm
# 2xd = 24.5 mm = 24.5e6 nm for SPIRou
CDict.set('DOPD0', value=2.4e7, source=__NAME__, group=cgroup)

# Define the polynomial fit degree between FP line numbers and the
# measured cavity width for each line
CDict.set('CAVFIT_DEG', value=9, source=__NAME__, group=cgroup)

# Define the FP jump size that is too large
CDict.set('LARGE_JUMP', value=250, source=__NAME__, group=cgroup)

# Index of FP line to start order cross-matching from
CDict.set('CROSSM_INDEX', value=-2, source=__NAME__, group=cgroup)

# Define the percentile to normalize the spectrum to (per order)
# used to determine FP peaks (peaks must be above a normalised limit
# Defined in WAVE_FP_PEAK_LIM
CDict.set('NORM_PTILE', value=95, source=__NAME__, group=cgroup)

# Define the normalised limit below which FP peaks are not used
CDict.set('PEAK_LIM', value=0.1, source=__NAME__, group=cgroup)

# Define pixel to pixel width that is too large (removed from FP peaks)
CDict.set('P2P_WID_CUT', value=30, source=__NAME__, group=cgroup)

# Define the minimum instrumental error
CDict.set('ERR_XMIN', value=0.01, source=__NAME__,
          author='EA', group=cgroup)  # 0.03

# Define the wavelength fit polynomial order
CDict.set('LL_DEGR_FIT', value=4, source=__NAME__,
          author='EA', group=cgroup)  # 5   #4  # 4

# Define the max rms for the wavelength sigma-clip fit
CDict.set('MAX_LLFIT_RMS', value=3.0, source=__NAME__,
          author='EA', group=cgroup)

# Define the weight threshold (small number) below which we do not keep fp
# lines
CDict.set('WEIGHT_THRES', value=1.0e-30, source=__NAME__,
          author='EA', group=cgroup)

# Minimum blaze threshold to keep FP peaks
CDict.set('BLAZE_THRES', value=0.3, source=__NAME__,
          author='EA', group=cgroup)

# Minimum FP peaks pixel separation fraction diff. from median
CDict.set('XDIF_MIN', value=0.75, source=__NAME__,
          author='EA', group=cgroup)

# Maximum FP peaks pixel separation fraction diff. from median
CDict.set('XDIF_MAX', value=1.25, source=__NAME__,
          author='EA', group=cgroup)

# Maximum fractional wavelength offset between cross-matched FP peaks
CDict.set('LL_OFFSET', value=0.25, source=__NAME__,
          author='EA', group=cgroup)

# Maximum DV to keep HC lines in combined (WAVE_NEW) solution
CDict.set('DV_MAX', value=0.25, source=__NAME__,
          author='EA', group=cgroup)

# Decide whether to refit the cavity width (will update if files do not
# exist)
CDict.set('UPDATE_CAVITY', value=True, source=__NAME__,
          author='EA', group=cgroup)

# Select the FP cavity fitting (WAVE_MODE_FP = 1 only)
# Should be one of the following:
# 0 - derive using the 1/m vs d fit from HC lines
# 1 - derive using the ll vs d fit from HC lines
CDict.set('CAVFIT_MODE', value=1, source=__NAME__,
          author='EA', group=cgroup)

# Select the FP wavelength fitting (WAVE_MODE_FP = 1 only)
# Should be one of the following:
# 0 - use fit_1d_solution function
# 1 - fit with sigma-clipping and mod 1 pixel correction
CDict.set('LLFIT_MODE', value=1, source=__NAME__,
          author='EA', group=cgroup)

# Minimum FP peaks wavelength separation fraction diff. from median
CDict.set('LLDIF_MIN', value=0.75, source=__NAME__,
          author='EA', group=cgroup)

# Maximum FP peaks wavelength separation fraction diff. from median
CDict.set('LLDIF_MAX', value=1.25, source=__NAME__,
          author='EA', group=cgroup)

# Sigma-clip value for sigclip_polyfit
CDict.set('SIGCLIP', value=7, source=__NAME__,
          author='EA', group=cgroup)

# First order for multi-order wave fp plot
CDict.set('PLOT_MULTI_INIT', value=20, source=__NAME__,
          author='EA', group=cgroup)

# Number of orders in multi-order wave fp plot
CDict.set('PLOT_MULTI_NBO', value=5, source=__NAME__,
          author='EA', group=cgroup)

# Define the dprtype for generating FPLINES (string list)
CDict.set('DPRLIST', value=['OBJ_FP'], source=__NAME__,
          author='EA', group=cgroup)

# Define the override for reference fiber for generating FPLINES
# None for no override
CDict.set('FIBER_TYPES', value=[], source=__NAME__,
          author='EA', group=cgroup)

# =============================================================================
# CALIBRATION: WAVE NIGHT SETTINGS
# =============================================================================
cgroup = 'CAL.WAVE.NIGHT'
# number of iterations for hc convergence
CDict.set('NIGHT_NITER1', value=4, source=__NAME__, group=cgroup)

# number of iterations for fp convergence
CDict.set('NIGHT_NITER2', value=3, source=__NAME__, group=cgroup)

# starting points for the cavity corrections
CDict.set('DCAVITY', value=0, source=__NAME__, group=cgroup)

# Define the sigma clip value to remove bad hc lines
CDict.set('HC_SIGCLIP', value=50, source=__NAME__, group=cgroup)

# median absolute deviation cut off
CDict.set('MED_ABSDEV', value=5, source=__NAME__, group=cgroup)

# sigma clipping for the fit
CDict.set('NSIG_FIT_CUT', value=7, source=__NAME__, group=cgroup)

# wave night plot hist number of bins
CDict.set('PLT_NBINS', value=51, source=__NAME__, group=cgroup)

# wave night plot hc bin lower bound in multiples of rms
CDict.set('PLT_BINL', value=-20, source=__NAME__, group=cgroup)

# wave night plot hc bin upper bound in multiples of rms
CDict.set('PLT_BINU', value=20, source=__NAME__, group=cgroup)

# =============================================================================
# OBJ.LIST: OBJECT LIST SETTINGS
# =============================================================================
cgroup = 'OBJ.LIST'
# Define the SIMBAD TAP url
CDict.set('SIMBAD_TAPURL',
          value='http://simbad.cds.unistra.fr/simbad/sim-tap',
          source=__NAME__, group=cgroup)

# Define the TAP Gaia URL (for use in crossmatching to Gaia via astroquery)
CDict.set('GAIA_URL',
          value='https://gea.esac.esa.int/tap-server/tap',
          source=__NAME__, group=cgroup)

# Define the google sheet to use for crossmatch (may be set to a directory for
# completely offline reduction)
CDict.set('GSHEET_URL',
          value='1dOogfEwC7wAagjVFdouB1Y1JdF9Eva4uDW6CTZ8x2FM', source=__NAME__, group=cgroup)

# Define the google sheet objname list main list id number (may be set to a
# csv file for completely offline reduction)
CDict.set('GSHEET_MAINLIST_ID', value='0', source=__NAME__, group=cgroup)

# Define the google sheet objname list pending list id number (may be set to a
# csv file for completely offline reduction)
CDict.set('GSHEET_PENDLIST_ID', value='623506317', source=__NAME__, group=cgroup)

# Define the google sheet objname list reject list id number
CDict.set('GSHEET_REJECTLIST_ID', value='2006484513', source=__NAME__, group=cgroup)

# Define the bad list header key
CDict.set('REJECT_DRS_HKEY', value=None, source=__NAME__, group=cgroup)

# Define the bad list google spreadsheet value column
CDict.set('REJECT_VALCOL', value='IDENTIFIER', source=__NAME__, group=cgroup)

# Define the bad list google spreadsheet mask column for preprocessing
CDict.set('REJECT_MASKCOL', value='PP', source=__NAME__, group=cgroup)

# Define the google sheet bibcode id number
CDict.set('GSHEET_BIBCODE_UD', value='956956617', source=__NAME__, group=cgroup)

# Define the google sheet user url object list (None for no user list)
# (may be set to a directory for completely offline reduction)
CDict.set('GSHEET_USER_URL', value='None', source=__NAME__, group=cgroup)

# Define the google sheet user id object list id number (may be set to a
# csv file for completely offline reduction)
CDict.set('GSHEET_USER_ID', value='0', source=__NAME__, group=cgroup)

# Define whether to resolve from local database (via drs_database / drs_db)
CDict.set('RESOLVE_FROM_DB', value=True, source=__NAME__, group=cgroup)

# Define whether to resolve from gaia id (via TapPlus to Gaia) if False
# ra/dec/pmra/pmde/plx will always come from header
CDict.set('RESOLVE_FROM_GAIAID', value=True, source=__NAME__, group=cgroup)

# Define whether to get Gaia ID / Teff / RV from google sheets if False
# will try to resolve if gaia ID given otherwise will use ra/dec if
# OBJ_LIST_RESOLVE_FROM_COORDS = True else will default to header values
CDict.set('RESOLVE_FROM_GLIST', value=True, source=__NAME__, group=cgroup)

# Define whether to get Gaia ID from header RA and Dec (basically if all other
# option fails) - WARNING - this is a crossmatch so may lead to a bad
# identification of the gaia id - not recommended
CDict.set('RESOLVE_FROM_COORDS', value=False, source=__NAME__, group=cgroup)

# Define the gaia epoch to use in the gaia query
CDict.set('GAIA_EPOCH', value=2015.5, source=__NAME__, group=cgroup)

# Define the radius for crossmatching objects (in both lookup table and query)
# measured in arc sec (only used if OBJ_LIST_RESOLVE_FROM_COORDS = True)
CDict.set('CM_RADIUS', value=180.0, source=__NAME__, group=cgroup)

# Define the gaia parallax limit for using gaia point meansure in mas
# (only used if OBJ_LIST_RESOLVE_FROM_COORDS = True)
CDict.set('GAIA_PLX_LIM', value=0.5, source=__NAME__, group=cgroup)

# Define the gaia magnitude cut (rp mag) to use in the gaia query
# (only used if OBJ_LIST_RESOLVE_FROM_COORDS = True)
CDict.set('GAIA_MAGCUT', value=15.0, source=__NAME__, group=cgroup)

# Define the google sheet to use for update the reject list
CDict.set('RLIST_GSHEET_URL',
          value='1gvMp1nHmEcKCUpxsTxkx-5m115mLuQIGHhxJCyVoZCM',
          source=__NAME__, group=cgroup)

# Define the google sheet id to use for update the reject list
CDict.set('RLIST_GSHEET_MAINLIST_ID', value='768446388',
          source=__NAME__, group=cgroup)

# Define the google sheet name to use for the reject list
CDict.set('RLIST_GSHEET_SHEETNAME', value='NIRPS_HA', source=__NAME__, group=cgroup)

# gaia col name in google sheet
CDict.set('GAIA_COLNAME', value='GAIADR2ID', source=__NAME__, group=cgroup)
# object col name in google sheet
CDict.set('OBJ_COLNAME', value='OBJNAME', source=__NAME__, group=cgroup)
# alias col name in google sheet
CDict.set('ALIAS_COLNAME', value='ALIASES', source=__NAME__, group=cgroup)
# rv col name in google sheet
CDict.set('RV_COLNAME', value='RV', source=__NAME__, group=cgroup)
CDict.set('RVREF_COLNAME', value='RV_REF', source=__NAME__, group=cgroup)
# teff col name in google sheet
CDict.set('TEFF_COLNAME', value='TEFF', source=__NAME__, group=cgroup)
CDict.set('TEFFREFF_COLNAME', value='TEFF_REF', source=__NAME__, group=cgroup)
# Reject like google columns
CDict.set('REJECT_IDENT_COLNAME', value='ODOMETER', source=__NAME__, group=cgroup)
CDict.set('REJECT_PP_COLNAME', value='PP', source=__NAME__, group=cgroup)
CDict.set('REJECT_RV_COLNAME', value='RV', source=__NAME__, group=cgroup)

# =============================================================================
# OBJECT: SKY CORR SETTINGS
# =============================================================================
cgroup = 'OBJ.SKY_CORR'
# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
# input sky files
CDict.set('SKYMODEL_FILETYPE', value='EXT_E2DS_FF', source=__NAME__)

# Define the order to get the snr from (for input data qc check)
CDict.set('MODEL_EXT_SNR_ORDER', value=59, source=__NAME__, author='EA', group=cgroup)

# Define the minimum exptime to use a sky in the model [s]
CDict.set('MODEL_MIN_EXPTIME', value=300, source=__NAME__, author='EA', group=cgroup)

# Define the maximum number of files to have open simultaneously
CDict.set('MODEL_MAX_OPEN_FILES', value=10, source=__NAME__, group=cgroup)

# Define the sigma that positive excursions need to have to be identified
# as lines
CDict.set('MODEL_LINE_SIG', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the erosion size to use on a line
CDict.set('MODEL_LINE_ERODE_SIZE', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the dilatation size to use on a line
CDict.set('MODEL_LINE_DILATE_SIZE', value=27, source=__NAME__, author='EA', group=cgroup)

# Define the number of weight iterations to use when constructing sky model
# weight vector
CDict.set('MODEL_WEIGHT_ITERS', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the erosion size for the sky model line weight calculation
CDict.set('MODEL_WEIGHT_ERODE_SIZE', value=3, source=__NAME__, author='EA', group=cgroup)

# Define the allowed DPRTYPEs for sky correction
CDict.set('ALLOWED_DPRTYPES',
          value=[],
          source=__NAME__, group=cgroup)

# Define the number of iterations used to create sky correction weights
CDict.set('WEIGHT_ITERS', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the size of the fine low pass filter (must be an odd integer)
CDict.set('LOWPASS_SIZE1', value=51, source=__NAME__, author='EA', group=cgroup)

# Define the size of the coarse low pass filter (must be an odd integer)
CDict.set('LOWPASS_SIZE2', value=101, source=__NAME__, author='EA', group=cgroup)

# Define the number of iterations to use for the coarse low pass filter
CDict.set('LOWPASS_ITRS', value=2, source=__NAME__, author='EA', group=cgroup)

# Define the number of sigma threshold for sky corr sigma clipping
CDict.set('NSIG_THRES', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the flux ratio of sky lines that can not be corrected for
CDict.set('RATIO_THRES', value=4, source=__NAME__, author='EA', group=cgroup)

# =============================================================================
# OBJECT: TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJ.TELL.GEN'
# Define the name of the tapas file used
CDict.set('TAPAS_FILE', value='tapas_all_sp.fits.gz', source=__NAME__, group=cgroup)

# Define the format (astropy format) of the tapas file "TAPAS_FILE"
CDict.set('TAPAS_FILE_FMT', value='fits', source=__NAME__, group=cgroup)

# The allowed input DPRTYPES for input telluric files
CDict.set('ALLOWED_DPRTYPES',
          value=['OBJ_DARK', 'OBJ_FP', 'OBJ_SKY', 'TELLU_SKY', 'FLUXSTD_SKY'],
          source=__NAME__, group=cgroup)

# the INPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
# input telluric files
CDict.set('FILETYPE', value='EXT_E2DS_FF', source=__NAME__, group=cgroup)

# the fiber required for input template files
CDict.set('FIBER_TYPE', value='A', source=__NAME__, group=cgroup)

# Define level above which the blaze is high enough to accurately
# measure telluric
CDict.set('CUT_BLAZE_NORM', value=0.2, source=__NAME__, group=cgroup)

# Define telluric include/exclude list directory
CDict.set('LIST_DIR', value='telluric/', source=__NAME__, group=cgroup)

# Define telluric white list name
CDict.set('ALLOWLIST_NAME', value='tellu_whitelist.txt', source=__NAME__, group=cgroup)

# Define telluric black list name
CDict.set('REJECTLIST_NAME', value='tellu_blacklist.txt', source=__NAME__, group=cgroup)

# Force only pre-cleaning (not recommended - only for debugging)
CDict.set('ONLY_PRECLEAN', value=False, source=__NAME__, group=cgroup)

# Whether to fit line of sight velocity in telluric pre-cleaning
CDict.set('ABSO_FIT_LOSVEL', value=False, source=__NAME__, group=cgroup)

# Define bad wavelength regions to mask before correcting tellurics
bad_regions = [(1370, 1410), (1850, 2000)]
CDict.set('BAD_WAVE_REGIONS', value=bad_regions, source=__NAME__, group=cgroup)

# =============================================================================
# OBJECT: TELLURIC PRE-CLEANING SETTINGS
# =============================================================================
cgroup = 'OBJ.TELL.PCLEAN'
# Define whether we do pre-cleaning
CDict.set('DO_PRECLEANING', value=True, source=__NAME__, group=cgroup)

# Define whether we do finite resolution correct (if we have a template)
CDict.set('DO_FINITE_RES_CORR', value=True, source=__NAME__, group=cgroup)

# width in km/s for the ccf scan to determine the abso in pre-cleaning
CDict.set('CCF_SCAN_RANGE', value=25, source=__NAME__, group=cgroup)

# Define whether to clean OH lines
CDict.set('CLEAN_OHLINES', value=False, source=__NAME__, group=cgroup)

# Define the number of bright OH lines that will be individually adjusted
# in amplitude. Done only on lines that are at an SNR > 1
CDict.set('OHLINE_N_BRIGHT', value=300, source=__NAME__, group=cgroup)

# Define the OH line pca file
CDict.set('OHLINE_PCA_FILE', value='sky_PCs.fits', source=__NAME__, group=cgroup)

# Define the orders not to use in pre-cleaning fit (due to thermal
# background)
CDict.set('REMOVE_ORDERS', value=[43, 44, 45], source=__NAME__, group=cgroup)

# Define the minimum snr to accept orders for pre-cleaning fit
CDict.set('SNR_MIN_THRES', value=3.0, source=__NAME__, group=cgroup)

# Define the telluric trans other abso CCF file
CDict.set('OTHERS_CCF_FILE', value='trans_others_abso_ccf.mas',
          source=__NAME__, group=cgroup)

# Define the telluric trans water abso CCF file
CDict.set('WATER_CCF_FILE', value='trans_h2o_abso_ccf.mas', source=__NAME__, group=cgroup)

# Define dexpo convergence threshold
CDict.set('DEXPO_CONV_THRES', value=1.0e-3, source=__NAME__, group=cgroup)

# Define the maximum number of iterations to try to get dexpo
# convergence
CDict.set('DEXPO_MAX_ITR', value=40, source=__NAME__, group=cgroup)

# Define the kernel threshold in abso_expo
CDict.set('ABSO_EXPO_KTHRES', value=1.0e-6, source=__NAME__, group=cgroup)

# Define the gaussian width of the kernel used in abso_expo
CDict.set('ABSO_EXPO_KWID', value=4.0, source=__NAME__, group=cgroup)

# Define the gaussian exponent of the kernel used in abso_expo
# a value of 2 is gaussian, a value >2 is boxy
CDict.set('ABSO_EXP_KEXP', value=2.20, source=__NAME__, group=cgroup)

# Define the transmission threshold (in exponential form) for keeping
# valid transmission
CDict.set('TRANS_THRES', value=-1, source=__NAME__, group=cgroup)

# Define the threshold for discrepant transmission (in sigma)
CDict.set('TRANS_SIGLIM', value=10, source=__NAME__, group=cgroup)

# Define whether to force airmass fit to header airmass value
CDict.set('FORCE_AIRMASS', value=False, source=__NAME__, group=cgroup)

# set the typical water abso exponent. Compare to values in header for
# high-snr targets later
CDict.set('DWATER_ABSO', value=8.0, source=__NAME__, group=cgroup)

# set the lower and upper bounds (String list) for the exponent of
# the other species of absorbers as a ratio to the airmass
# i.e. value/airmass compared to bound
CDict.set('OTHER_BOUNDS', value=[0.8, 1.5], source=__NAME__, group=cgroup)

# set the lower and upper bounds (string list) for the exponent of
# water absorber as a ratio to the airmass i.e. value/airmass compared to bound
CDict.set('WATER_BOUNDS', value=[0.1, 20], source=__NAME__, group=cgroup)

# set the plot order for the finite resolution plot (somewhere around 1.45 um)
CDict.set('FINITE_RES_ORDER', value=49, source=__NAME__, group=cgroup)

# =============================================================================
# OBJECT: MAKE TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJ.TELL.MAKE'
# value below which the blaze in considered too low to be useful
# for all blaze profiles, we normalize to the 95th percentile.
# That's pretty much the peak value, but it is resistent to
# eventual outliers
CDict.set('BLAZE_PTILE', value=95, source=__NAME__, group=cgroup)
CDict.set('CUT_BLAZE_NORM', value=0.1, source=__NAME__, group=cgroup)

# Define list of absorbers in the tapas fits table
CDict.set('ABSORBERS',
          value=['combined', 'h2o', 'o3', 'n2o', 'o2', 'co2', 'ch4'],
          source=__NAME__, group=cgroup)

# Define the default convolution width [in pixels]
CDict.set('DEF_CONV_WID', value=100, source=__NAME__, group=cgroup)

# median-filter the template. we know that stellar features
# are very broad. this avoids having spurious noise in our
# templates [pixel]
CDict.set('TEMP_MED_FILT', value=15, source=__NAME__, group=cgroup)

# Define the orders to plot (not too many)
CDict.set('PLOT_ORDER_NUM', value=[19, 26, 35], source=__NAME__, group=cgroup)

# Define the order to use for SNR check when accepting tellu files
# to the telluDB
CDict.set('QC_SNR_ORDER', value=64, source=__NAME__, group=cgroup)

# Defines the minimum allowed value for the recovered water vapor
# optical depth
CDict.set('TRANS_MIN_WATERCOL', value=0.2, source=__NAME__, group=cgroup)

# Defines the maximum allowed value for the recovered water vapor optical
# depth
CDict.set('TRANS_MAX_WATERCOL', value=99, source=__NAME__, group=cgroup)

# minimum transmission required for use of a given pixel in the TAPAS
# and SED fitting
CDict.set('THRES_TRANSFIT', value=0.3, source=__NAME__, group=cgroup)

# Defines the bad pixels if the spectrum is larger than this value.
# These values are likely an OH line or a cosmic ray
CDict.set('TRANS_FIT_UBAD', value=1.1, source=__NAME__, group=cgroup)

# Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
# accepted to the telluDB
CDict.set('QC_SNR_MIN', value=100, source=__NAME__, group=cgroup)

# Define the allowed difference between recovered and input airmass
# TODO: Change QC once using tapas from La silla
CDict.set('QC_AIRMASS_DIFF', value=1.0, source=__NAME__, group=cgroup)

# Define the sigma cut for tellu transmission model
CDict.set('TRANSMODEL_SIG', value=5.0, source=__NAME__, author='EA', group=cgroup)

# =============================================================================
# OBJECT: FIT TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJ.TELLU.FIT'
# Define the order to use for SNR check when accepting tellu files
# to the telluDB
CDict.set('QC_SNR_ORDER', value=64, source=__NAME__, group=cgroup)

# Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
# accepted to the telluDB
CDict.set('QC_SNR_MIN', value=3, source=__NAME__, group=cgroup)

# The number of principle components to use in PCA fit
CDict.set('NUM_PCA', value=5, source=__NAME__, group=cgroup)

# The number of transmission files to use in the PCA fit (use this number of
# trans files closest in expo_H2O and expo_water
CDict.set('NUM_TRANS', value=50, source=__NAME__, group=cgroup)

# Define whether to add the first derivative and broadening factor to the
# principal components this allows a variable resolution and velocity
# offset of the PCs this is performed in the pixel space and NOT the
# velocity space as this is should be due to an instrument shift
CDict.set('ADD_DERIV_PCA', value=True, source=__NAME__, group=cgroup)

# Define whether to fit the derivatives instead of the principal components
CDict.set('FIT_DERIV_PCA', value=True, source=__NAME__, group=cgroup)

# The number of pixels required (per order) to be able to interpolate the
# template on to a berv shifted wavelength grid
CDict.set('FIT_KEEP_NUM', value=20, source=__NAME__, group=cgroup)

# The minimum transmission allowed to define good pixels (for reconstructed
# absorption calculation)
CDict.set('FIT_MIN_TRANS', value=0.2, source=__NAME__, group=cgroup)

# The minimum wavelength constraint (in nm) to calculate reconstructed
# absorption
CDict.set('LAMBDA_MIN', value=1000.0, source=__NAME__, group=cgroup)

# The maximum wavelength constraint (in nm) to calculate reconstructed
# absorption
CDict.set('LAMBDA_MAX', value=2100.0, source=__NAME__, group=cgroup)

# The gaussian kernel used to smooth the template and residual spectrum [km/s]
CDict.set('KERNEL_VSINI', value=30.0, source=__NAME__, group=cgroup)

# The number of iterations to use in the reconstructed absorption calculation
CDict.set('FIT_ITERS', value=4, source=__NAME__, group=cgroup)

# The minimum log absorption the is allowed in the molecular absorption
# calculation
CDict.set('FIT_RECON_LIM', value=-0.5, source=__NAME__, group=cgroup)

# Define the orders to plot (not too many) for recon abso plot
CDict.set('PLOT_ORDER_NUMS', value=[19, 26, 35], source=__NAME__, group=cgroup)

# Define the selected fit telluric order for debug plots (when not in loop)
CDict.set('SPLOT_ORDER', value=30, source=__NAME__, group=cgroup)

# =============================================================================
# OBJECT: MAKE TEMPLATE SETTINGS
# =============================================================================
cgroup = 'OBJ.TELLU.TEMPLATE'
# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
# input template files
CDict.set('FILETYPE', value='TELLU_OBJ', source=__NAME__, group=cgroup)

# the fiber required for input template files
CDict.set('FIBER_TYPE', value='A', source=__NAME__, group=cgroup)

# the source of the input files (either "disk" or "telludb")
CDict.set('FILESOURCE', value='telludb', source=__NAME__, group=cgroup)

# the order to use for signal to noise cut requirement
CDict.set('SNR_ORDER', value=59, source=__NAME__, group=cgroup)

# The number of iterations to filter low frequency noise before medianing
# the template "big cube" to the final template spectrum
CDict.set('E2DS_ITNUM', value=5, source=__NAME__, group=cgroup)

# The size (in pixels) to filter low frequency noise before medianing
# the template "big cube" to the final template spectrum
CDict.set('E2DS_LOWF_SIZE', value=501, source=__NAME__, group=cgroup)

# The number of iterations to filter low frequency noise before medianing
# the s1d template "big cube" to the final template spectrum
CDict.set('S1D_ITNUM', value=5, source=__NAME__, group=cgroup)

# The size (in pixels) to filter low frequency noise before medianing
# the s1d template "big cube" to the final template spectrum
CDict.set('S1D_LOWF_SIZE', value=501, source=__NAME__, group=cgroup)

# Define the minimum allowed berv coverage to construct a template
# in km/s  (default is double the resolution in km/s)
CDict.set('BERVCOR_QCMIN', value=8.0, source=__NAME__, group=cgroup)

# Define the core SNR in order to calculate required BERV coverage
CDict.set('BERVCOV_CSNR', value=100.0, source=__NAME__, group=cgroup)

# Defome the resolution in km/s for calculating BERV coverage
CDict.set('BERVCOV_RES', value=4.0, source=__NAME__, group=cgroup)

# Define whether to run template making in debug mode (do not bin the
# data when medianing)
CDict.set('DEBUG_MODE', value=False, source=__NAME__, group=cgroup)

# Define the max number of files to be allowed into a bin (if not in debug
# mode)
CDict.set('MAX_OPEN_FILES', value=50, source=__NAME__, group=cgroup)

# Define the fwhm of hot star convolution kernel size in km/s so it is half
# the minimum v sin i of our hot stars
CDict.set('HOTSTAR_KER_VEL', value=25, source=__NAME__, group=cgroup)

# Define the threshold for the Lucy-Richardson deconvolution steps. This is
# the maximum  value of the 99th percentile of the feed-back term
CDict.set('DECONV_ITR_THRES', value=1.0e-3, source=__NAME__, author='EA', group=cgroup)

# Define the max number of iterations to run if the iteration threshold
# is not met
CDict.set('DECONV_ITR_MAX', value=100, source=__NAME__, author='EA', group=cgroup)

# =============================================================================
# CALIBRATION: CCF SETTINGS
# =============================================================================
cgroup = 'OBJ.CCF'
# Define the ccf mask path
CDict.set('MASK_PATH', value='ccf_masks/', source=__NAME__, group=cgroup)

# Define the TEFF mask table for when CCF_DEFAULT_MASK is TEFF
CDict.set('TEFF_MASK_TABLE', value='teff_masks.csv', source=__NAME__, datatype='csv', group=cgroup)

# Define the default CCF MASK to use (filename or TEFF to decide based on
# object temperature) - for TEFF setup see CCF_TEFF_MASK_TABLE file
CDict.set('DEFAULT_MASK', value='TEFF', source=__NAME__, group=cgroup)

# Define the default CCF MASK normalisation mode
# options are:
# 'None'         for no normalization
# 'all'          for normalization across all orders
# 'order'        for normalization for each order
CDict.set('MASK_NORM', value='order', source=__NAME__, group=cgroup)

# Define the wavelength units for the mask
CDict.set('MASK_UNITS', value='nm', source=__NAME__, group=cgroup)

# Define the CCF mask format (must be an astropy.table format)
CDict.set('MASK_FMT', value='ascii', source=__NAME__, group=cgroup)

# Define the weight of the CCF mask (if 1 force all weights equal)
CDict.set('MASK_MIN_WEIGHT', value=0.0, source=__NAME__, group=cgroup)

# Define the width of the template line (if 0 use natural)
CDict.set('MASK_WID', value=1.7, source=__NAME__, group=cgroup)

# Define target rv header null value
# (values greater than absolute value are set to zero)
CDict.set('RV_NULL_VAL', value=1000, source=__NAME__, group=cgroup)

# Define the maximum allowed ratio between input CCF STEP and CCF WIDTH
# i.e. error will be generated if CCF_STEP > (CCF_WIDTH / RATIO)
CDict.set('WID_STEP_RATIO', value=10.0, source=__NAME__, group=cgroup)

# Define the width of the CCF range [km/s]
CDict.set('DEFAULT_WID', value=300.0, source=__NAME__, group=cgroup)

# Define the computations steps of the CCF [km/s]
CDict.set('DEFAULT_STEP', value=0.25, source=__NAME__, group=cgroup)

# The value of the noise for wave dv rms calculation
# snr = flux/sqrt(flux + noise^2)
CDict.set('NOISE_SIGDET', value=8.0, source=__NAME__, group=cgroup)

# The size around a saturated pixel to flag as unusable for wave dv rms
# calculation
CDict.set('NOISE_BOXSIZE', value=12, source=__NAME__, group=cgroup)

# The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
CDict.set('NOISE_THRES', value=1.0e9, source=__NAME__, group=cgroup)

# Define the number of orders (from zero to ccf_num_orders_max) to use
# to calculate the CCF and RV
CDict.set('N_ORD_MAX', value=71, source=__NAME__, group=cgroup)

# Allowed input DPRTYPES for input for CCF recipe
CDict.set('ALLOWED_DPRTYPES',
          value=['OBJ_DARK', 'OBJ_FP', 'OBJ_SKY', 'TELLU_SKY', 'FLUXSTD_SKY'],
          source=__NAME__, group=cgroup)

# Valid DPRTYPES for FP in calibration fiber
CDict.set('VALID_FP_DPRTYPES',
          value=['OBJ_FP'],
          source=__NAME__, group=cgroup)

# Define the KW_OUTPUT types that are valid telluric corrected spectra
CDict.set('CORRECT_TELLU_TYPES', value='TELLU_OBJ', source=__NAME__, group=cgroup)

# The transmission threshold for removing telluric domain (if and only if
# we have a telluric corrected input file
CDict.set('TELLU_THRES', value=0.5, source=__NAME__, group=cgroup)

# The half size (in pixels) of the smoothing box used to calculate what value
# should replace the NaNs in the E2ds before CCF is calculated
CDict.set('FILL_NAN_KERN_SIZE', value=10, source=__NAME__, group=cgroup)

# The step size (in pixels) of the smoothing box used to calculate what value
# should replace the NaNs in the E2ds before CCF is calculated
CDict.set('FILL_NAN_KERN_RES', value=0.1, source=__NAME__, group=cgroup)

# Define the detector noise to use in the ccf
CDict.set('DET_NOISE', value=100.0, source=__NAME__, group=cgroup)

# Define the fit type for the CCF fit
# if 0 then we have an absorption line
# if 1 then we have an emission line
CDict.set('FIT_TYPE', value=0, source=__NAME__, group=cgroup)

# Define the percentile the blaze is normalised by before using in CCF calc
CDict.set('BLAZE_NORM_PTILE', value=90, source=__NAME__, group=cgroup)

# Define the minimum number of sigma the peak CCF must have to be acceptable
CDict.set('NSIG_THRES', value=5, source=__NAME__, author='EA', group=cgroup)

# Define the minimum number of sigma the FWHM of CCF must have to be acceptable
CDict.set('FWHM_SIGCUT', value=8, source=__NAME__, author='EA', group=cgroup)

# Define the top cut of the bisector cut (percent)
CDict.set('BIS_CUT_TOP', value=80, source=__NAME__, author='EA', group=cgroup)

# Define the bottom cut of the bisector cut (percent)
CDict.set('BIS_CUT_BOTTOM', value=30, source=__NAME__, author='EA', group=cgroup)

# =============================================================================
# LBL SETTINGS
# =============================================================================
cgroup = 'OBJ.LBL'
# Define the file definition type (DRSOUTID) for LBL input files
CDict.set('FILE_DEFS', value='TELLU_OBJ', source=__NAME__, group=cgroup)

# Define the dprtype for science files for LBL
CDict.set('DPRTYPES',
          value=['OBJ_DARK', 'OBJ_FP', 'OBJ_SKY', 'TELLU_SKY', 'FLUXSTD_SKY'],
          source=__NAME__, group=cgroup)

# Define the file definition type (DRSOUTID) for lbl input template
CDict.set('TEMPLATE_FILE_DEFS',
          value=['TELLU_TEMP', 'TELLU_TEMP_S1DV'],
          source=__NAME__, group=cgroup)

# Define the DPRTYPE for simultaneous FP files for lbl input
CDict.set('SIM_FP_DPRTYPES',
          value=['OBJ_FP'],
          source=__NAME__, group=cgroup)

# Define whether the LBL directory should use symlinks
CDict.set('SYMLINKS', value=True, source=__NAME__, group=cgroup)

# Define the dictionary of friend and friend teffs for LBL
CDict.set('FRIENDS',
          value={"HD85512": 4411, "GJ9425": 4060, "GL514": 3750,
                 "GJ2066": 3557, "GJ581": 3413, "GJ643": 3306,
                 "GJ3737": 3257, "GL699": 3224, "PROXIMA": 2900},
          source=__NAME__, group=cgroup)

# Define the specific data types (where objname is the data type) for LBL
CDict.set('SPECIFIC_DTYPES', value=['FP', 'LFC'], source=__NAME__,
          group=cgroup)

# Define objnames for which we should recalculate template if it doesn't
# exist (must include FP)
CDict.set('RECAL_TEMPLATES', value=['FP', 'LFC'], source=__NAME__,
          group=cgroup)

# Define which recipes should skip done files
CDict.set('SKIP_DONE', value=['LBL_COMPUTE', 'LBL_MASK'], source=__NAME__,
          group=cgroup)

# Define which object names should be run through LBL compute in parallel
CDict.set('MULTI_OBJLIST', value=['FP'], source=__NAME__, group=cgroup)

# Define the DTEMP gradient files
CDict.set('DTEMP',
          value={"DTEMP3000": "temperature_gradient_3000.fits",
                 "DTEMP3500": "temperature_gradient_3500.fits",
                 "DTEMP4000": "temperature_gradient_4000.fits",
                 "DTEMP4500": "temperature_gradient_4500.fits",
                 "DTEMP5000": "temperature_gradient_5000.fits",
                 "DTEMP5500": "temperature_gradient_5500.fits",
                 "DTEMP6000": "temperature_gradient_6000.fits"},
          source=__NAME__, group=cgroup)

# =============================================================================
# POST PROCESS SETTINGS
# =============================================================================
cgroup = 'OBJ.POST'
# Define whether (by default) to clear reduced directory
CDict.set('CLEAR_RED', value=False, source=__NAME__, group=cgroup)

# Define whether (by default) to overwrite post processed files
CDict.set('OVERWRITE', value=False, source=__NAME__, group=cgroup)

# Define the header keyword store to insert extension comment after
CDict.set('HDREXT_COMMKEY', value='KW_IDENTIFIER', source=__NAME__, group=cgroup)

# =============================================================================
# DEBUG OUTPUT FILE SETTINGS
# =============================================================================
cgroup = 'DEBUG.OUTFILE'
# Whether to save background debug file (large 0.5 GB per file)
# one of these per extraction (lots)
CDict.set('BCKGRD_FILE', value=False, source=__NAME__, group=cgroup)

# Whether to save the E2DSLL file (around 0.05 to 0.1 GB per file)
# one of these per fiber (lots)
CDict.set('E2DSLL_FILE', value=True, source=__NAME__, group=cgroup)

# Whether to save the shape in and out debug files (around 0.1 GB per file)
# but only one set of these per night
CDict.set('SHAPE_FILES', value=False, source=__NAME__, group=cgroup)

# Whether to save the uncorrected for FP C fiber leak files
# (around 0.01 GB per file) one of these per fiber
CDict.set('UNCORR_EXT_FILES', value=False, source=__NAME__, group=cgroup)

# =============================================================================
# DEBUG PLOT SETTINGS
# =============================================================================
cgroup = 'DEBUG.PLOT'
# turn on dark image region debug plot
CDict.set('DARK_IMAGE_REGIONS', value=True, source=__NAME__, group=cgroup)

# turn on dark histogram debug plot
CDict.set('DARK_HISTOGRAM', value=True, source=__NAME__, group=cgroup)

# turn on badpix map debug plot
CDict.set('BADPIX_MAP', value=True, source=__NAME__, group=cgroup)

# turn on localisation the width regions plot
CDict.set('LOC_WIDTH_REGIONS', value=True, source=__NAME__, group=cgroup)

# turn on localisation fiber doublet paroty plot
CDict.set('LOC_FIBER_DOUBLET_PARITY', value=True, source=__NAME__, group=cgroup)

# turn on localisation gap in orders plot
CDict.set('LOC_GAP_ORDERS', value=True, source=__NAME__, group=cgroup)

# turn on localisation image fit plot
CDict.set('LOC_IMAGE_FIT', value=True, source=__NAME__, group=cgroup)

# turn on localisation image corners plot
CDict.set('LOG_IM_CORNER', value=True, source=__NAME__, group=cgroup)

# turn on localisation image regions plot
CDict.set('LOC_IM_REGIONS', value=True, source=__NAME__, group=cgroup)

# turn on the shape dx debug plot
CDict.set('SHAPE_DX', value=True, source=__NAME__, group=cgroup)

# turn on the shape linear transform params plot
CDict.set('SHAPE_LINEAR_TPARAMS', value=True, source=__NAME__, group=cgroup)

# turn on the shape angle offset (all orders in loop) debug plot
CDict.set('SHAPE_ANGLE_OFFSET_ALL', value=True, source=__NAME__, group=cgroup)

# turn on the shape angle offset (one selected order) debug plot
CDict.set('SHAPE_ANGLE_OFFSET', value=True, source=__NAME__, group=cgroup)

# turn on the shape local zoom debug plot
CDict.set('SHAPEL_ZOOM_SHIFT', value=True, source=__NAME__, group=cgroup)

# turn on the flat order fit edges debug plot (loop)
CDict.set('FLAT_ORDER_FIT_EDGES1', value=False, source=__NAME__, group=cgroup)

# turn on the flat order fit edges debug plot (selected order)
CDict.set('FLAT_ORDER_FIT_EDGES2', value=True, source=__NAME__, group=cgroup)

# turn on the flat blaze order debug plot (loop)
CDict.set('FLAT_BLAZE_ORDER1', value=False, source=__NAME__, group=cgroup)

# turn on the flat blaze order debug plot (selected order)
CDict.set('FLAT_BLAZE_ORDER2', value=True, source=__NAME__, group=cgroup)

# turn on thermal background (in extract) debug plot
CDict.set('THERMAL_BACKGROUND', value=True, source=__NAME__, group=cgroup)

# turn on the extraction spectral order debug plot (loop)
CDict.set('EXTRACT_SPECTRAL_ORDER1', value=True, source=__NAME__, group=cgroup)

# turn on the extraction spectral order debug plot (selected order)
CDict.set('EXTRACT_SPECTRAL_ORDER2', value=True, source=__NAME__, group=cgroup)

# turn on the extraction 1d spectrum debug plot
CDict.set('EXTRACT_S1D', value=True, source=__NAME__, group=cgroup)

# turn on the extraction 1d spectrum weight (before/after) debug plot
CDict.set('EXTRACT_S1D_WEIGHT', value=True, source=__NAME__, group=cgroup)

# turn on the wave line fiber comparison plot
CDict.set('WAVE_FIBER_COMPARISON', value=True, source=__NAME__, group=cgroup)

# turn on the wave line fiber comparison plot
CDict.set('WAVE_FIBER_COMP', value=True, source=__NAME__, group=cgroup)

# turn on the wave length vs cavity width plot
CDict.set('WAVE_WL_CAV', value=True, source=__NAME__, group=cgroup)

# turn on the wave diff HC histograms plot
CDict.set('WAVE_HC_DIFF_HIST', value=True, source=__NAME__, group=cgroup)

# turn on the wave lines hc/fp expected vs measured debug plot
# (will plot once for hc once for fp)
CDict.set('WAVEREF_EXPECTED', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution hc guess debug plot (in loop)
CDict.set('WAVE_HC_GUESS', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution hc brightest lines debug plot
CDict.set('WAVE_HC_BRIGHTEST_LINES', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution hc triplet fit grid debug plot
CDict.set('WAVE_HC_TFIT_GRID', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution hc resolution map debug plot
CDict.set('WAVE_HC_RESMAP', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution hc resolution map debug plot
CDict.set('WAVE_RESMAP', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution littrow check debug plot
CDict.set('WAVE_LITTROW_CHECK1', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution littrow extrapolation debug plot
CDict.set('WAVE_LITTROW_EXTRAP1', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution littrow check debug plot
CDict.set('WAVE_LITTROW_CHECK2', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution littrow extrapolation debug plot
CDict.set('WAVE_LITTROW_EXTRAP2', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution final fp order debug plot
CDict.set('WAVE_FP_FINAL_ORDER', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution fp local width offset debug plot
CDict.set('WAVE_FP_LWID_OFFSET', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution fp wave residual debug plot
CDict.set('WAVE_FP_WAVE_RES', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution fp fp_m_x residual debug plot
CDict.set('WAVE_FP_M_X_RES', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution fp interp cavity width 1/m_d hc debug plot
CDict.set('WAVE_FP_IPT_CWID_1MHC', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution fp interp cavity width ll hc and fp debug plot
CDict.set('WAVE_FP_IPT_CWID_LLHC', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution old vs new wavelength difference debug plot
CDict.set('WAVE_FP_LL_DIFF', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution fp multi order debug plot
CDict.set('WAVE_FP_MULTI_ORDER', value=True, source=__NAME__, group=cgroup)

# turn on the wave solution fp single order debug plot
CDict.set('WAVE_FP_SINGLE_ORDER', value=True, source=__NAME__, group=cgroup)

# turn on the wave per night iteration debug plot
CDict.set('WAVENIGHT_ITERPLOT', value=True, source=__NAME__, group=cgroup)

# turn on the wave per night hist debug plot
CDict.set('WAVENIGHT_HISTPLOT', value=True, source=__NAME__, group=cgroup)

# turn on the sky model region plot
CDict.set('TELLU_SKYMODEL_REGION_PLOT', value=True, source=__NAME__, group=cgroup)

# turn on the sky model median plot
CDict.set('TELLU_SKYMODEL_MED', value=True, source=__NAME__, group=cgroup)

# turn on the sky model median plot
CDict.set('TELLU_SKYMODEL_LINEFIT', value=True, source=__NAME__, group=cgroup)

# turn on the sky correction debug plot
CDict.set('TELLU_SKY_CORR_PLOT', value=True, source=__NAME__, group=cgroup)

# turn on the sky correction debug plot
CDict.set('TELLUP_MEAN_RES', value=True, source=__NAME__, group=cgroup)

# turn on the telluric pre-cleaning result debug plot
CDict.set('TELLUP_ABSO_SPEC', value=True, source=__NAME__, group=cgroup)

# turn on the telluric OH cleaning debug plot
CDict.set('TELLUP_CLEAN_OH', value=True, source=__NAME__, group=cgroup)

# turn on the make tellu wave flux debug plot (in loop)
CDict.set('MKTELLU_WAVE_FLUX1', value=False, source=__NAME__, group=cgroup)

# turn on the make tellu wave flux debug plot (single order)
CDict.set('MKTELLU_WAVE_FLUX2', value=True, source=__NAME__, group=cgroup)

# turn on the make tellu model plot
CDict.set('MKTELLU_MODEL', value=True, source=__NAME__, group=cgroup)

# turn on the fit tellu pca component debug plot (in loop)
CDict.set('FTELLU_PCA_COMP1', value=False, source=__NAME__, group=cgroup)

# turn on the fit tellu pca component debug plot (single order)
CDict.set('FTELLU_PCA_COMP2', value=True, source=__NAME__, group=cgroup)

# turn on the fit tellu reconstructed spline debug plot (in loop)
CDict.set('FTELLU_RECON_SPLINE1', value=False, source=__NAME__, group=cgroup)

# turn on the fit tellu reconstructed spline debug plot (single order)
CDict.set('FTELLU_RECON_SPLINE2', value=True, source=__NAME__, group=cgroup)

# turn on the fit tellu wave shift debug plot (in loop)
CDict.set('FTELLU_WAVE_SHIFT1', value=False, source=__NAME__, group=cgroup)

# turn on the fit tellu wave shift debug plot (single order)
CDict.set('FTELLU_WAVE_SHIFT1', value=True, source=__NAME__, group=cgroup)

# turn on the fit tellu reconstructed absorption debug plot (in loop)
CDict.set('FTELLU_RECON_ABSO1', value=True, source=__NAME__, group=cgroup)

# turn on the fit tellu reconstructed absorption debug plot (single order)
CDict.set('FTELLU_RECON_ABSO2', value=True, source=__NAME__, group=cgroup)

# turn on the fit tellu res model debug plot
CDict.set('FTELLU_RES_MODEL', value=True, source=__NAME__, group=cgroup)

# turn on the finite resolution correction debug plot
CDict.set('TELLU_FINITE_RES_CORR', value=True, source=__NAME__, group=cgroup)

# turn on the berv coverage debug plot
CDict.set('MKTEMP_BERV_COV', value=True, source=__NAME__, group=cgroup)

# turn on the template s1d deconvolution plot
CDict.set('MKTEMP_S1D_DECONV', value=True, source=__NAME__, group=cgroup)

# turn on the ccf rv fit debug plot (in a loop around orders)
CDict.set('CCF_RV_FIT_LOOP', value=True, source=__NAME__, group=cgroup)

# turn on the ccf rv fit debug plot (for the mean order value)
CDict.set('CCF_RV_FIT', value=True, source=__NAME__, group=cgroup)

# turn on the ccf spectral order vs wavelength debug plot
CDict.set('CCF_SWAVE_REF', value=False, source=__NAME__, group=cgroup)

# turn on the ccf photon uncertainty debug plot
CDict.set('CCF_PHOTON_UNCERT', value=True, source=__NAME__, group=cgroup)

# =============================================================================
# TOOLS SETTINGS
# =============================================================================
cgroup = 'TOOLS.REPROCESS'
# Define which block kinds to reindex (warning can take a long time)
CDict.set('REINDEX_BLOCKS', value=['raw', 'tmp', 'red', 'out'],
          source=__NAME__, group=cgroup)

# Define whether to use multiprocess "pool" or "process" or use
# "linear" mode when parallelising recipes
CDict.set('MP_TYPE', value='process', source=__NAME__, group=cgroup)

# Define whether to use multiprocess "pool" or "process" or use
# "linear" mode when validating recipes
CDict.set('MP_TYPE_VAL', value='linear', source=__NAME__, group=cgroup)

# Key for use in run files
CDict.set('RUN_KEY', value='ID', source=__NAME__, group=cgroup)

# Define the obs_dir column name for raw file table
CDict.set('OBSDIR_COL', value='OBS_DIR', source=__NAME__, group=cgroup)

# Define the KW_OBJTYPE allowed for a science target
CDict.set('OBJECT_TYPES',
          value=['OBJECT', 'OBJECT,SKY', 'OBJECT,FP', 'OBJECT,DARK'],
          source=__NAME__, group=cgroup)

# Define the pi name column name for raw file table
CDict.set('PI_NAME_COL', value='KW_PI_NAME', source=__NAME__, group=cgroup)

# Define the absolute file column name for raw file table
CDict.set('ABS_FILE_COL', value='ABSPATH', source=__NAME__, group=cgroup)

# Define the modified file column name for raw file table
CDict.set('MODIFIED_COL', value='LAST_MODIFIED', source=__NAME__, group=cgroup)

# Define the sort column (from header keywords) for raw file table
CDict.set('SORTCOL_HDRKEY', value='KW_ACQTIME', source=__NAME__, group=cgroup)

# Define the raw index filename
CDict.set('RAW_INDEX_FILE', value='rawindex.fits', source=__NAME__, group=cgroup)

# Define the sequence (1 of 5, 2 of 5 etc) col for raw file table
CDict.set('SEQ_COL', value='KW_CMPLTEXP', source=__NAME__, group=cgroup)

# Define the time col for raw file table
CDict.set('TIME_COL', value='KW_ACQTIME', source=__NAME__, group=cgroup)

# Define the rejection sql query (between identifier and reject list col)
# must use a valid reject database column and use {identifier} in query
CDict.set('REJECT_SQL', value='FILENAME="{identifier}"',
          source=__NAME__, group=cgroup)

# Define the extra SQL science object select criteria
CDict.set('OBJ_SCI_SQL', value=' AND KW_OBSTYPE LIKE "OBJECT%"',
          source=__NAME__, group=cgroup)

# =============================================================================
# TOOLS: GENERAL SETTINGS
# =============================================================================
cgroup = 'TOOLS.GEN'
# Define whether we try to create a latex summary pdf
# (turn this off if you have any problems with latex/pdflatex)
CDict.set('SUMMARY_LATEX_PDF', value=True, source=__NAME__, group=cgroup)

# Define exposure meter minimum wavelength for mask
CDict.set('EXPMETER_MIN_LAMBDA', value=1478.7, source=__NAME__, group=cgroup)

# Define exposure meter maximum wavelength for mask
CDict.set('EXPMETER_MAX_LAMBDA', value=1823.1, source=__NAME__, group=cgroup)

# Define exposure meter telluric threshold (minimum tapas transmission)
CDict.set('EXPMETER_TELLU_THRES', value=0.95, source=__NAME__, group=cgroup)

# Define the types of file allowed for drift measurement
CDict.set('DRIFT_DPRTYPES',
          value=['FP_FP', 'OBJ_FP', 'DARK_FP'],
          source=__NAME__, group=cgroup)

# Define the fiber dprtype allowed for drift measurement (only FP)
CDict.set('DRIFT_DPR_FIBER_TYPE', value='FP', source=__NAME__, group=cgroup)

# =============================================================================
# End of configuration file
# =============================================================================