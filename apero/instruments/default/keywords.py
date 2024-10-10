"""
Default keywords for NO INSTRUMENT

This is the default keyword config file

Created on 2019-01-17

@author: cook
"""
from apero.base import base
from apero.core.constants import constant_functions

# -----------------------------------------------------------------------------
# Define variables
# -----------------------------------------------------------------------------
__NAME__ = 'apero.instruments.default.keywords'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# Constants definition
Const = constant_functions.Const
# Keyword defintion
Keyword = constant_functions.Keyword
KDict = constant_functions.KeywordDict(__NAME__)

# -----------------------------------------------------------------------------
# Required header keys (general)
# -----------------------------------------------------------------------------
# Define the header key that uniquely identifies the file
#     (i.e. an odometer code)
KDict.add('KW_IDENTIFIER', key='NULL', value=None, source=__NAME__,
          description=('Define the header key that uniquely '
                       'identifies the file (i.e. an odometer '
                       'code)'))

# define the HEADER key for acquisition time
#     Note must set the date format in KW_ACQTIME_FMT
KDict.add('KW_ACQTIME', key='NULL', value=None, source=__NAME__,
          description=('define the HEADER key for acquisition time '
                       'Note must set the date format in '
                       'KW_ACQTIME_FMT'))

# define the MJ end date HEADER key
KDict.add('KW_MJDEND', key='NULL', value=None, source=__NAME__,
          description='define the MJ end date HEADER key')

# define the MJ date HEADER key (only used for logging)
KDict.add('KW_MJDATE', key='NULL', value=None, source=__NAME__,
          description='define the MJ date HEADER key (only used '
                      'for logging)')

# define the observation date HEADER key
KDict.add('KW_DATE_OBS', key='NULL', dtype=float, source=__NAME__,
          description='define the observation date HEADER key')
# define the observation time HEADER key
KDict.add('KW_UTC_OBS', key='NULL', dtype=float, source=__NAME__,
          description='define the observation time HEADER key')

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KDict.add('KW_RDNOISE', key='NULL', dtype=float, source=__NAME__,
          description=('define the read noise HEADER key a.k.a '
                       'sigdet (used to get value only)'))

# define the gain HEADER key (used to get value only)
KDict.add('KW_GAIN', key='NULL', dtype=float, source=__NAME__,
          description=('define the gain HEADER key (used to get '
                       'value only)'))

# define the saturation limit HEADER key
KDict.add('KW_SATURATE', key='NULL', dtype=float, source=__NAME__,
          description='define the saturation limit HEADER key')

# define the frame time HEADER key
KDict.add('KW_FRMTIME', key='NULL', dtype=float, source=__NAME__,
          description='define the frame time HEADER key')

# define the exposure time HEADER key (used to get value only)
KDict.add('KW_EXPTIME', key='NULL', dtype=float, source=__NAME__,
          description=('define the exposure time HEADER key '
                       '(used to get value only)'))
# This is the units for the exposure time
KW_EXPTIME_UNITS = Const('KW_EXPTIME_UNITS', value='s', dtype=str,
                         options=['s', 'min', 'hr', 'day'],
                         source=__NAME__,
                         description=('This is the units for the exposure '
                                      'time'))

# define the required exposure time HEADER key (used to get value only)
KDict.add('KW_EXPREQ', key='NULL', dtype=float, source=__NAME__,
          description=('define the required exposure time HEADER '
                       'key (used to get value only)'))

# define the observation type HEADER key
KDict.add('KW_OBSTYPE', key='NULL', dtype=str, source=__NAME__,
          description='define the observation type HEADER key')

# define the science fiber type HEADER key
KDict.add('KW_CCAS', key='NULL', dtype=str, source=__NAME__,
          description='define the science fiber type HEADER key')

# define the reference fiber type HEADER key
KDict.add('KW_CREF', key='NULL', dtype=str, source=__NAME__,
          description='define the reference fiber type HEADER key')

# define the calibration wheel position
KDict.add('KW_CALIBWH', key='NULL', dtype=str, source=__NAME__,
          description='define the calibration wheel position')

# define the target type (object/sky)
KDict.add('KW_TARGET_TYPE', key='NULL', dtype=str, source=__NAME__,
          description='define the target type (object/sky)')

# define the density HEADER key
KDict.add('KW_CDEN', key='NULL', dtype=str, source=__NAME__,
          description='define the density HEADER key')

# define polarisation HEADER key
KDict.add('KW_CMMTSEQ', key='NULL', dtype=str, source=__NAME__,
          description='define polarisation HEADER key')

# define the exposure number within sequence HEADER key
KDict.add('KW_CMPLTEXP', key='NULL', dtype=int, source=__NAME__,
          description=('define the exposure number within sequence '
                       'HEADER key'))

# define the total number of exposures HEADER key
KDict.add('KW_NEXP', key='NULL', dtype=int, source=__NAME__,
          description=('define the total number of exposures HEADER '
                       'key'))

# define the pi name HEADER key
KDict.add('KW_PI_NAME', key='NULL', dtype=str, source=__NAME__,
          description='define the pi name HEADER key')

# define the run id HEADER key
KDict.add('KW_RUN_ID', key='NULL', dtype=str, source=__NAME__,
          description='define the run id HEADER key')

# define the instrument HEADER key
KDict.add('KW_INSTRUMENT', key='NULL', dtype=str, source=__NAME__,
          description='define the instrument HEADER key')

# define the instrument mode header key
KDict.add('KW_INST_MODE', key='NULL', dtype=str, source=__NAME__,
          description='define the instrument mode header key')

# define the raw dprtype from the telescope
KDict.add('KW_RAW_DPRTYPE', key='NULL', dtype=str, source=__NAME__,
          description='define the raw dprtype from the '
                      'telescope')

# define the raw dpr category
KDict.add('KW_RAW_DPRCATG', key='NULL', dtype=str, source=__NAME__,
          description='define the raw dpr category')

# -----------------------------------------------------------------------------
# Required header keys (related to science object)
# -----------------------------------------------------------------------------
# define the observation ra HEADER key
KDict.add('KW_OBJRA', key='NULL', dtype=float, source=__NAME__,
          description='define the observation ra HEADER key')

# define the observation dec HEADER key
KDict.add('KW_OBJDEC', key='NULL', dtype=float, source=__NAME__,
          description='define the observation dec HEADER key')

# define the observation name
KDict.add('KW_OBJNAME', key='NULL', dtype=str, source=__NAME__,
          description='define the observation name')

# define the raw observation name
KDict.add('KW_OBJECTNAME', key='NULL', dtype=str, source=__NAME__,
          description='define the raw observation name')
KDict.add('KW_OBJECTNAME2', key='NULL', dtype=str, source=__NAME__,
          description='another object name which may need to be'
                      'checked')

# define the observation equinox HEADER key
KDict.add('KW_OBJEQUIN', key='NULL', dtype=float, source=__NAME__,
          description='define the observation equinox HEADER key')

# define the observation proper motion in ra HEADER key
KDict.add('KW_OBJRAPM', key='NULL', dtype=float, source=__NAME__,
          description=('define the observation proper motion in ra '
                       'HEADER key'))

# define the observation proper motion in dec HEADER key
KDict.add('KW_OBJDECPM', key='NULL', dtype=float, source=__NAME__,
          description=('define the observation proper motion in dec '
                       'HEADER key'))

# define the airmass HEADER key
KDict.add('KW_AIRMASS', key='NULL', dtype=float, source=__NAME__,
          description='define the airmass HEADER key')

# define the weather tower temperature HEADER key
KDict.add('KW_WEATHER_TOWER_TEMP', key='NULL', dtype=float,
          source=__NAME__,
          description=('define the weather tower '
                       'temperature HEADER key'))

# define the cassegrain temperature HEADER key
KDict.add('KW_CASS_TEMP', key='NULL', dtype=float, source=__NAME__,
          description=('define the cassegrain temperature '
                       'HEADER key'))

# define the humidity HEADER key
KDict.add('KW_HUMIDITY', key='NULL', dtype=float, source=__NAME__,
          description='define the humidity HEADER key')

# define the parallax HEADER key
KDict.add('KW_PLX', key='NULL', dtype=float, source=__NAME__,
          description='define the parallax HEADER key')

# define the rv HEADER key
KDict.add('KW_INPUTRV', key='NULL', dtype=float, source=__NAME__,
          description='define the rv HEADER key')

# define the object temperature HEADER key
KDict.add('KW_OBJ_TEMP', key='NULL', dtype=float, source=__NAME__,
          description='define the object temperature HEADER key')

# define the first polar sequence key
KDict.add('KW_POLAR_KEY_1', key='NULL', dtype=str, source=__NAME__,
          description='define the first polar sequence key')

# define the second polar sequence key
KDict.add('KW_POLAR_KEY_2', key='NULL', dtype=str, source=__NAME__,
          description='define the first polar sequence key')

# -----------------------------------------------------------------------------
# Keys added as early as possible
# -----------------------------------------------------------------------------
# Define whether a target was observed at night
KDict.add('KW_NIGHT_OBS', key='NULL', dtype=bool, source=__NAME__,
          description='Define whether a target was observed '
                      'at night')

# Define whether a target was observed during civil twilight
KDict.add('KW_CIV_TWIL', key='NULL', dtype=bool, source=__NAME__,
          description='Define whether a target was observed '
                      'during civil twilight')

# Define whether a target was observed during nautical twilight
KDict.add('KW_NAU_TWIL', key='NULL', dtype=bool, source=__NAME__,
          description='Define whether a target was observed '
                      'during nautical twilight')

# Define whether a target was observed during astronomical twilight
KDict.add('KW_AST_TWIL', key='NULL', dtype=bool, source=__NAME__,
          description='Define whether a target was observed '
                      'during astronomical twilight')

# Define the calculated sun elevation during observation
KDict.add('KW_SUN_ELEV', key='NULL', dtype=float, source=__NAME__,
          description='Define the calculated sun elevation during '
                      'observation')

# -----------------------------------------------------------------------------
# Object resolution keys
# -----------------------------------------------------------------------------
# the object name to be used by the drs (after preprocessing)
KDict.add('KW_DRS_OBJNAME', key='NULL', dtype=str, source=__NAME__,
          description=('the object name to be used by the '
                       'drs (after preprocessing)'))

# the original name of the object name used by the drs
KDict.add('KW_DRS_OBJNAME_S', key='NULL', dtype=str,
          source=__NAME__,
          description='the original name of the object name '
                      'used by the drs')

# the right ascension to be used by the drs (after preprocessing)
KDict.add('KW_DRS_RA', key='NULL', dtype=float, source=__NAME__,
          description=('the right ascension to be used by the drs '
                       '(after preprocessing)'))

# the source of the ra to be used by the drs (after preprocessing)
KDict.add('KW_DRS_RA_S', key='NULL', dtype=str, source=__NAME__,
          description=('the source of the ra to be used by the drs '
                       '(after preprocessing)'))

# the declination to be used by the drs (after preprocessing)
KDict.add('KW_DRS_DEC', key='NULL', dtype=float, source=__NAME__,
          description=('the declination to be used by the drs '
                       '(after preprocessing)'))

# the source of the dec to be used by the drs (after preprocessing)
KDict.add('KW_DRS_DEC_S', key='NULL', dtype=str, source=__NAME__,
          description=('the source of the dec to be used by the '
                       'drs (after preprocessing)'))

# the proper motion in ra to be used by the drs (after preprocessing)
KDict.add('KW_DRS_PMRA', key='NULL', dtype=float, source=__NAME__,
          description=('the proper motion in ra to be used by the '
                       'drs (after preprocessing)'))

# the source of the pmra used by the drs (afer prepreocessing)
KDict.add('KW_DRS_PMRA_S', key='NULL', dtype=str, source=__NAME__,
          description=('the source of the pmra used by the drs '
                       '(afer prepreocessing)'))

# the proper motion in dec to be used by the drs (after preprocessing)
KDict.add('KW_DRS_PMDE', key='NULL', dtype=float, source=__NAME__,
          description=('the proper motion in dec to be used by the '
                       'drs (after preprocessing)'))

# the source of the pmde used by the drs (after preprocessing)
KDict.add('KW_DRS_PMDE_S', key='NULL', dtype=str, source=__NAME__,
          description=('the source of the pmde used by the drs '
                       '(after preprocessing)'))

# the parallax to be used by the drs (after preprocessing)
KDict.add('KW_DRS_PLX', key='NULL', dtype=float, source=__NAME__,
          description=('the parallax to be used by the drs '
                       '(after preprocessing)'))

# the source of the parallax used by the drs (after preprocessing)
KDict.add('KW_DRS_PLX_S', key='NULL', dtype=str, source=__NAME__,
          description=('the source of the parallax used by the '
                       'drs (after preprocessing)'))

# the radial velocity to be used by the drs (after preprocessing)
KDict.add('KW_DRS_RV', key='NULL', dtype=float, source=__NAME__,
          description=('the radial velocity to be used by the drs '
                       '(after preprocessing)'))

# the source of the radial velocity used by the drs (after preprocessing)
KDict.add('KW_DRS_RV_S', key='NULL', dtype=str, source=__NAME__,
          description=('the source of the radial velocity used by '
                       'the drs (after preprocessing)'))

# the epoch to be used by the drs (after preprocessing)
KDict.add('KW_DRS_EPOCH', key='NULL', dtype=float, source=__NAME__,
          description=('the epoch to be used by the drs (after '
                       'preprocessing)'))

# the effective temperature to be used by the drs (after preprocessing)
KDict.add('KW_DRS_TEFF', key='NULL', dtype=float, source=__NAME__,
          description=('the effective temperature to be used by '
                       'the drs (after preprocessing)'))

# the source of teff used by the drs (after preprocessing)
KDict.add('KW_DRS_TEFF_S', key='NULL', dtype=str, source=__NAME__,
          description=('the source of teff used by the drs '
                       '(after preprocessing)'))

# the spectral type (if present) used by the drs (after preprocessing)
KDict.add('KW_DRS_SPTYPE', key='NULL', dtype=float,
          source=__NAME__,
          description='the spectral type (if present) used by '
                      'the drs (after preprocessing)')

# the source of spectral type (if present) used by the drs (after preprocessing)
KDict.add('KW_DRS_SPTYPE_S', key='NULL', dtype=str,
          source=__NAME__,
          description='the source of spectral type (if present)'
                      ' used by the drs (after preprocessing)')

# The source of the DRS object data (after preprocessing)
KDict.add('KW_DRS_DSOURCE', key='NULL', dtype=str,
          source=__NAME__,
          description='The source of the DRS object data (after'
                      ' preprocessing)')

# The date of the source of the DRS object data (after preprocessing)
KDict.add('KW_DRS_DDATE', key='NULL', dtype=str,
          source=__NAME__,
          description='The date of the source of the DRS object '
                      'data (after preprocessing)')

# -----------------------------------------------------------------------------
# Define general keywords
# -----------------------------------------------------------------------------
# DRS version
KDict.add('KW_VERSION', key='NULL', dtype=str, source=__NAME__,
          description='DRS version')

# DRS preprocessing version
KDict.add('KW_PPVERSION', key='NULL', dtype=str, source=__NAME__,
          description='DRS preprocessing version')

# DRS process ID
KDict.add('KW_PID', key='NULL', dtype=str, source=__NAME__,
          description='DRS process ID')

# Processed date keyword
KDict.add('KW_DRS_DATE_NOW', key='NULL', dtype=str,
          source=__NAME__,
          description='Processed date keyword')

# DRS version date keyword
KDict.add('KW_DRS_DATE', key='NULL', dtype=str, source=__NAME__,
          description='DRS version date keyword')

# Define the key to get the data fits file type
KDict.add('KW_DPRTYPE', key='NULL', dtype=str, source=__NAME__,
          description=('Define the key to get the data fits '
                       'file type'))

# Define the key to get the drs mode
KDict.add('KW_DRS_MODE', key='NULL', dtype=str, source=__NAME__,
          description='Define the key to get the drs mode')

# Define the mid exposure time
KDict.add('KW_MID_OBS_TIME', key='NULL', source=__NAME__,
          description='Define the mid exposure time')

# Define the method by which the MJD was calculated
KDict.add('KW_MID_OBSTIME_METHOD', key='NULL', dtype=str,
          source=__NAME__,
          description=('Define the method by which the '
                       'MJD was calculated'))

# -----------------------------------------------------------------------------
# Define DRS input keywords
# -----------------------------------------------------------------------------
# input files
KDict.add('KW_INFILE1', key='NULL', dtype=str, source=__NAME__,
          description='input files')
KDict.add('KW_INFILE2', key='NULL', dtype=str, source=__NAME__,
          description='input files')
KDict.add('KW_INFILE3', key='NULL', dtype=str, source=__NAME__,
          description='input files')

# -----------------------------------------------------------------------------
# Define database input keywords
# -----------------------------------------------------------------------------
# dark calibration file used
KDict.add('KW_CDBDARK', key='NULL', dtype=str, source=__NAME__,
          description='dark cal file used in extract')
# time of dark calibration file used
KDict.add('KW_CDTDARK', key='NULL', dtype=float, source=__NAME__,
          description='time of dark cal file used in extract')
# bad pixel calibration file used
KDict.add('KW_CDBBAD', key='NULL', dtype=str, source=__NAME__,
          description='bad pixel cal file used in extract')
# time of bad pixel calibration file used
KDict.add('KW_CDTBAD', key='NULL', dtype=float, source=__NAME__,
          description='time of bad pixel cal file used in extract')
# background calibration file used
KDict.add('KW_CDBBACK', key='NULL', dtype=str, source=__NAME__,
          description='background cal file used in extract')
# time of background calibration file used
KDict.add('KW_CDTBACK', key='NULL', dtype=float, source=__NAME__,
          description='time of background cal file used in extract')
# order profile calibration file used
KDict.add('KW_CDBORDP', key='NULL', dtype=str, source=__NAME__,
          description='order profile calibration file used')
# time of order profile calibration file used
KDict.add('KW_CDTORDP', key='NULL', dtype=float, source=__NAME__,
          description='time of orderp cal file used in extract')
# localisation calibration file used
KDict.add('KW_CDBLOCO', key='NULL', dtype=str, source=__NAME__,
          description='loco cal file used')
# localisation calibration file used
KDict.add('KW_CDTLOCO', key='NULL', dtype=float, source=__NAME__,
          description='time of loco cal file used in extract')
# shape local calibration file used
KDict.add('KW_CDBSHAPEL', key='NULL', dtype=str, source=__NAME__,
          description='shapel cal file used in extract')
# time of shape local calibration file used
KDict.add('KW_CDTSHAPEL', key='NULL', dtype=float, source=__NAME__,
          description='time of shapel cal file used in extract')
# shape dy calibration file used
KDict.add('KW_CDBSHAPEDY', key='NULL', dtype=str, source=__NAME__,
          description='shape dy cal file used in extract')
# time of shape dy calibration file used
KDict.add('KW_CDTSHAPEDY', key='NULL', dtype=str, source=__NAME__,
          description='time of shape dy cal file used in extract')
# shape dx calibration file used
KDict.add('KW_CDBSHAPEDX', key='NULL', dtype=str, source=__NAME__,
          description='shape dx calibration file used')
# time of shape dx calibration file used
KDict.add('KW_CDTSHAPEDX', key='NULL', dtype=str, source=__NAME__,
          description='time of shape dx cal file used in extract')
# flat calibration file used
KDict.add('KW_CDBFLAT', key='NULL', dtype=str, source=__NAME__,
          description='flat calibration file used in extract')
# time of flat calibration file used
KDict.add('KW_CDTFLAT', key='NULL', dtype=str, source=__NAME__,
          description='flat cal file used in extract')
# blaze calibration file used
KDict.add('KW_CDBBLAZE', key='NULL', dtype=str, source=__NAME__,
          description='blaze cal file used in extract')
# time of blaze calibration file used
KDict.add('KW_CDTBLAZE', key='NULL', dtype=str, source=__NAME__,
          description='blaze cal file used in extract')
# wave solution calibration file used
KDict.add('KW_CDBWAVE', key='NULL', dtype=str, source=__NAME__,
          description='wave sol cal file used in extract')
# time of wave solution calibration file used
KDict.add('KW_CDTWAVE', key='NULL', dtype=str, source=__NAME__,
          description='time of wave sol cal file used in extract')
# thermal calibration file used
KDict.add('KW_CDBTHERMAL', key='NULL', dtype=str, source=__NAME__,
          description='thermal cal file used in extract')
# time of thermal calibration file used
KDict.add('KW_CDTTHERMAL', key='NULL', dtype=str, source=__NAME__,
          description='time of thermal cal file used in extract')
# leak reference calibration file used
KDict.add('KW_CDBLEAKM', key='NULL', dtype=str, source=__NAME__,
          description='leak reference calibration file used')
# time of leak reference calibration file used
KDict.add('KW_CDTLEAKM', key='NULL', dtype=str, source=__NAME__,
          description='time of leak reference calibration file used')
# ref leak reference calibration file used
KDict.add('KW_CDBLEAKR', key='NULL', dtype=str, source=__NAME__,
          description='ref leak reference calibration file used')
# time of ref leak reference calibration file used
KDict.add('KW_CDTLEAKR', key='NULL', dtype=str, source=__NAME__,
          description='time of ref leak reference calibration file '
                      'used')

# additional properties of calibration

# whether the calibrations have been flipped
KDict.add('KW_C_FLIP', key='NULL', dtype=str, source=__NAME__,
          description='whether the calibrations have been flipped')
# whether the calibratoins have been converted to electrons
KDict.add('KW_C_CVRTE', key='NULL', dtype=str, source=__NAME__,
          description='whether the calibratoins have been converted '
                      'to electrons')
# whether the calibrations have been resized
KDict.add('KW_C_RESIZE', key='NULL', dtype=str, source=__NAME__,
          description='whether the calibrations have been resized')
# whether the calibrations have an ftype
KDict.add('KW_C_FTYPE', key='NULL', dtype=str, source=__NAME__,
          description='whether the calibrations have an ftype')
# the fiber name
KDict.add('KW_FIBER', key='NULL', dtype=str, source=__NAME__,
          description='the fiber name')

# the ratio used for thermal correction (method=tapas or envelope)
KDict.add('KW_THERM_RATIO', key='NULL', dtype=float,
          source=__NAME__,
          description='the ratio used for thermal correction '
                      '(method=tapas or envelope)')

# the ratio method used for thermal correction
KDict.add('KW_THERM_RATIO_U', key='NULL', dtype=str,
          source=__NAME__,
          description='the ratio method used for thermal '
                      'correction')

# define the sky model used for sky correction
KDict.add('KW_TDBSKY', key='NULL', dtype=str, source=__NAME__,
          description='the sky model used for sky correction')

# define the measured effective readout noise
KDict.add('KW_EFF_RON', key='NULL', dtype=str, source=__NAME__,
          description='The measured eff readout noise before ext')

# -----------------------------------------------------------------------------
# Define DRS outputs keywords
# -----------------------------------------------------------------------------
# the output key for drs outputs
KDict.add('KW_OUTPUT', key='NULL', dtype=str, source=__NAME__,
          description='the output key for drs outputs')

# the config run file used (if given)
KDict.add('KW_CRUNFILE', key='NULL', dtype=str, source=__NAME__,
          description='the config run file used (if given)')

# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
# the drs qc
KDict.add('KW_DRS_QC', key='NULL', dtype=str, source=__NAME__,
          description='the drs qc ')
# the value of the qc
KDict.add('KW_DRS_QC_VAL', key='NULL', dtype=str, source=__NAME__,
          description='the value of the qc')
# the name of the quality control parameter
KDict.add('KW_DRS_QC_NAME', key='NULL', dtype=str, source=__NAME__,
          description='the name of the quality control '
                      'parameter')
# the logic of the quality control parameter
KDict.add('KW_DRS_QC_LOGIC', key='NULL', dtype=str, source=__NAME__,
          description='the logic of the quality control '
                      'parameter')
# whether this quality control parameter passed
KDict.add('KW_DRS_QC_PASS', key='NULL', dtype=str, source=__NAME__,
          description='whether this quality control parameter '
                      'passed')

# -----------------------------------------------------------------------------
# Define preprocessing variables
# -----------------------------------------------------------------------------
# The shift in pixels so that image is at same location as engineering flat
KDict.add('KW_PPSHIFTX', key='NULL', dtype=float, source=__NAME__,
          description=('The shift in pixels so that image is at '
                       'same location as engineering flat'))
KDict.add('KW_PPSHIFTY', key='NULL', dtype=float, source=__NAME__,
          description=('The shift in pixels so that image is at '
                       'same location as engineering flat'))

# the number of bad pixels found via the intercept (cosmic ray rejection)
KDict.add('KW_PPC_NBAD_INTE', key='NULL', dtype=int,
          source=__NAME__,
          description=('the number of bad pixels found via '
                       'the intercept (cosmic ray rejection)'))

# the number of bad pixels found via the slope (cosmic ray rejection)
KDict.add('KW_PPC_NBAD_SLOPE', key='NULL', dtype=int,
          source=__NAME__,
          description=('the number of bad pixels found via '
                       'the slope (cosmic ray rejection)'))

# the number of bad pixels found with both intercept and slope (cosmic ray)
KDict.add('KW_PPC_NBAD_BOTH', key='NULL', dtype=int,
          source=__NAME__,
          description=('the number of bad pixels found with '
                       'both intercept and slope (cosmic '
                       'ray)'))

# The number of sigma used to construct pp reference mask
KDict.add('KW_PP_REF_NSIG', key='NULL', dtype=float, source=__NAME__,
          description=('The number of sigma used to construct '
                       'pp reference mask'))

# Define the key to store the name of the pp reference file used in pp (if used)
KDict.add('KW_PP_REF_FILE', key='NULL', dtype=str, source=__NAME__,
          description=('Define the key to store the name of the '
                       'pp reference file used in pp (if used)'))

# Define the percentile stats for LED flat in pp (50th percentile)
KDict.add('KW_PP_LED_FLAT_P50', key='NULL', dtype=float,
          source=__NAME__,
          description='Define the percentile stats for LED '
                      'flat in pp (50th percentile)')

# Define the percentile stats for LED flat in pp (16th percentile)
KDict.add('KW_PP_LED_FLAT_P16', key='NULL', dtype=float,
          source=__NAME__,
          description='Define the percentile stats for LED '
                      'flat in pp (16th percentile)')

# Define the percentile stats for LED flat in pp (84th percentile)
KDict.add('KW_PP_LED_FLAT_P84', key='NULL', dtype=float,
          source=__NAME__,
          description='Define the percentile stats for LED '
                      'flat in pp (84th percentile)')

# Define the LED flat file used
KDict.add('KW_PP_LED_FLAT_FILE', key='NULL', dtype=str,
          source=__NAME__,
          description='Define the LED flat file used')

# Define the flux-weighted mid-exposure [Expert use only]
KDict.add('KW_PP_MJD_FLUX', key='NULL', dtype=str,
          source=__NAME__,
          description='Define the flux-weighted mid-exposure '
                      '[Expert use only]')

# Define fractional RMS of posemteter [Expert use only]
KDict.add('KW_PP_RMS_POSE', key='NULL', dtype=str,
          source=__NAME__,
          description='Define fractional RMS of posemteter '
                      '[Expert use only]')

# Define median flux in posemeter [Expert use only]
KDict.add('KW_PP_MED_POSE', key='NULL', dtype=str,
          source=__NAME__,
          description='Define median flux in posemeter '
                      '[Expert use only]')

# -----------------------------------------------------------------------------
# Define apero_dark variables
# -----------------------------------------------------------------------------
# The fraction of dead pixels in the dark (in %)
KDict.add('KW_DARK_DEAD', key='NULL', dtype=float, source=__NAME__,
          description=('The fraction of dead pixels in the dark '
                       '(in %)'))

# The median dark level in ADU/s
KDict.add('KW_DARK_MED', key='NULL', dtype=float, source=__NAME__,
          description='The median dark level in ADU/s')

# The fraction of dead pixels in the blue part of the dark (in %)
KDict.add('KW_DARK_B_DEAD', key='NULL', dtype=float, source=__NAME__,
          description=('The fraction of dead pixels in the blue '
                       'part of the dark (in %)'))

# The median dark level in the blue part of the dark in ADU/s
KDict.add('KW_DARK_B_MED', key='NULL', dtype=float, source=__NAME__,
          description=('The median dark level in the blue part '
                       'of the dark in ADU/s'))

# The fraction of dead pixels in the red part of the dark (in %)
KDict.add('KW_DARK_R_DEAD', key='NULL', dtype=float, source=__NAME__,
          description=('The fraction of dead pixels in the red '
                       'part of the dark (in %)'))

# The median dark level in the red part of the dark in ADU/s
KDict.add('KW_DARK_R_MED', key='NULL', dtype=float, source=__NAME__,
          description=('The median dark level in the red part of '
                       'the dark in ADU/s'))

# The threshold of the dark level to retain in ADU
KDict.add('KW_DARK_CUT', key='NULL', dtype=float, source=__NAME__,
          description=('The threshold of the dark level to retain '
                       'in ADU'))

# -----------------------------------------------------------------------------
# Define apero_badpix variables
# -----------------------------------------------------------------------------
# fraction of hot pixels
KDict.add('KW_BHOT', key='NULL', dtype=float, source=__NAME__,
          description='fraction of hot pixels')

# fraction of bad pixels from flat
KDict.add('KW_BBFLAT', key='NULL', dtype=float, source=__NAME__,
          description='fraction of bad pixels from flat')

# fraction of non-finite pixels in dark
KDict.add('KW_BNDARK', key='NULL', dtype=float, source=__NAME__,
          description='fraction of non-finite pixels in dark')

# fraction of non-finite pixels in flat
KDict.add('KW_BNFLAT', key='NULL', dtype=float, source=__NAME__,
          description='fraction of non-finite pixels in flat')

# fraction of bad pixels with all criteria
KDict.add('KW_BBAD', key='NULL', dtype=float, source=__NAME__,
          description='fraction of bad pixels with all criteria')

# fraction of un-illuminated pixels (from engineering flat)
KDict.add('KW_BNILUM', key='NULL', dtype=float, source=__NAME__,
          description=('fraction of un-illuminated pixels (from '
                       'engineering flat)'))

# fraction of total bad pixels
KDict.add('KW_BTOT', key='NULL', dtype=float, source=__NAME__,
          description='fraction of total bad pixels')

# -----------------------------------------------------------------------------
# Define localisation variables
# -----------------------------------------------------------------------------
# Mean background (as percentage)
KDict.add('KW_LOC_BCKGRD', key='NULL', dtype=float, source=__NAME__,
          description='Mean background (as percentage)')
# Number of orders located
KDict.add('KW_LOC_NBO', key='NULL', dtype=int, source=__NAME__,
          description='Number of orders located')
# Polynomial type for localization
KDict.add('KW_LOC_POLYT', key='NULL', dtype=str, source=__NAME__,
          description='Polynomial type for localization')
# fit degree for order centers
KDict.add('KW_LOC_DEG_C', key='NULL', dtype=int, source=__NAME__,
          description='fit degree for order centers')
# fit degree for order widths
KDict.add('KW_LOC_DEG_W', key='NULL', dtype=int, source=__NAME__,
          description='fit degree for order widths')
# Maximum flux in order
KDict.add('KW_LOC_MAXFLX', key='NULL', dtype=float, source=__NAME__,
          description='Maximum flux in order')
# Maximum number of removed points allowed for location fit
KDict.add('KW_LOC_SMAXPTS_CTR', key='NULL', dtype=int,
          source=__NAME__,
          description=('Maximum number of removed points '
                       'allowed for location fit'))
# Maximum number of removed points allowed for width fit
KDict.add('KW_LOC_SMAXPTS_WID', key='NULL', dtype=int,
          source=__NAME__,
          description=('Maximum number of removed points '
                       'allowed for width fit'))
# Maximum rms allowed for location fit
KDict.add('KW_LOC_RMS_CTR', key='NULL', dtype=float, source=__NAME__,
          description='Maximum rms allowed for location fit')
# Maximum rms allowed for width fit (formally KW_LOC_rms_fwhm)
KDict.add('KW_LOC_RMS_WID', key='NULL', dtype=float, source=__NAME__,
          description=('Maximum rms allowed for width fit '
                       '(formally KW_LOC_rms_fwhm)'))
# Coeff center order
KDict.add('KW_LOC_CTR_COEFF', key='NULL', dtype=int,
          source=__NAME__,
          description='Coeff center order')
# Coeff width order
KDict.add('KW_LOC_WID_COEFF', key='NULL', dtype=int,
          source=__NAME__, description='Coeff width order')

# -----------------------------------------------------------------------------
# Define shape variables
# -----------------------------------------------------------------------------
# Shape transform dx parameter
KDict.add('KW_SHAPE_DX', key='NULL', dtype=float, source=__NAME__,
          description='Shape transform dx parameter')

# Shape transform dy parameter
KDict.add('KW_SHAPE_DY', key='NULL', dtype=float, source=__NAME__,
          description='Shape transform dy parameter')

# Shape transform A parameter
KDict.add('KW_SHAPE_A', key='NULL', dtype=float, source=__NAME__,
          description='Shape transform A parameter')

# Shape transform B parameter
KDict.add('KW_SHAPE_B', key='NULL', dtype=float, source=__NAME__,
          description='Shape transform B parameter')

# Shape transform C parameter
KDict.add('KW_SHAPE_C', key='NULL', dtype=float, source=__NAME__,
          description='Shape transform C parameter')

# Shape transform D parameter
KDict.add('KW_SHAPE_D', key='NULL', dtype=float, source=__NAME__,
          description='Shape transform D parameter')

# -----------------------------------------------------------------------------
# Define extraction variables
# -----------------------------------------------------------------------------
# The extraction type (only added for E2DS files in extraction)
KDict.add('KW_EXT_TYPE', key='NULL', dtype=str, source=__NAME__,
          description=('The extraction type (only added for E2DS '
                       'files in extraction)'))

# SNR calculated in extraction process (per order)
KDict.add('KW_EXT_SNR', key='NULL', dtype=float, source=__NAME__,
          description=('SNR calculated in extraction process '
                       '(per order)'))

# Number of orders used in extraction process
KDict.add('KW_EXT_NBO', key='NULL', dtype=int, source=__NAME__,
          description='Number of orders used in extraction process')

# the start order for extraction
KDict.add('KW_EXT_START', key='NULL', dtype=int, source=__NAME__,
          description='the start order for extraction')

# the end order for extraction
KDict.add('KW_EXT_END', key='NULL', dtype=int, source=__NAME__,
          description='the end order for extraction')

# the upper bound for extraction of order
KDict.add('KW_EXT_RANGE1', key='NULL', dtype=int, source=__NAME__,
          description='the upper bound for extraction of order')

# the lower bound for extraction of order
KDict.add('KW_EXT_RANGE2', key='NULL', dtype=int, source=__NAME__,
          description='the lower bound for extraction of order')

# whether cosmics where rejected
KDict.add('KW_COSMIC', key='NULL', dtype=int, source=__NAME__,
          description='whether cosmics where rejected')

# the cosmic cut criteria
KDict.add('KW_COSMIC_CUT', key='NULL', dtype=float, source=__NAME__,
          description='the cosmic cut criteria')

# the cosmic threshold used
KDict.add('KW_COSMIC_THRES', key='NULL', dtype=float,
          source=__NAME__,
          description='the cosmic threshold used')

# the blaze with used
KDict.add('KW_BLAZE_WID', key='NULL', dtype=float, source=__NAME__,
          description='the blaze with used')

# the blaze cut used
KDict.add('KW_BLAZE_CUT', key='NULL', dtype=float, source=__NAME__,
          description='the blaze cut used')

# the blaze degree used (to fit)
KDict.add('KW_BLAZE_DEG', key='NULL', dtype=int, source=__NAME__,
          description='the blaze degree used (to fit)')

# The blaze sinc cut threshold used
KDict.add('KW_BLAZE_SCUT', key='NULL', dtype=float, source=__NAME__,
          description='The blaze sinc cut threshold used')

# The blaze sinc sigma clip (rejection threshold) used
KDict.add('KW_BLAZE_SIGFIG', key='NULL', dtype=float,
          source=__NAME__,
          description=('The blaze sinc sigma clip (rejection '
                       'threshold) used'))

# The blaze sinc bad percentile value used
KDict.add('KW_BLAZE_BPRCNTL', key='NULL', dtype=float,
          source=__NAME__,
          description=('The blaze sinc bad percentile '
                       'value used'))

# The number of iterations used in the blaze sinc fit
KDict.add('KW_BLAZE_NITER', key='NULL', dtype=int, source=__NAME__,
          description=('The number of iterations used in the '
                       'blaze sinc fit'))

# the saturation QC limit
KDict.add('KW_SAT_QC', key='NULL', dtype=int, source=__NAME__,
          description='the saturation QC limit')

# the max saturation level
KDict.add('KW_SAT_LEVEL', key='NULL', dtype=int, source=__NAME__,
          description='the max saturation level')

# the wave starting point used for s1d
KDict.add('KW_S1D_WAVESTART', key='NULL', dtype=float,
          source=__NAME__,
          description=('the wave starting point used for '
                       's1d'))

# the wave end point used for s1d
KDict.add('KW_S1D_WAVEEND', key='NULL', dtype=float, source=__NAME__,
          description='the wave end point used for s1d')

# the wave grid kind used for s1d (wave or velocity)
KDict.add('KW_S1D_KIND', key='NULL', dtype=str, source=__NAME__,
          description=('the wave grid kind used for s1d (wave '
                       'or velocity)'))

# the bin size for wave grid kind=wave
KDict.add('KW_S1D_BWAVE', key='NULL', dtype=float, source=__NAME__,
          description='the bin size for wave grid kind=wave')

# the bin size for wave grid kind=velocity
KDict.add('KW_S1D_BVELO', key='NULL', dtype=float, source=__NAME__,
          description='the bin size for wave grid kind=velocity')

# the smooth size for the s1d
KDict.add('KW_S1D_SMOOTH', key='NULL', dtype=float, source=__NAME__,
          description='the smooth size for the s1d')

# the blaze threshold used for the s1d
KDict.add('KW_S1D_BLAZET', key='NULL', dtype=float, source=__NAME__,
          description='the blaze threshold used for the s1d')

# the observatory latitude used to calculate the BERV
KDict.add('KW_BERVLAT', key='NULL', dtype=float, source=__NAME__,
          description=('the observatory latitude used to calculate '
                       'the BERV'))

# the observatory longitude used to calculate the BERV
KDict.add('KW_BERVLONG', key='NULL', dtype=float, source=__NAME__,
          description=('the observatory longitude used to '
                       'calculate the BERV'))

# the observatory altitude used to calculate the BERV
KDict.add('KW_BERVALT', key='NULL', dtype=float, source=__NAME__,
          description=('the observatory altitude used to calculate '
                       'the BERV'))

# the BERV calculated with KW_BERVSOURCE
KDict.add('KW_BERV', key='NULL', dtype=float, source=__NAME__,
          description='the BERV calculated with KW_BERVSOURCE')

# the Barycenter Julian date calculate with KW_BERVSOURCE
KDict.add('KW_BJD', key='NULL', dtype=float, source=__NAME__,
          description=('the Barycenter Julian date calculate with '
                       'KW_BERVSOURCE'))

# the maximum BERV found across 1 year (with KW_BERVSOURCE)
KDict.add('KW_BERVMAX', key='NULL', dtype=float, source=__NAME__,
          description=('the maximum BERV found across 1 year (with '
                       'KW_BERVSOURCE)'))

# the derivative of the BERV (BERV at time + 1s - BERV)
KDict.add('KW_DBERV', key='NULL', dtype=float, source=__NAME__,
          description=('the derivative of the BERV (BERV at time + '
                       '1s - BERV)'))

# the source of the calculated BERV parameters
KDict.add('KW_BERVSOURCE', key='NULL', dtype=str, source=__NAME__,
          description=('the source of the calculated BERV '
                       'parameters'))

# the BERV calculated with the estimate
KDict.add('KW_BERV_EST', key='NULL', dtype=float, source=__NAME__,
          description='the BERV calculated with the estimate')

# the Barycenter Julian date calculated with the estimate
KDict.add('KW_BJD_EST', key='NULL', dtype=float, source=__NAME__,
          description=('the Barycenter Julian date calculated with '
                       'the estimate'))

# the maximum BERV found across 1 year (calculated with estimate)
KDict.add('KW_BERVMAX_EST', key='NULL', dtype=float, source=__NAME__,
          description=('the maximum BERV found across 1 year '
                       '(calculated with estimate)'))

# the derivative of the BERV (BERV at time + 1s - BERV) calculated with
#     estimate
KDict.add('KW_DBERV_EST', key='NULL', dtype=float, source=__NAME__,
          description=('the derivative of the BERV (BERV at time'
                       ' + 1s - BERV) calculated with estimate'))

# the actual jd time used to calculate the BERV
KDict.add('KW_BERV_OBSTIME', key='NULL', dtype=float,
          source=__NAME__,
          description=('the actual jd time used to calculate '
                       'the BERV'))

# the method used to obtain the berv obs time
KDict.add('KW_BERV_OBSTIME_METHOD', key='NULL', dtype=str,
          source=__NAME__,
          description=('the method used to obtain the '
                       'berv obs time'))

# -----------------------------------------------------------------------------
# Define leakage variables
# -----------------------------------------------------------------------------
# Define whether leak correction has been done
KDict.add('KW_LEAK_CORR', key='NULL', dtype=int, source=__NAME__,
          description=('Define whether leak correction has been '
                       'done'))

# Define the background percentile used for correcting leakage
KDict.add('KW_LEAK_BP_U', key='NULL', dtype=float, source=__NAME__,
          description=('Define the background percentile used for '
                       'correcting leakage'))

# Define the normalisation percentile used for correcting leakage
KDict.add('KW_LEAK_NP_U', key='NULL', dtype=float, source=__NAME__,
          description=('Define the normalisation percentile used '
                       'for correcting leakage'))

# Define the e-width smoothing used for correcting leakage reference
KDict.add('KW_LEAK_WSMOOTH', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the e-width smoothing used for '
                       'correcting leakage reference'))

# Define the kernel size used for correcting leakage reference
KDict.add('KW_LEAK_KERSIZE', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the kernel size used for '
                       'correcting leakage reference'))

# Define the lower bound percentile used for correcting leakage
KDict.add('KW_LEAK_LP_U', key='NULL', dtype=float, source=__NAME__,
          description=('Define the lower bound percentile used '
                       'for correcting leakage'))

# Define the upper bound percentile used for correcting leakage
KDict.add('KW_LEAK_UP_U', key='NULL', dtype=float, source=__NAME__,
          description=('Define the upper bound percentile used '
                       'for correcting leakage'))

# Define the bad ratio offset limit used for correcting leakage
KDict.add('KW_LEAK_BADR_U', key='NULL', dtype=float, source=__NAME__,
          description=('Define the bad ratio offset limit used '
                       'for correcting leakage'))

# -----------------------------------------------------------------------------
# Define wave variables
# -----------------------------------------------------------------------------
# Number of orders in wave image
KDict.add('KW_WAVE_NBO', key='NULL', dtype=int, source=__NAME__,
          description='Number of orders in wave image')

# fit degree for wave solution
KDict.add('KW_WAVE_DEG', key='NULL', dtype=int, source=__NAME__,
          description='fit degree for wave solution')

# wave polynomial type
KDict.add('KW_WAVE_POLYT', key='NULL', dtype=str, source=__NAME__,
          description='type of wave polynomial')

# the wave file used
KDict.add('KW_WAVEFILE', key='NULL', dtype=str, source=__NAME__,
          description='the wave file used')

# the wave file mid exptime [mjd]
KDict.add('KW_WAVETIME', key='NULL', dtype=float, source=__NAME__,
          description='the wave file mid exptime [mjd]')

# the wave source of the wave file used
KDict.add('KW_WAVESOURCE', key='NULL', dtype=str, source=__NAME__,
          description='the wave source of the wave file used')

# the wave coefficients
KDict.add('KW_WAVECOEFFS', key='NULL', dtype=float, source=__NAME__,
          description='the wave coefficients')

# the wave echelle numbers
KDict.add('KW_WAVE_ECHELLE', key='NULL', dtype=float,
          source=__NAME__,
          description='the wave echelle numbers')

# the initial wave file used for wave solution
KDict.add('KW_INIT_WAVE', key='NULL', dtype=str, source=__NAME__,
          description=('the initial wave file used for wave '
                       'solution'))

# define the cavity width polynomial key
KDict.add('KW_CAVITY_WIDTH', key='NULL', dtype=float,
          source=__NAME__,
          description='define the cavity width polynomial key')

# define the cavity fit degree used
KDict.add('KW_CAVITY_DEG', key='NULL', dtype=int,
          source=__NAME__,
          description='define the cavity fit degree used')

# define the cavity poly zero point (to be added on when using)
KDict.add('KW_CAV_PEDESTAL', key='NULL', dtype=int,
          source=__NAME__,
          description='define the cavity poly zero point '
                      '(to be added on when using)')

# define the mean hc velocity calculated
KDict.add('KW_WAVE_MEANHC', key='NULL', dtype=float,
          source=__NAME__,
          description='define the mean hc velocity calculated')

# define the err on mean hc velocity calculated
KDict.add('KW_WAVE_EMEANHC', key='NULL', dtype=float,
          source=__NAME__,
          description='define the err on mean hc velocity '
                      'calculated')

# -----------------------------------------------------------------------------
# the fit degree for wave solution used
KDict.add('KW_WAVE_FITDEG', key='NULL', dtype=int, source=__NAME__,
          description='the fit degree for wave solution used')

# the mode used to calculate the hc wave solution
KDict.add('KW_WAVE_MODE_HC', key='NULL', dtype=str, source=__NAME__,
          description=('the mode used to calculate the hc '
                       'wave solution'))

# the mode used to calculate the fp wave solution
KDict.add('KW_WAVE_MODE_FP', key='NULL', dtype=str, source=__NAME__,
          description=('the mode used to calculate the fp '
                       'wave solution'))

# the echelle number of the first order used
KDict.add('KW_WAVE_ECHELLE_START', key='NULL', dtype=int,
          source=__NAME__,
          description=('the echelle number of the first '
                       'order used'))

# the width of the box for fitting hc lines used
KDict.add('KW_WAVE_HCG_WSIZE', key='NULL', dtype=int,
          source=__NAME__,
          description=('the width of the box for fitting hc '
                       'lines used'))

# the sigma above local rms for fitting hc lines used
KDict.add('KW_WAVE_HCG_SIGPEAK', key='NULL', dtype=float,
          source=__NAME__,
          description=('the sigma above local rms for '
                       'fitting hc lines used'))

# the fit degree for the gaussian peak fitting used
KDict.add('KW_WAVE_HCG_GFITMODE', key='NULL', dtype=int,
          source=__NAME__,
          description=('the fit degree for the gaussian '
                       'peak fitting used'))

# the min rms for gaussian peak fitting used
KDict.add('KW_WAVE_HCG_FB_RMSMIN', key='NULL', dtype=float,
          source=__NAME__,
          description=('the min rms for gaussian peak '
                       'fitting used'))

# the max rms for gaussian peak fitting used
KDict.add('KW_WAVE_HCG_FB_RMSMAX', key='NULL', dtype=float,
          source=__NAME__,
          description=('the max rms for gaussian peak '
                       'fitting used'))

# the min e-width of the line for gaussian peak fitting used
KDict.add('KW_WAVE_HCG_EWMIN', key='NULL', dtype=float,
          source=__NAME__,
          description=('the min e-width of the line for '
                       'gaussian peak fitting used'))

# the min e-width of the line for gaussian peak fitting used
KDict.add('KW_WAVE_HCG_EWMAX', key='NULL', dtype=float,
          source=__NAME__,
          description=('the min e-width of the line for '
                       'gaussian peak fitting used'))

# the filename for the HC line list generated
KDict.add('KW_WAVE_HCLL_FILE', key='NULL', dtype=str,
          source=__NAME__,
          description=('the filename for the HC line list '
                       'generated'))

# the number of bright lines to used in triplet fit
KDict.add('KW_WAVE_TRP_NBRIGHT', key='NULL', dtype=int,
          source=__NAME__,
          description=('the number of bright lines to used '
                       'in triplet fit'))

# the number of iterations done in triplet fit
KDict.add('KW_WAVE_TRP_NITER', key='NULL', dtype=float,
          source=__NAME__,
          description=('the number of iterations done in '
                       'triplet fit'))

# the max distance between catalog line and initial guess line in triplet fit
KDict.add('KW_WAVE_TRP_CATGDIST', key='NULL', dtype=float,
          source=__NAME__,
          description=(
              'the max distance between catalog line and '
              'initial guess line in triplet fit'))

# the fit degree for triplet fit
KDict.add('KW_WAVE_TRP_FITDEG', key='NULL', dtype=int,
          source=__NAME__,
          description='the fit degree for triplet fit')

# the minimum number of lines required per order in triplet fit
KDict.add('KW_WAVE_TRP_MIN_NLINES', key='NULL', dtype=int,
          source=__NAME__,
          description=('the minimum number of lines '
                       'required per order in triplet fit'))

# the total number of lines required in triplet fit
KDict.add('KW_WAVE_TRP_TOT_NLINES', key='NULL', dtype=int,
          source=__NAME__,
          description=('the total number of lines '
                       'required in triplet fit'))

# the degree(s) of fit to ensure continuity in triplet fit
KDict.add('KW_WAVE_TRP_ORDER_FITCONT', key='NULL',
          dtype=float, source=__NAME__,
          description=('the degree(s) of fit to '
                       'ensure continuity in '
                       'triplet fit'))

# the iteration number for sigma clip in triplet fit
KDict.add('KW_WAVE_TRP_SCLIPNUM', key='NULL', dtype=float,
          source=__NAME__,
          description=('the iteration number for sigma '
                       'clip in triplet fit'))

# the sigma clip threshold in triplet fit
KDict.add('KW_WAVE_TRP_SCLIPTHRES', key='NULL', dtype=float,
          source=__NAME__,
          description=('the sigma clip threshold in '
                       'triplet fit'))

# the distance away in dv to reject order triplet in triplet fit
KDict.add('KW_WAVE_TRP_DVCUTORD', key='NULL', dtype=float,
          source=__NAME__,
          description=('the distance away in dv to reject '
                       'order triplet in triplet fit'))

# the distance away in dv to reject all triplet in triplet fit
KDict.add('KW_WAVE_TRP_DVCUTALL', key='NULL', dtype=float,
          source=__NAME__,
          description=('the distance away in dv to reject '
                       'all triplet in triplet fit'))

# the wave resolution map dimensions
KDict.add('KW_WAVE_RES_MAPSIZE', key='NULL', dtype=int,
          source=__NAME__,
          description=('the wave resolution map '
                       'dimensions'))

# the width of the box for wave resolution map
KDict.add('KW_WAVE_RES_WSIZE', key='NULL', dtype=float,
          source=__NAME__,
          description=('the width of the box for wave '
                       'resolution map'))

# the max deviation in rms allowed in wave resolution map
KDict.add('KW_WAVE_RES_MAXDEVTHRES', key='NULL',
          dtype=float, source=__NAME__,
          description=('the max deviation in rms '
                       'allowed in wave resolution map'))

# the littrow start order used for HC
KDict.add('KW_WAVE_LIT_START_1', key='NULL', dtype=int,
          source=__NAME__,
          description=('the littrow start order used '
                       'for HC'))

# the littrow end order used for HC
KDict.add('KW_WAVE_LIT_END_1', key='NULL', dtype=float,
          source=__NAME__,
          description='the littrow end order used for HC')

# the orders removed from the littrow test
KDict.add('KW_WAVE_LIT_RORDERS', key='NULL', dtype=float,
          source=__NAME__,
          description=('the orders removed from the '
                       'littrow test'))

# the littrow order initial value used for HC
KDict.add('KW_WAVE_LIT_ORDER_INIT_1', key='NULL',
          dtype=int, source=__NAME__,
          description=('the littrow order initial '
                       'value used for HC'))

# the littrow order start value used for HC
KDict.add('KW_WAVE_LIT_ORDER_START_1', key='NULL',
          dtype=int, source=__NAME__,
          description=('the littrow order start '
                       'value used for HC'))

# the littrow order end value used for HC
KDict.add('KW_WAVE_LIT_ORDER_END_1', key='NULL',
          dtype=int, source=__NAME__,
          description=('the littrow order end value '
                       'used for HC'))

# the littrow x cut step value used for HC
KDict.add('KW_WAVE_LITT_XCUTSTEP_1', key='NULL',
          dtype=int, source=__NAME__,
          description=('the littrow x cut step value '
                       'used for HC'))

# the littrow fit degree value used for HC
KDict.add('KW_WAVE_LITT_FITDEG_1', key='NULL', dtype=int,
          source=__NAME__,
          description=('the littrow fit degree value '
                       'used for HC'))

# the littrow extrapolation fit degree value used for HC
KDict.add('KW_WAVE_LITT_EXT_FITDEG_1', key='NULL',
          dtype=int, source=__NAME__,
          description=('the littrow extrapolation '
                       'fit degree value used for HC'))

# the littrow extrapolation start order value used for HC
KDict.add('KW_WAVE_LITT_EXT_ORD_START_1', key='NULL',
          dtype=int, source=__NAME__,
          description=('the littrow extrapolation '
                       'start order value used '
                       'for HC'))

# the first order used for FP wave sol improvement
KDict.add('KW_WFP_ORD_START', key='NULL', dtype=int,
          source=__NAME__,
          description=('the first order used for FP wave sol '
                       'improvement'))

# the last order used for FP wave sol improvement
KDict.add('KW_WFP_ORD_FINAL', key='NULL', dtype=int,
          source=__NAME__,
          description=('the last order used for FP wave sol '
                       'improvement'))

# the blaze threshold used for FP wave sol improvement
KDict.add('KW_WFP_BLZ_THRES', key='NULL', dtype=float,
          source=__NAME__,
          description=('the blaze threshold used for FP wave '
                       'sol improvement'))

# the minimum fp peak pixel sep used for FP wave sol improvement
KDict.add('KW_WFP_XDIFF_MIN', key='NULL', dtype=float,
          source=__NAME__,
          description=('the minimum fp peak pixel sep used '
                       'for FP wave sol improvement'))

# the maximum fp peak pixel sep used for FP wave sol improvement
KDict.add('KW_WFP_XDIFF_MAX', key='NULL', dtype=float,
          source=__NAME__,
          description=('the maximum fp peak pixel sep used '
                       'for FP wave sol improvement'))

# the initial value of the FP effective cavity width used
KDict.add('KW_WFP_DOPD0', key='NULL', dtype=float, source=__NAME__,
          description=('the initial value of the FP effective '
                       'cavity width used'))

# the  maximum fraction wavelength offset btwn xmatch fp peaks used
KDict.add('KW_WFP_LL_OFFSET', key='NULL', dtype=float,
          source=__NAME__,
          description=('the maximum fraction wavelength '
                       'offset btwn xmatch fp peaks used'))

# the max dv to keep hc lines used
KDict.add('KW_WFP_DVMAX', key='NULL', dtype=float, source=__NAME__,
          description='the max dv to keep hc lines used')

# the used polynomial fit degree (to fit wave solution)
KDict.add('KW_WFP_LLFITDEG', key='NULL', dtype=int,
          source=__NAME__,
          description=('the used polynomial fit degree (to '
                       'fit wave solution)'))

# whether the cavity file was updated
KDict.add('KW_WFP_UPDATECAV', key='NULL', dtype=int,
          source=__NAME__,
          description='whether the cavity file was updated')

# the mode used to fit the FP cavity
KDict.add('KW_WFP_FPCAV_MODE', key='NULL', dtype=int,
          source=__NAME__,
          description='the mode used to fit the FP cavity')

# the mode used to fit the wavelength
KDict.add('KW_WFP_LLFIT_MODE', key='NULL', dtype=int,
          source=__NAME__,
          description='the mode used to fit the wavelength')

# the minimum instrumental error used
KDict.add('KW_WFP_ERRX_MIN', key='NULL', dtype=float,
          source=__NAME__,
          description='the minimum instrumental error used')

# the max rms for the wave sol sig clip
KDict.add('KW_WFP_MAXLL_FIT_RMS', key='NULL', dtype=float,
          source=__NAME__,
          description=('the max rms for the wave sol '
                       'sig clip'))

# the echelle number used for the first order
KDict.add('KW_WFP_T_ORD_START', key='NULL', dtype=int,
          source=__NAME__,
          description=('the echelle number used for the '
                       'first order'))

# the weight below which fp lines are rejected
KDict.add('KW_WFP_WEI_THRES', key='NULL', dtype=float,
          source=__NAME__,
          description=('the weight below which fp lines are '
                       'rejected'))

# the polynomial degree fit order used for fitting the fp cavity
KDict.add('KW_WFP_CAVFIT_DEG', key='NULL', dtype=int,
          source=__NAME__,
          description=('the polynomial degree fit order '
                       'used for fitting the fp cavity'))

# the largest jump in fp that was allowed
KDict.add('KW_WFP_LARGE_JUMP', key='NULL', dtype=float,
          source=__NAME__,
          description=('the largest jump in fp that was '
                       'allowed'))

# the index to start crossmatching fps at
KDict.add('KW_WFP_CM_INDX', key='NULL', dtype=float, source=__NAME__,
          description=('the index to start crossmatching '
                       'fps at'))

# the FP widths used for each order (1D list)
KDict.add('KW_WFP_WIDUSED', key='NULL', dtype=float, source=__NAME__,
          description=('the FP widths used for each order '
                       '(1D list)'))

# the percentile to normalise the FP flux per order used
KDict.add('KW_WFP_NPERCENT', key='NULL', dtype=float,
          source=__NAME__,
          description=('the percentile to normalise the FP '
                       'flux per order used'))

# the normalised limited used to detect FP peaks
KDict.add('KW_WFP_LIMIT', key='NULL', dtype=float, source=__NAME__,
          description=('the normalised limited used to detect '
                       'FP peaks'))

# the normalised cut width for large peaks used
KDict.add('KW_WFP_CUTWIDTH', key='NULL', dtype=float,
          source=__NAME__,
          description=('the normalised cut width for large '
                       'peaks used'))

# Wavelength solution for fiber C that is source of the WFP keys
KDict.add('KW_WFP_FILE', key='NULL', dtype=str, source=__NAME__,
          description=('Wavelength solution for fiber C that is '
                       'source of the WFP keys'))

# drift of the FP file used for the wavelength solution
KDict.add('KW_WFP_DRIFT', key='NULL', dtype=float, source=__NAME__,
          description=('drift of the FP file used for the '
                       'wavelength solution'))

# FWHM of the wave FP file CCF
KDict.add('KW_WFP_FWHM', key='NULL', dtype=float, source=__NAME__,
          description='FWHM of the wave FP file CCF')

# Contrast of the wave FP file CCF
KDict.add('KW_WFP_CONTRAST', key='NULL', dtype=float,
          source=__NAME__,
          description='Contrast of the wave FP file CCF')

# Mask for the wave FP file CCF
KDict.add('KW_WFP_MASK', key='NULL', dtype=float, source=__NAME__,
          description='Mask for the wave FP file CCF')

# Number of lines for the wave FP file CCF
KDict.add('KW_WFP_LINES', key='NULL', dtype=float, source=__NAME__,
          description='Number of lines for the wave FP file CCF')

# Target RV for the wave FP file CCF
KDict.add('KW_WFP_TARG_RV', key='NULL', dtype=float, source=__NAME__,
          description='Target RV for the wave FP file CCF')

# Width for the wave FP file CCF
KDict.add('KW_WFP_WIDTH', key='NULL', dtype=float, source=__NAME__,
          description='Width for the wave FP file CCF')

# Step for the wave FP file CCF
KDict.add('KW_WFP_STEP', key='NULL', dtype=float, source=__NAME__,
          description='Step for the wave FP file CCF')

# The sigdet used for FP file CCF
KDict.add('KW_WFP_SIGDET', key='NULL', dtype=float, source=__NAME__,
          description='The sigdet used for FP file CCF')

# The boxsize used for FP file CCF
KDict.add('KW_WFP_BOXSIZE', key='NULL', dtype=int, source=__NAME__,
          description='The boxsize used for FP file CCF')

# The max flux used for the FP file CCF
KDict.add('KW_WFP_MAXFLUX', key='NULL', dtype=float, source=__NAME__,
          description='The max flux used for the FP file CCF')

# The det noise used for the FP file CCF
KDict.add('KW_WFP_DETNOISE', key='NULL', dtype=float,
          source=__NAME__,
          description=('The det noise used for the '
                       'FP file CCF'))

# the highest order used for the FP file CCF
KDict.add('KW_WFP_NMAX', key='NULL', dtype=int, source=__NAME__,
          description=('the highest order used for the '
                       'FP file CCF'))

# The weight of the CCF mask (if 1 force all weights equal) used for FP CCF
KDict.add('KW_WFP_MASKMIN', key='NULL', dtype=float, source=__NAME__,
          description=('The weight of the CCF mask (if 1 '
                       'force all weights equal) used for '
                       'FP CCF'))

# The width of the CCF mask template line (if 0 use natural) used for FP CCF
KDict.add('KW_WFP_MASKWID', key='NULL', dtype=float, source=__NAME__,
          description=('The width of the CCF mask template '
                       'line (if 0 use natural) used for FP CCF'))

# The units of the input CCF mask (converted to nm in code)
KDict.add('KW_WFP_MASKUNITS', key='NULL', dtype=str,
          source=__NAME__,
          description=('The units of the input CCF mask '
                       '(converted to nm in code)'))

# number of iterations for convergence used in wave night (hc)
KDict.add('KW_WNT_NITER1', key='NULL', dtype=int, source=__NAME__,
          description=('number of iterations for convergence '
                       'used in wave night (hc)'))

# number of iterations for convergence used in wave night (fp)
KDict.add('KW_WNT_NITER2', key='NULL', dtype=int, source=__NAME__,
          description=('number of iterations for convergence '
                       'used in wave night (fp)'))

# starting point for the cavity corrections used in wave night
KDict.add('KW_WNT_DCAVITY', key='NULL', dtype=int, source=__NAME__,
          description=('starting point for the cavity '
                       'corrections used in wave night'))

# source fiber for the cavity correction
KDict.add('KW_WNT_DCAVSRCE', key='NULL', dtype=str, source=__NAME__,
          description=('source fiber for the cavity '
                       'correction'))

# define the sigma clip value to remove bad hc lines used
KDict.add('KW_WNT_HCSIGCLIP', key='NULL', dtype=float,
          source=__NAME__,
          description=('define the sigma clip value to remove '
                       'bad hc lines used'))

# median absolute deviation cut off used
KDict.add('KW_WNT_MADLIMIT', key='NULL', dtype=float,
          source=__NAME__,
          description=('median absolute deviation cut off '
                       'used'))

# sigma clipping for the fit used in wave night
KDict.add('KW_WNT_NSIG_FIT', key='NULL', dtype=int, source=__NAME__,
          description=('sigma clipping for the fit used '
                       'in wave night'))

# -----------------------------------------------------------------------------
# Define wave ref (new) variables
# -----------------------------------------------------------------------------
# number of orders for the resolution map header
KDict.add('KW_RESMAP_NBO', key='NULL', dtype=int, source=__NAME__,
          description='number of orders for the resolution '
                      'map header')

# number of pixels in an order for the resolution map header
KDict.add('KW_RESMAP_NBPIX', key='NULL', dtype=int, source=__NAME__,
          description='number of pixels in an order for the '
                      'resolution map header')

# current bin number for order direction for the resolution map header
KDict.add('KW_RESMAP_BINORD', key='NULL', dtype=int, source=__NAME__,
          description='current bin number for order direction '
                      'for the resolution map header')

# total number of bins in order direction for the resolution map header
KDict.add('KW_RESMAP_NBINORD', key='NULL', dtype=int,
          source=__NAME__,
          description='total number of bins in order '
                      'direction for the resolution map '
                      'header')

# current bin number in spatial direction for the resolution map header
KDict.add('KW_RESMAP_BINPIX', key='NULL', dtype=int,
          source=__NAME__,
          description='current bin number in spatial direction'
                      ' for the resolution map header')

# total number of bins in spatial direction for the resolution map header
KDict.add('KW_RESMAP_NBINPIX', key='NULL', dtype=int,
          source=__NAME__,
          description='total number of bins in spatial '
                      'direction for the resolution map '
                      'header')

# First order used in this sector
KDict.add('KW_RES_MAP_ORDLOW', key='NULL', dtype=int,
          source=__NAME__,
          description='First order used in this sector')

# Last order used in this sector
KDict.add('KW_RES_MAP_ORDHIGH', key='NULL', dtype=int,
          source=__NAME__,
          description='Last order used in this sector')

# First pixel used in this sector
KDict.add('KW_RES_MAP_PIXLOW', key='NULL', dtype=int,
          source=__NAME__,
          description='First pixel used in this sector')

# Last pixel used in this sector
KDict.add('KW_RES_MAP_PIXHIGH', key='NULL', dtype=int,
          source=__NAME__,
          description='Last pixel used in this sector')

# FWHM from fit for this sector
KDict.add('KW_RES_MAP_FWHM', key='NULL', dtype=int,
          source=__NAME__,
          description='FWHM from fit for this sector')

# Amplitude from fit for this sector
KDict.add('KW_RES_MAP_AMP', key='NULL', dtype=int,
          source=__NAME__,
          description='FWHM from fit for this sector')

# Exponent from fit for this sector
KDict.add('KW_RES_MAP_EXPO', key='NULL', dtype=int,
          source=__NAME__,
          description='Exponent from fit for this sector')

# Measured effective resolution measured for this sector
KDict.add('KW_RES_MAP_RESEFF', key='NULL', dtype=int,
          source=__NAME__,
          description='Measured effective resolution measured'
                      ' for this sector')

# -----------------------------------------------------------------------------
# Define telluric sky model variables
# -----------------------------------------------------------------------------
# Defines whether we have a sky correction for the science fiber
KDict.add('KW_HAS_SKY_SCI', key='NULL', dtype=bool,
          source=__NAME__,
          description='Defines whether we have a sky correction '
                      'for the science fiber')

# Defines whether we have a sky correction for the calib fiber
KDict.add('KW_HAS_SKY_CAL', key='NULL', dtype=bool,
          source=__NAME__,
          description='Defines whether we have a sky correction '
                      'for the science fiber')

# Defines which fiber was used for the science fiber sky correction model
KDict.add('KW_SKY_SCI_FIBER', key='NULL', dtype=str,
          source=__NAME__,
          description='Defines which fiber was used for the '
                      'science fiber sky correction model')

# Defines which fiber was used for the calib fiber sky correction model
KDict.add('KW_SKY_CAL_FIBER', key='NULL', dtype=str,
          source=__NAME__,
          description='Defines which fiber was used for the '
                      'science fiber sky correction model')

# -----------------------------------------------------------------------------
# Define telluric preclean variables
# -----------------------------------------------------------------------------
# Define the exponent of water key from telluric preclean process
KDict.add('KW_TELLUP_EXPO_WATER', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the exponent of water key '
                       'from telluric preclean process'))

# Define the exponent of other species from telluric preclean process
KDict.add('KW_TELLUP_EXPO_OTHERS', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the exponent of other '
                       'species from telluric preclean process'))

# Define the velocity of water absorbers calculated in telluric preclean process
KDict.add('KW_TELLUP_DV_WATER', key='NULL', dtype=float,
          source=__NAME__,
          description=(
              'Define the velocity of water absorbers '
              'calculated in telluric preclean process'))

# Define the velocity of other species absorbers calculated in telluric
#     preclean process
KDict.add('KW_TELLUP_DV_OTHERS', key='NULL', dtype=float,
          source=__NAME__,
          description=(
              'Define the velocity of other species '
              'absorbers calculated in telluric preclean process'))

# Define the ccf power of the water
KDict.add('KW_TELLUP_CCFP_WATER', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the ccf power of the '
                       'water'))

# Define the ccf power of the others
KDict.add('KW_TELLUP_CCFP_OTHERS', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the ccf power of the '
                       'others'))

# Define whether precleaning was done (tellu pre-cleaning)
KDict.add('KW_TELLUP_DO_PRECLEAN', key='NULL', dtype=bool,
          source=__NAME__,
          description=('Define whether precleaning was '
                       'done (tellu pre-cleaning)'))

# Define whether finite correction was done (tellu pre-cleaning)
KDict.add('KW_TELLUP_DO_FINITE_RES', key='NULL',
          dtype=bool, source=__NAME__,
          description='Define whether finite '
                      'correction was done '
                      '(tellu pre-cleaning)')

# Define default water absorption used (tellu pre-cleaning)
KDict.add('KW_TELLUP_DFLT_WATER', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define default water absorption '
                       'used (tellu pre-cleaning)'))

# Define ccf scan range that was used (tellu pre-cleaning)
KDict.add('KW_TELLUP_CCF_SRANGE', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define ccf scan range that was '
                       'used (tellu pre-cleaning)'))

# Define whether we cleaned OH lines
KDict.add('KW_TELLUP_CLEAN_OHLINES', key='NULL', dtype=float,
          source=__NAME__)

# Define which orders were removed from tellu pre-cleaning
KDict.add('KW_TELLUP_REMOVE_ORDS', key='NULL', dtype=str,
          source=__NAME__,
          description=('Define which orders were removed '
                       'from tellu pre-cleaning'))

# Define which min snr threshold was used for tellu pre-cleaning
KDict.add('KW_TELLUP_SNR_MIN_THRES', key='NULL',
          dtype=float, source=__NAME__,
          description=('Define which min snr threshold '
                       'was used for tellu '
                       'pre-cleaning'))

# Define dexpo convergence threshold used
KDict.add('KW_TELLUP_DEXPO_CONV_THRES', key='NULL',
          dtype=float, source=__NAME__,
          description=('Define dexpo convergence '
                       'threshold used'))

# Define the maximum number of operations used to get dexpo convergence
KDict.add('KW_TELLUP_DEXPO_MAX_ITR', key='NULL',
          dtype=int, source=__NAME__,
          description=('Define the maximum number of '
                       'operations used to get dexpo '
                       'convergence'))

# Define the kernel threshold in abso_expo used in tellu pre-cleaning
KDict.add('KW_TELLUP_ABSOEXPO_KTHRES', key='NULL',
          dtype=int, source=__NAME__,
          description=('Define the kernel threshold '
                       'in abso_expo used in tellu '
                       'pre-cleaning'))

# Define the wave start (same as s1d) in nm used
KDict.add('KW_TELLUP_WAVE_START', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the wave start (same as '
                       's1d) in nm used'))

# Define the wave end (same as s1d) in nm used
KDict.add('KW_TELLUP_WAVE_END', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the wave end (same as s1d) '
                       'in nm used'))

# Define the dv wave grid (same as s1d) in km/s used
KDict.add('KW_TELLUP_DVGRID', key='NULL', dtype=float,
          source=__NAME__,
          description=('Define the dv wave grid (same as s1d) '
                       'in km/s used'))

# Define the gauss width of the kernel used in abso_expo for tellu pre-cleaning
KDict.add('KW_TELLUP_ABSOEXPO_KWID', key='NULL',
          dtype=float, source=__NAME__,
          description=(
              'Define the gauss width of the kernel '
              'used in abso_expo for tellu '
              'pre-cleaning'))

# Define the gauss shape of the kernel used in abso_expo for tellu pre-cleaning
KDict.add('KW_TELLUP_ABSOEXPO_KEXP', key='NULL',
          dtype=float, source=__NAME__,
          description=(
              'Define the gauss shape of the kernel '
              'used in abso_expo for tellu '
              'pre-cleaning'))

# Define the exponent of the transmission threshold used for tellu pre-cleaning
KDict.add('KW_TELLUP_TRANS_THRES', key='NULL',
          dtype=float, source=__NAME__,
          description=(
              'Define the exponent of the transmission '
              'threshold used for tellu pre-cleaning'))

# Define the threshold for discrepant tramission used for tellu pre-cleaning
KDict.add('KW_TELLUP_TRANS_SIGL', key='NULL',
          dtype=float, source=__NAME__,
          description=(
              'Define the threshold for discrepant '
              'tramission used for tellu pre-cleaning'))

# Define the whether to force fit to header airmass used for tellu pre-cleaning
KDict.add('KW_TELLUP_FORCE_AIRMASS', key='NULL',
          dtype=bool, source=__NAME__,
          description=(
              'Define the whether to force fit to '
              'header airmass used for tellu '
              'pre-cleaning'))

# Define the bounds of the exponent of other species used for tellu pre-cleaning
KDict.add('KW_TELLUP_OTHER_BOUNDS', key='NULL',
          dtype=str, source=__NAME__,
          description=(
              'Define the bounds of the exponent of '
              'other species used for tellu '
              'pre-cleaning'))

# Define the bounds of the exponent of water used for tellu pre-cleaning
KDict.add('KW_TELLUP_WATER_BOUNDS', key='NULL',
          dtype=str, source=__NAME__,
          description=('Define the bounds of the '
                       'exponent of water used for '
                       'tellu pre-cleaning'))

# -----------------------------------------------------------------------------
# Define make telluric variables
# -----------------------------------------------------------------------------
# The template file used for mktellu calculation
KDict.add('KW_MKTELL_TEMP_FILE', key='NULL', dtype=str,
          source=__NAME__,
          description=('The template file used for '
                       'mktellu calculation'))

# the number of template files used
KDict.add('KW_MKTELL_TEMPNUM', key='NULL', dtype=str,
          source=__NAME__,
          description='the number of template files used')

# the hash for the template generation (unique)
KDict.add('KW_MKTELL_TEMPHASH', key='NULL', dtype=str,
          source=__NAME__,
          description=('the hash for the template '
                       'generation (unique)'))

# the time the template was generated
KDict.add('KW_MKTELL_TEMPTIME', key='NULL', dtype=str,
          source=__NAME__,
          description=('the time the template was '
                       'generated'))

# The blaze percentile used for mktellu calculation
KDict.add('KW_MKTELL_BLAZE_PRCT', key='NULL', dtype=float,
          source=__NAME__,
          description=('The blaze percentile used for '
                       'mktellu calculation'))

# The blaze normalization cut used for mktellu calculation
KDict.add('KW_MKTELL_BLAZE_CUT', key='NULL', dtype=float,
          source=__NAME__,
          description=('The blaze normalization cut used '
                       'for mktellu calculation'))

# The default convolution width in pix used for mktellu calculation
KDict.add('KW_MKTELL_DEF_CONV_WID', key='NULL', dtype=int,
          source=__NAME__,
          description=('The default convolution width '
                       'in pix used for mktellu '
                       'calculation'))

# The median filter width used for mktellu calculation
KDict.add('KW_MKTELL_TEMP_MEDFILT', key='NULL', dtype=float,
          source=__NAME__,
          description=('The median filter width used '
                       'for mktellu calculation'))

# The recovered airmass value calculated in mktellu calculation
KDict.add('KW_MKTELL_AIRMASS', key='NULL', dtype=float,
          source=__NAME__,
          description=('The recovered airmass value '
                       'calculated in mktellu calculation'))

# The recovered water optical depth calculated in mktellu calculation
KDict.add('KW_MKTELL_WATER', key='NULL', dtype=float,
          source=__NAME__,
          description=('The recovered water optical depth '
                       'calculated in mktellu calculation'))

# The min transmission requirement used for mktellu/ftellu
KDict.add('KW_MKTELL_THRES_TFIT', key='NULL', dtype=float,
          source=__NAME__,
          description=('The min transmission requirement '
                       'used for mktellu/ftellu'))

# The upper limit for trans fit used in mktellu/ftellu
KDict.add('KW_MKTELL_TRANS_FIT_UPPER_BAD',
          key='NULL', dtype=float, source=__NAME__,
          description=('The upper limit for '
                       'trans fit used in '
                       'mktellu/ftellu'))

# The number of files used in the trans file model
KDict.add('KW_MKMODEL_NFILES', key='NULL', dtype=int,
          source=__NAME__,
          description='The number of files used in the trans '
                      'file model')

# The min number of files in the trans file model
KDict.add('KW_MKMODEL_MIN_FILES', key='NULL', dtype=int,
          source=__NAME__,
          description='The min number of files in the trans '
                      'file model')

# The sigma cut for the trans file model
KDict.add('KW_MKMODEL_SIGCUT', key='NULL', dtype=float,
          source=__NAME__,
          description='The sigma cut for the trans file '
                      'model')

# -----------------------------------------------------------------------------
# Define fit telluric variables
# -----------------------------------------------------------------------------
# The number of principle components used
KDict.add('KW_FTELLU_NPC', key='NULL', dtype=int, source=__NAME__,
          description='The number of principle components used')

# The number of trans files used in pc fit (closest in expo H2O/others)
KDict.add('KW_FTELLU_NTRANS', key='NULL', dtype=int,
          source=__NAME__,
          description=('The number of trans files used in pc '
                       'fit (closest in expo H2O/others)'))

# whether we added first derivative to principal components
KDict.add('KW_FTELLU_ADD_DPC', key='NULL', dtype=bool,
          source=__NAME__,
          description=('whether we added first derivative to '
                       'principal components'))

# whether we fitted the derivatives of the principal components
KDict.add('KW_FTELLU_FIT_DPC', key='NULL', dtype=bool,
          source=__NAME__,
          description=('whether we fitted the derivatives of '
                       'the principal components'))

# The source of the loaded absorption (npy file or trans_file from database)
KDict.add('KW_FTELLU_ABSO_SRC', key='NULL', dtype=str,
          source=__NAME__,
          description=('The source of the loaded absorption '
                       '(npy file or trans_file from '
                       'database)'))

# The prefix for molecular
KDict.add('KW_FTELLU_ABSO_PREFIX', key='NULL', dtype=float,
          source=__NAME__,
          description='The prefix for molecular')

# Number of good pixels requirement used
KDict.add('KW_FTELLU_FIT_KEEP_NUM', key='NULL', dtype=int,
          source=__NAME__,
          description=('Number of good pixels '
                       'requirement used'))

# The minimum transmission used
KDict.add('KW_FTELLU_FIT_MIN_TRANS', key='NULL',
          dtype=float, source=__NAME__,
          description='The minimum transmission used')

# The minimum wavelength used
KDict.add('KW_FTELLU_LAMBDA_MIN', key='NULL', dtype=float,
          source=__NAME__,
          description='The minimum wavelength used')

# The maximum wavelength used
KDict.add('KW_FTELLU_LAMBDA_MAX', key='NULL', dtype=float,
          source=__NAME__,
          description='The maximum wavelength used')

# The smoothing kernel size [km/s] used
KDict.add('KW_FTELLU_KERN_VSINI', key='NULL', dtype=float,
          source=__NAME__,
          description=('The smoothing kernel size '
                       '[km/s] used'))

# The image pixel size used
KDict.add('KW_FTELLU_IM_PX_SIZE', key='NULL', dtype=float,
          source=__NAME__,
          description='The image pixel size used')

# the number of iterations used to fit
KDict.add('KW_FTELLU_FIT_ITERS', key='NULL', dtype=int,
          source=__NAME__,
          description=('the number of iterations used '
                       'to fit'))

# the log limit in minimum absorption used
KDict.add('KW_FTELLU_RECON_LIM', key='NULL', dtype=float,
          source=__NAME__,
          description=('the log limit in minimum '
                       'absorption used'))

# the template that was used (or None if not used)
KDict.add('KW_FTELLU_TEMPLATE', key='NULL', dtype=str,
          source=__NAME__,
          description=('the template that was used (or '
                       'None if not used)'))

# the number of template files used
KDict.add('KW_FTELLU_TEMPNUM', key='NULL', dtype=int,
          source=__NAME__,
          description='the number of template files used')

# the hash for the template generation (unique)
KDict.add('KW_FTELLU_TEMPHASH', key='NULL', dtype=str,
          source=__NAME__,
          description=('the hash for the template '
                       'generation (unique)'))

# the hash for the template generation (unique)
KDict.add('KW_FTELLU_TEMPTIME', key='NULL', dtype=str,
          source=__NAME__,
          description=('the hash for the template '
                       'generation (unique)'))

# Telluric principle component amplitudes (for use with 1D list)
KDict.add('KW_FTELLU_AMP_PC', key='NULL', dtype=float,
          source=__NAME__,
          description=('Telluric principle component '
                       'amplitudes (for use with 1D list)'))

# Telluric principle component first derivative
KDict.add('KW_FTELLU_DVTELL1', key='NULL', dtype=float,
          source=__NAME__,
          description=('Telluric principle component '
                       'first derivative'))

# Telluric principle component second derivative
KDict.add('KW_FTELLU_DVTELL2', key='NULL', dtype=float,
          source=__NAME__,
          description=('Telluric principle component '
                       'second derivative'))

# Tau Water depth calculated in fit tellu
KDict.add('KW_FTELLU_TAU_H2O', key='NULL', dtype=float,
          source=__NAME__,
          description=('Tau Water depth calculated in '
                       'fit tellu'))

# Tau Rest depth calculated in fit tellu
KDict.add('KW_FTELLU_TAU_REST', key='NULL', dtype=float,
          source=__NAME__,
          description=('Tau Rest depth calculated in '
                       'fit tellu'))

# -----------------------------------------------------------------------------
# Define make template variables
# -----------------------------------------------------------------------------
# store the number of files we had to create template
KDict.add('KW_MKTEMP_NFILES', key='NULL', dtype=int,
          source=__NAME__,
          description=('store the number of files we had to '
                       'create template'))

# store the number of files used to create template
KDict.add('KW_MKTEMP_NFILES_USED', key='NULL', dtype=int,
          source=__NAME__,
          description=('store the number of files used '
                       'to create template'))

# store a unique hash for this template (based on file name etc)
KDict.add('KW_MKTEMP_HASH', key='NULL', dtype=str,
          source=__NAME__,
          description=('store a unique hash for this template '
                       '(based on file name etc)'))

# store time template was created
KDict.add('KW_MKTEMP_TIME', key='NULL', dtype=float,
          source=__NAME__,
          description='store time template was created')

# the snr order used for quality control cut in make template calculation
KDict.add('KW_MKTEMP_SNR_ORDER', key='NULL', dtype=int,
          source=__NAME__,
          description=('the snr order used for quality '
                       'control cut in make template calculation'))

# the snr threshold used for quality control cut in make template calculation
KDict.add('KW_MKTEMP_SNR_THRES', key='NULL', dtype=float,
          source=__NAME__,
          description=(
              'the snr threshold used for quality control '
              'cut in make template calculation'))

# the berv coverage calculated for this template calculation
KDict.add('KW_MKTEMP_BERV_COV', key='NULL', dtype=float,
          source=__NAME__,
          description=('the berv coverage calculated for '
                       'this template calculation'))

# the minimum berv coverage allowed for this template calculation
KDict.add('KW_MKTEMP_BERV_COV_MIN', key='NULL', dtype=float,
          source=__NAME__,
          description=('the minimum berv coverage '
                       'allowed for this template '
                       'calculation'))

# the core snr used for this template calculation
KDict.add('KW_MKTEMP_BERV_COV_SNR', key='NULL', dtype=float,
          source=__NAME__,
          description=('the core snr used for this '
                       'template calculation'))

# the resolution used for this template calculation
KDict.add('KW_MKTEMP_BERV_COV_RES', key='NULL', dtype=float,
          source=__NAME__,
          description=('the resolution used for this '
                       'template calculation'))

# -----------------------------------------------------------------------------
# Define ccf variables
# -----------------------------------------------------------------------------
# type of ccf fit (aborption or emission)
KDict.add('KW_CCF_FIT_TYPE', key='NULL', dtype=str,
          source=__NAME__,
          description='type of ccf fit (aborption or '
                      'emission)')

# The rv calculated from the ccf stack
KDict.add('KW_CCF_STACK_RV', key='NULL', dtype=float,
          source=__NAME__,
          description='The rv calculated from the ccf '
                      'stack')

# the constrast (depth of fit ccf) from the ccf stack
KDict.add('KW_CCF_STACK_CONTRAST', key='NULL',
          dtype=float, source=__NAME__,
          description=('the constrast (depth of '
                       'fit ccf) from the ccf stack'))

# the fwhm from the ccf stack
KDict.add('KW_CCF_STACK_FWHM', key='NULL', dtype=float,
          source=__NAME__,
          description='the fwhm from the ccf stack')

# the bisector span from the ccf stack
KDict.add('KW_CCF_BISECTOR', key='NULL', dtype=float,
          source=__NAME__,
          description='the bisector span from the ccf stack')

# the bisector span values (Top to bottom)
KDict.add('KW_CCF_BIS_SPAN', key='NULL', dtype=str,
          source=__NAME__,
          description='the bisector span values (Top to '
                      'bottom)')

# the total number of mask lines used in all ccfs
KDict.add('KW_CCF_TOT_LINES', key='NULL', dtype=int,
          source=__NAME__,
          description=('the total number of mask lines '
                       'used in all ccfs'))

# The SNR of the CCF stack
KDict.add('KW_CCF_SNR_STACK', key='NULL', dtype=float,
          source=__NAME__,
          description='The SNR of the CCF stack')

# The normalization coefficient of the CCF stack
KDict.add('KW_CCF_NORM_STACK', key='NULL', dtype=float,
          source=__NAME__,
          description='The normalization coeffcient of the '
                      'CCF stack')

# the ccf mask file used
KDict.add('KW_CCF_MASK', key='NULL', dtype=str, source=__NAME__,
          description='the ccf mask file used')

# the ccf step used (in km/s)
KDict.add('KW_CCF_STEP', key='NULL', dtype=float, source=__NAME__,
          description='the ccf step used (in km/s)')

# the width of the ccf used (in km/s)
KDict.add('KW_CCF_WIDTH', key='NULL', dtype=float, source=__NAME__,
          description='the width of the ccf used (in km/s)')

# the central rv used (in km/s) rv elements run from rv +/- width in the ccf
KDict.add('KW_CCF_TARGET_RV', key='NULL', dtype=float,
          source=__NAME__,
          description=('the central rv used (in km/s) rv '
                       'elements run from rv +/- width in '
                       'the ccf'))

# the read noise used in the photon noise uncertainty calculation in the ccf
KDict.add('KW_CCF_SIGDET', key='NULL', dtype=float, source=__NAME__,
          description=('the read noise used in the photon noise '
                       'uncertainty calculation in the ccf'))

# the size in pixels around saturated pixels to regard as bad pixels used in
#    the ccf photon noise calculation
KDict.add('KW_CCF_BOXSIZE', key='NULL', dtype=int, source=__NAME__,
          description=(
              'the size in pixels around saturated pixels to '
              'regard as bad pixels used in the ccf photon '
              'noise calculation'))

# the upper limit for good pixels (above this are bad) used in the ccf photon
#   noise calculation
KDict.add('KW_CCF_MAXFLUX', key='NULL', dtype=float, source=__NAME__,
          description=(
              'the upper limit for good pixels (above this are '
              'bad) used in the ccf photon noise calculation'))

# The last order used in the mean CCF (from 0 to nmax are used)
KDict.add('KW_CCF_NMAX', key='NULL', dtype=int, source=__NAME__,
          description=('The last order used in the mean CCF (from '
                       '0 to nmax are used)'))

# the minimum weight of a line in the CCF MASK used
KDict.add('KW_CCF_MASK_MIN', key='NULL', dtype=float,
          source=__NAME__,
          description=('the minimum weight of a line in the '
                       'CCF MASK used'))

# the mask width of lines in the CCF Mask used
KDict.add('KW_CCF_MASK_WID', key='NULL', dtype=float,
          source=__NAME__,
          description=('the mask width of lines in the CCF '
                       'Mask used'))

# the wavelength units used in the CCF Mask for line centers
KDict.add('KW_CCF_MASK_UNITS', key='NULL', dtype=str,
          source=__NAME__,
          description=('the wavelength units used in the '
                       'CCF Mask for line centers'))

# the dv rms calculated for spectrum [m/s]
KDict.add('KW_CCF_DVRMS_SP', key='NULL', dtype=float,
          source=__NAME__,
          description=('the dv rms calculated for spectrum '
                       '[m/s]'))

# the dev rms calculated during the CCF [m/s]
KDict.add('KW_CCF_DVRMS_CC', key='NULL', dtype=float,
          source=__NAME__,
          description=('the dev rms calculated during the '
                       'CCF [m/s]'))

# The radial velocity measured from the wave solution FP CCF
KDict.add('KW_CCF_RV_WAVE_FP', key='NULL', dtype=float,
          source=__NAME__,
          description=('The radial velocity measured from '
                       'the wave solution FP CCF'))

# The radial velocity measured from a simultaneous FP CCF
#     (FP in reference channel)
KDict.add('KW_CCF_RV_SIMU_FP', key='NULL', dtype=float,
          source=__NAME__,
          description=(
              'The radial velocity measured from a '
              'simultaneous FP CCF (FP in reference '
              'channel)'))

# The radial velocity drift between wave sol FP and simultaneous FP (if present)
#   if simulataneous FP not present this is just the wave solution FP CCF value
KDict.add('KW_CCF_RV_DRIFT', key='NULL', dtype=float,
          source=__NAME__,
          description=(
              'The radial velocity drift between wave sol '
              'FP and simultaneous FP (if present) if '
              'simulataneous FP not present this is just the '
              'wave solution FP CCF value'))

# The radial velocity measured from the object CCF against the CCF MASK
KDict.add('KW_CCF_RV_OBJ', key='NULL', dtype=float, source=__NAME__,
          description=('The radial velocity measured from the '
                       'object CCF against the CCF MASK'))

# the corrected radial velocity of the object (taking into account the FP RVs)
KDict.add('KW_CCF_RV_CORR', key='NULL', dtype=float, source=__NAME__,
          description=('the corrected radial velocity of the '
                       'object (taking into account the '
                       'FP RVs)'))

# the wave file used for the rv (fiber specific)
KDict.add('KW_CCF_RV_WAVEFILE', key='NULL', dtype=str,
          source=__NAME__,
          description=('the wave file used for the rv '
                       '(fiber specific)'))

# the wave file time used for the rv [mjd] (fiber specific)
KDict.add('KW_CCF_RV_WAVETIME', key='NULL', dtype=str,
          source=__NAME__,
          description=('the wave file time used for the '
                       'rv [mjd] (fiber specific)'))

# the time diff (in days) between wave file and file (fiber specific)
KDict.add('KW_CCF_RV_TIMEDIFF', key='NULL', dtype=str,
          source=__NAME__,
          description=('the time diff (in days) between '
                       'wave file and file '
                       '(fiber specific)'))

# the wave file source used for the rv reference fiber
KDict.add('KW_CCF_RV_WAVESRCE', key='NULL', dtype=str,
          source=__NAME__,
          description=('the wave file source used for '
                       'the rv reference fiber'))

# -----------------------------------------------------------------------------
# Define polar variables
# -----------------------------------------------------------------------------
# define the Elapsed time of observation (sec)
KDict.add('KW_POL_ELAPTIME', key='NULL', dtype=float,
          source=__NAME__,
          description=('define the Elapsed time of '
                       'observation (sec)'))

# define the MJD at center of observation
KDict.add('KW_POL_MJDCEN', key='NULL', dtype=float, source=__NAME__,
          description='define the MJD at center of observation')

# define the BJD at center of observation
KDict.add('KW_POL_BJDCEN', key='NULL', dtype=float, source=__NAME__,
          description='define the BJD at center of observation')

# define the BERV at center of observation
KDict.add('KW_POL_BERVCEN', key='NULL', dtype=float, source=__NAME__,
          description=('define the BERV at center of '
                       'observation'))

# define the Mean BJD for polar sequence
KDict.add('KW_POL_MEAN_MJD', key='NULL', dtype=float,
          source=__NAME__,
          description=('define the Mean MJD for polar '
                       'sequence'))

# define the Mean BJD for polar sequence
KDict.add('KW_POL_MEAN_BJD', key='NULL', dtype=float,
          source=__NAME__,
          description=('define the Mean BJD for polar '
                       'sequence'))

# define the mean BERV of the exposures
KDict.add('KW_POL_MEAN_BERV', key='NULL', dtype=float,
          source=__NAME__,
          description=('define the mean BERV of the '
                       'exposures'))

# define the Stokes paremeter: Q, U, V, or I
KDict.add('KW_POL_STOKES', key='NULL', dtype=str, source=__NAME__,
          description=('define the Stokes paremeter: '
                       'Q, U, V, or I'))

# define Number of exposures for polarimetry
KDict.add('KW_POL_NEXP', key='NULL', dtype=int, source=__NAME__,
          description=('define Number of exposures for '
                       'polarimetry'))

# defines the Polarimetry method
KDict.add('KW_POL_METHOD', key='NULL', dtype=str, source=__NAME__,
          description='defines the Polarimetry method')

# define the Total exposure time (sec)
KDict.add('KW_POL_EXPTIME', key='NULL', dtype=float, source=__NAME__,
          description='define the Total exposure time (sec)')

# define the MJD at flux-weighted center of 4 exposures
KDict.add('KW_POL_MJD_FW_CEN', key='NULL', dtype=float,
          source=__NAME__,
          description='define the MJD at flux-weighted '
                      'center of 4 exposures')

# define the BJD at flux-weighted center of 4 exposures
KDict.add('KW_POL_BJD_FW_CEN', key='NULL', dtype=float,
          source=__NAME__,
          description='define the BJD at flux-weighted '
                      'center of 4 exposures')

# define whether we corrected for BERV
KDict.add('KW_POL_CORR_BERV', key='NULL', dtype=bool,
          source=__NAME__,
          description='define whether we corrected for BERV')

# define whether we corrected for source RV
KDict.add('KW_POL_CORR_SRV', key='NULL', dtype=bool,
          source=__NAME__,
          description='define whether we corrected for '
                      'source RV')

# define whether we normalized stokes I by continuum
KDict.add('KW_POL_NORM_STOKESI', key='NULL', dtype=bool,
          source=__NAME__,
          description='define whether we normalized stokes'
                      ' I by continuum')

# define whether we normalized stokes I by continuum
KDict.add('KW_POL_INTERP_FLUX', key='NULL', dtype=bool,
          source=__NAME__,
          description='define whether we normalized stokes '
                      'I by continuum')

# define whether we apply polarimetric sigma-clip cleaning
KDict.add('KW_POL_SIGCLIP', key='NULL', dtype=bool,
          source=__NAME__,
          description='define whether we apply polarimetric '
                      'sigma-clip cleaning')

# define the number of sigma swithin which to apply sigma clipping
KDict.add('KW_POL_NSIGMA', key='NULL', dtype=int,
          source=__NAME__,
          description='define the number of sigma swithin which '
                      'to apply sigma clipping')

# define whether we removed continuum polarization
KDict.add('KW_POL_REMOVE_CONT', key='NULL', dtype=int,
          source=__NAME__,
          description='define whether we removed continuum '
                      'polarization')

# define the stokes I continuum detection algorithm
KDict.add('KW_POL_SCONT_DET_ALG', key='NULL', dtype=str,
          source=__NAME__,
          description='define the stokes I continuum '
                      'detection algorithm')

# define the polar continuum detection algorithm
KDict.add('KW_POL_PCONT_DET_ALG', key='NULL', dtype=str,
          source=__NAME__,
          description='define the polar continuum '
                      'detection algorithm')

# define whether we used polynomial fit for continuum polarization
KDict.add('KW_POL_CONT_POLYFIT', key='NULL', dtype=bool,
          source=__NAME__,
          description='define whether we used polynomial '
                      'fit for continuum polarization')

# define polynomial degree of fit continuum polarization
KDict.add('KW_POL_CONT_DEG_POLY', key='NULL', dtype=int,
          source=__NAME__,
          description='define polynomial degree of fit '
                      'continuum polarization')

# define the iraf function that was used to fit stokes I continuum
KDict.add('KW_POL_S_IRAF_FUNC', key='NULL', dtype=str,
          source=__NAME__,
          description='define the iraf function that '
                      'was used to fit stokes I continuum')

# define the iraf function that was used to fit polar continuum
KDict.add('KW_POL_P_IRAF_FUNC', key='NULL', dtype=str,
          source=__NAME__,
          description='define the iraf function that was '
                      'used to fit polar continuum')

# define the degree of the polynomial used to fit stokes I continuum
KDict.add('KW_POL_S_IRAF_DEGREE', key='NULL', dtype=int,
          source=__NAME__,
          description='define the degree of the '
                      'polynomial used to fit stokes '
                      'I continuum')

# define the degree of the polynomial used to fit polar continuum
KDict.add('KW_POL_P_IRAF_DEGREE', key='NULL', dtype=int,
          source=__NAME__,
          description='define the degree of the '
                      'polynomial used to fit polar '
                      'continuum')

# define the polar continuum bin size used
KDict.add('KW_POL_CONT_BINSIZE', key='NULL', dtype=int,
          source=__NAME__,
          description='define the polar continuum bin '
                      'size used')

# define the polar continuum overlap size used
KDict.add('KW_POL_CONT_OVERLAP', key='NULL', dtype=int,
          source=__NAME__,
          description='define the polar continuum overlap '
                      'size used')

# define the telluric mask parameters (1D list)
KDict.add('KW_POL_CONT_TELLMASK', key='NULL', dtype=str,
          source=__NAME__,
          description='define the telluric mask '
                      'parameters (1D list)')

# define the lsd origin
KDict.add('KW_LSD_ORIGIN', key='NULL', dtype=str,
          source=__NAME__,
          description='define the lsd origin')

# define the rv from lsd gaussian fit
KDict.add('KW_LSD_FIT_RV', key='NULL', dtype=float,
          source=__NAME__,
          description='define the rv from lsd gaussian fit')

# define the mean degree of polarization
KDict.add('KW_LSD_POL_MEAN', key='NULL', dtype=float,
          source=__NAME__,
          description='define the mean degree of polarization')

# define the std deviation of degree of polarization
KDict.add('KW_LSD_POL_STDDEV', key='NULL', dtype=float,
          source=__NAME__,
          description='define the std deviation of degree of '
                      'polarization')

# define the median degree of polarization
KDict.add('KW_LSD_POL_MEDIAN', key='NULL', dtype=float,
          source=__NAME__,
          description='define the median degree of '
                      'polarization')

# define the median deviations of degree of polarization
KDict.add('KW_LSD_POL_MEDABSDEV', key='NULL', dtype=float,
          source=__NAME__,
          description='define the median deviations of '
                      'degree of polarization')

# define the mean of stokes VQU lsd profile
KDict.add('KW_LSD_STOKESVQU_MEAN', key='NULL', dtype=float,
          source=__NAME__,
          description='define the mean of stokes VQU '
                      'lsd profile')

# define the std deviation of stokes VQU LSD profile
KDict.add('KW_LSD_STOKESVQU_STDDEV', key='NULL',
          dtype=float, source=__NAME__,
          description='define the std deviation of '
                      'stokes VQU LSD profile')

# define the mean of stokes VQU LSD null profile
KDict.add('KW_LSD_NULL_MEAN', key='NULL', dtype=float,
          source=__NAME__,
          description='define the mean of stokes VQU LSD '
                      'null profile')

# define the std deviation of stokes vqu lsd null profile
KDict.add('KW_LSD_NULL_STDDEV', key='NULL', dtype=float,
          source=__NAME__,
          description='define the std deviation of stokes '
                      'vqu lsd null profile')

# define the mask file used in the lsd analysis
KDict.add('KW_LSD_MASK_FILE', key='NULL', dtype=str,
          source=__NAME__,
          description='define the mask file used in the '
                      'lsd analysis')

# define the number of lines in the original mask
KDict.add('KW_LSD_MASK_NUMLINES', key='NULL', dtype=int,
          source=__NAME__,
          description='define the number of lines in '
                      'the original mask')

# define the number of lines used in the LSD analysis
KDict.add('KW_LSD_MASKLINES_USED', key='NULL', dtype=int,
          source=__NAME__,
          description='define the number of lines used '
                      'in the LSD analysis')

# define the mean wavelength of lines use din lsd analysis
KDict.add('KW_LSD_NORM_WLC', key='NULL', dtype=float,
          source=__NAME__,
          description='define the mean wavelength of '
                      'lines use din lsd analysis')

# define the mean lande of lines used in lsd analysis
KDict.add('KW_LSD_NORM_LANDE', key='NULL',
          dtype=float, source=__NAME__,
          description='define the mean lande of lines used '
                      'in lsd analysis')

# define the depth used in lsd analysis
KDict.add('KW_LSD_NORM_DEPTH', key='NULL',
          dtype=float, source=__NAME__,
          description='define the depth used in lsd analysis')

# define the calculate normalisation of the weights used in the lsd analysis
KDict.add('KW_LSD_NORM_WEIGHT', key='NULL',
          dtype=float, source=__NAME__,
          description='define the calculate normalisation '
                      'of the weights used in the lsd '
                      'analysis')

# =============================================================================
#  End of configuration file
# =============================================================================
