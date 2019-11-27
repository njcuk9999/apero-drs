


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
