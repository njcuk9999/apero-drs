# This is the main config file
from terrapipe.core.constants import constant_functions

# -----------------------------------------------------------------------------
# Define variables
# -----------------------------------------------------------------------------
# all definition
__all__ = ['KW_ACQTIME', 'KW_ACQTIME_FMT', 'KW_ACQTIME_DTYPE', 'KW_OBJRA',
           'KW_OBJDEC', 'KW_OBJNAME', 'KW_OBJEQUIN', 'KW_OBJRAPM',
           'KW_OBJDECPM', 'KW_RDNOISE', 'KW_GAIN', 'KW_EXPTIME', 'KW_OBSTYPE',
           'KW_CCAS', 'KW_CREF', 'KW_CDEN', 'KW_CMMTSEQ', 'KW_AIRMASS',
           'KW_MJDEND', 'KW_CMPLTEXP', 'KW_NEXP', 'KW_VERSION', 'KW_PPVERSION',
           'KW_DPRTYPE', 'KW_PID', 'KW_INFILE1', 'KW_INFILE2', 'KW_INFILE3',
           'KW_DRS_QC', 'KW_DRS_QC_VAL', 'KW_DRS_QC_NAME', 'KW_DRS_QC_LOGIC',
           'KW_DRS_QC_PASS', 'KW_DATE_OBS', 'KW_UTC_OBS', 'KW_OUTPUT',
           'KW_EXT_TYPE', 'KW_DARK_DEAD', 'KW_DARK_MED', 'KW_DARK_B_DEAD',
           'KW_DARK_B_MED', 'KW_DARK_R_DEAD', 'KW_DARK_R_MED', 'KW_DARK_CUT',
           'KW_BHOT', 'KW_BBFLAT', 'KW_BNDARK', 'KW_BNFLAT', 'KW_BBAD',
           'KW_BNILUM', 'KW_BTOT', 'KW_CDBDARK', 'KW_CDBBAD', 'KW_CDBBACK',
           'KW_CDBORDP', 'KW_CDBLOCO', 'KW_CDBSHAPE', 'KW_CDBFLAT',
           'KW_CDBBLAZE', 'KW_CDBWAVE', 'ROOT_DRS_LOC', 'KW_LOC_BCKGRD',
           'KW_LOC_NBO', 'KW_LOC_DEG_C', 'KW_LOC_DEG_W', 'KW_LOC_MAXFLX',
           'KW_LOC_SMAXPTS_CTR', 'KW_LOC_SMAXPTS_WID', 'KW_LOC_RMS_CTR',
           'KW_LOC_RMS_WID', 'KW_LOC_CTR_COEFF', 'KW_LOC_WID_COEFF',
           'KW_WEATHER_TOWER_TEMP', 'KW_CASS_TEMP', 'KW_HUMIDITY',
           'KW_DRS_DATE_NOW', 'KW_DRS_DATE', 'KW_WAVE_NBO', 'KW_WAVE_DEG',
           'KW_WAVE_PARAM']
# set name
__NAME__ = 'terrapipe.constants.default.default_keywords'
# Constants definition
Const = constant_functions.Const
# Keyword defintion
Keyword = constant_functions.Keyword

# -----------------------------------------------------------------------------
# Required header keys (general)
# -----------------------------------------------------------------------------
# define the HEADER key for acquisition time
#     Note must set the date format in KW_ACQTIME_FMT
KW_ACQTIME = Keyword('KW_ACQTIME', key='', value=None, comment='',
                     source=__NAME__)

# the format of ACQTIME as required by astropy.time
#  options are:
#          "mjd": mean julian date
#          "iso": YYYY-MM-DD HH:MM:SS.S
#          "unix": seconds since 1970-01-01 00:00:00
#          "jyear": year as a decimal number
KW_ACQTIME_FMT = Const('KW_ACQTIME_FMT', value='mjd', dtype=str,
                       options=['mjd', 'iso', 'unix', 'jyear'],
                       source=__NAME__)
# This is the dtype of the acqtime (i.e. str or float)
KW_ACQTIME_DTYPE = Const('KW_ACQTIME_FMT', value=float, dtype=None,
                         options=[float, str], source=__NAME__)

# define the observation date HEADER key
KW_DATE_OBS = Keyword('KW_DATE_OBS', key='', dtype=float, source=__NAME__)
# define the observation time HEADER key
KW_UTC_OBS = Keyword('KW_UTC_OBS', key='', dtype=float, source=__NAME__)

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KW_RDNOISE = Keyword('KW_RDNOISE', key='', dtype=float, source=__NAME__)

# define the gain HEADER key (used to get value only)
KW_GAIN = Keyword('KW_GAIN', key='', dtype=float, source=__NAME__)

# define the exposure time HEADER key (used to get value only)
KW_EXPTIME = Keyword('KW_EXPTIME', key='', dtype=float, source=__NAME__)

# define the observation type HEADER key
KW_OBSTYPE = Keyword('KW_OBSTYPE', key='', dtype=str, source=__NAME__)

# define the science fiber type HEADER key
KW_CCAS = Keyword('KW_CCAS', key='', dtype=str, source=__NAME__)

# define the reference fiber type HEADER key
KW_CREF = Keyword('KW_CREF', key='', dtype=str, source=__NAME__)

# define the density HEADER key
KW_CDEN = Keyword('KW_CDEN', key='', dtype=str, source=__NAME__)

# define polarisation HEADER key
KW_CMMTSEQ = Keyword('KW_CMMTSEQ', key='', dtype=str, source=__NAME__)

# define the MJ end date HEADER key
KW_MJDEND = Keyword('KW_MJEND', key='', dtype=float, source=__NAME__)

# define the exposure number within sequence HEADER key
KW_CMPLTEXP = Keyword('KW_CMPLTEXP', key='', dtype=int, source=__NAME__)

# define the total number of exposures HEADER key
KW_NEXP = Keyword('KW_NEXP', key='', dtype=int, source=__NAME__)

# -----------------------------------------------------------------------------
# Required header keys (related to science object)
# -----------------------------------------------------------------------------
# define the observation ra HEADER key
KW_OBJRA = Keyword('KW_OBJRA', key='', dtype=float, source=__NAME__)

# define the observation dec HEADER key
KW_OBJDEC = Keyword('KW_OBJDE', key='', dtype=float, source=__NAME__)

# define the observation name
KW_OBJNAME = Keyword('KW_OBJNAME', key='', dtype=str, source=__NAME__)

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
KW_CDBSHAPE = Keyword('KW_CDBSHAPE', key='', dtype=str, source=__NAME__)
KW_CDBFLAT = Keyword('KW_CDBFLAT', key='', dtype=str, source=__NAME__)
KW_CDBBLAZE = Keyword('KW_CDBBLAZE', key='', dtype=str, source=__NAME__)
KW_CDBWAVE = Keyword('KW_CDBWAVE', key='', dtype=str, source=__NAME__)


# -----------------------------------------------------------------------------
# Define DRS outputs keywords
# -----------------------------------------------------------------------------
# the output key for drs outputs
KW_OUTPUT = Keyword('KW_OUTPUT', key='', dtype=str, source=__NAME__)
# the extraction type of an output (KW_DPRTYPE)
KW_EXT_TYPE = Keyword('KW_EXT_TYPE', key='', dtype=str, source=__NAME__)


# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
KW_DRS_QC = Keyword('KW_DRS_QC', key='', dtype=str, source=__NAME__)
KW_DRS_QC_VAL = Keyword('KW_DRS_QC_VAL', key='', dtype=str, source=__NAME__)
KW_DRS_QC_NAME = Keyword('KW_DRS_QC_NAME', key='', dtype=str, source=__NAME__)
KW_DRS_QC_LOGIC = Keyword('KW_DRS_QC_LOGIC', key='', dtype=str, source=__NAME__)
KW_DRS_QC_PASS = Keyword('KW_DRS_QC_PASS', key='', dtype=str, source=__NAME__)

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

# -----------------------------------------------------------------------------
# Define wave variables
# -----------------------------------------------------------------------------
# Number of orders in wave image
KW_WAVE_NBO = Keyword('KW_WAVE_NBO', key='', dtype=int, source=__NAME__)

# fit degree for wave solution
KW_WAVE_DEG = Keyword('KW_WAVE_DEG', key='', dtype=int, source=__NAME__)

# the prefix used to get the wave solution fit coefficients
KW_WAVE_PARAM = Keyword('KW_WAVE_PARAM', key='', dtype=float, source=__NAME__)




