"""
Default keywords for instrument

Created on 2019-01-17

@author: cook
"""
from terrapipe.config.instruments.default.default_keywords import *

# TODO: Note: If variables are not showing up MUST CHECK __all__ definition
# TODO:    in import * module

__NAME__ = 'config.instruments.spirou.default_keywords.py'

# -----------------------------------------------------------------------------
# Required header keys (main fits file)
# -----------------------------------------------------------------------------
# define the HEADER key for acquisition time
#     Note must set the date format in KW_ACQTIME_FMT
KW_ACQTIME = KW_ACQTIME.copy(__NAME__)
KW_ACQTIME.set(key='MJDATE')

# the format of ACQTIME as required by astropy.time
#  options are:
#          "mjd": mean julian date
#          "iso": YYYY-MM-DD HH:MM:SS.S
#          "unix": seconds since 1970-01-01 00:00:00
#          "jyear": year as a decimal number
# Dev Note: This is a "Const" not a "Keyword"
KW_ACQTIME_FMT = KW_ACQTIME_FMT.copy(__NAME__)
KW_ACQTIME_FMT.value = 'mjd'
# This is the dtype of the acqtime (i.e. str or float)
KW_ACQTIME_DTYPE = KW_ACQTIME_DTYPE.copy(__NAME__)
KW_ACQTIME_DTYPE.value = float

# define the observation date HEADER key
KW_DATE_OBS = KW_DATE_OBS.copy(__NAME__)
KW_DATE_OBS.set(key='DATE-OBS')
# define the observation time HEADER key
KW_UTC_OBS = KW_UTC_OBS.copy('__NAME__')
KW_UTC_OBS.set(key='UTC-OBS')

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KW_RDNOISE = KW_RDNOISE.copy(__NAME__)
KW_RDNOISE.set(key='RDNOISE')

# define the gain HEADER key (used to get value only)
KW_GAIN = KW_GAIN.copy(__NAME__)
KW_GAIN.set(key='GAIN')

# define the exposure time HEADER key (used to get value only)
KW_EXPTIME = KW_EXPTIME.copy(__NAME__)
KW_EXPTIME.set(key='EXPTIME')

# define the observation type HEADER key
KW_OBSTYPE = KW_OBSTYPE.copy(__NAME__)
KW_OBSTYPE.set(key='OBSTYPE')

# define the science fiber type HEADER key
KW_CCAS = KW_CCAS.copy(__NAME__)
KW_CCAS.set(key='SBCCAS_P')

# define the reference fiber type HEADER key
KW_CREF = KW_CREF.copy(__NAME__)
KW_CREF.set(key='SBCREF_P')

# define the density HEADER key
KW_CDEN = KW_CDEN.copy(__NAME__)
KW_CDEN.set(key='SBCDEN_P')

# define polarisation HEADER key
KW_CMMTSEQ = KW_CMMTSEQ.copy(__NAME__)
KW_CMMTSEQ.set(key='CMMTSEQ')


# define the MJ end date HEADER key
KW_MJDEND = KW_MJDEND.copy(__NAME__)
KW_MJDEND.set(key='MJDEND')

# define the exposure number within sequence HEADER key
KW_CMPLTEXP = KW_CMPLTEXP.copy(__NAME__)
KW_CMPLTEXP.set(key='CMPLTEXP')

# define the total number of exposures HEADER key
KW_NEXP = KW_NEXP.copy(__NAME__)
KW_NEXP.set(key='NEXP')

# -----------------------------------------------------------------------------
# Required header keys (related to science object)
# -----------------------------------------------------------------------------
# define the observation ra HEADER key
KW_OBJRA = KW_OBJRA.copy(__NAME__)
KW_OBJRA.set(key='OBJRA')

# define the observation dec HEADER key
KW_OBJDEC = KW_OBJDEC.copy(__NAME__)
KW_OBJDEC.set(key='OBJDEC')

# define the observation name
KW_OBJNAME = KW_OBJNAME.copy(__NAME__)
KW_OBJNAME.set(key='OBJNAME')

# define the observation equinox HEADER key
KW_OBJEQUIN = KW_OBJEQUIN.copy(__NAME__)
KW_OBJEQUIN.set(key='OBJEQUIN')

# define the observation proper motion in ra HEADER key
KW_OBJRAPM = KW_OBJRAPM.copy(__NAME__)
KW_OBJRAPM.set(key='OBJRAPM')

# define the observation proper motion in dec HEADER key
KW_OBJDECPM = KW_OBJDECPM.copy(__NAME__)
KW_OBJDECPM.set(key='OBJDECPM')

# define the airmass HEADER key
KW_AIRMASS = KW_AIRMASS.copy(__NAME__)
KW_AIRMASS.set(key='AIRMASS')

# define the weather tower temperature HEADER key
KW_WEATHER_TOWER_TEMP = KW_WEATHER_TOWER_TEMP.copy(__NAME__)
KW_WEATHER_TOWER_TEMP.set(key='TEMPERAT')

# define the cassegrain temperature HEADER key
KW_CASS_TEMP = KW_CASS_TEMP.copy(__NAME__)
KW_CASS_TEMP.set(key='SB_POL_T')

# define the humidity HEADER key
KW_HUMIDITY = KW_HUMIDITY.copy(__NAME__)
KW_HUMIDITY.set(key='RELHUMID')

# -----------------------------------------------------------------------------
# Define general keywords
# -----------------------------------------------------------------------------
# DRS version
KW_VERSION = KW_VERSION.copy(__NAME__)
KW_VERSION.set(key='VERSION', comment='DRS version')

KW_PPVERSION = KW_PPVERSION.copy(__NAME__)
KW_PPVERSION.set(key='PVERSION', comment='DRS Pre-Processing version')

# DRS process ID
KW_PID = KW_PID.copy(__NAME__)
KW_PID.set(key='DRSPID', comment='The process ID that outputted this file.')

# Processed date keyword
KW_DRS_DATE_NOW = KW_DRS_DATE_NOW.copy(__NAME__)
KW_DRS_DATE_NOW.set(key='DRSPDATE', comment='DRS Processed date')

# DRS version date keyword
KW_DRS_DATE = KW_DRS_DATE.copy(__NAME__)
KW_DRS_DATE.set(key='DRSVDATE', comment='DRS Release date')

# root keys (for use below and in finding keys later)
root_loc = 'LO'
root_flat = 'FF'
root_hc = 'LMP'

# Define the key to get the data fits file type
KW_DPRTYPE = KW_DPRTYPE.copy(__NAME__)
KW_DPRTYPE.set(key='DPRTYPE', comment='The type of file (from pre-process)')

# -----------------------------------------------------------------------------
# Define DRS input keywords
# -----------------------------------------------------------------------------
# input files
KW_INFILE1 = KW_INFILE1.copy(__NAME__)
KW_INFILE1.set(key='INF1{0:03d}', comment='Input file used to create output')
KW_INFILE2 = KW_INFILE2.copy(__NAME__)
KW_INFILE2.set(key='INF1{0:03d}', comment='Input file used to create output')
KW_INFILE3 = KW_INFILE3.copy(__NAME__)
KW_INFILE3.set(key='INF1{0:03d}', comment='Input file used to create output')

# -----------------------------------------------------------------------------
# Define database input keywords
# -----------------------------------------------------------------------------
KW_CDBDARK = KW_CDBDARK.copy(__NAME__)
KW_CDBDARK.set(key='CDBDARK', comment='The calibration DARK file used')
KW_CDBBAD = KW_CDBBAD.copy(__NAME__)
KW_CDBBAD.set(key='CDBBAD', comment='The calibration BADPIX file used')
KW_CDBBACK = KW_CDBBACK.copy(__NAME__)
KW_CDBBACK.set(key='CDBBACK', comment='The calibration BKGRDMAP file used')
KW_CDBORDP = KW_CDBORDP.copy(__NAME__)
KW_CDBORDP.set(key='CDBORDP', comment='The calibration ORDER_PROFILE file used')
KW_CDBLOCO = KW_CDBLOCO.copy(__NAME__)
KW_CDBLOCO.set(key='CDBLOCO', comment='The calibration LOC file used')
KW_CDBSHAPE = KW_CDBSHAPE.copy(__NAME__)
KW_CDBSHAPE.set(key='CDBSHAPE', comment='The calibration SHAPE file used')
KW_CDBFLAT = KW_CDBFLAT.copy(__NAME__)
KW_CDBFLAT.set(key='CDBFLAT', comment='The calibration FLAT file used')
KW_CDBBLAZE = KW_CDBBLAZE.copy(__NAME__)
KW_CDBBLAZE.set(key='CDBBLAZE', comment='The calibration BLAZE file used')
KW_CDBWAVE = KW_CDBWAVE.copy(__NAME__)
KW_CDBWAVE.set(key='CDBWAVE', comment='The calibration WAVE file used')


# -----------------------------------------------------------------------------
# Define DRS outputs keywords
# -----------------------------------------------------------------------------
KW_OUTPUT = KW_OUTPUT.copy(__NAME__)
KW_OUTPUT.set(key='DRSOUTID', comment='DRS output identification code')
KW_EXT_TYPE = KW_EXT_TYPE.copy(__NAME__)
KW_EXT_TYPE.set(key='DRS_EOUT', comment='DRS Extraction input DPRTYPE')


# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
KW_DRS_QC = KW_DRS_QC.copy(__NAME__)
KW_DRS_QC.set(key='QCC', comment='All quality control passed')
KW_DRS_QC_VAL = KW_DRS_QC_VAL.copy(__NAME__)
KW_DRS_QC_VAL.set(key='QCC{0:03d}V', comment='All quality control passed')
KW_DRS_QC_NAME = KW_DRS_QC_NAME.copy(__NAME__)
KW_DRS_QC_NAME.set(key='QCC{0:03d}N', comment='All quality control passed')
KW_DRS_QC_LOGIC = KW_DRS_QC_LOGIC.copy(__NAME__)
KW_DRS_QC_LOGIC.set(key='QCC{0:03d}L', comment='All quality control passed')
KW_DRS_QC_PASS = KW_DRS_QC_PASS.copy(__NAME__)
KW_DRS_QC_PASS.set(key='QCC{0:03d}P', comment='All quality control passed')

# -----------------------------------------------------------------------------
# Define cal_dark variables
# -----------------------------------------------------------------------------
# The fraction of dead pixels in the dark (in %)
KW_DARK_DEAD = KW_DARK_DEAD.copy(__NAME__)
KW_DARK_DEAD.set(key='DADEAD', comment='Fraction dead pixels [%]')

# The median dark level in ADU/s
KW_DARK_MED = KW_DARK_MED.copy(__NAME__)
KW_DARK_MED.set(key='DAMED', comment='median dark level [ADU/s]')

# The fraction of dead pixels in the blue part of the dark (in %)
KW_DARK_B_DEAD = KW_DARK_B_DEAD.copy(__NAME__)
KW_DARK_B_DEAD.set(key='DABDEAD', comment='Fraction dead pixels blue part [%]')

# The median dark level in the blue part of the dark in ADU/s
KW_DARK_B_MED = KW_DARK_B_MED.copy(__NAME__)
KW_DARK_B_MED.set(key='DABMED', comment='median dark level blue part [ADU/s]')

# The fraction of dead pixels in the red part of the dark (in %)
KW_DARK_R_DEAD = KW_DARK_R_DEAD.copy(__NAME__)
KW_DARK_R_DEAD.set(key='DARDEAD', comment='Fraction dead pixels red part [%]')

# The median dark level in the red part of the dark in ADU/s
KW_DARK_R_MED = KW_DARK_R_MED.copy(__NAME__)
KW_DARK_R_MED.set(key='DARMED', comment='median dark level red part [ADU/s]')

# The threshold of the dark level to retain in ADU
KW_DARK_CUT = KW_DARK_CUT.copy(__NAME__)
KW_DARK_CUT.set(key='DACUT', comment='Threshold of dark level retain [ADU/s]')

# -----------------------------------------------------------------------------
# Define cal_badpix variables
# -----------------------------------------------------------------------------
# fraction of hot pixels
KW_BHOT = KW_BHOT.copy(__NAME__)
KW_BHOT.set(key='BHOT', comment='Frac of hot px [%]')

# fraction of bad pixels from flat
KW_BBFLAT = KW_BBFLAT.copy(__NAME__)
KW_BBFLAT.set(key='BBFLAT', comment='Frac of bad px from flat [%]')

# fraction of non-finite pixels in dark
KW_BNDARK = KW_BNDARK.copy(__NAME__)
KW_BNDARK.set(key='BNDARK', comment='Frac of non-finite px in dark [%]')

# fraction of non-finite pixels in flat
KW_BNFLAT = KW_BNFLAT.copy(__NAME__)
KW_BNFLAT.set(key='BNFLAT', comment='Frac of non-finite px in flat [%]')

# fraction of bad pixels with all criteria
KW_BBAD = KW_BBAD.copy(__NAME__)
KW_BBAD.set(key='BBAD', comment='Frac of bad px with all criteria [%]')

# fraction of un-illuminated pixels (from engineering flat)
KW_BNILUM = KW_BNILUM.copy(__NAME__)
KW_BNILUM.set(key='BNILUM', comment='Frac of un-illuminated pixels [%]')

# fraction of total bad pixels
KW_BTOT = KW_BTOT.copy(__NAME__)
KW_BTOT.set(key='BTOT', comment='Frac of bad pixels (total) [%]')

# -----------------------------------------------------------------------------
# Define localisation variables
# -----------------------------------------------------------------------------
# root for localisation header keys
ROOT_DRS_LOC = ROOT_DRS_LOC.copy(__NAME__)
ROOT_DRS_LOC.value = root_loc

# Mean background (as percentage)
KW_LOC_BCKGRD = KW_LOC_BCKGRD.copy(__NAME__)
KW_LOC_BCKGRD.set(key=root_loc + 'BCKGRD', comment='mean background [%]')

# Number of orders located
KW_LOC_NBO = KW_LOC_NBO.copy(__NAME__)
KW_LOC_NBO.set(key=root_loc + 'NBO', comment='nb orders localised')

# fit degree for order centers
KW_LOC_DEG_C = KW_LOC_DEG_C.copy(__NAME__)
KW_LOC_DEG_C.set(key=root_loc + 'DEGCTR', comment='degree fit ctr ord')

# fit degree for order widths
KW_LOC_DEG_W = KW_LOC_DEG_W.copy(__NAME__)
KW_LOC_DEG_W.set(key=root_loc + 'DEGFWH', comment='degree fit width ord')

# Maximum flux in order
KW_LOC_MAXFLX = KW_LOC_MAXFLX.copy(__NAME__)
KW_LOC_MAXFLX.set(key=root_loc + 'FLXMAX', comment='max flux in order [ADU]')

# Maximum number of removed points allowed for location fit
KW_LOC_SMAXPTS_CTR = KW_LOC_SMAXPTS_CTR.copy(__NAME__)
KW_LOC_SMAXPTS_CTR.set(key=root_loc + 'CTRMAX', comment='max rm pts ctr')

# Maximum number of removed points allowed for width fit
KW_LOC_SMAXPTS_WID = KW_LOC_SMAXPTS_WID.copy(__NAME__)
KW_LOC_SMAXPTS_WID.set(key=root_loc + 'WIDMAX', comment='max rm pts width')

# Maximum rms allowed for location fit
KW_LOC_RMS_CTR = KW_LOC_RMS_CTR.copy(__NAME__)
KW_LOC_RMS_CTR.set(key=root_loc + 'RMSCTR', comment='max rms ctr')

# Maximum rms allowed for width fit (formally KW_LOC_rms_fwhm)
KW_LOC_RMS_WID = KW_LOC_RMS_WID.copy(__NAME__)
KW_LOC_RMS_WID.set(key=root_loc + 'RMSWID', comment='max rms width')

# Coeff center order
KW_LOC_CTR_COEFF = KW_LOC_CTR_COEFF.copy(__NAME__)
KW_LOC_CTR_COEFF.set(key=root_loc + 'CTR', comment='Coeff center')

# Coeff width order
KW_LOC_WID_COEFF = KW_LOC_WID_COEFF.copy(__NAME__)
KW_LOC_WID_COEFF.set(key=root_loc + 'FW', comment='Coeff fwhm')

