


================================================================================
* Thu Oct 12 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.001

================================================================================
	- added evaluate value function to try to interpret the value in a config file (i.e. set to float/int/bool before setting to a string) (rev.33496f95)
	- added line separator (rev.bc8933ae)
	- added __version__ (rev.fad32b70)
	- added keyslookup function (rev.28f5d852)
	- first commit (rev.7496d329)
	- added GetKeys + ResizeImage function to init (rev.654845b6)
	- added ic_cc(x/y)_(blue/red)_(low/high) variables (rev.8e4b6a3d)
	- added read image and resize iamge sections (rev.ba1d1b3a)
	- modified run_startup to deal with no fitfilename file (rev.5b33578d)
	- updated DRS_ROOT path (rev.e31ecc42)
	- added readimage+read_raw_Data documentation and keylookup+math_controller function (rev.384d3c75)
	- added ReadImage and GetKey to init (rev.c9087f18)
	- added ReadImage functions and got keys from header (rev.c78b6d25)
	- Added initial files, added readimage and read_raw_data functions (rev.37d42d0e)
	- Added initial files (rev.2d8f5a2b)
	- Updated title of readme (rev.326dbfd3)



================================================================================
* Fri Oct 13 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.002

================================================================================
	- added check for reduced directory (and make if needed) (rev.c696f75d)
	- First commit (rev.3336e35b)
	- added PutFile and UpdateMaster functions (rev.d87cedf5)
	- added writeimage and copy_original_keys functions (rev.04e4a945)
	- added readimage and writeimage function to init (rev.9c6deba8)
	- added dark quality control parameters (rev.823fc9d5)
	- added short name to measure_dark function (rev.2f2150d1)
	- added more TODO's regarding user defined config file (rev.e3b6b177)
	- added DRS_PLOT variable (rev.cd42a2c5)
	- added image region plot (rev.32bf8355)
	- added dark histogram variables (rev.8a3f3831)
	- added measure dark function (rev.b8219b1e)



================================================================================
* Mon Oct 16 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.003

================================================================================
	- added nbframes as a parameter to get in run_startup function (rev.6ce222f7)
	- changed ACQTIME_KEY to getting from config file (rev.cf5eb368)
	- allow math_controller arg "framemath" to be None --> pass straight through (rev.fa11ca1f)
	- added correct_for_dark function (rev.4e924b7f)
	- added CorrectForDark to init (rev.d63ca50f)
	- added ACQTIME_KEY constant (rev.9ae97956)
	- added read image file section (rev.59ae0e43)
	- added rotation and conversion to e- (commented out currently) (rev.9065d548)
	- added fiber_params function (rev.812a58ad)
	- Added a requirement that calibdb is defined in run_startup function (rev.2e79b04a)
	- updated the README with summary of changes to cal_DARK_spirou.py (rev.8ed078eb)



================================================================================
* Tue Oct 24 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.004

================================================================================
	- set out plan for code (rev.ded97dc2)
	- move config file (rev.efd2571a)
	- add warning logger and remove sys.exit from all but logger (rev.48eb7009)



================================================================================
* Wed Oct 25 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.005

================================================================================
	- added locate_central_positions function (rev.336d0f7d)
	- added some code for locating central positions (rev.9187c46c)
	- removed sys.exit (now in WLOG for key='error') (rev.6db476e8)
	- added keys argument to write_file_to_master (rev.3962daa4)
	- moved smoothed_boxmean_image function to spirouLOCOR (rev.914475c9)
	- moved smoothed_boxmean_image function to spirouLOCOR (rev.873b593a)
	- corrected typo 'Adding' --> 'ADD' (rev.7bb2969c)
	- updates init with boxsmoothedminmax (rev.c5ab0cd6)
	- Added config readme at top (rev.a35c344f)
	- Added measure background function and plot_y_miny_maxy and plot_min_ycc_loc_threshold (rev.6955534e)
	- Changed updatemaster key to variable instead of hardcoded string (rev.70172bdd)
	- Added cal_loc_RAW_spirou section to changelog (rev.de915bef)
	- First commit of spirouLOCOR (empty) (rev.cb458c0f)
	- Added flip_image, convert_to_e, and smoothed_boxmean_image functions (rev.a8605ef4)
	- Added 'BoxSmoothedImage, ConvertToE and FlipImage functions (rev.f8ac5a1c)
	- Added loc_box_size constant and localisation parameters section (rev.ae3e2109)
	- Added construct image order_profile section and write order_profile to file/calibDB sections (rev.4f3c106c)
	- updated comment with spelling correction (rev.304fd3cf)



================================================================================
* Thu Oct 26 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.006

================================================================================
	- Revert "added example of BoxSmoothedImage with mode 'convolve' vs 'manual'" This reverts commit f7637bf (rev.b70ff318)
	- changed the logged to exit via sys.exit (rev.d9ccd91c)
	- added a minimum width requirement and return widths in "locate_center_order_position" functions (rev.be0be432)
	- closed the hdu and added a header extension argument (default = 0) (rev.db5a81c9)
	- Changed name of locate_central_position alias (rev.a74ebcb8)
	- added constants from cal_loc_RAW_spirou (rev.b8e50f80)
	- added to position and width finding (incomplete + untested) (rev.1c941f8e)
	- fixed formatting (rev.14edc82d)
	- Reformatted BoxSmoothedimage and LocateCentralPosition descriptions in change log (rev.cd4fac4d)
	- wrapped for locate_order_positions to go between manual and convolve versions (rev.c111e589)
	- Added more documentation for smoothed_boxmean_image (rev.87684674)
	- added BoxSmoothedImage 'convolve' vs 'manual' change to change log (rev.c17fd452)
	- added BoxSmoothedImage with mode 'convolve' vs 'manual' (rev.20f9934a)



================================================================================
* Fri Oct 27 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.007

================================================================================
	- reworked fit order into "initial order fit" and "sigmaclip_order_fit" (rev.8492e34c)
	- added some more location parameters (rev.86389f0c)
	- updated locate center order position into two functions (rev.ede29b87)
	- return header from last "added" fits and set fitsfilename to last file (as in original code) - not sure it this is wanted but it is how it is (rev.e42991e3)
	- changed locate_center_order_positions to two functions one for center finding one for center + width of individual (subtle differences) (rev.cd21ea34)



================================================================================
* Mon Oct 30 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.008

================================================================================
	- file migration and new imports (rev.243dec61)
	- file migration and new imports (rev.f2cd5dc7)
	- file migration and new imports (rev.d2d8c77f)
	- file migration and new imports (rev.be5f1d80)
	- file migration and new imports (rev.3eb1cc7a)
	- file migration and new imports (rev.d8c7a1c2)
	- file migration and new imports (rev.fa356b4e)
	- file migration and new imports (rev.ed9bdaaf)
	- file migration and new imports (rev.da87060b)
	- file migration and new imports (rev.5935788b)
	- file migration and new imports (rev.ae654249)
	- file migration and new imports (rev.41435902)
	- file migration and new imports (rev.b5118c81)
	- tmp file for keyword args? - sort this out (rev.7cbd2230)
	- file migration and new imports (rev.b9092721)
	- file migration and new imports (rev.c20ff924)
	- file migration and new imports (rev.6c8a44b0)
	- reordered files (rev.58b7c91a)



================================================================================
* Tue Oct 31 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.009

================================================================================
	- modified measure_background_and_get_central_pixels to accept and return loc (rev.9ab531fc)
	- added empty holder for image_localazation_super function (not finished) (rev.b643ab96)
	- updated call for ACQTIME_KEY to kw_ACQTIME_KEY (rev.348bb9c9)
	- moved functions into sections (rev.e7a81ddc)
	- updated init file (rev.f5fe3696)
	- updated call to spirouConfig (rev.511e46a8)
	- removed log constants (to spirouConfig) (rev.886bc539)
	- updated spirouCore init (rev.e589c552)
	- first commit (rev.5e0da060)
	- moved some constants to here (TRIG_KEY, WRITE_LEVEL, EXIT) (rev.fb41622c)
	- first commit for spirouConfig ini - moved config and keyword function calls to here (rev.15e5cd83)
	- added ic_locfitp, ic_loc_delta_width, ic_locopt1 to config file (rev.583df939)
	- added SPECIAL_NAME back to config (rev.d8b7f353)
	- updated function calls (rev.2f4fd513)
	- updated function calls (rev.a01562e2)
	- added call to AddNewKey (rev.8f73f1df)



================================================================================
* Wed Nov 01 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.010

================================================================================
	- set_source for param dicts (rev.ad3eb621)
	- set_source for param dicts (rev.9058ab5a)
	- renamed set_source function to set_source_for_defaulting_statements (to avoid confusion) (rev.651f1e0e)
	- added set_source (rev.a76f493d)
	- added documentation to ConfigException, added new class ParamDict (custom dictionary), added set_source to param dicts and a set_source function for dealing with default values from check_params() (rev.27ee5a91)
	- added ParamDict to init (rev.06b66f2b)
	- added set source + c_Database --> ParamDict (rev.845fac87)
	- added set source + fparam --> ParamDict (rev.5008c31e)
	- added set source + updated keywords to match spirouKeywords (rev.c6db4970)



================================================================================
* Thu Nov 02 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.011

================================================================================
	- added timer, moved plots to spirouPlots, moved functions to spirouLOCOR, updated AddNewKey --> AddKey, added quality control section and add to calibDB section (rev.02505eb0)
	- added timer, moved plots to spirouPlots, updated AddNewKey--> Addkey, (rev.e228f6eb)
	- added __getitem__, __contains, __delitem__ functions, forced all keys to uppercase (now ParamDict is case-insensitive), added source_keys, __capitalise_keys__, __capitalise__key__ functions, (rev.60d70762)
	- reloaded keywords USE_KEYS, added ParamDict call, added kw_LOC_ keys, added source to overwritten warning (rev.2b63e222)
	- renamed AddNewKey to AddKey (rev.1c7f68b5)
	- added wrapper function for add_new_key (add_new_keys), (rev.9ac9b952)
	- renamed image_localazation_superposition to image_localization_superposition (rev.e13c792d)
	- added functions from cal_loc --> spirouLOCOR, added image_localazation_superposition function (rev.46c9b02d)
	- added functions from cal_loc --> spirouLOCOR to init (rev.0fd29ca3)
	- moved fiber variables to own section, added qc for cal_loc (rev.f3d229b5)
	- changed keys as now param dict all uppercase (rev.6873d365)
	- first commit - all plotting functions moved here (rev.ef67c66f)



================================================================================
* Fri Nov 03 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.012

================================================================================
	- updated comments in constants_SPIROU (rev.68ad681b)
	- added a label to locplot_order (rev.63e50ace)
	- changed splt to sPlt (rev.f2ca005a)



================================================================================
* Tue Nov 07 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.013

================================================================================
	- added doc for get_loc_coefficients, initial_order_fit, sigmaclip_oder_fit and image_localization_superposition added calcualte_location_fits function (rev.8917dccc)
	- first commit - added extract wrapper alias (rev.b9416bdc)
	- first commit - added extract wrapper and first attempt at extract code (rev.b3ac2df3)
	- first commit - added fast polyval function (rev.c6d00493)
	- added doc string comments for all functions (rev.fbe258d5)
	- edited kw_loco_ctr_coeff and kw_loco_fwhm_coeff (rev.f2060b4c)
	- allowed max_time to be None and get max_time from p['fitsfilename'] (rev.6fb99fa9)
	- added some slit parameters (rev.de6b78f7)
	- added extract function (rev.ec6d22f9)
	- added test via sys.argv (rev.eeda0ea4)
	- added get_loc_coefficients function (rev.ca19d015)
	- added GetCoeffs to init (rev.cbd60bc8)
	- called GetAcqTime in correct_for_dark function (rev.a5c1863c)
	- added read_header, read_key and read_key_2d_list functions (rev.61f78fe9)
	- added ReadHeader, ReadKey, Read2Dkey to init (rev.fb8b20b1)
	- added CopyCDBfiles call to run_startup function (rev.8d2535df)
	- added get_acquision_time and copy_files function (rev.b93bf7c9)
	- added CopyCDB and GetAcqTime to init (rev.62291e39)
	- updates cal_SLIT with __NAME__ and new functions, updated startup section, added read image section, correction of dark section, resize image section, get coefficients section (rev.482d781c)
	- removed unused cocde from cal_loc_RAW (rev.9f3240d1)



================================================================================
* Wed Nov 08 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.014

================================================================================
	- added doc string for extract and added ExtractABorder alias to init (rev.18cf198f)
	- added FitTilt and GetTilt to init (rev.4903ce75)
	- moved extract_AB_order here (from cal_SLIT_spirou) (rev.b5457c14)
	- removed get_tilt and fit_filt functions (to spirouImage) (rev.f8748c4f)
	- moved get_tilt and fit_filt functions here (rev.74c40879)
	- added doc strings for slit plotting functions (rev.9e9003dc)
	- updated USE_KEYS list formatting (rev.a3cb17e2)
	- updated readme (rev.633fe8f3)
	- reworked get_tilt function, added extract AB order function and fit filt function, added plotting section, added tilt calculation section, added todo quality control section, added update calibDB section (rev.9e9f220f)
	- added coi ic_tilt_fit and ic_slit_order_plot constants (rev.cb4852f4)
	- added kw_TILT keyword (rev.15a29f8c)
	- added slit plotting functions: selected_order_plot and slit_tilt_angle_and_fit_plot (rev.63c95775)
	- added doc string for extract_wrapper, extract_const_range, added test functions extract_const_range_fortran and moved extract_const_range to extract_const_range_wrong (updates former) (rev.beb23aed)
	- changed plt.ion to sPlt controller function (rev.6041d5b8)



================================================================================
* Thu Nov 09 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.015

================================================================================
	- added cal_slit section (rev.6890feec)
	- stricked done progress (rev.caa43047)
	- added hlines (rev.4d78b1d2)
	- edit table of contents, added back to top, added future sections (rev.0f29532d)
	- added table of contents (rev.2b8dc991)
	- section numbering (rev.724a85b4)
	- added WLOG update (rev.5aa2d3ae)
	- added WLOG update, and configError update (rev.7fa6eb8c)
	- added jpg py3 logo (rev.67f03d78)
	- added picture as jpg (rev.fefefe57)
	- changed path for plot (rev.3f07b083)
	- correlation with a box test plot (rev.64426813)
	- change test function for smoothed_boxmean_image (rev.1b427ddb)
	- added to general section, cal_dark section and cal_loc section (rev.e6d923fd)
	- moved kw_TILT to own section (rev.76f4ae36)
	- edited description of slit param (rev.a02c46b2)



================================================================================
* Fri Nov 10 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.016

================================================================================
	- added fib_type to fiber types constants, added cal_ff params, added a qc param (rev.2e449e34)
	- moved measure_box_min_max and measure_background_and_get_central_pixels to spirouBACK (rev.0ce7762c)
	- added measure_background_and_get_central_pixels, measure_box_min_max to spirouBACK measure_background_flatfield (not finished) to init (rev.ef72ca4b)
	- moved measure_background_and_get_central_pixels, measure_box_min_max to spirouBACK, added measure_background_flatfield (not finished) (rev.0ed147aa)
	- moved measure_background_and_get_central_pixels, measure_box_min_max to spirouBACK (rev.4a4e9cc9)
	- moved MeasureBkgrdGetCentPixs to spirouBACK (rev.0c7bba1f)
	- added setup section, added read image section, added correction of dark section, added resize image section, , added max_signal section (rev.3e42c72a)
	- chnaged ccdsigdet to sigdet, added test (no need to specific files) (rev.c0c2ce96)



================================================================================
* Mon Nov 13 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.017

================================================================================
	- First commit, added some well used constants (constants but need input and functions so not formed from basic string/int/float/list) (rev.da91a499)
	- reworked fiber_params to get dictionaries of constants with particular suffix, added more logging to get_loc_coefficients, added merge_coefficients function (rev.5f4ecefa)
	- added mergecoefficients alias (rev.00b89564)
	- added masterfile constant, added get_gain, get_sigdet, get_param functions (rev.cc0cbfb6)
	- moved bulk of getting file name from calibDB to spirouCDB, added read_order_profile_superposition function (rev.a9369889)
	- added GetSigdet, GetExptime, GetGain and ReadOrderProfile aliases to init (rev.c26b2512)
	- added extract_tilt_weight_order function (not finished), added extract_tilt_weight skeleton code, changed extraction_wrapper to fit changes of other functions (rev.c0cbc55f)
	- added ExtractTiltWeightOrder alias to init file (rev.d304296f)
	- added reduced folder constant, fixed calibd_dir path on line 150 (now 149) (rev.d0bf109d)
	- fixed logging to file (date wasn't working) (rev.9870569b)
	- added sigdet, exptime and gain keywords, moved acqtime to "required header keys" section (rev.d4587cac)
	- added extract_dict_params function (rev.29f18313)
	- added ExtractDictParam to init (rev.005afb9b)
	- added raw and reduced dir constants, added new function get_file_name, added lock_file and master file constants (rev.07373e82)
	- added GetFile command to init (rev.c76c12ae)
	- chagned fiber param variables to dictionaries (rev.bb852c58)
	- changed getting sigdet, exptime and gain to functions, added reduced folder constant, added new fiber params command (rev.6ef17178)
	- changed getting sigdet, exptime and gain to functions, added reduced folder constant (rev.22102bec)
	- changed getting sigdet, exptime and gain to functions, added reduced folder constant, added read tilt slit angle, added start of fiber extract loop (not finished) (rev.05c58bb0)
	- changed getting sigdet, exptime and gain to functions, added reduced folder constant (rev.b3be5b55)
	- added pep8 cosmetic corrections (rev.c90c8600)
	- added pep8 cosmetic corrections (rev.43351098)
	- added filename option to readimage function, added read_tilt_file function (rev.1b2fb803)
	- Added ReadTiltFile to init (rev.ea4cb517)
	- added image to doc string for extract_AB_order (rev.2e6c516a)
	- added ic_tilt_nbo constant (rev.f5e32ed6)
	- added space between comma (rev.27070340)
	- added read tilt slit angle section (rev.9d4f278b)



================================================================================
* Tue Nov 14 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.018

================================================================================
	- added convert_to_adu function, fixed get_gain/get_sigdet/get_param functions (rev.ad361d00)
	- removed reducedfolder call and fixed order_profile key (rev.da0547d5)
	- added ConvertToADU alias to init (rev.1f291183)
	- first commit spirouFLAT.py added measure_blaze_for_order function (rev.80e1ee14)
	- first commit spirouFLAT init (added MeasureBlazeForOrder alias) (rev.e4f77e45)
	- modified extract_tilt_weight_order and extract_wrapper functions, added extract_tilt_weight function and extract_tilt_weight_old function (rev.e4b0f847)
	- fixed error in gain/exptime keyword (rev.acd9e441)
	- fixed hard coded key in get_file_name function (rev.ab2b390a)
	- cosmetic change (rev.028c980f)
	- added ic_ff_sigdet, ic_extfblaz, ic_blaze_fitn constants (rev.b38d6917)
	- added storage set up for extraction, added extract with tilt+weight loop, added skip for max_signal QC (rev.c12be7ec)



================================================================================
* Wed Nov 15 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.019

================================================================================
	- added cal_FF_RAW summary of changes section, updated progress (rev.75b5cef6)
	- added add_key_1d_list function, updated add_key_2d_list to be more generic (with header comment) (rev.e52931ef)
	- added AddKey1DList alias to init (rev.ea0cfacd)
	- added selected_order_fit_and_edges, selected_order_tilt_adjusted_e2ds_blaze and selected_order_flat plot functions (rev.b7193b6f)
	- added kw_EXTRA_SN and kw_FLAT_RMS (rev.76272626)
	- added ic_ff_order_plot constant (rev.96a9181e)
	- cosmetic change (rev.6ddd2803)
	- added plot section, added saving blaze and flat field section (rev.35570175)



================================================================================
* Thu Nov 16 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.020

================================================================================
	- add calibDB to p in startup if calibdb required (should be faster than reloading it each time) (rev.cac9291b)
	- corrected cal_ff extractiltweightorder spelling mistake (rev.189d063b)
	- added check for calibDB in p (rev.0640d121)
	- added check for 'calibDB' in p (rev.5c288066)
	- moved forbidden_copy_keys to constants, added get_type_from_header function, added read_raw_header function (rev.b22f5221)
	- added GetTypeFromHeader alias to init (rev.9d84ac54)
	- added dealing with customargs and added run_time_custom_args + display_custom_args functions (rev.0a385ff1)
	- added kw_DPRTYPE (rev.7702d5c7)
	- added FORBIDDEN_COPY_KEYS constant (rev.8d50e67c)
	- added tests for calibDB in p (rev.794ac3c8)
	- reformatted comments on variables (rev.0b81aeea)
	- added dprtype find from header, modified test code (rev.595f3eb8)
	- added dprtype find from header, modified test code (rev.20219aa2)
	- added dprtype find from header, modified test code (rev.cd589bef)
	- added dprtype find from header, added test code, added __NAME__, added setup section (rev.73d3d236)
	- added dprtype find from header, added test code (rev.faa41781)



================================================================================
* Fri Nov 17 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.021

================================================================================
	- added p to spiouCDB.GetDatabase (for max_time constants) (rev.76dd088d)
	- added p to spiouCDB.GetDatabase (for max_time constants), added read out of max_time in error (helps to identify why error was caused) (rev.b3a3c5f6)
	- fixed call to spirouEXTOR.ExtractABOrder, added p to spiouCDB.GetDatabase (for max_time constants) (rev.18dba768)
	- fixed error in add_key_2d_list (rev.c7af0612)
	- fixed selected_order_fit_and_edges, added function all_order_fit_and_edges (rev.20d34e0d)
	- added stringtime2unixtime and unixtime2stringtime functions (fixed from spirouCDB) (rev.0840dded)
	- added DATE_FMT_HEADER and DATE_FMT_CALIBDB constants (rev.7283e5d9)
	- added ic_ff_plot_all_orders constant, fixed loc_file_fpall and orderp_file_fpall (rev.63650939)
	- fixed acqtime key error, fixed time getting error (inconsistent times), made check that times are consistent, added max_time_human and max_time_unix to p (rev.98a18a24)
	- added due test mode (rev.ede6b6f4)
	- added due test mode, added plot all orders (instead of just selected) - slower, added flat to calibDB (rev.7876b462)
	- modified imports, added version/author from constants (rev.28122580)
	- modified imports, added version/author from constants, and added __all__ function (rev.fe91627a)
	- modified imports, added version/author from constants, changed lloc to loc, added functions for extract_order, extract_order_0, extract_tilt_order, extract_weight_order (None currently working) - will need to edit extract_wrapper to make work (rev.370c7539)
	- modified imports, added version/author from constants and interactive plot constant (rev.2f817cbe)
	- modified imports, added version/author from constants, added TRIG_KEY, WRITE_LEVEL, EXIT and WARN from constants, added CONFIG_KEY_ERROR warning (rev.aaa26d77)
	- added constants PACKAGE(), VERSION(), AUTHORS(), LATEST_EDIT(), CONFIGFOLDER(), CONFIGFILE(), INTERACTIVE_PLOT_ENABLED(), LOG_TRIG_KEYS(), WRITE_LEVEL(), LOG_EXIT_TYPE(), LOG_CAUGHT_WARNINGS(), CONFIG_KEY_ERROR, add set version and author from constants (rev.b6d86424)
	- modified imports, added version/author from constants, added package config_file, configfolder and trig key from Constants (rev.d247f499)
	- modified imports, added version/author from constants (rev.d5d23241)
	- modified imports, added version/author from constants (rev.de854ac3)
	- modified imports, added version/author from constants (rev.ccbca83a)
	- modified imports, added version/author from constants, added __all__ aliases, added printing of sub-package names (rev.43cb6dc8)
	- first commit, modified imports, added version/author from constants, added __all__ aliases, moved RunInitialStartup and RunStartup here (from SpirouCore) (rev.6346b185)
	- modified imports, added version/author from constants, added __all__ aliases (rev.5ce74973)
	- modified imports, added version/author from constants, added __all__ aliases, added aliases for different extraction types (rev.2297605a)
	- modified imports, added version/author from constants, added __all__ aliases, moved RunInitialStartup and RunStartup to spirouStartup module (rev.4c1b22e7)
	- modified imports, added version/author from constants, added __all__ aliases (rev.174a5e19)
	- modified imports, added version/author from constants, added __all__ aliases (rev.6d72d3c3)
	- modified imports, added version/author from constants, added __all__ aliases (rev.2c8492ce)
	- editted comments for ic_extopt (rev.cfce1332)
	- modified imports, moved spirouStartup to own module, added calls to extract functions (rev.1122258d)
	- modified imports, moved spirouStartup to seperate module (rev.5953707e)
	- modified get_loc_coefficients to look for keyword 'LOC_FILE' (rev.ae7bc86a)
	- added key to arguments of read_tilt_file function, added read_wave_file function, modified read_order_profile_superposition to look for keyword 'ORDERP_FILE' (rev.2326277f)
	- added ReadWaveFile alias (rev.dc0ed08f)
	- added A and B to fiber type parameters, added loc_fil and orderp_file parameters (rev.77eac3f4)
	- moved dprtype from header getting section, added fiber A B and AB replacement for AB (in merging coefficients) (rev.7a3f7a48)
	- added read image section, added basic image properties section, added correction of dark, added resize image, added the logging of dead pixels, added minmax max_signal section, added background computation section, added tilt reading section, added wave solution reading section, added localaization coefficient getting section, added order profile getting section, added order loop, added noise/flux/SNR calculation, added saturation warning section, added quality control section (rev.ce0167fb)



================================================================================
* Mon Nov 20 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.023

================================================================================
	- updated progress section (rev.88b04cc8)
	- added function copy_root_keys function, modified read_header function (rev.3476deb4)
	- added alias for CopyRootKeys to init and __all__ (rev.940a8406)
	- modified extract_AB_order, extract_order, extract_tilt_order, extract_tilt_weight_order, extract_tilt_weight_order2, extract_weight_order, extract_const_range, extract_const_range_fortran, extract_const_range_wrong and extract_wrapper (rev.34dc6aab)
	- updated __all__ (rev.1c7cd553)
	- added alias to ExtractTiltWeightOrder2 (rev.3002221f)
	- added cal_extract plot functions (rev.414d764b)
	- moved EXIT definition to constants (rev.ce55029a)
	- added kw_LOCO_FILE keyword (rev.11c7c9b7)
	- added EXIT function (to return exit statement based on log_exit_type() (rev.538a4923)
	- added ic_ext_range_fpall, modified ic_ff_plot_all_orders, added ic_extmeanzone constants (rev.6c398756)
	- renamed extracttiltweightorder function to extracttiltweightorder2 (rev.970b4fed)
	- added timing to extraction comparison, corrected noise calculation, added plot section, added saving e2ds to file (rev.01b451a8)



================================================================================
* Tue Nov 21 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.024

================================================================================
	- modified readme with change in plot function (rev.ae0d48bf)
	- added imports, added startup section, read ref image section, get basic ref props section, resize ref image section, get loc/tilt/wave sections, merge coeffs section, extract ref section, computer dvrms section, plot ref section, get all files section, started all file loop (not finished) (rev.723e7013)
	- first commit, added delta_v_rms_2d function (rev.6a40f9c6)
	- first commit (rev.1da71656)
	- added get_all_similar_files function, modified correct_for_dark function (now can return dark for use later), modified get_exptime, get_gain, get_sigdet, get_param, added get_acqtime (rev.0f71b230)
	- redefined readimage (no combining) and added readimage_and_combine (to do reading and combining), updated readimage functions throughout (rev.d4a23422)
	- updated __all__ (rev.7062460e)
	- added GetAllSimilarFiles, GetAcqTime, ReadImage and ReadImageAndCombine functions (rev.3a4bd17f)
	- modified extract functions to have and look for keywords in function calls before using defaults (allows customisation) (rev.81d7a519)
	- renamed plots for clarity, added drift_plot_selected_wave_ref, drift_plot_photo_uncertainty (rev.3165b793)
	- added filename arg to get_acquisaion_time and code to deal with it (rev.2ac66bc8)
	- added ic_ext_d_range_fpall, ic_drift_noise, ic_dv_maxflux, ic_dv_boxsize, drift_nlarge, drift_file_skip, modified ic_ext_range_fpall (rev.276d6c08)
	- renamed ReadImage to ReadImageAndCombine for clarity and renamed plotting functions (for clarity) (rev.7d8ea81a)
	- renamed ReadImage to ReadImageAndCombine for clarity and renamed plotting functions (for clarity) (rev.de30dcc6)
	- renamed ReadImage to ReadImageAndCombine for clarity, changed fiber to p['fiber'], and renamed plotting functions (for clarity) (rev.831f21aa)
	- renamed ReadImage to ReadImageAndCombine for clarity (rev.44ebff86)
	- renamed ReadImage to ReadImageAndCombine for clarity (rev.08d647a6)



================================================================================
* Wed Nov 22 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.025

================================================================================
	- cosmetic changes to layout (rev.3c531467)
	- fixed some bugs, added compute cosmic+renorm section, added calculate RV drift section (rev.0ceb7b23)
	- changed mask1 and mask to flag in delta_v_rms_2d, added renormalise_cosmic2d and calculate_RV_drifts_2D functions (rev.cd1a5f5a)
	- added aliases for ReNormCosmic2D and CalcRVdrift2D (rev.4f76ed3e)
	- fixed error in get_all_similar_files (filelist not returned) (rev.b2676c7c)
	- fixed error in drift_plot_photon_uncertainty ('number_orders' in loc not p) (rev.ba682513)
	- added ic_drift_cut, renamed ic_dv_maxflux and ic_dv_boxsize (rev.1f33597a)



================================================================================
* Thu Nov 23 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.026

================================================================================
	- made unit test compatible with python 2 (ordered dict) (rev.fd6e8d2a)
	- updated progress in readme (rev.f97475b0)
	- Added to table of contents, added section 2.3 (to be filled out like section 2.2) (rev.e634df4d)
	- imported division from __future (to make sure all division is float division not int), cleaned up code, applied pep8 convensions (rev.78b48e70)
	- removed debug timing stuff (rev.7755f9ab)
	- update readme with cal_extract and cal_drift sections, added unit test timing section (rev.3c9dd84a)
	- renamed run_inital_startup to run_initial_startup (rev.52c2869f)
	- wrapper around cal_extract_RAW_spirou to allow fiber_type defined as 'C' (rev.6b994d13)
	- wrapper around cal_extract_RAW_spirou to define AB as the fiber type (rev.d157ba9a)
	- first commit - unit test for all tested files (with timings) (rev.5303b8f8)
	- modified run_inital_startup function to allow night_name and files arguments to be passed from main function calls (rev.8f6a8cb1)
	- moved measure_dark function here from cal_DARK_spirou, added 'human'/'unix' time to get_acqtime (rev.83c12ee6)
	- added alias to MeasureDark function (rev.664a00bf)
	- cosmetic change to __all__ (rev.78176a3a)
	- added drift_plot_dtime_Against_mdrift function (rev.e2d70a2c)
	- added kw_ACQTIME_KEY_UNIX (rev.8fbb254a)
	- modified ARG_FILE_NAMES and ARG_NIGHT_NAME to accept value already in p (from function call over command line arguments) (rev.2195d530)
	- added human/unix acqtime getting (rev.77fb5155)
	- added ic_drift_n_order_max parameter, cosmetic changes (spaces between sections increased) (rev.091c6501)
	- moved __main__ code to main function (rev.ae19cb0d)
	- moved __main__ code to main function (rev.a58f2a86)
	- moved __main__ code to main function (rev.ab129cbf)
	- moved __main__ code to main function (rev.304d25b2)
	- moved __main__ code to main function, added rv properties section, added plot section, added save drift values to file section (rev.f1e8e2d2)
	- moved __main__ code to main function (rev.9d40b078)



================================================================================
* Fri Nov 24 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.027

================================================================================
	- updated section naming in readme (rev.881f7038)
	- Added installation process to readme (rev.b793eb1e)
	- added ic_ext_all constant (rev.b54d1175)
	- added timing to debug run (rev.5d29aab4)
	- added posibility to save all extraction types to file (simple, tilt, tiltweight, weight) (rev.a44c8767)
	- added timed unit tests sections (rev.2d6736ad)
	- corrected unit test (rev.8a986ad0)



================================================================================
* Fri Nov 24 2017 eartigau <33963920+eartigau@users.noreply.github.com> - 0.0.027

================================================================================
	- Delete fits2ramp.py (rev.efdfb210)
	- Add files via upload (rev.84f54fb5)



================================================================================
* Mon Nov 27 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.028

================================================================================
	- Added latex gitignore (rev.2e6bbd62)
	- Memoir chapter styles (for pdf building) (rev.6bab88d4)
	- first commit dev guide (rev.5ce12122)
	- first commit user guide (rev.cc4a7504)
	- added logo to figures (rev.713a7b9c)
	- added constants first commit (rev.d6637b37)
	- added commands (from old manual) (rev.439d7f81)
	- added coding formats (using new styles) (rev.984fb2af)
	- Added installation process (first commit) for linux+mac and windows (rev.7528d70d)
	- what (rev.e99190da)
	- Added placeholder first commit tex files (empty other than title) (rev.ad4e6561)
	- updated progress in readme (with documentation needs) (rev.e25f1c54)
	- added a function to check write level, corrected bug in logging (was print_level needed to be log_level) (rev.b24a3cf8)
	- added logo to documentation files (rev.b9bdd6fa)
	- edited comments (rev.96cfe829)
	- added validation code (to test imports and display user setup) (rev.9fa85295)
	- updated links in table of contents (rev.1f6d97d6)



================================================================================
* Tue Nov 28 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.029

================================================================================
	- first commit of user version of data_architecture (not to be kept - use if statements?) (rev.80df7cca)
	- first commit of dev version of data_architecture (not to be kept - use if statements?) (rev.888d6814)
	- rebuilt pdf (rev.35317642)
	- rebuilt pdf (rev.55b82ab3)
	- added packages, modified abstract (noindent) (rev.b84785d2)
	- added packages, modified abstract (noindent) (rev.113df0cd)
	- ignored .listing files (rev.3161c6d9)
	- added recipe constants (rev.dcafef26)
	- added a definevariablecmd function (cyan instead of blue for definevariable) (rev.519f59a6)
	- complete redo of code formatting (using newtcblistings) (rev.e1872836)
	- updated label for chapter (rev.989d0ae0)
	- updated label for chapter (rev.766690ed)
	- updated label for chapter (rev.13a1207b)
	- added code blocks section (rev.e5948195)
	- added code block sections (rev.6c83b810)
	- updated notes to environment, code to code environments (rev.bc72a4dd)
	- added folder layout section, installation root dir section, bin dir section, spirou module directory section (rev.46aeebf5)
	- renamed cal_validate_drs to cal_validate_spirou (rev.8a2b1723)



================================================================================
* Wed Nov 29 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.030

================================================================================
	- rebuilt pdf files (rev.a52c49fc)
	- renamed preample to preamble (rev.25396646)
	- first commit of preamble file (rev.50595443)
	- first commit of packages file (rev.8d31a3b1)
	- first commit of merged variables file (rev.33633201)
	- first commit of merged recipes file (rev.3a5b95b2)
	- first commit of merged intro file (rev.f05b9c8e)
	- updated folder path for figures in readme (rev.9f87ce32)
	- rebuilt pdf files (rev.10ae8f71)
	- moved bulk of same code to packages file and preample file, added ifdevguide (to distinguish between dev and user) added coloured border, moved chapters around after merges (rev.b74374a4)
	- added masterclibddbfile, configtxtfile, acqtimekey, folderdateformat constants (rev.7b8eb112)
	- Added paraeter command and devnote devsection (all dependent on devguide or userguide) (rev.347396a8)
	- attempted breakable tcolorbox (rev.b6c4aefc)
	- first full commit - wrote section (rev.17f78506)
	- corrected spelling and added command in place of filename (rev.383c3a81)
	- added from old manual (rev.42646503)
	- added more sections (rev.e9314c2c)
	- deleted (not used) (rev.f17c7693)
	- deleted and merged dev and user (rev.6b3fffba)
	- deleted and merged dev and user (rev.fa3ada93)
	- deleted (rev.9adcdcda)
	- deleted and merged dev and user (rev.16aa58e4)
	- deleted and merged dev and user (rev.89d67875)
	- deleted and merged dev and user (rev.bed7b59c)
	- deleted and merged dev and user (rev.6dbe6a1c)
	- deleted and merged dev and user (rev.0639dacf)



================================================================================
* Thu Nov 30 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.031

================================================================================
	- cosmetic change to spacing (rev.14b55157)
	- added placeholder sections (rev.9d389582)
	- rebuilt pdfs (rev.ca44131e)
	- changed the user manual from yellow to red (and updated the margin label) (rev.da4c95a3)
	- changed the level of green on the dev margin (rev.d89ab2b8)
	- Added new constants (rev.ddbf3adc)
	- modified ParameterEntry command (rev.ba0042fb)
	- added a python inline style (rev.7798c19e)
	- added variable file locations section, image variable section, fiber variable section, dark calibration section (rev.cd4eea2e)
	- minor spelling changes to comments (rev.d0b1b7d2)
	- rebuilt pdfs (rev.b668d669)
	- now getting DRS_NAME and DRS_VERSION from spirouConfig.Consants (rev.711c19c0)
	- added a NAME function constant (rev.2103a142)
	- added spirouCONSt and spirouKeywords constants (rev.fb5a9ddc)
	- added minipage to parameter definition (to force items on one page) (rev.0f2698fa)
	- modified drs_name and drs_version - only in dev version (rev.3a7d3252)
	- removed drs_name and drs_version from config.txt (now in spirouConst) (rev.ddb24a5f)



================================================================================
* Fri Dec 01 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.032

================================================================================
	- rebuilt pdf (rev.0221148a)
	- corrected syntax errors and line breaking (rev.dc3da7eb)
	- rebuilt pdf files (rev.53bae521)
	- changed coi to os_fac and called from ic_tilt_coi (rev.5c36720c)
	- added getting DRS_NAME and DRS_VERSION from spirouConfig.Constants (rev.d316b5cc)
	- moved the internal hyperlink setup out of preamble (rev.b88192cd)
	- moved the internal hyperlink setup out of preamble (rev.323a7422)
	- added module aliases, added hslip 0pt for long variable names (so they can split on line break) (rev.ad2c7184)
	- moved colour definitions to commands, modified ParameterEntry to add called from form (for devguide only) (rev.63f7ec54)
	- moved colour definitions to commands (rev.51661436)
	- reformated ParameterEntry (added call from for devguide), added many new variables (still not complete) (rev.106f1d80)
	- added error if calibDB file does not exist (and proper exception + log/print message) (rev.6953cde1)
	- corrected typo (rev.0f9b5b84)
	- added sources for some constants, renamed coi to ic_tilt_coi (rev.c90a3774)
	- added source for fib_type (rev.299ef2c8)



================================================================================
* Mon Dec 04 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.033

================================================================================
	- image change (rev.b8ca969a)
	- image change (rev.4400c6f6)
	- added pdf manuals to readme (rev.836a512d)
	- added pdf manuals to readme (rev.34e0b968)
	- added pdf manuals to readme (rev.d993afeb)
	- added pdf manuals to readme (rev.9ed12e8e)
	- cosmetic changes only (rev.ad188d0e)
	- rebuilt pdf (rev.230f30c6)
	- rebuilt pdf (rev.95217d74)
	- removed .py from recipe command added more hskips for module commands (rev.4cabd40e)
	- added psuedoparamentry command (rev.181a6433)
	- added blank pythonbox tcblisting (rev.c08d7c8f)
	- added sections (rev.d67d43be)
	- changed note to dev note (rev.c624bc76)
	- wrote section (from readme) (rev.6986bdc7)



================================================================================
* Tue Dec 05 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.034

================================================================================
	- first commit of output_keywords chapter (filled and completed) (rev.47495770)
	- added output_keywords chapter (rev.be696d78)
	- rebuild pdf (rev.78bca374)
	- added keyword aliases (rev.28c47c3a)
	- added keywordentry command (similar to parmeterentry) (rev.45b96d1f)
	- added escaping to inline python text (rev.52472e32)
	- added text (rev.8d5dc785)
	- readme link update (rev.d3ac5dbf)
	- rebuilt pdf (rev.c67cf225)
	- rebuild pdf (rev.75501cf7)
	- cosmetic change (rev.0fe39aae)
	- added EXIT_LEVELS definition (rev.2cd0f3c1)
	- changed exit vairable to log_exit_type (rev.6b56f9f7)
	- added main init paramdict commands and move mac command (rev.3eab6588)
	- changed title size to tiny (rev.12a44ebd)
	- changed title size to tiny (rev.d49ab8df)
	- modified sections (rev.90020281)
	- added section (rev.dbcab84f)
	- removed sections added intro paragraph (rev.8e1186d3)



================================================================================
* Wed Dec 06 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.035

================================================================================
	- moved unit_Test1 to unit test module (rev.62b6f992)
	- first commit if unit test init file (rev.6b98f913)
	- modified run_time_custom_args (now works and tested), added get_custom_from_run_time_args and get_file functions, modified display_custom_args function (rev.3904460c)
	- added GetCustomFromRuntime and GetFile aliases (rev.dc2f3b05)
	- added normalise_median_flux and locate_bad_pixel functions (rev.286f344f)
	- Added functionality to readimage (rev.6646b3bb)
	- added LocateBadPixels and NormMedianFlat aliases (rev.3da1d311)
	- added badpix keywords (rev.3ea24f21)
	- added startswith function to ParamDict (rev.fb284c8a)
	- rebuilt pdf (rev.f54fc235)
	- cosmetic changes to commenting (rev.5cd57a05)
	- commented packages (rev.be463e05)
	- updated to-do list (rev.1d678b79)
	- added placeholder module sections (rev.b53de688)
	- added badpix constants (rev.e8430618)
	- fixed Addkey not assigning to hdict (rev.d8d713b7)
	- first commit cal_BADPIX (rev.4d293cf6)
	- rebuilt pdf (rev.f721f0f8)
	- rebuilt pdf (rev.5fa1bea5)
	- added to question (rev.a59342fa)
	- first commit to do list chapter (rev.f27a28af)
	- first commit documentation chapter (rev.e3130748)
	- added todolist and documentation chapters to main tex (rev.9f3e3c00)
	- added package ulem (For strikethrough) removed duplicate packages (rev.26e1451d)
	- removed visibility level from pseudoparamentry (rev.9bb106f6)
	- added latexbox (and latexbox1) (rev.b74c4c74)
	- removed visibility level for pseudo code (should be all private) (rev.7a897417)
	- added new code sections (rev.acd77525)
	- added latex code example (rev.f910b906)



================================================================================
* Thu Dec 07 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.036

================================================================================
	- added get_fiber_type function (rev.cbd74539)
	- added Get Fiber type function (rev.4fb5f7c2)
	- first commit (rev.6c63b1a1)
	- modified get_all_similar_files (rev.6166e362)
	- added readdata function and modified readimage, added read_flat_file function (rev.e72f68b1)
	- added MakeTable and WriteTable to init (rev.c32bbb58)
	- made sure we dont get filename unless we need it in get_acquision_time (rev.62559112)
	- added extra drift constants (rev.5acb42b6)
	- updated (rev.054ee72f)
	- first commit (no working) (rev.bee633fe)
	- changed __main__ to main() in sources (rev.f4a4a542)
	- updated readme with badpix section (rev.959b89a8)
	- corrected typo in wmed - in normalise_median_flat function (flat_median_width to badpix_flat_med_wid) (rev.a187cd4e)
	- corrected type (comma) in USE_KEYS (rev.85bf236f)
	- rebuild pdfs (rev.35283691)
	- added numbered pdf bookmarks + contents to bookmarks (rev.48911d87)
	- added TOC commands to change spacing in TOC (rev.0c68b29e)
	- added tocloft package (rev.9e6d55b1)
	- added calbadpix constant (rev.e1e648c3)
	- added badpix section (rev.0a79f79d)
	- updated todo section (rev.18acd5c6)
	- added badpix section (rev.51e4e4f8)
	- added badpix section (rev.266bbe8e)
	- added badpix constants (rev.d2123da2)
	- fixed badpixelfits construction (rev.a1ff389e)



================================================================================
* Fri Dec 08 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.037

================================================================================
	- rebuild pdfs (rev.4e735971)
	- updated readme (rev.877b8edb)
	- updated readme (rev.d3d92dc9)
	- added description of some variables (rev.7ea168c3)
	- added to changelog (rev.887e7fbc)
	- fixed fibertype function (now got from constants) (rev.3a672ff8)
	- fixed bug with LOC_FILE not being used (rev.4b409c84)
	- added root to copy root keys - now works as supposed to (only copies keys with root not all keys) (rev.c6eb8a44)
	- moved ww calc to function and calculating for all unique combinations (up to 4) of ww0 and ww1 (caused by rounding) (rev.4b2d44f0)
	- added closeall funciton, modified ext and drift functions (rev.65159702)
	- changed root_drs keywords (now used in code) (rev.1974ae23)
	- rebuild pdfs (rev.c86d4a17)
	- updated date (rev.9a44c969)
	- rebuild pdf (rev.48be2572)
	- added DRIFT-E2DS and changed rootdrs keywords (rev.74a6f351)
	- updated todo list (rev.2175f501)
	- removed duplicate sections (i.e. drifts should all be in one section etc), renamed placeholder sections (rev.6e253d51)
	- added new extract and drift constants, added spacing (rev.48e94896)
	- added new extract and drift keywords (rev.a3708f79)
	- added fiber_types, reworked extract and drift constants (rev.96c788f7)
	- added return locals (rev.89c4a89c)
	- added return locals (rev.5ef0ee83)
	- added return locals (rev.809209a9)
	- added return locals (rev.9367c1e7)
	- added return locals, added extra input to make like old extractrawC (rev.50dac88c)
	- added return locals, added extra input to make like old extractrawAB (rev.1af4b528)
	- added return locals, fixed changes from old to new (rev.c9b07bc2)
	- added return locals, fixed minor differences (rev.3819ad7c)
	- added return locals, fixed minor differences between old and new code (rev.970eeed4)
	- added return locals (rev.7898d67c)
	- returned locals (rev.6f88b7bf)



================================================================================
* Mon Dec 11 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.038

================================================================================
	- updated readme progress (rev.ddf77870)
	- first commit unit test 2 (rev.b9763556)
	- updated latest edit date (rev.bf61bda8)
	- updated todo list (rev.617453c5)
	- removed unneeded comment (rev.c49359ee)
	- checked against old versions and updated edit date (rev.88a98011)
	- checked against old versions and updated edit date (rev.69cf34a4)
	- checked against old versions and updated edit date (rev.e83f6f1c)
	- checked against old versions and updated edit date (rev.cb7df1ca)
	- checked against old versions and updated edit date (rev.ccf36523)
	- checked against old versions and updated edit date (rev.a6539d55)
	- checked against old versions and updated edit date (rev.7fe7c48b)
	- checked against old versions and updated edit date (rev.4056bafa)
	- checked against old versions and updated edit date, added badpix key (rev.c7985dc2)
	- checked against old versions and updated edit date (rev.8c57ba46)



================================================================================
* Tue Dec 12 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.039

================================================================================
	- corrected cal_drift_e2ds test (file was wrong) (rev.75fb592d)
	- first commit - copy of cal_drift_e2ds - in process of modifying - not tested (rev.86f44e92)
	- added global c constant, added create_drift_file, gauss_function, remove_wide_peaks, remove_zero_peaks, get_drift, pearson_rtest functions (not tested) (rev.18906337)
	- rearranged function aliases, added drift_peak function aliases (rev.c7dfcd00)
	- Change MeasureMinMax function name (rev.3a6a7258)
	- added append_source, append_sources, append_all methods to ParamDict (rev.4eb890ab)
	- changed doc string of measure_box_min_max (rev.c9adf323)
	- added drift constants (rev.2e919901)
	- Change MeasureMinMax function name (rev.2b4ef04d)
	- Change MeasureMinMax function name (rev.38268a4e)
	- cosmetic changes (rev.85cf09c4)
	- cosmetic changes (rev.da1f0d58)



================================================================================
* Wed Dec 13 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.040

================================================================================
	- rebuild pdf (rev.24a9d843)
	- updated todo list (rev.45e1681b)
	- updated progress in readme (rev.58ed8978)
	- added drift-peak plot to documentation figures (rev.bceacbe0)
	- added RV aliases (rev.1d46f75c)
	- corrected some code, added warning catch, added sigma_clip function, added drift_per_order and drift_all_orders functions (rev.48f63f0c)
	- added drift_peak plot, drift_plot_correlation_comp and working function (rev.309168c7)
	- added drift_peak constants (rev.985211df)
	- cosmetic change to logging (rev.7b98eeb0)
	- cosmetic change to logging (rev.a6d40faf)
	- added many sections (code finished - untested) (rev.cd05cbad)



================================================================================
* Thu Dec 14 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.041

================================================================================
	- rebuilt pdf (rev.18a6e49e)
	- updated drift_peak_exp_width function calls (rev.6f5b6ca9)
	- changed hardcoded width to width from constant in get_drift() (rev.80dfcbb3)
	- rebuilt pdf (rev.4e927aba)
	- added TOC page divider (rev.7254205c)
	- added caldriftpeak command (rev.f4ebeb7c)
	- added drift peak section and constants (rev.0fe450a8)
	- updated constants (rev.f329e7d6)
	- rebuilt pdfs (rev.73feaff8)
	- deep copy on speref in create_drift_file function, other modifications to correct errors (rev.50cea4c9)
	- corrected errors in drift_peak_plot_dtime_against_drift (rev.8c246d64)
	- added to change log (rev.5b3594f4)
	- added drift-peak constants (rev.9109f493)
	- fixes to cal_drift-peak - now works in gaussfit and non-gaussfit mode (rev.daa621da)



================================================================================
* Mon Dec 18 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.042

================================================================================
	- first commit (similar to cal_drift_e2ds) -- currently unfinished (rev.eaf7f411)
	- modified get_custom_from_run_time_Args function (Added for function arguments) to allow more functionality, commented old function (rev.e6284061)
	- added start of get_ccf_mask function (not finished) (rev.3f05c52c)
	- added alias to get_ccf_mask (GetCCFMask) (rev.e1a8c2ae)
	- added ability to define x and y in drift_plot_Selected_wave_ref (rev.62a0b4df)
	- added two cal_CCF constants (rev.a6cb1f61)
	- added dividers between sections 2.7 - 2.10 (rev.218ea716)
	- rebuilt pdf (rev.363e4e04)
	- rebuilt pdf (rev.6d51f662)
	- updated progress (rev.db2535f0)



================================================================================
* Tue Dec 19 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.043

================================================================================
	- need to finish code (rev.280eeeb5)
	- redefined wave getting (GetE2DSll) and added a micron mask checking section. Code unfinished (rev.8b64fc3b)
	- first commit added get_e2ds_ll, get_ll_from_coeffiecients, and get_dll_from_coefficients functions (rev.899ead8e)
	- first commit added GetE2DSll alias (rev.9bc24a1e)
	- need to finish coravelation function (rev.068de02e)
	- added get_ccf_mask function, added coravelation function (not finished) (rev.e25b85d9)
	- added to write_table, added read_table function, added update_docs function and call to function at end (rev.0f28b2d7)
	- modified read_wave_file (rev.c912464d)
	- added ReadTable alias (rev.d8f23f0e)
	- added keywords to use list (rev.5f54e7e3)
	- added cal_CCF keywords (input from WAVE_AB) (rev.6383a35a)
	- added GetKwValues alias to get_keyword_values_from_header (rev.e34b089e)
	- cosmetic changes to comments (rev.d17926c4)



================================================================================
* Wed Dec 20 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.044

================================================================================
	- temporarily put mask in bin folder (where does it go?) (rev.3b2c1e6e)
	- corrected mistakes in get_e2ds_ll (rev.5644fa1c)
	- added aliases for getll and getdll (rev.88215224)
	- added to coravelation function (not finished), added calculate_ccf function (not finished), added raw_correlbin function, added correlbin function (not finished) (rev.1b75eb5e)
	- added to coravelation function (not finished), added calculate_ccf function (not finished), added raw_correlbin function, added correlbin function (not finished) (rev.34b82448)
	- fixed error in read_table (with colnames != None) (rev.ce8f3bd8)
	- added keyword (rev.d661d302)
	- updated configerror error message (rev.d567d74d)
	- added constants (rev.03a38746)
	- added data to loc (rev.38f06af1)



================================================================================
* Thu Dec 21 2017 Neil Cook <neil.james.cook@gmail.com> - 0.0.045

================================================================================
	- added coravelation and sub functions, added ccf fit functions and misc functions (rev.a41a7397)
	- added aliases for coravelation and fitccf (rev.6756ad16)
	- added ccf plots (rev.758499e7)
	- added ccf keywords (rev.4326ae9b)
	- added ccf table and fits pseudo constants (rev.d5a58c9d)
	- added ccf constants (rev.7c7fea67)
	- unchanged (rev.ac39b8b2)
	- unchanged (rev.7645c023)
	- unchanged (rev.ced875e5)
	- added correlation sections - code finished but untested (rev.9469d308)
	- what (rev.ef59e7f1)



================================================================================
* Mon Jan 08 2018 Neil Cook <neil.james.cook@gmail.com> - 0.0.046

================================================================================
	- updated text for conversion from .txt to .py config files (rev.8599d12a)
	- added return_locals for debugging purposes (rev.7b68bd1f)
	- added aliases for unit_test_functions (rev.0ab2a2e3)
	- added/modified renamed functions for setup, changed errors that span multiple lines to list argument for logger (rev.b40fb70d)
	- added/modified renamed functions for setup (rev.1333edf1)
	- removed call to unused constant (update to V48) (rev.16b8ce45)
	- corrected change for update to V48 (rev.e8b7547d)
	- updated text for config files from .txt to .py conversion (rev.aef14645)
	- allow list log messages, coloured log messages, and launch debugger in DEBUG mode on error (rev.41cb8b44)
	- updated text for change of .txt config to .py (rev.6b2d438e)
	- added colour levels and debug pseudo constants (rev.83db977f)
	- fixed error with getting dictionaries from config files (rev.8073fac4)
	- rebuilt pdfs (rev.b636acb6)
	- added qc constants (rev.ba6c98cf)
	- converts to py file (but still read as text file) + added some qc constants (rev.2a07bb75)
	- converts to py file (but still read as text file) (rev.8e686208)
	- moved exit function to top, changed startup alias (rev.f747483e)
	- updated for V48 of old code (rev.baab8b92)
	- updated for V48 of old code (rev.59934047)
	- updated for V48 of old code (rev.9f8618fa)
	- modified startup functions (rev.895f5d92)
	- modified startup functions (rev.c169f4d5)
	- modified startup functions (rev.147b6e23)
	- modified startup functions (rev.5ac38da4)
	- added date and release type to codes for modules (rev.4f21c4c0)
	- added date and release type to codes for recipes (rev.c8d6a81e)
	- rebuilt pdfs after variables changes (rev.89980fab)
	- unit test 2 now uses unit_test_functions (rev.0558044a)
	- unit test 1 now uses unit_test_functions (rev.b8656874)
	- moved argument definitions of unit tests to functions file (can call from multiple files without having to update all) (rev.52f01223)
	- modified create_drift_file (V48 update) (rev.be5d71c7)
	- added fiber to 'WAVE' calib key (V48 update) (rev.6b90d21b)
	- added drift_peak_plot_llpeak_amps function (V48 update) (rev.ae423e94)
	- added calib_prefix const function (rev.d3e303b8)
	- updated descriptions of drift_peak variables (rev.c9735da1)
	- added and updated drift_peak constants (rev.f17d78cc)
	- added 'ALL' fiber type option and error if fiber_type is not understood (rev.647ac419)
	- updated to version 48 (untested) (rev.e99e28f2)
	- updated to version 48 (untested) (rev.24aa078a)



================================================================================
* Tue Jan 09 2018 Neil Cook <neil.james.cook@gmail.com> - 0.0.048

================================================================================
	- fixed import and removed cal_CCF (problem with code) from unit tests (rev.ec1fc6e1)
	- fixed import (rev.55f6dd42)
	- reformatted multi-line error message (rev.55ac4aff)
	- fixed comments (rev.253da234)
	- better dealing with calibDB file (rev.25d9c779)
	- rebuilt pdf (rev.26854c08)
	- overlhaul of define variable function (rev.ddcb74c0)
	- overlhaul of define variable function (rev.8946148e)
	- overlhaul of define variable function (rev.406bff63)
	- overlhaul of define variable function (rev.af950a92)
	- overlhaul of define variable function (rev.902460c7)
	- overlhaul of define variable function (rev.0199723f)
	- overlhaul of define variable function (rev.64768046)
	- overlhaul of define variable function (rev.6a6bf306)
	- overlhaul of define variable function (rev.4f597487)
	- overlhaul of define variable function (rev.2f9ffee0)
	- overlhaul of define variable function (rev.48a9912d)
	- overlhaul of define variable function (rev.043e73a4)
	- overlhaul of define variable function (rev.7db31494)
	- overlhaul of define variable function (rev.00b55d6a)
	- overlhaul of define variable function (rev.6b368938)
	- readded qc_max_signal, added calib_db_match constant (rev.7a79aa45)
	- placeholder for cal_WAVE (rev.e9544398)
	- placeholder for cal_HC (rev.e23755c8)
	- moved wave into fiber loop (now needs fiber) (rev.8f3c3315)
	- added calibdb prefix (from update to V48) (rev.21732594)



================================================================================
* Wed Jan 10 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.000

================================================================================
	- readded cal_CCF to unit test 2 (rev.66662730)
	- moved UrNe.mas to data folder (rev.121076ea)
	- added a locate_mask function - to local file if filename is not a valid path and found by os.path.exists, make ic_debug drs_debug==2 (rev.29ebf2a2)
	- make ic_debug drs_debug==2 (rev.35f5a86e)
	- corrected typo in debug plot (rev.a3a290a1)
	- added CDATA_FOLDER constant (rev.9d84dec3)
	- added get_relative_folder function (rev.7a0c328f)
	- added aliases to init (rev.6e1a4269)
	- added removal of lockfile in generated error (rev.8c2d7dfe)
	- make ic_debug drs_debug==2 (rev.fc3c9cf9)
	- rebuild pdf (rev.59fc9bc3)
	- added spaces to some commands (rev.9acb1687)
	- added listing style and tcolorbox to print out cmd prompt in colours red/yellow/green (rev.860ae25a)
	- added to variables (rev.0fecb3eb)
	- added to todo (rev.a87e81a5)
	- added coloured log section (rev.27892973)
	- change log updated (ccf update needs doing) (rev.3e2ba338)
	- debug mode explained in comments (rev.acde01c8)
	- moved file (rev.fa96b16c)
	- make ic_debug drs_debug==2 (rev.8905a171)
	- remove template logging (moved into spirouRv.GetCCFMask function (rev.dd2e15ac)
	- removed ic_debug and replaced with drs_debug (rev.e3aeffad)
	- removed ic_debug (replaced with drs_debug) (rev.c706a988)
	- added an option in debug_start to allow no coloured text (rev.fd7e5cfa)
	- changed order to allow reading of config file (to access certain parameters without running recipe) (rev.35436611)
	- first commit - config file reading (base level no drs imports allowed) (rev.4e0f6a6c)
	- moved config file reading to new code (rev.ec06e358)
	- removed ic_debug (now drs_debug) (rev.8b0147b2)
	- added input keyword chapter for user (rev.1e561dc6)
	- rebuilt pdfs (rev.5d90dbcd)
	- removed devguide if statements (rev.526b05ba)
	- created named label command (to allow linking to individual text via phantom sections) (rev.279beeeb)
	- changed label to namedlabel (rev.2a19436c)
	- changed label to namedlabel (rev.a123fe1e)
	- removed typo (rev.f07542d5)
	- changed label to namedlabel (rev.806a77cf)
	- changed label to named label (rev.544de58f)
	- made links to modules only for dev guide (rev.91a8b8ec)
	- modified variables (rev.c5dc8098)
	- made most of input keywords section devguide only (rev.c20058d2)
	- removed ic_debug constant (rev.37087141)
	- added drs_debug and coloured_log constants (rev.8b2582fc)
	- removed ic_debug and replaced with drs_debug (rev.2b65da53)
	- removed ic_debug and replaced with drs_debug (rev.07578ac4)



================================================================================
* Thu Jan 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.001

================================================================================
	- updated progress (rev.79a6807d)
	- fixed list not appending (rev.50af84cb)
	- first commit - comparison functions for old vs new test (rev.cafcba87)
	- added ability to test outputs (rev.6e388d75)
	- added aliases to utc (rev.428c23b7)
	- added fiber definition to fiber loop (rev.e8aa3738)
	- first commit unit_Test3 - testing the outputs (rev.30bb616a)
	- added output assignment to all unit tests (rev.ee7b2079)
	- added output filename functions, reordered functions for better clarity (rev.36c35558)
	- removed output filenaming to spirouConfig.spirouConst (rev.b9031c35)
	- removed output filenaming to spirouConfig.spirouConst (rev.e9b6f380)
	- removed output filenaming to spirouConfig.spirouConst (rev.050d3c17)
	- removed output filenaming to spirouConfig.spirouConst (rev.2aa57ae3)
	- removed output filenaming to spirouConfig.spirouConst (rev.ed3cd8d0)
	- removed output filenaming to spirouConfig.spirouConst (rev.5afc6f73)
	- added a question re fiber type for wave file (rev.96dbd962)
	- updated version (rev.e323c04b)
	- rebuilt pdfs (rev.765cb29f)
	- modified date and version (rev.03a63ad2)
	- added cdata_folder constant (rev.4d423390)
	- added spirouTHORCA placeholder section (rev.70c4024a)
	- added cal_CCF section (rev.4c9e14a0)



================================================================================
* Fri Jan 12 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.002

================================================================================
	- updated progress (rev.5e1004d0)
	- rebuilt pdf file (rev.f0d17f67)
	- updated todo list (rev.dcfe0195)
	- added fortran python conversion (for test purposes only) (rev.345383ef)
	- unignore fitgaus.so (rev.8a03c966)
	- added fitgaus.f (for test purposes only) (rev.e29ba8e2)
	- added comparison + tests + nanstats in order to pass or fail found errors (rev.460c4749)
	- set a threshold for order of magnitude difference (in comparison) (rev.2ff3bfe2)
	- added a test_fit_ccf to compare "fortran fit" with "python fit" (rev.e2c9fa61)
	- cosmetic comment fix (rev.3634cdb9)
	- added writeimage dtype fix (rev.a6155fd4)
	- added kw_drs_QC keyword (rev.40fa39d2)
	- cosmetic fixes (rev.b66680b2)
	- moved qc and fixed header bugs (rev.3173c9a9)
	- fixed badpixelfits error (rev.82410347)
	- added logs (rev.d29dae7c)
	- fixed header error (rev.73ebb940)



================================================================================
* Mon Jan 15 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.002

================================================================================
	- rotated speed table + rebuild pdf (rev.383892e8)
	- rebuilt pdf (rev.ca24d8cb)
	- rebuilt pdf (rev.b40a9de5)
	- updated python module versions (rev.8f30e191)
	- updated readme (quick manual out of date and useless - use pdfs) (rev.b93c6754)
	- updated dates and version (rev.3e4b5b7d)
	- updates architecture (rev.bdd42fb5)
	- cal_ccf fitting difference graph (rev.e8ea74db)
	- cal_dark graph 3 (rev.85af89ed)
	- cal_dark graph 2 (rev.f258c97b)
	- cal_dark graph 1 (rev.ad1418ee)
	- changed reporting of errors to "differences" (rev.87a3fd69)
	- first commit unit test including all current recipes (with comparison) + cal_drift_raw and cal_driftpeak_e2ds (rev.413e55bc)
	- updated name of unit test 3 (rev.c95fa118)
	- updated name of unit test 2 (rev.105aada7)
	- added new and old methods for calulating badpix normalisation constant (for testing purposes) (rev.f84c42a0)
	- changed location of TOC page break (rev.f747169b)
	- rebuilt pdf (rev.fcf4e7e3)
	- commented conflicting text (do not use memoir captions) (rev.ca4ca4ac)
	- added new packages (rev.da25e080)
	- added new constants (rev.d9b56bf3)
	- added named labels to some constants (rev.700188b9)
	- added calibdb section (unfinished) (rev.6531b77c)
	- updated todo list (rev.cdaeb057)
	- added caldark to recipes (rev.9cb2574f)
	- updated versions (rev.17a44032)
	- updated change log and moved around sections (rev.52a7ca44)
	- updated imports in placeholder file (rev.a4856a66)
	- updated imports in placeholder file (rev.39dfe770)
	- added reffilename to paramdict (rev.18733307)
	- added to log printing in qc (rev.609f6f07)
	- allowed norm median flat to be old or new method (rev.c1eb44d3)



================================================================================
* Tue Jan 16 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.003

================================================================================
	- Update README.md (rev.acc84ae2)
	- updated to alpha 0.1 (rev.b4c5dcb7)
	- rebuilt pdf (rev.f250d9d3)
	- rebuilt pdf (rev.ae2aba3e)
	- updated to alpha 0.1 (rev.0d843de9)



================================================================================
* Fri Jan 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.003

================================================================================
	- updated version and date (rev.a3a94774)
	- updated version and date (rev.8cabd5d7)



================================================================================
* Mon Jan 22 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.004

================================================================================
	- added test data link (rev.75d45d66)
	- link to logo change (rev.bc567090)
	- rebuilt pdfs (rev.feeda88e)
	- updated version (rev.bb97143f)
	- added spacing to constants (rev.6c435337)
	- changed the cmd code boxes (rev.f18944d4)
	- added a general section (rev.01f2cd3d)
	- removed definevariablecmd variables (rev.e109964f)
	- added some namedlabels (rev.753e5f78)
	- fixed typo in log message (rev.443db7f2)
	- updated readme (rev.961b0e06)
	- updated date and rebuilt (rev.bc7b9a30)
	- added quick install chapter (rev.ee72ccc7)
	- updated date + version (rev.33de1c98)
	- rebuild pdfs (rev.d75b2bb2)
	- updated version (rev.59ac4722)
	- unchanged (rev.6b339b9e)
	- updated dirs (rev.e919a08c)
	- fixed errors (rev.010f2579)
	- rebuilt pdf (rev.72cb00e8)
	- updated log colourring (rev.67bc0aec)
	- updated paths (rev.81824f31)
	- added readme files (rev.4f474da3)
	- Added example data readme files (rev.c1b7bb44)
	- Added calibDB minimum files (rev.7c8893ea)
	- Restructure of drs file (rev.e090f1d6)
	- rebuilt pdfs (rev.02535b50)
	- updated version (rev.7e6a6942)
	- added spacing to constants (rev.8ed95903)
	- changed the cmd code boxes (rev.80227183)
	- added a general section (rev.6204bc3e)
	- removed definevariablecmd variables (rev.bc1a89af)
	- added some namedlabels (rev.21c914a1)
	- fixed typo in log message (rev.0cb281a4)
	- updated readme (rev.8f96465e)
	- updated date and rebuilt (rev.5cce41a2)
	- added quick install chapter (rev.b230a4cd)
	- updated date + version (rev.b20bf42b)
	- rebuild pdfs (rev.7285b2d3)
	- updated version (rev.3a35534e)
	- unchanged (rev.3a8e5094)
	- updated dirs (rev.d54984cc)
	- fixed errors (rev.c0366c22)
	- rebuilt pdf (rev.32be9ae5)
	- updated log colourring (rev.fabdfa01)
	- updated paths (rev.4a4bf982)
	- added readme files (rev.a955db5c)
	- Added example data readme files (rev.4853b576)
	- Added calibDB minimum files (rev.1b384e3c)
	- Restructure of drs file (rev.f5a0389f)



================================================================================
* Tue Jan 23 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.004

================================================================================
	- first commit of quick install guide (rev.67a6e76c)
	- added DARK_CUTLIMIT to keyword used variables, added a hack to avoid not having config file ICDP_NAME (will complain elsewhere) (rev.c03cfd81)
	- added DARK_CUTLIMIT to keyword used variables, added a hack to avoid not having config file ICDP_NAME (rev.c67e8798)
	- added logic for quick install guide (false) (rev.df83937d)
	- rebuilt pdfs (rev.7ce8bfd5)
	- fixed installDIR (rev.033c6443)
	- sorted out environment paths (rev.9c76bbe0)
	- sorted out environment paths (rev.142e45e7)
	- fixed debug mode (rev.8714d644)
	- fixed comment (rev.50ab14ad)
	- fixed init __all__ call (rev.32c5044e)
	- editted log to print message even if we cannot log to file (rev.f4d042fa)
	- updated version and latest edit date (rev.070ff8c4)
	- added additional way to read config file (slow using python open) or give good error message if cannot open (rev.a0c0498e)
	- allowed ConfigError "message" to take list as input (rev.68b77657)
	- streamlined config strings (rev.94e0c02e)
	- streamlined config strings (rev.df40f982)
	- fixed error with DRS_NAME, DRS_VERSION (rev.06a433a0)



================================================================================
* Wed Jan 24 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.005

================================================================================
	- update versions + date (rev.6da670b0)
	- rebuild pdfs (rev.74b89c6b)
	- version + date update (rev.17d3c7ed)
	- updated __all__ (rev.3757c147)
	- added to warninglogger (funcname), changed end card colour (rev.bbe1b24c)
	- added warnlog alias (rev.5b777d2b)
	- better error handling + reporting (rev.a1d19964)
	- better error handling + reporting (rev.00ac755d)
	- better error handling + reporting (rev.2599e410)
	- better error handling + reporting (rev.e89a8a45)
	- better error handling (rev.466fea09)
	- doc strings added (rev.f854746b)
	- doc strings added (rev.aee90c5d)
	- warnings added, better error handling (rev.a5c521df)
	- update of code (rev.6e6777cd)
	- config param change (debug mode active) (rev.30c38d45)
	- submodule clean up and doc string writing (rev.3cace1d5)



================================================================================
* Fri Jan 26 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.006

================================================================================
	- added test help file - for cal_DARK_spirou (rev.bfc5145d)
	- updated todo list with help files that are needed (rev.c523c278)
	- update doc strings (rev.67bb1fa4)
	- update doc string (rev.5f478ec4)
	- update doc strings + help file management (rev.d2ab9020)
	- update doc strings (rev.e39cecd5)
	- update doc strings (rev.b8f23c84)
	- update doc strings (rev.1b8c9d28)
	- update doc strings, remove __main__ (rev.84519442)
	- update doc strings (rev.3e549bdf)
	- update doc strings (rev.a8ffda9e)
	- update doc strings (rev.f98675dd)
	- update doc (rev.093b2502)
	- rebuild pdfs (rev.12a2cacd)
	- update todo list with man files need writing (rev.a97dfb9f)
	- modified MANUAL FILE (corrected) (rev.16f73fee)
	- updated date and version (rev.5c595db2)
	- rebuild pdf (rev.b18ac708)
	- rebuild pdf (rev.3a9e5374)
	- rebuild pdf (rev.a18bbf12)
	- updated the date and version numbers (rev.d6fbcbdd)
	- added/corrected some cal drift variables (rev.12faac86)
	- added descriptions (rev.b2559c32)
	- added doc string for sPlt (rev.4e5c76ba)
	- added constant for drift peak (rev.065754e4)
	- fixed plotting function calls (rev.11cc2130)
	- updated descriptions (UNFINISHED) (rev.3f9653d9)
	- updated descriptions and unix/string time getting (rev.cb757d04)
	- updated descriptions and unix/string time getting (rev.72b0f8e0)
	- added doc strings + math time functions (rev.09b12869)
	- added more formats (defaults + log), removed main code (rev.aa9f08f8)
	- updated config error (rev.7d2cc7be)
	- updated descriptions and unix/string time getting (rev.2227bb57)



================================================================================
* Mon Jan 29 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.007

================================================================================
	- rebuild pdf (rev.59a89669)
	- rebuild pdf (rev.813f0e3e)
	- rebuild pdf (rev.fd3f4010)
	- updated versions + dates (rev.06bccd7e)
	- updated versions + dates (rev.1a41c8e3)
	- updated versions + dates (rev.609e9ad3)
	- doc strings and error handling (unfinished) (rev.522765c2)
	- doc strings and error handling (unfinished) (rev.a54bfb06)
	- doc strings and error handling (rev.ae32943c)
	- updated doc strings [unfinished] (rev.a5d5ceaa)



================================================================================
* Tue Jan 30 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.008

================================================================================
	- added spacing (rev.371ff5c7)
	- edit of doc string (unfinished) (rev.5915848c)
	- create DEFAULT_LOG_OPT() from sys.argv[0] (rev.7beb86dc)
	- replace sys.argv[0] in logs with spirouConfig.Constant.DEFAULT_LOG_OPT() (rev.140e5724)
	- added doc strings, moved gaussian function and added some error handling (rev.4dd3650d)
	- moved gaussian function here (rev.60649ae6)
	- added doc strings (rev.c8327896)
	- added doc strings (rev.071dc967)
	- corrected error "mean_background" --> "mean_backgrd" (rev.52cf31a9)
	- updated back to my data folder (rev.d8e4b37c)
	- rebuild pdfs (rev.a30fc285)
	- updated version (rev.6f0a6c97)
	- updated doc_strings and error handling (rev.6b535bb7)
	- updated doc_strings and error handling (rev.3a02a370)
	- updated doc_strings (rev.fbdc9998)
	- updated version and date (rev.71afb0da)
	- updated version and date (rev.f33d092e)
	- added badpix_norm_percentile constant constant (rev.d29027a5)
	- added badpix_norm_percentile constant constant (rev.9a6729b0)



================================================================================
* Wed Jan 31 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.009

================================================================================
	- updated doc strings (rev.131092f2)
	- updated doc strings (rev.f03e5f94)
	- updated doc strings (rev.5e0bb329)
	- removed doc strings + added __all__ functions (rev.07593ad1)
	- removed doc strings (rev.94cfb821)
	- removed doc strings (rev.80533a85)
	- removed doc strings (rev.4b43f426)
	- removed doc strings (rev.990c5bdd)
	- removed doc strings (rev.ae7a0898)
	- removed doc strings (rev.e50b6024)
	- removed doc strings (rev.94ed6876)
	- removed doc strings (rev.afdec8cc)
	- removed doc strings (rev.8b1c3e01)
	- removed doc strings (rev.c68f231f)
	- removed doc strings (rev.e4fda83f)
	- rebuilt pdfs (rev.f022bc03)
	- updated date and version (rev.25204427)
	- updated todo list (rev.065e5f30)
	- cosmetic change to comment (rev.fffc49e7)



================================================================================
* Thu Feb 01 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.010

================================================================================
	- updated doc strings with parameter dictionary descriptions (rev.ad5807d1)
	- updated doc strings with parameter dictionary descriptions (rev.0f489a32)
	- rebuild pdf (rev.7403cd99)
	- rebuild pdf (rev.29f9c768)
	- rebuild pdf (rev.1b734e18)
	- updated date and version (rev.8627158a)
	- updated date and version (rev.2679fe54)
	- add res to loc (for debug_locplot_fit_residual) (rev.7ef80b61)
	- update doc string (p and loc) (rev.a1fda7b6)
	- update doc string (p and loc) (rev.9566a8a2)
	- update doc string (p and loc) (rev.b3eb87ea)
	- updated doc strings (rev.37c2fa1a)
	- update doc string (p and loc) (rev.4c97287d)



================================================================================
* Fri Feb 02 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.011

================================================================================
	- first commit - module tex file (rev.ef5dc038)
	- first commit - module tex file (rev.e97eed88)
	- first commit - module tex file (rev.81b40ca1)
	- first commit - module tex file (rev.8c1327ca)
	- edited doc string (rev.12c29f69)
	- rebuild pdf (rev.7ecffe2f)
	- changed size of subsubsection (rev.c897b502)
	- added new package (rev.d3cd420a)
	- added docstring tcbox (rev.40f156df)
	- changing format input module tex files (rev.4139953e)
	- updated doc strings with parameter dictionary descriptions (rev.ea643575)
	- updated doc strings with parameter dictionary descriptions (rev.15b5ed0f)
	- updated date and version (rev.18537ca3)
	- rebuild pdf (rev.a5462b5d)
	- rebuild pdf (rev.23e2089e)
	- rebuild pdf (rev.b1bd0fc8)
	- updated latest edit and version (rev.76acdcb1)
	- updated some constants descriptions (rev.ba05fab5)



================================================================================
* Mon Feb 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.012

================================================================================
	- added spirouRV and spirouTHORCA imports to init (rev.082b9e6b)
	- started updating doc strings (p and loc) [unfinished] (rev.fe60a847)
	- started updating doc strings (p and loc) [unfinished] (rev.dfd693c2)
	- updated date and version (rev.38ebdb55)
	- started module writing (incomplete) (rev.2b96d5e8)
	- rebuilt pdf (rev.4db05680)
	- added inputs (rev.f07d5b07)
	- updated imports (rev.e82e88f6)
	- removed unneeded comment for alias (rev.7af73ca5)
	- modified some doc strings (rev.b1831265)
	- refactored "imageLocSuperimp" --> "ImageLocSuperimp" (rev.61481951)
	- modified comments for several functions (more concise) (rev.47fb7634)
	- modified doc_string for writeimage (rev.0d93a215)
	- modified doc_string for warninglogger (rev.b3858a77)
	- added to __all__ (rev.bf43b4b8)
	- modified get_keywords doc_string (rev.35958704)
	- added doc strings for ConfigError methods (rev.6924457c)
	- first commit - added doc strings + sub-module func descriptions (based on spirouBLANK.tex) (rev.159556a9)
	- first commit - added doc strings + sub-module func descriptions (based on spirouBLANK.tex) (rev.421e5f41)
	- first commit - added doc strings + sub-module func descriptions (based on spirouBLANK.tex) (rev.beccc2c5)
	- first commit - added doc strings + sub-module func descriptions (based on spirouBLANK.tex) (rev.316b7d9d)
	- first commit - added doc strings + sub-module func descriptions (based on spirouBLANK.tex) (rev.69a06742)
	- first commit - added doc strings + sub-module func descriptions (based on spirouBLANK.tex) (rev.9a5742fd)
	- rebuilt pdf (rev.be1d67d7)
	- changed subsection and section size in nav bar menu (rev.70382ff7)
	- added spirouCore and spirouFLAT to constants , modified paths for WLOG, ParamDict and ConfigError (to module file) (rev.287ee719)
	- added blue to the special cmd colours (rev.dc7e3fe9)
	- added introduction (rev.044af1d5)
	- added doc strings (rev.cc9495c8)
	- changed default module tex file template (rev.939c7ece)
	- refactor imageLocSuperimp --> ImageLocSuperimp (rev.e4a6dbc2)



================================================================================
* Tue Feb 06 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.013

================================================================================
	- first commit module description for thorca (rev.4ac8d4c8)
	- first commit module description for startup (rev.8ae1ae79)
	- updated doc strings with p and loc descriptions (rev.13e1ab87)
	- updated doc strings with p and loc descriptions (rev.8f4ca51d)
	- updated doc strings with p and loc descriptions (rev.09a23800)
	- updated wave to wave_ll (rev.98d2a9ae)
	- rebuild pdf (rev.03151b66)
	- added startup and THORCA (rev.aec75029)
	- added doc strings to RV tex file (rev.142a95a7)
	- changed wave to wave_ll in loc (rev.a7e418a6)



================================================================================
* Wed Feb 07 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.014

================================================================================
	- first commit - move recipe to individual file (rev.1be8fc10)
	- first commit - move recipe to individual file (rev.b73ca5d7)
	- first commit - move recipe to individual file (rev.d67fd73e)
	- first commit - move recipe to individual file (rev.41c1106b)
	- first commit - move recipe to individual file (rev.1e74f230)
	- updated date and version (rev.c8b6e253)
	- rebuilt pdf (rev.dfcef155)
	- rebuilt pdf (rev.b8a714cc)
	- rebuilt pdf (rev.4c471343)
	- updated date and version (rev.6ae440ef)
	- updated the highlight parameters for doc string (rev.4ee8a4d6)
	- moved individual recipes to indivudal files (rev.18a3c4e7)



================================================================================
* Fri Feb 09 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.015

================================================================================
	- rebuilt pdfs (rev.d03418f4)
	- moved calibration database loading to separate function (for custom arg recipes), tweaked functions accordingly, added getting of multi arguments (as last param) + wrapper around get_file (get_files) (rev.ba325a46)
	- added new aliases (rev.267e479f)
	- tweaked readimage_and_combine and math_controller to be more generic (rev.c92a0273)
	- removed Config Error from messages (shouldn't be an error unless error=error) (rev.626b385c)
	- added to custom arg section + added setup summary (rev.28a3104d)
	- added/edited section (rev.0342322e)
	- rewrote section (rev.613c5b41)
	- edited/updated doc strings (rev.4f85e798)
	- edited/updated doc strings (rev.a6e35069)
	- designed basic layout (setup + sections) (rev.c14d072c)
	- updated ghost template (rev.efb5fcd3)
	- added loading of calibDB (rev.386ce7f6)
	- update date and version numbers (rev.5da0644b)
	- rebuilt pdfs (rev.d28c6f4c)
	- updated TILT and WAVE fixes (with todo) (rev.2f989eb2)
	- updated todolist (rev.e0b16fe0)
	- added indents to minipages, added alias/internal function definition (rev.1ae00c5b)
	- added titles to some code boxes (rev.ee13b974)
	- added titles to some code boxes (rev.008dd9b2)
	- added titels to some code boxes, changes paths for print outputs (rev.0456d1bb)
	- added some new packages to dependencies, added that custom args can be added to code boxes (rev.11edda36)
	- added recipe and module reference sections and some titles for calibDB text file examples (rev.a8ee4def)
	- changed a bashbox to a cmdbox (rev.c049784c)
	- added example of addition to calibration database (rev.a31546a4)
	- updated indentation of minipages (rev.64f79f48)
	- updated indentation of minipages (rev.42f03e61)
	- updated indentation of minipages (rev.d9d58847)
	- updated indentation of minipages (rev.0cb4a400)
	- updated indentation of minipages (rev.b15aa6fd)
	- updated indentation of minipages (rev.cf023fb2)
	- updated indentation of minipages (rev.405e10bb)
	- updated indentation of minipages (rev.e0d9d6fe)
	- updated indentation of minipages (rev.2608e129)
	- updated indentation of minipages (rev.9e0fd22d)
	- updated indentation of minipages (rev.54300cfb)
	- updated indentation of minipages (rev.2c057efd)



================================================================================
* Mon Feb 12 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.016

================================================================================
	- rebuilt pdf (rev.5b6c6cd4)
	- rebuilt pdf (rev.dabdc2d7)
	- rebuilt pdf (rev.ecc543a5)
	- updated date and versions (rev.8f13710b)
	- updated date and versions (rev.28c900ad)
	- fix for only one file name in readimage_and_combine (rev.7b1f62a1)
	- changed rawfits to orderpfile (name change) (rev.c7509208)
	- rebuilt pdfs (rev.1501dbf0)
	- change back to doc class comment (rev.d54c98cd)
	- change to doc class? (rev.a64eaa58)
	- made cmdboxprintspecial breakable (rev.ba027578)
	- added some named labels and some new file names (rev.4aad15ee)
	- input calloc (rev.62a873bb)
	- edited receipe (rev.a4ea98fc)
	- edited receipe (rev.285d1c39)
	- edited receipe (rev.d329c6eb)
	- edited receipe (rev.13a36997)



================================================================================
* Tue Feb 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.017

================================================================================
	- cal loc figures (rev.18ab194e)
	- windows environment figures (rev.b5d3e36d)
	- display system info, moved header bar to a constant (rev.fde10252)
	- modified logger to accept printonly and logonly inputs (rev.1efe68fc)
	- updated version and date (rev.28fcc2c7)
	- changed the windows installation section (rev.ef67be32)
	- rebuild pdf (rev.821ca24a)
	- modified end of code section to reflect changes (rev.b5fe1fbb)
	- modified doc string for logger (rev.6ca2acee)
	- updated shebang, added exit_script dealing with interactive sessions in __main__ call (rev.54ff427f)
	- updated shebang (rev.433f7a6f)
	- updated shebang (rev.96489dad)
	- updated shebang (rev.d50cb731)
	- updated shebang (rev.bbdd5980)
	- updated shebang (rev.9ac3bce0)
	- updated shebang (rev.5e7fa34b)
	- updated shebang (rev.a0c1ea8a)
	- updated shebang (rev.f09e848d)
	- updated shebang (rev.d17c83ee)
	- updated shebang (rev.7b93caaa)
	- updated shebang (rev.d971ba07)
	- updated shebang (rev.c0df4add)
	- updated shebang and __main__ exiting (rev.9d2c08f4)
	- updated shebang and __main__ exiting (rev.53cb9e9a)
	- updated shebang and __main__ exiting (rev.6c2fe656)
	- updated shebang and __main__ exiting (rev.34032ea1)
	- updated shebang (rev.90a9c31d)
	- updated shebang and __main__ exiting (rev.fee151c8)
	- updated shebang and __main__ exiting (rev.b92b907d)
	- updated shebang and __main__ exiting (rev.269498e2)
	- updated shebang and __main__ exiting (rev.ad61d01b)
	- updated shebang and __main__ exiting (rev.21fd090b)
	- updated shebang and __main__ exiting (rev.c7ad4044)
	- updated shebang and __main__ exiting (rev.432c0af2)
	- updated shebang and __main__ exiting (rev.6bc9ff44)
	- updated shebang and __main__ exiting (rev.053be262)



================================================================================
* Wed Feb 14 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.018

================================================================================
	- cal_slit graphs (rev.58900187)
	- cal_slit graphs (rev.c92ef488)
	- cal_slit graphs (rev.e233a29f)
	- first commit - recipe for cal_slit_spirou (rev.79654229)
	- added labels to slit plot (were missed before) (rev.b3f642ed)
	- rebuilt pdf (rev.189b5a7b)
	- rebuilt pdf (rev.a15f049e)
	- rebuilt pdf (rev.62bfaace)
	- updated date and version info (rev.235a5038)
	- updated date and version info (rev.8ad8005e)
	- commented TOC separator (may use later to clean up) (rev.58eac89a)
	- removed TOC separator (rev.55406338)
	- removed use of caption in favour of capt-of (screwdriver vs hammer) (rev.a435c2ce)
	- added some named labels, fixed typo namdlabels --> namedlabels (rev.36160d1f)
	- added calslit include (rev.551b16b1)
	- added labels to sections (rev.b44a5c14)
	- corrected errors in windows sections (ref links) (rev.d1b91609)
	- addede Interactive mode section (rev.def95e89)
	- fixed program call typo and ref to \calDARK (rev.beebb7bd)
	- fixed subsection title and some paths (rev.ecbae968)



================================================================================
* Thu Feb 15 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.019

================================================================================
	- corrected need for mainfitsfile to define arg_file_names and fitsfilename (rev.318323b2)
	- corrected doc string typo (rev.045f730a)
	- added return_header/return_shape options to readdata function, corrected readrawdata function (rev.92ffce73)
	- first commit of telluric mask file (currently a pseudo-recipe) (rev.daa23866)
	- updated doc strings (rev.ff39d811)
	- changed typo and updated some doc strings (rev.48bdfae9)
	- fixed needing mainfitsfile for custom files (rev.93a5a38f)
	- fixed needing mainfitsfile for custom files (rev.9b9984ce)
	- updated edit date and version (rev.4f1d9064)
	- updated edit date and version (rev.43467aaf)
	- added calff (rev.65cf7152)
	- first commit - blank cal_ff recipe (rev.4b6ae89b)
	- added package descriptions (from CTAN) (rev.5e6b648c)
	- updated keys (missed order_profile) (rev.1aeb507c)



================================================================================
* Fri Feb 16 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.020

================================================================================
	- Update README.md (rev.db0b0fb7)
	- rebuilt pdfs (rev.a9efbac4)
	- added current default files (for reset) (rev.9314f5ac)
	- first commit - a reset switch - setting DRS back to default (rev.f53c8113)
	- added mainfitsdir for when we are using custom arguments, resorted functions, added get_custom_arg_files_fitsfilename to deal with setting arg_file_names and fitsfilename with custom arguments (rev.50b1711f)
	- fixed problem with plot (wave_ll only for CCF - so use x instead) normally want "wave" (rev.3d61e265)
	- moved log_file_name getting to constants file (rev.60dc1d60)
	- added log_file_name to constants (rev.203f548e)
	- fixed bug for arg_file_names from custom args (rev.8919b7c7)
	- updated doc string (rev.507685a2)
	- added mainfitsdir for custom loadarguments (rev.33878b55)
	- rebuilt pdf (rev.3922b881)
	- readded cal_slit plots for interactive sessions (accidentally overwritten) (rev.d1c88821)
	- readded cal_FF_raw plots for interactive sessions (rev.801fab64)
	- added cal_FF_raw plots for interactive sessions (rev.082952fc)
	- rebuilt pdfs (rev.9894106a)
	- added cal_FF_raw file definitions (rev.1dea8e83)
	- updated cal_FF_raw change log (rev.f25133c6)
	- fixed errors in default recipe (rev.98d91bca)
	- added paths for example files, fixed example run (rev.0d4d55a0)
	- added paths for example files (rev.6422fce2)
	- added all sections (previously empty) (rev.5c137284)
	- added paths for example files (rev.3bf4a9b0)
	- added path for example file (rev.ec8f6ec0)
	- updated date and version (rev.87de6fc4)
	- updated date and version (rev.f8d28d39)
	- replace use of log_opt (not valid in load_arguments) with DPROG (Defaults to sys.argv[0]) (rev.cc000293)
	- renamed GetKwValues to GetKeywordValues (rev.2cbfbe4a)
	- renamed GetKwValues to GetKeywordValues (rev.f564266d)
	- renamed GetKwValues to GetKeywordValues (rev.2f91faf4)
	- added blaze to calibDB (rev.641b7773)



================================================================================
* Mon Feb 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.021

================================================================================
	- rebuilt pdfs (rev.e9218105)
	- rebuilt pdfs (rev.cd0941d2)
	- rebuilt pdfs (rev.9543f880)
	- added extract figure (rev.53800dab)
	- added extract figure (rev.89be6889)
	- added extract figure (rev.391ee2db)
	- first commit of verify recipe section (rev.e4df2fb8)
	- first commit of extract recipe section (rev.00267e3c)
	- added ReadBlazeFile (rev.074d2343)
	- updated doc strings and minor code fixes (for no header in writeimage) (rev.99e9deab)
	- updated date and versions (rev.afd1a6cd)
	- added function to convert waveimage to interpretted spectrum (rev.2a88d160)
	- updated date and version (rev.c0173dc3)
	- added extract file variables (rev.65ddc806)
	- changed order + added input for extract and validate (rev.1ca0f9a6)
	- changes to example code run (rev.88e367e7)
	- changes to example code run (rev.2ec309be)
	- fixed cmdbox typo (rev.86a515c6)
	- changed some doc strings (rev.4dce989c)
	- changed comment (rev.7d3e4570)



================================================================================
* Tue Feb 20 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.022

================================================================================
	- major changes to code (rev.1286cef0)



================================================================================
* Wed Feb 21 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.023

================================================================================
	- cal drift raw plot files for docs (rev.50a96877)
	- cal drift raw plot files for docs (rev.252d81b0)
	- cal drift e2ds plot files for docs (rev.82a81476)
	- cal drift e2ds plot files for docs (rev.92909e6a)
	- first commit - cal drift recipe (unfinished) (rev.d399ab68)
	- updated quick todo list (rev.686d3de1)
	- moved the arg_file_name/fitsfilename setting when we have custom args to after we read from runtime (rev.ba8f046c)
	- updated date and versions (rev.59515c1a)
	- rebuilt pdf (rev.a1336dbb)
	- rebuilt pdf (rev.2c169f87)
	- rebuilt pdf (rev.20e25e62)
	- updated date and versions (rev.940cc292)
	- added drift filenames (rev.dff6302b)
	- updated todo list (rev.791c150a)
	- input the caldrift section (rev.a84123f7)
	- fix for loadcalibdb (rev.fe3f6aac)
	- fix for loadcalibdb (rev.2e423146)



================================================================================
* Thu Feb 22 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.023

================================================================================
	- take some things out loop to speed up (rev.8c2e72e2)
	- fixes to tilt above and below central fit (untested) (rev.8ad1ac12)
	- moved setting of fitsfilename and arg_file_names (when files is not None) to a separate function to deal with run time vs call (rev.113a2ebd)
	- moved some constants outside a loop (rev.d8a1bf02)
	- added cal driftpeak figure (rev.858ac645)
	- added cal driftpeak figure (rev.d8caa4bd)
	- added cal driftpeak figure (rev.f5f9f761)
	- added cal driftpeak figure (rev.67760659)
	- rebuilt pdf (rev.9fe622e8)
	- rebuilt pdf (rev.87e64be5)
	- rebuilt pdf (rev.9ff39159)
	- updated the versions and date (rev.636d20b4)
	- updated the versions and date (rev.0ad3bb22)
	- updated examples and interactive mode figures (rev.ec9a650a)



================================================================================
* Fri Feb 23 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.024

================================================================================
	- rebuilt pdf (rev.24be377e)
	- rebuilt pdf (rev.f48dda6d)
	- rebuilt pdf (rev.0ba9a5e6)
	- cal ccf figure 3 (rev.89119812)
	- cal ccf figure 2 (rev.c48e74e8)
	- cal ccf figure 1 (rev.4c2a06a8)
	- first commit of cal ccf recipe doc (unfinished) (rev.9eba0d18)
	- updated reffile to e2ds file (rev.dee072e3)
	- updated date and version (rev.f3340484)
	- first commit - new faster version of telluric mask generation - using polyderivatives (rev.ca929c40)
	- updated telluric 2d mask (rev.25a15a50)
	- updated date and version (rev.959061a5)
	- added ccf filenames to variables (rev.1f3ae4cc)
	- added calccf recipe to inputs (rev.8a2ff091)
	- changed reffile to e2dsfile (rev.f4e424b4)



================================================================================
* Mon Feb 26 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.025

================================================================================
	- small fixes to refix pep8 across module/suppressing known and required pep8 exceptions (rev.b1d1bb33)
	- pep8 fixes (rev.ff9485a8)
	- pep8 fixes (rev.8d8b1f52)
	- pep8 fixes (rev.7f90a93b)
	- pep8 fixes (rev.404e3269)
	- pep8 fixes (rev.11e22359)
	- pep8 fixes (rev.47805ef0)
	- pep8 fixes (rev.bb353d03)
	- pep8 fixes (rev.9c7a4192)
	- pep8 fixes (rev.02a298d4)
	- pep8 fixes (rev.f73953f6)
	- pep8 fixes (rev.a8d09d14)
	- pep8 fixes + doc strings (rev.b08cdde3)
	- rebuilt pdfs (rev.16533d36)
	- updated date and version (rev.2bf8c68d)
	- added summary of properties and graphs section (rev.f05c45e9)
	- pep8 fixes (rev.f43ca0fa)
	- pep8 fixes (rev.bcc3ad02)
	- pep8 fixes (rev.b943776c)
	- pep8 fixes (rev.f1355a27)
	- pep8 fixes (rev.61bc3dd5)
	- pep8 fixes (rev.10175e8a)
	- pep8 fixes (rev.b8098050)
	- pep8 fixes (rev.4842512c)
	- pep8 fixes (rev.1375150b)



================================================================================
* Tue Feb 27 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.026

================================================================================
	- changed printing in function + added warning that user will reset all processed files (rev.fc147009)
	- changed printing in function (rev.2bdd985a)
	- changed display_title function (rev.3c0f2fda)
	- modified printlog function and added printcolour function (rev.66d9a948)
	- added printlog and printcolour aliases (rev.b5dd464d)
	- added dependencies and updated latest versions of py modules (rev.b39cbb75)
	- added printlog and printcolour functions (rev.021c88f4)
	- tweaked display title (rev.c3c90f66)
	- rebuilt pdfs (rev.e253428b)
	- fixed bug: set_souce -> set_source (rev.19aa0ebb)
	- updated date and version (rev.848db5b8)
	- minor text change (rev.1093a946)
	- corrected cal_loc example and call (rev.2adf6df4)
	- update date and version (rev.e8c67dcf)
	- add get_folder_name function and fix file name of comparison results file (name it by input program) (rev.041f5ab9)
	- update test comparison dir (rev.5314d19c)
	- update test comparison dir (rev.439ec41f)
	- same? (rev.37538970)
	- first commit - get dependencies for the drs (and current versions) (rev.c57f6e98)
	- added source to arg_file_names, nbframes and fitsfilename (rev.53ca3630)
	- corrected BIG bug (NBframes not redefined when arg_file_names redefined) (rev.77addafc)
	- corrected error statement (format missing) (rev.503dd296)
	- support astropy < 2.0.1 bug in astro.io.fits hdu.scale (this fixes it) (rev.5372445a)
	- updated plot imshow should not take True and False array (convert to ints) (rev.603a5d19)
	- removed use of tqdm (unnecessary dependency) (rev.785dcab4)
	- added new page preak for TOC (rev.10e742aa)
	- example - slight change to format (rev.0c763e33)



================================================================================
* Wed Feb 28 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.026

================================================================================
	- updated pep8 fixes + added sys info (rev.8e180f80)
	- updated display_title and display_system_info doc strings (rev.75ad919a)
	- added DisplayTitle and DisplaySysInfo aliases in __init__ (rev.3e6b2e85)
	- rebuilt pdf (rev.1e8744bb)
	- rebuilt pdf (rev.386785d7)
	- rebuilt pdf (rev.c788a296)
	- updated dependencies with python versions (rev.96de32e9)
	- added DisplayTitle and DisplaySysInfo to spirouStartup public functions (rev.c13b859c)
	- twaeked import (rev.f3d7831c)



================================================================================
* Thu Mar 01 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.027

================================================================================
	- rebuilt pdfs (rev.6f83105f)
	- updated tabbing in TOC (rev.f9889498)
	- updated versions and dates (rev.af952e7b)
	- modified initial_file_setup to include a "contains" keyword, to make sure all files (arg_file_names) contain this substring if contains is not None (rev.e735772c)
	- rebuilt pdfs (rev.2f4a0f29)
	- added description (rev.4ead02d6)
	- added chagnes to initial_file_steup (rev.685815e6)
	- added placeholder sections and added setup and exit sections (rev.c28f2206)
	- modified recipe description (rev.e0198d58)
	- modified recipe description (rev.9c0e7d51)
	- modified recipe description (rev.d21f4e9a)
	- modified recipe description (rev.7ee3c6d5)
	- modified recipe description (rev.341ed605)
	- modified recipe description (rev.cdd4c976)
	- modified recipe description (rev.f8a7cede)
	- modified recipe description (rev.ed5c33a9)
	- modified recipe description (rev.bf50bca7)
	- modified recipe description (rev.929fbd1c)
	- modified recipe description (rev.36bb39c9)



================================================================================
* Fri Mar 02 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.027

================================================================================
	- updated unit test - py2 error is valueerror not importerror (rev.6df430ac)
	- updated unit test - py2 error is valueerror not importerror (rev.fa3040e4)
	- updated unit test - py2 error is valueerror not importerror (rev.2257be17)
	- updated unit test - py2 error is valueerror not importerror (rev.abd53edf)



================================================================================
* Tue Mar 06 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.028

================================================================================
	- added note about using texteidter and smart speechmarks (rev.f5728b83)
	- fixed importing issues (rev.40738a32)
	- fixed importing issues (rev.cd21256c)
	- fixed importing issues (rev.ae4d2413)
	- fixed importing issues (rev.ffee4e02)
	- updated date and version (rev.728f3918)
	- rebuilt pdf (rev.aa72f463)
	- rebuilt pdf (rev.bb64f5cb)
	- rebuilt pdf (rev.c526a52b)
	- updated date and version (rev.8e9e803c)
	- updated dependencies (rev.797d22fe)
	- added a test of text file having bad (illegal) characters (non letters, punctuation, whitespace, digits) as defined by python string module (rev.f0d9dac7)
	- added .bash_profile for mac install (rev.f6305306)
	- added .bash_profile for mac install (rev.f90d2294)
	- test of bad characters (rev.3d2900bf)
	- added a run time debug option and reformatted logging (rev.799bb81d)



================================================================================
* Wed Mar 07 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.029

================================================================================
	- ipython notebooks converted to html (rev.6c6150e4)
	- first commit: ipython notebook example: "What is a parameter dictionary?" (rev.d52a5972)
	- first commit ipython notebook example1: "Calling recipes from python" (rev.8f4e4a80)
	- added blank template file (rev.50f06ce2)
	- updated date and version (rev.79586f18)
	- modified read_config_file to be able to return just filename (rev.de06e4e0)
	- rebuilt pdfs (rev.64f975e7)
	- set config_file name so sources are correct (rev.67a29e3a)
	- updated date and version (rev.8b2723c3)
	- set debug to 0 (rev.c3983d66)
	- updated exit message (rev.cfe77bcd)
	- updated exit message (rev.18debee0)
	- updated exit message (rev.698bb443)
	- updated exit message (rev.fe1e063b)
	- updated exit message (rev.8d174715)
	- updated exit message (rev.f1da6439)
	- updated exit message (rev.283f31b5)
	- updated exit message (rev.5b923d5d)
	- updated exit message (rev.d6413454)
	- updated exit message (rev.828c7afe)
	- updated exit message (rev.13c026b5)
	- updated exit message (rev.46f862e1)



================================================================================
* Tue Mar 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.030

================================================================================
	- conversion to html (rev.217ada1d)
	- first commit - using custom arguments (rev.6866fc9b)
	- update date and version (rev.7451eb14)
	- rebuilt pdfs (rev.4dcef23c)
	- updated date and version (rev.de9f2e0a)
	- updated docs for GetCustomFromRuntime function (rev.df3e8ccd)
	- added spacer (rev.d8d74bbc)
	- reformatted customargs (to be like cal_CCF) for consistency (rev.94858642)
	- example3 in html format (rev.2eb74aed)
	- first commit - the debugger (rev.384d8861)
	- rerun code (rev.abdd27e8)



================================================================================
* Wed Mar 14 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.031

================================================================================
	- updated image size (rev.b332d9d5)
	- update readme (rev.bac3360b)



================================================================================
* Fri Mar 16 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.031

================================================================================
	- examples 5 convert to html (rev.28d93884)
	- first commit - common python 3 functions different from old python 2 (rev.af1a919e)



================================================================================
* Mon Mar 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.032

================================================================================
	- corrected spelling (rev.f5bb466e)
	- corrected spelling (rev.c4683e6c)
	- corrected spelling (rev.388f6733)
	- corrected spelling (rev.2bdbd543)
	- corrected spelling (rev.7240e416)
	- corrected spelling (rev.5e1d6c4d)
	- corrected spelling (rev.b7f946f8)
	- corrected spelling (rev.0ba61252)
	- corrected spelling (rev.e9d6b28e)
	- corrected spelling (rev.03124088)



================================================================================
* Tue Mar 20 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.032

================================================================================
	- rebuilt pdfs (rev.471110fa)
	- updated edit date and versions (rev.b095deab)
	- corrected spelling (rev.f5badb1d)
	- corrected spelling (rev.4150506f)
	- corrected spelling (rev.d92e61f2)
	- corrected spelling (rev.20bf9ddf)
	- corrected spelling (rev.3c5466c6)
	- corrected spelling (rev.95e8988d)
	- corrected spelling (rev.94305707)
	- corrected spelling (rev.01cef9ab)
	- corrected spelling (rev.16b1fd69)
	- corrected spelling (rev.f1fd471c)



================================================================================
* Wed Mar 21 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.032

================================================================================
	- updates to comments (rev.8856c9cb)
	- rebuilt pdfs (rev.fdb8c9bd)
	- update date and versions (rev.c656c7aa)
	- spell check (rev.98e6df5c)
	- spell check (rev.3de2c5e7)
	- spell check (rev.17b0503a)
	- spell check (rev.07326813)
	- spell check (rev.3c46b527)
	- page split (rev.15c2ca4a)
	- added parameters to record file (rev.bd0f0626)
	- added return_filename for added functionality (rev.0c58fcb8)
	- improvements to telluric file - added header keys (rev.c4c7d880)



================================================================================
* Thu Mar 22 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.033

================================================================================
	- new example 7 (rev.aefc1121)
	- new example 6 (rev.3b8a7f49)
	- rebuilt pdfs (rev.af4b01d3)
	- updated versions and dates (rev.c9847b15)
	- moved examples to subfolder (rev.9ac9f146)
	- moved examples to subfolder (rev.91472752)
	- moved examples to subfolder (rev.f0d3a450)
	- moved examples to subfolder (rev.09178a5c)
	- moved examples to subfolder (rev.684f2444)
	- moved examples to subfolder (rev.90d35de5)
	- spelling check (rev.789aa2b4)
	- spelling check (rev.fe87e658)
	- spelling check (rev.570acd96)
	- spelling check (rev.13f8972b)
	- updates to comments (rev.ec918a8c)
	- spelling check (rev.c97b436f)
	- fixed error in call (rev.e240501e)



================================================================================
* Sun Mar 25 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.034

================================================================================
	- new unit test (not comp full run) (rev.6d5b0347)
	- updated date and version (rev.700e488a)
	- rebuilt pdfs (rev.29c81a27)
	- added new test full run no compare (rev.6954c88c)



================================================================================
* Wed Mar 28 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.0342

================================================================================
	- removed new constant (test) (rev.25aee593)
	- added new constant (rev.1c049c50)



================================================================================
* Thu Mar 29 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.0342

================================================================================
	- same? (rev.fb36b84e)



================================================================================
* Thu Apr 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.0344

================================================================================
	- fixed typo in call to deal_with+prefixes (requires filename if p not defined) and fixed __NAME__ (rev.03f49501)
	- removed call to calibDB (note needed) (rev.859f580c)
	- added quick mention of startswith, contains and endswith method to documentation (rev.47dd74f6)
	- added contains and endswith methods to ParamDict (rev.0eb9f1c1)
	- moved blank recipe to spirouTools (rev.840f4058)
	- Wrote some generic tools: list raw/reduced/calib files (with filter), display calibDB (with date filter) (rev.08cc0a01)
	- DRS reset moved to spirouTools (rev.ffa9676b)
	- dependencies corrected and moved to SpirouTools (rev.f36714ec)
	- moved tools to separate package (rev.f700327e)
	- updated change log with changes to calibdb (rev.6d2ba098)
	- added quiet modes for run_begin and load_arguments (rev.3e17d762)
	- calibDB now also contains humantime and unixtime accessible from dictionary call (rev.ac2cbafa)
	- updated module descriptions (based on changes) (rev.2dcec1e2)
	- fix of issue #156 - Parameter dictionary source dictionary not case insensitive (rev.21573134)
	- fix of issue #162 - cal_SLIT save TILT to file using Add1Dlist - slight change (rev.3471f51f)
	- fix of issue #162 - cal_SLIT save TILT to file using Add1Dlist (rev.1568fa8f)
	- fix of issue #171 - fixed cal_validate_spirou --> cal_validate_spirou.py (rev.077ecd10)
	- fix of issue #168 - Documentation: chapter installation weird <PATH> variable #168 (rev.1970835a)
	- fix of issue #166 - cal_DRIFTPEAK should accept hc or fp (rev.6b43de02)
	- fix of issue #164 - cal_extract kind is incorrect (rev.4ea2d0ff)
	- fix of issue #160 - too many decimal places in quality control - fixed (rev.71fe3425)
	- fix of issue #157 (Unix time doesn't match human time for UT) bug was only in "fake" wave solution files (rev.4ab44197)
	- Fixed Issue #154 (Installation type update to config.txt and constants_SPIROU.txt (now ```.py``` files) (rev.913a5cad)



================================================================================
* Fri Apr 06 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.0346

================================================================================
	- fix to issue #173 - Need a versioned text file (rev.be6652f8)
	- fix to issue #174 - License required (rev.d9beb67d)
	- fixed call to python (was python3 now python) (rev.5619ab74)
	- fix issue #170 - PYTHONPATH in installation - what happens if not defined? (rev.2010eabb)
	- fix issue #170 - PYTHONPATH in installation - what happens if not defined? (rev.3d78ff7c)
	- fix issue #170 - PYTHONPATH in installation - what happens if not defined? (rev.305af200)
	- fix issue #170 - PYTHONPATH in installation - what happens if not defined? (rev.0161dfbe)
	- fix issue #170 - PYTHONPATH in installation - what happens if not defined? (rev.3a9da123)
	- fix issue #170 - PYTHONPATH in installation - what happens if not defined? (rev.42dadc3b)
	- fix issue #165 - cal_extract plotting issue with bounding edges (rev.40a823e9)
	- fix issue #163 - cal_ff plot fit edges error (rev.f0e5144a)
	- fix issue #161 - cal_SLIT plot wrong offse - offset is now corrected (rev.31b8243a)
	- fixed plots closing automatically in an interactive session --> now user is asked (rev.dc5424ba)
	- fix to issue #159 - updated fix giving several allowed backends (rev.f1f16586)
	- fix to issue #159 - matplotlib plots freeze on macOSX (rev.9eeaac9f)



================================================================================
* Mon Apr 09 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.0348

================================================================================
	- fix to issue #152 - User/Custom config.py file - rebuilt pdfs (rev.5a937123)
	- fix to issue #152 - User/Custom config.py file - updated documentation (rev.ea19c317)
	- fix to issue #152 - User/Custom config.py file - updated documentation (rev.ac976d5d)
	- fix to issue #152 - User/Custom config.py file - rebuilt pdfs (rev.7b15b36d)
	- fix to issue #152 - User/Custom config.py file - updated documentation (rev.67a7edb8)
	- fix to issue #152 - User/Custom config.py file - updated documentation (rev.ca8c100a)
	- fix to issue #152 - User/Custom config.py file - updated documentation (rev.02e94c2a)
	- fix to issue #152 - User/Custom config.py file - updated documentation (rev.44e04026)
	- fix to issue #152 - User/Custom config.py file (rev.93356cc9)
	- fix to issue #152 - User/Custom config.py file (rev.3726864e)
	- fix to issue #152 - User/Custom config.py file (rev.f3f117c4)
	- fix to issue #152 - User/Custom config.py file (rev.227b5086)
	- fix to issue #152 - User/Custom config.py file (rev.acf4902c)
	- fix to issue #152 - User/Custom config.py file (rev.1b80d563)
	- fix to issue #152 - User/Custom config.py file (rev.7ad5b370)
	- fix to issue #152 - User/Custom config.py file (rev.1947e950)



================================================================================
* Wed Apr 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.0349

================================================================================
	- added unit test for cal_HC_E2DS_spirou (rev.42a00a93)
	- added hcone extraction to unit test (rev.93b59436)
	- replacement of rawfile with p['ARG_FILE_DIR'] (rev.8f74dda4)
	- replacement of rawfile with p['ARG_FILE_DIR'] (rev.42066a88)
	- place holder function for flat correction (rev.919e0a29)
	- replacement of rawfile with p['ARG_FILE_DIR'] (rev.4260a71e)
	- replacement of rawfile with p['ARG_FILE_DIR'] (rev.e86339fe)
	- fix to issue #176 - in progress - updating cal_HC_E2DS (rev.39b898c5)



================================================================================
* Thu Apr 12 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.035

================================================================================
	- Issue #176 - added get_lamp_parameters, fiirst_guess_at_wave_soltuion (unfinished), and decide_on_lamp_type functions (rev.fc1db233)
	- Issue #176 - added GetLampParams alias (rev.e319778a)
	- Issue #176 - renamed cdata_folder (rev.c4f8adec)
	- Issue #176 - created a read_line_list function (unfinished) (rev.c7233377)
	- Issue #176 - modified GetFile call (with required key) (rev.bf8af569)
	- Issue #176 - added correct_flat function (rev.c6fc8ca2)
	- Issue #176 - added CorrectFlat (rev.f752cf4b)
	- Issue #176 - renamed cdata folder - make it more clear it is a relative path (rev.c3ea6b48)
	- Issue #176 - modifications to get_file_name (rev.424fc847)
	- Issue #176 - added some cal_HC params (rev.8e7ee09b)
	- Issue #176 - added fiber getting, application of flat and start of first guess at solution (rev.804142b7)
	- update to version ready for new alpha release 0.1.035 (rev.0c5b2c52)
	- update to version ready for new alpha release 0.1.035 (rev.61eede62)
	- update to version ready for new alpha release 0.1.035 (rev.170b81ed)
	- update to version ready for new alpha release 0.1.035 (rev.a0506b7d)
	- update to version ready for new alpha release 0.1.035 (rev.c6b8e4d8)



================================================================================
* Fri Apr 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.036

================================================================================
	- Issue #176 - Added catalogue line lists to SpirouDRS data folder (rev.61590f7e)
	- Issue 176 - continued update of first_guess_solution (unfinished), added find_lines function (unfinished), added fit_emi_line (unfinished) (rev.11bd2f93)
	- fit gaussian moved to spirouCore.spirouMath (rev.8e8ec638)
	- read table modified to display numbe rof columns on error (rev.962d2068)
	- Issue #176 - read line list function modified (rev.0a5d3efa)
	- added overwrite to hdu.writeto function in spirouFits.writeimage function (rev.8eeed4f3)
	- issue #176 - alias for ReadLineList (rev.cb1f2d97)
	- moved fit gaussian to spirouMath (rev.58a739bd)
	- Issue #185 and #186 - kw_ACQTIME_KEY and kw_ACQTIME_KEY_UNIX are different between H2RG and H4RG (rev.2ad72c4c)
	- Issue #185 and #186 - DATE_FMT_HEADER now requires p to function (rev.d2cbebe8)
	- Issue #185 and #186 - DATE_FMT_HEADER now requires p to function (rev.61785b20)
	- Issue #186 - added "ic_image_type", Issue #176 - modified ic_lamp types (rev.8941e2d7)
	- Issue #186 - modified DRS_UCONFIG for H2RG/H4RG configs (rev.8d755dcd)
	- Issue #176 - modified to allow running without function (temporarily) (rev.c8852aa4)
	- Revert "Melissa" (rev.c47b2ed4)



================================================================================
* Fri Apr 13 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.1.036

================================================================================
	- Preprocessing script (currently does rotation only) (rev.8e890380)
	-  (rev.8f2806c3)
	-  (rev.c888abc0)



================================================================================
* Mon Apr 16 2018 Neil Cook <neil.james.cook@gmail.com> - 0.1.037

================================================================================
	- Spirou tools addition - compare two files (plot images and diff in a user-friendly manner) (rev.faf57802)
	- Issue #176 - continued development of find_lines (rev.e9e5f23f)
	- Issue #176 - Added FirstGuessSolution alias to init (rev.11c738d6)
	- Issue #176 - continued to build cal_HC_E2DS (rev.cfb26259)
	- Fix for bug introduced in last build - night_name now set in arg_file_names (rev.15dfc79d)
	- Merge from Melissa - H4RG constants_SPIROU file (values set from Melissa) (rev.495c54b3)
	- Merge from Melissa - update constants_SPIROU_H2RG with pep8 styling (rev.519721cb)
	- Merge from Melissa - switch between constants in H2RG and H4RG now constants_SPIROU.py is different for both (rev.b6621545)
	- Merge from Melissa - pre-processing script for H4RG images (currently only rotation) (rev.b2ef7c3e)



================================================================================
* Tue Apr 17 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.001

================================================================================
	- Continuation of Issue #176 - writing cal_HC - very stuck on replacing fitgaus.fitgaus (rev.87bfdb3a)
	- Fix for Issue #183 - now checks module and version (rev.c203f69d)
	- change to doc logo size (rev.c0233876)
	- change to doc logo size (rev.26ade6ec)
	- edit - test version needed main (rev.d922f381)
	- Updated documentation and added example custom configs to config folder (rev.fa2c11a9)
	- Issue # 193 - matplotlib dependency (rev.8f42408b)
	- Update spirouPlot.py (rev.1fbd8742)
	- Update spirouLOCOR.py (rev.bc7a6bc7)
	- Update spirouPlot.py (rev.2513f5ac)
	- Issue # 194 - Fix to python version string parsing failing if format isn't as expected (rev.4477c9c1)



================================================================================
* Tue Apr 17 2018 Chris Usher <usher@cfht.hawaii.edu> - 0.2.002

================================================================================
	- Copied the matplotlib backend fix into spirouLOCOR.py (rev.4a3e295b)
	- Only import IPython when it will be used. (rev.59891f0f)
	- Prevent failed import for missing matplotlib backends. (rev.43743595)



================================================================================
* Wed Apr 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.003

================================================================================
	- Fix to Issue #215 - spirouImage.WriteImage do not use dtype='float64' (rev.28bbc891)
	- Fix to Issue #215 - spirouImage.WriteImage do not use dtype='float64' (rev.5bf2573a)



================================================================================
* Thu Apr 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.004

================================================================================
	- fix to handling of custom arguments to accept only a list of filenames (rev.a24a8199)
	- New way to handle files (with wildcards built in) (rev.f6daa3a5)
	- Dealing with Issue #219 - pre-processing - unfinished (rev.a3a96ee7)



================================================================================
* Fri Apr 20 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.005

================================================================================
	- fix for issue #235 - added TODO to remove from cal_DARK eventually (rev.72bb4d81)
	- fix for issue #235 changed BADPIX to BADPIX_OLD for calibDB key (rev.ad22fd43)
	- added the has_plots=False to exit script (rev.a70959a9)
	- Fix to issue #176 (unfinished) - avoids the importing of cal_HC in unit tests running the code (currently doesn't have .main() for ease of debugging) (rev.74c0611a)
	- fix to issue #212 - night_name now is allowed a backslash at the end and now gives error if incorrectly defined (before wasn't checked specifically) (rev.f9ba5b15)
	- updated date and versions (rev.97b1ecc5)
	- Fix for issue #218 - threshold in find_order_centers should be in constnats file - also updated documentation with new constant (rev.991d08c5)
	- Issue #219 - Added PP function aliases to spirouImage (called in cal_preprocess_spirou) (rev.1e5e8478)
	- Issue #219 - pre-processing add Etienne's code to recipe- added functions "ref_top_bottom", "median_filter_dark_amp", "median_one_over_f_noise" (rev.7539f60f)
	- fix: exit script should only ask to close graphs if we have plots (see "has_plots" keyword) (rev.3a1d9bb6)
	- Issue #219 - pre-processing add Etienne's code to recipe (rev.429ca1ac)
	- Issue #219 - Add Etiennes pre-processing code to recipe (rev.cdc57035)



================================================================================
* Mon Apr 23 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.005

================================================================================
	- re-built pdfs (rev.28778833)
	- updated date and versions (rev.084c879d)
	- updated version in readme (rev.881cbfca)
	- Added alias to load_other_config_file (LoadOtherConfig) - used in tools (rev.24156e0c)
	- fixed bug in __all__ statement (rev.e6b2cb75)
	- update to style (rev.b2e801d6)
	- new tool - drs documentation - doc functions useful for keeping the docs up-to-date (rev.02fcdb6a)
	- Added % comments to doc (in variables) - needed to know which are missing (rev.44224863)
	- fix to suggestion in Issue #229 - changed argument order around to avoid confusion (rev.9d2c98fb)
	- changed plot colour to "gist_gray" and linetype to "red" to help ID fits better (pink on rainbow was bad) (rev.f5def9d1)
	- updated preporecess for use with H2RG (rev.2924ddc4)
	- fix for issue #220 - added alias to InterpolateBadRegions (call to spirouImage.interp_bad_regions) (rev.68b4da7c)
	- fix for issue #220 - added interp_bad_regions function and added doc strings for other new functions (rev.cd7b1b05)
	- fix for issue #220 - added bad_region constants (rev.96197998)
	- fix for issue #220 - added call to spirouImage.InterpolateBadRegions (rev.ef33ae10)



================================================================================
* Mon Apr 23 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.006

================================================================================
	- Corrected order of inputs in cal_BADPIX main definition. (rev.8f5e5869)



================================================================================
* Tue Apr 24 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.006

================================================================================
	- updated order of cal_BADPIX_spirou in the unit test functions (rev.6c245df3)
	- fix for Issue #229 - added alias to spirouImage.locate_bad_pixels_full (LocateFullBadPixels) (rev.eda16f2c)
	- code to un-resize and un-flip the image (for back processing files created by the DRS) (rev.52311ecf)
	- fix for Issue #229 - full flat detector image from engineering data (required for badpix fit) (rev.9014c4bd)
	- fix for Issue #229 - wrote locate_bad_pixel_full to workout threshold from full flat engineering data (rev.4cb3bd50)
	- fix for Issue #229 - added parameters to constants_spirou file (rev.63a214d3)
	- fix for Issue #229 - added parameters to constants_spirou file (rev.b89a632a)
	- Fix to Issue #193 - try statement to import matplotlib and error output via WLOG (does not fix but catches exceptions) (rev.01f5fa2c)
	- fix for Issue #229 - added call to ```spirouImage.LocateFullBadPixels```, plotted graph, added resizing and flipping the image to match other recipes (rev.90861956)



================================================================================
* Wed Apr 25 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.007

================================================================================
	- fix to cal_badpix to allow use with H2RG (required bool mask for bad_pixel_mask2) (rev.d105ebd4)



================================================================================
* Wed Apr 25 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.0097

================================================================================
	- cal_DARK: increased decimals shown (rev.d7ebf39d)



================================================================================
* Thu Apr 26 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.008

================================================================================
	- reset paths to defaults (shouldn't have overwritten) (rev.14e12b4f)
	- Add files via upload (rev.5775929c)
	- Add files via upload (rev.df2fa5a9)



================================================================================
* Fri Apr 27 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.009

================================================================================
	- Fix to issue #264 - spirouFLAT.MEasurEBlazeForOrder now requires p (for H2RG dependency) (rev.f19c22fb)
	- Fix to issue #264 - stop blaze setting zero or negative values to 1 (rev.df5972e2)
	- update? (rev.9d7354f4)
	- Issue #263 and Issue #262 - tilt borders added and mask for negative pixel added to all functions (rev.57137ff4)
	- added function to extract valid order numbers from constants_SPIROU (via ParamDict) (rev.561a2b8c)
	- added function to extract valid order numbers from constants_SPIROU (via ParamDict) (rev.2406a84c)
	- added function to extract valid order numbers from constants_SPIROU (via ParamDict) (rev.bd730110)
	- Addressing issues #225 and #226 - compatability with both H2RG and H4RG by adding "method" (switch between average and median), pep8 fixes (rev.6d420567)
	- pep8 fixes and Issue #226 - compatibility with both H2RG and H4RG (rev.aea05755)
	- Issue #263 - allowed tilt border to be changed in constants and first and last order to be selected. (rev.43ecf66d)
	- Issue #250 - average --> median and dependency with H2RG (rev.e0b53cf5)
	- allowed valid orders to be changed in constants. (rev.0564f33c)
	- dealt with dependency of H2RG (Issue #266) and allowed valid orders to be changed in constants. (rev.dd0d4684)
	- Revert "Francois" (rev.0dca6713)
	- Revert "Francois" (rev.4a522112)
	- Update config.py (rev.2108ed65)
	- Update visu_RAW_spirou.py (rev.9ee81924)
	- Update vcs.xml (rev.a998dae7)



================================================================================
* Fri Apr 27 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.010

================================================================================
	- Update constant parameters for flat-field and blaze (rev.d37f8a43)
	- Modification of spirouPLot to Display all orders with correct NBFIB parameter (rev.f3352a8a)
	- Start extraction from order 4th in cal_extract_RAW_spirou (rev.62ccade2)
	- Start extraction from order 4th in cal_FF_RAW_spirou (rev.4f747270)



================================================================================
* Fri Apr 27 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.011

================================================================================
	- manually adding francois changes (rev.76aec87d)
	- manually adding francois changes (rev.37cb7e74)
	- change (rev.cafbc049)
	- cleaning up files (rev.092e09d5)
	- removed cached files (rev.4806b261)
	- reset to master (rev.a9ae6535)



================================================================================
* Mon Apr 30 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.012

================================================================================
	- Regarding issue #264 - change no longer needed - revert to earlier version (rev.96f32d09)
	- fix to issue #267 - SNR saved in the headers - added keys to E2DS header (rev.88781021)
	- fix to issue #267 - SNR saved in the headers - added new keyword to list (rev.4cedc6ed)
	- fix to code dependency (rev.94a4ec3c)
	- Update cal_FF_RAW_spirou.py (rev.749a1217)
	- Update spirouLOCOR.py (rev.627eac64)



================================================================================
* Mon Apr 30 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.013

================================================================================
	- Update constant parameters for localization, flat-field and blaze (rev.38440110)
	- Plot the central column threshold for DRS_DEBUG=0 (rev.e2056d74)
	- Add the plot of the central column with miny and maxy for DRS_DEBUG=0 (rev.d80c999f)
	- plot values of e2ds>0 and values of blaze>1 (rev.89db1797)
	- Force the curvature of orders in case of no detection (rev.40c39aa3)



================================================================================
* Tue May 01 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.014

================================================================================
	- rebuild pdfs (rev.ea82cb5f)
	- updated date and versions (rev.67e6c0b0)
	- Redefining unit tests - example run files (for unit test) (rev.aea72de6)
	- Redefining unit tests - first commit - slight changes (logging) (rev.6895b60b)
	- Redefining unit tests - first commit - new recipe for unit test (rev.b0afd8bb)
	- Redefining unit tests - first commit - new functions for unit test (rev.c669dcf9)
	- Redefining unit tests - first commit - new recipe definitions for unit tests (rev.19d27f1f)
	- Redefining unit tests - added new function aliases (rev.44c37e6d)
	- Redefining unit tests - moved old (rev.c27bc3a7)
	- Redefining unit tests - moved old (rev.29cc9252)
	- Redefining unit tests - moved old (rev.20291619)
	- Redefining unit tests - moved old (rev.5bee0b07)
	- Redefining unit tests - moved old (rev.fb30c966)
	- Redefining unit tests - moved old (rev.cfb251f4)
	- Redefining unit tests - allowing silent reset (not advised) (rev.9d0a12f0)
	- updating versions (rev.bcfc14ab)
	- Redefining unit tests - add function alias (rev.302fe1e3)



================================================================================
* Wed May 02 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.015

================================================================================
	- notebook additions - conversion to html (rev.26ba1665)
	- notebook additions - added a quiet mode for notebooks (no user input needed) (rev.63dfdb36)
	- notebook additions - added unit_test alias to init file (for loading up from python) (rev.cb2ab243)
	- notebook additions - test unit test for notebooks (rev.8d1748c6)
	- notebook additions - example 9 - unit tests (rev.e080bf4b)
	- notebook additions - example 8 - wlog (rev.26dafbd8)
	- notebook additions - code to convert (rev.6cf30683)



================================================================================
* Thu May 03 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.016

================================================================================
	- pep8 update all ParamDict constants to capitals (rev.0fdab7d7)
	- unit_test - added additional run files (rev.f61b27fa)
	- unit_test fix - DRS_Reset modification, loading arguments modification and set_type --> check_Type change (rev.c5376f93)
	- unit_test fix - set_type doesn't work - just check type instead (and throw error) (rev.b3acf21e)
	- unit_test fix - rename set_type to check_type (rev.bf32583f)
	- unit_test fix - alias to load_minimum (rev.031b890e)
	- unit_test fix - reset_confirmation modification and log successful completion (rev.6fd33ded)
	- unit_test fix - do not require night_name (rev.825fe5cd)



================================================================================
* Fri May 04 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.017

================================================================================
	- updated date and versions (rev.1f8494ee)
	- unit_test fix - add total time to log_timings print out (rev.41c15b8a)
	- fix to Issue #278 - make cal_extract_RAW_spirouAB and cal_extract_RAW_spirouC work again (rev.a3417c0b)
	- fix to Issue #278 - make cal_extract_RAW_spirouAB and cal_extract_RAW_spirouC work again (rev.92e57ce5)
	- fix to issue #281 - small function to deal with some extensions being corrupted (will still crash if all extensions bad) and will assume first valid extension (i.e. with shape) is the image to be used. (rev.9ef5f7a7)
	- fix to issue #277 - check "files" and if it is a string force it into a length=1 list, if not string or list throw error (rev.a115c777)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.18c3d3cf)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.d780ae0e)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.5e4dde44)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.d761b553)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.4523c6e6)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.2e4ef943)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.4c755d94)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.d6b72394)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.579f67d6)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.740b0919)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.6cb17ae6)
	- fix to issue #277 - added doc string to main functions to make it clear what inputs are expected (rev.c69e37a2)



================================================================================
* Mon May 07 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.018

================================================================================
	- fix to latex format (rev.64410030)
	- fix to install (cal validate from cmd line needs .py) (rev.81d28a5b)
	- rebuilt pdfs (rev.96a1f86d)
	- added retrun possibility to list_modules, and added find_all_missing_modules wrapper function (rev.5d732cbb)
	- completed doc string (rev.9019ec84)
	- corrected __all__ (rev.4afa9aa8)
	- added missing doc strings (rev.904e0f18)
	- added missing doc strings (rev.9295ba15)
	- added missing functions from tex files (rev.6c3149cc)
	- added tex and pdf versions of the examples (auto-generated from notebooks) (rev.b39bc84f)
	- added unit tests and tools to SpirouDRS __all__ list (and imported) (rev.0dab475f)
	- example 10 in html format (rev.32fbb52a)
	- example 10 - how to use spirou tools (rev.98470492)
	- fixed bug in display_calibdb (use LoadMinimum not LoadArguments) (rev.008810c6)
	- updated date and version (rev.32a9949f)
	- updated date and version (rev.2ed5d936)
	- updated variables (added CCF variables and missed cal_BADPIX variabels) (rev.4f2a47f5)
	- update to ic_ext_tilt_bord description (rev.a21a111d)
	- H4RG by default (rev.c470b1f5)
	- update to unit_test file (post unit_test changes) (rev.85c2a98e)
	- fix to issue #287 - extra issue log statements with errors inside - print warnings first then internal errors after - set key after too (avoids printing errors inbetween warnings) (rev.71b2e912)
	- fix to issue #287 - extra issue of crash before config loads (IC_IMAGE_TYPE) missing from needed spirouKeyword USE_PARAMS (rev.9cd1c171)
	- fix to issue #287 - deal with DRS_UCONFIG warning printing (rev.dc99a99e)
	- Update README.md (rev.95cb2d69)



================================================================================
* Wed May 09 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.019

================================================================================
	- fitgaus fortan code (for testing only) (rev.5d8a5621)
	- example in ipynb and tex format (rev.802a9f6e)
	- modified test run unit test (rev.7d984ab3)
	- added new unit test runs (all and minimum required) (rev.c4408d3f)
	- removed old unit test runs (rev.12b94ca7)
	- added cal_extract_RAW_spirou AB and C to unit tests (rev.3a8ae09f)
	- fix problem with reset = False (rev.69528f62)
	- fix so wrapper extractions work with unit_tests (and can be called from python) (rev.75f5dda6)
	- ic_ext_sigdet should be -1 (rev.a307516a)
	- fix to Issue #289 - was a problem with WLOG message (argument missing from format) (rev.281744e3)



================================================================================
* Wed May 09 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.020

================================================================================
	- Faction of dead pixels display with 4 digits (rev.629405ca)
	- Fake wavelength solution due to missing WAVE in calibDB (rev.823e45db)
	- Display of the format of the resized image (rev.dd4728b3)
	- New extraction_tilt_weight2cosm with cosmic correction. (rev.598f3947)
	- Display of bad pixels with 4 digits (rev.7765ee90)
	- ic_blake_fitn set to 7 (rev.5b995a6a)
	- ConvertToADU convert from ADU/s to ADU (not e-) (rev.044c7af5)
	- Fake wavelength solution to run without WAVE fiel in the calibDB (rev.77b49c9d)
	- Correction of the display of the image size (rev.2918c56f)



================================================================================
* Fri May 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.020

================================================================================
	- fix to Issue #294 - stats for bad_pixel_map_2 in cal_BADPIX_spirou (rev.a4cb57d9)
	- fix to Issue #294 - stats for bad_pixel_map_2 in cal_BADPIX_spirou (rev.5b1ba116)
	- start of fix to issue #295 - Switch between extraction routines in constants_SPIROU file - unfinished (rev.e2629543)
	- fix to issue #294 - stats for bad_pixel_map_2 in cal_BADPIX_spirou (rev.de3820c6)
	- fix imports for python 2 and make runs sorted (again for python 2) (rev.d6cb14d2)
	- fix imports for python 2 (rev.662d42fb)
	- update units tests with new run names (sortable) - python 2 safe (rev.f844ad8f)
	- fix unit test import (should be inner call to function) (rev.2b58791e)
	- fix typo (rev.5488910a)
	- fix for typo (rev.b0fc8981)
	- fix to import statements (for python 2 compatibility) (rev.b8914e63)
	- New extraction_tilt_weight2cosm with cosmic correction. (rev.ecb0ff1b)
	- Display of bad pixels with 4 digits (rev.a80d6678)
	- ic_blake_fitn set to 7 (rev.2b39cc3d)
	- ConvertToADU convert from ADU/s to ADU (not e-) (rev.5fa74f23)
	- Fake wavelength solution to run without WAVE fiel in the calibDB (rev.44c1d12a)
	- Correction of the display of the image size (rev.13dbf602)



================================================================================
* Sat May 12 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.021

================================================================================
	- fix to issue #300 - added correct_for_badpix function (rev.169427d5)
	- fix to issue #300 - alias to correct_for_badpix function (rev.f49882f0)
	- fix to issue #298 - exit script should deal with new DRS_INTERACTIVE parameter (rev.e087134f)
	- fix to issue #298 - DRS_INTERACTIVE should be set to 1 by default (rev.9336780a)
	- fix to bug identified - no exit script in AB or C (rev.82e8bc96)
	- fix to issue #298 - set DRS_PLOT to zero if DRS_INTERACTIVE == 0 and if DRS_INTERACTIVE == 0 do not prompt user at the end of recipes about exiting and plotting (rev.f24ece47)
	- fix to issue #298 - set DRS_PLOT to zero if DRS_INTERACTIVE == 0 and if DRS_INTERACTIVE == 0 do not prompt user at the end of recipes about exiting and plotting (rev.beeb739b)
	- fix to issue #298 - added DRS_INTERACTIVE to config.py (rev.37743a2f)
	- fix to issue #297 - Unit test to display current files if no argument (rev.264597aa)
	- fixes to unit_tests for internal bugs and to correct for issue #295 (rev.3cd72b1d)
	- fix to issue #294 - H2RG needs to return "bstats2" too (set to zero) (rev.69cc6737)
	- fix to Issue #295 - complete reworking of wrapper function (which is now called from recipes) (rev.8bbcdc8e)
	- fix to Issue #295 - updated alias functions (rev.30571b39)
	- fix to Issue #295 - added E2DS_EXTM and E2DS_FUNC HEADER keys to report extract type and extract function (rev.93fcd039)
	- fix for Issue #295 - removed EXTRACT_E2DS_ALL_FILES - not needed any more (rev.aed0ed59)
	- fix to Issue #295 - change the way extraction is managed - modified IC_EXTRACT_TYPE and added IC_FF_EXTRACT_TYPE (rev.6cb3b7e3)
	- fix to Issue #295 - change the way extraction is managed - now type IC_FF_EXTRACT_TYPE (rev.66eb2be3)
	- fix to Issue #295 - change the way extraction is managed - now type 2 (rev.cb201f51)
	- fix to Issue #295 - change the way extraction is managed - now type 2 (rev.d36fd16e)
	- fix to Issue #295 - change the way extraction is managed (rev.62fce79f)



================================================================================
* Mon May 14 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.022

================================================================================
	- Update README.md (rev.1bcf0233)
	- updated date and versions (rev.cff231b0)
	- fix for issue #296 - was mistake in argument to test_suffix = suffix.format  - called dictionary incorrectly (rev.e338e90d)
	- fix for issue #302 - IC_COSMIC_THRES --> IC_COSMIC_THRESH (rev.59b5359a)
	- updated test run (rev.19030835)
	- fix for issue #302 - added IC_COSMIC_SIGCUT and IC_COSMIC_THRES (rev.ac535ff6)
	- fix for issue #302 - added IC_COSMIC_SIGCUT and IC_COSMIC_THRES (rev.ffa07e33)
	- fix to Issue #296 - added alias (CheckPreProcess) for spirouStartup.check_preprocess (rev.67962cae)
	- fix to Issue #296 - added IC_FORCE_PREPROCESS and added all other preprcess constants to constants file (rev.dbbb9284)
	- fix to #296 - added .fits to suffix (rev.d506967c)
	- fix to Issue #296 - added call to CheckPreProcess - check for preprocessed files (rev.d5c63e9c)
	- fix to #296 - added check_preprocess function (rev.26618227)
	- fix to unit_test - bug in logic when file does not exist --> True to False (rev.175bffea)
	- fix to issue #292 - get_fiber_type modified to accept and require suffix to get fiber type (rev.82bc5eea)



================================================================================
* Tue May 15 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.023

================================================================================
	- updated run (rev.97c4aeb9)
	- fixed typo (rev.3bf3e5ba)
	- added runname to comparison table (rev.45437b2c)
	- added run name to comparison table (to name table) (rev.69fffd0c)
	- corrected bug with unit test (files were duplicated in list i.e. file1 file1 file2 file3 (rev.13c37898)
	- tool file - clear out cached .pyc files (useful when rebuilding) (rev.49c3d245)
	- H2RG compatibility - fitsfilename = arg_file_names[-1] and only adding SNR keys and EXTM/FUNC for H4RG, p returned to call (rev.f0016c0b)
	- fixed pep8 in smoothed_box_mean_image1 function (rev.48ccb515)
	- updated date and version + rebuild pdfs (rev.95ffbc31)
	- updated date and version (rev.c8a323a0)
	- H2RG compatibility - fitsfilename = arg_file_names[-1] and only adding SNR keys and EXTM/FUNC for H4RG (rev.ef7cedf8)
	- H2RG compatibility - fitsfilename = arg_file_names[-1] (rev.619474c3)
	- true on comparison in H2RG run (rev.5bd56da0)
	- fix to calling from python (bug introduced in last update) (rev.bd1fa1e6)
	- fix to unit_test comparison table (rev.8ef00e03)
	- fix to unit_test comparison table (rev.60001f4d)
	- fix to unit_test comparison table (rev.f75c040d)



================================================================================
* Wed May 16 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.024

================================================================================
	- removed dependency on cal_drift_raw (rev.d7089169)
	- updated test.run (rev.f3b5790f)
	- fix to Issue #227 - dealt with warnings for cal_driftpeak (rev.7fd7c875)
	- updated date and version (rev.ffee1e83)
	- fake file comments added (rev.80419525)
	- added fake fp_fp files for drift (copies of fp_fp_001) (rev.6f48a60b)
	- fix to Issue #227 - removed support for cal_drift_raw_spirou (rev.08c44707)
	- fix to Issue #227 - removed cal_DRIFT_RAW_spirou (rev.a7b6dff3)
	- fix to Issue #227 - refactored warnlog (rev.296b66c3)
	- fix to Issue #227 - added cal_drift and drift peak to tests (rev.368dacc9)
	- fix to Issue #227 - deal with warnings (rev.758d692c)
	- fix to Issue #227 - refactor warnlog (+ fix bug) (rev.4fb9d514)
	- update date and version (rev.18a695c1)
	- fix to Issue #227 - refactor warnlog (rev.8c71668e)
	- fix to Issue #227 - apply H4RG fixes to drift codes (rev.dd070eff)
	- enchancement - compare function gets ARG_NIGHT_NAME from ll, prints old and new file locations (for extra confirmation) (rev.254851a9)
	- update oldpath (don't include path) (rev.617d284d)
	- updated test run (rev.7f40e863)
	- fix for bug when HEADER time not string (should always be string but can be interpreted as number and thus break function) (rev.ecccf372)
	- fix - removed unneeded comment (rev.ef38791c)



================================================================================
* Thu May 17 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.025

================================================================================
	- fix to Issue #227 - added cal_drift and drift peak to tests (rev.babab427)
	- fix to Issue #227 - added cal_drift and drift peak to tests (rev.8d132fde)
	- fix to Issue #227 - added cal_drift and drift peak to tests (rev.703a358b)
	- work on issue #176 - Attempt to get First Guess solution working and detection of badlines (rev.92a70853)
	- work on issue #176 - Attempt to get First Guess solution working and detection of badlines (aliases) (rev.7c7517fd)
	- work on issue #176 - added three cal_HC constants (rev.640e635f)
	- work on issue #176 - Attempt to get First Guess solution working and detection of badlines (rev.06f58769)



================================================================================
* Fri May 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.026

================================================================================
	- update readme (rev.8780b3cd)
	- rebuilt pdfs (rev.11a93f53)
	- fixed bug when config files only have one or zero lines. (rev.702986d7)
	- reset constant back to default (rev.bbc0b503)
	- fix to Issue #232 - added cal_exposure_meter to unit tests (rev.646a3367)
	- fix to Issue #232 - added cal_exposure_meter to unit tests (rev.52681550)
	- fix to Issue #232 - add file names for cal_exposure_meter (rev.95353fc0)
	- fix to Issue #232 - add different outputs (rev.bfe040d6)
	- fix to Issue #232 - add different outputs (rev.b81516a9)
	- fix to Issue #232 - bug in applying badpixmask (rev.ca447f69)
	- commented out work-in-progress function (rev.980c5892)
	- fix to Issue #232 - added get_badpixel_map and modified correct_for_badpix functions (rev.3e062e9e)
	- fix to Issue #232 - added exposure-meter functions to new sub-module in spirouImage (rev.6c049915)
	- fix to Issue #232 - added alias to get_badpixel_map function (GetBadPixMap) (rev.df3e4df6)
	- fix to Issue #232 - added output keywords to spirouKeywords (rev.e76d938f)
	- fix to Issue #232 - added telluric exposure meter maps to calibDB (rev.68fa8384)
	- fix to Issue #232 - added expsoure-meter constants (rev.fe298933)
	- fix to Issue #232 - produce expsoure-meter recipe (compatible with H2RG and H4RG) (rev.c1c4fa90)
	- work on cal_HC (restore from bad merge) (rev.fcccf3e1)
	- added wavelength solution file for H4RG (rev.a151117e)
	- added H4RG wavelength solution files to the calib DB default files (for reseting) (rev.d2abd7ca)
	- @FrancoisBoucy - 4 digit to diplay the dark statistics (rev.088a1583)
	- @FrancoisBouchy - new lower limit in dark level plot (with H2RG compatibility) (rev.139782ee)
	- fix error message in get_database (calibDB) (rev.6a3e6ae0)
	- update default master_calib_spirou file (with H2RG and H4RG default wave solutions) (rev.84c56e7a)
	- update date and version (rev.10c1d83a)
	- @FrancoisBouchy - update to dark constants (rev.f77c796f)
	- @FrancoisBouchy - visu_RAW_spirou adapted for preprocessed files (rev.bcbd5231)
	- @FrancoisBouchy - Use the wavelength solution from the calibDB, set all negative pixels to zero and update ext_sorder_fit upper limit (rev.11ddf43c)
	- @FrancoisBouchy - Use the wavelength solution from the calibDB (rev.5eae6b85)
	- @FrancoisBouchy - Quality control of the dark level on the blue part of the detector (rev.5ca7d451)
	- added recipe to reset (while in development only) (rev.ce802c5b)



================================================================================
* Fri May 18 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.027

================================================================================
	- 4 digit to diplay the dark statistics (rev.83cd93ee)
	- Range adjusted to display Dark frame (rev.2a728ef3)
	- Dark constant and Dark quality control adjusted (rev.d57d179a)
	- visu_RAW_spirou adapted for preprocessed files (rev.573584b2)
	- Negative pixels are set to zero (rev.60f96e78)
	- Use the first wavelength solution from the calibDB spirou_wave_H4RG_v0.fits (rev.cb5e449f)
	- Quality control of the dark level on the blue part of the detector (rev.3ca1d937)



================================================================================
* Fri May 25 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.029

================================================================================
	- Update of cal_DRIFT_E2DS_spirou. Results now comparable to cal_DRIFTPEAK_E2DS_spirou (rev.c94ba46d)
	- First wavelength solution added to SpirouDRS/data (rev.f9e9d351)
	- Telluric mask added on SpirouDRS/data (rev.3c324646)
	- fortran module for BERV computation : Require f2py -c -m newbervmain --noopt --quiet newbervmain.f (rev.3fe86bbd)
	- Update of cal_CCF_E2DS with target parameters and BERV computation from the fortran module newbervmain (rev.12b632b3)
	- Update of cal_DRIFT_E2DS_spirou. Results now comparable to cal_DRIFTPEAK_E2DS_spirou (rev.86ee03bb)
	- Background correctionis now an option (rev.1e7e4780)
	- cal_FF_RAW_spirou must run on flat_flat and provide flat and blaze for A, B, AB and C fibers (rev.8f4bfecb)
	- New recipes to display the full spectral range of an E2DS file (rev.ca5084b9)
	- Typo on the name corrected (rev.7708446e)
	- Added CFHT parameters and option for background correction on cal_DRIFT (rev.0210c47d)
	- Add targets keywords + Date of observations for cal_CCF_E2DS_spirou (rev.d6dd9865)
	- All wavelength are in nm (rev.31c94e61)
	- #300 Bug on the fit_ccf on individual orders to investigate (rev.96fc073b)



================================================================================
* Fri May 25 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.030

================================================================================
	- worked on fit_1d_solution (complete?), added to doc strings (gparams) (rev.d52da12e)
	- added alias to fit_1d_solution (Fit1DSolution) (rev.465cf1bb)
	- added new cal_hc variables (rev.61fec410)
	- change FirstGuessSolution mode to new (to avoid needing fortran fitgaus code) (rev.28733469)



================================================================================
* Fri May 25 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.031

================================================================================
	- Update cal_CCF_E2DS_spirou.py (rev.2b2b7352)



================================================================================
* Sat May 26 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.033

================================================================================
	- updated date and version number (rev.1acb26ed)
	- update tests with CCF test (rev.ef41fe2f)
	- update h2rg constant file (to be same as h4rg) (rev.99e89f9e)
	- fix typos (rev.56d48e44)
	- fix runtime errors on ccf test (set order to empty) (rev.d650946e)
	- added ee (rev.eb9c443d)
	- removed fortran code (rev.ea879e4a)
	- update unit tests (rev.cd5493fd)
	- update fortran codes (rev.5d42518d)
	- updated script doc string (rev.e0018d3c)
	- update unit tests (cal_FF_raw needs flat_flat) (rev.42e63e24)
	- synced h2rg and h4rg (rev.fb0d4464)
	- correct the comments and indentation of the background (rev.4c8eddec)
	- @FrancoisBouchy change (merged by @njcuk9999) - why comment out this line? (rev.db15720c)
	- @FrancoisBouchy change (merged by @njcuk9999) - plot labels should be in nm not angstrom (rev.296c5f1d)
	- @FrancoisBouchy change (merged by @njcuk9999) - added new required input HEADER keywords (rev.0d356356)
	- @FrancoisBouchy change (merged by @njcuk9999) (rev.3159d988)
	- @FrancoisBouchy change (merged by @njcuk9999) (rev.cc9177a0)
	- @FrancoisBouchy change (merged by @njcuk9999) (rev.c8a6a67e)
	- update H2RG dependency flag (rev.b9d0ac56)
	- @ Francois Bouchy - fixed changes dark_flat/flat_dark --> flat_flat (rev.a2d4a713)
	- @FrancoisBouchy added earth_velocity_correction, newbervmain functions and modified coravelation (rev.a74ed500)
	- @FrancoisBouchy - added alias to earth_velocity_correction (rev.fdae9032)
	- @FrancoisBouchy added read star parameters and earth velocity calculation (rev.287f7a95)



================================================================================
* Sun May 27 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.033

================================================================================
	- update value for speed of light, added invert_1ds_ll_solution (rev.c767449e)
	- added new trial method to newbervmain (using barycorrpy) (rev.42d98427)



================================================================================
* Mon May 28 2018 Spirou DRS <spdrs@mail.cfht.hawaii.edu> - 0.2.033

================================================================================
	- new masks added on data (rev.3fcb4dfd)



================================================================================
* Mon May 28 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.034

================================================================================
	- updated for cal_hc (rev.9f433e60)
	- removed redundant comment (rev.9207565c)
	- added test from old drs (rev.0cebb94e)



================================================================================
* Tue May 29 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.035

================================================================================
	- fix matplotlib bug (rev.c68d00e7)
	- fix small bug (rev.92250644)
	- update date and version (rev.9f8d0a23)
	- update config.py (rev.68aadee4)
	- re-added BERV correction just for H4RG (rev.8e4100e3)
	- added masks to correct folder (rev.a5230945)
	- added new SpirouDRS data directories (rev.e97b9611)
	- added new SpirouDRS data directories (rev.7587a81e)
	- added new SpirouDRS data directories (rev.d1e5d183)
	- added new SpirouDRS data directories (rev.7c975577)
	- sorted SpirouDRS data folder (rev.18b3fe9e)
	- barycorrpy leap sec files (moved to drs) (rev.4648c525)
	- added constant for berv (ccf) (rev.59617791)
	- updated ccf function (rev.b9317e69)
	- edited ccf (rev.c5343492)



================================================================================
* Mon Jun 04 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.035

================================================================================
	- Fitgaus - python version (rev.c88a499a)



================================================================================
* Thu Jun 07 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.036

================================================================================
	- find lines test (cal_HC test) (rev.0a46d8c3)
	- continued work on cal_HC - aliases for new THORCA functions (rev.dec752b7)
	- continued work on cal_HC - wave littrow plot (rev.50c5c058)
	- continued work on cal_HC - experimentation with fitting (rev.e13bea14)
	- continued work on cal_HC (rev.0ce9e317)
	- continued work on cal_HC - constants for cal_HC (rev.d6a5076e)
	- continued work on cal_HC (rev.49783620)



================================================================================
* Thu Jun 07 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.037

================================================================================
	- added default user config path (rev.87b27a9b)
	- added my path (rev.8f7b14bd)
	- @FrancoisBouchy changes - merge confirmed, added some pe8 and comments and simplifications (rev.7a2b5669)
	- @FrancoisBouchy changes - merge confirmed (rev.d9ba61dd)
	- @FrancoisBouchy changes - merge confirmed + added ff_rms_plot function (rev.afda4a15)
	- @FrancoisBouchy changes - merge confirmed (rev.68618ae4)
	- @FrancoisBouchy changes - merge confirmed + added ff_rms_plot_skip_orders (rev.cddc8561)
	- Added ff_rms_plot_skip_orders (blank for H2RG) (rev.1598432f)
	- @FrancoisBouchy changes - merge confirmed (rev.46f8496d)
	- @FrancoisBouchy changes - merge confirmed (rev.37724168)
	- @FrancoisBouchy changes - merge confirmed (rev.f3bfc698)
	- @FrancoisBouchy changes - merge confirmed (rev.8a834fb1)
	- @FrancoisBouchy changes - merge confirmed, moved plotting to spirouPlot (rev.30dcd506)
	- @FrancoisBouchy changes - merge confirmed, some pep8 and commenting (rev.abec824c)
	- @FrancoisBouchy changes - merge confirmed (rev.07ff8a63)



================================================================================
* Fri Jun 08 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.039

================================================================================
	- continued work on cal_HC (Issue #176) - test of fit gauss functions (rev.89fde772)
	- continued work on cal_HC (Issue #176) - modified first_guess_at_wave_solution, detect_bad_lines, fit_1d_solution, calculate_littrow_sol, extrapolate_littrow_sol, second_guess_at_wave_solution. Added join_orders (rev.180c85c5)
	- continued work on cal_HC (Issue #176) - added alias to spirouTHORCA.join_orders (JoinOrders) (rev.8f0b7405)
	- continued work on cal_HC (Issue #176) - added wave_littrow_check_plot and corrected wave_littrow_extrap_plot (rev.80551c3f)
	- continued work on cal_HC (Issue #176) - corrected imports and a bug in fitgaussian functions (rev.3de8845f)
	- continued work on cal_HC (Issue #176) - added how to compile fortran (rev.2366410a)
	- continued work on cal_HC (Issue #176) - python version of fitgaus by @melissa-hobson (rev.16a45f27)
	- continued work on cal_HC (Issue #176) - added new constants (rev.b30b7f55)
	- continued work on cal_HC (Issue #176) - added new constants (rev.81ba591b)
	- continued work on cal_HC (Issue #176) (rev.ab7e5d79)



================================================================================
* Mon Jun 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.041

================================================================================
	- updated date and version (rev.608abe42)
	- continued work on cal_HC (Issue #176) - added two masks for cal_HC (rev.f61ef4a5)
	- continued work on cal_HC (Issue #176) - updated keywords, renamed some loc variables (for clarity) (rev.3f65e0df)
	- continued work on cal_HC (Issue #176) - added some fixes to coravelation (to accommodate cal_hc) (rev.5201cad8)
	- continued work on cal_HC (Issue #176) - added merge table and added some fixes to small bugs (rev.4fb4a066)
	- continued work on cal_HC (Issue #176) - added alias to spirouTable.merge_table (MergeTable) (rev.9b78fba7)
	- continued work on cal_HC (Issue #176) - added FWHM calculation (from sigma) (rev.aa1cf01c)
	- continued work on cal_HC (Issue #176) - added keywords for cal_hc (rev.015b5ca6)
	- continued work on cal_HC (Issue #176) - added wave file output filename definitions (rev.69a48e79)
	- continued work on cal_HC (Issue #176) - added constants (rev.7ffc6eee)
	- continued work on cal_HC (Issue #176) - output to file + ccf calculation (from cal_CCF mainly) (rev.beae0d3f)
	- continued work on cal_HC (Issue #176) - fixed value of FWHM from sigma (rev.c19736e4)



================================================================================
* Tue Jun 12 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.043

================================================================================
	- work on issue #155 - added recipe control file (rev.4cc32a08)
	- work on issue #155 - (un-finished) added new initial_file_setup and get file (now use single_file_setup) (rev.7e7a962a)
	- work on issue #155 - modified read_header to optionally return comments (rev.e3a247f8)
	- work on issue #155 - added ID functions (rev.dd2a9dfa)
	- work on issue #155 - reworked aliases and __ALL__ (rev.71454d18)
	- work on issue #155 - updated DPRTYPE comment (rev.59767ca3)
	- work on issue #155 - added some required keywords (rev.cc53365f)
	- work on issue #155 - rearranged some constants, added data constant directory (rev.1d70a592)
	- work on issue #155 - changed import to deal with change in location of spirouFile (rev.211de775)
	- work on issue #155 - test of ID-ing files (rev.4928d833)
	- work on issue #155 - added section to ID files and modify the header accordingly (based on filename OR header keys) (rev.19f87ebe)



================================================================================
* Wed Jun 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.044

================================================================================
	- modified run order (rev.a7f01545)
	- work on issue #176 - changes from variable names (in line with other recipes) (rev.6f477509)
	- work on issue #155 - modified initial_file_setup, added single_file_setup and multi_file_setup, set todo's to remove now obsolete functions, added new get_file function (rev.70ce8e14)
	- added aliases (rev.5b580342)
	- added rotate function, fix non pre-processed files function (rev.e7e9624a)
	- work on issue #155 - finished id checking functions (rev.e75eceb7)
	- added aliases (rev.fbbc12b5)
	- updated date and version, shortened log_opt (no suffix just program name) (rev.b421158b)
	- shorterned calibration --> cal. in log messages (for copying/not copying cal files) (rev.823d9df5)
	- work on issue #155 - added more files to control (rev.c0b11717)
	- updated constant name (rev.6be34a9b)
	- added constants (preprocessing, exposuremeter, cal_hc, cal_wave) (rev.73fffb7c)
	- fix for non pre-processed files (rev.01367dd9)
	- fixed bug in gfkwargs (rev.435d1109)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via InitialFileSetup), fix for non pre-processed files (rev.1c163666)
	- made rotation a function based on a given rotation from constant (rev.f400c473)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via InitialFileSetup), fix for non pre-processed files (rev.420c863f)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via InitialFileSetup), fix for non pre-processed files, added H2RG compatibility fix (rev.988c29ee)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via InitialFileSetup), fix for non pre-processed files (rev.b6876236)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via InitialFileSetup), fix for non pre-processed files (rev.55a83d10)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via InitialFileSetup), fix for H2RG compatibility, added H4RG kw objects needed for berv calculation (rev.e9987a9c)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via SingleFileSetup + MultiFileSetup) (rev.9ae18b76)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via SingleFileSetup) (rev.ba389381)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via SingleFileSetup) (rev.68c4e5d6)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via InitialFileSetup), fix for H2RG compatibility (rev.2edaac32)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via SingleFileSetup) (rev.19ea016a)
	- work on issue #155 - modified set up to accommodate checks via filename and header (via SingleFileSetup) (rev.7567558f)



================================================================================
* Thu Jun 14 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.045

================================================================================
	- work on Issue #155 - fix for new single file return (rev.f346e670)
	- work on issues #167, #176 and #231 - first commmit spirouWAVE file with cal_WAVE (only) functions (rev.d250d12f)
	- work on issues #167, #176 and #231 - renamed 'DATA' to 'HCDATA', moved get_ll, get_dll to spirouMath (rev.910f51ee)
	- work on Issue #155 - modified multi_file_setup function and return of single_file_setup (rev.d8fda026)
	- moved get_dll to spirouMath (rev.8dad0e16)
	- work on issues #167, #176 and #231 - added read_hcref, fixed bug with NBFRAMES append_source --> set_source (rev.dbf96439)
	- work on Issue #155 - fixing bugs for multi file setup (custom) (rev.5ab8912c)
	- added aliases (rev.b757a0bc)
	- added aliases (rev.f05cff3c)
	- renamed correct_flat to get_flat (rev.2d3428dc)
	- added aliases (rev.f05dd44b)
	- work on issue #167, #176, #231 - added wave_plot_instrument_drift, wave_plot_final_fp_order, wave_local_width_offset_plot, and wave_fp_wavelength_residuals (rev.70b8e34f)
	- moved get_ll_from_coefficients and get_dll_from_coefficients here (rev.d2f38533)
	- added aliases (rev.5cb7598c)
	- updated date and version (rev.2a16434c)
	- modified comment (rev.b2af430f)
	- work on Issue #176, #167, #231 - added constants (rev.f9e7e48c)
	- work on Issue #176, #167, #231 (rev.f98bfa83)
	- work on Issue #155 - modified return of recipe (rev.41c88025)
	- work on Issue #155 - modified return of recipe (rev.6c1926f7)
	- work on Issue #155 - modified return of recipe (rev.9b15a96d)
	- work on Issue #155 - modified return of recipe (rev.f2614bdd)



================================================================================
* Fri Jun 15 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.046

================================================================================
	- fixed hidden bug (formats should be allowed to be None - chosen by astropy (rev.46ae2368)
	- fixed hidden bug (rev.9ce1dd61)
	- added extra check for bad key in WLOG (dev issue only) (rev.c53f0f10)
	- added some keys (OBJNAME, SBCDEN_P) (rev.5b7ab156)
	- updated date and version and added OFF_LISTING_FILE function (rev.66081073)
	- @FrancoisBouchy - Added commit: Creation of off_listing_RAW_spirou - modified to conform with DRS standards + functions + keywords + parameters (rev.05f8c0ba)
	- @FrancoisBouchy - Added commit: Flux ratio display with 3 digit (rev.caacabe7)
	- @FrancoisBouchy - Added commit: Background correction of the ref file (rev.aeedd35a)
	- @FrancoisBouchy - Added commit: Correction to avoid division by zero (rev.39cfc04f)



================================================================================
* Fri Jun 15 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.047

================================================================================
	- Flux ratio display with 3 digit (rev.82dd141b)
	- Background correction of the ref file (rev.a497783e)
	- #300 Bug on the fit_ccf on individual orders to investigate (rev.44ebb55b)
	- Correction to avoid division by zero (rev.8f45dc9b)



================================================================================
* Fri Jun 15 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.047

================================================================================
	- cal_WAVE_NEW_E2DS_spirou.py: first version (untested) (rev.da1d0d13)



================================================================================
* Mon Jun 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.048

================================================================================
	- rebuilt pdfs (rev.73fc1cbe)
	- updated doc strings (rev.aab89fbc)
	- updated author list (rev.1c2d99fe)
	- udpated date and version and added spirouFile command (rev.456d794e)
	- updated some function descriptions (rev.8c93383d)
	- Issue #330 - fixed comment description (rev.a3a390ef)
	- Issue #330 - fix WLOG message (rev.979a80fb)
	- Issue #330 - add pol_spirou to recipe control (rev.82829987)
	- Issue #330 - fix entry value, set sources keys, and float(nexp) --> int(nexp) (rev.5f19d6f0)
	- Issue #330 - change scatter --> plot (rev.a949e786)
	- Issue #330 - add keyword kw_CMMTSEQ (rev.4af7466c)
	- Issue #330 - fix constant value (run tested correction) (rev.df480f94)
	- Issue #330 - fix setup and a few other minor (run tested correction) (rev.182db263)
	- fix bug and cleanup the imports (rev.61d43b70)
	- Update config.py (rev.5e9f1431)
	- renamed and chmod files (rev.c7e01c3a)
	- renaming file (rev.2cc1ed8c)
	- rename file (rev.64dc2374)
	- Issue #330 - Adding plots for polarimetry (rev.674bf5bc)
	- Issue #330 - alaises for spirouPOLAR (rev.704cb1d8)
	- Issue #330 - re-write of SPIROU polarimetry module (for DRS compatibility class --> functions) (rev.82c8a960)
	- Issue #330 - Adding keywords for polarimetry (rev.a36f3ea6)
	- updated date and version (rev.7e9af3a7)
	- Issue #330 - Adding file name definitions for polarimetry (rev.3e18da5e)
	- Issue #330 - Adding constants for polarimetry (rev.be98e299)
	- Issue #330: integrating pol_spirou from @edermartioli into DRS format (rev.9af1599f)



================================================================================
* Tue Jun 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.049

================================================================================
	- corrected bug in night_name error reporting (rev.f46eb44b)
	- updated documentation (function definitions) (rev.b5436ced)
	- improved functionality in reset (allow reset of calibDB or reduced or log or all via user input) (rev.0f1718da)
	- improved reporting of bad night name (rev.a4a2b896)
	- removed old misc files (rev.79a733ca)
	- add obj name to raw files if no other suffix added (for objects) (rev.6954c36d)
	- added preprocessed trigger (for automating pre-processing on DRS_RAW_DATA directory) (rev.3fb28279)
	- fixed bug with processed suffix (rev.f9d40d5d)



================================================================================
* Tue Jun 19 2018 Eder <edermartioli@gmail.com> - 0.2.050

================================================================================
	- changed config to my local paths (rev.8f6ef8c2)
	- put config back (rev.875dd72c)
	- non (rev.196f25dc)



================================================================================
* Wed Jun 20 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.051

================================================================================
	- no main file (rev.e9d5b26f)
	- must use unit test to run recipes (rev.2a237309)
	- undo print test (rev.c7291ae9)
	- updated chmod (rev.52133915)
	- fixes to main raw trigger (rev.22681854)
	- corrected bug where OFF_LISTING_FILE was missing (rev.31e5555d)
	- corrected bug where no night name does give good error (rev.30ebe0df)
	- fixed bug that arg_night_name and files not checked any more (rev.cbc01dcf)
	- fixed bug with no DRPTYPE assigned (rev.1c48f325)
	- modified recipe control (added order and detector validity) (rev.ff36a1b3)
	- fisrt commit - raw file trigger (cal_dark to cal_extract) (rev.0e83cb49)



================================================================================
* Wed Jun 20 2018 Eder <edermartioli@gmail.com> - 0.2.051

================================================================================
	- config.py (rev.1d60b770)



================================================================================
* Thu Jun 21 2018 Eder <edermartioli@gmail.com> - 0.2.052

================================================================================
	- Implemented polarimetric errors calculation (rev.7ccd3453)
	- Implemented polarimetric errors calculation (rev.0e8360ac)
	- Changed polarimetry stuff to adapt changes made by Neil (rev.bce9bcf3)



================================================================================
* Thu Jun 21 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.052

================================================================================
	- fix to print out (rev.d41abb31)
	- updated files for reset (rev.7bcbae15)
	- added new wavesolution to cal reset (rev.33d8510b)
	- Work on Issue #338 - added possibility to enter debug mode and added the table printed to screen (rev.d1ef6749)
	- update date and version (rev.dc09b965)
	- added catch of warnings with polyfit (rev.ed5d5f07)
	- added catch warning for polyfit, fixed bug with lamp_type in decide_on_lamp_type (rev.1acce90e)
	- added missing plot function (wave_fp_wavelength_residuals), added iteration number to plots for wave_littrow_check_plot and wave_plot_final_fp_order (rev.9cbcd071)
	- added doc string to cal_HC main function (rev.b9fc172b)
	- work on issue #337: modified decide_on_lamp_type function to accept ic_lamps values as lists (and iterate through) - still must only have one of the two (rev.449b5be5)
	- updated constants in H2RG to match H4RG (rev.c792e03b)
	- work on issue #337: changed ic_lamps values to be lists + cleaned up constants (pep8) (rev.6f31580b)
	- Work on Issue #337: slight clean up of @FrancoisBouchy changes. Renamed part1b to part2 and commented out old part 2 (rev.1222acc0)
	- fix - spirouUnitRecipes.wrapper requires true python strings (rev.9e637e24)



================================================================================
* Thu Jun 21 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.052

================================================================================
	- Part 1b created as a copy of Part 2 and Modified (rev.8b47b845)
	- Adaptation of all the parameters for cal_HC (rev.7127739e)
	- Change e2ds with e2dsff to define the wave filename (rev.51cee109)
	- Define ord_start and ord_final for the first guess solution (rev.b4acb0c3)



================================================================================
* Fri Jun 22 2018 Eder <edermartioli@gmail.com> - 0.2.052

================================================================================
	- Update output name without _A, save errors to output using WriteImageMulti (rev.f516b14a)
	- Update output name without _A, save errors to output using WriteImageMulti (rev.f9030a88)
	- Update output name without _A, save errors to output using WriteImageMulti (rev.2cd24a84)
	- Implemented total flux (Stokes I) calculation (rev.4d53ffcc)



================================================================================
* Fri Jun 22 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.052

================================================================================
	- fixed to run with new setup (rev.5c40efaa)
	- fix for warninglogger (rev.204bf708)
	- log handled exits! (rev.b3becd14)
	- fixed setup for badpix (rev.2db41ae9)
	- fix set up changes (rev.5b9b3bbf)
	- update set up begin function (rev.14c76e9b)
	- updated setup (use of spirouStartup.Begin) (rev.c398c023)
	- dealt with recipe name handling better (rev.0b440637)
	- fix program with recipe name instead of sys.argv (unless not present) (rev.e7760781)
	- fix recipe setup (rev.abf777b2)
	- updated master time (rev.e8d57edd)
	- fixed system exit quitting automated run (rev.1f9d02c5)
	- Now cleaning WLOG in run_begin (via WLOG.clean_log()), and added main_end_script (to push logging to p and run clean_log) (rev.8b489bba)
	- Added function write_image_multi (aliased to WriteImageMulti) to save multiple extensions to filename - for @edermartioli and the pol_spirou code specifically (rev.016c5c4e)
	- defined logger function into class (allows storage or any errors/warnings/info and piping back into p at the end of recipe. Must clear WLOG at start and end of recipes! (rev.ecccdba5)
	- Fix for issue #337 - add e2dsff as well as e2ds (defaults to e2dsff if present) and added log_storage_keys pseudo variable (rev.c1e61edd)
	- updated trigger to add error and logger values to HISTORY.txt (rev.51755315)
	- updated recipes main end script (to allow piping of logging into p - thus accessible outside via ll['p']['LOGGING_ERROR'] for example (rev.a8073d32)



================================================================================
* Fri Jun 22 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.253

================================================================================
	- cal_WAVE_NEW_E2DS_spirou.py: first version (untested) (rev.8475802e)



================================================================================
* Sun Jun 24 2018 Neil Cook <neil.james.cook@gmail.com> - 0.254

================================================================================
	- update date and version (rev.f403e9b5)
	- fix for loggers being out of range (rev.d8692d31)



================================================================================
* Tue Jun 26 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.055

================================================================================
	- added cal_hc and cal_wave to unit test definitions (rev.f12246fe)
	- fix to cal_HC and cal_WAVE added to unit test runs (rev.0c122c22)
	- added printout of max time for calibDB (rev.150428a4)
	- added cal_HC, cal_WAVE (and setup for cal_WAVE_NEW) to all run (rev.69bfbbec)
	- we have FIBER therefore use FIBER not FIB_TYP, modified error reporting give we use header keys (rev.9f087540)
	- fixed bug that allows reduced files to be None (should be found by file name or generate error) (rev.a609ec16)
	- added e2dsff files to recipe control for cal_HC and cal_WAVE, added cal_WAVE_NEW files (same as cal_WAVE) (rev.9508fef7)
	- fixed typo (bug?) (rev.af93dc0b)
	- updated to work with odometer identification (like rest of DRS) (rev.d8f20f22)
	- update for use with e2dsff files as well as e2ds files (rev.7ff394fb)
	- fixed bug in header key berv_max (rev.08f8944a)
	- Update pol_spirou.py (rev.698b104b)
	- add calibDB setup to cal_validiate (rev.c4cb6858)
	- add BERV corrections to header (rev.666897a0)
	- added cal_preprocess, off_listing, visu_raw, visa_e2ds and pol_spirou to the unit testing (rev.17b1b495)
	- modified a warning message to be slightly more descriptive (rev.6e333888)
	- Issue #348 - fixed definition of WLOG in spirouPlot ("sometimes" causes a crash sometimes doesn't) (rev.dd89d969)
	- update date and version (rev.a596936c)
	- undo bad merge by @melissa-hobson (rev.8317474e)
	- Revert changes to get wave solution from calibDB (errors were due to badly set up calibDB) (rev.6489937f)
	- Merged changes from @edermartioli: added alias to calculate_stokes_i and added aliases to __all__ (rev.caa596c3)
	- Merged changes from @edermartioli: Update output name with _A, save errors to output using WriteImageMulti, Implemented total flux (Stokes I) calculation, implemented polarimetric error calculation. (rev.569120ee)
	- Merged changes from @edermartioli: aqdded stokesI plot, spelling correction + polarisation is now percentage (bug was missing in conversion) (rev.ae695cfd)
	- Merged changes from @edermartioli: Update output name with _A, save errors to output using WriteImageMulti, Implemented total flux (Stokes I) calculation, implemented polarimetric error calculation. (rev.553fb412)
	- added warning in config.py to not change PATHs here (todo in docs) (rev.0b7576fb)
	- Merged changes from @edermartioli: Update output name with _A, save errors to output using WriteImageMulti, Implemented total flux (Stokes I) calculation, implemented polarimetric error calculation. (rev.b7944412)



================================================================================
* Tue Jun 26 2018 Eder <edermartioli@gmail.com> - 0.2.055

================================================================================
	- fixed bugs in plot and added new keywords to polar products (rev.fa1bba6c)
	- fixed bugs in plot and added new keywords (rev.27c89465)
	- reset config.py (rev.e3c318fe)
	- Merging changes (rev.204f8999)



================================================================================
* Tue Jun 26 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.055

================================================================================
	- Update spirouTHORCA.GetLampParams to identify lamp type from fiber position header key (rev.a1848421)
	- visu_WAVE_spirou: higher base level for lines (rev.53042ff1)
	- Update for visu_WAVE_spirou.py - now working (rev.42411460)
	- cal_HC_E2DS_spirou.py: added fiber position identification from fiber type (rev.a27a51b0)
	- cal_HC_E2DS_spirou.py: added fiber position identification from fiber type (rev.5dce7093)
	- cal_HC_E2DS_spirou.py: added fiber position identification from fiber type (rev.db6de7a2)
	- Log calibDB match method (rev.b5fe833e)
	- cal_WAVE_NEW_E2DS_spirou.py: first version (untested) (rev.3d760b70)



================================================================================
* Wed Jun 27 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.056

================================================================================
	- first commit of spirouPOLOAR module tex file (rev.4dc55492)
	- update main init (rev.74e84ad2)
	- add spirouPOLAR to aliases (rev.09a032bc)
	- doc string update (rev.cbada37e)
	- doc string update (rev.7e9f7c3d)
	- doc string update (rev.31f11c39)
	- move functions around and add todo/fixme (rev.281fc5b8)
	- doc string update (rev.0157bfaa)
	- update date and version (rev.7c177217)
	- rebuild pdf after doc string update (rev.a7c7fa69)
	- update date and versions (rev.c770ef45)
	- doc string update (rev.79f8cb49)
	- doc string update (rev.8467838b)
	- doc string update (rev.41afb366)
	- doc string update (rev.7ac8493b)
	- doc string update (rev.da6ab910)
	- doc string update (rev.e6a00730)
	- added new tool to calculate barycentric velocity and add it to the header of the input file (rev.8f87988d)
	- added a skip check to check_file (rev.08adba77)



================================================================================
* Thu Jun 28 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.057

================================================================================
	- updated date and version and added new recipes (rev.dc4a4d62)
	- rebuilt pdfs (rev.943f5d75)
	- rebuilt pdfs (rev.048e155b)
	- rebuilt pdfs (rev.9552b644)
	- added more variable definitions (rev.0ce9edec)
	- update to variables - adding new ones (rev.9a71fc23)
	- update to comment (rev.8c70aa33)
	- tried to speed up plotting + fixed a bug with call to spirouTHORCA.GetLampParams (now requires header) (rev.7ed4f7fb)
	- fix python 2/python 3 incompatibility with numpy change (rev.f1c5b32e)
	- fix call to fiber_params change (from circular import bug) (rev.ec7434a8)
	- doc string update - requires spirouPOLAR command (rev.1ca773dc)
	- fix circulate import bug --> move fiber_params from spirouLOCOR to spirouFile and update calls accordingly (rev.e299ad82)



================================================================================
* Thu Jun 28 2018 Eder <edermartioli@gmail.com> - 0.2.057

================================================================================
	- Swap exposure 3 and 4 to agree with actual SPIRou sequence, and added doc string to spirouPolar functions (rev.b3574045)



================================================================================
* Fri Jun 29 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.057

================================================================================
	- rebuild pdf (rev.7aeb45b6)
	- rebuild pdf (rev.e8c1577d)
	- rebuild pdf (rev.92e379b8)
	- added variabels to cal_hc/cal_wave variable definitions (rev.6ec60d51)
	- added more cal_hc/cal_wave variable definitions (rev.4bf7f8d2)
	- removed old cal_hc constants (rev.d77aea51)
	- removed old cal_hc code (rev.004ad210)
	- rebuild pdf (rev.8419dd7d)
	- rebuild pdf (rev.47dcf7fa)
	- rebuild pdf (rev.518ceec4)
	- update version, date and module root definitions (rev.30356d99)
	- update variable definitions (rev.ae38d732)



================================================================================
* Tue Jul 03 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.058

================================================================================
	- add generic change log (not used but for history) (rev.3b9e519b)
	- make sure object name is "good" with function: get_good_object_name (rev.f456dddf)
	- correct typo (rev.3f90cbdb)
	- rebuild pdfs (rev.6e46c11f)
	- remove change log (rev.5fed5752)
	- add user_dir and cal_reset constants (rev.4605731f)
	- add pp mode variable (rev.7cd7591e)
	- update using the DRS with H4RG example (rev.16dbedea)
	- update todo list (remove done + add new) (rev.e312f62a)
	- update quick installation (rev.0bbae4d9)
	- update output keywords (not finished) (rev.ee7b4c34)
	- update installation (rev.3c090e1d)
	- update input keywords (rev.a0235588)
	- update date architecture (rev.12072a95)
	- removed old change log (rev.092ad7cf)
	- add pp_mode (the way to switch on/off) file type suffix adding (rev.b1030859)
	- add output files to p (and thus sent back to main() function call) (rev.bb499732)
	- update commentation (rev.52e14703)
	- updated module definitions in spirouPOLAR (rev.1732ac12)
	- updated doc strings to be consistent with rest of DRS (rev.67bb777e)
	- Update pol_spirou.py (rev.e3603014)
	- Update spirouPOLAR.py (rev.069eb88a)
	- Update spirouPlot.py (rev.97bb96d1)
	- rebuilt pdf (rev.723794c4)
	- updated date and version (rev.5cb6a174)
	- rebuilt pdf (rev.58154cdf)
	- added variable definitions to wave solution section and qulaity control section (rev.335e6aeb)
	- rebuilt pdf (rev.58d829da)
	- updated date and version (rev.a35bda77)
	- updated date and version (rev.a334fe2a)


================================================================================
* Wed Jul 04 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.059

================================================================================
	- update change log (rev.14dc9124)
	- update change log (rev.17012c5b)
	- the output changelog (rev.5b9c1771)
	- added functionality to update VERSION.txt and the version in the spirouConst.py file (rev.f93ca422)
	- DRS version added to VERSION.txt (rev.716e6da5)
	- recipe to get/update change log (moved to spirouTools - final location) (rev.366f9e2d)
	- recipe to get/update change log (rev.466217d8)
	- output: the change log (backup) (rev.e3ae78d8)



================================================================================
* Thu Jul 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.060

================================================================================
	- fix and test of find_lines (rev.77ca6c26)



================================================================================
* Mon Jul 09 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.061

================================================================================
	- removed berv calculation from RV module (rev.ee54c282)
	- added print_full_table function (rev.66483781)
	- updated aliases and __all_ (rev.2e3c7544)
	- updated aliases and __all_ (rev.9317b4eb)
	- updated aliases and __all_ (rev.069848f0)
	- moved earth barycentric correction here (rev.9bdb58a9)
	- test fitting versus interpolation (rev.599d8d24)
	- updated test to only show "good" orders (rev.0ccbeca8)
	- fixed a comment and updated the berv variable (rev.eea3d51e)
	- fixed logging all analysed files and printing to screen (rev.d62ecea9)
	- fixed off_listing printing only a few rows (now prints all) (rev.cc825d1b)
	- moved berv calculation to extraction (rev.9516e55d)
	- moved berv calculation to extraction (rev.efd05451)



================================================================================
* Tue Jul 10 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.062

================================================================================
	- added filename functions (WAVE_MAP_SPE_FILE and WAVE_MAP_SPE0_FILE) (rev.200b94f3)
	- added filenames in spirouConfig (rev.6dc52656)
	- define todos (rev.b3ae08b8)
	- fix bug: night_name should only be a string (could be a int) (rev.183ffaa3)
	- update to accept multiple fibers AB and C or A B and C or any combination (rev.49a86896)
	- change the files tested (rev.a1c28522)
	- fix to a bug ll_line_cat --> ll_line_fit (rev.64e31772)
	- e2ds back projection - first commit (rev.a4a29ab8)
	- fix for choice of fiber(s) (rev.98751d51)



================================================================================
* Wed Jul 11 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.063

================================================================================
	- add master_tellu_spirou file (rev.b802cfeb)
	- add cal_wave_mapper to recipe control file (rev.4b824404)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.56a984f1)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.1bedc55f)
	- add reset tellu to drs_reset functions (rev.9caad51a)
	- adde dcal_wave_mapper to recipe list (and unit recipe) (rev.39c8a9bc)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.1b6acf69)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.45ddf813)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.55e5a2a6)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.b23a500d)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) + added printing of tilt/wave/blaze/flat file used (rev.b76dee65)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.cea44b5f)
	- fixed bug: hdr['KW_X'] --> hdr[p['KW_X'][0]] (rev.2a2cd8a4)
	- add telluDB constants (rev.131d1767)
	- add telluDB (for now a copy of spirouCDB - but will change) (rev.0392d8af)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.3e706ac6)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.548af301)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.811ff6a3)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.db9c88c5)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.bec2f117)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.f620fd40)
	- update cal_wave_mapper (as main function with returns to local) (rev.bafcb677)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.ebddd8f0)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.fce4d026)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.53b1c68d)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.9a7b7b50)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.a9157257)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.5d911a40)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.3b2fe5bc)
	- rename calibDB module: spirouCDB --> spirouDB (to add telluric database) (rev.c7053fea)



================================================================================
* Thu Jul 12 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.064

================================================================================
	- first commit - added obj_mk_tellu functions (rev.11cb25f1)
	- added spirouTelluric aliases (rev.0cb7a927)
	- added wave param aliases (rev.a7f365a3)
	- added read andget wave param functions (rev.cb14c7b1)
	- added plot for obj_mk_tellu (rev.4d0208e5)
	- added file name definitions for obj_mk_tellu (rev.b65b6122)
	- added obj_mk_tellu to recipe control (rev.971d3a40)
	- added obj_mk_tellu constants (rev.dcafd2bc)
	- integrated obj_mmk_tellu into spirou drs (rea/write/constants etc) (rev.563d5bcb)
	- added saving of wave parameters to header of E2DS (rev.0b92cca0)
	- remove (rev.0cc6033d)
	- copy of etiennes raw mk_tellu code (rev.e5c8b722)
	- added imports to python local namespace (for embeded run after code finish) (rev.8dd15555)
	- blank files for telluric functions (rev.e8f545ba)
	- first commit of the spirou visu GUI (rev.18f5e438)
	- first commit of obj_mk_tellu - processing the telluric files and adding them to telluDB (rev.239dca54)



================================================================================
* Fri Jul 13 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.065

================================================================================
	- add functions: calculate_absorption_pca, get_berv_value (rev.7b7973a7)
	- add telluric aliases (rev.192a0f5c)
	- add functions get_database_tell_template, update_database_tell_temp (rev.92d37d3d)
	- continue to integrate functions (rev.7762dbb6)
	- correct duplication of header is None (rev.3c9c3d86)
	- added telluric alias (rev.5d5421f7)
	- added telluric pca plot (rev.904eeba1)
	- corrected bad function call to GetNormalizedBlaze and duplicated call to loc=ParamDict() (rev.fe70d350)
	- moved getting berv to spirouTelluric (rev.9a0d59b0)
	- first attempt at integrating code (unfinished) (rev.34f85593)
	- add keys defined in functions (rev.79397ed7)
	- add new TDB aliases (rev.c9112a46)
	- correct access to telluric database and update telluric database (rev.a5942e55)
	- first commit - direct integration of mk_template.py from Etienne (rev.7d06e7c9)
	- first commit - blank (rev.a54039a4)
	- updated where we get the telluric molecular file (now from database) (rev.ab0066d6)
	- added getting of absolute path for telluric files (rev.b3c5c11e)
	- added switch between telluricand calibration databases (rev.fbeaa5c3)
	- added aliases from TDB (rev.8c4c6988)
	- added get and update functions (wrapping generic functions in spirouDB) (rev.0a538911)
	- added todo's to make general (rev.9e262156)
	- first commit - generic functions for database management (rev.52ba975f)



================================================================================
* Sun Jul 15 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.066

================================================================================
	- add new mask from Xavier (rev.44edfbf3)
	- changed encoding (copy/paste/revert) -- ignore (rev.dcdae94d)
	- fixed log to not wrap this text - ONLY (rev.1feca27b)
	- changed name of sub-module (rev.1fc00efc)
	- fixed cyclic imports (new sub-module - spirouBERV) (rev.afe9a5a1)
	- Fixed cyclic imports (rev.c651c28f)
	- added character_log_length pseudo constant (rev.379f773d)
	- added maximum log length (wraps to new row with a tab) wraps words but still problem with long filenames (rev.6ae91108)
	- fixed typo in Merge from @FrancoisBouchy (rev.8326be0e)
	- fixed cyclic importing and typos in keyword assignment (rev.8a94f556)
	- Fixed cyclic importing (rev.d8a59f6f)
	- Bring S1D (cal_extract) in-line with rest of DRS (Fixing merges from @FrancoisBouchy) (rev.e64b267a)
	- Bring S1D (cal_extract) in-line with rest of DRS (Fixing merges from @FrancoisBouchy) (rev.a294ced9)
	- Bring S1D (cal_extract) in-line with rest of DRS (Fixing merges from @FrancoisBouchy) (rev.7f888956)
	- Bring S1D (cal_extract) in-line with rest of DRS (Fixing merges from @FrancoisBouchy) (rev.bbb63b34)
	- Bring S1D (cal_extract) in-line with rest of DRS (Fixing merges from @FrancoisBouchy) (rev.79422a76)
	- Bring S1D (cal_extract) in-line with rest of DRS (Fixing merges from @FrancoisBouchy) (rev.431a3097)
	- Bring S1D (cal_extract) in-line with rest of DRS (Fixing merges from @FrancoisBouchy) (rev.680d20bf)
	- Added spirouTelluric to modules list (rev.96a45ba6)
	- fix pep8 issues (in-line comment should have at least two spaces between code and comment (rev.d9d67042)
	- Merge @FrancoisBouchy changes - still need fixing (PEP8 and integration) (rev.67cf7d9e)
	- Merge @FrancoisBouchy changes - still need fixing (PEP8 and integration) (rev.a9dde403)
	- Merge @FrancoisBouchy changes - still need fixing (PEP8 and integration) (rev.92c9e64d)
	- Merge @FrancoisBouchy changes - still need fixing (PEP8 and integration) (rev.07e45462)
	- Merge @FrancoisBouchy changes - still need fixing (PEP8 and integration) (rev.6812fdb2)
	- Merge @FrancoisBouchy changes - still need fixing (PEP8 and integration) (rev.1f699ee2)
	- Merge @FrancoisBouchy changes - still need fixing (PEP8 and integration) (rev.8b5f5734)
	- Fix needed commented code (commented for testing) --> uncommented now (rev.1b3eb3fd)
	- updated construct_convolution_kernal2 function (rev.d76ebeef)
	- added teullric aliases (rev.c70f99bf)
	- added tellu_fit_tellu_spline_plot function (rev.ea195472)
	- update ConstructConvKernel2 function (rev.c840a850)
	- continued to merge Etiennes code (rev.5e0792a8)



================================================================================
* Mon Jul 16 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.67

================================================================================
	- telluric integration: bug fixes (after move of functions) (rev.e14337ef)
	- updated call to plot (rev.0e42ee0a)
	- moved debug plot back to main code (rev.632d5eec)
	- updating integration of tellu files: added functions - interp_at_shifted_wavelengths, calc_recon_abso, calc_molecular_absorption and lin_mini (rev.eca587ea)
	- updating integration of tellu files: added new function aliases (rev.a5e68450)
	- updating integration of tellu files: added plot function "tellu_fit_recon_abso_plot" (rev.b47ec6b3)
	- updating integration of tellu files: Added abso output keyword (rev.b719cd11)
	- updating integration of tellu files; Added filename pseudo constants (rev.1e33b4a1)
	- updating integration of tellu files: added constants (need commenting!) (rev.b1f12bfa)
	- updating integration of tellu files (rev.426ff830)
	- updating integration of tellu files (rev.f4ef1297)



================================================================================
* Tue Jul 17 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.68

================================================================================
	- copy (same) (rev.ea4f78ac)
	- update tellu recipes: fix bug with file name (rev.50acc4f5)
	- update tellu recipes: drs telluDB reset now resets telluDB not calibDB (fix typos) (rev.e796a80b)
	- update tellu recipes: fix after test run FWHM is function not object (rev.05659100)
	- update tellu recipes: fix after test run - telluDB get database values are already split on spaces (rev.5c1ada01)
	- update tellu recipes: fix after test run - fix bug (needed ```enumerate(lines)```) (rev.7c832174)
	- update tellu recipes: fix after test run - add alias to update_datebase_tell_temp (rev.9655cb6f)
	- possible bug fix: tried to separate out interactive options in end_interactive_session function (rev.a839f26d)
	- possible bug fix: tried to reduce repetition of displayed warnings (rev.e301be46)
	- update tellu recipes: added AIRMASS header key (rev.77c67374)
	- bug fix: fix file name ````'_s1d_{0}.fits'``` --> ```'_s1d_{0}.fits'.format(p['FIBER'])``` (rev.706e4a4b)
	- update tellu recipes: add required line in master telluDB (rev.0a14e56d)
	- update tellu recipes: add obj_mk_tell_template to recipe control (rev.7c9895ad)
	- update tellu recipes: move obj_mk_tell_template constantsto here and correct some bugs after test run (rev.98bbfe8a)
	- update tellu recipes: fix after test run (rev.4c405049)
	- update tellu recipes: fix after test run (rev.f8387526)


================================================================================
* Wed Jul 18 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.069

================================================================================
	- integrate telluric recipes with test runs: updated after test runs (rev.2a56529a)
	- integrate telluric recipes with test runs: added get_wave_keys function (rev.764ad44b)
	- integrate telluric recipes with test runs: updated aliases (rev.d2635ec2)
	- integrate telluric recipes with test runs: test run only (rev.3c1a6ad2)
	- integrate telluric recipes with test runs: updated plots (corrected) (rev.dccf1ff3)
	- integrate telluric recipes with test runs: resorted use_keys + added wave and telluric keys (rev.2884a947)
	- updated filename (TELLU_FIT_OUT_FILE) (rev.0537a839)
	- integrate telluric recipes with test runs: added constants from Etienne and corrected bug in tell_lambda_max (rev.1cea1808)
	- integrate telluric recipes with test runs: update after running fit_tellu (rev.8525785d)
	- integrate telluric recipes with test runs: update after running fit_tellu (rev.c904711e)
	- integrate telluric recipes with test runs: test run only (rev.7cbe7b40)
	- modified cal_extract to save wavefile name and wave file dates (for telluric) (rev.0a52c288)



================================================================================
* Thu Jul 19 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.070

================================================================================
	- add telluric database reset to cal_validate (rev.bcf3dc94)
	- tellu recipes - bug fix for plot (rev.324d79be)
	- fix bug with timestamp (telluDB only) (rev.bebe2a37)
	- integrate telluric recipes with test runs: compressed + binned tapas_all_sp file (rev.1ba578dc)
	- integrate telluric recipes with test runs: updated after test runs (rev.9ce2af04)
	- integrate telluric recipes with test runs: updated error message in get_param (rev.489dd801)
	- cal_preprocess - DPRTYPE = None  rows of recipe_control should not be used to ID files (rev.0232ed48)
	- integrate telluric recipes with test runs: fixes afer test runs (rev.df28b8a9)
	- integrate telluric recipes with test runs: updated aliases (rev.a61e6c8a)
	- integrate telluric recipes with test runs: updated TELL_MOLE file (.gz) (rev.85e317b1)
	- integrate telluric recipes with test runs: fixes afer test runs (rev.a687ff10)
	- integrate telluric recipes with test runs: fixes afer test runs (rev.9b6c82db)
	- integrate telluric recipes with test runs: fixes afer test runs (rev.89ac9788)



================================================================================
* Fri Jul 20 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.071

================================================================================
	- update test run (rev.283ce6f9)
	- misc functions (rev.c80005f5)
	- Fixed call to earth velocity correction function (rev.107d3dca)
	- move get_good_object_name function (rev.3101c114)
	- add aliases for getting obj name and airmass (rev.8d873247)
	- fix acquisition time naming (rev.e5fda006)
	- added file iteration to plot (rev.7e4f1585)
	- fix acquitision time naming (julian not unix) (rev.75d685df)
	- add tellu template file definition (rev.ae4bab60)
	- remove extra recipe control key (rev.c3b3248a)
	- move objname and airmass to functions (rev.a2ecbe8f)
	- fix naming conversion time is julian not unix (rev.90525073)
	- correct filename bug (rev.ad763020)
	- fixed bug with convolve file not being read correctly (rev.d1276a09)
	- fxied bug with get_param (rev.5936a8ec)
	- fxied bug with get_param (rev.bb945613)
	- fxied bug with get_param (rev.547d5b94)
	- fix bug in get_wave_solution (rev.fe98481a)
	- fixed but with header key too long (9 > 8) (rev.0092c861)
	- fix bug in assigned WAVEFILE (rev.f2fedbf0)
	- fix bug in get_param call (rev.66c7b9d1)



================================================================================
* Wed Aug 08 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.072

================================================================================
	- correctioned some constants and added value to loc (rev.6f0ce414)
	- added definitions from FP files and EA wave files (rev.b38c9099)
	- updated cal_WAVE_E2DS files to check for (rev.1e93422f)
	- part2 test and updated/corrected some constants (rev.f76330ab)
	- added background subtraction (rev.26f2c5cb)
	- title to the plots + action TODO to find the right FIBER type (rev.e389f0f9)
	- Refinement of the cut of the left edge of blue orders for localisation - merge from @FrancoisBouchy (rev.9132e301)
	- Use only the part of E2DS > 0 to build the S1D spectra (rev.b10a0ce5)
	- Read the OBSTYPE before computing BERV - OBSTYPE should be OBJECT to derive the BERV (i.e. not for calibrations) - merge from @FrancoisBouchy (rev.8d991bd9)
	- some cosmetic / improvement for plot display - merged from @FrancoisBouchy (rev.ab287bbd)
	- updated constants + new definition for the blue window on DARK - uc_fracminblaze = 16, new param to restrict the wings of spectral orders with flux lower than flux_at_blaze / 16, spectral order 0 is not taken into account (rev.ad89c21c)
	- correction of center of the blaze window - put to zero edge of the spectra hwere flux is too low (less than flux_at_blaze/ IC_FRACMINBLAZE) - merged from @FrancoisBouchy (rev.3931475f)
	- put to zero part of spectra where the blaze is not defined (rev.97dc2b42)
	- add the background subtraction - from @FrancoisBouchy (rev.74d66d09)
	- @melissa-hobson correct call to GetLampParams (rev.e0da9f78)
	- added fiber position identification from fiber type (rev.e868a1e7)
	- first version cal_WAVE developed by @eartigau, adapted to DRS format by @melissa-hobson (rev.d52734f1)



================================================================================
* Tue Jun 26 2018 Melissa Hobson <melissa.hobson@lam.fr> - 0.2.073

================================================================================
	- cal_HC_E2DS_spirou.py: added fiber position identification from fiber type (rev.417a2fff)



================================================================================
* Thu Jun 28 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.075

================================================================================
	- visu_WAVE_spirou.py: correct call to GetLampParams (rev.07c55f21)



================================================================================
* Wed Jul 04 2018 Eder <edermartioli@gmail.com> - 0.2.074

================================================================================
	- Removed duplicated function calculate_stokes_i in spirouPOLAR.py (rev.720f9328)



================================================================================
* Wed Jul 11 2018 Eder <edermartioli@gmail.com> - 0.2.075

================================================================================
	- Removed small comment -- nothing really (rev.525778d8)



================================================================================
* Fri Jul 13 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.076

================================================================================
	- New correlation Mask made by XD (rev.1aecdfd1)
	- Background correction and set negative values to zero (rev.c823decf)
	- Background correction and negative values set to zero (rev.2948af8c)
	- Typo correction to read the fitted lines (rev.01a09df4)
	- New constant parameters for background correction and e2dstos1d (rev.b6b07a87)
	- Adaptation of function to measure the global background in the image (rev.682f7a69)
	- Add the two new functions e2dstos1d and write_s1d (rev.ee2f17ce)
	- New function to write S1D spectra with the same format than HARPS (rev.e73b826d)
	- New function to build S1D spectra (rev.122582d1)



================================================================================
* Wed Jul 25 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.077

================================================================================
	- Improvement for the localisation (rev.50378c7d)
	- Adaptation parameters for localisation (rev.da1b0044)
	- Add the background subtraction (rev.492cbeae)



================================================================================
* Wed Jul 25 2018 Eder <edermartioli@gmail.com> - 0.2.078

================================================================================
	- Inserted filename, MJD, and MJDEND keywords from expsoures in polar sequence to the header of polarimetry products (rev.a67e6b16)



================================================================================
* Fri Jul 27 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.2.079

================================================================================
	- Title to the plots + Action TODO to find the right FIBER type (rev.f87574b4)
	- Refinement of the Cut of the left edge of blue orders for localisation (rev.9ae887b1)
	- Use only the part of E2DS > 0 to build the S1D spectra (rev.407d081b)
	- Read the OBSTYPE Before computing BERV (rev.9882d8f0)
	- Some cosmetic / improvemtn for plot display (rev.3d7a6029)
	- New definition for the blue window on DARK (rev.d551df04)
	- Add the background correction (rev.be4541f6)
	- Correction of center of the blaze window (rev.31314183)
	- Put to zero part of spectra where the blaze is not define (rev.885045bf)



================================================================================
* Wed Aug 01 2018 Melissa Hobson <melissa.hobson@lam.fr> - 0.2.080

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py: first version of cal_WAVE developed by @eartigau, adapted to DRS format (rev.69ddc1a1)



================================================================================
* Fri Aug 03 2018 Melissa Hobson <melissa.hobson@lam.fr> - 0.2.081

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py: (rev.47dfe48f)



================================================================================
* Tue Aug 07 2018 Melissa Hobson <melissa.hobson@lam.fr> - 0.2.082

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py: added posibility to set a pixel shift (rev.6e7b4d41)



================================================================================
* Wed Aug 08 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.083

================================================================================
	- Update spirouFITS.py (rev.9c1e44d0)



================================================================================
* Wed Aug 08 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.084

================================================================================
	- added fiber position identification from fiber type (rev.e868a1e7)



================================================================================
* Wed Aug 08 2018 Melissa Hobson <melissa.hobson@lam.fr> - 0.2.085

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py: (rev.a74cb795)



================================================================================
* Wed Aug 08 2018 Chris Usher <usher@cfht.hawaii.edu> - 0.2.086

================================================================================
	- Suppress warnings about truncating FITS comments. (rev.2e8ec30e)
	- Prevent measure_background_flatfield from throwing error. (rev.21c6ad6d)
	- Fixed scrambled FITS headers. (rev.cbc40ef7)



================================================================================
* Thu Aug 09 2018 Melissa Hobson <melissa.hobson@lam.fr> - 0.2.087

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py: incorporated extrapolation of Littrow solution for last two orders; added save to calibDB of good solutions (rev.e1695894)



================================================================================
* Mon Aug 13 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.088

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py: began incorporation of FP lines (work in progress) (rev.e20dd388)



================================================================================
* Tue Aug 14 2018 Eder <edermartioli@gmail.com> - 0.2.089

================================================================================
	- Implemented Least Squares Deconvolution (LSD) Analysis to polar module (rev.eb039258)
	- Implemented Least Squares Deconvolution (LSD) Analysis to polar module (rev.ca3f6ba4)



================================================================================
* Tue Aug 14 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.090

================================================================================
	- obj_fit_tellu.py: re-add blaze, set NaNs to zero in final e2ds (UNTESTED), as per #389, #390 (rev.f46b1016)
	- spirouLOCOR.py now prints name of localization file (Discussed in #387) (rev.a653edb7)
	- spirouStartup.py: removed lines that caused exit if DRS_PLOT was not set even when DRS_INTERACTIVE was set. Fixes #395 (rev.75a66a00)



================================================================================
* Tue Aug 14 2018 Chris Usher <usher@cfht.hawaii.edu> - 0.2.091

================================================================================
	- Fixed __NAME__ of obj_fit_tellu (rev.8031edd6)



================================================================================
* Wed Aug 15 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.092

================================================================================
	- Update config.py (rev.0f642023)
	- Update spirouFITS.py (rev.812a2125)
	- Delete vcs.xml (rev.4294be5e)
	- Update spirouConst.py (rev.9d522dd4)


================================================================================
* Wed Aug 15 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.093

================================================================================
	- update telluric unit test (rev.5841b207)
	- add obj_mk_tellu and obj_fit_tellu to the unit tests (rev.605b48e0)
	- turn off the LSD analysis (until problem fixed) (rev.93f6fba6)
	- added a telluric test (based on Neil's files) (rev.ffbeae28)
	- Fix to issue #398: The first time running obj_mk_tellu fails with an I/O problem - convolve_file was being saved to the wrong location (and hence put_file was failing to copy it to telluDB) (rev.62b3ca06)
	- updated descriptions (from Etienne) (rev.4e8dc33e)
	- updated date, changelog and version (rev.2ee7f3fd)



================================================================================
* Thu Aug 16 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.094

================================================================================
	- Issue #392: added per-processed version keyword (rev.5c3fdd5c)
	- Issue #392: added version to outputs (rev.655a2c2a)
	- Issue #392: added version to outputs (rev.4e48b229)
	- Issue #392: added version to outputs (rev.15bef5f4)
	- Issue #392: added version to outputs (rev.0e2e3939)
	- Issue #392: added version to outputs (rev.6b5e6be0)
	- Issue #392: added version to outputs (rev.6a3d7c72)
	- Issue #392: added version to outputs (rev.5d988c97)
	- Issue #392: added version to outputs (rev.83a8ad5e)
	- Issue #392: added version to outputs (rev.64322b80)
	- Issue #392: added version to outputs (rev.fd072135)
	- Issue #392: added version to outputs (rev.d0028096)
	- Issue #392: added version to outputs (rev.5e4c8156)
	- Issue #392: added version to outputs (rev.758ce865)
	- Issue #392: added version to outputs (rev.36441ecc)
	- Issue #392: added version to outputs (rev.0f1c1687)
	- Issue #392: added version to outputs (rev.cef09e6c)
	- Issue #392: added version to outputs (rev.bd011a12)
	- Entries prepared ready to fix issues #394 and #406 (rev.8dc95a91)
	- Issue #407: fix bug where split lines not all printed to log file (only to screen) (rev.e226a31e)



================================================================================
* Fri Aug 17 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.095

================================================================================
	- Issue #401 - Added check that number of TELLU_MAP files > number of PCA components (rev.ee52b3c7)
	- Issue #392 change "PPVERSION" to "PVERSION" - header key too long (rev.380cbf35)
	- Issue #405 - add message when reset userinput is not "yes" (rev.241dfdbb)



================================================================================
* Sat Aug 18 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.096

================================================================================
	- Issue #382 - added a position to check for FLATFILE and DARKFILE (must agree with ```recipe_control.txt```) (rev.9fe2d6d4)



================================================================================
* Thu Aug 16 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.097

================================================================================
	- NaN-to-zero change moved from obj_fit_tellu to cal_CCF (rev.7e046736)
	- Pixel shift incorporated to all wavelength solutions (rev.330b3b0b)



================================================================================
* Fri Aug 17 2018 Eder <edermartioli@gmail.com> - 0.2.098

================================================================================
	- Fixed memory issue by avoiding direct use of an nxn S^2 matrix (rev.9217deff)



================================================================================
* Sat Aug 18 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.099

================================================================================
	- fix to file name (allow e2ds and e2dsff by only replaceing "_A.fits" (rev.c4e3a0ce)
	- allow LSD process (now it is fixed) (rev.67e486d6)
	- update date, version, changelog (rev.2a05927a)



================================================================================
* Sat Aug 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.101

================================================================================
	- Update spirouMath.py (rev.f759846c)



================================================================================
* Sat Aug 18 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.102

================================================================================
	- Issue #411: reset cal_wave changes from Melissa (not working with unit_test 20180409all.run (rev.80268e99)
	- update version (rev.2331213e)



================================================================================
* Thu Aug 23 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.103

================================================================================
	- Re-write of median_one_over_f_noise function (Issue #420) (rev.d51982c9)
	- New alias for function re-write (Issue #420) (rev.a93af1fc)
	- Using new function (re-write) from issue #420 (rev.0233a30f)



================================================================================
* Thu Aug 23 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.104

================================================================================
	- add check_blacklist and get_blacklist functions (Issue #419) (rev.6a96b33e)
	- Add alias to check black list function (Issue #419) (rev.b8177d68)
	- Add alias to raw text file function (Issue #419) (rev.d0a9b1d6)
	- Add blacklist filename (Issue #419) (rev.2ffb4fa0)
	- Add code to read raw text file (Issue #419) (rev.38709cc4)
	- Add code to check for blacklisted file (Issue #419) (rev.be00d692)
	- Add blacklist file (Issue #419) (rev.2b243a4d)
	- Issue #389 - NaN values vauses error to be raised (Needs to be fixed properly) (rev.d7541d1e)



================================================================================
* Fri Aug 24 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.105

================================================================================
	- Fix for Issue #406 - cal_CCF does not accept StokesI or e2dsff - fixed (rev.cd4b2c7c)
	- Fix for issue #406 - CCF recipe does not accept Stokes I spectra --> replace '_A.fits' with '_AB_StokesI.fits' (rev.b07359df)
	- Fix for Issue #406 -CCF recipe does not accept stokes I spectra --> replace '_A.fits' with '_AB_StokesI.fits' (rev.7c2a9116)
	- Fix for Issue #423 - cal_reset fails if folder does not exist (rev.1c57c390)
	- changed blacklist functino to look at objnames (Issue #419) (rev.78b6b335)
	- Changed blacklist file to object names (Issue #419) (rev.8a4c7982)
	- Moved blacklist check to after we have the OBJNAME (Issue #419) (rev.6d341eca)



================================================================================
* Mon Aug 27 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.106

================================================================================
	- Set pixel_shift_inter and pixel_shift_slope back to zero (Issue #411) (rev.b4bb88c3)



================================================================================
* Mon Aug 27 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.107

================================================================================
	- updated date, version and changelog (rev.2502f9c5)



================================================================================
* Tue Aug 21 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.108

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py: - check to remove double-fitted or spurious FP peaks - incorporation of FP lines (now working with no jumps) (rev.7bd5cce2)
	- spirouMATH.py, spirouTHORCA.py: redo pixel shift implementation (rev.9f0b3e3e)
	- Removed test prints (rev.a3bb973f)



================================================================================
* Wed Aug 22 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.109

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py: moved FP solution to spirouWAVE. (rev.279d8c06)



================================================================================
* Thu Aug 23 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.110

================================================================================
	- Update cal_HC_E2DS_spirou.py (rev.90c9ed8c)
	- Update spirouMath.py (rev.38026113)



================================================================================
* Thu Aug 23 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.111

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py update (rev.0a1d4be0)



================================================================================
* Mon Aug 27 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.112

================================================================================
	- updated date, version and changelog (rev.18bafb75)



================================================================================
* Tue Aug 28 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.113

================================================================================
	- First commit - Etienne's cal_HC - added functions for cal_hc_ea (rev.2e44e6b9)
	- First commit - Etienne's cal_HC - added call to spirouMath (rev.732d1b8b)
	- First commit - Etienne's cal_HC - moved lin_mini to spirouMath (rev.b50d180a)
	- First commit - Etienne's cal_HC - ReadTable/WriteTable/MakeTable correction when no formats (rev.0598daa4)
	- First commit - Etienne's cal_HC - wave_ea_plots (rev.2370e0bc)
	- First commit - Etienne's cal_HC - gauss functions and lin_mini (rev.2f122173)
	- First commit - Etienne's cal_HC - filename definition (rev.db5d5cf4)
	- First commit - Etienne's cal_HC (rev.52ee42a6)
	- Set pixel_shift_inter and pixel_shift_slope back to zero (Issue #411) (rev.3b795323)



================================================================================
* Wed Aug 29 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.114

================================================================================
	- added fixes to triplet fitting function (rev.9e737919)
	- added alias for the get_night_dirs function (GetNightDirs) (rev.722fa23b)
	- Fixed number of night_name dirs displayed on error (rev.b41baaba)
	- added night_name display limit (for when NIGHT_NAME is not an argument) (rev.b178a36b)
	- fix to bad copy and paste in spirouPlot (rev.d799bbb6)
	- Improvements to having no FOLDER name - now displays all available folders (rev.429799e8)
	- Improvements to off_listing - having no night_name argument now displays all available night_names (rev.59d78610)
	- Improvements to off_listing - having no night_name argument now displays all available night_names (rev.43bb3fc5)
	- Added off_listing_REDUC_spirou to allow listing of reduced folders (rev.60e30805)
	- Issue #428 - force calibDB wave solution - modify get_wave_keys (rev.605de20b)
	- Issue #428 - force calibDB wave solution - modify get_wave_solution (rev.c476923a)
	- Issue #428 - force calibDB wave solution - add constant switch (rev.6096c40d)
	- cal_HC_E2DS_EA - Set up for local running (rev.73e1f5cc)



================================================================================
* Wed Aug 29 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.115

================================================================================
	- TC3 initial wavelength solution (rev.3baddd60)



================================================================================
* Thu Aug 30 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.116

================================================================================
	- add off_listing_REDUC_spirou to recipes available for testing (rev.ebf2bcaa)
	- write a test for 18BQ01-Aug05 test files (20180805_test1.run) - Issue #400 (rev.e94c7f02)
	- fix micro seconds = 1e-6 not 1e-3 (rev.ec63483e)
	- fix bug with PATH in bashrc file (rev.7e8ad072)
	- add the resolution map (work-in-progress) (rev.34db4ee9)
	- fix bugs with cal_HC_E2DS_EA (rev.4e62fdf9)
	- fix bug with timestamp in logging (rev.bba7a275)
	- add writing of file for off_listing (rev.4e3b9566)



================================================================================
* Fri Aug 31 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.117

================================================================================
	- Added new wavelength solution and deleted files in data_example (not needed - run cal_reset or cal_validate) (rev.005f5fa5)



================================================================================
* Mon Aug 27 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.118

================================================================================
	- Issue #399 - copied in extra files (FILE_B and read me files) required by iers (but not currently linked to) (rev.8e7646fc)
	- Issue #399 - modification to iers to make offline (hopefully) given testing offline (rev.2be0b826)
	- Issue #399 - fix astropy_iers_dir to be the actual directory (rev.c9234bf6)



================================================================================
* Mon Aug 27 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.119

================================================================================
	- Added location to save astropy iers file (Issue #389) (rev.ba9cae58)
	- Possible fix for Issue #389: from @cusher - ```import astropy.utils.iers``` and set ```iers_table``` (rev.4bcc0a0d)



================================================================================
* Fri Aug 31 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.120

================================================================================
	- update date and version (rev.02ceb0f9)
	- script to manually add file to calibDB (from file in reduced folder) (rev.14dee133)
	- update change log/version and date (rev.4b37a9e0)
	- update master calibDB for reset (rev.473f0fa7)
	- reset cal_CCF set NaNs to zeros (Issue #389) (rev.ced3a142)



================================================================================
* Tue Sep 04 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.121

================================================================================
	- Add placeholder marker for the new cal_HC_E2DS_EA_spirou work (rev.07ead653)
	- modify generate_resolution_map --> fixes for integrating etiennes hcpeak functions (rev.f6a26ecc)
	- Enter todo to rename variable (rev.5134a486)
	- add plot for cal_HC_E2DS_EA_spirou (wave_ea_plot_line_profiles) and worker function (remove_first_last_ticks) (rev.7f67abf9)
	- Modify the gauss_fit_s function (cal_HC_EA_E2DS usuage) (rev.139910d5)
	- Separate input and output filename pseudo constant functions, added EA versions of cal_HC output filename definitions (rev.472a6e8e)
	- update leapsec log (rev.e8b051da)
	- Update to cal_HC_E2DS_EA_spirou - finish work on integrating Etienne's work (rev.fb6e1c6c)
	- Fix for S1D spectra - there may be occasions when we cannot convert to S1D - print a warning if this is the case (rev.400d6d0d)



================================================================================
* Mon Sep 03 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.122

================================================================================
	- manually incorporated possibility to read wavelength solution from calibDB (from dev2) (rev.f41f623a)



================================================================================
* Tue Sep 04 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.123

================================================================================
	- Move cal_HC_E2DS_EA constants to here (rev.875829dc)
	- Prep cal_HC_E2DS_EA for recipe run (add main function, move constants etc) (rev.0a8b9970)



================================================================================
* Wed Sep 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.2.124

================================================================================
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data), and added the obtaining of DPRTYPE to add  EXT_TYPE key to header (extraction output id key --> giving DPRTYPE for extracted files) (rev.0798e09e)
	- added a new log output to split up files to help see progress (rev.3ecfd669)
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data) (rev.207bda22)
	- Issue #429 - re-worked file identification only using header keys (no filename identification) (rev.876cd652)
	- Issue #429 - added kw_OUTPUT and kw_EXT_TYPE definitions for saving output header id and extraction output header id (rev.90a75498)
	- Issue #429 - added TAGFOLDER and TAGFILE functions and modified all fits-file definition functions to accept tags (rev.c7ae77f9)
	- Issue #429 - added get_tags function (rev.a2614ee2)
	- pep8 fixes (rev.87096f51)
	- Issue #429 - re-work recipe_control.txt to take into account added output keys (and check keys on start up) (rev.b14d93f0)
	- Issue #429 - definition of output header keys (based on output filename in spirouConst.py) (rev.ec6dae31)
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data) (rev.0e23fed3)
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data) (rev.e2f75088)
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data) (rev.d01d9bfd)
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data) (rev.94c9bffc)
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data) (rev.42c99315)
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data) (rev.d3f40be7)
	- Issue #429 - add output header key to identify output files (KW_OUTPUT) - defined in output_keys.py (SpirouDRS/data) (rev.5ed02b84)



================================================================================
* Wed Sep 05 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.125

================================================================================
	- cal_WAVE_E2DS_EA_spirou: updated HC section from cal_HC_E2DS_EA_spirou.py (rev.adf2cc99)
	- visu_E2DS_spirou, recipe_control: fiber is now obtained from file (Fixes #437) (rev.4cccc671)
	- visu_E2DS_spirou, recipe_control: fiber is now obtained from file (rev.39990d51)



================================================================================
* Wed Sep 05 2018 Melissa Hobson <melissa.hobson@lam.fr> - 0.2.126

================================================================================
	- commit local changes (rev.b9c64dfd)



================================================================================
* Wed Sep 05 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.2.127

================================================================================
	- spirouRV (for cal_DRIFTPEAK_E2DS_spirou) - Fix repetition of warning messages in while loop (rev.ba0d49a7)



================================================================================
* Thu Sep 06 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.2.128

================================================================================
	- spirouPlot: updated wave_ea_plot_per_order_hcguess: (rev.984c8d02)



================================================================================
* Thu Sep 06 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.000

================================================================================
	- Issue #418 spirouStartup.py - Make directory for NIGHT_NAME in TMP_DIR, index.fits saves to TMP_DIR, files are now checked for RAW in TMP_DIR (rev.315673f2)
	- Issue #418 spirouFile.py: obtaining tmppath and tmpfile to check for raw files (instead of rawpath which now throws error when used) (rev.553944ca)
	- Issue #418 spirouConfig: added TMP_DIR definition (as DRS_DATA_WORKING dir) (rev.a910b075)
	- Issue #418 cal_preprocess_spirou.py: made pp target raw folder but save to tmp dir (rev.50ff74b3)
	- updated notes (rev.18dd2a60)
	- updated the update notes (rev.423f5dee)
	- Added Update Notes (rev.c90c3858)
	- Update 20180805_test1.run to extract FP sequences and run DRIFT recipes (with extracted FPs) (rev.ac13ac1d)
	- update 20180409 test to include off_listing_RAW/REDUC and not include pol_spirou (do not have the raw files needed) (rev.a7a33fbf)
	- unit_test.py: Move Reset after set up (so errors reported before reset questions) (rev.b0c409e4)
	- Issue #429: spirouUnitRecipes.py: modify the outputs of off_listing recipes (distinguish between RAW and REDUCED listing) (rev.1d83c547)
	- Issue #429: calc_berv - modify input/output of WriteImage (for handling p['OUTPUTS']) (rev.4a876bc4)
	- Issue #429: spirouStartup.py modify "main_end_script" to index outputs or pre-processing - via functions "index_pp", "index_outputs", "indexing" and "sort_and_save_outputs" (rev.d492811e)
	- Issue #429: spirouStartup.__init__.py: alias sort_and_save_outputs to SortSaveOutputs (rev.a695104b)
	- Issue #429: spirouLSD - modify WriteImage to accept new input/output for writing p['OUTPUTS'] (rev.77f4eaed)
	- Issue #429: spirouTable: Add ways of making, reading and writing fits table (via astropy.table.Table) - functions added = make_fits_table, read_fits_table, write_fits_table (rev.570bc798)
	- Issue #429: spirouImage.py: replace "get_all_similar_files" function to look at header keys instead of file name (for cal_DRIFT recipes) (rev.160fb38e)
	- spirouFITS: modify write_image and write_image_multi to deal with writing output dict to p (via new function "write_output_dict") (rev.8e7c7d43)
	- spirouFile: add DRS_TYPE to identify RAW and REDUCED recipes (and pass to output processing later) (rev.bfa1ee45)
	- spirouImage.__init__: add aliases for make_fits_table, read_fits_table and write_fits_table (rev.3d4578dc)
	- spirouMath: reformat exception on timestamp (to print the input --> helps with debugging) (rev.13daa695)
	- spirouConst: add OFF_LISTING_RAW_FILE, OFF_LISTING_REDUC_FILE, INDEX_OUTPUT_FILENAME, OUTPUT_FILE_HEADER_KEYS, RAW_OUTPUT_COLUMNS, REDUC_OUTPUT_COLUMNS functions (rev.a702c193)
	- modify unresize.py with the output to WriteImage (outputs management) (rev.189b375b)
	- update cal_drift_raw for outputs (but not file list) (rev.44bc7f79)
	- Re-work off_listing recipes to look at the index files first (Much faster) - and to update the index files (rev.88466d31)
	- modify cal_preprocess_spirou to sort out outputs and to skip index file (rev.d8813d94)
	- Issue #429 - Re-work "listfiles" to get files from the headers (and index files) + deal with outputs (rev.23e86409)
	- Issue #429 - ReWork "WriteImage" to save to p['OUTPUTS'] and deal with spirouStartup.End dealing with outputs (rev.0d5eff99)



================================================================================
* Fri Sep 07 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.002

================================================================================
	- Added an all_order plot of fitted gaussians (as discussed in #442) (rev.fe689cf0)
	- fit_emi_line: added check to not fit on lines with more than one zero-value (fix for #393) (rev.d706131c)


================================================================================
* Mon Sep 10 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.003

================================================================================
	- update notes - update (rev.70b7a9e0)
	- unit test .run files - update after removing H2RG dependency (rev.069c1aaf)
	- spirouUnitTests.py: remove H2RG dependency (comparison not needed) (rev.95e9801f)
	- unit_test.py: replace dict() --> OrderedDict() + remove H2RG dependency (rev.ffda5073)
	- spirouUnitTests.py: replace dict() --> OrderedDict() + remove H2RG dependency (rev.3065faf1)
	- spirouUnitRecipes.py: remove H2RG dependency (no comparison needed) + replace dict() --> OrderedDict() (rev.b705aa15)
	- spirouUnitTests.__init__.py: remove H2RG dependency (remove check_type and set_comp) (rev.36998d02)
	- drs_tools: replace dict() --> OrderedDict() (rev.4963227e)
	- drs_documentation: replace dict() --> OrderedDict() (rev.c8fb784b)
	- drs_dependencies: replace dict() --> OrderedDict() (rev.b64a7d7f)
	- drs_changelog: replace dict() --> OrderedDict() (rev.641919b0)
	- calc_berv: replace dict() --> OrderedDict() and remove H2RG dependency (rev.63856e66)
	- spirouWAVE: replace dict() --> OrderedDict() (rev.e5d5d4b5)
	- spirouTHORCA.py: remove H2RG dependency (rev.a379b36f)
	- spirouTelluric.py: remove unused line (norm) (rev.8d40ccfa)
	- spirouStartup.py: remove H2RG dependency and add "UNIX" file column (rev.e24955c0)
	- spirouRV.py: remove H2RG dependency (rev.0f6d35dd)
	- spirouPOLAR.py: replace dict() --> OrderedDict() (rev.1800cd1d)
	- spirouLOCOR.py: remove H2RG dependency (rev.b555b029)
	- spirouImage.py: remove H2RG dependency (rev.8e36d194)
	- spirouFITS.py: remove H2RG dependency + replace dict() --> OrderedDict() (rev.b0e08d49)
	- spirouBERV.py: remove H2RG dependency (rev.e7501ba1)
	- spirouEXTOR: replace dict() --> OrderedDict() (rev.f1e00449)
	- spirouDB: replace dict() --> OrderedDict() (rev.8e78baa9)
	- spirouPlot.py: remove H2RG dependency (rev.729cd045)
	- spirouConst.py: update reduced output columns (remove obs date and utc from reduced products) (rev.0e9dfd4b)
	- spirouConfig.py: replace dict() --> OrderedDict() (rev.d962af8f)
	- main_drs_trigger: remove H2RG dependency (rev.6bbd39d2)
	- constants_SPIROU_H2RG: remove H2RG dependency (Delete file) (rev.0b42567d)
	- off_listing_REDUC_spirou - add column for last modified (unix time) (rev.a3c968f9)
	- cal_wave_mapper: replace dict() --> OrderedDict() (rev.5878a511)
	- cal_SLIT_spirou: remove H2RG dependency (rev.73c77f0f)
	- cal_preprocess_spirou: remove H2RG dependency (rev.97771e10)
	- cal_loc_RAW_spirou: remove H2RG dependency (rev.8adcf001)
	- cal_FF_RAW_spirou: remove H2RG dependency (rev.7c4fe45d)
	- cal_extract_RAW_spirou: remove H2RG dependency (rev.4e79daf1)
	- cal_exposure_meter: replace dict() --> OrderedDict() (rev.134560d1)
	- cal_DARK_spirou.py: remove H2RG dependency (rev.0576328c)
	- cal_CCF_E2DS_spirou.py: replace dict() --> OrderedDict() (rev.531707eb)
	- spirouWAVE - re-add dict() --> OrderedDict() (rev.98c31995)
	- config - merge fix - do NOT upload own config! (rev.64cdc181)
	- cal_WAVE_E2DS_EA - extra imports (rev.fa0dc831)
	- cal_exposure_meter.py: fix bad call to get_telluric (p, loc --> loc) (rev.60784433)
	- updated changelog/date/version/update notes (rev.14394d2d)
	- update unit tests (rev.473572e7)
	- spirouUnitTests: fix outputs of manage_run (post H2RG removal) (rev.338020dd)
	- spirouTelluric.py: fix kind when reading TAPAS file (was FLAT now TAPAS) (rev.8a4fa81a)
	- spirouStartup.py: fix indexing of files (add "LAST_MODIFIED" column) (rev.720b6071)
	- spirouStartup.__init__.py: fix aliases (rev.b6a4685f)
	- spirouTable - increase width of table (now 9999) (rev.63094fe8)
	- spirouExoposeMeter.py: update where TAPAS file is taken from (now from telluDB) (rev.301921a6)
	- spirouConst.py: update reduced output columns (need date and utc for drift) (rev.a9caa917)
	- update master_calib_SPIROU.txt for reset - now we don't need H2RG or TAPAS input (rev.a10af728)
	- off_listing_RAW/REDUC_spirou - fix bug in adding unix time - now called "last_modified" (to be more specific) (rev.a62d29fe)
	- cal_FF_RAW_spirou: fix bug in H2RG removal (rev.562e3668)
	- cal_DARK_spirou.py: remove H2RG dependency (rev.0576328c)



================================================================================
* Tue Sep 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.004

================================================================================
	- recipe_control.txt --> add cases (for fiber) for visu_E2DS_spirou (rev.f6da5cd7)
	- spirouFile.py - fix bad error output {0} --> {1} (rev.d6d27e7d)
	- cal_test.run: fix errors (typos ...f --> ...a) (rev.86b0b5f3)
	- update recipe control for visu_RAW and visu_E2DS recipes (rev.45121f60)
	- update notes with not done/finished (rev.0c33cb19)



================================================================================
* Tue Sep 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.005

================================================================================
	- pep8 updates (rev.01bce8f9)
	- update_notes.txt: update with new unit tests (rev.f6db5001)
	- unit tests: update unit test --> add "Tellu_Test.run" and modify "Cal_Test.run", remove test_tellu.run (rev.e462e025)
	- recipe_control.txt --> add telluric and polarisation cases for visu_E2DS_spirou (rev.bfc3c646)
	- obj_fit_tellu, obj_mk_tell_template, obj_mk_tellu: fix writing outputs to file (rev.520b8c88)



================================================================================
* Wed Sep 12 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.006

================================================================================
	- off_listing.py: fix bug and add to index (if prompted by user) (rev.ab90fab1)
	- spirouStartup.py: added Y/N question function (rev.d020f80f)
	- off_listing.py: fix to bug in code (rawloc --> list) (rev.3118329d)
	- off_listing.py: generic off listing that takes any directory as only input (no night name) and read's index.fits / _pp fits file headers to get off listing for that directory (rev.9a1b57cb)
	- spirouStartup.py: fix for not requiring night name in load_arguments (rev.24148aa4)
	- spirouConst.py: Added general off listing columns (rev.618a444b)
	- made spirouTools executable (rev.dd5fa2ee)
	- fix bad pep8 updates (rev.647fde11)
	- pep8 updates (rev.5e28150a)



================================================================================
* Thu Sep 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.007

================================================================================
	- drs_changelog.py: undo pep8 name change (and redo properly) (rev.0a9b6b48)
	- update_notes.txt: add unit tests to update (files and some explanation) (rev.11fb9f05)
	- pol_spirou.py: fix error with new input/output to WriteImageMulti (rev.8ca56903)
	- spirouWAVE.py: hide testing "print" statements (rev.c07d7fb7)
	- unit_tests: update unit test + add polarisation test (rev.a821b2d8)
	- spirouCDB.py: fix bad call to DATE_FMT_HEADER (p not required) (rev.522ff10c)
	- cal_reset.py: exit script has_plots=False (rev.b55de667)
	- spirouWAVE.py: fix issue with pep8 update (ll_prev defined in wrong place) (rev.7f39d0aa)
	- spirouWAVE.py (Issue #452): wave_catalog is now initialised as a NaN array (instead of an array of zeros) (rev.074f79fa)



================================================================================
* Thu Sep 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.008

================================================================================
	- version.txt: update/check dependencies (rev.fdf8134c)
	- drs_dependencies.py: fix for python 2 path (rev.a2177be9)
	- update date/version/changelog (rev.67113c33)



================================================================================
* Mon Sep 17 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.009

================================================================================
	- test runs: update tellu_test.run (rev.aa95ba91)
	- update cal_test.run (rev.73f72ebf)
	- spirouStartup.py: extra check for no outputs in indexing (fixes crash) (rev.2a54412f)
	- spirouPlot: fix telluric plots (labels, titles, limits) (rev.8a0abf11)
	- obj_mk_tellu: save SP to loc (rev.2befaea4)
	- obj_fit_tellu: fix bug (blaze must be normalised to fit telluric) (rev.a2402037)



================================================================================
* Tue Sep 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.010

================================================================================
	- tellu_test.run: add actual non-hot stars to telluric test (rev.963dfb27)
	- tellu_test.run: add actual non-hot stars to telluric test (rev.74926c51)
	- tellu_test.run: reset for full test (rev.73a66736)



================================================================================
* Wed Sep 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.011

================================================================================
	- recipe_control.txt - add e2dsff files to cal_drift codes and cal_ccf (rev.b99e7904)
	- cal_DRIFTPEAK_E2DS_spirou: fix obtaining of lamp type with hc_hc (ext_type == "HCONE_HCONE" or "HCTWO_HCTWO") (rev.0d991a01)
	- cal_extract_RAW_spirou.py: better error message for no DPRTYPE in header (Issue #456) (rev.371922c5)



================================================================================
* Wed Sep 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.012

================================================================================
	- unit_tests: add cal_CCF test to Tellu_Test.run (rev.5467d047)
	- unit_tests: update unit test with new hc files (from 2018-08-05) (rev.c8d2c4ca)
	- recipe_control.txt - remove duplicate line in cal_CCF definition (rev.67ef51d1)
	- cal_CCF_E2DS_spirou.py - update comments and remove extra spaces (rev.172015c1)



================================================================================
* Wed Sep 19 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.3.013

================================================================================
	- New CCF mask provided by Xavier on 2018 Sept 19 (rev.fd8dd6be)
	- Add E2DS_FF for cal_CCF_E2DS recipe (rev.24649509)
	- Adaptation for telluric corrected spectra (rev.bfa08b02)



================================================================================
* Wed Sep 19 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.3.014

================================================================================
	- New CCF mask provided by Xavier on 2018 Sept 19 (rev.fd8dd6be)



================================================================================
* Wed Sep 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.015

================================================================================
	- unit_tests: fix bug in run names (rev.19fe91f3)




================================================================================
* Fri Sep 21 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.016

================================================================================
	- remove user specific ignore (should not be needed) (rev.28d08b71)
	- update .gitignore to ignore misc folder (rev.7cce836c)
	- spirouWAVE.py - Merge changes from Dev into Melissa (rev.736690cb)
	- spirouTHORCA.py - Merge changes from Dev into Melissa (rev.25763190)
	- spirouRV.py - Merge changes from Dev into Melissa (rev.300036d3)
	- spirouPlot.py - Merge changes from Dev into Melissa (Issue #460) (rev.564931d5)
	- constants_SPIROU_H4RG.py - Merge changes from Dev into Melissa (rev.72bfa14c)
	- cal_WAVE_E2DS_EA_spirou.py - Merge changes from Melissa (rev.cdd8fee3)
	- cal_CCF_E2DS_spirou.py - full header added to "CCF_FITS_FILE" (rev.dbcefdc4)



================================================================================
* Fri Sep 21 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.017

================================================================================
	- spirouTHORCA.py - fix code to not have min/max of HC/FP_N_ORD START/FINAL for cal WAVE/cal HC (rev.bd7f4a60)
	- cal_WAVE_E2DS_spirou.py - fix code to not have min/max of HC/FP_N_ORD START/FINAL for cal WAVE (rev.f1cc29c6)
	- cal_WAVE_E2DS_EA_spirou.py - fix code to not have min/max of HC/FP_N_ORD START/FINAL for cal WAVE (rev.4cdb280a)



================================================================================
* Fri Sep 21 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.018

================================================================================
	- update timings (rev.967e9282)



================================================================================
* Mon Sep 24 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.019

================================================================================
	- cal_DRIFTPEAK_E2DS_spirou.py - fix typo bug with drift_peak_allowed_types (rev.a44642df)
	- recipe_control.txt - add HCTWO_HCTWO and OBJ_FP to cal_DRIFT and cal_DRIFTPEAK recipes - Issue #464 (rev.2d68c46f)
	- constnats_SPIROU_H4RG.py - added new constant to control with files (with header key KW_EXT_TYPE) are associated with fp and hc (for setting other constants) - Issue #464 (rev.b9989ffa)
	- cal_extract_RAW_spirou.py - note from Etienne to Francois re: negative fluxes to zero after background correction (rev.57262b57)
	- cal_DRIFTPEAK_E2DS_spirou.py - modified the lamp parameter to get from constants (for easier addition of different types) - Issue #464 (rev.b0d74f77)



================================================================================
* Tue Sep 25 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.020

================================================================================
	- spirouPlot.py - pass font changes for all graphs (via matplotlib.rc) (rev.22a450c1)
	- spirouConst - add descriptions for plot font functions (rev.e3384687)
	- spirouConst.py - add plot pseudo constants (to enable changing plot fontsize easily - for all plots) (rev.6069dad8)
	- cal_CCF_E2DS_spirou.py - add inputs for ccf_rv_ccf_plot (modified inputs for plot title) (rev.fbac65ca)



================================================================================
* Wed Sep 26 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.021

================================================================================
	- spirouWAVE.py - adapt to allow force creating of linelist (rev.bef63e35)
	- spirouPlot.py - adapt to be able to use different style (rev.6f0eb3bf)
	- spirouConst.py - add plot style (for alternate plotting) (rev.66c1548b)
	- constants_SPIROU_H4RG.py - add control to force linelist re-computation (rev.76fe208f)



================================================================================
* Mon Oct 01 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.022

================================================================================
	- spirouTHORCA.__init__.py - remove use of GetE2DSll - use GetWaveSolution (Issue #468) (rev.1e00cb3c)
	- spirouTHORCA.py - remove use of GetE2DSll - use GetWaveSolution (Issue #468) (rev.60661273)
	- cal_CCF_E2DS_spirou.py - remove use of GetE2DSll - use GetWaveSolution (Issue #468) (rev.cdcd738e)
	- spirouTHORCA.py - re-work the obtaining of wave solution (Issue #468) (rev.c5baf9e8)
	- spirouFITS.py - re work wave solution functions (Issue #468) (rev.dc01166b)
	- spirouImage.__init__.py - remove old wave sol functions (Issue #468) (rev.f4530754)
	- cal_DRIFT_RAW_spirou.py - work on wave solution functions (Issue #468) (rev.81684e90)
	- pol_spirou.py - work on wave solution functions (Issue #468) (rev.aa5dca75)
	- cal_extract_RAW_spirou.py - work on wave solution functions (Issue #468) (rev.5a580a64)
	- visu_[ALL]_spirou.py - work on wave solution functions (Issue #468) (rev.33f64e6c)
	- obj_[fit/mk]_tellu.py - work on wave solution functions (Issue #468) (rev.d0ddf2a4)
	- cal_wave_mapper.py - work on wave solution functions (Issue #468) (rev.276db432)
	- cal_HC_E2DS_EA_spirou.py - work on wave solution functions (Issue #468) (rev.82315102)
	- cal_WAVE_[ALL].py - work on wave solution functions (Issue #468) (rev.f2749f2b)
	- cal_exposure_meter.py - work on wave solution functions (Issue #468) (rev.f7601dbd)
	- cal_DRIFTPEAK_E2DS_spirou.py - work on wave solution functions (Issue #468) (rev.69fe6ce8)
	- cal_DRIFT_E2DS_spirou.py - work on wave solution functions (Issue #468) (rev.2cd1669e)
	- spirouImage.py - modify get_all_similar_files to add check of fiber for OBJ_FP OBJ_HCONE etc (i.e. only allow on fiber C) and return filetype to show user which DRS_EXTOUT were allowed (Issue #464) (rev.3e9b8f23)
	- spirouImage.__init__.py - update alias to better represent what we are doing get_all_similar_files --> GetSimilarDriftFiles (rev.df446d47)
	- constants_SPIROU_H4RG.py - add constant to check which fiber is being used (for OBJ_FP and OBJ_HCONE etc should only work on fiber C)  - Issue #464 (rev.5201100d)
	- cal_DRIFTPEAK_E2DS_spirou.py - fix code to allow FP_FP and OBB_FP (and report back on allowed types) - Issue #464 (rev.88077a89)
	- cal_DRIFT_E2DS_spirou.py - fix code to allow FP_FP and OBB_FP (and report back on allowed types) - Issue #464 (rev.d88566aa)
	- teset.run - update tested files (rev.10683a9d)
	- re-add misc folder to github sync (rev.eba69830)
	- spirouImage.py - change how get_all_similar_files works (now look for kw_OUTPUT based on "DRIFT_PEAK_ALLOWED_OUTPUT" - Issue #464 (rev.db2d5e29)
	- constnats_SPIROU_H4RG.py - Issue #464 - add definitions for which outputs are allowed for "fp" and "hc" (rev.567a714b)
	- add misc backup files (rev.3b94ce65)
	- removed problematic fitgaus.py from fortran (conflicts with fitgaus.f) and removed fitgaus.f from spirouTHORCA (rev.43603b7c)
	- spirouImage.py - Issue #464 - get_all_similar_files - modify to run indexing if no index.fits exists (rev.7d50d9e6)
	- off_listing_REDUC_spirou.py - Issue #464 - allow off_listing to run in quiet mode (rev.c06558ef)
	- spirouWAVE - replace get_e2ds_ll (Issue #468) (rev.7e768052)
	- spirouFITS.py - allow header return (rev.d8471e5a)
	- spirouPlot.py - fix bug plot_style cannot be None - now '' when empty (rev.5e3a0420)
	- cal_CCF_E2DS_spirou.py - fix bug - swap wave and param (rev.799c3ac9)



================================================================================
* Tue Oct 02 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.023

================================================================================
	- cal_CCF_E2DS_spirou.py - fix order out GetWaveSolution outputs (Issue #464) (rev.6b81a010)
	- Cal_Test.run - change over (cal_exposure_meter last) (rev.61d08521)
	- spirouTelluric.py - modify functions to allow filename saved to p - for insertion into header at hdict creation (Issue  #471) (rev.23976dcf)
	- spirouLOCOR.py - modify functions to allow filename save to p - for insertion into header at hdict creation (Issue  #471) (rev.45757bc0)
	- spirouImage.py - modify functions to allow filename to be saved to p - to insert into header at hdict creation (Issue  #471) - fix bug with mask2 (in getting drift files function) (rev.80f7f3f3)
	- spirouFITS.py - mmodify read functions to save the filename to p - to inject into header at hdict creation (Issue  #471) (rev.7fa9cca5)
	- spirouFLAT - add filenames to headers (Issue  #471) (rev.c1553335)
	- spirouKeywords.py - add the keywords for each file (that will go in the header) - Issue  #471 (rev.7e1e60d3)
	- obj_mk_tellu.py - add filenames to headers (Issue  #471) (rev.fa5ab5d4)
	- obj_mk_tellu_template.py - add filenames to headers (Issue  #471) (rev.b4edf263)
	- obj_fit_tellu.py - add filenames to headers (Issue  #471) (rev.54e8205d)
	- cal_wavE_mapper.py - add filenames to headers (Issue  #471) (rev.052e4847)
	- cal_[WAVE_E2DS]_spirou.py - add filenames to headers (Issue  #471) (rev.d2bde2ee)
	- cal_SLIT_spirou.py - add filenames to headers (Issue  #471) (rev.240d5927)
	- cal_loc_RAW_spirou.py - add filenames to headers (Issue  #471) (rev.f7e450cc)
	- cal_HC_E2DS_spirou.py - add filenames to headers (Issue  #471) (rev.bde11970)
	- cal_HC_E2DS_EA_spirou.py - add filenames to headers (Issue  #471) (rev.143361dc)
	- cal_FF_RAW_spirou.py - add filenames to headers (Issue  #471) (rev.81966571)
	- cal_extract_RAW_spirou.py - add filenames to headers (Issue  #471) (rev.c07a5efd)
	- cal_exposure_meter.py - add filenames to headers (Issue  #471) (rev.b0688686)
	- cal_DRIFTPEAK_E2DS_spirou.py - add filenames to headers (Issue  #471) (rev.3b2a192f)
	- cal_DRIFT_E2D.py - add filenames to headers (Issue  #471) (rev.f4bb881f)
	- cal_DARK_spirou.py - add filenames to headers (Issue  #471) (rev.8ec40729)
	- cal_BADPIX_spirou.py - add filenames to headers (Issue  #471) (rev.86b4d30f)
	- Update spirouImage.py (rev.276c1027)



================================================================================
* Wed Oct 03 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.024

================================================================================
	- cal_SHAPE_spirou.py - fix typo dx[iw] = coeffs[1] --> dx[iw] = gcoeffs[1] (rev.6496ddfc)
	- new_bananarama.py - added TODO questions for Etienne (rev.9216b16c)
	- cal_SHAPE_spirou.py - more changes to update with Etiennes new_bananarama code (rev.a1dafd01)
	- Cal_Test.run - must test HC/WAVE EA recipes - added to runs (rev.0290405c)
	- cal_HC_E2DS_EA_spirou.py - fix bug flatfile in header should be blazefile (rev.7d56f2e9)
	- cal_SHAPE_spirou.py - updated code [unfinished/not working] (rev.428ae653)
	- copy of etiennes shap finding code (rev.965fec59)
	- update timings and update notes (rev.aac4dafe)
	- test code for one target (rev.50ef5e11)
	- update version/date/changelog/update notes (rev.48457465)
	- unit tests - remove some extractions (not needed for minimum test) (rev.4adfd897)
	- unit tests - add full telluric test for TC3 (rev.57d396c9)
	- spirouImage.py - WAVE_FILE is now WAVEFILE (rev.9333c919)
	- dark_test.py - test of the values supplied in the dark header file (for specific files + night_name) (rev.58b1c501)
	- visu_E2DS_spirou.py - readblazefile now need p returned (rev.388497df)
	- obj_fit_tellu.py - re-add loc['WAVE'] (used for plotting) + loc['WAVE_IT'] need filename returned (rev.f222a470)
	- cal_wave_mapper.py - remove flat file (not used or obtained) from header (rev.0d020f26)



================================================================================
* Thu Oct 04 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.025

================================================================================
	- spirouFITS.py - get shape file from header (rev.318dba86)
	- cal_extract_RAW_spirou.py - add shape file to header (if mode 4a/4b) (rev.27a2b4f6)
	- cal_SHAPE_spirou.py - fix type - should be SHAPE file not TILT file (rev.5bd99336)
	- spirouImage.__init__.py - add alias to get_shape_map (GetShapeMap) (rev.77ab0fc2)
	- spirouImage.py - move get_shape_map to spirouImage functions (And add imports as required) (rev.d188c3ff)
	- spirouPlot.py - add slit shape plot (rev.a06c9f08)
	- spirouKeywords.py - add kw_SHAPEFILE to output keys (rev.a80fc71c)
	- spirouConst.py - add SLIT_SHAPE_FILE filename definition (rev.63a75301)
	- output_keys.py - add slit_shape_file output key (rev.6ca1d0ee)
	- new_bananarama.py - fix to work with DRS (rev.b9fa0fc4)
	- cal_SLIT_spirou.py - replace old path function with new and correct small typo (rev.01adc940)
	- cal_SHAPE_spirou.py - add plotting, filesaving, calibDB movement and move functions to spirouImage (finally runs) (rev.c1ac85cd)
	- cal_SHAPE_spirou.py - added plotting, file saving and adding to calibDB (rev.826e9632)
	- cal_SHAPE_spirou.py - fix bugs that now produce identical results to new_bananarama code (rev.9f027cb8)



================================================================================
* Fri Oct 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.026

================================================================================
	- Cal_Test.run - add cal_SHAPE_spirou.py to unit test (rev.a95ca65c)
	- spirouUnitsRecipes.py - add cal_HC_E2DS_EA_spirou, cal_SHAPE_spirou, cal_WAVE_E2DS_EA_spirou to unit tests (rev.b1f5e578)
	- recipe_control.txt - add cal_SHAPE_spirou (copy of cal_SLIT_spirou) (rev.ee743993)
	- cal_SHAPE_spirou.py - change __NAME__ (after recipe control integration) (rev.31ee09e2)
	- spirouImage.py - optimisation - moved a few things out of loop to speed up process (rev.ff25e9cb)
	- spirouPlot.py - corrected type in constant name (slit_shape_angle_plot) (rev.361df98b)
	- constants_SPIROU_H4RG.py - move cal_SHAPE_spirou.py constants to constants file (rev.6bc37dc3)
	- cal_SHAPE_spirou.py - move constants to constants file (rev.9634f6ca)



================================================================================
* Fri Oct 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.027

================================================================================
	- Timings.txt - update timings with new runs (rev.b92914b8)
	- Cal_Test.run - comment out cal_WAVE_E2DS_EA_spirou - not working with extraction 4b? (rev.16d4abab)
	- spirouTHORCA.__init__.py - add alias to generate_res_files (GenerateResFiles) (rev.f5c278d2)
	- spirouWAVE.py - add generate_res_files functions to generate arrays/header dictionary in correct format for wave resolution line profile map file (rev.c964a9c5)
	- spirouConst.py - add WAVE_RES_FILE_EA to file definitions (rev.139af4bf)
	- cal_WAVE_E2DS_EA_spirou.py - add saving of wavelength resolution line profiles to file (rev.78b46b27)
	- output_keys.py - added "WAVE_RES" to output keys (for wave solution res map) (rev.edecd892)
	- cal_HC_E2DS_EA_spirou.py - added saving of resolution map and line profiles to file (rev.7e123626)
	- spirouUnitTest.py - up date title of log timings (rev.6f8c7de4)
	- recipe_control.txt - hide dark_fp dark_flat for now (test later) (rev.145350fb)
	- spirouFITS.py - allow fiber-forcing in getting wave solution (otherwise when calibDB is used, uses p['FIBER']) (rev.bdfcb817)
	- off_listing_RAW_spirou.py - correct mistake with off_listing (rawloc should be a list) (rev.02b06153)
	- spirouFITS.py - make sure the source of the wavelength solution is reported (Issue #468) (rev.c666052c)



================================================================================
* Fri Oct 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.028

================================================================================
	- update_note.txt - update with note about setting extraction to 4b (default = 3d) (rev.78deee57)
	- constants_SPIROU_H4RG.py - set extraction_type back to 3d for now - until 4a/4b tested (rev.260561ff)



================================================================================
* Sat Oct 06 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.029

================================================================================
	- cal_FF_RAW_spirou.py - update extraction to deal with different outputs (rev.4f03c1cd)
	- spirouFile.py - made sure pre-procesing always adds DPRTYPE even if file not recognised (#Issue 475) (rev.d78b2b88)
	- spirouEXTOR.py - for modes 3c, 3d, 4a, 4b add the e2dsll extraction type (rev.124af309)
	- spirouConst.py - add file definition for e2dsll (rev.a2ed2bb5)
	- recipe_control.txt - added and corrected dark_fp, dark_flat and obj_obj (rev.d2495ab1)
	- output_keys.py - added output type extract_e2dsll_file (rev.36941c49)
	- cal_extract_RAW_spirou.py - added "un-sum" extraction output (E2DSLL) to see what the extraction is doing (rev.34efe8bc)



================================================================================
* Tue Oct 09 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.030
================================================================================

	- spirouUnitRecipes.py - remove the moved HC/WAVE recipes from import (no longer in bin folder) (rev.09b55f4c)
	- spirouTelluric - add function wave2wave to shift an image from one wavelength grid to another (Issue #478) (rev.fd27bb52)
	- spirouFITS.py - allow wave solution to be obtained quietly (rev.03cb3e5a)
	- spirouTDB - add get_database_master_wave to get the master wavelength grid from TelluDB (Issue #478) (rev.79bb509a)
	- recipe_control.txt - Allow sky objects for cal_DARK_spirou (Issue #479) (rev.15b48645)
	- master_tellu_SPIROU.py + file - modify master telluric database to have a MASTER_WAVE key - containing the master wavelength grid [unfinished] - Issue #478 (rev.f3b34703)
	- wave2wave.py - backup of Etiennes function to shift images from one wavelength grid to another - Issue #478 (rev.cfbd0b62)
	- HC/WAVE recipes - move all (older) recipes to misc folder - can still be used when in this directory - cannot currently be used with unit tests (rev.6f58ca4b)
	- obj_mk_tellu.py - add code to shift transmission map [unfinished] - Issue #478 (rev.3079588a)
	- obj_fit_tellu.py - add code to shift pca components and template components [unfinished] - Issue #478 (rev.10493a7c)
	- cal_extract_RAW_spirou.py - fix bug with extraction method 4a and 4b - data2 shallow copied - shouldn't be! (Issue #477) (rev.07d50437)



================================================================================
* Wed Oct 10 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.031

================================================================================
	- Tellu_Test2.run - add additional test to test different wavelength solutions in telluric recipes (rev.dbd7cd87)
	- spirouUnitTests/Runs - fix the units test with new recipes/names (rev.9c94c967)
	- spirouUnitRecipes.py - fix for the change of name of obj_mk_tell_template --> obj_mk_obj_template (rev.57c17924)
	- spirouWAVE.py - Etienne's fix for cal_HC stability in "fit_gaussian_triplets" (rev.6498dbd1)
	- spirouFITS.py - add a quiet mode (to not duplicate log) and fix bug in getting wavemap from header (from wave params) (rev.db23f3c4)
	- spirouConst.py - add filenames for obj_mk_obj_template (rev.38decfac)
	- master_calibDB_SPIROU.txt - no longer need AB wave solutions and shape - only AB and C needed / shape generated online (rev.5d1186a0)
	- output_keys.py - add obj_mk_obj_template filenames to output keys + recipe_control (rev.37d0a0d0)
	- constnats_SPIROU_H4RG.py - turn off force calibDB for wave solution + add HC parameters (Etienne's fix) (rev.93ff0d0e)
	- obj_mk_obj_template - renamed from obj_mk_tell_template.py + fixed for wavelength grid shift - Issue #478 (rev.09f3088a)
	- obj_mk_tell_template.py - update with shifted wavelength grid - Issue #478 (rev.a254b44a)
	- cal_HC_E2DS_EA_spirou.py - correct bug that wavelength solution parameters were not saved to header correctly (rev.a1971b91)
	- recipe_control.txt - add DARK_FP to drift and driftpeak allowed inputs - Issue #475 (rev.3654147e)
	- constants_SPIROU_H4RG.py - add dark_fp to the drift peak allowed constants (to all in use for drift/driftpeak) - Issue #475 (rev.069c6043)
	- recipe_control.txt - add OBJ_DARK to allowed files used in cal_DARK_spirou.py (Issue #479) (rev.8e6e35e1)
	- cal_DARK_spirou.py - all use of skydarks and push SKYDARK to calibDB if used (Issue #479) (rev.ee20f4ef)
	- constants_SPIROU_H4RG.py - add key "use_skydark_correction" to allow SKYDARKs to be use (and take presence over DARK in calibDB) (rev.66ac412f)
	- spirouTelluric.py - shift templates if they are not created at runtime from mastergrid to current wavelength grid - Issue #478 (rev.7c9d3b6e)
	- spirouTelluric.py - fix bug with convolve_files (should not be re-copied into telluDB) (rev.6a0c2b8f)
	- spirouImage.py - allow SKYDARK to be used (if present in calibDB) if USE_SKYDARK_CORRECTION = True - Issue #479 (rev.5159b7e9)
	- obj_mk_tellu.py - fix headers in saved file (now wavelength is shifted) - Issue #478 (rev.73baeb8b)
	- obj_fit_tellu.py - fix bug with shifting PCA components (Issue #478) (rev.f44df6a2)
	- pol_spirou.py + all recipes use GetWaveSolution - force fiber A and B to use wave solution AB (Issue #480) (rev.2813e08f)
	- all recipes using GetWaveSolution - force fiber A and B to use AB wave solution (rev.7c07ae63)



================================================================================
* Thu Oct 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.032

================================================================================
	- unit_tests - update tellu_test2 and test (rev.3a7ac5ca)
	- spirouFITS.py - fix output of wavelength solution - Issue #483 (rev.844f70d5)
	- spirouConst.py - after reading default config file must look for a user config file (parameters depend on it) (rev.4a1cc2a5)
	- spirouConfigFile.py - moved get_user_config to here (to allow accessing from spirouConst.py) (rev.40db643c)
	- spirouConfig.py - move get_user_config to spirouConfigFile.py - (needed to fix not obtaining constants from user config file) (rev.ab88a21a)
	- spirouLog.py - add a possibility to debug in ipython (rev.449fa77a)
	- spirouFITS.py - fix error - now if image is not defined tries to get dimensions from header before giving error - Issue #483 (rev.82fecda8)



================================================================================
* Tue Sep 11 2018 Eder <edermartioli@gmail.com> - 0.3.033
* Thu Oct 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.033

================================================================================
	- Added BJD# and MEANBJD to header of polar products (rev.29a19764)
	- Minor changes (rev.630d0c27)
	- Added new keywords in polar products, mainly the BJD time calculated at center of observations. Also fixed small bugs (rev.b83c7206)
	- Added new keywords in polar products, mainly the BJD time calculated at center of observations. Also fixed small bugs (rev.c04144f9)
	- Added new keywords in polar products, mainly the BJD time calculated at center of observations. Also fixed small bugs (rev.c94b6171)
	- Added new keywords in polar products, mainly the BJD time calculated at center of observations. Also fixed small bugs (rev.947ed27a)
	- Updated keyworks BERV, BJD, and MJD of polar products by central values calculated in the module. Also updated keyword EXPTIME by the sum of all EXPTIME values from individual exposures (rev.09beee21)
	- Updated keyworks BERV, BJD, and MJD of polar products by central values calculated in the module. Also updated keyword EXPTIME by the sum of all EXPTIME values from individual exposures (rev.a7543efc)
	- Tuned parameters to improve LSD analaysis and added new statistical quantities calculated from LSD analysis (rev.587fc630)
	- Changed parameters for LSD analysis (rev.15791803)
	- Implemented selection of CCFFILE in LSD analysis matching closest temperature to source observed (rev.b59d10d7)
	- spirouLSD.py - add a few outstanding TODO comments and fix error print (filename may not be defined) (rev.d257822c)
	- spirouPOLAR.__init__.py - chagen polarHeader --> PolarHeader (for convention) (rev.4efa4d03)
	- pol_spirou.py - Update to alias for convention polarHeader --> PolarHeader (rev.486d7811)
	- spirouLog.py - add a possibility to debug in ipython (rev.449fa77a)
	- Minor changes (rev.630d0c27)

================================================================================
* Thu Oct 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.034

================================================================================
	- unit_test.py - make sure all plots are closed. (rev.e928eed7)
	- spirouEXTOR.__init__.py - add alias for compare_extraction_modes (CompareExtMethod) - Issue #481 (rev.b0516e44)
	- spirouEXTOR.py - add compare_extraction_mode function to test difference between flat and e2ds extraction modes (#481) (rev.06440731)
	- cal_FF_RAW_spirou.py - save extraction method to header (like cal_extract) (rev.cacf1925)
	- cal_extract_RAW_spirou.py - get flat header, compare flat extraction to extraction type  (Issue #481) (rev.beeed62d)
	- spirouFITS.py - return header for flat file so we can get extraction type for the flat (Issue #481) (rev.1b8a26e6)
	- unit_tests - do not currently test cal_WAVE_E2DS_EA_spirou.py - comment out (rev.67f480c4)
	- pol_spirou.py - Update to alias for convention polarHeader --> PolarHeader (rev.486d7811)


================================================================================
* Fri Oct 12 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.035

================================================================================
	- update unit test runs (rev.99517394)
	- spirouTelluric.py - modify get_molecular_tell_lines to use master wavelength solution, rename functions to better describe functionality, use relativistic dv correction function (rev.ba180af0)
	- spirouTDB.py - rename functions to better describe functionality (rev.4b484e12)
	- spirouDB.__init__.py - rename aliases to better describe functions (rev.6ebe0beb)
	- spirouPlot.py - add tellu_fit_debug_shift_plot - Issue #478 (rev.c6c46929)
	- spirouMath.py - add relativistic_waveshift function (rev.4a2da36e)
	- constants_SPIROU_H4RG.py - turn off the fit derviative part for principle components - Issue #478 (rev.e3a4f288)
	- obj_mk_obj_template.py - further fixes for wavelength shift addition - Issue #478 (rev.2c8b7c5a)
	- obj_fit_tellu.py - further fixes for wavelength shift addition - Issue #478 (rev.5a980e06)
	- obj_fit_tellu.py - fix bugs in shifting wavelength (Issue #478) (rev.a878ca1b)
	- cal_extract/FF_RAW_spirou.py - catch warnings from extraction process (rev.c788e478)
	- cal_WAVE_E2DS_EA_spirou.py - currently only supports one FP_FP and one HC_HC (due to file updating) - added check to error if more used (rev.51325fa2)
	- cal_HC_E2DS_EA_spirou.py - currently only supports one FP_FP and one HC_HC (due to file updating) - added check to error if more used (rev.b9e5ab48)
	- spirouTelluric.py - change bad mask from 0.999 to 0.5 to avoid NaN fringing - Issue #478 (rev.8e68cffd)
	- spirouTelluric.py - catch known warnings and disregard (rev.db5fd2ef)




================================================================================
* Sun Oct 14 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.036

================================================================================
	- spirouEXTOR.py  - fix bug where whole order is zeros - will break spline (rev.10eef6ad)



================================================================================
* Mon Oct 15 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.037

================================================================================
	- spirouKeywords.py - add the two new header keys for bigcube list (rev.bdb62f34)
	- obj_mk_obj_template.py - add file names and bervs for input files to big cube header (rev.09b38e2b)
	- update_note.txt - update with telluric changes (rev.cae3ae30)
	- spirouConst.py - add prefix and change filename (rev.f64f46d2)
	- obj_fit_tellu.py - save and remove abso save files - massive speed up (rev.6de88749)
	- spirouTelluric.py - catch more NaN warnings from order_tapas (rev.a7e267e0)
	- spirouFile.py - add get_most_recent function to get most recent unix time of list of files (rev.9e46d6ee)
	- spirouConst.py - add TELLU_ABSO_SAVE file (for saving loaded trans files) (rev.d00d9807)
	- obj_fit_tellu.py - store abso unless there are new trans_files (rev.22fffa6b)
	- spirouTelluric.py - swap sign on dv (rev.cbfcba8c)
	- spirouFITS.py - fix for new output of read_tilt_file (rev.0b53da0e)
	- spirouFITS.py - add reading a key 1D list from header (rev.6d55b94c)
	- constants_SPIROU_H4RG.py - add constants for quality control in obj_mk_tellu (rev.5cbb32a3)
	- obj_mk_tellu.py - quality control SNR in order QC_TELLU_SNR_ORDER greater than QC_TELLU_SNR_MIN (rev.30dd9792)
	- obj_mk_obj_tellu.py - only use unique filenames for tellu files (rev.9a62fd0e)
	- obj_fit_tellu.py - only use unique filenames from trans files (rev.8a2c6c4d)



================================================================================
* Tue Oct 16 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.038

================================================================================
	- update version/date/changelog/update notes (rev.a4704115)
	- Cal_Test.run - add cal_DRIFTCCF_E2DS_spirou to tested codes (rev.a2825de2)
	- spirouUnitRecipes.py - add cal_DRIFTCCF_E2DS_spirou to unit recipe definitions (rev.7af61eb8)
	- spirouKeywords.py - add reference rv keyword and keywordstore definition (rev.818f6870)
	- spirouConst.py - fix tags in new DRIFTCCF file name definitions (rev.c62a1e6b)
	- recipe_control.txt - add cal_DRIFTCCF_E2DS_spiour to the runable codes - for FP only (rev.44baa139)
	- output_keys.py - add DRIFTCCF_E2DS_FITS_FILE to output keys (rev.737ff685)
	- constants_SPIROU_H4RG.py - add driftccf constants to constants file (rev.e2025bf7)
	- cal_DRIFTCCF_E2DS_spirou.py - re-save driftfits to file (rev.d137862b)
	- cal_DRIFTCCF_E2DS_spirou.py - pep8 changes + load constants from file + add flux ratio + save reference RV to header (rev.9f851f30)
	- spirouEXTOR.py - undo debananafication all zeros check - does not work (rev.4ac08d74)
	- spirouFile.py - add function to sort by base name (sort_by_name) with alias SortByName (rev.5e85258e)
	- explore_headers.py - code to explore headers of all files in given dir string (with wild cards) (rev.63c85cdd)
	- obj_mk_obj_stack.py - for making stacks of images (Nobs x Nb_xpix x Nbo) (rev.6c030a84)
	- spirouKeywords.py - add new header keys to list + define them as keywordstores (rev.b05756cd)
	- obj_mk_obj_template.py - sort template files by base file name (rev.60a3d747)
	- cal_WAVE_E2DS_EA_spirou.py - add some header keys to help identify the source of output (rev.d17afad6)
	- cal_HC_E2DS_EA_spirou.py - add some more header keys to enable identifying source of output files (rev.929b23e4)



================================================================================
* Tue Oct 16 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.3.039

================================================================================
	- New recipe to compute the drift of simultaneous FP on Fiber C with fp.mas (rev.b5dde68f)
	- New function DRIFTCCF_E2DS_TBL_FILE to save driftccf file (rev.6c229f78)



================================================================================
* Wed Oct 17 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.040

================================================================================
	- extract_trigger.py - add filters to allow only certain files to be process based on DPRTYPE (rev.773e92b9)
	- clean_calibDB - custom script to remove all unwanted keys (set in the code) and remove files not in the calibDB and move all good files to new folder with a new master calibDB file (rev.7b62e834)
	- reset the calibDB and telluDB with new MASTER wave solutions (rev.d08619ae)
	- spirouStartup.py - fix bug with inputs (numpy array not allowed) (rev.490ff1bd)
	- extract_trigger.py - start work on a simple calibration trigger (upto and including extraction) (rev.eda392ea)



================================================================================
* Wed Oct 17 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.041

================================================================================
	- spirouStartup.py - fixed problem when no column is present (set to None) (rev.b0e94316)
	- fp.mas - added the fp mask to the ccf_masks folder (for cal_driftccf) (rev.8a8ea6f2)
	- extract_trigger.py - start of a trigger that goes from pp --> extraction (including all calibrations) - [NOT FINISHED] (rev.569db3fc)
	- spirouConst.py - add DPRTYPE to index file for raw outputs (rev.b33a98c0)
	- spirouFITS.py - added "check_wave_sol_consistency" function to check and remap coefficients if incorrect from constants file (IC_LL_DEGR_FIT) (rev.9f913b51)
	- cal_HC/ cal_WAVE - added check for consistent number of coefficients in wave solution - if wrong refitted onto new coefficients with correct number (rev.b90ee7c5)



================================================================================
* Thu Oct 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.042

================================================================================
	- update date/version/changelog (rev.3898587b)
	- unit_test.py - fix comment (rev.7f5d83c0)
	- TelluricsAll.run - add a list of all tellurics for maestria (rev.986a0deb)
	- constants_SPIROU_H4RG.py - add quality control parameters for mk_tellu (RMS) (rev.9dd5516d)
	- obj_mk_tellu.py - add an RMS cut to the QC parameters checked (rev.d3e5d8db)
	- obj_mk_obj_template.py - turn multi fits into fits cubes (rev.65a48759)
	- unit_test_parallel.py - test of multiprocessing on unit tests - DRS not stable to use this yet! (rev.06c253ec)
	- extract_trigger.py - for now only do up to extraction of HC_HC and FP_FP (rev.980fe3dc)
	- Gl699_small.run - just extract and fit those across one glitch (rev.c8dd99cf)
	- cal_HC/cal_WAVE only copy over original file parameters if QC passed (rev.dbbe92dd)
	- spirouFITS.py - fix bug in check_wave_sol_consistency (rev.97dce735)
	- obj_mk_tellu.py - add notes for new QC check (TODO's) (rev.f76e39c4)
	- cal_WAVE_E2DS_EA_spirou.py - remove print statement (rev.76b09b20)
	- cal_SHAPE_spirou.py - update permissions on cal_SHAPE (rev.a928d2c3)
	- update run list (for maestria runs) (rev.0dcab8ec)
	- recipe_control.txt - do not support FLAT_DARK and DARK_FLAT in cal_FF (rev.9a320102)
	- cal_DRIFTCCF_E2DS_spirou.py - comment out saving of fits file - no loc['DRIFT'] defined (rev.9d385f2a)



================================================================================
* Fri Oct 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.043

================================================================================
	- unit_test runs - add maestria tests (rev.a7f0e145)
	- update triggers/unit_tests to catch and handle errors better (rev.20f7c00a)
	- update triggers/unit_tests to catch and handle errors better (rev.2e0d5962)
	- redo tests - comments where broken (rev.197c927a)
	- spirouStartup.py - remove print statement (was there to debug) (rev.2b83c7e3)
	- spirouLog.py - return useful message on sys.exit (after error log) (rev.4ebbe16a)
	- error_test.py - test catching errors for trigger/unit_tests (rev.5b241406)
	- spirouWAVE.py - make debug plot only show in debug mode (even with plotting on) (rev.7aaa8499)
	- update HC/WAVE test (rev.a07ca29b)
	- unit_test.py - better catching/recording of errors (for batch run that doesn't crash out) (rev.d2460e0b)
	- update HC/WAVE test (rev.02c5c2f5)
	- update HC/WAVE test (rev.7b391260)
	- update HC/WAVE test (rev.021a18ae)
	- update HC/WAVE test (rev.16f9d95d)
	- update HC/WAVE test (rev.820cf3b2)



================================================================================
* Tue Oct 16 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.3.044
* Sat Oct 20 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.3.044
* Sat Oct 20 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.044
================================================================================
	- New function DRIFTCCF_E2DS_TBL_FILE to save driftccf file (rev.6c229f78)
	- cal_CCF_E2DS with simultaneous CCFDrift on FP fiber C (rev.9adc6fe6)
	- update tests (rev.b9ae6f72)



================================================================================
* Mon Oct 22 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.045

================================================================================
	- updated permissions on spirouUnitTest files (chmod +x) (rev.1befaf6e)
	- Tellu_Test.run - added a test of cal_CCF_E2DS_FP_spirou.py (currently not working) (rev.eac75e35)
	- spirouKeywords.py - added kw_DRIFT_RV definition to keywords files (for use in cal_CCF_E2DS_FP_spirou.py) (rev.85368dfc)
	- recipe_control.txt - added cal_CCF_E2DS_FP_spirou to recipe_control - for fiber AB only (will only work with fiber AB) (rev.2260a6e5)
	- cal_CCF_E2DS_FP_spirou.py - added changes to integrate into DRS (rev.e0ac5640)



================================================================================
* Mon Oct 22 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.046

================================================================================
	- obj_mk_tellu.py - make sure the NaNs do not propagate through to the convolution (NaN * 0.0 = NaN ---> need 0.0) (rev.463bb82d)
	- obj_mk_tellu.py - make sure the NaNs do not propagate through to the convolution (NaN * 0.0 = NaN ---> need 0.0) (rev.8a42ae8d)
	- obj_mk_tellu.py - catch warnings as sp now can have nans (rev.16aeefd2)
	- obj_mk_obj_template.py - change median to nan median and catch warnings with nanmedian of empty stack (all nans) (rev.d192c50d)
	- obj_mk_tellu.py - catch warnings in dev (nans allowed) (rev.378ec35d)
	- spirouTelluric.py - kernal resize (rev.0ccbf573)
	- obj_mk_tellu.py - shift data to master before (to match tapas) - instead of shifting transmission after (rev.0a12fbe4)
	- spirouUnitRecipes.py - add cal_CCF_E2DS_FP_spirou to unit tests (rev.2dd9812f)



================================================================================
* Tue Oct 23 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.047

================================================================================
	- Cal_Test.run - add cal_wave_mapper to tested recipes (rev.919bab3b)
	- spirouExoposureMeter.py - use wave parameters instead of wave map + add normalisation option (rev.06bd46d1)
	- constants_SPIROU_H4RG.py - add constants for normalisation and flat_correction (rev.19d348fb)
	- cal_exposure_meter.py - try rescale for the flux (Issue #490) (rev.bba4f0f8)
	- cal_wave_mapper.py - divide through by flat field (on request) and attempt to rescale flux (Issue #490) (rev.92e9da4d)
	- spirouExoposeMeter.py - Issue #490 - add ability to not re-calculate order profile image (if already processed) + add shape as well as tilt (use shape if in calibDB) (rev.0a1e0cee)
	- spirouKeywords.py - add infilelist as keyword (For use for pushing input file list to header) (rev.c5ff8dd4)
	- spirouConst.py - define a tmp file for the order profile map (Issue #490) (rev.29b9fb33)
	- cal_wave_mapper.py - Issue #490 - add shape + fix badpixel function returns (rev.ce9b02e7)
	- cal_exposure_meter.py - fix Issue #490 - use shape file + correct output of badpix mask (rev.42d25934)



================================================================================
* Wed Oct 24 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.048

================================================================================
	- spirouRV.py - need to deal with the differing fibers (for now manually) (rev.fc830e27)
	- spirouRV.py - added function "get_foberc_e2ds_name" to deal with the different file types expected --> need E2DS AB file for C fiber (rev.a1d25393)
	- spirouPOLAR.py - adjusted calls to headers to not be hard coded (should have been called from p --> spirouKeywords.py) (rev.8dca7843)
	- spirouKeywords.py - add MJEND keyword (for pol_spirou.py) - also changed naming to all upper case (rev.78325376)
	- obj_mk_tellu.py - turn off debug plot (rev.0da1f19c)
	- cal_CCF_E2DS_FP_spirou.py - get correct filename for fiber C (E2DS file only) (rev.5dd7ca94)
	- cal_validate_spirou.py - add option to check (check=0 just prints paths) (rev.79b84d63)
	- cal_CCF_E2DS_FP_spirou.py - correct imports and catch warnings (As with cal_CCF_E2DS_spirou) (rev.0bec7905)
	- cal_CCF_E2DS_FP_spirou.py - correct link to header key in p (rev.4bf1b2f7)
	- spirouKeywords.py - make tellu header keys shorter (rev.537379cb)
	- cal_CCF_E2DS_FP_spirou.py - load file C not from a telluric corrected spectrum but from the E2DS itself (using header) (rev.5dad40f9)
	- spirouExposeMeter.py - fix some pep8 issues (rev.235c55e2)
	- spirouKeywords.py - add header key definitions for options input in tellu (rev.989d0747)
	- obj_fit_tellu.py - add extra header keys to know how many components were fit in PCA etc (rev.f5332212)
	- cal_CCF_E2DS_spirou.py - fix some pep8 convension (rev.1bc50559)
	- update unit test runs (rev.3f76805e)
	- spirouUnitRecipes.py - update input name for cal_exposure_meter and cal_wave_mapper (rev.dbf131fd)
	- cal_exposure_meter.py - correct input name: "reffile" --> "flatfile" (rev.3466c645)
	- cal_CCF_E2DS_spirou.py + spirouRV.py - catch warnings for NaNs in mean and divide (rev.04cfcd89)



================================================================================
* Thu Oct 25 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.049

================================================================================
	- Tellurics2.run - add a second telluric run - to preprocess, extract and mk_tellu missed tellurics (rev.55e83023)
	- update test - only 1 telluric test + move others to old_tests (rev.6d297f4e)
	- spirouTelluric.py - template should be in MASTERWAVE frame not WAVE_IT frame (rev.4ef17b4d)
	- spirouPlot.py - modify tellu_fit_debug_shift_plot to only plot one order (rev.57997f9c)
	- recipe_control.txt - allow cal_CCF_E2DS_FP_spirou to use A, B files and TELLU_CORRECTED/POL_ files (rev.d0ad00b1)
	- update unit tests (rev.059f866a)
	- obj_fit_telluy.py - todo question about possibly broken plot (rev.d458a499)
	- spirouFile.py - better error message when wrong directory used for input files (rev.454addce)
	- new unit_test runs for maestria with missed Gl699 targets (rev.53e80579)
	- update test files - mistake in run018b (rev.2b709e4c)
	- Gl699_Aug05-A_B.run - unit test run for A and B files (rev.acad317d)



================================================================================
* Fri Oct 26 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.050

================================================================================
	- spirouKeywords.py - add separate set of header keys for the FP analysis (rev.bfa12618)
	- spirouConst.py - add CCF_FP versions so files are separate (for now) (rev.7d10cf74)
	- output_keys.py - add new keys for CCF_FP (rev.9494aeab)
	- spirouConfig.py - define a copy function for ParamDict - copy all keys into new ParamDict (rev.eb344c56)
	- cal_CCF_E2DS_FP_spirou.py - separate and keep separate the FP analysis (cp and cloc) - including header keys (rev.488a4b49)



================================================================================
* Fri Oct 26 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.051

================================================================================
	- pep8 clean up (rev.e2f3254a)
	- update TODO's, remove old H3RG dependencies and clean up (rev.b5721f9a)



================================================================================
* Mon Oct 29 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.052

================================================================================
	- pep8 clean up (rev.edded0ad)



================================================================================
* Mon Oct 29 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.053

================================================================================
	- add hc_test.run back to unit tests (rev.d3f4b083)



================================================================================
* Tue Oct 30 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.054

================================================================================
	- test_wavsol.py - fixed bugs and added STD for H band (rev.94eaa633)
	- test_wavsol.py - added code to compare wave solutions from a calibDB (defined manually in the code) (rev.cfc23578)
	- HC_Test.run - added run 47 back in (had been missed) (rev.1f1e6104)



================================================================================
* Wed Nov 07 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.3.055
================================================================================
	- Add hcone files for the cal_DRIFTCCF_E2DS recipe (rev.11998745)
	- New UrNe CCF mask based on lines used for the wavelength solution and to be used to compute DRIFT on hcone files (rev.e572c156)



================================================================================
* Thu Nov 08 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.056

================================================================================
	- spirouWAVE.py - Melissa's fix for Issue #507 ->   "<" needs to be "<=" (rev.38b9c0b1)



================================================================================
* Tue Oct 30 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.057

================================================================================
	- cal_WAVE_NEW update (rev.ab94ecd8)



================================================================================
* Wed Oct 31 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.058

================================================================================
	- cal_WAVE_NEW update (rev.bee08367)



================================================================================
* Thu Nov 01 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.059

================================================================================
	- Test of not using Littrow sols for cal_WAVE_EA (rev.69b43391)



================================================================================
* Thu Nov 08 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.060

================================================================================
	- cal_WAVE_EA match to master (rev.e38c6619)
	- Bug fix for fit_gaussian triplet (fixes #507) (rev.863e2dfb)



================================================================================
* Thu Nov 08 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.061

================================================================================
	- update date/version/changelog (rev.92c692e8)



================================================================================
* Wed Nov 14 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.062

================================================================================
	- fit_triplets sigma-clip change (rev.b6f7746f)
	- cal_WAVE_E2DS_EA - fix HC file being overwritten with FP data (fixes #513) (rev.56007df4)



================================================================================
* Tue Nov 20 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.063

================================================================================
	- add test files to misc (rev.e50431cb)
	- add Etiennes files in misc folder (rev.5d9698d8)
	- Runs - update the unit tests (rev.e4f1a9b7)



================================================================================
* Wed Nov 21 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.064

================================================================================
	- add copy of old xt code (to compare with new one for changes) (rev.1218e840)
	- add function: read_cavity_length, get_shape_map2, get_offset_sp for new shape code (rev.99f7a855)
	- spirouConst.py - add new file definitions (rev.c9045df7)
	- output_keys.py - add defintions for shape sanity check debug files (rev.058679ad)
	- notes on etiennes codes - no real changes just comments (rev.0b376319)
	- constants_SPIROU_H4RG.py - modify SHAPE constants to for new shape code (rev.1801851a)
	- obj_mk_tellu.py - fix copy of code - redundant (rev.e1a1d7f3)
	- cal_SHAPE_spirou2.py - modification of cal_SHAPE_spirou.py with changes to cal_shape needed (rev.9467b289)
	- spirouBERV.py - fix bug in berv code - non-objects should not look for star parameters (rev.de5e6cc5)



================================================================================
* Thu Nov 22 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.065

================================================================================
	- spirouTable.py - updated the error outputs to include filename (rev.8d78f0f0)
	- spirouImage.py - continued to modify get_offset_sp and get_shape_file2 (for new SHAPE code) (rev.8dcde75d)
	- spirouPlot.py - adjusted slit_shape_angle_plot and added slit_shape_offset_plot (for new SHAPE recipe) (rev.02eacc31)
	- spirouMath.py - adjusted problem in gauss_fit_s file "correction = (x - np.mean(x)) * slope" --> "correction = (x - x0) * slope" (rev.593b0493)
	- updated the catalogue_UNe.dat file and added cavity_length.dat file (for new SHAPE code) (rev.3e291d5f)
	- master_tellu_SPIROU.txt - updated the master calibdb with the new MASTER_WAVE.fits (rev.135870af)
	- master_calib_SPIROU.txt - updated the master calibdb with the new MASTER_WAVE.fits (rev.04ab9bb4)
	- recipe_control.txt - added cal_SHAPE_spirou2 to the recipe control (with two arguments for FP_FP and HC_HC files - pp fits not e2ds!) (rev.ab4a4df5)
	- constants_SPIROU_H4RG.py - added new constants and modified constants changed by Etienne (rev.5aeeac6d)
	- cal_SHAPE_spirou2.py - continued work on adapting Etiennes changes into cal_SHAPE (rev.5011215e)



================================================================================
* Fri Nov 23 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.066

================================================================================
	- spirouFits.py - fix bug with hdict being empty (possible on some writes) (rev.505b1705)



================================================================================
* Sat Nov 24 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.067

================================================================================
	- Cal_Test.run - add cal_SHAPE_spirou2 to Cal_Test.run (rev.c04b93a9)
	- unit tests: add cal_SHAPE_spirou2 to unit test definition (rev.9d48194d)
	- spirouImage.py - update get_shape_map2 and get_offset_sp in-line with Etienne's changes (rev.8c29b9e5)
	- spirouPlot.py - update new shape plots in-ilne with Etiennes changes (rev.90d51ec7)
	- spirouMath.py - update "gauss_fit_s" (Etienne updated it) (rev.1338156b)
	- spirouKeywords.py - add extra keys (for index.fits) and for wave-list in bigcubes (rev.a8114448)
	- spirouConst.py - update acquisition of filenames now we have "HCFILE" and "FPFILES" (not "HCFILES" and "FPFILE") (rev.f9756ecc)
	- constants_SPIROU_H4RG.py - update constants inline with Etiennes changes (rev.9054d7d2)
	- obj_mk_obj_template.py - list wave files in header (along with file name and berv) for big cube (rev.a50cab72)
	- cal_SHAPE_spirou2.py - continued work on shape upgrade + now 1 hcfile and multiple fp files (rev.f351dfa3)



================================================================================
* Sat Nov 24 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.068

================================================================================
	- update extraction trigger (rev.f0713458)
	- spirouConst.py - add MJDATE to index.fit (rev.7e2d2bd0)
	- cal_SHAPE_spirou/spirou2 - correct mistakes found by unit test run (rev.86e39c45)
	- obj_mk_obj_template.py - list wave files in header (along with file name and berv) for big cube (rev.a50cab72)



================================================================================
* Mon Nov 26 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.069

================================================================================
	- run_off_listing.py - correct to try/except in run_off_listing.py (rev.deea1f03)
	- extract_trigger.py - upgrades to extract trigger just do extractions (rev.7026d36c)
	- run_off_listing.py - code to redo indexing (rev.801bc170)
	- spirouStartup.py - fix error with change to indexing (and old index files) (rev.898a8382)
	- spirouConst.py - change func_name for REDUC_OUTPUT_COLUMNS (rev.a58fba12)



================================================================================
* Mon Nov 26 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.070

================================================================================
	- update test.run (rev.2fe5d94c)
	- run_off_listing.py - fix errors in code (rev.9c9b8b2c)



================================================================================
* Tue Nov 27 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.071

================================================================================
	- extract_trigger.py - correct problems with pre-processing automation (rev.8db96a67)
	- recipe_control.txt - add some more options for POL_STOKES_I (rev.f39841c9)



================================================================================
* Wed Nov 28 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.072

================================================================================
	- changes to parallelisation (test) (rev.3064be67)
	- extract_trigger.py - updates to extraction trigger (rev.bc91d1f0)
	- tellu_whitelist.txt - a white list of telluric stars (rev.412bbbc6)



================================================================================
* Fri Nov 30 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.3.073

================================================================================
	- update test.run (rev.f51360fd)



================================================================================
* Mon Dec 03 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.074

================================================================================
	- spirouConst.py - modify colour for white screen people (rev.83479b2b)
	- spirouKeywords.py - update keys (must be shorter with addition of numbers) (rev.6a86af56)
	- spirouKeywords.py - update keys (must be shorter) (rev.bb59520b)
	- spirouUnitRecipes.py - remove cal_SHAPE_spirou2 (rev.f286c920)
	- extract_trigger.py - update run arguments (rev.d88bdf11)
	- unit_tests - update test.run and Pol_Test.run (rev.41d60edd)
	- spirouStartup.py - add functionality to assign process id (on begin) --> timestamp (rev.cf65f584)
	- spirouTable.py - update comment to give some idea of the IDL command to open table (rev.a574089c)
	- spirouLog.py - start process of having individual logs for each instance (rev.97b0af0b)
	- recipe control - adjust inputs to cal_SHAPE_spirou (rev.ea84d8fd)
	- cal_SHAPE_spirou.py - change name of cal_SHAPE_spirou2.py --> cal_SHAPE_spirou.py (rev.3cb553ae)
	- spirouLSD.py - modify output of LSD table to be a FIT BINARY Table. (rev.875836e4)
	- extract_trigger.py - update extract_trigger run constants (rev.66e47fd4)
	- spirouLSD.py - change format of output to FITS table (rev.8e55bbe5)
	- spirouTable.py - add option in write_table to accept header (hdict) (rev.01d1b0f7)
	- spirouUnitRecipes.py - remove reference to cal_SHAPE_spirou2.py (rev.8ee9fe6a)
	- extract_trigger.py - update run parameters (and slightly change order of constants) (rev.1ddfcb45)
	- cal_SHAPE_spirou.py - change reference to GetShapeMap2 --> GetShapeMap (rev.515233e7)
	- spirouImage.py - change get_shape_map2 --> get_shape_map (change old get_shape_map --> get_shape_map_old) (rev.ad1ce473)
	- recipe_control.txt - change cal_SHAPE_spirou2 --> cal_SHAPE_spirou (remove old one) (rev.6f25b15c)
	- cal_SHAPE_spirou.py - renamed from cal_SHAPE_spirou2.py (old code moved to ./misc) (rev.e82e71a1)


================================================================================
* Mon Dec 03 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.074

================================================================================
	- improvements to fp_wavelength_sol_new fp m value determination (rev.630b4d1c)
	- Littrow: get total orders from echelle_orders, not all_lines; (rev.caacdbb9)
	- spirouMath: calculates wave coeff from chebyshev polynomials (rev.c9e38fcb)
	- cal_WAVE_NEW_E2DS_EA update (calculates wave sol, does Littrow) (rev.0cbd9a55)
	- cal_WAVE_EA order information on Littrow QC fail (rev.23992b18)


================================================================================
* Mon Dec 03 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.074

================================================================================
	- improvements to fp_wavelength_sol_new fp m value determination (rev.630b4d1c)
	- Littrow: get total orders from echelle_orders, not all_lines; (rev.caacdbb9)
	- spirouMath: calculates wave coeff from chebyshev polynomials (rev.c9e38fcb)
	- cal_WAVE_NEW_E2DS_EA update (calculates wave sol, does Littrow) (rev.0cbd9a55)
	- cal_WAVE_EA order information on Littrow QC fail (rev.23992b18)


================================================================================
* Mon Dec 03 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.074

================================================================================
	- cal_WAVE_EA order information on Littrow QC fail (rev.23992b18)


================================================================================
* Tue Dec 04 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.075

================================================================================
	- spirouImage.py - adjust warning for getting unix_time from string (where time is not valid) - warning or error? (rev.3259a87c)


================================================================================
* Tue Dec 04 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.3.075

================================================================================
	- Remove hard-coded initial wavelenth solution (rev.19a390c7)


================================================================================
* Wed Dec 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.076

================================================================================
	- SpirouDRS/spirouUnitTest folder - major redo of logging system (to allow passing of process-id) (rev.1ddc7ce8)
	- SpirouDRS/spirouUnitTest folder - major redo of logging system (to allow passing of process-id) (rev.63d77a70)
	- SpirouDRS/spirouTools folder - major redo of logging system (to allow passing of process-id) (rev.60eb724b)
	- SpirouDRS/spirouTHORCA folder - major redo of logging system (to allow passing of process-id) (rev.b1296a33)
	- SpirouDRS/spirouTelluric folder - major redo of logging system (to allow passing of process-id) (rev.95e899de)
	- SpirouDRS/spirouStartup folder - major redo of logging system (to allow passing of process-id) (rev.40e34a32)
	- SpirouDRS/spirouRV folder - major redo of logging system (to allow passing of process-id) (rev.a7af7572)
	- SpirouDRS/spirouPOLAR folder - major redo of logging system (to allow passing of process-id) (rev.3f31fae2)
	- SpirouDRS/spirouLOCOR folder - major redo of logging system (to allow passing of process-id) (rev.9ac8a178)
	- SpirouDRS/spirouImage folder - major redo of logging system (to allow passing of process-id) (rev.988e61c8)
	- SpirouDRS/spirouFLAT folder - major redo of logging system (to allow passing of process-id) (rev.a3e6e679)
	- SpirouDRS/spirouEXTOR folder - major redo of logging system (to allow passing of process-id) (rev.208b2185)
	- SpirouDRS/spirouDB folder - major redo of logging system (to allow passing of process-id) (rev.185b997d)
	- SpirouDRS/spirouCore folder - major redo of logging system (to allow passing of process-id) (rev.46e4ac00)
	- SpirouDRS/spirouConfig folder - major redo of logging system (to allow passing of process-id) (rev.b9c4c9b7)
	- SpirouDRS/spirouBACK folder - major redo of logging system (to allow passing of process-id) (rev.e62cb4ae)
	- spirou_drs/misc folder - major redo of logging system (to allow passing of process-id) (rev.5c500a2d)
	- spirou_drs/bin folder - major redo of logging system (to allow passing of process-id) (rev.e13ced1e)
	- spirou_drs/bin folder - major redo of logging system (to allow passing of process-id) (rev.1f5eb344)
	- cal_extract_RAW_spirou.py - remove the need to a TILT file is mode == '4a' or '4b' (rev.a350cc64)
	- cal_extract_RAW_spirou.py - remove the need to a TILT file is mode == '4a' or '4b' (rev.5c691af3)
	- spirouConfigFile.py - update comment to make it clear why two tests are needed (rev.16a34834)



================================================================================
* Fri Dec 07 2018 Neil Cook <neil.james.cook@gmail.com> - 0.3.077

================================================================================
	- spirouTable.py - add lock files around writing to fits file (avoids writing at the same time) (rev.e3f2ada7)
	- spirouImage.__init__.py - add links to check/close/open fits lock file (rev.1cd383ab)
	- spirouFITS.py - add fits file lock file (to avoid writing to same fits file at same time) (rev.341852d3)
	- spirouDB.py - edit message and sleep time for waiting lock file (rev.397681b6)
	- extract_trigger - update to allow skipping of mk_tellu and fit_tellu files (rev.61ec0ff4)
	- obj_fit_tellu.py - fix problems with WLOG update (rev.3c9fcf89)
	- spirouStartup.py - add telluDB info to the start up printout/log (rev.9df24d42)


================================================================================
* Sat Dec 08 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.000

================================================================================
    - confirmation of parallisation (log/fits/databases)

================================================================================
* Sat Dec 08 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.001

================================================================================
	- unit_Test runs - update test for run (rev.789dff2e)
	- extract_trigger.py - update values for run time (rev.2ed5440a)
	- spirouStartup.py - define initial values for log_opt and program in Begin() (rev.0d016ad7)
	- constants_SPIROU_H4RG.py - add "fitsopen_max_wait" time (rev.b1d766bd)
	- cal_reset.py - fix fake p (with real p) (rev.bbbe93c7)


================================================================================
* Sat Dec 08 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.002

================================================================================
	- constants_SPIROU_H4RG.py - add "fitsopen_max_wait" time (rev.b1d766bd)


================================================================================
* Mon Dec 10 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.003

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py - correct pep8 and add TODO's for problems (rev.b4e5a6f3)
	- cal_WAVE_NEW_E2DS_spirou.py - correct pep8 and WLOG changes (rev.9bfbdf50)
	- update timings for V0.4.001 (rev.89c6b2c1)
	- spirouRV.py - change an info log message to general log message (too many for CCF) (rev.8e990df7)
	- spirouLSD.py - remove some of the info logs and make them general logs (rev.42142016)
	- pol_spirou.py - remove some of the info logs and make them general logs (rev.56fb9972)


================================================================================
* Mon Dec 10 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.004

================================================================================
	- spirouConst.py - undo change to global file (rev.2ddb2b7c)
	- spirouFITS.py - fix for lock file on non-fits files (rev.1c7fe0ae)



================================================================================
* Tue Dec 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.005

================================================================================
	- spirouTable.py - fix an error with missing end card (rev.6eb263e0)
	- update extraction_trigger.py run time parameters (rev.775066b2)
	- cal_validate_spirou.py - correct cal_validate for new wlog (rev.678f0b30)



================================================================================
* Wed Dec 12 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.006

================================================================================
	- add .idea to .gitignore (rev.9a0fd322)
	- cal_WAVE_E2DS_EA_spirou.py - pep8 clean up of Francois branch (rev.d9583cb0)
	- cal_DRIFTPEAK_E2DS_spirou.py - pep8 clean up of Francois branch (rev.be5cbc4e)
	- cal_CCF_E2DS_FP_spirou.py - pep8 clean up of Francois branch (rev.07660540)
	- code to check the telluric corrections (rev.9e56bd98)
	- update requirements (barycorrpy required) (rev.91b15f56)
	- Update README.md (rev.c8d7624a)
	- add a minimum requirements and current requirements (as .txt files) (rev.3463fd8a)
	- re-do requirements files (rev.9f3487b1)


================================================================================
* Wed Dec 12 2018 FrancoisBouchy <francois.bouchy@unige.ch> - 0.4.006

================================================================================
	- Format of flux ratio set to .3f (rev.2831f5fb)
	- Compute the absolute CCF drift of the FP and save it in the wavelength solution file as CCFRV2. (rev.3df4cea9)
	- Absolute CCF drift of FP is read from the wavelength solution file. The relative CCF drift takes into account this Absolute drift. (rev.68e9fd5f)


================================================================================
* Thu Dec 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.007

================================================================================
	- extract_trigger.py - changes to reprocessing code (correct order) (rev.7529390b)



================================================================================
* Thu Dec 13 2018 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.4.008

================================================================================
	- constants_SPIROU_H4RG: new constants for start/end littrow orders (rev.3f494eb6)
	- cal_WAVE_E2DS_EA: littrow can now start and end at any order. (rev.ce2da33d)
	- extrapolate_littrow_sol: correct initial littrow order (rev.4c101d66)
	- WAVE_FILE_EA_2 function adds fp filename to wavefilename (rev.f5f8d42b)
	- cal_WAVE_NEW shifted plots (rev.481ec09c)



================================================================================
* Thu Dec 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.008

================================================================================
	- update date/version/changelog (rev.0580ec32)



================================================================================
* Fri Dec 14 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.009

================================================================================
	- cal_CCF_E2DS_FP_spirou.py - fix if CCF_RV2 not in whdr (rev.097f46e6)
	- cal_CCF_E2DS_FP_spirou.py - fix if CCF_RV2 not in whdr (rev.2189d76f)
	- cal_CCF_E2DS_FP_spirou.py - fix if CCF_RV2 not in whdr (rev.3f7ff4a2)
	- test.run - update for current testing (rev.a42191d8)
	- cal_CCF_E2DS_FP_spirou.py - fix crash bug Exception --> SystemExit (rev.dace47b0)
	- test.run - change for continued test (rev.10582fa0)
	- test.run - change for continued test (rev.77a69aa6)
	- spirouTHORCA.py - fudge factor fix --> n_order_init = p['IC_LITTROW_ORDER_INIT_{0}'.format(1)] (rev.b3c58d8a)
	- spirouTHORCA.py - test fix (rev.4e0ad479)
	- spirouTHORCA.py - fix for n_order_init (from init --> init_1/init_2) (rev.57f7978c)
	- update test.run - cal_test.run (from cal_WAVE) onwards (rev.80044088)
	- spirouConst.py - pep8 changes to WAVE_FILE_EA_2 (rev.ceb49645)
	- cal_WAVE_NEW_E2DS_spirou.py - pep8 changes (rev.e7b111d2)
	- cal_WAVE_E2DS_EA_spirou.py - few logic checks and pep8 changes (rev.cc8c4969)
	- extract_trigger.py - update run time parameters (rev.e7a3d9af)
	- extract_trigger.py - fix incompatible version of cal_shape in reprocessing code (rev.b796998b)



================================================================================
* Sun Dec 16 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.010

================================================================================
	- wave_sol_to_header.py - code to update header of all e2ds/e2dsff (object and fpfps) in a night_name or all files (rev.37605873)



================================================================================
* Mon Dec 17 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.011

================================================================================
	- obj_mk_obj_template.py - fix bug when forcing calibDB from wave solution (calibDB needs to be re-read each time) (rev.4687dfe6)
	- obj_mk_obj_template.py - fix bug when forcing calibDB from wave solution (calibDB needs to be re-read each time) (rev.5f70210b)
	- obj_mk_obj_template.py - fix bug when forcing calibDB from wave solution (calibDB needs to be re-read each time) (rev.a5310966)
	- spirouLog.py - update log to allow option to be added (by default uses "RECIPE" or "LOG_OPT" or '') (rev.9b01e846)



================================================================================
* Tue Dec 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.012

================================================================================
	- spirouStartup.py - update display (rev.ee002954)
	- spirouConst.py - update colours and themes and Color Class (rev.123fb988)
	- spirouLog.py - add debug and custom colour modes to log messages (rev.770686a3)
	- spirouLog.py - add debug and custom colour modes to log messages (rev.86d4f714)
	- spirouConst.py - update log constants (rev.be0181d9)
	- obj_mk_obj_template.py - adjust log message to be more clear (rev.b165e004)
	- test codes for testing bug in BigCube/telluDB (rev.e4ee7a8f)
	- spirouFile.sort_by_name - return sort indices not array (so we can sort multiple arrays) (rev.8f5a675b)
	- obj_mk_obj_template.py - fix bug in sorting files (wrong OBJNAME for filename) (rev.06bb3cd1)



================================================================================
* Wed Dec 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.013

================================================================================
	- spirouLog.py - fix for printlogandcmd now having argument "colour" (rev.9173cf21)
	- spirouLog.py - update of ipdb to allow magic commands (rev.e9f7928d)



================================================================================
* Mon Jan 07 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.014

================================================================================
	- spirouDB.py - changed from reading human date to reading julian date, changed to use astropy.timea (rev.770e16e9)
	- spirouCDB.py - reformatted calibDB functions to use spirouDB wherever possible, changed from reading human date to reading julian date, changed to use astropy.time (rev.768bf28d)
	- spirouDB.__init__.py - moved location of get_acqtime (moved to spirouDB) (rev.9b0a19da)
	- spirouKeywords.py - removed KW_ACQTIME_KEY and KW_ACQTIME_KEY_JUL in place of KW_ACQTIME (which is the modified julian date) - with supporting format in case of change (uses astropy.time) (rev.b7e0890f)
	- spirouConst.py - removed the use of ACQTIME_KEY_JUL now uses KW_ACQTIME (which is the modified julian date by definition) (rev.0c4488f9)
	- cal_HC_E2DS_EA_spirou.py - changed acqtime to ACQTIME (for consistency) (rev.6c6f3a42)
	- updated version/date/changelog (rev.958cf147)



================================================================================
* Tue Jan 08 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.015

================================================================================
	- spirouPOLAR.py - fix dependence on KW_ACQTIME_KEY_JUL --> KW_ACQTIME (rev.82ad0648)
	- spirouCDB.py/spirouDB.py - change all human times to be in format YYYY-mm-dd_HH:MM:SS.f for consistency (rev.3667e33b)
	- test.run - update test.run to finish testing (start before last failure) (rev.9bf132d5)
	- spirouDB.py - fix database definitions in modified "get_database" function (rev.0e06e038)
	- update the reset files for the calibDB and telluDB (rev.efbb2ecb)



================================================================================
* Tue Jan 15 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.016

================================================================================
	- spirouLog.py - fixed an error with logging (if p not set crashes because there was no DRS_DEBUG key -- fixed now) (rev.295e54e3)
	- spirouRV.py - fixed bug found with part of correlbin - only affects spectra which have peaks with start/end different by +2 (rare?) but for now using the old correlbin which works for these (rev.94541178)



================================================================================
* Mon Jan 28 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.017

================================================================================
	- spirouLog.py - fix a bug in logger (only a problem when log breaks) (rev.9751cb5c)



================================================================================
* Tue Jan 29 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.020

================================================================================
	- update .gitignore to ignore .npy files (rev.3102dda5)
	- spirouTelluric.py - added aliases to two new mk_tellu functions (rev.241a639f)
	- spirouTelluric.__init__.py - added aliases to two new mk_tellu functions (rev.9831cd9f)
	- spirouKeywords.py - added two new keywords for new mk_tellu recipe (rev.d0df6a87)
	- spirouConfig.py - update bug in ConfigError (forced list) (rev.058ca76a)
	- combine_tapas.py - new mk_tellu recipe (original code from E.A.) (rev.5b61430e)
	- obj_mk_tellu_new.py - new mk_tellu recipe (rev.61ed4431)



================================================================================
* Wed Jan 30 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.021

================================================================================
	- spirouTelluric.py - continue to write/upgrade new mk_tellu functions and functions for mk_tellu_db (rev.d82ed3d1)
	- spirouPlot.py - add new mk_tellu plot (rev.3c6bc979)
	- spirouConst.py - add definition of whitelist file (rev.74195499)
	- tellu_whitelist.txt - add a white list of all possible telluric star names (rev.a2f6aaf3)
	- constants_SPIROU_H4RG.py - add constants from new recipes (rev.2c92099a)
	- obj_mk_tellu_db.py - move constants to constants files and functions to spirouTelluric (rev.1aa8bcdd)
	- obj_mk_tellu_new.py - move constants to constants file (rev.36bd4823)
	- obj_mk_tellu_new.py - update code with Etienne's changes (rev.a915f5c4)
	- obj_mk_tellu_db.py - new wrapper script for mk_tellu + fit_tellu on tellurics -- creates the telluric database (rev.28f58782)



================================================================================
* Fri Sep 14 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.022

================================================================================
	- input update: spirouStartup.__init__.py aliases / imports to spirouStartup2 (temporary) (rev.2b0a31d7)
	- input update: recipes.py - holder for recipe definitions (rev.eff7f0de)
	- input update: spirouRecipe.py - holder for new recipe classes (rev.9fc3df0c)
	- input update: spirouStartup2.py - holder for new spirouStartup (rev.0f76d5c1)
	- input update: test_recipe.py - test recipe to test new input functions (rev.5ac23025)



================================================================================
* Mon Sep 17 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.023

================================================================================
	- test_recipe: todo's added (rev.db6b4c50)



================================================================================
* Tue Sep 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.024

================================================================================
	- test_recipe.py - continue work on getting new input method to work (rev.1b14bb82)
	- spirouStartup2.py - continue work on getting new input method to work (rev.6565c08f)
	- spirouRecipe.py - continue work on getting new input method to work (rev.e13c00e8)
	- recipes.py - add test recipe to test new definition method (rev.31c8d34e)
	- spirouConst.py: fix pep8 issue - brackets not needed (rev.d94c4147)



================================================================================
* Sat Oct 06 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.025

================================================================================
	- input_file.txt - update list of inputs (Issue #475) (rev.7d128651)



================================================================================
* Wed Oct 31 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.026

================================================================================
	- recipe.py - add new comment (rev.344e055f)



================================================================================
* Thu Nov 01 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.027

================================================================================
	- spirouStartup2.py - continue work on input code (rev.300cffd5)
	- spirouRecipe.py - continue work on input code (rev.1760f449)
	- spirouFiles.py - define file types using new classes (rev.71b24452)
	- recipe.py - update recipe definitions based on changes (rev.c3a54c1a)



================================================================================
* Fri Nov 02 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.028

================================================================================
	- spirouRecipes.py - add todo (rev.9eb4acfe)
	- spirouStartup2.py - pushed renaming of recipes --> recipes_spirou into code (rev.791e65a1)
	- recipes_spirou.py - renamed from recipes.py (rev.4c7c42d0)
	- files_spirou.py - renamed from spirouFiles.py (rev.a5baf0a7)
	- spirouRecipe.py - add doc strings for new classes (DrsArgument/DrsRecipe/DrsInputFile/DrsFitsFile) (rev.b83ac3b5)
	- test_receip.py - update with new name for "ufiles"-->"filelist" (rev.874e1f9d)
	- spirouStartup2.py - continue work on input code - update with changes to spirouRecipe.py (rev.ea087a87)
	- spirouRecipe.py - define how DrsArgument, DrsRecipe and DrsInput (+DrsFitsFile) interact - continued testing of input redo (rev.80fac467)
	- spirouFiles.py - define all raw/pp/out files as instances of DrsFitsFile (rev.4329be95)
	- recipes.py - continue to test new inputs with test_recipe definition (rev.0ec7a5ec)



================================================================================
* Sun Nov 04 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.4.029

================================================================================
	- spirouRecipe.py - move DrsInputs from here to spirouFile.py (rev.0ba855fe)
	- spirouFile.py - move DrsInputs from spirouRecipes to here (rev.d9b64fc8)
	- files_spirou.py - update links to DrsInput: spirouRecipe --> spirouFile (rev.f5bcd1be)



================================================================================
* Mon Nov 05 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.030

================================================================================
	- test_recipe.py - tested cal_FF_RAW_spirou.py inputs (rev.f5f08d0e)
	- spirouStartup2.py - modified code to line up with continued work on spirouRecipe (rev.55cffad5)
	- spirouRecipe.py - continued to develop new recipe class (rev.7d0f889e)
	- spirouFile.py - filled out some attributes/methods (rev.acb0448f)
	- recipe_spirou.py - added more definitions and started to fill out drs recipes (badpix --> extract) (rev.e374e384)
	- files_spirou.py - updated call to spirouFile.DrsInput --> spirouFile.DrsInputFile (rev.75474e5a)



================================================================================
* Tue Nov 06 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.031

================================================================================
	- test_recipe.py - tested cal_badpix_spirou.py (rev.b166a655)
	- spirouStartup2.py - continue work on inputs update (rev.865c8b8d)
	- spirouRecipe.py - continue work on inputs update (rev.f5733bbe)
	- spirouFile.py - allow filename to be set in construction (via kwargs) (rev.089d89b2)
	- recipes_spirou.py - add and reformat options to set/take defaults (rev.6f545f46)
	- spirouConst.py - add a variable that can globally update pp (for use when we don't have p) (rev.94a3124b)



================================================================================
* Wed Nov 07 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.032

================================================================================
	- spirouFile.py - continue to fill out drs file fits methods (rev.9f9812d9)



================================================================================
* Fri Nov 09 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.033

================================================================================
	- continued work on input redo (rev.dbd27ff3)



================================================================================
* Wed Nov 14 2018 njcuk9999 <neil.james.cook@gmail.com> - 0.4.034

================================================================================
	- test_recipe.py - change permissions for file (rev.e6b0e61f)



================================================================================
* Mon Dec 10 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.035

================================================================================
	- spirouStartup2.py - upgrade WLOG (requires drs_params to track pid) (rev.6205431c)
	- spirouRecipe.py - upgrade WLOG (requires drs_params to track pid) (rev.92f0007d)
	- spirouFile.py - upgrade WLOG function (requires drs_params to track pid) (rev.7753211d)
	- recipes_spirou.py - fix pep8 in helpstr (rev.8ee02be1)



================================================================================
* Tue Dec 11 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.036

================================================================================
	- cal_validate_spirou.py - correct cal_validate for new wlog (rev.796ed8d5)



================================================================================
* Thu Dec 13 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.037

================================================================================
	- spirouRecipe.py - update to check code (put into DrsRecipe class as methods) (rev.b72afd7c)
	- spirouRecipe.py - update to check code (put into DrsRecipe class as methods) (rev.58ad7139)



================================================================================
* Fri Dec 14 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.038

================================================================================
	- spirouRecipe.py and spirouStartup2.py - continued update to input redo (rev.ff7bc6a5)
	- extract_trigger.py - fix incompatible version of cal_shape in reprocessing code (rev.63355b10)



================================================================================
* Sat Dec 15 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.039

================================================================================
	- spirouFile.py - continued work on input redo (rev.9977ecdb)
	- spirouRecipe.py - continued work on input redo (rev.b92dbc98)



================================================================================
* Mon Dec 17 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.040

================================================================================
	- spirouRecipe.py - continued work on input redo (rev.31bde9c9)
	- spirouStartup2.py - continued work on input redo (rev.cdb97a96)
	- spirouRecipe.py - continued work on input redo (rev.caf6eed0)
	- spirouFile.py - continued work on input redo (rev.95445f3e)
	- test_recipe.py - continued update for input_redo (rev.1cde31f9)
	- spirouRecipe.py - continued update for input_redo (rev.5bb64505)
	- spirouFile.py - continued update for input_redo (rev.c8f04154)



================================================================================
* Tue Dec 18 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.041

================================================================================
	- test_recipe.py - continued update of input redo (rev.c9955ad2)
	- spirouStartup2.py - continued update of input redo (rev.b11a4897)
	- spirouStartup.py - update from spirouStartup2.py (rev.abdd0224)
	- spirouRecipe.py - continued update of input redo (rev.0c15ba7b)
	- spirouFile.py - continued update of input redo (rev.80c0198b)



================================================================================
* Wed Dec 19 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.042

================================================================================
	- spirouRecipe.py - continue input redo upgrade (rev.91d4d565)
	- spirouFile.py - add some extra empty attributes to DrsInputFile and DrsFitsFile (rev.eb8986cd)
	- spirouLog.py - alias for embeded ipython (in ipdb type "ipython()") (rev.c3dcd509)
	- recipes_spirou.py - update values during input_redo upgrade (rev.1f360422)
	- test_processing.py - script to test input_redo with processing (rev.40396dba)



================================================================================
* Fri Dec 21 2018 Neil Cook <neil.james.cook@gmail.com> - 0.4.043

================================================================================
	- test_processing.py - continued work on input_redo (rev.39352e5a)
	- spirouRecipe.py - continued work on input_redo (rev.86ffc793)
	- recipes_spirou.py - continued work on input_redo (rev.fa04e3f5)



================================================================================
* Tue Jan 08 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.044

================================================================================
	- spirouConst.py, spirouRecipe, spirouStartup2.py - move around the header --> into spirouConst.py (rev.e1484718)
	- spirouStartup2.py - add a check for special keys and do not display normal "splash" if found. (rev.96a1f93c)
	- spirouRecipe.py - update listing, add version/ epilog and other small fixes to input redo (rev.ccdb4455)
	- recipe_spirou.py - continued work on recipe definitions (including references to recipe_descriptions) (rev.f082a240)
	- recipe_descriptions.py - storage for longer text (allowing possibility of language support later) (rev.0f4e2956)
	- spirouConst.py - added constant to define the maximum display limit for files/directorys (when showing an argument error) (rev.5965c872)



================================================================================
* Wed Jan 09 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.045

================================================================================
	- test_recipe.py - test on cal_HC_E2DS_spirou.py (rev.d591a03f)
	- spirouStartup2.py - modified which argument display on setup (now only those that were entered at run time) (rev.a94817ef)
	- spirouRecipe.py - redone error reporting on header check (rev.ff59d702)
	- spirouFile.py - continued upgrade of input redo (rev.2dd622a2)
	- recipes_spirou.py - added cal_hc definition (rev.2c6a3786)
	- recipe_descriptions.py - added cal_hc text (rev.d8593b00)
	- files_spirou.py - updated names to better represent files (i.e. added fiber name) (rev.9587df1f)
	- spirouRecipe.py - make some methods/function private (protected) using the "_" character as a prefix (rev.90e54a96)
	- recipe_spirou.py - add more argument defintions (blazefile/flatfile/wavefile), add cal_hc test (rev.80656ee8)
	- recipe_descriptions - fix imports and define language in constants file (rev.3e425ad8)
	- spirouConst.py - add language constant (Not used yet) (rev.75e06155)
	- spirouStartup2.py - modify special_keys_present function to look at altnames as well as names (i.e. DrsArgument.names instead of DrsArgument.name) (rev.0f3632f6)
	- spirouRecipe.py - modify and add special actions (now: --help, --listing, --listall, --version, --info) (rev.25e99124)
	- recipe_spirou.py - convert remaining descriptions/help to recipe_descriptions calls (rev.2afa3003)
	- recipe_descriptions.py - continue to fill out recipe descriptions/examples/help (rev.38e52a4c)



================================================================================
* Fri Jan 11 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.046

================================================================================
	- recipe_spirou.py - change nomenclature require kwarg arguments have '-' optional have '--' (rev.6a637e7c)
	- test_recipe.py - change comment to make clearer (rev.5e5df0ed)
	- spirouStartup2.py - remove '-' in specials to allow them to work (rev.b2d77201)
	- spirouRecipe.py - modify _parse_args to take into that we don't wont the '-' (rev.844db5a7)
	- recipes_spirou.py - testing file list as keyword arguments (rev.0b969c17)
	- spirouStartup2.py - changed order of functions, modified display order, added functionality to deal with debug mode and other special keys (rev.b30581c0)
	- spirouRecipe.py - continued upgrade (changes to parser handling of special arguments, check files + added debug as special argument) (rev.3eefcff4)
	- spirouFile.py - small formatting changes in continued input redo (rev.3079218a)
	- recipe_spirou.py - remove references to debug (now a special command added to all recipes) (rev.a04b54bc)
	- recipe_descriptions.py - remove unused help (rev.8736b1f1)
	- files_spirou.py - modify names to better suit input redo (rev.bf493227)



================================================================================
* Tue Jan 15 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.047

================================================================================
	- drs_dependencies.py - remove looking in the /misc/ folder for dependecies/code stats (rev.a09b0775)
	- test_recipe.py - test self (rev.945e55d2)
	- test_processing.py - upgrade to allow execution of recipes (in single and in parallel) (rev.2541093b)
	- spirouStartup2.py - allow overwriting of drs_params when they are obtained via kwargs (get_params) (rev.c63aaa70)
	- spirouRecipe.py - continued upgrade of input_redo (rev.d2507112)
	- recipe_spirou.py - continued upgrade of input_redo (rev.12b806d2)



================================================================================
* Wed Jan 16 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.048

================================================================================
	- test_processing.py - for now comment out main call (while testing) (rev.74557987)
	- spirouRecipe.py - reformat help printing, add required option to optional arguments (for when we do not have positional arguments) and rework the generation of runs from files (especially when we only have optional arguments) (rev.362f4b5f)
	- recipe_spirou.py - add required keyword (for testing) (rev.642db992)
	- wavecomp.py - code to compare wavelength solutions (misc) (rev.07e8c980)



================================================================================
* Thu Jan 17 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.049

================================================================================
	- added additional file to INTROOT 2 (remanage) (rev.5cfcf287)
	- test_processing.py - remove need for replacing '.py' (rev.03381aa4)
	- recipes_spirou.py - added instrument name (will be needed in the future) (rev.33a4612d)
	- First draft of INTROOT remanage (rev.fcf45699)
	- test_processing.py - modify code to return errors and timings (via multiprocessing.Manager) (rev.61d7c188)
	- spirouRecipe.py - modified the generate_runs_from_filelist function to fix when there is no directory from pos args (rev.ddfca73b)
	- spirouFile.py - added read_header/read_data functions and optimized (with todo comment) the read function (rev.e8951db0)
	- wavecompy.py - added some comments (rev.08eec453)



================================================================================
* Fri Jan 18 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.050

================================================================================
	- move constants functions from package --> core (remove package module) (rev.a606489c)
	- add init file for drsmodule (to be named something else eventually) (rev.edea2e91)
	- add configuration.instruments.spirou files (rev.1a4f78a1)
	- remove the core.general package (rev.4967e1b2)
	- add init and README.md to constants module (rev.121428b2)
	- add a defaults folder (this has definitions of constants as well as default values) - sets up the classes for instruments to overwrite (rev.7ebaff0b)
	- remove the const package (now "constants") (rev.9461e6b7)
	- add a time module to the configurations.math module (rev.e8dd0fbf)
	- add a init file to configuration.instruments (rev.50f218a7)
	- add spirou config files to configuration.instruments (rev.eecd5d60)
	- add logging to configuration.core (rev.75421b2d)
	- add default user config files (will be commented out in future) (rev.50fd0090)
	- spirouRecipe.py - add "instrument" to attributes of spirouRecipe.py (rev.85fca8df)
	- files_spirou.py - modify name and description docstring (rev.0c5f7104)
	- spirouConst.py - fix a bug in exit definition (rev.b6301126)



================================================================================
* Sat Jan 19 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.051

================================================================================
	- add minor changes to drs_recipe.py and drs_startup.py (rev.e176d6f9)
	- add a test recipe to recipes.test (rev.e90921ca)
	- added a plot module (rev.70fbd9a7)
	- continued upgrade of constants.default packages (rev.0f6f012f)
	- added locale package (rev.350d93cb)
	- continued update of instruments.spirou defintions (rev.61648eae)
	- adding drs_recipe + drs_file  to configuration.core modules (rev.325d683f)



================================================================================
* Mon Jan 21 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.052

================================================================================
	- add source config file to error messages (rev.d5c69694)
	- fixed printing of config errors in constants file (rev.726b72bf)
	- added a test recipe for spirou and nirps (rev.85ac3b87)
	- added lock and table to drsmodule.io package (rev.bcc6d43e)
	- added "getmodnames" to drsmodule.constants.__init__ file (rev.6eee426b)
	- continued upgrade to drsmodule.constants.default (rev.8c367c6b)
	- continued upgrade to drsmodule.constants.core (rev.451bb678)
	- added __init__ file to drsmodule.configuration (rev.ccf965db)
	- continued upgrade to drsmodule.configuration.instruments.spirou (rev.4db609d2)
	- added a drsmodule.configuration.core.default folder (for default file/recipe descriptions) (rev.4c73e844)
	- continued upgrade to drsmodule.configuration.core (rev.b3f2aa1a)
	- default file definitions and recipe defintions (rev.8738adb3)
	- add test default config for NIRPS (rev.2ba6a20e)
	- add test user config for NIRPS (rev.ad9690e2)



================================================================================
* Tue Jan 22 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.053

================================================================================
	- added error.csv and "language.xls" - use language.xls to edit strings for each language (given a specific key) (rev.85d4786a)
	- default_config.py - updated options (now with ENG and FR allowed - ENG as default) (rev.8a7b2d8e)
	- updated help.csv (rev.be8bf5d0)
	- removed recipe_descriptions.py from config.locale.core (rev.6f51ef49)
	- drs_text.py - (formally text.py) - continued work on upgrade (rev.75ccf94c)
	- recipe_definitions.py - use HelpText to define strings (language support) (rev.afbd7bd3)
	- drs_recipe.py - COLOURED_LOG --> DRS_COLOURED_LOG (rev.48d544db)
	- drs_log.py - update WLOG to deal with ErrorEntry objects as WLOG messages (rev.765c4792)
	- use HelpText to define strings (language support) (rev.0c9b5067)
	- update user_config.ini file (rev.e36a5401)
	- update user_config.ini file (rev.087a331f)
	- add default help file (rev.453a377a)
	- change from ./configuration --> ./config (rev.3e440d27)
	- change from ./configuration --> ./config (rev.930fc62f)
	- added alias to new function "get_file_names" (rev.92f9b287)
	- adjusted path name ./configuration --> ./config (rev.75e59b4b)
	- started adding language support (rev.fb1ebd3e)
	- renamed drsmodule.configuration to drsmodule.config (rev.16c04265)



================================================================================
* Wed Jan 23 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.054

================================================================================
	- moved locale module to drsmodule root (rev.f19ce12e)
	- locale.databases - continued to add to databases (rev.7c38fed6)
	- locale.databases - continued to add to databases (rev.8455f896)
	- .gitignore - added ignoring of .npy files and .~lock files (rev.6eb39cbd)
	- constants.default.pseudo_const.py - added REPORT_KEYS method (rev.dba80713)
	- constants.core.param_functions.py - started added language / basic log functionality (rev.151c627c)
	- constants.core.constants_functions.py - added tracking of warnings (so they only print once) (rev.d05d7f47)
	- config.math.time.py - added get_hhmmss_now function (for log) (rev.401baf9a)
	- removed locale folder from config folder to separate sub-module directory (rev.e61148a2)
	- instruments.spirou.recipe_definitions.py - language implementation (rev.040afbe4)
	- instruments.nirps.recipe_definitions.py - language implementation (rev.048f4315)
	- instruments.nirps.pseudo_const.py - format change (rev.490419ee)
	- drs_startup.py - language implementation (rev.044cf22d)
	- drs_recipe.py - language implementation (rev.7e31512c)
	- drs_log.py - language implementation (rev.748baba8)



================================================================================
* Thu Jan 24 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.055

================================================================================
	- add READMEs to explain empty directories (rev.5ec89c61)
	- add instrument language packs and backup folder for language database (rev.32e3bf40)
	- drsmodule.locale - construct a readme (rev.78bb165d)
	- drsmodule.locale.__init__.py - add drs_exceptions to internal imported modules (rev.b48da1cc)
	- drsmodule.locale.databases - update language databases (rev.38e3acfc)
	- drmodule.locale.core - move exceptions and make sure all are using basiclogger (rev.35ee058b)
	- drsmodule.constants - update readme (rev.68022e5a)
	- constants.default - make Const and Keywords have a source argument (rev.645735a6)
	- constants.core - change how exceptions work and where they are sourced from (rev.34c3a6d4)
	- config.instruments.spirou - make copy have a source argument (rev.a0cd24ec)
	- config.instruments.nirps - make copy have a source argument (rev.bc34245e)
	- drs_setup.py - change how the exceptions work and where they are sourced from + continue to replace hard-coded text to text from database (rev.6fe070bf)
	- drs_recipe.py - carryon replacing text hard-coded to text in database (rev.070b2227)
	- drs_log.py - change how the exceptions work and where they are sourced from (rev.ae1cb733)



================================================================================
* Fri Jan 25 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.056

================================================================================
	- drs_startup.py - tweak the system information display section (rev.c23e087a)
	- drs_log.py - separate print and log (and use default language for log) (rev.a8097994)
	- backup language database (rev.aa4afc1e)
	- drs_text.py - fill language database empty with 'N/A' (rev.ca8a1a3a)
	- update language databases (rev.37699d7d)



================================================================================
* Sat Jan 26 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.057

================================================================================
	- modify test recipes with upgrades (rev.8ec9abd0)
	- drsmodule.plotting - moved from drsmodule.plot (rev.b1423ef7)
	- drsmodule.locale - continue upgrade (rev.0266c24e)
	- drsmodule.constants.io - continue upgrade (rev.07553f1c)
	- drsmodule.constants.default - continue upgrade (rev.973ae969)
	- drsmodule.constants.core - continue upgrade (rev.f081ad66)
	- drsmodule.config.instruments - continue upgrade (rev.953ab831)
	- drsmodule.config.core - continue upgrade (rev.e53ddab4)
	- update DRS_VERSION / DRS_DATE / DRS_RELEASE (rev.2372d3d1)
	- update user_config.ini (rev.160b5031)
	- update user_config.ini (rev.26c623ff)



================================================================================
* Mon Jan 28 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.058

================================================================================
	- upgrade of language database (rev.fa782712)
	- drs_lock.py - continued upgrade of error entry (rev.c7e7d73f)
	- drs_recipe.py - continued upgrade of error entry (rev.67d6bcdf)
	- drs_log.py - continued upgrade of error entry (rev.5d057a13)
	- drs_file.py - continued upgrade of error entry (rev.82c9f9fd)
	- drs_log.py - fix bug in log and how exceptions are handled (rev.78e24f8f)



================================================================================
* Wed Jan 30 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.059

================================================================================
	- obj_mk_tellu_new.py - update code with Etienne's changes (rev.a915f5c4)



================================================================================
* Thu Jan 31 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.060

================================================================================
	- update langauge databases (rev.ae728cef)
	- drs_file.py - continue to take out error messages (rev.2fb93ed7)
	- recipe_definitions.py - update location of locale module (rev.ee3f31fa)
	- extract_trigger.py - add obj_mk_tellu_db to triggered files (rev.1606a887)
	- unit test runs - add obj_mk_tellu_db to runs (rev.1c3042ef)
	- spirouTelluric.py - fix bugs after moving functions here (rev.f550fe3c)
	- code to check the calibdb entries vs files (rev.43d89e34)
	- add obj_mk_tellu_db to list of available unit tests (rev.76ea9e69)



================================================================================
* Fri Feb 01 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.061

================================================================================
	- update language database (rev.fa862edf)
	- drs_file.py - continue taking out error messages (rev.0af7c60d)
	- add wiki plots (rev.7d835ac5)
	- spirouWAVE.py - fix a deprecated WLOG message (found by Melissa) (rev.3e3f27f5)
	- spirouLog.py - must catch WLOG error before trying to do anything with p (rev.3c8195f4)
	- update langauge databases (rev.275caec3)
	- drs_file.py - continued error movement to database (rev.cfdf3c21)



================================================================================
* Sun Feb 03 2019 njcuk9999 <neil.james.cook@gmail.com> - 0.4.062

================================================================================
	- port_database.py - just try to open csv files as they are done in the drs -- hits problems here and not later. (rev.0bca614c)
	- drs_text.py - edit the way csv databases are loaded (to avoid encoding errors) (rev.7c615bbb)
	- drs_exceptions.py - add errorobj as possible input to exceptions (and exctract message/level accordingly) (rev.ef5e73d8)
	- update language database (rev.a0792061)
	- drs_recipe.py - continue moving errors to database (rev.44aefd55)
	- drs_log.py - continue moving errors to database (rev.c0142aa0)
	- drs_file.py - continue moving errors to database (rev.26579be9)



================================================================================
* Mon Feb 04 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.063

================================================================================
	- obj_mk_tellu_db.py - do not reset tellu db in code (do it manually before) (rev.a399ae51)
	- update extract_trigger.py for obj_mk_tellu_db.py (rev.1b841532)



================================================================================
* Tue Feb 05 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.064

================================================================================
	- drs_startup.py - tweak display settings for interactive + debug mode in drs setup text (rev.b39b2b79)
	- update language database (rev.a3718432)
	- drs_text.py - tweak short codes and how length works with Entry(None) (rev.716adbc5)
	- drs_exceptions.py - tweak how exception work (and add string representation) (rev.b0714b4e)
	- update language database (rev.31914af3)
	- pseudo_const.py - do not automatically write debug message language codes (only when debug >= 100) (rev.744115cc)
	- drs_startup.py - continue editing how errors work (rev.76a79fe4)
	- drs_recipe.py - continue update to errors (rev.f7d3dcf3)
	- drs_log.py - do not use 'p' use params, update reporting (report all if debug >= 100) (rev.61a46992)
	- drs_file.py - add extra param (pep8) (rev.d0e807fa)
	- drs_argument.py - redo DrsArgument.exception and update _display_info (rev.8f359c9d)
	- update extract_trigger settings (rev.ecdf66fb)
	- update telluric white/black lists (rev.0ee9deee)
	- extract_trigger.py - add a comment (rev.0407e262)
	- check_calibdb_2.py - check calibdb and sort and make "pernight" and "pertc" calibdb entries (rev.4cd14320)
	- spirouTelluric.__init__.py - Add aliases to blacklist and whitelist functions (rev.b72a0555)
	- extract_trigger.py - get whitelist from file (rev.fed03813)
	- drs_text.py - expand functionality of Entry classes (__add__, __radd__, __len__, __iter__, __next__, __eq__, __ne__, __contains__) and how .get() works (rev.d48042c9)
	- drs_exception.py - add ArgumentException/Error/Warning (rev.a2500052)
	- update language database (rev.afe7795a)
	- param_functions.py - get ArgumentError/Warning (rev.a3b7fdbc)
	- drs_startup.py - deal with changes to ErrorEntry (no "\n" automatically added now) (rev.c508a300)
	- drs_recipe.py - move argument classes/functions to separate script + continue string moving to language database (rev.4370a5b4)
	- drs_loy.py - add comment that some strings cannot be moved to language database (rev.3d4cae0e)
	- drs_argument.py - move argument classes/function to separate script (rev.d46bf1b9)



================================================================================
* Wed Feb 06 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.065

================================================================================
	- add a note to locale README.md (rev.ef2382f3)
	- update language database (rev.6b4ca4eb)
	- drs_table.py - remove text to language database (rev.6cf1d294)
	- check_objname.py - pep9 remove blank lines (rev.991a2eff)
	- check_objname.py - check objnames and dprtype for preprocessed files in a given directory (rev.5274e889)



================================================================================
* Thu Feb 07 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.066

================================================================================
	- update the leapseconds (rev.cf112d94)
	- check_for_corrupt_files.py - worker code to check corrupt files functionality (before implementing into preprocessing) (rev.7a90d0fa)
	- update to only do mk_tellu and fit_tellu (rev.f694983b)
	- add  / get functions for recon file (rev.02d7e6dc)
	- constants_SPIROU_H4RG.py - qc snr for mk_tellu and fit_tellu (rev.4784756d)
	- obj_mk_tellu_*.py - distinguish between SNR cut in fit_tellu and mk_tellu (rev.8a126a5d)
	- obj_fit_tellu.py - add qc of SNR > 100 for order 33 (rev.73616172)



================================================================================
* Fri Feb 08 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.067

================================================================================
	- cal_preprocess_spirou.py - print out the corruption check value (rev.b2815339)
	- cal_preprocess_spirou.py - print out the corruption check value (rev.64c27725)
	- cal_preprocess_spirou.py - better message for corrupt file (rev.cf34eed2)
	- cal_preprocess_spirou.py - better message for corrupt file (rev.b29be8c3)
	- spirouImage.py - catch warning "RuntimeWarning: All-NaN slice encountered r = func(a, **kwargs)" (rev.f40d210c)
	- cal_preprocess_spirou.py - pep8 tidy up of QC (rev.f9712c6b)
	- spirouImage.py - add get_full_flat, get_hot_pixels, test_for_corrupt_files functions (for checking corruption in preprocessing) (rev.379965fd)
	- constants_SPIROU_H4RG.py - add corrupt file constants (rev.cab77758)
	- cal_preprocess_spirou.py - add QC for corrupt files (rev.47cf0fc0)
	- extract_trigger.py - update conditions for mk_tellu and fit_tellu (rev.ddc9c17c)
	- extract_trigger.py - update conditions for mk_tellu and fit_tellu (rev.14ae05eb)
	- obj_mk_obj_template.py - make sure BigCube table in both BigCube and BigCube0 (rev.32a320fd)
	- obj_mk_obj_tempalte.py - fit BADFILE --> BADPFILE keyword (rev.032fbd99)
	- spirouKeywords.py - update KW_OBJECT (was a typo) (rev.7e9d03ec)
	- obj_mk_obj_template.py - add the data type to ReadParams (otherwise tries to make them floats) (rev.78b3eec2)
	- spirouImage.py - deal with keylook up and report better error (via keylookup) (rev.fa45fbf7)
	- obj_mk_obj_template.py - fix another typo since last update (rev.8cffb4d2)
	- spirouKeywords.py - add keyword KW_OBJECT (rev.9975a69d)
	- obj_mk_obj_template.py - fix type in previous changes (rev.b95ab156)
	- check_for_corrupt_files.py - add an extra fix from Etienne (rev.5fed5537)
	- obj_mk_tellu_db.py - fix typo in printout text (rev.511cc553)
	- obj_mk_obj_template.py - correct mistake in calling ReadParams (from most recent edit) (rev.6c3f8da6)
	- spirouTelluric.py - add a function to construct the big cube table (added as a second import to BigCube) (rev.cc4853da)
	- spirouFITS.py - add a write_image_table function to write a image and a table to single fits file (rev.35a75c3d)
	- check_for_corrupt_files.py - adjust with Etiennes changes (rev.a7f28900)
	- obj_mk_obj_template.py - add fits table to big table with rows of file parameters (used in the big cube) (rev.15d6066c)
	- check_for_corrupt_files.py - fix bugs in the test (rev.61bd8aee)



================================================================================
* Sun Feb 10 2019 njcuk9999 <neil.james.cook@gmail.com> - 0.4.068

================================================================================
	- spirouPlot.py - make sure plots are unique (rev.93c76653)
	- cal_DRIFTPEAK_E2DS_spirou.py - modifications to plotting changes (rev.34f80d06)
	- drs_reset.py - add option to reset plot folder (rev.783ee9f9)
	- spirouStartup.py - deal with getting / setting / displaying plot level (rev.e7a88346)
	- spirouPlot.py - add all functionality to support plotting to file (rev.32882709)
	- spirouConst.py - add plot extensions and plot figsize to constants (for saving plots to file) (rev.dfbfc1d0)
	- spirou modules - make all plot calls compatible with saving to file (rev.3e91d6dd)
	- misc - make all plot calls compatible with saving to file (rev.f7219742)
	- config.py - make DRS_PLOT an int and change description of DRS_INTERACTIVE (rev.abc6b885)
	- bin folder - modify all calls to plot to allow saving to file (all calls require "p" as an argument) (rev.381ec23b)
	- DRS startup - need to make data/msg etc folders if they don't exist (rev.42e741a5)



================================================================================
* Mon Feb 11 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.069

================================================================================
	- cal_WAVE_E2DS_EA_spirou.py - Big Bug FIX ASAP (rev.119da91c)
	- spirouPlot.py - update wave_ea_plot_line_profiles fig size (rev.77f12b98)
	- spirouImage.py - pep8 correction to corruption test (rev.25bcc9fc)
	- constants_SPIROU_H4RG.py - add second criteria for corrupt files (rev.47bf14e1)
	- cal_preprocess_spirou.py - update corruption tests (rev.54c60beb)
	- spirouImage.py - adjust rms values (scaled by percentile) (rev.25c438b7)
	- cal_preprocess_spirou.py - move qc cuts to main code (from function) (rev.cdf10d85)
	- spirouImage.py - update corruption test (rev.b52d2b6d)
	- spirouPlot.py - update some plot parameters (rev.691a3816)
	- spirouPlot.py - enforce a default fig size on all plots + only save in png and pdf (rev.a337b9a0)



================================================================================
* Tue Feb 12 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.070

================================================================================
	- spirouFITS.py - add UpdateWaveSolution (update_wave_sol) function to update correctly the HC and FP files (rev.8bbe960e)
	- obj_mk_obj_template.py - add criteria to check median SNR and remove any below half the median SNR (in specific order) (rev.82fcbb24)
	- cal_WAVE_E2DS_EA_spirou.py - BUG FIX - hc and fp files have wrong headers when updating wave solution (rev.ed799395)



================================================================================
* Tue Feb 12 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.071

================================================================================
	- extract_trigger.py - make sure obj_fit_tellu errors are stored (rev.5ed03775)
	- obj_mk_tellu_db.py - keep track of errors and exceptions - only print at end (rev.c2c48b49)
	- obj_mk_obj_template.py - fix bug when filtering by snr (all columns of fits table must be same length) (rev.cbca77bf)
	- spirouPlot.py - fix bug with HC plot (from added save of plotting) (rev.ab6b441c)
	- cal_preprocess_spirou.py - remove rms printout and add values to QC errors (rev.c487d26f)
	- spirouPlot.py - deal with TclError (with new call for setup_figure) (rev.b8bdf43a)
	- cal_loc_RAW_spirou.py - add p to call to plotting function (rev.e3bc8f29)
	- spirouPlot.py - modify figure setup to try to catch TclError's and deal with them (rev.8a9f1c04)
	- extract_trigger.py - modify printing to logfile (print input args) (rev.242eebd8)
	- obj_mk_obj_template.py - change number of tell files to info (rev.a712a1fe)
	- obj_mk_obj_template.py - fix typo in new snr constraint (rev.74490cf9)
	- obj_mk_obj_template.py - fix typo in new snr constraint (rev.735787fe)
	- obj_mk_obj_template.py - fix typo in new snr constraint (rev.685ec40c)
	- obj_mk_obj_template.py - fix typo in new snr constraint (rev.02348eed)



================================================================================
* Wed Feb 13 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.072

================================================================================
	- obj_mk_tellu_db.py - need to only print errors if we have errors (rev.d32c97ac)
	- obj_mk_tellu_db.py - need to only print errors if we have errors (rev.3660e5f3)



================================================================================
* Tue Feb 19 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.073

================================================================================
	- cal_validate_spirou.py - fix bug it version checking (found by Melissa) (rev.ca1317e4)
	- cal_validate_spirou.py - fix bug it version checking (found by Melissa) (rev.7d7e7303)
	- spirouWAVE.py - add some more comments for resolution map (rev.9584f094)



================================================================================
* Tue Feb 19 2019 njcuk9999 <neil.james.cook@gmail.com> - 0.4.074

================================================================================
	- spirouTelluric.py - remove hard coded number of orders (rev.a02420a2)
	- obj_mk_tellu_new.py - comment out unused lines (rev.303cf104)



================================================================================
* Thu Feb 21 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.075

================================================================================
	- spirouTelluric.py - need to stop if not index files found. (rev.001427b9)



================================================================================
* Fri Feb 22 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.076

================================================================================
	- spirouLOCOR.py - fix problem with locplot_im_sat_threshold plot (rev.453cba5a)
	- spirouPlot.py - fix problem with locplot_im_sat_threshold plot (rev.c19a3234)
	- cal_loc_RAW_spirou.py - fix problem with locplot_im_sat_threshold plot (rev.95c074af)



================================================================================
* Fri Feb 01 2019 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.4.077

================================================================================
	- cal_WAVE_NEW_E2DS attempt to fix issues with FP line adjacent to reference peak being missing (rev.18f961ac)



================================================================================
* Mon Feb 04 2019 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.4.078

================================================================================
	- cal_WAVE_NEW update: no longer breaks if FP peak(s) next to reference line are missing (rev.0b7b871a)



================================================================================
* Wed Feb 06 2019 melissa-hobson <melihobson@gmail.com> - 0.4.079

================================================================================
	- cal_WAVE_NEW corrected Littrow extrapolation for reddest orders (rev.4daacbf8)



================================================================================
* Mon Feb 18 2019 melissa-hobson <melihobson@gmail.com> - 0.4.080

================================================================================
	- testing linear minimization FP wave sol fitting (rev.02ccd126)
	- Tests: (rev.305f5953)



================================================================================
* Fri Feb 22 2019 melissa-hobson <melihobson@gmail.com> - 0.4.081

================================================================================
	- Littrow check plot: ylimits added based on QCs and results (rev.8a956cbf)
	- cal_WAVE_NEW gets HC catalog lines correctly (rev.4c973507)
	- Correct error estimation for cal_WAVE_NEW (rev.7224eee4)



================================================================================
* Fri Feb 22 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.082

================================================================================
	- spirouPlot.py - fix problem with locplot_im_sat_threshold plot (rev.c19a3234)



================================================================================
* Thu Feb 28 2019 melissa-hobson <melihobson@gmail.com> - 0.4.083

================================================================================
	- sPlt.debug_locplot_finding_orders pauses correctly after each plot; plot limit modified to improve visualization (rev.8e5a38f1)
	- spirouBACK.measure_background_and_get_central_pixels: removed duplicate call to locplot_y_miny_maxy (rev.dfa22338)



================================================================================
* Tue Mar 05 2019 melissa-hobson <34136975+melissa-hobson@users.noreply.github.com> - 0.4.084

================================================================================
	- Delete wave_comp_night.py (rev.38956fb4)
	- Update cal_WAVE_E2DS_EA_spirou.py (rev.107a8ecd)



================================================================================
* Thu Mar 07 2019 Chris Usher <usher@cfht.hawaii.edu> - 0.4.085

================================================================================
	- Fixed lock timer bug and added barycorr retry. (rev.ab1a1c52)



================================================================================
* Fri Mar 08 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.086

================================================================================
	- spirouBERV.py - add BERVHOUR to loc (for saving to header) (rev.b4c5b61a)
	- cal_WAVE_E2DS_EA_spirou.py - add some more TODO's for sections that need work (rev.5399c3ec)
	- cal_HC - allow multiple files (need to update all files + add files to header) (rev.731fea36)
	- add WMEANREF for AB and C to header (rev.a666d9cc)
	- Add PID to output header files (so one can find the log file for each) (rev.0a020843)
	- add Quality control header keys QC, QCV# (value), QCN# (name), QCL# (name) - and make sure these are not copied over from inputs + some pep8 fixes (rev.d790e772)
	- spirouWAVE.py - clean up the code (pep8) (rev.dac36aa7)
	- spirouFITS.py - clean up the code (pep8) (rev.c442a186)
	- spirouBERV.py - clean up the code (pep8) (rev.f96688ba)
	- spirouPlot.py - clean up the code (pep8) (rev.e46aadd7)
	- spirouConst.py - clean up the code (pep8) (rev.0ad1cace)
	- cal_WAVE_NEW_E2DS_spirou.py - clean up the code (pep8) (rev.f581044f)
	- cal_WAVE_E2DS_EA_spirou.py - clean up the code (pep8) (rev.1871d48a)



================================================================================
* Fri Mar 08 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.087

================================================================================
	- change AddKey --> AddKey1DList for QC names/values/logic (rev.2779756d)
	- cal_preprocess_spirou.py - correct qc missing from param dict (rev.f6350eae)
	- spirouKeywords.py - fix missed comma in list (rev.1e560b5d)
	- spirouBERV.py - add BERVHOUR to loc (for saving to header) (rev.5889e099)



================================================================================
* Sat Mar 09 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.088

================================================================================
	- spirouLSD.py - fix str to float bug (rev.47c737e1)
	- test.run - update (rev.e6a5ff61)
	- spirouPOLAR.py - fix string - float bug (rev.25c93982)
	- spirouTelluric.py -fix berv from string (rev.8cc9bd56)
	- spirouRV - must have finite BERV value -- but should this be set to zero? (rev.5b198830)
	- spirouFITS.py - undo hdr type fix (rev.c7d80525)
	- update test.run (rev.a0c6b145)
	- spirouBERV.py - correct strings coming from header (BERV, BJD, BERV_MAX) (rev.c82c63fc)
	- update test.run (rev.f7fe23fe)
	- update test.run (rev.64e18fef)
	- spirouLOCOR.py - fix bug with strings not being ints (rev.41d35468)
	- spirouFITS.py - fix problem with changing output type (should not change) (rev.c77c8d52)
	- cal_HC_E2DS_EA_spirou.py - fix typo in updatewavesolution (rev.2d3d9ddb)
	- spirouWAVE.py - fix typo in new masknaems ordermask-->omask (rev.0aff80d2)
	- spirouFITS.py - fix values now as strings --> cast to ints/floats (rev.e28efc01)
	- fix problem with mjd being a string (rev.c3423e5c)
	- fix problem with mjd being a string (rev.f75eed46)
	- spirouFITS.py - allow NaNs into header by converting to string (rev.72b933e4)
	- spirouFITS.py - allow NaNs into header by converting to string (rev.8dca2b0f)
	- spirouFITS.py - allow NaNs into header by converting to string (rev.bbb01dc1)
	- spirouFITS.py - allow NaNs into header by converting to string (rev.6cba9ab1)
	- spirouFITS.py - allow NaNs into header by converting to string (rev.d59e064f)
	- spirouBERV.py - fix bug when we don't need a BERV still need BERVHOUR in loc (rev.86857d11)
	- cal_extract_RAW_spirou.py - fix typo BCHOUR --> BERVHOUR (rev.a874dd5d)
	- cal_loc_RAW_spirou.py - fix mistake in assigned QCV value (rev.b9995e6e)
	- cal_loc_RAW_spirou.py - fix mistake in assigned QCV value (rev.e647b41e)



================================================================================
* Mon Mar 11 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.089

================================================================================
	- extract_trigger.py - update the settings ready for re-runs of extractions (rev.28834c48)
	- spirouStartup.py - fix where we lock the index file (rev.0a006234)
	- spirouConst.py - add an INDEX_LOCK_FILENAME to lock the indexing in parallel processes (rev.eac02bc2)
	- tellu_file_number_test.py - code to test the number of telluric files at difference stages of the DRS (rev.1a8a0367)



================================================================================
* Tue Mar 12 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.090

================================================================================
	- update extraction trigger (rev.763ea897)
	- spirouPOLAR.py - add qc_pass (rev.56cca973)
	- spirouFITS.py - add a test for formatting defined in the keyword (for 1d and 2d lists only) (rev.6e56e7eb)
	- spirouKeywords.py - add KW_DRS_QC_PASS + change position of number in QCV, QCN, QCL (rev.f45436bc)
	- spirouConst.py - change the qc_keys to look for (rev.d93a8bda)
	- add qc_pass parameter (flag for each qc parameter) (rev.2b58ebef)
	- spirouConst.py - add version to the index files (rev.1aa7f1d5)
	- drs_reset.py - set DEBUG = False in reset, add the removal of all sub-directories in drs folders (rev.af356c7e)
	- spirouStartup.py - fix bug that we only need lock file is outputs is not None (rev.d18f1f5f)
	- cal_WAVE_E2DS_EA_spirou.py - fix bug with new qc_pass criteria (rev.521f5cd2)
	- unit_test.py - update logging (log all) (rev.6ae3a4a4)
	- spirouFITS.py - add function "add_qc_keys" to take the keys and push them into hdict correctly (rev.a258d4e8)
	- spirouConst.py - change PPVERSION to VERSION for reduced index.fits (rev.d89fba5f)
	- update QC parameters (to store in order) (rev.37297739)



================================================================================
* Wed Mar 13 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.091

================================================================================
	- cal_DARK_spirou.py and spirouImage.py - tweak changes to all SKYDARK files to be used (rev.1fe57a62)
	- extract_trigger.py - readd the "skip" criteria (rev.ff472dc8)
	- drs_reset.py - skip the log file for this instance of drs_reset (otherwise can get stuck) (rev.832ad004)
	- drs_reset.py - fix removal of files when in dir (if still present) (rev.2a805a48)
	- cal_CCF_E2DS_FP_spirou.py - correct bad qc parameters (rev.e29e0443)
	- obj_mk_tellu_new.py - fix typo in qc parameters (rev.55ffa7a1)
	- obj_mk_tellu_new.py - fix typo in qc parameters (rev.47af75b4)
	- drs_reset.py - fix typo in reset1 (rev.edac07fe)
	- cal_WAVE_E2DS_EA_spirou.py - fix bug with new qc_pass criteria (rev.34426d43)



================================================================================
* Thu Mar 14 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.092

================================================================================
	- make sure all input files are added to header in form: INF#### where the first digit shows the file-set and the other three the position i.e. for recipe.py night_name file1 file2 file3 file4   where inputs expected are 1 flat and multiple darks header would add INF1001 INF2001 INF2002 INF2003 (rev.d3f996dc)
	- add header keys for calibration files used to create outputs (CDBDARK, CDBWAVE) etc, also add a source for the wave solution (WAVELOC) (rev.9fba0e20)
	- spirouImage.py - correct the rms percentile to allow more darks to pass the rms test (rev.0381146a)



================================================================================
* Thu Mar 14 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.093

================================================================================
	- cal_preprocess_spirou.py - fix filename (should only be filename not path) (rev.620efd9d)
	- cal_CCF_E2DS_FP_spirou.py - plot duplicate plot correctly (rev.63c92fed)
	- cal_CCF_E2DS_FP_spirou.py - correct typo in WMREF (rev.e0e763a7)
	- cal_CCF_E2DS_FP_spirou.py - correct typo in WSOURCE (was WAVESOURCE) (rev.909dc99f)
	- spirouConst.py - correct typo (rev.fcefe5c6)


================================================================================
* Fri Mar 15 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.094

================================================================================
	- spirouConst.py - remove DRS_EOUT from forbidden keys (it should follow extracted file) (rev.ba801cd7)
	- calc_berv.py - make sure CopyOriginalKeys comes first before other calls to hdict (rev.0625e99b)
	- spirouFITS.py - change QC_HEADER_KEYS to FORBIDDEN_HEADER_PREFIXES (rev.8085cbf8)
	- spirouKeywords.py - change some keyword to make them unique (thus can remove them) (rev.59f3109d)
	- spirouConst.py - add more forbidden keys, change qc_keys to any prefix that shouldn't be copied (rev.fb0d10f5)
	- obj_fit_tellu.py - CopyOriginalKeys should be called before other hdict commands (rev.a768c9cd)
	- update unit test scripts (rev.bf1de7ab)
	- spirouRV.py - fix problem with getting C file from header (rev.17480abb)
	- spirouConst.py - add CCF_FP_TABLE1 and 2 (rev.6d270c7f)
	- recipe_control.txt - do not allow OBJ_DARK files - only OBJ_FP (rev.4ca8cb1a)
	- cal_CCF_E2DS_FP_spirou.py - add a C table as well as a fits table (rev.6e0579d8)
	- extract_trigger.py - update settings (rev.82798761)
	- spirouKeywords.py - remove unused keywords (rev.9cc7ca2f)
	- spirouConst.py - add AB and C files for CCF_FP (rev.60c313f4)
	- tellu_file_number_test.py - change path (for new test) (rev.621de6f5)
	- cal_CCF_E2DS_FP_spirou.py - separate AB and C files for output (rev.813625d0)
	- spirouTelluric.py - fix list of col names for bigcube (only one bad file now) (rev.96e549c9)
	- extract_trigger - update trigger (rev.117673b1)
	- spirouLOCOR.py - fix localisation error - should be a median not an average (option was there but not used) (rev.7464c1e4)
	- spirouFITS.py - remove a HUGE BUG - eval('2018-08-05') --> 2005 (as date is interpreted as a subtraction)!!!!! (rev.e533163b)
	- tellu_file_number_test.py - add raw files and disk vs index.fits (rev.bce0e178)
	- log_analyser.py - code to look for errors in set of log files (rev.821b1ebe)
	- cal_DRIFT_E2DS_spirou.py - fix typo in get wave sol return (rev.fa6c4785)
	- cal_SHAPE_spirou.py - fix typo in cdbbad value name (rev.9bc7859d)
	- cal_SHAPE_spirou.py - fix typo in cdbbad value name (rev.222e87b7)
	- fix the references to old values of fp_rv (rev.6dbbbfa6)



================================================================================
* Sat Mar 16 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.095

================================================================================
	- obj_mk_obj_template.py - copy all cdb from other outputs (rev.2c483b8f)
	- spirouFITS.py - separate forbidden keys into absolutely don't copy and drs don't copy (that will be copied for updating current files) (rev.84be29d0)
	- spirouFITS.py - separate forbidden keys into absolutely don't copy and drs don't copy (that will be copied for updating current files) (rev.de935715)
	- spirouFITS.py - need to copy all keys when updating wave solutions (rev.df0b6c6e)
	- spirouTelluric.py - remove extract_file (rev.e59e0afd)



================================================================================
* Mon Mar 18 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.096

================================================================================
	- tellu_file_number_test.py - update the paths (rev.3982f42a)
	- spirouConst.py - fix bug with INDEX_LOCK_FILENAME - must not use PID (must be unique to night name not individual process otherwise does not lock out other pids) (rev.d6e13fb9)
	- update extract_trigger.py (rev.f26f399c)
	- spirouFITS.py - fix bug with index lock file (when path does not exist) (rev.ee68d005)
	- spirouFITS.py - add lock file descriptions for print message (rev.dc458462)
	- spirouStartup.py - allow main_end script to be used not at the end (rev.d132fa34)
	- spirouFITS.py - modify open/close lock file functions (rev.e9fb369c)
	- constants_SPIROU_H4RG.py - reduced max db wait time to 10 minutes (rev.3515ae02)
	- cal_preprocess_spirou.py - index files separately (rev.28a827e1)
	- update extract_trigger to be able to extract darks (rev.f222d270)
	- update notes (rev.4610f30f)
	- spirouImage.py - re-add skydark in (rev.e5b06274)
	- constants_SPIROU_H4RG.py - add option to switch between SKYDARK only and "DARK or SKYDARK" (depending which is closest) (rev.6638b8a9)
	- spirouImage.py - correct bug in sky dark (rev.53d4eac3)
	- update extract_trigger.py (rev.0b4bfaa2)



================================================================================
* Tue Mar 19 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.097

================================================================================
	- spirouKeywords.py - remove the "1" suffix (no longer needed) (rev.2d4f930d)
	- spirouEXTOR.py - set up two new extract functions to test adding of fractional contributions of pixels (rev.d2f21687)
	- update test.run (rev.7abbaf91)
	- update test.run (rev.6229328d)



================================================================================
* Tue Mar 19 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.098

================================================================================
	- cal_extract_RAW_spirou.py - fix problem with width getting for fiber A (rev.e4d3c17c)
	- extract_test_5a_5b.py - want a and b and c separately (rev.f8009c5d)
	- cal_extract_RAW_spirou.py - fix bug in width getting (rev.c7164ce8)
	- spirouLOCOR.py - add function required to get AB + C fiber coefficients when needed (rev.c55d47a7)
	- spirouEXTOR.py - add changes required for extract mode 5a/5b (rev.b01c9f4e)
	- test of extract mode 5a/5b (rev.9c624d41)
	- cal_extract_RAW_spirou.py - add code required for mode 5a/5b (rev.a88a4006)



================================================================================
* Wed Mar 20 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.099

================================================================================
	- tellu_file_number_test.py - distinguish between TELL_OBJ and TELL_MAP in counting from telluDB (rev.dfbf14f0)



================================================================================
* Fri Mar 22 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.100

================================================================================
	- spirouLOCOR.py - add get_fiber_data function and get_straightened_orderprofile function (rev.a286e062)
	- spirouEXTOR.py - fix bug in modes which don't use pos_a (rev.20e0b56b)
	- spirouImage (spirouFile/spirouFITS/spirouImage) - add changes for new extraction mode (rev.14178fad)
	- spirouEXTOR.py - add etienne's changes to debananafication (rev.496f043d)
	- spirouPlot.py - add ext_debanana_plot to show straightened image (rev.d2caf1e4)
	- spirouConfig.py - fix ParamDict copy function (rev.3671881b)
	- constants_SPIROU_H4RG.py - change mode to '5b' and '5a' (rev.32ece65b)
	- cal_extract_RAW_spirou.py - add changes to all modes '5a' and '5b' to work (rev.68b3b23d)
	- qc_examples.py - add code to document qc parameters for each output in reduced (rev.18736be1)



================================================================================
* Mon Mar 25 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.101

================================================================================
	- spirouPlot.py - add the debanana plot in (rev.83c3d1a7)
	- misc/new_plot_test.py - test of plotting fixes (rev.01162668)
	- spirouEXTOR.py - do not round in dy statement (rev.235773e2)



================================================================================
* Thu Mar 28 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.102

================================================================================
	- cal_extract_RAW_spirou.py - turn off ic_extract debug (rev.a83e1626)



================================================================================
* Tue Mar 12 2019 melissa-hobson <melihobson@gmail.com> - 0.4.103

================================================================================
	- Updates to cal_WAVE_NEW_2 (rev.6dc053d7)



================================================================================
* Thu Mar 28 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.104

================================================================================
	- fix bug in extraction modes for cal_exposure_meter and cal_wave_mapper (rev.40bcfdb7)
	- cal_FF_RAW_spirou.py - missed the debananafication (rev.8a5443f1)
	- cal_extract/cal_ff - fix mode extract_shape/ll (rev.20b448ec)
	- cal_extract/cal_FF - fix mode selection (rev.07a07e3c)
	- spirouImage.py - DeBananafication needs ParamDict in function call (rev.9ba58e8e)
	- make_1ds_etienne_new.py - new s1d code to integrate into the drs (rev.01a5986a)
	- spirouImage.py - fix for use of DeBananafication since change to function (for cal_SHAPE here) (rev.5bea07c1)
	- update date/version/changelog/update_notes (rev.eb1d8e49)



================================================================================
* Thu Mar 28 2019 melissa-hobson <melihobson@gmail.com> - 0.4.105

================================================================================
	- cal_HC_E2DS_EA: log statistics (rev.a46a488a)



================================================================================
* Fri Mar 29 2019 melissa-hobson <melihobson@gmail.com> - 0.4.106

================================================================================
	- github backup before merging with master (rev.2a68e6bc)
	- cal_WAVE_NEW improved cross-order matching (rev.a7e105c4)



================================================================================
* Tue Apr 02 2019 melissa-hobson <melihobson@gmail.com> - 0.4.107

================================================================================
	- cal_WAVE_NEW: modified FP CCF keywords spirouKeywords: added unique WFP keywords for wave FP CCF keys (rev.fa90a6f3)
	- config save (rev.d399b296)



================================================================================
* Wed Apr 03 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.108

================================================================================
	- spirouPlot.py - allow all orders to be plot in tellu plot (rev.f4e1ad05)



================================================================================
* Wed Apr 03 2019 njcuk9999 <neil.james.cook@gmail.com> - 0.4.109

================================================================================
	- update test.run (rev.ca1d8ed7)
	- spirouWAVE.py - comment out non-used line (rev.841eed05)
	- SpirouDrs.data - undo changes from Melissa Branch (rev.c67bc842)
	- config.py - undo changes from Melissa Branch (rev.361992ec)
	- cal_WAVE_E2DS_EA_spirou.py - undo changes from Melissa branch (rev.2bb8c07b)
	- cal_extract_RAW_spirou.py - add WFP keys to cal extract and deal with not having values (rev.891de849)
	- cal_extract_RAW_spirou.py - add WFP keys to cal extract (rev.e03fd069)
	- cal_CCF_E2DS_FP_spirou.py - replace manual call to filename (rev.554a4507)
	- spirouEXTOR.py - fix normalisation of spelong (E2DSLL) (rev.0adadff5)



================================================================================
* Wed Apr 03 2019 melissa-hobson <melihobson@gmail.com> - 0.4.110

================================================================================
	- cal_WAVE_NEW: fixes to m(x) residuals plot (rev.3b063b05)
	- cal_CCF_E2DS_FP: keeps base name only for WFP file (rev.50e03788)
	- cal_WAVE_E2DS_EA: save wave FP CCF keys (rev.961be7fc)
	- cal_WAVE_NEW: save wave FP CCF target RV and width (rev.1b963f91)
	- cal_CCF_E2DS_FP: writes WFP keys to CCF headers properly (rev.8de078ff)
	- cal_CCF_E2DS_FP: read correct keyword for drift (rev.b1749985)
	- cal_CCF_E2DS_FP: reads correct keyword for wave sol drift, writes WFP keys to CCF headers (rev.55c0e408)
	- spirouKeywords: add wave FP CCF keys to list (rev.ca49bcc0)



================================================================================
* Thu Apr 04 2019 njcuk9999 <neil.james.cook@gmail.com> - 0.4.111

================================================================================
	- cal_SHAPE_spirou.py - fix typo in output filenames (only affected debug outputs) (rev.c5b69f3a)
	- cal_CCF_wrap_MH.py - fix typo in return table values 'cloc' --> 'loc' (rev.db5ae6f1)
	- cal_CCF_wrap_MH.py - call from command line was missing (rev.673c40db)
	- cal_CCF_wrapper changes for Melissa (temporary addition of cal_CCF_E2DS_FP_MH_spirou.py) (rev.6436fcce)



================================================================================
* Fri Apr 05 2019 njcuk9999 <neil.james.cook@gmail.com> - 0.4.112

================================================================================
	- spirouEXTOR.py - remove weighting of raw pixels less than zero to very low value (rev.cac18d7c)
	- spirouConst.py - update date and version (rev.d19bdcc2)
	- cal_SHAPE_spirou_old.py - edit background correction (rev.80520b94)
	- cal_SLIT_spirou.py - do not mask out the zeros (rev.fa707ee1)
	- caal_loc_RAW_spirou.py - do not mask out the zeros (rev.9bec375f)
	- cal_FF_RAW_spirou.py - do not mask out the zeros (rev.ef4d1eec)
	- cal_extract_RAW_spirou.py - do not mask out the zeros (rev.9e6ee0ab)
	- spirouBACK.py - add background debug plot to background finding function (rev.b863345b)
	- cal_SLIT_spirou.py - add hdr and cdr to background correction (to save debug file) (rev.e79da9b5)
	- cal_loc_RAW_spirou.py - add hdr and cdr to background correction (to save debug file) (rev.d83820c3)
	- cal_extract_RAW_spirou.py - add hdr and cdr to background correction (to save debug file) (rev.bd7b9a3a)
	- cal_FF_RAW_spirou.py - add hdr and cdr to background correction (to save debug file) (rev.59d7a14b)
	- misc/cal_SHAPE_spirou_old.py - add changes to background subtraction (rev.2b31f748)
	- cal_low_RAW_spirou.py - add changes to background subtraction (rev.0938ba11)
	- cal_FF_RAW_spirou.py - add changes to background subtraction (rev.0f46aa1b)
	- spirouWAVE.py - add initial keep parameter for line width (rev.2937c924)
	- spirouBACK.py - add Etienne's changes into measure_background_flatfield (rev.76f52723)
	- cal_WAVE_NEW_E2DS_spirou_2.py - add fix for updating the HC/Fp header for wave solution (rev.01b4b1c0)
	- constants_SPIROU_H4RG.py - change background correction constants (rev.3735fb00)
	- cal_extract_RAW_spirou.py - change background correction to Etienne's new method! (rev.af2c9bc2)



================================================================================
* Sat Apr 06 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.113

================================================================================
	- cal_FF_RAW_spirou.py - remove background subtraction (for test) (rev.86c2d730)
	- test.run - update test.run (rev.4d532076)
	- cal_FF_RAW_spirou.py - unfix negative values set to zero (rev.9b01b46a)



================================================================================
* Sun Apr 07 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.114

================================================================================
	- cal_FF_RAW_spirou.py - re-add in new background subtraction (rev.81d687a6)
	- spirouEXTOR.py - reset raw_weights (rev.79275a7d)
	- spirouEXTOR.py - reset raw_weights (rev.89afcca7)
	- cal_FF_RAW_spirou.py - try to match neil branch (rev.aa5b8dda)
	- cal_FF_RAW_spirou.py - try to match master (rev.165511a1)
	- cal_FF_RAW_spirou.py - test force extractff type to 3c (rev.8ea9a04e)
	- spirouBACK.py - add in old measure background function (as test) (rev.df8f9be4)
	- cal_FF_RAW_spirou.py - redo debananafication (rev.9d332245)
	- cal_FF_RAW_spirou.py - undo debananafication (rev.9a207ff7)
	- reset cal_loc (no background) for test (rev.ce933bc4)
	- reset cal_loc (no background) for test (rev.22f6acbe)
	- cal_FF_RAW_spirou.py - remove background subtraction (for test) (rev.7083a406)



================================================================================
* Mon Apr 08 2019 njcuk9999 <neil.james.cook@gmail.com> - 0.4.115

================================================================================
	- spirouEXTOR.py - add options in extraction method to test different weighting systems (rev.6f3f474d)
	- spirouImage.py - replace zeros with NaNs (rev.e909f60d)
	- spirouFLAT.py - replace zero's with NaNs (rev.ca1bc4e9)
	- spirouEXTOR.py - replace zeros with NaNs (rev.d6d61821)
	- spirouPlot.py - replace zeros with NaNs (rev.b178ce49)
	- spirouBACK.py - replace zeros with NaNs (rev.a386fade)
	- cal_FF_RAW_spirou.py - replace zeros with nans (rev.1d0ea71c)
	- spirouEXTOR.py - readd raw_weights (rev.b9a9a60f)



================================================================================
* Wed Apr 10 2019 njcuk9999 <neil.james.cook@gmail.com> - 0.4.116

================================================================================
	- update test.run (rev.40fb702a)
	- spirouRV.py - deal with NaNs (rev.bb533a39)
	- spirouLOCOR.py - deal with NaNs (rev.35b03bf3)
	- spirouImage.py - deal with NaNs (rev.f4bfaa87)
	- spirouPlot.py - convert zeros to NaNs (rev.396dad14)
	- see_shift.py - test for pixel shifting by different amounts (rev.8c1547e8)
	- cal_WAVE_E2DS_EA_spirou.py - convert zeros to NaNs (rev.1073a2e0)
	- cal_SLIT_spirou.py - change zeros to NaNs (rev.7268bc23)
	- cal_loc_RAW_spirou.py - change zeros to NaNs (rev.45aad289)
	- cal_extract_RAW_spirou.py - change zeros to NaN (rev.8f57fd93)



================================================================================
* Wed Apr 24 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.117

================================================================================
	- change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit (rev.474cec87)
	- change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit (rev.7db4647d)
	- change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit (rev.9a3b2d53)
	- change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit (rev.06e6a318)
	- change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit (rev.4a3170cb)
	- change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit (rev.bdae77f7)
	- change all np.polyfit to SpirouDRS.spirouCore.spirouMath.nanpolyfit (rev.dce74cb5)
	- change the way InterpolatedUnivariateSpline works (rev.56e6db79)
	- update test.run (rev.13ffd01f)
	- update test.run (rev.43b9a420)



================================================================================
* Thu Apr 25 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.118

================================================================================
	- spirouImage.py - write new s1d function (rev.9791da7a)
	- spirouPlot.py - add ext_1d_spectrum_debug_plot plot for debugging s1d plot (rev.3b683a68)
	- constants_SPIROU_H4RG.py - add new s1d constants (rev.dae6fa8f)
	- cal_extract_RAW_spirou.py - added new s1d code (not finished) (rev.f1b34838)
	- spirouRV.py - update pearson r test for NaNs (rev.afc06b24)
	- update test.run (rev.136d3627)
	- spirouRV.py - catch NaN warnings that are valid (rev.ba10e189)
	- spirouRV.py - catch NaN warnings that are valid (rev.bb0413c3)
	- spirouRV.py - catch NaN warnings that are valid (rev.e2e5099d)
	- spirouRV.py - catch NaN warnings that are valid (rev.b68b0018)
	- spirouRV.py - looking for NaN warnings (rev.526a74a8)
	- spirouRV.py - looking for NaN warnings (rev.a36047d2)
	- cal_CCF_E2DS_FP_spirou.py - looking for NaN warnings (rev.b60e5e0c)
	- cal_CCF_E2DS_FP_spirou.py - looking for NaN warnings (rev.467d92d1)
	- cal_CCF_E2DS_FP_spirou.py - looking for NaN warnings (rev.2d0dea48)
	- cal_CCF_E2DS_FP_spirou.py - looking for NaN warnings (rev.14f65ed8)
	- cal_CCF_E2DS_FP_spirou.py - looking for NaN warnings (rev.894608a1)
	- cal_CCF_E2DS_FP_spirou.py - looking for NaN warnings (rev.6b0c1b69)
	- spirouTelluric.py - catch warnings from less than for NaNs (rev.5425fbd4)
	- compare_outputs.py - script to difference all outputs in two folders with files of the same name (output difference) (rev.d0d7910d)
	- constants_SPIROU_H4RG.py - turn off plotting all fit_tellu orders (rev.12a044a2)
	- obj_mk_tellu_new.py - add warning around less than (for NaNs) (rev.3d7cc239)
	- obj_fit_tellu.py - remove a NaN sum (rev.70688966)
	- test.run - update just mk_tellu/fit_tellu to test (rev.bc727b72)
	- test.run - update just fit_tellu to test (rev.fdb98d2a)
	- change np.sum --> np.nansum, np.mean --> np.nanmean, np.median --> np.nanmedian etc (rev.d68dfdd7)



================================================================================
* Fri Apr 26 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.119

================================================================================
	- extract_trigger.py - correct mistake with extraction trigger (rev.d23ab0a7)
	- update test.run (rev.de0fd097)
	- spirouTable.py - fix problem with NaNs in header (make string) (rev.5b5d9f05)
	- spirouTable.py - fix problem with NaNs in header (make string) (rev.fea24bd1)
	- extract_trigger.py - should use DRS_DATA_RAW in preprocessing (rev.07aeeaa0)
	- obj_fit_tellu.py - add s1d telluric corrected files (rev.c67964fa)
	- spirouImage.py - correct s1d ith telluric NaNs (rev.d2c02a1b)
	- obj_fit_tellu.py - change to NBLAZE (rev.68e96cdc)
	- spirouImage.py - new s1d - deal with full order being NaNs (for telluric) (rev.56365352)
	- obj_fit_tellu.py - save s1d for corrected spectrum (rev.ad4b9da8)
	- constants_SPIROU_H4RG.py - increase edge smoothing size (rev.99f0cce4)
	- constants_SPIROU_H4RG.py - increase edge smoothing size (rev.f2e758b3)
	- constants_SPIROU_H4RG.py - increase edge smoothing size (rev.88c9f646)
	- cal_extract_RAW_spirou.py - s1d fix problems with adding new s1d code (rev.7f76591c)
	- cal_extract_RAW_spirou.py - s1d fix problems with adding new s1d code (rev.1621a6e4)
	- spirouImage.py - new s1d - iuv spline wrong (rev.b4c5cb78)
	- spirouImage.py - edges was wrong (rev.a188cbdc)
	- cal_extract_RAW_spirou.py - correct s1d (now s1dw and s1dv) (rev.900e5514)



================================================================================
* Mon Apr 29 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.120

================================================================================
	- compare_outputs.py - change paths (rev.68d2bd68)



================================================================================
* Tue Apr 30 2019 Neil Cook <neil.james.cook@gmail.com> - 0.4.121

================================================================================
	- update trigger (rev.dd8bbabb)
	- obj_fit_tellu.py - fix NBLAZE to BLAZE in uniform velocity s1d (rev.7c861048)
