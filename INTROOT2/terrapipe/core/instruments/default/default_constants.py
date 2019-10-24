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
    'SKIP_DONE_PP',
    # image constants
    'FIBER_TYPES',
    'INPUT_COMBINE_IMAGES', 'INPUT_FLIP_IMAGE', 'INPUT_RESIZE_IMAGE',
    'IMAGE_X_LOW', 'IMAGE_X_HIGH',
    'IMAGE_Y_LOW', 'IMAGE_Y_HIGH', 'IMAGE_X_LOW', 'IMAGE_X_HIGH',
    'IMAGE_Y_LOW', 'IMAGE_Y_HIGH', 'IMAGE_X_BLUE_LOW',
    'IMAGE_PIXEL_SIZE', 'FWHM_PIXEL_LSF',
    # general calib constants
    'CAVITY_LENGTH_FILE', 'CAVITY_LENGTH_FILE_FMT', 'CAVITY_1M_FILE',
    'CAVITY_LENGTH_FILE_COLS', 'CAVITY_LENGTH_FILE_START', 'CAVITY_LL_FILE',
    'CAVITY_LENGTH_FILE_WAVECOL', 'OBJ_LIST_FILE', 'OBJ_LIST_FILE_FMT',
    'OBJ_LIST_CROSS_MATCH_RADIUS', 'OBJ_LIST_GAIA_URL', 'OBJ_LIST_SIMBAD_URL',
    'OBJ_LIST_GAIA_MAG_CUT', 'OBJ_LIST_GAIA_EPOCH', 'OBJ_LIST_GAIA_PLX_LIM',
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
    'LOC_ORDER_CURVE_DROP', 'LOC_PLOT_CORNER_XZOOM1', 'LOC_PLOT_CORNER_XZOOM2',
    'LOC_PLOT_CORNER_YZOOM1', 'LOC_PLOT_CORNER_YZOOM2', 'LOC_COEFF_SIGCLIP',
    'LOC_COEFFSIG_DEG',
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
    'SHAPE_QC_DXMAP_STD', 'SHAPEOFFSET_XOFFSET',
    'SHAPEOFFSET_BOTTOM_PERCENTILE', 'SHAPEOFFSET_TOP_PERCENTILE',
    'SHAPEOFFSET_TOP_FLOOR_FRAC',
    'SHAPEOFFSET_MED_FILTER_WIDTH', 'SHAPEOFFSET_FPINDEX_MAX',
    'SHAPEOFFSET_VALID_FP_LENGTH', 'SHAPEOFFSET_DRIFT_MARGIN',
    'SHAPEOFFSET_WAVEFP_INV_IT', 'SHAPEOFFSET_MASK_BORDER',
    'SHAPEOFFSET_MIN_MAXPEAK_FRAC', 'SHAPEOFFSET_MASK_PIXWIDTH',
    'SHAPEOFFSET_MASK_EXTWIDTH', 'SHAPEOFFSET_DEVIANT_PMIN',
    'SHAPEOFFSET_DEVIANT_PMAX', 'SHAPEOFFSET_FPMAX_NUM_ERROR',
    'SHAPEOFFSET_FIT_HC_SIGMA', 'SHAPEOFFSET_MAXDEV_THRESHOLD',
    'SHAPEOFFSET_ABSDEV_THRESHOLD', 'SHAPE_UNIQUE_FIBERS',
    'SHAPE_DEBUG_OUTPUTS', 'SHAPE_PLOT_SELECTED_ORDER',
    'SHAPEL_PLOT_ZOOM1', 'SHAPEL_PLOT_ZOOM2',
    # flat constants
    'FF_BLAZE_HALF_WINDOW', 'FF_BLAZE_THRESHOLD', 'FF_BLAZE_DEGREE',
    'FF_RMS_SKIP_ORDERS', 'QC_FF_MAX_RMS', 'FF_PLOT_ORDER',
    'FF_BLAZE_SCUT', 'FF_BLAZE_SIGFIT', 'FF_BLAZE_BPERCENTILE',
    'FF_BLAZE_NITER',
    # extract constants
    'EXT_START_ORDER', 'EXT_END_ORDER', 'EXT_RANGE1', 'EXT_RANGE2',
    'EXT_SKIP_ORDERS', 'EXT_COSMIC_CORRETION', 'EXT_COSMIC_SIGCUT',
    'EXT_COSMIC_THRESHOLD', 'QC_EXT_FLUX_MAX',
    'EXT_S1D_WAVESTART', 'EXT_S1D_WAVEEND', 'EXT_S1D_BIN_UWAVE',
    'EXT_S1D_BIN_UVELO', 'EXT_S1D_EDGE_SMOOTH_SIZE',
    'EXT_ALLOWED_BERV_DPRTYPES', 'EXT_BERV_EST_ACC', 'EXT_BERV_KIND',
    'EXTRACT_PLOT_ORDER', 'EXTRACT_S1D_PLOT_ZOOM1', 'EXTRACT_S1D_PLOT_ZOOM2',
    # thermal constants
    'THERMAL_ALWAYS_EXTRACT', 'THERMAL_CORRETION_TYPE1',
    'THERMAL_CORRETION_TYPE2', 'THERMAL_ORDER',
    'THERMAL_FILTER_WID', 'THERMAL_RED_LIMIT', 'THERMAL_BLUE_LIMIT',
    'THERMAL_THRES_TAPAS', 'THERMAL_ENVELOPE_PERCENTILE',
    'THERMAL_PLOT_START_ORDER',
    # wave general constants
    'WAVE_LINELIST_FILE', 'WAVE_LINELIST_FMT', 'WAVE_LINELIST_AMPCOL',
    'WAVE_LINELIST_COLS', 'WAVE_LINELIST_START', 'WAVE_LINELIST_WAVECOL',
    'WAVE_ALWAYS_EXTRACT', 'WAVE_EXTRACT_TYPE', 'WAVE_FIT_DEGREE',
    'WAVE_PIXEL_SHIFT_INTER', 'WAVE_PIXEL_SHIFT_SLOPE',
    'WAVE_T_ORDER_START', 'WAVE_N_ORD_START', 'WAVE_N_ORD_FINAL',
    # wave hc constants
    'WAVE_MODE_HC', 'WAVE_HC_FITBOX_SIZE', 'WAVE_HC_FITBOX_SIGMA',
    'WAVE_HC_FITBOX_GFIT_DEG', 'WAVE_HC_FITBOX_RMS_DEVMIN',
    'WAVE_HC_FITBOX_RMS_DEVMAX', 'WAVE_HC_FITBOX_EWMIN',
    'WAVE_HC_FITBOX_EWMAX', 'WAVE_HCLL_FILE_FMT',
    'WAVE_HC_NMAX_BRIGHT', 'WAVE_HC_NITER_FIT_TRIPLET',
    'WAVE_HC_MAX_DV_CAT_GUESS', 'WAVE_HC_TFIT_DEG', 'WAVE_HC_TFIT_CUT_THRES',
    'WAVE_HC_TFIT_MINNUM_LINES', 'WAVE_HC_TFIT_MINTOT_LINES',
    'WAVE_HC_TFIT_ORDER_FIT_CONT', 'WAVE_HC_TFIT_SIGCLIP_NUM',
    'WAVE_HC_TFIT_SIGCLIP_THRES', 'WAVE_HC_TFIT_DVCUT_ORDER',
    'WAVE_HC_TFIT_DVCUT_ALL', 'WAVE_HC_RESMAP_SIZE', 'WAVE_HC_RES_MAXDEV_THRES',
    'WAVE_HC_QC_SIGMA_MAX', 'WAVE_HC_RESMAP_DV_SPAN', 'WAVE_HC_RESMAP_XLIM',
    'WAVE_HC_RESMAP_YLIM',
    # wave littrow parameters
    'WAVE_LITTROW_ORDER_INIT_1', 'WAVE_LITTROW_ORDER_INIT_2',
    'WAVE_LITTROW_ORDER_FINAL_1', 'WAVE_LITTROW_ORDER_FINAL_2',
    'WAVE_LITTROW_REMOVE_ORDERS', 'WAVE_LITTROW_CUT_STEP_1',
    'WAVE_LITTROW_CUT_STEP_2', 'WAVE_LITTROW_FIG_DEG_1',
    'WAVE_LITTROW_FIG_DEG_2', 'WAVE_LITTROW_EXT_ORDER_FIT_DEG',
    'WAVE_LITTROW_QC_RMS_MAX', 'WAVE_LITTROW_QC_DEV_MAX',
    # wave fp constants
    'WAVE_MODE_FP', 'WAVE_FP_DOPD0', 'WAVE_FP_CAVFIT_DEG', 'WAVE_FP_CM_IND',
    'WAVE_FP_LARGE_JUMP', 'WAVE_FP_BORDER_SIZE', 'WAVE_FP_FPBOX_SIZE',
    'WAVE_FP_PEAK_SIG_LIM', 'WAVE_FP_IPEAK_SPACING', 'WAVE_FP_EXP_WIDTH',
    'WAVE_FP_NORM_WIDTH_CUT', 'WAVE_FP_ERRX_MIN', 'WAVE_FP_LL_DEGR_FIT',
    'WAVE_FP_MAX_LLFIT_RMS', 'WAVE_FP_WEIGHT_THRES', 'WAVE_FP_BLAZE_THRES',
    'WAVE_FP_XDIF_MIN', 'WAVE_FP_XDIF_MAX', 'WAVE_FP_LL_OFFSET',
    'WAVE_FP_DV_MAX', 'WAVE_FP_UPDATE_CAVITY', 'WAVE_FP_CAVFIT_MODE',
    'WAVE_FP_LLFIT_MODE', 'WAVE_FP_LLDIF_MIN', 'WAVE_FP_LLDIF_MAX',
    'WAVE_FP_SIGCLIP', 'WAVE_FP_PLOT_MULTI_INIT', 'WAVE_FP_PLOT_MULTI_NBO',
    # wave ccf constantsCCF_N_ORD_MAX
    'WAVE_CCF_NOISE_SIGDET', 'WAVE_CCF_NOISE_BOXSIZE', 'WAVE_CCF_NOISE_THRES',
    'WAVE_CCF_STEP', 'WAVE_CCF_WIDTH', 'WAVE_CCF_TARGET_RV',
    'WAVE_CCF_DETNOISE', 'WAVE_CCF_MASK', 'WAVE_CCF_MASK_UNITS',
    'WAVE_CCF_MASK_PATH', 'WAVE_CCF_MASK_FMT', 'WAVE_CCF_MASK_MIN_WEIGHT',
    'WAVE_CCF_MASK_WIDTH', 'WAVE_CCF_N_ORD_MAX',
    # telluric constants
    'TAPAS_FILE', 'TAPAS_FILE_FMT', 'TELLU_CUT_BLAZE_NORM',
    'TELLU_ALLOWED_DPRTYPES', 'TELLURIC_FILETYPE', 'TELLURIC_FIBER_TYPE',
    'TELLU_LIST_DIRECOTRY', 'TELLU_WHITELIST_NAME', 'TELLU_BLACKLIST_NAME',
    # make telluric constants
    'MKTELLU_BLAZE_PERCENTILE', 'MKTELLU_CUT_BLAZE_NORM', 'TELLU_ABSORBERS',
    'MKTELLU_DEFAULT_CONV_WIDTH', 'MKTELLU_FINER_CONV_WIDTH',
    'MKTELLU_CLEAN_ORDERS', 'MKTELLU_TEMP_MED_FILT', 'MKTELLU_DPARAMS_THRES',
    'MKTELLU_MAX_ITER', 'MKTELLU_THRES_TRANSFIT', 'MKTELLU_TRANS_FIT_UPPER_BAD',
    'MKTELLU_TRANS_MIN_WATERCOL', 'MKTELLU_TRANS_MAX_WATERCOL',
    'MKTELLU_TRANS_MIN_NUM_GOOD', 'MKTELLU_TRANS_TAU_PERCENTILE',
    'MKTELLU_TRANS_SIGMA_CLIP', 'MKTELLU_TRANS_TEMPLATE_MEDFILT',
    'MKTELLU_SMALL_WEIGHTING_ERROR', 'MKTELLU_PLOT_ORDER_NUMS',
    'MKTELLU_TAU_WATER_ULIMIT', 'MKTELLU_TAU_OTHER_LLIMIT',
    'MKTELLU_TAU_OTHER_ULIMIT', 'MKTELLU_SMALL_LIMIT', 'MKTELLU_QC_SNR_ORDER',
    'MKTELLU_QC_SNR_MIN', 'MKTELLU_QC_AIRMASS_DIFF',
    # fit telluric constants,
    'FTELLU_NUM_PRINCIPLE_COMP', 'FTELLU_ADD_DERIV_PC', 'FTELLU_FIT_DERIV_PC',
    'FTELLU_FIT_KEEP_NUM', 'FTELLU_FIT_MIN_TRANS', 'FTELLU_LAMBDA_MIN',
    'FTELLU_LAMBDA_MAX', 'FTELLU_KERNEL_VSINI', 'FTELLU_FIT_ITERS',
    'FTELLU_FIT_RECON_LIMIT', 'FTELLU_PLOT_ORDER_NUMS', 'FTELLU_SPLOT_ORDER',
    # make template constants
    'MKTEMPLATE_SNR_ORDER', 'MKTEMPLATE_FILETYPE', 'MKTEMPLATE_FIBER_TYPE',
    'MKTEMPLATE_E2DS_ITNUM', 'MKTEMPLATE_E2DS_LOWF_SIZE',
    'MKTEMPLATE_S1D_ITNUM', 'MKTEMPLATE_S1D_LOWF_SIZE',
    # ccf constants
    'CCF_MASK_PATH', 'CCF_MASK_MIN_WEIGHT', 'CCF_MASK_WIDTH',
    'CCF_N_ORD_MAX', 'CCF_DEFAULT_MASK', 'CCF_MASK_UNITS', 'CCF_MASK_FMT',
    'CCF_DEFAULT_WIDTH', 'CCF_DEFAULT_STEP', 'CCF_ALLOWED_DPRTYPES',
    'CCF_CORRECT_TELLU_TYPES', 'CCF_TELLU_THRES', 'CCF_FILL_NAN_KERN_SIZE',
    'CCF_FILL_NAN_KERN_RES', 'CCF_DET_NOISE', 'CCF_FIT_TYPE', 'CCF_N_ORD_MAX',
    'CCF_NOISE_SIGDET', 'CCF_NOISE_BOXSIZE', 'CCF_NOISE_THRES',
    # debug plot settings
    'PLOT_DARK_IMAGE_REGIONS', 'PLOT_DARK_HISTOGRAM', 'PLOT_BADPIX_MAP',
    'PLOT_LOC_MINMAX_CENTS', 'PLOT_LOC_MIN_CENTS_THRES',
    'PLOT_LOC_FINDING_ORDERS', 'PLOT_LOC_IM_SAT_THRES', 'PLOT_LOC_ORD_VS_RMS',
    'PLOT_LOC_CHECK_COEFFS', 'PLOT_SHAPE_DX', 'PLOT_SHAPE_ANGLE_OFFSET_ALL',
    'PLOT_SHAPE_ANGLE_OFFSET', 'PLOT_SHAPEL_ZOOM_SHIFT',
    'PLOT_FLAT_ORDER_FIT_EDGES1', 'PLOT_FLAT_ORDER_FIT_EDGES2',
    'PLOT_FLAT_BLAZE_ORDER1', 'PLOT_FLAT_BLAZE_ORDER2',
    'PLOT_THERMAL_BACKGROUND', 'PLOT_EXTRACT_SPECTRAL_ORDER1',
    'PLOT_EXTRACT_SPECTRAL_ORDER2', 'PLOT_EXTRACT_S1D',
    'PLOT_EXTRACT_S1D_WEIGHT', 'PLOT_WAVE_HC_GUESS', 'PLOT_WAVE_HC_TFIT_GRID',
    'PLOT_WAVE_HC_BRIGHTEST_LINES', 'PLOT_WAVE_HC_RESMAP',
    'PLOT_WAVE_LITTROW_CHECK1', 'PLOT_WAVE_LITTROW_EXTRAP1',
    'PLOT_WAVE_LITTROW_CHECK2', 'PLOT_WAVE_LITTROW_EXTRAP2',
    'PLOT_WAVE_FP_FINAL_ORDER', 'PLOT_WAVE_FP_LWID_OFFSET',
    'PLOT_WAVE_FP_WAVE_RES', 'PLOT_WAVE_FP_M_X_RES', 'PLOT_WAVE_FP_LL_DIFF',
    'PLOT_WAVE_FP_IPT_CWID_1MHC', 'PLOT_WAVE_FP_IPT_CWID_LLHC',
    'PLOT_WAVE_FP_MULTI_ORDER', 'PLOT_WAVE_FP_SINGLE_ORDER',
    'PLOT_MKTELLU_WAVE_FLUX1', 'PLOT_MKTELLU_WAVE_FLUX2',
    'PLOT_FTELLU_PCA_COMP1', 'PLOT_FTELLU_PCA_COMP2',
    'PLOT_FTELLU_RECON_SPLINE1', 'PLOT_FTELLU_RECON_SPLINE2',
    'PLOT_FTELLU_WAVE_SHIFT1', 'PLOT_FTELLU_WAVE_SHIFT2',
    'PLOT_FTELLU_RECON_ABSO1', 'PLOT_FTELLU_RECON_ABSO2',
    'PLOT_CCF_RV_FIT_LOOP', 'PLOT_CCF_RV_FIT',
    # tool constants
    'REPROCESS_RUN_KEY', 'REPROCESS_NIGHTCOL', 'REPROCESS_ABSFILECOL',
    'REPROCESS_MODIFIEDCOL', 'REPROCESS_SORTCOL_HDRKEY',
    'REPROCESS_RAWINDEXFILE', 'REPROCESS_SEQCOL', 'REPROCESS_TIMECOL',
]

# set name
__NAME__ = 'core.instruments.default.default_constants.py'

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

# Define the pixel size in km/s / pix
#    also used for the median sampling size in tellu correction
IMAGE_PIXEL_SIZE = Const('IMAGE_PIXEL_SIZE', value=None, dtype=float,
                         source=__NAME__)

# Define mean line width expressed in pix
FWHM_PIXEL_LSF = Const('FWHM_PIXEL_LSF', value=None, dtype=float,
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

# Define the coefficients of the fit of 1/m vs d
CAVITY_1M_FILE = Const('CAVITY_1M_FILE', value=None, dtype=str, source=__NAME__)

# Define the coefficients of the fit of wavelength vs d
CAVITY_LL_FILE = Const('CAVITY_LL_FILE', value=None, dtype=str, source=__NAME__)

# Define the object list file name
OBJ_LIST_FILE = Const('OBJ_LIST_FILE', value=None, dtype=str, source=__NAME__)

# Define the object query list format
OBJ_LIST_FILE_FMT = Const('OBJ_LIST_FILE_FMT', value=None, dtype=str,
                          source=__NAME__)

# Define the radius for crossmatching objects (in both lookup table and query)
#   in arcseconds
OBJ_LIST_CROSS_MATCH_RADIUS = Const('OBJ_LIST_CROSS_MATCH_RADIUS', value=None,
                                    dtype=float, source=__NAME__, minimum=0.0)

# Define the TAP Gaia URL (for use in crossmatching to Gaia via astroquery)
OBJ_LIST_GAIA_URL = Const('OBJ_LIST_GAIA_URL', value=None, dtype=str,
                          source=__NAME__)

# Define the TAP SIMBAD URL (for use in crossmatching OBJNAME via astroquery)
OBJ_LIST_SIMBAD_URL = Const('OBJ_LIST_SIMBAD_URL', value=None, dtype=str,
                            source=__NAME__)

# Define the gaia magnitude cut to use in the gaia query
OBJ_LIST_GAIA_MAG_CUT = Const('OBJ_LIST_GAIA_MAG_CUT', value=None, dtype=float,
                              source=__NAME__, minimum=10.0, maximum=25.0)

# Define the gaia epoch to use in the gaia query
OBJ_LIST_GAIA_EPOCH = Const('OBJ_LIST_GAIA_EPOCH', value=None, dtype=float,
                            source=__NAME__, minimum=2000.0, maximum=2100.0)

# Define the gaia parallax limit for using gaia point
OBJ_LIST_GAIA_PLX_LIM = Const('OBJ_LIST_GAIA_PLX_LIM', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

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

# Define whether to skip preprocessed files that have already be processed
SKIP_DONE_PP = Const('SKIP_DONE_PP', value=None, dtype=bool,
                     source=__NAME__)

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

# set the sigma clipping cut off value for cleaning coefficients
LOC_COEFF_SIGCLIP = Const('LOC_COEFF_SIGCLIP', value=None, dtype=float,
                          source=__NAME__, minimum=0)

#  Defines the fit degree to fit in the coefficient cleaning
LOC_COEFFSIG_DEG = Const('LOC_COEFFSIG_DEG', value=None, dtype=int,
                         source=__NAME__, minimum=1)

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

# set the zoom in levels for the plots (xmin values)
LOC_PLOT_CORNER_XZOOM1 = Const('LOC_PLOT_CORNER_XZOOM1', value=None,
                               dtype=str, source=__NAME__)

# set the zoom in levels for the plots (xmax values)
LOC_PLOT_CORNER_XZOOM2 = Const('LOC_PLOT_CORNER_XZOOM2', value=None,
                               dtype=str, source=__NAME__)

# set the zoom in levels for the plots (ymin values)
LOC_PLOT_CORNER_YZOOM1 = Const('LOC_PLOT_CORNER_YZOOM1', value=None,
                               dtype=str, source=__NAME__)

# set the zoom in levels for the plots (ymax values)
LOC_PLOT_CORNER_YZOOM2 = Const('LOC_PLOT_CORNER_YZOOM2', value=None,
                               dtype=str, source=__NAME__)

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

# The order to use on the shape plot
SHAPE_PLOT_SELECTED_ORDER = Const('SHAPE_PLOT_SELECTED_ORDER', value=None,
                                  dtype=int, minimum=0, source=__NAME__)

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

#  Define first zoom plot for shape local zoom debug plot
#     should be a string list (xmin, xmax, ymin, ymax)
SHAPEL_PLOT_ZOOM1 = Const('SHAPEL_PLOT_ZOOM1', value=None, dtype=str,
                          source=__NAME__)

#  Define second zoom plot for shape local zoom debug plot
#     should be a string list (xmin, xmax, ymin, ymax)
SHAPEL_PLOT_ZOOM2 = Const('SHAPEL_PLOT_ZOOM2', value=None, dtype=str,
                          source=__NAME__)

# =============================================================================
# CALIBRATION: FLAT SETTINGS
# =============================================================================
# TODO: is blaze_size needed with sinc function?
#  Half size blaze smoothing window
FF_BLAZE_HALF_WINDOW = Const('FF_BLAZE_HALF_WINDOW', value=None, dtype=int,
                             source=__NAME__)

# TODO: is blaze_cut needed with sinc function?
# Minimum relative e2ds flux for the blaze computation
FF_BLAZE_THRESHOLD = Const('FF_BLAZE_THRESHOLD', value=None, dtype=float,
                           source=__NAME__)

# TODO: is blaze_deg needed with sinc function?
#  The blaze polynomial fit degree
FF_BLAZE_DEGREE = Const('FF_BLAZE_DEGREE', value=None, dtype=int,
                        source=__NAME__)

# Define the threshold, expressed as the fraction of the maximum peak, below
#    this threshold the blaze (and e2ds) is set to NaN
FF_BLAZE_SCUT = Const('FF_BLAZE_SCUT', value=None, dtype=float,
                        source=__NAME__)

# Define the rejection threshold for the blaze sinc fit
FF_BLAZE_SIGFIT = Const('FF_BLAZE_SIGFIT', value=None, dtype=float,
                        source=__NAME__)

# Define the hot bad pixel percentile level (using in blaze sinc fit)
FF_BLAZE_BPERCENTILE = Const('FF_BLAZE_BPERCENTILE', value=None, dtype=float,
                             source=__NAME__)

# Define the number of times to iterate around blaze sinc fit
FF_BLAZE_NITER = Const('FF_BLAZE_BPERCENTILE', value=None, dtype=int,
                       source=__NAME__, minimum=0)

# Define the orders not to plot on the RMS plot should be a string
#     containing a list of integers
FF_RMS_SKIP_ORDERS = Const('FF_RMS_SKIP_ORDERS', value=None, dtype=str,
                           source=__NAME__)

# Maximum allowed RMS of flat field
QC_FF_MAX_RMS = Const('QC_FF_MAX_RMS', value=None, dtype=float, source=__NAME__)

# Define the order to plot in summary plots
FF_PLOT_ORDER = Const('FF_PLOT_ORDER', value=None, dtype=int, source=__NAME__)

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

# Define the order to plot in summary plots
EXTRACT_PLOT_ORDER = Const('EXTRACT_PLOT_ORDER', value=None, dtype=int,
                           source=__NAME__)

# Define the wavelength lower bounds for s1d plots
#     (must be a string list of floats) defines the lower wavelength in nm
EXTRACT_S1D_PLOT_ZOOM1 = Const('EXTRACT_S1D_PLOT_ZOOM1', value=None,
                               dtype=str, source=__NAME__)

# Define the wavelength upper bounds for s1d plots
#     (must be a string list of floats) defines the upper wavelength in nm
EXTRACT_S1D_PLOT_ZOOM2 = Const('EXTRACT_S1D_PLOT_ZOOM2', value=None,
                               dtype=str, source=__NAME__)

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

# define the order to plot on the thermal debug plot
THERMAL_PLOT_START_ORDER = Const('THERMAL_PLOT_START_ORDER', value=None,
                                 dtype=int, source=__NAME__)

# =============================================================================
# CALIBRATION: WAVE GENERAL SETTINGS
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

# define whether to always extract HC/FP files in the wave code (even if they
#    have already been extracted
WAVE_ALWAYS_EXTRACT = Const('WAVE_ALWAYS_EXTRACT', value=None, dtype=bool,
                            source=__NAME__)

# define the type of file to use for wave solution (currently allowed are
#    'E2DS' or 'E2DSFF'
WAVE_EXTRACT_TYPE = Const('WAVE_EXTRACT_TYPE', value=None, dtype=str,
                          source=__NAME__, options=['E2DS', 'E2DSFF'])

# define the fit degree for the wavelength solution
WAVE_FIT_DEGREE = Const('WAVE_FIT_DEGREE', value=None, dtype=int,
                        source=__NAME__)

# Define intercept and slope for a pixel shift
WAVE_PIXEL_SHIFT_INTER = Const('WAVE_PIXEL_SHIFT_INTER', value=None,
                               dtype=float, source=__NAME__)
WAVE_PIXEL_SHIFT_SLOPE = Const('WAVE_PIXEL_SHIFT_SLOPE', value=None,
                               dtype=float, source=__NAME__)

#  Defines echelle of first extracted order
WAVE_T_ORDER_START = Const('WAVE_T_ORDER_START', value=None,
                           dtype=int, source=__NAME__)

#  Defines order from which the solution is calculated
WAVE_N_ORD_START = Const('WAVE_N_ORD_START', value=None, dtype=int,
                         source=__NAME__)

#  Defines order to which the solution is calculated
WAVE_N_ORD_FINAL = Const('WAVE_N_ORD_FINAL', value=None, dtype=int,
                         source=__NAME__)

# =============================================================================
# CALIBRATION: WAVE HC SETTINGS
# =============================================================================
# Define the mode to calculate the hc wave solution
WAVE_MODE_HC = Const('WAVE_MODE_HC', value=None, dtype=int, source=__NAME__,
                     options=[0])

# width of the box for fitting HC lines. Lines will be fitted from -W to +W,
#     so a 2*W+1 window
WAVE_HC_FITBOX_SIZE = Const('WAVE_HC_FITBOX_SIZE', value=None, dtype=int,
                            source=__NAME__)

# number of sigma above local RMS for a line to be flagged as such
WAVE_HC_FITBOX_SIGMA = Const('WAVE_HC_FITBOX_SIGMA', value=None, dtype=float,
                             source=__NAME__)

# the fit degree for the wave hc gaussian peaks fit
WAVE_HC_FITBOX_GFIT_DEG = Const('WAVE_HC_FITBOX_GFIT_DEG', value=None,
                                dtype=int, source=__NAME__)

# the RMS of line-fitted line must be between DEVMIN and DEVMAX of the peak
#     value must be SNR>5 (or 1/SNR<0.2)
WAVE_HC_FITBOX_RMS_DEVMIN = Const('WAVE_HC_FITBOX_RMS_DEVMIN', value=None,
                                  dtype=float, source=__NAME__, minimum=0.0)
WAVE_HC_FITBOX_RMS_DEVMAX = Const('WAVE_HC_FITBOX_RMS_DEVMAX', value=None,
                                  dtype=float, source=__NAME__, minimum=0.0)

# the e-width of the line expressed in pixels.
WAVE_HC_FITBOX_EWMIN = Const('WAVE_HC_FITBOX_EWMIN', value=None, dtype=float,
                             source=__NAME__, minimum=0.0)
WAVE_HC_FITBOX_EWMAX = Const('WAVE_HC_FITBOX_EWMAX', value=None, dtype=float,
                             source=__NAME__, minimum=0.0)

# define the file type for saving the initial guess at the hc peak list
WAVE_HCLL_FILE_FMT = Const('WAVE_LINELIST_FMT', value=None, dtype=str,
                           source=__NAME__)

# number of bright lines kept per order
#     avoid >25 as it takes super long
#     avoid <12 as some orders are ill-defined and we need >10 valid
#         lines anyway
#     20 is a good number, and I see no reason to change it
WAVE_HC_NMAX_BRIGHT = Const('WAVE_HC_NMAX_BRIGHT', value=None, dtype=int,
                            source=__NAME__, minimum=10, maximum=30)

# Number of times to run the fit triplet algorithm
WAVE_HC_NITER_FIT_TRIPLET = Const('WAVE_HC_NITER_FIT_TRIPLET', value=None,
                                  dtype=int, source=__NAME__, minimum=1)

# Maximum distance between catalog line and init guess line to accept
#     line in m/s
WAVE_HC_MAX_DV_CAT_GUESS = Const('WAVE_HC_MAX_DV_CAT_GUESS', value=None,
                                 dtype=int, source=__NAME__, minimum=0.0)

# The fit degree between triplets
WAVE_HC_TFIT_DEG = Const('WAVE_HC_TFIT_DEG', value=None, dtype=int,
                         source=__NAME__, minimum=0)

# Cut threshold for the triplet line fit [in km/s]
WAVE_HC_TFIT_CUT_THRES = Const('WAVE_HC_TFIT_CUT_THRES', value=None,
                               dtype=float, source=__NAME__, minimum=0.0)

# Minimum number of lines required per order
WAVE_HC_TFIT_MINNUM_LINES = Const('WAVE_HC_TFIT_MINNUM_LINES', value=None,
                                  dtype=int, source=__NAME__, minimum=0)

# Minimum total number of lines required
WAVE_HC_TFIT_MINTOT_LINES = Const('WAVE_HC_TFIT_MINTOT_LINES', value=None,
                                  dtype=int, source=__NAME__, minimum=0)

# this sets the order of the polynomial used to ensure continuity
#     in the  xpix vs wave solutions by setting the first term = 12,
#     we force that the zeroth element of the xpix of the wavelegnth
#     grid is fitted with a 12th order polynomial as a function of
#     order number (format = string list separated by commas
WAVE_HC_TFIT_ORDER_FIT_CONT = Const('WAVE_HC_TFIT_ORDER_FIT_CONT', value=None,
                                    dtype=str, source=__NAME__)

# Number of times to loop through the sigma clip for triplet fit
WAVE_HC_TFIT_SIGCLIP_NUM = Const('WAVE_HC_TFIT_SIGCLIP_NUM', value=None,
                                 dtype=int, source=__NAME__, minimum=1)

# Sigma clip threshold for triplet fit
WAVE_HC_TFIT_SIGCLIP_THRES = Const('WAVE_HC_TFIT_SIGCLIP_THRES', value=None,
                                   dtype=float, source=__NAME__, minimum=0.0)

# Define the distance in m/s away from the center of dv hist points
#     outside will be rejected [m/s]
WAVE_HC_TFIT_DVCUT_ORDER = Const('WAVE_HC_TFIT_DVCUT_ORDER', value=None,
                                 dtype=float, source=__NAME__, minimum=0.0)
WAVE_HC_TFIT_DVCUT_ALL = Const('WAVE_HC_TFIT_DVCUT_ALL', value=None,
                               dtype=float, source=__NAME__, minimum=0.0)

# Define the resolution and line profile map size (y-axis by x-axis)
WAVE_HC_RESMAP_SIZE = Const('WAVE_HC_RESMAP_SIZE', value=None, dtype=str,
                            source=__NAME__)

# Define the maximum allowed deviation in the RMS line spread function
WAVE_HC_RES_MAXDEV_THRES = Const('WAVE_HC_RES_MAXDEV_THRES', value=None,
                                 dtype=float, source=__NAME__)

# quality control criteria if sigma greater than this many sigma fails
WAVE_HC_QC_SIGMA_MAX = Const('WAVE_HC_QC_SIGMA_MAX', value=None, dtype=float,
                             source=__NAME__, minimum=0.0)

# Defines the dv span for PLOT_WAVE_HC_RESMAP debug plot, should be a
#    string list containing a min and max dv value
WAVE_HC_RESMAP_DV_SPAN = Const('WAVE_HC_RESMAP_DV_SPAN', value=None, dtype=str,
                             source=__NAME__)

# Defines the x limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
#   string list containing a min and max x value
WAVE_HC_RESMAP_XLIM = Const('WAVE_HC_RESMAP_XLIM', value=None, dtype=str,
                             source=__NAME__)

# Defines the y limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
#   string list containing a min and max y value
WAVE_HC_RESMAP_YLIM = Const('WAVE_HC_RESMAP_YLIM', value=None, dtype=str,
                             source=__NAME__)

# =============================================================================
# CALIBRATION: WAVE LITTROW SETTINGS
# =============================================================================
#  Define the order to start the Littrow fit from
WAVE_LITTROW_ORDER_INIT_1 = Const('WAVE_LITTROW_ORDER_INIT_1', value=None,
                                  dtype=int, source=__NAME__)
WAVE_LITTROW_ORDER_INIT_2 = Const('WAVE_LITTROW_ORDER_INIT_2', value=None,
                                  dtype=int, source=__NAME__)

#  Define the order to end the Littrow fit at
WAVE_LITTROW_ORDER_FINAL_1 = Const('WAVE_LITTROW_ORDER_FINAL_1', value=None,
                                   dtype=int, source=__NAME__)
WAVE_LITTROW_ORDER_FINAL_2 = Const('WAVE_LITTROW_ORDER_FINAL_2', value=None,
                                   dtype=int, source=__NAME__)

#  Define orders to ignore in Littrow fit (should be a string list separated
#      by commas
WAVE_LITTROW_REMOVE_ORDERS = Const('WAVE_LITTROW_REMOVE_ORDERS', value=None,
                                   dtype=str, source=__NAME__)

#  Define the littrow cut steps
WAVE_LITTROW_CUT_STEP_1 = Const('WAVE_LITTROW_CUT_STEP_1', value=None,
                                dtype=int, source=__NAME__)
WAVE_LITTROW_CUT_STEP_2 = Const('WAVE_LITTROW_CUT_STEP_2', value=None,
                                dtype=int, source=__NAME__)

#  Define the fit polynomial order for the Littrow fit (fit across the orders)
WAVE_LITTROW_FIG_DEG_1 = Const('WAVE_LITTROW_FIG_DEG_1', value=None,
                               dtype=int, source=__NAME__)
WAVE_LITTROW_FIG_DEG_2 = Const('WAVE_LITTROW_FIG_DEG_2', value=None,
                               dtype=int, source=__NAME__)

#  Define the order fit for the Littrow solution (fit along the orders)
# TODO needs to be the same as ic_ll_degr_fit
WAVE_LITTROW_EXT_ORDER_FIT_DEG = Const('WAVE_LITTROW_EXT_ORDER_FIT_DEG',
                                       value=None, dtype=int, source=__NAME__)

#   Maximum littrow RMS value
WAVE_LITTROW_QC_RMS_MAX = Const('WAVE_LITTROW_QC_RMS_MAX', value=None,
                                dtype=float, source=__NAME__)

#   Maximum littrow Deviation from wave solution (at x cut points)
WAVE_LITTROW_QC_DEV_MAX = Const('WAVE_LITTROW_QC_DEV_MAX', value=None,
                                dtype=float, source=__NAME__)

# =============================================================================
# CALIBRATION: WAVE FP SETTINGS
# =============================================================================
# Define the mode to calculate the fp wave solution
WAVE_MODE_FP = Const('WAVE_MODE_FP', value=None, dtype=int, source=__NAME__,
                     options=[0, 1])

# Define the initial value of FP effective cavity width 2xd in nm
WAVE_FP_DOPD0 = Const('WAVE_FP_DOPD0', value=None, dtype=float,
                      source=__NAME__, minimum=0.0)

#  Define the polynomial fit degree between FP line numbers and the
#      measured cavity width for each line
WAVE_FP_CAVFIT_DEG = Const('WAVE_FP_CAVFIT_DEG', value=None, dtype=int,
                           source=__NAME__, minimum=0)

#  Define the FP jump size that is too large
WAVE_FP_LARGE_JUMP = Const('WAVE_FP_LARGE_JUMP', value=None, dtype=float,
                           source=__NAME__, minimum=0)

# index of FP line to start order cross-matching from
WAVE_FP_CM_IND = Const('WAVE_FP_CM_IND', value=None, dtype=int, source=__NAME__)

#    Define the border size (edges in x-direction) for the FP fitting algorithm
WAVE_FP_BORDER_SIZE = Const('WAVE_FP_BORDER_SIZE', value=None, dtype=int,
                            source=__NAME__, minimum=0)

#    Define the box half-size (in pixels) to fit an individual FP peak to
#        - a gaussian will be fit to +/- this size from the center of
#          the FP peak
WAVE_FP_FPBOX_SIZE = Const('WAVE_FP_FPBOX_SIZE', value=None, dtype=int,
                           source=__NAME__, minimum=0)

#    Define the sigma above the median that a peak must have  - [cal_drift-peak]
#        to be recognised as a valid peak (before fitting a gaussian)
#        must be a string dictionary and must have an fp key
WAVE_FP_PEAK_SIG_LIM = Const('WAVE_FP_PEAK_SIG_LIM', value=None, dtype=str,
                             source=__NAME__)

#    Define the minimum spacing between peaks in order to be recognised
#        as a valid peak (before fitting a gaussian)
WAVE_FP_IPEAK_SPACING = Const('WAVE_FP_IPEAK_SPACING', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

#    Define the expected width of FP peaks - used to "normalise" peaks
#        (which are then subsequently removed if > WAVE_FP_NORM_WIDTH_CUT
WAVE_FP_EXP_WIDTH = Const('WAVE_FP_EXP_WIDTH', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

#    Define the "normalised" width of FP peaks that is too large normalised
#        width = FP FWHM - WAVE_FP_EXP_WIDTH
#        cut is essentially:
#           FP FWHM < (WAVE_FP_EXP_WIDTH + WAVE_FP_NORM_WIDTH_CUT)
WAVE_FP_NORM_WIDTH_CUT = Const('WAVE_FP_NORM_WIDTH_CUT', value=None,
                               dtype=float, source=__NAME__, minimum=0.0)

# Define the minimum instrumental error
WAVE_FP_ERRX_MIN = Const('WAVE_FP_ERRX_MIN', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

#  Define the wavelength fit polynomial order
WAVE_FP_LL_DEGR_FIT = Const('WAVE_FP_LL_DEGR_FIT', value=None, dtype=int,
                            source=__NAME__, minimum=0)

#  Define the max rms for the wavelength sigma-clip fit
WAVE_FP_MAX_LLFIT_RMS = Const('WAVE_FP_MAX_LLFIT_RMS', value=None, dtype=float,
                              source=__NAME__, minimum=0)

#  Define the weight threshold (small number) below which we do not keep fp
#     lines
WAVE_FP_WEIGHT_THRES = Const('WAVE_FP_WEIGHT_THRES', value=None, dtype=float,
                             source=__NAME__, minimum=0.0)

# Minimum blaze threshold to keep FP peaks
WAVE_FP_BLAZE_THRES = Const('WAVE_FP_BLAZE_THRES', value=None, dtype=float,
                            source=__NAME__, minimum=0.0)

# Minimum FP peaks pixel separation fraction diff. from median
WAVE_FP_XDIF_MIN = Const('WAVE_FP_XDIF_MIN', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

# Maximum FP peaks pixel separation fraction diff. from median
WAVE_FP_XDIF_MAX = Const('WAVE_FP_XDIF_MAX', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

# Maximum fract. wavelength offset between cross-matched FP peaks
WAVE_FP_LL_OFFSET = Const('WAVE_FP_LL_OFFSET', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

# Maximum DV to keep HC lines in combined (WAVE_NEW) solution
WAVE_FP_DV_MAX = Const('WAVE_FP_DV_MAX', value=None, dtype=float,
                       source=__NAME__, minimum=0.0)

# Decide whether to refit the cavity width (will update if files do not
#   exist)
WAVE_FP_UPDATE_CAVITY = Const('WAVE_FP_UPDATE_CAVITY', value=None, dtype=bool,
                              source=__NAME__)

# Select the FP cavity fitting (WAVE_MODE_FP = 1 only)
#   Should be one of the following:
#       0 - derive using the 1/m vs d fit from HC lines
#       1 - derive using the ll vs d fit from HC lines
WAVE_FP_CAVFIT_MODE = Const('WAVE_FP_CAVFIT_MODE', value=None, dtype=int,
                            source=__NAME__, options=[0, 1])

# Select the FP wavelength fitting (WAVE_MODE_FP = 1 only)
#   Should be one of the following:
#       0 - use fit_1d_solution function
#       1 - fit with sigma-clipping and mod 1 pixel correction
WAVE_FP_LLFIT_MODE = Const('WAVE_FP_LLFIT_MODE', value=None, dtype=int,
                           source=__NAME__, options=[0, 1])

# Minimum FP peaks wavelength separation fraction diff. from median
WAVE_FP_LLDIF_MIN = Const('WAVE_FP_LLDIF_MIN', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

# Maximum FP peaks wavelength separation fraction diff. from median
WAVE_FP_LLDIF_MAX = Const('WAVE_FP_LLDIF_MAX', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

# Sigma-clip value for sigclip_polyfit
WAVE_FP_SIGCLIP = Const('WAVE_FP_SIGCLIP', value=None, dtype=float,
                        source=__NAME__, minimum=0.0)

# First order for multi-order wave fp plot
WAVE_FP_PLOT_MULTI_INIT = Const('WAVE_FP_PLOT_MULTI_INIT', value=None,
                                dtype=int, source=__NAME__, minimum=0)

# Number of orders in multi-order wave fp plot
WAVE_FP_PLOT_MULTI_NBO = Const('WAVE_FP_PLOT_MULTI_NBO', value=None, dtype=int,
                               source=__NAME__, minimum=1)

# =============================================================================
# CALIBRATION: WAVE CCF SETTINGS
# =============================================================================
#   The value of the noise for wave dv rms calculation
#       snr = flux/sqrt(flux + noise^2)
WAVE_CCF_NOISE_SIGDET = Const('WAVE_CCF_NOISE_SIGDET', value=None, dtype=float,
                              source=__NAME__, minimum=0.0)

#   The size around a saturated pixel to flag as unusable for wave dv rms
#      calculation
WAVE_CCF_NOISE_BOXSIZE = Const('WAVE_CCF_NOISE_BOXSIZE', value=None, dtype=int,
                               source=__NAME__, minimum=0.0)

#   The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
WAVE_CCF_NOISE_THRES = Const('WAVE_CCF_NOISE_THRES', value=None, dtype=float,
                             source=__NAME__, minimum=0.0)

#   The CCF step size to use for the FP CCF
WAVE_CCF_STEP = Const('WAVE_CCF_STEP', value=None, dtype=float, source=__NAME__,
                      minimum=0.0)

#   The CCF width size to use for the FP CCF
WAVE_CCF_WIDTH = Const('WAVE_CCF_WIDTH', value=None, dtype=float,
                       source=__NAME__, minimum=0.0)

#   The target RV (CCF center) to use for the FP CCF
WAVE_CCF_TARGET_RV = Const('WAVE_CCF_TARGET_RV', value=None, dtype=float,
                           source=__NAME__, minimum=0.0)

#  The detector noise to use for the FP CCF
WAVE_CCF_DETNOISE = Const('WAVE_CCF_DETNOISE', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

#  The filename of the CCF Mask to use for the FP CCF
WAVE_CCF_MASK = Const('WAVE_CCF_MASK', value=None, dtype=str, source=__NAME__)

# Define the wavelength units for the mask for the FP CCF
WAVE_CCF_MASK_UNITS = Const('WAVE_CCF_MASK_UNITS', value=None, dtype=str,
                            source=__NAME__)

# Define the ccf mask path the FP CCF
WAVE_CCF_MASK_PATH = Const('WAVE_CCF_MASK_PATH', value=None, dtype=str,
                           source=__NAME__)

# Define the CCF mask format (must be an astropy.table format)
WAVE_CCF_MASK_FMT = Const('WAVE_CCF_MASK_FMT', value=None, dtype=str,
                          source=__NAME__)

#  Define the weight of the CCF mask (if 1 force all weights equal)
WAVE_CCF_MASK_MIN_WEIGHT = Const('WAVE_CCF_MASK_MIN_WEIGHT', value=None,
                                 dtype=float, source=__NAME__)

#  Define the width of the template line (if 0 use natural)
WAVE_CCF_MASK_WIDTH = Const('WAVE_CCF_MASK_WIDTH', value=None, dtype=float,
                            source=__NAME__)

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#      to calculate the FP CCF
WAVE_CCF_N_ORD_MAX = Const('WAVE_CCF_N_ORD_MAX', value=None, dtype=int,
                           source=__NAME__, minimum=1)

# =============================================================================
# CALIBRATION: TELLURIC SETTINGS
# =============================================================================
# Define the name of the tapas file to use
TAPAS_FILE = Const('TAPAS_FILE', value=None, dtype=str, source=__NAME__)

# Define the format (astropy format) of the tapas file "TAPAS_FILE"
TAPAS_FILE_FMT = Const('TAPAS_FILE_FMT', value=None, dtype=str, source=__NAME__)

# The allowed input DPRTYPES for input telluric files
TELLU_ALLOWED_DPRTYPES = Const('TELLU_ALLOWED_DPRTYPES', value=None, dtype=str,
                               source=__NAME__)

# Define level above which the blaze is high enough to accurately
#    measure telluric
TELLU_CUT_BLAZE_NORM = Const('TELLU_CUT_BLAZE_NORM', value=None, dtype=float,
                             source=__NAME__)

# Define telluric black/white list directory
TELLU_LIST_DIRECOTRY = Const('TELLU_LIST_DIRECTORY', value=None, dtype=str,
                             source=__NAME__)

# Define telluric white list name
TELLU_WHITELIST_NAME = Const('TELLU_WHITELIST_NAME', value=None, dtype=str,
                             source=__NAME__)

# Define telluric black list name
TELLU_BLACKLIST_NAME = Const('TELLU_BLACKLIST_NAME', value=None, dtype=str,
                             source=__NAME__)

# =============================================================================
# CALIBRATION: MAKE TELLURIC SETTINGS
# =============================================================================
# value below which the blaze in considered too low to be useful
#     for all blaze profiles, we normalize to the 95th percentile.
#     That's pretty much the peak value, but it is resistent to
#     eventual outliers
MKTELLU_BLAZE_PERCENTILE = Const('MKTELLU_BLAZE_PERCENTILE', value=None,
                                 dtype=float, source=__NAME__)
MKTELLU_CUT_BLAZE_NORM = Const('MKTELLU_CUT_BLAZE_NORM', value=None,
                               dtype=float, source=__NAME__)

# Define list of absorbers in the tapas fits table
TELLU_ABSORBERS = Const('TELLU_ABSORBERS', value=None, dtype=str,
                        source=__NAME__)

# define the default convolution width [in pixels]
MKTELLU_DEFAULT_CONV_WIDTH = Const('MKTELLU_DEFAULT_CONV_WIDTH', value=None,
                                   dtype=int, source=__NAME__)

# define the finer convolution width [in pixels]
MKTELLU_FINER_CONV_WIDTH = Const('MKTELLU_FINER_CONV_WIDTH', value=None,
                                 dtype=int, source=__NAME__)

# define which orders are clean enough of tellurics to use the finer
#     convolution width (should be a string list separated by commas)
MKTELLU_CLEAN_ORDERS = Const('MKTELLU_CLEAN_ORDERS', value=None,
                             dtype=str, source=__NAME__)

# median-filter the template. we know that stellar features
#    are very broad. this avoids having spurious noise in our
#    templates [pixel]
MKTELLU_TEMP_MED_FILT = Const('MKTELLU_TEMP_MED_FILT', value=None, dtype=int,
                              source=__NAME__)

# threshold in absorbance where we will stop iterating the absorption
#     model fit
MKTELLU_DPARAMS_THRES = Const('MKTELLU_DPARAMS_THRES', value=None, dtype=float,
                              source=__NAME__)

# max number of iterations, normally converges in about 12 iterations
MKTELLU_MAX_ITER = Const('MKTELLU_MAX_ITER', value=None, dtype=int,
                         source=__NAME__, minimum=1)

# minimum transmission required for use of a given pixel in the TAPAS
#    and SED fitting
MKTELLU_THRES_TRANSFIT = Const('MKTELLU_THRES_TRANSFIT', value=None,
                               dtype=float, source=__NAME__)

# Defines the bad pixels if the spectrum is larger than this value.
#    These values are likely an OH line or a cosmic ray
MKTELLU_TRANS_FIT_UPPER_BAD = Const('MKTELLU_TRANS_FIT_UPPER_BAD', value=None,
                                    dtype=float, source=__NAME__)

# Defines the minimum allowed value for the recovered water vapor optical
#    depth (should not be able 1)
MKTELLU_TRANS_MIN_WATERCOL = Const('MKTELLU_TRANS_MIN_WATERCOL', value=None,
                                   dtype=float, source=__NAME__)

# Defines the maximum allowed value for the recovered water vapor optical
#    depth
MKTELLU_TRANS_MAX_WATERCOL = Const('MKTELLU_TRANS_MAX_WATERCOL', value=None,
                                   dtype=float, source=__NAME__)

# Defines the minimum number of good points required to normalise the
#    spectrum, if less than this we don't normalise the spectrum by its
#    median
MKTELLU_TRANS_MIN_NUM_GOOD = Const('MKTELLU_TRANS_MIN_NUM_GOOD', value=None,
                                   dtype=int, source=__NAME__)

# Defines the percentile used to gauge which transmission points should
#    be used to median (above this percentile is used to median)
MKTELLU_TRANS_TAU_PERCENTILE = Const('MKTELLU_TRANS_TAU_PERCENTILE', value=None,
                                     dtype=float, source=__NAME__)

# sigma-clipping of the residuals of the difference between the
# spectrum divided by the fitted TAPAS absorption and the
# best guess of the SED
MKTELLU_TRANS_SIGMA_CLIP = Const('MKTELLU_TRANS_SIGMA_CLIP', value=None,
                                 dtype=float, source=__NAME__)

# median-filter the trans data measured in pixels
MKTELLU_TRANS_TEMPLATE_MEDFILT = Const('MKTELLU_TRANS_TEMPLATE_MEDFILT',
                                       value=None, dtype=int, source=__NAME__)

# Define the threshold for "small" values that do not add to the weighting
MKTELLU_SMALL_WEIGHTING_ERROR = Const('MKTELLU_SMALL_WEIGHTING_ERROR',
                                      value=None, dtype=float, source=__NAME__)

# Define the orders to plot (not too many)
#    values should be a string list separated by commas
MKTELLU_PLOT_ORDER_NUMS = Const('MKTELLU_PLOT_ORDER_NUMS', value=None,
                                dtype=str, source=__NAME__)

# Set an upper limit for the allowed line-of-sight optical depth of water
MKTELLU_TAU_WATER_ULIMIT = Const('MKTELLU_TAU_WATER_ULIMIT', value=None,
                                 dtype=float, source=__NAME__)

# set a lower and upper limit for the allowed line-of-sight optical depth
#    for other absorbers (upper limit equivalent to airmass limit)
# line-of-sight optical depth for other absorbers cannot be less than one
#      (that's zenith) keep the limit at 0.2 just so that the value gets
#      propagated to header and leaves open the possibility that during
#      the convergence of the algorithm, values go slightly below 1.0
MKTELLU_TAU_OTHER_LLIMIT = Const('MKTELLU_TAU_OTHER_LLIMIT', value=None,
                                 dtype=float, source=__NAME__)

# line-of-sight optical depth for other absorbers cannot be greater than 5
#       that would be an airmass of 5 and SPIRou cannot observe there
MKTELLU_TAU_OTHER_ULIMIT = Const('MKTELLU_TAU_OTHER_ULIMIT', value=None,
                                 dtype=float, source=__NAME__)

# bad values and small values are set to this value (as a lower limit to
#   avoid dividing by small numbers or zero
MKTELLU_SMALL_LIMIT = Const('MKTELLU_SMALL_LIMIT', value=None, dtype=float,
                            source=__NAME__, minimum=0.0)

#   Define the order to use for SNR check when accepting tellu files
#      to the telluDB
MKTELLU_QC_SNR_ORDER = Const('MKTELLU_QC_SNR_ORDER', value=None, dtype=int,
                             source=__NAME__, minimum=0)

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
#      accepted to the telluDB
MKTELLU_QC_SNR_MIN = Const('MKTELLU_QC_SNR_MIN', value=None, dtype=float,
                           source=__NAME__, minimum=0.0)

# Define the allowed difference between recovered and input airmass
MKTELLU_QC_AIRMASS_DIFF = Const('MKTELLU_QC_AIRMASS_DIFF', value=None,
                                dtype=float, source=__NAME__)

# =============================================================================
# CALIBRATION: FIT TELLURIC SETTINGS
# =============================================================================
# The number of principle components to use in PCA fit
FTELLU_NUM_PRINCIPLE_COMP = Const('FTELLU_NUM_PRINCIPLE_COMP', value=None,
                                  dtype=int, source=__NAME__, minimum=1)

# Define whether to add the first derivative and broadening factor to the
#     principal components this allows a variable resolution and velocity
#     offset of the PCs this is performed in the pixel space and NOT the
#     velocity space as this is should be due to an instrument shift
FTELLU_ADD_DERIV_PC = Const('FTELLU_ADD_DERIV_PC', value=None, dtype=bool,
                            source=__NAME__)

# Define whether to fit the derivatives instead of the principal components
FTELLU_FIT_DERIV_PC = Const('FTELLU_FIT_DERIV_PC', value=None, dtype=bool,
                            source=__NAME__)

# The number of pixels required (per order) to be able to interpolate the
#    template on to a berv shifted wavelength grid
FTELLU_FIT_KEEP_NUM = Const('FTELLU_FIT_KEEP_NUM', value=None, dtype=int,
                            source=__NAME__)

# The minimium transmission allowed to define good pixels (for reconstructed
#    absorption calculation)
FTELLU_FIT_MIN_TRANS = Const('FTELLU_FIT_MIN_TRANS', value=None, dtype=float,
                             source=__NAME__)

# The minimum wavelength constraint (in nm) to calculate reconstructed
#     absorption
FTELLU_LAMBDA_MIN = Const('FTELLU_LAMBDA_MIN', value=None, dtype=float,
                          source=__NAME__)

# The maximum wavelength constraint (in nm) to calculate reconstructed
#     absorption
FTELLU_LAMBDA_MAX = Const('FTELLU_LAMBDA_MAX', value=None, dtype=float,
                          source=__NAME__)

# The gaussian kernel used to smooth the template and residual spectrum [km/s]
FTELLU_KERNEL_VSINI = Const('FTELLU_KERNEL_VSINI', value=None, dtype=float,
                            source=__NAME__)

# The number of iterations to use in the reconstructed absorption calculation
FTELLU_FIT_ITERS = Const('FTELLU_FIT_ITERS', value=None, dtype=int,
                         source=__NAME__)

# The minimum log absorption the is allowed in the molecular absorption
#     calculation
FTELLU_FIT_RECON_LIMIT = Const('FTELLU_FIT_RECON_LIMIT', value=None,
                               dtype=float, source=__NAME__)

# Define the orders to plot (not too many) for recon abso plot
#    values should be a string list separated by commas
FTELLU_PLOT_ORDER_NUMS = Const('FTELLU_PLOT_ORDER_NUMS', value=None,
                               dtype=str, source=__NAME__)

# Define the selected fit telluric order for debug plots (when not in loop)
FTELLU_SPLOT_ORDER = Const('FTELLU_SPLOT_ORDER', value=None,
                           dtype=int, source=__NAME__)

# =============================================================================
# CALIBRATION: MAKE TEMPLATE SETTINGS
# =============================================================================
# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input template files
TELLURIC_FILETYPE = Const('TELLURIC_FILETYPE', value=None, dtype=str,
                          source=__NAME__)

# the fiber required for input template files
TELLURIC_FIBER_TYPE = Const('TELLURIC_FIBER_TYPE', value=None, dtype=str,
                            source=__NAME__)

# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input template files
MKTEMPLATE_FILETYPE = Const('MKTEMPLATE_FILETYPE', value=None, dtype=str,
                            source=__NAME__)

# the fiber required for input template files
MKTEMPLATE_FIBER_TYPE = Const('MKTEMPLATE_FIBER_TYPE', value=None, dtype=str,
                              source=__NAME__)

# the order to use for signal to noise cut requirement
MKTEMPLATE_SNR_ORDER = Const('MKTEMPLATE_SNR_ORDER', value=None, dtype=int,
                             source=__NAME__, minimum=0)

# The number of iterations to filter low frequency noise before medianing
#   the template "big cube" to the final template spectrum
MKTEMPLATE_E2DS_ITNUM = Const('MKTEMPLATE_E2DS_ITNUM', value=None, dtype=int,
                              source=__NAME__, minimum=1)

# The size (in pixels) to filter low frequency noise before medianing
#   the template "big cube" to the final template spectrum
MKTEMPLATE_E2DS_LOWF_SIZE = Const('MKTEMPLATE_E2DS_LOWF_SIZE', value=None,
                                  dtype=int, source=__NAME__, minimum=1)

# The number of iterations to filter low frequency noise before medianing
#   the s1d template "big cube" to the final template spectrum
MKTEMPLATE_S1D_ITNUM = Const('MKTEMPLATE_S1D_ITNUM', value=None, dtype=int,
                             source=__NAME__, minimum=1)

# The size (in pixels) to filter low frequency noise before medianing
#   the s1d template "big cube" to the final template spectrum
MKTEMPLATE_S1D_LOWF_SIZE = Const('MKTEMPLATE_S1D_LOWF_SIZE', value=None,
                                 dtype=int, source=__NAME__, minimum=1)

# =============================================================================
# CALIBRATION: CCF SETTINGS
# =============================================================================
# Define the ccf mask path
CCF_MASK_PATH = Const('CCF_MASK_PATH', value=None, dtype=str, source=__NAME__)

# Define the default CCF MASK to use
CCF_DEFAULT_MASK = Const('CCF_DEFAULT_MASK', value=None, dtype=str,
                         source=__NAME__)

# Define the wavelength units for the mask
CCF_MASK_UNITS = Const('CCF_DEFAULT_MASK', value=None, dtype=str,
                       source=__NAME__,
                       options=['AA', 'Angstrom', 'nm', 'nanometer', 'um',
                                'micron', 'mm', 'millimeter', 'cm',
                                'centimeter', 'm', 'meter'])

# Define the CCF mask format (must be an astropy.table format)
CCF_MASK_FMT = Const('CCF_MASK_FMT', value=None, dtype=str, source=__NAME__)

#  Define the weight of the CCF mask (if 1 force all weights equal)
CCF_MASK_MIN_WEIGHT = Const('CCF_MASK_MIN_WEIGHT', value=None, dtype=float,
                            source=__NAME__, minimum=0.0)

#  Define the width of the template line (if 0 use natural)
CCF_MASK_WIDTH = Const('CCF_MASK_WIDTH', value=None, dtype=float,
                       source=__NAME__, minimum=0.0)

# Define the width of the CCF range [km/s]
CCF_DEFAULT_WIDTH = Const('CCF_DEFAULT_WIDTH', value=None, dtype=float,
                          source=__NAME__, minimum=0.0)

# Define the computations steps of the CCF [km/s]
CCF_DEFAULT_STEP = Const('CCF_DEFAULT_STEP', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

#   The value of the noise for wave dv rms calculation
#       snr = flux/sqrt(flux + noise^2)
CCF_NOISE_SIGDET = Const('CCF_NOISE_SIGDET', value=None, dtype=float,
                         source=__NAME__, minimum=0.0)

#   The size around a saturated pixel to flag as unusable for wave dv rms
#      calculation
CCF_NOISE_BOXSIZE = Const('CCF_NOISE_BOXSIZE', value=None, dtype=int,
                          source=__NAME__, minimum=0.0)

#   The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
CCF_NOISE_THRES = Const('CCF_NOISE_THRES', value=None, dtype=float,
                        source=__NAME__, minimum=0.0)

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#      to calculate the CCF and RV
CCF_N_ORD_MAX = Const('CCF_N_ORD_MAX', value=None, dtype=int, source=__NAME__,
                      minimum=1)

# Allowed input DPRTYPES for input  for CCF recipe
CCF_ALLOWED_DPRTYPES = Const('CCF_ALLOWED_DPRTYPES', value=None, dtype=str,
                             source=__NAME__)

# Define the KW_OUTPUT types that are valid telluric corrected spectra
CCF_CORRECT_TELLU_TYPES = Const('CCF_CORRECT_TELLU_TYPES', value=None,
                                dtype=str, source=__NAME__)

# The transmission threshold for removing telluric domain (if and only if
#     we have a telluric corrected input file
CCF_TELLU_THRES = Const('CCF_TELLU_THRES', value=None, dtype=float,
                        source=__NAME__)

# The half size (in pixels) of the smoothing box used to calculate what value
#    should replace the NaNs in the E2ds before CCF is calculated
CCF_FILL_NAN_KERN_SIZE = Const('CCF_FILL_NAN_KERN_SIZE', value=None,
                               dtype=float, source=__NAME__)

# the step size (in pixels) of the smoothing box used to calculate what value
#   should replace the NaNs in the E2ds before CCF is calculated
CCF_FILL_NAN_KERN_RES = Const('CCF_FILL_NAN_KERN_RES', value=None,
                              dtype=float, source=__NAME__)

#  Define the detector noise to use in the ccf
CCF_DET_NOISE = Const('CCF_DET_NOISE', value=None, dtype=float, source=__NAME__)

# Define the fit type for the CCF fit
#     if 0 then we have an absorption line
#     if 1 then we have an emission line
CCF_FIT_TYPE = Const('CCF_FIT_TYPE', value=None, dtype=int, source=__NAME__,
                     options=[0, 1])

# =============================================================================
# DEBUG PLOT SETTINGS
# =============================================================================
# turn on dark image region debug plot
PLOT_DARK_IMAGE_REGIONS = Const('PLOT_DARK_IMAGE_REGIONS', value=False,
                                dtype=bool, source=__NAME__)

# turn on dark histogram debug plot
PLOT_DARK_HISTOGRAM = Const('PLOT_DARK_HISTOGRAM', value=False, dtype=bool,
                            source=__NAME__)

# turn on badpix map debug plot
PLOT_BADPIX_MAP = Const('PLOT_BADPIX_MAP', value=False, dtype=bool,
                        source=__NAME__)

# turn on the localisation cent min max debug plot
PLOT_LOC_MINMAX_CENTS = Const('PLOT_LOC_MINMAX_CENTS', value=False,
                              dtype=bool, source=__NAME__)

# turn on the localisation cent/thres debug plot
PLOT_LOC_MIN_CENTS_THRES = Const('PLOT_LOC_MIN_CENTS_THRES', value=False,
                                 dtype=bool, source=__NAME__)

# turn on the localisation finding orders debug plot
PLOT_LOC_FINDING_ORDERS = Const('PLOT_LOC_FINDING_ORDERS', value=False,
                                dtype=bool, source=__NAME__)

# turn on the image above saturation threshold debug plot
PLOT_LOC_IM_SAT_THRES = Const('PLOT_LOC_IM_SAT_THRES', value=False,
                              dtype=bool, source=__NAME__)

# turn on the order number vs rms debug plot
PLOT_LOC_ORD_VS_RMS = Const('PLOT_LOC_ORD_VS_RMS', value=False,
                            dtype=bool, source=__NAME__)

# turn on the localisation check coeffs debug plot
PLOT_LOC_CHECK_COEFFS = Const('PLOT_LOC_CHECK_COEFFS', value=False,
                              dtype=bool, source=__NAME__)

# turn on the shape dx debug plot
PLOT_SHAPE_DX = Const('PLOT_SHAPE_DX', value=False, dtype=bool, source=__NAME__)

# turn on the shape angle offset (all orders in loop) debug plot
PLOT_SHAPE_ANGLE_OFFSET_ALL = Const('PLOT_SHAPE_ANGLE_OFFSET_ALL', value=False,
                                    dtype=bool, source=__NAME__)

# turn on the shape angle offset (one selected order) debug plot
PLOT_SHAPE_ANGLE_OFFSET = Const('PLOT_SHAPE_ANGLE_OFFSET', value=False,
                                dtype=bool, source=__NAME__)

# turn on the shape local zoom plot
PLOT_SHAPEL_ZOOM_SHIFT = Const('PLOT_SHAPEL_ZOOM_SHIFT', value=False,
                               dtype=bool, source=__NAME__)

# turn on the flat order fit edges debug plot (loop)
PLOT_FLAT_ORDER_FIT_EDGES1 = Const('PLOT_FLAT_ORDER_FIT_EDGES1', value=False,
                                   dtype=bool, source=__NAME__)

# turn on the flat order fit edges debug plot (selected order)
PLOT_FLAT_ORDER_FIT_EDGES2 = Const('PLOT_FLAT_ORDER_FIT_EDGES2', value=False,
                                   dtype=bool, source=__NAME__)

# turn on the flat blaze order debug plot (loop)
PLOT_FLAT_BLAZE_ORDER1 = Const('PLOT_FLAT_BLAZE_ORDER1', value=False,
                               dtype=bool, source=__NAME__)

# turn on the flat blaze order debug plot (selected order)
PLOT_FLAT_BLAZE_ORDER2 = Const('PLOT_FLAT_BLAZE_ORDER2', value=False,
                               dtype=bool, source=__NAME__)

# turn on thermal background (in extract) debug plot
PLOT_THERMAL_BACKGROUND = Const('PLOT_THERMAL_BACKGROUND', value=False,
                                dtype=bool, source=__NAME__)

# turn on the extraction spectral order debug plot (loop)
PLOT_EXTRACT_SPECTRAL_ORDER1 = Const('PLOT_EXTRACT_SPECTRAL_ORDER1',
                                     value=False, dtype=bool, source=__NAME__)

# turn on the extraction spectral order debug plot (selected order)
PLOT_EXTRACT_SPECTRAL_ORDER2 = Const('PLOT_EXTRACT_SPECTRAL_ORDER2',
                                     value=False, dtype=bool, source=__NAME__)

# turn on the extraction 1d spectrum debug plot
PLOT_EXTRACT_S1D = Const('PLOT_EXTRACT_S1D', value=False, dtype=bool,
                         source=__NAME__)

# turn on the extraction 1d spectrum weight (before/after) debug plot
PLOT_EXTRACT_S1D_WEIGHT = Const('PLOT_EXTRACT_S1D_WEIGHT', value=False,
                                dtype=bool, source=__NAME__)

# turn on the wave solution hc guess debug plot (in loop)
PLOT_WAVE_HC_GUESS = Const('PLOT_WAVE_HC_GUESS', value=False,
                           dtype=bool, source=__NAME__)

# turn on the wave solution hc brightest lines debug plot
PLOT_WAVE_HC_BRIGHTEST_LINES = Const('PLOT_WAVE_HC_BRIGHTEST_LINES',
                                     value=False, dtype=bool, source=__NAME__)

# turn on the wave solution hc triplet fit grid debug plot
PLOT_WAVE_HC_TFIT_GRID = Const('PLOT_WAVE_HC_TFIT_GRID', value=False,
                               dtype=bool, source=__NAME__)

# turn on the wave solution hc resolution map debug plot
PLOT_WAVE_HC_RESMAP = Const('PLOT_WAVE_HC_RESMAP', value=False,
                            dtype=bool, source=__NAME__)

# turn on the wave solution littrow check debug plot
PLOT_WAVE_LITTROW_CHECK1 = Const('PLOT_WAVE_LITTROW_CHECK1', value=False,
                                 dtype=bool, source=__NAME__)

# turn on the wave solution littrow extrapolation debug plot
PLOT_WAVE_LITTROW_EXTRAP1 = Const('PLOT_WAVE_LITTROW_EXTRAP1', value=False,
                                  dtype=bool, source=__NAME__)

# turn on the wave solution littrow check debug plot
PLOT_WAVE_LITTROW_CHECK2 = Const('PLOT_WAVE_LITTROW_CHECK2', value=False,
                                 dtype=bool, source=__NAME__)

# turn on the wave solution littrow extrapolation debug plot
PLOT_WAVE_LITTROW_EXTRAP2 = Const('PLOT_WAVE_LITTROW_EXTRAP2', value=False,
                                  dtype=bool, source=__NAME__)

# turn on the wave solution final fp order debug plot
PLOT_WAVE_FP_FINAL_ORDER = Const('PLOT_WAVE_FP_FINAL_ORDER', value=False,
                                 dtype=bool, source=__NAME__)

# turn on the wave solution fp local width offset debug plot
PLOT_WAVE_FP_LWID_OFFSET = Const('PLOT_WAVE_FP_LWID_OFFSET', value=False,
                                 dtype=bool, source=__NAME__)

# turn on the wave solution fp wave residual debug plot
PLOT_WAVE_FP_WAVE_RES = Const('PLOT_WAVE_FP_WAVE_RES', value=False,
                              dtype=bool, source=__NAME__)

# turn on the wave solution fp fp_m_x residual debug plot
PLOT_WAVE_FP_M_X_RES = Const('PLOT_WAVE_FP_M_X_RES', value=False,
                             dtype=bool, source=__NAME__)

# turn on the wave solution fp interp cavity width 1/m_d hc debug plot
PLOT_WAVE_FP_IPT_CWID_1MHC = Const('PLOT_WAVE_FP_IPT_CWID_1MHC', value=False,
                                   dtype=bool, source=__NAME__)

# turn on the wave solution fp interp cavity width ll hc and fp debug plot
PLOT_WAVE_FP_IPT_CWID_LLHC = Const('PLOT_WAVE_FP_IPT_CWID_LLHC', value=False,
                                   dtype=bool, source=__NAME__)

# turn on the wave solution old vs new wavelength difference debug plot
PLOT_WAVE_FP_LL_DIFF = Const('PLOT_WAVE_FP_LL_DIFF', value=False, dtype=bool,
                             source=__NAME__)

# turn on the wave solution fp multi order debug plot
PLOT_WAVE_FP_MULTI_ORDER = Const('PLOT_WAVE_FP_MULTI_ORDER', value=False,
                                 dtype=bool, source=__NAME__)

# turn on the wave solution fp single order debug plot
PLOT_WAVE_FP_SINGLE_ORDER = Const('PLOT_WAVE_FP_SINGLE_ORDER', value=False,
                                  dtype=bool, source=__NAME__)

# turn on the make tellu wave flux debug plot (in loop)
PLOT_MKTELLU_WAVE_FLUX1 = Const('PLOT_MKTELLU_WAVE_FLUX1', value=False,
                                dtype=bool, source=__NAME__)

# turn on the make tellu wave flux debug plot (single order)
PLOT_MKTELLU_WAVE_FLUX2 = Const('PLOT_MKTELLU_WAVE_FLUX2', value=False,
                                dtype=bool, source=__NAME__)

# turn on the fit tellu pca component debug plot (in loop)
PLOT_FTELLU_PCA_COMP1 = Const('PLOT_FTELLU_PCA_COMP1', value=False,
                             dtype=bool, source=__NAME__)

# turn on the fit tellu pca component debug plot (single order)
PLOT_FTELLU_PCA_COMP2 = Const('PLOT_FTELLU_PCA_COMP2', value=False,
                             dtype=bool, source=__NAME__)

# turn on the fit tellu reconstructed spline debug plot (in loop)
PLOT_FTELLU_RECON_SPLINE1 = Const('PLOT_FTELLU_RECON_SPLINE1', value=False,
                                 dtype=bool, source=__NAME__)

# turn on the fit tellu reconstructed spline debug plot (single order)
PLOT_FTELLU_RECON_SPLINE2 = Const('PLOT_FTELLU_RECON_SPLINE2', value=False,
                                 dtype=bool, source=__NAME__)

# turn on the fit tellu wave shift debug plot (in loop)
PLOT_FTELLU_WAVE_SHIFT1 = Const('PLOT_FTELLU_WAVE_SHIFT1', value=False,
                               dtype=bool, source=__NAME__)

# turn on the fit tellu wave shift debug plot (single order)
PLOT_FTELLU_WAVE_SHIFT2 = Const('PLOT_FTELLU_WAVE_SHIFT2', value=False,
                               dtype=bool, source=__NAME__)

# turn on the fit tellu reconstructed absorption debug plot (in loop)
PLOT_FTELLU_RECON_ABSO1 = Const('PLOT_FTELLU_RECON_ABSO1', value=False,
                               dtype=bool, source=__NAME__)

# turn on the fit tellu reconstructed absorption debug plot (single order)
PLOT_FTELLU_RECON_ABSO2 = Const('PLOT_FTELLU_RECON_ABSO12', value=False,
                               dtype=bool, source=__NAME__)

# turn on the ccf rv fit debug plot (in a loop around orders)
PLOT_CCF_RV_FIT_LOOP = Const('PLOT_CCF_RV_FIT_LOOP', value=False,
                             dtype=bool, source=__NAME__)

# turn on the ccf rv fit debug plot (for the mean order value)
PLOT_CCF_RV_FIT = Const('PLOT_CCF_RV_FIT', value=False,
                        dtype=bool, source=__NAME__)

# =============================================================================
# TOOLS SETTINGS
# =============================================================================
# Key for use in run files
REPROCESS_RUN_KEY = Const('REPROCESS_RUN_KEY', value=None, dtype=str,
                          source=__NAME__)

# Define the night name column name for raw file table
REPROCESS_NIGHTCOL = Const('REPROCESS_NIGHTCOL', value=None, dtype=str,
                           source=__NAME__)

# Define the absolute file column name for raw file table
REPROCESS_ABSFILECOL = Const('REPROCESS_ABSFILECOL', value=None, dtype=str,
                             source=__NAME__)

# Define the modified file column name for raw file table
REPROCESS_MODIFIEDCOL = Const('REPROCESS_MODIFIEDCOL', value=None, dtype=str,
                              source=__NAME__)

# Define the sort column (from header keywords) for raw file table
REPROCESS_SORTCOL_HDRKEY = Const('REPROCESS_SORTCOL_HDRKEY', value=None,
                                 dtype=str, source=__NAME__)

# Define the raw index filename
REPROCESS_RAWINDEXFILE = Const('REPROCESS_RAWINDEXFILE', value=None, dtype=str,
                               source=__NAME__)

# define the sequence (1 of 5, 2 of 5 etc) col for raw file table
REPROCESS_SEQCOL = Const('REPROCESS_SEQCOL', value=None, dtype=str,
                         source=__NAME__)

# define the time col for raw file table
REPROCESS_TIMECOL = Const('REPROCESS_TIMECOL', value=None, dtype=str,
                          source=__NAME__)

# =============================================================================
#  End of configuration file
# =============================================================================
