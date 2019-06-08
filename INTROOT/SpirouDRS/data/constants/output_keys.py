# ========================================================
#   Output keys
# ========================================================
#
#     These are the keys assigned to output files
#     in the header (on file saving)
#
#     - Obviously this is only for output fits files!
#
#     Format:
#              key = "value"    or  key = 'value'
#

# Defines the dark file tag
DARK_FILE = 'DARK'

# Defines the bad pix  tag from cal_DARK
DARK_BADPIX_FILE = 'DARK_BADPIX'

# Define the dark master file tag from cal_dark_master
DARK_MASTER_FILE = 'DARK_MASTER'

# Defines the bad pixel tag from cal_BADPIX
BADPIX_FILE = 'BADPIX'

# Defines the background map tag from cal_BADPIX
BKGD_MAP_FILE = 'BKGRD_MAP'

# Defines the localisation order profile tag
LOC_ORDER_PROFILE_FILE = 'LOC_ORDERP'

# Defines the localisation file tag
LOC_LOCO_FILE = 'LOC_LOCO'

# Defines the localisation fwhm file tag
LOC_LOCO_FILE2 = 'LOC_FWHM'

# Defines the localisation superposition file tag
LOC_LOCO_FILE3 = 'LOC_SUP'

# Defines the slit tilt file tag
SLIT_TILT_FILE = 'SLIT_TILT'

# Define the shape file tags
SLIT_XSHAPE_FILE = 'SLIT_SHAPE_X'
SLIT_YSHAPE_FILE = 'SLIT_SHAPE_Y'
SLIT_SHAPE_LOCAL_FILE = 'SLIT_SHAPE'

# Define the master FP file tag
SLIT_MASTER_FP_FILE = 'MASTER_FP'

# Define the shape sanity check debug files
SLIT_SHAPE_IN_FP_FILE = 'SHAPE_IN_FP'
SLIT_SHAPE_OUT_FP_FILE = 'SHAPE_OUT_FP'
SLIT_SHAPE_IN_HC_FILE = 'SHAPE_IN_HC'
SLIT_SHAPE_OUT_HC_FILE = 'SHAPE_OUT_HC'
SLIT_SHAPE_OVERLAP_FILE = 'SHAPE_ORD_OVERLAP'

# Defines the flat fielding blaze file tag
FF_BLAZE_FILE = 'FF_BLAZE'

# Defines the flat fielding flat
FF_FLAT_FILE = 'FF_FLAT'

# Defines the E2DS file tag
EXTRACT_E2DS_FILE = 'EXT_E2DS'

# Defines the E2DS flat-fielded file tag
EXTRACT_E2DSFF_FILE = 'EXT_E2DS_FF'

# Defines the E2DS non-folded file tag
EXTRACT_E2DSLL_FILE = 'EXT_E2DS_LL'

# Defines the extraction localisation file tag
EXTRACT_LOCO_FILE = 'EXT_LOCO'

# Defines the extraction S1D file tag
EXTRACT_S1D_FILE = 'EXT_S1D'

# Defines the raw drift file tag
DRIFT_RAW_FILE = 'DRIFT_RAW'

# Defines the E2DS drift file tag
DRIFT_E2DS_FITS_FILE = 'DRIFT_E2DS'

# Defines the E2DS drift-peak file tag
DRIFTPEAK_E2DS_FITS_FILE = 'DRIFTPEAK_E2DS'

# Define the E2DS drift-ccf file tag
DRIFTCCF_E2DS_FITS_FILE = 'DRIFTCCF_E2DS'

# Defines the CCF file tag
CCF_FITS_FILE = 'CCF_E2DS'
CCF_FITS_FILE_FF = 'CCF_E2DS_FF'
CCF_FP_FITS_FILE = 'CCF_E2DS_FP'
CCF_FP_FITS_FILE_FF = 'CCF_E2DS_FP_FF'

# Defines the exposure meter telluric spectrum map file tag
EM_SPE_FILE = 'EM_TELL_SPEC'

# Defines the exposure meter wave map file tag
EM_WAVE_FILE = 'EM_WAVEMAP'

# Defines the exposure meter mask file tag
EM_MASK_FILE = 'EM_MASK'

# Defines the exposure meter wave map SPE file tag
WAVE_MAP_SPE_FILE = 'EM_WAVEMAP_SPE'
WAVE_MAP_SPE0_FILE = 'EM_WAVEMAP_SPE0'

# Defines the wave solution file tag
WAVE_FILE = 'WAVE_SOL'
WAVE_FILE_EA = 'WAVE_SOL_EA'

# Defines the wave solution with fp file tag
WAVE_FILE_FP = 'WAVE_FP_SOL'

# Defines the wave solution copy of E2DS file tag
WAVE_E2DS_COPY = 'WAVE_E2DSCOPY'

# Defines the wave resolution fits file tag
WAVE_RES_FILE_EA = 'WAVE_RES'

# Defines the telluric trans map file tag
TELLU_TRANS_MAP_FILE = 'TELLU_TRANS'

# Defines the telluric absorption map file tag
TELLU_ABSO_MAP_FILE = 'TELLU_ABSO_MAP'

# Defines the telluric absorption median file tag
TELLU_ABSO_MEDIAN_FILE = 'TELLU_ABSO_MED'

# Defines the telluric absorption norm file tag
TELLU_ABSO_NORM_MAP_FILE = 'TELLU_ABSO_NORM'

# Defines the telluric corrected output file tag
TELLU_FIT_OUT_FILE = 'TELLU_CORRECTED'

# Defines the telluric reconstructed file tag
TELLU_FIT_RECON_FILE = 'TELLU_RECON'

# Define the telluric extraction S1D file tags
TELLU_S1D_FILE1 = 'TELLU_S1D_W'
TELLU_S1D_FILE2 = 'TELLU_S1D_V'

# Defines the object tellu template file tag
OBJTELLU_TEMPLATE_FILE = 'OBJTELLU_TEMPLATE'

# Defines the object tellu bigcube template file tag
OBJTELLU_TEMPLATE_CUBE_FILE1 = 'OBJTELLU_BIG1'
OBJTELLU_TEMPLATE_CUBE_FILE2 = 'OBJTELLU_BIG0'

# Defines the polarisation file tag
DEG_POL_FILE = 'POL_DEG'

# Defines the polarisation stokes I file tag
STOKESI_POL_FILE = 'POL_STOKES_I'

# Defines the polarisation null pol1 file tag
NULL_POL1_FILE = 'POL_NULL_POL1'

# Defines the polarisation null pol2 file tag
NULL_POL2_FILE = 'POL_NULL_POL2'

# Defines the polarisation LSD file tag
LSD_POL_FILE = 'POL_LSD'
