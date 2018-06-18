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
ic_image_type = "H2RG"

#    Interval between plots (for certain interactive graphs)         - [cal_loc]
#       formally ic_disptimeout
ic_display_timeout = 0.5

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
ic_ccdx_blue_low = 2048 - 200
ic_ccdx_blue_high = 2048 - 1500
ic_ccdy_blue_low = 2048 - 20
ic_ccdy_blue_high = 2048 - 350

#   Resize red window                                               - [cal_dark]
ic_ccdx_red_low = 2048 - 20
ic_ccdx_red_high = 2048 - 1750
ic_ccdy_red_low = 2048 - 1570
ic_ccdy_red_high = 2048 - 1910

#   Resize image                                                     - [cal_loc]
ic_ccdx_low = 5
ic_ccdx_high = 2040
ic_ccdy_low = 5
ic_ccdy_high = 1935

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
ic_first_order_jump_fpall = {'AB': 2, 'A': 0, 'B': 0, 'C': 0}

#   Maximum number of order to use                                   - [cal_loc]
ic_locnbmaxo_fpall = {'AB': 72, 'A': 36, 'B': 36, 'C': 36}

#   Quality control "normal" number of orders on fiber               - [cal_loc]
qc_loc_nbo_fpall = {'AB': 72, 'A': 36, 'B': 36, 'C': 36}

#   Fiber type                                                        - [cal_ff]
fib_type_fpall = {'AB': ['AB'], 'A': ['A'], 'B': ['B'], 'C': ['C']}

#   Half-zone extraction width left side (formally plage1)            - [cal_ff]
ic_ext_range1_fpall = {'AB': 14.5, 'A': 0.0, 'B': 14.5, 'C': 7.5}

#   Half-zone extraction width right side (formally plage2)           - [cal_ff]
ic_ext_range2_fpall = {'AB': 14.5, 'A': 14.5, 'B': 0.0, 'C': 7.5}

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
ic_force_preprocess = 0

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

#   Define rotation angle                                             - [cal_pp]
#       (in degrees counter-clockwise direction)
raw_to_pp_rotation = 0


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
histo_range_low = -0.5
histo_range_high = 5

#   Define a bad pixel cut limit (in ADU/s)                         - [cal_dark]
dark_cutlimit = 100.0

# -----------------------------------------------------------------------------
#   cal_loc parameters
# -----------------------------------------------------------------------------

#   Size of the order_profile smoothed box                           - [cal_loc]
#     (from pixel - size to pixel + size)
loc_box_size = 10

#   row number of image to start processing at                       - [cal_loc]
ic_offset = 40

#   Definition of the central column                       - [cal_loc, cal_slit]
#      (formally ic_ccdcolc)
ic_cent_col = 1000

#   Definition of the extraction window size (half size)             - [cal_loc]
ic_ext_window = 12

#   Definition of the gap index in the selected area                 - [cal_loc]
#       (formally ic_ccdgap)
ic_image_gap = 0

#   Define the column separation for fitting orders                  - [cal_loc]
ic_locstepc = 20

#   Define minimum width of order to be accepted                     - [cal_loc]
ic_widthmin = 5

#   Define the noise multiplier threshold in order to accept an      - [cal_loc]
#       order center as usable
#       max(pixel value) - min(pixel value) > ic_noise_mult_thres * sigdet
ic_noise_mult_thres = 100.0

#   Define the polynomial fit parameters for interpolating over the  - [cal_loc]
#      bad regions (holes) before localization is done
#      NOT USED FOR H2RG
bad_region_fit = [0.0, 0.0, 0.0]

#   Define the median_filter box size used in interpolating over the - [cal_loc]
#      bad regions (holes) before localization is done
#      NOT USED FOR H2RG
bad_region_med_size = 0

#   Define the threshold below which the image (normalised between   - [cal_loc]
#      0 and 1) should be regarded as bad. Used in interpolating over
#      the bad regions (holes) before localization is done
#      NOT USED FOR H2RG
bad_region_threshold = 0.0

#   Define the box size (kernel) for the convolution used in         - [cal_loc]
#      interpolating over the bad regions (holes) before localization
#      is done
#      NOT USED FOR H2RG
bad_region_kernel_size = 0

#   Define the median_filter box size used in interpolating over the - [cal_loc]
#      bad regions (holes) (during the convolution) before
#      localization is done
#      NOT USED FOR H2RG
bad_region_med_size2 = 0

#   Define the thresholds (of the ratio between original image and   - [cal_loc]
#      the normalised image) where pixels are deem "good" and "bad".
#      For use in interpolating over the bad regions (holes) before
#      localization is done
#      NOT USED FOR H2RG
bad_region_good_value = 0.0
bad_region_bad_value = 0.0

#   Half spacing between orders                                      - [cal_loc]
ic_locnbpix = 45

#   Minimum amplitude to accept (in e-)                              - [cal_loc]
ic_min_amplitude = 100

#   Normalised amplitude threshold to accept pixels                  - [cal_loc]
#       for background calculation
ic_locseuil = 0.2

#   Saturation threshold on order profile plot                       - [cal_loc]
ic_satseuil = 64536

#   Order of polynomial to fit for positions                         - [cal_loc]
ic_locdfitc = 5

#   Order of polynomial to fit for widths                            - [cal_loc]
ic_locdfitw = 5

#   Order of polynomial to fit for position error             - [spirouKeywords]
#      Currently not used
ic_locdfitp = 3

#   Maximum rms for sigma-clip order fit (center positions)          - [cal_loc]
ic_max_rms_center = 0.2

#   Maximum peak-to-peak for sigma-clip order fit                    - [cal_loc]
#      (center positions)
ic_max_ptp_center = 0.200

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
ic_facdec = 1.6

#   Order of polynomial to fit for tilt                             - [cal_slit]
ic_tilt_fit = 4

#   Order to plot on slit image plot                                - [cal_slit]
ic_slit_order_plot = 10

# -----------------------------------------------------------------------------
#   cal_ff parameters
# -----------------------------------------------------------------------------

#    Do background measurement (True = 1, False = 0)                  - [cal_ff]
ic_do_bkgr_subtraction = 0

#    Half-size of window for background measurements                  - [cal_ff]
ic_bkgr_window = 100

#    Number of orders in tilt file (formally nbo)                     - [cal_ff]
ic_tilt_nbo = 36

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
ic_blaze_fitn = 5

#   Order to plot on ff image plot (formally ic_order_plot)           - [cal_ff]
ic_ff_order_plot = 5

#   Plot all order fits (True = 1, False = 0)                         - [cal_ff]
#        (takes slightly longer than just one example order)
ic_ff_plot_all_orders = 0

#   Define the orders not to plot on the RMS plot                     - [cal_ff]
#      should be a list of integers
ff_rms_plot_skip_orders = []

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
ic_extnbsig = 2.5

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
ic_extract_type = '3c'
# Now select the extraction type in cal_ff ONLY                       - [cal_FF]
ic_ff_extract_type = '3c'

#   Set the number of pixels to set as                   - [cal_extract, cal_FF]
#       the border (needed to allow for tilt to not go off edge of image)
ic_ext_tilt_bord = 2

#   Set a custom noise level for extract (formally sigdet)       - [cal_extract]
#       set to -1 to use sigdet from file header
ic_ext_sigdet = 100

#    Define order to plot                                        - [cal_extract]
ic_ext_order_plot = 5

#    Define the percentage of flux above which we use    - [cal_ff, cal_extract]
#        to cut
#        ONLY USED IF EXTRACT_TYPE = '3d'
ic_cosmic_sigcut = 0.25

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
#   NOT USED ON H2RG
badpix_full_flat = 'detector_flat_full.fits'

#   Defines the threshold on the full detector flat file to       - [cal_badpix]
#      deem pixels as good
#   NOT USED ON H2RG
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

#  Define the mode to work out the Earth Velocity calculation        - [cal_CCF]
#      Options are:
#           - "off" - berv, bjd, bervmax is set to zero
#           - "old" - berv is calculated with FORTRAN newbervmain.f
#             WARNING: requires newbervmain.f to be compiled
#                      with f2py -c -m newbervmain --noopt --quiet newbervmain.f
#                      located in the SpirouDRS/fortran directory
#           - "new" - berv is calculated using barycorrpy  but needs to be
#                     installed (i.e. pip install barycorrpy)
#                     CURRENTLY NOT WORKING!!!
ccf_bervmode = "off"

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


# -----------------------------------------------------------------------------
#   cal_hc/cal_wave parameters
# -----------------------------------------------------------------------------
#  Define the lamp types                                    - [cal_HC, cal_wave]
#      these must be present in the the following dictionaries to
#      be used
#                  - ic_ll_line_file
#                  - ic_cat_type
ic_lamps = {'UNe':'hcone', 'TH':'hctwo'}

#  Define the catalogue line list to use for each           - [cal_HC, cal_wave]
#       lamp type (dictionary)
ic_ll_line_file_all = {'UNe':'catalogue_UNe.dat', 'TH':'catalogue_ThAr.dat'}

#  Define the type of catalogue to use for each lamp type   - [cal_HC, cal_wave]
ic_cat_type_all = {'UNe': 'fullcat', 'TH':'thcat'}

#  Define the Resolution of detector                        - [cal_HC, cal_wave]
ic_resol = 55000

#  Define wavelength free span parameter in find            - [cal_HC, cal_wave]
#      lines search
# default = 3   or 2.6
ic_ll_free_span = 3

#  Define minimum wavelength of the detector to use in      - [cal_HC, cal_wave]
#     find lines
ic_ll_sp_min = 900

#  Define maximum wavelength of the detector to use in      - [cal_HC, cal_wave]
#     find lines
ic_ll_sp_max = 2400

#  Define the read out noise to use in find lines           - [cal_HC, cal_wave]
# default = 16.8
ic_hc_noise = 30

# Maximum sig-fit of the guessed lines                      - [cal_HC, cal_wave]
#     fwhm/2.35 of th lines)
ic_max_sigll_cal_lines = 5.2

# Maximum error on first guess lines                        - [cal_HC, cal_wave]
# default = 1
ic_max_errw_onfit = 1

# Maximum amplitude of the guessed lines                    - [cal_HC, cal_wave]
# default = 2.0e5
ic_max_ampl_line = 2.0e8

#  Defines order to which the solution is calculated        - [cal_HC, cal_wave]
#      previously called n_ord_final
# QUESTION: Not used in cal_HC???
ic_hc_n_ord_start = 0

#  Defines order to which the solution is calculated        - [cal_HC, cal_wave]
#      previously called n_ord_final
ic_hc_n_ord_final = 24

#  Defines echeele of first extracted order                 - [cal_HC, cal_wave]
ic_hc_t_order_start = 66

# Define the minimum instrumental error                     - [cal_HC, cal_wave]
ic_errx_min = 0.03

#  Define the wavelength fit polynomial order               - [cal_HC, cal_wave]
# default = 5
ic_ll_degr_fit = 4

#  Define the max rms for the sigma-clip fit ll             - [cal_HC, cal_wave]
ic_max_llfit_rms = 3.0

#  Define the fit polynomial order for the Littrow fit      - [cal_HC, cal_wave]
#      (fit across the orders)
ic_Littrow_fit_deg = 4

#  Define the littrow cut steps                             - [cal_HC, cal_wave]
ic_Littrow_cut_step_1 = 250
ic_Littrow_cut_step_2 = 500

#  Define the order to start the Littrow fit from           - [cal_HC, cal_wave]
#  (ends at ic_hc_n_ord_final)
ic_Littrow_order_init = 0

#  Define orders to ignore in Littrow fit                   - [cal_HC, cal_wave]
ic_Littrow_remove_orders = []

#  Define the order fit for the Littrow solution            - [cal_HC, cal_wave]
#      (fit along the orders)
ic_Littrow_order_fit_deg = 4

#  Define wavelength free span parameter in find            - [cal_HC, cal_wave]
#    lines search (used AFTER littrow fit) default = 3
ic_ll_free_span_2 = 2.6


#  Defines order to which the solution is calculated        - [cal_HC, cal_wave]
#      previously called n_ord_final (used AFTER littrow fit)
# Question: Not used in cal_HC???
ic_hc_n_ord_start_2 = 0

#  Defines order to which the solution is calculated        - [cal_HC, cal_wave]
#      previously called n_ord_final (used AFTER littrow fit)
ic_hc_n_ord_final_2 = 24

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
hc_find_lines_mode = 0

#  Define the CCF mask for the wave solution CCF            - [cal_HC, cal_wave]
#       calculation
ic_wave_ccf_mask = {'UNe': 'test_mask_UNe_firstguess_R50000.mas', 'TH':'test_mask_TH_R50000.mas'}

#  Define the weight of the wave CCF mask                   - [cal_HC, cal_wave]
#     (if 1 force all weights equal)
ic_wave_ccf_w_mask_min = 1.0

#  Define the wave CCF width of the template line           - [cal_HC, cal_wave]
#     (if 0 use natural)
ic_wave_ccf_mask_width = 0.0

#  Define the wave CCF half width                           - [cal_HC, cal_wave]
ic_wave_ccf_half_width = 10.0

#  Define the wave CCF step                                 - [cal_HC, cal_wave]
ic_wave_ccf_step = 0.1

#  Define the type of fit for the wave CCF fit              - [cal_HC, cal_wave]
wave_ccf_fit_type = 1

#  Define first order FP solution is calculated from                - [cal_wave]
ic_fp_n_ord_start = 0

#  Defines last order FP solution is calculated to                  - [cal_wave]
ic_fp_n_ord_final = 24

#  Define the size of region where each line is fitted               -[cal_wave]
ic_fp_size = 3

#  Define the threshold to use in detecting the positions            -[cal_wave]
#      of FP peaks
ic_fp_threshold = 0.2

#  Define the initial value of FP effective cavity width            - [cal_wave]
#   2xd = 24.5 mm = 24.5e6 nm  for SPIRou
ic_fp_dopd0 = 2.45e7

#  Define the polynomial fit degree between FP line numbers and     - [cal_wave]
#      the measured cavity width for each line
ic_fp_fit_degree = 9

#  Define the FP jump size that is too large                        - [cal_wave]
ic_fp_large_jump = 0.7

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


# -----------------------------------------------------------------------------
#   polarimtery parameters
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
ic_polar_cont_binsize = 4000

#  Define the polarimetry continuum overlap size (for plotting)   - [pol_spirou]
ic_poalr_cont_overlap = 0


# -----------------------------------------------------------------------------
#  Quality control settings
# -----------------------------------------------------------------------------

#   Max dark median level [ADU/s]                                   - [cal_dark]
qc_max_darklevel = 0.5

#   Max fraction of dead pixels                                     - [cal_dark]
qc_max_dead = 20.0

#   Max fraction of dark pixels (percent)                           - [cal_dark]
qc_max_dark = 6.0

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
qc_ff_rms = 0.12

#   Saturation level reached warning                                  - [cal_ff]
qc_loc_flumax = 64500

#   Maximum allowed RMS allowed for the RMS of the tilt             - [cal_slit]
#        for the slit
qc_slit_rms = 0.1

#   Minimum allowed angle for the tilt of the slit [deg]            - [cal_slit]
qc_slit_min = -8.0

#   Maximum allowed angle for the tilt of the slit [deg]            - [cal_slit]
qc_slit_max = 0.0

#   Maximum signal allowed (set saturation limit)                - [cal_extract]
#        however currently does not trigger qc
qc_max_signal = 65500

#   Maximum littrow RMS value for cal_hc                    - [cal_HC, cal_wave]
#       (at x cut points)
qc_hc_rms_littrow_max = 0.3

#   Maximum littrow devilation from wave solution for       - [cal_HC, cal_wave]
#        cal_wave (at x cut points)
qc_hc_dev_littrow_max = 0.9

#   Maximum littrow RMS value for cal_hc                    - [cal_HC, cal_wave]
#       (at x cut points)
qc_wave_rms_littrow_max = 0.1

#   Maximum littrow devilation from wave solution for       - [cal_HC, cal_wave]
#       cal_wave (at x cut points)
qc_wave_dev_littrow_max = 0.3

#   Define the maximum number of orders to remove from RV            -[cal_wave]
#       calculation (for instrumental drift calculation)
qc_wave_idrift_nborderout = 15

#   Define the maximum allowed drift (in m/s) in the                 -[cal_wave]
#       instrumental drift calculation
qc_wave_idrift_rv_max = 150.0


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
