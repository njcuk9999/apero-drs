"""
Default keywords for instrument

Created on 2019-01-17

@author: cook
"""
from terrapipe.core.instruments.default.default_keywords import *
from astropy import units as uu

# TODO: Note: If variables are not showing up MUST CHECK __all__ definition
# TODO:    in import * module

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
KW_ACQTIME.set(key='MJDATE', datatype='mjd', dataformat=float)

# define the MJ end date HEADER key
KW_MJDEND = KW_MJDEND.copy(__NAME__)
KW_MJDEND.set(key='MJDEND', datatype='mjd', dataformat=float)

# define the observation date HEADER key
KW_DATE_OBS = KW_DATE_OBS.copy(__NAME__)
KW_DATE_OBS.set(key='DATE-OBS')

# define the observation time HEADER key
KW_UTC_OBS = KW_UTC_OBS.copy(__NAME__)
KW_UTC_OBS.set(key='UTC-OBS')

# define the read noise HEADER key a.k.a sigdet (used to get value only)
KW_RDNOISE = KW_RDNOISE.copy(__NAME__)
KW_RDNOISE.set(key='RDNOISE')

# define the gain HEADER key (used to get value only)
KW_GAIN = KW_GAIN.copy(__NAME__)
KW_GAIN.set(key='GAIN')

# define the exposure time HEADER key (used to get value only)
KW_EXPTIME = KW_EXPTIME.copy(__NAME__)
KW_EXPTIME.set(key='EXPTIME', unit=uu.s)

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
KW_OBJRA.set(key='OBJRA', unit=uu.hourangle)

# define the observation dec HEADER key
KW_OBJDEC = KW_OBJDEC.copy(__NAME__)
KW_OBJDEC.set(key='OBJDEC', unit=uu.deg)

# define the observation name
# Todo: Change to OBJECT?
KW_OBJNAME = KW_OBJNAME.copy(__NAME__)
KW_OBJNAME.set(key='OBJECT')

# define the gaia id
KW_GAIA_ID = KW_GAIA_ID.copy(__NAME__)
KW_GAIA_ID.set(key='GAIA_ID')

# define the observation equinox HEADER key
KW_OBJEQUIN = KW_OBJEQUIN.copy(__NAME__)
KW_OBJEQUIN.set(key='OBJEQUIN', datatype='decimalyear')

# define the observation proper motion in ra HEADER key
KW_OBJRAPM = KW_OBJRAPM.copy(__NAME__)
KW_OBJRAPM.set(key='OBJRAPM', unit=uu.arcsec / uu.yr)

# define the observation proper motion in dec HEADER key
KW_OBJDECPM = KW_OBJDECPM.copy(__NAME__)
KW_OBJDECPM.set(key='OBJDECPM', unit=uu.arcsec / uu.yr)

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

# define the parallax HEADER key
KW_PLX = KW_PLX.copy(__NAME__)
KW_PLX.set(key='OBJPLX', unit=uu.mas)

# define the rv HEADER key
KW_INPUTRV = KW_INPUTRV.copy(__NAME__)
KW_INPUTRV.set(key='OBSRV', unit=uu.km / uu.s)

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

# Define the key to get the data fits file type
KW_DPRTYPE = KW_DPRTYPE.copy(__NAME__)
KW_DPRTYPE.set(key='DPRTYPE', comment='The type of file (from pre-process)')

# Define the mid exposure time
KW_MID_OBS_TIME = KW_MID_OBS_TIME.copy(__NAME__)
KW_MID_OBS_TIME.set(key='MJDMID', comment='Mid Observation time [mjd]',
                    datatype='mjd', dataformat=float)

# Define the method by which the MJD was calculated
KW_MID_OBS_TIME_METHOD = KW_MID_OBS_TIME_METHOD.copy(__NAME__)
KW_MID_OBS_TIME_METHOD.set(key='MJDMIDMD',
                           comment='Mid Observation time calc method')

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
KW_EXT_TYPE = KW_EXT_TYPE.copy(__NAME__)
KW_EXT_TYPE.set(key='DRS_EOUT', comment='DRS Extraction input DPRTYPE')

# -----------------------------------------------------------------------------
# Define qc variables
# -----------------------------------------------------------------------------
KW_DRS_QC = KW_DRS_QC.copy(__NAME__)
KW_DRS_QC.set(key='QCC_ALL', comment='All quality control passed')
KW_DRS_QC_VAL = KW_DRS_QC_VAL.copy(__NAME__)
KW_DRS_QC_VAL.set(key='QCC{0:03d}V', comment='All quality control passed')
KW_DRS_QC_NAME = KW_DRS_QC_NAME.copy(__NAME__)
KW_DRS_QC_NAME.set(key='QCC{0:03d}N', comment='All quality control passed')
KW_DRS_QC_LOGIC = KW_DRS_QC_LOGIC.copy(__NAME__)
KW_DRS_QC_LOGIC.set(key='QCC{0:03d}L', comment='All quality control passed')
KW_DRS_QC_PASS = KW_DRS_QC_PASS.copy(__NAME__)
KW_DRS_QC_PASS.set(key='QCC{0:03d}P', comment='All quality control passed')

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

# the blaze with used
KW_BLAZE_WID = KW_BLAZE_WID.copy(__NAME__)
KW_BLAZE_WID.set(key='BLAZEWID', comment='Extract: Blaze width used')

# the blaze cut used
KW_BLAZE_CUT = KW_BLAZE_CUT.copy(__NAME__)
KW_BLAZE_CUT.set(key='BLAZECUT', comment='Extract: Blaze cut used')

# the blaze degree used (to fit)
KW_BLAZE_DEG = KW_BLAZE_DEG.copy(__NAME__)
KW_BLAZE_DEG.set(key='BLAZEDEG', comment='Extract: Blaze fit degree used')

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
# Define wave variables
# -----------------------------------------------------------------------------
# Number of orders in wave image
KW_WAVE_NBO = KW_WAVE_NBO.copy(__NAME__)
KW_WAVE_NBO.set(key='WAVEORDN', comment='nb orders in total')

# fit degree for wave solution
KW_WAVE_DEG = KW_WAVE_DEG.copy(__NAME__)
KW_WAVE_DEG.set(key='WAVEDEGN', comment='degree of wave polyn fit')

# the wave file used
KW_WAVEFILE = KW_WAVEFILE.copy(__NAME__)
KW_WAVEFILE.set(key='WAVEFILE', comment='Wavelength solution file used')

# the wave source of the wave file used
KW_WAVESOURCE = KW_WAVESOURCE.copy(__NAME__)
KW_WAVESOURCE.set(key='WAVESOUR', comment='Source of the wave solution used.')

# the wave coefficients
KW_WAVECOEFFS = KW_WAVECOEFFS.copy(__NAME__)
KW_WAVECOEFFS.set(key='WAVE{0:04d}', comment='Wavelength coefficients')

# the initial wave file used for wave solution
KW_INIT_WAVE = KW_INIT_WAVE.copy(__NAME__)
KW_INIT_WAVE.set(key='WAVEINIT', comment='Initial wavelength solution used')

# -----------------------------------------------------------------------------
# the fit degree for wave solution used
KW_WAVE_FITDEG = KW_WAVE_FITDEG.copy(__NAME__)
KW_WAVE_FITDEG.set(key='WAVE_DEG', comment='fit degree used for wave sol')

# the mode used to calculate the hc wave solution
KW_WAVE_MODE_HC = KW_WAVE_MODE_HC.copy(__NAME__)
KW_WAVE_MODE_HC.set(key='WAVHCMOD', comment='mode used to calc hc wave sol')

# the mode used to calculate the fp wave solution
KW_WAVE_MODE_FP = KW_WAVE_MODE_FP.copy(__NAME__)
KW_WAVE_MODE_FP.set(key='WAVFPMOD', comment='mode used to calc fp wave sol')

# the echelle number of the first order used
KW_WAVE_ECHELLE_START = KW_WAVE_ECHELLE_START.copy(__NAME__)
KW_WAVE_ECHELLE_START.set(key='WAV_ECH0', comment='Echelle no. of first order')

# the width of the box for fitting hc lines used
KW_WAVE_HCG_WSIZE = KW_WAVE_HCG_WSIZE.copy(__NAME__)
KW_WAVE_HCG_WSIZE.set(key='WAVHGSIZ', comment='HC Gauss peak fit box width')

# the sigma above local rms for fitting hc lines used
KW_WAVE_HCG_SIGPEAK = KW_WAVE_HCG_SIGPEAK.copy(__NAME__)
KW_WAVE_HCG_SIGPEAK.set(key='WAVHGSPK',
                        comment='HC Gauss peak fit rms sig peak')

# the fit degree for the gaussian peak fitting used
KW_WAVE_HCG_GFITMODE = KW_WAVE_HCG_GFITMODE.copy(__NAME__)
KW_WAVE_HCG_GFITMODE.set(key='WAVHGGFM',
                         comment='HC Gauss peak fit, fit degree')

# the min rms for gaussian peak fitting used
KW_WAVE_HCG_FB_RMSMIN = KW_WAVE_HCG_FB_RMSMIN.copy(__NAME__)
KW_WAVE_HCG_FB_RMSMIN.set(key='WAVHGRMN',
                          comment='HC Gauss peak fit, min rms for peak')

# the max rms for gaussian peak fitting used
KW_WAVE_HCG_FB_RMSMAX = KW_WAVE_HCG_FB_RMSMAX.copy(__NAME__)
KW_WAVE_HCG_FB_RMSMAX.set(key='WAVHGRMX',
                          comment='HC Gauss peak fit, max rms for peak')

# the min e-width of the line for gaussian peak fitting used
KW_WAVE_HCG_EWMIN = KW_WAVE_HCG_EWMIN.copy(__NAME__)
KW_WAVE_HCG_EWMIN.set(key='WAVHGEW0', comment='HC Gauss peak fit, e-width min')

# the min e-width of the line for gaussian peak fitting used
KW_WAVE_HCG_EWMAX = KW_WAVE_HCG_EWMAX.copy(__NAME__)
KW_WAVE_HCG_EWMAX.set(key='WAVHGEW1', comment='HC Gauss peak fit, e-width max')

# the filename for the HC line list generated
KW_WAVE_HCLL_FILE = KW_WAVE_HCLL_FILE.copy(__NAME__)
KW_WAVE_HCLL_FILE.set(key='WAVEHCLL', comment='HC line list file generated')

# the number of bright lines to used in triplet fit
KW_WAVE_TRP_NBRIGHT = KW_WAVE_TRP_NBRIGHT.copy(__NAME__)
KW_WAVE_TRP_NBRIGHT.set(key='WAVTNBRI',
                        comment='Triplet fit - no. bright lines used')

# the number of iterations done in triplet fit
KW_WAVE_TRP_NITER = KW_WAVE_TRP_NITER.copy(__NAME__)
KW_WAVE_TRP_NITER.set(key='WAVTNITR',
                      comment='Triplet fit - no. iterations used')

# the max distance between catalog line and initial guess line in triplet fit
KW_WAVE_TRP_CATGDIST = KW_WAVE_TRP_CATGDIST.copy(__NAME__)
KW_WAVE_TRP_CATGDIST.set(key='WAVTCATD',
                         comment='Triplet fit - max dist btwn line cat & guess')

# the fit degree for triplet fit
KW_WAVE_TRP_FITDEG = KW_WAVE_TRP_FITDEG.copy(__NAME__)
KW_WAVE_TRP_FITDEG.set(key='WAVTFDEG', comment='Triplet fit - fit degree')

# the minimum number of lines required per order in triplet fit
KW_WAVE_TRP_MIN_NLINES = KW_WAVE_TRP_MIN_NLINES.copy(__NAME__)
KW_WAVE_TRP_MIN_NLINES.set(key='WAVTMINL',
                           comment='Triplet fit - min no. lines req. per order')

# the total number of lines required in triplet fit
KW_WAVE_TRP_TOT_NLINES = KW_WAVE_TRP_TOT_NLINES.copy(__NAME__)
KW_WAVE_TRP_TOT_NLINES.set(key='WAVTTOTL',
                           comment='Triplet fit - total no. lines required')

# the degree(s) of fit to ensure continuity in triplet fit
KW_WAVE_TRP_ORDER_FITCONT = KW_WAVE_TRP_ORDER_FITCONT.copy(__NAME__)
KW_WAVE_TRP_ORDER_FITCONT.set(key='WAVTO{0:03d}',
                              comment='Triplet fit - order continuity fit')

# the iteration number for sigma clip in triplet fit
KW_WAVE_TRP_SCLIPNUM = KW_WAVE_TRP_SCLIPNUM.copy(__NAME__)
KW_WAVE_TRP_SCLIPNUM.set(key='WAVT_SCN',
                         comment='Triplet fit - iter no. for sig clip')

# the sigma clip threshold in triplet fit
KW_WAVE_TRP_SCLIPTHRES = KW_WAVE_TRP_SCLIPTHRES.copy(__NAME__)
KW_WAVE_TRP_SCLIPTHRES.set(key='WAVT_SCT',
                           comment='Triplet fit - sig clip threshold')

# the distance away in dv to reject order triplet in triplet fit
KW_WAVE_TRP_DVCUTORD = KW_WAVE_TRP_DVCUTORD.copy(__NAME__)
KW_WAVE_TRP_DVCUTORD.set(key='WAVT_DVO',
                         comment='Triplet fit - dist in dv per order to reject')

# the distance away in dv to reject all triplet in triplet fit
KW_WAVE_TRP_DVCUTALL = KW_WAVE_TRP_DVCUTALL.copy(__NAME__)
KW_WAVE_TRP_DVCUTALL.set(key='WAVT_DVA',
                         comment='Triplet fit - dist in dv all to reject')

# the wave resolution map dimensions
KW_WAVE_RES_MAPSIZE = KW_WAVE_RES_MAPSIZE.copy(__NAME__)
KW_WAVE_RES_MAPSIZE.set(key='WAVRE{0:03d}',
                        comment='Wave res map - map dimensions')

# the width of the box for wave resolution map
KW_WAVE_RES_WSIZE = KW_WAVE_RES_WSIZE.copy(__NAME__)
KW_WAVE_RES_WSIZE.set(key='WAVRSIZE',
                      comment='Wave res map - width of box')

# the max deviation in rms allowed in wave resolution map
KW_WAVE_RES_MAXDEVTHRES = KW_WAVE_RES_MAXDEVTHRES.copy(__NAME__)
KW_WAVE_RES_MAXDEVTHRES.set(key='WAVRDEV',
                            comment='Wave res map - max dev in rms allowed')

# the littrow start order used for HC
KW_WAVE_LIT_START_1 = KW_WAVE_LIT_START_1.copy(__NAME__)
KW_WAVE_LIT_START_1.set(key='WAVL1_ST', comment='Littrow HC - start value')

# the littrow end order used for HC
KW_WAVE_LIT_END_1 = KW_WAVE_LIT_END_1.copy(__NAME__)
KW_WAVE_LIT_END_1.set(key='WAVL1_EN', comment='Littrow HC - end value')

# the orders removed from the littrow test
KW_WAVE_LIT_RORDERS = KW_WAVE_LIT_RORDERS.copy(__NAME__)
KW_WAVE_LIT_RORDERS.set(key='WAVLR{0:03d}', comment='Littrow - removed orders')

# the littrow order initial value used for HC
KW_WAVE_LIT_ORDER_INIT_1 = KW_WAVE_LIT_ORDER_INIT_1.copy(__NAME__)
KW_WAVE_LIT_ORDER_INIT_1.set(key='WAVL1OIN',
                             comment='Littrow HC - order init value')

# the littrow order start value used for HC
KW_WAVE_LIT_ORDER_START_1 = KW_WAVE_LIT_ORDER_START_1.copy(__NAME__)
KW_WAVE_LIT_ORDER_START_1.set(key='WAVL1OST',
                              comment='Littrow HC - order start value')

# the littrow order end value used for HC
KW_WAVE_LIT_ORDER_END_1 = KW_WAVE_LIT_ORDER_END_1.copy(__NAME__)
KW_WAVE_LIT_ORDER_END_1.set(key='WAVL1OEN',
                            comment='Littrow HC - order end value')

# the littrow x cut step value used for HC
KW_WAVE_LITT_XCUTSTEP_1 = KW_WAVE_LITT_XCUTSTEP_1.copy(__NAME__)
KW_WAVE_LITT_XCUTSTEP_1.set(key='WAVL1XCT',
                            comment='Littrow HC - x cut step value')

# the littrow fit degree value used for HC
KW_WAVE_LITT_FITDEG_1 = KW_WAVE_LITT_FITDEG_1.copy(__NAME__)
KW_WAVE_LITT_FITDEG_1.set(key='WAVL1FDG',
                          comment='Littrow HC - littrow fit degree')

# the littrow extrapolation fit degree value used for HC
KW_WAVE_LITT_EXT_FITDEG_1 = KW_WAVE_LITT_EXT_FITDEG_1.copy(__NAME__)
KW_WAVE_LITT_EXT_FITDEG_1.set(key='WAVL1EDG',
                              comment='Littrow HC - extrapolation fit degree')

# the littrow extrapolation start order value used for HC
KW_WAVE_LITT_EXT_ORD_START_1 = KW_WAVE_LITT_EXT_ORD_START_1.copy(__NAME__)
KW_WAVE_LITT_EXT_ORD_START_1.set(key='WAVL1EST',
                                 comment='Littrow HC - extrap start order')

# the first order used for FP wave sol improvement
KW_WFP_ORD_START = KW_WFP_ORD_START.copy(__NAME__)
KW_WFP_ORD_START.set(key='WFP_ORD0',
                     comment='First order used for FP wave sol.')

# the last order used for FP wave sol improvement
KW_WFP_ORD_FINAL = KW_WFP_ORD_FINAL.copy(__NAME__)
KW_WFP_ORD_FINAL.set(key='WFP_ORD1',
                     comment='Last order used for FP wave sol.')

# the blaze threshold used for FP wave sol improvement
KW_WFP_BLZ_THRES = KW_WFP_BLZ_THRES.copy(__NAME__)
KW_WFP_BLZ_THRES.set(key='WFPBLZTH',
                     comment='Blaze threshold used for FP wave sol.')

# the minimum fp peak pixel sep used for FP wave sol improvement
KW_WFP_XDIFF_MIN = KW_WFP_XDIFF_MIN.copy(__NAME__)
KW_WFP_XDIFF_MIN.set(key='WFPXDIF0',
                     comment='Min fp peak pixel sep for FP wave sol.')

# the maximum fp peak pixel sep used for FP wave sol improvement
KW_WFP_XDIFF_MAX = KW_WFP_XDIFF_MAX.copy(__NAME__)
KW_WFP_XDIFF_MAX.set(key='WFPXDIF1',
                     comment='Max fp peak pixel sep for FP wave sol.')

# the initial value of the FP effective cavity width used
KW_WFP_DOPD0 = KW_WFP_DOPD0.copy(__NAME__)
KW_WFP_DOPD0.set(key='WFPDOPD0',
                 comment='initial value of Fp effective cavity width')

# the  maximum fraction wavelength offset btwn xmatch fp peaks used
KW_WFP_LL_OFFSET = KW_WFP_LL_OFFSET.copy(__NAME__)
KW_WFP_LL_OFFSET.set(key='WFPLLOFF',
                     comment='max frac. wavelength offset btwn fp peaks')

# the max dv to keep hc lines used
KW_WFP_DVMAX = KW_WFP_DVMAX.copy(__NAME__)
KW_WFP_DVMAX.set(key='WFPDVMAX',
                 comment='max dv to kee[ hc lines for fp wave sol.')

# the used polynomial fit degree (to fit wave solution)
KW_WFP_LLFITDEG = KW_WFP_LLFITDEG.copy(__NAME__)
KW_WFP_LLFITDEG.set(key='WFPLLDEG',
                    comment='Used poly fit degree for fp wave sol.')

# whether the cavity file was updated
KW_WFP_UPDATECAV = KW_WFP_UPDATECAV.copy(__NAME__)
KW_WFP_UPDATECAV.set(key='WFPUPCAV',
                     comment='Whether wave sol. was used to update cav file')

# the mode used to fit the FP cavity
KW_WFP_FPCAV_MODE = KW_WFP_FPCAV_MODE.copy(__NAME__)
KW_WFP_FPCAV_MODE.set(key='WFPCAVMO',
                      comment='The mode used to fit the FP cavity')

# the mode used to fit the wavelength
KW_WFP_LLFIT_MODE = KW_WFP_LLFIT_MODE.copy(__NAME__)
KW_WFP_LLFIT_MODE.set(key='WFPLLFMO',
                      comment='The mode used to fit the wavelength sol.')

# the minimum instrumental error used
KW_WFP_ERRX_MIN = KW_WFP_ERRX_MIN.copy(__NAME__)
KW_WFP_ERRX_MIN.set(key='WFPERRXM',
                    comment='The minimum instrumental error used for wave sol.')

# the max rms for the wave sol sig clip
KW_WFP_MAXLL_FIT_RMS = KW_WFP_MAXLL_FIT_RMS.copy(__NAME__)
KW_WFP_MAXLL_FIT_RMS.set(key='WFPMAXLL',
                         comment='The max rms for the FP wave sol sig cut')

# the echelle number used for the first order
KW_WFP_T_ORD_START = KW_WFP_T_ORD_START.copy(__NAME__)
KW_WFP_T_ORD_START.set(key='WFPTORD',
                       comment='The echelle number of order 0 (fp wave sol.)')

# the weight below which fp lines are rejected
KW_WFP_WEI_THRES = KW_WFP_WEI_THRES.copy(__NAME__)
KW_WFP_WEI_THRES.set(key='WFPWTHRE',
                     comment='The weight below which FP lines are rejected')

# the polynomial degree fit order used for fitting the fp cavity
KW_WFP_CAVFIT_DEG = KW_WFP_CAVFIT_DEG.copy(__NAME__)
KW_WFP_CAVFIT_DEG.set(key='WFPCVFIT',
                      comment='The fit degree used for fitting the fp cavity')

# the largest jump in fp that was allowed
KW_WFP_LARGE_JUMP = KW_WFP_LARGE_JUMP.copy(__NAME__)
KW_WFP_LARGE_JUMP.set(key='WFPLJUMP',
                      comment='The largest jump in fp that is allowed')

# the index to start crossmatching fps at
KW_WFP_CM_INDX = KW_WFP_CM_INDX.copy(__NAME__)
KW_WFP_CM_INDX.set(key='WFPCMIND',
                   comment='The index to start crossmatch at')

# border size allowed to fit fps used
KW_WFP_BORDER = KW_WFP_BORDER.copy(__NAME__)
KW_WFP_BORDER.set(key='WFPBORDR',
                  comment='Allowed border size for fittin FPs')

# the box size used to fit fps (half-size)
KW_WFP_BSIZE = KW_WFP_BSIZE.copy(__NAME__)
KW_WFP_BSIZE.set(key='WFPBSIZE', comment='half box size used to fit FPs')

# the sigma above median a peak must have to be a valid fp peak used
KW_WFP_SIGLIM = KW_WFP_SIGLIM.copy(__NAME__)
KW_WFP_SIGLIM.set(key='WFPSIGLM',
                  comment='sigma above median for FP peak to be valid')

# the lamp value that was used
KW_WFP_LAMP = KW_WFP_LAMP.copy(__NAME__)
KW_WFP_LAMP.set(key='WFPLAMP', comment='Lamp value used for FP wave sol.')

# the minimum spacing between peaks used
KW_WFP_IPEAK_SPACE = KW_WFP_IPEAK_SPACE.copy(__NAME__)
KW_WFP_IPEAK_SPACE.set(key='WFPIPKSP',
                       comment='Min spacing between FP peaks used.')

# the expected width of the FP peaks used
KW_WFP_EXPWIDTH = KW_WFP_EXPWIDTH.copy(__NAME__)
KW_WFP_EXPWIDTH.set(key='WFPEXPWD', comment='expected width of FP peaks')

# the normalised cut width for large peaks used
KW_WFP_CUTWIDTH = KW_WFP_CUTWIDTH.copy(__NAME__)
KW_WFP_CUTWIDTH.set(key='WFPCUTWD',
                    comment='Normalised cut width used for large FP peaks')

# Wavelength solution for fiber C that is is source of the WFP keys
KW_WFP_FILE = KW_WFP_FILE.copy(__NAME__)
KW_WFP_FILE.set(key='WFP_FILE', comment='WFP source file')

# drift of the FP file used for the wavelength solution
KW_WFP_DRIFT = KW_WFP_DRIFT.copy(__NAME__)
KW_WFP_DRIFT.set(key='WFPDRIFT',
                 comment='Wavelength sol absolute CCF FP Drift [km/s]')

# FWHM of the wave FP file CCF
KW_WFP_FWHM = KW_WFP_FWHM.copy(__NAME__)
KW_WFP_FWHM.set(key='WFPFWHM', comment='FWHM of wave sol FP CCF [km/s]')

# Contrast of the wave FP file CCF
KW_WFP_CONTRAST = KW_WFP_CONTRAST.copy(__NAME__)
KW_WFP_CONTRAST.set(key='WFPCONT', comment='wave sol FP Contrast of CCF (%)')

# Max count/pixel of the wave FP file CCF
KW_WFP_MAXCPP = KW_WFP_MAXCPP.copy(__NAME__)
KW_WFP_MAXCPP.set(key='WFPMACPP',
                  comment='wave sol FP max count/pixel of CCF (e-)')

# Mask for the wave FP file CCF
KW_WFP_MASK = KW_WFP_MASK.copy(__NAME__)
KW_WFP_MASK.set(key='WFPMASK', comment='wave sol FP Mask filename')

# Number of lines for the wave FP file CCF
KW_WFP_LINES = KW_WFP_LINES.copy(__NAME__)
KW_WFP_LINES.set(key='WFPLINE', comment='wave sol FP nbr of lines used')

# Target RV for the wave FP file CCF
KW_WFP_TARG_RV = KW_WFP_TARG_RV.copy(__NAME__)
KW_WFP_TARG_RV.set(key='WFPTRV', comment='wave sol FP target RV [km/s]')

# Width for the wave FP file CCF
KW_WFP_WIDTH = KW_WFP_WIDTH.copy(__NAME__)
KW_WFP_WIDTH.set(key='WFPWIDTH', comment='wave sol FP CCF width [km/s]')

# Step for the wave FP file CCF
KW_WFP_STEP = KW_WFP_STEP.copy(__NAME__)
KW_WFP_STEP.set(key='WFPSTEP', comment='wave sol FP CCF step [km/s]')

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

# The original tapas file used for mktellu calculation
KW_MKTELL_TAPASFILE = KW_MKTELL_TAPASFILE.copy(__NAME__)
KW_MKTELL_TAPASFILE.set(key='MKTTAPAS', comment='mktellu tapas file used')

# The mean line width in pix used for mktellu calculation
KW_MKTELL_FWHMPLSF = KW_MKTELL_FWHMPLSF.copy(__NAME__)
KW_MKTELL_FWHMPLSF.set(key='MKTFWHMP', comment='mktellu FWHM pixel LSF used')

# The default convolution width in pix used for mktellu calculation
KW_MKTELL_DEF_CONV_WID = KW_MKTELL_DEF_CONV_WID.copy(__NAME__)
KW_MKTELL_DEF_CONV_WID.set(key='MKTDCONV',
                           comment='mktellu default conv width used')

# The finer convolution width in pix used for mktellu calculation
KW_MKTELL_FIN_CONV_WID = KW_MKTELL_FIN_CONV_WID.copy(__NAME__)
KW_MKTELL_FIN_CONV_WID.set(key='MKTFCONV',
                           comment='mktellu finer conv width used')

# The median filter width used for mktellu calculation
KW_MKTELL_TEMP_MEDFILT = KW_MKTELL_TEMP_MEDFILT.copy(__NAME__)
KW_MKTELL_TEMP_MEDFILT.set(key='MKT_TMED',
                           comment='mktellu template med filter used')

# The threshold in absorbance used for mktellu calculation
KW_MKTELL_DPARAM_THRES = KW_MKTELL_DPARAM_THRES.copy(__NAME__)
KW_MKTELL_DPARAM_THRES.set(key='MKTDPART',
                           comment='mktellu absorbance threshold used')

# The max num of iterations used for mktellu calculation
KW_MKTELL_MAX_ITER = KW_MKTELL_MAX_ITER.copy(__NAME__)
KW_MKTELL_MAX_ITER.set(key='MKTMAXIT', comment='mktellu max iterations used')

# The min transmission requirement used for mktellu calculation
KW_MKTELL_THRES_TFIT = KW_MKTELL_THRES_TFIT.copy(__NAME__)
KW_MKTELL_THRES_TFIT.set(key='MKTTTFIT',
                         comment='mktellu min transmission used')

# The min allowed value for recovered water vapor optical depth in mktellu
KW_MKTELL_MIN_WATERCOL = KW_MKTELL_MIN_WATERCOL.copy(__NAME__)
KW_MKTELL_MIN_WATERCOL.set(key='MKTMINWC',
                           comment='mktellu min water col opt. depth allowed')

# The max allowed value for recovered water vapor optical depth in mktellu
KW_MKTELL_MAX_WATERCOL = KW_MKTELL_MAX_WATERCOL.copy(__NAME__)
KW_MKTELL_MAX_WATERCOL.set(key='MKTMAXWC',
                           comment='mktellu max water col opt. depth allowed')

# The min num of good points requirement used for mktellu calculation
KW_MKTELL_MIN_NUM_GOOD = KW_MKTELL_MIN_NUM_GOOD.copy(__NAME__)
KW_MKTELL_MIN_NUM_GOOD.set(key='MKTMNUMG',
                           comment='mktellu min num good points required')

# The transmission percentile used to normalise by for mktellu calculation
KW_MKTELL_BTRANS_PERC = KW_MKTELL_BTRANS_PERC.copy(__NAME__)
KW_MKTELL_BTRANS_PERC.set(key='MKTBTRP',
                          comment='mktellu trans percentile used for norm')

# The sigma clip used to clip residuals of the diff for mktellu calculation
KW_MKTELL_NSIGCLIP = KW_MKTELL_NSIGCLIP.copy(__NAME__)
KW_MKTELL_NSIGCLIP.set(key='MKTNSIGC', comment='mktellu sig clip res diff used')

# The median filter used for the trans data used for mktellu calculation
KW_MKTELL_TRANS_TMFILT = KW_MKTELL_TRANS_TMFILT.copy(__NAME__)
KW_MKTELL_TRANS_TMFILT.set(key='MKTTTMF',
                           comment='mktellu med filt used for trans data')

# The threshold for small values to be weighted used for mktellu calculation
KW_MKTELL_SMALL_W_ERR = KW_MKTELL_SMALL_W_ERR.copy(__NAME__)
KW_MKTELL_SMALL_W_ERR.set(key='MKTSMWE', comment='mktellu small weight value')

# The image pixel size used (in km/s) used for mktellu calculation
KW_MKTELL_IM_PSIZE = KW_MKTELL_IM_PSIZE.copy(__NAME__)
KW_MKTELL_IM_PSIZE.set(key='MKTIMPS', comment='mktellu image pixel size used')

# The upper lim allowed for optical depth of water used for mktellu calculation
KW_MKTELL_TAU_WATER_U = KW_MKTELL_TAU_WATER_U.copy(__NAME__)
KW_MKTELL_TAU_WATER_U.set(key='MKTTAUWU',
                          comment='mktellu upper limit for tau water')

# The lower lim allowed for other absorbers used for mktellu calculation
KW_MKTELL_TAU_OTHER_L = KW_MKTELL_TAU_OTHER_L.copy(__NAME__)
KW_MKTELL_TAU_OTHER_L.set(key='MKTTAUOL',
                          comment='mktellu lower limit for tau others')

# The upper lim allowed for other absorbers used for mktellu calculation
KW_MKTELL_TAU_OTHER_U = KW_MKTELL_TAU_OTHER_U.copy(__NAME__)
KW_MKTELL_TAU_OTHER_U.set(key='MKTTAUOU',
                          comment='mktellu upper limit for tau others')

# The bad values are set to this small number, used for mktellu calculation
KW_MKTELL_TAPAS_SNUM = KW_MKTELL_TAPAS_SNUM.copy(__NAME__)
KW_MKTELL_TAPAS_SNUM.set(key='MKTTAPSN',
                         comment='mktellu tapas small bad num')

# The recovered airmass value calculated in mktellu calculation
KW_MKTELL_AIRMASS = KW_MKTELL_AIRMASS.copy(__NAME__)
KW_MKTELL_AIRMASS.set(key='TAU_H2O',
                      comment='mktellu recovered airmass (tau H2O)')

# The recovered water optical depth calculated in mktellu calculation
KW_MKTELL_WATER = KW_MKTELL_WATER.copy(__NAME__)
KW_MKTELL_WATER.set(key='TAU_OTHE',
                    comment='mktellu recovered depth others (tau other)')

# -----------------------------------------------------------------------------
# Define fit telluric variables
# -----------------------------------------------------------------------------
# The number of principle components used
KW_FTELLU_NPC = KW_FTELLU_NPC.copy(__NAME__)
KW_FTELLU_NPC.set(key='FTT_NPC',
                  comment='ftellu Number of principal components used')

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

# Telluric principle component amplitudes (for use with 1D list)
KW_FTELLU_AMP_PC = KW_FTELLU_AMP_PC.copy(__NAME__)
KW_FTELLU_AMP_PC.set(key='AMPPC{0:03d}',
                     comment='Principle Component Amplitudes')

# Telluric principle component first derivative
KW_FTELLU_DVTELL1 = KW_FTELLU_DVTELL1.copy(__NAME__)
KW_FTELLU_DVTELL1.set(key='DV_TELL1', comment='Principle Component first der.')

# Telluric principle component second derivative
KW_FTELLU_DVTELL2 = KW_FTELLU_DVTELL2.copy(__NAME__)
KW_FTELLU_DVTELL2.set(key='DV_TELL1', comment='Principle Component second der.')

# Tau Water depth calculated in fit tellu
KW_FTELLU_TAU_H2O = KW_FTELLU_TAU_H2O.copy(__NAME__)
KW_FTELLU_TAU_H2O.set(key='TAU_H20', comment='TAPAS tau H2O')

# Tau Rest depth calculated in fit tellu
KW_FTELLU_TAU_REST = KW_FTELLU_TAU_REST.copy(__NAME__)
KW_FTELLU_TAU_REST.set(key='TAU_OTHE',
                       comment='TAPAS tau for O2,O3,CH4,N2O,CO2')

# -----------------------------------------------------------------------------
# Define make template variables
# -----------------------------------------------------------------------------
# the snr order used for quality control cut in make template calculation
KW_MKTEMP_SNR_ORDER = KW_MKTEMP_SNR_ORDER.copy(__NAME__)
KW_MKTEMP_SNR_ORDER.set(key='MTPSNROD', comment='mktemplate snr order used')

# the snr threshold used for quality control cut in make template calculation
KW_MKTEMP_SNR_THRES = KW_MKTEMP_SNR_THRES.copy(__NAME__)
KW_MKTEMP_SNR_THRES.set(key='MTPSNRTH', comment='mktemplate snr threshold used')

