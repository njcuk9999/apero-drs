"""
Default keywords for NIRPS HE

Created on 2019-01-17

@author: cook
"""
from astropy import units as uu

from apero.base import base
from apero.core.instruments.default import keywords

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero.core.instruments.nirps_ha.keywords.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__author__ = base.__author__
__date__ = base.__date__
__release__ = base.__release__
# copy the storage
KDict = keywords.KDict.copy(source=__NAME__)

# -----------------------------------------------------------------------------
# Required header keys (main fits file)
# -----------------------------------------------------------------------------
# Define the header key that uniquely identifies the file
#     (i.e. an odometer code)
KDict.set('KW_IDENTIFIER', key='ARCFILE',
          comment='filename anticipated by fitspipe server',
          group='raw')

# define the MJ date HEADER key (only used for logging)
KDict.set('KW_MJDATE', key='MJD-OBS', datatype='mjd', dataformat=float,
          comment='Observation Start (Modified Julian Date)',
          combine_method='minimum', group='raw')

# define the observation date HEADER key
KDict.set('KW_DATE_OBS', key='DATE-OBS', datatype='fits', dataformat=str,
          comment='Observation Start (YYYY-MM-DDThh:mm:ss UTC)',
          group='raw')

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KDict.set('KW_RDNOISE', key='HIERARCH ESO DET OUT1 RON',
          comment='Read noise (electrons)', combine_method='flux',
          group='raw')

# define the gain HEADER key (used to get value only)
# TODO: was HIERARCH ESO DET CHIP1 GAIN
KDict.set('KW_GAIN', key='HIERARCH ESO DET OUT1 CONAD',
          comment='[adu/e-] Conversion electrons to ADU',
          combine_method='mean', group='raw')

# define the exposure time HEADER key (used to get value only)
KDict.set('KW_EXPTIME', key='EXPTIME', unit=uu.s,
          comment='[sec] Integration time',
          combine_method='math', group='raw')

# define the required exposure time HEADER key (used to get value only)
# NIRPS-CHANGE: Do we have this for NIRPS?
# TODO: For now set this to the actual exposure time
KDict.set('KW_EXPREQ', key='EXPTIME', unit=uu.s,
          comment='[sec] Requested integration time',
          combine_method='math', group='raw')

# define the observation type HEADER key
KDict.set('KW_OBSTYPE', key='HIERARCH ESO DPR TYPE',
          comment='Observation / Exposure type', group='raw')

# define the science fiber type HEADER key
# KW_CCAS = KW_CCAS.copy(__NAME__)
# KW_CCAS.set(key='SBCCAS_P',
#             comment='SPIRou Cassegrain Fiber Position (predefined)',
#             group='raw')

# define the reference fiber type HEADER key
# KW_CREF = KW_CREF.copy(__NAME__)
# KW_CREF.set(key='SBCREF_P',
#             comment='SPIRou Reference Fiber Position (predefined)',
#             group='raw')

# define the calibration wheel position
# KW_CALIBWH = KW_CALIBWH.copy(__NAME__)
# KW_CALIBWH.set(key='SBCALI_P',
#                comment='SPIRou calibwh predefined position or angle',
#                group='raw')

# define the target type (object/sky)
KDict.set('KW_TARGET_TYPE', key='TRG_TYPE', comment='target or sky object', group='raw')

# define the density HEADER key
# KW_CDEN = KW_CDEN.copy(__NAME__)
# KW_CDEN.set(key='SBCDEN_P',
#             comment='SPIRou Calib-Reference density (0 to 3.3)', group='raw')

# define polarisation HEADER key
# KW_CMMTSEQ = KW_CMMTSEQ.copy(__NAME__)
# KW_CMMTSEQ.set(key='CMMTSEQ', group='raw')

# define the exposure number within sequence HEADER key
KDict.set('KW_CMPLTEXP', key='HIERARCH ESO TPL EXPNO',
          comment='Exposure number within the exposure sequence ',
          combine_method='1', group='raw')

# define the total number of exposures HEADER key
KDict.set('KW_NEXP', key='HIERARCH ESO TPL NEXP',
          comment='Total number of exposures within the sequence',
          combine_method='1', group='raw')

# define the pi name HEADER key
KDict.set('KW_PI_NAME', key='HIERARCH ESO OBS PI-COI NAME',
          comment='The PI of the program', group='raw')

# define the run id HEADER key
KDict.set('KW_RUN_ID', key='HIERARCH ESO OBS PROG ID',
          comment='ESO program identification', group='raw')

# define the instrument HEADER key
KDict.set('KW_INSTRUMENT', key='INSTRUME', comment='Instrument Name', group='raw')

# define the instrument mode header key
KDict.set('KW_INST_MODE', key='HIERARCH ESO INS MODE', comment='Instrument mode used',
          group='raw')

# define the raw dprtype from the telescope
KDict.set('KW_RAW_DPRTYPE', key='HIERARCH ESO DPR TYPE', comment='Observation type',
          group='raw')

# define the raw dpr category
KDict.set('KW_RAW_DPRCATG', key='HIERARCH ESO DPR CATG', comment='Observation category',
          group='raw')

# -----------------------------------------------------------------------------
# Required header keys (related to science object)
# -----------------------------------------------------------------------------
# define the observation ra HEADER key
KDict.set('KW_OBJRA', key='RA', unit=uu.deg, comment='Target right ascension',
          group='raw')

# define the observation dec HEADER key
KDict.set('KW_OBJDEC', key='DEC', unit=uu.deg, comment='Target declination ',
          group='raw')

# define the observation name
KDict.set('KW_OBJECTNAME', key='OBJECT', comment='Target name', group='raw')

# define the observation name
KDict.set('KW_OBJECTNAME2', key='HIERARCH ESO OBS TARG NAME', comment='OB target name',
          group='raw')

# define the observation equinox HEADER key
KDict.set('KW_OBJEQUIN', key='EQUINOX', datatype='decimalyear',
          comment='Target equinox ', group='raw')

# define the observation proper motion in ra HEADER key
KDict.set('KW_OBJRAPM', key='OBJRAPM', unit=uu.arcsec / uu.yr,
          comment='Target right ascension proper motion in as/yr ',
          group='raw')

# define the observation proper motion in dec HEADER key
KDict.set('KW_OBJDECPM', key='OBJDECPM', unit=uu.arcsec / uu.yr,
          comment='Target declination proper motion in as/yr',
          group='raw')

# define the airmass HEADER key
KDict.set('KW_AIRMASS', key='HIERARCH ESO TEL AIRM START',
          comment='Airmass at start of observation',
          group='raw')

# define the weather tower temperature HEADER key
# KW_WEATHER_TOWER_TEMP = KW_WEATHER_TOWER_TEMP.copy(__NAME__)
# KW_WEATHER_TOWER_TEMP.set(key='TEMPERAT',
#                           comment='86 temp, air, weather tower deg C  ',
#                           group='raw')

# define the cassegrain temperature HEADER key
# KW_CASS_TEMP = KW_CASS_TEMP.copy(__NAME__)
# KW_CASS_TEMP.set(key='SB_POL_T',
#                  comment='SPIRou tpolar temp at start of exp (deg C)  ',
#                  group='raw')

# define the humidity HEADER key
# KW_HUMIDITY = KW_HUMIDITY.copy(__NAME__)
# KW_HUMIDITY.set(key='RELHUMID',
#                 comment='87 relative humidity, weather tower % ', group='raw')

# -----------------------------------------------------------------------------
# Wanted header keys (related to science object)
# -----------------------------------------------------------------------------
# define the parallax HEADER key
KDict.set('KW_PLX', key='OBJPLX', unit=uu.mas, group='raw')

# define the rv HEADER key
KDict.set('KW_INPUTRV', key='OBJRV', unit=uu.km / uu.s, group='raw')

# define the object temperature HEADER key
KDict.set('KW_OBJ_TEMP', key='OBJTEMP', unit=uu.K, group='raw')

# -----------------------------------------------------------------------------
# Keys added as early as possible
# -----------------------------------------------------------------------------
# define whether a target was observed at night
KDict.set('KW_NIGHT_OBS', key='DRS_NOBS', comment='Whether target was observed at night',
          group='raw-add')

# Define whether a target was observed during civil twilight
KDict.set('KW_CIV_TWIL', key='DRSCTWIL', group='raw-add',
          comment='Whether target was observed during civil twilight')

# Define whether a target was observed during nautical twilight
KDict.set('KW_NAU_TWIL', key='DRSNTWIL', group='raw-add',
          comment='Whether target was observed during nautical twilight')

# Define whether a target was observed during astronomical twilight
KDict.set('KW_AST_TWIL', key='DRSATWIL', group='raw-add',
          comment='Whether target was observed during astronomical '
                  'twilight')

# Define the calculated sun elevation during observation
KDict.set('KW_SUN_ELEV', key='DRSSUNEL', group='raw-add',
          comment='The calculated sun elevation during observation')

# -----------------------------------------------------------------------------
# Object resolution keys
# -----------------------------------------------------------------------------
# the object name to be used by the drs (after preprocessing)
KDict.set('KW_DRS_OBJNAME', key='PP_OBJN',
          comment='cleaned object name to be used by the DRS',
          group='resolve', post_exclude=True)

# the original name of the object name used by the drs
KDict.set('KW_DRS_OBJNAME_S', key='PP_OBJNS',
          comment='Original object name as in header',
          group='resolve', post_exclude=True)

# the right ascension to be used by the drs (after preprocessing)
KDict.set('KW_DRS_RA', key='PP_RA', unit=uu.deg,
          comment='The RA [in deg] used by the DRS',
          group='resolve', post_exclude=True)

# the source of the ra to be used by the drs (after preprocessing)
KDict.set('KW_DRS_RA_S', key='PP_RAS',
          comment='Source of the ra used by the DRS',
          group='resolve', post_exclude=True)

# the declination to be used by the drs (after preprocessing)
KDict.set('KW_DRS_DEC', key='PP_DEC', unit=uu.deg,
          comment='The dec [in deg] used by the DRS',
          group='resolve', post_exclude=True)

# the source of the dec to be used by the drs (after preprocessing)
KDict.set('KW_DRS_DEC_S', key='PP_DECS',
          comment='Source of the dec used by the DRS',
          group='resolve', post_exclude=True)

# the proper motion in ra to be used by the drs (after preprocessing)
KDict.set('KW_DRS_PMRA', key='PP_PMRA', unit=uu.mas / uu.yr,
          comment='The pmra [mas/yr] used by the DRS',
          group='resolve', post_exclude=True)

# the source of the pmra used by the drs (afer prepreocessing)
KDict.set('KW_DRS_PMRA_S', key='PP_PMRAS',
          comment='Source of the pmra used by the DRS',
          group='resolve', post_exclude=True)

# the proper motion in dec to be used by the drs (after preprocessing)
KDict.set('KW_DRS_PMDE', key='PP_PMDE', unit=uu.mas / uu.yr,
          comment='The pmdec [mas/yr] used by the DRS',
          group='resolve', post_exclude=True)

# the source of the pmde used by the drs (after preprocessing)
KDict.set('KW_DRS_PMDE_S', key='PP_PMDES',
          comment='Source of the pmde used by the DRS',
          group='resolve', post_exclude=True)

# the parallax to be used by the drs (after preprocessing)
KDict.set('KW_DRS_PLX', key='PP_PLX', unit=uu.mas,
          comment='The parallax [mas] used by the DRS',
          group='resolve', post_exclude=True)

# the source of the parallax used by the drs (after preprocessing)
KDict.set('KW_DRS_PLX_S', key='PP_PLXS',
          comment='Source of the plx used by the DRS',
          group='resolve', post_exclude=True)

# the radial velocity to be used by the drs (after preprocessing)
KDict.set('KW_DRS_RV', key='PP_RV', unit=uu.km / uu.s,
          comment='The RV [km/s] used by the DRS',
          group='resolve', post_exclude=True)

# the source of the radial velocity used by the drs (after preprocessing)
KDict.set('KW_DRS_RV_S', key='PP_RVS',
          comment='Source of the rv used by the DRS',
          group='resolve', post_exclude=True)

# the epoch to be used by the drs (after preprocessing)
KDict.set('KW_DRS_EPOCH', key='PP_EPOCH', unit=uu.yr,
          comment='The Epoch used by the DRS',
          group='resolve', post_exclude=True)

# the effective temperature to be used by the drs (after preprocessing)
KDict.set('KW_DRS_TEFF', key='PP_TEFF', unit=uu.K,
          comment='The Teff [K] used by the DRS',
          group='resolve', post_exclude=True)

# the source of teff used by the drs (after preprocessing)
KDict.set('KW_DRS_TEFF_S', key='PP_TEFFS',
          comment='Source of the Teff used by the DRS',
          group='resolve', post_exclude=True)

# the spectral type (if present) used by the drs (after preprocessing)
KDict.set('KW_DRS_SPTYPE', key='PP_SPT', unit=uu.K,
          comment='The SpT used by the DRS',
          group='resolve', post_exclude=True)

# the source of spectral type (if present) used by the drs (after preprocessing)
KDict.set('KW_DRS_SPTYPE_S', key='PP_SPTS',
          comment='Source of the SpT used by the DRS',
          group='resolve', post_exclude=True)

# The source of the DRS object data (after preprocessing)
KDict.set('KW_DRS_DSOURCE', key='PP_SRCE', unit=uu.K,
          comment='The source of DRS object data',
          group='resolve', post_exclude=True)

# The date of the source of the DRS object data (after preprocessing)
KDict.set('KW_DRS_DDATE', key='PP_DDATE', unit=uu.K,
          comment='The date of source of DRS object data',
          group='resolve', post_exclude=True)

# -----------------------------------------------------------------------------
# Define general keywords
# -----------------------------------------------------------------------------
# DRS version
KDict.set('KW_VERSION', key='VERSION', comment='APERO version', group='pp')

KDict.set('KW_PPVERSION', key='PVERSION', comment='APERO Pre-Processing version',
          group='pp')

# DRS process ID
KDict.set('KW_PID', key='DRSPID', comment='The process ID that outputted this file.',
          post_exclude=True, group='pp')

# Processed date keyword
KDict.set('KW_DRS_DATE_NOW', key='DRSPDATE', comment='DRS Processed date',
          post_exclude=True, group='pp')

# DRS version date keyword
KDict.set('KW_DRS_DATE', key='DRSVDATE', comment='DRS Release date', group='pp')

# root keys (for use below and in finding keys later)
#     - must only be 2 characters long
root_loc = 'LO'
root_flat = 'FF'
root_hc = 'HC'

# define the observation name
KDict.set('KW_OBJNAME', key='DRSOBJN', comment='APERO-cleaned Target name',
          group='ppraw')

# Define the key to get the data fits file type
KDict.set('KW_DPRTYPE', key='DPRTYPE', comment='APERO-type of file (from pre-process)',
          group='ppraw')

# Define the key to get the drs mode
KDict.set('KW_DRS_MODE', key='DRSMODE', comment='APERO-mode (HA or HE)',
          group='ppraw')

# Define the mid exposure time
# Note: must change INDEX_HEADER_KEYS data type definition if changing this
KDict.set('KW_MID_OBS_TIME', key='MJDMID',
          comment='APERO calculated Mid Observation time [mjd]',
          datatype='mjd', dataformat=float,
          combine_method='mean', group='ppraw')

# Define the method by which the MJD was calculated
KDict.set('KW_MID_OBSTIME_METHOD', key='MJDMIDMD',
          comment='Mid Observation time calc method',
          group='ppraw')

# -----------------------------------------------------------------------------
# Define DRS input keywords
# -----------------------------------------------------------------------------
# input files
KDict.set('KW_INFILE1', key='INF1{0:03d}', comment='Input file used to create output',
          post_exclude=True)
KDict.set('KW_INFILE2', key='INF2{0:03d}', comment='Input file used to create output',
          post_exclude=True)
KDict.set('KW_INFILE3', key='INF3{0:03d}', comment='Input file used to create output',
          post_exclude=True)

# -----------------------------------------------------------------------------
# Define database input keywords
# -----------------------------------------------------------------------------
# dark calibration file used
KDict.set('KW_CDBDARK', key='CDBDARK', comment='The cal DARK file for extract')
# time of dark calibration file used
KDict.set('KW_CDTDARK', key='CDTDARK', comment='MJDMID of cal DARK file used')
# bad pixel calibration file used
KDict.set('KW_CDBBAD', key='CDBBAD', comment='The cal BADPIX file for extract')
# time of bad pixel calibration file used
KDict.set('KW_CDTBAD', key='CDTBAD', comment='MJDMID of cal BADPIX file used')
# background calibration file used
KDict.set('KW_CDBBACK', key='CDBBACK', comment='The cal BKGRDMAP file for extract')
# time of background calibration file used
KDict.set('KW_CDTBACK', key='CDTBACK',
          comment='MJDMID of cal BKGRDMAP file used')
# order profile calibration file used
KDict.set('KW_CDBORDP', key='CDBORDP', comment='The cal ORDER_PROFILE file used')
# time of order profile calibration file used
KDict.set('KW_CDTORDP', key='CDTORDP', comment='MJDMID of cal ORDER_PROFILE file used')
# localisation calibration file used
KDict.set('KW_CDBLOCO', key='CDBLOCO', comment='The cal LOC file used')
# localisation calibration file used
KDict.set('KW_CDTLOCO', key='CDTLOCO', comment='MJDMID of cal LOC file used')
# shape local calibration file used
KDict.set('KW_CDBSHAPEL', key='CDBSHAPL', comment='The cal SHAPEL file used')
# time of shape local calibration file used
KDict.set('KW_CDTSHAPEL', key='CDTSHAPL', comment='MJDMID of cal SHAPEL file used')
# shape dy calibration file used
KDict.set('KW_CDBSHAPEDY', key='CDBSHAPY', comment='The cal SHAPE DX file used')
# time of shape dy calibration file used
KDict.set('KW_CDTSHAPEDY', key='CDTSHAPY', comment='MJDMID of cal SHAPE DX file used')
# shape dx calibration file used
KDict.set('KW_CDBSHAPEDX', key='CDBSHAPX', comment='The cal SHAPE DX file used')
# time of shape dx calibration file used
KDict.set('KW_CDTSHAPEDX', key='CDTSHAPX', comment='MJDMID of cal SHAPE DX file used')
# flat calibration file used
KDict.set('KW_CDBFLAT', key='CDBFLAT', comment='The cal FLAT file used')
# time of flat calibration file used
KDict.set('KW_CDBFLAT', key='CDTFLAT', comment='MJDMID of cal FLAT file used')
# blaze calibration file used
KDict.set('KW_CDBBLAZE', key='CDBBLAZE', comment='The cal BLAZE file used')
# time of blaze calibration file used
KDict.set('KW_CDTBLAZE', key='CDTBLAZE', comment='MJDMID of cal BLAZE file used')
# wave solution calibration file used
KDict.set('KW_CDBWAVE', key='CDBWAVE', comment='The cal WAVE file used')
# time of wave solution calibration file used
KDict.set('KW_CDTWAVE', key='CDTWAVE', comment='MJDMID of cal WAVE file used')
# thermal calibration file used
KDict.set('KW_CDBTHERMAL', key='CDBTHERM', comment='The cal THERMAL file used')
# time of thermal calibration file used
KDict.set('KW_CDTTHERMAL', key='CDTTHERM', comment='MJDMID of cal THERMAL file used')
# the leak reference calibration file used
KDict.set('KW_CDBLEAKM', key='CDBLEAKM', comment='The cal LEAKM file used')
# time of the leak reference calibration file used
KDict.set('KW_CDTLEAKM', key='CDTLEAKM', comment='MJDMID of cal LEAK file used')
# the ref leak reference calibration file used
KDict.set('KW_CDBLEAKR', key='CDBLEAKR', comment='The cal ref LEAKM file used')
# time of the ref leak reference calibration file used
KDict.set('KW_CDTLEAKR', key='CDTLEAKR', comment='MJDMID of cal ref LEAK file used')
# additional properties of calibration
KDict.set('KW_C_FLIP', key='CAL_FLIP', comment='Whether the image was flipped from pp')
KDict.set('KW_C_CVRTE', key='CAL_TOE', comment='Whether the flux was converted to e-')
KDict.set('KW_C_RESIZE', key='CAL_SIZE', comment='Whether the image was resized from pp')
KDict.set('KW_C_FTYPE', key='CAL_FTYP', comment='What this fiber was identified as')
KDict.set('KW_FIBER', key='FIBER', comment='The fiber name')

# define the sky model used for sky correction
KDict.set('KW_TDBSKY', key='TDTSKYCO', comment='Sky model used for sky correction')

# define the measured effective readout noise
KDict.set('KW_EFF_RON', key='EFFRON', comment='Measured eff readout noise before ext')

# -----------------------------------------------------------------------------
# Define DRS outputs keywords
# -----------------------------------------------------------------------------
# the DRS output identification code
KDict.set('KW_OUTPUT', key='DRSOUTID', comment='DRS output identification code')

# the config run file used (if given)
KDict.set('KW_CRUNFILE', key='CRUNFILE', comment='Config run file used')

# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
KDict.set('KW_DRS_QC', key='QCC_ALL', comment='All quality control passed',
          post_exclude=True)
KDict.set('KW_DRS_QC_VAL', key='QCC{0:03d}V', comment='Quality control measured value',
          post_exclude=True)
KDict.set('KW_DRS_QC_NAME', key='QCC{0:03d}N', comment='Quality control parameter name',
          post_exclude=True)
KDict.set('KW_DRS_QC_LOGIC', key='QCC{0:03d}L', comment='Quality control logic used',
          post_exclude=True)
KDict.set('KW_DRS_QC_PASS', key='QCC{0:03d}P', comment='Quality control param passed QC',
          post_exclude=True)

# -----------------------------------------------------------------------------
# Define preprocessing variables
# -----------------------------------------------------------------------------
# The shift in pixels so that image is at same location as engineering flat
KDict.set('KW_PPSHIFTX', key='DETOFFDX', comment='Pixel offset in x from readout lag',
          post_exclude=True)
# The shift in pixels so that image is at same location as engineering flat
KDict.set('KW_PPSHIFTY', key='DETOFFDY', comment='Pixel offset in y from readout lag',
          post_exclude=True)

# the number of bad pixels found via the intercept (cosmic ray rejection)
KDict.set('KW_PPC_NBAD_INTE', key='NBADINTE',
          comment='No. bad px intercept cosmic reject',
          post_exclude=True)

# the number of bad pixels found via the slope (cosmic ray rejection)
KDict.set('KW_PPC_NBAD_SLOPE', key='NBADSLOP',
          comment='No. bad px slope cosmic reject',
          post_exclude=True)

# the number of bad pixels found with both intercept and slope (cosmic ray)
KDict.set('KW_PPC_NBAD_BOTH', key='NBADBOTH',
          comment='No. bad px both cosmic reject',
          post_exclude=True)

# The number of sigma used to construct pp reference mask
KDict.set('KW_PP_REF_NSIG', key='PPMNSIG', comment='PP reference mask nsig used')

# Define the key to store the name of the pp reference file used in pp (if used)
KDict.set('KW_PP_REF_FILE', key='PPMFILE', comment='PP reference mask file used')

# Define the percentile stats for LED flat in pp (50th percentile)
KDict.set('KW_PP_LED_FLAT_P50', key='PPLEDP50', comment='LED RMS 50th percentile')

# Define the percentile stats for LED flat in pp (16th percentile)
KDict.set('KW_PP_LED_FLAT_P16', key='PPLEDP16', comment='LED RMS 16th percentile')

# Define the percentile stats for LED flat in pp (84th percentile)
KDict.set('KW_PP_LED_FLAT_P84', key='PPLEDP84', comment='LED RMS 84th percentile')

# Define the LED flat file used
KDict.set('KW_PP_LED_FLAT_FILE', key='PPLEDFIL', comment='LED flat file used')

# Define the flux-weighted mid-exposure [Expert use only]
KDict.set('KW_PP_MJD_FLUX', key='MJD_FLUX',
          comment='weighted flux in posemeter [Expert use only]')

# Define fractional RMS of posemteter [Expert use only]
KDict.set('KW_PP_RMS_POSE', key='RMS_POSE ',
          comment='RMS of flux in posemeter [Expert use only]')

# Define median flux in posemeter [Expert use only]
KDict.set('KW_PP_MED_POSE', key='MED_POSE',
          comment='Median flux in posemeter [Expert use only]')

# -----------------------------------------------------------------------------
# Define apero_dark variables
# -----------------------------------------------------------------------------
# The fraction of dead pixels in the dark (in %)
KDict.set('KW_DARK_DEAD', key='DADEAD', comment='Fraction dead pixels [%]')

# The median dark level in ADU/s
KDict.set('KW_DARK_MED', key='DAMED', comment='median dark level [ADU/s]')

# The fraction of dead pixels in the blue part of the dark (in %)
KDict.set('KW_DARK_B_DEAD', key='DABDEAD', comment='Fraction dead pixels blue part [%]')

# The median dark level in the blue part of the dark in ADU/s
KDict.set('KW_DARK_B_MED', key='DABMED', comment='median dark level blue part [ADU/s]')

# The fraction of dead pixels in the red part of the dark (in %)
KDict.set('KW_DARK_R_DEAD', key='DARDEAD', comment='Fraction dead pixels red part [%]')

# The median dark level in the red part of the dark in ADU/s
KDict.set('KW_DARK_R_MED', key='DARMED', comment='median dark level red part [ADU/s]')

# The threshold of the dark level to retain in ADU
KDict.set('KW_DARK_CUT', key='DACUT', comment='Threshold of dark level retain [ADU/s]')

# -----------------------------------------------------------------------------
# Define apero_badpix variables
# -----------------------------------------------------------------------------
# fraction of hot pixels
KDict.set('KW_BHOT', key='BHOT', comment='Frac of hot px [%]')

# fraction of bad pixels from flat
KDict.set('KW_BBFLAT', key='BBFLAT', comment='Frac of bad px from flat [%]')

# fraction of non-finite pixels in dark
KDict.set('KW_BNDARK', key='BNDARK', comment='Frac of non-finite px in dark [%]')

# fraction of non-finite pixels in flat
KDict.set('KW_BNFLAT', key='BNFLAT', comment='Frac of non-finite px in flat [%]')

# fraction of bad pixels with all criteria
KDict.set('KW_BBAD', key='BBAD', comment='Frac of bad px with all criteria [%]')

# fraction of un-illuminated pixels (from engineering flat)
KDict.set('KW_BNILUM', key='BNILUM', comment='Frac of un-illuminated pixels [%]')

# fraction of total bad pixels
KDict.set('KW_BTOT', key='BTOT', comment='Frac of bad pixels (total) [%]')

# -----------------------------------------------------------------------------
# Define localisation variables
# -----------------------------------------------------------------------------
# Mean background (as percentage)
KDict.set('KW_LOC_BCKGRD', key=root_loc + 'BCKGRD', comment='mean background [%]',
          group='loc')

# Number of orders located
KDict.set('KW_LOC_NBO', key=root_loc + 'NBO', comment='nb orders localised',
          group='loc')

# Polynomial type for localization
KDict.set('KW_LOC_POLYT', key='LOCPOLYT')

# fit degree for order centers
KDict.set('KW_LOC_DEG_C', key=root_loc + 'DEGCTR', comment='degree fit ctr ord',
          group='loc')

# fit degree for order widths
KDict.set('KW_LOC_DEG_W', key=root_loc + 'DEGFWH', comment='degree fit width ord',
          group='loc')

# Maximum flux in order
KDict.set('KW_LOC_MAXFLX', key=root_loc + 'FLXMAX', comment='max flux in order [ADU]',
          group='loc')

# Maximum number of removed points allowed for location fit
KDict.set('KW_LOC_SMAXPTS_CTR', key=root_loc + 'CTRMAX', comment='max rm pts ctr',
          group='loc')

# Maximum number of removed points allowed for width fit
KDict.set('KW_LOC_SMAXPTS_WID', key=root_loc + 'WIDMAX', comment='max rm pts width',
          group='loc')

# Maximum rms allowed for location fit
KDict.set('KW_LOC_RMS_CTR', key=root_loc + 'RMSCTR', comment='max rms ctr',
          group='loc')

# Maximum rms allowed for width fit (formally KW_LOC_rms_fwhm)
KDict.set('KW_LOC_RMS_WID', key=root_loc + 'RMSWID', comment='max rms width',
          group='loc')

# Coeff center order
KDict.set('KW_LOC_CTR_COEFF', key=root_loc + 'CE{0:04d}', comment='Coeff center',
          group='loc')

# Coeff width order
KDict.set('KW_LOC_WID_COEFF', key=root_loc + 'FW{0:04d}', comment='Coeff fwhm',
          group='loc')

# -----------------------------------------------------------------------------
# Define shape variables
# -----------------------------------------------------------------------------
# Shape transform dx parameter
KDict.set('KW_SHAPE_DX', key='SHAPE_DX', comment='Shape transform dx parameter',
          group='shape')

# Shape transform dy parameter
KDict.set('KW_SHAPE_DY', key='SHAPE_DY', comment='Shape transform dy parameter',
          group='shape')

# Shape transform A parameter
KDict.set('KW_SHAPE_A', key='SHAPE_A', comment='Shape transform A parameter',
          group='shape')

# Shape transform B parameter
KDict.set('KW_SHAPE_B', key='SHAPE_B', comment='Shape transform B parameter',
          group='shape')

# Shape transform C parameter
KDict.set('KW_SHAPE_C', key='SHAPE_C', comment='Shape transform C parameter',
          group='shape')

# Shape transform D parameter
KDict.set('KW_SHAPE_D', key='SHAPE_D', comment='Shape transform D parameter',
          group='shape')

# -----------------------------------------------------------------------------
# Define extraction variables
# -----------------------------------------------------------------------------
# The extraction type (only added for E2DS files in extraction)
KDict.set('KW_EXT_TYPE', key='EXT_TYPE', comment='Extract type (E2DS or E2DSFF)')

# SNR calculated in extraction process (per order)
KDict.set('KW_EXT_SNR', key='EXTSN{0:03d}', comment='Extract: S_N order center')

# Number of orders used in extraction process
KDict.set('KW_EXT_NBO', key='EXT_NBO', comment='Extract: Number of orders used')

# the start order for extraction
KDict.set('KW_EXT_START', key='EXTSTART', comment='Extract: Start order for extraction')

# the end order for extraction
KDict.set('KW_EXT_END', key='EXT_END', comment='Extract: End order for extraction')

# the upper bound for extraction of order
KDict.set('KW_EXT_RANGE1', key='EXTR1', comment='Extract: width1 for order extraction')

# the lower bound for extraction of order
KDict.set('KW_EXT_RANGE2', key='EXTR2', comment='Extract: width2 for order extraction')

# whether cosmics where rejected
KDict.set('KW_COSMIC', key='EXTCOS', comment='Extract: Whether cosmics were rejected')

# TODO: is blaze_size needed with sinc function?
# the blaze with used
KDict.set('KW_BLAZE_WID', key='BLAZEWID', comment='Extract: Blaze width used')

# TODO: is blaze_cut needed with sinc function?
# the blaze cut used
KDict.set('KW_BLAZE_CUT', key='BLAZECUT', comment='Extract: Blaze cut used')

# TODO: is blaze_deg needed with sinc function?
# the blaze degree used (to fit)
KDict.set('KW_BLAZE_DEG', key='BLAZEDEG', comment='Extract: Blaze fit degree used')

# The blaze sinc cut threshold used
KDict.set('KW_BLAZE_SCUT', key='BLAZSCUT', comment='Extract: Blaze sinc cut thres used')

# The blaze sinc sigma clip (rejection threshold) used
KDict.set('KW_BLAZE_SIGFIG', key='BLAZSIGF',
          comment='Extract: Blaze sinc reject thres used')

# The blaze sinc bad percentile value used
KDict.set('KW_BLAZE_BPRCNTL', key='BLAZBPTL',
          comment='Extract: Blaze sinc bad percentile used')

# The number of iterations used in the blaze sinc fit
KDict.set('KW_BLAZE_NITER', key='BLAZNITR', comment='Extract: Blaze sinc no. iters used')

# the cosmic cut criteria
KDict.set('KW_COSMIC_CUT', key='EXTCCUT', comment='Extract: cosmic cut criteria used')

# the cosmic threshold used
KDict.set('KW_COSMIC_THRES', key='EXTCTHRE', comment='Extract: cosmic cut thres used')

# the saturation QC limit
KDict.set('KW_SAT_QC', key='EXTSATQC', comment='Extract: saturation limit criteria')

# the max saturation level
KDict.set('KW_SAT_LEVEL', key='EXTSMAX', comment='Extract: maximum saturation level')

# the wave starting point used for s1d
KDict.set('KW_S1D_WAVESTART', key='S1DWAVE0', comment='Initial wavelength for s1d [nm]')

# the wave end point used for s1d
KDict.set('KW_S1D_WAVEEND', key='S1DWAVE1', comment='Final wavelength for s1d [nm]')

# the wave grid kind used for s1d (wave or velocity)
KDict.set('KW_S1D_KIND', key='S1DWAVEK', comment='Wave grid kind for s1d')

# the bin size for wave grid kind=wave
KDict.set('KW_S1D_BWAVE', key='S1DBWAVE',
          comment='Bin size for wave grid constant in wavelength')

# the bin size for wave grid kind=velocity
KDict.set('KW_S1D_BVELO', key='S1DBVELO',
          comment='Bin size for wave grid constant in velocity')

# the smooth size for the s1d
KDict.set('KW_S1D_SMOOTH', key='S1DSMOOT', comment='Smoothing scale for s1d edge mask')

# the blaze threshold used for the s1d
KDict.set('KW_S1D_BLAZET', key='S1DBLAZT', comment='Blaze threshold for s1d')

# the observatory latitude used to calculate the BERV
KDict.set('KW_BERVLAT', key='BC_LAT', comment='OBS Latitude [deg] used to calc. BERV')

# the observatory longitude used to calculate the BERV
KDict.set('KW_BERVLONG', key='BC_LONG', comment='OBS Longitude [deg] used to calc. BERV')

# the observatory altitude used to calculate the BERV
KDict.set('KW_BERVALT', key='BC_ALT', comment='OBS Altitude [m] used to calc. BERV')

# the BERV calculated with KW_BERVSOURCE
KDict.set('KW_BERV', key='BERV', comment='Barycentric Velocity calc. in BERVSRCE [km/s]',
          datatype=float)

# the Barycenter Julian date calculate with KW_BERVSOURCE
KDict.set('KW_BJD', key='BJD',
          comment='Barycentric Julian date mid exp calc. BERVSRCE',
          datatype=float)

# the maximum BERV found across 1 year (with KW_BERVSOURCE)
KDict.set('KW_BERVMAX', key='BERVMAX', comment='Max BERV 1 yr calc. in BERVSRCE [km/s]',
          datatype=float)

# the derivative of the BERV (BERV at time + 1s - BERV)
KDict.set('KW_DBERV', key='DBERV', comment='Deviation in BERV in BERVSRCE [km/s/s]',
          datatype=float)

# the source of the calculated BERV parameters
KDict.set('KW_BERVSOURCE', key='BERVSRCE', comment='How BERV was calculated',
          datatype=str)

# the BERV calculated with the estimate
KDict.set('KW_BERV_EST', key='BERV_EST', comment='Barycentric Velocity estimate [km/s]',
          datatype=float)

# the Barycenter Julian date calculated with the estimate
KDict.set('KW_BJD_EST', key='BJD_EST', comment='Barycentric Julian date estimate',
          datatype=float)

# the maximum BERV found across 1 year (calculated with estimate)
KDict.set('KW_BERVMAX_EST', key='BERVMAXE', comment='Max BERV 1 yr estimate [km/s]',
          datatype=float)

# the derivative of the BERV (BERV at time + 1s - BERV)
KDict.set('KW_DBERV_EST', key='DBERVE',
          comment='Deviation in BERV estimate [km/s/s]',
          datatype=float)

# the actual jd time used to calculate the BERV
KDict.set('KW_BERV_OBSTIME', key='BERVOBST', comment='BERV observation time used [days]',
          datatype=float)

# the method used to obtain the berv obs time
KDict.set('KW_BERV_OBSTIME_METHOD', key='BERVOBSM',
          comment='BERV method used to calc observation time',
          datatype=str)

# -----------------------------------------------------------------------------
# Define leakage variables
# -----------------------------------------------------------------------------
# Define whether leak correction has been done
KDict.set('KW_LEAK_CORR', key='LEAKCORR',
          comment='Whether DARK_FP leakage correction has been done',
          datatype=int)

# Define the background percentile used for correcting leakage
KDict.set('KW_LEAK_BP_U', key='LEAK_BPU', datatype=float,
          comment='LEAK bckgrd percentile used for leakage corr')

# Define the normalisation percentile used for correcting leakage
KDict.set('KW_LEAK_NP_U', key='LEAK_NPU', datatype=float,
          comment='LEAK norm percentile used for leakage corr')

# Define the e-width smoothing used for correcting leakage reference
KDict.set('KW_LEAK_WSMOOTH', key='LEAKMWSM', datatype=float,
          comment='LEAKM e-width smoothing used for leak reference corr')

# Define the kernel size used for correcting leakage reference
KDict.set('KW_LEAK_KERSIZE', key='LEAKMKSZ', datatype=float,
          comment='LEAKM kernel size used for leak reference corr')

# Define the lower bound percentile used for correcting leakage
KDict.set('KW_LEAK_LP_U', key='LEAK_LPU', datatype=float,
          comment='LEAK lower bound percentile used for leakage corr')

# Define the upper bound percentile used for correcting leakage
KDict.set('KW_LEAK_UP_U', key='LEAK_UPU', datatype=float,
          comment='LEAK upper bound percentile used for leakage corr')

# Define the bad ratio offset limit used for correcting leakage
KDict.set('KW_LEAK_BADR_U', key='LEAKBADR', datatype=float,
          comment='LEAK bad ratio offset limit used for leakage corr')

# -----------------------------------------------------------------------------
# Define wave variables
# -----------------------------------------------------------------------------
# Number of orders in wave image
KDict.set('KW_WAVE_NBO', key='WAVEORDN', comment='nb orders in total',
          parent=None, group='wave')

# fit degree for wave solution
KDict.set('KW_WAVE_DEG', key='WAVEDEGN', comment='degree of wave polyn fit',
          parent=None, group='wave')

# wave polynomial type
KDict.set('KW_WAVE_POLYT', key='WAVEPOLY', comment='type of wave polynomial',
          parent=None, group='wave')

# the wave file used
KDict.set('KW_WAVEFILE', key='WAVEFILE', comment='Wavelength solution file used',
          parent=None, group='wave')

# the wave file mid exptime [mjd]
KDict.set('KW_WAVETIME', key='WAVETIME', comment='Wavelength solution mid exptime',
          parent=None, group='wave')

# the wave source of the wave file used
KDict.set('KW_WAVESOURCE', key='WAVESOUR', comment='Source of the wave solution used.',
          parent=None, group='wave')

# the wave coefficients
KDict.set('KW_WAVECOEFFS', key='WAVE{0:04d}', comment='Wavelength coefficients',
          parent=None, group='wave')

# the wave echelle numbers
KDict.set('KW_WAVE_ECHELLE', key='WAVEEC{0:02d}', comment='Echelle order numbers',
          parent=None, group='wave')

# the initial wave file used for wave solution
KDict.set('KW_INIT_WAVE', key='WAVEINIT', comment='Initial wavelength solution used',
          parent=None, group='wave')

# define the cavity width polynomial key
KDict.set('KW_CAVITY_WIDTH', key='WCAV{0:03d}', comment='Wave cavity polynomial',
          parent=None, group='wave')

# define the cavity fit degree used
KDict.set('KW_CAVITY_DEG', key='WCAV_DEG', comment='Wave cavity fit degree',
          parent=None, group='wave')

# define the cavity poly zero point (to be added on when using)
KDict.set('KW_CAV_PEDESTAL', key='WCAV_PED', comment='Wave cavity pedestal',
          parent=None, group='wave')

# define the mean hc velocity calculated
KDict.set('KW_WAVE_MEANHC', key='WAVEMHC', comment='Wave mean hc velocity')

# define the err on mean hc velocity calculated
KDict.set('KW_WAVE_EMEANHC', key='WAVEEMHC', comment='Wave error mean hc velocity')

# -----------------------------------------------------------------------------
# the fit degree for wave solution used
KDict.set('KW_WAVE_FITDEG', key='WAVE_DEG', comment='fit degree used for wave sol',
          parent='WAVE_FIT_DEGREE', group='wave')

# the mode used to calculate the hc wave solution
KDict.set('KW_WAVE_MODE_HC', key='WAVHCMOD', comment='mode used to calc hc wave sol',
          parent='WAVE_MODE_HC', group='wave')

# the mode used to calculate the fp wave solution
KDict.set('KW_WAVE_MODE_FP', key='WAVFPMOD', comment='mode used to calc fp wave sol',
          parent='WAVE_MODE_FP', group='wave')

# the echelle number of the first order used
KDict.set('KW_WAVE_ECHELLE_START', key='WAV_ECH0', comment='Echelle no. of first order',
          parent='WAVE_T_ORDER_START', group='wave')

# the width of the box for fitting hc lines used
KDict.set('KW_WAVE_HCG_WSIZE', key='WAVHGSIZ', comment='HC Gauss peak fit box width',
          parent='WAVE_HC_FITBOX_SIZE', group='wave')

# the sigma above local rms for fitting hc lines used
KDict.set('KW_WAVE_HCG_SIGPEAK', key='WAVHGSPK',
          comment='HC Gauss peak fit rms sig peak',
          parent='WAVE_HC_FITBOX_SIGMA', group='wave')

# the fit degree for the gaussian peak fitting used
KDict.set('KW_WAVE_HCG_GFITMODE', key='WAVHGGFM',
          comment='HC Gauss peak fit, fit degree',
          parent='WAVE_HC_FITBOX_GFIT_DEG', group='wave')

# the min rms for gaussian peak fitting used
KDict.set('KW_WAVE_HCG_FB_RMSMIN', key='WAVHGRMN',
          comment='HC Gauss peak fit, min rms for peak',
          parent='WAVE_HC_FITBOX_RMS_DEVMIN', group='wave')

# the max rms for gaussian peak fitting used
KDict.set('KW_WAVE_HCG_FB_RMSMAX', key='WAVHGRMX',
          comment='HC Gauss peak fit, max rms for peak',
          parent='WAVE_HC_FITBOX_RMS_DEVMAX', group='wave')

# the min e-width of the line for gaussian peak fitting used
KDict.set('KW_WAVE_HCG_EWMIN', key='WAVHGEW0', comment='HC Gauss peak fit, e-width min',
          parent='WAVE_HC_FITBOX_EWMIN', group='wave')

# the min e-width of the line for gaussian peak fitting used
KDict.set('KW_WAVE_HCG_EWMAX', key='WAVHGEW1', comment='HC Gauss peak fit, e-width max',
          parent='WAVE_HC_FITBOX_EWMAX', group='wave')

# the filename for the HC line list generated
KDict.set('KW_WAVE_HCLL_FILE', key='WAVEHCLL', comment='HC line list file generated',
          parent=None, group='wave')

# the number of bright lines to used in triplet fit
KDict.set('KW_WAVE_TRP_NBRIGHT', key='WAVTNBRI',
          comment='Triplet fit - no. bright lines used',
          parent='WAVE_HC_NMAX_BRIGHT', group='wave')

# the number of iterations done in triplet fit
KDict.set('KW_WAVE_TRP_NITER', key='WAVTNITR',
          comment='Triplet fit - no. iterations used',
          parent='WAVE_HC_NITER_FIT_TRIPLET', group='wave')

# the max distance between catalog line and initial guess line in triplet fit
KDict.set('KW_WAVE_TRP_CATGDIST', key='WAVTCATD',
          comment='Triplet fit - max dist btwn line cat & guess',
          parent='WAVE_HC_MAX_DV_CAT_GUESS', group='wave')

# the fit degree for triplet fit
KDict.set('KW_WAVE_TRP_FITDEG', key='WAVTFDEG', comment='Triplet fit - fit degree',
          parent='WAVE_HC_TFIT_DEG', group='wave')

# the minimum number of lines required per order in triplet fit
KDict.set('KW_WAVE_TRP_MIN_NLINES', key='WAVTMINL',
          comment='Triplet fit - min no. lines req. per order',
          parent='WAVE_HC_TFIT_MINNUM_LINES', group='wave')

# the total number of lines required in triplet fit
KDict.set('KW_WAVE_TRP_TOT_NLINES', key='WAVTTOTL',
          comment='Triplet fit - total no. lines required',
          parent='WAVE_HC_TFIT_MINTOT_LINES', group='wave')

# the degree(s) of fit to ensure continuity in triplet fit
KDict.set('KW_WAVE_TRP_ORDER_FITCONT', key='WAVTO{0:03d}',
          comment='Triplet fit - order continuity fit',
          parent='WAVE_HC_TFIT_ORDER_FIT_CONT', group='wave')

# the iteration number for sigma clip in triplet fit
KDict.set('KW_WAVE_TRP_SCLIPNUM', key='WAVT_SCN',
          comment='Triplet fit - iter no. for sig clip',
          parent='WAVE_HC_TFIT_SIGCLIP_NUM', group='wave')

# the sigma clip threshold in triplet fit
KDict.set('KW_WAVE_TRP_SCLIPTHRES', key='WAVT_SCT',
          comment='Triplet fit - sig clip threshold',
          parent='WAVE_HC_TFIT_SIGCLIP_THRES', group='wave')

# the distance away in dv to reject order triplet in triplet fit
KDict.set('KW_WAVE_TRP_DVCUTORD', key='WAVT_DVO',
          comment='Triplet fit - dist in dv per order to reject',
          parent='WAVE_HC_TFIT_DVCUT_ORDER', group='wave')

# the distance away in dv to reject all triplet in triplet fit
KDict.set('KW_WAVE_TRP_DVCUTALL', key='WAVT_DVA',
          comment='Triplet fit - dist in dv all to reject',
          parent='WAVE_HC_TFIT_DVCUT_ALL', group='wave')

# the wave resolution map dimensions
KDict.set('KW_WAVE_RES_MAPSIZE', key='WAVRE{0:03d}',
          comment='Wave res map - map dimensions',
          parent='WAVE_HC_RESMAP_SIZE', group='wave')

# the width of the box for wave resolution map
KDict.set('KW_WAVE_RES_WSIZE', key='WAVRSIZE',
          comment='Wave res map - width of box',
          parent='WAVE_HC_FITBOX_SIZE', group='wave')

# the max deviation in rms allowed in wave resolution map
KDict.set('KW_WAVE_RES_MAXDEVTHRES', key='WAVRDEV',
          comment='Wave res map - max dev in rms allowed',
          parent='WAVE_HC_RES_MAXDEV_THRES', group='wave')

# the littrow start order used for HC
KDict.set('KW_WAVE_LIT_START_1', key='WAVL1_ST', comment='Littrow HC - start value',
          parent=['WAVE_LITTROW_ORDER_INIT_1',
                  'WAVE_LITTROW_ORDER_INIT_2'],
          group='wave')

# the littrow end order used for HC
KDict.set('KW_WAVE_LIT_END_1', key='WAVL1_EN', comment='Littrow HC - end value',
          parent=['WAVE_LITTROW_ORDER_FINAL_1',
                  'WAVE_LITTROW_ORDER_FINAL_2'],
          group='wave')

# the orders removed from the littrow test
KDict.set('KW_WAVE_LIT_RORDERS', key='WAVLR{0:03d}', comment='Littrow - removed orders',
          parent='WAVE_LITTROW_REMOVE_ORDERS', group='wave')

# the littrow order initial value used for HC
KDict.set('KW_WAVE_LIT_ORDER_INIT_1', key='WAVL1OIN',
          comment='Littrow HC - order init value',
          parent='WAVE_LITTROW_ORDER_INIT_1', group='wave')

# the littrow order start value used for HC
KDict.set('KW_WAVE_LIT_ORDER_START_1', key='WAVL1OST',
          comment='Littrow HC - order start value',
          parent='WAVE_N_ORD_START', group='wave')

# the littrow order end value used for HC
KDict.set('KW_WAVE_LIT_ORDER_END_1', key='WAVL1OEN',
          comment='Littrow HC - order end value',
          parent='WAVE_N_ORD_FINAL', group='wave')

# the littrow x cut step value used for HC
KDict.set('KW_WAVE_LITT_XCUTSTEP_1', key='WAVL1XCT',
          comment='Littrow HC - x cut step value',
          parent='WAVE_LITTROW_CUT_STEP_1', group='wave')

# the littrow fit degree value used for HC
KDict.set('KW_WAVE_LITT_FITDEG_1', key='WAVL1FDG',
          comment='Littrow HC - littrow fit degree',
          parent='WAVE_LITTROW_FIG_DEG_1', group='wave')

# the littrow extrapolation fit degree value used for HC
KDict.set('KW_WAVE_LITT_EXT_FITDEG_1', key='WAVL1EDG',
          comment='Littrow HC - extrapolation fit degree',
          parent='WAVE_LITTROW_EXT_ORDER_FIT_DEG',
          group='wave')

# the littrow extrapolation start order value used for HC
KDict.set('KW_WAVE_LITT_EXT_ORD_START_1', key='WAVL1EST',
          comment='Littrow HC - extrap start order',
          parent='WAVE_LITTROW_ORDER_INIT_1',
          group='wave')

# the first order used for FP wave sol improvement
KDict.set('KW_WFP_ORD_START', key='WFP_ORD0',
          comment='First order used for FP wave sol.',
          parent='WAVE_N_ORD_START', group='wave')

# the last order used for FP wave sol improvement
KDict.set('KW_WFP_ORD_FINAL', key='WFP_ORD1',
          comment='Last order used for FP wave sol.',
          parent='WAVE_N_ORD_FINAL', group='wave')

# the blaze threshold used for FP wave sol improvement
KDict.set('KW_WFP_BLZ_THRES', key='WFPBLZTH',
          comment='Blaze threshold used for FP wave sol.',
          parent='WAVE_FP_BLAZE_THRES', group='wave')

# the minimum fp peak pixel sep used for FP wave sol improvement
KDict.set('KW_WFP_XDIFF_MIN', key='WFPXDIF0',
          comment='Min fp peak pixel sep for FP wave sol.',
          parent='WAVE_FP_XDIF_MIN', group='wave')

# the maximum fp peak pixel sep used for FP wave sol improvement
KDict.set('KW_WFP_XDIFF_MAX', key='WFPXDIF1',
          comment='Max fp peak pixel sep for FP wave sol.',
          parent='WAVE_FP_XDIF_MAX', group='wave')

# the initial value of the FP effective cavity width used
KDict.set('KW_WFP_DOPD0', key='WFPDOPD0',
          comment='initial value of Fp effective cavity width',
          parent='WAVE_FP_DOPD0', group='wave')

# the  maximum fraction wavelength offset btwn xmatch fp peaks used
KDict.set('KW_WFP_LL_OFFSET', key='WFPLLOFF',
          comment='max frac. wavelength offset btwn fp peaks',
          parent='WAVE_FP_LL_OFFSET', group='wave')

# the max dv to keep hc lines used
KDict.set('KW_WFP_DVMAX', key='WFPDVMAX',
          comment='max dv to kee[ hc lines for fp wave sol.',
          parent='WAVE_FP_DV_MAX', group='wave')

# the used polynomial fit degree (to fit wave solution)
KDict.set('KW_WFP_LLFITDEG', key='WFPLLDEG',
          comment='Used poly fit degree for fp wave sol.',
          parent='WAVE_FP_LL_DEGR_FIT', group='wave')

# whether the cavity file was updated
KDict.set('KW_WFP_UPDATECAV', key='WFPUPCAV',
          comment='Whether wave sol. was used to update cav file',
          parent='WAVE_FP_UPDATE_CAVITY', group='wave')

# the mode used to fit the FP cavity
KDict.set('KW_WFP_FPCAV_MODE', key='WFPCAVMO',
          comment='The mode used to fit the FP cavity',
          parent='WAVE_FP_CAVFIT_MODE', group='wave')

# the mode used to fit the wavelength
KDict.set('KW_WFP_LLFIT_MODE', key='WFPLLFMO',
          comment='The mode used to fit the wavelength sol.',
          parent='WAVE_FP_LLFIT_MODE', group='wave')

# the minimum instrumental error used
KDict.set('KW_WFP_ERRX_MIN', key='WFPERRXM',
          comment='The minimum instrumental error used for wave sol.',
          parent='WAVE_FP_ERRX_MIN', group='wave')

# the max rms for the wave sol sig clip
KDict.set('KW_WFP_MAXLL_FIT_RMS', key='WFPMAXLL',
          comment='The max rms for the FP wave sol sig cut',
          parent='WAVE_FP_MAX_LLFIT_RMS', group='wave')

# the echelle number used for the first order
KDict.set('KW_WFP_T_ORD_START', key='WFPTORD',
          comment='The echelle number of order 0 (fp wave sol.)',
          parent='WAVE_T_ORDER_START', group='wave')

# the weight below which fp lines are rejected
KDict.set('KW_WFP_WEI_THRES', key='WFPWTHRE',
          comment='The weight below which FP lines are rejected',
          parent='WAVE_FP_WEIGHT_THRES', group='wave')

# the polynomial degree fit order used for fitting the fp cavity
KDict.set('KW_WFP_CAVFIT_DEG', key='WFPCVFIT',
          comment='The fit degree used for fitting the fp cavity',
          parent='WAVE_FP_CAVFIT_DEG', group='wave')

# the largest jump in fp that was allowed
KDict.set('KW_WFP_LARGE_JUMP', key='WFPLJUMP',
          comment='The largest jump in fp that is allowed',
          parent='WAVE_FP_LARGE_JUMP', group='wave')

# the index to start crossmatching fps at
KDict.set('KW_WFP_CM_INDX', key='WFPCMIND',
          comment='The index to start crossmatch at',
          parent='WAVE_FP_CM_IND', group='wave')

# the FP widths used for each order (1D list)
KDict.set('KW_WFP_WIDUSED', key='WFPWD{0:03d}',
          comment='The FP width (peak to peak) used for each order',
          group='wave')

# the percentile to normalise the FP flux per order used
KDict.set('KW_WFP_NPERCENT', key='WFPNPRCT',
          comment='WAVE FP percentile thres to norm FP flux used',
          parent='WAVE_FP_NORM_PERCENTILE', group='wave')

# the normalised limited used to detect FP peaks
KDict.set('KW_WFP_LIMIT', key='WFPNLIMT',
          comment='WAVE FP norm limit to detect FP peaks used',
          parent='WAVE_FP_PEAK_LIM', group='wave')

# the normalised cut width for large peaks used
KDict.set('KW_WFP_CUTWIDTH', key='WFPCUTWD',
          comment='Normalised cut width used for large FP peaks',
          parent='WAVE_FP_P2P_WIDTH_CUT', group='wave')

# Wavelength solution for fiber C that is is source of the WFP keys
KDict.set('KW_WFP_FILE', key='WFP_FILE', comment='WFP source file',
          parent=None, group='wave')

# drift of the FP file used for the wavelength solution
KDict.set('KW_WFP_DRIFT', key='WFPDRIFT',
          comment='Wavelength sol absolute CCF FP Drift [km/s]',
          parent=None, group='wave')

# FWHM of the wave FP file CCF
KDict.set('KW_WFP_FWHM', key='WFPFWHM', comment='FWHM of wave sol FP CCF [km/s]',
          parent=None, group='wave')

# Contrast of the wave FP file CCF
KDict.set('KW_WFP_CONTRAST', key='WFPCONT', comment='wave sol FP Contrast of CCF (%)',
          parent=None, group='wave')

# Mask for the wave FP file CCF
KDict.set('KW_WFP_MASK', key='WFPMASK', comment='wave sol FP Mask filename',
          parent='WAVE_CCF_MASK', group='wave')

# Number of lines for the wave FP file CCF
KDict.set('KW_WFP_LINES', key='WFPLINE', comment='wave sol FP nbr of lines used',
          parent=None, group='wave')

# Target RV for the wave FP file CCF
KDict.set('KW_WFP_TARG_RV', key='WFPTRV', comment='wave sol FP target RV [km/s]',
          parent='WAVE_CCF_TARGET_RV', group='wave')

# Width for the wave FP file CCF
KDict.set('KW_WFP_WIDTH', key='WFPWIDTH', comment='wave sol FP CCF width [km/s]',
          parent='WAVE_CCF_WIDTH', group='wave')

# Step for the wave FP file CCF
KDict.set('KW_WFP_STEP', key='WFPSTEP', comment='wave sol FP CCF step [km/s]',
          parent='WAVE_CCF_STEP', group='wave')

# The sigdet used for FP file CCF
KDict.set('KW_WFP_SIGDET', key='WFPCSDET', comment='wave sol FP CCF sigdet used',
          parent='WAVE_CCF_NOISE_SIGDET', group='wave')

# The boxsize used for FP file CCF
KDict.set('KW_WFP_BOXSIZE', key='WFPCBSZ', comment='wave sol FP CCF boxsize used',
          parent='WAVE_CCF_NOISE_BOXSIZE', group='wave')

# The max flux used for the FP file CCF
KDict.set('KW_WFP_MAXFLUX', key='WFPCMFLX', comment='wave sol FP CCF max flux used',
          parent='CCF_N_ORD_MAX', group='wave')

# The det noise used for the FP file CCF
KDict.set('KW_WFP_DETNOISE', key='WFPCDETN', comment='wave sol FP CCF det noise used',
          parent='WAVE_CCF_DETNOISE', group='wave')

# the highest order used for the FP file CCF
KDict.set('KW_WFP_NMAX', key='WFPCNMAX', comment='wave sol FP CCF highest order used',
          parent='WAVE_CCF_N_ORD_MAX', group='wave')

# The weight of the CCF mask (if 1 force all weights equal) used for FP CCF
KDict.set('KW_WFP_MASKMIN', key='WFPCMMIN', comment='wave sol FP CCF mask weight used',
          parent='WAVE_CCF_MASK_MIN_WEIGHT', group='wave')

# The width of the CCF mask template line (if 0 use natural) used for FP CCF
KDict.set('KW_WFP_MASKWID', key='WFPCMWID', comment='wave sol FP CCF mask width used',
          parent='WAVE_CCF_MASK_WIDTH', group='wave')

# The units of the input CCF mask (converted to nm in code)
KDict.set('KW_WFP_MASKUNITS', key='WFPCMUNT', comment='wave sol FP CCF mask units used',
          parent='WAVE_CCF_MASK_UNITS', group='wave')

# number of iterations for convergence used in wave night (hc)
KDict.set('KW_WNT_NITER1', key='WNTNITER', comment='wave night hc n iterations used',
          parent='WAVE_NIGHT_NITERATIONS1', group='wave')

# number of iterations for convergence used in wave night (fp)
KDict.set('KW_WNT_NITER21', key='WNTNITER',
          comment='wave night fp n iterations used',
          parent='WAVE_NIGHT_NITERATIONS2', group='wave')

# starting point for the cavity corrections used in wave night
KDict.set('KW_WNT_DCAVITY', key='WNTDCVTY',
          comment='wave night starting point for cavity corr used',
          parent='WAVE_NIGHT_DCAVITY', group='wave')

# source fiber for the cavity correction
KDict.set('KW_WNT_DCAVSRCE', key='WNTDCVSR',
          comment='wave night source fiber used for cavity corr',
          group='wave')

# define the sigma clip value to remove bad hc lines used
KDict.set('KW_WNT_HCSIGCLIP', key='WNTHCSIG', comment='wave night hc sig clip used',
          group='wave', parent='WAVE_NIGHT_HC_SIGCLIP')

# median absolute deviation cut off used
KDict.set('KW_WNT_MADLIMIT', key='WNT_MADL',
          comment='wave night med abs dev cut off used',
          group='wave', parent='WAVE_NIGHT_MED_ABS_DEV')

# sigma clipping for the fit used in wave night
KDict.set('KW_WNT_NSIG_FIT', key='WNTNSIGF', comment='wave night sig clip fit cut used',
          parent='WAVE_NIGHT_NSIG_FIT_CUT', group='wave')

# -----------------------------------------------------------------------------
# Define wave res (new) variables
# -----------------------------------------------------------------------------
# number of orders for the resolution map header
KDict.set('KW_RESMAP_NBO', key='RES_NBO', comment='Total number of orders',
          group='wave-res')

# number of pixels in an order for the resolution map header
KDict.set('KW_RESMAP_NBPIX', key='RESNBPIX', comment='Total number of pixels per order')

# current bin number for order direction for the resolution map header
KDict.set('KW_RESMAP_BINORD', key='RESCBINO', group='wave-res',
          comment='Current bin number for order direction')

# total number of bins in order direction for the resolution map header
KDict.set('KW_RESMAP_NBINORD', key='RESNBINO', group='wave-res',
          comment='Total number bins in order direction')

# current bin number in spatial direction for the resolution map header
KDict.set('KW_RESMAP_BINPIX', key='RESCBINP', group='wave-res',
          comment='Current bin number for spatial direction')

# total number of bins in spatial direction for the resolution map header
KDict.set('KW_RESMAP_NBINPIX', key='RESNBINP', group='wave-res',
          comment='Total number bins in spatial direction')

# First order used in this sector
KDict.set('KW_RES_MAP_ORDLOW', key='ORDSTART', group='wave-res',
          comment='First order used in this sector')

# Last order used in this sector
KDict.set('KW_RES_MAP_ORDHIGH', key='ORDFINAL', group='wave-res',
          comment='Last order used in this sector')

# First pixel used in this sector
KDict.set('KW_RES_MAP_PIXLOW', key='PIXSTART', group='wave-res',
          comment='First pixel used in this sector')

# Last pixel used in this sector
KDict.set('KW_RES_MAP_PIXHIGH', key='PIXFINAL', group='wave-res',
          comment='Last pixel used in this sector')

# FWHM from fit for this sector
KDict.set('KW_RES_MAP_FWHM', key='FIT_FWHM', group='wave-res',
          comment='FWHM from fit for this sector')

# Amplitude from fit for this sector
KDict.set('KW_RES_MAP_AMP', key='FIT_AMP', group='wave-res',
          comment='Amplitude from fit for this sector')

# Exponent from fit for this sector
KDict.set('KW_RES_MAP_EXPO', key='FIT_EXPO', group='wave-res',
          comment='Exponent from fit for this sector')

# Measured effective resolution measured for this sector
KDict.set('KW_RES_MAP_RESEFF', key='RES_EFF', group='wave-res',
          comment='Measured effective resolution for this sector')

# -----------------------------------------------------------------------------
# Define telluric sky model variables
# -----------------------------------------------------------------------------
# Defines whether we have a sky correction for the science fiber
KDict.set('KW_HAS_SKY_SCI', key='HSKYSCI', group='skymodel',
          comment='Sky model calculated for science fiber')

# Defines whether we have a sky correction for the calib fiber
KDict.set('KW_HAS_SKY_CAL', key='HSKYCAL', group='skymodel',
          comment='Sky model calculated for science fiber')

# Defines which fiber was used for the science fiber sky correction model
KDict.set('KW_SKY_SCI_FIBER', key='FSKYSCI', group='skymodel',
          comment='Sky model fiber used as science fiber')

# Defines which fiber was used for the calib fiber sky correction model
KDict.set('KW_SKY_CAL_FIBER', key='FSKYCAL', group='skymodel',
          comment='Sky model fiber used as calibration fiber')

# -----------------------------------------------------------------------------
# Define telluric preclean variables
# -----------------------------------------------------------------------------
# Define the exponent of water key from telluric preclean process
KDict.set('KW_TELLUP_EXPO_WATER', key='TLPEH2O',
          comment='tellu preclean expo water calculated')

# Define the exponent of other species from telluric preclean process
KDict.set('KW_TELLUP_EXPO_OTHERS', key='TLPEOTR',
          comment='tellu preclean expo others calculated')

# Define the velocity of water absorbers calculated in telluric preclean process
KDict.set('KW_TELLUP_DV_WATER', key='TLPDVH2O',
          comment='tellu preclean velocity water absorbers')

# Define the velocity of other species absorbers calculated in telluric
#     preclean process
KDict.set('KW_TELLUP_DV_OTHERS', key='TLPDVOTR',
          comment='tellu preclean velocity others absorbers')

# Define the ccf power of the water
KDict.set('KW_TELLUP_CCFP_WATER', key='TLPCPH2O', comment='CCF power of H20')

# Define the ccf power of the others
KDict.set('KW_TELLUP_CCFP_OTHERS', key='TLPCPOTR', comment='CCF power of other species')

# Define whether precleaning was done (tellu pre-cleaning)
KDict.set('KW_TELLUP_DO_PRECLEAN', key='TLPDOCLN', comment='tellu preclean done',
          parent='TELLUP_DO_PRECLEANING')

# Define default water absorption used (tellu pre-cleaning)
KDict.set('KW_TELLUP_DFLT_WATER', key='TLPDFH2O',
          comment='tellu preclean default H2O abso used',
          parent='TELLUP_D_WATER_ABSO')

# Define default water absorption used (tellu pre-cleaning)
KDict.set('KW_TELLUP_DFLT_WATER', key='TLPDFH2O',
          comment='tellu preclean default H2O abso used',
          parent='TELLUP_D_WATER_ABSO')

# Define ccf scan range that was used (tellu pre-cleaning)
KDict.set('KW_TELLUP_CCF_SRANGE', key='TLPSCRNG',
          comment='tellu preclean ccf scan range km/s',
          parent='TELLUP_CCF_SCAN_RANGE')

# Define whether we cleaned OH lines
KDict.set('KW_TELLUP_CLEAN_OHLINES', key='TLPCLORD',
          comment='tellu preclean were OH lines were cleaned',
          parent='TELLUP_CLEAN_OH_LINES')

# Define which orders were removed from tellu pre-cleaning
KDict.set('KW_TELLUP_REMOVE_ORDS', key='TLPRORDS',
          comment='tellu preclean which orders were removed',
          parent='TELLUP_REMOVE_ORDS')

# Define which min snr threshold was used for tellu pre-cleaning
KDict.set('KW_TELLUP_SNR_MIN_THRES', key='TLPSNRMT',
          comment='tellu preclean snr min threshold',
          parent='TELLUP_SNR_MIN_THRES')

# Define dexpo convergence threshold used
KDict.set('KW_TELLUP_DEXPO_CONV_THRES', key='TLPDEXCT',
          comment='tellu preclean dexpo conv thres used',
          parent='TELLUP_DEXPO_CONV_THRES')

# Define the maximum number of oterations used to get dexpo convergence
KDict.set('KW_TELLUP_DEXPO_MAX_ITR', key='TLPMXITR',
          comment='tellu preclean max iterations used',
          parent='TELLUP_DEXPO_MAX_ITR')

# Define the kernel threshold in abso_expo used in tellu pre-cleaning
KDict.set('KW_TELLUP_ABSOEXPO_KTHRES', key='TLPAEKTH',
          comment='tellu preclean abso expo kernel thres',
          parent='TELLUP_ABSO_EXPO_KTHRES')

# Define the wave start (same as s1d) in nm used
KDict.set('KW_TELLUP_WAVE_START', key='TLPWAVES',
          comment='tellu preclean wave start used [nm]',
          parent='EXT_S1D_WAVESTART')

# Define the wave end (same as s1d) in nm used
KDict.set('KW_TELLUP_WAVE_END', key='TLPWAVEF',
          comment='tellu preclean wave end used [nm]',
          parent='EXT_S1D_WAVEEND')

# Define the dv wave grid (same as s1d) in km/s used
KDict.set('KW_TELLUP_DVGRID', key='TLPDVGRD',
          comment='tellu preclean dv wave grid used [km/s]',
          parent='EXT_S1D_BIN_UVELO')

# Define the gauss width of the kernel used in abso_expo for tellu pre-cleaning
KDict.set('KW_TELLUP_ABSOEXPO_KWID', key='TLPAEKWD',
          comment='tellu preclean gauss width kernel used',
          parent='TELLUP_ABSO_EXPO_KWID')

# Define the gauss shape of the kernel used in abso_expo for tellu pre-cleaning
KDict.set('KW_TELLUP_ABSOEXPO_KEXP', key='TLPAEKEX',
          comment='tellu preclean gauss shape kernel used',
          parent='TELLUP_ABSO_EXPO_KEXP')

# Define the exponent of the transmission threshold used for tellu pre-cleaning
KDict.set('KW_TELLUP_TRANS_THRES', key='TLPTRSTH',
          comment='tellu preclean transmission thres used',
          parent='TELLUP_TRANS_THRES')

# Define the threshold for discrepant tramission used for tellu pre-cleaning
KDict.set('KW_TELLUP_TRANS_SIGL', key='TLPTRSLM',
          comment='tellu preclean transmission sig limit used',
          parent='TELLUP_TRANS_SIGLIM')

# Define the whether to force fit to header airmass used for tellu pre-cleaning
KDict.set('KW_TELLUP_FORCE_AIRMASS', key='TLPFCARM',
          comment='tellu preclean force airmass from hdr',
          parent='TELLUP_FORCE_AIRMASS')

# Define the bounds of the exponent of other species used for tellu pre-cleaning
KDict.set('KW_TELLUP_OTHER_BOUNDS', key='TLP_OTHB',
          comment='tellu preclean lower/upper bounds others',
          parent='TELLUP_OTHER_BOUNDS')

# Define the bounds of the exponent of water used for tellu pre-cleaning
KDict.set('KW_TELLUP_WATER_BOUNDS', key='TLP_H2OB',
          comment='tellu preclean lower/upper bounds water',
          parent='TELLUP_WATER_BOUNDS')

# -----------------------------------------------------------------------------
# Define make telluric variables
# -----------------------------------------------------------------------------
# The template file used for mktellu calculation
KDict.set('KW_MKTELL_TEMP_FILE', key='MKTTEMPF', comment='mktellu template file used')

# the number of template files used
KDict.set('KW_MKTELL_TEMPNUM', key='MKTTEMPN', comment='mktellu template used for sed')

# the hash for the template generation (unique)
KDict.set('KW_MKTELL_TEMPHASH', key='MKTTEMPH', comment='mktellu template unique hash')

# the time the template was generated
KDict.set('KW_MKTELL_TEMPTIME', key='MKTTEMPT', comment='mktellu template create time')

# The blaze percentile used for mktellu calculation
KDict.set('KW_MKTELL_BLAZE_PRCT', key='MKTBPRCT', comment='mktellu blaze percentile')

# The blaze normalization cut used for mktellu calculation
KDict.set('KW_MKTELL_BLAZE_CUT', key='MKTBZCUT', comment='mktellu blaze cut used')

# The default convolution width in pix used for mktellu calculation
KDict.set('KW_MKTELL_DEF_CONV_WID', key='MKTDCONV',
          comment='mktellu default conv width used')

# The median filter width used for mktellu calculation
KDict.set('KW_MKTELL_TEMP_MEDFILT', key='MKT_TMED',
          comment='mktellu template med filter used')

# The recovered airmass value calculated in mktellu calculation
KDict.set('KW_MKTELL_AIRMASS', key='MTAUOTHE',
          comment='mktellu recovered airmass (tau other)')

# The recovered water optical depth calculated in mktellu calculation
KDict.set('KW_MKTELL_WATER', key='MTAUH2O',
          comment='mktellu recovered water depth (tau H2O)')

# The min transmission requirement used for mktellu/ftellu
KDict.set('KW_MKTELL_THRES_TFIT', key='MKTTTFIT',
          comment='mktellu min transmission used',
          parent='MKTELLU_THRES_TRANSFIT')

# The upper limit for trans fit used in mktellu/ftellu
KDict.set('KW_MKTELL_TRANS_FIT_UPPER_BAD', key='MKTTTMAX',
          comment='mktellu max transmission used',
          parent='MKTELLU_TRANS_FIT_UPPER_BAD')

# The number of files used in the trans file model
KDict.set('KW_MKMODEL_NFILES', key='MKMNFILE',
          comment='mkmodel number of trans files')

# The min number of files in the trans file model
KDict.set('KW_MKMODEL_MIN_FILES', key='MKMMFILE',
          comment='mkmodel min number of trans files')

# The sigma cut for the trans file model
KDict.set('KW_MKMODEL_SIGCUT', key='MKMSIGMA',
          comment='mkmodel sigma cut for trans model')

# -----------------------------------------------------------------------------
# Define fit telluric variables
# -----------------------------------------------------------------------------
# The number of principle components used
KDict.set('KW_FTELLU_NPC', key='FTT_NPC',
          comment='ftellu Number of principal components used')

# The number of trans files used in pc fit (closest in expo H2O/others)
KDict.set('KW_FTELLU_NTRANS', key='FTT_NTRS',
          comment='ftellu NUmber of trans files used in pc fit')

# whether we added first derivative to principal components
KDict.set('KW_FTELLU_ADD_DPC', key='FTT_ADPC',
          comment='ftellu first deriv. was added to pc')

# whether we fitted the derivatives of the principal components
KDict.set('KW_FTELLU_FIT_DPC', key='FTT_FDPC',
          comment='ftellu deriv. of pc was fit instead of pc')

# The source of the loaded absorption (npy file or trans_file from database)
KDict.set('KW_FTELLU_ABSO_SRC', key='FTTABSOS',
          comment='ftellu source of the abso (file or database)')

# The prefix for molecular
KDict.set('KW_FTELLU_ABSO_PREFIX', key='ABSO', comment='Absorption in {0}')

# Number of good pixels requirement used
KDict.set('KW_FTELLU_FIT_KEEP_NUM', key='FTTFKNUM',
          comment='ftellu num of good pixels used per order')

# The minimum transmission used
KDict.set('KW_FTELLU_FIT_MIN_TRANS', key='FTTMTRAN',
          comment='ftellu min transmission used')

# The minimum wavelength used
KDict.set('KW_FTELLU_LAMBDA_MIN', key='FTTMINLL', comment='ftellu min wavelength used')

# The maximum wavelength used
KDict.set('KW_FTELLU_LAMBDA_MAX', key='FTTMAXLL', comment='ftellu max wavelength used')

# The smoothing kernel size [km/s] used
KDict.set('KW_FTELLU_KERN_VSINI', key='FTTSKERN',
          comment='ftellu smoothing kernal used [km/s]')

# The image pixel size used
KDict.set('KW_FTELLU_IM_PX_SIZE', key='FTTIMPXS', comment='ftellu image pixel size used')

# the number of iterations used to fit
KDict.set('KW_FTELLU_FIT_ITERS', key='FTTFITRS',
          comment='ftellu num iterations used for fit')

# the log limit in minimum absorption used
KDict.set('KW_FTELLU_RECON_LIM', key='FTTRCLIM',
          comment='ftellu log limit in min absorption used')

# the template that was used (or None if not used)
KDict.set('KW_FTELLU_TEMPLATE', key='FTTTEMPL', comment='ftellu template used for sed')

# the number of template files used
KDict.set('KW_FTELLU_TEMPNUM', key='FTTTEMPN',
          comment='ftellu number of files used for template')

# the hash for the template generation (unique)
KDict.set('KW_FTELLU_TEMPHASH', key='FTTTEMPH', comment='ftellu template unique hash')

# the hash for the template generation (unique)
KDict.set('KW_FTELLU_TEMPTIME', key='FTTTEMPT', comment='ftellu template create time')

# Telluric principle component amplitudes (for use with 1D list)
KDict.set('KW_FTELLU_AMP_PC', key='AMPPC{0:03d}',
          comment='ftellu Principle Component Amplitudes')

# Telluric principle component first derivative
KDict.set('KW_FTELLU_DVTELL1', key='DV_TELL1',
          comment='ftellu Principle Component first der.')

# Telluric principle component second derivative
KDict.set('KW_FTELLU_DVTELL2', key='DV_TELL1',
          comment='ftellu Principle Component second der.')

# Tau Water depth calculated in fit tellu
KDict.set('KW_FTELLU_TAU_H2O', key='TAU_H2O', comment='ftellu TAPAS tau H2O')

# Tau Rest depth calculated in fit tellu
KDict.set('KW_FTELLU_TAU_REST', key='TAU_OTHE',
          comment='ftellu TAPAS tau for O2,O3,CH4,N2O,CO2')

# -----------------------------------------------------------------------------
# Define make template variables
# -----------------------------------------------------------------------------
# store the number of files we had to create template
KDict.set('KW_MKTEMP_NFILES', key='MTPNFILO', comment='mktemplate num files orig')

# store the number of files used to create template
KDict.set('KW_MKTEMP_NFILES_USED', key='MTPNFILU', comment='mktemplate num files used')

# store a unique hash for this template (based on file name etc)
KDict.set('KW_MKTEMP_HASH', key='MTP_HASH', comment='unique hash id for template')

# store time template was created
KDict.set('KW_MKTEMP_TIME', key='MTP_TIME', comment='time the template was created')

# the snr order used for quality control cut in make template calculation
KDict.set('KW_MKTEMP_SNR_ORDER', key='MTPSNROD', comment='mktemplate snr order used')

# the snr threshold used for quality control cut in make template calculation
KDict.set('KW_MKTEMP_SNR_THRES', key='MTPSNRTH', comment='mktemplate snr threshold used')

# the berv coverage calculated for this template calculation
KDict.set('KW_MKTEMP_BERV_COV', key='MTPBCOV',
          comment='mktemplate berv coverage km/s')

# the minimum berv coverage allowed for this template calculation
KDict.set('KW_MKTEMP_BERV_COV_MIN', key='MTPBCMIN',
          comment='mktemplate min berv coverage used km/s')

# the core snr used for this template calculation
KDict.set('KW_MKTEMP_BERV_COV_SNR', key='MTPBCSNR',
          comment='mktemplate berv cov snr used')

# the resolution used for this template calculation
KDict.set('KW_MKTEMP_BERV_COV_RES', key='MTPBCRES',
          comment='mktemplate berv cov resolution used')

# -----------------------------------------------------------------------------
# Define ccf variables
# -----------------------------------------------------------------------------
# type of ccf fit (aborption or emission)
KDict.set('KW_CCF_FIT_TYPE', key='CCFFTYPE', comment='CCF fit type (abs or em)')

# The rv calculated from the ccf stack
KDict.set('KW_CCF_STACK_RV', key='CCFMNRV',
          comment='RV calc. from the CCF stack [km/s]')

# the constrast (depth of fit ccf) from the ccf stack
KDict.set('KW_CCF_STACK_CONTRAST', key='CCFMCONT',
          comment='Contrast (depth of fit) from CCF stack')

# the fwhm from the ccf stack
KDict.set('KW_CCF_STACK_FWHM', key='CCFMFWHM', comment='FWHM from CCF stack')

# the bisector span from the ccf stack
KDict.set('KW_CCF_BISECTOR', key='CCFMBISV', comment='Bisector span from CCF stack')

# the bisector span values (Top to bottom)
KDict.set('KW_CCF_BIS_SPAN', key='CCFMBISL', comment='Bisector top and bottom values')

# the total number of mask lines used in all ccfs
KDict.set('KW_CCF_TOT_LINES', key='CCFTLINE',
          comment='Total no. of mask lines used in CCF')

# The SNR of the CCF stack
KDict.set('KW_CCF_SNR_STACK', key='CCFSNRST',
          comment='SNR of the CCF stack')

# The normalization coefficient of the CCF stack
KDict.set('KW_CCF_NORM_STACK', key='CCFNORMS',
          comment='Normalization coefficient of the CCF stack')

# the ccf mask file used
KDict.set('KW_CCF_MASK', key='CCFMASK', comment='CCF mask file used')

# the ccf step used (in km/s)
KDict.set('KW_CCF_STEP', key='CCFSTEP', comment='CCF step used [km/s]')

# the width of the ccf used (in km/s)
KDict.set('KW_CCF_WIDTH', key='CCFWIDTH', comment='CCF width used [km/s]')

# the central rv used (in km/s) rv elements run from rv +/- width in the ccf
KDict.set('KW_CCF_TARGET_RV', key='CCFTRGRV',
          comment='CCF central RV used in CCF [km/s]')

# the read noise used in the photon noise uncertainty calculation in the ccf
KDict.set('KW_CCF_SIGDET', key='CCFSIGDT',
          comment='Read noise used in photon noise calc. in CCF')

# the size in pixels around saturated pixels to regard as bad pixels used in
#    the ccf photon noise calculation
KDict.set('KW_CCF_BOXSIZE', key='CCFBOXSZ',
          comment='Size of bad px used in photon noise calc. in CCF')

# the upper limit for good pixels (above this are bad) used in the ccf photon
#   noise calculation
KDict.set('KW_CCF_MAXFLUX', key='CCFMAXFX',
          comment='Flux thres for bad px in photon noise calc. in CCF')

# The last order used in the mean CCF (from 0 to nmax are used)
KDict.set('KW_CCF_NMAX', key='CCFORDMX',
          comment='Last order used in mean for mean CCF')

# the minimum weight of a line in the CCF MASK used
KDict.set('KW_CCF_MASK_MIN', key='CCFMSKMN',
          comment='Minimum weight of lines used in the CCF mask')

# the mask width of lines in the CCF Mask used
KDict.set('KW_CCF_MASK_WID', key='CCFMSKWD',
          comment='Width of lines used in the CCF mask')

# the wavelength units used in the CCF Mask for line centers
KDict.set('KW_CCF_MASK_UNITS', key='CCFMUNIT', comment='Units used in CCF Mask')

# the dv rms calculated for spectrum
KDict.set('KW_CCF_DVRMS_SP', key='DVRMS_SP',
          comment='RV photon-noise uncertainty calc on E2DS '
                  'spectrum [m/s] ')

# the dev rms calculated during the CCF [m/s]
KDict.set('KW_CCF_DVRMS_CC', key='DVRMS_CC',
          comment='final photon-noise RV uncertainty calc on mean '
                  'CCF [m/s]')

# The radial velocity measured from the wave solution FP CCF
KDict.set('KW_CCF_RV_WAVE_FP', key='RV_WAVFP',
          comment='RV measured from wave sol FP CCF [km/s]')

# The radial velocity measured from a simultaneous FP CCF
#     (FP in reference channel)
KDict.set('KW_CCF_RV_SIMU_FP', key='RV_SIMFP',
          comment='RV measured from simultaneous FP CCF [km/s]')

# The radial velocity drift between wave sol FP and simultaneous FP (if present)
#   if simulataneous FP not present this is just the wave solution FP CCF value
KDict.set('KW_CCF_RV_DRIFT', key='RV_DRIFT',
          comment='RV drift between wave sol and sim. FP CCF [km/s]')

# The radial velocity measured from the object CCF against the CCF MASK
KDict.set('KW_CCF_RV_OBJ', key='RV_OBJ',
          comment='RV calc in the object CCF (non corr.) [km/s]')

# the corrected radial velocity of the object (taking into account the FP RVs)
KDict.set('KW_CCF_RV_CORR', key='RV_CORR',
          comment='RV corrected for FP CCF drift [km/s]')

# the wave file used for the rv (fiber specific)
KDict.set('KW_CCF_RV_WAVEFILE', key='RV_WAVFN',
          comment='RV wave file used')

# the wave file time used for the rv [mjd] (fiber specific)
KDict.set('KW_CCF_RV_WAVETIME', key='RV_WAVTM',
          comment='RV wave file time used')

# the time diff (in days) between wave file and file (fiber specific)
KDict.set('KW_CCF_RV_TIMEDIFF', key='RV_WAVTD',
          comment='RV timediff [days] btwn file and wave sol.')

# the wave file source used for the rv reference fiber
KDict.set('KW_CCF_RV_WAVESRCE', key='RV_WAVSR',
          comment='RV wave file source used')

# =============================================================================
#  End of configuration file
# =============================================================================
