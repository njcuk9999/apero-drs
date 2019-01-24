# This is the main config file
from drsmodule.constants.core import constant_functions

# -----------------------------------------------------------------------------
# Define variables
# -----------------------------------------------------------------------------
# all definition
__all__ = ['KW_ACQTIME', 'KW_ACQTIME_FMT', 'KW_OBJRA', 'KW_OBJDEC',
           'KW_OBJNAME', 'KW_OBJEQUIN', 'KW_OBJRAPM', 'KW_OBJDECPM',
           'KW_RDNOISE', 'KW_GAIN', 'KW_EXPTIME', 'KW_OBSTYPE', 'KW_CCAS',
           'KW_CREF', 'KW_CDEN', 'KW_CMMTSEQ', 'KW_AIRMASS', 'KW_MJDEND',
           'KW_CMPLTEXP', 'KW_NEXP', 'KW_VERSION', 'KW_PPVERSION',
           'KW_DPRTYPE']
# set name
__NAME__ = 'drsmodule.constants.default.default_keywords'
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

# define the airmass HEADER key
KW_AIRMASS = Keyword('KW_AIRMASS', key='', dtype=float, source=__NAME__)

# define the MJ end date HEADER key
KW_MJDEND = Keyword('KW_MJEND', key='', dtype=float, source=__NAME__)

# define the exposure number within sequence HEADER key
KW_CMPLTEXP = Keyword('KW_CMPLTEXP', key='', dtype=int, source=__NAME__)

# define the total number of exposures HEADER key
KW_NEXP = Keyword('KW_NEXP', key='', dtype=int, source=__NAME__)

# -----------------------------------------------------------------------------
# Define general keywords
# -----------------------------------------------------------------------------
# DRS version
KW_VERSION = Keyword('KW_VERSION', key='', dtype=str, source=__NAME__)
KW_PPVERSION = Keyword('KW_PPVERSION', key='', dtype=str, source=__NAME__)

# Define the key to get the data fits file type
KW_DPRTYPE = Keyword('KW_DPRTYPE', key='', dtype=str, source=__NAME__)