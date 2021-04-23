# This is the main config file
from apero.base import base
from apero.core.constants import constant_functions

# -----------------------------------------------------------------------------
# Define variables
# -----------------------------------------------------------------------------
# all definition
__all__ = [  # input keys
    'KW_ACQTIME', 'KW_OBJRA', 'KW_OBJDEC', 'KW_OBJNAME', 'KW_OBJEQUIN',
    'KW_OBJRAPM', 'KW_OBJDECPM', 'KW_RDNOISE', 'KW_GAIN', 'KW_EXPTIME',
    'KW_UTC_OBS', 'KW_EXPTIME_UNITS', 'KW_OBSTYPE', 'KW_CCAS', 'KW_EXPREQ',
    'KW_CREF', 'KW_CDEN', 'KW_CMMTSEQ', 'KW_AIRMASS', 'KW_MJDEND', 'KW_MJDATE',
    'KW_CMPLTEXP', 'KW_NEXP', 'KW_PI_NAME', 'KW_PLX', 'KW_CALIBWH',
    'KW_TARGET_TYPE', 'KW_WEATHER_TOWER_TEMP', 'KW_CASS_TEMP',
    'KW_HUMIDITY', 'KW_GAIA_ID', 'KW_GAIA_DR', 'KW_INPUTRV', 'KW_OBJ_TEMP',
    'KW_POLAR_KEY_1', 'KW_POLAR_KEY_2',
    'KW_SATURATE', 'KW_FRMTIME', 'KW_OBJECTNAME', 'KW_IDENTIFIER',
    'KW_RAW_DPRTYPE',
    # object resolution keys
    'KW_DRS_OBJNAME', 'KW_DRS_OBJNAME_S', 'KW_DRS_GAIAID', 'KW_DRS_GAIAID_S',
    'KW_DRS_RA', 'KW_DRS_RA_S', 'KW_DRS_DEC', 'KW_DRS_DEC_S',
    'KW_DRS_PMRA', 'KW_DRS_PMRA_S', 'KW_DRS_PMDE', 'KW_DRS_PMDE_S',
    'KW_DRS_PLX', 'KW_DRS_PLX_S', 'KW_DRS_RV', 'KW_DRS_RV_S',
    'KW_DRS_GMAG', 'KW_DRS_GMAG_S', 'KW_DRS_BPMAG', 'KW_DRS_BPMAG_S',
    'KW_DRS_RPMAG', 'KW_DRS_RPMAG_S', 'KW_DRS_EPOCH', 'KW_DRS_EPOCH_S',
    'KW_DRS_TEFF', 'KW_DRS_TEFF_S',
    # general output keys
    'KW_VERSION', 'KW_PPVERSION', 'KW_DPRTYPE', 'KW_PID', 'KW_DRS_MODE',
    'KW_INFILE1', 'KW_INFILE2', 'KW_INFILE3', 'KW_DRS_MODE',
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
    'KW_PPC_NBAD_INTE', 'KW_PPC_NBAD_SLOPE', 'KW_PPC_NBAD_BOTH',
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
    # wave resolution map variables
    'KW_RESMAP_NBO', 'KW_RESMAP_NBPIX', 'KW_RESMAP_BINORD', 'KW_RESMAP_NBINORD',
    'KW_RESMAP_BINPIX', 'KW_RESMAP_NBINPIX', 'KW_RES_MAP_ORDLOW',
    'KW_RES_MAP_ORDHIGH', 'KW_RES_MAP_PIXLOW', 'KW_RES_MAP_PIXHIGH',
    'KW_RES_MAP_FWHM', 'KW_RES_MAP_AMP', 'KW_RES_MAP_EXPO', 'KW_RES_MAP_RESEFF',
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
    'KW_MKTELL_TEMP_FILE', 'KW_MKTELL_TEMPNUM', 'KW_MKTELL_TEMPHASH',
    'KW_MKTELL_TEMPTIME', 'KW_MKTELL_BLAZE_PRCT', 'KW_MKTELL_BLAZE_CUT',
    'KW_MKTELL_DEF_CONV_WID', 'KW_MKTELL_TEMP_MEDFILT', 'KW_MKTELL_AIRMASS',
    'KW_MKTELL_WATER', 'KW_MKTELL_THRES_TFIT', 'KW_MKTELL_TRANS_FIT_UPPER_BAD',
    # fittellu values
    'KW_FTELLU_NPC', 'KW_FTELLU_ADD_DPC', 'KW_FTELLU_FIT_DPC',
    'KW_FTELLU_ABSO_SRC', 'KW_FTELLU_FIT_KEEP_NUM',
    'KW_FTELLU_FIT_MIN_TRANS', 'KW_FTELLU_LAMBDA_MIN',
    'KW_FTELLU_LAMBDA_MAX', 'KW_FTELLU_KERN_VSINI',
    'KW_FTELLU_IM_PX_SIZE', 'KW_FTELLU_FIT_ITERS', 'KW_FTELLU_RECON_LIM',
    'KW_FTELLU_AMP_PC', 'KW_FTELLU_DVTELL1', 'KW_FTELLU_DVTELL2',
    'KW_FTELLU_TAU_H2O', 'KW_FTELLU_TAU_REST', 'KW_FTELLU_ABSO_PREFIX',
    'KW_FTELLU_TEMPLATE', 'KW_FTELLU_TEMPNUM', 'KW_FTELLU_TEMPHASH',
    'KW_FTELLU_TEMPTIME', 'KW_FTELLU_NTRANS',
    # make template values
    'KW_MKTEMP_NFILES', 'KW_MKTEMP_HASH', 'KW_MKTEMP_TIME',
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
    'KW_CCF_DVRMS_CC', 'KW_MKTEMP_BERV_COV', 'KW_MKTEMP_BERV_COV_MIN',
    'KW_MKTEMP_BERV_COV_SNR', 'KW_MKTEMP_BERV_COV_RES',
    # polar values
    'KW_POL_STOKES', 'KW_POL_NEXP', 'KW_POL_METHOD', 'KW_POL_ELAPTIME',
    'KW_POL_MJDCEN', 'KW_POL_BJDCEN', 'KW_POL_BERVCEN',
    'KW_POL_MEAN_MJD', 'KW_POL_MEAN_BJD', 'KW_POL_MEAN_BERV',
    'KW_POL_EXPTIME', 'KW_POL_MJD_FW_CEN', 'KW_POL_BJD_FW_CEN',
    'KW_POL_CORR_BERV', 'KW_POL_CORR_SRV', 'KW_POL_NORM_STOKESI',
    'KW_POL_INTERP_FLUX', 'KW_POL_SIGCLIP', 'KW_POL_NSIGMA',
    'KW_POL_REMOVE_CONT', 'KW_POL_SCONT_DET_ALG', 'KW_POL_PCONT_DET_ALG',
    'KW_POL_CONT_POLYFIT', 'KW_POL_CONT_DEG_POLY',
    'KW_POL_S_IRAF_FUNC', 'KW_POL_P_IRAF_FUNC', 'KW_POL_S_IRAF_DEGREE',
    'KW_POL_P_IRAF_DEGREE', 'KW_POL_CONT_BINSIZE', 'KW_POL_CONT_OVERLAP',
    'KW_POL_CONT_TELLMASK',
    # polar lsd values
    'KW_LSD_ORIGIN', 'KW_LSD_FIT_RV', 'KW_LSD_POL_MEAN', 'KW_LSD_POL_STDDEV',
    'KW_LSD_POL_MEDIAN', 'KW_LSD_POL_MEDABSDEV', 'KW_LSD_STOKESVQU_MEAN',
    'KW_LSD_STOKESVQU_STDDEV', 'KW_LSD_NULL_MEAN', 'KW_LSD_NULL_STDDEV',
    'KW_LSD_MASK_FILE', 'KW_LSD_MASK_NUMLINES', 'KW_LSD_MASKLINES_USED',
    'KW_LSD_MASKLINES_MWAVE', 'KW_LSD_MASKLINES_MLANDE'
]

# set name
__NAME__ = 'apero.constants.default.default_keywords'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Constants definition
Const = constant_functions.Const
# Keyword defintion
Keyword = constant_functions.Keyword

# -----------------------------------------------------------------------------
# Required header keys (general)
# -----------------------------------------------------------------------------
# Define the header key that uniquely identifies the file
#     (i.e. an odometer code)
KW_IDENTIFIER = Keyword('KW_IDENTIFIER', key='', value=None, source=__NAME__,
                        description=('Define the header key that uniquely '
                                     'identifies the file (i.e. an odometer '
                                     'code)'))

# define the HEADER key for acquisition time
#     Note must set the date format in KW_ACQTIME_FMT
KW_ACQTIME = Keyword('KW_ACQTIME', key='', value=None, source=__NAME__,
                     description=('define the HEADER key for acquisition time '
                                  'Note must set the date format in '
                                  'KW_ACQTIME_FMT'))

# define the MJ end date HEADER key
KW_MJDEND = Keyword('KW_MJDEND', key='', value=None, source=__NAME__,
                    description='define the MJ end date HEADER key')

# define the MJ date HEADER key (only used for logging)
KW_MJDATE = Keyword('KW_MJDATE', key='', value=None, source=__NAME__,
                    description='define the MJ date HEADER key (only used '
                                'for logging)')

# define the observation date HEADER key
KW_DATE_OBS = Keyword('KW_DATE_OBS', key='', dtype=float, source=__NAME__,
                      description='define the observation date HEADER key')
# define the observation time HEADER key
KW_UTC_OBS = Keyword('KW_UTC_OBS', key='', dtype=float, source=__NAME__,
                     description='define the observation time HEADER key')

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KW_RDNOISE = Keyword('KW_RDNOISE', key='', dtype=float, source=__NAME__,
                     description=('define the read noise HEADER key a.k.a '
                                  'sigdet (used to get value only)'))

# define the gain HEADER key (used to get value only)
KW_GAIN = Keyword('KW_GAIN', key='', dtype=float, source=__NAME__,
                  description=('define the gain HEADER key (used to get '
                               'value only)'))

# define the saturation limit HEADER key
KW_SATURATE = Keyword('KW_SATURATE', key='', dtype=float, source=__NAME__,
                      description='define the saturation limit HEADER key')

# define the frame time HEADER key
KW_FRMTIME = Keyword('KW_FRMTIME', key='', dtype=float, source=__NAME__,
                     description='define the frame time HEADER key')

# define the exposure time HEADER key (used to get value only)
KW_EXPTIME = Keyword('KW_EXPTIME', key='', dtype=float, source=__NAME__,
                     description=('define the exposure time HEADER key '
                                  '(used to get value only)'))
# This is the units for the exposure time
KW_EXPTIME_UNITS = Const('KW_EXPTIME_UNITS', value='s', dtype=str,
                         options=['s', 'min', 'hr', 'day'],
                         source=__NAME__,
                         description=('This is the units for the exposure '
                                      'time'))

# define the required exposure time HEADER key (used to get value only)
KW_EXPREQ = Keyword('KW_EXPREQ', key='', dtype=float, source=__NAME__,
                    description=('define the required exposure time HEADER '
                                 'key (used to get value only)'))

# define the observation type HEADER key
KW_OBSTYPE = Keyword('KW_OBSTYPE', key='', dtype=str, source=__NAME__,
                     description='define the observation type HEADER key')

# define the science fiber type HEADER key
KW_CCAS = Keyword('KW_CCAS', key='', dtype=str, source=__NAME__,
                  description='define the science fiber type HEADER key')

# define the reference fiber type HEADER key
KW_CREF = Keyword('KW_CREF', key='', dtype=str, source=__NAME__,
                  description='define the reference fiber type HEADER key')

# define the calibration wheel position
KW_CALIBWH = Keyword('KW_CALIBWH', key='', dtype=str, source=__NAME__,
                     description='define the calibration wheel position')

# define the target type (object/sky)
KW_TARGET_TYPE = Keyword('KW_TARGET_TYPE', key='', dtype=str, source=__NAME__,
                         description='define the target type (object/sky)')

# define the density HEADER key
KW_CDEN = Keyword('KW_CDEN', key='', dtype=str, source=__NAME__,
                  description='define the density HEADER key')

# define polarisation HEADER key
KW_CMMTSEQ = Keyword('KW_CMMTSEQ', key='', dtype=str, source=__NAME__,
                     description='define polarisation HEADER key')

# define the exposure number within sequence HEADER key
KW_CMPLTEXP = Keyword('KW_CMPLTEXP', key='', dtype=int, source=__NAME__,
                      description=('define the exposure number within sequence '
                                   'HEADER key'))

# define the total number of exposures HEADER key
KW_NEXP = Keyword('KW_NEXP', key='', dtype=int, source=__NAME__,
                  description=('define the total number of exposures HEADER '
                               'key'))

# define the pi name HEADER key
KW_PI_NAME = Keyword('KW_PI_NAME', key='', dtype=str, source=__NAME__,
                     description='define the pi name HEADER key')

# define the raw dprtype from the telescope (if given)
KW_RAW_DPRTYPE = Keyword('KW_RAW_DPRTYPE', key='', dtype=str, source=__NAME__)

# -----------------------------------------------------------------------------
# Required header keys (related to science object)
# -----------------------------------------------------------------------------
# define the observation ra HEADER key
KW_OBJRA = Keyword('KW_OBJRA', key='', dtype=float, source=__NAME__,
                   description='define the observation ra HEADER key')

# define the observation dec HEADER key
KW_OBJDEC = Keyword('KW_OBJDEC', key='', dtype=float, source=__NAME__,
                    description='define the observation dec HEADER key')

# define the observation name
KW_OBJNAME = Keyword('KW_OBJNAME', key='', dtype=str, source=__NAME__,
                     description='define the observation name')

# define the raw observation name
KW_OBJECTNAME = Keyword('KW_OBJECTNAME', key='', dtype=str, source=__NAME__,
                        description='define the raw observation name')

# define the gaia id
KW_GAIA_ID = Keyword('KW_GAIA_ID', key='', dtype=str, source=__NAME__,
                     description='define the gaia id')

# define the gaia data release key
KW_GAIA_DR = Keyword('KW_GAIA_DR', key='', dtype=str, source=__NAME__,
                     description='define the gaia data release key')

# define the observation equinox HEADER key
KW_OBJEQUIN = Keyword('KW_OBJEQUIN', key='', dtype=float, source=__NAME__,
                      description='define the observation equinox HEADER key')

# define the observation proper motion in ra HEADER key
KW_OBJRAPM = Keyword('KW_OBJRAPM', key='', dtype=float, source=__NAME__,
                     description=('define the observation proper motion in ra '
                                  'HEADER key'))

# define the observation proper motion in dec HEADER key
KW_OBJDECPM = Keyword('KW_OBJDECPM', key='', dtype=float, source=__NAME__,
                      description=('define the observation proper motion in dec '
                                   'HEADER key'))

# define the airmass HEADER key
KW_AIRMASS = Keyword('KW_AIRMASS', key='', dtype=float, source=__NAME__,
                     description='define the airmass HEADER key')

# define the weather tower temperature HEADER key
KW_WEATHER_TOWER_TEMP = Keyword('KW_WEATHER_TOWER_TEMP', key='', dtype=float,
                                source=__NAME__,
                                description=('define the weather tower '
                                             'temperature HEADER key'))

# define the cassegrain temperature HEADER key
KW_CASS_TEMP = Keyword('KW_CASS_TEMP', key='', dtype=float, source=__NAME__,
                       description=('define the cassegrain temperature '
                                    'HEADER key'))

# define the humidity HEADER key
KW_HUMIDITY = Keyword('KW_HUMIDITY', key='', dtype=float, source=__NAME__,
                      description='define the humidity HEADER key')

# define the parallax HEADER key
KW_PLX = Keyword('KW_PLX', key='', dtype=float, source=__NAME__,
                 description='define the parallax HEADER key')

# define the rv HEADER key
KW_INPUTRV = Keyword('KW_INPUTRV', key='', dtype=float, source=__NAME__,
                     description='define the rv HEADER key')

# define the object temperature HEADER key
KW_OBJ_TEMP = Keyword('KW_OBJ_TEMP', key='', dtype=float, source=__NAME__,
                      description='define the object temperature HEADER key')

# define the first polar sequence key
KW_POLAR_KEY_1 = Keyword('KW_POLAR_KEY_1', key='', dtype=str, source=__NAME__,
                         description='define the first polar sequence key')

# define the second polar sequence key
KW_POLAR_KEY_2 = Keyword('KW_POLAR_KEY_2', key='', dtype=str, source=__NAME__,
                         description='define the first polar sequence key')

# -----------------------------------------------------------------------------
# Object resolution keys
# -----------------------------------------------------------------------------
# the object name to be used by the drs (after preprocessing)
KW_DRS_OBJNAME = Keyword('KW_DRS_OBJNAME', key='', dtype=str, source=__NAME__,
                         description=('the object name to be used by the '
                                      'drs (after preprocessing)'))

# the source of the object name used by the drs
KW_DRS_OBJNAME_S = Keyword('KW_DRS_OBJNAME_S', key='', dtype=str,
                           source=__NAME__,
                           description=('the source of the object name used '
                                        'by the drs'))

# the gaia id to be used by the drs (after preprocessing)
KW_DRS_GAIAID = Keyword('KW_DRS_GAIAID', key='', dtype=str, source=__NAME__,
                        description=('the gaia id to be used by the drs '
                                     '(after preprocessing)'))

# the source of the gaia id to be used by the drs (after preprocessing)
KW_DRS_GAIAID_S = Keyword('KW_DRS_GAIAID_S', key='', dtype=str, source=__NAME__,
                          description=('the source of the gaia id to be used '
                                       'by the drs (after preprocessing)'))

# the right ascension to be used by the drs (after preprocessing)
KW_DRS_RA = Keyword('KW_DRS_RA', key='', dtype=float, source=__NAME__,
                    description=('the right ascension to be used by the drs '
                                 '(after preprocessing)'))

# the source of the ra to be used by the drs (after preprocessing)
KW_DRS_RA_S = Keyword('KW_DRS_RA_S', key='', dtype=str, source=__NAME__,
                      description=('the source of the ra to be used by the drs '
                                   '(after preprocessing)'))

# the declination to be used by the drs (after preprocessing)
KW_DRS_DEC = Keyword('KW_DRS_DEC', key='', dtype=float, source=__NAME__,
                     description=('the declination to be used by the drs '
                                  '(after preprocessing)'))

# the source of the dec to be used by the drs (after preprocessing)
KW_DRS_DEC_S = Keyword('KW_DRS_DEC_S', key='', dtype=str, source=__NAME__,
                       description=('the source of the dec to be used by the '
                                    'drs (after preprocessing)'))

# the proper motion in ra to be used by the drs (after preprocessing)
KW_DRS_PMRA = Keyword('KW_DRS_PMRA', key='', dtype=float, source=__NAME__,
                      description=('the proper motion in ra to be used by the '
                                   'drs (after preprocessing)'))

# the source of the pmra used by the drs (afer prepreocessing)
KW_DRS_PMRA_S = Keyword('KW_DRS_PMRA_S', key='', dtype=str, source=__NAME__,
                        description=('the source of the pmra used by the drs '
                                     '(afer prepreocessing)'))

# the proper motion in dec to be used by the drs (after preprocessing)
KW_DRS_PMDE = Keyword('KW_DRS_PMDE', key='', dtype=float, source=__NAME__,
                      description=('the proper motion in dec to be used by the '
                                   'drs (after preprocessing)'))

# the source of the pmde used by the drs (after preprocessing)
KW_DRS_PMDE_S = Keyword('KW_DRS_PMDE_S', key='', dtype=str, source=__NAME__,
                        description=('the source of the pmde used by the drs '
                                     '(after preprocessing)'))

# the parallax to be used by the drs (after preprocessing)
KW_DRS_PLX = Keyword('KW_DRS_PLX', key='', dtype=float, source=__NAME__,
                     description=('the parallax to be used by the drs '
                                  '(after preprocessing)'))

# the source of the parallax used by the drs (after preprocessing)
KW_DRS_PLX_S = Keyword('KW_DRS_PLX_S', key='', dtype=str, source=__NAME__,
                       description=('the source of the parallax used by the '
                                    'drs (after preprocessing)'))

# the radial velocity to be used by the drs (after preprocessing)
KW_DRS_RV = Keyword('KW_DRS_RV', key='', dtype=float, source=__NAME__,
                    description=('the radial velocity to be used by the drs '
                                 '(after preprocessing)'))

# the source of the radial velocity used by the drs (after preprocessing)
KW_DRS_RV_S = Keyword('KW_DRS_RV_S', key='', dtype=str, source=__NAME__,
                      description=('the source of the radial velocity used by '
                                   'the drs (after preprocessing)'))

# the Gaia G magnitude to be used by the drs (after preprocessing)
KW_DRS_GMAG = Keyword('KW_DRS_GMAG', key='', dtype=float, source=__NAME__,
                      description=('the Gaia G magnitude to be used by the '
                                   'drs (after preprocessing)'))

# the source of the gmag used by the drs (after preprocessing)
KW_DRS_GMAG_S = Keyword('KW_DRS_GMAG_S', key='', dtype=str, source=__NAME__,
                        description=('the source of the gmag used by the drs '
                                     '(after preprocessing)'))

# the Gaia BP magnitude to be used by the drs (after preprocessing)
KW_DRS_BPMAG = Keyword('KW_DRS_BPMAG', key='', dtype=float, source=__NAME__,
                       description=('the Gaia BP magnitude to be used by the '
                                    'drs (after preprocessing)'))

# the source of the bpmag used by the drs (after preprocessing)
KW_DRS_BPMAG_S = Keyword('KW_DRS_BPMAG_S', key='', dtype=str, source=__NAME__,
                         description=('the source of the bpmag used by the '
                                      'drs (after preprocessing)'))

# the Gaia RP magnitude to be used by the drs (after preprocessing)
KW_DRS_RPMAG = Keyword('KW_DRS_RPMAG', key='', dtype=float, source=__NAME__,
                       description=('the Gaia RP magnitude to be used by the '
                                    'drs (after preprocessing)'))

# the source of the rpmag used by the drs (after preprocessing)
KW_DRS_RPMAG_S = Keyword('KW_DRS_RPMAG_S', key='', dtype=str, source=__NAME__,
                         description=('the source of the rpmag used by the drs '
                                      '(after preprocessing)'))

# the epoch to be used by the drs (after preprocessing)
KW_DRS_EPOCH = Keyword('KW_DRS_EPOCH', key='', dtype=float, source=__NAME__,
                       description=('the epoch to be used by the drs (after '
                                    'preprocessing)'))

# the source of the epoch used by the drs (after preprocessing)
KW_DRS_EPOCH_S = Keyword('KW_DRS_EPOCH_S', key='', dtype=str, source=__NAME__,
                         description=('the source of the epoch used by the drs '
                                      '(after preprocessing)'))

# the effective temperature to be used by the drs (after preprocessing)
KW_DRS_TEFF = Keyword('KW_DRS_TEFF', key='', dtype=float, source=__NAME__,
                      description=('the effective temperature to be used by '
                                   'the drs (after preprocessing)'))

# the source of teff used by the drs (after preprocessing)
KW_DRS_TEFF_S = Keyword('KW_DRS_TEFF_S', key='', dtype=str, source=__NAME__,
                        description=('the source of teff used by the drs '
                                     '(after preprocessing)'))

# -----------------------------------------------------------------------------
# Define general keywords
# -----------------------------------------------------------------------------
# DRS version
KW_VERSION = Keyword('KW_VERSION', key='', dtype=str, source=__NAME__,
                     description='DRS version')

# DRS preprocessing version
KW_PPVERSION = Keyword('KW_PPVERSION', key='', dtype=str, source=__NAME__,
                       description='DRS preprocessing version')

# DRS process ID
KW_PID = Keyword('KW_PID', key='', dtype=str, source=__NAME__,
                 description='DRS process ID')

# Processed date keyword
KW_DRS_DATE_NOW = Keyword('KW_DRS_DATE_NOW', key='', dtype=str,
                          source=__NAME__,
                          description='Processed date keyword')

# DRS version date keyword
KW_DRS_DATE = Keyword('KW_DRS_DATE', key='', dtype=str, source=__NAME__,
                      description='DRS version date keyword')

# Define the key to get the data fits file type
KW_DPRTYPE = Keyword('KW_DPRTYPE', key='', dtype=str, source=__NAME__,
                     description=('Define the key to get the data fits '
                                  'file type'))

# Define the key to get the drs mode
KW_DRS_MODE = Keyword('KW_DRS_MODE', key='', dtype=str, source=__NAME__,
                      description='Define the key to get the drs mode')

# Define the mid exposure time
KW_MID_OBS_TIME = Keyword('KW_MID_OBS_TIME', key='', source=__NAME__,
                          description='Define the mid exposure time')

# Define the method by which the MJD was calculated
KW_MID_OBSTIME_METHOD = Keyword('KW_MID_OBSTIME_METHOD', key='', dtype=str,
                                source=__NAME__,
                                description=('Define the method by which the '
                                             'MJD was calculated'))

# -----------------------------------------------------------------------------
# Define DRS input keywords
# -----------------------------------------------------------------------------
# input files
KW_INFILE1 = Keyword('KW_INFILE1', key='', dtype=str, source=__NAME__,
                     description='input files')
KW_INFILE2 = Keyword('KW_INFILE2', key='', dtype=str, source=__NAME__,
                     description='input files')
KW_INFILE3 = Keyword('KW_INFILE3', key='', dtype=str, source=__NAME__,
                     description='input files')

# -----------------------------------------------------------------------------
# Define database input keywords
# -----------------------------------------------------------------------------
# dark calibration file used
KW_CDBDARK = Keyword('KW_CDBDARK', key='', dtype=str, source=__NAME__,
                     description='dark calibration file used')
# bad pixel calibration file used
KW_CDBBAD = Keyword('KW_CDBBAD', key='', dtype=str, source=__NAME__,
                    description='bad pixel calibration file used')
# background calibration file used
KW_CDBBACK = Keyword('KW_CDBBACK', key='', dtype=str, source=__NAME__,
                     description='background calibration file used')
# order profile calibration file used
KW_CDBORDP = Keyword('KW_CDBORDP', key='', dtype=str, source=__NAME__,
                     description='order profile calibration file used')
# localisation calibration file used
KW_CDBLOCO = Keyword('KW_CDBLOCO', key='', dtype=str, source=__NAME__,
                     description='localisation calibration file used')
# shape local calibration file used
KW_CDBSHAPEL = Keyword('KW_CDBSHAPEL', key='', dtype=str, source=__NAME__,
                       description='shape local calibration file used')
# shape dy calibration file used
KW_CDBSHAPEDY = Keyword('KW_CDBSHAPEDY', key='', dtype=str, source=__NAME__,
                        description='shape dy calibration file used')
# shape dx calibration file used
KW_CDBSHAPEDX = Keyword('KW_CDBSHAPEDX', key='', dtype=str, source=__NAME__,
                        description='shape dx calibration file used')
# flat calibration file used
KW_CDBFLAT = Keyword('KW_CDBFLAT', key='', dtype=str, source=__NAME__,
                     description='flat calibration file used')
# blaze calibration file used
KW_CDBBLAZE = Keyword('KW_CDBBLAZE', key='', dtype=str, source=__NAME__,
                      description='blaze calibration file used')
# wave solution calibration file used
KW_CDBWAVE = Keyword('KW_CDBWAVE', key='', dtype=str, source=__NAME__,
                     description='wave solution calibration file used')
# thermal calibration file used
KW_CDBTHERMAL = Keyword('KW_CDBTHERMAL', key='', dtype=str, source=__NAME__,
                        description='thermal calibration file used')

# additional properties of calibration

# whether the calibrations have been flipped
KW_C_FLIP = Keyword('KW_C_FLIP', key='', dtype=str, source=__NAME__,
                    description='whether the calibrations have been flipped')
# whether the calibratoins have been converted to electrons
KW_C_CVRTE = Keyword('KW_C_CVRTE', key='', dtype=str, source=__NAME__,
                     description='whether the calibratoins have been converted '
                                 'to electrons')
# whether the calibrations have been resized
KW_C_RESIZE = Keyword('KW_C_RESIZE', key='', dtype=str, source=__NAME__,
                      description='whether the calibrations have been resized')
# whether the calibrations have an ftype
KW_C_FTYPE = Keyword('KW_C_FTYPE', key='', dtype=str, source=__NAME__,
                     description='whether the calibrations have an ftype')
# the fiber name
KW_FIBER = Keyword('KW_FIBER', key='', dtype=str, source=__NAME__,
                   description='the fiber name')

# -----------------------------------------------------------------------------
# Define DRS outputs keywords
# -----------------------------------------------------------------------------
# the output key for drs outputs
KW_OUTPUT = Keyword('KW_OUTPUT', key='', dtype=str, source=__NAME__,
                    description='the output key for drs outputs')

# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
# the drs qc
KW_DRS_QC = Keyword('KW_DRS_QC', key='', dtype=str, source=__NAME__,
                    description='the drs qc ')
# the value of the qc
KW_DRS_QC_VAL = Keyword('KW_DRS_QC_VAL', key='', dtype=str, source=__NAME__,
                        description='the value of the qc')
# the name of the quality control parameter
KW_DRS_QC_NAME = Keyword('KW_DRS_QC_NAME', key='', dtype=str, source=__NAME__,
                         description='the name of the quality control '
                                     'parameter')
# the logic of the quality control parameter
KW_DRS_QC_LOGIC = Keyword('KW_DRS_QC_LOGIC', key='', dtype=str, source=__NAME__,
                          description='the logic of the quality control '
                                      'parameter')
# whether this quality control parameter passed
KW_DRS_QC_PASS = Keyword('KW_DRS_QC_PASS', key='', dtype=str, source=__NAME__,
                         description='whether this quality control parameter '
                                     'passed')

# -----------------------------------------------------------------------------
# Define preprocessing variables
# -----------------------------------------------------------------------------
# The shift in pixels so that image is at same location as engineering flat
KW_PPSHIFTX = Keyword('KW_PPSHIFTX', key='', dtype=float, source=__NAME__,
                      description=('The shift in pixels so that image is at '
                                   'same location as engineering flat'))
KW_PPSHIFTY = Keyword('KW_PPSHIFTY', key='', dtype=float, source=__NAME__,
                      description=('The shift in pixels so that image is at '
                                   'same location as engineering flat'))

# the number of bad pixels found via the intercept (cosmic ray rejection)
KW_PPC_NBAD_INTE = Keyword('KW_PPC_NBAD_INTE', key='', dtype=int,
                           source=__NAME__,
                           description=('the number of bad pixels found via '
                                        'the intercept (cosmic ray rejection)'))

# the number of bad pixels found via the slope (cosmic ray rejection)
KW_PPC_NBAD_SLOPE = Keyword('KW_PPC_NBAD_INTE', key='', dtype=int,
                           source=__NAME__,
                           description=('the number of bad pixels found via '
                                        'the slope (cosmic ray rejection)'))

# the number of bad pixels found with both intercept and slope (cosmic ray)
KW_PPC_NBAD_BOTH = Keyword('KW_PPC_NBAD_INTE', key='', dtype=int,
                           source=__NAME__,
                           description=('the number of bad pixels found with '
                                        'both intercept and slope (cosmic '
                                        'ray)'))

# The number of sigma used to construct pp master mask
KW_PPMSTR_NSIG = Keyword('KW_PPMSTR_NSIG', key='', dtype=float, source=__NAME__,
                         description=('The number of sigma used to construct '
                                      'pp master mask'))

# Define the key to store the name of the pp master file used in pp (if used)
KW_PPMSTR_FILE = Keyword('KW_PPMSTR_FILE', key='', dtype=str, source=__NAME__,
                         description=('Define the key to store the name of the '
                                      'pp master file used in pp (if used)'))

# -----------------------------------------------------------------------------
# Define apero_dark variables
# -----------------------------------------------------------------------------
# The fraction of dead pixels in the dark (in %)
KW_DARK_DEAD = Keyword('KW_DARK_DEAD', key='', dtype=float, source=__NAME__,
                       description=('The fraction of dead pixels in the dark '
                                    '(in %)'))

# The median dark level in ADU/s
KW_DARK_MED = Keyword('KW_DARK_MED', key='', dtype=float, source=__NAME__,
                      description='The median dark level in ADU/s')

# The fraction of dead pixels in the blue part of the dark (in %)
KW_DARK_B_DEAD = Keyword('KW_DARK_B_DEAD', key='', dtype=float, source=__NAME__,
                         description=('The fraction of dead pixels in the blue '
                                      'part of the dark (in %)'))

# The median dark level in the blue part of the dark in ADU/s
KW_DARK_B_MED = Keyword('KW_DARK_B_MED', key='', dtype=float, source=__NAME__,
                        description=('The median dark level in the blue part '
                                     'of the dark in ADU/s'))

# The fraction of dead pixels in the red part of the dark (in %)
KW_DARK_R_DEAD = Keyword('KW_DARK_R_DEAD', key='', dtype=float, source=__NAME__,
                         description=('The fraction of dead pixels in the red '
                                      'part of the dark (in %)'))

# The median dark level in the red part of the dark in ADU/s
KW_DARK_R_MED = Keyword('KW_DARK_R_MED', key='', dtype=float, source=__NAME__,
                        description=('The median dark level in the red part of '
                                     'the dark in ADU/s'))

# The threshold of the dark level to retain in ADU
KW_DARK_CUT = Keyword('KW_DARK_CUT', key='', dtype=float, source=__NAME__,
                      description=('The threshold of the dark level to retain '
                                   'in ADU'))

# -----------------------------------------------------------------------------
# Define apero_badpix variables
# -----------------------------------------------------------------------------
# fraction of hot pixels
KW_BHOT = Keyword('KW_BHOT', key='', dtype=float, source=__NAME__,
                  description='fraction of hot pixels')

# fraction of bad pixels from flat
KW_BBFLAT = Keyword('KW_BBFLAT', key='', dtype=float, source=__NAME__,
                    description='fraction of bad pixels from flat')

# fraction of non-finite pixels in dark
KW_BNDARK = Keyword('KW_BNDARK', key='', dtype=float, source=__NAME__,
                    description='fraction of non-finite pixels in dark')

# fraction of non-finite pixels in flat
KW_BNFLAT = Keyword('KW_BNFLAT', key='', dtype=float, source=__NAME__,
                    description='fraction of non-finite pixels in flat')

# fraction of bad pixels with all criteria
KW_BBAD = Keyword('KW_BBAD', key='', dtype=float, source=__NAME__,
                  description='fraction of bad pixels with all criteria')

# fraction of un-illuminated pixels (from engineering flat)
KW_BNILUM = Keyword('KW_BNILUM', key='', dtype=float, source=__NAME__,
                    description=('fraction of un-illuminated pixels (from '
                                 'engineering flat)'))

# fraction of total bad pixels
KW_BTOT = Keyword('KW_BTOT', key='', dtype=float, source=__NAME__,
                  description='fraction of total bad pixels')

# -----------------------------------------------------------------------------
# Define localisation variables
# -----------------------------------------------------------------------------
# root for localisation header keys
ROOT_DRS_LOC = Const('ROOT_DRS_LOC', value=None, dtype=str, source=__NAME__,
                     description='root for localisation header keys')
# Mean background (as percentage)
KW_LOC_BCKGRD = Keyword('KW_LOC_BCKGRD', key='', dtype=float, source=__NAME__,
                        description='Mean background (as percentage)')
# Number of orders located
KW_LOC_NBO = Keyword('KW_LOC_NBO', key='', dtype=int, source=__NAME__,
                     description='Number of orders located')
# fit degree for order centers
KW_LOC_DEG_C = Keyword('KW_LOC_DEG_C', key='', dtype=int, source=__NAME__,
                       description='fit degree for order centers')
# fit degree for order widths
KW_LOC_DEG_W = Keyword('KW_LOC_DEG_W', key='', dtype=int, source=__NAME__,
                       description='fit degree for order widths')
# Maximum flux in order
KW_LOC_MAXFLX = Keyword('KW_LOC_MAXFLX', key='', dtype=float, source=__NAME__,
                        description='Maximum flux in order')
# Maximum number of removed points allowed for location fit
KW_LOC_SMAXPTS_CTR = Keyword('KW_LOC_SMAXPTS_CTR', key='', dtype=int,
                             source=__NAME__,
                             description=('Maximum number of removed points '
                                          'allowed for location fit'))
# Maximum number of removed points allowed for width fit
KW_LOC_SMAXPTS_WID = Keyword('KW_LOC_SMAXPTS_WID', key='', dtype=int,
                             source=__NAME__,
                             description=('Maximum number of removed points '
                                          'allowed for width fit'))
# Maximum rms allowed for location fit
KW_LOC_RMS_CTR = Keyword('KW_LOC_RMS_CTR', key='', dtype=float, source=__NAME__,
                         description='Maximum rms allowed for location fit')
# Maximum rms allowed for width fit (formally KW_LOC_rms_fwhm)
KW_LOC_RMS_WID = Keyword('KW_LOC_RMS_WID', key='', dtype=float, source=__NAME__,
                         description=('Maximum rms allowed for width fit '
                                      '(formally KW_LOC_rms_fwhm)'))
# Coeff center order
KW_LOC_CTR_COEFF = Keyword('KW_LOC_CTR_COEFF', key='', dtype=int,
                           source=__NAME__,
                           description='Coeff center order')
# Coeff width order
KW_LOC_WID_COEFF = Keyword('KW_LOC_WID_COEFF', key='', dtype=int,
                           source=__NAME__, description='Coeff width order')

# -----------------------------------------------------------------------------
# Define shape variables
# -----------------------------------------------------------------------------
# Shape transform dx parameter
KW_SHAPE_DX = Keyword('KW_SHAPE_DX', key='', dtype=float, source=__NAME__,
                      description='Shape transform dx parameter')

# Shape transform dy parameter
KW_SHAPE_DY = Keyword('KW_SHAPE_DY', key='', dtype=float, source=__NAME__,
                      description='Shape transform dy parameter')

# Shape transform A parameter
KW_SHAPE_A = Keyword('KW_SHAPE_A', key='', dtype=float, source=__NAME__,
                     description='Shape transform A parameter')

# Shape transform B parameter
KW_SHAPE_B = Keyword('KW_SHAPE_B', key='', dtype=float, source=__NAME__,
                     description='Shape transform B parameter')

# Shape transform C parameter
KW_SHAPE_C = Keyword('KW_SHAPE_C', key='', dtype=float, source=__NAME__,
                     description='Shape transform C parameter')

# Shape transform D parameter
KW_SHAPE_D = Keyword('KW_SHAPE_D', key='', dtype=float, source=__NAME__,
                     description='Shape transform D parameter')

# -----------------------------------------------------------------------------
# Define extraction variables
# -----------------------------------------------------------------------------
# The extraction type (only added for E2DS files in extraction)
KW_EXT_TYPE = Keyword('KW_EXT_TYPE', key='', dtype=str, source=__NAME__,
                      description=('The extraction type (only added for E2DS '
                                   'files in extraction)'))

# SNR calculated in extraction process (per order)
KW_EXT_SNR = Keyword('KW_EXT_SNR', key='', dtype=float, source=__NAME__,
                     description=('SNR calculated in extraction process '
                                  '(per order)'))

# the start order for extraction
KW_EXT_START = Keyword('KW_EXT_START', key='', dtype=int, source=__NAME__,
                       description='the start order for extraction')

# the end order for extraction
KW_EXT_END = Keyword('KW_EXT_END', key='', dtype=int, source=__NAME__,
                     description='the end order for extraction')

# the upper bound for extraction of order
KW_EXT_RANGE1 = Keyword('KW_EXT_RANGE1', key='', dtype=int, source=__NAME__,
                        description='the upper bound for extraction of order')

# the lower bound for extraction of order
KW_EXT_RANGE2 = Keyword('KW_EXT_RANGE2', key='', dtype=int, source=__NAME__,
                        description='the lower bound for extraction of order')

# whether cosmics where rejected
KW_COSMIC = Keyword('KW_COSMIC', key='', dtype=int, source=__NAME__,
                    description='whether cosmics where rejected')

# the cosmic cut criteria
KW_COSMIC_CUT = Keyword('KW_COSMIC_CUT', key='', dtype=float, source=__NAME__,
                        description='the cosmic cut criteria')

# the cosmic threshold used
KW_COSMIC_THRES = Keyword('KW_COSMIC_THRES', key='', dtype=float,
                          source=__NAME__,
                          description='the cosmic threshold used')

# the blaze with used
KW_BLAZE_WID = Keyword('KW_BLAZE_WID', key='', dtype=float, source=__NAME__,
                       description='the blaze with used')

# the blaze cut used
KW_BLAZE_CUT = Keyword('KW_BLAZE_CUT', key='', dtype=float, source=__NAME__,
                       description='the blaze cut used')

# the blaze degree used (to fit)
KW_BLAZE_DEG = Keyword('KW_BLAZE_DEG', key='', dtype=int, source=__NAME__,
                       description='the blaze degree used (to fit)')

# The blaze sinc cut threshold used
KW_BLAZE_SCUT = Keyword('KW_BLAZE_SCUT', key='', dtype=float, source=__NAME__,
                        description='The blaze sinc cut threshold used')

# The blaze sinc sigma clip (rejection threshold) used
KW_BLAZE_SIGFIG = Keyword('KW_BLAZE_SIGFIG', key='', dtype=float,
                          source=__NAME__,
                          description=('The blaze sinc sigma clip (rejection '
                                       'threshold) used'))

# The blaze sinc bad percentile value used
KW_BLAZE_BPRCNTL = Keyword('KW_BLAZE_BPRCNTL', key='', dtype=float,
                           source=__NAME__,
                           description=('The blaze sinc bad percentile '
                                        'value used'))

# The number of iterations used in the blaze sinc fit
KW_BLAZE_NITER = Keyword('KW_BLAZE_NITER', key='', dtype=int, source=__NAME__,
                         description=('The number of iterations used in the '
                                      'blaze sinc fit'))

# the saturation QC limit
KW_SAT_QC = Keyword('KW_SAT_QC', key='', dtype=int, source=__NAME__,
                    description='the saturation QC limit')

# the max saturation level
KW_SAT_LEVEL = Keyword('KW_SAT_LEVEL', key='', dtype=int, source=__NAME__,
                       description='the max saturation level')

# the wave starting point used for s1d
KW_S1D_WAVESTART = Keyword('KW_S1D_WAVESTART', key='', dtype=float,
                           source=__NAME__,
                           description=('the wave starting point used for '
                                        's1d'))

# the wave end point used for s1d
KW_S1D_WAVEEND = Keyword('KW_S1D_WAVEEND', key='', dtype=float, source=__NAME__,
                         description='the wave end point used for s1d')

# the wave grid kind used for s1d (wave or velocity)
KW_S1D_KIND = Keyword('KW_S1D_KIND', key='', dtype=str, source=__NAME__,
                      description=('the wave grid kind used for s1d (wave '
                                   'or velocity)'))

# the bin size for wave grid kind=wave
KW_S1D_BWAVE = Keyword('KW_S1D_BWAVE', key='', dtype=float, source=__NAME__,
                       description='the bin size for wave grid kind=wave')

# the bin size for wave grid kind=velocity
KW_S1D_BVELO = Keyword('KW_S1D_BVELO', key='', dtype=float, source=__NAME__,
                       description='the bin size for wave grid kind=velocity')

# the smooth size for the s1d
KW_S1D_SMOOTH = Keyword('KW_S1D_SMOOTH', key='', dtype=float, source=__NAME__,
                        description='the smooth size for the s1d')

# the blaze threshold used for the s1d
KW_S1D_BLAZET = Keyword('KW_S1D_BLAZET', key='', dtype=float, source=__NAME__,
                        description='the blaze threshold used for the s1d')

# the Right Ascension used to calculate the BERV
KW_BERVRA = Keyword('KW_BERVRA', key='', dtype=float, source=__NAME__,
                    description=('the Right Ascension used to calculate '
                                 'the BERV'))

# the Declination used to calculate the BERV
KW_BERVDEC = Keyword('KW_BERVDEC', key='', dtype=float, source=__NAME__,
                     description='the Declination used to calculate the BERV')

# the Gaia ID used to identify KW_BERV_POS_SOURCE for BERV calculation
KW_BERVGAIA_ID = Keyword('KW_BERVGAIA_ID', key='', dtype=str, source=__NAME__,
                         description=('the Gaia ID used to identify '
                                      'KW_BERV_POS_SOURCE for BERV calculation'))

# the OBJNAME used to identify KW_BERV_POS_SOURCE for BERV calculation
KW_BERVOBJNAME = Keyword('KW_BERVOBJNAME', key='', dtype=str, source=__NAME__,
                         description=('the OBJNAME used to identify '
                                      'KW_BERV_POS_SOURCE for BERV calculation'))

# the epoch (jd) used to calculate the BERV
KW_BERVEPOCH = Keyword('KW_BERVEPOCH', key='', dtype=float, source=__NAME__,
                       description=('the epoch (jd) used to calculate '
                                    'the BERV'))

# the pmra [mas/yr] used to calculate the BERV
KW_BERVPMRA = Keyword('KW_BERVPMRA', key='', dtype=float, source=__NAME__,
                      description=('the pmra [mas/yr] used to calculate '
                                   'the BERV'))

# the pmde [mas/yr] used to calculate the BERV
KW_BERVPMDE = Keyword('KW_BERVPMDE', key='', dtype=float, source=__NAME__,
                      description=('the pmde [mas/yr] used to calculate '
                                   'the BERV'))

# the parallax [mas] used to calculate the BERV
KW_BERVPLX = Keyword('KW_BERVPLX', key='', dtype=float, source=__NAME__,
                     description=('the parallax [mas] used to calculate '
                                  'the BERV'))

# the rv [km/s] used to calculate the BERV
KW_BERVRV = Keyword('KW_BERVRV', key='', dtype=float, source=__NAME__,
                    description='the rv [km/s] used to calculate the BERV')

# the source of the BERV star parameters (header or gaia)
KW_BERV_POS_SOURCE = Keyword('KW_BERV_POS_SOURCE', key='', dtype=str,
                             source=__NAME__,
                             description=('the source of the BERV star '
                                          'parameters (header or gaia)'))

# the Gaia G mag (if present) for the gaia query
KW_BERV_GAIA_GMAG = Keyword('KW_BERV_GAIA_GMAG', key='', dtype=float,
                            source=__NAME__,
                            description=('the Gaia G mag (if present) for '
                                         'the gaia query'))

# the Gaia BP mag (if present) for the gaia query
KW_BERV_GAIA_BPMAG = Keyword('KW_BERV_GAIA_BPMAG', key='', dtype=float,
                             source=__NAME__,
                             description=('the Gaia BP mag (if present) for '
                                          'the gaia query'))

# the Gaia RP mag (if present) for the gaia query
KW_BERV_GAIA_RPMAG = Keyword('KW_BERV_GAIA_RPMAG', key='', dtype=float,
                             source=__NAME__,
                             description=('the Gaia RP mag (if present) for '
                                          'the gaia query'))

# the Gaia G mag limit used for the gaia query
KW_BERV_GAIA_MAGLIM = Keyword('KW_BERV_GAIA_MAGLIM', key='', dtype=float,
                              source=__NAME__,
                              description=('the Gaia G mag limit used for '
                                           'the gaia query'))

# the Gaia parallax limit used the gaia query
KW_BERV_GAIA_PLXLIM = Keyword('KW_BERV_GAIA_PLXLIM', key='', dtype=float,
                              source=__NAME__,
                              description=('the Gaia parallax limit used the '
                                           'gaia query'))

# the observatory latitude used to calculate the BERV
KW_BERVLAT = Keyword('KW_BERVLAT', key='', dtype=float, source=__NAME__,
                     description=('the observatory latitude used to calculate '
                                  'the BERV'))

# the observatory longitude used to calculate the BERV
KW_BERVLONG = Keyword('KW_BERVLONG', key='', dtype=float, source=__NAME__,
                      description=('the observatory longitude used to '
                                   'calculate the BERV'))

# the observatory altitude used to calculate the BERV
KW_BERVALT = Keyword('KW_BERVALT', key='', dtype=float, source=__NAME__,
                     description=('the observatory altitude used to calculate '
                                  'the BERV'))

# the BERV calculated with KW_BERVSOURCE
KW_BERV = Keyword('KW_BERV', key='', dtype=float, source=__NAME__,
                  description='the BERV calculated with KW_BERVSOURCE')

# the Barycenter Julian date calculate with KW_BERVSOURCE
KW_BJD = Keyword('KW_BJD', key='', dtype=float, source=__NAME__,
                 description=('the Barycenter Julian date calculate with '
                              'KW_BERVSOURCE'))

# the maximum BERV found across 1 year (with KW_BERVSOURCE)
KW_BERVMAX = Keyword('KW_BERVMAX', key='', dtype=float, source=__NAME__,
                     description=('the maximum BERV found across 1 year (with '
                                  'KW_BERVSOURCE)'))

# the derivative of the BERV (BERV at time + 1s - BERV)
KW_DBERV = Keyword('KW_DBERV', key='', dtype=float, source=__NAME__,
                   description=('the derivative of the BERV (BERV at time + '
                                '1s - BERV)'))

# the source of the calculated BERV parameters
KW_BERVSOURCE = Keyword('KW_BERVSOURCE', key='', dtype=str, source=__NAME__,
                        description=('the source of the calculated BERV '
                                     'parameters'))

# the BERV calculated with the estimate
KW_BERV_EST = Keyword('KW_BERV_EST', key='', dtype=float, source=__NAME__,
                      description='the BERV calculated with the estimate')

# the Barycenter Julian date calculated with the estimate
KW_BJD_EST = Keyword('KW_BJD_EST', key='', dtype=float, source=__NAME__,
                     description=('the Barycenter Julian date calculated with '
                                  'the estimate'))

# the maximum BERV found across 1 year (calculated with estimate)
KW_BERVMAX_EST = Keyword('KW_BERVMAX_EST', key='', dtype=float, source=__NAME__,
                         description=('the maximum BERV found across 1 year '
                                      '(calculated with estimate)'))

# the derivative of the BERV (BERV at time + 1s - BERV) calculated with
#     estimate
KW_DBERV_EST = Keyword('KW_DBERV_EST', key='', dtype=float, source=__NAME__,
                       description=('the derivative of the BERV (BERV at time'
                                    ' + 1s - BERV) calculated with estimate'))

# the actual jd time used to calculate the BERV
KW_BERV_OBSTIME = Keyword('KW_BERV_OBSTIME', key='', dtype=float,
                          source=__NAME__,
                          description=('the actual jd time used to calculate '
                                       'the BERV'))

# the method used to obtain the berv obs time
KW_BERV_OBSTIME_METHOD = Keyword('KW_BERV_OBSTIME_METHOD', key='', dtype=str,
                                 source=__NAME__,
                                 description=('the method used to obtain the '
                                              'berv obs time'))

# -----------------------------------------------------------------------------
# Define leakage variables
# -----------------------------------------------------------------------------
# Define whether leak correction has been done
KW_LEAK_CORR = Keyword('KW_LEAK_CORR', key='', dtype=int, source=__NAME__,
                       description=('Define whether leak correction has been '
                                    'done'))

# Define the background percentile used for correcting leakage
KW_LEAK_BP_U = Keyword('KW_LEAK_BP_U', key='', dtype=float, source=__NAME__,
                       description=('Define the background percentile used for '
                                    'correcting leakage'))

# Define the normalisation percentile used for correcting leakage
KW_LEAK_NP_U = Keyword('KW_LEAK_NP_U', key='', dtype=float, source=__NAME__,
                       description=('Define the normalisation percentile used '
                                    'for correcting leakage'))

# Define the e-width smoothing used for correcting leakage master
KW_LEAK_WSMOOTH = Keyword('KW_LEAK_WSMOOTH', key='', dtype=float,
                          source=__NAME__,
                          description=('Define the e-width smoothing used for '
                                       'correcting leakage master'))

# Define the kernel size used for correcting leakage master
KW_LEAK_KERSIZE = Keyword('KW_LEAK_KERSIZE', key='', dtype=float,
                          source=__NAME__,
                          description=('Define the kernel size used for '
                                       'correcting leakage master'))

# Define the lower bound percentile used for correcting leakage
KW_LEAK_LP_U = Keyword('KW_LEAK_LP_U', key='', dtype=float, source=__NAME__,
                       description=('Define the lower bound percentile used '
                                    'for correcting leakage'))

# Define the upper bound percentile used for correcting leakage
KW_LEAK_UP_U = Keyword('KW_LEAK_UP_U', key='', dtype=float, source=__NAME__,
                       description=('Define the upper bound percentile used '
                                    'for correcting leakage'))

# Define the bad ratio offset limit used for correcting leakage
KW_LEAK_BADR_U = Keyword('KW_LEAK_BADR_U', key='', dtype=float, source=__NAME__,
                         description=('Define the bad ratio offset limit used '
                                      'for correcting leakage'))

# -----------------------------------------------------------------------------
# Define wave variables
# -----------------------------------------------------------------------------
# Number of orders in wave image
KW_WAVE_NBO = Keyword('KW_WAVE_NBO', key='', dtype=int, source=__NAME__,
                      description='Number of orders in wave image')

# fit degree for wave solution
KW_WAVE_DEG = Keyword('KW_WAVE_DEG', key='', dtype=int, source=__NAME__,
                      description='fit degree for wave solution')

# the wave file used
KW_WAVEFILE = Keyword('KW_WAVEFILE', key='', dtype=str, source=__NAME__,
                      description='the wave file used')

# the wave file mid exptime [mjd]
KW_WAVETIME = Keyword('KW_WAVETIME', key='', dtype=float, source=__NAME__,
                      description='the wave file mid exptime [mjd]')

# the wave source of the wave file used
KW_WAVESOURCE = Keyword('KW_WAVESOURCE', key='', dtype=str, source=__NAME__,
                        description='the wave source of the wave file used')

# the wave coefficients
KW_WAVECOEFFS = Keyword('KW_WAVECOEFFS', key='', dtype=float, source=__NAME__,
                        description='the wave coefficients')

# the initial wave file used for wave solution
KW_INIT_WAVE = Keyword('KW_INIT_WAVE', key='', dtype=str, source=__NAME__,
                       description=('the initial wave file used for wave '
                                    'solution'))

# -----------------------------------------------------------------------------
# the fit degree for wave solution used
KW_WAVE_FITDEG = Keyword('KW_WAVE_FITDEG', key='', dtype=int, source=__NAME__,
                         description='the fit degree for wave solution used')

# the mode used to calculate the hc wave solution
KW_WAVE_MODE_HC = Keyword('KW_WAVE_MODE_HC', key='', dtype=str, source=__NAME__,
                          description=('the mode used to calculate the hc '
                                       'wave solution'))

# the mode used to calculate the fp wave solution
KW_WAVE_MODE_FP = Keyword('KW_WAVE_MODE_FP', key='', dtype=str, source=__NAME__,
                          description=('the mode used to calculate the fp '
                                       'wave solution'))

# the echelle number of the first order used
KW_WAVE_ECHELLE_START = Keyword('KW_WAVE_ECHELLE_START', key='', dtype=int,
                                source=__NAME__,
                                description=('the echelle number of the first '
                                             'order used'))

# the width of the box for fitting hc lines used
KW_WAVE_HCG_WSIZE = Keyword('KW_WAVE_HCG_WSIZE', key='', dtype=int,
                            source=__NAME__,
                            description=('the width of the box for fitting hc '
                                         'lines used'))

# the sigma above local rms for fitting hc lines used
KW_WAVE_HCG_SIGPEAK = Keyword('KW_WAVE_HCG_SIGPEAK', key='', dtype=float,
                              source=__NAME__,
                              description=('the sigma above local rms for '
                                           'fitting hc lines used'))

# the fit degree for the gaussian peak fitting used
KW_WAVE_HCG_GFITMODE = Keyword('KW_WAVE_HCG_GFITMODE', key='', dtype=int,
                               source=__NAME__,
                               description=('the fit degree for the gaussian '
                                            'peak fitting used'))

# the min rms for gaussian peak fitting used
KW_WAVE_HCG_FB_RMSMIN = Keyword('KW_WAVE_HCG_FB_RMSMIN', key='', dtype=float,
                                source=__NAME__,
                                description=('the min rms for gaussian peak '
                                             'fitting used'))

# the max rms for gaussian peak fitting used
KW_WAVE_HCG_FB_RMSMAX = Keyword('KW_WAVE_HCG_FB_RMSMAX', key='', dtype=float,
                                source=__NAME__,
                                description=('the max rms for gaussian peak '
                                             'fitting used'))

# the min e-width of the line for gaussian peak fitting used
KW_WAVE_HCG_EWMIN = Keyword('KW_WAVE_HCG_EWMIN', key='', dtype=float,
                            source=__NAME__,
                            description=('the min e-width of the line for '
                                         'gaussian peak fitting used'))

# the min e-width of the line for gaussian peak fitting used
KW_WAVE_HCG_EWMAX = Keyword('KW_WAVE_HCG_EWMAX', key='', dtype=float,
                            source=__NAME__,
                            description=('the min e-width of the line for '
                                         'gaussian peak fitting used'))

# the filename for the HC line list generated
KW_WAVE_HCLL_FILE = Keyword('KW_WAVE_HCLL_FILE', key='', dtype=str,
                            source=__NAME__,
                            description=('the filename for the HC line list '
                                         'generated'))

# the number of bright lines to used in triplet fit
KW_WAVE_TRP_NBRIGHT = Keyword('KW_WAVE_TRP_NBRIGHT', key='', dtype=int,
                              source=__NAME__,
                              description=('the number of bright lines to used '
                                           'in triplet fit'))

# the number of iterations done in triplet fit
KW_WAVE_TRP_NITER = Keyword('KW_WAVE_TRP_NITER', key='', dtype=float,
                            source=__NAME__,
                            description=('the number of iterations done in '
                                         'triplet fit'))

# the max distance between catalog line and initial guess line in triplet fit
KW_WAVE_TRP_CATGDIST = Keyword('KW_WAVE_TRP_CATGDIST', key='', dtype=float,
                               source=__NAME__,
                               description=(
                                   'the max distance between catalog line and '
                                   'initial guess line in triplet fit'))

# the fit degree for triplet fit
KW_WAVE_TRP_FITDEG = Keyword('KW_WAVE_TRP_FITDEG', key='', dtype=int,
                             source=__NAME__,
                             description='the fit degree for triplet fit')

# the minimum number of lines required per order in triplet fit
KW_WAVE_TRP_MIN_NLINES = Keyword('KW_WAVE_TRP_MIN_NLINES', key='', dtype=int,
                                 source=__NAME__,
                                 description=('the minimum number of lines '
                                              'required per order in triplet fit'))

# the total number of lines required in triplet fit
KW_WAVE_TRP_TOT_NLINES = Keyword('KW_WAVE_TRP_TOT_NLINES', key='', dtype=int,
                                 source=__NAME__,
                                 description=('the total number of lines '
                                              'required in triplet fit'))

# the degree(s) of fit to ensure continuity in triplet fit
KW_WAVE_TRP_ORDER_FITCONT = Keyword('KW_WAVE_TRP_ORDER_FITCONT', key='',
                                    dtype=float, source=__NAME__,
                                    description=('the degree(s) of fit to '
                                                 'ensure continuity in '
                                                 'triplet fit'))

# the iteration number for sigma clip in triplet fit
KW_WAVE_TRP_SCLIPNUM = Keyword('KW_WAVE_TRP_SCLIPNUM', key='', dtype=float,
                               source=__NAME__,
                               description=('the iteration number for sigma '
                                            'clip in triplet fit'))

# the sigma clip threshold in triplet fit
KW_WAVE_TRP_SCLIPTHRES = Keyword('KW_WAVE_TRP_SCLIPTHRES', key='', dtype=float,
                                 source=__NAME__,
                                 description=('the sigma clip threshold in '
                                              'triplet fit'))

# the distance away in dv to reject order triplet in triplet fit
KW_WAVE_TRP_DVCUTORD = Keyword('KW_WAVE_TRP_DVCUTORD', key='', dtype=float,
                               source=__NAME__,
                               description=('the distance away in dv to reject '
                                            'order triplet in triplet fit'))

# the distance away in dv to reject all triplet in triplet fit
KW_WAVE_TRP_DVCUTALL = Keyword('KW_WAVE_TRP_DVCUTALL', key='', dtype=float,
                               source=__NAME__,
                               description=('the distance away in dv to reject '
                                            'all triplet in triplet fit'))

# the wave resolution map dimensions
KW_WAVE_RES_MAPSIZE = Keyword('KW_WAVE_RES_MAPSIZE', key='', dtype=int,
                              source=__NAME__,
                              description=('the wave resolution map '
                                           'dimensions'))

# the width of the box for wave resolution map
KW_WAVE_RES_WSIZE = Keyword('KW_WAVE_RES_WSIZE', key='', dtype=float,
                            source=__NAME__,
                            description=('the width of the box for wave '
                                         'resolution map'))

# the max deviation in rms allowed in wave resolution map
KW_WAVE_RES_MAXDEVTHRES = Keyword('KW_WAVE_RES_MAXDEVTHRES', key='',
                                  dtype=float, source=__NAME__,
                                  description=('the max deviation in rms '
                                               'allowed in wave resolution map'))

# the littrow start order used for HC
KW_WAVE_LIT_START_1 = Keyword('KW_WAVE_LIT_START_1', key='', dtype=int,
                              source=__NAME__,
                              description=('the littrow start order used '
                                           'for HC'))

# the littrow end order used for HC
KW_WAVE_LIT_END_1 = Keyword('KW_WAVE_LIT_END_1', key='', dtype=float,
                            source=__NAME__,
                            description='the littrow end order used for HC')

# the orders removed from the littrow test
KW_WAVE_LIT_RORDERS = Keyword('KW_WAVE_LIT_RORDERS', key='', dtype=float,
                              source=__NAME__,
                              description=('the orders removed from the '
                                           'littrow test'))

# the littrow order initial value used for HC
KW_WAVE_LIT_ORDER_INIT_1 = Keyword('KW_WAVE_LIT_ORDER_INIT_1', key='',
                                   dtype=int, source=__NAME__,
                                   description=('the littrow order initial '
                                                'value used for HC'))

# the littrow order start value used for HC
KW_WAVE_LIT_ORDER_START_1 = Keyword('KW_WAVE_LIT_ORDER_START_1', key='',
                                    dtype=int, source=__NAME__,
                                    description=('the littrow order start '
                                                 'value used for HC'))

# the littrow order end value used for HC
KW_WAVE_LIT_ORDER_END_1 = Keyword('KW_WAVE_LIT_ORDER_END_1', key='',
                                  dtype=int, source=__NAME__,
                                  description=('the littrow order end value '
                                               'used for HC'))

# the littrow x cut step value used for HC
KW_WAVE_LITT_XCUTSTEP_1 = Keyword('KW_WAVE_LITT_XCUTSTEP_1', key='',
                                  dtype=int, source=__NAME__,
                                  description=('the littrow x cut step value '
                                               'used for HC'))

# the littrow fit degree value used for HC
KW_WAVE_LITT_FITDEG_1 = Keyword('KW_WAVE_LITT_FITDEG_1', key='', dtype=int,
                                source=__NAME__,
                                description=('the littrow fit degree value '
                                             'used for HC'))

# the littrow extrapolation fit degree value used for HC
KW_WAVE_LITT_EXT_FITDEG_1 = Keyword('KW_WAVE_LITT_EXT_FITDEG_1', key='',
                                    dtype=int, source=__NAME__,
                                    description=('the littrow extrapolation '
                                                 'fit degree value used for HC'))

# the littrow extrapolation start order value used for HC
KW_WAVE_LITT_EXT_ORD_START_1 = Keyword('KW_WAVE_LITT_EXT_ORD_START_1', key='',
                                       dtype=int, source=__NAME__,
                                       description=('the littrow extrapolation '
                                                    'start order value used '
                                                    'for HC'))

# the first order used for FP wave sol improvement
KW_WFP_ORD_START = Keyword('KW_WFP_ORD_START', key='', dtype=int,
                           source=__NAME__,
                           description=('the first order used for FP wave sol '
                                        'improvement'))

# the last order used for FP wave sol improvement
KW_WFP_ORD_FINAL = Keyword('KW_WFP_ORD_FINAL', key='', dtype=int,
                           source=__NAME__,
                           description=('the last order used for FP wave sol '
                                        'improvement'))

# the blaze threshold used for FP wave sol improvement
KW_WFP_BLZ_THRES = Keyword('KW_WFP_BLZ_THRES', key='', dtype=float,
                           source=__NAME__,
                           description=('the blaze threshold used for FP wave '
                                        'sol improvement'))

# the minimum fp peak pixel sep used for FP wave sol improvement
KW_WFP_XDIFF_MIN = Keyword('KW_WFP_XDIFF_MIN', key='', dtype=float,
                           source=__NAME__,
                           description=('the minimum fp peak pixel sep used '
                                        'for FP wave sol improvement'))

# the maximum fp peak pixel sep used for FP wave sol improvement
KW_WFP_XDIFF_MAX = Keyword('KW_WFP_XDIFF_MAX', key='', dtype=float,
                           source=__NAME__,
                           description=('the maximum fp peak pixel sep used '
                                        'for FP wave sol improvement'))

# the initial value of the FP effective cavity width used
KW_WFP_DOPD0 = Keyword('KW_WFP_DOPD0', key='', dtype=float, source=__NAME__,
                       description=('the initial value of the FP effective '
                                    'cavity width used'))

# the  maximum fraction wavelength offset btwn xmatch fp peaks used
KW_WFP_LL_OFFSET = Keyword('KW_WFP_LL_OFFSET', key='', dtype=float,
                           source=__NAME__,
                           description=('the maximum fraction wavelength '
                                        'offset btwn xmatch fp peaks used'))

# the max dv to keep hc lines used
KW_WFP_DVMAX = Keyword('KW_WFP_DVMAX', key='', dtype=float, source=__NAME__,
                       description='the max dv to keep hc lines used')

# the used polynomial fit degree (to fit wave solution)
KW_WFP_LLFITDEG = Keyword('KW_WFP_LLFITDEG', key='', dtype=int,
                          source=__NAME__,
                          description=('the used polynomial fit degree (to '
                                       'fit wave solution)'))

# whether the cavity file was updated
KW_WFP_UPDATECAV = Keyword('KW_WFP_UPDATECAV', key='', dtype=int,
                           source=__NAME__,
                           description='whether the cavity file was updated')

# the mode used to fit the FP cavity
KW_WFP_FPCAV_MODE = Keyword('KW_WFP_FPCAV_MODE', key='', dtype=int,
                            source=__NAME__,
                            description='the mode used to fit the FP cavity')

# the mode used to fit the wavelength
KW_WFP_LLFIT_MODE = Keyword('KW_WFP_LLFIT_MODE', key='', dtype=int,
                            source=__NAME__,
                            description='the mode used to fit the wavelength')

# the minimum instrumental error used
KW_WFP_ERRX_MIN = Keyword('KW_WFP_ERRX_MIN', key='', dtype=float,
                          source=__NAME__,
                          description='the minimum instrumental error used')

# the max rms for the wave sol sig clip
KW_WFP_MAXLL_FIT_RMS = Keyword('KW_WFP_MAXLL_FIT_RMS', key='', dtype=float,
                               source=__NAME__,
                               description=('the max rms for the wave sol '
                                            'sig clip'))

# the echelle number used for the first order
KW_WFP_T_ORD_START = Keyword('KW_WFP_T_ORD_START', key='', dtype=int,
                             source=__NAME__,
                             description=('the echelle number used for the '
                                          'first order'))

# the weight below which fp lines are rejected
KW_WFP_WEI_THRES = Keyword('KW_WFP_WEI_THRES', key='', dtype=float,
                           source=__NAME__,
                           description=('the weight below which fp lines are '
                                        'rejected'))

# the polynomial degree fit order used for fitting the fp cavity
KW_WFP_CAVFIT_DEG = Keyword('KW_WFP_CAVFIT_DEG', key='', dtype=int,
                            source=__NAME__,
                            description=('the polynomial degree fit order '
                                         'used for fitting the fp cavity'))

# the largest jump in fp that was allowed
KW_WFP_LARGE_JUMP = Keyword('KW_WFP_LARGE_JUMP', key='', dtype=float,
                            source=__NAME__,
                            description=('the largest jump in fp that was '
                                         'allowed'))

# the index to start crossmatching fps at
KW_WFP_CM_INDX = Keyword('KW_WFP_CM_INDX', key='', dtype=float, source=__NAME__,
                         description=('the index to start crossmatching '
                                      'fps at'))

# the FP widths used for each order (1D list)
KW_WFP_WIDUSED = Keyword('KW_WFP_WIDUSED', key='', dtype=float, source=__NAME__,
                         description=('the FP widths used for each order '
                                      '(1D list)'))

# the percentile to normalise the FP flux per order used
KW_WFP_NPERCENT = Keyword('KW_WFP_NPERCENT', key='', dtype=float,
                          source=__NAME__,
                          description=('the percentile to normalise the FP '
                                       'flux per order used'))

# the normalised limited used to detect FP peaks
KW_WFP_LIMIT = Keyword('KW_WFP_LIMIT', key='', dtype=float, source=__NAME__,
                       description=('the normalised limited used to detect '
                                    'FP peaks'))

# the normalised cut width for large peaks used
KW_WFP_CUTWIDTH = Keyword('KW_WFP_CUTWIDTH', key='', dtype=float,
                          source=__NAME__,
                          description=('the normalised cut width for large '
                                       'peaks used'))

# Wavelength solution for fiber C that is source of the WFP keys
KW_WFP_FILE = Keyword('KW_WFP_FILE', key='', dtype=str, source=__NAME__,
                      description=('Wavelength solution for fiber C that is '
                                   'source of the WFP keys'))

# drift of the FP file used for the wavelength solution
KW_WFP_DRIFT = Keyword('KW_WFP_DRIFT', key='', dtype=float, source=__NAME__,
                       description=('drift of the FP file used for the '
                                    'wavelength solution'))

# FWHM of the wave FP file CCF
KW_WFP_FWHM = Keyword('KW_WFP_FWHM', key='', dtype=float, source=__NAME__,
                      description='FWHM of the wave FP file CCF')

# Contrast of the wave FP file CCF
KW_WFP_CONTRAST = Keyword('KW_WFP_CONTRAST', key='', dtype=float,
                          source=__NAME__,
                          description='Contrast of the wave FP file CCF')

# Mask for the wave FP file CCF
KW_WFP_MASK = Keyword('KW_WFP_MASK', key='', dtype=float, source=__NAME__,
                      description='Mask for the wave FP file CCF')

# Number of lines for the wave FP file CCF
KW_WFP_LINES = Keyword('KW_WFP_LINES', key='', dtype=float, source=__NAME__,
                       description='Number of lines for the wave FP file CCF')

# Target RV for the wave FP file CCF
KW_WFP_TARG_RV = Keyword('KW_WFP_TARG_RV', key='', dtype=float, source=__NAME__,
                         description='Target RV for the wave FP file CCF')

# Width for the wave FP file CCF
KW_WFP_WIDTH = Keyword('KW_WFP_WIDTH', key='', dtype=float, source=__NAME__,
                       description='Width for the wave FP file CCF')

# Step for the wave FP file CCF
KW_WFP_STEP = Keyword('KW_WFP_STEP', key='', dtype=float, source=__NAME__,
                      description='Step for the wave FP file CCF')

# The sigdet used for FP file CCF
KW_WFP_SIGDET = Keyword('KW_WFP_SIGDET', key='', dtype=float, source=__NAME__,
                        description='The sigdet used for FP file CCF')

# The boxsize used for FP file CCF
KW_WFP_BOXSIZE = Keyword('KW_WFP_BOXSIZE', key='', dtype=int, source=__NAME__,
                         description='The boxsize used for FP file CCF')

# The max flux used for the FP file CCF
KW_WFP_MAXFLUX = Keyword('KW_WFP_MAXFLUX', key='', dtype=float, source=__NAME__,
                         description='The max flux used for the FP file CCF')

# The det noise used for the FP file CCF
KW_WFP_DETNOISE = Keyword('KW_WFP_DETNOISE', key='', dtype=float,
                          source=__NAME__,
                          description=('The det noise used for the '
                                       'FP file CCF'))

# the highest order used for the FP file CCF
KW_WFP_NMAX = Keyword('KW_WFP_NMAX', key='', dtype=int, source=__NAME__,
                      description=('the highest order used for the '
                                   'FP file CCF'))

# The weight of the CCF mask (if 1 force all weights equal) used for FP CCF
KW_WFP_MASKMIN = Keyword('KW_WFP_MASKMIN', key='', dtype=float, source=__NAME__,
                         description=('The weight of the CCF mask (if 1 '
                                      'force all weights equal) used for '
                                      'FP CCF'))

# The width of the CCF mask template line (if 0 use natural) used for FP CCF
KW_WFP_MASKWID = Keyword('KW_WFP_MASKWID', key='', dtype=float, source=__NAME__,
                         description=('The width of the CCF mask template '
                                      'line (if 0 use natural) used for FP CCF'))

# The units of the input CCF mask (converted to nm in code)
KW_WFP_MASKUNITS = Keyword('KW_WFP_MASKUNITS', key='', dtype=str,
                           source=__NAME__,
                           description=('The units of the input CCF mask '
                                        '(converted to nm in code)'))

# number of iterations for convergence used in wave night (hc)
KW_WNT_NITER1 = Keyword('KW_WNT_NITER1', key='', dtype=int, source=__NAME__,
                        description=('number of iterations for convergence '
                                     'used in wave night (hc)'))

# number of iterations for convergence used in wave night (fp)
KW_WNT_NITER2 = Keyword('KW_WNT_NITER2', key='', dtype=int, source=__NAME__,
                        description=('number of iterations for convergence '
                                     'used in wave night (fp)'))

# starting point for the cavity corrections used in wave night
KW_WNT_DCAVITY = Keyword('KW_WNT_DCAVITY', key='', dtype=int, source=__NAME__,
                         description=('starting point for the cavity '
                                      'corrections used in wave night'))

# source fiber for the cavity correction
KW_WNT_DCAVSRCE = Keyword('KW_WNT_DCAVSRCE', key='', dtype=str, source=__NAME__,
                          description=('source fiber for the cavity '
                                       'correction'))

# define the sigma clip value to remove bad hc lines used
KW_WNT_HCSIGCLIP = Keyword('KW_WNT_HCSIGCLIP', key='', dtype=float,
                           source=__NAME__,
                           description=('define the sigma clip value to remove '
                                        'bad hc lines used'))

# median absolute deviation cut off used
KW_WNT_MADLIMIT = Keyword('KW_WNT_MADLIMIT', key='', dtype=float,
                          source=__NAME__,
                          description=('median absolute deviation cut off '
                                       'used'))

# sigma clipping for the fit used in wave night
KW_WNT_NSIG_FIT = Keyword('KW_WNT_NSIG_FIT', key='', dtype=int, source=__NAME__,
                          description=('sigma clipping for the fit used '
                                       'in wave night'))

# -----------------------------------------------------------------------------
# Define wave ref (new) variables
# -----------------------------------------------------------------------------
# number of orders for the resolution map header
KW_RESMAP_NBO = Keyword('KW_RESMAP_NBO', key='', dtype=int, source=__NAME__,
                          description='number of orders for the resolution '
                                      'map header')

# number of pixels in an order for the resolution map header
KW_RESMAP_NBPIX = Keyword('KW_RESMAP_NBO', key='', dtype=int, source=__NAME__,
                          description='number of pixels in an order for the '
                                      'resolution map header')

# current bin number for order direction for the resolution map header
KW_RESMAP_BINORD = Keyword('KW_RESMAP_NBO', key='', dtype=int, source=__NAME__,
                           description='current bin number for order direction '
                                       'for the resolution map header')

# total number of bins in order direction for the resolution map header
KW_RESMAP_NBINORD = Keyword('KW_RESMAP_NBINORD', key='', dtype=int,
                            source=__NAME__,
                            description='total number of bins in order '
                                        'direction for the resolution map '
                                        'header')

# current bin number in spatial direction for the resolution map header
KW_RESMAP_BINPIX = Keyword('KW_RESMAP_BINPIX', key='', dtype=int,
                           source=__NAME__,
                           description='current bin number in spatial direction'
                                       ' for the resolution map header')

# total number of bins in spatial direction for the resolution map header
KW_RESMAP_NBINPIX = Keyword('KW_RESMAP_NBINPIX', key='', dtype=int,
                           source=__NAME__,
                           description='total number of bins in spatial '
                                       'direction for the resolution map '
                                       'header')

# First order used in this sector
KW_RES_MAP_ORDLOW = Keyword('KW_RES_MAP_ORDLOW', key='', dtype=int,
                           source=__NAME__,
                           description='First order used in this sector')

# Last order used in this sector
KW_RES_MAP_ORDHIGH = Keyword('KW_RES_MAP_ORDHIGH', key='', dtype=int,
                           source=__NAME__,
                           description='Last order used in this sector')

# First pixel used in this sector
KW_RES_MAP_PIXLOW = Keyword('KW_RES_MAP_PIXLOW', key='', dtype=int,
                            source=__NAME__,
                            description='First pixel used in this sector')

# Last pixel used in this sector
KW_RES_MAP_PIXHIGH = Keyword('KW_RES_MAP_PIXHIGH', key='', dtype=int,
                             source=__NAME__,
                             description='Last pixel used in this sector')

# FWHM from fit for this sector
KW_RES_MAP_FWHM = Keyword('KW_RES_MAP_FWHM', key='', dtype=int,
                          source=__NAME__,
                          description='FWHM from fit for this sector')

# Amplitude from fit for this sector
KW_RES_MAP_AMP = Keyword('KW_RES_MAP_AMP', key='', dtype=int,
                         source=__NAME__,
                         description='FWHM from fit for this sector')

# Exponent from fit for this sector
KW_RES_MAP_EXPO = Keyword('KW_RES_MAP_EXPO', key='', dtype=int,
                          source=__NAME__,
                          description='Exponent from fit for this sector')

# Measured effective resolution measured for this sector
KW_RES_MAP_RESEFF = Keyword('KW_RES_MAP_RESEFF', key='', dtype=int,
                            source=__NAME__,
                            description='Measured effective resolution measured'
                                        ' for this sector')

# -----------------------------------------------------------------------------
# Define telluric preclean variables
# -----------------------------------------------------------------------------
# Define the exponent of water key from telluric preclean process
KW_TELLUP_EXPO_WATER = Keyword('KW_TELLUP_EXPO_WATER', key='', dtype=float,
                               source=__NAME__,
                               description=('Define the exponent of water key '
                                            'from telluric preclean process'))

# Define the exponent of other species from telluric preclean process
KW_TELLUP_EXPO_OTHERS = Keyword('KW_TELLUP_EXPO_OTHERS', key='', dtype=float,
                                source=__NAME__,
                                description=('Define the exponent of other '
                                             'species from telluric preclean process'))

# Define the velocity of water absorbers calculated in telluric preclean process
KW_TELLUP_DV_WATER = Keyword('KW_TELLUP_DV_WATER', key='', dtype=float,
                             source=__NAME__,
                             description=(
                                 'Define the velocity of water absorbers '
                                 'calculated in telluric preclean process'))

# Define the velocity of other species absorbers calculated in telluric
#     preclean process
KW_TELLUP_DV_OTHERS = Keyword('KW_TELLUP_DV_OTHERS', key='', dtype=float,
                              source=__NAME__,
                              description=(
                                  'Define the velocity of other species '
                                  'absorbers calculated in telluric preclean process'))

# Define the ccf power of the water
KW_TELLUP_CCFP_WATER = Keyword('KW_TELLUP_CCFP_WATER', key='', dtype=float,
                               source=__NAME__,
                               description=('Define the ccf power of the '
                                            'water'))

# Define the ccf power of the others
KW_TELLUP_CCFP_OTHERS = Keyword('KW_TELLUP_CCFP_OTHERS', key='', dtype=float,
                                source=__NAME__,
                                description=('Define the ccf power of the '
                                             'others'))

# Define whether precleaning was done (tellu pre-cleaning)
KW_TELLUP_DO_PRECLEAN = Keyword('KW_TELLUP_DO_PRECLEAN', key='', dtype=bool,
                                source=__NAME__,
                                description=('Define whether precleaning was '
                                             'done (tellu pre-cleaning)'))

# Define default water absorption used (tellu pre-cleaning)
KW_TELLUP_DFLT_WATER = Keyword('KW_TELLUP_DFLT_WATER', key='', dtype=float,
                               source=__NAME__,
                               description=('Define default water absorption '
                                            'used (tellu pre-cleaning)'))

# Define ccf scan range that was used (tellu pre-cleaning)
KW_TELLUP_CCF_SRANGE = Keyword('KW_TELLUP_CCF_SRANGE', key='', dtype=float,
                               source=__NAME__,
                               description=('Define ccf scan range that was '
                                            'used (tellu pre-cleaning)'))

# Define whether we cleaned OH lines
KW_TELLUP_CLEAN_OHLINES = Keyword('KW_TELLUP_CCF_SRANGE', key='', dtype=float,
                                  source=__NAME__)

# Define which orders were removed from tellu pre-cleaning
KW_TELLUP_REMOVE_ORDS = Keyword('KW_TELLUP_REMOVE_ORDS', key='', dtype=str,
                                source=__NAME__,
                                description=('Define which orders were removed '
                                             'from tellu pre-cleaning'))

# Define which min snr threshold was used for tellu pre-cleaning
KW_TELLUP_SNR_MIN_THRES = Keyword('KW_TELLUP_SNR_MIN_THRES', key='',
                                  dtype=float, source=__NAME__,
                                  description=('Define which min snr threshold '
                                               'was used for tellu '
                                               'pre-cleaning'))

# Define dexpo convergence threshold used
KW_TELLUP_DEXPO_CONV_THRES = Keyword('KW_TELLUP_DEXPO_CONV_THRES', key='',
                                     dtype=float, source=__NAME__,
                                     description=('Define dexpo convergence '
                                                  'threshold used'))

# Define the maximum number of operations used to get dexpo convergence
KW_TELLUP_DEXPO_MAX_ITR = Keyword('KW_TELLUP_DEXPO_MAX_ITR', key='',
                                  dtype=int, source=__NAME__,
                                  description=('Define the maximum number of '
                                               'operations used to get dexpo '
                                               'convergence'))

# Define the kernel threshold in abso_expo used in tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KTHRES = Keyword('KW_TELLUP_ABSOEXPO_KTHRES', key='',
                                    dtype=int, source=__NAME__,
                                    description=('Define the kernel threshold '
                                                 'in abso_expo used in tellu '
                                                 'pre-cleaning'))

# Define the wave start (same as s1d) in nm used
KW_TELLUP_WAVE_START = Keyword('KW_TELLUP_WAVE_START', key='', dtype=float,
                               source=__NAME__,
                               description=('Define the wave start (same as '
                                            's1d) in nm used'))

# Define the wave end (same as s1d) in nm used
KW_TELLUP_WAVE_END = Keyword('KW_TELLUP_WAVE_END', key='', dtype=float,
                             source=__NAME__,
                             description=('Define the wave end (same as s1d) '
                                          'in nm used'))

# Define the dv wave grid (same as s1d) in km/s used
KW_TELLUP_DVGRID = Keyword('KW_TELLUP_DVGRID', key='', dtype=float,
                           source=__NAME__,
                           description=('Define the dv wave grid (same as s1d) '
                                        'in km/s used'))

# Define the gauss width of the kernel used in abso_expo for tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KWID = Keyword('KW_TELLUP_ABSOEXPO_KWID', key='',
                                  dtype=float, source=__NAME__,
                                  description=(
                                      'Define the gauss width of the kernel '
                                      'used in abso_expo for tellu '
                                      'pre-cleaning'))

# Define the gauss shape of the kernel used in abso_expo for tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KEXP = Keyword('KW_TELLUP_ABSOEXPO_KEXP', key='',
                                  dtype=float, source=__NAME__,
                                  description=(
                                      'Define the gauss shape of the kernel '
                                      'used in abso_expo for tellu '
                                      'pre-cleaning'))

# Define the exponent of the transmission threshold used for tellu pre-cleaning
KW_TELLUP_TRANS_THRES = Keyword('KW_TELLUP_TRANS_THRES', key='',
                                dtype=float, source=__NAME__,
                                description=(
                                    'Define the exponent of the transmission '
                                    'threshold used for tellu pre-cleaning'))

# Define the threshold for discrepant tramission used for tellu pre-cleaning
KW_TELLUP_TRANS_SIGL = Keyword('KW_TELLUP_TRANS_SIGL', key='',
                               dtype=float, source=__NAME__,
                               description=(
                                   'Define the threshold for discrepant '
                                   'tramission used for tellu pre-cleaning'))

# Define the whether to force fit to header airmass used for tellu pre-cleaning
KW_TELLUP_FORCE_AIRMASS = Keyword('KW_TELLUP_FORCE_AIRMASS', key='',
                                  dtype=bool, source=__NAME__,
                                  description=(
                                      'Define the whether to force fit to '
                                      'header airmass used for tellu '
                                      'pre-cleaning'))

# Define the bounds of the exponent of other species used for tellu pre-cleaning
KW_TELLUP_OTHER_BOUNDS = Keyword('KW_TELLUP_OTHER_BOUNDS', key='',
                                 dtype=str, source=__NAME__,
                                 description=(
                                     'Define the bounds of the exponent of '
                                     'other species used for tellu '
                                     'pre-cleaning'))

# Define the bounds of the exponent of water used for tellu pre-cleaning
KW_TELLUP_WATER_BOUNDS = Keyword('KW_TELLUP_WATER_BOUNDS', key='',
                                 dtype=str, source=__NAME__,
                                 description=('Define the bounds of the '
                                              'exponent of water used for '
                                              'tellu pre-cleaning'))

# -----------------------------------------------------------------------------
# Define make telluric variables
# -----------------------------------------------------------------------------
# The template file used for mktellu calculation
KW_MKTELL_TEMP_FILE = Keyword('KW_MKTELL_TEMP_FILE', key='', dtype=str,
                              source=__NAME__,
                              description=('The template file used for '
                                           'mktellu calculation'))

# the number of template files used
KW_MKTELL_TEMPNUM = Keyword('KW_MKTELL_TEMPNUM', key='', dtype=str,
                            source=__NAME__,
                            description='the number of template files used')

# the hash for the template generation (unique)
KW_MKTELL_TEMPHASH = Keyword('KW_MKTELL_TEMPHASH', key='', dtype=str,
                             source=__NAME__,
                             description=('the hash for the template '
                                          'generation (unique)'))

# the time the template was generated
KW_MKTELL_TEMPTIME = Keyword('KW_MKTELL_TEMPTIME', key='', dtype=str,
                             source=__NAME__,
                             description=('the time the template was '
                                          'generated'))

# The blaze percentile used for mktellu calculation
KW_MKTELL_BLAZE_PRCT = Keyword('KW_MKTELL_BLAZE_PRCT', key='', dtype=float,
                               source=__NAME__,
                               description=('The blaze percentile used for '
                                            'mktellu calculation'))

# The blaze normalization cut used for mktellu calculation
KW_MKTELL_BLAZE_CUT = Keyword('KW_MKTELL_BLAZE_CUT', key='', dtype=float,
                              source=__NAME__,
                              description=('The blaze normalization cut used '
                                           'for mktellu calculation'))

# The default convolution width in pix used for mktellu calculation
KW_MKTELL_DEF_CONV_WID = Keyword('KW_MKTELL_DEF_CONV_WID', key='', dtype=int,
                                 source=__NAME__,
                                 description=('The default convolution width '
                                              'in pix used for mktellu '
                                              'calculation'))

# The median filter width used for mktellu calculation
KW_MKTELL_TEMP_MEDFILT = Keyword('KW_MKTELL_TEMP_MEDFILT', key='', dtype=float,
                                 source=__NAME__,
                                 description=('The median filter width used '
                                              'for mktellu calculation'))

# The recovered airmass value calculated in mktellu calculation
KW_MKTELL_AIRMASS = Keyword('KW_MKTELL_AIRMASS', key='', dtype=float,
                            source=__NAME__,
                            description=('The recovered airmass value '
                                         'calculated in mktellu calculation'))

# The recovered water optical depth calculated in mktellu calculation
KW_MKTELL_WATER = Keyword('KW_MKTELL_WATER', key='', dtype=float,
                          source=__NAME__,
                          description=('The recovered water optical depth '
                                       'calculated in mktellu calculation'))

# The min transmission requirement used for mktellu/ftellu
KW_MKTELL_THRES_TFIT = Keyword('KW_MKTELL_THRES_TFIT', key='', dtype=float,
                               source=__NAME__,
                               description=('The min transmission requirement '
                                            'used for mktellu/ftellu'))

# The upper limit for trans fit used in mktellu/ftellu
KW_MKTELL_TRANS_FIT_UPPER_BAD = Keyword('KW_MKTELL_TRANS_FIT_UPPER_BAD',
                                        key='', dtype=float, source=__NAME__,
                                        description=('The upper limit for '
                                                     'trans fit used in '
                                                     'mktellu/ftellu'))

# -----------------------------------------------------------------------------
# Define fit telluric variables
# -----------------------------------------------------------------------------
# The number of principle components used
KW_FTELLU_NPC = Keyword('KW_FTELLU_NPC', key='', dtype=int, source=__NAME__,
                        description='The number of principle components used')

# The number of trans files used in pc fit (closest in expo h20/others)
KW_FTELLU_NTRANS = Keyword('KW_FTELLU_NTRANS', key='', dtype=int,
                           source=__NAME__,
                           description=('The number of trans files used in pc '
                                        'fit (closest in expo h20/others)'))

# whether we added first derivative to principal components
KW_FTELLU_ADD_DPC = Keyword('KW_FTELLU_ADD_DPC', key='', dtype=bool,
                            source=__NAME__,
                            description=('whether we added first derivative to '
                                         'principal components'))

# whether we fitted the derivatives of the principal components
KW_FTELLU_FIT_DPC = Keyword('KW_FTELLU_FIT_DPC', key='', dtype=bool,
                            source=__NAME__,
                            description=('whether we fitted the derivatives of '
                                         'the principal components'))

# The source of the loaded absorption (npy file or trans_file from database)
KW_FTELLU_ABSO_SRC = Keyword('KW_FTELLU_ABSO_SRC', key='', dtype=str,
                             source=__NAME__,
                             description=('The source of the loaded absorption '
                                          '(npy file or trans_file from '
                                          'database)'))

# The prefix for molecular
KW_FTELLU_ABSO_PREFIX = Keyword('KW_FTELLU_ABSO_PREFIX', key='', dtype=float,
                                source=__NAME__,
                                description='The prefix for molecular')

# Number of good pixels requirement used
KW_FTELLU_FIT_KEEP_NUM = Keyword('KW_FTELLU_FIT_KEEP_NUM', key='', dtype=int,
                                 source=__NAME__,
                                 description=('Number of good pixels '
                                              'requirement used'))

# The minimum transmission used
KW_FTELLU_FIT_MIN_TRANS = Keyword('KW_FTELLU_FIT_MIN_TRANS', key='',
                                  dtype=float, source=__NAME__,
                                  description='The minimum transmission used')

# The minimum wavelength used
KW_FTELLU_LAMBDA_MIN = Keyword('KW_FTELLU_LAMBDA_MIN', key='', dtype=float,
                               source=__NAME__,
                               description='The minimum wavelength used')

# The maximum wavelength used
KW_FTELLU_LAMBDA_MAX = Keyword('KW_FTELLU_LAMBDA_MAX', key='', dtype=float,
                               source=__NAME__,
                               description='The maximum wavelength used')

# The smoothing kernel size [km/s] used
KW_FTELLU_KERN_VSINI = Keyword('KW_FTELLU_KERN_VSINI', key='', dtype=float,
                               source=__NAME__,
                               description=('The smoothing kernel size '
                                            '[km/s] used'))

# The image pixel size used
KW_FTELLU_IM_PX_SIZE = Keyword('KW_FTELLU_IM_PX_SIZE', key='', dtype=float,
                               source=__NAME__,
                               description='The image pixel size used')

# the number of iterations used to fit
KW_FTELLU_FIT_ITERS = Keyword('KW_FTELLU_FIT_ITERS', key='', dtype=int,
                              source=__NAME__,
                              description=('the number of iterations used '
                                           'to fit'))

# the log limit in minimum absorption used
KW_FTELLU_RECON_LIM = Keyword('KW_FTELLU_RECON_LIM', key='', dtype=float,
                              source=__NAME__,
                              description=('the log limit in minimum '
                                           'absorption used'))

# the template that was used (or None if not used)
KW_FTELLU_TEMPLATE = Keyword('KW_FTELLU_TEMPLATE', key='', dtype=str,
                             source=__NAME__,
                             description=('the template that was used (or '
                                          'None if not used)'))

# the number of template files used
KW_FTELLU_TEMPNUM = Keyword('KW_FTELLU_TEMPNUM', key='', dtype=int,
                            source=__NAME__,
                            description='the number of template files used')

# the hash for the template generation (unique)
KW_FTELLU_TEMPHASH = Keyword('KW_FTELLU_TEMPHASH', key='', dtype=str,
                             source=__NAME__,
                             description=('the hash for the template '
                                          'generation (unique)'))

# the hash for the template generation (unique)
KW_FTELLU_TEMPTIME = Keyword('KW_FTELLU_TEMPTIME', key='', dtype=str,
                             source=__NAME__,
                             description=('the hash for the template '
                                          'generation (unique)'))

# Telluric principle component amplitudes (for use with 1D list)
KW_FTELLU_AMP_PC = Keyword('KW_FTELLU_AMP_PC', key='', dtype=float,
                           source=__NAME__,
                           description=('Telluric principle component '
                                        'amplitudes (for use with 1D list)'))

# Telluric principle component first derivative
KW_FTELLU_DVTELL1 = Keyword('KW_FTELLU_DVTELL1', key='', dtype=float,
                            source=__NAME__,
                            description=('Telluric principle component '
                                         'first derivative'))

# Telluric principle component second derivative
KW_FTELLU_DVTELL2 = Keyword('KW_FTELLU_DVTELL2', key='', dtype=float,
                            source=__NAME__,
                            description=('Telluric principle component '
                                         'second derivative'))

# Tau Water depth calculated in fit tellu
KW_FTELLU_TAU_H2O = Keyword('KW_FTELLU_TAU_H2O', key='', dtype=float,
                            source=__NAME__,
                            description=('Tau Water depth calculated in '
                                         'fit tellu'))

# Tau Rest depth calculated in fit tellu
KW_FTELLU_TAU_REST = Keyword('KW_FTELLU_TAU_REST', key='', dtype=float,
                             source=__NAME__,
                             description=('Tau Rest depth calculated in '
                                          'fit tellu'))

# -----------------------------------------------------------------------------
# Define make template variables
# -----------------------------------------------------------------------------
# store the number of files used to create template
KW_MKTEMP_NFILES = Keyword('KW_MKTEMP_NFILES', key='', dtype=int,
                           source=__NAME__,
                           description=('store the number of files used to '
                                        'create template'))

# store a unique hash for this template (based on file name etc)
KW_MKTEMP_HASH = Keyword('KW_MKTEMP_HASH', key='', dtype=str,
                         source=__NAME__,
                         description=('store a unique hash for this template '
                                      '(based on file name etc)'))

# store time template was created
KW_MKTEMP_TIME = Keyword('KW_MKTEMP_TIME', key='', dtype=float,
                         source=__NAME__,
                         description='store time template was created')

# the snr order used for quality control cut in make template calculation
KW_MKTEMP_SNR_ORDER = Keyword('KW_MKTEMP_SNR_ORDER', key='', dtype=int,
                              source=__NAME__,
                              description=('the snr order used for quality '
                                           'control cut in make template calculation'))

# the snr threshold used for quality control cut in make template calculation
KW_MKTEMP_SNR_THRES = Keyword('KW_MKTEMP_SNR_THRES', key='', dtype=float,
                              source=__NAME__,
                              description=(
                                  'the snr threshold used for quality control '
                                  'cut in make template calculation'))

# the berv coverage calculated for this template calculation
KW_MKTEMP_BERV_COV = Keyword('KW_MKTEMP_BERV_COV', key='', dtype=float,
                             source=__NAME__,
                             description=('the berv coverage calculated for '
                                          'this template calculation'))

# the minimum berv coverage allowed for this template calculation
KW_MKTEMP_BERV_COV_MIN = Keyword('KW_MKTEMP_BERV_COV_MIN', key='', dtype=float,
                                 source=__NAME__,
                                 description=('the minimum berv coverage '
                                              'allowed for this template '
                                              'calculation'))

# the core snr used for this template calculation
KW_MKTEMP_BERV_COV_SNR = Keyword('KW_MKTEMP_BERV_COV_SNR', key='', dtype=float,
                                 source=__NAME__,
                                 description=('the core snr used for this '
                                              'template calculation'))

# the resolution used for this template calculation
KW_MKTEMP_BERV_COV_RES = Keyword('KW_MKTEMP_BERV_COV_RES', key='', dtype=float,
                                 source=__NAME__,
                                 description=('the resolution used for this '
                                              'template calculation'))

# -----------------------------------------------------------------------------
# Define ccf variables
# -----------------------------------------------------------------------------
# The mean rv calculated from the mean ccf
KW_CCF_MEAN_RV = Keyword('KW_CCF_MEAN_RV', key='', dtype=float, source=__NAME__,
                         description='The mean rv calculated from the mean ccf')

# the mean constrast (depth of fit ccf) from the mean ccf
KW_CCF_MEAN_CONSTRAST = Keyword('KW_CCF_MEAN_CONSTRAST', key='', dtype=float,
                                source=__NAME__,
                                description=('the mean constrast (depth of '
                                             'fit ccf) from the mean ccf'))

# the mean fwhm from the mean ccf
KW_CCF_MEAN_FWHM = Keyword('KW_CCF_MEAN_FWHM', key='', dtype=float,
                           source=__NAME__,
                           description='the mean fwhm from the mean ccf')

# the total number of mask lines used in all ccfs
KW_CCF_TOT_LINES = Keyword('KW_CCF_TOT_LINES', key='', dtype=int,
                           source=__NAME__,
                           description=('the total number of mask lines '
                                        'used in all ccfs'))

# the ccf mask file used
KW_CCF_MASK = Keyword('KW_CCF_MASK', key='', dtype=str, source=__NAME__,
                      description='the ccf mask file used')

# the ccf step used (in km/s)
KW_CCF_STEP = Keyword('KW_CCF_STEP', key='', dtype=float, source=__NAME__,
                      description='the ccf step used (in km/s)')

# the width of the ccf used (in km/s)
KW_CCF_WIDTH = Keyword('KW_CCF_WIDTH', key='', dtype=float, source=__NAME__,
                       description='the width of the ccf used (in km/s)')

# the central rv used (in km/s) rv elements run from rv +/- width in the ccf
KW_CCF_TARGET_RV = Keyword('KW_CCF_TARGET_RV', key='', dtype=float,
                           source=__NAME__,
                           description=('the central rv used (in km/s) rv '
                                        'elements run from rv +/- width in '
                                        'the ccf'))

# the read noise used in the photon noise uncertainty calculation in the ccf
KW_CCF_SIGDET = Keyword('KW_CCF_SIGDET', key='', dtype=float, source=__NAME__,
                        description=('the read noise used in the photon noise '
                                     'uncertainty calculation in the ccf'))

# the size in pixels around saturated pixels to regard as bad pixels used in
#    the ccf photon noise calculation
KW_CCF_BOXSIZE = Keyword('KW_CCF_BOXSIZE', key='', dtype=int, source=__NAME__,
                         description=(
                             'the size in pixels around saturated pixels to '
                             'regard as bad pixels used in the ccf photon '
                             'noise calculation'))

# the upper limit for good pixels (above this are bad) used in the ccf photon
#   noise calculation
KW_CCF_MAXFLUX = Keyword('KW_CCF_MAXFLUX', key='', dtype=float, source=__NAME__,
                         description=(
                             'the upper limit for good pixels (above this are '
                             'bad) used in the ccf photon noise calculation'))

# The last order used in the mean CCF (from 0 to nmax are used)
KW_CCF_NMAX = Keyword('KW_CCF_NMAX', key='', dtype=int, source=__NAME__,
                      description=('The last order used in the mean CCF (from '
                                   '0 to nmax are used)'))

# the minimum weight of a line in the CCF MASK used
KW_CCF_MASK_MIN = Keyword('KW_CCF_MASK_MIN', key='', dtype=float,
                          source=__NAME__,
                          description=('the minimum weight of a line in the '
                                       'CCF MASK used'))

# the mask width of lines in the CCF Mask used
KW_CCF_MASK_WID = Keyword('KW_CCF_MASK_WID', key='', dtype=float,
                          source=__NAME__,
                          description=('the mask width of lines in the CCF '
                                       'Mask used'))

# the wavelength units used in the CCF Mask for line centers
KW_CCF_MASK_UNITS = Keyword('KW_CCF_MASK_UNITS', key='', dtype=str,
                            source=__NAME__,
                            description=('the wavelength units used in the '
                                         'CCF Mask for line centers'))

# the dv rms calculated for spectrum [m/s]
KW_CCF_DVRMS_SP = Keyword('KW_CCF_DVRMS_SP', key='', dtype=float,
                          source=__NAME__,
                          description=('the dv rms calculated for spectrum '
                                       '[m/s]'))

# the dev rms calculated during the CCF [m/s]
KW_CCF_DVRMS_CC = Keyword('KW_CCF_DVRMS_CC', key='', dtype=float,
                          source=__NAME__,
                          description=('the dev rms calculated during the '
                                       'CCF [m/s]'))

# The radial velocity measured from the wave solution FP CCF
KW_CCF_RV_WAVE_FP = Keyword('KW_CCF_RV_WAVE_FP', key='', dtype=float,
                            source=__NAME__,
                            description=('The radial velocity measured from '
                                         'the wave solution FP CCF'))

# The radial velocity measured from a simultaneous FP CCF
#     (FP in reference channel)
KW_CCF_RV_SIMU_FP = Keyword('KW_CCF_RV_SIMU_FP', key='', dtype=float,
                            source=__NAME__,
                            description=(
                                'The radial velocity measured from a '
                                'simultaneous FP CCF (FP in reference '
                                'channel)'))

# The radial velocity drift between wave sol FP and simultaneous FP (if present)
#   if simulataneous FP not present this is just the wave solution FP CCF value
KW_CCF_RV_DRIFT = Keyword('KW_CCF_RV_DRIFT', key='', dtype=float,
                          source=__NAME__,
                          description=(
                              'The radial velocity drift between wave sol '
                              'FP and simultaneous FP (if present) if '
                              'simulataneous FP not present this is just the '
                              'wave solution FP CCF value'))

# The radial velocity measured from the object CCF against the CCF MASK
KW_CCF_RV_OBJ = Keyword('KW_CCF_RV_OBJ', key='', dtype=float, source=__NAME__,
                        description=('The radial velocity measured from the '
                                     'object CCF against the CCF MASK'))

# the corrected radial velocity of the object (taking into account the FP RVs)
KW_CCF_RV_CORR = Keyword('KW_CCF_RV_CORR', key='', dtype=float, source=__NAME__,
                         description=('the corrected radial velocity of the '
                                      'object (taking into account the '
                                      'FP RVs)'))

# the wave file used for the rv (fiber specific)
KW_CCF_RV_WAVEFILE = Keyword('KW_CCF_RV_WAVEFILE', key='', dtype=str,
                             source=__NAME__,
                             description=('the wave file used for the rv '
                                          '(fiber specific)'))

# the wave file time used for the rv [mjd] (fiber specific)
KW_CCF_RV_WAVETIME = Keyword('KW_CCF_RV_WAVETIME', key='', dtype=str,
                             source=__NAME__,
                             description=('the wave file time used for the '
                                          'rv [mjd] (fiber specific)'))

# the time diff (in days) between wave file and file (fiber specific)
KW_CCF_RV_TIMEDIFF = Keyword('KW_CCF_RV_TIMEDIFF', key='', dtype=str,
                             source=__NAME__,
                             description=('the time diff (in days) between '
                                          'wave file and file '
                                          '(fiber specific)'))

# the wave file source used for the rv reference fiber
KW_CCF_RV_WAVESRCE = Keyword('KW_CCF_RV_WAVESRCE', key='', dtype=str,
                             source=__NAME__,
                             description=('the wave file source used for '
                                          'the rv reference fiber'))

# -----------------------------------------------------------------------------
# Define polar variables
# -----------------------------------------------------------------------------
# define the Elapsed time of observation (sec)
KW_POL_ELAPTIME = Keyword('KW_POL_ELAPTIME', key='', dtype=float,
                          source=__NAME__,
                          description=('define the Elapsed time of '
                                       'observation (sec)'))

# define the MJD at center of observation
KW_POL_MJDCEN = Keyword('KW_POL_MJDCEN', key='', dtype=float, source=__NAME__,
                        description='define the MJD at center of observation')

# define the BJD at center of observation
KW_POL_BJDCEN = Keyword('KW_POL_BJDCEN', key='', dtype=float, source=__NAME__,
                        description='define the BJD at center of observation')

# define the BERV at center of observation
KW_POL_BERVCEN = Keyword('KW_POL_BERVCEN', key='', dtype=float, source=__NAME__,
                         description=('define the BERV at center of '
                                      'observation'))

# define the Mean BJD for polar sequence
KW_POL_MEAN_MJD = Keyword('KW_POL_MEAN_MJD', key='', dtype=float,
                          source=__NAME__,
                          description=('define the Mean MJD for polar '
                                       'sequence'))

# define the Mean BJD for polar sequence
KW_POL_MEAN_BJD = Keyword('KW_POL_MEAN_BJD', key='', dtype=float,
                          source=__NAME__,
                          description=('define the Mean BJD for polar '
                                       'sequence'))

# define the mean BERV of the exposures
KW_POL_MEAN_BERV = Keyword('KW_POL_MEAN_BERV', key='', dtype=float,
                           source=__NAME__,
                           description=('define the mean BERV of the '
                                        'exposures'))

# define the Stokes paremeter: Q, U, V, or I
KW_POL_STOKES = Keyword('KW_POL_STOKES', key='', dtype=str, source=__NAME__,
                        description=('define the Stokes paremeter: '
                                     'Q, U, V, or I'))

# define Number of exposures for polarimetry
KW_POL_NEXP = Keyword('KW_POL_NEXP', key='', dtype=int, source=__NAME__,
                      description=('define Number of exposures for '
                                   'polarimetry'))

# defines the Polarimetry method
KW_POL_METHOD = Keyword('KW_POL_METHOD', key='', dtype=str, source=__NAME__,
                        description='defines the Polarimetry method')


# define the Total exposure time (sec)
KW_POL_EXPTIME = Keyword('KW_POL_EXPTIME', key='', dtype=float, source=__NAME__,
                         description='define the Total exposure time (sec)')

# define the MJD at flux-weighted center of 4 exposures
KW_POL_MJD_FW_CEN = Keyword('KW_POL_MJD_FW_CEN', key='', dtype=float,
                            source=__NAME__,
                            description='define the MJD at flux-weighted '
                                        'center of 4 exposures')

# define the BJD at flux-weighted center of 4 exposures
KW_POL_BJD_FW_CEN = Keyword('KW_POL_BJD_FW_CEN', key='', dtype=float,
                            source=__NAME__,
                            description='define the BJD at flux-weighted '
                                        'center of 4 exposures')

# define whether we corrected for BERV
KW_POL_CORR_BERV = Keyword('KW_POL_CORR_BERV', key='', dtype=bool,
                           source=__NAME__,
                           description='define whether we corrected for BERV')

# define whether we corrected for source RV
KW_POL_CORR_SRV = Keyword('KW_POL_CORR_SRV', key='', dtype=bool,
                          source=__NAME__,
                          description='define whether we corrected for '
                                      'source RV')

# define whether we normalized stokes I by continuum
KW_POL_NORM_STOKESI = Keyword('KW_POL_NORM_STOKESI', key='', dtype=bool,
                              source=__NAME__,
                              description='define whether we normalized stokes'
                                          ' I by continuum')

# define whether we normalized stokes I by continuum
KW_POL_INTERP_FLUX = Keyword('KW_POL_INTERP_FLUX', key='', dtype=bool,
                             source=__NAME__,
                             description='define whether we normalized stokes '
                                         'I by continuum')

# define whether we apply polarimetric sigma-clip cleaning
KW_POL_SIGCLIP = Keyword('KW_POL_SIGCLIP', key='', dtype=bool,
                         source=__NAME__,
                         description='define whether we apply polarimetric '
                                     'sigma-clip cleaning')

# define the number of sigma swithin which to apply sigma clipping
KW_POL_NSIGMA = Keyword('KW_POL_NSIGMA', key='', dtype=int,
                         source=__NAME__,
                         description='define the number of sigma swithin which '
                                     'to apply sigma clipping')

# define whether we removed continuum polarization
KW_POL_REMOVE_CONT = Keyword('KW_POL_REMOVE_CONT', key='', dtype=int,
                             source=__NAME__,
                             description='define whether we removed continuum '
                                         'polarization')

# define the stokes I continuum detection algorithm
KW_POL_SCONT_DET_ALG = Keyword('KW_POL_SCONT_DET_ALG', key='', dtype=str,
                               source=__NAME__,
                               description='define the stokes I continuum '
                                           'detection algorithm')

# define the polar continuum detection algorithm
KW_POL_PCONT_DET_ALG =  Keyword('KW_POL_PCONT_DET_ALG', key='', dtype=str,
                               source=__NAME__,
                               description='define the polar continuum '
                                           'detection algorithm')

# define whether we used polynomial fit for continuum polarization
KW_POL_CONT_POLYFIT = Keyword('KW_POL_CONT_POLYFIT', key='', dtype=bool,
                               source=__NAME__,
                               description='define whether we used polynomial '
                                           'fit for continuum polarization')

# define polynomial degree of fit continuum polarization
KW_POL_CONT_DEG_POLY = Keyword('KW_POL_CONT_DEG_POLY', key='', dtype=int,
                               source=__NAME__,
                               description='define polynomial degree of fit '
                                           'continuum polarization')

# define the iraf function that was used to fit stokes I continuum
KW_POL_S_IRAF_FUNC = Keyword('KW_POL_S_IRAF_FUNC', key='', dtype=str,
                             source=__NAME__,
                             description='define the iraf function that '
                                         'was used to fit stokes I continuum')

# define the iraf function that was used to fit polar continuum
KW_POL_P_IRAF_FUNC = Keyword('KW_POL_P_IRAF_FUNC', key='', dtype=str,
                             source=__NAME__,
                             description='define the iraf function that was '
                                         'used to fit polar continuum')

# define the degree of the polynomial used to fit stokes I continuum
KW_POL_S_IRAF_DEGREE = Keyword('KW_POL_S_IRAF_DEGREE', key='', dtype=int,
                               source=__NAME__,
                               description='define the degree of the '
                                           'polynomial used to fit stokes '
                                           'I continuum')

# define the degree of the polynomial used to fit polar continuum
KW_POL_P_IRAF_DEGREE = Keyword('KW_POL_P_IRAF_DEGREE', key='', dtype=int,
                               source=__NAME__,
                               description='define the degree of the '
                                           'polynomial used to fit polar '
                                           'continuum')

# define the polar continuum bin size used
KW_POL_CONT_BINSIZE = Keyword('KW_POL_CONT_BINSIZE', key='', dtype=int,
                              source=__NAME__,
                              description='define the polar continuum bin '
                                          'size used')

# define the polar continuum overlap size used
KW_POL_CONT_OVERLAP = Keyword('KW_POL_CONT_OVERLAP', key='', dtype=int,
                              source=__NAME__,
                               description='define the polar continuum overlap '
                                           'size used')

# define the telluric mask parameters (1D list)
KW_POL_CONT_TELLMASK = Keyword('KW_POL_CONT_TELLMASK', key='', dtype=str,
                               source=__NAME__,
                               description='define the telluric mask '
                                           'parameters (1D list)')

# define the lsd origin
KW_LSD_ORIGIN = Keyword('KW_LSD_ORIGIN', key='', dtype=str,
                        source=__NAME__,
                        description='define the lsd origin')


# define the rv from lsd gaussian fit
KW_LSD_FIT_RV = Keyword('KW_LSD_FIT_RV', key='', dtype=float,
                        source=__NAME__,
                        description='define the rv from lsd gaussian fit')

# define the mean degree of polarization
KW_LSD_POL_MEAN = Keyword('KW_LSD_POL_MEAN', key='', dtype=float,
                          source=__NAME__,
                          description='define the mean degree of polarization')

# define the std deviation of degree of polarization
KW_LSD_POL_STDDEV = Keyword('KW_LSD_POL_MEAN', key='', dtype=float,
                            source=__NAME__,
                            description='define the std deviation of degree of '
                                        'polarization')

# define the median degree of polarization
KW_LSD_POL_MEDIAN = Keyword('KW_LSD_POL_MEDIAN', key='', dtype=float,
                            source=__NAME__,
                            description='define the median degree of '
                                        'polarization')

# define the median deviations of degree of polarization
KW_LSD_POL_MEDABSDEV = Keyword('KW_LSD_POL_MEDABSDEV', key='', dtype=float,
                               source=__NAME__,
                               description='define the median deviations of '
                                           'degree of polarization')

# define the mean of stokes VQU lsd profile
KW_LSD_STOKESVQU_MEAN = Keyword('KW_LSD_STOKESVQU_MEAN', key='', dtype=float,
                               source=__NAME__,
                               description='define the mean of stokes VQU '
                                           'lsd profile')

# define the std deviation of stokes VQU LSD profile
KW_LSD_STOKESVQU_STDDEV = Keyword('KW_LSD_STOKESVQU_STDDEV', key='',
                                  dtype=float, source=__NAME__,
                                  description='define the std deviation of '
                                              'stokes VQU LSD profile')

# define the mean of stokes VQU LSD null profile
KW_LSD_NULL_MEAN = Keyword('KW_LSD_NULL_MEAN', key='', dtype=float,
                           source=__NAME__,
                           description='define the mean of stokes VQU LSD '
                                       'null profile')

# define the std deviation of stokes vqu lsd null profile
KW_LSD_NULL_STDDEV = Keyword('KW_LSD_NULL_STDDEV', key='', dtype=float,
                           source=__NAME__,
                           description='define the std deviation of stokes '
                                       'vqu lsd null profile')

# define the mask file used in the lsd analysis
KW_LSD_MASK_FILE = Keyword('KW_LSD_MASK_FILE', key='', dtype=str,
                           source=__NAME__,
                           description='define the mask file used in the '
                                       'lsd analysis')

# define the number of lines in the original mask
KW_LSD_MASK_NUMLINES = Keyword('KW_LSD_MASK_NUMLINES', key='', dtype=int,
                               source=__NAME__,
                               description='define the number of lines in '
                                           'the original mask')

# define the number of lines used in the LSD analysis
KW_LSD_MASKLINES_USED = Keyword('KW_LSD_MASK_NUMLINES', key='', dtype=int,
                               source=__NAME__,
                               description='define the number of lines used '
                                           'in the LSD analysis')

# define the mean wavelength of lines use din lsd analysis
KW_LSD_MASKLINES_MWAVE = Keyword('KW_LSD_MASKLINES_MWAVE', key='', dtype=float,
                                source=__NAME__,
                                description='define the mean wavelength of '
                                            'lines use din lsd analysis')

# define the mean lande of lines used in lsd analysis
KW_LSD_MASKLINES_MLANDE = Keyword('KW_LSD_MASKLINES_MLANDE', key='',
                                  dtype=float, source=__NAME__,
                                 description='define the mean lande of lines '
                                             'used in lsd analysis')


# =============================================================================
#  End of configuration file
# =============================================================================
