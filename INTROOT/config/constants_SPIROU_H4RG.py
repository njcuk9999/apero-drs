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

# detector type (from switching between H2RG and H4RG)
ic_image_type = "H4RG"

#    Interval between plots (for certain interactive graphs)         - [cal_loc]
#       formally ic_disptimeout
ic_display_timeout = 0.5

# -----------------------------------------------------------------------------
#  image variables
# -----------------------------------------------------------------------------

#   Resize blue window                                              - [cal_dark]
ic_ccdx_blue_low = 500
ic_ccdx_blue_high = 3500
ic_ccdy_blue_low = 2000
ic_ccdy_blue_high = 3500

#   Resize red window                                               - [cal_dark]
ic_ccdx_red_low = 100
ic_ccdx_red_high = 4000
ic_ccdy_red_low = 780
ic_ccdy_red_high = 1200

#   Resize image                                                     - [cal_loc]
ic_ccdx_low = 4
ic_ccdx_high = 4092
ic_ccdy_low = 250 # 100 #4
ic_ccdy_high = 3350 #3450

#    Define the types of fiber to look for            - [cal_extract, cal_drift]
#       (earlier in list takes priority)
fiber_types = ['AB', 'A', 'B', 'C']

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
ic_ext_range1_fpall = {'AB': 14.5, 'A': 0.0, 'B': 14.5, 'C': 7.}

#   Half-zone extraction width right side (formally plage2)           - [cal_ff]
ic_ext_range2_fpall = {'AB': 14.5, 'A': 14.5, 'B': 0.0, 'C': 7.}

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
loc_box_size = 5  # 10

#   row number of image to start processing at                       - [cal_loc]
ic_offset = 0 #40

#   Definition of the central column                       - [cal_loc, cal_slit]
#      (formally ic_ccdcolc)
ic_cent_col = 2500

#   Definition of the extraction window size (half size)             - [cal_loc]
ic_ext_window = 15  #20 #40 #12

#   Definition of the gap index in the selected area                 - [cal_loc]
#       (formally ic_ccdgap)
ic_image_gap = 0

#   Define the column separation for fitting orders                  - [cal_loc]
ic_locstepc = 20 # 20

#   Define minimum width of order to be accepted                     - [cal_loc]
ic_widthmin = 10 # 5

#   Define the noise multiplier threshold in order to accept an      - [cal_loc]
#       order center as usable
#       max(pixel value) - min(pixel value) > ic_noise_mult_thres * sigdet
ic_noise_mult_thres =  10  #10 # 100.0

#   Define the polynomial fit parameters for interpolating over the  - [cal_loc]
#      bad regions (holes) before localization is done
bad_region_fit = [3.19884964e-05,  -1.08289228e-01,   2.16643659e+03]

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
ic_locnbpix = 45  #45

#   Minimum amplitude to accept (in e-)                              - [cal_loc]
ic_min_amplitude = 10 # 50

#   Normalised amplitude threshold to accept pixels                  - [cal_loc]
#       for background calculation
ic_locseuil = 0.18

#   Saturation threshold on order profile plot                       - [cal_loc]
ic_satseuil = 1000 # 64536

#   Order of polynomial to fit for positions                         - [cal_loc]
ic_locdfitc = 4 #5

#   Order of polynomial to fit for widths                            - [cal_loc]
ic_locdfitw = 4 #5

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
#   cal_slit parameters
# -----------------------------------------------------------------------------

#   oversampling factor (for tilt finding)
ic_tilt_coi = 10

#   Offset multiplicative factor (for width)                        - [cal_slit]
ic_facdec =  0.9 # 1.6

#   Order of polynomial to fit for tilt                             - [cal_slit]
ic_tilt_fit = 4

#   Order to plot on slit image plot                                - [cal_slit]
ic_slit_order_plot = 20 * 2

# -----------------------------------------------------------------------------
#   cal_ff parameters
# -----------------------------------------------------------------------------

#    Do background measurement (True = 1, False = 0)                  - [cal_ff]
ic_do_bkgr_subtraction = 0

#    Half-size of window for background measurements                  - [cal_ff]
ic_bkgr_window = 100

#    Number of orders in tilt file (formally nbo)                     - [cal_ff]
ic_tilt_nbo = 49  #36

#    Start order of the extraction in cal_ff                          - [cal_ff]
#       if None starts from 0
ff_start_order = None

#    End order of the extraction in cal_ff                            - [cal_ff]
#       if None ends at last order
ff_end_order = None

#   Manually set the sigdet to use in weighted tilt extraction        - [cal_ff]
#       set to -1 to use from fitsfilename HEADER
#       (formally ccdsigdet)
ic_ff_sigdet = 100.0

#    Half size blaze smoothing window                                 - [cal_ff]
ic_extfblaz = 50

#    The blaze polynomial fit degree                                  - [cal_ff]
# (formally harded coded = 5)
ic_blaze_fitn = 7    # 10

#   Order to plot on ff image plot (formally ic_order_plot)           - [cal_ff]
ic_ff_order_plot = 27

#   Plot all order fits (True = 1, False = 0)                         - [cal_ff]
#        (takes slightly longer than just one example order)
ic_ff_plot_all_orders = 0

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
ic_extnbsig = 1 #2.5

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
ic_extract_type = '3d'  #'3d'
# Now select the extraction type in cal_ff ONLY                       - [cal_FF]
ic_ff_extract_type = '3c'

#   Set the number of pixels to set as                   - [cal_extract, cal_FF]
#       the border (needed to allow for tilt to not go off edge of image)
ic_ext_tilt_bord = 2

#   Set a custom noise level for extract (formally sigdet)       - [cal_extract]
#       set to -1 to use sigdet from file header
ic_ext_sigdet = -1   # 100

#    Define order to plot                                        - [cal_extract]
ic_ext_order_plot = 17

#    Define the percentage of flux above which we use    - [cal_ff, cal_extract]
#        to cut
#        ONLY USED IF EXTRACT_TYPE = '3d'
ic_cosmic_sigcut = 0.25  # 0.25

#    Defines the maximum number of iterations we use     - [cal_ff, cal_extract]
#        to check for cosmics (for each pixel)
#        ONLY USED IF EXTRACT_TYPE = '3d'
ic_cosmic_thresh = 5

# -----------------------------------------------------------------------------
#   cal_drift parameters
# -----------------------------------------------------------------------------
#   The value of the noise for drift calculation                   - [cal_drift]
#      snr = flux/sqrt(flux + noise^2)
ic_drift_noise = 100.0

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
ic_drift_n_order_max = 28

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

#    Define the sigma above the median that a peak must have  - [cal_drift-peak]
#        to be recognised as a valid peak (before fitting a gaussian)
#        dictionary must have keys equal to the lamp types (hc, fp)
drift_peak_peak_sig_lim = {'fp': 1.0, 'hc': 7.0}

#    Define the minimum spacing between peaks in order to be  - [cal_drift-peak]
#        recognised as a valid peak (before fitting a gaussian)
drift_peak_inter_peak_spacing = 5

#    Define the expected width of FP peaks - used to          - [cal_drift-peak]
#        "normalise" peaks (which are then subsequently removed
#        if > drift_peak_norm_width_cut
drift_peak_exp_width = 0.8

#    Define the "normalised" width of FP peaks that is too    - [cal_drift-peak]
#        large normalised width = FP FWHM - drift_peak_exp_width
#        cut is essentially:
#           FP FWHM < (drift_peak_exp_width + drift_peak_norm_width_cut)
drift_peak_norm_width_cut = 0.2

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
badpix_max_hotpix = 100.0

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
ccf_num_orders_max = 25

# -----------------------------------------------------------------------------
#   cal_hc parameters
# -----------------------------------------------------------------------------
#  Define the lamp types                                              - [cal_HC]
#      these must be present in the the following dictionaries to
#      be used
#                  - ic_ll_line_file
#                  - ic_cat_type
ic_lamps = {'UNe': 'hcone', 'TH': 'hctwo'}

#  Define the catalogue line list to use for each lamp type           - [cal_HC]
#      (dictionary)
ic_ll_line_file_all = {'UNe': 'catalogue_UNe.dat', 'TH': 'catalogue_ThAr.dat'}

#  Define the type of catalogue to use for each lamp type             - [cal_HC]
ic_cat_type_all = {'UNe': 'fullcat', 'TH': 'thcat'}

#
# default = 5
ic_ll_degr_fit = 4

#
ic_ll_sp_min = 900

#
ic_ll_sp_max = 2400

# Maximum amplitude of the line
# default = 2.0e5
ic_max_ampl_line = 2.0e8

#
# default = 1
ic_max_errw_infit = 1

#
# default = 50000  or 60000
ic_resol = 55000

#
# default = 3   or 2.6
ic_ll_free_span = 3

#
# default = 16.8
ic_hc_noise = 30

#  Defines order to which the solution is calculated                  - [cal_HC]
#      previously called n_ord_final
cal_hc_n_ord_final = 24

#  Defines echeele of first extracted order
cal_hc_t_order_start = 66

#
ic_ll_smooth = 0


# -----------------------------------------------------------------------------
#  Quality control settings
# -----------------------------------------------------------------------------

#   Max dark median level [ADU/s]                                   - [cal_dark]
qc_max_darklevel = 0.07

#   Max fraction of dead pixels                                     - [cal_dark]
qc_max_dead = 1.0

#   Max fraction of dark pixels (percent)                           - [cal_dark]
qc_max_dark = 1.0

#   Min dark exposure time                                          - [cal_dark]
#   TODO: This should be set to 599.0
# qc_dark_time = 599.0
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
qc_ff_rms =  5   #  0.14

#   Saturation level reached warning                                  - [cal_ff]
qc_loc_flumax = 64500

#   Maximum allowed RMS allowed for the RMS of the tilt             - [cal_slit]
#        for the slit
qc_slit_rms = 0.1

#   Minimum allowed angle for the tilt of the slit [deg]            - [cal_slit]
qc_slit_min = -10.0

#   Maximum allowed angle for the tilt of the slit [deg]            - [cal_slit]
qc_slit_max = 0.0

#   Maximum signal allowed (set saturation limit)                - [cal_extract]
#        however currently does not trigger qc
qc_max_signal = 65500

# -----------------------------------------------------------------------------
#  Calib DB settings
# -----------------------------------------------------------------------------

#   Define calibd DB master filename                                     - [all]
#      (formally ic_calib_db_master_file)
ic_calibDB_filename = 'master_calib_SPIROU.txt'

#   the maximum wait time for calibration database file to be            - [all]
#       in use (locked) after which an error is raised (in seconds)
calib_max_wait = 3600

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
#  End of constants file
# -----------------------------------------------------------------------------
