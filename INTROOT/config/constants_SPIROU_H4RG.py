# -----------------------------------------------------------------------------
#
#   This is the SPIROU DRS constants config file
#
# -----------------------------------------------------------------------------
#        Read Me:
#
#        Lines must either start with a # or be a key-value pair or be a blank
#            line, blank lines and lines that start with a # will be ignored
#
#        Key value pairs are of the form:
#                 key = value
#
#        Note python will try to interpret values so basic math is allowed:
#
#        i.e.   x = 10 + 10
#
#        will be interpreted in the parameter dictionary (p) as:
#
#        p['x'] = 100
#
#        and will be an integer.
#
#        Interpretation works as in eval('10 + 10')
#
#            [Try it in python for the result that will be passed to the
#             parameter dictionary]
#

# -----------------------------------------------------------------------------
#  General variables
# -----------------------------------------------------------------------------

#   detector type (from switching between H2RG and H4RG)
ic_image_type = "H4RG"

#   Interval between plots (for certain interactive graphs)          - [cal_loc]
#       formally ic_disptimeout
ic_display_timeout = 0.5

#   The number of night name directories to display when there is        - [all]
#       no night name argument
drs_night_name_display_limit = 10

# -----------------------------------------------------------------------------
#  CFHT variables
# -----------------------------------------------------------------------------

#  Defines the CFHT longitude West (deg)                             - [cal_CCF]
ic_longit_obs = 155.468876
#  Defines the CFHT latitude North (deg)                             - [cal_CCF]
ic_latit_obs = 19.825252
#  Defines the CFHT altitude (km)                                    - [cal_CCF]
ic_altit_obs = 4.204

# -----------------------------------------------------------------------------
#  image variables
# -----------------------------------------------------------------------------

#   Resize blue window                                              - [cal_dark]
ic_ccdx_blue_low = 100  # 500
ic_ccdx_blue_high = 4000  # 3500
ic_ccdy_blue_low = 3300  # 2000
ic_ccdy_blue_high = 3720  # 3500

#   Resize red window                                               - [cal_dark]
ic_ccdx_red_low = 100
ic_ccdx_red_high = 4000
ic_ccdy_red_low = 780
ic_ccdy_red_high = 1200

#   Resize image                                                     - [cal_loc]
ic_ccdx_low = 4
ic_ccdx_high = 4092
ic_ccdy_low = 250  # 100 #4
ic_ccdy_high = 3350  # 3450

#    Define the types of fiber to look for            - [cal_extract, cal_drift]
#       (earlier in list takes priority)
fiber_types = ['AB', 'A', 'B', 'C']

#    Define whether to use SKYDARK for dark corrections                  - [all]
use_skydark_correction = False

#    If use_skydark_correction is True define whether we use
#       the SKYDARK only or use SKYDARK/DARK (whichever is closest)
use_skydark_only = False

# -----------------------------------------------------------------------------
#   fiber variables
# -----------------------------------------------------------------------------
#    MUST have "_fpall" at the end
#    MUST be a dictionary in form:
#         {"fibertype":value, "fibertype":value}
#
#    i.e.    {'AB':1, 'C':2, 'A':3}

#   Number of fibers                                                 - [cal_loc]
nbfib_fpall = {'AB': 2, 'A': 1, 'B': 1, 'C': 1}

#   Number of orders to skip at start of image                       - [cal_loc]
ic_first_order_jump_fpall = {'AB': 2, 'A': 0, 'B': 0, 'C': 1}

#   Maximum number of order to use                                   - [cal_loc]
ic_locnbmaxo_fpall = {'AB': 98, 'A': 49, 'B': 49, 'C': 49}

#   Quality control "normal" number of orders on fiber               - [cal_loc]
qc_loc_nbo_fpall = {'AB': 98, 'A': 49, 'B': 49, 'C': 49}

#   Fiber type                                                        - [cal_ff]
fib_type_fpall = {'AB': ['AB'], 'A': ['A'], 'B': ['B'], 'C': ['C']}

#   Half-zone extraction width left side (formally plage1)            - [cal_ff]
ic_ext_range1_fpall = {'AB': 16., 'A': 8., 'B': 8., 'C': 7.}

#   Half-zone extraction width right side (formally plage2)           - [cal_ff]
ic_ext_range2_fpall = {'AB': 16., 'A': 8., 'B': 8., 'C': 7.}

#   Half-zone extraction width for full extraction               - [cal_extract]
#       (formally ic_ext_nbsig)
ic_ext_range_fpall = {'AB': 14.5, 'A': 14.5, 'B': 14.5, 'C': 7.5}

#   Localisation fiber for extraction                            - [cal_extract]
loc_file_fpall = {'AB': 'AB', 'A': 'AB', 'B': 'AB', 'C': 'C'}

#   Order profile fiber for extraction                           - [cal_extract]
orderp_file_fpall = {'AB': 'AB', 'A': 'AB', 'B': 'AB', 'C': 'C'}

#   Half-zone extract width for right and left side                - [cal_drift]
#       (formally ic_extnbsig)
ic_ext_d_range_fpall = {'AB': 14.0, 'A': 14.0, 'B': 14.0, 'C': 7.0}

# -----------------------------------------------------------------------------
#   cal_preprocess parameters
# -----------------------------------------------------------------------------

# define output type. Currently excepted values are:                  - [cal_pp]
#    mode=0:    adds only the processed_suffix
#    mode=1:    adds the processed_suffix and an identifying suffix
#               (i.e. flat_dark, dark_dark etc)
pp_mode = 0

# force pre-processed files only (Should be 1 or True to check and       - [all]
#     force DRS to accept pre-processed files only - i.e. rotated and
#     corrected) - if 0 or False DRS will except any file
#     (at users own risk)
ic_force_preprocess = 1

#   Define the suffix to apply to the pre-processed files                - [all]
#       if "None" then no suffix is added (or checked for)
processed_suffix = '_pp.fits'

#   Define the number of dark amplifiers                              - [cal_pp]
number_dark_amp = 5

#   Define the total number of amplifiers                             - [cal_pp]
total_amp_num = 32

#   Define the number of un-illuminated reference pixels at           - [cal_pp]
#       top of image
number_ref_top = 4

#   Define the number of un-illuminated reference pixels at           - [cal_pp]
#       bottom of image
number_ref_bottom = 4

#   Define the number of bins used in the dark median process         - [cal_pp]
dark_med_binnum = 32

#   Define rotation angle (must be multiple of 90 degrees)            - [cal_pp]
#       (in degrees counter-clockwise direction)
raw_to_pp_rotation = -90

# Defines the size around badpixels that is considered part of        - [cal_pp]
#    the bad pixel
PP_CORRUPT_MED_SIZE = 2

# Defines the threshold (above the full engineering flat)             - [cal_pp]
#     that selects bad (hot) pixels
PP_CORRUPT_HOT_THRES = 2

# Defines the snr hotpix threshold to define a corrupt file           - [cal_pp]
PP_CORRUPT_SNR_HOTPIX = 10

# Defines the RMS threshold to also catch corrupt files
PP_CORRUPT_RMS_THRES = 0.15

# Define the percentile value for the rms normalisation (0-100)
PP_RMS_PERCENTILE = 95

# Define the lowest rms value of the rms percentile allowed
#    if the value of the pp_rms_percentile-th is lower than this this
#    value is used
PP_LOWEST_RMS_PERCENTILE = 10


# -----------------------------------------------------------------------------
#   cal_dark parameters
# -----------------------------------------------------------------------------

#   The lower percentile (0 - 100)                                  - [cal_dark]
dark_qmin = 5

#   The upper percentile (0 - 100)                                  - [cal_dark]
dark_qmax = 95

#   The number of bins in dark histogram                            - [cal_dark]
histo_bins = 200

#   The range of the histogram in ADU/s                             - [cal_dark]
histo_range_low = -0.2
histo_range_high = 0.8

#   Define a bad pixel cut limit (in ADU/s)                         - [cal_dark]
dark_cutlimit = 5.0

# -----------------------------------------------------------------------------
#   cal_loc parameters
# -----------------------------------------------------------------------------

#   Size of the order_profile smoothed box                           - [cal_loc]
#     (from pixel - size to pixel + size)
loc_box_size = 5  # 5   # 10

#   row number of image to start processing at                       - [cal_loc]
ic_offset = 0  # 40

#   Definition of the central column                       - [cal_loc, cal_slit]
#      (formally ic_ccdcolc)
ic_cent_col = 2500

#   Definition of the extraction window size (half size)             - [cal_loc]
ic_ext_window = 15  # 20 #40 #12

#   Definition of the gap index in the selected area                 - [cal_loc]
#       (formally ic_ccdgap)
ic_image_gap = 0

#   Define the column separation for fitting orders                  - [cal_loc]
ic_locstepc = 20  # 20

#   Define minimum width of order to be accepted                     - [cal_loc]
ic_widthmin = 10  # 5

#   Define the noise multiplier threshold in order to accept an      - [cal_loc]
#       order center as usable
#       max(pixel value) - min(pixel value) > ic_noise_mult_thres * sigdet
ic_noise_mult_thres = 50  # 30  #10 # 100.0

#   Define the polynomial fit parameters for interpolating over the  - [cal_loc]
#      bad regions (holes) before localization is done
bad_region_fit = [3.19884964e-05, -1.08289228e-01, 2.16643659e+03]

#   Define the median_filter box size used in interpolating over the - [cal_loc]
#      bad regions (holes) before localization is done
bad_region_med_size = 101

#   Define the threshold below which the image (normalised between   - [cal_loc]
#      0 and 1) should be regarded as bad. Used in interpolating over
#      the bad regions (holes) before localization is done
bad_region_threshold = 0.2

#   Define the box size (kernel) for the convolution used in         - [cal_loc]
#      interpolating over the bad regions (holes) before localization
#      is done
bad_region_kernel_size = 51

#   Define the median_filter box size used in interpolating over the - [cal_loc]
#      bad regions (holes) (during the convolution) before
#      localization is done
bad_region_med_size2 = 11

#   Define the thresholds (of the ratio between original image and   - [cal_loc]
#      the interpolated image) where pixels are deem "good" and "bad".
#      For use in interpolating over the bad regions (holes) before
#      localization is done
bad_region_good_value = 0.5
bad_region_bad_value = 0.25

#   Half spacing between orders                                      - [cal_loc]
ic_locnbpix = 45  # 45

#   Minimum amplitude to accept (in e-)                              - [cal_loc]
ic_min_amplitude = 10  # 10 # 50

#   Normalised amplitude threshold to accept pixels                  - [cal_loc]
#       for background calculation
ic_locseuil = 0.17  # 0.18

#   Saturation threshold on order profile plot                       - [cal_loc]
ic_satseuil = 1000  # 64536

#   Order of polynomial to fit for positions                         - [cal_loc]
ic_locdfitc = 4  # 5

#   Order of polynomial to fit for widths                            - [cal_loc]
ic_locdfitw = 4  # 5

#   Order of polynomial to fit for position error             - [spirouKeywords]
#      Currently not used
ic_locdfitp = 3

#   Maximum rms for sigma-clip order fit (center positions)          - [cal_loc]
ic_max_rms_center = 0.1

#   Maximum peak-to-peak for sigma-clip order fit                    - [cal_loc]
#      (center positions)
ic_max_ptp_center = 0.300  # 0.200

#   Maximum frac ptp/rms for sigma-clip order fit                    - [cal_loc]
#      (center positions)
ic_ptporms_center = 8.0

#   Maximum rms for sigma-clip order fit (width)                     - [cal_loc]
ic_max_rms_fwhm = 1.0

#   Maximum fractional peak-to-peak for sigma-clip order             - [cal_loc]
#       fit (width)
ic_max_ptp_fracfwhm = 10.0

#   Currently only used in keywords for loco file                       - [None]
#       Delta width (pix) for 3 convol shape model
ic_loc_delta_width = 1.85

#   Localisation option 1: Option for archiving the location image   - [cal_loc]
ic_locopt1 = 1

# -----------------------------------------------------------------------------
#   cal_slit (tilt) parameters
# -----------------------------------------------------------------------------

#   oversampling factor (for tilt finding)
ic_tilt_coi = 10

#   Offset multiplicative factor (for width)                        - [cal_slit]
ic_facdec = 0.9  # 1.6

#   Order of polynomial to fit for tilt                             - [cal_slit]
ic_tilt_fit = 4

#   Order to plot on slit image plot                                - [cal_slit]
ic_slit_order_plot = 2 * 2

# -----------------------------------------------------------------------------
#   cal_slit (shape) parameters
# -----------------------------------------------------------------------------
# The number of iterations to run the shape finding out to         - [cal_shape]
shape_num_iterations = 4

# width of the ABC fibers                                          - [cal_shape]
shape_abc_width = 60

# the range of angles (in degrees) for the first iteration (large) - [cal_shape]
# and subsequent iterations (small)
shape_large_angle_range = [-12.0, 0.0]
shape_small_angle_range = [-1.0, 1.0]

# number of sections per order to split the order into             - [cal_shape]
shape_nsections = 32

# max sigma clip (in sigma) on points within a section             - [cal_shape]
shape_sigmaclip_max = 4

# the size of the median filter to apply along the order           - [cal_shape]
#     (in pixels)
shape_median_filter_size = 51

# The minimum value for the cross-correlation to be deemed good    - [cal_shape]
shape_min_good_correlation = 0.3

#  The selected order to plot for the slit shape plot              - [cal_shape]
shape_selected_order = 33

#  Define whether to output debug (sanity check) files             - [cal_shape]
shape_debug_outputs = True

# defines the shape offset xoffset (before and after) fp peaks     - [cal_shape]
SHAPEOFFSET_XOFFSET = 30

# defines the bottom percentile for fp peak                        - [cal_shape]
SHAPEOFFSET_BOTTOM_PERCENTILE = 10

# defines the top percentile for fp peak                           - [cal_shape]
SHAPEOFFSET_TOP_PERCENTILE = 95

# defines the floor below which top values should be set to        - [cal_shape]
#   this fraction away from the max top value
SHAPEOFFSET_TOP_FLOOR_FRAC = 0.1

# define the median filter to apply to the hc (high pass filter)   - [cal_shape]
SHAPEOFFSET_MED_FILTER_WIDTH = 15

# Maximum number of FP (larger than expected number                - [cal_shape]
#      (~10000 to ~25000)
SHAPEOFFSET_FPINDEX_MAX = 30000

# Define the valid length of a FP peak                             - [cal_shape]
SHAPEOFFSET_VALID_FP_LENGTH = 5

# Define the maximum allowed offset (in nm) that we allow for      - [cal_shape]
#     the detector)
SHAPEOFFSET_DRIFT_MARGIN = 20

# Define the number of iterations to do for the wave_fp            - [cal_shape]
#     inversion trick
SHAPEOFFSET_WAVEFP_INV_ITERATION = 5

# Define the border in pixels at the edge of the detector          - [cal_shape]
SHAPEOFFSET_MASK_BORDER = 30

# Define the minimum maxpeak value as a fraction of the            - [cal_shape]
#    maximum maxpeak
SHAPEOFFSET_MINIMUM_MAXPEAK_FRAC = 0.4

# Define the width of the FP mask (+/- the center)                 - [cal_shape]
SHAPEOFFSET_MASK_PIXWIDTH = 3

# Define the width of the FP to extract (+/- the center)           - [cal_shape]
SHAPEOFFSET_MASK_EXTWIDTH = 5

# Define the most deviant peaks                                    - [cal_shape]
SHAPEOFFSET_DEVIANT_PERCENTILES = [5, 95]

# Define the maximum error in FP order assignment                  - [cal_shape]
#    we assume that the error in FP order assignment could range
#    from -50 to +50 in practice, it is -1, 0 or +1 for the cases we've
#    tested to date
SHAPEOFFSET_FPMAX_NUM_ERROR = 50

# The number of sigmas that the HC spectrum is allowed to be       - [cal_shape]
#     away from the predicted (from FP) position
SHAPEOFFSET_FIT_HC_SIGMA = 3

# Define the maximum allowed maximum absolute deviation away       - [cal_shape]
#     from the error fit
SHAPEOFFSET_MAXDEV_THRESHOLD = 5

# very low thresholding values tend to clip valid points           - [cal_shape]
SHAPEOFFSET_ABSDEV_THRESHOLD = 0.2

# Define the first pass (short) median filter width for dx         - [cal_shape]
SHAPE_SHORT_DX_MEDFILT_WID = 9

# Define the second pass (long) median filter width for dx.        - [cal_shape]
#    Used to fill NaN positions in dx that are not covered by short pass
SHAPE_LONG_DX_MEDFILT_WID = 9

# -----------------------------------------------------------------------------
#   cal_ff parameters
# -----------------------------------------------------------------------------

#    Do background measurement (True = 1, False = 0)                  - [cal_ff]
ic_do_bkgr_subtraction = 1

#    Do background percentile to compute minium value (%)             - [cal_ff]
ic_bkgr_percent = 5

#    Half-size of window for background measurements                  - [cal_ff]
ic_bkgr_window = 50

#    Width of the box to produce the background mask
IC_BKGR_BOXSIZE = 64

#    Size in pixels of the convolve tophat for the background mask
IC_BKGR_MASK_CONVOLVE_SIZE = 7

#    If a pixel has this or more "dark" neighbours, we consider it dark
#        regardless of its initial value
IC_BKGR_N_BAD_NEIGHBOURS = 3

#    Number of orders in tilt file (formally nbo)                     - [cal_ff]
ic_tilt_nbo = 49  # 36

#    Start order of the extraction in cal_ff                          - [cal_ff]
#       if None starts from 0
ff_start_order = None

#    End order of the extraction in cal_ff                            - [cal_ff]
#       if None ends at last order
ff_end_order = None

#   Manually set the sigdet to use in weighted tilt extraction        - [cal_ff]
#       set to -1 to use from fitsfilename HEADER
#       (formally ccdsigdet)
ic_ff_sigdet = -1

#    Half size blaze smoothing window                                 - [cal_ff]
ic_extfblaz = 50

# Minimum relative e2ds flux for the blaze computation                - [cal_ff]
ic_fracminblaze = 16.

#    The blaze polynomial fit degree                                  - [cal_ff]
# (formally harded coded = 5)
ic_blaze_fitn = 10  # 10

#   Order to plot on ff image plot (formally ic_order_plot)           - [cal_ff]
ic_ff_order_plot = 4

#   Plot all order fits (True = 1, False = 0)                         - [cal_ff]
#        (takes slightly longer than just one example order)
ic_ff_plot_all_orders = 0

#   Define the orders not to plot on the RMS plot                     - [cal_ff]
#      should be a list of integers
ff_rms_plot_skip_orders = [0, 22, 23, 24, 25, 48]

# -----------------------------------------------------------------------------
#   cal_extract parameters
# -----------------------------------------------------------------------------

#    Start order of the extraction in cal_ff                     - [cal_extract]
#       if None starts from 0
ext_start_order = None

#    End order of the extraction in cal_ff                       - [cal_extract]
#       if None ends at last order
ext_end_order = None

# distance away from center to extract out to +/-                   - [cal_slit]
ic_extnbsig = 1  # 2.5

#   Select extraction type                                       - [cal_extract]
#        Should be one of the following:
#                 0 - Simple extraction
#                         (function = spirouEXTOR.extract_const_range)
#
#                 1 - weighted extraction
#                         (function = spirouEXTOR.extract_weight)
#
#                 2 - tilt extraction
#                         (function = spirouEXTOR.extract_tilt)
#
#                 3a - tilt weight extraction (old 1)
#                         (function = spirouEXTOR.extract_tilt_weight)
#
#                 3b - tilt weight extraction 2 (old)
#                         (function = spirouEXTOR.extract_tilt_weight_old2)
#
#                 3c - tilt weight extraction 2
#                         (function = spirouEXTOR.extract_tilt_weight2)
#
#                 3d - tilt weight extraction 2 (cosmic correction)
#                         (function = spirouEXTOR.extract_tilt_weight2cosm)
#
#                 4a - shape map + weight extraction
#                          (function = spirouEXTOR.extract_shape_weight)
#
#                 4b - shape map + weight extraction (cosmic correction)
#                          (function = spirouEXTOR.extract_shape_weight_cosm)
#
#                 5a - shape map + weight extraction + fractional pix
#                          (function = spirouEXTOR.extract_shape_weight2)
#
#                 5b - shape map + weight extraction (cosmic correction)
#                      + fractional pix
#                          (function = spirouEXTOR.extract_shape_weight_cosm2)
ic_extract_type = '5b'  # '3d'
# Now select the extraction type in cal_ff ONLY                       - [cal_FF]
ic_ff_extract_type = '5a'

#   Set the number of pixels to set as                   - [cal_extract, cal_FF]
#       the border (needed to allow for tilt to not go off edge of image)
ic_ext_tilt_bord = 2

#   Set a custom noise level for extract (formally sigdet)       - [cal_extract]
#       set to -1 to use sigdet from file header
ic_ext_sigdet = -1  # 100

#    Define order to plot                                        - [cal_extract]
ic_ext_order_plot = 7

#    Define the percentage of flux above which we use    - [cal_ff, cal_extract]
#        to cut
#        ONLY USED IF EXTRACT_TYPE = '3d'
ic_cosmic_sigcut = 0.25  # 0.25

#    Defines the maximum number of iterations we use     - [cal_ff, cal_extract]
#        to check for cosmics (for each pixel)
#        ONLY USED IF EXTRACT_TYPE = '3d'
ic_cosmic_thresh = 5



#    Define the first order for the S1D spectra                  - [cal_extract]
ic_start_order_1d = 1

#    Define the last order for the S1D spectra                   - [cal_extract]
ic_end_order_1d = 48

#   Define the start s1d wavelength (in nm)
extract_s1d_wavestart = 980

#   Define the end s1d wavelength (in nm)
extract_s1d_waveend = 2500

#    Define the s1d spectral bin for S1D spectra (nm) when uniform in wavelength
ic_bin_s1d_uwave = 0.005

#    Define the s1d spectral bin for S1D spectra (nm) when uniform in velocity
ic_bin_s1d_uvelo = 1.0

#    Define the s1d smoothing kernel for the transition between orders
#             in pixels
ic_s1d_edge_smooth_size = 20

#    Define the threshold hold for a good blaze value (below the maximum value)
#         here a value of 0.5 would be 50% of the maximum value
ic_s1d_blaze_min = 0.05


# -----------------------------------------------------------------------------
#   cal_drift parameters
# -----------------------------------------------------------------------------
#   The value of the noise for drift calculation                   - [cal_drift]
#      snr = flux/sqrt(flux + noise^2)
ic_drift_noise = 8.0  # 100

#  Option for the background correction [0/1]                      - [cal_drift]
ic_drift_back_corr = 0

#   The maximum flux for a good (unsaturated) pixel                - [cal_drift]
ic_drift_maxflux = 1.e9

#   The size around a saturated pixel to flag as unusable          - [cal_drift]
ic_drift_boxsize = 12

#   Define large number of files for which skip will be used       - [cal_drift]
drift_nlarge = 300

#   Skip (for large number of files this is the iterator to        - [cal_drift]
#      skip over) - i.e. do every "ic_drift_skip" files
#      also allows quick speed up of code
drift_file_skip = 3
drift_e2ds_file_skip = 1
drift_peak_file_skip = 1

#   Define the number of standard deviations cut at in             - [cal_drift]
#       cosmic renormalisation
ic_drift_cut_raw = 3
ic_drift_cut_e2ds = 4.5

#   Define the number of orders to use (starting from 0 to max)    - [cal_drift]
#       used to get median drift  median(order0 --> order max)
#       (not used in drift_e2ds)
ic_drift_n_order_max = 49  # 28

#   Define the starting order to use (starting from           - [cal_drift-peak]
#       0 to max) used to get median drift  median(order min --> order max)
#       (used in drift-peak_e2ds)
ic_drift_peak_n_order_min = 2

#   Define the number of orders to use (starting from         - [cal_drift-peak]
#       0 to max) used to get median drift  median(order min --> order max)
#       (used in drift-peak_e2ds)
ic_drift_peak_n_order_max = 30

#   Define the way to calculate the drift                          - [cal_drift]
#       either 'weighted mean' or 'median'
#       for cal_drift_raw and cal_drift_e2ds
drift_type_raw = 'median'
drift_type_e2ds = 'weighted mean'

#    Define order to plot                                          - [cal_drift]
ic_drift_order_plot = 20

#    Define the size of the min max smoothing box for         - [cal_drift-peak]
#        background subtraction
drift_peak_minmax_boxsize = 6

#    Define the border size (edges in x-direction) for the    - [cal_drift-peak]
#        FP fitting algorithm
drift_peak_border_size = 3

#    Define the box half-size (in pixels) to fit an           - [cal_drift-peak]
#        individual FP peak to - a gaussian will be fit to +/- this size from
#        the center of the FP peak
drift_peak_fpbox_size = 3

#    Define the minimum normalised flux a FP peak must        - [cal_drift-peak]
#        have to be recognised as a FP peak (before fitting a gaussian)
# drift_peak_min_nfp_peak = 0.25

# define drift peak types, the keys should be KW_EXT_TYPE header keys
#
# noinspection PyPep8
drift_peak_allowed_types = {'FP_FP': 'fp', 'HCONE_HCONE': 'hc', 'HCTWO_HCTWO': 'hc', 'OBJ_FP': 'fp', 'DARK_FP': 'fp'}

#    Define the sigma above the median that a peak must have  - [cal_drift-peak]
#        to be recognised as a valid peak (before fitting a gaussian)
#        dictionary must have keys equal to the keys in
#        drift_peak_allowed_types
drift_peak_peak_sig_lim = {'fp': 1.0, 'hc': 7.0}

#    Define the allowed file types for the input files
#       fp/hc is based on the reference file these are which other
#       files are allowed for each input type
#        dictionary must have keys equal to the keys in
#        drift_peak_allowed_types
# noinspection PyPep8
drift_peak_allowed_output = {'fp': ['FP_FP', 'OBJ_FP', 'DARK_FP'], 'hc': ['HCONE_HCONE', 'HCTWO_HCTWO', 'OBJ_HCONE', 'OBJ_HCTWO']}

#    Define fibers which these can be used on
drift_peak_output_except = {'OBJ_FP': 'C', 'OBJ_HCONE': 'C', 'OBJ_HCTWO': 'C'}

#    Define the minimum spacing between peaks in order to be  - [cal_drift-peak]
#        recognised as a valid peak (before fitting a gaussian)
drift_peak_inter_peak_spacing = 5

#    Define the expected width of FP peaks - used to          - [cal_drift-peak]
#        "normalise" peaks (which are then subsequently removed
#        if > drift_peak_norm_width_cut
drift_peak_exp_width = 0.9  # 0.8

#    Define the "normalised" width of FP peaks that is too    - [cal_drift-peak]
#        large normalised width = FP FWHM - drift_peak_exp_width
#        cut is essentially:
#           FP FWHM < (drift_peak_exp_width + drift_peak_norm_width_cut)
drift_peak_norm_width_cut = 0.25  # 0.2

#    Define whether to fit a gaussain (slow) or adjust a      - [cal_drift-peak]
#        barycenter to get the drift
drift_peak_getdrift_gaussfit = False

#    Define the minimum Pearson R coefficient allowed in a    - [cal_drift-peak]
#        file to obtain drifts from that order
drift_peak_pearsonr_cut = 0.9

#    Define the sigma for the sigma clip of found FP peaks    - [cal_drift-peak]
drift_peak_sigmaclip = 1.0

#    Define whether we plot the linelist vs amplitude         - [cal_drift-peak]
drift_peak_plot_line_log_amp = False

#    Define which peak to plot in the linelist vs amp plot    - [cal_drift-peak]
drift_peak_selected_order = 30

#    Define which mask to use                                  - [cal_drift-ccf]
drift_ccf_mask = 'fp.mas'

#    Define the drift target RV to use                         - [cal_drift-ccf]
drift_target_rv = 0.0

#    Define the drift CCF width to use                         - [cal_drift-ccf]
drift_ccf_width = 7.5

#    Define the drift CCF step to use                          - [cal_drift-ccf]
drift_ccf_step = 0.5


# -----------------------------------------------------------------------------
#  cal_BADPIX parameters
# -----------------------------------------------------------------------------

#   Define the median image in the x dimension over a             - [cal_badpix]
#       boxcar of this width (formally wmed)
badpix_flat_med_wid = 7

#   Define the illumination cut parameter                         - [cal_badpix]
#       (formally illum_cut)
badpix_illum_cut = 0.05

#   Define the maximum differential pixel cut ratio               - [cal_badpix]
#       (formally cut_ratio)
badpix_flat_cut_ratio = 0.5

#   Define the maximum flux in ADU/s to be considered too         - [cal_badpix]
#       hot to be used (formally max_hotpix)
badpix_max_hotpix = 5  # same as dark_cutlimit !!!

#   Percentile to normalise to when normalising and median        - [cal_badpix]
#      filtering image [percentage]
badpix_norm_percentile = 90.0

#   Defines the full detector flat file (located in the data      - [cal_badpix]
#      folder)
badpix_full_flat = 'detector_flat_full.fits'

#   Defines the threshold on the full detector flat file to       - [cal_badpix]
#      deem pixels as good
badpix_full_threshold = 0.3


# -----------------------------------------------------------------------------
#  cal_CCF_E2DS_spirou
# -----------------------------------------------------------------------------

#  Define the width of the CCF range                                 - [cal_CCF]
ic_ccf_width = 30.0

#  Define the computations steps of the CCF                          - [cal_CCF]
ic_ccf_step = 0.5

#  Define the weight of the CCF mask                                 - [cal_CCF]
#     (if 1 force all weights equal)
ic_w_mask_min = 0.0

#  Define the width of the template line                             - [cal_CCF]
#     (if 0 use natural)
ic_mask_width = 1.7

#  Define the barycentric Earth RV (berv)                            - [cal_CCF]
ccf_berv = 0.0

#  Define the maximum barycentric Earth RV                           - [cal_CCF]
ccf_berv_max = 0.0

#  Define the detector noise to use in the ccf                       - [cal_CCF]
ccf_det_noise = 100.0

#  Define the type of fit for the CCF fit                            - [cal_CCF]
ccf_fit_type = 0

#  Define the number of orders (from zero to ccf_num_orders_max)     - [cal_CCF]
#      to use to calculate the CCF and RV
ccf_num_orders_max = 48

#  Define the mode to work out the Earth Velocity       - [cal_extract, cal_CCF]
#     correction calculation
#      Options are:
#           - "off" - berv is set to zero
#           - "old" - berv is calculated with FORTRAN newbervmain.f
#             WARNING: requires newbervmain.f to be compiled
#                      with f2py -c -m newbervmain --noopt --quiet newbervmain.f
#                      located in the SpirouDRS/fortran directory
#           - "new" - berv is calculated using barycorrpy  but needs to be
#                     installed (i.e. pip install barycorrpy)
#                     CURRENTLY NOT WORKING!!!
bervmode = "new"

# -----------------------------------------------------------------------------
#   cal_exposure_meter parameters
# -----------------------------------------------------------------------------

#  Define which fiber to extract                                      - [cal_em]
#     One of AB, A, B, or C
em_fib_type = 'AB'

#  Define the telluric threshold (transmission) to mask at            - [cal_em]
em_tell_threshold = 0.95

#  Define the minimum wavelength (in nm) to mask at                   - [cal_em]
em_min_lambda = 1478.7

#  Define the maximum wavelength (in nmm) to mask at                  - [cal_em]
em_max_lambda = 1823.1

#  Define what size we want the mask                                  - [cal_em]
#      options are:
#           - "raw" (4096 x 4096)
#           - "drs" flipped in x and y and resized by
#                (ic_ccdx_low, ic_ccdx_high, ic_ccdy_low, ic_ccdy_high
#           - "pre-process" (4096 x 4096) and rotated from raw
#           - "all" - all of the above
em_output_type = "all"

#  Define whether to combine with bad pixel mask or not               - [cal_em]
#     if True badpixel mask is combined if False it is not
em_combined_badpix = True

#  Define whether to just save wavelength map                         - [cal_em]
em_save_wave_map = True

#  Define whether to save the telluric spectrum                       - [cal_em]
em_save_tell_spec = True

#  Define whether to save the exposure meter mask                     - [cal_em]
em_save_mask_map = True

#  Define whether to normalise the flux                      - [cal_wave_mapper]
em_norm_flux = False

#  Define whether to multiple by flat                        - [cal_wave_mapper]
em_flat_correction = True

# -----------------------------------------------------------------------------
#   cal_hc/cal_wave parameters
# -----------------------------------------------------------------------------
#  Define the lamp types                                    - [cal_HC, cal_wave]
#      these must be present in the the following dictionaries to
#      be used
#                  - ic_ll_line_file
#                  - ic_cat_type
#      values must be a list of strings to look for in filenames
ic_lamps = {'UNe': ['hcone', 'hc1'], 'TH': ['hctwo', 'hc2']}

#  Define the catalogue line list to use for each           - [cal_HC, cal_wave]
#       lamp type (dictionary)
ic_ll_line_file_all = {'UNe': 'catalogue_UNe.dat', 'TH': 'catalogue_ThAr.dat'}

#  Define the type of catalogue to use for each lamp type   - [cal_HC, cal_wave]
ic_cat_type_all = {'UNe': 'fullcat', 'TH': 'thcat'}

#  Define the Resolution of detector                        - [cal_HC, cal_wave]
ic_resol = 65000

#  Define wavelength free span parameter in find            - [cal_HC, cal_wave]
#      lines search
# default = 3   or 2.6
ic_ll_free_span = [6., 3.5]

#  Define minimum wavelength of the detector to use in      - [cal_HC, cal_wave]
#     find lines
ic_ll_sp_min = 900

#  Define maximum wavelength of the detector to use in      - [cal_HC, cal_wave]
#     find lines
ic_ll_sp_max = 2400

#  Define the read out noise to use in find lines           - [cal_HC, cal_wave]
# default = 16.8
ic_hc_noise = 60  # 30

# Maximum sig-fit of the guessed lines                      - [cal_HC, cal_wave]
#     fwhm/2.35 of th lines)
ic_max_sigll_cal_lines = 4  # 5.2

# Maximum error on first guess lines                        - [cal_HC, cal_wave]
# default = 1
ic_max_errw_onfit = 1  # 1

# Maximum amplitude of the guessed lines                    - [cal_HC, cal_wave]
# default = 2.0e5
ic_max_ampl_line = 1.0e8

#  Defines order to which the solution is calculated        - [cal_HC, cal_wave]
#      previously called n_ord_final
ic_hc_n_ord_start = 13  # 13

#  Defines order to which the solution is calculated        - [cal_HC, cal_wave]
#      previously called n_ord_final
ic_hc_n_ord_final = 40  # 40

#  Defines echelle of first extracted order                 - [cal_HC, cal_wave]
ic_hc_t_order_start = 79

# Define the minimum instrumental error                     - [cal_HC, cal_wave]
ic_errx_min = 0.01  # 0.03

#  Define the wavelength fit polynomial order               - [cal_HC, cal_wave]
# default = 5
ic_ll_degr_fit = 4  # 5   #4  # 4

#  Define the max rms for the wavelength sigma-clip fit     - [cal_HC, cal_wave]
ic_max_llfit_rms = 3.0

#  Define the fit polynomial order for the Littrow fit      - [cal_HC, cal_wave]
#      (fit across the orders)
ic_Littrow_fit_deg_1 = 5  # 5  # 4
ic_Littrow_fit_deg_2 = 8  # 4

#  Define the littrow cut steps                             - [cal_HC, cal_wave]
ic_Littrow_cut_step_1 = 250
ic_Littrow_cut_step_2 = 500

#  Define the order to start the Littrow fit from           - [cal_HC, cal_wave]
ic_Littrow_order_init_1 = 0
ic_Littrow_order_init_2 = 1

#  Define the order to end the Littrow fit at	            - [cal_HC, cal_wave]
ic_Littrow_order_final_1 = 46
ic_Littrow_order_final_2 = 47

#  Define orders to ignore in Littrow fit                   - [cal_HC, cal_wave]
ic_Littrow_remove_orders = []

#  Define the order fit for the Littrow solution            - [cal_HC, cal_wave]
#      (fit along the orders)
# TODO needs to be the same as ic_ll_degr_fit
ic_Littrow_order_fit_deg = 4  # 5  # 4

#  Define wavelength free span parameter in find            - [cal_HC, cal_wave]
#    lines search (used AFTER littrow fit) default = 3
ic_ll_free_span_2 = [4.25, 3.0]  # 2.6

#  Defines order from which the solution is calculated      - [cal_HC, cal_wave]
#      previously called n_ord_start (used AFTER littrow fit)
ic_hc_n_ord_start_2 = 0  # 5  #0

#  Defines order to which the solution is calculated        - [cal_HC, cal_wave]
#      previously called n_ord_final (used AFTER littrow fit)
ic_hc_n_ord_final_2 = 46  # 40    #46

#  Defines the mode to "find_lines"                         - [cal_HC, cal_wave]
#      Currently allowed modes are:
#          0: Fortran "fitgaus" routine (requires SpirouDRS.fortran.figgaus.f
#             to be compiled using f2py:
#                 f2py -c -m fitgaus --noopt --quiet fitgaus.f
#          1: Python fit using scipy.optimize.curve_fit
#          2: Python fit using lmfit.models (Model, GaussianModel) - requires
#              lmfit python module to be installed (pip install lmfit)
#          3: Python (conversion of Fortran "fitgaus") - direct fortran gaussj
#          4: Python (conversion of Fortran "fitgaus") - gaussj Melissa
#          5: Python (conversion of Fortran "fitgaus") - gaussj Neil
# hc_find_lines_mode = 0

#  Define first order FP solution is calculated from                - [cal_wave]
ic_fp_n_ord_start = 0  # 0   # 9

#  Defines last order FP solution is calculated to                  - [cal_wave]
ic_fp_n_ord_final = 47  # 47   # 45

#  Define the size of region where each line is fitted               -[cal_wave]
ic_fp_size = 3

#  Define the threshold to use in detecting the positions            -[cal_wave]
#      of FP peaks
ic_fp_threshold = 0.3  # 0.2

#  Define the initial value of FP effective cavity width            - [cal_wave]
#   2xd = 24.5 mm = 24.5e6 nm  for SPIRou
ic_fp_dopd0 = 2.44999e7  # 2.45e7

#  Define the polynomial fit degree between FP line numbers and     - [cal_wave]
#      the measured cavity width for each line
ic_fp_fit_degree = 9

#  Define the FP jump size that is too large                        - [cal_wave]
ic_fp_large_jump = 0.5

#  Define the plot order for the comparison between spe and speref  - [cal_wave]
ic_wave_idrift_plot_order = 14

#  Define the noise to use in the instrument drift calculation      - [cal_wave]
ic_wave_idrift_noise = 50.0

#   The maximum flux for a good (unsaturated) pixel                 - [cal_wave]
ic_wave_idrift_maxflux = 350000

#   The size around a saturated pixel to flag as unusable           - [cal_wave]
ic_wave_idrift_boxsize = 12

#   Define the number of standard deviations cut at in              - [cal_wave]
#       cosmic renormalisation (for instrumental drift calculation)
ic_wave_idrift_cut_e2ds = 4.5

#  Define the maximum uncertainty allowed on the RV                 - [cal_wave]
#      (for instrumental drift calculation)
ic_wave_idrift_max_err = 3.0

#  Define the RV cut above which the RV from orders are not used    - [cal_wave]
#      (for instrumental drift calculation)
ic_wave_idrift_rv_cut = 20.0

# Define intercept and slope for a pixel shift              - [cal_HC, cal_wave]
# pixel_shift_inter = 6.26637214e+00
# pixel_shift_slope = 4.22131253e-04
pixel_shift_inter = 0.0
pixel_shift_slope = 0.0

# force reading the wave solution from calibDB              - [cal_HC, cal_wave]
calib_db_force_wavesol = False

# Define whether to use FP in cal_WAVE solution                     - [cal_wave]
ic_wave_use_fp = True

# -----------------------------------------------------------------------------
#   cal_hc/cal_wave parameters
# -----------------------------------------------------------------------------
# Whether to force the linelist to be created (or re-created)         - [cal_HC]
HC_EA_FORCE_CREATE_LINELIST = False
# whether to do plot per order (very slow + interactive)              - [cal_HC]
HC_EA_PLOT_PER_ORDER = False
# width of the box for fitting HC lines. Lines will be fitted         - [cal_HC]
#     from -W to +W, so a 2*W+1 window
HC_FITTING_BOX_SIZE = 6
# number of sigma above local RMS for a line to be flagged as such    - [cal_HC]
HC_FITTING_BOX_SIGMA = 2.0
# the fit degree for the gaussian fit
HC_FITTING_BOX_GFIT_TYPE = 5
# the RMS of line-fitted line must be before 0 and 0.2 of the         - [cal_HC]
#     peak value must be SNR>5 (or 1/SNR<0.2)
HC_FITTINGBOX_RMS_DEVMIN = 0
HC_FITTINGBOX_RMS_DEVMAX = 0.2
# the e-width of the line expressed in pixels.                        - [cal_HC]
HC_FITTINGBOX_EW_MIN = 0.7
HC_FITTINGBOX_EW_MAX = 1.1
# number of bright lines kept per order                               - [cal_HC]
#     avoid >25 as it takes super long
#     avoid <12 as some orders are ill-defined and we need >10 valid
#         lines anyway
#     20 is a good number, and I see no reason to change it
HC_NMAX_BRIGHT = 20
# Number of times to run the fit triplet algorithm                    - [cal_HC]
HC_NITER_FIT_TRIPLET = 3
# Maximum distance between catalog line and init guess line           - [cal_HC]
#    to accept line in m/s
HC_MAX_DV_CAT_GUESS = 60000
# The fit degree between triplets                                     - [cal_HC]
HC_TFIT_DEG = 2
# Cut threshold for the triplet line fit [in km/s]                    - [cal_HC]
HC_TFIT_CUT_THRES = 1.0
# Minimum number of lines required per order                          - [cal_HC]
HC_TFIT_MIN_NUM_LINES = 10
# Minimum total number of lines required                              - [cal_HC]
HC_TFIT_MIN_TOT_LINES = 200

# Define the distance in m/s away from the center of dv hist          - [cal_HC]
#      points outside will be rejected [m/s]
HC_TFIT_DVCUT_ORDER = 2000
HC_TFIT_DVCUT_ALL = 5000

# this sets the order of the polynomial used to ensure continuity     - [cal_HC]
#     in the  xpix vs wave solutions by setting the first term = 12,
#     we force that the zeroth element of the xpix of the wavelegnth
#     grid is fitted with a 12th order polynomial as a function of
#     order number
HC_TFIT_ORDER_FIT_CONTINUITY = [12, 9, 6, 2, 2]
# Number of times to loop through the sigma clip                      - [cal_HC]
HC_TFIT_SIGCLIP_NUM = 20
# Sigma clip threshold
HC_TFIT_SIGCLIP_THRES = 3.5
# quality control criteria if sigma greater than this                 - [cal_HC]
# many sigma fails
QC_HC_WAVE_SIGMA_MAX = 8
# resolution and line profile map size (y-axis by x-axis)             - [cal_HC]
HC_RESMAP_SIZE = [5, 4]
# The maximum allowed deviation in the RMS line spread function       - [cal_HC]
HC_RES_MAXDEV_THRES = 8
# The line profile dv plot range (+range and -range) in km/s          - [cal_HC]
HC_RESMAP_DV_SPAN = [-15, 15]
# the line profile x limits                                           - [cal_HC]
HC_RESMAP_PLOT_XLIM = [-8, 8]
# the line profile y limits                                           - [cal_HC]
HC_RESMAP_PLOT_YLIM = [-0.05, 0.7]
# index of FP line to start order cross-matching from               - [cal_wave]
ic_wave_fp_cm_ind = -2
# order to plot HC + fitted lines                                     - [cal_HC]
ic_wave_ea_plot_order = 7

# -----------------------------------------------------------------------------
#  Telluric parameters
# -----------------------------------------------------------------------------
tellu_fiber = 'AB'

tellu_suffix = 'e2dsff'

tellu_blaze_percentile = 95

# Define level above which the blaze is high enough to          - [obj_mk_tellu]
#     accurately measure telluric
tellu_cut_blaze_norm = 0.2

# Define mean line width expressed in pix
fwhm_pixel_lsf = 2.1

# Define list of absorbers in the tapas fits table
tellu_absorbers = ['combined', 'h2o', 'o3', 'n2o', 'o2', 'co2', 'ch4']

# Define whether to fit the derivatives instead of the          - [obj_mk_tellu]
#     principal components
fit_deriv_pc = False

# Define whether to add the first derivative and broadening     - [obj_mk_tellu]
#     factor to the principal components this allows a variable
#     resolution and velocity offset of the PCs this is performed
#     in the pixel space and NOT the velocity space as this is
#     should be due to an instrument shift
add_deriv_pc = True

# Define min transmission in tapas models to consider an        - [obj_mk_tellu]
#     element part of continuum
transmission_cut = 0.98

# Define the number of iterations to find the SED of hot        - [obj_mk_tellu]
# stars + sigma clipping
n_iter_sed_hotstar = 5

# Define the smoothing parameter for the interpolation of       - [obj_mk_tellu]
#     the hot star continuum. Needs to be reasonably matched
#     to the true width
tellu_vsini = 250.0

# Define the median sampling expressed in km/s / pix
tellu_med_sampling = 2.2

# TODO: Need comments
tellu_sigma_dev = 5
tellu_bad_threshold = 1.2
tellu_nan_threshold = 0.2
tellu_abso_maps = False
tellu_abso_low_thres = 0.01
tellu_abso_high_thres = 1.05
tellu_abso_sig_n_iter = 5
tellu_abso_sig_thres = -1
tellu_abso_dv_order = 33
tellu_abso_dv_size = 5
tellu_abso_dv_good_thres = 0.2

# TODO: Need comments
tellu_template_keep_limit = 0.5
tellu_template_med_low = 2048 - 128
tellu_template_med_high = 2048 + 128

# TODO: Need comments
tellu_number_of_principle_comp = 5
tellu_fit_keep_frac = 20.0
tellu_plot_order = 35
tellu_fit_min_transmission = 0.2
tellu_lambda_min = 1000.0
tellu_lambda_max = 2100.0
tellu_fit_vsini = 15.0
tellu_fit_niter = 4
tellu_fit_vsini2 = 30.0
tellu_fit_log_limit = -0.5

# Defines the order to plot the reconstructed absorption for
#    Note this can be a number or 'all' to display all orders
tellu_fit_recon_plt_order = 33    # 'all'    # 33

# -----------------------------------------------------------------------------
#  New make telluric parameter
# -----------------------------------------------------------------------------
# value below which the blaze in considered too low to be useful
#     for all blaze profiles, we normalize to the 95th percentile.
#     That's pretty much the peak value, but it is resistent to
#     eventual outliers
MKTELLU_CUT_BLAZE_NORM = 0.1
MKTELLU_BLAZE_PERCENTILE = 95

# define the default convolution width [in pixels]
MKTELLU_DEFAULT_CONV_WIDTH = 900
# define the finer convolution width [in pixels]
MKTELLU_FINER_CONV_WIDTH = 100
# define which orders are clean enough of tellurics to use the finer
#     convolution width
MKTELLU_CLEAN_ORDERS = [2, 3, 5, 6, 7, 8, 9, 14, 15, 19, 20, 28, 29, 30, 31, 32, 33, 34, 35, 43, 44]

# median-filter the template. we know that stellar features
#    are very broad. this avoids having spurious noise in our
#    templates [pixel]
MKTELLU_TEMPLATE_MED_FILTER = 15

# Set an upper limit for the allowed line-of-sight optical depth of water
MKTELLU_TAU_WATER_ULIMIT = 99

# set a lower and upper limit for the allowed line-of-sight optical depth
#    for other absorbers (upper limit equivalent to airmass limit)
# line-of-sight optical depth for other absorbers cannot be less than one
#      (that's zenith) keep the limit at 0.2 just so that the value gets
#      propagated to header and leaves open the possibility that during
#      the convergence of the algorithm, values go slightly below 1.0
MKTELLU_TAU_OTHER_LLIMIT = 0.2
# line-of-sight optical depth for other absorbers cannot be greater than 5
# ... that would be an airmass of 5 and SPIRou cannot observe there
MKTELLU_TAU_OTHER_ULIMIT = 5.0

# bad values and small values are set to this value (as a lower limit to
#   avoid dividing by small numbers or zero
MKTELLU_SMALL_LIMIT = 1.0e-9

# threshold in absorbance where we will stop iterating the absorption
#     model fit
MKTELLU_DPARAM_THRES = 0.001

# max number of iterations, normally converges in about 12 iterations
MKTELLU_MAX_ITER = 50

# minimum transmission required for use of a given pixel in the TAPAS
#    and SED fitting
MKTELLU_THRES_TRANSFIT = 0.3

# Defines the bad pixels if the spectrum is larger than this value.
#    These values are likely an OH line or a cosmic ray
MKTELLU_TRANS_FIT_UPPER_BAD = 1.1

# Defines the minimum allowed value for the recovered water vapor optical
#    depth (should not be able 1)
MKTELLU_TRANS_MIN_WATERCOL = 0.2

# Defines the maximum allowed value for the recovered water vapor optical
#    depth
MKTELLU_TRANS_MAX_WATERCOL = 99

# Defines the minimum number of good points required to normalise the
#    spectrum, if less than this we don't normalise the spectrum by its
#    median
MKTELLU_TRANS_MIN_NUM_GOOD = 100

# Defines the percentile used to gauge which transmission points should
#    be used to median (above this percentile is used to median)
MKTELLU_TRANS_TAU_PERCENTILE = 95

# sigma-clipping of the residuals of the difference between the
# spectrum divided by the fitted TAPAS absorption and the
# best guess of the SED
MKTELLU_TRANS_SIGMA_CLIP = 20.0

# median-filter the trans data measured in pixels
MKTELLU_TRANS_TEMPLATE_MEDFILT = 31

# Define the median sampling expressed in km/s / pix
MKTELLU_MED_SAMPLING = 2.2

# Define the threshold for "small" values that do not add to the weighting
MKTELLU_SMALL_WEIGHTING_ERROR = 0.01

# Define the allowed difference between recovered and input airmass
QC_MKTELLU_AIRMASS_DIFF = 0.1

# Define the orders to plot (not too many) - but can put 'all' to show all
#    'all' are shown one-by-one and then closed (in non-interactive mode)
MKTELLU_PLOT_ORDER_NUMS = [19, 26, 35]
# MKTELLU_PLOT_ORDER_NUMS = 'all'


# -----------------------------------------------------------------------------
#  make telluric db parameter
# -----------------------------------------------------------------------------
# Allowed data types (corresponding to header key defined by "KW_OUTPUT")
TELLU_DB_ALLOWED_OUTPUT = ['EXT_E2DS_AB', 'EXT_E2DS_A', 'EXT_E2DS_B', 'EXT_E2DS_FF_AB', 'EXT_E2DS_FF_A', 'EXT_E2DS_FF_B']

# Allowed data types (corresponding to header key defined by "KW_EXT_TYPE")
TELLU_DB_ALLOWED_EXT_TYPE = ['OBJ_DARK', 'OBJ_FP']

# -----------------------------------------------------------------------------
#   polarimetry parameters
# -----------------------------------------------------------------------------
#  Define all possible stokes parameters                          - [pol_spirou]
ic_polar_stokes_params = ['V', 'Q', 'U']

#  Define all possible fibers used for polarimetry                - [pol_spirou]
ic_polar_fibers = ['A', 'B']

#  Define the polarimetry method                                  - [pol_spirou]
#    currently must be either:
#         - Ratio
#         - Difference
ic_polar_method = 'Ratio'

#  Define the polarimetry continuum bin size (for plotting)       - [pol_spirou]
ic_polar_cont_binsize = 1000

#  Define the polarimetry continuum overlap size (for plotting)   - [pol_spirou]
ic_polar_cont_overlap = 0

#  Define the telluric mask for calculation of continnum          - [pol_spirou]
# noinspection PyPep8
ic_polar_cont_tellmask = [[930, 967], [1109, 1167], [1326, 1491], [1782, 1979], [1997, 2027], [2047, 2076]]

# Remove continuum polarization (True = 1, False = 0)
ic_polar_remove_continuum = 1

#  Perform LSD analysis (True = 1, False = 0)                     - [pol_spirou]
ic_polar_lsd_analysis = 1

#  Define initial velocity (km/s) for output LSD profile          - [pol_spirou]
ic_polar_lsd_v0 = -150.

#  Define final velocity (km/s) for output LSD profile            - [pol_spirou]
ic_polar_lsd_vf = 150.

#  Define number of points for output LSD profile                 - [pol_spirou]
ic_polar_lsd_np = 201

#  Define files with spectral lines for LSD analysis              - [pol_spirou]
# noinspection PyPep8
ic_polar_lsd_ccflines = ['marcs_t2500g50_all', 'marcs_t3000g50_all', 'marcs_t3500g50_all']

#  Define mask for selecting lines to be used in the LSD analysis - [pol_spirou]
# noinspection PyPep8
ic_polar_lsd_wlranges = [[983., 1116.], [1163., 1260.], [1280., 1331.], [1490., 1790.], [1975., 1995.], [2030., 2047.5]]

#  Define minimum line depth to be used in the LSD analyis        - [pol_spirou]
ic_polar_lsd_min_linedepth = 0.175

# Normalize Stokes I spectrum before LSD analysis (True = 1, False = 0)
ic_polar_lsd_normalize = 1

# Definitions of output LSD data 
# noinspection PyPep8
ic_polar_lsd_datainfo = ['LSD_VELOCITIES', 'LSD_STOKESI', 'LSD_STOKESI_MODEL', 'LSD_STOKESVQU', 'LSD_NULL']

# -----------------------------------------------------------------------------
#  Quality control settings
# -----------------------------------------------------------------------------

#   Max dark median level [ADU/s]                                   - [cal_dark]
qc_max_darklevel = 0.07  # 0.07

#   Max fraction of dead pixels                                     - [cal_dark]
qc_max_dead = 1.0

#   Max fraction of dark pixels (percent)                           - [cal_dark]
qc_max_dark = 1.0

#   Min dark exposure time                                          - [cal_dark]
qc_dark_time = 1.0

#   Maximum points removed in location fit                           - [cal_loc]
qc_loc_maxlocfit_removed_ctr = 1500

#   Maximum points removed in width fit                              - [cal_loc]
qc_loc_maxlocfit_removed_wid = 105

#   Maximum rms allowed in fitting location                          - [cal_loc]
qc_loc_rmsmax_center = 100

#   Maximum rms allowed in fitting width                             - [cal_loc]
qc_loc_rmsmax_fwhm = 500

#   Maximum allowed RMS of flat field                                 - [cal_ff]
qc_ff_rms = 0.05  # 0.14

#   Saturation level reached warning                                  - [cal_ff]
qc_loc_flumax = 50000

#   Maximum allowed RMS allowed for the RMS of the tilt             - [cal_slit]
#        for the slit
qc_slit_rms = 0.1

#   Minimum allowed angle for the tilt of the slit [deg]            - [cal_slit]
qc_slit_min = -10.0

#   Maximum allowed angle for the tilt of the slit [deg]            - [cal_slit]
qc_slit_max = 0.0

#   Maximum signal allowed (set saturation limit)                - [cal_extract]
#        however currently does not trigger qc
qc_max_signal = 50000

#   Maximum littrow RMS value for cal_hc                    - [cal_HC, cal_wave]
#       (at x cut points)
qc_hc_rms_littrow_max = 0.15  # 0.3

#   Maximum littrow Deviation from wave solution for       - [cal_HC, cal_wave]
#        cal_wave (at x cut points)
qc_hc_dev_littrow_max = 0.4  # 0.9

#   Maximum littrow RMS value for cal_hc                    - [cal_HC, cal_wave]
#       (at x cut points)
qc_wave_rms_littrow_max = 0.1

#   Maximum littrow Deviation from wave solution for       - [cal_HC, cal_wave]
#       cal_wave (at x cut points)
qc_wave_dev_littrow_max = 0.3

#   Define the maximum number of orders to remove from RV            -[cal_wave]
#       calculation (for instrumental drift calculation)
qc_wave_idrift_nborderout = 15

#   Define the maximum allowed drift (in m/s) in the                 -[cal_wave]
#       instrumental drift calculation
qc_wave_idrift_rv_max = 150.0

#   Define the order to use for SNR check when accepting tellu   -[obj_mk_tellu]
#      files to the telluDB
qc_mk_tellu_snr_order = 33

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER"         -[obj_mk_tellu]
#      that will be accepted to the telluDB
qc_mk_tellu_snr_min = 100

#   Define the order to use for SNR check when accepting tellu   -[obj_mk_tellu]
#      files to the telluDB
qc_fit_tellu_snr_order = 33

#  Define the minimum SNR for order "QC_TELLU_SNR_ORDER"         -[obj_mk_tellu]
#      that will be accepted to the telluDB
qc_fit_tellu_snr_min = 10

#  Define the maximum RMS around 1 for domain clean from         -[obj_mk_tellu]
#     tellurics according to TAPAS
qc_tellu_clean_rms_max = 0.01



# -----------------------------------------------------------------------------
#  DB settings
# -----------------------------------------------------------------------------
#   the maximum wait time for calibration database file to be            - [all]
#       in use (locked) after which an error is raised (in seconds)
db_max_wait = 600

# file max wait
fitsopen_max_wait = 3600

# -----------------------------------------------------------------------------
#  Calibration DB settings
# -----------------------------------------------------------------------------

#   Define calibd DB master filename                                     - [all]
#      (formally ic_calib_db_master_file)
ic_calibDB_filename = 'master_calib_SPIROU.txt'

#   Define the match type for calibDB files                              - [all]
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         calibDB file will be used
calib_db_match = 'closest'

# -----------------------------------------------------------------------------
#  Telluric DB settings
# -----------------------------------------------------------------------------

#   Define tellu DB master filename                                     - [all]
#      (formally ic_tellu_db_master_file)
ic_telluDB_filename = 'master_tellu_SPIROU.txt'

#   Define the match type for telluDB files                              - [all]
#         match = 'older'  when more than one file for each key will
#                          select the newest file that is OLDER than
#                          time in fitsfilename
#         match = 'closest'  when more than on efile for each key will
#                            select the file that is closest to time in
#                            fitsfilename
#    if two files match with keys and time the key lower in the
#         telluDB file will be used
tellu_db_match = 'closest'

# -----------------------------------------------------------------------------
#  End of constants file
# -----------------------------------------------------------------------------
