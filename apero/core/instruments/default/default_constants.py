# This is the main config file
import numpy as np

from apero.base import base
from apero.core.constants import constant_functions

# =============================================================================
# Define variables
# =============================================================================
# all definition
__all__ = [
    # general
    'DATA_ENGINEERING', 'CALIB_DB_FORCE_WAVESOL', 'DATA_CORE',
    # preprocessing constants
    'PP_OBJ_DPRTYPES', 'PP_BADLIST_SSID',
    'PP_BADLIST_SSWB', 'PP_BADLIST_DRS_HKEY', 'PP_BADLIST_SS_VALCOL',
    'PP_BADLIST_SS_MASKCOL', 'PP_HOTPIX_BOXSIZE', 'PP_CORRUPT_HOT_THRES',
    'PP_NUM_DARK_AMP', 'PP_HOTPIX_FILE', 'PP_TOTAL_AMP_NUM',
    'PP_CORRUPT_MED_SIZE', 'PP_NUM_REF_TOP', 'PP_NUM_REF_BOTTOM',
    'PP_NUM_REF_LEFT', 'PP_NUM_REF_RIGHT',
    'PP_RMS_PERCENTILE', 'PP_LOWEST_RMS_PERCENTILE', 'PP_CORRUPT_SNR_HOTPIX',
    'PP_CORRUPT_RMS_THRES', 'PP_COSMIC_NOISE_ESTIMATE', 'PP_COSMIC_VARCUT1',
    'PP_COSMIC_VARCUT2', 'PP_COSMIC_INTCUT1', 'PP_COSMIC_INTCUT2',
    'PP_COSMIC_BOXSIZE', 'RAW_TO_PP_ROTATION', 'PP_DARK_MED_BINNUM',
    'SKIP_DONE_PP', 'ALLOWED_PPM_TYPES', 'PPM_MASK_NSIG', 'PP_MEDAMP_BINSIZE',
    'PP_BAD_EXPTIME_FRACTION',
    # object database settings
    'GL_GAIA_COL_NAME', 'GL_OBJ_COL_NAME', 'GL_ALIAS_COL_NAME',
    'GL_RV_COL_NAME', 'GL_RVREF_COL_NAME', 'GL_TEFF_COL_NAME',
    'GL_TEFFREF_COL_NAME', 'GL_R_ODO_COL', 'GL_R_PP_COL', 'GL_R_RV_COL',
    # image constants
    'FIBER_TYPES', 'IMAGE_X_FULL', 'IMAGE_Y_FULL',
    'INPUT_COMBINE_IMAGES', 'INPUT_FLIP_IMAGE', 'INPUT_RESIZE_IMAGE',
    'IMAGE_X_LOW', 'IMAGE_X_HIGH',
    'IMAGE_Y_LOW', 'IMAGE_Y_HIGH', 'IMAGE_X_LOW', 'IMAGE_X_HIGH',
    'IMAGE_Y_LOW', 'IMAGE_Y_HIGH', 'IMAGE_X_BLUE_LOW',
    'IMAGE_PIXEL_SIZE', 'FWHM_PIXEL_LSF', 'IMAGE_SATURATION',
    'IMAGE_FRAME_TIME',
    # general calib constants
    'COMBINE_METRIC_THRESHOLD1', 'CAVITY_1M_FILE', 'CAVITY_LL_FILE',
    'OBJ_LIST_GAIA_URL', 'CALIB_CHECK_FP_PERCENTILE', 'CALIB_CHECK_FP_THRES',
    'CALIB_CHECK_FP_CENT_SIZE', 'COMBINE_METRIC1_TYPES',
    'OBJ_LIST_GOOGLE_SHEET_URL', 'OBJ_LIST_GOOGLE_SHEET_WNUM',
    'OBJ_LIST_RESOLVE_FROM_DATABASE', 'OBJ_LIST_RESOLVE_FROM_GAIAID',
    'OBJ_LIST_RESOLVE_FROM_GLIST', 'OBJ_LIST_RESOLVE_FROM_COORDS',
    'OBJ_LIST_GAIA_EPOCH', 'OBJ_LIST_GAIA_PLX_LIM', 'OBJ_LIST_GAIA_MAG_CUT',
    'OBJ_LIST_CROSS_MATCH_RADIUS', 'ODOCODE_REJECT_GSHEET_ID',
    'ODOCODE_REJECT_GSHEET_NUM',
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
    'LOC_COEFFSIG_DEG', 'LOC_MAX_YPIX_VALUE',
    # shape constants
    'ALLOWED_FP_TYPES', 'FP_MASTER_MATCH_TIME',
    'FP_MASTER_PERCENT_THRES', 'SHAPE_QC_LTRANS_RES_THRES',
    'SHAPE_MASTER_VALIDFP_PERCENTILE', 'SHAPE_MASTER_VALIDFP_THRESHOLD',
    'SHAPE_MASTER_LINTRANS_NITER', 'SHAPE_MASTER_FP_INI_BOXSIZE',
    'SHAPE_MASTER_FP_SMALL_BOXSIZE', 'SHAPE_FP_MASTER_MIN_IN_GROUP',
    'SHAPE_MASTER_FIBER', 'SHAPE_NUM_ITERATIONS', 'SHAPE_ORDER_WIDTH',
    'SHAPE_NSECTIONS', 'SHAPE_SIGMACLIP_MAX', 'SHAPE_MASTER_DX_RMS_QC',
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
    'SHAPE_PLOT_SELECTED_ORDER',
    'SHAPEL_PLOT_ZOOM1', 'SHAPEL_PLOT_ZOOM2',
    # flat constants
    'FF_BLAZE_HALF_WINDOW', 'FF_BLAZE_THRESHOLD', 'FF_BLAZE_DEGREE',
    'FF_RMS_SKIP_ORDERS', 'QC_FF_MAX_RMS', 'FF_PLOT_ORDER',
    'FF_BLAZE_SCUT', 'FF_BLAZE_SIGFIT', 'FF_BLAZE_BPERCENTILE',
    'FF_BLAZE_NITER',
    # leakage constants
    'ALLOWED_LEAKM_TYPES', 'LEAKM_ALWAYS_EXTRACT', 'LEAKM_EXTRACT_TYPE',
    'ALLOWED_LEAK_TYPES', 'LEAK_EXTRACT_FILE', 'LEAK_2D_EXTRACT_FILES',
    'LEAK_1D_EXTRACT_FILES', 'LEAK_BCKGRD_PERCENTILE', 'LEAK_NORM_PERCENTILE',
    'LEAKM_WSMOOTH', 'LEAKM_KERSIZE', 'LEAK_LOW_PERCENTILE',
    'LEAK_HIGH_PERCENTILE', 'LEAK_BAD_RATIO_OFFSET',
    # extract constants
    'EXT_START_ORDER', 'EXT_END_ORDER', 'EXT_RANGE1', 'EXT_RANGE2',
    'EXT_SKIP_ORDERS', 'EXT_COSMIC_CORRETION', 'EXT_COSMIC_SIGCUT',
    'EXT_COSMIC_THRESHOLD', 'QC_EXT_FLUX_MAX', 'EXT_S1D_INTYPE',
    'EXT_S1D_INFILE', 'EXT_S1D_WAVESTART', 'EXT_S1D_WAVEEND',
    'EXT_S1D_BIN_UWAVE', 'EXT_S1D_BIN_UVELO', 'EXT_S1D_EDGE_SMOOTH_SIZE',
    'EXT_ALLOWED_BERV_DPRTYPES', 'EXT_BERV_EST_ACC', 'EXT_BERV_KIND',
    'EXT_BERV_BARYCORRPY_DIR', 'EXT_BERV_IERSFILE', 'EXT_BERV_IERS_A_URL',
    'EXT_BERV_LEAPDIR', 'EXT_BERV_LEAPUPDATE', 'EXTRACT_PLOT_ORDER',
    'EXTRACT_S1D_PLOT_ZOOM1', 'EXTRACT_S1D_PLOT_ZOOM2', 'EXT_QUICK_LOOK',
    # thermal constants
    'THERMAL_CORRECT', 'THERMAL_ALWAYS_EXTRACT', 'THERMAL_EXTRACT_TYPE',
    'THERMAL_CORRETION_TYPE1', 'THERMAL_CORRETION_TYPE2', 'THERMAL_ORDER',
    'THERMAL_FILTER_WID', 'THERMAL_RED_LIMIT', 'THERMAL_BLUE_LIMIT',
    'THERMAL_THRES_TAPAS', 'THERMAL_ENVELOPE_PERCENTILE',
    'THERMAL_PLOT_START_ORDER',
    # wave general constants
    'WAVE_MASTER_FIBER', 'WAVE_GUESS_CAVITY_WIDTH', 'WAVE_WAVESOL_FIT_DEGREE',
    'WAVE_CAVITY_FIT_DEGREE', 'WAVE_NSIG_CUT', 'WAVE_MIN_HC_LINES',
    'WAVE_MAX_FP_COUNT_OFFSET', 'WAVE_FP_COUNT_OFFSET_ITRS',
    'WAVE_CAVITY_FIT_ITRS1', 'WAVE_ORDER_OFFSET_ITRS',
    'WAVE_MAX_ORDER_BULK_OFFSET', 'WAVE_CAVITY_CHANGE_ERR_THRES',
    'WAVE_CAVITY_FIT_ITRS2', 'WAVE_HC_VEL_ODD_RATIO', 'WAVE_FWAVESOL_ITRS',
    'WAVE_FIBER_COMP_PLOT_ORD',
    # wave master reference constants
    'WAVEREF_NSIG_MIN', 'WAVEREF_EDGE_WMAX', 'WAVEREF_HC_BOXSIZE',
    'WAVEREF_HC_FIBTYPES', 'WAVEREF_FP_FIBTYPES', 'WAVEREF_FITDEG',
    'WAVEREF_FP_NLOW', 'WAVEREF_FP_NHIGH', 'WAVEREF_FP_POLYINV',
    # wave resolution settings
    'WAVE_RES_MAP_ORDER_BINS', 'WAVE_RES_MAP_SPATIAL_BINS',
    'WAVE_RES_MAP_FILTER_SIZE', 'WAVE_RES_VELO_CUTOFF1',
    'WAVE_RES_VELO_CUTOFF2',
    # wave ccf constants
    'WAVE_CCF_NOISE_SIGDET', 'WAVE_CCF_NOISE_BOXSIZE', 'WAVE_CCF_NOISE_THRES',
    'WAVE_CCF_STEP', 'WAVE_CCF_WIDTH', 'WAVE_CCF_TARGET_RV',
    'WAVE_CCF_DETNOISE', 'WAVE_CCF_MASK', 'WAVE_CCF_MASK_UNITS',
    'WAVE_CCF_MASK_PATH', 'WAVE_CCF_MASK_FMT', 'WAVE_CCF_MASK_MIN_WEIGHT',
    'WAVE_CCF_MASK_WIDTH', 'WAVE_CCF_N_ORD_MAX', 'WAVE_CCF_UPDATE_MASK',
    'WAVE_CCF_SMART_MASK_WIDTH', 'WAVE_CCF_SMART_MASK_MINLAM',
    'WAVE_CCF_SMART_MASK_MAXLAM', 'WAVE_CCF_SMART_MASK_TRIAL_NMIN',
    'WAVE_CCF_SMART_MASK_TRIAL_NMAX', 'WAVE_CCF_SMART_MASK_DWAVE_THRES',
    'WAVE_CCF_RV_THRES_QC', 'WAVE_CCF_MASK_NORMALIZATION',


    # TODO: sort out these constants
    # wave general constants
    'WAVE_MASTER_FIBER', 'WAVE_LINELIST_FILE', 'WAVE_LINELIST_FMT',
    'WAVE_LINELIST_AMPCOL', 'WAVE_LINELIST_COLS', 'WAVE_LINELIST_START',
    'WAVE_LINELIST_WAVECOL', 'WAVE_ALWAYS_EXTRACT', 'WAVE_EXTRACT_TYPE',
    'WAVE_FIT_DEGREE', 'WAVE_PIXEL_SHIFT_INTER', 'WAVE_PIXEL_SHIFT_SLOPE',
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
    'WAVE_FP_LARGE_JUMP', 'WAVE_FP_NORM_PERCENTILE', 'WAVE_FP_PEAK_LIM',
    'WAVE_FP_P2P_WIDTH_CUT', 'WAVE_FP_ERRX_MIN', 'WAVE_FP_LL_DEGR_FIT',
    'WAVE_FP_MAX_LLFIT_RMS', 'WAVE_FP_WEIGHT_THRES', 'WAVE_FP_BLAZE_THRES',
    'WAVE_FP_XDIF_MIN', 'WAVE_FP_XDIF_MAX', 'WAVE_FP_LL_OFFSET',
    'WAVE_FP_DV_MAX', 'WAVE_FP_UPDATE_CAVITY', 'WAVE_FP_CAVFIT_MODE',
    'WAVE_FP_LLFIT_MODE', 'WAVE_FP_LLDIF_MIN', 'WAVE_FP_LLDIF_MAX',
    'WAVE_FP_SIGCLIP', 'WAVE_FP_PLOT_MULTI_INIT', 'WAVE_FP_PLOT_MULTI_NBO',
    'WAVE_FP_DPRLIST',
    # wave night constants
    'WAVE_NIGHT_NITERATIONS1', 'WAVE_NIGHT_NITERATIONS2', 'WAVE_NIGHT_DCAVITY',
    'WAVE_NIGHT_HC_SIGCLIP', 'WAVE_NIGHT_MED_ABS_DEV',
    'WAVE_NIGHT_NSIG_FIT_CUT', 'WAVENIGHT_PLT_BINL', 'WAVENIGHT_PLT_BINU',
    'WAVENIGHT_PLT_NBINS',
    # telluric constants
    'TAPAS_FILE', 'TAPAS_FILE_FMT', 'TELLU_CUT_BLAZE_NORM',
    'TELLU_ALLOWED_DPRTYPES', 'TELLURIC_FILETYPE', 'TELLURIC_FIBER_TYPE',
    'TELLU_LIST_DIRECTORY', 'TELLU_WHITELIST_NAME', 'TELLU_BLACKLIST_NAME',
    # telluric pre-cleaning constants
    'TELLUP_DO_PRECLEANING', 'TELLUP_CCF_SCAN_RANGE', 'TELLUP_CLEAN_OH_LINES',
    'TELLUP_OHLINE_PCA_FILE', 'TELLUP_REMOVE_ORDS', 'TELLUP_SNR_MIN_THRES',
    'TELLUP_OTHERS_CCF_FILE', 'TELLUP_H2O_CCF_FILE', 'TELLUP_DEXPO_CONV_THRES',
    'TELLUP_DEXPO_MAX_ITR', 'TELLUP_ABSO_EXPO_KTHRES',
    'TELLUP_ABSO_EXPO_KWID', 'TELLUP_ABSO_EXPO_KEXP', 'TELLUP_TRANS_THRES',
    'TELLUP_TRANS_SIGLIM', 'TELLUP_FORCE_AIRMASS', 'TELLUP_D_WATER_ABSO',
    'TELLUP_OTHER_BOUNDS', 'TELLUP_WATER_BOUNDS', 'TELLUP_OHLINE_NBRIGHT',
    # make telluric constants
    'MKTELLU_BLAZE_PERCENTILE', 'MKTELLU_CUT_BLAZE_NORM', 'TELLU_ABSORBERS',
    'MKTELLU_DEFAULT_CONV_WIDTH', 'MKTELLU_TEMP_MED_FILT',
    'MKTELLU_PLOT_ORDER_NUMS', 'MKTELLU_TAU_WATER_ULIMIT',
    'MKTELLU_QC_SNR_ORDER', 'MKTELLU_QC_SNR_MIN', 'MKTELLU_QC_AIRMASS_DIFF',
    'MKTELLU_TRANS_MAX_WATERCOL', 'MKTELLU_TRANS_MIN_WATERCOL',
    'MKTELLU_THRES_TRANSFIT', 'MKTELLU_TRANS_FIT_UPPER_BAD',
    # fit telluric constants,
    'FTELLU_NUM_PRINCIPLE_COMP', 'FTELLU_ADD_DERIV_PC', 'FTELLU_FIT_DERIV_PC',
    'FTELLU_FIT_KEEP_NUM', 'FTELLU_FIT_MIN_TRANS', 'FTELLU_LAMBDA_MIN',
    'FTELLU_LAMBDA_MAX', 'FTELLU_KERNEL_VSINI', 'FTELLU_FIT_ITERS',
    'FTELLU_FIT_RECON_LIMIT', 'FTELLU_PLOT_ORDER_NUMS', 'FTELLU_SPLOT_ORDER',
    'FTELLU_QC_SNR_ORDER', 'FTELLU_QC_SNR_MIN', 'FTELLU_NUM_TRANS',
    # make template constants
    'MKTEMPLATE_SNR_ORDER', 'MKTEMPLATE_FILETYPE', 'MKTEMPLATE_FIBER_TYPE',
    'MKTEMPLATE_E2DS_ITNUM', 'MKTEMPLATE_E2DS_LOWF_SIZE',
    'MKTEMPLATE_S1D_ITNUM', 'MKTEMPLATE_S1D_LOWF_SIZE', 'MKTEMPLATE_FILESOURCE',
    'MKTEMPLATE_BERVCOR_QCMIN', 'MKTEMPLATE_BERVCOV_CSNR',
    'MKTEMPLATE_BERVCOV_RES',
    # ccf constants
    'CCF_MASK_PATH', 'CCF_NO_RV_VAL', 'CCF_MASK_MIN_WEIGHT', 'CCF_MASK_WIDTH',
    'CCF_N_ORD_MAX', 'CCF_DEFAULT_MASK', 'CCF_MASK_UNITS', 'CCF_MASK_FMT',
    'CCF_DEFAULT_WIDTH', 'CCF_DEFAULT_STEP', 'CCF_ALLOWED_DPRTYPES',
    'CCF_CORRECT_TELLU_TYPES', 'CCF_TELLU_THRES', 'CCF_FILL_NAN_KERN_SIZE',
    'CCF_FILL_NAN_KERN_RES', 'CCF_DET_NOISE', 'CCF_FIT_TYPE',
    'CCF_NOISE_SIGDET', 'CCF_NOISE_BOXSIZE', 'CCF_NOISE_THRES',
    'CCF_MAX_CCF_WID_STEP_RATIO', 'CCF_BLAZE_NORM_PERCENTILE',
    'CCF_OBJRV_NULL_VAL', 'CCF_MASK_NORMALIZATION',
    # general polar constants
    'POLAR_FIBERS', 'POLAR_STOKES_PARAMS', 'POLAR_BERV_CORRECT',
    'POLAR_SOURCE_RV_CORRECT', 'POLAR_METHOD', 'POLAR_INTERPOLATE_FLUX',
    'STOKESI_CONTINUUM_DET_ALG', 'POLAR_CONTINUUM_DET_ALG',
    'POLAR_NORMALIZE_STOKES_I', 'POLAR_REMOVE_CONTINUUM',
    'POLAR_CLEAN_BY_SIGMA_CLIPPING', 'POLAR_NSIGMA_CLIPPING',
    # polar poly moving median settings
    'POLAR_CONT_BINSIZE', 'POLAR_CONT_OVERLAP', 'POLAR_CONT_POLYNOMIAL_FIT',
    'POLAR_CONT_DEG_POLYNOMIAL',
    # polar iraf settings
    'STOKESI_IRAF_CONT_FIT_FUNC', 'POLAR_IRAF_CONT_FIT_FUNC',
    'STOKESI_IRAF_CONT_FUNC_ORDER', 'POLAR_IRAF_CONT_FUNC_ORDER',
    # polar lsd constants
    'POLAR_LSD_DIR', 'POLAR_LSD_FILE_KEY', 'POLAR_LSD_MIN_LANDE',
    'POLAR_LSD_MAX_LANDE', 'POLAR_LSD_CCFLINES_AIR_WAVE',
    'POLAR_LSD_MIN_LINEDEPTH', 'POLAR_LSD_V0', 'POLAR_LSD_VF', 'POLAR_LSD_NP',
    'POLAR_LSD_NORMALIZE', 'POLAR_LSD_REMOVE_EDGES',
    'POLAR_LSD_RES_POWER_GUESS',
    # debug output file settings
    'DEBUG_BACKGROUND_FILE', 'DEBUG_E2DSLL_FILE', 'DEBUG_SHAPE_FILES',
    'DEBUG_UNCORR_EXT_FILES',
    # debug dark plot settings
    'PLOT_DARK_IMAGE_REGIONS', 'PLOT_DARK_HISTOGRAM',
    # debug badpix plot settings
    'PLOT_BADPIX_MAP',
    # debug loc plot settings
    'PLOT_LOC_MINMAX_CENTS', 'PLOT_LOC_MIN_CENTS_THRES',
    'PLOT_LOC_FINDING_ORDERS', 'PLOT_LOC_IM_SAT_THRES', 'PLOT_LOC_ORD_VS_RMS',
    'PLOT_LOC_CHECK_COEFFS', 'PLOT_LOC_FIT_RESIDUALS',
    # debug shape plot settings
    'PLOT_SHAPE_DX', 'PLOT_SHAPE_ANGLE_OFFSET_ALL', 'PLOT_SHAPE_ANGLE_OFFSET',
    'PLOT_SHAPEL_ZOOM_SHIFT', 'PLOT_SHAPE_LINEAR_TPARAMS',
    # debug flat plot settings
    'PLOT_FLAT_ORDER_FIT_EDGES1', 'PLOT_FLAT_ORDER_FIT_EDGES2',
    'PLOT_FLAT_BLAZE_ORDER1', 'PLOT_FLAT_BLAZE_ORDER2',
    # debug thermal plot settings
    'PLOT_THERMAL_BACKGROUND',
    # debug extract plot settings
    'PLOT_EXTRACT_SPECTRAL_ORDER1', 'PLOT_EXTRACT_SPECTRAL_ORDER2',
    'PLOT_EXTRACT_S1D', 'PLOT_EXTRACT_S1D_WEIGHT',
    # debug wave plot settings
    'PLOT_WAVE_FIBER_COMPARISON', 'PLOT_WAVE_FIBER_COMP',
    'PLOT_WAVE_WL_CAV', 'PLOT_WAVE_HC_DIFF_HIST', 'PLOT_WAVEREF_EXPECTED',

    # debug wave plot settings
    'PLOT_WAVE_HC_GUESS', 'PLOT_WAVE_HC_TFIT_GRID',
    'PLOT_WAVE_HC_BRIGHTEST_LINES', 'PLOT_WAVE_HC_RESMAP',
    'PLOT_WAVE_LITTROW_CHECK1', 'PLOT_WAVE_LITTROW_EXTRAP1',
    'PLOT_WAVE_LITTROW_CHECK2', 'PLOT_WAVE_LITTROW_EXTRAP2',
    'PLOT_WAVE_FP_FINAL_ORDER', 'PLOT_WAVE_FP_LWID_OFFSET',
    'PLOT_WAVE_FP_WAVE_RES', 'PLOT_WAVE_FP_M_X_RES', 'PLOT_WAVE_FP_LL_DIFF',
    'PLOT_WAVE_FP_IPT_CWID_1MHC', 'PLOT_WAVE_FP_IPT_CWID_LLHC',
    'PLOT_WAVE_FP_MULTI_ORDER', 'PLOT_WAVE_FP_SINGLE_ORDER',
    'PLOT_WAVENIGHT_ITERPLOT', 'PLOT_WAVENIGHT_HISTPLOT',
    'PLOT_WAVE_RESMAP',
    # debug telluric plot settings
    'PLOT_TELLUP_WAVE_TRANS', 'PLOT_TELLUP_ABSO_SPEC',
    'PLOT_MKTELLU_WAVE_FLUX1', 'PLOT_MKTELLU_WAVE_FLUX2',
    'PLOT_FTELLU_PCA_COMP1', 'PLOT_FTELLU_PCA_COMP2',
    'PLOT_FTELLU_RECON_SPLINE1', 'PLOT_FTELLU_RECON_SPLINE2',
    'PLOT_FTELLU_WAVE_SHIFT1', 'PLOT_FTELLU_WAVE_SHIFT2',
    'PLOT_FTELLU_RECON_ABSO1', 'PLOT_FTELLU_RECON_ABSO2',
    'PLOT_MKTEMP_BERV_COV', 'PLOT_TELLUP_CLEAN_OH',
    # debug ccf plot settings
    'PLOT_CCF_RV_FIT_LOOP', 'PLOT_CCF_RV_FIT', 'PLOT_CCF_SWAVE_REF',
    'PLOT_CCF_PHOTON_UNCERT',
    # debug polar plot settings
    'PLOT_POLAR_FIT_CONT', 'PLOT_POLAR_CONTINUUM', 'PLOT_POLAR_RESULTS',
    'PLOT_POLAR_STOKES_I', 'PLOT_POLAR_LSD',
    # post processing settings
    'POST_CLEAR_REDUCED', 'POST_OVERWRITE', 'POST_HDREXT_COMMENT_KEY',
    # tool constants
    'REPROCESS_RUN_KEY', 'REPROCESS_OBSDIR_COL', 'REPROCESS_ABSFILECOL',
    'REPROCESS_MODIFIEDCOL', 'REPROCESS_SORTCOL_HDRKEY',
    'REPROCESS_RAWINDEXFILE', 'REPROCESS_SEQCOL', 'REPROCESS_TIMECOL',
    'REPROCESS_OBJ_DPRTYPES',
    'SUMMARY_LATEX_PDF', 'EXPMETER_MIN_LAMBDA', 'EXPMETER_MAX_LAMBDA',
    'EXPMETER_TELLU_THRES', 'REPROCESS_PINAMECOL', 'DRIFT_DPRTYPES',
    'DRIFT_DPR_FIBER_TYPE', 'REPROCESS_MP_TYPE',
]

# set name
__NAME__ = 'core.instruments.default.default_constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Constants class
Const = constant_functions.Const

# =============================================================================
# DRS DATA SETTINGS
# =============================================================================
cgroup = 'DRS DATA SETTINGS'
# Define the data engineering path
DATA_ENGINEERING = Const('DATA_ENGINEERING', value=None, dtype=str,
                         source=__NAME__, group=cgroup,
                         description='Define the data engineering path')

# Define core data path
DATA_CORE = Const('DATA_CORE', value=None, dtype=str, source=__NAME__,
                  group=cgroup, description='Define core data path')

# Define whether to force wave solution from calibration database (instead of
#  using header wave solution if available)
CALIB_DB_FORCE_WAVESOL = Const('CALIB_DB_FORCE_WAVESOL', value=None,
                               dtype=bool, source=__NAME__, user=True,
                               active=False, group=cgroup,
                               description='Define whether to force wave '
                                           'solution from calibration database '
                                           '(instead of using header wave '
                                           'solution if available)')

# =============================================================================
# COMMON IMAGE SETTINGS
# =============================================================================
cgroup = 'COMMON IMAGE SETTINGS'

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
RAW_TO_PP_ROTATION = Const('RAW_TO_PP_ROTATION', dtype=int, value=None,
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

# Define raw image size (mostly just used as a check and in places where we
#   don't have access to this information) in x dim
IMAGE_X_FULL = Const('IMAGE_X_FULL', dtype=int, value=None, source=__NAME__,
                     group=cgroup, 
                     description=('Define raw image size (mostly just used as '
                                  'a check and in places where we dont have '
                                  'access to this information) in x dim'))

# Define raw image size (mostly just used as a check and in places where we
#   don't have access to this information) in y dim
IMAGE_Y_FULL = Const('IMAGE_Y_FULL', dtype=int, value=None, source=__NAME__,
                     group=cgroup,
                     description=('Define raw image size (mostly just used as '
                                  'a check and in places where we dont have '
                                  'access to this information) in y dim'))

# Define the fibers
FIBER_TYPES = Const('FIBER_TYPES', dtype=str, value=None, source=__NAME__,
                    group=cgroup, description='Define the fibers')

# Defines whether to by default combine images that are inputted at the same
# time
INPUT_COMBINE_IMAGES = Const('INPUT_COMBINE_IMAGES', dtype=bool, value=True,
                             source=__NAME__, user=True, active=False,
                             group=cgroup,
                             description='Defines whether to by default combine'
                                         ' images that are inputted at the '
                                         'same time')

# Defines whether to, by default, flip images that are inputted
INPUT_FLIP_IMAGE = Const('INPUT_FLIP_IMAGE', dtype=bool, value=True,
                         source=__NAME__, group=cgroup, 
                         description=('Defines whether to, by default, '
                                      'flip images that are inputted'))

# Defines whether to, by default, resize images that are inputted
INPUT_RESIZE_IMAGE = Const('INPUT_RESIZE_IMAGE', dtype=bool, value=True,
                           source=__NAME__, group=cgroup, 
                           description=('Defines whether to, by default, '
                                        'resize images that are inputted'))

# Defines the resized image
IMAGE_X_LOW = Const('IMAGE_X_LOW', value=None, dtype=int, minimum=0,
                    source=__NAME__, group=cgroup,
                    description='Defines the resized image')
IMAGE_X_HIGH = Const('IMAGE_X_HIGH', value=None, dtype=int, minimum=0,
                     source=__NAME__, group=cgroup, description='')
IMAGE_Y_LOW = Const('IMAGE_Y_LOW', value=None, dtype=int, minimum=0,
                    source=__NAME__, group=cgroup, description='')
IMAGE_Y_HIGH = Const('IMAGE_Y_HIGH', value=None, dtype=int, minimum=0,
                     source=__NAME__, group=cgroup, description='')

# Define the pixel size in km/s / pix
#    also used for the median sampling size in tellu correction
IMAGE_PIXEL_SIZE = Const('IMAGE_PIXEL_SIZE', value=None, dtype=float,
                         source=__NAME__, group=cgroup, 
                         description=('Define the pixel size in km/s / pix '
                                      'also used for the median sampling '
                                      'size in tellu correction'))

# Define mean line width expressed in pix
FWHM_PIXEL_LSF = Const('FWHM_PIXEL_LSF', value=None, dtype=float,
                       source=__NAME__, group=cgroup,
                       description='Define mean line width expressed in pix')

# Define the point at which the detector saturates
IMAGE_SATURATION = Const('IMAGE_SATURATION', value=None, dtype=float,
                         source=__NAME__, group=cgroup,
                         description='Define the point at which the detector '
                                     'saturates')

# Define the frame time for an image
IMAGE_FRAME_TIME = Const('IMAGE_FRAME_TIME', value=None, dtype=float,
                         source=__NAME__, group=cgroup,
                         description='Define the frame time for an image')

# =============================================================================
# CALIBRATION: GENERAL SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: GENERAL SETTINGS'

# Define the threshold under which a file should not be combined
#  (metric is compared to the median of all files 1 = perfect, 0 = noise)
COMBINE_METRIC_THRESHOLD1 = Const('COMBINE_METRIC_THRESHOLD1', value=None,
                                  dtype=float, source=__NAME__, group=cgroup,
                                  minimum=0, maximum=1, 
                                  description=('Define the threshold under '
                                               'which a file should not be '
                                               'combined (metric is compared '
                                               'to the median of all files 1 '
                                               '= perfect, 0 = noise)'))

# Define the DPRTYPES allowed for the combine metric 1 comparison
COMBINE_METRIC1_TYPES = Const('COMBINE_METRIC1_TYPES', value=None, dtype=str,
                              source=__NAME__, group=cgroup, 
                              description=('Define the DPRTYPES allowed for '
                                           'the combine metric 1 comparison'))

# Define the coefficients of the fit of 1/m vs d
CAVITY_1M_FILE = Const('CAVITY_1M_FILE', value=None, dtype=str, source=__NAME__,
                       group=cgroup, 
                       description=('Define the coefficients of the fit of '
                                    '1/m vs d'))

# Define the coefficients of the fit of wavelength vs d
CAVITY_LL_FILE = Const('CAVITY_LL_FILE', value=None, dtype=str, source=__NAME__,
                       group=cgroup, 
                       description=('Define the coefficients of the fit of '
                                    'wavelength vs d'))

# define the check FP percentile level
CALIB_CHECK_FP_PERCENTILE = Const('CALIB_CHECK_FP_PERCENTILE', value=None,
                                  dtype=int, minimum=0, source=__NAME__,
                                  group=cgroup, 
                                  description=('define the check FP percentile '
                                               'level'))

# define the check FP threshold qc parameter
CALIB_CHECK_FP_THRES = Const('CALIB_CHECK_FP_THRES', value=None,
                             dtype=float, minimum=0.0, source=__NAME__,
                             group=cgroup, 
                             description=('define the check FP threshold qc '
                                          'parameter'))

# define the check FP center image size [px]
CALIB_CHECK_FP_CENT_SIZE = Const('CALIB_CHECK_FP_CENT_SIZE', value=None,
                                 dtype=int, minimum=0, source=__NAME__,
                                 group=cgroup, 
                                 description=('define the check FP center '
                                              'image size [px]'))

# Define the TAP Gaia URL (for use in crossmatching to Gaia via astroquery)
OBJ_LIST_GAIA_URL = Const('OBJ_LIST_GAIA_URL', value=None, dtype=str,
                          source=__NAME__, group=cgroup, 
                          description=('Define the TAP Gaia URL (for use in '
                                       'crossmatching to Gaia via astroquery)'))

# Define the google sheet to use for crossmatch
OBJ_LIST_GOOGLE_SHEET_URL = Const('OBJ_LIST_GOOGLE_SHEET_URL', value=None,
                                  dtype=str, source=__NAME__, group=cgroup, 
                                  description=('Define the google sheet to use '
                                               'for crossmatch'))

# Define the google sheet workbook number
OBJ_LIST_GOOGLE_SHEET_WNUM = Const('OBJ_LIST_GOOGLE_SHEET_WNUM', value=0,
                                   dtype=int, source=__NAME__, group=cgroup,
                                   minimum=0, 
                                   description=('Define the google sheet '
                                                'workbook number'))

# Define whether to resolve from local database (via drs_database / drs_db)
OBJ_LIST_RESOLVE_FROM_DATABASE = Const('OBJ_LIST_RESOLVE_FROM_DATABASE',
                                       value=None, dtype=bool, source=__NAME__,
                                       group=cgroup, 
                                       description=('Define whether to resolve '
                                                    'from local database '
                                                    '(via drs_database / '
                                                    'drs_db)'))

# Define whether to resolve from gaia id (via TapPlus to Gaia) if False
#    ra/dec/pmra/pmde/plx will always come from header
OBJ_LIST_RESOLVE_FROM_GAIAID = Const('OBJ_LIST_RESOLVE_FROM_GAIAID',
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
OBJ_LIST_RESOLVE_FROM_GLIST = Const('OBJ_LIST_RESOLVE_FROM_GLIST',
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
OBJ_LIST_RESOLVE_FROM_COORDS = Const('OBJ_LIST_RESOLVE_FROM_COORDS',
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
OBJ_LIST_GAIA_EPOCH = Const('OBJ_LIST_GAIA_EPOCH', value=None, dtype=float,
                            source=__NAME__, minimum=2000.0, maximum=2100.0,
                            group=cgroup, 
                            description=('Define the gaia epoch to use in '
                                         'the gaia query'))

# Define the radius for crossmatching objects (in both lookup table and query)
#   in arcseconds
OBJ_LIST_CROSS_MATCH_RADIUS = Const('OBJ_LIST_CROSS_MATCH_RADIUS', value=None,
                                    dtype=float, source=__NAME__, minimum=0.0,
                                    group=cgroup, 
                                    description=('Define the radius for '
                                                 'crossmatching objects (in '
                                                 'both lookup table and '
                                                 'query) in arcseconds'))

# Define the gaia parallax limit for using gaia point
OBJ_LIST_GAIA_PLX_LIM = Const('OBJ_LIST_GAIA_PLX_LIM', value=None, dtype=float,
                              source=__NAME__, minimum=0.0, group=cgroup, 
                              description=('Define the gaia parallax limit '
                                           'for using gaia point'))

# Define the gaia magnitude cut to use in the gaia query
OBJ_LIST_GAIA_MAG_CUT = Const('OBJ_LIST_GAIA_MAG_CUT', value=None, dtype=float,
                              source=__NAME__, minimum=10.0, maximum=25.0,
                              group=cgroup, 
                              description=('Define the gaia magnitude cut to '
                                           'use in the gaia query'))

# Define the odometer code rejection google sheet id
ODOCODE_REJECT_GSHEET_ID = Const('ODOCODE_REJECT_GSHEET_ID', value=None,
                                 dtype=str, source=__NAME__, group=cgroup, 
                                 description=('Define the odometer code '
                                              'rejection google sheet id'))

# Define the odmeter code rejection google sheet workbook
ODOCODE_REJECT_GSHEET_NUM = Const('ODOCODE_REJECT_GSHEET_NUM', value=int,
                                  dtype=str, source=__NAME__, minimum=0,
                                  group=cgroup, 
                                  description=('Define the odmeter code '
                                               'rejection google sheet '
                                               'workbook'))

# =============================================================================
# CALIBRATION: FIBER SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: FIBER SETTINGS'
# Number of orders to skip at start of image
FIBER_FIRST_ORDER_JUMP_AB = Const('FIBER_FIRST_ORDER_JUMP_AB', value=None,
                                  dtype=int, minimum=0, source=__NAME__,
                                  group=cgroup, 
                                  description=('Number of orders to skip '
                                               'at start of image'))
FIBER_FIRST_ORDER_JUMP_A = Const('FIBER_FIRST_ORDER_JUMP_A', value=None,
                                 dtype=int, minimum=0, source=__NAME__,
                                 group=cgroup, description='')
FIBER_FIRST_ORDER_JUMP_B = Const('FIBER_FIRST_ORDER_JUMP_B', value=None,
                                 dtype=int, minimum=0, source=__NAME__,
                                 group=cgroup, description='')
FIBER_FIRST_ORDER_JUMP_C = Const('FIBER_FIRST_ORDER_JUMP_C', value=None,
                                 dtype=int, minimum=0, source=__NAME__,
                                 group=cgroup, description='')

# Maximum number of order to use
FIBER_MAX_NUM_ORDERS_AB = Const('FIBER_MAX_NUM_ORDERS_AB', value=None,
                                dtype=int, minimum=1, source=__NAME__,
                                group=cgroup,
                                description='Maximum number of order to use')
FIBER_MAX_NUM_ORDERS_A = Const('FIBER_MAX_NUM_ORDERS_A', value=None,
                               dtype=int, minimum=1, source=__NAME__,
                               group=cgroup, description='')
FIBER_MAX_NUM_ORDERS_B = Const('FIBER_MAX_NUM_ORDERS_B', value=None,
                               dtype=int, minimum=1, source=__NAME__,
                               group=cgroup, description='')
FIBER_MAX_NUM_ORDERS_C = Const('FIBER_MAX_NUM_ORDERS_C', value=None,
                               dtype=int, minimum=1, source=__NAME__,
                               group=cgroup, description='')

# Number of fibers
FIBER_SET_NUM_FIBERS_AB = Const('FIBER_SET_NUM_FIBERS_AB', value=None,
                                dtype=int, minimum=1, source=__NAME__,
                                group=cgroup,
                                description='Number of fibers')
FIBER_SET_NUM_FIBERS_A = Const('FIBER_SET_NUM_FIBERS_A', value=None,
                               dtype=int, minimum=1, source=__NAME__,
                               group=cgroup, description='')
FIBER_SET_NUM_FIBERS_B = Const('FIBER_SET_NUM_FIBERS_B', value=None,
                               dtype=int, minimum=1, source=__NAME__,
                               group=cgroup, description='')
FIBER_SET_NUM_FIBERS_C = Const('FIBER_SET_NUM_FIBERS_C', value=None,
                               dtype=int, minimum=1, source=__NAME__,
                               group=cgroup, description='')

# =============================================================================
# PRE-PROCESSSING SETTINGS
# =============================================================================
cgroup = 'PRE-PROCESSING SETTINGS'
# Define object dpr types
PP_OBJ_DPRTYPES = Const('PP_OBJ_DPRTYPES', value=None, dtype=str,
                        source=__NAME__, group=cgroup,
                        description='Define object dpr types')

# Define the bad list google spreadsheet id
PP_BADLIST_SSID = Const('PP_BADLIST_SSID', value=None, dtype=str,
                        source=__NAME__, group=cgroup,
                        description='Define the bad list google spreadsheet id')

# Define the bad list google workbook number
PP_BADLIST_SSWB = Const('PP_BADLIST_SSWB', value=None, dtype=int,
                        source=__NAME__, group=cgroup,
                        description='Define the bad list google workbook '
                                    'number')

# Define the bad list header key
PP_BADLIST_DRS_HKEY = Const('PP_BADLIST_DRS_HKEY', value=None, dtype=str,
                            source=__NAME__, group=cgroup,
                            description='Define the bad list header key')

# Define the bad list google spreadsheet value column
PP_BADLIST_SS_VALCOL = Const('PP_BADLIST_SS_VALCOL', value=None, dtype=str,
                            source=__NAME__, group=cgroup,
                            description='Define the bad list google '
                                        'spreadsheet value column')

# Define the bad list google spreadsheet mask column for preprocessing
PP_BADLIST_SS_MASKCOL = Const('PP_BADLIST_SS_MASKCOL', value=None, dtype=str,
                              source=__NAME__, group=cgroup,
                              description='Define the bad list google '
                                          'spreadsheet mask column for '
                                          'preprocessing')

# Defines the box size surrounding hot pixels to use
PP_HOTPIX_BOXSIZE = Const('PP_HOTPIX_BOXSIZE', value=None, dtype=int,
                          minimum=1, source=__NAME__, group=cgroup, 
                          description=('Defines the box size surrounding '
                                       'hot pixels to use'))

# Defines the size around badpixels that is considered part of the bad pixel
PP_CORRUPT_MED_SIZE = Const('PP_CORRUPT_MED_SIZE', value=None, dtype=int,
                            minimum=1, source=__NAME__, group=cgroup, 
                            description=('Defines the size around badpixels '
                                         'that is considered part of the '
                                         'bad pixel'))

# Define the fraction of the required exposure time that is required for a
#   valid observation
PP_BAD_EXPTIME_FRACTION = Const('PP_BAD_EXPTIME_FRACTION', value=None,
                                dtype=float, minimum=0, source=__NAME__,
                                group=cgroup, 
                                description=('Define the fraction of the '
                                             'required exposure time that '
                                             'is required for a valid '
                                             'observation'))

# Defines the threshold in sigma that selects hot pixels
PP_CORRUPT_HOT_THRES = Const('PP_CORRUPT_HOT_THRES', value=None, dtype=int,
                             minimum=0, source=__NAME__, group=cgroup, 
                             description=('Defines the threshold in sigma that '
                                          'selects hot pixels'))

# Define the total number of amplifiers
PP_TOTAL_AMP_NUM = Const('PP_TOTAL_AMP_NUM', value=None, dtype=int,
                         minimum=0, source=__NAME__, group=cgroup,
                         description='Define the total number of amplifiers')

# Define the number of dark amplifiers
PP_NUM_DARK_AMP = Const('PP_NUM_DARK_AMP', value=None, dtype=int,
                        minimum=0, source=__NAME__, group=cgroup,
                        description='Define the number of dark amplifiers')

# Define the number of bins used in the dark median process         - [apero_preprocess]
PP_DARK_MED_BINNUM = Const('PP_DARK_MED_BINNUM', value=None, dtype=int,
                           minimum=0, source=__NAME__, group=cgroup, 
                           description=('Define the number of bins used in the '
                                        'dark median process - [apero_preprocess]'))

#   Defines the pp hot pixel file (located in the data folder)
PP_HOTPIX_FILE = Const('PP_HOTPIX_FILE', value=None, dtype=str, source=__NAME__,
                       group=cgroup, 
                       description=('Defines the pp hot pixel file (located in '
                                    'the data folder)'))

# Define the number of un-illuminated reference pixels at top of image
PP_NUM_REF_TOP = Const('PP_NUM_REF_TOP', value=None, dtype=int,
                       source=__NAME__, group=cgroup, 
                       description=('Define the number of un-illuminated '
                                    'reference pixels at top of image'))

# Define the number of un-illuminated reference pixels at bottom of image
PP_NUM_REF_BOTTOM = Const('PP_NUM_REF_BOTTOM', value=None, dtype=int,
                          source=__NAME__, group=cgroup, 
                          description=('Define the number of un-illuminated '
                                       'reference pixels at bottom of image'))

# Define the number of un-illuminated reference pixels at left of image
PP_NUM_REF_LEFT = Const('PP_NUM_REF_LEFT', value=None, dtype=int,
                          source=__NAME__, group=cgroup,
                          description=('Define the number of un-illuminated '
                                       'reference pixels at left of image'))

# Define the number of un-illuminated reference pixels at right of image
PP_NUM_REF_RIGHT = Const('PP_NUM_REF_RIGHT', value=None, dtype=int,
                          source=__NAME__, group=cgroup,
                          description=('Define the number of un-illuminated '
                                       'reference pixels at right of image'))

# Define the percentile value for the rms normalisation (0-100)
PP_RMS_PERCENTILE = Const('PP_RMS_PERCENTILE', value=None, dtype=int,
                          minimum=0, maximum=100, source=__NAME__, group=cgroup, 
                          description=('Define the percentile value for the '
                                       'rms normalisation (0-100)'))

# Define the lowest rms value of the rms percentile allowed if the value of
#   the pp_rms_percentile-th is lower than this this value is used
PP_LOWEST_RMS_PERCENTILE = Const('PP_LOWEST_RMS_PERCENTILE', value=None,
                                 dtype=float, minimum=0.0, source=__NAME__,
                                 group=cgroup, 
                                 description=('Define the lowest rms value of '
                                              'the rms percentile allowed if '
                                              'the value of the '
                                              'pp_rms_percentile-th is lower '
                                              'than this this value is used'))

# Defines the snr hotpix threshold to define a corrupt file
PP_CORRUPT_SNR_HOTPIX = Const('PP_CORRUPT_SNR_HOTPIX', value=None, dtype=float,
                              minimum=0.0, source=__NAME__, group=cgroup, 
                              description=('Defines the snr hotpix threshold '
                                           'to define a corrupt file'))

# Defines the RMS threshold to also catch corrupt files
PP_CORRUPT_RMS_THRES = Const('PP_CORRUPT_RMS_THRES', value=None, dtype=float,
                             minimum=0.0, source=__NAME__, group=cgroup, 
                             description=('Defines the RMS threshold to also '
                                          'catch corrupt files'))

# super-pessimistic noise estimate. Includes uncorrected common noise
PP_COSMIC_NOISE_ESTIMATE = Const('PP_COSMIC_NOISE_ESTIMATE', value=None,
                                 dtype=float, minimum=0.0, source=__NAME__,
                                 group=cgroup,
                                 description=('super-pessimistic noise '
                                              'estimate. Includes uncorrected '
                                              'common noise'))

# define the cuts in sigma where we should look for cosmics (variance)
PP_COSMIC_VARCUT1 = Const('PP_COSMIC_VARCUT1', value=None, dtype=float,
                          minimum=0.0, source=__NAME__, group=cgroup,
                          description=('define the cuts in sigma where we '
                                       'should look for cosmics (variance)'))

# define the cuts in sigma where we should look for cosmics (variance)
PP_COSMIC_VARCUT2 = Const('PP_COSMIC_VARCUT2', value=None, dtype=float,
                          minimum=0.0, source=__NAME__, group=cgroup,
                          description=('define the cuts in sigma where we '
                                       'should look for cosmics (variance)'))

# define the cuts in sigma where we should look for cosmics (intercept)
PP_COSMIC_INTCUT1 = Const('PP_COSMIC_INTCUT1', value=None, dtype=float,
                          minimum=0.0, source=__NAME__, group=cgroup,
                          description=('define the cuts in sigma where we '
                                       'should look for cosmics (intercept)'))

# define the cuts in sigma where we should look for cosmics (intercept)
PP_COSMIC_INTCUT2 = Const('PP_COSMIC_INTCUT2', value=None, dtype=float,
                          minimum=0.0, source=__NAME__, group=cgroup,
                          description=('define the cuts in sigma where we '
                                       'should look for cosmics (intercept)'))

# random box size [in pixels] to speed-up low-frequency band computation
PP_COSMIC_BOXSIZE = Const('PP_COSMIC_BOXSIZE', value=None, dtype=int,
                          minimum=0.0, source=__NAME__, group=cgroup,
                          description=('random box size [in pixels] to '
                                       'speed-up low-frequency band '
                                       'computation'))

# Define whether to skip preprocessed files that have already be processed
SKIP_DONE_PP = Const('SKIP_DONE_PP', value=None, dtype=bool,
                     source=__NAME__, user=True, active=False, group=cgroup,
                     description='Define whether to skip preprocessed files '
                                 'that have already be processed')

# Define allowed preprocess master file types (PP DPRTYPE)
ALLOWED_PPM_TYPES = Const('ALLOWED_PPM_TYPES', value=None, dtype=str,
                          source=__NAME__, group=cgroup,
                          description='Define allowed preprocess master '
                                      'filetypes (PP DPRTYPE)')

# Define the allowed number of sigma for preprocessing master mask
PPM_MASK_NSIG = Const('PPM_MASK_NSIG', value=None, dtype=float,
                      source=__NAME__, group=cgroup,
                      description='Define allowed preprocess master mask '
                                  'number of sigma')

# Define the bin to use to correct low level frequences. This value cannot
#   be smaller than the order footprint on the array as it would lead to a set
#   of NaNs in the downsized image
PP_MEDAMP_BINSIZE = Const('PP_MEDAMP_BINSIZE', value=None, dtype=int,
                          source=__NAME__, group=cgroup,
                          description='Define the bin to use to correct low '
                                      'level frequences. This value cannot be '
                                      'smaller than the order footprint on the '
                                      'array as it would lead to a set of NaNs '
                                      'in the downsized image')

# =============================================================================
# CALIBRATION: OBJECT DATABASE SETTINGS
# =============================================================================
# gaia col name in google sheet
GL_GAIA_COL_NAME = Const('GL_GAIA_COL_NAME', value=None, dtype=str,
                         source=__NAME__, group=cgroup,
                         description='gaia col name in google sheet')
# object col name in google sheet
GL_OBJ_COL_NAME = Const('GL_OBJ_COL_NAME', value=None, dtype=str,
                        source=__NAME__, group=cgroup,
                        description='object col name in google sheet')
# alias col name in google sheet
GL_ALIAS_COL_NAME = Const('GL_ALIAS_COL_NAME', value=None, dtype=str,
                          source=__NAME__, group=cgroup,
                          description='alias col name in google sheet')
# rv col name in google sheet
GL_RV_COL_NAME = Const('GL_RV_COL_NAME', value=None, dtype=str,
                       source=__NAME__, group=cgroup,
                       description='rv col name in google sheet')
GL_RVREF_COL_NAME = Const('GL_RVREF_COL_NAME', value=None, dtype=str,
                          source=__NAME__, group=cgroup, description='')
# teff col name in google sheet
GL_TEFF_COL_NAME = Const('GL_TEFF_COL_NAME', value=None, dtype=str,
                         source=__NAME__, group=cgroup,
                         description='teff col name in google sheet')
GL_TEFFREF_COL_NAME = Const('GL_TEFFREF_COL_NAME', value=None, dtype=str,
                            source=__NAME__, group=cgroup, description='')
# Reject like google columns
GL_R_ODO_COL = Const('GL_R_ODO_COL', value=None, dtype=str,
                     source=__NAME__, group=cgroup,
                     description='Reject like google columns')
GL_R_PP_COL = Const('GL_R_PP_COL', value=None, dtype=str,
                    source=__NAME__, group=cgroup, description='')
GL_R_RV_COL = Const('GL_R_RV_COL', value=None, dtype=str,
                    source=__NAME__, group=cgroup, description='')

# =============================================================================
# CALIBRATION: DARK SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: DARK SETTINGS'
# Min dark exposure time
QC_DARK_TIME = Const('QC_DARK_TIME', value=None, dtype=float, minimum=0.0,
                     source=__NAME__, group=cgroup,
                     description='Min dark exposure time')

# Max dark median level [ADU/s]
QC_MAX_DARKLEVEL = Const('QC_MAX_DARKLEVEL', value=None, dtype=float,
                         source=__NAME__, group=cgroup,
                         description='Max dark median level [ADU/s]')

# Max fraction of dark pixels (percent)
QC_MAX_DARK = Const('QC_MAX_DARK', value=None, dtype=float, source=__NAME__,
                    group=cgroup,
                    description='Max fraction of dark pixels (percent)')

# Max fraction of dead pixels
QC_MAX_DEAD = Const('QC_MAX_DEAD', value=None, dtype=float, source=__NAME__,
                    group=cgroup, description='Max fraction of dead pixels')

# Defines the resized blue image
IMAGE_X_BLUE_LOW = Const('IMAGE_X_BLUE_LOW', value=None, dtype=int, minimum=0,
                         source=__NAME__, group=cgroup,
                         description='Defines the resized blue image')
IMAGE_X_BLUE_HIGH = Const('IMAGE_X_BLUE_HIGH', value=None, dtype=int, minimum=0,
                          source=__NAME__, group=cgroup, description='')
IMAGE_Y_BLUE_LOW = Const('IMAGE_Y_BLUE_LOW', value=None, dtype=int, minimum=0,
                         source=__NAME__, group=cgroup, description='')
IMAGE_Y_BLUE_HIGH = Const('IMAGE_Y_BLUE_HIGH', value=None, dtype=int, minimum=0,
                          source=__NAME__, group=cgroup, description='')

# Defines the resized red image
IMAGE_X_RED_LOW = Const('IMAGE_X_RED_LOW', value=None, dtype=int, minimum=0,
                        source=__NAME__, group=cgroup,
                        description='Defines the resized red image')
IMAGE_X_RED_HIGH = Const('IMAGE_X_RED_HIGH', value=None, dtype=int, minimum=0,
                         source=__NAME__, group=cgroup, description='')
IMAGE_Y_RED_LOW = Const('IMAGE_Y_RED_LOW', value=None, dtype=int, minimum=0,
                        source=__NAME__, group=cgroup, description='')
IMAGE_Y_RED_HIGH = Const('IMAGE_Y_RED_HIGH', value=None, dtype=int, minimum=0,
                         source=__NAME__, group=cgroup, description='')

# Define a bad pixel cut limit (in ADU/s)
DARK_CUTLIMIT = Const('DARK_CUTLIMIT', value=None, dtype=float, source=__NAME__,
                      group=cgroup,
                      description='Define a bad pixel cut limit (in ADU/s)')

# Defines the lower and upper percentiles when measuring the dark
DARK_QMIN = Const('DARK_QMIN', value=None, dtype=int, source=__NAME__,
                  minimum=0, maximum=100, group=cgroup, 
                  description=('Defines the lower and upper percentiles when '
                               'measuring the dark'))
DARK_QMAX = Const('DARK_QMAX', value=None, dtype=int, source=__NAME__,
                  minimum=0, maximum=100, group=cgroup, description='')

# The number of bins in dark histogram
HISTO_BINS = Const('HISTO_BINS', value=None, dtype=int, source=__NAME__,
                   minimum=1, group=cgroup,
                   description='The number of bins in dark histogram')

# The range of the histogram in ADU/s
HISTO_RANGE_LOW = Const('HISTO_RANGE_LOW', value=None, dtype=int,
                        source=__NAME__, group=cgroup,
                        description='The range of the histogram in ADU/s')
HISTO_RANGE_HIGH = Const('HISTO_RANGE_LOW', value=None, dtype=int,
                         source=__NAME__, group=cgroup)

#  Define whether to use SKYDARK for dark corrections
USE_SKYDARK_CORRECTION = Const('USE_SKYDARK_CORRECTION', value=None,
                               dtype=bool, source=__NAME__, group=cgroup, 
                               description=('Define whether to use SKYDARK for '
                                            'dark corrections'))

#  If use_skydark_correction is True define whether we use
#     the SKYDARK only or use SKYDARK/DARK (whichever is closest)
USE_SKYDARK_ONLY = Const('USE_SKYDARK_ONLY', value=None, dtype=bool,
                         source=__NAME__, group=cgroup, 
                         description=('If use_skydark_correction is True define'
                                      ' whether we use the SKYDARK only or use '
                                      'SKYDARK/DARK (whichever is closest)'))

#  Define the allowed DPRTYPES for finding files for DARK_MASTER will
#      only find those types define by 'filetype' but 'filetype' must
#      be one of theses (strings separated by commas)
ALLOWED_DARK_TYPES = Const('ALLOWED_DARK_TYPES', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           description=('Define the allowed DPRTYPES for '
                                        'finding files for DARK_MASTER will '
                                        'only find those types define by '
                                        'filetype but filetype must be one '
                                        'of theses (strings separated by '
                                        'commas)'))

# Define the maximum time span to combine dark files over (in hours)
DARK_MASTER_MATCH_TIME = Const('DARK_MASTER_MATCH_TIME', value=None,
                               dtype=float, source=__NAME__, group=cgroup, 
                               description=('Define the maximum time span to '
                                            'combine dark files over (in '
                                            'hours)'))

# median filter size for dark master
DARK_MASTER_MED_SIZE = Const('DARK_MASTER_MED_SIZE', value=None, dtype=int,
                             source=__NAME__, group=cgroup,
                             description='median filter size for dark master')

# =============================================================================
# CALIBRATION: BAD PIXEL MAP SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: BAD PIXEL MAP SETTINGS'
# Defines the full detector flat file (located in the data folder)
BADPIX_FULL_FLAT = Const('BADPIX_FULL_FLAT', value=None, dtype=str,
                         source=__NAME__, group=cgroup, 
                         description=('Defines the full detector flat file '
                                      '(located in the data folder)'))

# Percentile to normalise to when normalising and median filtering
#    image [percentage]
BADPIX_NORM_PERCENTILE = Const('BADPIX_NORM_PERCENTILE', value=None,
                               dtype=float, source=__NAME__,
                               minimum=0.0, maximum=100.0, group=cgroup, 
                               description=('Percentile to normalise to when '
                                            'normalising and median filtering '
                                            'image [percentage]'))

# Define the median image in the x dimension over a boxcar of this width
BADPIX_FLAT_MED_WID = Const('BADPIX_FLAT_MED_WID', value=None, dtype=int,
                            source=__NAME__, minimum=0, group=cgroup, 
                            description=('Define the median image in the x '
                                         'dimension over a boxcar of this '
                                         'width'))

# Define the maximum differential pixel cut ratio
BADPIX_FLAT_CUT_RATIO = Const('BADPIX_FLAT_CUT_RATIO', value=None, dtype=float,
                              source=__NAME__, minimum=0.0, group=cgroup, 
                              description=('Define the maximum differential '
                                           'pixel cut ratio'))

# Define the illumination cut parameter
BADPIX_ILLUM_CUT = Const('BADPIX_ILLUM_CUT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0, group=cgroup,
                         description='Define the illumination cut parameter')

# Define the maximum flux in ADU/s to be considered too hot to be used
BADPIX_MAX_HOTPIX = Const('BADPIX_MAX_HOTPIX', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Define the maximum flux in ADU/s to '
                                       'be considered too hot to be used'))

# Defines the threshold on the full detector flat file to deem pixels as good
BADPIX_FULL_THRESHOLD = Const('BADPIX_FULL_THRESHOLD', value=None, dtype=float,
                              source=__NAME__, minimum=0.0, group=cgroup, 
                              description=('Defines the threshold on the full '
                                           'detector flat file to deem pixels '
                                           'as good'))

# =============================================================================
# CALIBRATION: BACKGROUND CORRECTION SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: BACKGROUND CORRECTION SETTINGS'
#  Width of the box to produce the background mask
BKGR_BOXSIZE = Const('BKGR_BOXSIZE', value=None, dtype=int,
                     source=__NAME__, minimum=0, group=cgroup, 
                     description=('Width of the box to produce the background '
                                  'mask'))

#  Do background percentile to compute minimum value (%)
BKGR_PERCENTAGE = Const('BKGR_PERCENTAGE', value=None, dtype=float,
                        source=__NAME__, minimum=0.0, maximum=100.0,
                        group=cgroup, 
                        description=('Do background percentile to compute '
                                     'minimum value (%)'))

#  Size in pixels of the convolve tophat for the background mask
BKGR_MASK_CONVOLVE_SIZE = Const('BKGR_MASK_CONVOLVE_SIZE', value=None,
                                dtype=int, source=__NAME__, minimum=0,
                                group=cgroup, 
                                description=('Size in pixels of the convolve '
                                             'tophat for the background mask'))

#  If a pixel has this or more "dark" neighbours, we consider it dark
#      regardless of its initial value
BKGR_N_BAD_NEIGHBOURS = Const('BKGR_N_BAD_NEIGHBOURS', value=None, dtype=int,
                              source=__NAME__, minimum=0, group=cgroup, 
                              description=('If a pixel has this or more "dark" '
                                           'neighbours, we consider it dark '
                                           'regardless of its initial value'))

#  Do not correct for background measurement (True or False)
BKGR_NO_SUBTRACTION = Const('BKGR_NO_SUBTRACTION', value=None, dtype=bool,
                            source=__NAME__, group=cgroup, 
                            description=('Do not correct for background '
                                         'measurement (True or False)'))

#  Kernel amplitude determined from drs_local_scatter.py
BKGR_KER_AMP = Const('BKGR_KER_AMP', value=None, dtype=float, source=__NAME__,
                     group=cgroup, 
                     description=('Kernel amplitude determined from '
                                  'drs_local_scatter.py'))

#  Background kernel width in in x and y [pixels]
BKGR_KER_WX = Const('BKGR_KER_WX', value=None, dtype=int, source=__NAME__,
                    group=cgroup, 
                    description=('Background kernel width in in x and '
                                 'y [pixels]'))
BKGR_KER_WY = Const('BKGR_KER_WY', value=None, dtype=int, source=__NAME__,
                    group=cgroup, description='')

#  construct a convolution kernel. We go from -IC_BKGR_KER_SIG to
#      +IC_BKGR_KER_SIG sigma in each direction. Its important no to
#      make the kernel too big as this slows-down the 2D convolution.
#      Do NOT make it a -10 to +10 sigma gaussian!
BKGR_KER_SIG = Const('BKGR_KER_SIG', value=None, dtype=float, source=__NAME__,
                     group=cgroup, 
                     description=('construct a convolution kernel. We go from '
                                  '-IC_BKGR_KER_SIG to +IC_BKGR_KER_SIG sigma '
                                  'in each direction. Its important no to make '
                                  'the kernel too big as this slows-down the '
                                  '2D convolution. Do NOT make it a -10 to +10 '
                                  'sigma gaussian!'))

# =============================================================================
# CALIBRATION: LOCALISATION SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: LOCALISATION SETTINGS'
# Size of the order_profile smoothed box
#   (from pixel - size to pixel + size)
LOC_ORDERP_BOX_SIZE = Const('LOC_ORDERP_BOX_SIZE', value=None, dtype=int,
                            source=__NAME__, group=cgroup, 
                            description=('Size of the order_profile smoothed '
                                         'box (from pixel - size to pixel '
                                         '+ size)'))

# row number of image to start localisation processing at
LOC_START_ROW_OFFSET = Const('LOC_START_ROW_OFFSET', value=None, dtype=int,
                             source=__NAME__, minimum=0, group=cgroup, 
                             description=('row number of image to start '
                                          'localisation processing at'))

# Definition of the central column for use in localisation
LOC_CENTRAL_COLUMN = Const('LOC_CENTRAL_COLUMN', value=None, dtype=int,
                           source=__NAME__, minimum=0, group=cgroup, 
                           description=('Definition of the central column '
                                        'for use in localisation'))

# Half spacing between orders
LOC_HALF_ORDER_SPACING = Const('LOC_HALF_ORDER_SPACING', value=None,
                               dtype=int, source=__NAME__, minimum=0,
                               group=cgroup,
                               description='Half spacing between orders')

# Minimum amplitude to accept (in e-)
LOC_MINPEAK_AMPLITUDE = Const('LOC_MINPEAK_AMPLITUDE', value=None, dtype=float,
                              source=__NAME__, minimum=0.0, group=cgroup, 
                              description=('Minimum amplitude to accept '
                                           '(in e-)'))

# Normalised amplitude threshold to accept pixels for background calculation
LOC_BKGRD_THRESHOLD = Const('LOC_BKGRD_THRESHOLD', value=None, dtype=float,
                            source=__NAME__, minimum=0.0, group=cgroup, 
                            description=('Normalised amplitude threshold to '
                                         'accept pixels for background '
                                         'calculation'))

# Define the amount we drop from the centre of the order when
#    previous order center is missed (in finding the position)
LOC_ORDER_CURVE_DROP = Const('LOC_ORDER_CURVE_DROP', value=None, dtype=float,
                             source=__NAME__, minimum=0.0, group=cgroup, 
                             description=('Define the amount we drop from the '
                                          'centre of the order when previous '
                                          'order center is missed (in finding '
                                          'the position)'))

# set the sigma clipping cut off value for cleaning coefficients
LOC_COEFF_SIGCLIP = Const('LOC_COEFF_SIGCLIP', value=None, dtype=float,
                          source=__NAME__, minimum=0, group=cgroup, 
                          description=('set the sigma clipping cut off value '
                                       'for cleaning coefficients'))

#  Defines the fit degree to fit in the coefficient cleaning
LOC_COEFFSIG_DEG = Const('LOC_COEFFSIG_DEG', value=None, dtype=int,
                         source=__NAME__, minimum=1, group=cgroup, 
                         description=('Defines the fit degree to fit in the '
                                      'coefficient cleaning'))

#  Define the maximum value allowed in the localisation (cuts bluest orders)
LOC_MAX_YPIX_VALUE = Const('LOC_MAX_YPIX_VALUE', value=None, dtype=int,
                           source=__NAME__, minimum=0, group=cgroup,
                           description='Define the maximum value allowed in '
                                       'the localisation (cuts bluest orders)')

# Order of polynomial to fit for widths
LOC_WIDTH_POLY_DEG = Const('LOC_WIDTH_POLY_DEG', value=None, dtype=int,
                           source=__NAME__, minimum=1, group=cgroup, 
                           description=('Order of polynomial to fit for '
                                        'widths'))

# Order of polynomial to fit for positions
LOC_CENT_POLY_DEG = Const('LOC_CENT_POLY_DEG', value=None, dtype=int,
                          source=__NAME__, minimum=1, group=cgroup, 
                          description=('Order of polynomial to fit for '
                                       'positions'))

#   Define the jump size when finding the order position
#       (jumps in steps of this from the center outwards)
LOC_COLUMN_SEP_FITTING = Const('LOC_COLUMN_SEP_FITTING', value=None, dtype=int,
                               source=__NAME__, minimum=1, group=cgroup, 
                               description=('Define the jump size when finding '
                                            'the order position (jumps in '
                                            'steps of this from the center '
                                            'outwards)'))

# Definition of the extraction window size (half size)
LOC_EXT_WINDOW_SIZE = Const('LOC_EXT_WINDOW_SIZE', value=None, dtype=int,
                            source=__NAME__, minimum=1, group=cgroup, 
                            description=('Definition of the extraction window '
                                         'size (half size)'))

# Definition of the gap index in the selected area
LOC_IMAGE_GAP = Const('LOC_IMAGE_GAP', value=None, dtype=int, source=__NAME__,
                      minimum=0, group=cgroup, 
                      description=('Definition of the gap index in the '
                                   'selected area'))

# Define minimum width of order to be accepted
LOC_ORDER_WIDTH_MIN = Const('LOC_ORDER_WIDTH_MIN', value=None, dtype=float,
                            source=__NAME__, minimum=0.0, group=cgroup, 
                            description=('Define minimum width of order to be '
                                         'accepted'))

# Define the noise multiplier threshold in order to accept an
#     order center as usable i.e.
#     max(pixel value) - min(pixel value) > THRES * RDNOISE
LOC_NOISE_MULTIPLIER_THRES = Const('LOC_NOISE_MULTIPLIER_THRES', value=None,
                                   dtype=float, source=__NAME__, minimum=0.0,
                                   group=cgroup, 
                                   description=('Define the noise multiplier '
                                                'threshold in order to accept '
                                                'an order center as usable '
                                                'i.e. max(pixel value) - '
                                                'min(pixel value) > '
                                                'THRES * RDNOISE'))

# Maximum rms for sigma-clip order fit (center positions)
LOC_MAX_RMS_CENT = Const('LOC_MAX_RMS_CENT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0, group=cgroup, 
                         description=('Maximum rms for sigma-clip order fit '
                                      '(center positions)'))

# Maximum peak-to-peak for sigma-clip order fit (center positions)
LOC_MAX_PTP_CENT = Const('LOC_MAX_PTP_CENT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0, group=cgroup, 
                         description=('Maximum peak-to-peak for sigma-clip '
                                      'order fit (center positions)'))

# Maximum frac ptp/rms for sigma-clip order fit (center positions)
LOC_PTPORMS_CENT = Const('LOC_PTPORMS_CENT', value=None, dtype=float,
                         source=__NAME__, minimum=0.0, group=cgroup, 
                         description=('Maximum frac ptp/rms for sigma-clip '
                                      'order fit (center positions)'))

# Maximum rms for sigma-clip order fit (width)
LOC_MAX_RMS_WID = Const('LOC_MAX_RMS_WID', value=None, dtype=float,
                        source=__NAME__, minimum=0.0, group=cgroup, 
                        description=('Maximum rms for sigma-clip order fit '
                                     '(width)'))

# Maximum fractional peak-to-peak for sigma-clip order fit (width)
LOC_MAX_PTP_WID = Const('LOC_MAX_PTP_WID', value=None, dtype=float,
                        source=__NAME__, minimum=0.0, group=cgroup, 
                        description=('Maximum fractional peak-to-peak for '
                                     'sigma-clip order fit (width)'))

# Saturation threshold for localisation
LOC_SAT_THRES = Const('LOC_SAT_THRES', value=None, dtype=float, source=__NAME__,
                      minimum=0.0, group=cgroup,
                      description='Saturation threshold for localisation')

# Maximum points removed in location fit
QC_LOC_MAXFIT_REMOVED_CTR = Const('QC_LOC_MAXFIT_REMOVED_CTR', value=None,
                                  dtype=int, source=__NAME__, minimum=0,
                                  group=cgroup, 
                                  description=('Maximum points removed in '
                                               'location fit'))

# Maximum points removed in width fit
QC_LOC_MAXFIT_REMOVED_WID = Const('QC_LOC_MAXFIT_REMOVED_WID', value=None,
                                  dtype=int, source=__NAME__, minimum=0,
                                  group=cgroup, 
                                  description=('Maximum points removed '
                                               'in width fit'))

# Maximum rms allowed in fitting location
QC_LOC_RMSMAX_CTR = Const('QC_LOC_RMSMAX_CTR', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Maximum rms allowed in fitting '
                                       'location'))

# Maximum rms allowed in fitting width
QC_LOC_RMSMAX_WID = Const('QC_LOC_RMSMAX_WID', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Maximum rms allowed in fitting '
                                       'width'))

# Option for archiving the location image
LOC_SAVE_SUPERIMP_FILE = Const('LOC_SAVE_SUPERIMP_FILE', value=None,
                               dtype=bool, source=__NAME__, group=cgroup, 
                               description=('Option for archiving the '
                                            'location image'))

# set the zoom in levels for the plots (xmin values)
LOC_PLOT_CORNER_XZOOM1 = Const('LOC_PLOT_CORNER_XZOOM1', value=None,
                               dtype=str, source=__NAME__, group=cgroup, 
                               description=('set the zoom in levels for '
                                            'the plots (xmin values)'))

# set the zoom in levels for the plots (xmax values)
LOC_PLOT_CORNER_XZOOM2 = Const('LOC_PLOT_CORNER_XZOOM2', value=None,
                               dtype=str, source=__NAME__, group=cgroup, 
                               description=('set the zoom in levels for the '
                                            'plots (xmax values)'))

# set the zoom in levels for the plots (ymin values)
LOC_PLOT_CORNER_YZOOM1 = Const('LOC_PLOT_CORNER_YZOOM1', value=None,
                               dtype=str, source=__NAME__, group=cgroup, 
                               description=('set the zoom in levels for the '
                                            'plots (ymin values)'))

# set the zoom in levels for the plots (ymax values)
LOC_PLOT_CORNER_YZOOM2 = Const('LOC_PLOT_CORNER_YZOOM2', value=None,
                               dtype=str, source=__NAME__, group=cgroup, 
                               description=('set the zoom in levels for the '
                                            'plots (ymax values)'))

# =============================================================================
# CALIBRATION: SHAPE SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: SHAPE SETTINGS'
#  Define the allowed DPRTYPES for finding files for SHAPE_MASTER will
#      only find those types define by 'filetype' but 'filetype' must
#      be one of theses (strings separated by commas)
ALLOWED_FP_TYPES = Const('ALLOWED_FP_TYPES', value=None, dtype=str,
                         source=__NAME__, group=cgroup, 
                         description=('Define the allowed DPRTYPES for finding '
                                      'files for SHAPE_MASTER will only find '
                                      'those types define by filetype but '
                                      'filetype must be one of theses '
                                      '(strings separated by commas)'))

# Define the maximum time span to combine fp files over (in hours)
FP_MASTER_MATCH_TIME = Const('FP_MASTER_MATCH_TIME', value=None,
                             dtype=float, source=__NAME__, group=cgroup, 
                             description=('Define the maximum time span to '
                                          'combine fp files over (in hours)'))

# Define the percentile at which the FPs are normalised when getting the
#    fp master in shape master
FP_MASTER_PERCENT_THRES = Const('FP_MASTER_PERCENT_THRES', value=None,
                                dtype=float, minimum=0, maximum=100,
                                source=__NAME__, group=cgroup, 
                                description=('Define the percentile at which '
                                             'the FPs are normalised when '
                                             'getting the fp master in shape '
                                             'master'))

#  Define the largest standard deviation allowed for the shift in
#   x or y when doing the shape master fp linear transform
SHAPE_QC_LTRANS_RES_THRES = Const('SHAPE_QC_LTRANS_RES_THRES', value=None,
                                  dtype=float, source=__NAME__, group=cgroup, 
                                  description=('Define the largest standard '
                                               'deviation allowed for the '
                                               'shift in x or y when doing the '
                                               'shape master fp linear '
                                               'transform'))

#  Define the percentile which defines a true FP peak [0-100]
SHAPE_MASTER_VALIDFP_PERCENTILE = Const('SHAPE_MASTER_VALIDFP_PERCENTILE',
                                        value=None, dtype=float, minimum=0,
                                        maximum=100, source=__NAME__,
                                        group=cgroup, 
                                        description=('Define the percentile '
                                                     'which defines a true FP '
                                                     'peak [0-100]'))

#  Define the fractional flux an FP much have compared to its neighbours
SHAPE_MASTER_VALIDFP_THRESHOLD = Const('SHAPE_MASTER_VALIDFP_THRESHOLD',
                                       value=None, dtype=float, minimum=0,
                                       source=__NAME__, group=cgroup, 
                                       description=('Define the fractional '
                                                    'flux an FP much have '
                                                    'compared to its '
                                                    'neighbours'))

#  Define the number of iterations used to get the linear transform params
SHAPE_MASTER_LINTRANS_NITER = Const('SHAPE_MASTER_LINTRANS_NITER', value=None,
                                    dtype=int, minimum=1, source=__NAME__,
                                    group=cgroup, 
                                    description=('Define the number of '
                                                 'iterations used to get the '
                                                 'linear transform params'))

#  Define the initial search box size (in pixels) around the fp peaks
SHAPE_MASTER_FP_INI_BOXSIZE = Const('SHAPE_MASTER_FP_INI_BOXSIZE', value=None,
                                    dtype=int, minimum=1, source=__NAME__,
                                    group=cgroup, 
                                    description=('Define the initial search '
                                                 'box size (in pixels) around '
                                                 'the fp peaks'))

#  Define the small search box size (in pixels) around the fp peaks
SHAPE_MASTER_FP_SMALL_BOXSIZE = Const('SHAPE_MASTER_FP_SMALL_BOXSIZE',
                                      value=None, dtype=int, minimum=1,
                                      source=__NAME__, group=cgroup, 
                                      description=('Define the small search '
                                                   'box size (in pixels) '
                                                   'around the fp peaks'))

#  Define the minimum number of FP files in a group to mean group is valid
SHAPE_FP_MASTER_MIN_IN_GROUP = Const('SHAPE_FP_MASTER_MIN_IN_GROUP', value=None,
                                     dtype=int, minimum=1, source=__NAME__,
                                     group=cgroup, 
                                     description=('Define the minimum number '
                                                  'of FP files in a group to '
                                                  'mean group is valid'))

#  Define which fiber should be used for fiber-dependent calibrations in
#   shape master
SHAPE_MASTER_FIBER = Const('SHAPE_MASTER_FIBER', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           
                           description=('Define which fiber should be used '
                                        'for fiber-dependent calibrations '
                                        'in shape master'))

#  Define the shape master dx rms quality control criteria (per order)
SHAPE_MASTER_DX_RMS_QC = Const('SHAPE_MASTER_FIBER', value=None, dtype=float,
                               source=__NAME__, group=cgroup,
                               description='Define the shape master dx rms'
                                           'quality control criteria (per '
                                           'order)')

# The number of iterations to run the shape finding out to
SHAPE_NUM_ITERATIONS = Const('SHAPE_NUM_ITERATIONS', value=None, dtype=int,
                             minimum=1, source=__NAME__, group=cgroup, 
                             description=('The number of iterations to run '
                                          'the shape finding out to'))

# The order to use on the shape plot
SHAPE_PLOT_SELECTED_ORDER = Const('SHAPE_PLOT_SELECTED_ORDER', value=None,
                                  dtype=int, minimum=0, source=__NAME__,
                                  group=cgroup, 
                                  description=('The order to use on the '
                                               'shape plot'))

# width of the ABC fibers (in pixels)
SHAPE_ORDER_WIDTH = Const('SHAPE_ORDER_WIDTH', value=None, dtype=int,
                          minimum=1, source=__NAME__, group=cgroup,
                          description='width of the ABC fibers (in pixels)')

# number of sections per order to split the order into
SHAPE_NSECTIONS = Const('SHAPE_NSECTIONS', value=None, dtype=int,
                        minimum=1, source=__NAME__, group=cgroup, 
                        description=('number of sections per order to split '
                                     'the order into'))

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
SHAPE_LARGE_ANGLE_MIN = Const('SHAPE_LARGE_ANGLE_MIN', value=None,
                              dtype=float, source=__NAME__, group=cgroup, 
                              description=('the range of angles (in degrees) '
                                           'for the first iteration (large) '
                                           'and subsequent iterations (small)'))

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
SHAPE_LARGE_ANGLE_MAX = Const('SHAPE_LARGE_ANGLE_MAX', value=None,
                              dtype=float, source=__NAME__, group=cgroup,
                              description=('the range of angles (in degrees) '
                                           'for the first iteration (large) '
                                           'and subsequent iterations (small)'))

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
SHAPE_SMALL_ANGLE_MIN = Const('SHAPE_SMALL_ANGLE_MIN', value=None,
                              dtype=float, source=__NAME__, group=cgroup,
                              description=('the range of angles (in degrees) '
                                           'for the first iteration (large) '
                                           'and subsequent iterations (small)'))

# the range of angles (in degrees) for the first iteration (large)
# and subsequent iterations (small)
SHAPE_SMALL_ANGLE_MAX = Const('SHAPE_SMALL_ANGLE_MAX', value=None,
                              dtype=float, source=__NAME__, group=cgroup, 
                              description=('the range of angles (in degrees) '
                                           'for the first iteration (large) '
                                           'and subsequent iterations (small)'))

# max sigma clip (in sigma) on points within a section
SHAPE_SIGMACLIP_MAX = Const('SHAPE_SIGMACLIP_MAX', value=None, dtype=float,
                            minimum=0.0, source=__NAME__, group=cgroup, 
                            description=('max sigma clip (in sigma) on points '
                                         'within a section'))

# the size of the median filter to apply along the order (in pixels)
SHAPE_MEDIAN_FILTER_SIZE = Const('SHAPE_MEDIAN_FILTER_SIZE', value=None,
                                 dtype=int, minimum=0, source=__NAME__,
                                 group=cgroup, 
                                 description=('the size of the median filter '
                                              'to apply along the order '
                                              '(in pixels)'))

# The minimum value for the cross-correlation to be deemed good
SHAPE_MIN_GOOD_CORRELATION = Const('SHAPE_MIN_GOOD_CORRELATION', value=None,
                                   dtype=float, minimum=0.0, source=__NAME__,
                                   group=cgroup, 
                                   description=('The minimum value for the '
                                                'cross-correlation to be '
                                                'deemed good'))

# Define the first pass (short) median filter width for dx
SHAPE_SHORT_DX_MEDFILT_WID = Const('SHAPE_SHORT_DX_MEDFILT_WID', value=None,
                                   dtype=int, source=__NAME__, group=cgroup,
                                   description=('Define the first pass (short) '
                                                'median filter width for dx'))

# Define the second pass (long) median filter width for dx.
#  Used to fill NaN positions in dx that are not covered by short pass
SHAPE_LONG_DX_MEDFILT_WID = Const('SHAPE_SHORT_DX_MEDFILT_WID', value=None,
                                  dtype=int, source=__NAME__, group=cgroup)

#  Defines the largest allowed standard deviation for a given
#  per-order and per-x-pixel shift of the FP peaks
SHAPE_QC_DXMAP_STD = Const('SHAPE_QC_DXMAP_STD', value=None, dtype=int,
                           source=__NAME__, group=cgroup, 
                           description=('Defines the largest allowed standard '
                                        'deviation for a given per-order and '
                                        'per-x-pixel shift of the FP peaks'))

# defines the shape offset xoffset (before and after) fp peaks
SHAPEOFFSET_XOFFSET = Const('SHAPEOFFSET_XOFFSET', value=None, dtype=int,
                            source=__NAME__, group=cgroup, 
                            description=('defines the shape offset xoffset '
                                         '(before and after) fp peaks'))

# defines the bottom percentile for fp peak
SHAPEOFFSET_BOTTOM_PERCENTILE = Const('SHAPEOFFSET_BOTTOM_PERCENTILE',
                                      value=None, dtype=float, source=__NAME__,
                                      group=cgroup, 
                                      description=('defines the bottom '
                                                   'percentile for fp peak'))

# defines the top percentile for fp peak
SHAPEOFFSET_TOP_PERCENTILE = Const('SHAPEOFFSET_TOP_PERCENTILE', value=None,
                                   dtype=float, source=__NAME__, group=cgroup, 
                                   description=('defines the top percentile '
                                                'for fp peak'))

# defines the floor below which top values should be set to
# this fraction away from the max top value
SHAPEOFFSET_TOP_FLOOR_FRAC = Const('SHAPEOFFSET_TOP_FLOOR_FRAC', value=None,
                                   dtype=float, source=__NAME__, group=cgroup, 
                                   description=('defines the floor below which '
                                                'top values should be set to '
                                                'this fraction away from the '
                                                'max top value'))

# define the median filter to apply to the hc (high pass filter)]
SHAPEOFFSET_MED_FILTER_WIDTH = Const('SHAPEOFFSET_MED_FILTER_WIDTH',
                                     value=None, dtype=int, source=__NAME__,
                                     group=cgroup, 
                                     description=('define the median filter to '
                                                  'apply to the hc (high pass '
                                                  'filter)]'))

# Maximum number of FP (larger than expected number
#    (~10000 to ~25000)
SHAPEOFFSET_FPINDEX_MAX = Const('SHAPEOFFSET_FPINDEX_MAX', value=None,
                                dtype=int, source=__NAME__,
                                minimum=10000, maximum=25000, group=cgroup, 
                                description=('Maximum number of FP (larger '
                                             'than expected number (~10000 to '
                                             '~25000)'))

# Define the valid length of a FP peak
SHAPEOFFSET_VALID_FP_LENGTH = Const('SHAPEOFFSET_VALID_FP_LENGTH', value=None,
                                    dtype=int, source=__NAME__, group=cgroup, 
                                    description=('Define the valid length of a'
                                                 ' FP peak'))

# Define the maximum allowed offset (in nm) that we allow for
#   the detector)
SHAPEOFFSET_DRIFT_MARGIN = Const('SHAPEOFFSET_DRIFT_MARGIN', value=None,
                                 dtype=float, source=__NAME__, group=cgroup, 
                                 description=('Define the maximum allowed '
                                              'offset (in nm) that we allow '
                                              'for the detector)'))

# Define the number of iterations to do for the wave_fp
#   inversion trick
SHAPEOFFSET_WAVEFP_INV_IT = Const('SHAPEOFFSET_WAVEFP_INV_IT',
                                  value=None, dtype=int, source=__NAME__,
                                  group=cgroup, 
                                  description=('Define the number of '
                                               'iterations to do for the '
                                               'wave_fp inversion trick'))

# Define the border in pixels at the edge of the detector
SHAPEOFFSET_MASK_BORDER = Const('SHAPEOFFSET_MASK_BORDER', value=None,
                                dtype=int, source=__NAME__, group=cgroup, 
                                description=('Define the border in pixels at '
                                             'the edge of the detector'))

# Define the minimum maxpeak value as a fraction of the
#  maximum maxpeak
SHAPEOFFSET_MIN_MAXPEAK_FRAC = Const('SHAPEOFFSET_MIN_MAXPEAK_FRAC', value=None,
                                     dtype=float, source=__NAME__, group=cgroup, 
                                     description=('Define the minimum maxpeak '
                                                  'value as a fraction of the '
                                                  'maximum maxpeak'))

# Define the width of the FP mask (+/- the center)
SHAPEOFFSET_MASK_PIXWIDTH = Const('SHAPEOFFSET_MASK_PIXWIDTH', value=None,
                                  dtype=int, source=__NAME__, group=cgroup, 
                                  description=('Define the width of the FP '
                                               'mask (+/- the center)'))

# Define the width of the FP to extract (+/- the center)
SHAPEOFFSET_MASK_EXTWIDTH = Const('SHAPEOFFSET_MASK_EXTWIDTH', value=None,
                                  dtype=int, source=__NAME__, group=cgroup, 
                                  description=('Define the width of the FP to '
                                               'extract (+/- the center)'))

# Define the most deviant peaks - percentile from [min to max]
SHAPEOFFSET_DEVIANT_PMIN = Const('SHAPEOFFSET_DEVIANT_PMIN', value=None,
                                 dtype=float, minimum=0, maximum=100,
                                 source=__NAME__, group=cgroup, 
                                 description=('Define the most deviant peaks - '
                                              'percentile from [min to max]'))
SHAPEOFFSET_DEVIANT_PMAX = Const('SHAPEOFFSET_DEVIANT_PMAX', value=None,
                                 dtype=float, minimum=0, maximum=100,
                                 source=__NAME__, group=cgroup,
                                 description='')

# Define the maximum error in FP order assignment
#  we assume that the error in FP order assignment could range
#  from -50 to +50 in practice, it is -1, 0 or +1 for the cases we've
#  tested to date
SHAPEOFFSET_FPMAX_NUM_ERROR = Const('SHAPEOFFSET_FPMAX_NUM_ERROR', value=None,
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
SHAPEOFFSET_FIT_HC_SIGMA = Const('SHAPEOFFSET_FIT_HC_SIGMA', value=None,
                                 dtype=float, source=__NAME__, group=cgroup, 
                                 description=('The number of sigmas that the '
                                              'HC spectrum is allowed to be '
                                              'away from the predicted (from '
                                              'FP) position'))

# Define the maximum allowed maximum absolute deviation away
#   from the error fit
SHAPEOFFSET_MAXDEV_THRESHOLD = Const('SHAPEOFFSET_MAXDEV_THRESHOLD', value=None,
                                     dtype=float, source=__NAME__, group=cgroup, 
                                     description=('Define the maximum allowed '
                                                  'maximum absolute deviation '
                                                  'away from the error fit'))

# very low thresholding values tend to clip valid points
SHAPEOFFSET_ABSDEV_THRESHOLD = Const('SHAPEOFFSET_ABSDEV_THRESHOLD', value=None,
                                     dtype=float, source=__NAME__, group=cgroup, 
                                     description=('very low thresholding '
                                                  'values tend to clip valid '
                                                  'points'))

# define the names of the unique fibers (i.e. not AB) for use in
#   getting the localisation coefficients for dymap
SHAPE_UNIQUE_FIBERS = Const('SHAPE_UNIQUE_FIBERS', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('define the names of the unique '
                                         'fibers (i.e. not AB) for use in '
                                         'getting the localisation '
                                         'coefficients for dymap'))

#  Define first zoom plot for shape local zoom debug plot
#     should be a string list (xmin, xmax, ymin, ymax)
SHAPEL_PLOT_ZOOM1 = Const('SHAPEL_PLOT_ZOOM1', value=None, dtype=str,
                          source=__NAME__, group=cgroup, 
                          description=('Define first zoom plot for shape local '
                                       'zoom debug plot should be a string '
                                       'list (xmin, xmax, ymin, ymax)'))

#  Define second zoom plot for shape local zoom debug plot
#     should be a string list (xmin, xmax, ymin, ymax)
SHAPEL_PLOT_ZOOM2 = Const('SHAPEL_PLOT_ZOOM2', value=None, dtype=str,
                          source=__NAME__, group=cgroup, 
                          description=('Define second zoom plot for shape '
                                       'local zoom debug plot should be a '
                                       'string list (xmin, xmax, ymin, ymax)'))

# =============================================================================
# CALIBRATION: FLAT SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: FLAT SETTINGS'
# TODO: is blaze_size needed with sinc function?
# Half size blaze smoothing window
FF_BLAZE_HALF_WINDOW = Const('FF_BLAZE_HALF_WINDOW', value=None, dtype=int,
                             source=__NAME__, group=cgroup, 
                             description='Half size blaze smoothing window')

# TODO: is blaze_cut needed with sinc function?
# Minimum relative e2ds flux for the blaze computation
FF_BLAZE_THRESHOLD = Const('FF_BLAZE_THRESHOLD', value=None, dtype=float,
                           source=__NAME__, group=cgroup, 
                           description=('Minimum relative e2ds flux for the '
                                        'blaze computation'))

# TODO: is blaze_deg needed with sinc function?
# The blaze polynomial fit degree
FF_BLAZE_DEGREE = Const('FF_BLAZE_DEGREE', value=None, dtype=int,
                        source=__NAME__, group=cgroup,
                        description='The blaze polynomial fit degree')

# Define the threshold, expressed as the fraction of the maximum peak, below
#    this threshold the blaze (and e2ds) is set to NaN
FF_BLAZE_SCUT = Const('FF_BLAZE_SCUT', value=None, dtype=float,
                      source=__NAME__, group=cgroup, 
                      description=('Define the threshold, expressed as the '
                                   'fraction of the maximum peak, below this '
                                   'threshold the blaze (and e2ds) is set to '
                                   'NaN'))

# Define the rejection threshold for the blaze sinc fit
FF_BLAZE_SIGFIT = Const('FF_BLAZE_SIGFIT', value=None, dtype=float,
                        source=__NAME__, group=cgroup, 
                        description=('Define the rejection threshold for the '
                                     'blaze sinc fit'))

# Define the hot bad pixel percentile level (using in blaze sinc fit)
FF_BLAZE_BPERCENTILE = Const('FF_BLAZE_BPERCENTILE', value=None, dtype=float,
                             source=__NAME__, group=cgroup,
                             description=('Define the hot bad pixel percentile '
                                          'level (using in blaze sinc fit)'))

# Define the number of times to iterate around blaze sinc fit
FF_BLAZE_NITER = Const('FF_BLAZE_BPERCENTILE', value=None, dtype=int,
                       source=__NAME__, minimum=0, group=cgroup)

# Define the orders not to plot on the RMS plot should be a string
#     containing a list of integers
FF_RMS_SKIP_ORDERS = Const('FF_RMS_SKIP_ORDERS', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           description=('Define the orders not to plot on the '
                                        'RMS plot should be a string '
                                        'containing a list of integers'))

# Maximum allowed RMS of flat field
QC_FF_MAX_RMS = Const('QC_FF_MAX_RMS', value=None, dtype=float, source=__NAME__,
                      group=cgroup,
                      description='Maximum allowed RMS of flat field')

# Define the order to plot in summary plots
FF_PLOT_ORDER = Const('FF_PLOT_ORDER', value=None, dtype=int, source=__NAME__,
                      group=cgroup,
                      description='Define the order to plot in summary plots')

# =============================================================================
# CALIBRATION: LEAKAGE SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: LEAKAGE SETTINGS'
# Define the types of input file allowed by the leakage master recipe
ALLOWED_LEAKM_TYPES = Const('ALLOWED_LEAKM_TYPES', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('Define the types of input file '
                                         'allowed by the leakage master '
                                         'recipe'))

# define whether to always extract leak master files
#      (i.e. overwrite existing files)
LEAKM_ALWAYS_EXTRACT = Const('LEAKM_ALWAYS_EXTRACT', value=None, dtype=bool,
                             source=__NAME__, group=cgroup, 
                             description=('define whether to always extract '
                                          'leak master files (i.e. overwrite '
                                          'existing files)'))

# define the type of file to use for leak master solution
#    (currently allowed are 'E2DSFF') - must match with LEAK_EXTRACT_FILE
LEAKM_EXTRACT_TYPE = Const('LEAKM_EXTRACT_TYPE', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           description=('define the type of file to use for '
                                        'leak master solution (currently '
                                        'allowed are E2DSFF) - must match with '
                                        'LEAK_EXTRACT_FILE'))

# Define the types of input extracted files to correct for leakage
ALLOWED_LEAK_TYPES = Const('ALLOWED_LEAK_TYPES', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           description=('Define the types of input extracted '
                                        'files to correct for leakage'))

# define the type of file to use for the leak correction (currently allowed are
#     'E2DS_FILE' or 'E2DSFF_FILE' (linked to recipe definition outputs)
#     must match with LEAKM_EXTRACT_TYPE
LEAK_EXTRACT_FILE = Const('LEAK_EXTRACT_FILE', value=None, dtype=str,
                          source=__NAME__, group=cgroup, 
                          description=('define the type of file to use for the '
                                       'leak correction (currently allowed are '
                                       'E2DS_FILE or E2DSFF_FILE (linked to '
                                       'recipe definition outputs) must match '
                                       'with LEAKM_EXTRACT_TYPE'))

# define the extraction files which are 2D images (i.e. order num x nbpix)
LEAK_2D_EXTRACT_FILES = Const('LEAK_2D_EXTRACT_FILES', value=None, dtype=str,
                              source=__NAME__, group=cgroup, 
                              description=('define the extraction files which '
                                           'are 2D images (i.e. order num x '
                                           'nbpix)'))

# define the extraction files which are 1D spectra
LEAK_1D_EXTRACT_FILES = Const('LEAK_1D_EXTRACT_FILES', value=None, dtype=str,
                              source=__NAME__, group=cgroup, 
                              description=('define the extraction files which '
                                           'are 1D spectra'))

# define the thermal background percentile for the leak and leak master
LEAK_BCKGRD_PERCENTILE = Const('LEAK_BCKGRD_PERCENTILE', value=None, dtype=float,
                               source=__NAME__, group=cgroup, 
                               description=('define the thermal background '
                                            'percentile for the leak and '
                                            'leak master'))

# define the normalisation percentile for the leak and leak master
LEAK_NORM_PERCENTILE = Const('LEAK_NORM_PERCENTILE', value=None, dtype=float,
                             source=__NAME__, group=cgroup, 
                             description=('define the normalisation percentile '
                                          'for the leak and leak master'))

# define the e-width of the smoothing kernel for leak master
LEAKM_WSMOOTH = Const('LEAKM_WSMOOTH', value=None, dtype=int,
                      source=__NAME__, minimum=0, group=cgroup, 
                      description=('define the e-width of the smoothing kernel '
                                   'for leak master'))

# define the kernel size for leak master
LEAKM_KERSIZE = Const('LEAKM_KERSIZE', value=None, dtype=float,
                      source=__NAME__, minimum=0.0, group=cgroup,
                      description='define the kernel size for leak master')

# define the lower bound percentile for leak correction
LEAK_LOW_PERCENTILE = Const('LEAK_LOW_PERCENTILE', value=None, dtype=float,
                            source=__NAME__, minimum=0.0, maximum=100.0,
                            group=cgroup,
                            description=('define the lower bound percentile '
                                         'for leak correction'))

# define the upper bound percentile for leak correction
LEAK_HIGH_PERCENTILE = Const('LEAK_LOW_PERCENTILE', value=None, dtype=float,
                             source=__NAME__, minimum=0.0, maximum=100.0,
                             group=cgroup)

# define the limit on surpious FP ratio (1 +/- limit)
LEAK_BAD_RATIO_OFFSET = Const('LEAK_BAD_RATIO_OFFSET', value=None, dtype=float,
                              source=__NAME__, minimum=0.0, group=cgroup, 
                              description=('define the limit on surpious FP '
                                           'ratio (1 +/- limit)'))

# =============================================================================
# CALIBRATION: EXTRACTION SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: EXTRACTION SETTINGS'
#    Whether extraction code is done in quick look mode (do not use for
#       final products)
EXT_QUICK_LOOK = Const('EXT_QUICK_LOOK', value=None, dtype=bool,
                       source=__NAME__, group=cgroup, 
                       description=('Whether extraction code is done in quick '
                                    'look mode (do not use for final '
                                    'products)'))

#  Start order of the extraction in apero_flat if None starts from 0
EXT_START_ORDER = Const('EXT_START_ORDER', value=None, dtype=int,
                        source=__NAME__, group=cgroup, 
                        description=('Start order of the extraction in apero_flat '
                                     'if None starts from 0'))

#  End order of the extraction in apero_flat if None ends at last order
EXT_END_ORDER = Const('EXT_END_ORDER', value=None, dtype=int,
                      source=__NAME__, group=cgroup, 
                      description=('End order of the extraction in apero_flat if '
                                   'None ends at last order'))

# Half-zone extraction width left side (formally plage1)
EXT_RANGE1 = Const('EXT_RANGE1', value=None, dtype=str, source=__NAME__,
                   group=cgroup, 
                   description=('Half-zone extraction width left side '
                                '(formally plage1)'))

# Half-zone extraction width right side (formally plage2)
EXT_RANGE2 = Const('EXT_RANGE2', value=None, dtype=str, source=__NAME__,
                   group=cgroup, 
                   description=('Half-zone extraction width right side '
                                '(formally plage2)'))

# Define the orders to skip extraction on (will set all order values
#    to NaN. If None no orders are skipped. If Not None should be a
#    string (valid python list)
EXT_SKIP_ORDERS = Const('EXT_SKIP_ORDERS', value=None, dtype=str,
                        source=__NAME__, group=cgroup, 
                        description=('Define the orders to skip extraction on '
                                     '(will set all order values to NaN. If '
                                     'None no orders are skipped. If Not None '
                                     'should be a string (valid python list)'))

#  Defines whether to run extraction with cosmic correction
EXT_COSMIC_CORRETION = Const('EXT_COSMIC_CORRETION', value=None, dtype=bool,
                             source=__NAME__, group=cgroup, 
                             description=('Defines whether to run extraction '
                                          'with cosmic correction'))

#  Define the percentage of flux above which we use to cut
EXT_COSMIC_SIGCUT = Const('EXT_COSMIC_SIGCUT', value=None, dtype=float,
                          source=__NAME__, group=cgroup, 
                          description=('Define the number of sigmas away from '
                                       'the median flux which we use to cut '
                                       'cosmic rays'))

#  Defines the maximum number of iterations we use to check for cosmics
#      (for each pixel)
EXT_COSMIC_THRESHOLD = Const('EXT_COSMIC_THRESHOLD', value=None, dtype=int,
                             source=__NAME__, group=cgroup, 
                             description=('Defines the maximum number of '
                                          'iterations we use to check for '
                                          'cosmics (for each pixel)'))

# Saturation level reached warning
QC_EXT_FLUX_MAX = Const('QC_EXT_FLUX_MAX', value=None, dtype=float,
                        source=__NAME__, group=cgroup,
                        description='Saturation level reached warning')

# Define which extraction file to use for s1d creation
EXT_S1D_INTYPE = Const('EXT_S1D_INTYPE', value=None, dtype=str,
                       source=__NAME__, group=cgroup, 
                       description=('Define which extraction file to use for '
                                    's1d creation'))
# Define which extraction file (recipe definitons) linked to EXT_S1D_INTYPE
EXT_S1D_INFILE = Const('EXT_S1D_INFILE', value=None, dtype=str,
                       source=__NAME__, group=cgroup, 
                       description=('Define which extraction file (recipe '
                                    'definitons) linked to EXT_S1D_INTYPE'))

# Define the start s1d wavelength (in nm)
EXT_S1D_WAVESTART = Const('EXT_S1D_WAVESTART', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Define the start s1d wavelength '
                                       '(in nm)'))

# Define the end s1d wavelength (in nm)
EXT_S1D_WAVEEND = Const('EXT_S1D_WAVEEND', value=None, dtype=float,
                        source=__NAME__, minimum=0.0, group=cgroup,
                        description='Define the end s1d wavelength (in nm)')

#  Define the s1d spectral bin for S1D spectra (nm) when uniform in wavelength
EXT_S1D_BIN_UWAVE = Const('EXT_S1D_BIN_UWAVE', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Define the s1d spectral bin for S1D '
                                       'spectra (nm) when uniform in '
                                       'wavelength'))

#  Define the s1d spectral bin for S1D spectra (km/s) when uniform in velocity
EXT_S1D_BIN_UVELO = Const('EXT_S1D_BIN_UVELO', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Define the s1d spectral bin for '
                                       'S1D spectra (km/s) when uniform in '
                                       'velocity'))

#  Define the s1d smoothing kernel for the transition between orders in pixels
EXT_S1D_EDGE_SMOOTH_SIZE = Const('EXT_S1D_EDGE_SMOOTH_SIZE', value=None,
                                 dtype=int, source=__NAME__, minimum=0,
                                 group=cgroup, 
                                 description=('Define the s1d smoothing kernel '
                                              'for the transition between '
                                              'orders in pixels'))

#    Define dprtypes to calculate berv for
EXT_ALLOWED_BERV_DPRTYPES = Const('EXT_ALLOWED_BERV_DPRTYPES', value=None,
                                  dtype=str, source=__NAME__, group=cgroup, 
                                  description=('Define dprtypes to calculate '
                                               'berv for'))

#    Define which BERV calculation to use ('barycorrpy' or 'estimate' or 'None')
EXT_BERV_KIND = Const('EXT_BERV_KIND', value=None, dtype=str, source=__NAME__,
                      options=['barycorrpy', 'estimate', 'None'], group=cgroup, 
                      description=('Define which BERV calculation to use '
                                   '(barycorrpy or estimate or None)'))

#   Define the barycorrpy data directory
EXT_BERV_BARYCORRPY_DIR = Const('EXT_BERV_BARYCORRPY_DIR', value=None,
                                dtype=str, source=__NAME__, group=cgroup, 
                                description=('Define the barycorrpy data '
                                             'directory'))

#   Define the barycorrpy iers file
EXT_BERV_IERSFILE = Const('EXT_BERV_IERSFILE', value=None, dtype=str,
                          source=__NAME__, group=cgroup,
                          description='Define the barycorrpy iers file')

#   Define the barycorrpy iers a url
EXT_BERV_IERS_A_URL = Const('EXT_BERV_IERS_A_URL', value=None, dtype=str,
                            source=__NAME__, group=cgroup,
                            description='Define the barycorrpy iers a url')

#   Define barycorrpy leap directory
EXT_BERV_LEAPDIR = Const('EXT_BERV_LEAPDIR', value=None, dtype=str,
                         source=__NAME__, group=cgroup,
                         description='Define barycorrpy leap directory')

#   Define whether to update leap seconds if older than 6 months
EXT_BERV_LEAPUPDATE = Const('EXT_BERV_LEAPUPDATE', value=None, dtype=bool,
                            source=__NAME__, group=cgroup, 
                            description=('Define whether to update leap '
                                         'seconds if older than 6 months'))

#    Define the accuracy of the estimate (for logging only) [m/s]
EXT_BERV_EST_ACC = Const('EXT_BERV_EST_ACC', value=None, dtype=float,
                         source=__NAME__, group=cgroup, 
                         description=('Define the accuracy of the estimate '
                                      '(for logging only) [m/s]'))

# Define the order to plot in summary plots
EXTRACT_PLOT_ORDER = Const('EXTRACT_PLOT_ORDER', value=None, dtype=int,
                           source=__NAME__, group=cgroup, 
                           description=('Define the order to plot in '
                                        'summary plots'))

# Define the wavelength lower bounds for s1d plots
#     (must be a string list of floats) defines the lower wavelength in nm
EXTRACT_S1D_PLOT_ZOOM1 = Const('EXTRACT_S1D_PLOT_ZOOM1', value=None,
                               dtype=str, source=__NAME__, group=cgroup, 
                               description=('Define the wavelength lower '
                                            'bounds for s1d plots (must be a '
                                            'string list of floats) defines '
                                            'the lower wavelength in nm'))

# Define the wavelength upper bounds for s1d plots
#     (must be a string list of floats) defines the upper wavelength in nm
EXTRACT_S1D_PLOT_ZOOM2 = Const('EXTRACT_S1D_PLOT_ZOOM2', value=None,
                               dtype=str, source=__NAME__, group=cgroup, 
                               description=('Define the wavelength upper '
                                            'bounds for s1d plots (must be a '
                                            'string list of floats) defines '
                                            'the upper wavelength in nm'))

# =============================================================================
# CALIBRATION: THERMAL SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: THERMAL SETTINGS'
# whether to apply the thermal correction to extractions
THERMAL_CORRECT = Const('THERMAL_CORRECT', value=None, dtype=bool,
                        source=__NAME__, user=True, active=False, group=cgroup,
                        description='whether to apply the thermal correction '
                                    'to extractions')

# define whether to always extract thermals (i.e. overwrite existing files)
THERMAL_ALWAYS_EXTRACT = Const('THERMAL_ALWAYS_EXTRACT', value=None,
                               dtype=bool, source=__NAME__,
                               user=True, active=False, group=cgroup,
                               description='define whether to always extract '
                                           'thermals (i.e. overwrite existing '
                                           'files)')

# define the type of file to use for wave solution (currently allowed are
#    'E2DS' or 'E2DSFF')
THERMAL_EXTRACT_TYPE = Const('THERMAL_EXTRACT_TYPE', value=None, dtype=str,
                             source=__NAME__, user=True, active=False,
                             group=cgroup,
                             description='define the type of file to use for '
                                         'wave solution (currently allowed '
                                         'are "E2DS" or "E2DSFF")')

# define DPRTYPEs we need to correct thermal background using
#  telluric absorption (TAPAS)
THERMAL_CORRETION_TYPE1 = Const('THERMAL_CORRETION_TYPE1', value=None,
                                dtype=str, source=__NAME__, group=cgroup, 
                                description=('define DPRTYPEs we need to '
                                             'correct thermal background using '
                                             'telluric absorption (TAPAS)'))

# define DPRTYPEs we need to correct thermal background using
#   method 2
THERMAL_CORRETION_TYPE2 = Const('THERMAL_CORRETION_TYPE2', value=None,
                                dtype=str, source=__NAME__, group=cgroup, 
                                description=('define DPRTYPEs we need to '
                                             'correct thermal background '
                                             'using method 2'))

# define the order to perform the thermal background scaling on
THERMAL_ORDER = Const('THERMAL_ORDER', value=None, dtype=int, source=__NAME__,
                      group=cgroup, 
                      description=('define the order to perform the thermal '
                                   'background scaling on'))

# width of the median filter used for the background
THERMAL_FILTER_WID = Const('THERMAL_FILTER_WID', value=None, dtype=int,
                           source=__NAME__, group=cgroup, 
                           description=('width of the median filter used for '
                                        'the background'))

# define thermal red limit (in nm)
THERMAL_RED_LIMIT = Const('THERMAL_RED_LIMIT', value=None, dtype=float,
                          source=__NAME__, group=cgroup,
                          description='define thermal red limit (in nm)')

# define thermal blue limit (in nm)
THERMAL_BLUE_LIMIT = Const('THERMAL_BLUE_LIMIT', value=None, dtype=float,
                           source=__NAME__, group=cgroup,
                           description='define thermal blue limit (in nm)')

# maximum tapas transmission to be considered completely opaque for the
# purpose of background determination in last order.
THERMAL_THRES_TAPAS = Const('THERMAL_THRES_TAPAS', value=None, dtype=float,
                            source=__NAME__, group=cgroup, 
                            description=('maximum tapas transmission to be '
                                         'considered completely opaque for '
                                         'the purpose of background '
                                         'determination in last order.'))

# define the percentile to measure the background for correction type 2
THERMAL_ENVELOPE_PERCENTILE = Const('THERMAL_ENVELOPE_PERCENTILE', value=None,
                                    dtype=float, source=__NAME__,
                                    minimum=0, maximum=100, group=cgroup, 
                                    description=('define the percentile to '
                                                 'measure the background for '
                                                 'correction type 2'))

# define the order to plot on the thermal debug plot
THERMAL_PLOT_START_ORDER = Const('THERMAL_PLOT_START_ORDER', value=None,
                                 dtype=int, source=__NAME__, group=cgroup, 
                                 description=('define the order to plot on the '
                                              'thermal debug plot'))

# =============================================================================
# CALIBRATION: WAVE EA GENERAL SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: WAVE GENERAL SETTING'

# Define wave master fiber (controller fiber)
WAVE_MASTER_FIBER = Const('WAVE_MASTER_FIBER', value=None, dtype=str,
                          source=__NAME__, group=cgroup,
                          description='Define wave master fiber (controller '
                                      'fiber)')

# Define the initial value of FP effective cavity width 2xd in nm
WAVE_GUESS_CAVITY_WIDTH = Const('WAVE_GUESS_CAVITY_WIDTH', value=None,
                                dtype=float, minimum=0,
                                source=__NAME__, group=cgroup,
                                description='Define the initial value of FP '
                                            'effective cavity width 2xd in nm')

# Define the wave solution polynomial fit degree
WAVE_WAVESOL_FIT_DEGREE = Const('WAVE_WAVESOL_FIT_DEGREE', value=None,
                                dtype=int, source=__NAME__, group=cgroup,
                                minimum=0, maximum=20,
                                description='Define the wave solution '
                                            'polynomial fit degree')

# Define the cavity fit polynomial fit degree for wave solution
#   Note default: 9 for spirou  3 for NIRPS
WAVE_CAVITY_FIT_DEGREE = Const('WAVE_CAVITY_FIT_DEGREE', value=None,
                               dtype=int, source=__NAME__, group=cgroup,
                               minimum=0, maximum=20,
                               description='Define the cavity fit polynomial '
                                           'fit degree for wave solution')

# Define the number of sigmas to use in wave sol robust fits
WAVE_NSIG_CUT = Const('WAVE_NSIG_CUT', value=None, dtype=int, source=__NAME__,
                      group=cgroup, minimum=0, maximum=20,
                      description='Define the number of sigmas to use in wave '
                                  'sol robust fits')

# Define the minimum number of HC lines in an order to try to find
#   absolute numbering
WAVE_MIN_HC_LINES = Const('WAVE_NSIG_CUT', value=None, dtype=int,
                          source=__NAME__, group=cgroup, minimum=1,
                          description='Define the minimum number of HC lines '
                                      'in an order to try to find absolute '
                                      'numbering')

# Define the maximum offset in FP peaks to explore when FP peak counting
WAVE_MAX_FP_COUNT_OFFSET = Const('WAVE_MAX_FP_COUNT_OFFSET', value=None,
                                 dtype=int, source=__NAME__, group=cgroup,
                                 minimum=1,
                                 description='Define the maximum offset in FP '
                                             'peaks to explore when FP peak '
                                             'counting')

# Define the number of iterations required to converge the FP peak counting
#   offset loop
WAVE_FP_COUNT_OFFSET_ITRS = Const('WAVE_FP_COUNT_OFFSET_ITRS', value=None,
                                  dtype=int, source=__NAME__, group=cgroup,
                                  minimum=1,
                                  description='Define the number of iterations '
                                              'required to converge the FP '
                                              'peak counting offset loop')

# Define the number of iterations required to converge on a cavity fit
#  (first time this is done)
WAVE_CAVITY_FIT_ITRS1 = Const('WAVE_CAVITY_FIT_ITRS1', value=None,
                              dtype=int, source=__NAME__, group=cgroup,
                              minimum=1,
                              description='Define the number of iterations '
                                          'required to converge on a cavity '
                                          'fit (first time this is done)')

# Define the number of iterations required to check order offset
WAVE_ORDER_OFFSET_ITRS = Const('WAVE_ORDER_OFFSET_ITRS', value=None,
                               dtype=int, source=__NAME__, group=cgroup,
                               minimum=1,
                               description='Define the number of iterations '
                                           'required to check order offset')

# Define the maximum bulk offset of lines in a order can have
WAVE_MAX_ORDER_BULK_OFFSET = Const('WAVE_MAX_ORDER_BULK_OFFSET', value=None,
                                   dtype=int, source=__NAME__, group=cgroup,
                                   minimum=1,
                                   description='Define the maximum bulk '
                                               'offset of lines in a order '
                                               'can have')

# Define the required precision that the cavity width change must converge
#   to (will be a fraction of the error)
WAVE_CAVITY_CHANGE_ERR_THRES = Const('WAVE_CAVITY_CHANGE_ERR_THRES', value=None,
                                     dtype=float, source=__NAME__, group=cgroup,
                                     minimum=0,
                                     description='Define the required precision'
                                                 ' that the cavity width change'
                                                 ' must converge  to (will be '
                                                 'a fraction of the error)')

# Define the number of iterations required to converge on a cavity fit
#  (second time this is done)
WAVE_CAVITY_FIT_ITRS2 = Const('WAVE_CAVITY_FIT_ITRS2', value=None,
                              dtype=int, source=__NAME__, group=cgroup,
                              minimum=1,
                              description='Define the number of iterations '
                                          'required to converge on a cavity '
                                          'fit (second time this is done)')

# Define the odd ratio that is used in generating the weighted mean
WAVE_HC_VEL_ODD_RATIO = Const('WAVE_HC_VEL_ODD_RATIO', value=None,
                              dtype=float, source=__NAME__, group=cgroup,
                              minimum=0,
                              description='Define the odd ratio that is used '
                                          'in generating the weighted mean')

# Define the number of iterations required to do the final fplines
#   wave solution
WAVE_FWAVESOL_ITRS = Const('WAVE_FWAVESOL_ITRS', value=None,
                           dtype=int, source=__NAME__, group=cgroup,
                           minimum=0,
                           description='Define the number of iterations '
                                       'required to do the final fplines '
                                       'wave solution')

# define the wave fiber comparison plot order number
WAVE_FIBER_COMP_PLOT_ORD = Const('WAVE_FIBER_COMP_PLOT_ORD', value=None,
                                 dtype=int, source=__NAME__, minimum=0,
                                 group=cgroup,
                                 description=('define the wave fiber '
                                              'comparison plot order number'))

# =============================================================================
# CALIBRATION: WAVE LINES REFERENCE SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: WAVE LINES REFERENCE SETTINGS'
# min SNR to consider the line
WAVEREF_NSIG_MIN = Const('WAVEREF_NSIG_MIN', value=None, dtype=int,
                         source=__NAME__, minimum=0, group=cgroup,
                         description='min SNR to consider the line')

# minimum distance to the edge of the array to consider a line
WAVEREF_EDGE_WMAX = Const('WAVEREF_EDGE_WMAX', value=None, dtype=int,
                          source=__NAME__, minimum=0, group=cgroup,
                          description=('minimum distance to the edge of the '
                                       'array to consider a line'))

# value in pixel (+/-) for the box size around each HC line to perform fit
WAVEREF_HC_BOXSIZE = Const('WAVEREF_HC_BOXSIZE', value=None, dtype=int,
                           source=__NAME__, minimum=0, group=cgroup,
                           description=('value in pixel (+/-) for the box size '
                                        'around each HC line to perform fit'))

# get valid hc dprtypes (string list separated by commas)
WAVEREF_HC_FIBTYPES = Const('WAVEREF_HC_FIBTYPES', value=None, dtype=str,
                            source=__NAME__, group=cgroup,
                            description=('get valid hc dprtypes (string list '
                                         'separated by commas)'))

# get valid fp dprtypes (string list separated by commas)
WAVEREF_FP_FIBTYPES = Const('WAVEREF_HC_FIBTYPES', value=None, dtype=str,
                            source=__NAME__, group=cgroup)

# get the degree to fix master wavelength to in hc mode
WAVEREF_FITDEG = Const('WAVEREF_FITDEG', value=None, dtype=int,
                       source=__NAME__, minimum=1, group=cgroup,
                       description=('get the degree to fix master wavelength '
                                    'to in hc mode'))

# define the lowest N for fp peaks
WAVEREF_FP_NLOW = Const('WAVEREF_FP_NLOW', value=None, dtype=int,
                        source=__NAME__, minimum=0, group=cgroup,
                        description='define the lowest N for fp peaks')

# define the highest N for fp peaks
WAVEREF_FP_NHIGH = Const('WAVEREF_FP_NHIGH', value=None, dtype=int,
                         source=__NAME__, minimum=1, group=cgroup,
                         description='define the highest N for fp peaks')

# define the number of iterations required to do the FP polynomial inversion
WAVEREF_FP_POLYINV = Const('WAVEREF_FP_POLYINV', value=None, dtype=int,
                           source=__NAME__, minimum=1, group=cgroup,
                           description=('define the number of iterations '
                                        'required to do the FP polynomial '
                                        'inversion'))

# =============================================================================
# CALIBRATION: WAVE RESOLUTION MAP SETTINGS
# =============================================================================
# define the number of bins in order direction to use in the resolution map
WAVE_RES_MAP_ORDER_BINS = Const('WAVE_RES_MAP_ORDER_BINS', value=None,
                                dtype=int, source=__NAME__, minimum=1,
                                group=cgroup,
                                description='define the number of bins in '
                                            'order direction to use in the '
                                            'resolution map')

# define the number of bins in spatial direction to use in the resolution map
WAVE_RES_MAP_SPATIAL_BINS = Const('WAVE_RES_MAP_SPATIAL_BINS', value=None,
                                  dtype=int, source=__NAME__, minimum=1,
                                  group=cgroup,
                                  description='define the number of bins in '
                                              'spatial direction to use in the '
                                              'resolution map')

# define the low pass filter size for the HC E2DS file in the resolution map
WAVE_RES_MAP_FILTER_SIZE = Const('WAVE_RES_MAP_FILTER_SIZE', value=None,
                                 dtype=int,
                                 source=__NAME__, minimum=1, group=cgroup,
                                 description='define the low pass filter size '
                                             'for the HC E2DS file in the '
                                             'resolution map')

# define the broad resolution map velocity cut off (in km/s)
WAVE_RES_VELO_CUTOFF1 = Const('WAVE_RES_VELO_CUTOFF1', value=None,
                              dtype=float, source=__NAME__, minimum=0,
                              group=cgroup,
                              description='define the broad resolution map '
                                          'velocity cut off (in km/s)')

# define the tight resolution map velocity cut off (in km/s)
WAVE_RES_VELO_CUTOFF2 = Const('WAVE_RES_VELO_CUTOFF2', value=None,
                              dtype=float, source=__NAME__, minimum=0,
                              group=cgroup,
                              description='define the tight resolution map '
                                          'velocity cut off (in km/s)')

# =============================================================================
# CALIBRATION: WAVE CCF SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: WAVE CCF SETTINGS'
#   The value of the noise for wave dv rms calculation
#       snr = flux/sqrt(flux + noise^2)
WAVE_CCF_NOISE_SIGDET = Const('WAVE_CCF_NOISE_SIGDET', value=None, dtype=float,
                              source=__NAME__, minimum=0.0, group=cgroup,

                              description=('The value of the noise for wave '
                                           'dv rms calculation '
                                           '\n\tsnr = flux/sqrt(flux + '
                                           'noise^2)'))

#   The size around a saturated pixel to flag as unusable for wave dv rms
#      calculation
WAVE_CCF_NOISE_BOXSIZE = Const('WAVE_CCF_NOISE_BOXSIZE', value=None, dtype=int,
                               source=__NAME__, minimum=0.0, group=cgroup,
                               description=('The size around a saturated pixel '
                                            'to flag as unusable for wave dv '
                                            'rms calculation'))

#   The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
WAVE_CCF_NOISE_THRES = Const('WAVE_CCF_NOISE_THRES', value=None, dtype=float,
                             source=__NAME__, minimum=0.0, group=cgroup,
                             description=('The maximum flux for a good '
                                          '(unsaturated) pixel for wave dv '
                                          'rms calculation'))

#   The CCF step size to use for the FP CCF
WAVE_CCF_STEP = Const('WAVE_CCF_STEP', value=None, dtype=float, source=__NAME__,
                      minimum=0.0, group=cgroup,
                      description='The CCF step size to use for the FP CCF')

#   The CCF width size to use for the FP CCF
WAVE_CCF_WIDTH = Const('WAVE_CCF_WIDTH', value=None, dtype=float,
                       source=__NAME__, minimum=0.0, group=cgroup,
                       description='The CCF width size to use for the FP CCF')

#   The target RV (CCF center) to use for the FP CCF
WAVE_CCF_TARGET_RV = Const('WAVE_CCF_TARGET_RV', value=None, dtype=float,
                           source=__NAME__, minimum=0.0, group=cgroup,
                           description=('The target RV (CCF center) to use for '
                                        'the FP CCF'))

#  The detector noise to use for the FP CCF
WAVE_CCF_DETNOISE = Const('WAVE_CCF_DETNOISE', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup,
                          description=('The detector noise to use for the '
                                       'FP CCF'))

#  The filename of the CCF Mask to use for the FP CCF
WAVE_CCF_MASK = Const('WAVE_CCF_MASK', value=None, dtype=str, source=__NAME__,
                      group=cgroup,
                      description=('The filename of the CCF Mask to use for '
                                   'the FP CCF'))

# Define the default CCF MASK normalisation mode for FP CCF
#   options are:
#     'None'         for no normalization
#     'all'          for normalization across all orders
#     'order'        for normalization for each order
WAVE_CCF_MASK_NORMALIZATION = Const('WAVE_CCF_MASK_NORMALIZATION', value=None,
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
WAVE_CCF_MASK_UNITS = Const('WAVE_CCF_MASK_UNITS', value=None, dtype=str,
                            source=__NAME__, group=cgroup,
                            description=('Define the wavelength units for '
                                         'the mask for the FP CCF'))

# Define the ccf mask path the FP CCF
WAVE_CCF_MASK_PATH = Const('WAVE_CCF_MASK_PATH', value=None, dtype=str,
                           source=__NAME__, group=cgroup,

                           description='Define the ccf mask path the FP CCF')

# Define the CCF mask format (must be an astropy.table format)
WAVE_CCF_MASK_FMT = Const('WAVE_CCF_MASK_FMT', value=None, dtype=str,
                          source=__NAME__, group=cgroup,
                          description=('Define the CCF mask format (must be an '
                                       'astropy.table format)'))

#  Define the weight of the CCF mask (if 1 force all weights equal)
WAVE_CCF_MASK_MIN_WEIGHT = Const('WAVE_CCF_MASK_MIN_WEIGHT', value=None,
                                 dtype=float, source=__NAME__, group=cgroup,
                                 description=('Define the weight of the CCF '
                                              'mask (if 1 force all weights '
                                              'equal)'))

#  Define the width of the template line (if 0 use natural)
WAVE_CCF_MASK_WIDTH = Const('WAVE_CCF_MASK_WIDTH', value=None, dtype=float,
                            source=__NAME__, group=cgroup,
                            description=('Define the width of the template '
                                         'line (if 0 use natural)'))

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#      to calculate the FP CCF
WAVE_CCF_N_ORD_MAX = Const('WAVE_CCF_N_ORD_MAX', value=None, dtype=int,
                           source=__NAME__, minimum=1, group=cgroup,
                           description=('Define the number of orders (from '
                                        'zero to ccf_num_orders_max) to use '
                                        'to calculate the FP CCF'))

#  Define whether to regenerate the fp mask (WAVE_CCF_MASK) when we
#      update the cavity width in the master wave solution recipe
WAVE_CCF_UPDATE_MASK = Const('WAVE_CCF_UPDATE_MASK', value=None, dtype=bool,
                             source=__NAME__, group=cgroup,
                             description=('Define whether to regenerate the '
                                          'fp mask (WAVE_CCF_MASK) when we '
                                          'update the cavity width in the '
                                          'master wave solution recipe'))

# define the width of the lines in the smart mask [km/s]
WAVE_CCF_SMART_MASK_WIDTH = Const('WAVE_CCF_SMART_MASK_WIDTH', value=None,
                                  dtype=float, source=__NAME__,
                                  minimum=0, group=cgroup,
                                  description=('define the width of the lines '
                                               'in the smart mask [km/s]'))

# define the minimum wavelength for the smart mask [nm]
WAVE_CCF_SMART_MASK_MINLAM = Const('WAVE_CCF_SMART_MASK_MINLAM', value=None,
                                   dtype=float, source=__NAME__,
                                   minimum=0, group=cgroup,
                                   description=('define the minimum wavelength '
                                                'for the smart mask [nm]'))

# define the maximum wavelength for the smart mask [nm]
WAVE_CCF_SMART_MASK_MAXLAM = Const('WAVE_CCF_SMART_MASK_MAXLAM', value=None,
                                   dtype=float, source=__NAME__,
                                   minimum=0, group=cgroup,
                                   description=('define the maximum wavelength '
                                                'for the smart mask [nm]'))

# define a trial minimum FP N value (should be lower than true
#     minimum FP N value)
WAVE_CCF_SMART_MASK_TRIAL_NMIN = Const('WAVE_CCF_SMART_MASK_TRIAL_NMIN',
                                       value=None, dtype=int, source=__NAME__,
                                       minimum=0, group=cgroup,
                                       description='define a trial minimum FP '
                                                   'N value (should be lower '
                                                   'than true minimum FP N '
                                                   'value)')

# define a trial maximum FP N value (should be higher than true
#     maximum FP N value)
WAVE_CCF_SMART_MASK_TRIAL_NMAX = Const('WAVE_CCF_SMART_MASK_TRIAL_NMAX',
                                       value=None, dtype=int, source=__NAME__,
                                       minimum=0, group=cgroup,
                                       description=('define a trial maximum FP '
                                                    'N value (should be higher '
                                                    'than true maximum FP N '
                                                    'value)'))

# define the converges parameter for dwave in smart mask generation
WAVE_CCF_SMART_MASK_DWAVE_THRES = Const('WAVE_CCF_SMART_MASK_TRIAL_NMAX',
                                        value=None, dtype=float,
                                        source=__NAME__, minimum=0,
                                        group=cgroup,
                                        description=('define the converges '
                                                     'parameter for dwave '
                                                     'in smart mask '
                                                     'generation'))

# define the quality control threshold from RV of CCF FP between master
#    fiber and other fibers, above this limit fails QC [m/s]
WAVE_CCF_RV_THRES_QC = Const('WAVE_CCF_RV_THRES_QC', value=None, dtype=float,
                             source=__NAME__, minimum=0, group=cgroup,
                             description=('define the quality control '
                                          'threshold from RV of CCF FP between '
                                          'master fiber and other fibers, '
                                          'above this limit fails QC [m/s]'))



# TODO: Sort out wave constants below here
# =============================================================================
# CALIBRATION: WAVE GENERAL SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: WAVE GENERAL SETTING'


# Define the line list file (located in the DRS_WAVE_DATA directory)
WAVE_LINELIST_FILE = Const('WAVE_LINELIST_FILE', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           description=('Define the line list file (located in '
                                        'the DRS_WAVE_DATA directory)'))

# Define the line list file format (must be astropy.table format)
WAVE_LINELIST_FMT = Const('WAVE_LINELIST_FMT', value=None, dtype=str,
                          source=__NAME__, group=cgroup,
                          description=('Define the line list file format (must '
                                       'be astropy.table format)'))

# Define the line list file column names (must be separated by commas
# and must be equal to the number of columns in file)
WAVE_LINELIST_COLS = Const('WAVE_LINELIST_COLS', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           description=('Define the line list file column '
                                        'names (must be separated by commas '
                                        'and must be equal to the number of '
                                        'columns in file)'))

# Define the line list file row the data starts
WAVE_LINELIST_START = Const('WAVE_LINELIST_START', value=None, dtype=int,
                            source=__NAME__, group=cgroup, 
                            description=('Define the line list file row the '
                                         'data starts'))

# Define the line list file wavelength column and amplitude column
#  Must be in WAVE_LINELIST_COLS
WAVE_LINELIST_WAVECOL = Const('WAVE_LINELIST_WAVECOL', value=None, dtype=str,
                              source=__NAME__, group=cgroup, 
                              description=('Define the line list file '
                                           'wavelength column and amplitude '
                                           'column Must be in '
                                           'WAVE_LINELIST_COLS'))
WAVE_LINELIST_AMPCOL = Const('WAVE_LINELIST_AMPCOL', value=None, dtype=str,
                             source=__NAME__, group=cgroup, description='')

# define whether to always extract HC/FP files in the wave code (even if they
#    have already been extracted
WAVE_ALWAYS_EXTRACT = Const('WAVE_ALWAYS_EXTRACT', value=None, dtype=bool,
                            source=__NAME__, user=True, active=False,
                            group=cgroup,
                            description='define whether to always extract '
                                        'HC/FP files in the wave code '
                                        '(even if they')

# define the type of file to use for wave solution (currently allowed are
#    'E2DS' or 'E2DSFF'
WAVE_EXTRACT_TYPE = Const('WAVE_EXTRACT_TYPE', value=None, dtype=str,
                          source=__NAME__, options=['E2DS', 'E2DSFF'],
                          user=True, active=False, group=cgroup,
                          description='define the type of file to use for '
                                      'wave solution (currently allowed '
                                      'are "E2DS" or "E2DSFF"')

# define the fit degree for the wavelength solution
WAVE_FIT_DEGREE = Const('WAVE_FIT_DEGREE', value=None, dtype=int,
                        source=__NAME__, user=True, active=False, group=cgroup,
                        description='define the fit degree for the '
                                    'wavelength solution')

# Define intercept and slope for a pixel shift
WAVE_PIXEL_SHIFT_INTER = Const('WAVE_PIXEL_SHIFT_INTER', value=None,
                               dtype=float, source=__NAME__, group=cgroup, 
                               description=('Define intercept and slope for a '
                                            'pixel shift'))
WAVE_PIXEL_SHIFT_SLOPE = Const('WAVE_PIXEL_SHIFT_SLOPE', value=None,
                               dtype=float, source=__NAME__, group=cgroup,
                               description='')

#  Defines echelle of first extracted order
WAVE_T_ORDER_START = Const('WAVE_T_ORDER_START', value=None,
                           dtype=int, source=__NAME__, group=cgroup, 
                           description=('Defines echelle of first extracted '
                                        'order'))

#  Defines order from which the solution is calculated
WAVE_N_ORD_START = Const('WAVE_N_ORD_START', value=None, dtype=int,
                         source=__NAME__, group=cgroup, 
                         description=('Defines order from which the solution '
                                      'is calculated'))

#  Defines order to which the solution is calculated
WAVE_N_ORD_FINAL = Const('WAVE_N_ORD_FINAL', value=None, dtype=int,
                         source=__NAME__, group=cgroup, 
                         description=('Defines order to which the solution is '
                                      'calculated'))

# =============================================================================
# CALIBRATION: WAVE HC SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: WAVE HC SETTING'
# Define the mode to calculate the hc wave solution
WAVE_MODE_HC = Const('WAVE_MODE_HC', value=None, dtype=int, source=__NAME__,
                     options=[0], user=True, active=False, group=cgroup,
                     description='Define the mode to calculate the hc '
                                 'wave solution')

# width of the box for fitting HC lines. Lines will be fitted from -W to +W,
#     so a 2*W+1 window
WAVE_HC_FITBOX_SIZE = Const('WAVE_HC_FITBOX_SIZE', value=None, dtype=int,
                            source=__NAME__, group=cgroup, 
                            description=('width of the box for fitting HC '
                                         'lines. Lines will be fitted from -W '
                                         'to +W, so a 2*W+1 window'))

# number of sigma above local RMS for a line to be flagged as such
WAVE_HC_FITBOX_SIGMA = Const('WAVE_HC_FITBOX_SIGMA', value=None, dtype=float,
                             source=__NAME__, group=cgroup, 
                             description=('number of sigma above local RMS for '
                                          'a line to be flagged as such'))

# the fit degree for the wave hc gaussian peaks fit
WAVE_HC_FITBOX_GFIT_DEG = Const('WAVE_HC_FITBOX_GFIT_DEG', value=None,
                                dtype=int, source=__NAME__, group=cgroup, 
                                description=('the fit degree for the wave hc '
                                             'gaussian peaks fit'))

# the RMS of line-fitted line must be between DEVMIN and DEVMAX of the peak
#     value must be SNR>5 (or 1/SNR<0.2)
WAVE_HC_FITBOX_RMS_DEVMIN = Const('WAVE_HC_FITBOX_RMS_DEVMIN', value=None,
                                  dtype=float, source=__NAME__, minimum=0.0,
                                  group=cgroup, 
                                  description=('the RMS of line-fitted line '
                                               'must be between DEVMIN and '
                                               'DEVMAX of the peak value must '
                                               'be SNR>5 (or 1/SNR<0.2)'))
WAVE_HC_FITBOX_RMS_DEVMAX = Const('WAVE_HC_FITBOX_RMS_DEVMAX', value=None,
                                  dtype=float, source=__NAME__, minimum=0.0,
                                  group=cgroup, description='')

# the e-width of the line expressed in pixels.
WAVE_HC_FITBOX_EWMIN = Const('WAVE_HC_FITBOX_EWMIN', value=None, dtype=float,
                             source=__NAME__, minimum=0.0, group=cgroup, 
                             description=('the e-width of the line expressed '
                                          'in pixels.'))
WAVE_HC_FITBOX_EWMAX = Const('WAVE_HC_FITBOX_EWMAX', value=None, dtype=float,
                             source=__NAME__, minimum=0.0, group=cgroup,
                             description='')

# define the file type for saving the initial guess at the hc peak list
WAVE_HCLL_FILE_FMT = Const('WAVE_LINELIST_FMT', value=None, dtype=str,
                           source=__NAME__, group=cgroup)

# number of bright lines kept per order
#     avoid >25 as it takes super long
#     avoid <12 as some orders are ill-defined and we need >10 valid
#         lines anyway
#     20 is a good number, and we see no reason to change it
WAVE_HC_NMAX_BRIGHT = Const('WAVE_HC_NMAX_BRIGHT', value=None, dtype=int,
                            source=__NAME__, minimum=10, maximum=30,
                            group=cgroup, 
                            description=('number of bright lines kept per '
                                         'order avoid >25 as it takes super '
                                         'long avoid <12 as some orders are '
                                         'ill-defined and we need >10 valid '
                                         'lines anyway 20 is a good number, '
                                         'and we see no reason to change it'))

# Number of times to run the fit triplet algorithm
WAVE_HC_NITER_FIT_TRIPLET = Const('WAVE_HC_NITER_FIT_TRIPLET', value=None,
                                  dtype=int, source=__NAME__, minimum=1,
                                  group=cgroup, 
                                  description=('Number of times to run the fit '
                                               'triplet algorithm'))

# Maximum distance between catalog line and init guess line to accept
#     line in m/s
WAVE_HC_MAX_DV_CAT_GUESS = Const('WAVE_HC_MAX_DV_CAT_GUESS', value=None,
                                 dtype=int, source=__NAME__, minimum=0.0,
                                 group=cgroup, 
                                 description=('Maximum distance between '
                                              'catalog line and init guess '
                                              'line to accept line in m/s'))

# The fit degree between triplets
WAVE_HC_TFIT_DEG = Const('WAVE_HC_TFIT_DEG', value=None, dtype=int,
                         source=__NAME__, minimum=0, group=cgroup,
                         description='The fit degree between triplets')

# Cut threshold for the triplet line fit [in km/s]
WAVE_HC_TFIT_CUT_THRES = Const('WAVE_HC_TFIT_CUT_THRES', value=None,
                               dtype=float, source=__NAME__, minimum=0.0,
                               group=cgroup, 
                               description=('Cut threshold for the triplet '
                                            'line fit [in km/s]'))

# Minimum number of lines required per order
WAVE_HC_TFIT_MINNUM_LINES = Const('WAVE_HC_TFIT_MINNUM_LINES', value=None,
                                  dtype=int, source=__NAME__, minimum=0,
                                  group=cgroup, 
                                  description=('Minimum number of lines '
                                               'required per order'))

# Minimum total number of lines required
WAVE_HC_TFIT_MINTOT_LINES = Const('WAVE_HC_TFIT_MINTOT_LINES', value=None,
                                  dtype=int, source=__NAME__, minimum=0,
                                  group=cgroup, 
                                  description=('Minimum total number of '
                                               'lines required'))

# this sets the order of the polynomial used to ensure continuity
#     in the  xpix vs wave solutions by setting the first term = 12,
#     we force that the zeroth element of the xpix of the wavelegnth
#     grid is fitted with a 12th order polynomial as a function of
#     order number (format = string list separated by commas
WAVE_HC_TFIT_ORDER_FIT_CONT = Const('WAVE_HC_TFIT_ORDER_FIT_CONT', value=None,
                                    dtype=str, source=__NAME__, group=cgroup, 
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
                                                 'number (format = string list '
                                                 'separated by commas'))

# Number of times to loop through the sigma clip for triplet fit
WAVE_HC_TFIT_SIGCLIP_NUM = Const('WAVE_HC_TFIT_SIGCLIP_NUM', value=None,
                                 dtype=int, source=__NAME__, minimum=1,
                                 group=cgroup, 
                                 description=('Number of times to loop through '
                                              'the sigma clip for triplet fit'))

# Sigma clip threshold for triplet fit
WAVE_HC_TFIT_SIGCLIP_THRES = Const('WAVE_HC_TFIT_SIGCLIP_THRES', value=None,
                                   dtype=float, source=__NAME__, minimum=0.0,
                                   group=cgroup, 
                                   description=('Sigma clip threshold for '
                                                'triplet fit'))

# Define the distance in m/s away from the center of dv hist points
#     outside will be rejected [m/s]
WAVE_HC_TFIT_DVCUT_ORDER = Const('WAVE_HC_TFIT_DVCUT_ORDER', value=None,
                                 dtype=float, source=__NAME__, minimum=0.0,
                                 group=cgroup, 
                                 description=('Define the distance in m/s away '
                                              'from the center of dv hist '
                                              'points outside will be rejected '
                                              '[m/s]'))
WAVE_HC_TFIT_DVCUT_ALL = Const('WAVE_HC_TFIT_DVCUT_ALL', value=None,
                               dtype=float, source=__NAME__, minimum=0.0,
                               group=cgroup, description='')

# Define the resolution and line profile map size (y-axis by x-axis)
WAVE_HC_RESMAP_SIZE = Const('WAVE_HC_RESMAP_SIZE', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('Define the resolution and line '
                                         'profile map size (y-axis by x-axis)'))

# Define the maximum allowed deviation in the RMS line spread function
WAVE_HC_RES_MAXDEV_THRES = Const('WAVE_HC_RES_MAXDEV_THRES', value=None,
                                 dtype=float, source=__NAME__, group=cgroup, 
                                 description=('Define the maximum allowed '
                                              'deviation in the RMS line '
                                              'spread function'))

# quality control criteria if sigma greater than this many sigma fails
WAVE_HC_QC_SIGMA_MAX = Const('WAVE_HC_QC_SIGMA_MAX', value=None, dtype=float,
                             source=__NAME__, minimum=0.0, group=cgroup, 
                             description=('quality control criteria if sigma '
                                          'greater than this many sigma fails'))

# Defines the dv span for PLOT_WAVE_HC_RESMAP debug plot, should be a
#    string list containing a min and max dv value
WAVE_HC_RESMAP_DV_SPAN = Const('WAVE_HC_RESMAP_DV_SPAN', value=None, dtype=str,
                               source=__NAME__, group=cgroup, 
                               description=('Defines the dv span for '
                                            'PLOT_WAVE_HC_RESMAP debug plot, '
                                            'should be a string list '
                                            'containing a min and max dv '
                                            'value'))

# Defines the x limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
#   string list containing a min and max x value
WAVE_HC_RESMAP_XLIM = Const('WAVE_HC_RESMAP_XLIM', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('Defines the x limits for '
                                         'PLOT_WAVE_HC_RESMAP debug plot, '
                                         'should be a string list containing '
                                         'a min and max x value'))

# Defines the y limits for PLOT_WAVE_HC_RESMAP debug plot, should be a
#   string list containing a min and max y value
WAVE_HC_RESMAP_YLIM = Const('WAVE_HC_RESMAP_YLIM', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('Defines the y limits for '
                                         'PLOT_WAVE_HC_RESMAP debug plot, '
                                         'should be a string list containing a '
                                         'min and max y value'))

# =============================================================================
# CALIBRATION: WAVE LITTROW SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: WAVE LITTROW SETTINGS'
#  Define the order to start the Littrow fit from for the HC wave solution
WAVE_LITTROW_ORDER_INIT_1 = Const('WAVE_LITTROW_ORDER_INIT_1', value=None,
                                  dtype=int, source=__NAME__, group=cgroup, 
                                  description=('Define the order to start the '
                                               'Littrow fit from for the HC '
                                               'wave solution'))

#  Define the order to start the Littrow fit from for the FP wave solution
# TODO: Note currently used
WAVE_LITTROW_ORDER_INIT_2 = Const('WAVE_LITTROW_ORDER_INIT_2', value=None,
                                  dtype=int, source=__NAME__, group=cgroup, 
                                  description=('Define the order to start the '
                                               'Littrow fit from for the FP '
                                               'wave solution'))

#  Define the order to end the Littrow fit at for the HC wave solution
WAVE_LITTROW_ORDER_FINAL_1 = Const('WAVE_LITTROW_ORDER_FINAL_1', value=None,
                                   dtype=int, source=__NAME__, group=cgroup, 
                                   description=('Define the order to end the '
                                                'Littrow fit at for the HC '
                                                'wave solution'))

#  Define the order to end the Littrow fit at for the FP wave solution
# TODO: Note currently used
WAVE_LITTROW_ORDER_FINAL_2 = Const('WAVE_LITTROW_ORDER_FINAL_2', value=None,
                                   dtype=int, source=__NAME__, group=cgroup, 
                                   description=('Define the order to end the '
                                                'Littrow fit at for the FP '
                                                'wave solution'))

#  Define orders to ignore in Littrow fit (should be a string list separated
#      by commas
WAVE_LITTROW_REMOVE_ORDERS = Const('WAVE_LITTROW_REMOVE_ORDERS', value=None,
                                   dtype=str, source=__NAME__, group=cgroup, 
                                   description=('Define orders to ignore in '
                                                'Littrow fit (should be a '
                                                'string list separated by '
                                                'commas'))

#  Define the littrow cut steps for the HC wave solution
WAVE_LITTROW_CUT_STEP_1 = Const('WAVE_LITTROW_CUT_STEP_1', value=None,
                                dtype=int, source=__NAME__, group=cgroup, 
                                description=('Define the littrow cut steps for '
                                             'the HC wave solution'))

#  Define the littrow cut steps for the FP wave solution
WAVE_LITTROW_CUT_STEP_2 = Const('WAVE_LITTROW_CUT_STEP_2', value=None,
                                dtype=int, source=__NAME__, group=cgroup, 
                                description=('Define the littrow cut steps for '
                                             'the FP wave solution'))

#  Define the fit polynomial order for the Littrow fit (fit across the orders)
#    for the HC wave solution
WAVE_LITTROW_FIG_DEG_1 = Const('WAVE_LITTROW_FIG_DEG_1', value=None,
                               dtype=int, source=__NAME__, group=cgroup, 
                               description=('Define the fit polynomial order '
                                            'for the Littrow fit (fit across '
                                            'the orders) for the HC wave '
                                            'solution'))

#  Define the fit polynomial order for the Littrow fit (fit across the orders)
#    for the FP wave solution
WAVE_LITTROW_FIG_DEG_2 = Const('WAVE_LITTROW_FIG_DEG_2', value=None,
                               dtype=int, source=__NAME__, group=cgroup, 
                               description=('Define the fit polynomial order '
                                            'for the Littrow fit (fit across '
                                            'the orders) for the FP wave '
                                            'solution'))

#  Define the order fit for the Littrow solution (fit along the orders)
# TODO needs to be the same as ic_ll_degr_fit
WAVE_LITTROW_EXT_ORDER_FIT_DEG = Const('WAVE_LITTROW_EXT_ORDER_FIT_DEG',
                                       value=None, dtype=int, source=__NAME__,
                                       group=cgroup, 
                                       description=('Define the order fit for '
                                                    'the Littrow solution (fit '
                                                    'along the orders) TODO '
                                                    'needs to be the same as '
                                                    'ic_ll_degr_fit'))

#   Maximum littrow RMS value
WAVE_LITTROW_QC_RMS_MAX = Const('WAVE_LITTROW_QC_RMS_MAX', value=None,
                                dtype=float, source=__NAME__, group=cgroup,
                                description='Maximum littrow RMS value')

#   Maximum littrow Deviation from wave solution (at x cut points)
WAVE_LITTROW_QC_DEV_MAX = Const('WAVE_LITTROW_QC_DEV_MAX', value=None,
                                dtype=float, source=__NAME__, group=cgroup, 
                                description=('Maximum littrow Deviation from '
                                             'wave solution (at x cut points)'))

# =============================================================================
# CALIBRATION: WAVE FP SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: WAVE FP SETTING'
# Define the mode to calculate the fp wave solution
WAVE_MODE_FP = Const('WAVE_MODE_FP', value=None, dtype=int, source=__NAME__,
                     options=[0, 1], user=True, active=False, group=cgroup,
                     description='Define the mode to calculate the fp '
                                 'wave solution')

# Define the initial value of FP effective cavity width 2xd in nm
WAVE_FP_DOPD0 = Const('WAVE_FP_DOPD0', value=None, dtype=float,
                      source=__NAME__, minimum=0.0, group=cgroup, 
                      description=('Define the initial value of FP effective '
                                   'cavity width 2xd in nm'))

#  Define the polynomial fit degree between FP line numbers and the
#      measured cavity width for each line
WAVE_FP_CAVFIT_DEG = Const('WAVE_FP_CAVFIT_DEG', value=None, dtype=int,
                           source=__NAME__, minimum=0, group=cgroup, 
                           description=('Define the polynomial fit degree '
                                        'between FP line numbers and the '
                                        'measured cavity width for each line'))

#  Define the FP jump size that is too large
WAVE_FP_LARGE_JUMP = Const('WAVE_FP_LARGE_JUMP', value=None, dtype=float,
                           source=__NAME__, minimum=0, group=cgroup, 
                           description=('Define the FP jump size that is too '
                                        'large'))

# index of FP line to start order cross-matching from
WAVE_FP_CM_IND = Const('WAVE_FP_P2P_WIDTH_CUT', value=None, dtype=int,
                       source=__NAME__, group=cgroup)

# define the percentile to normalize the spectrum to (per order)
#  used to determine FP peaks (peaks must be above a normalised limit
#   defined in WAVE_FP_PEAK_LIM
WAVE_FP_NORM_PERCENTILE = Const('WAVE_FP_NORM_PERCENTILE', value=None,
                                dtype=float, source=__NAME__, minimum=0.0,
                                group=cgroup, 
                                description=('define the percentile to '
                                             'normalize the spectrum to '
                                             '(per order) used to determine FP '
                                             'peaks (peaks must be above a '
                                             'normalised limit defined in '
                                             'WAVE_FP_PEAK_LIM'))

# define the normalised limit below which FP peaks are not used
WAVE_FP_PEAK_LIM = Const('WAVE_FP_PEAK_LIM', value=None,
                         dtype=float, source=__NAME__, minimum=0.0,
                         group=cgroup, 
                         description=('define the normalised limit below which '
                                      'FP peaks are not used'))

#    Define peak to peak width that is too large (removed from FP peaks)
WAVE_FP_P2P_WIDTH_CUT = Const('WAVE_FP_P2P_WIDTH_CUT', value=None,
                              dtype=float, source=__NAME__, minimum=0.0,
                              group=cgroup,
                              description=('Define peak to peak width that is '
                                           'too large (removed from FP peaks)'))

# Define the minimum instrumental error
WAVE_FP_ERRX_MIN = Const('WAVE_FP_ERRX_MIN', value=None, dtype=float,
                         source=__NAME__, minimum=0.0, group=cgroup,
                         description='Define the minimum instrumental error')

#  Define the wavelength fit polynomial order
WAVE_FP_LL_DEGR_FIT = Const('WAVE_FP_LL_DEGR_FIT', value=None, dtype=int,
                            source=__NAME__, minimum=0, group=cgroup, 
                            description=('Define the wavelength fit polynomial '
                                         'order'))

#  Define the max rms for the wavelength sigma-clip fit
WAVE_FP_MAX_LLFIT_RMS = Const('WAVE_FP_MAX_LLFIT_RMS', value=None, dtype=float,
                              source=__NAME__, minimum=0, group=cgroup, 
                              description=('Define the max rms for the '
                                           'wavelength sigma-clip fit'))

#  Define the weight threshold (small number) below which we do not keep fp
#     lines
WAVE_FP_WEIGHT_THRES = Const('WAVE_FP_WEIGHT_THRES', value=None, dtype=float,
                             source=__NAME__, minimum=0.0, group=cgroup, 
                             description=('Define the weight threshold (small '
                                          'number) below which we do not keep '
                                          'fp lines'))

# Minimum blaze threshold to keep FP peaks
WAVE_FP_BLAZE_THRES = Const('WAVE_FP_BLAZE_THRES', value=None, dtype=float,
                            source=__NAME__, minimum=0.0, group=cgroup, 
                            description=('Minimum blaze threshold to keep '
                                         'FP peaks'))

# Minimum FP peaks pixel separation fraction diff. from median
WAVE_FP_XDIF_MIN = Const('WAVE_FP_XDIF_MIN', value=None, dtype=float,
                         source=__NAME__, minimum=0.0, group=cgroup, 
                         description=('Minimum FP peaks pixel separation '
                                      'fraction diff. from median'))

# Maximum FP peaks pixel separation fraction diff. from median
WAVE_FP_XDIF_MAX = Const('WAVE_FP_XDIF_MAX', value=None, dtype=float,
                         source=__NAME__, minimum=0.0, group=cgroup, 
                         description=('Maximum FP peaks pixel separation '
                                      'fraction diff. from median'))

# Maximum fract. wavelength offset between cross-matched FP peaks
WAVE_FP_LL_OFFSET = Const('WAVE_FP_LL_OFFSET', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Maximum fract. wavelength offset '
                                       'between cross-matched FP peaks'))

# Maximum DV to keep HC lines in combined (WAVE_NEW) solution
WAVE_FP_DV_MAX = Const('WAVE_FP_DV_MAX', value=None, dtype=float,
                       source=__NAME__, minimum=0.0, group=cgroup, 
                       description=('Maximum DV to keep HC lines in combined '
                                    '(WAVE_NEW) solution'))

# Decide whether to refit the cavity width (will update if files do not
#   exist)
WAVE_FP_UPDATE_CAVITY = Const('WAVE_FP_UPDATE_CAVITY', value=None, dtype=bool,
                              source=__NAME__, group=cgroup, 
                              description=('Decide whether to refit the cavity '
                                           'width (will update if files do not '
                                           'exist)'))

# Select the FP cavity fitting (WAVE_MODE_FP = 1 only)
#   Should be one of the following:
#       0 - derive using the 1/m vs d fit from HC lines
#       1 - derive using the ll vs d fit from HC lines
WAVE_FP_CAVFIT_MODE = Const('WAVE_FP_CAVFIT_MODE', value=None, dtype=int,
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
WAVE_FP_LLFIT_MODE = Const('WAVE_FP_LLFIT_MODE', value=None, dtype=int,
                           source=__NAME__, options=[0, 1], group=cgroup, 
                           description=('Select the FP wavelength fitting '
                                        '(WAVE_MODE_FP = 1 only) Should be '
                                        'one of the following: '
                                        '\n\t0 - use fit_1d_solution function '
                                        '\n\t1 - fit with sigma-clipping and '
                                        'mod 1 pixel correction'))

# Minimum FP peaks wavelength separation fraction diff. from median
WAVE_FP_LLDIF_MIN = Const('WAVE_FP_LLDIF_MIN', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Minimum FP peaks wavelength separation '
                                       'fraction diff. from median'))

# Maximum FP peaks wavelength separation fraction diff. from median
WAVE_FP_LLDIF_MAX = Const('WAVE_FP_LLDIF_MAX', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Maximum FP peaks wavelength separation '
                                       'fraction diff. from median'))

# Sigma-clip value for sigclip_polyfit
WAVE_FP_SIGCLIP = Const('WAVE_FP_SIGCLIP', value=None, dtype=float,
                        source=__NAME__, minimum=0.0, group=cgroup,
                        description='Sigma-clip value for sigclip_polyfit')

# First order for multi-order wave fp plot
WAVE_FP_PLOT_MULTI_INIT = Const('WAVE_FP_PLOT_MULTI_INIT', value=None,
                                dtype=int, source=__NAME__, minimum=0,
                                group=cgroup, 
                                description=('First order for multi-order wave '
                                             'fp plot'))

# Number of orders in multi-order wave fp plot
WAVE_FP_PLOT_MULTI_NBO = Const('WAVE_FP_PLOT_MULTI_NBO', value=None, dtype=int,
                               source=__NAME__, minimum=1, group=cgroup, 
                               description=('Number of orders in multi-order '
                                            'wave fp plot'))

# define the dprtype for generating FPLINES (string list)
WAVE_FP_DPRLIST = Const('WAVE_FP_DPRLIST', value=None, dtype=str,
                        source=__NAME__, group=cgroup, 
                        description=('define the dprtype for generating '
                                     'FPLINES (string list)'))

# =============================================================================
# CALIBRATION: WAVE NIGHT SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: WAVE NIGHT SETTINGS'

# number of iterations for hc convergence
WAVE_NIGHT_NITERATIONS1 = Const('WAVE_NIGHT_NITERATIONS1', value=None,
                                dtype=int, source=__NAME__, minimum=1,
                                group=cgroup, 
                                description=('number of iterations for hc '
                                             'convergence'))

# number of iterations for fp convergence
WAVE_NIGHT_NITERATIONS2 = Const('WAVE_NIGHT_NITERATIONS2', value=None,
                                dtype=int, source=__NAME__, minimum=1,
                                group=cgroup, 
                                description=('number of iterations for fp '
                                             'convergence'))

# starting point for the cavity corrections
WAVE_NIGHT_DCAVITY = Const('WAVE_NIGHT_DCAVITY', value=None, dtype=float,
                           source=__NAME__, minimum=0.0, group=cgroup, 
                           description=('starting point for the cavity '
                                        'corrections'))

# define the sigma clip value to remove bad hc lines
WAVE_NIGHT_HC_SIGCLIP = Const('WAVE_NIGHT_HC_SIGCLIP', value=None, dtype=float,
                              source=__NAME__, minimum=0.0, group=cgroup, 
                              description=('define the sigma clip value to '
                                           'remove bad hc lines'))

# median absolute deviation cut off
WAVE_NIGHT_MED_ABS_DEV = Const('WAVE_NIGHT_MED_ABS_DEV', value=None,
                               dtype=float, source=__NAME__, minimum=0.0,
                               group=cgroup, 
                               description=('median absolute deviation '
                                            'cut off'))

# sigma clipping for the fit
WAVE_NIGHT_NSIG_FIT_CUT = Const('WAVE_NIGHT_NSIG_FIT_CUT', value=None,
                                dtype=float, source=__NAME__, minimum=1,
                                group=cgroup,
                                description='sigma clipping for the fit')

# wave night plot hist number of bins
WAVENIGHT_PLT_NBINS = Const('WAVENIGHT_PLT_NBINS', value=None, dtype=int,
                            source=__NAME__, minimum=0, group=cgroup, 
                            description=('wave night plot hist number of '
                                         'bins'))

# wave night plot hc bin lower bound in multiples of rms
WAVENIGHT_PLT_BINL = Const('WAVENIGHT_PLT_BINL', value=None, dtype=float,
                           source=__NAME__, minimum=0, group=cgroup, 
                           description=('wave night plot hc bin lower bound '
                                        'in multiples of rms'))

# wave night plot hc bin upper bound in multiples of rms
WAVENIGHT_PLT_BINU = Const('WAVENIGHT_PLT_BINU', value=None, dtype=float,
                           source=__NAME__, minimum=0, group=cgroup, 
                           description=('wave night plot hc bin upper bound in '
                                        'multiples of rms'))

# =============================================================================
# OBJECT: TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJECT: TELLURIC SETTINGS'
# Define the name of the tapas file to use
TAPAS_FILE = Const('TAPAS_FILE', value=None, dtype=str, source=__NAME__,
                   group=cgroup,
                   description='Define the name of the tapas file to use')

# Define the format (astropy format) of the tapas file "TAPAS_FILE"
TAPAS_FILE_FMT = Const('TAPAS_FILE_FMT', value=None, dtype=str, source=__NAME__,
                       group=cgroup, 
                       description=('Define the format (astropy format) of the '
                                    'tapas file "TAPAS_FILE"'))

# The allowed input DPRTYPES for input telluric files
TELLU_ALLOWED_DPRTYPES = Const('TELLU_ALLOWED_DPRTYPES', value=None, dtype=str,
                               source=__NAME__, group=cgroup, 
                               description=('The allowed input DPRTYPES for '
                                            'input telluric files'))

# Define level above which the blaze is high enough to accurately
#    measure telluric
TELLU_CUT_BLAZE_NORM = Const('TELLU_CUT_BLAZE_NORM', value=None, dtype=float,
                             source=__NAME__, group=cgroup, 
                             description=('Define level above which the blaze '
                                          'is high enough to accurately '
                                          'measure telluric'))

# Define telluric include/exclude list directory
TELLU_LIST_DIRECTORY = Const('TELLU_LIST_DIRECTORY', value=None, dtype=str,
                             source=__NAME__, group=cgroup, 
                             description=('Define telluric include/exclude list '
                                          'directory'))

# Define telluric white list name
TELLU_WHITELIST_NAME = Const('TELLU_WHITELIST_NAME', value=None, dtype=str,
                             source=__NAME__, group=cgroup,
                             description='Define telluric white list name')

# Define telluric black list name
TELLU_BLACKLIST_NAME = Const('TELLU_BLACKLIST_NAME', value=None, dtype=str,
                             source=__NAME__, group=cgroup,
                             description='Define telluric black list name')

# =============================================================================
# OBJECT: TELLURIC PRE-CLEANING SETTINGS
# =============================================================================
cgroup = 'OBJECT: TELLURIC PRE-CLEANING SETTINGS'

# define whether we do pre-cleaning
TELLUP_DO_PRECLEANING = Const('TELLUP_DO_PRECLEANING', value=None, dtype=bool,
                              source=__NAME__, group=cgroup,
                              description='define whether we do pre-cleaning')

# width in km/s for the ccf scan to determine the abso in pre-cleaning
TELLUP_CCF_SCAN_RANGE = Const('TELLUP_CCF_SCAN_RANGE', value=None, dtype=float,
                              source=__NAME__, group=cgroup, minimum=0.0, 
                              description=('width in km/s for the ccf scan to '
                                           'determine the abso in '
                                           'pre-cleaning'))

# define whether to clean OH lines
TELLUP_CLEAN_OH_LINES = Const('TELLUP_CLEAN_OH_LINES', value=None, dtype=bool,
                              source=__NAME__, group=cgroup,
                              description='define whether to clean OH lines')

# Define the number of bright OH lines that will be individually adjusted
#     in amplitude. Done only on lines that are at an SNR > 1
TELLUP_OHLINE_NBRIGHT = Const('TELLUP_OHLINE_NBRIGHT', value=None, dtype=int,
                              source=__NAME__, group=cgroup,
                              description='Define the number of bright OH '
                                          'lines that will be individually '
                                          'adjusted in amplitude. Done only on '
                                          'lines that are at an SNR > 1')

# define the OH line pca file
TELLUP_OHLINE_PCA_FILE = Const('TELLUP_OHLINE_PCA_FILE', value=None, dtype=str,
                               source=__NAME__, group=cgroup,
                               description='define the OH line pca file')

# define the orders not to use in pre-cleaning fit (due to thermal
# background)
TELLUP_REMOVE_ORDS = Const('TELLUP_REMOVE_ORDS', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           description=('define the orders not to use in '
                                        'pre-cleaning fit (due to thermal '
                                        'background)'))

# define the minimum snr to accept orders for pre-cleaning fit
TELLUP_SNR_MIN_THRES = Const('TELLUP_SNR_MIN_THRES', value=None, dtype=float,
                             source=__NAME__, group=cgroup, minimum=0.0, 
                             description=('define the minimum snr to accept '
                                          'orders for pre-cleaning fit'))

# define the telluric trans other abso CCF file
TELLUP_OTHERS_CCF_FILE = Const('TELLUP_OTHERS_CCF_FILE', value=None, dtype=str,
                               source=__NAME__, group=cgroup, 
                               description=('define the telluric trans other '
                                            'abso CCF file'))

# define the telluric trans water abso CCF file
TELLUP_H2O_CCF_FILE = Const('TELLUP_H2O_CCF_FILE', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('define the telluric trans water abso '
                                         'CCF file'))

# define dexpo convergence threshold
TELLUP_DEXPO_CONV_THRES = Const('TELLUP_DEXPO_CONV_THRES', value=None,
                                dtype=float, source=__NAME__, group=cgroup,
                                minimum=0.0, 
                                description=('define dexpo convergence '
                                             'threshold'))

# define the maximum number of iterations to try to get dexpo
# convergence
TELLUP_DEXPO_MAX_ITR = Const('TELLUP_DEXPO_MAX_ITR', value=None, dtype=int,
                             source=__NAME__, group=cgroup, minimum=1, 
                             description=('define the maximum number of '
                                          'iterations to try to get dexpo '
                                          'convergence'))

# define the kernel threshold in abso_expo
TELLUP_ABSO_EXPO_KTHRES = Const('TELLUP_ABSO_EXPO_KTHRES', value=None,
                                dtype=float, source=__NAME__, group=cgroup,
                                minimum=0.0, 
                                description=('define the kernel threshold in '
                                             'abso_expo'))

# define the gaussian width of the kernel used in abso_expo
TELLUP_ABSO_EXPO_KWID = Const('TELLUP_ABSO_EXPO_KWID', value=None,
                              dtype=float, source=__NAME__, group=cgroup,
                              minimum=0.0, 
                              description=('define the gaussian width of the '
                                           'kernel used in abso_expo'))

# define the gaussian exponent of the kernel used in abso_expo
#   a value of 2 is gaussian, a value >2 is boxy
TELLUP_ABSO_EXPO_KEXP = Const('TELLUP_ABSO_EXPO_KEXP', value=None,
                              dtype=float, source=__NAME__, group=cgroup,
                              minimum=0.0, 
                              description=('define the gaussian exponent of '
                                           'the kernel used in abso_expo a '
                                           'value of 2 is gaussian, a '
                                           'value >2 is boxy'))

# define the transmission threshold (in exponential form) for keeping
#   valid transmission
TELLUP_TRANS_THRES = Const('TELLUP_TRANS_THRES', value=None,
                           dtype=float, source=__NAME__, group=cgroup, 
                           description=('define the transmission threshold '
                                        '(in exponential form) for keeping '
                                        'valid transmission'))

# define the threshold for discrepant transmission (in sigma)
TELLUP_TRANS_SIGLIM = Const('TELLUP_TRANS_SIGLIM', value=None,
                            dtype=float, source=__NAME__, group=cgroup,
                            minimum=0.0, 
                            description=('define the threshold for discrepant '
                                         'transmission (in sigma)'))

# define whether to force airmass fit to header airmass value
TELLUP_FORCE_AIRMASS = Const('TELLUP_FORCE_AIRMASS', value=None, dtype=bool,
                             source=__NAME__, group=cgroup, 
                             description=('define whether to force airmass '
                                          'fit to header airmass value'))

# set the typical water abso exponent. Compare to values in header for
#    high-snr targets later
TELLUP_D_WATER_ABSO = Const('TELLUP_D_WATER_ABSO', value=None,
                            dtype=float, source=__NAME__, group=cgroup,
                            minimum=0.0, 
                            description=('set the typical water abso exponent. '
                                         'Compare to values in header for '
                                         'high-snr targets later'))

# set the lower and upper bounds (String list) for the exponent of
#  the other species of absorbers
TELLUP_OTHER_BOUNDS = Const('TELLUP_OTHER_BOUNDS', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('set the lower and upper bounds '
                                         '(String list) for the exponent of '
                                         'the other species of absorbers'))

# set the lower and upper bounds (string list) for the exponent of
#  water absorber
TELLUP_WATER_BOUNDS = Const('TELLUP_WATER_BOUNDS', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('set the lower and upper bounds '
                                         '(string list) for the exponent of '
                                         'water absorber'))

# =============================================================================
# OBJECT: MAKE TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJECT: MAKE TELLURIC SETTINGS'
# value below which the blaze in considered too low to be useful
#     for all blaze profiles, we normalize to the 95th percentile.
#     That's pretty much the peak value, but it is resistent to
#     eventual outliers
MKTELLU_BLAZE_PERCENTILE = Const('MKTELLU_BLAZE_PERCENTILE', value=None,
                                 dtype=float, source=__NAME__, group=cgroup, 
                                 description=('value below which the blaze in '
                                              'considered too low to be useful '
                                              'for all blaze profiles, we '
                                              'normalize to the 95th '
                                              'percentile. Thats pretty much '
                                              'the peak value, but it is '
                                              'resistent to eventual outliers'))
MKTELLU_CUT_BLAZE_NORM = Const('MKTELLU_CUT_BLAZE_NORM', value=None,
                               dtype=float, source=__NAME__, group=cgroup,
                               description='')

# Define list of absorbers in the tapas fits table
TELLU_ABSORBERS = Const('TELLU_ABSORBERS', value=None, dtype=str,
                        source=__NAME__, group=cgroup, 
                        description=('Define list of absorbers in the tapas '
                                     'fits table'))

# define the default convolution width [in pixels]
MKTELLU_DEFAULT_CONV_WIDTH = Const('MKTELLU_DEFAULT_CONV_WIDTH', value=None,
                                   dtype=int, source=__NAME__, group=cgroup, 
                                   description=('define the default convolution'
                                                ' width [in pixels]'))

# median-filter the template. we know that stellar features
#    are very broad. this avoids having spurious noise in our
#    templates [pixel]
MKTELLU_TEMP_MED_FILT = Const('MKTELLU_TEMP_MED_FILT', value=None, dtype=int,
                              source=__NAME__, group=cgroup, 
                              description=('median-filter the template. we '
                                           'know that stellar features are '
                                           'very broad. this avoids having '
                                           'spurious noise in our templates '
                                           '[pixel]'))

# Define the orders to plot (not too many)
#    values should be a string list separated by commas
MKTELLU_PLOT_ORDER_NUMS = Const('MKTELLU_PLOT_ORDER_NUMS', value=None,
                                dtype=str, source=__NAME__, group=cgroup, 
                                description=('Define the orders to plot '
                                             '(not too many) values should '
                                             'be a string list separated by '
                                             'commas'))

# Set an upper limit for the allowed line-of-sight optical depth of water
MKTELLU_TAU_WATER_ULIMIT = Const('MKTELLU_TAU_WATER_ULIMIT', value=None,
                                 dtype=float, source=__NAME__, group=cgroup, 
                                 description=('Set an upper limit for the '
                                              'allowed line-of-sight optical '
                                              'depth of water'))

#   Define the order to use for SNR check when accepting tellu files
#      to the telluDB
MKTELLU_QC_SNR_ORDER = Const('MKTELLU_QC_SNR_ORDER', value=None, dtype=int,
                             source=__NAME__, minimum=0, group=cgroup, 
                             description=('Define the order to use for SNR '
                                          'check when accepting tellu files '
                                          'to the telluDB'))

# Defines the maximum allowed value for the recovered water vapor optical
#    depth
MKTELLU_TRANS_MAX_WATERCOL = Const('MKTELLU_TRANS_MAX_WATERCOL', value=None,
                                   dtype=float, source=__NAME__, group=cgroup, 
                                   description=('Defines the maximum allowed '
                                                'value for the recovered water '
                                                'vapor optical depth'))

# Defines the minimum allowed value for the recovered water vapor optical
#    depth (should not be able 1)
MKTELLU_TRANS_MIN_WATERCOL = Const('MKTELLU_TRANS_MIN_WATERCOL', value=None,
                                   dtype=float, source=__NAME__, group=cgroup, 
                                   description=('Defines the minimum allowed '
                                                'value for the recovered water '
                                                'vapor optical depth (should '
                                                'not be able 1)'))

# minimum transmission required for use of a given pixel in the TAPAS
#    and SED fitting
MKTELLU_THRES_TRANSFIT = Const('MKTELLU_THRES_TRANSFIT', value=None,
                               dtype=float, source=__NAME__, group=cgroup, 
                               description=('minimum transmission required '
                                            'for use of a given pixel in the '
                                            'TAPAS and SED fitting'))

# Defines the bad pixels if the spectrum is larger than this value.
#    These values are likely an OH line or a cosmic ray
MKTELLU_TRANS_FIT_UPPER_BAD = Const('MKTELLU_TRANS_FIT_UPPER_BAD', value=None,
                                    dtype=float, source=__NAME__, group=cgroup, 
                                    description=('Defines the bad pixels if '
                                                 'the spectrum is larger '
                                                 'than this value. These '
                                                 'values are likely an OH line '
                                                 'or a cosmic ray'))

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
#      accepted to the telluDB
MKTELLU_QC_SNR_MIN = Const('MKTELLU_QC_SNR_MIN', value=None, dtype=float,
                           source=__NAME__, minimum=0.0, group=cgroup, 
                           description=('Define the minimum SNR for order '
                                        '"QC_TELLU_SNR_ORDER" that will be '
                                        'accepted to the telluDB'))

# Define the allowed difference between recovered and input airmass
MKTELLU_QC_AIRMASS_DIFF = Const('MKTELLU_QC_AIRMASS_DIFF', value=None,
                                dtype=float, source=__NAME__, group=cgroup, 
                                description=('Define the allowed difference '
                                             'between recovered and input '
                                             'airmass'))

# =============================================================================
# OBJECT: FIT TELLURIC SETTINGS
# =============================================================================
cgroup = 'OBJECT: FIT TELLURIC SETTINGS'

#   Define the order to use for SNR check when accepting tellu files
#      to the telluDB
FTELLU_QC_SNR_ORDER = Const('FTELLU_QC_SNR_ORDER', value=None, dtype=int,
                            source=__NAME__, minimum=0, group=cgroup, 
                            description=('Define the order to use for SNR '
                                         'check when accepting tellu files '
                                         'to the telluDB'))

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be
#      accepted to the telluDB
FTELLU_QC_SNR_MIN = Const('FTELLU_QC_SNR_MIN', value=None, dtype=float,
                          source=__NAME__, minimum=0.0, group=cgroup, 
                          description=('Define the minimum SNR for order '
                                       '"QC_TELLU_SNR_ORDER" that will be '
                                       'accepted to the telluDB'))

# The number of principle components to use in PCA fit
FTELLU_NUM_PRINCIPLE_COMP = Const('FTELLU_NUM_PRINCIPLE_COMP', value=None,
                                  dtype=int, source=__NAME__, minimum=1,
                                  user=True, active=False, group=cgroup,
                                  description='The number of principle '
                                              'components to use in PCA fit')

# The number of transmission files to use in the PCA fit (use this number of
#    trans files closest in expo_h20 and expo_water
FTELLU_NUM_TRANS = Const('FTELLU_NUM_TRANS', value=None, dtype=int,
                         source=__NAME__, minimum=1,
                         user=True, active=False, group=cgroup,
                         description='The number of transmission files to use '
                                     'in the PCA fit (use this number of '
                                     'trans files closest in expo_h20 and '
                                     'expo_water')

# Define whether to add the first derivative and broadening factor to the
#     principal components this allows a variable resolution and velocity
#     offset of the PCs this is performed in the pixel space and NOT the
#     velocity space as this is should be due to an instrument shift
FTELLU_ADD_DERIV_PC = Const('FTELLU_ADD_DERIV_PC', value=None, dtype=bool,
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
FTELLU_FIT_DERIV_PC = Const('FTELLU_FIT_DERIV_PC', value=None, dtype=bool,
                            source=__NAME__, user=True, active=False,
                            group=cgroup,
                            description='Define whether to fit the derivatives '
                                        'instead of the principal components')

# The number of pixels required (per order) to be able to interpolate the
#    template on to a berv shifted wavelength grid
FTELLU_FIT_KEEP_NUM = Const('FTELLU_FIT_KEEP_NUM', value=None, dtype=int,
                            source=__NAME__, group=cgroup, 
                            description=('The number of pixels required (per '
                                         'order) to be able to interpolate the '
                                         'template on to a berv shifted '
                                         'wavelength grid'))

# The minimium transmission allowed to define good pixels (for reconstructed
#    absorption calculation)
FTELLU_FIT_MIN_TRANS = Const('FTELLU_FIT_MIN_TRANS', value=None, dtype=float,
                             source=__NAME__, group=cgroup, 
                             description=('The minimium transmission allowed '
                                          'to define good pixels (for '
                                          'reconstructed absorption '
                                          'calculation)'))

# The minimum wavelength constraint (in nm) to calculate reconstructed
#     absorption
FTELLU_LAMBDA_MIN = Const('FTELLU_LAMBDA_MIN', value=None, dtype=float,
                          source=__NAME__, group=cgroup, 
                          description=('The minimum wavelength constraint '
                                       '(in nm) to calculate reconstructed '
                                       'absorption'))

# The maximum wavelength constraint (in nm) to calculate reconstructed
#     absorption
FTELLU_LAMBDA_MAX = Const('FTELLU_LAMBDA_MAX', value=None, dtype=float,
                          source=__NAME__, group=cgroup, 
                          description=('The maximum wavelength constraint '
                                       '(in nm) to calculate reconstructed '
                                       'absorption'))

# The gaussian kernel used to smooth the template and residual spectrum [km/s]
FTELLU_KERNEL_VSINI = Const('FTELLU_KERNEL_VSINI', value=None, dtype=float,
                            source=__NAME__, group=cgroup, 
                            description=('The gaussian kernel used to smooth '
                                         'the template and residual spectrum '
                                         '[km/s]'))

# The number of iterations to use in the reconstructed absorption calculation
FTELLU_FIT_ITERS = Const('FTELLU_FIT_ITERS', value=None, dtype=int,
                         source=__NAME__, group=cgroup, 
                         description=('The number of iterations to use in the '
                                      'reconstructed absorption calculation'))

# The minimum log absorption the is allowed in the molecular absorption
#     calculation
FTELLU_FIT_RECON_LIMIT = Const('FTELLU_FIT_RECON_LIMIT', value=None,
                               dtype=float, source=__NAME__, group=cgroup, 
                               description=('The minimum log absorption the is '
                                            'allowed in the molecular '
                                            'absorption calculation'))

# Define the orders to plot (not too many) for recon abso plot
#    values should be a string list separated by commas
FTELLU_PLOT_ORDER_NUMS = Const('FTELLU_PLOT_ORDER_NUMS', value=None,
                               dtype=str, source=__NAME__, group=cgroup, 
                               description=('Define the orders to plot (not '
                                            'too many) for recon abso plot '
                                            'values should be a string list '
                                            'separated by commas'))

# Define the selected fit telluric order for debug plots (when not in loop)
FTELLU_SPLOT_ORDER = Const('FTELLU_SPLOT_ORDER', value=None,
                           dtype=int, source=__NAME__, group=cgroup, 
                           description=('Define the selected fit telluric '
                                        'order for debug plots (when not in '
                                        'loop)'))

# =============================================================================
# OBJECT: MAKE TEMPLATE SETTINGS
# =============================================================================
cgroup = 'OBJECT: MAKE TEMPLATE SETTINGS'
# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input template files
TELLURIC_FILETYPE = Const('TELLURIC_FILETYPE', value=None, dtype=str,
                          source=__NAME__, user=True, active=False,
                          group=cgroup,
                          description='the OUTPUT type (KW_OUTPUT header key) '
                                      'and DrsFitsFile name required for input '
                                      'template files')

# the fiber required for input template files
TELLURIC_FIBER_TYPE = Const('TELLURIC_FIBER_TYPE', value=None, dtype=str,
                            source=__NAME__, user=True, active=False,
                            group=cgroup,
                            description='the fiber required for input '
                                        'template files')

# the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for
#   input template files
MKTEMPLATE_FILETYPE = Const('MKTEMPLATE_FILETYPE', value=None, dtype=str,
                            source=__NAME__, user=True, active=False,
                            group=cgroup,
                            description='the OUTPUT type (KW_OUTPUT header '
                                        'key) and DrsFitsFile name required '
                                        'for input template files')

# the fiber required for input template files
MKTEMPLATE_FIBER_TYPE = Const('MKTEMPLATE_FIBER_TYPE', value=None, dtype=str,
                              source=__NAME__, user=True, active=False,
                              group=cgroup,
                              description='the fiber required for input '
                                          'template files')

# the order to use for signal to noise cut requirement
MKTEMPLATE_FILESOURCE = Const('MKTEMPLATE_FILESOURCE', value=None, dtype=str,
                              source=__NAME__, group=cgroup,
                              options=['telludb', 'disk'], 
                              description=('the order to use for signal to '
                                           'noise cut requirement'))

# the order to use for signal to noise cut requirement
MKTEMPLATE_SNR_ORDER = Const('MKTEMPLATE_SNR_ORDER', value=None, dtype=int,
                             source=__NAME__, minimum=0, group=cgroup, 
                             description=('the order to use for signal to '
                                          'noise cut requirement'))

# The number of iterations to filter low frequency noise before medianing
#   the template "big cube" to the final template spectrum
MKTEMPLATE_E2DS_ITNUM = Const('MKTEMPLATE_E2DS_ITNUM', value=None, dtype=int,
                              source=__NAME__, minimum=1, group=cgroup, 
                              description=('The number of iterations to filter '
                                           'low frequency noise before '
                                           'medianing the template "big cube" '
                                           'to the final template spectrum'))

# The size (in pixels) to filter low frequency noise before medianing
#   the template "big cube" to the final template spectrum
MKTEMPLATE_E2DS_LOWF_SIZE = Const('MKTEMPLATE_E2DS_LOWF_SIZE', value=None,
                                  dtype=int, source=__NAME__, minimum=1,
                                  group=cgroup, 
                                  description=('The size (in pixels) to filter '
                                               'low frequency noise before '
                                               'medianing the template "big '
                                               'cube" to the final template '
                                               'spectrum'))

# The number of iterations to filter low frequency noise before medianing
#   the s1d template "big cube" to the final template spectrum
MKTEMPLATE_S1D_ITNUM = Const('MKTEMPLATE_S1D_ITNUM', value=None, dtype=int,
                             source=__NAME__, minimum=1, group=cgroup, 
                             description=('The number of iterations to filter '
                                          'low frequency noise before '
                                          'medianing the s1d template "big '
                                          'cube" to the final template '
                                          'spectrum'))

# The size (in pixels) to filter low frequency noise before medianing
#   the s1d template "big cube" to the final template spectrum
MKTEMPLATE_S1D_LOWF_SIZE = Const('MKTEMPLATE_S1D_LOWF_SIZE', value=None,
                                 dtype=int, source=__NAME__, minimum=1,
                                 group=cgroup, 
                                 description=('The size (in pixels) to filter '
                                              'low frequency noise before '
                                              'medianing the s1d template '
                                              '"big cube" to the final '
                                              'template spectrum'))

# Define the minimum allowed berv coverage to construct a template
#   in km/s  (default is double the resolution in km/s)
MKTEMPLATE_BERVCOR_QCMIN = Const('MKTEMPLATE_BERVCOR_QCMIN', value=None,
                                 dtype=float, source=__NAME__, minimum=0.0,
                                 group=cgroup, 
                                 description=('Define the minimum allowed berv '
                                              'coverage to construct a '
                                              'template in km/s (default '
                                              'is double the resolution in '
                                              'km/s)'))

# Define the core SNR in order to calculate required BERV coverage
MKTEMPLATE_BERVCOV_CSNR = Const('MKTEMPLATE_BERVCOV_CSNR', value=None,
                                dtype=float, source=__NAME__, minimum=0.0,
                                group=cgroup, 
                                description=('Define the core SNR in order to '
                                             'calculate required BERV '
                                             'coverage'))

# Defome the resolution in km/s for calculating BERV coverage
MKTEMPLATE_BERVCOV_RES = Const('MKTEMPLATE_BERVCOV_RES', value=None,
                               dtype=float, source=__NAME__, minimum=0.0,
                               group=cgroup, 
                               description=('Defome the resolution in km/s for '
                                            'calculating BERV coverage'))

# =============================================================================
# CALIBRATION: CCF SETTINGS
# =============================================================================
cgroup = 'CALIBRATION: CCF SETTINGS'
# Define the ccf mask path
CCF_MASK_PATH = Const('CCF_MASK_PATH', value=None, dtype=str, source=__NAME__,
                      group=cgroup)

# Define target rv the null value for CCF (only change if changing code)
CCF_NO_RV_VAL = Const('CCF_NO_RV_VAL', value=np.nan, dtype=float,
                      source=__NAME__, group=cgroup, 
                      description=('Define target rv the null value for CCF'
                                   ' (only change if changing code)'))

# Define target rv header null value
#     (values greater than absolute value are set to zero)
CCF_OBJRV_NULL_VAL = Const('CCF_OBJRV_NULL_VAL', value=1000, dtype=float,
                           source=__NAME__, group=cgroup, 
                           description=('Define target rv header null value '
                                        '(values greater than absolute value '
                                        'are set to zero)'))

# Define the default CCF MASK to use
CCF_DEFAULT_MASK = Const('CCF_DEFAULT_MASK', value=None, dtype=str,
                         source=__NAME__, user=True, active=False,
                         group=cgroup,
                         description='Define the default CCF MASK to use')

# Define the default CCF MASK normalisation mode
#   options are:
#     'None'         for no normalization
#     'all'          for normalization across all orders
#     'order'        for normalization for each order
CCF_MASK_NORMALIZATION = Const('CCF_MASK_NORMALIZATION', value=None,
                               dtype=str, options=['None', 'all', 'order'],
                               source=__NAME__, group=cgroup)

# Define the wavelength units for the mask
CCF_MASK_UNITS = Const('CCF_MASK_UNITS', value=None, dtype=str,
                       source=__NAME__,
                       options=['AA', 'Angstrom', 'nm', 'nanometer', 'um',
                                'micron', 'mm', 'millimeter', 'cm',
                                'centimeter', 'm', 'meter'],
                       user=True, active=False, group=cgroup,
                       description='Define the wavelength units for the mask')

# Define the CCF mask format (must be an astropy.table format)
CCF_MASK_FMT = Const('CCF_MASK_FMT', value=None, dtype=str, source=__NAME__,
                     group=cgroup)

#  Define the weight of the CCF mask (if 1 force all weights equal)
CCF_MASK_MIN_WEIGHT = Const('CCF_MASK_MIN_WEIGHT', value=None, dtype=float,
                            source=__NAME__, minimum=0.0, group=cgroup)

#  Define the width of the template line (if 0 use natural)
CCF_MASK_WIDTH = Const('CCF_MASK_WIDTH', value=None, dtype=float,
                       source=__NAME__, minimum=0.0, group=cgroup)

#  Define the maximum allowed ratio between input CCF STEP and CCF WIDTH
#     i.e. error will be generated if CCF_STEP > (CCF_WIDTH / RATIO)
CCF_MAX_CCF_WID_STEP_RATIO = Const('CCF_MAX_CCF_WID_STEP_RATIO', value=None,
                                   dtype=float, source=__NAME__, minimum=1.0,
                                   group=cgroup, 
                                   description=('Define the maximum allowed '
                                                'ratio between input CCF STEP '
                                                'and CCF WIDTH i.e. error will '
                                                'be generated if CCF_STEP > '
                                                '(CCF_WIDTH / RATIO)'))

# Define the width of the CCF range [km/s]
CCF_DEFAULT_WIDTH = Const('CCF_DEFAULT_WIDTH', value=None, dtype=float,
                          source=__NAME__, minimum=0.0,
                          user=True, active=False, group=cgroup,
                          description='Define the width of the CCF '
                                      'range [km/s]')

# Define the computations steps of the CCF [km/s]
CCF_DEFAULT_STEP = Const('CCF_DEFAULT_STEP', value=None, dtype=float,
                         source=__NAME__, minimum=0.0,
                         user=True, active=False, group=cgroup,
                         description='Define the computations steps of'
                                     ' the CCF [km/s]')

#   The value of the noise for wave dv rms calculation
#       snr = flux/sqrt(flux + noise^2)
CCF_NOISE_SIGDET = Const('CCF_NOISE_SIGDET', value=None, dtype=float,
                         source=__NAME__, minimum=0.0, group=cgroup)

#   The size around a saturated pixel to flag as unusable for wave dv rms
#      calculation
CCF_NOISE_BOXSIZE = Const('CCF_NOISE_BOXSIZE', value=None, dtype=int,
                          source=__NAME__, minimum=0.0, group=cgroup)

#   The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
CCF_NOISE_THRES = Const('CCF_NOISE_THRES', value=None, dtype=float,
                        source=__NAME__, minimum=0.0, group=cgroup)

#  Define the number of orders (from zero to ccf_num_orders_max) to use
#      to calculate the CCF and RV
CCF_N_ORD_MAX = Const('CCF_N_ORD_MAX', value=None, dtype=int, source=__NAME__,
                      minimum=1, group=cgroup)

# Allowed input DPRTYPES for input for CCF recipe
CCF_ALLOWED_DPRTYPES = Const('CCF_ALLOWED_DPRTYPES', value=None, dtype=str,
                             source=__NAME__, user=True, active=False,
                             group=cgroup,
                             description='Allowed input DPRTYPES for input '
                                         'for CCF recipe')

# Define the KW_OUTPUT types that are valid telluric corrected spectra
CCF_CORRECT_TELLU_TYPES = Const('CCF_CORRECT_TELLU_TYPES', value=None,
                                dtype=str, source=__NAME__, group=cgroup, 
                                description=('Define the KW_OUTPUT types that '
                                             'are valid telluric corrected '
                                             'spectra'))

# The transmission threshold for removing telluric domain (if and only if
#     we have a telluric corrected input file
CCF_TELLU_THRES = Const('CCF_TELLU_THRES', value=None, dtype=float,
                        source=__NAME__, group=cgroup, 
                        description=('The transmission threshold for removing '
                                     'telluric domain (if and only if we have'
                                     ' a telluric corrected input file'))

# The half size (in pixels) of the smoothing box used to calculate what value
#    should replace the NaNs in the E2ds before CCF is calculated
CCF_FILL_NAN_KERN_SIZE = Const('CCF_FILL_NAN_KERN_SIZE', value=None,
                               dtype=float, source=__NAME__, group=cgroup, 
                               description=('The half size (in pixels) of the '
                                            'smoothing box used to calculate '
                                            'what value should replace the '
                                            'NaNs in the E2ds before CCF is '
                                            'calculated'))

# the step size (in pixels) of the smoothing box used to calculate what value
#   should replace the NaNs in the E2ds before CCF is calculated
CCF_FILL_NAN_KERN_RES = Const('CCF_FILL_NAN_KERN_RES', value=None,
                              dtype=float, source=__NAME__, group=cgroup, 
                              description=('the step size (in pixels) of the '
                                           'smoothing box used to calculate '
                                           'what value should replace the '
                                           'NaNs in the E2ds before CCF is '
                                           'calculated'))

#  Define the detector noise to use in the ccf
CCF_DET_NOISE = Const('CCF_DET_NOISE', value=None, dtype=float, source=__NAME__,
                      group=cgroup, 
                      description=('Define the detector noise to use in '
                                   'the ccf'))

# Define the fit type for the CCF fit
#     if 0 then we have an absorption line
#     if 1 then we have an emission line
CCF_FIT_TYPE = Const('CCF_FIT_TYPE', value=None, dtype=int, source=__NAME__,
                     options=[0, 1], group=cgroup, 
                     description=('Define the fit type for the CCF fit if 0 '
                                  'then we have an absorption line if 1 then '
                                  'we have an emission line'))

# Define the percentile the blaze is normalised by before using in CCF calc
CCF_BLAZE_NORM_PERCENTILE = Const('CCF_BLAZE_NORM_PERCENTILE', value=None,
                                  dtype=float, source=__NAME__, minimum=0,
                                  maximum=100, group=cgroup, 
                                  description=('Define the percentile the '
                                               'blaze is normalised by before '
                                               'using in CCF calc'))

# =============================================================================
# GENERAL POLARISATION SETTINGS
# =============================================================================
cgroup = 'GENERAL POLARISATION SETTINGS'

# Define all possible fibers used for polarimetry
POLAR_FIBERS = Const('POLAR_FIBERS', value=None, dtype=str, source=__NAME__,
                     group=cgroup,
                     description='Define all possible fibers used for '
                                 'polarimetry')

# Define all possible stokes parameters
POLAR_STOKES_PARAMS = Const('POLAR_STOKES_PARAMS', value=None, dtype=str,
                            source=__NAME__, group=cgroup,
                            description='Define all possible stokes parameters')

# Whether or not to correct for BERV shift before calculate polarimetry
POLAR_BERV_CORRECT = Const('POLAR_BERV_CORRECT', value=None, dtype=bool,
                           source=__NAME__, group=cgroup,
                           description='Whether or not to correct for BERV '
                                       'shift before calculate polarimetry')

# Whether or not to correct for SOURCE RV shift before calculate polarimetry
POLAR_SOURCE_RV_CORRECT = Const('POLAR_SOURCE_RV_CORRECT', value=None,
                                dtype=bool, source=__NAME__, group=cgroup,
                                description='Whether or not to correct for '
                                            'SOURCE RV shift before calculate '
                                            'polarimetry')

#  Define the polarimetry method
#    currently must be either:
#         - Ratio
#         - Difference
POLAR_METHOD = Const('POLAR_METHOD', value=None, dtype=str, source=__NAME__,
                     group=cgroup,
                     description='Define the polarimetry method currently '
                                 'must be either: - Ratio - Difference')

# Whether or not to interpolate flux values to correct for wavelength
#   shifts between exposures
POLAR_INTERPOLATE_FLUX = Const('POLAR_INTERPOLATE_FLUX', value=None,
                               dtype=bool, source=__NAME__, group=cgroup,
                               description='Whether or not to interpolate flux '
                                           'values to correct for wavelength '
                                           'shifts between exposures')

# Select stokes I continuum detection algorithm:
#     'IRAF' or 'MOVING_MEDIAN'
STOKESI_CONTINUUM_DET_ALG = Const('STOKESI_CONTINUUM_DET_ALG', value=None,
                                  dtype=str, source=__NAME__, group=cgroup,
                                  options=['IRAF', 'MOVING_MEDIAN'],
                                  description='Select stokes I continuum '
                                              'detection algorithm: '
                                              'IRAF or MOVING_MEDIAN')

# Select stokes I continuum detection algorithm:
#     'IRAF' or 'MOVING_MEDIAN'
POLAR_CONTINUUM_DET_ALG = Const('POLAR_CONTINUUM_DET_ALG', value=None,
                                dtype=str, source=__NAME__, group=cgroup,
                                options=['IRAF', 'MOVING_MEDIAN'],
                                description='Select stokes I continuum '
                                            'detection algorithm: '
                                            'IRAF or MOVING_MEDIAN')

# Normalize Stokes I (True or False)
POLAR_NORMALIZE_STOKES_I = Const('POLAR_NORMALIZE_STOKES_I', value=None,
                                 dtype=bool, source=__NAME__, group=cgroup,
                                 description='Normalize Stokes I (True or '
                                             'False)')

# Remove continuum polarization
POLAR_REMOVE_CONTINUUM = Const('POLAR_REMOVE_CONTINUUM', value=None,
                               dtype=bool, source=__NAME__, group=cgroup,
                               description='Remove continuum polarization')

# Apply polarimetric sigma-clip cleanning (Works better if continuum
#     is removed)
POLAR_CLEAN_BY_SIGMA_CLIPPING = Const('POLAR_CLEAN_BY_SIGMA_CLIPPING',
                                      value=None, dtype=bool, source=__NAME__,
                                      group=cgroup,
                                      description='Apply polarimetric sigma-'
                                                  'clip cleanning (Works '
                                                  'better if continuum is '
                                                  'removed)')

# Define number of sigmas within which apply clipping
POLAR_NSIGMA_CLIPPING = Const('POLAR_NSIGMA_CLIPPING', value=None, dtype=float,
                              source=__NAME__, group=cgroup,
                              description='Define number of sigmas within '
                                          'which apply clipping')

# =============================================================================
# POLAR POLY MOVING MEDIAN SETTINGS
# =============================================================================
cgroup = 'POLAR POLY MOVING MEDIAN SETTINGS'

# Define the polarimetry continuum bin size
POLAR_CONT_BINSIZE = Const('POLAR_CONT_BINSIZE', value=None, dtype=int,
                           source=__NAME__, group=cgroup,
                           description='Define the polarimetry continuum bin '
                                       'size')
# Define the polarimetry continuum overlap size
POLAR_CONT_OVERLAP = Const('POLAR_CONT_OVERLAP', value=None, dtype=int,
                           source=__NAME__, group=cgroup,
                           description='Define the polarimetry continuum '
                                       'overlap size')

# Fit polynomial to continuum polarization?
#    If False it will use a cubic interpolation instead of polynomial fit
POLAR_CONT_POLYNOMIAL_FIT = Const('POLAR_CONT_POLYNOMIAL_FIT', value=None,
                                  dtype=bool, source=__NAME__, group=cgroup,
                                  description='Fit polynomial to continuum '
                                              'polarization? If False it will '
                                              'use a cubic interpolation '
                                              'instead of polynomial fit')

# Define degree of polynomial to fit continuum polarization
POLAR_CONT_DEG_POLYNOMIAL = Const('POLAR_CONT_DEG_POLYNOMIAL', value=None,
                                  dtype=int, source=__NAME__, group=cgroup,
                                  description='Define degree of polynomial to '
                                              'fit continuum polarization')

# =============================================================================
# POLAR IRAF SETTINGS
# =============================================================================
cgroup = 'POLAR IRAF SETTINGS'

# function to fit to the stokes I continuum: must be 'polynomial' or
#    'spline3'
STOKESI_IRAF_CONT_FIT_FUNC = Const('STOKESI_IRAF_CONT_FIT_FUNC', value=None,
                                   dtype=str, options=['polynomial', 'spline3'],
                                   source=__NAME__, group=cgroup,
                                   description='function to fit to the stokes '
                                               'I continuum must be polynomial '
                                               'or spline3')

# function to fit to the polar continuum: must be 'polynomial' or 'spline3'
POLAR_IRAF_CONT_FIT_FUNC = Const('POLAR_IRAF_CONT_FIT_FUNC', value=None,
                                 dtype=str, options=['polynomial', 'spline3'],
                                 source=__NAME__, group=cgroup,
                                 description='function to fit to the polar '
                                             'continuum: must be polynomial '
                                             'or spline3')

# stokes i continuum fit function order: 'polynomial': degree or 'spline3':
#    number of knots
STOKESI_IRAF_CONT_FUNC_ORDER = Const('STOKESI_IRAF_CONT_FUNC_ORDER',
                                     value=None, dtype=int,
                                   source=__NAME__, group=cgroup,
                                   description='polar continuum fit function '
                                               'order, polynomial: degree, '
                                               'spline3: number of knots')

# polar continuum fit function order: 'polynomial': degree or 'spline3':
#    number of knots
POLAR_IRAF_CONT_FUNC_ORDER = Const('POLAR_IRAF_CONT_FUNC_ORDER',
                                   value=None, dtype=int,
                                   source=__NAME__, group=cgroup,
                                   description='stokes i continuum fit function'
                                               ' order, polynomial: degree, '
                                               'spline3: number of knots')

# =============================================================================
# POLAR LSD SETTINGS
# =============================================================================
cgroup = 'POLAR LSD SETTINGS'

#  Define the spectral lsd mask directory for lsd polar calculations
POLAR_LSD_DIR = Const('POLAR_LSD_DIR', value=None, dtype=str, source=__NAME__,
                      group=cgroup,
                      description='Define the spectral lsd mask directory for '
                                  'lsd polar calculations')

#  Define the file regular expression key to lsd mask files
#  for "marcs_t3000g50_all" this should be:
#     - filekey = 'marcs_t*g
#  for "t4000_g4.0_m0.00" it should be:
#     - filekey = 't*_g'
POLAR_LSD_FILE_KEY = Const('POLAR_LSD_FILE_KEY',
                           value=None, dtype=str,
                           source=__NAME__, group=cgroup,
                           description='Define the file regular expression key '
                                       'to lsd mask files for '
                                       'marcs_t3000g50_all this should be: '
                                       'filekey = marcs_t*g for '
                                       't4000_g4.0_m0.00 it should be: filekey '
                                       '= t*_g')

# Define minimum lande of lines to be used in the LSD analyis
POLAR_LSD_MIN_LANDE = Const('POLAR_LSD_MIN_LANDE', value=None, dtype=float,
                            source=__NAME__, group=cgroup,
                            description='Define minimum lande of lines to be '
                                        'used in the LSD analyis')

# Define maximum lande of lines to be used in the LSD analyis
POLAR_LSD_MAX_LANDE = Const('POLAR_LSD_MAX_LANDE', value=None, dtype=float,
                            source=__NAME__, group=cgroup,
                            description='Define maximum lande of lines to be '
                                        'used in the LSD analyis')

# If mask lines are in air-wavelength then they will have to be
#     converted from air to vacuum
POLAR_LSD_CCFLINES_AIR_WAVE = Const('POLAR_LSD_CCFLINES_AIR_WAVE', value=None,
                                    dtype=bool, source=__NAME__, group=cgroup,
                                    description='If mask lines are in air-'
                                                'wavelength then they will '
                                                'have to be converted from air '
                                                'to vacuum')

# Define minimum line depth to be used in the LSD analyis
POLAR_LSD_MIN_LINEDEPTH = Const('POLAR_LSD_MIN_LINEDEPTH', value=None,
                                dtype=float, source=__NAME__, group=cgroup,
                                description='Define minimum line depth to be '
                                            'used in the LSD analyis')

# Define initial velocity (km/s) for output LSD profile
POLAR_LSD_V0 = Const('POLAR_LSD_V0',  value=None, dtype=float, source=__NAME__,
                     group=cgroup,
                     description='Define initial velocity (km/s) for output '
                                 'LSD profile')

#  Define final velocity (km/s) for output LSD profile
POLAR_LSD_VF =  Const('POLAR_LSD_VF', value=None, dtype=float, source=__NAME__,
                      group=cgroup,
                      description='Define final velocity (km/s) for output LSD '
                                  'profile')

# Define number of points for output LSD profile
POLAR_LSD_NP = Const('POLAR_LSD_NP', value=None, dtype=int, source=__NAME__,
                     group=cgroup,
                     description='Define number of points for output '
                                 'LSD profile')

# Renormalize data before LSD analysis
POLAR_LSD_NORMALIZE = Const('POLAR_LSD_NORMALIZE', value=None, dtype=bool,
                            source=__NAME__, group=cgroup,
                            description='Renormalize data before LSD analysis')

# Remove edges of LSD profile
POLAR_LSD_REMOVE_EDGES = Const('POLAR_LSD_REMOVE_EDGES',  value=None,
                               dtype=bool, source=__NAME__, group=cgroup,
                               description='Remove edges of LSD profile')

# Define the guess at the resolving power for lsd profile fit
POLAR_LSD_RES_POWER_GUESS = Const('POLAR_LSD_RES_POWER_GUESS', value=None,
                                  dtype=float, source=__NAME__, group=cgroup,
                                  description='Define the guess at the '
                                              'resolving power for lsd profile '
                                              'fit')

# =============================================================================
# DEBUG OUTPUT FILE SETTINGS
# =============================================================================
cgroup = 'DEBUG OUTPUT FILE SETTINGS'
# Whether to save background debug file (large 0.5 GB per file)
#   one of these per extraction (lots)
DEBUG_BACKGROUND_FILE = Const('DEBUG_BACKGROUND_FILE', value=True,
                              dtype=bool, source=__NAME__,
                              user=True, active=False, group=cgroup,
                              description='Whether to save background debug '
                                          'file (large 0.5 GB per file) one '
                                          'of these per extraction (lots)')

# Whether to save the E2DSLL file (around 0.05 to 0.1 GB per file)
#   one of these per fiber (lots)
DEBUG_E2DSLL_FILE = Const('DEBUG_E2DSLL_FILE', value=True,
                          dtype=bool, source=__NAME__,
                          user=True, active=False, group=cgroup,
                          description='Whether to save the E2DSLL file '
                                      '(around 0.05 to 0.1 GB per file) '
                                      'one of these per fiber (lots)')

# Whether to save the shape in and out debug files (around 0.1 GB per file)
#   but only one set of these per night
DEBUG_SHAPE_FILES = Const('DEBUG_SHAPE_FILES', value=True,
                              dtype=bool, source=__NAME__,
                              user=True, active=False, group=cgroup,
                              description='Whether to save the shape in and '
                                          'out debug files (around 0.1 GB per '
                                          'file) but only one set of these '
                                          'per night')

# Whether to save the uncorrected for FP C fiber leak files
#      (around 0.01 GB per file) one of these per fiber
DEBUG_UNCORR_EXT_FILES = Const('DEBUG_UNCORR_EXT_FILES', value=True,
                              dtype=bool, source=__NAME__,
                              user=True, active=False, group=cgroup,
                              description='Whether to save the uncorrected '
                                          'for FP C fiber leak files (around '
                                          '0.01 GB per file) one of these per '
                                          'fiber')


# =============================================================================
# DEBUG PLOT SETTINGS
# =============================================================================
cgroup = 'DEBUG PLOT SETTINGS'
# turn on dark image region debug plot
PLOT_DARK_IMAGE_REGIONS = Const('PLOT_DARK_IMAGE_REGIONS', value=False,
                                dtype=bool, source=__NAME__,
                                user=True, active=False, group=cgroup,
                                description='turn on dark image region '
                                            'debug plot')

# turn on dark histogram debug plot
PLOT_DARK_HISTOGRAM = Const('PLOT_DARK_HISTOGRAM', value=False, dtype=bool,
                            source=__NAME__, user=True, active=False,
                            group=cgroup,
                            description='turn on dark histogram debug plot')

# turn on badpix map debug plot
PLOT_BADPIX_MAP = Const('PLOT_BADPIX_MAP', value=False, dtype=bool,
                        source=__NAME__, user=True, active=False,
                        group=cgroup,
                        description='turn on badpix map debug plot')

# turn on the localisation cent min max debug plot
PLOT_LOC_MINMAX_CENTS = Const('PLOT_LOC_MINMAX_CENTS', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the localisation cent min '
                                          'max debug plot')

# turn on the localisation cent/thres debug plot
PLOT_LOC_MIN_CENTS_THRES = Const('PLOT_LOC_MIN_CENTS_THRES', value=False,
                                 dtype=bool, source=__NAME__, user=True,
                                 active=False, group=cgroup,
                                 description='turn on the localisation '
                                             'cent/thres debug plot')

# turn on the localisation finding orders debug plot
PLOT_LOC_FINDING_ORDERS = Const('PLOT_LOC_FINDING_ORDERS', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the localisation finding '
                                            'orders debug plot')

# turn on the image above saturation threshold debug plot
PLOT_LOC_IM_SAT_THRES = Const('PLOT_LOC_IM_SAT_THRES', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the image above saturation '
                                          'threshold debug plot')

# turn on the order number vs rms debug plot
PLOT_LOC_ORD_VS_RMS = Const('PLOT_LOC_ORD_VS_RMS', value=False,
                            dtype=bool, source=__NAME__, user=True,
                            active=False, group=cgroup,
                            description='turn on the order number vs '
                                        'rms debug plot')

# turn on the localisation check coeffs debug plot
PLOT_LOC_CHECK_COEFFS = Const('PLOT_LOC_CHECK_COEFFS', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the localisation check '
                                          'coeffs debug plot')

# turn on the localisation fit residuals plot (warning: done many times)
PLOT_LOC_FIT_RESIDUALS = Const('PLOT_LOC_FIT_RESIDUALS', value=False,
                               dtype=bool, source=__NAME__, user=True,
                               active=False, group=cgroup,
                               description='turn on the localisation fit '
                                           'residuals plot (warning: '
                                           'done many times)')

# turn on the shape dx debug plot
PLOT_SHAPE_DX = Const('PLOT_SHAPE_DX', value=False, dtype=bool, source=__NAME__,
                      user=True, active=False, group=cgroup,
                      description='turn on the shape dx debug plot')

# turn on the shape angle offset (all orders in loop) debug plot
PLOT_SHAPE_ANGLE_OFFSET_ALL = Const('PLOT_SHAPE_ANGLE_OFFSET_ALL', value=False,
                                    dtype=bool, source=__NAME__,
                                    user=True, active=False, group=cgroup,
                                    description='turn on the shape angle '
                                                'offset (all orders in loop) '
                                                'debug plot')

# turn on the shape angle offset (one selected order) debug plot
PLOT_SHAPE_ANGLE_OFFSET = Const('PLOT_SHAPE_ANGLE_OFFSET', value=False,
                                dtype=bool, source=__NAME__,
                                user=True, active=False, group=cgroup,
                                description='turn on the shape angle offset '
                                            '(one selected order) debug plot')

# turn on the shape local zoom plot
PLOT_SHAPEL_ZOOM_SHIFT = Const('PLOT_SHAPEL_ZOOM_SHIFT', value=False,
                               dtype=bool, source=__NAME__, user=True,
                               active=False, group=cgroup,
                               description='turn on the shape local zoom plot')

# turn on the shape linear transform params plot
PLOT_SHAPE_LINEAR_TPARAMS = Const('PLOT_SHAPE_LINEAR_TPARAMS', value=False,
                                  dtype=bool, source=__NAME__, user=True,
                                  active=False, group=cgroup,
                                  description='turn on the shape linear '
                                              'transform params plot')

# turn on the flat order fit edges debug plot (loop)
PLOT_FLAT_ORDER_FIT_EDGES1 = Const('PLOT_FLAT_ORDER_FIT_EDGES1', value=False,
                                   dtype=bool, source=__NAME__, user=True,
                                   active=False, group=cgroup,
                                   description='turn on the flat order fit '
                                               'edges debug plot (loop)')

# turn on the flat order fit edges debug plot (selected order)
PLOT_FLAT_ORDER_FIT_EDGES2 = Const('PLOT_FLAT_ORDER_FIT_EDGES2', value=False,
                                   dtype=bool, source=__NAME__, user=True,
                                   active=False, group=cgroup,
                                   description='turn on the flat order fit '
                                               'edges debug plot (selected '
                                               'order)')

# turn on the flat blaze order debug plot (loop)
PLOT_FLAT_BLAZE_ORDER1 = Const('PLOT_FLAT_BLAZE_ORDER1', value=False,
                               dtype=bool, source=__NAME__, user=True,
                               active=False, group=cgroup,
                               description='turn on the flat blaze order '
                                           'debug plot (loop)')

# turn on the flat blaze order debug plot (selected order)
PLOT_FLAT_BLAZE_ORDER2 = Const('PLOT_FLAT_BLAZE_ORDER2', value=False,
                               dtype=bool, source=__NAME__, user=True,
                               active=False, group=cgroup,
                               description='turn on the flat blaze order debug '
                                           'plot (selected order)')

# turn on thermal background (in extract) debug plot
PLOT_THERMAL_BACKGROUND = Const('PLOT_THERMAL_BACKGROUND', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on thermal background '
                                            '(in extract) debug plot')

# turn on the extraction spectral order debug plot (loop)
PLOT_EXTRACT_SPECTRAL_ORDER1 = Const('PLOT_EXTRACT_SPECTRAL_ORDER1',
                                     value=False, dtype=bool, source=__NAME__,
                                     user=True, active=False, group=cgroup,
                                     description='turn on the extraction '
                                                 'spectral order debug plot '
                                                 '(loop)')

# turn on the extraction spectral order debug plot (selected order)
PLOT_EXTRACT_SPECTRAL_ORDER2 = Const('PLOT_EXTRACT_SPECTRAL_ORDER2',
                                     value=False, dtype=bool, source=__NAME__,
                                     user=True, active=False, group=cgroup,
                                     description='turn on the extraction '
                                                 'spectral order debug plot '
                                                 '(selected order)')

# turn on the extraction 1d spectrum debug plot
PLOT_EXTRACT_S1D = Const('PLOT_EXTRACT_S1D', value=False, dtype=bool,
                         source=__NAME__, user=True, active=False, group=cgroup,
                         description='turn on the extraction 1d spectrum'
                                     ' debug plot')

# turn on the extraction 1d spectrum weight (before/after) debug plot
PLOT_EXTRACT_S1D_WEIGHT = Const('PLOT_EXTRACT_S1D_WEIGHT', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the extraction 1d spectrum'
                                            ' weight (before/after) debug plot')


# turn on the wave line fiber comparison plot
PLOT_WAVE_FIBER_COMPARISON = Const('PLOT_WAVE_FIBER_COMPARISON', value=False,
                                   dtype=bool, source=__NAME__, user=True,
                                   active=False, group=cgroup,
                                   description='turn on the wave line fiber '
                                               'comparison plot')

# turn on the wave line fiber comparison plot
PLOT_WAVE_FIBER_COMP = Const('PLOT_WAVE_FIBER_COMP', value=False,
                             dtype=bool, source=__NAME__, user=True,
                             active=False, group=cgroup,
                             description='turn on the wave line fiber '
                                         'comp plot')

# turn on the wave length vs cavity width plot
PLOT_WAVE_WL_CAV = Const('PLOT_WAVE_WL_CAV_PLOT', value=False,
                         dtype=bool, source=__NAME__, user=True,
                         active=False, group=cgroup,
                         description='turn on the wave length vs cavity '
                                     'width plot')

# turn on the wave diff HC histograms plot
PLOT_WAVE_HC_DIFF_HIST = Const('PLOT_WAVE_HC_DIFF_HIST', value=False,
                         dtype=bool, source=__NAME__, user=True,
                         active=False, group=cgroup,
                         description='turn on the wave diff HC histograms plot')

# TODO: WAVE plots need sorting

# turn on the wave solution hc guess debug plot (in loop)
PLOT_WAVE_HC_GUESS = Const('PLOT_WAVE_HC_GUESS', value=False,
                           dtype=bool, source=__NAME__, user=True, active=False,
                           group=cgroup,
                           description='turn on the wave solution hc guess '
                                       'debug plot (in loop)')

# turn on the wave solution hc brightest lines debug plot
PLOT_WAVE_HC_BRIGHTEST_LINES = Const('PLOT_WAVE_HC_BRIGHTEST_LINES',
                                     value=False, dtype=bool, source=__NAME__,
                                     user=True, active=False, group=cgroup,
                                     description='turn on the wave solution hc '
                                                 'brightest lines debug plot')

# turn on the wave solution hc triplet fit grid debug plot
PLOT_WAVE_HC_TFIT_GRID = Const('PLOT_WAVE_HC_TFIT_GRID', value=False,
                               dtype=bool, source=__NAME__, user=True,
                               active=False, group=cgroup,
                               description='turn on the wave solution hc '
                                           'triplet fit grid debug plot')

# turn on the wave solution hc resolution map debug plot
PLOT_WAVE_RESMAP = Const('PLOT_WAVE_RESMAP', value=False,
                         dtype=bool, source=__NAME__, user=True,
                         active=False, group=cgroup,
                         description='turn on the wave solution hc '
                                     'resolution map debug plot')

# turn on the wave solution hc resolution map debug plot
PLOT_WAVE_HC_RESMAP = Const('PLOT_WAVE_HC_RESMAP', value=False,
                            dtype=bool, source=__NAME__, user=True,
                            active=False, group=cgroup,
                            description='turn on the wave solution hc '
                                        'resolution map debug plot')

# turn on the wave solution littrow check debug plot
PLOT_WAVE_LITTROW_CHECK1 = Const('PLOT_WAVE_LITTROW_CHECK1', value=False,
                                 dtype=bool, source=__NAME__, user=True,
                                 active=False, group=cgroup,
                                 description='turn on the wave solution littrow'
                                             ' check debug plot')

# turn on the wave solution littrow extrapolation debug plot
PLOT_WAVE_LITTROW_EXTRAP1 = Const('PLOT_WAVE_LITTROW_EXTRAP1', value=False,
                                  dtype=bool, source=__NAME__, user=True,
                                  active=False, group=cgroup,
                                  description='turn on the wave solution '
                                              'littrow extrapolation '
                                              'debug plot')

# turn on the wave solution littrow check debug plot
PLOT_WAVE_LITTROW_CHECK2 = Const('PLOT_WAVE_LITTROW_CHECK2', value=False,
                                 dtype=bool, source=__NAME__, user=True,
                                 active=False, group=cgroup,
                                 description='turn on the wave solution '
                                             'littrow check debug plot')

# turn on the wave solution littrow extrapolation debug plot
PLOT_WAVE_LITTROW_EXTRAP2 = Const('PLOT_WAVE_LITTROW_EXTRAP2', value=False,
                                  dtype=bool, source=__NAME__, user=True,
                                  active=False, group=cgroup,
                                  description='turn on the wave solution '
                                              'littrow extrapolation debug '
                                              'plot')

# turn on the wave solution final fp order debug plot
PLOT_WAVE_FP_FINAL_ORDER = Const('PLOT_WAVE_FP_FINAL_ORDER', value=False,
                                 dtype=bool, source=__NAME__, user=True,
                                 active=False, group=cgroup,
                                 description='turn on the wave solution final '
                                             'fp order debug plot')

# turn on the wave solution fp local width offset debug plot
PLOT_WAVE_FP_LWID_OFFSET = Const('PLOT_WAVE_FP_LWID_OFFSET', value=False,
                                 dtype=bool, source=__NAME__, user=True,
                                 active=False, group=cgroup,
                                 description='turn on the wave solution fp '
                                             'local width offset debug plot')

# turn on the wave solution fp wave residual debug plot
PLOT_WAVE_FP_WAVE_RES = Const('PLOT_WAVE_FP_WAVE_RES', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the wave solution fp wave '
                                          'residual debug plot')

# turn on the wave solution fp fp_m_x residual debug plot
PLOT_WAVE_FP_M_X_RES = Const('PLOT_WAVE_FP_M_X_RES', value=False,
                             dtype=bool, source=__NAME__, user=True,
                             active=False, group=cgroup,
                             description='turn on the wave solution fp '
                                         'fp_m_x residual debug plot')

# turn on the wave solution fp interp cavity width 1/m_d hc debug plot
PLOT_WAVE_FP_IPT_CWID_1MHC = Const('PLOT_WAVE_FP_IPT_CWID_1MHC', value=False,
                                   dtype=bool, source=__NAME__, user=True,
                                   active=False, group=cgroup,
                                   description='turn on the wave solution fp '
                                               'interp cavity width 1/m_d hc '
                                               'debug plot')

# turn on the wave solution fp interp cavity width ll hc and fp debug plot
PLOT_WAVE_FP_IPT_CWID_LLHC = Const('PLOT_WAVE_FP_IPT_CWID_LLHC', value=False,
                                   dtype=bool, source=__NAME__, user=True,
                                   active=False, group=cgroup,
                                   description='turn on the wave solution fp '
                                               'interp cavity width ll hc and '
                                               'fp debug plot')

# turn on the wave solution old vs new wavelength difference debug plot
PLOT_WAVE_FP_LL_DIFF = Const('PLOT_WAVE_FP_LL_DIFF', value=False, dtype=bool,
                             source=__NAME__, user=True, active=False,
                             group=cgroup,
                             description='turn on the wave solution old vs '
                                         'new wavelength difference debug plot')

# turn on the wave solution fp multi order debug plot
PLOT_WAVE_FP_MULTI_ORDER = Const('PLOT_WAVE_FP_MULTI_ORDER', value=False,
                                 dtype=bool, source=__NAME__, user=True,
                                 active=False, group=cgroup,
                                 description='turn on the wave solution fp '
                                             'multi order debug plot')

# turn on the wave solution fp single order debug plot
PLOT_WAVE_FP_SINGLE_ORDER = Const('PLOT_WAVE_FP_SINGLE_ORDER', value=False,
                                  dtype=bool, source=__NAME__, user=True,
                                  active=False, group=cgroup,
                                  description='turn on the wave solution fp '
                                              'single order debug plot')

# turn on the wave lines hc/fp expected vs measured debug plot
#  (will plot once for hc once for fp)
PLOT_WAVEREF_EXPECTED = Const('PLOT_WAVEREF_EXPECTED', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the wave lines hc/fp '
                                          'expected vs measured debug plot'
                                          '(will plot once for hc once for fp)')

# turn on the wave per night iteration debug plot
PLOT_WAVENIGHT_ITERPLOT = Const('PLOT_WAVENIGHT_ITERPLOT', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the wave per night '
                                            'iteration debug plot')

# turn on the wave per night hist debug plot
PLOT_WAVENIGHT_HISTPLOT = Const('PLOT_WAVENIGHT_HISTPLOT', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the wave per night '
                                            'hist debug plot')

# turn on the telluric pre-cleaning ccf debug plot
PLOT_TELLUP_WAVE_TRANS = Const('PLOT_TELLUP_WAVE_TRANS', value=False,
                               dtype=bool, source=__NAME__, user=True,
                               active=False, group=cgroup,
                               description='turn on the telluric pre-cleaning '
                                           'ccf debug plot')

# turn on the telluric pre-cleaning result debug plot
PLOT_TELLUP_ABSO_SPEC = Const('PLOT_TELLUP_ABSO_SPEC', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the telluric pre-cleaning '
                                          'result debug plot')

# turn on the telluric OH cleaning debug plot
PLOT_TELLUP_CLEAN_OH = Const('PLOT_TELLUP_CLEAN_OH', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the telluric OH cleaning '
                                          'debug plot')

# turn on the make tellu wave flux debug plot (in loop)
PLOT_MKTELLU_WAVE_FLUX1 = Const('PLOT_MKTELLU_WAVE_FLUX1', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the make tellu wave flux '
                                            'debug plot (in loop)')

# turn on the make tellu wave flux debug plot (single order)
PLOT_MKTELLU_WAVE_FLUX2 = Const('PLOT_MKTELLU_WAVE_FLUX2', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the make tellu wave flux '
                                            'debug plot (single order)')

# turn on the fit tellu pca component debug plot (in loop)
PLOT_FTELLU_PCA_COMP1 = Const('PLOT_FTELLU_PCA_COMP1', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the fit tellu pca component'
                                          ' debug plot (in loop)')

# turn on the fit tellu pca component debug plot (single order)
PLOT_FTELLU_PCA_COMP2 = Const('PLOT_FTELLU_PCA_COMP2', value=False,
                              dtype=bool, source=__NAME__, user=True,
                              active=False, group=cgroup,
                              description='turn on the fit tellu pca component '
                                          'debug plot (single order)')

# turn on the fit tellu reconstructed spline debug plot (in loop)
PLOT_FTELLU_RECON_SPLINE1 = Const('PLOT_FTELLU_RECON_SPLINE1', value=False,
                                  dtype=bool, source=__NAME__, user=True,
                                  active=False, group=cgroup,
                                  description='turn on the fit tellu '
                                              'reconstructed spline debug '
                                              'plot (in loop)')

# turn on the fit tellu reconstructed spline debug plot (single order)
PLOT_FTELLU_RECON_SPLINE2 = Const('PLOT_FTELLU_RECON_SPLINE2', value=False,
                                  dtype=bool, source=__NAME__, user=True,
                                  active=False, group=cgroup,
                                  description='turn on the fit tellu '
                                              'reconstructed spline debug '
                                              'plot (single order)')

# turn on the fit tellu wave shift debug plot (in loop)
PLOT_FTELLU_WAVE_SHIFT1 = Const('PLOT_FTELLU_WAVE_SHIFT1', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the fit tellu wave shift'
                                            ' debug plot (in loop)')

# turn on the fit tellu wave shift debug plot (single order)
PLOT_FTELLU_WAVE_SHIFT2 = Const('PLOT_FTELLU_WAVE_SHIFT2', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the fit tellu wave shift '
                                            'debug plot (single order)')

# turn on the fit tellu reconstructed absorption debug plot (in loop)
PLOT_FTELLU_RECON_ABSO1 = Const('PLOT_FTELLU_RECON_ABSO1', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the fit tellu '
                                            'reconstructed absorption debug '
                                            'plot (in loop)')

# turn on the fit tellu reconstructed absorption debug plot (single order)
PLOT_FTELLU_RECON_ABSO2 = Const('PLOT_FTELLU_RECON_ABSO12', value=False,
                                dtype=bool, source=__NAME__, user=True,
                                active=False, group=cgroup,
                                description='turn on the fit tellu '
                                            'reconstructed absorption debug '
                                            'plot (single order)')

# turn on the berv coverage debug plot
PLOT_MKTEMP_BERV_COV = Const('PLOT_MKTEMP_BERV_COV', value=False,
                             dtype=bool, source=__NAME__, user=True,
                             active=False, group=cgroup,
                             description='turn on the berv coverage '
                                         'debug plot')

# turn on the ccf rv fit debug plot (in a loop around orders)
PLOT_CCF_RV_FIT_LOOP = Const('PLOT_CCF_RV_FIT_LOOP', value=False,
                             dtype=bool, source=__NAME__, user=True,
                             active=False, group=cgroup,
                             description='turn on the ccf rv fit debug '
                                         'plot (in a loop around orders)')

# turn on the ccf rv fit debug plot (for the mean order value)
PLOT_CCF_RV_FIT = Const('PLOT_CCF_RV_FIT', value=False,
                        dtype=bool, source=__NAME__, user=True, active=False,
                        group=cgroup,
                        description='turn on the ccf rv fit debug plot '
                                    '(for the mean order value)')

# turn on the ccf spectral order vs wavelength debug plot
PLOT_CCF_SWAVE_REF = Const('PLOT_CCF_SWAVE_REF', value=False,
                           dtype=bool, source=__NAME__, user=True, active=False,
                           group=cgroup,
                           description='turn on the ccf spectral order vs '
                                       'wavelength debug plot')

# turn on the ccf photon uncertainty debug plot
PLOT_CCF_PHOTON_UNCERT = Const('PLOT_CCF_PHOTON_UNCERT', value=False,
                               dtype=bool, source=__NAME__, user=True,
                               active=False, group=cgroup,
                               description='turn on the ccf photon uncertainty '
                                           'debug plot')


# turn on the polar fit continuum plot
PLOT_POLAR_FIT_CONT = Const('PLOT_POLAR_FIT_CONT', value=False,
                            dtype=bool, source=__NAME__, user=True,
                            active=False, group=cgroup,
                            description='turn on the polar fit continuum '
                                        'plot')

# turn on the polar continuum debug plot
PLOT_POLAR_CONTINUUM = Const('PLOT_POLAR_CONTINUUM', value=False,
                             dtype=bool, source=__NAME__, user=True,
                             active=False, group=cgroup,
                             description='turn on the polar continuum '
                                         'debug plot')

# turn on the polar results debug plot
PLOT_POLAR_RESULTS = Const('PLOT_POLAR_RESULTS', value=False,
                           dtype=bool, source=__NAME__, user=True, active=False,
                           group=cgroup,
                           description='turn on the polar results debug plot')

# turn on the polar stokes i debug plot
PLOT_POLAR_STOKES_I = Const('PLOT_POLAR_STOKES_I', value=False,
                            dtype=bool, source=__NAME__, user=True,
                            active=False, group=cgroup,
                            description='turn on the polar stokes i debug plot')

# turn on the polar lsd debug plot
PLOT_POLAR_LSD = Const('PLOT_POLAR_LSD', value=False,
                       dtype=bool, source=__NAME__, user=True, active=False,
                       group=cgroup,
                       description='turn on the polar lsd debug plot')

# =============================================================================
# POST PROCESS SETTINGS
# =============================================================================
cgroup = 'POST PROCESS SETTINGS'
# Define whether (by deafult) to clear reduced directory
POST_CLEAR_REDUCED = Const('POST_CLEAR_REDUCED', value=False,
                           dtype=bool, source=__NAME__, user=True, active=True,
                           group=cgroup,
                           description='Define whether (by deafult) to '
                                       'clear reduced directory')

# Define whether (by default) to overwrite post processed files
POST_OVERWRITE = Const('POST_OVERWRITE', value=False,
                       dtype=bool, source=__NAME__, user=True, active=True,
                       group=cgroup,
                       description='Define whether (by default) to '
                                   'overwrite post processed files')

# Define the header keyword store to insert extension comment after
POST_HDREXT_COMMENT_KEY = Const('POST_HDREXT_COMMENT_KEY', value=None,
                                dtype=str, source=__NAME__, user=False,
                                active=False, group=cgroup,
                                description='Define the header keyword store '
                                            'to insert extension comment after')

# =============================================================================
# TOOLS SETTINGS
# =============================================================================
cgroup = 'TOOLS SETTING'

# Define whether to use multiprocess Pool or Process
REPROCESS_MP_TYPE = Const('REPROCESS_MP_TYPE', value=None, dtype=str,
                          source=__NAME__, group=cgroup,
                          user=True, active=True,
                          options=['pool', 'process'],
                          description='Define whether to use multiprocess '
                                      '"pool" or "process"')

# Key for use in run files
REPROCESS_RUN_KEY = Const('REPROCESS_RUN_KEY', value=None, dtype=str,
                          source=__NAME__, group=cgroup,
                          description='Key for use in run files')

# Define the obs_dir column name for raw file table
REPROCESS_OBSDIR_COL = Const('REPROCESS_OBSDIR_COL', value=None, dtype=str,
                           source=__NAME__, group=cgroup, 
                           description=('Define the obs_dir column name '
                                        'for raw file table'))

# Define the pi name column name for raw file table
REPROCESS_PINAMECOL = Const('REPROCESS_PINAMECOL', value=None, dtype=str,
                            source=__NAME__, group=cgroup, 
                            description=('Define the pi name column name for '
                                         'raw file table'))

# Define the absolute file column name for raw file table
REPROCESS_ABSFILECOL = Const('REPROCESS_ABSFILECOL', value=None, dtype=str,
                             source=__NAME__, group=cgroup, 
                             description=('Define the absolute file column '
                                          'name for raw file table'))

# Define the modified file column name for raw file table
REPROCESS_MODIFIEDCOL = Const('REPROCESS_MODIFIEDCOL', value=None, dtype=str,
                              source=__NAME__, group=cgroup, 
                              description=('Define the modified file column '
                                           'name for raw file table'))

# Define the sort column (from header keywords) for raw file table
REPROCESS_SORTCOL_HDRKEY = Const('REPROCESS_SORTCOL_HDRKEY', value=None,
                                 dtype=str, source=__NAME__, group=cgroup, 
                                 description=('Define the sort column (from '
                                              'header keywords) for raw file '
                                              'table'))

# Define the raw index filename
REPROCESS_RAWINDEXFILE = Const('REPROCESS_RAWINDEXFILE', value=None, dtype=str,
                               source=__NAME__, group=cgroup,
                               description='Define the raw index filename')

# define the sequence (1 of 5, 2 of 5 etc) col for raw file table
REPROCESS_SEQCOL = Const('REPROCESS_SEQCOL', value=None, dtype=str,
                         source=__NAME__, group=cgroup, 
                         description=('define the sequence (1 of 5, 2 of 5 '
                                      'etc) col for raw file table'))

# define the time col for raw file table
REPROCESS_TIMECOL = Const('REPROCESS_TIMECOL', value=None, dtype=str,
                          source=__NAME__, group=cgroup, 
                          description=('define the time col for raw file '
                                       'table'))


# define the dprtypes for objects (for getting non telluric stars)
REPROCESS_OBJ_DPRTYPES = Const('REPROCESS_OBJ_DPRTYPES', value=None, dtype=str,
                               source=__NAME__, group=cgroup,
                               description=('define the dprtypes for objects '
                                            '(for getting non telluric stars)'))

# define the default database to remake
REMAKE_DATABASE_DEFAULT = Const('REMAKE_DATABASE_DEFAULT', value='calibration',
                                dtype=str, source=__NAME__, group=cgroup, 
                                description=('define the default database to '
                                             'remake'))

# Define whether we try to create a latex summary pdf
#   (turn this off if you have any problems with latex/pdflatex)
SUMMARY_LATEX_PDF = Const('SUMMARY_LATEX_PDF', value=True, dtype=bool,
                          source=__NAME__, group=cgroup, active=False,
                          user=True,
                          description='Define whether we try to create a latex '
                                      'summary pdf (turn this off if you have '
                                      'any problems with latex/pdflatex)')

# Define exposure meter minimum wavelength for mask
EXPMETER_MIN_LAMBDA = Const('EXPMETER_MIN_LAMBDA', value=None, dtype=float,
                            source=__NAME__, group=cgroup, 
                            description=('Define exposure meter minimum '
                                         'wavelength for mask'))

# Define exposure meter maximum wavelength for mask
EXPMETER_MAX_LAMBDA = Const('EXPMETER_MAX_LAMBDA', value=None, dtype=float,
                            source=__NAME__, group=cgroup, 
                            description=('Define exposure meter maximum '
                                         'wavelength for mask'))

# Define exposure meter telluric threshold (minimum tapas transmission)
EXPMETER_TELLU_THRES = Const('EXPMETER_TELLU_THRES', value=None, dtype=float,
                             source=__NAME__, group=cgroup, 
                             description=('Define exposure meter telluric '
                                          'threshold (minimum tapas '
                                          'transmission)'))

# Define the types of file allowed for drift measurement
DRIFT_DPRTYPES = Const('DRIFT_DPRTYPES', value=None, dtype=str,
                       source=__NAME__, group=cgroup, 
                       description=('Define the types of file allowed for '
                                    'drift measurement'))

# Define the fiber dprtype allowed for drift measurement (only FP)
DRIFT_DPR_FIBER_TYPE = Const('DRIFT_DPR_FIBER_TYPE', value=None, dtype=str,
                             source=__NAME__, group=cgroup, 
                             description=('Define the fiber dprtype allowed '
                                          'for drift measurement (only FP)'))

# =============================================================================
#  End of configuration file
# =============================================================================
