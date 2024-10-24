.. _glossary:

************
Glossary
************


.. _glossary_constants:

Detailed Constants
===================

These are usually defined in the instruments :file:`default_config.py` and
:file:`default_constants.py` scripts and are overwritten in the :file:`user_config.ini` and
:file`user_constant.ini` files.

.. glossary::

  DRS_ROOT

    * This is the path where apero-drs was installed (via github)
    * a suggested directory is :file:`/home/user/bin/apero-drs`

  DRS_UCONFIG

    * The directory containing the users configurations files
    * default is :file:`/home/user/apero/{PROFILE}`

  DrsInputFile

    * This is a class controlling how files are defined - it comes in three
      flavors - a generic file type (:meth:`apero.core.core.drs_file.DrsInputFile`),
      a fits file type (:meth:`apero.core.core.drs_file.DrsFitsFile`) and a
      temporary numpy file type (:meth:`apero.core.core.drs_file.DrsNPYFile`)



Detailed Keywords
==================

These are usually defined in the instruments :file:`default_keywords.py` script.
These keywords control what keys are read from fits headers and also what
keys and comments are saved to fits headers.

.. glossary::

    KW_GAIA_ID

        * This is the gaia id key from the header
        * The header value should contain a valid gaia id
        * This key is used to cross-match with the object database and with
          gaia online database to get position and velocity data precise enough
          for a good BERV correction
        * If key is missing or invalid the BERV calculation defers to the header
          values for position and velocity (may be less precise).

    KW_OBJECTNAME

        * This is the object name used from the header
        * This is the unmodified value from the fits file creation
        * It is cleaned and then added to a new header key (:term:`KW_OBJNAME`)

    KW_OBJNAME

        * This is the cleaned object name - suitable for use throughout APERO.
        * Currently it is cleaned using and instruments :term:`PseudoConst` cleaning function
          e.g. :meth:`apero.core.instruments.spirou.pseudo_const.clean_obj_name`


.. _glossary_main:

General
======== 

.. glossary::  

  block_kind

    * this is the type of file we have related to the various data directories
    * valid block kinds are: "raw", "tmp", "red", "calib", "tellu"

  ds9

    * An astronomical imaging and data visualization application
    * see `ds9.si.edu <http://ds9.si.edu/site/Home.html>`_

  engineering-directories

    * This are directories without science observations in
    * In general we do not recommend to reduce these nights as they may
      reduce the quality of reduced data

  file-definitions

    * This is an instrument specific python script that defines all the
      file types for use with this instrument (raw, preprocessed, output).
    * Each file definition is a :term:`DrsInputFile` instance

  INSTRUMENT

    * This is the instrument used at a specific telescope. Some settings are instrument specific.
    * Currently supported instruments are::
      SPIROU, NIRPS_HA, NIRPS_HE


  observation-directory

    * This is the sub-directories within the raw directory (define by :term:`DRS_DATA_RAW`) that individual
      observations are separated into, this is recommended to be on a night-by-night basis but can be split in
      other ways (for example by object name).

  PID

    * The unique process id for this specific :term:`recipe-run`
    * Stored in the header using :term:`KW_PID`

  pdflatex

    * The pdf latex compiler
    * see `www.latex-project.org <https://www.latex-project.org/get/>`_

  pre-processing-coordinate-system

    * This is the standard coordinate system for pre-processed images
    * It consists of the bluest wavelength at the top right and the reddest
      order in the bottom left

  PROFILE

    * This is a short descriptive name given to a specific set of installation configurations
    * Each profile contains setup files: :file:`{PROFILE}.bash.setup file`, :file:`{PROFILE}.sh.setup file`
    * Each profile contains an instrument directory for each instrument. These contain user_config.ini and user_constant.ini files for said instrument.


  PseudoConst

    * This is an instrument specific class that has functions that cannot be
      simply defined by an integer, float or string
    * Sometimes pseudo constant methods require input and are hence dynamic
    * They are located in the instrument directory
      e.g. :meth:`apero.core.instruments.spirou.psuedo_const`
    * There is also a default psuedo constant class which all instruments
      inherit from - if no instrument is defined, or a method is not defined
      for a specific instrument it will default to this method - this is stored
      in :meth:`apero.core.instruments.default.psuedo_const`


  recipe

    * a python script for use directly by the user

  recipe-run

    * An individual, single, run of a given recipe, all required arguments for a single
      recipe-run should be given before running

  recipe-sequence, recipe-sequences

    * A recipe sequence is a set of recipes to be run in a certain order, with
      certain parameters, the sequences are set up such that the apero_processing recipe
      can take all files in the raw directory (or a sub-set of these) and figure out
      all recipe-runs in a recipe-sequence for all the valid raw files. A sequence
      can be only a few different recipes or all recipes required for the full reduction
      of the raw data from start to finish.

  run-ini-file

    * This is the file used in apero_processing recipe to switch on and off recipes in sequences,
      to skip recipes, and indicate other processing features (such as the number of cores)
      these are also used in the apero_precheck to give some indication on what will happen
      when the apero_processing recipe is run. If no sequences are given one can use
      the run.ini files as a batch processor where individual recipe-runs can be given

  shortname

    * a shortened name for a specific recipe, these are used in log files, when
      turning off and skipping recipes in a :term:run-ini-file and elsewhere to
      reference a specific recipe, please check the recipe definitions for the link
      between short name and recipe names (Note some sequences alter shortnames when
      they need to be unique from the recipes themselves).


Constants (Autogen)
======================

.. glossary::



  ALLOWED_DARK_TYPES

    * Description: Define the allowed DPRTYPES for finding files for DARK_MASTER will only find those types define by filetype but filetype must be one of theses (strings separated by commas)
    * Type: str

  ALLOWED_FP_TYPES

    * Description: Define the allowed DPRTYPES for finding files for SHAPE_MASTER will only find those types define by filetype but filetype must be one of theses (strings separated by commas)
    * Type: str

  ALLOWED_LEAKM_TYPES

    * Description: Define the types of input file allowed by the leakage master recipe
    * Type: str

  ALLOWED_LEAK_TYPES

    * Description: Define the types of input extracted files to correct for leakage
    * Type: str

  ALLOWED_PPM_TYPES

    * Description: Define allowed preprocess master filetypes (PP DPRTYPE)
    * Type: str

  ALLOW_BREAKPOINTS

    * Description: whether to allow break points
    * Type: bool

  AUTHORS

    * Description: Authors
    * Type: list

  BADPIX_FLAT_CUT_RATIO

    * Description: Define the maximum differential pixel cut ratio
    * Type: float
    * Minimum: 0.0

  BADPIX_FLAT_MED_WID

    * Description: Define the median image in the x dimension over a boxcar of this width
    * Type: int
    * Minimum: 0

  BADPIX_FULL_FLAT

    * Description: Defines the full detector flat file (located in the data folder)
    * Type: str

  BADPIX_FULL_THRESHOLD

    * Description: Defines the threshold on the full detector flat file to deem pixels as good
    * Type: float
    * Minimum: 0.0

  BADPIX_ILLUM_CUT

    * Description: Define the illumination cut parameter
    * Type: float
    * Minimum: 0.0

  BADPIX_MAX_HOTPIX

    * Description: Define the maximum flux in ADU/s to be considered too hot to be used
    * Type: float
    * Minimum: 0.0

  BADPIX_NORM_PERCENTILE

    * Description: Percentile to normalise to when normalising and median filtering image [percentage]
    * Type: float
    * Minimum: 0.0
    * Maximum: 100.0

  BKGR_BOXSIZE

    * Description: Width of the box to produce the background mask
    * Type: int
    * Minimum: 0

  BKGR_KER_AMP

    * Description: Kernel amplitude determined from drs_local_scatter.py
    * Type: float

  BKGR_KER_SIG

    * Description: construct a convolution kernel. We go from -IC_BKGR_KER_SIG to +IC_BKGR_KER_SIG sigma in each direction. Its important no to make the kernel too big as this slows-down the 2D convolution. Do NOT make it a -10 to +10 sigma gaussian!
    * Type: float

  BKGR_KER_WX

    * Description: Background kernel width in in x and y [pixels]
    * Type: int

  BKGR_KER_WY

    * Description:
    * Type: int

  BKGR_MASK_CONVOLVE_SIZE

    * Description: Size in pixels of the convolve tophat for the background mask
    * Type: int
    * Minimum: 0

  BKGR_NO_SUBTRACTION

    * Description: Do not correct for background measurement (True or False)
    * Type: bool

  BKGR_N_BAD_NEIGHBOURS

    * Description: If a pixel has this or more "dark" neighbours, we consider it dark regardless of its initial value
    * Type: int
    * Minimum: 0

  BKGR_PERCENTAGE

    * Description: Do background percentile to compute minimum value (%)
    * Type: float
    * Minimum: 0.0
    * Maximum: 100.0

  CALIB_CHECK_FP_CENT_SIZE

    * Description: define the check FP center image size [px]
    * Type: int
    * Minimum: 0

  CALIB_CHECK_FP_PERCENTILE

    * Description: define the check FP percentile level
    * Type: int
    * Minimum: 0

  CALIB_CHECK_FP_THRES

    * Description: define the check FP threshold qc parameter
    * Type: float
    * Minimum: 0.0

  CALIB_DB_FORCE_WAVESOL

    * Description: Define whether to force wave solution from calibration database (instead of using header wave solution if available)
    * Type: bool

  CALIB_DB_MATCH

    * Description: Define the match type for calibDB filesmatch = older when more than one file for each key will select the newest file that is OLDER than time in fitsfilename match = closest when more than on efile for each key will select the file that is closest to time in fitsfilename if two files match with keys and time the key lower in the calibDB file will be used
    * Type: str

  CAVITY_1M_FILE

    * Description: Define the coefficients of the fit of 1/m vs d
    * Type: str

  CAVITY_LL_FILE

    * Description: Define the coefficients of the fit of wavelength vs d
    * Type: str

  CCF_ALLOWED_DPRTYPES

    * Description: Allowed input DPRTYPES for input for CCF recipe
    * Type: str

  CCF_BLAZE_NORM_PERCENTILE

    * Description: Define the percentile the blaze is normalised by before using in CCF calc
    * Type: float
    * Minimum: 0
    * Maximum: 100

  CCF_CORRECT_TELLU_TYPES

    * Description: Define the KW_OUTPUT types that are valid telluric corrected spectra
    * Type: str

  CCF_DEFAULT_MASK

    * Description: Define the default CCF MASK to use
    * Type: str

  CCF_DEFAULT_STEP

    * Description: Define the computations steps of the CCF [km/s]
    * Type: float
    * Minimum: 0.0

  CCF_DEFAULT_WIDTH

    * Description: Define the width of the CCF range [km/s]
    * Type: float
    * Minimum: 0.0

  CCF_DET_NOISE

    * Description: Define the detector noise to use in the ccf
    * Type: float

  CCF_FILL_NAN_KERN_RES

    * Description: the step size (in pixels) of the smoothing box used to calculate what value should replace the NaNs in the E2ds before CCF is calculated
    * Type: float

  CCF_FILL_NAN_KERN_SIZE

    * Description: The half size (in pixels) of the smoothing box used to calculate what value should replace the NaNs in the E2ds before CCF is calculated
    * Type: float

  CCF_FIT_TYPE

    * Description: Define the fit type for the CCF fit if 0 then we have an absorption line if 1 then we have an emission line
    * Type: int

  CCF_MASK_FMT

    * Type: str

  CCF_MASK_MIN_WEIGHT

    * Type: float
    * Minimum: 0.0

  CCF_MASK_NORMALIZATION

    * Type: str

  CCF_MASK_PATH

    * Type: str

  CCF_MASK_UNITS

    * Description: Define the wavelength units for the mask
    * Type: str

  CCF_MASK_WIDTH

    * Type: float
    * Minimum: 0.0

  CCF_MAX_CCF_WID_STEP_RATIO

    * Description: Define the maximum allowed ratio between input CCF STEP and CCF WIDTH i.e. error will be generated if CCF_STEP > (CCF_WIDTH / RATIO)
    * Type: float
    * Minimum: 1.0

  CCF_NOISE_BOXSIZE

    * Type: int
    * Minimum: 0.0

  CCF_NOISE_SIGDET

    * Type: float
    * Minimum: 0.0

  CCF_NOISE_THRES

    * Type: float
    * Minimum: 0.0

  CCF_NO_RV_VAL

    * Description: Define target rv the null value for CCF (only change if changing code)
    * Type: float

  CCF_N_ORD_MAX

    * Type: int
    * Minimum: 1

  CCF_OBJRV_NULL_VAL

    * Description: Define target rv header null value (values greater than absolute value are set to zero)
    * Type: float

  CCF_TELLU_THRES

    * Description: The transmission threshold for removing telluric domain (if and only if we have a telluric corrected input file
    * Type: float

  COMBINE_METRIC1_TYPES

    * Description: Define the DPRTYPES allowed for the combine metric 1 comparison
    * Type: str

  COMBINE_METRIC_THRESHOLD1

    * Description: Define the threshold under which a file should not be combined (metric is compared to the median of all files 1 = perfect, 0 = noise)
    * Type: float
    * Minimum: 0
    * Maximum: 1

  DARK_CUTLIMIT

    * Description: Define a bad pixel cut limit (in ADU/s)
    * Type: float

  DARK_MASTER_MATCH_TIME

    * Description: Define the maximum time span to combine dark files over (in hours)
    * Type: float

  DARK_MASTER_MED_SIZE

    * Description: median filter size for dark master
    * Type: int

  DARK_QMAX

    * Description:
    * Type: int
    * Minimum: 0
    * Maximum: 100

  DARK_QMIN

    * Description: Defines the lower and upper percentiles when measuring the dark
    * Type: int
    * Minimum: 0
    * Maximum: 100

  DATABASE_DIR

    * Description: Define database directory (relative to assets directory)
    * Type: str

  DATA_CORE

    * Description: Define core data path
    * Type: str

  DATA_ENGINEERING

    * Description: Define the data engineering path
    * Type: str

  DEBUG_MODE_FUNC_PRINT

    * Description: The debug number to print function definitions
    * Type: int

  DEBUG_MODE_LOG_PRINT

    * Description: The debug number to print debug log messages
    * Type: int

  DEBUG_MODE_TEXTNAME_PRINT

    * Description: The debug number to print text entry names on all messages
    * Type: int

  DRIFT_DPRTYPES

    * Description: Define the types of file allowed for drift measurement
    * Type: str

  DRIFT_DPR_FIBER_TYPE

    * Description: Define the fiber dprtype allowed for drift measurement (only FP)
    * Type: str

  DRS_BADPIX_DATA

    * Description: where the bad pixel data are stored (within assets directory)
    * Type: str

  DRS_CALIB_DATA

    * Description: where the calibration data are stored (within assets directory)
    * Type: str

  DRS_CALIB_DB

    * Description: Define the directory that the calibration files should be saved to/read from
    * Type: path

  DRS_COLOURED_LOG

    * Description: Coloured logging to standard output (console)
    * Type: bool

  DRS_DATA_ASSETS

    * Description: Define the assets directory
    * Type: path

  DRS_DATA_MSG

    * Description: Define the directory that the log messages are stored in
    * Type: path

  DRS_DATA_MSG_FULL

    * Description: Define the full data message path (set after group name known)
    * Type: path

  DRS_DATA_OUT

    * Description: Define the directory that the post processed data should be saved to
    * Type: path

  DRS_DATA_PLOT

    * Description: Define the plotting directory
    * Type: path

  DRS_DATA_RAW

    * Description: Define the folder with the raw data files in
    * Type: path

  DRS_DATA_REDUC

    * Description: Define the directory that the reduced data should be saved to/read from
    * Type: path

  DRS_DATA_RUN

    * Description: Define the run directory
    * Type: path

  DRS_DATA_WORKING

    * Description: Define the working directory
    * Type: path

  DRS_DATE

    * Description: Date
    * Type: str

  DRS_DEBUG

    * Description: Debug mode: 0: no debug 1: some debug output + python debugging 100: all in (1) and Language DB codes on all text 200: all in (100) + function entry printouts
    * Type: int

  DRS_DEFAULT_RECIPE_PATH

    * Description: where the default recipes are stored
    * Type: str

  DRS_DS9_PATH

    * Description: Define ds9 path (optional)
    * Type: str

  DRS_GROUP

    * Description: The group this target is set as (set in drs_setup)
    * Type: str

  DRS_HEADER

    * Description: DRS Header string
    * Type: str

  DRS_INDEX_FILE

    * Description: Define the name of the index file (in each working/reduced directory)
    * Type: str

  DRS_INDEX_FILENAME

    * Description: Define the filename column of the index file
    * Type: str

  DRS_INSTRUMENTS

    * Description: Currently supported instruments
    * Type: list

  DRS_INSTRUMENT_RECIPE_PATH

    * Description: where the instrument recipes are stored
    * Type: str

  DRS_LOG_CAUGHT_WARNINGS

    * Description: Defines a master switch, whether to report warnings that are caught in
    * Type: bool

  DRS_LOG_EXIT_TYPE

    * Description: Defines how python exits, when an exit is required after logging, string input fed into spirouConst.EXIT() if sys exits via sys.exit - soft exit (ipython Exception) if os exits via os._exit - hard exit (complete exit)
    * Type: str

  DRS_LOG_FITS_NAME

    * Description: Define the log fits file name
    * Type: str

  DRS_LOG_FORMAT

    * Description: Defines the DRS log format
    * Type: str

  DRS_LOG_LEVEL

    * Description: Level at which to log in log file, values can be: all - to print all events info - to print info/warning/error events warning - to print warning/error eventserror - to print only error events
    * Type: str

  DRS_MAX_IO_DISPLAY_LIMIT

    * Description: Maximum display limit for files/directory when argument error raise
    * Type: int

  DRS_MOD_CORE_CONFIG

    * Description: where the core configuration files are stored (do not change here)
    * Type: str

  DRS_MOD_DATA_PATH

    * Description: where to store internal data
    * Type: str

  DRS_MOD_INSTRUMENT_CONFIG

    * Description: where instrument configuration files are stored (do not change here)
    * Type: str

  DRS_PACKAGE

    * Description: The top-level package name (i.e. import PACKAGE)
    * Type: str

  DRS_PDB_RC_FILE

    * Description: where the pdb rc file is (do not change - just here for use)
    * Type: str

  DRS_PDB_RC_FILENAME

    * Description: what the pdb file should be called (do not change - just here for use)
    * Type: str

  DRS_PDFLATEX_PATH

    * Description: Define latex path (optional)
    * Type: str

  DRS_PLOT

    * Description: Plotting mode: 0: only summary plots 1: debug plots at end of code 2: debug plots at time of creation (pauses code)
    * Type: int

  DRS_PLOT_EXT

    * Description: Set the plot file extension
    * Type: str

  DRS_PLOT_FONT_FAMILY

    * Description: Set the default font family for all graphs (i.e. monospace) "None" for not set
    * Type: str

  DRS_PLOT_FONT_SIZE

    * Description: Set the default font size for all graphs (-1 for not set)
    * Type: int

  DRS_PLOT_FONT_WEIGHT

    * Description: Set the default font weight for all graphs (i.e. bold/normal) "None" for not set
    * Type: str

  DRS_PLOT_STYLE

    * Description: Set the default plotting style (i.e. seaborn or dark_background) "None" for not set
    * Type: str

  DRS_PRINT_LEVEL

    * Description: Level at which to print, values can be: all - to print all events info - to print info/warning/error events warning - to print warning/error events error - to print only error events
    * Type: str

  DRS_RECIPE_KIND

    * Description: The recipe kind that this parameter dictionary is associated with
    * Type: str

  DRS_RELEASE

    * Description: Release version
    * Type: str

  DRS_RESET_ASSETS_PATH

    * Description: where the assets directory is (relative to apero module)
    * Type: str

  DRS_RESET_CALIBDB_PATH

    * Description: where the reset data are stored (within assets directory) for calibDB (within assets directory)
    * Type: str

  DRS_RESET_RUN_PATH

    * Description: for run files (within assets directory)
    * Type: str

  DRS_RESET_TELLUDB_PATH

    * Description: for telluDB (within assets directory)
    * Type: str

  DRS_ROOT

    * Description: Define the root installation directory
    * Type: path

  DRS_SUMMARY_EXT

    * Description: Set the summary document extension
    * Type: str

  DRS_SUMMARY_STYLE

    * Description: Set the summary document style
    * Type: str

  DRS_TELLU_DB

    * Description: Define the directory that the calibration files should be saved to/read from
    * Type: path

  DRS_THEME

    * Description: Theme (DARK or LIGHT)
    * Type: str

  DRS_USERENV

    * Description: User-config environmental variable
    * Type: str

  DRS_USER_DEFAULT

    * Description: User-config default location (if environmental variable not set) this is relative to the package level
    * Type: str

  DRS_USER_PROGRAM

    * Description: User-defined program name (overwrite logging program)
    * Type: str

  DRS_VERSION

    * Description: Version
    * Type: str

  DRS_WAVE_DATA

    * Description: where the wave data are stored (within assets directory)
    * Type: str

  EXPMETER_MAX_LAMBDA

    * Description: Define exposure meter maximum wavelength for mask
    * Type: float

  EXPMETER_MIN_LAMBDA

    * Description: Define exposure meter minimum wavelength for mask
    * Type: float

  EXPMETER_TELLU_THRES

    * Description: Define exposure meter telluric threshold (minimum tapas transmission)
    * Type: float

  EXTRACT_PLOT_ORDER

    * Description: Define the order to plot in summary plots
    * Type: int

  EXTRACT_S1D_PLOT_ZOOM1

    * Description: Define the wavelength lower bounds for s1d plots (must be a string list of floats) defines the lower wavelength in nm
    * Type: str

  EXTRACT_S1D_PLOT_ZOOM2

    * Description: Define the wavelength upper bounds for s1d plots (must be a string list of floats) defines the upper wavelength in nm
    * Type: str

  EXT_ALLOWED_BERV_DPRTYPES

    * Description: Define dprtypes to calculate berv for
    * Type: str

  EXT_BERV_BARYCORRPY_DIR

    * Description: Define the barycorrpy data directory
    * Type: str

  EXT_BERV_EST_ACC

    * Description: Define the accuracy of the estimate (for logging only) [m/s]
    * Type: float

  EXT_BERV_IERSFILE

    * Description: Define the barycorrpy iers file
    * Type: str

  EXT_BERV_IERS_A_URL

    * Description: Define the barycorrpy iers a url
    * Type: str

  EXT_BERV_KIND

    * Description: Define which BERV calculation to use (barycorrpy or estimate or None)
    * Type: str

  EXT_BERV_LEAPDIR

    * Description: Define barycorrpy leap directory
    * Type: str

  EXT_BERV_LEAPUPDATE

    * Description: Define whether to update leap seconds if older than 6 months
    * Type: bool

  EXT_COSMIC_CORRETION

    * Description: Defines whether to run extraction with cosmic correction
    * Type: bool

  EXT_COSMIC_SIGCUT

    * Description: Define the percentage of flux above which we use to cut
    * Type: float

  EXT_COSMIC_THRESHOLD

    * Description: Defines the maximum number of iterations we use to check for cosmics (for each pixel)
    * Type: int

  EXT_END_ORDER

    * Description: End order of the extraction in cal_ff if None ends at last order
    * Type: int

  EXT_QUICK_LOOK

    * Description: Whether extraction code is done in quick look mode (do not use for final products)
    * Type: bool

  EXT_RANGE1

    * Description: Half-zone extraction width left side (formally plage1)
    * Type: str

  EXT_RANGE2

    * Description: Half-zone extraction width right side (formally plage2)
    * Type: str

  EXT_S1D_BIN_UVELO

    * Description: Define the s1d spectral bin for S1D spectra (km/s) when uniform in velocity
    * Type: float
    * Minimum: 0.0

  EXT_S1D_BIN_UWAVE

    * Description: Define the s1d spectral bin for S1D spectra (nm) when uniform in wavelength
    * Type: float
    * Minimum: 0.0

  EXT_S1D_EDGE_SMOOTH_SIZE

    * Description: Define the s1d smoothing kernel for the transition between orders in pixels
    * Type: int
    * Minimum: 0

  EXT_S1D_INFILE

    * Description: Define which extraction file (recipe definitons) linked to EXT_S1D_INTYPE
    * Type: str

  EXT_S1D_INTYPE

    * Description: Define which extraction file to use for s1d creation
    * Type: str

  EXT_S1D_WAVEEND

    * Description: Define the end s1d wavelength (in nm)
    * Type: float
    * Minimum: 0.0

  EXT_S1D_WAVESTART

    * Description: Define the start s1d wavelength (in nm)
    * Type: float
    * Minimum: 0.0

  EXT_SKIP_ORDERS

    * Description: Define the orders to skip extraction on (will set all order values to NaN. If None no orders are skipped. If Not None should be a string (valid python list)
    * Type: str

  EXT_START_ORDER

    * Description: Start order of the extraction in cal_ff if None starts from 0
    * Type: int

  FF_BLAZE_BPERCENTILE

    * Type: int
    * Minimum: 0

  FF_BLAZE_DEGREE

    * Description: The blaze polynomial fit degree
    * Type: int

  FF_BLAZE_HALF_WINDOW

    * Description: Half size blaze smoothing window
    * Type: int

  FF_BLAZE_SCUT

    * Description: Define the threshold, expressed as the fraction of the maximum peak, below this threshold the blaze (and e2ds) is set to NaN
    * Type: float

  FF_BLAZE_SIGFIT

    * Description: Define the rejection threshold for the blaze sinc fit
    * Type: float

  FF_BLAZE_THRESHOLD

    * Description: Minimum relative e2ds flux for the blaze computation
    * Type: float

  FF_PLOT_ORDER

    * Description: Define the order to plot in summary plots
    * Type: int

  FF_RMS_SKIP_ORDERS

    * Description: Define the orders not to plot on the RMS plot should be a string containing a list of integers
    * Type: str

  FIBER_FIRST_ORDER_JUMP_A

    * Description:
    * Type: int
    * Minimum: 0

  FIBER_FIRST_ORDER_JUMP_AB

    * Description: Number of orders to skip at start of image
    * Type: int
    * Minimum: 0

  FIBER_FIRST_ORDER_JUMP_B

    * Description:
    * Type: int
    * Minimum: 0

  FIBER_FIRST_ORDER_JUMP_C

    * Description:
    * Type: int
    * Minimum: 0

  FIBER_MAX_NUM_ORDERS_A

    * Description:
    * Type: int
    * Minimum: 1

  FIBER_MAX_NUM_ORDERS_AB

    * Description: Maximum number of order to use
    * Type: int
    * Minimum: 1

  FIBER_MAX_NUM_ORDERS_B

    * Description:
    * Type: int
    * Minimum: 1

  FIBER_MAX_NUM_ORDERS_C

    * Description:
    * Type: int
    * Minimum: 1

  FIBER_SET_NUM_FIBERS_A

    * Description:
    * Type: int
    * Minimum: 1

  FIBER_SET_NUM_FIBERS_AB

    * Description: Number of fibers
    * Type: int
    * Minimum: 1

  FIBER_SET_NUM_FIBERS_B

    * Description:
    * Type: int
    * Minimum: 1

  FIBER_SET_NUM_FIBERS_C

    * Description:
    * Type: int
    * Minimum: 1

  FIBER_TYPES

    * Description: Define the fibers
    * Type: str

  FP_MASTER_MATCH_TIME

    * Description: Define the maximum time span to combine fp files over (in hours)
    * Type: float

  FP_MASTER_PERCENT_THRES

    * Description: Define the percentile at which the FPs are normalised when getting the fp master in shape master
    * Type: float
    * Minimum: 0
    * Maximum: 100

  FTELLU_ADD_DERIV_PC

    * Description: Define whether to add the first derivative and broadening factor to the principal components this allows a variable resolution and velocity offset of the PCs this is performed in the pixel space and NOT the velocity space as this is should be due to an instrument shift
    * Type: bool

  FTELLU_FIT_DERIV_PC

    * Description: Define whether to fit the derivatives instead of the principal components
    * Type: bool

  FTELLU_FIT_ITERS

    * Description: The number of iterations to use in the reconstructed absorption calculation
    * Type: int

  FTELLU_FIT_KEEP_NUM

    * Description: The number of pixels required (per order) to be able to interpolate the template on to a berv shifted wavelength grid
    * Type: int

  FTELLU_FIT_MIN_TRANS

    * Description: The minimium transmission allowed to define good pixels (for reconstructed absorption calculation)
    * Type: float

  FTELLU_FIT_RECON_LIMIT

    * Description: The minimum log absorption the is allowed in the molecular absorption calculation
    * Type: float

  FTELLU_KERNEL_VSINI

    * Description: The gaussian kernel used to smooth the template and residual spectrum [km/s]
    * Type: float

  FTELLU_LAMBDA_MAX

    * Description: The maximum wavelength constraint (in nm) to calculate reconstructed absorption
    * Type: float

  FTELLU_LAMBDA_MIN

    * Description: The minimum wavelength constraint (in nm) to calculate reconstructed absorption
    * Type: float

  FTELLU_NUM_PRINCIPLE_COMP

    * Description: The number of principle components to use in PCA fit
    * Type: int
    * Minimum: 1

  FTELLU_NUM_TRANS

    * Description: The number of transmission files to use in the PCA fit (use this number of trans files closest in expo_h20 and expo_water
    * Type: int
    * Minimum: 1

  FTELLU_PLOT_ORDER_NUMS

    * Description: Define the orders to plot (not too many) for recon abso plot values should be a string list separated by commas
    * Type: str

  FTELLU_QC_SNR_MIN

    * Description: Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be accepted to the telluDB
    * Type: float
    * Minimum: 0.0

  FTELLU_QC_SNR_ORDER

    * Description: Define the order to use for SNR check when accepting tellu files to the telluDB
    * Type: int
    * Minimum: 0

  FTELLU_SPLOT_ORDER

    * Description: Define the selected fit telluric order for debug plots (when not in loop)
    * Type: int

  FWHM_PIXEL_LSF

    * Description: Define mean line width expressed in pix
    * Type: float

  GL_ALIAS_COL_NAME

    * Description: alias col name in google sheet
    * Type: str

  GL_GAIA_COL_NAME

    * Description: gaia col name in google sheet
    * Type: str

  GL_OBJ_COL_NAME

    * Description: object col name in google sheet
    * Type: str

  GL_RVREF_COL_NAME

    * Description:
    * Type: str

  GL_RV_COL_NAME

    * Description: rv col name in google sheet
    * Type: str

  GL_R_ODO_COL

    * Description: Reject like google columns
    * Type: str

  GL_R_PP_COL

    * Description:
    * Type: str

  GL_R_RV_COL

    * Description:
    * Type: str

  GL_TEFFREF_COL_NAME

    * Description:
    * Type: str

  GL_TEFF_COL_NAME

    * Description: teff col name in google sheet
    * Type: str

  HISTO_BINS

    * Description: The number of bins in dark histogram
    * Type: int
    * Minimum: 1

  HISTO_RANGE_LOW

    * Type: int

  IMAGE_PIXEL_SIZE

    * Description: Define the pixel size in km/s / pix also used for the median sampling size in tellu correction
    * Type: float

  IMAGE_X_BLUE_HIGH

    * Description:
    * Type: int
    * Minimum: 0

  IMAGE_X_BLUE_LOW

    * Description: Defines the resized blue image
    * Type: int
    * Minimum: 0

  IMAGE_X_FULL

    * Description: Define raw image size (mostly just used as a check and in places where we dont have access to this information) in x dim
    * Type: int

  IMAGE_X_HIGH

    * Description:
    * Type: int
    * Minimum: 0

  IMAGE_X_LOW

    * Description: Defines the resized image
    * Type: int
    * Minimum: 0

  IMAGE_X_RED_HIGH

    * Description:
    * Type: int
    * Minimum: 0

  IMAGE_X_RED_LOW

    * Description: Defines the resized red image
    * Type: int
    * Minimum: 0

  IMAGE_Y_BLUE_HIGH

    * Description:
    * Type: int
    * Minimum: 0

  IMAGE_Y_BLUE_LOW

    * Description:
    * Type: int
    * Minimum: 0

  IMAGE_Y_FULL

    * Description: Define raw image size (mostly just used as a check and in places where we dont have access to this information) in y dim
    * Type: int

  IMAGE_Y_HIGH

    * Description:
    * Type: int
    * Minimum: 0

  IMAGE_Y_LOW

    * Description:
    * Type: int
    * Minimum: 0

  IMAGE_Y_RED_HIGH

    * Description:
    * Type: int
    * Minimum: 0

  IMAGE_Y_RED_LOW

    * Description:
    * Type: int
    * Minimum: 0

  INPUT_COMBINE_IMAGES

    * Description: Defines whether to by default combine images that are inputted at the same time
    * Type: bool

  INPUT_FLIP_IMAGE

    * Description: Defines whether to, by default, flip images that are inputted
    * Type: bool

  INPUT_RESIZE_IMAGE

    * Description: Defines whether to, by default, resize images that are inputted
    * Type: bool

  INSTRUMENT

    * Description: Instrument Name
    * Type: str

  IPYTHON_RETURN

    * Description: whether to be in ipython return mode (always exits to ipdb via pdbrc)
    * Type: bool

  IS_MASTER

    * Description: Flag for master recipe associated with this param set
    * Type: bool

  KW_EXPTIME_UNITS

    * Description: This is the units for the exposure time
    * Type: str

  LANGUAGE

    * Description: Language for DRS messages (if translated)
    * Type: str

  LEAKM_ALWAYS_EXTRACT

    * Description: define whether to always extract leak master files (i.e. overwrite existing files)
    * Type: bool

  LEAKM_EXTRACT_TYPE

    * Description: define the type of file to use for leak master solution (currently allowed are E2DSFF) - must match with LEAK_EXTRACT_FILE
    * Type: str

  LEAKM_KERSIZE

    * Description: define the kernel size for leak master
    * Type: float
    * Minimum: 0.0

  LEAKM_WSMOOTH

    * Description: define the e-width of the smoothing kernel for leak master
    * Type: int
    * Minimum: 0

  LEAK_1D_EXTRACT_FILES

    * Description: define the extraction files which are 1D spectra
    * Type: str

  LEAK_2D_EXTRACT_FILES

    * Description: define the extraction files which are 2D images (i.e. order num x nbpix)
    * Type: str

  LEAK_BAD_RATIO_OFFSET

    * Description: define the limit on surpious FP ratio (1 +/- limit)
    * Type: float
    * Minimum: 0.0

  LEAK_BCKGRD_PERCENTILE

    * Description: define the thermal background percentile for the leak and leak master
    * Type: float

  LEAK_EXTRACT_FILE

    * Description: define the type of file to use for the leak correction (currently allowed are E2DS_FILE or E2DSFF_FILE (linked to recipe definition outputs) must match with LEAKM_EXTRACT_TYPE
    * Type: str

  LEAK_LOW_PERCENTILE

    * Type: float
    * Minimum: 0.0
    * Maximum: 100.0

  LEAK_NORM_PERCENTILE

    * Description: define the normalisation percentile for the leak and leak master
    * Type: float

  LEAK_SAVE_UNCORRECTED

    * Description: Define whether to save uncorrected files
    * Type: bool

  LOC_BKGRD_THRESHOLD

    * Description: Normalised amplitude threshold to accept pixels for background calculation
    * Type: float
    * Minimum: 0.0

  LOC_CENTRAL_COLUMN

    * Description: Definition of the central column for use in localisation
    * Type: int
    * Minimum: 0

  LOC_CENT_POLY_DEG

    * Description: Order of polynomial to fit for positions
    * Type: int
    * Minimum: 1

  LOC_COEFFSIG_DEG

    * Description: Defines the fit degree to fit in the coefficient cleaning
    * Type: int
    * Minimum: 1

  LOC_COEFF_SIGCLIP

    * Description: set the sigma clipping cut off value for cleaning coefficients
    * Type: float
    * Minimum: 0

  LOC_COLUMN_SEP_FITTING

    * Description: Define the jump size when finding the order position (jumps in steps of this from the center outwards)
    * Type: int
    * Minimum: 1

  LOC_EXT_WINDOW_SIZE

    * Description: Definition of the extraction window size (half size)
    * Type: int
    * Minimum: 1

  LOC_HALF_ORDER_SPACING

    * Description: Half spacing between orders
    * Type: int
    * Minimum: 0

  LOC_IMAGE_GAP

    * Description: Definition of the gap index in the selected area
    * Type: int
    * Minimum: 0

  LOC_MAX_PTP_CENT

    * Description: Maximum peak-to-peak for sigma-clip order fit (center positions)
    * Type: float
    * Minimum: 0.0

  LOC_MAX_PTP_WID

    * Description: Maximum fractional peak-to-peak for sigma-clip order fit (width)
    * Type: float
    * Minimum: 0.0

  LOC_MAX_RMS_CENT

    * Description: Maximum rms for sigma-clip order fit (center positions)
    * Type: float
    * Minimum: 0.0

  LOC_MAX_RMS_WID

    * Description: Maximum rms for sigma-clip order fit (width)
    * Type: float
    * Minimum: 0.0

  LOC_MINPEAK_AMPLITUDE

    * Description: Minimum amplitude to accept (in e-)
    * Type: float
    * Minimum: 0.0

  LOC_NOISE_MULTIPLIER_THRES

    * Description: Define the noise multiplier threshold in order to accept an order center as usable i.e. max(pixel value) - min(pixel value) > THRES * RDNOISE
    * Type: float
    * Minimum: 0.0

  LOC_ORDERP_BOX_SIZE

    * Description: Size of the order_profile smoothed box (from pixel - size to pixel + size)
    * Type: int

  LOC_ORDER_CURVE_DROP

    * Description: Define the amount we drop from the centre of the order when previous order center is missed (in finding the position)
    * Type: float
    * Minimum: 0.0

  LOC_ORDER_WIDTH_MIN

    * Description: Define minimum width of order to be accepted
    * Type: float
    * Minimum: 0.0

  LOC_PLOT_CORNER_XZOOM1

    * Description: set the zoom in levels for the plots (xmin values)
    * Type: str

  LOC_PLOT_CORNER_XZOOM2

    * Description: set the zoom in levels for the plots (xmax values)
    * Type: str

  LOC_PLOT_CORNER_YZOOM1

    * Description: set the zoom in levels for the plots (ymin values)
    * Type: str

  LOC_PLOT_CORNER_YZOOM2

    * Description: set the zoom in levels for the plots (ymax values)
    * Type: str

  LOC_PTPORMS_CENT

    * Description: Maximum frac ptp/rms for sigma-clip order fit (center positions)
    * Type: float
    * Minimum: 0.0

  LOC_SAT_THRES

    * Description: Saturation threshold for localisation
    * Type: float
    * Minimum: 0.0

  LOC_SAVE_SUPERIMP_FILE

    * Description: Option for archiving the location image
    * Type: bool

  LOC_START_ROW_OFFSET

    * Description: row number of image to start localisation processing at
    * Type: int
    * Minimum: 0

  LOC_WIDTH_POLY_DEG

    * Description: Order of polynomial to fit for widths
    * Type: int
    * Minimum: 1

  MKTELLU_BLAZE_PERCENTILE

    * Description: value below which the blaze in considered too low to be useful for all blaze profiles, we normalize to the 95th percentile. Thats pretty much the peak value, but it is resistent to eventual outliers
    * Type: float

  MKTELLU_CUT_BLAZE_NORM

    * Description:
    * Type: float

  MKTELLU_DEFAULT_CONV_WIDTH

    * Description: define the default convolution width [in pixels]
    * Type: int

  MKTELLU_PLOT_ORDER_NUMS

    * Description: Define the orders to plot (not too many) values should be a string list separated by commas
    * Type: str

  MKTELLU_QC_AIRMASS_DIFF

    * Description: Define the allowed difference between recovered and input airmass
    * Type: float

  MKTELLU_QC_SNR_MIN

    * Description: Define the minimum SNR for order "QC_TELLU_SNR_ORDER" that will be accepted to the telluDB
    * Type: float
    * Minimum: 0.0

  MKTELLU_QC_SNR_ORDER

    * Description: Define the order to use for SNR check when accepting tellu files to the telluDB
    * Type: int
    * Minimum: 0

  MKTELLU_TAU_WATER_ULIMIT

    * Description: Set an upper limit for the allowed line-of-sight optical depth of water
    * Type: float

  MKTELLU_TEMP_MED_FILT

    * Description: median-filter the template. we know that stellar features are very broad. this avoids having spurious noise in our templates [pixel]
    * Type: int

  MKTELLU_THRES_TRANSFIT

    * Description: minimum transmission required for use of a given pixel in the TAPAS and SED fitting
    * Type: float

  MKTELLU_TRANS_FIT_UPPER_BAD

    * Description: Defines the bad pixels if the spectrum is larger than this value. These values are likely an OH line or a cosmic ray
    * Type: float

  MKTELLU_TRANS_MAX_WATERCOL

    * Description: Defines the maximum allowed value for the recovered water vapor optical depth
    * Type: float

  MKTELLU_TRANS_MIN_WATERCOL

    * Description: Defines the minimum allowed value for the recovered water vapor optical depth (should not be able 1)
    * Type: float

  MKTEMPLATE_BERVCOR_QCMIN

    * Description: Define the minimum allowed berv coverage to construct a template in km/s (default is double the resolution in km/s)
    * Type: float
    * Minimum: 0.0

  MKTEMPLATE_BERVCOV_CSNR

    * Description: Define the core SNR in order to calculate required BERV coverage
    * Type: float
    * Minimum: 0.0

  MKTEMPLATE_BERVCOV_RES

    * Description: Defome the resolution in km/s for calculating BERV coverage
    * Type: float
    * Minimum: 0.0

  MKTEMPLATE_E2DS_ITNUM

    * Description: The number of iterations to filter low frequency noise before medianing the template "big cube" to the final template spectrum
    * Type: int
    * Minimum: 1

  MKTEMPLATE_E2DS_LOWF_SIZE

    * Description: The size (in pixels) to filter low frequency noise before medianing the template "big cube" to the final template spectrum
    * Type: int
    * Minimum: 1

  MKTEMPLATE_FIBER_TYPE

    * Description: the fiber required for input template files
    * Type: str

  MKTEMPLATE_FILESOURCE

    * Description: the order to use for signal to noise cut requirement
    * Type: str

  MKTEMPLATE_FILETYPE

    * Description: the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for input template files
    * Type: str

  MKTEMPLATE_S1D_ITNUM

    * Description: The number of iterations to filter low frequency noise before medianing the s1d template "big cube" to the final template spectrum
    * Type: int
    * Minimum: 1

  MKTEMPLATE_S1D_LOWF_SIZE

    * Description: The size (in pixels) to filter low frequency noise before medianing the s1d template "big cube" to the final template spectrum
    * Type: int
    * Minimum: 1

  MKTEMPLATE_SNR_ORDER

    * Description: the order to use for signal to noise cut requirement
    * Type: int
    * Minimum: 0

  OBJ_LIST_CROSS_MATCH_RADIUS

    * Description: Define the radius for crossmatching objects (in both lookup table and query) in arcseconds
    * Type: float
    * Minimum: 0.0

  OBJ_LIST_GAIA_EPOCH

    * Description: Define the gaia epoch to use in the gaia query
    * Type: float
    * Minimum: 2000.0
    * Maximum: 2100.0

  OBJ_LIST_GAIA_MAG_CUT

    * Description: Define the gaia magnitude cut to use in the gaia query
    * Type: float
    * Minimum: 10.0
    * Maximum: 25.0

  OBJ_LIST_GAIA_PLX_LIM

    * Description: Define the gaia parallax limit for using gaia point
    * Type: float
    * Minimum: 0.0

  OBJ_LIST_GAIA_URL

    * Description: Define the TAP Gaia URL (for use in crossmatching to Gaia via astroquery)
    * Type: str

  OBJ_LIST_GOOGLE_SHEET_URL

    * Description: Define the google sheet to use for crossmatch
    * Type: str

  OBJ_LIST_GOOGLE_SHEET_WNUM

    * Description: Define the google sheet workbook number
    * Type: int
    * Minimum: 0

  OBJ_LIST_RESOLVE_FROM_COORDS

    * Description: Define whether to get Gaia ID from header RA and Dec (basically if all other option fails) - WARNING - this is a crossmatch so may lead to a bad identification of the gaia id - not recommended
    * Type: bool

  OBJ_LIST_RESOLVE_FROM_DATABASE

    * Description: Define whether to resolve from local database (via drs_database / drs_db)
    * Type: bool

  OBJ_LIST_RESOLVE_FROM_GAIAID

    * Description: Define whether to resolve from gaia id (via TapPlus to Gaia) if False ra/dec/pmra/pmde/plx will always come from header
    * Type: bool

  OBJ_LIST_RESOLVE_FROM_GLIST

    * Description: Define whether to get Gaia ID / Teff / RV from google sheets if False will try to resolve if gaia ID given otherwise will use ra/dec if OBJ_LIST_RESOLVE_FROM_COORDS = True else will default to header values
    * Type: bool

  OBS_LAT

    * Type: float

  OBS_LONG

    * Description: Defines the longitude West is negative
    * Type: float

  ODOCODE_REJECT_GSHEET_ID

    * Description: Define the odometer code rejection google sheet id
    * Type: str

  ODOCODE_REJECT_GSHEET_NUM

    * Description: Define the odmeter code rejection google sheet workbook
    * Type: str
    * Minimum: 0

  PLOT_BADPIX_MAP

    * Description: turn on badpix map debug plot
    * Type: bool

  PLOT_CCF_PHOTON_UNCERT

    * Description: turn on the ccf photon uncertainty debug plot
    * Type: bool

  PLOT_CCF_RV_FIT

    * Description: turn on the ccf rv fit debug plot (for the mean order value)
    * Type: bool

  PLOT_CCF_RV_FIT_LOOP

    * Description: turn on the ccf rv fit debug plot (in a loop around orders)
    * Type: bool

  PLOT_CCF_SWAVE_REF

    * Description: turn on the ccf spectral order vs wavelength debug plot
    * Type: bool

  PLOT_DARK_HISTOGRAM

    * Description: turn on dark histogram debug plot
    * Type: bool

  PLOT_DARK_IMAGE_REGIONS

    * Description: turn on dark image region debug plot
    * Type: bool

  PLOT_EXTRACT_S1D

    * Description: turn on the extraction 1d spectrum debug plot
    * Type: bool

  PLOT_EXTRACT_S1D_WEIGHT

    * Description: turn on the extraction 1d spectrum weight (before/after) debug plot
    * Type: bool

  PLOT_EXTRACT_SPECTRAL_ORDER1

    * Description: turn on the extraction spectral order debug plot (loop)
    * Type: bool

  PLOT_EXTRACT_SPECTRAL_ORDER2

    * Description: turn on the extraction spectral order debug plot (selected order)
    * Type: bool

  PLOT_FLAT_BLAZE_ORDER1

    * Description: turn on the flat blaze order debug plot (loop)
    * Type: bool

  PLOT_FLAT_BLAZE_ORDER2

    * Description: turn on the flat blaze order debug plot (selected order)
    * Type: bool

  PLOT_FLAT_ORDER_FIT_EDGES1

    * Description: turn on the flat order fit edges debug plot (loop)
    * Type: bool

  PLOT_FLAT_ORDER_FIT_EDGES2

    * Description: turn on the flat order fit edges debug plot (selected order)
    * Type: bool

  PLOT_FTELLU_PCA_COMP1

    * Description: turn on the fit tellu pca component debug plot (in loop)
    * Type: bool

  PLOT_FTELLU_PCA_COMP2

    * Description: turn on the fit tellu pca component debug plot (single order)
    * Type: bool

  PLOT_FTELLU_RECON_ABSO1

    * Description: turn on the fit tellu reconstructed absorption debug plot (in loop)
    * Type: bool

  PLOT_FTELLU_RECON_ABSO12

    * Description: turn on the fit tellu reconstructed absorption debug plot (single order)
    * Type: bool

  PLOT_FTELLU_RECON_SPLINE1

    * Description: turn on the fit tellu reconstructed spline debug plot (in loop)
    * Type: bool

  PLOT_FTELLU_RECON_SPLINE2

    * Description: turn on the fit tellu reconstructed spline debug plot (single order)
    * Type: bool

  PLOT_FTELLU_WAVE_SHIFT1

    * Description: turn on the fit tellu wave shift debug plot (in loop)
    * Type: bool

  PLOT_FTELLU_WAVE_SHIFT2

    * Description: turn on the fit tellu wave shift debug plot (single order)
    * Type: bool

  PLOT_LOC_CHECK_COEFFS

    * Description: turn on the localisation check coeffs debug plot
    * Type: bool

  PLOT_LOC_FINDING_ORDERS

    * Description: turn on the localisation finding orders debug plot
    * Type: bool

  PLOT_LOC_FIT_RESIDUALS

    * Description: turn on the localisation fit residuals plot (warning: done many times)
    * Type: bool

  PLOT_LOC_IM_SAT_THRES

    * Description: turn on the image above saturation threshold debug plot
    * Type: bool

  PLOT_LOC_MINMAX_CENTS

    * Description: turn on the localisation cent min max debug plot
    * Type: bool

  PLOT_LOC_MIN_CENTS_THRES

    * Description: turn on the localisation cent/thres debug plot
    * Type: bool

  PLOT_LOC_ORD_VS_RMS

    * Description: turn on the order number vs rms debug plot
    * Type: bool

  PLOT_MKTELLU_WAVE_FLUX1

    * Description: turn on the make tellu wave flux debug plot (in loop)
    * Type: bool

  PLOT_MKTELLU_WAVE_FLUX2

    * Description: turn on the make tellu wave flux debug plot (single order)
    * Type: bool

  PLOT_MKTEMP_BERV_COV

    * Description: turn on the berv coverage debug plot
    * Type: bool

  PLOT_POLAR_CONTINUUM

    * Description: turn on the polar continuum debug plot
    * Type: bool

  PLOT_POLAR_LSD

    * Description: turn on the polar lsd debug plot
    * Type: bool

  PLOT_POLAR_RESULTS

    * Description: turn on the polar results debug plot
    * Type: bool

  PLOT_POLAR_STOKES_I

    * Description: turn on the polar stokes i debug plot
    * Type: bool

  PLOT_SHAPEL_ZOOM_SHIFT

    * Description: turn on the shape local zoom plot
    * Type: bool

  PLOT_SHAPE_ANGLE_OFFSET

    * Description: turn on the shape angle offset (one selected order) debug plot
    * Type: bool

  PLOT_SHAPE_ANGLE_OFFSET_ALL

    * Description: turn on the shape angle offset (all orders in loop) debug plot
    * Type: bool

  PLOT_SHAPE_DX

    * Description: turn on the shape dx debug plot
    * Type: bool

  PLOT_SHAPE_LINEAR_TPARAMS

    * Description: turn on the shape linear transform params plot
    * Type: bool

  PLOT_TELLUP_ABSO_SPEC

    * Description: turn on the telluric pre-cleaning result debug plot
    * Type: bool

  PLOT_TELLUP_WAVE_TRANS

    * Description: turn on the telluric pre-cleaning ccf debug plot
    * Type: bool

  PLOT_THERMAL_BACKGROUND

    * Description: turn on thermal background (in extract) debug plot
    * Type: bool

  PLOT_WAVENIGHT_HISTPLOT

    * Description: turn on the wave per night hist debug plot
    * Type: bool

  PLOT_WAVENIGHT_ITERPLOT

    * Description: turn on the wave per night iteration debug plot
    * Type: bool

  PLOT_WAVEREF_EXPECTED

    * Description: turn on the wave lines hc/fp expected vs measured debug plot(will plot once for hc once for fp)
    * Type: bool

  PLOT_WAVE_FIBER_COMPARISON

    * Description: turn on the wave line fiber comparison plot
    * Type: bool

  PLOT_WAVE_FP_FINAL_ORDER

    * Description: turn on the wave solution final fp order debug plot
    * Type: bool

  PLOT_WAVE_FP_IPT_CWID_1MHC

    * Description: turn on the wave solution fp interp cavity width 1/m_d hc debug plot
    * Type: bool

  PLOT_WAVE_FP_IPT_CWID_LLHC

    * Description: turn on the wave solution fp interp cavity width ll hc and fp debug plot
    * Type: bool

  PLOT_WAVE_FP_LL_DIFF

    * Description: turn on the wave solution old vs new wavelength difference debug plot
    * Type: bool

  PLOT_WAVE_FP_LWID_OFFSET

    * Description: turn on the wave solution fp local width offset debug plot
    * Type: bool

  PLOT_WAVE_FP_MULTI_ORDER

    * Description: turn on the wave solution fp multi order debug plot
    * Type: bool

  PLOT_WAVE_FP_M_X_RES

    * Description: turn on the wave solution fp fp_m_x residual debug plot
    * Type: bool

  PLOT_WAVE_FP_SINGLE_ORDER

    * Description: turn on the wave solution fp single order debug plot
    * Type: bool

  PLOT_WAVE_FP_WAVE_RES

    * Description: turn on the wave solution fp wave residual debug plot
    * Type: bool

  PLOT_WAVE_HC_BRIGHTEST_LINES

    * Description: turn on the wave solution hc brightest lines debug plot
    * Type: bool

  PLOT_WAVE_HC_GUESS

    * Description: turn on the wave solution hc guess debug plot (in loop)
    * Type: bool

  PLOT_WAVE_HC_RESMAP

    * Description: turn on the wave solution hc resolution map debug plot
    * Type: bool

  PLOT_WAVE_HC_TFIT_GRID

    * Description: turn on the wave solution hc triplet fit grid debug plot
    * Type: bool

  PLOT_WAVE_LITTROW_CHECK1

    * Description: turn on the wave solution littrow check debug plot
    * Type: bool

  PLOT_WAVE_LITTROW_CHECK2

    * Description: turn on the wave solution littrow check debug plot
    * Type: bool

  PLOT_WAVE_LITTROW_EXTRAP1

    * Description: turn on the wave solution littrow extrapolation debug plot
    * Type: bool

  PLOT_WAVE_LITTROW_EXTRAP2

    * Description: turn on the wave solution littrow extrapolation debug plot
    * Type: bool

  POLAR_CONT_TELLMASK_LOWER

    * Description: Define the telluric mask for calculation of continnum lower limits (string list)
    * Type: float

  POLAR_CONT_TELLMASK_UPPER

    * Description: Define the telluric mask for calculation of continnum upper limits (string list)
    * Type: float

  POLAR_LSD_ANALYSIS

    * Description: Perform LSD analysis
    * Type: str

  POLAR_LSD_FILE_KEY

    * Description: Define the file regular expression key to lsd mask files
    * Type: str

  POLAR_LSD_MIN_LINEDEPTH

    * Description: Define minimum line depth to be used in the LSD analyis
    * Type: float

  POLAR_LSD_NBIN1

    * Description: Define the normalise by continuum lsd binsize used in the normalization with POLAR_LSD_NORM = True
    * Type: int
    * Minimum: 1

  POLAR_LSD_NBIN2

    * Description: Define the normalise by continuum lsd binsize used in the profile calculation
    * Type: int
    * Minimum: 1

  POLAR_LSD_NLFIT1

    * Description: Define whether to use a linear fit in the normalise by continuum lsd calc used in the normalization with POLAR_LSD_NORM = True
    * Type: bool

  POLAR_LSD_NLFIT2

    * Description: Define whether to use a linear fit in the normalise by continuum lsd calc used in the profile calculation
    * Type: bool

  POLAR_LSD_NORM

    * Description: Define whether to normalise by stokei by the continuum in lsd process
    * Type: bool

  POLAR_LSD_NOVERLAP1

    * Description: Define the normalise by continuum lsd overlap with adjacent bins used in the normalization with POLAR_LSD_NORM = True
    * Type: int
    * Minimum: 0

  POLAR_LSD_NOVERLAP2

    * Description: Define the normalise by continuum lsd overlap with adjacent bins used in the profile calculation
    * Type: int
    * Minimum: 0

  POLAR_LSD_NPOINTS

    * Description: Define number of points for output LSD profile
    * Type: int

  POLAR_LSD_NSIGCLIP1

    * Description: Define the normalise by continuum lsd sigma clip value used in the profile calculation
    * Type: float
    * Minimum: 0

  POLAR_LSD_NSIGCLIP2

    * Description: Define the normalise by continuum lsd sigma clip value used in the profile calculation
    * Type: float
    * Minimum: 0

  POLAR_LSD_NWINDOW1

    * Type: str

  POLAR_LSD_NWINDOW2

    * Type: str

  POLAR_LSD_ORDER_MASK

    * Description: Define the order wavelength mask filename
    * Type: str

  POLAR_LSD_PATH

    * Description: Define the spectral lsd mask directory for lsd polar calculations
    * Type: str

  POLAR_LSD_VFINAL

    * Description: Define final velocity (km/s) for output LSD profile
    * Type: float

  POLAR_LSD_VINIT

    * Description: Define initial velocity (km/s) for output LSD profile
    * Type: float

  POLAR_LSD_WL_LOWER

    * Description: Define mask for selecting lines to be used in the LSD analysis lower bounds (string list)
    * Type: str

  POLAR_LSD_WL_UPPER

    * Description: Define mask for selecting lines to be used in the LSD analysis upper bounds (string list)
    * Type: str

  POLAR_METHOD

    * Description: Define the polarimetry calculation method
    * Type: str

  POLAR_VALID_FIBERS

    * Description: Define all possible fibers used for polarimetry (define as a string list)
    * Type: str

  POLAR_VALID_STOKES

    * Description: Define all possible stokes parameters used for polarimetry (define as a string list)
    * Type: str

  POST_CLEAR_REDUCED

    * Description: Define whether (by deafult) to clear reduced directory
    * Type: bool

  POST_OVERWRITE

    * Description: Define whether (by default) to overwrite post processed files
    * Type: bool

  PPM_MASK_NSIG

    * Description: Define allowed preprocess master mask number of sigma
    * Type: float

  PP_BAD_EXPTIME_FRACTION

    * Description: Define the fraction of the required exposure time that is required for a valid observation
    * Type: float
    * Minimum: 0

  PP_CORRUPT_HOT_THRES

    * Description: Defines the threshold in sigma that selects hot pixels
    * Type: int
    * Minimum: 0

  PP_CORRUPT_MED_SIZE

    * Description: Defines the size around badpixels that is considered part of the bad pixel
    * Type: int
    * Minimum: 1

  PP_CORRUPT_RMS_THRES

    * Description: Defines the RMS threshold to also catch corrupt files
    * Type: float
    * Minimum: 0.0

  PP_CORRUPT_SNR_HOTPIX

    * Description: Defines the snr hotpix threshold to define a corrupt file
    * Type: float
    * Minimum: 0.0

  PP_DARK_MED_BINNUM

    * Description: Define the number of bins used in the dark median process - [cal_pp]
    * Type: int
    * Minimum: 0

  PP_HOTPIX_BOXSIZE

    * Description: Defines the box size surrounding hot pixels to use
    * Type: int
    * Minimum: 1

  PP_HOTPIX_FILE

    * Description: Defines the pp hot pixel file (located in the data folder)
    * Type: str

  PP_LOWEST_RMS_PERCENTILE

    * Description: Define the lowest rms value of the rms percentile allowed if the value of the pp_rms_percentile-th is lower than this this value is used
    * Type: float
    * Minimum: 0.0

  PP_MEDAMP_BINSIZE

    * Description: Define the bin to use to correct low level frequences. This value cannot be smaller than the order footprint on the array as it would lead to a set of NaNs in the downsized image
    * Type: int

  PP_NUM_DARK_AMP

    * Description: Define the number of dark amplifiers
    * Type: int
    * Minimum: 0

  PP_NUM_REF_BOTTOM

    * Description: Define the number of un-illuminated reference pixels at bottom of image
    * Type: int

  PP_NUM_REF_TOP

    * Description: Define the number of un-illuminated reference pixels at top of image
    * Type: int

  PP_OBJ_DPRTYPES

    * Description: Define object dpr types
    * Type: str

  PP_RMS_PERCENTILE

    * Description: Define the percentile value for the rms normalisation (0-100)
    * Type: int
    * Minimum: 0
    * Maximum: 100

  PP_TOTAL_AMP_NUM

    * Description: Define the total number of amplifiers
    * Type: int
    * Minimum: 0

  QC_DARK_TIME

    * Description: Min dark exposure time
    * Type: float
    * Minimum: 0.0

  QC_EXT_FLUX_MAX

    * Description: Saturation level reached warning
    * Type: float

  QC_FF_MAX_RMS

    * Description: Maximum allowed RMS of flat field
    * Type: float

  QC_LOC_MAXFIT_REMOVED_CTR

    * Description: Maximum points removed in location fit
    * Type: int
    * Minimum: 0

  QC_LOC_MAXFIT_REMOVED_WID

    * Description: Maximum points removed in width fit
    * Type: int
    * Minimum: 0

  QC_LOC_RMSMAX_CTR

    * Description: Maximum rms allowed in fitting location
    * Type: float
    * Minimum: 0.0

  QC_LOC_RMSMAX_WID

    * Description: Maximum rms allowed in fitting width
    * Type: float
    * Minimum: 0.0

  QC_MAX_DARK

    * Description: Max fraction of dark pixels (percent)
    * Type: float

  QC_MAX_DARKLEVEL

    * Description: Max dark median level [ADU/s]
    * Type: float

  QC_MAX_DEAD

    * Description: Max fraction of dead pixels
    * Type: float

  RAW_TO_PP_ROTATION

    * Description: Define the rotation of the pp files in relation to the raw files, nrot = 0 -> same as input, nrot = 1 -> 90deg counter-clock-wise, nrot = 2 -> 180deg, nrot = 3 -> 90deg clock-wise,  nrot = 4 -> flip top-bottom, nrot = 5 -> flip top-bottom and rotate 90 deg counter-clock-wisenrot = 6 -> flip top-bottom and rotate 180 deg, nrot = 7 -> flip top-bottom and rotate 90 deg clock-wise, nrot >=8 -> performs a modulo 8 anyway
    * Type: int

  REMAKE_DATABASE_DEFAULT

    * Description: define the default database to remake
    * Type: str

  REPROCESS_ABSFILECOL

    * Description: Define the absolute file column name for raw file table
    * Type: str

  REPROCESS_MODIFIEDCOL

    * Description: Define the modified file column name for raw file table
    * Type: str

  REPROCESS_NIGHTCOL

    * Description: Define the night name column name for raw file table
    * Type: str

  REPROCESS_PINAMECOL

    * Description: Define the pi name column name for raw file table
    * Type: str

  REPROCESS_RAWINDEXFILE

    * Description: Define the raw index filename
    * Type: str

  REPROCESS_RUN_KEY

    * Description: Key for use in run files
    * Type: str

  REPROCESS_SEQCOL

    * Description: define the sequence (1 of 5, 2 of 5 etc) col for raw file table
    * Type: str

  REPROCESS_SORTCOL_HDRKEY

    * Description: Define the sort column (from header keywords) for raw file table
    * Type: str

  REPROCESS_TIMECOL

    * Description: define the time col for raw file table
    * Type: str

  ROOT_DRS_LOC

    * Description: root for localisation header keys
    * Type: str

  SHAPEL_PLOT_ZOOM1

    * Description: Define first zoom plot for shape local zoom debug plot should be a string list (xmin, xmax, ymin, ymax)
    * Type: str

  SHAPEL_PLOT_ZOOM2

    * Description: Define second zoom plot for shape local zoom debug plot should be a string list (xmin, xmax, ymin, ymax)
    * Type: str

  SHAPEOFFSET_ABSDEV_THRESHOLD

    * Description: very low thresholding values tend to clip valid points
    * Type: float

  SHAPEOFFSET_BOTTOM_PERCENTILE

    * Description: defines the bottom percentile for fp peak
    * Type: float

  SHAPEOFFSET_DEVIANT_PMAX

    * Description:
    * Type: float
    * Minimum: 0
    * Maximum: 100

  SHAPEOFFSET_DEVIANT_PMIN

    * Description: Define the most deviant peaks - percentile from [min to max]
    * Type: float
    * Minimum: 0
    * Maximum: 100

  SHAPEOFFSET_DRIFT_MARGIN

    * Description: Define the maximum allowed offset (in nm) that we allow for the detector)
    * Type: float

  SHAPEOFFSET_FIT_HC_SIGMA

    * Description: The number of sigmas that the HC spectrum is allowed to be away from the predicted (from FP) position
    * Type: float

  SHAPEOFFSET_FPINDEX_MAX

    * Description: Maximum number of FP (larger than expected number (~10000 to ~25000)
    * Type: int
    * Minimum: 10000
    * Maximum: 25000

  SHAPEOFFSET_FPMAX_NUM_ERROR

    * Description: Define the maximum error in FP order assignment we assume that the error in FP order assignment could range from -50 to +50 in practice, it is -1, 0 or +1 for the cases weve tested to date
    * Type: int

  SHAPEOFFSET_MASK_BORDER

    * Description: Define the border in pixels at the edge of the detector
    * Type: int

  SHAPEOFFSET_MASK_EXTWIDTH

    * Description: Define the width of the FP to extract (+/- the center)
    * Type: int

  SHAPEOFFSET_MASK_PIXWIDTH

    * Description: Define the width of the FP mask (+/- the center)
    * Type: int

  SHAPEOFFSET_MAXDEV_THRESHOLD

    * Description: Define the maximum allowed maximum absolute deviation away from the error fit
    * Type: float

  SHAPEOFFSET_MED_FILTER_WIDTH

    * Description: define the median filter to apply to the hc (high pass filter)]
    * Type: int

  SHAPEOFFSET_MIN_MAXPEAK_FRAC

    * Description: Define the minimum maxpeak value as a fraction of the maximum maxpeak
    * Type: float

  SHAPEOFFSET_TOP_FLOOR_FRAC

    * Description: defines the floor below which top values should be set to this fraction away from the max top value
    * Type: float

  SHAPEOFFSET_TOP_PERCENTILE

    * Description: defines the top percentile for fp peak
    * Type: float

  SHAPEOFFSET_VALID_FP_LENGTH

    * Description: Define the valid length of a FP peak
    * Type: int

  SHAPEOFFSET_WAVEFP_INV_IT

    * Description: Define the number of iterations to do for the wave_fp inversion trick
    * Type: int

  SHAPEOFFSET_XOFFSET

    * Description: defines the shape offset xoffset (before and after) fp peaks
    * Type: int

  SHAPE_DEBUG_OUTPUTS

    * Description: Define whether to output debug (sanity check) files
    * Type: bool

  SHAPE_FP_MASTER_MIN_IN_GROUP

    * Description: Define the minimum number of FP files in a group to mean group is valid
    * Type: int
    * Minimum: 1

  SHAPE_LARGE_ANGLE_MAX

    * Description: the range of angles (in degrees) for the first iteration (large) and subsequent iterations (small)
    * Type: float

  SHAPE_LARGE_ANGLE_MIN

    * Description: the range of angles (in degrees) for the first iteration (large) and subsequent iterations (small)
    * Type: float

  SHAPE_MASTER_FIBER

    * Description: Define the shape master dx rmsquality control criteria (per order)
    * Type: float

  SHAPE_MASTER_FP_INI_BOXSIZE

    * Description: Define the initial search box size (in pixels) around the fp peaks
    * Type: int
    * Minimum: 1

  SHAPE_MASTER_FP_SMALL_BOXSIZE

    * Description: Define the small search box size (in pixels) around the fp peaks
    * Type: int
    * Minimum: 1

  SHAPE_MASTER_LINTRANS_NITER

    * Description: Define the number of iterations used to get the linear transform params
    * Type: int
    * Minimum: 1

  SHAPE_MASTER_VALIDFP_PERCENTILE

    * Description: Define the percentile which defines a true FP peak [0-100]
    * Type: float
    * Minimum: 0
    * Maximum: 100

  SHAPE_MASTER_VALIDFP_THRESHOLD

    * Description: Define the fractional flux an FP much have compared to its neighbours
    * Type: float
    * Minimum: 0

  SHAPE_MEDIAN_FILTER_SIZE

    * Description: the size of the median filter to apply along the order (in pixels)
    * Type: int
    * Minimum: 0

  SHAPE_MIN_GOOD_CORRELATION

    * Description: The minimum value for the cross-correlation to be deemed good
    * Type: float
    * Minimum: 0.0

  SHAPE_NSECTIONS

    * Description: number of sections per order to split the order into
    * Type: int
    * Minimum: 1

  SHAPE_NUM_ITERATIONS

    * Description: The number of iterations to run the shape finding out to
    * Type: int
    * Minimum: 1

  SHAPE_ORDER_WIDTH

    * Description: width of the ABC fibers (in pixels)
    * Type: int
    * Minimum: 1

  SHAPE_PLOT_SELECTED_ORDER

    * Description: The order to use on the shape plot
    * Type: int
    * Minimum: 0

  SHAPE_QC_DXMAP_STD

    * Description: Defines the largest allowed standard deviation for a given per-order and per-x-pixel shift of the FP peaks
    * Type: int

  SHAPE_QC_LTRANS_RES_THRES

    * Description: Define the largest standard deviation allowed for the shift in x or y when doing the shape master fp linear transform
    * Type: float

  SHAPE_SHORT_DX_MEDFILT_WID

    * Type: int

  SHAPE_SIGMACLIP_MAX

    * Description: max sigma clip (in sigma) on points within a section
    * Type: float
    * Minimum: 0.0

  SHAPE_SMALL_ANGLE_MAX

    * Description: the range of angles (in degrees) for the first iteration (large) and subsequent iterations (small)
    * Type: float

  SHAPE_SMALL_ANGLE_MIN

    * Description: the range of angles (in degrees) for the first iteration (large) and subsequent iterations (small)
    * Type: float

  SHAPE_UNIQUE_FIBERS

    * Description: define the names of the unique fibers (i.e. not AB) for use in getting the localisation coefficients for dymap
    * Type: str

  SKIP_DONE_PP

    * Description: Define whether to skip preprocessed files that have already be processed
    * Type: bool

  SUMMARY_LATEX_PDF

    * Description: Define whether we try to create a latex summary pdf (turn this off if you have any problems with latex/pdflatex)
    * Type: bool

  TAPAS_FILE

    * Description: Define the name of the tapas file to use
    * Type: str

  TAPAS_FILE_FMT

    * Description: Define the format (astropy format) of the tapas file "TAPAS_FILE"
    * Type: str

  TELLUP_ABSO_EXPO_KEXP

    * Description: define the gaussian exponent of the kernel used in abso_expo a value of 2 is gaussian, a value >2 is boxy
    * Type: float
    * Minimum: 0.0

  TELLUP_ABSO_EXPO_KTHRES

    * Description: define the kernel threshold in abso_expo
    * Type: float
    * Minimum: 0.0

  TELLUP_ABSO_EXPO_KWID

    * Description: define the gaussian width of the kernel used in abso_expo
    * Type: float
    * Minimum: 0.0

  TELLUP_CCF_SCAN_RANGE

    * Description: width in km/s for the ccf scan to determine the abso in pre-cleaning
    * Type: float
    * Minimum: 0.0

  TELLUP_CLEAN_OH_LINES

    * Description: define whether to clean OH lines
    * Type: bool

  TELLUP_DEXPO_CONV_THRES

    * Description: define dexpo convergence threshold
    * Type: float
    * Minimum: 0.0

  TELLUP_DEXPO_MAX_ITR

    * Description: define the maximum number of iterations to try to get dexpo convergence
    * Type: int
    * Minimum: 1

  TELLUP_DO_PRECLEANING

    * Description: define whether we do pre-cleaning
    * Type: bool

  TELLUP_D_WATER_ABSO

    * Description: set the typical water abso exponent. Compare to values in header for high-snr targets later
    * Type: float
    * Minimum: 0.0

  TELLUP_FORCE_AIRMASS

    * Description: define whether to force airmass fit to header airmass value
    * Type: bool

  TELLUP_H2O_CCF_FILE

    * Description: define the telluric trans water abso CCF file
    * Type: str

  TELLUP_OHLINE_PCA_FILE

    * Description: define the OH line pca file
    * Type: str

  TELLUP_OTHERS_CCF_FILE

    * Description: define the telluric trans other abso CCF file
    * Type: str

  TELLUP_OTHER_BOUNDS

    * Description: set the lower and upper bounds (String list) for the exponent of the other species of absorbers
    * Type: str

  TELLUP_REMOVE_ORDS

    * Description: define the orders not to use in pre-cleaning fit (due to theraml background)
    * Type: str

  TELLUP_SNR_MIN_THRES

    * Description: define the minimum snr to accept orders for pre-cleaning fit
    * Type: float
    * Minimum: 0.0

  TELLUP_TRANS_SIGLIM

    * Description: define the threshold for discrepant transmission (in sigma)
    * Type: float
    * Minimum: 0.0

  TELLUP_TRANS_THRES

    * Description: define the transmission threshold (in exponential form) for keeping valid transmission
    * Type: float

  TELLUP_WATER_BOUNDS

    * Description: set the lower and upper bounds (string list) for the exponent of water absorber
    * Type: str

  TELLURIC_FIBER_TYPE

    * Description: the fiber required for input template files
    * Type: str

  TELLURIC_FILETYPE

    * Description: the OUTPUT type (KW_OUTPUT header key) and DrsFitsFile name required for input template files
    * Type: str

  TELLU_ABSORBERS

    * Description: Define list of absorbers in the tapas fits table
    * Type: str

  TELLU_ALLOWED_DPRTYPES

    * Description: The allowed input DPRTYPES for input telluric files
    * Type: str

  TELLU_BLACKLIST_NAME

    * Description: Define telluric black list name
    * Type: str

  TELLU_CUT_BLAZE_NORM

    * Description: Define level above which the blaze is high enough to accurately measure telluric
    * Type: float

  TELLU_DB_MATCH

    * Description: Define the match type for telluDB files match = older when more than one file for each key will select the newest file that is OLDER than time in fitsfilename match = closest when more than on efile for each key will select the file that is closest to time in fitsfilename if two files match with keys and time the key lower in the calibDB file will be used
    * Type: str

  TELLU_LIST_DIRECTORY

    * Description: Define telluric black/white list directory
    * Type: str

  TELLU_WHITELIST_NAME

    * Description: Define telluric white list name
    * Type: str

  THERMAL_ALWAYS_EXTRACT

    * Description: define whether to always extract thermals (i.e. overwrite existing files)
    * Type: bool

  THERMAL_BLUE_LIMIT

    * Description: define thermal blue limit (in nm)
    * Type: float

  THERMAL_CORRECT

    * Description: whether to apply the thermal correction to extractions
    * Type: bool

  THERMAL_CORRETION_TYPE1

    * Description: define DPRTYPEs we need to correct thermal background using telluric absorption (TAPAS)
    * Type: str

  THERMAL_CORRETION_TYPE2

    * Description: define DPRTYPEs we need to correct thermal background using method 2
    * Type: str

  THERMAL_ENVELOPE_PERCENTILE

    * Description: define the percentile to measure the background for correction type 2
    * Type: float
    * Minimum: 0
    * Maximum: 100

  THERMAL_EXTRACT_TYPE

    * Description: define the type of file to use for wave solution (currently allowed are "E2DS" or "E2DSFF")
    * Type: str

  THERMAL_FILTER_WID

    * Description: width of the median filter used for the background
    * Type: int

  THERMAL_ORDER

    * Description: define the order to perform the thermal background scaling on
    * Type: int

  THERMAL_PLOT_START_ORDER

    * Description: define the order to plot on the thermal debug plot
    * Type: int

  THERMAL_RED_LIMIT

    * Description: define thermal red limit (in nm)
    * Type: float

  THERMAL_THRES_TAPAS

    * Description: maximum tapas transmission to be considered completely opaque for the purpose of background determination in last order.
    * Type: float

  USE_SKYDARK_CORRECTION

    * Description: Define whether to use SKYDARK for dark corrections
    * Type: bool

  USE_SKYDARK_ONLY

    * Description: If use_skydark_correction is True define whether we use the SKYDARK only or use SKYDARK/DARK (whichever is closest)
    * Type: bool

  WAVENIGHT_PLT_BINL

    * Description: wave night plot hc bin lower bound in multiples of rms
    * Type: float
    * Minimum: 0

  WAVENIGHT_PLT_BINU

    * Description: wave night plot hc bin upper bound in multiples of rms
    * Type: float
    * Minimum: 0

  WAVENIGHT_PLT_NBINS

    * Description: wave night plot hist number of bins
    * Type: int
    * Minimum: 0

  WAVEREF_EDGE_WMAX

    * Description: minimum distance to the edge of the array to consider a line
    * Type: int
    * Minimum: 0

  WAVEREF_FITDEG

    * Description: get the degree to fix master wavelength to in hc mode
    * Type: int
    * Minimum: 1

  WAVEREF_FP_NHIGH

    * Description: define the highest N for fp peaks
    * Type: int
    * Minimum: 1

  WAVEREF_FP_NLOW

    * Description: define the lowest N for fp peaks
    * Type: int
    * Minimum: 0

  WAVEREF_FP_POLYINV

    * Description: define the number of iterations required to do the Fp polynomial inversion
    * Type: int
    * Minimum: 1

  WAVEREF_HC_BOXSIZE

    * Description: value in pixel (+/-) for the box size around each HC line to perform fit
    * Type: int
    * Minimum: 0

  WAVEREF_HC_FIBTYPES

    * Type: str

  WAVEREF_NSIG_MIN

    * Description: min SNR to consider the line
    * Type: int
    * Minimum: 0

  WAVE_ALWAYS_EXTRACT

    * Description: define whether to always extract HC/FP files in the wave code (even if they
    * Type: bool

  WAVE_CCF_DETNOISE

    * Description: The detector noise to use for the FP CCF
    * Type: float
    * Minimum: 0.0

  WAVE_CCF_MASK

    * Description: The filename of the CCF Mask to use for the FP CCF
    * Type: str

  WAVE_CCF_MASK_FMT

    * Description: Define the CCF mask format (must be an astropy.table format)
    * Type: str

  WAVE_CCF_MASK_MIN_WEIGHT

    * Description: Define the weight of the CCF mask (if 1 force all weights equal)
    * Type: float

  WAVE_CCF_MASK_NORMALIZATION

    * Description: Define the default CCF MASK normalisation mode for FP CCF options are: None for no normalization all for normalization across all ordersorder for normalization for each order
    * Type: str

  WAVE_CCF_MASK_PATH

    * Description: Define the ccf mask path the FP CCF
    * Type: str

  WAVE_CCF_MASK_UNITS

    * Description: Define the wavelength units for the mask for the FP CCF
    * Type: str

  WAVE_CCF_MASK_WIDTH

    * Description: Define the width of the template line (if 0 use natural)
    * Type: float

  WAVE_CCF_NOISE_BOXSIZE

    * Description: The size around a saturated pixel to flag as unusable for wave dv rms calculation
    * Type: int
    * Minimum: 0.0

  WAVE_CCF_NOISE_SIGDET

    * Description: The value of the noise for wave dv rms calculation snr = flux/sqrt(flux + noise^2)
    * Type: float
    * Minimum: 0.0

  WAVE_CCF_NOISE_THRES

    * Description: The maximum flux for a good (unsaturated) pixel for wave dv rms calculation
    * Type: float
    * Minimum: 0.0

  WAVE_CCF_N_ORD_MAX

    * Description: Define the number of orders (from zero to ccf_num_orders_max) to use to calculate the FP CCF
    * Type: int
    * Minimum: 1

  WAVE_CCF_RV_THRES_QC

    * Description: define the quality control threshold from RV of CCF FP between master fiber and other fibers, above this limit fails QC [m/s]
    * Type: float
    * Minimum: 0

  WAVE_CCF_SMART_MASK_MAXLAM

    * Description: define the maximum wavelength for the smart mask [nm]
    * Type: float
    * Minimum: 0

  WAVE_CCF_SMART_MASK_MINLAM

    * Description: define the minimum wavelength for the smart mask [nm]
    * Type: float
    * Minimum: 0

  WAVE_CCF_SMART_MASK_TRIAL_NMAX

    * Description: define the converges parameter for dwave in smart mask generation
    * Type: float
    * Minimum: 0

  WAVE_CCF_SMART_MASK_TRIAL_NMIN

    * Description: define a trial minimum FP N value (should be lower than true minimum FP N value)
    * Type: int
    * Minimum: 0

  WAVE_CCF_SMART_MASK_WIDTH

    * Description: define the width of the lines in the smart mask [km/s]
    * Type: float
    * Minimum: 0

  WAVE_CCF_STEP

    * Description: The CCF step size to use for the FP CCF
    * Type: float
    * Minimum: 0.0

  WAVE_CCF_TARGET_RV

    * Description: The target RV (CCF center) to use for the FP CCF
    * Type: float
    * Minimum: 0.0

  WAVE_CCF_UPDATE_MASK

    * Description: Define whether to regenerate the fp mask (WAVE_CCF_MASK) when we update the cavity width in the master wave solution recipe
    * Type: bool

  WAVE_CCF_WIDTH

    * Description: The CCF width size to use for the FP CCF
    * Type: float
    * Minimum: 0.0

  WAVE_EXTRACT_TYPE

    * Description: define the type of file to use for wave solution (currently allowed are "E2DS" or "E2DSFF"
    * Type: str

  WAVE_FIBER_COMP_PLOT_ORD

    * Description: define the wave fiber comparison plot order number
    * Type: int
    * Minimum: 0

  WAVE_FIT_DEGREE

    * Description: define the fit degree for the wavelength solution
    * Type: int

  WAVE_FP_BLAZE_THRES

    * Description: Minimum blaze threshold to keep FP peaks
    * Type: float
    * Minimum: 0.0

  WAVE_FP_CAVFIT_DEG

    * Description: Define the polynomial fit degree between FP line numbers and the measured cavity width for each line
    * Type: int
    * Minimum: 0

  WAVE_FP_CAVFIT_MODE

    * Description: Select the FP cavity fitting (WAVE_MODE_FP = 1 only) Should be one of the following: 0 - derive using the 1/m vs d fit from HC lines 1 - derive using the ll vs d fit from HC lines
    * Type: int

  WAVE_FP_DOPD0

    * Description: Define the initial value of FP effective cavity width 2xd in nm
    * Type: float
    * Minimum: 0.0

  WAVE_FP_DPRLIST

    * Description: define the dprtype for generating FPLINES (string list)
    * Type: str

  WAVE_FP_DV_MAX

    * Description: Maximum DV to keep HC lines in combined (WAVE_NEW) solution
    * Type: float
    * Minimum: 0.0

  WAVE_FP_ERRX_MIN

    * Description: Define the minimum instrumental error
    * Type: float
    * Minimum: 0.0

  WAVE_FP_LARGE_JUMP

    * Description: Define the FP jump size that is too large
    * Type: float
    * Minimum: 0

  WAVE_FP_LLDIF_MAX

    * Description: Maximum FP peaks wavelength separation fraction diff. from median
    * Type: float
    * Minimum: 0.0

  WAVE_FP_LLDIF_MIN

    * Description: Minimum FP peaks wavelength separation fraction diff. from median
    * Type: float
    * Minimum: 0.0

  WAVE_FP_LLFIT_MODE

    * Description: Select the FP wavelength fitting (WAVE_MODE_FP = 1 only) Should be one of the following: 0 - use fit_1d_solution function 1 - fit with sigma-clipping and mod 1 pixel correction
    * Type: int

  WAVE_FP_LL_DEGR_FIT

    * Description: Define the wavelength fit polynomial order
    * Type: int
    * Minimum: 0

  WAVE_FP_LL_OFFSET

    * Description: Maximum fract. wavelength offset between cross-matched FP peaks
    * Type: float
    * Minimum: 0.0

  WAVE_FP_MAX_LLFIT_RMS

    * Description: Define the max rms for the wavelength sigma-clip fit
    * Type: float
    * Minimum: 0

  WAVE_FP_NORM_PERCENTILE

    * Description: define the percentile to normalize the spectrum to (per order) used to determine FP peaks (peaks must be above a normalised limit defined in WAVE_FP_PEAK_LIM
    * Type: float
    * Minimum: 0.0

  WAVE_FP_P2P_WIDTH_CUT

    * Description: Define peak to peak width that is too large (removed from FP peaks)
    * Type: float
    * Minimum: 0.0

  WAVE_FP_PEAK_LIM

    * Description: define the normalised limit below which FP peaks are not used
    * Type: float
    * Minimum: 0.0

  WAVE_FP_PLOT_MULTI_INIT

    * Description: First order for multi-order wave fp plot
    * Type: int
    * Minimum: 0

  WAVE_FP_PLOT_MULTI_NBO

    * Description: Number of orders in multi-order wave fp plot
    * Type: int
    * Minimum: 1

  WAVE_FP_SIGCLIP

    * Description: Sigma-clip value for sigclip_polyfit
    * Type: float
    * Minimum: 0.0

  WAVE_FP_UPDATE_CAVITY

    * Description: Decide whether to refit the cavity width (will update if files do not exist)
    * Type: bool

  WAVE_FP_WEIGHT_THRES

    * Description: Define the weight threshold (small number) below which we do not keep fp lines
    * Type: float
    * Minimum: 0.0

  WAVE_FP_XDIF_MAX

    * Description: Maximum FP peaks pixel separation fraction diff. from median
    * Type: float
    * Minimum: 0.0

  WAVE_FP_XDIF_MIN

    * Description: Minimum FP peaks pixel separation fraction diff. from median
    * Type: float
    * Minimum: 0.0

  WAVE_HC_FITBOX_EWMAX

    * Description:
    * Type: float
    * Minimum: 0.0

  WAVE_HC_FITBOX_EWMIN

    * Description: the e-width of the line expressed in pixels.
    * Type: float
    * Minimum: 0.0

  WAVE_HC_FITBOX_GFIT_DEG

    * Description: the fit degree for the wave hc gaussian peaks fit
    * Type: int

  WAVE_HC_FITBOX_RMS_DEVMAX

    * Description:
    * Type: float
    * Minimum: 0.0

  WAVE_HC_FITBOX_RMS_DEVMIN

    * Description: the RMS of line-fitted line must be between DEVMIN and DEVMAX of the peak value must be SNR>5 (or 1/SNR<0.2)
    * Type: float
    * Minimum: 0.0

  WAVE_HC_FITBOX_SIGMA

    * Description: number of sigma above local RMS for a line to be flagged as such
    * Type: float

  WAVE_HC_FITBOX_SIZE

    * Description: width of the box for fitting HC lines. Lines will be fitted from -W to +W, so a 2*W+1 window
    * Type: int

  WAVE_HC_MAX_DV_CAT_GUESS

    * Description: Maximum distance between catalog line and init guess line to accept line in m/s
    * Type: int
    * Minimum: 0.0

  WAVE_HC_NITER_FIT_TRIPLET

    * Description: Number of times to run the fit triplet algorithm
    * Type: int
    * Minimum: 1

  WAVE_HC_NMAX_BRIGHT

    * Description: number of bright lines kept per order avoid >25 as it takes super long avoid <12 as some orders are ill-defined and we need >10 valid lines anyway 20 is a good number, and we see no reason to change it
    * Type: int
    * Minimum: 10
    * Maximum: 30

  WAVE_HC_QC_SIGMA_MAX

    * Description: quality control criteria if sigma greater than this many sigma fails
    * Type: float
    * Minimum: 0.0

  WAVE_HC_RESMAP_DV_SPAN

    * Description: Defines the dv span for PLOT_WAVE_HC_RESMAP debug plot, should be a string list containing a min and max dv value
    * Type: str

  WAVE_HC_RESMAP_SIZE

    * Description: Define the resolution and line profile map size (y-axis by x-axis)
    * Type: str

  WAVE_HC_RESMAP_XLIM

    * Description: Defines the x limits for PLOT_WAVE_HC_RESMAP debug plot, should be a string list containing a min and max x value
    * Type: str

  WAVE_HC_RESMAP_YLIM

    * Description: Defines the y limits for PLOT_WAVE_HC_RESMAP debug plot, should be a string list containing a min and max y value
    * Type: str

  WAVE_HC_RES_MAXDEV_THRES

    * Description: Define the maximum allowed deviation in the RMS line spread function
    * Type: float

  WAVE_HC_TFIT_CUT_THRES

    * Description: Cut threshold for the triplet line fit [in km/s]
    * Type: float
    * Minimum: 0.0

  WAVE_HC_TFIT_DEG

    * Description: The fit degree between triplets
    * Type: int
    * Minimum: 0

  WAVE_HC_TFIT_DVCUT_ALL

    * Description:
    * Type: float
    * Minimum: 0.0

  WAVE_HC_TFIT_DVCUT_ORDER

    * Description: Define the distance in m/s away from the center of dv hist points outside will be rejected [m/s]
    * Type: float
    * Minimum: 0.0

  WAVE_HC_TFIT_MINNUM_LINES

    * Description: Minimum number of lines required per order
    * Type: int
    * Minimum: 0

  WAVE_HC_TFIT_MINTOT_LINES

    * Description: Minimum total number of lines required
    * Type: int
    * Minimum: 0

  WAVE_HC_TFIT_ORDER_FIT_CONT

    * Description: this sets the order of the polynomial used to ensure continuity in the xpix vs wave solutions by setting the first term = 12, we force that the zeroth element of the xpix of the wavelegnth grid is fitted with a 12th order polynomial as a function of order number (format = string list separated by commas
    * Type: str

  WAVE_HC_TFIT_SIGCLIP_NUM

    * Description: Number of times to loop through the sigma clip for triplet fit
    * Type: int
    * Minimum: 1

  WAVE_HC_TFIT_SIGCLIP_THRES

    * Description: Sigma clip threshold for triplet fit
    * Type: float
    * Minimum: 0.0

  WAVE_LINELIST_AMPCOL

    * Description:
    * Type: str

  WAVE_LINELIST_COLS

    * Description: Define the line list file column names (must be separated by commas and must be equal to the number of columns in file)
    * Type: str

  WAVE_LINELIST_FILE

    * Description: Define the line list file (located in the DRS_WAVE_DATA directory)
    * Type: str

  WAVE_LINELIST_FMT

    * Type: str

  WAVE_LINELIST_START

    * Description: Define the line list file row the data starts
    * Type: int

  WAVE_LINELIST_WAVECOL

    * Description: Define the line list file wavelength column and amplitude column Must be in WAVE_LINELIST_COLS
    * Type: str

  WAVE_LITTROW_CUT_STEP_1

    * Description: Define the littrow cut steps for the HC wave solution
    * Type: int

  WAVE_LITTROW_CUT_STEP_2

    * Description: Define the littrow cut steps for the FP wave solution
    * Type: int

  WAVE_LITTROW_EXT_ORDER_FIT_DEG

    * Description: Define the order fit for the Littrow solution (fit along the orders) TODO needs to be the same as ic_ll_degr_fit
    * Type: int

  WAVE_LITTROW_FIG_DEG_1

    * Description: Define the fit polynomial order for the Littrow fit (fit across the orders) for the HC wave solution
    * Type: int

  WAVE_LITTROW_FIG_DEG_2

    * Description: Define the fit polynomial order for the Littrow fit (fit across the orders) for the FP wave solution
    * Type: int

  WAVE_LITTROW_ORDER_FINAL_1

    * Description: Define the order to end the Littrow fit at for the HC wave solution
    * Type: int

  WAVE_LITTROW_ORDER_FINAL_2

    * Description: Define the order to end the Littrow fit at for the FP wave solution
    * Type: int

  WAVE_LITTROW_ORDER_INIT_1

    * Description: Define the order to start the Littrow fit from for the HC wave solution
    * Type: int

  WAVE_LITTROW_ORDER_INIT_2

    * Description: Define the order to start the Littrow fit from for the FP wave solution
    * Type: int

  WAVE_LITTROW_QC_DEV_MAX

    * Description: Maximum littrow Deviation from wave solution (at x cut points)
    * Type: float

  WAVE_LITTROW_QC_RMS_MAX

    * Description: Maximum littrow RMS value
    * Type: float

  WAVE_LITTROW_REMOVE_ORDERS

    * Description: Define orders to ignore in Littrow fit (should be a string list separated by commas
    * Type: str

  WAVE_MASTER_FIBER

    * Description: Define wave master fiber (controller fiber)
    * Type: str

  WAVE_MODE_FP

    * Description: Define the mode to calculate the fp wave solution
    * Type: int

  WAVE_MODE_HC

    * Description: Define the mode to calculate the hc wave solution
    * Type: int

  WAVE_NIGHT_DCAVITY

    * Description: starting point for the cavity corrections
    * Type: float
    * Minimum: 0.0

  WAVE_NIGHT_HC_SIGCLIP

    * Description: define the sigma clip value to remove bad hc lines
    * Type: float
    * Minimum: 0.0

  WAVE_NIGHT_MED_ABS_DEV

    * Description: median absolute deviation cut off
    * Type: float
    * Minimum: 0.0

  WAVE_NIGHT_NITERATIONS1

    * Description: number of iterations for hc convergence
    * Type: int
    * Minimum: 1

  WAVE_NIGHT_NITERATIONS2

    * Description: number of iterations for fp convergence
    * Type: int
    * Minimum: 1

  WAVE_NIGHT_NSIG_FIT_CUT

    * Description: sigma clipping for the fit
    * Type: float
    * Minimum: 1

  WAVE_N_ORD_FINAL

    * Description: Defines order to which the solution is calculated
    * Type: int

  WAVE_N_ORD_START

    * Description: Defines order from which the solution is calculated
    * Type: int

  WAVE_PIXEL_SHIFT_INTER

    * Description: Define intercept and slope for a pixel shift
    * Type: float

  WAVE_PIXEL_SHIFT_SLOPE

    * Description:
    * Type: float

  WAVE_T_ORDER_START

    * Description: Defines echelle of first extracted order
    * Type: int

Keywords (Autogen)
======================

.. glossary::



  KW_ACQTIME

    * Description: define the HEADER key for acquisition time Note must set the date format in KW_ACQTIME_FMT

  KW_AIRMASS

    * Description: define the airmass HEADER key
    * Type: float

  KW_BBAD

    * Description: fraction of bad pixels with all criteria
    * Type: float

  KW_BBFLAT

    * Description: fraction of bad pixels from flat
    * Type: float

  KW_BERV

    * Description: the BERV calculated with KW_BERVSOURCE
    * Type: float

  KW_BERVALT

    * Description: the observatory altitude used to calculate the BERV
    * Type: float

  KW_BERVDEC

    * Description: the Declination used to calculate the BERV
    * Type: float

  KW_BERVEPOCH

    * Description: the epoch (jd) used to calculate the BERV
    * Type: float

  KW_BERVGAIA_ID

    * Description: the Gaia ID used to identify KW_BERV_POS_SOURCE for BERV calculation
    * Type: str

  KW_BERVLAT

    * Description: the observatory latitude used to calculate the BERV
    * Type: float

  KW_BERVLONG

    * Description: the observatory longitude used to calculate the BERV
    * Type: float

  KW_BERVMAX

    * Description: the maximum BERV found across 1 year (with KW_BERVSOURCE)
    * Type: float

  KW_BERVMAX_EST

    * Description: the maximum BERV found across 1 year (calculated with estimate)
    * Type: float

  KW_BERVOBJNAME

    * Description: the OBJNAME used to identify KW_BERV_POS_SOURCE for BERV calculation
    * Type: str

  KW_BERVPLX

    * Description: the parallax [mas] used to calculate the BERV
    * Type: float

  KW_BERVPMDE

    * Description: the pmde [mas/yr] used to calculate the BERV
    * Type: float

  KW_BERVPMRA

    * Description: the pmra [mas/yr] used to calculate the BERV
    * Type: float

  KW_BERVRA

    * Description: the Right Ascension used to calculate the BERV
    * Type: float

  KW_BERVRV

    * Description: the rv [km/s] used to calculate the BERV
    * Type: float

  KW_BERVSOURCE

    * Description: the source of the calculated BERV parameters
    * Type: str

  KW_BERV_EST

    * Description: the BERV calculated with the estimate
    * Type: float

  KW_BERV_GAIA_BPMAG

    * Description: the Gaia BP mag (if present) for the gaia query
    * Type: float

  KW_BERV_GAIA_GMAG

    * Description: the Gaia G mag (if present) for the gaia query
    * Type: float

  KW_BERV_GAIA_MAGLIM

    * Description: the Gaia G mag limit used for the gaia query
    * Type: float

  KW_BERV_GAIA_PLXLIM

    * Description: the Gaia parallax limit used the gaia query
    * Type: float

  KW_BERV_GAIA_RPMAG

    * Description: the Gaia RP mag (if present) for the gaia query
    * Type: float

  KW_BERV_OBSTIME

    * Description: the actual jd time used to calculate the BERV
    * Type: float

  KW_BERV_OBSTIME_METHOD

    * Description: the method used to obtain the berv obs time
    * Type: str

  KW_BERV_POS_SOURCE

    * Description: the source of the BERV star parameters (header or gaia)
    * Type: str

  KW_BHOT

    * Description: fraction of hot pixels
    * Type: float

  KW_BJD

    * Description: the Barycenter Julian date calculate with KW_BERVSOURCE
    * Type: float

  KW_BJD_EST

    * Description: the Barycenter Julian date calculated with the estimate
    * Type: float

  KW_BLAZE_BPRCNTL

    * Description: The blaze sinc bad percentile value used
    * Type: float

  KW_BLAZE_CUT

    * Description: the blaze cut used
    * Type: float

  KW_BLAZE_DEG

    * Description: the blaze degree used (to fit)
    * Type: int

  KW_BLAZE_NITER

    * Description: The number of iterations used in the blaze sinc fit
    * Type: int

  KW_BLAZE_SCUT

    * Description: The blaze sinc cut threshold used
    * Type: float

  KW_BLAZE_SIGFIG

    * Description: The blaze sinc sigma clip (rejection threshold) used
    * Type: float

  KW_BLAZE_WID

    * Description: the blaze with used
    * Type: float

  KW_BNDARK

    * Description: fraction of non-finite pixels in dark
    * Type: float

  KW_BNFLAT

    * Description: fraction of non-finite pixels in flat
    * Type: float

  KW_BNILUM

    * Description: fraction of un-illuminated pixels (from engineering flat)
    * Type: float

  KW_BTOT

    * Description: fraction of total bad pixels
    * Type: float

  KW_CALIBWH

    * Description: define the calibration wheel position
    * Type: str

  KW_CASS_TEMP

    * Description: define the cassegrain temperature HEADER key
    * Type: float

  KW_CCAS

    * Description: define the science fiber type HEADER key
    * Type: str

  KW_CCF_BOXSIZE

    * Description: the size in pixels around saturated pixels to regard as bad pixels used in the ccf photon noise calculation
    * Type: int

  KW_CCF_DVRMS_CC

    * Description: the dev rms calculated during the CCF [m/s]
    * Type: float

  KW_CCF_DVRMS_SP

    * Description: the dv rms calculated for spectrum [m/s]
    * Type: float

  KW_CCF_MASK

    * Description: the ccf mask file used
    * Type: str

  KW_CCF_MASK_MIN

    * Description: the minimum weight of a line in the CCF MASK used
    * Type: float

  KW_CCF_MASK_UNITS

    * Description: the wavelength units used in the CCF Mask for line centers
    * Type: str

  KW_CCF_MASK_WID

    * Description: the mask width of lines in the CCF Mask used
    * Type: float

  KW_CCF_MAXFLUX

    * Description: the upper limit for good pixels (above this are bad) used in the ccf photon noise calculation
    * Type: float

  KW_CCF_MEAN_CONSTRAST

    * Description: the mean constrast (depth of fit ccf) from the mean ccf
    * Type: float

  KW_CCF_MEAN_FWHM

    * Description: the mean fwhm from the mean ccf
    * Type: float

  KW_CCF_MEAN_RV

    * Description: The mean rv calculated from the mean ccf
    * Type: float

  KW_CCF_NMAX

    * Description: The last order used in the mean CCF (from 0 to nmax are used)
    * Type: int

  KW_CCF_RV_CORR

    * Description: the corrected radial velocity of the object (taking into account the FP RVs)
    * Type: float

  KW_CCF_RV_DRIFT

    * Description: The radial velocity drift between wave sol FP and simultaneous FP (if present) if simulataneous FP not present this is just the wave solution FP CCF value
    * Type: float

  KW_CCF_RV_OBJ

    * Description: The radial velocity measured from the object CCF against the CCF MASK
    * Type: float

  KW_CCF_RV_SIMU_FP

    * Description: The radial velocity measured from a simultaneous FP CCF (FP in reference channel)
    * Type: float

  KW_CCF_RV_TIMEDIFF

    * Description: the time diff (in days) between wave file and file (fiber specific)
    * Type: str

  KW_CCF_RV_WAVEFILE

    * Description: the wave file used for the rv (fiber specific)
    * Type: str

  KW_CCF_RV_WAVESRCE

    * Description: the wave file source used for the rv reference fiber
    * Type: str

  KW_CCF_RV_WAVETIME

    * Description: the wave file time used for the rv [mjd] (fiber specific)
    * Type: str

  KW_CCF_RV_WAVE_FP

    * Description: The radial velocity measured from the wave solution FP CCF
    * Type: float

  KW_CCF_SIGDET

    * Description: the read noise used in the photon noise uncertainty calculation in the ccf
    * Type: float

  KW_CCF_STEP

    * Description: the ccf step used (in km/s)
    * Type: float

  KW_CCF_TARGET_RV

    * Description: the central rv used (in km/s) rv elements run from rv +/- width in the ccf
    * Type: float

  KW_CCF_TOT_LINES

    * Description: the total number of mask lines used in all ccfs
    * Type: int

  KW_CCF_WIDTH

    * Description: the width of the ccf used (in km/s)
    * Type: float

  KW_CDBBACK

    * Description: background calibration file used
    * Type: str

  KW_CDBBAD

    * Description: bad pixel calibration file used
    * Type: str

  KW_CDBBLAZE

    * Description: blaze calibration file used
    * Type: str

  KW_CDBDARK

    * Description: dark calibration file used
    * Type: str

  KW_CDBFLAT

    * Description: flat calibration file used
    * Type: str

  KW_CDBLOCO

    * Description: localisation calibration file used
    * Type: str

  KW_CDBORDP

    * Description: order profile calibration file used
    * Type: str

  KW_CDBSHAPEDX

    * Description: shape dx calibration file used
    * Type: str

  KW_CDBSHAPEDY

    * Description: shape dy calibration file used
    * Type: str

  KW_CDBSHAPEL

    * Description: shape local calibration file used
    * Type: str

  KW_CDBTHERMAL

    * Description: thermal calibration file used
    * Type: str

  KW_CDBWAVE

    * Description: wave solution calibration file used
    * Type: str

  KW_CDEN

    * Description: define the density HEADER key
    * Type: str

  KW_CMMTSEQ

    * Description: define polarisation HEADER key
    * Type: str

  KW_CMPLTEXP

    * Description: define the exposure number within sequence HEADER key
    * Type: int

  KW_COSMIC

    * Description: whether cosmics where rejected
    * Type: int

  KW_COSMIC_CUT

    * Description: the cosmic cut criteria
    * Type: float

  KW_COSMIC_THRES

    * Description: the cosmic threshold used
    * Type: float

  KW_CREF

    * Description: define the reference fiber type HEADER key
    * Type: str

  KW_C_CVRTE

    * Description: whether the calibratoins have been converted to electrons
    * Type: str

  KW_C_FLIP

    * Description: whether the calibrations have been flipped
    * Type: str

  KW_C_FTYPE

    * Description: whether the calibrations have an ftype
    * Type: str

  KW_C_RESIZE

    * Description: whether the calibrations have been resized
    * Type: str

  KW_DARK_B_DEAD

    * Description: The fraction of dead pixels in the blue part of the dark (in %)
    * Type: float

  KW_DARK_B_MED

    * Description: The median dark level in the blue part of the dark in ADU/s
    * Type: float

  KW_DARK_CUT

    * Description: The threshold of the dark level to retain in ADU
    * Type: float

  KW_DARK_DEAD

    * Description: The fraction of dead pixels in the dark (in %)
    * Type: float

  KW_DARK_MED

    * Description: The median dark level in ADU/s
    * Type: float

  KW_DARK_R_DEAD

    * Description: The fraction of dead pixels in the red part of the dark (in %)
    * Type: float

  KW_DARK_R_MED

    * Description: The median dark level in the red part of the dark in ADU/s
    * Type: float

  KW_DATE_OBS

    * Description: define the observation date HEADER key
    * Type: float

  KW_DBERV

    * Description: the derivative of the BERV (BERV at time + 1s - BERV)
    * Type: float

  KW_DBERV_EST

    * Description: the derivative of the BERV (BERV at time + 1s - BERV) calculated with estimate
    * Type: float

  KW_DPRTYPE

    * Description: Define the key to get the data fits file type
    * Type: str

  KW_DRS_BPMAG

    * Description: the Gaia BP magnitude to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_BPMAG_S

    * Description: the source of the bpmag used by the drs (after preprocessing)
    * Type: str

  KW_DRS_DATE

    * Description: DRS version date keyword
    * Type: str

  KW_DRS_DATE_NOW

    * Description: Processed date keyword
    * Type: str

  KW_DRS_DEC

    * Description: the declination to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_DEC_S

    * Description: the source of the dec to be used by the drs (after preprocessing)
    * Type: str

  KW_DRS_EPOCH

    * Description: the epoch to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_EPOCH_S

    * Description: the source of the epoch used by the drs (after preprocessing)
    * Type: str

  KW_DRS_GAIAID

    * Description: the gaia id to be used by the drs (after preprocessing)
    * Type: str

  KW_DRS_GAIAID_S

    * Description: the source of the gaia id to be used by the drs (after preprocessing)
    * Type: str

  KW_DRS_GMAG

    * Description: the Gaia G magnitude to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_GMAG_S

    * Description: the source of the gmag used by the drs (after preprocessing)
    * Type: str

  KW_DRS_OBJNAME

    * Description: the object name to be used by the drs (after preprocessing)
    * Type: str

  KW_DRS_OBJNAME_S

    * Description: the source of the object name used by the drs
    * Type: str

  KW_DRS_PLX

    * Description: the parallax to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_PLX_S

    * Description: the source of the parallax used by the drs (after preprocessing)
    * Type: str

  KW_DRS_PMDE

    * Description: the proper motion in dec to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_PMDE_S

    * Description: the source of the pmde used by the drs (after preprocessing)
    * Type: str

  KW_DRS_PMRA

    * Description: the proper motion in ra to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_PMRA_S

    * Description: the source of the pmra used by the drs (afer prepreocessing)
    * Type: str

  KW_DRS_QC

    * Description: the drs qc
    * Type: str

  KW_DRS_QC_LOGIC

    * Description: the logic of the quality control parameter
    * Type: str

  KW_DRS_QC_NAME

    * Description: the name of the quality control parameter
    * Type: str

  KW_DRS_QC_PASS

    * Description: whether this quality control parameter passed
    * Type: str

  KW_DRS_QC_VAL

    * Description: the value of the qc
    * Type: str

  KW_DRS_RA

    * Description: the right ascension to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_RA_S

    * Description: the source of the ra to be used by the drs (after preprocessing)
    * Type: str

  KW_DRS_RPMAG

    * Description: the Gaia RP magnitude to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_RPMAG_S

    * Description: the source of the rpmag used by the drs (after preprocessing)
    * Type: str

  KW_DRS_RV

    * Description: the radial velocity to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_RV_S

    * Description: the source of the radial velocity used by the drs (after preprocessing)
    * Type: str

  KW_DRS_TEFF

    * Description: the effective temperature to be used by the drs (after preprocessing)
    * Type: float

  KW_DRS_TEFF_S

    * Description: the source of teff used by the drs (after preprocessing)
    * Type: str

  KW_EXPREQ

    * Description: define the required exposure time HEADER key (used to get value only)
    * Type: float

  KW_EXPTIME

    * Description: define the exposure time HEADER key (used to get value only)
    * Type: float

  KW_EXT_END

    * Description: the end order for extraction
    * Type: int

  KW_EXT_RANGE1

    * Description: the upper bound for extraction of order
    * Type: int

  KW_EXT_RANGE2

    * Description: the lower bound for extraction of order
    * Type: int

  KW_EXT_SNR

    * Description: SNR calculated in extraction process (per order)
    * Type: float

  KW_EXT_START

    * Description: the start order for extraction
    * Type: int

  KW_EXT_TYPE

    * Description: The extraction type (only added for E2DS files in extraction)
    * Type: str

  KW_FIBER

    * Description: the fiber name
    * Type: str

  KW_FRMTIME

    * Description: define the frame time HEADER key
    * Type: float

  KW_FTELLU_ABSO_PREFIX

    * Description: The prefix for molecular
    * Type: float

  KW_FTELLU_ABSO_SRC

    * Description: The source of the loaded absorption (npy file or trans_file from database)
    * Type: str

  KW_FTELLU_ADD_DPC

    * Description: whether we added first derivative to principal components
    * Type: bool

  KW_FTELLU_AMP_PC

    * Description: Telluric principle component amplitudes (for use with 1D list)
    * Type: float

  KW_FTELLU_DVTELL1

    * Description: Telluric principle component first derivative
    * Type: float

  KW_FTELLU_DVTELL2

    * Description: Telluric principle component second derivative
    * Type: float

  KW_FTELLU_FIT_DPC

    * Description: whether we fitted the derivatives of the principal components
    * Type: bool

  KW_FTELLU_FIT_ITERS

    * Description: the number of iterations used to fit
    * Type: int

  KW_FTELLU_FIT_KEEP_NUM

    * Description: Number of good pixels requirement used
    * Type: int

  KW_FTELLU_FIT_MIN_TRANS

    * Description: The minimum transmission used
    * Type: float

  KW_FTELLU_IM_PX_SIZE

    * Description: The image pixel size used
    * Type: float

  KW_FTELLU_KERN_VSINI

    * Description: The smoothing kernel size [km/s] used
    * Type: float

  KW_FTELLU_LAMBDA_MAX

    * Description: The maximum wavelength used
    * Type: float

  KW_FTELLU_LAMBDA_MIN

    * Description: The minimum wavelength used
    * Type: float

  KW_FTELLU_NPC

    * Description: The number of principle components used
    * Type: int

  KW_FTELLU_NTRANS

    * Description: The number of trans files used in pc fit (closest in expo h20/others)
    * Type: int

  KW_FTELLU_RECON_LIM

    * Description: the log limit in minimum absorption used
    * Type: float

  KW_FTELLU_TAU_H2O

    * Description: Tau Water depth calculated in fit tellu
    * Type: float

  KW_FTELLU_TAU_REST

    * Description: Tau Rest depth calculated in fit tellu
    * Type: float

  KW_FTELLU_TEMPHASH

    * Description: the hash for the template generation (unique)
    * Type: str

  KW_FTELLU_TEMPLATE

    * Description: the template that was used (or None if not used)
    * Type: str

  KW_FTELLU_TEMPNUM

    * Description: the number of template files used
    * Type: int

  KW_FTELLU_TEMPTIME

    * Description: the hash for the template generation (unique)
    * Type: str

  KW_GAIA_ID

    * Description: define the gaia id
    * Type: str

  KW_GAIN

    * Description: define the gain HEADER key (used to get value only)
    * Type: float

  KW_HUMIDITY

    * Description: define the humidity HEADER key
    * Type: float

  KW_IDENTIFIER

    * Description: Define the header key that uniquely identifies the file (i.e. an odometer code)

  KW_INFILE1

    * Description: input files
    * Type: str

  KW_INFILE2

    * Description: input files
    * Type: str

  KW_INFILE3

    * Description: input files
    * Type: str

  KW_INIT_WAVE

    * Description: the initial wave file used for wave solution
    * Type: str

  KW_INPUTRV

    * Description: define the rv HEADER key
    * Type: float

  KW_LEAK_BADR_U

    * Description: Define the bad ratio offset limit used for correcting leakage
    * Type: float

  KW_LEAK_BP_U

    * Description: Define the background percentile used for correcting leakage
    * Type: float

  KW_LEAK_CORR

    * Description: Define whether leak correction has been done
    * Type: int

  KW_LEAK_KERSIZE

    * Description: Define the kernel size used for correcting leakage master
    * Type: float

  KW_LEAK_LP_U

    * Description: Define the lower bound percentile used for correcting leakage
    * Type: float

  KW_LEAK_NP_U

    * Description: Define the normalisation percentile used for correcting leakage
    * Type: float

  KW_LEAK_UP_U

    * Description: Define the upper bound percentile used for correcting leakage
    * Type: float

  KW_LEAK_WSMOOTH

    * Description: Define the e-width smoothing used for correcting leakage master
    * Type: float

  KW_LOC_BCKGRD

    * Description: Mean background (as percentage)
    * Type: float

  KW_LOC_CTR_COEFF

    * Description: Coeff center order
    * Type: int

  KW_LOC_DEG_C

    * Description: fit degree for order centers
    * Type: int

  KW_LOC_DEG_W

    * Description: fit degree for order widths
    * Type: int

  KW_LOC_MAXFLX

    * Description: Maximum flux in order
    * Type: float

  KW_LOC_NBO

    * Description: Number of orders located
    * Type: int

  KW_LOC_RMS_CTR

    * Description: Maximum rms allowed for location fit
    * Type: float

  KW_LOC_RMS_WID

    * Description: Maximum rms allowed for width fit (formally KW_LOC_rms_fwhm)
    * Type: float

  KW_LOC_SMAXPTS_CTR

    * Description: Maximum number of removed points allowed for location fit
    * Type: int

  KW_LOC_SMAXPTS_WID

    * Description: Maximum number of removed points allowed for width fit
    * Type: int

  KW_LOC_WID_COEFF

    * Description: Coeff width order
    * Type: int

  KW_MID_OBSTIME_METHOD

    * Description: Define the method by which the MJD was calculated
    * Type: str

  KW_MID_OBS_TIME

    * Description: Define the mid exposure time

  KW_MJDEND

    * Description: define the MJ end date HEADER key

  KW_MKTELL_AIRMASS

    * Description: The recovered airmass value calculated in mktellu calculation
    * Type: float

  KW_MKTELL_BLAZE_CUT

    * Description: The blaze normalization cut used for mktellu calculation
    * Type: float

  KW_MKTELL_BLAZE_PRCT

    * Description: The blaze percentile used for mktellu calculation
    * Type: float

  KW_MKTELL_DEF_CONV_WID

    * Description: The default convolution width in pix used for mktellu calculation
    * Type: int

  KW_MKTELL_TEMPHASH

    * Description: the hash for the template generation (unique)
    * Type: str

  KW_MKTELL_TEMPNUM

    * Description: the number of template files used
    * Type: str

  KW_MKTELL_TEMPTIME

    * Description: the time the template was generated
    * Type: str

  KW_MKTELL_TEMP_FILE

    * Description: The template file used for mktellu calculation
    * Type: str

  KW_MKTELL_TEMP_MEDFILT

    * Description: The median filter width used for mktellu calculation
    * Type: float

  KW_MKTELL_THRES_TFIT

    * Description: The min transmission requirement used for mktellu/ftellu
    * Type: float

  KW_MKTELL_TRANS_FIT_UPPER_BAD

    * Description: The upper limit for trans fit used in mktellu/ftellu
    * Type: float

  KW_MKTELL_WATER

    * Description: The recovered water optical depth calculated in mktellu calculation
    * Type: float

  KW_MKTEMP_BERV_COV

    * Description: the berv coverage calculated for this template calculation
    * Type: float

  KW_MKTEMP_BERV_COV_MIN

    * Description: the minimum berv coverage allowed for this template calculation
    * Type: float

  KW_MKTEMP_BERV_COV_RES

    * Description: the resolution used for this template calculation
    * Type: float

  KW_MKTEMP_BERV_COV_SNR

    * Description: the core snr used for this template calculation
    * Type: float

  KW_MKTEMP_HASH

    * Description: store a unique hash for this template (based on file name etc)
    * Type: str

  KW_MKTEMP_NFILES

    * Description: store the number of files used to create template
    * Type: int

  KW_MKTEMP_SNR_ORDER

    * Description: the snr order used for quality control cut in make template calculation
    * Type: int

  KW_MKTEMP_SNR_THRES

    * Description: the snr threshold used for quality control cut in make template calculation
    * Type: float

  KW_MKTEMP_TIME

    * Description: store time template was created
    * Type: float

  KW_NEXP

    * Description: define the total number of exposures HEADER key
    * Type: int

  KW_OBJDEC

    * Description: define the observation dec HEADER key
    * Type: float

  KW_OBJDECPM

    * Description: define the observation proper motion in dec HEADER key
    * Type: float

  KW_OBJECTNAME

    * Description: define the raw observation name
    * Type: str

  KW_OBJEQUIN

    * Description: define the observation equinox HEADER key
    * Type: float

  KW_OBJNAME

    * Description: define the observation name
    * Type: str

  KW_OBJRA

    * Description: define the observation ra HEADER key
    * Type: float

  KW_OBJRAPM

    * Description: define the observation proper motion in ra HEADER key
    * Type: float

  KW_OBJ_TEMP

    * Description: define the object temperature HEADER key
    * Type: float

  KW_OBSTYPE

    * Description: define the observation type HEADER key
    * Type: str

  KW_OUTPUT

    * Description: the output key for drs outputs
    * Type: str

  KW_PID

    * Description: DRS process ID
    * Type: str

  KW_PI_NAME

    * Description: define the pi name HEADER key
    * Type: str

  KW_PLX

    * Description: define the parallax HEADER key
    * Type: float

  KW_POLAR_LSD_FIT_RESOL

    * Description: define the Resolving power from gaussian fit from polar lsd
    * Type: float

  KW_POLAR_LSD_FIT_RV

    * Description: define the Radial velocity (km/s) from gaussian fit from polar lsd
    * Type: float

  KW_POLAR_LSD_MASK

    * Description: define the LSD mask filename
    * Type: str

  KW_POLAR_LSD_MEANNULL

    * Description: define the Mean of null LSD profile
    * Type: float

  KW_POLAR_LSD_MEANPOL

    * Description: define the Mean polarization of data in LSD
    * Type: float

  KW_POLAR_LSD_MEANSVQU

    * Description: define the mean of pol LSD profile
    * Type: float

  KW_POLAR_LSD_MEDABSDEV

    * Description: define the Med abs dev polarization of data in LSD
    * Type: float

  KW_POLAR_LSD_MEDPOL

    * Description: define the Median polarization of data in LSD
    * Type: float

  KW_POLAR_LSD_MLDEPTH

    * Description: define the minimum line depth value used in LSD analysis
    * Type: float

  KW_POLAR_LSD_NBIN1

    * Description: define the bin size used for norm continuum
    * Type: int

  KW_POLAR_LSD_NBIN2

    * Description: define the bin sized used in profile calc
    * Type: int

  KW_POLAR_LSD_NLAP1

    * Description: define the overlap used for norm continuum
    * Type: int

  KW_POLAR_LSD_NLAP2

    * Description: define the overlap used in profile calc
    * Type: int

  KW_POLAR_LSD_NLFIT1

    * Description: define whether a linear fit was used for norm continuum
    * Type: bool

  KW_POLAR_LSD_NLFIT2

    * Description: define whether a linear fit was used in profile calc
    * Type: bool

  KW_POLAR_LSD_NMODE1

    * Description: define the mode used for norm continuum
    * Type: str

  KW_POLAR_LSD_NMODE2

    * Description: define the mode used in profile calc
    * Type: str

  KW_POLAR_LSD_NORM

    * Description: Define whether stokesI was normalised by continuum
    * Type: bool

  KW_POLAR_LSD_NPOINTS

    * Description: define the Number of points for LSD profile
    * Type: int

  KW_POLAR_LSD_NSIG1

    * Description: define the sig clip used for norm continuum
    * Type: float

  KW_POLAR_LSD_NSIG2

    * Description: define the sigma clip used in profile calc
    * Type: float

  KW_POLAR_LSD_NWIN1

    * Description: define the window size used for norm continuum
    * Type: int

  KW_POLAR_LSD_NWIN2

    * Description: define the window size used in profile calc
    * Type: int

  KW_POLAR_LSD_STDNULL

    * Description: define the Std dev of null LSD profile
    * Type: float

  KW_POLAR_LSD_STDPOL

    * Description: define the Std dev polarization of data in LSD
    * Type: float

  KW_POLAR_LSD_STDSVQU

    * Description: define the Std dev of pol LSD profile
    * Type: float

  KW_POLAR_LSD_VFINAL

    * Description: Define final velocity value used in LSD analysis
    * Type: float

  KW_POLAR_LSD_VINIT

    * Description: Define initial velocity value used in LSD analysis
    * Type: float

  KW_POL_BERVCEN

    * Description: define the BERV at center of observation
    * Type: float

  KW_POL_BERVS

    * Description: define the bervs for exposure list
    * Type: float

  KW_POL_BJDCEN

    * Description: define the BJD at center of observation
    * Type: float

  KW_POL_BJDS

    * Description: define the bjds for exposure list
    * Type: float

  KW_POL_ELAPTIME

    * Description: define the Elapsed time of observation (sec)
    * Type: float

  KW_POL_EXPS

    * Description: define the exposure times of exposure list
    * Type: float

  KW_POL_EXPTIME

    * Description: define the Total exposure time (sec)
    * Type: float

  KW_POL_FILES

    * Description: define the base file name exposure list
    * Type: str

  KW_POL_LSD_COL1

    * Description: define the lsd column: Velocities (km/s)
    * Type: str

  KW_POL_LSD_COL2

    * Description: define the lsd column: Stokes I LSD profile
    * Type: str

  KW_POL_LSD_COL3

    * Description: define the lsd column: Gaussian fit to Stokes I LSD profile
    * Type: str

  KW_POL_LSD_COL4

    * Description: define the lsd column: Stokes V, U, or Q LSD profile
    * Type: str

  KW_POL_LSD_COL5

    * Description: define the lsd column: Null polarization LSD profile
    * Type: str

  KW_POL_MEANBJD

    * Description: define the Mean BJD for polar sequence
    * Type: float

  KW_POL_METHOD

    * Description: defines the Polarimetry method
    * Type: str

  KW_POL_MJDCEN

    * Description: define the MJD at center of observation
    * Type: float

  KW_POL_MJDENDS

    * Description: define the mjdends at end for exposure list
    * Type: float

  KW_POL_MJDS

    * Description: define the mjds at start for exposure list
    * Type: float

  KW_POL_NEXP

    * Description: define Number of exposures for polarimetry
    * Type: int

  KW_POL_STOKES

    * Description: define the Stokes paremeter: Q, U, V, or I
    * Type: str

  KW_PPMSTR_FILE

    * Description: Define the key to store the name of the pp master file used in pp (if used)
    * Type: str

  KW_PPMSTR_NSIG

    * Description: The number of sigma used to construct pp master mask
    * Type: float

  KW_PPSHIFTX

    * Description: The shift in pixels so that image is at same location as engineering flat
    * Type: float

  KW_PPSHIFTY

    * Description: The shift in pixels so that image is at same location as engineering flat
    * Type: float

  KW_PPVERSION

    * Description: DRS preprocessing version
    * Type: str

  KW_RDNOISE

    * Description: define the read noise HEADER key a.k.a sigdet (used to get value only)
    * Type: float

  KW_S1D_BLAZET

    * Description: the blaze threshold used for the s1d
    * Type: float

  KW_S1D_BVELO

    * Description: the bin size for wave grid kind=velocity
    * Type: float

  KW_S1D_BWAVE

    * Description: the bin size for wave grid kind=wave
    * Type: float

  KW_S1D_KIND

    * Description: the wave grid kind used for s1d (wave or velocity)
    * Type: str

  KW_S1D_SMOOTH

    * Description: the smooth size for the s1d
    * Type: float

  KW_S1D_WAVEEND

    * Description: the wave end point used for s1d
    * Type: float

  KW_S1D_WAVESTART

    * Description: the wave starting point used for s1d
    * Type: float

  KW_SATURATE

    * Description: define the saturation limit HEADER key
    * Type: float

  KW_SAT_LEVEL

    * Description: the max saturation level
    * Type: int

  KW_SAT_QC

    * Description: the saturation QC limit
    * Type: int

  KW_SHAPE_A

    * Description: Shape transform A parameter
    * Type: float

  KW_SHAPE_B

    * Description: Shape transform B parameter
    * Type: float

  KW_SHAPE_C

    * Description: Shape transform C parameter
    * Type: float

  KW_SHAPE_D

    * Description: Shape transform D parameter
    * Type: float

  KW_SHAPE_DX

    * Description: Shape transform dx parameter
    * Type: float

  KW_SHAPE_DY

    * Description: Shape transform dy parameter
    * Type: float

  KW_TARGET_TYPE

    * Description: define the target type (object/sky)
    * Type: str

  KW_TELLUP_ABSOEXPO_KEXP

    * Description: Define the gauss shape of the kernel used in abso_expo for tellu pre-cleaning
    * Type: float

  KW_TELLUP_ABSOEXPO_KTHRES

    * Description: Define the kernel threshold in abso_expo used in tellu pre-cleaning
    * Type: int

  KW_TELLUP_ABSOEXPO_KWID

    * Description: Define the gauss width of the kernel used in abso_expo for tellu pre-cleaning
    * Type: float

  KW_TELLUP_CCFP_OTHERS

    * Description: Define the ccf power of the others
    * Type: float

  KW_TELLUP_CCFP_WATER

    * Description: Define the ccf power of the water
    * Type: float

  KW_TELLUP_CCF_SRANGE

    * Type: float

  KW_TELLUP_DEXPO_CONV_THRES

    * Description: Define dexpo convergence threshold used
    * Type: float

  KW_TELLUP_DEXPO_MAX_ITR

    * Description: Define the maximum number of operations used to get dexpo convergence
    * Type: int

  KW_TELLUP_DFLT_WATER

    * Description: Define default water absorption used (tellu pre-cleaning)
    * Type: float

  KW_TELLUP_DO_PRECLEAN

    * Description: Define whether precleaning was done (tellu pre-cleaning)
    * Type: bool

  KW_TELLUP_DVGRID

    * Description: Define the dv wave grid (same as s1d) in km/s used
    * Type: float

  KW_TELLUP_DV_OTHERS

    * Description: Define the velocity of other species absorbers calculated in telluric preclean process
    * Type: float

  KW_TELLUP_DV_WATER

    * Description: Define the velocity of water absorbers calculated in telluric preclean process
    * Type: float

  KW_TELLUP_EXPO_OTHERS

    * Description: Define the exponent of other species from telluric preclean process
    * Type: float

  KW_TELLUP_EXPO_WATER

    * Description: Define the exponent of water key from telluric preclean process
    * Type: float

  KW_TELLUP_FORCE_AIRMASS

    * Description: Define the whether to force fit to header airmass used for tellu pre-cleaning
    * Type: bool

  KW_TELLUP_OTHER_BOUNDS

    * Description: Define the bounds of the exponent of other species used for tellu pre-cleaning
    * Type: str

  KW_TELLUP_REMOVE_ORDS

    * Description: Define which orders were removed from tellu pre-cleaning
    * Type: str

  KW_TELLUP_SNR_MIN_THRES

    * Description: Define which min snr threshold was used for tellu pre-cleaning
    * Type: float

  KW_TELLUP_TRANS_SIGL

    * Description: Define the threshold for discrepant tramission used for tellu pre-cleaning
    * Type: float

  KW_TELLUP_TRANS_THRES

    * Description: Define the exponent of the transmission threshold used for tellu pre-cleaning
    * Type: float

  KW_TELLUP_WATER_BOUNDS

    * Description: Define the bounds of the exponent of water used for tellu pre-cleaning
    * Type: str

  KW_TELLUP_WAVE_END

    * Description: Define the wave end (same as s1d) in nm used
    * Type: float

  KW_TELLUP_WAVE_START

    * Description: Define the wave start (same as s1d) in nm used
    * Type: float

  KW_USED_CONT_BINSIZE

    * Description: define the continuum bin size used
    * Type: int

  KW_USED_CONT_OVERLAP

    * Description: define the continuum overlap used
    * Type: int

  KW_USED_MIN_FILES

    * Description: define the minimum number of files used
    * Type: int

  KW_USED_VALID_FIBERS

    * Description: define all possible fibers for polarimetry used
    * Type: str

  KW_USED_VALID_STOKES

    * Description: define all possible stokes parameters used
    * Type: str

  KW_UTC_OBS

    * Description: define the observation time HEADER key
    * Type: float

  KW_VERSION

    * Description: DRS version
    * Type: str

  KW_WAVECOEFFS

    * Description: the wave coefficients
    * Type: float

  KW_WAVEFILE

    * Description: the wave file used
    * Type: str

  KW_WAVESOURCE

    * Description: the wave source of the wave file used
    * Type: str

  KW_WAVETIME

    * Description: the wave file mid exptime [mjd]
    * Type: float

  KW_WAVE_DEG

    * Description: fit degree for wave solution
    * Type: int

  KW_WAVE_ECHELLE_START

    * Description: the echelle number of the first order used
    * Type: int

  KW_WAVE_FITDEG

    * Description: the fit degree for wave solution used
    * Type: int

  KW_WAVE_HCG_EWMAX

    * Description: the min e-width of the line for gaussian peak fitting used
    * Type: float

  KW_WAVE_HCG_EWMIN

    * Description: the min e-width of the line for gaussian peak fitting used
    * Type: float

  KW_WAVE_HCG_FB_RMSMAX

    * Description: the max rms for gaussian peak fitting used
    * Type: float

  KW_WAVE_HCG_FB_RMSMIN

    * Description: the min rms for gaussian peak fitting used
    * Type: float

  KW_WAVE_HCG_GFITMODE

    * Description: the fit degree for the gaussian peak fitting used
    * Type: int

  KW_WAVE_HCG_SIGPEAK

    * Description: the sigma above local rms for fitting hc lines used
    * Type: float

  KW_WAVE_HCG_WSIZE

    * Description: the width of the box for fitting hc lines used
    * Type: int

  KW_WAVE_HCLL_FILE

    * Description: the filename for the HC line list generated
    * Type: str

  KW_WAVE_LITT_EXT_FITDEG_1

    * Description: the littrow extrapolation fit degree value used for HC
    * Type: int

  KW_WAVE_LITT_EXT_ORD_START_1

    * Description: the littrow extrapolation start order value used for HC
    * Type: int

  KW_WAVE_LITT_FITDEG_1

    * Description: the littrow fit degree value used for HC
    * Type: int

  KW_WAVE_LITT_XCUTSTEP_1

    * Description: the littrow x cut step value used for HC
    * Type: int

  KW_WAVE_LIT_END_1

    * Description: the littrow end order used for HC
    * Type: float

  KW_WAVE_LIT_ORDER_END_1

    * Description: the littrow order end value used for HC
    * Type: int

  KW_WAVE_LIT_ORDER_INIT_1

    * Description: the littrow order initial value used for HC
    * Type: int

  KW_WAVE_LIT_ORDER_START_1

    * Description: the littrow order start value used for HC
    * Type: int

  KW_WAVE_LIT_RORDERS

    * Description: the orders removed from the littrow test
    * Type: float

  KW_WAVE_LIT_START_1

    * Description: the littrow start order used for HC
    * Type: int

  KW_WAVE_MODE_FP

    * Description: the mode used to calculate the fp wave solution
    * Type: str

  KW_WAVE_MODE_HC

    * Description: the mode used to calculate the hc wave solution
    * Type: str

  KW_WAVE_NBO

    * Description: Number of orders in wave image
    * Type: int

  KW_WAVE_RES_MAPSIZE

    * Description: the wave resolution map dimensions
    * Type: int

  KW_WAVE_RES_MAXDEVTHRES

    * Description: the max deviation in rms allowed in wave resolution map
    * Type: float

  KW_WAVE_RES_WSIZE

    * Description: the width of the box for wave resolution map
    * Type: float

  KW_WAVE_TRP_CATGDIST

    * Description: the max distance between catalog line and initial guess line in triplet fit
    * Type: float

  KW_WAVE_TRP_DVCUTALL

    * Description: the distance away in dv to reject all triplet in triplet fit
    * Type: float

  KW_WAVE_TRP_DVCUTORD

    * Description: the distance away in dv to reject order triplet in triplet fit
    * Type: float

  KW_WAVE_TRP_FITDEG

    * Description: the fit degree for triplet fit
    * Type: int

  KW_WAVE_TRP_MIN_NLINES

    * Description: the minimum number of lines required per order in triplet fit
    * Type: int

  KW_WAVE_TRP_NBRIGHT

    * Description: the number of bright lines to used in triplet fit
    * Type: int

  KW_WAVE_TRP_NITER

    * Description: the number of iterations done in triplet fit
    * Type: float

  KW_WAVE_TRP_ORDER_FITCONT

    * Description: the degree(s) of fit to ensure continuity in triplet fit
    * Type: float

  KW_WAVE_TRP_SCLIPNUM

    * Description: the iteration number for sigma clip in triplet fit
    * Type: float

  KW_WAVE_TRP_SCLIPTHRES

    * Description: the sigma clip threshold in triplet fit
    * Type: float

  KW_WAVE_TRP_TOT_NLINES

    * Description: the total number of lines required in triplet fit
    * Type: int

  KW_WEATHER_TOWER_TEMP

    * Description: define the weather tower temperature HEADER key
    * Type: float

  KW_WFP_BLZ_THRES

    * Description: the blaze threshold used for FP wave sol improvement
    * Type: float

  KW_WFP_BOXSIZE

    * Description: The boxsize used for FP file CCF
    * Type: int

  KW_WFP_CAVFIT_DEG

    * Description: the polynomial degree fit order used for fitting the fp cavity
    * Type: int

  KW_WFP_CM_INDX

    * Description: the index to start crossmatching fps at
    * Type: float

  KW_WFP_CONTRAST

    * Description: Contrast of the wave FP file CCF
    * Type: float

  KW_WFP_CUTWIDTH

    * Description: the normalised cut width for large peaks used
    * Type: float

  KW_WFP_DETNOISE

    * Description: The det noise used for the FP file CCF
    * Type: float

  KW_WFP_DOPD0

    * Description: the initial value of the FP effective cavity width used
    * Type: float

  KW_WFP_DRIFT

    * Description: drift of the FP file used for the wavelength solution
    * Type: float

  KW_WFP_DVMAX

    * Description: the max dv to keep hc lines used
    * Type: float

  KW_WFP_ERRX_MIN

    * Description: the minimum instrumental error used
    * Type: float

  KW_WFP_FILE

    * Description: Wavelength solution for fiber C that is source of the WFP keys
    * Type: str

  KW_WFP_FPCAV_MODE

    * Description: the mode used to fit the FP cavity
    * Type: int

  KW_WFP_FWHM

    * Description: FWHM of the wave FP file CCF
    * Type: float

  KW_WFP_LARGE_JUMP

    * Description: the largest jump in fp that was allowed
    * Type: float

  KW_WFP_LIMIT

    * Description: the normalised limited used to detect FP peaks
    * Type: float

  KW_WFP_LINES

    * Description: Number of lines for the wave FP file CCF
    * Type: float

  KW_WFP_LLFITDEG

    * Description: the used polynomial fit degree (to fit wave solution)
    * Type: int

  KW_WFP_LLFIT_MODE

    * Description: the mode used to fit the wavelength
    * Type: int

  KW_WFP_LL_OFFSET

    * Description: the maximum fraction wavelength offset btwn xmatch fp peaks used
    * Type: float

  KW_WFP_MASK

    * Description: Mask for the wave FP file CCF
    * Type: float

  KW_WFP_MASKMIN

    * Description: The weight of the CCF mask (if 1 force all weights equal) used for FP CCF
    * Type: float

  KW_WFP_MASKUNITS

    * Description: The units of the input CCF mask (converted to nm in code)
    * Type: str

  KW_WFP_MASKWID

    * Description: The width of the CCF mask template line (if 0 use natural) used for FP CCF
    * Type: float

  KW_WFP_MAXFLUX

    * Description: The max flux used for the FP file CCF
    * Type: float

  KW_WFP_MAXLL_FIT_RMS

    * Description: the max rms for the wave sol sig clip
    * Type: float

  KW_WFP_NMAX

    * Description: the highest order used for the FP file CCF
    * Type: int

  KW_WFP_NPERCENT

    * Description: the percentile to normalise the FP flux per order used
    * Type: float

  KW_WFP_ORD_FINAL

    * Description: the last order used for FP wave sol improvement
    * Type: int

  KW_WFP_ORD_START

    * Description: the first order used for FP wave sol improvement
    * Type: int

  KW_WFP_SIGDET

    * Description: The sigdet used for FP file CCF
    * Type: float

  KW_WFP_STEP

    * Description: Step for the wave FP file CCF
    * Type: float

  KW_WFP_TARG_RV

    * Description: Target RV for the wave FP file CCF
    * Type: float

  KW_WFP_T_ORD_START

    * Description: the echelle number used for the first order
    * Type: int

  KW_WFP_UPDATECAV

    * Description: whether the cavity file was updated
    * Type: int

  KW_WFP_WEI_THRES

    * Description: the weight below which fp lines are rejected
    * Type: float

  KW_WFP_WIDTH

    * Description: Width for the wave FP file CCF
    * Type: float

  KW_WFP_WIDUSED

    * Description: the FP widths used for each order (1D list)
    * Type: float

  KW_WFP_XDIFF_MAX

    * Description: the maximum fp peak pixel sep used for FP wave sol improvement
    * Type: float

  KW_WFP_XDIFF_MIN

    * Description: the minimum fp peak pixel sep used for FP wave sol improvement
    * Type: float

  KW_WNT_DCAVITY

    * Description: starting point for the cavity corrections used in wave night
    * Type: int

  KW_WNT_DCAVSRCE

    * Description: source fiber for the cavity correction
    * Type: str

  KW_WNT_HCSIGCLIP

    * Description: define the sigma clip value to remove bad hc lines used
    * Type: float

  KW_WNT_MADLIMIT

    * Description: median absolute deviation cut off used
    * Type: float

  KW_WNT_NITER1

    * Description: number of iterations for convergence used in wave night (hc)
    * Type: int

  KW_WNT_NITER2

    * Description: number of iterations for convergence used in wave night (fp)
    * Type: int

  KW_WNT_NSIG_FIT

    * Description: sigma clipping for the fit used in wave night
    * Type: int
      
      
      
      
      
      
      
      
      
      