# This is the main config file
from apero.core.constants import constant_functions

# -----------------------------------------------------------------------------
# Define variables
# -----------------------------------------------------------------------------
# all definition
__all__ = [  # input keys
    'KW_ACQTIME', 'KW_OBJRA', 'KW_OBJDEC', 'KW_OBJNAME', 'KW_OBJEQUIN',
    'KW_OBJRAPM', 'KW_OBJDECPM', 'KW_RDNOISE', 'KW_GAIN', 'KW_EXPTIME',
    'KW_UTC_OBS', 'KW_EXPTIME_UNITS', 'KW_OBSTYPE', 'KW_CCAS',
    'KW_CREF', 'KW_CDEN', 'KW_CMMTSEQ', 'KW_AIRMASS', 'KW_MJDEND',
    'KW_CMPLTEXP', 'KW_NEXP', 'KW_PI_NAME', 'KW_PLX', 'KW_CALIBWH',
    'KW_TARGET_TYPE', 'KW_WEATHER_TOWER_TEMP', 'KW_CASS_TEMP',
    'KW_HUMIDITY', 'KW_GAIA_ID', 'KW_INPUTRV', 'KW_OBJ_TEMP',
    'KW_SATURATE', 'KW_FRMTIME', 'KW_OBJECTNAME',
    # general output keys
    'KW_VERSION', 'KW_PPVERSION', 'KW_DPRTYPE', 'KW_PID',
    'KW_INFILE1', 'KW_INFILE2', 'KW_INFILE3',
    'KW_DRS_QC', 'KW_DRS_QC_VAL', 'KW_DRS_QC_NAME', 'KW_DRS_QC_LOGIC',
    'KW_DRS_QC_PASS', 'KW_DATE_OBS', 'KW_OUTPUT',
    'KW_DRS_DATE', 'KW_C_FLIP', 'KW_C_CVRTE',
    'KW_C_RESIZE', 'KW_DRS_DATE_NOW', 'KW_C_FTYPE',
    'KW_MID_OBS_TIME', 'KW_MID_OBSTIME_METHOD',
    # calibration file header keys
    'KW_CDBDARK', 'KW_CDBBAD', 'KW_CDBBACK', 'KW_CDBORDP', 'KW_CDBLOCO',
    'KW_CDBSHAPEL', 'KW_CDBSHAPEDX', 'KW_CDBSHAPEDY', 'KW_CDBFLAT',
    'KW_CDBBLAZE', 'KW_CDBWAVE', 'KW_CDBTHERMAL',
    # preprocess keys
    'KW_PPSHIFTX', 'KW_PPSHIFTY', 'KW_PPMSTR_NSIG', 'KW_PPMSTR_FILE',
    # dark keys
    'KW_DARK_DEAD', 'KW_DARK_MED', 'KW_DARK_B_DEAD',
    'KW_DARK_B_MED', 'KW_DARK_R_DEAD', 'KW_DARK_R_MED', 'KW_DARK_CUT',
    # bad pix keys
    'KW_BHOT', 'KW_BBFLAT', 'KW_BNDARK', 'KW_BNFLAT', 'KW_BBAD',
    'KW_BNILUM', 'KW_BTOT',
    # loc keys
    'ROOT_DRS_LOC', 'KW_LOC_BCKGRD',
    'KW_LOC_NBO', 'KW_LOC_DEG_C', 'KW_LOC_DEG_W', 'KW_LOC_MAXFLX',
    'KW_LOC_SMAXPTS_CTR', 'KW_LOC_SMAXPTS_WID', 'KW_LOC_RMS_CTR',
    'KW_LOC_RMS_WID', 'KW_LOC_CTR_COEFF', 'KW_LOC_WID_COEFF',
    # shape keys
    'KW_SHAPE_DX', 'KW_SHAPE_DY', 'KW_SHAPE_A', 'KW_SHAPE_B',
    'KW_SHAPE_C', 'KW_SHAPE_D',
    # flat values
    'KW_BLAZE_WID', 'KW_BLAZE_CUT', 'KW_BLAZE_DEG', 'KW_BLAZE_SCUT',
    'KW_BLAZE_SIGFIG', 'KW_BLAZE_BPRCNTL', 'KW_BLAZE_NITER',
    # extraction values
    'KW_EXT_TYPE', 'KW_EXT_SNR', 'KW_EXT_START', 'KW_EXT_END',
    'KW_EXT_RANGE1', 'KW_EXT_RANGE2', 'KW_COSMIC', 'KW_COSMIC_CUT',
    'KW_COSMIC_THRES', 'KW_SAT_QC', 'KW_SAT_LEVEL', 'KW_S1D_WAVESTART',
    'KW_S1D_WAVEEND', 'KW_S1D_KIND', 'KW_S1D_BWAVE', 'KW_S1D_BVELO',
    'KW_S1D_SMOOTH', 'KW_S1D_BLAZET', 'KW_BERVRA', 'KW_BERVDEC',
    'KW_BERVEPOCH', 'KW_BERVPMRA', 'KW_BERVPMDE', 'KW_BERVPLX',
    'KW_BERV_POS_SOURCE', 'KW_BERVLAT', 'KW_BERVLONG', 'KW_BERVALT',
    'KW_BERV', 'KW_BJD', 'KW_BERVMAX', 'KW_BERVSOURCE',
    'KW_BERV_EST', 'KW_BJD_EST', 'KW_BERVMAX_EST',
    'KW_BERV_OBSTIME', 'KW_BERV_OBSTIME_METHOD',
    'KW_BERVGAIA_ID', 'KW_FIBER', 'KW_BERVOBJNAME', 'KW_BERVRV',
    'KW_BERV_GAIA_GMAG', 'KW_BERV_GAIA_BPMAG', 'KW_BERV_GAIA_RPMAG',
    'KW_BERV_GAIA_MAGLIM', 'KW_BERV_GAIA_PLXLIM', 'KW_DBERV',
    'KW_DBERV_EST',
    # leakage values
    'KW_LEAK_CORR', 'KW_LEAK_BP_U', 'KW_LEAK_NP_U', 'KW_LEAK_WSMOOTH',
    'KW_LEAK_KERSIZE', 'KW_LEAK_LP_U', 'KW_LEAK_UP_U', 'KW_LEAK_BADR_U',
    # wave values
    'KW_WAVE_NBO', 'KW_WAVE_DEG', 'KW_WAVEFILE', 'KW_WAVESOURCE',
    'KW_WAVECOEFFS', 'KW_WAVE_FITDEG', 'KW_WAVE_MODE_HC',
    'KW_WAVE_MODE_FP', 'KW_WAVE_ECHELLE_START', 'KW_WAVE_HCG_WSIZE',
    'KW_WAVE_HCG_SIGPEAK', 'KW_WAVE_HCG_GFITMODE',
    'KW_WAVE_HCG_FB_RMSMIN', 'KW_WAVE_HCG_FB_RMSMAX',
    'KW_WAVE_HCG_EWMIN', 'KW_WAVE_HCG_EWMAX', 'KW_WAVE_HCLL_FILE',
    'KW_WAVE_TRP_NBRIGHT', 'KW_WAVE_TRP_NITER', 'KW_WAVE_TRP_CATGDIST',
    'KW_WAVE_TRP_FITDEG', 'KW_WAVE_TRP_MIN_NLINES',
    'KW_WAVE_TRP_TOT_NLINES', 'KW_WAVE_TRP_ORDER_FITCONT',
    'KW_WAVE_TRP_SCLIPNUM', 'KW_WAVE_TRP_SCLIPTHRES',
    'KW_WAVE_TRP_DVCUTORD', 'KW_WAVE_TRP_DVCUTALL',
    'KW_WAVE_RES_MAPSIZE', 'KW_WAVE_RES_WSIZE',
    'KW_WAVE_RES_MAXDEVTHRES', 'KW_INIT_WAVE', 'KW_WAVETIME',
    # wave littrow values
    'KW_WAVE_LIT_START_1', 'KW_WAVE_LIT_END_1', 'KW_WAVE_LIT_RORDERS',
    'KW_WAVE_LIT_ORDER_INIT_1', 'KW_WAVE_LIT_ORDER_START_1',
    'KW_WAVE_LIT_ORDER_END_1', 'KW_WAVE_LITT_XCUTSTEP_1',
    'KW_WAVE_LITT_FITDEG_1', 'KW_WAVE_LITT_EXT_FITDEG_1',
    'KW_WAVE_LITT_EXT_ORD_START_1',
    # wave fp values
    'KW_WFP_ORD_START', 'KW_WFP_ORD_FINAL', 'KW_WFP_BLZ_THRES',
    'KW_WFP_XDIFF_MIN', 'KW_WFP_XDIFF_MAX', 'KW_WFP_DOPD0',
    'KW_WFP_LL_OFFSET', 'KW_WFP_DVMAX', 'KW_WFP_LLFITDEG',
    'KW_WFP_UPDATECAV', 'KW_WFP_FPCAV_MODE', 'KW_WFP_LLFIT_MODE',
    'KW_WFP_ERRX_MIN', 'KW_WFP_MAXLL_FIT_RMS', 'KW_WFP_T_ORD_START',
    'KW_WFP_WEI_THRES', 'KW_WFP_CAVFIT_DEG', 'KW_WFP_LARGE_JUMP',
    'KW_WFP_CM_INDX', 'KW_WFP_NPERCENT', 'KW_WFP_LIMIT',
    'KW_WFP_CUTWIDTH', 'KW_WFP_FILE', 'KW_WFP_DRIFT', 'KW_WFP_WIDUSED',
    'KW_WFP_FWHM', 'KW_WFP_CONTRAST', 'KW_WFP_MASK',
    'KW_WFP_LINES', 'KW_WFP_TARG_RV', 'KW_WFP_WIDTH',
    'KW_WFP_STEP', 'KW_WFP_SIGDET', 'KW_WFP_BOXSIZE', 'KW_WFP_MAXFLUX',
    'KW_WFP_DETNOISE', 'KW_WFP_NMAX', 'KW_WFP_MASKMIN', 'KW_WFP_MASKWID',
    'KW_WFP_MASKUNITS',
    # wave night values
    'KW_WNT_DCAVITY', 'KW_WNT_DCAVSRCE',
    'KW_WNT_NITER1', 'KW_WNT_NITER2', 'KW_WNT_HCSIGCLIP',
    'KW_WNT_MADLIMIT', 'KW_WNT_NSIG_FIT',
    # telluric preclean variables
    'KW_TELLUP_EXPO_WATER', 'KW_TELLUP_EXPO_OTHERS',
    'KW_TELLUP_DV_WATER', 'KW_TELLUP_DV_OTHERS', 'KW_TELLUP_DO_PRECLEAN',
    'KW_TELLUP_CCFP_WATER', 'KW_TELLUP_CCFP_OTHERS',
    'KW_TELLUP_DFLT_WATER', 'KW_TELLUP_CCF_SRANGE',
    'KW_TELLUP_CLEAN_OHLINES', 'KW_TELLUP_REMOVE_ORDS',
    'KW_TELLUP_SNR_MIN_THRES', 'KW_TELLUP_DEXPO_CONV_THRES',
    'KW_TELLUP_DEXPO_MAX_ITR', 'KW_TELLUP_ABSOEXPO_KTHRES',
    'KW_TELLUP_WAVE_START', 'KW_TELLUP_WAVE_END',
    'KW_TELLUP_DVGRID', 'KW_TELLUP_ABSOEXPO_KWID',
    'KW_TELLUP_ABSOEXPO_KEXP', 'KW_TELLUP_TRANS_THRES',
    'KW_TELLUP_TRANS_SIGL', 'KW_TELLUP_FORCE_AIRMASS',
    'KW_TELLUP_OTHER_BOUNDS', 'KW_TELLUP_WATER_BOUNDS',
    # mktellu values
    'KW_MKTELL_TEMP_FILE', 'KW_MKTELL_BLAZE_PRCT', 'KW_MKTELL_BLAZE_CUT',
    'KW_MKTELL_DEF_CONV_WID',  'KW_MKTELL_TEMP_MEDFILT', 'KW_MKTELL_AIRMASS',
    'KW_MKTELL_WATER',
    # fittellu values
    'KW_FTELLU_NPC', 'KW_FTELLU_ADD_DPC', 'KW_FTELLU_FIT_DPC',
    'KW_FTELLU_ABSO_SRC', 'KW_FTELLU_FIT_KEEP_NUM',
    'KW_FTELLU_FIT_MIN_TRANS', 'KW_FTELLU_LAMBDA_MIN',
    'KW_FTELLU_LAMBDA_MAX', 'KW_FTELLU_KERN_VSINI',
    'KW_FTELLU_IM_PX_SIZE', 'KW_FTELLU_FIT_ITERS', 'KW_FTELLU_RECON_LIM',
    'KW_FTELLU_AMP_PC', 'KW_FTELLU_DVTELL1', 'KW_FTELLU_DVTELL2',
    'KW_FTELLU_TAU_H2O', 'KW_FTELLU_TAU_REST', 'KW_FTELLU_ABSO_PREFIX',
    'KW_FTELLU_TEMPLATE',
    # make template values
    'KW_MKTEMP_SNR_ORDER', 'KW_MKTEMP_SNR_THRES',
    # ccf values
    'KW_CCF_MEAN_RV', 'KW_CCF_MEAN_CONSTRAST', 'KW_CCF_MEAN_FWHM',
    'KW_CCF_TOT_LINES', 'KW_CCF_MASK',
    'KW_CCF_STEP', 'KW_CCF_WIDTH', 'KW_CCF_TARGET_RV', 'KW_CCF_SIGDET',
    'KW_CCF_BOXSIZE', 'KW_CCF_MAXFLUX', 'KW_CCF_NMAX', 'KW_CCF_MASK_MIN',
    'KW_CCF_MASK_WID', 'KW_CCF_MASK_UNITS', 'KW_CCF_RV_WAVE_FP',
    'KW_CCF_RV_SIMU_FP', 'KW_CCF_RV_DRIFT', 'KW_CCF_RV_OBJ',
    'KW_CCF_RV_CORR', 'KW_CCF_RV_WAVEFILE', 'KW_CCF_RV_WAVETIME',
    'KW_CCF_RV_TIMEDIFF', 'KW_CCF_RV_WAVESRCE', 'KW_CCF_DVRMS_SP',
    'KW_CCF_DVRMS_CC',
    # polar values
    'KW_POL_STOKES', 'KW_POL_NEXP', 'KW_POL_METHOD', 'KW_POL_FILES',
    'KW_POL_EXPS', 'KW_POL_MJDS', 'KW_POL_MJDENDS', 'KW_POL_BJDS',
    'KW_POL_BERVS', 'KW_POL_EXPTIME', 'KW_POL_ELAPTIME', 'KW_POL_MJDCEN',
    'KW_POL_BJDCEN', 'KW_POL_BERVCEN', 'KW_POL_MEANBJD',
    'KW_USED_MIN_FILES', 'KW_USED_VALID_FIBERS', 'KW_USED_VALID_STOKES',
    'KW_USED_CONT_BINSIZE', 'KW_USED_CONT_OVERLAP', 'KW_POLAR_LSD_MASK',
    'KW_POLAR_LSD_FIT_RV', 'KW_POLAR_LSD_FIT_RESOL',
    'KW_POLAR_LSD_MEANPOL', 'KW_POLAR_LSD_STDPOL', 'KW_POLAR_LSD_MEDPOL',
    'KW_POLAR_LSD_MEDABSDEV', 'KW_POLAR_LSD_MEANSVQU',
    'KW_POLAR_LSD_STDSVQU', 'KW_POLAR_LSD_MEANNULL',
    'KW_POLAR_LSD_STDNULL', 'KW_POL_LSD_COL1', 'KW_POL_LSD_COL2',
    'KW_POL_LSD_COL3', 'KW_POL_LSD_COL4', 'KW_POL_LSD_COL5',
    'KW_POLAR_LSD_MLDEPTH', 'KW_POLAR_LSD_VINIT', 'KW_POLAR_LSD_VFINAL',
    'KW_POLAR_LSD_NORM', 'KW_POLAR_LSD_NBIN1', 'KW_POLAR_LSD_NLAP1',
    'KW_POLAR_LSD_NSIG1', 'KW_POLAR_LSD_NWIN1', 'KW_POLAR_LSD_NMODE1',
    'KW_POLAR_LSD_NLFIT1', 'KW_POLAR_LSD_NPOINTS', 'KW_POLAR_LSD_NBIN2',
    'KW_POLAR_LSD_NLAP2', 'KW_POLAR_LSD_NSIG2', 'KW_POLAR_LSD_NWIN2',
    'KW_POLAR_LSD_NMODE2', 'KW_POLAR_LSD_NLFIT2',
]

# set name
__NAME__ = 'apero.constants.default.default_keywords'
# Constants definition
Const = constant_functions.Const
# Keyword defintion
Keyword = constant_functions.Keyword

# -----------------------------------------------------------------------------
# Required header keys (general)
# -----------------------------------------------------------------------------
# define the HEADER key for acquisition time
#     Note must set the date format in KW_ACQTIME_FMT
KW_ACQTIME = Keyword('KW_ACQTIME', key='', value=None, source=__NAME__)

# define the MJ end date HEADER key
KW_MJDEND = Keyword('KW_MJEND', key='', value=None, source=__NAME__)

# define the observation date HEADER key
KW_DATE_OBS = Keyword('KW_DATE_OBS', key='', dtype=float, source=__NAME__)
# define the observation time HEADER key
KW_UTC_OBS = Keyword('KW_UTC_OBS', key='', dtype=float, source=__NAME__)

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KW_RDNOISE = Keyword('KW_RDNOISE', key='', dtype=float, source=__NAME__)

# define the gain HEADER key (used to get value only)
KW_GAIN = Keyword('KW_GAIN', key='', dtype=float, source=__NAME__)

# define the saturation limit HEADER key
KW_SATURATE = Keyword('KW_SATURATE', key='', dtype=float, source=__NAME__)

# define the frame time HEADER key
KW_FRMTIME = Keyword('KW_FRMTIME', key='', dtype=float, source=__NAME__)

# define the exposure time HEADER key (used to get value only)
KW_EXPTIME = Keyword('KW_EXPTIME', key='', dtype=float, source=__NAME__)
# This is the units for the exposure time
KW_EXPTIME_UNITS = Const('KW_EXPTIME_UNITS', value='s', dtype=str,
                         options=['s', 'min', 'hr', 'day'])

# define the observation type HEADER key
KW_OBSTYPE = Keyword('KW_OBSTYPE', key='', dtype=str, source=__NAME__)

# define the science fiber type HEADER key
KW_CCAS = Keyword('KW_CCAS', key='', dtype=str, source=__NAME__)

# define the reference fiber type HEADER key
KW_CREF = Keyword('KW_CREF', key='', dtype=str, source=__NAME__)

# define the calibration wheel position
KW_CALIBWH = Keyword('KW_CALIBWH', key='', dtype=str, source=__NAME__)

# define the target type (object/sky)
KW_TARGET_TYPE = Keyword('KW_TARGET_TYPE', key='', dtype=str, source=__NAME__)

# define the density HEADER key
KW_CDEN = Keyword('KW_CDEN', key='', dtype=str, source=__NAME__)

# define polarisation HEADER key
KW_CMMTSEQ = Keyword('KW_CMMTSEQ', key='', dtype=str, source=__NAME__)

# define the exposure number within sequence HEADER key
KW_CMPLTEXP = Keyword('KW_CMPLTEXP', key='', dtype=int, source=__NAME__)

# define the total number of exposures HEADER key
KW_NEXP = Keyword('KW_NEXP', key='', dtype=int, source=__NAME__)

# define the pi name HEADER key
KW_PI_NAME = Keyword('KW_PI_NAME', key='', dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# Required header keys (related to science object)
# -----------------------------------------------------------------------------
# define the observation ra HEADER key
KW_OBJRA = Keyword('KW_OBJRA', key='', dtype=float, source=__NAME__)

# define the observation dec HEADER key
KW_OBJDEC = Keyword('KW_OBJDE', key='', dtype=float, source=__NAME__)

# define the observation name
KW_OBJNAME = Keyword('KW_OBJNAME', key='', dtype=str, source=__NAME__)

# define the raw observation name
KW_OBJECTNAME = Keyword('KW_OBJECTNAME', key='', dtype=str, source=__NAME__)

# define the gaia id
KW_GAIA_ID = Keyword('KW_GAIAID', key='', dtype=str, source=__NAME__)

# define the observation equinox HEADER key
KW_OBJEQUIN = Keyword('KW_OBJEQUIN', key='', dtype=float, source=__NAME__)

# define the observation proper motion in ra HEADER key
KW_OBJRAPM = Keyword('KW_OBJRAPM', key='', dtype=float, source=__NAME__)

# define the observation proper motion in dec HEADER key
KW_OBJDECPM = Keyword('KW_OBJDECPM', key='', dtype=float, source=__NAME__)

# define the airmass HEADER key
KW_AIRMASS = Keyword('KW_AIRMASS', key='', dtype=float, source=__NAME__)

# define the weather tower temperature HEADER key
KW_WEATHER_TOWER_TEMP = Keyword('KW_WEATHER_TOWER_TEMP', key='', dtype=float,
                                source=__NAME__)

# define the cassegrain temperature HEADER key
KW_CASS_TEMP = Keyword('KW_CASS_TEMP', key='', dtype=float, source=__NAME__)

# define the humidity HEADER key
KW_HUMIDITY = Keyword('KW_HUMIDITY', key='', dtype=float, source=__NAME__)

# define the parallax HEADER key
KW_PLX = Keyword('KW_PLX', key='', dtype=float, source=__NAME__)

# define the rv HEADER key
KW_INPUTRV = Keyword('KW_RV', key='', dtype=float, source=__NAME__)

# define the object temperature HEADER key
KW_OBJ_TEMP = Keyword('KW_OBJ_TEMP', key='', dtype=float, source=__NAME__)

# -----------------------------------------------------------------------------
# Define general keywords
# -----------------------------------------------------------------------------
# DRS version
KW_VERSION = Keyword('KW_VERSION', key='', dtype=str, source=__NAME__)
KW_PPVERSION = Keyword('KW_PPVERSION', key='', dtype=str, source=__NAME__)

# DRS process ID
KW_PID = Keyword('KW_PID', key='', dtype=str, source=__NAME__)

# Processed date keyword
KW_DRS_DATE_NOW = Keyword('KW_DRS_DATE_NOW', key='', dtype=str,
                          source=__NAME__)

# DRS version date keyword
KW_DRS_DATE = Keyword('KW_DRS_DATE', key='', dtype=str, source=__NAME__)

# Define the key to get the data fits file type
KW_DPRTYPE = Keyword('KW_DPRTYPE', key='', dtype=str, source=__NAME__)

# Define the mid exposure time
KW_MID_OBS_TIME = Keyword('KW_MID_OBS_TIME', key='', source=__NAME__)

# Define the method by which the MJD was calculated
KW_MID_OBSTIME_METHOD = Keyword('KW_MID_OBS_TIME_METHOD', key='', dtype=str,
                                source=__NAME__)

# -----------------------------------------------------------------------------
# Define DRS input keywords
# -----------------------------------------------------------------------------
# input files
KW_INFILE1 = Keyword('KW_INFILE1', key='', dtype=str, source=__NAME__)
KW_INFILE2 = Keyword('KW_INFILE2', key='', dtype=str, source=__NAME__)
KW_INFILE3 = Keyword('KW_INFILE3', key='', dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# Define database input keywords
# -----------------------------------------------------------------------------
KW_CDBDARK = Keyword('KW_CDBDARK', key='', dtype=str, source=__NAME__)
KW_CDBBAD = Keyword('KW_CDBBAD', key='', dtype=str, source=__NAME__)
KW_CDBBACK = Keyword('KW_CDBBACK', key='', dtype=str, source=__NAME__)
KW_CDBORDP = Keyword('KW_CDBORDP', key='', dtype=str, source=__NAME__)
KW_CDBLOCO = Keyword('KW_CDBLOCO', key='', dtype=str, source=__NAME__)
KW_CDBSHAPEL = Keyword('KW_CDBSHAPE', key='', dtype=str, source=__NAME__)
KW_CDBSHAPEDY = Keyword('KW_CDBSHAPE', key='', dtype=str, source=__NAME__)
KW_CDBSHAPEDX = Keyword('KW_CDBSHAPE', key='', dtype=str, source=__NAME__)
KW_CDBFLAT = Keyword('KW_CDBFLAT', key='', dtype=str, source=__NAME__)
KW_CDBBLAZE = Keyword('KW_CDBBLAZE', key='', dtype=str, source=__NAME__)
KW_CDBWAVE = Keyword('KW_CDBWAVE', key='', dtype=str, source=__NAME__)
KW_CDBTHERMAL = Keyword('KW_CDBTHERMAL', key='', dtype=str, source=__NAME__)

# additional properties of calibration
KW_C_FLIP = Keyword('KW_C_FLIP', key='', dtype=str, source=__NAME__)
KW_C_CVRTE = Keyword('KW_C_CVRTE', key='', dtype=str, source=__NAME__)
KW_C_RESIZE = Keyword('KW_C_RESIZE', key='', dtype=str, source=__NAME__)
KW_C_FTYPE = Keyword('KW_C_FTYPE', key='', dtype=str, source=__NAME__)
# the fiber name
KW_FIBER = Keyword('KW_FIBER', key='', dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# Define DRS outputs keywords
# -----------------------------------------------------------------------------
# the output key for drs outputs
KW_OUTPUT = Keyword('KW_OUTPUT', key='', dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
KW_DRS_QC = Keyword('KW_DRS_QC', key='', dtype=str, source=__NAME__)
KW_DRS_QC_VAL = Keyword('KW_DRS_QC_VAL', key='', dtype=str, source=__NAME__)
KW_DRS_QC_NAME = Keyword('KW_DRS_QC_NAME', key='', dtype=str, source=__NAME__)
KW_DRS_QC_LOGIC = Keyword('KW_DRS_QC_LOGIC', key='', dtype=str, source=__NAME__)
KW_DRS_QC_PASS = Keyword('KW_DRS_QC_PASS', key='', dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# Define preprocessing variables
# -----------------------------------------------------------------------------
# The shift in pixels so that image is at same location as engineering flat
KW_PPSHIFTX = Keyword('KW_PPSHIFTX', key='', dtype=float, source=__NAME__)
KW_PPSHIFTY = Keyword('KW_PPSHIFTY', key='', dtype=float, source=__NAME__)

# The number of sigma used to construct pp master mask
KW_PPMSTR_NSIG = Keyword('KW_PPMSTR_NSIG', key='', dtype=float, source=__NAME__)

# Define the key to store the name of the pp master file used in pp (if used)
KW_PPMSTR_FILE = Keyword('KW_PPMSTER_FILE', key='', dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# Define cal_dark variables
# -----------------------------------------------------------------------------
# The fraction of dead pixels in the dark (in %)
KW_DARK_DEAD = Keyword('DADEAD', key='', dtype=float, source=__NAME__)

# The median dark level in ADU/s
KW_DARK_MED = Keyword('KW_DARK_MED', key='', dtype=float, source=__NAME__)

# The fraction of dead pixels in the blue part of the dark (in %)
KW_DARK_B_DEAD = Keyword('KW_DARK_B_DEAD', key='', dtype=float, source=__NAME__)

# The median dark level in the blue part of the dark in ADU/s
KW_DARK_B_MED = Keyword('KW_DARK_B_MED', key='', dtype=float, source=__NAME__)

# The fraction of dead pixels in the red part of the dark (in %)
KW_DARK_R_DEAD = Keyword('KW_DARK_R_DEAD', key='', dtype=float, source=__NAME__)

# The median dark level in the red part of the dark in ADU/s
KW_DARK_R_MED = Keyword('KW_DARK_R_MED', key='', dtype=float, source=__NAME__)

# The threshold of the dark level to retain in ADU
KW_DARK_CUT = Keyword('KW_DARK_CUT', key='', dtype=float, source=__NAME__)

# -----------------------------------------------------------------------------
# Define cal_badpix variables
# -----------------------------------------------------------------------------
# fraction of hot pixels
KW_BHOT = Keyword('KW_BHOT', key='', dtype=float, source=__NAME__)

# fraction of bad pixels from flat
KW_BBFLAT = Keyword('KW_BBFLAT', key='', dtype=float, source=__NAME__)

# fraction of non-finite pixels in dark
KW_BNDARK = Keyword('KW_BNDARK', key='', dtype=float, source=__NAME__)

# fraction of non-finite pixels in flat
KW_BNFLAT = Keyword('KW_BNFLAT', key='', dtype=float, source=__NAME__)

# fraction of bad pixels with all criteria
KW_BBAD = Keyword('KW_BBAD', key='', dtype=float, source=__NAME__)

# fraction of un-illuminated pixels (from engineering flat)
KW_BNILUM = Keyword('KW_BNILUM', key='', dtype=float, source=__NAME__)

# fraction of total bad pixels
KW_BTOT = Keyword('KW_BTOT', key='', dtype=float, source=__NAME__)

# -----------------------------------------------------------------------------
# Define localisation variables
# -----------------------------------------------------------------------------
# root for localisation header keys
ROOT_DRS_LOC = Const('ROOT_DRS_LOC', value=None, dtype=str, source=__NAME__)
# Mean background (as percentage)
KW_LOC_BCKGRD = Keyword('KW_LOC_BCKGRD', key='', dtype=float, source=__NAME__)
# Number of orders located
KW_LOC_NBO = Keyword('KW_LOC_NBO', key='', dtype=int, source=__NAME__)
# fit degree for order centers
KW_LOC_DEG_C = Keyword('KW_LOC_DEG_C', key='', dtype=int, source=__NAME__)
# fit degree for order widths
KW_LOC_DEG_W = Keyword('KW_LOC_DEG_W', key='', dtype=int, source=__NAME__)
# Maximum flux in order
KW_LOC_MAXFLX = Keyword('KW_LOC_MAXFLX', key='', dtype=float, source=__NAME__)
# Maximum number of removed points allowed for location fit
KW_LOC_SMAXPTS_CTR = Keyword('KW_LOC_SMAXPTS_CTR', key='', dtype=int,
                             source=__NAME__)
# Maximum number of removed points allowed for width fit
KW_LOC_SMAXPTS_WID = Keyword('KW_LOC_SMAXPTS_WID', key='', dtype=int,
                             source=__NAME__)
# Maximum rms allowed for location fit
KW_LOC_RMS_CTR = Keyword('KW_LOC_RMS_CTR', key='', dtype=float, source=__NAME__)
# Maximum rms allowed for width fit (formally KW_LOC_rms_fwhm)
KW_LOC_RMS_WID = Keyword('KW_LOC_RMS_WID', key='', dtype=float, source=__NAME__)
# Coeff center order
KW_LOC_CTR_COEFF = Keyword('KW_LOC_CTR_COEFF', key='', dtype=int,
                           source=__NAME__)
# Coeff width order
KW_LOC_WID_COEFF = Keyword('KW_LOC_WID_COEFF', key='', dtype=int,
                           source=__NAME__)

# -----------------------------------------------------------------------------
# Define shape variables
# -----------------------------------------------------------------------------
# Shape transform dx parameter
KW_SHAPE_DX = Keyword('KW_SHAPE_DX', key='', dtype=float, source=__NAME__)

# Shape transform dy parameter
KW_SHAPE_DY = Keyword('KW_SHAPE_DY', key='', dtype=float, source=__NAME__)

# Shape transform A parameter
KW_SHAPE_A = Keyword('KW_SHAPE_A', key='', dtype=float, source=__NAME__)

# Shape transform B parameter
KW_SHAPE_B = Keyword('KW_SHAPE_B', key='', dtype=float, source=__NAME__)

# Shape transform C parameter
KW_SHAPE_C = Keyword('KW_SHAPE_C', key='', dtype=float, source=__NAME__)

# Shape transform D parameter
KW_SHAPE_D = Keyword('KW_SHAPE_D', key='', dtype=float, source=__NAME__)

# -----------------------------------------------------------------------------
# Define extraction variables
# -----------------------------------------------------------------------------
# The extraction type (only added for E2DS files in extraction)
KW_EXT_TYPE = Keyword('KW_EXT_TYPE', key='', dtype=str, source=__NAME__)

# SNR calculated in extraction process (per order)
KW_EXT_SNR = Keyword('KW_EXT_SNR', key='', dtype=float, source=__NAME__)

# the start order for extraction
KW_EXT_START = Keyword('KW_EXT_START', key='', dtype=int, source=__NAME__)

# the end order for extraction
KW_EXT_END = Keyword('KW_EXT_END', key='', dtype=int, source=__NAME__)

# the upper bound for extraction of order
KW_EXT_RANGE1 = Keyword('KW_EXT_RANGE1', key='', dtype=int, source=__NAME__)

# the lower bound for extraction of order
KW_EXT_RANGE2 = Keyword('KW_EXT_RANGE2', key='', dtype=int, source=__NAME__)

# whether cosmics where rejected
KW_COSMIC = Keyword('KW_COSMIC', key='', dtype=int, source=__NAME__)

# the cosmic cut criteria
KW_COSMIC_CUT = Keyword('KW_COSMIC_CUT', key='', dtype=float, source=__NAME__)

# the cosmic threshold used
KW_COSMIC_THRES = Keyword('KW_COSMIC_THRES', key='', dtype=float,
                          source=__NAME__)

# the blaze with used
KW_BLAZE_WID = Keyword('KW_BLAZE_WID', key='', dtype=float, source=__NAME__)

# the blaze cut used
KW_BLAZE_CUT = Keyword('KW_BLAZE_CUT', key='', dtype=float, source=__NAME__)

# the blaze degree used (to fit)
KW_BLAZE_DEG = Keyword('KW_BLAZE_DEG', key='', dtype=int, source=__NAME__)

# The blaze sinc cut threshold used
KW_BLAZE_SCUT = Keyword('KW_BLAZE_SCUT', key='', dtype=float, source=__NAME__)

# The blaze sinc sigma clip (rejection threshold) used
KW_BLAZE_SIGFIG = Keyword('KW_BLAZE_SIGFIG', key='', dtype=float,
                          source=__NAME__)

# The blaze sinc bad percentile value used
KW_BLAZE_BPRCNTL = Keyword('KW_BLAZE_BPRCNTL', key='', dtype=float,
                           source=__NAME__)

# The number of iterations used in the blaze sinc fit
KW_BLAZE_NITER = Keyword('KW_BLAZE_NITER', key='', dtype=int, source=__NAME__)

# the saturation QC limit
KW_SAT_QC = Keyword('KW_SAT_QC', key='', dtype=int, source=__NAME__)

# the max saturation level
KW_SAT_LEVEL = Keyword('KW_SAT_LEVEL', key='', dtype=int, source=__NAME__)

# the wave starting point used for s1d
KW_S1D_WAVESTART = Keyword('KW_S1D_WAVESTART', key='', dtype=float,
                           source=__NAME__)

# the wave end point used for s1d
KW_S1D_WAVEEND = Keyword('KW_S1D_WAVEEND', key='', dtype=float, source=__NAME__)

# the wave grid kind used for s1d (wave or velocity)
KW_S1D_KIND = Keyword('KW_S1D_KIND', key='', dtype=str, source=__NAME__)

# the bin size for wave grid kind=wave
KW_S1D_BWAVE = Keyword('KW_S1D_BWAVE', key='', dtype=float, source=__NAME__)

# the bin size for wave grid kind=velocity
KW_S1D_BVELO = Keyword('KW_S1D_BVELO', key='', dtype=float, source=__NAME__)

# the smooth size for the s1d
KW_S1D_SMOOTH = Keyword('KW_S1D_SMOOTH', key='', dtype=float, source=__NAME__)

# the blaze threshold used for the s1d
KW_S1D_BLAZET = Keyword('KW_S1D_BLAZET', key='', dtype=float, source=__NAME__)

# the Right Ascension used to calculate the BERV
KW_BERVRA = Keyword('KW_BERVRA', key='', dtype=float, source=__NAME__)

# the Declination used to calculate the BERV
KW_BERVDEC = Keyword('KW_BERVDEC', key='', dtype=float, source=__NAME__)

# the Gaia ID used to identify KW_BERV_POS_SOURCE for BERV calculation
KW_BERVGAIA_ID = Keyword('KW_BERVGAIA_ID', key='', dtype=str, source=__NAME__)

# the OBJNAME used to identify KW_BERV_POS_SOURCE for BERV calculation
KW_BERVOBJNAME = Keyword('KW_BERVOBJNAME', key='', dtype=str, source=__NAME__)

# the epoch (jd) used to calculate the BERV
KW_BERVEPOCH = Keyword('KW_BERVEPOCH', key='', dtype=float, source=__NAME__)

# the pmra [mas/yr] used to calculate the BERV
KW_BERVPMRA = Keyword('KW_BERVPMRA', key='', dtype=float, source=__NAME__)

# the pmde [mas/yr] used to calculate the BERV
KW_BERVPMDE = Keyword('KW_BERVPMDE', key='', dtype=float, source=__NAME__)

# the parallax [mas] used to calculate the BERV
KW_BERVPLX = Keyword('KW_BERVPLX', key='', dtype=float, source=__NAME__)

# the rv [km/s] used to calculate the BERV
KW_BERVRV = Keyword('KW_BERVR', key='', dtype=float, source=__NAME__)

# the source of the BERV star parameters (header or gaia)
KW_BERV_POS_SOURCE = Keyword('KW_BERV_POS_SOURCE', key='', dtype=str,
                             source=__NAME__)

# the Gaia G mag (if present) for the gaia query
KW_BERV_GAIA_GMAG = Keyword('KW_BERV_GAIA_GMAG', key='', dtype=float,
                            source=__NAME__)

# the Gaia BP mag (if present) for the gaia query
KW_BERV_GAIA_BPMAG = Keyword('KW_BERV_GAIA_BPMAG', key='', dtype=float,
                             source=__NAME__)

# the Gaia RP mag (if present) for the gaia query
KW_BERV_GAIA_RPMAG = Keyword('KW_BERV_GAIA_RPMAG', key='', dtype=float,
                             source=__NAME__)

# the Gaia G mag limit used for the gaia query
KW_BERV_GAIA_MAGLIM = Keyword('KW_BERV_GAIA_MAGLIM', key='', dtype=float,
                              source=__NAME__)

# the Gaia parallax limit used the gaia query
KW_BERV_GAIA_PLXLIM = Keyword('KW_BERV_GAIA_PLXLIM', key='', dtype=float,
                              source=__NAME__)

# the observatory latitude used to calculate the BERV
KW_BERVLAT = Keyword('KW_BERVLAT', key='', dtype=float, source=__NAME__)

# the observatory longitude used to calculate the BERV
KW_BERVLONG = Keyword('KW_BERVLONG', key='', dtype=float, source=__NAME__)

# the observatory altitude used to calculate the BERV
KW_BERVALT = Keyword('KW_BERVALT', key='', dtype=float, source=__NAME__)

# the BERV calculated with KW_BERVSOURCE
KW_BERV = Keyword('KW_BERV', key='', dtype=float, source=__NAME__)

# the Barycenter Julian date calculate with KW_BERVSOURCE
KW_BJD = Keyword('KW_BJD', key='', dtype=float, source=__NAME__)

# the maximum BERV found across 1 year (with KW_BERVSOURCE)
KW_BERVMAX = Keyword('KW_BERVMAX', key='', dtype=float, source=__NAME__)

# the derivative of the BERV (BERV at time + 1s - BERV)
KW_DBERV = Keyword('KW_DBERV', key='', dtype=float, source=__NAME__)

# the source of the calculated BERV parameters
KW_BERVSOURCE = Keyword('KW_BERVSOURCE', key='', dtype=str, source=__NAME__)

# the BERV calculated with the estimate
KW_BERV_EST = Keyword('KW_BERV_EST', key='', dtype=float, source=__NAME__)

# the Barycenter Julian date calculated with the estimate
KW_BJD_EST = Keyword('KW_BJD_EST', key='', dtype=float, source=__NAME__)

# the maximum BERV found across 1 year (calculated with estimate)
KW_BERVMAX_EST = Keyword('KW_BERVMAX_EST', key='', dtype=float, source=__NAME__)

# the derivative of the BERV (BERV at time + 1s - BERV) calculated with
#     estimate
KW_DBERV_EST = Keyword('KW_DBERV_EST', key='', dtype=float, source=__NAME__)

# the actual jd time used to calculate the BERV
KW_BERV_OBSTIME = Keyword('KW_BERV_OBSTIME', key='', dtype=float,
                          source=__NAME__)

# the method used to obtain the berv obs time
KW_BERV_OBSTIME_METHOD = Keyword('KW_BERV_OBSTIME_METHOD', key='', dtype=str,
                                 source=__NAME__)

# -----------------------------------------------------------------------------
# Define leakage variables
# -----------------------------------------------------------------------------
# Define whether leak correction has been done
KW_LEAK_CORR = Keyword('KW_LEAK_CORR', key='', dtype=int, source=__NAME__)

# Define the background percentile used for correcting leakage
KW_LEAK_BP_U = Keyword('KW_LEAK_BP_U', key='', dtype=float, source=__NAME__)

# Define the normalisation percentile used for correcting leakage
KW_LEAK_NP_U = Keyword('KW_LEAK_NP_U', key='', dtype=float, source=__NAME__)

# Define the e-width smoothing used for correcting leakage master
KW_LEAK_WSMOOTH = Keyword('KW_LEAK_WSMOOTH', key='', dtype=float,
                          source=__NAME__)

# Define the kernel size used for correcting leakage master
KW_LEAK_KERSIZE = Keyword('KW_LEAK_KERSIZE', key='', dtype=float,
                          source=__NAME__)

# Define the lower bound percentile used for correcting leakage
KW_LEAK_LP_U = Keyword('KW_LEAK_LP_U', key='', dtype=float, source=__NAME__)

# Define the upper bound percentile used for correcting leakage
KW_LEAK_UP_U = Keyword('KW_LEAK_UP_U', key='', dtype=float, source=__NAME__)

# Define the bad ratio offset limit used for correcting leakage
KW_LEAK_BADR_U = Keyword('KW_LEAK_BADR_U', key='', dtype=float, source=__NAME__)

# -----------------------------------------------------------------------------
# Define wave variables
# -----------------------------------------------------------------------------
# Number of orders in wave image
KW_WAVE_NBO = Keyword('KW_WAVE_NBO', key='', dtype=int, source=__NAME__)

# fit degree for wave solution
KW_WAVE_DEG = Keyword('KW_WAVE_DEG', key='', dtype=int, source=__NAME__)

# the wave file used
KW_WAVEFILE = Keyword('KW_WAVEFILE', key='', dtype=str, source=__NAME__)

# the wave file mid exptime [mjd]
KW_WAVETIME = Keyword('KW_WAVETIME', key='', dtype=float, source=__NAME__)

# the wave source of the wave file used
KW_WAVESOURCE = Keyword('KW_WAVESOURCE', key='', dtype=str, source=__NAME__)

# the wave coefficients
KW_WAVECOEFFS = Keyword('KW_WAVECOEFFS', key='', dtype=float, source=__NAME__)

# the initial wave file used for wave solution
KW_INIT_WAVE = Keyword('KW_INIT_WAVE', key='', dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# the fit degree for wave solution used
KW_WAVE_FITDEG = Keyword('KW_WAVE_FITDEG', key='', dtype=int, source=__NAME__)

# the mode used to calculate the hc wave solution
KW_WAVE_MODE_HC = Keyword('KW_WAVE_MODE_HC', key='', dtype=str, source=__NAME__)

# the mode used to calculate the fp wave solution
KW_WAVE_MODE_FP = Keyword('KW_WAVE_MODE_FP', key='', dtype=str, source=__NAME__)

# the echelle number of the first order used
KW_WAVE_ECHELLE_START = Keyword('KW_WAVE_ECHELLE_START', key='', dtype=int,
                                source=__NAME__)

# the width of the box for fitting hc lines used
KW_WAVE_HCG_WSIZE = Keyword('KW_WAVE_HCG_WSIZE', key='', dtype=int,
                            source=__NAME__)

# the sigma above local rms for fitting hc lines used
KW_WAVE_HCG_SIGPEAK = Keyword('KW_WAVE_HCG_SIGPEAK', key='', dtype=float,
                              source=__NAME__)

# the fit degree for the gaussian peak fitting used
KW_WAVE_HCG_GFITMODE = Keyword('KW_WAVE_HCG_GFITMODE', key='', dtype=int,
                               source=__NAME__)

# the min rms for gaussian peak fitting used
KW_WAVE_HCG_FB_RMSMIN = Keyword('KW_WAVE_HCG_FB_RMSMIN', key='', dtype=float,
                                source=__NAME__)

# the max rms for gaussian peak fitting used
KW_WAVE_HCG_FB_RMSMAX = Keyword('KW_WAVE_HCG_FB_RMSMAX', key='', dtype=float,
                                source=__NAME__)

# the min e-width of the line for gaussian peak fitting used
KW_WAVE_HCG_EWMIN = Keyword('KW_WAVE_HCG_EWMIN', key='', dtype=float,
                            source=__NAME__)

# the min e-width of the line for gaussian peak fitting used
KW_WAVE_HCG_EWMAX = Keyword('KW_WAVE_HCG_EWMAX', key='', dtype=float,
                            source=__NAME__)

# the filename for the HC line list generated
KW_WAVE_HCLL_FILE = Keyword('KW_WAVE_HCLL_FILE', key='', dtype=str,
                            source=__NAME__)

# the number of bright lines to used in triplet fit
KW_WAVE_TRP_NBRIGHT = Keyword('KW_WAVE_TRP_NBRIGHT', key='', dtype=int,
                              source=__NAME__)

# the number of iterations done in triplet fit
KW_WAVE_TRP_NITER = Keyword('KW_WAVE_TRP_NITER', key='', dtype=float,
                            source=__NAME__)

# the max distance between catalog line and initial guess line in triplet fit
KW_WAVE_TRP_CATGDIST = Keyword('KW_WAVE_TRP_CATGDIST', key='', dtype=float,
                               source=__NAME__)

# the fit degree for triplet fit
KW_WAVE_TRP_FITDEG = Keyword('KW_WAVE_TRP_FITDEG', key='', dtype=int,
                             source=__NAME__)

# the minimum number of lines required per order in triplet fit
KW_WAVE_TRP_MIN_NLINES = Keyword('KW_WAVE_TRP_MIN_NLINES', key='', dtype=int,
                                 source=__NAME__)

# the total number of lines required in triplet fit
KW_WAVE_TRP_TOT_NLINES = Keyword('KW_WAVE_TRP_TOT_NLINES', key='', dtype=int,
                                 source=__NAME__)

# the degree(s) of fit to ensure continuity in triplet fit
KW_WAVE_TRP_ORDER_FITCONT = Keyword('KW_WAVE_TRP_ORDER_FITCONT', key='',
                                    dtype=float, source=__NAME__)

# the iteration number for sigma clip in triplet fit
KW_WAVE_TRP_SCLIPNUM = Keyword('KW_WAVE_TRP_SCLIPNUM', key='', dtype=float,
                               source=__NAME__)

# the sigma clip threshold in triplet fit
KW_WAVE_TRP_SCLIPTHRES = Keyword('KW_WAVE_TRP_SCLIPTHRES', key='', dtype=float,
                                 source=__NAME__)

# the distance away in dv to reject order triplet in triplet fit
KW_WAVE_TRP_DVCUTORD = Keyword('KW_WAVE_TRP_DVCUTORD', key='', dtype=float,
                               source=__NAME__)

# the distance away in dv to reject all triplet in triplet fit
KW_WAVE_TRP_DVCUTALL = Keyword('KW_WAVE_TRP_DVCUTALL', key='', dtype=float,
                               source=__NAME__)

# the wave resolution map dimensions
KW_WAVE_RES_MAPSIZE = Keyword('KW_WAVE_RES_MAPSIZE', key='', dtype=int,
                              source=__NAME__)

# the width of the box for wave resolution map
KW_WAVE_RES_WSIZE = Keyword('KW_WAVE_RES_WSIZE', key='', dtype=float,
                            source=__NAME__)

# the max deviation in rms allowed in wave resolution map
KW_WAVE_RES_MAXDEVTHRES = Keyword('KW_WAVE_RES_MAXDEVTHRES', key='',
                                  dtype=float, source=__NAME__)

# the littrow start order used for HC
KW_WAVE_LIT_START_1 = Keyword('KW_WAVE_LIT_START_1', key='', dtype=int,
                              source=__NAME__)

# the littrow end order used for HC
KW_WAVE_LIT_END_1 = Keyword('KW_WAVE_LIT_END_1', key='', dtype=float,
                            source=__NAME__)

# the orders removed from the littrow test
KW_WAVE_LIT_RORDERS = Keyword('KW_WAVE_LIT_RORDERS', key='', dtype=float,
                              source=__NAME__)

# the littrow order initial value used for HC
KW_WAVE_LIT_ORDER_INIT_1 = Keyword('KW_WAVE_LIT_ORDER_INIT_1', key='',
                                   dtype=int, source=__NAME__)

# the littrow order start value used for HC
KW_WAVE_LIT_ORDER_START_1 = Keyword('KW_WAVE_LIT_ORDER_START_1', key='',
                                    dtype=int, source=__NAME__)

# the littrow order end value used for HC
KW_WAVE_LIT_ORDER_END_1 = Keyword('KW_WAVE_LIT_ORDER_END_1', key='',
                                  dtype=int, source=__NAME__)

# the littrow x cut step value used for HC
KW_WAVE_LITT_XCUTSTEP_1 = Keyword('KW_WAVE_LITT_XCUTSTEP_1', key='',
                                  dtype=int, source=__NAME__)

# the littrow fit degree value used for HC
KW_WAVE_LITT_FITDEG_1 = Keyword('KW_WAVE_LITT_FITDEG_1', key='', dtype=int,
                                source=__NAME__)

# the littrow extrapolation fit degree value used for HC
KW_WAVE_LITT_EXT_FITDEG_1 = Keyword('KW_WAVE_LITT_EXT_FITDEG_1', key='',
                                    dtype=int, source=__NAME__)

# the littrow extrapolation start order value used for HC
KW_WAVE_LITT_EXT_ORD_START_1 = Keyword('KW_WAVE_LITT_EXT_ORD_START_1', key='',
                                       dtype=int, source=__NAME__)

# the first order used for FP wave sol improvement
KW_WFP_ORD_START = Keyword('KW_WFP_ORD_START', key='', dtype=int,
                           source=__NAME__)

# the last order used for FP wave sol improvement
KW_WFP_ORD_FINAL = Keyword('KW_WFP_ORD_FINAL', key='', dtype=int,
                           source=__NAME__)

# the blaze threshold used for FP wave sol improvement
KW_WFP_BLZ_THRES = Keyword('KW_WFP_BLZ_THRES', key='', dtype=float,
                           source=__NAME__)

# the minimum fp peak pixel sep used for FP wave sol improvement
KW_WFP_XDIFF_MIN = Keyword('KW_WFP_XDIFF_MIN', key='', dtype=float,
                           source=__NAME__)

# the maximum fp peak pixel sep used for FP wave sol improvement
KW_WFP_XDIFF_MAX = Keyword('KW_WFP_XDIFF_MAX', key='', dtype=float,
                           source=__NAME__)

# the initial value of the FP effective cavity width used
KW_WFP_DOPD0 = Keyword('KW_WFP_DOPD0', key='', dtype=float, source=__NAME__)

# the  maximum fraction wavelength offset btwn xmatch fp peaks used
KW_WFP_LL_OFFSET = Keyword('KW_WFP_LL_OFFSET', key='', dtype=float,
                           source=__NAME__)

# the max dv to keep hc lines used
KW_WFP_DVMAX = Keyword('KW_WFP_DVMAX', key='', dtype=float, source=__NAME__)

# the used polynomial fit degree (to fit wave solution)
KW_WFP_LLFITDEG = Keyword('KW_WFP_LLFITDEG', key='', dtype=int,
                          source=__NAME__)

# whether the cavity file was updated
KW_WFP_UPDATECAV = Keyword('KW_WFP_UPDATECAV', key='', dtype=int,
                           source=__NAME__)

# the mode used to fit the FP cavity
KW_WFP_FPCAV_MODE = Keyword('KW_WFP_FPCAV_MODE', key='', dtype=int,
                            source=__NAME__)

# the mode used to fit the wavelength
KW_WFP_LLFIT_MODE = Keyword('KW_WFP_LLFIT_MODE', key='', dtype=int,
                            source=__NAME__)

# the minimum instrumental error used
KW_WFP_ERRX_MIN = Keyword('KW_WFP_ERRX_MIN', key='', dtype=float,
                          source=__NAME__)

# the max rms for the wave sol sig clip
KW_WFP_MAXLL_FIT_RMS = Keyword('KW_WFP_MAXLL_FIT_RMS', key='', dtype=float,
                               source=__NAME__)

# the echelle number used for the first order
KW_WFP_T_ORD_START = Keyword('KW_WFP_T_ORD_START', key='', dtype=int,
                             source=__NAME__)

# the weight below which fp lines are rejected
KW_WFP_WEI_THRES = Keyword('KW_WFP_WEI_THRES', key='', dtype=float,
                           source=__NAME__)

# the polynomial degree fit order used for fitting the fp cavity
KW_WFP_CAVFIT_DEG = Keyword('KW_WFP_CAVFIT_DEG', key='', dtype=int,
                            source=__NAME__)

# the largest jump in fp that was allowed
KW_WFP_LARGE_JUMP = Keyword('KW_WFP_LARGE_JUMP', key='', dtype=float,
                            source=__NAME__)

# the index to start crossmatching fps at
KW_WFP_CM_INDX = Keyword('KW_WFP_CM_INDX', key='', dtype=float, source=__NAME__)

# the FP widths used for each order (1D list)
KW_WFP_WIDUSED = Keyword('KW_WFP_WIDUSED', key='', dtype=float, source=__NAME__)

# the percentile to normalise the FP flux per order used
KW_WFP_NPERCENT = Keyword('KW_WFP_NPERCENT', key='', dtype=float,
                          source=__NAME__)

# the normalised limited used to detect FP peaks
KW_WFP_LIMIT = Keyword('KW_WFP_LIMIT', key='', dtype=float, source=__NAME__)

# the normalised cut width for large peaks used
KW_WFP_CUTWIDTH = Keyword('KW_WFP_CUTWIDTH', key='', dtype=float,
                          source=__NAME__)

# Wavelength solution for fiber C that is is source of the WFP keys
KW_WFP_FILE = Keyword('KW_WFP_FILE', key='', dtype=str, source=__NAME__)

# drift of the FP file used for the wavelength solution
KW_WFP_DRIFT = Keyword('KW_WFP_DRIFT', key='', dtype=float, source=__NAME__)

# FWHM of the wave FP file CCF
KW_WFP_FWHM = Keyword('KW_WFP_FWHM', key='', dtype=float, source=__NAME__)

# Contrast of the wave FP file CCF
KW_WFP_CONTRAST = Keyword('KW_WFP_CONTRAST', key='', dtype=float,
                          source=__NAME__)

# Mask for the wave FP file CCF
KW_WFP_MASK = Keyword('KW_WFP_MASK', key='', dtype=float, source=__NAME__)

# Number of lines for the wave FP file CCF
KW_WFP_LINES = Keyword('KW_WFP_LINES', key='', dtype=float, source=__NAME__)

# Target RV for the wave FP file CCF
KW_WFP_TARG_RV = Keyword('KW_WFP_TARG_RV', key='', dtype=float, source=__NAME__)

# Width for the wave FP file CCF
KW_WFP_WIDTH = Keyword('KW_WFP_WIDTH', key='', dtype=float, source=__NAME__)

# Step for the wave FP file CCF
KW_WFP_STEP = Keyword('KW_WFP_STEP', key='', dtype=float, source=__NAME__)

# The sigdet used for FP file CCF
KW_WFP_SIGDET = Keyword('KW_WFP_SIGDET', key='', dtype=float, source=__NAME__)

# The boxsize used for FP file CCF
KW_WFP_BOXSIZE = Keyword('KW_WFP_BOXSIZE', key='', dtype=int, source=__NAME__)

# The max flux used for the FP file CCF
KW_WFP_MAXFLUX = Keyword('KW_WFP_MAXFLUX', key='', dtype=float, source=__NAME__)

# The det noise used for the FP file CCF
KW_WFP_DETNOISE = Keyword('KW_WFP_DETNOISE', key='', dtype=float,
                          source=__NAME__)

# the highest order used for the FP file CCF
KW_WFP_NMAX = Keyword('KW_WFP_NMAX', key='', dtype=int, source=__NAME__)

# The weight of the CCF mask (if 1 force all weights equal) used for FP CCF
KW_WFP_MASKMIN = Keyword('KW_WFP_MASKMIN', key='', dtype=float, source=__NAME__)

# The width of the CCF mask template line (if 0 use natural) used for FP CCF
KW_WFP_MASKWID = Keyword('KW_WFP_MASKWID', key='', dtype=float, source=__NAME__)

# The units of the input CCF mask (converted to nm in code)
KW_WFP_MASKUNITS = Keyword('KW_WFP_MASKUNITS', key='', dtype=str,
                           source=__NAME__)

# number of iterations for convergence used in wave night (hc)
KW_WNT_NITER1 = Keyword('KW_WNT_NITER1', key='', dtype=int, source=__NAME__)

# number of iterations for convergence used in wave night (fp)
KW_WNT_NITER2 = Keyword('KW_WNT_NITER2', key='', dtype=int, source=__NAME__)

# starting point for the cavity corrections used in wave night
KW_WNT_DCAVITY = Keyword('KW_WNT_DCAVITY', key='', dtype=int, source=__NAME__)

# source fiber for the cavity correction
KW_WNT_DCAVSRCE = Keyword('KW_WNT_DCAVSRCE', key='', dtype=str, source=__NAME__)

# define the sigma clip value to remove bad hc lines used
KW_WNT_HCSIGCLIP = Keyword('KW_WNT_HCSIGCLIP', key='', dtype=float,
                           source=__NAME__)

# median absolute deviation cut off used
KW_WNT_MADLIMIT = Keyword('KW_WNT_MADLIMIT', key='', dtype=float,
                          source=__NAME__)

# sigma clipping for the fit used in wave night
KW_WNT_NSIG_FIT = Keyword('KW_WNT_NSIG_FIT', key='', dtype=int, source=__NAME__)

# -----------------------------------------------------------------------------
# Define telluric preclean variables
# -----------------------------------------------------------------------------
# Define the exponent of water key from telluric preclean process
KW_TELLUP_EXPO_WATER = Keyword('KW_TELLUP_EXPO_WATER', key='', dtype=float,
                               source=__NAME__)

# Define the exponent of other species from telluric preclean process
KW_TELLUP_EXPO_OTHERS = Keyword('KW_TELLUP_EXPO_OTHERS', key='', dtype=float,
                                source=__NAME__)

# Define the velocity of water absorbers calculated in telluric preclean process
KW_TELLUP_DV_WATER = Keyword('KW_TELLUP_DV_WATER', key='', dtype=float,
                             source=__NAME__)

# Define the velocity of other species absorbers calculated in telluric
#     preclean process
KW_TELLUP_DV_OTHERS = Keyword('KW_TELLUP_DV_OTHERS', key='', dtype=float,
                              source=__NAME__)

# Define the ccf power of the water
KW_TELLUP_CCFP_WATER = Keyword('KW_TELLUP_CCFP_WATER', key='', dtype=float,
                               source=__NAME__)

# Define the ccf power of the others
KW_TELLUP_CCFP_OTHERS = Keyword('KW_TELLUP_CCFP_OTHERS', key='', dtype=float,
                                source=__NAME__)

# Define whether precleaning was done (tellu pre-cleaning)
KW_TELLUP_DO_PRECLEAN = Keyword('KW_TELLUP_DO_PRECLEAN', key='', dtype=bool,
                                source=__NAME__)

# Define default water absorption used (tellu pre-cleaning)
KW_TELLUP_DFLT_WATER = Keyword('KW_TELLUP_DFLT_WATER', key='', dtype=float,
                               source=__NAME__)

# Define ccf scan range that was used (tellu pre-cleaning)
KW_TELLUP_CCF_SRANGE = Keyword('KW_TELLUP_CCF_SRANGE', key='', dtype=float,
                               source=__NAME__)

# Define whether we cleaned OH lines
KW_TELLUP_CLEAN_OHLINES = Keyword('KW_TELLUP_CCF_SRANGE', key='', dtype=float,
                                  source=__NAME__)

# Define which orders were removed from tellu pre-cleaning
KW_TELLUP_REMOVE_ORDS = Keyword('KW_TELLUP_REMOVE_ORDSv', key='', dtype=str,
                                source=__NAME__)

# Define which min snr threshold was used for tellu pre-cleaning
KW_TELLUP_SNR_MIN_THRES = Keyword('KW_TELLUP_SNR_MIN_THRES', key='',
                                  dtype=float, source=__NAME__)

# Define dexpo convergence threshold used
KW_TELLUP_DEXPO_CONV_THRES = Keyword('KW_TELLUP_DEXPO_CONV_THRES', key='',
                                     dtype=float, source=__NAME__)

# Define the maximum number of oterations used to get dexpo convergence
KW_TELLUP_DEXPO_MAX_ITR = Keyword('KW_TELLUP_DEXPO_MAX_ITR', key='',
                                  dtype=int, source=__NAME__)

# Define the kernel threshold in abso_expo used in tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KTHRES = Keyword('KW_TELLUP_ABSOEXPO_KTHRES', key='',
                                    dtype=int, source=__NAME__)

# Define the wave start (same as s1d) in nm used
KW_TELLUP_WAVE_START = Keyword('KW_TELLUP_WAVE_START', key='', dtype=float,
                               source=__NAME__)

# Define the wave end (same as s1d) in nm used
KW_TELLUP_WAVE_END = Keyword('KW_TELLUP_WAVE_END', key='', dtype=float,
                             source=__NAME__)

# Define the dv wave grid (same as s1d) in km/s used
KW_TELLUP_DVGRID = Keyword('KW_TELLUP_DVGRID', key='', dtype=float,
                           source=__NAME__)

# Define the gauss width of the kernel used in abso_expo for tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KWID = Keyword('KW_TELLUP_ABSOEXPO_KWID', key='',
                                  dtype=float, source=__NAME__)

# Define the gauss shape of the kernel used in abso_expo for tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KEXP = Keyword('KW_TELLUP_ABSOEXPO_KEXP', key='',
                                  dtype=float, source=__NAME__)

# Define the exponent of the transmission threshold used for tellu pre-cleaning
KW_TELLUP_TRANS_THRES = Keyword('KW_TELLUP_TRANS_THRES', key='',
                                dtype=float, source=__NAME__)

# Define the threshold for discrepant tramission used for tellu pre-cleaning
KW_TELLUP_TRANS_SIGL = Keyword('KW_TELLUP_TRANS_SIGL', key='',
                               dtype=float, source=__NAME__)

# Define the whether to force fit to header airmass used for tellu pre-cleaning
KW_TELLUP_FORCE_AIRMASS = Keyword('KW_TELLUP_FORCE_AIRMASS', key='',
                                  dtype=bool, source=__NAME__)

# Define the bounds of the exponent of other species used for tellu pre-cleaning
KW_TELLUP_OTHER_BOUNDS = Keyword('KW_TELLUP_OTHER_BOUNDS', key='',
                                 dtype=str, source=__NAME__)

# Define the bounds of the exponent of water used for tellu pre-cleaning
KW_TELLUP_WATER_BOUNDS = Keyword('KW_TELLUP_WATER_BOUNDS', key='',
                                 dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# Define make telluric variables
# -----------------------------------------------------------------------------
# The template file used for mktellu calculation
KW_MKTELL_TEMP_FILE = Keyword('KW_MKTELL_TEMP_FILE', key='', dtype=str,
                              source=__NAME__)

# The blaze percentile used for mktellu calculation
KW_MKTELL_BLAZE_PRCT = Keyword('KW_MKTELL_BLAZE_PRCT', key='', dtype=float,
                               source=__NAME__)

# The blaze normalization cut used for mktellu calculation
KW_MKTELL_BLAZE_CUT = Keyword('KW_MKTELL_BLAZE_CUT', key='', dtype=float,
                              source=__NAME__)

# The default convolution width in pix used for mktellu calculation
KW_MKTELL_DEF_CONV_WID = Keyword('KW_MKTELL_DEF_CONV_WID', key='', dtype=int,
                                 source=__NAME__)

# The median filter width used for mktellu calculation
KW_MKTELL_TEMP_MEDFILT = Keyword('KW_MKTELL_TEMP_MEDFILT', key='', dtype=float,
                                 source=__NAME__)

# The recovered airmass value calculated in mktellu calculation
KW_MKTELL_AIRMASS = Keyword('KW_MKTELL_AIRMASS', key='', dtype=float,
                            source=__NAME__)

# The recovered water optical depth calculated in mktellu calculation
KW_MKTELL_WATER = Keyword('KW_MKTELL_WATER', key='', dtype=float,
                          source=__NAME__)

# -----------------------------------------------------------------------------
# Define fit telluric variables
# -----------------------------------------------------------------------------
# The number of principle components used
KW_FTELLU_NPC = Keyword('KW_FTELLU_NPC', key='', dtype=int, source=__NAME__)

# whether we added first derivative to principal components
KW_FTELLU_ADD_DPC = Keyword('KW_FTELLU_ADD_DPC', key='', dtype=bool,
                            source=__NAME__)

# whether we fitted the derivatives of the principal components
KW_FTELLU_FIT_DPC = Keyword('KW_FTELLU_FIT_DPC', key='', dtype=bool,
                            source=__NAME__)

# The source of the loaded absorption (npy file or trans_file from database)
KW_FTELLU_ABSO_SRC = Keyword('KW_FTELLU_ABSO_SRC', key='', dtype=str,
                             source=__NAME__)

# The prefix for molecular
KW_FTELLU_ABSO_PREFIX = Keyword('KW_FTELLU_ABSO_PREFIX', key='', dtype=float,
                                source=__NAME__)

# Number of good pixels requirement used
KW_FTELLU_FIT_KEEP_NUM = Keyword('KW_FTELLU_FIT_KEEP_NUM', key='', dtype=int,
                                 source=__NAME__)

# The minimum transmission used
KW_FTELLU_FIT_MIN_TRANS = Keyword('KW_FTELLU_FIT_MIN_TRANS', key='',
                                  dtype=float, source=__NAME__)

# The minimum wavelength used
KW_FTELLU_LAMBDA_MIN = Keyword('KW_FTELLU_LAMBDA_MIN', key='', dtype=float,
                               source=__NAME__)

# The maximum wavelength used
KW_FTELLU_LAMBDA_MAX = Keyword('KW_FTELLU_LAMBDA_MAX', key='', dtype=float,
                               source=__NAME__)

# The smoothing kernel size [km/s] used
KW_FTELLU_KERN_VSINI = Keyword('KW_FTELLU_KERN_VSINI', key='', dtype=float,
                               source=__NAME__)

# The image pixel size used
KW_FTELLU_IM_PX_SIZE = Keyword('KW_FTELLU_IM_PX_SIZE', key='', dtype=float,
                               source=__NAME__)

# the number of iterations used to fit
KW_FTELLU_FIT_ITERS = Keyword('KW_FTELLU_FIT_ITERS', key='', dtype=int,
                              source=__NAME__)

# the log limit in minimum absorption used
KW_FTELLU_RECON_LIM = Keyword('KW_FTELLU_RECON_LIM', key='', dtype=float,
                              source=__NAME__)

# the template that was used (or None if not used)
KW_FTELLU_TEMPLATE = Keyword('KW_FTELLU_TEMPLATE', key='', dtype=str,
                             source=__NAME__)

# Telluric principle component amplitudes (for use with 1D list)
KW_FTELLU_AMP_PC = Keyword('KW_FTELLU_AMP_PC', key='', dtype=float,
                           source=__NAME__)

# Telluric principle component first derivative
KW_FTELLU_DVTELL1 = Keyword('KW_FTELLU_DVTELL1', key='', dtype=float,
                            source=__NAME__)

# Telluric principle component second derivative
KW_FTELLU_DVTELL2 = Keyword('KW_FTELLU_DVTELL2', key='', dtype=float,
                            source=__NAME__)

# Tau Water depth calculated in fit tellu
KW_FTELLU_TAU_H2O = Keyword('KW_FTELLU_TAU_H2O', key='', dtype=float,
                            source=__NAME__)

# Tau Rest depth calculated in fit tellu
KW_FTELLU_TAU_REST = Keyword('KW_FTELLU_TAU_REST', key='', dtype=float,
                             source=__NAME__)

# -----------------------------------------------------------------------------
# Define make template variables
# -----------------------------------------------------------------------------
# the snr order used for quality control cut in make template calculation
KW_MKTEMP_SNR_ORDER = Keyword('KW_MKTEMP_SNR_ORDER', key='', dtype=int,
                              source=__NAME__)

# the snr threshold used for quality control cut in make template calculation
KW_MKTEMP_SNR_THRES = Keyword('KW_MKTEMP_SNR_THRES', key='', dtype=float,
                              source=__NAME__)

# -----------------------------------------------------------------------------
# Define ccf variables
# -----------------------------------------------------------------------------
# The mean rv calculated from the mean ccf
KW_CCF_MEAN_RV = Keyword('KW_CCF_MEAN_RV', key='', dtype=float, source=__NAME__)

# the mean constrast (depth of fit ccf) from the mean ccf
KW_CCF_MEAN_CONSTRAST = Keyword('KW_CCF_MEAN_CONSTRAST', key='', dtype=float,
                                source=__NAME__)

# the mean fwhm from the mean ccf
KW_CCF_MEAN_FWHM = Keyword('KW_CCF_MEAN_FWHM', key='', dtype=float,
                           source=__NAME__)

# the total number of mask lines used in all ccfs
KW_CCF_TOT_LINES = Keyword('KW_CCF_TOT_LINES', key='', dtype=int,
                           source=__NAME__)

# the ccf mask file used
KW_CCF_MASK = Keyword('KW_CCF_MASK', key='', dtype=str, source=__NAME__)

# the ccf step used (in km/s)
KW_CCF_STEP = Keyword('KW_CCF_STEP', key='', dtype=float, source=__NAME__)

# the width of the ccf used (in km/s)
KW_CCF_WIDTH = Keyword('KW_CCF_WIDTH', key='', dtype=float, source=__NAME__)

# the central rv used (in km/s) rv elements run from rv +/- width in the ccf
KW_CCF_TARGET_RV = Keyword('KW_CCF_TARGET_RV', key='', dtype=float,
                           source=__NAME__)

# the read noise used in the photon noise uncertainty calculation in the ccf
KW_CCF_SIGDET = Keyword('KW_CCF_SIGDET', key='', dtype=float, source=__NAME__)

# the size in pixels around saturated pixels to regard as bad pixels used in
#    the ccf photon noise calculation
KW_CCF_BOXSIZE = Keyword('KW_CCF_BOXSIZE', key='', dtype=int, source=__NAME__)

# the upper limit for good pixels (above this are bad) used in the ccf photon
#   noise calculation
KW_CCF_MAXFLUX = Keyword('KW_CCF_MAXFLUX', key='', dtype=float, source=__NAME__)

# The last order used in the mean CCF (from 0 to nmax are used)
KW_CCF_NMAX = Keyword('KW_CCF_NMAX', key='', dtype=int, source=__NAME__)

# the minimum weight of a line in the CCF MASK used
KW_CCF_MASK_MIN = Keyword('KW_CCF_MASK_MIN', key='', dtype=float,
                          source=__NAME__)

# the mask width of lines in the CCF Mask used
KW_CCF_MASK_WID = Keyword('KW_CCF_MASK_WID', key='', dtype=float,
                          source=__NAME__)

# the wavelength units used in the CCF Mask for line centers
KW_CCF_MASK_UNITS = Keyword('KW_CCF_MASK_UNITS', key='', dtype=str,
                            source=__NAME__)

# the dv rms calculated for spectrum [m/s]
KW_CCF_DVRMS_SP = Keyword('KW_CCF_DVRMS_SP', key='', dtype=float,
                          source=__NAME__)

# the dev rms calculated during the CCF [m/s]
KW_CCF_DVRMS_CC = Keyword('KW_CCF_DVRMS_CC', key='', dtype=float,
                          source=__NAME__)

# The radial velocity measured from the wave solution FP CCF
KW_CCF_RV_WAVE_FP = Keyword('KW_CCF_RV_WAVE_FP', key='', dtype=float,
                            source=__NAME__)

# The radial velocity measured from a simultaneous FP CCF
#     (FP in reference channel)
KW_CCF_RV_SIMU_FP = Keyword('KW_CCF_RV_SIMU_FP', key='', dtype=float,
                            source=__NAME__)

# The radial velocity drift between wave sol FP and simultaneous FP (if present)
#   if simulataneous FP not present this is just the wave solution FP CCF value
KW_CCF_RV_DRIFT = Keyword('KW_CCF_RV_DRIFT', key='', dtype=float,
                          source=__NAME__)

# The radial velocity measured from the object CCF against the CCF MASK
KW_CCF_RV_OBJ = Keyword('KW_CCF_RV_OBJ', key='', dtype=float, source=__NAME__)

# the corrected radial velocity of the object (taking into account the FP RVs)
KW_CCF_RV_CORR = Keyword('KW_CCF_RV_CORR', key='', dtype=float, source=__NAME__)

# the wave file used for the rv (fiber specific)
KW_CCF_RV_WAVEFILE = Keyword('KW_CCF_RV_WAVEFILE', key='', dtype=str,
                             source=__NAME__)

# the wave file time used for the rv [mjd] (fiber specific)
KW_CCF_RV_WAVETIME = Keyword('KW_CCF_RV_WAVETIME', key='', dtype=str,
                             source=__NAME__)

# the time diff (in days) between wave file and file (fiber specific)
KW_CCF_RV_TIMEDIFF = Keyword('KW_CCF_RV_TIMEDIFF', key='', dtype=str,
                             source=__NAME__)

# the wave file source used for the rv reference fiber
KW_CCF_RV_WAVESRCE = Keyword('KW_CCF_RV_WAVESRCE', key='', dtype=str,
                             source=__NAME__)

# -----------------------------------------------------------------------------
# Define polar variables
# -----------------------------------------------------------------------------

# define the Stokes paremeter: Q, U, V, or I
KW_POL_STOKES = Keyword('KW_POL_STOKES', key='', dtype=str, source=__NAME__)

# define Number of exposures for polarimetry
KW_POL_NEXP = Keyword('KW_POL_NEXP', key='', dtype=int, source=__NAME__)

# defines the Polarimetry method
KW_POL_METHOD = Keyword('KW_POL_METHOD', key='', dtype=str, source=__NAME__)

# define the base file name exposure list
KW_POL_FILES = Keyword('KW_POL_FILES', key='', dtype=str, source=__NAME__)

# define the exposure times of exposure list
KW_POL_EXPS = Keyword('KW_POL_EXPS', key='', dtype=float, source=__NAME__)

# define the mjds at start for exposure list
KW_POL_MJDS = Keyword('KW_POL_MJDS', key='', dtype=float, source=__NAME__)

# define the mjdends at end for exposure list
KW_POL_MJDENDS = Keyword('KW_POL_MJDENDS', key='', dtype=float, source=__NAME__)

# define the bjds for exposure list
KW_POL_BJDS = Keyword('KW_POL_BJDS', key='', dtype=float, source=__NAME__)

# define the bervs for exposure list
KW_POL_BERVS = Keyword('KW_POL_BERVS', key='', dtype=float, source=__NAME__)

# define the Total exposure time (sec)
KW_POL_EXPTIME = Keyword('KW_POL_EXPTIME', key='', dtype=float, source=__NAME__)

# define the Elapsed time of observation (sec)
KW_POL_ELAPTIME = Keyword('KW_POL_ELAPTIME', key='', dtype=float,
                          source=__NAME__)

# define the MJD at center of observation
KW_POL_MJDCEN = Keyword('KW_POL_MJDCEN', key='', dtype=float, source=__NAME__)

# define the BJD at center of observation
KW_POL_BJDCEN = Keyword('KW_POL_BJDCEN', key='', dtype=float, source=__NAME__)

# define the BERV at center of observation
KW_POL_BERVCEN = Keyword('KW_POL_BERVCEN', key='', dtype=float, source=__NAME__)

# define the Mean BJD for polar sequence
KW_POL_MEANBJD = Keyword('KW_POL_MEANBJD', key='', dtype=float, source=__NAME__)

# define the minimum number of files used
KW_USED_MIN_FILES = Keyword('KW_USED_MIN_FILES', key='', dtype=int,
                            source=__NAME__)

# define all possible fibers for polarimetry used
KW_USED_VALID_FIBERS = Keyword('KW_USED_VALID_FIBERS', key='', dtype=str,
                               source=__NAME__)

# define all possible stokes parameters used
KW_USED_VALID_STOKES = Keyword('KW_USED_VALID_STOKES', key='', dtype=str,
                               source=__NAME__)

# define the continuum bin size used
KW_USED_CONT_BINSIZE = Keyword('KW_USED_CONT_BINSIZE', key='', dtype=int,
                               source=__NAME__)

# define the continuum overlap used
KW_USED_CONT_OVERLAP = Keyword('KW_USED_CONT_OVERLAP', key='', dtype=int,
                               source=__NAME__)

# define the LSD mask filename
KW_POLAR_LSD_MASK = Keyword('KW_POLAR_LSD_MASK', key='', dtype=str,
                            source=__NAME__)

# define the Radial velocity (km/s) from gaussian fit from polar lsd
KW_POLAR_LSD_FIT_RV = Keyword('KW_POLAR_LSD_FIT_RV', key='', dtype=float,
                              source=__NAME__)

# define the Resolving power from gaussian fit from polar lsd
KW_POLAR_LSD_FIT_RESOL = Keyword('KW_POLAR_LSD_FIT_RESOL', key='', dtype=float,
                                 source=__NAME__)

# define the Mean polarization of data in LSD
KW_POLAR_LSD_MEANPOL = Keyword('KW_POLAR_LSD_MEANPOL', key='', dtype=float,
                               source=__NAME__)

# define the Std dev polarization of data in LSD
KW_POLAR_LSD_STDPOL = Keyword('KW_POLAR_LSD_STDPOL', key='', dtype=float,
                              source=__NAME__)

# define the Median polarization of data in LSD
KW_POLAR_LSD_MEDPOL = Keyword('KW_POLAR_LSD_MEDPOL', key='', dtype=float,
                              source=__NAME__)

# define the Med abs dev polarization of data in LSD
KW_POLAR_LSD_MEDABSDEV = Keyword('KW_POLAR_LSD_MEDABSDEV', key='', dtype=float,
                                 source=__NAME__)

# define the mean of pol LSD profile
KW_POLAR_LSD_MEANSVQU = Keyword('KW_POLAR_LSD_MEANSVQU', key='', dtype=float,
                                source=__NAME__)

# define the Std dev of pol LSD profile
KW_POLAR_LSD_STDSVQU = Keyword('KW_POLAR_LSD_STDSVQU', key='', dtype=float,
                               source=__NAME__)

# define the Mean of null LSD profile
KW_POLAR_LSD_MEANNULL = Keyword('KW_POLAR_LSD_MEANNULL', key='', dtype=float,
                                source=__NAME__)

# define the Std dev of null LSD profile
KW_POLAR_LSD_STDNULL = Keyword('KW_POLAR_LSD_STDNULL', key='', dtype=float,
                               source=__NAME__)

# define the lsd column: Velocities (km/s)
KW_POL_LSD_COL1 = Keyword('KW_POL_LSD_COL1', key='', dtype=str, source=__NAME__)

# define the lsd column: Stokes I LSD profile
KW_POL_LSD_COL2 = Keyword('KW_POL_LSD_COL2', key='', dtype=str, source=__NAME__)

# define the lsd column: Gaussian fit to Stokes I LSD profile
KW_POL_LSD_COL3 = Keyword('KW_POL_LSD_COL3', key='', dtype=str, source=__NAME__)

# define the lsd column: Stokes V, U, or Q LSD profile
KW_POL_LSD_COL4 = Keyword('KW_POL_LSD_COL4', key='', dtype=str, source=__NAME__)

# define the lsd column: Null polarization LSD profile
KW_POL_LSD_COL5 = Keyword('KW_POL_LSD_COL5', key='', dtype=str, source=__NAME__)

# define the minimum line depth value used in LSD analysis
KW_POLAR_LSD_MLDEPTH = Keyword('KW_POLAR_LSD_MLDEPTH', key='', dtype=float,
                               source=__NAME__)

# Define initial velocity value used in LSD analysis
KW_POLAR_LSD_VINIT = Keyword('KW_POLAR_LSD_VINIT', key='', dtype=float,
                             source=__NAME__)

# Define final velocity value used in LSD analysis
KW_POLAR_LSD_VFINAL = Keyword('KW_POLAR_LSD_VFINAL', key='', dtype=float,
                              source=__NAME__)

# Define whether stokesI was normalised by continuum
KW_POLAR_LSD_NORM = Keyword('KW_POLAR_LSD_NORM', key='', dtype=bool,
                            source=__NAME__)

# define the bin size used for norm continuum
KW_POLAR_LSD_NBIN1 = Keyword('KW_POLAR_LSD_NBIN1', key='', dtype=int,
                             source=__NAME__)

# define the overlap used for norm continuum
KW_POLAR_LSD_NLAP1 = Keyword('KW_POLAR_LSD_NLAP1', key='', dtype=int,
                             source=__NAME__)

# define the sig clip used for norm continuum
KW_POLAR_LSD_NSIG1 = Keyword('KW_POLAR_LSD_NSIG1', key='', dtype=float,
                             source=__NAME__)

# define the window size used for norm continuum
KW_POLAR_LSD_NWIN1 = Keyword('KW_POLAR_LSD_NWIN1', key='', dtype=int,
                             source=__NAME__)

# define the mode used for norm continuum
KW_POLAR_LSD_NMODE1 = Keyword('KW_POLAR_LSD_NMODE1', key='', dtype=str,
                              source=__NAME__)

# define whether a linear fit was used for norm continuum
KW_POLAR_LSD_NLFIT1 = Keyword('KW_POLAR_LSD_NLFIT1', key='', dtype=bool,
                              source=__NAME__)

# define the Number of points for LSD profile
KW_POLAR_LSD_NPOINTS = Keyword('KW_POLAR_LSD_NPOINTS', key='', dtype=int,
                               source=__NAME__)

# define the bin sized used in profile calc
KW_POLAR_LSD_NBIN2 = Keyword('KW_POLAR_LSD_NBIN2', key='', dtype=int,
                             source=__NAME__)

# define the overlap used in profile calc
KW_POLAR_LSD_NLAP2 = Keyword('KW_POLAR_LSD_NLAP2', key='', dtype=int,
                             source=__NAME__)

# define the sigma clip used in profile calc
KW_POLAR_LSD_NSIG2 = Keyword('KW_POLAR_LSD_NSIG2', key='', dtype=float,
                             source=__NAME__)

# define the window size used in profile calc
KW_POLAR_LSD_NWIN2 = Keyword('KW_POLAR_LSD_NWIN2', key='', dtype=int,
                             source=__NAME__)

# define the mode used in profile calc
KW_POLAR_LSD_NMODE2 = Keyword('KW_POLAR_LSD_NMODE2', key='', dtype=str,
                              source=__NAME__)

# define whether a linear fit was used in profile calc
KW_POLAR_LSD_NLFIT2 = Keyword('KW_POLAR_LSD_NLFIT2', key='', dtype=bool,
                              source=__NAME__)

# =============================================================================
#  End of configuration file
# =============================================================================
