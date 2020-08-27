"""
Default keywords for instrument

Created on 2019-01-17

@author: cook
"""
from apero.core.instruments.default.default_keywords import *
from astropy import units as uu

# Note: If variables are not showing up MUST CHECK __all__ definition
#       in import * module
__NAME__ = 'config.instruments.spirou.default_keywords.py'

# -----------------------------------------------------------------------------
# Required header keys (main fits file)
# -----------------------------------------------------------------------------
# define the HEADER key for acquisition time
#     Note datatype must be a astropy.Time.format
#     'jd', 'mjd', 'decimalyear', 'unix', 'cxcsec', 'gps', 'plot_date',
#     'datetime', 'iso', 'isot', 'yday', 'datetime64', 'fits', 'byear',
#     'jyear', 'byear_str', 'jyear_str'
KW_ACQTIME = KW_ACQTIME.copy(__NAME__)
KW_ACQTIME.set(key='MJDATE', datatype='mjd', dataformat=float,
               comment='Modified Julian Date at start of observation')

# define the MJ end date HEADER key
KW_MJDEND = KW_MJDEND.copy(__NAME__)
KW_MJDEND.set(key='MJDEND', datatype='mjd', dataformat=float,
              comment='Modified Julian Date at end of observation')

# define the observation date HEADER key
KW_DATE_OBS = KW_DATE_OBS.copy(__NAME__)
KW_DATE_OBS.set(key='DATE-OBS', comment='Date at start of observation (UTC)')

# define the observation time HEADER key
KW_UTC_OBS = KW_UTC_OBS.copy(__NAME__)
KW_UTC_OBS.set(key='UTC-OBS', comment='Time at start of observation (UTC)')

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KW_RDNOISE = KW_RDNOISE.copy(__NAME__)
KW_RDNOISE.set(key='RDNOISE', comment='Read noise (electrons)')

# define the gain HEADER key (used to get value only)
KW_GAIN = KW_GAIN.copy(__NAME__)
KW_GAIN.set(key='GAIN', comment='Amplifier gain (electrons/ADU)')

# define the saturation limit HEADER key
KW_SATURATE = KW_SATURATE.copy(__NAME__)
KW_SATURATE.set(key='SATURATE', comment='Saturation value (ADU) ')

# define the frame time HEADER key
KW_FRMTIME = KW_FRMTIME.copy(__NAME__)
KW_FRMTIME.set(key='FRMTIME', comment='[sec] Frame time, cadence of IR reads')

# define the exposure time HEADER key (used to get value only)
KW_EXPTIME = KW_EXPTIME.copy(__NAME__)
KW_EXPTIME.set(key='EXPTIME', unit=uu.s, comment='[sec] Integration time')

# define the observation type HEADER key
KW_OBSTYPE = KW_OBSTYPE.copy(__NAME__)
KW_OBSTYPE.set(key='OBSTYPE', comment='Observation / Exposure type')

# define the science fiber type HEADER key
KW_CCAS = KW_CCAS.copy(__NAME__)
KW_CCAS.set(key='SBCCAS_P',
            comment='SPIRou Cassegrain Fiber Position (predefined)')

# define the reference fiber type HEADER key
KW_CREF = KW_CREF.copy(__NAME__)
KW_CREF.set(key='SBCREF_P',
            comment='SPIRou Reference Fiber Position (predefined)')

# define the calibration wheel position
KW_CALIBWH = KW_CALIBWH.copy(__NAME__)
KW_CALIBWH.set(key='SBCALI_P',
               comment='SPIRou calibwh predefined position or angle')

# define the target type (object/sky)
KW_TARGET_TYPE = KW_TARGET_TYPE.copy(__NAME__)
KW_TARGET_TYPE.set(key='TRG_TYPE', comment='target or sky object')

# define the density HEADER key
KW_CDEN = KW_CDEN.copy(__NAME__)
KW_CDEN.set(key='SBCDEN_P', comment='SPIRou Calib-Reference density (0 to 3.3)')

# define polarisation HEADER key
KW_CMMTSEQ = KW_CMMTSEQ.copy(__NAME__)
KW_CMMTSEQ.set(key='CMMTSEQ')

# define the exposure number within sequence HEADER key
KW_CMPLTEXP = KW_CMPLTEXP.copy(__NAME__)
KW_CMPLTEXP.set(key='CMPLTEXP',
                comment='Exposure number within the exposure sequence ')

# define the total number of exposures HEADER key
KW_NEXP = KW_NEXP.copy(__NAME__)
KW_NEXP.set(key='NEXP', comment='Total number of exposures within the sequence')

# define the pi name HEADER key
KW_PI_NAME = KW_PI_NAME.copy(__NAME__)
KW_PI_NAME.set(key='PI_NAME', comment='The PI of the program')

# -----------------------------------------------------------------------------
# Required header keys (related to science object)
# -----------------------------------------------------------------------------
# define the observation ra HEADER key
KW_OBJRA = KW_OBJRA.copy(__NAME__)
KW_OBJRA.set(key='OBJRA', unit=uu.hourangle, comment='Target right ascension')

# define the observation dec HEADER key
KW_OBJDEC = KW_OBJDEC.copy(__NAME__)
KW_OBJDEC.set(key='OBJDEC', unit=uu.deg, comment='Target declination ')

# define the observation name
KW_OBJECTNAME = KW_OBJECTNAME.copy(__NAME__)
KW_OBJECTNAME.set(key='OBJECT', comment='Target name')

# define the observation equinox HEADER key
KW_OBJEQUIN = KW_OBJEQUIN.copy(__NAME__)
KW_OBJEQUIN.set(key='OBJEQUIN', datatype='decimalyear',
                comment='Target equinox ')

# define the observation proper motion in ra HEADER key
KW_OBJRAPM = KW_OBJRAPM.copy(__NAME__)
KW_OBJRAPM.set(key='OBJRAPM', unit=uu.arcsec / uu.yr,
               comment='Target right ascension proper motion in as/yr ')

# define the observation proper motion in dec HEADER key
KW_OBJDECPM = KW_OBJDECPM.copy(__NAME__)
KW_OBJDECPM.set(key='OBJDECPM', unit=uu.arcsec / uu.yr,
                comment='Target declination proper motion in as/yr')

# define the airmass HEADER key
KW_AIRMASS = KW_AIRMASS.copy(__NAME__)
KW_AIRMASS.set(key='AIRMASS', comment='Airmass at start of observation')

# define the weather tower temperature HEADER key
KW_WEATHER_TOWER_TEMP = KW_WEATHER_TOWER_TEMP.copy(__NAME__)
KW_WEATHER_TOWER_TEMP.set(key='TEMPERAT',
                          comment='86 temp, air, weather tower deg C  ')

# define the cassegrain temperature HEADER key
KW_CASS_TEMP = KW_CASS_TEMP.copy(__NAME__)
KW_CASS_TEMP.set(key='SB_POL_T',
                 comment='SPIRou tpolar temp at start of exp (deg C)  ')

# define the humidity HEADER key
KW_HUMIDITY = KW_HUMIDITY.copy(__NAME__)
KW_HUMIDITY.set(key='RELHUMID',
                comment='87 relative humidity, weather tower % ')

# define the object temperature HEADER key
KW_OBJ_TEMP = KW_OBJ_TEMP.copy(__NAME__)
KW_OBJ_TEMP.set(key='OBJTEMP', unit=uu.K)

# -----------------------------------------------------------------------------
# Wanted header keys (related to science object)
# -----------------------------------------------------------------------------
# define the gaia id
KW_GAIA_ID = KW_GAIA_ID.copy(__NAME__)
KW_GAIA_ID.set(key='GAIA_ID')

# define the parallax HEADER key
KW_PLX = KW_PLX.copy(__NAME__)
KW_PLX.set(key='OBJPLX', unit=uu.mas)

# define the rv HEADER key
KW_INPUTRV = KW_INPUTRV.copy(__NAME__)
KW_INPUTRV.set(key='OBJRV', unit=uu.km / uu.s)

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
#     - must only be 2 characters long
root_loc = 'LO'
root_flat = 'FF'
root_hc = 'HC'

# define the observation name
KW_OBJNAME = KW_OBJNAME.copy(__NAME__)
KW_OBJNAME.set(key='DRSOBJN', comment='Target name')

# Define the key to get the data fits file type
KW_DPRTYPE = KW_DPRTYPE.copy(__NAME__)
KW_DPRTYPE.set(key='DPRTYPE', comment='The type of file (from pre-process)')

# Define the mid exposure time
KW_MID_OBS_TIME = KW_MID_OBS_TIME.copy(__NAME__)
KW_MID_OBS_TIME.set(key='MJDMID', comment='Mid Observation time [mjd]',
                    datatype='mjd', dataformat=float)

# Define the method by which the MJD was calculated
KW_MID_OBSTIME_METHOD = KW_MID_OBSTIME_METHOD.copy(__NAME__)
KW_MID_OBSTIME_METHOD.set(key='MJDMIDMD',
                          comment='Mid Observation time calc method')

# -----------------------------------------------------------------------------
# Define DRS input keywords
# -----------------------------------------------------------------------------
# input files
KW_INFILE1 = KW_INFILE1.copy(__NAME__)
KW_INFILE1.set(key='INF1{0:03d}', comment='Input file used to create output')
KW_INFILE2 = KW_INFILE2.copy(__NAME__)
KW_INFILE2.set(key='INF2{0:03d}', comment='Input file used to create output')
KW_INFILE3 = KW_INFILE3.copy(__NAME__)
KW_INFILE3.set(key='INF3{0:03d}', comment='Input file used to create output')

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
KW_CDBSHAPEL = KW_CDBSHAPEL.copy(__NAME__)
KW_CDBSHAPEL.set(key='CDBSHAPL', comment='The calibration SHAPEL file used')
KW_CDBSHAPEDX = KW_CDBSHAPEDX.copy(__NAME__)
KW_CDBSHAPEDX.set(key='CDBSHAPX', comment='The calibration SHAPE DX file used')
KW_CDBSHAPEDY = KW_CDBSHAPEDY.copy(__NAME__)
KW_CDBSHAPEDY.set(key='CDBSHAPY', comment='The calibration SHAPE DX file used')
KW_CDBFLAT = KW_CDBFLAT.copy(__NAME__)
KW_CDBFLAT.set(key='CDBFLAT', comment='The calibration FLAT file used')
KW_CDBBLAZE = KW_CDBBLAZE.copy(__NAME__)
KW_CDBBLAZE.set(key='CDBBLAZE', comment='The calibration BLAZE file used')
KW_CDBWAVE = KW_CDBWAVE.copy(__NAME__)
KW_CDBWAVE.set(key='CDBWAVE', comment='The calibration WAVE file used')
KW_CDBTHERMAL = KW_CDBTHERMAL.copy(__NAME__)
KW_CDBTHERMAL.set(key='CDBTHERM', comment='The calibration THERMAL file used')

# additional properties of calibration
KW_C_FLIP = KW_C_FLIP.copy(__NAME__)
KW_C_FLIP.set(key='CAL_FLIP', comment='Whether the image was flipped from pp')
KW_C_CVRTE = KW_C_CVRTE.copy(__NAME__)
KW_C_CVRTE.set(key='CAL_TOE', comment='Whether the flux was converted to e-')
KW_C_RESIZE = KW_C_RESIZE.copy(__NAME__)
KW_C_RESIZE.set(key='CAL_SIZE', comment='Whether the image was resized from pp')
KW_C_FTYPE = KW_C_FTYPE.copy(__NAME__)
KW_C_FTYPE.set(key='CAL_FTYP', comment='What this fiber was identified as')
KW_FIBER = KW_FIBER.copy(__NAME__)
KW_FIBER.set(key='FIBER', comment='The fiber name')
# -----------------------------------------------------------------------------
# Define DRS outputs keywords
# -----------------------------------------------------------------------------
KW_OUTPUT = KW_OUTPUT.copy(__NAME__)
KW_OUTPUT.set(key='DRSOUTID', comment='DRS output identification code')

# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
KW_DRS_QC = KW_DRS_QC.copy(__NAME__)
KW_DRS_QC.set(key='QCC_ALL', comment='All quality control passed')
KW_DRS_QC_VAL = KW_DRS_QC_VAL.copy(__NAME__)
KW_DRS_QC_VAL.set(key='QCC{0:03d}V', comment='Quality control measured value')
KW_DRS_QC_NAME = KW_DRS_QC_NAME.copy(__NAME__)
KW_DRS_QC_NAME.set(key='QCC{0:03d}N', comment='Quality control parameter name')
KW_DRS_QC_LOGIC = KW_DRS_QC_LOGIC.copy(__NAME__)
KW_DRS_QC_LOGIC.set(key='QCC{0:03d}L', comment='Quality control logic used')
KW_DRS_QC_PASS = KW_DRS_QC_PASS.copy(__NAME__)
KW_DRS_QC_PASS.set(key='QCC{0:03d}P', comment='Quality control param passed QC')

# -----------------------------------------------------------------------------
# Define preprocessing variables
# -----------------------------------------------------------------------------
# The shift in pixels so that image is at same location as engineering flat
KW_PPSHIFTX = KW_PPSHIFTX.copy(__NAME__)
KW_PPSHIFTX.set(key='DETOFFDX', comment='Pixel offset in x from readout lag')

KW_PPSHIFTY = KW_PPSHIFTY.copy(__NAME__)
KW_PPSHIFTY.set(key='DETOFFDY', comment='Pixel offset in y from readout lag')

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
KW_LOC_BCKGRD.set(key=root_loc + 'BCKGRD', comment='mean background [%]',
                  group='loc')

# Number of orders located
KW_LOC_NBO = KW_LOC_NBO.copy(__NAME__)
KW_LOC_NBO.set(key=root_loc + 'NBO', comment='nb orders localised',
               group='loc')

# fit degree for order centers
KW_LOC_DEG_C = KW_LOC_DEG_C.copy(__NAME__)
KW_LOC_DEG_C.set(key=root_loc + 'DEGCTR', comment='degree fit ctr ord',
                 group='loc')

# fit degree for order widths
KW_LOC_DEG_W = KW_LOC_DEG_W.copy(__NAME__)
KW_LOC_DEG_W.set(key=root_loc + 'DEGFWH', comment='degree fit width ord',
                 group='loc')

# Maximum flux in order
KW_LOC_MAXFLX = KW_LOC_MAXFLX.copy(__NAME__)
KW_LOC_MAXFLX.set(key=root_loc + 'FLXMAX', comment='max flux in order [ADU]',
                  group='loc')

# Maximum number of removed points allowed for location fit
KW_LOC_SMAXPTS_CTR = KW_LOC_SMAXPTS_CTR.copy(__NAME__)
KW_LOC_SMAXPTS_CTR.set(key=root_loc + 'CTRMAX', comment='max rm pts ctr',
                       group='loc')

# Maximum number of removed points allowed for width fit
KW_LOC_SMAXPTS_WID = KW_LOC_SMAXPTS_WID.copy(__NAME__)
KW_LOC_SMAXPTS_WID.set(key=root_loc + 'WIDMAX', comment='max rm pts width',
                       group='loc')

# Maximum rms allowed for location fit
KW_LOC_RMS_CTR = KW_LOC_RMS_CTR.copy(__NAME__)
KW_LOC_RMS_CTR.set(key=root_loc + 'RMSCTR', comment='max rms ctr',
                   group='loc')

# Maximum rms allowed for width fit (formally KW_LOC_rms_fwhm)
KW_LOC_RMS_WID = KW_LOC_RMS_WID.copy(__NAME__)
KW_LOC_RMS_WID.set(key=root_loc + 'RMSWID', comment='max rms width',
                   group='loc')

# Coeff center order
KW_LOC_CTR_COEFF = KW_LOC_CTR_COEFF.copy(__NAME__)
KW_LOC_CTR_COEFF.set(key=root_loc + 'CE{0:04d}', comment='Coeff center',
                     group='loc')

# Coeff width order
KW_LOC_WID_COEFF = KW_LOC_WID_COEFF.copy(__NAME__)
KW_LOC_WID_COEFF.set(key=root_loc + 'FW{0:04d}', comment='Coeff fwhm',
                     group='loc')

# -----------------------------------------------------------------------------
# Define shape variables
# -----------------------------------------------------------------------------
# Shape transform dx parameter
KW_SHAPE_DX = KW_SHAPE_DX.copy(__NAME__)
KW_SHAPE_DX.set(key='SHAPE_DX', comment='Shape transform dx parameter',
                group='shape')

# Shape transform dy parameter
KW_SHAPE_DY = KW_SHAPE_DY.copy(__NAME__)
KW_SHAPE_DY.set(key='SHAPE_DY', comment='Shape transform dy parameter',
                group='shape')

# Shape transform A parameter
KW_SHAPE_A = KW_SHAPE_A.copy(__NAME__)
KW_SHAPE_A.set(key='SHAPE_A', comment='Shape transform A parameter',
               group='shape')

# Shape transform B parameter
KW_SHAPE_B = KW_SHAPE_B.copy(__NAME__)
KW_SHAPE_B.set(key='SHAPE_B', comment='Shape transform B parameter',
               group='shape')

# Shape transform C parameter
KW_SHAPE_C = KW_SHAPE_C.copy(__NAME__)
KW_SHAPE_C.set(key='SHAPE_C', comment='Shape transform C parameter',
               group='shape')

# Shape transform D parameter
KW_SHAPE_D = KW_SHAPE_D.copy(__NAME__)
KW_SHAPE_D.set(key='SHAPE_D', comment='Shape transform D parameter',
               group='shape')

# -----------------------------------------------------------------------------
# Define extraction variables
# -----------------------------------------------------------------------------
# The extraction type (only added for E2DS files in extraction)
KW_EXT_TYPE = KW_EXT_TYPE.copy(__NAME__)
KW_EXT_TYPE.set(key='EXT_TYPE', comment='Extract type (E2DS or E2DSFF)')

# SNR calculated in extraction process (per order)
KW_EXT_SNR = KW_EXT_SNR.copy(__NAME__)
KW_EXT_SNR.set(key='EXTSN{0:03d}', comment='Extract: S_N order center')

# the start order for extraction
KW_EXT_START = KW_EXT_START.copy(__NAME__)
KW_EXT_START.set(key='EXTSTART', comment='Extract: Start order for extraction')

# the end order for extraction
KW_EXT_END = KW_EXT_END.copy(__NAME__)
KW_EXT_END.set(key='EXTEND', comment='Extract: End order for extraction')

# the upper bound for extraction of order
KW_EXT_RANGE1 = KW_EXT_RANGE1.copy(__NAME__)
KW_EXT_RANGE1.set(key='EXTR1', comment='Extract: width1 for order extraction')

# the lower bound for extraction of order
KW_EXT_RANGE2 = KW_EXT_RANGE2.copy(__NAME__)
KW_EXT_RANGE2.set(key='EXTR2', comment='Extract: width2 for order extraction')

# whether cosmics where rejected
KW_COSMIC = KW_COSMIC.copy(__NAME__)
KW_COSMIC.set(key='EXTCOS', comment='Extract: Whether cosmics were rejected')

# TODO: is blaze_size needed with sinc function?
# the blaze with used
KW_BLAZE_WID = KW_BLAZE_WID.copy(__NAME__)
KW_BLAZE_WID.set(key='BLAZEWID', comment='Extract: Blaze width used')

# TODO: is blaze_cut needed with sinc function?
# the blaze cut used
KW_BLAZE_CUT = KW_BLAZE_CUT.copy(__NAME__)
KW_BLAZE_CUT.set(key='BLAZECUT', comment='Extract: Blaze cut used')

# TODO: is blaze_deg needed with sinc function?
# the blaze degree used (to fit)
KW_BLAZE_DEG = KW_BLAZE_DEG.copy(__NAME__)
KW_BLAZE_DEG.set(key='BLAZEDEG', comment='Extract: Blaze fit degree used')

# The blaze sinc cut threshold used
KW_BLAZE_SCUT = KW_BLAZE_SCUT.copy(__NAME__)
KW_BLAZE_SCUT.set(key='BLAZSCUT', comment='Extract: Blaze sinc cut thres used')

# The blaze sinc sigma clip (rejection threshold) used
KW_BLAZE_SIGFIG = KW_BLAZE_SIGFIG.copy(__NAME__)
KW_BLAZE_SIGFIG.set(key='BLAZSIGF',
                    comment='Extract: Blaze sinc reject thres used')

# The blaze sinc bad percentile value used
KW_BLAZE_BPRCNTL = KW_BLAZE_BPRCNTL.copy(__NAME__)
KW_BLAZE_BPRCNTL.set(key='BLAZBPTL',
                     comment='Extract: Blaze sinc bad percentile used')

# The number of iterations used in the blaze sinc fit
KW_BLAZE_NITER = KW_BLAZE_NITER.copy(__NAME__)
KW_BLAZE_NITER.set(key='BLAZNITR', comment='Extract: Blaze sinc no. iters used')

# the cosmic cut criteria
KW_COSMIC_CUT = KW_COSMIC_CUT.copy(__NAME__)
KW_COSMIC_CUT.set(key='EXTCCUT', comment='Extract: cosmic cut criteria used')

# the cosmic threshold used
KW_COSMIC_THRES = KW_COSMIC_THRES.copy(__NAME__)
KW_COSMIC_THRES.set(key='EXTCTHRE', comment='Extract: cosmic cut thres used')

# the saturation QC limit
KW_SAT_QC = KW_SAT_QC.copy(__NAME__)
KW_SAT_QC.set(key='EXTSATQC', comment='Extract: saturation limit criteria')

# the max saturation level
KW_SAT_LEVEL = KW_SAT_LEVEL.copy(__NAME__)
KW_SAT_LEVEL.set(key='EXTSMAX', comment='Extract: maximum saturation level')

# the wave starting point used for s1d
KW_S1D_WAVESTART = KW_S1D_WAVESTART.copy(__NAME__)
KW_S1D_WAVESTART.set(key='S1DWAVE0', comment='Initial wavelength for s1d [nm]')

# the wave end point used for s1d
KW_S1D_WAVEEND = KW_S1D_WAVEEND.copy(__NAME__)
KW_S1D_WAVEEND.set(key='S1DWAVE1', comment='Final wavelength for s1d [nm]')

# the wave grid kind used for s1d (wave or velocity)
KW_S1D_KIND = KW_S1D_KIND.copy(__NAME__)
KW_S1D_KIND.set(key='S1DWAVEK', comment='Wave grid kind for s1d')

# the bin size for wave grid kind=wave
KW_S1D_BWAVE = KW_S1D_BWAVE.copy(__NAME__)
KW_S1D_BWAVE.set(key='S1DBWAVE',
                 comment='Bin size for wave grid constant in wavelength')

# the bin size for wave grid kind=velocity
KW_S1D_BVELO = KW_S1D_BVELO.copy(__NAME__)
KW_S1D_BVELO.set(key='S1DBVELO',
                 comment='Bin size for wave grid constant in velocity')

# the smooth size for the s1d
KW_S1D_SMOOTH = KW_S1D_SMOOTH.copy(__NAME__)
KW_S1D_SMOOTH.set(key='S1DSMOOT', comment='Smoothing scale for s1d edge mask')

# the blaze threshold used for the s1d
KW_S1D_BLAZET = KW_S1D_BLAZET.copy(__NAME__)
KW_S1D_BLAZET.set(key='S1DBLAZT', comment='Blaze threshold for s1d')

# the Right Ascension used to calculate the BERV
KW_BERVRA = KW_BERVRA.copy(__NAME__)
KW_BERVRA.set(key='BC_RA', comment='Right Ascension used to calc. BERV')

# the Declination used to calculate the BERV
KW_BERVDEC = KW_BERVDEC.copy(__NAME__)
KW_BERVDEC.set(key='BC_DEC', comment='Declination used to calc. BERV')

# the Gaia ID used to identify KW_BERV_POS_SOURCE for BERV calculation
KW_BERVGAIA_ID = KW_BERVGAIA_ID.copy(__NAME__)
KW_BERVGAIA_ID.set(key='BC_GAIA', comment='The Gaia ID used for BERV params')

# the OBJNAME used to identify KW_BERV_POS_SOURCE for BERV calculation
KW_BERVOBJNAME = KW_BERVOBJNAME.copy(__NAME__)
KW_BERVOBJNAME.set(key='BC_OBJNM', comment='The OBJNAME used for BERV params')

# the epoch (jd) used to calculate the BERV
KW_BERVEPOCH = KW_BERVEPOCH.copy(__NAME__)
KW_BERVEPOCH.set(key='BC_EPOCH', comment='Epoch [JD] used to calc. BERV')

# the pmra [mas/yr] used to calculate the BERV
KW_BERVPMRA = KW_BERVPMRA.copy(__NAME__)
KW_BERVPMRA.set(key='BC_PMRA', comment='PMRA [mas/yr] used to calc. BERV')

# the pmde [mas/yr] used to calculate the BERV
KW_BERVPMDE = KW_BERVPMDE.copy(__NAME__)
KW_BERVPMDE.set(key='BC_PMDE', comment='PMDE [mas/yr] used to calc. BERV')

# the parallax [mas] used to calculate the BERV
KW_BERVPLX = KW_BERVPLX.copy(__NAME__)
KW_BERVPLX.set(key='BC_PLX', comment='PLX [mas] used to calc. BERV')

# the rv [km/s] used to calculate the BERV
KW_BERVRV = KW_BERVRV.copy(__NAME__)
KW_BERVRV.set(key='BC_RV', comment='RV [km/s] used to calc. BERV')

# the source of the BERV star parameters (header or gaia)
KW_BERV_POS_SOURCE = KW_BERV_POS_SOURCE.copy(__NAME__)
KW_BERV_POS_SOURCE.set(key='BC_PSRCE', comment='Source of BERV star params')

# the Gaia G mag (if present) for the gaia query
KW_BERV_GAIA_GMAG = KW_BERV_GAIA_GMAG.copy(__NAME__)
KW_BERV_GAIA_GMAG.set(key='BC_GMAG', comment='Gaia G mag for BERV calc.')

# the Gaia BP mag (if present) for the gaia query
KW_BERV_GAIA_BPMAG = KW_BERV_GAIA_BPMAG.copy(__NAME__)
KW_BERV_GAIA_BPMAG.set(key='BC_BPMAG', comment='Gaia BP mag for BERV calc.')

# the Gaia RP mag (if present) for the gaia query
KW_BERV_GAIA_RPMAG = KW_BERV_GAIA_RPMAG.copy(__NAME__)
KW_BERV_GAIA_RPMAG.set(key='BC_RPMAG', comment='Gaia RP mag for BERV calc.')

# the Gaia G mag limit used for the gaia query
KW_BERV_GAIA_MAGLIM = KW_BERV_GAIA_MAGLIM.copy(__NAME__)
KW_BERV_GAIA_MAGLIM.set(key='BC_MAG_L', comment='Gaia mag lim for BERV calc.')

# the Gaia parallax limit used the gaia query
KW_BERV_GAIA_PLXLIM = KW_BERV_GAIA_PLXLIM.copy(__NAME__)
KW_BERV_GAIA_PLXLIM.set(key='BC_PLX_L', comment='Gaia plx lim for BERV calc.')

# the observatory latitude used to calculate the BERV
KW_BERVLAT = KW_BERVLAT.copy(__NAME__)
KW_BERVLAT.set(key='BC_LAT', comment='OBS Latitude [deg] used to calc. BERV')

# the observatory longitude used to calculate the BERV
KW_BERVLONG = KW_BERVLONG.copy(__NAME__)
KW_BERVLONG.set(key='BC_LONG', comment='OBS Longitude [deg] used to calc. BERV')

# the observatory altitude used to calculate the BERV
KW_BERVALT = KW_BERVALT.copy(__NAME__)
KW_BERVALT.set(key='BC_ALT', comment='OBS Altitude [m] used to calc. BERV')

# the BERV calculated with KW_BERVSOURCE
KW_BERV = KW_BERV.copy(__NAME__)
KW_BERV.set(key='BERV', comment='Barycentric Velocity calc. in BERVSRCE [km/s]',
            datatype=float)

# the Barycenter Julian date calculate with KW_BERVSOURCE
KW_BJD = KW_BJD.copy(__NAME__)
KW_BJD.set(key='BJD', comment='Barycentric Julian data calc. in BERVSRCE',
           datatype=float)

# the maximum BERV found across 1 year (with KW_BERVSOURCE)
KW_BERVMAX = KW_BERVMAX.copy(__NAME__)
KW_BERVMAX.set(key='BERVMAX', comment='Max BERV 1 yr calc. in BERVSRCE [km/s]',
               datatype=float)

# the derivative of the BERV (BERV at time + 1s - BERV)
KW_DBERV = KW_DBERV.copy(__NAME__)
KW_DBERV.set(key='DBERV', comment='Deviation in BERV in BERVSRCE [km/s/s]',
             datatype=float)

# the source of the calculated BERV parameters
KW_BERVSOURCE = KW_BERVSOURCE.copy(__NAME__)
KW_BERVSOURCE.set(key='BERVSRCE', comment='How BERV was calculated',
                  datatype=str)

# the BERV calculated with the estimate
KW_BERV_EST = KW_BERV_EST.copy(__NAME__)
KW_BERV_EST.set(key='BERV_EST', comment='Barycentric Velocity estimate [km/s]',
                datatype=float)

# the Barycenter Julian date calculated with the estimate
KW_BJD_EST = KW_BJD_EST.copy(__NAME__)
KW_BJD_EST.set(key='BJD_EST', comment='Barycentric Julian data estimate',
               datatype=float)

# the maximum BERV found across 1 year (calculated with estimate)
KW_BERVMAX_EST = KW_BERVMAX_EST.copy(__NAME__)
KW_BERVMAX_EST.set(key='BERVMAXE', comment='Max BERV 1 yr estimate [km/s]',
                   datatype=float)

# the derivative of the BERV (BERV at time + 1s - BERV)
KW_DBERV_EST = KW_DBERV_EST.copy(__NAME__)
KW_DBERV_EST.set(key='DBERVE',
                 comment='Deviation in BERV estimate [km/s/s]',
                 datatype=float)

# the actual jd time used to calculate the BERV
KW_BERV_OBSTIME = KW_BERV_OBSTIME.copy(__NAME__)
KW_BERV_OBSTIME.set(key='BERVOBST', comment='BERV observation time used [days]',
                    datatype=float)

# the method used to obtain the berv obs time
KW_BERV_OBSTIME_METHOD = KW_BERV_OBSTIME_METHOD.copy(__NAME__)
KW_BERV_OBSTIME_METHOD.set(key='BERVOBSM',
                           comment='BERV method used to calc observation time',
                           datatype=str)

# -----------------------------------------------------------------------------
# Define leakage variables
# -----------------------------------------------------------------------------
# Define whether leak correction has been done
KW_LEAK_CORR = KW_LEAK_CORR.copy(__NAME__)
KW_LEAK_CORR.set(key='LEAKCORR',
                 comment='Whether DARK_FP leakage correction has been done',
                 datatype=int)

# Define the background percentile used for correcting leakage
KW_LEAK_BP_U = KW_LEAK_BP_U.copy(__NAME__)
KW_LEAK_BP_U.set(key='LEAK_BPU', datatype=float,
                 comment='LEAK bckgrd percentile used for leakage corr')

# Define the normalisation percentile used for correcting leakage
KW_LEAK_NP_U = KW_LEAK_NP_U.copy(__NAME__)
KW_LEAK_NP_U.set(key='LEAK_NPU', datatype=float,
                 comment='LEAK norm percentile used for leakage corr')

# Define the e-width smoothing used for correcting leakage master
KW_LEAK_WSMOOTH = KW_LEAK_WSMOOTH.copy(__NAME__)
KW_LEAK_WSMOOTH.set(key='LEAKMWSM', datatype=float,
                    comment='LEAKM e-width smoothing used for leak master corr')

# Define the kernel size used for correcting leakage master
KW_LEAK_KERSIZE = KW_LEAK_KERSIZE.copy(__NAME__)
KW_LEAK_KERSIZE.set(key='LEAKMKSZ', datatype=float,
                    comment='LEAKM kernel size used for leak master corr')

# Define the lower bound percentile used for correcting leakage
KW_LEAK_LP_U = KW_LEAK_LP_U.copy(__NAME__)
KW_LEAK_LP_U.set(key='LEAK_LPU', datatype=float,
                 comment='LEAK lower bound percentile used for leakage corr')

# Define the upper bound percentile used for correcting leakage
KW_LEAK_UP_U = KW_LEAK_UP_U.copy(__NAME__)
KW_LEAK_UP_U.set(key='LEAK_UPU', datatype=float,
                 comment='LEAK upper bound percentile used for leakage corr')

# Define the bad ratio offset limit used for correcting leakage
KW_LEAK_BADR_U = KW_LEAK_BADR_U.copy(__NAME__)
KW_LEAK_BADR_U.set(key='LEAKBADR', datatype=float,
                   comment='LEAK bad ratio offset limit used for leakage corr')

# -----------------------------------------------------------------------------
# Define wave variables
# -----------------------------------------------------------------------------
# Number of orders in wave image
KW_WAVE_NBO = KW_WAVE_NBO.copy(__NAME__)
KW_WAVE_NBO.set(key='WAVEORDN', comment='nb orders in total',
                parent=None, group='wave')

# fit degree for wave solution
KW_WAVE_DEG = KW_WAVE_DEG.copy(__NAME__)
KW_WAVE_DEG.set(key='WAVEDEGN', comment='degree of wave polyn fit',
                parent=None, group='wave')

# the wave file used
KW_WAVEFILE = KW_WAVEFILE.copy(__NAME__)
KW_WAVEFILE.set(key='WAVEFILE', comment='Wavelength solution file used',
                parent=None, group='wave')

# the wave file mid exptime [mjd]
KW_WAVETIME = KW_WAVETIME.copy(__NAME__)
KW_WAVETIME.set(key='WAVETIME', comment='Wavelength solution mid exptime',
                parent=None, group='wave')

# the wave source of the wave file used
KW_WAVESOURCE = KW_WAVESOURCE.copy(__NAME__)
KW_WAVESOURCE.set(key='WAVESOUR', comment='Source of the wave solution used.',
                  parent=None, group='wave')

# the wave coefficients
KW_WAVECOEFFS = KW_WAVECOEFFS.copy(__NAME__)
KW_WAVECOEFFS.set(key='WAVE{0:04d}', comment='Wavelength coefficients',
                  parent=None, group='wave')

# the initial wave file used for wave solution
KW_INIT_WAVE = KW_INIT_WAVE.copy(__NAME__)
KW_INIT_WAVE.set(key='WAVEINIT', comment='Initial wavelength solution used',
                 parent=None, group='wave')

# -----------------------------------------------------------------------------
# the fit degree for wave solution used
KW_WAVE_FITDEG = KW_WAVE_FITDEG.copy(__NAME__)
KW_WAVE_FITDEG.set(key='WAVE_DEG', comment='fit degree used for wave sol',
                   parent='WAVE_FIT_DEGREE', group='wave')

# the mode used to calculate the hc wave solution
KW_WAVE_MODE_HC = KW_WAVE_MODE_HC.copy(__NAME__)
KW_WAVE_MODE_HC.set(key='WAVHCMOD', comment='mode used to calc hc wave sol',
                    parent='WAVE_MODE_HC', group='wave')

# the mode used to calculate the fp wave solution
KW_WAVE_MODE_FP = KW_WAVE_MODE_FP.copy(__NAME__)
KW_WAVE_MODE_FP.set(key='WAVFPMOD', comment='mode used to calc fp wave sol',
                    parent='WAVE_MODE_FP', group='wave')

# the echelle number of the first order used
KW_WAVE_ECHELLE_START = KW_WAVE_ECHELLE_START.copy(__NAME__)
KW_WAVE_ECHELLE_START.set(key='WAV_ECH0', comment='Echelle no. of first order',
                          parent='WAVE_T_ORDER_START', group='wave')

# the width of the box for fitting hc lines used
KW_WAVE_HCG_WSIZE = KW_WAVE_HCG_WSIZE.copy(__NAME__)
KW_WAVE_HCG_WSIZE.set(key='WAVHGSIZ', comment='HC Gauss peak fit box width',
                      parent='WAVE_HC_FITBOX_SIZE', group='wave')

# the sigma above local rms for fitting hc lines used
KW_WAVE_HCG_SIGPEAK = KW_WAVE_HCG_SIGPEAK.copy(__NAME__)
KW_WAVE_HCG_SIGPEAK.set(key='WAVHGSPK',
                        comment='HC Gauss peak fit rms sig peak',
                        parent='WAVE_HC_FITBOX_SIGMA', group='wave')

# the fit degree for the gaussian peak fitting used
KW_WAVE_HCG_GFITMODE = KW_WAVE_HCG_GFITMODE.copy(__NAME__)
KW_WAVE_HCG_GFITMODE.set(key='WAVHGGFM',
                         comment='HC Gauss peak fit, fit degree',
                         parent='WAVE_HC_FITBOX_GFIT_DEG', group='wave')

# the min rms for gaussian peak fitting used
KW_WAVE_HCG_FB_RMSMIN = KW_WAVE_HCG_FB_RMSMIN.copy(__NAME__)
KW_WAVE_HCG_FB_RMSMIN.set(key='WAVHGRMN',
                          comment='HC Gauss peak fit, min rms for peak',
                          parent='WAVE_HC_FITBOX_RMS_DEVMIN', group='wave')

# the max rms for gaussian peak fitting used
KW_WAVE_HCG_FB_RMSMAX = KW_WAVE_HCG_FB_RMSMAX.copy(__NAME__)
KW_WAVE_HCG_FB_RMSMAX.set(key='WAVHGRMX',
                          comment='HC Gauss peak fit, max rms for peak',
                          parent='WAVE_HC_FITBOX_RMS_DEVMAX', group='wave')

# the min e-width of the line for gaussian peak fitting used
KW_WAVE_HCG_EWMIN = KW_WAVE_HCG_EWMIN.copy(__NAME__)
KW_WAVE_HCG_EWMIN.set(key='WAVHGEW0', comment='HC Gauss peak fit, e-width min',
                      parent='WAVE_HC_FITBOX_EWMIN', group='wave')

# the min e-width of the line for gaussian peak fitting used
KW_WAVE_HCG_EWMAX = KW_WAVE_HCG_EWMAX.copy(__NAME__)
KW_WAVE_HCG_EWMAX.set(key='WAVHGEW1', comment='HC Gauss peak fit, e-width max',
                      parent='WAVE_HC_FITBOX_EWMAX', group='wave')

# the filename for the HC line list generated
KW_WAVE_HCLL_FILE = KW_WAVE_HCLL_FILE.copy(__NAME__)
KW_WAVE_HCLL_FILE.set(key='WAVEHCLL', comment='HC line list file generated',
                      parent=None, group='wave')

# the number of bright lines to used in triplet fit
KW_WAVE_TRP_NBRIGHT = KW_WAVE_TRP_NBRIGHT.copy(__NAME__)
KW_WAVE_TRP_NBRIGHT.set(key='WAVTNBRI',
                        comment='Triplet fit - no. bright lines used',
                        parent='WAVE_HC_NMAX_BRIGHT', group='wave')

# the number of iterations done in triplet fit
KW_WAVE_TRP_NITER = KW_WAVE_TRP_NITER.copy(__NAME__)
KW_WAVE_TRP_NITER.set(key='WAVTNITR',
                      comment='Triplet fit - no. iterations used',
                      parent='WAVE_HC_NITER_FIT_TRIPLET', group='wave')

# the max distance between catalog line and initial guess line in triplet fit
KW_WAVE_TRP_CATGDIST = KW_WAVE_TRP_CATGDIST.copy(__NAME__)
KW_WAVE_TRP_CATGDIST.set(key='WAVTCATD',
                         comment='Triplet fit - max dist btwn line cat & guess',
                         parent='WAVE_HC_MAX_DV_CAT_GUESS', group='wave')

# the fit degree for triplet fit
KW_WAVE_TRP_FITDEG = KW_WAVE_TRP_FITDEG.copy(__NAME__)
KW_WAVE_TRP_FITDEG.set(key='WAVTFDEG', comment='Triplet fit - fit degree',
                       parent='WAVE_HC_TFIT_DEG', group='wave')

# the minimum number of lines required per order in triplet fit
KW_WAVE_TRP_MIN_NLINES = KW_WAVE_TRP_MIN_NLINES.copy(__NAME__)
KW_WAVE_TRP_MIN_NLINES.set(key='WAVTMINL',
                           comment='Triplet fit - min no. lines req. per order',
                           parent='WAVE_HC_TFIT_MINNUM_LINES', group='wave')

# the total number of lines required in triplet fit
KW_WAVE_TRP_TOT_NLINES = KW_WAVE_TRP_TOT_NLINES.copy(__NAME__)
KW_WAVE_TRP_TOT_NLINES.set(key='WAVTTOTL',
                           comment='Triplet fit - total no. lines required',
                           parent='WAVE_HC_TFIT_MINTOT_LINES', group='wave')

# the degree(s) of fit to ensure continuity in triplet fit
KW_WAVE_TRP_ORDER_FITCONT = KW_WAVE_TRP_ORDER_FITCONT.copy(__NAME__)
KW_WAVE_TRP_ORDER_FITCONT.set(key='WAVTO{0:03d}',
                              comment='Triplet fit - order continuity fit',
                              parent='WAVE_HC_TFIT_ORDER_FIT_CONT', group='wave')

# the iteration number for sigma clip in triplet fit
KW_WAVE_TRP_SCLIPNUM = KW_WAVE_TRP_SCLIPNUM.copy(__NAME__)
KW_WAVE_TRP_SCLIPNUM.set(key='WAVT_SCN',
                         comment='Triplet fit - iter no. for sig clip',
                         parent='WAVE_HC_TFIT_SIGCLIP_NUM', group='wave')

# the sigma clip threshold in triplet fit
KW_WAVE_TRP_SCLIPTHRES = KW_WAVE_TRP_SCLIPTHRES.copy(__NAME__)
KW_WAVE_TRP_SCLIPTHRES.set(key='WAVT_SCT',
                           comment='Triplet fit - sig clip threshold',
                           parent='WAVE_HC_TFIT_SIGCLIP_THRES', group='wave')

# the distance away in dv to reject order triplet in triplet fit
KW_WAVE_TRP_DVCUTORD = KW_WAVE_TRP_DVCUTORD.copy(__NAME__)
KW_WAVE_TRP_DVCUTORD.set(key='WAVT_DVO',
                         comment='Triplet fit - dist in dv per order to reject',
                         parent='WAVE_HC_TFIT_DVCUT_ORDER', group='wave')

# the distance away in dv to reject all triplet in triplet fit
KW_WAVE_TRP_DVCUTALL = KW_WAVE_TRP_DVCUTALL.copy(__NAME__)
KW_WAVE_TRP_DVCUTALL.set(key='WAVT_DVA',
                         comment='Triplet fit - dist in dv all to reject',
                         parent='WAVE_HC_TFIT_DVCUT_ALL', group='wave')

# the wave resolution map dimensions
KW_WAVE_RES_MAPSIZE = KW_WAVE_RES_MAPSIZE.copy(__NAME__)
KW_WAVE_RES_MAPSIZE.set(key='WAVRE{0:03d}',
                        comment='Wave res map - map dimensions',
                        parent='WAVE_HC_RESMAP_SIZE', group='wave')

# the width of the box for wave resolution map
KW_WAVE_RES_WSIZE = KW_WAVE_RES_WSIZE.copy(__NAME__)
KW_WAVE_RES_WSIZE.set(key='WAVRSIZE',
                      comment='Wave res map - width of box',
                      parent='WAVE_HC_FITBOX_SIZE', group='wave')

# the max deviation in rms allowed in wave resolution map
KW_WAVE_RES_MAXDEVTHRES = KW_WAVE_RES_MAXDEVTHRES.copy(__NAME__)
KW_WAVE_RES_MAXDEVTHRES.set(key='WAVRDEV',
                            comment='Wave res map - max dev in rms allowed',
                            parent='WAVE_HC_RES_MAXDEV_THRES', group='wave')

# the littrow start order used for HC
KW_WAVE_LIT_START_1 = KW_WAVE_LIT_START_1.copy(__NAME__)
KW_WAVE_LIT_START_1.set(key='WAVL1_ST', comment='Littrow HC - start value',
                        parent=['WAVE_LITTROW_ORDER_INIT_1',
                                'WAVE_LITTROW_ORDER_INIT_2'],
                        group='wave')

# the littrow end order used for HC
KW_WAVE_LIT_END_1 = KW_WAVE_LIT_END_1.copy(__NAME__)
KW_WAVE_LIT_END_1.set(key='WAVL1_EN', comment='Littrow HC - end value',
                      parent=['WAVE_LITTROW_ORDER_FINAL_1',
                              'WAVE_LITTROW_ORDER_FINAL_2'],
                      group='wave')

# the orders removed from the littrow test
KW_WAVE_LIT_RORDERS = KW_WAVE_LIT_RORDERS.copy(__NAME__)
KW_WAVE_LIT_RORDERS.set(key='WAVLR{0:03d}', comment='Littrow - removed orders',
                        parent='WAVE_LITTROW_REMOVE_ORDERS', group='wave')

# the littrow order initial value used for HC
KW_WAVE_LIT_ORDER_INIT_1 = KW_WAVE_LIT_ORDER_INIT_1.copy(__NAME__)
KW_WAVE_LIT_ORDER_INIT_1.set(key='WAVL1OIN',
                             comment='Littrow HC - order init value',
                             parent='WAVE_LITTROW_ORDER_INIT_1', group='wave')

# the littrow order start value used for HC
KW_WAVE_LIT_ORDER_START_1 = KW_WAVE_LIT_ORDER_START_1.copy(__NAME__)
KW_WAVE_LIT_ORDER_START_1.set(key='WAVL1OST',
                              comment='Littrow HC - order start value',
                              parent='WAVE_N_ORD_START', group='wave')

# the littrow order end value used for HC
KW_WAVE_LIT_ORDER_END_1 = KW_WAVE_LIT_ORDER_END_1.copy(__NAME__)
KW_WAVE_LIT_ORDER_END_1.set(key='WAVL1OEN',
                            comment='Littrow HC - order end value',
                            parent='WAVE_N_ORD_FINAL', group='wave')

# the littrow x cut step value used for HC
KW_WAVE_LITT_XCUTSTEP_1 = KW_WAVE_LITT_XCUTSTEP_1.copy(__NAME__)
KW_WAVE_LITT_XCUTSTEP_1.set(key='WAVL1XCT',
                            comment='Littrow HC - x cut step value',
                            parent='WAVE_LITTROW_CUT_STEP_1', group='wave')

# the littrow fit degree value used for HC
KW_WAVE_LITT_FITDEG_1 = KW_WAVE_LITT_FITDEG_1.copy(__NAME__)
KW_WAVE_LITT_FITDEG_1.set(key='WAVL1FDG',
                          comment='Littrow HC - littrow fit degree',
                          parent='WAVE_LITTROW_FIG_DEG_1', group='wave')

# the littrow extrapolation fit degree value used for HC
KW_WAVE_LITT_EXT_FITDEG_1 = KW_WAVE_LITT_EXT_FITDEG_1.copy(__NAME__)
KW_WAVE_LITT_EXT_FITDEG_1.set(key='WAVL1EDG',
                              comment='Littrow HC - extrapolation fit degree',
                              parent='WAVE_LITTROW_EXT_ORDER_FIT_DEG',
                              group='wave')

# the littrow extrapolation start order value used for HC
KW_WAVE_LITT_EXT_ORD_START_1 = KW_WAVE_LITT_EXT_ORD_START_1.copy(__NAME__)
KW_WAVE_LITT_EXT_ORD_START_1.set(key='WAVL1EST',
                                 comment='Littrow HC - extrap start order',
                                 parent='WAVE_LITTROW_ORDER_INIT_1',
                                 group='wave')

# the first order used for FP wave sol improvement
KW_WFP_ORD_START = KW_WFP_ORD_START.copy(__NAME__)
KW_WFP_ORD_START.set(key='WFP_ORD0',
                     comment='First order used for FP wave sol.',
                     parent='WAVE_N_ORD_START', group='wave')

# the last order used for FP wave sol improvement
KW_WFP_ORD_FINAL = KW_WFP_ORD_FINAL.copy(__NAME__)
KW_WFP_ORD_FINAL.set(key='WFP_ORD1',
                     comment='Last order used for FP wave sol.',
                     parent='WAVE_N_ORD_FINAL', group='wave')

# the blaze threshold used for FP wave sol improvement
KW_WFP_BLZ_THRES = KW_WFP_BLZ_THRES.copy(__NAME__)
KW_WFP_BLZ_THRES.set(key='WFPBLZTH',
                     comment='Blaze threshold used for FP wave sol.',
                     parent='WAVE_FP_BLAZE_THRES', group='wave')

# the minimum fp peak pixel sep used for FP wave sol improvement
KW_WFP_XDIFF_MIN = KW_WFP_XDIFF_MIN.copy(__NAME__)
KW_WFP_XDIFF_MIN.set(key='WFPXDIF0',
                     comment='Min fp peak pixel sep for FP wave sol.',
                     parent='WAVE_FP_XDIF_MIN', group='wave')

# the maximum fp peak pixel sep used for FP wave sol improvement
KW_WFP_XDIFF_MAX = KW_WFP_XDIFF_MAX.copy(__NAME__)
KW_WFP_XDIFF_MAX.set(key='WFPXDIF1',
                     comment='Max fp peak pixel sep for FP wave sol.',
                     parent='WAVE_FP_XDIF_MAX', group='wave')

# the initial value of the FP effective cavity width used
KW_WFP_DOPD0 = KW_WFP_DOPD0.copy(__NAME__)
KW_WFP_DOPD0.set(key='WFPDOPD0',
                 comment='initial value of Fp effective cavity width',
                 parent='WAVE_FP_DOPD0', group='wave')

# the  maximum fraction wavelength offset btwn xmatch fp peaks used
KW_WFP_LL_OFFSET = KW_WFP_LL_OFFSET.copy(__NAME__)
KW_WFP_LL_OFFSET.set(key='WFPLLOFF',
                     comment='max frac. wavelength offset btwn fp peaks',
                     parent='WAVE_FP_LL_OFFSET', group='wave')

# the max dv to keep hc lines used
KW_WFP_DVMAX = KW_WFP_DVMAX.copy(__NAME__)
KW_WFP_DVMAX.set(key='WFPDVMAX',
                 comment='max dv to kee[ hc lines for fp wave sol.',
                 parent='WAVE_FP_DV_MAX', group='wave')

# the used polynomial fit degree (to fit wave solution)
KW_WFP_LLFITDEG = KW_WFP_LLFITDEG.copy(__NAME__)
KW_WFP_LLFITDEG.set(key='WFPLLDEG',
                    comment='Used poly fit degree for fp wave sol.',
                    parent='WAVE_FP_LL_DEGR_FIT', group='wave')

# whether the cavity file was updated
KW_WFP_UPDATECAV = KW_WFP_UPDATECAV.copy(__NAME__)
KW_WFP_UPDATECAV.set(key='WFPUPCAV',
                     comment='Whether wave sol. was used to update cav file',
                     parent='WAVE_FP_UPDATE_CAVITY', group='wave')

# the mode used to fit the FP cavity
KW_WFP_FPCAV_MODE = KW_WFP_FPCAV_MODE.copy(__NAME__)
KW_WFP_FPCAV_MODE.set(key='WFPCAVMO',
                      comment='The mode used to fit the FP cavity',
                      parent='WAVE_FP_CAVFIT_MODE', group='wave')

# the mode used to fit the wavelength
KW_WFP_LLFIT_MODE = KW_WFP_LLFIT_MODE.copy(__NAME__)
KW_WFP_LLFIT_MODE.set(key='WFPLLFMO',
                      comment='The mode used to fit the wavelength sol.',
                      parent='WAVE_FP_LLFIT_MODE', group='wave')

# the minimum instrumental error used
KW_WFP_ERRX_MIN = KW_WFP_ERRX_MIN.copy(__NAME__)
KW_WFP_ERRX_MIN.set(key='WFPERRXM',
                    comment='The minimum instrumental error used for wave sol.',
                    parent='WAVE_FP_ERRX_MIN', group='wave')

# the max rms for the wave sol sig clip
KW_WFP_MAXLL_FIT_RMS = KW_WFP_MAXLL_FIT_RMS.copy(__NAME__)
KW_WFP_MAXLL_FIT_RMS.set(key='WFPMAXLL',
                         comment='The max rms for the FP wave sol sig cut',
                         parent='WAVE_FP_MAX_LLFIT_RMS', group='wave')

# the echelle number used for the first order
KW_WFP_T_ORD_START = KW_WFP_T_ORD_START.copy(__NAME__)
KW_WFP_T_ORD_START.set(key='WFPTORD',
                       comment='The echelle number of order 0 (fp wave sol.)',
                       parent='WAVE_T_ORDER_START', group='wave')

# the weight below which fp lines are rejected
KW_WFP_WEI_THRES = KW_WFP_WEI_THRES.copy(__NAME__)
KW_WFP_WEI_THRES.set(key='WFPWTHRE',
                     comment='The weight below which FP lines are rejected',
                     parent='WAVE_FP_WEIGHT_THRES', group='wave')

# the polynomial degree fit order used for fitting the fp cavity
KW_WFP_CAVFIT_DEG = KW_WFP_CAVFIT_DEG.copy(__NAME__)
KW_WFP_CAVFIT_DEG.set(key='WFPCVFIT',
                      comment='The fit degree used for fitting the fp cavity',
                      parent='WAVE_FP_CAVFIT_DEG', group='wave')

# the largest jump in fp that was allowed
KW_WFP_LARGE_JUMP = KW_WFP_LARGE_JUMP.copy(__NAME__)
KW_WFP_LARGE_JUMP.set(key='WFPLJUMP',
                      comment='The largest jump in fp that is allowed',
                      parent='WAVE_FP_LARGE_JUMP', group='wave')

# the index to start crossmatching fps at
KW_WFP_CM_INDX = KW_WFP_CM_INDX.copy(__NAME__)
KW_WFP_CM_INDX.set(key='WFPCMIND',
                   comment='The index to start crossmatch at',
                   parent='WAVE_FP_CM_IND', group='wave')

# the FP widths used for each order (1D list)
KW_WFP_WIDUSED = KW_WFP_WIDUSED.copy(__NAME__)
KW_WFP_WIDUSED.set(key='WFPWD{0:03d}',
                   comment='The FP width (peak to peak) used for each order',
                   group='wave')

# the percentile to normalise the FP flux per order used
KW_WFP_NPERCENT = KW_WFP_NPERCENT.copy(__NAME__)
KW_WFP_NPERCENT.set(key='WFPNPRCT',
                    comment='WAVE FP percentile thres to norm FP flux used',
                    parent='WAVE_FP_NORM_PERCENTILE', group='wave')

# the normalised limited used to detect FP peaks
KW_WFP_LIMIT = KW_WFP_LIMIT.copy(__NAME__)
KW_WFP_LIMIT.set(key='WFPNLIMT',
                 comment='WAVE FP norm limit to detect FP peaks used',
                 parent='WAVE_FP_PEAK_LIM', group='wave')

# the normalised cut width for large peaks used
KW_WFP_CUTWIDTH = KW_WFP_CUTWIDTH.copy(__NAME__)
KW_WFP_CUTWIDTH.set(key='WFPCUTWD',
                    comment='Normalised cut width used for large FP peaks',
                    parent='WAVE_FP_P2P_WIDTH_CUT', group='wave')

# Wavelength solution for fiber C that is is source of the WFP keys
KW_WFP_FILE = KW_WFP_FILE.copy(__NAME__)
KW_WFP_FILE.set(key='WFP_FILE', comment='WFP source file',
                parent=None, group='wave')

# drift of the FP file used for the wavelength solution
KW_WFP_DRIFT = KW_WFP_DRIFT.copy(__NAME__)
KW_WFP_DRIFT.set(key='WFPDRIFT',
                 comment='Wavelength sol absolute CCF FP Drift [km/s]',
                 parent=None, group='wave')

# FWHM of the wave FP file CCF
KW_WFP_FWHM = KW_WFP_FWHM.copy(__NAME__)
KW_WFP_FWHM.set(key='WFPFWHM', comment='FWHM of wave sol FP CCF [km/s]',
                parent=None, group='wave')

# Contrast of the wave FP file CCF
KW_WFP_CONTRAST = KW_WFP_CONTRAST.copy(__NAME__)
KW_WFP_CONTRAST.set(key='WFPCONT', comment='wave sol FP Contrast of CCF (%)',
                    parent=None, group='wave')

# Mask for the wave FP file CCF
KW_WFP_MASK = KW_WFP_MASK.copy(__NAME__)
KW_WFP_MASK.set(key='WFPMASK', comment='wave sol FP Mask filename',
                parent='WAVE_CCF_MASK', group='wave')

# Number of lines for the wave FP file CCF
KW_WFP_LINES = KW_WFP_LINES.copy(__NAME__)
KW_WFP_LINES.set(key='WFPLINE', comment='wave sol FP nbr of lines used',
                 parent=None, group='wave')

# Target RV for the wave FP file CCF
KW_WFP_TARG_RV = KW_WFP_TARG_RV.copy(__NAME__)
KW_WFP_TARG_RV.set(key='WFPTRV', comment='wave sol FP target RV [km/s]',
                   parent='WAVE_CCF_TARGET_RV', group='wave')

# Width for the wave FP file CCF
KW_WFP_WIDTH = KW_WFP_WIDTH.copy(__NAME__)
KW_WFP_WIDTH.set(key='WFPWIDTH', comment='wave sol FP CCF width [km/s]',
                 parent='WAVE_CCF_WIDTH', group='wave')

# Step for the wave FP file CCF
KW_WFP_STEP = KW_WFP_STEP.copy(__NAME__)
KW_WFP_STEP.set(key='WFPSTEP', comment='wave sol FP CCF step [km/s]',
                parent='WAVE_CCF_STEP', group='wave')

# The sigdet used for FP file CCF
KW_WFP_SIGDET = KW_WFP_SIGDET.copy(__NAME__)
KW_WFP_SIGDET.set(key='WFPCSDET', comment='wave sol FP CCF sigdet used',
                  parent='WAVE_CCF_NOISE_SIGDET', group='wave')

# The boxsize used for FP file CCF
KW_WFP_BOXSIZE = KW_WFP_BOXSIZE.copy(__NAME__)
KW_WFP_BOXSIZE.set(key='WFPCBSZ', comment='wave sol FP CCF boxsize used',
                   parent='WAVE_CCF_NOISE_BOXSIZE', group='wave')

# The max flux used for the FP file CCF
KW_WFP_MAXFLUX = KW_WFP_MAXFLUX.copy(__NAME__)
KW_WFP_MAXFLUX.set(key='WFPCMFLX', comment='wave sol FP CCF max flux used',
                   parent='CCF_N_ORD_MAX', group='wave')

# The det noise used for the FP file CCF
KW_WFP_DETNOISE = KW_WFP_DETNOISE.copy(__NAME__)
KW_WFP_DETNOISE.set(key='WFPCDETN', comment='wave sol FP CCF det noise used',
                    parent='WAVE_CCF_DETNOISE', group='wave')

# the highest order used for the FP file CCF
KW_WFP_NMAX = KW_WFP_NMAX.copy(__NAME__)
KW_WFP_NMAX.set(key='WFPCNMAX', comment='wave sol FP CCF highest order used',
                parent='WAVE_CCF_N_ORD_MAX', group='wave')

# The weight of the CCF mask (if 1 force all weights equal) used for FP CCF
KW_WFP_MASKMIN = KW_WFP_MASKMIN.copy(__NAME__)
KW_WFP_MASKMIN.set(key='WFPCMMIN', comment='wave sol FP CCF mask weight used',
                   parent='WAVE_CCF_MASK_MIN_WEIGHT', group='wave')

# The width of the CCF mask template line (if 0 use natural) used for FP CCF
KW_WFP_MASKWID = KW_WFP_MASKWID.copy(__NAME__)
KW_WFP_MASKWID.set(key='WFPCMWID', comment='wave sol FP CCF mask width used',
                   parent='WAVE_CCF_MASK_WIDTH', group='wave')

# The units of the input CCF mask (converted to nm in code)
KW_WFP_MASKUNITS = KW_WFP_MASKUNITS.copy(__NAME__)
KW_WFP_MASKUNITS.set(key='WFPCMUNT', comment='wave sol FP CCF mask units used',
                     parent='WAVE_CCF_MASK_UNITS', group='wave')

# number of iterations for convergence used in wave night (hc)
KW_WNT_NITER1 = KW_WNT_NITER1.copy(__NAME__)
KW_WNT_NITER1.set(key='WNTNITER', comment='wave night hc n iterations used',
                  parent='WAVE_NIGHT_NITERATIONS1', group='wave')

# number of iterations for convergence used in wave night (fp)
KW_WNT_NITER21 = KW_WNT_NITER2.copy(__NAME__)
KW_WNT_NITER2.set(key='WNTNITER', comment='wave night fp n iterations used',
                  parent='WAVE_NIGHT_NITERATIONS2', group='wave')

# starting point for the cavity corrections used in wave night
KW_WNT_DCAVITY = KW_WNT_DCAVITY.copy(__NAME__)
KW_WNT_DCAVITY.set(key='WNTDCVTY',
                   comment='wave night starting point for cavity corr used',
                   parent='WAVE_NIGHT_DCAVITY', group='wave')

# source fiber for the cavity correction
KW_WNT_DCAVSRCE = KW_WNT_DCAVSRCE.copy(__NAME__)
KW_WNT_DCAVSRCE.set(key='WNTDCVSR',
                    comment='wave night source fiber used for cavity corr',
                    group='wave')

# define the sigma clip value to remove bad hc lines used
KW_WNT_HCSIGCLIP = KW_WNT_HCSIGCLIP.copy(__NAME__)
KW_WNT_HCSIGCLIP.set(key='WNTHCSIG', comment='wave night hc sig clip used',
                     group='wave', parent='WAVE_NIGHT_HC_SIGCLIP')

# median absolute deviation cut off used
KW_WNT_MADLIMIT = KW_WNT_MADLIMIT.copy(__NAME__)
KW_WNT_MADLIMIT.set(key='WNT_MADL',
                    comment='wave night med abs dev cut off used',
                    group='wave', parent='WAVE_NIGHT_MED_ABS_DEV')

# sigma clipping for the fit used in wave night
KW_WNT_NSIG_FIT = KW_WNT_NSIG_FIT.copy(__NAME__)
KW_WNT_NSIG_FIT.set(key='WNTNSIGF', comment='wave night sig clip fit cut used',
                    parent='WAVE_NIGHT_NSIG_FIT_CUT', group='wave')

# -----------------------------------------------------------------------------
# Define telluric preclean variables
# -----------------------------------------------------------------------------
# Define the exponent of water key from telluric preclean process
KW_TELLUP_EXPO_WATER = KW_TELLUP_EXPO_WATER.copy(__NAME__)
KW_TELLUP_EXPO_WATER.set(key='TLPEH2O',
                         comment='tellu preclean expo water calculated')

# Define the exponent of other species from telluric preclean process
KW_TELLUP_EXPO_OTHERS = KW_TELLUP_EXPO_OTHERS.copy(__NAME__)
KW_TELLUP_EXPO_OTHERS.set(key='TLPEOTR',
                          comment='tellu preclean expo others calculated')

# Define the velocity of water absorbers calculated in telluric preclean process
KW_TELLUP_DV_WATER = KW_TELLUP_DV_WATER.copy(__NAME__)
KW_TELLUP_DV_WATER.set(key='TLPDVH2O',
                       comment='tellu preclean velocity water absorbers')

# Define the velocity of other species absorbers calculated in telluric
#     preclean process
KW_TELLUP_DV_OTHERS = KW_TELLUP_DV_OTHERS.copy(__NAME__)
KW_TELLUP_DV_OTHERS.set(key='TLPDVOTR',
                        comment='tellu preclean velocity others absorbers')

# Define the ccf power of the water
KW_TELLUP_CCFP_WATER = KW_TELLUP_CCFP_WATER.copy(__NAME__)
KW_TELLUP_CCFP_WATER.set(key='TLPCPH2O', comment='CCF power of H20')

# Define the ccf power of the others
KW_TELLUP_CCFP_OTHERS = KW_TELLUP_CCFP_OTHERS.copy(__NAME__)
KW_TELLUP_CCFP_OTHERS.set(key='TLPCPOTR', comment='CCF power of other species')

# Define whether precleaning was done (tellu pre-cleaning)
KW_TELLUP_DO_PRECLEAN = KW_TELLUP_DO_PRECLEAN.copy(__NAME__)
KW_TELLUP_DO_PRECLEAN.set(key='TLPDOCLN', comment='tellu preclean done',
                          parent='TELLUP_DO_PRECLEANING')

# Define default water absorption used (tellu pre-cleaning)
KW_TELLUP_DFLT_WATER = KW_TELLUP_DFLT_WATER.copy(__NAME__)
KW_TELLUP_DFLT_WATER.set(key='TLPDFH2O',
                         comment='tellu preclean default h20 abso used',
                         parent='TELLUP_D_WATER_ABSO')

# Define ccf scan range that was used (tellu pre-cleaning)
KW_TELLUP_CCF_SRANGE = KW_TELLUP_CCF_SRANGE.copy(__NAME__)
KW_TELLUP_CCF_SRANGE.set(key='TLPSCRNG',
                         comment='tellu preclean ccf scan range km/s',
                         parent='TELLUP_CCF_SCAN_RANGE')

# Define whether we cleaned OH lines
KW_TELLUP_CLEAN_OHLINES = KW_TELLUP_CLEAN_OHLINES.copy(__NAME__)
KW_TELLUP_CLEAN_OHLINES.set(key='TLPCLORD',
                            comment='tellu preclean were OH lines were cleaned',
                            parent='TELLUP_CLEAN_OH_LINES')

# Define which orders were removed from tellu pre-cleaning
KW_TELLUP_REMOVE_ORDS = KW_TELLUP_REMOVE_ORDS.copy(__NAME__)
KW_TELLUP_REMOVE_ORDS.set(key='TLPRORDS',
                          comment='tellu preclean which orders were removed',
                          parent='TELLUP_REMOVE_ORDS')

# Define which min snr threshold was used for tellu pre-cleaning
KW_TELLUP_SNR_MIN_THRES = KW_TELLUP_SNR_MIN_THRES.copy(__NAME__)
KW_TELLUP_SNR_MIN_THRES.set(key='TLPSNRMT',
                            comment='tellu preclean snr min threshold',
                            parent='TELLUP_SNR_MIN_THRES')

# Define dexpo convergence threshold used
KW_TELLUP_DEXPO_CONV_THRES = KW_TELLUP_DEXPO_CONV_THRES.copy(__NAME__)
KW_TELLUP_DEXPO_CONV_THRES.set(key='TLPDEXCT',
                               comment='tellu preclean dexpo conv thres used',
                               parent='TELLUP_DEXPO_CONV_THRES')

# Define the maximum number of oterations used to get dexpo convergence
KW_TELLUP_DEXPO_MAX_ITR = KW_TELLUP_DEXPO_MAX_ITR.copy(__NAME__)
KW_TELLUP_DEXPO_MAX_ITR.set(key='TLPMXITR',
                            comment='tellu preclean max iterations used',
                            parent='TELLUP_DEXPO_MAX_ITR')

# Define the kernel threshold in abso_expo used in tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KTHRES = KW_TELLUP_ABSOEXPO_KTHRES.copy(__NAME__)
KW_TELLUP_ABSOEXPO_KTHRES.set(key='TLPAEKTH',
                              comment='tellu preclean abso expo kernel thres',
                              parent='TELLUP_ABSO_EXPO_KTHRES')

# Define the wave start (same as s1d) in nm used
KW_TELLUP_WAVE_START = KW_TELLUP_WAVE_START.copy(__NAME__)
KW_TELLUP_WAVE_START.set(key='TLPWAVES',
                         comment='tellu preclean wave start used [nm]',
                         parent='EXT_S1D_WAVESTART')

# Define the wave end (same as s1d) in nm used
KW_TELLUP_WAVE_END = KW_TELLUP_WAVE_END.copy(__NAME__)
KW_TELLUP_WAVE_END.set(key='TLPWAVEF',
                       comment='tellu preclean wave end used [nm]',
                       parent='EXT_S1D_WAVEEND')

# Define the dv wave grid (same as s1d) in km/s used
KW_TELLUP_DVGRID = KW_TELLUP_DVGRID.copy(__NAME__)
KW_TELLUP_DVGRID.set(key='TLPDVGRD',
                     comment='tellu preclean dv wave grid used [km/s]',
                     parent='EXT_S1D_BIN_UVELO')

# Define the gauss width of the kernel used in abso_expo for tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KWID = KW_TELLUP_ABSOEXPO_KWID.copy(__NAME__)
KW_TELLUP_ABSOEXPO_KWID.set(key='TLPAEKWD',
                            comment='tellu preclean gauss width kernel used',
                            parent='TELLUP_ABSO_EXPO_KWID')

# Define the gauss shape of the kernel used in abso_expo for tellu pre-cleaning
KW_TELLUP_ABSOEXPO_KEXP = KW_TELLUP_ABSOEXPO_KEXP.copy(__NAME__)
KW_TELLUP_ABSOEXPO_KEXP.set(key='TLPAEKEX',
                            comment='tellu preclean gauss shape kernel used',
                            parent='TELLUP_ABSO_EXPO_KEXP')

# Define the exponent of the transmission threshold used for tellu pre-cleaning
KW_TELLUP_TRANS_THRES = KW_TELLUP_TRANS_THRES.copy(__NAME__)
KW_TELLUP_TRANS_THRES.set(key='TLPTRSTH',
                          comment='tellu preclean transmission thres used',
                          parent='TELLUP_TRANS_THRES')

# Define the threshold for discrepant tramission used for tellu pre-cleaning
KW_TELLUP_TRANS_SIGL = KW_TELLUP_TRANS_SIGL.copy(__NAME__)
KW_TELLUP_TRANS_SIGL.set(key='TLPTRSLM',
                         comment='tellu preclean transmission sig limit used',
                         parent='TELLUP_TRANS_SIGLIM')

# Define the whether to force fit to header airmass used for tellu pre-cleaning
KW_TELLUP_FORCE_AIRMASS = KW_TELLUP_FORCE_AIRMASS.copy(__NAME__)
KW_TELLUP_FORCE_AIRMASS.set(key='TLPFCARM',
                            comment='tellu preclean force airmass from hdr',
                            parent='TELLUP_FORCE_AIRMASS')

# Define the bounds of the exponent of other species used for tellu pre-cleaning
KW_TELLUP_OTHER_BOUNDS = KW_TELLUP_OTHER_BOUNDS.copy(__NAME__)
KW_TELLUP_OTHER_BOUNDS.set(key='TLP_OTHB',
                           comment='tellu preclean lower/upper bounds others',
                           parent='TELLUP_OTHER_BOUNDS')

# Define the bounds of the exponent of water used for tellu pre-cleaning
KW_TELLUP_WATER_BOUNDS = KW_TELLUP_WATER_BOUNDS.copy(__NAME__)
KW_TELLUP_WATER_BOUNDS.set(key='TLP_H2OB',
                           comment='tellu preclean lower/upper bounds water',
                           parent='TELLUP_WATER_BOUNDS')

# -----------------------------------------------------------------------------
# Define make telluric variables
# -----------------------------------------------------------------------------
# The template file used for mktellu calculation
KW_MKTELL_TEMP_FILE = KW_MKTELL_TEMP_FILE.copy(__NAME__)
KW_MKTELL_TEMP_FILE.set(key='MKTTEMPF', comment='mktellu template file used')

# The blaze percentile used for mktellu calculation
KW_MKTELL_BLAZE_PRCT = KW_MKTELL_BLAZE_PRCT.copy(__NAME__)
KW_MKTELL_BLAZE_PRCT.set(key='MKTBPRCT', comment='mktellu blaze percentile')

# The blaze normalization cut used for mktellu calculation
KW_MKTELL_BLAZE_CUT = KW_MKTELL_BLAZE_CUT.copy(__NAME__)
KW_MKTELL_BLAZE_CUT.set(key='MKTBZCUT', comment='mktellu blaze cut used')

# The default convolution width in pix used for mktellu calculation
KW_MKTELL_DEF_CONV_WID = KW_MKTELL_DEF_CONV_WID.copy(__NAME__)
KW_MKTELL_DEF_CONV_WID.set(key='MKTDCONV',
                           comment='mktellu default conv width used')

# The median filter width used for mktellu calculation
KW_MKTELL_TEMP_MEDFILT = KW_MKTELL_TEMP_MEDFILT.copy(__NAME__)
KW_MKTELL_TEMP_MEDFILT.set(key='MKT_TMED',
                           comment='mktellu template med filter used')

# The recovered airmass value calculated in mktellu calculation
KW_MKTELL_AIRMASS = KW_MKTELL_AIRMASS.copy(__NAME__)
KW_MKTELL_AIRMASS.set(key='MTAUOTHE',
                      comment='mktellu recovered airmass (tau other)')

# The recovered water optical depth calculated in mktellu calculation
KW_MKTELL_WATER = KW_MKTELL_WATER.copy(__NAME__)
KW_MKTELL_WATER.set(key='MTAUH2O',
                    comment='mktellu recovered water depth (tau H2O)')

# The min transmission requirement used for mktellu/ftellu
KW_MKTELL_THRES_TFIT = KW_MKTELL_THRES_TFIT.copy(__NAME__)
KW_MKTELL_THRES_TFIT.set(key='MKTTTFIT',
                         comment='mktellu min transmission used',
                         parent='MKTELLU_THRES_TRANSFIT')

# The upper limit for trans fit used in mktellu/ftellu
KW_MKTELL_TRANS_FIT_UPPER_BAD = KW_MKTELL_TRANS_FIT_UPPER_BAD.copy(__NAME__)
KW_MKTELL_TRANS_FIT_UPPER_BAD.set(key='MKTTTMAX',
                                  comment='mktellu max transmission used',
                                  parent='MKTELLU_TRANS_FIT_UPPER_BAD')

# -----------------------------------------------------------------------------
# Define fit telluric variables
# -----------------------------------------------------------------------------
# The number of principle components used
KW_FTELLU_NPC = KW_FTELLU_NPC.copy(__NAME__)
KW_FTELLU_NPC.set(key='FTT_NPC',
                  comment='ftellu Number of principal components used')

# The number of trans files used in pc fit (closest in expo h20/others)
KW_FTELLU_NTRANS = KW_FTELLU_NTRANS.copy(__NAME__)
KW_FTELLU_NTRANS.set(key='FTT_NTRS',
                     comment='ftellu NUmber of trans files used in pc fit')

# whether we added first derivative to principal components
KW_FTELLU_ADD_DPC = KW_FTELLU_ADD_DPC.copy(__NAME__)
KW_FTELLU_ADD_DPC.set(key='FTT_ADPC',
                      comment='ftellu first deriv. was added to pc')

# whether we fitted the derivatives of the principal components
KW_FTELLU_FIT_DPC = KW_FTELLU_FIT_DPC.copy(__NAME__)
KW_FTELLU_FIT_DPC.set(key='FTT_FDPC',
                      comment='ftellu deriv. of pc was fit instead of pc')

# The source of the loaded absorption (npy file or trans_file from database)
KW_FTELLU_ABSO_SRC = KW_FTELLU_ABSO_SRC.copy(__NAME__)
KW_FTELLU_ABSO_SRC.set(key='FTTABSOS',
                       comment='ftellu source of the abso (file or database)')

# The prefix for molecular
KW_FTELLU_ABSO_PREFIX = KW_FTELLU_ABSO_PREFIX.copy(__NAME__)
KW_FTELLU_ABSO_PREFIX.set(key='ABSO', comment='Absorption in {0}')

# Number of good pixels requirement used
KW_FTELLU_FIT_KEEP_NUM = KW_FTELLU_FIT_KEEP_NUM.copy(__NAME__)
KW_FTELLU_FIT_KEEP_NUM.set(key='FTTFKNUM',
                           comment='ftellu num of good pixels used per order')

# The minimum transmission used
KW_FTELLU_FIT_MIN_TRANS = KW_FTELLU_FIT_MIN_TRANS.copy(__NAME__)
KW_FTELLU_FIT_MIN_TRANS.set(key='FTTMTRAN',
                            comment='ftellu min transmission used')

# The minimum wavelength used
KW_FTELLU_LAMBDA_MIN = KW_FTELLU_LAMBDA_MIN.copy(__NAME__)
KW_FTELLU_LAMBDA_MIN.set(key='FTTMINLL', comment='ftellu min wavelength used')

# The maximum wavelength used
KW_FTELLU_LAMBDA_MAX = KW_FTELLU_LAMBDA_MAX.copy(__NAME__)
KW_FTELLU_LAMBDA_MAX.set(key='FTTMAXLL', comment='ftellu max wavelength used')

# The smoothing kernel size [km/s] used
KW_FTELLU_KERN_VSINI = KW_FTELLU_KERN_VSINI.copy(__NAME__)
KW_FTELLU_KERN_VSINI.set(key='FTTSKERN',
                         comment='ftellu smoothing kernal used [km/s]')

# The image pixel size used
KW_FTELLU_IM_PX_SIZE = KW_FTELLU_IM_PX_SIZE.copy(__NAME__)
KW_FTELLU_IM_PX_SIZE.set(key='FTTIMPXS', comment='ftellu image pixel size used')

# the number of iterations used to fit
KW_FTELLU_FIT_ITERS = KW_FTELLU_FIT_ITERS.copy(__NAME__)
KW_FTELLU_FIT_ITERS.set(key='FTTFITRS',
                        comment='ftellu num iterations used for fit')

# the log limit in minimum absorption used
KW_FTELLU_RECON_LIM = KW_FTELLU_RECON_LIM.copy(__NAME__)
KW_FTELLU_RECON_LIM.set(key='FTTRCLIM',
                        comment='ftellu log limit in min absorption used')

# the template that was used (or None if not used)
KW_FTELLU_TEMPLATE = KW_FTELLU_TEMPLATE.copy(__NAME__)
KW_FTELLU_TEMPLATE.set(key='FTTTEMPL', comment='ftellu template used for sed')

# Telluric principle component amplitudes (for use with 1D list)
KW_FTELLU_AMP_PC = KW_FTELLU_AMP_PC.copy(__NAME__)
KW_FTELLU_AMP_PC.set(key='AMPPC{0:03d}',
                     comment='ftellu Principle Component Amplitudes')

# Telluric principle component first derivative
KW_FTELLU_DVTELL1 = KW_FTELLU_DVTELL1.copy(__NAME__)
KW_FTELLU_DVTELL1.set(key='DV_TELL1',
                      comment='ftellu Principle Component first der.')

# Telluric principle component second derivative
KW_FTELLU_DVTELL2 = KW_FTELLU_DVTELL2.copy(__NAME__)
KW_FTELLU_DVTELL2.set(key='DV_TELL1',
                      comment='ftellu Principle Component second der.')

# Tau Water depth calculated in fit tellu
KW_FTELLU_TAU_H2O = KW_FTELLU_TAU_H2O.copy(__NAME__)
KW_FTELLU_TAU_H2O.set(key='TAU_H2O', comment='ftellu TAPAS tau H2O')

# Tau Rest depth calculated in fit tellu
KW_FTELLU_TAU_REST = KW_FTELLU_TAU_REST.copy(__NAME__)
KW_FTELLU_TAU_REST.set(key='TAU_OTHE',
                       comment='ftellu TAPAS tau for O2,O3,CH4,N2O,CO2')

# -----------------------------------------------------------------------------
# Define make template variables
# -----------------------------------------------------------------------------
# the snr order used for quality control cut in make template calculation
KW_MKTEMP_SNR_ORDER = KW_MKTEMP_SNR_ORDER.copy(__NAME__)
KW_MKTEMP_SNR_ORDER.set(key='MTPSNROD', comment='mktemplate snr order used')

# the snr threshold used for quality control cut in make template calculation
KW_MKTEMP_SNR_THRES = KW_MKTEMP_SNR_THRES.copy(__NAME__)
KW_MKTEMP_SNR_THRES.set(key='MTPSNRTH', comment='mktemplate snr threshold used')

# -----------------------------------------------------------------------------
# Define ccf variables
# -----------------------------------------------------------------------------
# The mean rv calculated from the mean ccf
KW_CCF_MEAN_RV = KW_CCF_MEAN_RV.copy(__NAME__)
KW_CCF_MEAN_RV.set(key='CCFMNRV',
                   comment='Mean RV calc. from the mean CCF [km/s]')

# the mean constrast (depth of fit ccf) from the mean ccf
KW_CCF_MEAN_CONSTRAST = KW_CCF_MEAN_CONSTRAST.copy(__NAME__)
KW_CCF_MEAN_CONSTRAST.set(key='CCFMCONT',
                          comment='Mean contrast (depth of fit) from mean CCF')

# the mean fwhm from the mean ccf
KW_CCF_MEAN_FWHM = KW_CCF_MEAN_FWHM.copy(__NAME__)
KW_CCF_MEAN_FWHM.set(key='CCFMFWHM', comment='Mean FWHM from mean CCF')

# the total number of mask lines used in all ccfs
KW_CCF_TOT_LINES = KW_CCF_TOT_LINES.copy(__NAME__)
KW_CCF_TOT_LINES.set(key='CCFTLINE',
                     comment='Total no. of mask lines used in CCF')

# the ccf mask file used
KW_CCF_MASK = KW_CCF_MASK.copy(__NAME__)
KW_CCF_MASK.set(key='CCFMASK', comment='CCF mask file used')

# the ccf step used (in km/s)
KW_CCF_STEP = KW_CCF_STEP.copy(__NAME__)
KW_CCF_STEP.set(key='CCFSTEP', comment='CCF step used [km/s]')

# the width of the ccf used (in km/s)
KW_CCF_WIDTH = KW_CCF_WIDTH.copy(__NAME__)
KW_CCF_WIDTH.set(key='CCFWIDTH', comment='CCF width used [km/s]')

# the central rv used (in km/s) rv elements run from rv +/- width in the ccf
KW_CCF_TARGET_RV = KW_CCF_TARGET_RV.copy(__NAME__)
KW_CCF_TARGET_RV.set(key='CCFTRGRV',
                     comment='CCF central RV used in CCF [km/s]')

# the read noise used in the photon noise uncertainty calculation in the ccf
KW_CCF_SIGDET = KW_CCF_SIGDET.copy(__NAME__)
KW_CCF_SIGDET.set(key='CCFSIGDT',
                  comment='Read noise used in photon noise calc. in CCF')

# the size in pixels around saturated pixels to regard as bad pixels used in
#    the ccf photon noise calculation
KW_CCF_BOXSIZE = KW_CCF_BOXSIZE.copy(__NAME__)
KW_CCF_BOXSIZE.set(key='CCFBOXSZ',
                   comment='Size of bad px used in photon noise calc. in CCF')

# the upper limit for good pixels (above this are bad) used in the ccf photon
#   noise calculation
KW_CCF_MAXFLUX = KW_CCF_MAXFLUX.copy(__NAME__)
KW_CCF_MAXFLUX.set(key='CCFMAXFX',
                   comment='Flux thres for bad px in photon noise calc. in CCF')

# The last order used in the mean CCF (from 0 to nmax are used)
KW_CCF_NMAX = KW_CCF_NMAX.copy(__NAME__)
KW_CCF_NMAX.set(key='CCFORDMX',
                comment='Last order used in mean for mean CCF')

# the minimum weight of a line in the CCF MASK used
KW_CCF_MASK_MIN = KW_CCF_MASK_MIN.copy(__NAME__)
KW_CCF_MASK_MIN.set(key='CCFMSKMN',
                    comment='Minimum weight of lines used in the CCF mask')

# the mask width of lines in the CCF Mask used
KW_CCF_MASK_WID = KW_CCF_MASK_WID.copy(__NAME__)
KW_CCF_MASK_WID.set(key='CCFMSKWD',
                    comment='Width of lines used in the CCF mask')

# the wavelength units used in the CCF Mask for line centers
KW_CCF_MASK_UNITS = KW_CCF_MASK_UNITS.copy(__NAME__)
KW_CCF_MASK_UNITS.set(key='CCFMUNIT', comment='Units used in CCF Mask')

# the dv rms calculated for spectrum
KW_CCF_DVRMS_SP = KW_CCF_DVRMS_SP.copy(__NAME__)
KW_CCF_DVRMS_SP.set(key='DVRMS_SP',
                    comment='RV photon-noise uncertainty calc on E2DS '
                            'spectrum [m/s] ')

# the dev rms calculated during the CCF [m/s]
KW_CCF_DVRMS_CC = KW_CCF_DVRMS_CC.copy(__NAME__)
KW_CCF_DVRMS_CC.set(key='DVRMS_CC',
                    comment='final photon-noise RV uncertainty calc on mean '
                            'CCF [m/s]')

# The radial velocity measured from the wave solution FP CCF
KW_CCF_RV_WAVE_FP = KW_CCF_RV_WAVE_FP.copy(__NAME__)
KW_CCF_RV_WAVE_FP.set(key='RV_WAVFP',
                      comment='RV measured from wave sol FP CCF [km/s]')

# The radial velocity measured from a simultaneous FP CCF
#     (FP in reference channel)
KW_CCF_RV_SIMU_FP = KW_CCF_RV_SIMU_FP.copy(__NAME__)
KW_CCF_RV_SIMU_FP.set(key='RV_SIMFP',
                      comment='RV measured from simultaneous FP CCF [km/s]')

# The radial velocity drift between wave sol FP and simultaneous FP (if present)
#   if simulataneous FP not present this is just the wave solution FP CCF value
KW_CCF_RV_DRIFT = KW_CCF_RV_DRIFT.copy(__NAME__)
KW_CCF_RV_DRIFT.set(key='RV_DRIFT',
                    comment='RV drift between wave sol and sim. FP CCF [km/s]')

# The radial velocity measured from the object CCF against the CCF MASK
KW_CCF_RV_OBJ = KW_CCF_RV_OBJ.copy(__NAME__)
KW_CCF_RV_OBJ.set(key='RV_OBJ',
                  comment='RV calc in the object CCF (non corr.) [km/s]')

# the corrected radial velocity of the object (taking into account the FP RVs)
KW_CCF_RV_CORR = KW_CCF_RV_CORR.copy(__NAME__)
KW_CCF_RV_CORR.set(key='RV_CORR',
                   comment='RV corrected for FP CCF drift [km/s]')

# the wave file used for the rv (fiber specific)
KW_CCF_RV_WAVEFILE = KW_CCF_RV_WAVEFILE.copy(__NAME__)
KW_CCF_RV_WAVEFILE.set(key='RV_WAVFN',
                       comment='RV wave file used')

# the wave file time used for the rv [mjd] (fiber specific)
KW_CCF_RV_WAVETIME = KW_CCF_RV_WAVETIME.copy(__NAME__)
KW_CCF_RV_WAVETIME.set(key='RV_WAVTM',
                       comment='RV wave file time used')

# the time diff (in days) between wave file and file (fiber specific)
KW_CCF_RV_TIMEDIFF = KW_CCF_RV_TIMEDIFF.copy(__NAME__)
KW_CCF_RV_TIMEDIFF.set(key='RV_WAVTD',
                       comment='RV timediff [days] btwn file and wave sol.')

# the wave file source used for the rv reference fiber
KW_CCF_RV_WAVESRCE = KW_CCF_RV_WAVESRCE.copy(__NAME__)
KW_CCF_RV_WAVESRCE.set(key='RV_WAVSR',
                       comment='RV wave file source used')

# -----------------------------------------------------------------------------
# Define polar variables
# -----------------------------------------------------------------------------
# define the Stokes paremeter: Q, U, V, or I
KW_POL_STOKES = KW_POL_STOKES.copy(__NAME__)
KW_POL_STOKES.set(key='STOKES', comment='POLAR Stokes paremeter: Q, U, V, or I')

# define Number of exposures for polarimetry
KW_POL_NEXP = KW_POL_NEXP.copy(__NAME__)
KW_POL_NEXP.set(key='POLNEXP',
                comment='POLAR Number of exposures for polarimetry')

# defines the Polarimetry method
KW_POL_METHOD = KW_POL_METHOD.copy(__NAME__)
KW_POL_METHOD.set(key='POLMETHO', comment='POLAR Polarimetry method')

# define the base file name exposure list
KW_POL_FILES = KW_POL_FILES.copy(__NAME__)
KW_POL_FILES.set(key='P_IN{0:02d}', comment='POLAR Base filename of')

# define the exposure times of exposure list
KW_POL_EXPS = KW_POL_EXPS.copy(__NAME__)
KW_POL_EXPS.set(key='P_EX{0:02d}', comment='POLAR EXPTIME [s] of')

# define the mjds at start for exposure list
KW_POL_MJDS = KW_POL_MJDS.copy(__NAME__)
KW_POL_MJDS.set(key='P_MJD{0:02d}', comment='POLAR MJD at start of')

# define the mjdends at end for exposure list
KW_POL_MJDENDS = KW_POL_MJDENDS.copy(__NAME__)
KW_POL_MJDENDS.set(key='P_MJDE{0:02d}', comment='POLAR MJDEND at end of ')

# define the bjds for exposure list
KW_POL_BJDS = KW_POL_BJDS.copy(__NAME__)
KW_POL_BJDS.set(key='P_BJD{0:02d}', comment='POLAR BJD for ')

# define the bervs for exposure list
KW_POL_BERVS = KW_POL_BERVS.copy(__NAME__)
KW_POL_BERVS.set(key='P_BERV{0:02d}', comment='POLAR BERV for')

# define the Total exposure time (sec)
KW_POL_EXPTIME = KW_POL_EXPTIME.copy(__NAME__)
KW_POL_EXPTIME.set(key='POLTTIME', comment='POLAR Total exposure time (sec)')

# define the Elapsed time of observation (sec)
KW_POL_ELAPTIME = KW_POL_ELAPTIME.copy(__NAME__)
KW_POL_ELAPTIME.set(key='POLETIME',
                    comment='POLAR Elapsed time of observation (sec)')

# define the MJD at center of observation
KW_POL_MJDCEN = KW_POL_MJDCEN.copy(__NAME__)
KW_POL_MJDCEN.set(key='POLMJDC', comment='POLAR MJD at center of observation')

# define the BJD at center of observation
KW_POL_BJDCEN = KW_POL_BJDCEN.copy(__NAME__)
KW_POL_BJDCEN.set(key='POLBJDC', comment='POLAR BJD at center of observation')

# define the BERV at center of observation
KW_POL_BERVCEN = KW_POL_BERVCEN.copy(__NAME__)
KW_POL_BERVCEN.set(key='POLBERVC',
                   comment='POLAR BERV at center of observation')

# define the Mean BJD for polar sequence
KW_POL_MEANBJD = KW_POL_MEANBJD.copy(__NAME__)
KW_POL_MEANBJD.set(key='POLMNBJD', comment='POLAR Mean BJD for polar sequence')

# define the minimum number of files used
KW_USED_MIN_FILES = KW_USED_MIN_FILES.copy(__NAME__)
KW_USED_MIN_FILES.set(key='POLMINFL', comment='POLAR Min no. files used')

# define all possible fibers for polarimetry used
KW_USED_VALID_FIBERS = KW_USED_VALID_FIBERS.copy(__NAME__)
KW_USED_VALID_FIBERS.set(key='P_VFIB{0:02d}', comment='POLAR valid fibers used')

# define all possible stokes parameters used
KW_USED_VALID_STOKES = KW_USED_VALID_STOKES.copy(__NAME__)
KW_USED_VALID_STOKES.set(key='P_VSTK{0:02d}', comment='POLAR valid stokes used')

# define the continuum bin size used
KW_USED_CONT_BINSIZE = KW_USED_CONT_BINSIZE.copy(__NAME__)
KW_USED_CONT_BINSIZE.set(key='POLUCBIN',
                         comment='POLAR continuum binsize used')

# define the continuum overlap used
KW_USED_CONT_OVERLAP = KW_USED_CONT_OVERLAP.copy(__NAME__)
KW_USED_CONT_OVERLAP.set(key='POLUCOVL',
                         comment='POLAR continuum overlap used')

# define the LSD mask filename
KW_POLAR_LSD_MASK = KW_POLAR_LSD_MASK.copy(__NAME__)
KW_POLAR_LSD_MASK.set(key='PLSDMASK', comment='POLAR LSD mask filename')

# define the Radial velocity (km/s) from gaussian fit from polar lsd
KW_POLAR_LSD_FIT_RV = KW_POLAR_LSD_FIT_RV.copy(__NAME__)
KW_POLAR_LSD_FIT_RV.set(key='PLSD_FRV',
                        comment='POLAR LSD RV [km/s] from gaussfit')

# define the Resolving power from gaussian fit from polar lsd
KW_POLAR_LSD_FIT_RESOL = KW_POLAR_LSD_FIT_RESOL.copy(__NAME__)
KW_POLAR_LSD_FIT_RESOL.set(key='PLSD_FRE',
                           comment='POLAR LSD Resolving power from gaussfit')

# define the Mean polarization of data in LSD
KW_POLAR_LSD_MEANPOL = KW_POLAR_LSD_MEANPOL.copy(__NAME__)
KW_POLAR_LSD_MEANPOL.set(key='PLSDMN_P',
                         comment='POLAR LSD Mean polarization in data')

# define the Std dev polarization of data in LSD
KW_POLAR_LSD_STDPOL = KW_POLAR_LSD_STDPOL.copy(__NAME__)
KW_POLAR_LSD_STDPOL.set(key='PLSDST_P',
                        comment='POLAR LSD Std dev polarization of dataD')

# define the Median polarization of data in LSD
KW_POLAR_LSD_MEDPOL = KW_POLAR_LSD_MEDPOL.copy(__NAME__)
KW_POLAR_LSD_MEDPOL.set(key='PLSDME_P',
                        comment='POLAR LSD Median polarization of data')

# define the Med abs dev polarization of data in LSD
KW_POLAR_LSD_MEDABSDEV = KW_POLAR_LSD_MEDABSDEV.copy(__NAME__)
KW_POLAR_LSD_MEDABSDEV.set(key='PLSDMADP',
                           comment='POLAR LSD Med absdev polarization of data')

# define the mean of pol LSD profile
KW_POLAR_LSD_MEANSVQU = KW_POLAR_LSD_MEANSVQU.copy(__NAME__)
KW_POLAR_LSD_MEANSVQU.set(key='PLSDMVQU',
                          comment='POLAR LSD mean of pol LSD profile')

# define the Std dev of pol LSD profile
KW_POLAR_LSD_STDSVQU = KW_POLAR_LSD_STDSVQU.copy(__NAME__)
KW_POLAR_LSD_STDSVQU.set(key='PLSDSVQU',
                         comment='POLAR LSD Std dev of pol LSD profile')

# define the Mean of null LSD profile
KW_POLAR_LSD_MEANNULL = KW_POLAR_LSD_MEANNULL.copy(__NAME__)
KW_POLAR_LSD_MEANNULL.set(key='PLSDMNUL',
                          comment='POLAR LSD Mean of null LSD profile')

# define the Std dev of null LSD profile
KW_POLAR_LSD_STDNULL = KW_POLAR_LSD_STDNULL.copy(__NAME__)
KW_POLAR_LSD_STDNULL.set(key='PLSDSNUL',
                         comment='POLAR LSD Std dev of null LSD profile')

# define the lsd column: Velocities (km/s)
KW_POL_LSD_COL1 = KW_POL_LSD_COL1.copy(__NAME__)
KW_POL_LSD_COL1.set(key='PLSDCOL1', comment='POLAR LSD COL: Velocities (km/s)')

# define the lsd column: Stokes I LSD profile
KW_POL_LSD_COL2 = KW_POL_LSD_COL2.copy(__NAME__)
KW_POL_LSD_COL2.set(key='PLSDCOL2',
                    comment='POLAR LSD COL: Stokes I LSD profile')

# define the lsd column: Gaussian fit to Stokes I LSD profile
KW_POL_LSD_COL3 = KW_POL_LSD_COL3.copy(__NAME__)
KW_POL_LSD_COL3.set(key='PLSDCOL3',
                    comment='POLAR LSD COL: Gaussfit to Stokes I LSD profile')

# define the lsd column: Stokes V, U, or Q LSD profile
KW_POL_LSD_COL4 = KW_POL_LSD_COL4.copy(__NAME__)
KW_POL_LSD_COL4.set(key='PLSDCOL4',
                    comment='POLAR LSD COL: Stokes V, U, or Q LSD profile')

# define the lsd column: Null polarization LSD profile
KW_POL_LSD_COL5 = KW_POL_LSD_COL5.copy(__NAME__)
KW_POL_LSD_COL5.set(key='PLSDCOL5',
                    comment='POLAR LSD COL: Null polarization LSD profile')

# define the minimum line depth value used in LSD analysis
KW_POLAR_LSD_MLDEPTH = KW_POLAR_LSD_MLDEPTH.copy(__NAME__)
KW_POLAR_LSD_MLDEPTH.set(key='PLSDMLSP',
                         comment='POLAR LSD minimum line depth used')

# Define initial velocity value used in LSD analysis
KW_POLAR_LSD_VINIT = KW_POLAR_LSD_VINIT.copy(__NAME__)
KW_POLAR_LSD_VINIT.set(key='PLSD_V0',
                       comment='POLAR LSD Initial velocity [km/s]')

# Define final velocity value used in LSD analysis
KW_POLAR_LSD_VFINAL = KW_POLAR_LSD_VFINAL.copy(__NAME__)
KW_POLAR_LSD_VFINAL.set(key='PLSD_VF',
                        comment='POLAR LSD Final velocity [km/s]')

# Define whether stokesI was normalised by continuum
KW_POLAR_LSD_NORM = KW_POLAR_LSD_NORM.copy(__NAME__)
KW_POLAR_LSD_NORM.set(key='PLSDNCONT',
                      comment='POLAR LSD whether stokesI norm by continuum')

# define the bin size used for norm continuum
KW_POLAR_LSD_NBIN1 = KW_POLAR_LSD_NBIN1.copy(__NAME__)
KW_POLAR_LSD_NBIN1.set(key='PLSDNBIN',
                       comment='POLAR LSD bin size used for norm continuum')

# define the overlap used for norm continuum
KW_POLAR_LSD_NLAP1 = KW_POLAR_LSD_NLAP1.copy(__NAME__)
KW_POLAR_LSD_NLAP1.set(key='PLSDNLAP',
                       comment='POLAR LSD overlap used for norm continuum')

# define the sig clip used for norm continuum
KW_POLAR_LSD_NSIG1 = KW_POLAR_LSD_NSIG1.copy(__NAME__)
KW_POLAR_LSD_NSIG1.set(key='PLSDNSIG',
                       comment='POLAR LSD sigclip used for norm continuum')

# define the window size used for norm continuum
KW_POLAR_LSD_NWIN1 = KW_POLAR_LSD_NWIN1.copy(__NAME__)
KW_POLAR_LSD_NWIN1.set(key='PLSDNWIN',
                       comment='POLAR LSD window size used for norm continuum')

# define the mode used for norm continuum
KW_POLAR_LSD_NMODE1 = KW_POLAR_LSD_NMODE1.copy(__NAME__)
KW_POLAR_LSD_NMODE1.set(key='PLSDNMOD',
                        comment='POLAR LSD mode used for norm continuum')

# define whether a linear fit was used for norm continuum
KW_POLAR_LSD_NLFIT1 = KW_POLAR_LSD_NLFIT1.copy(__NAME__)
KW_POLAR_LSD_NLFIT1.set(key='PLSDNLFT',
                        comment='POLAR LSD whether linfit used norm continuum')

# define the Number of points for LSD profile
KW_POLAR_LSD_NPOINTS = KW_POLAR_LSD_NPOINTS.copy(__NAME__)
KW_POLAR_LSD_NORM.set(key='PLSD_NP',
                      comment='POLAR LSD Number of points for LSD profile')

# define the bin sized used in profile calc
KW_POLAR_LSD_NBIN2 = KW_POLAR_LSD_NBIN2.copy(__NAME__)
KW_POLAR_LSD_NBIN2.set(key='PLSDPBIN',
                       comment='POLAR LSD bin size used for profile calc.')

# define the overlap used in profile calc
KW_POLAR_LSD_NLAP2 = KW_POLAR_LSD_NLAP2.copy(__NAME__)
KW_POLAR_LSD_NLAP2.set(key='PLSDPLAP',
                       comment='POLAR LSD overlap used for profile calc.')

# define the sigma clip used in profile calc
KW_POLAR_LSD_NSIG2 = KW_POLAR_LSD_NSIG2.copy(__NAME__)
KW_POLAR_LSD_NSIG2.set(key='PLSDPSIG',
                       comment='POLAR LSD sigclip used for profile calc.')

# define the window size used in profile calc
KW_POLAR_LSD_NWIN2 = KW_POLAR_LSD_NWIN2.copy(__NAME__)
KW_POLAR_LSD_NWIN2.set(key='PLSDPWIN',
                       comment='POLAR LSD window size used for profile calc.')

# define the mode used in profile calc
KW_POLAR_LSD_NMODE2 = KW_POLAR_LSD_NMODE2.copy(__NAME__)
KW_POLAR_LSD_NMODE2.set(key='PLSDPMOD',
                        comment='POLAR LSD mode used for profile calc.')

# define whether a linear fit was used in profile calc
KW_POLAR_LSD_NLFIT2 = KW_POLAR_LSD_NLFIT2.copy(__NAME__)
KW_POLAR_LSD_NLFIT2.set(key='PLSDPLFT',
                        comment='POLAR LSD whether linfit used profile calc.')

# =============================================================================
#  End of configuration file
# =============================================================================
