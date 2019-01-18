"""
Default keywords for instrument

Created on 2019-01-17

@author: cook
"""
from drsmodule.constants.default.default_keywords import *


# -----------------------------------------------------------------------------
# Required header keys (main fits file)
# -----------------------------------------------------------------------------
# define the HEADER key for acquisition time
#     Note must set the date format in KW_ACQTIME_FMT
KW_ACQTIME.set(key='MJDATE')

# the format of ACQTIME as required by astropy.time
#  options are:
#          "mjd": mean julian date
#          "iso": YYYY-MM-DD HH:MM:SS.S
#          "unix": seconds since 1970-01-01 00:00:00
#          "jyear": year as a decimal number
# Dev Note: This is a "Const" not a "Keyword"
KW_ACQTIME_FMT.value = 'mjd'

# -----------------------------------------------------------------------------
# Required header keys (related to science object)
# -----------------------------------------------------------------------------
# define the observation ra HEADER key
KW_OBJRA.set(key='OBJRA')

# define the observation dec HEADER key
KW_OBJDEC.set(key='OBJDEC')

# define the observation name
KW_OBJNAME.set(key='OBJNAME')

# define the observation equinox HEADER key
KW_OBJEQUIN.set(key='OBJEQUIN')

# define the observation proper motion in ra HEADER key
KW_OBJRAPM.set(key='OBJRAPM')

# define the observation proper motion in dec HEADER key
KW_OBJDECPM.set(key='OBJDECPM')

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KW_RDNOISE.set(key='RDNOISE')

# define the gain HEADER key (used to get value only)
KW_GAIN.set(key='GAIN')

# define the exposure time HEADER key (used to get value only)
KW_EXPTIME.set(key='EXPTIME')

# define the observation type HEADER key
KW_OBSTYPE.set(key='OBSTYPE')

# define the science fiber type HEADER key
KW_CCAS.set(key='SBCCAS_P')

# define the reference fiber type HEADER key
KW_CREF.set(key='SBCREF_P')

# define the density HEADER key
KW_CDEN.set(key='SBCDEN_P')

# define polarisation HEADER key
KW_CMMTSEQ.set(key='CMMTSEQ')

# define the airmass HEADER key
KW_AIRMASS.set(key='AIRMASS')

# define the MJ end date HEADER key
KW_MJDEND.set(key='MJDEND')

# define the exposure number within sequence HEADER key
KW_CMPLTEXP.set(key='CMPLTEXP')

# define the total number of exposures HEADER key
KW_NEXP.set(key='NEXP')
